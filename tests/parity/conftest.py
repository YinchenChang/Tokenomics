"""數值檢查的共用設定（修訂八-B：停用公式引擎，所有檢查改讀 LibreOffice 重算後的值）。

- 模型路徑：讀 model/CURRENT；環境變數 TOKENOMICS_MODEL 設定時改用該檔（供「故意改錯」檢查）。
- `lo` fixture：`lo.view(inputs)` 對一組輸入改寫活頁簿、以 LibreOffice 重算，回傳唯讀的 `View`。
  同一組輸入整個 session 只算一次；session 開始時以 2 條執行緒預先算好 scenarios.yaml 的全部情境與基準。
"""
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import get_column_letter, range_boundaries

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo 根目錄
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parity_lib import lo_recalc, parse_ref, resolve_key, set_inputs  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
# 由 .gitignore 排除；供每輪報告取數。
RESULTS = Path(os.environ.get("PARITY_RESULTS") or Path(__file__).parent / "_results.json")
LO_THREADS = 2


def model_path() -> Path:
    env = os.environ.get("TOKENOMICS_MODEL")
    if env:
        return Path(env).resolve()
    return REPO / "model" / (REPO / "model" / "CURRENT").read_text(encoding="utf-8").strip()


def _norm(v):
    """空格一律回傳 ""（同舊引擎 norm）。"""
    return "" if v is None else v


class View:
    """某一組輸入經 LibreOffice 重算後的唯讀檢視；介面同舊 Engine 的唯讀部分。"""

    def __init__(self, meta: "Meta", cells: dict):
        self._m = meta
        self._cells = cells          # {頁名: {座標: 值}}，只含非空儲存格
        self._all = None

    names = property(lambda self: self._m.names)
    sheetnames = property(lambda self: list(self._m.sheetnames))
    formula_cells = property(lambda self: list(self._m.formula_cells))

    def name_ref(self, name: str):
        return parse_ref(self._m.names[name])

    def get(self, sheet: str, ref: str):
        """單格回傳純量；多格回傳巢狀 list（列 × 欄）。"""
        ref = ref.replace("$", "")
        d = self._cells.get(sheet, {})
        if ":" not in ref:
            return _norm(d.get(ref))
        c1, r1, c2, r2 = range_boundaries(ref)
        return [[_norm(d.get(f"{get_column_letter(c)}{r}")) for c in range(c1, c2 + 1)] for r in range(r1, r2 + 1)]

    def get_name(self, name: str):
        """單格→純量；單列或單欄→一維 list；其他→巢狀 list。"""
        sheet, ref = self.name_ref(name)
        v = self.get(sheet, ref)
        if isinstance(v, list) and (len(v) == 1 or all(len(r) == 1 for r in v)):
            return [x for row in v for x in row]
        return v

    def evaluate_all(self) -> dict:
        """全部公式格的值。"""
        if self._all is None:
            self._all = {(s, c): _norm(self._cells.get(s, {}).get(c)) for s, c in self._m.formula_cells}
        return self._all


class Meta:
    """從原檔（公式模式）讀一次：具名範圍、公式格清單、工作表順序。"""

    def __init__(self, path: Path):
        wb = openpyxl.load_workbook(path)
        self.sheetnames = list(wb.sheetnames)
        self.names = {k: v.attr_text for k, v in wb.defined_names.items()}
        self.formula_cells = [(ws.title, c.coordinate) for ws in wb for row in ws.iter_rows() for c in row
                              if isinstance(c.value, str) and c.value.startswith("=")]
        wb.close()


class LO:
    def __init__(self, path: Path):
        self.path = path
        self.meta = Meta(path)
        self._cache: dict[str, View] = {}
        self._lock = threading.Lock()
        self.recalc_seconds: dict[str, float] = {}

    @staticmethod
    def _key(inputs: dict) -> str:
        return json.dumps(inputs, sort_keys=True, ensure_ascii=False, default=str)

    def _compute(self, inputs: dict) -> View:
        t0 = time.perf_counter()
        tmp = Path(tempfile.mkdtemp(prefix="lo_view_"))
        try:
            src = tmp / self.path.name
            set_inputs(self.path, src, inputs)
            out = lo_recalc(src, tmp / "lo")
            wb = openpyxl.load_workbook(out, data_only=True, read_only=True)
            cells = {}
            for ws in wb.worksheets:
                d = cells[ws.title] = {}
                for row in ws.iter_rows():
                    for c in row:
                        if c.value is not None:
                            d[sys.intern(c.coordinate)] = c.value
            wb.close()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.recalc_seconds[self._key(inputs)] = time.perf_counter() - t0
        return View(self.meta, cells)

    def view(self, inputs: dict) -> View:
        k = self._key(inputs)
        with self._lock:
            v = self._cache.get(k)
        if v is None:
            v = self._compute(inputs)
            with self._lock:
                v = self._cache.setdefault(k, v)
        return v

    def prewarm(self, input_sets: list[dict]) -> None:
        todo = [i for n, i in enumerate(input_sets) if self._key(i) not in {self._key(j) for j in input_sets[:n]}]
        with ThreadPoolExecutor(LO_THREADS) as ex:
            list(ex.map(self.view, todo))


@pytest.fixture(scope="session")
def lo(request):
    """session 開始時，以 2 條執行緒預先算好「本次選到的測試」會用到的輸入組合（基準、被選到的情境，
    以及測試模組以 PREWARM 宣告的額外組合）；其餘組合第一次用到時才算。全套執行時即為 scenarios.yaml 全部情境＋額外組合。"""
    path = model_path()
    obj = LO(path)
    sets = [{}]
    for item in request.session.items:
        sc = getattr(getattr(item, "callspec", None), "params", {}).get("sc")
        if sc is not None:
            sets.append(sc["inputs"])
        sets.extend(getattr(item.module, "PREWARM", {}).get(item.originalname, []))
    t0 = time.perf_counter()
    obj.prewarm(sets)
    print(f"\n[lo] 預先重算 {len(obj._cache)} 組輸入，{time.perf_counter() - t0:.0f} 秒", file=sys.stderr)
    return obj


@pytest.fixture(scope="session")
def results_store():
    data = json.loads(RESULTS.read_text()) if RESULTS.exists() else {}
    yield data
    RESULTS.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str))

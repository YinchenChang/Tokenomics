"""v21.3＋v21.4＋v21.5＋v21.6＋v21.7（＋v21.8：v218_cells／v218_names）看守的「v21.2 → 現行版逐格差異」集合，供舊版逐格差異測試（*_diffs_only_expected_*）放寬用。

只放寬到兩張工作單列明的格：docs/workorders/20261024_v21.3_機架價低端與Sol快取價.md 的 W1–W6，
以及 docs/workorders/20261024_v21.4_token帳讀法與過時文字.md 的 W1–W6（v21.4 新增的格見 `exact` 內標註）；
規則與 test_v2130／test_v2140 的逐格差異測試相同（那裡是權威，這裡重複驗證一次，寬於工作單即斷言失敗）。
舊測試的做法：實際差異與預期清單兩邊都扣掉本集合（`strip`），其餘比較不變。
（v21.4 起沿用 v213_cells 的函式名稱；內容已含 v21.4、v21.5、v21.6、v21.7 的差異格；v21.7：docs/workorders/20261025_v21.7_NonNV_AMD與Trn同源價.md 的 W1–W3——NonNV B5:G5、F7、L5、L7、L8、L9、A2，Interface A368，DB_Evidence 第 334、335 列，Decisions 第 336 列；v21.5：docs/workorders/20261025_v21.5_計價倍數新舊約與GM088.md 的 W1、W2、W4；v21.6：docs/workorders/20261025_v21.6_NonNV持有比TPU_Trn.md 的 W1、W2——NonNV E6:G7、L6、L7，DB_Evidence 第 333 列，Decisions 第 335 列。）
"""
import re
from functools import lru_cache
from pathlib import Path

import openpyxl

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V212 = REPO / "model" / "archive" / "20261023_Tokenomics_v21.2.xlsx"
V217 = REPO / "model" / "archive" / "20261025_Tokenomics_v21.7.xlsx"
SHEETS = {"Gov_Map", "README", "Interface", "Spec_Rack", "Cap_In", "Alloc_In", "Alloc", "L1", "Checks", "Decisions", "DB_Evidence", "NonNV", "SRC_Price", "SRC_HW", "SRC_Index"}
_row = lambda coord: int(re.sub(r"[A-Z]+", "", coord))
_col = lambda coord: re.sub(r"\d+", "", coord)
_num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)


def _eqv(x, y):
    if _num(x) and _num(y):
        return abs(x - y) <= 1e-9 * max(abs(x), abs(y), 1e-300) + 1e-12
    return x == y


@lru_cache(maxsize=None)
def v218_cells() -> dict:
    """v21.7 → 現行版（v21.8）的全部差異格（公式文字或重算值不同）。內容由 test_v2180（權威）逐類看守：
    預期變動 CSV、第 2 節文字、第 3 節 SRC／DB_Evidence／Decisions、治理連帶（SRC 等級與旗標、SRC_Index、Gov_Map AF／T／AH／AJ／AI、
    Interface U／V／R219／S219、Load_Bearing L／N、Checks D86／D87／D89／D99）與區間端點重產。舊測試兩邊都扣掉本集合（strip）。"""
    a, b = openpyxl.load_workbook(V217), openpyxl.load_workbook(model_path())
    av, bv = openpyxl.load_workbook(V217, data_only=True), openpyxl.load_workbook(model_path(), data_only=True)
    out = {}
    for ws in a:
        wn, va, vb = b[ws.title], av[ws.title], bv[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                if ws.cell(r, c).value != wn.cell(r, c).value or not _eqv(va.cell(r, c).value, vb.cell(r, c).value):
                    out.setdefault(ws.title, set()).add(ws.cell(r, c).coordinate)
    return out


@lru_cache(maxsize=None)
def v218_names() -> set:
    """v21.7 → v21.8 值改變或新增的具名範圍（test_v2180_names 看守）。舊測試的「名稱不變」檢查扣掉本集合。"""
    a = openpyxl.load_workbook(V217, data_only=True)
    bf, bv = openpyxl.load_workbook(model_path()), openpyxl.load_workbook(model_path(), data_only=True)
    from openpyxl.utils import range_boundaries
    out = set(bf.defined_names) - set(a.defined_names)
    for n, d in a.defined_names.items():
        t = d.attr_text
        if "!" not in t or "," in t:
            continue
        if n not in bf.defined_names or bf.defined_names[n].attr_text != t:
            out.add(n); continue
        sh, rg = t.rsplit("!", 1); sh = sh.strip("'")
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        if any(not _eqv(a[sh].cell(r, c).value, bv[sh].cell(r, c).value) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
            out.add(n)
    return out


@lru_cache(maxsize=None)
def v213_cells() -> dict:
    a, b = openpyxl.load_workbook(V212), openpyxl.load_workbook(model_path())
    assert a.sheetnames == b.sheetnames
    d = {}
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    d.setdefault(ws.title, []).append((ws.cell(r, c).coordinate, x, y))
    v218 = v218_cells()      # v21.8：先扣掉 v21.7 → v21.8 的差異格（兩邊都扣）
    d = {sh: [t for t in lst if t[0] not in v218.get(sh, set())] for sh, lst in d.items()}
    d = {sh: lst for sh, lst in d.items() if lst}
    assert set(d) <= SHEETS, set(d) - SHEETS
    exact = {
        "README": {"A1", "A73", "B5", "B73", "A74", "B74", "A75", "B75"}, "Spec_Rack": {"F11"}, "Cap_In": {"A47", "D7", "F47", "G7", "H335"}, "Alloc_In": {"G23"},
        "L1": {f"I{r}" for r in range(128, 137)}, "Checks": {"D86"},
        "Gov_Map": {"H92", "I92", "N92", "R92"},      # v21.5 W3：GM088（Spec_Rack F11）
        "Decisions": {f"{c}{r}" for r in (332, 333, 334, 335, 336) for c in "ABCDEFGHIJ"},      # v21.7：SL64-01（第 336 列）；v21.6：SL63-01（第 335 列）
        "DB_Evidence": {f"{c}{r}" for r in (328, 329, 330, 331, 332, 333, 334, 335) for c in "ABCDEFGHIJKLMNOPQR"},      # v21.7：E410／E411（第 334、335 列）；v21.6：E409（第 333 列）
        "NonNV": {"E6", "F6", "G6", "E7", "F7", "G7", "L6", "L7"} | {f"{c}5" for c in "BCDEFG"} | {"L5", "L8", "L9", "A2"},      # v21.6 W1；v21.7 W1／W2
        "Interface": {"A368"},      # v21.7 W2
        "SRC_Price": {"B10", "H10", "W10", "B12", "H12", "W12", "O11", "P11", "V11", "O53", "Q53", "V53", "W53", "R53", "V54"},
    }
    out = {}
    for sh, lst in d.items():
        got = {t[0] for t in lst}
        if sh in exact:
            want = exact[sh] - v218.get(sh, set())
            assert got == want, (sh, sorted(got ^ want))
        elif sh == "SRC_HW":      # 新增兩列（第 102、103 列）、X 欄範圍、V20、W21
            assert all(_row(x) in (102, 103) or (_col(x) == "X" and 5 <= _row(x) <= 101) or x in ("V20", "W21") for x in got)
        elif sh == "SRC_Index":      # 只因 SRC_HW 多兩列而重排（A:F 欄，第 102 列起）
            assert all(_col(x) in "ABCDEF" and _row(x) >= 102 for x in got)
        elif sh == "Alloc":      # 版本字串 C177、區間端點常數（數字對數字）、指紋記錄列（第 1230–1240 列）
            assert all(t[0] == "C177" or (_num(t[1]) and _num(t[2])) or 1230 <= _row(t[0]) <= 1240 for t in lst)
        out[sh] = got
    return out


def strip(sheet: str, coords) -> list:
    """從座標清單扣掉 v21.3 的差異格（舊測試的實際清單與預期清單兩邊都用）。"""
    gone = v213_cells().get(sheet, set()) | v218_cells().get(sheet, set())
    return sorted(c for c in coords if c not in gone)


@lru_cache(maxsize=None)
def csv_value_cells() -> dict:
    """預期變動 CSV 的 (頁, 儲存格) -> (v21.2 值, v21.3 值)（工作單第 0 節，chat 端實測）。"""
    import csv
    out = {}
    for r in csv.DictReader(open(REPO / "docs" / "workorders" / "20261024_v21.3_預期變動.csv", encoding="utf-8")):
        a, b = r["v21.2"], r["new"]
        try:
            a, b = float(a), float(b)
        except ValueError:
            pass      # 文字格（動態說明文字）照原字串
        out[(r["sheet"], r["cell"])] = (a, b)
    return out


NUM_DIFFS_V2160 = {      # v21.6 工作單第 0 節清單（數值差異）
    ("NonNV", c) for c in ("E6", "F6", "G6", "H6", "I6", "J6", "E7", "F7", "G7", "H7", "I7", "J7")} | {
    ("Interface", f"{c}{r}") for r in (375, 376) for c in "CDE"} | {
    ("Gov_Map", c) for c in ("K396", "L396", "Q396", "Q399", "Q400", "K402", "L402", "Q402", "Q405", "Q406")}
NUM_DIFFS_V2170 = {      # v21.7 工作單第 0 節清單（數值差異；對 v21.6）
    ("NonNV", c) for c in ("B5", "C5", "D5", "E5", "F5", "G5", "H5", "I5", "J5", "F7", "H7")} | {
    ("Interface", c) for c in ("C369", "D369", "E369", "C374", "D374", "E374", "D376")} | {
    ("Gov_Map", c) for c in ("K389", "L389", "Q389", "K390", "L390", "Q390", "Q391", "Q392", "Q393", "Q394", "Q402")}
NUM_DIFFS = NUM_DIFFS_V2160 | NUM_DIFFS_V2170      # 累計（v21.5 → 現行；舊版逐格比較測試扣除用）

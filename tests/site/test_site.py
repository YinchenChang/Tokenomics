"""靜態網站（GitHub Pages 唯讀版，site/build_site.py）檢查。

1. 每一頁都產生（app/nav.py 的 11 頁 ＋ build.json）。
2. 左側導覽頁名＝Andy 核定的頁名（Block 2–5、Alloc 逐字），且與 Streamlit app/main.py 同一份清單。
3. 抽樣數字＝Excel 存值：本測試以 openpyxl 直接讀現行活頁簿（data_only=True，不經 app/ 的取數函式），
   依具名範圍與表頭找到儲存格，格式化（與網站相同的 fmt）後比對頁面上對應的表格格或 KPI 卡。
4. 不載入任何外部資源（無 http(s)／協定相對 URL 的 src、href、url()、@import、fetch）。
5. 刊頭的模型版本與 Excel 檔名＝model/CURRENT。
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.common import fmt, fmt_unit  # noqa: E402  # 只用顯示格式（與網站相同）；值由本測試自行讀 Excel
from app.nav import PAGES  # noqa: E402

APPROVED = {   # Andy 2026-11-05 核定（逐字）
    "overview": "總覽",
    "block2": "推論：每 GW 產能與單位成本",
    "block3": "訓練：算力與成本",
    "block4": "價格、營收與攤提",
    "block5": "任務成功率與每任務成本",
    "alloc": "算力分配：服務／訓練／研發",
}


def _load_builder():
    spec = importlib.util.spec_from_file_location("tokenomics_build_site", ROOT / "site" / "build_site.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    meta = _load_builder().build(out)
    return out, meta


@pytest.fixture(scope="module")
def xl():
    """獨立讀取：openpyxl 直接開 model/CURRENT 的活頁簿（存值）。"""
    name = (ROOT / "model" / "CURRENT").read_text(encoding="utf-8").strip()
    wb = openpyxl.load_workbook(ROOT / "model" / name, data_only=True)

    def get(defined: str):
        sheet, ref = next(iter(wb.defined_names[defined].destinations))
        ws = wb[sheet]
        c1, r1, c2, r2 = range_boundaries(ref.replace("$", ""))
        vals = [ws.cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        return vals[0] if len(vals) == 1 else vals

    def label(defined: str):
        sheet, ref = next(iter(wb.defined_names[defined].destinations))
        _, r1, _, _ = range_boundaries(ref.replace("$", ""))
        ws = wb[sheet]
        lab = re.sub(r"\s*\[IF[A-Z]?_\w+\]\s*$", "", str(ws.cell(r1, 1).value)).strip("　 ")
        return lab, ws.cell(r1, 2).value

    return {"name": name, "get": get, "label": label}


class _Tables(HTMLParser):
    """收集頁面上的表格（含所在選擇器版本的 data-v-* 與表格 id）、KPI 卡與 meta。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.kpis, self.ids, self.nav = [], {}, {}, []
        self._stack, self._cell, self._row, self._tbl = [], None, None, None
        self._kpi, self._kpi_part, self._id, self._nav_a = None, None, None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in ("br", "meta", "input", "line", "rect", "path"):
            self._stack.append((tag, a))
        if tag == "table":
            dims = {k[7:]: v for _, at in self._stack for k, v in at.items() if k.startswith("data-v-")}
            self._tbl = {"id": a.get("id"), "dims": dims, "rows": []}
        elif tag == "tr" and self._tbl is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = ""
        elif tag == "div" and a.get("class") == "kpi":
            self._kpi = {}
        elif tag == "div" and self._kpi is not None and a.get("class") in ("k", "v num", "s"):
            self._kpi_part = a["class"].split()[0]
            self._kpi[self._kpi_part] = ""
        elif tag == "dd" and a.get("id"):
            self._id = a["id"]
            self.ids[self._id] = ""
        elif tag == "a" and any(t == "nav" for t, _ in self._stack):
            self._nav_a = True
            self.nav.append("")

    def handle_endtag(self, tag):
        while self._stack:
            t, _ = self._stack.pop()
            if t == tag:
                break
        if tag in ("td", "th") and self._cell is not None:
            self._row.append(self._cell.strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self._tbl["rows"].append(self._row)
            self._row = None
        elif tag == "table" and self._tbl is not None:
            self.tables.append(self._tbl)
            self._tbl = None
        elif tag == "div" and self._kpi_part:
            self._kpi_part = None
        elif tag == "div" and self._kpi is not None and self._kpi_part is None and "k" in self._kpi and "v" in self._kpi:
            self.kpis[self._kpi["k"]] = self._kpi["v"]
            self._kpi = None
        elif tag == "dd":
            self._id = None
        elif tag == "a":
            self._nav_a = False

    def handle_data(self, data):
        if self._cell is not None:
            self._cell += data
        if self._kpi is not None and self._kpi_part:
            self._kpi[self._kpi_part] += data
        if self._id:
            self.ids[self._id] += data
        if self._nav_a:
            self.nav[-1] += data


def _parse(out: Path, fn: str) -> _Tables:
    p = _Tables()
    p.feed((out / fn).read_text(encoding="utf-8"))
    return p


def _file(key: str) -> str:
    path = dict((k, p) for k, _, p in PAGES)[key]
    return "index.html" if path == PAGES[0][2] else f"{path}.html"


def _cell(tables, row_start: str, col: str, dims: dict | None = None, tid: str | None = None) -> str:
    """在符合選擇器版本（dims）或 id 的表格中，找列首以 row_start 開頭、欄名＝col 的格。"""
    for t in tables:
        if dims is not None and t["dims"] != dims:
            continue
        if tid is not None and t["id"] != tid:
            continue
        head = t["rows"][0]
        if col not in head:
            continue
        j = head.index(col)
        for r in t["rows"][1:]:
            if r and r[0].startswith(row_start):
                return r[j]
    raise AssertionError(f"找不到格：列「{row_start}」欄「{col}」dims={dims} id={tid}")


# ── 1. 每一頁都產生 ───────────────────────────────────────────────

def test_every_page_exists(site):
    out, meta = site
    files = [_file(k) for k, _, _ in PAGES]
    assert len(files) == 11 and files[0] == "index.html"
    for f in files:
        assert (out / f).stat().st_size > 5000, f
    assert [p["file"] for p in meta["pages"]] == files
    assert json.loads((out / "build.json").read_text(encoding="utf-8"))["pages"] == meta["pages"]


# ── 2. 導覽頁名 ───────────────────────────────────────────────────

def test_nav_names_as_approved(site):
    out, _ = site
    titles = dict((k, t) for k, t, _ in PAGES)
    for k, v in APPROVED.items():
        assert titles[k] == v
    expected = [t for _, t, _ in PAGES]
    for k, _, _ in PAGES:
        p = _parse(out, _file(k))
        assert p.nav == expected, k
        html = (out / _file(k)).read_text(encoding="utf-8")
        assert f'<h2 class="pt">{titles[k]}</h2>' in html
        assert len(re.findall(r'<a href="[^"]+" aria-current="page">', html)) == 1


def test_streamlit_uses_same_titles():
    src = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "from app.nav import PAGES" in src and "title=title" in src
    assert not re.search(r'title="Block \d"|title="Alloc"', src)


# ── 3. 抽樣數字＝Excel 存值 ───────────────────────────────────────

def _gen_case_value(xl, name, gen, case):
    vals, gens, cases = xl["get"](name), xl["get"]("IF_HdrGen"), xl["get"]("IF_HdrCost")
    return next(v for v, g, c in zip(vals, gens, cases) if g == gen and c == case)


def test_meta_matches_current(site, xl):
    out, _ = site
    p = _parse(out, "index.html")
    assert p.ids["meta-excel"] == xl["name"]
    assert p.ids["meta-version"] == re.search(r"_(v[\d.]+)\.xlsx$", xl["name"]).group(1) == "v21.10"
    assert re.fullmatch(r"[0-9a-f]{7}.*", p.ids["meta-commit"])
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.ids["meta-date"])


def test_sample_kpis_equal_excel(site, xl):
    out, _ = site
    pay = _parse(out, _file("payback"))
    for n in ("L1_M", "L1_LTotalFleetVDisc", "L1_RevGW_PQ_VR200"):
        key = next(k for k in pay.kpis if k.startswith(n + "（"))
        assert pay.kpis[key] == fmt(xl["get"](n)), n
    ov = _parse(out, _file("overview"))
    for n in ("GOV_Errors", "GOV_Warnings", "GOV_Info", "CTL_GW"):
        assert ov.kpis[n] == fmt(xl["get"](n)), n
    assert ov.kpis["IF_Util"] == fmt_unit(xl["get"]("IF_Util"), "%")
    b5 = _parse(out, _file("block5"))
    lab, unit = xl["label"]("IF_PFloor")
    assert b5.kpis[f"{lab}（{unit}）"] == fmt_unit(xl["get"]("IF_PFloor"), unit)


@pytest.mark.parametrize("name,tier_i,case_i,gen", [
    ("IF_TokGW_Luna", 0, 1, "VR200 NVL72"),
    ("IF_CostDec_Sol", 1, 0, "GB300 NVL72"),
    ("IF_VReq_Astra", 2, 2, "Rubin Ultra（MGX NVL 單架，72 GPU）"),
    ("IF_TokPerJ_Luna", 0, 2, "Hopper H100"),
])
def test_block2_cells_equal_excel(site, xl, name, tier_i, case_i, gen):
    out, _ = site
    tier = name.rsplit("_", 1)[1]
    case = ["低成本", "基準", "高成本"][case_i]
    lab, unit = xl["label"](name)
    got = _cell(_parse(out, _file("block2")).tables, f"{tier}｜{lab}（{unit}）", gen, dims={"tier": str(tier_i), "case": str(case_i)})
    assert got == fmt(_gen_case_value(xl, name, gen, case))


@pytest.mark.parametrize("name,tier_i,case_i,gen", [
    ("IF_RevGW_Astra", 2, 1, "VR200 NVL72"),
    ("IF_AmortDefault_Sol", 1, 0, "GB200 NVL72"),
])
def test_block4_cells_equal_excel(site, xl, name, tier_i, case_i, gen):
    out, _ = site
    tier = name.rsplit("_", 1)[1]
    case = ["低成本", "基準", "高成本"][case_i]
    lab, unit = xl["label"](name)
    p = _parse(out, _file("block4"))
    got = _cell(p.tables, f"{tier}｜{lab}（{unit}）", gen, dims={"tier": str(tier_i), "case": str(case_i)})
    assert got == fmt(_gen_case_value(xl, name, gen, case))
    price = p.tables[0]                                     # 單價表：列＝層級、欄＝token 類型
    plab, _ = xl["label"]("IF_PriceFresh_Sol")
    col = next(i for i, h in enumerate(price["rows"][0]) if h.startswith(plab))
    row = next(r for r in price["rows"][1:] if r[0].startswith("Sol"))
    assert row[col] == fmt(xl["get"]("IF_PriceFresh_Sol"))


@pytest.mark.parametrize("name", ["IF_CapexTotal", "IF_DeprIT", "IF_AvgDraw"])
def test_overview_block1_row_equals_excel(site, xl, name):
    """總覽 Block 1 表（兩層表頭：世代 × 成本情境）的整列 15 格＝Excel。"""
    out, _ = site
    t = next(t for t in _parse(out, _file("overview")).tables if len(t["rows"]) > 3 and len(t["rows"][1]) == 15)
    lab, unit = xl["label"](name)
    row = next(r for r in t["rows"][2:] if r[0] == f"{lab}（{unit}）")
    assert row[1:] == [fmt(v) for v in xl["get"](name)]
    assert t["rows"][1] == [str(c) for c in xl["get"]("IF_HdrCost")]


def test_lookup_and_alloc_values_equal_excel(site, xl):
    out, _ = site
    p = _parse(out, _file("lookup"))
    for n in ("IF_Util", "AL_Q1", "GOV_Errors", "L1_M"):
        got = _cell(p.tables, n, "值", tid="lk")
        assert got == fmt(xl["get"](n)), n
    a = _parse(out, _file("alloc"))
    lab, unit = xl["label"]("AL_Q1")
    got = _cell(a.tables, lab, "值（多格為 C–E 欄：世代或層級）")
    v = xl["get"]("AL_Q1")
    assert got == " ｜ ".join(fmt_unit(x, unit or "") for x in (v if isinstance(v, list) else [v]))


# ── 4. 不載入外部資源 ─────────────────────────────────────────────

EXTERNAL = [
    re.compile(r"""\b(?:src|href|action|poster|data)\s*=\s*["']?\s*(?:https?:)?//""", re.I),
    re.compile(r"url\(\s*['\"]?\s*(?:https?:)?//", re.I),
    re.compile(r"@import", re.I),
    re.compile(r"<(?:link|iframe|img|object|embed|source|video|audio)\b", re.I),
    re.compile(r"<script\b[^>]*\bsrc\s*=", re.I),
    re.compile(r"\bfetch\s*\(|XMLHttpRequest|navigator\.sendBeacon|new\s+WebSocket|import\s*\(", re.I),
]


def test_no_external_resources(site):
    out, _ = site
    pages = {_file(k) for k, _, _ in PAGES}
    for f in pages:
        html = (out / f).read_text(encoding="utf-8")
        for rx in EXTERNAL:
            m = rx.search(html)
            assert not m, f"{f}: {rx.pattern} → {html[max(0, m.start() - 60):m.end() + 60]!r}"
        for href in re.findall(r'href="([^"]*)"', html):     # 站內連結只指向本站各頁
            assert href in pages, (f, href)

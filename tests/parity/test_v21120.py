"""v21.12 專屬測試（v22.0 B2「結構二」：GPT-6.1 Terra 第四層級進入 Block 4–6；設計文件 docs/plan/20261105_v22.0_Terra第四層級_設計.md 第 6.1、6.4 節）。
讀 LibreOffice 重算後存檔的現行版（model/CURRENT）與封存的 v21.11。（檔名 test_v21120＝v21.12；test_v2112x 會讀成 v21.1.x。）

  1. V1 具名範圍：v21.11 的 1,865 個名稱逐值相同（相對 1e-9；1×3 → 1×4 者比前 3 格），只有版本字串改變；形狀改變只限列明的名稱。
  2. V1 公式頁：以鍵對齊逐格比較（tools/cmp_v21120.py），差異只在列明的文字格。
  3. V5：四層組合合計＝1（2026／2025 × 付費／免費）；Terra＝0；2025 錨點（V4 清單）逐值不變。
  4. Terra 輸入與結構：Cap_In F 欄、R 節、F 節第 59 列；Price_Frontier 保底；沒有 Terra 的 IF_／IFW_／L1_／RNG_ 名稱；Terra 區只貢獻 0。
  5. GOV 計數、時效旗標、版本字串、Decisions SL69-01、README。"""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

import openpyxl
import pytest

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
sys.path.insert(0, str(REPO / "tools"))
import cmp_v21120  # noqa: E402
import v21120  # noqa: E402

V2111 = REPO / "model" / "archive" / "20261105_Tokenomics_v21.11.xlsx"
VALUE_CHANGED = {"RNG_Version", "RNG_Current"}
NEW_NAMES = {"B4_MixPaid25", "B4_MixFree25", "B4_TerraFam", "CAP_TokGWPaidMix25", "B5_SuccOvr_Terra"}
# 1×3 → 1×4（Terra 欄）與 1×13 → 1×14（Terra 候選列）；RNG_Dem004_*：Alloc P 節指紋多 30 葉格，下方 Q 節下移 30 列（值不變）
SHAPE_OK = ({"B4_PriceIn", "B4_PriceCache", "B4_PriceOut", "B4_Life", "B4_MixPaid", "B4_MixFree", "B4_ISL", "B4_OSL", "B4_EffIn", "B4_EffCache",
             "B4_EffOut", "B4_EffRef", "B4_FrontRef", "B5_H50", "B5_H50Lo", "B5_H50Hi"}
            | {f"B4_Mkt{x}" for x in ("Model", "Vendor", "Country", "Open", "In", "Cache", "Out", "Peak", "Index", "China")})
# 鍵對齊比較中允許的文字差異（頁首、標籤、版本、契約前驅說明；全部非數值）
TEXT_OK = {("README", "A1"), ("README", "B5"), ("Alloc", "A153"), ("Alloc", "G153"), ("Alloc", "G46"), ("Alloc", "C177"), ("Alloc", "C178"),
           ("Amortize", "A2"), ("Amortize", "A39"), ("Amortize", "A40"), ("Amortize", "A42"), ("Cap_In", "A281"), ("Cap_In", "A333"), ("Cap_In", "A60"),
           ("Cap_In", "A90"), ("Checks", "A56"), ("Checks", "B97"), ("Fleet_1GW", "A2"), ("Fleet_1GW", "A30"), ("Fleet_1GW", "A33"), ("Fleet_1GW", "A41"),
           ("Fleet_1GW", "A42"), ("Fleet_1GW_Prod", "A41"), ("Fleet_1GW_Prod", "A42"), ("L1", "C135"), ("Price_Frontier", "A2"), ("Price_Frontier", "A20"),
           ("Price_Frontier", "A21"), ("Price_Frontier", "A25")} \
    | {("Price_Frontier", f"{c}5") for c in "KLMNOP"} \
    | {("Interface", f"W{r}") for r in (195, 196, 197, 198, 201, 318, 358, 360, 361)}      # 契約前驅 Gov_Map 計數：2025 名稱不再讀 Cap_In 第 31／32 列（J5）
ANCHORS_2025 = ["L1_MFleet", "L1_MFleet_Lo", "L1_MFleet_Hi", "L1_LReqFleet", "L1_LReqFleet_Full", "L1_M_2025", "CAP_Price25Mix", "IF_PxEffMix25",
                "AL_PriceFleet25", "IF_AllocQ1", "IF_AllocQ1_R2", "IF_AllocQ2", "IF_AllocServeGW", "IF_AllocImpliedNk", "IF_AllocRDGW", "L1_TokPaid_GW25",
                "L1_TokLedger_GW25", "L1_PayRatio25", "L1_HoldFleet25"]


@pytest.fixture(scope="module")
def cmp():
    out = Path(tempfile.mkdtemp()) / "cmp.json"
    old_argv = sys.argv
    sys.argv = ["cmp_v21120.py", str(V2111), str(model_path()), str(out)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cmp_v21120.main()
    finally:
        sys.argv = old_argv
    return json.loads(out.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


@pytest.fixture(scope="module")
def wbv():
    return openpyxl.load_workbook(model_path(), data_only=True)


def _val(wbf, wbv, n):
    sh, ref = wbf.defined_names[n].attr_text.rsplit("!", 1)
    sh = sh.strip("'")
    ref = ref.replace("$", "")
    if ":" in ref:
        return [c.value for row in wbv[sh][ref] for c in row]
    return wbv[sh][ref].value


# ---------------------------------------------------------------- 1. V1 具名範圍
def test_v21120_names_value_identical(cmp):
    n = cmp["names"]
    assert n["compared"] == 1865 and n["only_old"] == [] and set(n["only_new"]) == NEW_NAMES
    bad = {b[0] for b in n["bad"]}
    assert bad == VALUE_CHANGED, n["bad"]
    moved = set(n["shape_changed"]) - SHAPE_OK
    assert all(x.startswith("RNG_Dem004_") for x in moved), moved


# ---------------------------------------------------------------- 2. V1 公式頁（鍵對齊）
def test_v21120_cells_keyed_identical(cmp):
    diffs = {(s, x[1]) for s, v in cmp["sheets"].items() for x in v.get("first", [])}
    assert all(not v.get("missing_in_new") and not v.get("new_sheet") for v in cmp["sheets"].values())
    assert diffs <= TEXT_OK, sorted(diffs - TEXT_OK)
    kinds = {x[2] for v in cmp["sheets"].values() for x in v.get("first", [])}
    assert kinds <= {"value"}      # 沒有公式 ↔ 常數的種類改變


# ---------------------------------------------------------------- 3. V5 與 2025 錨點
def test_v21120_mix_sums_and_terra_zero(wbf, wbv):
    for n in ("B4_MixPaid", "B4_MixFree", "B4_MixPaid25", "B4_MixFree25"):
        v = _val(wbf, wbv, n)
        assert len(v) == 4 and abs(sum(v) - 1) < 1e-9 and v[3] == 0, (n, v)
    assert _val(wbf, wbv, "B4_MixPaid") == [0.4, 0.45, 0.15, 0] and _val(wbf, wbv, "B4_MixPaid25") == [0.4, 0.45, 0.15, 0]
    assert _val(wbf, wbv, "B4_TerraFam") == 0
    ck = wbf["Checks"]
    rows = [r for r in range(1, ck.max_row + 1) if str(ck.cell(r, 1).value).startswith("Z3")]
    assert len(rows) == 4 and all(wbv["Checks"].cell(r, 4).value == 0 for r in rows)
    gov = wbf.defined_names["GOV_Errors"].attr_text
    assert all(f"D{r}" in str(ck[gov.split("!")[1].replace("$", "")].value) for r in rows)


def test_v21120_2025_anchors_unchanged(wbf, wbv):
    old_f, old_v = openpyxl.load_workbook(V2111), openpyxl.load_workbook(V2111, data_only=True)
    for n in ANCHORS_2025:
        a, b = _val(old_f, old_v, n), _val(wbf, wbv, n)
        a, b = (a if isinstance(a, list) else [a]), (b if isinstance(b, list) else [b])
        assert len(a) == len(b), n
        for x, y in zip(a, b):
            assert x == y or (isinstance(x, (int, float)) and abs(x - y) <= 1e-9 * max(abs(x), abs(y), 1e-300)), (n, x, y)


def test_v21120_2025_basis_wiring(wbf):
    al = wbf["Alloc"]
    assert "B4_MixPaid25" in al["C22"].value and "B4_MixFree25" in al["C23"].value and "B4_MixPaid25" in al["C119"].value
    assert "B4_MixPaid25" in al["C148"].value and "IF_RevGWFleet" not in al["C153"].value
    ci = wbf["Cap_In"]
    assert "B4_MixPaid25" in ci["C281"].value and "CAP_TokGWPaidMix25" in ci["C333"].value and "IF_TokGWPaidMix" not in ci["C333"].value
    assert "INDEX(B4_MixPaid,1,4)" in ci["C90"].value      # 2026 需求路線單價：四項
    for sh in ("Alloc", "Cap_In"):
        txt = [c.value for row in wbf[sh].iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
        assert not any("B4_MixPaid," in t and sh == "Alloc" for t in txt)


# ---------------------------------------------------------------- 4. Terra 輸入與結構
def test_v21120_cap_in_terra(wbf, wbv):
    ci, cv = wbf["Cap_In"], wbv["Cap_In"]
    assert [cv[f"F{r}"].value for r in (6, 7, 8)] == [1, 0.05, 5]
    assert [cv[f"F{r}"].value for r in (22, 23, 24)] == [9, 4, 18]
    assert [cv[f"F{r}"].value for r in (31, 32)] == [0, 0]
    for r in (6, 7, 8, 22, 23, 24, 31, 32):
        assert ci[f"F{r}"].font.color.rgb == "FF0000FF", r      # 藍字輸入
    assert [ci[f"{c}5"].value for c in "FGH"] == ["Terra", "標記", "說明"]
    assert ci["G7"].value == "Verified" and str(ci["H7"].value).startswith("v21.3：Sol 快取＝0.10")      # 說明 G → H，追加文字跟著
    assert "v15.0 O12 口徑" in str(ci["H31"].value) and "v15.0 O12 口徑" in str(ci["G28"].value)
    assert ci["A59"].value == "GPT-6.1 Terra" and ci["I59"].value is None and str(ci["A60"].value).startswith("註：")
    for c in "CDE":      # 既有藍字格位置不變（R3）
        assert ci[f"{c}31"].font.color.rgb == "FF0000FF"


def test_v21120_price_frontier(wbf, wbv):
    pv = wbv["Price_Frontier"]
    r = {pv.cell(i, 1).value: i for i in range(1, pv.max_row + 1) if pv.cell(i, 1).value}
    fr = r["前緣 混合單價（表列；無合格者＝OpenAI 層級模型本身，R7）"]
    assert pv[f"F{fr}"].value == pytest.approx(0.98) and pv[f"F{fr + 1}"].value == "GPT-6.1 Terra"
    pos = r["門檻模型在候選表的位置（Cap_In F 節第幾列；v21.12 起取代「前 3 列」規則）"]
    assert [pv.cell(pos, c).value for c in range(3, 7)] == [1, 2, 3, 14]
    assert "前 3" not in str(wbf["Price_Frontier"]["L6"].value) and f"$C${pos}" in str(wbf["Price_Frontier"]["L6"].value)
    assert _val(wbf, wbv, "B4_EffRef")[3] == pytest.approx(0.784)


def test_v21120_no_terra_contract_names(wbf):
    terra = sorted(n for n in wbf.defined_names if "Terra" in n)
    assert terra == ["B4_TerraFam", "B5_SuccOvr_Terra"], terra
    assert not [n for n in wbf.defined_names if n.startswith(("IF_", "IFW_", "L1_", "RNG_")) and "Terra" in n]


def test_v21120_terra_blocks_zero_contribution(wbv):
    f = wbv["Fleet_1GW"]
    rows = [r for r in range(1, f.max_row + 1) if str(f.cell(r, 1).value).startswith("Terra（中低層） 付費 token")]
    assert len(rows) == 1 and all(f.cell(rows[0], c).value == 0 for c in range(3, 18))
    t = wbv["Theory_Rev"]
    rr = [r for r in range(1, t.max_row + 1) if str(t.cell(r, 1).value).startswith("機隊付費服務營收 Terra")]
    assert len(rr) == 2 and all(t.cell(r, c).value == 0 for r in rr for c in range(3, 18))
    rev = next(r for r in range(1, t.max_row + 1) if str(t.cell(r, 1).value).startswith("理論營收 — OpenAI 有效單價（v22.0 名稱 IF_RevGW_Terra"))
    assert 200 < t[f"M{rev}"].value < 280      # 設計第 5.2 節：Terra VR200 約 240 $B/GW/年


# ---------------------------------------------------------------- 5. GOV、版本、Decisions、README
def test_v21120_gov_counts_and_version(lo, wbf):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 129, 183)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.12") and str(v.get_name("RNG_Current")).endswith("v21.12")
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []
    stem = (REPO / "model" / "CURRENT").read_text(encoding="utf-8").strip()
    assert v21120.VERSION + ".xlsx" == stem
    d = stem.split("_", 1)[0]
    assert wbf["Load_Bearing"]["C3"].value == f"{d[:4]}-{d[4:6]}-{d[6:8]}"


def test_v21120_decisions_readme(wbf):
    d = wbf["Decisions"]
    rr = [r for r in range(5, d.max_row + 1) if d.cell(r, 1).value == "SL69-01"]
    assert len(rr) == 1 and d.cell(rr[0] - 1, 1).value == "SL68-01"
    r = rr[0]
    assert d.cell(r, 2).value == "v21.12" and d.cell(r, 7).value == "v21.12 已建"
    for key in ("B4_MixPaid25", "B4_TerraFam", "R6", "R7", "Checks Z3", "完整第四層級"):
        assert key in d.cell(r, 4).value or key in d.cell(r, 6).value, key
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert b5.startswith("20261105_Tokenomics_v21.12（結構版，底版 v21.11：") and "以下為 v21.11（結構版，底版 v21.10：" in b5
    assert str(rm["A1"].value).startswith("Tokenomics v21.12")

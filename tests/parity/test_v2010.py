"""v20.1 LifeSelf 主口徑（工作單 docs/workorders/20261023_v20.1_LifeSelf主口徑.md r0）專屬測試。讀 LibreOffice 重算後的值。

  1. W1：8 個 IFW_*_LifeSelf 的基準欄 40 值＝工作單事前值（相對 1e-3）；全部 120 格＝_Prod × 該世代 L1_LDiscGen × L1_M（相對 1e-9）；L1_LDiscGen 四格＝Cap_In C322:F322。
  2. W2：L1_PriceReqBE（＋_Lo／_Hi）＝工作單事前值（工作單事前值由四捨五入的乘數算出，容差 3e-5 相對）且＝v20.0 值 × L1_LTotal ÷ L1_LTotalFleetVDisc（相對 1e-9，精確換算）。
  3. W3：Cap_In 第 238 列判讀字樣、C233 不變、第 313 列數值不變、標籤文字。
  4. 不回流（Interface、Load_Bearing、Gov_Map 以外無公式引用 _LifeSelf）；Hopper SLO 不可達情境回傳文字不出錯誤值；L 輸入（WACC）變動時 LifeSelf 隨之改變。
  5. 既有名稱數值不變（對封存的 v20.0）：只有 8 個 LifeSelf、L1_PriceReqBE 三格與版本字串；逐格差異只落在工作單預期範圍。
  6. 記錄：Decisions SL56-01、README、公式 ISNUMBER 防護。
"""
import re
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path
from v2170_allow import v213_cells, strip, csv_value_cells      # v21.3：v21.2 → v21.3 的逐格差異集合（規則同 test_v2130，只到工作單 W1–W6 列明的格）
from test_v2120 import CHANGED as V2120_CHANGED, REVERT as SB_OLD      # v21.2：AL_SpendBasis 改 1.8 的預期變動名稱（44 個）與舊值輸入
from test_v2130 import CHANGED as _V2130_CHANGED, LABEL_NAMES as _V2130_LABEL, INDEX_NAMES as _V2130_INDEX, REVERT as R213_OLD      # v21.3：機架價低端 7.5／Sol 快取價 0.10 的預期變動名稱與舊值輸入（test_v2130 看守）
V2130_CHANGED = _V2130_CHANGED | _V2130_LABEL | _V2130_INDEX | {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi", "SRC_PRC_049"}      # v21.3：171 個值變動名稱＋Cap_In A47 改名連帶的 2 個文字名稱＋SRC_Index 延伸的 4 個 IDX_Src*＋新 SRC 紀錄 4 個名稱＋SRC_PRC_049（舊值輸入 R213_OLD 把它設回 0.2 的副作用；v21.3 起 Active）
from test_v2110 import NEW_NAMES as V2110_NEW_NAMES      # v21.1：+18 個新名稱（test_v2110 看守）

REPO = Path(__file__).resolve().parents[2]
V200 = REPO / "model" / "archive" / "20261022_Tokenomics_v20.0.xlsx"

STEMS = ["RevGW_Luna", "RevGW_Sol", "RevGW_Astra", "RevGWFleet", "RevGWFront_Luna", "RevGWFront_Sol", "RevGWFront_Astra", "RevGWFleetFront"]
G_OF = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4]      # C..Q；Rubin Ultra（O–Q）取 VR200
BASE_IDX = [1, 4, 7, 10, 13]      # D／G／J／M／P
WO = {      # 工作單 W1 事前值（Hopper, GB200, GB300, VR200, Rubin Ultra；$B/GW/年）
    "IFW_RevGW_Luna_LifeSelf": (5.611, 25.385, 31.361, 45.346, 61.087),      # v21.3：(5.561, 25.157, 31.079, 44.939, 60.539) → 新值（Sol 快取價 0.20 → 0.10：m +0.9%，test_v2130 看守）
    "IFW_RevGW_Sol_LifeSelf": (28.831, 125.373, 154.980, 233.672, 318.507),      # v21.3：(29.285, 127.347, 157.420, 237.351, 323.521) → 新值（同上）
    "IFW_RevGW_Astra_LifeSelf": (27.144, 126.644, 139.139, 252.842, 359.575),      # v21.3：(26.901, 125.507, 137.890, 250.572, 356.347) → 新值（同上）
    "IFW_RevGWFleet_LifeSelf": (5.766, 26.213, 30.209, 50.638, 70.598),
    "IFW_RevGWFront_Luna_LifeSelf": (5.611, 25.385, 31.361, 45.346, 61.087),      # v21.3：同 IFW_RevGW_Luna_LifeSelf
    "IFW_RevGWFront_Sol_LifeSelf": (28.831, 125.373, 154.980, 233.672, 318.507),      # v21.3：同 IFW_RevGW_Sol_LifeSelf
    "IFW_RevGWFront_Astra_LifeSelf": (26.153, 122.021, 134.060, 243.612, 346.449),      # v21.3：(25.919, 120.925, 132.856, 241.425, 343.339) → 新值（同上）
    "IFW_RevGWFleetFront_LifeSelf": (5.637, 25.625, 29.531, 49.501, 69.014),
}
WO_PRICE = {"L1_PriceReqBE": 1.63424, "L1_PriceReqBE_Lo": 1.08913, "L1_PriceReqBE_Hi": 2.58579}      # v21.3：Hi 2.59072 → 2.58579（機架價低端 7.8 → 7.5：L1_LTotalFleetVDisc_Lo 0.47853 → 0.47944，Hi ∝ 1 ÷ L 低端；test_v2130 看守）
CHANGED_NAMES = {f"IFW_{s}_LifeSelf" for s in STEMS} | {"L1_PriceReqBE", "L1_PriceReqBE_Lo", "L1_PriceReqBE_Hi"}
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
SKIP = ("RNG_", "IDX_", "GOV_", "IFC_")      # v21.0：IFC_ 契約欄範圍隨 O／P 節新列延伸
SLO_UNREACH = {"CTL_ProdDerate": 0.3}      # 生產折減 0.3：Hopper 欄 _Prod 的營收列為文字（SLO 不可達）；Serving!C18 的不可達情境（z1_c18_07_text）下 _Prod 營收列仍為數字
WACC_UP = {"Inputs!E28": 0.15}
PREWARM = {"test_v2010_l_input_propagates": [WACC_UP], "test_v2010_slo_unreachable_returns_text": [SLO_UNREACH]}


def _flat(v):
    if isinstance(v, (list, tuple)):
        return [x for r in v for x in _flat(r)]
    return [v]


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ---------------------------------------------------------------- 1. W1
@pytest.mark.parametrize("name", sorted(WO))
def test_v2010_w1_workorder_values(lo, name):
    got = _flat(lo.view({}).get_name(name))
    assert len(got) == 15
    for i, w in zip(BASE_IDX, WO[name]):
        assert _num(got[i]) and abs(got[i] / w - 1) <= 1e-3, (name, i, got[i], w)


def test_v2010_w1_all_cells_formula(lo):
    """120 格＝_Prod × 該世代折現 L × L1_M（相對 1e-9）；L1_LDiscGen 四格＝Cap_In C322:F322。"""
    v = lo.view({})
    ld = _flat(v.get_name("L1_LDiscGen"))
    assert len(ld) == 4 and all(_num(x) and 0 < x < 1.5 for x in ld)
    assert v.names["L1_LDiscGen"].replace("'", "") in ("Cap_In!$C$322:$F$322",)
    assert [v.get("Cap_In", f"{c}322") for c in "CDEF"] == ld
    assert ld[2] == pytest.approx(ld[3], rel=1e-12)      # 現行 GB300 與 VR200 起點相同
    m = v.get_name("L1_M")
    n = 0
    for s in STEMS:
        ls, pr = _flat(v.get_name(f"IFW_{s}_LifeSelf")), _flat(v.get_name(f"IFW_{s}_Prod"))
        assert len(ls) == len(pr) == 15
        for k, (a, b) in enumerate(zip(ls, pr)):
            want = b * ld[G_OF[k] - 1] * m
            assert _num(a) and abs(a - want) <= 1e-9 * max(abs(want), 1e-300), (s, k, a, want)
            n += 1
    assert n == 120
    # Rubin Ultra 與 VR200 同 L：比值相同
    for s in STEMS:
        ls, pr = _flat(v.get_name(f"IFW_{s}_LifeSelf")), _flat(v.get_name(f"IFW_{s}_Prod"))
        assert ls[13] / pr[13] == pytest.approx(ls[10] / pr[10], rel=1e-12)


# ---------------------------------------------------------------- 2. W2
@pytest.mark.parametrize("name", sorted(WO_PRICE))
def test_v2010_w2_workorder_values(lo, name):
    g = _flat(lo.view({}).get_name(name))[0]
    # 工作單事前值由四捨五入到 5–6 位的乘數算出（1.87980 × 0.659506 ÷ 0.758597），與活頁簿精確值差約 5e-6 相對；列入報告待判斷 1
    assert abs(g / WO_PRICE[name] - 1) <= 3e-5, (name, g, WO_PRICE[name])


def test_v2010_w2_exact_conversion(lo):
    """新值＝v20.0 值 × 舊 L ÷ 新 L（精確換算，相對 1e-9）。注意低／高端的 L 方向：_Lo 配 L 高端、_Hi 配 L 低端。"""
    pw = openpyxl.load_workbook(V200, data_only=True)

    def old(name):
        sh, c = pw.defined_names[name].attr_text.split("!")
        return pw[sh.strip("'")][c.replace("$", "")].value
    v = lo.view({})
    pairs = {"L1_PriceReqBE": ("L1_LTotal", "L1_LTotalFleetVDisc"), "L1_PriceReqBE_Lo": ("L1_LTotal_Hi", "L1_LTotalFleetVDisc_Hi"), "L1_PriceReqBE_Hi": ("L1_LTotal_Lo", "L1_LTotalFleetVDisc_Lo")}
    for nm, (a, b) in pairs.items():
        want = old(nm) * old(a) / (_flat(v.get_name(b))[0] if nm == "L1_PriceReqBE_Hi" else old(b))      # v21.3：Hi 的分母 L1_LTotalFleetVDisc_Lo 隨機架價低端 7.5 變動（0.47853 → 0.47944），改讀現值；分子 L1_LTotal_Lo（v20.0 值）是舊 Hi 的換算基礎，不隨之改（test_v2130 看守）
        got = _flat(v.get_name(nm))[0]
        assert abs(got / want - 1) <= 1e-9, (nm, got, want)
    # 低 < 基準 < 高；L 取主口徑
    lo_, bs, hi_ = (_flat(v.get_name(n))[0] for n in ("L1_PriceReqBE_Lo", "L1_PriceReqBE", "L1_PriceReqBE_Hi"))
    assert lo_ < bs < hi_


# ---------------------------------------------------------------- 3. W3
def test_v2010_w3_judgement_and_unchanged_cells(lo):
    v = lo.view({})
    assert v.get("Cap_In", "C238").startswith("區間內（0.3–1.0）")      # 主口徑 L 0.759
    assert v.get("Cap_In", "D238").startswith("區間內") and v.get("Cap_In", "E238").startswith("區間外")      # 低端 0.479 內、高端 1.138 外（區間 0.3–1.0）
    pw = openpyxl.load_workbook(V200, data_only=True)
    for c in "CDE":
        if ("Cap_In", f"{c}233") in csv_value_cells():      # v21.3：Cap_In D233 隨 L 低端變動（預期變動 CSV；舊值須等於 v20.0 值）
            was, now = csv_value_cells()[("Cap_In", f"{c}233")]
            assert abs(pw["Cap_In"][f"{c}233"].value / was - 1) <= 1e-9 and abs(v.get("Cap_In", f"{c}233") / now - 1) <= 1e-9
            continue
        assert v.get("Cap_In", f"{c}233") == pw["Cap_In"][f"{c}233"].value      # C233 本身不改
    assert _flat(v.get_name("L1_LTotalV")) == [pw["Cap_In"][f"{c}313"].value for c in "CDEF"]      # 第 313 列數值不改
    assert _flat(v.get_name("L1_LTotalFleetVDisc"))[0] == pytest.approx(0.758597367273996, rel=1e-9)


# ---------------------------------------------------------------- 4. 不回流、不可達、輸入傳遞
def test_v2010_no_reference_outside(wbf):
    bad = []
    for ws in wbf:
        if ws.title in {"Interface", "Load_Bearing", "Gov_Map"}:
            continue
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=") and "_LifeSelf" in c.value:
                    bad.append((ws.title, c.coordinate))
    assert not bad, bad[:5]
    # L1_LDiscGen 只被 Interface LifeSelf 列引用
    users = {ws.title for ws in wbf for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=") and "L1_LDiscGen" in c.value}
    assert users <= {"Interface", "Load_Bearing", "Gov_Map"}, users


def test_v2010_slo_unreachable_returns_text(lo):
    v = lo.view(SLO_UNREACH)
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []
    n_text = 0
    for s in STEMS:
        ls, pr = _flat(v.get_name(f"IFW_{s}_LifeSelf")), _flat(v.get_name(f"IFW_{s}_Prod"))
        for a, b in zip(ls, pr):
            if not _num(b):
                assert a == b and isinstance(a, str) and not a.startswith("#"), (s, a, b)
                n_text += 1
    assert n_text >= 24      # 此情境 Hopper 三欄 _Prod 營收列為文字（SLO 不可達）：8 個名稱 × 3 欄


def test_v2010_l_input_propagates(lo):
    base, hi = lo.view({}), lo.view(WACC_UP)
    b, h = _flat(base.get_name("L1_LDiscGen")), _flat(hi.get_name("L1_LDiscGen"))
    assert b != h
    m = _flat(hi.get_name("L1_M"))[0]
    ls, pr = _flat(hi.get_name("IFW_RevGW_Sol_LifeSelf")), _flat(hi.get_name("IFW_RevGW_Sol_Prod"))
    for k in (1, 4, 7, 10):
        assert ls[k] == pytest.approx(pr[k] * h[G_OF[k] - 1] * m, rel=1e-9)
    errs = [(s, c) for (s, c), x in hi.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 5. 既有名稱不變（對封存的 v20.0）
def test_v2010_existing_names_unchanged(lo):
    pw = openpyxl.load_workbook(V200, data_only=True)
    v = lo.view({})
    bad, n = [], 0
    for name, d in pw.defined_names.items():
        if name.startswith(SKIP) or name in VERSION_NAMES or name in CHANGED_NAMES or name in V2120_CHANGED or name in V2130_CHANGED or "!" not in d.attr_text or "," in d.attr_text:      # v21.3：+171 個機架價低端／Sol 快取價預期變動名稱（test_v2130 看守）
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(name))
        n += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
    assert n > 1350
      # v21.3：扣除 171 個預期變動名稱後的比較數下修（原 > 1500）    assert bad == [], bad[:20]
    # 被改的名稱確實改了
    for nm in CHANGED_NAMES:
        sh, rg = pw.defined_names[nm].attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        assert not all(_eq(a, b) for a, b in zip(want, _flat(v.get_name(nm)))), nm


# ---------------------------------------------------------------- 6. 記錄、公式、逐格差異
@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


def _rows(ws, col, val):
    return [r for r in range(5, ws.max_row + 1) if ws.cell(r, col).value == val]


def test_v2010_records(wbf):
    d = wbf["Decisions"]
    rd = _rows(d, 1, "SL56-01")
    assert len(rd) == 1 and d.cell(rd[0], 2).value == "v20.1" and d.cell(rd[0], 7).value == "v20.1 已建" and len(_rows(d, 1, "SL55-01")) == 1
    txt = d.cell(rd[0], 4).value + d.cell(rd[0], 6).value
    for key in ("本来就是应该用自己每个世代来算的", "m＝實收單價 ÷ 有效牌價", "07:34", "J1", "J6", "08:54"):
        assert key in txt, key
    rm = wbf["README"]
    assert "v21.0（主版：" in str(rm["B5"].value) and "v20.1（次版，底版 v20.0：" in str(rm["B5"].value) and "v20.0（主版：" in str(rm["B5"].value) and str(rm["A1"].value).startswith("Tokenomics v21.")
    rows = [x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v20.1 LifeSelf 主口徑"]
    assert len(rows) == 1 and "L1_LDiscGen" in rm.cell(rows[0], 2).value and "L1_LTotalFleetVDisc" in rm.cell(rows[0], 2).value
    assert wbf.defined_names["L1_LDiscGen"].attr_text == "Cap_In!$C$322:$F$322"


def test_v2010_formulas_and_labels(wbf):
    ws = wbf["Interface"]
    for stem in STEMS:
        sh, rg = wbf.defined_names[f"IFW_{stem}_LifeSelf"].attr_text.split("!")
        r = int(re.findall(r"\$(\d+)", rg)[0])
        assert "（L1_LDiscGen、L1_M）" in ws[f"A{r}"].value and "L1_LTotal" not in ws[f"A{r}"].value
        sh2, rg2 = wbf.defined_names[f"IFW_{stem}_Prod"].attr_text.split("!")
        p = int(re.findall(r"\$(\d+)", rg2)[0])
        for k, col in enumerate("CDEFGHIJKLMNOPQ"):
            f = ws[f"{col}{r}"].value
            g = G_OF[k]
            assert f == (f'=IF(ISNUMBER({col}{p}),IF(AND(ISNUMBER(INDEX(L1_LDiscGen,1,{g})),ISNUMBER(L1_M)),{col}{p}*INDEX(L1_LDiscGen,1,{g})*L1_M,"L、m 非數字（本情境）"),{col}{p})'), (col, r, f)
        assert "O–Q" in ws[f"Z{r}"].value
    t = ws[f"A{int(re.findall(r'[$](\d+)', wbf.defined_names['IFW_RevGW_Luna_LifeSelf'].attr_text)[0]) - 1}"].value
    assert t.startswith("L. 情境：自算 L、m（v20.1 起）：") and "L1_LDiscGen" in t and "v10.0–v20.0 口徑" in t
    l1 = wbf["L1"]
    r = int(wbf.defined_names["L1_PriceReqBE"].attr_text.split("$")[-1])
    assert l1[f"B{r}"].value == "回本所需實收單價（L＝L1_LTotalFleetVDisc，世代起點＋折現主口徑；v20.1 起）"
    assert l1[f"C{r}"].value.endswith("｜成本範圍仍為 L1_FleetBreakeven2025（v20.0 全部算力口徑未套用，見待判斷）")
    for c, nm in zip("DEF", ("L1_LTotalFleetVDisc", "L1_LTotalFleetVDisc_Hi", "L1_LTotalFleetVDisc_Lo")):
        f = l1[f"{c}{r}"].value
        assert f"ISNUMBER({nm})" in f and f.endswith(f"/{nm},\"L 非數字（本情境）\")") and "L1_LTotal," not in f and "L1_LTotal_" not in f.replace("L1_LTotalFleetVDisc_", "")
    ci = wbf["Cap_In"]
    assert ci["A238"].value.startswith("判讀：主口徑 L（L1_LTotalFleetVDisc，世代起點＋折現）對 Gov_Map CTL_PriceLife 區間") and ci["A238"].value.endswith("v20.1 前讀 L_total")
    for c, nm in zip("CDE", ("L1_LTotalFleetVDisc", "L1_LTotalFleetVDisc_Lo", "L1_LTotalFleetVDisc_Hi")):
        f = ci[f"{c}238"].value
        assert f.startswith(f"=IF(ISNUMBER({nm}),") and f"{c}233" not in f
    assert ci["A313"].value.startswith("各世代 L（現行：四格皆為 L1_LTotal，2025＝第 0 年，非各世代自身起點") and ci["A313"].value.endswith("→ L1_LTotalV")
    assert ci["C313"].value == "=L1_LTotal"
    k = next(ws.cell(rr, 1).value for rr in range(300, 340) if str(ws.cell(rr, 1).value).startswith("K. 服務 GW 的 token 路線對照"))
    assert "IF_AllocServeGW 為支出路線主口徑（v20.0 起 2025 校準主口徑改為 GW 優先 L1_ServeGW_GW25；支出路線為對照）" in k


def test_v2010_diffs_only_expected_vs_v200():
    a, b = openpyxl.load_workbook(V200), openpyxl.load_workbook(model_path())
    assert a.sheetnames == b.sheetnames
    d = {}
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y and (x is not None or ws.title == "Interface" and c == 26):
                    d.setdefault(ws.title, []).append((ws.cell(r, c).coordinate, x, y))
    allowed = {"Cap_In", "Decisions", "Gov_Map", "Interface", "L1", "Load_Bearing", "README", "SRC_Index", "Alloc", "Checks", "NonNV", "Alloc_In", "SRC_Demand", "DB_Evidence"}      # v21.0：Checks D118／D119／E118（範圍延伸）、NonNV M5:M9（test_v2100 看守）； v21.1：Alloc_In G24、SRC_Demand W10（test_v2110 看守）
    assert set(d) <= allowed | set(v213_cells()), set(d) - allowed - set(v213_cells())      # v21.3：另加 Spec_Rack／SRC_HW／SRC_Price（W1／W2，test_v2130 看守）
    # Cap_In 既有格：只有 A238、C238:E238、A313
    assert strip("Cap_In", sorted(t[0] for t in d["Cap_In"])) == strip("Cap_In", ["A238", "A313", "C238", "D238", "E238", "G28"]), sorted(t[0] for t in d["Cap_In"])      # v21.3：扣掉 A47／D7／F47／G7（W2，test_v2130 看守）      # v21.2：G28（test_v2120 看守）
    # L1 既有格：只有第 93 列的 B／C／D／E／F／H（以及指向它的說明欄不變）
    r93 = int(b.defined_names["L1_PriceReqBE"].attr_text.split("$")[-1])
    assert sorted({int(re.sub(r"[A-Z]+", "", t[0])) for t in d["L1"] if t[0] != "T4"}) == [71, r93, *range(128, 137)], d["L1"][:3]      # v21.4：第 128–136 列 I（W1／W2，test_v2140 看守）； v21.3：第 128–131 列 I（W5，test_v2130 看守）； v21.2：第 71 列 C／H（test_v2120 看守）      # v21.1：T4 表頭（增「情境」性質）由 test_v2110 看守
    assert {re.sub(r"\d+", "", t[0]) for t in d["L1"] if t[0] != "T4"} <= {"B", "C", "D", "E", "F", "H", "I", "J", "K"}      # v21.0：第 93 列 I／J／K（test_v2100 看守）
    # Interface：LifeSelf 列（C:Q 與 A）、第 320 列標題、K 節標題、契約元資料欄（R／V／W）、Z 欄說明
    cols = {re.sub(r"\d+", "", t[0]) for t in d["Interface"]}
    assert cols <= set("ACDEFGHIJKLMNOPQ") | {"R", "S", "T", "U", "V", "W", "Z"}, cols
    # 名稱：只新增 L1_LDiscGen
    na, nb = set(a.defined_names), set(b.defined_names)
    assert na <= nb and nb - na == {"L1_LDiscGen"} | {"IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU"} | {f"IF_NonNV_{k}_{x}" for k in ("Out", "Hold") for x in ("AMD", "TPU", "Trn", "CS", "OAI")} | V2110_NEW_NAMES | {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi"}, sorted(nb - na)      # v21.3：另加 SRC_HW_098／099 與 099 的 _Lo／_Hi（W1，test_v2130 看守）； v21.0：+13（test_v2100 看守）
    changed = {k for k in na if a.defined_names[k].attr_text != b.defined_names[k].attr_text}
    assert all(k.startswith(("IDX_", "RNG_", "GOV_", "IFC_")) for k in changed), sorted(changed)[:10]      # v21.0：IFC_ 契約欄範圍延伸

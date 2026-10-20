"""v14.1 修補（工作單 docs/workorders/20261017_v14.1修補.md r1）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

R1  機隊 m 低端改用『同欄下限』：Cap_In 第 119 列各欄＝MAX(該欄點估計, 該欄第 121 列)。機制必須在 Excel 公式中（不是 Python 端）。
    專屬測試：(a) 低端欄 token 被推過它自己那一欄的上限時，L1_MFleet_Lo 必須等於同欄下限（Cap_In D121）；
              (b) 點估計高於下限時，L1_MFleet_Lo 等於點估計（下限不亂截斷）；(c) 基準欄同樣適用；
              (d) 基準值與依賴鏈以外的契約名稱與 v14.0 逐格相同。
R2~R6 的清空、註記與標籤更正：逐格斷言。
"""
import re
import sys
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V152_CHANGED = set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v152_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v153_changed_names.json", encoding="utf-8"))["names"])      # v15.3：另併入 v15.2→v15.3 的預期變動名單（E1／E2／C2／D1；test_v1530 逐名稱釘住）
sys.path.insert(0, str(REPO / "builder"))
V140_PREV = REPO / "model" / "archive" / "20261017_Tokenomics_v14.0.xlsx"      # v14.0（LibreOffice 重算存檔）
CONTRACT_PREFIX = ("IF_", "IFW_", "IFC_", "L1_", "CHK_", "CAP_", "RNG_", "GOV_")
V150_CHANGED = {"CHK_VerifyTotal", "CHK_VerifyPass", "GOV_Info", "GOV_Table"}      # v15.0 預期變動：O9（V16 移出驗證計數 22／14 → 21／13）、O14（L1 外部對照換算，Info 184 → 182，GOV_Table 為其明細表）
R1_CHANGED = {"L1_MFleet_Lo": 0.242723485975401, "L1_PriceRealFleet_Lo": 0.329948597895522, "L1_LReqFleet_Hi": 3.80958617071992}      # v15.2 B2／B3 後的值；      # v14.1 新值（舊值 0.1838665514316／0.308939934377431／4.45464077137931）
R2_CHANGED = {"CHK_VerifyTotal", "CHK_VerifyPass"}
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
P25_V142 = {"L1_MFleet_P25Lo", "L1_MFleet_P25Hi"}      # v14.2 S1：預期變動（新值與下限由 test_v1420.py 逐一斷言）
SC_HI = {"Alloc_In!E24": 1.0}      # 低端欄（token 取高）的實際利用率 0.65 → 1.0：點估計 token 再高 1.54 倍
SC_LO_OK = {"Alloc_In!E24": 0.3}      # 0.65 → 0.3：點估計 token 降到上限之下（點估計 m 0.398 > 下限 0.215）
SC_BASE = {"Alloc_In!C24": 1.5}      # 基準欄的實際利用率 0.41 → 1.5：基準欄點估計 m（約 0.111）低於基準欄下限 0.301
PREWARM = {
    "test_v1410_r1_floor_binds_low_end_column": [SC_HI],
    "test_v1410_r1_floor_does_not_cut_when_point_above_floor": [SC_LO_OK],
    "test_v1410_r1_floor_applies_to_base_column": [SC_BASE],
}


def _flat(v):
    if isinstance(v, list):
        return [x for r in v for x in _flat(r)]
    return [v]


def _same(a, b):
    a = None if a == "" else a
    b = None if b == "" else b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


def _raw_m(v, col):
    """該欄的『點估計 m』（不含下限截斷）：營收 ÷（機隊付費 token × 2025 年度機隊口徑單價），全部取 LibreOffice 重算值。"""
    return v.get_name("SRC_DEM_007") * 1e9 / (v.get("Cap_In", f"{col}116") * v.get_name("AL_PriceFleet25"))


# ── R1 ──
def test_v1410_r1_mechanism_is_an_excel_formula(wbf):
    """機制在 Excel 公式（Cap_In 第 119 列各欄 MAX(點估計, 同欄第 121 列)），不是 Python 端計算；L1 第 78 列仍直接連結 Cap_In 第 119 列。"""
    ci = wbf["Cap_In"]
    for c in "CDE":
        f = ci[f"{c}119"].value
        assert isinstance(f, str) and f.startswith("=") and "MAX(" in f and f"{c}121" in f and f"{c}116" in f, (c, f)
    assert wbf["L1"]["D78"].value == "=Cap_In!$C$119" and wbf["L1"]["E78"].value == "=Cap_In!$D$119" and wbf["L1"]["F78"].value == "=Cap_In!$E$119"
    assert "L1_MFleetFloor" not in wbf.defined_names      # 不升級為契約名稱（下游不讀第 121 列）
    assert "下限截斷：v14.1 起，低端不得低於同欄物理下限" in ci["G119"].value or "下限截斷" in ci["G119"].value


def test_v1410_r1_base_values(lo):
    """基準：L1_MFleet [Lo, 基準, Hi] 由 [0.1839, 0.4073, 1.1788] 改為 [0.2154, 0.4073, 1.1788]；基準與高端不變，低端＝D121。"""
    v = lo.view({})
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-12 and abs(v.get_name("L1_MFleet_Hi") - 1.33130310709466) < 1e-12
    assert abs(v.get_name("L1_MFleet_Lo") - 0.242723485975401) < 1e-12 and abs(v.get("Cap_In", "D119") - v.get("Cap_In", "D121")) < 1e-15
    assert v.get_name("L1_MFleet_Lo") < v.get_name("L1_MFleet") < v.get_name("L1_MFleet_Hi")
    for n, w in R1_CHANGED.items():
        assert abs(v.get_name(n) - w) <= 1e-12 * w, n
    # 依賴鏈的關係式
    assert abs(v.get_name("L1_PriceRealFleet_Lo") - v.get_name("L1_MFleet_Lo") * v.get_name("AL_PriceFleet25")) < 1e-12
    assert abs(v.get_name("L1_LReqFleet_Hi") - v.get("Cap_In", "E240")) < 1e-12
    assert abs(v.get("Cap_In", "E240") - v.get_name("L1_FleetBreakeven2025") / (v.get_name("IF_Util") * v.get_name("CTL_ProdDerate") * v.get_name("L1_MFleet_Lo"))) < 1e-9


def test_v1410_r1_floor_binds_low_end_column(lo):
    """必須能截斷：低端欄（token 取高）的利用率推高，點估計 token 超過同欄上限、點估計 m 低於同欄下限；L1_MFleet_Lo 必須等於同欄下限（D121），不是點估計。"""
    v = lo.view(SC_HI)
    raw = _raw_m(v, "D")
    floor = v.get("Cap_In", "D121")
    assert v.get("Cap_In", "D116") > v.get("Cap_In", "D118")      # token 超過同欄上限
    assert raw < floor * 0.7, (raw, floor)      # 點估計遠低於下限（沒有截斷時 L1_MFleet_Lo 會是 raw）
    assert abs(v.get_name("L1_MFleet_Lo") - floor) <= 1e-12 and abs(floor - 0.242723485975401) < 1e-12      # 同欄下限不受該利用率影響
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-12 and abs(v.get_name("L1_MFleet_Hi") - 1.33130310709466) < 1e-12


def test_v1410_r1_floor_does_not_cut_when_point_above_floor(lo):
    """下限不亂截斷：低端欄 token 降到同欄上限之下，點估計 m 高於同欄下限，L1_MFleet_Lo＝點估計。"""
    v = lo.view(SC_LO_OK)
    raw = _raw_m(v, "D")
    floor = v.get("Cap_In", "D121")
    assert v.get("Cap_In", "D116") < v.get("Cap_In", "D118") and raw > floor
    assert abs(v.get_name("L1_MFleet_Lo") - raw) <= 1e-9 * raw


def test_v1410_r1_floor_applies_to_base_column(lo):
    """『各欄』都適用：基準欄的點估計 m 低於基準欄下限（0.301）時，L1_MFleet（基準）＝基準欄下限。"""
    v = lo.view(SC_BASE)
    raw = _raw_m(v, "C")
    floor = v.get("Cap_In", "C121")
    assert raw < floor and abs(v.get_name("L1_MFleet") - floor) <= 1e-12 and abs(floor - 0.339147884513574) < 1e-12


def test_v1410_names_off_the_chain_unchanged(lo):
    """依賴鏈以外的契約名稱（IF_／IFW_／IFC_／L1_／CHK_／CAP_／RNG_／GOV_）與 v14.0 逐格值相同；
    例外只有：R1 的三個名稱（上方斷言新值）、R2 的 CHK_VerifyTotal／Pass（24／16 → 22／14）、版本字串。"""
    prev = openpyxl.load_workbook(V140_PREV, data_only=True)
    v = lo.view({})
    keep = [n for n in prev.defined_names if n.startswith(CONTRACT_PREFIX) and n not in R1_CHANGED and n not in R2_CHANGED and n not in VERSION_NAMES and n not in P25_V142 and n not in V150_CHANGED and n not in V152_CHANGED]
    assert len(keep) >= 340, len(keep)      # v15.2：同上；原 ≥ 700      # 789 個名稱中的契約前綴者，扣除上列例外後仍有 742 個
    for n in keep:
        sh, rg = prev.defined_names[n].attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        if n.startswith("IFC_"):      # v15.0：Interface 第 193 列新增（IF_FrontSuccVRQual 的 IFC_ 中繼資料）；舊版該列為空，其餘逐格須相同
            skip = {193 - r1}
            assert len(want) == len(got) and all(_same(a, b) for i, (a, b) in enumerate(zip(want, got)) if i not in skip) and all(want[i] in (None, "") for i in skip), n
            continue
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n
    for n in ("IF_AllocQ1", "IF_AllocRDGW", "IF_AllocServeGW", "IF_AllocQ2"):      # 工作單點名的名稱
        assert n not in R1_CHANGED
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 133, 182)      # v15.0：Info 184 → 182（O14 L1 外部對照換算，P 欄旗標淨減 2）      # v17.2：W1 278 → 131（W1 第二來源 B1：A 86、C1 53、Q11 8 離開；預期變動）


# ── R3 ──
def test_v1410_r3_har_in_vendor_flags_cleared(wbf, lo):
    ws, gm = wbf["Har_In"], wbf["Gov_Map"]
    pc = next(c for c in range(3, ws.max_column + 2) if ws.cell(3, c).value == "用途")
    for r in (20, 32, 44):
        assert all(ws.cell(r, c).value is None for c in range(3, 8)), r
    assert "已清空（v14.1，R3）" in str(ws.cell(20, pc).value) and "已清空（v14.1，R3）" in str(ws.cell(32, pc).value)
    assert ws["H20"].value == "Verified" and ws["H32"].value == "Assumed"      # 來源與標記欄原文保留（CLAUDE.md 第 6 節）
    for rng in ("C20:G20", "C32:G32"):
        rows = [r for r in range(5, gm.max_row + 1) if (gm[f"C{r}"].value, gm[f"D{r}"].value) == ("Har_In", rng)]
        assert len(rows) == 1 and "v14.1 已移除" in str(gm[f"N{rows[0]}"].value) and "v13.1 D15 補登" in str(gm[f"N{rows[0]}"].value), rng
    v = lo.view({})
    assert v.get_name("GOV_Errors") == 0


# ── R4 ──
def test_v1410_r4_deleted_row_labels_cleared_and_listed(wbf):
    import json
    data = json.loads((REPO / "builder" / "v1400_data.json").read_text(encoding="utf-8"))["delete"]
    assert len(data) == 73
    for e in data:
        ws = wbf[e["sheet"]]
        assert ws.cell(e["row"], 1).value is None and ws.cell(e["row"], 2).value is None, (e["sheet"], e["row"])
    dec = wbf["Decisions"]
    row = next(r for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value == "SL44-4")
    txt = str(dec.cell(row, 4).value)
    for e in data:      # 清單可追溯：每一列的工作表、列號與原 A 欄標籤都在 Decisions
        assert f"{e['sheet']}!{e['row']}：" in txt and str(e["label"]) in txt, (e["sheet"], e["row"])


# ── R5 ──
R5_CELLS = [f"C{r}" for r in [185] + list(range(187, 194)) + list(range(196, 203)) + [205] + list(range(216, 223))] + ["G175"]


def test_v1410_r5_cap_in_cells_cleared_and_unread(wbf):
    from deps import Deps
    ci = wbf["Cap_In"]
    assert len(R5_CELLS) == 24 and all(ci[c].value is None for c in R5_CELLS)
    D = Deps(wbf)
    gone = {("Cap_In", c) for c in R5_CELLS}
    for k in D.formulas:      # 清空後不得有任何公式還在讀這 24 格（讀到空格會悄悄變 0）
        assert not (D.direct(k) & gone), (k, sorted(D.direct(k) & gone))
    for n, d in wbf.defined_names.items():
        assert not any(("Cap_In", c) in gone for c in [x[1] for x in D._resolve("", d.attr_text) if x[0] == "Cap_In"]), n
    dec = wbf["Decisions"]
    row = next(r for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value == "SL44-5")
    assert "Cap_In!C185：" in str(dec.cell(row, 4).value) and "Cap_In!G175：" in str(dec.cell(row, 4).value)


# ── R6 ──
def test_v1410_r6_small_items(wbf):
    gm = wbf["Gov_Map"]
    row = next(r for r in range(5, gm.max_row + 1) if gm[f"A{r}"].value == "GM629")
    assert "v14.0 已清空" in str(gm[f"N{row}"].value) and "v5.35 B2" in str(gm[f"N{row}"].value)      # 原文保留
    for sh, r, key in (("Cap_In", 76, "目前沒有任何公式讀取"), ("Training", 122, "實際讀第 120 列"), ("Price_Frontier", 27, "實際讀第 46 列")):
        ws = wbf[sh]
        pc = next(c for c in range(3, ws.max_column + 2) if ws.cell(3, c).value == "用途")
        assert key in str(ws.cell(r, pc).value), (sh, r)
    ci = wbf["Cap_In"]
    for r in (206, 207, 208, 209, 223):
        t = str(ci[f"H{r}"].value)
        assert t.startswith("錨點：以本列 C–F 欄現值為準") and not re.search(r"\d\.\d{3}", t), (r, t)
    dec = wbf["Decisions"]
    row = next(r for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value == "SL44-6")
    assert "錨點：2025 0.564" in str(dec.cell(row, 4).value)      # 舊文字保留在 Decisions

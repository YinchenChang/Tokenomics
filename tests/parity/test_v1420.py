"""v14.2 修補（工作單 docs/workorders/20261017_v14.2修補.md r0）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

S1  L1_MFleet_P25Lo／L1_MFleet_P25Hi（Cap_In 第 285、286 列）各欄＝MAX(該欄點估計, 該欄『同單價』下限)，機制在 Excel 公式。
    專屬測試：(a) 低端欄（token 取高）點估計低於同欄下限時，兩個名稱都等於同欄下限；(b) 點估計高於下限時不亂截斷；(c) 基準欄同樣適用；
              (d) 依賴鏈以外的契約名稱（含 L1_MFleet 三端、IF_Alloc*、IF_TokGW_*、全部 RNG_* 端點）與 v14.1 逐格相同。
S2  Har_In 第 20、32 列 A、B 欄標籤清空，H、I 欄保留，原文記入 Decisions SL45-2。
"""
import sys
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V152_CHANGED = set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v152_changed_names.json", encoding="utf-8"))["names"])      # v15.2 預期變動名單（B2／B3；test_v1520 逐名稱釘住，不多不少）
sys.path.insert(0, str(REPO / "builder"))
V141_PREV = REPO / "model" / "archive" / "20261017_Tokenomics_v14.1.xlsx"      # v14.1（LibreOffice 重算存檔）
CONTRACT_PREFIX = ("IF_", "IFW_", "IFC_", "L1_", "CHK_", "CAP_", "RNG_", "GOV_")
V150_CHANGED = {"CHK_VerifyTotal", "CHK_VerifyPass", "GOV_Info", "GOV_Table"}      # v15.0 預期變動：O9（驗證計數 22／14 → 21／13）、O14（Info 184 → 182）
P25_CHANGED = {"L1_MFleet_P25Lo", "L1_MFleet_P25Hi"}      # v14.2 S1 預期變動（只有低端欄 D）
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
P25_LO_NEW = [0.613453002685703, 0.323692273630786, 1.77540516071392]      # v15.2（B2 單價改變後）；v14.2 值 [0.783006655732561, 0.41409276867464, 2.26611338012012]；      # 舊 [0.783006655732561, 0.353474950317881, 2.26611338012012]
P25_HI_NEW = [0.379778478578724, 0.200392464734859, 1.09912359682784]      # v15.2；v14.2 值 [0.236137899833928, 0.124881437488884, 0.683410863048779]；      # 舊 [0.236137899833928, 0.106600412398634, 0.683410863048779]
SC_HI = {"Alloc_In!E24": 1.0}      # 低端欄（token 取高）的實際利用率 0.65 → 1.0：點估計 token 再高 1.54 倍
SC_LO_OK = {"Alloc_In!E24": 0.3}      # 0.65 → 0.3：點估計 token 降到上限之下（點估計 m 高於下限）
SC_BASE = {"Alloc_In!C24": 1.5}      # 基準欄的實際利用率 0.41 → 1.5：基準欄點估計 token 超過基準欄上限
PREWARM = {
    "test_v1420_s1_floor_binds_low_end_column": [SC_HI],
    "test_v1420_s1_floor_does_not_cut_when_point_above_floor": [SC_LO_OK],
    "test_v1420_s1_floor_applies_to_base_column": [SC_BASE],
}
ROW_PX = {285: "AL_PriceFleet25_Lo", 286: "AL_PriceFleet25_Hi"}


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


def _raw(v, row, col):
    """該欄的『點估計』（不含下限截斷）：營收 ÷（機隊付費 token（第 116 列）× 該列單價），全部取 LibreOffice 重算值。"""
    return v.get_name("SRC_DEM_007") * 1e9 / (v.get("Cap_In", f"{col}116") * v.get_name(ROW_PX[row]))


def _floor(v, row, col):
    """該欄『同單價』下限：營收 ÷（該欄機隊付費 token 上限（第 118 列）× 該列單價）。"""
    return v.get_name("SRC_DEM_007") * 1e9 / (v.get("Cap_In", f"{col}118") * v.get_name(ROW_PX[row]))


# ── S1 ──
def test_v1420_s1_mechanism_is_an_excel_formula(wbf):
    """六格（第 285、286 列的 C／D／E）都是 Excel 公式 MAX(點估計, 同欄下限)，只讀自己那一欄的第 116、118 列與該列單價名稱；名稱範圍不變。"""
    ci = wbf["Cap_In"]
    for r, px in ROW_PX.items():
        for c in "CDE":
            f = ci[f"{c}{r}"].value
            assert isinstance(f, str) and f.startswith("=") and "MAX(" in f and f"{c}116" in f and f"{c}118" in f and px in f, (r, c, f)
            assert f.count(px) == 2, (r, c, f)      # 點估計與下限同單價
            assert all(f"{x}116" not in f and f"{x}118" not in f for x in "CDE" if x != c), (r, c, f)      # 只讀同欄
        assert "v14.2 起比照 v14.1 R1" in ci[f"G{r}"].value
    assert wbf.defined_names["L1_MFleet_P25Lo"].attr_text == "Cap_In!$C$285:$E$285"
    assert wbf.defined_names["L1_MFleet_P25Hi"].attr_text == "Cap_In!$C$286:$E$286"
    assert "L1_MFleetFloor" not in wbf.defined_names


def test_v1420_s1_base_values(lo):
    """基準：P25Lo 低端欄 0.3535 → 0.4141、P25Hi 低端欄 0.1066 → 0.1249，等於各自『同單價』下限；基準欄與高端欄不變；L1_MFleet 三端不變。"""
    v = lo.view({})
    lo_, hi_ = v.get_name("L1_MFleet_P25Lo"), v.get_name("L1_MFleet_P25Hi")
    for got, want in ((lo_, P25_LO_NEW), (hi_, P25_HI_NEW)):
        assert all(abs(a - b) <= 1e-12 * max(1, abs(b)) for a, b in zip(got, want)), (got, want)
    assert abs(lo_[1] - _floor(v, 285, "D")) <= 1e-12 and abs(hi_[1] - _floor(v, 286, "D")) <= 1e-12
    # v14.1 的點估計（未截斷）確實低於下限：截斷有作用
    assert abs(_raw(v, 285, "D") - 0.27693285626520464) < 1e-12 and abs(_raw(v, 286, "D") - 0.1714444926675899) < 1e-12      # v15.2：舊 0.3535／0.1066（v14.2）
    assert _raw(v, 285, "D") < _floor(v, 285, "D") and _raw(v, 286, "D") < _floor(v, 286, "D")
    # 其他欄的點估計高於下限，不被截斷
    for r, row in ((285, lo_), (286, hi_)):
        for i, c in ((0, "C"), (2, "E")):
            assert row[i] > _floor(v, r, c) and abs(row[i] - _raw(v, r, c)) <= 1e-12 * row[i], (r, c)
    # 單價低端使 m 較高：同欄 P25Hi ≤ L1_MFleet 端 ≤ P25Lo 的順序（顯示用區間，不乘入 L1_MFleet）
    assert hi_[0] < v.get_name("L1_MFleet") < lo_[0]
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-12 and abs(v.get_name("L1_MFleet_Lo") - 0.242723485975401) < 1e-12 and abs(v.get_name("L1_MFleet_Hi") - 1.33130310709466) < 1e-12


def test_v1420_s1_floor_binds_low_end_column(lo):
    """必須能截斷：低端欄 token 被推到遠高於同欄上限，點估計遠低於下限；兩個名稱的低端欄必須等於同欄下限（不是點估計）。"""
    v = lo.view(SC_HI)
    for r, nm in ((285, "L1_MFleet_P25Lo"), (286, "L1_MFleet_P25Hi")):
        raw, floor = _raw(v, r, "D"), _floor(v, r, "D")
        assert v.get("Cap_In", "D116") > v.get("Cap_In", "D118")
        assert raw < floor * 0.7, (r, raw, floor)
        assert abs(v.get_name(nm)[1] - floor) <= 1e-12 * floor
    assert abs(v.get_name("L1_MFleet_P25Lo")[1] - P25_LO_NEW[1]) < 1e-12 and abs(v.get_name("L1_MFleet_P25Hi")[1] - P25_HI_NEW[1]) < 1e-12      # 同欄下限不受該利用率影響
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-12


def test_v1420_s1_floor_does_not_cut_when_point_above_floor(lo):
    """下限不亂截斷：低端欄 token 降到同欄上限之下，點估計高於下限，兩個名稱的低端欄＝點估計。"""
    v = lo.view(SC_LO_OK)
    assert v.get("Cap_In", "D116") < v.get("Cap_In", "D118")
    for r, nm in ((285, "L1_MFleet_P25Lo"), (286, "L1_MFleet_P25Hi")):
        raw, floor = _raw(v, r, "D"), _floor(v, r, "D")
        assert raw > floor and abs(v.get_name(nm)[1] - raw) <= 1e-9 * raw, (r, raw, floor)


def test_v1420_s1_floor_applies_to_base_column(lo):
    """『各欄』都適用：基準欄的點估計低於基準欄下限時，兩個名稱的基準欄＝基準欄同單價下限。"""
    v = lo.view(SC_BASE)
    for r, nm in ((285, "L1_MFleet_P25Lo"), (286, "L1_MFleet_P25Hi")):
        raw, floor = _raw(v, r, "C"), _floor(v, r, "C")
        assert raw < floor and abs(v.get_name(nm)[0] - floor) <= 1e-12 * floor, (r, raw, floor)


def test_v1420_s1_p25_cells_have_no_readers(wbf):
    """受影響名稱只有 L1_MFleet_P25Lo／_Hi 自己：第 285、286 列的 C:E 沒有任何公式讀取（依賴圖），所以沒有下游名稱受影響。"""
    from deps import Deps
    D = Deps(wbf)
    cells = {("Cap_In", f"{c}{r}") for r in (285, 286) for c in "CDE"}
    for k in D.formulas:
        assert not (D.direct(k) & cells), (k, sorted(D.direct(k) & cells))
    for n, d in wbf.defined_names.items():
        if n in P25_CHANGED:
            continue
        assert not any(x in cells for x in D._resolve("", d.attr_text)), n


def test_v1420_names_off_the_chain_unchanged(lo):
    """依賴鏈以外的契約名稱（IF_／IFW_／IFC_／L1_／CHK_／CAP_／RNG_／GOV_）與 v14.1 逐格值相同；
    例外只有：L1_MFleet_P25Lo／P25Hi（S1，上方斷言新值）與版本字串。含 L1_MFleet 三端、IF_Alloc*、IF_TokGW_*、全部 RNG_* 端點。"""
    prev = openpyxl.load_workbook(V141_PREV, data_only=True)
    v = lo.view({})
    names = [n for n in prev.defined_names if n.startswith(CONTRACT_PREFIX)]
    keep = [n for n in names if n not in P25_CHANGED and n not in VERSION_NAMES and n not in V150_CHANGED and n not in V152_CHANGED]
    assert len(keep) >= 340, len(keep)      # v15.2：同上；原 ≥ 740
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
    allnames = set(keep) | V152_CHANGED      # v15.2：RNG_*、IF_Alloc*、IF_TokGW_* 都在 B2／B3 預期變動名單內（test_v1520 逐名稱釘住），不再屬『不變』比較集
    assert any(n.startswith("RNG_") for n in allnames) and any(n.startswith("IF_AllocQ1") for n in allnames) and any(n.startswith("IF_TokGW_") for n in allnames)
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 280, 182)      # v15.0：Info 184 → 182（O14）
    assert (v.get_name("CHK_VerifyTotal"), v.get_name("CHK_VerifyPass"), v.get_name("CHK_VerifyFail"), v.get_name("CHK_VerifyWarn")) == (21, 13, 7, 1)      # v15.0 O9：V16 移出計數
    assert v.get_name("RNG_StaleFlag") == "一致"      # 區間檔與指紋檔的版本字串已隨 v14.2 更新，端點與指紋格逐值不變


# ── S2 ──
def test_v1420_s2_har_in_labels_cleared(wbf):
    ws, dec = wbf["Har_In"], wbf["Decisions"]
    for r in (20, 32):
        assert ws.cell(r, 1).value is None and ws.cell(r, 2).value is None, r
        assert all(ws.cell(r, c).value is None for c in range(3, 8)), r      # v14.1 R3 已清空
    assert ws["H20"].value == "Verified" and ws["H32"].value == "Assumed"      # 來源與標記欄原文保留（CLAUDE.md 第 6 節）
    assert ws["I20"].value == "不透明推理狀態只能在原廠 API 使用（轉換成本，[I]）" and ws["I32"].value == "編排框架多為開源或開發者自建"
    row = next(r for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value == "SL45-2")
    txt = str(dec.cell(row, 4).value)
    assert "Har_In!20：供應商專屬（1＝是）｜旗標" in txt and "Har_In!32：供應商專屬（1＝是）｜旗標" in txt


def test_v1420_decisions_recorded(wbf):
    dec = wbf["Decisions"]
    ids = {dec.cell(r, 1).value: str(dec.cell(r, 4).value) for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value}
    assert {"SL45-1", "SL45-2", "SL45-3"} <= set(ids)
    assert "v14.1 R1" in ids["SL45-1"]
    assert "0.3535 對 0.4141" in ids["SL45-1"] and "0.1066 對 0.1249" in ids["SL45-1"]
    assert "test_v1400_q3_floor_row121_unchanged_and_mfleet_lo_is_v141_floor" in ids["SL45-3"]

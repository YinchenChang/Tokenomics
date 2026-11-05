"""v21.8 專屬測試（工作單 docs/workorders/20261102_v21.8_財報季與月度證據.md r0）。讀 LibreOffice 重算後的值。

  1. 具名範圍：值改變的契約名稱，其儲存格全部列在預期變動 CSV（chat 端預檢）；例外只有治理計數與鏡像（GOV_Info／GOV_Table、IFC_Conf／IFC_Updated／IFC_Use、LB_Days）、
     區間端點 RNG_*（重產）、IDX_Src*（SRC_Index 延長）；新增名稱只有本版新增的 SRC 紀錄；沒有名稱被刪除；基準與低成本欄不變。
  2. W1：SRC_DC_008 4 → 5（Inputs!F23）、Cap_In!F58＝SRC_PRC_051（0.06）、Inputs!H23／Cap_In!M58／Sensitivity 文字。
  3. W2：SRC 等級與出處升級（值不變、原文保留）、第二來源、備註、SRC_DC_004 指標更正、新紀錄。
  4. W3：DB_Evidence 115 列、E014 結案、Decisions SL65-01、README B5。
  5. GOV 三項計數 0／129／183；RNG_StaleFlag 一致；全部公式格無錯誤值。
  6. 逐格比較 v21.7 → v21.8：數值差異只落在預期變動 CSV 與第 3 節的治理連帶格（規則見 GOV_RULES）。
"""
import csv
import json
import re
import sys
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path
import v21110_allow      # v21.11（v22.0 B1）：DRV_／TRN_ 與 RNG_Dem004_* 的參照位址改變、值不變（test_v21110 看守；R10）

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
import v2180  # noqa: E402
import v2190  # noqa: E402      # v21.9
from v2110_allow import v2110_revert_text      # v21.10
from v2110_allow import v219_cells, v219_names      # v21.9：v21.8 → v21.9 的差異格與名稱兩邊都扣掉（test_v2190 看守）

V217 = REPO / "model" / "archive" / "20261025_Tokenomics_v21.7.xlsx"
CSV = REPO / "docs" / "workorders" / "20261102_v21.8_預期變動.csv"
GOV_NAMES = {"GOV_Info", "GOV_Table", "GOV_Warnings", "IFC_Conf", "IFC_Updated", "IFC_Use", "LB_Days"}
NEW_IDS = ([f"SRC_PRC_{i:03d}" for i in range(51, 78)] + ["SRC_HW_100", "SRC_HW_101", "SRC_HW_102"] + [f"SRC_DC_{i:03d}" for i in range(23, 28)]
           + ["SRC_DEM_091", "SRC_DEM_092", "SRC_MOD_107", "SRC_PERF_086", "SRC_PERF_087"])
_num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
_rown = lambda coord: int(re.sub(r"[A-Z]+", "", coord))
_col = lambda coord: re.sub(r"\d+", "", coord)


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if _num(a) and _num(b):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


def _cells(attr):
    sh, rg = attr.rsplit("!", 1)
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    return sh.strip("'"), [(r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def _csv():
    rows = list(csv.reader(open(CSV, encoding="utf-8-sig")))[1:]
    return {(r[0], r[1]): r for r in rows}


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


@pytest.fixture(scope="module")
def wbv():
    return openpyxl.load_workbook(model_path(), data_only=True)


@pytest.fixture(scope="module")
def pf():
    return openpyxl.load_workbook(V217)


@pytest.fixture(scope="module")
def pw():
    return openpyxl.load_workbook(V217, data_only=True)


def _row(ws, sid):
    rr = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid]
    assert len(rr) == 1, (sid, rr)
    return rr[0]


def _src(wb, sid):
    for sh in ("SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Cap", "SRC_Harness", "SRC_Demand"):
        ws = wb[sh]
        for r in range(5, ws.max_row + 1):
            if ws.cell(r, 1).value == sid:
                return ws, r
    raise KeyError(sid)


# ---------------------------------------------------------------- 1. 具名範圍
def test_v2180_names(wbf, wbv, pw):
    exp = _csv()
    added = set(wbf.defined_names) - set(pw.defined_names)
    assert set(pw.defined_names) <= set(wbf.defined_names)      # 沒有名稱被刪除
    want_added = set(NEW_IDS) | {"SRC_PRC_074_Lo", "SRC_PRC_074_Hi", "SRC_HW_101_Lo", "SRC_HW_101_Hi"}
    assert added == want_added, sorted(added ^ want_added)
    bad, changed = [], set()
    for name, d in pw.defined_names.items():
        t = d.attr_text
        if "!" not in t or "," in t:
            continue
        sh, cells = _cells(t)
        if wbf.defined_names[name].attr_text != t:
            assert name.startswith("IDX_Src") or v21110_allow.ref_moved(name), name      # SRC_Index 延長；v21.11：DRV_／TRN_ 1×15 → 1×20、RNG_Dem004_* 下移（值不變，test_v21110 看守）
            continue
        diff = [(r, c) for r, c in cells if not _eq(pw[sh].cell(r, c).value, wbv[sh].cell(r, c).value)]
        if not diff:
            continue
        changed.add(name)
        if name in v219_names() - {"IDX_SrcGrade", "IDX_SrcStat", "LB_Days", "RNG_Version", "RNG_Current"}:
            continue      # v21.9：IF_NonNV_Out_TPU／Trn（test_v2190 看守）
        if name.startswith("RNG_") or name in GOV_NAMES or name == "SRC_DC_008":
            continue
        miss = [pw[sh].cell(r, c).coordinate for r, c in diff if (sh, pw[sh].cell(r, c).coordinate) not in exp]
        if miss:
            bad.append((name, miss[:5]))
    assert bad == [], bad
    assert {"IF_HoldEcon", "IF_DeprLifeIT", "L1_Ans5_GM_Lo", "B4_MktCache"} <= changed
    # 基準與低成本欄不變：Interface C:Q 中只有高成本欄（E、H、K、N、Q）可變
    for name in changed:
        if not name.startswith("IF_") or name in v219_names():      # v21.9：IF_NonNV_Out_TPU／Trn（test_v2190 看守）
            continue
        sh, cells = _cells(wbf.defined_names[name].attr_text)
        if sh != "Interface":
            continue
        for r, c in cells:
            coord = pw[sh].cell(r, c).coordinate
            if not _eq(pw[sh].cell(r, c).value, wbv[sh].cell(r, c).value):
                assert _col(coord) in ("E", "H", "K", "N", "Q"), (name, coord)
    assert abs(wbv["L1"][wbf.defined_names["L1_Ans5_GM_Lo"].attr_text.rsplit("!", 1)[1].replace("$", "")].value - 0.9408) < 5e-5


# ---------------------------------------------------------------- 2. W1
def test_v2180_w1_inputs_and_text(wbf, wbv, pf):
    dc = wbf["SRC_DC"]
    assert dc["A12"].value == "SRC_DC_008" and dc["C12"].value == 5 and dc["K12"].value == 1 and dc["N12"].value == "一手" and dc["I12"].value == "2026-04"
    assert dc["J12"].value == "Nebius Group 20-F FY2025（2026-04-30）＋6-K Q2 2026" and dc["S12"].value == "2026-11-02" and dc["Q12"].value == "E120；E467"
    w = dc["W12"].value
    assert w.startswith("v21.8（E467，1-A）：2026-01-01 起 GPU 4 → 5 年（會計估計變更）；FY2025 仍 4 年") and "原值＝4" in w and "原等級＝2" in w
    assert "原出處＝『capefearadvisors.substack.com；CNBC 2025-11；SiliconANGLE』" in w
    assert wbf["Inputs"]["F23"].value == "=SRC_DC_008" and wbv["Inputs"]["F23"].value == 5 and wbv["Inputs"]["E23"].value == 6 and wbv["Inputs"]["D23"].value == 6
    h23 = v2110_revert_text("Inputs", "H23", wbf["Inputs"]["H23"].value)      # v21.10：句尾補 v21.8 原句（追加 13，test_v21100 看守）
    assert h23 == v2190.H23_NEW and h23.endswith("｜原：" + pf["Inputs"]["H23"].value)      # v21.9 W3 第 3 點改寫 v21.8 句（test_v2190 看守）
    ci = wbf["Cap_In"]
    assert ci["F58"].value == "=SRC_PRC_051" and wbv["Cap_In"]["F58"].value == 0.06 and pf["Cap_In"]["F58"].value is None
    assert ci["M58"].value == "S54（≤512K 輸入；快取 0.06（E428））；指數未取得"
    assert wbv["Price_Frontier"]["F18"].value == 0.06 and abs(wbv["Price_Frontier"]["H18"].value - 0.282666666666667) < 1e-12
    se = wbf["Sensitivity"]
    assert (se["N4"].value, se["O4"].value, se["A72"].value) == ("IT 折舊年限（7 年對 5 年）－低", "IT 折舊年限（7 年對 5 年）－高", "IT 折舊年限（7 年對 5 年）")
    assert wbv["Sensitivity"]["O37"].value == 5


# ---------------------------------------------------------------- 3. W2
def test_v2180_src_upgrades(wbf, pf, pw):
    for sid, val, lab, grade, src, hand, date, ev, extra in v2180.UPG:
        ws, r = _src(wbf, sid)
        ows, orr = _src(pf, sid)
        assert lab in ws[f"B{r}"].value and ws[f"B{r}"].value == ows[f"B{orr}"].value, sid
        for col in "CDE":      # 值不變
            assert ws[f"{col}{r}"].value == ows[f"{col}{orr}"].value, (sid, col)
        assert ws[f"J{r}"].value == src, sid
        if grade is not None:
            assert ws[f"K{r}"].value == grade, sid
        w = ws[f"W{r}"].value
        assert str(ows[f"W{orr}"].value) in w and f"｜v21.8 升級（{ev}；值不變；修訂九；Decisions SL65-01）" in w, sid
        assert f"原出處＝『{ows[f'J{orr}'].value}』" in w, sid
        if grade is not None and ows[f"K{orr}"].value != grade:
            assert f"等級 {ows[f'K{orr}'].value} → {grade}" in w, sid
        assert ws[f"Q{r}"].value == ows[f"Q{orr}"].value, sid      # Evidence ID 欄不動（記在 W 欄）
    for sid, sec in v2180.SECOND.items():
        ws, r = _src(wbf, sid)
        assert ws[f"R{r}"].value == sec, sid
        assert _src(wbf, sec)[0][f"O{_src(wbf, sec)[1]}"].value == "Alt"
    for sid, note in v2180.NOTES.items():
        ws, r = _src(wbf, sid)
        ows, orr = _src(pf, sid)
        assert ws[f"W{r}"].value.startswith(note + "｜" + str(ows[f"W{orr}"].value)), sid
    ws, r = _src(wbf, "SRC_DC_004")
    assert ws[f"B{r}"].value == "AI 資料中心對傳統建造溢價（Turner & Townsend）" and "原 B 欄（指標）＝『液冷溢價（Turner & Townsend）』" in ws[f"W{r}"].value
    assert (ws[f"D{r}"].value, ws[f"E{r}"].value) == (0.07, 0.1)


def test_v2180_new_records(wbf, wbv):
    for sid in NEW_IDS:
        ws, r = _src(wbf, sid)
        assert ws[f"U{r}"].value == "U-V2180", sid
        assert ws[f"O{r}"].value == ("Active" if sid == "SRC_PRC_051" else "Superseded" if sid == "SRC_HW_100" else "Alt"), sid      # v21.9：SRC_HW_100 撤銷（test_v2190 看守）
        assert str(ws[f"Q{r}"].value).startswith("E"), sid
    ws, r = _src(wbf, "SRC_PRC_051")
    assert ws[f"C{r}"].value == 0.06 and ws[f"Q{r}"].value == "E428" and ws[f"V{r}"].value == "Cap_In!F58｜直接" and ws[f"R{r}"].value.startswith("免（C1")
    ws, r = _src(wbf, "SRC_PRC_050")      # 既有紀錄（gpt-6.1-sol 長上下文快取）不動
    assert ws[f"B{r}"].value == "gpt-6.1-sol 快取輸入（長上下文）" and ws[f"C{r}"].value == 0.2 and ws[f"O{r}"].value == "Alt"
    ws, r = _src(wbf, "SRC_DC_023")
    assert ws[f"C{r}"].value == 6 and ws[f"H{r}"].value == "Alphabet" and ws[f"Q{r}"].value == "E476"
    ws, r = _src(wbf, "SRC_DEM_091")
    assert ws[f"C{r}"].value == 32 and ws[f"F{r}"].value == "B tok/min"
    ws, r = _src(wbf, "SRC_HW_101")
    assert (ws[f"D{r}"].value, ws[f"E{r}"].value) == (0.15, 0.17)


# ---------------------------------------------------------------- 4. W3
def test_v2180_evidence_decisions_readme(wbf):
    ev = wbf["DB_Evidence"]
    data = json.loads((REPO / "builder" / "v2180_evidence.json").read_text(encoding="utf-8"))
    r0 = _row(ev, "E412")
    assert ev.cell(r0 - 1, 1).value == "E411"
    ids = [ev.cell(r0 + i, 1).value for i in range(115)]
    assert ids == [d[0] for d in data] and ev.cell(r0 + 115, 1).value == "E559"      # v21.9：E559 接在 E558 後（test_v2190 看守）
    assert ids[:64] == [f"E{i}" for i in range(412, 476)] and ids[64:96] == [f"E{i}" for i in range(476, 508)] and ids[96:] == [f"E{i}" for i in range(540, 559)]
    st = {ev.cell(r0 + i, 1).value: ev.cell(r0 + i, 12).value for i in range(115)}
    assert st["E467"] == st["E428"] == st["E476"] == st["E488"] == "已處理（v21.8）"
    assert all(st[e] == "待判定（12-01 月度）" for e in ("E438", "E462", "E507", "E415", "E421", "E455", "E464"))
    assert st["E550"] == "已處理（高端 5.0 已涵蓋，1-D）" and st["E430"] == "已處理" and st["E412"] == "已處理"
    assert all(ev.cell(r0 + i, 10).value == "v21.8" for i in range(115))
    r14 = _row(ev, "E014")
    assert ev.cell(r14, 12).value == "已處理" and "E419" in ev.cell(r14, 11).value and "原狀態：待判定" in ev.cell(r14, 11).value
    d = wbf["Decisions"]
    r = _row(d, "SL65-01")
    assert d.cell(r - 1, 1).value == "SL64-01" and d.cell(r, 2).value == "v21.8" and d.cell(r, 7).value == "v21.8 已建"
    txt = d.cell(r, 4).value
    for key in ("1-A 採用 E467：SRC_DC_008 4 → 5", "方向計數：縮窄 1、放寬 0、改基準 0、不變其餘", "SRC_PRC_051", "修訂九"):
        assert key in txt, key
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert "以下為 v21.8（次版，底版 v21.7：" in b5 and "以下為 v21.7（次版，底版 v21.6：" in b5      # v21.9：B5 開頭為 v21.9 段（test_v2190 看守）
    assert "基準與低成本欄不變" in b5 and str(rm["A1"].value).startswith("Tokenomics v21.11")


# ---------------------------------------------------------------- 5. GOV
def test_v2180_gov_counts(lo):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 129, 183)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.11") and str(v.get_name("RNG_Current")).endswith("v21.11")      # v21.9：版本字串（test_v2190 看守）
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 6. 逐格比較 v21.7 → v21.8
SRC_SHEETS = {"SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Demand"}


def gov_rule(sh, coord, old_n, new_n):
    """第 3 節（SRC 等級、第二來源、審查日、新紀錄）與區間重產的治理連帶格；工作單第 0 節與第 4 節第 2 點。"""
    c, r = _col(coord), _rown(coord)
    if sh == "Alloc":      # 區間端點常數（重產）與指紋記錄值
        return (180 < r <= 406) or (413 <= r <= 1245 and c == "D")
    if sh in SRC_SHEETS:      # 等級（K）、缺第二來源旗標（Z／AE）
        return c in ("K", "Z", "AE")
    if sh == "SRC_Index":      # SRC 頁新增紀錄使堆疊重排
        return c in "ABCDEF"
    if sh == "Gov_Map":      # SRC_Index 列（AF）、SRC 等級（T）、IFC B 級旗標（AH）、審查日數值（AJ）
        return c in ("AF", "T", "AH", "AJ")
    if sh == "Interface":      # IFC 審查日數值（V）
        return c == "V"
    if sh == "Load_Bearing":      # 審查日距建置日（N）
        return c == "N"
    if sh == "Checks":      # W1 缺第二來源、I1 待判定、GOV_Info
        return coord in ("D87", "D89", "D99")
    return False


def test_v2180_cell_diffs_only_expected(pf, pw, wbf, wbv):
    exp = _csv()
    assert pf.sheetnames == wbf.sheetnames
    num_out, text_out = [], []
    v219 = v219_cells()      # v21.9：v21.8 → v21.9 的差異格兩邊都扣掉（test_v2190 看守）
    for ws in pf:
        wn, va, vb = wbf[ws.title], pw[ws.title], wbv[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                p, q = va.cell(r, c).value, vb.cell(r, c).value
                coord = ws.cell(r, c).coordinate
                if coord in v219.get(ws.title, set()):
                    continue
                key = (ws.title, coord)
                if _eq(p, q):
                    continue
                if key in exp:
                    e = exp[key][3]
                    if key == ("Checks", "D98"):
                        assert q == 129, q
                    elif _num(q):
                        assert abs(float(e) - q) <= 1e-9 * max(1, abs(q)), (key, e, q)
                    continue
                if (_num(p) or p in (None, "")) and (_num(q) or q in (None, "")) and (p is not None and q is not None):
                    if not gov_rule(ws.title, coord, p, q):
                        num_out.append(key)
                    continue
                text_out.append(key)
    assert num_out == [], num_out[:40]
    allowed_text = {("Inputs", "H23"), ("Cap_In", "M58"), ("README", "A1"), ("README", "B5"), ("Alloc", "C177"), ("Alloc", "C178"),
                    ("Sensitivity", "N4"), ("Sensitivity", "O4"), ("Sensitivity", "A72"), ("Interface", "R219"), ("Interface", "S219")}
    for sh, coord in text_out:
        if (sh, coord) in allowed_text:
            continue
        if sh in SRC_SHEETS | {"SRC_Index", "DB_Evidence", "Decisions"}:
            continue      # 第 3 節：SRC 文字欄、新紀錄、SRC_Index 重排、DB_Evidence／Decisions 新列（逐欄內容由上面各測試看守）
        if sh == "Gov_Map" and _col(coord) == "AI":
            continue      # IFC 審查日文字
        if sh == "Interface" and _col(coord) == "U":
            continue      # IFC_Updated（審查日文字）
        if sh == "Load_Bearing" and _col(coord) == "L":
            continue      # 審查日（SRC）
        if sh == "Cap_In" and coord == "F58":
            continue
        if gov_rule(sh, coord, None, None):
            continue      # 治理連帶格由「—」變數字（例：Load_Bearing N52 新出現審查日）
        raise AssertionError((sh, coord))
    # 公式文字：只有 Cap_In F58（新連結）、Checks D86（SRC 範圍）、SRC_* 檢查欄、SRC_Index 改變
    for ws in pf:
        if ws.title in SRC_SHEETS | {"SRC_Index", "DB_Evidence", "Decisions"}:
            continue
        wn = wbf[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if ws.cell(r, c).coordinate in v219.get(ws.title, set()):
                    continue
                if x != y and ((isinstance(x, str) and x.startswith("=")) or (isinstance(y, str) and y.startswith("="))):
                    assert (ws.title, ws.cell(r, c).coordinate) in {("Cap_In", "F58"), ("Checks", "D86"), ("Alloc", "C177")}, (ws.title, ws.cell(r, c).coordinate)

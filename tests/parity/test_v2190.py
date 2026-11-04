"""v21.9 專屬測試（工作單 docs/workorders/20261103_v21.9_Q1原生精度與文字治理修正.md r0）。讀 LibreOffice 重算後的值。

  1. 具名範圍：沒有新增或刪除；值改變的契約名稱只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（儲存格全部在預期變動 CSV），
     另有版本字串 RNG_Version／RNG_Current 與治理鏡像 IDX_SrcGrade／IDX_SrcStat（SRC_Index）、LB_Days（Load_Bearing 建置日）。
  2. W1：NonNV B6:D7 新值；每 token 成本比 H6／H7。
  3. W2：NonNV L6／L7／L8／L9／A2、Interface A368 說明，被改寫的原文逐字保留於「｜原（v21.9 前）：」之後。
  4. W3：SRC_HW_100 Superseded、SRC_HW_010 Evidence、SRC_DC_004、SRC_PRC_074、SRC_DEM_091、Inputs!H23、Decisions SL65-01、README B5 v21.8 段、Load_Bearing!C3。
  5. W4：DB_Evidence E559、Decisions SL66-01、README B5 開頭。
  6. GOV 三項計數 0／129／183；RNG_StaleFlag 一致；全部公式格無錯誤值。
  7. 逐格比較 v21.8 → v21.9：數值差異只落在預期變動 CSV 與 W3 的治理連帶格（規則見 gov_rule）；文字差異只在 W2–W4 所列格與其鏡像。
v21.10 起現行版為 v21.10：NonNV B6:D7 以 V2110_OLD 讀回 v21.9 值、說明格以 v2110_revert_text 讀回 v21.9 文字；逐格比較兩邊扣掉 v2110_cells（v21.9 → v21.10，test_v21100 看守），
預期變動 CSV 的格若也在 v21.10 改變，改與封存的 v21.9 檔比值。
"""
import csv
import re
import sys
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
import v2180  # noqa: E402
import v2190  # noqa: E402
from v2110_allow import V2110_OLD, V219, v2110_cells, v2110_old_sheet, v2110_revert_text      # v21.10（test_v21100 看守 v21.10 的改變）

V218 = REPO / "model" / "archive" / "20261102_Tokenomics_v21.8.xlsx"
CSV = REPO / "docs" / "workorders" / "20261103_v21.9_預期變動.csv"
CHANGED = {"IF_NonNV_Out_TPU", "IF_NonNV_Out_Trn"}
OTHER = {"RNG_Version", "RNG_Current", "IDX_SrcGrade", "IDX_SrcStat", "LB_Days"}
_num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
_rown = lambda coord: int(re.sub(r"[A-Z]+", "", coord))
_col = lambda coord: re.sub(r"\d+", "", coord)
TAG = "｜原（v21.9 前）："


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
    return openpyxl.load_workbook(V218)


@pytest.fixture(scope="module")
def pw():
    return openpyxl.load_workbook(V218, data_only=True)


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
def test_v2190_names(wbf, wbv, pw):
    exp = _csv()
    assert set(wbf.defined_names) == set(pw.defined_names)      # 名稱不增不減（契約名稱與 SRC 名稱）
    changed, bad = set(), []
    for name, d in pw.defined_names.items():
        t = d.attr_text
        if "!" not in t or "," in t:
            continue
        assert wbf.defined_names[name].attr_text == t, name      # 參照位址不變
        sh, cells = _cells(t)
        diff = [(r, c) for r, c in cells if not _eq(pw[sh].cell(r, c).value, wbv[sh].cell(r, c).value)]
        if not diff:
            continue
        changed.add(name)
        if name in CHANGED:
            miss = [pw[sh].cell(r, c).coordinate for r, c in diff if (sh, pw[sh].cell(r, c).coordinate) not in exp]
            if miss:
                bad.append((name, miss))
    assert bad == [], bad
    assert changed == CHANGED | OTHER, sorted(changed ^ (CHANGED | OTHER))
    iv = openpyxl.load_workbook(V219, data_only=True)["Interface"]      # v21.10：Interface 第 370、371 列改 FP8 對齊（test_v21100 看守）；這裡核對封存的 v21.9
    assert [iv[f"{c}370"].value for c in "CDE"] == [0.25, 0.35, 0.4]
    assert [iv[f"{c}371"].value for c in "CDE"] == [0.06, 0.14, 0.25]


# ---------------------------------------------------------------- 2. W1
def test_v2190_w1_inputs(lo, wbf, pf):
    nn, po = v2110_old_sheet(wbf["NonNV"], "NonNV"), pf["NonNV"]      # v21.10：B6:D7 讀回 v21.9 值（FP8 對齊新值由 test_v21100 看守）
    v = lo.view(V2110_OLD)
    assert nn["A6"].value == "Google TPU v7 Ironwood" and nn["A7"].value == "AWS Trainium3"
    assert [nn[f"{c}6"].value for c in "BCD"] == [0.25, 0.35, 0.40] and [po[f"{c}6"].value for c in "BCD"] == [0.6, 0.8, 1.1]
    assert [nn[f"{c}7"].value for c in "BCD"] == [0.06, 0.14, 0.25] and [po[f"{c}7"].value for c in "BCD"] == [0.3, 0.5, 0.8]
    for r in (6, 7):      # 持有比與公式不變
        for c in "EFGHIJK":
            assert nn[f"{c}{r}"].value == po[f"{c}{r}"].value, (c, r)
    assert abs(v.get("NonNV", "H6") - 2.0) < 1e-12 and abs(v.get("NonNV", "H7") - 0.61 / 0.14) < 1e-12
    assert abs(v.get("NonNV", "I6") - 1.625) < 1e-12 and abs(v.get("NonNV", "J6") - 3.6) < 1e-12
    assert abs(v.get("NonNV", "I7") - 1.8) < 1e-12 and abs(v.get("NonNV", "J7") - 0.7 / 0.06) < 1e-12


# ---------------------------------------------------------------- 3. W2
def test_v2190_w2_text(wbf, pf):
    nn, po = v2110_old_sheet(wbf["NonNV"], "NonNV"), pf["NonNV"]      # v21.10：說明格讀回 v21.9 文字（test_v21100 看守）
    for r in (6, 7):
        t, o = nn[f"L{r}"].value, po[f"L{r}"].value
        assert v2190.Q1_OLD in o and v2190.Q1_NEW not in o
        assert t == o.replace(v2190.Q1_OLD, v2190.Q1_NEW) + TAG + v2190.Q1_OLD, r
        assert t.index(v2190.Q1_NEW) < t.index("｜原：") < t.index(TAG)
    assert "v21.7：持有比基準 0.55 → 0.61" in nn["L7"].value      # L7 既有 v21.7 段保留
    l8 = nn["L8"].value
    assert "｜v21.9：PR #176 查過——晶圓級系統無同口徑機架價" in l8 and l8.index("｜v21.9：") < l8.index("｜原：")
    assert l8.endswith(TAG + v2190.NO_DATA) and l8.count(v2190.NO_DATA) == 1
    l9 = nn["L9"].value
    assert l9.startswith("v21.9：Jalapeño 規格推導產出比 0.35／0.60／1.15（方法一，PR #176），基準與現值 0.6 相同；持有比界線 0.64／0.82／1.27")
    assert l9.endswith(TAG + v2190.L9_OPEN_OLD + "；" + v2190.NO_DATA) and l9.count(v2190.NO_DATA) == 1
    for r in (8, 9):      # 原「｜原：」段逐字保留
        o = po[f"L{r}"].value
        assert o[o.index("｜原："):] in nn[f"L{r}"].value, r
    a2 = nn["A2"].value
    assert a2 == po["A2"].value.replace(v2190.A2_ANCHOR + "｜原：", v2190.A2_ANCHOR + v2190.A2_ADD + "｜原：")
    a368, o368 = v2110_old_sheet(wbf["Interface"], "Interface")["A368"].value, pf["Interface"]["A368"].value
    assert a368 == o368.replace(v2190.A368_OLD, v2190.A368_NEW) + TAG + v2190.A368_OLD
    for r in (8, 9):      # Cerebras、OpenAI 客製數值不改
        for c in "BCDEFG":
            assert nn[f"{c}{r}"].value == po[f"{c}{r}"].value, (c, r)


# ---------------------------------------------------------------- 4. W3
def test_v2190_w3_governance(wbf, wbv, pf):
    ws, r = _src(wbf, "SRC_HW_100")
    ows, orr = _src(pf, "SRC_HW_100")
    assert ws[f"O{r}"].value == "Superseded" and ws[f"P{r}"].value == "SRC_HW_010"
    w = ws[f"W{r}"].value
    assert w.startswith("重複：與 SRC_HW_010 同一原文（Data Gravity／wing.vc，5.0 $M）｜v21.9 更正（修訂九；Decisions SL66-01")
    assert "原狀態＝Alt" in w and w.endswith("｜" + ows[f"W{orr}"].value)
    for c in "BCDEFGHIJKLMNQ":      # 其他欄不動
        assert ws[f"{c}{r}"].value == ows[f"{c}{orr}"].value, c
    ws, r = _src(wbf, "SRC_HW_010")
    assert ws[f"Q{r}"].value == "E106；E200；E263；E450" and ws[f"O{r}"].value == "Active" and ws[f"C{r}"].value == 5
    ws, r = _src(wbf, "SRC_HW_101")
    assert ws[f"Q{r}"].value == "E550"      # E550 即 HW_101 紀錄（只核對）
    ws, r = _src(wbf, "SRC_DC_004")
    assert ws[f"J{r}"].value == v2190.DC004_J and ws[f"H{r}"].value == "AI 資料中心"
    assert "原出處＝『archdesk.com、gigacapacity.com 轉述 JLL』；原適用對象＝『液冷設施』" in ws[f"W{r}"].value
    assert (ws[f"D{r}"].value, ws[f"E{r}"].value, ws[f"K{r}"].value) == (0.07, 0.1, 1)      # v21.10 追加 15：等級 3 → 1（test_v21100 看守）
    ws, r = _src(wbf, "SRC_PRC_074")
    assert ws[f"K{r}"].value == 2 and ws[f"L{r}"].value == "Derived" and "原等級＝1" in ws[f"W{r}"].value
    ws, r = _src(wbf, "SRC_DEM_091")
    assert ws[f"G{r}"].value == v2190.DEM091_G_NEW and "近（nearly）" in ws[f"G{r}"].value and ws[f"C{r}"].value == 32
    assert v2190.DEM091_G_OLD in ws[f"W{r}"].value
    h23 = v2110_revert_text("Inputs", "H23", wbf["Inputs"]["H23"].value)      # v21.10 追加 13：句尾補 v21.8 原句（test_v21100 看守）
    assert h23 == v2190.H23_NEW and "Amazon、Meta、Microsoft、SpaceX 10-Q 皆無 4 年，Alphabet 6 年見其法說（10-Q 未讀）" in h23
    assert "四家 hyperscaler" not in h23 and pf["Inputs"]["H23"].value == v2180.H23_NEW
    d = wbf["Decisions"]
    t = d.cell(_row(d, "SL65-01"), 4).value
    assert v2190.HIGH_ANCHOR + v2190.HIGH_ADD in t and t.count("B4_MktCache") == 1
    lb = wbf["Load_Bearing"]
    assert openpyxl.load_workbook(V219)["Load_Bearing"]["C3"].value == "2026-11-03" and pf["Load_Bearing"]["C3"].value == "2026-10-08"      # v21.10：現行版 C3 改由版本檔名日期帶出（test_v21100 看守）
    assert openpyxl.load_workbook(V219, data_only=True)["Load_Bearing"]["N43"].value == 2      # 審查日 2026-11-01 距建置日 2 天（v21.8 為 −24）


# ---------------------------------------------------------------- 5. W4
def test_v2190_evidence_decisions_readme(wbf):
    ev = wbf["DB_Evidence"]
    r = _row(ev, "E559")
    assert ev.cell(r - 1, 1).value == "E558" and ev.cell(r + 1, 1).value == "E560"      # v21.10：E560 接在 E559 後（test_v21100 看守）
    assert [ev.cell(r, c).value for c in range(1, 19)] == v2190.E559
    assert ev.cell(r, 12).value == "已處理" and ev.cell(r, 10).value == "v21.9" and "Andy 2026-11-03" in ev.cell(r, 11).value
    d = wbf["Decisions"]
    r = _row(d, "SL66-01")
    assert d.cell(r - 1, 1).value == "SL65-01" and d.cell(r, 2).value == "v21.9" and d.cell(r, 7).value == "v21.9 已建"
    txt = d.cell(r, 4).value
    for key in ("W1 下修（不利方向）、改基準 2 列", "SRC_HW_100 改 Superseded", "修訂九", "IF_NonNV_Out_TPU、IF_NonNV_Out_Trn"):
        assert key in txt, key
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert "以下為 v21.9（次版，底版 v21.8：" in b5 and "以下為 v21.8（次版，底版 v21.7：" in b5      # v21.10：B5 開頭為 v21.10 段（test_v21100 看守）
    assert "契約名稱值改變者只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串" in b5
    assert v2190.HIGH_ANCHOR + v2190.HIGH_ADD + "；基準與低成本欄不變" in b5      # W3 第 2 點：v21.8 段補連帶
    assert str(rm["A1"].value).startswith("Tokenomics v21.10")


# ---------------------------------------------------------------- 6. GOV
def test_v2190_gov_counts(lo):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 129, 183)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.10") and str(v.get_name("RNG_Current")).endswith("v21.10")
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 7. 逐格比較 v21.8 → v21.9
SRC_SHEETS = {"SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Demand"}
NUM_GOV = {("SRC_Price", "K78"), ("SRC_Index", "E600"), ("Alloc", "C177"), ("Alloc", "C178")}      # SRC_PRC_074 等級、SRC_Index 等級鏡像、版本字串
TEXT_OK = ({("NonNV", c) for c in ("L6", "L7", "L8", "L9", "A2")} | {("Interface", "A368"), ("Inputs", "H23"), ("README", "A1"), ("README", "B5"),
           ("Load_Bearing", "C3"), ("Alloc", "C177"), ("Alloc", "C178"),
           ("SRC_HW", "O104"), ("SRC_HW", "P104"), ("SRC_HW", "W104"), ("SRC_HW", "Q14"), ("SRC_DC", "H8"), ("SRC_DC", "J8"), ("SRC_DC", "W8"), ("SRC_DC", "AH8"),
           ("SRC_Price", "W78"), ("SRC_Demand", "G95"), ("SRC_Demand", "W95"), ("SRC_Index", "D104")}
           | {("Gov_Map", f"N{r}") for r in range(395, 419)})      # Gov_Map N 欄＝NonNV L6／L7／L8／L9 說明的鏡像（=NonNV!$L$6 等）


def gov_rule(sh, coord):
    """W3 第 4 點：Load_Bearing!C3 改建置日 → 審查日距建置日（N 欄）全部重算。"""
    return sh == "Load_Bearing" and _col(coord) == "N"


def test_v2190_cell_diffs_only_expected(pf, pw, wbf, wbv):
    exp = _csv()
    assert pf.sheetnames == wbf.sheetnames
    hit, num_out, text_out = set(), [], []
    v2110 = v2110_cells()      # v21.10：v21.9 → v21.10 的差異格兩邊都扣掉（test_v21100 看守）
    w219 = openpyxl.load_workbook(V219, data_only=True)
    for ws in pf:
        wn, va, vb = wbf[ws.title], pw[ws.title], wbv[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                coord = ws.cell(r, c).coordinate
                key = (ws.title, coord)
                p, q = va.cell(r, c).value, vb.cell(r, c).value
                if _eq(p, q) and ws.cell(r, c).value == wn.cell(r, c).value:
                    continue
                if key in exp:
                    hit.add(key)
                    if coord in v2110.get(ws.title, set()):
                        q = w219[ws.title][coord].value      # v21.10 也改了這格：與封存的 v21.9 檔比值
                    assert abs(float(exp[key][3]) - q) <= 1e-9 * max(1, abs(q)), (key, exp[key][3], q)
                    continue
                if coord in v2110.get(ws.title, set()):
                    continue
                if ws.title in ("DB_Evidence", "Decisions"):
                    continue      # W4 新列與 SL65-01 文字（下面逐列核對）
                if key in NUM_GOV or gov_rule(ws.title, coord):
                    continue
                if _num(p) and _num(q):
                    num_out.append(key)
                elif key not in TEXT_OK:
                    text_out.append(key)
    assert hit == set(exp), sorted(set(exp) - hit)      # 預期變動 CSV 28 格全部改變且值與預檢相同
    assert num_out == [], num_out
    assert text_out == [], text_out
    # DB_Evidence 只多 E559 一列；Decisions 只多 SL66-01 一列，另 SL65-01 的 D 欄
    r559 = _row(wbf["DB_Evidence"], "E559")
    rs = _row(wbf["Decisions"], "SL66-01")
    for sh, allowed in (("DB_Evidence", lambda co: _rown(co) == r559), ("Decisions", lambda co: _rown(co) == rs or co == f"D{_row(wbf['Decisions'], 'SL65-01')}")):
        a, b = pf[sh], wbf[sh]
        for r in range(1, max(a.max_row, b.max_row) + 1):
            for c in range(1, max(a.max_column, b.max_column) + 1):
                if a.cell(r, c).value != b.cell(r, c).value and a.cell(r, c).coordinate not in v2110.get(sh, set()):
                    assert allowed(a.cell(r, c).coordinate), (sh, a.cell(r, c).coordinate)
    # 公式文字：模型計算頁沒有任何公式改變
    for ws in pf:
        wn = wbf[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if ws.cell(r, c).coordinate in v2110.get(ws.title, set()):
                    continue
                if x != y and ((isinstance(x, str) and x.startswith("=")) or (isinstance(y, str) and y.startswith("="))):
                    raise AssertionError((ws.title, ws.cell(r, c).coordinate, x, y))

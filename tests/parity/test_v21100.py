"""v21.10 專屬測試（工作單 docs/workorders/20261104_v21.10_TPU產出比改FP8對齊與文字修正.md r0）。讀 LibreOffice 重算後的值。
（檔名 test_v21100＝v21.10；test_v2110 是 v21.1。）

  1. 具名範圍：沒有新增或刪除；值改變的契約名稱只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（儲存格全部在預期變動 CSV），
     另有版本字串 RNG_Version／RNG_Current 與治理名稱 IDX_SrcGrade（SRC_Index 等級鏡像）、LB_Days（Load_Bearing 建置日）。
  2. W1：NonNV B6:D7 新值（FP8 對齊作基準、原生精度為低端）；每 token 成本比 H:J。
  3. W2：NonNV L6／L7／A2／L8、Interface A368 說明，被改寫的 v21.9 原句逐字保留於「｜原（v21.10 前）：」之後；Inputs!H23 句尾補 v21.8 原句；NonNV L9 插入一句。
  4. W3：Load_Bearing!C3＝版本檔名日期（追加 14）；DB_Evidence E450 相關 SRC、SRC_DC_004 等級與一手（追加 15）；E560；Decisions SL67-01；README B5。
  5. GOV 三項計數 0／129／183；RNG_StaleFlag 一致；全部公式格無錯誤值。
  6. 逐格比較 v21.9 → v21.10：數值差異只落在預期變動 CSV 與治理連帶格；文字差異只在工作單所列格與其鏡像；公式文字 0 變動。
"""
import csv
import datetime as dt
import re
import sys
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
import v2190  # noqa: E402
import v21100  # noqa: E402

V219 = REPO / "model" / "archive" / "20261103_Tokenomics_v21.9.xlsx"
CSV = REPO / "docs" / "workorders" / "20261104_v21.10_預期變動.csv"
CHANGED = {"IF_NonNV_Out_TPU", "IF_NonNV_Out_Trn"}
OTHER = {"RNG_Version", "RNG_Current", "IDX_SrcGrade", "LB_Days"}
TAG = "｜原（v21.10 前）："
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


# v21.11（v22.0 B1，R10）：v21.10 已移到 archive；本檔改為看守封存的 v21.10 檔本身（v21.9 → v21.10 的改變）。
# 現行 v21.11 是結構版（Terra 第四層級的欄位重排），對 v21.10 的逐值相等由 test_v21110 以鍵對齊比較看守。
V2110 = REPO / "model" / "archive" / "20261104_Tokenomics_v21.10.xlsx"


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(V2110)


@pytest.fixture(scope="module")
def wbv():
    return openpyxl.load_workbook(V2110, data_only=True)


@pytest.fixture(scope="module")
def pf():
    return openpyxl.load_workbook(V219)


@pytest.fixture(scope="module")
def pw():
    return openpyxl.load_workbook(V219, data_only=True)


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
def test_v21100_names(wbf, wbv, pw):
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
    iv = wbv["Interface"]
    assert [iv[f"{c}370"].value for c in "CDE"] == [0.35, 0.66, 0.84]
    assert [iv[f"{c}371"].value for c in "CDE"] == [0.14, 0.28, 0.5]


# ---------------------------------------------------------------- 2. W1
def test_v21100_w1_inputs(wbf, wbv, pf):
    nn, nv, po = wbf["NonNV"], wbv["NonNV"], pf["NonNV"]
    assert nn["A6"].value == "Google TPU v7 Ironwood" and nn["A7"].value == "AWS Trainium3"
    assert [nn[f"{c}6"].value for c in "BCD"] == [0.35, 0.66, 0.84] and [po[f"{c}6"].value for c in "BCD"] == [0.25, 0.35, 0.40]
    assert [nn[f"{c}7"].value for c in "BCD"] == [0.14, 0.28, 0.50] and [po[f"{c}7"].value for c in "BCD"] == [0.06, 0.14, 0.25]
    assert nn["B6"].value == po["C6"].value and nn["B7"].value == po["C7"].value      # 低端＝原生精度的基準值（v21.9 基準）
    for r in (6, 7):      # 持有比、公式與標記不變
        for c in "EFGHIJK":
            assert nn[f"{c}{r}"].value == po[f"{c}{r}"].value, (c, r)
    for r in (5, 8, 9, 10, 11):      # 其他列不動
        for c in "BCDEFG":
            assert nn[f"{c}{r}"].value == po[f"{c}{r}"].value, (c, r)
    assert abs(nv["H6"].value - 0.70 / 0.66) < 1e-12 and abs(nv["H7"].value - 0.61 / 0.28) < 1e-12      # 基準：TPU 1.061、Trn3 2.179
    assert round(nv["H6"].value, 3) == 1.061 and round(nv["H7"].value, 3) == 2.179
    assert abs(nv["I6"].value - 0.65 / 0.84) < 1e-12 and abs(nv["J6"].value - 0.9 / 0.35) < 1e-12      # 最佳角落 0.774、最差角落 2.571
    assert abs(nv["I7"].value - 0.9) < 1e-12 and abs(nv["J7"].value - 5.0) < 1e-12


# ---------------------------------------------------------------- 3. W2
def test_v21100_w2_text(wbf, pf):
    nn, po = wbf["NonNV"], pf["NonNV"]
    for r in (6, 7):
        t, o = nn[f"L{r}"].value, po[f"L{r}"].value
        assert v2190.Q1_NEW in o and v21100.Q1_NEW not in o
        assert t == o.replace(v2190.Q1_NEW, v21100.Q1_NEW, 1) + TAG + v2190.Q1_NEW, r
        assert t.index(v21100.Q1_NEW) < t.index("｜原：") < t.index("｜原（v21.9 前）：") < t.index(TAG)
        assert "基準＝FP8 對齊（VR200 也以 FP8 比，PR #172 E 節方法一），低端＝各晶片最高原生精度基準值（v21.9 基準），高端＝FP8 對齊高端" in t
        assert "docs/evidence/20261104_TPU產出比查核/" in t and "Andy 2026-11-04 照建議" in t.split("｜原：")[0]
    a2, o2 = nn["A2"].value, po["A2"].value
    assert a2 == o2.replace(v2190.A2_ADD, v21100.A2_NEW, 1) + TAG + v2190.A2_ADD[1:]
    assert "（TPU、Trn3 為 v21.10 FP8 對齊口徑，原生精度為低端）" in a2 and "OpenAI 客製推導基準 0.60 與現值相同；Cerebras 無推導值、證據偏不利（#176 Q3 替代下修 0.05／0.15／0.45），維持慣例值" in a2
    l8, o8 = nn["L8"].value, po["L8"].value
    assert l8 == o8.replace(v2190.L8_ADD, v21100.L8_NEW, 1) + TAG + v2190.L8_ADD
    assert "無官方售價；每 kW 法（記者估價，持有比 2.5／3.1／3.9）與 OpenAI 合約法相差 3.7–7.7 倍、互相衝突；產出比只得界線" in l8.split("｜原：")[0]
    l9, o9 = nn["L9"].value, po["L9"].value
    assert l9 == v2190.L9_OPEN_NEW + "；Jalapeño 機架與規格證據見 #176 §3" + o9[len(v2190.L9_OPEN_NEW):]
    a368, o368 = wbf["Interface"]["A368"].value, pf["Interface"]["A368"].value
    assert a368 == o368.replace(v2190.A368_NEW, v21100.A368_NEW, 1) + TAG + v2190.A368_NEW
    assert "產出比已推導：AMD、昇騰、Maia、TPU、Trn3（v21.10：FP8 對齊作基準、原生精度為低端）" in a368
    h23, o23 = wbf["Inputs"]["H23"].value, pf["Inputs"]["H23"].value
    v218 = openpyxl.load_workbook(REPO / "model" / "archive" / "20261102_Tokenomics_v21.8.xlsx")["Inputs"]["H23"].value
    assert h23 == o23 + "｜原（v21.9 前）：v21.8 起高成本由 4 改 5：2026Q3 四家 hyperscaler 10-Q 皆無 4 年"
    assert "v21.8 起高成本由 4 改 5：2026Q3 四家 hyperscaler 10-Q 皆無 4 年" in v218      # 逐字取 v21.8 檔
    gm = wbf["Gov_Map"]
    for r in range(395, 419):      # Gov_Map N 欄仍是 NonNV L6:L9 的鏡像公式
        assert gm[f"N{r}"].value == pf["Gov_Map"][f"N{r}"].value and str(gm[f"N{r}"].value).startswith("=NonNV!$L$"), r


# ---------------------------------------------------------------- 4. W3
def test_v21100_load_bearing_date_is_version_date(wbf, wbv):
    """追加 14：Load_Bearing!C3＝版本檔名的日期（v21.11 起看守封存的 v21.10 檔；現行版由 test_v21110 看守）。"""
    stem = V2110.name
    d = stem.split("_", 1)[0]
    assert wbf["Load_Bearing"]["C3"].value == f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    assert v21100.VERSION + ".xlsx" == stem      # builder 的版本常數與 CURRENT 一致
    c3 = dt.date.fromisoformat(wbf["Load_Bearing"]["C3"].value)
    assert wbv["Load_Bearing"]["N43"].value == (c3 - dt.date(2026, 11, 1)).days      # 審查日 2026-11-01 距建置日（v21.9 為 2）


def test_v21100_w3_governance(wbf, pf):
    ws, r = _src(wbf, "SRC_DC_004")
    ows, orr = _src(pf, "SRC_DC_004")
    assert (ws[f"K{r}"].value, ws[f"N{r}"].value, ws[f"M{r}"].value) == (1, "一手", v21100.DC004_M_NEW)
    assert (ows[f"K{orr}"].value, ows[f"N{orr}"].value, ows[f"M{orr}"].value) == (3, "二手", v21100.DC004_M_OLD)
    w = ws[f"W{r}"].value
    assert w.startswith(ows[f"W{orr}"].value + "｜v21.10 更正（修訂九；Decisions SL67-01") and "原等級＝3；原一手／二手＝二手" in w
    for c in "ABCDEFGHIJLOPQRSTUV":      # 其他欄不動
        assert ws[f"{c}{r}"].value == ows[f"{c}{orr}"].value, c
    ev = wbf["DB_Evidence"]
    r = _row(ev, "E450")
    assert ev.cell(r, 13).value == "SRC_HW_052、SRC_HW_100、SRC_HW_010"
    for c in range(1, 19):
        if c != 13:
            assert ev.cell(r, c).value == pf["DB_Evidence"].cell(r, c).value, c


def test_v21100_evidence_decisions_readme(wbf):
    ev = wbf["DB_Evidence"]
    r = _row(ev, "E560")
    assert ev.cell(r - 1, 1).value == "E559" and ev.cell(r + 1, 1).value is None
    assert [ev.cell(r, c).value for c in range(1, 19)] == v21100.E560
    assert ev.cell(r, 12).value == "已處理" and ev.cell(r, 10).value == "v21.10" and "Andy 2026-11-04 12:55" in ev.cell(r, 11).value
    assert "docs/evidence/20261104_TPU產出比查核/" in ev.cell(r, 4).value and "Google、NVIDIA" in ev.cell(r, 17).value and "SemiAnalysis" in ev.cell(r, 17).value
    d = wbf["Decisions"]
    r = _row(d, "SL67-01")
    assert d.cell(r - 1, 1).value == "SL66-01" and d.cell(r, 2).value == "v21.10" and d.cell(r, 7).value == "v21.10 已建"
    txt = d.cell(r, 4).value
    for key in ("W1 放寬 2 列", "縮窄 0", "保留原生精度為低端", "修訂九", "IF_NonNV_Out_TPU、IF_NonNV_Out_Trn", "需要我决定的都按照你的建议去执行"):
        assert key in txt, key
    assert "Andy 2026-11-04 12:55" in d.cell(r, 6).value
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert b5.startswith("20261104_Tokenomics_v21.10（次版，底版 v21.9：") and "以下為 v21.9（次版，底版 v21.8：" in b5
    assert "契約名稱值改變者只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串" in b5.split("以下為 v21.9")[0]
    assert str(rm["A1"].value).startswith("Tokenomics v21.10")


# ---------------------------------------------------------------- 5. GOV
def test_v21100_gov_counts(lo):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 129, 183)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v22.0") and str(v.get_name("RNG_Current")).endswith("v22.0")      # v21.11：lo 讀現行版
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 6. 逐格比較 v21.9 → v21.10
NUM_GOV = {("SRC_DC", "K8"), ("SRC_Index", "E160")}      # SRC_DC_004 等級 3 → 1 與 SRC_Index 等級鏡像
TEXT_OK = ({("NonNV", c) for c in ("L6", "L7", "L8", "L9", "A2")} | {("Interface", "A368"), ("Inputs", "H23"), ("README", "A1"), ("README", "B5"),
           ("Load_Bearing", "C3"), ("Alloc", "C177"), ("Alloc", "C178"), ("SRC_DC", "M8"), ("SRC_DC", "N8"), ("SRC_DC", "W8")}
           | {("Gov_Map", f"N{r}") for r in range(395, 419)})      # Gov_Map N 欄＝NonNV L6／L7／L8／L9 說明的鏡像（=NonNV!$L$6 等）


def gov_rule(sh, coord):
    """追加 14：Load_Bearing!C3 改為版本檔名日期 → 審查日距建置日（N 欄）重算。"""
    return sh == "Load_Bearing" and _col(coord) == "N"


def test_v21100_cell_diffs_only_expected(pf, pw, wbf, wbv):
    exp = _csv()
    assert pf.sheetnames == wbf.sheetnames
    hit, num_out, text_out = set(), [], []
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
                    assert abs(float(exp[key][2]) - p) <= 1e-9 * max(1, abs(p)), (key, exp[key][2], p)
                    assert abs(float(exp[key][3]) - q) <= 1e-9 * max(1, abs(q)), (key, exp[key][3], q)
                    continue
                if ws.title in ("DB_Evidence", "Decisions"):
                    continue      # 新列與 E450（下面逐列核對）
                if key in NUM_GOV or gov_rule(ws.title, coord):
                    continue
                if _num(p) and _num(q):
                    num_out.append(key)
                elif key not in TEXT_OK:
                    text_out.append(key)
    assert hit == set(exp), sorted(set(exp) - hit)      # 預期變動 CSV 28 格全部改變且值與預檢相同
    assert len(exp) == 28
    assert num_out == [], num_out
    assert text_out == [], text_out
    # DB_Evidence 只多 E560 一列與 E450 的相關 SRC 欄；Decisions 只多 SL67-01 一列
    r560 = _row(wbf["DB_Evidence"], "E560")
    r450 = _row(wbf["DB_Evidence"], "E450")
    rs = _row(wbf["Decisions"], "SL67-01")
    for sh, allowed in (("DB_Evidence", lambda co: _rown(co) == r560 or co == f"M{r450}"), ("Decisions", lambda co: _rown(co) == rs)):
        a, b = pf[sh], wbf[sh]
        for r in range(1, max(a.max_row, b.max_row) + 1):
            for c in range(1, max(a.max_column, b.max_column) + 1):
                if a.cell(r, c).value != b.cell(r, c).value:
                    assert allowed(a.cell(r, c).coordinate), (sh, a.cell(r, c).coordinate)
    # 公式文字：沒有任何公式改變
    for ws in pf:
        wn = wbf[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y and ((isinstance(x, str) and x.startswith("=")) or (isinstance(y, str) and y.startswith("="))):
                    raise AssertionError((ws.title, ws.cell(r, c).coordinate, x, y))

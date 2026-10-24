"""v15.2 m 證據 B 段（工作單 docs/workorders/20261017_v15.2_m證據B段.md r1）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

V1 B2 Cap_In C280:E280 ＝ 4.5／3.3／5.9；B3 Calib D67 ＝ 1.15；B1／B5 只加註（數值不變）；B6 只改 Gov_Map 文字。
V2 Gov_Map GM342 類別 Analogy → Derived（修訂九，原字樣保留於 N、AL 欄），區間 0.9–1.45；承重清單 57 → 56。
V3 J2、B4 標籤；V4 Decisions SL47-01…05；V5 DB_Evidence E387…E392；V6 區間端點重產。
"""
import json
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path
from test_v2120 import CHANGED as V2120_CHANGED, REVERT as SB_OLD      # v21.2：AL_SpendBasis 改 1.8 的預期變動名稱（44 個）與舊值輸入

# v19.1：Arch!C17 改值（4224 → 2176，W1 B2）後 Luna 相關值變動；本檔下列檢驗的事前值在 C17 回 4224（SRC_MOD_106＝1024）時仍成立，由 test_v1910 看守兩者的關係
C17_OLD = {"SRC_MOD_106": 1024, **SB_OLD}      # v21.2：另把 Alloc_In C23:E23 設回 0.85／0.73／1.17，下列事前值仍成立；新值由 test_v2120 看守
PREWARM = {"test_v1520_m_values_and_decomposition": [C17_OLD]}

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "parity" / "fixtures"
PREV = REPO / "model" / "archive" / "20261017_Tokenomics_v15.1.xlsx"
V152 = REPO / "model" / "archive" / "20261017_Tokenomics_v15.2.xlsx"      # v15.3：v15.1→v15.2 的差異改對封存的 v15.2 釘住（現行版已是 v15.3；v15.2→v15.3 由 test_v1530 釘住）
CHANGED = set(json.loads((FIXTURES / "v152_changed_names.json").read_text(encoding="utf-8"))["names"])


def _flat(v):
    if isinstance(v, (list, tuple)):
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


def _row(ws, rid, col=1):
    rows = [r for r in range(5, ws.max_row + 1) if ws.cell(r, col).value == rid]
    assert len(rows) == 1, (rid, rows)
    return rows[0]


def test_v1520_inputs_changed_and_guards_unchanged(wbf, lo):
    ci, cal = wbf["Cap_In"], wbf["Calib"]
    assert [ci[f"{c}280"].value for c in "CDE"] == [4.5, 3.3, 5.9]
    assert cal["D67"].value == 1.15
    v = lo.view({})
    assert v.get_name("CAP_Px25_Astra") == 4.5 and v.get_name("CAP_Px25_Astra_Lo") == 3.3 and v.get_name("CAP_Px25_Astra_Hi") == 5.9
    # 不得變
    assert [cal[f"{c}67"].value for c in "CEFG"] == [1.2, 1, 1, 1]
    assert wbf["Alloc_In"]["C26"].value == 1.0
    sd = wbf["SRC_Demand"]
    r = _row(sd, "SRC_DEM_004")
    assert [sd[f"{c}{r}"].value for c in "CDE"] == [8.4, 7.5, 8.8]
    prev = openpyxl.load_workbook(PREV)
    for a in ("C31", "D31", "E31"):
        assert ci[a].value == prev["Cap_In"][a].value


def test_v1520_m_values_and_decomposition(lo):
    """L1_MFleet 0.4073 → 0.4600；單項：只套 B2 0.5034、只套 B3 0.3722（見報告第 4 節）。"""
    v = lo.view(C17_OLD)
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-9
    assert abs(v.get_name("L1_MFleet_Lo") - 0.242723485975401) < 1e-9 and abs(v.get_name("L1_MFleet_Hi") - 1.33130310709466) < 1e-9
    b2 = lo.view({**C17_OLD, "Cap_In!C280": 4.5, "Cap_In!D280": 3.3, "Cap_In!E280": 5.9, "Calib!D67": 1})
    b3 = lo.view({**C17_OLD, "Cap_In!C280": 7.174, "Cap_In!D280": 2.089, "Cap_In!E280": 16.33, "Calib!D67": 1.15})
    assert abs(b2.get_name("L1_MFleet") - 0.503438442475506) < 1e-9
    assert abs(b3.get_name("L1_MFleet") - 0.37215506256345) < 1e-9
    assert abs(v.get_name("IF_AllocServeGW") - 0.89809617101894) < 1e-12 and abs(v.get_name("L1_LReqFleet_Id") - 0.756109635897205) < 1e-12


def test_v1520_only_expected_names_changed(lo):
    """與 v15.1 逐名稱比較：值不同的具名範圍恰好等於 fixtures/v152_changed_names.json（不多不少）。"""
    pw = openpyxl.load_workbook(PREV, data_only=True)
    v152 = openpyxl.load_workbook(V152, data_only=True)      # v15.3：以封存的 v15.2（LibreOffice 重算存檔）取值
    v = lo.view({})
    changed = set()
    for n, d in pw.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text:
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        sh2, rg2 = v152.defined_names[n].attr_text.rsplit("!", 1)
        c1b, r1b, c2b, r2b = range_boundaries(rg2.replace("$", ""))
        got = [v152[sh2.strip("'")].cell(r, c).value for r in range(r1b, r2b + 1) for c in range(c1b, c2b + 1)]
        if len(want) != len(got) or not all(_same(a, b) for a, b in zip(want, got)):
            changed.add(n)
    assert changed == CHANGED, (sorted(changed - CHANGED)[:20], sorted(CHANGED - changed)[:20])
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 135, 182)      # v21.1: 133 → 135 (SRC_DEM_089/090 lack a second source, W1 +2)
    #      # v19.1：133 → 132（SRC_MOD_018 填 C1 免除標記，Z22 缺第二來源 1 → 0）； v17.2：W1 278 → 131（W1 第二來源 B1：A 86、C1 53、Q11 8 離開；預期變動）
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert v.get_name("LB_LiveCount") == 56 and len(_flat(v.get_name("LB_Rows"))) == 56


def test_v1520_gm342_correction_original_kept(wbf):
    ws = wbf["Gov_Map"]
    r = next(x for x in range(5, ws.max_row + 1) if ws.cell(x, 3).value == "Calib" and ws.cell(x, 4).value == "D67")
    assert ws[f"A{r}"].value == "GM342"
    assert ws[f"F{r}"].value == "Derived" and ws[f"K{r}"].value == 0.9 and ws[f"L{r}"].value == 1.45
    assert ws[f"M{r}"].value == "×0.9–×1.45（v15.2 B3；原 ×0.5–×1.5 Sens_Perf 情境）"
    n = ws[f"N{r}"].value
    assert n.startswith("非 Hopper 世代沿用 GB300 擬合的 η_d（Block 2 最大 Analogy）") and "6.0-0078" in n and "1.13–1.27" in n
    al = ws[f"AL{r}"].value
    assert "類別＝Analogy" in al and "非 Hopper 世代沿用 GB300 擬合的 η_d（Block 2 最大 Analogy）" in al and "×0.5–×1.5（Sens_Perf 情境）" in al and "SL47-05" in al
    r57 = next(x for x in range(5, ws.max_row + 1) if ws.cell(x, 3).value == "Cap_In" and ws.cell(x, 4).value == "C31:E31")
    assert ws[f"M{r57}"].value.startswith("各層 ±0.15，合計維持 1") and "v15.2 B6：Astra 0.10–0.30" in ws[f"M{r57}"].value
    r44 = next(x for x in range(5, ws.max_row + 1) if ws.cell(x, 3).value == "Alloc_In" and ws.cell(x, 4).value == "C26")
    assert "v15.2 B5：維持 1.0" in ws[f"N{r44}"].value and ws[f"N{r44}"].value.startswith("v5.36 B4（X47）")
    lb = wbf["Load_Bearing"]
    assert "GM342" not in {lb.cell(x, 1).value for x in range(5, lb.max_row + 1)} and "=Gov_Map!$A$%d" % r not in {lb.cell(x, 1).value for x in range(5, lb.max_row + 1)}


def test_v1520_labels_and_notes(wbf):
    ci = wbf["Cap_In"]
    assert "用量加權" in ci["A280"].value and "在售天數加權" not in ci["A280"].value
    g = ci["G280"].value
    assert g.startswith("推理旗艦序列") and "按在售天數加權，不是按用量" in g and "v15.2 B2：改用量加權" in g and "4.5、區間 3.3–5.9" in g
    cal = wbf["Calib"]
    assert cal["G9"].value == "驗證（舊軟體；容量受限點，不用於 η 驗證）" and cal["F9"].value == "驗證（舊軟體）"
    assert cal["J67"].value.endswith("（v15.2 起 D67＝1.15，依 MLPerf v6.0 配對，見 GM342）") and "GB200、VR200 沿用 GB300" in cal["J67"].value
    sd = wbf["SRC_Demand"]
    r8, r22 = _row(sd, "SRC_DEM_004"), _row(sd, "SRC_DEM_018")
    assert "v15.2 B1：低端 7.5 維持" in sd[f"W{r8}"].value and sd[f"W{r8}"].value.startswith("服務占比 0.41")
    assert sd[f"B{r22}"].value == "Microsoft 端推論類工作負載（含研究推論；Azure 帳單，全年推估）"
    assert "v15.2 J2：標籤更正" in sd[f"W{r22}"].value and [sd[f"{c}{r22}"].value for c in "CDE"] == [12.6, 12.3, 13]


def test_v1520_decisions_and_evidence(wbf):
    d = wbf["Decisions"]
    for i in range(1, 6):
        r = _row(d, f"SL47-0{i}")
        assert d.cell(r, 2).value == "v15.2" and d.cell(r, 7).value == "v15.2 已建" and d.cell(r, 10).value == "否"
        assert "可撤回" in d.cell(r, 6).value and "Andy 2026-10-17" in d.cell(r, 6).value
    assert "Analogy" in d.cell(_row(d, "SL47-05"), 4).value and "更正理由" in d.cell(_row(d, "SL47-05"), 4).value
    e = wbf["DB_Evidence"]
    ids = [e.cell(r, 1).value for r in range(5, e.max_row + 1)]
    assert ids[ids.index("E387"):ids.index("E387") + 6] == ["E387", "E388", "E389", "E390", "E391", "E392"]      # v15.3：其後另有 E393…E397
    r = _row(e, "E392")
    assert e.cell(r, 9).value == "待查" and e.cell(r, 12).value == "待判定"
    assert "可撤回" in e.cell(_row(e, "E389"), 11).value and e.cell(_row(e, "E389"), 9).value == "採用（B3）"


def test_v1520_changed_cells_only_expected():
    """與 v15.1 逐格比對（公式文字或輸入值）：只有預期的頁與格不同；其餘頁 0。
    Alloc 的 298 格＝Alloc N 節情境值 10 格（v12.0 靜態表，與 RNG_* 同源重產）＋ O 節 RNG 靜態端點與 P 節指紋（重產）及版本字串；Load_Bearing 392 格＝少一列（GM342 離開承重清單）後上移；Checks B122＝K5 標籤文字。"""
    a, b = openpyxl.load_workbook(PREV), openpyxl.load_workbook(V152)      # v15.3：對封存的 v15.2
    diffs = {}
    for ws in a:
        wn = b[ws.title]
        coords = {c.coordinate for r in ws.iter_rows() for c in r if c.value is not None} | {c.coordinate for r in wn.iter_rows() for c in r if c.value is not None}
        d = sorted(x for x in coords if ws[x].value != wn[x].value)
        if d:
            diffs[ws.title] = d
    assert set(diffs) == {"README", "Calib", "Cap_In", "Alloc", "Load_Bearing", "Checks", "Gov_Map", "Decisions", "SRC_Demand", "DB_Evidence"}, set(diffs)
    assert diffs["Calib"] == ["D67", "G9", "J67"]
    assert diffs["Cap_In"] == ["A280", "C280", "D280", "E280", "G280"]
    assert diffs["Gov_Map"] == sorted(["F346", "K346", "L346", "M346", "N346", "AL346", "M461", "N648"])
    assert diffs["SRC_Demand"] == ["B22", "W22", "W8"]
    assert diffs["Checks"] == ["B122"] and sorted(diffs["README"]) == ["A1", "A59", "B5", "B59"]
    assert len(diffs["Decisions"]) == 50 and len(diffs["DB_Evidence"]) == 108
    import re
    assert len(diffs["Alloc"]) == 298 and {re.match("[A-Z]+", x).group() for x in diffs["Alloc"]} == {"C", "D", "F", "G", "H"}
    assert len(diffs["Load_Bearing"]) == 392

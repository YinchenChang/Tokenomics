"""v16.0 L 按世代起點計算（工作單 docs/workorders/20261018_v16.0_L世代起點.md r0）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

W1 Cap_In N 節：s_v／A／g_pre 輸入、t0、L_rel、權重、機隊 L（L1_LTotalFleetV 三值 ＝ 事前計算，容差 1e-6）、L1_LTotalV（4 格）、L1_LTotalDisc、L1_LReqFleet_IdNoK。
W2 Cap_In 第 242 列改讀 L1_LTotalFleetV（三態各一情境）；三列對照；L1 P89；L1 新增四列。
W3 Decisions SL49-01…04、DB_Evidence E398、README。
不得變：所有既有名稱（L1_LTotal、L1_LReqFleet_Id、L1_MFleet 等）逐值不變，唯一例外是版本字串與 Gov_Map 哨兵（RNG_Version／RNG_Current／IDX_SrcID）。
"""
import re
from math import exp, log
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V153 = REPO / "model" / "archive" / "20261018_Tokenomics_v15.3.xlsx"
NEW_NAMES = {"L1_LTotalFleetV", "L1_LTotalFleetV_Lo", "L1_LTotalFleetV_Hi", "L1_LTotalV", "L1_LTotalDisc", "L1_LTotalDisc_Lo", "L1_LTotalDisc_Hi",
             "L1_LReqFleet_IdNoK", "L1_LReqFleet_IdNoK_Lo", "L1_LReqFleet_IdNoK_Hi"}
VERSION_NAMES = {"RNG_Version", "RNG_Current", "IDX_SrcID"}      # 版本字串；Gov_Map 新增 6 列使 SRC_Index 哨兵由空字串變 '—'
PRE = {"L1_LTotalFleetV": 0.7159, "L1_LTotalFleetV_Lo": 0.4265, "L1_LTotalFleetV_Hi": 1.1190,
       "L1_LTotalDisc": 0.6988, "L1_LTotalDisc_Lo": 0.4401, "L1_LTotalDisc_Hi": 1.0941,
       "L1_LReqFleet_IdNoK": 0.7561, "L1_LReqFleet_IdNoK_Lo": 0.4905, "L1_LReqFleet_IdNoK_Hi": 0.9223}      # 工作單 W1 的 chat 端事前計算（4 位）


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


def _lab(ws, prefix):
    rows = [r for r in range(290, ws.max_row + 1) if str(ws.cell(r, 1).value or "").startswith(prefix)]
    assert len(rows) == 1, (prefix, rows)
    return rows[0]


def _ref(wbf, name):
    t = wbf.defined_names[name].attr_text
    sh, rg = t.rsplit("!", 1)
    return sh, rg.replace("$", "")


def _lrel(g, t1, rho, T, t0, gpre):
    past = (1 - (1 + gpre) ** (-t0)) / log(1 + gpre) if t0 > 0 else 0.0
    fut = (((1 + g) ** (t1 - t0) - 1) + rho * ((1 + g) ** (T - t0) - (1 + g) ** (t1 - t0))) / log(1 + g)
    return (past + fut) / T


def test_v1600_new_values_match_precomputed(lo):
    v = lo.view({})
    for n, want in PRE.items():
        assert abs(v.get_name(n) - want) < 1e-4, (n, v.get_name(n), want)      # 工作單事前計算只有 4 位
    assert abs(v.get_name("L1_LTotalFleetV") - 0.715893335392) < 1e-6 and abs(v.get_name("L1_LTotalFleetV_Lo") - 0.426456907365) < 1e-6
    assert abs(v.get_name("L1_LTotalFleetV_Hi") - 1.119003153247) < 1e-6


def test_v1600_independent_python_recomputation(wbf, lo):
    """用 Python 獨立重算：機隊 L、折現版 L、不含 κ 所需 L，與 LibreOffice 的值相同（1e-9）。"""
    v = lo.view({})
    ci = wbf["Cap_In"]
    g = {c: v.get("Cap_In", f"{c}226") for c in "CDE"}
    t1 = {c: v.get("Cap_In", f"{c}227") for c in "CDE"}
    rho = {c: v.get("Cap_In", f"{c}228") for c in "CDE"}
    T = {c: v.get("Cap_In", f"{c}229") for c in "CDE"}
    r_sv, r_lo, r_hi, r_a, r_gp = (_lab(ci, p) for p in ("世代服務起點 s_v（年", "世代服務起點 s_v 低", "世代服務起點 s_v 高", "校準錨點年 A", "錨點前中階牌價年變化率 g_pre"))
    A = v.get("Cap_In", f"C{r_a}")
    gp = {c: v.get("Cap_In", f"{c}{r_gp}") for c in "CDE"}
    sv = {k: [v.get("Cap_In", f"{c}{r}") for c in "CDEF"] for k, r in (("b", r_sv), ("lo", r_lo), ("hi", r_hi))}
    share = _flat(v.get_name("AL_ShareGen")); rev = _flat(v.get_name("AL_RevGW25"))
    w = [s * r if s > 0 else 0.0 for s, r in zip(share, rev)]
    comb = {"C": ("hi" if False else "b", "C", gp["C"]), "D": ("hi", "D", gp["E"]), "E": ("lo", "E", gp["D"])}      # 低端組合：s_v 取高（較晚）、g_pre 取 E 欄；高端組合：s_v 取低（較早）、g_pre 取 D 欄
    got = {}
    for col, (k, sc, g_pre) in comb.items():
        ls = [_lrel(g[sc], t1[sc], rho[sc], T[sc], max(0.0, A - s), g_pre) for s in sv[k]]
        got[col] = sum(a * b for a, b in zip(w, ls)) / sum(w)
    assert abs(v.get_name("L1_LTotalFleetV") - got["C"]) < 1e-9
    assert abs(v.get_name("L1_LTotalFleetV_Lo") - got["D"]) < 1e-9 and abs(v.get_name("L1_LTotalFleetV_Hi") - got["E"]) < 1e-9
    wacc = {"C": v.get("Inputs", "E28"), "D": v.get("Inputs", "D28"), "E": v.get("Inputs", "F28")}

    def disc(c):
        a = log(1 + g[c]) - log(1 + wacc[c]); d = -log(1 + wacc[c])
        return (((exp(a * t1[c]) - 1) + rho[c] * (exp(a * T[c]) - exp(a * t1[c]))) / a) / ((exp(d * T[c]) - 1) / d)
    assert abs(v.get_name("L1_LTotalDisc") - disc("C")) < 1e-9 and abs(v.get_name("L1_LTotalDisc_Lo") - disc("D")) < 1e-9 and abs(v.get_name("L1_LTotalDisc_Hi") - disc("E")) < 1e-9
    d4, d7 = v.get_name("SRC_DEM_004"), v.get_name("SRC_DEM_007")
    sb, sb_lo, sb_hi = v.get_name("AL_SpendBasis"), v.get_name("AL_SpendBasis_Lo"), v.get_name("AL_SpendBasis_Hi")
    assert abs(v.get_name("L1_LReqFleet_IdNoK") - d4 / (sb * d7)) < 1e-9
    assert abs(v.get_name("L1_LReqFleet_IdNoK_Lo") - v.get_name("SRC_DEM_004_Lo") / (sb_hi * d7)) < 1e-9
    assert abs(v.get_name("L1_LReqFleet_IdNoK_Hi") - v.get_name("SRC_DEM_004_Hi") / (sb_lo * d7)) < 1e-9


def test_v1600_t0_zero_equals_l1_ltotal(wbf, lo):
    """t0＝0 的世代（GB300、VR200 基準；GB200 低端組合）L_rel 等於 L1_LTotal（對應欄的 g、T1、ρ、T）。"""
    v = lo.view({})
    ci = wbf["Cap_In"]
    r_t0, r_t0lo, r_l, r_llo, r_lhi = (_lab(ci, p) for p in ("錨點時已服務年數 t0＝MAX", "t0（低端組合", "L_rel（相對錨點；基準", "L_rel（低端組合", "L_rel（高端組合"))
    for col in "EF":
        assert v.get("Cap_In", f"{col}{r_t0}") == 0
        assert abs(v.get("Cap_In", f"{col}{r_l}") - v.get_name("L1_LTotal")) < 1e-12
    assert v.get("Cap_In", f"D{r_t0lo}") == 0 and abs(v.get("Cap_In", f"D{r_llo}") - v.get_name("L1_LTotal_Lo")) < 1e-12
    assert v.get("Cap_In", f"E{r_t0lo}") == 0 and abs(v.get("Cap_In", f"E{r_llo}") - v.get_name("L1_LTotal_Lo")) < 1e-12
    assert abs(v.get("Cap_In", f"F{r_lhi}") - v.get_name("L1_LTotal_Hi")) < 1e-12 and abs(v.get("Cap_In", f"E{r_lhi}") - v.get_name("L1_LTotal_Hi")) < 1e-12
    assert v.get("Cap_In", f"C{r_t0}") == 2.0 and abs(v.get("Cap_In", f"D{r_t0}") - 0.5) < 1e-12      # Hopper 2.0、GB200 0.5（基準）


def test_v1600_ltotalv_is_four_cell_range(wbf, lo):
    v = lo.view({})
    sh, rg = _ref(wbf, "L1_LTotalV")
    assert sh == "Cap_In" and re.fullmatch(r"C\d+:F\d+", rg), (sh, rg)
    vals = _flat(v.get_name("L1_LTotalV"))
    assert len(vals) == 4 and all(abs(x - v.get_name("L1_LTotal")) < 1e-12 for x in vals)
    assert "L1_LTotalV_Lo" not in wbf.defined_names and "L1_LTotalV_Hi" not in wbf.defined_names
    l1 = wbf["L1"]
    r = _row(l1, "L1_LTotalV")
    assert l1[f"D{r}"].value.startswith("=INDEX(Cap_In!") and l1[f"E{r}"].value.startswith("=MIN(") and l1[f"F{r}"].value.startswith("=MAX(")


def test_v1600_three_state_row242(wbf, lo):
    v = lo.view({})
    assert v.get("Cap_In", "C242") == "未定（區間重疊；基準 L 0.716 對所需 L 0.756）"
    assert v.get("Cap_In", "D242").startswith("對照：低端欄 L ") and v.get("Cap_In", "E242").startswith("對照：高端欄 L ")
    neg = lo.view({"Cap_In!C226": -0.9, "Cap_In!D226": -0.9, "Cap_In!E226": -0.85})      # 世代起點 L 較 v15.3 口徑低，需 g 更低才使 L 上端 0.315 < 所需 L 下端 0.357
    assert neg.get("Cap_In", "C242") == "未回本（L 區間全在所需 L 之下）"
    pos = lo.view({"Cap_In!C226": 0.3, "Cap_In!D226": 0.3, "Cap_In!E226": 0.4, "Cap_In!C227": 6, "Cap_In!D227": 6, "Cap_In!E227": 6})
    assert pos.get("Cap_In", "C242") == "回本（L 區間全在所需 L 之上）"
    # L1 P89 同步（恆等式讀法）
    p89 = v.get("L1", "P89")
    assert p89.startswith("恆等式讀法：未定（世代起點 L 0.72 對所需 L 0.76；v15.3 口徑 2025＝第 0 年：L 0.660）")
    assert neg.get("L1", "P89").startswith("恆等式讀法：未回本") and pos.get("L1", "P89").startswith("恆等式讀法：回本")
    assert "v15.3 口徑 2025＝第 0 年：L " in neg.get("L1", "P89") and "v15.3 口徑 2025＝第 0 年：L " in pos.get("L1", "P89")


def test_v1600_comparison_rows(wbf, lo):
    v = lo.view({})
    ci = wbf["Cap_In"]
    ra, rb, rc = (_lab(ci, p) for p in ("對照：2025＝第 0 年（v15.3 口徑）", "對照：世代起點 L 對 不含 κ 所需 L", "對照：折現版 L 對 不含 κ 所需 L"))
    assert v.get("Cap_In", f"C{ra}") == "未定（區間重疊；基準 L（2025＝第 0 年） 0.660 對所需 L 0.756）"
    assert v.get("Cap_In", f"C{rb}") == "未定（區間重疊；基準 世代起點 L 0.716 對所需 L 0.756）"
    assert v.get("Cap_In", f"C{rc}") == "未定（區間重疊；基準 折現版 L 0.699 對所需 L 0.756）"
    neg = lo.view({"Cap_In!C226": -0.9, "Cap_In!D226": -0.9, "Cap_In!E226": -0.85})      # 世代起點 L 較 v15.3 口徑低，需 g 更低才使 L 上端 0.315 < 所需 L 下端 0.357
    assert neg.get("Cap_In", f"C{rb}").startswith(("未回本", "未定")) and neg.get("Cap_In", f"C{rc}").startswith(("未回本", "未定"))


def test_v1600_t0_above_t1_unsupported(wbf, lo):
    """t0 > T1 的世代（目前沒有）：L_rel 輸出文字、機隊 L 與判讀回報『未支援／非數字』，不出錯誤值（待 Project 判斷）。"""
    ci = wbf["Cap_In"]
    r_sv = _lab(ci, "世代服務起點 s_v（年")
    r_t0, r_l = (_lab(ci, p) for p in ("錨點時已服務年數 t0＝MAX", "L_rel（相對錨點；基準"))
    s = lo.view({f"Cap_In!C{r_sv}": 2020.0})
    assert s.get("Cap_In", f"C{r_l}") == "t0 > T1（已降級，未支援）"
    assert s.get_name("L1_LTotalFleetV") == "含 t0 > T1 的世代（已降級，未支援）"
    assert s.get("Cap_In", "C242") == "所需 L 或 L 非數字（本情境）"
    assert s.get("L1", "P89") == "推算值非數字（本情境）"
    assert isinstance(s.get_name("L1_LTotalFleetV_Lo"), float)      # 低端組合用 s_v 較晚，不受影響


def test_v1600_inputs_marks_and_gov_map(wbf):
    ci, gm = wbf["Cap_In"], wbf["Gov_Map"]
    r_sv, r_lo, r_hi, r_a, r_gp = (_lab(ci, p) for p in ("世代服務起點 s_v（年", "世代服務起點 s_v 低", "世代服務起點 s_v 高", "校準錨點年 A", "錨點前中階牌價年變化率 g_pre"))
    assert [ci[f"{c}{r_sv}"].value for c in "CDEF"] == [2023.5, 2025.0, 2025.5, 2026.75]
    assert [ci[f"{c}{r_lo}"].value for c in "CDEF"] == [2023.0, 2025.0, 2025.5, 2026.75]
    assert [ci[f"{c}{r_hi}"].value for c in "CDEF"] == [2024.0, 2025.5, 2025.6, 2027.0]
    assert ci[f"C{r_a}"].value == 2025.5 and [ci[f"{c}{r_gp}"].value for c in "CDE"] == [-0.09, -0.30, -0.09]
    assert ci[f"G{r_sv}"].value == "Assumed" and ci[f"G{r_a}"].value == "Decision" and ci[f"G{r_gp}"].value == "Assumed"
    rows = {(gm.cell(r, 3).value, gm.cell(r, 4).value): r for r in range(5, gm.max_row + 1)}
    for cell, cls in ((f"C{r_sv}:F{r_sv}", "Assumed"), (f"C{r_lo}:F{r_lo}", "Assumed"), (f"C{r_hi}:F{r_hi}", "Assumed"), (f"C{r_a}", "Decision"), (f"C{r_gp}", "Assumed"), (f"D{r_gp}:E{r_gp}", "Assumed")):
        r = rows[("Cap_In", cell)]
        assert gm[f"F{r}"].value == cls and str(gm[f"J{r}"].value).startswith("SL49-"), cell
    # 修訂九：不改寫既有標記（本版不更正任何標記）；v15.3 的 Derived 標記仍在
    assert ci["F226"].value == "Derived" and ci["F228"].value == "Derived（兩種讀法）"


def test_v1600_decisions_evidence_readme(wbf):
    d = wbf["Decisions"]
    for i in range(1, 5):
        r = _row(d, f"SL49-0{i}")
        assert d.cell(r, 2).value == "v16.0" and d.cell(r, 7).value == "v16.0 已建" and d.cell(r, 10).value == "否" and "可撤回" in d.cell(r, 6).value
    t1 = d.cell(_row(d, "SL49-01"), 4).value
    assert "L 应该就是衡量在这个硬体的生命周期里" in t1 and "我们用二零二五，其实是只是一个锚点" in t1 and "SL48-01 已於 v15.3 補登 C1" in t1
    assert "L1_LTotalFleetV" in d.cell(_row(d, "SL49-02"), 4).value
    t3 = d.cell(_row(d, "SL49-03"), 4).value
    assert "F1" in t3 and "F2" in t3 and "未回應前不改主口徑" in t3
    e = wbf["DB_Evidence"]
    ids = [e.cell(r, 1).value for r in range(5, e.max_row + 1)]
    assert ids[-1] == "E398" and ids[-6:-1] == ["E393", "E394", "E395", "E396", "E397"]
    assert "不新增外部來源" in e.cell(_row(e, "E398"), 4).value and "可撤回" in e.cell(_row(e, "E398"), 11).value
    rd = wbf["README"]
    assert str(rd["B5"].value).startswith("20261018_Tokenomics_v16.0（主版：") and str(rd["A1"].value).startswith("Tokenomics v16.0")
    assert any(rd.cell(r, 1).value == "v16.0 L 世代起點" for r in range(4, rd.max_row + 1))


def test_v1600_only_new_names_and_nothing_else_changed(lo):
    """與封存的 v15.3 逐名稱比較：新增名稱恰為 10 個；既有名稱值全部相同，唯一例外是版本字串與 Gov_Map 哨兵。"""
    pw = openpyxl.load_workbook(V153, data_only=True)
    pf = openpyxl.load_workbook(V153)
    v = lo.view({})
    assert set(v.names) - set(pf.defined_names) == NEW_NAMES
    assert set(pf.defined_names) - set(v.names) == set()
    changed = set()
    for n, d in pw.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text:
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        if len(want) != len(got) or not all(_same(a, b) for a, b in zip(want, got)):
            changed.add(n)
    assert changed == VERSION_NAMES, sorted(changed ^ VERSION_NAMES)
    # 重點名稱逐值
    for n, want in (("L1_LTotal", 0.659505673291395), ("L1_LTotal_Lo", 0.396282624140417), ("L1_LTotal_Hi", 1.09636652745877), ("L1_LReqFleet_Id", 0.756109635897205),
                    ("L1_MFleet", 0.460003106109943), ("IF_AllocServeGW", 0.89809617101894)):
        assert abs(v.get_name(n) - want) < 1e-9, n
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 280, 182)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0


def test_v1600_changed_cells_only_expected():
    """與封存的 v15.3 逐格比對（公式文字或輸入值）：只有預期的頁與格不同。"""
    a, b = openpyxl.load_workbook(V153), openpyxl.load_workbook(model_path())
    diffs = {}
    for ws in a:
        wn = b[ws.title]
        coords = {c.coordinate for r in ws.iter_rows() for c in r if c.value is not None} | {c.coordinate for r in wn.iter_rows() for c in r if c.value is not None}
        d = sorted(x for x in coords if ws[x].value != wn[x].value)
        if d:
            diffs[ws.title] = d
    assert set(diffs) <= {"README", "Cap_In", "L1", "Alloc", "Gov_Map", "Load_Bearing", "Decisions", "DB_Evidence", "SRC_Index"}, set(diffs)
    rows = lambda cells: sorted({int(re.sub("[A-Z]+", "", x)) for x in cells})
    assert sorted(diffs["README"]) == ["A1", "A61", "B5", "B61"]
    cap = diffs["Cap_In"]
    assert {x for x in cap if int(re.sub("[A-Z]+", "", x)) <= 296} == {"A242", "C242", "D242", "E242", "G242"}      # 既有格：只有第 242 列
    assert rows(cap)[0] == 242 and min(r for r in rows(cap) if r > 242) == 298      # 新節接在第 296 列之後
    assert sorted(diffs["L1"], key=lambda s: (int(re.sub("[A-Z]+", "", s)), s))[0] == "P89" and rows(diffs["L1"]) == [89, 112, 113, 114, 115]
    assert sorted(diffs["Alloc"]) == ["C177"]      # RNG_Version（常數）；RNG_Current 是公式，文字不變、值隨 README B5
    assert len(diffs["Decisions"]) == 40 and len(diffs["DB_Evidence"]) == 18
    assert {re.match("[A-Z]+", x).group() for x in diffs["Load_Bearing"]} == {"J"}      # 『影響的 L1 列』清單新增新名稱
    assert min(rows(diffs["Gov_Map"])) == 692 and len(rows(diffs["Gov_Map"])) == 6

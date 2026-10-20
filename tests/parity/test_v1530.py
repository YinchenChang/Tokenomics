"""v15.3 L 證據 B 段＋v15.2 修補（工作單 docs/workorders/20261018_v15.3_L證據與修補.md r0）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

W1 E1 Cap_In C226:E226 g＝−0.09／−0.20／+0.05；E2 D228 公式乘吞吐倍數（GB200 欄，≈0.170）、E228＝0.7；E3 T1 不變；標記 Assumed → Derived（修訂九，原字樣保留）。
W2 D1 Cap_In 第 242 列三態判讀（恆等式讀法）；第 243 列標籤改對照。
W3 C2 Calib D156＝SQRT(C254*D201/$D$67)（2.050；r1 同口徑）；Gov_Map GM685 區間 1.59–2.64；RNG_* 端點重產。r1：L1 P89 三態、過期標籤更新、Decisions SL48-09。
W4 Gov_Map AA 欄 COUNTIF 範圍 1000。W5 Decisions SL48-01…09。W6 DB_Evidence E393…E397。
不得變：L1_MFleet、IF_AllocServeGW、L1_LReqFleet_Id、Calib D67、Cap_In C280。
"""
import json
import re
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "tests" / "parity" / "fixtures"
V152 = REPO / "model" / "archive" / "20261017_Tokenomics_v15.2.xlsx"
V153 = REPO / "model" / "archive" / "20261018_Tokenomics_v15.3.xlsx"      # v16.0：v15.2→v15.3 的差異改對封存的 v15.3 釘住（現行版已是 v16.0；v15.3→v16.0 由 test_v1600 釘住）
CHANGED = set(json.loads((FIXTURES / "v153_changed_names.json").read_text(encoding="utf-8"))["names"])
RHO_D = "=IF_PriceRef_Luna/IF_PriceRef_Sol*INDEX(IF_TokGW_Luna,1,4)/INDEX(IF_TokGW_Sol,1,4)"


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


def _gm(ws, sheet, cell):
    rows = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 3).value == sheet and ws.cell(r, 4).value == cell]
    assert len(rows) == 1, (sheet, cell, rows)
    return rows[0]


def test_v1530_w1_inputs_and_l_values(wbf, lo):
    ci = wbf["Cap_In"]
    assert [ci[f"{c}226"].value for c in "CDE"] == [-0.09, -0.2, 0.05]
    assert [ci[f"{c}227"].value for c in "CDE"] == [4, 3, 5]                 # E3 不變
    assert ci["C228"].value == 0.5 and ci["E228"].value == 0.7 and ci["D228"].value == RHO_D
    v = lo.view({})
    rho_lo = v.get_name("IF_PriceRef_Luna") / v.get_name("IF_PriceRef_Sol") * _flat(v.get_name("IF_TokGW_Luna"))[3] / _flat(v.get_name("IF_TokGW_Sol"))[3]
    assert abs(v.get("Cap_In", "D228") - rho_lo) < 1e-12 and abs(rho_lo - 0.170368021775908) < 1e-9
    assert abs(_flat(v.get_name("IF_TokGW_Luna"))[3] / _flat(v.get_name("IF_TokGW_Sol"))[3] - 3.4073) < 1e-3      # 第 4 格＝GB200 欄（吞吐倍數 3.41）
    assert abs(v.get_name("L1_LTotal") - 0.659505673291395) < 1e-9
    assert abs(v.get_name("L1_LTotal_Lo") - 0.396282624140417) < 1e-9 and abs(v.get_name("L1_LTotal_Hi") - 1.09636652745877) < 1e-9
    assert abs(v.get_name("L1_LPrice") - 0.763665278739318) < 1e-9 and abs(v.get_name("L1_LDemote") - 0.86360568124837) < 1e-9


def test_v1530_unchanged_guards(wbf, lo):
    v = lo.view({})
    assert abs(v.get_name("L1_MFleet") - 0.460003106109943) < 1e-12
    assert abs(v.get_name("L1_MFleet_Lo") - 0.242723485975401) < 1e-9 and abs(v.get_name("L1_MFleet_Hi") - 1.33130310709466) < 1e-9
    assert abs(v.get_name("IF_AllocServeGW") - 0.89809617101894) < 1e-12 and abs(v.get_name("L1_LReqFleet_Id") - 0.756109635897205) < 1e-12
    assert wbf["Calib"]["D67"].value == 1.15 and wbf["Cap_In"]["C280"].value == 4.5
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 133, 182)      # v17.2：W1 278 → 131（W1 第二來源 B1：A 86、C1 53、Q11 8 離開；預期變動）
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0


def test_v1530_marks_corrected_original_kept(wbf):
    ci, gm = wbf["Cap_In"], wbf["Gov_Map"]
    assert ci["F226"].value == "Derived" and ci["F228"].value == "Derived（兩種讀法）"
    assert "標記由「Assumed」更正為「Derived」" in ci["G226"].value and ci["G226"].value.startswith("藍字三格（登錄 Gov_Map）；現值以 C226:E226 為準（v17.0：基準 −0.09、低 −0.20、高 +0.05）｜原始設定：基準 −0.10、低 −0.25、高 +0.05。")      # v17.1 W6：開頭改指向現值，原始設定保留
    assert "標記由「Assumed（C、E）／Derived（D）」更正為「Derived（兩種讀法）」" in ci["G228"].value and "v15.3 E2" in ci["G228"].value and "0.17" in ci["G228"].value
    assert "v15.3 E1：2024-05～2026-10 中階牌價" in ci["G226"].value and "分廠商 OpenAI −4.4%、Anthropic −19.4%、Google −2.6%" in ci["G226"].value
    for cell, f_new in (("C226", "Derived"), ("D226:E226", "Derived"), ("C228", "Derived（兩種讀法）"), ("E228", "Derived（兩種讀法）")):
        r = _gm(gm, "Cap_In", cell)
        assert gm[f"F{r}"].value == f_new, cell
        assert "類別＝Assumed" in gm[f"AL{r}"].value and "修訂九" in gm[f"AL{r}"].value and "SL48-0" in gm[f"AL{r}"].value, cell
    r = _gm(gm, "Cap_In", "C226")
    assert "原 −0.25～+0.05" in gm[f"M{r}"].value and "−0.25～+0.05（D 欄＝L 低端 −0.25、E 欄 +0.05）" in gm[f"AL{r}"].value
    assert gm[f"N{r}"].value.startswith("v5.35 J22：中階 token 牌價年變化率 g Assumed −0.10") and "v15.3 E1：2024-05～2026-10" in gm[f"N{r}"].value
    r = _gm(gm, "Cap_In", "C228")
    assert gm[f"N{r}"].value.startswith("v5.35 J22：降級後價值比 ρ Assumed 0.5") and "讀法甲" in gm[f"N{r}"].value and "原低端公式（未乘吞吐倍數）與原高端 1.0" in gm[f"N{r}"].value
    assert "0.05–1.0（D 欄為公式 IF_PriceRef_Luna ÷ IF_PriceRef_Sol、E 欄 1.0）" in gm[f"AL{r}"].value
    r = _gm(gm, "Cap_In", "C227")
    assert gm[f"F{r}"].value == "Assumed" and "v15.3 E3：維持" in gm[f"N{r}"].value and gm[f"N{r}"].value.startswith("v5.35 J22：降級前服務中階的年數 T1 Assumed 4（3–5）")


def test_v1530_d1_three_state(wbf, lo):
    """v16.0：第 242 列與 L1 第 89 列的 L 側改讀 L1_LTotalFleetV（test_v1600 釘住）；本測試改對封存的 v15.3 檔釘住 v15.3 當時的文字與三態規則。"""
    ci = wbf["Cap_In"]
    assert ci["A243"].value.startswith("對照（字面讀法，口徑不一致，不作判讀；見 L1 第 89 列說明）")
    assert ci["C243"].value.startswith("=IF(ISNUMBER(C241),IF(C233>=C241,")        # 公式保留
    pv = openpyxl.load_workbook(V153, data_only=True)
    assert pv["Cap_In"]["C242"].value == "未定（區間重疊；基準 L 0.660 對所需 L 0.756）"
    assert pv["Cap_In"]["D242"].value.startswith("對照：") and pv["Cap_In"]["E242"].value.startswith("對照：")
    assert pv["L1"]["P89"].value.startswith("恆等式讀法：未定（L_total 0.66 對所需 L 0.76）")
    v = lo.view({})
    assert v.get("Cap_In", "D242").startswith("對照：") and v.get("Cap_In", "E242").startswith("對照：")
    pf = openpyxl.load_workbook(V153)
    assert pf["Cap_In"]["C242"].value.count("L1_LTotal_Hi<L1_LReqFleet_Id_Lo") == 1      # v15.3 三態規則（L1_LTotal 區間對 L1_LReqFleet_Id 區間）


def test_v1530_c2_batch_multiple(wbf, lo):
    cal = wbf["Calib"]
    assert cal["D156"].value == "=IF(AND(ISNUMBER(C254),ISNUMBER(D201)),SQRT(C254*D201/$D$67),1)"
    v = lo.view({})
    c254, d201 = v.get("Calib", "C254"), v.get("Calib", "D201")
    assert abs(c254 - 1.59105729779618) < 1e-9 and abs(d201 - 3.03725962564159) < 1e-9
    assert abs(v.get("Calib", "D156") - (c254 * d201 / v.get("Calib", "D67")) ** 0.5) < 1e-12 and abs(v.get("Calib", "D156") - 2.049910728) < 1e-8
    assert _flat(v.get_name("CAL_BatchEtaD"))[0] == 1 and _flat(v.get_name("CAL_BatchEtaD"))[2:] == [1, 0.75, 1]
    gm = wbf["Gov_Map"]
    r = _gm(gm, "Calib", "D156")
    assert gm[f"A{r}"].value == "GM685" and gm[f"K{r}"].value == 1.59 and gm[f"L{r}"].value == 2.64 and gm[f"F{r}"].value == "Derived"
    assert gm[f"M{r}"].value.startswith("1.83–3.04（兩個批次口徑反推點") and "v15.3 C2" in gm[f"M{r}"].value
    assert "原 2.36（＝√(1.83×3.04)）與原區間 1.83–3.04 保留於本說明" in gm[f"N{r}"].value and "v15.3 r1：上端改同口徑（D201 ÷ D67）；原 3.04 保留" in gm[f"N{r}"].value and "v15.3 r1：上端改同口徑（D201 ÷ D67＝3.0373 ÷ 1.15＝2.641，取 2.64）；原 3.04 保留" in gm[f"M{r}"].value and "退回 1" in gm[f"N{r}"].value
    assert "v15.3 C2" in cal["J156"].value and "v15.3 C2" in cal["H156"].value and "v12.0 H2：GB200 D156 由 3.04 改為 2.36" in cal["J156"].value
    # 區間端點：高端情境 1.59 與低端 3.04／3.74 之內含基準
    assert v.get_name("IF_AllocRDGW") >= v.get_name("RNG_IF_AllocRDGW_Lo") and v.get_name("IF_AllocRDGW") <= v.get_name("RNG_IF_AllocRDGW_Hi")
    # Alloc N 節靜態表（含 1.59）
    al = wbf["Alloc"]
    labels = {al.cell(r, 1).value: r for r in range(150, 200) if al.cell(r, 1).value}
    hi = next(r for k, r in labels.items() if str(k).startswith("高端（GB200 1.59"))
    assert al.cell(hi, 3).value == 1.59 and abs(al.cell(hi, 6).value - 0.211628) < 1e-9


def test_v1530_only_expected_names_changed(lo):
    """與封存的 v15.2 逐名稱比較（現行版對封存的 v15.3 取值）：值不同的具名範圍恰好等於 fixtures/v153_changed_names.json（不多不少）。"""
    pw = openpyxl.load_workbook(V152, data_only=True)
    nw = openpyxl.load_workbook(V153, data_only=True)      # v16.0：以封存的 v15.3（LibreOffice 重算存檔）取值
    changed = set()
    for n, d in pw.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text:
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        sh2, rg2 = nw.defined_names[n].attr_text.rsplit("!", 1)
        d1, e1, d2, e2 = range_boundaries(rg2.replace("$", ""))
        got = [nw[sh2.strip("'")].cell(r, c).value for r in range(e1, e2 + 1) for c in range(d1, d2 + 1)]
        if len(want) != len(got) or not all(_same(a, b) for a, b in zip(want, got)):
            changed.add(n)
    assert changed == CHANGED, (sorted(changed - CHANGED)[:20], sorted(CHANGED - changed)[:20])
    assert set(pw.defined_names) == set(nw.defined_names)      # 具名範圍增減 0


def test_v1530_decisions_evidence_readme(wbf):
    d = wbf["Decisions"]
    for i in range(1, 10):
        r = _row(d, f"SL48-0{i}")
        assert d.cell(r, 2).value == "v15.3" and d.cell(r, 7).value == "v15.3 已建" and d.cell(r, 10).value == "否" and "可撤回" in d.cell(r, 6).value
    assert "Assumed" in d.cell(_row(d, "SL48-04"), 4).value and "更正理由" in d.cell(_row(d, "SL48-04"), 4).value
    assert "Assumed" in d.cell(_row(d, "SL48-05"), 4).value and "更正理由" in d.cell(_row(d, "SL48-05"), 4).value
    assert "2.641" in d.cell(_row(d, "SL48-02"), 4).value and "$D$67" in d.cell(_row(d, "SL48-02"), 4).value
    t9 = d.cell(_row(d, "SL48-09"), 4).value      # r1：原文逐字保留
    for old in ("Assumed −0.10；−0.25～+0.05", "g：Assumed（chat 端迴歸；歷史牌價等級 3）", "三者皆 Assumed", "T1、ρ：Assumed（無直接觀測）", "低端以 Luna ÷ Sol 參考請求單價 0.05 為代理", "錨點 基準 L_price 0.7412、L_total 0.6426、L_demote 0.867", "中階 token 牌價年變化率 g（I-1；Assumed）"):
        assert old in t9, old
    assert d.max_row > 300 and _row(d, "SL47-05") == 300      # W4：Decisions 已超過第 300 列，Gov_Map AA 範圍同步放寬
    gm = wbf["Gov_Map"]
    aa = [gm[f"AA{r}"].value for r in range(5, gm.max_row + 1) if isinstance(gm[f"AA{r}"].value, str) and "COUNTIF(Decisions!" in gm[f"AA{r}"].value]
    assert len(aa) >= 680 and all("Decisions!$A$5:$A$1000" in x for x in aa)
    e = wbf["DB_Evidence"]
    ids = [e.cell(r, 1).value for r in range(5, e.max_row + 1)]
    assert ids[ids.index("E393"):ids.index("E393") + 5] == ["E393", "E394", "E395", "E396", "E397"]      # v16.0：其後另有 E398
    assert e.cell(_row(e, "E393"), 9).value == "採用（E1）" and e.cell(_row(e, "E396"), 9).value == "部分採用（E4，只記錄）"
    assert all("可撤回" in e.cell(_row(e, f"E{n}"), 11).value for n in range(393, 398))
    rd = openpyxl.load_workbook(V153, data_only=True)["README"]      # v16.0：封存的 v15.3
    assert str(rd["B5"].value).startswith("20261018_Tokenomics_v15.3（次版：") and "v15.3" in str(rd["A1"].value)


def test_v1530_l1_labels(wbf):
    l1 = wbf["L1"]
    assert l1["H88"].value.startswith("低＝g −0.20、T1 3、ρ 0.17；高＝g +0.05、T1 5、ρ 0.7（同向組合；v15.3 E1／E2，原低端 g −0.25、ρ 0.05，高端 ρ 1.0）")
    assert l1["H86"].value.startswith("低＝g −0.20、高＝g +0.05") and l1["H87"].value.startswith("低＝T1 3、ρ 0.17")


def test_v1530_changed_cells_only_expected():
    """與封存的 v15.2 逐格比對（公式文字或輸入值）：只有預期的頁與格不同。"""
    a, b = openpyxl.load_workbook(V152), openpyxl.load_workbook(V153)      # v16.0：對封存的 v15.3
    diffs = {}
    for ws in a:
        wn = b[ws.title]
        coords = {c.coordinate for r in ws.iter_rows() for c in r if c.value is not None} | {c.coordinate for r in wn.iter_rows() for c in r if c.value is not None}
        d = sorted(x for x in coords if ws[x].value != wn[x].value)
        if d:
            diffs[ws.title] = d
    assert set(diffs) <= {"README", "Calib", "Cap_In", "L1", "Alloc", "Interface", "Gov_Map", "Decisions", "DB_Evidence"}, set(diffs)
    assert diffs["Calib"] == ["D156", "H156", "J156"]
    assert diffs["Cap_In"] == sorted(["A226", "A228", "A230", "A242", "A243", "C226", "C242", "D226", "D228", "D242", "E228", "E242", "F226", "F228", "G226", "G228", "G242", "G243"])
    assert diffs["L1"] == ["C86", "C87", "H86", "H87", "H88", "K86", "K87", "K88", "P89", "S87"]      # r1：過期標籤與 P89 三態
    assert sorted(diffs["README"]) == ["A1", "A60", "B5", "B60"]
    gm = [x for x in diffs["Gov_Map"] if not x.startswith("AA")]
    assert sorted(gm) == sorted(["AL638", "AL639", "AL642", "AL643", "F638", "F639", "F642", "F643", "M638", "M639", "M642", "M643", "N638", "N639", "N640", "N642", "N643",
                                 "K689", "L689", "M689", "N689", "U689", "E638", "E639", "E642", "E643"]), gm
    assert len(diffs["Decisions"]) == 90 and len(diffs["DB_Evidence"]) == 90
    # Interface：只有 R–W 欄（契約追溯文字與公式，D156 公式使上游登錄輸入變多）
    assert {re.match("[A-Z]+", x).group() for x in diffs["Interface"]} <= {"R", "S", "T", "U", "V", "W"}


def test_v1530_r1_labels_and_p89(wbf):
    l1, ci, gm = wbf["L1"], wbf["Cap_In"], wbf["Gov_Map"]
    assert "Derived −0.09；−0.20～+0.05" in l1["C86"].value and "Derived（兩種讀法）0.5；0.17–0.7" in l1["C87"].value
    assert l1["K86"].value.startswith("g：Derived") and l1["K87"].value.startswith("T1：Assumed（E3 維持）；ρ：Derived") and l1["K88"].value == "g、ρ：Derived；T1：Assumed"
    assert "0.05 × 低階模型每 GPU 吞吐倍數 3.41（GB200 欄）＝0.17 為代理" in l1["S87"].value
    assert ci["A226"].value == "中階 token 牌價年變化率 g（I-1；Derived）" and ci["A228"].value.startswith("降級後價值比 ρ（I-3；Derived（兩種讀法）；")
    assert "錨點 基準 L_price 0.7637、L_total 0.6595、L_demote 0.8636" in ci["A230"].value
    for cell, lab in (("C226", ci["A226"].value), ("D226:E226", ci["A226"].value), ("C228", ci["A228"].value), ("E228", ci["A228"].value)):
        assert gm[f"E{_gm(gm, 'Cap_In', cell)}"].value == lab, cell
    assert gm[f"E{_gm(gm, 'Cap_In', 'C227')}"].value.endswith("Assumed）")      # T1 仍是 Assumed（E3 維持）
    assert openpyxl.load_workbook(V153)["L1"]["P89"].value.count('IF(F88<E107,"未回本"') == 2      # v16.0：P89 改讀 L1_LTotalFleetV（test_v1600）；v15.3 的寫法在封存檔

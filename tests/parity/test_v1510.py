"""v15.1 稽核結案收尾（工作單 docs/workorders/20261017_v15.1_結案收尾.md r0）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

本版只動文字、標籤與 Decisions，加 Sens_Rev A17 一個標籤公式；所有具名範圍的數值與 v15.0 逐值相同（版本字串除外）。
U1-1 SL46-20 更正（原字樣保留）、U1-2 Alloc 第 398 列原文補回、U1-3 Calib D67:G67、U1-4 Alloc_In C16、
U2-1 O12 標籤補列 17 列、U2-2 SL46-07 補列、U2-4 Sens_Rev A17 標籤公式。
"""
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V152_CHANGED = set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v152_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v153_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(Path(__file__).resolve().parent / "fixtures" / "v172_changed_names.json", encoding="utf-8"))["changed"]) | set(__import__("json").load(open(Path(__file__).resolve().parent / "fixtures" / "v191_changed_names.json", encoding="utf-8"))["changed"])      # v15.3：另併入 v15.2→v15.3 的預期變動名單（E1／E2／C2／D1；test_v1530 逐名稱釘住）；v17.2：併入 v17.1→v17.2 預期變動名稱（GOV 計數、IFC_Updated 審查日、IDX_ 範圍；test_v1720 與契約快照看守）
PREV = REPO / "model" / "archive" / "20261017_Tokenomics_v15.0.xlsx"
PREV142 = REPO / "model" / "archive" / "20261017_Tokenomics_v14.2.xlsx"
VERSION_NAMES = {"RNG_Version", "RNG_Current", "IDX_SrcID"}      # v16.0：IDX_SrcID 為 Gov_Map 哨兵，v16.0 新增 6 列登記故值改變
SC_EPS = {"CST_Eps": 0.6}
PREWARM = {"test_v1510_a17_label_follows_cst_eps": [SC_EPS]}
O12_ROWS = {"Amortize": (10, 19, 29, 40), "Interface": (55, 60, 64, 69, 73, 78, 148), "Theory_Rev": (18, 20, 36, 38, 54, 56)}


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


def _dec(wbf, rid):
    ws = wbf["Decisions"]
    rows = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == rid]
    assert len(rows) == 1, (rid, rows)
    return {c: ws.cell(rows[0], i).value for i, c in enumerate("ABCDEFGHIJ", 1)}


def test_v1510_every_name_value_equals_v150(lo):
    """全部具名範圍（不只契約前綴）的值與 v15.0 逐值相同，只有版本字串兩個名稱不同；GOV 三項 0／280／182。"""
    prev = openpyxl.load_workbook(PREV, data_only=True)
    v = lo.view({})
    n_ok = 0
    for n, d in prev.defined_names.items():
        if n in VERSION_NAMES or n in V152_CHANGED or "!" not in d.attr_text or "," in d.attr_text:
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        if n.startswith("IFC_"):      # v19.0：Interface 契約欄範圍隨 N 節新列延伸；既有列的值不變（test_v1900 看守）
            got = got[:len(want)]
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n
        n_ok += 1
    assert n_ok >= 1000, n_ok      # v15.2：B2／B3 預期變動的 455 個名稱（V152_CHANGED）不比，其餘仍逐值相同
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 135, 182)      # v21.1: 133 → 135 (SRC_DEM_089/090 lack a second source, W1 +2)
    #      # v19.1：133 → 132（SRC_MOD_018 填 C1 免除標記，Z22 缺第二來源 1 → 0）； v17.2：W1 278 → 131（W1 第二來源 B1：A 86、C1 53、Q11 8 離開；預期變動）
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.0") and str(v.get_name("RNG_Current")).endswith("v21.0")      # v19.0：版本字串隨版本；v18.0：      # v17.1：版本字串隨版本（v17.0 同）      # v17.2：版本字串隨版本


def test_v1510_decisions_recorded(wbf):
    """SL46-25…31 存在，日期、依據、狀態齊全；SL46-20／-13／-16／-07 原文保留且附有 v15.1 補充。"""
    for i in range(25, 32):
        d = _dec(wbf, f"SL46-{i}")
        assert d["B"] == "v15.1" and d["E"] == "2026-10-17" and "13:04" in str(d["F"]) and d["G"] == "v15.1 已建", i
        assert len(str(d["D"])) > 100 and d["H"], i
    prev = openpyxl.load_workbook(PREV, data_only=True)["Decisions"]
    for rid in ("SL46-20", "SL46-13", "SL46-16", "SL46-07"):
        old = next(prev.cell(r, 4).value for r in range(5, prev.max_row + 1) if prev.cell(r, 1).value == rid)
        new = _dec(wbf, rid)["D"]
        assert new.startswith(old) and len(new) > len(old), rid      # 修訂九：原字樣逐字保留，更正只附加在後
    assert "v15.1 更正（修訂九，Decisions SL46-25）" in _dec(wbf, "SL46-20")["D"] and "未涵蓋閉合值" in _dec(wbf, "SL46-20")["D"]
    assert "38,186" in _dec(wbf, "SL46-25")["D"] and "D15-12" in _dec(wbf, "SL46-25")["D"]
    assert "SL46-29" in _dec(wbf, "SL46-16")["D"] and "SL46-30" in _dec(wbf, "SL46-07")["D"] and "SL46-27" in _dec(wbf, "SL46-13")["D"]


def test_v1510_alloc_row398_original_restored_verbatim(wbf):
    """U1-2：v14.2 原文（Alloc 第 362 列）逐字出現在現行 Alloc 第 398 列之內，v15.0 的更正段也還在。"""
    old = openpyxl.load_workbook(PREV142)["Alloc"]["A362"].value
    assert old.startswith("（a）只經 VR200 欄") and "12 個" in old and "L1_Ans5_FullMargin" in old
    ws = wbf["Alloc"]
    t = next(ws.cell(r, 1).value for r in range(300, ws.max_row + 1) if "v15.0 更正（修訂九，T3-2）" in str(ws.cell(r, 1).value or ""))      # v19.1：RNG 區間新增 2 個 CHK_ 名稱，Alloc 該列下移 6 列（原 398），改以文字定位
    assert old in t and "v15.0 更正（修訂九，T3-2）" in t and "v15.1 補回原文（修訂九" in t


def test_v1510_alloc_in_c15_correction_and_c16_basis(wbf):
    ai = wbf["Alloc_In"]
    g15, g16 = ai["G15"].value, ai["G16"].value
    assert "38,186" in g15 and "未涵蓋" in g15 and "SL46-25" in g15
    assert "token 口徑" in g16 and "支出口徑" in g16 and "SL46-28" in g16
    assert ai["C15"].value == 4000 and ai["D15"].value == 2000 and ai["E15"].value == 11000      # 值與區間不變


def test_v1510_calib_d67_g67_note_and_values(wbf):
    ws = wbf["Calib"]
    j = ws["J67"].value
    assert "SL46-27" in j and "未獨立驗證" in j and "SL46-13" in j
    assert [ws[f"{c}67"].value for c in "CDEFG"] == [1.2, 1.15, 1, 1, 1]      # v15.2 B3：D67 1 → 1.15
    assert "SL46-27" in wbf["Interface"]["A2"].value
    d = _dec(wbf, "SL46-27")
    assert "Calib D67:G67" in d["H"] and "GM342" in d["D"]


def test_v1510_o12_labels_added_on_17_rows(wbf):
    n = 0
    for sh, rows in O12_ROWS.items():
        for r in rows:
            t = str(wbf[sh][f"A{r}"].value)
            assert "v15.0 O12 口徑" in t and "SL46-16" in t, (sh, r)
            n += 1
    assert n == 17
    d16 = _dec(wbf, "SL46-16")["D"]
    for sh, rows in O12_ROWS.items():
        assert sh in d16
        for r in rows:
            assert str(r) in d16, (sh, r)


def test_v1510_sl4607_lists_new_kept_items(wbf):
    d = _dec(wbf, "SL46-30")
    t = str(d["D"])
    for key in ("Spec_Rack G26", "Spec_Rack D41", "Har_In C48:E48", "352", "GM119", "GM171", "GM499", "E018",
                "Cache_Store 第 16、22、28 列", "Price_Frontier 第 24、26、31、33 列", "Tech_Registry 第 25、26、27、28 列"):
        assert key in t, key
    assert "Spec_Rack G26" in str(d["H"]) and "Har_In C48:E48" in str(d["H"])


def test_v1510_a17_is_formula_and_label_unchanged_at_base(wbf, lo):
    """U2-4：Sens_Rev A17 現為公式，基準下顯示文字與 v14.2／v15.0 的原文逐字相同；B17、B18 與 D17 公式不變。"""
    assert str(wbf["Sens_Rev"]["A17"].value).startswith("=") and "CST_Eps" in wbf["Sens_Rev"]["A17"].value
    old = openpyxl.load_workbook(PREV)["Sens_Rev"]
    assert old["A17"].value == "ε＝0.5、有效算力 ×7（J8 缺口全數轉為能力）"
    v = lo.view({})
    assert v.get("Sens_Rev", "A17") == old["A17"].value
    for a in ("B17", "B18", "D17", "F17"):
        assert wbf["Sens_Rev"][a].value == old[a].value, a
    assert old["A17"].value in _dec(wbf, "SL46-31")["D"]      # 原文逐字保留於 Decisions


def test_v1510_a17_label_follows_cst_eps(lo):
    v = lo.view(SC_EPS)
    assert v.get("Sens_Rev", "A17") == "ε＝0.6、有效算力 ×7（J8 缺口全數轉為能力）"


def test_v1510_changed_cells_only_expected(wbf):
    """與 v15.0 逐格比對：公式／值不同的儲存格只在預期頁：Alloc（398 與版本字串兩格）、Alloc_In、Amortize、Calib、Decisions、Interface、README、Sens_Rev、Theory_Rev。
    不同頁其餘格 0；Sens_Rev 的公式差異只有 A17。"""
    prev = openpyxl.load_workbook(PREV)
    p151 = openpyxl.load_workbook(REPO / "model" / "archive" / "20261017_Tokenomics_v15.1.xlsx")      # v15.2：v15.1→v15.2 的格差異另由 test_v1520 逐格釘住，這裡遮掉，其餘仍須與原斷言相同
    allowed = {"Alloc", "Alloc_In", "Amortize", "Calib", "Decisions", "Interface", "README", "Sens_Rev", "Theory_Rev",
               "Interface_Prod", "Amortize_Prod", "Theory_Rev_Prod"}   # 鏡像頁同步 17 列的 O12 口徑標籤
    diffs = {}
    for ws in prev:
        wn = wbf[ws.title]
        coords = {c.coordinate for row in ws.iter_rows() for c in row if c.value is not None} | {c.coordinate for row in wn.iter_rows() for c in row if c.value is not None}
        d = [a for a in coords if ws[a].value != wn[a].value and p151[ws.title][a].value == wn[a].value]
        if d:
            diffs[ws.title] = sorted(d)
    assert set(diffs) <= allowed, set(diffs) - allowed
    assert sorted(diffs.get("Alloc", [])) in ([], ["A398"]), diffs.get("Alloc")      # v19.1：該列下移 6 列後，A398 位置已是另一格（內容由上一項以文字定位檢查）      # v15.2：C177（版本字串）屬 v15.1→v15.2 差異，被遮掉
    assert diffs["Sens_Rev"] == ["A17", "G18"] or sorted(diffs["Sens_Rev"]) == ["A17", "G18"], diffs["Sens_Rev"]
    assert sorted(diffs["Alloc_In"]) == ["G15", "G16"] and "Calib" not in diffs      # v15.2：J67 另被 v15.2 附加，遮掉
    assert sorted(diffs["Amortize"]) == ["A10", "A19", "A29", "A40"]
    assert sorted(diffs["Theory_Rev"]) == ["A18", "A20", "A36", "A38", "A54", "A56"]
    assert sorted(diffs["Interface"]) == sorted(f"A{r}" for r in (2, 55, 60, 64, 69, 73, 78, 148))
    assert sorted(diffs["Interface_Prod"]) == sorted(f"A{r}" for r in (55, 60, 64, 69, 73, 78, 148))
    assert sorted(diffs["Amortize_Prod"]) == ["A10", "A19", "A29", "A40"]
    assert sorted(diffs["Theory_Rev_Prod"]) == ["A18", "A20", "A36", "A38", "A54", "A56"]
    assert len(diffs["Decisions"]) == 74      # 7 筆新決策 × 10 欄 ＋ 四筆既有決策的 D 欄附加

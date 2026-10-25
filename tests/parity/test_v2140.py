"""v21.4 專屬測試（工作單 docs/workorders/20261024_v21.4_token帳讀法與過時文字.md r1）。只改文字；讀 LibreOffice 重算後的值。

  1. 全部具名範圍的值與封存 v21.3 相同（容差同 test_v2130），只有 GOV_Warnings（135 → 134）、GOV_Table（內含 D87）、版本字串 RNG_Version／RNG_Current 例外。
  2. W1–W4 各格新文字存在；舊數字「5.62」「65.96」不再單獨出現於列明的格（「5.62」只留在「v20.0 時 5.62」）。
  3. W3：SRC_Price R53＝免…、AE53＝0；Checks D87 133 → 132、D98＝GOV_Warnings 135 → 134；GOV 三項計數 0／134／182。
  4. W5：DB_Evidence E406、Decisions SL61-01、README B5 開頭與新列；Decisions D332 更正。
  5. W6：RNG_StaleFlag 一致、RNG_OutCount 0。
  6. 逐格比較 v21.3 → v21.4：數值差異恰為 SRC_Price!AE53、Checks!D87、Checks!D98；文字／公式差異只落在工作單列明的格與 W5／版本字串。
"""
import re
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path
from v2170_allow import NUM_DIFFS as V2160_NUM      # v21.6：NonNV 持有比的數值差異清單（test_v2160 看守）

REPO = Path(__file__).resolve().parents[2]
V213 = REPO / "model" / "archive" / "20261024_Tokenomics_v21.3.xlsx"
PREWARM = {}

VERSION_NAMES = {"RNG_Version", "RNG_Current"}


def _flat(v):
    if isinstance(v, (list, tuple)):
        return [x for r in v for x in _flat(r)]
    return [v]


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if _num(a) and _num(b):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


def _arch_value(pw, d):
    sh, rg = d.attr_text.rsplit("!", 1)
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    return [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


@pytest.fixture(scope="module")
def pw():
    return openpyxl.load_workbook(V213, data_only=True)


def _row(ws, sid):
    rr = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid]
    assert len(rr) == 1, (sid, rr)
    return rr[0]


# ---------------------------------------------------------------- 1. 具名範圍值不變
def test_v2140_all_names_unchanged(lo, pw, wbf):
    v = lo.view({})
    bad, n = [], 0
    for name, d in wbf.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text or name not in pw.defined_names:
            continue
        want = _arch_value(pw, pw.defined_names[name])
        got = _flat(v.get_name(name))
        n += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
            if name == "GOV_Table":
                pairs = {(a, b) for a, b in zip(want, got) if not _eq(a, b)}
                assert pairs == {(133, 132)}, pairs      # GOV_Table 範圍 Checks A74:D96 內只有 D87（W1 的 WARN 計數）；D98 是 GOV_Warnings 本身
    assert n > 1500, n
    assert sorted(bad) == sorted({"GOV_Warnings", "GOV_Table", "IDX_SrcID", "IF_NonNV_Hold_TPU", "IF_NonNV_Hold_Trn", "IF_NonNV_Out_AMD", "IF_NonNV_Hold_AMD"} | VERSION_NAMES), bad      # v21.6：NonNV 持有比（test_v2160 看守）      # v21.5：哨兵 IDX_SrcID（GM088，test_v2150 看守）
    assert set(wbf.defined_names) == set(pw.defined_names)      # 名稱沒有增減


# ---------------------------------------------------------------- 2. W1–W4 文字
Q_NEW_FRAGS = ("Q 與 GW 路線 token 帳同構（每 GW 產能 × 對外服務 ×（1 − 免費）× 利用率 × 生產折減），折算用 GW 路線：2025 為 L1_TokLedger_GW25（約 1.52）；"
               "2026 Q2 約 2.0–2.1（OpenAI 2026 GW 屬公司層級，數值權威在 company-models OpenAI 模型；Tokenomics PR #164）。"
               "若誤差全在每 GW 產能側，實際營收約為本列 ÷ 2.0–2.1。限制：須各世代誤差一致；GW 數本身的誤差不在 Q 裡。"
               "支出路線 L1_TokLedger_2026Q2（約 3.0）只作對照，不用於折算本列（v21.4）。")


def test_v2140_w1_text(wbf):
    l1 = wbf["L1"]
    for r in range(128, 132):
        t = l1[f"I{r}"].value
        assert t.startswith("v18.0：P × Q 由基本定義計算。") and "(1) Q 是模型產能推算，token 帳未閉合。" + Q_NEW_FRAGS in t, r
        assert "L1_RevGW_Fleet_VR200（v21.3 為 66.35）是理想上限" in t and "65.96" not in t, r
        assert "÷ 3.0" not in t and "v21.1 以前約 6.3" not in t, r      # 舊 (1) 段已換掉
        assert "(2) 回本比較不在本版" in t and "(4) 壽命期年均假設 m 不變" in t and t.count("低／高只動利用率（J4）。") == (1 if r == 128 else 0), r
    assert "｜殘差未分配：GW 優先校準後 2025 供給 ÷ 需求為 L1_TokLedger_GW25；若殘差在利用率，Q 應下修" in l1["I129"].value
    assert l1["I132"].value == ("v18.0：模型付費 token（機隊，成本鏈推出）÷ 需求面付費 token。＞1 表示模型產能推算的 token 多於需求面觀測；舊 L1_MFleet＝m ÷ 本列。不是 m。"
                                " v21.4：支出路線，只作對照；P×Q 的 Q 用 GW 路線 L1_TokLedger_GW25 折算。")
    assert l1["I133"].value == ("v18.0：同 L1_TokLedger，2026 Q2（支出路線）。v21.4：L1_RevGW_PQ_VR200 的 Q 與 GW 路線同構，折算改用 GW 路線（見 L1 I128 (1)）；本列只作對照，不用於折算該列。"
                                "｜原：L1_RevGW_PQ_VR200 的 Q 為模型產能，若誤差全在模型產能側，實際營收約為該列 ÷ 本列。")      # 修訂九：原文逐字保留


def _only_dated_562(t):
    assert "5.62" not in t.replace("v20.0 時 5.62", ""), t


def test_v2140_w2_text(wbf):
    l1, ci = wbf["L1"], wbf["Cap_In"]
    for r in (134, 135):
        t = l1[f"I{r}"].value
        assert "支出路線（AL_ServeGWSpend、L1_TokLedger，v21.3 為 2.652；v20.0 時 5.62）保留為對照。" in t, r
        _only_dated_562(t)
    assert l1["I135"].value.endswith(" 免費切分用支出口徑（Andy 07:34）。")
    t = l1["I136"].value
    assert t == "v20.0：GW 優先後供給 ÷ 需求；支出路線 L1_TokLedger（v21.3 為 2.652；v20.0 時 5.62）保留對照。v21.4：P×Q 的 Q 與本列同構，折算用本列。＞ 1 表示模型供給多於需求面觀測；＜ 1 則相反。不是 m。"
    _only_dated_562(t)
    h = ci["H335"].value
    assert h.startswith("讀法：GW 優先後供給 ÷ 需求。支出路線 L1_TokLedger（v21.3 為 2.652；v20.0 時 5.62）保留對照。需求面 AL_DPaid 無區間，Lo／Hi 都除以同一個基準 AL_DPaid")
    _only_dated_562(h)
    # L1、Cap_In 全頁：「5.62」只剩帶 v20.0 標註的寫法；「65.96」不再出現（README／Decisions 的 v21.4 說明文字會提到這兩個舊數字，不掃）
    for ws in (l1, ci):
        for row in ws.iter_rows():
            for c in row:
                x = c.value
                if isinstance(x, str) and not x.startswith("="):
                    assert "65.96" not in x, (ws.title, c.coordinate)
                    _only_dated_562(x)


def test_v2140_w3_w4_text(lo, wbf):
    sp = wbf["SRC_Price"]
    r49, r50 = _row(sp, "SRC_PRC_049"), _row(sp, "SRC_PRC_050")
    assert (r49, r50) == (53, 54)
    assert sp["V54"].value == "—（未連結模型格；主值為 SRC_PRC_049，v21.3 起）｜原：主值 SRC_PRC_007 不改"
    assert sp["R53"].value == "免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）" == sp["R5"].value      # 比照 SRC_PRC_001
    v = lo.view({})
    assert v.get("SRC_Price", "AE53") == 0
    rm = wbf["README"]
    assert "GPT-6.1 Sol 快取價 0.20 → 0.10（官方頁短上下文；有效牌價混合 1.961 → 1.943，m 同比例 +0.9%，P×Q 營收與 L 的基準不變（_Lo 變體隨機架價低端而變））。" in rm["B73"].value
    b5 = rm["B5"].value
    assert ("L1_RevGW_PQ_VR200*、L1_LReqFleet_Full*、L1_LTotal*、L1_TokLedger* 的基準不變（_Lo 變體中 5 個隨機架價低端而變：L1_LTotal_Lo、L1_LTotalFleetV_Lo、L1_LTotalDisc_Lo、"
            "L1_LTotalFleetVDisc_Lo、L1_RevGW_PQ_VR200_Life_Lo；見 v21.3 預期變動 CSV）。）以下為") in b5
    assert "L1_TokLedger* 不變。）" not in b5
    d = wbf["Decisions"]
    r = _row(d, "SL60-01")
    assert "P×Q 營收、L 的基準不變（_Lo 變體隨機架價低端而變；v21.4 更正）；L 觀測點不登錄（預設，可撤回）。" in d[f"D{r}"].value and "P×Q 營收、L 不變" not in d[f"D{r}"].value


# ---------------------------------------------------------------- 3. GOV
def test_v2140_gov_counts(lo, wbf):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 134, 182)
    assert v.get("Checks", "D98") == 134 and v.get("Checks", "D87") == 132
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.7") and str(v.get_name("RNG_Current")).endswith("v21.7")      # v21.5：版本字串（test_v2150 看守）
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 4. W5 記錄
def test_v2140_records(wbf):
    d = wbf["Decisions"]
    r = _row(d, "SL61-01")
    assert d.cell(r - 1, 1).value == "SL60-01" and d.cell(r, 2).value == "v21.4" and d.cell(r, 7).value == "v21.4 已建"
    txt = d.cell(r, 4).value + d.cell(r, 6).value
    for key in ("L1 I128:I131", "GW 路線", "L1_TokLedger_GW25", "約 2.0–2.1", "65.96", "5.62", "SRC_Price V54", "R53", "GOV_Warnings 135 → 134", "5 個隨機架價低端而變",
                "E406", "弱反對", "SL60-01", "I128:I131", "J2", "J3", "修訂九"):
        assert key in txt, key
    ev = wbf["DB_Evidence"]
    r6 = _row(ev, "E406")
    assert ev.cell(r6 - 1, 1).value == "E405" and ev.cell(r6, 10).value == "v21.4" and ev.cell(r6, 12).value == "已處理"
    t6 = " ".join(str(ev.cell(r6, c).value) for c in range(1, 19))
    for key in ("CoreWeave 2026 Q2 10-Q", "0.76–1.28", "0.95–1.60", "AL_SpendBasis 1.8", "弱反對", "不改", "active power 口徑待 10-K", "Interested-party", "Alloc_In C23",
                "docs/evidence/20261024_CoreWeave10Q_計價錨點/"):
        assert key in t6, key
    al = wbf["Alloc_In"]
    assert (al["C23"].value, al["D23"].value, al["E23"].value) == (1.8, 0.85, 2.3)      # 值不改
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert "以下為 v21.5（次版，底版 v21.4：" in b5 and "v21.4（次版，底版 v21.3：" in b5 and "只改文字；所有契約名稱的值不變；GOV_Warnings 135 → 134（W3）" in b5
    assert "v21.3（次版，底版 v21.2：" in b5 and str(rm["A1"].value).startswith("Tokenomics v21.7")
    rr = [x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v21.4 token 帳讀法與過時文字"]
    assert len(rr) == 1 and rr[0] == 74 and "只改文字，所有契約名稱的值不變" in rm.cell(rr[0], 2).value


# ---------------------------------------------------------------- 6. 逐格比較 v21.3 → 現行（v21.4 的差異＋v21.5 的 W1／W2／W4 格，後者由 test_v2150 另行看守）
EXACT_CELLS = {
    "README": {"A1", "B5", "B73", "A74", "B74", "A75", "B75"}, "Cap_In": {"H335"}, "Alloc": {"C177"}, "Alloc_In": {"G23"}, "Gov_Map": {"H92", "I92", "N92", "R92"},      # v21.5：A75／B75、G23
    "L1": {f"I{r}" for r in range(128, 137)},
    "Decisions": {"D332"} | {f"{c}{r}" for r in (333, 334, 335, 336) for c in "ABCDEFGHIJ"},      # v21.7：SL64-01（第 336 列）；v21.6：SL63-01（第 335 列）
    "DB_Evidence": {f"{c}{r}" for r in (330, 331, 332, 333, 334, 335) for c in "ABCDEFGHIJKLMNOPQR"},      # v21.7：E410／E411（第 334、335 列）；v21.6：E409（第 333 列）
    "NonNV": {"E6", "F6", "G6", "E7", "F7", "G7", "L6", "L7"} | {f"{c}5" for c in "BCDEFG"} | {"L5", "L8", "L9", "A2"},      # v21.6 W1；v21.7 W1／W2
    "Interface": {"A368"},      # v21.7 W2
    "SRC_Price": {"R53", "V54"},
}


def test_v2140_cell_diffs_only_expected():
    a, b = openpyxl.load_workbook(V213), openpyxl.load_workbook(model_path())
    av, bv = openpyxl.load_workbook(V213, data_only=True), openpyxl.load_workbook(model_path(), data_only=True)
    assert a.sheetnames == b.sheetnames
    fd, nd = {}, []
    for ws in a:
        wn, va, vb = b[ws.title], av[ws.title], bv[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    fd.setdefault(ws.title, set()).add(ws.cell(r, c).coordinate)
                p, q = va.cell(r, c).value, vb.cell(r, c).value
                if _num(p) and _num(q) and not _eq(p, q):
                    nd.append((ws.title, ws.cell(r, c).coordinate, p, q))
    assert fd == EXACT_CELLS, {k: sorted(fd.get(k, set()) ^ EXACT_CELLS.get(k, set())) for k in set(fd) | set(EXACT_CELLS) if fd.get(k, set()) != EXACT_CELLS.get(k, set())}
    nd = [t for t in nd if (t[0], t[1]) not in V2160_NUM]      # v21.6：NonNV 持有比的數值差異由 test_v2160 看守
    assert sorted(nd) == [("Checks", "D87", 133, 132), ("Checks", "D98", 135, 134), ("Gov_Map", "AF92", 15, 98), ("Gov_Map", "R92", 7.8, 7.52), ("SRC_Price", "AE53", 1, 0)], nd      # v21.5：加 GM088 連動的 Gov_Map AF92、R92
    # 輸入值（藍字格）與公式文字不變：公式差異格都是文字格（非 "=" 開頭）
    for sh, cells in fd.items():
        for coord in cells:
            x, y = a[sh][coord].value, b[sh][coord].value
            assert sh == "Gov_Map" or (not (isinstance(x, str) and x.startswith("=")) and not (isinstance(y, str) and y.startswith("="))), (sh, coord)      # v21.5：Gov_Map H92／R92 是 builder 連結 SRC 的公式（GM088）

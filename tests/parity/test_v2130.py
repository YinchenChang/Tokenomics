"""v21.3 專屬測試（工作單 docs/workorders/20261024_v21.3_機架價低端與Sol快取價.md r0）。讀 LibreOffice 重算後的值。

  1. 輸入與連結：Spec_Rack F11＝7.5、F13＝9.1（F12 仍 8.4）；Cap_In D7／F47 公式含 SRC_PRC_049；SRC_PRC_049 Active、SRC_PRC_007 Superseded、SRC_PRC_050 仍 Alt；IF_PriceCached_Sol＝0.08。
  2. 第 0 節「不變」名稱（P×Q 營收、L 回本口徑、_Hi 與基準的持有成本與資本支出、token 帳、m 機隊面）對封存 v21.2 差 0。
  3. 值變動名稱集合：恰為工作單預期變動 CSV 的名稱（175 個，扣掉 GOV_Warnings、RNG_OutCount、RNG_StaleFlag、SRC_PRC_007 這四個「中途狀態或記錄本身」名稱），
     另加 W6 區間端點（RNG_*）、版本字串名稱、Cap_In A47 改名連帶的兩個文字名稱（IF_FrontModel_Sol、B4_MktModel），
     以及 SRC_HW 多兩列使 SRC_Index 延伸的四個 IDX_Src* 名稱。
  4. 只有兩個輸入驅動：F11 改回 7.8、SRC_PRC_049 值改回 0.2，CSV 名稱回到 v21.2 的值。
  5. W1–W5 文字與記錄；Decisions SL60-01、DB_Evidence E404／E405、README。
  6. W6：區間時效指紋、RNG_StaleFlag＝一致、RNG_OutCount＝0、GOV 三項計數 0／135／182。
  7. 公式文字逐格差異只落在工作單列明的格（含 SRC 頁新增列連帶的 SRC_Index 重排與 Checks D86 範圍）。
"""
import csv
import re
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V212 = REPO / "model" / "archive" / "20261023_Tokenomics_v21.2.xlsx"
CSV = REPO / "docs" / "workorders" / "20261024_v21.3_預期變動.csv"
REVERT = {"Spec_Rack!F11": 7.8, "SRC_Price!C53": 0.2}
PREWARM = {"test_v2130_only_two_inputs_drive": [REVERT]}


def _csv_names():
    out = set()
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        for n in (r["names"] or "").split(";"):
            if n.strip():
                out.add(n.strip())
    return out


CSV_NAMES = _csv_names()
INTERIM = {"GOV_Warnings", "RNG_OutCount", "RNG_StaleFlag", "SRC_PRC_007"}      # 預期變動 CSV 是中途狀態（指紋未重產、SRC_PRC_007 值被改）；最終值回到 v21.2
CHANGED = CSV_NAMES - INTERIM
LABEL_NAMES = {"IF_FrontModel_Sol", "B4_MktModel"}      # Cap_In A47 GPT-6 Sol -> GPT-6.1 Sol 連帶（文字值）
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
INDEX_NAMES = {"IDX_SrcID", "IDX_SrcStat", "IDX_SrcGrade", "IDX_SrcDate"}      # SRC_Index 因 SRC_HW 多兩列而延伸（範圍 A5:A1586 → A5:A1588）
assert len(CSV_NAMES) == 175 and len(CHANGED) == 171

# 第 0 節「不變」：前綴（含 _Lo／_Hi）與全名
KEEP_PREFIX = ("L1_RevGW_PQ_VR200", "L1_LReqFleet_Full", "L1_LTotal", "L1_TokLedger", "L1_MFleet", "L1_M_2025", "L1_PriceReqBE", "L1_LDiscGen")
KEEP_EXACT = {"L1_HoldEconGW_VR200", "L1_HoldEconGW_VR200_Hi", "L1_CapexGW_VR200", "L1_CapexGW_VR200_Hi"}


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
    return openpyxl.load_workbook(V212, data_only=True)


def _row(ws, sid):
    rr = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid]
    assert len(rr) == 1, (sid, rr)
    return rr[0]


# ---------------------------------------------------------------- 1. 輸入、連結、狀態
def test_v2130_inputs_links_status(lo, wbf):
    sp = wbf["Spec_Rack"]
    assert sp["A11"].value == "機架價格 低（$M）"
    assert sp["F11"].value == 7.5 and sp["F13"].value == 9.1 and sp["F12"].value == 8.4
    ci = wbf["Cap_In"]
    assert ci["D7"].value == "=SRC_PRC_049" and ci["F47"].value == "=SRC_PRC_049"
    assert ci["C7"].value == "=SRC_PRC_004" and ci["E7"].value == "=SRC_PRC_010"      # Luna／Astra 快取價不變
    price = wbf["SRC_Price"]
    r49, r07, r50 = _row(price, "SRC_PRC_049"), _row(price, "SRC_PRC_007"), _row(price, "SRC_PRC_050")
    assert price[f"O{r49}"].value == "Active" and price[f"O{r07}"].value == "Superseded" and price[f"O{r50}"].value == "Alt"
    assert price[f"P{r07}"].value == "SRC_PRC_049" and price[f"C{r49}"].value == 0.1 and price[f"C{r07}"].value == 0.2 and price[f"C{r50}"].value == 0.2
    assert price[f"Q{r49}"].value == "E405"
    v = lo.view({})
    assert v.get("Spec_Rack", "F11") == 7.5 and v.get("Spec_Rack", "F13") == 9.1
    assert v.get("Cap_In", "D7") == 0.1 and v.get("Cap_In", "F47") == 0.1
    assert v.get_name("IF_PriceCached_Sol") == pytest.approx(0.08, abs=1e-12)
    assert _flat(v.get_name("IF_RackPrice"))[0] == 7.5 or 7.5 in _flat(v.get_name("IF_RackPrice"))
    # 新 SRC 紀錄
    hw = wbf["SRC_HW"]
    r98, r99 = _row(hw, "SRC_HW_098"), _row(hw, "SRC_HW_099")
    assert (r98, r99) == (102, 103) and hw[f"A{r98 - 1}"].value == "SRC_HW_097"
    assert hw[f"C{r98}"].value == 7.52 and hw[f"F{r98}"].value == "$M/架" and hw[f"K{r98}"].value == 2 and hw[f"L{r98}"].value == "中立"
    assert hw[f"N{r98}"].value == "二手" and hw[f"O{r98}"].value == "Active" and hw[f"V{r98}"].value == "Spec_Rack!F11｜取整（7.52 → 7.5）"
    assert "remio.ai/post/bernstein-ai-data-center-costs-hit-39-5-billion-per-gw" in hw[f"J{r98}"].value and "2026-10-10" in hw[f"J{r98}"].value
    assert "每 GW 金額只作對照、不驅動" in hw[f"W{r98}"].value and "SRC_HW_017" in hw[f"W{r98}"].value
    assert hw[f"O{r99}"].value == "Alt" and hw[f"K{r99}"].value == 2 and hw[f"L{r99}"].value == "中立" and hw[f"N{r99}"].value == "二手"
    assert "247wallst.com/investing/2026/07/15/morgan-stanley" in hw[f"J{r99}"].value
    assert "49" in hw[f"G{r99}"].value and "39" in hw[f"G{r99}"].value and "35" in hw[f"G{r99}"].value
    assert "50.26／44.91／36.69" in hw[f"W{r99}"].value
    assert str(hw[f"V{r99}"].value).startswith("—")      # 不連結模型格
    assert wbf.defined_names["SRC_HW_098"].attr_text == f"SRC_HW!$C${r98}"


# ---------------------------------------------------------------- 2. 第 0 節「不變」名稱
# 工作單第 0 節以前綴（L1_LTotal*、L1_MFleet 系列等）描述「不變」，但預期變動 CSV（chat 端實測）顯示下列 12 個名稱隨低端／情境欄變動
# （皆為 _Lo、_Hi 或情境變體；基準名稱不變）。以 CSV 為準，並在報告「待 Project 判斷」註明文字與 CSV 的出入。
KEEP_BUT_CHANGED = {"L1_CapexGW_VR200_Lo", "L1_HoldEconGW_VR200_Lo", "L1_LTotalDisc_Lo", "L1_LTotalFleetVDisc_Lo", "L1_LTotalFleetV_Lo", "L1_LTotal_Lo",
                    "L1_MFleet_Px2026", "L1_MFleet_Px2026_Hi", "L1_MFleet_Px2026_Lo", "L1_MFleet_Ser", "L1_PriceReqBE_Hi", "L1_RevGW_PQ_VR200_Life_Lo"}


def test_v2130_unchanged_names(lo, pw, wbf):
    v = lo.view({})
    n_keep, bad, hit = 0, [], set()
    for name, d in wbf.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text:
            continue
        if not (name.startswith(KEEP_PREFIX) or name in KEEP_EXACT):
            continue
        if name in CHANGED:
            hit.add(name)
            continue
        assert name in pw.defined_names, name
        want = _arch_value(pw, pw.defined_names[name])
        got = _flat(v.get_name(name))
        n_keep += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
    assert n_keep > 40
    expect = KEEP_BUT_CHANGED - {"L1_CapexGW_VR200_Lo", "L1_HoldEconGW_VR200_Lo"}      # 這兩個不在 KEEP_EXACT 掃描範圍（下方另行點名）
    assert hit == expect, (sorted(hit - expect), sorted(expect - hit))
    assert bad == [], bad[:20]
    # 點名（第 0 節）：基準名稱不變；L1_HoldEconGW_VR200、L1_CapexGW_VR200 的基準與 _Hi 不變，只有 _Lo 變
    for nm in ("L1_RevGW_PQ_VR200", "L1_RevGW_PQ_VR200_FY", "L1_RevGW_PQ_VR200_Life", "L1_LReqFleet_Full", "L1_LReqFleet_Full_Lo", "L1_LReqFleet_Full_Hi", "L1_LTotal",
               "L1_LDiscGen", "L1_HoldEconGW_VR200", "L1_HoldEconGW_VR200_Hi", "L1_CapexGW_VR200", "L1_CapexGW_VR200_Hi", "L1_TokLedger", "L1_TokLedger_2026Q2",
               "L1_MFleet", "L1_M_2025", "L1_PriceReqBE"):
        assert nm in wbf.defined_names and nm not in CHANGED, nm
    for nm in ("L1_HoldEconGW_VR200_Lo", "L1_CapexGW_VR200_Lo"):
        assert nm in CHANGED, nm


# ---------------------------------------------------------------- 3. 變動名稱集合與主要新值
KEY_VALUES = {      # 名稱 -> (v21.2, v21.3)；工作單第 0 節「主要變動（以重算值為準）」
    "L1_M": (1.3432, 1.3554), "L1_PxEff_2026": (1.9607, 1.9431), "IF_PxEffMix": (1.9607, 1.9431), "AL_PriceFleet": (1.9607, 1.9431),
    "IF_PriceCached_Sol": (0.16, 0.08), "IF_PriceRef_Sol": (1.6071, 1.568),
    "L1_HoldEconGW_VR200_Lo": (9.512, 9.219), "L1_CapexGW_VR200_Lo": (43.49, 42.21),
}


@pytest.mark.parametrize("nm", sorted(KEY_VALUES))
def test_v2130_key_values(lo, pw, wbf, nm):
    old, new = KEY_VALUES[nm]
    v = lo.view({})
    got = _flat(v.get_name(nm))[0]
    assert got == pytest.approx(new, rel=1e-3), nm
    was = _flat(_arch_value(pw, pw.defined_names[nm]))[0]
    assert was == pytest.approx(old, rel=1e-3), nm


def test_v2130_changed_set_is_exactly_expected(lo, pw, wbf):
    v = lo.view({})
    changed = set()
    for name, d in wbf.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text:
            continue
        if name not in pw.defined_names:
            continue
        want = _arch_value(pw, pw.defined_names[name])
        got = _flat(v.get_name(name))
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            changed.add(name)
    rng = {n for n in changed if n.startswith("RNG_")}
    other = changed - rng
    V214 = {"GOV_Warnings", "GOV_Table", "IF_NonNV_Hold_TPU", "IF_NonNV_Hold_Trn", "IF_NonNV_Out_AMD", "IF_NonNV_Hold_AMD"}      # v21.6：NonNV 持有比 TPU／Trn（test_v2160 看守）
    V214 |= set()      # v21.4 W3：SRC_PRC_049 第二來源「免」使 GOV_Warnings 135 → 134、GOV_Table 內的 D87（W1 WARN 計數）133 → 132（test_v2140 看守）
    assert other == CHANGED | LABEL_NAMES | INDEX_NAMES | V214, (sorted(other - CHANGED - LABEL_NAMES - INDEX_NAMES - V214), sorted((CHANGED | LABEL_NAMES | INDEX_NAMES | V214) - other))
    assert VERSION_NAMES <= rng
    assert str(v.get_name("RNG_Version")).endswith("v21.7") and str(v.get_name("RNG_Current")).endswith("v21.7")      # v21.4：版本字串（原 v21.3）
    assert v.get_name("IF_FrontModel_Sol") == "GPT-6.1 Sol"
    # 名稱沒有增減（SRC_ID 名稱除外：SRC_HW_098／099 與 099 的 _Lo／_Hi）
    new_names = set(wbf.defined_names) - set(pw.defined_names)
    assert new_names == {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi"}, sorted(new_names)
    assert set(pw.defined_names) - set(wbf.defined_names) == set()


# ---------------------------------------------------------------- 4. 只有兩個輸入驅動
def test_v2130_only_two_inputs_drive(lo, pw, wbf):
    h = lo.view(REVERT)
    for nm in sorted(CHANGED):
        want = _arch_value(pw, pw.defined_names[nm])
        got = _flat(h.get_name(nm))
        assert len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got)), nm
    errs = [(s, c) for (s, c), x in h.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 5. 文字與記錄
G23_OLD_TAIL = ("經濟口徑：依據的價格 ÷ 會計成本 1.16 × 會計 ÷ 經濟持有成本 0.73 ≈ 0.85（區間 0.73–1.17）；分母維持經濟口徑持有成本。"
                "小於 1 表示 Azure 計價未涵蓋全部資本成本，這本身是 m 的一項實質命題（決定紀錄 D10）")


def test_v2130_text_w1_to_w5(wbf):
    hw = wbf["SRC_HW"]
    r17, r16, r15 = _row(hw, "SRC_HW_017"), _row(hw, "SRC_HW_016"), _row(hw, "SRC_HW_015")
    w17 = hw[f"W{r17}"].value
    assert w17.startswith("v21.3：原出處 Bernstein 已於 2026-10 下修至 7.52（SRC_HW_098），高端 9.1 保留作上緣（Andy 2026-10-24 決定）｜模型取 9.1；與 MS 同口徑")
    assert hw[f"V{r16}"].value == "—（v21.3 起 F11 來源為 SRC_HW_098；原：Spec_Rack!F11｜直接）"
    assert hw[f"V{r15}"].value == "Spec_Rack!F12｜直接" and hw[f"O{r16}"].value == "Alt"
    price = wbf["SRC_Price"]
    r49, r07 = _row(price, "SRC_PRC_049"), _row(price, "SRC_PRC_007")
    assert price[f"V{r49}"].value == "Cap_In!D7｜直接；Cap_In!F47｜直接"
    assert price[f"W{r49}"].value.startswith("v21.3：Andy 2026-10-24 決定採官方頁短上下文 0.10 為主值（C&W 證據送件 #6；官方頁 2026-10-24 再讀仍為 0.10）｜v17.2 W1 B1 Q3：")
    assert price[f"V{r07}"].value == "—（v21.3 起由 SRC_PRC_049 取代；原：Cap_In!D7｜直接；Cap_In!F47｜直接）"
    assert price[f"B{r07}"].value == "GPT-6 Sol 快取輸入" and price[f"H{r07}"].value == "GPT-6 Sol"      # 已 Superseded，不改名
    for sid, lab in (("SRC_PRC_006", "GPT-6.1 Sol 新鮮輸入"), ("SRC_PRC_008", "GPT-6.1 Sol 輸出（含思考）")):
        r = _row(price, sid)
        assert price[f"B{r}"].value == lab and price[f"H{r}"].value == "GPT-6.1 Sol"
        assert price[f"W{r}"].value.startswith("v21.3 改名（原：GPT-6 Sol；值不變）｜—｜v17.2 Q3：")
    ci = wbf["Cap_In"]
    assert ci["A47"].value == "GPT-6.1 Sol"
    assert ci["G7"].value == "v21.3：Sol 快取＝0.10（官方頁短上下文，輸入價 5%；SRC_PRC_049）｜原：＝輸入價 10%（S50）"
    # W3：G23 前綴、原文逐字在後；C23:E23／F23 不改
    ai = wbf["Alloc_In"]
    g = ai["G23"].value
    assert g.startswith("v21.5：") and "｜v21.3（2026-10-24 Azure 實付價 A 段 J3，PR #159；Andy 14:50「同意用預設建議」）：獨立價格錨點約 4 組，重心 1.0–1.5；" in g      # v21.5：G23 前面再加 v21.5 段（test_v2150 看守）
    assert "2024 A100 $1.30／小時（原文 per server，採每顆為推論，單位未證實）約 1.31 倍" in g
    assert "1.8 為跨供應商混合殘差，未被推翻，維持基準 1.8、區間 0.85–2.3。｜v21.2（2026-10-23 9a 查證 J5" in g
    assert g.endswith("｜原說明（v21.1 以前）：" + G23_OLD_TAIL)
    assert (ai["C23"].value, ai["D23"].value, ai["E23"].value, ai["F23"].value) == (1.8, 0.85, 2.3, "Derived")
    # W5：L1 I128:I131
    l1 = wbf["L1"]
    for r in range(128, 132):
        t = l1[f"I{r}"].value
        assert "6.26" not in t, r      # v21.4：第 (1) 段改寫為 GW 路線（「L1_TokLedger_2026Q2 倍（約 3.0；v21.1 以前約 6.3）」與「÷ 3.0」不再存在；test_v2140 看守）
        assert "(2) 回本比較不在本版" in t       # 其餘文字不動
    for r in range(1, l1.max_row + 1):
        for c in range(1, l1.max_column + 1):
            x = l1.cell(r, c).value
            assert not (isinstance(x, str) and "6.26" in x), (r, c)


def test_v2130_records(wbf):
    d = wbf["Decisions"]
    rows = [r for r in range(5, d.max_row + 1) if d.cell(r, 1).value == "SL60-01"]
    assert len(rows) == 1 and d.cell(rows[0] - 1, 1).value == "SL59-01"
    assert d.cell(rows[0], 2).value == "v21.3" and d.cell(rows[0], 7).value == "v21.3 已建"
    txt = d.cell(rows[0], 4).value + d.cell(rows[0], 6).value
    for key in ("F11 7.8 → 7.5", "SRC_HW_098", "SRC_HW_099", "SRC_PRC_049", "Superseded", "GPT-6.1 Sol", "G23", "E404", "E405", "約 6.26", "修訂九", "原值逐字保留".replace("原值逐字保留", "原文逐字保留"),
                "同意用預設建議", "L 觀測點不登錄"):
        assert key in txt, key
    ev = wbf["DB_Evidence"]
    e4 = [r for r in range(5, ev.max_row + 1) if ev.cell(r, 1).value == "E404"]
    e5 = [r for r in range(5, ev.max_row + 1) if ev.cell(r, 1).value == "E405"]
    assert len(e4) == 1 and len(e5) == 1 and ev.cell(e4[0] - 1, 1).value == "E403" and e5[0] == e4[0] + 1
    t4 = " ".join(str(ev.cell(e4[0], c).value) for c in range(1, 19))
    assert "A100 $1.30／小時" in t4 and "弱反對 AL_SpendBasis 1.8" in t4 and "per server 或 per GPU 均未證實" in t4 and "2.2（1.9–2.6）" in t4 and "20261024_Azure實付價_A段" in t4
    t5 = " ".join(str(ev.cell(e5[0], c).value) for c in range(1, 19))
    for key in ("SRC_HW_098", "SRC_HW_099", "47.6", "50.26", "47.58", "鴻海董事長 47", "SRC_PRC_049", "L 觀測點不登錄"):
        assert key in t5, key
    rm = wbf["README"]
    assert "以下為 v21.5（次版，底版 v21.4：" in str(rm["B5"].value) and "v21.4（次版，底版 v21.3：" in str(rm["B5"].value) and "v21.3（次版，底版 v21.2：" in str(rm["B5"].value) and "v21.2（次版，底版 v21.1：" in str(rm["B5"].value)      # v21.4：版本字串（原 v21.3）
    assert str(rm["A1"].value).startswith("Tokenomics v21.7")
    rr = [x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v21.3 機架價低端 7.5 與 Sol 快取價 0.10"]
    assert len(rr) == 1 and "7.5" in rm.cell(rr[0], 2).value


# ---------------------------------------------------------------- 6. W6：指紋、區間、GOV
def test_v2130_fingerprint_ranges_and_gov(lo, wbf):
    v = lo.view({})
    assert v.get_name("RNG_StaleFlag") == "一致"
    assert v.get_name("RNG_OutCount") == 0
    assert v.get("Alloc", "C410") == 0
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 134, 182)      # v21.4：W3 SRC_PRC_049 第二來源「免」，135 → 134（test_v2140 看守）
    # 指紋記錄值（Alloc P 節：A＝頁、B＝格、D＝記錄值）：F11 與 SRC_PRC_049 為葉格；SRC_PRC_007（C11）不再是葉格
    al = wbf["Alloc"]
    rec = {(al.cell(r, 1).value, al.cell(r, 2).value): al.cell(r, 4).value for r in range(400, 1300) if al.cell(r, 1).value}
    assert rec[("Spec_Rack", "F11")] == 7.5 and rec[("SRC_Price", "C53")] == 0.1 and ("SRC_Price", "C11") not in rec
    assert (rec[("Alloc_In", "C23")], rec[("Alloc_In", "D23")], rec[("Alloc_In", "E23")]) == (1.8, 0.85, 2.3)
    # 檔案層級的指紋與端點檔對現行活頁簿一致由 tools/gen_fingerprint.py --check、tools/gen_ranges.py --check 驗證（見報告）


# ---------------------------------------------------------------- 7. 公式文字逐格差異
def test_v2130_diffs_only_expected_vs_v212():
    a, b = openpyxl.load_workbook(V212), openpyxl.load_workbook(model_path())
    assert a.sheetnames == b.sheetnames
    d = {}
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    d.setdefault(ws.title, []).append((ws.cell(r, c).coordinate, x, y))
    got = {k: sorted(t[0] for t in v) for k, v in d.items()}
    row = lambda coord: int(re.sub(r"[A-Z]+", "", coord))
    col = lambda coord: re.sub(r"\d+", "", coord)
    exact = {
        "README": ["A1", "A73", "B5", "B73", "A74", "B74", "A75", "B75"],      # v21.4：B73 更正、第 74 列新增；v21.5：第 75 列新增
        "Spec_Rack": ["F11"],
        "Cap_In": ["A47", "D7", "F47", "G7", "H335"],      # v21.4 W2：H335
        "Alloc_In": ["G23"],
        "L1": [f"I{r}" for r in range(128, 137)],      # v21.4 W1／W2：I128:I136
        "Checks": ["D86"],
        "Decisions": sorted(f"{c}{r}" for r in (332, 333, 334, 335, 336) for c in "ABCDEFGHIJ"),      # v21.7：SL64-01（第 336 列）；v21.6：SL63-01（第 335 列）      # v21.4：D332 更正、SL61-01（第 333 列）；v21.5：SL62-01（第 334 列）
        "DB_Evidence": sorted(f"{c}{r}" for r in (328, 329, 330, 331, 332, 333, 334, 335) for c in "ABCDEFGHIJKLMNOPQR"),      # v21.7：E410／E411（第 334、335 列）；v21.6：E409（第 333 列）
        "NonNV": sorted(["E6", "E7", "F6", "F7", "G6", "G7", "L6", "L7", "B5", "C5", "D5", "E5", "F5", "G5", "L5", "L8", "L9", "A2"]),      # v21.7 W1／W2（test_v2170 看守）
        "Interface": ["A368"],      # v21.7 W2（test_v2170 看守）
             # v21.6 W1（test_v2160 看守）      # v21.4：E406（第 330 列）；v21.5：E407／E408（第 331、332 列）
        "SRC_Price": sorted(["B10", "H10", "W10", "B12", "H12", "W12", "O11", "P11", "V11", "O53", "Q53", "V53", "W53", "R53", "V54"]),      # v21.4 W3：R53、V54
    }
    for sh, want in exact.items():
        assert got.get(sh) == sorted(want), (sh, sorted(set(got.get(sh, [])) ^ set(want)))
    # SRC_HW：新增兩列（第 102、103 列 A:Z、AH）、X 欄範圍（$AH$5:$AH$151 → $AH$153）、V20、W21
    hw = got["SRC_HW"]
    assert all((row(x) in (102, 103)) or (col(x) == "X" and 5 <= row(x) <= 101) or x in ("V20", "W21") for x in hw), [x for x in hw if not ((row(x) in (102, 103)) or (col(x) == "X") or x in ("V20", "W21"))]
    assert {"V20", "W21"} <= set(hw)
    for t in d["SRC_HW"]:
        if col(t[0]) == "X" and row(t[0]) <= 101:
            assert t[1].replace("$AH$151", "$AH$153") == t[2], t
    # SRC_Index：只因 SRC_HW 多兩列而重排（A:F 欄，第 102 列起）
    assert all(col(x) in "ABCDEF" and row(x) >= 102 for x in got["SRC_Index"])
    # Alloc：版本字串 C177、區間端點常數（數字對數字）、指紋記錄列（第 1233–1237 列的連結位址）
    for t in d["Alloc"]:
        coord, x, y = t
        assert coord == "C177" or (_num(x) and _num(y)) or 1230 <= row(coord) <= 1240, t
    assert "C177" in got["Alloc"]

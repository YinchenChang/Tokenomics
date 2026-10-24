# v21.4 (work order docs/workorders/20261024_v21.4_token帳讀法與過時文字.md r1, branch claude/v21-4): TEXT ONLY.
# MINOR version: no input value, formula or contract name changes; every contract name keeps its value. Only two SRC_Price cells change what a Checks formula counts:
# SRC_Price R53 (second source of SRC_PRC_049) "—" -> "免（…）" => SRC_Price!AE53 1 -> 0, Checks D87 133 -> 132, Checks D98 (= GOV_Warnings) 135 -> 134.
#   W1  L1 I128:I131 (1) the token-ledger conversion moves to the GW route (2025: L1_TokLedger_GW25 about 1.52; 2026 Q2 about 2.0-2.1, authority in company-models OpenAI),
#       (3) "65.96" -> "v21.3 為 66.35"; I132 tail; I133 rewritten (original kept after "｜原：", CLAUDE.md revision 9).
#   W2  stale "5.62": L1 I134／I135／I136, Cap_In H335 ("v21.3 為 2.652；v20.0 時 5.62").
#   W3  SRC_Price V54 (SRC_PRC_050 model-use text, original kept), R53 (second source "免…", same wording as SRC_PRC_001).
#   W4  "unchanged" scope: README B5 (v21.3 paragraph), README B73, Decisions D332 (SL60-01): the base is unchanged, the _Lo variants move with the rack price low end.
#   W5  DB_Evidence E406 (CoreWeave 2026 Q2 10-Q lessor pricing anchor, weak opposition to AL_SpendBasis 1.8; value not changed), Decisions SL61-01, README B5 opening paragraph.
#   W6  (outside this file) tools/gen_fingerprint.py and tools/gen_ranges.py re-run, contract snapshot, builder md.
# L1 and Cap_In H335 are rebuilt by the builder on every run, so their v21.3 text is the "old" text here; README rows are built from the v21.3 constants with the exact
# substrings replaced (asserted); Excel-owned cells (SRC_Price, Decisions, DB_Evidence) are written only while they still hold the old text. Idempotent.
from openpyxl.utils import get_column_letter as L

from common import put, F_CALC
import v1410
import v2130

VERSION = "20261024_Tokenomics_v21.4"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-24"
DASH = "—"
V = "v21.4"
WO = "工作單 docs/workorders/20261024_v21.4_token帳讀法與過時文字.md（r1）"
DEC_ID = "SL61-01"
EID = "E406"
EVD_CW = "docs/evidence/20261024_CoreWeave10Q_計價錨點/"
DEC_BY = ("Andy 未回應，照工作單預設：PR #164（token 帳缺口 A 段）J1（L1 第 128–133 列讀法改引 GW 路線）、J3（對外折算改 ÷2.0–2.1）；"
          "PR #163（CoreWeave 10-Q 計價錨點）J1（AL_SpendBasis 1.8 不改，DB_Evidence 記一筆弱反對）；J2（不新增 GW 路線折算後的營收名稱）、J3（SRC_HW_099 不拆）；"
          "v21.3 報告第 4 節（過時文字）與第 6 節 P1、P9；v21.3 獨立核對補充")

# ---------------------------------------------------------------- W1 / W2 text (old -> new; each old text must occur exactly as often as expected)
Q_OLD = '(1) Q 是模型產能推算，token 帳未閉合：2026 Q2 模型付費 token 為需求面的 L1_TokLedger_2026Q2 倍（約 3.0；v21.1 以前約 6.3）；若誤差全在模型產能側，實際營收約為本列 ÷ 3.0。'
Q_NEW = '(1) Q 是模型產能推算，token 帳未閉合。Q 與 GW 路線 token 帳同構（每 GW 產能 × 對外服務 ×（1 − 免費）× 利用率 × 生產折減），折算用 GW 路線：2025 為 L1_TokLedger_GW25（約 1.52）；2026 Q2 約 2.0–2.1（OpenAI 2026 GW 屬公司層級，數值權威在 company-models OpenAI 模型；Tokenomics PR #164）。若誤差全在每 GW 產能側，實際營收約為本列 ÷ 2.0–2.1。限制：須各世代誤差一致；GW 數本身的誤差不在 Q 裡。支出路線 L1_TokLedger_2026Q2（約 3.0）只作對照，不用於折算本列（v21.4）。'
P_OLD, P_NEW = "L1_RevGW_Fleet_VR200（65.96）", "L1_RevGW_Fleet_VR200（v21.3 為 66.35）"
I132_TAIL = " v21.4：支出路線，只作對照；P×Q 的 Q 用 GW 路線 L1_TokLedger_GW25 折算。"
I133_OLD = "v18.0：同 L1_TokLedger，2026 Q2。L1_RevGW_PQ_VR200 的 Q 為模型產能，若誤差全在模型產能側，實際營收約為該列 ÷ 本列。"
I133_ORIG = "L1_RevGW_PQ_VR200 的 Q 為模型產能，若誤差全在模型產能側，實際營收約為該列 ÷ 本列。"
I133_NEW = ("v18.0：同 L1_TokLedger，2026 Q2（支出路線）。v21.4：L1_RevGW_PQ_VR200 的 Q 與 GW 路線同構，折算改用 GW 路線（見 L1 I128 (1)）；本列只作對照，不用於折算該列。"
            "｜原：" + I133_ORIG)
S_OLD, S_NEW = "L1_TokLedger 5.62）保留為對照。", "L1_TokLedger，v21.3 為 2.652；v20.0 時 5.62）保留為對照。"                    # L1 I134／I135
I136_OLD = "舊 L1_TokLedger（5.62）為支出路線，保留對照。＞ 1 表示"
I136_NEW = "支出路線 L1_TokLedger（v21.3 為 2.652；v20.0 時 5.62）保留對照。v21.4：P×Q 的 Q 與本列同構，折算用本列。＞ 1 表示"
H335_OLD = "讀法：GW 優先後供給 ÷ 需求。舊 L1_TokLedger（5.62）為支出路線，保留對照。需求面"
H335_NEW = "讀法：GW 優先後供給 ÷ 需求。支出路線 L1_TokLedger（v21.3 為 2.652；v20.0 時 5.62）保留對照。需求面"

# ---------------------------------------------------------------- W3 text
V54_OLD = "—（未連結模型格；主值 SRC_PRC_007 不改）"
V54_NEW = "—（未連結模型格；主值為 SRC_PRC_049，v21.3 起）｜原：主值 SRC_PRC_007 不改"
R53_OLD = DASH
R53_NEW = "免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）"

# ---------------------------------------------------------------- W4 text
B73_OLD, B73_NEW = "P×Q 營收與 L 不變）", "P×Q 營收與 L 的基準不變（_Lo 變體隨機架價低端而變））"
B5_OLD = "L1_RevGW_PQ_VR200*、L1_LReqFleet_Full*、L1_LTotal*、L1_TokLedger* 不變。）以下為"
B5_NEW = ("L1_RevGW_PQ_VR200*、L1_LReqFleet_Full*、L1_LTotal*、L1_TokLedger* 的基準不變（_Lo 變體中 5 個隨機架價低端而變：L1_LTotal_Lo、L1_LTotalFleetV_Lo、"
          "L1_LTotalDisc_Lo、L1_LTotalFleetVDisc_Lo、L1_RevGW_PQ_VR200_Life_Lo；見 v21.3 預期變動 CSV）。）以下為")
D332_OLD, D332_NEW = "P×Q 營收、L 不變；L 觀測點不登錄", "P×Q 營收、L 的基準不變（_Lo 變體隨機架價低端而變；v21.4 更正）；L 觀測點不登錄"


def _find(ws, sid, col=1):
    rr = [r for r in range(5, ws.max_row + 1) if ws.cell(r, col).value == sid]
    assert len(rr) == 1, (sid, rr)
    return rr[0]


def _sub(cur, old, new, cell, count=1):
    """replace old by new (old must occur `count` times); already-applied text is returned unchanged"""
    if new in cur and old not in cur:
        return cur, 0
    assert cur.count(old) == count, (cell, cur.count(old))
    return cur.replace(old, new), 1


def _set(ws, ref, old, new):
    cur = ws[ref].value
    if cur == new:
        return 0
    assert cur == old, (ws.title, ref, cur)
    ws[ref].value = new
    return 1


def _edit(ws, ref, old, new, count=1):
    cur = ws[ref].value
    assert isinstance(cur, str), (ws.title, ref)
    out, n = _sub(cur, old, new, f"{ws.title}!{ref}", count)
    if n:
        ws[ref].value = out
    return n


# ================================================================== W1-W4 text (after every builder step that writes these cells)
def text_fixes(wb):
    n = 0
    l1 = wb["L1"]
    keys = {r: l1.cell(r, 1).value for r in range(128, 137)}
    assert [keys[r] for r in range(128, 137)] == ["L1_TokGW_PaidPQ_VR200", "L1_RevGW_PQ_VR200", "L1_RevGW_PQ_VR200_FY", "L1_RevGW_PQ_VR200_Life", "L1_TokLedger",
                                                   "L1_TokLedger_2026Q2", "L1_ServeGW_GW25", "L1_TokPaid_GW25", "L1_TokLedger_GW25"], keys
    for r in range(128, 132):                                   # W1-1
        n += _edit(l1, f"I{r}", Q_OLD, Q_NEW)
        n += _edit(l1, f"I{r}", P_OLD, P_NEW)
    cur = l1["I132"].value                                       # W1-2
    if not cur.endswith(I132_TAIL):
        assert cur.endswith("舊 L1_MFleet＝m ÷ 本列。不是 m。"), cur
        l1["I132"].value = cur + I132_TAIL; n += 1
    n += _set(l1, "I133", I133_OLD, I133_NEW)                    # W1-3
    for r in (134, 135):                                         # W2
        n += _edit(l1, f"I{r}", S_OLD, S_NEW)
    n += _edit(l1, "I136", I136_OLD, I136_NEW)
    ci = wb["Cap_In"]
    assert ci["A335"].value.startswith("token 帳") or "token 帳" in str(ci["A335"].value), ci["A335"].value
    n += _edit(ci, "H335", H335_OLD, H335_NEW)

    sp = wb["SRC_Price"]                                         # W3
    r49, r50 = _find(sp, "SRC_PRC_049"), _find(sp, "SRC_PRC_050")
    assert (r49, r50) == (53, 54), (r49, r50)
    n += _set(sp, f"V{r50}", V54_OLD, V54_NEW)
    n += _set(sp, f"R{r49}", R53_OLD, R53_NEW)

    dc = wb["Decisions"]                                         # W4
    rr = _find(dc, "SL60-01")
    n += _edit(dc, f"D{rr}", D332_OLD, D332_NEW)
    return n


# ================================================================== W5: DB_Evidence E406, Decisions SL61-01
EVIDENCE = [
    EID, DATE, "CoreWeave 2026 Q2 10-Q 出租方計價錨點：出租方每 active GW 年營收 ÷ Tokenomics 持有成本 0.76–1.28（7 月漲價後 0.95–1.60），低於 AL_SpendBasis 1.8",
    "CoreWeave 2026 Q2 10-Q（出租方自揭）；計價錨點查證 " + EVD_CW + "（PR #163）",
    "Interested-party（CoreWeave 自揭）", "Alloc_In C23（AL_SpendBasis 1.8；0.85–2.3，不改）",
    "AL_SpendBasis 1.8（0.85–2.3，Derived；v21.2 J5 殘差法）",
    "出租方每 active GW 年營收 ÷ Tokenomics 持有成本 0.76–1.28（7 月漲價後 0.95–1.60）",
    "弱反對 AL_SpendBasis 1.8；1.8 不改（PR #163 J1，照預設；" + V + " W5）", V,
    "出租方計價錨點低於 1.8，判讀『弱反對』；active power 口徑待 10-K（PR #163 J2）；Alloc_In C23 不改，值與公式不變｜" + WO, "已處理",
    DASH, DASH, "AL_SpendBasis（不改值）", 3, "利害關係方", "弱反對（1.8 不改，active power 口徑待 10-K）｜v21.4 新增列"]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    if any(ws.cell(r, 1).value == EID for r in range(5, ws.max_row + 1)):
        return 0
    r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
    assert ws.cell(r - 1, 1).value == "E405", ws.cell(r - 1, 1).value
    for i, v in enumerate(EVIDENCE):
        put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 17))
    return 1


def _decisions():
    return [[DEC_ID, V, "v21.4 token 帳讀法改 GW 路線、過時文字更正、CoreWeave 計價錨點登錄（只改文字）",
             "W1：L1 I128:I131 第 (1) 段 token 帳折算改 GW 路線（2025 為 L1_TokLedger_GW25 約 1.52；2026 Q2 約 2.0–2.1，數值權威在 company-models OpenAI 模型），支出路線 L1_TokLedger_2026Q2（約 3.0）降為對照；"
             "第 (3) 段 L1_RevGW_Fleet_VR200 的 65.96 改『v21.3 為 66.35』；I132 句末加支出路線註；I133 改寫、原文逐字保留於『｜原：』之後（修訂九）。"
             "W2：過時數字 5.62 改『v21.3 為 2.652；v20.0 時 5.62』（L1 I134／I135／I136、Cap_In H335）。"
             "W3：SRC_Price V54（SRC_PRC_050 模型使用位置）主值改 SRC_PRC_049、原文保留；R53（SRC_PRC_049 第二來源）『—』→『免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）』，"
             "GOV_Warnings 135 → 134（SRC_Price AE53 1 → 0、Checks D87 133 → 132、D98 135 → 134）。"
             "W4：『不變』範圍寫清楚——L1_RevGW_PQ_VR200*、L1_LReqFleet_Full*、L1_LTotal*、L1_TokLedger* 的基準不變，_Lo 變體中 5 個隨機架價低端而變"
             "（L1_LTotal_Lo、L1_LTotalFleetV_Lo、L1_LTotalDisc_Lo、L1_LTotalFleetVDisc_Lo、L1_RevGW_PQ_VR200_Life_Lo）；更正 README B5／B73 與 Decisions SL60-01（D332）。"
             "W5：DB_Evidence E406（CoreWeave 2026 Q2 10-Q 出租方計價錨點，弱反對 AL_SpendBasis 1.8，不改值）。"
             "補記 v21.3 P1：v21.3 工作單 W5 寫 L1 C／H 欄，實際文字在 I 欄，v21.3 已照實際位置 I128:I131 修改（SL60-01 未寫明，於此補記）。"
             "不新增名稱（J2：不新增 GW 路線折算後的營收名稱）；SRC_HW_099 不拆（J3）；契約名稱與值不變。"
             "Andy 原話與依據：" + DEC_BY,
             DATE, DEC_BY, "v21.4 已建",
             "L1 I128:I136；Cap_In H335；SRC_Price R53／V54；README B5／B73；Decisions D332；DB_Evidence E406",
             f"{WO} W1–W6", "否"]]


def apply(wb, append_text):
    log = {"text_fixes": text_fixes(wb)}
    log["evidence"] = evidence_append(wb)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README (rows are rebuilt from the v21.3 constants with the exact substrings replaced)
def _once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)


_prev = _once(v2130.README_VERSION, B5_OLD, B5_NEW)
README_VERSION = (VERSION + "（次版，底版 v21.3：" + WO + "——只改文字；所有契約名稱的值不變；GOV_Warnings 135 → 134（W3）。"
                  "L1 I128:I133 token 帳折算改 GW 路線（支出路線 L1_TokLedger_2026Q2 降為對照）；過時數字 5.62／65.96 更正（L1 I134:I136、Cap_In H335）；"
                  "SRC_Price V54／R53；『不變』範圍寫清楚（README B5／B73、Decisions D332）；DB_Evidence E406（CoreWeave 10-Q 計價錨點，弱反對 1.8，不改值）；"
                  "區間端點與時效指紋重產；Decisions SL61-01。）以下為 " + _prev.split("_Tokenomics_", 1)[1])
_T = v2130.README_TITLE
README_TITLE = V + _T[len(v2130.V):]
README_ROW_V213 = (v2130.README_ROW[0], _once(v2130.README_ROW[1], B73_OLD, B73_NEW))      # replaces v2130.README_ROW (row 73)
README_ROW = ("v21.4 token 帳讀法與過時文字",
              "只改文字，所有契約名稱的值不變。L1 第 128–133 列 P×Q 的 token 帳折算改用 GW 路線（2025 為 L1_TokLedger_GW25 約 1.52；2026 Q2 約 2.0–2.1，數值權威在 company-models OpenAI 模型），"
              "支出路線 L1_TokLedger_2026Q2（約 3.0）降為對照；過時數字 5.62、65.96 更正；SRC_PRC_049 第二來源登錄為『免』（GOV_Warnings 135 → 134）；"
              "DB_Evidence E406 記 CoreWeave 10-Q 計價錨點（弱反對 AL_SpendBasis 1.8，1.8 不改）。細節見工作單 docs/workorders/20261024_v21.4_token帳讀法與過時文字.md 與 Decisions SL61-01。")

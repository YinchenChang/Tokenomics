# v22.0 (= v22.0 segment B3「啟用」; design docs/plan/20261105_v22.0_Terra第四層級_設計.md, section 6.1 row B3; branch claude/v22-b3).
# Module name v22000 (= v22.0.00): same five-digit rule as v21100／v21110／v21120.
# Andy's authorization (2026-11-05): 「完整第四層級」; the J1–J15 recommendations of the design are adopted as defaults (「照建議」).
#
# MAJOR version: GPT-6.1 Terra becomes the fourth live model tier; the contract gains the Terra names.
#   T1  builder/tiers.py NT_LIVE 3 -> 4 (Checks energy closure, unreachable count and V23 now include Terra; V23 comparison 32 -> 42).
#       The pre-v22.0 row layouts keep their three tier blocks (tiers.TIERS_ROWS); Terra rows are separate blocks (J14).
#   T2  Before the mix changes, the three-term readers become four-term: Interface N IF_TokGWPaidMix (v1900.TIERS_MIX), L1 row 127
#       L1_TokGW_PaidCap_VR200 (v1800); IF_PxEffMix reads Cap_In row 90 (four-term since v21.12).
#   T3  Inputs (Excel-owned, old-value guards): Cap_In D31 Sol 0.45 -> 0.30, F31 Terra 0 -> 0.15 (J6 (a)); B4_TerraFam 0 -> 1 (J9 (a));
#       Terra list prices Cap_In F6:F8 and E59:G59 -> =SRC_PRC_066／067／068 (status Alt -> Active).
#   T4  Contract names: Interface R section (IF_*_Terra, IFW_*_Terra_*, IF_MixPaid_Terra／IF_MixFree_Terra) below every existing row; L1 end
#       (L1_CostDec_Terra_VR200／_GB300, L1_RevGW_Terra_VR200, each with _Lo／_Hi). No CAP_Px25_Terra*, L1_RLshare_Terra*, L1_PretrainFLOP_Terra* (J13).
#       The Terra *_Prod chain (Theory_Rev F rows) is mirrored onto the *_Prod sheets by a second v5.19 X1 pass (mirror_terra).
#   T5  SRC: SRC_PERF_088／089 (AA 77, OpenRouter P50 59 tok/s), SRC_CAP_022／023 (Terra v5.0.1 51; v4.3.2 48, grade 3) — recorded, not linked (J7 (b));
#       SRC_CAP_008 note (Sol 48 may be the GPT-6 Sol score; 12-01 monthly 1-C). Gov_Map: Cap_In R inputs and the Cap_In Terra cells.
#   T6  Records: Checks Z4, DB_Evidence E561–E565, Decisions SL70-01 and SL70-J01…J15, README, Load_Bearing!C3.
import re

from openpyxl.formula import Tokenizer
from openpyxl.utils import get_column_letter as L, range_boundaries
from openpyxl.workbook.defined_name import DefinedName

from common import put, section, F_IN, F_CALC, F_NOTE, F_BOLD, F_LINK, FILL_KEY
import tiers
import v1000
import v1410
import v21110
import v21120

VERSION = "20261105_Tokenomics_v22.0"      # single source of the version string: README!B5 and README!A1 (finish.readme); Load_Bearing!C3
DATE = "2026-11-05"
DASH = "—"
V = "v22.0"
DESIGN = v21110.DESIGN
WO = f"v22.0 B3 段（啟用）：設計文件 {DESIGN} 第 6.1 節 B3 列（chat 端派工）"
DEC_ID = "SL70-01"
DEC_BY = ("Andy 2026-11-05：「完整第四層級」；設計文件第 4 節 J1–J15 依建議預設值執行（「照建議」）。"
          "本段（B3）啟用 Terra：付費組合 Luna 0.40／Sol 0.30／Astra 0.15／Terra 0.15、家族研發計入 Terra")
TK, TL = tiers.TERRA_KEY, tiers.TERRA_LAB
TT = tiers.TERRA
EID = ["E561", "E562", "E563", "E564", "E565"]
SRC_SPD_AA, SRC_SPD_OR = "SRC_PERF_088", "SRC_PERF_089"
SRC_CAP_V5, SRC_CAP_V4 = "SRC_CAP_022", "SRC_CAP_023"
NA = '"SLO 不可達"'


def _nm(wb, n, ref):
    if n in wb.defined_names:
        del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


def _row_of_label(ws, label, col=1):
    rows = [r for r in range(1, ws.max_row + 1) if ws.cell(r, col).value == label]
    assert len(rows) == 1, (ws.title, label, rows)
    return rows[0]


# ================================================================== T3 inputs (after restore, before gov_all; old-value guards)
MIX_NOTE = (" ｜v22.0 B3（J6 (a)，Andy 2026-11-05「完整第四層級」、J1–J15 照建議）：Terra 0.15 全部取自 Sol（Sol 0.45 → 0.30），"
            "Luna 0.40、Astra 0.15 不變；Terra 區間 0.05–0.30（同量由 Sol 增減）；四項合計須為 1（Checks Z3a）。GPT-5.6 時代 Terra 本身就是中層，"
            "現行 Sol 0.45 原本就含 Terra 類用量；Terra 半價且性能接近 Sol，主要替代 Sol")
FREE_NOTE = " ｜v22.0 B3：Terra 免費組合 0（ChatGPT 免費方案未見 Terra，設計 T9；Interested-party），區間 0–0.05"
PRICE_NOTE = " ｜v22.0 B3：Terra（F 欄）＝SRC_PRC_066／067／068（gpt-6.1-terra 官方牌價 1.00／0.05／5.00，2026-10-26 發布；v21.12 為同值藍字，狀態 Alt → Active）"


def _guard(cell, old, new, log, tag):
    if cell.value == old or (isinstance(old, float) and isinstance(cell.value, (int, float)) and abs(cell.value - old) < 1e-12):
        cell.value = new
        log.append(f"{tag} {cell.parent.title}!{cell.coordinate}: {old!r} -> {new!r}")
        return True
    return False


def inputs_update(wb):
    log = []
    ws = wb["Cap_In"]
    ref = wb.defined_names["B4_MixPaid"].attr_text.split("!")[1].replace("$", "")
    c1, r1, c2, r2 = range_boundaries(ref)
    assert (c1, c2, r1) == (3, 6, 31), ref
    _guard(ws.cell(31, 4), 0.45, 0.30, log, "v22.0 T3 (J6)")
    _guard(ws.cell(31, 6), 0, 0.15, log, "v22.0 T3 (J6)")
    fam = wb.defined_names["B4_TerraFam"].attr_text.split("!")[1].replace("$", "")
    _guard(ws[fam], 0, 1, log, "v22.0 T3 (J9)")
    for r, sid, v in ((6, "SRC_PRC_066", 1), (7, "SRC_PRC_067", 0.05), (8, "SRC_PRC_068", 5)):
        if _guard(ws.cell(r, 6), v, f"={sid}", log, "v22.0 T3 (SRC link)"):
            ws.cell(r, 6).font = F_LINK
    r59 = 59
    assert ws.cell(r59, 1).value == "GPT-6.1 Terra", ws.cell(r59, 1).value
    for c, sid, v in ((5, "SRC_PRC_066", 1), (6, "SRC_PRC_067", 0.05), (7, "SRC_PRC_068", 5)):
        if _guard(ws.cell(r59, c), v, f"={sid}", log, "v22.0 T3 (SRC link)"):
            ws.cell(r59, c).font = F_LINK
    import v518
    for r, txt in ((31, MIX_NOTE), (32, FREE_NOTE), (6, PRICE_NOTE)):
        if v518._append_text(ws.cell(r, 8), txt):
            log.append(f"v22.0 T3 note Cap_In!H{r}")
    # SRC_PRC_066–068: Alt -> Active (they now feed Cap_In F6:F8 / E59:G59); the old status and use text stay in the note column W
    sp = wb["SRC_Price"]
    for r in range(5, sp.max_row + 1):
        sid = sp.cell(r, 1).value
        if sid in ("SRC_PRC_066", "SRC_PRC_067", "SRC_PRC_068") and sp.cell(r, 15).value == "Alt":
            old_use = sp.cell(r, 22).value
            sp.cell(r, 15).value = "Active"
            row = {"SRC_PRC_066": 6, "SRC_PRC_067": 7, "SRC_PRC_068": 8}[sid]
            col = {"SRC_PRC_066": "E", "SRC_PRC_067": "F", "SRC_PRC_068": "G"}[sid]
            sp.cell(r, 22).value = f"Cap_In!F{row}｜直接；Cap_In!{col}59｜直接（F 節 Terra 候選列）"
            v518._append_text(sp.cell(r, 23), f" ｜{V}：狀態 Alt → Active，連結 Cap_In F 欄（Terra 第四層級啟用；原狀態 Alt、原使用位置「{old_use}」；{WO}）")
            log.append(f"v22.0 T3 {sid} Alt -> Active")
    return log


# ================================================================== T5 SRC records (appended by gov.src_append)
AA_URL = "https://artificialanalysis.ai/models/gpt-6-1-terra"
OR_URL = "https://openrouter.ai/openai/gpt-6.1-terra"


def src_new_records(wb):
    from v1720 import _rec
    recs = []
    for sid, metric, val, basis, src, stance_note, note in (
        (SRC_SPD_AA, "GPT-6.1 Terra 每用戶輸出速度（Artificial Analysis；Max）", 77, "第三方量測；模型頁中位數；GPT-6.1 Terra (Max)", AA_URL + "（2026-11-05 讀取）",
         "Artificial Analysis：獨立量測（探測請求）",
         f"{V} B3（設計 T10）：同一來源一週內 77–97 浮動（10-27 為 91、11-01 為 97，二手轉述），只作區間；Serving!F21 基準 67.4＝√(77×59)（v21.11 以數值寫入，本紀錄不連結）"),
        (SRC_SPD_OR, "GPT-6.1 Terra 每用戶輸出速度（OpenRouter，OpenAI 供應商 P50）", 59, "第三方量測；實際流量 P50；供應商 OpenAI", OR_URL + "（2026-11-05 讀取）",
         "OpenRouter：路由服務實測（實際流量）",
         f"{V} B3（設計 T10）：同頁 Azure 55、Bedrock 75、OpenAI Fast 70、Flex 48；Serving!F21 基準 67.4＝√(77×59)（本紀錄不連結）")):
        rec = _rec(sid, "SRC_Perf", metric, val, None, None, "tok/s", basis, "GPT-6.1 Terra", "2026-11-05", src, 1, "中立", stance_note, "一手（已讀）",
                   "—（Serving!F21 的依據；未以公式連結）", note)
        rec.update(status="Alt", s="U-V2200", ev=EID[1])
        recs.append(rec)
    for sid, metric, val, basis, src, grade, hand, note in (
        (SRC_CAP_V5, "AA Intelligence Index v5.0.1：GPT-6.1 Terra", 51, "v5.0.1（Max）", AA_URL + "（2026-11-05 讀取）", 1, "一手（已讀）",
         f"{V} B3（設計 T13，J7 (b)）：同一版本 v5.0.1 下 Luna 28／Terra 51／Sol 55／Astra 57；只登錄、不連結（Cap_In F 節 Terra 能力指數暫空白），12-01 月度 1-C 以 v5.0 重基準時填入"),
        (SRC_CAP_V4, "AA Intelligence Index v4.3.2：GPT-6.1 Terra（發布時）", 48, "v4.3.2（二手轉述）", "https://aiwiki.ai/wiki/gpt_6_1_terra（轉述 AA 發布文；2026-11-05 讀取）", 3, "二手",
         f"{V} B3（設計 T14，J7 (b)）：二手稱「比 Sol 低 4 分、比 Luna 高 10 分」，與 TK 現值 Sol 48（SRC_CAP_008）、Luna 37 不一致——版本混用的產物；只登錄、不連結")):
        rec = _rec(sid, "SRC_Cap", metric, val, None, None, "指數", basis, "GPT-6.1 Terra", "2026-11-05", src, grade, "中立",
                   "Artificial Analysis：獨立評測" + ("" if grade == 1 else "（經二手轉述）"), hand, "—（未連結模型格；J7 (b)）", note)
        rec.update(status="Alt", s="U-V2200", ev=EID[2])
        recs.append(rec)
    return recs


CAP008_NOTE = (f" ｜{V} B3 待核（12-01 月度 1-C）：二手稱 v4.3.2 下 GPT-6.1 Terra 48「比 Sol 低 4 分」，暗示 v4.3.2 的 GPT-6.1 Sol 為 52；"
               "本筆 48 可能是 GPT-6 Sol 而非 GPT-6.1 Sol 的分數（見 SRC_CAP_023、DB_Evidence E564）")


def src_notes(wb, append_text):
    ws = wb["SRC_Cap"]
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "SRC_CAP_008":
            return int(bool(append_text(ws.cell(r, 23), CAP008_NOTE)))
    return 0


# ================================================================== T5 Gov_Map (gov.gm_append_c)
def gov_map_rows(wb):
    out = []
    sc = "v22.0 B3（Terra 第四層級）"
    ws = wb["Cap_In"]

    def ent(row, cell, role, cls, lo, hi, rtext, reason, src="", rel="", dec=DEC_ID):
        lab = ws[f"A{row}"].value
        out.append({'scope': sc, 'sheet': "Cap_In", 'cell': cell, 'label': lab, 'check': lab, 'cls': cls, 'role': role, 'src': src, 'rel': rel, 'dec': dec,
                    'lo': lo, 'hi': hi, 'rtext': rtext, 'reason': reason, 'retag': '', 'seg': '無'})
    for r, sid in ((6, "SRC_PRC_066"), (7, "SRC_PRC_067"), (8, "SRC_PRC_068")):
        ent(r, f"F{r}", "單值", "原始數據", None, None, DASH, "連結 SRC（G1）：gpt-6.1-terra 官方牌價（設計 T1）", src=sid, rel="直接", dec="")
    ent(22, "F22:F24", "群組", "Assumed", None, None, "低＝第 23 列 4、高＝第 24 列 18（月）",
        "J10：Terra 商業壽命 9 個月（4–18）——GPT-5.6 Terra（2026-07-09）到 6.1 Terra（10-26）約 3.5 個月；只影響 Terra 訓練攤提")
    ent(31, "F31", "單值", "Assumed", 0.05, 0.30, "0.05–0.30（同量由 Sol 增減；四項合計維持 1）",
        "J6 (a)：Terra 2026 付費 token 占比 0.15，全部取自 Sol（0.45 → 0.30）；GPT-5.6 時代 Terra 即中層，Terra 半價且性能接近 Sol")
    ent(32, "F32", "單值", "Interested-party", 0, 0.05, "0–0.05", "設計 T9：ChatGPT 免費方案未見 Terra；Terra 免費組合 0")
    k = wb.defined_names["B4_MixPaid25"].attr_text.split("!")[1].replace("$", "").split(":")[0]
    rp = int(re.sub(r"[A-Z]+", "", k))
    ent(rp, f"C{rp}:F{rp}", "群組", "Decision", None, None, "結構選擇（無數值區間）",
        "J5 (a)：2025 校準口徑不含 Terra（Terra＝0），數值逐字等於 v21.10 的 D 節付費組合（0.40／0.45／0.15）；Alloc、CAP_Price25Mix、L1_TokPaid_GW25 讀本列")
    ent(rp + 1, f"C{rp + 1}:F{rp + 1}", "群組", "Decision", None, None, "結構選擇（無數值區間）",
        "J5 (a)：2025 免費組合（0.90／0.10／0／0），等於 v21.10 的 D 節免費組合；Terra＝0")
    ent(rp + 2, f"C{rp + 2}", "單值", "Decision", None, None, "結構選擇（0／1）",
        "J9 (a)：2026 起家族研發含 Terra（1）；作用在 Fleet_1GW 家族研發計畫與 Amortize K6 自下而上總額的 Terra 項")
    return out


# ================================================================== T4 L1 rows (appended at the end of L1, J14)
COST_RNG = "成本情境 低／高（Interface 第 5 列）"
UTIL_RNG = "利用率 40–80%（Sens_Rev 情境值；J6 區間）"


def l1_rows_new():
    R = []
    for g, c0 in (("VR200", 10), ("GB300", 7)):
        R.append((f"CostDec_{TK}_{g}", f"decode（含思考）每 M token 成本 — {TK}（{g}；v22.0 第四層級）", "經濟口徑、100% 利用率、SLO 下", f"=INDEX(IF_CostDec_{TK},1,{c0+1})",
                  f"=INDEX(IF_CostDec_{TK},1,{c0})", f"=INDEX(IF_CostDec_{TK},1,{c0+2})", "$/M", COST_RNG,
                  "基準利用率版＝100% 版 ÷ 利用率（IF_Util）；Terra 架構未公開（V4 家族內插 700B／30B，Analogy；J4）", "η_d、每層延遲、SLO、Terra 架構（Arch F 欄）",
                  "Terra 架構：Analogy（低／高端每 GW 產能約 ±60%，見 v22.0 報告）",
                  DASH, None, None, f"IF_CostDec_{TK}", "Interface R 節", "VR200 無實測，η_d 沿用 GB300" if g == "VR200" else DASH))
    R.append((f"RevGW_{TK}_VR200", f"每 GW 理論營收（理想上限）— {TK}（VR200；v22.0 第四層級）", "OpenAI 有效單價、基準成本、基準利用率", f"=INDEX(IF_RevGW_{TK},1,11)",
              f"=INDEX(IF_RevGW_{TK},1,11)*(Sens_Rev!$B$6/IF_Util)", f"=INDEX(IF_RevGW_{TK},1,11)*(Sens_Rev!$B$7/IF_Util)", "$B/GW/年", UTIL_RNG,
              "單一層級滿載的上限；實際營收（需求、市占）在下游", "利用率、折扣、快取命中 χ（Sens_Rev）；Terra 架構與 SLO",
              "利用率 60%：Assumed（K11）；Terra 架構：Analogy", DASH, None, None, f"IF_RevGW_{TK}", "Interface R 節", "需求與市占不在第 0 層（D7）"))
    return R


v1000._n(v1000.E_, "roofline 推導的每 token 成本（自下而上；v22.0 Terra 第四層級）", f"CostDec_{TK}_VR200", f"CostDec_{TK}_GB300")
v1000._n(v1000.E_, "理論營收上限＝每 GW 產出 × 牌價（物理量 × 單價），不含 L、m（v22.0 Terra 第四層級）", f"RevGW_{TK}_VR200")


# ================================================================== T4 Terra *_Prod chain (second v5.19 X1 pass)
def mirror_terra(wb, terra_late):
    """Mirror the cells behind the Terra Theory_Rev F rows (理論營收、全成本) onto the existing *_Prod sheets at the same addresses (v5.19 X1 rules:
    references to chain cells point to *_Prod, the seed reads CTL_ProdDerate; check copy at +SHIFT reads Serving!C18). Cells already mirrored by
    v519.x1 are not rewritten (the old chain does not read the new cells: a cell in both cones of the old targets is already in the old chain)."""
    import collections
    import v519
    tr = terra_late["theory_rev"]
    names = {n: wb.defined_names[n].attr_text for n in wb.defined_names}
    cells = v519._formula_cells(wb)
    refs = v519._refs(wb, names, cells)
    by_sheet = collections.defaultdict(list)
    for key, rl in refs.items():
        for (sh, c1, r1, c2, r2) in rl:
            by_sheet[sh].append((key, c1, r1, c2, r2))
    seeds = [k for k, rl in refs.items() if any(sh == "Serving" and c1 <= 3 <= c2 and r1 <= 18 <= r2 for (sh, c1, r1, c2, r2) in rl)]
    fwd, frontier = set(seeds), list(seeds)
    while frontier:
        nxt = []
        grid = collections.defaultdict(set)
        for sh, c, r in frontier:
            grid[sh].add((c, r))
        for sh, pts in grid.items():
            for key, c1, r1, c2, r2 in by_sheet[sh]:
                if key not in fwd and any(c1 <= c <= c2 and r1 <= r <= r2 for c, r in pts):
                    fwd.add(key); nxt.append(key)
        frontier = nxt

    def back(targets):
        bwd, stack = set(targets), list(targets)
        while stack:
            key = stack.pop()
            for (sh, c1, r1, c2, r2) in refs.get(key, []):
                for c in range(c1, c2 + 1):
                    for r in range(r1, r2 + 1):
                        k = (sh, c, r)
                        if k in cells and k not in bwd:
                            bwd.add(k); stack.append(k)
        return bwd
    old_t = [("Theory_Rev", c, r) for r, _ in v519.TARGETS for c in v519.SEED_COLS]
    new_t = [("Theory_Rev", c, r) for r in (tr["rev"], tr["fc"]) for c in v519.SEED_COLS]
    S_old = fwd & back(old_t)
    S_new = fwd & back(new_t)
    S = S_old | S_new
    add = sorted(S_new - S_old)
    seeds = set(seeds)
    assert all(k[0] in v519.SRC_SHEETS for k in add), sorted({k[0] for k in add})
    rows_new = collections.defaultdict(set)
    from copy import copy
    for key in add:
        s, c, r = key
        src = wb[s]; ws = wb[s + v519.SUFFIX]
        assert c in v519.span(s), key
        sc = src.cell(r, c)
        for shift in (0, v519.SHIFT):
            if key in seeds:
                f = "=CTL_ProdDerate" if shift == 0 else v519.C18
            else:
                f = v519.mirror_formula(cells[key], s, S, names, shift)
            assert ws.cell(r, c + shift).value is None, (s, r, c + shift, ws.cell(r, c + shift).value)
            put(ws, f"{L(c + shift)}{r}", f, fmt=sc.number_format, fill=copy(sc.fill) if sc.fill.fill_type else None)
        rows_new[s].add(r)
    for s, rows in rows_new.items():
        src = wb[s]; ws = wb[s + v519.SUFFIX]
        for r in rows:
            for c in (1, 2):
                v = src.cell(r, c).value
                if v is None or ws.cell(r, c).value is not None:
                    continue
                put(ws, f"{L(c)}{r}", f"={v519._qs(s)}!{L(c)}{r}" if isinstance(v, str) and v.startswith("=") else v, F_NOTE if c == 2 else None)
    return {"cells": len(add), "rows": {s: sorted(v) for s, v in rows_new.items()}}


# ================================================================== T4 Interface R section
R_TITLE = (f"R. {TL}第四層級（v22.0；J1 (a) 計算索引 4、J14 (a) 集中於本節，既有各節列不位移）：GPT-6.1 Terra 的契約名稱。每列口徑同列名「對應 X 節」的 Luna／Sol／Astra 列"
           "（欄位同該節：C–Q＝5 世代 × 3 成本情境；對應 E 節者 C–G＝Workload 任務；單格者只用 C）。閱讀順序依價格 Luna < Terra < Sol < Astra。"
           "Terra 架構未公開（V4 家族內插 700B／30B，Analogy／Assumed，J4）；能力指數暫空白，不參與其他層級前緣（J7 (b)）")
SUB = {"B": "Block 2 產出（100%＝理想上限）", "C": "Block 3 產出（訓練與研發計畫）", "D": "Block 4 產出（牌價、前緣、壽命、攤提、全成本、理論營收、機隊貢獻）",
       "E": "Block 5 產出（每任務：成功率、每成功任務成本與營收、R、有效時間範圍）", "G": "生產折減並列（CTL_ProdDerate；*_Prod 鏡像）", "H": "營收實現過渡別名（下一個主版刪除，J15）",
       "J": "四層瀑布（_100 → _Util → _Prod → _Life）", "L": "情境：自算 L、m（IFW_*_LifeSelf）", "M": "契約補名（訓練 FLOPs、推論占比、預設毛利率）",
       "N": "P×Q 取數：層級組合（v22.0 起四項合計 1；三個 IF_MixPaid_Luna／Sol／Astra 不再合計 1）"}
TIER4 = ("B4_Life", "B4_MixPaid", "B4_MixFree", "B4_FrontRef", "B4_EffRef", "B4_EffIn", "B4_EffCache", "B4_EffOut", "B4_PriceIn", "B4_PriceCache", "B4_PriceOut",
         "B4_ISL", "B4_OSL")
TAG = re.compile(r"　\[([A-Za-z0-9_]+)\]")


def _sec_of_rows(ws):
    """Interface row -> section letter (A. … P. titles)."""
    sec, out = None, {}
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        m = re.match(r"^([A-Z])\. ", a) if isinstance(a, str) else None
        if m:
            sec = m.group(1)
        out[r] = sec
    return out


def _cells_of(ref):
    sh, rg = ref.split("!")
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    return sh, c1, r1, c2, r2


def interface_r(wb, S4, A4, terra_late):
    ws = wb["Interface"]
    sec_of = _sec_of_rows(ws)
    tr, ht = terra_late["theory_rev"], terra_late["harness"]
    # Luna contract names on Interface (in row order) -> their Terra counterparts
    luna = []
    for n in wb.defined_names:
        if not re.match(r"^IFW?_.*(_Luna$|_Luna_)", n):
            continue
        sh, c1, r1, c2, r2 = _cells_of(wb.defined_names[n].attr_text)
        if sh != "Interface":
            continue
        luna.append((r1, n, c1, c2))
    luna.sort()
    assert len(luna) == 66, len(luna)
    # per-sheet row maps Luna -> Terra (single-reference rows), Price_Frontier column map C -> F
    stem = lambda n: n.replace("_Luna", "_{T}")
    single = {}
    for r, n, c1, c2 in luna:
        f = ws.cell(r, 3).value
        m = re.fullmatch(r"=(\w+)!C(\d+)", f) if isinstance(f, str) else None
        if m:
            single[stem(n)] = (m.group(1), int(m.group(2)))
    TGT = {      # Terra row of each single-reference stem (sheet must match the Luna row's sheet)
        "IF_CacheStore_{T}": ("Cache_Store", S4[TK]),
        "IF_AmortBU_{T}": ("Amortize", A4[f"bu{TT - 1}"]), "IF_AmortTD_{T}": ("Amortize", A4[f"td{TT - 1}"]),
        "IF_AmortDefault_{T}": ("Amortize", A4[f"dc{TT - 1}"]), "IF_AmortRev_{T}": ("Amortize", A4[f"dd{TT - 1}"]),
        "IF_FullCost_{T}": ("Theory_Rev", tr["fc"]), "IF_FullCostDefault_{T}": ("Theory_Rev", tr["fcd"]), "IF_RevGW_{T}": ("Theory_Rev", tr["rev"]),
        "IF_RevGWFront_{T}": ("Theory_Rev", tr["revf"]), "IF_GMDefault_{T}": ("Theory_Rev", tr["gmd"]),
        "IF_RevGWFleet_{T}": ("Theory_Rev", tr["flt"]), "IF_RevGWFleetFront_{T}": ("Theory_Rev", tr["flft"]),
        "IF_FullCost_{T}_Prod": ("Theory_Rev_Prod", tr["fc"]), "IF_RevGW_{T}_Prod": ("Theory_Rev_Prod", tr["rev"]),
        "IF_TaskSucc_{T}": ("Harness", ht["p_cur"]), "IF_TaskSuccSel_{T}": ("Harness", ht["p_sel"]), "IF_CostSuccVR_{T}": ("Harness", ht["cs_VR200cur"]),
        "IF_CostSuccGB_{T}": ("Harness", ht["cs_GB300cur"]), "IF_RevSucc_{T}": ("Harness", ht["rs_cur"]), "IF_HarR_{T}": ("Harness", ht["R_VR200"]),
        "IF_CostAttVR_{T}": ("Harness", ht["c_VR200cur"]), "IF_HzEff_{T}": ("Harness", ht["hz"]),
    }
    U = tiers.SRC["U"]
    for key in ("cf", "cc", "cd", "cda"):
        nm = {"cf": "IF_CostPre_{T}", "cc": "IF_CostCache_{T}", "cd": "IF_CostDec_{T}", "cda": "IF_CostDecAcct_{T}"}[key]
        assert single[nm] == ("Unit_Cost", U[(1, key)]), (nm, single[nm])
        TGT[nm] = ("Unit_Cost", U[(TT, key)])
    rowmap = {}      # (sheet, luna row) -> terra row
    for nm, (sh, r) in TGT.items():
        lsh, lr = single[nm]
        assert lsh == sh, (nm, lsh, sh)
        rowmap[(sh, lr)] = r
    lr_rev = single["IF_RevGW_{T}"][1]
    rowmap[("Theory_Rev_Prod", lr_rev - 1)] = tr["tok"]      # 每 GW 產出（IFW_TokGW_*_Prod reads it）
    assert ("Theory_Rev", lr_rev - 1) not in rowmap
    # layout: one block per source section, rows in the Luna order
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    plan = []
    r = r0 + 1
    cur = None
    for lr, n, c1, c2 in luna:
        s = sec_of[lr]
        if s != cur:
            plan.append(("sub", s, r)); r += 1; cur = s
        plan.append(("row", (lr, n, c1, c2, s), r)); r += 1
    plan.append(("sub", "N", r)); r += 1      # IF_MixPaid_Terra／IF_MixFree_Terra already in plan (N rows of Luna) — the extra sub row holds the note
    ifmap = {lr: rr for kind, x, rr in plan if kind == "row" for lr in [x[0]]}
    # the Terra alias IF_RevGW_Terra_Life points at IFW_RevGW_Terra_Life (no Theory_Rev alias row for Terra)
    life_row = next(rr for kind, x, rr in plan if kind == "row" and x[1] == "IFW_RevGW_Luna_Life")

    def tf(f, lr):
        if not (isinstance(f, str) and f.startswith("=")):
            return f
        f = re.sub(r"(\d\*\(Unit_Cost!\$?[A-Z]+\$?6-1\))\+1(?!\d)", rf"\g<1>+{TT}", f)
        f = re.sub(r"INDEX\((" + "|".join(TIER4) + r"),1,1\)", rf"INDEX(\1,1,{TT})", f)
        out = ["="]
        for t in Tokenizer(f).items:
            v = t.value
            if t.type == "OPERAND" and t.subtype == "RANGE":
                if "!" in v:
                    sh, rg = v.rsplit("!", 1)
                    sh = sh.strip("'")
                    m = re.fullmatch(r"(\$?)([A-Z]{1,3})(\$?)(\d+)", rg)
                    if sh == "Price_Frontier" and m and m.group(2) == "C":
                        v = f"Price_Frontier!{m.group(1)}{tiers.TC[TT - 1]}{m.group(3)}{m.group(4)}"
                    elif m and (sh, int(m.group(4))) in rowmap:
                        v = f"{sh}!{m.group(1)}{m.group(2)}{m.group(3)}{rowmap[(sh, int(m.group(4)))]}"
                    elif sh in ("Perf", "Training") and re.fullmatch(r"\$C\$(\d+):\$[A-Z]+\$\1", rg):
                        pass
                    elif sh == "Unit_Cost" and m and int(m.group(4)) in (6, 8):
                        pass
                    else:
                        raise AssertionError(f"unmapped tier reference {v!r} in {f!r} (Interface row {lr})")
                elif re.fullmatch(r"\$?[A-Z]{1,3}\$?\d+", v):
                    m = re.fullmatch(r"(\$?)([A-Z]{1,3})(\$?)(\d+)", v)
                    rr = int(m.group(4))
                    assert rr in ifmap, f"unmapped Interface reference {v!r} in {f!r} (row {lr})"
                    v = f"{m.group(1)}{m.group(2)}{m.group(3)}{ifmap[rr]}"
                elif "Luna" in v:
                    v = v.replace("Luna", TK)
            out.append(v)
        g = "".join(out)
        assert "Luna" not in g, g
        return g

    section(ws, r0, R_TITLE, 17)
    made = []
    from copy import copy
    for kind, x, rr in plan:
        if kind == "sub":
            s = x
            put(ws, f"A{rr}", f"R-{s}　{TL}｜{SUB.get(s, '')}（對應 {s} 節）", F_BOLD)
            if s == "N" and rr == plan[-1][2]:
                put(ws, f"A{rr}", f"註：{V} 起付費組合四項（IF_MixPaid_Luna＋_Sol＋_Astra＋_Terra）合計＝1、免費組合四項合計＝1（Checks Z3／Z4）；"
                                  "下游以三個 IF_MixPaid_* 合計當 1 者須加讀 IF_MixPaid_Terra（下游契約 v0.28）", F_NOTE)
            continue
        lr, n, c1, c2, s = x
        tn = n.replace("_Luna", f"_{TK}")
        lab = TAG.sub("", str(ws.cell(lr, 1).value)).split("｜v15.0 O12")[0]
        lab = lab.replace("Luna（低層）", TL).replace("Luna", TK)
        if TK not in lab:
            lab = f"{TL}｜{lab}"
        put(ws, f"A{rr}", f"{lab}（對應 {s} 節）　[{tn}]"); put(ws, f"B{rr}", ws.cell(lr, 2).value)
        for c in range(c1, c2 + 1):
            src = ws.cell(lr, c)
            if tn == f"IF_RevGW_{TK}_Life":
                f = f"={L(c)}{life_row}"
            else:
                f = tf(src.value, lr)
            put(ws, f"{L(c)}{rr}", f, fmt=src.number_format, fill=copy(src.fill) if src.fill.fill_type else None)
        ref = f"Interface!${L(c1)}${rr}" if c1 == c2 else f"Interface!${L(c1)}${rr}:${L(c2)}${rr}"
        _nm(wb, tn, ref)
        made.append((tn, ref, rr))
    return {"start": r0, "end": plan[-1][2], "made": made}


# ================================================================== T6 Checks Z4 (after Z3)
def checks_z4(wb):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, f"Z4. Terra 第四層級（{V} B3）：Z4a／Z4b 為 ERROR 計入 GOV_Errors；Z4c／Z4d 為 WARN 計入 GOV_Warnings（設計 V6）；Z4e 為對照（不計數）", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]):
        put(ws, f"{'ABCDE'[i]}{r}", h, F_BOLD)
    r += 1
    tg = lambda t, k: f"INDEX(IF_TokGW_{t},1,{k})"
    cd = lambda t, k: f"INDEX(IF_CostDec_{t},1,{k})"
    base = (2, 5, 8, 11, 14)      # base-cost column of each generation inside C:Q
    between = lambda f: "+".join(f"IF(AND(ISNUMBER({f(TK, k)}),ISNUMBER({f('Sol', k)}),ISNUMBER({f('Luna', k)})),"
                                 f"IF(AND({f(TK, k)}>=MIN({f('Sol', k)},{f('Luna', k)}),{f(TK, k)}<=MAX({f('Sol', k)},{f('Luna', k)})),0,1),1)" for k in base)
    rows = [("Z4a", "契約名稱付費組合 IF_MixPaid_Luna＋_Sol＋_Astra＋_Terra 合計 ≠ 1（容差 1e-9）", "ERROR",
             "=IF(ABS(IF_MixPaid_Luna+IF_MixPaid_Sol+IF_MixPaid_Astra+IF_MixPaid_Terra-1)>1E-9,1,0)", "Interface N 節＋R 節（v22.0 起三個 IF_MixPaid_* 不再合計 1）"),
            ("Z4b", "契約名稱免費組合 IF_MixFree_* 四項合計 ≠ 1（容差 1e-9）", "ERROR",
             "=IF(ABS(IF_MixFree_Luna+IF_MixFree_Sol+IF_MixFree_Astra+IF_MixFree_Terra-1)>1E-9,1,0)", "Interface N 節＋R 節"),
            ("Z4c", "Terra 每 GW 產能（IF_TokGW_Terra，基準成本欄）不在 Sol 與 Luna 之間的世代數（或不可達）", "WARN", "=" + between(tg),
             "5 世代 × 基準成本欄；高端架構時 Terra 可略低於 Sol（設計 V6）"),
            ("Z4d", "Terra decode 成本（IF_CostDec_Terra，基準成本欄）不在 Luna 與 Sol 之間的世代數（或不可達）", "WARN", "=" + between(cd), "同上"),
            ("Z4e", "單價前緣模型：Terra（J7 (b)：能力指數空白，前緣＝自身）", "—", "=Price_Frontier!F26", "Price_Frontier F26（對照；第 47–49 列為 Luna／Sol／Astra）")]
    out = {}
    for code, lab, lvl, f, note in rows:
        put(ws, f"A{r}", code); put(ws, f"B{r}", lab); put(ws, f"C{r}", lvl, F_BOLD if lvl == "ERROR" else None)
        put(ws, f"D{r}", f, fmt="0" if code != "Z4e" else None); put(ws, f"E{r}", note, F_NOTE)
        out[code] = r; r += 1
    for nm, codes in (("GOV_Errors", ("Z4a", "Z4b")), ("GOV_Warnings", ("Z4c", "Z4d"))):
        ref = wb.defined_names[nm].attr_text.split("!")[1].replace("$", "")
        cell = ws[ref]
        for c in codes:
            if f"D{out[c]}" not in str(cell.value):
                cell.value = f"{cell.value}+D{out[c]}"
    b = ws[f"B{int(wb.defined_names['GOV_Errors'].attr_text.split('$')[-1])}"]
    if "Z4" not in str(b.value):
        b.value = str(b.value).replace("Z2、Z3 節）", "Z2、Z3、Z4 節）")
    return out


# ================================================================== T6 DB_Evidence, Decisions
def _ev(eid, claim, src, tag, param, then, new, verdict, note, status, sids, affected, grade, stance, d15):
    return [eid, DATE, claim, src, tag, param, then, new, verdict, V, note + "｜" + WO, status, sids, DASH, affected, grade, stance, d15]


EVID = [
    _ev(EID[0], "gpt-6.1-terra 啟用為第四層級：牌價 1.00／0.05／5.00 連結 Cap_In F6:F8 與 F 節第 59 列；2026 付費組合 Terra 0.15（取自 Sol），家族研發計入 Terra",
        "OpenAI 官方定價頁與模型頁（SRC_PRC_066–068，E415）；設計文件第 2、3.5 節", "Interested-party／1 級（牌價）；組合 Assumed",
        "Cap_In F6:F8、E59:G59、D31、F31、B4_TerraFam", "牌價藍字同值（v21.12）；組合 0.40／0.45／0.15／0", "牌價連結 SRC；組合 0.40／0.30／0.15／0.15；B4_TerraFam 1",
        "採用（v22.0 B3；J6 (a)、J9 (a)）", "E415 的「是否入 Cap_In」由 v22.0 B3 回答：Terra 入模為第四層級（Andy「完整第四層級」）；能力指數仍空白（J7 (b)）", "已處理",
        "SRC_PRC_066、SRC_PRC_067、SRC_PRC_068", "IF_MixPaid_Sol、IF_PxEffMix、IF_TokGWPaidMix、L1_M、L1_RevGW_PQ_VR200 等（見 v22.0 預期變動 CSV）", 1, "利害關係方（OpenAI 牌價）", "採用｜v22.0 新增列"),
    _ev(EID[1], "GPT-6.1 Terra 第三方輸出速度：AA 77 tok/s（Max，2026-11-05）；OpenRouter OpenAI 供應商 P50 59 tok/s（2026-11-05）",
        f"{AA_URL}；{OR_URL}（設計 T10）", "Verified-measured（第三方）", "Serving!F21（Terra SLO 67.4＝√(77×59)）", "67.4（v21.11 以數值寫入）", "77／59",
        "登錄（不改值）", "AA 一週內 77–97 浮動，只作區間（59–90）；本版不把 F21 改為公式（待 Project 判斷）", "已處理", f"{SRC_SPD_AA}、{SRC_SPD_OR}", "—（值不變）", 1, "中立", "登錄｜v22.0 新增列"),
    _ev(EID[2], "GPT-6.1 Terra 能力指數：AA v5.0.1＝51（同版本 Luna 28／Sol 55／Astra 57）；v4.3.2＝48（二手轉述）",
        f"{AA_URL}；aiwiki 轉述（設計 T13、T14）", "Verified-measured（v5.0.1）／Analogy（v4.3.2 二手）", "Cap_In F 節第 59 列 I 欄（能力指數；空白）", "空白（v21.12）", "51（v5.0.1）／48（v4.3.2）",
        "登錄、不連結（J7 (b)）", "v4.3.2 的 48 與 Sol 48 打平是版本混用；同版本 v5.0.1 下 Terra 51 < Sol 55。12-01 月度 1-C 以 v5.0 重基準時 14 列一次填入", "待判定（12-01 月度 1-C）",
        f"{SRC_CAP_V5}、{SRC_CAP_V4}", "—（值不變；若改採 J7 (a)，IF_FrontRef_Sol 約減半）", 1, "中立", "登錄｜v22.0 新增列"),
    _ev(EID[3], "待核：SRC_CAP_008（AA v4.3.2 GPT-6.1 Sol＝48）可能是 GPT-6 Sol 的分數——二手稱 v4.3.2 下 Terra 48「比 Sol 低 4 分」，暗示 GPT-6.1 Sol 為 52",
        "aiwiki 轉述 AA 發布文（設計第 0 節第 5 點、3.6 節）", "Analogy（二手）", "Cap_In!I47（Sol 能力指數，SRC_CAP_008）", "48", "可能 52（未證實）",
        "列入 12-01 月度 1-C", "Sol 前緣由能力門檻決定；若 SRC_CAP_008 改值，Sol 前緣可能改變。本版不改", "待判定（12-01 月度 1-C）", "SRC_CAP_008、" + SRC_CAP_V4,
        "—（本版不改）", 3, "中立（經二手）", "待核｜v22.0 新增列"),
    _ev(EID[4], "GPT-6.1 Terra 可用範圍：ChatGPT Work 與 Codex（Plus／Pro／Business／Enterprise／Edu），免費方案未見；API gpt-6.1-terra",
        "aicybr、aiwiki、aiweekly 二手轉述官方說明（設計 T9）", "Interested-party（二手）", "Cap_In!F32（Terra 免費組合）", "0", "0（區間 0–0.05）", "採用（值不變）",
        "免費組合 Terra 0；付費組合 Terra 0.15（J6 (a)）", "已處理", "—", "—（值不變）", 2, "利害關係方（OpenAI 方案說明）", "採用｜v22.0 新增列"),
]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    have = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    n = 0
    for row in EVID:
        if row[0] in have:
            continue
        r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
        for i, v in enumerate(row):
            put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 17))
        n += 1
    return n


J_ROWS = [
    ("J01", "J1 Terra 的層級索引與顯示順序", "(a) 附加為索引 4（計算順序 Luna、Sol、Astra、Terra）；閱讀版、網站、Interface R 節依價格 Luna < Terra < Sol < Astra；標籤「Terra（中低層）」"),
    ("J02", "J2 輸入頁 Terra 欄位置", "(a) 緊接 Astra 的 F 欄，不移動任何既有藍字輸入格（v21.11／v21.12 已建）"),
    ("J03", "J3 世代 × 層級頁欄位", "(a) 20 欄（C–V），索引 4×(世代−1)＋層級；preserve 欄位對照（v21.11 已建）"),
    ("J04", "J4 Terra 架構代表", "(a) DeepSeek V4 家族內插（700B／30B，V4 注意力）；Analogy／Assumed 區間見 Arch F 欄"),
    ("J05", "J5 2025 校準與 Terra", "(a) 2025 口徑不含 Terra（B4_MixPaid25／B4_MixFree25，Terra＝0）；2025 錨點逐值不變（v22.0 驗收 V4）"),
    ("J06", "J6 2026 付費組合重分", "(a) Terra 0.15 全部取自 Sol：Luna 0.40／Sol 0.30／Astra 0.15／Terra 0.15，區間 Terra 0.05–0.30；免費組合 Terra 0（v22.0 寫入）"),
    ("J07", "J7 Terra 是否進前緣候選、能力指數", "(b) 入表但能力指數空白，不參與其他層級前緣；Terra 自身前緣＝自身牌價；v5.0.1＝51 與 v4.3.2＝48 只登錄 SRC（SRC_CAP_022／023），SRC_CAP_008 待核列入 12-01 月度 1-C"),
    ("J08", "J8 下游預設層級", "(a) 維持 Sol（IF_FullCostDefault_Sol、IF_GMDefault_* 用法不變）；OpenAI 模型的 top／mid／low 對應由該模型自己決定"),
    ("J09", "J9 家族研發計畫", "(a) 2026 起家族含 Terra（B4_TerraFam＝1，v22.0 寫入）；2025 Alloc 家族三層"),
    ("J10", "J10 Terra 商業壽命", "9 個月（4–18）"),
    ("J11", "J11 SLO 速度取法", "(a) AA × OpenRouter 幾何平均 67.4，區間 59–90；四層同日重量列入下次月度，本版不改既有三層"),
    ("J12", "J12 Terra 參考 ISL／OSL", "16,384／2,048，區間 8K–32K／1K–4K"),
    ("J13", "J13 命名", "_Terra 後綴；標籤「Terra（中低層）」；不建 CAP_Px25_Terra*、L1_RLshare_Terra*、L1_PretrainFLOP_Terra*"),
    ("J14", "J14 Interface 與 L1 的 Terra 列位置", "(a) 新增 Interface R 節與 L1 末端，既有列不位移；N 節 IF_TokGWPaidMix 就地改四項，IF_MixPaid_Terra／IF_MixFree_Terra 放 R 節"),
    ("J15", "J15 過渡別名（Theory_Rev 第 90 列 IF_RevGW_*_Life）", "(a) 不併入，另開工作單；Terra 的 IF_RevGW_Terra_Life 為 IFW_RevGW_Terra_Life 的別名（Interface R 節，同一下一個主版處理）"),
]


def _decisions():
    head = [DEC_ID, V, "v22.0 B3（啟用）：GPT-6.1 Terra 成為第四個現行層級（主版：契約新增 Terra 名稱）",
            "依設計文件 " + DESIGN + "（第 6.1 節 B3 列；J1–J15 依建議）：tiers.NT_LIVE 3 → 4（Checks 能量閉合、不可達欄數、V23 納入 Terra，V23 對照值 32 → 42）；"
            "先把 Interface N 節 IF_TokGWPaidMix 與 L1 第 127 列 L1_TokGW_PaidCap_VR200 改四項（IF_PxEffMix 讀 Cap_In 第 90 列，v21.12 已四項），再寫組合："
            "Cap_In D31 Sol 0.45 → 0.30、F31 Terra 0 → 0.15（只在仍為舊值時才寫）；B4_TerraFam 0 → 1；Terra 牌價 Cap_In F6:F8、E59:G59 改連 SRC_PRC_066–068（Alt → Active）。"
            "契約名稱：Interface R 節（IF_*_Terra 52、IFW_*_Terra_* 14，含 IF_MixPaid_Terra／IF_MixFree_Terra）與 L1 末端（L1_CostDec_Terra_VR200／_GB300、L1_RevGW_Terra_VR200，各含 _Lo／_Hi）；"
            "RNG_ 端點重產；Terra 的 *_Prod 鏈以第二次 X1 鏡像補上（Theory_Rev F 節）。SRC_PERF_088／089、SRC_CAP_022／023 只登錄不連結；SRC_CAP_008 待核。"
            "Train_In 層級代碼標籤加「4 Terra」（SNAP_MOVES）。Checks Z4。L1_M 因有效牌價下降而機械性上升（1.355 → 約 1.44），不是變現改善。依據：" + DEC_BY,
            DATE, DEC_BY, "v22.0 已建",
            "builder/tiers.py；Cap_In D31、F31、F6:F8、E59:G59、R 節；Interface N 節、R 節；L1 第 127 列與末端；SRC_Price 066–068；SRC_Perf 088／089；SRC_Cap 022／023；Checks Z4；*_Prod Theory_Rev F 節",
            WO, "否"]
    rows = [head]
    for j, title, dec in J_ROWS:
        rows.append([f"SL70-{j}", V, f"v22.0 Terra 設計判斷 {title}", f"照建議：{dec}", DATE,
                     "Andy 2026-11-05：「完整第四層級」；設計文件第 4 節 J1–J15 依建議預設值執行（「照建議」）", "v22.0 已建",
                     "見 SL70-01；設計文件第 4 節", WO, "否"])
    return rows


def apply(wb, append_text):
    log = {"z4": checks_z4(wb), "evidence": evidence_append(wb), "cap008": src_notes(wb, append_text)}
    ws = wb["Decisions"]
    have = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    log["decisions"] = v1410.decisions_append(wb, [x for x in _decisions() if x[0] not in have])
    return log


# ================================================================== Load_Bearing!C3, README
def load_bearing_date(wb):
    ws = wb["Load_Bearing"]
    assert str(ws["A3"].value).startswith("建置日"), ws["A3"].value
    d = VERSION.split("_", 1)[0]
    put(ws, "C3", f"{d[:4]}-{d[4:6]}-{d[6:]}", F_CALC)


_prev = v21120.README_VERSION.split("_Tokenomics_", 1)[1]
README_VERSION = (VERSION + "（主版，底版 v21.12：" + WO + "——v22.0：GPT-6.1 Terra 啟用為第四個現行層級（Andy 2026-11-05「完整第四層級」，J1–J15 照建議）："
                  "2026 付費組合 Luna 0.40／Sol 0.30／Astra 0.15／Terra 0.15（原 Sol 0.45），家族研發計入 Terra；Terra 牌價連結 SRC_PRC_066–068；"
                  "IF_TokGWPaidMix、L1_TokGW_PaidCap_VR200 改四項；新增 Interface R 節（Terra 契約名稱 IF_*_Terra、IFW_*_Terra_*、IF_MixPaid_Terra／IF_MixFree_Terra）與 L1 末端 Terra 列；"
                  "三個 IF_MixPaid_Luna／Sol／Astra 不再合計 1；2025 錨點不變（J5）；L1_M 因有效牌價下降機械性上升，不是變現改善；Checks Z4；Decisions SL70-*。）以下為 " + _prev)
README_TITLE = V + v21120.README_TITLE[len(v21120.V):]

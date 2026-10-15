# v5.33 (work order docs/workorders/20261012_v5.33.md r1, B section): paid-token calibration from the A-section evidence report
# (docs/reports/20261012_v5.33A_查證.md, PR #40; J7–J14 chat-side judgements, Andy 2026-10-13 06:46「2.2025 基準年世代組合：或改為 Hopper 60／GB200 40　其餘支持照你的建議」).
#   B1 DB_Evidence E302–E324 (A-section N01–N23, verdicts as proposed); SRC_Demand SRC_DEM_049– (A-section §8 proposals, one record per
#      line); SRC_DEM_007 note (J14), SRC_DEM_009 note (N15), SRC_DEM_045 note (N12); DB_Evidence E301 verdict (N13: now sourced).
#   B2 Alloc_In blue inputs, each written only while the cell still holds its v5.32 value: C9 0 -> 0.6, C11 0.4 -> 0, C12 0.2 -> 0
#      (J8: 2025 Hopper 60／GB200 40), E15 6400 -> 11000 (J9); C10 unchanged; G notes appended.
#   B3 Cap_In H7「機隊口徑」inserted before the H-section reading row (no defined name moves; the reading row moves down and is rewritten):
#      spend-route serving GW ÷ Azure multiple (AL_SpendBasis), paid／free capacity (AL_BlendPaid／AL_BlendFree), free÷paid ratio r (model and
#      spend-basis comparison, J10), utilisation correction (J13: point = AL_UtilActual ÷ IF_Util, ceiling = CTL_ProdDerate), fleet paid tokens
#      (point and ceiling), fleet m (point), m floor (ceiling), must-be-true rows (m = 1／0.6／0.3), non-text share comparison (J11, three blue cells).
#   B4 L1_MFleet (external = CTL_Monetize, judgement inside／outside the Gov_Map range) and L1_TokCeiling (external = AL_DPaid, judgement demand ÷ ceiling);
#      Checks M2 (AL_DPaid > L1_TokCeiling) and M3 (L1_MFleet outside the range), WARN, counted in GOV_Warnings.
#   B6 Gov_Map: GM590 (C9:C12) reason J8, GM586／GM587 (C15) range text and reason J9, GM594 (CTL_Monetize) reason, three new rows for the
#      J11 share cells; Decisions X27–X34 and X22／X26 notes.
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v532, so a rebuild never overwrites a later Excel edit.
from copy import copy
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter as L
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY, section
import v518
import v532

VERSION = "20261013_Tokenomics_v5.33"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-13"
V = "v5.33"
DASH = "—"
ANDY = ("chat 端判定（A 段查證報告 PR #40 第 9 節 (a)–(h)，chat 端審查 2026-10-12），Andy 2026-10-13 06:46「2.2025 基準年世代組合：或改為 Hopper 60／GB200 40　"
        "其餘支持照你的建議」；可撤回")
ANDY_R0 = "Andy 2026-10-12 07:43「起草工作單 v5.33『付費 token 數量校準』A 段（查證、不改 Excel），內容依交接檔第 5 節四項」（文字，未改字）"
ANDY_R1 = "Andy 2026-10-13 06:46「2.2025 基準年世代組合：或改為 Hopper 60／GB200 40　其餘支持照你的建議」（文字，未改字）"
REPORT_A = "docs/reports/20261012_v5.33A_查證.md"
EV = {f"N{i:02d}": f"E{301 + i}" for i in range(1, 24)}          # A-section N01–N23 -> E302–E324 (next free number after E301)


def S(n): return f"SRC_DEM_{n:03d}"


# ================================================================== B1: SRC_Demand records (next free number at v5.32: SRC_DEM_049)
_A = f"A 段查證（{REPORT_A}）"
_NBER = "NBER WP 34255《How People Use ChatGPT》（Chatterji 等，OpenAI 研究者合著）https://www.nber.org/system/files/working_papers/w34255/w34255.pdf"
_OAI_STAKE = "OpenAI 公司揭露；融資期間有呈現成長的誘因"
_OAI_MEDIA = "OpenAI 數字經媒體轉述；有呈現成長的誘因"
_SCALE = "OpenAI「Scaling AI for everyone」https://openai.com/index/scaling-ai-for-everyone/"
_WAU_SRC = {
    "2025-03": ("Turley（OpenAI）X 貼文，經 TechCrunch https://techcrunch.com/2025/08/04/openai-says-chatgpt-is-on-track-to-reach-700m-weekly-users/", 2, "二手"),
    "2025-07": ("OpenAI 經 TechCrunch https://techcrunch.com/2025/08/04/openai-says-chatgpt-is-on-track-to-reach-700m-weekly-users/", 2, "二手"),
    "2025-10": ("Altman DevDay 2025（與 SRC_DEM_010 同場合）", 2, "二手"),
    "2026-02": (_SCALE, 1, "一手（已讀）"),
    "2026-07": ("Bloomberg 2026-07-31（v5.32 A 段 U13）", 2, "二手"),
    "2026-09": ("OpenAI DevDay 2026 recap https://openai.com/index/devday-2026-recap/", 1, "一手（已讀）"),
}


def _rec(n, ev, metric, val, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note, lo=None, hi=None):
    return dict(id=S(n), sheet="SRC_Demand", metric=metric, val=val, lo=lo, hi=hi, unit=unit, basis=basis, applies=applies, date=date,
                src=src, grade=grade, stance=stance, stance_note=stance_note, hand=hand, status="Active", ev=EV[ev], s="U-V533", use=use,
                note=f"v5.33 新增（{EV[ev]}，A 段暫編 {ev}）：{note}；{_A}")


_NO_LINK = "（時間序列；不連結模型格）"
SRC_NEW = [
    # S-01／S-02 (N01): NBER table 1 daily messages, two time points
    _rec(49, "N01", "ChatGPT 每日訊息數（7 日平均）", 0.451, "B 則/日", "時點 2024-06-26 止；消費方案（Free／Plus／Pro；排除 Business／Enterprise／Edu、未登入、18 歲以下）",
         "OpenAI ChatGPT", "2025-09-15", _NBER + "（表 1）", 1, "利害關係方", _OAI_STAKE + "；論文期間正值融資", "一手（已讀）", _NO_LINK,
         "採用：SRC_DEM_012（2.5 B，2025-07）的時間序列前一年點；總數「exact」"),
    _rec(50, "N01", "ChatGPT 每日訊息數（7 日平均）", 2.627, "B 則/日", "時點 2025-06-26 止；消費方案（同上）；工作相關占比 47% → 27%",
         "OpenAI ChatGPT", "2025-09-15", _NBER + "（表 1）", 1, "利害關係方", _OAI_STAKE + "；論文期間正值融資", "一手（已讀）", _NO_LINK,
         "採用：與 SRC_DEM_012 一致（18 B／週 ÷ 7＝2.57）；SRC_DEM_012 不改（A 段 1.3 節：2025 全年平均取 2.5 B，2.2–2.7）"),
    # S-03 (N02)
    _rec(51, "N02", "ChatGPT 多媒體類訊息占比", 0.07, "%", "消費方案；2024-07 2% → 2025-06「略超過 7%」；訊息口徑，非營收口徑", "OpenAI ChatGPT", "2025-09-15",
         _NBER + "（第 5.2 節）", 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "Cap_In H7 非文字對照列的唯一一手代理（份額為 Assumed 藍字，不連結）",
         "採用：非文字份額（J11）的唯一一手代理；同文沒有每則 token、方案別占比、用量分布（「不存在於該文」）", lo=0.02, hi=0.07),
    # S-04 (N03) LMSYS; S-05 (N04) WildChat — value column = per-prompt tokens; reply tokens and turns in the basis column (one record per proposal line)
    _rec(52, "N03", "LMSYS-Chat-1M 每則提示 token 數", 69.5, "tok", "2023-04～08；Llama-2 tokenizer；每則回覆 214.5 tok；每對話 2.0 輪（本筆值＝提示；回覆與輪數見口徑）",
         "LMSYS Chatbot Arena（類比，非 ChatGPT）", "2023-09", "arXiv 2309.11998 表 1 https://arxiv.org/pdf/2309.11998", 1, "中立", "LMSYS 學術資料集；無銷售 token 誘因",
         "一手（已讀）", "（Alloc_In C15 組成 (a)(e) 的下界對照；不連結模型格）", "部分採用：2023 Arena 用戶，只作每則 token 下界（a＋e＝284）；Decisions C4 已登錄資料集名稱，本筆補 token 數"),
    _rec(53, "N04", "WildChat 每則用戶 token 數", 295.6, "tok", "2023-04～2024-05；GPT-3.5／GPT-4 API 免費代理；每則回覆 441.3 tok；每對話 2.54 輪；標準差 1,609（本筆值＝用戶；回覆與輪數見口徑）",
         "WildChat（AI2；類比，非 ChatGPT）", "2024-05", "arXiv 2405.01470 表 1 https://arxiv.org/pdf/2405.01470", 1, "中立", "AI2 學術資料集；無銷售 token 誘因",
         "一手（已讀）", "（Alloc_In C15 組成 (a)(e) 對照；不連結模型格）", "部分採用：分布極右偏（sd 為平均 5 倍）的證據；a＋e＝737"),
    # S-06 (N05) reasoning-model daily user share: value = free, hi = Plus (two numbers of one proposal line)
    _rec(54, "N05", "推理模型每日用戶占比（免費／Plus）", 0.07, "%", "GPT-5 發布後（2025-08）；免費 <1% → 7%（本筆值）、Plus 7% → 24%（高欄）；用戶占比，非訊息占比",
         "OpenAI ChatGPT", "2025-08-10", "Altman X https://x.com/sama/status/1954603417252532479，經 Simon Willison https://www.simonwillison.net/2025/Aug/10/sam-altman/", 2,
         "利害關係方", "OpenAI 管理層一手貼文經轉載", "一手貼文經轉載", "（付費 vs 免費用量倍數的線索；不連結模型格）",
         "採用：付費 vs 免費用量差的唯一一手線索（Plus ÷ 免費＝3.4 倍）", hi=0.24),
    # S-07 (N06) context limits: value = Free, hi = Pro reasoning (all plan values in the basis column)
    _rec(55, "N06", "ChatGPT 方案上下文上限", 27000, "tok", "現行（2026-10）；Instant：Free 27K（本筆值）／Go·Plus 54K／Pro 128K；推理模型：Go·Plus 256K／Pro 400K（高欄）；Free／Go 不限文字訊息（受濫用防護）",
         "OpenAI ChatGPT", "2026-10-12", "ChatGPT 定價頁 https://chatgpt.com/pricing/；Help「GPT-6 in ChatGPT」https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt（2026-10-12 讀）", 1,
         "利害關係方", _OAI_STAKE, "一手（已讀）", "（Alloc_In C15 組成 (b) 歷史上下文的物理上限；不連結模型格）",
         "採用：歷史上下文的物理上限；限流不封頂人數口徑的用量倍數 k", hi=400000),
    # S-08 (N07)
    _rec(56, "N07", "ChatGPT 每週網頁搜尋次數", 1, "B 次/週", "「超過」；2025-04；÷ 每週 18 B 則 ≈ 5.6% 訊息觸發搜尋（Derived，期間略不同）", "OpenAI ChatGPT", "2025-04-28",
         "OpenAI（購物功能公告），經 The Decoder https://the-decoder.com/chatgpt-search-hits-a-billion-weekly-queries-as-openai-bets-big-on-ai-powered-shopping/", 2,
         "利害關係方", _OAI_MEDIA, "二手", "（Alloc_In C15 組成 (c) 工具內容的唯一量化依據；不連結模型格）", "採用：工具內容的唯一量化依據；日期由公告推定（二手轉述，未取得一手）"),
    # S-09 (N08) image generation: value = images per week (B), users in the basis column
    _rec(57, "N08", "ChatGPT 圖像生成一週張數", 0.7, "B 張/週", "2025-04 初（尖峰週）；1.3 億用戶；÷ 25 億則／日 ≈ 4% 訊息（Derived）", "OpenAI ChatGPT", "2025-08-04",
         "Lightcap，經 TechCrunch https://techcrunch.com/2025/08/04/openai-says-chatgpt-is-on-track-to-reach-700m-weekly-users/", 2, "利害關係方", _OAI_MEDIA, "二手",
         "（非文字份額對照；不連結模型格）", "部分採用：尖峰週，非平均"),
    # S-10 (N10)
    _rec(58, "N10", "OpenAI 每日產生字數", 100, "B 字/日", "2024-02；含 API；≈133 B tok（0.75 字／token）；÷ 2024-06 每日 4.51 億則 → 每則可見輸出約 300 tok（Derived，上界含 API）",
         "OpenAI", "2025-06", "Altman X 貼文，經 Interconnects https://www.interconnects.ai/p/people-use-ai-more-than-you-think", 2, "利害關係方", _OAI_MEDIA, "二手",
         "（Alloc_In C15 組成 (e) 可見輸出對照；不連結模型格）", "部分採用：2024 時點；二手轉述，未取得一手"),
    # S-11 (N11) Epoch poll: value = used ChatGPT last week, hi slot not a range -> subscriber share in the basis column
    _rec(59, "N11", "美國成人上週用過 ChatGPT 的比例", 0.35, "%", "2025-11／12 調查 5,660 人；同調查：付費 AI 訂閱 <10%、OpenAI 訂閱者占美國成人 4.6%（4.6 ÷ 35＝13% 的美國週用戶付費，Derived）",
         "ChatGPT（美國）", "2026-01-21", "Epoch AI https://epochai.substack.com/p/polling-on-ai-usage；https://epoch.ai/data/polling", 1, "中立", "Epoch 中立調查",
         "一手（已讀）", "（人數口徑付費率對照；美國高於全球 5.7%；不連結模型格）", "採用：中立調查；無每用戶訊息數、無付費／免費用量差（CSV 本輪未下載）"),
    # S-12 (N13)
    _rec(60, "N13", "Codex 每週用戶", 8, "百萬", "時點 2026-07-14；序列 2026-02-05 1M → 03-05 2M → 04-21 4M → 05-31 5M → 07-14 8M", "OpenAI Codex", "2026-07-15",
         "Altman／Sottiaux X，經 Fortune，彙整於 https://fourweekmba.com/ai-ai-openai-codex-7-million-weekly-users-harness-war/", 2, "利害關係方", _OAI_MEDIA, "二手",
         "（程式代理用戶序列；SRC_DEM_021 為 2026-02 點；不連結模型格）", "採用：解決 v5.32 E301「待查」（8M 有出處：Altman 2026-07-14）；彙整站轉述 Fortune，未取得一手"),
    # S-13 (N14) forward-looking compute: value = inference GW, hi = training GW is not a range -> basis column
    _rec(61, "N14", "OpenAI 專用推論算力（前瞻承諾）", 3, "GW", "2026-02-27 起（前瞻，非 2025 運轉量）；另 2 GW 訓練（Vera Rubin）；口徑未明（IT／設施）；推論 ÷ 總＝60%",
         "OpenAI", "2026-02-27", _SCALE + "（與 SRC_DEM_019 同文）", 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "（算力序列；不入 2025 平均；不連結模型格）",
         "部分採用：登錄為前瞻承諾，不入 2025 平均"),
    # S-14 (N16／N17) ARR
    _rec(62, "N16", "OpenAI ARR", 50, "$B/年", "時點 2026-10；OpenAI 自身營收口徑（只記自身份額，不含經雲端夥伴銷售）；高欄 70＝先前報導的毛額口徑（gross up，與 Anthropic 可比）",
         "OpenAI", "2026-10-08", "Axios https://www.axios.com/2026/10/08/openai-50-billion-arr-anthropic-revenue-accounting；"
         "Axios 2026-09-29 https://www.axios.com/2026/09/29/scoop-openais-annual-recurring-revenue-nears-70b", 2, "利害關係方", "雙方（OpenAI、Anthropic）經媒體；匿名消息來源",
         "二手", "（J14：SRC_DEM_007 營收口徑的佐證；不連結模型格）", "採用：營收口徑（毛額／淨額）證據；SRC_DEM_007 13.07 為 OpenAI 自身營收口徑（J14）；匿名消息來源，未取得一手", hi=70),
    # S-15–S-20 (N20) WAU series, one record per time point
    *[_rec(63 + i, "N20", "ChatGPT 週活用戶數", v, "百萬", f"時點 {d}；每週活躍用戶" + ("；「超過」" if d == "2026-07" else ""), "OpenAI ChatGPT", dd,
           _WAU_SRC[d][0], _WAU_SRC[d][1], "利害關係方", _OAI_STAKE if _WAU_SRC[d][1] == 1 else _OAI_MEDIA, _WAU_SRC[d][2],
           "（人數口徑付費率的分母；不連結模型格）", f"採用：WAU 序列第 {i + 1} 點（v5.32 U18 未登錄）")
      for i, (d, dd, v) in enumerate([("2025-03", "2025-08-04", 500), ("2025-07", "2025-08-04", 700), ("2025-10", "2025-10-06", 800),
                                       ("2026-02", "2026-02-27", 900), ("2026-07", "2026-07-31", 1000), ("2026-09", "2026-10-06", 1200)])],
]
SRC_LAST_ID = SRC_NEW[-1]["id"]          # SRC_DEM_068


def src_new_records():
    return SRC_NEW


J14_NOTE = ("13.07 為 OpenAI 自身營收口徑（不含 Azure OpenAI Service 轉售），與分母的 OpenAI 自身 Azure 帳單口徑一致；待一手確認"
            f"（v5.33 J14；Reuters／Axios 2026-10-08：OpenAI 年化數字不含經雲端夥伴銷售，{S(62)}、{EV['N16']}）")
SRC_UPD = {
    "SRC_DEM_007": ("SRC_Demand", {"W": ("+", f" ｜v5.33 J14：{J14_NOTE}")}),
    "SRC_DEM_009": ("SRC_Demand", {"W": ("+", f" ｜v5.33（{EV['N15']}，N15 部分採用）：Altman 2025-10-13「2025 年底超過 2 GW」（YouTube 訪談，經 Parekh 轉述）與 1.9 一致；口徑未明")}),
    "SRC_DEM_045": ("SRC_Demand", {"W": ("+", f" ｜v5.33（{EV['N12']}，N12 部分採用）：同文：Enterprise 每週訊息一年 ×8、每人 +30%、前沿公司每席 2 倍")}),
}


def src_update(wb):
    n = 0; log = []
    for sid, (sh, fields) in SRC_UPD.items():
        ws = wb[sh]
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row is None: log.append(f"{sid}: record not found"); continue
        for col, spec in fields.items():
            if v518._apply(ws[f"{col}{row}"], spec): n += 1
            else: log.append(f"{sid}!{col}: kept (already applied)")
    return n, log


# ================================================================== B2: Alloc_In blue inputs (Excel-owned; written only while at the v5.32 value)
LAB_MIX = {"C9": "服務世代組合：Hopper", "C10": "服務世代組合：GB200", "C11": "服務世代組合：GB300", "C12": "服務世代組合：VR200"}
LAB_TOK = "每則提示 token 數"
IN_UPD = [  # (label, column, old, new, J)
    ("服務世代組合：Hopper", "C", 0, 0.6, "J8"),
    ("服務世代組合：GB300", "C", 0.4, 0, "J8"),
    ("服務世代組合：VR200", "C", 0.2, 0, "J8"),
    (LAB_TOK, "E", 6400, 11000, "J9"),
]
NOTE_J8 = " ｜v5.33 J8：2025 基準年實際組合（VR200 2025 未出貨；h_alloc_mix_2025 情境轉為基準：Hopper 60／GB200 40／GB300 0／VR200 0；低／高區間不改）"
NOTE_J9 = " ｜v5.33 J9：高端 6,400 → 11,000（A 段 1.2 節五組成高端 11,300 取整；基準 4,000 與低端 2,000 不改；不拆成多個輸入）"


def _row_by_label(ws, lab):
    rows = [r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == lab]
    assert len(rows) == 1, (lab, rows)
    return rows[0]


def inputs_update(wb):
    ws = wb["Alloc_In"]; log = []
    for lab, col, old, new in [(a, b, c, d) for a, b, c, d, _ in IN_UPD]:
        r = _row_by_label(ws, lab); c = ws[f"{col}{r}"]
        if c.value == old and type(c.value) is not bool:
            c.value = new; c.font = copy(F_IN); c.fill = PatternFill(fill_type=None)
            log.append(f"Alloc_In!{col}{r}: {old!r} -> {new!r} (v5.33 {'J9' if lab == LAB_TOK else 'J8'})")
    for lab in ("服務世代組合：Hopper", "服務世代組合：GB300", "服務世代組合：VR200"):
        r = _row_by_label(ws, lab)
        if v518._append_text(ws[f"G{r}"], NOTE_J8): log.append(f"Alloc_In!G{r}: note appended (v5.33 J8)")
    r = _row_by_label(ws, LAB_TOK)
    if v518._append_text(ws[f"G{r}"], NOTE_J9): log.append(f"Alloc_In!G{r}: note appended (v5.33 J9)")
    return log


# ================================================================== B3: Cap_In H7 (inserted before the H-section reading row; nothing named moves)
FMT = {"GW": "0.0000", "M tok/GW/年": "#,##0", "x": "0.000", "M tok/年": "#,##0", "%": "0.0%"}
LAB = dict(nontext="非文字服務份額（圖像、語音、影片；只扣訂閱分子；J11 對照用）")
# (key, label, unit, C, D, E, tag, note); key None = sub-header. {k} = this section's rows; {P_k} = v5.32 H-section rows.
# D＝m 低端（token 取高：Azure 倍數取低、實際利用率取高、非文字份額取高）；E＝m 高端（反之）。
# Rows that read AL_BlendPaid／AL_BlendFree carry the Alloc guard (text「SLO 不可達」when a generation in the mix cannot serve, e.g. Hopper at Serving!C18 0.7).
SPEC = [
    (None, "H7. 機隊口徑（v5.33；工作單 v5.33 r1 B3，J7、J10、J11、J13）：支出路線服務 GW → 機隊付費 token（點估計與上限）→ 機隊 m、m 下限、「必須為真」、非文字對照"),
    ("gw_az", "支出路線服務 GW（經 Azure 計價倍數）＝AL_ServeGWSpend ÷ AL_SpendBasis", "GW", "=AL_ServeGWSpend/AL_SpendBasis",
     "=AL_ServeGWSpend/AL_SpendBasis_Lo", "=AL_ServeGWSpend/AL_SpendBasis_Hi", "Derived（輸入 Assumed）",
     "Alloc 第 61 列（SRC_DEM_018 ÷ 世代組合持有成本）÷ Alloc_In C23（2；m 低端取 1.5＝GW 取高、m 高端取 3）"),
    ("cap_paid", "付費每 GW 年產能（世代組合後；Alloc 第 24 列，已含 IF_Util）", "M tok/GW/年", "=AL_BlendPaid", "=AL_BlendPaid", "=AL_BlendPaid", "Derived",
     "AL_BlendPaid；改世代組合（J8）後自動更新"),
    ("cap_free", "免費每 GW 年產能（世代組合後；Alloc 第 25 列，已含 IF_Util）", "M tok/GW/年", "=AL_BlendFree", "=AL_BlendFree", "=AL_BlendFree", "Derived", "AL_BlendFree"),
    ("r_model", "免費 ÷ 付費 token 比 r（模型）＝AL_DFree ÷ AL_DPaid", "x", "=AL_DFree/AL_DPaid", "=AL_DFree/AL_DPaid", "=AL_DFree/AL_DPaid", "Derived",
     "Alloc 第 10 ÷ 第 9 列（Alloc_In C16 免費占比 0.6 下約 0.57）"),
    ("r_spend", "對照：r 支出口徑換算＝IF_FreeShare × 付費產能倍數 ÷（1 − IF_FreeShare）（J10；A 段 P09 3.22）", "x",
     "=IF(AND(ISNUMBER(C{cap_paid}),ISNUMBER(C{cap_free})),IF_FreeShare*(C{cap_free}/C{cap_paid})/(1-IF_FreeShare),\"SLO 不可達\")", "=IF(AND(ISNUMBER(D{cap_paid}),ISNUMBER(D{cap_free})),IF_FreeShare*(D{cap_free}/D{cap_paid})/(1-IF_FreeShare),\"SLO 不可達\")",
     "=IF(AND(ISNUMBER(E{cap_paid}),ISNUMBER(E{cap_free})),IF_FreeShare*(E{cap_free}/E{cap_paid})/(1-IF_FreeShare),\"SLO 不可達\")", "Derived（支出口徑 Interested-party）",
     "免費推論支出占比 IF_FreeShare（SRC_DEM_005 ÷ 004）換算為 token 比：付費每 token 用的算力＝免費的（AL_BlendFree ÷ AL_BlendPaid）倍；只作對照，Alloc_In C16 不改"),
    ("corr_pt", "利用率修正（點估計）＝AL_UtilActual ÷ IF_Util（J13）", "x", "=AL_UtilActual/IF_Util", "=AL_UtilActual_Hi/IF_Util", "=AL_UtilActual_Lo/IF_Util",
     "Derived（輸入 Assumed）", "Alloc 第 22 列已含 IF_Util（0.6），換成實際利用率 × 生產折減（Alloc_In C24，0.35；m 低端取 0.4、高端取 0.3）"),
    ("corr_cap", "利用率修正（上限）＝付費產能比（生產折減 CTL_ProdDerate 重解 SLO 後 ÷ 基準；AL_ProdRatioPaid；J13；v6.0 D7-2）", "x", "=AL_ProdRatioPaid", "=AL_ProdRatioPaid", "=AL_ProdRatioPaid", "Derived",
     "最大產出：生產折減下重解 SLO 的付費產能 ÷ 基準付費產能（Alloc H 節；2025 組合約 0.712），取代 v5.36 的線性 CTL_ProdDerate（0.85）；Alloc 第 22 列已含 IF_Util，只再乘此比"),
    ("tok_fleet", "機隊付費 token（點估計）＝服務 GW × 修正 ÷（1 ÷ 付費產能 ＋ r ÷ 免費產能）", "M tok/年",
     "=IF(AND(ISNUMBER(C{cap_paid}),ISNUMBER(C{cap_free}),ISNUMBER(C{r_model})),C{gw_az}*C{corr_pt}/(1/C{cap_paid}+C{r_model}/C{cap_free}),\"SLO 不可達\")", "=IF(AND(ISNUMBER(D{cap_paid}),ISNUMBER(D{cap_free}),ISNUMBER(D{r_model})),D{gw_az}*D{corr_pt}/(1/D{cap_paid}+D{r_model}/D{cap_free}),\"SLO 不可達\")",
     "=IF(AND(ISNUMBER(E{cap_paid}),ISNUMBER(E{cap_free}),ISNUMBER(E{r_model})),E{gw_az}*E{corr_pt}/(1/E{cap_paid}+E{r_model}/E{cap_free}),\"SLO 不可達\")", "Derived", "r 取模型（第 r 列）；A 段 3.2 節 2025 組合變體約 8.2 × 10⁹"),
    ("tok_fleet_rs", "對照：機隊付費 token（點估計，r 取支出口徑）", "M tok/年",
     "=IF(AND(ISNUMBER(C{cap_paid}),ISNUMBER(C{cap_free}),ISNUMBER(C{r_spend})),C{gw_az}*C{corr_pt}/(1/C{cap_paid}+C{r_spend}/C{cap_free}),\"SLO 不可達\")", "=IF(AND(ISNUMBER(D{cap_paid}),ISNUMBER(D{cap_free}),ISNUMBER(D{r_spend})),D{gw_az}*D{corr_pt}/(1/D{cap_paid}+D{r_spend}/D{cap_free}),\"SLO 不可達\")",
     "=IF(AND(ISNUMBER(E{cap_paid}),ISNUMBER(E{cap_free}),ISNUMBER(E{r_spend})),E{gw_az}*E{corr_pt}/(1/E{cap_paid}+E{r_spend}/E{cap_free}),\"SLO 不可達\")", "Derived", "免費 token 較多時付費 token 較少"),
    ("tok_ceil", "機隊付費 token 上限（上限讀法）＝服務 GW × 付費產能比 ÷（1 ÷ 付費產能 ＋ r ÷ 免費產能）　→ L1_TokCeiling", "M tok/年",
     "=IF(AND(ISNUMBER(C{cap_paid}),ISNUMBER(C{cap_free}),ISNUMBER(C{r_model}),ISNUMBER(C{corr_cap})),C{gw_az}*C{corr_cap}/(1/C{cap_paid}+C{r_model}/C{cap_free}),\"SLO 不可達\")", "=IF(AND(ISNUMBER(D{cap_paid}),ISNUMBER(D{cap_free}),ISNUMBER(D{r_model}),ISNUMBER(D{corr_cap})),D{gw_az}*D{corr_cap}/(1/D{cap_paid}+D{r_model}/D{cap_free}),\"SLO 不可達\")",
     "=IF(AND(ISNUMBER(E{cap_paid}),ISNUMBER(E{cap_free}),ISNUMBER(E{r_model}),ISNUMBER(E{corr_cap})),E{gw_az}*E{corr_cap}/(1/E{cap_paid}+E{r_model}/E{cap_free}),\"SLO 不可達\")", "Derived", "A 段 3.2 節約 12.0 × 10⁹；上限 ÷ 需求路線＝L1_ScaleServe ÷（L1_GapSpendBasis × L1_GapUtil）"),
    ("m_fleet", "機隊 m（點估計）＝營收 ÷（機隊付費 token × 混合有效單價）　→ L1_MFleet", "x",
     "=IF(ISNUMBER(C{tok_fleet}),SRC_DEM_007*1000000000/(C{tok_fleet}*C{P_price}),\"SLO 不可達\")", "=IF(ISNUMBER(D{tok_fleet}),SRC_DEM_007*1000000000/(D{tok_fleet}*D{P_price}),\"SLO 不可達\")", "=IF(ISNUMBER(E{tok_fleet}),SRC_DEM_007*1000000000/(E{tok_fleet}*E{P_price}),\"SLO 不可達\")",
     "Derived", "分子同 H1（毛額，SRC_DEM_007）；單價同 H4；A 段 2025 組合約 0.81"),
    ("m_fleet_rs", "對照：機隊 m（點估計，r 取支出口徑）", "x", "=IF(ISNUMBER(C{tok_fleet_rs}),SRC_DEM_007*1000000000/(C{tok_fleet_rs}*C{P_price}),\"SLO 不可達\")",
     "=IF(ISNUMBER(D{tok_fleet_rs}),SRC_DEM_007*1000000000/(D{tok_fleet_rs}*D{P_price}),\"SLO 不可達\")", "=IF(ISNUMBER(E{tok_fleet_rs}),SRC_DEM_007*1000000000/(E{tok_fleet_rs}*E{P_price}),\"SLO 不可達\")", "Derived", ""),
    ("m_floor", "m 下限（上限讀法）＝營收 ÷（機隊付費 token 上限 × 混合有效單價）", "x", "=IF(ISNUMBER(C{tok_ceil}),SRC_DEM_007*1000000000/(C{tok_ceil}*C{P_price}),\"SLO 不可達\")",
     "=IF(ISNUMBER(D{tok_ceil}),SRC_DEM_007*1000000000/(D{tok_ceil}*D{P_price}),\"SLO 不可達\")", "=IF(ISNUMBER(E{tok_ceil}),SRC_DEM_007*1000000000/(E{tok_ceil}*E{P_price}),\"SLO 不可達\")", "Derived", "A 段 2025 組合約 0.56；m 不可能低於此值（除非 C23、C24 改）"),
    (None, "「必須為真」：m 分別＝1／0.6／0.3 時所需的付費 token（＝營收 ÷（m × 單價））；本三列 C＝所需 token（M tok/年）、D＝÷ 需求路線 AL_DPaid 的倍數、E＝對上限（基準欄）判讀"),
    ("need_1", "m＝1 所需付費 token", "M tok/年", "=SRC_DEM_007*1000000000/(1*C{P_price})", "=C{need_1}/AL_DPaid",
     '=IF(ISNUMBER(C{tok_ceil}),IF(C{need_1}<=C{tok_ceil},"低於上限（m＝1 未被排除）","高於上限（m＝1 被物理上限排除）"),"SLO 不可達")', "Derived", "D 欄＝倍數（x）、E 欄＝文字"),
    ("need_06", "m＝0.6 所需付費 token", "M tok/年", "=SRC_DEM_007*1000000000/(0.6*C{P_price})", "=C{need_06}/AL_DPaid",
     '=IF(ISNUMBER(C{tok_ceil}),IF(C{need_06}<=C{tok_ceil},"低於上限（m＝0.6 未被排除）","高於上限（m＝0.6 被物理上限排除）"),"SLO 不可達")', "Derived", "D 欄＝倍數（x）、E 欄＝文字"),
    ("need_03", "m＝0.3 所需付費 token", "M tok/年", "=SRC_DEM_007*1000000000/(0.3*C{P_price})", "=C{need_03}/AL_DPaid",
     '=IF(ISNUMBER(C{tok_ceil}),IF(C{need_03}<=C{tok_ceil},"低於上限（m＝0.3 未被排除）","高於上限（m＝0.3 被物理上限排除）"),"SLO 不可達")', "Derived", "D 欄＝倍數（x）、E 欄＝文字"),
    (None, "非文字對照（J11）：訂閱營收中的非文字服務份額（Assumed 0.05／0.10／0.20）只從訂閱分子扣除後的 m；不進 H1 分子，只作顯示"),
    ("nontext", LAB["nontext"], "%", 0.10, 0.20, 0.05, "Assumed",
     f"藍字三格（登錄 Gov_Map）：基準 0.10、m 低端 0.20（扣得多）、m 高端 0.05；唯一一手代理＝{S(51)}（NBER 多媒體類訊息 7%，訊息口徑）；Deep Research／代理不扣（文字 token）"),
    ("m_sub_ex", "扣除非文字後 — 訂閱路線隱含 m（模型 token）", "x", "=C{P_rev_sub}*(1-C{nontext})*1000000000/(C{P_tok_chat}*C{P_price})",
     "=D{P_rev_sub}*(1-D{nontext})*1000000000/(D{P_tok_chat}*D{P_price})", "=E{P_rev_sub}*(1-E{nontext})*1000000000/(E{P_tok_chat}*E{P_price})", "Derived",
     "H5 訂閱路線 ×（1 − 份額）；各欄用該欄的 H1／H3 值"),
    ("m_all_ex", "扣除非文字後 — 合併隱含 m（模型 token）", "x", "=(C{P_rev_sub}*(1-C{nontext})+C{P_rev_api})*1000000000/(C{P_tok_paid}*C{P_price})",
     "=(D{P_rev_sub}*(1-D{nontext})+D{P_rev_api})*1000000000/(D{P_tok_paid}*D{P_price})", "=(E{P_rev_sub}*(1-E{nontext})+E{P_rev_api})*1000000000/(E{P_tok_paid}*E{P_price})",
     "Derived", "L1_MImplied 的分子只扣訂閱部分；API 不扣（已按 token 計價）"),
]
NOTE_END = ("讀法（v5.33 改寫）：(1) 需求路線 L1_MImplied > 1 的主因不在每則 token 與付費占比（A 段 1.1、1.2 各只能放大 ≤1.8、≤1.4 倍），而在需求路線沒數到的機隊產出"
            "（H7：支出路線服務 GW × 實際產出）；(2) 對回本條件有意義的是機隊 m（L1_MFleet，點估計）與 m 下限（上限讀法）；(3) m < 1 時回本條件改為 "
            "L ≥ L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m），例如 m＝0.6 時需 L ≥ 0.49，在 L1_GapUtil 的實際利用率下需 L ≥ 0.72，超過 L 類比區間上緣 0.70（照 v5.32）。"
            "外部分母（H3 (ii)）的 Epoch 區間跨一個數量級；程式代理對照列（H6）不進合併。追蹤規則（J5／X24）：每次升版檢查 OpenAI、Anthropic 的新揭露，另加季度檢查。")
BLUE = {("nontext", "C"), ("nontext", "D"), ("nontext", "E")}
ROWS = {}


def cap_in_h7(wb, h32):
    """Rows of H7 start where v5.32 wrote its reading row (h32['end']); that row is cleared and rewritten after H7 (no defined name there)."""
    ws = wb["Cap_In"]
    r0 = h32["end"]
    assert str(ws[f"A{r0}"].value).startswith("讀法") and ws.max_row == r0, (r0, ws.max_row)
    ws[f"A{r0}"].value = None
    P = {f"P_{k}": v for k, v in h32["rows"].items()}
    r = r0
    for item in SPEC:
        if item[0] is not None: ROWS[item[0]] = r
        r += 1
    r = r0
    for item in SPEC:
        if item[0] is None:
            put(ws, f"A{r}", item[1], F_BOLD); r += 1; continue
        key, lab, unit, c, d, e, tag, note = item
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        fmt = FMT.get(unit)
        for col, v in (("C", c), ("D", d), ("E", e)):
            if isinstance(v, str) and v.startswith("="):
                v = v.format(**ROWS, **P)
                font = F_LINK if v in ("=AL_BlendPaid", "=AL_BlendFree", "=CTL_ProdDerate", "=AL_ProdRatioPaid") else F_CALC
                put(ws, f"{col}{r}", v, font, fmt=("0.00" if key.startswith("need_") and col == "D" else fmt),
                    fill=FILL_KEY if key in ("m_fleet", "tok_ceil", "m_floor") and col == "C" else None)
            elif isinstance(v, (int, float)):
                assert (key, col) in BLUE, (key, col)
                put(ws, f"{col}{r}", v, F_IN, fmt=fmt)
            else:
                put(ws, f"{col}{r}", v, F_CALC)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True)
        r += 1
    put(ws, f"A{r}", NOTE_END, F_NOTE)
    return dict(start=r0, rows=dict(ROWS), end=r)


# ================================================================== B6: Gov_Map rows for the three J11 blue cells (gov.gm_append_c; appended when absent)
def gov_map_rows(wb):
    if not ROWS: return []
    ws = wb["Cap_In"]; sc = "切片三（v5.33 機隊口徑）"; r = ROWS["nontext"]; lab = ws[f"A{r}"].value
    assert lab == LAB["nontext"], (r, lab)
    reason = (f"v5.33 J11：A 段 4.2 節 Assumed 0.05／0.10／0.20（唯一一手代理 {S(51)}：NBER 多媒體類訊息 7%，訊息口徑非營收口徑）；只從訂閱分子扣除、只作顯示，不進 H1；"
              "要讓訂閱 m 降到 1 以下需 69%（A 段 4.2 節）")
    return [
        {'scope': sc, 'sheet': 'Cap_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '基準', 'src': S(51),
         'rel': f'類比：NBER 多媒體類訊息占比（{EV["N02"]}）', 'dec': 'X31', 'lo': f'=Cap_In!E{r}', 'hi': f'=Cap_In!D{r}',
         'rtext': '0.05–0.20（A 段 4.2 節；D 欄＝m 低端 0.20、E 欄＝m 高端 0.05）', 'reason': reason, 'retag': '', 'seg': '無'},
        {'scope': sc, 'sheet': 'Cap_In', 'cell': f'D{r}:E{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '低／高', 'src': '',
         'rel': '', 'dec': 'X31', 'lo': None, 'hi': None, 'rtext': f'C{r} 的 m 低端（0.20）、m 高端（0.05）端點', 'reason': reason, 'retag': '', 'seg': '無'},
    ]


# ================================================================== B6: Gov_Map judgement updates on existing rows (guarded)
GM594_TAIL = " ｜v5.33：機隊 m 點估計約 0.8（2025 Hopper 組合）、下限約 0.56；需求路線 m > 1 不是分母偏低的證據；基準暫不改"
GM590_TAIL = " ｜v5.33 J8：2025 基準年實際組合改為 Hopper 60／GB200 40／GB300 0／VR200 0（VR200 2025 未出貨；h_alloc_mix_2025 情境轉為基準；Andy 2026-10-13）；低／高區間不改"
GM586_TAIL = " ｜v5.33 J9：高端 6,400 → 11,000（A 段 1.2 節五組成高端 11,300 取整；基準與低端不改；不拆成多個輸入）"
GM586_RANGE = ("2,000–6,400（X14 (l)：下限 Robonomics 假設上緣，上限 OpenRouter 實測 6,400，E261）",
               "2,000–11,000（v5.33 J9：下限 Robonomics 假設上緣（X14 (l)），上限 A 段五組成高端 11,300 取整；原上限 OpenRouter 實測 6,400，E261）")


def _gm_row(ws, sheet, cell):
    rows = [r for r in range(5, ws.max_row + 1) if (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sheet, cell)]
    assert len(rows) == 1, (sheet, cell, rows)
    return rows[0]


def gov_update(ws, append_text):
    n = 0
    r = _gm_row(ws, "Cap_In", "C64"); assert ws[f"A{r}"].value == "GM594"
    n += append_text(ws[f"N{r}"], GM594_TAIL)
    r = _gm_row(ws, "Alloc_In", "C9:C12")
    n += append_text(ws[f"N{r}"], GM590_TAIL)
    for cell in ("C15", "D15:E15"):
        r = _gm_row(ws, "Alloc_In", cell)
        n += append_text(ws[f"N{r}"], GM586_TAIL)
        if cell == "C15" and ws[f"M{r}"].value == GM586_RANGE[0]:
            ws[f"M{r}"].value = GM586_RANGE[1]; n += 1
    return n


# ================================================================== B4: L1 rows (appended after every existing L1 row; no L1 name moves)
READ_FLEET = ("兩種讀法（J7）：(i) 點估計＝支出路線服務 GW（SRC_DEM_018 ÷ 持有成本 ÷ Azure 倍數 AL_SpendBasis）× 實際利用率修正（AL_UtilActual ÷ IF_Util），得機隊 m；"
              "(ii) 上限＝同一 GW × CTL_ProdDerate 的最大產出，得 m 下限（L1_TokCeiling 列）。對回本條件有意義的是機隊 m，不是需求路線的 L1_MImplied。"
              "(2) m < 1 時回本條件改為 L ≥ L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m），例如 m＝0.6 時需 L ≥ 0.49，在 L1_GapUtil 的實際利用率下需 L ≥ 0.72，超過 L 類比區間上緣 0.70")
READ_CEIL = ("上限不是獨立證據：A 段恆等式 上限 ÷ 需求路線＝L1_ScaleServe ÷（L1_GapSpendBasis × L1_GapUtil），由 Alloc_In C23（Azure 倍數）、C24（實際利用率）決定。"
             "需求路線（AL_DPaid）超過上限即物理上不可能（Checks M2）；m＝1／0.6／0.3 所需的付費 token 對上限的判讀見 Cap_In H7「必須為真」三列")


def l1_rows_new():
    rm, rc = ROWS["m_fleet"], ROWS["tok_ceil"]
    return [
        ("MFleet", "機隊變現率 m — 點估計（支出路線服務 GW × 實際產出）", "OpenAI 2025；毛額營收 SRC_DEM_007 ÷（機隊付費 token（點估計）× Cap_In 第 31 列層級組合混合有效單價）；v5.33 J7 (i)",
         f"=Cap_In!$C${rm}", f"=Cap_In!$D${rm}", f"=Cap_In!$E${rm}", "x",
         "低＝token 取高（Azure 倍數 1.5、實際利用率 0.4）；高＝token 取低（3、0.3）；營收與單價單值", READ_FLEET,
         "推論支出 SRC_DEM_018、Azure 計價倍數、實際利用率 × 生產折減、世代組合、免費 ÷ 付費 token 比", "Azure 倍數、實際利用率：Assumed（Alloc_In C23、C24）",
         "CTL_Monetize（模型假設；Gov_Map GM594 區間）", "=CTL_Monetize", "=CTL_Monetize", "CTL_Monetize；AL_ServeGWSpend；AL_SpendBasis；AL_UtilActual；AL_BlendPaid；AL_BlendFree；IF_PriceRef_*",
         f"Cap_In 第 {rm} 列", "分母為帳單反推的機隊產出，非實測 token；OpenAI 未揭露 2025 實際運轉推論 GW 與 ChatGPT token 數"),
        ("TokCeiling", "機隊付費 token 上限（上限讀法：支出路線服務 GW × 最大產出）", "OpenAI 2025；支出路線服務 GW ÷ Azure 倍數 × CTL_ProdDerate ÷（1 ÷ AL_BlendPaid ＋ r ÷ AL_BlendFree）；v5.33 J7 (ii)",
         f"=Cap_In!$C${rc}", f"=Cap_In!$E${rc}", f"=Cap_In!$D${rc}", "M tok/年",
         "低＝Azure 倍數取高（3，GW 取低）；高＝取低（1.5）", READ_CEIL,
         "推論支出 SRC_DEM_018、Azure 計價倍數、世代組合、CTL_ProdDerate、免費 ÷ 付費 token 比", "Azure 倍數：Assumed（Alloc_In C23）",
         "AL_DPaid（需求路線付費 token；Alloc 第 9 列）", "=AL_DPaid", "=AL_DPaid", "AL_DPaid；AL_ServeGWSpend；AL_SpendBasis；CTL_ProdDerate；AL_BlendPaid；AL_BlendFree",
         f"Cap_In 第 {rc} 列", "上限由 C23、C24 決定，不是獨立證據"),
    ]


def l1_judge(wb):
    """L1 P column: L1_MFleet = inside／outside the Gov_Map range of CTL_Monetize (as v5.32); L1_TokCeiling = demand route ÷ ceiling."""
    ws = wb["L1"]; lo, hi = v532._gm_ref(wb); out = []
    r = int(wb.defined_names["L1_MFleet"].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == "L1_MFleet"
    rng = f'"落在 "&TEXT({lo},"0.0")&"–"&TEXT({hi},"0.0")&" 區間'
    ws[f"P{r}"].value = f'=IF(ISNUMBER(D{r}),IF(AND(D{r}>={lo},D{r}<={hi}),{rng}內",{rng}外"),"推算值非數字（本情境）")'
    out.append(r)
    r = int(wb.defined_names["L1_TokCeiling"].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == "L1_TokCeiling"
    ws[f"P{r}"].value = (f'=IF(AND(ISNUMBER(D{r}),ISNUMBER(M{r})),"需求路線 ÷ 上限＝"&TEXT(M{r}/D{r},"0.00")&IF(M{r}>D{r},"（需求超過物理上限）","（需求在上限內）"),'
                         f'"推算值非數字（本情境）")')
    out.append(r)
    return out


# ================================================================== B4: Checks M2／M3 (WARN; appended after M1, counted in GOV_Warnings)
def checks_m23(wb):
    ws = wb["Checks"]
    r1 = next(r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value == "M1")
    assert ws[f"A{r1 + 1}"].value is None
    lo, hi = v532._gm_ref(wb)
    rows = [
        ("M2", "需求路線付費 token AL_DPaid 超過機隊付費 token 上限 L1_TokCeiling：1＝超過（物理上不可能）", f"=IF(AND(ISNUMBER(AL_DPaid),ISNUMBER(L1_TokCeiling)),IF(AL_DPaid>L1_TokCeiling,1,0),0)",
         "AL_DPaid；L1_TokCeiling（Cap_In H7 上限讀法）；依現值不觸發（v5.33 B4）"),
        ("M3", "L1_MFleet（機隊 m，點估計）基準落在 CTL_Monetize 的 Gov_Map 區間外：1＝區間外", f"=IF(ISNUMBER(L1_MFleet),IF(OR(L1_MFleet<{lo},L1_MFleet>{hi}),1,0),0)",
         f"L1_MFleet；{lo.replace('$', '')}／{hi.replace('$', '')}（GM594 低、高）；依錨點 0.81 不觸發（v5.33 B4）"),
    ]
    ref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    for i, (cid, lab, f, note) in enumerate(rows):
        r = r1 + 1 + i
        put(ws, f"A{r}", cid); put(ws, f"B{r}", lab, wrap=True); put(ws, f"C{r}", "WARN"); put(ws, f"D{r}", f, F_CALC, fmt="0"); put(ws, f"E{r}", note, F_NOTE)
        if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "WARN 合計（含 H3、K1、M1–M3）"
    ws[f"A{r1 - 2}"].value = "M. 變現率 m 追蹤檢查（工作單 v5.32 r1 B3，J4 (a)；v5.33 r1 B4 加 M2、M3）：M1–M3 為 WARN 計入 GOV_Warnings（不阻擋）"
    return [r1 + 1, r1 + 2]


# ================================================================== B1: DB_Evidence E302–E324 (17 columns A..Q; layout of v531／v532)
def _ev(n, claim, src, tag, param, cur, new, verdict, note, sids, affected, grade, stance):
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, f"{note}｜A 段暫編 {n}｜{ANDY}｜讀取者：CC（A 段，{REPORT_A}）",
            "已處理", sids, DASH, affected, grade, stance]


SECOND = "二手轉述，未取得一手"
MF = "L1_MFleet、L1_TokCeiling（v5.33 新列）"
EVIDENCE_V533 = [
    _ev("N01", "ChatGPT 每日訊息 7 日平均：2024-06 451M、2025-06 2,627M；工作占比 47% → 27%；消費方案口徑", _NBER + "（表 1）", "Verified／1 級",
        "SRC_DEM_012 的時間序列前後點", "2.5 B（2025-07）", "0.451／2.627 B", f"採用（X27）：新登錄 {S(49)}、{S(50)}（兩時點各一筆）；SRC_DEM_012 不改（2025 全年平均取 2.5 B，2.2–2.7）",
        "一手已讀；論文期間正值融資；只含消費方案", f"{S(49)}；{S(50)}；SRC_DEM_012", "AL_DChat（若改全年平均；本版未改）", "1", "利害關係方"),
    _ev("N02", "NBER 多媒體類訊息 2% → 7%；無每則 token、無方案別占比、無分布", _NBER + "（第 5.2 節、第 3 節）", "Verified／1 級", "非文字份額（1.4；Cap_In H7 對照列）",
        DASH, "7%（訊息）", f"採用（X31）：新登錄 {S(51)}；非文字份額唯一一手代理；「不存在於該文」事項一併登錄（每則 token、方案別占比、分布）",
        "訊息口徑非營收口徑", S(51), "Cap_In H7 非文字對照列（份額為 Assumed 藍字）", "1", "利害關係方"),
    _ev("N03", "LMSYS-Chat-1M：每則提示 69.5、回覆 214.5 tok、2.0 輪", "arXiv 2309.11998 表 1 https://arxiv.org/pdf/2309.11998", "Analogy／1 級",
        "Alloc_In C15 組成 (a)(e)", "4,000", "284／則（a＋e）", f"部分採用（X29）：新登錄 {S(52)}（2023 Arena 用戶；只作下界）", "Decisions C4 已登錄資料集名稱，未登錄 token 數",
        S(52), DASH, "1", "中立"),
    _ev("N04", "WildChat：每則 295.6／441.3 tok、2.54 輪；sd 1,609", "arXiv 2405.01470 表 1 https://arxiv.org/pdf/2405.01470", "Analogy／1 級",
        "Alloc_In C15 組成 (a)(e)", "4,000", "737／則（a＋e）", f"部分採用（X29）：新登錄 {S(53)}（分布右偏證據）", "同上", S(53), DASH, "1", "中立"),
    _ev("N05", "Altman：推理模型每日用戶占比，免費 <1% → 7%、Plus 7% → 24%（GPT-5 後）", "Altman X 2025-08-10，經 Simon Willison", "Verified／2 級（一手貼文經轉載）",
        "付費／免費用量倍數；C15 組成 (d)", DASH, "7%／24%", f"採用（X30）：新登錄 {S(54)}（值＝免費、高欄＝Plus）；付費 vs 免費用量差的唯一一手線索", "用戶占比，非訊息占比",
        S(54), DASH, "2", "利害關係方"),
    _ev("N06", "方案上下文上限 Free 27K／Go·Plus 54K／Pro 128K；推理 256K／400K；Free／Go 不限文字訊息", "ChatGPT 定價頁；Help「GPT-6 in ChatGPT」（2026-10-12 讀）", "Verified／1 級",
        "C15 組成 (b) 上限；P07 方案上限", DASH, "27K–400K", f"採用（X29）：新登錄 {S(55)}（值＝Free 27K、高欄＝Pro 推理 400K）；歷史上下文的物理上限；限流不封頂倍數 k",
        "—", S(55), DASH, "1", "利害關係方"),
    _ev("N07", "ChatGPT 搜尋每週 >10 億次（2025-04）", "OpenAI 經 The Decoder 2025-04-28", "Interested-party／2 級", "C15 組成 (c)", DASH, "1 B／週 ≈ 5.6% 訊息",
        f"採用（X29）：新登錄 {S(56)}；工具內容的唯一量化依據", f"{SECOND}；日期由公告推定", S(56), DASH, "2", "利害關係方"),
    _ev("N08", "圖像生成 1.3 億用戶一週 7 億張（2025-04）", "Lightcap 經 TechCrunch 2025-08-04", "Interested-party／2 級", "非文字份額", DASH, "~4% 訊息（尖峰）",
        f"部分採用（X31）：新登錄 {S(57)}（尖峰週，非平均）", "—", S(57), "Cap_In H7 非文字對照列", "2", "利害關係方"),
    _ev("N09", "Sora app 下載 960 萬、消費者支出累計 $1.4M", "Appfigures，經 TechBriefly https://techbriefly.com/2026/01/30/sora-app-downloads-plunge-45-in-january-2026/",
        "Interested-party／2 級", "非文字份額（影片）", DASH, "$1.4M", "部分採用（X31）：影片營收歸屬 ≈ 0 的證據；不登錄 SRC（無模型用數值）", "Appfigures 賣數據", DASH, DASH, "2", "第三方量測"),
    _ev("N10", "Altman 2024-02：每日約 1,000 億字 → 每則可見輸出 ≈ 300 tok（Derived）", "Altman X 經 Interconnects", "Interested-party／2 級", "C15 組成 (e)", DASH, "~300",
        f"部分採用（X29）：新登錄 {S(58)}（2024 時點；上界含 API）", SECOND, S(58), DASH, "2", "利害關係方"),
    _ev("N11", "Epoch 調查：35% 美國人上週用 ChatGPT；<10% 付費；OpenAI 訂閱者 4.6%", "Epoch AI https://epochai.substack.com/p/polling-on-ai-usage", "Verified／1 級", "人數口徑（美國）",
        DASH, "4.6%／35%＝13%", f"採用（X30）：新登錄 {S(59)}（中立調查；美國付費率高於全球 5.7%）", "無每用戶訊息數、無付費／免費用量差", S(59), DASH, "1", "中立"),
    _ev("N12", "OpenAI Enterprise：每週訊息一年 ×8、每人 +30%、前沿公司每席 2 倍", "OpenAI「The state of enterprise AI 2025」", "Verified／1 級", "席次用量；SRC_DEM_045 補充",
        "6（p95 ÷ 中位）", "×8；2×", "部分採用（X30）：補到 SRC_DEM_045 備註，不另開 SRC", "SRC_DEM_045 同文", "SRC_DEM_045", DASH, "1", "利害關係方"),
    _ev("N13", "Codex 週用戶 1M（02-05）→ 2M → 4M → 5M → 8M（07-14）", "Altman／Sottiaux X，經 Fortune，彙整於 fourweekmba", "Interested-party／2 級", "程式代理用戶數",
        "1.6M（SRC_DEM_021）", "8M", f"採用（X27）：E301「待查」改「已查證」（Altman 2026-07-14）；新登錄 {S(60)}（07-14 一筆）", f"{SECOND}（彙整站轉述 Fortune）",
        f"{S(60)}；SRC_DEM_021", DASH, "2", "利害關係方"),
    _ev("N14", "OpenAI 2026-02-27：3 GW 專用推論＋2 GW 訓練（Vera Rubin；前瞻）", _SCALE, "Verified／1 級", "SRC_DEM_009 之後的算力序列", "1.9 GW（2025 底）", "3＋2 GW（前瞻）",
        f"部分採用（X27）：新登錄 {S(61)}（前瞻承諾，不入 2025 平均；口徑未明）", "與 SRC_DEM_019 同文", f"{S(61)}；SRC_DEM_019（同源）", DASH, "1", "利害關係方"),
    _ev("N15", "Altman 2025-10：2025 底「超過 2 GW」", "YouTube 訪談，經 Parekh https://michaelparekh.substack.com/p/ai-openais-ongoing-mega-ai-deals（作者轉述）", "Interested-party／2 級（轉述）",
        "SRC_DEM_009 佐證", "1.9", ">2", "部分採用（X27）：備註到 SRC_DEM_009，不另開 SRC", SECOND, "SRC_DEM_009", DASH, "2", "利害關係方"),
    _ev("N16", "Axios 2026-10-08：OpenAI ARR 500 億 vs 先前 700 億；差異為毛額／淨額會計口徑（OpenAI 只記自身份額）", "Axios https://www.axios.com/2026/10/08/openai-50-billion-arr-anthropic-revenue-accounting",
        "Interested-party／2 級", "J3／J14 營收口徑（Cap_In H1；SRC_DEM_007）", "13.07（口徑未標）", "50 vs 70", f"採用（X34）：新登錄 {S(62)}；SRC_DEM_007 備註補 J14（13.07 為 OpenAI 自身營收口徑，待一手確認）；數值不改",
        f"{SECOND}（匿名消息來源）", f"{S(62)}；SRC_DEM_007", "L1_MImplied、L1_MFleet（若改口徑；本版未改）", "2", "雙方"),
    _ev("N17", "Axios 2026-09-29：ARR 近 700 億；B2B >100%、企業倍增", "Axios https://www.axios.com/2026/09/29/scoop-openais-annual-recurring-revenue-nears-70b", "Interested-party／2 級", "營收序列",
        DASH, "~70 $B", f"部分採用（X34）：登錄為 {S(62)} 高欄（毛額口徑）；2026 時點，無拆分", f"{SECOND}（匿名消息來源）", S(62), DASH, "2", "利害關係方"),
    _ev("N18", "Deep Research 每次約 1 M token（作者友人估計）", "Interconnects（N10 同文）", "Analogy／3 級", "C15 組成 (c)", DASH, "~1 M", "不採用為數值（估計無出處）；只作方向", "—", DASH, DASH, "3", "中立"),
    _ev("N19", "Abilene 2026-05 運轉 0.3–1 GW（Epoch 估計，FutureSearch 彙整）", "https://futuresearch.ai/app/p/a/openai-data-center-capacity-gw-2027", "Analogy／3 級", "2026 算力", DASH, "0.3–1",
        "不採用（2026；二手估計）", "—", DASH, DASH, "3", "中立"),
    _ev("N20", "ChatGPT WAU 序列 500M（2025-03）→ 700M → 800M → 900M → 1B → 1.2B（2026-09）六點", "Turley X 經 TechCrunch；OpenAI；DevDay 2025；OpenAI 2026-02-27；Bloomberg 2026-07-31；DevDay 2026 recap",
        "Verified／Interested-party／1–2 級", "人數口徑分母", DASH, "500–1,200", f"採用（X30）：新登錄 {S(63)}–{S(68)}（六時點各一筆）；付費率計算的分母", "v5.32 U18 已列、未登錄",
        "；".join(S(k) for k in range(63, 69)), DASH, "1–2", "利害關係方"),
    _ev("N21", "Sensor Tower：每用戶每日 16 分鐘、每月 12 天", "TechCrunch 2025-08-04（Sensor Tower）", "Analogy／2 級", "用量強度", DASH, "16 min", "不採用為數值（app 端、非 token）；登錄已看過",
        "Sensor Tower 賣數據", DASH, DASH, "2", "第三方量測"),
    _ev("N22", "2026 每日訊息數：OpenAI 未揭露（搜尋紀錄）", "搜尋：WebSearch「OpenAI ChatGPT messages per day 2026」「billion messages 2026」「DevDay 2026 recap」；OpenAI DevDay 2026 recap、「Scaling AI for everyone」；dageno.ai；getpanto.ai",
        DASH, "SRC_DEM_012 更新", "2.5 B", "未找到", "缺口登錄（「未找到」，含搜尋範圍，避免重搜）；代理：WAU 序列 × 每用戶訊息成長，方向 2026 高於 2025", "—", DASH, DASH, DASH, DASH),
    _ev("N23", "付費用戶占訊息比例、每則 token、系統提示長度、語音與 Deep Research 用量：未找到／未揭露", "A 段 P03、1.4 節、V05（搜尋紀錄見報告）", DASH, "Alloc_In C15、C16", DASH, DASH,
        "缺口登錄（「未找到」）；C15 高端改 11,000（J9）、C16 不改（J10）", "—", DASH, DASH, DASH, DASH),
]


def evidence_rows():
    return EVIDENCE_V533


E301_TAIL = f" ｜v5.33 已查證（{EV['N13']}，N13）：8M 有出處＝Altman X 2026-07-14，經 Fortune；登錄 {S(60)}"


def evidence_update(wb):
    """E301 (v5.32 N23「待查」) verdict column: appended once (guarded by presence)."""
    ws = wb["DB_Evidence"]; n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "E301" and v518._append_text(ws.cell(r, 9), E301_TAIL): n += 1
    return n


# ================================================================== B6: Decisions X27–X34 (10 columns; layout of v531／v532) and X22／X26 notes
_ANDY_BOTH = f"{ANDY_R0}；{ANDY_R1}；chat 端建議（A 段查證報告 PR #40 第 9 節），可撤回"
_X = [
    ("X27", "J7 物理路線兩種讀法", "機隊口徑兩種讀法並列：(i) 點估計＝支出路線服務 GW（SRC_DEM_018 ÷ 持有成本 ÷ Azure 倍數）× 實際利用率修正（AL_UtilActual ÷ IF_Util）→ 機隊付費 token → 機隊 m；"
     "(ii) 上限＝同一 GW × CTL_ProdDerate 的最大產出 → 機隊付費 token 上限 → m 下限。兩者都進 Cap_In H7 與 L1（L1_MFleet、L1_TokCeiling）；對回本條件有意義的是機隊 m",
     "Cap_In H7；L1_MFleet／L1_TokCeiling；Checks M2／M3", "B3、B4"),
    ("X28", "J8 2025 基準年服務世代組合", "Alloc_In C9–C12 改為 Hopper 0.6／GB200 0.4／GB300 0／VR200 0（Andy 2026-10-13：「或改為 Hopper 60／GB200 40」）；低／高區間不改。理由：VR200 2025 未出貨；"
     "C9 備註的 h_alloc_mix_2025 情境即此組合。連動：Alloc B–G 節、IF_AllocQ1／Q1_R2／Q2／ServeGW／ImpliedNk、L1_ScaleServe 等（IF_AllocDemand、IF_AllocRDGW 不變）",
     "Alloc_In C9、C11、C12；Gov_Map GM590", "B2"),
    ("X29", "J9 每則提示 token 數高端", "Alloc_In C15 基準 4,000 與低端 2,000 不改；高端 6,400 → 11,000（A 段 1.2 節五組成高端 11,300 取整）；不拆成多個輸入（五組成全為 Assumed／Analogy，無一手校準）",
     "Alloc_In E15；Gov_Map GM586／GM587；L1_GapPrompt_Hi", "B2"),
    ("X30", "J10 免費占比不改＋支出口徑對照", "Alloc_In C16 不改（0.6，0.4–0.8）；Cap_In H7 新增對照列：免費 ÷ 付費 token 比 r＝支出口徑換算（IF_FreeShare × 付費產能倍數 ÷（1 − IF_FreeShare），A 段 P09 約 3.2）"
     "vs 模型 AL_DFree ÷ AL_DPaid（約 0.57）；人數口徑 5.7%、訊息 15–38%、token 18–55%、支出 24% 並列於 A 段 2.2 節",
     "Cap_In H7 r 兩列；Alloc_In C16（不改）", "B3"),
    ("X31", "J11 非文字服務份額對照", "非文字份額不進 Cap_In H1 分子；H7 新增對照列：藍字 Assumed 0.05／0.10／0.20（登錄 Gov_Map），只重算「扣除後訂閱 m、合併 m」作顯示；Deep Research／代理不扣（文字 token）；API 不扣",
     "Cap_In H7 非文字三列；Gov_Map 新列", "B3、B6"),
    ("X32", "J12 訂閱占比結案", "訂閱占比維持 0.70（SRC_DEM_039）；0.765（A 段試算副本）不登錄。v5.32 報告「待 Project 判斷」第 1 項結案", "Cap_In C70（不改）", "B3"),
    ("X33", "J13 利用率修正公式", "Alloc 第 22 列定義不改（只含 IF_Util）。H7 新列自帶修正：點估計乘 AL_UtilActual ÷ IF_Util（0.35 ÷ 0.6＝0.583）；上限乘 CTL_ProdDerate（0.85）；A 段用的 0.686 不採用",
     "Cap_In H7 修正兩列", "B3"),
    ("X34", "J14 營收口徑（SRC_DEM_007）", "SRC_DEM_007 13.07 數值不改。登錄 Reuters／Axios 2026-10-08 證據（OpenAI 年化數字不含經雲端夥伴銷售）；SRC_DEM_007 備註與 Decisions X22 備註補："
     "「13.07 為 OpenAI 自身營收口徑（不含 Azure OpenAI Service 轉售），與分母的 OpenAI 自身 Azure 帳單口徑一致；待一手確認」",
     f"SRC_DEM_007 備註；{S(62)}；Decisions X22", "B1、B6"),
]
DECISIONS_V533 = [[i, V, f"{i} {t}", txt, DATE, _ANDY_BOTH, "v5.33 已建", where, f"工作單 v5.33 r1 {sec}", "否"] for i, t, txt, where, sec in _X]
X22_TAIL = f" ｜v5.33 J14：{J14_NOTE}"
X26_TAIL = " ｜v5.33 A 段後：「m＝1 很可能高估」的證據只剩 API／程式代理路線與現行組合下的機隊 m；2025 Hopper 組合下機隊 m 約 0.8"


def decisions_update(ws, append_text):
    n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "X22" and append_text(ws.cell(r, 4), X22_TAIL): n += 1
        if ws.cell(r, 1).value == "X26" and append_text(ws.cell(r, 4), X26_TAIL): n += 1
    return n


# ================================================================== README (version string is built from VERSION; v5.32 text is kept after it)
README_VERSION = (VERSION + "（判斷類，工作單 docs/workorders/20261012_v5.33.md r1；A 段查證 PR #40：付費 token 數量校準——Alloc_In 2025 基準年世代組合改 Hopper 0.6／GB200 0.4／GB300 0／VR200 0（J8）、"
                  "每則提示 token 數高端 6,400 → 11,000（J9）；Cap_In 新增 H7「機隊口徑」（支出路線服務 GW ÷ Azure 倍數 × 利用率修正 → 機隊付費 token 點估計與上限 → 機隊 m、m 下限、"
                  "「必須為真」三列、非文字對照）；L1 新增 L1_MFleet、L1_TokCeiling，Checks M2、M3；SRC_DEM_049–068、DB_Evidence E302–E324、Decisions X27–X34；"
                  "IF_AllocQ1／Q1_R2／Q2／ServeGW／ImpliedNk 與 Alloc 相關 L1 隨世代組合改變，其餘 IF_ 不變；CTL_Monetize 不改）。以下為 " + v532.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v532.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v532.VERSION.split("_")[-1]):]
README_ROW = ("機隊口徑與付費 token 校準（v5.33）",
              "Cap_In H7：支出路線服務 GW（Alloc 第 61 列 ÷ Alloc_In C23 Azure 倍數）× 利用率修正 ÷（1 ÷ AL_BlendPaid ＋ r ÷ AL_BlendFree）＝機隊付費 token；修正：點估計＝AL_UtilActual ÷ IF_Util（X33），"
              "上限＝CTL_ProdDerate。機隊 m（點估計）＝SRC_DEM_007 ÷（機隊付費 token × H4 單價）→ L1_MFleet；上限讀法 → L1_TokCeiling 與 m 下限（X27）。"
              "「必須為真」三列給 m＝1／0.6／0.3 所需付費 token、÷ 需求路線倍數與對上限判讀；非文字份額（Assumed 0.05／0.10／0.20）只作訂閱分子扣除後的對照（X31）。"
              "Checks M2（需求路線 > 上限）、M3（機隊 m 區間外）為 WARN。2025 基準年世代組合 Hopper 60／GB200 40（X28）；每則提示 token 數高端 11,000（X29）；免費占比與訂閱占比不改（X30、X32）；"
              "SRC_DEM_007 為 OpenAI 自身營收口徑（X34，待一手確認）。")

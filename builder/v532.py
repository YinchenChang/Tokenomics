# v5.32 (work order docs/workorders/20261011_v5.32.md r1, B section): monetisation-rate m tracking from the A-section evidence report
# (docs/reports/20261011_v5.32A_查證.md, PR #38; J1 (a′), J2–J6 adopted; Andy 2026-10-11 11:21「了解，接著照建議依序執行」).
#   B1 DB_Evidence E279–E301 (A-section N01–N23, verdicts as proposed); SRC_Demand SRC_DEM_019–048 (one record per time point and metric
#      for N01–N04, N06–N16 with values; N15／N16 registered only, Cap_In C13 unchanged); SRC_DEM_018 note gets N12.
#   B2 Cap_In H section「m 追蹤（v5.32）」after G (Cap_In ends at row 64, so no existing name moves): revenue (SRC_DEM_007 × subscription
#      share), subscribers (period average), paid tokens with two denominators side by side (model: Alloc rows 5／8; external: SRC_DEM_011,
#      SRC_DEM_013 × (1 − IF_FreeShare)), blended price (Cap_In row 31 × IF_PriceRef_*; no new price input), implied m per route × denominator,
#      coding-agent comparison rows (not in the combined route).
#   B3 L1_MImplied／L1_MImplied_Ext (with _Lo／_Hi; external columns = CTL_Monetize; judgement = inside／outside the Gov_Map range of
#      CTL_Monetize); Checks M1 (WARN when L1_MImplied base is outside that range).
#   B4 CTL_Monetize (value 1) and its Gov_Map range stay unchanged; no IF_ name added.
#   B5 Gov_Map GM594 reason column (append); Decisions X21–X26.
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v531, so a rebuild never overwrites a later Excel edit.
from openpyxl.utils import get_column_letter as L
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY, section
import v518
import v531

VERSION = "20261011_Tokenomics_v5.32"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-11"
V = "v5.32"
DASH = "—"
ANDY = "chat 端判定（A 段查證報告 PR #38 J1–J6；J1 調整為 (a′)），Andy 2026-10-11 11:21「了解，接著照建議依序執行」；可撤回"
ANDY_0941 = ("Andy 2026-10-11 09:41「把那个就是我们要追踪 M 的这个最直接的数据，付费用户数乘上每年每年 token 用量，这个把它追踪下去，"
             "就是放到工作单里面，叫那个 tokenomics 去更新版的时候，要把它放进去。」（語音轉寫，未改字）")
REPORT_A = "docs/reports/20261011_v5.32A_查證.md"
EV = {f"N{i:02d}": f"E{278 + i}" for i in range(1, 24)}          # A-section N01–N23 -> E279–E301 (next free number after E278)


def S(n): return f"SRC_DEM_{n:03d}"


# ================================================================== B1: SRC_Demand records (next free number at v5.31: SRC_DEM_019)
_A = f"A 段查證（{REPORT_A}）"
_OAI_SCALE = "OpenAI「Scaling AI for everyone」https://openai.com/index/scaling-ai-for-everyone/"
_OAI_FUND = "OpenAI 融資公告 https://openai.com/index/accelerating-the-next-phase-ai/"
_TI_AIN = "The Information，經 AIN.UA 轉述 https://en.ain.ua/2025/04/02/chatgpt-revenue-grew-30-percent"
_CNBC = "CNBC，經 NBC Miami https://www.nbcmiami.com/news/business/money-report/openai-hits-10-billion-in-annual-recurring-revenue-fueled-by-chatgpt-growth/3632896/"
_REUTERS_S1 = ("Reuters（Echo Wang、Krystal Hu）讀機密 S-1，經 Global Banking & Finance "
               "https://www.globalbankingandfinance.com/exclusive-anthropic-ipo-prospectus-lays-bare-deep-dependence/（Khaleej Times 同文）")
_OAI_STAKE = "OpenAI 公司揭露；融資期間有呈現成長的誘因"
_MEDIA_STAKE = "OpenAI 內部數字經媒體轉述；有呈現成長的誘因"
_ANT_STAKE = "Anthropic 未公開 S-1 經媒體轉述；上市前"
_PEG = "Peng 等（Pegatron PEGAVERSE）arXiv:2607.13080 https://arxiv.org/pdf/2607.13080"
_PEG_STANCE = "作者比較雲端與自建成本，無銷售 token 誘因；n＝1"


def _rec(n, ev, metric, val, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note, lo=None, hi=None):
    return dict(id=S(n), sheet="SRC_Demand", metric=metric, val=val, lo=lo, hi=hi, unit=unit, basis=basis, applies=applies, date=date,
                src=src, grade=grade, stance=stance, stance_note=stance_note, hand=hand, status="Active", ev=EV[ev], s="U-V532", use=use,
                note=f"v5.32 新增（{EV[ev]}，A 段暫編 {ev}）：{note}；{_A}")


SRC_NEW = [
    # N01 (2026-02-27, OpenAI first-hand)
    _rec(19, "N01", "ChatGPT 消費訂閱數", 50, "百萬", "時點 2026-02-27；「超過」；消費訂閱（Plus／Pro 等）", "OpenAI ChatGPT", "2026-02-27",
         _OAI_SCALE, 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "Cap_In H 節（訂閱人數期間平均的期末端）｜換算",
         "採用：訂閱時間序列的一手錨點；2026-03-31 融資公告同值（不構成新時點）"),
    _rec(20, "N01", "ChatGPT 付費商用用戶數", 9, "百萬", "時點 2026-02-27；「超過」；Business／Enterprise／Edu 付費用戶", "OpenAI ChatGPT", "2026-02-27",
         _OAI_SCALE, 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "（時間序列；不連結模型格）",
         "採用：商用時間序列的一手錨點（A 段 U12；N06 序列的最後一點）"),
    _rec(21, "N01", "Codex 每週用戶", 1.6, "百萬", "時點 2026-02-27；每週活躍；含訂閱內使用與 API", "OpenAI Codex", "2026-02-27",
         _OAI_SCALE, 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "（時間序列；不連結模型格）",
         "採用：程式代理用戶數；2026-03-31 >2M（同公司融資公告，未另登錄）"),
    # N02 (2026-03-31)
    _rec(22, "N02", "OpenAI 月營收", 2, "$B/月", "時點 2026-03；月營收", "OpenAI", "2026-03-31",
         _OAI_FUND, 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "（時間序列；不連結模型格）",
         "採用：營收拆分下限的分母；同公告 API >15B tok/min 已為 SRC_DEM_011"),
    _rec(23, "N02", "OpenAI 營收中「企業」占比", 0.40, "%", "時點 2026-03；「超過」；「企業」口徑未定義（可能含商用席次＋API）", "OpenAI", "2026-03-31",
         _OAI_FUND, 1, "利害關係方", _OAI_STAKE, "一手（已讀）", "（時間序列；不連結模型格）",
         "採用（口徑註明未定義）：與「消費約 70%」相加 >100%，口徑互相重疊"),
    # N03 (2025-01／04, one report)
    _rec(24, "N03", "ChatGPT 消費訂閱數", 15.5, "百萬", "時點 2025-01；消費訂閱（Plus＋Pro）", "OpenAI ChatGPT", "2025-04-02",
         _TI_AIN, 2, "利害關係方", _MEDIA_STAKE, "二手", "Cap_In H 節（訂閱人數期間平均的期初端）｜換算",
         f"部分採用：時間序列早段；與 {S(25)} 同一則報導（不獨立）"),
    _rec(25, "N03", "ChatGPT 消費訂閱數", 20, "百萬", "時點 2025-03／04；「超過」；消費訂閱", "OpenAI ChatGPT", "2025-04-02",
         _TI_AIN + "（The Information「ChatGPT revenue surges 30% in just three months」）", 2, "利害關係方", _MEDIA_STAKE, "二手",
         "Cap_In H 節（訂閱人數時間序列）｜顯示", f"部分採用：時間序列早段；與 {S(24)} 同一則報導（不獨立）"),
    # N04 (2025-07)
    _rec(26, "N04", "ChatGPT 消費訂閱數", 35, "百萬", "時點 2025-07；消費訂閱（Plus 或 Pro）", "OpenAI ChatGPT", "2025-11-26",
         "Reuters 轉述 The Information https://tech.yahoo.com/ai/chatgpt/articles/openai-projected-least-220-million-012027742.html", 2,
         "利害關係方", "OpenAI 投資人資料經媒體；有呈現成長的誘因", "二手", "Cap_In H 節（訂閱人數時間序列）｜顯示", "採用：2025 年中錨點"),
    # N06 (business users time series; the 2026-02 point is SRC_DEM_020)
    _rec(27, "N06", "ChatGPT 付費商用用戶數", 2, "百萬", "時點 2025-02", "OpenAI ChatGPT", "2025-06-09",
         _CNBC, 2, "利害關係方", "OpenAI 發言人經媒體", "二手", "（時間序列；不連結模型格）", f"採用：商用序列第 1 點（與 {S(28)} 同一則報導）"),
    _rec(28, "N06", "ChatGPT 付費商用用戶數", 3, "百萬", "時點 2025-06", "OpenAI ChatGPT", "2025-06-04",
         _CNBC + "；TipRanks https://www.tipranks.com/news/microsoft-backed-openai-msft-now-has-three-million-paying-business-users", 2,
         "利害關係方", "OpenAI 發言人經媒體（多家轉述同一公司發言，不另算）", "二手", "（時間序列；不連結模型格）", "採用：商用序列第 2 點"),
    _rec(29, "N06", "ChatGPT 付費商用用戶數", 5, "百萬", "時點 2025-08", "OpenAI ChatGPT", "2025-08",
         "The Decoder https://the-decoder.com/chatgpt-is-set-to-reach-700-million-weekly-users-this-week/", 2, "利害關係方", "OpenAI 經媒體",
         "二手", "（時間序列；不連結模型格）", "採用：商用序列第 3 點"),
    _rec(30, "N06", "ChatGPT for Work 席次", 7, "百萬", "時點 2025-11-05；「超過」；席次（非用戶；口徑與前後點不同）", "OpenAI ChatGPT", "2025-11-05",
         "OpenAI「1 million businesses」https://openai.com/index/1-million-businesses-putting-ai-to-work/", 1, "利害關係方", _OAI_STAKE,
         "一手（已讀）", "（時間序列；不連結模型格）", "採用（7M 為「席次」口徑另註）：商用序列第 4 點；同文：商用客戶 >100 萬家"),
    # N07
    _rec(31, "N07", "OpenAI 平台開發者數", 4, "百萬", "時點 2025-10-06；開發者（非付費 API 組織）", "OpenAI API", "2025-10-06",
         "Altman DevDay 2025，經 https://alicialyttle.com/openai-devday-2025-what-just-changed-for-builders/（TechCrunch 同日報導）", 2,
         "利害關係方", "OpenAI 管理層", "二手", "（API 路線每開發者口徑的上界分母；不連結模型格）",
         "部分採用：只作上界分母；付費 API 組織數找不到；與 SRC_DEM_010 同一場合"),
    # N08 (Anthropic)
    _rec(32, "N08", "Anthropic 商用客戶數", 300000, "家", "時點 2025-08／09；「超過」；家（非席次）", "Anthropic", "2025-09-02",
         "Anthropic Series F 公告（GIC 存檔）https://www.gic.com.sg/uploads/2025/09/Anthropic-raises-13B-Series-F-at-183B-post-money-valuation.pdf", 1,
         "利害關係方", "Anthropic 融資公告", "一手（已讀）", "（Anthropic 序列；Alloc_In A8 尚未啟用）", "採用：Anthropic 序列起點；消費訂閱數未揭露"),
    _rec(33, "N08", "Anthropic 年付超過 $1M 客戶數", 500, "家", "時點 2026-02-12；「超過」", "Anthropic", "2026-02-12",
         "Anthropic Series G https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation", 1,
         "利害關係方", "Anthropic 融資公告", "一手（已讀）", "（Anthropic 序列；不連結模型格）", "採用；同文：Claude Code 商用訂閱自年初 4 倍"),
    # N09 (Anthropic 2025 split, confidential S-1 via Reuters)
    _rec(34, "N09", "Anthropic 2025 用量計費營收", 3.8, "$B", "2025 年度；用量計費（API 等）", "Anthropic", "2026-09-29",
         _REUTERS_S1, 2, "利害關係方", _ANT_STAKE, "二手", "（m 偏離來源 (4) 通路分潤的依據；不連結模型格）", "採用；公開 S-1 出來後升級"),
    _rec(35, "N09", "Anthropic 2025 訂閱營收", 0.789, "$B", "2025 年度；訂閱（占約 17%）", "Anthropic", "2026-09-29",
         _REUTERS_S1, 2, "利害關係方", _ANT_STAKE, "二手", "（不連結模型格）", "採用；公開 S-1 出來後升級"),
    _rec(36, "N09", "Anthropic 2025 經雲端市集營收（AWS、Google）", 2.16, "$B", "2025 年度；雲端市集（占約 47%；營收為總額）", "Anthropic", "2026-09-29",
         _REUTERS_S1, 2, "利害關係方", _ANT_STAKE, "二手", "（不連結模型格）", "採用；公開 S-1 出來後升級"),
    _rec(37, "N09", "Anthropic 2025 付給雲端平台的分潤", 0.351, "$B", "2025 年度；Reuters 自行分析；列為費用（÷ 市集營收＝16%，÷ 總營收＝7.6%，Derived）",
         "Anthropic", "2026-09-29", _REUTERS_S1 + "；分潤為 Reuters 自行分析", 2, "利害關係方", _ANT_STAKE, "二手",
         "（m 偏離來源 (4) 通路分潤唯一量化依據；不連結模型格）", "採用；公開 S-1 出來後升級"),
    # N10 (OpenAI revenue split)
    _rec(38, "N10", "OpenAI 營收中消費訂閱占比", 0.75, "%", "時點 2024-10；約值；CFO 口述", "OpenAI", "2024-10-28",
         "Friar 於 Bloomberg TV，經 CO/AI https://getcoai.com/news/openai-cfo-reveals-75-of-revenue-from-consumer-subscriptions", 2,
         "利害關係方", "OpenAI CFO", "二手", "（時間序列；不連結模型格）", "採用；另：免費轉付費 5–6%"),
    _rec(39, "N10", "OpenAI 營收中消費訂閱占比", 0.70, "%", "2025 年度（年營收約 $13B）；約值", "OpenAI", "2025-10-15",
         "FT，經 Global Trade Mag https://www.globaltrademag.com/openai-hits-13b-revenue-fueled-by-consumer-subscriptions/", 2,
         "利害關係方", _MEDIA_STAKE, "二手", "Cap_In H 節（訂閱占比基準）｜直接", "採用：訂閱占比區間 0.61／0.70／0.82 的基準"),
    _rec(40, "N10", "OpenAI 2024 ChatGPT 營收（預期）", 2.7, "$B", "2024 年度預期；其他（API 等）1.0、合計 3.7", "OpenAI", "2024-09-27",
         "NYT（Isaac、Griffith）財務文件，經 https://www.simonwillison.net/2024/Oct/23/mike-isaac-and-erin-griffith", 2,
         "利害關係方", "OpenAI 募資文件", "二手", "（時間序列；不連結模型格）", "採用：ChatGPT 占 2024 營收約 73%"),
    _rec(41, "N10", "OpenAI 2025 ChatGPT 營收（預期）", 8, "$B", "2025 年度預期（同期營收預期約 12.7）", "OpenAI", "2025-06-10",
         "CTech https://www.calcalistech.com/ctechnews/article/ry8117uhmll（引 The Information）", 2, "利害關係方", "OpenAI 預測",
         "二手", "Cap_In H 節（訂閱占比低端＝本筆 ÷ SRC_DEM_007）｜換算", "採用：8 ÷ 13.07＝0.61 為訂閱占比低端"),
    # N11
    _rec(42, "N11", "OpenAI 季營收", 6.7, "$B", "2026 Q2；季度", "OpenAI", "2026-08-18",
         "WSJ，經 CryptoBriefing https://cryptobriefing.com/openai-revenue-6-7-billion-q2-2026/", 2, "利害關係方", _MEDIA_STAKE,
         "二手", "（時間序列；不連結模型格）", "部分採用：營收採用；同文「消費約 70%」與「企業 >40%」口徑重疊，占比不採用"),
    # N12
    _rec(43, "N12", "OpenAI 付 Microsoft 營收分成比例", 0.20, "%", "2025-10 重組後至 2030；上限 $38B（只有二手，待查一手）", "OpenAI／Microsoft", "2026-05-13",
         "The Decoder https://the-decoder.com/openai-and-microsoft-rewrite-their-deal-no-more-exclusivity-no-more-agi-clause/；"
         "Let's Data Science 引 CryptoBriefing https://letsdatascience.com/news/openai-renegotiates-microsoft-deal-caps-payments-at-38b-94907359", 2,
         "利害關係方", "交易雙方", "二手", "（m 偏離來源 (4)；營收以毛額計（J3），不扣分潤；不連結模型格）",
         "部分採用：20% 採用；$38B 上限待查一手；Azure 轉售 OpenAI 模型的 20% 回付已停止；SRC_DEM_018 備註同步"),
    # N13
    _rec(44, "N13", "Claude Code 企業部署平均花費", 13, "$／開發者·活躍日", "列價口徑；企業部署平均；高欄＝p90 上限（<$30）；月約 $150–250",
         "Anthropic Claude Code（企業）", "2026-10-11", "Claude Code 文件「Manage costs」https://code.claude.com/docs/en/costs（2026-10-11 讀）；"
         "舊值 $6／p90 $12 見 Shopifreaks 2026-04-29", 1, "利害關係方", "Anthropic；預算建議偏保守或偏高皆可能", "一手（已讀）",
         "Cap_In H 節（程式代理對照列）｜直接", "採用：程式代理路線每用戶用量的唯一一手數字（列價口徑；平均 vs p90 → 分布右偏）", hi=30),
    # N14
    _rec(45, "N14", "ChatGPT Enterprise 員工訊息數 p95 ÷ 中位數", 6, "倍", "2025；分布形狀（若對數常態，平均 ÷ 中位數 ≈ 1.8，Derived）", "OpenAI ChatGPT Enterprise",
         "2025-12-08", "OpenAI「The state of enterprise AI 2025」https://openai.com/index/the-state-of-enterprise-ai-2025-report/", 1,
         "利害關係方", _OAI_STAKE, "一手（已讀）", "（重度用戶占比的分布線索；不連結模型格）", "採用：分布形狀唯一一手；同文：每組織推理 token 一年 ×320"),
    # N15 (registered only; Cap_In C13 χ unchanged)
    _rec(46, "N15", "單一開發者 Claude Code 快取讀取占輸入", 0.993, "%", "2026-05-11～06-07 實測；n＝1；極端重度用戶（548 M tok／日）", "Claude Code＋Opus（單一開發者）",
         "2026-07-13", _PEG, 1, "中立", _PEG_STANCE, "一手（已讀）", "Cap_In H 節（程式代理單價結構對照）｜直接；Cap_In C13 不改",
         "部分採用：n＝1，只作程式代理高端佐證；每 M 實付 $0.573（無快取時 8.8 倍）"),
    _rec(47, "N15", "單一開發者 Claude Code 輸入占全部 token", 0.9987, "%", "2026-05-11～06-07 實測；n＝1；每 1 萬 token 約 9,987 輸入：13 輸出", "Claude Code＋Opus（單一開發者）",
         "2026-07-13", _PEG, 1, "中立", _PEG_STANCE, "一手（已讀）", "Cap_In H 節（程式代理單價結構對照）｜直接",
         "部分採用：n＝1；A 段第 4.2 節以 9,987：13 計"),
    # N16 (registered only)
    _rec(48, "N16", "Claude Code 快取命中率（cached ÷ input）", 0.919, "%", "2026-04；路由流量；樣本數未揭露（其他代理 46–89%）", "Claude Code（經 Requesty 路由）",
         "2026-05-16", "Requesty 路由資料 https://www.requesty.ai/data/coding-agent-cache-hit-rate-apr-2026", 2, "利害關係方",
         "Requesty：推廣自家路由", "一手（已讀）", "Cap_In H 節（程式代理單價結構對照）｜直接；Cap_In C13 不改",
         "部分採用：程式代理 χ 高於 Cap_In C13 高端 0.75；只登錄，不改 χ"),
]
SID = {"subs_2602": S(19), "subs_2501": S(24), "subs_2504": S(25), "subs_2507": S(26), "share_base": S(39), "chatgpt_2025": S(41),
       "cc_spend": S(44), "peg_cache": S(46), "peg_input": S(47), "req_cache": S(48)}


def src_new_records():
    return SRC_NEW


SRC_UPD = {"SRC_DEM_018": ("SRC_Demand", {"W": ("+", f" ｜v5.32（{EV['N12']}，N12 部分採用）：Microsoft 分潤 20%（至 2030）另登錄 {S(43)}；"
                                                       "$38B 上限只有二手，待查一手；Azure 轉售 OpenAI 模型的 20% 回付已停止")})}


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


# ================================================================== B2: Cap_In H section (after G; Cap_In ends at row 64 in v5.31)
CAP_START = 66
FMT = {"$B": "#,##0.000", "%": "0.0%", "百萬": "#,##0.0", "M tok/年": "#,##0", "T tok/日": "#,##0.0", "$/M": "#,##0.0000", "x": "0.000",
       "M tok/人·年": "#,##0.0", "$／開發者·活躍日": "#,##0.0", "日／月": "0", "$／開發者·月": "#,##0", "$／月": "#,##0"}
LAB = dict(  # column-A labels of the rows other modules locate (Gov_Map 'check' labels; L1 links)
    share="訂閱占比（OpenAI 2025 營收中的消費訂閱）",
    days="每開發者每月活躍日（程式代理對照用）",
    fee="程式代理訂閱方案月費（Claude Max 20x 列價；對照用）",
    inshare="程式代理輸入占全部 token（Requesty 情境）",
)
# (key, label, unit, C, D, E, tag, note); key None = sub-header text row. Formulas use {key} placeholders for rows of this section.
# D＝m 低端（營收取低、token 取高）；E＝m 高端（營收取高、token 取低）。單價三欄相同（J2 (iii)：不新增輸入）。
SPEC = [
    (None, "H1. 分子：付費營收（OpenAI 2025，毛額；J3：不扣 Microsoft 分潤）"),
    ("rev", "OpenAI 2025 營收（毛額）", "$B", "=SRC_DEM_007", "=SRC_DEM_007", "=SRC_DEM_007", "Interested-party（連結 SRC）",
     "SRC_DEM_007；單值（三欄相同）"),
    ("share", LAB["share"], "%", f"={SID['share_base']}", f"={SID['chatgpt_2025']}/SRC_DEM_007", 0.82, "Derived（N10）",
     f"基準＝{SID['share_base']}（FT，約 70%）；低端＝{SID['chatgpt_2025']}（2025 ChatGPT 營收預期 8）÷ SRC_DEM_007＝0.61；高端 0.82＝A 段 N10 區間上緣"
     "（藍字常數：A 段第 6 節 13.07 × 82%＝10.7，未能追溯到單一 SRC；登錄 Gov_Map）"),
    ("api_share", "API 占比（＝1 − 訂閱占比；其他＝0：A 段第 6 節「扣訂閱後餘額」）", "%", "=1-C{share}", "=1-E{share}", "=1-D{share}", "Derived",
     "m 低端取 API 營收低（＝1 − 訂閱占比高端），m 高端反之"),
    ("rev_sub", "訂閱營收", "$B", "=C{rev}*C{share}", "=D{rev}*D{share}", "=E{rev}*E{share}", "Derived", "營收 × 訂閱占比"),
    ("rev_api", "API 營收", "$B", "=C{rev}*C{api_share}", "=D{rev}*D{api_share}", "=E{rev}*E{api_share}", "Derived", "營收 × API 占比"),
    (None, "H2. 訂閱人數（每人口徑的直覺檢查；不進 m；J6：期間平均）"),
    ("subs_2501", "ChatGPT 消費訂閱數 — 2025-01", "百萬", f"={SID['subs_2501']}", DASH, DASH, "Interested-party（連結 SRC）", SID["subs_2501"]),
    ("subs_2504", "ChatGPT 消費訂閱數 — 2025-03／04", "百萬", f"={SID['subs_2504']}", DASH, DASH, "Interested-party（連結 SRC）", SID["subs_2504"]),
    ("subs_2507", "ChatGPT 消費訂閱數 — 2025-07", "百萬", f"={SID['subs_2507']}", DASH, DASH, "Interested-party（連結 SRC）", SID["subs_2507"]),
    ("subs_2602", "ChatGPT 消費訂閱數 — 2026-02-27", "百萬", f"={SID['subs_2602']}", DASH, DASH, "Verified（連結 SRC）", SID["subs_2602"]),
    ("subs_avg", "2025 期間平均訂閱數（＝(2025-01 ＋ 2026-02) ÷ 2：首尾平均，線性成長近似；J6 (a)）", "百萬", "=(C{subs_2501}+C{subs_2602})/2",
     "=C{subs_avg}", "=C{subs_avg}", "Derived", "A 段 J6 (a)：期間平均約 3,300 萬（與年營收、年 token 對齊）；期末值 5,000 萬為 J6 (b)"),
    (None, "H3. 分母：付費 token（M tok/年；J2 (i)：模型 token 與外部 token 兩種分母並列）"),
    ("tok_chat", "(i) 模型 token：ChatGPT 付費 token（Alloc 第 8 列；低高端以 Alloc_In 區間同向組合）", "M tok/年", "=AL_DChatPaid",
     "=SRC_DEM_012*1000000000*AL_TokPerPrompt_Hi*365/1000000*(1-AL_FreeShare_Lo)",
     "=SRC_DEM_012*1000000000*AL_TokPerPrompt_Lo*365/1000000*(1-AL_FreeShare_Hi)", "Derived（輸入 Assumed）",
     "基準連結 Alloc 第 8 列；端點＝Alloc 第 6–8 列同式，每則提示 token 數與免費占比取區間端點（A 段第 6 節）"),
    ("tok_api", "(i) 模型 token：API token（Alloc 第 5 列；低高端以 API 全年平均比例區間）", "M tok/年", "=AL_DAPI",
     "=SRC_DEM_010*1000000000*525600*AL_APIratio_Hi/1000000", "=SRC_DEM_010*1000000000*525600*AL_APIratio_Lo/1000000", "Derived（輸入 Assumed）",
     "基準連結 Alloc 第 5 列；端點＝同式，API 全年平均 ÷ 10 月時點值取區間端點"),
    ("tok_paid", "(i) 模型 token：付費合計（＝Alloc 第 9 列）", "M tok/年", "=C{tok_chat}+C{tok_api}", "=D{tok_chat}+D{tok_api}",
     "=E{tok_chat}+E{tok_api}", "Derived", "基準欄等於 AL_DPaid"),
    ("tok_per_sub", "每付費訂閱者年 token（模型；直覺檢查）", "M tok/人·年", "=C{tok_chat}/(C{subs_avg}*1000000)", "=D{tok_chat}/(D{subs_avg}*1000000)",
     "=E{tok_chat}/(E{subs_avg}*1000000)", "Derived", "ChatGPT 付費 token ÷ 期間平均訂閱數（A 段 K01：約 44）"),
    ("ext_api", "(ii) 外部 token：API（SRC_DEM_011 時點值年化；2026-03，不打折）", "M tok/年", "=SRC_DEM_011*1000000000*525600/1000000",
     "=C{ext_api}", "=C{ext_api}", "Verified（連結 SRC；年化為 Derived）", "15B tok/min × 525,600；為 2026-03 時點值，與 2025 營收不同期"),
    ("ext_daily", "(ii) 外部 token：Epoch 前沿實驗室每日 token（SRC_DEM_013；基準＝幾何中點）", "T tok/日", "=(SRC_DEM_013_Lo*SRC_DEM_013_Hi)^0.5",
     "=SRC_DEM_013_Hi", "=SRC_DEM_013_Lo", "Verified（連結 SRC）", "SRC_DEM_013 只有低 10、高 100；基準取幾何中點（A 段第 6.2 節「Epoch 中值約 30 T／日」）"),
    ("paid_share", "付費占比（token 口徑＝1 − AL_FreeShare；v8.1 M2 由支出口徑 IF_FreeShare 改）", "%", "=1-AL_FreeShare", "=C{paid_share}", "=C{paid_share}", "Assumed（連結 Alloc_In）",
     "v8.1 M2（D9）：此占比乘在 token 上，一律用 token 口徑 AL_FreeShare（ChatGPT token 中免費用戶占比 0.6；0.4–0.8）；原用支出口徑 IF_FreeShare（免費占服務 0.46，Cap_In 第 29 列）。"
     "注意：Epoch 為前沿實驗室總量（含 API），ChatGPT 免費占比是否適用於全體為判斷事項，見 2-4 報告待 Project 判斷"),
    ("ext_paid", "(ii) 外部 token：付費合計（Epoch × 365 × 付費占比）", "M tok/年", "=C{ext_daily}*1000000*365*C{paid_share}",
     "=D{ext_daily}*1000000*365*D{paid_share}", "=E{ext_daily}*1000000*365*E{paid_share}", "Derived", "T → M：× 1,000,000"),
    (None, "H4. 單價（J2 (iii)：Cap_In 第 31 列付費層級組合 × IF_PriceRef_*；不新增輸入，三欄相同）"),
    ("price", "付費 token 混合有效單價（層級組合 Luna／Sol／Astra；× AL_Kappa，v8.1 M3）", "$/M", "=(INDEX(B4_MixPaid,1,1)*IF_PriceRef_Luna+INDEX(B4_MixPaid,1,2)*IF_PriceRef_Sol+INDEX(B4_MixPaid,1,3)*IF_PriceRef_Astra)*AL_Kappa",
     "=C{price}", "=C{price}", "Derived", "參考請求混合有效單價（OpenAI 有效價＝表列 ×（1−折扣））按 Cap_In 第 31 列（B4_MixPaid）加權；A 段第 6 節基準 1.961"),
    (None, "H5. 隱含 m＝付費營收 ÷（付費 token × 混合有效單價）；對照 CTL_Monetize（第 64 列，基準 1；Gov_Map 區間 0.3–1.0，J1 (a′) 不改）"),
    ("m_sub", "隱含 m — 訂閱路線（模型 token）", "x", "=C{rev_sub}*1000000000/(C{tok_chat}*C{price})",
     "=D{rev_sub}*1000000000/(D{tok_chat}*D{price})", "=E{rev_sub}*1000000000/(E{tok_chat}*E{price})", "Derived", "$B × 1e9 ÷（M tok × $/M）"),
    ("m_api", "隱含 m — API 路線（模型 token）", "x", "=C{rev_api}*1000000000/(C{tok_api}*C{price})",
     "=D{rev_api}*1000000000/(D{tok_api}*D{price})", "=E{rev_api}*1000000000/(E{tok_api}*E{price})", "Derived", ""),
    ("m_all", "隱含 m — 合併（模型 token）　→ L1_MImplied", "x", "=C{rev}*1000000000/(C{tok_paid}*C{price})",
     "=D{rev}*1000000000/(D{tok_paid}*D{price})", "=E{rev}*1000000000/(E{tok_paid}*E{price})", "Derived",
     "模型 token 分母已知偏低（L1_ScaleServe），> 1 代表分母問題，不代表 m > 1"),
    ("m_sub_ext", "隱含 m — 訂閱路線（外部 token）", "x", "—（無外部 token：OpenAI 未揭露 ChatGPT token 數）", DASH, DASH, DASH,
     "外部只有 API（SRC_DEM_011）與總量（SRC_DEM_013），無法分出訂閱 token"),
    ("m_api_ext", "隱含 m — API 路線（外部 token；SRC_DEM_011 為 2026-03 時點值，營收為 2025）", "x",
     "=C{rev_api}*1000000000/(C{ext_api}*C{price})", "=D{rev_api}*1000000000/(D{ext_api}*D{price})",
     "=E{rev_api}*1000000000/(E{ext_api}*E{price})", "Derived", "分子分母不同期（2025 營收 ÷ 2026-03 處理量），只作方向"),
    ("m_all_ext", "隱含 m — 合併（外部 token：Epoch）　→ L1_MImplied_Ext", "x", "=C{rev}*1000000000/(C{ext_paid}*C{price})",
     "=D{rev}*1000000000/(D{ext_paid}*D{price})", "=E{rev}*1000000000/(E{ext_paid}*E{price})", "Derived",
     "Epoch 區間跨一個數量級（10–100 T／日），m 跨一個數量級"),
    (None, "H6. 程式代理路線（對照列；不進合併；J2 (ii)：N13，加 N15／N16 的 token 組合）"),
    ("cc_spend", "Claude Code 企業平均花費（列價）", "$／開發者·活躍日", f"={SID['cc_spend']}", f"={SID['cc_spend']}_Hi", f"={SID['cc_spend']}",
     "Verified（連結 SRC）", f"{SID['cc_spend']}：平均 13；m 低端取 p90 上限 30"),
    ("days", LAB["days"], "日／月", 21, "=C{days}", "=C{days}", "Assumed", "A 段對照 C：每月 21 個活躍工作日（單值；登錄 Gov_Map）"),
    ("cc_month", "每開發者每月列價用量", "$／開發者·月", "=C{cc_spend}*C{days}", "=D{cc_spend}*D{days}", "=E{cc_spend}*E{days}", "Derived", ""),
    ("fee", LAB["fee"], "$／月", 200, "=C{fee}", "=C{fee}", "Assumed", "A 段對照 C 的方案列價（單值；未另登錄 SRC；登錄 Gov_Map）"),
    ("m_cc", "對照：程式代理訂閱 m（月費 ÷ 月列價用量；m 高端另扣有效折扣 B4_Disc）", "x", "=C{fee}/C{cc_month}", "=D{fee}/D{cc_month}",
     "=E{fee}/(E{cc_month}*(1-B4_Disc))", "Analogy", "分母以 Anthropic 列價計（m 的定義改用 Anthropic 價，非 OpenAI 價）；A 段對照 C：0.32／0.73／0.92"),
    ("inshare", LAB["inshare"], "%", 0.995, f"={SID['peg_input']}", "=C{inshare}", "Assumed（基準）／Analogy（低端）",
     f"基準 0.995＝A 段第 4.2 節 Requesty 情境（995：5，藍字，登錄 Gov_Map）；低端＝{SID['peg_input']}（Pegatron 實測）"),
    ("chi", "程式代理快取命中率 χ", "%", f"={SID['req_cache']}", f"={SID['peg_cache']}", "=C{chi}", "Interested-party／Analogy（連結 SRC）",
     f"基準＝{SID['req_cache']}（Requesty）；低端＝{SID['peg_cache']}（Pegatron，n＝1）；Cap_In C13 參考請求 χ 不改"),
    ("cc_price", "程式代理 Sol 每 M token 實收（OpenAI 有效價）", "$/M",
     "=C{inshare}*((1-C{chi})*IF_PriceFresh_Sol+C{chi}*IF_PriceCached_Sol)+(1-C{inshare})*IF_PriceOut_Sol",
     "=D{inshare}*((1-D{chi})*IF_PriceFresh_Sol+D{chi}*IF_PriceCached_Sol)+(1-D{inshare})*IF_PriceOut_Sol",
     "=E{inshare}*((1-E{chi})*IF_PriceFresh_Sol+E{chi}*IF_PriceCached_Sol)+(1-E{inshare})*IF_PriceOut_Sol", "Derived",
     "Sol 層；新鮮輸入、快取輸入、輸出（含思考）三類 token 依組合加權"),
    ("cc_ratio", "對照：程式代理單價結構倍數（÷ IF_PriceRef_Sol；m 的 token 組合成分）", "x", "=C{cc_price}/IF_PriceRef_Sol",
     "=D{cc_price}/IF_PriceRef_Sol", "=E{cc_price}/IF_PriceRef_Sol", "Derived", "A 段第 4.2 節：0.20（Requesty）、0.11（Pegatron）"),
]
TITLE = ("H. 變現率 m 追蹤（v5.32；工作單 v5.32 r1 B2，J2–J6）：隱含 m＝付費營收 ÷（付費 token × 混合有效單價）；只作追蹤與對照，"
         "不驅動任何 IF_ 輸出；CTL_Monetize 不改（J1 (a′)）。欄位：C＝基準、D＝m 低端（營收取低、token 取高）、E＝m 高端（營收取高、token 取低）")
NOTE_END = ("讀法：(1) 模型 token 分母（H3 (i)）來自 Alloc 的 token 路線，已知偏低（L1_ScaleServe），所以合併路線 > 1 代表分母問題，不代表 m > 1；"
            "(2) 外部分母（H3 (ii)）的 Epoch 區間跨一個數量級；(3) 程式代理對照列不進合併。追蹤規則（J5）：每次升版檢查 OpenAI、Anthropic 是否有新的付費用戶數、"
            "用量或營收拆分揭露，另加季度檢查；Anthropic 公開 S-1 出來時另開工作單。")


def _rows():
    R = {}; r = CAP_START + 2
    for item in SPEC:
        if item[0] is not None: R[item[0]] = r
        r += 1
    return R, r


ROWS, _END = _rows()
BLUE = {("share", "E"), ("days", "C"), ("fee", "C"), ("inshare", "C")}


def cap_in_h(wb):
    """Appended after Cap_In G (asserts v5.31's last row, so nothing is silently moved). No new defined name."""
    ws = wb["Cap_In"]
    assert ws.max_row == CAP_START - 2, f"Cap_In ends at row {ws.max_row}; v5.32 H section expects it to start at row {CAP_START}"
    section(ws, CAP_START, TITLE, 7)
    r = CAP_START + 1
    for c, h in zip("ABCDEFG", ["項目", "單位", "基準", "m 低端", "m 高端", "標記", "說明"]): put(ws, f"{c}{r}", h, F_BOLD)
    r += 1
    for item in SPEC:
        if item[0] is None:
            put(ws, f"A{r}", item[1], F_BOLD); r += 1; continue
        key, lab, unit, c, d, e, tag, note = item
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        fmt = FMT.get(unit)
        for col, v in (("C", c), ("D", d), ("E", e)):
            if isinstance(v, str) and v.startswith("="):
                v = v.format(**ROWS)
                font = F_LINK if (v.startswith("=SRC_") and "*" not in v and "/" not in v) else F_CALC
                put(ws, f"{col}{r}", v, font, fmt=fmt, fill=FILL_KEY if key in ("m_all", "m_all_ext") and col == "C" else None)
            elif isinstance(v, (int, float)):
                assert (key, col) in BLUE, (key, col)
                put(ws, f"{col}{r}", v, F_IN, fmt=fmt)
            else:
                put(ws, f"{col}{r}", v, F_CALC)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True)
        r += 1
    put(ws, f"A{r}", NOTE_END, F_NOTE)
    return dict(start=CAP_START, rows=ROWS, end=r)


# ================================================================== B2: Gov_Map rows for the four blue constants (gov.gm_append_c; appended when absent)
def gov_map_rows(wb):
    ws = wb["Cap_In"]; sc = "切片三（v5.32 m 追蹤）"; out = []
    def chk(key):
        r = ROWS[key]; lab = ws[f"A{r}"].value
        assert lab == LAB[key], (key, lab)
        return r, lab
    r, lab = chk("share")
    out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'E{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '高', 'src': SID["share_base"],
                'rel': f'類比：A 段 N10 區間上緣（{EV["N10"]}）', 'dec': 'X21', 'lo': None, 'hi': None, 'rtext': f'C{r} 的 m 高端端點；0.61–0.82（A 段 N10）',
                'reason': 'A 段第 6 節：訂閱營收高端 10.7 $B＝13.07 × 82%；未能追溯到單一 SRC（低端 0.61、基準 0.70 已連結 SRC）', 'retag': '', 'seg': '無'})
    for key, rtext, reason in (
            ("days", "單值（A 段對照 C）", "A 段對照 C：Claude Code 每日花費 × 每月 21 個活躍工作日；只用於程式代理對照列，不進合併"),
            ("fee", "單值（方案列價，A 段對照 C）", "A 段對照 C：Claude Max 20x 月費列價 $200；未另登錄 SRC；只用於程式代理對照列"),
            ("inshare", "單值（A 段第 4.2 節 Requesty 情境 995：5）", "A 段第 4.2 節：程式代理輸入占 99%+；Requesty 情境取 995：5；只用於程式代理對照列")):
        r, lab = chk(key)
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '單值', 'src': '',
                    'rel': '', 'dec': 'X21', 'lo': None, 'hi': None, 'rtext': rtext, 'reason': reason, 'retag': '', 'seg': '無'})
    return out


# ================================================================== B5: Gov_Map GM594 (CTL_Monetize) reason column, append (guarded)
GM594_TAIL = " ｜v5.32 A 段：可信證據多在 0.3–0.9，方向偏高估；基準暫不改（J1 (a′)），以 L1_MImplied／_Ext 追蹤"


def _monetize_gm_row(ws):
    rows = [r for r in range(5, ws.max_row + 1) if (ws[f"C{r}"].value, ws[f"D{r}"].value) == ("Cap_In", "C64")]
    assert len(rows) == 1 and ws[f"A{rows[0]}"].value == "GM594", rows
    return rows[0]


def gov_update(ws, append_text):
    r = _monetize_gm_row(ws)
    return 1 if append_text(ws[f"N{r}"], GM594_TAIL) else 0


# ================================================================== B3: L1 rows (appended after every existing L1 row; no L1 name moves)
READ_M = ("(1) 模型 token 分母已知偏低（L1_ScaleServe：支出路線服務算力約為 token 路線的 18 倍），所以 L1_MImplied > 1 代表分母問題，不代表 m > 1；"
          "(2) m < 1 時回本條件改為 L ≥ L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m），例如 m＝0.6 時需 L ≥ 0.49，在 L1_GapUtil 的實際利用率下需 L ≥ 0.72，"
          "超過 L 類比區間上緣 0.70")
READ_EXT = ("外部分母＝Epoch 每日 token（SRC_DEM_013，10–100 T／日；基準取幾何中點）× 365 ×（1 − AL_FreeShare，token 口徑；v8.1 M2）；區間跨一個數量級。"
            "(2) m < 1 時回本條件改為 L ≥ L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m），例如 m＝0.6 時需 L ≥ 0.49，在 L1_GapUtil 的實際利用率下需 L ≥ 0.72，"
            "超過 L 類比區間上緣 0.70")


def l1_rows_new():
    rm, rx = ROWS["m_all"], ROWS["m_all_ext"]
    ext = ("CTL_Monetize（模型假設；Gov_Map GM594 區間）", "=CTL_Monetize", "=CTL_Monetize")
    return [
        ("MImplied", "隱含變現率 m — 合併路線（模型 token 分母）", "OpenAI 2025；毛額營收 SRC_DEM_007 ÷（Alloc 付費 token × Cap_In 第 31 列層級組合混合有效單價）；v5.32 J2",
         f"=Cap_In!$C${rm}", f"=Cap_In!$D${rm}", f"=Cap_In!$E${rm}", "x",
         "端點同向組合：低＝token 取高（每則提示 token 數高、免費占比低、API 全年比例高），高反之；營收與單價單值（J2 (iii) 不新增輸入）",
         READ_M, "每則提示 token 數、ChatGPT 免費占比、API 全年平均比例、付費層級組合", "每則提示 token 數、免費占比：Assumed（Alloc_In）",
         *ext, "CTL_Monetize；AL_DPaid；IF_PriceRef_*", f"Cap_In 第 {rm} 列", "分母為模型自身 token 需求（Assumed），非實測；OpenAI 未揭露 ChatGPT token 數"),
        ("MImplied_Ext", "隱含變現率 m — 合併路線（外部 token 分母：Epoch）", "OpenAI 2025；毛額營收 SRC_DEM_007 ÷（Epoch 每日 token × 365 × 付費占比 × 混合有效單價）；v5.32 J2 (i)",
         f"=Cap_In!$C${rx}", f"=Cap_In!$D${rx}", f"=Cap_In!$E${rx}", "x", "SRC_DEM_013 低高（10–100 T／日）；基準＝幾何中點",
         READ_EXT, "Epoch 每日 token、免費占比、付費層級組合", "SRC_DEM_013：1 級、中立（由算力推估）",
         *ext, "CTL_Monetize；SRC_DEM_013；IF_FreeShare；IF_PriceRef_*", f"Cap_In 第 {rx} 列", "Epoch 為前沿實驗室總量推估（含 API），非 OpenAI 揭露"),
    ]


def _gm_ref(wb):
    ws = wb["Gov_Map"]; r = _monetize_gm_row(ws)
    return f"Gov_Map!$K${r}", f"Gov_Map!$L${r}"


def l1_judge(wb):
    """L1 P column of the two new rows: inside／outside the Gov_Map range of CTL_Monetize (replaces the generic ±20% text; I3 does not count it)."""
    ws = wb["L1"]; lo, hi = _gm_ref(wb); out = []
    for name in ("L1_MImplied", "L1_MImplied_Ext"):
        r = int(wb.defined_names[name].attr_text.split("$")[-1])
        assert ws[f"A{r}"].value == name, (name, r)
        rng = f'"落在 "&TEXT({lo},"0.0")&"–"&TEXT({hi},"0.0")&" 區間'
        ws[f"P{r}"].value = (f'=IF(ISNUMBER(D{r}),IF(AND(D{r}>={lo},D{r}<={hi}),{rng}內",{rng}外"),"推算值非數字（本情境）")')
        out.append(r)
    return out


# ================================================================== B3: Checks M1 (WARN; appended after the K section, counted in GOV_Warnings)
def checks_m(wb):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "M. 變現率 m 追蹤檢查（工作單 v5.32 r1 B3，J4 (a)）：M1 為 WARN 計入 GOV_Warnings（不阻擋）", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    lo, hi = _gm_ref(wb)
    put(ws, f"A{r}", "M1"); put(ws, f"B{r}", "L1_MImplied（合併路線、模型 token 分母）基準落在 CTL_Monetize 的 Gov_Map 區間外：1＝區間外", wrap=True)
    put(ws, f"C{r}", "WARN")
    put(ws, f"D{r}", f"=IF(ISNUMBER(L1_MImplied),IF(OR(L1_MImplied<{lo},L1_MImplied>{hi}),1,0),0)", F_CALC, fmt="0")
    put(ws, f"E{r}", f"L1_MImplied；{lo.replace('$', '')}／{hi.replace('$', '')}（GM594 低、高）；模型 token 分母已知偏低，觸發屬預期（J4 (a)）", F_NOTE)
    ref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "WARN 合計（含 H3、K1、M1）"
    return r


# ================================================================== B1: DB_Evidence E279–E301 (17 columns A..Q; layout of v531)
def _ev(n, claim, src, tag, param, cur, new, verdict, note, sids, affected, grade, stance):
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, f"{note}｜A 段暫編 {n}｜{ANDY}｜讀取者：CC（A 段，{REPORT_A}）",
            "已處理", sids, DASH, affected, grade, stance]


MT = "L1_MImplied、L1_MImplied_Ext（v5.32 新列）"
EVIDENCE_V532 = [
    _ev("N01", "OpenAI：消費訂閱 >5,000 萬、付費商用用戶 >900 萬、Codex 每週用戶 160 萬（2026-02-27）", _OAI_SCALE, "Verified／1 級",
        "SRC_Demand 新列（m 追蹤）", DASH, "50 M／9 M／1.6 M", f"採用（X21）：新登錄 {S(19)}–{S(21)}；訂閱、商用時間序列的一手錨點",
        "一手已讀；融資期間有呈現成長的誘因", f"{S(19)}；{S(20)}；{S(21)}", MT, "1", "利害關係方"),
    _ev("N02", "OpenAI：>50M 訂閱、月營收 $2B、「企業」占營收 >40%、API >15B tok/min（2026-03-31）", _OAI_FUND, "Verified／1 級",
        "SRC_Demand；SRC_DEM_011 同文", DASH, "2B／月；>40%", f"採用（X21）：新登錄 {S(22)}、{S(23)}（「企業」口徑註明未定義）；>50M 與 2026-02 同值不另登錄",
        "SRC_DEM_011 已登錄同一公告的 token 數", f"{S(22)}；{S(23)}；SRC_DEM_011（同源）", MT, "1", "利害關係方"),
    _ev("N03", "ChatGPT 消費訂閱 15.5M（2025-01）、>20M（2025-03／04）", _TI_AIN, "Interested-party／2 級", "SRC_Demand 時間序列", DASH, "15.5／20",
        f"部分採用（X21）：新登錄 {S(24)}、{S(25)}（各時點一筆；同一則報導，不獨立）", "時間序列早段", f"{S(24)}；{S(25)}", MT, "2", "利害關係方"),
    _ev("N04", "ChatGPT 消費訂閱 35M（2025-07）", "Reuters 轉述 The Information https://tech.yahoo.com/ai/chatgpt/articles/openai-projected-least-220-million-012027742.html",
        "Interested-party／2 級", "SRC_Demand 時間序列；m 試算的每人口徑", DASH, "35", f"採用（X21）：新登錄 {S(26)}；2025 年中錨點",
        "與 N03 為不同報導", S(26), MT, "2", "利害關係方"),
    _ev("N05", "ChatGPT Plus 2025 年 4,400 萬；2026 年目標 Go 1.12 億／Plus 900 萬（合計 1.22 億，預測）",
        "The Information，經 Xataka https://www.xataka.com/empresas-y-economia/openai-preve-caida-80-sus-ingresos-estrella-chatgpt-go-coste-su-huida-adelante；"
        "經 Shopifreaks（2026-04-29）", "Interested-party／2 級", DASH, DASH, "44；122（預測）",
        "待查：44M 時點不明、二手；預測值不入序列，只作方案組合變化（$20 → $8）的定性證據", "未登錄 SRC", DASH, DASH, "2", "利害關係方"),
    _ev("N06", "ChatGPT 付費商用用戶 2M（2025-02）→ 3M（2025-06）→ 5M（2025-08）→ 7M 席次（2025-11）→ >9M（2026-02）",
        "CNBC（NBC Miami）；TipRanks；The Decoder；OpenAI「1 million businesses」；OpenAI「Scaling AI for everyone」", "Verified／Interested-party／1–2 級",
        "SRC_Demand 時間序列", DASH, "2→9 M", f"採用（X21）：新登錄 {S(27)}–{S(30)}（7M 為「席次」口徑另註）；2026-02 的 9M 即 {S(20)}（N01）",
        "2025-11 改「席次」口徑", f"{S(27)}；{S(28)}；{S(29)}；{S(30)}；{S(20)}", MT, "1–2", "利害關係方"),
    _ev("N07", "OpenAI 平台 400 萬開發者（DevDay 2025）", "Altman DevDay 2025，經 https://alicialyttle.com/openai-devday-2025-what-just-changed-for-builders/",
        "Interested-party／2 級", "API 路線每開發者口徑", DASH, "4 M", f"部分採用（X21）：新登錄 {S(31)}；只作上界分母（「開發者」≠ 付費 API 組織；付費組織數找不到）",
        "與 SRC_DEM_010 同一場合", f"{S(31)}；SRC_DEM_010（同源）", DASH, "2", "利害關係方"),
    _ev("N08", "Anthropic 商用客戶 >30 萬（2025-09）；年付 >$1M 客戶 >500（2026-02）", "Anthropic Series F（GIC 存檔）；Anthropic Series G", "Verified／1 級",
        "SRC_Demand（Anthropic；Alloc_In A8 尚未啟用）", DASH, "300k；500", f"採用（X21）：新登錄 {S(32)}、{S(33)}；Anthropic 消費訂閱數未揭露",
        "Anthropic 序列起點", f"{S(32)}；{S(33)}", DASH, "1", "利害關係方"),
    _ev("N09", "Anthropic 2025 營收：用量計費 3.8、訂閱 0.789、雲端市集 2.16（47%）、付給平台分潤約 0.351 $B", _REUTERS_S1, "Interested-party／2 級",
        "m 偏離來源 (4) 通路分潤", DASH, "分潤 ÷ 市集營收 16%；÷ 總營收 7.6%", f"採用（X21）：新登錄 {S(34)}–{S(37)}；公開 S-1 出來後升級",
        "機密 S-1 經 Reuters；分潤為 Reuters 自行分析", f"{S(34)}；{S(35)}；{S(36)}；{S(37)}", DASH, "2", "利害關係方"),
    _ev("N10", "OpenAI 營收消費訂閱占比 75%（2024-10）、約 70%（2025）；ChatGPT 營收 2.7／3.7（2024 預期）、8／12.7（2025 預期）",
        "CO/AI（Friar）；FT（Global Trade Mag）；NYT（simonwillison）；CTech（The Information）", "Interested-party／2 級", "訂閱路線營收（m 追蹤）",
        "13.07（SRC_DEM_007）", "訂閱 61–82%", f"採用（X22）：新登錄 {S(38)}–{S(41)}；Cap_In H 節訂閱占比 低＝{S(41)} ÷ SRC_DEM_007、基準＝{S(39)}、高 0.82（藍字）",
        "SRC_DEM_007 只有總額", f"{S(38)}；{S(39)}；{S(40)}；{S(41)}；SRC_DEM_007", MT, "2", "利害關係方"),
    _ev("N11", "OpenAI 2026 Q2 營收 6.7 $B；消費約 70%（WSJ）", "WSJ，經 CryptoBriefing https://cryptobriefing.com/openai-revenue-6-7-billion-q2-2026/",
        "Interested-party／2 級", "營收時間序列", DASH, "6.7；70%", f"部分採用（X21）：營收新登錄 {S(42)}；70% 與「企業 >40%」口徑重疊，占比不採用",
        "—", S(42), DASH, "2", "利害關係方"),
    _ev("N12", "Microsoft 分潤：OpenAI 付 Microsoft 營收 20% 至 2030、上限 $38B；Azure 轉售 OpenAI 模型的 20% 回付已停止",
        "The Decoder；Let's Data Science（引 CryptoBriefing）", "Interested-party／2 級", "m 偏離來源 (4)", DASH, "20%",
        f"部分採用（X22）：20% 新登錄 {S(43)}，SRC_DEM_018 備註補記；$38B 上限待查一手；營收維持毛額（J3）", "SRC_DEM_018 備註原已有「Microsoft 分成 20%」",
        f"{S(43)}；SRC_DEM_018", DASH, "2", "利害關係方"),
    _ev("N13", "Claude Code 企業部署平均 $13／開發者·活躍日（p90 <$30），月約 $150–250（舊值 $6／$12）", "https://code.claude.com/docs/en/costs（2026-10-11 讀）",
        "Verified／1 級", "程式代理路線每用戶用量（Cap_In H6 對照列）", DASH, "13 $／日", f"採用（X21）：新登錄 {S(44)}（高欄＝p90 上限 30）；Cap_In H6 程式代理訂閱 m 對照",
        "列價口徑；平均 vs p90 → 分布右偏", S(44), "Cap_In H6（對照列，不進合併）", "1", "利害關係方"),
    _ev("N14", "ChatGPT Enterprise：員工訊息數 p95 ÷ 中位數＝6；每組織推理 token 一年 ×320",
        "OpenAI「The state of enterprise AI 2025」https://openai.com/index/the-state-of-enterprise-ai-2025-report/", "Verified／1 級",
        "平均 vs 中位數（重度用戶占比）", DASH, "6 倍", f"採用（X21）：新登錄 {S(45)}；分布形狀唯一一手（平均 ÷ 中位數 ≈1.8 為 Derived）", "—", S(45), DASH, "1", "利害關係方"),
    _ev("N15", "Pegatron 單一開發者：548M tok／日、快取讀 99.3%、輸入 99.9%（9,987：13）", _PEG, "Analogy（n＝1）／1 級",
        "Cap_In C13（χ）高端；程式代理 token 組合", "0.55（0.3–0.75）", "0.993", f"部分採用（X21）：新登錄 {S(46)}、{S(47)}（只登錄；Cap_In C13 不改）；Cap_In H6 單價結構對照低端",
        "SRC_DEM_014／015 為 OpenRouter 全市場平均", f"{S(46)}；{S(47)}；SRC_DEM_014", "Cap_In H6（對照列）", "1", "中立"),
    _ev("N16", "Requesty：Claude Code 快取命中 91.9%（其他代理 46–89%）", "https://www.requesty.ai/data/coding-agent-cache-hit-rate-apr-2026（2026-05-16）",
        "Interested-party／2 級", "Cap_In C13（χ）", "0.55（0.3–0.75）", "0.92", f"部分採用（X21）：新登錄 {S(48)}（只登錄；Cap_In C13 不改）；Cap_In H6 單價結構對照基準",
        "樣本數未揭露；程式代理 χ 高於 Cap_In 高端 0.75", S(48), "Cap_In H6（對照列）", "2", "利害關係方"),
    _ev("N17", "Anthropic 每週上限：影響 <5% 訂閱者；「一位用戶在 $200 方案上用掉數萬美元的模型用量」",
        "Anthropic 聲明，經 https://simonwillison.net/2025/Jul/28/anthropic/ 與 TechCrunch（2025-07-28）", "Verified（公司聲明，經轉載）／1 級",
        "m 偏離來源 (1) 訂閱吃到飽（定性）", DASH, DASH, "採用（定性）：重度用戶補貼的一手定性證據；不登錄 SRC（無數值）", "Anthropic 有放大濫用的誘因", DASH, DASH, "1", "利害關係方"),
    _ev("N18", "SemiAnalysis：$200 方案上限用量值 $8k–14k 列價（35–70 倍月費）",
        "SemiAnalysis（X 貼文），經 https://pasqualepillitteri.it/en/news/4793/semianalysis-token-value-claude-chatgpt-plans", "Interested-party／2 級",
        "m 偏離來源 (1)", DASH, "35–70 倍", "不採用為數值（SemiAnalysis 不可單獨引用）；登錄為已看過，方向與 N17 一致", "上限用量，不是平均", DASH, DASH, "2", "利害關係方"),
    _ev("N19", "OpenAI Plus 恢復 5 小時上限（2026-08-25）；ChatGPT Pro 500 額度＝Plus 25 倍",
        "9to5Mac（Sottiaux 於 X，2026-08-24）；OpenAI DevDay 2026 https://openai.com/index/devday-2026-recap/", "Verified／1–2 級",
        "m 偏離來源 (1)（定性）", DASH, DASH, "採用（定性）：方案之間每單位額度價格接近，補貼集中在用量接近上限者；不登錄 SRC", "—", DASH, DASH, "1–2", "利害關係方"),
    _ev("N20", "OpenAI 資料分享換免費 token：每組織每日 0.25–10M（依等級）",
        "OpenAI Help Center https://help.openai.com/en/articles/10306912-sharing-feedback-evaluation-and-fine-tuning-data-and-api-inputs-and-outputs-with-openai",
        "Verified／1 級", "m 偏離來源 (5) 付費帳戶內免費額度", DASH, "0.25–10 M／日", "部分採用：機制存在；總量未揭露，不量化、不登錄 SRC", "參與組織數未揭露",
        DASH, DASH, "1", "利害關係方"),
    _ev("N21", "MiniMax：Talkie 付費 139 萬、海螺 AI 訂閱 31 萬、企業客戶 13 萬（2025-09-30）", "MiniMax 招股書（經 Deep News https://www.itiger.com/news/1162773889）",
        "Verified（經二手）／2 級", "MiniMax 模型（不在 Tokenomics）", DASH, DASH, "不採用：Tokenomics 只追 OpenAI；轉交 MiniMax 模型", "招股書原檔本輪未讀",
        DASH, DASH, "2", "利害關係方"),
    _ev("N22", "Google 付費訂閱 3.5 億（全部 Google 服務，2026 Q1）", "Alphabet Q1 2026 法說，經 9to5Google", "Interested-party／2 級", DASH, DASH, "350 M",
        "不採用：未拆 AI 方案", "口徑含 YouTube、Google One", DASH, DASH, "2", "利害關係方"),
    _ev("N23", "Codex 每週用戶約 800 萬（2026-07）", "getpanto 彙整 https://www.getpanto.ai/blog/codex-ai-statistics（未附原始出處）", "Interested-party／3 級",
        "程式代理路線用戶數", DASH, "約 8 M", "待查：彙整站未附原始出處", "—", DASH, DASH, "3", "不明"),
]


def evidence_rows():
    return EVIDENCE_V532


# ================================================================== B5: Decisions X21–X26 (10 columns; layout of v531)
_ANDY_BOTH = f"{ANDY_0941}；Andy 2026-10-11 11:21「了解，接著照建議依序執行」；chat 端建議（A 段查證報告 PR #38），可撤回"
_X = [
    ("X21", "J2 m 追蹤機制", "Cap_In 新增 H 節「m 追蹤（v5.32）」：隱含 m＝付費營收 ÷（付費 token × 混合有效單價），依路線（訂閱、API、合併）× 分母（模型 token：Alloc 第 5、8 列；"
     "外部 token：SRC_DEM_011 年化、SRC_DEM_013 × (1 − IF_FreeShare)）各給基準／m 低端／m 高端；單價＝Cap_In 第 31 列層級組合 × IF_PriceRef_*（不新增輸入）；"
     "程式代理路線（N13，加 N15／N16 的 token 組合）只作對照列，不進合併。L1 新增 L1_MImplied（合併、模型 token）與 L1_MImplied_Ext（合併、外部 token），外部欄＝CTL_Monetize，"
     "判讀「落在 Gov_Map 區間內／外」；SRC_DEM_019–048 與 DB_Evidence E279–E301 登錄；只作追蹤，不驅動任何 IF_",
     "Cap_In H 節；L1_MImplied／_Ext；SRC_DEM_019–048；DB_Evidence E279–E301；Gov_Map 新列", "B1、B2、B3"),
    ("X22", "J3 營收口徑：毛額", "隱含 m 的分子用毛額營收（SRC_DEM_007，不扣 Microsoft 20% 分潤），與模型有效單價口徑一致；分潤是 m 偏離 1 的來源 (4)，不先扣；"
     "訂閱占比 0.61／0.70／0.82（N10，Derived），API 占比＝1 − 訂閱占比", "Cap_In H1；SRC_DEM_038–041、043", "B2"),
    ("X23", "J4 Warning 條件", "Checks M1：L1_MImplied（合併路線、模型 token 分母）基準落在 CTL_Monetize 的 Gov_Map 區間（0.3–1.0）外即 WARN（計入 GOV_Warnings，不阻擋）；"
     "依 v5.32 現值會觸發，屬預期（分母或 m 至少一個有問題）", "Checks M 節", "B3"),
    ("X24", "J5 追蹤頻率", "每次 Tokenomics 升版工作單檢查 OpenAI、Anthropic 是否有新的付費用戶數、用量或營收拆分揭露（工作單 v5.32 第 4 節），另加季度固定檢查"
     "（季報、融資公告、DevDay 後）；Anthropic 公開 S-1 出來時另開工作單", "（流程；無模型格）", "B5"),
    ("X25", "J6 人數口徑：期間平均", "訂閱路線的人數分母用期間平均（2025：約 3,300 萬＝(2025-01 15.5M ＋ 2026-02 50M) ÷ 2），與年營收、年 token 對齊；只用於每人口徑的直覺檢查，不進 m",
     "Cap_In H2", "B2"),
    ("X26", "J1 (a′) CTL_Monetize 不改", "CTL_Monetize 基準 1 與 Gov_Map 區間 0.3–1.0 暫不改：數值量不準前不改，但追蹤區塊（L1_MImplied／_Ext、Checks M1）讓高估程度可見；"
     "chat 端判斷「m＝1 很可能高估（方向中信心、數值低信心；可信證據多落在 0.3–0.9）」", "Cap_In C64（不改）；Gov_Map GM594 理由欄", "B4、B5"),
]
DECISIONS_V532 = [[i, V, f"{i} {t}", txt, DATE, _ANDY_BOTH, "v5.32 已建", where, f"工作單 v5.32 r1 {sec}", "否"] for i, t, txt, where, sec in _X]


# ================================================================== README (version string is built from VERSION; v5.31 text is kept after it)
README_VERSION = (VERSION + "（判斷類，工作單 docs/workorders/20261011_v5.32.md r1；A 段查證 PR #38：變現率 m 追蹤——Cap_In 新增 H 節「m 追蹤」"
                  "（隱含 m＝付費營收 ÷（付費 token × 混合有效單價），訂閱、API、合併 × 模型 token、外部 token 兩種分母；程式代理對照列），"
                  "L1 新增 L1_MImplied、L1_MImplied_Ext（外部欄＝CTL_Monetize），Checks M1（區間外 WARN）；SRC_DEM_019–048、DB_Evidence E279–E301、Decisions X21–X26；"
                  "CTL_Monetize 與既有 IF_／L1_ 數值不變）。以下為 " + v531.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v531.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v531.VERSION.split("_")[-1]):]
README_ROW = ("變現率 m 追蹤（v5.32）",
              "Cap_In H 節：隱含 m＝付費營收 ÷（付費 token × 混合有效單價），只作追蹤與對照，不驅動任何 IF_ 輸出；CTL_Monetize（Cap_In C64）不改（X26，J1 (a′)）。"
              "分子：SRC_DEM_007 × 訂閱占比（0.61／0.70／0.82）與 API 占比（＝1 − 訂閱占比），毛額（X22）。分母兩欄並列：(i) 模型 token＝Alloc 第 5、8 列"
              "（已知偏低，L1_ScaleServe）；(ii) 外部 token＝SRC_DEM_011 年化（API）與 SRC_DEM_013 × 365 ×（1 − IF_FreeShare）（總量）。單價＝Cap_In 第 31 列層級組合 × IF_PriceRef_*。"
              "欄位：C＝基準、D＝m 低端（營收取低、token 取高）、E＝m 高端。L1_MImplied（合併、模型 token）與 L1_MImplied_Ext（合併、外部 token）外部欄＝CTL_Monetize，"
              "判讀「落在 Gov_Map 區間內／外」；Checks M1：L1_MImplied 基準落在區間外即 WARN（X23）。訂閱人數（期間平均，X25）只作每人口徑的直覺檢查。"
              "追蹤規則（X24）：每次升版檢查 OpenAI、Anthropic 新揭露，另加季度檢查。")

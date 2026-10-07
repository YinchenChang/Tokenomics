# v5.25 (work order docs/workorders/20261007_v5.25.md r0): evidence registration only, no model input changes.
#   1.1 SRC_Demand SRC_DEM_014–017 (OpenRouter "State of AI", arXiv 2601.10088v1; pure evidence, no model links)
#   1.2 SRC_Model SRC_MOD_055 (Epoch frontier_ai_models.csv, GPT-6 Astra training compute); L1 row 36 external comparison 033 -> 055
#   1.3 DB_Evidence E247–E250
#   2   Gov_Map GM248 low 512 -> 400 and range text (X12); reason-column notes on GM245–250, GM203–205, GM531; Decisions X11, X12
#   3   README version string (single source: VERSION below; finish.readme reads it)
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v524, so a rebuild never overwrites a later Excel edit.
import v518

VERSION = "20261007_Tokenomics_v5.25"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-07"
V = "v5.25"
DASH = "—"

# ------------------------------------------------------------------ 1.1 OpenRouter "State of AI" (read by CC 2026-10-07)
OR_URL = "https://arxiv.org/html/2601.10088v1"
OR_SRC = ("arXiv 2601.10088v1《State of AI: An Empirical 100 Trillion Token Study with OpenRouter》（OpenRouter Inc.、a16z；"
          f"{OR_URL}；{DATE} CC 讀原文 HTML 並逐字核對）")
OR_PERIOD = "資料期間 2024-11-03 至 2025-11-30（2.5 節）"
OR_STANCE = "OpenRouter 自身路由流量；a16z 為其投資人；樣本偏 API、開發者與代理流量"
OR_APPLIES = "OpenRouter 全市場路由流量"
OR_DATE = "2026-01"                         # arXiv 2601 = 2026-01 submission month; data period in basis
OR_EID = "E247"
OR_NOTE0 = "v5.25 X12 新增（純證據，不連結任何模型格）；"


def _or(i, metric, val, lo, hi, unit, basis, quote, extra=""):
    return dict(id=f"SRC_DEM_{14 + i:03d}", sheet="SRC_Demand", metric=metric, val=val, lo=lo, hi=hi, unit=unit,
                basis=f"平均值（非中位數）；{basis}；{OR_PERIOD}", applies=OR_APPLIES, date=OR_DATE, src=OR_SRC, grade=1,
                stance="利害關係方", stance_note=OR_STANCE, hand="一手（已讀）", status="Active", ev=OR_EID, s="U-V525", use=DASH,
                note=OR_NOTE0 + quote + extra)


SRC_DEM = [
    _or(0, "OpenRouter 每請求平均輸入 token（2025 年末）", 6000, None, None, "tok／請求", "2025 年末",
        "4.3 節、Figure 14：「Average prompt tokens per request have increased roughly fourfold from around 1.5K to over 6K」",
        "；原文另稱平均序列長 2025 年末 over 5,400（4.4 節、Figure 17），與輸入 6K＋輸出 400 不一致，原文未說明"),
    _or(1, "OpenRouter 每請求平均輸出 token（含推理 token；2025 年末）", 400, None, None, "tok／請求", "含推理 token；2025 年末",
        "4.3 節、Figure 15：「completions have nearly tripled from about 150 to 400 tokens」；2.3 節：「Reasoning tokens ... are included within completion tokens」"),
    _or(2, "OpenRouter 程式類輸入長度 ÷ 一般類", 3.5, 3, 4, "倍", "程式類 ÷ 一般類的提示長度",
        "4.4 節、Figure 18：「programming-related prompts now average 3–4 times the token length of general-purpose prompts」；基準取中值 3.5"),
    _or(3, "OpenRouter 推理模型 token 占比（2025 年末）", 0.5, 0.5, None, "%", "全部 token 中經推理模型路由的占比；下限值",
        "4.1 節、Figure 10：「now exceeds fifty percent」（下限值；高端未給）"),
]

# ------------------------------------------------------------------ 1.2 Epoch GPT-6 Astra (read by CC 2026-10-07)
EP_URL = "https://epoch.ai/data/frontier_ai_models.csv"
EP_DOC = "https://epoch.ai/data/ai-models-documentation/records"
EP_EID = "E248"
CONF_DEF = ("Confidence＝Likely。Epoch 定義（" + EP_DOC + "，Confidence 欄）：「Similar to confident in terms of methodology, but the inputs to the methodology are not as reliable.」"
            "該欄適用於 Training compute、Parameters、Training dataset size；Epoch 未給各等級的數值倍數區間")
EP_NOTES = ("CSV Training compute notes 原文：「per OpenAI and affiliates (e.g. Nvidia), 6 Astra was trained on at least 100,000 GB200s in Abilene, Texas "
            "(so 100,000 in \"Hardware quantity\" is a lower bound/underestimate). This suggests around 1e27 FLOP (corresponding to ~100k GB200s over 90 days at 25% FP8 MFU). "
            "See more detailed estimate in this notebook, yielding a CI of ~[5e26, 2e27] FLOP.」")
SRC_MOD = [dict(
    id="SRC_MOD_055", sheet="SRC_Model", metric="GPT-6 Astra 訓練算力（Epoch 估計）", val=1.0001e27, lo=None, hi=None, unit="FLOP",
    basis="訓練總算力（硬體推估；GB200 數為下限；Epoch 信度 Likely）", applies="GPT-6 Astra", date="2026-09-03",
    src=f"Epoch AI frontier_ai_models.csv（{EP_URL}；Model＝GPT-6 Astra 列；{DATE} CC 讀取核對：Training compute (FLOP)＝1.0001e+27、Hardware quantity＝100000、Training hardware＝NVIDIA GB200、Confidence＝Likely）",
    grade=1, stance="中立", stance_note="Epoch 獨立研究；硬體數字轉述 OpenAI 與 NVIDIA", hand="一手（已讀）", status="Active", ev=EP_EID, s="U-V525",
    use="L1!M36｜對照；L1!N36｜對照",
    note=("v5.25 X12 新增：L1 第 36 列（L1_PretrainFLOP_Astra）外部對照，取代 SRC_MOD_033（Grok-3）；與模型值的差距即 J8 缺口。" + CONF_DEF + "。"
          + EP_NOTES + "（notebook 區間未登錄為低／高：工作單「不得自行推定區間」，待 Project 判斷）"))]


def src_new_records():
    return SRC_DEM + SRC_MOD


# ------------------------------------------------------------------ 1.2 L1 row 36 (builder-owned; read by gov._rows_l1)
L1_ASTRA_SID = "SRC_MOD_055"
L1_ASTRA_GAP = "外部為 GPT-6 Astra 的 Epoch 估計（訓練總算力、硬體推估，GB200 數為下限）；與模型值的差距即 J8 缺口（X12）"

# ------------------------------------------------------------------ 1.3 DB_Evidence E247–E250 (17 columns A..Q; same layout as v521／v522)
OR_PAGE_FAIL = ("OpenRouter 個別模型頁（例：openrouter.ai/openai/gpt-6-astra/activity）的輸入／輸出／推理分項為動態載入，chat 端 2026-10-07 以 WebFetch 讀不到"
                "——屬讀取失敗，不代表資料不存在")
EVIDENCE_V525 = [
    ["E247", DATE,
     "OpenRouter：每請求平均輸入 >6K、輸出約 400（含推理）、程式類 3–4 倍、推理模型 token 占比 >50%",
     OR_SRC, "一手（已讀原文）", "Serving C23:E24（GM245–GM250）",
     "ISL 8,192／16,384／32,768；OSL 1,024／2,048／4,096（輸出占比 1/9≈11%）；GM248 區間 512–2,048",
     "輸入 >6K、輸出約 400（輸出占比約 6%）；程式類輸入為一般類 3–4 倍；推理模型 token 占比 >50%（全部為平均值）",
     "部分採納：基準不改；GM248 區間下限 512→400（X12）", V,
     f"讀取者：CC｜讀取日 {DATE}｜4.3 節 Figure 14／15、4.4 節 Figure 17／18、4.1 節 Figure 10、2.3 節逐字核對，與工作單第 1.1 節相符｜{OR_PERIOD}；全部為平均值｜"
     f"原文另稱平均序列長 2025 年末 over 5,400（4.4 節、Figure 17），與輸入 6K＋輸出 400 不一致，原文未說明｜{OR_PAGE_FAIL}",
     "已處理", "SRC_DEM_014；SRC_DEM_015；SRC_DEM_016；SRC_DEM_017", DASH, "Gov_Map GM248 區間（基準輸出影響 0）", "1", "利害關係方"],
    ["E248", DATE,
     "Epoch：GPT-6 Astra 訓練算力 1.0001e27 FLOP（硬體推估，GB200 數為下限；信度 Likely）",
     f"Epoch AI frontier_ai_models.csv（{EP_URL}；Model＝GPT-6 Astra 列）", "一手（已讀原文）",
     "L1 第 36 列；Arch E6–E8、Train_In E25（J8）",
     "L1_PretrainFLOP_Astra＝6.84e25（外部對照 SRC_MOD_033 Grok-3 4.6e26）", "1.0001e27 FLOP（模型 ÷ 外部約 0.068）",
     "採用為 L1 外部對照（X12）；J8 基準不改", V,
     f"讀取者：CC｜讀取日 {DATE}｜CSV 欄位 Training compute (FLOP)＝1.0001e+27、Hardware quantity＝100000、Training hardware＝NVIDIA GB200、Confidence＝Likely，與工作單第 1.2 節相符｜"
     f"{CONF_DEF}｜{EP_NOTES}｜notebook 區間未登錄為低／高（待 Project 判斷）",
     "已處理", "SRC_MOD_055", DASH, "L1_PretrainFLOP_Astra（外部欄與判讀；D:F 不變）", "1", "中立"],
    ["E249", DATE,
     "Epoch 同表：Grok 3 訓練算力 3.5e26、Parameters 3e12（Parameters notes 空白，原始出處未明）；與 SRC_MOD_033（4.6e26，Epoch 另一頁）不同",
     f"Epoch AI frontier_ai_models.csv（{EP_URL}；Model＝Grok 3 列）", "一手（已讀原文）",
     "Arch E6（GM203）；SRC_MOD_033", "GM203 區間 2,000–10,000 B；SRC_MOD_033＝4.6e26", "Grok 3：Training compute 3.5e+26、Parameters 3e12（Parameters notes 空白）",
     "已讀，未採用：參數無出處，只作 GM203 區間（2–10T）內的參考；033 不改，差異記錄待查", V,
     f"讀取者：CC（讀 CSV）｜讀取日 {DATE}｜CSV Grok 3 列：Training compute notes「Estimate based on a cluster of 80,000 H100s per the xai website and an estimated training time of approximately three months.」；"
     "Hardware quantity 80000；Confidence Likely｜與工作單第 1.3 節相符",
     "已處理", "SRC_MOD_033", DASH, "無（純紀錄）", "1", "中立"],
    ["E250", DATE,
     "「GPT-6 Astra 約 10T 參數 MoE」（teamorouter.com 等；原文自稱未證實傳聞，無出處）",
     "teamorouter.com 等（chat 端 2026-10-07 搜尋；摘要級）", "摘要級，原文未讀",
     "Arch E6（GM203）", "GM203 區間 2,000–10,000 B", "約 10T（傳聞）",
     "不採納（R6：找不到原始出處）；10T 已是 GM203 區間上限", V,
     "讀取者：chat 端（2026-10-07 搜尋）；摘要級，不得標為已讀原文｜原文自稱未證實傳聞、無出處",
     "已處理", DASH, DASH, "無", "3", "未明（傳聞，無出處）"],
]


def evidence_rows():
    return EVIDENCE_V525


# ------------------------------------------------------------------ 2.1 Gov_Map GM248 (Serving C24) low 512 -> 400 and range text
GM248_K_OLD = ("=Serving!C24*0.5", 512)     # formula (v5.24; = 512 while Serving!C24 = 1024) or the literal 512
GM248_K_NEW = 400
GM248_M_OLD = "×0.5–×2（Claude 提議，Andy 2026-10-03 確認）"
GM248_M_NEW = "400–2,048（下限依 E247 放寬，X12）"
# 2.2 reason-column (N) notes (guarded append; same convention as v520／v521)
NOTE_OR = " ｜v5.25 X12：OpenRouter 市場平均輸入 >6K、輸出約 400（E247）；基準不改"
NOTE_EP = " ｜v5.25 X12：Epoch GPT-6 Astra 1.0e27（E248）；J8 未結"
GOV_NOTES = [(f"GM{n}", NOTE_OR) for n in range(245, 251)] + [(g, NOTE_EP) for g in ("GM203", "GM204", "GM205", "GM531")]
GOV_CHECK = {"GM248": ("Serving", "C24"), "GM245": ("Serving", "C23"), "GM250": ("Serving", "E24"), "GM203": ("Arch", "E6"), "GM531": ("Train_In", "E25")}


def gov_update(ws, append_text):
    from common import F_IN
    from copy import copy
    rows = {ws[f"A{r}"].value: r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value}
    for gm, (sh, cell) in GOV_CHECK.items():
        r = rows[gm]
        assert (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sh, cell), f"Gov_Map {gm} is {ws[f'C{r}'].value}!{ws[f'D{r}'].value}, expected {sh}!{cell}"
    n = 0
    r = rows["GM248"]
    c = ws[f"K{r}"]
    if c.value in GM248_K_OLD and ws.parent["Serving"]["C24"].value == 1024:
        c.value = GM248_K_NEW; c.font = copy(F_IN); n += 1
    if ws[f"M{r}"].value == GM248_M_OLD:
        ws[f"M{r}"].value = GM248_M_NEW; n += 1
    for gm, txt in GOV_NOTES:
        if append_text(ws[f"N{rows[gm]}"], txt): n += 1
    return n


# ------------------------------------------------------------------ 2.3 Decisions X11, X12 (10 columns; same layout as v523)
ANDY = "「基本上就用你的建議值就好了，你自己先看着办吧」（2026-10-07，經 chat 端轉達）"
X12_TEXT = ("(a) Serving C23:E24（參考 ISL／OSL）基準不改；只把 GM248（C24，Luna OSL）區間下限 512 → 400。(b) Arch E6–E8、Train_In E25（Astra）基準不改，J8 維持未結。"
            "(c) L1 第 36 列（L1_PretrainFLOP_Astra）外部對照由 SRC_MOD_033（Grok-3）改為 SRC_MOD_055（GPT-6 Astra，Epoch）。"
            "依據：OSL——OpenRouter 全市場平均每請求輸入 over 6K、輸出約 400（含推理 token），輸出占比約 6%；模型三層級皆 1/9≈11%；OpenRouter 偏 API 與代理流量，"
            "本模型 Workload 頁的消費聊天輸出占比為一般聊天 17%（500／3,000）、推理聊天 60%（3,700／6,200），11% 介於兩者之間，基準不改；Luna 為最接近 OpenRouter 主流量（Flash 級）的層級，"
            "其區間下限放寬到 400 以涵蓋市場平均。ISL——市場平均 6K 落在 Luna 區間 4,096–16,384 內；程式類為一般的 3–4 倍，與 Sol／Astra 基準 16K／32K 及 E211（Copilot 每呼叫中位 68K）一致；"
            "基準與區間皆不改。J8——Epoch 對 GPT-6 Astra 的訓練算力估計 1.0001e27 FLOP（硬體推估，10 萬顆 GB200 為下限），模型 L1_PretrainFLOP_Astra＝6.84e25，比值約 0.068；"
            "缺口來自啟用參數、token 數或 RL 占比中的哪一項，公開資料無法分離（OpenAI 未揭露參數），故不改基準；把對照改為同一模型的估計，讓缺口直接可見。"
            "硬性停止條件檢查：本單無任何下游取數值變動，未觸及。")
DECISIONS_V525 = [
    ["X11", V, "GM595（CAL_BatchEtaD）P 欄維持「中」",
     "v5.23 報告第十節第 6 項：GM595（CAL_BatchEtaD）Gov_Map P 欄維持「中」。X2 清單輸出擺動最大 +3.2%／−11.0%，未達 20%；不在 X2 清單的訓練成本與 RL rollout GPU 小時（+14%～+20%）另列監控，"
     "日後若納入 X2 清單再重判。依據：規則字面一致",
     DATE, ANDY, "v5.25 已建", "Gov_Map GM595（P 欄不變）", "工作單 v5.25 第 0 節", "否"],
    ["X12", V, "ISL／OSL 與 Astra 架構證據登錄；L1 前沿算力對照改 GPT-6 Astra", X12_TEXT,
     DATE, ANDY, "v5.25 已建",
     "Gov_Map GM248、L1 L36:N36／S36、SRC_DEM_014–017、SRC_MOD_055、DB_Evidence E247–E250", "工作單 v5.25 第 0、1、2 節", "否"],
]

# ------------------------------------------------------------------ README (version string is built from VERSION; v5.24 text is kept after it)
import v524
README_VERSION = (VERSION + "（X12：證據登錄——SRC_Demand 新增 SRC_DEM_014–017（OpenRouter《State of AI》，arXiv 2601.10088v1；純證據）、SRC_Model 新增 SRC_MOD_055（Epoch GPT-6 Astra 訓練算力 1.0001e27）、"
                  "DB_Evidence E247–E250；L1 第 36 列（L1_PretrainFLOP_Astra）外部對照由 SRC_MOD_033 改為 SRC_MOD_055；Gov_Map GM248 區間下限 512→400；Decisions X11、X12；"
                  "模型輸入值與所有模型頁數值不變；工作單 docs/workorders/20261007_v5.25.md）。以下為 " + v524.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v524.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v524.VERSION.split("_")[-1]):]

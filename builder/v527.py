# v5.27 (work order docs/workorders/20261008_v5.27.md r0): evidence registration and L1 external comparisons; no model input changes.
#   1.1 SRC_MOD_055 low／high (Epoch notebook CI ~[5e26, 2e27]); L1 row 36 M／N -> SRC_MOD_055_Lo／_Hi
#   1.2 Grok-3 (SRC_MOD_033): CC read Epoch "models over 1e25 FLOP" on 2026-10-08 -> still 4.6e+26, so the "no new record" branch
#       of X13 (b): no SRC_MOD_056, SRC_MOD_033 unchanged, Train_In H46:H48 unchanged; only E249 note appended (guarded)
#   1.3 SRC_MOD_057–062 Kimi K3 architecture (pure evidence, no model links)
#   1.4 DB_Evidence E251–E255
#   1.5 Gov_Map reason-column notes (GM576, GM580, GM203–205, GM209, GM210, GM531)
#   2   L1 row 39 (L1_Ans3) external comparison -> SRC_DEM_006; S39 text
#   0   Decisions X13
#   3.4 README version string (single source: VERSION below; finish.readme reads it)
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v525, so a rebuild never overwrites a later Excel edit.
import v526

VERSION = "20261008_Tokenomics_v5.27"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-08"
V = "v5.27"
DASH = "—"

# ------------------------------------------------------------------ 1.2 path taken (CC read both Epoch pages on DATE)
GROK_PATH = "4.6e26"                        # "3.5e26" would add SRC_MOD_056 and supersede 033; not taken (see E252)
EP_URL = "https://epoch.ai/data/frontier_ai_models.csv"
EP_PAGE = "https://epoch.ai/data-insights/models-over-1e25-flop"

# ------------------------------------------------------------------ 1.1 SRC_MOD_055 low／high (Excel-owned row; guarded)
MOD055_ID = "SRC_MOD_055"
MOD055_VAL = 1.0001e27
MOD055_LO, MOD055_HI = 5e26, 2e27
MOD055_NOTE = (" ｜v5.27 X13 (a)：低 5e26、高 2e27 依上列 notes 原句「See more detailed estimate in this notebook, yielding a CI of ~[5e26, 2e27] FLOP.」登錄"
               f"（{DATE} CC 以 WebFetch 讀 {EP_URL} GPT-6 Astra 列逐字核對）；前句「notebook 區間未登錄為低／高」已由本項取代")


def src_update(wb):
    """SRC_MOD_055 D／E only while both are empty and C still holds the v5.25 value; W note appended once. Returns (n, log)."""
    import v518
    from common import F_IN
    from copy import copy
    ws = wb["SRC_Model"]; n = 0; log = []
    rows = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == MOD055_ID]
    if not rows: return 0, [f"{MOD055_ID} not found (left as is)"]
    r = rows[0]
    if ws[f"C{r}"].value == MOD055_VAL and ws[f"D{r}"].value is None and ws[f"E{r}"].value is None:
        for col, v in (("D", MOD055_LO), ("E", MOD055_HI)):
            ws[f"{col}{r}"].value = v; ws[f"{col}{r}"].font = copy(F_IN); n += 1
        log.append(f"SRC_Model!D{r}:E{r} {MOD055_ID} low／high -> {MOD055_LO}／{MOD055_HI}")
    if v518._append_text(ws[f"W{r}"], MOD055_NOTE): n += 1; log.append(f"SRC_Model!W{r} {MOD055_ID} note appended")
    return n, log


# ------------------------------------------------------------------ 1.3 Kimi K3 (read by CC on DATE)
K3_CFG = "https://huggingface.co/moonshotai/Kimi-K3/blob/main/config.json"
K3_CARD = "https://huggingface.co/moonshotai/Kimi-K3"
K3_SRC = (f"Hugging Face moonshotai/Kimi-K3：config.json（{K3_CFG}）與模型卡 Model Summary 表（{K3_CARD}）；"
          f"{DATE} CC 以 WebFetch 讀取，關鍵行讀兩次逐字核對")
K3_STANCE = "Moonshot 自揭；config 與權重一同發布、可由權重形狀互證，誤報誘因低（同 DeepSeek 紀錄慣例）"
K3_APPLIES = "Kimi K3（Moonshot，開放權重；Astra 架構可比）"
K3_EID = "E253"
K3_NOTE0 = "v5.27 X13 (e) 新增（純證據，不連結任何模型格；Astra 基準不改）；"


def _k3(i, metric, val, unit, basis, quote):
    return dict(id=f"SRC_MOD_{57 + i:03d}", sheet="SRC_Model", metric=metric, val=val, lo=None, hi=None, unit=unit, basis=basis,
                applies=K3_APPLIES, date="2026", src=K3_SRC, grade=1, stance="利害關係方", stance_note=K3_STANCE,
                hand="一手（已讀）", status="Active", ev=K3_EID, s="U-V527", use=DASH, note=K3_NOTE0 + quote)


SRC_MOD = [
    _k3(0, "Kimi K3 總參數", 2800, "B", "模型卡 Model Summary（config.json 未載明參數量）",
        "模型卡原文「Total Parameters | 2.8T」；config.json 無參數量欄位；二手轉述（genaiassembling.substack.com）稱 2.78T"),
    _k3(1, "Kimi K3 啟用參數", 104, "B", "模型卡 Model Summary（config.json 未載明參數量）",
        "模型卡原文「Activated Parameters | 104B」；config.json 無參數量欄位；二手轉述（genaiassembling.substack.com）稱 104.2B"),
    _k3(2, "Kimi K3 層數（num_hidden_layers）", 93, "層", "config.json text_config.num_hidden_layers",
        "config.json 原文「\"num_hidden_layers\": 93,」；模型卡「Number of Layers | 93」（含 Dense 1 層；注意力 69 KDA＋24 Gated MLA）"),
    _k3(3, "Kimi K3 d_model（hidden_size）", 7168, "維", "config.json text_config.hidden_size",
        "config.json 原文「\"hidden_size\": 7168,」；模型卡「Attention Hidden Dimension | 7168」"),
    _k3(4, "Kimi K3 routed experts（num_experts）", 896, "個", "config.json text_config.num_experts",
        "config.json 原文「\"num_experts\": 896,」；模型卡「Number of Experts | 896」；另有 shared experts 2（\"num_shared_experts\": 2）"),
    _k3(5, "Kimi K3 每 token 啟用 routed experts（num_experts_per_token）", 16, "個", "config.json text_config.num_experts_per_token",
        "config.json 原文「\"num_experts_per_token\": 16,」；模型卡「Selected Experts per Token | 16」"),
]
K3_IDS = [r["id"] for r in SRC_MOD]


def src_new_records():
    return SRC_MOD


# ------------------------------------------------------------------ 1.1 L1 row 36 and 2 L1 row 39 (builder-owned; read by gov._rows_l1)
L1_ASTRA_ELO = f"={MOD055_ID}_Lo"
L1_ASTRA_EHI = f"={MOD055_ID}_Hi"
ANS3_SID = "SRC_DEM_006"
ANS3_GAP = ("未能回答：非算力成本（人事、資料、評測、非 GPU 費用）不在第 0 層，歸 OpenAI 模型。外部對照為 OpenAI 揭露 2025 訓練支出（利害關係方，2 級）；"
            "本列絕對值約為其 1/10，服務端同幅度偏小（Alloc 第 61 列），只宜取比值口徑（Q1、Q2），絕對規模由 OpenAI 模型校準（X13 c）。")


def l1_rows(R):
    """Ans3 tuple: L (SRC_ID), M／N (external low／high), S (gap text). D:F and everything else unchanged."""
    out = []
    for row in R:
        if row[0] == "Ans3":
            row = list(row)
            row[11], row[12], row[13], row[16] = ANS3_SID, f"={ANS3_SID}", f"={ANS3_SID}", ANS3_GAP
            row = tuple(row)
        out.append(row)
    return out


# ------------------------------------------------------------------ 1.4 DB_Evidence E251–E255 (17 columns A..Q; same layout as v525)
GROK_PAGE_QUOTE = ("「Grok-3 | 4.6e+26 | High-precision」；表列「…Grok 3 Beta — The Age of Reasoning Agents https://x.ai/blog/grok-3 4.6e+26 … Confident …」；"
                   "頁面日期「Jan. 30, 2025 (updated Jun. 6, 2025)」；3.5e+26 未出現在該頁")
GROK_CSV_QUOTE = ("CSV Grok 3 列：Training compute (FLOP)＝3.5e+26；Training compute notes「Estimate based on a cluster of 80,000 H100s per the xai website "
                  "and an estimated training time of approximately three months.」")
E249_NOTE = (f" ｜v5.27（E252）：{DATE} CC 再讀兩處 Epoch——{EP_PAGE} 仍為 4.6e+26（{GROK_PAGE_QUOTE}）；{EP_URL} Grok 3 列為 3.5e+26。"
             "兩處不一致，依 X13 (b) 不改 SRC_MOD_033")
EVIDENCE_V527 = [
    ["E251", DATE,
     "Epoch：GPT-6 Astra 訓練算力 CI ~[5e26, 2e27]（Training compute notes 原句）",
     f"Epoch AI frontier_ai_models.csv（{EP_URL}；Model＝GPT-6 Astra 列）", "一手（已讀原文）",
     "L1 第 36 列；SRC_MOD_055", "SRC_MOD_055 低／高空白；L1 M36＝N36＝1.0001e27（判讀「差距 >20%」）",
     "低 5e26、高 2e27（基準 1.0001e27 不變）", "採納為區間（X13 a）", V,
     f"讀取者：CC｜讀取日 {DATE}｜WebFetch 讀兩次：notes 末句逐字為「See more detailed estimate in this notebook, yielding a CI of ~[5e26, 2e27] FLOP.」，"
     "與工作單第 1.1 節相符（第一次逐字讀取未回出此句，指定查詢後第二次讀出；同 chat 端 2026-10-07 第二次讀取漏句的情形）｜"
     "另記：chat 端 2026-10-07 第二次逐字讀取曾漏掉此句，於 v5.25 審查時更正",
     "已處理", "SRC_MOD_055", DASH, "L1_PretrainFLOP_Astra（外部欄與判讀；D:F 不變）", "1", "中立"],
    ["E252", DATE,
     "Grok-3 算力兩處 Epoch 數字查核：models-over-1e25-flop 頁 4.6e26；frontier_ai_models.csv 3.5e26",
     f"Epoch AI {EP_PAGE}；{EP_URL}（Model＝Grok 3 列）", "一手（已讀原文）",
     "SRC_MOD_033（Train_In C46:C48 錨點來源）", "SRC_MOD_033＝4.6e26（Active）", "頁面 4.6e+26（未改）；CSV 3.5e+26",
     "該頁仍為 4.6e26：不新增、不取代（X13 b 後一路）；E249 備註附加兩處數字與讀取日；Train_In C46:C48 不改", V,
     f"讀取者：CC｜讀取日 {DATE}｜頁面讀兩次，皆只見 4.6e+26：{GROK_PAGE_QUOTE}｜{GROK_CSV_QUOTE}",
     "已處理", "SRC_MOD_033", DASH, "無（純紀錄）", "1", "中立"],
    ["E253", DATE,
     "Kimi K3 架構：總參數 2.8T、啟用 104B、93 層、hidden 7168、896 routed experts、每 token 16（另 shared 2；注意力 69 KDA＋24 Gated MLA）",
     K3_SRC, "一手（已讀原文）",
     "Arch E6–E8、E12、E13（GM203–GM205、GM209、GM210）",
     "Astra：總參數 4,000 B（區間 2,000–10,000）、啟用 180 B（60–250）、100 層（80–160）、routed 512（256–1,024）、每 token 16（8–32）",
     "2,800 B、104 B、93 層、896、16",
     "已讀，作為可比；Astra 基準不改（X13 e）", V,
     f"讀取者：CC｜讀取日 {DATE}｜config.json（text_config）逐字讀兩次：\"num_hidden_layers\": 93、\"hidden_size\": 7168、\"num_experts\": 896、"
     "\"num_experts_per_token\": 16、\"num_shared_experts\": 2；config.json 無參數量與訓練 token 欄位，總參數與啟用參數取自同 repo 模型卡"
     "（「Total Parameters | 2.8T」「Activated Parameters | 104B」）｜工作單引用的二手轉述（2.78T、104.2B、93 層、896／16、KDA 與 MLA 3:1）與一手相符（精度不同）｜"
     "總參數 2.8T 落在 GM203 區間 2–10T 下段；啟用 104B 在 GM204 區間 60–250B 內；93 層在 GM205 區間 80–160 內；896 在 GM209 區間 256–1,024 內；16 等於 GM210 基準｜"
     "預訓練 token：config 與模型卡皆未載明；技術報告 PDF（github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf）讀取失敗（容器下載 403、WebFetch 權限請求逾時），未能查",
     "已處理", "、".join(K3_IDS), DASH, "無（純證據）", "1", "利害關係方"],
    ["E254", DATE,
     "硬體錨點：Epoch GPT-6 Astra ≥10 萬顆 GB200 × 約 90 天＝≥2.16 億 GB200 GPU 小時；模型 IF_TrainGPUh_Astra GB200 基準欄＝3.868e7（比值 ≥5.6）",
     f"Epoch AI frontier_ai_models.csv（{EP_URL}；GPT-6 Astra 列 notes）；本活頁簿 v5.26 快取值", "chat 端已讀（2026-10-08）",
     "Alloc_In C8 k（GM580）、C6 N_major（GM576）；L1_Ans3",
     "k＝1、N_major＝1；L1_Ans3＝1.157 $B；Q1 0.636；token 路線服務 GW 0.052、隱含 N × k 1.52（Alloc 第 57 列）",
     "支出路線隱含 N × k＝21.8（研發 GW 1.061 ÷ 家族計畫 GW 年 0.0486）；支出路線服務 GW 0.743（Alloc 第 61 列）；OpenAI 2025 訓練支出 12 $B（SRC_DEM_006）",
     "已讀，基準不改（X13 c）；兩端規模同幅度偏小，比值口徑可用，絕對規模歸 OpenAI 模型校準", V,
     f"讀取者：chat 端（2026-10-08）｜CC {DATE} 以 v5.26 活頁簿快取值核對：IF_TrainGPUh_Astra GB200 基準欄（Interface F72）＝38,678,967；"
     "2.16e8 ÷ 3.868e7＝5.58；Alloc C37:E37 合計（F37，AL_FamGWyr）＝0.04864；C55 支出比＝0.5882；C56 隱含研發 GW（token 路線）＝0.0741；"
     "C57 隱含 N × k＝1.524；C61 支出路線服務 GW＝0.7427；支出路線研發 GW＝0.5882 ÷ 0.4118 × 0.7427＝1.061；1.061 ÷ 0.04864＝21.8；"
     "L1_Ans3＝1.1573；IF_AllocQ1＝0.6361；IF_AllocServeGW＝0.0519——與工作單第 1.4 節相符",
     "已處理", "SRC_MOD_055；SRC_DEM_006", DASH, "L1_Ans3（外部欄與判讀；D:F 不變）", DASH, DASH],
    ["E255", DATE,
     "Train_In E25：2026 年公開技術報告未見新的預訓練 token 揭露（Kimi K3 未載明；Raschka 2026-01–02 十款開放權重模型只有 Kimi K2.5 載明約 15T 視覺與文字混合 token）",
     "chat 端 2026-10-08 搜尋（Raschka 2026-01–02 開放權重模型整理等；摘要級）", "摘要級，原文未讀",
     "Train_In E25（GM531）", "Astra 預訓練 token 60T（區間 30–100T）", "未揭露（Kimi K2.5 約 15T 混合 token）",
     "已搜尋；區間 30–100T 與基準 60T 不改", V,
     f"讀取者：chat 端（2026-10-08）；摘要級，不得標為已讀原文｜CC {DATE} 補：Kimi K3 config.json 與模型卡皆未載明預訓練 token（見 E253）",
     "已處理", DASH, DASH, "無", "3", "未明（摘要級）"],
]


def evidence_rows():
    return EVIDENCE_V527


def evidence_update(wb):
    """E249 note (K column) appended once (guarded by text presence). Returns n."""
    import v518
    ws = wb["DB_Evidence"]
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "E249":
            return 1 if v518._append_text(ws.cell(r, 11), E249_NOTE) else 0
    return 0


# ------------------------------------------------------------------ 1.5 Gov_Map reason-column (N) notes (guarded append; same convention as v525)
NOTE_K = " ｜v5.27 X13：E254；基準不改，比值口徑"
NOTE_K3 = " ｜v5.27：Kimi K3（E253）"
NOTE_E25 = " ｜v5.27：E255"
GOV_NOTES = [("GM580", NOTE_K), ("GM576", NOTE_K)] + [(g, NOTE_K3) for g in ("GM203", "GM204", "GM205", "GM209", "GM210")] + [("GM531", NOTE_E25)]
GOV_CHECK = {"GM580": ("Alloc_In", "C8"), "GM576": ("Alloc_In", "C6"), "GM203": ("Arch", "E6"), "GM204": ("Arch", "E7"), "GM205": ("Arch", "E8"),
             "GM209": ("Arch", "E12"), "GM210": ("Arch", "E13"), "GM531": ("Train_In", "E25")}


def gov_update(ws, append_text):
    rows = {ws[f"A{r}"].value: r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value}
    for gm, (sh, cell) in GOV_CHECK.items():
        r = rows[gm]
        assert (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sh, cell), f"Gov_Map {gm} is {ws[f'C{r}'].value}!{ws[f'D{r}'].value}, expected {sh}!{cell}"
    n = 0
    for gm, txt in GOV_NOTES:
        if append_text(ws[f"N{rows[gm]}"], txt): n += 1
    return n


# ------------------------------------------------------------------ 0 Decisions X13 (10 columns; same layout as v525)
ANDY = "「基本上就用你的建議值就好了，你自己先看着办吧」（2026-10-07，經 chat 端轉達）"
X13_TEXT = ("(a) SRC_MOD_055（GPT-6 Astra 訓練算力，Epoch）登錄 Epoch notes 所述區間：低 5e26、高 2e27；L1 第 36 列外部欄改連 _Lo／_Hi。"
            "(b) Grok-3 算力：Epoch 現行資料表為 3.5e26（E249）；「models over 1e25 FLOP」頁若已改為 3.5e26 則新增 Active 紀錄取代 SRC_MOD_033，"
            "若仍為 4.6e26 只在 E249 記錄兩處不一致、不改 SRC——v5.27 CC 讀取結果該頁仍為 4.6e26，採後者（E252）；Train_In C46:C48 錨點（2e26／5e26／2e27）不改。"
            "(c) Alloc k、N_major 基準不改（k＝1、N_major＝1）。理由：模型研發算力成本 L1_Ans3＝1.157 $B，約為 OpenAI 揭露 2025 訓練支出 12 $B（SRC_DEM_006）的 1/10；"
            "服務端 token 路線服務 GW（0.052）亦約為支出路線（0.743，Alloc 第 61 列）的 1/14。兩端同幅度偏小，故比值 Q1（0.636）接近揭露支出比 0.588。"
            "只上調 k（例如 Epoch 硬體錨點隱含的 ≥5.6）會使 Q1 升至約 0.91，與支出比矛盾。絕對機隊規模屬公司資料（Andy 2026-10-06 範圍決定），由 OpenAI 模型同時校準研發與服務兩端；"
            "Tokenomics 只揭露此落差。(d) L1_Ans3 外部對照連 SRC_DEM_006（OpenAI 2025 訓練支出），使上項落差在 L1 直接可見。"
            "(e) Train_In E25（Astra 預訓練 60T）與 Arch E6–E8 基準不改；Kimi K3 登錄為架構可比（純證據）。"
            "硬性停止條件檢查：本單無任何下游取數值變動，未觸及。")
DECISIONS_V527 = [
    ["X13", V, "J8 證據與 L1 外部對照（Epoch 區間、Grok-3 查核、Ans3 對照揭露支出）、Kimi K3 架構證據", X13_TEXT,
     DATE, ANDY, "v5.27 已建",
     "SRC_MOD_055 低／高、L1 L36:P36、L39:P39、S39、SRC_MOD_057–062、DB_Evidence E251–E255（E249 備註）、Gov_Map GM576／GM580／GM203–205／GM209／GM210／GM531 理由欄",
     "工作單 v5.27 第 0、1、2 節", "否"],
]

# ------------------------------------------------------------------ README (version string is built from VERSION; v5.26 text is kept after it)
README_VERSION = (VERSION + "（X13：J8 證據與 L1 外部對照——SRC_MOD_055 登錄 Epoch 區間低 5e26／高 2e27，L1 第 36 列外部欄改連 _Lo／_Hi；"
                  "L1 第 39 列（L1_Ans3）外部對照連 SRC_DEM_006（OpenAI 2025 訓練支出）；Grok-3 查核：Epoch 1e25 頁仍為 4.6e26，SRC_MOD_033 不改（E252）；"
                  "SRC_Model 新增 SRC_MOD_057–062（Kimi K3 架構，純證據）；DB_Evidence E251–E255；Gov_Map 理由欄附註；Decisions X13；"
                  "模型輸入值與所有模型頁數值不變；工作單 docs/workorders/20261008_v5.27.md）。以下為 " + v526.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v526.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v526.VERSION.split("_")[-1]):]

# v10.2 (work order docs/workorders/20261016_η校準.md, branch claude/batch4-wo; segment "η 校準與驗證判準").
#   E1  generation conversion: Calib J section = calibration copy rows (Hopper: DeepSeek profile 2,324; GB200: vLLM 10.1K) that show model ÷ target and the multiplier that would be needed.
#       The stop rule of the work order applies: the Hopper copy row is bounded by the EP-communication term (no C67 value reaches the target), the GB200 solution (x2.8-3.0) puts the effective
#       GB200 compute above GB300 and fails V5. Calib C67 (1.2) and D67 (1) are therefore NOT written; the solved values are shown on the copy rows and reported for Project to decide.
#   E2  Serving row 21 (SLO, tok/s/user) = geometric mean of the Artificial Analysis and OpenRouter medians (SRC_PERF_066-071); old values (120/65/55) stay as scenario slo_v10.
#   E3  Checks V: V2 (MLPerf v6.0 server GB200 NVIDIA 72 GPU), V3 (same round GB300 72-GPU rack), V7/V8 (LMSYS conditions aligned, Calib J), V13/V14 upper bound 3, new V15 (DeepSeek online 1,850),
#       B26 and B36 counted again as V16/V17.
#   E4  Perf_Batch R-S columns kept (Sens_Train W59:X62 reads them): header and registry notes say so.
# Every write to an Excel-owned cell is guarded (old value / old text). Minor version: no new contract name.
import re
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY, section
import v1000
import v1010

VERSION = "20261016_Tokenomics_v10.2"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-16"
V = "v10.2"
WO = "工作單 docs/workorders/20261016_η校準.md（分支 claude/batch4-wo，PR #78）"
DEC_BY = "Andy 2026-10-16 18:18「都依建議」（E1–E4）；E4 為 18:22 決定 (b)；細節預設由 chat 端補充，可撤回"
EID = "E379"
DASH = "—"
REPORT = "docs/reports/20261016_服務條件查證.md"
EVTAB = "docs/evidence/20261016_服務條件/證據表.xlsx"

# ================================================================== SRC records (SRC_Perf 066-078)
_SRC = f"{REPORT} 與 {EVTAB}（CC 查證，2026-10-16；原始出處見證據表）"


def _rec(i, metric, val, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note, second="—"):
    r = v1000._rec(i, "SRC_Perf", metric, val, None, None, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note)
    r["ev"] = EID; r["s"] = "U-V1020"
    if second != "—": r["second"] = second
    return r


_AA = "Artificial Analysis（第三方量測商；以 API 探測請求量測，OpenAI 端點，72 小時中位數，10K 輸入探測）"
_OR = "OpenRouter（路由商；OpenAI 端點，實際流量 P50）"
_SLO_USE = "Serving!C21／D21／E21（兩家中位數的幾何平均）"
SRC_NEW = [
    _rec("SRC_PERF_066", "輸出速度（AA 中位）：GPT-6 Luna", 116.5, "tok/s/user", "每用戶輸出速度（首 chunk 之後）；" + _AA, "GPT-6 Luna", "2026-10",
         "https://artificialanalysis.ai/models/gpt-6-luna/providers", 2, "中立", "第三方量測，無賣方利益；探測請求（低頻），數值系統性高於實際流量", "一手（WebFetch 摘要）", _SLO_USE + "｜Luna",
         f"v10.2 E2（{EID}）：Luna 層代表模型 GPT-6 Luna；與 SRC_PERF_067 取幾何平均", second="SRC_PERF_067"),
    _rec("SRC_PERF_067", "輸出速度（OpenRouter P50）：GPT-6 Luna", 61, "tok/s/user", "每用戶輸出速度；" + _OR, "GPT-6 Luna", "2026-10",
         "https://openrouter.ai/models/openai/gpt-6-luna", 2, "中立", "第三方量測，實際流量；延遲 2.59 s", "一手（WebFetch 摘要）", _SLO_USE + "｜Luna",
         f"v10.2 E2（{EID}）：與 SRC_PERF_066 取幾何平均；兩家量測商系統性相差 1.5–2 倍（原因未查明）", second="SRC_PERF_066"),
    _rec("SRC_PERF_068", "輸出速度（AA 中位）：GPT-6.1 Sol (medium)", 50.7, "tok/s/user", "每用戶輸出速度（首 chunk 之後）；" + _AA, "GPT-6.1 Sol (medium)", "2026-10",
         "https://artificialanalysis.ai/models/gpt-6-1-sol-medium/providers", 2, "中立", "第三方量測，無賣方利益", "一手（WebFetch 摘要）", _SLO_USE + "｜Sol",
         f"v10.2 E2（{EID}）：Sol 層代表模型 GPT-6.1 Sol（現行 API 與 ChatGPT／Codex 主力；chat 端預設）", second="SRC_PERF_069"),
    _rec("SRC_PERF_069", "輸出速度（OpenRouter P50）：GPT-6.1 Sol", 37, "tok/s/user", "每用戶輸出速度；" + _OR, "GPT-6.1 Sol", "2026-10",
         "https://openrouter.ai/models/openai/gpt-6.1-sol", 2, "中立", "第三方量測，實際流量；延遲 3.36 s", "一手（WebFetch 摘要）", _SLO_USE + "｜Sol",
         f"v10.2 E2（{EID}）：與 SRC_PERF_068 取幾何平均", second="SRC_PERF_068"),
    _rec("SRC_PERF_070", "輸出速度（AA 中位）：GPT-6 Astra (high)", 52.1, "tok/s/user", "每用戶輸出速度（首 chunk 之後）；" + _AA, "GPT-6 Astra (high)", "2026-10",
         "https://artificialanalysis.ai/ko/models/gpt-6-astra-high/providers", 2, "中立", "第三方量測，無賣方利益", "一手（WebFetch 摘要）", _SLO_USE + "｜Astra",
         f"v10.2 E2（{EID}）：Astra 層代表模型 GPT-6 Astra", second="SRC_PERF_071"),
    _rec("SRC_PERF_071", "輸出速度（OpenRouter P50）：GPT-6 Astra", 32, "tok/s/user", "每用戶輸出速度；" + _OR, "GPT-6 Astra", "2026-10",
         "https://openrouter.ai/models/openai/gpt-6-astra", 2, "中立", "第三方量測，實際流量；延遲 4.16 s", "一手（WebFetch 摘要）", _SLO_USE + "｜Astra",
         f"v10.2 E2（{EID}）：與 SRC_PERF_070 取幾何平均", second="SRC_PERF_070"),
    _rec("SRC_PERF_072", "DeepSeek profile decode 每 GPU（H800，EP128，批次 128，4K）", 2324, "tok/s/GPU（decode）", "官方 profile 配置；每 GPU 批次 128；提示長度 4K；兩個 micro-batch 重疊；TPOT 約 55 ms",
         "DeepSeek-V3/R1 on H800（EP128）", "2025-02", "https://github.com/deepseek-ai/profile-data；數值轉引 Step-3 論文表 8（arXiv 2507.19427）", 1, "利害關係方", "DeepSeek 自揭（宣傳成本效率）；Step-3 論文為轉引，非獨立量測",
         "一手（官方配置）＋二手（吞吐轉引）", "Calib J 節 C 欄（Hopper 校準複本列）", f"v10.2 E1（{EID}）：Hopper 校準目標；與 SRC_PERF_073 同一家公司，相關性高，兩者不獨立"),
    _rec("SRC_PERF_073", "DeepSeek 線上服務 decode 每 GPU（H800，24 小時平均）", 1850, "tok/s/GPU（decode）", "24 小時平均（2025-02-27 至 02-28）；平均每用戶輸出 20–22 tok/s；每輸出 token 平均 KV 長度 4,989；decode 單元 18 節點（EP144）",
         "DeepSeek-V3/R1 on H800（線上服務）", "2025-03", "https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md", 1, "利害關係方",
         "DeepSeek 自營服務自揭（並宣稱理論利潤率 545%）；Step-3 論文表 8 轉引 1,850", "一手（官方文件）", "Calib J 節 E 欄；Checks V15（驗證，不用於校準）",
         f"v10.2 E3（{EID}）：Hopper 條件對齊後驗證點；與校準點 SRC_PERF_072（2,324）同一家公司，相關性高"),
    _rec("SRC_PERF_074", "vLLM WideEP on GB200：decode 每 GPU（DeepSeek-R1 類，2K／2K，專家 FP4）", 10100, "tok/s/GPU（decode）", "decode 1 個 8 GPU 實例；批次填滿 HBM；無 ITL／SLO；是否只算輸出未寫",
         "GB200 NVL72（vLLM wide-EP）", "2026-02", "https://vllm.ai/blog/dsr1-gb200-part1", 1, "利害關係方", "vLLM 專案（開源；宣傳）；與 LMSYS 13,386（NVFP4）互相佐證但非同一數字", "一手（WebFetch 摘要）",
         "Calib J 節 D 欄（GB200 校準複本列）", f"v10.2 E1（{EID}）：GB200 大批次、無 SLO 的校準目標（候選）；MLPerf v6.0 server 4,668 才是有 SLO 的對照"),
    _rec("SRC_PERF_075", "MLPerf v6.0 DeepSeek-R1 server：NVIDIA GB200 NVL72（72 GPU）每 GPU", 4668.1, "tok/s/GPU（輸出 token）", "server；Closed；available；TPOT p99 80 ms；336,106 ÷ 72；MLCommons summary_results.json",
         "GB200 NVL72（NVIDIA 提交 6.0-0075）", "2026-04", "https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json", 1, "利害關係方",
         "MLCommons 稽核為中立；提交者 NVIDIA 為賣方；其他提交者 Google 2,178、CoreWeave 4,868（依軟體調校差很多）", "一手（原始 JSON 已讀）",
         "Calib H 節 H 欄；Checks V2（MLPerf 上限）", f"v10.2 E3（{EID}）：V2 新上限（取代 v5.1 的 SRC_PERF_061，2,327）；第二來源 SRC_PERF_077", second="SRC_PERF_077"),
    _rec("SRC_PERF_076", "MLPerf v6.0 DeepSeek-R1 server：NVIDIA GB300 NVL72（72 GPU）每 GPU", 5561.6, "tok/s/GPU（輸出 token）", "server；Closed；available；400,437 ÷ 72；MLCommons summary_results.json",
         "GB300 NVL72（NVIDIA 提交 6.0-0078）", "2026-04", "https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json", 1, "利害關係方",
         "MLCommons 稽核為中立；提交者 NVIDIA 為賣方；同輪 Nebius 72 GPU 為 7,994，Nebius 8 GPU 單機 8,064（即舊 V3 對照）", "一手（原始 JSON 已讀）",
         "Calib H 節 F 欄；Checks V3（MLPerf 上限）", f"v10.2 E3（{EID}）：V3 對照改為同輪 72 GPU 機櫃；範圍 5,562–7,994；第二來源 SRC_PERF_078", second="SRC_PERF_078"),
    _rec("SRC_PERF_077", "MLPerf v6.0 DeepSeek-R1 server：CoreWeave GB200 NVL72（64 GPU）每 GPU", 4867.7, "tok/s/GPU（輸出 token）", "server；Closed；available；311,531 ÷ 64",
         "GB200 NVL72（CoreWeave 提交 6.0-0015）", "2026-04", "https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json", 1, "利害關係方",
         "CoreWeave 為雲端出租方；MLCommons 稽核為中立", "一手（原始 JSON 已讀）", "Checks V2 說明欄（第二來源）", f"v10.2 E3（{EID}）：V2 第二來源（不同提交者、64 GPU）", second="SRC_PERF_075"),
    _rec("SRC_PERF_078", "MLPerf v6.0 DeepSeek-R1 server：Nebius GB300 NVL72（72 GPU）每 GPU", 7994.2, "tok/s/GPU（輸出 token）", "server；Closed；available；575,580 ÷ 72",
         "GB300 NVL72（Nebius 提交 6.0-0081）", "2026-04", "https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json", 1, "利害關係方",
         "Nebius 為雲端出租方；MLCommons 稽核為中立", "一手（原始 JSON 已讀）", "Checks V3 說明欄（第二來源，範圍上端）", f"v10.2 E3（{EID}）：V3 第二來源（同輪 72 GPU，不同提交者）", second="SRC_PERF_076"),
]


def src_new_records():
    return SRC_NEW


_IDS = "；".join(x["id"] for x in SRC_NEW)
EVIDENCE_V1020 = [[
    EID, DATE,
    "服務條件查證（A 段）：Q1 OpenAI 標準端點每用戶輸出速度（AA 與 OpenRouter 各層級）；Q3 大批次 decode 獨立點（DeepSeek profile 2,324、線上服務 1,850、vLLM GB200 10.1K）；Q4 MLPerf v6.0 server GB200／GB300 72 GPU（4,668／5,562）與第二來源",
    f"{REPORT} 第 1、3、4 節；{EVTAB}（證據表、MLPerf_v6.0 原始資料頁）", "Verified（AA、OpenRouter）；Interested-party（DeepSeek、vLLM、MLPerf 提交者）",
    "Serving 第 21 列；Calib J 節；Calib H 節 F、H 欄；Checks V2、V3、V7、V8、V15", "SLO 120／65／55（GPT-5.6 時代）；V2 對照 v5.1 的 2,327；V3 對照 Nebius 8 GPU 單機 8,064；V7／V8 以 Sol 服務條件比 LMSYS",
    "SLO 取兩家中位數的幾何平均（Luna 84.3、Sol 43.3、Astra 40.8）；V2 4,668；V3 5,562；V7／V8／V15 條件對齊後比較",
    "採納（E1–E4）；Hopper 與 GB200 的 η_d 倍數未寫入（停損規則，見 Decisions ETA-E1H／ETA-E1G）", V,
    f"讀取者：chat 端（A 段查證）；CC 轉入｜{DEC_BY}｜OpenAI／Azure 的每 GPU 批次已搜尋未找到；ChatGPT 網頁版獨立量測已搜尋未找到；兩家量測商系統性相差 1.5–2 倍",
    "已處理", _IDS, DASH, "IF_TokGW_* 全部及其下游（Alloc、L1_MFleet、L1_ScaleServe、成本與營收名稱）；Checks V 節（CHK_Verify*）", "1–2", "混合（見各 SRC 紀錄）"]]


def evidence_rows():
    return EVIDENCE_V1020


# ================================================================== Decisions (10 columns)
_D = [
    ("E1H", "E1 Hopper 世代換算（Calib C67）：求解無解，不寫入",
     "校準目標 DeepSeek profile 2,324 tok/s/GPU（H800，EP128，批次 128，4K）。Calib J 節 C 欄複本列（比照 H 節公式）在 C67＝1.2 時模型 ÷ 目標＝0.34。每序列時間被 EP 通訊項（0.2975 ms，IB 0.05 TB/s × η_link 0.7、"
     "3 B／元素）卡住：C67 加大到約 4.5（η_d 16%）後產出飽和在 2,187 tok/s/GPU（目標的 0.94），再加大也不增加，所以沒有 C67 值使模型 ÷ 目標＝1（±2%）。C67＝4.5 時 Hopper η_d 為 16%，"
     "高於 GB300 擬合值 3.6%。依工作單停損規則（解超出物理合理範圍即停、不寫入），C67 維持 1.2、C68 維持 1.5（J4）。若改用 C68 吸收：C67＝1.2 時即使每層延遲為 0 也只達目標的 0.37，同樣無解。"
     "待 Project 判斷：EP 通訊與計算的重疊（DeepSeek 兩個 micro-batch 重疊）是否納入模型、或另一種校準方式。",
     "Calib J 節（複本列、所需倍數列）；Calib C67／C68 不變", "未寫入，待 Project 判斷"),
    ("E1G", "E1 GB200 世代換算（Calib D67／CAL_EtaD_GB200）：模型 ÷ 目標 0.37，解會使 V5 失敗，不寫入",
     "校準目標 vLLM GB200 10.1K tok/s/GPU（decode 8 GPU 實例，批次填滿 HBM，無 SLO，2K／2K）。D 欄複本列在 D67＝1 時模型 ÷ 目標＝0.37（不在 0.9–1.1）。達標需 GB200 η_d 倍數約 3.04（η_d 10.9%），"
     "即 GB200 有效算力（η_d × 10 PF）高於 GB300 擬合值（3.6% × 15 PF）約 2 倍，且 V5（MLPerf v6.0 interactive GB200）模型 ÷ MLPerf 由 0.49 升至約 1.3 而失敗。"
     "同一個 η_d 無法同時滿足無 SLO 大批次點與 interactive 小批次點，表示 η_d 隨批次變化的問題仍在。依停損規則不寫入，D67 維持 1，不新增 CAL_EtaD_GB200 具名範圍。",
     "Calib J 節 D 欄；Calib D67 不變", "未寫入，待 Project 判斷"),
    ("E2", "E2 Serving SLO 改為觀測中位數的幾何平均（讀法 R1：基準一併改，舊 SLO 留作情境 slo_v10）",
     "Serving C21:E21＝√(AA 中位 × OpenRouter 中位)：Luna＝GPT-6 Luna（116.5、61）→ 84.3；Sol＝GPT-6.1 Sol（50.7、37）→ 43.3；Astra＝GPT-6 Astra（52.1、32）→ 40.8；區間取兩家之中較低者到較高者。"
     "標記 Derived（第三方量測的幾何平均）。首 token 時間 SLO 不改。兩家量測商系統性相差 1.5–2 倍（AA 探測請求、OpenRouter 實際流量），原因未查明。Sol 層對應 GPT-6.1 Sol（chat 端預設；GPT-6 Sol 為 102.8／63）。"
     "若 Andy 的原意是基準在本段不動，改採 R2：只保留情境、C21:E21 回到 120／65／55。情境 slo_v10＝舊口徑 120／65／55。",
     "Serving C21:E21；SRC_PERF_066–071；Gov_Map GM239–GM241；情境 slo_v10；IF_TokGW_* 及其下游", "v10.2 已建"),
    ("E3", "E3 驗證判準",
     "V2 對照改 MLPerf v6.0 server GB200 NVL72（NVIDIA 72 GPU）4,668（SRC_PERF_075；第二來源 CoreWeave 4,868＝SRC_PERF_077）；V3 對照改同輪 GB300 NVL72 72 GPU 機櫃 NVIDIA 5,562（SRC_PERF_076；範圍 5,562–7,994、Nebius 8 GPU 單機 8,064）；"
     "V7、V8 改為 LMSYS 條件對齊後的模型值（Calib J 節 F、G 欄：DeepSeek-V3 規模、輸入 2,000、輸出 2,000（來源未寫，取 2,000）、ITL 100 ms、無 MTP、批次由速度下限與 HBM 決定），通過帶維持 0.5–2.0；"
     "新增 V15 DeepSeek 線上服務 1,850（Calib J 節 E 欄，帶 0.5–2.0，註明與校準點同一家公司）；V13、V14 加上限 ≤ 3（chat 端預設，可撤回）；B26、B36 改回驗證計數（V16、V17）。",
     "Checks V 節；Calib H 節 F、H 欄；Calib J 節 E–G 欄；SRC_PERF_072–078", "v10.2 已建"),
    ("E4", "E4 Perf_Batch R–S 欄保留（取代 SL41-1a-3 的『刪除』）",
     "Andy 2026-10-16 18:22 決定 (b)：保留 R–S 欄（FP8 rollout 情境），Sens_Train W59:X62 讀取；頁首與 Gov_Map GM558 標明『只供敏感度情境（不進任何 IF_／L1_ 輸出）』。只改標籤，數值不變。取代 17:35 的『刪除』。",
     "Perf_Batch R3:S3、A2；Gov_Map GM558；Decisions SL41-1a-3 狀態", "v10.2 已建"),
]
DECISIONS_V1020 = [[f"ETA-{i}", V, f"η 校準段：{t}", txt, DATE, DEC_BY, st, where, f"{WO} {i}", "否"] for i, t, txt, where, st in _D]


def decisions_update(wb):
    """SL41-1a-3 (4-1: R-S columns not deleted, listed for Project) is closed by the 18:22 decision (b)."""
    ws = wb["Decisions"]; log = []
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "SL41-1a-3" and ws.cell(r, 7).value == "未執行，待 Project 判斷":
            ws.cell(r, 7).value = "已決定（Andy 2026-10-16 18:22：保留，改標註）；v10.2 ETA-E4 執行"; log.append("Decisions SL41-1a-3: status")
    return log


# ================================================================== formula map (builder-owned links): Serving row 21 = geometric mean of the two measurers
FM = {"Serving!C21": "=SQRT(SRC_PERF_066*SRC_PERF_067)", "Serving!D21": "=SQRT(SRC_PERF_068*SRC_PERF_069)", "Serving!E21": "=SQRT(SRC_PERF_070*SRC_PERF_071)", "Calib!F120": "=SRC_PERF_076"}


def formula_map(fm):
    fm = dict(fm); fm.update(FM); return fm


# base blue inputs that become non-input cells: Calib F120 (8064 literal; V3 reads SRC_PERF_076 now)
SNAP_RETIRED = [("Calib", ("MLPerf 實測輸出 tok/s/GPU（總量 ÷ 72）", 0), 6)]

SLO_TXT = ("SLO 為兩個第三方量測商中位數的幾何平均（v10.2 E2）：Luna＝GPT-6 Luna √(116.5×61)＝84.3；Sol＝GPT-6.1 Sol √(50.7×37)＝43.3；Astra＝GPT-6 Astra √(52.1×32)＝40.8 tok/s。"
           "區間取兩家之中較低者到較高者（Luna 61–116.5、Sol 37–50.7、Astra 32–52.1）。Derived（第三方量測 Verified → 幾何平均）。兩家系統性相差 1.5–2 倍（AA 探測請求、OpenRouter 實際流量）。"
           "舊口徑 120／65／55（GPT-5.6 時代，S26）留作情境 slo_v10。首 token 時間 SLO（第 22 列）不改")


# ================================================================== Calib J: calibration copy rows and aligned conditions
CJ_COLS = "CDEFG"
CJ_LABELS = {
    "C": "Hopper 校準點：DeepSeek profile（H800，批次 128，4K，EP128）",
    "D": "GB200 校準點：vLLM WideEP（2K／2K，批次填滿 HBM，無 SLO，8 GPU 實例）",
    "E": "Hopper 驗證點 V15：DeepSeek 線上服務（H800，24 小時平均，KV 4,989，EP144，約 21 tok/s/user）",
    "F": "Hopper 驗證點 V7：LMSYS 條件對齊（DeepSeek-V3 規模，輸入 2,000，ITL 100 ms）",
    "G": "GB200 驗證點 V8：LMSYS 條件對齊（同上，NVFP4 實測）",
}
CJ_NOTE = {
    "g": "世代索引（Spec_Rack 欄）：1 Hopper、2 GB200；黑字常數（測量條件，不是 Excel 擁有的輸入）",
    "isl": "C：profile 的 KV 長度 4K；D：2K／2K；E：每輸出 token 平均 KV 4,989；F、G：LMSYS 輸入 2,000（輸出長度來源未寫，取 2,000，診斷報告第 2.2 節；改為更短 OSL 影響小於 10%）",
    "ep": "0＝依容量規則 MAX(EP 基準, …)（同 H 節）；C：EP128（官方 profile）；D：decode 1 個 8 GPU 實例；E：decode 單元 18 節點（EP144）",
    "spd": "0＝無 SLO（批次只受 HBM 限制）。E：平均每用戶 20–22 tok/s 取 21；F、G：ITL 100 ms＝10 tok/s",
    "bat": "C：官方 profile 每 GPU 批次 128；其餘 0＝由速度下限與 HBM 決定（B*＝MIN(速度下限批次, 容量批次)）",
    "T": "實測 decode tok/s/GPU（decode GPU 口徑，不含 prefill GPU）：SRC_PERF_072／074／073／062／063",
    "R": "模型 ÷ 目標。C、D 為校準點（目標 1，容差 ±2%）；E、F、G 為驗證點（Checks V15、V7、V8，通過帶 0.5–2.0）",
    "mult": "達標所需 η_d 倍數＝（算力項係數 ÷ 達標所需每序列時間）÷ CAL_EtaD；若所需每序列時間 ≤ 非算力項（KV、EP 通訊）下限，則『無解』——此時 C67／D67 再大也達不到目標",
}


def calib_j(wb, CAL, SP):
    ws = wb["Calib"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, "J. η 校準與條件對齊複製列（v10.2 E1／E3）：比照 H 節公式（decode-only），條件改為各點的實際條件；模型 ÷ 目標顯示在每欄下方。校準用 C、D；驗證用 E、F、G（不重用校準點）", 10)
    r = r0 + 1
    R = {}
    put(ws, f"A{r}", "點位", F_BOLD)
    for X in CJ_COLS: put(ws, f"{X}{r}", CJ_LABELS[X], F_BOLD, wrap=True)
    ws.row_dimensions[r].height = 58; R["hdr"] = r; r += 1
    consts = [("jg", "世代索引", "", "0", [1, 2, 1, 1, 2]), ("jisl", "輸入長度（decode 起始上下文）", "tok", "#,##0", [4096, 2000, 4989, 2000, 2000]),
              ("josl", "輸出長度", "tok", "#,##0", [0, 2000, 0, 2000, 2000]), ("jep0", "EP 寬度設定（0＝依容量規則）", "GPU", "0", [128, 8, 144, 0, 0]),
              ("jspd", "每用戶速度下限（0＝無 SLO）", "tok/s", "0.0", [0, 0, 21, 10, 10]), ("jbat", "固定批次（0＝由速度下限與 HBM 決定）", "序列/GPU", "0", [128, 0, 0, 0, 0]),
              ("jmtp", "推測解碼（1＝有）", "", "0", [0, 0, 0, 0, 0])]
    for key, lab, unit, fmt, vals in consts:
        R[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X, v in zip(CJ_COLS, vals): put(ws, f"{X}{r}", v, F_CALC, fmt=fmt)
        r += 1
    put(ws, f"J{R['jg']}", CJ_NOTE["g"], F_NOTE, wrap=True); put(ws, f"J{R['jisl']}", CJ_NOTE["isl"], F_NOTE, wrap=True)
    put(ws, f"J{R['jep0']}", CJ_NOTE["ep"], F_NOTE, wrap=True); put(ws, f"J{R['jspd']}", CJ_NOTE["spd"], F_NOTE, wrap=True); put(ws, f"J{R['jbat']}", CJ_NOTE["bat"], F_NOTE, wrap=True)
    R["jT"] = r; put(ws, f"A{r}", "實測 decode tok/s/GPU（目標）"); put(ws, f"B{r}", "tok/s/GPU")
    for X, s in zip(CJ_COLS, ["SRC_PERF_072", "SRC_PERF_074", "SRC_PERF_073", "SRC_PERF_062", "SRC_PERF_063"]): put(ws, f"{X}{r}", f"={s}", fmt="#,##0", fill=FILL_KEY)
    put(ws, f"J{r}", CJ_NOTE["T"], F_NOTE, wrap=True); r += 1
    gl = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}{{jg}})"
    cl = lambda row: f"=INDEX($C${row}:$G${row},{{X}}{{jg}})"
    rows = [
        ("jgn", "世代", "", None, "=INDEX(Spec_Rack!$C$4:$G$4,{X}{jg})"),
        ("jP", "計算用峰值", "PF", "#,##0.000", gl(SP["pk"])), ("jH", "HBM", "GB", "#,##0", gl(SP["hbm"])), ("jB", "HBM 頻寬", "TB/s", "#,##0.00", gl(SP["bw"])),
        ("jLk", "EP 頻寬", "TB/s", "#,##0.00", gl(SP["link"])), ("jEb", "EP 基準", "", "#,##0", gl(SP["ep"])),
        ("jbe", "專家 B/param", "", "0.0000", gl(SP["be"])), ("jbn", "非專家 B/param", "", "0.00", gl(SP["bn"])),
        ("jU", "可用 HBM", "GB", "#,##0", "={X}{jH}*(1-Serving!$C$9)"),
        ("jTP", "注意力 TP", "", "0", "=MAX(1,CEILING($C${rne}*{X}{jbn}/(Serving!$C$10*{X}{jU}),1))"),
        ("jEP", "EP 寬度", "", "#,##0", "=IF({X}{jep0}>0,{X}{jep0},MAX({X}{jEb},CEILING($C${rex}*{X}{jbe}/(Serving!$C$11*{X}{jU}),1)))"),
        ("jW", "每 GPU 權重", "GB", "#,##0.0", "=$C${rne}*{X}{jbn}/{X}{jTP}+$C${rex}*{X}{jbe}/{X}{jEP}"),
        ("jcd", "decode 平均上下文", "tok", "#,##0", "={X}{jisl}+{X}{josl}/2"),
        ("jFd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*$C${rA}*1E9+$C${rac}*{X}{jcd})/1E9"),
        ("jn", "草稿數", "", "0", "=Serving!$C$6*{X}{jmtp}"), ("ja", "每步接受", "", "0.00", "=IF({X}{jmtp}=1,Serving!$C$8,1)"),
        ("jed", "η_d（該世代；含 C67／D67）", "%", "0.00%", cl(CAL["etad"])), ("jtl", "每層延遲（該世代；含 C68）", "µs", "#,##0", cl(CAL["tl"])),
        ("jtf", "每步固定延遲", "ms", "#,##0.00", "={X}{jW}/{X}{jB}+($C${rL}+{X}{jn})*{X}{jtl}/1000"),
        ("jc1", "每序列時間：算力項", "ms", "0.0000", "=({X}{jn}+1)*{X}{jFd}/({X}{jP}*{X}{jed})/1000"),
        ("jc2", "每序列時間：KV 讀取項", "ms", "0.0000", "=$C${rkv}*{X}{jcd}/({X}{jB}*Serving!$C$13)/1E9"),
        ("jc3", "每序列時間：EP 通訊項", "ms", "0.0000", "=({X}{jn}+1)*$C${rL}*$C${rk}*$C${rd}*Serving!$C$12*({X}{jEP}-1)/{X}{jEP}/({X}{jLk}*Serving!$C$14)/1E9"),
        ("jce", "每序列每步時間（三項取最大）", "ms", "0.0000", "=MAX({X}{jc1},{X}{jc2},{X}{jc3})"),
        ("jcap", "容量批次上限", "序列", "#,##0.0", "=({X}{jU}-{X}{jW})*1E9/($C${rkv}*{X}{jcd})"),
        ("jslo", "速度下限批次上限", "序列", "#,##0.0", '=IF({X}{jspd}>0,MAX(0,(1000*{X}{ja}/{X}{jspd}-{X}{jtf})/{X}{jce}),"無 SLO")'),
        ("jBs", "B*（批次）", "序列", "#,##0.0", "=IF({X}{jbat}>0,MIN({X}{jbat},{X}{jcap}),MAX(0,IF(ISNUMBER({X}{jslo}),MIN({X}{jslo},{X}{jcap}),{X}{jcap})))"),
        ("jD", "模型 decode tok/s/GPU", "tok/s", "#,##0", "=IF({X}{jBs}>0,{X}{jBs}*{X}{ja}/(({X}{jtf}+{X}{jBs}*{X}{jce})/1000),0)"),
        ("jR", "模型 ÷ 目標", "x", "0.000", "=IF(ISNUMBER({X}{jT}),IF({X}{jT}>0,{X}{jD}/{X}{jT},\"—\"),\"—\")"),
        ("jEff", "採用 η_d × 計算用峰值（有效 PF/GPU）", "PF", "0.000", "={X}{jed}*{X}{jP}"),
        ("jfl", "非算力項下限（KV、EP 通訊取大）", "ms", "0.0000", "=MAX({X}{jc2},{X}{jc3})"),
        ("jneed", "達標所需每序列每步時間", "ms", "0.0000", '=IF({X}{jBs}>0,(1000*{X}{jBs}*{X}{ja}/{X}{jT}-{X}{jtf})/{X}{jBs},"—")'),
        ("jmax", "η_d 無限大時的產出上限（只剩非算力項）", "tok/s", "#,##0", "=IF({X}{jBs}>0,{X}{jBs}*{X}{ja}/(({X}{jtf}+{X}{jBs}*{X}{jfl})/1000),0)"),
        ("jmaxR", "上限 ÷ 目標", "x", "0.000", "=IF(ISNUMBER({X}{jT}),IF({X}{jT}>0,{X}{jmax}/{X}{jT},\"—\"),\"—\")"),
        ("jmult", "達標所需 η_d 倍數（Calib C67／D67 的解）", "x", "0.00",
         '=IF(ISNUMBER({X}{jneed}),IF({X}{jneed}<={X}{jfl},"無解（非算力項下限）",(({X}{jn}+1)*{X}{jFd}/{X}{jP}/1000/{X}{jneed})/CAL_EtaD),"—")'),
        ("jetan", "達標所需 η_d（絕對值）", "%", "0.0%", '=IF(ISNUMBER({X}{jmult}),{X}{jmult}*CAL_EtaD,"—")'),
    ]
    consts_map = dict(CAL); consts_map.update(R)
    for key, lab, unit, fmt, tpl in rows:
        R[key] = r; consts_map[key] = r
        r += 1
    r = max(R[k] for k, *_ in rows) + 1
    # second pass writes with the full row map (templates refer forward to rows defined later)
    for key, lab, unit, fmt, tpl in rows:
        rr = R[key]; put(ws, f"A{rr}", lab); put(ws, f"B{rr}", unit)
        for X in CJ_COLS:
            m = dict(consts_map); m["X"] = X
            f = tpl.format(**m)
            put(ws, f"{X}{rr}", f, fmt=fmt, fill=FILL_KEY if key in ("jR", "jmult") else None)
    put(ws, f"J{R['jR']}", CJ_NOTE["R"], F_NOTE, wrap=True); put(ws, f"J{R['jmult']}", CJ_NOTE["mult"], F_NOTE, wrap=True)
    put(ws, f"J{R['jEff']}", "對照：GB300 擬合值 η_d × 15 PF＝下一列；Hopper 的有效 PF 本來就低於 GB300（峰值為 FP8 對 NVFP4）", F_NOTE, wrap=True)
    R["jGB300"] = r
    put(ws, f"A{r}", "對照：GB300 擬合 η_d × 計算用峰值（有效 PF/GPU）"); put(ws, f"B{r}", "PF")
    put(ws, f"C{r}", "=CAL_EtaD*INDEX(Spec_Rack!$C$35:$G$35,3)", fmt="0.000"); r += 1
    R["jstate"] = r
    put(ws, f"A{r}", "校準狀態（v10.2；停損規則）", F_BOLD)
    put(ws, f"C{r}", '="Hopper：C67 現值 "&TEXT($C$67,"0.00")&"；模型 ÷ 目標 "&TEXT(C' + str(R["jR"]) + ',"0.00")&"；"&IF(ISNUMBER(C' + str(R["jmult"]) + '),"所需倍數 "&TEXT(C' + str(R["jmult"]) + ',"0.00"),C' + str(R["jmult"]) + ')&"（C67 再大產出上限 "&TEXT(C' + str(R["jmax"]) + ',"#,##0")&"＝目標的 "&TEXT(C' + str(R["jmaxR"]) + ',"0.00")&"）"', F_CALC)
    put(ws, f"D{r}", '="GB200：D67 現值 "&TEXT($D$67,"0.00")&"；模型 ÷ 目標 "&TEXT(D' + str(R["jR"]) + ',"0.00")&"；"&IF(ISNUMBER(D' + str(R["jmult"]) + '),"所需倍數 "&TEXT(D' + str(R["jmult"]) + ',"0.00")&"（η_d "&TEXT(D' + str(R["jetan"]) + ',"0.0%")&"）",D' + str(R["jmult"]) + ')', F_CALC)
    put(ws, f"J{r}", "依工作單停損規則：解超出物理合理範圍即不寫入 C67／D67（Decisions ETA-E1H、ETA-E1G）；Hopper 無解、GB200 的解使有效算力高於 GB300 並使 V5 失敗。待 Project 判斷", F_NOTE, wrap=True)
    r += 1
    return R


# ================================================================== Gov_Map: judgement columns of existing rows (A–P Excel-owned; each field only while it holds its old value)
def _gm_row(ws, sheet, cell):
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 3).value == sheet and ws.cell(r, 4).value == cell: return r
    raise KeyError((sheet, cell))


_E2_ROWS = [  # (cell, GM id, SRC_ID, relation, low, high, range text, lo/hi label)
    ("C21", "GM239", "SRC_PERF_066", "換算（√(SRC_PERF_066 × SRC_PERF_067)＝√(AA 116.5 × OpenRouter 61)＝84.3）", 61, 116.5, "61–116.5（OpenRouter 中位至 AA 中位；Luna）"),
    ("D21", "GM240", "SRC_PERF_068", "換算（√(SRC_PERF_068 × SRC_PERF_069)＝√(AA 50.7 × OpenRouter 37)＝43.3；GPT-6.1 Sol）", 37, 50.7, "37–50.7（OpenRouter 中位至 AA 中位；Sol）"),
    ("E21", "GM241", "SRC_PERF_070", "換算（√(SRC_PERF_070 × SRC_PERF_071)＝√(AA 52.1 × OpenRouter 32)＝40.8；GPT-6 Astra）", 32, 52.1, "32–52.1（OpenRouter 中位至 AA 中位；Astra）"),
]
_E2_REASON = ("v10.2 E2（ETA-E2）：SLO 改為 AA 與 OpenRouter 兩家中位數的幾何平均（Derived）；舊值 120／65／55 為 GPT-5.6 時代的單一來源（S26），留作情境 slo_v10；"
              "兩家系統性相差 1.5–2 倍（AA 探測請求、OpenRouter 實際流量），原因未查明，故區間涵蓋兩者；Sol 對應 GPT-6.1 Sol（chat 端預設，可撤回）")


def gov_update(ws, append_text):
    n = 0

    def rep(sheet, cell, col, old, new):
        nonlocal n
        r = _gm_row(ws, sheet, cell)
        if ws[f"{col}{r}"].value == old:
            ws[f"{col}{r}"].value = new; n += 1
        return r

    for cell, gid, src, rel, lo, hi, rtext in _E2_ROWS:
        r = _gm_row(ws, "Serving", cell); assert ws[f"A{r}"].value == gid, (cell, ws[f"A{r}"].value)
        if ws[f"F{r}"].value in ("原始數據", "Decision"):
            ws[f"F{r}"].value = "Derived（公式）"; ws[f"H{r}"].value = src; ws[f"I{r}"].value = rel; ws[f"J{r}"].value = "ETA-E2"
            ws[f"K{r}"].value = lo; ws[f"L{r}"].value = hi; ws[f"M{r}"].value = rtext; ws[f"N{r}"].value = _E2_REASON
            ws[f"O{r}"].value = "原始數據／Decision → Derived（公式）（v10.2 E2）"; n += 1
    r = _gm_row(ws, "Calib", "F120"); assert ws[f"A{r}"].value == "GM381"
    rep("Calib", "F120", "H", "SRC_PERF_026", "SRC_PERF_076")
    rep("Calib", "F120", "E", "MLPerf 實測輸出 tok/s/GPU（總量 ÷ 72）", "MLPerf v6.0 server GB300 NVL72（NVIDIA 72 GPU）每 GPU（V3 對照）")
    n += append_text(ws[f"N{r}"], " ｜v10.2 E3：V3 對照由 Nebius 8 GPU 單機 8,064（SRC_PERF_026）改為同輪 NVIDIA 72 GPU 機櫃 5,562（SRC_PERF_076）；SRC_PERF_026 保留作單機參考")
    r = _gm_row(ws, "Perf_Batch", "R19:S20"); assert ws[f"A{r}"].value == "GM558"
    n += append_text(ws[f"N{r}"], " ｜v10.2 E4（ETA-E4；Andy 2026-10-16 18:22 決定 (b)）：R–S 欄保留，只供敏感度情境（Sens_Train W59:X62 讀取；不進任何 IF_／L1_ 輸出）；取代 4-1 的『刪除』")
    return n


# ================================================================== end-of-build edits (idempotent)
E4_HDR = "情境：FP8 rollout（只供敏感度情境：Sens_Train W59:X62 讀取；不進任何 IF_／L1_ 輸出）"
E4_A2 = "｜v10.2 E4：R、S 欄保留（Sens_Train W59:X62 讀取），只供敏感度情境，不進任何 IF_／L1_ 輸出（Andy 2026-10-16 18:22 決定 (b)）"


def apply(wb, append_text):
    log = {}
    ws = wb["Perf_Batch"]
    n = 0
    for ref in ("R3", "S3"):
        if ws[ref].value == "情境：FP8 rollout":
            ws[ref].value = E4_HDR; n += 1
    n += append_text(ws["A2"], E4_A2)
    sv = wb["Serving"]
    if sv["F21"].value != SLO_TXT: sv["F21"].value = SLO_TXT; n += 1
    log["perf_batch"] = n
    s = wb["SRC_Perf"]; k = 0
    for rr in range(5, s.max_row + 1):
        if s.cell(rr, 1).value in ("SRC_PERF_018", "SRC_PERF_019", "SRC_PERF_020"):
            k += append_text(s.cell(rr, 23), " ｜v10.2 E2：Serving 第 21 列已改讀 SRC_PERF_066–071 的幾何平均；本紀錄保留作前一代（GPT-5.6）對照與情境 slo_v10 的來源")
    log["src_notes"] = k
    sec = {x["id"]: x["second"] for x in SRC_NEW if x.get("second")}
    k2 = 0
    for rr in range(5, s.max_row + 1):
        i = s.cell(rr, 1).value
        if i in sec and s.cell(rr, 18).value in (None, DASH, ""):
            s.cell(rr, 18).value = sec[i]; k2 += 1       # column R = 第二來源 SRC_ID (Excel-owned; written only while it is still the dash)
    log["second_sources"] = k2
    log["decisions"] = decisions_update(wb)
    return log


# ================================================================== README
README_VERSION = (VERSION + "（次版：η 校準與驗證判準，" + WO + "——E1 Calib J 節複本列（Hopper 校準點 DeepSeek profile、GB200 校準點 vLLM WideEP；停損：C67／D67 不寫入）；E2 Serving SLO 改兩家量測商中位數的幾何平均（84.3／43.3／40.8），舊值留作情境 slo_v10；"
                  "E3 Checks V2／V3 對照更新、V7／V8 條件對齊、V13／V14 上限、新增 V15、B26／B36 改回 V16／V17；E4 Perf_Batch R–S 標註；Decisions ETA-*）。以下為 " + v1010.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1010.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v1010.VERSION.split("_")[-1]):]
README_ROW = ("η 校準與驗證判準（v10.2）",
              "SLO 改兩家量測商的幾何平均；Calib J 節校準複本列（Hopper 無解、GB200 解不物理，C67／D67 未寫入）；驗證 V2／V3／V7／V8／V13／V14 判準更新並新增 V15–V17。細節見 Decisions ETA-*。")

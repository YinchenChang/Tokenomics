# 產生證據表.xlsx（只含查證所得；不讀不寫 model/）
# 用法：python3 docs/evidence/20261015_稽核修正3A/00_build_evidence.py
import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

H = ["題號", "數值", "單位與口徑", "日期", "來源（URL）", "標記", "利害關係方與動機", "是否為獨立的第二來源", "備註"]
V = "Verified"
I = "Interested-party"
A = "Analogy"
D = "Derived"
N = "未找到"
R = []


def add(*a):
    assert len(a) == 9, a
    R.append(a)


# ---- Q1
add("Q1", "1.9（2023 為 0.2、2024 為 0.6）", "GW，OpenAI 自述 compute capacity，未明 IT 或設施電力；2025 年底", "2026-01", "https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/", I, "OpenAI（CFO 文章）；動機：說明算力與營收同步成長，利於募資與談判", "基準", "Epoch 的 H100e 估計以此為輸入，不算獨立")
add("Q1", "1.743M（90% 區間 1.251M–2.185M）", "H100 等效（依峰值 FLOP 換算），2025 年底，研發加推論的用量", "2026-01", "https://epoch.ai/latest/introducing-the-ai-chip-users-explorer", D, "Epoch AI（非營利研究；無銷售動機）", "否（由 OpenAI 1.9 GW 推得）", "文字未給世代占比；圖說稱 2025 年 Blackwell 占多數")
add("Q1", "Blackwell 占多數（圖說，無數值）", "2025 年底 OpenAI 算力按晶片世代", "2026-01", "https://epoch.ai/gradient-updates/frontier-labs-dont-use-most-ai-compute", D, "Epoch AI", "否", "只取到圖的替代文字，未取到圖上數值；Epoch 資料 zip 無法下載（對外連線被擋）")
add("Q1", "4,600 座以上 GB300 NVL72（換算 331,200 顆 GPU，以每座 72 顆計）", "機架數；Microsoft 稱 first at-scale production cluster for OpenAI workloads", "2025-10-09", "https://azure.microsoft.com/en-us/blog/microsoft-azure-delivers-the-first-large-scale-cluster-with-nvidia-gb300-nvl72-for-openai-workloads/", I, "Microsoft／NVIDIA 行銷；動機：展示對 OpenAI 的交付", "基準", "GPU 顆數為本表換算，文章未寫；是否全部專供 OpenAI 與何時全數上線，文章未寫。以模型 GB300 機架 136 kW 換算約 0.63 GW IT。第二來源：已搜尋，未找到（其他報導皆轉述此文）")
add("Q1", "211（Q3 為 105）", "MW IT，Epoch 估計，Abilene，GB200", "2025-12-24", "https://epoch.ai/data/ai-data-centers/directory/openai-stargate-abilene", D, "Epoch AI", "是（與 Microsoft、OpenAI 皆無關）", "H100e 255k；2025-09 約 50,000 顆 GB200；OpenAI 稱 2025-06 起 Oracle 開始交付首批 GB200 機架")
add("Q1", "約 400,000 顆 GB200；站點設計 1.2 GW；2025 年約 200 MW 可用", "晶片數與設計電力", "2025-05-27", "https://www.theregister.com/2025/05/27/oracle_openai_40b/", I, "轉述 Financial Times 報導（Oracle 採購）；Oracle 有融資與業績動機", "是", "每個 NVL72 機架峰值 120 kW")
add("Q1", ">50,000 顆 Grace Blackwell 已交付（客戶未點名）", "顆數，累計至 2025 年底", "2026-02-26", "https://finance.yahoo.com/news/coreweave-q4-earnings-call-highlights-030733529.html", I, "CoreWeave 財報電話會；動機：展示交付", "是", "未點名 OpenAI；活躍電力 >850 MW（2025-12-31）；未揭露世代占比")
add("Q1", "Microsoft 2024 年購入約 485,000 顆 Hopper；ByteDance 230k、Tencent 230k、Meta 224k、xAI/Tesla 200k、Amazon 196k、Google 169k", "顆數，Omdia 估計，2024 年", "2024-12-18", "https://www.datacenterdynamics.com/en/news/microsoft-bought-twice-as-many-nvidia-hopper-gpus-as-other-big-tech-companies-report", A, "Omdia（市調）；轉述 DCD", "否", "只能說明 Azure 側 Hopper 存量大；無法分出 OpenAI 使用部分")
add("Q1", "premium hardware 用於最吃能力的訓練；高流量工作用較低成本基礎設施（定性）", "定性", "2026-01", "https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/", I, "OpenAI", "基準", "暗示推論機隊的世代組合可能比整體機隊更偏舊世代；無數值")
add("Q1", "Hopper 級約 37%／GB200 約 40%／GB300 約 23%", "2025 年底，MW 占比（Derived）", "—", "本報告 Q1 節推導", D, "本代理推導；假設 Hopper 級存量 0.6–0.8 GW（2024 年底 0.6 GW 加少量新增）、GB300 取 Azure 叢集 25%–100% 計入、分母 1.9 GW", "不適用", "三者在區間端點不加總為 100%")
add("Q1", "Hopper 級約 59%／GB200 約 36%／GB300 約 5%", "2025 年全年平均，MW 加權（Derived）", "—", "本報告 Q1 節推導", D, "本代理推導；假設 Blackwell 自 2025 年 Q2 起線性爬升、GB300 僅 Q4 有量", "不適用", "現值 60／40／0 落在此區間內")
# ---- Q2 / MLPerf
add("Q2", "1,253（offline）／556（server）", "tok/s/GPU，DeepSeek-R1，DGX H200（8 Hopper GPU），MLPerf Inference v5.1，Closed", "2025-09", "https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut", I, "NVIDIA 自行提交；動機：展示 GB300 對 Hopper 的倍數", "否", "NVIDIA 部落格註明 Hopper 結果未經 MLCommons 驗證；Server 條件：TTFT 2 秒、12.5 tok/s/user")
add("Q2", "4,024／2,327", "tok/s/GPU，DeepSeek-R1，GB200 NVL72（72 GPU），v5.1 offline／server", "2025-09", "https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut", I, "NVIDIA", "否", "")
add("Q2", "5,842／2,907", "tok/s/GPU，DeepSeek-R1，GB300 NVL72（72 GPU），v5.1 offline／server，available 類別", "2025-09", "https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut", I, "NVIDIA", "否", "")
add("Q2", "9,821（offline）／8,064（server）", "tok/s/GPU，DeepSeek-R1，GB300 NVL72，MLPerf Inference v6.0，Closed", "2026-04-01", "https://developer.nvidia.com/blog/nvidia-platform-delivers-lowest-token-cost-enabled-by-extreme-co-design", I, "NVIDIA", "否", "來源未寫 available 或 preview")
add("Q2", "8 GPU：server 64,510／offline 76,347（每顆 8,064／9,543，本表相除）；72 GPU：575,580／673,936（每顆 7,994／9,360）", "tok/s 系統總量，DeepSeek-R1，GB300 NVL72，v6.0", "2026-04", "https://nebius.com/blog/posts/mlperf-inference-v6-0-results", I, "Nebius（雲端業者；動機：展示自家 MLPerf 名次）", "是（不同提交者；同一款硬體）", "來源未寫 available 或 preview")
add("Q2", "HGX B200（8）：server 51,693／offline 58,582；HGX B300（8）：60,413／69,319", "tok/s 系統總量，DeepSeek-R1，v6.0", "2026-04", "https://nebius.com/blog/posts/mlperf-inference-v6-0-results", I, "Nebius", "是", "每顆：B200 6,462／7,323；B300 7,552／8,665（本表相除）")
add("Q2", "2,494,310（offline）／1,555,110（server）", "tok/s 系統總量，4 套 GB300 NVL72＝288 GPU，DeepSeek-R1，v6.0", "2026-04", "https://developer.nvidia.com/blog/nvidia-platform-delivers-lowest-token-cost-enabled-by-extreme-co-design", I, "NVIDIA", "否", "每顆 8,661／5,400（本表相除）；Interactive 總量 250,634，GPU 數未寫")
add("Q2", "Llama 3.1 405B：GB300 v5.1 為 224／170／138（offline／server／interactive），v6.0 為 271（offline）／259（server）", "tok/s/GPU", "2025-09、2026-04", "https://developer.nvidia.com/blog/nvidia-platform-delivers-lowest-token-cost-enabled-by-extreme-co-design", I, "NVIDIA", "否", "Hopper 的 Llama 3.1 405B 數值：已搜尋，未取得")
add("Q2", "v6.0 DeepSeek-R1 的 Hopper（H100／H200）提交", N, "2026-04", "已搜尋：Nebius、NVIDIA、nand-research、ai2.work、spheron 的 v6.0 摘要皆未列 Hopper DeepSeek-R1", "—", "—", "—", "已搜尋，未找到；官方結果表（github.com/mlcommons/inference_results_v6.0、mlcommons.org）未能取得（mlcommons.org 回錯誤，shell 對外連線被擋）")
add("Q2", "Llama 2 70B offline：B200 約 17,500、H200 約 7,800、MI355X 約 6,200", "tok/s/GPU，v6.0，轉述文章自行相除", "2026-04", "https://www.spheron.network/blog/mlperf-inference-v6-benchmark-results-2026/", A, "Spheron（GPU 租賃商，二手轉述）", "否", "精度低；只作旁證")
add("Q2", "2,785（decode，22.3k／node÷8）、6,538（prefill，52.3k／node÷8）", "output／input tok/s/GPU，DeepSeek-V3，96×H100（12 節點），PD 分離＋大規模 EP，輸入 2,000 tok；ITL 約 100 ms，TTFT 2–5 秒，無明確 SLO", "2025-05-05", "https://lmsys.org/blog/2025-05-05-large-scale-ep/", A, "LMSYS／SGLang 團隊與 Atlas Cloud（機器提供者，商業動機）", "是（獨立複現；但 DeepSeek 自揭已用於 η_p 校準，故只算同類對照）", "對應 Hopper、Sol 級（671B MoE，激活 37B）。作為獨立驗證點：中等")
add("Q2", "約 2,200（sustained）；舊版約 1,500", "tok/s/GPU，DeepSeek 類稀疏 MoE，H200，CoreWeave，InfiniBand，wide-EP；不分 decode／prefill；未寫長度與 SLO", "2025-12-17", "https://vllm.ai/blog/large-scale-serving", A, "vLLM 專案（貢獻者含 CoreWeave 等；動機：宣傳 vLLM）", "是", "對應 Hopper、Sol 級；口徑不明，只能當量級對照")
add("Q2", "13,386（decode，FP8 注意力＋NVFP4 MoE）／9,087（原精度）；prefill 26,156／18,471", "output／input tok/s/GPU，DeepSeek-V3/R1，GB200 NVL72，輸入 2,000 tok，decode 48 rank，無 TPOT", "2025-09-25", "https://lmsys.org/blog/2025-09-25-gb200-part-2", A, "SGLang 團隊與 NVIDIA 合作；NVIDIA 有硬體銷售動機", "是", "對應 GB200、Sol 級。文中稱對 H100 為 prefill 3.8 倍、decode 4.8 倍")
add("Q2", "約 1,850（decode，14.8k／node÷8）、約 9,210（prefill 含快取命中，73.7k／node÷8）", "tok/s/GPU，H800，生產環境 24 小時平均，快取命中 56.3%", "2025-02-28", "https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md", I, "DeepSeek 自揭；動機：展示成本利潤率（稱理論利潤率 545%）", "—", "背景用，不當獨立驗證點（模型已用於 η_p 校準）")
add("Q2", "總量約 1.1M；換算每顆約 15,300", "tok/s，Llama 2 70B，GB300 NVL72 機架（72 GPU，換算）", "2025-11-04", "https://techcommunity.microsoft.com/blog/azurehighperformancecomputingblog/-/4466080", I, "Microsoft Azure／NVIDIA；動機：行銷 ND GB300 v6", "否", "只取到頁面描述，內文不全；70B 稠密模型與模型層級不對應。Signal65 報告列為第二管道，未讀")
add("Q2", "746–1,065（H200）／4,759–6,057（GB200 NVL72），比值約 5.0–6.4 倍", "tok/s/chip，DeepSeek R1 0528，8K 輸入／1K 輸出，互動度 65–133 tok/s/user（插值）", "2026（無跑測日期）", "https://inferencex.semianalysis.com/compare/deepseek-r1-gb200-vs-h200", A, "SemiAnalysis（研究與顧問公司）", "否（SemiAnalysis 不可單獨使用）", "與 MLPerf 比值同量級，作旁證；精度（FP8 或 FP4）頁面未能確認")
add("Q2", "每 GPU 吞吐（Artificial Analysis）", N, "—", "已搜尋：Artificial Analysis 硬體基準／系統負載頁", "—", "—", "—", "已搜尋，未找到 AA 公開的每 GPU 吞吐（其公開數字為 API 端速度與價格）。管道：WebSearch；未登入其付費報告")
# ---- Q3
add("Q3", "RL 後訓練算力預算超過預訓練成本的 10%", "比值，成本口徑，DeepSeek-V3.2", "2025-12", "https://arxiv.org/html/2512.02556v1", I, "DeepSeek（技術報告；動機：展示 RL 擴充能力）", "是（不同於模型現有的 R1 約 5%）", "為下限式陳述（exceeding）")
add("Q3", "RL 約 0.11（continuation 21 天×224 GPU 約 4,704 GPU 天 ÷ 預訓練約 43,300 GPU 天）；首輪 RL 約 5 天，GPU 數未寫", "GPU 天比值，Olmo 3 32B Think，H100；本表相除", "2025-12", "https://arxiv.org/pdf/2512.13961", V, "AI2（非營利，完全開放）", "是", "全部後訓練約 9 天；只含明列的 RL 階段，不含合成資料與評測 rollout")
add("Q3", "RL 占預訓練 10%–200%（Epoch 的假設區間）；2025 年初約 1%–10%", "比值，FLOP 口徑，GPT-5／前沿模型", "2025-10-13", "https://epochai.substack.com/p/notes-on-gpt-5-training-compute", D, "Epoch AI", "是", "是 Epoch 為估總算力而設的假設，不是量測")
add("Q3", "Grok 4 的 RLVR 與預訓練一樣多（開場投影片的讀法），作者判斷是 GPU 時間口徑，FLOP 可能少約 5 倍", "比值", "2025-07", "https://www.greaterwrong.com/posts/eq2aJt8ZqMaGhBu3r/zach-stein-perlman-s-shortform/comment/8rb4sJPQsqaxjJ2DD", A, "LessWrong 評論；原始為 xAI 直播（Interested-party）", "否", "模型 S42 已用 Grok 4，不重複計為獨立點；此處只取口徑可能是 GPU 時間的說明")
add("Q3", "各實驗室內部 RL rollout 算力占比", N, "—", "已搜尋：OpenAI、Anthropic、Google 無公開值", "—", "—", "—", "已搜尋，未找到；管道：WebSearch、Epoch 文章、各技術報告")
add("Q3", "工具呼叫數：原生 scaffold 比 mini-SWE-agent 多約 1.5–2 倍（Opus 4.6：Claude Code 約 100 對 56；GPT-5.4：Codex 約 82 對 58）", "每次試驗平均工具呼叫數，SWE Atlas（三種工作流混合）", "2026", "https://arxiv.org/pdf/2605.08366", V, "論文作者（評測基準）；未見廠商利益", "是（不同於模型現有的 ARC 0.51）", "方向與模型的 0.7（供應商原生增強使輪數減少）相反；工具呼叫數不等於輪數；數值讀自圖上標籤")
add("Q3", "中位輪數：SWE-Bench 33–74、Terminal-Bench 30–47（規劃開）；關規劃時 SWE-Bench 30B 由 40 降到 5；僅 bash 少 24%–32% 呼叫", "輪數，Nemotron-3、Mistral-Medium-3.5，T4／128k 上下文", "2026", "https://arxiv.org/pdf/2609.20804", V, "論文作者", "是", "顯示輪數對 harness 設定非常敏感（變動可達數倍），不支持單一倍數 0.7")
add("Q3", "單代理工具迴圈的平均輪數（生產環境）", N, "—", "已搜尋：Anthropic、OpenAI 未公布 Claude Code／Codex 生產任務平均輪數", "—", "—", "—", "已搜尋，未找到公開的生產環境值；只有基準測試軌跡")
# ---- Q4
add("Q4", "GB300 對 H200 每顆 decode 比：offline 4.66 倍、server 5.23 倍", "MLPerf v5.1 DeepSeek-R1，5,842÷1,253 與 2,907÷556", "2025-09", "https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut", D, "NVIDIA 提交（Interested-party）", "否", "推出 η_d 倍數 1.63（offline）、1.45（server）；方法見報告 Q4")
add("Q4", "GB300 v6.0 對 H200 v5.1：7.8 倍（offline）、14.5 倍（server）", "軟體世代不同（GB300 為 2026-04 版、Hopper 為 2025-09 版）", "2026-04", "https://developer.nvidia.com/blog/nvidia-platform-delivers-lowest-token-cost-enabled-by-extreme-co-design", D, "NVIDIA", "否", "倍數 0.97（offline）、0.52（server）當下限；Hopper 在 v6.0 無 DeepSeek-R1 提交")
add("Q4", "SGLang：GB200 對 H100 decode 4.8 倍（FP4 對 FP8）", "LMSYS 自述", "2025-09-25", "https://lmsys.org/blog/2025-09-25-gb200-part-2", A, "SGLang 與 NVIDIA", "是", "η_d 倍數約 1.05（對 GB200 峰值）；換成 GB300 基準約 1.1–1.3（乘 MLPerf 的 GB300÷GB200 比 1.25–1.45）")
add("Q4", "GB200 對 H200 約 5.0–6.4 倍", "InferenceX，DeepSeek R1 0528，8K／1K", "2026", "https://inferencex.semianalysis.com/compare/deepseek-r1-gb200-vs-h200", A, "SemiAnalysis", "否（不可單獨使用）", "η_d 倍數約 0.8–1.0")
add("Q4", "η_d 倍數推導區間 0.8–1.6，中心約 1.1–1.3", "x，GB300＝1", "—", "本報告 Q4 節", D, "本代理推導", "不適用", "現值 1.5 位於區間上端")
# ---- Q5
add("Q5", "0.816（226.75÷278 節點）", "時間平均占用節點 ÷ 當日峰值占用節點，H800，DeepSeek V3＋R1，24 小時", "2025-02-28", "https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md", I, "DeepSeek 自揭；動機：展示成本利潤率", "基準", "是節點數口徑，非 token 吞吐；夜間釋出節點供研究使用，故不代表整個機隊")
add("Q5", "0.66–0.80", "每節點平均 decode 14.8k ÷ 容量（SGLang H100 複現 22.3k，或 DeepSeek 自己的 profile 18.6k）", "2025-02／2025-05", "https://lmsys.org/blog/2025-05-05-large-scale-ep/", D, "本表相除；兩來源皆有利害（DeepSeek、Atlas Cloud）", "部分", "兩者的輸入長度與 SLO 不完全相同，只能當量級")
add("Q5", "0.54–0.65（上兩項相乘）", "平均 token 吞吐 ÷ 容量的代理值（單一模型、集中式服務）", "—", "本報告 Q5 節", D, "本代理推導", "不適用", "不含多模型、長尾部署的損失")
add("Q5", "17.7% 的 GPU 只服務 1.35% 的請求；GPU 需求 1,192 → 213（減 82%）", "多模型市集的專屬部署；H20", "2025-10", "https://www.datacenterdynamics.com/en/news/alibaba-cloud-claims-it-can-reduce-gpu-use-by-82-with-pooling-system/", I, "Alibaba Cloud（SOSP 論文；動機：展示系統）", "是", "長尾極端案例，不能外推到前沿單一模型；1.35% 的分母論文未清楚定義")
add("Q5", "最多省 25% GPU 小時；浪費減 80%", "相對現行自動擴縮基準，Microsoft O365 超過 1,000 萬請求／日", "2025", "https://arxiv.org/html/2502.14617v3", V, "Microsoft Research 論文", "是", "指自動擴縮的浪費，不是 token 吞吐 ÷ 容量；全文未給平均利用率")
add("Q5", "平均 token 吞吐 ÷ 容量（前沿實驗室機隊）", N, "—", "已搜尋：OpenAI、Anthropic、Google、Microsoft、Meta 無公開值；arXiv 2603.16054 只有模擬值", "—", "—", "—", "已搜尋，未找到。管道：WebSearch、arXiv、各雲端業者部落格")
# ---- Q6
add("Q6a", "1.10（2023）／1.09（2024）", "fleet 平均 PUE，Google，Q4 滾動十二個月", "2024-12", "https://datacenters.google/efficiency/", I, "Google 自揭", "基準", "全機隊，不分氣冷或液冷、不分 Hopper")
add("Q6a", "1.15", "全球平均 PUE，AWS，2023；最佳站點 1.04", "2024", "https://www.datacenterdynamics.com/en/news/aws-global-data-centers-achieved-pue-of-115-in-2023", I, "AWS 自揭，DCD 轉述", "是", "")
add("Q6a", "1.16（FY24）／1.17（FY25）", "全球 PUE，Microsoft，自有且營運滿 12 個月的資料中心；亞太 1.25–1.28", "2025", "https://datacenters.microsoft.com/sustainability/efficiency/", I, "Microsoft 自揭", "是", "Azure 是 OpenAI 最大雲端供應者")
add("Q6a", "1.58（2023，單站平均）／1.47（容量加權）；1.56（2024）", "產業平均 PUE，Uptime Institute 全球調查", "2024-2025", "https://journal.uptimeinstitute.com/large-data-centers-are-mostly-more-efficient-analysis-confirms/", V, "Uptime Institute（認證與顧問業務）", "是", "2024 值取自 https://www.upsite.com/blog/data-center-trends-rack-density-rises-while-pue-and-outage-frequency-remain-flat/ 的轉述；超大型 colo 設計值 ≤1.4")
add("Q6a", "1.1（超大規模業者）／1.25（其他）", "Epoch 估算訓練成本所用 PUE 假設", "2024", "https://arxiv.org/html/2405.21015v2", D, "Epoch AI", "是", "假設而非量測")
add("Q6a", "Hopper 氣冷機房專屬 PUE", N, "—", "已搜尋：Meta、Microsoft、NVIDIA、Uptime 皆未公布 Hopper 專屬或氣冷 GPU 大廳的 PUE", "—", "—", "—", "已搜尋，未找到。管道：WebSearch、Meta 工程部落格（未提 PUE）、Uptime")
add("Q6b", "約 270,000", "美元，DGX H100（8 GPU）市價估計，2023-05-29", "2023-05", "https://gpuperhour.com/blog/nvidia-dgx-explained", A, "轉述 SemiAnalysis（分析公司）", "否（單一來源）", "取自 gpuperhour 的整理表，未讀 SemiAnalysis 原文")
add("Q6b", "每顆 25,000–30,000（零售均價 25,000–40,000）；製造成本約 3,320", "美元／顆 H100，Raymond James 估計", "2023-08-16", "https://the-decoder.com/nvidias-h100-gpu-sells-like-hot-cakes-with-high-profit-margins/", A, "Raymond James（賣方分析師）；轉述", "是", "8 顆僅 GPU 約 200,000–240,000，不含 CPU、NIC、機殼")
add("Q6b", "約 25,000／顆，10 萬顆約 25 億美元；整體建置 30–40 億美元", "美元，xAI Colossus（H100），估計", "2024-09-05", "https://www.hpcwire.com/2024/09/05/xai-colossus-the-elon-project/", A, "HPCwire 估計（非 xAI 揭露）", "是", "整體建置含設施與網路")
add("Q6b", "約 482,000", "美元，DGX H100 發表時零售價（含軟體與支援）", "2022-12", "https://en.wikipedia.org/wiki/DGX-1", A, "Wikipedia 引 YouTube 影片", "是", "DGX 不是 HGX；視為上限")
add("Q6b", "8,665 美元／GPU（製造成本，SuperPOD 推估）", "美元，製造成本不是售價", "2024", "https://arxiv.org/html/2405.21015v2", D, "Epoch AI", "是", "只能當成本下限")
add("Q6b", "306,672", "美元，Supermicro 8×H100 HGX 伺服器 Newegg 標價，2026-09 擷取", "2026-09", "https://gpuperhour.com/blog/nvidia-dgx-explained", A, "零售商標價", "—", "是 2026 價，不是部署當時價；僅供對照")
add("Q6b", "部署當時（2023–2024）超大規模業者實付價", N, "—", "已搜尋：Microsoft、Meta、Oracle、CoreWeave 未揭露每台實付價", "—", "—", "—", "已搜尋，未找到")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "證據表.xlsx")
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "證據表"
ws.append(H)
for r in R:
    ws.append(list(r))
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor="305496")
for i, x in enumerate([7, 38, 38, 12, 48, 14, 34, 22, 44], 1):
    ws.column_dimensions[get_column_letter(i)].width = x
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
ws.freeze_panes = "A2"
ws.auto_filter.ref = ws.dimensions
wb.save(out)
print(len(R), out)

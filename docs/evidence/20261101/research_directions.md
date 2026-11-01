# Andy 調研方向（參考，非結論）｜20261101

- 來源：Gov_Map「CC 敏感度分段＝高」且類別為 Assumed／Analogy 的 56 格，加上本月「已搜尋，未找到」的項目。排序＝對結論的影響 × 公開資料難取得（兩者皆為本月主觀判斷，不是計算值）。
- 只列方向與「什麼證據能定案」，不給推測值；各格現值與區間抄自 Gov_Map（Excel v21.7）。
- 「本月外部 LLM 工作單」欄：Drive `外部搜尋/intake/` 為空，repo 無進行中的外部搜尋工作單（v5.35 工作單記「Gemini 外部搜尋工作單待設定完成」），因此全部為「無」。

| # | GM 編號 | 工作表／列標籤 | 現值（區間） | 敏感度 | 為什麼重要（白話） | 什麼證據能定案（口徑與單位） | 公開搜尋為何不足 | 建議一手管道類型 | 本月外部 LLM 工作單 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | GM236 | Serving!C17 基準利用率（第 0 層，IF_Util） | 0.6（0.4–0.8）Assumed | 高 | 每 GW 實際賣得出去的 token 全部乘這個數；下游每個公司模型都讀 `IF_Util` | 「已上線容量在 SLO 下的平均負載」，單位：年平均 %（GPU-小時口徑），分模型商與 GPU 雲兩類，2025 全年；至少兩家獨立揭露 | 利用率是營運機密；公開只有 Anthropic S-1 的算力費用比（間接）與新雲「簽約率」（不同口徑） | 新雲法說會提問（CoreWeave／Nebius：已交付容量的平均負載）、推論服務商（Together、Fireworks、DeepInfra）訪談、同業研究員交換 | 無 |
| 2 | GM237、GM592 | Serving!C18 實測→生產效率折減；Serving!C28 CTL_ProdDerate | 1.0（0.7–1.0）；0.85（0.7–1.0）Assumed | 高 | 基準測試是固定長度穩態負載，生產環境有長度變異、路由不均、故障；這格決定「理論產能打幾折」 | 同一模型、同一硬體、同一 tok/s/user 下，生產叢集月平均 tok/s/GPU ÷ 基準測試 tok/s/GPU（無單位比值），附 ISL／OSL 分布 | 沒有人公開生產叢集的月平均吞吐；InferenceX 全是基準測試 | vLLM／SGLang／Dynamo 維護者訪談（他們看得到用戶叢集）、推論服務商工程部落格作者、GTC／MLSys 走廊 | 無 |
| 3 | GM586 | Alloc_In!C15 每則提示 token 數 | 4,000（2,000–11,000）Assumed | 高 | 研發算力占比 Q1 最弱的輸入：ChatGPT 每日 25 億則訊息要乘它才變成 token；差 2 倍，Q1 就差一截 | ChatGPT（含消費與企業）每則訊息的平均總 token（輸入＋上下文＋推理＋輸出），單位 token／則，2025 或 2026 年均 | OpenAI 只揭露訊息數與 API tok/min，從未揭露每則 token；OpenRouter 6K 是 API 流量不是 ChatGPT | Microsoft／OpenAI 投資人關係提問（Azure 帳單中的 token 總量）、OpenRouter 團隊（API 側對照）、企業客戶 IT 部門（Copilot 用量報表） | 無 |
| 4 | GM453–456 | Cap_In!C28 對外服務占機隊 B4_Serve；C29 免費占服務 B4_Free | 0.41（0.30–0.60）；0.46（0.35–0.60）Assumed（依 SRC_DEM_004／005，2 級） | 高 | 決定「機隊有多少在賺錢」與回本所需 L、m；現值全靠 The Information 一篇付費牆報導 | OpenAI 2025 全年推論支出與其中免費用戶部分（US$B，Azure 帳單口徑或持有成本口徑要寫明）；或任一前沿實驗室的「對外服務算力 ÷ 全部算力」 | The Information 原文付費牆；Reuters 只轉述「4 倍」；Anthropic S-1 已給一個對照點（服務占比 ≤0.43）但 OpenAI 無 | OpenAI 若送 S-1 即可定案；Microsoft 10-K／法說對 OpenAI 相關營收與成本的揭露；The Information 訂閱原文 | 無 |
| 5 | GM304 | Calib!C5 η_p：prefill 達成峰值比例 | 0.3（0.15–0.45）Analogy（DeepSeek H800 線上約 0.37） | 高 | 長上下文（Astra 32K ISL）成本大半在 prefill；這格決定 prefill 一秒能吃多少 token | GB200／GB300 生產或基準 prefill 的達成 TFLOPS ÷ 峰值 dense TFLOPS（比值），ISL 8K–32K，附批次大小 | 只有 DeepSeek 2025-02 H800 一筆；Blackwell 世代無人公開 prefill 效率 | SGLang／vLLM 維護者、NVIDIA Dynamo 團隊（GTC 技術場次）、InferenceX 原始 run 資料（SemiAnalysis 訂閱） | 無 |
| 6 | GM343–345、GM687 | Calib!E67–G67 η_d 倍數（GB200／VR200／Rubin Ultra 沿用 GB300）；Calib!C156 Hopper 批次口徑倍數 | 1（0.5–1.5）Analogy；1（1–3.74）Assumed | 高 | Block 2 最大的 Analogy：非 GB300 世代的 decode 效率全部「假設跟 GB300 一樣」；Hopper 批次倍數無解 | 同一模型、固定 tok/s/user（例如 50／100）下，各世代實測 decode tok/s/GPU（總 token 口徑），GB200 與 VR200 至少各一筆非 SemiAnalysis 來源 | MLPerf 用延遲情境不是 tok/s/user；InferenceX 單一來源；VR200 只有 preview | MLPerf v6.1 提交者（Nebius、CoreWeave）工程部落格與直接聯絡、NVIDIA 技術部落格作者、LMSYS／SGLang 團隊 | 無 |
| 7 | GM519、GM520、GM526 | Train_In!C6 預訓練 MFU；C7 goodput；C13 研發倍數 | 0.25（0.18–0.35）；0.9（0.8–0.95）；8（4.4–10.4）Analogy | 高 | 訓練側每 token 成本與研發 GW 全部由這三格放大；錨點是 Llama 3（2024）與 Epoch 支出推估 | GB200／GB300 叢集上前沿模型預訓練的 MFU（FP8 分母，%）與有效訓練時間比（%）；研發總 GPU 小時 ÷ 最終訓練 GPU 小時（倍） | 實驗室技術報告只偶爾揭露（DeepSeek V3 有，V4 未見 MFU）；研發倍數只有 Epoch 推估 | 技術報告與 MLSys 論文追蹤（DeepSeek V4、Kimi K3.1 Pro 報告）、Epoch AI 研究員訪談、實驗室基礎設施工程師 | 無 |
| 8 | GM255、GM270、GM275、GM290 | Workload!G5 輪數 T；G8 每輪思考 token h；G9 每輪可見輸出 o；G12 並行子代理數 m（長任務代理） | 30（15–60）；600（300–1,200）；400（200–800）；0（0–1）Assumed | 高 | harness 層（每成功任務成本、L1_HarVsGen）的 token 帳全是假設；一輪差 2 倍，整個任務成本差 2 倍 | 編碼代理（Claude Code、Codex、Cursor）每任務平均輪數、每輪思考與輸出 token、子代理占比，單位 token／任務，附任務類型分布與成功率 | 廠商只給總量（Codex 10 倍成長）不給每任務分解；METR 有時間不公開 token | Anthropic／OpenAI 用量報告（Anthropic Economic Index 方法學團隊）、METR 任務追蹤資料、企業客戶訪談（代理工具的帳單 token ÷ 任務數） | 無 |
| 9 | GM092（E450） | Spec_Rack!E12 GB300 NVL72 機架價格基準 | 4.0 $M/架（MS BOM，2 級）；本月二手稱採購單約 5.0 | 高 | GB300 是 2026 主力世代，機架占總資本支出 65%；差 25% 就是持有成本差 13% | 2026 H2 實際採購單或 ODM 報價（US$M／NVL72 架，寫明含不含 CDU、含不含 NVIDIA 軟體授權） | 只有分析師 BOM 表與媒體估計；採購價不公開 | 供應鏈（Quanta、Wiwynn、Foxconn 法說提問：每架 ASP）、HSBC／Morgan Stanley 硬體分析師、新雲採購主管訪談 | 無 |
| 10 | SRC_DC_002（E455）、Inputs!E13（GM 切片一 Analogy） | Inputs!F13 網路占 AI 支出 15%（高成本情境）；E13 Scale-out 網路 ÷ 機架價格 5–15% | 0.15；0.10（0.05–0.15）Analogy | 中高 | GW 級叢集的網路層數比千卡叢集多，這格決定 IT 設備小計多 5–15%；JPM 15% 的原文本月找不到 | GW 級（≥100K GPU）叢集的 scale-out 網路資本支出 ÷ GPU／機架資本支出（%），實際採購口徑 | hedgehog 只算 1,024 GPU；超大規模業者不拆網路支出 | 網路設備商法說（Arista、NVIDIA Networking 的 AI 後端網路占比說法）、超大規模業者資料中心工程師、JPM AM Cembalest 原文（訂閱／直接索取） | 無 |

## 本月「已搜尋，未找到」中未入表者（低影響或已有處置）

- Kimi K3 官方價格（JS 渲染）：工具問題，下月瀏覽器重試即可。
- Codex 每日 2 兆 token 的「40 兆」原文：對照列不驅動。
- NVIDIA 一手 Rubin GPU TGP、Rubin Ultra NVL576 規格：2027 產品，等正式 datasheet。
- 黃仁勳每 GW 成本的 CNBC 原文：僅 Checks 對照。

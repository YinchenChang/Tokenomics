# A2：2025–2026 真實 LLM 推論流量形狀（ISL / OSL / 快取命中率）

研究日期：2026-10-17｜研究方式：WebSearch + WebFetch，唯讀
標籤：[Verified] 一手來源原文可查｜[Interested-party] 利害關係方自述（註明立場與誘因）｜[Analogy] 類比／替代資料｜[Derived] 本文推算

**通用警語：OpenRouter 是代理指標。** 它是開發者用的 API 路由器，樣本偏向開發者、開源／中國模型、角色扮演與 coding agent。它看不到 ChatGPT／Claude.ai／Gemini App 的消費端流量，也看不到 OpenAI／Anthropic 直連的大客戶。另外 OpenRouter 本身是利害關係方：它的商業模式靠「AI 流量快速成長、agent 化」這個敘事，數字通常會挑對自己有利的面向講。

---

## 1. OpenRouter × a16z《State of AI: An Empirical 100 Trillion Token Study》（2025-12）

來源：https://openrouter.ai/state-of-ai （arXiv 版 2601.10088：https://www.alphaxiv.org/overview/2601.10088 ）
資料窗口：2024-11-03 至 2025-11-30（滾動 13 個月）。類別分析從 2025-05 起算，靠約 0.25% 的 prompt 抽樣。

| 指標 | 數值 | 原文 | 標籤 |
|---|---|---|---|
| 每請求平均 prompt tokens | 約 1.5K → 6K 以上（約 4 倍） | "Average prompt tokens per request have increased roughly fourfold from around 1.5K to over 6K" | [Verified]（OpenRouter 自有資料，[Interested-party]：OpenRouter/a16z，a16z 投資 AI 公司，誘因是放大成長敘事） |
| 每請求平均 completion tokens | 約 150 → 400（約 3 倍） | "completions have nearly tripled from about 150 to 400 tokens" | 同上 |
| 平均序列長度（prompt+completion） | 2023 年底不到 2,000 → 2025 年底超過 5,400 | "from under 2,000 tokens in late 2023 to over 5,400 by late 2025" | 同上 |
| 程式類 prompt 長度 | 常超過 20K input tokens；平均是一般 prompt 的 3–4 倍 | "routinely exceed 20K input tokens"；"average 3–4 times the token length of general-purpose prompts" | 同上 |
| 推理模型流量占比 | 2025 Q1 初幾乎為 0 → 年底超過 50% | "negligible slice of usage in early Q1 now exceeds fifty percent"。注意原文明講這**不是**輸出中 reasoning tokens 的占比 | 同上 |
| 程式類 token 占比 | 2025 年初約 11% → 2025 年底超過 50% | "roughly 11% of total token volume" → "exceeded 50%" | 同上 |
| Anthropic 在程式類支出的份額 | 多數期間超過 60%；2025-11-17 那週首次跌破 60% | — | 同上 |
| Tool call 占比 | 原文沒有給數字，只說「全年持續上升」。5 月的尖峰來自單一大客戶。Input Tool 指標 2025-09 才開始記錄 | — | 查過，報告未提供 |
| 快取命中率 | 原文沒有給數字。只說快取讓實付價低於牌價；混合中位成本是 $0.73/1M tokens | — | 查過，報告未提供 |
| 各廠商總 tokens（兆，2024-11 至 2025-11） | DeepSeek 14.37、Qwen 5.59、Meta 3.96、Mistral 2.92、OpenAI 1.65、MiniMax 1.26、Z-AI 1.18、TNG 1.13、Moonshot 0.92、Google 0.82 | — | [Verified]（偏差極大：OpenAI/Google 的主力流量不走 OpenRouter） |
| 開源占比 | 約 1/3，均衡點約 30%；中國開源週占比最低曾到 1.2% | — | 同上 |

**解讀：** 模型裡「API 類 6,000 in / 400 out」跟這份報告 2025 年底的平均值幾乎一樣。這是 2025 年底 OpenRouter 全體流量的平均，人類、agent、角色扮演都混在裡面。它不代表 2026 年的 agent 流量。completion 的 400 是否含 reasoning tokens，原文沒有分開講。OpenRouter 的 completion 計費通常把 reasoning 算進去，但本文**未驗證**。

## 2. OpenRouter 2026 年的快取與 agent 數據

### 2a. Inferred 電子報 Edition 03《Cache is Crucial》（2026-10-08，作者 Peter Walker）
來源：https://openrouter.ai/data/newsletter/cache-is-crucial
定義：「Cache rate = cached prompt tokens / total prompt tokens」

| 指標 | 數值 | 標籤 |
|---|---|---|
| agent 流量中，快取 prompt tokens 占全部 agent tokens 的比例（2026-09） | "just under 90%"；2026-01 約 60% | [Verified]／[Interested-party: OpenRouter] |
| agent 流量中，output+reasoning 占比 | 約 1% | 同上 |
| 人類流量中，output+reasoning 占比 | 約 12%。新（未快取）prompt 仍是多數，但沒給精確數字 | 同上 |
| agent 對人類 token 倍數（2026-09 最後一週） | 約 7 倍 | 同上 |
| agent 超越人類的日期 | 2026-02-06 | 同上 |
| 依模型梯隊的 agent 快取率 | 2026 Q3 推出的模型 88.2%；2025 Q2 推出的模型 54.8% | 同上 |
| 依供應商的 agent 快取率 | 2026-01：中位數 44%，35 家中只有 2 家超過 90%，Google/Anthropic 在 65–80%。2026-09：中位數 85%，54 家中 11 家超過 90%（含 OpenAI、Together、Z.ai、DeepSeek），DeepSeek 約 96% 最高，幾乎所有供應商都超過 70% | 同上 |
| 範例 | 1M agent tokens，約 87% 快取、12% 新 prompt、1% 輸出：含快取約 $0.51，不含快取約 $2.08 | [Interested-party] 範例 |

注意：這裡的「90%」分母是**全部 agent tokens**，分子是快取 prompt tokens。因為 output 只占約 1%，換算成 prompt 層級的快取率約 87/(87+12) ≈ **88%**。[Derived]

### 2b. 其他 OpenRouter／a16z 數字
- 《DeepSeek V4 Is Earning Agentic Token Share》：https://openrouter.ai/blog/insights/deepseek-v4-adoption/ 。樣本是 2026-01-01 至 06-14，超過 450 兆 tokens。agent 請求的每請求 tokens 是人類的約 **15 倍**（"about 15x more per request"）。分類方式是在 API key 層級用 7 個訊號加權。[Verified]／[Interested-party: OpenRouter]
- a16z（2026-08-21）：「more than 85% of [agentic usage] consists of cached input」。Walker 另說「平均每個 agent 請求的快取比例約 70%」，兩者聚合方式不同（token 加權 vs 請求平均）。轉引自 https://xenospectrum.com/en/openrouter-agent-tokens-cache-economics/ 。[Interested-party: a16z/OpenRouter]，屬二手轉引
- 2026-08 第一週七日均量：agent 約 7.3 兆、人類約 1.4–1.5 兆，約 5 倍。來源：https://magica.com/news/ai-agents-token-use-outpaces-humans （二手）
- 《The Token State of Play》（2026-09-22）：https://openrouter.ai/data/newsletter/the-token-state-of-play 。OpenRouter 週 tokens 從 0.5 兆（2025-01-13 週）增加到 128.4 兆（2026-09-14 週）。開源權重 token 占比上週 72%，中國實驗室 69%。[Verified]／[Interested-party]
- 同一份電子報**沒有**給每請求 ISL/OSL。2026 年每請求長度：查過，OpenRouter 未公開。

## 3. 其他獨立來源

### 3a. DeepSeek 開源週 Day 6（2025-03-01）
原始 GitHub 頁面（https://github.com/deepseek-ai/open-infra-index/blob/main/202502OpenSourceWeek/day_6_one_more_thing_deepseekV3R1_inference_system_overview.md ）**本次被權限擋下，沒有讀到原文**。以下數字轉引自 The Decoder：https://the-decoder.com/deepseeks-language-models-could-deliver-massive-profits-even-priced-far-below-openai/

| 指標 | 數值 |
|---|---|
| 24 小時輸入 tokens | 608B |
| 其中快取命中 | 56.3%（約 342B） |
| 輸出 tokens | 168B |
| 輸出速度 | 20–22 tok/s |
| 節點 | 平均 226.75 個，每個 8×H800 |
| 理論營收（全部以 R1 價計） | $562,027/日 |
| 成本（$2/GPU-hr） | $87,072/日 |
| 理論利潤率 | 545% |

標籤：[Interested-party: DeepSeek]（自家數據，誘因是展示成本效率），二手轉引，數字在多家媒體報導中一致。
[Derived] 輸入:輸出 = 608/168 ≈ **3.6:1**。這是 App（免費消費端）加 API 的混合流量，V3 與 R1 都在內。來源沒有給每請求長度與請求數，所以算不出 ISL/OSL。

**解讀：** 模型參考請求設的快取 0.55，應該就是對齊這個 56.3%。但這是 **2025 年初、消費端占多數、agent 尚未普及**時的值。OpenRouter 顯示 DeepSeek 在 2026-09 的 agent 快取率約 96%，兩者不能混用。

### 3b. Google
- 2026-07-22 Q2 2026 財報：「Our model APIs are now processing approximately 22 billion tokens per minute」，上一季是 16B/分鐘；Gemini App 950M MAU。來源：https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2026/ 。[Verified]／[Interested-party: Alphabet]
- [Derived] 22B/分鐘 ≈ 31.7 兆/日 ≈ 每月約 950 兆（只算 API）
- 另有報導稱全公司每月超過 3.2 千兆 tokens（https://www.shacknews.com/article/149205/google-3-2-quadrillion-monthly-ai-tokens ），本次沒有讀原文。Google **沒有**公開 ISL/OSL 或快取率。查過，未找到。

### 3c. Anthropic／Claude Code
- Thariq Shihipar（Claude Code 工程師，2026-02-20）："we build our entire harness around prompt caching"；"we run alerts on our prompt cache hit rate and declare SEVs if they're too low"。來源：https://simonwillison.net/2026/Feb/20/thariq-shihipar 。**沒有給具體命中率數字**。[Interested-party: Anthropic]
- 官方部落格 https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything （2026-04-30）："A few percentage points of cache miss rate can dramatically affect cost and latency"，沒有數字。
- Claude Code 文件 https://code.claude.com/docs/en/prompt-caching ：每回合重送全部歷史、前綴比對、預設 150K 觸發 compaction（轉引自 implicator.ai）。沒有平均命中率。
- **結論：** Anthropic 對 Claude Code 的整體命中率：查過，未公開。數值只能用 OpenRouter 的 Anthropic agent 快取率（2026-01 在 65–80%）當代理。

### 3d. OpenAI／Codex
- 《Better prompt caching for GPT-6》（2026-09-22）：https://openai.com/index/better-prompt-caching-for-gpt-6/ 。客戶自述：Manus 命中率從約 85% 升到持續超過 90%；某 agent 公司評測從 83% 升到 91%；GitHub Copilot 需要重新處理的 prompt token 比例下降超過 50%。快取折扣「up to 90%」。[Interested-party: OpenAI 與客戶]
- Codex 的整體命中率、API 全體命中率、平均 context 長度：**查過，OpenAI 未公開**。

### 3e. Manus（agent 類型，2025-07-18）
https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- "the average input-to-output token ratio is around 100:1"
- "A typical task in Manus requires around 50 tool calls on average"
- "the KV-cache hit rate is the single most important metric for a production-stage AI agent"
- 標籤：[Interested-party: Manus，現屬 Meta]。跟 OpenRouter「agent output 約 1%」的數字吻合。

### 3f. Serverless 供應商（Together／Fireworks／Baseten／DeepInfra）
這幾家的 input:output 比例統計：**查過，沒找到公開數字**。只有行銷頁與價格比較頁。OpenRouter 的供應商快取率（Together 在 2026-09 超過 90%）是目前唯一可用的間接數據。

### 3g. Requesty 閘道的 reasoning token 占比（2026-04）
https://requesty.ai/data/reasoning-token-share-by-provider-april-2026 。定義是 reasoning_tokens / output_tokens。OpenAI 35.9%、OpenAI Responses 32.5%、Vertex (Gemini) 39.9%、xAI 59.7%、z.ai 51.3%、DeepSeek 2.7%。Anthropic 顯示 0%，但那是因為「Anthropic 不另外回報 reasoning tokens」，屬量測限制。[Interested-party: Requesty]，閘道樣本偏開發者，樣本數未公開。

### 3h. Epoch AI 輸出長度趨勢（2025-04-17，資料更新至 2025-11-20）
https://epoch.ai/data-insights/output-length 。基準測試題的輸出長度：推理模型每年約 5 倍，非推理模型每年約 2.2 倍；推理模型平均是非推理模型的約 8 倍。[Analogy]：這是基準題，不是真實流量。

### 3i. 未能驗證的 trace 資料
Mooncake（Kimi）論文 https://arxiv.org/html/2407.00079 本次被權限擋下，沒有讀到。坊間常引用的值（平均輸入約 7.6K、輸出約 180、前綴重用約 50%）**本文未驗證，不列入表格**。Azure/Splitwise trace 也沒有取得原文。

## 4. ChatGPT 對話統計

### 4a. OpenAI／NBER《How People Use ChatGPT》（2025-09-15，NBER w34255）
https://www.nber.org/papers/w34255 ；https://openai.com/index/how-people-are-using-chatgpt/ ；摘要轉引自 https://c3.unu.edu/blog/what-over-2-5-billion-daily-messages-reveal-about-how-people-use-chatgpt

| 指標 | 數值 | 標籤 |
|---|---|---|
| WAU | 700M（2025-07），約占全球成人 10% | [Interested-party: OpenAI] |
| 每日訊息數 | 超過 2.5B（2025 年中，約 29,000 則/秒） | 同上（UNU 摘要轉引） |
| 非工作用途 | 53% → 超過 70% | [Verified]（NBER 頁面） |
| Asking / Doing / Expressing | 49% / 40% / 11% | 同上 |
| 主題 | 實用建議約 29%、資訊查詢 24%、寫作 24%、程式 4.2% | 同上（轉引） |
| 訊息長度／token 數 | **論文未提供** | 查過，不存在於該論文 |

[Derived] 2.5B 則/日 ÷ 700M WAU ≈ 每位週活躍用戶每天 3.6 則（WAU 不等於 DAU，僅供量級參考）。

### 4b. 公開的 ChatGPT 類對話資料集（[Analogy]，2023–2024 年 GPT-3.5/4 年代）
WildChat 論文 Table 1（https://arxiv.org/html/2405.01470v1 ，Llama-2 tokenizer）：

| 資料集 | 對話數 | 平均回合數 | 用戶 tokens/回合 | 模型 tokens/回合 |
|---|---|---|---|---|
| WildChat | 1,039,785 | 2.54 | 295.6 | 441.3 |
| LMSYS-Chat-1M | 1,000,000 | 2.02 | 69.8 | 215.7 |
| ShareGPT | 94,145 | 3.51 | 94.5 | 348.5 |

### 4c. Epoch AI 估算（2025-02-07）
https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use ："I assume that a typical number of output tokens per query is 500 tokens"。一般手打問題的輸入成本「negligible」；另舉 10K 與 100K 長輸入兩種情境。[Analogy]／估計值。

### 4d. ChatGPT 的 ISL/OSL/快取率
OpenAI **沒有**公開 ChatGPT 每則訊息的 token 數、reasoning token 占比或快取率。查過，未找到；推測不存在公開資料。

[Derived] 用 WildChat 推算每請求 ISL：2.54 回合，第 k 回合的輸入是系統提示加上前 k−1 回合歷史再加上本回合提問。每回合約 296+441 ≈ 737 tokens，平均歷史約 (2.54−1)/2 × 737 ≈ 570 tokens，再加本回合提問 296，約 870 tokens。這還沒加系統提示、記憶、工具定義、檔案或搜尋結果，ChatGPT 實際的系統前綴應該有數千 tokens（未驗證）。所以「3,500 in」是合理量級，前提是系統前綴約 2–3K。「2,000 in（免費）」也在合理區間。OSL：WildChat 平均 441，Epoch 假設 500，免費版的 500 對齊這兩個值。付費版因 Thinking 模型與更長回答設 800 屬合理推定，但**沒有直接證據**。

快取 0.8 對 ChatGPT [Derived]：若系統前綴約 2,000 tokens 可跨用戶共享、命中率約 100%，加上同對話內的歷史重用，3,500 tokens 中可快取的約 2,000 + 570 ≈ 2,570，約 **0.73**。2,000 in 的免費版若前綴約 1,200，則約 (1,200+570)/2,000 ≈ **0.88**。0.8 落在推算區間內，但這完全取決於系統前綴長度的假設，**沒有公開數據**。

## 5. 綜合對照表

| 流量類別 | ISL | OSL（含 reasoning） | 快取命中 | 日期 | 來源 URL | 標籤 |
|---|---|---|---|---|---|---|
| OpenRouter 全體平均（混合） | 約 6,000+ | 約 400 | 未公開 | 2025-11 | https://openrouter.ai/state-of-ai | [Interested-party: OpenRouter/a16z]，偏開發者 |
| OpenRouter 全體平均（起點） | 約 1,500 | 約 150 | — | 約 2024 年初 | 同上 | 同上 |
| 程式類請求 | 常超過 20,000；一般 prompt 的 3–4 倍 | 未公開 | 未公開 | 2025 | 同上 | 同上 |
| Agent（OpenRouter） | 每請求約為人類的 15 倍（絕對值未公開） | output 約占 agent tokens 1%（I:O ≈ 99:1） | prompt 層級約 88%（token 加權）；請求平均約 70%；2026-01 約 60% | 2026-09／2026-06 | https://openrouter.ai/data/newsletter/cache-is-crucial ；https://openrouter.ai/blog/insights/deepseek-v4-adoption/ | [Interested-party: OpenRouter] |
| Agent，Q3 2026 新模型 | — | — | 88.2% | 2026-09 | cache-is-crucial | 同上 |
| Agent，供應商中位數 | — | — | 44%（2026-01）→ 85%（2026-09）；DeepSeek 約 96% | 2026 | 同上 | 同上 |
| Agent（Manus） | I:O 約 100:1；每任務約 50 次 tool call | — | 約 85% → 超過 90%（OpenAI 模型） | 2025-07／2026-09 | manus.im 部落格；openai.com better-prompt-caching | [Interested-party: Manus/OpenAI] |
| 人類流量（OpenRouter） | — | output 約占 12%（I:O ≈ 7.3:1） | 未快取 prompt 仍是多數，即低於約 50%（推斷） | 2026-09 | cache-is-crucial | [Interested-party]；快取欄為 [Derived] |
| DeepSeek App+API 混合 | I:O ≈ 3.6:1（608B:168B） | — | 56.3% | 2025-03-01 | the-decoder（轉引 DeepSeek GitHub） | [Interested-party: DeepSeek] |
| ChatGPT 類消費對話 | 對話內容約 870/請求（不含系統前綴） | 約 440（WildChat）；500（Epoch 假設） | 未公開；推算 0.7–0.9 | 2023–24／2025-02 | arxiv 2405.01470；epoch.ai | [Analogy]／[Derived] |
| ChatGPT 量級 | — | — | — | 2025-07 | nber.org/papers/w34255 | 2.5B 則/日，700M WAU [Interested-party: OpenAI] |
| Serverless 供應商 I:O | 查過，未找到 | — | Together 超過 90%（OpenRouter 上的 agent 流量） | 2026-09 | cache-is-crucial | — |

## 6. 對模型假設的校準建議（[Derived]，判斷題留給 Andy）

1. **API 類 6,000/400、快取 0.55：** ISL/OSL 跟 OpenRouter 2025 年底的全體平均吻合，但快取 0.55 的依據是 DeepSeek 2025-03 的數字，已經過時。若 API 類在 2026 年以 agent 為主，快取應落在 0.70（請求平均）到 0.88（token 加權）之間。若要保留人類 API，建議把 API 拆成「人類 API」與「Agent API」兩類。
2. **參考請求 16,384/2,048/0.55：** ISL 16K 接近程式類請求的量級。但 OSL 2,048 遠高於所有實測：OpenRouter 平均約 400；agent 的 I:O 是 99:1，16K 輸入只對應約 165 輸出；人類 I:O 7.3:1，16K 輸入對應約 2,200 輸出。所以 16K in / 2K out 只符合「人類長輸入加推理模型」的情境，不符合 agent。快取 0.55 對 2026 年的 agent 偏低。
3. **ChatGPT 付費 3,500/800/0.8、免費 2,000/500/0.8：** 沒有反證，但也沒有直接證據。OSL 500 對齊 WildChat 與 Epoch 的值。付費 800 依賴 Thinking 模型的滲透率，Requesty 顯示 OpenAI 的 reasoning 約占 output 的 36%（閘道樣本）。快取 0.8 是推算區間 0.7–0.9 的中間值。
4. **每則 ChatGPT 訊息約 4,000 tokens（in+out）：** 跟付費 3,500+800=4,300 一致，但沒有任何一手來源。查過，OpenAI 未公開。

## 7. 本次無法取得（被權限擋下，不等於不存在）
- DeepSeek GitHub Day 6 原文（數字改用 The Decoder 轉引）
- Mooncake arXiv 2407.00079（相關數字未列入）
- fourweekmba 文章（抓取錯誤）

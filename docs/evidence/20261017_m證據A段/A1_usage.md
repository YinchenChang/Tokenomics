# A1｜OpenAI 2025 頂層（Astra／推理）模型價格：以「用量」取代「上架天數」加權的證據

研究日期：2026-10-17｜研究者：唯讀研究代理（未修改任何 repo 或 Excel）
標籤：[Verified]＝一手來源或可查證的一手引述；[Interested-party]＝利害關係人自述（標明其動機）；[Analogy]＝以他者類比；[Derived]＝本文推算。
「搜尋未找到」與「不存在」分開標示。

---

## 0. 結論先講

1. **沒有任何公開來源提供 OpenAI 2025 年「依模型別」的 API token 或 ChatGPT 訊息占比。** OpenAI 從未公布 o1/o3/o4-mini 與 GPT-4o/4.1/GPT-5 的 token 占比，也沒有公布推理 token 占輸出 token 的比例。這是「搜尋未找到」，不代表 OpenAI 內部沒有這些數字。
2. 可用的時間剖面證據有三類，方向一致，都顯示**2025 下半年的量遠大於上半年**。
   - (a) OpenAI 在 Azure 的推論支出逐季成長：Q1 2.075、Q2 2.947、Q3 3.648（$B）。
   - (b) API 吞吐量：2025-10 達每分鐘 60 億 token，兩年成長 20 倍。
   - (c) 推理模型的滲透率在 2025 年由「可忽略」升到「過半」：OpenRouter 的推理模型 token 占比由 Q1 初期可忽略升至 >50%；ChatGPT 每日使用推理模型的用戶比例，免費版由 <1% 升到 7%，Plus 由 7% 升到 24%。
3. **[Derived] 改用用量加權後，2025 頂層混合價約為天數加權的 0.45–0.80 倍。** 以 7.17 $/M 為基準，相當於約 **3.3–5.7 $/M**。
   - 只用總量指數加權（推理占比固定）：約 0.70–0.80 倍，即 5.0–5.7 $/M。
   - 再疊加推理占比逐步上升：約 0.45–0.53 倍，即 3.3–3.8 $/M。
   - 這個倍數對 input／cached／output 混合比例不敏感（見 §6）。

---

## 1. Altman 2025-08 推理模型日用比例，以及之後的相關數據

| 項目 | 內容 | 日期 | 來源 | 標籤 |
|---|---|---|---|---|
| 原始 X 貼文 | "the percentage of users using reasoning models each day is significantly increasing"。免費用戶 <1% → 7%，Plus 用戶 7% → 24% | 2025-08-10 | https://x.com/sama/status/1954603417252532479 （Simon Willison 轉錄：https://simonwillison.net/2025/Aug/10/sam-altman ） | [Interested-party] Altman／OpenAI；GPT-5 上線遭批評後的辯護，有動機強調推理模型受歡迎 |
| 同期媒體轉述 | "I expect use of reasoning to increase over time greatly, so rate limit increases are important"；"All model-class limits will shortly be higher than they were before GPT-5." | 2025-08-11 | https://www.digit.in/news/general/openai-boosts-reasoning-model-limits-for-all-users-amid-gpt-5-backlash.html | [Interested-party] |
| Plus 的 GPT-5 Thinking 上限 | 每週 3,000 則，超過後改用 Thinking mini；GPT-5 Thinking 的 context 為 196k | 2025-08-13 | https://threadreaderapp.com/thread/1955438916645130740.html | [Verified]（官方 rate limit 宣告；只是上限，不是實際用量） |
| GPT-5 上線初期上限 | Plus 每週 200 則 Thinking（上線當下） | 2025-08-08 | https://the-decoder.com/openai-ceo-sam-altman-responds-to-gpt-5-backlash-outlines-next-steps/ | [Verified] |
| API 流量 | GPT-5 上線後 24 小時內 API 流量約翻倍；現有容量只能再承受約 30% 的新 API 成長 | 2025-08-08 至 08-12 | https://www.thestack.technology/chatgpt-capacity-tradeoffs-gpt5-bumpy-rollout/ | [Interested-party] Altman |
| 免費／Go 用戶撤除 router | 2025-12-11 免費與 Go 用戶改為預設 GPT-5.2 Instant，不再自動路由到 Thinking；Plus 與 Pro 保留 router。WIRED 引知情人士說法，指 router 傷害了 DAU（推理回覆太慢） | 2025-12-11（報導 12-17） | https://the-decoder.com/openais-gpt-5-router-rollback-shows-why-ai-requires-unlearning-old-habits ；https://letsdatascience.com/news/openai-sets-gpt-52-instant-as-default-cad3071a | [Verified]（release notes）＋[Interested-party]（匿名消息源） |
| 企業端推理採用 | 企業 MAU 中有 14% 從未用過推理功能，DAU 中只有 1% | 2025-11／12（Nov'24–Nov'25 期間） | https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf | [Interested-party] OpenAI 銷售文件，有動機誇大採用率 |

**搜尋未找到：** 2025-08 之後 OpenAI 沒有公布「多少比例的訊息或 token 被路由到 Thinking」。Altman 2025-08-12 的說法只有定性描述（"significantly increasing"）。
**解讀限制：** 7% 和 24% 是「當天至少用過一次推理模型的用戶比例」，不是訊息占比，也不是 token 占比。推理回覆的 token 數遠多於一般回覆，所以推理模型的 token 占比應高於用戶占比，但無法直接換算。

---

## 2. 2025 年依模型別的 token／訊息占比；推理 token 占比；OpenRouter／a16z

### 2.1 OpenAI 自己的數據
- **依模型別的 API token 占比，或 ChatGPT 訊息占比：搜尋未找到。** OpenAI 的 NBER 論文 "How People Use ChatGPT"（2025-09）沒有依模型拆分，只在附錄列出模型上線時間表。
- **推理 token 占輸出 token 的比例：搜尋未找到。**
- **最接近的 OpenAI 一手數據：** "Average reasoning token consumption per organization has increased by approximately 320x in the past 12 months"（約 2024-11 至 2025-11）。同一份報告也說 ChatGPT Enterprise 每週訊息成長約 8 倍；有 9,000 多個組織處理超過 100 億 token，近 200 個組織超過 1 兆 token。[Interested-party] OpenAI 企業報告。
  - 這個 320 倍是「每組織」的推理 token 消耗，且基期（2024-11 只有 o1-preview／o1-mini）極低。它能說明推理 token 在 2025 年從極小的基數暴增，但不能直接當作總量指數。

### 2.2 OpenRouter × a16z "State of AI: An Empirical 100 Trillion Token Study"（2025-12）
來源：https://openrouter.ai/assets/State-of-AI.pdf ；摘要頁 https://www.a16z.com/state-of-ai ；arXiv 2601.10088。
期間：模型與價格分析涵蓋 2024-11-03 至 2025-11-30；分類分析從 2025-05 開始。

| 發現 | 原文 | 標籤 |
|---|---|---|
| 推理模型 token 占比 | "What was effectively a negligible slice of usage in early Q1 now exceeds fifty percent."（§4.1）；Fig.10 註明這是經推理型模型的 token 占比，"not the share of 'reasoning tokens' within model outputs" | [Analogy]（代理指標：OpenRouter 偏重開發者與開源模型） |
| 每次請求長度 | prompt 約 1.5K → >6K（約 4 倍）；completion 約 150 → 400（約 3 倍），"mostly due to reasoning tokens"（Fig.15） | [Analogy] |
| 開源與閉源 | 閉源模型全年平均約 70%；開源模型到 2025 年底約占三分之一 | [Analogy] |
| OpenAI 在 OpenRouter 的份額 | 只有 Programming 類別：「自 7 月起由約 2% 擴大至約 8%」。Table 1「依作者的總 token」中 OpenAI 為 1.65T（DeepSeek 14.37T、Qwen 5.59T）。但表中不見 Anthropic，所以這張表很可能只算開源權重模型（gpt-oss）。論文 caption 沒有明說，標為存疑 | [Analogy]，存疑 |
| 價格彈性 | 「價格下降 10% 只對應用量增加約 0.5–0.7%」，需求相對缺乏彈性 | [Analogy]（跨模型的橫斷面關係，不是同一模型降價前後的對比） |
| o3／o4-mini | 論文完全沒提到 o3 或 o4-mini。o1 被描述為第一個被廣泛採用的推理模型 | 搜尋未找到 |
| a16z 摘要頁 | "OpenAI's entire API averaged about 8.6 trillion tokens per day in October." 這與 60 億 TPM × 1,440 分鐘 = 8.64 兆一致 | [Interested-party] 轉述 OpenAI 數字 |

**使用注意：** OpenRouter 上 OpenAI 份額很小，用戶多是開發者，對開源模型的偏重明顯。它只能當作「推理模型在整個產業 token 中的滲透曲線形狀」的類比。曲線形狀是 Q1 接近 0，年底超過 50%，論文正文沒有提供中間各月數值，Fig.10 的圖值本次無法擷取。

---

## 3. OpenAI 2025 年總量的時間剖面（可建月或季指數）

| 指標 | 數值 | 日期 | 來源 | 標籤 |
|---|---|---|---|---|
| OpenAI 在 Azure 的推論支出（季） | 2024：Q1 0.547／Q2 0.748／Q3 1.005／Q4 1.467（合計 3.767）；2025：**Q1 2.075／Q2 2.947／Q3 3.648**（前三季 8.67） | 2025-11 報導 | https://wheresyoured.at/oai_docs ；FT 與 The Register 轉述 https://www.theregister.com/2025/11/12/openai_spending_report/ | [Interested-party]：洩漏文件，Ed Zitron 是 OpenAI 批評者；Microsoft 回應 "the numbers aren't quite right"。季增 +42%、+24% |
| API 吞吐量 | "we process over 6 billion tokens per minute on the API"；兩年成長 20 倍（隱含 2023-10 約 3 億 TPM，為 [Derived]） | 2025-10-06 DevDay | https://techcrunch.com/2025/10/06/sam-altman-says-chatgpt-has-hit-800m-weekly-active-users/ | [Interested-party] Altman（官方 keynote） |
| API 吞吐量（之後） | 2026-04 約 150 億 TPM（5 個月 2.5 倍） | 2026-04 | https://substack.com/@exponentialview/note/c-239157898 | [Interested-party] 轉述 |
| ChatGPT WAU | 2025-03 底 5 億 → 2025-08 近 7 億 → 2025-10 8 億 | 2025 | TechCrunch 同上；Nick Turley 2025-08-04 | [Interested-party] |
| ChatGPT 每日訊息（全部消費方案，精確量測） | 2024-06：4.51 億則／日 → **2025-06：26.27 億則／日**（5.8 倍）；2025-07 每週 180 億則（約 25.7 億則／日）；2024-07 至 2025-07 訊息量成長超過 5 倍 | NBER w34255（2025-09） | https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf | [Verified]（OpenAI 經濟研究，經 NBER 發表）；作者含 OpenAI 員工 |
| Microsoft Foundry／Azure token | FY25Q3（2025 年 1–3 月）"over 100 trillion tokens this quarter, up 5x"，其中 3 月單月 50 兆；FY25 全年（2024-07 至 2025-06）"over 500 trillion…up over 7x" | 2025-04-30、2025-07-30 | https://www.marketbeat.com/earnings/reports/2025-4-30-microsoft-co-stock ；https://storage.googleapis.com/magi-store/earnings/MSFT/2025-07-30_Q4_FY2025/03_outputs/transcript.html | [Verified]（財報電話會議）；但這是 Microsoft 全平台的 token，**不等於 OpenAI 的 token** |

**結論：** 沒有比 Azure 推論支出更細的 OpenAI 專屬月度 token 指數，這部分「搜尋未找到」。
- Azure 支出是**成本**，而 2025 年單位 token 成本下降，所以 token 量的成長應快於支出成長。用它當量指數會**低估**下半年的權重，屬保守估計。
- API TPM 只有 2023-10 和 2025-10 兩個錨點，可以用指數內插：月增約 13.3%，2025 全年 1 月到 12 月約 4.5 倍。[Derived]

---

## 4. o1／o3 當時的用量與上限

| 項目 | 內容 | 日期 | 來源 | 標籤 |
|---|---|---|---|---|
| o1 Pro 用量超預期 | Altman："we are currently losing money on openai pro subscriptions! people use it much more than we expected" | 2025-01-05 | https://www.theregister.com/2025/01/06/altman_gpt_profits/ | [Interested-party]（有動機暗示需要漲價或擴容） |
| o3／o4-mini 上市後的 Plus 上限 | o3 每週 50 → **100** 則；o4-mini-high 每天 100 則；o4-mini 每天 300 則。Altman："we have doubled rate limits for o3 and o4-mini-high for chatgpt plus subscribers." | 2025-04-23／24 | https://www.gizmodo.jp/2025/04/openai_doubled_o3_usage_limit_for_chatgpt_plus.html ；https://global.techradar.com/fr-fr/computing/artificial-intelligence/openai-booste-chatgpt-plus-avec-des-limites-dusage-bien-plus-genereuses | [Verified] |
| o3 降價 80% | "we dropped the price of o3 by 80%!!" | 2025-06-10 | https://threadreaderapp.com/thread/1932434606558462459.html ；https://simonwillison.net/2025/Jun/10/o3-price-drop/ | [Verified] |
| 降價後 o3 用量是否上升 | **搜尋未找到** OpenAI 或第三方公布的 o3 降價前後用量。坊間流傳「6 月 o3 的 Plus 上限再翻倍到每週 200 則」，本次未能以一手來源確認 | — | — | 未確認 |
| 上限的意義 | Plus 的 o3 上限是每週 100 則（約每天 14 則），GPT-5 Thinking 是每週 3,000 則，上限提高約 30 倍。這說明 ChatGPT 端的推理用量在 2025-08 之後才「解鎖」 | — | — | [Derived] |

---

## 5. 付費 token 的層級組合（低／中／頂層）

- **OpenAI 依 mini／nano、旗艦、推理分層的付費 token 占比：搜尋未找到。** OpenAI、Microsoft 和主要媒體都沒有公布。
- 間接證據：
  - (a) OpenRouter 的價格–用量散布圖顯示，OpenAI 與 Anthropic 的閉源模型位在「高價、高用量」區；GPT-4 與 GPT-5 Pro 位在「高價、低用量」區，屬 premium specialists。[Analogy]
  - (b) 2025 年 API 的 GPT-5 全系列（含 mini／nano）都是推理模型。所以 2025-08 之後，「推理」不再只等於「頂層」，推理 token 的增加有一部分落在 mini 和 nano。[Verified：官方產品結構]
  - (c) 企業端 320 倍推理 token 成長沒有區分層級。[Interested-party]
- **建議：** 層級組合目前只能用假設參數。可以借用 OpenRouter「閉源約 70%」作為上限式的類比，但不要當成 OpenAI 的實際數字。

---

## 6. [Derived] 用量加權試算

**方法：** 對 2025 年每一天 d 給一個權重 w(d) = 總量指數(d) × 推理占比(d)，再依權重把天數加總到五個價格段。各段價格 P_i = a·input + b·cached + c·output。

**天數權重（現行做法）：** o1 0.288｜o3 0.151｜o3 降價 0.159｜GPT-5 0.345｜GPT-5.2 0.058。

**情境：**
- S1：Azure 季支出，第 4 季外推 4.516；推理占比固定。
- S2：API TPM 指數，月增 13.3%；推理占比固定。
- S3：Azure 支出 × 推理占比由 5% 線性升至 55%，形狀參照 OpenRouter 由近 0 升到 >50%。
- S4：Azure 支出 × 階梯占比：4/16 前 10%、8/6 前 20%、GPT-5 上線後 50%。
- S5：TPM 指數 × 線性推理占比。

| 情境 | 段權重（o1／o3／o3 降價／GPT-5／5.2） | 用量加權價 ÷ 天數加權價 |
|---|---|---|
| S1 | 0.192／0.134／0.163／0.432／0.079 | 0.79–0.80 |
| S2 | 0.155／0.112／0.149／0.477／0.106 | 0.70–0.71 |
| S3 | 0.071／0.092／0.150／0.562／0.125 | 0.50–0.54 |
| S4 | 0.057／0.080／0.098／0.647／0.118 | 0.46–0.50 |
| S5 | 0.055／0.072／0.129／0.586／0.158 | 0.45–0.49 |

上表的倍數區間，是用三種 input／cached／output 混合比例分別計算的結果：
- 1%／82%／17%：這是唯一能把天數加權價還原為約 7.15 的組合，只是反推值，請以模型實際混合比例取代；
- 75%／0%／25%；
- 25%／50%／25%。

三種混合比例下倍數差異不大。套用到 7.17 $/M：
- S1 約 5.6–5.7；
- S2 約 5.0；
- S3–S5 約 3.3–3.8 $/M。

**主要不確定性：**
1. Azure 支出是成本，不是 token；如前所述，用它會讓下半年權重偏保守。
2. 推理占比曲線是 OpenRouter 的類比加上 Altman 的用戶占比，沒有 OpenAI 的 token 實數。
3. GPT-5 時期的「頂層」是否也包含非 thinking 的 GPT-5 main：API 定價相同，對價格不影響，但影響量的歸屬。
4. o1 時期的頂層量有一部分來自 ChatGPT Pro 的 o1 pro，是重度用戶。Altman 說「用量遠超預期」，可能讓 Q1 權重比 S3–S5 假設的稍高。

---

## 7. 總表

| 項目 | 數值 | 日期 | 來源 URL | 標籤 | 可用方式 |
|---|---|---|---|---|---|
| ChatGPT 每日使用推理模型的用戶比例（免費版） | <1% → 7% | 2025-08-10 | https://x.com/sama/status/1954603417252532479 | [Interested-party] Altman | 推理占比在 GPT-5 上線時的階躍點（用戶占比，不是 token 占比） |
| 同上（Plus） | 7% → 24% | 2025-08-10 | 同上；https://simonwillison.net/2025/Aug/10/sam-altman | [Interested-party] | 同上；顯示付費端上線前已有 7% 基礎 |
| Plus 的 GPT-5 Thinking 上限 | 每週 3,000 則（初期每週 200 則） | 2025-08-13（08-08） | https://threadreaderapp.com/thread/1955438916645130740.html | [Verified] | 說明 8 月後推理用量上限放寬約 30 倍 |
| Plus 的 o3 上限 | 每週 50 → 100 則；o4-mini-high 每天 100 則；o4-mini 每天 300 則 | 2025-04-23 | https://www.gizmodo.jp/2025/04/openai_doubled_o3_usage_limit_for_chatgpt_plus.html | [Verified] | o3 時期 ChatGPT 端頂層用量的上界 |
| o3 降價後用量 | — | — | — | 搜尋未找到 | 無 |
| GPT-5 上線後 API 流量 | 24 小時內約翻倍；容量只夠再成長約 30% | 2025-08-08 至 08-12 | https://www.thestack.technology/chatgpt-capacity-tradeoffs-gpt5-bumpy-rollout/ | [Interested-party] | 8 月起量階躍的證據 |
| 免費／Go 用戶撤除 router | 預設改為 5.2 Instant | 2025-12-11 | https://the-decoder.com/openais-gpt-5-router-rollback-shows-why-ai-requires-unlearning-old-habits | [Verified]＋匿名消息源 | 12 月免費端推理量回落，5.2 段權重需下修 |
| OpenRouter 推理模型 token 占比 | Q1 初期可忽略 → 年底 >50% | 2025-12 | https://openrouter.ai/assets/State-of-AI.pdf | [Analogy] | 推理占比曲線的形狀（S3–S5） |
| OpenRouter 每次請求長度 | prompt 1.5K → 6K；completion 150 → 400 | 2024-11 至 2025-11 | 同上 | [Analogy] | 每次請求的推理 token 增加 |
| OpenRouter 價格彈性 | 價格降 10%，用量增 0.5–0.7% | 2025-12 | 同上 | [Analogy] | 不支持「降價 80% 帶來量暴增」的假設；量的成長主要來自能力與產品 |
| OpenAI API 吞吐量 | 每分鐘 60 億 token（約每日 8.6 兆），兩年 20 倍 | 2025-10-06 | https://techcrunch.com/2025/10/06/sam-altman-says-chatgpt-has-hit-800m-weekly-active-users/ ；https://www.a16z.com/state-of-ai | [Interested-party] | 總量指數錨點（S2，月增約 13%） |
| OpenAI 的 Azure 推論支出 | 2025 Q1 2.075／Q2 2.947／Q3 3.648（$B）；2024 年 3.767 | 2025-11 | https://wheresyoured.at/oai_docs | [Interested-party] 洩漏文件，Zitron；Microsoft 稱不完全正確 | 季度量指數（成本口徑，偏保守，S1） |
| ChatGPT 每日訊息 | 2024-06 4.51 億 → 2025-06 26.27 億 | 2025-09 | https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf | [Verified] | 消費端量的年增約 5.8 倍 |
| ChatGPT WAU | 5 億（2025-03 底）→ 近 7 億（2025-08）→ 8 億（2025-10） | 2025 | TechCrunch 同上 | [Interested-party] | 月度內插 |
| 企業每組織推理 token | 約 320 倍（12 個月） | 2025-11／12 | https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf | [Interested-party] | 推理 token 自極低基期暴增；不可直接當量指數 |
| Microsoft 全平台 token | 2025 年 1–3 月超過 100 兆（3 月 50 兆），年增 5 倍；FY25 超過 500 兆 | 2025-04-30、2025-07-30 | https://www.marketbeat.com/earnings/reports/2025-4-30-microsoft-co-stock | [Verified]（非 OpenAI 專屬） | 只作類比 |
| 依模型別的 token／訊息占比；推理 token 占輸出比例；層級組合 | — | — | — | 搜尋未找到（非「不存在」） | 只能用假設參數 |
| 用量加權價 ÷ 天數加權價 | 0.70–0.80（只用量）；0.45–0.54（量 × 推理占比） | — | 本文 §6 | [Derived] | 7.17 → 約 5.0–5.7 或 3.3–3.8 $/M |

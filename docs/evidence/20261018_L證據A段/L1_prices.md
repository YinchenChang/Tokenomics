# L1：中階 LLM token 牌價年變動率 g 與低/中階價比 ρ（2023-01 至 2026-10）

擷取日：2026-10-18。研究方式為唯讀，沒有修改任何 repo 或 Excel。

## 0. 方法與標籤

**參考請求混合價（Blended, $/M tokens）**

B = (16384 × (0.45 × fresh_input + 0.55 × cached_input) + 2048 × output) / 18432

- 模型或時點沒有快取價時，cached_input 以 fresh_input 計（即無折扣）。
- Anthropic 的 cache write 溢價（1.25×/2×）與 Google 的快取儲存費（$/M·hr）不計入。
- 長上下文分級一律取短檔：Google ≤200K、OpenAI ≤272K、Haiku 5.5 ≤100K。參考請求 18,432 tokens 都落在短檔內。
- 在這個混合價中，output 占比約 57%（GPT-6.1 Sol／Sonnet 5.5）。2023 年的 GPT-4 只有 20%，因為當時 input 很貴。

**標籤**

- [Verified]：本次從官方頁面擷取（OpenAI developers.openai.com 模型頁／定價頁、platform.claude.com 定價頁、ai.google.dev 定價頁、官方部落格）。注意，這些官方頁面是經 WebFetch 摘要模型讀取的，不是原始 HTML，因為 curl 被 proxy 403 擋下。
- [Verified-歷史]：官方公告或部落格上的歷史價格。
- [Secondary]：新聞或彙整站的報導。這不是 interested party，但也不是官方。
- [Interested-party]：有商業利害的來源，例如賣 router 的 Morph。
- [Memory]：我的既有知識，本次沒有重新擷取到官方原文。可信度高，但未驗證。
- [Derived]：本文計算所得。
- [Analogy]：類比推論。

**未找到 vs 不存在**

- Wayback Machine 被擋（SITE_BLOCKED），所以沒有任何封存頁面作佐證。歷史價格改以官方公告或官方模型頁現價為依據。
- 「Gemini 3.5 Pro」在官方模型清單中不存在：本次查閱的 ai.google.dev/models（更新於 2026-10-13）沒有列出它。Google 2026-05 曾預告 6 月推出，但沒有出現。Pro 線從 3.1 Pro 直接接到 Gemini 4 Argon。

## 1.（a）價格點表

### OpenAI

| vendor | model | tier | date | input | cached | output | blended | 來源／標籤 |
|---|---|---|---|---|---|---|---|---|
| OpenAI | GPT-4 (8K) | 中（當時旗艦） | 2023-03-14 | 30 | — | 60 | 33.33 | developers.openai.com/api/docs/models/gpt-4 [Verified] |
| OpenAI | GPT-4 Turbo | 中 | 2023-11-06 | 10 | — | 30 | 12.22 | openai.com/index/new-models-and-developer-products-announced-at-devday [Verified-歷史] |
| OpenAI | GPT-4o (05-13) | 中 | 2024-05-13 | 5 | — | 15 | 6.11 | openai.com/index/hello-gpt-4o（「GPT-4 Turbo 的一半價」）[Verified-歷史]、[Derived] |
| OpenAI | GPT-4o (08-06) | 中 | 2024-08-06 | 2.5 | — | 10 | 3.33 | openai.com/index/introducing-structured-outputs-in-the-api [Verified-歷史] |
| OpenAI | GPT-4o + prompt caching | 中 | 2024-10-01 | 2.5 | 1.25 | 10 | 2.72 | gpt-4o 模型頁 [Verified]；生效日 [Memory] |
| OpenAI | GPT-4.1 | 中 | 2025-04-14 | 2 | 0.50 | 8 | 1.93 | models/gpt-4.1 [Verified] |
| OpenAI | GPT-5 | 中 | 2025-08-07 | 1.25 | 0.125 | 10 | 1.67 | models/gpt-5 [Verified]（GPT-5.1 於 2025-11 同價 [Memory]） |
| OpenAI | GPT-5.2 | 中 | 2025-12-11 | 1.75 | 0.175 | 14 | 2.34 | models/gpt-5.2 [Verified] |
| OpenAI | GPT-5.4 | 中 | 2026-03-05 | 2.5 | 0.25 | 15 | 2.79 | models/gpt-5.4 [Verified] |
| OpenAI | GPT-5.5 | 中 | 2026-04-23 | 5 | 0.50 | 30 | 5.58 | models/gpt-5.5 [Verified] |
| OpenAI | GPT-5.6 Sol（首發） | 中（官方稱「對應 GPT-5 無後綴層」） | 2026-07-09 | 5 | 0.50 | 30 | 5.58 | eesel.ai [Secondary] |
| OpenAI | GPT-5.6 Sol（促銷降價，至 2026-11-21） | 中 | 2026-08-21 | 4 | 0.40 | 20 | 4.02 | models/gpt-5.6-sol [Verified]；日期見 thestar.com.my（Reuters）[Secondary] |
| OpenAI | GPT-6 Sol | 中（Astra 之下） | 2026-09-22 | 2 | 0.20 | 10 | 2.01 | models/gpt-6-sol [Verified]；日期見 propakistani [Secondary] |
| OpenAI | GPT-6.1 Sol | 中（「Default」） | 約 2026-09-29 | 2 | 0.10 | 10 | 1.96 | developers.openai.com/api/docs/pricing、models/gpt-6.1-sol [Verified] |
| OpenAI | GPT-6 Astra（參考，頂層） | 頂 | 2026-09-03 | 10 | 1.00 | 50 | 10.04 | pricing 頁 [Verified] |
| OpenAI | GPT-3.5 Turbo | 低 | 2023-03-01 | 2 | — | 2 | 2.00 | [Memory] |
| OpenAI | GPT-3.5T-0613 | 低 | 2023-06-13 | 1.5 | — | 2 | 1.56 | [Memory] |
| OpenAI | GPT-3.5T-1106 | 低 | 2023-11-06 | 1 | — | 2 | 1.11 | [Memory] |
| OpenAI | GPT-3.5T-0125 | 低 | 2024-01-25 | 0.5 | — | 1.5 | 0.61 | [Memory] |
| OpenAI | GPT-4o mini | 低 | 2024-07-18 | 0.15 | 0.075（2024-10 起） | 0.6 | 0.20 → 0.163 | models/gpt-4o-mini [Verified] |
| OpenAI | GPT-4.1 mini／nano | 低 | 2025-04-14 | 0.40／0.10 | 0.10／0.025 | 1.60／0.40 | 0.387／0.097 | models 頁 [Verified] |
| OpenAI | GPT-5 mini／nano | 低 | 2025-08-07 | 0.25／0.05 | 0.025／0.005 | 2.00／0.40 | 0.334／0.067 | models 頁 [Verified] |
| OpenAI | GPT-5.4 mini／nano | 低 | 2026-03-17 | 0.75／0.20 | 0.075／0.02 | 4.50／1.25 | 0.837／0.229 | models 頁 [Verified] |
| OpenAI | GPT-5.6 Terra（官方稱「對應 mini 層」）首發 → 降價 | 低 | 2026-07-09 → 07-30 | 2.5 → 2.0 | 0.25 → 0.20 | 15 → 12 | 2.79 → 2.23 | 首發價：eesel.ai [Secondary]、[Derived]；現價：models/gpt-5.6-terra [Verified] |
| OpenAI | GPT-5.6 Luna（「對應 nano 層」）首發 → 降價 | 低 | 2026-07-09 → 07-30 | 1.0 → 0.20 | 0.10 → 0.02 | 6.0 → 1.20 | 1.12 → 0.223 | 首發價：eesel [Secondary]、[Derived]；現價：models/gpt-5.6-luna [Verified] |
| OpenAI | GPT-6 Luna | 低 | 2026-09-22 | 0.10 | 0.01 | 0.50 | 0.100 | pricing 頁 [Verified] |

GPT-6 世代只有 Astra、Sol、Luna 三層，沒有 Terra 這種 mini 對應層。官方定價頁搜尋結果：未見 GPT-6 Terra。

### Anthropic

| vendor | model | tier | date | input | cached | output | blended | 來源／標籤 |
|---|---|---|---|---|---|---|---|---|
| Anthropic | Claude 3 Sonnet | 中 | 2024-03-04 | 3 | — | 15 | 4.33 | anthropic.com/news/claude-3-family [Verified-歷史] |
| Anthropic | Claude 3.5 Sonnet | 中 | 2024-06-20 | 3 | — | 15 | 4.33 | 「同前代價」，見 anthropic.com/news/3-5-models-and-computer-use [Verified-歷史]；日期 [Memory] |
| Anthropic | 3.5 Sonnet + prompt caching | 中 | 2024-08-14 | 3 | 0.30 | 15 | 3.01 | [Memory]（cache hit = 10% 的機制見現行官方頁 [Verified]） |
| Anthropic | 3.7 Sonnet／Sonnet 4／4.5／4.6 | 中 | 2025-02-24／2025-05-22／2025-09-29／2026-02-17 | 3 | 0.30 | 15 | 3.01 | 定價頁 platform.claude.com/docs/en/about-claude/pricing（列有 4／4.5／4.6）[Verified]；日期 [Memory]，4.6 另見 [Secondary] |
| Anthropic | Sonnet 5 | 中 | 2026-06-30 | 2 | 0.20 | 10 | 2.01 | 定價頁 [Verified]。原定為「至 8/31 的首發價，之後 $3/$15」，後來取消漲價、改為常態價，見 constellationr、claudeaihub [Secondary] |
| Anthropic | Sonnet 5.5 | 中 | 2026-09-28 | 2 | 0.20 → 0.10（2026-10-07） | 10 | 2.01 → 1.96 | 定價頁 [Verified]；日期見 anotherwrapper、letsdatascience [Secondary] |
| Anthropic | Opus 5.5／Fable 5.1（參考，頂層） | 頂 | 2026 | 4／10 | 0.20／0.25 | 20／50 | 3.92／9.68 | 定價頁 [Verified] |
| Anthropic | Claude 3 Haiku | 低 | 2024-03-13 | 0.25 | 0.03（2024-08 起） | 1.25 | 0.361 → 0.254 | claude-3-family [Verified-歷史]；快取價 [Memory] |
| Anthropic | Claude 3.5 Haiku | 低 | 2024-11-04 → 2024-12-03 | 1.0 → 0.80 | 0.10 → 0.08 | 5 → 4 | 1.00 → 0.80 | 2024-12-03 更新：「$0.80/$4」[Verified-歷史]；$1/$5 首發價 [Memory] |
| Anthropic | Haiku 4.5 | 低 | 2025-10-15 | 1 | 0.10 | 5 | 1.00 | 定價頁 [Verified]；日期 [Memory] |
| Anthropic | Haiku 5.5（≤100K 檔） | 低 | 2026-10-07 | 0.10 | 0.01 | 0.50 | 0.100 | 定價頁 [Verified]；日期見 letsdatascience [Secondary] |

### Google

| vendor | model | tier | date | input | cached | output | blended | 來源／標籤 |
|---|---|---|---|---|---|---|---|---|
| Google | Gemini 1.5 Pro（≤128K） | 中 | 2024-05-14 | 3.5 | —（2024-06 起 0.875） | 10.5 | 4.28 → 2.99 | simonwillison.net 2024-09-24 引 Google [Secondary]；快取價 [Memory] |
| Google | 1.5 Pro 降價 | 中 | 2024-10-01 | 1.25 | 0.3125 | 5.0 | 1.21 | developers.googleblog.com（input −64%、output −52%、cache −64%）[Verified-歷史]；金額 [Derived]。Willison 摘要寫 output $2.50，與官方 −52% 不符，故不採用 |
| Google | Gemini 2.5 Pro（≤200K） | 中 | 2025-04-04 | 1.25 | 0.31 → 0.125 | 10 | 1.76 → 1.67 | 定價頁現價 [Verified]；$0.31 與日期 [Memory]；快取降價日期未查到，暫置 2025-06 |
| Google | Gemini 3 Pro（≤200K） | 中 | 2025-11-18 | 2 | 0.20 | 12 | 2.23 | [Memory]；gemini-3-pro-preview 已列為 shut down [Verified] |
| Google | Gemini 3.1 Pro Preview（≤200K） | 中 | 2026-02-19 | 2 | 0.20 | 12 | 2.23 | 定價頁 [Verified]；日期 [Memory] |
| Google | Gemini 4 Argon（首發價至 2026-11-30） | 中／旗艦 | 2026-09-30 | 2 | 0.10 | 10 | 1.96 | 定價頁 [Verified]；日期見 anotherwrapper [Secondary] |
| Google | Gemini 4 Argon（2026-12-01 起） | 中／旗艦 | 2026-12-01 | 4 | 0.20 | 20 | 3.92 | 定價頁 [Verified]（官方已公告） |
| Google | Gemini 1.5 Flash | 低 | 2024-05-14 → 2024-08-12 | 0.35 → 0.075 | — → 0.01875 | 1.05 → 0.30 | 0.428 → 0.073 | simonwillison 2024-08-08 [Secondary]；developers.googleblog（−78%）[Verified-歷史] |
| Google | Gemini 2.0 Flash | 低 | 2025-02-05 | 0.10 | 0.025 | 0.40 | 0.097 | [Memory]；現已 shut down [Verified] |
| Google | Gemini 2.5 Flash | 低 | 2025-06-17 | 0.30 | 0.075 → 0.03 | 2.50 | 0.434 | 定價頁現價 [Verified]；日期 [Memory] |
| Google | Gemini 3 Flash Preview | 低 | 2025-12-17 | 0.50 | 0.05 | 3.00 | 0.558 | 定價頁 [Verified]；日期 [Memory] |
| Google | Gemini 3.5 Flash | 低（價格逼近 Pro） | 2026-05-19 | 1.50 | 0.15（假設為 10%） | 9.00 | 1.67 | simonwillison.net/2026/May/19 [Secondary]；快取價 [Derived 假設] |
| Google | Gemini 3.6／3.7／3.8 Flash（促銷至 2026-12-31） | 低 | 2026-07-21／2026-08-13／2026-09-02 | 0.75（2027 起 1.50） | 0.075（0.15） | 3.75（7.50） | 0.753（1.507） | 定價頁 [Verified]；日期見 chatbase、tech-insider [Secondary] |
| Google | 2.0 Flash-Lite／2.5 Flash-Lite | 更低 | 2025-02-25／2025-07-22 | 0.075／0.10 | —／0.025（現 0.01） | 0.30／0.40 | 0.100／0.097 | 2.5 Flash-Lite 現價 [Verified]；其餘 [Memory] |
| Google | 3.1 Flash-Lite／3.5 Flash-Lite | 更低 | 2026-03-03／2026-07-21 | 0.25／0.30 | 0.025／0.03 | 1.50／2.50 | 0.279／0.412 | 定價頁 [Verified]；日期 [Memory]／[Secondary] |

**2026-10 三家收斂。** GPT-6.1 Sol、Claude Sonnet 5.5、Gemini 4 Argon（首發價）的報價完全相同：input $2、cached $0.10、output $10，B 都是 1.96 [Verified]。中階牌價目前形成單一「市場價」。

## 2. 單一模型存續期間的價格是否變動（問題 5）

**慣例：舊模型不降價，由新模型以同價或更低價取代。**
- 現行官方頁仍以首發價列出 GPT-4（$30/$60）、GPT-4 Turbo（$10/$30）[Verified]。
- Sonnet 3 → 3.5 → 3.7 → 4 → 4.5 → 4.6 連續 6 代都維持 $3/$15，歷時 27 個月（2024-03 至 2026-06）[Verified]。
- Opus 4 和 4.1 仍為 $15/$75；降到 $5/$25 的是新模型 Opus 4.5，不是舊模型降價 [Verified]。

**例外：存續期間的變價。**
- GPT-4o：以新 snapshot 降價，input −50%、output −33%（2024-08）。
- o3：$10/$40 → $2/$8，降 80%，發生於 2025-06 [Memory]；現價 $2/$8 [Verified]。
- Gemini 1.5 Pro：−64%／−52%（2024-10）[Verified-歷史]。
- Gemini 1.5 Flash：−78%（2024-08）。
- Claude 3.5 Haiku：上市一個月內 $1 → $0.80。
- GPT-5.6：Terra −20%、Luna −80%（2026-07-30）；Sol −20%／−33% 是 3 個月促銷（2026-08-21）。
- 只降快取價的案例：Gemini 2.5 Pro 快取 $0.31 → $0.125；Sonnet 5.5 cache hit 降 50%（2026-10-07）。
- 漲價方向：
  - Sonnet 5 原定 9 月漲至 $3/$15，後取消 [Secondary]。
  - Gemini 3.6／3.7／3.8 Flash 已公告 2027-01-01 起價格 ×2 [Verified]。
  - Gemini 4 Argon 已公告 2026-12-01 起 ×2 [Verified]。

**結論 [Derived]**
- 2024 年以前，降價主要發生在同一模型或同一模型系列內（GPT-4o、Gemini 1.5）。
- 2025–2026 年轉為兩種形式：一是換代時改定價（有升有降），二是限時「首發／促銷價」。2026 年已多次出現事先公告的漲價。
- 因此「同一 GPU 服務同一個中階層 T1 年」期間的單價，不應假設呈平滑指數下降，而是階梯式變動，且可能上下來回。

## 3. 已發表分析：固定能力的價格 vs 中階前沿的牌價（問題 6）

**固定能力下的價格（下降極快）**
- Epoch AI〈LLM inference prices〉（2025-03-12）：達到固定能力門檻的最低價，每年下降 9× 到 900×；以 GPQA 上的 GPT-4 水準為例，每年下降 40× [Verified，研究機構]。作者也提醒，最快的降幅集中在最近一年，未必會持續。
- 該研究不處理前沿模型牌價。
- a16z〈LLMflation〉（2024-11-12）：以 MMLU 固定分數計算，每年約下降 10× [Interested-party，創投]。文中也指出前沿模型價格行為不同，例如 o1 的 output 價 $60/M 與 2021 年的 GPT-3 相同。
- 二手報導另稱 Epoch 有「同性能每季降 47%」的新估計，但原文因 robots 限制無法讀取，屬「搜尋到報導、未讀到原文」，本文不採用。

**中階前沿牌價（我們需要的）**
- 目前沒找到正式的學術時間序列，屬「搜尋未找到」。
- capitalandcompute.net 整理旗艦 output 價：2021–2024 年在 $30–60 間持平約 4 年，2026 年才出現下修與新高層（Astra $50）[Secondary]。
- Artificial Analysis：本次未取得可引用的前沿價格序列，屬「未查」，不是「不存在」。
- 本文 §1 的官方牌價序列本身就是證據。兩類指標相差兩個數量級：固定能力每年下降 90%–99.9%，中階層牌價在 2024 年中以後近乎持平。

## 4.（b）年變動率 g

方法 [Derived]：
- 對 ln(B) 和時間（以年為單位）做 OLS 擬合，g = e^斜率 − 1。
- 「事件法」：只用每個價格變動點做回歸。
- 「月階梯法」：每月取當時「最新中階模型的現行價」做回歸，較貼近 L_total 的定義。
- 「端點 CAGR」：只看首尾兩點的年化變動。
- Pooled：三家 vendor 各給一個截距（固定效果），共用一個斜率。

### 依起始窗口的估計

| 窗口 | OpenAI | Anthropic | Google | Pooled（月階梯、FE） |
|---|---|---|---|---|
| 全期，事件法（OpenAI 2023-03／Anthropic 2024-03／Google 2024-05 起） | −37.8% | −24.0% | −13.3% | −30.8%（事件 FE） |
| 全期，月階梯 | −53.9% | −20.1% | −2.6% | — |
| 全期，端點 CAGR | −54.5% | −26.1% | −27.5% | — |
| 2024-05 至 2026-10，月階梯 | −4.4% | −19.4% | −2.6% | **−9.1%** |
| 2024-10 至 2026-10，月階梯 | +28.2% | −14.5% | +45.5% | +16.8% |
| 2025-01 至 2026-10，月階梯 | +46.4% | −17.9% | +44.5% | +20.2% |
| 2024-10 至 2026-10，端點 CAGR | −14.8% | −17.9% | +26.7% | 約 −4.4%（三家對數平均） |
| 2024-05 起，不計快取（cached = input） | +10.1% | −10.6% | +2.8% | +0.4% |
| 2024-05 至 2027-01，含已公告的 Argon ×2 | −10.0% | −21.2% | +6.8% | −8.8% |

### 解讀 [Derived]

1. **有明顯的結構斷點。** 2023-03 到 2024-10 是 GPT-4 定價的重估期：GPT-4 → 4o 的 B 從 33.3 降到 2.7，降了 92%，Gemini 1.5 Pro 也大降。之後中階 B 在 $1.2–5.6 區間來回，2026-10 收斂到 1.96。
2. **2024-10 以後幾乎沒有一致的下降趨勢。**
   - OpenAI 先降到 1.67（GPT-5），再升到 5.58（GPT-5.5／5.6 Sol），又回到 1.96。
   - Google 從 1.21 升到 2.23，再到 1.96，並已公告 2026-12 起升到 3.92。
   - 只有 Anthropic 單調下降，約 −15% 到 −20%/年。其降幅來自兩個一次性步階：2024-08 引入快取，2026-06 推出 Sonnet 5 降 33%。
3. **g 對窗口與方法極度敏感**，在同一份資料上可得出 −9% 到 +20%。快取折扣的引入（一次性，約 −30%）在 2024 年後的降幅中占很大一部分；不計快取時，pooled 約為 0%。
4. **對模型假設 g = −10%（範圍 −25% 到 +5%）的意涵：**
   - 2024-05 起的 pooled 月階梯值 −9.1% 與基準相近。
   - 2024-10 起的端點值約 −4%，2024-10 起的回歸值為 +17%，兩者都高於損益兩平的 −3.7%。
   - 證據無法判斷 g 在 −3.7% 的哪一側。合理中心約落在 −10% 到 0% 之間，−25% 只有在納入 2023–24 重估期時才成立。
   - 建議將標籤由 Assumed 改為「Derived-窗口敏感」，並同時呈報窗口選擇。

## 5.（c）ρ（低階 B ÷ 同日中階 B，同一 vendor）[Derived]

| 日期 | OpenAI mini 系 | OpenAI nano 系 | Anthropic Haiku | Google Flash | Google Flash-Lite |
|---|---|---|---|---|---|
| 2023-03 | 0.060（3.5T／GPT-4） | — | — | — | — |
| 2023-12 | 0.091 | — | — | — | — |
| 2024-06 | 0.100（3.5T／4o） | — | 0.083（H3／S3.5） | 0.100（1.5F 原價） | — |
| 2024-09 | 0.060（4o mini） | — | 0.084 | 0.024（1.5F 降價後） | — |
| 2024-12 | 0.060 | — | 0.267（H3.5） | 0.060 | — |
| 2025-05 | 0.200（4.1 mini） | 0.050 | 0.267 | 0.055（2.0F） | 0.057 |
| 2025-09 | 0.200（5 mini） | 0.040 | 0.267 | 0.260（2.5F） | 0.058 |
| 2025-11 | 0.200 | 0.040 | 0.333（H4.5） | 0.260 | 0.058 |
| 2026-01 | 0.143 | 0.029 | 0.333 | 0.250（3F） | 0.043 |
| 2026-04 | 0.300（5.4 mini） | 0.082 | 0.333 | 0.250 | 0.125 |
| 2026-06 | 0.150 | 0.041 | 0.333 | 0.750（3.5F） | 0.125 |
| 2026-08 | 0.400（5.6 Terra 降價後） | 0.040 | 0.500（S5 降價） | 0.338 | 0.185 |
| 2026-09 上旬 | 0.555（Terra／5.6 Sol 促銷價） | 0.056 | 0.500 | 0.338 | 0.185 |
| 2026-10-18 | 0.051（GPT-6 Luna；GPT-6 沒有 mini 層） | 0.051 | 0.051（H5.5） | 0.384（3.8F／Argon；2027 起兩者都 ×2，ρ 不變） | 0.210 |

### 解讀

- ρ 的分布呈雙峰：
  - 「mini／Haiku／Flash」層：2025 年後約 0.20–0.40（2026 年偶有 0.5–0.75）。
  - 「nano／Lite」層：約 0.03–0.08，2026 年 Google Lite 上升到 0.12–0.21。
  - 2026-10 時 OpenAI 與 Anthropic 都把最低層壓到 $0.10/$0.50，ρ 約 0.05。
- 模型基準 ρ = 0.5 位於觀察到的價格比上緣，只有 2026-08 的 Anthropic 和 2026-09 的 OpenAI Terra 曾短暫達到。觀察值的中位數約 0.2–0.3（mini 層）。
- [Analogy] 但模型中的 ρ 是「同一張 GPU 的價值比」，不是 token 價格比。GPU 降級去服務小模型時，每 GPU-hour 的 token 吞吐量會高出數倍。因此價值比 ≈ 價格比 × 吞吐倍數，可能明顯高於上表的價格比。這個轉換需要另外的吞吐證據，本文未涵蓋。

## 6. 尚未解決的問題與注意事項

- 數個歷史日期與快取價屬 [Memory]：GPT-3.5T 系列、3.5 Sonnet 快取生效日、Gemini 2.5／3 Pro 日期、o3 原價。Wayback 被擋，無法封存佐證。
- 所有 [Verified] 數字是經 WebFetch 摘要模型讀取官方頁面而得，不是原始 HTML。重點數字最好以人工或瀏覽器再核對一次，特別是 2026 年的新模型。
- 「中階」歸屬屬判斷：
  - OpenAI：採官方說法「Sol = GPT-5 無後綴層」。2026-09 起 Astra 是新增的頂層，不納入中階。
  - Google：依題意採 Pro 線，再接 Gemini 4 Argon（官方稱「flagship」）。如果把 Argon 視為頂層，Google 中階的 2026-10 點會懸空。
- 促銷價與限時價（GPT-5.6 Sol、Gemini Flash、Argon）都按「當時實際牌價」計算，並另外列出已公告的未來價。

## 摘要

- **2026-10 三家中階牌價收斂。** GPT-6.1 Sol、Sonnet 5.5、Gemini 4 Argon（首發價）同為 $2／$0.10／$10，混合價 B = 1.96 [Verified]。
- **g 有結構斷點。**
  - 2023-03 到 2024-10 是 GPT-4 定價的重估期，B 從 33.3 降到 2.7，年化約 −55%。
  - 2024-10 以後，中階 B 在 $1.2–5.6 之間來回，沒有一致的下降趨勢。
  - Pooled 月階梯回歸（三家各自截距）：2024-05 起 −9.1%/年；2024-10 起 +16.8%/年；2024-10 起端點值約 −4%/年。不計快取（cached 視同 fresh input）時約 0%。
  - 分 vendor：Anthropic −15% 到 −20%/年，來自兩個步階（2024-08 引入快取、2026-06 推出 Sonnet 5）；OpenAI 先跌後漲再跌；Google 2024-10 後上升，並已公告 Argon 2026-12 起價格 ×2。
  - 損益兩平 −3.7% 落在證據區間內，證據判斷不了 g 在哪一側。−25% 只有納入 2023–24 重估期才成立。
- **單一模型很少在存續期間降價。** 慣例是新模型以同價或更低價取代舊模型（Sonnet 連續 6 代 $3/$15，歷時 27 個月）。存續期間降價的例外：GPT-4o、o3（−80%）、Gemini 1.5、GPT-5.6。2026 年已出現事先公告的漲價：Gemini Flash 與 Argon ×2，Sonnet 5 原定漲價後取消。
- **ρ 呈雙峰。** mini／Haiku／Flash 層約 0.2–0.4；nano／Lite 層約 0.03–0.08。2026-10 時 OpenAI 與 Anthropic 最低層約 0.05，Google Flash 約 0.38。基準 ρ = 0.5 位於上緣。另需注意，ρ 應為 GPU 價值比（價格比 × 小模型的吞吐倍數），不能直接套用 token 價格比。
- **已發表分析的兩種指標。** Epoch（每年 9×–900×）與 a16z（每年 10×）衡量的是固定能力下的價格；中階前沿牌價本身近乎持平。

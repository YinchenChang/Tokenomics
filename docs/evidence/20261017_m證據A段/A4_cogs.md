# A4：OpenAI 2025 營業成本（COGS $7.5B）拆解：算力與非算力

研究日期：2026-10-17｜方法：先整理原始數據並交叉驗證，最後才下判斷。全程唯讀，沒有修改任何 repo 或 Excel。

標籤說明：
- [Verified]：經審計報表本身，或至少兩家獨立媒體轉述同一份文件。
- [Interested-party]：來自利害關係人，括號內註明是誰、動機為何。
- [Analogy]：可比公司的數據。
- [Derived]：本文自行推算。

「搜尋未果」不等於「不存在」：凡是寫「搜尋未果」，意思是公開網路上找不到，不代表該資訊不存在。

---

## 0. 基準數據（經審計 2025 損益表，Zitron 取得，FT 獨立驗證）

| 科目 | 2025 | 其中付給 Microsoft | 2024 |
|---|---|---|---|
| 營收 | $13.07B | — | $3.7B |
| 營業成本 | $7.5B | $6.047B | $2.65B |
| 研發 | $19.18B | $10.59B | $7.81B |
| 銷售及行銷 | $5.73B | $0.527B | $1.11B |
| 管理費用 | $1.57B | $0.042B | $0.907B |
| 總成本費用 | $34B | 合計 $17.2B | $12.48B |

- 另有兩筆反向款項：Microsoft 付給 OpenAI $303M，SoftBank 付給 OpenAI $867M。
- 來源：https://wheresyoured.at/exclusive-openai-financials （2026-06-15/16）。原文稱文件經 "independently verified by the Financial Times"；Quartz 轉述相同說法：https://qz.com/openai-leaked-financials-losses-revenue-ipo-061626 。[Verified]
- 推算：GAAP 毛利率 2025 為 (13.07−7.5)/13.07 = 42.6%，2024 為 28.4%。[Derived]
- 營業成本中不屬於 Microsoft 的部分：7.5 − 6.047 = **$1.453B**。[Derived]

---

## 1. 給 Microsoft 的 20% 營收分成：記在營業成本、營收減項，還是其他科目？

### 1a. 直接證據
- **搜尋未果。** 沒有找到任何報導（The Information、FT、Zitron、TechCrunch、Sacra）明確說明 OpenAI 把營收分成記在哪個會計科目。
- Zitron 2026-06 那篇只列出「各科目付給 Microsoft 的金額」，沒有標示哪一筆是營收分成。
- Sacra 的整理同樣沒有分類："does not classify either payment as a cost of revenue or a reduction of revenue"（https://sacra.com/chat/h/824bbb60-05b2-40cf-b6d3-e08254a0b265 ）。

### 1b. 營收分成的金額與口徑
Zitron 取得的 Microsoft 內部文件（https://wheresyoured.at/oai_docs ，2025-11-12）：
- 2024 年營收分成 $493.8M。
- 2025 年 Q1 $206.4M、Q2 $248.3M、Q3 $411.1M，前三季合計 **$865.9M**。
- 依據為 Microsoft 內部文件，原報導後於 2026-04 加註為應計基礎。標記 [Interested-party]：文件出自 Microsoft，Zitron 本人對 AI 泡沫持空方立場。TechCrunch 有報導同一份文件。

**這些金額是淨額。** TechCrunch（2025-11-14）引述消息人士：
- Microsoft 會把 Bing 與 Azure OpenAI 的分潤（約 20%）付回給 OpenAI，再 "deducts those figures from its internally reported revenue share numbers"。
- 來源：https://www.techcrunch.com/2025/11/14/leaked-documents-shed-light-into-how-much-openai-pays-microsoft 。[Interested-party：匿名消息人士]

推算如下，全部為 [Derived]：
- 第四季若按 Q3 再成長約 20% 估算，2025 全年淨分成約 **$1.3–1.5B**。
- 若改用總額口徑，20% × $13.07B = **$2.61B**。
- 推算總額 2.61 減去淨額 1.3–1.5，差額約 $1.1–1.3B，應該就是 Microsoft 付回的分潤。
- 審計報表上 Microsoft 只付給 OpenAI $303M，代表大部分分潤是用抵銷方式處理，而不是現金對付。

### 1c. 從間接證據推論 OpenAI 營收是總額還是淨額
- 審計營收 $13.07B，與 The Information／Reuters 引用的內部數字「2025 revenue totaled $13 billion」一致（https://finance.yahoo.com/news/openai-sees-compute-spend-around-223950561.html ，2026-02-20）。
- 若營收分成被列為營收減項，總額營收應該是 $14.4–15.7B，但沒有任何媒體報過這個量級。
- 推論：OpenAI 營收較可能是**總額、未扣除營收分成**。信心度為中，因為內部數字與審計數字可能用同一套口徑，這個比對只是弱證據。[Derived]
- 會計上的另一種可能：Microsoft 同時是 OpenAI 的客戶（Azure OpenAI 授權）。若被認定為「應付客戶之對價」（ASC 606-10-32-25），營收分成可能要沖減營收；若被視為投資人的利潤參與權，則可能另列。**這兩種處理方式都搜尋未果，沒有找到任何報導證實。**

### 1d. Microsoft 端怎麼認列
- Microsoft FY2026 10-K（截至 2026-06-30）的文字："recorded revenue from commercial arrangements with OpenAI, inclusive of revenue sharing payments, of $24.1 billion"，另有應收 OpenAI 款項 $6.0B。
- 來源：https://wheresyoured.at/news-microsoft-disclosures-suggest-openai-sales-account-for-around-70-of-fy26-ai-revenue-more-than-7-of-fy26-revenue 、https://www.techzine.eu/news/infrastructure/143461/microsoft-earned-24-billion-from-openai-but-its-unclear-exactly-how/ （2026-08-05/06）。
- 標記 [Verified]：兩家媒體引述同一句 10-K 原文。原文未能直接從 SEC 取得，SEC 全文搜尋被代理擋下。
- 結論：**Microsoft 把收到的營收分成記為營收**，而不是投資報酬。這與 OpenAI 端把它記為費用相容，但無法證明它落在 OpenAI 的哪個科目。

### 1e. 合約後續變化
- 2025-10 重組協議：營收分成持續到 AGI 經專家小組驗證為止，Microsoft 表示 "payments will be made over a longer period of time"（https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/ ）。
- 2026-04-27 修約：
  - OpenAI 照原比例支付到 2030 年，總額上限 $38B。上限金額出自 The Information 引述消息人士。[Interested-party]
  - Microsoft "will no longer pay a revenue share to OpenAI"。
  - 來源：https://ppc.land/microsoft-and-openai-rewrite-the-deal-what-actually-changed/ 、https://www.outlookbusiness.com/corporate/openai-microsoft-deal-gets-38-bn-revenue-cap-amid-ipo-talks
- 這次修約不影響 2025 年數字，但意味著 2026 年起總額與淨額的差異會消失。

---

## 2. 營業成本的其他組成

### 2a. 推論營業成本中的 Azure 算力
**用帳單規模做上限比對：**
- 依 Zitron 文件，OpenAI 在 Azure 上的推論支出：2025 年 Q1 $2.075B、Q2 $2.947B、Q3 $3.648B，前三季 **$8.67B**；2024 全年 $3.77B（https://wheresyoured.at/oai_docs ）。[Interested-party：同 1b]
- 第四季外推約 $4.3–4.5B，2025 全年 Azure 推論約 **$13B**。[Derived]
- 審計營業成本裡付給 Microsoft 的只有 $6.047B，代表 **Azure 推論帳單至少約 53% 不在營業成本**。最可能落在研發：研發中付給 Microsoft 的 $10.59B 足以容納約 $7B 推論加約 $3.6B 訓練。[Derived]
- 2024 年同樣如此：營業成本總額 $2.65B 小於 Azure 推論 $3.77B。
- 推論：**免費用戶及研究用的推論很可能記在研發，不在營業成本。** 沒有直接報導證實，搜尋未果。

**用「算力毛利率」交叉驗證：**
- Fortune／Bloomberg 轉述 The Information（2025-12-21）：算力毛利率定義為 "share of revenue after the costs of running models for paying users"，2024 年底為 52%，2025 年 10 月為 70%（約為 2024 年 1 月的兩倍）。
- 來源：https://www.fortune.com/2025/12/21/openai-compute-margins-revenue-chatgpt-earnings-sam-altman 。
- 標記 [Interested-party]：OpenAI 內部指標，經消息人士流出，OpenAI 拒絕評論。OpenAI 有動機展示單位經濟改善。
- 2025 全年平均算力毛利率若取 52–65%，付費用戶推論成本約 **$4.6–6.3B**，中點約 $5.2B。[Derived]
- 這個區間與營業成本「只含付費用戶推論」的假設吻合。

### 2b. 「調整後毛利率」與 GAAP 毛利率的矛盾（尚未解決）
- The Information 經 The Decoder／Reuters 轉述：調整後毛利率 2025 年 33%，2024 年 40%，目標 46%；推論成本 2025 年成長四倍。
- 來源：https://the-decoder.com/openai-adds-111-billion-to-its-cash-burn-forecast-as-ai-costs-spiral-beyond-projections/ （2026-02-21）。
- 「調整後」排除或納入什麼，**搜尋未果**，各來源都沒有定義。
- 比對結果互相衝突：
  - 2025 年 GAAP 42.6% 高於調整後 33%。
  - 2024 年 GAAP 28.4% 低於調整後 40%。
  - 兩年方向相反，代表兩者口徑不同，或口徑中途改過。
- 33% 換算成本為 0.67 × 13.07 = $8.76B，比 GAAP 營業成本多 $1.26B。可能的解釋：調整後口徑把部分免費用戶推論算進去，或採用營收分成總額。**目前未解決，不宜把 33% 直接套到審計營業成本上。**

### 2c. 金流與應用商店手續費
- 直接數字：**搜尋未果。**
- ChatGPT 行動版 2025 年消費者支出約 **$2.48B**（Appfigures 估計，https://techcrunch.com/2025/12/18/chatgpts-mobile-app-hits-new-milestone-of-3b-in-consumer-spending/ ）。[Analogy／第三方估計]
- 若營收按總額認列，應用商店抽成 15–30%，約為 **$0.37–0.74B**。
- 網頁端與 API 以信用卡或發票收款，約 $9–10B 營收乘以約 2.5–3%，約 $0.2–0.3B。
- 合計金流成本約 **$0.6–1.0B**。[Derived]
- 注意：若 OpenAI 按淨額認列行動版營收，應用商店抽成就不在營業成本裡。這點**搜尋未果**。

### 2d. 股份基礎給付
- 報表各科目的股份基礎給付金額：**搜尋未果**，Zitron 的文章沒有列出。
- 已知數字：
  - 2025 上半年股份基礎給付 $2.5B（The Information 經 Sacra／Longterm Wiki 轉述，https://www.longtermwiki.com/sourcing/fact/f_DtyJCdGd1g ）。
  - WSJ（2025-12-31，經 The Decoder 轉述）：平均每名員工 $1.5M、約 4,000 名員工、股份基礎給付占營收 46.2%（以 2025 預測為基礎）（https://the-decoder.com/openais-stock-compensation-averages-1-5-million-per-employee-dwarfing-every-tech-startup-in-history/ ）。
  - 依此推算全年約 **$6B**。[Interested-party：OpenAI 提供給投資人的預測／Derived]
- 營業成本中的股份基礎給付推測很小：營業成本相關人員只有客服與基礎設施維運，大部分股份基礎給付應在研發。[Derived，沒有直接證據]

### 2e. 其他項目
以下三項都**搜尋未果**：
- 客服、主機維運人員成本。
- 資料授權：已知與新聞集團、Reddit 等有授權協議，但沒有找到金額，也不知道記在營業成本還是研發。
- 非 Azure 算力：CoreWeave 2025 年主要經由 Microsoft 轉供 OpenAI，這部分成本已經包含在 Azure 帳單裡。直接合約與 Oracle、Google Cloud 在 2025 年的金額不明。

非 Microsoft 營業成本 $1.453B 的推估組成 [Derived]：
- 金流約 $0.6–1.0B。
- 剩餘約 $0.45–0.85B，涵蓋非 Azure 算力、客服、股份基礎給付、授權等。

---

## 3. Microsoft 給 OpenAI 的 Azure 定價與抵用額度
- **定價：** The Information 經 DCD 轉述（2024-07-24）："OpenAI gets heavily discounted rates from Microsoft Azure… about $1.30 per A100 server per hour, way below normal rates"（https://datacenterdynamics.com/en/news/openai-training-and-inference-costs-could-reach-7bn-for-2024-ai-startup-set-to-lose-5bn-report ）。[Interested-party：流出的 OpenAI 財務文件]
  - 這說明是大幅折扣，屬於低於牌價的協議價，但不能證明是成本加成。
  - 成本加成的說法：**搜尋未果**。
- **投資款中的雲端抵用額度：** Semafor（2023-11）報導，Microsoft 約 $10B 投資中 "much…is actually tied up in cloud compute"（https://www.techradar.com/pro/most-of-microsofts-dollar10bn-investment-in-openai-has-gone-on-cloud ）。
  - Microsoft 承諾投資 $13B，截至 2026-06-30 已撥付 $11.9B（Techzine）。
  - 抵用額度在 OpenAI 帳上如何費用化，以及 2025 年還剩多少：**搜尋未果**。
- 對本題的意義：
  - 審計報表付給 Microsoft 的 $17.2B 是費用化金額，不等於現金支出。
  - 無論以現金還是抵用額度支付，都計入營業成本、研發等科目，所以不影響 $6.047B 屬於算力的判斷。
  - 但如果抵用額度按折扣價入帳，將來恢復牌價時，算力成本會跳升。

---

## 4. 可比公司：金流成本占營收比重 [Analogy]

| 公司 | 數字 | 來源 |
|---|---|---|
| Duolingo 2024 | 營業成本 $203.6M，毛利率 72.8%。營業成本 "predominantly consists of third-party payment processing fees… in addition to hosting fees and generative AI costs"。按總額認列，金流費用列入營業成本；Apple 占營收 61%、Google 占 20%，抽成 15–30%。 | https://www.sec.gov/Archives/edgar/data/1562088/000156208825000042/duol-20241231.htm |
| Match Group 2024 | 應用內購手續費 **$696.6M**，占營收 $3,479.4M 的 **20.0%**；營業成本占營收 28%。 | https://www.sec.gov/Archives/edgar/data/891103/000089110325000027/mtch-20241231.htm |
| 信用卡收款（網頁端） | 一般約 2.5–3.5%（業界常識）。Stripe 官網定價頁本次被權限擋下，**未能核實**。 | — |
| Spotify、Netflix | 營業成本以版權費或內容攤銷為主，金流費用沒有單獨揭露。本次未取得具體數字。 | — |

OpenAI 的營收組成中，行動版約占 19%（$2.48B／$13.07B），比 Duolingo、Match 低很多，所以金流成本占營收比重應該遠低於 20%。推估約 5–8%，即 $0.6–1.0B。[Derived]

---

## 5. 綜合判斷：$7.5B 營業成本中算力占多少

| 情境 | 營收分成的處理 | 營業成本中的算力 | 算力占比 | 與交叉證據的吻合度 |
|---|---|---|---|---|
| A | 不在營業成本（營收減項或其他科目） | 6.047 + 0.2–0.5 ≈ $6.2–6.5B | **83–87%** | 隱含付費推論算力毛利率約 50%，低於報導的 52–70% 區間，吻合度偏低 |
| **B（最佳估計）** | 淨額 $1.3–1.5B 記在營業成本的 Microsoft 項下 | 4.6–4.75 + 0.2–0.5 ≈ $4.8–5.2B | **64–70%** | 付費推論約 $5.2B，加分成 $1.4B、金流 $0.8B、其他，合計約 $7.5B，吻合度最高 |
| C | 總額 $2.61B 記在營業成本 | 3.44 + 0.2–0.5 ≈ $3.6–3.9B | **48–52%** | 隱含算力毛利率約 71%，高於全年平均，偏樂觀 |

**結論 [Derived]：** 2025 年營業成本 $7.5B 中，算力約 **$4.8–5.2B，占 64–70%**，中點約 67%。非算力部分約 $2.3–2.7B：營收分成約 $1.3–1.5B、金流約 $0.6–1.0B、其他約 $0.3–0.5B。

**最大不確定性：**
1. 營收分成記在哪個科目。直接證據搜尋未果。
2. The Information「調整後毛利率 33%」的口徑與 GAAP 衝突。
3. Azure 推論帳單約 $13B 遠大於營業成本，代表免費用戶推論大概率在研發。若模型把「推論」全數視為營業成本，會嚴重高估毛利壓力。

---

## 最終表

| 項目 | 數字 | 來源 URL | 日期 | 標籤 | 對「$7.5B 營業成本中算力占比」的意涵 |
|---|---|---|---|---|---|
| 營業成本總額／付給 Microsoft 部分 | $7.5B／$6.047B | https://wheresyoured.at/exclusive-openai-financials | 2026-06-16 | Verified（FT） | 算力上限約為 Microsoft 部分加少量非 Azure 算力 |
| 非 Microsoft 營業成本 | $1.453B | 同上 | 2026-06-16 | Derived | 金流、客服、其他算力都在這裡 |
| 淨營收分成，2025 前三季 | $865.9M | https://wheresyoured.at/oai_docs | 2025-11-12 | Interested-party（Microsoft 文件；Zitron 空方立場） | 全年約 $1.3–1.5B；若記在營業成本，算力占比降 18–20 個百分點 |
| 分成為淨額，扣除 Bing/Azure 分潤 | 約 20% 互付 | https://www.techcrunch.com/2025/11/14/leaked-documents-shed-light-into-how-much-openai-pays-microsoft | 2025-11-14 | Interested-party（匿名消息人士） | 總額 $2.61B 與淨額差異約 $1.2B |
| Microsoft 付給 OpenAI | $303M | https://wheresyoured.at/exclusive-openai-financials | 2026-06-16 | Verified | 分潤多以抵銷方式處理 |
| 營收分成的會計科目 | 搜尋未果 | — | — | — | 最大不確定因素，形成情境 A/B/C |
| Microsoft 將收到的分成記為營收 | FY26 OpenAI 相關營收 $24.1B | https://www.techzine.eu/news/infrastructure/143461/microsoft-earned-24-billion-from-openai-but-its-unclear-exactly-how/ | 2026-08-06 | Verified（10-K 原文經轉述） | 對方記營收，與 OpenAI 記為費用相容 |
| Azure 推論帳單 | 2025 前三季 $8.67B，全年約 $13B | https://wheresyoured.at/oai_docs | 2025-11-12 | Interested-party／Derived | 約 53% 以上不在營業成本，免費用戶推論可能在研發 |
| 付費用戶算力毛利率 | 2024 年底 52%，2025-10 70% | https://www.fortune.com/2025/12/21/openai-compute-margins-revenue-chatgpt-earnings-sam-altman | 2025-12-21 | Interested-party（OpenAI 內部指標） | 付費推論約 $4.6–6.3B，支持情境 B |
| 調整後毛利率 | 2025 33%，2024 40% | https://the-decoder.com/openai-adds-111-billion-to-its-cash-burn-forecast-as-ai-costs-spiral-beyond-projections/ | 2026-02-21 | Interested-party（The Information 流出文件） | 與 GAAP 方向相反，口徑不明，不宜套用 |
| 股份基礎給付 | 2025 上半年 $2.5B；全年約 $6B（占營收 46%） | https://the-decoder.com/openais-stock-compensation-averages-1-5-million-per-employee-dwarfing-every-tech-startup-in-history/ | 2025-12-31 | Interested-party／Derived | 營業成本中的部分推測很小，各科目分配搜尋未果 |
| 行動版消費者支出 | $2.48B | https://techcrunch.com/2025/12/18/chatgpts-mobile-app-hits-new-milestone-of-3b-in-consumer-spending/ | 2025-12-18 | Analogy（Appfigures 估計） | 應用商店抽成 $0.37–0.74B |
| Azure 折扣價 | 每台 A100 伺服器每小時約 $1.30 | https://datacenterdynamics.com/en/news/openai-training-and-inference-costs-could-reach-7bn-for-2024-ai-startup-set-to-lose-5bn-report | 2024-07-24 | Interested-party | 算力以折扣價入帳；恢復牌價時有上行風險 |
| 投資款多為雲端算力 | 約 $10B 中 "much" | https://www.techradar.com/pro/most-of-microsofts-dollar10bn-investment-in-openai-has-gone-on-cloud | 2023-11-20 | Interested-party（消息人士） | 不影響科目歸屬；費用化方式搜尋未果 |
| Match 應用內購手續費 | 營收的 20.0% | https://www.sec.gov/Archives/edgar/data/891103/000089110325000027/mtch-20241231.htm | 2025-02 | Analogy | 行動版占比高的公司上限約 20% |
| Duolingo 營業成本 | 營收的 27.2%，以金流費用為主 | https://www.sec.gov/Archives/edgar/data/1562088/000156208825000042/duol-20241231.htm | 2025-02 | Analogy | 按總額認列，金流費用列入營業成本 |
| 2026-04 修約 | 分成總額上限 $38B，到 2030 年；Microsoft 不再付分潤 | https://www.outlookbusiness.com/corporate/openai-microsoft-deal-gets-38-bn-revenue-cap-amid-ipo-talks | 2026-05-12 | Interested-party（The Information 消息人士） | 2026 年起總額與淨額差異消失 |
| **算力占營業成本（最佳估計）** | **$4.8–5.2B（64–70%）** | 本文綜合 | 2026-10-17 | Derived | 情境 A 為 83–87%，情境 C 為 48–52% |


## 更正（2026-10-27 證據引述回查）

> 來源：API 自動回查（`tools/evidence_audit/`，報告 `docs/reports/20261027_證據引述回查.md`）＋未參與代理人工複核。原文保留不改，以本節為準。

- **2025 年營收 $13B 的出處**：是 **Reuters（2026-02-20）引匿名知情人士**，不是 The Information；該文引用 The Information 的只有推論成本與毛利率。數字與審計營收 $13.07B 一致，結論不變；同源計數應把這筆算作 Reuters 來源。

# L2 硬體端證據：GPU 機隊終身價格係數 L、T1、ρ、g

研究日期：2026-10-18｜唯讀研究，未修改任何 repo / Excel
模型現行假設（全為 Assumed）：L_total = 0.643（0.342–1.162）；g = −10%/年；T1 = 4 年（3–5）；ρ = 0.5（0.05–1.0）；損益兩平需 L ≥ 0.756；T = 6 年。既有類比：DB_Evidence E246 H100 租價指數 0.42–0.70。

標籤說明：
- [Verified]：第一手文件（SEC 申報、官方價目/公告），或兩個以上獨立來源一致。
- [Interested-party]：利害關係方的說法，附上當事方名稱與誘因。
- [Analogy]：類比資料。
- [Derived]：本文自行推算。

---

## 0. 先做量化（在讀模型結論前，先獨立處理原始資料）

### 0.1 H100 租價路徑（$/GPU-hr）

| 時點 | 價格 | 類型 | 來源 | 標籤 |
|---|---|---|---|---|
| 2023-07-26 | AWS p5.48xlarge 約 $98.3/節點 → **$12.29/GPU** | 隨需（on-demand）牌價 | NextPlatform：3 年隨需總價 $2.58M（換算 $98.2/hr）；Azure ND96isr H100 v5 至 2026-09 仍為 $12.29/GPU | [Derived]，兩來源一致 |
| 2023-07 | AWS p5 3 年預留合約 $1.13M → 約 **$5.37/GPU**（比隨需低 56%） | 3 年合約 | NextPlatform 2023-07-27 | [Verified] 單一來源，數字可回推 |
| 2023-03 | 典型價約 $4.70，尖峰 >$8 | 市場隨需 | latent.space，經 gpusmith 轉引 | [Analogy]（二手） |
| 2023-08~12 | 雲端巨頭（下稱巨頭）中位數 $7.76 | 巨頭隨需 | Silicon Data 部落格 | [Interested-party]：Silicon Data 銷售指數產品，與 CME 合作期貨 |
| 2024 年初 | 約 $2.85 | 新雲/市場 | latent.space（gpusmith 轉引） | [Analogy] |
| 2024 下半年 | 巨頭 $9.34；新雲 $2.99；租賃平台 $2.58（中位數） | 依通路區分 | Silicon Data | [Interested-party] |
| 2024-09 → 2025-06 | Silicon Data H100 指數 $3.06 → $2.36 | 指數 | Introl 轉引 Silicon Data | [Interested-party] |
| 2025-06-01 | AWS P5 隨需 **−44%**；3 年 EC2 Savings Plan −45%；P5en（H200）−25%；P4d（A100）−33% | 牌價 | AWS 官方部落格 2025-06-05 | [Verified] |
| 2025 下半年 | 巨頭 $6.26；新雲 $3.33；租賃平台 $1.95 | 依通路區分 | Silicon Data | [Interested-party] |
| 2025-10 | 1 年合約低點 **$1.70** | 1 年合約 | SemiAnalysis（經 gpusmith、Akash、CryptoBriefing 轉引） | [Interested-party]，不可單獨使用（見下行交叉驗證） |
| 2025-12-09 → 2026-01-06 | Silicon Data 指數 $2.00 → $2.20（+10%） | 隨需指數 | Silicon Data（gpusmith 轉引） | [Interested-party]，方向與 SemiAnalysis 一致 |
| 2026-03 | 1 年合約 **$2.35**（較 2025-10 低點 +38%）；2026-04 區間 $2.10–2.70 | 1 年合約 | SemiAnalysis（多家轉引） | 方向有 Silicon Data 與 GetDeploying 佐證，視為 [Verified 方向] |
| 2026-09-11 | GetDeploying 隨需中位數約 $3.39（53 家）；近 90 天 +10%、年增 +11% | 隨需 | Akash 轉引 GetDeploying | [Analogy]/[Interested-party]（Akash 自身也賣算力） |
| 2026-09-12 | AWS P5 $6.88、Azure ND96 $12.29、GCP a3 $11.06、CoreWeave $6.16、Lambda SXM $3.99、Vast $1.73 起 | 各家牌價 | Akash 價格表 | [Verified]：AWS $6.88 = $12.29 × 0.56，與 AWS 公告的 −44% 吻合 |

另有兩項來源，都沒有拿到數值：
- Ornn 指數（Bloomberg 代碼 ORNNH100，ICE 期貨 2026-05 宣布）：已搜尋，**公開網頁沒有歷史數值**，數據在 Bloomberg 終端機內。屬「搜尋未得」，不是「不存在」。
- CoreWeave 舊版牌價頁：H100 HGX $4.76、A100 80GB $2.21，但只是 GPU 元件價，與現行含 CPU/RAM 的節點價（$6.16）**不可比較**。

### 0.2 A100

| 時點 | 價格 | 來源 | 標籤 |
|---|---|---|---|
| 2020-11 上市 | AWS p4d.24xlarge 約 $32.77/節點 → **$4.10/GPU** | 推算：現價 $21.96 = $32.77 × 0.67，與 AWS 公告的 −33% 精確吻合 | [Derived] |
| 2025-06 | AWS P4d −33% → **$2.74/GPU** | AWS 部落格；vpsbenchmarks 現價 $21.96 | [Verified] |
| 2026-10-17 | 隨需中位數 **$1.59**（25 家）、預留 $1.63、現貨 $1.14；CoreWeave $2.70、Azure $3.40 | flopper.io | [Analogy]（聚合網站） |
| 2026-06 | A100 80GB $1.61–1.62，報告稱「自低點急升」 | UOB Private Bank〈Compute is revenue〉，資料取自 Bloomberg | [Analogy]，與 flopper 一致 |
| 2025 全年 | A100 平均價「在 2025 年上升」 | CoreWeave Q4'25 法說，Intrator | [Interested-party] |

已搜尋但未得：2021–2024 年 A100 市場（新雲）一致的時間序列。這是搜尋未得，不是不存在；SDA100RT 指數存在但未公開。

### 0.3 H200 / B200 / GB200

- **H200**：
  - AWS P5en 2025-06 牌價 −25% [Verified]。
  - 2026-08：巨頭約 $10–10.60，新雲 $3.82–4.59 [Analogy, Jarvislabs]。
  - CoreWeave $6.31 [Interested-party 牌價]。
  - 上市時（2024）的系統性價格序列：搜尋未得。
- **B200**：
  - Lambda 隨需 $5.50（2026-04，Silicon Analysts）→ $6.79（2026-10-06，morphllm）：**+23%** [Analogy]。
  - 每 PFLOP 租價：0.72（2025 Q1）→ 0.78（2026 Q2）[Analogy]。
  - UOB 2026-06：約 $5.42。
  - CoreWeave 牌價 $8.60 [Interested-party]。
  - 結論：**Blackwell 上市後約 1.5 年，價格未見下跌。**
- **GB200 NVL72**：CoreWeave 牌價 $10.50/GPU [Interested-party]。歷史序列：搜尋未得。

### 0.4 推算的年降幅 g 與 L（[Derived]）

| 序列 | 推算 | 結果 |
|---|---|---|
| AWS H100 牌價 | $12.29 →（2025-06）$6.88，3 年 CAGR | **g = −17.6%/年** |
| AWS A100 牌價 | $4.10 → $2.74，5.9 年 CAGR | **g = −6.6%/年** |
| H100 市場隨需 | $4.70（2023-03）→ $2.9–3.4（2026 年中），3.3 年 | **g = −9.4% ~ −13.6%/年** |
| H100 最差段 | 尖峰 $8 → $2.85，約 2 年 | 約 −40%/年，**之後反彈 +38%** |
| **L：AWS A100 牌價**，6 年 | 4.58 年 × $4.10 + 1.42 年 × $2.74 | **L ≈ 0.92** |
| **L：AWS H100 牌價**，6 年（2023-07 → 2029-07） | 假設 2025-06 後持平 | **L ≈ 0.70** |
| 同上 | 假設 2027 年再降 30% | **L ≈ 0.64** |
| **L：H100 市場**，以第 1 年均價 $3.8 為基準 | 年均相對值 Y1 1.00、Y2 0.76、Y3 0.66、Y4 0.79（2026 已觀測） | Y5–6 持平：**0.80**；Y5–6 每年 −20%：**0.73**；Y5–6 跌到 0.40：**0.67** |
| 同上，改以上市價 $4.70 為基準 | 同上三種情境 | **0.65 / 0.59 / 0.54** |
| **L：合約產能** | 5 年固定價 + 第 6 年以原價 95% 續約 | **L ≈ 0.99** |

Y2–Y4 是由多來源年均值粗估的 [Derived]，精度約 ±0.1。

---

## 1. 長約是否鎖價（決定合約產能的 L 是否 ≈ 1）

- **CoreWeave FY2025 10-K（2026 申報）**：
  - 客戶透過「multi-year committed contracts … on a take-or-pay basis」購買產能 [Verified：SEC 文件]。
  - 截至 2025-12-31，「weighted-average contract duration of approximately five years」；RPO（剩餘履約義務）$60.7B [Verified]。
  - 10-K 摘錄**沒有明寫「固定價格」**。
  - 風險揭露提到「inability to redeploy components … to extend past their contracted life」。
  - URL：https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm
- **Intrator（CoreWeave 執行長），Q4'25 法說（2026-02-26）**：
  - 巨頭以五年期購買，鎖定「at a fixed price for five years」。
  - 合約平均年限從約 4 年延長到約 5 年。
  - [Interested-party：CoreWeave，需支撐以合約擔保的舉債與估值，誘因是強調合約穩定]
- **Q2'26 法說（2026-08-11）**：
  - Agrawal（CFO）：「a typical five-year contract carries strong and still expanding unit economics across its term」。
  - 2026 年 7 月牌價「approximately 25% increase across SKUs」。
  - Intrator：企業客戶偏好 2–3 年期合約。
  - 2026-03 投資人簡報：近期大型合約 5–6 年。
  - [Interested-party]
- **Nebius–Microsoft**：$17.4–19.4B，2026 年開始放量。6-K 的股東信**沒有揭露年期、單價與是否固定價**。新聞稱為五年期，本文未取得原文確認。[Interested-party / 搜尋未得細節]
- **Oracle**：FY2026 10-K 摘錄中搜尋**未得** RPO 年期與定價條款。

**判讀**：合約產能在合約期內的 L 接近 1，有第一手 take-or-pay 文件與管理層「固定價」說法支撐。但這是**收入的 L**，不是市場價格的 L。風險在於交易對手信用與續約時的價格。

---

## 2. 服役年限與降級（T1、ρ）

| 證據 | 內容 | 日期 | 標籤 |
|---|---|---|---|
| CoreWeave H100 續約 | 「first 10,000-plus H100 contract approaching expiration … re-contracted … at a price within 5% of the original agreement」，提前兩季續約 | Q3'25 法說（2025-11） | [Interested-party：CoreWeave] |
| 同上，CNBC 版本 | 「以原價 95% 續租」 | 2025-11 | [Interested-party] |
| CoreWeave H100 價格 | 「Average H100 pricing in Q4 was within 10% of where it started the year」 | 2026-02-26 | [Interested-party] |
| CoreWeave A100 新約 | 「recently signed an A100 contract that extends into 2029 at an attractive price」（A100 2020 年上市，屆時約 9 年）。客戶、單價、數量皆未揭露 | 2026-08-11 | [Interested-party：CoreWeave] |
| CoreWeave 舊世代價格 | 「pricing for prior generation SKUs is at or above where it was years ago」；「largely sold out of prior generations」；但續約量只占「limited portion」 | 2026-08-11 | [Interested-party] |
| Nvidia（Kress，CFO） | 「the A100 GPUs we shipped six years ago are still running at full utilization today」 | Q3 FY26 法說，2025-11-19 | [Interested-party：Nvidia，賣新卡；強調耐用可降低客戶疑慮] |
| Google（Vahdat） | 「seven and eight-year-old TPUs have 100 percent utilization」 | 2025-10，DCD 報導 | [Interested-party：Google]；TPU 屬 [Analogy] |
| Microsoft（Nadella） | 「I didn't want to go get stuck with four or five years of depreciation on one generation」：Nvidia 換代加速，刻意分散世代 | 2025-11（Dwarkesh 訪談） | [Interested-party]：隱含**單一世代的經濟主力期 < 4–5 年** |
| 匿名 Google 架構師 | 資料中心 GPU 服役 1–3 年 | 2024（Tom's Hardware 轉引） | [Analogy]，未具名，弱證據 |
| 前沿訓練世代更替 | A100（2020）→ H100（2023）→ GB200（2025–26）：前沿訓練的主力期約 2.5–3 年 | 產業常識 | [Derived] |

**ρ 的觀測值**（降級後價值比；[Derived]，屬於市場緊俏期的觀測）：
- A100 / H100 現價比：flopper $1.59 / 約 $2.9 ≈ **0.55**；UOB $1.61 / $2.65 ≈ **0.61**。
- AWS A100 第 5.6 年牌價 / 上市牌價：$2.74 / $4.10 = **0.67**。

注意：2026 年電力受限、供不應求，舊卡價格被墊高。在 2024 年底到 2025 年的供過於求期，ρ 可能明顯較低，但該期間的 A100 序列搜尋未得。

---

## 3. 折舊年限政策（伺服器／網通設備）

| 公司 | 歷程 | 現況 | 標籤／來源 |
|---|---|---|---|
| MSFT | FY2023（2022-07 宣布）4→6 年，FY23 營業利益 +約 $3.7B | FY2026 10-K：「two to six years」；2026-07 另將資料中心建物 15→25 年（非伺服器） | [Verified]：10-K，經 Hudson Labs、gpuinsights 轉述 |
| GOOGL | 2023 伺服器 4→6 年，FY23 折舊 −$3.9B | FY2025 10-K：「generally over six years」 | [Verified] 同上 |
| META | 2025-01-01 延長至 5.5 年，2025 折舊 −約 $2.9B | FY2025 10-K 維持 5.5 年 | [Verified]：Meta Q4'24 附件 |
| AMZN | 2022 伺服器 4→5 年（−$3.6B D&A）；2024 5→6 年（−$3.2B）；**2025-01-01 部分伺服器 6→5 年**（+$1.4B D&A），另 2024 Q4 加速折舊約 $920M；理由：「increased pace of technology development, particularly in … AI and ML」 | FY2025 10-K 維持 | [Verified]：10-K，經 Hudson Labs 轉述 |
| ORCL | 歷史變更搜尋未得 | FY2026 10-K（2026-05-31）：「servers and networking equipment with estimated useful life of six years」 | [Verified]：edgar.tools |
| CRWV | 2023-01-01 由 5→6 年 | FY2025 10-K：technology equipment 6 年 | [Verified]：gpuinsights 轉引 10-K |
| NBIS / Lambda | 4 年 / 5 年 | — | [Analogy]：beancount.io 二手，未經 SEC 原文確認 |

2026 年有無新的伺服器年限變更：已搜尋 MSFT FY26 10-K、META/GOOGL/AMZN FY25 10-K，**未見**變更。

**批評**：Michael Burry（2025-11-10，X 貼文）
- 估計 2026–2028 年巨頭少提折舊約 **$176B**；認為經濟壽命 2–3 年，會計假設 5–6 年。
- 估 2028 年 Oracle 利潤高估約 27%、Meta 約 21%。
- [Interested-party：Burry 公開做空 AI 相關標的，誘因是強調高估]
- 反方論據為上述 CoreWeave、Nvidia、Google 的說法，但同樣是利害關係方。

---

## 4. 交叉驗證（每個「合理」判斷都對照反證）

1. **「g ≈ −10%/年合理」**
   - 市場隨需價 3.3 年 CAGR −9% ~ −14% 支持。
   - 反證：AWS 牌價 −17.6%/年；2024–25 低谷期約 −40%/年。
   - 化解：路徑**不是單調下降，而是循環**（先崩 40–60%、後反彈 40%）。同一個平均 g 可以對應很不同的 6 年 L。單一常數 g 會低估波動風險，但長期平均落在 −10% ~ −15%。
2. **「T1 = 4 年」**
   - 前沿訓練主力期約 2.5–3 年（Nadella 的說法與世代更替都指向 < 4 年）。
   - 但「推論／中階主力」的收入期，A100 已達 6 年以上，並有合約到 2029 年。
   - 化解：若 T1 定義為「維持中階價格的年數」，3–4 年合理；若定義為「仍有可觀收入」，則遠超過 4 年，此時 ρ 才是關鍵。
3. **「ρ = 0.5」**
   - 2026 年觀測 0.55–0.67，略高於假設。
   - 反證：觀測點落在供給受限的高峰期；在供過於求期，ρ 可能低於 0.5（缺 A100 2024–25 序列，未能驗證）。
4. **「L = 0.643 < 0.756」**
   - H100 推算 L：AWS 牌價 0.64–0.70；市場價 0.54–0.80（依基準與尾段情境而定）；合約產能約 0.99；A100 AWS 牌價 0.92。
   - 結論：0.643 落在 H100 現貨市場推算區間的中段，並不離譜。但**機隊中長約占比越高，有效 L 越接近 1**。CoreWeave 這類 take-or-pay 業者的 L 應拆成「合約期 L ≈ 1」與「續約／殘值 L」兩段，不宜用單一現貨 L。

---

## 5. 總表

| 項目 | 數值 | 日期 | 來源 URL | 標籤 | 對 g / T1 / ρ / L 的含義 |
|---|---|---|---|---|---|
| AWS P5 H100 隨需降價 | −44%（3 年 SP −45%） | 2025-06-01 | https://aws.amazon.com/blogs/aws/announcing-up-to-45-price-reduction-for-amazon-ec2-nvidia-gpu-accelerated-instances/ | Verified | 巨頭牌價 g ≈ −17.6%/年 |
| AWS P4d A100 隨需降價 | −33% | 2025-06-01 | 同上 | Verified | A100 牌價 g ≈ −6.6%/年；L（6 年）≈ 0.92 |
| AWS P5 上市價 | 約 $12.29/GPU（$98.3/節點）；3 年合約約 $5.37 | 2023-07 | https://www.nextplatform.com/2023/07/27/h100-gpu-instance-pricing-on-aws-grin-and-bear-it | Derived | 年 0 基準；L（AWS H100）0.64–0.70 |
| H100 1 年合約價 | $1.70 → $2.35（+38%） | 2025-10 → 2026-03 | https://cryptobriefing.com/nvidia-h100-gpu-rental-costs-surge/ | Interested-party（SemiAnalysis），方向有 Silicon Data 佐證 | 路徑循環；g 非常數 |
| Silicon Data H100 分通路中位數 | 巨頭 7.76 → 6.26；新雲 2.99 → 3.33；租賃平台 2.58 → 1.95 | 2023H2 → 2025H2 | https://www.silicondata.com/blog/h100-rental-price-over-time | Interested-party（指數業者） | 通路差異大；新雲價格未跌 |
| H100 隨需中位數 | 約 $3.39，年增 +11% | 2026-09 | https://akash.network/the-bid/h100-rental-price-2026-cost-per-hour/ | Analogy | 第 4 年相對值約 0.79（以 $3.8 為基準） |
| A100 隨需中位數 | $1.59（預留 $1.63） | 2026-10-17 | https://flopper.io/pricing/nvidia-a100 | Analogy | ρ ≈ 0.55（相對 H100） |
| A100 / H100 / B200 | $1.61 / $2.65 / $5.42 | 2026-06 | https://www.uob.com.sg/assets/web-resources/private/pdfs/compute-is-revenue.pdf | Analogy | ρ ≈ 0.61 |
| B200 Lambda 隨需 | $5.50 → $6.79 | 2026-04 → 2026-10 | https://www.morphllm.com/nvidia-b200 ; https://siliconanalysts.com/market-data/gpu-rental-price-per-tflop | Analogy | 新世代初期 g 為正，不是 −10% |
| CoreWeave H100 續約 | 原價 5% 以內（約 95%） | 2025-11 | https://www.marketscreener.com/news/coreweave-third-quarter-2025-earnings-conference-call-transcript-ce7d5fd8d08ff220 | Interested-party（CRWV） | 續約 ρ 約 0.95；支持較高 L |
| CoreWeave 合約年期 | 加權平均約 5 年，take-or-pay，RPO $60.7B | 2025-12-31 | https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm | Verified | 合約期 L ≈ 1 |
| Intrator：五年固定價 | 「fixed price for five years」 | 2026-02-26 | https://gloom.sh/stocks/crwv/transcripts/q4-2025 | Interested-party | 合約產能 L ≈ 0.99 |
| CoreWeave A100 合約至 2029 | 「attractive price」；舊世代價格「at or above」數年前；7 月牌價 +25% | 2026-08-11 | https://www.investing.com/news/transcripts/earnings-call-transcript-coreweave-tops-q2-2026-estimates-shares-jump-135-93CH-4852937 | Interested-party | 收入期 > 6 年；T1（收入定義）> 4 |
| Nvidia：A100 滿載 | 「six years ago … full utilization」 | 2025-11-19 | https://www.rev.com/transcripts/nvidia-q3-2026-earnings-conference-call | Interested-party（NVDA） | 支持長服役；但滿載不等於價格維持 |
| Google：舊 TPU 滿載 | 7–8 年前的 TPU 100% 使用率 | 2025-10 | https://datacenterdynamics.com/en/news/google-says-tpu-demand-is-outstripping-supply-claims-8yr-old-hardware-iterations-have-100-utilization | Interested-party / Analogy | 同上 |
| Nadella | 不想被單一世代 4–5 年折舊綁住 | 2025-11 | https://davefriedman.substack.com/p/the-176-billion-accounting-question | Interested-party | 前沿主力期 < 4–5 年，T1 偏 3 |
| AMZN 年限縮短 | 部分伺服器 6→5 年，D&A +$1.4B | 2025-01-01 | https://www.hudson-labs.com/research/amazon-server-depreciation-amzn | Verified | 會計端承認技術加速；T1 偏短 |
| META 年限延長 | 5.5 年，折舊 −$2.9B | 2025-01-01 | https://platformonomics.com/2025/01/platformonomics-tgif-78-january-31-2025/ | Verified | 與 AMZN 方向相反；會計年限不等於經濟年限 |
| MSFT / GOOGL / ORCL / CRWV | 2–6 / 6 / 6 / 6 年 | FY2025–26 | https://gpuinsights.net/server-useful-life-gpu-depreciation-2026/ ; https://app.edgar.tools/companies/ORCL/disclosures/property-plant-equipment | Verified | T = 6 與業界會計一致 |
| Burry 批評 | 2026–28 年少提折舊約 $176B；經濟壽命 2–3 年 | 2025-11-10 | https://techstrong.ai/features/tech-investor-michael-burry-alleges-accounting-irregularities-at-hyperscalers-in-pursuit-of-ai-boom/ | Interested-party（放空者） | 下緣情境：T1 約 2–3、ρ 偏低 |
| Ornn H100 指數 | 公開網頁無歷史數值（Bloomberg ORNNH100） | 2026-03 | https://theinnermostloop.substack.com/p/the-first-tradable-compute-price | 搜尋未得（非不存在） | 建議用 Bloomberg 補第三方序列 |
| H100 推算 L | 現貨 0.54–0.80；AWS 牌價 0.64–0.70；合約約 0.99 | 2026-10 | 本文 §0.4 | Derived | 0.643 在現貨區間中段；機隊混合 L 取決於長約占比 |

---

## 摘要（≤300 字）

H100 市場隨需價 2023–2026 年的 CAGR 約 −9% ~ −14%，與 g = −10% 相符。但路徑是循環的：2024–25 年先崩 40–60%，2025-10 到 2026-03 合約價反彈 +38%（SemiAnalysis，Silicon Data 佐證方向）。巨頭牌價則是階梯式：AWS H100 −44%，推算 g 約 −17.6%/年；A100 牌價 g 約 −6.6%/年。B200 上市 1.5 年仍在漲價。

推算的 6 年 L：
- H100 現貨 0.54–0.80（依基準與尾段假設）
- AWS H100 牌價 0.64–0.70
- AWS A100 牌價 約 0.92
- 長約產能 約 0.99：CoreWeave 10-K 為 take-or-pay、加權約 5 年；管理層稱固定價，續約達原價約 95%，屬利害關係方說法。

服役年限：前沿訓練主力期約 2.5–3 年，Nadella 的說法也暗示 T1 < 4 年。但收入期遠長於此：A100 合約到 2029 年，Nvidia、Google 都稱舊卡滿載，同屬利害關係方。2026 年觀測的 ρ 約 0.55–0.67，但處於供給緊俏期，可能高估。

會計面：MSFT、GOOGL、ORCL、CRWV 為 6 年，META 為 5.5 年，AMZN 部分伺服器縮為 5 年。Burry 認為經濟壽命只有 2–3 年。

結論：0.643 對純現貨機隊並不離譜，但低於 0.756 的損益兩平門檻。實際的 L 取決於長約占比與續約價。建議把 L 拆成「合約期 ≈ 1」與「現貨／殘值」兩段，T1 下修到 3 年，並為 ρ 設定隨景氣循環變動的區間。

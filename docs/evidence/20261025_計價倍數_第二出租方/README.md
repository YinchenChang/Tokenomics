# 計價倍數的第二出租方錨點（A 段，唯讀查證）

分支 `claude/evidence-lessor-anchor2`　基準 master `3ac70ac`（CURRENT v21.4）　工作單 `docs/workorders/20261025_計價倍數第二出租方錨點.md`
檔案：`第二出租方錨點.xlsx`（審閱檔；換算全用公式，共 213 格；LibreOffice 重算錯誤 0；每家一頁＋彙總頁，CoreWeave 並排）、`證據原稿.md`、`script/build_xlsx.py`（產生審閱檔）。未改 `model/`、`builder/`、`tests/`。模式：LIGHT。
承接：CoreWeave 10-Q 錨點（PR #163）。TK 數值取自 v21.4（持有成本 Hopper 9.70／GB200 8.83／GB300 10.89／VR200 12.23 $B/GW·年）。
狀態：尚待未參與代理獨立核對。

## 結論先行

1. **比值依合約時點分成兩群，不是一個數字。**
   - **機隊平均（存量合約）：0.65–1.32。** 低於 1.8。
     - CoreWeave Q2 2026 為 0.76–1.28（PR #163）。
     - CoreWeave Q1 2026 為 0.83–1.32（新增點）。
     - Nebius Q4 2025 為 0.65–0.83。
     - WhiteFiber Q2 2026 為 0.86–0.95（偏上界）。
   - **2026 年新約的邊際價：1.84–2.30（÷GB300）。** 涵蓋 1.8。
     - 兩家互相獨立的公司各自揭露同一價位：Nebius Q2 四筆大單每 MW 年合約值 2,000–2,500 萬美元；IREN「近期 3 年約 >$20m per MW (IT)」、洽談中約 2,500 萬。
     - 若對 VR200 為 1.64–2.04。
     - WhiteFiber 的 Blackwell 新約（10-Q 揭露總值，再以 TK 密度換算）為 1.36–1.86。
   - **其他點：**
     - 短約（≤6 個月）：Nebius 4,000–5,000 萬美元，3.7–4.6。
     - 2025 年簽的長約：IREN–Microsoft 為 0.89。
     - Nebius 自報「2026 base」（存量合約平均）每 MW 1,200 萬美元：1.10–1.36。
   - **讀法：**
     - CoreWeave 錨點「約 1 倍」代表的是存量機隊的平均價。
     - 2026 年中起的新約價格約為 TK 持有成本的 2 倍。
     - `AL_SpendBasis` 1.8 落在新約區間的下緣，高於機隊平均。
     - 所以「1.8 偏高」只對以 2025 年及以前長約為主的支出成立，對 2026 年新增容量不成立。
     - OpenAI 2026 年的混合支出中新舊約各占多少，本段沒有資料，屬不可分離。
2. **年化讀法有檢查。** 新約單價若是合約總額而非年額，與兩家公司各自揭露的回本期不符：
   - Nebius 1 年 10 個月，隱含資本支出 33–42 $B/GW，對照 TK GB300 IT＋廠房 44.9。
   - IREN 約 2 年，隱含 GPU 資本支出 35–43，對照 TK IT 32.2。
   - Nebius 註 (1) 寫明 ACV＝「Annual contract value」。
   - 以上表示單價是年額。
3. **Nebius MW 定義（一手全文，20-F 與股東信）：**
   - contracted＝以已簽約土地與電力承諾取得的容量。
   - connected＝已接入（完整建成並配備的）資料中心的電力；2025 年的說明是「含 active，以及已配好電、裝上 GPU 即可啟用的容量」。
   - **active＝「capacity being consumed by IT equipment and available for revenue generation」。**
   - 結論：active 是 IT 側（設備端），不是設施或電網電力；但沒有寫「關鍵 IT 設計容量」或「實際耗電」。本段讀作可供營收的 IT 容量（Assumed）。若是實際耗電，比值再乘 0.7–0.9。
   - 與 CoreWeave 的可比性取決於 CoreWeave 的口徑（第 4 點，未定）：
     - CoreWeave 若是 IT 口徑，兩者可比；
     - 若是設施口徑，Nebius 的比值相對偏低約 1/PUE。
   - contracted 與 connected 都沒有寫 IT 或設施。
4. **CoreWeave J2：仍未找到定義。**
   - 已查：10-K FY2025 全文（active power 6 次，全為數字）、2026 Q1 10-Q（0 次）、三季 8-K 新聞稿、Q2 2026 法說逐字稿（二手轉載；「critical IT」「IT load」「PUE」0 次）。
   - 唯一相關的是 10-K 寫「與資料中心夥伴追蹤 PUE」。這說明電力在夥伴機房計量，但不是 active power 的定義。
   - Q1 2026 法說逐字稿在付費牆後，未讀。
5. **GB300 IT 單價與營運費用（只列）：**
   - **IT 資本支出（$B／IT GW）：** 公開點 29.0–44.0，TK 基準 32.2（28.6–39.3）。
     - IREN Dell 29.0（2025-11）；
     - Data Gravity 採購單只機架 33.8、部署後 38.4（2026-08）；
     - 媒體 40.6–44.0；
     - 由 IREN 回本期推算 34.8–43.5（Derived）。
     - 2026 年的點多數高於 TK 基準。
   - **營運費用（不含折舊，$B/GW·年）：** 公開點 1.6–3.3，TK 基準 1.98（1.21–3.00）。
     - IREN 直接成本率 13% × 新約單價＝2.6–3.3；
     - CoreWeave cost of revenue ÷ active GW＝2.8（含機房租金，不可直接比）；
     - Data Gravity 每架年營運換算 1.6–2.8。
     - 方向偏高，但口徑差異大。

## Facts & Data

### 各出租方（完整見 xlsx 各頁）

| 出租方 | 營收範圍 | 電力數字與口徑 | 季平均推法 | 機隊世代 | 每 GW 年營收（$B） | 比值 |
|---|---|---|---|---|---|---|
| CoreWeave Q2 2026 | 全公司營收（10-Q 稱軟體不重大）；Verified | 1.5 GW active（8-K）；口徑未定義 | 線性／6 月集中 | Hopper＋GB200 為主，GB300 開始 | IT 8.24–8.70；設施 9.9–11.3 | 0.76–1.28（÷GB200／GB300）；漲價後 0.95–1.60 |
| CoreWeave Q1 2026 | H1 − Q2＝20.78 億；Verified | 0.85（10-K「over 850 MW」）→ 1.0（8-K「Surpassed 1 GW」）；兩端皆為下限 | 線性 | 同上 | IT 8.99；PUE 1.3 為 11.7 | 0.83–1.32（÷Hopper／GB200／GB300） |
| Nebius Q4 2025 | core AI cloud（占集團約 94%）；股東信（Interested-party） | 年底 ~170 MW active（IT 設備耗用，公司定義）；9 月底未揭露 | (1) 12 月 ARR ÷ 年底 MW；(2) 9 月底依 ARR 比例 75 MW（Assumed）線性；(3) 9 月底取上界 100 MW | Hopper 為主，B200／GB200，B300／GB300 剛開始 | 6.35–7.35 | 0.65–0.83（÷Hopper／GB200）；若為實際耗電 0.46–0.75 |
| Nebius 合約 | ACV per MW（營收認列口徑，不含預付）；Interested-party | MW 未定義（以 IT 計；若為設施，比值 ×1.2–1.3） | 不適用 | 新約 Blackwell／Vera Rubin，2026 下半年至 2027 上線 | 2026 base 12；Q2 大單 20–25；短約 40–50 | 1.10–1.36；1.84–2.30；3.67–4.59（÷GB300） |
| IREN | AI cloud；機隊 MW 未揭露，只能做合約層 | 「MW (IT)」公司標明 | 不適用 | Microsoft 為 GB300；近期約為較早訂購的 GPU | Microsoft 9.70；近期 >20、洽談約 25 | 0.89；1.84–2.30（÷GB300） |
| WhiteFiber Q2 2026 | 雲端分部扣終止費 12.3＝11.5 百萬／季；Verified（10-Q） | 冰島 5.5 MW-IT 已簽約；亞特蘭大 MW 未揭露 → 偏上界 | 季營收 × 4 | H100／H200／B200 | 8.37 | 0.86–0.95（÷Hopper／GB200） |
| WhiteFiber 合約 | 10-Q 合約總值；GPU 數 ÷ TK 每 GW GPU 數（B300 以 GB300、B200 以 GB200 近似，Analogy） | 由 GPU 換算 IT | 不適用 | B300、GB200、VR200、B200、H100 | 8.8–20.3 | Blackwell 新約 1.36–1.86；VR200 1.49；B200／H100 續約 0.91–1.34 |

### 彙總（xlsx「彙總」頁）

| 組別 | 低 | 高 |
|---|---|---|
| 機隊平均（CoreWeave Q1／Q2、Nebius Q4；不含漲價、不含 WhiteFiber 上界） | 0.65 | 1.32 |
| 新約邊際（Nebius、IREN、WhiteFiber Blackwell；不含短約） | 1.36 | 2.30 |
| AL_SpendBasis | 1.8（0.85–2.3） | |

### 標記
- **Verified：** CoreWeave 營收（10-Q）；WhiteFiber 雲端營收、終止費與合約總值（10-Q）。
- **Interested-party：**
  - Nebius 季度營收、ARR、MW、ACV、回本期（股東信；誘因：支撐募資與股價，Q2 同時發 5 GW 目標）；
  - IREN 每 MW 單價、回本期、成本（新聞稿與法說；誘因同上，並在洽談新約）；
  - CoreWeave active power（8-K）。
- **Assumed：**
  - Nebius 9 月底 active MW 依 ARR 比例；
  - IREN 的 200 MW 全數對應 Microsoft 合約；
  - WhiteFiber 的「256 台伺服器」以每台 8 顆計；
  - PUE 1.2–1.3；
  - 新約 MW 以 IT 計（Nebius 未定義）。
- **Analogy：** WhiteFiber 合約的 GPU→GW 換算用 TK 密度；Data Gravity、媒體機架價。
- **Derived：** 所有比值、回本期隱含資本支出、IREN 隱含營運費用。

## Judgment（LIGHT）

- **Stance：** 出租方的計價倍數有明顯的合約時點結構。存量平均約 0.7–1.3；2026 年中起的新約約 1.8–2.3；短約更高。1.8 不是被推翻，而是只適用於 2026 年起的新增容量。
- **Confidence：**
  - 機隊平均：Medium。三家同向，但 MW 口徑與季平均都有假設。
  - 新約價：Medium–Low。兩家獨立、數字一致，但都是 Interested-party，且正在募資或洽約。
- **最強反向證據與處理：**
  1. **新約單價是公司自報的邊際價，可能挑最好的幾筆。** Nebius「四筆大單」、IREN「近期 3 年約」都不是全部新約平均。WhiteFiber 10-Q 揭露的是全部新約的總值，換算 1.36–1.86，略低於前兩家，可作為較中性的下緣。
  2. **新約 MW 口徑。**
     - IREN 寫明 IT，Nebius 未寫。
     - 若 Nebius 的 MW 是設施電力，IT 口徑的比值會更高（2.2–3.0），方向不利於「1.8 偏高」。
     - 若是實際耗電，則反向，但 Nebius 的 ACV per MW 與 active 定義不一定同口徑。
  3. **持有成本世代選擇。**
     - 新約若是 VR200，比值降為 1.64–2.04；
     - 若是 B300 HGX（成本低於 GB300 NVL72），比值會更高。
     - 本段以 GB300 為主、VR200 為敏感度。
  4. **Nebius 機隊平均偏低（0.65–0.83）可能來自上線爬坡：** 年底新上線的容量 12 月未全額計費，而且 2025 年的 Hopper 價格較低。這與 Nebius 自報「2026 base 12」（1.10–1.36）有落差：前者是 2025 Q4 的實際營收，後者是 2026 年存量合約的年額，兩者時點不同。
- **方向檢查（第 10 條）：**
  - 不利於「比值低於 1.8」的選擇 3 個：
    - Nebius 機隊比值採「可用容量」讀法，不採實際耗電（後者更低）；
    - 新約 MW 以 IT 計（若為設施則更高）；
    - 新約比值以 GB300 為主（若為 B300 HGX 則更高）。
  - 有利於「比值低於 1.8」的選擇 2 個：
    - CoreWeave 與 Nebius 的季平均都用線性（爬坡未計費會低估單價）；
    - WhiteFiber 機隊以冰島 MW 為分母（偏上界，但仍低於 1）。
  - 中性：新約單價取公司區間端點，不取中點。
  - 都沒有收窄 Andy 留下的選項。
- **覆蓋檢查（第 11 條）：**
  - [P] 出租方定價結構（存量／新約／短約、預付、期限）：已做。
  - [A] 恆等式「比值＝每 GW 年營收 ÷ TK 世代持有成本」；回本期檢查「回本 × (單價 − 營運費用)＝資本支出」：已做。
  - [I] 募資與股價誘因（Nebius、IREN）、第三方採購單（Data Gravity）：已標。
  - 未做：
    - Oracle OCI（無 GW 口徑，不可分離）；
    - Lambda、Crusoe（未上市、無 MW 揭露）；
    - OpenAI 自身新舊約占比（不可分離）。
- **判定性證據（Invalidation）：**
  - CoreWeave、Nebius 揭露季末 active MW 與其 IT／設施口徑；
  - OpenAI 或其供應商揭露 2026 年新簽容量的每 MW 價格；
  - IREN、Nebius 揭露全部新約平均（而非代表性大單）；
  - Nebius Q3 2026（11 月）的 active MW 與 ARR。
- **實務意涵：**
  - DB_Evidence 可記兩筆：
    - 「機隊平均 0.65–1.32（三家），弱反對 1.8」；
    - 「2026 新約 1.84–2.30（兩家）、WhiteFiber 1.36–1.86，支持 1.8 作為新增容量價」。
  - 1.8 的含義可改寫為「新舊約混合」。

## 已搜尋，未找到 ／ 不存在或不可分離

**已搜尋，未找到：**
- Nebius 2025-09-30、2026-03-31、2026-06-30 的 active MW 與 connected MW。已查 Q3 2025 至 Q2 2026 股東信、新聞稿、6-K 財報，Nasdaq、MarketBeat、blockspace 法說摘要，以及 Zhitongcaijing（webull）報導；法說逐字稿 ziven.io 付費牆。
- Nebius 新約 MW 的 IT／設施口徑。
- CoreWeave active power 的 IT／設施定義。已查 10-K、兩季 10-Q、三季新聞稿、Q2 法說；Q1 法說付費牆。
- IREN 營運中 AI cloud MW 與 GPU 數（FY26 新聞稿、簡報、Q4 法說）；Microsoft 合約的 GPU 數。
- WhiteFiber 亞特蘭大、巴黎、安大略的 MW。
- GB300 每架或每 GW 的公司揭露營運費用。

**不存在或不可分離：**
- IREN 機隊平均每 MW 營收：營運中 MW 未揭露。Horizon 1 驗收後 ARR 10 億美元中的舊機隊部分約 5 億，但沒有 MW。
- Oracle OCI：營收含非 GPU 業務，未揭露上線 GW。
- Lambda、Crusoe：未上市，無 MW 與雲端營收拆分（只有 Sacra 等第三方估計）。
- OpenAI 2026 年支出中的新約與舊約占比。
- Nebius Q2 2026 ARR 30 億美元：無對應 MW，不能換算。

## 待 Project 判斷（附預設）

| 編號 | 事項 | 建議預設 |
|---|---|---|
| L1 | `AL_SpendBasis` 1.8 | 不改值；DB_Evidence 記兩筆（機隊平均 0.65–1.32 弱反對；2026 新約 1.84–2.30 支持），說明改為「新舊約混合；機隊平均約 1，新約約 2」 |
| L2 | Nebius active power 口徑 | 視為 IT 側可用容量（與 TK IT GW 同口徑）；「實際耗電」讀法只作敏感度（× 0.7–0.9） |
| L3 | CoreWeave J2 | 維持「未定義」，比值保留 IT／設施兩算；下次 Q3 2026 10-Q／法說（11 月）再查 |
| L4 | 新約比值的分母世代 | 以 GB300 為基準、VR200 為敏感度（1.64–2.04） |
| L5 | GB300 IT 資本支出 32.2 是否偏低 | 不改；記錄 2026 年公開點 33.8–44.0 多數高於基準（Data Gravity 只機架即 33.8），列入下次 IF_CapexIT 檢討 |
| L6 | IREN 隱含營運費用 2.6–3.3 | 只記錄；直接成本率來自 Q4 FY26 混合機隊，不代表 GB300 穩態 |

## 下游要改的輸入（本段不改）
- **TK：**
  - DB_Evidence 新增兩筆（L1）；
  - `AL_SpendBasis` 說明文字（若 L1 照預設）；
  - Spec_Rack／IF_CapexIT 的對照列可加 Data Gravity 部署後 38.4 與 IREN 回本期推算（L5，不改值）。
- **CoreWeave 模型：** 新約價格倍數 k 可對照 2026 新約 1.84–2.30（現行模型對存量用約 1 倍）。7 月漲價 25% 與新約價方向一致。
- **Nebius 模型：**
  - MW 主口徑維持 IT（公司定義支持）。
  - 2026 存量合約平均每 MW 12（÷GB300 1.10）可作為存量 k 的對照。
  - 新約 20–25 可作為新增容量 k 的對照。
  - 2025 Q4 實際 7.0–7.35 可作為爬坡折減的對照。
- **MAG 模型：** k 若代表 2026 年新增容量的外租價，可對照 1.8–2.3；若代表存量平均，對照約 1。

## 本段限制
- 網頁多由工具摘述（標「摘述」）；SEC 原文為一手全文檢索。
- 比值以單一世代持有成本為分母；機隊實際為混合世代，所以給區間。
- 未登入付費牆；未使用 SemiAnalysis。

# Tokenomics 評估與改進建議（整合版）

2026-10-08 · Andy Chang（chat 端 Claude 整合三份評估：Claude 評估報告、Copilot 整體報告 v2.0、Copilot MW 收入報告）

> **版本脈絡（2026-10-08 推入 repo 時補記）**：本報告評估對象為 v5.25。推入時 master `70d859e` 的 `model/CURRENT` 為 v5.26（Interface 新增 DC_Cost 構件，純工程），另有 v5.27（J8 證據與 L1 外部對照；判斷類決定 X13）與 v5.28（網站同步）工作單待建置或合併。X13 (c) 已決定 Astra 規模與 Alloc k、N_major 基準不改，理由是研發端（L1_Ans3 對揭露支出 1/10）與服務端（token 路線對支出路線 1/14）同幅度偏小、絕對規模歸 OpenAI 模型校準。本報告 P0-1、P0-2 與 X13 的關係見「改進建議」表前的說明；本報告建議事項的實作工作單編為 v5.29（`docs/workorders/20261008_v5.29.md`）。

## 摘要與總評

三份報告的結論互補而不衝突：Copilot 整體報告回答「這個系統應該長成什麼樣」，Claude 報告回答「它現在哪裡有病」，Copilot MW 報告回答「下游該怎麼取數」。整合後的判斷：Tokenomics v5.25 的核心架構已成立，下一階段不是擴張，而是先處置兩個已記錄未結的數量級落差，再把已有的並列輸出收斂成一個正式的輸出契約供下游使用。

| 面向 | 整合後評等 | 依據（來源報告） |
| --- | --- | --- |
| 架構與定位 | 高 | 統一計量框架、治理鏈、L1／Interface 已成型（Copilot 整體） |
| 計算正確性 | 高 | 39,252 公式 0 錯誤格；Block 1／4 獨立重算誤差 <1%（Claude） |
| 內部一致性 | 中 | token 對帳落差 14 倍、Astra 規模落差 14.6 倍，兩者已登錄未處置（Claude；Copilot 整體只提 Astra） |
| 資料品質 | 中 | Active SRC 24% 為 3 級；213 筆利害關係方紀錄缺第二來源（Claude） |
| 下游可用性 | 中低 | 輸出無信心與用途標記（Copilot 整體）；下游自行把成本加成與市場價 50/50 平均，屬誤用（Copilot MW） |

三個最重要發現：

1. 物理層不是瓶頸，落差在實現層：Sol 每 GW 理論營收上限 $229B 對持有成本 $12.8B；但機隊層級的營收 ÷ 持有成本 3.8x 在利用率 × 生產折減 × L × m 同向移動時可降至 1 以下（損益兩平乘積 0.157，基準 0.60）。三份報告在這點一致：Theory Revenue 是上限，不是預測。
2. 兩個數量級落差必須在下游取數前處置：OpenAI 2025 需求推出的服務 GW（0.052）只有支出路線（0.74）的 7%；Astra 預訓練算力 6.8e25 對 Epoch 1.0e27。前者決定 IF_TokGW_ 在生產環境的可用性，後者連鎖到攤提與研發占比。
3. 每 MW 收入不應由成本加成與市場價平均：現行 11.62／17.40／24.20 的算術可重現，但混合了「供應商要求」與「市場願付」。補一個該報告沒有指出的點：保守情境的市場點（IREN–Microsoft $9.70M/MW）低於 Tokenomics 的 GB300 經濟持有成本 $12.72M/MW，比值 0.76；即以 Tokenomics 的成本基礎，該合約不覆蓋經濟成本。

P0 清單（下游 OpenAI v0.6／Nebius／Oracle 取數前完成）：

- P0-1 處置 token 對帳 14 倍落差，決定需求 D 與每 GW 產能各自的修正幅度。
- P0-2 結案 J8（Astra 規模），或正式採雙基準。
- P0-3 建立輸出契約：Interface／L1 每列加 Confidence、Decision Use、最近更新；現有 _Prod、_Life、IF_Util 收斂成一個四層瀑布，損益兩平乘積做成 L1 正式列。
- P0-4 每 MW 收入：停用 50/50 平均；Tokenomics 輸出成本底線與分層市場價，下游自行選定契約類型與價值捕獲率。

## 三份報告 PK

三份報告的分工不同，比較標準是「該報告的結論是否有證據、是否可執行、是否與工作簿現狀與 Andy 已做的決策一致」。

| 項目 | Copilot 整體報告（v2.0 校準版） | Claude 報告 | Copilot MW 收入報告 |
| --- | --- | --- | --- |
| 核心資問 | 系統應該是什麼、層次如何劃分 | 工作簿哪裡有錯、多弱 | 下游每 MW 收入該怎麼設 |
| 證據基礎 | 引用工作簿數字，未做獨立重算或治理統計 | 逐表統計、獨立重算、Gov_Map／SRC／Checks 全量讀取 | JSON 公式可重現；未與 Tokenomics 成本底線對帳 |
| 最強貢獻 | L0–L5 層級、輸出信心閘門（A／B／C）、負荷輸入註冊表、命題到參數介面 | token 對帳 14 倍落差、機隊損益兩平乘積、W1／3 級統計、營收構成 45% 來自輸入 token | 成本加成與市場價不同質、容量與單價情境軸必須分離、價值捕獲率 |
| 主要弱點 | 建議多為新建模組，未注意工作簿已有對應物（G8 邊界、_Prod／_Life 瀑布、Gov_Map P 欄）；成熟度評分為主觀值 | 未處理下游如何消費輸出；對定位與層次着墨少 | 未對帳成本底線；示範參數（q、p、c）無來源；對 CoreWeave 現狀的描述未驗證 |
| 與 Andy 既有決策的衝突 | P1-1「每成功任務成本升為主 KPI」與 L3／L4（harness 不入基準、不影響每 GW 營收）相抵；P1-2 價值分配、P2-1 公司映射超出 G8 邊界 | 無 | P0-4「滿產滿租 100%」須與 Tokenomics IF_Util 60% 口徑對齊，否則重複扣減 |
| 引用的數字正確性 | Rubin Ultra 2,705 架、$62.76B；Astra 14.6 倍——與工作簿一致 | 全部取自工作簿計算值並重算 | 路徑 A／B 六個數字全部重現（誤差 <0.1） |

採納與捨棄：

| 來源 | 建議 | 處理 | 理由 |
| --- | --- | --- | --- |
| Copilot 整體 | 三層系統邊界 | 採納，改為「把 G8 寫成輸出契約」 | 邊界已在 Decisions G8 決定，缺的是一頁可執行的契約 |
| Copilot 整體 | 輸出信心閘門 A／B／C | 採納，並改為公式 | 可由 Gov_Map 的「最弱輸入標記」與 SRC 等級自動算出，不必手填 |
| Copilot 整體 | 負荷輸入註冊表 | 採納，與 Claude P1-1（Stage 2 清單）合併 | 同一件事：Gov_Map 高段 Assumed／Analogy 50 格的集中頁 |
| Copilot 整體 | Theory Revenue 四層瀑布 | 採納，改為「收斂現有並列輸出」 | 層 1（2 已存在（100%、IF_Util、_Prod），層 3 部分存在（_Life 的 L、m），只缺整合與層 4 |
| Copilot 整體 | 命題到參數介面（Thesis_Map） | 採納，降為 P1 | L1 的 Ans1–Ans9 已是雛形；補反轉門檻欄即可 |
| Copilot 整體 | Benchmark 正規化層 | 採納，降為 P2 | SRC_Perf 已有平台、ISL、OSL、速度、MTP 欄；補軟體版本與 batch 即可 |
| Copilot 整體 | 每成功任務成本升為主 KPI | 捨棄（維持情境） | 與 L3／L4 決策相抵；成功率證據為 Assumed 或 3 級，升為主 KPI 會把最弱輸入放到最前 |
| Copilot 整體 | 產業價值分配模組、公司映射、回報歸因 | 移出 Tokenomics，屬 Project 層 | G8：公司特有逻輯屬下游；已有 OpenAI／CRWV／Nebius／Oracle 模型承接 |
| Copilot 整體 | 工作簿拆為 Evidence store／Calculation core／Reporting | 捨棄 | 與「Excel 為事實來源、Excel 優先」的已定工作方式相抵；repo 已是計算與測試層 |
| Copilot 整體 | 成熟度評分 3.8／5 | 捨棄 | 無可重現的評分依據；本報告改用可驗證的統計 |
| Claude | token 對帳落差、J8、損益兩平乘積、W1 高段先補、鏡像頁參數化 | 全部採納 | 均有工作簿內證據 |
| Copilot MW | 停用 50/50 平均；分離容量與單價情境軸；成本路徑改為損益兩平檢查 | 採納 | 經濟邏輯正確；與 Tokenomics「理論上限 vs 實現」的分層一致 |
| Copilot MW | 每 MW 收入＝產出 × 價格 × 捕獲率；中性情境持平 | 採納，但捕獲率留在下游 | 捕獲率依合約計價單位而異，是公司特有變數 |
| Copilot MW | q、p、c 示範參數（1.4／0.55／0.95 等） | 捨棄 | 無來源；報告自身也說明不應採用 |
| Copilot MW | 滿產滿租 100% 簽約率 | 採納，附條件 | 須與 IF_Util 60% 分工：IF_Util 是技術利用率，簽約率是商業變數，兩者都在時則重複扣減 |

## Facts & Data

所有數字除另注者外為 20261007_Tokenomics_v5.25.xlsx 的計算值 [Verified-工作簿]；外部對照值沿用工作簿 SRC 頁標記；MW 報告的市場價格為該報告轉述 [Interested-party／2 級]。

工作簿統計：56 張工作表、39,252 公式、31,654 常數格、0 錯誤格；Gov_Map 595 輸入格（Assumed 279、原始數據 178、Analogy 41；高敏感度段 123 格中 Assumed／Analogy 50）；SRC 296 筆（Active 276；1 級 127、2 級 82、3 級 67；利害關係方 222 筆中 213 筆缺第二來源）；DB_Evidence 170 筆；Checks ERROR 0、WARN 213、INFO 107。

關鍵數字（VR200 基準，GW＝IT 關鍵電力）：

| 指標 | 值 | 獨立重算 |
| --- | --- | --- |
| 每 GW 機架／GPU | 4,052／291,744 | 4,052／291,744 |
| 每 GW 資本支出 | $50.26B | $50.26B |
| 每 GW 年經濟持有成本 | $12.76B | $12.65B |
| $/GPU-hr 經濟（100% 時數） | $4.99 | $4.95 |
| Sol decode $/M（100%） | $0.344 | — |
| Sol 每 GW 理論營收（利用率 60%） | $228.8B（混合 $1.607/M） | $228.8B／$1.607 |
| 營收構成 | decode 55%、新鮮 prefill 40%、快取 5% | — |
| 機隊營收 ÷ 持有成本 | 3.82x | 損益兩平乘積 0.157 |
| OpenAI 2025 服務 GW：token 路線／支出路線 | 0.052／0.743 | 比值 0.07 |
| Astra 預訓練 FLOP 對 Epoch GPT-6 | 6.8e25／1.0e27 | 比值 0.068 |

每 MW 收入三情境（GB300，$M/MW-IT/年；MW 報告公式以 Tokenomics 輸入重算）：

| 情境 | 路徑 A 成本加成 | 路徑 B 市場價 | 50/50 平均 | 路徑 B ÷ 持有成本 12.72 | 市場點隱含 $/GPU-hr（100% 時數） |
| --- | --- | --- | --- | --- | --- |
| 保守 | 13.53 | 9.70（IREN–Microsoft 5 年約） | 11.62 | 0.76 | $2.27 |
| 基準 | 15.90 | 18.89（Verda $5.21 × 487 × 8,760 × 85%） | 17.40 | 1.49 | $4.43 |
| 積極 | 18.37 | 30.02（Verda 24 月預留 $7.82 × 90%） | 24.20 | 2.36 | $7.04 |

兩點對帳結果：（1）MW 報告六個數字全部重現，其中 487 GPU/MW 與 12.72 $M/MW 與 Tokenomics GB300 一致；（2）保守情境的市場點低於 Tokenomics 經濟持有成本 24%，對應 $2.27/GPU-hr 對 $2.98/GPU-hr；MW 報告未指出這點。可能解讀：IREN 的場址與電力成本低於 Tokenomics 的通用廠房假設（$12.67M/MW），或該合約含客戶預付與非收入條款，或該合約在經濟口徑下確實不回本。三者都是下游 Nebius／Oracle 模型應回答的問題，不是 Tokenomics 的。

## 評估結論

| 判定 | 項目 | 來源 |
| --- | --- | --- |
| Supported | Tokenomics 已建立統一計量框架與治理鏈，定位為「技術事實與投資判斷之間的轉譯層」 | Copilot 整體 |
| Supported | Block 1 成本鏈、Block 2 機制與 GB300 樣本外對照、Block 4 營收公式（獨立重算一致） | Claude |
| Supported | 單位算力價格隨世代下降（Luna decode 每 M token 成本 Hopper → VR200 下降 7 倍，全部來自每 GPU 產出提升 22 倍，每 GPU 小時成本反而上升 3.1 倍） | Claude |
| Supported | Theory Revenue 應保留為技術經濟上限，與實現收入分層 | 三份一致 |
| Supported | 成本加成路徑與市場價路徑不同質，50/50 平均無依據；容量與單價情境軸應分離 | Copilot MW |
| Contradicted | Astra 規模與前沿錨點（低 14.6 倍）；隱含家族研發計畫數 12.1 對合理 1–3 | Claude／Copilot 整體 |
| Contradicted | token 對帳與營收對帳不能同時成立；營收對帳的閉合屬循環驗證（K7 用同一組 OpenAI 2025 支出校準） | Claude |
| Contradicted | 每 MW 收入保守情境的市場點覆蓋經濟成本（實為 0.76） | 本報告新增 |
| Contradicted | 每成功任務成本可升為主 KPI（證據等級不足，與 L3／L4 相抵） | 對 Copilot 整體 P1-1 |
| Uncertain | 利用率 60%、生產折減 1.0、L、m（皆 Assumed 且負荷最重） | 三份一致 |
| Uncertain | RL ÷ 預訓練（外部錨點過舉）；GB300 ÷ GB200 產出比（三來源不一致）；Block 6 Q1 區間 47–92% | Claude |
| Uncertain | 新世代 token 產出提升有多少被供應商捕獲（依合約計價單位而異） | Copilot MW |

衝突調和：

- Copilot 整體評「成熟度中高、約 3.8／5」與 Claude 評「內部一致性中」不衝突：前者評架構，後者評數值。整合版不用評分，改用「架構已成立；兩個數量級落差未處置」。
- Copilot 整體認為「公司財務映射不完整不是扣分項」，Copilot MW 卻指出下游已經在誤用 Tokenomics 數字。兩者同時成立：不扣分，但輸出契約是 P0，因為誤用已發生。
- Copilot MW 建議「滿產滿租 100%」與 Tokenomics IF_Util 60%：兩者定義不同。IF_Util 是技術層（已上線容量在 SLO 下的平均負載），簽約率是商業層（容量是否已售出）。按 GPU-hour 或 MW-year 計價的神雲，收入只看簽約率，技術利用率歸客戶；按 token 計價的模型商，收入看技術利用率。輸出契約必須寫明這點。

方向統計：本整合做了 5 項歧義解決——每成功任務成本維持情境（保留 Andy 的 L3）；價值分配與公司映射移出 Tokenomics（保留 G8）；捕獲率留在下游（保留 G8）；token 對帳判為 Contradicted（縮窄：排除「只是需求低估」）；四層瀑布改為收斂現有輸出而非新建（縮窄：排除平行第二套）。保留 3、縮窄 2。

覆蓋統計：[P] 物理與 [A] 會計兩類在三份報告中都有檢驗；[I] 誘因類只有 Copilot MW 處理了「誰捕獲效能利益」，但沒有資料可檢驗；「價格由誰決定」（K2、K4）仍無人檢驗，屬沒有生成。

## 系統邊界與輸出契約

Copilot 的三層架構與工作簿已決的 G8 邊界一致；差別在於 G8 是一條決策，不是一份下游能照著做的契約。以下是對齊後的分層，每層註明現狀。

| 層 | 內容 | 持有者 | 現狀（v5.25） | 缺的東西 |
| --- | --- | --- | --- | --- |
| 核心 Tokenomics | 硬體、機架、電力、DC 成本；架構、SLO、KV、EP；推論、訓練、harness；每 GW 產能、每 M token 成本、每成功任務成本；產業級價格與需求資料 | Tokenomics 工作簿（G8） | Block 1–6、SRC_\* 已完整 | 輸出的信心與用途標記；損益兩平條件 |
| 產業經濟（跨公司） | 需求量、有效售價與下降速度、免費／付費、研發與服務配置、價值分配 | Tokenomics Block 4／6（以 OpenAI 為代理）+ Project 層 | Theory_Rev、Price_Frontier、Alloc 已有雛形；價值分配無 | 登錄「OpenAI 為代表性實驗室代理」的決策；價值分配留在 Project 層論述 |
| 公司與投資 | 產品組合、市占、合約計價、價值捕獲率、容量交付、WACC、收入、EPS、估值 | OpenAI／CRWV／Nebius／Oracle 等模型 | 各模型存在，取數方式不一 | 統一的取數規則（只取 IF_、L1_、SRC_ Active） |

輸出契約（建議為 Interface B 節新增欄位，由公式生成）：

| 欄位 | 定義 | 產生方式 |
| --- | --- | --- |
| Confidence | A：最弱輸入為 Verified／1 級；B：最弱輸入為 Analogy／Assumed 有區間；C：最弱輸入為 3 級或無區間 | 由 Gov_Map「CC 敏感度分段」與「SRC 等級」欄以公式徙出，不手填 |
| Decision Use | 該列可用於：基準輸入／情境與相對比較／探索；不得用於：點估計收入、EPS | 依 Confidence 映射；A 層也註「為上限」者禁止當預測 |
| 口徑 | 100%／IF_Util／生產折減／L × m 四層中的哪一層 | 現有 D／G／H 節合併成一個瀑布欄 |
| 最近更新／觸發條件 | 該列最弱輸入的 SRC 審查日；何種新證據應觸發重算 | 從 SRC「審查日」欄連結 |
| 利用率定義 | 技術利用率（IF_Util）與商業簽約率的分工：按 token 計價者用前者；按 GPU-hr／MW-year 計價者用後者，前者歸客戶 | README 與 Interface 頁首各一段 |

下游取數規則（寫入 Project 的資料契約文件）：

1. 只取 IF_、L1_ 具名範圍與 SRC_ Active 紀錄；DRV_、CAL_、B4_、CST_ 禁止連結。
2. 每 GW 產能必須同時取四層瀑布，不得只取 100% 層。
3. 公司特有變數（WACC、合約價、捕獲率、簽約率、交付進度）在下游覆寫，不回寫 Tokenomics。
4. 下游發現的產業級缺口（例如新的市場 GPU-hr 價格點）走 G2 流程進 DB_Evidence，不自行建表。

## 每 MW 收入設定

Copilot MW 報告的核心論點成立：成本加成是「供應商要求的價」，市場價是「客戶願付的價」，兩者平均沒有經濟意義。整合版接受其收入生成式與情境軸分離，但把它放回 Tokenomics 的分層裡：Tokenomics 負責成本底線與產業級價格資料，下游負責合約類型、捕獲率與簽約率。

| 情境 | 路徑 A 成本加成 | 路徑 B 市場價 | 持有成本底線 |
| --- | --- | --- | --- |
| 保守 | 13.53 | 9.70 | 12.72 |
| 基準 | 15.90 | 18.89 | 12.72 |
| 積極 | 18.37 | 30.02 | 12.72 |

（US$M / MW-IT / 年，GB300；路徑 A／B 依 Copilot MW 報告公式以 Tokenomics GB300 輸入重算；持有成本＝L1_HoldEconGW_GB300 ÷ 1000）

圖中保守情境的市場點（IREN–Microsoft，9.70）低於持有成本 24%，是 MW 報告未指出的發現：要麼該合約在經濟口徑下不回本，要麼 IREN 的廠房與電力成本遠低於 Tokenomics 的通用假設。兩種解讀對 Nebius／Oracle 模型的含意相反，下游必須指定。

收入生成式（採 MW 報告，註明每項的持有層）：

| 項 | 定義 | 持有層 | Tokenomics 現有對應 |
| --- | --- | --- | --- |
| 每 MW token 產出 | 依世代與層級，四層瀑布口徑 | Tokenomics | IF_TokGW_\*、_Prod |
| 每 token 實收價格 | 模型商牌價 × 折扣；或 GPU-hr／MW-year 合約價 | 產業級價格點屬 Tokenomics SRC_Price；合約價屬下游 | Cap_In A 節、SRC_PRC_001／002 |
| 價值捕獲率 | 新世代效能提升中供應商留住的比例；按 token 計價≈ 1，按 MW-year 計價≈ 0 | 下游 | 無；不應新建 |
| 簽約／可計費率 | 已上線容量已售出的比例 | 下游 | 無；與 IF_Util 分工見上節 |
| 成本底線 | 經濟持有成本 ÷ MW，依世代 | Tokenomics | L1_HoldEconGW_*、L1_GPUhr_* |

三情境的機制（採 MW 報告）：每 MW 收入乘數＝產出乘數 q × 價格乘數 p × 捕獲乘數 c。中性情境為 q × p ≈ 1（產出進步被降價抵銷，每 MW 收入持平），樂觀為 q × p > 1，保守為 q × p < 1。q 由 Tokenomics 跨世代產出比提供（VR200 ÷ GB300 Sol 基準 1.57，區間 0.92–2.05）；p 由 SRC_Price 的時間序列提供（K9 目前不入年降幅，需補）；c 由下游依合約計價單位設定。MW 報告的示範參數（1.40／0.55／0.95 等）無來源，不採用。

Tokenomics 應新增的介面（小、可在 v5.29 完成）：

1. L1_HoldEconMW_\*：每 MW-IT 年經濟持有成本（現有每 GW 值 ÷ 1,000，依世代），標註為損益兩平底線。
2. L1_TokMW_Gen_ratio：相鄰世代每 MW 產出比（Sol 基準，附區間），供下游做 q。
3. SRC_Price 新增分層欄位：隨需／預留／長約、合約期、客戶規模、可中斷性；三類價格不得混用（MW 報告 P1-3）。
4. 不輸出「每 MW 收入」本身：那是下游的 q × p × c 與簽約率的結果，放在 Tokenomics 會把公司變數帶進核心層。

下游模型的對應修正（採 MW 報告 P0／P3）：Nebius／Oracle 停用 50/50 平均，容量交付與單價改為兩個獨立情境軸；現行 11.62／17.40／24.20 降為舊版對照；CoreWeave 模型明確採固定機隊平均或接上單價情境；每個模型以 Tokenomics 持有成本做 ROIC 與資金缺口檢查。

## 改進建議（依優先順序）

排序標準：對下游取數正確性的影響 × 改實成本的倒數。P0 在下游開工前完成，P1 在 v5.29–v5.30，P2 為持續維護，P3 為下游模型的對應修正。「來源」欄標明該建議出自哪份報告；合併者列出兩者。

> **與 X13 的關係**：X13 (c) 把兩端落差的「絕對規模」歸給 OpenAI 模型，只在 L1 揭露落差（X13 (d)）。本報告接受這個分工，但把 P0-1、P0-2 改寫為「承接 X13」：（1）兩端落差合成單一 L1 規模係數列（研發端約 10、服務端約 14）並進輸出契約，下游以此校準；（2）若 OpenAI v0.6 校準後兩端係數不一致，差額才是 Tokenomics 須自行解釋的部分（每 GW 產能或每則提示 token 數）；（3）Astra 雙基準列（bottom-up 與 external-anchor 並列）仍建議新增，它是 X13 (d) 的延伸，且不改任何輸入值。

| 優先 | 建議 | 理由 | 做法 | 驗收標準 | 來源 |
| --- | --- | --- | --- | --- | --- |
| P0-1 | 處置 token 對帳落差（服務 GW 0.052 對 0.743） | 14 倍落差決定 IF_TokGW_ 在生產環境的可用性；目前只是 INFO | 分離三個來源：每則提示 token 數改用 OpenRouter（SRC_DEM_014–017）；改用 OpenAI 自揭每日 token；剩餘落差歸入實際利用率 × 生產折減，寫成 Serving C17／C18 的證據 | 落差縮至 ±50%，或 Decisions 登錄「不可分離」與下游用法限制 | Claude |
| P0-2 | 結案 J8（Astra 規模），正式採雙基準 | 低 14.6 倍；連鎖到 K6 縮放 8.2、隱含計畫數 12.1、Alloc J8 落差 | Astra 保留 bottom-up（架構 × token）與 external-anchor（Epoch 1.0e27）兩列；差額拆為最終訓練、後訓練、實驗、合成資料、評測，無法橋接者標 Unknown；下游預設取 external-anchor | 隱含計畫數落在 1–3；L1_PretrainFLOP_Astra 兩列並列 | Claude + Copilot 整體 P1-5 |
| P0-3 | 輸出契約：Confidence、Decision Use、口徑、最近更新 | 下游已發生誤用（50/50 平均）；現有並列輸出散在 D／G／H 節 | Interface B 節加四欄，全部由 Gov_Map 與 SRC 公式徙出；100%／IF_Util／_Prod／_Life 合併為一個四層瀑布欄；新增 L1_FleetBreakeven（持有成本 ÷ 機隊 100% 營收，基準 0.157）與 L1_FleetMargin（基準乘積 ÷ 損益兩平） | 下游不讀公式即知每列可用於什麼；X1／X7 檢查仍為 0 | Copilot 整體 P0-4／P1-3 + Claude P0-3 |
| P0-4 | 每 MW 收入：停用 50/51；Tokenomics 輸出成本底線與分層價格 | 成本加成與市場價不同質；保守市場點低於成本底線 24% | 新增 L1_HoldEconMW_\*、L1_TokMW_Gen_ratio；SRC_Price 加隨需／預留／長約分層欄；Tokenomics 不輸出每 MW 收入 | Nebius／Oracle 只從這三項取數；舊值 11.62／17.40／24.20 降為對照 | Copilot MW P0／P1 + 本報告 |
| P1-1 | 負荷輸入註冊表（即 Stage 2 清單） | 高段 Assumed／Analogy 50 格散在 Gov_Map，無從追蹤 | 新增 Load_Bearing 頁：參數、區間、標記、影響的輸出與命題、反轉門檻、更新日、觸發條件；由公式從 Gov_Map 篩選；第一批：η_d、利用率、生產折減、ISL／OSL、χ、資產年限、L、m、Astra FLOPs、研發倍數、每則提示 token | 列數＝Gov_Map 高段 Assumed+Analogy 格數；每版結案數可讀 | Copilot 整體 P0-3 + Claude P1-1 |
| P1-2 | W1 第二來源先補高段；44 筆「一手未讀」清零 | 213 筆不可能一次補齊；未讀的一手等同二手 | W1 依敏感度分段計數，高段升 ERROR 的日期寫入 Decisions；逐筆開原文，讀不到者降 2 級 | 高段 W1 歸零；「一手未讀」歸零 | Claude |
| P1-3 | 命題到參數介面（Thesis_Map） | L1_Ans1–Ans9 已是雛形，缺反轉門檻與最強反方 | L1 問題列加三欄：反轉門檻（公式）、最強反方證據（SRC_ID）、監控指標；先做 VR200 vs GB300（損益兩平 η_d）與機隊損益兩平兩條 | 管理層問題可由 L1 進入輸入與門檻 | Copilot 整體 P0-2 |
| P1-4 | 更新過舉外部錨點；對帳判讀尺度統一 | RL ÷ 預訓練對照為 R1 2025-01；Checks 與 L1 判讀尺度不同 | 以 2026 揭露取代 SRC_MOD_034；L1 判讀改為「區間內／外 × 對照方立場」兩軸 | I3 列數重算並註明歸類 | Claude |
| P1-5 | 營收構成透明化；K9 加價格時間序列 | 理論毛利率 95% 的 45% 來自輸入 token；下游 q × p 需要 p | Theory_Rev A 節加新鮮 prefill／快取／decode 三列；SRC_Price 對同層級價格保留歷史快照，K9 輸出年降幅作為情境值 | 三列合計等於 IF_RevGW_\*；L1 有「同層級年降幅」列 | Claude + Copilot MW |
| P2-1 | 鏡像頁參數化 | 8 張 _Prod 頁 4,220 個公式只為一個參數；X1 抓不到「兩邊都改錯」 | Serving C18 改為基準／生產兩欄，第 50 列用 CHOOSE；或全由 builder 生成 | 鏡像頁手維公式歸零 | Claude |
| P2-2 | Benchmark 正規化欄位補齊 | SRC_Perf 已有平台、ISL、OSL、速度、MTP，缺軟體版本、batch、提交者 | 補三欄；條件不足者只作方向證據、不算世代倍數 | 每筆 SRC_Perf 欄位齊全或標「方向」 | Copilot 整體 P1-4 |
| P2-3 | I8 標記變更 53 格清零；README 版本日誌移出；Sources_Legacy 退役；Block 6 與 G8 邊界登錄 | 累積的工程待辦 | 一次性審閱；README 只留當前版本；確認對應後刪除；Decisions 加「OpenAI 為代表性實驗室代理」 | I8 歸零；B5 <300 字；工作表 −12 | Claude |
| P2-4 | 每成功任務成本：維持情境，補中立證據後再議 | 與 L3／L4 一致；成功率證據為 Assumed 或 3 級 | 只收 METR／ARC／AA 同條件實測；非 GPU 成本（沙箱、verifier）列待辦 | 成功率格的 3 級占比下降 | 對 Copilot 整體 P1-1 的改寫 |
| P3-1 | Nebius／Oracle：容量與單價兩個獨立情境軸；成本路徑改為 ROIC 與資金缺口檢查 | 單一選擇器同向綁定會雙重放大 | 情境矩陣；顯示市場收入低於經濟成本的年度與累計缺口；稀缺溢價設為可衰減變數 | 新舊版並行一版，提供目標價與缺口差異橋接 | Copilot MW P0／P2／P3 |
| P3-2 | 回答「IREN–Microsoft 為何低於成本底線」 | 決定保守情境的含意是「不回本」還是「成本結構不同」 | 在 Nebius／Oracle 模型中對該合約做成本對帳（場址、電價、預付、非收入條款）；結論進 DB_Evidence | 比值 0.76 有歸因 | 本報告新增 |
| P3-3 | CoreWeave 模型明確採固定機隊平均或接上單價情境 | 現狀未與情境選擇器連動（MW 報告陳述，本報告未驗證） | 先驗證現狀，再二擇一 | Decisions 登錄 | Copilot MW P3 |

不建議做的事：（1）把 L、m、生產折減改進基準——理論上限的定義是對的，實際值屬下游；（2）在 P0 未解前擴充 Block 5／6；（3）在 Tokenomics 內建價值分配、公司映射、回報歸因模組——屬 Project 層與下游模型；（4）把工作簿拆成多個系統——與 Excel 優先的工作方式相抵，repo 已承擔計算與測試。

## 追加考量（Andy 2026-10-08 提出三點）

三點核對結果：Astra 衝突已在 P0-2；harness 只納入一半，工作簿數字支持 Andy 的說法，升為 P1；自動更新排程未納入，新增 P1-6。

### Astra 訓練規模（已納入，P0-2）

模型 6.842e25 FLOP 對 Epoch GPT-6 Astra 1.0001e27 FLOP，比值 14.6 倍。處置維持 P0-2：bottom-up 與 external-anchor 兩列並列，差額拆為最終訓練、後訓練、實驗、合成資料、評測，無法橋接者標 Unknown，下游預設取 external-anchor。連鎖影響：K6 縮放倍數 8.2、隱含家族計畫數 12.1、Alloc J8 落差 0.82，三者同源，結案 J8 後應一併回到 1–3 與接近 1。

### Harness 與每成功任務成本（升為 P1-7）

工作簿已同時建模兩條路徑：參數組降低 token（輪數、思考保留、快取命中、子代理），METR 型成功率 p 乘上 harness 時間範圍倍數；每成功任務成本＝每次嘗試 ÷ p。工作簿自己的數字支持「harness 改善可能大於硬體世代」：

| 比較（Coding agent，Sol） | 值 | 來源 |
| --- | --- | --- |
| 選定 harness ÷ 標準 harness，每成功任務成本（VR200） | 0.48 | L1_Ans8 |
| VR200 ÷ GB300，decode 每 M token 成本 | 0.61 | Sens_Perf L 節 |
| Sens_Har Astra R 最小～最大 | 0.36–0.77 | Checks Block 5 |
| ARC 重現：token 比、成本比（中立方） | 0.49 對 0.51；0.52 對 0.42 | S58 |

即 harness 在基準下改善 52%，一個硬體世代改善 39%，且 harness 區間內無一情境超過 1。原報告把它留在 P2「維持情境」的理由（成功率證據多為 Assumed 或 3 級）只支持「不入基準」，不支持「不正式輸出」。修正為 P1-7：

1. 新增 L1_HarVsGen＝（選定 harness ÷ 標準）÷（VR200 ÷ GB300），依任務分列，附區間；<1 即 harness 改善大於世代改善。
2. harness 成功率倍數與 token 參數組列入負荷輸入註冊表，反轉門檻＝使 L1_HarVsGen ≥ 1 的成功率倍數。
3. 基準仍維持 L3（w＝0）、L4（不影響每 GW 營收）；升入基準的條件寫成決策：至少兩個中立方同條件實測（L7）且跨任務方向一致。
4. 非 GPU 成本（沙箱、verifier、工具呼叫）仍列待辦（L6），但在 L1_HarVsGen 註明「未含」，因為它只會讋 harness 的改善變小。

### 自動更新排程（新增 P1-6）

原則：自動化只做「搜尋、登錄、比對、提案」，不做「寫入 SRC」——與 G2（比較判定屬判斷類）、G6（A 級不自動取代）一致。每次執行的產出是 DB_Evidence 候選列（狀態「待判定」）與一份比較摘要，不是新版工作簿。

分區分類的週期：

| 分區 | 週期 | 搜尋對象 | 觸發標準 |
| --- | --- | --- | --- |
| SRC_Price | 每月 | Cap_In F 節 13 個模型的牌價；CoreWeave／Verda 等 GPU-hr 隨需與預留僷；新公布的長約每 MW 實收 | 任一價格變動 >10%，或前緣模型更換 |
| SRC_Perf | 季或事件 | MLPerf Inference 新輪、InferenceX 更新、廠商發布的 tok/s/GPU | 新一手結果落在現有區間外 |
| SRC_HW／SRC_DC | 季 | 機架價、功率、HBM；每 MW 廠房資本支出；VR200 量產規格 | 新世代出貨或報價更新 |
| SRC_Model | 事件 | 新旗艦發布的架構、訓練 token、RL 規模揭露；Epoch 更新 | 影響 J8、J9、T10 者 |
| SRC_Demand | 季 | OpenAI／Anthropic 自揭每日 token、ARR、推論支出；OpenRouter | 影響 P0-1 token 對帳者 |
| SRC_Harness／SRC_Cap | 季 | METR、ARC、AA 指數新版 | 影響 L1_Ans8／K3 者 |
| 低信心清單 | 每月 | SRC 中 3 級 Active（67 筆）、W1 高段缺第二來源、I7 尚無 SRC 紀錄（3 格）、審查日超過 90 天者 | 找到第二來源或一手原文即登錄 |

每次執行的步驟：

1. 從 repo 取 model/CURRENT 指向的 Excel，讀 SRC_\* 的 Active 紀錄、等級、審查日、第二來源欄，與 Gov_Map 的高段清單，產生本次搜尋清單（依上表分區與週期）。
2. 逐筆網路搜尋；只接受能開到原文的來源，記錄日期、口徑、立場。
3. 與現有 Active 值比對（G4 順序：等級 → 立場 → 口徑 → 日期），寫入 DB_Evidence 候選（E 編號續號，狀態待判定）；落在區間外的一級中立證據標「待 Andy」（G6）。
4. 產出：DB_Evidence 候選 CSV、比較摘要（哪些 L1 列會受影響、方向與幅度）、建議的工作單草稿；推到 repo 的 docs/evidence/《YYYYMMDD》並通知。
5. 判定與寫入 SRC 留在 chat；工程類（附加 SRC 列、重算、Checks）由 Claude Code 執行。

實作選項：（a）Claude 排程任務（雲端，每月一次全區，季度分區由同一任務依月份判斷）；（b）GitHub Actions cron 只做機械檢查（審查日過期清單、parity、GOV_Errors），不做網路判斷。建議 (a)+(b) 並行：(b) 產生清單，(a) 消費清單。驗收標準：連續三次執行後，3 級 Active 筆數與高段 W1 筆數單調下降，且無一筆 SRC 由自動任動直接寫入。

## 執行路線

順序原則：先處置會改變下游取數的落差，再建契約，再補資料；下游模型在契約完成後才改取數。每個版本一份工作單，判斷類在 chat、工程類由 Claude Code 在 repo 執行（P4）。

| 版本／階段 | 內容 | 屬性 | 完成定義 |
| --- | --- | --- | --- |
| v5.29 | P0-1 token 對帳、P0-2 Astra 雙基準、P2-3 的 G8 邊界登錄 | 判斷類 | 兩個落差有歸因與 Decisions 登錄；Checks ERROR 0 |
| v5.30 | P0-3 輸出契約（四欄 + 四層瀑布 + 損益兩平列）、P0-4 每 MW 介面、P1-1 Load_Bearing 頁 | 工程類為主 | 下游可只讀 Interface B 節取數；L1 新列均為即時公式 |
| Project 資料契約文件 | 下游取數規則四條、利用率與簽約率分工、每 MW 收入生成式 | 文件 | 放入 Project 一頁契約，各模型 handoff 引用 |
| Nebius／Oracle v+1 | P3-1、P3-2 | 下游 | 新舊版並行，差異橋接完成 |
| OpenAI v0.6 | 從 v5.30 Interface 取數，四層瀑布全取 | 下游 | 不再自建 roofline（D8） |
| v5.31 起 | P1-2、P1-3、P1-4、P1-5、P2-1、P2-2 | 持續 | 每版工作單記錄結案數 |
| 每月／事件觸發 | 證據更新、W1 追蹤、網站 parity | 維運 | 新證據能指出受影響的 L1 列 |

全案成功判準（採 Copilot 整體，精簡為可觀測者）：任一重要結論可追溯至 SRC、假設與決策；弱輸入以區間與門檻呈現；L1／Interface 被至少一個下游模型穩定取數；公司特有逻輯不進核心層。

## 附錄

捨棄項目與理由（未進入建議表者）：

| 項目 | 來源 | 理由 |
| --- | --- | --- |
| 成熟度評分（3.8／5 等） | Copilot 整體 | 無可重現依據；改用統計 |
| 工作簿拆為 Evidence store／Calculation core／Reporting | Copilot 整體 P2-3 | 與 Excel 為事實來源的工作方式相抵 |
| 公司映射模板、回報歸因 | Copilot 整體 P2-1／P2-2 | 屬下游模型；已有 OpenAI／CRWV／Nebius／Oracle 承接 |
| 產業價值分配模組 | Copilot 整體 P1-2 | 屬 Project 層論述，無資料可檢驗；不入工作簿 |
| q、p、c 示範參數 | Copilot MW | 無來源 |
| 中性情境「每 MW 收入持平」機率 55% | Copilot MW | 機率無依據；保留機制，不保留機率 |
| Sprint 1–4 時程（1–12 週） | Copilot 整體 | 改為版本順序，時程由 Andy 定 |

重算腳本（只用工作簿與 MW 報告的輸入值）：

```python
# 每 MW 收入三情境（GB300）：路徑 A／B 重現與成本底線對帳
hold = 12.72           # L1_HoldEconGW_GB300 ÷ 1000，$M/MW-IT/yr
gpu_mw = 6764*72/1000  # 487 GPU/MW-IT
for name, k, o in [("保守", 0, .06), ("基準", .15, .08), ("積極", .30, .10)]:
    print(name, "路徑A", round(hold*(1+k)/(1-o), 2))        # 13.53 / 15.90 / 18.37
for name, p, u in [("基準 Verda", 5.21, .85), ("積極 Verda", 7.82, .90)]:
    print(name, "路徑B", round(p*gpu_mw*8760*u/1e6, 2))     # 18.89 / 30.02
print("IREN 隱含 $/GPU-hr", round(9.70e6/(gpu_mw*8760), 2),  # 2.27
      "vs 持有成本", round(hold*1e6/(gpu_mw*8760), 2))     # 2.98
print("保守市場點 ÷ 持有成本", round(9.70/hold, 2))         # 0.76

# 機隊損益兩平（VR200）：Theory_Rev 機隊營收 ÷ 持有成本 3.818 @ 利用率 0.6
print("損益兩平 util*derate*L*m =", round(0.6/3.818, 3))   # 0.157
```

工作簿統計與 Block 1／4 重算腳本見 Claude 原報告附錄；本報告的數字與該報告一致。

名詞：Luna／Sol／Astra＝低／中／頂層級代表模型；IF_Util＝第 0 層基準技術利用率；生產折減＝實測→生產效率折減（Serving C18）；L／m＝壽命期價格係數／變數率；q／p／c＝每 MW 產出／每 token 價格／價值捕獲乘數；G8、J8、K7、L3 等＝Tokenomics Decisions 頁的決策 ID。

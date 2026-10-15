# Tokenomics 下游資料契約 v0.3（2026-10-16；對應 Tokenomics v7.0）

適用對象：OpenAI、CoreWeave、Nebius、Oracle、Anthropic、MiniMax 等公司模型，以及任何用到 AI 算力數據的產業或個股研究。依據：Decisions G8（邊界）、X13（規模分工）、X14（輸出契約，v5.29 工作單）；整合版評估報告 `docs/reports/20261008_eval_integrated.md`。

## 1. 三層邊界

| 層 | 內容 | 持有者 |
|---|---|---|
| 核心 Tokenomics | 硬體、機架、電力、DC 成本；架構、SLO、KV、EP；推論、訓練、harness；每 GW 產能、每 M token 成本、每成功任務成本；產業級價格與需求資料 | Tokenomics 工作簿 |
| 產業經濟（跨公司） | 需求量、有效售價與下降速度、免費／付費、研發與服務配置（以 OpenAI 為代表性實驗室代理，G15）、價值分配 | Tokenomics Block 4／6 + Project 層論述 |
| 公司與投資 | 產品組合、市占、合約計價、價值捕獲率、簽約率、容量交付、WACC、收入、EPS、估值 | 各公司模型 |

## 2. 取數規則

1. 只取 `IF_`、`IFW_`、`IFC_`、`L1_` 具名範圍與 `SRC_` Active 紀錄；`DRV_`、`CAL_`、`B4_`、`B5_`、`CST_`、`IDX_`、`IF_Hdr*` 禁止連結。
2. 每 GW 產能與理論營收必須同時取四層瀑布（`IFW_*_100`／`_Util`／`_Prod`／`_Life`），不得只取 100% 層；取用時依 `IFC_Use` 欄的用途限制（「上限，不得作預測」者不得當收入預測）。四層單調遞減（v6.0 起定義如下，稽核修正 1 D7）：`_Util`＝`_100` × IF_Util；`_Prod`＝生產折減（CTL_ProdDerate）下**重解 SLO** 後的產能（營收讀 Interface G 節，token 產能與前緣單價營收讀 Theory_Rev_Prod／Fleet_1GW_Prod），**不是** `_Util` × CTL_ProdDerate；同一層級的 `_Prod` 營收 ÷ `_Prod` token＝該層級單價（Checks Z1，容差 1e-9）；`_Life`＝`_Prod` × L × m，唯一定義為 `IFW_*_Life`。`IF_RevGW_*_Life`、`IF_RevGWFleet_Life` 為**過渡別名**（＝對應 `IFW_*_Life`），下一個主版刪除，下游請改取 `IFW_*_Life`。名稱輸出為文字時，代表不可用（SLO 不可達或無法計算），下游不得以 0 代入。
3. 公司特有變數（WACC、合約價、價值捕獲率、簽約率、交付進度、產品組合）在下游覆寫，不回寫 Tokenomics。
4. 下游發現的產業級缺口（例如新的市場 GPU-hr 價格點、新 benchmark）走 G2 流程進 DB_Evidence，不自行建表。
5. 規模校準：Tokenomics 的代表性模型與需求 D 相對 OpenAI 2025 實際規模偏小（`L1_ScaleRD` 約 10、`L1_ScaleServe` 約 14，X13）。服務端落差已分解為四項口徑差（X14 (m)，`L1_Gap*`）：每則提示 token 數、支出計價口徑（Azure 帳單對持有成本）、參考請求 ISL 對實際混合、實際利用率對 60%。下游以自身的請求組合、計價口徑與利用率逐項換算，不得把 `IF_TokGW_*` 直接當成生產環境產能；OpenAI 模型校準後若四項乘積與觀測落差不符，差額回報 Tokenomics。

## 3. 利用率與簽約率的分工

| 計價方式 | 收入取決於 | Tokenomics 提供 | 下游設定 |
|---|---|---|---|
| 按 token（模型商） | 技術利用率（已上線容量在 SLO 下的平均負載） | `IF_Util`（基準 60%，Assumed）、`CTL_ProdDerate` | 可覆寫利用率；L、m |
| 按 GPU-hour／MW-year（新雲、雲平台） | 商業簽約率（容量是否已售出） | 成本底線 `L1_HoldEconMW_*`、世代產出比 `L1_TokMW_Gen_ratio_*` | 簽約率（滿產滿租＝100%）、價格層、價值捕獲率 c |

兩者同時扣減即重複扣減；每個下游模型必須在 handoff 寫明採哪一種。

## 4. 每 MW 收入生成式（新雲、雲平台）

- 每 MW 收入 = 每 MW token 產出 × 每 token 實收價格 × 價值捕獲率 × 簽約率；乘數形式：q × p × c。
- q 由 Tokenomics 跨世代產出比提供；p 由 SRC_Price 時間序列提供（隨需／預留／長約三層不得混用）；c 與簽約率由下游設定（按 token 計價 c ≈ 1，按 MW-year 計價 c ≈ 0）。
- 成本加成路徑（持有成本 × (1+k) ÷ (1−o)）只作 ROIC 與資金缺口檢查，不作收入輸入；成本加成與市場價平均的做法停用（X14 (j)）。
- **q × p ≈ 1 是情境標籤「持平情境」，不是基準**（v7.0 起；v6.3 以前曾寫為「中性情境」）。持平情境成立的條件，是年價格變化等於 `L1_GenPxThr_Rev_<世代>`（例如 GB300→VR200 基準約 −32%／年）；高於門檻為樂觀（q × p > 1），低於門檻為保守（q × p < 1）。
- **世代間每 MW 簽約收入的判讀方式**（v7.0 新增）：
  - 下游以自己採用的價格口徑（建議用算力租賃價，隨需／預留／長約分開，不混用），把觀察到的**年價格變化**與 `L1_GenPxThr_Rev_*`（新世代每 MW 收入持平）、`L1_GenPxThr_Pay_*`（新世代回本餘裕持平，含持有成本比）比較：實證的年價格變化高於門檻，新世代每 MW 收入（回本餘裕）高於上一世代。
  - Tokenomics **不提供世代間價格基準**，也不提供含價格的每 MW 收入指數；門檻不含價格。
  - 門檻屬**固定模型口徑**（q 為同一模型、換新硬體的產出比，Arch 三層級為單一時點快照）。若以層級牌價配對，實際各世代上市時層級代表的模型可能變大（`ARCH_ScaleGen`），需由下游自行扣除模型變大的成本；Tokenomics 另以情境 `d1_model_scale` 提供模型變大時的門檻值（報告 `docs/reports/20261016_稽核修正2-2.md`）。
  - 區間欄 `_Lo`／`_Hi` 是兩個端點（q 低端＋Δ 低端、q 高端＋Δ 高端）中的較小／較大者，不一定對應「q 低」或「q 高」（VR200 的 q 低端 0.915 使收入門檻轉正）。
  - 世代上市間隔 Δ 為單一樣本（Analogy）：`CAP_GenGap_GB200／GB300／VR200`（Cap_In L 節，年；基準／低／高 1.88／1.88／2.17、0.41／0.41／0.54、1.18／1.11／1.24）。GB200→GB300 約半年，年化價格變化率對 Δ 極敏感，宜讀區間，不讀單點。
- **v7.0 新增的具名範圍**：`L1_GenPxThr_Rev_GB200／GB300／VR200`、`L1_GenPxThr_Pay_GB200／GB300／VR200`（各含 `_Lo`／`_Hi`；%／年，小數）、`CAP_GenGap_GB200／GB300／VR200`（各含 `_Lo`／`_Hi`；輸入，下游不得覆寫）、`L1_FleetProdRatio`（含 `_Lo`／`_Hi`；機隊營收重解比，顯示用）。
- 對帳提醒：IREN–Microsoft 長約隱含 9.70 US$M/MW-IT/年，低於 Tokenomics GB300 經濟持有成本 12.72（比值 0.76；v5.31 J1／J2 後為 10.89，比值 0.89）；下游須指定解讀（不回本、成本結構不同、或合約含非收入條款）。

- IT 維護（v5.31 X17）：Tokenomics 穩態成本用壽命期等值費率（`IF_MaintIT`）；下游公司模型若逐年追蹤機隊年齡，改用 `IF_MaintITWarr`（前 `IF_WarrantyYrs` 年）與 `IF_MaintITPost`（之後），不得與 `IF_MaintIT` 重複計入。`IF_StaffSW` 不含平台研發，下游另列。

## 5. 版本與引用

- 下游 handoff 記錄所用 Tokenomics 版本（`model/CURRENT` 檔名與 master 合併雜湊）。
- Tokenomics 次版升級（SRC Active 值或公式改變）時，下游在下一版重新取數並在 handoff 註明差異。
- v6.0（主版，契約改變）起 `_Prod`、`_Life` 的定義變更（第 2 條），並新增「文字＝不可用」語意；受影響的名稱清單與新舊值見 `docs/reports/20261015_稽核修正1.md` 的「下游契約名稱新舊值表」。回本所需單價溢價 `IF_AmortBU_*` 的分母改為付費 token（`IF_FullCost_*`、`IF_FullCostDefault_*` 隨之上升）。
- v7.0（主版，契約改變）：第 4 節改寫（持平情境改為情境標籤，新增門檻名稱）；`L1_FleetMargin` 的生產折減改讀重解值（基準 3.388 → 3.118）、`L1_GapUtil` 乘生產折減（1.463 → 1.722，`L1_GapProduct` 1.635 → 1.924）；Alloc 敏感度表的『全 GB200』『全 VR200』改為純世代（不影響 `IF_`／`IFW_`）。名稱新舊值見 `docs/reports/20261016_稽核修正2-2.md` 的「下游契約名稱新舊值表」。

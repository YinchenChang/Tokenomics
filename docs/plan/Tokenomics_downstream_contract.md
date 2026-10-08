# Tokenomics 下游資料契約 v0.1（2026-10-08）

適用對象：OpenAI、CoreWeave、Nebius、Oracle、Anthropic、MiniMax 等公司模型，以及任何用到 AI 算力數據的產業或個股研究。依據：Decisions G8（邊界）、X13（規模分工）、X14（輸出契約，v5.29 工作單）；整合版評估報告 `docs/reports/20261008_eval_integrated.md`。

## 1. 三層邊界

| 層 | 內容 | 持有者 |
|---|---|---|
| 核心 Tokenomics | 硬體、機架、電力、DC 成本；架構、SLO、KV、EP；推論、訓練、harness；每 GW 產能、每 M token 成本、每成功任務成本；產業級價格與需求資料 | Tokenomics 工作簿 |
| 產業經濟（跨公司） | 需求量、有效售價與下降速度、免費／付費、研發與服務配置（以 OpenAI 為代表性實驗室代理，G15）、價值分配 | Tokenomics Block 4／6 + Project 層論述 |
| 公司與投資 | 產品組合、市占、合約計價、價值捕獲率、簽約率、容量交付、WACC、收入、EPS、估值 | 各公司模型 |

## 2. 取數規則

1. 只取 `IF_`、`IFW_`、`IFC_`、`L1_` 具名範圍與 `SRC_` Active 紀錄；`DRV_`、`CAL_`、`B4_`、`B5_`、`CST_`、`IDX_`、`IF_Hdr*` 禁止連結。
2. 每 GW 產能與理論營收必須同時取四層瀑布（`IFW_*_100`／`_Util`／`_Prod`／`_Life`），不得只取 100% 層；取用時依 `IFC_Use` 欄的用途限制（「上限，不得作預測」者不得當收入預測）。v5.30 起四層為逐層累乘、單調遞減（`_Util`＝`_100` × IF_Util、`_Prod`＝`_Util` × CTL_ProdDerate、`_Life`＝`_Prod` × L × m；X15 (a)）。
3. 公司特有變數（WACC、合約價、價值捕獲率、簽約率、交付進度、產品組合）在下游覆寫，不回寫 Tokenomics。
4. 下游發現的產業級缺口（例如新的市場 GPU-hr 價格點、新 benchmark）走 G2 流程進 DB_Evidence，不自行建表。
5. 規模校準：Tokenomics 的代表性模型與需求 D 相對 OpenAI 2025 實際規模偏小（`L1_ScaleRD` 約 10、`L1_ScaleServe` 約 14，X13）。服務端落差已分解為四項口徑差（X14 (m)，`L1_Gap*`）：每則提示 token 數、支出計價口徑（Azure 帳單對持有成本）、參考請求 ISL 對實際混合、實際利用率對 60%。下游以自身的請求組合、計價口徑與利用率逐項換算，不得把 `IF_TokGW_*` 直接當成生產環境產能；OpenAI 模型校準後若四項乘積與觀測落差不符，差額回報 Tokenomics。

## 3. 利用率與簽約率的分工

| 計價方式 | 收入取決於 | Tokenomics 提供 | 下游設定 |
|---|---|---|---|
| 按 token（模型商） | 技術利用率（已上線容量在 SLO 下的平均負載） | `IF_Util`（基準 60%，Assumed）、`CTL_ProdDerate` | 可覆寫利用率；L、m |
| 按 GPU-hour／MW-year（神雲、雲平台） | 商業簽約率（容量是否已售出） | 成本底線 `L1_HoldEconMW_*`、世代產出比 `L1_TokMW_Gen_ratio_*` | 簽約率（滿產滿租＝100%）、價格層、價值捕獲率 c |

兩者同時扣減即重複扣減；每個下游模型必須在 handoff 寫明採哪一種。

## 4. 每 MW 收入生成式（神雲、雲平台）

- 每 MW 收入 = 每 MW token 產出 × 每 token 實收價格 × 價值捕獲率 × 簽約率；乘數形式：q × p × c。
- q 由 Tokenomics 跨世代產出比提供；p 由 SRC_Price 時間序列提供（隨需／預留／長約三層不得混用）；c 與簽約率由下游設定（按 token 計價 c ≈ 1，按 MW-year 計價 c ≈ 0）。
- 成本加成路徑（持有成本 × (1+k) ÷ (1−o)）只作 ROIC 與資金缺口檢查，不作收入輸入；成本加成與市場價平均的做法停用（X14 (j)）。
- 中性情境定義為 q × p ≈ 1（每 MW 收入持平）；樂觀 q × p > 1；保守 q × p < 1。
- 對帳提醒：IREN–Microsoft 長約隱含 9.70 US$M/MW-IT/年，低於 Tokenomics GB300 經濟持有成本 12.72（比值 0.76）；下游須指定解讀（不回本、成本結構不同、或合約含非收入條款）。

## 5. 版本與引用

- 下游 handoff 記錄所用 Tokenomics 版本（`model/CURRENT` 檔名與 master 合併雜湊）。
- Tokenomics 次版升級（SRC Active 值或公式改變）時，下游在下一版重新取數並在 handoff 註明差異。

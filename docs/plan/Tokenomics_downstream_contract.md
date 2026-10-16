# Tokenomics 下游資料契約 v0.7（2026-10-16；對應 Tokenomics v10.2）

適用對象：OpenAI、CoreWeave、Nebius、Oracle、Anthropic、MiniMax 等公司模型，以及任何用到 AI 算力數據的產業或個股研究。依據：Decisions G8（邊界）、X13（規模分工）、X14（輸出契約，v5.29 工作單）；整合版評估報告 `docs/reports/20261008_eval_integrated.md`。

## 1. 三層邊界

| 層 | 內容 | 持有者 |
|---|---|---|
| 核心 Tokenomics | 硬體、機架、電力、DC 成本；架構、SLO、KV、EP；推論、訓練、harness；每 GW 產能、每 M token 成本、每成功任務成本；產業級價格與需求資料 | Tokenomics 工作簿 |
| 產業經濟（跨公司） | 需求量、有效售價與下降速度、免費／付費、研發與服務配置（以 OpenAI 為代表性實驗室代理，G15）、價值分配 | Tokenomics Block 4／6 + Project 層論述 |
| 公司與投資 | 產品組合、市占、合約計價、價值捕獲率、簽約率、容量交付、WACC、收入、EPS、估值 | 各公司模型 |

## 2. 取數規則

1. 只取 `IF_`、`IFW_`、`IFC_`、`L1_` 具名範圍與 `SRC_` Active 紀錄；`DRV_`、`CAL_`、`B4_`、`B5_`、`CST_`、`IDX_`、`IF_Hdr*` 禁止連結。
2. 每 GW 產能與理論營收必須同時取四層瀑布（`IFW_*_100`／`_Util`／`_Prod`／`_Life`），不得只取 100% 層；取用時依 `IFC_Use` 欄的用途限制（「上限，不得作預測」者不得當收入預測）。四層單調遞減（v6.0 起定義如下，稽核修正 1 D7）：`_Util`＝`_100` × IF_Util；`_Prod`＝生產折減（CTL_ProdDerate）下**重解 SLO** 後的產能（營收讀 Interface G 節，token 產能與前緣單價營收讀 Theory_Rev_Prod／Fleet_1GW_Prod），**不是** `_Util` × CTL_ProdDerate；同一層級的 `_Prod` 營收 ÷ `_Prod` token＝該層級單價（Checks Z1，容差 1e-9）；`_Life`＝`_Prod` × L × m，唯一定義為 `IFW_*_Life`。`IF_RevGW_*_Life`、`IF_RevGWFleet_Life` 為**過渡別名**（＝對應 `IFW_*_Life`），延後到「下游同步（Andy 跑完 CoreWeave）之後的第一個主版」刪除（v9.0 仍保留），下游請改取 `IFW_*_Life`。**凡文字＝不可用，下游不得以 0 代入。** 目前可能的字樣有三種，依成因而異：「SLO 不可達」（decode 不可達）、「TTFT 不可達」（首 token 時間超過上限）、「整代不可達」（某占比大於 0 的世代整代不可用）；下游以「是否為數字」判斷，不以字串比對（字樣日後可能增減）。
3. 公司特有變數（WACC、合約價、價值捕獲率、簽約率、交付進度、產品組合）在下游覆寫，不回寫 Tokenomics。
4. 下游發現的產業級缺口（例如新的市場 GPU-hr 價格點、新 benchmark）走 G2 流程進 DB_Evidence，不自行建表。
5. 規模校準：Tokenomics 的代表性模型與需求 D 相對 OpenAI 2025 實際規模偏小（`L1_ScaleRD`、`L1_ScaleServe` 現值見 Interface／L1，X13；v9.0 為 5.318、5.406，隨版本變動，不在此寫死）。服務端落差已分解為四項口徑差（X14 (m)，`L1_Gap*`）：每則提示 token 數、支出計價口徑（Azure 帳單對持有成本）、參考請求 ISL 對實際混合、實際利用率對 60%。下游以自身的請求組合、計價口徑與利用率逐項換算，不得把 `IF_TokGW_*` 直接當成生產環境產能；OpenAI 模型校準後若四項乘積與觀測落差不符，差額回報 Tokenomics。

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
- **q × p ≈ 1 是情境標籤「持平情境」，不是基準**（v7.0 起；v6.3 以前曾寫為「中性情境」）。持平情境成立的條件，是年價格變化等於 `L1_GenPxThr_Rev_GB200／GB300／VR200`（例如 GB300→VR200 基準，v10.2 的 `L1_GenPxThr_Rev_VR200` 約 −29.2%／年；此值隨版本變動，以 Excel 現值為準）；高於門檻為樂觀（q × p > 1），低於門檻為保守（q × p < 1）。
- **世代間每 MW 簽約收入的判讀方式**（v7.0 新增）：
  - 下游以自己採用的價格口徑（建議用算力租賃價，隨需／預留／長約分開，不混用），把觀察到的**年價格變化**與 `L1_GenPxThr_Rev_*`（新世代每 MW 收入持平）、`L1_GenPxThr_Pay_*`（新世代回本餘裕持平，含持有成本比）比較：實證的年價格變化高於門檻，新世代每 MW 收入（回本餘裕）高於上一世代。
  - Tokenomics **不提供世代間價格基準**，也不提供含價格的每 MW 收入指數；門檻不含價格。
  - 門檻屬**固定模型口徑**（q 為同一模型、換新硬體的產出比，Arch 三層級為單一時點快照）。若以層級牌價配對，實際各世代上市時層級代表的模型可能變大（`ARCH_ScaleGen`），需由下游自行扣除模型變大的成本；Tokenomics 另以情境 `d1_model_scale` 提供模型變大時的門檻值（報告 `docs/reports/20261016_稽核修正2-2.md`）。
  - 區間欄 `_Lo`／`_Hi` 是兩個端點（q 低端＋Δ 低端、q 高端＋Δ 高端）中的較小／較大者，不一定對應「q 低」或「q 高」（VR200 的 q 低端 0.915 使收入門檻轉正）。
  - 世代上市間隔 Δ 為單一樣本（Analogy）：`CAP_GenGap_GB200／GB300／VR200`（Cap_In L 節，年；基準／低／高 1.88／1.88／2.17、0.41／0.41／0.54、1.18／1.11／1.24）。GB200→GB300 約半年，年化價格變化率對 Δ 極敏感，宜讀區間，不讀單點。
- **v7.0 新增的具名範圍**：`L1_GenPxThr_Rev_GB200／GB300／VR200`、`L1_GenPxThr_Pay_GB200／GB300／VR200`（各含 `_Lo`／`_Hi`；%／年，小數）、`CAP_GenGap_GB200／GB300／VR200`（各含 `_Lo`／`_Hi`；輸入，下游不得覆寫）、`L1_FleetProdRatio`（含 `_Lo`／`_Hi`；機隊營收重解比，顯示用）。
- 對帳提醒：IREN–Microsoft 長約隱含 9.70 US$M/MW-IT/年，低於 Tokenomics GB300 經濟持有成本 12.72（比值 0.76；v5.31 J1／J2 後為 10.89，比值 0.89）；下游須指定解讀（不回本、成本結構不同、或合約含非收入條款）。

- IT 維護（v5.31 X17）：Tokenomics 穩態成本用壽命期等值費率（`IF_MaintIT`）；下游公司模型若逐年追蹤機隊年齡，改用 `IF_MaintITWarr`（前 `IF_WarrantyYrs` 年）與 `IF_MaintITPost`（之後），不得與 `IF_MaintIT` 重複計入。`IF_StaffSW` 不含平台研發，下游另列。

- **Q1、Q2、服務 GW 的定義（v8.0 改寫，D14）**：
  - `IF_AllocServeGW`（服務 GW 合計）改為**支出路線**＝推論支出（`SRC_DEM_004`）÷（Σ 服務世代占比 × 各世代每 GW 年持有成本）。舊的 token 路線（需求 D ÷ 每 GW 產能）改名保留為 `IF_AllocServeGW_Tok`，只供對照，**不得當產能或主口徑**。
  - `IF_AllocQ1`（研發算力占比，R1）＝研發 GW ÷（研發 GW ＋ 支出路線服務 GW）。`IF_AllocQ2`（研發算力成本占比）＝研發 GW × 持有成本 ÷（研發 GW × 持有成本 ＋ 支出路線服務 GW × Σ 服務世代占比 × 持有成本）。`IF_AllocQ1_R2`（免費服務算作產品改良）＝（研發 GW ＋ 支出路線服務 GW × `AL_FreeSpendShare`）÷（研發 GW ＋ 支出路線服務 GW）（**v9.0 改**：v8.0 為 token 路線，0.665；v9.0 為 0.577）。
  - 研發 GW（`IF_AllocRDGW`）改按 2025 年研發世代組合加權（Alloc_In 新增 `AL_RDMix*` 四格，基準 Hopper 60%／GB200 38%／GB300 2%／VR200 0%；不可達世代依 D8 排除並重新正規化），不再只用 `IF_TrainGenDefault`（VR200）。
  - 下游若引用 Q1、Q2，須知 v7.0 → v8.0 基準值由 0.364／0.428 變為 0.211／0.212；兩者的變動來自兩項獨立改動（研發世代組合使研發 GW 增加、支出路線使服務 GW 增加）加上交互作用，拆解見 `docs/reports/20261016_稽核修正2-3.md`。
- **所需 L 與 m 的 2025 年度口徑（v8.0 改寫，D2）**：`L1_MFleet` 改用 2025 年度層級單價（`CAP_Px25_*`、`AL_PriceFleet25`），`L1_LReqFleet` 的損益兩平改讀 2025 機隊口徑（`L1_FleetBreakeven2025`）。`L1_FleetBreakeven`、`L1_FleetMargin` 維持 VR200 截面（Checks K4 比對的恆等式），不是 2025 機隊。基準下所需 L 由 0.530 變為 1.968，大於 `L1_LTotal`（0.643），回本判讀由「回本」變為「未回本」；依恆等式讀法為 0.756（同樣大於 L_total）。

- **快取命中進產能（v9.0 改，D9）**：`IF_TokGW_*`（及由它推得的 `IFW_*`、`IF_RevGW*`、`IF_Cost*`、`IF_Amort*`）的 prefill 只計新鮮輸入 ISL × (1 − `B4_CacheHit`)；`IF_TokGW_*` 計入的 token 定義不變（每請求 ISL＋OSL，快取輸入仍算已服務 token，以快取價計價）。基準下各世代各層級的 `IF_TokGW_*` 上升 8–22%，Hopper × Astra 由「TTFT 不可達」變為數字（基準 3.63e9 M tok/年）。倍數表見 `docs/reports/20261016_稽核修正2-4.md`。批次推論（Perf_Batch，訓練端）不套用快取，`IF_Train*` 不變。
- **回本判讀的兩種讀法（v9.0，M5）**：`L1_LReqFleet`（字面讀法）＝`L1_FleetBreakeven2025` ÷（`IF_Util` × `CTL_ProdDerate` × `L1_MFleet`）；`L1_LReqFleet_Id`（恆等式讀法）＝支出路線服務 GW 的持有成本 ÷ 營收。v9.0 基準兩者相差 2.69 倍（字面 2.04、恆等式 0.756；`L1_LTotal` 0.643），來源是機隊每 GW 營收只含付費服務占比（B4_Serve × (1 − B4_Free)＝22%）、實際利用率對 `IF_Util`、免費 token 稀釋三項（兩種讀法差 2.69 倍＝付費服務占比倒數 4.52 × 付費 token 占比 0.873 × 實際÷模型利用率 0.683，此拆解寫在 L1 判讀欄，隨數值更新）。L1 判讀欄以恆等式讀法為主、字面讀法並列（v10.1 刪除舊規則「兩者相差 ≤10% 時自動改以字面讀法為主」：v10.0 N4-8 起判讀欄只用恆等式讀法）。下游引用「所需 L」時須註明所用讀法。字面讀法的分子（營收）與分母（持有成本）口徑不一致，僅供對照，不作為回本結論；回本結論一律取恆等式讀法 `L1_LReqFleet_Id`（v10.0 N5）。
- **需求路線 m 與免費占比口徑（v9.0，D9、M6）**：`L1_MImplied`、`L1_MImplied_Ext`、`L1_MAPI`、`L1_MSub`、`L1_MSeat` 的單價改用 2025 年度混合有效單價 `CAP_Price25Mix`（× `AL_Kappa`），與 `L1_MFleet` 同年度口徑；價格區間（`CAP_Px25_*_Lo／_Hi`）不交叉進 m 的 `_Lo`／`_Hi`（m 的低高只反映 token 端）。`L1_MImplied_Ext` 的付費占比改用 token 口徑 1 − `AL_FreeShare`（原用支出口徑 `IF_FreeShare`）。`IF_AmortRev_*`（營收權重攤提）的分母改為該層級付費 token（與 `IF_AmortBU_*` 一致）。`L1_ExtServeGW` 的推算值改回 `IF_AllocServeGW`（支出路線）；token 路線見 `IF_AllocServeGW_Tok`。

## 5. 版本與引用

- 下游 handoff 記錄所用 Tokenomics 版本（`model/CURRENT` 檔名與 master 合併雜湊）。
- Tokenomics 次版升級（SRC Active 值或公式改變）時，下游在下一版重新取數並在 handoff 註明差異。
- v6.0（主版，契約改變）起 `_Prod`、`_Life` 的定義變更（第 2 條），並新增「文字＝不可用」語意；受影響的名稱清單與新舊值見 `docs/reports/20261015_稽核修正1.md` 的「下游契約名稱新舊值表」。回本所需單價溢價 `IF_AmortBU_*` 的分母改為付費 token（`IF_FullCost_*`、`IF_FullCostDefault_*` 隨之上升）。
- v7.0（主版，契約改變）：第 4 節改寫（持平情境改為情境標籤，新增門檻名稱）；`L1_FleetMargin` 的生產折減改讀重解值（基準 3.388 → 3.118）、`L1_GapUtil` 乘生產折減（1.463 → 1.722，`L1_GapProduct` 1.635 → 1.924）；Alloc 敏感度表的『全 GB200』『全 VR200』改為純世代（不影響 `IF_`／`IFW_`）。名稱新舊值見 `docs/reports/20261016_稽核修正2-2.md` 的「下游契約名稱新舊值表」。
- v8.0（主版，契約改變）：`IF_AllocQ1`／`IF_AllocQ2`／`IF_AllocServeGW` 改為支出路線定義，`IF_AllocRDGW` 改按 2025 研發世代組合；`L1_MFleet`、`L1_LReqFleet`、`L1_PriceReqBE`、`L1_ScaleRD`、`L1_RevGWFleet_OAI2025` 與 `L1_Ans1–3` 數值改變。新舊值表見 `docs/reports/20261016_稽核修正2-3.md`。
- v6.2（次版）：新增模型規模倍數 `ARCH_ScaleGen`（基準 1，情境 `d1_model_scale`）；TTFT 納入可達判斷（文字旗標「TTFT 不可達」）；Alloc 排除不可達層級後重新正規化。名稱新舊值見 `docs/reports/20261016_稽核修正2-1.md`。
- v6.3（次版）：機隊 m 的單價與機隊 token 同用可達層級（`AL_PriceFleet`、`B4_PriceFleet`）；整代不可達輸出文字「整代不可達」（`AL_UnavailTxt`）；TTFT 不可達的 decode 成本列輸出文字；`ARCH_ScaleGen_Lo／_Hi` 依 2Q 報告修訂。名稱新舊值見 `docs/reports/20261016_稽核修正2-1b.md`。
- v9.0（主版，契約改變）：`IF_TokGW_*` 因快取命中進產能全部上升（各世代 Sol 欄 ×1.17–1.22），Hopper × Astra 恢復可達；`IF_AllocQ1_R2` 改支出路線；`IF_AmortRev_*` 分母改付費 token；`L1_MImplied`／`MImplied_Ext`／`MAPI`／`MSub`／`MSeat` 改 2025 單價（`MImplied_Ext` 並改 token 口徑付費占比）；`L1_ExtServeGW` 推算值改回支出路線；回本判讀以恆等式讀法為主。`IF_AllocQ1`／`Q2`／`ServeGW`、`IF_AllocRDGW`、`L1_LReqFleet_Id`、`L1_LTotal`、Training 頁與 `IF_Train*` 不變。新舊值表見 `docs/reports/20261016_稽核修正2-4.md`。M1 另以傳遞方式使 `L1_FleetMargin`、`L1_GenPxThr_*`、`L1_TokMW_Gen_ratio_*`、`L1_GapProduct` 等數值改變（上游輸入改變所致，非定義改變）。

- v10.0（主版，契約改變；稽核修正2 第 2-5 段）：既有 `IF_`／`IFW_`／`L1_` 名稱數值不變。新增名稱：（1）`IFW_RevGW_Luna_LifeSelf`、`IFW_RevGW_Sol_LifeSelf`、`IFW_RevGW_Astra_LifeSelf`、`IFW_RevGWFleet_LifeSelf`、`IFW_RevGWFront_Luna_LifeSelf`、`IFW_RevGWFront_Sol_LifeSelf`、`IFW_RevGWFront_Astra_LifeSelf`、`IFW_RevGWFleetFront_LifeSelf`（共 8 個，Interface L 節）＝`_Prod` × `L1_LTotal` × `L1_MFleet`，標示「情境：自算 L、m；不回流，不建議下游作為基準」，不得連回 Tokenomics 其他計算；下游若採 L、m 以自身估計為準，不取此組作基準；（2）`L1_GapUnexplained`（＋`_Lo`／`_Hi`）＝服務端落差中四項口徑差未解釋的部分（`L1_ScaleServe2000` ÷ `L1_GapProduct`）；（3）`CHK_VerifyTotal`／`CHK_VerifyPass`／`CHK_VerifyFail`（唯讀）：只計能失敗的驗證項（MLPerf 上限、LMSYS 獨立點、RL 占比、harness 輪數、樣本外點），恆等式不計入；基準 14 項、7 通過、7 失敗，失敗項不進 GOV_Errors，下游引用 Tokenomics 產能時須知有 7 項驗證未通過；（4）L1 新增「性質」欄（估計／殘差／倒推／恆等式／未解釋），下游引用 L1 數值時依性質判斷可信度；（5）`SRC_PERF_060–065`、`SRC_HAR_016`（MLPerf v5.1 Hopper／GB200 與 harness 檢查來源）。回本判讀字面讀法的口徑不一致已於第 2 節註明。名稱新舊值與驗證清單見 `docs/reports/20261016_稽核修正2-5.md`。

- v10.2（次版；η 校準與驗證判準，工作單 `docs/workorders/20261016_η校準.md`）：（1）Serving 每用戶 decode 速度 SLO 由 120／65／55 改為兩家量測商（Artificial Analysis、OpenRouter）中位數的幾何平均 84.3／43.3／40.8 tok/s/user（Luna＝GPT-6 Luna、Sol＝GPT-6.1 Sol、Astra＝GPT-6 Astra），`IF_TokGW_*` 及其下游（`IF_Cost*`、`IF_FullCost*`、`IF_RevGW*`、`IF_Amort*`、`L1_MFleet`、`L1_ScaleServe*`、`L1_Gap*`）全部改變；Sol 欄各世代 `IF_TokGW_Sol` 約 ×1.48（Hopper）、×1.20（GB200、GB300）、×1.13（VR200）、×1.11（Rubin Ultra）；`L1_MFleet` 0.550 → 0.407。舊口徑留作情境 `slo_v10`。（2）E1：C67（Hopper η_d 倍數）與 GB200 倍數**未改**（Hopper 在條件對齊的複本列無解、GB200 的解使有效算力高於 GB300，依停損規則待 Project 判斷）；Calib 新增 J 節（校準複本列與條件對齊列）。（3）`CHK_VerifyTotal`／`Pass`／`Fail` 由 14／7／7 改為 17／9／8：V2、V3 對照改 MLPerf v6.0 NVIDIA 72 GPU 值（4,668、5,562）、V7／V8 改條件對齊、V13／V14 加上限 3、新增 V15（DeepSeek 線上服務 1,850）、V16／V17（原 Checks B26／B36 改回驗證）。（4）新增 `SRC_PERF_066–078`（共 13 個名稱）。`IF_AllocServeGW`、`IF_AllocRDGW`、`L1_LReqFleet_Id`、`L1_HoldEconMW_*`、Training 各頁數值不變。名稱新舊值見 `docs/reports/20261016_η校準.md`。

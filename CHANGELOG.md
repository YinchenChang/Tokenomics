# CHANGELOG

每次同步 Excel 新版本記錄：Excel 版本、commit、變動摘要。

## 20261001_Tokenomics_v5.7.xlsx（取代 v5.6；第 6 輪，PR #6）

- Commit：見 PR #6 的合併提交（合併後補上雜湊）。
- Excel：公式 16,251（不變）；具名範圍 142 → 144（新增 `IF_TrainGenDefaultName`、`IF_TrainGenAltName`，指向 `Interface!D81`、`D82`）；新增工作表 `DB_Evidence`（證據登錄表，純輸入、無公式，A4:K13，9 筆）。
- 迴歸：v5.7 對 v5.6，兩版共有的 142 個具名範圍逐格一致；22 個既有工作表只有 README 的 26 格文字不同。
- 測試：期望值改為 144 個具名範圍（顯示用 75、下游 67）、工作表清單 23 頁（含 `DB_Evidence`，無公式）；新增世代名稱與索引一致檢查、`model/CURRENT` 與現行檔一致檢查。
- 網站：預設與並列訓練世代改讀 `IF_TrainGen*Name`；新增「證據登錄」唯讀頁（讀 `DB_Evidence` 工作表）。
- 檔案：v5.6 以 `git mv` 移入 `model/archive/`；新增 `model/CURRENT` 與 `builder/`。
- builder（修訂四第 4 節）：依 `docs/builder/Tokenomics_builder_v5.md` 的 9 個區塊逐字寫入 `builder/`（common、inputs、calib、perf、outputs、training、finish、preserve、build）。驗證兩次重建（以 v5.6、v5.7 為底稿），LibreOffice 重算後皆與 v5.7 逐格一致（20,539 格不符 0、錯誤 0、公式 16,251、具名範圍 144 且完全相同）；`restore_log`：對應 770、Excel 值保留 0、未對應 0。

## 20261001_Tokenomics_v5.6.xlsx（取代 v5.5；第 5 輪，併入第 4 輪 PR）

- Commit：`e0017b6`（PR #5 合併提交；v5.5、v5.6 同屬此 PR）。
- Excel：公式 16,245 → 16,251（+6）；具名範圍 117 → 142（新增 25：`TR_` 23 個、`IF_TrainGenDefault`、`IF_TrainGenAlt`；無移除）。
- 變動：非同步 RL 併入基準（rollout 效率 0.6 → 0.85、rollout token 重校）；Block 1、2 的具名範圍與 v5.5 逐格一致，變動只在 Block 3 的 `IF_`（24 個）與 `TRN_`（10 個）。
- 迴歸門檻：Hopper 差異 0.0506% 經 Andy 確認接受（倍數取整所致），迴歸門檻改為 0.06%。
- 測試：期望值改為 16,251 格、142 個具名範圍（顯示用 75、下游 65）；新增 `TR_` 形狀檢查（登錄表 12 格、掛鉤彙總 11 格）與 `IF_TrainGen*`（世代索引 1–5）檢查。
- 網站：Tech_Registry 唯讀表改讀 `TR_` 具名範圍；預設與並列訓練世代改讀 `IF_TrainGenDefault`／`IF_TrainGenAlt`（不再以世代名稱字串或欄 A 定位）。
- 檔案：v5.5 以 `git mv` 移入 `model/archive/`。

## 20260930_Tokenomics_v5.5.xlsx（取代 v5.4；第 4 輪）

- Commit：`e0017b6`（PR #5 合併提交；v5.5、v5.6 同屬此 PR）。
- Excel：公式 8,438 → 16,245；具名範圍 78 → 117（移除 `DRV_CostDec`；新增 `IF_` 25 個：Block 3 的 8 個指標 × 3 層級與 `IF_RDMult`；`TRN_` 15 個）。新增工作表：Tech_Registry、Train_In、Perf_Batch、Training、Sens_Train。
- Block 2 迴歸：非 Hopper 欄與 v5.4 一致；Hopper 欄差異約 0.0506%、能量閉合比 6.5% → 3.7%（Luna），來自 Spec_Rack Hopper FP8 峰值更正。
- 測試：期望值改為 16,245 格、117 個具名範圍（顯示用 52、下游 63）；情境 5 → 7（新增 Tech_Registry!O11:O13＝1、Train_In!C13＝4.4）；新增 Block 3 名稱與欄數檢查；函數語意新增 `EXP(SUMPRODUCT(…LN…))` 與 `SUMPRODUCT` 條件加總。
- 引擎：pycel 不需改動即可計算 v5.5。
- 網站：新增 Block 3 頁（推導鏈、後訓練占比兩種口徑、RL 有效 MFU、Tech_Registry 唯讀表、VR200／GB300 並列）；總覽 Block 1 表排除 Block 3 列。

## 20260930_Tokenomics_v5.4.xlsx（取代 v5.3；第 3 輪）

- Commit：`58e8ece`（PR #4 合併提交）。
- Excel：公式 8,427 → 8,438（+11，皆為 Calib 組合標籤與世代名稱）；具名範圍 67 → 78（+11：CAL_F_Gen／Eng／Speed／Meas／Model／Basis、CAL_H_Gen／Speed／Meas／Model／Basis）；`CAL_F_Label` 改指向新的組合標籤列（世代｜用途｜速度）。
  與 v5.3 相比，其餘 11,101 個非空儲存格（Calib 插入 F 節 2 列、H 節 2 列後對齊）數值相同，只有 README 的 2 格版本標籤文字不同。
- 測試：期望值改為 8,438 格、78 個具名範圍（顯示用 38、下游 38）；新增 CAL_F_* 同為 7 格、CAL_H_* 同為 4 格檢查；網站測試新增「推導鏈成本列跟隨成本情境」。
- 網站：Calib 驗證表拆成 F、H 兩張並加欄（世代、軟體／日期（僅 F）、每用戶速度、實測、模型、口徑）；推導鏈成本列改讀 `IF_CostDec_<層級>`（跟隨成本情境）；`DRV_CostDec` 不再使用。

## 20260930_Tokenomics_v5.3.xlsx（取代 v5.2；PR 第 2 輪）

- Commit：`afb22c9`（PR #3 合併提交；v5.2、v5.3 同屬此 PR）。
- Excel：公式仍為 8,427；具名範圍 40 → 67（新增 27：IF_HdrGen、IF_HdrCost；DRV_ 17 個；CAL_ 8 個）。
  與 v5.2 相比，公式格數值相同；位置變動只有 Calib H 節於第 119 列插入「量測平台」；另有 31 格標籤文字（decode 標註「含思考 token」等）與 Checks 的 5 個參照常數（文字改數字）不同。
- 測試：parity 名稱檢查改為 67 個（另查 DRV_ 17、CAL_ 8、下游 IF_ 38；表頭與推導鏈欄數對齊）。
- 網站：Block 2 頁新增「推導鏈」；Calib 驗證表與表頭改讀 CAL_*、IF_Hdr*，移除以欄 A 標籤定位。
- 引擎：移除 `column_labels`、`row_values`（不再需要）。
- 停用：逐步能量模型不恢復（由 Excel Perf J 節取代）。
- v5.2 移入 `model/archive/`（master 上已由 Andy 完成；v5.0 亦由 Andy 於 master 刪除，本分支從其例）。

## 20260930_Tokenomics_v5.2.xlsx（取代 v5.0）

- Commit：`afb22c9`（PR #3 合併提交）
- Excel：8,427 個公式、40 個具名範圍（Block 2 新增 28 個）。
- 引擎：pycel 1.0b30（`engine/`）；以外掛補齊 `TEXT` 的十進位進位語意。
- 測試：`tests/parity/`（全部公式格、具名範圍、基準＋5 情境、函數語意）；`tests/app/`。
- CI：`.github/workflows/parity.yml`。
- 網站：`app/`（總覽、Block 2、Calib 驗證表）。
- 停用：`legacy/tokenomics_v4.py`（v4 手抄公式）、`tests/legacy/`；刪除 `tokenomics_bk.py`。
- 搬移：v5.0 與 `data/` 內舊 FTGP xlsx → `model/archive/`。

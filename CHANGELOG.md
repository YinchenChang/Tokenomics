# CHANGELOG

每次同步 Excel 新版本記錄：Excel 版本、commit、變動摘要。

## 20261004_Tokenomics_v5.14.xlsx（取代 v5.13；第 13 輪續：L1 錯誤值修正）

- Commit：見本輪 PR #13 的合併提交（合併後補上雜湊）。報告：`docs/reports/20261004_v5.14_sync.md`。
- **v5.13 未單獨合併**：v5.13 的 parity 有 2 個情境因 `L1!O35`、`L1!P35` 出現錯誤值而未通過，改由 v5.14 修正；v5.13 與 v5.14 在同一個 PR #13 合併（下方 v5.13 一節保留）。
- Excel（chat 端產生，CC 未改任何數值或公式）：SHA-256 `dc4ef406…2b56`；公式格 33,480、具名範圍 736、工作表 46，皆與 v5.13 相同。`L1` 的 O、P 欄在推算值非數字（SLO 不可達情境）時顯示「—」與「推算值非數字（本情境）」；SRC 各頁 X 欄的比對範圍縮小。
- builder：依 md 的 15 個區塊逐字覆寫（只有 `gov.py`、`finish.py` 有變動）。以 v5.13 為底稿重建，LibreOffice 重算後與 v5.14 逐格一致（61,184 格不符 0、錯誤 0、46 張工作表同序）；`restore_log` matched 936／Excel 值保留 0／unmatched 0。冪等：以 v5.14 為底稿重建，兩邊都經 LibreOffice 存檔後比對，公式文字 0 不符、重算值 0 不符、具名範圍 736 個逐一相同（61,715 格）。
- 檔案：v5.13 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.14；`model/` 只留一份 xlsx。
- 測試：期望值不變（33,480／736／46）；沒有改情境、比對範圍或容差。parity 127 項全過，含 `b_prod_derate`、`f_registry_t07_t09_on` 的「錯誤值 0」閘門；18 個情境數值不符 0（最大相對誤差約 5e-15）。網站測試 13 項全過；網站沒有寫死 L1 P 欄判讀文字，無需改動。
- 重算時間：本機全簿強制重算 1.44 秒、增量最大 0.59 秒（第 13 輪本機為 1.76／0.86 秒）。GitHub Actions 上 parity 127 項全過（2,534 秒）。
- CI：`.github/workflows/parity.yml` 新增一步，把情境數、不符格數、增量與全簿重算秒數寫入 job summary（只改輸出，不改斷言）。
- 治理：GOV_Errors 0、GOV_Warnings 238、GOV_Info 99。export_csv：GOV_Errors 0；SRC_HW 61、DC 14、Model 54、Perf 52、Price 45、Cap 22、Harness 16、Demand 10 列（含表頭各 1 列）、Interface 186 列。

## 20261003_Tokenomics_v5.13.xlsx（取代 v5.12；第 13 輪：切片二同步）

- Commit：見本輪 PR 的合併提交（合併後補上雜湊）。報告：`docs/reports/20261003_v5.13_sync.md`。v5.12 的合併提交為 `a466307`（第 12 輪 PR #12）。
- Excel（chat 端產生，CC 未改任何數值或公式）：SHA-256 `9b76f1e5…6540`；公式 30,158 → 33,480；具名範圍 611 → 736（`SRC_` 220 → 324、`L1_` 75 → 96，其餘前綴不變）；工作表 42 → 46（新增 `SRC_Price` 44、`SRC_Cap` 21、`SRC_Harness` 15、`SRC_Demand` 9 列）。Arch 第 21–23 列、Arch C9:C10、Cap_In N46:N58 改為公式；L1 由 25 列增為 32 列。Checks G 節：GOV_Errors 0、GOV_Warnings 238、GOV_Info 99。
- builder：依 md 的 15 個區塊逐字覆寫（新增 `gov_seed2.py`；`block4.py`、`build.py`、`finish.py`、`gov.py`、`inputs.py` 有變動）。以 v5.12 為底稿重建，LibreOffice 重算後與 v5.13 逐格一致（61,184 格不符 0、錯誤 0、46 張工作表同序）；`restore_log` matched 1,008／Excel 值保留 0／unmatched 0；`gov_log` 「retired input (now formula)」22 格。以 v5.13 為底稿重建（冪等）：matched 936／unmatched 0，重算值 61,184 格不符 0，具名範圍 736 個相同（公式原始文字寫法差異 3,895 格，數值不受影響）。
- 檔案：v5.12 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.13。
- 測試：期望值改為 33,480 格、736 個具名範圍（`SRC_` 324、`L1_` 96）、46 張工作表。沒有情境把 KV bytes（Arch 第 21–23 列）、Arch C9:C10、Cap_In N46:N58 當輸入，故情境檔未改；比對範圍與容差未動。parity 127 項：125 過、2 失敗（見下）；網站測試 13 項全過（證據頁 67 → 85 筆、L1 25 → 32 列、SRC_Perf 40 → 51 筆，並加 SRC 八頁列數檢查）。
- **（已由 v5.14 修正；v5.13 未單獨合併，與 v5.14 同一 PR #13）未通過：2 個情境（Excel 問題，未在 Python 修補）**：`b_prod_derate`、`f_registry_t07_t09_on`。兩者數值不符 0 格（最大相對誤差約 4.9e-15），失敗的是「任何情境不得出現錯誤值」閘門：`L1!O35`、`L1!P35`（OpenAI 2025 對帳列）在 SLO 不可達情境下，`D35`（連 `Checks!B43`）為文字「SLO 不可達」，公式只檢查 M35、N35 是否為數字，造成 #VALUE!。需 Project 端改 Excel。
- 重算時間（本機）：全簿強制重算 1.76 秒（< 2 秒）、增量最大 0.86 秒（< 2 秒）。GitHub Actions 實測秒數見 PR comment。
- 工具與網站：`tools/export_csv.py` 匯出 SRC 八頁（Price 44、Cap 21、Harness 15、Demand 9；Model 53、Perf 51；CSV 含表頭列各多 1 列）並檢查 GOV_Errors（0）；`tools/stage0_inventory.py` 治理頁清單加 4 頁；`app/common.py` SRC 頁前綴加 4 個（`IDX_`、`CST_` 仍不顯示為下游名稱）。數值與機制未改。

## 20261003_Tokenomics_v5.12.xlsx（取代 v5.11；第 12 輪：工程基礎）

- Commit：見本輪 PR 的合併提交（合併後補上雜湊）。報告：`docs/reports/20261003_v5.12_sync.md`。v5.11 的合併提交為 `a9bc106`（第 11 輪 PR #11）。
- Excel（chat 端產生，CC 未改任何數值或公式）：SHA-256 `d04fac3b…0926`；公式 27,700 → 30,158；具名範圍 604 → 611（新增 `CST_` 4、`IDX_` 3；`SRC_` 仍 220）；工作表 41 → 42（新增 `SRC_Index`；`Sources` 更名 `Sources_Legacy`）。Gov_Map 的 S、T 欄改查 SRC_Index（取代 6,960 個多頁 MATCH）；Checks G 節新增 E13（23 項，其後各列下移 1 列）；`B5_SelRho` 公式大小寫改為 `B5_Selrho`（25 格，與名稱一致）。
- builder：依 `docs/builder/Tokenomics_builder_v5.md` 14 個區塊逐字覆寫（`block4.py`、`block5.py`、`build.py`、`finish.py`、`gov.py`、`inputs.py`、`outputs.py`、`training.py` 有變動）。以 v5.11 為底稿重建，LibreOffice 重算後與 v5.12 逐格一致（52,520 格不符 0、錯誤 0）；`restore_log`：藍字輸入 1,021 全數對應、Excel 值保留 0、未對應 0。以 v5.12 為底稿：1,030／0／0，公式語意相同（原始文字差異 3,849 格皆為寫法）、具名範圍 611 個逐一相同。
- 檔案：v5.11 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.12。
- 效能門檻：全簿強制重算恢復為 < 2 秒（硬性）；移除「暫行至 v5.12」註記（測試與 `CLAUDE.md`）。本機實測全簿 1.39 秒、增量最大 0.53 秒（v5.11 為 3.4–3.7 秒）。
- 測試：期望值改為 30,158 格、611 個具名範圍、42 張工作表，另加 `CST_`／`IDX_` 名稱數與「CST_／IDX_ 不是下游名稱」檢查。18 個情境各 30,158 格不符 0，最大相對誤差約 5e-15。pycel 載入不再出現「Table Name not found」。
- 工具與網站：`tools/stage0_inventory.py` 的 `GOVERNANCE_SHEETS` 改 `Sources_Legacy` 並加 `SRC_Index`；網站 Checks G 節測試期望 22 → 23 項。`app/` 沒有寫死 `Sources` 頁名，無需修改；`CST_`、`IDX_` 不是 `IF_` 名稱，網站不顯示為下游名稱。
- 評估未採用：以 deepcopy 共用已建圖的引擎範本可將測試總時長由約 37 分降至約 10 分，但複本偶發 `'NoneType' object has no attribute 'get_range'`，且複本的重算變慢（4.9–6.2 秒），故不採用，測試維持每個情境重新建圖。

## 20261002_Tokenomics_v5.11.xlsx（取代 v5.10；第 11 輪：治理 Stage 1 切片一）

- Commit：見本輪 PR 的合併提交（合併後補上雜湊）。報告：`docs/reports/20261002_v5.11_sync.md`；Gate 1 輸出：`docs/reports/20261002_gate1.md`。
- Excel（chat 端產生，CC 未改任何數值或公式）：公式 20,780 → 27,700；具名範圍 305 → 604（SRC_ 220、L1_ 75、GOV_ 4 新增）；工作表 34 → 41（新增 L1、Gov_Map、Decisions、SRC_HW、SRC_DC、SRC_Model、SRC_Perf）。
- builder：依 `docs/builder/Tokenomics_builder_v5.md` 14 個區塊逐字覆寫（新增 `gov.py`、`gov_seed.py`、`gov_decisions.py`；`build.py`、`calib.py`、`finish.py`、`perf.py`、`training.py` 有變動）。以 v5.10 為底稿重建，LibreOffice 重算後與 v5.11 逐格一致（46,869 格不符 0、錯誤 0）；restore 1,152／Excel 值保留 0／未對應 0。以 v5.11 為底稿：1,021／0／0，公式語意相同、具名範圍 604 個逐一相同（原始文字差異 3,871 格皆為寫法：1E9 對 1000000000、名稱大小寫、工作表引號、9E+99 對 9E+099）。
- 檔案：v5.10 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.11。
- 測試：parity 期望值改為 27,700 格、604 個具名範圍、41 張工作表，另加 SRC_／L1_／GOV_ 名稱數；情境 16 → 18（新增 `gw_2`：`CTL_GW`＝2；`src_hw038_x1_1`：SRC_HW_038 ×1.1）。18 個情境各 27,700 格不符 0。
- engine：`norm()` 把 numpy 純量轉為 Python 型別（SUMPRODUCT 回傳 np.int64，型別嚴格比對下造成 158 格誤報；只改型別表示，不改數值）。
- 效能門檻（chat 端定案）：全簿強制重算 3.4–3.7 秒（v5.10 為 0.47 秒），主因是 Gov_Map S、T 欄 6,960 個 MATCH。測試拆為 (a) 每情境增量重算 < 2 秒（硬性）、(b) 全簿強制重算 < 5 秒（暫行，至 v5.12 為止；v5.12 以 SRC_Index 改寫後恢復 < 2 秒）；`CLAUDE.md` 引擎規則同步。
- 網站：新增「治理」頁（Checks G 節、L1 25 列、SRC 四頁 A–W 欄唯讀）；總覽加 `GOV_Errors`／`GOV_Warnings`／`GOV_Info` 與 Checks G 節表；證據登錄頁筆數 20 → 67（只讀 A:K 欄，L–Q 欄未顯示）。網站測試 13 項全過。
- 工具：`tools/stage0_inventory.py` 新增 `gate1` 子指令（含被單位表排除的整數常數複核表）；`tools/export_csv.py` 匯出 SRC_*、Interface 為 CSV 並檢查 `GOV_Errors`；CI 新增兩步（治理檢查、上傳匯出 CSV）。

## 第 10 輪：Stage 0 盤點（唯讀）＋網站小修（Excel 不變，仍為 `20261002_Tokenomics_v5.10.xlsx`）

- Commit：見本輪 PR 的合併提交（合併後補上雜湊）。
- Excel：**未產生新版**；v5.10 的 SHA-256 於本輪前後相同（`d7d59ab8a9c965e9c9a0ed96d7e5a6ba820fbb90adedd146a3542b0ba979497f`）。`builder/`、`model/` 無變動。
- 新增 `tools/stage0_inventory.py`（可重跑的盤點與影響範圍工具，不在 CI）與盤點檔 `docs/reports/20261002_stage0_inventory.xlsx`；詳見 `docs/reports/20261002_stage0_inventory.md`。
- 網站：Block 5 任務表改以 `st.table` 呈現（表頭與標籤自動換行），1280 px 下 5 個任務欄全部可見、無橫向捲動；只改呈現，不改數值。截圖在 `docs/reports/img/`。
- 總覽頁崩潰修正（第 9 輪遺留）：v5.10 新增的 10 個名稱（`IF_CostAttVR_*`、`IF_HzEff_*`、`IF_FrontSuccVR*`、`IF_PFloor`）未列入 Block 5 名稱，總覽頁把它們當 Block 1 的 15 欄名稱而崩潰；`app/common.py` 名稱前綴補 4 個，`tests/app` 兩處期望值同步（任務表改 `at.table`、推導鏈 8 步），12 項全過。不涉及任何數值。
- CHANGELOG：v5.10 條目補上 PR #9 合併提交雜湊 `fcbb384`。

## 20261002_Tokenomics_v5.10.xlsx（取代 v5.9；第 9 輪）

- Commit：`fcbb384`（第 9 輪 PR #9 合併提交）。v5.9 的合併提交為 `7627a82`（第 8 輪 PR #8）。
- Excel（M1 可靠度下限）：公式 20,686 → 20,780（+94）；具名範圍 294 → 305（新增 11、無移除）：`B5_PFloor`（Har_In!C8，p_min 輸入）；Interface E 節末尾新增 `IF_CostAttVR_{Luna,Sol,Astra}`（每次嘗試成本）、`IF_HzEff_{Luna,Sol,Astra}`（有效時間範圍）、`IF_PFloor`（單格）、`IF_FrontSuccVR`、`IF_FrontSuccVRName`、`IF_FrontSuccVRP`（前緣，5 欄；無合格時為文字「無合格」）。分類計數：`IF_` 167（`IF_Hdr` 3；下游 154 → 164）、`B4_` 39、`B5_` 24、`TR_` 23、`CAL_` 19、`DRV_` 16、`TRN_` 15、`CTL_` 2。
- 差異：v5.9 → v5.10 以 LibreOffice 重算後共 157 格不同，只在 Har_In 5、Harness 68、Interface 66、Checks 15、README 3；其餘工作表逐格一致；工作表清單不變。Interface E 節既有列位置不變。
- builder：依 `docs/builder/Tokenomics_builder_v5.md` 還原；`block5.py`、`finish.py`、`build.py` 有變動，其餘 8 檔與 md 逐字相同且未變。以 v5.9、v5.10 為底稿重建，LibreOffice 重算後皆與 repo 的 v5.10 逐格一致（27,334 格不符 0、錯誤 0）；`restore_log` 未對應 0（以 v5.9 為底稿：藍字輸入 1,151 全數對應；以 v5.10 為底稿：1,152）。
- 測試：期望值改為 20,780 格、305 個具名範圍（顯示用 139、下游 164、`B5_` 24）；Interface E 節形狀檢查納入新增 10 個下游名稱（`IF_FrontSuccVR`、`IF_FrontSuccVRP` 接受數值或「無合格」）；情境 13 → 15（新增 `floor_0`、`floor_80`，皆以 `B5_PFloor` 設定）；新增期望值測試（基準前緣組合；`floor_0` 前緣＝「對照（不設下限）」列、Coding agent＝Luna｜選定；`floor_80` Coding agent 全為「無合格」、Checks 無合格任務數＝1）。無新增 Excel 函數。parity 比對維持嚴格。
- 網站：Block 5 推導鏈新增「每次嘗試成本（$）」（`IF_CostAttVR_*`），時間範圍改顯示有效值（`IF_HzEff_*`）並以 `B5_H50` 為對照列，成功率依單位顯示為百分比；新增「成功任務成本前緣（VR200）」表（`IF_PFloor`、`IF_FrontSuccVR*`，「無合格」原樣顯示，不在網站重算）；Block 4 的「攤提 $/M 對照」圖只放四種攤提口徑，兩條全成本序列移到另一張圖。
- 檔案：v5.9 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.10。
- CHANGELOG：補上 v5.8（`e59bf4f`）、v5.9（`7627a82`）的雜湊。

## 20261001_Tokenomics_v5.9.xlsx（取代 v5.8；第 8 輪）

- Commit：`7627a82`（第 8 輪 PR #8 合併提交）。v5.8 的合併提交為 `e59bf4f`（第 7 輪 PR #7）。
- Excel：公式 18,596 → 20,686；具名範圍 228 → 294（新增 67、移除 1）：`IF_` 115 → 157（`IF_Hdr` 3；下游 113 → 154，新增 41）、`B4_` 38 → 39、新增 `B5_` 23；`B4_Chi` 改名 `B4_CacheHit`，新增 `B4_MktChina`；新增 3 個工作表 Har_In、Harness、Sens_Har（Block 5：harness、任務層成功率與每成功任務成本）；`DB_Evidence` 15 → 20 筆。
- 名稱異動：v5.8 與 v5.9 共有的 227 個名稱，值（LibreOffice 重算後逐格）全部相同，只有 `TR_Acts`、`TR_HookName`、`TR_Source`、`TR_Trigger` 的 T12／H_HAR 文字不同（`Interface` 列序因新增列而移動，位址以具名範圍為準）；`Interface` D 節新增 K6 下游預設 (c)（`IF_AmortDefault_*`、`IF_FullCostDefault_*`）、(d)（`IF_AmortRev_*`）與機隊三層級貢獻（`IF_RevGWFleet_*`、`IF_RevGWFleetFront_*`）；新增 E 節（任務層 5 欄，表頭 `IF_HdrTask`）。
- builder：依 `docs/builder/Tokenomics_builder_v5.md` 還原（新增 `block5.py`；`outputs.py`、`block4.py`、`training.py`、`finish.py`、`preserve.py`、`build.py` 有變動；`common.py`、`inputs.py`、`calib.py`、`perf.py` 與 md 逐字相同且未變）。以 v5.8、v5.9 為底稿重建，LibreOffice 重算後皆與 v5.9 逐格一致（27,190 格不符 0、錯誤 0）；`restore_log` 未對應 0（以 v5.9 為底稿：藍字輸入 1,151 全數對應）。
- 測試：期望值改為 20,686 格、294 個具名範圍（顯示用 138、下游 154、`B4_` 39、`B5_` 23）；Interface D／E 形狀檢查（單格、15 欄、5 欄任務分開）；v5.9 新增的 41 個下游名稱逐一檢查；情境 11 → 13（新增 `harness_w1`、`harness_p3`）；函數語意新增 AVERAGE、OR；**parity 比對改回嚴格**（情境 b、f 的 SLO 不可達錯誤已於 Excel 端消除；任何情境出現錯誤值，或兩邊錯誤代碼不同，皆失敗）。
- 網站：Block 4 頁 K6 改顯示下游預設 (c)，自下而上、由上而下、(d)、全成本（自下而上口徑）列為對照；機隊列改為三層級貢獻＋合計；中國廠商標記改讀 `B4_MktChina`（刪除 `CN_COUNTRY` 字串判斷）；新增 Block 5 頁（只讀 Interface E 節與 `IF_HdrTask`）；總覽排除 Block 5 名稱；README 補 `B5_`。

## 20261001_Tokenomics_v5.8.xlsx（取代 v5.7；第 7 輪）

- Commit：`e59bf4f`（第 7 輪 PR #7 合併提交）。
- Excel：公式 16,251 → 18,596；具名範圍 144 → 228（新增 84：`B4_` 38 個、`IF_` 46 個）；新增 8 個工作表 Cap_In、Capability、Price_Frontier、Cache_Store、Fleet_1GW、Amortize、Theory_Rev、Sens_Rev（Block 4：單價前緣、快取儲存、1 GW 參考機隊、訓練攤提、理論營收）；`DB_Evidence` 9 → 15 筆。
- 名稱分類（程式計數）：`IF_` 115（`IF_Hdr` 2、下游可連結 113；v5.7 為 67，本版新增 46）、`B4_` 38（顯示或內部用，下游不得連結）、`TR_` 23、`CAL_` 19、`DRV_` 16、`TRN_` 15、`CTL_` 2；`DRV_`、`CAL_`、`TRN_`、`TR_` 數量不變。
- builder：依 `docs/builder/Tokenomics_builder_v5.md` 寫入 `builder/`（新增 `block4.py`；`build.py`、`finish.py`、`preserve.py` 有變動；其餘 6 檔與 md 逐字相同）。以 v5.7 為底稿重建、以 v5.8 為底稿重建，LibreOffice 重算後皆與 v5.8 逐格一致（24,093 格不符 0、錯誤 0）；`restore_log` 未對應 0。
- 測試：期望值改為 18,596 格、228 個具名範圍；新增 Interface D 節形狀檢查（單格與 15 欄分開）、`B4_` 分類檢查；情境 7 → 11（新增 `B4_Disc`、`B4_PeakMode`、`B4_Eps`＋`B4_CompMult`、`B4_MktIndex[6]`，輸入一律用具名範圍）；函數語意新增 MATCH、COUNTIF 文字條件、一列範圍 INDEX、IF 文字＋ISNUMBER、CHOOSE、EXP(ε*LN(x))、公式內具名範圍。每個情境加防空轉檢查（改變格數與 Interface 格數寫入統計）。
- 引擎：`engine/core.py` 新增 pycel 與 openpyxl 3.1 的具名範圍讀取相容轉接（公式內使用具名範圍時需要；只改名稱目的地的讀法，不涉計算）；新增情境輸入鍵 `NAME`／`NAME[k]`。
- parity 比對：兩邊都是錯誤值、僅錯誤代碼不同（引擎 `#VALUE!`、LibreOffice `#DIV/0!`）者單獨列帳、不計入不符；詳見 `docs/reports/20261001_v5.8_sync.md`。
- 網站：新增「Block 4」頁（層級、世代、成本情境選擇器；單價表、市場候選表、理論營收（理想上限）、成本與攤提兩種口徑並列、推導鏈）；總覽頁排除 Block 4 名稱；README 補 `B4_` 說明。
- 檔案：v5.7 以 `git mv` 移入 `model/archive/`；`model/CURRENT` 改為 v5.8。
- CI：timeout 30 → 60 分鐘（11 個情境各建一次引擎，全套約 25 分鐘）。

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

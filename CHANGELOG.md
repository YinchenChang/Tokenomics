# CHANGELOG

每次同步 Excel 新版本記錄：Excel 版本、commit、變動摘要。

## 20261006_Tokenomics_v5.22.xlsx（取代 v5.21；X7 壽命期價格係數 L、變現率 m 並列輸出；X8 補充；X9 Q2 第二來源；CI 工程兩項；判斷類＋工程類，依工作單 `docs/workorders/20261006_v5.22.md` r4 執行）

- Commit：合併雜湊 `a5931f0`（PR #23）；分支 `claude/new-session-mtq0pj`。報告：`docs/reports/20261006_v5.22.md`。底稿：master `4b70496`（含 v5.21 合併 `fef9bfd`）；`model/CURRENT` 原為 v5.21。
- Excel（CC 以 `builder/` 自 v5.21 產生，經 LibreOffice 重算存檔）：**X7** 新輸入格 `CTL_PriceLife`（L）與 `CTL_Monetize`（m）（Cap_In!C63、C64，基準 1，藍字，Gov_Map GM593／GM594，區間 0.3–1.0，P 欄＝高）；Theory_Rev D 節新增四列 _Life（第 90–93 列）與自我檢查旗標（第 96–99 列）；Interface H 節（第 212–216 列）新增 `IF_RevGW_Luna／Sol／Astra_Life`、`IF_RevGWFleet_Life`（＝基準列 × L × m；文字列輸出相同文字）；Checks Y 節 X7（ERROR，計入 GOV_Errors）。既有 IF_RevGW_*、IF_RevGWFleet、L1 與 `_Prod` 列公式與數值逐格不變。**X8 補充** DB_Evidence E246（產業租金指數，L 的 Analogy 證據，摘要級、原文未讀；不新增任何 SRC 紀錄）。**X9 Q2** SRC_Perf 第 056–059 與 052–055 互填第二來源（R 欄）、備註欄附加說明。Decisions 新增 X7、X8、X9。
- 敏感度（只報告，不改模型）：Perf_Batch 側 VR200 效率 k＝0.70／0.75／0.84 的唯讀對照見報告第 3 節；任一 Interface 輸出變動 ≥ 10% 已列入「待 Project 判斷」。
- builder：新增 `v522.py`（版本字串的唯一來源）；`build.py`、`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v522.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生。
- 工程類（CI）：(1) `engine/core.py` 快取指紋的 Python 欄只比對主、次版號（修正 PR #22 run 177／178 因 runner 映像修訂號不同〔3.11.16 ≠ 3.11.17〕而在 `test_cache_matches_fresh` 失敗）；(2) 新 job `ci-status`（`parity.yml` 末尾）與 `tools/ci_status.py`：把每次 run 的結果寫進孤立分支 `ci-status`（`<sha>/<run_number>-a<attempt>-<event>.json`），`on.push` 加 `branches-ignore: [ci-status]`，scenario-guard 加上傳 `junit-scenario-guard`；合併門檻 `parity` 不變。
- 測試：期望值 `formula_cells` 38,989 → 39,198、`defined_names` 896 → 902、`downstream_names` 178 → 182、`GOV_Warnings` 217 → 209；新增情境 `h_price_life_050`、`test_price_life_expected_values`、`tests/parity/test_ci_status.py`（6 項，只用 fixture）。既有情境與期望值未動。
- 治理：GOV_Errors 0、GOV_Warnings 209（W1 209＋W2 0＋H3 0；W1 −8）、GOV_Info 107（不變）。

## 20261006_Tokenomics_v5.21.xlsx（取代 v5.20；X6：X4 結案、MLPerf v6.1 一手結果寫入；判斷類＋工程小項，依工作單 `docs/workorders/20261006_v5.21.md` r1 執行）

- Commit：合併雜湊 `fef9bfd`（PR #22）；分支 `claude/new-session-by13ws`。報告：`docs/reports/20261006_v5.21.md`。底稿：master `6c2bc89`（含 v5.20 合併 `0b4808e`）；`model/CURRENT` 原為 v5.20。
- Excel：**X6** 一手來源 MLCommons `inference_results_v6.1/summary.csv`（repo HEAD `4bb63cd`，SHA-256 `87980a2d…065a`，CC 已讀並逐列核對）。SRC_Perf：`SRC_PERF_027`／`028` 由 2 級二手升為 1 級一手（已讀）；新增 `SRC_PERF_052`–`059`（Nebius VR200／GB300 的 Offline、Server 各 2 筆，NVIDIA Vera Rubin／GB300 的 Offline、Server 各 2 筆；1 級、利害關係方、不連結任何模型格）。DB_Evidence 新增 E245（取代 E244，連 GM344）；Gov_Map GM344 理由欄加註；Decisions 新增 X6、X4 狀態改「v5.21 結案（X6）」。Calib F67 維持 1.0／0.5–1.5。`Alloc_In!G7` 備註補「；區間 0–6（v5.20 X3）」。SRC_ 具名範圍 335 → 343、公式格 38,933 → 38,989、具名範圍 888 → 896。Interface、L1、所有模型頁數值逐格不變。
- builder：新增 `v521.py`（版本字串的唯一來源，`finish.py` 的 README!A1／B5 改讀它）；`gov.py`、`build.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v521.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生。以 v5.21 重建冪等 0 不符。
- 測試：期望值 `formula_cells` 38,933 → 38,989、`defined_names` 888 → 896、`src_names` 335 → 343、`GOV_Warnings` 209 → 217；新增 `test_readme_version_consistency`（README!A1 版本號、README!B5 檔名、`model/CURRENT` 三者一致）。
- 治理：GOV_Errors 0、GOV_Warnings 217（W1 217＋W2 0；較 v5.20 +8，為新增 8 筆利害關係方 Active 紀錄的第二來源欄依規則留空）、GOV_Info 107。

## 20261006_Tokenomics_v5.20.xlsx（取代 v5.19；X3 新高段 8 列補齊、X4 F67 衝突證據、X5 攤提耦合註記；判斷類，依工作單 `docs/workorders/20261006_v5.20.md` r1 執行）

- Commit：合併雜湊 `0b4808e`（PR #21）；分支 `claude/affectionate-euler-bdacy2`。報告：`docs/reports/20261006_v5.20.md`。底稿：master `f02d418`；`model/CURRENT` 原為 v5.19。v5.19 合併雜湊 `ef9a12e`（PR #20）。
- Excel：**X3** DB_Evidence E236–E243（Analogy、摘要級、原文未讀）；Gov_Map GM205／203／459／270／290／578 判 6.2 齊備、GM275／354 為「已搜尋、無可比對象」；`Alloc_In!E7`（AL_Nrefresh_Hi）4 → 6，GM578 區間文字更新；Decisions 新增 X3，C2 追加 GM275／GM354。**X4** DB_Evidence E244、GM344 理由欄加註（F67 數值與區間不改）。**X5** Interface A3 與 README 新列加註攤提耦合。Alloc G 節 N_refresh 高端列連動（Q1 0.693→0.747、Q2 0.718→0.769、RDGW 0.117→0.153）；L1 數值逐格不變。
- builder：新增 `v520.py`；`gov.py`、`finish.py`、`build.py` 接上；`docs/builder/Tokenomics_builder_v5.md` 重新產生。`docs/stage2_source_check_rules.md` 同步 C2 列名。
- 治理：GOV_Errors 0、GOV_Warnings 209（W1 209＋W2 0）、GOV_Info 107（不變）。

## 20261006_Tokenomics_v5.19.xlsx（取代 v5.18；X1 生產折減並列輸出、X2 P 欄升段；判斷類，依工作單 `docs/workorders/20261006_v5.19.md` r1 執行）

- Commit：合併雜湊 `ef9a12e`（PR #20）；分支 `claude/ecstatic-galileo-ue0ggt`。報告：`docs/reports/20261006_v5.19.md`。底稿：master `a9adc7a`；`model/CURRENT` 原為 v5.18。
- Excel（CC 以 `builder/` 自 v5.18 產生，經 LibreOffice 重算存檔）：**X1** 新輸入格 `CTL_ProdDerate`（Serving!C28，0.85，情境值）；8 個 `*_Prod` 鏡像頁（Perf、Perf_Batch、Training、Unit_Cost、Interface、Fleet_1GW、Amortize、Theory_Rev；從 Serving!C18 進入模型的兩處起到 Theory_Rev 七個輸出列，1,575 格，同位置鏡像，右側 S:AG 為檢查副本）；Interface G 節七列 `IF_FullCost_*_Prod`、`IF_RevGW_*_Prod`、`IF_RevGWFleet_Prod`；Checks X 節 X1（計入 GOV_Errors）。Serving!C18 維持 1.0（G0-11）。**X2** Gov_Map P 欄 11 格升為高段（GM205、586、578、104、270、459、275、304、290、203、354），新增 Gov_Map GM592（CTL_ProdDerate）。Decisions 新增 X1、X2。公式格 34,593 → 38,933（+12.6%）、具名範圍 880 → 888、工作表 48 → 56。
- builder：新增 `v519.py`（鏈由活頁簿公式於建置時自動求出：Serving!C18 讀取格的前向相依 ∩ 七個輸出列的後向相依）；`gov.py`、`build.py`、`inputs.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v519.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生。以 v5.19 重建冪等 0 不符。
- 測試：期望值 34,593 → 38,933 格、880 → 888 名稱、`downstream_names` 171 → 178、sheets 48 → 56；新增情境 `h_prod_derate_070` 與 `test_prod_derate_expected_values`。既有情境與期望值未動。
- 其他：`docs/reports/20261005_v5.18.md` 第七節第 4 項證據編號 E212 → E213；`docs/reports/20261006_v5.19_查核.xlsx`（第 3 節唯讀查核，不入 DB_Evidence）。
- 治理：GOV_Errors 0、GOV_Warnings 209、GOV_Info 107（不變）。

## 20261005_Tokenomics_v5.18.xlsx（取代 v5.17；Stage 2 第一批寫入；判斷類，依工作單 `docs/workorders/20261005_v5.18.md` r3 執行）

- Commit：合併雜湊 `a9adc7a`（PR #19）。報告：`docs/reports/20261005_v5.18.md`。底稿：master `efe1765`（含 PR #18 合併 `5b8dc44`）；`model/CURRENT` 原為 v5.17。**依 r3**（r2 開工後改 r3：G4 低改 7.8、F13 維持 9.1；D5 只改 Serving D23、E23 高值）。
- Excel（CC 以 `builder/` 自 v5.17 產生，經 LibreOffice 重算存檔）：SRC 等級依 S1 (a)、G15、H1 規則寫入並登錄 DB_Evidence E170–E226；新增 SRC_HW_061–064、SRC_MOD_054（SRC_ 名稱 330 → 335，具名範圍 875 → 880）；`Train_In!C44`、`Calib!C69` 改公式；SRC_PERF_009／010 改為內插值；`Spec_Rack` 的 VR200（F8、F11、F12）、GB200（D9）、GB300（E9、E10）機架功率與價格、Rubin Ultra 欄（單架 72 封裝）；`Arch!D16`（SRC_MOD_054）、`Train_In!C21`、`Checks!I46`；Gov_Map P 欄改 B 法「O＋L1」分段；Checks 第 21 列改述；Decisions 新增 S1、S2、H1、G15、C1。W2 33 → 3。
- builder：新增 `v518.py`（舊值守衛寫入、步驟開關 `V518_STEPS`）、`gov_seed4.py`（由 `tools/gen_seed_v518.py` 產生）；`gov.py`、`build.py`、`block4.py`、`finish.py`、`inputs.py`、`training.py` 接上；`docs/builder/Tokenomics_builder_v5.md` 重新產生（19 個檔）。以 v5.17 重建 `restore_log` matched 970／Excel 值保留 0／unmatched 0；冪等（以 v5.18 重建）公式文字與數值不符 0。
- 測試：期望值 34,552 → 34,590 格、875 → 880 名稱、`src_names` 330 → 335；`test_parity.py` 內依 Excel 輸出的硬編期望值改為 v5.18 的 LibreOffice 重算值（`IF_FrontSuccVR`、`AL_*`、`IF_Alloc*`、`L1_Ans5_*`、`L1_Ans6_GPUh`、`L1_Ans8`、GOV_Warnings 241 → 212、GOV_Info 103 → 107）。情境、比對範圍、容差未動。
- 工程類修正（工作單外，報告表 2 列出）：`gov.py` 的 L1 四列 RevGW 的 E、F 公式改為 `INDEX(…)*(Sens_Rev!$B$6/IF_Util)` 形式（8 格；數學相同、差 ≤1e-15），修正情境 `e_util_08` 下 Checks H3 因 1 ulp 平手使引擎與 LibreOffice 不一致（v5.16 起的潛在缺口）。
- CI：`parity.yml` 的 structure-recalc 摘要步驟改 `| tee -a "$GITHUB_STEP_SUMMARY"`，兩個重算秒數同時出現在 job 日誌。
- 規則：查核紀錄規則（R5／R6 網址須為摘要實際所在頁面）寫入 `docs/stage2_source_check_rules.md`（CLAUDE.md 屬 Project 端維護）。
- 治理：GOV_Errors 0、GOV_Warnings 209（W1 209＋W2 0）、GOV_Info 107。

## 20261005_Tokenomics_v5.17.xlsx（取代 v5.16；收尾小項；工程類，依工作單 `docs/workorders/20261005_v5.17_stage2-1.md` r1 PR A 執行）

- Commit：合併雜湊 `1b36811`（PR #17）。報告：`docs/reports/20261005_v5.17.md`。底稿：master `0fe187f`（含 `f2b3492`）。
- Excel（CC 以 `builder/` 自 v5.16 產生，經 LibreOffice 重算存檔）：僅 `L1!I43`（L1_Ans7 讀法欄文字，A1）與 `README!B5`（版本文字）兩格不同。數值、公式、具名範圍（875）、工作表（48）逐格不變。
- builder：`block6.py`（`l1_rows_b6` 第 7 題讀法文字）、`finish.py`（README）；`docs/builder/Tokenomics_builder_v5.md` 重新產生。以 v5.16 重建 `restore_log` matched 970／Excel 值保留 0／unmatched 0；冪等（以 v5.17 重建）公式文字與數值不符 0。
- 測試與 CI：`scenarios.yaml` 的 `l1_names` 註解更正（A2；值 141 不變）；新增 `chk_names: 1` 與對應斷言（A5）；刪除 `test_l1_v516_expected_values_and_h3` 中重複的 `L1_Ans5_GM` 斷言（A3）；增量重算秒數（最大值、所屬情境、中位數）寫入 `results_store`，`tools/ci_summary.py` 的摘要同時輸出全簿與增量兩個秒數（A6；門檻與斷言不變）。本機受影響子集一律先以 `tools/build_engine_cache.py` 建快取並設 `TOKENOMICS_ENGINE_CACHE`（A4）。
- 治理：GOV_Errors 0、GOV_Warnings 241、GOV_Info 103（不變）。

## 20261004_Tokenomics_v5.16.xlsx（取代 v5.15；L1 Answers 修正；判斷類，依工作單 `docs/workorders/20261004_v5.16.md` r1 執行）

- Commit：合併雜湊 `f2b3492`（PR #16）。報告：`docs/reports/20261004_v5.16.md`。**依賴 PR #15**（底稿為 PR #15 分支 `claude/dreamy-fermat-x5o30w` 最新提交 `86dd4bc`，其上併入 master 的工作單提交；PR #15 合併後本 PR 併入 master）。
- Excel（CC 以 `builder/` 自 v5.15 產生，經 LibreOffice 重算存檔）：L1 第 41–44 列改公式與標籤（毛利率移出、第 6 題 FLOPs 口徑、第 7 題比值、第 8 題改連 `IF_HarR_Sol`）；新增第 49–51 列 `L1_Ans5_GM`、`L1_Ans5_FullMargin`、`L1_Ans6_GPUh`；L1 欄位約定寫入說明；Checks 新增 H3（WARN，計入 `GOV_Warnings`）。公式格 34,534 → 34,552；具名範圍 865 → 875（L1_ 132 → 141；另加 CHK_L1Order）；工作表 48 不變。模型頁、Interface、SRC、Gov_Map 數值與公式逐格不變。
- builder：`block6.py`（`l1_rows_b6`、`checks_h`）、`finish.py`（README）；`docs/builder/Tokenomics_builder_v5.md` 重新產生。以 v5.15 重建 `restore_log` matched 970／Excel 值保留 0／unmatched 0；冪等（以 v5.16 重建）0 不符。
- 測試：期望值 34,534 → 34,552 格、865 → 875 名稱、`l1_names` 132 → 141；網站 L1 44 → 47 列、問答頁 9 → 12 個小標題；新增 `test_l1_v516_expected_values_and_h3`。情境、比對範圍、容差、斷言未動。
- 治理：GOV_Errors 0、GOV_Warnings 241（不變；H3＝0）、GOV_Info 102 → 103（I3 +1：毛利率對 2025 隱含值）。

## 20261004_Tokenomics_v5.15.xlsx（取代 v5.14；Block 6 Alloc；判斷類，依工作單 `docs/workorders/20261004_v5.15.md` r3 執行）

- Commit：見本輪 PR（合併後補上雜湊）。報告：`docs/reports/20261004_v5.15.md`。底稿：master `7402b3e`（含 PR #13、#14）。
- Excel（CC 以 `builder/` 自 v5.14 產生，經 LibreOffice 重算存檔）：新增 `Alloc_In`（輸入）與 `Alloc`（推導）；Interface F 節新增 `IF_AllocQ1`、`IF_AllocQ1_R2`、`IF_AllocQ2`、`IF_AllocServeGW`、`IF_AllocRDGW`、`IF_AllocDemand`、`IF_AllocImpliedNk`；L1 新增 Answers 9 題與外部對照 3 列；SRC_Demand 新增 SRC_DEM_010–013；DB_Evidence 新增 E166–E169；Decisions 新增 A9、A10，A1–A8 狀態改「v5.15 已建」；Checks 新增 H 節（計入 GOV_Errors）。公式格 33,480 → 34,534；具名範圍 736 → 865；工作表 46 → 48。既有模型頁、Interface 既有列、既有 L1 列數值逐格不變。
- 工單更正：W1 支出路線服務 GW 不乘 1e9；W2 改版計畫取 Training 第 104 列。補充 2：服務世代組合加 Hopper 欄；新增情境 `h_alloc_mix_2025`。
- builder：新增 `block6.py`、`gov_seed3.py`；`build.py`、`gov.py`、`preserve.py`、`finish.py` 接上；`docs/builder/Tokenomics_builder_v5.md` 重新產生（`tools/gen_builder_md.py`）。以 v5.14 重建 `restore_log` matched 936／Excel 值保留 0／unmatched 0；冪等（以 v5.15 重建）0 不符。
- 測試：期望值 33,480 → 34,534 格、736 → 865 名稱（新增 `al_names` 80）、`downstream_names` 164 → 171、`src_names` 324 → 330、`l1_names` 96 → 132、工作表 46 → 48；新增情境 `h_alloc_no_refresh`、`h_alloc_k_high`、`h_alloc_tok_high`、`h_alloc_growth`、`h_alloc_mix_2025`（共 23 個含基準）；新增 `test_alloc_expected_values_and_slo_text`、`test_alloc_mix_2025_expected_values`；`test_cache_matches_fresh` 的具名範圍比對加型別檢查。網站新增 Alloc 與問答頁。`tools/export_csv.py` 的 Interface 匯出範圍 200 → 300 列。
- 治理：GOV_Errors 0、GOV_Warnings 238 → 241、GOV_Info 99 → 102。

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

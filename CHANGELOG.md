# CHANGELOG

每次同步 Excel 新版本記錄：Excel 版本、commit、變動摘要。

## 20261017_Tokenomics_v15.1.xlsx（取代 v15.0；**次版：只改文字、標籤、Decisions 與帳本，具名範圍值不變**；依工作單 `docs/workorders/20261017_v15.1_結案收尾.md`）

- 分支 `claude/v15-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_v15.1_結案收尾.md`；進度檔：`docs/reports/20261017_v15.1_進度.md`。
- Excel（CC 以 `builder/v1510.py` 自 v15.0 產生，經 LibreOffice 重算存檔）：
  - U1（修訂九更正，原文逐字保留）：SL46-20 的 Alloc_In C15「區間已涵蓋」更正（SL46-25）；Alloc 第 398 列還原 v14.2 原文（SL46-26）；Calib D67:G67 補決策（SL46-27）；Alloc_In C16 token／支出口徑說明（SL46-28）。
  - U2：17 列補 O12 口徑標籤（SL46-29）；Spec_Rack G26、D41、Har_In C48:E48 列入刻意保留清單（SL46-30，含 Harness 126／129／132）；Sens_Rev A17 標籤改隨 CST_Eps，基準顯示文字不變（SL46-31）。
  - 具名範圍：增減 0；值差異只有 `RNG_Version`、`RNG_Current`（版本字串）。GOV 0／280／182。
- 測試：契約快照 v15.1（名稱 822 → 826，新增的 4 個名稱 v15.0 簿內已存在、值相同，因契約文件提及而納入快照）；`scenarios.yaml` formula_cells 52,225 → 52,226（Sens_Rev A17 變公式）；新增 `tests/parity/test_v1510.py`。
- 帳本：`docs/reports/20261017_稽核結案對帳_v15.1.md` 與明細（逐單元重判，未處理 0；高嚴重度輸入格仍有 98／146 標 Assumed 且無 SRC）。
- 工程修正：`tools/gen_builder_md.py` 的順序表補上 `v1500.py`（v15.0 的 builder md 漏列）與 `v1510.py`。

## 20261017_Tokenomics_v15.0.xlsx（取代 v14.2；**主版：契約改變，新增 32 個名稱**；稽核結案，依工作單 `docs/workorders/20261017_v14.3_稽核結案.md` r1）

- 分支 `claude/v14-3`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_v14.3_稽核結案.md`；進度檔：`docs/reports/20261017_v14.3_進度.md`。底稿：master（v14.2，`0e8f3c5`）。版號判定：O13 與 T3-2 新增 `RNG_*`、B11 新增 `IF_FrontSuccVRQual`，依 CLAUDE.md 第 4 節為契約改變 → 主版 v15.0（工作單以 v14.3 暫稱）。
- Excel（CC 以 `builder/v1500.py` 自 v14.2 產生，經 LibreOffice 重算存檔）：
  - O13：`SRC_DEM_004_Lo`／`_Hi` 以公式接進支出路線（Alloc Q 節）：新增 `RNG_Dem004_IF_AllocServeGW／IF_AllocQ1／IF_AllocQ2` 的 `_Lo`／`_Hi` 與 `RNG_Dem004_OutCount`（7 個名稱）；Checks RG4。基準值不變。
  - T3-2（O4）：VR200 批次倍數區間 0.70–1.0；只經 VR200 欄的 12 個名稱各補 `RNG_<名稱>_Lo`／`_Hi`（24 個名稱）；既有 59 個名稱的端點逐值不變；指紋 591 → 604 葉。
  - B11：`IF_FrontSuccVRQual`（Interface 第 193 列）。
  - O14：L1 第 31、59–65 列外部對照換算成模型單位（D 欄基準不變）；新增 `SRC_PRC_047`；第 35 列只加註。
  - O9：V16 標恆等式（非驗證）：`CHK_VerifyTotal`／`Pass` 22／14 → 21／13。
  - O15：B20 口徑標註、Y9 敏感度端點（Sens_Train 第 13 列 0.18／0.35；Sens_Rev 折扣連結 Cap_In）、F16 註記；其餘小項刻意保留（Decisions SL46-07）。
  - O20：Alloc_In κ 推導區塊（顯示用，`AL_Kappa` 不變）＋Checks KP1／KP2；O6：SRC_Index 哨兵列 B 欄改公式；O8／O12 標籤；T3-1（O5）：SRC_PERF_060 來源登錄更正（修訂九，值 556 與 V1 判定不變）。
  - Decisions 新增 SL46-01…24。
- 測試：契約快照 `contract_snapshot_v14.2.json` → `contract_snapshot_v15.0.json`（789 → 822 個名稱）；新增 `tests/parity/test_v1500.py`（O13、B11、T3-2、O5、O9、O14、O20、Decisions）與情境 `batch_vr200_lo`／`batch_vr200_hi`；`test_v1300_ranges_equal_scenarios` 加入 VR200 區間名單與端點核對（原 59 個名稱／647 格的斷言不變）；期望值隨預期變動更新（公式格數、名稱數、驗證計數 21／13／7／1、GOV_Info 182），逐項見報告。
- `docs/plan/Tokenomics_downstream_contract.md` v0.13 → v0.14（v15.0 條目；v13.0 條目附更正，原字樣保留）。`docs/builder/Tokenomics_builder_v5.md` 已重產。

## 20261017_Tokenomics_v14.2.xlsx（取代 v14.1；次版：無新增契約名稱；v14.2 修補，依工作單 `docs/workorders/20261017_v14.2修補.md` r0）

- 分支 `claude/v14-2`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_v14.2修補.md`；進度檔：`docs/reports/20261017_v14.2修補_進度.md`。底稿：master（v14.1，`32dfce0`）。
- Excel（CC 以 `builder/v1420.py` 自 v14.1 產生，經 LibreOffice 重算存檔）：
  - S1：Cap_In 第 285、286 列（`L1_MFleet_P25Lo`／`L1_MFleet_P25Hi`）C／D／E 各欄改為 `MAX(該欄點估計, 該欄同單價下限)`，下限＝營收 ÷（該欄機隊付費 token 上限（第 118 列）× 該列單價）；機制同 v14.1 R1，全部是 Excel 公式。低端欄（D）`L1_MFleet_P25Lo` 0.3535 → 0.4141、`L1_MFleet_P25Hi` 0.1066 → 0.1249；其他欄與 `L1_MFleet` 三端不變。數值變動的契約名稱只有這兩個（這兩個名稱沒有任何下游公式讀取）。
  - S2：Har_In 第 20、32 列 A、B 欄標籤清空（原文記入 Decisions SL45-2；H、I 欄保留）。
  - Decisions 新增 SL45-1…3；區間檔 `builder/v1300_ranges.json` 與指紋檔 `builder/v1310_fingerprint.json` 只更新版本字串（端點與指紋格逐值不變）。
- 測試：契約快照 `contract_snapshot_v14.1.json` → `contract_snapshot_v14.2.json`（789 個名稱不變，值變動 2 個加版本字串）；新增 `tests/parity/test_v1420.py`（S1 專屬：低端欄必須截在同欄同單價下限、不亂截斷、基準欄同樣適用、依賴鏈以外的名稱與 v14.1 逐格相同；S2 逐格斷言）；`test_v1400_q3_floor_and_mfleet_lo_values_unchanged` 改名為 `test_v1400_q3_floor_row121_unchanged_and_mfleet_lo_is_v141_floor`（內容不變）；沒有刪除或放寬任何測試。

## 20261017_Tokenomics_v14.1.xlsx（取代 v14.0；次版：無新增契約名稱；v14.1 修補，依工作單 `docs/workorders/20261017_v14.1修補.md` r1）

- 分支 `claude/v14-1`（PR #106，合併 SHA `ee5ccf7`；v14.2 S3 補記）。報告：`docs/reports/20261017_v14.1修補.md`；進度檔：`docs/reports/20261017_v14.1修補_進度.md`。底稿：master（v14.0，`e7693a3`）。
- Excel（CC 以 `builder/v1410.py` 自 v14.0 產生，經 LibreOffice 重算存檔）：
  - R1：Cap_In 第 119 列（機隊 m）各欄改為 `MAX(該欄點估計, 第 121 列同欄下限)`（Excel 公式，下限截斷）；`L1_MFleet`／`_Lo`／`_Hi` 由 [0.184, 0.407, 1.179] 變 [0.215, 0.407, 1.179]；受影響名稱只有 `L1_MFleet_Lo`、`L1_PriceRealFleet_Lo`、`L1_LReqFleet_Hi`；`RNG_*` 端點、`IF_AllocQ1`／`IF_AllocRDGW` 不變。Cap_In 第 121 列用途標記由「待定義」改為正式定義，不升級為契約名稱。
  - R2：Checks V23、V24 標「恆等式（非驗證）」，移出驗證計數：`CHK_Verify*` 24／16／7／1 → 22／14／7／1。
  - R3：Har_In 第 20、32 列供應商旗標清空；Gov_Map 該兩列加註「v14.1 已移除」，原文保留。
  - R4：v14.0 刪除的 73 列 A、B 欄標籤清空；清單寫入 Decisions SL44-4。
  - R5：Cap_In 24 格（C 欄 23 列＋G175）刪除前以依賴圖確認無外部讀者後清空；原公式寫入 Decisions SL44-5。
  - R6：Gov_Map GM629 註記、三筆用途標記更正（Cap_In 76、Training 122、Price_Frontier 27）、Cap_In 206–209／223 過時錨點文字改為「以現值為準」。
  - Decisions 新增 SL44-1…6；區間檔 `builder/v1300_ranges.json` 與指紋檔 `builder/v1310_fingerprint.json` 只更新版本字串（端點與指紋格逐值不變）。
- 測試：契約快照 `contract_snapshot_v14.0.json` → `contract_snapshot_v14.1.json`（789 個名稱不變，值變動 7 個）；新增 `tests/parity/test_v1410.py`（R1 專屬：低端欄 token 推過上限時 `L1_MFleet_Lo` 必須等於同欄下限；另測不亂截斷、基準欄同樣適用、依賴鏈以外的名稱與 v14.0 逐格相同；R3–R6 逐格斷言）；期望值依預期變動更新；沒有刪除或放寬任何測試。

## 20261017_Tokenomics_v14.0.xlsx（取代 v13.1；主版：新增 18 個契約名稱；4-3 B 段依 A 段建議執行瘦身，依工作單 `docs/workorders/20261017_4-3B.md`）

- 分支 `claude/4-3b`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_4-3B.md`；進度檔：`docs/reports/20261017_4-3B_進度.md`。底稿：master（v13.1，`ab7fca7`）。
- Excel（CC 以 `builder/v1400.py` 自 v13.1 產生，經 LibreOffice 重算存檔）：
  - Q1：刪除 73 列（A 段明細 72 列＋Har_In 第 44 列）共 514 個公式格，只清空數值格、不移動列欄；各列『用途』欄寫刪除註記；移除無人使用的名稱 `B5_TaskTok`、`B5_SelVendor`；Harness A157 刪去供應商專屬一句。公式格 51,610 → 51,439。
  - Q2：新增 18 個契約名稱——Interface M 節 11 個（`IF_TaskTokMult`、`IF_TrainFLOP_`／`IF_TrainInferShare_`／`IF_GMDefault_` × Luna／Sol／Astra、`IF_AmortRevShare`）與 Cap_In 序列 7 個（`L1_MAPI_Ser`、`L1_MSub_Ser`、`L1_MSeat_Ser`、`L1_MImplied_Ser`、`L1_MFleet_Ser`、`L1_MFleet_P25Lo`、`L1_MFleet_P25Hi`）；`IF_GMDefault_*`、`IF_TrainInferShare_*` 補 12 個 `RNG_` 區間名稱。`L1_MFleetFloor` 不升級（Q3 只查明，定義待 Project 判斷）。
  - Q4：Checks 新增 V23–V26（計入驗證項目數）；Checks D104、D140 改讀 Alloc_In C18、C33。`CHK_Verify` 總數／通過／失敗／警示 20／12／7／1 → 24／16／7／1。
  - Q5：用途標記補齊（保留顯示用 155 列＋刪除後新增的死格），無標記死格 0；死格 3,604 → 2,798。
  - 區間檔 `builder/v1300_ranges.json` 與指紋檔 `builder/v1310_fingerprint.json` 依 v14.0 重產（53 → 59 個區間名稱、579 → 591 個指紋格）。
- 變動：既有 `IF_`／`IFW_`／`L1_`／`RNG_` 名稱數值 0 變動；`GOV_Errors`／`GOV_Warnings`／`GOV_Info` ＝ 0／280／184（不變）。
- 測試：契約快照 `contract_snapshot_v13.1.json` → `contract_snapshot_v14.0.json`；新增 `tests/parity/test_v1400.py`（V23–V26、D104／D140 必須失敗測試；既有名稱不變；刪除與名稱檢查）；期望值依預期變動更新（公式格數、名稱數、驗證計數、區間名稱數與格數、指紋格數、`DEAD_BASELINE` 3604 → 2798）；沒有刪除或放寬任何測試。

## 20261017_Tokenomics_v13.1.xlsx（取代 v13.0；次版：無新增契約名稱；D15 來源補齊 B 段＋查核 #96 小項，依工作單 `docs/workorders/20261017_D15_B段.md`）

- 分支 `claude/d15-b`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_D15_B段.md`；進度檔：`docs/reports/20261017_D15_B段_進度.md`。底稿：master（v13.0）。
- Excel（CC 以 `builder/v1310.py` 自 v13.0 產生，經 LibreOffice 重算存檔）：
  - P1：Gov_Map「無來源也無決策」列 312 → 0（J 欄補決策編號、25 格補 H 欄）；Decisions 新增 D15-01…D15-12；新增 SRC_DC_018／019、SRC_PRC_045／046、SRC_HW_069／070（Lenovo 第二來源）；DB_Evidence 106 筆積壓寫入建議判定（新增 E381–E386）；Arch E6–E8 標 Assumed（修訂九更正例外，原文保留）；SRC_PERF_060 標待回查；V1 與 L1_GapPrompt 註記。
  - P2：VR200 欄為點值之註記；區間指紋旗標（Alloc P 節，579 個上游常數格；Checks RG3，計入 `GOV_Warnings`）；v13.0／4-2b-1 報告文字更正；GM346 欄 O 改寫。
- 變動：既有 `IF_`／`IFW_`／`L1_`／`CHK_`／`RNG_` 名稱數值 0 變動；`GOV_Warnings` 282 → 280、`GOV_Info` 182 → 184、`GOV_Errors` 0。
- 測試：契約快照 `contract_snapshot_v13.0.json` → `contract_snapshot_v13.1.json`；新增指紋、舊名稱不變與 P2-2 專屬測試；沒有刪除或放寬任何測試。

## 20261017_Tokenomics_v13.0.xlsx（取代 v12.0；主版：新增契約名稱 `RNG_*` 共 110 個；4-2b-1 K1–K5，依工作單 `docs/workorders/20261017_4-2b.md` 第 1 節）

- 分支 `claude/4-2b-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261017_4-2b-1.md`；進度檔：`docs/reports/20261017_4-2b-1_進度.md`。底稿：master（v12.0）。版號：工作單標題寫 v12.1，因新增契約名稱，依 CLAUDE.md 第 4 節升主版為 v13.0。
- Excel（CC 以 `builder/v1300.py` 自 v12.0 產生，經 LibreOffice 重算存檔）：
  - K1：53 個隨 `CAL_BatchEtaD` GB200／Hopper 倍數變動的契約名稱（`IF_` 41、`L1_` 12，557 格）補區間 `RNG_<名稱>_Lo`／`_Hi`（Alloc O 節）；端點檔 `builder/v1300_ranges.json` 由 `tools/gen_ranges.py` 產生。
  - K2：`RNG_Version`、`RNG_Current`、`RNG_OutCount`、`RNG_StaleFlag`（『一致』／『區間過期』）；Checks RG1、RG2（WARN，計入 `GOV_Warnings`）；parity 新增逐格重算全部端點的測試。
  - K3：Calib C68 的 Gov_Map 類別『倒推』→ Assumed，進 Load_Bearing（57 列）；舊類別與 v12.0 前區間保留於 Gov_Map AL 欄。
  - K4：『Pass＋Fail＋Warn＝Total』標恆等式（非驗證），只改標籤。
  - K5：v12.0 報告追加 2026-10-17 更正（名稱數 5／57／87，「73」為筆誤）。
- 變動：既有 `IF_`／`IFW_`／`L1_`／`CHK_` 名稱數值 0 變動；`GOV_Info` 181 → 182；`LB_Rows`／`LB_LiveCount` 56 → 57。
- 測試：契約快照 `contract_snapshot_v12.0.json` → `contract_snapshot_v13.0.json`（643 → 756 名稱，4,595 → 5,772 格（含因契約文件提及而收錄的 LB_Rows）；快照涵蓋範圍加入 `RNG_*`、`AL_Rng*`）；新增 K1–K4 專屬測試與情境 `batch_corner_x`；期望值更新逐項見報告。

## 20261016_Tokenomics_v12.0.xlsx（取代 v11.0；主版：新增契約名稱 `CHK_SoftCapFail`；v11.1 修補 H1–H7，依工作單 `docs/workorders/20261016_v11.1修補.md`）

- 分支 `claude/v11-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_v11.1修補.md`；進度檔：`docs/reports/20261016_v11.1修補_進度.md`。底稿：master（v11.0）。
- Excel（CC 以 `builder/v1200.py` 自 v11.0 產生，經 LibreOffice 重算存檔）：
  - H1：新增輸入 `CHK_SoftCapFail`＝2（Calib M 節，Assumed，區間 1.5–3）；V1–V3 比值超過它才判失敗，介於 1 與它之間為警示；契約、CHANGELOG、v11.0 報告「未超過上限」的敘述更正。
  - H2：GB200 `CAL_BatchEtaD` 3.04 → 2.36（＝√(1.83×3.04)，區間 1.83–3.04）；V20 標「校準相關（非獨立）」，不計入驗證總數。
  - H3：Hopper 維持 1，標已知低估、無解；Gov_Map 區間 1–3.74。
  - H4：C68 維持 1.5，標 Assumed（無來源，v5.2 建檔以來的整數假設），區間 1.0–1.5；以更正註記與 Decisions 記錄，原文不改。
  - H5：Alloc N 節列出 `IF_AllocRDGW`／`IF_AllocQ1` 的區間（靜態情境值，由測試守住）。
  - H6：契約表頭、Calib H156 區間文字、scenarios.yaml 過時描述更正。
  - H7：V19 由 I/J/L/M 與 CST_MainMin 重算 T 欄並與之比對；V18 標恆等式（非驗證），不計入驗證總數。
- 變動：GB200 欄研發 GW 與訓練鏈名稱隨 2.36 改變；服務端（`IF_TokGW_*`、`L1_MFleet`、`IF_AllocServeGW`）、`L1_LReqFleet_Id`、`L1_HoldEconMW_*` 不變。
- 測試：契約快照 `contract_snapshot_v11.0.json` → `contract_snapshot_v12.0.json`；新增 H1–H7 專屬測試與 7 個情境；期望值更新逐項見報告。

## 20261016_Tokenomics_v11.0.xlsx（取代 v10.3；主版：新增契約名稱 `CHK_VerifyWarn`；大批次修正 G1–G4，依工作單 `docs/workorders/20261016_大批次修正.md`）

- 分支 `claude/bigbatch-fix`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_大批次修正.md`；進度檔：`docs/reports/20261016_大批次修正_進度.md`。底稿：master（v10.3，已確認）。
- Excel（CC 以 `builder/v1100.py` 自 v10.3 產生，經 LibreOffice 重算存檔）：
  - G1：追查 Calib C68（1.5）是否與固定延遲重複計算——無法確認，C68 不改；追查過程與 Decision BB-G1 記入 Decisions。
  - G2：`CAL_BatchEtaD` GB200 1 → 3.04（Calib D156，Derived，區間 1.5–6.7；對 vLLM 10.1K 的 Calib J 複本列比值 1.0007）；Hopper 在 C68＝1.5 下無解，維持 1（待 Project 判斷）。
  - G3：Calib 新增 L 節（V20–V22 驗證點複製列）；Checks 驗證清單新增 V20（MLPerf v6.0 offline GB200 6,752）、V21（GB300 8,987）、V22（TensorRT-LLM H200 1,436）；新增 `SRC_PERF_079–083`、`SRC_HW_067`／`068`。
  - G4：V1–V3 改軟上限（高於 1 但未超過失敗門檻＝警示；v12.0 H1 更正：v11.0 實作沒有失敗門檻，V1–V3 不會失敗），新增 `CHK_VerifyWarn`；`CHK_VerifyTotal`／`Pass`／`Fail`／`Warn` 19／11／8／— → 22／14／7／1。
- 變動：`IF_AllocRDGW` 0.2402 → 0.1973、`IF_AllocQ1` 0.2110 → 0.1801、`L1_ScaleRD` 5.318 → 6.476，GB200 欄成本與訓練鏈名稱隨之改變；`IF_AllocServeGW`、`L1_MFleet`、各世代 `IF_TokGW_*` 不變。公式格 49,490 → 49,696；具名範圍 1,362 → 1,370。
- 測試：期望值更新（逐項舊→新見報告）；契約快照 `contract_snapshot_v10.3.json` → `contract_snapshot_v11.0.json`（637 名稱）；死格基準 3,574 → 3,598（Calib L 節顯示格，已填用途）；未刪除或放寬任何測試。

## 20261016_Tokenomics_v10.3.xlsx（取代 v10.2；次版：第 4 批 4-2a 段，外露寫死參數、重複定義、驗證與契約快照；依工作單 `docs/workorders/20261016_瘦身4-2.md`）

- 分支 `claude/slim-4-2a`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_瘦身4-2a.md`；進度檔：`docs/reports/20261016_瘦身4-2a_進度.md`。底稿：master（v10.2，已確認）。
- Excel（CC 以 `builder/v1030.py` 自 v10.2 產生，經 LibreOffice 重算存檔）：
  - F1：新增輸入 `L1_JudgeTol`（Calib K，0.2）、`SR_RU_PxMultLo`／`SR_RU_PxMultHi`（Spec_Rack，1.5／2.5）；L1 判定欄、Checks I3／E5 與 Spec_Rack G11／G13 改讀這些名稱；Gov_Map 新增 3 列（Assumed 區間）；物理慣例 22 處加註。
  - F2：Sens_Rev B20／B21 改讀 Cap_In 商業壽命區間；Cap_In H10 的 2025 欄 6 格改引用 H 節（值不變）；D10 與現況不符，未執行（待 Project 判斷）。
  - F3：Checks 驗證清單新增 V18（Tech_Registry K 欄＝主流判定）、V19（T 欄一致性）；CHK_VerifyTotal／Pass／Fail 17／9／8 → 19／11／8。不進 GOV_Errors。
  - F4：Calib J 欄 105 格死格、Alloc 27 格、70 個無人讀取輸入加用途標記。
- 不變：所有 `IF_`／`IFW_`／`L1_` 名稱的值（0 格變動）；公式格 49,424 → 49,490；具名範圍 1,359 → 1,362。
- 測試：新增 `tests/parity/test_snapshot.py`、`tests/parity/fixtures/`（契約快照 636 名稱／4,584 格、死格基準）；`test_slim.py` 新增死格用途標記、D08／D09／D11 與外露參數測試，死格基準 3,599 → 3,574。

## 20261016_Tokenomics_v10.2.xlsx（取代 v10.1；次版：η 校準與驗證判準；依工作單 `docs/workorders/20261016_η校準.md`）

- 分支 `claude/eta-calib`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_η校準.md`；進度檔：`docs/reports/20261016_η校準_進度.md`。底稿：master（v10.1，已移至 `model/archive/`）。
- Excel（CC 以 `builder/v1020.py` 自 v10.1 產生，經 LibreOffice 重算存檔）：
  - E1：Calib 新增 J 節（校準與條件對齊複本列）。Hopper 在 DeepSeek profile 條件下無解（EP 通訊項下限使產出上限只有目標的 0.94），GB200 的解（約 3.0）使有效算力高於 GB300 並使 V5 失敗：依停損規則 C67（1.2）、GB200 倍數**未寫入**，列待 Project 判斷。
  - E2：Serving C21:E21 改為 AA 與 OpenRouter 中位數的幾何平均 84.3／43.3／40.8 tok/s/user（SRC_PERF_066–071）；Gov_Map GM239–GM241 改 Derived；新增情境 `slo_v10`（120／65／55）。
  - E3：V2 改 MLPerf v6.0 GB200 NVL72 4,668、V3 改 GB300 72 GPU 機櫃 5,562、V7／V8 條件對齊、V13／V14 加上限 3、新增 V15（DeepSeek 線上服務 1,850）、V16／V17（原 Checks B26／B36）；驗證計數 14／7／7 → 17／9／8。新增 SRC_PERF_066–078、證據 E379、Decisions ETA-*。
  - E4：Perf_Batch R–S 欄標註「只供敏感度情境」，Decisions 記錄 Andy 2026-10-16 18:22 決定 (b)。
- 不變：`IF_AllocServeGW`、`IF_AllocRDGW`、`L1_LReqFleet_Id`、`L1_HoldEconMW_*`、Training 各頁。
- 測試：`tests/parity/scenarios.yaml` 新增情境 `slo_v10`、更新公式格數 49,424、具名範圍 1,359、SRC 名稱 458；`test_parity.py` 驗證計數 17／9／8。

## 20261016_Tokenomics_v10.1.xlsx（取代 v10.0；工程類（CC 執行）：第 4 批 4-1 瘦身，輸出不變；依工作單 `docs/workorders/20261016_瘦身4.md` 第 1 節）

- 分支 `claude/slim-4-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_瘦身4-1.md`；進度檔：`docs/reports/20261016_瘦身4-1_進度.md`。底稿：master（v10.0，已移至 `model/archive/`）。
- Excel（CC 以 `builder/v1010.py`、`v1010_marks.py`、`v1010_text.py`、`v1010_gov.py` 自 v10.0 產生，經 LibreOffice 重算存檔）：
  - 1-a 刪除：Capability 頁（19 公式格）與無人讀取的公式格 136（L1 O 欄 62、Alloc 10、Perf 30、Perf_Batch 34）；Perf／Perf_Batch 速覽列 104–105 清空。Perf_Batch R–S 欄因 Sens_Train W59:X62 仍讀取而保留（列入待 Project 判斷）。
  - 1-b 標記：23 頁「用途」欄 288 列（1,305 格）、情境格黃底 55 格、NonNV 與 Theory_Rev_Prod 頁首註記。
  - 1-c 文字：26 格過時說明改為引用現值、標籤與契約文字修正、README 名稱數。
  - 1-d Gov_Map：重複登錄與標籤整理；新增 GM681（Alloc I94:L95）。
  - 1-e 新增常設檢查 `tests/parity/test_slim.py`（10 項）。
- 公式格 49,241 → 49,127；具名範圍 1,346 不變；既有具名範圍與契約名稱數值變動 0。
- 驗收：LibreOffice 重算錯誤 0；restore_log unmatched 0；冪等差異 0。
- `docs/builder/Tokenomics_builder_v5.md` 已重新產生。

## 20261016_Tokenomics_v10.0.xlsx（取代 v9.0；主版：新增名稱與驗證計數，契約改變，既有 `IF_`／`IFW_`／`L1_` 名稱數值不變；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` 6r1 第 2-5 段）

- 分支 `claude/audit-fix-2-5`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-5.md`；進度檔：`docs/reports/20261016_稽核修正2-5_進度.md`。底稿：master（v9.0，已移至 `model/archive/`）；`model/CURRENT` 改為 v10.0。
- Excel（CC 以 `builder/v1000.py` 自 v9.0 產生，經 LibreOffice 重算存檔）：
  - N1（D12）：Interface L 節新增 8 個 `IFW_*_LifeSelf`（`_Prod` × `L1_LTotal` × `L1_MFleet`；情境，不回流）。
  - N2（D4）：L1 新增「性質」欄（估計／殘差／倒推／恆等式／未解釋）；新列 `L1_GapUnexplained`（＋`_Lo`／`_Hi`）；Calib C67／C68、Train_In 第 34 列、Alloc 倒推列加標記。
  - N3（D5）：Checks V 節與 `CHK_VerifyTotal／Pass／Fail`；Calib 新增 MLPerf v5.1 Hopper、GB200 兩點；新增 SRC_PERF_060–065、SRC_HAR_016、E378。
  - N4：TTFT、Perf_Batch、Alloc_In 標籤註記；N5：下游契約 v0.6。另依 PR #72 獨立查核修正 L1!P89 文字與契約第 2、5 節（僅標籤與文件）。
- 驗收：LibreOffice 重算錯誤 0；restore_log unmatched 0；冪等差異 0；既有 `IF_`／`IFW_`／`L1_` 名稱數值變動 0。

## 20261016_Tokenomics_v9.0.xlsx（取代 v8.0；主版：`IF_TokGW_*` 全部上升、`IF_AllocQ1_R2`／`IF_AmortRev_*`／`L1_MImplied*`／`L1_ExtServeGW` 定義改變，契約改變；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` 5r1 第 2-4 段）

- 分支 `claude/audit-fix-2-4`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-4.md`；進度檔：`docs/reports/20261016_稽核修正2-4_進度.md`。底稿：master（v8.0，已移至 `model/archive/`）；`model/CURRENT` 改為 v9.0。版號判為 v9.0 而非 v8.1：`IF_AllocQ1_R2`、`IF_AmortRev_*`、`L1_ExtServeGW` 的定義改變（契約改變）。
- Excel（CC 以 `builder/v810.py` 等自 v8.0 產生，經 LibreOffice 重算存檔）：
  - M1（D9）：快取命中進產能。Perf／Sens_Perf 與 `_Prod` 鏡像的 TTFT、每請求 GPU 秒、prefill GPU 占比，prefill 只計新鮮輸入 ISL × (1 − `B4_CacheHit`)；Perf_Batch（訓練端批次推論）不變。`IF_TokGW_*` 基準上升 8–22%（Sol 欄各世代 ×1.17–1.22），Hopper × Astra 由「TTFT 不可達」變為 3.63e9 M tok/年，Hopper 基準欄不再排除 Astra。
  - M2：Cap_In 第 87 列付費占比改 token 口徑 `1 − AL_FreeShare`（0.54 → 0.40），只影響 `L1_MImplied_Ext`。
  - M3：κ 套到價格端（Cap_In 第 90 列、`CAP_Price25Mix` 各乘 `AL_Kappa`）；基準 κ＝1，基準值不變。
  - M4：`IF_AmortRev_*` 分母改付費 token（Amortize 與 Amortize_Prod）。
  - M5：L1 `L1_LReqFleet` 判讀欄以恆等式讀法為主、字面讀法並列；兩者相差 2.69 倍，拆解見報告。
  - M6：`L1_MImplied`／`MImplied_Ext`／`MAPI`／`MSub`／`MSeat` 與 Cap_In H5、H8、H10（C 欄）、第 241 列改 2025 單價 `CAP_Price25Mix`；`IF_AllocQ1_R2` 改支出路線服務 GW（0.665 → 0.577）；`L1_ExtServeGW` 推算值改回支出路線。
  - M7：下游契約改 v0.5（文字旗標三種字樣、新增 v6.2／v6.3／v9.0 條目）。
  - 情境 `d9_cache_cap_off`（`B4_CacheHit`＝0）：Perf、Sens_Perf、Perf_Prod、Perf_Batch、Unit_Cost、Fleet_1GW、Training 等容量頁與 v8.0 逐格相同（只有兩格標籤文字不同）。
  - 具名範圍 1,322、公式格 48,906 不變；GOV_Errors 0、Warnings 271、Info 177 → 176；Decisions 新增 `AF2e-M1`–`M7`。
- 契約（相對 v8.0）：IF_ 60、IFW_ 44、L1_ 115 個名稱數值改變（含 _Lo／_Hi 與 Hopper × Astra 欄），無新增、無刪除；`IF_AllocQ1`／`Q2`／`ServeGW`／`RDGW`、`L1_LReqFleet_Id`、`L1_LTotal`、Training 頁不變。`docs/plan/Tokenomics_downstream_contract.md` 改為 v0.5。
- 驗證：parity 72 項全過（新增情境 `d9_cache_cap_off`；v6.2／v6.3 的 TTFT 不可達結構改以 `B4_CacheHit`＝0 情境驗證，Hopper × Astra 基準改為可達）；預期值更新逐項記於報告；冪等重建差異 0；與 v8.0 逐格比較無範圍外差異；`restore_log` unmatched 0、Excel 保留值 30 格（與 v8.0 相同）。
- `docs/builder/Tokenomics_builder_v5.md` 已重新產生（新增 `v810.py`）。

## 20261016_Tokenomics_v8.0.xlsx（取代 v7.0；主版：`IF_AllocQ1`／`Q2`／`ServeGW` 改支出路線，契約改變；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` 4r1 第 2-3 段）

- 分支 `claude/audit-fix-2-3`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-3.md`；進度檔：`docs/reports/20261016_稽核修正2-3_進度.md`。底稿：master（v7.0，已移至 `model/archive/`）；`model/CURRENT` 改為 v8.0。
- Excel（CC 以 `builder/v800.py` 等自 v7.0 產生，經 LibreOffice 重算存檔）：
  - L1（D2）：Cap_In 新增 M 節（第 276 列起）：2025 年度層級單價（Luna 0.1035／Sol 2.184／Astra 7.174 $/M，Derived，含低高）、2025 混合有效單價 `CAP_Price25Mix` 1.680（C90 的 0.857 倍）；`L1_MFleet` 改用 2025 機隊口徑單價 `AL_PriceFleet25`（0.5565 → 0.6171），2026 牌價值保留為 `L1_MFleet_Px2026`。
  - L2（D2 × D1(c)）：基準維持固定模型產能（R1）；新增情境 `d2_model_2025`、`_lo`、`_hi`（`ARCH_ScaleGen` Hopper、GB200 兩格 0.65／0.35／1.1）。
  - L3（D2）：Alloc_In 新增研發世代組合 `AL_RDMix*`（Hopper 0.60／GB200 0.38／GB300 0.02／VR200 0，含低高；Derived）；Alloc J 節以 GW 占比加權計算 `AL_FamGWyr`、`AL_RefGWyr`、`AL_HoldTrain`；不可達世代依 D8 排除並重新正規化（`AL_RDShareExcl` 另列）。`IF_AllocRDGW` 0.0907 → 0.2402。Checks Z2（合計 100%，ERROR）。
  - L4（D2）：`L1_LReqFleet` 改 2025 機隊口徑（Alloc K 節 `L1_FleetBreakeven2025`），原 VR200 讀法與恆等式讀法並列（`L1_LReqFleet_VR200`、`L1_LReqFleet_Id`）；`L1_PriceReqBE` 同口徑；`L1_FleetBreakeven`、`L1_FleetMargin` 維持 VR200 截面並改標籤；Checks B43 的 Hopper 占比改讀 `AL_MixHopper`。基準所需 L 0.530 → 1.968，大於 `L1_LTotal` 0.643，判讀由「回本」變「未回本」。
  - L5（D14）：`AL_Q1`／`AL_Q2`／`AL_ImpliedRDGW` 與 `IF_AllocQ1`／`Q2`／`ServeGW` 改支出路線（`IF_AllocServeGW` 0.1584 → 0.8981；Q1 0.3641 → 0.2110；Q2 0.4281 → 0.2117）；token 路線保留為 `AL_Q1_Tok`、`AL_Q2_Tok`、`IF_AllocServeGW_Tok`；`L1_ScaleServe` 改標未解釋差距、數值不變；L1!L69 來源標籤改 SRC_DEM_004；新增 `L1_AstraExtTok_180B／400B／800B` 與 Epoch 1e27 上限欄。
  - Decisions 新增 `AF2d-L1`–`L5`；DB_Evidence 新增 E374–E377；Gov_Map 新增 16 列；Alloc G 敏感度表新增「服務 GW（支出路線）」欄，自我檢查欄後移一欄。
  - 具名範圍 +77（1,245 → 1,322）；公式格 48,399 → 48,906；GOV_Errors 0、Warnings 271、Info 177（174 → 177）。
- 契約（相對 v7.0）：IF_ 6 個、L1_ 24 個數值改變（含 _Lo／_Hi），IFW_ 0；新增名稱見報告。`docs/plan/Tokenomics_downstream_contract.md` 改為 v0.4（Q1、Q2、服務 GW、所需 L 定義段改寫）。
- 驗證：parity 71 項全過（新增 `test_v800_audit_fix2_3`、3 個 L2 情境）；預期值更新逐項記於報告；冪等重建差異 0；與 v7.0 逐格比較無範圍外差異；`restore_log` unmatched 0、Excel 保留值 30 格與 v7.0 相同。
- `docs/builder/Tokenomics_builder_v5.md` 已重新產生（新增 `v800.py`）。

## 20261016_Tokenomics_v7.0.xlsx（取代 v6.3；主版：下游契約第 4 節改寫、新增名稱；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` r0 第 3 節＝2-2 段與 `docs/workorders/20261015_世代價格B.md` r0）

- 分支 `claude/audit-fix-2-2`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-2.md`；進度檔：`docs/reports/20261016_稽核修正2-2_進度.md`。底稿：master（v6.3，已移至 `model/archive/`）；`model/CURRENT` 改為 v7.0。
- Excel（CC 以 `builder/v700.py` 等自 v6.3 產生，經 LibreOffice 重算存檔）：
  - 世代價格 B 段：Cap_In L 節（第 271–274 列）新增世代上市間隔 `CAP_GenGap_GB200／GB300／VR200`（基準／低／高 1.88／1.88／2.17、0.41／0.41／0.54、1.18／1.11／1.24 年，Analogy 單一樣本）；L1 新增 `L1_GenPxThr_Rev_*`、`L1_GenPxThr_Pay_*`（各世代，含 `_Lo`／`_Hi`；不含價格；固定模型口徑，情境 `d1_model_scale` 見報告）。DB_Evidence 新增 E366–E373，E338／E339／E341 附註。
  - 2-2-b：新增 `L1_FleetProdRatio`；`L1_FleetMargin` 與 Checks K4 改讀重解值（3.3876 → 3.1176）；`L1_GapUtil` 分母乘 `CTL_ProdDerate`（1.4634 → 1.7217，`L1_GapProduct` 1.6352 → 1.9238）；Interface A231 標題；Serving C18 固定 1.0（說明欄；情境 b_prod_derate 改驅動 `CTL_ProdDerate`）；Alloc『全 GB200』『全 VR200』兩列改純世代常數；Calib C68 標記由 Assumed 改倒推（數值不變，Load_Bearing 56 → 55）；Decisions 新增 AF2c-*（GEN、Q3R1、J1–J5、D7R、K3）。GOV K3（f_registry）查明未修，見報告。
  - 具名範圍 +30（1,215 → 1,245）；公式格 48,273 → 48,399；GOV_Errors 0、Warnings 271、Info 174（175 → 174）。
- 下游契約：`docs/plan/Tokenomics_downstream_contract.md` 改為 v0.3（第 4 節改寫）。IF_／IFW_ 名稱數值不變。
- `docs/builder/Tokenomics_builder_v5.md` 已重新產生（新增 `v700.py`）。

## 20261016_Tokenomics_v6.3.xlsx（取代 v6.2；次版：機隊口徑單價、整代不可達、TTFT 進 decode 成本列、J1 r1 規模倍數；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` r1 第 2b 節＝2-1b 段）

- 分支 `claude/audit-fix-2-1b`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-1b.md`；進度檔：`docs/reports/20261016_稽核修正2-1b_進度.md`。底稿：master（v6.2，已移至 `model/archive/`）；`model/CURRENT` 改為 v6.3。
- Excel（CC 以 `builder/v603.py` 等自 v6.2 產生，經 LibreOffice 重算存檔）：
  - K1：新增 Alloc I 節（`AL_PriceGen`、`AL_PriceFleet`）與 Cap_In K 節（`B4_PriceFleet`）。機隊口徑單價＝可達層級重新正規化、以付費 token 加權；Cap_In H7（m_fleet、m 下限、所需 token 三列）、H10 m_fleet、L1 `PriceRealFleet`／`PriceReqBE` 改讀它。需求路線（H5／H8）仍用第 90 列完整層級組合單價。基準值 1.5844 $/M（完整組合 1.9606）。
  - K2：任一占比 > 0 的世代整代不可達時，Alloc／Cap_In 輸出文字「整代不可達」，不再把該世代權重併入其餘世代（`f_registry_t07_t09_on`：`IF_AllocQ1`／`Q2`／`IF_AllocServeGW` 由數值變文字；`b_prod_derate` 不受影響）。文字一路傳到單價、H7 所需 token 與 L1 機隊閉合名稱（`L1_ScaleServe`、`L1_MFleet`、`L1_TokPerPromptClose`、`L1_Gap*` 等；新增 `AL_UnavailTxt` 取代 Cap_In H7 起與 L1 寫死的「SLO 不可達」），無數值、負值或 #VALUE!。
  - K3：Perf／Perf_Batch／Sens_Perf／Perf_Prod 第 103 列（decode GPU 秒）讀 TTFT 旗標，Hopper × Astra 為文字；`IF_CostDec_Astra`、`IF_CostDecAcct_Astra`、`IF_AmortTD_Astra` 的 Hopper 三欄由數值變文字。Perf_Batch_Prod 因第 103 列依賴而多出第 76／77 列鏡像。
  - J1 r1：`ARCH_ScaleGen_Lo`／`_Hi` 依 2Q 報告 Q2 改為 0.5／0.3／—／— 與 1.3／1.0／—／2.5（基準仍 1）；情境 `d1_model_scale` 改為 0.8／0.55／1.0／1.4。
  - Decisions 新增 `AF2b-K1`、`K2`、`K3`；`AF2-D1c` 加 r1 註記；Gov_Map 範圍文字與註記更新。
- 契約（相對 v6.2）：名稱 IF_ 3、L1_ 9 個數值改變，IFW_ 0；新增名稱 `AL_PriceGen`、`AL_PriceFleet`、`AL_UnavailTxt`、`B4_PriceFleet`。相對 v6.1：IF_ 45、IFW_ 20、L1_ 43 個改變。完整新舊值表見報告。
- 驗證：parity 全數通過；新增 `test_v603_fleet_price_k2_k3`；預期值更新逐項記於報告；冪等重建差異 0；與 v6.2 逐格比較無範圍外差異。

## 20261016_Tokenomics_v6.2.xlsx（取代 v6.1；次版：D1(c) 模型規模倍數、TTFT 進可達判斷、Alloc 重新正規化；判斷類，依工作單 `docs/workorders/20261016_稽核修正2.md` r0 第 2 節＝2-1 段）

- 分支 `claude/audit-fix-2-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261016_稽核修正2-1.md`；進度檔：`docs/reports/20261016_稽核修正2-1_進度.md`。底稿：master `728ff30`（v6.1，已移至 `model/archive/`）；`model/CURRENT` 改為 v6.2。
- Excel（CC 以 `builder/v602.py` 等自 v6.1 產生，經 LibreOffice 重算存檔）：
  - 2-1-a：Spec_Rack 新增「模型規模倍數」節三列（具名範圍 `ARCH_ScaleGen`／`_Lo`／`_Hi`，1×5，Assumed）；Perf／Perf_Batch／Sens_Perf 第 28、32、33 列與 Training／Sens_Train 第 22 列乘倍數（基準 1，數值不變）；Calib 第 30 列不乘。新增 parity 情境 `d1_model_scale`。Interface B／C／D 節標題與 `L1_TokMW_Gen_ratio_*` 說明加註「固定模型口徑」。
  - 2-1-b：Perf／Perf_Batch／Sens_Perf／Perf_Prod 第 90、93 列讀第 77 列 TTFT，不符輸出「TTFT 不可達」；Checks B27 同時計兩種旗標。基準下 Hopper × Astra 的 `IF_TokGW_Astra` 等由數值變文字旗標。
  - 2-1-c：Alloc 排除不可達層級後層級權重重新正規化，全不可達的世代排除、世代組合重新正規化；新增「未服務需求占比」顯示列（`AL_UnservedPaid`／`AL_UnservedFree`／`AL_UnservedGen`／`AL_GenShareOK`／`AL_GenOK`）。`AL_ServeGW`、`IF_AllocQ1`／`Q2`、`L1_ScaleServe`、`L1_MFleet` 等隨之改變。
  - Decisions 新增 `AF2-D1c`、`AF2-TTFT`、`AF2-ALLOC`；`AF1-D8` 狀態標「TTFT 部分由 AF2-TTFT 取代」（不刪）；Gov_Map 新增 3 列。

## 20261015_Tokenomics_v6.1.xlsx（取代 v6.0；次版：輸入值與一處公式改變；D3、D6、D10、D13、Q3、Q6；判斷類，依工作單 `docs/workorders/20261015_稽核修正3B.md` r0）

- 分支 `claude/audit-fix-3b`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261015_稽核修正3B.md`；進度檔：`docs/reports/20261015_稽核修正3B_進度.md`。底稿：master `43ccdd7`（v6.0，已移至 `model/archive/`）；`model/CURRENT` 改為 v6.1。
- Excel（CC 以 `builder/v601.py` 自 v6.0 產生，經 LibreOffice 重算存檔）：
  - D3：Alloc_In D9:E12 2025 組合低／高端（Hopper 0.5–0.7、GB200 0.25–0.4、GB300 0–0.1、VR200 0）；Derived。
  - D6：Calib C67 η_d 倍數 1.5 → 1.2。
  - D10：Alloc_In C23:E23 計價倍數 0.85／0.73／1.17；Derived。
  - D13：Alloc_In C24:E24 改為純利用率 0.41／0.30／0.65；Cap_In 第 114、218、255 列（及產生它們的 v533／v534／v536 規格）乘 `CTL_ProdDerate`。暫定、待證據。
  - Q3：Har_In C61／D61 0.7／1.7；Train_In 第 34 列 RL token 區間登錄為高段 Assumed。Q6：Inputs H9／H17／H19、Spec_Rack C16 僅改說明。
  - Decisions 新增 `AF3B-D3`、`D6`、`D10`、`D13`、`Q3`、`Q6`。
- 契約：185 個 IF_／IFW_／L1_ 名稱數值改變（IF_ 90、IFW_ 44、L1_ 51；向量變動僅在 Hopper 欄）；名稱與形狀不變。完整新舊值表見報告表 3。不發下游同步，併入 CoreWeave 後那一次。
- 驗證：parity 全數通過；新增情境 `h_alloc_mix_2025ye`；預期值更新逐項記於報告表 1；冪等重建差異 0。

## 20261015_Tokenomics_v6.0.xlsx（取代 v5.36；主版：下游契約定義變更；D7 _Prod／_Life 統一、D8「SLO 不可達」文字語意、D11 回本溢價分母＝付費 token；判斷類，依工作單 `docs/workorders/20261015_稽核修正1.md`）

- 分支 `claude/audit-fix-1`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261015_稽核修正1.md`；進度檔：`docs/reports/20261015_稽核修正1_進度.md`。底稿：v5.36（已移至 `model/archive/`）；`model/CURRENT` 改為 v6.0。
- Excel（CC 以 `builder/v600.py` 等自 v5.36 產生，經 LibreOffice 重算存檔）：
  - D7：`IFW_*_Prod` 讀 Theory_Rev_Prod（生產折減下重解 SLO），不再是 `_Util` × CTL_ProdDerate；`IF_*_Life` 為 `IFW_*_Life` 的過渡別名；Theory_Rev 新增 E 節 `_Prod` 恆等式與 Checks Z1（ERROR）；Alloc H 節新增 `AL_CapPaidProd`、`AL_BlendPaidProd`、`AL_ProdRatioPaid`，Cap_In 利用率修正（上限）改讀付費產能比。
  - D8：Perf／Unit_Cost／Training／Amortize／Theory_Rev／Fleet_1GW／Alloc 等所有「SLO 不可達」改輸出文字，下游判斷改 ISNUMBER；Fleet_1GW 排除不可達層級並重新正規化（新 D 節）。
  - D11：Amortize 回本溢價分母改為付費 token（`IF_AmortBU_*`、`IF_FullCost_*`、`IF_FullCostDefault_*` 隨之上升）。
  - Decisions 新增 `AF1-D7`、`AF1-D8`、`AF1-D11`。
- 契約文件 `docs/plan/Tokenomics_downstream_contract.md` 升 v0.2；builder md 重新產生。
- 驗證：parity 全數通過（見報告），新增情境 `z1_c18_07_text`、`z2_train_e31_100` 與兩個新測試；預期值更新逐項記於報告表 1。

## 20261015_Tokenomics_v5.36.xlsx（取代 v5.35；支出路線改 SRC_DEM_004、計價倍數 1.3、κ、缺口恆等式與 L1 價格列；判斷類，依工作單 `docs/workorders/20261015_v5.36.md` r0）

- 分支 `claude/v5.36-build`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261015_v5.36.md`；進度檔：`docs/reports/20261015_v5.36_進度.md`。底稿：master `9dff7f5`（v5.35）；`model/CURRENT` 原為 v5.35。
- Excel（CC 以 `builder/v536.py` 自 v5.35 產生，經 LibreOffice 重算存檔；藍字輸入以「仍為舊值才寫」守衛寫入）：
  - B1：支出路線改 `SRC_DEM_004`（D 7.5／E 8.8）；新增 `SRC_DEM_073`（稽核後營收成本 7.5）；`SRC_DEM_018` 降為顯示對照列。
  - B2：計價倍數 C／D／E 2.0／1.5／3.0 → 1.3／1.0／1.6，標籤更名。
  - B4：新增 `AL_Kappa`（1.0；0.65–1.2）乘入有效服務 GW；`L1_GapISL`＝1/κ。
  - B5：`L1_GapPrompt` 1.3013、`L1_GapUtil` 1.7143；缺口恆等式與 Checks M5（基準欄）置於 Cap_In J 節（第 244–264 列）。
  - B6：L1 新增 `L1_ScaleServe2000`、`L1_PriceRealFleet`、`L1_PriceRealDemand`、`L1_PriceReqBE`、`L1_PriceRho`（各含 `_Lo`／`_Hi`）。
  - B7：DB_Evidence E344–E365、Decisions X45–X47、README。
- 所有 `IF_` 名稱數值逐格不變；變動的既有名稱 37 個，皆在工作單預期範圍（`AL_ServeGWSpend`、`L1_ScaleServe`、`L1_MFleet`、`L1_LReqFleet`、`L1_TokCeiling`、`L1_TokPerPromptClose`、`L1_Gap*` 等）。
- 測試：`formula_cells` 47,391 → 47,602、`defined_names` 1,180 → 1,201、`src_names` 432 → 435、`l1_names` 255 → 270、`al_names` 86 → 89；GOV_Errors 0／Warnings 271／Info 169；舊期望值依工作單預期變動更新；新增 `test_v536_spend_route_kappa_price`。

## 工程類：修訂八-B 停用公式引擎與網站（不改 Excel；Excel 仍為 20261014_Tokenomics_v5.35.xlsx）

- 分支 `claude/parity-rev8`（合併 SHA 見報告與 PR）。報告：`docs/reports/20261015_修訂八B_停用引擎.md`；進度檔：`docs/reports/20261015_修訂八B_進度.md`；工作單：`docs/workorders/20261015_修訂八B_停用引擎.md`。
- 不改 `model/`、`builder/`、任何數值；測試期望值與容差不改（逐項例外見報告表 1）。
- `engine/`、`app/`、`tests/app/`、`tools/build_engine_cache.py`、`tools/stage0_inventory.py` 以 `git mv` 移到 `legacy/`（`tests/app` → `tests/legacy/app`）；`tests/parity/test_functions.py` → `tests/legacy/`。
- `tests/parity/` 改為讀 LibreOffice 重算值：`conftest.py` 的 `lo.view(inputs)`（同組輸入只算一次，2 條執行緒預先算好情境）；`test_scenario_checks` 取代引擎對 LibreOffice 的逐格比對；刪除快取等價、增量／全簿重算秒數等測試。
- `tokenomics.py`、`run_local.bat` 改為印出暫停訊息；`tools/export_csv.py` 改讀 LibreOffice 重算值；`requirements.txt` 移除 pycel／streamlit／pandas，新增 `requirements-legacy.txt`。
- `.github/workflows/parity.yml`：單一 parity job＋governance＋ci-status，仍不阻擋合併。
- `CLAUDE.md` 修訂八（含 4b 第 8 項代理模型）、`README.md` 同步更新。

## 20261014_Tokenomics_v5.35.xlsx（取代 v5.34；m 序列三項修正 ＋ L 拆分（L_price × L_demote）；判斷類（chat 端判定 J22–J24，CC 執行），依工作單 `docs/workorders/20261014_v5.35.md` r0）

- Commit：分支 `claude/v5.35-build`（內容提交 `de39f92`；合併 SHA 見報告與 PR）。報告：`docs/reports/20261014_v5.35.md`；進度檔：`docs/reports/20261014_v5.35_進度.md`。底稿：master `322e1c7`（PR #44，v5.34）；`model/CURRENT` 原為 v5.34。
- 依據：Andy 2026-10-14 19:38「3. Assume 0.65，其餘照建議」（對象＝v5.34 報告「待 Project 判斷」第 1–3 項的 chat 端建議）、15:49「兩件事我都同意。」（L 拆分）；chat 端判定 J22–J24。
- Excel（CC 以 `builder/` 自 v5.34 產生，經 LibreOffice 重算存檔）：
  - B1（J23；Cap_In H10）：廣告營收列 D／E／F 改為藍字 0／0.5／1.0（各登 Gov_Map，區間 0–0.2／0.3–0.8／0.5–1.5）；消費訂閱／商用席次／API 營收三列改以「m 分子營收（營收 − 廣告）」為基底（三分之和＝m_整體分子）；新列「2026 消費訂閱占 ChatGPT 付費 token 份額」（第 200 列；C 連結 H8 0.75、D 藍字 0.65（0.5–0.8）、E／F 連結 D），消費訂閱／商用席次 token 列改引用此列；原「中階牌價指數」預留列（第 204 列）改為連結 I 節 L_price（顯示用，四個藍字 1 退役）。2026 Q2：m_API 0.3467 → **0.3403**、m_消費訂閱 4.768 → **5.399**、m_商用席次 6.502 → **4.557**、m_整體 **1.343**（不變）、m_fleet **0.781**（不變）；Q1 0.295／5.744／3.556／1.192；FY2026 0.348／5.569／8.044／1.432；2025 欄全部不變。
  - B2（J22；Cap_In I 節，第 225–243 列，接在 H10 之後、讀法列之前）：藍字 g −0.10（−0.25～+0.05）、T1 4（3–5）、ρ 0.5（低端＝IF_PriceRef_Luna ÷ IF_PriceRef_Sol 0.05 公式、高端 1.0）；T＝INDEX(IF_DeprLifeIT,1,2)＝6；k＝LN(1+g)；L_price **0.7412**（0.4762–1.1618）、L_total **0.6426**（0.342–1.1618）、L_demote **0.867**（0.718–1.0）；對照 CTL_PriceLife 1、E246 類比 0.42–0.70、Gov_Map GM593 區間判讀「區間內（0.3–1.0）」；回本所需 L（m＝L1_MFleet）**0.3645**（0.208–0.555）、（m＝L1_MAPI）0.5237；判讀「回本（L_total 口徑）」。
  - B3：SRC_Demand 新增 `SRC_DEM_072`（OpenAI 廣告年化 $1B，CNBC 2026-08-31；Active）；DB_Evidence E338–E343（N14–N19：牌價序列 OpenAI／Sonnet／Gemini、迴歸結果、L 換算式、廣告年化）；SRC_Price 不新增（等級 3，待一手確認）。
  - B4：L1 新增 `L1_LPrice`、`L1_LDemote`、`L1_LTotal`（外部欄＝CTL_PriceLife，判讀「落在 0.3–1.0 區間內」）、`L1_LReqFleet`（外部欄＝L1_LTotal，判讀「回本（L_total 口徑）：L_total 0.64 ≥ 所需 L 0.36」），各含 `_Lo`／`_Hi`（第 86–89 列）；既有 L1 列（第 5–85 列）逐格不變。
  - B5：Gov_Map 新登錄 10 列（GM634–GM643：I 節 g／T1／ρ 基準與端點、H10 廣告三格、0.65 一格）；GM629（原 C203:F203）改指 C204:F204、類別改「顯示用（公式）」；GM630–GM633（2026 世代組合）因插列改指 D211–D214（值不變）；Decisions X42–X44（X44 為 v5.34 待判斷第 4–13 項十項定案）；Excel README A1、B5、新列 A37／B37。
  - 既有 IF_ 逐格不變（Interface 0 格差異）；既有 L1_（含 v5.34 六個）數值不變；`CTL_PriceLife`、`CTL_Monetize` 不改。
- builder：新增 `v535.py`（`patch_h10` 在寫入前就地修改 v534 的 H10 規格；`cap_in_i`；`gov_map_repoint` 以標籤守衛改指位移的 Gov_Map 列）；`gov.py`、`build.py`（SNAP_RETIRED 加 H10 牌價指數四格）、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v535.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（36 個檔）。
- 測試：`formula_cells` 47,134 → 47,391、`defined_names` 1,167 → 1,180、`src_names` 431 → 432、`l1_names` 243 → 255；GOV_Warnings 270 → 271、GOV_Info 169 不變；`test_v534_m_split` 的 2026 Q2 錨點改為 v5.35 值（工作單預期變動）；新增 `test_v535_l_split`；情境 b_prod_derate 補 L1_LReqFleet 的 ISNUMBER 守衛斷言。
- 治理：GOV_Errors 0、GOV_Warnings 271（W1 +1：SRC_DEM_072 利害關係方 Active 無第二來源）、GOV_Info 169。

## 20261014_Tokenomics_v5.34.xlsx（取代 v5.33；變現率 m 細化：m 按收費模式分拆、token 帳三路線與閉合解、m 季度序列；判斷類（chat 端判定 J15–J21，CC 執行），依工作單 `docs/workorders/20261014_v5.34.md` r0.1）

- Commit：分支 `claude/v5.34-build`（內容提交 `508da71`；合併 SHA 見報告與 PR）。報告：`docs/reports/20261014_v5.34.md`；進度檔：`docs/reports/20261014_v5.34_進度.md`。底稿：master `ebeb7e6`（PR #42，CLAUDE.md 修訂七）；`model/CURRENT` 原為 v5.33。
- 依據：Andy 2026-10-14 15:35「我能說甚麼呢，你已經包括我的想法了。關於第6點，這個m當然是實驗室(OAI)視角」、15:39「同意，請進行。」、15:49（r0.1）「兩件事我都同意。」；chat 端判定 J15–J21。
- Excel（CC 以 `builder/` 自 v5.33 產生，經 LibreOffice 重算存檔）：
  - B1：SRC_Demand 新增 `SRC_DEM_069`（2026 Q1 營收 5.7）、`SRC_DEM_070`（2026 推論支出預測 14.1，Alt）、`SRC_DEM_071`（API 占營收 0.20，低 0.15）；`SRC_DEM_042`、`SRC_DEM_060` 備註補；DB_Evidence E325–E337（N01–N13）。
  - B2：Cap_In 新增 H8「m 分拆」（第 130–169 列）：藍字 商用席次占比 0.10（0.05–0.15）、消費訂閱占付費 token 份額 0.75（0.60–0.90）、2026 廣告 0.5（0–1.0）、方案上限讀法四格（20／700／200／14,000）；營收三分 9.149／1.307／2.614、token 三分、m_API **0.564**、m_消費訂閱 **4.261**、m_商用席次 **1.826**、m_整體 **1.743**（自我檢查＝L1_MImplied，差 0）；折讓因子 1.0／0.75／1.125、隱含組合因子 0.564（對照代理型極端 0.196）；訂閱 m 下限 0.029／0.014；「必須為真」每訂閱者年 token 142 M（現值 44.6 的 3.2 倍）；J21 Anthropic 對照 0.828／0.163。
  - B3：Cap_In H9「token 帳三路線」（第 170–181 列）：需求 3.83e9／機隊 8.23e9／上限 1.20e10，殘差 0.465、0.319；閉合解 有效服務 GW 0.3929 → T_chat* 1.273e10 → τ* **13,950**（高於 Alloc_In C15 區間 2,000–11,000）；閉合免費占比 0.213。Checks M4（WARN）＝1（預期）。
  - B4：L1 新增 `L1_MAPI`（0.564；0.106–0.794）、`L1_MSub`（4.261；0.753–24.96）、`L1_MSeat`（1.826；0.553–6.849）、`L1_MixFactorAPI`（0.564；0.094–1.058）、`L1_TokPerPromptClose`（13,950；6,911–22,758；外部＝Alloc_In C15 區間，判讀「高於外部區間」）、`L1_MAPI_Anthropic`（文字「缺分母」；外部欄 0.828／0.163），各含 `_Lo`／`_Hi`；m 三列外部欄＝CTL_Monetize，判讀 L1_MAPI「區間內」、MSub／MSeat「區間外」。
  - B5：Cap_In H10「m 季度序列」（第 182–223 列；顯示用）：2025／2026 Q1／Q2／FY2026 營收 13.07／22.8／26.8／36（藍字 36）、份額每欄各自輸入（0.70／0.10、0.60／0.20、0.55／0.25、0.45／0.35；API 餘額 0.20）、API token（SRC_DEM_011 年化 7.884e9；FY × 1.3）、ChatGPT 則數 2.5／3.2／3.6／3.8、2026 世代組合 Hopper 0.25／GB200 0.45／GB300 0.25／VR200 0.05；m_API 0.564／0.295／**0.347**／0.358、m_整體 1.743／1.166／**1.343**／1.452、m_fleet 0.810／0.658／**0.781**／1.042；中階牌價指數預留列（1，不乘入）。
  - B6：Cap_In E12（`B4_Disc` 高端）0.3 → **0.4**（J20；基準 0.2、低端 0.1 不改，`IF_Price*` 不變）；Gov_Map GM441 區間文字補 0.1–0.4、GM441／GM442 理由附加，新登錄 20 列（GM614–GM633）；Decisions X35–X41；Excel README A1、B5、新列 A36／B36；Checks M 區標題補 M4。具名範圍新增 `B4_Disc_Lo`／`B4_Disc_Hi`（顯示用）。
  - 既有 IF_、L1_ 數值全部不變（逐格比對）；`CTL_Monetize` 不改（J15）。
- builder：新增 `v534.py`；`gov.py`、`build.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v534.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（35 個檔）。
- 測試：`formula_cells` 46,471 → 47,134、`defined_names` 1,140 → 1,167、`src_names` 424 → 431、`l1_names` 225 → 243、`b4_names` 39 → 41、`display_only_names` 140 → 142；GOV_Warnings 267 → 270、GOV_Info 168 → 169；新增 `test_v534_m_split`；情境 b_prod_derate 補 L1_TokPerPromptClose 與 Checks M4 的 SLO 守衛斷言。
- 治理：GOV_Errors 0、GOV_Warnings 270（M4 +1、W1 +2：SRC_DEM_069／071 利害關係方 Active 無第二來源）、GOV_Info 169（I3 +1：L1_TokPerPromptClose「高於外部區間」）。

## 20261013_Tokenomics_v5.33.xlsx（取代 v5.32；付費 token 數量校準：2025 基準年世代組合、每則 token 高端、機隊口徑（兩種讀法）；判斷類（chat 端判定，CC 執行），依工作單 `docs/workorders/20261012_v5.33.md` r1（B 段））

- Commit：PR #41 合併 `388f274`（內容 `4c4a336`→`48e19a9`）。報告：`docs/reports/20261013_v5.33.md`。底稿：master `63dc78a`（v5.32 合併，PR #39）；`model/CURRENT` 原為 v5.32。A 段查證：`docs/reports/20261012_v5.33A_查證.md`（PR #40）。
- 依據：Andy 2026-10-12 07:43（A 段工作單原話）與 2026-10-13 06:46「2.2025 基準年世代組合：或改為 Hopper 60／GB200 40　其餘支持照你的建議」；chat 端判定 J7–J14。
- Excel（CC 以 `builder/` 自 v5.32 產生，經 LibreOffice 重算存檔）：
  - B1：SRC_Demand 新增 `SRC_DEM_049`–`SRC_DEM_068`（20 筆，A 段第 8 節 S-01–S-20 各一筆）；`SRC_DEM_007` 備註補 J14（13.07 為 OpenAI 自身營收口徑，待一手確認）、`SRC_DEM_009` 補 N15、`SRC_DEM_045` 補 N12；DB_Evidence E302–E324（A 段 N01–N23，判定照提案）；E301 判定補「已查證」（N13）。
  - B2：Alloc_In 藍字 C9 0 → **0.6**、C11 0.4 → **0**、C12 0.2 → **0**（J8；C10 0.4 不變）、E15 6,400 → **11,000**（J9）；G 欄備註補 J8／J9。連動：Alloc B–G 節；`IF_AllocQ1` 0.573 → 0.332、`IF_AllocQ1_R2` 0.629 → 0.420、`IF_AllocQ2` 0.614 → 0.394、`IF_AllocServeGW` 0.0675 → 0.1826、`IF_AllocImpliedNk` 1.98 → 5.36；`L1_ScaleServe` 18.07 → 7.38、`L1_GapPrompt_Hi` 3.2 → 5.5、`L1_MImplied_Lo` 1.05 → 0.75 等（B2 列明者）。
  - B3：Cap_In 新增 H7「機隊口徑」（第 108–130 列，接在 H6 之後；原第 108 列讀法移到第 130 列並改寫；既有具名範圍不位移）：支出路線服務 GW ÷ Azure 倍數 0.674、付費／免費產能、r 模型 0.57 vs 支出口徑 3.22、利用率修正 0.583／0.85、機隊付費 token 點估計 8.23 × 10⁹（上限 11.99 × 10⁹）、機隊 m 0.810（0.531–1.417）、m 下限 0.556、「必須為真」三列（m＝0.3 被上限排除）、非文字份額 0.05／0.10／0.20（藍字，Gov_Map GM612／GM613）與扣除後 m。
  - B4：L1 新增 `L1_MFleet`（0.810；外部欄＝CTL_Monetize，判讀「落在 0.3–1.0 區間內」）與 `L1_TokCeiling`（1.199 × 10¹⁰；外部欄＝AL_DPaid，判讀「需求路線 ÷ 上限＝0.32」）；Checks M2、M3（WARN，依現值 0）。
  - B5／B6：`CTL_Monetize` 基準 1 與區間 0.3–1.0 不改；Gov_Map GM590（C9:C12）、GM586／GM587（C15 區間文字改 2,000–11,000）、GM594 理由欄附加；Decisions X27–X34，X22／X26 備註附加；README A1、B5、新列 A35／B35。
- builder：新增 `v533.py`；`gov.py`、`build.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v533.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（34 個檔）。
- 測試：`formula_cells` 46,203 → 46,471、`defined_names` 1,109 → 1,140、`src_names` 399 → 424、`l1_names` 219 → 225；GOV_Warnings 250 → 267；`L1_ScaleServe`、`AL_ServeGWSpend`、`L1_MImplied_Lo` 期望值更新；`test_batch_etad_expected_values` 另略過 v5.32 → v5.33 改變的名稱；新增 `test_v533_fleet_basis`。
- 規範：CLAUDE.md 修訂六（2026-10-13，Andy 決定）——本機數值檢查取代等待 GitHub CI 作為提交與合併門檻；重算秒數改為警告（`RecalcTimeWarning`）；兩輪停損；數值檢查通過後 CC 自行合併。另補 `L1_Ans1` 批次 η_d 比對期望值 0.0530 → 0.0829、`AL_ServeGWSpend` 1.21964 → 1.34714。新增 `docs/reviews/`（外部驗收紀錄）。
- 治理：GOV_Errors 0、GOV_Warnings 250 → 267（W1 +17：新 SRC_DEM 利害關係方 Active 無第二來源；M2、M3 為 0）、GOV_Info 168（不變）。

## 20261011_Tokenomics_v5.32.xlsx（取代 v5.31；變現率 m 追蹤：付費用戶數 × 每用戶年 token 用量；判斷類（chat 端判定，CC 執行），依工作單 `docs/workorders/20261011_v5.32.md` r1（B 段））

- Commit：見本輪分支 `claude/v5.32-build`（合併後補上雜湊）。報告：`docs/reports/20261011_v5.32.md`。底稿：master `f16f161`（v5.31 合併，PR #36）；`model/CURRENT` 原為 v5.31。A 段查證：`docs/reports/20261011_v5.32A_查證.md`（PR #38）。
- 依據：Andy 2026-10-11 09:41（追蹤 m 的工作單原話）與 11:21「了解，接著照建議依序執行」；chat 端判定 A 段 J1–J6（J1 調整為 (a′)）。
- Excel（CC 以 `builder/` 自 v5.31 產生，經 LibreOffice 重算存檔）：
  - B1：SRC_Demand 新增 `SRC_DEM_019`–`SRC_DEM_048`（30 筆，A 段 N01–N04、N06–N16 各時點一筆；N15／N16 只登錄，Cap_In C13 不改）；`SRC_DEM_018` 備註補 N12（Microsoft 分潤 20%；$38B 上限待查一手）；DB_Evidence E279–E301（A 段 N01–N23，判定照提案）。
  - B2：Cap_In 新增 H 節「m 追蹤（v5.32）」（第 66–108 列，接在 G 節之後，既有具名範圍不位移）：分子＝SRC_DEM_007 × 訂閱占比 0.61／0.70／0.82；訂閱人數期間平均 32.75 M；分母兩欄並列（模型 token＝Alloc 第 5、8 列；外部 token＝SRC_DEM_011 年化、SRC_DEM_013 × (1 − IF_FreeShare)）；單價＝B4_MixPaid × IF_PriceRef_*；隱含 m（訂閱、API、合併 × 模型、外部）；程式代理對照列不進合併。
  - B3：L1 新增 `L1_MImplied`（1.743；1.051–2.953）與 `L1_MImplied_Ext`（1.070；0.338–3.382），外部欄＝CTL_Monetize，判讀「落在 0.3–1.0 區間內／外」；Checks M1（WARN）。
  - B4：`CTL_Monetize` 基準 1 與 Gov_Map 區間 0.3–1.0 不改；既有 IF_／L1_ 數值逐格不變；Interface 不新增名稱。
  - B5：Gov_Map GM594 理由欄附加 J1 (a′)；Gov_Map 新登錄 4 列（Cap_In H 節 4 個藍字常數）；Decisions X21–X26；README A1、B5、新列 A34／B34。
- builder：新增 `v532.py`；`gov.py`、`build.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v532.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（33 個檔）。
- 測試：`formula_cells` 45,788 → 46,203、`defined_names` 1,072 → 1,109、`src_names` 368 → 399、`l1_names` 213 → 219；GOV_Warnings 221 → 250；新增 `test_v532_m_tracking`；`test_price_life_expected_values` 允許 L1_MImplied／_Ext 的 M:P 欄（外部欄＝CTL_Monetize）隨情境改變。
- 治理：GOV_Errors 0、GOV_Warnings 221 → 250（M1 +1：J4 (a) 預期；W1 +28：新 SRC_DEM 利害關係方 Active 無第二來源）、GOV_Info 168（不變）。

## 20261008_Tokenomics_v5.31.xlsx（取代 v5.30；J1–J6：GB300 機架價格、IT 維護機齡兩段（壽命期等值費率）、口徑註記、IREN 對照；判斷類（chat 端判定，CC 執行），依工作單 `docs/workorders/20261008_v5.31.md` r1（B 段））

- Commit：合併雜湊 `f16f161`（PR #36）；分支 `claude/v5.31-build`。報告：`docs/reports/20261008_v5.31.md`。底稿：master `bc03f5c`（v5.30 合併，PR #35）；`model/CURRENT` 原為 v5.30。A 段查證：`docs/reports/20261008_v5.31A_查證.md`（PR #34）。
- 依據：chat 端依 A 段報告建議 J1–J6，Andy 2026-10-08 22:31「不反對，請繼續」（全部採 A 段建議值）。
- Excel（CC 以 `builder/` 自 v5.30 產生，經 LibreOffice 重算存檔）：
  - J1（X16）：Spec_Rack GB300 機架價格 低／基準／高 4.0／5.0／6.5 → **4.0／4.3／5.0** $M——E11 維持連 SRC_HW_052（MS BOM 推算，等級 3→2）；E12 改 Derived 常數 4.3（＝4.0 × 1.075，同 VR200 F12 算法）；E13 改連 SRC_HW_010（Data Gravity 採購單 5.0）；SRC_HW_007（媒體 6.0–6.5）改 Alt；E16／E17 價格來源與標記文字。
  - J2／J3（X17／X18）：Inputs 新增第 36–38 列（IT 原廠保固年限＝SRC_DC_015 3 年；保固期內 0.25／0.5／1.0%；保固期滿後 2／3／5%，Analogy）；第 30 列「IT 維護」改為壽命期等值費率公式（同欄 WACC 與 IT 折舊年限年金加權）：低／基準／高 **1.02%／1.57%／1.82%**（原 2／3／4%）；DC_Cost 第 44 列公式不變。Interface I 節（續，J 節之後）新增 `IF_MaintITWarr`、`IF_MaintITPost`、`IF_WarrantyYrs`。
  - J4／J5（X19）：Spec_Rack F14 補 Bernstein 含網路註記（VR200 數值不改；SRC_HW_017 等級 3→2）；`IF_StaffSW` 標籤與 DC_Cost A46 補「（站點營運；不含平台研發）」。
  - J6（X20）：SRC_DC_014（IREN 29.0 $M/IT MW）與 `L1_CapexITMW_GB300_vsIREN`（基準 32.24，比值 1.11，±20% 內）。
  - 另 SRC_HW_065（Wolfe 4.3，Alt）、SRC_HW_066（TrendForce 比值）、SRC_DC_015–017（HPE、Supermicro 保固；DGX 續約 3.8%）；DB_Evidence E263–E278（A 段 N01–N16）；Decisions X16–X20；Gov_Map 判斷更新 6 列、新登錄 7 列；README A1、B5、新列 A33／B33。
- 主要數值（基準欄，$B/GW）：GB300 `IF_CapexIT` 37.446 → 32.237、`IF_MaintIT` 1.123 → 0.507、`IF_HoldEcon` 12.725 → 10.886、`IF_GPUhrEcon` 2.983 → 2.552 $/GPU-hr；VR200 `IF_MaintIT` 1.128 → 0.591、`IF_HoldEcon` 12.762 → 12.226（−4.2%）。
- builder：新增 `v531.py`（版本字串唯一來源；所有 Excel 擁有格的寫入皆有舊值守衛）；`gov.py`（formula_map 掛鉤、SRC 新紀錄與更新、Gov_Map、L1、Evidence、Decisions）、`build.py`、`finish.py` 接上；`v526._dc_rows` 容許 DC_Cost A46 標籤加註；`tools/gen_builder_md.py` 加 `v531.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（32 個檔）。
- 文件：README.md 下游名稱 192 → 195 與 I 節（續）說明；下游契約補 IT 維護兩段取用規則、IREN 對帳比值更新。
- 測試：`formula_cells` 45,543 → 45,788、`defined_names` 1,060 → 1,072、`src_names` 362 → 368、`l1_names` 210 → 213、`downstream_names` 192 → 195；成本相關期望值改為 v5.31 的 LibreOffice 重算值（見報告）。
- 治理：GOV_Errors 0、GOV_Warnings 220 → 221（W1：SRC_DC_014、SRC_DC_017 利害關係方無第二來源 +2，SRC_HW_007 改 Alt −1）、GOV_Info 165 → 168（I3 15 → 17：L1_GPUhr_GB300_vsBE、L1_GapProduct 判讀改為「差距 >20%」；I8 53 → 54：Spec_Rack E12 標記變更）。
- 前版合併雜湊：v5.30 `bc03f5c`（PR #35）補入下段。

## 20261008_Tokenomics_v5.30.xlsx（取代 v5.29；X15 定義更正：四層瀑布逐層累乘、L1_HoldEconMW 單位更正、IFW_ 上限標記；判斷類（chat 端定案，CC 執行），依工作單 `docs/workorders/20261008_v5.30.md` r0，試行 (B)）

- Commit：合併雜湊 `bc03f5c`（PR #35）；分支 `claude/v5.30-build`。報告：`docs/reports/20261008_v5.30.md`。底稿：master `a5061d9`（v5.29 合併，PR #31）＋工作單提交 `7720f72`；`model/CURRENT` 原為 v5.29。
- 依據：Andy 2026-10-08「請直接做」（八家公司模型審視報告 company-models PR #36–#43 共同指出的 Tokenomics 端問題）。**不改任何輸入值**。
- Excel（CC 以 `builder/` 自 v5.29 產生，經 LibreOffice 重算存檔）：
  - X15 (a)：Interface J 節四層瀑布改為逐層累乘、單調遞減——token 產能 `IFW_TokGW_*_Prod`＝`_Util` × CTL_ProdDerate（不再讀 Interface_Prod），`_Life`＝`_Prod`；營收 `IFW_*_Prod` 維持讀 G 節（Front 四組無 G 節者＝`_Util` × CTL_ProdDerate，取代「—」），`IFW_*_Life`＝`_Prod` × CTL_PriceLife × CTL_Monetize（不再讀 H 節）。H 節與 Interface_Prod 不動。VR200 基準欄：`IFW_TokGW_Sol` 2,373／1,424／1,916／1,916 → 2,373／1,424／**1,210**／**1,210** 億 M tok；`IFW_RevGW_Sol` 381.3／228.8／184.8／228.8 → 381.3／228.8／184.8／**184.8** $B/GW/年。自我檢查列改為 (i) 來源比對 11 列（營收 _Util＝D 節、token _100＝B 節）＋(ii) 單調檢查 11 列；Checks K3 加總兩者（0）。
  - X15 (b)：`L1_HoldEconMW_*`（含 `_Lo`／`_Hi`）改為 `=L1_HoldEconGW_*`（不除以 1000；1 $B/GW＝1 $M/MW），單位欄維持「$M/MW/年」，標籤改述；GB300 0.0127 → **12.72**、VR200 0.0128 → **12.76**、Hopper 0.0101 → 10.10、GB200 0.0092 → 9.17。
  - X15 (c)：`IFC_Use`（S 欄）對 `IFW_RevGW*`／`IFW_RevGWFleet*`／`IFW_RevGWFront*` 全部四層與 `IFW_TokGW_*_100` 附「；上限，不得作預測」（Y 欄應附旗標同步擴充；K2＝0）。
  - Decisions X15a–c；README A1、B5（置頂 v5.30）、A32／B32（瀑布說明改寫為逐層累乘）；Checks K2／K3 文字。
- builder：新增 `v530.py`（版本字串唯一來源；`interface_j` 取代 v529 版、`should_cap`、`checks_k` 文字、`l1_rows`、Decisions、README）；`v529.interface_contract` 加 `should_fn` 參數；`build.py`、`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v530.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（31 個檔）。以 v5.30 重建冪等 0 不符。
- 文件：下游契約 `docs/plan/Tokenomics_downstream_contract.md` 第 2 條第 2 項補「v5.30 起四層為逐層累乘、單調遞減」。
- 測試：`formula_cells` 45,383 → 45,543（Front 8 列改公式 120 格＋其輸出契約公式 40 格）；`defined_names` 1,060 不變；`L1_HoldEconMW_VR200` 期望值 0.012762 → 12.762016；v5.29 測試的「IFW_*_Life＝IF_*_Life」斷言移除（定義改變），新增 `test_v530_waterfall_running_product`；`b_prod_derate`（Serving C18＝0.7）情境的 GOV_Errors 0 → 57（K3 單調檢查：G 節以 0.85 取代 C18 重解，故營收 _Prod > _Util；列入報告「待 Project 判斷」第 1 項）。
- 治理：GOV_Errors 0、GOV_Warnings 220、GOV_Info 165（皆不變；K2 0、K3 0）。

## 20261008_Tokenomics_v5.29.xlsx（取代 v5.27；X14 (a)–(m)：輸出契約欄、四層瀑布、損益兩平與每 MW 介面、Load_Bearing、落差分解；SRC_DEM_018 新增（與 SRC_DEM_004 並列，r2）、每則提示 token 數 2,000 → 4,000；判斷類（chat 端定案）＋工程類，依工作單 `docs/workorders/20261008_v5.29.md` r1＋r2 執行，試行 (B)）

- Commit：合併雜湊 `a5061d9`（PR #31）；分支 `claude/v5.29-build`。報告：`docs/reports/20261008_v5.29.md`。底稿：master `862bdd4`（＝v5.27 合併 `19d667f`（PR #28）＋v5.28／v5.29 工作單與證據提交）；`model/CURRENT` 原為 v5.27（v5.28 為純網站工作單，不改 Excel，尚未建置）。
- 判斷類（Andy 2026-10-08「依建議」）：SRC_Demand 新增 `SRC_DEM_018`（OpenAI 2025 推論支出，Azure 帳單全年推估 12.6 $B，低 12.3／高 13.0，2 級、利害關係方、二手，E259）；第 1–2 輪將 `SRC_DEM_004` 改 Superseded 並把全部推論支出公式改連 018，**r2 改為兩筆並列 Active、只有支出路線服務 GW 用 018**（見下方 r2 段）。Alloc_In「每則提示 token 數」2,000 → 4,000（低 1,000 → 2,000、高 6,000 → 6,400），理由欄附加 E261。連動：Alloc 鏈、Interface F 節 IF_Alloc*、L1_Ans1／Ans2／ExtServeGW／ExtFreeShare／ExtDaily 改變（每日 token 11.48 → 16.48 T、token 路線服務 GW 0.0519 → 0.0675、支出路線 0.7427 → 1.1140、Q1 0.636 → 0.573）；其餘 IF_ 與模型頁數值逐格不變。
- Excel（CC 以 `builder/` 自 v5.27 產生，經 LibreOffice 重算存檔）：Interface R–U 輸出契約欄（Confidence／Decision Use／口徑層／最弱輸入更新日，`IFC_` 四名稱；V–Y 為輔助欄）與 J 節四層瀑布 `IFW_<name>_100／_Util／_Prod／_Life`（8 個營收列＋3 個 IF_TokGW 列，44 名稱）及自我檢查列；Gov_Map AG–AJ、SRC_Index F（`IDX_SrcDate`）為 builder 輔助欄；L1 新增 23 列（`L1_FleetBreakeven`、`L1_FleetMargin`、`L1_HoldEconMW_*`、`L1_TokMW_Gen_ratio_*`、`L1_HarVsGen_*`、`L1_PretrainFLOP_Astra_Ext`、`L1_AstraScale`、`L1_ScaleRD`、`L1_ScaleServe`、`L1_Gap*`）；Alloc_In 新增兩個 Assumed 輸入（`AL_SpendBasis` 2.0［1.5–3.0］、`AL_UtilActual` 0.35［0.3–0.4］）與常數 `CST_TokPerPromptV528`（Gov_Map GM596–GM600）；新頁 Load_Bearing（50 列，靜態展開）；SRC_Price X–AB 分層欄（檢查欄移至 AC–AE／AM）；Checks K1–K7；DB_Evidence E256–E262；Decisions X14a–X14m、G16（工作單稱 G15，該 ID 已存在）；Gov_Map 理由欄附註（GM236／237／593／594／586／453）；README A1／B5／B22、新增第 32 列。
- builder：新增 `v529.py`（版本字串唯一來源；所有 Excel 擁有格的寫入皆有舊值守衛）與 `deps.py`（建置時以公式文字靜態反查前置格；Confidence 與 Load_Bearing「影響的 L1 列」用）；`gov.py`（SRC 檢查欄依頁參數化、SRC_Index 審查日欄、L1 新列、X14 掛接）、`block6.py`（推論支出改連 `SRC_DEM_018`）、`build.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v529.py`、`deps.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（30 個檔）。以 v5.29 重建冪等 0 不符。
- 測試：期望值 `formula_cells` 39,461 → 45,337、`defined_names` 929 → 1,060、`src_names` 359 → 362、`l1_names` 141 → 210、`al_names` 80 → 86、`cst_names` 4 → 5、`idx_names` 3 → 4、工作表加 Load_Bearing；`GOV_Info` 108 → 168；Alloc 與 mix_2025 期望值依 (k)(l) 更新；`test_batch_etad_expected_values` 略過 (k)(l) 連動的 50 個名稱；`test_price_life_expected_values` 允許 L1_FleetMargin 列隨 L、m 改變；新增 `test_v529_contract_waterfall_expected_values`；`tests/app` L1 47 → 70 列、SRC_Demand 13 → 14 筆。
- 治理（第 1–2 輪）：GOV_Errors 0、GOV_Warnings 219（W1 219：SRC_DEM_018 +1、SRC_DEM_004 Superseded −1；K1 0）、GOV_Info 168（I3 8 → 17、K4 1、K5 50、K6 0、K7 0）；r2 後為 0／220／165（見 r2 段）。
- 前版合併雜湊：v5.27 `19d667f`（PR #28）補入下段。
- **r2 第 3 輪**（chat 端審查 PR #31 第九節後的判斷決定，工作單末節「r2 補充」，合併至 master `ca78a8f`（PR #32）；Andy 2026-10-08 授權）：(1) `SRC_DEM_004` 改回 Active、取代者清空、口徑欄加「json 一致集（與 005／006／007 同源）」；只有支出路線服務 GW（Alloc C61、L1_ExtServeGW 外部欄）連 `SRC_DEM_018`，Alloc C55（支出比 0.488 → 0.588）、C63（免費支出占比 0.310 → 0.464）、L1_ExtFreeShare 外部值（0.310 → 0.464）、L1_Ans5_GM 外部值（0.036 → 0.357）回到 004；Gov_Map GM453 改回連 004（R 8.4），附註「018 為 Azure 口徑，不用於比例」；Decisions X14k、DB_Evidence E259 決議欄同步改寫；連動：Alloc C56–C58 與 `IF_AllocImpliedNk`（1.322 → 1.983；v5.27 1.524）。(2) Checks K4 改為比對 `L1_FleetMargin` 與 Theory_Rev 機隊營收÷持有成本 × CTL_ProdDerate × CTL_PriceLife × CTL_Monetize（1 → 0）；L1_FleetMargin 讀法註明含折減（折減 1 時 3.82、基準 3.245）。(7) 反轉門檻改為 Gov_Map 新判斷欄「反轉門檻（v5.29）」（Excel 擁有；工作單寫 AI 欄，該欄已為 v5.29 的 IFC 輔助欄，故放第一個空欄 **AK**，builder 只建表頭、不覆寫內容）；Load_Bearing K 欄改公式讀該欄（本版「—」）。(10) L1_GapISL 讀法註明「D 為短提示端，非中點」。(11) L1_HoldEconMW_GB300、L1_FleetMargin 外部欄改「—」（判讀「無外部對照」），SRC_PRC_002 與 Ans5_GM 的對照改寫入讀法文字；I3 17 → 15。(3)(4)(5)(8)(9)(12)(13) 確認現狀，不改。
- r2 治理與測試：GOV_Errors 0、GOV_Warnings 219 → **220**（W1：SRC_DEM_004 維持 Active 故不再 −1）、GOV_Info 168 → **165**（I3 15、K4 0、K5 50、K6 0、K7 0）；`formula_cells` 45,337 → 45,383（Load_Bearing K 欄 +50、L1 M53／N53／M56／N56 改「—」−4）；`test_v529_contract_waterfall_expected_values` 期望依 r2 更新。
- **`IF_Alloc*` 六格前後值（r2 第 6 項；工作單「IF_ 全部不變」改為「除 `IF_Alloc*` 六格外不變」）**：v5.27 → v5.29：`IF_AllocQ1` 0.636 → 0.573；`IF_AllocQ1_R2` 0.667 → 0.629；`IF_AllocQ2` 0.664 → 0.603；`IF_AllocServeGW` 0.0519 → 0.0675；`IF_AllocDemand` 4,190,200,000 → 6,015,200,000；`IF_AllocImpliedNk` 1.524 → 1.983（PR #31 第 1–2 輪為 1.322；r2 支出比回到 004 後重算）；`IF_AllocRDGW` 0.0907 不變。下游 OpenAI 模型取數時核對版本。
- CI 第 1 輪（run 224／225）失敗兩項，第 2 輪修正：(1) `f_registry_t07_t09_on`（Hopper Sol SLO 不可達、每 GW 產出為 0）使 L1_TokMW_Gen_ratio_GB200 出現 #DIV/0!——新列的比值公式一律加「分母為 0 回傳 SLO 不可達」守衛（TokMW_Gen_ratio 三列與其低高、HarVsGen 世代比、GapISL）；基準數值不變。(2) `test_batch_etad_expected_values` 的 L1_Ans1 期望 0.0452 → 0.0530：(k)(l) 使服務 GW 上升，Q1 對研發 GW 的彈性改變（與 X10 無關）。

## 20261008_Tokenomics_v5.27.xlsx（取代 v5.26；X13 J8 證據與 L1 外部對照、Kimi K3 架構證據；CI 安裝失敗即停、ci-status 重跑殘留；判斷類（chat 端定案）＋工程類，依工作單 `docs/workorders/20261008_v5.27.md` r0 執行，試行 (B)）

- Commit：合併雜湊 `19d667f`（PR #28）；分支 `claude/v5.27-build`。報告：`docs/reports/20261008_v5.27.md`。底稿：master `3dd1216`（＝v5.26 合併 `4074684`＋本工作單提交）；`model/CURRENT` 原為 v5.26。
- 一手來源核對（CC 2026-10-08，WebFetch）：Epoch `frontier_ai_models.csv` GPT-6 Astra 列 notes 末句「…yielding a CI of ~[5e26, 2e27] FLOP.」相符；Grok 3 列 3.5e+26；Epoch「models over 1e25 FLOP」頁 Grok-3 仍為 4.6e+26（第 1.2 節採「不新增、不取代」一路）；Hugging Face `moonshotai/Kimi-K3` config.json 與模型卡（93 層、hidden 7168、896／16 experts；總參數 2.8T、啟用 104B 取自模型卡）。技術報告 PDF 讀取失敗。
- Excel（CC 以 `builder/` 自 v5.26 產生，經 LibreOffice 重算存檔）：SRC_MOD_055 低 5e26／高 2e27（新名稱 `_Lo`、`_Hi`）與備註；SRC_Model 新增 SRC_MOD_057–062（Kimi K3，1 級、利害關係方、純證據）；DB_Evidence E251–E255、E249 備註附加；Gov_Map 8 格理由欄附註；Decisions X13；L1 M36／N36 改連 `_Lo／_Hi`（O36 0.068 → 0.055、P36「差距 >20%」→「低於外部區間」）；L1 L39:N39 連 SRC_DEM_006（O39 — → 0.096、P39「無外部對照」→「差距 >20%」）、S39 文字；README A1／B5。Interface、L1 D:F、所有模型頁數值逐格不變。
- builder：新增 `v527.py`（版本字串唯一來源；所有寫入皆有舊值守衛）；`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v527.py`；`docs/builder/Tokenomics_builder_v5.md` 重新產生（28 個檔）。以 v5.27 重建冪等 0 不符。
- 工程類（CI）：`parity.yml` 兩個 LibreOffice 安裝步驟加 `shell: bash`（pipefail），`timeout-minutes` 10 → 25；`tools/install_libreoffice.sh` apt 逾時 90／180 → 180／420 秒、嘗試 2 → 3、成功分支驗證 `command -v soffice`；`tools/ci_status.py` 同名 artifact 只取最新一筆（failures 只彙整本次嘗試）。
- 測試：期望值 `formula_cells` 39,417 → 39,461、`defined_names` 921 → 929、`src_names` 351 → 359、`GOV_Warnings` 213 → 219、`GOV_Info` 107 → 108；`test_ci_status.py` 新增重跑去重測試。
- 治理：GOV_Errors 0、GOV_Warnings 219（W1 219、W2 0、H3 0）、GOV_Info 108（I3 7 → 8）。
- 前兩版合併雜湊：v5.25 `97e7b20`（PR #26）、v5.26 `4074684`（PR #27）已補入各段。

## 20261007_Tokenomics_v5.26.xlsx（取代 v5.25；Interface I 節 DC_Cost 構件 10 個下游名稱；工程類（CC 執行），依工作單 `docs/workorders/20261007_v5.26.md` r1，試行 (B)）

- Commit：合併雜湊 `4074684`（PR #27）；分支 `claude/v5.26-build`。報告：`docs/reports/20261007_v5.26.md`。底稿：分支 `claude/v5.25-build` `7180c86`（v5.25 PR #26 尚未合併，依 chat 端修訂採疊加；PR base＝`claude/v5.25-build`）；`model/CURRENT` 原為 v5.25。
- Excel（CC 以 `builder/` 自 v5.25 產生，經 LibreOffice 重算存檔）：Interface 第 218–229 列新增 I 節：`IF_DeprLifeIT`、`IF_DeprIT`、`IF_DeprFac`、`IF_AvgDraw`、`IF_PowerPrice`、`IF_MaintIT`、`IF_MaintFac`、`IF_StaffSW`、`IF_TaxIns`、`IF_OpexGW`（各連結 DC_Cost 第 38–42、44–48 列同欄；金額列 ÷ CTL_GW）與加總核對列（`IF_DeprIT＋IF_DeprFac＋IF_OpexGW − IF_HoldAcct`，15 欄皆 0）；README A1／B5 版本字串與新增第 31 列（I 節名稱說明）。與 v5.25 逐格比較：既有儲存格數值與公式 0 差異；公式格 39,252 → 39,417、具名範圍 911 → 921、工作表 56 不變。
- builder：新增 `v526.py`（版本字串的唯一來源；DC_Cost 列依 A 欄標籤定位）；`build.py`（H 節之後呼叫 `v526.interface_i`）、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v526.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生（27 個檔）。以 v5.26 重建冪等 0 不符。
- 網站：`app/` 的 Block 1 總覽表依名稱前綴自動納入新名稱（未改程式）。
- 測試：期望值 `formula_cells` 39,252 → 39,417、`defined_names` 911 → 921、`downstream_names` 182 → 192；`test_interface_d_e_shapes` 加 v5.26 名稱形狀檢查。
- 治理：GOV_Errors 0、GOV_Warnings 213、GOV_Info 107（皆與 v5.25 相同）。
- v5.25 段的合併雜湊：已於 v5.27 補上（`97e7b20`，PR #26）。

## 20261007_Tokenomics_v5.25.xlsx（取代 v5.24；X12 ISL／OSL 與 Astra 架構證據登錄、L1 前沿算力對照改 GPT-6 Astra；X11；判斷類（chat 端定案），依工作單 `docs/workorders/20261007_v5.25.md` r0 執行，試行 (B) 第二份）

- Commit：合併雜湊 `97e7b20`（PR #26）；分支 `claude/v5.25-build`。報告：`docs/reports/20261007_v5.25.md`。底稿：master `bdb0de7`（＝v5.24 合併 `098873a`＋本工作單提交）；`model/CURRENT` 原為 v5.24。
- 一手來源核對（CC 2026-10-07）：arXiv 2601.10088v1 HTML（4.3 節 Figure 14／15、4.4 節 Figure 17／18、4.1 節 Figure 10、2.3 節）與 Epoch `frontier_ai_models.csv`（GPT-6 Astra、Grok 3 列）逐項與工作單相符；Epoch `Confidence` 定義查得（records 文件頁）。
- Excel（CC 以 `builder/` 自 v5.24 產生，經 LibreOffice 重算存檔）：SRC_Demand 新增 `SRC_DEM_014`–`017`（OpenRouter，1 級、利害關係方、純證據）；SRC_Model 新增 `SRC_MOD_055`（GPT-6 Astra 訓練算力 1.0001e27，1 級、中立）；DB_Evidence E247–E250；Gov_Map GM248（Serving C24）低 `=Serving!C24*0.5`（512）→ 400、區間文字改寫，GM245–GM250、GM203–GM205、GM531 理由欄附註；Decisions X11、X12；L1 第 36 列 L、M、N、S 改為 `SRC_MOD_055`（O36 0.149 → 0.068，P36 仍「差距 >20%」）；README A1／B5。與 v5.24 逐格比較：差異全部在工作單第 4 節預期範圍內；Interface、L1 D:F、所有模型頁數值逐格不變。公式格 39,218 → 39,252、具名範圍 903 → 911、工作表 56 不變。
- builder：新增 `v525.py`（版本字串的唯一來源；所有寫入皆有舊值守衛）；`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v525.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生（26 個檔）。以 v5.25 重建冪等 0 不符。
- 測試：期望值 `formula_cells` 39,218 → 39,252、`defined_names` 903 → 911、`src_names` 343 → 351、`GOV_Warnings` 209 → 213；`test_batch_etad_expected_values` 的 k＝1 對 v5.22 比對改為跳過 `IDX_*`、`GOV_*`（新增 SRC 紀錄的連動，非 X10 範圍）。CI：push run 207、pull_request run 208（第 2 次嘗試）全部通過。
- 治理：GOV_Errors 0、GOV_Warnings 213（W1 213＋W2 0；W1 +4＝SRC_DEM_014–017）、GOV_Info 107（不變）。

## 20261007_Tokenomics_v5.24.xlsx（取代 v5.23；SRC_Perf 第 60–63 列舊句刪除；CI 只改文件的 push 不觸發；CHANGELOG 補合併雜湊；工程類，依工作單 `docs/workorders/20261007_v5.24.md` r0 執行，試行 (B) 第一份）

- Commit：合併雜湊 `098873a`（PR #25）；分支 `claude/v5.24-build`。報告：`docs/reports/20261007_v5.24.md`。底稿：master `10c0ca0`（v5.23 合併 `4d36786`＋本工作單提交）；`model/CURRENT` 原為 v5.23。
- Excel（CC 以 `builder/` 自 v5.23 產生，經 LibreOffice 重算存檔）：`SRC_Perf` 第 60–63 列（`SRC_PERF_056`–`059`，NVIDIA）W 欄刪除 v5.21 遺留句「（第二來源欄依 W1 規則不手動填）」，其餘文字原樣保留（4 格）；README A1／B5 版本字串。與 v5.23 逐格比較：數值差異 0、公式差異 0、文字差異只有上述 6 格；公式格 39,218、具名範圍 903、工作表 56 皆不變。
- builder：新增 `v524.py`（版本字串的唯一來源；`src_note_fix` 只在舊句仍存在時才改，每列先核對 A 欄 ID）；`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v524.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生（25 個檔）。以 v5.24 重建冪等 0 不符。
- 工程類（CI）：`.github/workflows/parity.yml` 的 `on.push` 加 `paths-ignore`（`docs/**`、`CHANGELOG.md`、根目錄 `README.md`、`CLAUDE.md`）；`pull_request` 不加；推標籤不評估路徑篩選，照常觸發（GitHub 文件）。
- 測試：期望值與斷言未改。
- 治理：GOV_Errors 0、GOV_Warnings 209、GOV_Info 107（皆與 v5.23 相同）。

## 20261007_Tokenomics_v5.23.xlsx（取代 v5.22；X10 Perf_Batch 側 VR200 批次口徑 η_d 倍數；SRC_Perf 備註文字修正；CI 穩定性三項；判斷類＋工程類，依工作單 `docs/workorders/20261007_v5.23.md` r0 執行）

- Commit：合併雜湊 `4d36786`（PR #24）；分支 `claude/new-session-ma4p0u`。報告：`docs/reports/20261007_v5.23.md`。底稿：master `a8ad27f`（含 v5.22 合併 `a5931f0`）；`model/CURRENT` 原為 v5.22。舊分支 `claude/new-session-mtq0pj` 上的 `bb2b707` 未沿用，v5.22 合併雜湊依工作單改在本版補記。
- Excel（CC 以 `builder/` 自 v5.22 產生，經 LibreOffice 重算存檔）：**X10** 新增 `CAL_BatchEtaD`（Calib 第 156 列 C:G，Calib I 節；VR200 格 F156＝0.75 藍字 Derived，其餘四格常數 1）；`Perf_Batch` 第 53 列 C:Q 與 `Perf_Batch_Prod` 第 53 列（主 C:Q 與自我檢查副本 S:AG）乘上 `INDEX(CAL_BatchEtaD,1,世代)`；Gov_Map GM595（Calib!F156，區間 0.70–1.0，P 欄高）；Decisions X10。訓練相關輸出數值改變（85 個具名範圍：IF 41、L1 21、AL 15、TRN 8），與 v5.22 報告第三節 k＝0.75 逐項相符；`IF_TrainGenDefault` 仍為 4；`TR_*`、`IF_RevGW_*`、`IF_RevGWFleet`、`_Life` 不變。`SRC_Perf` 第 56–63 列 W 欄備註文字修正（8 格）。
- builder：新增 `v523.py`（版本字串的唯一來源）；`build.py`、`gov.py`、`finish.py` 接上；`tools/gen_builder_md.py` 加 `v523.py` 位置；`docs/builder/Tokenomics_builder_v5.md` 重新產生。
- 工程類（CI）：(1) `tools/install_libreoffice.sh`：只裝 `libreoffice-calc`（`--no-install-recommends`）、apt 重試與逾時、失敗重試一次（run 189 因 libreoffice-core 下載約 19 分鐘逾時）；(2) `ci-status` 的 `jobs` 每筆加 `python` 欄（各 job 上傳 `pyver-*` artifact，`tools/ci_summary.py pyver`）；(3) actions 升級：checkout v4→v5、setup-python v5→v6、upload-artifact v4→v6、download-artifact v4→v7（皆為首個以 Node.js 24 為預設的主版本）。
- 測試：期望值 `formula_cells` 39,198 → 39,218、`defined_names` 902 → 903、`display_only_names` 139 → 140、`cal_names` 19 → 20；新增情境 `h_batch_etad_100`（情境總數 25 → 26）與 `test_batch_etad_expected_values`、`test_ci_status.py` 2 項。
- 治理：GOV_Errors 0、GOV_Warnings 209、GOV_Info 107（皆與 v5.22 相同）。

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

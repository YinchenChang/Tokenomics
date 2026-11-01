# 工作單草稿｜月度證據更新 20261101 的 SRC 同步（草稿，判斷類待 chat 端定案）

日期 2026-11-01 草擬　基準 master `90f7deb`（CURRENT `20261025_Tokenomics_v21.7.xlsx`）　依據 `docs/evidence/20261101/candidates.csv`（E412–E475）、`summary.md`。
格式仿 `docs/workorders/20261029_決定變數證據_C段.md`。**本草稿不是工作單**：第 1 節的每一項都是判斷類（改 SRC Active 值、等級、出處屬 Decisions G2），要 chat 端逐項定案、改寫成正式工作單後 CC 才動手；第 2 節為定案後可一併執行的工程類。

## 0. 版本號預判

- 若只做第 2 節（等級、出處、第二來源欄、審查日、DB_Evidence 登錄）：修補版（v21.8）。
- 若採 1-A（Nebius 4 → 5）或 1-B（VR200 19.2／1.5）：SRC Active 值改變 → 次版（v22.0）。
- 若採 1-C（AA v5.0 整欄重基準）：Cap_In F 節 I／J 欄 11 格與 SRC_CAP_001–011 全部取代，Price_Frontier 前緣可能改變 → 次版；若連帶改層級代表或契約名稱 → 主版。

## 1. 判斷類（待 chat 端定案；每項附預設）

| 項 | 候選 | 內容 | 預設（未回應即照此） | 理由一句 |
|---|---|---|---|---|
| 1-A | E467 | SRC_DC_008 Nebius GPU 折舊 4 → 5 年；Inputs!F23（高成本情境）4 → 5；Inputs 第 23 列說明改「Nebius 2026 起 5 年、Lambda 5 年；高成本情境取 5」；Evidence 填 E467；出處改 20-F FY2025 ＋ 6-K Q2 2026；等級 2 → 1 | **採**（一手監管文件，Active 值已過時） | 高成本情境失去 4 年的實證錨點；影響只在 `_Hi` 欄（經濟持有成本約 −10～−12%） |
| 1-B | E445 | SRC_HW_030 22 → 19.2 TB/s（Spec_Rack!F26；現值 22 只見第三方報導）；SRC_HW_049 1.8 → 1.5 TB/s（Spec_Rack!F27，單向＝雙向 3.0 ÷ 2；NVIDIA 2026-01／03 文件為 3.6 雙向）；備註寫明現行頁標 Preliminary、全架 1,400 TB/s ÷ 72＝19.44 | **暫不採，列區間**：F26 區間 19.2–22、F27 區間 1.5–1.8，基準不動；等正式 datasheet | 同一廠商前後不一且標 Preliminary；高敏感度世代欄不宜以預告頁翻盤 |
| 1-C | E438、E462 | Cap_In F 節能力指數整欄改 v5.0：須先由 chat 端查齊 F 節 13 個模型（現有 I 欄分數 10 格、「待查」3 格；另加 Terra、Haiku 5.5）的 v5.0 分數；SRC_CAP_001–011（11 筆，含未連結的 GPT-5.6 Sol）以新紀錄取代，舊紀錄 Superseded；J 欄版本改 v5.0；重看前緣選取 | **採，但分兩段**：A 段（唯讀）查齊分數並比對前緣是否改變；B 段再改 Excel | 跨版本不可比，一格一格改會產生混版 |
| 1-D | E450 | SRC_HW_052 GB300 機架價：新增 Alt 紀錄「採購單 just under $5.0M（無 CDU，Wing VC 2026-08）」，Spec_Rack E11 區間高端 4.0 → 5.0；基準 4.0 不動 | **採區間不採基準** | 二手無原件 |
| 1-E | E455 | SRC_DC_002 JPM AM 15%：下月再查兩份 EOTM；若仍無，改標 Assumed、出處改「無法核實（原記 JPM AM）」，並在 Decisions 記更正（修訂九例外） | **延一月** | 來源無法核實但只影響高成本情境 Inputs!F13 |
| 1-F | E464 | SRC_DEM_088 Codex 2 兆：補「40 兆」原文或改標 Assumed | **延一月** | 僅對照列，不驅動 |
| 1-G | E428 | 新增 SRC_PRC_050「MiniMax M3 快取輸入 0.06 $/M（≤512K）」並填 Cap_In!F58 | **採** | 一手牌價；只影響候選表 |
| 1-H | E424 | SRC_PRC_028 備註補「不含中國法定假日；年化尖峰時數約低 4–5%」；Cap_In!C17 不改 | **只補備註** | 口徑說明，不改值 |
| 1-I | E452 | SRC_DC_004 指標名「液冷溢價（Turner & Townsend）」更正為「AI 資料中心對傳統建造溢價（T&T）」；原字樣保留稽核欄；新增 Alt「JLL 液冷溢價 10%」；Decisions 記更正 | **採**（修訂九更正例外） | 標籤與原文不符 |
| 1-J | E415、E421 | gpt-6.1-terra（1.00／0.05／5.00）、Claude Haiku 5.5（0.10／—／0.50）是否入 Cap_In F 節 | **併 1-C A 段一起看**（有 v5.0 分數才有意義） | 候選表以價格×能力選前緣 |
| 1-K | E463 | SRC_DEM_071 OpenAI API 份額區間 0.15–0.20 是否放寬上緣至 0.27（Sacra 2026-03） | **不改，備註登錄** | Sacra 自家兩頁不一致 |
| 1-L | E470 | CAL_BatchEtaD GB200 是否以 SGLang 13,386 重解區間上端 | **不改，備註登錄；排入下次 η 校準** | 不同量化（NVFP4 MoE）與框架，需 Calib J 節複本列重解 |

## 2. 工程類（定案後由 CC 一次執行；不改任何數值）

1. **等級與出處升級（值不變）**：依 candidates.csv「取代（等級 … 值不變）」各筆改 SRC 的來源等級、出處、一手／二手、日期、審查日＝2026-11-01：
   - SRC_Price：PRC_001（3→1，coreweave.com/pricing）、PRC_012–020（2→1，platform.claude.com pricing）、PRC_038–040（2→1，alibabacloud.com 2026-10-11）、PRC_043/044（2→1，platform.minimax.io）、PRC_049（2→1）。
   - SRC_HW：HW_019/020/021/056（3→1，nvidia.com/h100；019 備註「稀疏 1,979 ÷ 2，Derived」）、HW_023/026/057/058/059/048（3→1，Blackwell Ultra 技術部落格 2025-08-22）、HW_041/042（3→1，nvidia.com/gb200-nvl72；042 備註 Derived）、HW_060（3→1，CX-7 datasheet）、HW_031/044（3→2，DCD）、HW_051（3→2；出處改「HSBC 估計經 Barron's Tae Kim X 貼文 2024-05-13」，日期補 2024-05）。
   - SRC_DC：DC_003（3→1，JLL 2026-01；備註 MW 口徑＝50 MW 氣冷 shell & core）、DC_001（3→1，hedgehog 2026-06-08；出處刪 JPM）、DC_010/011（3→2，Forbes 2025-09-22）、DC_007（2→1，10-K FY2025；第二來源欄填新增的 SiliconANGLE 紀錄）。
   - SRC_Model：MOD_020–021（3→1，arXiv，見下）、MOD_022–028、049–051（3→1，HF config.json；共 10 筆）、MOD_039–042（3→1，arXiv 已讀）、MOD_001/003/004/008/018/019（3→1，V4-Pro 模型卡與 config）、MOD_005（3→1，V4-Flash 模型卡）。
   - SRC_Perf：PERF_023（3→1，open-infra-index Day 6；值建議改區間 20–22 → 此點屬判斷類，先只改等級）、PERF_036/037（出處改一手已讀）、PERF_074（URL 改 2026-02-03-dsr1-gb200-part1）。
2. **第二來源欄**：SRC_MOD_029 ← 新增 DataNorth 2026-08-03 紀錄；SRC_PERF_037 ← MLOps Newsletter 2024-09-08；SRC_PERF_074 ← LMSYS 2025-09-25（13,386）；SRC_DEM_012 ← NBER WP 34255（2,627M／日）。新增紀錄狀態 Alt。
3. **新增 Alt／對照紀錄（不連結模型格）**：CoreWeave spot 與 H200（E430）、Verda 五機型（E431）、Nebius B300／H200（E432）、Host Digital 兩案 colocation 每 MW-IT 年化（E434；等級 2、利害關係方、付費稿）、GLM-5.3-FlashX、MiniMax M3.1-Flash、gpt-6.1-terra、Claude Haiku 5.5 牌價（E415、E421、E425、E428）。價格層欄：隨需／spot／預留（折扣率）／長約（colocation）。
4. **DB_Evidence**：E412–E475 依 CSV 登錄，狀態欄：取代與並列者「待判定」、不採納者「已處理」、待 Andy 者「待 Andy」；E014（Opus 5.5 牌價）可結案為「已處理」（E419）。
5. **Checks／GOV**：重算後 `GOV_Warnings`（W2 3 級×高段、利害關係方缺第二來源）應下降；`GOV_Errors` 維持 0；`RNG_StaleFlag` 若因 1-A／1-B 改輸入而顯示「區間過期」，重跑 `tools/gen_ranges.py` 與 `gen_fingerprint.py`。
6. 驗收照 CLAUDE.md 第 3、4 節：LibreOffice 重算錯誤 0、parity 全套、冪等、逐格比較差異落在本工作單「預期變動」內；報告表 1 逐項對應上表。
7. **先修 CI**：GitHub Actions `parity` 自 2026-10-28 起在 master 即為紅（`tests/parity/test_v2010.py` 第 246 行 f-string 內含反斜線，Python 3.11 收集階段 SyntaxError；workflow 用 3.11，本機若為 3.12 不會察覺）。修法：把 `re.findall(r'[$](\d+)', ...)` 移出 f-string 先賦值再代入。屬工程類，一行、不改數值；建議在本工作單執行前先合併修正，否則本機 parity 與 CI 持續不一致（依修訂六列「待 Project 判斷」）。

## 3. 預期變動（供逐格比較）

- 只做第 2 節：數值變動 0 格；文字變動限 SRC_\* 的等級、出處、一手／二手、日期、審查日、第二來源、備註欄與 DB_Evidence 新列；Gov_Map S／T 欄（SRC 狀態、等級）隨之改變；Checks G 節計數改變。
- 加 1-A：Inputs!F23、DC_Cost 第 38／39／44／52／53／55 列高成本欄（5 世代）、Interface／L1 所有 `_Hi` 成本欄；基準欄 0 變動。
- 加 1-G：Cap_In!F58、Price_Frontier MiniMax 列。
- 加 1-B／1-C／1-D：見第 1 節；B 段另發工作單。

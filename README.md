# Tokenomics

AI 推論的物理推導模型：**Excel 活頁簿是唯一事實來源**（`model/YYYYMMDD_Tokenomics_vN.xlsx`），
本 repo 只**執行**與**呈現**它。規範見 [CLAUDE.md](CLAUDE.md)。

## 結構

| 路徑 | 內容 |
|---|---|
| `model/` | 現行活頁簿（唯一一份）；舊版在 `model/archive/` |
| `tests/parity/` | 數值檢查與情境檔：以 LibreOffice 重算現行活頁簿與每個情境，檢查錯誤值、防空轉、各版本期望值、具名範圍與 GOV_Errors |
| `legacy/` | **網站暫停（CLAUDE.md 修訂八）**：公式引擎（`legacy/engine/`）、Streamlit 網站（`legacy/app/`）及其工具（`legacy/tools/`），以及早先停用的 v4 手抄公式；程式保留，不執行、不列入 CI |
| `tests/legacy/` | 暫停的網站與引擎測試（`app/`、`test_functions.py`）及舊 v4 測試，不列入 CI |
| `docs/reports/` | 每輪報告（繁體中文） |
| `CHANGELOG.md` | 每次同步的 Excel 版本、commit、變動摘要 |

## 具名範圍與下游連結

Excel 的具名範圍分為兩類（見 Excel README 頁）：

- **`IF_` 開頭且非 `IF_Hdr`**（195 個；v5.31，v5.26–v5.30 為 192 個）：Interface 輸出，**下游模型（OpenAI、CRWV、Nebius 等）只連結這一類**。
  - v5.26 新增 Interface I 節「DC_Cost 構件」10 個（下游公司模型的每 MW 營運成本用；金額 $B/GW/年，比率與年限不換算）：`IF_DeprLifeIT`（IT 折舊年限，年）、`IF_DeprIT`（IT 折舊）、`IF_DeprFac`（廠房折舊，土地不折舊）、`IF_AvgDraw`（平均用電 ÷ 配電設計功率）、`IF_PowerPrice`（電價，$/kWh）、`IF_MaintIT`（IT 維護）、`IF_MaintFac`（廠房維護）、`IF_StaffSW`（人員、軟體、水與耗材）、`IF_TaxIns`（財產稅與保險）、`IF_OpexGW`（營運費用小計，不含折舊、含電費）。`IF_DeprIT＋IF_DeprFac＋IF_OpexGW＝IF_HoldAcct`（I 節末列核對）。
  - v5.31 新增 Interface I 節（續，放在 J 節之後，既有名稱不位移）3 個：`IF_MaintITWarr`（保固期內 IT 維護＝IT 資本 × Inputs 第 37 列費率）、`IF_MaintITPost`（保固期滿後＝IT 資本 × 第 38 列費率），金額 $B/GW/年，下游公司模型依自身機隊年齡取用、兩者不加總；`IF_WarrantyYrs`（IT 原廠保固年限，單格，年；Inputs 第 36 列＝SRC_DC_015）。`IF_MaintIT` 改為壽命期等值費率（Inputs 第 30 列公式：兩段費率以同欄 WACC 與 IT 折舊年限年金加權），`IF_StaffSW` 標籤註明「站點營運；不含平台研發」。
  - v5.32 不新增 `IF_` 名稱（下游取數契約不變）。變現率 m 追蹤放在 Cap_In H 節（第 66–108 列）與 L1：`L1_MImplied`（合併路線、模型 token 分母）、`L1_MImplied_Ext`（合併路線、Epoch 外部 token 分母），各含 `_Lo`／`_Hi`；外部欄＝`CTL_Monetize`，判讀「落在 Gov_Map 區間內／外」。模型 token 分母已知偏低（`L1_ScaleServe`），`L1_MImplied` > 1 代表分母問題，不代表 m > 1；`CTL_Monetize` 基準 1 不改（Decisions X26）。
  - v5.33 不新增 `IF_` 名稱（下游取數契約不變）。**5 個 `IF_Alloc*` 數值改變**（2025 基準年服務世代組合改為 Hopper 60／GB200 40／GB300 0／VR200 0，Decisions X28）：`IF_AllocQ1` 0.573 → 0.332、`IF_AllocQ1_R2` 0.629 → 0.420、`IF_AllocQ2` 0.614 → 0.394、`IF_AllocServeGW` 0.0675 → 0.1826 GW、`IF_AllocImpliedNk` 1.98 → 5.36；`IF_AllocDemand`、`IF_AllocRDGW` 不變。機隊口徑放在 Cap_In H7（第 108–130 列）與 L1：`L1_MFleet`（機隊 m，點估計 0.81；外部欄＝`CTL_Monetize`，判讀「落在 0.3–1.0 區間內」）、`L1_TokCeiling`（機隊付費 token 上限 1.20 × 10¹⁰ M tok／年；外部欄＝`AL_DPaid`，判讀「需求路線 ÷ 上限」），各含 `_Lo`／`_Hi`；Checks M2（需求 > 上限）、M3（機隊 m 區間外）為 WARN，依現值不觸發。
  - v5.34 不新增 `IF_` 名稱、**既有 `IF_`／`L1_` 數值全部不變**（`B4_Disc` 基準 0.2 不改，只有高端 0.3 → 0.4，`IF_Price*` 不變；`CTL_Monetize` 不改，Decisions X35）。變現率 m 細化放在 Cap_In H8（m 分拆：營收三分 消費訂閱／商用席次／API × token 三分）、H9（token 帳三路線與閉合解）、H10（m 季度序列 2025／2026 Q1／Q2／FY2026，顯示用）與 L1 六個新名稱：`L1_MAPI`（m_API 2025 三分法 0.56）、`L1_MSub`（m_消費訂閱 4.26）、`L1_MSeat`（m_商用席次 1.83）、`L1_MixFactorAPI`（m_API 隱含組合因子 0.56）、`L1_TokPerPromptClose`（閉合解 τ* ≈ 13,950 每則 token）、`L1_MAPI_Anthropic`（J21 對照：文字「缺分母」，外部欄＝Anthropic 用量計費占營收 0.83／雲端分潤比 0.16），各含 `_Lo`／`_Hi`；Checks M4（需求 ÷ 機隊 < 0.5 或 > 2）為 WARN，依現值 0.465 觸發（預期）。另加 `B4_Disc_Lo`／`B4_Disc_Hi`（Cap_In D12／E12 端點，顯示用，下游不得連結）。
  - v5.36 不新增 `IF_` 名稱、**所有 `IF_` 數值逐格不變**（下游契約不動）。支出路線改連 `SRC_DEM_004`（Lo 7.5／Hi 8.8；新增 `SRC_DEM_073` 稽核後營收成本 7.5，`SRC_DEM_018` 降為顯示對照列）；計價倍數 2.0 → 1.3（區間 1.0–1.6）；新增 κ（`AL_Kappa` 1.0，區間 0.65–1.2）乘入有效服務 GW，`L1_GapISL`＝1/κ；`L1_GapPrompt` 改為有效倍數 1.3013、`L1_GapUtil`＝`IF_Util`÷`AL_UtilActual` 1.7143，缺口恆等式與 Checks M5 放在 Cap_In J 節；L1 新增 `L1_ScaleServe2000`、`L1_PriceRealFleet`、`L1_PriceRealDemand`、`L1_PriceReqBE`、`L1_PriceRho`（各含 `_Lo`／`_Hi`）。主要變動：`AL_ServeGWSpend` 1.347 → 0.898、`L1_ScaleServe` 7.378 → 4.919、`L1_MFleet` 0.810 → 0.790、`L1_LReqFleet` 0.365 → 0.374、`L1_TokPerPromptClose` 13,950 → 14,426。
  - v5.35 不新增 `IF_` 名稱、**既有 `IF_`／`L1_` 數值全部不變**（`CTL_PriceLife`／`CTL_Monetize` 皆維持 1，Gov_Map 區間 0.3–1.0 不改，Decisions X42）。L 拆分放在 Cap_In I 節（第 225–243 列）與 L1 四個新名稱：`L1_LPrice`（牌價分項 0.7412；g −0.10、T＝`IF_DeprLifeIT` 6 年）、`L1_LDemote`（降級分項 0.867；T1 4 年、ρ 0.5）、`L1_LTotal`（0.6426＝L_price × L_demote；外部欄＝`CTL_PriceLife`，判讀「落在 0.3–1.0 區間內」）、`L1_LReqFleet`（回本所需 L，m＝`L1_MFleet` → 0.3645；外部欄＝`L1_LTotal`，判讀「回本（L_total 口徑）」），各含 `_Lo`／`_Hi`。H10 m 季度序列修正（J23）：三分營收改以 m 分子營收（營收 − 廣告）為基底、廣告每欄各自輸入（2026 Q1 0／Q2 0.5／FY2026 1.0）、2026 消費訂閱占付費 token 份額 0.65（2026 Q2 m_API 0.340、m_消費訂閱 5.399、m_商用席次 4.557、m_整體 1.343 不變）；原「中階牌價指數」預留列改為連結 L_price（顯示用，不乘入單價）。
  - v19.0 新增 Interface N 節「P×Q 取數」25 個（`IF_Disc`、`IF_MixPaid_*`、`IF_MixFree_*`、`IF_UtilActual`、`IF_ProdDerate`、`IF_FleetProdRatio_VR200`、`IF_PxEffMix`、`IF_PxEffMix25`、`IF_LTotalDisc`、`IF_LTotalFleetVDisc`〔含 `_Lo`／`_Hi`〕與 15 欄的 `IF_TokGWPaidMix`）：下游做營收＝P × Q、實際 m×L ÷ 所需 m×L 時，每 GW 參數只從這裡取（`B4_*`、`AL_*`、`L1_*`、`CTL_*` 不得直接連結）；公司層級計算放 company-models。全部是既有格的引用或組合，既有名稱的值不變。
- **`IF_Hdr*`（`IF_HdrGen`、`IF_HdrCost`、`IF_HdrTask`）、`DRV_*`、`CAL_*`、`TRN_*`、`TR_*`、`B4_*`、`B5_*`、`CTL_*`**：僅供本網站顯示（表頭、推導鏈、Calib 驗證表、Tech_Registry 唯讀表）、內部用或輸入控制，下游不得連結。
  `B4_*`（41 個；v5.34 加 `B4_Disc_Lo`／`B4_Disc_Hi`）與 `B5_*`（24 個；v5.9 新增、v5.10 加 `B5_PFloor`）是 Block 4、Block 5 的顯示或內部用名稱（Cap_In／Har_In 輸入、市場候選表、有效單價列、選定 harness 檔案等），**下游一律不得連結**，應改連 `IF_` 的 Block 4、5 輸出（Interface D、E 節）。

## 變現率 m 的定義（Andy 2026-10-21，權威）

- **m ＝ 有效牌價的進一步打折程度**（收費業務 token 的有效牌價變現率）：實收單價 ÷ 有效牌價。有效牌價 ＝ 表列牌價 ×（1 − d），d＝預設折扣（`B4_Disc`，基準 20%，**為可調輸入，不得寫死**）。
- **m 只有收入面**（Andy 15:39、15:59）：m 跟營收有關，跟成本無關；免費服務與訓練研發算力不產生營收，計入管理費用，不進 m（14:37）。m 的證據只取收入面，不得經由成本鏈（推論支出 → 持有成本 → GW → token）反推。
- **影響 m 的變數（全部是收入面）**：API 實收價（含 Batch／Flex 折扣、優先處理溢價、快取輸入計價）、訂閱方案定價、企業折扣（承諾用量合約）、訂閱用戶的用量分布（重度與輕度用戶的人數與比例）；chat 端補列：訂閱方案用量上限／速率限制、年繳與月繳折扣、促銷與試用額度、區域定價、經雲端市集或合作夥伴的營收分成（毛額與淨額口徑）、退款與壞帳。
- **與 token 帳係數分開**：現行模型的 m 數字（`L1_MFleet` 0.460；14:45 試算的 0.740）以成本鏈推付費 token 再反推，＝ m ×（真實付費 token ÷ 模型推算付費 token），混有 token 帳誤差，不得當作 m 使用；token 帳誤差歸入數量 Q 側處理。
- **每 GW 營收一律以 P × Q 由基本定義計算**（Andy 15:59）：Q ＝ 付費服務 token（GW × 對外服務占比 ×（1 − 免費占比）× 實際利用率 × 生產折減 × 每 GW 付費產能）；P ＝ 層級表列牌價 ×（1 − d）× m × 價格路徑（g、L）。不得以「對 2025 的比例」推算新世代營收；2025 實際營收只作回測。
- 用語：$1.359／M（`CAP_Price25Mix`、`AL_PriceFleet25`）是「有效牌價」，不是表列牌價。
- **模型名稱（v18.0 起，Excel `20261021_Tokenomics_v18.0.xlsx`）**：收入面 m 為 `L1_M`（主口徑＝2026 Q2 年化；另有 `L1_M_2025`／`_2026Q1`／`_2026Q2`／`_FY2026`），分項 `L1_M_API`／`_Sub`／`_Seat`，單價 `L1_PxEff_2026`（有效）／`L1_PxList_2026`（表列）；VR200 每 GW 營收以 P × Q 計算為 `L1_RevGW_PQ_VR200`（`_FY`、`_Life` 為變體）；舊 `L1_MFleet` 等為 token 帳診斷（`L1_TokLedger`＝模型付費 token ÷ 需求面付費 token），不是 m。細節見下游契約 v0.20 與 Decisions SL52-01…06。
- **回本成本範圍（Andy 2026-10-21 14:55）**：只算與該 GW 算力相關的成本——付費服務、免費服務、訓練、研發所用算力的全部持有成本（多 GW 時同理）；算力以外的管理成本暫不計，與暫不計廣告營收同理。現行 2025 主口徑 `L1_LReqFleet_IdNoK`（＝0.756）只含推論、不含訓練研發，與此不一致，待改版；含訓練（SRC_DEM_006 12 $B）約 1.84。
- **定義由 Andy 給、Tokenomics 依定義取數（Andy 2026-10-22 04:41）**：Andy 原話「以後這些問題，我可能就會用我自己比較可以理解的方式去做定義……然後 tokenomics 就可以根據這個定義去拿取它裡面已經有的這些資料去做計算」。Tokenomics 是事實根據，只放基本資訊；特質化（公司特有）的內容另外處理。新增輸出前，先寫明定義（待解變數、固定量、觀測量），再取數。
- **營收拆解與 m×L 回本條件（Andy 2026-10-22 04:41）**：每 GW 模型商營收 ＝ P × Q；P ＝ m × L ×（1 − d）×（表列牌價）；Q ＝ 實際用於服務的算力（分世代機隊）× 每單位算力產出的 token（分高中低層級）。以已知營收與 Q 反推實際的 m×L，再與回本所需的 m×L 比較（2025：營收 130.7 億；2026：市場傳聞 360 億，Interested-party）。L 的讀法待 Andy 確認（10-22：預設沿用 10-18 定義＝壽命期價格係數，表列牌價另為一因子）。判讀重點是比值「實際 m×L ÷ 所需 m×L」的年度趨勢，不是單年絕對值（Andy 2026-10-22 04:51）；趨勢只在各年使用同一成本口徑時成立（固定倍數才會約掉），序列須按成本口徑分列。成本口徑（Andy 2026-10-22 05:01）：年度總算力成本＝當年平均上線 GW × Σ（世代占比 × 該世代每 GW 年持有成本）；外部揭露的算力支出只作對照。**計算一律先從 Tokenomics 取數**（Andy 2026-10-22 05:15）：就算 Tokenomics 的數字有錯，也能知道錯在哪；Tokenomics 沒有的才外找，先依 DB_Evidence 規則登錄進 Tokenomics 再使用。2025 推論＋訓練支出合計 204 億（SRC_DEM_004＋006）與「平均 GW × 每 GW 持有成本」（約 1 GW × 93.5 億）不一致，不作為算力成本，只作對照，待修正（Andy 05:15）。**分層（Andy 2026-10-22 05:19）**：Tokenomics 只提供每 GW（分世代、分層級）的持有成本、產能與牌價；公司層級的機隊規模（如 OpenAI 2026 平均上線 GW）、營收與 m×L 比值序列放在 company-models 各家模型，經 Interface 取用。

## 執行

網站暫停（CLAUDE.md 修訂八）；`python tokenomics.py` 與 `run_local.bat` 只印出暫停訊息。恢復網站時，安裝 `requirements-legacy.txt`，並先由 Project 端決定是否恢復引擎。

匯出 SRC_／Interface CSV 並檢查 GOV_Errors（以 LibreOffice 重算 `model/CURRENT`）：`python3 tools/export_csv.py --out data/export`。

## 測試

```bash
sudo apt-get install -y libreoffice-calc      # 重算用
pip install -r requirements-dev.txt
python -m pytest tests/parity                  # 全套約 10–15 分鐘；超過 2 分鐘請背景執行
```

數值檢查在本機執行，通過即可合併；CI（`.github/workflows/parity.yml`：單一 parity job＋governance）供事後對照，不阻擋合併。

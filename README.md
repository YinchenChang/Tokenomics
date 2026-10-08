# Tokenomics

AI 推論的物理推導模型：**Excel 活頁簿是唯一事實來源**（`model/YYYYMMDD_Tokenomics_vN.xlsx`），
本 repo 只**執行**與**呈現**它。規範見 [CLAUDE.md](CLAUDE.md)。

## 結構

| 路徑 | 內容 |
|---|---|
| `model/` | 現行活頁簿（唯一一份）；舊版在 `model/archive/` |
| `engine/` | 以公式引擎（pycel）直接計算 xlsx，不手抄公式 |
| `app/` | Streamlit 網站：只讀 Interface 具名範圍（＋Calib 驗證表、Block 4、5 頁的 `B4_`、`B5_` 顯示名稱） |
| `tests/parity/` | Excel（LibreOffice 重算）與 engine 的一致性測試與情境檔 |
| `tests/app/` | 網站煙霧測試 |
| `legacy/`、`tests/legacy/` | 已停用的 v4 手抄公式與舊測試（不列入 CI） |
| `docs/reports/` | 每輪報告（繁體中文） |
| `CHANGELOG.md` | 每次同步的 Excel 版本、commit、變動摘要 |

## 具名範圍與下游連結

Excel 的具名範圍分為兩類（見 Excel README 頁）：

- **`IF_` 開頭且非 `IF_Hdr`**（195 個；v5.31，v5.26–v5.30 為 192 個）：Interface 輸出，**下游模型（OpenAI、CRWV、Nebius 等）只連結這一類**。
  - v5.26 新增 Interface I 節「DC_Cost 構件」10 個（下游公司模型的每 MW 營運成本用；金額 $B/GW/年，比率與年限不換算）：`IF_DeprLifeIT`（IT 折舊年限，年）、`IF_DeprIT`（IT 折舊）、`IF_DeprFac`（廠房折舊，土地不折舊）、`IF_AvgDraw`（平均用電 ÷ 配電設計功率）、`IF_PowerPrice`（電價，$/kWh）、`IF_MaintIT`（IT 維護）、`IF_MaintFac`（廠房維護）、`IF_StaffSW`（人員、軟體、水與耗材）、`IF_TaxIns`（財產稅與保險）、`IF_OpexGW`（營運費用小計，不含折舊、含電費）。`IF_DeprIT＋IF_DeprFac＋IF_OpexGW＝IF_HoldAcct`（I 節末列核對）。
  - v5.31 新增 Interface I 節（續，放在 J 節之後，既有名稱不位移）3 個：`IF_MaintITWarr`（保固期內 IT 維護＝IT 資本 × Inputs 第 37 列費率）、`IF_MaintITPost`（保固期滿後＝IT 資本 × 第 38 列費率），金額 $B/GW/年，下游公司模型依自身機隊年齡取用、兩者不加總；`IF_WarrantyYrs`（IT 原廠保固年限，單格，年；Inputs 第 36 列＝SRC_DC_015）。`IF_MaintIT` 改為壽命期等值費率（Inputs 第 30 列公式：兩段費率以同欄 WACC 與 IT 折舊年限年金加權），`IF_StaffSW` 標籤註明「站點營運；不含平台研發」。
- **`IF_Hdr*`（`IF_HdrGen`、`IF_HdrCost`、`IF_HdrTask`）、`DRV_*`、`CAL_*`、`TRN_*`、`TR_*`、`B4_*`、`B5_*`、`CTL_*`**：僅供本網站顯示（表頭、推導鏈、Calib 驗證表、Tech_Registry 唯讀表）、內部用或輸入控制，下游不得連結。
  `B4_*`（39 個）與 `B5_*`（24 個；v5.9 新增、v5.10 加 `B5_PFloor`）是 Block 4、Block 5 的顯示或內部用名稱（Cap_In／Har_In 輸入、市場候選表、有效單價列、選定 harness 檔案等），**下游一律不得連結**，應改連 `IF_` 的 Block 4、5 輸出（Interface D、E 節）。

## 執行

```bash
pip install -r requirements.txt
streamlit run app/main.py        # 首次載入約 1 分鐘（v5.10 首次載入約 1 分鐘；引擎建圖並全簿重算）
```

## 測試

```bash
sudo apt-get install -y libreoffice-calc      # parity 基準
pip install -r requirements-dev.txt
python -m pytest tests/parity tests/app
```

CI（`.github/workflows/parity.yml`）在每次 push 與 PR 執行 parity；任一格不符即失敗，並列出前 20 個不符格。

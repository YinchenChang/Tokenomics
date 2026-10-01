# Tokenomics

AI 推論的物理推導模型：**Excel 活頁簿是唯一事實來源**（`model/YYYYMMDD_Tokenomics_vN.xlsx`），
本 repo 只**執行**與**呈現**它。規範見 [CLAUDE.md](CLAUDE.md)。

## 結構

| 路徑 | 內容 |
|---|---|
| `model/` | 現行活頁簿（唯一一份）；舊版在 `model/archive/` |
| `engine/` | 以公式引擎（pycel）直接計算 xlsx，不手抄公式 |
| `app/` | Streamlit 網站：只讀 Interface 具名範圍（＋Calib 驗證表、Block 4 頁的 `B4_` 顯示名稱） |
| `tests/parity/` | Excel（LibreOffice 重算）與 engine 的一致性測試與情境檔 |
| `tests/app/` | 網站煙霧測試 |
| `legacy/`、`tests/legacy/` | 已停用的 v4 手抄公式與舊測試（不列入 CI） |
| `docs/reports/` | 每輪報告（繁體中文） |
| `CHANGELOG.md` | 每次同步的 Excel 版本、commit、變動摘要 |

## 具名範圍與下游連結

Excel 的具名範圍分為兩類（見 Excel README 頁）：

- **`IF_` 開頭且非 `IF_Hdr`**（113 個；v5.8）：Interface 輸出，**下游模型（OpenAI、CRWV、Nebius 等）只連結這一類**。
- **`IF_Hdr*`、`DRV_*`、`CAL_*`、`TRN_*`、`TR_*`、`B4_*`、`CTL_*`**：僅供本網站顯示（表頭、推導鏈、Calib 驗證表、Tech_Registry 唯讀表）、內部用或輸入控制，下游不得連結。
  `B4_*`（38 個；v5.8 新增）是 Block 4 的顯示或內部用名稱（Cap_In 輸入、市場候選表、有效單價列等），**下游一律不得連結**，應改連 `IF_` 的 Block 4 輸出（Interface D 節）。

## 執行

```bash
pip install -r requirements.txt
streamlit run app/main.py        # 首次載入約 1 分鐘（v5.8 實測 47 秒；引擎建圖並全簿重算）
```

## 測試

```bash
sudo apt-get install -y libreoffice-calc      # parity 基準
pip install -r requirements-dev.txt
python -m pytest tests/parity tests/app
```

CI（`.github/workflows/parity.yml`）在每次 push 與 PR 執行 parity；任一格不符即失敗，並列出前 20 個不符格。

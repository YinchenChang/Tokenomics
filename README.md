# Tokenomics

AI 推論的物理推導模型：**Excel 活頁簿是唯一事實來源**（`model/YYYYMMDD_Tokenomics_vN.xlsx`），
本 repo 只**執行**與**呈現**它。規範見 [CLAUDE.md](CLAUDE.md)。

## 結構

| 路徑 | 內容 |
|---|---|
| `model/` | 現行活頁簿（唯一一份）；舊版在 `model/archive/` |
| `engine/` | 以公式引擎（pycel）直接計算 xlsx，不手抄公式 |
| `app/` | Streamlit 網站：只讀 Interface 具名範圍（＋Calib 驗證表） |
| `tests/parity/` | Excel（LibreOffice 重算）與 engine 的一致性測試與情境檔 |
| `tests/app/` | 網站煙霧測試 |
| `legacy/`、`tests/legacy/` | 已停用的 v4 手抄公式與舊測試（不列入 CI） |
| `docs/reports/` | 每輪報告（繁體中文） |
| `CHANGELOG.md` | 每次同步的 Excel 版本、commit、變動摘要 |

## 執行

```bash
pip install -r requirements.txt
streamlit run app/main.py        # 首次載入約 10–15 秒（引擎建圖並全簿重算）
```

## 測試

```bash
sudo apt-get install -y libreoffice-calc      # parity 基準
pip install -r requirements-dev.txt
python -m pytest tests/parity tests/app
```

CI（`.github/workflows/parity.yml`）在每次 push 與 PR 執行 parity；任一格不符即失敗，並列出前 20 個不符格。

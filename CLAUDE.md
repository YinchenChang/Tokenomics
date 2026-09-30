# Tokenomics — Claude Code 工作規範（2026-09-30 修訂二，取代舊版 CLAUDE.md）

## 1. 角色與事實來源

- **Excel 活頁簿是唯一事實來源**：`model/YYYYMMDD_Tokenomics_vN.xlsx`。所有計算機制與數值以 Excel 為準。
- 本 repo 的 Python 與網站只能**執行**或**呈現** Excel。不得自行新增、修改或省略任何計算機制與參數。
  - 本條取代舊版的「Build new features directly in Python (skip Excel prototyping)」。
- 需要新機制或新數據時，流程如下：
  1. 在 Project 端（Andy 與 Claude chat）修改 Excel 並升版。
  2. 依第 4 節同步到本 repo。
- 可以有更底層的資料庫（`DB_*` 工作表，或 `data/db/*.csv`），但必須由 Excel 讀入，且在 Excel 中看得到。
- Tokenomics 是本研究體系的第 0 層。下游 OpenAI、CRWV、Nebius 等模型只連結 Excel 的 `Interface` 頁。
- **為什麼以 Excel 為主**：本專案的最高優先是讓 Andy 能讀懂並掌握每一步的推導。開發效率排在其次。
  - 因此，任何能提高效率、但會讓機制離開 Excel 的做法都不採用。

## 1a. 建模精神（必須保留）

- **由下而上的物理推導**：從 token、維度、層數、參數、bytes、FLOPs，經 MFU、roofline、延遲與批次，推到每架 M tok 與每 GW 的收入和成本。
  - 推論、推理、訓練、harness 都用同一組物理量表達。
  - 新技術一律以「作用在這些物理量上的倍數」寫入 `Tech_Registry`，不另開捷徑公式。
- **實測數據的角色**：只用來校準效率係數（`Calibration` 頁），不取代 roofline 推導。
- **介面必須露出推導鏈**：網站依序顯示各中間物理量，不能只顯示最終數字。
- **層級標籤**：每一個每 token 成本、單價或營收的輸出，都必須帶上對應的模型層級與 token 類型（新鮮輸入、快取輸入、思考、可見輸出）。沒有層級的單一混合數字不得作為輸出。

## 2. 目標目錄結構

```
model/            現行 xlsx（唯一一份）；model/archive/ 放舊版
engine/           以公式引擎直接計算 xlsx，不手抄公式
app/              Streamlit 介面：讀輸入頁與 Interface 頁的具名範圍
tests/parity/     Excel 與 engine 的一致性測試與情境檔
CHANGELOG.md      每次同步：Excel 版本、commit、變動摘要
```

### engine 規則

- 以公式引擎（首選 `formulas`，備選 `pycel`）載入 xlsx 並重算。
- 選型標準：parity 測試全數通過，且單次全簿重算少於 2 秒。
- 遇到引擎不支援的 Excel 函數時：
  - 回報給 Andy，由 Project 端改寫 Excel。
  - 不得在 Python 另寫旁路計算。
- 輸入與輸出一律透過 Excel 具名範圍存取，不寫死儲存格位址。

## 3. 一致性測試（必須通過才可合併）

1. 以 LibreOffice headless 重算 xlsx，取得期望值。
2. 以 engine 計算同一組情境（`tests/parity/scenarios.yaml`：基準、低、高，另加每個世代與層級的組合）。
3. 比對範圍與容差：
   - `Interface` 頁全部儲存格，以及標為 `key` 的中間格。
   - 相對誤差不超過 1e-9；字串必須完全一致。
4. GitHub Actions 在每次 push 與 PR 執行。未通過即阻擋合併。

## 4. 同步流程（每個 Excel 新版本）

1. 新版 xlsx 放入 `model/`，舊版移到 `model/archive/`。
2. 執行 parity 測試。
3. 如果具名範圍有增減，依 Excel 更新 `app/` 的欄位映射。
4. 在 `CHANGELOG.md` 記錄 Excel 版本、commit 與變動摘要。
5. 發現 Excel 本身的錯誤（`#REF!`、`#DIV/0!`、循環參照、單位不一致）時：
   - 在 PR 描述中列出。
   - 不得在 Python 端修補。

## 5. Block 0 遷移任務（v4 → v5 過渡）

- `tokenomics.py`（單檔約 1,425 行）是 v4 的手抄公式。v5 起停用手抄路徑，改由 engine 計算。
- 刪除 `tokenomics_bk.py`。
- **逐步能量模型**（energy per step、Energy Economics）目前只存在 Python，未經 Excel 驗證。
  - 已決定在 Block 2（推論）移入 Excel，用途是能量閉合檢查與 tokens/J 指標。
  - 移入前：UI 保留並標示「未經 Excel 驗證」，不得連動任何輸出。
  - 移入後：改由 engine 計算，刪除 Python 版本。
- `test_tokenomics.py` 自行重寫公式、沒有匯入 app，因此無法偵測 app 與 Excel 的漂移。
  - 以第 3 節的 parity 測試取代。
  - 舊測試移到 `tests/legacy/`，不列入 CI。
- `data/` 內的舊 FTGP xlsx 移到 `model/archive/`。

## 6. 禁止事項

- 不得在 Python 硬編碼任何價格、規格、效率或比例參數。
- 不得刪除或改寫 Excel 的來源、標記、查核狀態欄。
- 不得把網站的計算結果回寫 Excel。
- 不得自行更新任何外部數據。數據更新一律經由 Excel。

## 7. 慣例

- **電力口徑**（Andy 於 2026-09-30 確認）：`GW` 以 IT 關鍵電力為基準。
  - 設施電力＝IT × PUE。Interface 頁同時列出兩者。
  - 外部揭露的 GW 數字逐一標註口徑：IT、設施或未明。
- **來源標記**：Verified／Interested-party／Analogy／Assumed／Derived。
  - Analogy 與 Assumed 一律以區間（低／基準／高）呈現。
- **版本命名**：`YYYYMMDD_Tokenomics_vN.xlsx`。repo 與 Project 使用同一檔名。
- **Excel 語言**：工作表名稱與具名範圍用英文（程式存取）；標籤與註解用繁體中文。

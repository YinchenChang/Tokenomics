# Tokenomics — Claude Code 工作規範（2026-10-01 修訂四，取代 repo 內現有 CLAUDE.md）

## 1. 角色與事實來源

- **Excel 活頁簿是唯一事實來源**：`model/YYYYMMDD_Tokenomics_vN.xlsx`。所有計算機制與數值以 Excel 為準。
- 本 repo 的 Python 與網站只能**執行**或**呈現** Excel。不得自行新增、修改或省略任何計算機制與參數。
  - 本條取代舊版的「Build new features directly in Python (skip Excel prototyping)」。
- **Excel 的修改分兩類**（2026-10-01 Andy 決定）：
  - **判斷類**：只能在 Project 端（Andy 與 Claude chat）修改並升版，再依第 4 節同步。範圍：任何輸入值、計算機制或公式邏輯、新參數、來源與標記、Tech_Registry 條目、DB_Evidence 判定、假設與區間。
  - **工程類**：Claude Code 可在本 repo 以 `builder/` 直接產生新版，依第 4a 節執行。範圍：具名範圍、標籤與單位文字、格式、僅供顯示的列、Checks 參照格改為儲存格引用、工作表順序、不改變任何數值的 builder 重構。
  - **分不清屬哪一類時，一律視為判斷類**：在報告中提出，不要動手。
- **Excel 優先（v5.7 起）**：輸入值（藍字格）由 Excel 擁有；`builder/` 只產生公式頁，重建時讀回所有藍字輸入。改輸入一律改 Excel，不改 builder 的預設值。
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
model/            現行 xlsx（唯一一份）；model/archive/ 放舊版；model/CURRENT 記錄現行檔名（一行）
builder/          產生 Block 2、3 公式頁的程式（Excel 的建檔程式；chat 與 CC 共用同一份）
engine/           以公式引擎直接計算 xlsx，不手抄公式
app/              Streamlit 介面：讀輸入頁與 Interface 頁的具名範圍
tests/parity/     Excel 與 engine 的一致性測試與情境檔
CHANGELOG.md      每次同步：Excel 版本、commit、變動摘要
```

### engine 規則

- 以公式引擎（首選 `formulas`，備選 `pycel`）載入 xlsx 並重算。
- 選型標準：parity 測試全數通過，且單次全簿重算少於 2 秒。
  - 效能門檻分兩條：(a) 每個 parity 情境改輸入後的增量重算少於 2 秒（硬性）；(b) 全簿強制重算少於 5 秒（暫行）。
  - 全簿 < 5 秒為暫行門檻，至 v5.12 為止；v5.12 以 SRC_Index 改寫 Gov_Map 查找後，恢復為全簿 < 2 秒。
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

1. 新版 xlsx 放入 `model/`，舊版以 `git mv` 移到 `model/archive/`（不刪除）；更新 `model/CURRENT`。
   - chat 端交付新的 `Tokenomics_builder_v5.md` 時：依檔內 `## <檔名>.py` 標題下的 python 區塊，覆寫 `builder/` 內同名檔（逐字，不改內容），並確認 `python3 builder/build.py model/archive/<前一版>.xlsx /tmp/check.xlsx` 經 LibreOffice 重算後，數值與新版逐格一致（README 版本文字除外）。不一致時在報告中列出，不要自行修正。
2. 執行 parity 測試。
3. 如果具名範圍有增減，依 Excel 更新 `app/` 的欄位映射。
4. 在 `CHANGELOG.md` 記錄 Excel 版本、commit 與變動摘要。
5. 發現 Excel 本身的錯誤（`#REF!`、`#DIV/0!`、循環參照、單位不一致）時：
   - 在 PR 描述中列出。
   - 不得在 Python 端修補。

## 4a. 工程類變更（CC 直接執行；2026-10-01 起）

1. 以 `python3 builder/build.py model/<現行>.xlsx model/<新版>.xlsx` 產生新版；版本號加 0.1，檔名依第 7 節。
2. 只改 `builder/` 程式；不得改任何藍字輸入值，也不得改公式邏輯。
3. 驗收條件（全部成立才可提交）：
   - LibreOffice 重算錯誤 0 格。
   - `restore_log.txt` 的「Excel value kept over code default」與「unmatched」皆為 0。
   - 與現行版逐格比對：全部既有儲存格數值不變；差異只能是新增的顯示格、標籤文字或具名範圍。報告逐項列出所有差異。
   - 第 3 節 parity 全過。
4. 依第 4 節完成同步（含 `model/CURRENT`、CHANGELOG），並更新 `builder/` 後重新產生 `docs/builder/Tokenomics_builder_v5.md`（標題與各檔區塊格式不變），讓 chat 端可直接讀取。
5. 報告標題標明「工程類（CC 執行）」；合併前請 Andy 確認。

## 5. Block 0 遷移任務（v4 → v5 過渡；已完成，保留紀錄）

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

## 5a. 每輪報告（必須）

Andy 不熟悉程式，所以每一輪工作結束都要交報告：

- **寫入 repo**：`docs/reports/YYYYMMDD_<主題>.md`，用繁體中文、非工程語言撰寫，內容包括：
  - 本輪做了什麼、為什麼這樣做。
  - parity 測試結果（通過／未通過的格數與情境數）。
  - 發現的 Excel 問題（只列出，不在 Python 端修補）。
  - 下一步與需要 Andy 決定的事項。
- **同一份內容也貼成 PR comment**，讓 Andy 可以從 GitHub 通知信讀取。
- 報告開頭列出：分支名稱、最新提交 SHA、報告檔路徑，讓 chat 端可直接以 `https://raw.githubusercontent.com/YinchenChang/Tokenomics/<SHA>/<路徑>` 讀取原檔。
- 合併前請 Andy 確認。

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
- **版本命名**：`YYYYMMDD_Tokenomics_vN.xlsx`。repo 與 Project 使用同一檔名。repo 的 master 為 Excel 與 builder 的存放處；Project 只需交接文件（chat 端直接從 repo 下載最新版）。
- **具名公式（Block 4 起）**：新公式的關鍵物理量以具名範圍引用，使公式讀起來像 `=每token訓練FLOPs/(峰值×MFU)`（名稱仍用英文，例如 `=TrainFLOPsPerTok/(PeakPF*MFU)`）；Block 1–3 的既有公式不追溯改寫。engine 與 parity 須支援公式內的具名範圍；不支援時回報。
- **Excel 語言**：工作表名稱與具名範圍用英文（程式存取）；標籤與註解用繁體中文。

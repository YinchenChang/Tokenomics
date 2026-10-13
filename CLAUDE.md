# Tokenomics — Claude Code 工作規範（2026-10-13 修訂六，取代 repo 內現有 CLAUDE.md）

> 修訂六（2026-10-13，Andy 決定）：本機數值檢查取代「等 GitHub CI」作為提交與合併門檻；重算秒數降為警告；加入兩輪停損；數值檢查通過後由 CC 自行合併，不再等 Andy 確認。理由：本模型用於研究，更新頻繁，等待 CI 一輪約 20 分鐘且修正循環沒有停損，v5.33 建置因此耗時 7 小時。數值檢查本身不放寬——Tokenomics 是第 0 層，下游公司模型全部讀它的 IF_ 數值。

## 1. 角色與事實來源

- **Excel 活頁簿是唯一事實來源**：`model/YYYYMMDD_Tokenomics_vN.xlsx`。所有計算機制與數值以 Excel 為準。
- 本 repo 的 Python 與網站只能**執行**或**呈現** Excel。不得自行新增、修改或省略任何計算機制與參數。
  - 本條取代舊版的「Build new features directly in Python (skip Excel prototyping)」。
- **Excel 的修改分兩類**（2026-10-01 Andy 決定；2026-10-04 修訂五：分工改為「Project 判斷、CC 執行、chat 審查」）：
  - **判斷類**：「決定權」只在 Project 端（Andy 與 Claude chat）。範圍：任何輸入值、計算機制或公式邏輯、新參數、來源與標記、Tech_Registry 條目、DB_Evidence 判定、假設與區間。
    - 「執行」由 CC 依工作單進行：工作單放在 `docs/workorders/YYYYMMDD_vN.md`，寫明要改什麼、確切數值與來源、公式邏輯、驗收標準。CC 依工作單改 `builder/` 並產生新版 Excel（第 4 節）。
    - 工作單沒寫到、或寫得不清楚的地方：CC 不自行決定，列在報告「待 Project 判斷」一節；能先做的部分照做，不能做的部分保留現狀。
  - **工程類**：Claude Code 直接執行，依第 4a 節。範圍：具名範圍、標籤與單位文字、格式、僅供顯示的列、Checks 參照格改為儲存格引用、工作表順序、不改變任何數值的 builder 重構。
  - **分不清屬哪一類時，一律視為判斷類**：沒有工作單就不動手，在報告中提出。
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
  - 效能門檻分兩條：(a) 每個 parity 情境改輸入後的增量重算少於 2 秒；(b) 全簿強制重算少於 2 秒。
  - **兩條門檻自修訂六起皆為警告，不是失敗**：超過時測試以 warning 記錄秒數並寫進報告，不阻擋提交或合併。秒數受執行機器影響（CI runner 曾量到 2.02–2.08 秒），不是數值正確性問題。只有在單一機器上連續三版都超過 3 秒，才列入「待 Project 判斷」討論引擎選型。
- 遇到引擎不支援的 Excel 函數時：
  - 回報給 Andy，由 Project 端改寫 Excel。
  - 不得在 Python 另寫旁路計算。
- 輸入與輸出一律透過 Excel 具名範圍存取，不寫死儲存格位址。

## 3. 一致性測試（數值檢查必須通過才可合併）

1. 以 LibreOffice headless 重算 xlsx，取得期望值。
2. 以 engine 計算同一組情境（`tests/parity/scenarios.yaml`：基準、低、高，另加每個世代與層級的組合）。
3. 比對範圍與容差：
   - `Interface` 頁全部儲存格，以及標為 `key` 的中間格。
   - 相對誤差不超過 1e-9；字串必須完全一致。
4. **檢查在本機執行，結果寫進報告；GitHub Actions 不阻擋**（修訂六）：
   - CC 在開 PR 前於本機跑完 `tests/parity` 全套（數值檢查：逐格一致、具名範圍期望值、情境無錯誤值、GOV_Errors 0），把通過／失敗項數與重算秒數寫進報告第 5a 節。本機全過即可開 PR 與合併。
   - GitHub Actions 照常在 push 與 PR 執行，供事後對照；CC **不等待、不輪詢**其結果。CI 與本機不一致時，列在下一版報告「待 Project 判斷」。
   - 重算秒數（第 2 節 engine 規則兩條門檻）只警告，不算失敗。
   - **停損**：同一個失敗項修正兩輪仍未通過，或失敗屬於環境因素（秒數、runner 差異、權限、網路），CC 停止修正，把現狀與未完成項寫進報告交 chat 端判斷；不得反覆推送重試。
   - 預期中的數值變動（工作單「預期變動」已列明者）造成的測試期望值不符，CC 直接更新測試期望值並在報告表 1 註明，不算失敗。

## 4. 建置與同步流程（每個 Excel 新版本）

1. 新版 Excel 一律由 CC 以 `python3 builder/build.py model/<現行>.xlsx model/<新版>.xlsx` 產生（經 LibreOffice 重算存檔後放入 `model/`）；版本號依交接文件第 11 節：只新增 Evidence 為修補版，SRC Active 值或公式改變為次版，契約改變為主版。
   - 舊版以 `git mv` 移到 `model/archive/`（不刪除）；更新 `model/CURRENT`。
   - CC 同時重新產生 `docs/builder/Tokenomics_builder_v5.md`（`tools/gen_builder_md.py`；標題與各檔 `## <檔名>.py` 區塊格式不變）。chat 端不再交付 Excel 或 builder md。
   - 工作單要求改動的輸入值：直接寫入 Excel 的藍字格，沿用「只在仍為舊值時才寫」的機制（`gov.gm_update` 同類寫法），不改 builder 的預設值。
2. **驗收（全部成立才可提交）**：
   - LibreOffice 重算錯誤 0 格；本機跑 parity 全套（第 3 節第 4 條）；合併門檻為本機數值檢查全部通過。增量與全簿重算秒數記錄於報告，超過 2 秒只警告。
   - `restore_log` unmatched 0；「Excel value kept over code default」只能出現工作單列明的格。
   - 冪等：以新版為底稿重建，兩邊都經 LibreOffice 重算存檔後比較，數值與公式文字不符 0（builder 直接輸出的科學記號寫法與 LibreOffice 存檔不同，不作為不一致）。
   - 與現行版逐格比較：差異必須全部落在工作單的「預期變動」範圍內。
3. 如果具名範圍有增減，依 Excel 更新 `app/` 的欄位映射。
4. 在 `CHANGELOG.md` 記錄 Excel 版本、commit 與變動摘要。
4a-bis. **合併（修訂六）**：第 2 項驗收全部成立、報告已寫入 repo 並貼成 PR comment 後，CC 以 `gh api -X PUT repos/YinchenChang/Tokenomics/pulls/<n>/merge -f merge_method=merge -f sha=<最新 SHA>` 自行合併到 master，不等 Andy 確認。合併被權限或衝突擋下時，不繞過，在最終回覆與報告寫明「待合併」與原因。Andy 事後有異議可 revert；判斷類內容仍以工作單為界，工作單沒寫的不因可自行合併而放寬。
5. 發現 Excel 本身的錯誤（`#REF!`、`#DIV/0!`、循環參照、單位不一致）時：
   - 在 PR 描述與報告中列出；不得在 Python 端旁路修補。
   - 例外：屬工作單範圍內可直接修正的 Excel 公式缺陷，可在同一版修正，並在報告表 1 列出。其他錯誤列在報告，交 Project 判斷。

## 4a. 工程類變更（CC 直接執行；2026-10-01 起）

1. 以 `python3 builder/build.py model/<現行>.xlsx model/<新版>.xlsx` 產生新版；版本號加 0.1，檔名依第 7 節。
2. 只改 `builder/` 程式；不得改任何藍字輸入值，也不得改公式邏輯。
3. 驗收條件（全部成立才可提交）：
   - LibreOffice 重算錯誤 0 格。
   - `restore_log.txt` 的「Excel value kept over code default」與「unmatched」皆為 0。
   - 與現行版逐格比對：全部既有儲存格數值不變；差異只能是新增的顯示格、標籤文字或具名範圍。報告逐項列出所有差異。
   - 第 3 節 parity 全過。
4. 依第 4 節完成同步（含 `model/CURRENT`、CHANGELOG），並更新 `builder/` 後重新產生 `docs/builder/Tokenomics_builder_v5.md`（標題與各檔區塊格式不變），讓 chat 端可直接讀取。
5. 報告標題標明「工程類（CC 執行）」；驗收成立後依第 4 節 4a-bis 自行合併。

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
- 數值檢查通過即自行合併（第 4 節 4a-bis）；報告寫明合併 SHA。
- **必填一節「預期變動 vs 實際變動」**（修訂五）：
  - 表 1：工作單每一項 → 是否完成、實際位置（頁、列或名稱）、數值摘要。
  - 表 2：逐格比較中，不在工作單範圍內的所有差異（應為 0；若非 0 逐項說明）。
  - 另列：重算秒數（本機為準；CI 若已完成可附）、parity 通過／失敗項數與情境數、GOV 三項計數。
- 必填「待 Project 判斷」一節：工作單沒寫到或寫得不清楚而 CC 未自行決定的事項。

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

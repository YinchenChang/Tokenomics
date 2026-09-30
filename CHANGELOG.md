# CHANGELOG

每次同步 Excel 新版本記錄：Excel 版本、commit、變動摘要。

## 20260930_Tokenomics_v5.2.xlsx（取代 v5.0）

- Commit：見 PR「同步 Tokenomics v5.2」（合併後補上 commit 雜湊）
- Excel：8,427 個公式、40 個具名範圍（Block 2 新增 28 個）。
- 引擎：pycel 1.0b30（`engine/`）；以外掛補齊 `TEXT` 的十進位進位語意。
- 測試：`tests/parity/`（全部公式格、具名範圍、基準＋5 情境、函數語意）；`tests/app/`。
- CI：`.github/workflows/parity.yml`。
- 網站：`app/`（總覽、Block 2、Calib 驗證表）。
- 停用：`legacy/tokenomics_v4.py`（v4 手抄公式）、`tests/legacy/`；刪除 `tokenomics_bk.py`。
- 搬移：v5.0 與 `data/` 內舊 FTGP xlsx → `model/archive/`。

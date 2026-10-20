# 推導檢核活頁簿的產生程式

這裡的程式產生 `docs/plan/` 的 m 推導檢核與 L 推導檢核活頁簿。它們只讀 Tokenomics，不改模型。

## 怎麼重建

1. 把現行模型複製到本資料夾，存成 `v170.xlsx`。換版時改各檔的 `SRC`。
2. 執行 `python3 build_m17.py`，它會呼叫 `build_m2_17.py`，輸出 `m推導檢核_v17.0.xlsx`。
3. 執行 `python3 build_L17.py`，輸出 `L推導檢核_v17.0.xlsx`。
4. 用 `parity_lib.lo_recalc` 以 LibreOffice 重算，再放進 `docs/plan/`（檔名前面加日期）。

## 檢查

- m 檔 3_m重算的「差異」欄應全為 0。
- L 檔 11_世代起點第 33 列應等於 Cap_In 第 325 列。

## 其他檔案

- `trace.py`：從 L1_MFleet（Cap_In!C119）遞迴列出全部前置格。
- `sens.py`、`sens.json`：m 的 27 個輸入的單變數敏感度。這是 v15.3 跑的；m 的前置格之後沒有變，所以結果仍適用。
- `parity_lib.py`：從 `tests/parity` 複製來的 LibreOffice 重算函式。

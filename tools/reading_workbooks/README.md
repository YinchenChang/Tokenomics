# m／L 閱讀版的維護工具

`docs/plan/` 的 **m 閱讀版**與 **L 閱讀版**是給 Andy 讀懂 m 與 L 推導用的 Excel。它們只讀 Tokenomics，不改模型。

## 規格（Andy 2026-10-20）

- 兩份的最高目標是**提升 Andy 的認知**，所以只做閱讀版，不做稽核版。
- 兩份都**必須有需求公式樹**：m 閱讀版的 `1A_需求公式樹`、L 閱讀版的 `1_公式樹`。換版時不得拿掉。
- 閱讀版裡每個取自 Tokenomics 的數字（輸入、原值欄、公式結果），都必須與現行 Tokenomics 一致。

## 換版步驟

1. 以上一版閱讀版為底稿（不要從頭重建；過去曾因從舊程式重建而漏掉公式樹）。
2. 用 `check_reading.py` 對新版 Tokenomics 核對：
   ```
   python3 check_reading.py <新版 Tokenomics.xlsx> <m閱讀版.xlsx> <L閱讀版.xlsx>
   ```
   兩份閱讀版要先用 LibreOffice 重算。全部通過時結束碼為 0。
3. 有不一致時，依核對結果更新閱讀版的輸入與原值欄；m 的前置格若有變動，m 的鏈要重新核對，必要時重跑敏感度（`sens.py`）。
4. 改版本標籤與修訂紀錄（0_說明），LibreOffice 重算後放進 `docs/plan/`，檔名 `YYYYMMDD_m閱讀版_vN.xlsx`、`YYYYMMDD_L閱讀版_vN.xlsx`；Drive 放 `02-算力收支/Tokenomics/閱讀版/`。
5. 合併前請未參與製作的代理獨立核對一次數字。

## 檢查內容（check_reading.py）

- 規格：兩份都有需求公式樹頁。
- m 的 2,993 個前置格（`m_precursors_v17.0.csv`，自 L1_MFleet 遞迴展開）在新版是否相同。
- m 閱讀版 2_輸入 的每個輸入、3_m重算 的原值對 Tokenomics；m 對 `L1_MFleet`。
- L 閱讀版 3_L逐世代 的情境摘要（原值與本簿重算）對具名範圍；所需 L 對 `L1_LReqFleet_IdNoK`。
- 兩份所有「差異」欄 ≤ 10⁻⁹，沒有錯誤值。

## 其他檔案

- `trace.py`：從 L1_MFleet（Cap_In!C119）遞迴列出全部前置格（產生前置格清單用）。
- `sens.py`、`sens.json`：m 的 27 個輸入的單變數敏感度（在 v15.3 執行；m 的前置格到 v17.0 都沒有變，所以結果仍適用）。
- `parity_lib.py`：從 `tests/parity` 複製來的 LibreOffice 重算函式。

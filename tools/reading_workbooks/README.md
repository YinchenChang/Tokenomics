# L 閱讀版的維護工具

> **m 閱讀版恢復（v21.2 重做，2026-10-24）：** 依 Andy 2026-10-21 新定義（m＝實收單價 ÷ 有效牌價，只有收入面）重做（v21.2）；現行 `docs/plan/20261025_m閱讀版_v21.4.xlsx`（v21.4 重產；說明句現行值改公式）（含必備的 `1A_需求公式樹`）。舊 m（成本鏈 `L1_MFleet`）現為 token 帳診斷，不是 m。v17.0 舊檔已刪除（歷史在 git）。
> 建檔：`python3 build_reading_m.py <Tokenomics.xlsx> <輸出.xlsx>`（再用 LibreOffice 重算存檔）；核對：`python3 check_reading_m.py <Tokenomics.xlsx> <m閱讀版.xlsx>`（先自動重算；檢查有 1A、9_核對對照 每格等於 Tokenomics、L1_M* 名稱一致、說明句數字檢查（v21.4 起）、無錯誤值；通過結束碼 0）。換版時重跑建檔程式即可，不必手改。
> 先前的 v18.0 說明：m 閱讀版 10-21 退役；`check_reading.py` 仍只核對 L 閱讀版。

`docs/plan/` 的 **L 閱讀版**是給 Andy 讀懂 L 推導用的 Excel。它只讀 Tokenomics，不改模型。

## 規格（Andy 2026-10-20）

- 閱讀版的最高目標是**提升 Andy 的認知**，所以只做閱讀版，不做稽核版。
- **必須有需求公式樹**：L 閱讀版的 `1_公式樹`（m 閱讀版重做時同樣要有）。換版時不得拿掉。
- 閱讀版裡每個取自 Tokenomics 的數字（輸入、原值欄、公式結果），都必須與現行 Tokenomics 一致。

## 換版步驟

1. 以上一版閱讀版為底稿（不要從頭重建；過去曾因從舊程式重建而漏掉公式樹）。
2. 用 `check_reading.py` 對新版 Tokenomics 核對：
   ```
   python3 check_reading.py <新版 Tokenomics.xlsx> <L閱讀版.xlsx>
   ```
   L 閱讀版要先用 LibreOffice 重算。全部通過時結束碼為 0。（現行：`20261024_Tokenomics_v21.4.xlsx` 對 `20261025_L閱讀版_v21.4.xlsx`：通過；v21.4 只改說明句的呈現方式（現行值數字改公式），數值不變。注意：先前認為「v18.0 起 L 側免換版」不成立——v19.1 改了 ρ 低端與每 GW 營收、v21.2 改了計價倍數，L 閱讀版已於 v21.2 換版。）
3. 有不一致時，依核對結果更新閱讀版的輸入與原值欄。
4. 改版本標籤與修訂紀錄（0_說明），LibreOffice 重算後放進 `docs/plan/`，檔名 `YYYYMMDD_L閱讀版_vN.xlsx`；Drive 放 `02-算力收支/Tokenomics/閱讀版/`。
5. 合併前請未參與製作的代理獨立核對一次數字。
6. 每次 Tokenomics 新版合併後都先跑一次 `check_reading.py`（不要假設免換版）；任一項不符就依上面步驟換版。

## 檢查內容（check_reading.py）

- 規格：L 閱讀版有需求公式樹頁。
- L 閱讀版 3_L逐世代 的情境摘要（原值與本簿重算）對具名範圍。
- 所需 L（v21.2 起主口徑）：1_公式樹 C8／C19／C20／C21 對 `L1_LReqFleet_Full`（＋`_Lo`／`_Hi`），C11／C17 與 2_輸入 IN_Hold 對 `L1_HoldFleet25`，區間文字與三態判讀（C14）對 Cap_In C242；舊口徑對照 C79／C80 對 `L1_LReqFleet_IdNoK`（＋區間）。
- 所有「差異」欄 ≤ 10⁻⁹，沒有錯誤值。
- 說明句數字檢查（v21.4 起）：盤點表列為現行值的格必須是公式且算出文字；含顯著數字而未登錄的文字格失敗；2_輸入 第 35 列 IN_GW 對 Cap_In 第 331 列（格數 78）。
- （v18.0 起不再檢查 m 閱讀版：m 的前置格比對、2_輸入、3_m重算 已移除。）

## 說明句數字（v21.4 起）

說明句（文字格）裡取自 Tokenomics 或本簿計算結果的「現行值」數字，一律用公式帶出，例如 `="每則 token "&TEXT(IN_Tau,"#,##0")&"…"`，不寫死。歷史敘述（修訂紀錄、各版舊值）、外部來源的事實、預設值說明不改，登錄為保留。

- 盤點表：`text_inventory_L.csv`、`text_inventory_m.csv`（頁、格、類別、原文、來源、處理方式）。類別：現行值（必須是公式）／已是公式／歷史保留／外部事實保留／原值貼上／預設值保留／待Project判斷（保留）。
- 新增或改寫說明句時：含數字的文字格一定要登錄在盤點表。現行值做成公式（用 `formula_text.py` 的 `apply_text`），再重跑 `make_text_inventory.py` 產生盤點表。
- m 閱讀版：公式化清單在 `build_reading_m_text.py`（由建檔程式在 9_核對對照 之前執行）。L 閱讀版：`update_reading_L_text.py`（以上一版為底稿，openpyxl 改公式；LibreOffice 重算存檔）。
- 要換版時：L 以上一版為底稿；說明句的公式不必重做，只需檢查新增句子與版本標籤。本表的規則由兩支核對程式的「說明句數字檢查」強制。
- 掃描規則（`text_scan.py`）：小數、千分位、百分比、≥13 的整數視為顯著數字；≤12 的整數（如 T1＝4）不由掃描抓，但盤點表列為現行值的格一定檢查。

## 其他檔案

- `formula_text.py`：說明句公式化工具（原句不動，只把數字段換成 TEXT(…)；字串常數自動切成每段 ≤240 字元以符合 Excel 限制）。
- `text_scan.py`、`text_check.py`、`make_text_inventory.py`：說明句數字檢查與盤點表產生。

- `build_reading_m.py`（＋`build_reading_m_part2.py`）：m 閱讀版建檔程式；`check_reading_m.py`：m 閱讀版核對。
- `trace.py`：（舊 m 閱讀版用）從 L1_MFleet（Cap_In!C119）遞迴列出全部前置格（產生前置格清單用）。
- `sens.py`、`sens.json`：（舊 m 閱讀版用）m 的 27 個輸入的單變數敏感度（在 v15.3 執行；m 的前置格到 v17.0 都沒有變，所以結果仍適用）。
- `parity_lib.py`：從 `tests/parity` 複製來的 LibreOffice 重算函式。

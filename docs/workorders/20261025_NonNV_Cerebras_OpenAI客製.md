# 工作單：NonNV D 段——Cerebras WSE-3、OpenAI／Broadcom 客製晶片（唯讀查證，可行性優先）

日期 2026-10-25　分支 `claude/evidence-nonnv-cs-oai`　基準 master `0c8c1b7`（CURRENT v21.7）
承接：NonNV A–C 段（`docs/evidence/20261023_NonNV昇騰Maia_A段/`、`20261025_NonNV_TPU_Trainium/`、`20261025_NonNV_AMD/`）。TK 現值 Cerebras 0.2／0.4／0.8、1.0（0.8／1.0／1.2）；OpenAI 客製 0.4／0.6／0.9、0.8（0.7／0.8／1.0），皆慣例值。不改 `model/`、`builder/`、`tests/`。模式：LIGHT。

## 要回答的問題
1. **Cerebras WSE-3／CS-3：** 每系統功率、峰值算力（各精度、dense）、SRAM／記憶體架構；推論吞吐的公開實測（第三方優先）；系統售價（公司、IPO 文件、賣方）。用 A–C 段同一套方法推產出比、持有比（低／基準／高）；注意 Cerebras 架構與 GPU 不同（晶圓級、SRAM），f 的類比要寫明限制；若方法不適用，寫明原因並給方向界線，不硬推。
2. **OpenAI／Broadcom 客製（Titan 等）：** 公開的晶片規格、功率、量產時程、合約規模（10 GW 等）、單價或每 GW 金額。資料不足以推導就照實寫「已搜尋，未找到」與可得的界線，**本段允許結論為「維持慣例值」**。
3. 兩列各給「是否寫進 TK 下一版」的預設。

## 規則
- 同 C 段：WebSearch／WebFetch；付費牆不登入；不得在任何對外請求使用使用者 email；SemiAnalysis 只作佐證；本人說與記者推論分清；外部價格須與 TK VR200 買方取得價（Spec_Rack F12 $8.4M）同口徑，不明時用同源比值；精度口徑兩種都算（若適用）。

## 交付
- `docs/evidence/20261025_NonNV_Cerebras_OpenAI/`：README（結論先行；待 Project 判斷附預設）、審閱檔 xlsx（若有推導；公式、LibreOffice 錯誤 0）、`證據原稿.md`。
- 未參與代理獨立核對後，依索引 0b 驗收全過即合併。

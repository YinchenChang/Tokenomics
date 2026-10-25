# 工作單：NonNV C 段——AMD MI455X（Helios）每 kW 重推（唯讀查證）

日期 2026-10-25　分支 `claude/evidence-nonnv-amd`　基準 master `e06a3c0`（CURRENT v21.6）
承接：NonNV B 段（PR #172，`docs/evidence/20261025_NonNV_TPU_Trainium/`）Q8 預設「AMD MI455X 另發工作單」；A 段（`docs/evidence/20261023_NonNV昇騰Maia_A段/`）。TK 現值 AMD 產出比 0.5／0.7／1.0、持有比 0.8／0.9／1.0（慣例值、未推導）。不改 `model/`、`builder/`、`tests/`。模式：LIGHT。

## 要回答的問題
1. **功率與規格：** AMD Instinct MI455X（與 MI450 系列）單顆 TDP、各精度峰值（FP4／FP8 dense，是否有 FP4 與倍率）、HBM；Helios 機架每架顆數與機架功率（原文口徑：IT、含冷卻與否）。
2. **每 kW 產出比：** 用 B 段同一套方法（每 kW 峰值算力 ÷ VR200 每 kW 峰值算力 × 效率 f）推產出比低／基準／高。**兩種精度口徑都算**：(a) 各晶片最高原生精度（若 MI455X 有 FP4，與 VR200 NVFP4 同口徑）；(b) FP8 對齊。f 的依據：MLPerf（AMD 有提交時優先）、第三方實測、公司自述（Interested-party）；SemiAnalysis／InferenceX 只作佐證，不得單獨支撐 f。
3. **每 kW 持有比：** 用 B 段的「每 kW 設備價推導」：MI455X 每顆或 Helios 每架價格（公司、賣方、媒體；標來源與誘因）；找不到寫「已搜尋，未找到」並給方向界線。
4. 與 TK 現值、B 段 TPU／Trn、A 段 Maia／昇騰並排。

## 取得方法、口徑規則
- 同 B 段工作單（WebSearch／WebFetch；付費牆不登入；不得在任何對外請求使用使用者 email）。VR200 基準讀 TK v21.6。
- 「已搜尋，未找到」與「不存在／不可分離」分開列；引述分清「本人說」與「記者推論」；方向檢查與覆蓋檢查照 B 段格式。

## 交付
- `docs/evidence/20261025_NonNV_AMD/`：README（結論先行；Facts & Data、Judgment；待 Project 判斷附預設）、審閱檔 `NonNV_AMD.xlsx`（換算全用公式，LibreOffice 重算錯誤 0）、`證據原稿.md`。
- 未參與代理獨立核對後，依索引 0b 驗收全過即合併。

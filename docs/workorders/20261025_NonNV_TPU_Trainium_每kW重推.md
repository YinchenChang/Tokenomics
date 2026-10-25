# 工作單：NonNV B 段——TPU v7、Trainium3 的機架功率與「每 kW」重推（唯讀查證）

日期 2026-10-25　分支 `claude/evidence-nonnv-tpu-trn`　基準 master `6aca7a3`（CURRENT v21.5）
承接：NonNV 昇騰／Maia A 段（`docs/evidence/20261023_NonNV昇騰Maia_A段/`）待判斷 2：持有比改「依每 kW 設備價推導」；既有五列（AMD、TPU、Trn、CS、OAI）目前是「慣例值、未推導」；限制寫明「TPU v7／Trainium3 機架功率沒找到（E20），無法用同一套每 kW 方法重現」。交接檔第 4 節 F。不改 `model/`、`builder/`、`tests/`。模式：LIGHT。

## 要回答的問題
1. **機架（或 pod）功率：** Google TPU v7（Ironwood）與 AWS Trainium3（Trn3 UltraServer）的每架／每 pod 功率、每顆晶片 TDP、每架晶片數。逐項給原文與口徑（晶片 TDP、伺服器、機架 IT、含冷卻與否）。
2. **每 kW 產出比：** 用 A 段對 Maia 的同一套方法（每 kW 峰值算力 ÷ VR200 每 kW 峰值算力 × 效率係數 f），重推 TPU v7、Trainium3 的產出比（低／基準／高），與 TK 現值（TPU 0.8、Trn 0.5）並列；寫明 f 的依據（MLPerf、公司自述、第三方實測；自述標 Interested-party）。
3. **每 kW 持有比：** 若找得到設備價（每架、每顆或每 GW 資本支出；含 Google、AWS 自述或賣方估計），用 A 段的「每 kW 設備價推導」重推持有比，與 TK 現值（TPU 0.8、Trn 0.7）並列；找不到就寫「已搜尋，未找到」並給方向界線。
4. （若時間允許）AMD MI455X／Helios 機架同法對照（TK 現值 0.7／0.9）。

## 取得方法（工程類，chat 端決定）
- WebSearch／WebFetch：Google Cloud 官方部落格與文件（Ironwood）、AWS re:Invent 與官方頁（Trainium3、Trn3 UltraServer）、Hot Chips、MLPerf 結果頁、公司法說；第三方（SemiAnalysis 只作佐證；付費牆不登入）。VR200 每 kW 基準讀 TK v21.5（`model/20261025_Tokenomics_v21.5.xlsx` Spec_Rack／NonNV 頁）。
- 不得在任何對外請求使用使用者 email。

## 口徑規則
- 「已搜尋，未找到」與「不存在／不可分離」分開列；精度與稀疏度（FP8 dense／FP4／sparse）一律對齊後才比較，對不齊的列出不比。
- 標記依 Analysis Protocol；Google、AWS 自述標 Interested-party 並寫誘因；Analogy／Assumed 給區間。
- 方向檢查（第 10 條）與覆蓋檢查（第 11 條）照 B 段格式。

## 交付
- `docs/evidence/20261025_NonNV_TPU_Trainium/`：README（結論先行；Facts & Data、Judgment；待 Project 判斷附預設，含「是否寫進 TK 下一版」）、審閱檔 `NonNV_TPU_Trainium.xlsx`（換算全用公式，LibreOffice 重算錯誤 0；與 A 段 Maia 並排）、`證據原稿.md`。
- 未參與代理獨立核對（實際打開來源、重現數字）後，依索引 0b 驗收全過即合併。

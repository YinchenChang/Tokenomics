# 工作單草稿｜併入 v5.29：token 對帳落差分解列與需求輸入區間（草稿，判斷類待 chat 端定案）

- 依據：`docs/evidence/20261008/summary.md`、`candidates.csv`（E256–E262）。
- 判斷類（待 Andy）：(1) E261 Alloc_In「每則提示 token 數」2,000 → 4,000（區間 2,000–6,400）；(2) E259 SRC_DEM_004 是否改為 2025 全年推估（區間 12.3–13 $B）並以 E259 為 Evidence；(3) E262 是否新增分解列。
- 工程類（定案後併入 v5.29 第 3 節）：L1 新增四列 `L1_GapPrompt`（＝新每則 token ÷ 舊值）、`L1_GapSpendBasis`（Assumed 區間 1.5–3，Gov_Map 登錄）、`L1_GapISL`（＝IF_TokGW_Sol(ISL 16K) ÷ Sens_Perf ISL 4K 欄）、`L1_GapUtil`（＝0.6 ÷ 實際利用率輸入，Assumed 區間 0.3–0.4）；`L1_GapProduct`＝四者乘積，外部對照＝1 ÷ L1_ExtServeGW 比值（目前 14）。
- DB_Evidence：E256–E262 依 CSV 登錄；E256–E258 判定「並列」、E260「不採納（維持）」、E259／E261／E262「待 Andy」。
- 契約：`docs/plan/Tokenomics_downstream_contract.md` 第 2 條第 5 項改寫為四項口徑差的逐項換算。

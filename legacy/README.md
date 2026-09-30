# legacy/ — 已停用（v4 手抄公式路徑）

`tokenomics_v4.py` 是 v4 的手抄公式（Config → WP_Param → TL_Param → DC_Cost_Model → Revenue_Model）。
v5 起依 CLAUDE.md 第 1、5 節停用：不再由 CI 執行、不再被任何頁面匯入，僅供對照。
相關測試已移至 `tests/legacy/`（不列入 CI）。

停用範圍：v4 的 Config／TL_Param／WP_Param／Revenue_Model 已由 v5.2 的
Arch、Serving、Workload、Calib、Perf、Sens_Perf、Unit_Cost 取代。
其中「逐步能量模型（Energy Economics）」只存在於此檔、未經 Excel 驗證。Andy 已決定（第 2 輪）不恢復，
由 Excel Perf J 節（能量閉合、tokens／焦耳）取代；本檔僅供對照。

# 證據引述回查（API 版，2026-10-27 起）

逐筆檢查 `docs/evidence/` 證據檔中「數字或引述＋來源網址」是否與原文一致，輸出問題清單 Excel。**只產出核對結果，不改證據檔或模型**；`不符`、`口徑不同` 須人工對原文確認後，才依工作單修正。

## 怎麼跑
在分支 `claude/evidence-audit` 的 `tools/evidence_audit/requests/` 放請求檔並 push（工作流程 `evidence-audit` 自動執行，結果 commit 回同一分支）：
```json
{"scope": ["docs/evidence/20261025_NonNV_AMD"], "max_urls": 80}
```
輸出：`tools/evidence_audit/out/<請求名>.xlsx`（「核對結果」頁依嚴重度排序：不符 → 口徑不同 → 部分相符 → 原文找不到 → 需人工 → 相符）與 `.md` 摘要。

## 流程
1. 抽取（Batch，Sonnet）：每份 .md 抽出附來源網址的數字或引述。
2. 抓原文：從 GitHub 雲端直接抓（識別用 User-Agent，不帶任何 email）。**網站拒絕、需登入或付費牆一律標「需人工」，不重試、不改用其他管道繞過**（算力收支 2026-10-27 規則）。
3. 核對（Batch，Sonnet）：每個網址一則請求，逐筆判定相符／部分相符／不符／原文找不到／口徑不同（含「記者推論寫成本人說」）。
4. 費用：試點三個資料夾估計 US$1–3；全部 42 個資料夾估計 US$15–30（Max 方案每月 API credit）。

# ci-status

此分支由 `.github/workflows/parity.yml` 的 `ci-status` job 自動寫入（`tools/ci_status.py`），只放每次 CI run 的結果摘要，供 chat 端以
`git fetch origin ci-status` 讀取（chat 端沒有 GitHub 登入，未登入 API 次數不足）。請勿手動編輯；本分支不含模型或程式。

檔案：`<提交 SHA>/<run 編號>-a<重跑次數>-<事件>.json`（pull_request 事件的 SHA 為 PR 分支頭）。每次 run、每次重跑各一檔，不覆寫。

欄位：`schema_version`、`repo`、`sha`、`github_sha`（Actions 的 GITHUB_SHA；PR 為合併提交）、`ref`、`event`、`pr_number`（pull_request 才有）、
`run_id`、`run_number`、`run_attempt`、`overall`（job `parity` 的結果）、`jobs`（名稱、結論、起訖時間、秒數）、`failures`（失敗或錯誤的測試與訊息前 20 列）、
`log_excerpts`（只含失敗 job：含 FAILED／Error／Traceback／python 版本字樣的列及最後 80 列，每 job 上限 200 列）、
`recalc_seconds`（全簿與增量重算秒數）、`generated_at`、`errors`（蒐集時取不到的項目）。

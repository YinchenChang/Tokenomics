#!/usr/bin/env python3
"""CI 結果寫回 repo（工作單 v5.22 第 5 節第 6 項；只用標準庫）。

為什麼：chat 端沒有 GitHub 登入，未登入 API 每 IP 每小時 60 次且沙盒對外 IP 多人共用；網頁讀得到 job 成敗、讀不到 log。
改由 CI 把每次 run 的結果寫進孤立分支 `ci-status`，chat 端以 `git fetch origin ci-status` 讀取。

用法（parity.yml 的 ci-status job）：
  python3 tools/ci_status.py --out status-out [--push]
環境：GITHUB_TOKEN（Actions 內有認證額度）、GITHUB_REPOSITORY、GITHUB_RUN_ID、GITHUB_RUN_NUMBER、GITHUB_RUN_ATTEMPT、GITHUB_SHA、
GITHUB_REF、GITHUB_EVENT_NAME、GITHUB_EVENT_PATH、OVERALL（needs.parity.result）。

輸出 JSON：schema_version、repo、sha、ref、event、pr_number（pull_request 才有）、run_id、run_number、run_attempt、overall、jobs、failures、
log_excerpts、recalc_seconds、generated_at（另有 github_sha、errors 兩個輔助欄位）。
檔名：<sha>/<run_number>-a<run_attempt>-<event>.json（每次 run、每次重跑各一檔，不覆寫）；pull_request 的 sha 取 PR 分支頭（GITHUB_SHA 是合併提交）。
不輸出環境變數或任何 secret；GitHub 已遮蔽的內容（***）照原樣保留遮蔽。本程式不影響任何數值，也不改 model/。
"""
import argparse
import datetime
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SCHEMA_VERSION = 1
BRANCH = "ci-status"
MAX_FAIL_LINES = 20          # 每個失敗測試保留的訊息列數
LOG_TAIL = 80                # 失敗 job 的 log 保留最後幾列
LOG_CAP = 200                # 每個失敗 job 的 log 列數上限
LOG_KEY = re.compile(r"FAILED|Error|Traceback|[Pp]ython \d")
# GitHub 在步驟標頭列印「env:」區塊（"<時間戳> <空白>NAME: value"）；整個區塊丟棄，不輸出環境變數
ENV_HEAD = re.compile(r"^(?:\S+\s+)?env:\s*$")
ENV_ITEM = re.compile(r"^(?:\S+\s+)?\s{2,}(?!ERROR|FAILED|WARNING|Error)[A-Za-z_][A-Za-z0-9_]*: ")
GOOD = {"success", "skipped"}


# ---------------------------------------------------------------- GitHub API（可替換為假物件測試）
class _StripAuthOnRedirect(urllib.request.HTTPRedirectHandler):
    """artifact／log 的下載會 302 到預簽名的儲存網址；換網域時不得帶 Authorization。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlparse(newurl).netloc != urllib.parse.urlparse(req.full_url).netloc:
            new.headers.pop("Authorization", None)
            new.unredirected_hdrs.pop("Authorization", None)
        return new


class Api:
    def __init__(self, token, base="https://api.github.com"):
        self.token, self.base = token, base.rstrip("/")
        self._opener = urllib.request.build_opener(_StripAuthOnRedirect)

    def _get(self, path):
        url = path if path.startswith("http") else self.base + path
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                                                   "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "tokenomics-ci-status"})
        with self._opener.open(req, timeout=60) as r:
            return r.read()

    def get_json(self, path):
        return json.loads(self._get(path).decode("utf-8"))

    def get_bytes(self, path):
        return self._get(path)


# ---------------------------------------------------------------- 蒐集
def _secs(a, b):
    try:
        f = lambda s: datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")      # noqa: E731
        return int((f(b) - f(a)).total_seconds())
    except Exception:
        return None


def list_jobs(api, repo, run_id, attempt):
    jobs, page = [], 1
    while True:
        d = api.get_json(f"/repos/{repo}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100&page={page}")
        jobs += d.get("jobs", [])
        if len(d.get("jobs", [])) < 100 or len(jobs) >= d.get("total_count", 0):
            return jobs
        page += 1


def summarize_job(j):
    return dict(id=j.get("id"), name=j.get("name"), conclusion=j.get("conclusion") or j.get("status"),
                started_at=j.get("started_at"), completed_at=j.get("completed_at"), seconds=_secs(j.get("started_at"), j.get("completed_at")))


def junit_failures(xml_bytes, source):
    """失敗與錯誤的測試名稱與訊息（前 MAX_FAIL_LINES 列）。"""
    out = []
    root = ET.fromstring(xml_bytes)
    for c in root.iter("testcase"):
        for kind in ("failure", "error"):
            e = c.find(kind)
            if e is None:
                continue
            text = ((e.get("message") or "") + "\n" + (e.text or "")).strip().splitlines()
            out.append(dict(source=source, test=f"{c.get('classname', '')}::{c.get('name', '')}", kind=kind,
                            message="\n".join(text[:MAX_FAIL_LINES])))
    return out


def log_excerpt(text):
    """含 FAILED／Error／Traceback／python 版本字樣的列＋最後 LOG_TAIL 列；環境變數列丟棄；上限 LOG_CAP 列。"""
    lines, in_env = [], False
    for l in text.splitlines():
        if ENV_HEAD.match(l):
            in_env = True; continue
        if in_env and ENV_ITEM.match(l):
            continue
        in_env = False
        lines.append(l)
    tail = lines[-LOG_TAIL:]
    head = [l for l in lines[:max(0, len(lines) - LOG_TAIL)] if LOG_KEY.search(l)][:LOG_CAP - len(tail) - 1]      # -1：分隔列
    return head + (["…（以下為最後 %d 列）" % len(tail)] if head else []) + tail


def _zip_members(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    return {Path(n).name: z.read(n) for n in z.namelist() if not n.endswith("/")}


def collect(api, env, event=None):
    """回傳要寫入的 dict；任何一段取不到都記入 errors，不中斷。"""
    repo, run_id, attempt = env["GITHUB_REPOSITORY"], env["GITHUB_RUN_ID"], env.get("GITHUB_RUN_ATTEMPT", "1")
    event = event or {}
    name = env.get("GITHUB_EVENT_NAME", "")
    pr = event.get("pull_request") or {}
    errors = []
    out = dict(schema_version=SCHEMA_VERSION, repo=repo, sha=(pr.get("head") or {}).get("sha") or env.get("GITHUB_SHA"), github_sha=env.get("GITHUB_SHA"),
               ref=env.get("GITHUB_REF"), event=name, run_id=int(run_id), run_number=int(env.get("GITHUB_RUN_NUMBER", 0)), run_attempt=int(attempt),
               overall=env.get("OVERALL", ""), jobs=[], failures=[], log_excerpts={}, recalc_seconds=None)
    if name == "pull_request":
        out["pr_number"] = pr.get("number") or event.get("number")
    try:
        raw_jobs = list_jobs(api, repo, run_id, attempt)
        out["jobs"] = [summarize_job(j) for j in raw_jobs]
    except Exception as e:                                   # noqa: BLE001
        raw_jobs = []; errors.append(f"jobs: {e}")
    results = {}
    try:
        arts = api.get_json(f"/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100").get("artifacts", [])
        for a in arts:
            if not (a["name"].startswith("parity-results-") or a["name"] == "junit-scenario-guard"):
                continue
            try:
                files = _zip_members(api.get_bytes(f"/repos/{repo}/actions/artifacts/{a['id']}/zip"))
            except Exception as e:                           # noqa: BLE001
                errors.append(f"artifact {a['name']}: {e}"); continue
            if "junit.xml" in files:
                try:
                    out["failures"] += junit_failures(files["junit.xml"], a["name"])
                except Exception as e:                       # noqa: BLE001
                    errors.append(f"junit {a['name']}: {e}")
            if "_results_structure.json" in files:
                results = json.loads(files["_results_structure.json"].decode("utf-8"))
    except Exception as e:                                   # noqa: BLE001
        errors.append(f"artifacts: {e}")
    if results:
        inc = results.get("_incr_recalc") or {}
        out["recalc_seconds"] = dict(full=results.get("_full_recalc_seconds"), incremental_max=inc.get("max_seconds"),
                                     incremental_max_scenario=inc.get("max_scenario"), incremental_median=inc.get("median_seconds"))
    for j in raw_jobs:                                       # 只取失敗 job 的 log
        if (j.get("conclusion") or "") and j.get("conclusion") not in GOOD:
            try:
                out["log_excerpts"][j["name"]] = log_excerpt(api.get_bytes(f"/repos/{repo}/actions/jobs/{j['id']}/logs").decode("utf-8", "replace"))
            except Exception as e:                           # noqa: BLE001
                errors.append(f"log {j.get('name')}: {e}")
    out["generated_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out["errors"] = errors
    return out


def filename(d):
    return f"{d['sha']}/{d['run_number']}-a{d['run_attempt']}-{d['event']}.json"


# ---------------------------------------------------------------- 推送到孤立分支
README_BRANCH = """# ci-status

此分支由 `.github/workflows/parity.yml` 的 `ci-status` job 自動寫入（`tools/ci_status.py`），只放每次 CI run 的結果摘要，供 chat 端以
`git fetch origin ci-status` 讀取（chat 端沒有 GitHub 登入，未登入 API 次數不足）。請勿手動編輯；本分支不含模型或程式。

檔案：`<提交 SHA>/<run 編號>-a<重跑次數>-<事件>.json`（pull_request 事件的 SHA 為 PR 分支頭）。每次 run、每次重跑各一檔，不覆寫。

欄位：`schema_version`、`repo`、`sha`、`github_sha`（Actions 的 GITHUB_SHA；PR 為合併提交）、`ref`、`event`、`pr_number`（pull_request 才有）、
`run_id`、`run_number`、`run_attempt`、`overall`（job `parity` 的結果）、`jobs`（名稱、結論、起訖時間、秒數）、`failures`（失敗或錯誤的測試與訊息前 20 列）、
`log_excerpts`（只含失敗 job：含 FAILED／Error／Traceback／python 版本字樣的列及最後 80 列，每 job 上限 200 列）、
`recalc_seconds`（全簿與增量重算秒數）、`generated_at`、`errors`（蒐集時取不到的項目）。
"""
IDENT = ["-c", "commit.gpgsign=false", "-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com"]


def _git(args, cwd, check=True):
    return subprocess.run(["git", *args], cwd=cwd, check=check, capture_output=True, text=True)


def push_files(repo_dir, files, message, branch=BRANCH, remote="origin", retries=5):
    """以另開的 worktree 檢出 `branch`（不存在則建孤立分支並附 README.md），寫入 files（相對路徑 → bytes），提交並推送；
    推送失敗時 fetch＋rebase 後重試，最多 retries 次（檔名唯一，不會衝突）。回傳 True／False。"""
    repo_dir = str(repo_dir)
    tmp = tempfile.mkdtemp(prefix="ci-status-")
    wt = os.path.join(tmp, "wt")
    local = f"{branch}-wt-{os.getpid()}"        # 孤立分支的本機暫名（避免與既有本機分支衝突；結束時刪除）
    try:
        have = _git(["fetch", remote, branch], repo_dir, check=False).returncode == 0
        if have:
            _git(["worktree", "add", "--detach", wt, f"{remote}/{branch}"], repo_dir)
        else:
            _git(["worktree", "add", "--detach", wt, "HEAD"], repo_dir)
            _git(["checkout", "--orphan", local], wt)
            _git(["rm", "-rf", "--quiet", "."], wt, check=False)
            for p in Path(wt).iterdir():                     # 孤立分支只留 README.md
                if p.name != ".git":
                    shutil.rmtree(p) if p.is_dir() else p.unlink()
            Path(wt, "README.md").write_text(README_BRANCH, encoding="utf-8")
        for rel, data in files.items():
            p = Path(wt, rel); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        _git(["add", "-A"], wt)
        _git([*IDENT, "commit", "-q", "-m", message], wt)
        for i in range(retries):
            r = _git(["push", remote, f"HEAD:refs/heads/{branch}"], wt, check=False)
            if r.returncode == 0:
                return True
            print(f"push 失敗（第 {i + 1} 次）：{r.stderr.strip()[:300]}", file=sys.stderr)
            if _git(["fetch", remote, branch], wt, check=False).returncode == 0:
                _git([*IDENT, "rebase", f"{remote}/{branch}"], wt, check=False)
        return False
    finally:
        _git(["worktree", "remove", "--force", wt], repo_dir, check=False)
        _git(["branch", "-D", local], repo_dir, check=False)
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- 進入點
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True, help="輸出目錄（檔名見 filename()）")
    ap.add_argument("--push", action="store_true", help="另推送到孤立分支 ci-status（失敗不使本程式失敗）")
    a = ap.parse_args(argv)
    env = dict(os.environ)
    event = {}
    if env.get("GITHUB_EVENT_PATH") and Path(env["GITHUB_EVENT_PATH"]).exists():
        event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    d = collect(Api(env["GITHUB_TOKEN"], env.get("GITHUB_API_URL", "https://api.github.com")), env, event)
    rel = filename(d)
    p = Path(a.out, rel); p.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(d, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    p.write_bytes(data)
    print(f"寫入 {p}（jobs {len(d['jobs'])}、failures {len(d['failures'])}、errors {len(d['errors'])}）")
    if a.push:
        ok = push_files(Path.cwd(), {rel: data}, f"ci-status: {d['event']} run {d['run_number']} attempt {d['run_attempt']} {str(d['sha'])[:7]} → {d['overall']}")
        print(f"推送 {BRANCH}：{'成功' if ok else '失敗（已容忍）'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""tools/ci_status.py 的測試（工作單 v5.22 第 5 節第 6 項）：只用 fixture，不連網；推送測試用本機 bare repo。
由 structure-recalc 執行（parity.yml 的 -k 篩選不排除本檔）。不涉及模型與任何數值。"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import ci_status as cs  # noqa: E402

ENV = {"GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "900", "GITHUB_RUN_NUMBER": "180", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "mergesha000",
       "GITHUB_REF": "refs/pull/22/merge", "GITHUB_EVENT_NAME": "pull_request", "OVERALL": "failure"}
EVENT = {"number": 22, "pull_request": {"number": 22, "head": {"sha": "headsha1111"}}}
JUNIT = ('<testsuites><testsuite name="pytest" tests="3"><testcase classname="tests.parity.test_parity" name="test_ok" time="1"/>'
         '<testcase classname="tests.parity.test_parity" name="test_cache_matches_fresh[base]" time="2">'
         '<failure message="引擎快取已失效：python 3.11.16 ≠ 3.11.17">' + "\n".join(f"line {i}" for i in range(40)) + '</failure></testcase>'
         '<testcase classname="tests.parity.test_parity" name="test_err" time="1"><error message="boom">trace</error></testcase></testsuite></testsuites>')
RESULTS = {"_full_recalc_seconds": 1.53, "_incr_recalc": {"max_seconds": 0.73, "max_scenario": "f_registry_t07_t09_on", "median_seconds": 0.5, "n": 24}}


def _zip(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, d in files.items():
            z.writestr(n, d)
    return b.getvalue()


class FakeApi:
    """模擬 jobs／artifacts／zip／logs 回應；paths 記錄呼叫過的路徑。"""

    def __init__(self, jobs, artifacts=None, logs=None, fail=()):
        self.jobs, self.artifacts, self.logs, self.fail, self.paths = jobs, artifacts or {}, logs or {}, set(fail), []

    def get_json(self, path):
        self.paths.append(path)
        if "jobs" in self.fail and "/jobs" in path:
            raise RuntimeError("403")
        if "/attempts/2/jobs" in path:
            return {"total_count": len(self.jobs), "jobs": self.jobs}
        if path.endswith("/artifacts?per_page=100"):
            return {"artifacts": [{"id": i, "name": n} for i, n in enumerate(self.artifacts, start=1)]}
        raise AssertionError(path)

    def get_bytes(self, path):
        self.paths.append(path)
        if "/artifacts/" in path:
            return _zip(list(self.artifacts.values())[int(path.split("/artifacts/")[1].split("/")[0]) - 1])
        return self.logs[int(path.split("/jobs/")[1].split("/")[0])].encode("utf-8")


JOBS = [{"id": 1, "name": "engine-cache（建一次計算圖）", "conclusion": "success", "started_at": "2026-10-06T10:00:00Z", "completed_at": "2026-10-06T10:01:30Z"},
        {"id": 2, "name": "scenarios（第 3 片／共 6）", "conclusion": "failure", "started_at": "2026-10-06T10:02:00Z", "completed_at": "2026-10-06T10:05:00Z"},
        {"id": 3, "name": "governance（GOV_Errors 必須為 0；匯出 CSV）", "conclusion": "skipped", "started_at": None, "completed_at": None},
        {"id": 4, "name": "ci-status", "conclusion": None, "status": "in_progress", "started_at": "2026-10-06T10:06:00Z", "completed_at": None}]
ARTS = {"engine-cache": {"x.pkl": b"x"},
        "parity-results-scenarios-2": {"junit.xml": JUNIT, "tests/parity/_results_shard2.json": "{}"},
        "parity-results-structure": {"junit.xml": '<testsuite tests="1"><testcase classname="a" name="b"/></testsuite>',
                                     "tests/parity/_results_structure.json": json.dumps(RESULTS)},
        "junit-scenario-guard": {"junit.xml": '<testsuite tests="1"><testcase classname="g" name="guard"/></testsuite>'},
        "export-csv": {"Interface.csv": "a"}}
LOGS = {2: "2026-10-06T10:02:01Z env:\n2026-10-06T10:02:01Z   PARITY_SHARD: 2/6\n2026-10-06T10:02:01Z   GITHUB_TOKEN: ***\n"
           "2026-10-06T10:04:59Z FAILED tests/parity/test_parity.py::test_cache_matches_fresh[base] - RuntimeError: 引擎快取已失效：python 3.11.16 ≠ 3.11.17\n"
           "2026-10-06T10:05:00Z Process completed with exit code 1."}


def test_fields_filename_failures_and_logs():
    api = FakeApi(JOBS, ARTS, LOGS)
    d = cs.collect(api, ENV, EVENT)
    assert {"schema_version", "repo", "sha", "ref", "event", "pr_number", "run_id", "run_number", "run_attempt", "overall", "jobs", "failures",
            "log_excerpts", "recalc_seconds", "generated_at"} <= set(d)
    assert d["sha"] == "headsha1111" and d["github_sha"] == "mergesha000" and d["pr_number"] == 22 and d["overall"] == "failure"
    assert cs.filename(d) == "headsha1111/180-a2-pull_request.json"                      # PR：檔名用 PR 分支頭，不用合併提交
    assert [j["name"] for j in d["jobs"]] == [j["name"] for j in JOBS] and d["jobs"][0]["seconds"] == 90 and d["jobs"][1]["conclusion"] == "failure"
    assert d["jobs"][3]["conclusion"] == "in_progress" and d["jobs"][2]["seconds"] is None
    f = {x["test"]: x for x in d["failures"]}                                              # 1 個 failure＋1 個 error；訊息前 20 列
    assert set(f) == {"tests.parity.test_parity::test_cache_matches_fresh[base]", "tests.parity.test_parity::test_err"}
    assert f["tests.parity.test_parity::test_cache_matches_fresh[base]"]["kind"] == "failure"
    assert f["tests.parity.test_parity::test_cache_matches_fresh[base]"]["message"].splitlines()[0].startswith("引擎快取已失效")
    assert len(f["tests.parity.test_parity::test_cache_matches_fresh[base]"]["message"].splitlines()) == cs.MAX_FAIL_LINES
    assert f["tests.parity.test_parity::test_err"]["kind"] == "error"
    assert d["recalc_seconds"] == {"full": 1.53, "incremental_max": 0.73, "incremental_max_scenario": "f_registry_t07_t09_on", "incremental_median": 0.5}
    assert set(d["log_excerpts"]) == {"scenarios（第 3 片／共 6）"}                          # 只取失敗 job（success、skipped、進行中不取）
    ex = "\n".join(d["log_excerpts"]["scenarios（第 3 片／共 6）"])
    assert "FAILED" in ex and "python 3.11.16" in ex and "PARITY_SHARD" not in ex and "GITHUB_TOKEN" not in ex   # 環境變數區塊不輸出
    assert d["errors"] == []
    json.dumps(d, ensure_ascii=False)                                                      # 可序列化


def test_push_event_uses_github_sha_and_has_no_pr_number():
    env = dict(ENV, GITHUB_EVENT_NAME="push", GITHUB_REF="refs/heads/b")
    d = cs.collect(FakeApi(JOBS, ARTS, LOGS), env, {"after": "x"})
    assert d["sha"] == "mergesha000" and "pr_number" not in d and cs.filename(d) == "mergesha000/180-a2-push.json"


def test_missing_artifacts_and_results_still_output():
    d = cs.collect(FakeApi(JOBS[:1], artifacts={}), ENV, EVENT)
    assert d["failures"] == [] and d["recalc_seconds"] is None and d["log_excerpts"] == {} and d["errors"] == []
    d = cs.collect(FakeApi(JOBS, {"parity-results-scenarios-2": {"junit.xml": JUNIT}}, LOGS), ENV, EVENT)   # 缺 _results_structure.json
    assert d["recalc_seconds"] is None and len(d["failures"]) == 2
    d = cs.collect(FakeApi(JOBS, ARTS, LOGS, fail=("jobs",)), ENV, EVENT)                                   # jobs API 失敗：記入 errors，其餘照常
    assert d["jobs"] == [] and any(e.startswith("jobs:") for e in d["errors"]) and len(d["failures"]) == 2


def test_log_excerpt_line_cap_and_tail():
    text = "\n".join(f"2026-10-06T10:00:{i % 60:02d}Z FAILED case {i}" for i in range(1000))
    ex = cs.log_excerpt(text)
    assert len(ex) <= cs.LOG_CAP
    assert ex[-cs.LOG_TAIL:] == text.splitlines()[-cs.LOG_TAIL:]                          # 最後 80 列一定保留
    short = cs.log_excerpt("a\nb\nc")
    assert short == ["a", "b", "c"]
    mixed = "\n".join(["noise"] * 500 + ["Traceback (most recent call last):"] + ["noise"] * 500)
    ex = cs.log_excerpt(mixed)
    assert "Traceback (most recent call last):" in ex and len(ex) <= cs.LOG_CAP


def test_push_files_to_local_bare_repo(tmp_path):
    """孤立分支建立（附 README.md）、再次推送附加新檔、既有檔不覆寫；全程本機，不連網。"""
    def git(*a, cwd):
        return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
    bare, work = tmp_path / "remote.git", tmp_path / "work"
    git("init", "--bare", "-q", str(bare), cwd=tmp_path)
    git("clone", "-q", str(bare), str(work), cwd=tmp_path)
    (work / "model.txt").write_text("model", encoding="utf-8")
    git("add", "-A", cwd=work)
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init", cwd=work)
    git("push", "-q", "origin", "HEAD:refs/heads/main", cwd=work)
    assert cs.push_files(work, {"abc/1-a1-push.json": b'{"n":1}\n'}, "ci-status: first")
    assert cs.push_files(work, {"abc/2-a1-push.json": b'{"n":2}\n'}, "ci-status: second")
    git("fetch", "-q", "origin", "ci-status", cwd=work)
    files = set(git("ls-tree", "-r", "--name-only", "origin/ci-status", cwd=work).splitlines())
    assert files == {"README.md", "abc/1-a1-push.json", "abc/2-a1-push.json"}                # 孤立分支：沒有 model.txt
    assert git("rev-list", "--count", "origin/ci-status", cwd=work) == "2"
    assert git("log", "-1", "--format=%an", "origin/ci-status", cwd=work) == "github-actions[bot]"
    assert git("show", "origin/ci-status:abc/1-a1-push.json", cwd=work) == '{"n":1}'          # 既有檔不覆寫
    assert git("worktree", "list", cwd=work).count("\n") == 0                                 # worktree 已清除
    # 推送失敗（遠端不存在）不丟例外，回傳 False
    git("remote", "set-url", "origin", str(tmp_path / "nope.git"), cwd=work)
    assert cs.push_files(work, {"abc/3-a1-push.json": b"{}"}, "x", retries=1) is False


def test_main_writes_file(tmp_path, monkeypatch):
    """main：以 FakeApi 取代網路，輸出檔名與內容；缺 token 以外的環境變數齊全。"""
    ev = tmp_path / "event.json"; ev.write_text(json.dumps(EVENT), encoding="utf-8")
    for k, v in {**ENV, "GITHUB_TOKEN": "t", "GITHUB_EVENT_PATH": str(ev)}.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(cs, "Api", lambda token, base="": FakeApi(JOBS, ARTS, LOGS))
    assert cs.main(["--out", str(tmp_path / "out")]) == 0
    p = tmp_path / "out" / "headsha1111" / "180-a2-pull_request.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["pr_number"] == 22 and d["run_attempt"] == 2 and d["schema_version"] == 1
    assert "GITHUB_TOKEN" not in p.read_text(encoding="utf-8")

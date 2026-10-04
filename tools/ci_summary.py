#!/usr/bin/env python3
"""CI job summary（CLAUDE.md 第 3 節；2026-10-04 提速指令第 1 點）。只輸出，不影響任何斷言。

用法：
  python3 tools/ci_summary.py job <名稱> <junit.xml> [<_results.json>]   # 單一 job：測試結果、各測試秒數、重算秒數 → stdout（Markdown）
  python3 tools/ci_summary.py gate <結果目錄>                              # 彙總：各片情境聯集必須恰為 scenarios.yaml 全部情境
"""
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path(__file__).resolve().parent.parent


def job(name, junit, results):
    root = ET.parse(junit).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    cases = [c for s in suites for c in s.iter("testcase")]
    bad = [c for c in cases if c.find("failure") is not None or c.find("error") is not None]
    skipped = [c for c in cases if c.find("skipped") is not None]
    wall = sum(float(c.get("time", 0)) for c in cases)
    print(f"## {name}")
    print(f"- 測試：{len(cases)} 項；失敗 {len(bad)}；略過 {len(skipped)}；pytest 內計時合計 {wall:.0f} 秒")
    if results and Path(results).exists():
        d = json.loads(Path(results).read_text())
        sc = {k: v for k, v in d.items() if isinstance(v, dict)}
        if sc:
            print(f"- 情境 {len(sc)} 個；不符格數合計 {sum(v['n_mismatch'] for v in sc.values())}；"
                  f"含錯誤值的情境 {[k for k, v in sc.items() if v['error_value_cells']]}")
            print(f"- 增量重算（改輸入後）最大 {max(v['eval_all_seconds_after_change'] for v in sc.values())} 秒")
        if "_full_recalc_seconds" in d:
            print(f"- 全簿強制重算 {d['_full_recalc_seconds']} 秒")
        if sc:
            print("\n| 情境 | 不符格 | 增量重算（秒） | 改變格數 |\n|---|---|---|---|")
            for k, v in sc.items():
                print(f"| {k} | {v['n_mismatch']} | {v['eval_all_seconds_after_change']} | {v['changed_cells']} |")
    slow = sorted(cases, key=lambda c: -float(c.get("time", 0)))[:5]
    print("\n最慢 5 項：" + "；".join(f"{c.get('name')} {float(c.get('time', 0)):.0f}s" for c in slow))
    for c in bad:
        print(f"- ❌ {c.get('classname')}::{c.get('name')}")


def gate(folder):
    import yaml
    want = [s["id"] for s in yaml.safe_load((REPO / "tests/parity/scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]]
    got, dup = [], []
    for f in sorted(Path(folder).rglob("_results*.json")):
        for k, v in json.loads(f.read_text()).items():
            if isinstance(v, dict):
                (dup if k in got else got).append(k)
    miss = sorted(set(want) - set(got))
    extra = sorted(set(got) - set(want))
    print("## 情境覆蓋檢查（分片不得漏跑或重跑）")
    print(f"- scenarios.yaml：{len(want)} 個；各片合計 {len(got)} 個；缺 {miss}；多 {extra}；重複 {dup}")
    ok = not miss and not extra and not dup
    print("- ✅ 全部情境恰跑一次" if ok else "- ❌ 情境覆蓋不完整")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "job":
        job(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif cmd == "gate":
        gate(sys.argv[2])
    else:
        sys.exit(__doc__)

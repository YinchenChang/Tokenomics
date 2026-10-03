#!/usr/bin/env python3
"""匯出（規劃書第 6 節「CC 可以隨時匯出」）：SRC_*（A–W 欄）與 Interface → data/export/*.csv；並檢查 GOV_Errors。

用法：python3 tools/export_csv.py [--out data/export] [--check-only]
- 值一律由 engine（pycel）重算 model/CURRENT 指向的活頁簿；不另寫任何計算。
- GOV_Errors ≠ 0 時以非零狀態結束（CI 用；CLAUDE.md 第 3 節、第 11 輪指令第 5 節）。
- 匯出檔只供外部讀取，不寫回 Excel（CLAUDE.md 第 6 節）。
"""
import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from engine import Engine  # noqa: E402

SRC_SHEETS = ("SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=REPO / "data" / "export")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    eng = Engine()
    errors = eng.get_name("GOV_Errors")
    print(f"{eng.path.name}: GOV_Errors={errors} GOV_Warnings={eng.get_name('GOV_Warnings')} GOV_Info={eng.get_name('GOV_Info')}")
    if not a.check_only:
        a.out.mkdir(parents=True, exist_ok=True)
        for s in SRC_SHEETS + ("Interface",):
            last = "W" if s.startswith("SRC_") else "R"
            first = 4 if s.startswith("SRC_") else 1
            grid = eng.get(s, f"A{first}:{last}{600 if s.startswith('SRC_') else 200}")
            rows = [r for r in grid if any(x != "" for x in r)]
            with open(a.out / f"{s}.csv", "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows(rows)
            print(f"  {s}.csv：{len(rows)} 列")
    if errors != 0:
        print("GOV_Errors 不為 0", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

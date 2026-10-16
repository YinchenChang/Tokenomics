"""產生（或核對）區間時效指紋檔 builder/v1310_fingerprint.json（D15 B 段 P2-2）。

用法：
    python3 tools/gen_fingerprint.py <xlsx> [--version <檔名主幹>]     寫出指紋檔
    python3 tools/gen_fingerprint.py <xlsx> --check                     重新推導並與現有檔逐格比對

指紋＝區間所依賴的全部上游「數值常數格」（依賴圖：從 builder/v1300_ranges.json 列的 53 個契約名稱往上游追，口徑同死格偵測，不穿越治理頁）
與產生端點時的值。builder 把它寫成 Alloc P 節：每格一列（現值＝連結、記錄值＝黑字常數、不符旗標），
RNG_StaleFlag 與 Checks RG3 在任一格現值與記錄值不同時顯示『區間過期』（即使基準仍在 Lo／Hi 之內）。
本工具不需要 LibreOffice 重算：葉格是常數，直接讀檔。每次改版（或改動任何上游輸入）後必須重跑，並在同一個 PR 更新指紋檔。"""
import argparse
import json
import sys
from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "parity"))
import deadcells_lib  # noqa: E402

RANGES = REPO / "builder" / "v1300_ranges.json"
OUT = REPO / "builder" / "v1310_fingerprint.json"


def derive(src, version=None):
    rng = json.loads(RANGES.read_text(encoding="utf-8"))
    roots = sorted(rng["names"])
    leaves = deadcells_lib.upstream_numeric_leaves(src, roots)
    if version is None:
        wb = openpyxl.load_workbook(src, read_only=True)
        version = str(wb["README"]["B5"].value).split("（", 1)[0]
        wb.close()
    return {"version": version, "roots": len(roots), "leaves": [[s, a, v] for s, a, v in leaves]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx")
    ap.add_argument("--version")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    d = derive(Path(a.xlsx).resolve(), a.version)
    by = {}
    for s, _, _ in d["leaves"]:
        by[s] = by.get(s, 0) + 1
    print("根名稱", d["roots"], "| 上游數值常數格", len(d["leaves"]), "| 分布", by)
    if a.check:
        cur = json.loads(Path(a.out).read_text(encoding="utf-8"))
        bad = []
        if [(s, c) for s, c, _ in cur["leaves"]] != [(s, c) for s, c, _ in d["leaves"]]:
            bad.append("葉格集合不同")
        else:
            for (s, c, v), (_, _, w) in zip(cur["leaves"], d["leaves"]):
                if v != w:
                    bad.append((s, c, v, w))
        print("核對：", "全部一致" if not bad else f"不一致 {len(bad)}：{bad[:10]}")
        sys.exit(1 if bad else 0)
    Path(a.out).write_text(json.dumps(d, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print("已寫入", a.out)


if __name__ == "__main__":
    main()

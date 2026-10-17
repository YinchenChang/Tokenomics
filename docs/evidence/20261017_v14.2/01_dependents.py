"""v14.2 S1：列出 Cap_In 第 285、286 列各格的全部下游（依賴圖反向閉包），並對應到具名範圍。
用法：python3 -I 01_dependents.py <model.xlsx> [輸出 json]    （從 repo 根目錄執行）
只讀公式文字與具名範圍，不計算數值。"""
import sys, json, collections
sys.path.insert(0, "builder")
import openpyxl
from deps import Deps

wb = openpyxl.load_workbook(sys.argv[1])
D = Deps(wb)
rev = collections.defaultdict(set)
for k in D.formulas:
    for p in D.direct(k):
        rev[p].add(k)


def down(start):
    seen, st = set(), [start]
    while st:
        x = st.pop()
        for y in rev.get(x, ()):
            if y not in seen:
                seen.add(y); st.append(y)
    return seen


cell_names = collections.defaultdict(list)
for n, d in wb.defined_names.items():
    try:
        for k in D._resolve("", d.attr_text):
            cell_names[k].append(n)
    except Exception:
        pass
out = {}
for c in ("C285", "D285", "E285", "C286", "D286", "E286"):
    s = down(("Cap_In", c))
    out[c] = dict(n_cells=len(s), cells=sorted(f"{a}!{b}" for a, b in s), names=sorted({n for k in s for n in cell_names.get(k, [])}))
    print(c, "cells", len(s), "names", len(out[c]["names"]))
    print("  direct readers:", sorted(f"{a}!{b}" for a, b in rev[("Cap_In", c)]))
if len(sys.argv) > 2:
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print("D285 names:", out["D285"]["names"]); print("D286 names:", out["D286"]["names"])

"""4-3 A 段步驟 1b：把 B 級（無「用途」標記的死格）彙總成列，附標籤、值、公式、直接使用者、同列是否有核心格、4-0 規則編號。
用法：python3 21_rows_v131.py <dead.pkl> <rows.pkl>   （工作目錄＝repo 根）"""
import sys, pickle, re, collections
from pathlib import Path
REPO = Path.cwd()
sys.path.insert(0, str(REPO / "tests" / "parity"))
import deadcells_lib as D
import openpyxl
from openpyxl.utils import column_index_from_string as CI

P = pickle.load(open(sys.argv[1], "rb"))
model = REPO / "model" / P["model"]
CONTRACT = REPO / "docs" / "plan" / "Tokenomics_downstream_contract.md"
cells, names, maxrc, sheets = D.load_formulas(model, )
edges = D.build_graph(cells, names, maxrc)
wbv = openpyxl.load_workbook(model, data_only=True)

# 重建可達集合（同 dead_formula_cells）
gov = {"Gov_Map", "Decisions", "DB_Evidence", "Checks", "Load_Bearing"} | {s for s in sheets if s.startswith("SRC_")}
copies = {s for s in sheets if s.startswith("Sens_") or s == "Sensitivity" or s.endswith("_Prod")}
root_cells = [k for k in cells if k[0] == "Checks"] + [k for k in cells if k[0] in copies]
roots = [("NAME", n) for n in D.contract_names(names, CONTRACT)] + root_cells
rootset = set(root_cells)
seen = set(); stack = list(roots)
while stack:
    n = stack.pop()
    if n in seen: continue
    seen.add(n)
    if n[0] not in ("NAME", "RANGE") and n[0] in D.NO_TRAVERSE and n not in rootset: continue
    stack.extend(p for p in edges.get(n, ()) if p not in seen)
deadset = set(P["dead"])
unmarked = set(P["unmarked"])
assert len(deadset) == 3604

# 反向邊：直接使用者（穿過 NAME／RANGE 虛擬節點）
rev = collections.defaultdict(set)
for n, ps in edges.items():
    for p in ps: rev[p].add(n)
def direct_users(node):
    out = set(); st = [node]; sn = set()
    while st:
        cur = st.pop()
        for u in rev.get(cur, ()):
            if u in sn: continue
            sn.add(u)
            if u[0] in ("NAME", "RANGE"): st.append(u)
            else: out.add(u)
    return out
def ukind(k):
    us = direct_users(k)
    if not us: return "無任何格引用"
    ks = set()
    for u in us:
        if u[0] in gov or u[0] in D.NO_TRAVERSE: ks.add("治理頁")
        elif u[0] in copies: ks.add("複本頁")
        elif u in deadset: ks.add("死格")
        else: ks.add("核心")
    return "、".join(sorted(ks))
# 同列有核心格：同頁同列任一公式格或輸入格在 seen（可達）
core_rows = set()
for (s, a), f in cells.items():
    if (s, a) in seen and s not in gov:
        core_rows.add((s, int(re.search(r"\d+", a).group())))
def label(s, r):
    for col in ("A", "B"):
        x = wbv[s][f"{col}{r}"].value
        if isinstance(x, str) and x.strip(): return x.strip()
        if x is not None and not isinstance(x, str): pass
    f = cells.get((s, f"A{r}"))
    return str(f) if f else ""
rows = collections.OrderedDict()
for s, a in sorted(unmarked, key=lambda k: (sheets.index(k[0]), int(re.search(r"\d+", k[1]).group()), CI(re.match(r"[A-Z]+", k[1]).group()))):
    r = int(re.search(r"\d+", a).group())
    rows.setdefault((s, r), []).append(a)
out = []
for (s, r), al in rows.items():
    cols = [re.match(r"[A-Z]+", a).group() for a in al]
    a0 = al[0]
    uk = collections.Counter(ukind((s, a)) for a in al)
    vals = [wbv[s][a].value for a in al]
    out.append(dict(sheet=s, row=r, label=label(s, r), cells=al, cols=cols, n=len(al), formula=str(cells[(s, a0)])[:260], value=vals[0],
                    values=vals[:6], users=dict(uk), row_has_core=(s, r) in core_rows, nrowcells=sum(1 for (s2, a2) in unmarked if s2 == s and int(re.search(r"\d+", a2).group()) == r)))
print("rows", len(out), "cells", sum(x["n"] for x in out), "whole-row-dead", sum(1 for x in out if not x["row_has_core"]))
pickle.dump(out, open(sys.argv[2], "wb"))

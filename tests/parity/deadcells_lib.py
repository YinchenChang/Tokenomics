"""死格偵測（瘦身 4-1，永久測試用）。只讀公式文字（不需要重算值），由 4-0 盤點腳本 01_graph.py／02_audit.py 精簡而來。

定義（同 4-0）：
- 節點＝(工作表, 儲存格)；範圍引用與具名範圍以虛擬節點連到其中每一格（保守：整個範圍都算上游）。
- 根＝下游契約文件列出的名稱、所有 IF_／IFW_／IFC_／L1_／GOV_／CHK_／CAP_ 具名範圍、Checks 全部格；
  4-1 新增：Sens_＊／Sensitivity 與 ＊_Prod 複本頁的全部格也是根（它們是人讀的複本，讀取模型格不算死格）。
- 追溯上游時不穿越 Gov_Map、Decisions、DB_Evidence、Load_Bearing、SRC_Index（避免 Gov_Map 的「模型值」欄把每格都接到 GOV_）。
- 死格＝模型頁（非治理、非說明、非複本頁）上，不被任何根追到的公式格。
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import openpyxl
from openpyxl.formula import Tokenizer
from openpyxl.utils import get_column_letter as L, range_boundaries

ROOT_PREFIX = ("IF_", "L1_", "GOV_", "IFW_", "IFC_", "CHK_", "CAP_", "RNG_", "AL_Rng")      # v13.0 K2：RNG_（批次口徑區間端點與時效旗標）與 AL_Rng*（v12.0 區間表）也是契約名稱，納入根與快照
NO_TRAVERSE = {"Gov_Map", "Decisions", "DB_Evidence", "Load_Bearing", "SRC_Index"}
META_PAGES = {"README", "Sources_Legacy"}


def _split_sheet(ref, cur):
    if "!" in ref:
        sh, rg = ref.rsplit("!", 1)
        sh = sh.strip("'").replace("''", "'")
    else:
        sh, rg = cur, ref
    return sh, rg.replace("$", "")


def load_formulas(path):
    wb = openpyxl.load_workbook(path, data_only=False)
    cells = {}
    maxrc = {}
    for ws in wb.worksheets:
        maxrc[ws.title] = (ws.max_row, ws.max_column)
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    cells[(ws.title, c.coordinate)] = c.value
    names = {n: dn.attr_text for n, dn in wb.defined_names.items()}
    return cells, names, maxrc, [ws.title for ws in wb.worksheets]


def build_graph(cells, names, maxrc):
    sheets = set(maxrc)
    lnames = {n.lower(): n for n in names}
    edges = collections.defaultdict(set)

    def expand(sh, rg):
        if sh not in sheets:
            return []
        mr, mc = maxrc[sh]
        try:
            c1, r1, c2, r2 = range_boundaries(rg)
        except Exception:
            return []
        c1 = c1 or 1
        r1 = r1 or 1
        c2 = c2 or mc
        r2 = r2 or mr
        return [(sh, f"{L(c)}{r}") for r in range(r1, min(r2, mr) + 1) for c in range(c1, min(c2, mc) + 1) if (sh, f"{L(c)}{r}") in cells]

    ranges = set()

    def ref_node(tok, cur):
        if tok.lower() in lnames:
            return ("NAME", lnames[tok.lower()])
        if tok.startswith("#"):
            return None
        sh, rg = _split_sheet(tok, cur)
        if ":" in rg:
            return ("RANGE", f"{sh}!{rg}")
        if sh in sheets and re.fullmatch(r"[A-Z]{1,3}[0-9]+", rg):
            return (sh, rg)
        if f"{sh}!{rg}" in names:
            return ("NAME", f"{sh}!{rg}")
        return None

    for (sh, a), f in cells.items():
        if not (isinstance(f, str) and f.startswith("=")):
            continue
        try:
            toks = Tokenizer(f).items
        except Exception:
            continue
        for t in toks:
            if t.type == "OPERAND" and t.subtype == "RANGE":
                n = ref_node(t.value, sh)
                if n:
                    edges[(sh, a)].add(n)
                    if n[0] == "RANGE":
                        ranges.add(n[1])
    for n, t in names.items():
        tg = []
        for p in t.lstrip("=").split(","):
            sh, rg = _split_sheet(p, None)
            if sh not in sheets:
                continue
            if ":" in rg:
                tg.append(("RANGE", f"{sh}!{rg}"))
                ranges.add(f"{sh}!{rg}")
            else:
                tg.append((sh, rg))
        edges[("NAME", n)] = set(tg)
    for r in ranges:
        sh, rg = r.split("!", 1)
        edges[("RANGE", r)] = set(expand(sh, rg))
    return edges


def contract_names(names, contract_path):
    out = set()
    if contract_path and Path(contract_path).exists():
        txt = Path(contract_path).read_text(encoding="utf-8")
        for t in sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9]*_[A-Za-z0-9_\*]+", txt))):
            pat = "^" + re.escape(t).replace(r"\*", ".*") + "$"
            out.update(n for n in names if re.match(pat, n))
    out.update(n for n in names if n.startswith(ROOT_PREFIX))
    return out


def dead_formula_cells(path, contract_path, copies_are_roots=True):
    """回傳 (死格集合, 全部公式格數, 逐頁死格數)。copies_are_roots=False 時還原 4-0 的舊定義（供對照）。"""
    cells, names, maxrc, sheets = load_formulas(path)
    edges = build_graph(cells, names, maxrc)
    gov = {"Gov_Map", "Decisions", "DB_Evidence", "Checks", "Load_Bearing"} | {s for s in sheets if s.startswith("SRC_")}
    copies = {s for s in sheets if s.startswith("Sens_") or s == "Sensitivity" or s.endswith("_Prod")}
    root_cells = [k for k in cells if k[0] == "Checks"]
    if copies_are_roots:
        root_cells += [k for k in cells if k[0] in copies]
    roots = [("NAME", n) for n in contract_names(names, contract_path)] + root_cells
    rootset = set(root_cells)
    seen = set()
    stack = list(roots)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        if n[0] not in ("NAME", "RANGE") and n[0] in NO_TRAVERSE and n not in rootset:
            continue
        stack.extend(p for p in edges.get(n, ()) if p not in seen)
    model_pages = [s for s in sheets if s not in gov and s not in META_PAGES and s != "SRC_Index"]
    skip = set() if copies_are_roots else set()
    dead = set()
    nform = 0
    for (s, a), f in cells.items():
        if isinstance(f, str) and f.startswith("="):
            nform += 1
            if s in model_pages and s not in copies and (s, a) not in seen:
                dead.add((s, a))
    per_page = collections.Counter(s for s, _ in dead)
    return dead, nform, per_page

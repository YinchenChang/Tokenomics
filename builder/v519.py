# v5.19 (work order docs/workorders/20261006_v5.19.md): X1 production-derate side-by-side outputs; X2 Gov_Map P promotions.
#
# X1 mirrors the dependency chain that starts where Serving!C18 enters the model (Perf row 50 and Perf_Batch row 50; Sens_Perf
# row 50 also reads it but feeds none of the targets) and ends at the seven Theory_Rev rows behind IF_FullCost_* /
# IF_RevGW_* / IF_RevGWFleet. The chain is found from the workbook's own
# formulas at build time (forward cone of the seed cells ∩ backward cone of the target cells); it is not a hand-kept list.
# Each mirrored cell sits at the SAME address as its source on a *_Prod sheet, with two rewrites only:
#   (1) a reference to a cell that is in the chain points to the mirror sheet; every other reference is unchanged (made explicit
#       with its original sheet name); defined names whose range is in the chain are replaced by the mirror range;
#   (2) the seed cell (Perf row 50) reads CTL_ProdDerate instead of Serving!C18.
# A second copy to the right (columns +17) has the seed cell on Serving!C18 and feeds the self-check (Checks X1): with the
# substitute set back to C18 the seven Prod rows must equal the baseline rows. No Python-side arithmetic anywhere.
import re
import collections
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from copy import copy
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY, FILL_SEC, WRAP, title, section

C18 = "=Serving!$C$18"
SEED_COLS = range(3, 18)                                   # C:Q (5 generations x 3 columns); also the span of the Theory_Rev targets
PROD_SHEETS = ["Perf_Prod", "Perf_Batch_Prod", "Training_Prod", "Unit_Cost_Prod", "Interface_Prod", "Fleet_1GW_Prod", "Amortize_Prod", "Theory_Rev_Prod"]
SRC_SHEETS = [x[:-len("_Prod")] for x in PROD_SHEETS]
# (Theory_Rev row, Interface name of the baseline row, new name)
TARGETS = [(18, "IF_FullCost_Luna"), (36, "IF_FullCost_Sol"), (54, "IF_FullCost_Astra"),
           (11, "IF_RevGW_Luna"), (29, "IF_RevGW_Sol"), (47, "IF_RevGW_Astra"), (67, "IF_RevGWFleet")]
SHIFT = 16                                                 # check copy: columns S:AG (C+16 … Q+16)
SUFFIX = "_Prod"
NEW_INPUT_ROW = 28                                         # Serving row of CTL_ProdDerate (after the existing content, no shifts)
CTL_DEFAULT = 0.85
TAG = re.compile(r"　\[[A-Za-z0-9_]+\]\s*$")

_CELL = re.compile(r"^(\$?)([A-Z]{1,3})(\$?)(\d+)$")


def _qs(sh):
    return f"'{sh}'" if re.search(r"[^A-Za-z0-9_]", sh) else sh


def _parse(tok, cur):
    if "!" in tok:
        sh, rg = tok.rsplit("!", 1)
        return sh.strip("'"), rg, True
    return cur, tok, False


def _bounds(rg):
    try:
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    except Exception:
        return None
    if None in (c1, r1, c2, r2):
        return None
    return c1, r1, c2, r2


def _formula_cells(wb):
    return {(ws.title, c.column, c.row): c.value for ws in wb for row in ws.iter_rows() for c in row
            if isinstance(c.value, str) and c.value.startswith("=")}


def _refs(wb, names, cells):
    """formula cell -> list of (sheet, c1, r1, c2, r2) it reads (defined names expanded)."""
    sheets = set(wb.sheetnames)
    out = {}
    for key, f in cells.items():
        refs = []
        for t in Tokenizer(f).items:
            if t.type == "OPERAND" and t.subtype == "RANGE":
                parts = names[t.value].split(",") if t.value in names else [t.value]
                for p in parts:
                    sh, rg, _ = _parse(p, key[0])
                    b = _bounds(rg)
                    if b and sh in sheets:
                        refs.append((sh, *b))
        out[key] = refs
    return out


def chain_cells(wb):
    """The mirrored cell set: forward cone of the seed ∩ backward cone of the targets."""
    names = {n: wb.defined_names[n].attr_text for n in wb.defined_names}
    cells = _formula_cells(wb)
    refs = _refs(wb, names, cells)
    by_sheet = collections.defaultdict(list)
    for key, rl in refs.items():
        for (sh, c1, r1, c2, r2) in rl:
            by_sheet[sh].append((key, c1, r1, c2, r2))
    seeds = [k for k, rl in refs.items() if any(sh == "Serving" and c1 <= 3 <= c2 and r1 <= 18 <= r2 for (sh, c1, r1, c2, r2) in rl)]
    assert seeds and all(cells[k] == C18 for k in seeds if k[0] != "Gov_Map"), "unexpected reader of Serving!C18"
    fwd, frontier = set(seeds), list(seeds)
    while frontier:
        nxt = []
        grid = collections.defaultdict(set)
        for sh, c, r in frontier:
            grid[sh].add((c, r))
        for sh, pts in grid.items():
            for key, c1, r1, c2, r2 in by_sheet[sh]:
                if key not in fwd and any(c1 <= c <= c2 and r1 <= r <= r2 for c, r in pts):
                    fwd.add(key); nxt.append(key)
        frontier = nxt
    targets = [("Theory_Rev", c, r) for r, _ in TARGETS for c in SEED_COLS]
    bwd, stack = set(targets), list(targets)
    while stack:
        key = stack.pop()
        for (sh, c1, r1, c2, r2) in refs.get(key, []):
            for c in range(c1, c2 + 1):
                for r in range(r1, r2 + 1):
                    k = (sh, c, r)
                    if k in cells and k not in bwd:
                        bwd.add(k); stack.append(k)
    S = fwd & bwd
    seeds = {k for k in seeds if k in S}
    return S, cells, names, seeds


def _shift_ref(rg, shift):
    """shift the column of an A1 reference or range, keeping $ markers"""
    def one(x):
        m = _CELL.match(x)
        return f"{m.group(1)}{L(openpyxl_col(m.group(2)) + shift)}{m.group(3)}{m.group(4)}"
    return ":".join(one(x) for x in rg.split(":"))


def openpyxl_col(letters):
    from openpyxl.utils import column_index_from_string
    return column_index_from_string(letters)


def mirror_formula(f, cur, S, names, shift):
    """rewrite one formula (see header); asserts that no range is split between chain and non-chain cells"""
    out = ["="]
    for t in Tokenizer(f).items:
        v = t.value
        if t.type == "OPERAND" and t.subtype == "RANGE":
            parts = names[v].split(",") if v in names else [v]
            hit, miss = 0, 0
            for p in parts:
                sh, rg, _ = _parse(p, cur)
                b = _bounds(rg)
                assert b, f"unparseable reference {v!r} in {f!r}"
                c1, r1, c2, r2 = b
                n = sum((sh, c, r) in S for c in range(c1, c2 + 1) for r in range(r1, r2 + 1))
                hit += n > 0; miss += n < (c2 - c1 + 1) * (r2 - r1 + 1)
            assert not (hit and miss), f"range split between chain and non-chain cells: {v!r} in {f!r}"
            if hit:                                                  # entirely inside the chain -> mirror range
                new = []
                for p in parts:
                    sh, rg, _ = _parse(p, cur)
                    new.append(f"{_qs(sh + SUFFIX)}!{_shift_ref(rg, shift)}")
                v = ",".join(new)
            elif v in names:
                pass                                                 # a name outside the chain stays a name
            else:
                sh, rg, explicit = _parse(v, cur)
                v = v if explicit else f"{_qs(sh)}!{rg}"
        out.append(v)
    return "".join(out)


def build_chain(wb):
    """Create the *_Prod sheets; returns info for the report (cell counts, sheets, rows)."""
    S, cells, names, seeds = chain_cells(wb)
    assert S and all(3 <= c <= 17 for (_, c, _) in S), "chain must live in columns C:Q"
    for key in S:
        assert mirror_formula(cells[key], key[0], set(), names, 0) is not None
    # tokenizer round trip must reproduce every formula (guards the rewrite)
    for key in S:
        assert "=" + "".join(t.value for t in Tokenizer(cells[key]).items) == cells[key], f"tokenizer round trip {key}"
    sheets = [s for s in SRC_SHEETS if any(k[0] == s for k in S)]
    assert sorted({k[0] for k in S}) == sorted(sheets) == sorted(SRC_SHEETS), sorted({k[0] for k in S})
    rows_of = {s: sorted({r for (sh, _, r) in S if sh == s}) for s in sheets}
    for s in sheets:
        src = wb[s]; ws = wb.create_sheet(s + SUFFIX)
        title(ws, f"{s}{SUFFIX} — {s} 的鏡像（v5.19 X1：生產折減並列輸出）",
              "同位置鏡像：公式逐格同 " + s + "，只改兩處——(1) 讀到鏈上其他格者改讀本組 *_Prod 頁；(2) Perf_Prod 與 Perf_Batch_Prod 第 50 列改讀 CTL_ProdDerate（Serving!C28），"
              "其餘仍讀原頁。右側 S:AG 為自我檢查副本（第 50 列＝Serving!C18，Checks X1）。只含從 Serving!C18 的進入點（兩個第 50 列）算到七個 _Prod 輸出所需的列。")
        for c in "ABCDEFGHIJKLMNOPQ":
            if src.column_dimensions[c].width: ws.column_dimensions[c].width = src.column_dimensions[c].width
        for i in range(19, 34): ws.column_dimensions[L(i)].width = src.column_dimensions["C"].width or 12
        ws.freeze_panes = src.freeze_panes
        for blk, shift in (("主", 0), ("檢查副本", SHIFT)):
            for r in (4, 5, 6, 7):                                    # header band (links; copies of the source header rows)
                for c in SEED_COLS:
                    sc = src.cell(r, c)
                    if sc.value is not None:
                        put(ws, f"{L(c + shift)}{r}", f"={_qs(s)}!{L(c)}{r}", fmt=sc.number_format, fill=copy(sc.fill) if sc.fill.fill_type else None)
            if shift:
                put(ws, f"{L(3 + shift)}3", "自我檢查副本（第 50 列＝Serving!C18；Checks X1 比對）", F_BOLD)
        for r in (4, 5, 6, 7): put(ws, f"A{r}", f"={_qs(s)}!A{r}"); put(ws, f"B{r}", f"={_qs(s)}!B{r}") if src.cell(r, 2).value is not None else None
        for r in rows_of[s]:
            for c in (1, 2):
                v = src.cell(r, c).value
                if v is None: continue
                put(ws, f"{L(c)}{r}", f"={_qs(s)}!{L(c)}{r}" if isinstance(v, str) and v.startswith("=") else v,
                    F_NOTE if c == 2 else None)
            for c in SEED_COLS:
                key = (s, c, r)
                if key not in S: continue
                sc = src.cell(r, c)
                for blk, shift in (("主", 0), ("檢查", SHIFT)):
                    if key in seeds:
                        f = "=CTL_ProdDerate" if shift == 0 else C18
                    else:
                        f = mirror_formula(cells[key], s, S, names, shift)
                    put(ws, f"{L(c + shift)}{r}", f, fmt=sc.number_format, fill=copy(sc.fill) if sc.fill.fill_type else None)
    return dict(S=S, sheets=sheets, rows=rows_of, cells=len(S), seeds=len(seeds))


def interface_x1(wb, start, info):
    """Interface G: seven rows, C:Q, one per target; named IF_*_Prod. Labels, units, formats follow the baseline rows."""
    ws = wb["Interface"]; r = start
    section(ws, r, "G. 生產折減並列輸出（X1，v5.19）：C18（Serving）維持 1.0；本節以 CTL_ProdDerate（Serving!C28，情境值，預設 0.85）"
                   "重算同一條推導鏈（Perf_Prod → Unit_Cost_Prod → Interface_Prod → Fleet_1GW_Prod → Amortize_Prod → Theory_Rev_Prod）。"
                   "口徑同 D 節對應列；SLO 不可達時為文字", 17); r += 1
    made = []
    for trow, base in TARGETS:
        nm = wb.defined_names[base].attr_text
        m = re.match(r"Interface!\$C\$(\d+):\$Q\$(\d+)", nm); brow = int(m.group(1))
        lab = TAG.sub("", ws.cell(brow, 1).value)
        put(ws, f"A{r}", f"{lab}（生產折減 CTL_ProdDerate）　[{base}{SUFFIX}]"); put(ws, f"B{r}", ws.cell(brow, 2).value)
        for c in SEED_COLS:
            bc = ws.cell(brow, c)
            put(ws, f"{L(c)}{r}", f"=Theory_Rev{SUFFIX}!{L(c)}{trow}", fmt=bc.number_format, fill=copy(bc.fill) if bc.fill.fill_type else None)
        made.append((f"{base}{SUFFIX}", f"Interface!$C${r}:$Q${r}", trow, r)); r += 1
    for n, ref, _, _ in made:
        if n in wb.defined_names: del wb.defined_names[n]
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return made


def checks_x1(wb, made):
    """Theory_Rev_Prod self-check flags (rows 90–96) and Checks X1 (ERROR, counted in GOV_Errors)."""
    tr = wb["Theory_Rev" + SUFFIX]
    put(tr, "A89", "自我檢查（v5.19 X1）：檢查副本（第 50 列＝Serving!C18）對基準列；0＝相同（容差 1e-12；兩邊皆為文字時不報錯）", F_BOLD)
    flag_rows = []
    for i, (trow, base) in enumerate(TARGETS):
        rr = 90 + i
        put(tr, f"A{rr}", f"{base}：檢查副本 vs 原 Theory_Rev 第 {trow} 列", F_NOTE)
        for c in SEED_COLS:
            a, b = f"{L(c + SHIFT)}{trow}", f"Theory_Rev!{L(c)}{trow}"
            put(tr, f"{L(c)}{rr}", f"=IF(AND(ISNUMBER({a}),ISNUMBER({b})),IF(ABS({a}-{b})<=1E-12*MAX(1,ABS({b})),0,1),"
                                   f"IF(AND(NOT(ISNUMBER({a})),NOT(ISNUMBER({b}))),0,1))", fmt="0")
        flag_rows.append(rr)
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "X. 生產折減並列輸出檢查（工作單 X1，v5.19）：X1 為 ERROR 計入 GOV_Errors", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    put(ws, f"A{r}", "X1"); put(ws, f"B{r}", "生產折減並列輸出的自我檢查：替代值改回 Serving!C18 時，七個 _Prod 列不等於對應基準列的格數"); put(ws, f"C{r}", "ERROR", F_BOLD)
    put(ws, f"D{r}", f"=SUM(Theory_Rev{SUFFIX}!C{flag_rows[0]}:Q{flag_rows[-1]})", fmt="0")
    put(ws, f"E{r}", f"Theory_Rev_Prod 第 {flag_rows[0]}–{flag_rows[-1]} 列 × C:Q（7 × 15＝105 格；檢查副本在 S:AG，不需手動改輸入）", F_NOTE)
    ref = wb.defined_names["GOV_Errors"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "ERROR 合計（CI 讀取 GOV_Errors；含 G、H、X 節）"
    return r


def serving_input(ws):
    """Serving row 28: CTL_ProdDerate (blue input, new row after the existing content, nothing moves)."""
    put(ws, f"A{NEW_INPUT_ROW}", "並列輸出用生產折減（情境值，X1；非估計值）"); put(ws, f"B{NEW_INPUT_ROW}", "x")
    put(ws, f"C{NEW_INPUT_ROW}", CTL_DEFAULT, fmt="0.00")
    put(ws, f"D{NEW_INPUT_ROW}", "情境值", F_NOTE)
    put(ws, f"F{NEW_INPUT_ROW}", "v5.19 X1：只驅動 Interface G 節的 _Prod 並列輸出（Perf_Prod 第 50 列）；Serving!C18 維持 1.0（G0-11），不受影響。"
                                 "0.85＝C18 區間 0.7–1.0 的中點，不是估計值；Andy 日後給 C18 值時，本格可保留作並列情境", F_NOTE)
    ws[f"C{NEW_INPUT_ROW}"].fill = copy(ws["C18"].fill)
    wb = ws.parent
    if "CTL_ProdDerate" in wb.defined_names: del wb.defined_names["CTL_ProdDerate"]
    wb.defined_names["CTL_ProdDerate"] = DefinedName("CTL_ProdDerate", attr_text=f"Serving!$C${NEW_INPUT_ROW}")


def x1(wb):
    info = build_chain(wb)
    made = interface_x1(wb, max(c.row for row in wb["Interface"].iter_rows() for c in row if c.value is not None) + 2, info)
    info["made"] = made
    info["check_row"] = checks_x1(wb, made)
    return info


# ------------------------------------------------------------------ X2 (Gov_Map P column; promotions only, never demotions)
# (GM_ID, sheet, cell, old P, swing text for the note column)   — chat-side scan 2026-10-06, work order 2.2
X2 = [
    ("GM205", "Arch", "E8", "中", "−14.8%／+82.4%（低／高端；IF_FullCost_Astra VR200）"),
    ("GM586", "Alloc_In", "C15", "中", "−15.1%／+60.2%（低／高端；IF_AllocServeGW）"),
    ("GM578", "Alloc_In", "C7", "中", "−45.0%／+45.0%（低／高端；IF_AllocRDGW）"),
    ("GM104", "Spec_Rack", "G23", "中", "+43.5%／−23.3%（低／高端；IF_FullCost_Sol Rubin Ultra）"),
    ("GM270", "Workload", "G8", "中", "−21.5%／+43.0%（低／高端；L1_Ans9）"),
    ("GM459", "Cap_In", "C36", "低", "−0.7%／+39.5%（低／高端；L1_Ans9）"),
    ("GM275", "Workload", "G9", "中", "−17.9%／+35.9%（低／高端；L1_Ans9）"),
    ("GM304", "Calib", "C5", "中", "−33.0%／+11.1%（低／高端；L1_Ans4）"),
    ("GM290", "Workload", "G12", "無", "+0.0%／+100.0%（低／高端；L1_Ans9）"),
    ("GM203", "Arch", "E6", "中", "+6.8%／+24.3%（低／高端；IF_RevGW_Astra VR200）"),
    ("GM354", "Calib", "F69", "中", "+23.0%／−7.7%（低／高端；L1_Ans9）"),
]


def x2_note(swing):
    return f" ｜v5.19 X2 升段：單變數擺動 {swing}；chat 端掃描 2026-10-06"


def gov_update(ws, append_text):
    """Promote P to 高 (only while the cell still holds the v5.18 value, same rule as gov.gm_update) and append the note to N."""
    loc = {(ws[f"C{r}"].value, ws[f"D{r}"].value): r for r in range(5, ws.max_row + 1) if ws[f"C{r}"].value}
    n = 0
    for gm, sh, cell, old, swing in X2:
        r = loc.get((sh, cell))
        assert r is not None and ws[f"A{r}"].value == gm, f"X2: {gm} {sh}!{cell} not at the expected Gov_Map row"
        if ws[f"P{r}"].value == old:
            ws[f"P{r}"].value = "高"; n += 1
            append_text(ws[f"N{r}"], x2_note(swing))
    return n


# ------------------------------------------------------------------ Gov_Map row, Decisions
GOV_MAP_V519 = [{'scope': '切片三（v5.19 X1）', 'sheet': 'Serving', 'cell': f'C{NEW_INPUT_ROW}',
                 'label': '並列輸出用生產折減（CTL_ProdDerate）', 'check': '並列輸出用生產折減（情境值，X1；非估計值）',
                 'cls': '情境值', 'role': '單值', 'src': '', 'rel': '', 'dec': 'X1', 'lo': 0.7, 'hi': 1.0,
                 'rtext': '區間 0.7–1.0（同 Serving!C18 的區間）',
                 'reason': 'X1：C18 區間中點，非估計值；C18 依 G0-11 維持 1.0', 'retag': '', 'seg': '高'}]

DECISIONS_V519 = [
    ['X1', 'v5.19', 'Serving C18 凍結並列輸出（生產折減）',
     'Serving C18（J15 生產折減）維持凍結（G0-11 不變），交接檔揭露擺動；v5.19 在 Interface G 節新增七列並列輸出（IF_FullCost_*_Prod、IF_RevGW_*_Prod、IF_RevGWFleet_Prod），'
     '由新輸入格 CTL_ProdDerate（Serving!C28，預設 0.85，區間 0.7–1.0，情境值）驅動；推導鏈以 *_Prod 鏡像頁重算，自我檢查 Checks X1',
     '2026-10-06', '「both OK」（回覆 chat 端 D1 建議：先 (a)，v5.19 做 (b)）', 'v5.19 已建',
     'Serving!C28（CTL_ProdDerate）；Interface G 節；Perf_Prod、Unit_Cost_Prod、Interface_Prod、Fleet_1GW_Prod、Amortize_Prod、Theory_Rev_Prod；Checks X1', '工作單 v5.19 第 0、1 節', '否'],
    ['X2', 'v5.19', 'Gov_Map P 欄升段規則（只升不降、不追溯）',
     'Gov_Map 數值區間端點單變數擺動 ≥20% 的非高段格升為高段（輸出範圍與排除見工作單 v5.19 第 2.1 節）；類別為 Decision 的格不適用；現為高段者不降；v5.17／v5.18 完成判定維持有效。'
     'v5.19 升段 11 格：GM205、GM586、GM578、GM104、GM270、GM459、GM275、GM304、GM290、GM203、GM354；未升：GM480（Decision）、GM443（19.9%）',
     '2026-10-06', '「both OK」（回覆 chat 端 D2 建議 (b)，門檻 20%）', 'v5.19 已建',
     'Gov_Map P 欄（11 格）；Checks G 節 W2', '工作單 v5.19 第 0、2 節', '否'],
]

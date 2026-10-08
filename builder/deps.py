# v5.29 (work order docs/workorders/20261008_v5.29.md r1, section 1 and 4): static precedent tracing at build time.
# Why: Excel has no formula that can walk a cell's precedent chain, so the Confidence column (Interface R) and the
# "affected L1 rows" column (Load_Bearing) are expanded by the builder: for every Interface row we collect the cells its
# formulas depend on (transitively), intersect them with the cells registered in Gov_Map, and write a formula that reads
# those Gov_Map rows live (the judgement columns stay in Excel; only the list of GM rows is static).
# Conservative: a range argument (e.g. INDEX(Perf!$C$95:$Q$95, …)) counts every cell of the range as a precedent, so a row
# may be attributed inputs of other generations／tiers (reported as over-attribution, never under-attribution).
# No arithmetic, no values: this module only reads formula text and defined names.
import re
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter

MAX_RANGE_CELLS = 20000           # a bigger range is still expanded (none in the workbook is close to this)
_SHEET_REF = re.compile(r"^(?:'((?:[^']|'')+)'|([^'!]+))!(.+)$")
_CELL = re.compile(r"^\$?[A-Z]{1,3}\$?\d+$")
_RANGE = re.compile(r"^\$?[A-Z]{1,3}\$?\d+:\$?[A-Z]{1,3}\$?\d+$")


def _expand(sheet, ref):
    ref = ref.replace("$", "")
    if _CELL.match(ref):
        return [(sheet, ref)]
    if _RANGE.match(ref):
        c1, r1, c2, r2 = range_boundaries(ref)
        if (c2 - c1 + 1) * (r2 - r1 + 1) > MAX_RANGE_CELLS:
            raise ValueError(f"range too large: {sheet}!{ref}")
        return [(sheet, f"{get_column_letter(c)}{r}") for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
    return []                      # whole-column／row refs and structured refs are not used in this workbook


class Deps:
    def __init__(self, wb):
        self.wb = wb
        self.names = {n: d.attr_text for n, d in wb.defined_names.items()}
        self.formulas = {}
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    v = c.value
                    if isinstance(v, str) and v.startswith("="):
                        self.formulas[(ws.title, c.coordinate)] = v
        self._direct = {}
        self._closure = {}

    # ---- direct precedents of one formula cell
    def direct(self, key):
        if key in self._direct: return self._direct[key]
        sheet, _ = key
        out = set()
        f = self.formulas.get(key)
        if f:
            try:
                toks = Tokenizer(f).items
            except Exception:
                toks = []
            for t in toks:
                if t.type != "OPERAND" or t.subtype != "RANGE": continue
                out.update(self._resolve(sheet, t.value))
        self._direct[key] = out
        return out

    def _resolve(self, sheet, text):
        text = text.strip()
        m = _SHEET_REF.match(text)
        if m:
            sh = (m.group(1) or m.group(2)).replace("''", "'")
            return _expand(sh, m.group(3))
        if _CELL.match(text) or _RANGE.match(text):
            return _expand(sheet, text)
        if text in self.names:                      # defined name -> its destination
            return self._resolve(sheet, self.names[text])
        return []                                   # TRUE／FALSE, function names mis-tokenised, etc.

    # ---- transitive closure (iterative, memoised, cycle-safe)
    def closure(self, key):
        if key in self._closure: return self._closure[key]
        seen = set(); stack = [key]
        while stack:
            k = stack.pop()
            for p in self.direct(k):
                if p in seen: continue
                seen.add(p)
                if p in self._closure:
                    seen.update(self._closure[p]); continue
                if p in self.formulas: stack.append(p)
        self._closure[key] = seen
        return seen

    def closure_many(self, keys):
        out = set()
        for k in keys: out |= self.closure(k)
        return out


def gov_map_cells(wb):
    """(sheet, cell) -> set of Gov_Map row numbers registering that cell (ranges expanded)."""
    ws = wb["Gov_Map"]; out = {}
    for r in range(5, ws.max_row + 1):
        sh, cell = ws.cell(r, 3).value, ws.cell(r, 4).value
        if not sh or not cell or sh not in wb.sheetnames: continue
        for k in _expand(sh, str(cell)):
            out.setdefault(k, set()).add(r)
    return out

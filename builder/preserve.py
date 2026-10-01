# v5.7: Excel-first input preservation.
# Before Block 2/3 sheets are deleted and rebuilt, snapshot every input cell (blue font, constant value);
# after rebuild, write the Excel value back wherever the same sheet / column-A label / column still holds an input.
# Code defaults therefore apply only to NEW input rows; existing inputs are owned by the Excel file.
BLUE = "FF0000FF"
REBUILT = ["Spec_Rack", "Arch", "Serving", "Workload", "Calib", "Energy", "NonNV", "Tech_Registry", "Perf",
           "Sens_Perf", "Unit_Cost", "Train_In", "Perf_Batch", "Training", "Sens_Train",
           "Cap_In", "Capability", "Price_Frontier", "Cache_Store", "Fleet_1GW", "Amortize", "Theory_Rev", "Sens_Rev",
           "Har_In", "Harness", "Sens_Har"]

def _is_input(cell):
    v = cell.value
    if v is None or (isinstance(v, str) and v.startswith("=")):
        return False
    c = cell.font.color if cell.font else None
    return c is not None and c.type == "rgb" and c.rgb == BLUE

def _keys(ws, min_row):
    seen = {}
    for r in range(min_row, ws.max_row + 1):
        lab = ws.cell(row=r, column=1).value
        if lab is None or (isinstance(lab, str) and lab.startswith("=")):
            continue
        k = (str(lab), seen.get(str(lab), 0)); seen[str(lab)] = k[1] + 1
        yield r, k

def snapshot(wb):
    snap = {}
    for s in REBUILT:
        if s not in wb.sheetnames: continue
        ws = wb[s]; r0 = 21 if s == "Spec_Rack" else 1
        for r, k in _keys(ws, r0):
            for c in range(2, ws.max_column + 1):
                cell = ws.cell(row=r, column=c)
                if _is_input(cell):
                    snap[(s, k, c)] = cell.value
    return snap

def restore(wb, snap, log_path=None):
    matched = changed = 0; lines = []
    present = set()
    for s in REBUILT:
        ws = wb[s]; r0 = 21 if s == "Spec_Rack" else 1
        for r, k in _keys(ws, r0):
            for c in range(2, ws.max_column + 1):
                key = (s, k, c)
                if key not in snap: continue
                cell = ws.cell(row=r, column=c)
                if not _is_input(cell): continue
                present.add(key); matched += 1
                if cell.value != snap[key]:
                    lines.append(f"{s}!{cell.coordinate} [{k[0]}]: code default {cell.value!r} -> Excel {snap[key]!r}")
                    cell.value = snap[key]; changed += 1
    dropped = [f"{s} [{k[0]}] col {c}: {v!r}" for (s, k, c), v in snap.items() if (s, k, c) not in present]
    report = [f"inputs in base: {len(snap)}; restored (matched): {matched}; Excel value kept over code default: {changed}; "
              f"base inputs with no matching input cell in rebuild: {len(dropped)}"] + lines + ["-- unmatched --"] + dropped
    if log_path: open(log_path, "w").write("\n".join(report))
    return matched, changed, dropped

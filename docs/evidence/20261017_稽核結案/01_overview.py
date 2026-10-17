import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
wb = lib.val()
print(lib.CUR)
for ws in wb:
    print(ws.title, ws.max_row, ws.max_column)
print('names', len(wb.defined_names))
ws = wb['Decisions']
for r in list(ws.iter_rows(min_row=1, max_row=6, values_only=True)):
    print([str(c)[:50] if c is not None else None for c in r])

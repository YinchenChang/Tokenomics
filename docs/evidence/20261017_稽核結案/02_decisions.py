import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
ws = lib.val()['Decisions']
rows = []
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[0]:
        rows.append([str(c) if c is not None else '' for c in r])
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decisions.json'), 'w'), ensure_ascii=False, indent=0)
print(len(rows))
for r in rows:
    if not r[0].startswith('D') or not r[0][1:].isdigit():
        print(r[0], '|', r[1][:20], '|', r[2][:50], '|', r[4][:20], '|', r[6][:12])

"""C4 延伸：Perf ↔ Perf_Batch（頁首聲明「與 Perf 同一套公式」）逐格結構比對；
Sens_Perf／Sens_Train 情境格是否上黃底；Sensitivity／Sens_Rev 藍字情境格是否上黃底。
用法：python3 08_c4_extra.py <wb.pkl> <out.pkl>"""
import pickle, sys, re, collections
from openpyxl.formula import Tokenizer
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']; names = d['names']
lname = {n.lower(): t for n, t in names.items() if ',' not in t}
def isf(x): return isinstance(x['f'], str) and x['f'].startswith('=')
def r1c1(formula, own, r0, c0):
    try: toks = Tokenizer(formula).items
    except Exception: return formula
    out = []
    for t in toks:
        val = t.value
        if t.type == 'OPERAND' and t.subtype == 'RANGE' and val.lower() in lname: val = lname[val.lower()]
        if t.type == 'OPERAND' and t.subtype == 'RANGE':
            sh = None; ref = val
            if '!' in ref: sh, ref = ref.rsplit('!', 1); sh = sh.strip("'")
            if sh == own: sh = None
            parts = []
            for p in ref.split(':'):
                m = re.fullmatch(r'(\$?)([A-Z]{1,3})?(\$?)(\d+)?', p)
                if not m: parts.append(p); continue
                ca, col, ra, row = m.groups(); s_ = ''
                if row: s_ += f'R{row}' if ra else f'R[{int(row)-r0}]'
                if col: s_ += f'C{CI(col)}' if ca else f'C[{CI(col)-c0}]'
                parts.append(s_)
            out.append((sh + '!' if sh else '') + ':'.join(parts))
        elif t.type == 'FUNC': out.append(t.value.upper())
        else: out.append(val)
    return ''.join(out)
res = dict(pb=[], scen=[])
# Perf ↔ Perf_Batch：C:Q 同格比對
cnt = collections.Counter()
for (s, a), x in sorted(cells.items(), key=lambda z: (z[1]['r'], z[1]['c'])):
    if s != 'Perf_Batch' or not isf(x) or x['c'] < 3 or x['c'] > 17 or x['r'] < 8: continue
    p = cells.get(('Perf', a))
    lab_b = cells.get(('Perf_Batch', f'A{x["r"]}')); lab_p = cells.get(('Perf', f'A{x["r"]}'))
    if p is None or not isf(p):
        cnt['Perf 同格非公式'] += 1
        res['pb'].append(dict(cell=a, row=x['r'], label=str(lab_b['v'])[:40] if lab_b else '', kind='Perf 同格非公式或空白', pb=x['f'][:200], pf=str(p['f'] if p else '')[:200])); continue
    if lab_b and lab_p and lab_b['v'] != lab_p['v']:
        cnt['列標籤不同'] += 1
    a1, b1 = r1c1(x['f'], 'Perf_Batch', x['r'], x['c']), r1c1(p['f'], 'Perf', p['r'], p['c'])
    if a1 == b1: cnt['結構相同'] += 1
    else:
        cnt['結構不同'] += 1
        res['pb'].append(dict(cell=a, row=x['r'], label=str(lab_b['v'])[:40] if lab_b else '', kind='結構不同', pb=x['f'][:200], pf=p['f'][:200]))
print('Perf_Batch ↔ Perf', dict(cnt))
rowdiff = collections.Counter(z['row'] for z in res['pb'])
print('結構不同的列', sorted(rowdiff.items()))
# 情境格上黃底
YEL = ('FFFFF2CC', 'FFFFFF00')
for sp in ('Sens_Perf', 'Sens_Train', 'Sensitivity', 'Sens_Rev', 'Sens_Har'):
    for (s, a), x in cells.items():
        if s != sp: continue
        if x['color'] == 'FF0000FF' and x['fill'] not in YEL and not (isinstance(x['f'], str) and not isinstance(x['f'], (int, float)) and not isf(x) and len(str(x['f'])) > 0 and x['r'] in (6, 7) and sp in ('Sens_Perf', 'Sens_Train')):
            res['scen'].append(dict(sheet=sp, cell=a, row=x['r'], label=str((cells.get((sp, f'A{x["r"]}')) or {}).get('v') or '')[:50], value=x['f'], note='藍字輸入未上黃底'))
print('藍字未黃底', collections.Counter(z['sheet'] for z in res['scen']))
pickle.dump(res, open(sys.argv[2], 'wb'))

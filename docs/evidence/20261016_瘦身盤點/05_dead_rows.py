"""死格彙總成「列」。用法：python3 05_dead_rows.py <wb.pkl> <a.pkl> <old.pkl> <out.pkl>
每列一筆：頁、列、標籤、死格數、欄、種類、同列是否有核心格、與 v5.36 比對狀態、Gov_Map 登錄。"""
import pickle, collections, re, sys
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI
d = pickle.load(open(sys.argv[1], 'rb')); a = pickle.load(open(sys.argv[2], 'rb')); o = pickle.load(open(sys.argv[3], 'rb'))
cells = d['cells']
dead = a['dead']
oldl = o['oldl']; old = o['old']
oldcells = {(r[0], r[1]) for r in old}
def colof(c): return re.match(r'[A-Z]+', c).group()
rows = collections.OrderedDict()
for z in dead:
    rows.setdefault((z['sheet'], z['row']), []).append(z)
# Gov_Map 登錄（輸入格）
gmcells = {}
for g in a.get('gm_list', []): pass
res = []
for (s, r), zs in rows.items():
    cols = sorted({colof(z['cell']) for z in zs}, key=CI)
    nform = sum(1 for z in zs if z['kind'] == '公式'); nin = len(zs) - nform
    lab = zs[0]['label']
    newcols = [c for c in cols if (s, str(lab).strip(), c) not in oldl]
    status = '新增（v5.36 無對應死格）' if len(newcols) == len(cols) else ('部分新增：' + '、'.join(newcols) if newcols else '沿用（v5.36 已是死格）')
    kinds = collections.Counter(z['kind'] for z in zs)
    ex = zs[0]
    res.append(dict(sheet=s, row=r, label=lab, n=len(zs), nform=nform, nin=nin, cols=cols, kinds=dict(kinds),
                    row_has_core=ex['row_has_core'][0] == '是', status=status, formula=ex['formula'], value=ex['value'],
                    users=ex['users'], users_union=sorted({u for z in zs for u in z['users'].split('、')}), via_gov=sum(1 for z in zs if z['reach_via_gov'] == '是'),
                    cellrefs=[z['cell'] for z in zs]))
print('dead rows', len(res), 'whole-row dead', sum(1 for x in res if not x['row_has_core']), 'partial', sum(1 for x in res if x['row_has_core']))
print('新增', sum(1 for x in res if x['status'].startswith('新增')), '部分新增', sum(1 for x in res if x['status'].startswith('部分')))
# 與 v5.36 逐格：舊死格現況
gone = []
for r in old:
    k = (r[0], r[1])
    cur = cells.get(k)
    if k in {(z['sheet'], z['cell']) for z in dead}: continue
    gone.append(dict(sheet=r[0], cell=r[1], row=r[2], label=r[3], kind=r[4], status='現為核心格（已接上下游）' if cur else '該格現為空白（已刪除或搬移）', cur=(cur or {}).get('v') if cur else None))
print('舊死格已不再是死格', len(gone), collections.Counter(g['status'] for g in gone), collections.Counter(g['sheet'] for g in gone))
pickle.dump(dict(rows=res, gone=gone), open(sys.argv[4], 'wb'))

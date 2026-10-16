"""治理頁盤點。用法：python3 11_govmap.py <wb.pkl> <a.pkl> <out.pkl>
G1 Gov_Map 指向公式格但狀態不是連結／公式、標籤與目標列不符、同格多登錄（取自 C1.1f/g/h）
G2 藍字數值輸入未登錄（C1.1）；藍字文字未登錄（C1.1b，分頁計數）
G3 SRC_ID 與決策 ID 皆為「—」（C1.2）依頁／類別，並與 v5.36 的 311 比較
G4 決策 ID 在 Decisions 頁不存在；SRC_ID 在 SRC 頁不存在
G5 輸入格無人引用（C1.6）依頁"""
import pickle, sys, re, collections
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']
a = pickle.load(open(sys.argv[2], 'rb')); c1 = a['c1']
res = dict(g1=[], g2=[], g3=[], g4=[], g5=[])
for z in c1:
    it = z['item']
    if it.startswith(('C1.1f', 'C1.1g', 'C1.1h')): res['g1'].append(z)
    elif it.startswith('C1.1 ') or it.startswith('C1.1b'): res['g2'].append(z)
    elif it.startswith('C1.2 '): res['g3'].append(z)
    elif it.startswith('C1.6'): res['g5'].append(z)
# G4
dec_ids = set()
for (s, ad), x in cells.items():
    if s == 'Decisions' and x['c'] == 1 and isinstance(x['v'], str): dec_ids.add(x['v'].strip())
src_ids = set()
for (s, ad), x in cells.items():
    if s.startswith('SRC_') and s != 'SRC_Index' and x['c'] == 1 and isinstance(x['v'], str) and re.fullmatch(r'SRC_[A-Z]+_\d+', x['v']): src_ids.add(x['v'])
miss = []
for r in range(5, 1200):
    gid = (cells.get(('Gov_Map', f'A{r}')) or {}).get('v')
    if not (isinstance(gid, str) and gid.startswith('GM')): continue
    dec = (cells.get(('Gov_Map', f'J{r}')) or {}).get('v'); src = (cells.get(('Gov_Map', f'H{r}')) or {}).get('v')
    for t in re.findall(r'\b[A-Z]{1,2}\d{1,2}[a-z]?\b', str(dec or '')):
        if t not in dec_ids and re.fullmatch(r'D\d+[a-z]?', t): miss.append(dict(gm=gid, row=r, kind='決策 ID', id=t))
    for t in re.findall(r'SRC_[A-Z]+_\d+', str(src or '')):
        if t not in src_ids: miss.append(dict(gm=gid, row=r, kind='SRC_ID', id=t))
res['g4'] = miss
print('Decisions IDs', len(dec_ids), list(sorted(dec_ids))[:8])
print('G1', len(res['g1']), collections.Counter(z['item'][:6] for z in res['g1']))
print('G2', collections.Counter(z['item'][:6] for z in res['g2']), collections.Counter(z['sheet'] for z in res['g2'] if z['item'].startswith('C1.1 ')))
print('G3', len(res['g3']), collections.Counter(z['sheet'] for z in res['g3']).most_common(8))
print('G4', len(miss), miss[:8])
print('G5', len(res['g5']), collections.Counter(z['sheet'] for z in res['g5']))
pickle.dump(res, open(sys.argv[3], 'wb'))

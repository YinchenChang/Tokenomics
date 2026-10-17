"""重複定義的機械掃描（候選清單，之後人工歸類）。用法：python3 07_dups_scan.py <wb.pkl> <out.pkl>
S1 同一目標多個具名範圍（別名）
S2 純連結列：整列公式都是 =其他頁!同欄同列 或 =名稱（內容只是搬運）
S3 同頁（或跨頁）不同列但「公式的 R1C1 形式與值」完全相同的整列
S4 標籤相同或相近（去括號後）的列出現在 ≥2 頁"""
import pickle, sys, re, collections
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']; names = d['names']
SKIP = {'Gov_Map', 'Decisions', 'DB_Evidence', 'Load_Bearing', 'SRC_Index', 'README', 'Sources_Legacy', 'Checks'}
SKIP |= {s for s, _, _ in d['sheets'] if s.startswith('SRC_') or s.startswith('Sens_') or s == 'Sensitivity' or s.endswith('_Prod')}
# S1
tgt = collections.defaultdict(list)
for n, t in names.items():
    if '!' in n: continue
    tgt[t.replace('$', '')].append(n)
s1 = [(t, ns) for t, ns in tgt.items() if len(ns) > 1]
print('S1 同目標多名稱', len(s1))
# S4 標籤
def norm(t):
    t = re.sub(r'（[^）]*）|\([^)]*\)', '', str(t)); return re.sub(r'[\s—–\-：:；;、，,｜|]+', '', t)
lab = collections.defaultdict(list)
for (s, a), x in cells.items():
    if s in SKIP or x['c'] != 1 or not isinstance(x['v'], str): continue
    if len(x['v']) < 6: continue
    lab[norm(x['v'])].append((s, x['r'], x['v']))
s4 = [(k, v) for k, v in lab.items() if len({z[0] for z in v}) > 1 or len(v) > 1]
print('S4 同標籤多列', len(s4))
# S3 同頁同公式 R1C1-ish：以去除列號後的公式文字比較（簡化）
def sig(s, r):
    parts = []
    for c in range(3, 8):
        x = cells.get((s, f'{chr(64+c)}{r}'))
        if x is None: continue
        f = x['f']
        parts.append(re.sub(r'\$?[A-Z]{1,2}\$?\d+', 'X', f) if isinstance(f, str) and f.startswith('=') else repr(f))
    return '|'.join(parts)
sigs = collections.defaultdict(list)
for (s, a), x in cells.items():
    if s in SKIP or x['c'] != 3 or x['r'] < 8: continue
    if isinstance(x['f'], str) and x['f'].startswith('=') and len(x['f']) > 25:
        sigs[(s, x['f'])].append(x['r'])
s3 = [(k, v) for k, v in sigs.items() if len(v) > 1]
print('S3 同頁 C 欄完全相同的長公式', len(s3))
pickle.dump(dict(s1=s1, s4=s4, s3=s3), open(sys.argv[2], 'wb'))
for t, ns in s1[:60]: print('S1', t, ns)
for k, v in s3[:40]: print('S3', k[0], v, k[1][:80])

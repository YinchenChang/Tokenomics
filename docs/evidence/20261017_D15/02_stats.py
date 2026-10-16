"""D15 第 2 步：以 v12.0 重新統計（無來源也無決策的 Gov_Map 列、49 格、證據積壓、缺第二來源的新 SRC）。
用法：python3 02_stats.py   （讀 01_load.pkl，寫 02_stats.pkl）"""
import pickle, os, re, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
d = pickle.load(open(os.path.join(HERE, '01_load.pkl'), 'rb'))
TODAY = datetime.date(2026, 10, 17)

def blank(x): return x is None or str(x).strip() in ('', '—', '-', '–')

# ---------- G3：無來源也無決策 ----------
H = d['gm_hdr']; ix = {h: i for i, h in enumerate(H)}
def g(row, name): return row[ix[name]]
SRC_COL = 'SRC_ID（來源或可比對象）'
g3 = [r for r in d['gm'] if blank(g(r, SRC_COL)) and blank(g(r, '決策 ID'))]
print('Gov_Map 列', len(d['gm']), '；G3 無來源也無決策', len(g3))
print(' 依頁', collections.Counter(g(r, '工作表') for r in g3).most_common())
print(' 依類別', collections.Counter(g(r, '類別') for r in g3).most_common())
print(' 依敏感度分段', collections.Counter(g(r, 'CC 敏感度分段') for r in g3).most_common())
lb_ids = {r[0] for r in d['lb']}
print(' 其中 Load_Bearing', sum(1 for r in g3 if r[0] in lb_ids))

# ---------- 49 格（v5.36 稽核第 1 段：m 路徑＋高嚴重度＋SRC 與決策皆無） ----------
A = d['a1_hdr']; ia = {h: i for i, h in enumerate(A)}
def a(row, name): return row[ia[name]]
c49 = [r for r in d['a1_rows'] if a(r, '是否在 m 路徑') == '是' and a(r, '嚴重度') == '高'
       and blank(a(r, 'SRC_ID')) and blank(a(r, '決策 ID'))]
print('49 格重現：', len(c49))
print(' 依頁', collections.Counter(a(r, '頁') for r in c49).most_common())
gm_by_id = {r[0]: r for r in d['gm']}
still = []
for r in c49:
    ids = re.findall(r'GM\d+', str(a(r, 'GM_ID')))
    st = []
    for i in ids:
        x = gm_by_id.get(i)
        if x is None: st.append((i, '不存在')); continue
        st.append((i, 'G3' if (blank(g(x, SRC_COL)) and blank(g(x, '決策 ID'))) else f"已有 SRC={g(x, SRC_COL)} 決策={g(x, '決策 ID')}"))
    still.append((r, st))
n_still = sum(1 for r, st in still if all(s[1] == 'G3' for s in st))
print(' v12.0 仍屬 G3', n_still, '；已補', len(c49) - n_still)
for r, st in still:
    if not all(s[1] == 'G3' for s in st): print('   已補', a(r, '頁'), a(r, '格'), st)

# ---------- 證據積壓（稽核第 0 段 C2 規則） ----------
def _eom(y, m):
    return (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1))
def parse_date(t):
    if t is None: return None
    if isinstance(t, datetime.datetime): return t.date()
    if isinstance(t, datetime.date): return t
    t = str(t).strip()
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', t)
    if m: return datetime.date(*map(int, m.groups()))
    m = re.search(r'(\d{4})-(\d{2})／(\d{2})', t)
    if m: y, _, mo = map(int, m.groups()); return _eom(y, mo)
    m = re.search(r'(\d{4})-(\d{2})', t)
    if m: return _eom(int(m.group(1)), int(m.group(2)))
    m = re.search(r'(\d{4})\s*Q([1-4])', t)
    if m: return _eom(int(m.group(1)), int(m.group(2)) * 3)
    m = re.search(r'(\d{4})[–-](\d{2})\b', t)
    m = re.search(r'\b(20\d{2})\b', t)
    if m: return datetime.date(int(m.group(1)), 12, 31)
    return None
src_date = {}
for i, s in d['src'].items():
    hdr = d['src_hdr'][s['sheet']]
    src_date[i] = (parse_date(s['vals'][hdr.index('日期')]), s['vals'][hdr.index('日期')])
backlog = []
for r in d['ev']:
    eid, date, claim, srcs, tag, param, cur, new, jd, ver, note, st, rel, rep, aff, grade, stance, rown = r
    ed = parse_date(date); st = str(st or ''); jd = str(jd or '')
    reasons = []
    if '待判定' in st or '待 Andy' in st or '待Andy' in st: reasons.append(f'狀態：{st}')
    if '待查' in jd: reasons.append('判定：待查')
    later = []
    for sid in re.findall(r'SRC_[A-Z]+_\d+', str(rel or '')):
        sd = src_date.get(sid, (None, None))
        if sd[0] and ed and ed > sd[0] and not jd.startswith(('採納', '採用')):
            later.append(f'{sid}（{sd[1]}）')
    if later: reasons.append('晚於相關 SRC 文件日期且判定非採納：' + '、'.join(later[:4]) + (f' 等 {len(later)} 筆' if len(later) > 4 else ''))
    if reasons: backlog.append(dict(row=r, reasons=reasons, later=later))
print('DB_Evidence 列', len(d['ev']), '；積壓', len(backlog))
cat = collections.Counter()
for b in backlog:
    k = []
    if any(x.startswith('狀態') for x in b['reasons']): k.append('待判定')
    if '判定：待查' in b['reasons']: k.append('待查')
    if b['later']: k.append('晚於SRC')
    cat['＋'.join(k)] += 1
print(' 類別', cat.most_common())
print(' 判定分布', collections.Counter(str(b['row'][8])[:12] for b in backlog).most_common(20))
print(' 狀態分布', collections.Counter(str(b['row'][11]) for b in backlog).most_common())

# ---------- 缺第二來源的利害關係方 SRC ----------
miss2 = []
for i, s in d['src'].items():
    hdr = d['src_hdr'][s['sheet']]; v = dict(zip(hdr, s['vals']))
    if str(v.get('狀態')) == 'Active' and '利害' in str(v.get('立場')) and blank(v.get('第二來源 SRC_ID')):
        miss2.append((i, v.get('指標'), v.get('數值'), v.get('單位'), v.get('日期'), v.get('Evidence ID'), v.get('審查日')))
print('利害關係方 Active 無第二來源', len(miss2))
recent = [m for m in miss2 if str(m[4]).startswith('2026-10') or str(m[6]).startswith('2026-10-1')]
for m in sorted(recent, key=lambda z: str(z[0])): print('  ', m)

pickle.dump(dict(g3=g3, c49=c49, still=still, backlog=backlog, miss2=miss2, src_date=src_date), open(os.path.join(HERE, '02_stats.pkl'), 'wb'))

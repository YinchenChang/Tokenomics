"""過時或錯誤的標籤與說明。用法：python3 10_labels.py <wb.pkl> <out.pkl>
規則 S1：文字中引用的具名範圍／SRC ID 不存在
規則 S2：文字宣稱的數字（約 N、≈N、＝N、N%、N×）與同列數值（C:Q 欄）相差 >20%
規則 S3：文字「第 N 列」「H5 第 94 列」之類的列參照，列出目標列標籤供人工核對
只掃模型頁（不含 SRC_*、DB_Evidence、Decisions、Sources_Legacy、README 的歷史記錄）。"""
import pickle, sys, re, collections
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']; names = d['names']
sheets = [s for s, _, _ in d['sheets']]
SKIP = {'Decisions', 'DB_Evidence', 'Sources_Legacy', 'Load_Bearing', 'SRC_Index'} | {s for s in sheets if s.startswith('SRC_')}
lname = set(names)
srcids = set()
for (s, a), x in cells.items():
    if s.startswith('SRC_') and s != 'SRC_Index' and x['c'] == 1 and isinstance(x['v'], str) and re.fullmatch(r'SRC_[A-Z]+_\d+', x['v']): srcids.add(x['v'])
nameset = set(names) | set(srcids)
# 具名範圍的後綴（_Lo/_Hi 等）容許
def known(tok):
    if tok in nameset: return True
    for suf in ('_Lo', '_Hi', '_Id', '_Tok'):
        if tok.endswith(suf) and tok[:-len(suf)] in nameset: return True
    return False
TOK = re.compile(r'(?<![A-Za-z0-9_])((?:IF|IFW|IFC|L1|AL|B4|B5|CAP|CTL|CHK|GOV|CST|ARCH|DRV|CAL|SRC)_[A-Za-z0-9_]+)')
s1 = []; s2 = []; s3 = []
def rowvals(s, r):
    vals = []
    for c in range(3, 18):
        x = cells.get((s, f'{chr(64+c) if c<27 else "A"+chr(64+c-26)}{r}'))
        if x and isinstance(x['v'], (int, float)) and not isinstance(x['v'], bool): vals.append(x['v'])
    return vals
NUMCLAIM = re.compile(r'(約|≈|大約|約為|＝|=|設為|預設)\s*([0-9]+(?:\.[0-9]+)?)\s*(%|倍|×|x|X|個月|月|年|天|GW|MW|B|M)?')
for (s, a), x in cells.items():
    if s in SKIP or not isinstance(x['v'], str) or (isinstance(x['f'], str) and x['f'].startswith('=') and False): continue
    t = x['v']
    # S1
    for tok in set(TOK.findall(t)):
        if tok.endswith('_') or tok.endswith('*') or len(tok) < 6: continue
        if not known(tok) and not re.search(re.escape(tok) + r'\*', t):
            s1.append(dict(sheet=s, cell=a, row=x['r'], text=t[:160], tok=tok))
    # S2：只看標籤／說明欄（A、B 欄與文字格），同列有數值
    if x['c'] <= 2 or x['c'] >= 18:
        vals = rowvals(s, x['r'])
        if not vals: continue
        for m in NUMCLAIM.finditer(t):
            n = float(m.group(2)); unit = m.group(3) or ''
            if n in (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 100) and not unit: continue   # 常見序號或索引
            cand = [n, n / 100 if unit == '%' else n]
            ok = any(v != 0 and any(abs(v / cv - 1) <= 0.2 for cv in cand if cv) for v in vals) or any(abs(v - n) < 1e-9 for v in vals)
            if not ok:
                s2.append(dict(sheet=s, cell=a, row=x['r'], text=t[:200], claim=m.group(0), vals=[round(v, 4) for v in vals[:4]]))
    # S3
    for m in re.finditer(r'(?:(?:Cap_In|Alloc|L1|Training|Perf|Interface|Theory_Rev|Amortize|Fleet_1GW|Harness|Calib)\s*)?(?:[A-Z]\d?\s*節\s*)?第\s*(\d+)\s*列', t):
        tgt = m.group(0)
        sh = re.match(r'(Cap_In|Alloc|L1|Training|Perf|Interface|Theory_Rev|Amortize|Fleet_1GW|Harness|Calib)', tgt)
        sh = sh.group(1) if sh else s
        r = int(m.group(1))
        lab = (cells.get((sh, f'A{r}')) or cells.get((sh, f'B{r}')) or {}).get('v')
        s3.append(dict(sheet=s, cell=a, row=x['r'], text=t[:160], ref=tgt, tsheet=sh, trow=r, tlabel=str(lab)[:80] if lab is not None else '（空白）'))
print('S1', len(s1), collections.Counter(z['sheet'] for z in s1))
print('S2', len(s2), collections.Counter(z['sheet'] for z in s2))
print('S3', len(s3), sum(1 for z in s3 if z['tlabel'] == '（空白）'))
pickle.dump(dict(s1=s1, s2=s2, s3=s3), open(sys.argv[2], 'wb'))

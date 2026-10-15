"""稽核第 0 段：C1–C7 機械檢查與瘦身盤點。
用法：python3 02_audit.py <wb.pkl> <graph.pkl> <out.pkl>
只讀 00_load.py / 01_graph.py 的輸出；不讀也不寫 model/。"""
import pickle, sys, re, collections, datetime, math
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter as L, column_index_from_string as CI

d = pickle.load(open(sys.argv[1], 'rb')); G = pickle.load(open(sys.argv[2], 'rb'))
cells = d['cells']; names = d['names']; edges = G['edges']
SHEETS = [s for s, _, _ in d['sheets']]
TODAY = datetime.date(2026, 10, 15)

def v(s, a): return (cells.get((s, a)) or {}).get('v')
def f(s, a): return (cells.get((s, a)) or {}).get('f')
def isformula(x): return isinstance(x['f'], str) and x['f'].startswith('=')
def isnum(x): return isinstance(x, (int, float)) and not isinstance(x, bool)

SRC_PAGES = [s for s in SHEETS if s.startswith('SRC_') and s != 'SRC_Index']
GOV_PAGES = {'Gov_Map', 'Decisions', 'DB_Evidence', 'Checks', 'Load_Bearing', *SRC_PAGES}
META_PAGES = {'README', 'Sources_Legacy'}
SENS_PAGES = {s for s in SHEETS if s.startswith('Sens_') or s == 'Sensitivity'}
MIRROR_PAGES = {s for s in SHEETS if s.endswith('_Prod')}
# 依賴追溯時不穿越的治理頁（避免 Gov_Map 的 Q 欄「模型值」把每格輸入都接到 GOV_*）
NO_TRAVERSE = {'Gov_Map', 'Decisions', 'DB_Evidence', 'Load_Bearing', 'SRC_Index'}
MODEL_PAGES = [s for s in SHEETS if s not in GOV_PAGES | META_PAGES | {'SRC_Index'}]

def page_class(s):
    if s in SENS_PAGES: return '敏感度'
    if s in MIRROR_PAGES: return '鏡像'
    if s in GOV_PAGES or s == 'SRC_Index': return '治理與來源'
    if s in META_PAGES: return '說明'
    return None

# ---------- 列標籤 ----------
def row_label(s, r):
    for col in ('A', 'B'):
        x = v(s, f'{col}{r}')
        if isinstance(x, str) and x.strip(): return x.strip()
    x = f(s, f'A{r}')
    return str(x) if x is not None else ''

# ---------- 輸入格定義 ----------
inputs = {}   # (s,a) -> kind
for (s, a), x in cells.items():
    if s not in MODEL_PAGES or isformula(x): continue
    if isnum(x['f']):
        inputs[(s, a)] = '藍字數值' if x['color'] == 'FF0000FF' else '非藍字數值常數'
    elif isinstance(x['f'], str) and x['color'] == 'FF0000FF':
        inputs[(s, a)] = '藍字文字'

# ---------- 反向圖（直接引用） ----------
rev = collections.defaultdict(set)
for n, ps in edges.items():
    for p in ps: rev[p].add(n)
def direct_users(node, seen=None):
    """回傳直接引用此格的公式格（穿過具名範圍與範圍節點，但不穿過其他公式格）。"""
    out = set(); stack = [node]; seen = set()
    while stack:
        cur = stack.pop()
        for u in rev.get(cur, ()):
            if u in seen: continue
            seen.add(u)
            if u[0] in ('NAME', 'RANGE'): stack.append(u)
            else: out.add(u)
    return out

REGISTRY = {'Gov_Map', 'Decisions', 'DB_Evidence', 'Load_Bearing', 'SRC_Index'}
# ---------- 上游追溯 ----------
def upstream(roots, stop_gov=True):
    seen = set(); stack = list(roots)
    while stack:
        n = stack.pop()
        if n in seen: continue
        seen.add(n)
        if stop_gov and n[0] not in ('NAME', 'RANGE') and n[0] in NO_TRAVERSE and n not in roots_set_cells:
            continue
        for p in edges.get(n, ()):
            if p not in seen: stack.append(p)
    return seen

# ---------- 根節點 ----------
contract_txt = open('docs/plan/Tokenomics_downstream_contract.md', encoding='utf-8').read()
contract_tokens = set(re.findall(r'\b[A-Z][A-Za-z0-9]*_[A-Za-z0-9_\*]+', contract_txt))
root_names = set()
contract_named = []
for t in sorted(contract_tokens):
    pat = '^' + re.escape(t).replace(r'\*', '.*') + '$'
    hits = [n for n in names if re.match(pat, n)]
    contract_named.append((t, len(hits)))
    root_names.update(hits)
root_names.update(n for n in names if n.startswith(('IF_', 'L1_', 'GOV_', 'IFW_', 'IFC_')))
root_cells = [k for k in cells if k[0] == 'Checks']
roots = [('NAME', n) for n in root_names] + root_cells
roots_set_cells = set(root_cells)
reach = upstream(roots, True)
reach_all = upstream(roots, False)   # 穿越治理頁的寬鬆版本（對照）

# ---------- C3 分類 ----------
cls = {}
for (s, a), x in cells.items():
    is_f = isformula(x)
    if not is_f and (s, a) not in inputs and not isnum(x['f']): continue   # 純標籤文字
    pc = page_class(s)
    if pc == '說明': continue
    if pc: cls[(s, a)] = pc
    elif (s, a) in reach: cls[(s, a)] = '核心'
    else: cls[(s, a)] = '死格'
c3_page = collections.defaultdict(collections.Counter)
for (s, a), c in cls.items():
    c3_page[s][c] += 1
    c3_page[s]['公式格' if isformula(cells[(s, a)]) else '輸入或常數'] += 1
def _user_kind(k):
    us = direct_users(k)
    if not us: return '無任何格引用'
    kinds = sorted({page_class(u[0]) or ('死格' if cls.get(u) == '死格' else '核心') for u in us})
    return '、'.join(kinds)
dead = []
for (s, a), c in cls.items():
    if c != '死格': continue
    x = cells[(s, a)]
    dead.append(dict(sheet=s, cell=a, row=x['r'], label=row_label(s, x['r']), kind='公式' if isformula(x) else inputs.get((s, a), '常數'),
                     formula=str(x['f'])[:300], value=x['v'], reach_via_gov=('是' if (s, a) in reach_all else '否'),
                     users=_user_kind((s, a))))
dead.sort(key=lambda r: (SHEETS.index(r['sheet']), r['row'], CI(re.match(r'[A-Z]+', r['cell']).group())))
# 鏡像／敏感度頁內：是否被任何根追到（資訊用）
side_unreached = collections.Counter((s) for (s, a), c in cls.items() if c in ('鏡像', '敏感度') and (s, a) not in reach)
core_rows = collections.defaultdict(lambda: collections.Counter())
for (s, a), c in cls.items():
    if c == '核心': core_rows[(s, cells[(s, a)]['r'])]['f' if isformula(cells[(s, a)]) else 'i'] += 1
core_row_list = [dict(sheet=s, row=r, label=row_label(s, r), formulas=cn['f'], inputs=cn['i']) for (s, r), cn in core_rows.items()]
core_row_list.sort(key=lambda z: (SHEETS.index(z['sheet']), z['row']))
nform = sum(1 for x in cells.values() if isformula(x))
slim = collections.Counter()
for (s, a), c in cls.items():
    if isformula(cells[(s, a)]): slim[c] += 1

# ---------- 日期解析 ----------
def parse_date(t):
    """回傳 (最晚可能日期, 粒度)；無日期回傳 (None, '無')。"""
    if t is None: return None, '無'
    if isinstance(t, datetime.datetime): return t.date(), '日'
    if isinstance(t, datetime.date): return t, '日'
    t = str(t).strip()
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', t)
    if m: return datetime.date(*map(int, m.groups())), '日'
    m = re.search(r'(\d{4})-(\d{2})／(\d{2})', t)
    if m:
        y, _, mo = map(int, m.groups()); return _eom(y, mo), '月'
    m = re.search(r'(\d{4})-(\d{2})', t)
    if m: return _eom(int(m.group(1)), int(m.group(2))), '月'
    m = re.search(r'(\d{4})[–-](\d{2})\b', t)
    if m: return datetime.date(2000 + int(m.group(2)), 12, 31), '年（區間）'
    m = re.search(r'(\d{4})', t)
    if m: return datetime.date(int(m.group(1)), 12, 31), '年'
    return None, '無'
def _eom(y, mo):
    nxt = datetime.date(y + (mo == 12), mo % 12 + 1, 1); return nxt - datetime.timedelta(days=1)

# ---------- SRC 表 ----------
src = {}
for s in SRC_PAGES:
    for r in range(5, 400):
        i = v(s, f'A{r}')
        if not (isinstance(i, str) and i.startswith('SRC_')): continue
        dt, gran = parse_date(v(s, f'I{r}'))
        src[i] = dict(sheet=s, row=r, metric=v(s, f'B{r}'), value=v(s, f'C{r}'), unit=v(s, f'F{r}'), date_raw=v(s, f'I{r}'),
                      date=dt, gran=gran, status=v(s, f'O{r}'), grade=v(s, f'K{r}'), review=v(s, f'S{r}'), replaced=v(s, f'P{r}'))
def src_ids(t):
    return re.findall(r'SRC_[A-Z]+_\d+', str(t or ''))

# ---------- Gov_Map ----------
gm = []
for r in range(5, 1000):
    gid = v('Gov_Map', f'A{r}')
    if not (isinstance(gid, str) and gid.startswith('GM')): continue
    gm.append(dict(row=r, id=gid, slice=v('Gov_Map', f'B{r}'), sheet=v('Gov_Map', f'C{r}'), ref=v('Gov_Map', f'D{r}'), label=v('Gov_Map', f'E{r}'),
                   cat=v('Gov_Map', f'F{r}'), role=v('Gov_Map', f'G{r}'), src=v('Gov_Map', f'H{r}'), rel=v('Gov_Map', f'I{r}'), dec=v('Gov_Map', f'J{r}'),
                   lo=v('Gov_Map', f'K{r}'), hi=v('Gov_Map', f'L{r}'), rng=v('Gov_Map', f'M{r}'), seg=v('Gov_Map', f'P{r}'), q=v('Gov_Map', f'Q{r}'),
                   actual=v('Gov_Map', f'U{r}')))
def expand_ref(s, ref):
    try: c1, r1, c2, r2 = range_boundaries(ref)
    except Exception: return []
    return [(s, f'{L(c)}{rr}') for rr in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
gm_cells = collections.defaultdict(list)
for g in gm:
    g['cells'] = expand_ref(g['sheet'], str(g['ref']))
    for k in g['cells']: gm_cells[k].append(g['id'])

def blank(x): return x is None or (isinstance(x, str) and x.strip() in ('', '—'))

# ---------- 標記欄（模型頁） ----------
def header_col(s, r, words):
    """在 r 以上最近的表頭列中找含 words 的欄。"""
    for rr in range(r, 0, -1):
        for (ss, a), x in [((s, f'{L(c)}{rr}'), cells.get((s, f'{L(c)}{rr}'))) for c in range(1, 40)]:
            if x and isinstance(x['v'], str) and any(x['v'].strip() == w or x['v'].strip().startswith(w) for w in words):
                return x['c'], rr
    return None, None
_hc = {}
def tag_of(s, r):
    k = (s, r, 'tag')
    if k not in _hc: _hc[k] = header_col(s, r, ['標記'])
    c, _ = _hc[k]
    return v(s, f'{L(c)}{r}') if c else None
def unit_of(s, r):
    k = (s, r, 'unit')
    if k not in _hc: _hc[k] = header_col(s, r, ['單位'])
    c, hr = _hc[k]
    return (v(s, f'{L(c)}{r}') if c else None), (c is not None)

# ================= C1 =================
c1 = []
def add1(item, sev, s, a, gid, label, detail):
    c1.append(dict(item=item, sev=sev, sheet=s, cell=a, gm=gid, label=label, detail=detail))
# 1a 輸入格未登錄
for (s, a), k in sorted(inputs.items(), key=lambda z: (SHEETS.index(z[0][0]), cells[z[0]]['r'], cells[z[0]]['c'])):
    if (s, a) in gm_cells: continue
    if k == '藍字數值': add1('C1.1 藍字數值輸入未登錄 Gov_Map', '高', s, a, '', row_label(s, cells[(s, a)]['r']), f"值 {cells[(s,a)]['f']}")
    elif k == '藍字文字': add1('C1.1b 藍字文字輸入未登錄 Gov_Map', '低', s, a, '', row_label(s, cells[(s, a)]['r']), f"值 {str(cells[(s,a)]['f'])[:60]}")
    else: add1('C1.1c 非藍字數值常數（未標示為輸入，未登錄）', '低' if '索引' in row_label(s, cells[(s, a)]['r']) else '中', s, a, '', row_label(s, cells[(s, a)]['r']), f"值 {cells[(s,a)]['f']}；字色 {cells[(s,a)]['color']}")
# 1b Gov_Map 指向
gm_target_kind = {}
for g in gm:
    kinds = collections.Counter()
    for k in g['cells']:
        x = cells.get(k)
        if x is None: kinds['空白'] += 1
        elif isformula(x): kinds['公式'] += 1
        elif k in inputs: kinds[inputs[k]] += 1
        else: kinds['其他常數或文字'] += 1
    gm_target_kind[g['id']] = kinds
    if g['sheet'] not in SHEETS:
        add1('C1.1d Gov_Map 指向不存在的工作表', '高', g['sheet'], g['ref'], g['id'], g['label'], '')
        continue
    if not g['cells']:
        add1('C1.1d Gov_Map 格位址無法解析', '高', g['sheet'], g['ref'], g['id'], g['label'], '')
        continue
    if kinds.get('空白', 0) == len(g['cells']):
        add1('C1.1e Gov_Map 指向空白格', '高', g['sheet'], g['ref'], g['id'], g['label'], '')
    elif kinds.get('空白', 0):
        add1('C1.1e Gov_Map 範圍內含空白格', '低', g['sheet'], g['ref'], g['id'], g['label'], dict(kinds).__str__())
    if kinds.get('公式', 0) and not (g['actual'] in ('連結 SRC', '公式') or str(g['cat']).startswith(('Derived', '顯示用'))):
        add1('C1.1f Gov_Map 指向公式格，但「實際狀態」不是連結 SRC／公式', '中', g['sheet'], g['ref'], g['id'], g['label'],
             f"類別 {g['cat']}；實際狀態 {g['actual']}；{dict(kinds)}")
    # 標籤一致性
    r0 = int(re.search(r'\d+', str(g['ref'])).group())
    lab = row_label(g['sheet'], r0)
    if g['label'] and lab and str(g['label'])[:6] not in lab and lab[:6] not in str(g['label']):
        add1('C1.1g Gov_Map 列標籤與目標列標籤不一致（可能錯位）', '中', g['sheet'], g['ref'], g['id'], g['label'], f'目標列標籤：{lab[:80]}')
dups = {k: ids for k, ids in gm_cells.items() if len(set(ids)) > 1}
for k, ids in sorted(dups.items()):
    add1('C1.1h 同一格被多個 GM 列登錄', '低', k[0], k[1], '、'.join(sorted(set(ids))), row_label(k[0], cells.get(k, {'r': 0})['r'] if k in cells else 0), '')
# 2 SRC_ID 與決策 ID
for g in gm:
    if blank(g['src']) and blank(g['dec']):
        sev = '高' if str(g['cat']).startswith(('原始數據', 'Analogy', 'Decision')) else '中'
        add1('C1.2 SRC_ID 與決策 ID 皆為「—」', sev, g['sheet'], g['ref'], g['id'], g['label'], f"類別 {g['cat']}")
    for sid in src_ids(g['src']):
        if sid not in src: add1('C1.2b SRC_ID 在 SRC_* 找不到', '高', g['sheet'], g['ref'], g['id'], g['label'], sid)
        elif src[sid]['status'] != 'Active': add1('C1.2c SRC_ID 非 Active', '中', g['sheet'], g['ref'], g['id'], g['label'], f"{sid} 狀態 {src[sid]['status']}")
# 3 區間與 Verified
for g in gm:
    if g['cat'] in ('Analogy', 'Assumed'):
        if not (isnum(g['lo']) and isnum(g['hi'])):
            has_txt = not blank(g['rng'])
            add1('C1.3 Analogy／Assumed 缺數值低高', '中' if has_txt else '高', g['sheet'], g['ref'], g['id'], g['label'],
                 f"區間角色 {g['role']}；低 {g['lo']}；高 {g['hi']}；區間文字 {g['rng']}")
    if str(g['cat']).startswith('原始數據') and blank(g['src']):
        add1('C1.3b 原始數據（Verified 類）沒有 SRC_ID', '高', g['sheet'], g['ref'], g['id'], g['label'], f"類別 {g['cat']}")
# 模型頁標記欄寫 Verified 但 Gov_Map 無 SRC
for (s, a), k in inputs.items():
    if k != '藍字數值': continue
    t = tag_of(s, cells[(s, a)]['r'])
    if isinstance(t, str) and 'Verified' in t:
        ids = gm_cells.get((s, a), [])
        srcs = [gg['src'] for gg in gm if gg['id'] in ids]
        if not ids or all(blank(x) for x in srcs):
            add1('C1.3c 模型頁標記含 Verified 但無 SRC_ID（藍字常數）', '高', s, a, '、'.join(ids), row_label(s, cells[(s, a)]['r']), f'標記 {t}')
# 4 目前值在區間內
for g in gm:
    if not (isnum(g['lo']) and isnum(g['hi'])): continue
    lo, hi = g['lo'], g['hi']
    if lo > hi: add1('C1.4b 低值大於高值', '高', g['sheet'], g['ref'], g['id'], g['label'], f'低 {lo} 高 {hi}')
    vals = []
    if isnum(g['q']): vals = [(g['ref'], g['q'])]
    else: vals = [(k[1], cells[k]['v']) for k in g['cells'] if k in cells and isnum(cells[k]['v'])]
    for a, val in vals:
        if not (min(lo, hi) - 1e-12 <= val <= max(lo, hi) + 1e-12):
            add1('C1.4 目前值不在低高之間', '高', g['sheet'], a, g['id'], g['label'], f'值 {val}；低 {lo}；高 {hi}')
# 5 來源日期
gm_date = {}
for g in gm:
    ids = src_ids(g['src'])
    if not ids: gm_date[g['id']] = (None, '無 SRC'); continue
    ds = [src[i]['date'] for i in ids if i in src]
    raws = '；'.join(f"{i}:{src[i]['date_raw']}" for i in ids if i in src)
    if not ds or any(x is None for x in ds):
        gm_date[g['id']] = (None, '無日期')
        add1('C1.5c 來源無日期', '中', g['sheet'], g['ref'], g['id'], g['label'], raws); continue
    dt = min(ds); gm_date[g['id']] = (dt, raws)
    age = (TODAY - dt).days
    if age > 365: add1('C1.5b 來源日期超過 12 個月', '中', g['sheet'], g['ref'], g['id'], g['label'], f'{raws}；距今約 {age} 天（以最晚可能日期計）')
    elif age > 182: add1('C1.5a 來源日期超過 6 個月（未滿 12 個月）', '低', g['sheet'], g['ref'], g['id'], g['label'], f'{raws}；距今約 {age} 天')
# 6 被引用次數
refcount = {}
for k in set(inputs) | set(gm_cells):
    us = direct_users(k)
    refcount[k] = (len(us), len([u for u in us if u[0] not in REGISTRY]))
for (s, a), k in sorted(inputs.items(), key=lambda z: (SHEETS.index(z[0][0]), cells[z[0]]['r'], cells[z[0]]['c'])):
    if k == '藍字文字': continue
    tot, mdl = refcount[(s, a)]
    if mdl == 0:
        add1('C1.6 輸入格被模型公式引用 0 次（只被登錄頁讀取或完全未被讀取）', '中' if k == '藍字數值' else '低', s, a, '、'.join(gm_cells.get((s, a), [])), row_label(s, cells[(s, a)]['r']),
             f'{k}；值 {cells[(s,a)]["f"]}；含治理頁引用 {tot} 次')

# ================= C2 =================
c2 = []
for r in range(5, 1000):
    eid = v('DB_Evidence', f'A{r}')
    if not (isinstance(eid, str) and re.match(r'E\d+', eid)): continue
    row = {c: v('DB_Evidence', f'{c}{r}') for c in 'ABCDEFGHIJKLMNOPQ'}
    ed, _ = parse_date(row['B'])
    reasons = []
    st = str(row['L'] or ''); jd = str(row['I'] or '')
    if '待判定' in st or '待 Andy' in st or '待Andy' in st: reasons.append(f'狀態：{st}')
    if '待查' in jd: reasons.append('判定：待查')
    later = []
    for sid in src_ids(row['M']):
        if sid in src and src[sid]['date'] and ed and ed > src[sid]['date'] and not jd.startswith('採納'):
            later.append(f"{sid}（{src[sid]['date_raw']}）")
    if later: reasons.append('日期晚於相關 SRC 文件日期且判定非採納：' + '、'.join(later[:6]) + (f' 等 {len(later)} 筆' if len(later) > 6 else ''))
    if not reasons: continue
    c2.append(dict(id=eid, date=row['B'], claim=str(row['C'])[:200], param=str(row['F'])[:120], status=row['L'], judge=row['I'],
                   src=str(row['M'])[:200], tag=row['E'], grade=row['P'], days=(TODAY - ed).days if ed else None,
                   cat=('待判定／待 Andy' if any(x.startswith('狀態') for x in reasons) else '') + ('｜待查' if '判定：待查' in reasons else '') + ('｜晚於 SRC 未採納' if later else ''),
                   reasons='；'.join(reasons), row=r))

# ================= C4 =================
def r1c1(formula, own, r0, c0, shift=0):
    """把公式轉成相對 R1C1 寫法（文字）。
    own：公式所在頁；*_Prod 頁名一律換成核心頁名（「改讀本組 _Prod 頁」為明訂差異）；與 own 的核心頁同名的前綴去掉。
    shift：自我檢查副本（S:AG）的欄位平移 16 欄；平移只套在本頁與 *_Prod 頁的引用。"""
    base = own[:-5] if own.endswith('_Prod') else own
    try: toks = Tokenizer(formula).items
    except Exception: return formula
    out = []
    for t in toks:
        if t.type == 'OPERAND' and t.subtype == 'RANGE' and t.value.lower() not in _lnames:
            ref = t.value; sh = None
            if '!' in ref:
                sh, ref = ref.rsplit('!', 1); sh = sh.strip("'")
            is_local = sh is None or sh == own or (sh.endswith('_Prod'))
            if sh is not None and sh.endswith('_Prod'): sh = sh[:-5]
            if sh == base: sh = None
            parts = []
            for p in ref.split(':'):
                m = re.fullmatch(r'(\$?)([A-Z]{1,3})?(\$?)(\d+)?', p)
                if not m: parts.append(p); continue
                ca, col, ra, row = m.groups(); s_ = ''
                if row: s_ += f'R{row}' if ra else f'R[{int(row)-r0}]'
                if col:
                    cn = CI(col)
                    if shift and is_local and cn >= 19: cn -= shift
                    s_ += f'C{cn}' if ca else f'C[{cn-c0}]'
                parts.append(s_)
            out.append((sh + '!' if sh else '') + ':'.join(parts))
        elif t.type == 'FUNC': out.append(t.value.upper())
        else: out.append(t.value)
    return ''.join(out)
def reads_core_not_prod(formula, mp):
    """鏡像公式中，讀原頁某格、而該格在對應 *_Prod 頁同位置也有公式（應讀本組 _Prod 頁？）的引用。"""
    hits = []
    for t in Tokenizer(formula).items:
        if not (t.type == 'OPERAND' and t.subtype == 'RANGE' and '!' in t.value): continue
        sh, ref = t.value.rsplit('!', 1); sh = sh.strip("'")
        if sh + '_Prod' not in MIRROR_PAGES: continue
        try: c1_, r1_, c2_, r2_ = range_boundaries(ref.replace('$', ''))
        except Exception: continue
        if r2_ is None or r2_ < 8: continue
        for rr in range(max(r1_, 8), r2_ + 1):
            for cc_ in range(c1_, (c2_ or c1_) + 1):
                x = cells.get((sh + '_Prod', f'{L(cc_)}{rr}'))
                if x and isformula(x) and not re.fullmatch(rf"='?{re.escape(sh)}'?!\$?{L(cc_)}\$?{rr}", x['f']):
                    hits.append(t.value); break
            else: continue
            break
    return hits
_lnames = {n.lower() for n in names}

c4 = []; c4_stats = collections.defaultdict(collections.Counter)
DOC_DIFF = {}
for mp in sorted(MIRROR_PAGES):
    core = mp[:-5]
    mcells = {(x['r'], x['c']): x for (s, a), x in cells.items() if s == mp}
    for (r, c), x in sorted(mcells.items()):
        if not isformula(x): continue
        if c >= 19:   # 自我檢查副本 S:AG ↔ 核心頁 C:Q
            cc = c - 16; kind = '自我檢查副本'
        else: cc = c; kind = '主體'
        core_a = f'{L(cc)}{r}'; cx = cells.get((core, core_a))
        mf = x['f']
        if re.fullmatch(rf"='?{re.escape(core)}'?!\$?{L(cc)}\$?{r}", mf):
            c4_stats[mp][f'{kind}：直接讀原頁同格'] += 1; continue
        if cx is None or not isformula(cx):
            c4_stats[mp][f'{kind}：核心頁同位置非公式'] += 1
            c4.append(dict(page=mp, core=core, cell=f'{L(c)}{r}', core_cell=core_a, label=row_label(core, r), kind=kind,
                           diff='核心頁同位置不是公式（或空白）', mirror_f=mf[:250], core_f=str(cx['f'] if cx else '')[:250], documented='否'))
            continue
        a1 = r1c1(mf, mp, r, cc, 16 if kind == '自我檢查副本' else 0); b1 = r1c1(cx['f'], core, r, cc)
        rc = reads_core_not_prod(mf, mp)
        if rc:
            c4.append(dict(page=mp, core=core, cell=f'{L(c)}{r}', core_cell=core_a, label=row_label(core, r), kind=kind,
                           diff='讀原頁某格，但該格在本組 _Prod 頁也有公式（是否應改讀 _Prod 頁）：' + '、'.join(rc[:4]), mirror_f=mf[:250], core_f=cx['f'][:250], documented='待判讀'))
            c4_stats[mp][f'{kind}：讀原頁但本組 _Prod 頁有對應格'] += 1
        if a1 == b1: c4_stats[mp][f'{kind}：結構相同（*_Prod 頁名視同原頁）'] += 1; continue
        if r == 50 and mp in ('Perf_Prod', 'Perf_Batch_Prod') and kind == '主體' and 'CTL_ProdDerate' in mf:
            c4_stats[mp]['主體：第 50 列改讀 CTL_ProdDerate（明訂）'] += 1; continue
        if r == 50 and kind == '自我檢查副本' and 'Serving!$C$18' in mf:
            c4_stats[mp]['副本：第 50 列＝Serving!C18（明訂）'] += 1; continue
        c4_stats[mp][f'{kind}：結構不同（未明訂）'] += 1
        c4.append(dict(page=mp, core=core, cell=f'{L(c)}{r}', core_cell=core_a, label=row_label(core, r), kind=kind,
                       diff='R1C1 結構不同', mirror_f=mf[:250], core_f=cx['f'][:250], documented='否'))
    # 鏡像頁缺列（資訊）
    crow = {x['r'] for (s, a), x in cells.items() if s == core and isformula(x)}
    mrow = {x['r'] for (s, a), x in cells.items() if s == mp and isformula(x)}
    c4_stats[mp]['（資訊）核心頁有公式、鏡像頁整列未鏡像的列數'] = len(crow - mrow)

# Sens_Perf/Sens_Train ↔ Perf/Training（依世代、層級索引對應欄）
def gen_tier_col(core, g, t):
    for c in range(3, 40):
        if v(core, f'{L(c)}6') == g and v(core, f'{L(c)}7') == t: return c
    return None
for sp, core in (('Sens_Perf', 'Perf'), ('Sens_Train', 'Training')):
    scen_cells = {(s, a) for (s, a), x in cells.items() if s == sp and (x['fill'] in ('FFFFFF00',) or (x['color'] == 'FF0000FF' and not isformula(x)))}
    for (s, a), x in sorted(cells.items(), key=lambda z: (z[1]['r'], z[1]['c'])):
        if s != sp or x['c'] < 3 or x['r'] < 8: continue
        g_, t_ = v(sp, f'{L(x["c"])}6'), v(sp, f'{L(x["c"])}7')
        cc = gen_tier_col(core, g_, t_)
        if cc is None: continue
        cx = cells.get((core, f'{L(cc)}{x["r"]}'))
        if (s, a) in scen_cells:
            c4_stats[sp]['情境輸入格（黃底或藍字）'] += 1; continue
        if not isformula(x):
            if cx is not None and not isformula(cx) and cx['f'] == x['f']: c4_stats[sp]['常數相同'] += 1; continue
            c4_stats[sp]['非公式且與核心頁不同'] += 1
            c4.append(dict(page=sp, core=core, cell=a, core_cell=f'{L(cc)}{x["r"]}', label=row_label(sp, x['r']), kind='敏感度',
                           diff='非情境格的常數與核心頁不同', mirror_f=str(x['f'])[:250], core_f=str(cx['f'] if cx else '')[:250], documented='否'))
            continue
        if cx is None or not isformula(cx):
            c4_stats[sp]['核心頁同位置非公式'] += 1
            c4.append(dict(page=sp, core=core, cell=a, core_cell=f'{L(cc)}{x["r"]}', label=row_label(sp, x['r']), kind='敏感度',
                           diff='核心頁同位置不是公式（或空白）', mirror_f=x['f'][:250], core_f=str(cx['f'] if cx else '')[:250], documented='否'))
            continue
        a1 = r1c1(x['f'], core, x['r'], x['c']); b1 = r1c1(cx['f'], core, x['r'], cc)
        if a1 == b1: c4_stats[sp]['結構相同'] += 1; continue
        # 讀情境倍數列（Sens_Train 第 8 列）或同頁情境格者視為情境機制
        c4_stats[sp]['結構不同'] += 1
        c4.append(dict(page=sp, core=core, cell=a, core_cell=f'{L(cc)}{x["r"]}', label=row_label(sp, x['r']), kind='敏感度',
                       diff='R1C1 結構不同', mirror_f=x['f'][:250], core_f=cx['f'][:250], documented='待判讀（可能為情境機制）'))
# 其他敏感度頁：同列跨情境欄的結構一致性
for sp in ('Sensitivity', 'Sens_Rev', 'Sens_Har'):
    rows = collections.defaultdict(list)
    for (s, a), x in cells.items():
        if s == sp and x['c'] >= 3 and isformula(x): rows[x['r']].append(x)
    for r, xs in sorted(rows.items()):
        xs.sort(key=lambda z: z['c'])
        base = xs[0]; bf = r1c1(base['f'], sp, r, base['c'])
        for x in xs[1:]:
            xf = r1c1(x['f'], sp, r, x['c'])
            if xf == bf: c4_stats[sp]['與同列首欄結構相同'] += 1; continue
            c4_stats[sp]['與同列首欄結構不同'] += 1
            c4.append(dict(page=sp, core='（同列首欄 ' + L(base['c']) + '）', cell=f'{L(x["c"])}{r}', core_cell=f'{L(base["c"])}{r}', label=row_label(sp, r), kind='敏感度（列內）',
                           diff='同列跨情境欄結構不同', mirror_f=x['f'][:250], core_f=base['f'][:250], documented='待判讀（可能為情境改動列）'))

# ================= C5 =================
ALLOWED = {0, 1, 2, 100, 1000, 1e6, 1e9, 1e12, 24, 365, 8760, 3600}
POSFN = {'INDEX', 'MATCH', 'CHOOSE', 'TEXT', 'LEFT', 'MID', 'RIGHT', 'ROUND', 'ROUNDUP', 'ROUNDDOWN', 'CEILING', 'FLOOR', 'OFFSET', 'DATE', 'FIND', 'SUBSTITUTE', 'COUNTIF', 'VALUE'}
c5 = []
for (s, a), c in cls.items():
    if c != '核心' or not isformula(cells[(s, a)]): continue
    fm = cells[(s, a)]['f']
    toks = Tokenizer(fm).items
    stack = []
    for i, t in enumerate(toks):
        if t.type == 'FUNC' and t.subtype == 'OPEN': stack.append(t.value[:-1].upper())
        elif t.type == 'PAREN' and t.subtype == 'OPEN': stack.append('(')
        elif t.subtype == 'CLOSE' and t.type in ('FUNC', 'PAREN'):
            if stack: stack.pop()
        elif t.type == 'OPERAND' and t.subtype == 'NUMBER':
            try: val = float(t.value)
            except ValueError: continue
            if val in ALLOWED: continue
            prev = toks[i - 1] if i else None; nxt = toks[i + 1] if i + 1 < len(toks) else None
            fn = stack[-1] if stack else ''
            bare_arg = prev is not None and ((prev.type == 'FUNC' and prev.subtype == 'OPEN') or prev.type == 'SEP') and \
                       (nxt is None or nxt.type == 'SEP' or (nxt.type == 'FUNC' and nxt.subtype == 'CLOSE'))
            lg = math.log10(abs(val)) if val else 0
            if fn in POSFN and bare_arg: ctx = '位置或格式參數'
            elif any(z in ('INDEX', 'MATCH', 'CHOOSE') for z in stack): ctx = '索引運算（INDEX／MATCH 內）'
            elif abs(lg - round(lg)) < 1e-9: ctx = '10 的次方（單位換算）'
            elif val in (12, 168, 525600, 60, 7, 52, 30, 31536000, 1440, 86400): ctx = '時間換算'
            elif abs(val) >= 1e90: ctx = '哨兵值（極大數）'
            else: ctx = '疑似參數或門檻（需判讀）'
            j0 = sum(len(x.value) for x in toks[:i]); frag = fm[max(0, j0 - 30): j0 + len(t.value) + 30]
            c5.append(dict(sheet=s, cell=a, row=cells[(s, a)]['r'], label=row_label(s, cells[(s, a)]['r']), const=t.value, func=fn, ctx=ctx, frag=frag))
C5ORDER = ['疑似參數或門檻（需判讀）', '時間換算', '10 的次方（單位換算）', '哨兵值（極大數）', '索引運算（INDEX／MATCH 內）', '位置或格式參數']
c5.sort(key=lambda z: (C5ORDER.index(z['ctx']), SHEETS.index(z['sheet']), z['row'], z['cell']))

# ================= C6 =================
c6 = []
unit_pages = set()
for (s, a), k in sorted(inputs.items(), key=lambda z: (SHEETS.index(z[0][0]), cells[z[0]]['r'], cells[z[0]]['c'])):
    if k != '藍字數值': continue
    u, has = unit_of(s, cells[(s, a)]['r'])
    if has: unit_pages.add(s)
    if has and blank(u):
        c6.append(dict(item='C6.1 輸入格的單位欄空白', sheet=s, cell=a, label=row_label(s, cells[(s, a)]['r']), unit='', other='', note=''))
no_unit_pages = sorted({s for (s, a), k in inputs.items() if k == '藍字數值'} - unit_pages, key=SHEETS.index)
# 6.2：同一物理量不同單位
GEN = r'(Hopper|H100|GB200|GB300|VR200|Rubin Ultra|Luna|Sol|Astra|NVL72|NVL\d+)'
def norm_label(t):
    t = re.sub(r'（[^）]*）|\([^)]*\)', '', str(t)); t = re.sub(GEN, '', t)
    t = re.sub(r'v5\.\d+', '', t); t = re.sub(r'[\s—–\-：:；;、，,]+', '', t)
    return t
qty = collections.defaultdict(list)
for s in SHEETS:
    if s in GOV_PAGES | META_PAGES | {'SRC_Index'} and s not in SRC_PAGES: continue
    for r in range(1, 400):
        lab = row_label(s, r)
        if not lab or len(lab) < 3: continue
        if s in SRC_PAGES:
            u = v(s, f'F{r}'); lab = v(s, f'B{r}') or ''
            if not isinstance(u, str) or not v(s, f'A{r}') or not str(v(s, f'A{r}')).startswith('SRC_'): continue
        elif s == 'L1':
            u = v(s, f'G{r}'); lab = v(s, f'B{r}') or ''
        else:
            u, has = unit_of(s, r)
            if not has: continue
        if not isinstance(u, str) or not u.strip() or u.strip() in ('單位',): continue
        qty[norm_label(lab)].append((s, r, lab, u.strip()))
KW = [('每 GPU／GPU-hr', r'GPU', '每架', r'架'), ('$/M', r'\$/M(?![WB])', '$/k', r'\$/k'), ('GW', r'GW', 'MW', r'MW'), ('年', r'年', '月', r'月')]
for key, lst in qty.items():
    units = {u for _, _, _, u in lst}
    if len(units) > 1 and len({s for s, _, _, _ in lst}) > 1:
        for s, r, lab, u in lst:
            c6.append(dict(item='C6.2a 同一列標籤（去除世代與括號後）在不同頁單位不同', sheet=s, cell=f'列 {r}', label=str(lab)[:100], unit=u,
                           other=' ／ '.join(sorted(units))[:200], note=f'標籤鍵：{key[:40]}'))
for key, lst in qty.items():
    for s, r, lab, u in lst:
        for nm, ra, nb, rb in KW:
            la, lb = re.search(ra, str(lab)), re.search(rb, str(lab))
            ua, ub = re.search(ra, u), re.search(rb, u)
            if (la and not lb and ub and not ua) or (lb and not la and ua and not ub):
                c6.append(dict(item=f'C6.2b 列標籤與單位的口徑詞不一致（{nm} 對 {nb}）', sheet=s, cell=f'列 {r}', label=str(lab)[:100], unit=u, other='', note=''))

# ================= C7 =================
# 世代維度
def page_has_gen_header(s):
    for r in range(1, 12):
        txt = ' '.join(str(v(s, f'{L(c)}{r}') or '') for c in range(1, 35))
        if sum(1 for g in ('Hopper', 'GB200', 'GB300', 'VR200') if g in txt) >= 2: return True
    return False
gen_hdr = {s: page_has_gen_header(s) for s in SHEETS}
def row_multi(s, r):
    vals = [cells[(s, f'{L(c)}{r}')]['v'] for c in range(3, 35) if (s, f'{L(c)}{r}') in cells and isnum(cells[(s, f'{L(c)}{r}')]['v'])]
    return len(vals) >= 2 and len(set(vals)) >= 2
# m 路徑根
MRX = r'變現|Monetiz|閉合|缺口|落差|κ|Kappa|計價倍數'
m_roots = []
for n in sorted(names):
    t = names[n]; sh, rg = t.split('!'); a0 = rg.replace('$', '').split(':')[0]
    r0 = int(re.search(r'\d+', a0).group()); lab = row_label(sh, r0)
    if sh == 'L1': lab = str(v('L1', f'B{r0}') or '')
    hit = re.search(MRX, n + ' ' + lab) or n in ('CTL_Monetize',) or re.match(r'L1_M(Implied|Fleet|API|Sub|Seat|ixFactor)', n) \
        or n.startswith(('L1_Gap', 'L1_PriceReal', 'L1_LReq', 'L1_TokPerPromptClose', 'L1_ScaleServe', 'AL_SpendBasis', 'AL_Kappa'))
    if hit: m_roots.append((('NAME', n), f'{n}（{sh}!{rg}）：{lab[:60]}'))
for r in range(1, 400):
    lab = str(v('Cap_In', f'A{r}') or '')
    if re.search(MRX, lab):
        for c in range(3, 10):
            k = ('Cap_In', f'{L(c)}{r}')
            if k in cells and (isformula(cells[k]) or k in inputs):
                m_roots.append((k, f'Cap_In 第 {r} 列：{lab[:60]}')); break
m_reach = upstream([k for k, _ in m_roots], True)
m_inputs = {k for k in m_reach if k in inputs}
m_rows = collections.defaultdict(collections.Counter)
for k in m_reach:
    if k[0] in ('NAME', 'RANGE') or k not in cells: continue
    if k[0] in GOV_PAGES | {'SRC_Index'}: continue
    m_rows[(k[0], cells[k]['r'])]['f' if isformula(cells[k]) else 'i'] += 1
m_row_list = [dict(sheet=s, row=r, label=row_label(s, r), formulas=cn['f'], inputs=cn['i'], cls=page_class(s) or '核心') for (s, r), cn in m_rows.items()]
m_row_list.sort(key=lambda z: (SHEETS.index(z['sheet']), z['row']))
# m 路徑上的 SRC 值（SRC 頁常數經具名範圍進入）
m_src = sorted({k for k in m_reach if k[0] in SRC_PAGES and k in cells and not isformula(cells[k])})

c7 = []
gm_by_id = {g['id']: g for g in gm}
allin = sorted(set(k for k, t in inputs.items() if t != '藍字文字') | {k for k in gm_cells if k in cells and not isformula(cells[k])},
               key=lambda z: (SHEETS.index(z[0]), cells[z]['r'], cells[z]['c']))
for k in allin:
    s, a = k; x = cells[k]; ids = gm_cells.get(k, []); g = gm_by_id[ids[0]] if ids else {}
    u, has = unit_of(s, x['r'])
    dt = gm_date.get(g.get('id'), (None, ''))
    c7.append(dict(gm='、'.join(ids), sheet=s, cell=a, label=row_label(s, x['r']), unit=u if has else '（本頁無單位欄）', value=x['v'],
                   kind=inputs.get(k, '（Gov_Map 登錄之非藍字格）'),
                   tag=g.get('cat') or tag_of(s, x['r']), lo=g.get('lo'), hi=g.get('hi'), src=g.get('src'), dec=g.get('dec'),
                   sdate=(dt[0].isoformat() if dt[0] else dt[1]), refs=refcount.get(k, (0, 0))[1], refs_all=refcount.get(k, (0, 0))[0],
                   mpath='是' if k in m_inputs else '否', gen=('世代欄頭' if gen_hdr[s] else '') + ('／列內多值' if row_multi(s, x['r']) else ''),
                   cls=cls.get(k, '')))

out = dict(c1=c1, c2=c2, c3_page={k: dict(v_) for k, v_ in c3_page.items()}, dead=dead, core_rows=core_row_list, slim=dict(slim), nform=nform,
           side_unreached=dict(side_unreached), c4=c4, c4_stats={k: dict(v_) for k, v_ in c4_stats.items()}, c5=c5, c6=c6, no_unit_pages=no_unit_pages,
           c7=c7, m_roots=[t for _, t in m_roots], m_rows=m_row_list, m_inputs=len(m_inputs), m_src=len(m_src),
           contract_named=contract_named, n_roots=len(roots), root_names=len(root_names), func_use=dict(G['func_use']), dynamic=G['dynamic'],
           n_inputs=collections.Counter(inputs.values()), n_gm=len(gm), gm_target_kind={k: dict(v_) for k, v_ in gm_target_kind.items()},
           reach_n=len([k for k in reach if k[0] not in ('NAME', 'RANGE')]), dead_via_gov=sum(1 for z in dead if z['reach_via_gov'] == '是'))
pickle.dump(out, open(sys.argv[3], 'wb'))
cnt = lambda L_, key: collections.Counter(z[key] for z in L_)
print('C1', cnt(c1, 'item')); print('C2', len(c2), cnt(c2, 'cat'))
print('C3 slim', slim, 'nform', nform, 'dead', len(dead), 'dead via gov', out['dead_via_gov'], 'side_unreached', side_unreached)
print('C4', {k: v_ for k, v_ in out['c4_stats'].items()}); print('C4 items', len(c4), cnt(c4, 'page'))
print('C5', len(c5), cnt(c5, 'ctx')); print('C6', cnt(c6, 'item'), 'no unit pages', no_unit_pages)
print('C7 inputs', len(c7), 'm roots', len(m_roots), 'm inputs', len(m_inputs), 'm rows', len(m_row_list), 'm src', len(m_src))
print('contract', contract_named)

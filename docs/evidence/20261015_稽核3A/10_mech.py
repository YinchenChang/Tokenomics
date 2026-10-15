"""3A 機械檢查（沿用第 2 段 10_mech.py／11_align.py／40_upY.py 的做法，列清單改為 3A 510 列）。
(a) 同列跨欄公式結構（R1C1）；(b) 同欄對位（世代×層級頁之間）與 INDEX 常數；(c) 文字回傳 IF 與下游未守衛使用；
(d) 上游 Y1–Y9 輸入（依賴圖）；(e) 每列下游使用者數（死列候選）。
用法：python3 10_mech.py <wb.pkl> <graph.pkl> <rows.json> <稽核1明細.xlsx> <out.pkl>"""
import pickle,sys,re,collections,json,openpyxl
from openpyxl.formula import Tokenizer
from openpyxl.utils import column_index_from_string as CI
d=pickle.load(open(sys.argv[1],'rb'));G=pickle.load(open(sys.argv[2],'rb'))
cells=d['cells'];edges=G['edges'];ROWS=json.load(open(sys.argv[3]))
byrow=collections.defaultdict(list)
for (s,a),x in cells.items(): byrow[(s,x['r'])].append((a,x))
def col(a): return re.match('[A-Z]+',a).group()
def r1c1(f,r0,c0):
    out=[]
    try: toks=Tokenizer(f).items
    except Exception: return f
    for t in toks:
        v=t.value
        if t.type=='OPERAND' and t.subtype=='RANGE' and re.fullmatch(r"((?:'[^']+'|[A-Za-z_0-9]+)!)?\$?[A-Z]{1,3}\$?[0-9]+(:\$?[A-Z]{1,3}\$?[0-9]+)?",v):
            def rep(m):
                sh=m.group(1) or ''; cd,cl,rd,rw=m.group(2),m.group(3),m.group(4),m.group(5)
                c=CI(cl); r=int(rw)
                return sh+(f'R{r}' if rd else f'R[{r-r0}]')+(f'C{c}' if cd else f'C[{c-c0}]')
            v=re.sub(r"((?:'[^']+'|[A-Za-z_0-9]+)!)?(\$?)([A-Z]{1,3})(\$?)([0-9]+)",rep,v)
        out.append(v)
    return ''.join(out)
TXT=re.compile(r'"([^"]{2,})"')
rev=collections.defaultdict(set)
for n,ps in edges.items():
    for p in ps: rev[p].add(n)
def users_of(k):
    us=set();stack=[k];seen=set()
    while stack:
        cur=stack.pop()
        for u in rev.get(cur,()):
            if u in seen: continue
            seen.add(u)
            if u[0] in('NAME','RANGE'): stack.append(u)
            else: us.add(u)
    return us
GOV={'Gov_Map','Checks','Load_Bearing','SRC_Index','Decisions','DB_Evidence'}
G15={'Perf','DC_Cost','Unit_Cost','Interface','Theory_Rev','Fleet_1GW','Amortize','Training','Perf_Batch','Cache_Store','Energy'}
COLS=[chr(c) for c in range(ord('C'),ord('Q')+1)]
res=[];mis=[];idx=[];l7=[]
for R in ROWS:
    s,r=R['sheet'],R['row']
    cs=sorted(byrow[(s,r)],key=lambda t:(len(col(t[0])),t[0]))
    fcs=[(a,x) for a,x in cs if isinstance(x['f'],str) and x['f'].startswith('=') and col(a) not in('A','B')]
    unit=None
    for a,x in cs:
        if col(a)=='B' and isinstance(x['v'],str) and len(x['v'])<25: unit=x['v']
    pats=collections.OrderedDict()
    for a,x in fcs: pats.setdefault(r1c1(x['f'],x['r'],x['c']),[]).append(a)
    txt=sorted({m.group(1) for a,x in fcs for m in TXT.finditer(x['f']) if m.group(1) not in('0.00','#,##0','0.0','0')})
    textvals=[a for a,x in fcs if isinstance(x['v'],str)]
    # 下游使用者（非治理頁）
    us=set()
    for a,x in cs: us|={u for u in users_of((s,a)) if u[0] not in GOV}
    us_sheets=collections.Counter(u[0] for u in us)
    # 對位
    for a,x in fcs:
        f=x['f']
        if s in G15 and col(a) in COLS:
            for t in Tokenizer(f).items:
                if t.type=='OPERAND' and t.subtype=='RANGE' and '!' in t.value:
                    sh,rg=t.value.rsplit('!',1); sh=sh.strip("'")
                    if sh in G15 and ':' not in rg:
                        m=re.match(r'(\$?)([A-Z]+)',rg)
                        if not m.group(1) and m.group(2)!=col(a): mis.append((f'{s}!{a}',t.value,f[:200]))
        for m in re.finditer(r'INDEX\(([A-Za-z_][A-Za-z_0-9]*|[A-Za-z_]+!\$?[A-Z]+\$?\d+:\$?[A-Z]+\$?\d+),\s*([0-9]+)(?:,\s*([0-9]+))?\)',f):
            idx.append((f'{s}!{a}',m.group(1),m.group(2),m.group(3)))
        if TXT.search(f) and 'IF(' in f:
            for u in users_of((s,a)):
                if u[0] in GOV: continue
                uf=cells[u]['f']
                if not isinstance(uf,str): continue
                guarded=bool(re.search(r'ISNUMBER|ISTEXT|ISERROR|IFERROR',uf))
                if not guarded: l7.append(dict(src=f'{s}!{a}',srcv=x['v'],user=f'{u[0]}!{u[1]}',userf=uf[:200],userv=cells[u]['v']))
    res.append(dict(sheet=s,row=r,label=R['label'],unit=unit,nform=len(fcs),patterns=[(p[:400],v) for p,v in pats.items()],texts=txt,textvals=textvals,
        users=len(us),user_sheets=dict(us_sheets),rep=(fcs[0][0],fcs[0][1]['f'][:500],fcs[0][1]['v']) if fcs else None))
# 上游 Y
wb=openpyxl.load_workbook(sys.argv[4],read_only=True)
ymap=collections.defaultdict(set)
for r in wb['系統性問題'].iter_rows(min_row=3,values_only=True):
    for part in str(r[6]).split('；'):
        if '!' not in part: continue
        sh,cs_=part.split('!',1)
        for c in cs_.split(','): ymap[(sh.strip(),c.strip())].add(r[0])
memo={}
def up(node):
    if node in memo: return memo[node]
    memo[node]=frozenset(); acc=set()
    if node[0] not in('NAME','RANGE') and node in ymap: acc|=ymap[node]
    for p in edges.get(node,()):
        if p[0] in GOV: continue
        acc|=up(p)
    memo[node]=frozenset(acc); return memo[node]
direct={}
for x in res:
    ys=set();dy=set()
    for a,c in byrow[(x['sheet'],x['row'])]:
        ys|=up((x['sheet'],a))
        if (x['sheet'],a) in ymap: dy|=ymap[(x['sheet'],a)]
        for p in edges.get((x['sheet'],a),()):
            q=[p]
            while q:
                n=q.pop()
                if n[0] in('NAME','RANGE'): q+=list(edges.get(n,()))
                elif n in ymap: dy|=ymap[n]
    x['upY']=sorted(ys); x['directY']=sorted(dy)
pickle.dump(dict(rows=res,mis=mis,idx=idx,l7=l7),open(sys.argv[5],'wb'))
print('rows',len(res),'multi',sum(1 for x in res if len(x['patterns'])>1),'mis',len(mis),'idx',len(idx),'l7',len(l7))
print('no users',[(x['sheet'],x['row']) for x in res if x['users']==0][:60])
print('upY',collections.Counter(y for x in res for y in x['upY']),'directY',collections.Counter(y for x in res for y in x['directY']))
for z in mis[:30]: print('MIS',z)

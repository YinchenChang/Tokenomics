"""3B 機械檢查（441 頁＋列）：
(a) 同列跨欄公式 R1C1 結構數；(b) 文字回傳（IF 文字）與數值 0 代替不可達（MAX(0,…)、IF(…,0)）；
(c) L8：上游含哪些第 1 段 Y 類輸入格（依賴圖，不穿越登錄頁）；(d) 下游契約名稱：本列格會影響哪些 IF_／IFW_／IFC_／L1_ 具名範圍；
(e) 本列是否被任何公式引用（無引用＝只顯示）。
用法：python3 10_mech.py <wb.pkl> <graph.pkl> <out.json>"""
import pickle,sys,json,re,collections,openpyxl
from openpyxl.formula import Tokenizer
from openpyxl.utils import column_index_from_string as CI
d=pickle.load(open(sys.argv[1],'rb'));G=pickle.load(open(sys.argv[2],'rb'))
cells=d['cells'];edges=G['edges'];names=d['names']
rows=json.load(open('docs/evidence/20261015_稽核3B/00_rows.json'))
SKIP={'Gov_Map','Decisions','DB_Evidence','Load_Bearing','SRC_Index','Checks'}
# Y 類輸入格（第 1 段明細）
wb=openpyxl.load_workbook('docs/reports/20261015_稽核1_明細.xlsx',read_only=True)
ymap=collections.defaultdict(set)
for r in wb['系統性問題'].iter_rows(min_row=3,values_only=True):
    for part in str(r[6]).split('；'):
        if '!' not in part: continue
        sh,cs=part.split('!',1)
        for c in cs.split(','): ymap[(sh.strip(),c.strip())].add(r[0])
memo={}
sys.setrecursionlimit(100000)
def up(node):
    if node in memo: return memo[node]
    memo[node]=frozenset(); acc=set()
    if node[0] not in('NAME','RANGE') and node in ymap: acc|=ymap[node]
    for p in edges.get(node,()):
        if p[0] in SKIP: continue
        acc|=up(p)
    memo[node]=frozenset(acc); return memo[node]
# 反向圖
rev=collections.defaultdict(set)
for k,ps in edges.items():
    for p in ps: rev[p].add(k)
# 下游契約名稱：名稱節點的上游格集合（不穿越登錄頁）
CONTRACT=[n for n in names if '!' not in n and re.match(r'(IF_|IFW_|IFC_|L1_)',n)]
upc={}
def upcells(node):
    if node in upc: return upc[node]
    upc[node]=frozenset(); acc=set()
    if node[0] not in('NAME','RANGE'): acc.add(node)
    for p in edges.get(node,()):
        if p[0] in SKIP: continue
        acc|=upcells(p)
    upc[node]=frozenset(acc); return upc[node]
cell2names=collections.defaultdict(set)
for n in CONTRACT:
    for c in upcells(('NAME',n)): cell2names[c].add(n)
byrow=collections.defaultdict(list)
for k,x in cells.items(): byrow[(k[0],x['r'])].append(k)
def r1c1(f,r0,c0):
    out=[]
    for t in Tokenizer(f).items:
        v=t.value
        if t.type=='OPERAND' and t.subtype=='RANGE':
            def rep(m):
                s=m.group(1) or '';cd,cl,rd,rw=m.group(2),m.group(3),m.group(4),m.group(5)
                c=CI(cl);r=int(rw)
                return s+(f'R{r}' if rd else f'R[{r-r0}]')+(f'C{c}' if cd else f'C[{c-c0}]')
            v=re.sub(r"(?<![A-Za-z_0-9.])((?:'[^']+'|[A-Za-z_0-9]+)!)?(\$?)([A-Z]{1,3})(\$?)([0-9]+)(?![A-Za-z_0-9(])",rep,v)
        out.append(v)
    return ''.join(out)
def directusers(k):
    """直接引用本格的公式格（含經範圍、名稱），排除登錄頁。"""
    out=set(); st=[k]; seen=set()
    while st:
        n=st.pop()
        for u in rev.get(n,()):
            if u in seen: continue
            seen.add(u)
            if u[0] in('NAME','RANGE'): st.append(u)
            elif u[0] not in SKIP: out.add(u)
    return out
res=[]
for x in rows:
    sh,r=x['sh'],x['r']
    ks=sorted(byrow[(sh,r)],key=lambda k:(len(re.match('[A-Z]+',k[1]).group()),k[1]))
    col=lambda k:re.match('[A-Z]+',k[1]).group()
    fks=[k for k in ks if isinstance(cells[k]['f'],str) and cells[k]['f'].startswith('=') and col(k) not in('A','B')]
    pats=collections.Counter(re.sub(r'(?<![A-Za-z_\[])\d+(?![\]\d])','#',r1c1(cells[k]['f'],cells[k]['r'],cells[k]['c'])) for k in fks)
    exact=collections.Counter(r1c1(cells[k]['f'],cells[k]['r'],cells[k]['c']) for k in fks)
    txt=sorted({m for k in fks for m in re.findall(r'"([^"]{2,})"',cells[k]['f']) if not re.fullmatch(r'[0#,.]+',m)})
    zero_guard=[k[1] for k in fks if re.search(r'MAX\(0,|,0\)\s*$|IF\([^"]*>0,[^"]*,0\)',cells[k]['f'])]
    textvals=[k[1] for k in fks if isinstance(cells[k]['v'],str)]
    ys=set()
    for k in ks: ys|=up(k)
    dn=set()
    for k in ks: dn|=cell2names.get(k,set())
    users=set()
    for k in ks: users|=directusers(k)
    users={u for u in users if (u[0],cells[u]['r'])!=(sh,r)}
    res.append(dict(sh=sh,r=r,label=x['label'],nform=len(fks),npat=len(pats),nexact=len(exact),texts=txt,zero_guard=zero_guard,textvals=textvals,
        Y=sorted(ys),down=sorted(dn),ndown=len(dn),nusers=len(users),users=sorted({f'{u[0]}!{cells[u]["r"]}' for u in users})[:12]))
json.dump(res,open(sys.argv[3],'w'),ensure_ascii=False,indent=0)
c=collections.Counter(y for v in res for y in v['Y'])
print('rows',len(res),'Y',c,'有Y',sum(1 for v in res if v['Y']))
print('多結構列',[(v['sh'],v['r'],v['npat']) for v in res if v['npat']>1])
print('無引用列',sum(1 for v in res if v['nusers']==0),[(v['sh'],v['r']) for v in res if v['nusers']==0 and v['nform']>0][:80])
print('有下游契約名稱',sum(1 for v in res if v['down']))
print('zero',[(v['sh'],v['r'],v['zero_guard'][:3]) for v in res if v['zero_guard']])

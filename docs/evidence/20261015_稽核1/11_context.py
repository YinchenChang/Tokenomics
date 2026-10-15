"""為第 1 段判讀產生每「頁＋列」輸入群組的上下文（列標籤、欄頭、值、標記、說明欄、Gov_Map 判斷欄、直接使用處）。
用法：python3 11_context.py <wb.pkl> <graph.pkl> <稽核0明細.xlsx> <out.json>"""
import pickle, sys, re, json, collections, openpyxl
from openpyxl.utils import column_index_from_string as CI, get_column_letter as L
d=pickle.load(open(sys.argv[1],'rb')); G=pickle.load(open(sys.argv[2],'rb'))
cells=d['cells']; edges=G['edges']
def v(s,a): return (cells.get((s,a)) or {}).get('v')
def f(s,a): return (cells.get((s,a)) or {}).get('f')
rev=collections.defaultdict(set)
for n,ps in edges.items():
    for p in ps: rev[p].add(n)
def direct_users(node):
    out=set(); stack=[node]; seen=set()
    while stack:
        cur=stack.pop()
        for u in rev.get(cur,()):
            if u in seen: continue
            seen.add(u)
            if u[0] in('NAME','RANGE'): stack.append(u)
            else: out.add(u)
    return out
def rowlab(s,r):
    for col in('A','B'):
        x=v(s,f'{col}{r}')
        if isinstance(x,str) and x.strip(): return x.strip()
    return ''
def header(s,col,r):
    # 往上找最近的文字欄頭（前 12 列內或本列上方 30 列內）
    for rr in range(r-1,0,-1):
        x=v(s,f'{col}{rr}')
        if isinstance(x,str) and x.strip() and not isinstance(f(s,f'{col}{rr}'),(int,float)):
            if not str(f(s,f'{col}{rr}')).startswith('='): return x.strip()[:40]
        if r-rr>40: break
    return ''
wb=openpyxl.load_workbook(sys.argv[3],read_only=True)
inp=list(wb['C7_第1段輸入清單'].iter_rows(min_row=3,values_only=True))
# Gov_Map
gm={}
for (s,a),x in cells.items():
    if s=='Gov_Map' and a.startswith('A') and x['r']>4 and isinstance(x['v'],str) and x['v'].startswith('GM'):
        r=x['r']; gm[x['v']]={k:v('Gov_Map',f'{c}{r}') for k,c in dict(cat='F',role='G',src='H',rel='I',dec='J',lo='K',hi='L',rtxt='M',why='N',tier='P').items()}
lb={v('Load_Bearing',f'A{r}') for r in range(5,60)}
c2=[r for r in wb['C2_證據積壓'].iter_rows(min_row=3,values_only=True)]
groups=collections.OrderedDict()
for r in inp:
    s=r[1]; a=r[2]; a0=a.split(':')[0]; row=int(re.sub('[A-Z]','',a0))
    groups.setdefault((s,row),[]).append(r)
out=[]
for (s,row),rs in groups.items():
    # 說明欄：本列最右側的長文字
    texts=[]
    for (ss,a),x in cells.items():
        if ss==s and x['r']==row and isinstance(x['v'],str) and len(x['v'])>3 and not str(x['f']).startswith('='):
            texts.append((CI(re.match('[A-Z]+',a).group()),a,x['v']))
    texts.sort()
    lab=rowlab(s,row)
    note=' ｜ '.join(f'{a}:{t[:400]}' for _,a,t in texts if t.strip()!=lab)[:900]
    users=collections.Counter(); ex={}
    for r_ in rs:
        for cc in r_[2].split(','):
            for a in [cc]:
                a1=a.split(':')[0]
                for u in direct_users((s,a1)):
                    if u[0] in('Gov_Map','Load_Bearing','SRC_Index','Decisions','DB_Evidence'): continue
                    k=(u[0],rowlab(u[0],cells[u]['r']))
                    users[k]+=1
                    ex.setdefault(k,f"{u[0]}!{u[1]} {str(cells[u]['f'])[:160]}")
    cellsinfo=[]
    for r_ in rs:
        a1=r_[2].split(':')[0]; col=re.match('[A-Z]+',a1).group()
        cellsinfo.append(dict(gm=r_[0],cell=r_[2],hdr=header(s,col,row),val=r_[5],unit=r_[4],tag=r_[7],lo=r_[8],hi=r_[9],src=r_[10],dec=r_[11],srcdate=r_[12],nref=r_[13],m=r_[16],gen=r_[17]))
    gms=sorted({c['gm'] for c in cellsinfo if c['gm']})
    out.append(dict(sheet=s,row=row,label=lab,note=note,
        m=any(c['m']=='是' for c in cellsinfo), lb=any(g in lb for g in gms),
        gov={g:gm.get(g) for g in gms},
        cells=cellsinfo,
        users=[dict(at=f'{k[0]}｜{k[1]}',n=n,ex=ex[k]) for k,n in users.most_common(8)],
        nusers=sum(users.values())))
json.dump(out,open(sys.argv[4],'w'),ensure_ascii=False,default=str,indent=0)
print(len(out), collections.Counter(o['sheet'] for o in out if o['m']))

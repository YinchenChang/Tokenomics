"""建立全簿依賴圖。輸入：00_load.py 的 pickle；輸出：graph pickle。
節點＝(工作表, 格)。範圍引用以虛擬節點 ('RANGE', 'Sheet!A1:B9') 表示，再連到其中每一格（保守：整個範圍都算上游）。
具名範圍以虛擬節點 ('NAME', 名稱) 表示。"""
import pickle, sys, re, collections
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter as L
d=pickle.load(open(sys.argv[1],'rb')); cells=d['cells']; names=d['names']
sheets={s for s,_,_ in d['sheets']}; maxrc={s:(r,c) for s,r,c in d['sheets']}
lnames={n.lower():n for n in names}
def split_sheet(ref, cur):
    if '!' in ref:
        sh,rg=ref.rsplit('!',1); sh=sh.strip("'").replace("''","'")
    else: sh,rg=cur,ref
    return sh,rg.replace('$','')
def expand(sh,rg):
    if sh not in sheets: return None
    mr,mc=maxrc[sh]
    try:
        c1,r1,c2,r2=range_boundaries(rg)
    except Exception: return None
    c1=c1 or 1; r1=r1 or 1; c2=c2 or mc; r2=r2 or mr
    out=[]
    for r in range(r1,min(r2,mr)+1):
        for c in range(c1,min(c2,mc)+1):
            a=f'{L(c)}{r}'
            if (sh,a) in cells: out.append((sh,a))
    return out
edges=collections.defaultdict(set)   # node -> set(precedent nodes)
unresolved=[]; dynamic=[]; func_use=collections.Counter(); consts={}
DYN={'OFFSET','INDIRECT'}
def ref_node(tok,cur,owner):
    v=tok
    if v.lower() in lnames:
        return ('NAME',lnames[v.lower()])
    if v.startswith('#'): unresolved.append((owner,v)); return None
    sh,rg=split_sheet(v,cur)
    if ':' in rg:
        return ('RANGE',f'{sh}!{rg}')
    if sh in sheets and re.fullmatch(r'[A-Z]{1,3}[0-9]+',rg):
        return (sh,rg)
    # 工作表範圍的具名範圍
    if f'{sh}!{rg}' in names: return ('NAME',f'{sh}!{rg}')
    unresolved.append((owner,v)); return None
ranges=set(); nameset=set()
formula_tokens={}
for (sh,a),x in cells.items():
    f=x['f']
    if not (isinstance(f,str) and f.startswith('=')): continue
    try: toks=Tokenizer(f).items
    except Exception as e: unresolved.append(((sh,a),'TOKENIZE:'+str(e))); continue
    nums=[]
    for t in toks:
        if t.type=='FUNC' and t.subtype=='OPEN':
            fn=t.value[:-1].upper(); func_use[fn]+=1
            if fn in DYN: dynamic.append(((sh,a),fn,f))
        elif t.type=='OPERAND' and t.subtype=='RANGE':
            n=ref_node(t.value,sh,(sh,a))
            if n:
                edges[(sh,a)].add(n)
                if n[0]=='RANGE': ranges.add(n[1])
                if n[0]=='NAME': nameset.add(n[1])
        elif t.type=='OPERAND' and t.subtype=='NUMBER':
            nums.append(t.value)
    consts[(sh,a)]=nums
# 具名範圍 -> 範圍/格
name_target={}
for n,t in names.items():
    t=t.lstrip('=')
    parts=[p for p in t.split(',')]
    tg=[]
    for p in parts:
        sh,rg=split_sheet(p,None)
        if ':' in rg: tg.append(('RANGE',f'{sh}!{rg}')); ranges.add(f'{sh}!{rg}')
        elif sh in sheets: tg.append((sh,rg))
        else: unresolved.append((('NAME',n),p))
    name_target[n]=tg
    edges[('NAME',n)]=set(tg)
range_cells={}
for r in ranges:
    sh,rg=r.split('!',1)
    ex=expand(sh,rg)
    if ex is None: unresolved.append((('RANGE',r),r)); ex=[]
    range_cells[r]=ex
    edges[('RANGE',r)]=set(ex)
pickle.dump(dict(edges=dict(edges),name_target=name_target,range_cells=range_cells,
    unresolved=unresolved,dynamic=dynamic,func_use=func_use,consts=consts),open(sys.argv[2],'wb'))
print('formula nodes',sum(1 for k in edges if k[0] not in('NAME','RANGE')),'ranges',len(ranges),'names used',len(nameset))
print('unresolved',len(unresolved),unresolved[:15]); print('dynamic',len(dynamic))

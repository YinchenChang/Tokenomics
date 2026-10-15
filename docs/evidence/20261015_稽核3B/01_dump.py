"""3B 閱讀用精簡列印：每列＝標籤、單位、說明欄、代表公式、同列跨欄 R1C1 結構（不同者全列）、各欄值。
用法：python3 01_dump.py <wb.pkl> <Sheet> [out.txt]；只印 00_rows.json 中的列（另印上下文列標籤）。"""
import pickle,sys,re,json,collections
sys.path.insert(0,'docs/evidence/20261015_稽核2')
from openpyxl.formula import Tokenizer
from openpyxl.utils import column_index_from_string as CI
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells'];sh=sys.argv[2]
rows=json.load(open('docs/evidence/20261015_稽核3B/00_rows.json'))
want=set(x['r'] for x in rows if x['sh']==sh)
byrow=collections.defaultdict(list)
for (s,a),x in cells.items():
    if s==sh: byrow[x['r']].append((a,x))
def r1c1(f,r0,c0):
    out=[]
    for t in Tokenizer(f).items:
        v=t.value
        if t.type=='OPERAND' and t.subtype=='RANGE':
            def rep(m):
                s=m.group(1) or '';cd,cl,rd,rw=m.group(2),m.group(3),m.group(4),m.group(5)
                c=CI(cl);r=int(rw)
                return s+(f'R{r}' if rd else f'R[{r-r0}]')+(f'C{c}' if cd else f'C[{c-c0}]')
            v=re.sub(r"(?<![A-Za-z_0-9.])((?:'[^']+'|[A-Za-z_0-9]+)!)?(\$?)([A-Z]{1,3})(\$?)([0-9]+)(?![A-Za-z_0-9(])",rep,v)  # 不改具名範圍內的字樣（如 B5_SelT）
        out.append(v)
    return ''.join(out)
def fmt(v):
    if isinstance(v,float): return f'{v:.4g}'
    if isinstance(v,str): return v[:40]
    return str(v)
out=[]
for r in sorted(byrow):
    cs=sorted(byrow[r],key=lambda t:(len(re.match('[A-Z]+',t[0]).group()),t[0]))
    col=lambda a:re.match('[A-Z]+',a).group()
    lab=' | '.join(str(x['v'])[:110] for a,x in cs if col(a)=='A')
    if r not in want:
        out.append(f'  ({r}) {lab[:120]}'); continue
    unit=' '.join(str(x['v'])[:30] for a,x in cs if col(a)=='B')
    fcs=[(a,x) for a,x in cs if isinstance(x['f'],str) and x['f'].startswith('=') and col(a) not in('A','B')]
    txts=[(a,x) for a,x in cs if not(isinstance(x['f'],str) and x['f'].startswith('=')) and col(a) not in('A','B')]
    pats=collections.OrderedDict()
    for a,x in fcs: pats.setdefault(r1c1(x['f'],x['r'],x['c']),[]).append(a)
    out.append(f'** {sh}!{r} [{unit}] {lab}')
    # 結構差異只在數字常數者（例如 INDEX 欄號依欄遞增）合併顯示
    grp=collections.OrderedDict()
    for p,v in pats.items(): grp.setdefault(re.sub(r'(?<![A-Za-z_\[])\d+(?![\]\d])','#',p),[]).append((p,v))
    for k,lst in grp.items():
        allc=[a for p,v in lst for a in v]; a=allc[0]
        tag='' if len(lst)==1 else f' [同結構、數字常數不同 ×{len(lst)}；末欄 {allc[-1]}: {cells[(sh,allc[-1])]["f"][:160]}]'
        out.append(f'   {",".join(allc) if len(allc)<4 else allc[0]+"…"+allc[-1]+f"({len(allc)})"}: {cells[(sh,a)]["f"][:330]}{tag}')
    if fcs: out.append('   = '+'  '.join(f'{col(a)}:{fmt(x["v"])}' for a,x in fcs[:16]))
    nt=[f'{col(a)}:{fmt(x["v"]) if not isinstance(x["v"],str) else str(x["v"])[:200]}' for a,x in txts]
    if nt: out.append('   inp/note '+' ; '.join(nt)[:700])
s='\n'.join(out)
if len(sys.argv)>3: open(sys.argv[3],'w').write(s)
else: print(s)

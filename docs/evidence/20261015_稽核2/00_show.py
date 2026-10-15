"""列印指定頁的列：標籤、各欄公式與值（第 2 段閱讀用）。用法：python3 00_show.py <wb.pkl> Sheet r1-r2 [cols]"""
import pickle,sys,re
from openpyxl.utils import get_column_letter as L
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells']
sh=sys.argv[2];a,b=map(int,sys.argv[3].split('-'));cols=sys.argv[4].split(',') if len(sys.argv)>4 else None
def fmt(v):
    if isinstance(v,float): return f'{v:.6g}'
    return str(v)[:90]
for r in range(a,b+1):
    row=[(k[1],x) for k,x in cells.items() if k[0]==sh and x['r']==r]
    if not row: continue
    row.sort(key=lambda t:(len(re.match('[A-Z]+',t[0]).group()),t[0]))
    out=[]
    for addr,x in row:
        col=re.match('[A-Z]+',addr).group()
        if cols and col not in cols: continue
        f=x['f']
        if isinstance(f,str) and f.startswith('='): out.append(f'{addr}: {f[:260]} => {fmt(x["v"])}')
        else: out.append(f'{addr}: [{fmt(x["v"])}]')
    print(f'--- {sh}!{r}'); print('\n'.join(out))

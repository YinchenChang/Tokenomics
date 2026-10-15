"""L3 引用對位機械檢查（m 路徑列）：
(1) 世代×層級／世代×成本頁（C:Q 15 欄）之間的直接引用，欄字母須相同（同欄對位），或為 $ 絕對欄（輸入頁）；
(2) INDEX(IF_*,1,k) 或 INDEX(<C:Q 範圍>,k) 的常數 k，列出供人工對照列標籤所寫世代。
用法：python3 11_align.py <wb.pkl> <mech.pkl> <out.pkl>"""
import pickle,sys,re,collections
from openpyxl.formula import Tokenizer
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells'];names=d['names']
M=pickle.load(open(sys.argv[2],'rb'))
G15={'Perf','Perf_Prod','DC_Cost','Unit_Cost','Interface','Interface_Prod','Theory_Rev','Theory_Rev_Prod','Fleet_1GW','Fleet_1GW_Prod','Amortize','Amortize_Prod','Training','Training_Prod','Perf_Batch','Perf_Batch_Prod','Cache_Store','Unit_Cost_Prod'}
COLS=[chr(c) for c in range(ord('C'),ord('Q')+1)]
pathrows={(x['sheet'],x['row']) for x in M['rows']}
mis=[];idx=[]
for (s,a),x in cells.items():
    if s not in G15 or (s,x['r']) not in pathrows: continue
    col=re.match('[A-Z]+',a).group()
    if col not in COLS: continue
    f=x['f']
    if not(isinstance(f,str) and f.startswith('=')): continue
    for t in Tokenizer(f).items:
        if t.type=='OPERAND' and t.subtype=='RANGE' and '!' in t.value:
            sh,rg=t.value.rsplit('!',1); sh=sh.strip("'")
            if sh in G15 and ':' not in rg:
                m=re.match(r'(\$?)([A-Z]+)',rg)
                if not m.group(1) and m.group(2)!=col: mis.append((f'{s}!{a}',t.value,f[:200]))
    for m in re.finditer(r'INDEX\((IF[A-Za-z_]*|[A-Za-z_]+!\$C\$\d+:\$Q\$\d+),\s*(?:1,)?([0-9]+)\)',f):
        idx.append((f'{s}!{a}',m.group(1),int(m.group(2))))
# L1／Cap_In／Alloc 的 INDEX 常數
for (s,a),x in cells.items():
    if s in('L1','Cap_In','Alloc') and (s,x['r']) in pathrows and isinstance(x['f'],str):
        for m in re.finditer(r'INDEX\(([A-Za-z_]+),1,([0-9]+)\)',x['f']):
            idx.append((f'{s}!{a}',m.group(1),int(m.group(2))))
pickle.dump(dict(mis=mis,idx=idx),open(sys.argv[3],'wb'))
print('同欄對位不符',len(mis))
for z in mis[:40]: print(z)
c=collections.Counter((i[0].split('!')[0],i[1],i[2]) for i in idx)
print('INDEX 常數（頁, 名稱, k）:')
for k,v in sorted(c.items()): print(k,v)

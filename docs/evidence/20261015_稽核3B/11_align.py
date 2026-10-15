"""L3 機械對位（3B 列）：Training／Theory_Rev（C:Q 世代×層級或世代×成本）直接引用其他 C:Q 頁時，欄字母須相同或為 $ 絕對欄；
INDEX(<C:Q 範圍>, 3*(世代-1)+k) 的 k 對照本頁層級索引；Harness 寫死欄（M＝VR200 基準、J＝GB300 基準）對照列標籤。
用法：python3 11_align.py <wb.pkl> <out.json>"""
import pickle,sys,re,json
from openpyxl.formula import Tokenizer
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells']
rows={(x['sh'],x['r']) for x in json.load(open('docs/evidence/20261015_稽核3B/00_rows.json'))}
G15={'Perf','DC_Cost','Unit_Cost','Interface','Theory_Rev','Fleet_1GW','Amortize','Training','Perf_Batch','Cache_Store','Calib'}
COLS=[chr(c) for c in range(ord('C'),ord('Q')+1)]
mis=[];idx=[];hard=[]
for (s,a),x in cells.items():
    if (s,x['r']) not in rows: continue
    f=x['f']
    if not(isinstance(f,str) and f.startswith('=')): continue
    col=re.match('[A-Z]+',a).group()
    if s in('Training','Theory_Rev') and col in COLS:
        for t in Tokenizer(f).items:
            if t.type=='OPERAND' and t.subtype=='RANGE' and '!' in t.value:
                sh,rg=t.value.rsplit('!',1); sh=sh.strip("'")
                if sh in G15 and ':' not in rg:
                    m=re.match(r'(\$?)([A-Z]+)',rg)
                    if not m.group(1) and m.group(2)!=col: mis.append((f'{s}!{a}',t.value))
        for m in re.finditer(r'INDEX\(([A-Za-z_]+!\$C\$\d+:\$Q\$\d+),3\*\(C?\$?([A-Z]*)\$?6-1\)\+([A-Z0-9$]+)\)',f):
            idx.append((f'{s}!{a}',m.group(1),m.group(3)))
    if s=='Harness':
        lab=str(cells.get((s,f'A{x["r"]}'),{}).get('v'))
        for m in re.finditer(r'(Unit_Cost|Cache_Store)!\$?([A-Z]+)\$?\d+',f):
            exp={'M':'VR200','J':'GB300'}.get(m.group(2))
            if exp is None or exp not in lab: hard.append((f'{s}!{a}',m.group(0),lab[:30]))
ks=sorted({(i[1],i[2]) for i in idx})
json.dump(dict(mis=mis,index_k=ks,hard=hard),open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print('同欄不符',len(mis),mis[:10]); print('INDEX k',ks); print('Harness 寫死欄不符',len(hard),hard[:5])

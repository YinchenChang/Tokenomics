"""驗證 20_eval.py（第 2 段，未改）在 3B 441 列全部公式格：不覆寫重算，與檔內快取值比對。
用法：python3 21_validate.py <wb.pkl>"""
import sys,importlib.util,json
spec=importlib.util.spec_from_file_location('ev','docs/evidence/20261015_稽核2/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[1])
rows={(x['sh'],x['r']) for x in json.load(open('docs/evidence/20261015_稽核3B/00_rows.json'))}
tg=[k for k,x in b.cells.items() if (k[0],x['r']) in rows and isinstance(x['f'],str) and x['f'].startswith('=')]
bad=[]
for k in tg:
    v=b.get(*k); c=b.cells[k]['v']
    if isinstance(c,bool) or isinstance(v,bool): ok=bool(v)==bool(c)
    elif isinstance(c,(int,float)): ok=isinstance(v,(int,float)) and abs(v-c)<=1e-9*max(1,abs(c))
    else: ok=(v==c)
    if not ok: bad.append((k,v,c))
fb=sorted({e for _,e in b.fallback})
print('fallback 函數',fb,'格數',len(b.fallback),[k for k,_ in b.fallback if (k[0],b.cells[k]['r']) in rows][:10])
print('3B 公式格',len(tg),'不一致',len(bad))
for x in bad[:30]: print(x)
json.dump(dict(n=len(tg),bad=[str(x) for x in bad],fallback=fb),open('docs/evidence/20261015_稽核3B/21_validate.json','w'),ensure_ascii=False,indent=1)

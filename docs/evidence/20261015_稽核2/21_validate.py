"""驗證 20_eval.py：對 m 路徑全部公式格與 S3 目標格，以不覆寫的方式重算，與檔內快取值比對。"""
import sys,importlib.util,pickle
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2]); M=pickle.load(open(sys.argv[3],'rb'))
rows={(x['sheet'],x['row']) for x in M['rows']}
tg=[k for k,x in b.cells.items() if (k[0],x['r']) in rows and isinstance(x['f'],str) and x['f'].startswith('=')]
bad=[]
for k in tg:
    v=b.get(*k); c=b.cells[k]['v']
    ok=(v==c) if not isinstance(c,(int,float)) or isinstance(c,bool) else (isinstance(v,(int,float)) and not isinstance(v,bool) and abs(v-c)<=1e-9*max(1,abs(c)))
    if isinstance(c,bool) or isinstance(v,bool): ok = bool(v)==bool(c)
    if not ok: bad.append((k,v,c))
print('fallback',sorted({e for _,e in b.fallback}),len(b.fallback)); print('m 路徑公式格',len(tg),'不一致',len(bad),'已求值格',len(b.memo))
for x in bad[:20]: print(x)

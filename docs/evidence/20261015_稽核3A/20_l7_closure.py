"""3A：(a) L7 端點情境下 3A 列的錯誤值／文字／變 0；(b) Amortize 由上而下總額 vs 訓練 GW × 持有成本 的閉合；
(c) 只顯示的檢查列是否被 Checks 引用。沿用第 2 段 20_eval.py（工作簿公式原文求值）。
用法：python3 20_l7_closure.py <evdir2> <wb.pkl> <graph.pkl> <rows.json> <out.json>"""
import sys,importlib.util,pickle,json,re,collections
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2]);G=pickle.load(open(sys.argv[3],'rb'));ROWS=json.load(open(sys.argv[4]))
rs={(x['sheet'],x['row']) for x in ROWS}
col=lambda a:re.match('[A-Z]+',a).group()
tg=[k for k,x in b.cells.items() if (k[0],x['r']) in rs and isinstance(x['f'],str) and x['f'].startswith('=') and not(k[0]=='Interface' and col(k[1]) in 'RSTUVWXY')]
# 驗證：不覆寫時與快取值一致
b.set({});bad=[]
for k in tg:
    v=b.get(*k);cv=b.cells[k]['v']
    if isinstance(v,(int,float)) and isinstance(cv,(int,float)) and not isinstance(v,bool):
        if abs(v-cv)>1e-9*max(1,abs(cv)): bad.append((k,v,cv))
    elif str(v)!=str(cv) and not(v is None and cv in('',None)): bad.append((k,v,cv))
out=dict(n_target=len(tg),validate_mismatch=[f'{a}!{c}:{v}|{w}' for (a,c),v,w in bad[:30]],n_mismatch=len(bad),fallback=sorted({str(k) for k,_ in b.fallback}))
SCEN={'Serving!C18=0.7':{('Serving','C18'):0.7},'Arch!E8=160':{('Arch','E8'):160},'Calib!C68=3':{('Calib','C68'):3},'Serving!D21,E21=100':{('Serving','D21'):100,('Serving','E21'):100}}
for nm,ov in SCEN.items():
    b.set(ov);err=[];txt=set();zero=set()
    for k in tg:
        v=b.get(*k);c=b.cells[k]['v']
        if isinstance(v,str) and v.startswith('#'): err.append(f'{k[0]}!{k[1]}:{v}')
        elif isinstance(v,str) and isinstance(c,(int,float)) and not isinstance(c,bool): txt.add(f"{k[0]}!{re.sub('[A-Z]+','',k[1])}")
        elif isinstance(v,(int,float)) and not isinstance(v,bool) and v==0 and isinstance(c,(int,float)) and c!=0: zero.add(f"{k[0]}!{re.sub('[A-Z]+','',k[1])}")
    out[nm]=dict(err=err,txt=sorted(txt),zero=sorted(zero))
    print(nm,'err',len(err),err[:5],'\n  txt',sorted(txt)[:40],'\n  zero',sorted(zero))
b.set({})
# (b) 由上而下攤提閉合
cols='CDEFGHIJKLMNOPQ'
clo=[]
for k in cols:
    td=b.get('Amortize',f'{k}39')/1000  # $B/年
    tr=b.get('Fleet_1GW',f'{k}13')*b.get('Interface',f'{k}13')  # 訓練＋研發 GW × 經濟持有成本 $B/GW/年
    serve=sum(b.get('Amortize',f'{k}{r}')*b.get('Amortize',f'{k}{t}') for r,t in((14,11),(23,20),(33,30)))/1e6/1000
    sv=b.get('Fleet_1GW',f'{k}10')*b.get('Interface',f'{k}13')
    clo.append(dict(col=k,gen=b.cells[('Interface',f'{k}4')]['v'],TD_total_B=td,TrainGW_x_Hold_B=tr,ratio=td/tr,ServeCost_x_tok_B=serve,ServeGW_x_Hold_B=sv,serve_ratio=serve/sv,scale=b.get('Amortize',f'{k}41')))
    print(k,round(td,3),round(tr,3),'TD/(訓練GW×持有)',round(td/tr,3),'服務成本×token ÷ 服務GW×持有',round(serve/sv,3),'scale',round(b.get('Amortize',f'{k}41'),2))
out['closure']=clo
# (c) Checks／Gov 引用
rev=collections.defaultdict(set)
for n,ps in G['edges'].items():
    for p in ps: rev[p].add(n)
def users(node):
    o=set();st=[node];seen=set()
    while st:
        x=st.pop()
        for u in rev.get(x,()):
            if u in seen: continue
            seen.add(u)
            if u[0] in('NAME','RANGE'): st.append(u)
            else: o.add(u)
    return o
chk={}
for s,r in [('Perf',77),('Perf',90),('Perf',116),('Calib',86),('Calib',149),('Calib',150),('Calib',151),('Calib',152),('Fleet_1GW',30),('Fleet_1GW',34),('Interface',229),('Interface',289),('Interface',300),('Price_Frontier',33)]:
    us=set()
    for k,x in b.cells.items():
        if k[0]==s and x['r']==r: us|=users(k)
    chk[f'{s}!{r}']=sorted({u[0]+'!'+u[1] for u in us})[:8]
    print('users',s,r,chk[f'{s}!{r}'])
out['check_users']=chk
json.dump(out,open(sys.argv[5],'w'),ensure_ascii=False,indent=1,default=str)
print('validate targets',len(tg),'mismatch',len(bad),bad[:5])

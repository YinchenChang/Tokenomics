"""報告用替代讀法（只重組工作簿數值，不是工作簿機制；不新增公式到活頁簿）：
(a) G02：以付費 token 為分母時的自下而上攤提與全成本變化；(b) G01：由上而下總額閉合到「訓練 GW × 持有成本」時的攤提變化；
(c) G06：L7 情境下變文字或變 0 的下游契約名稱數。用法：python3 33_alt.py <wb.pkl> <20_l7_closure.json> <out.json>"""
import pickle,sys,json,re
d=pickle.load(open(sys.argv[1],'rb'));c=d['cells'];n=d['names'];L7=json.load(open(sys.argv[2]))
v=lambda s,a:c[(s,a)]['v']
out={}
alt=[]
for k in 'DGJMP':
    g=v('Interface',f'{k}4').split('（')[0]
    for t,(p,f,bu,ifbu,full,dflt,fulld) in {'Luna':(21,22,13,95,97,98,100),'Sol':(24,25,22,113,115,116,118),'Astra':(27,28,32,131,133,134,136)}.items():
        r=(v('Fleet_1GW',f'{k}{p}')+v('Fleet_1GW',f'{k}{f}'))/v('Fleet_1GW',f'{k}{p}')
        BU=v('Interface',f'{k}{ifbu}');FC=v('Interface',f'{k}{full}');DF=v('Interface',f'{k}{dflt}');FD=v('Interface',f'{k}{fulld}')
        alt.append(dict(gen=g,tier=t,ratio=r,BU=BU,BU_paid=BU*r,FullCost=FC,FullCost_paid=FC+BU*(r-1),FullCostDefault=FD,FullCostDefault_paid=FD+DF*(r-1)))
out['G02']=alt
clo=[]
for k in 'DGJMP':
    td=v('Amortize',f'{k}39')/1000;tr=v('Fleet_1GW',f'{k}13')*v('Interface',f'{k}13')
    clo.append(dict(gen=v('Interface',f'{k}4').split('（')[0],ratio=td/tr,amort_up_pct=(tr/td-1)*100))
out['G01']=clo
# 契約名稱（IF_／IFW_／L1_）落在 Interface 哪些列
rows={}
for nm,t in n.items():
    m=re.match(r"=?Interface!\$C\$(\d+):\$Q\$\d+$",t)
    if m and re.match(r'(IF_|IFW_)',nm): rows[int(m.group(1))]=nm
cnt={}
for sc,o in L7.items():
    if not isinstance(o,dict) or 'txt' not in o: continue
    tx=[rows[int(x.split('!')[1])] for x in o['txt'] if x.startswith('Interface!') and int(x.split('!')[1]) in rows]
    zr=[rows[int(x.split('!')[1])] for x in o['zero'] if x.startswith('Interface!') and int(x.split('!')[1]) in rows]
    cnt[sc]=dict(text=sorted(tx),zero=sorted(zr))
out['G06']=cnt
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False,indent=1)
for a in alt:
    if a['gen'].startswith(('Hopper','VR200')): print(a['gen'][:6],a['tier'],round(a['ratio'],2),'FullCost',round(a['FullCost'],4),'->',round(a['FullCost_paid'],4),f"{(a['FullCost_paid']/a['FullCost']-1)*100:+.0f}%",'FCDefault',f"{(a['FullCostDefault_paid']/a['FullCostDefault']-1)*100:+.0f}%")
print(clo)
for sc,o in cnt.items(): print(sc,'text',len(o['text']),o['text'][:6],'zero',len(o['zero']),o['zero'][:6])

"""3B 補充量化（只讀；用工作簿公式值與 20_eval.py 重算，不新增機制，只做替代口徑的算術對照）：
(1) Q1、隱含 N×k 改用支出路線服務 GW（Alloc C61）；(2) L1_PriceReqBE 的損益兩平乘積改用各世代與 2025 組合；
(3) L_total 以 WACC 10% 現值加權；(4) 批次 SLO 不可達時 Training 的 0 值（Train_In E31）；(5) p_min 門檻（Har_In C8）；
(6) Q1 若研發端 × L1_ScaleRD、服務端用支出路線。用法：python3 31_extra.py <wb.pkl> <out.json>"""
import sys,importlib.util,json,math
spec=importlib.util.spec_from_file_location('ev','docs/evidence/20261015_稽核2/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[1]); g=b.get; out={}
rd=g('Alloc','C41'); sg=g('Alloc','C28'); sp=g('Alloc','C61'); fam=g('Alloc','F37'); ratio=g('Alloc','C55')
out['Q1']=dict(token_route=rd/(rd+sg),spend_route=rd/(rd+sp),ServeGW_token=sg,ServeGW_spend=sp,RDGW=rd)
out['ImpliedNk']=dict(token_route=g('Alloc','C57'),spend_route=ratio/(1-ratio)*sp/fam)
out['Q1_scaled']=dict(RDGW_x_ScaleRD=rd*g('L1','D68'),Q1=rd*g('L1','D68')/(rd*g('L1','D68')+sp),spend_ratio=ratio)
util=g('Interface','C48'); der=g('Serving','C28'); price=g('Cap_In','C90'); L=g('L1','D88')
pr={}
for name,c in (('Hopper','D'),('GB200','G'),('GB300','J'),('VR200','M')):
    he=g('Theory_Rev',f'{c}72'); rv=g('Theory_Rev',f'{c}67'); be=he/(rv/util)
    pr[name]=dict(breakeven=be,req_price=be/(util*der)*price/L)
he=0.6*g('Theory_Rev','D72')+0.4*g('Theory_Rev','G72'); rv=0.6*g('Theory_Rev','D67')+0.4*g('Theory_Rev','G67'); be=he/(rv/util)
pr['2025 組合 0.6／0.4']=dict(breakeven=be,req_price=be/(util*der)*price/L)
pr['機隊實收（L1 M93）']=g('L1','M93'); pr['工作簿 L1_PriceReqBE']=g('L1','D93'); pr['工作簿 L1_FleetBreakeven']=g('L1','D52')
out['PriceReqBE']=pr
gg=g('Cap_In','C226');T=g('Cap_In','C229');T1=g('Cap_In','C227');rho=g('Cap_In','C228')
def avg(w,N=20000):
    s=ws=0
    for i in range(N):
        t=(i+0.5)/N*T; p=(1+gg)**t*(1 if t<T1 else rho); s+=p*w(t); ws+=w(t)
    return s/ws
out['L_total']=dict(workbook=g('Cap_In','C233'),undiscounted_check=avg(lambda t:1),pv_wacc10=avg(lambda t:1.1**(-t)))
cols='CDEFGHIJKLMNOPQ'
z={}
for v in (20,40,60,80,100,150):
    b.set({('Train_In','E31'):v})
    z[v]=dict(PB103_Astra=[b.get('Perf_Batch',f'{c}103') for c in 'EHKNQ'],RLGPUh_Astra=[b.get('Training',f'{c}75') for c in 'EHKNQ'],
              Q1=b.get('Interface','C195'),L1_RLshare_Astra=b.get('L1','D33'),SynthGPUh_VR=[b.get('Training',f'{c}97') for c in 'LMN'])
b.set({}); out['batchSLO_zero']=z
pm={}
for v in (0.3,0.4,0.5,0.6):
    b.set({('Har_In','C8'):v}); pm[v]=dict(front=b.get('Interface','G190'),name=b.get('Harness','G152'),p=b.get('Harness','G153'))
b.set({}); out['pmin']=pm
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1,default=str)
print(json.dumps({k:v for k,v in out.items() if k!='batchSLO_zero'},ensure_ascii=False,indent=0,default=str)[:3000])
for v,x in z.items(): print(v,[round(y) if isinstance(y,float) else y for y in x['PB103_Astra']],round(x['Q1'],4) if isinstance(x['Q1'],float) else x['Q1'],round(x['L1_RLshare_Astra'],3))

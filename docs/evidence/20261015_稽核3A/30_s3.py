"""3A 傳遞強度：高嚴重度項目 → 下游契約名稱（IF_／IFW_／L1_）。
(1) 結構量（不擾動）：由上而下攤提閉合比、自下而上分母（付費＋免費）÷ 付費、_Prod 層兩種折減比、兩種 _Life 比、Calib G 節 η_d 隨 η_p。
(2) 單一輸入取 Gov_Map 區間端點，其他不變，以第 2 段 20_eval.py（工作簿公式原文求值）重算契約名稱。只讀；不新增機制。
用法：python3 30_s3.py <evdir2> <wb.pkl> <out.json>"""
import sys,importlib.util,json
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2])
G=lambda s,a:b.get(s,a)
COLS='CDEFGHIJKLMNOPQ'
gen=lambda k:b.cells[('Interface',f'{k}4')]['v'].split('（')[0]+'｜'+b.cells[('Unit_Cost',f'{k}5')]['v']
out={}
b.set({})
# (1a) 由上而下攤提閉合
out['closure_TD']=[dict(col=k,gen=gen(k),TD_B=G('Amortize',f'{k}39')/1000,TrainGW_Hold_B=G('Fleet_1GW',f'{k}13')*G('Interface',f'{k}13'),
    ratio=G('Amortize',f'{k}39')/1000/(G('Fleet_1GW',f'{k}13')*G('Interface',f'{k}13')),scale=G('Amortize',f'{k}41')) for k in COLS]
# (1b) 自下而上分母：(付費＋免費) ÷ 付費
pf={}
for t,(p,f) in {'Luna':(21,22),'Sol':(24,25),'Astra':(27,28)}.items():
    pf[t]={k:(G('Fleet_1GW',f'{k}{p}')+G('Fleet_1GW',f'{k}{f}'))/G('Fleet_1GW',f'{k}{p}') for k in 'DGJMP'}
out['BU_denominator_ratio']=pf
# (1c) _Prod 兩種折減
prod={}
for nm,(u,p) in {'IFW_RevGW_Luna':(234,235),'IFW_RevGW_Sol':(239,240),'IFW_RevGW_Astra':(244,245),'IFW_RevGWFleet':(249,250),'IFW_TokGW_Luna':(274,275),'IFW_TokGW_Sol':(279,280),'IFW_TokGW_Astra':(284,285)}.items():
    prod[nm]={gen(k):G('Interface',f'{k}{p}')/G('Interface',f'{k}{u}') for k in 'DGJMP'}
out['Prod_over_Util']=prod
# (1d) 兩種 _Life
out['Life_IF_vs_IFW']={nm:{gen(k):G('Interface',f'{k}{a}')/G('Interface',f'{k}{c}') for k in 'DGJMP'} for nm,(a,c) in {'IFW_RevGW_Luna_Life÷IF_RevGW_Luna_Life':(236,213),'IFW_RevGW_Sol_Life÷IF_RevGW_Sol_Life':(241,214),'IFW_RevGW_Astra_Life÷IF_RevGW_Astra_Life':(246,215),'IFW_RevGWFleet_Life÷IF_RevGWFleet_Life':(251,216)}.items()}
# (1e) Calib G 節
out['Calib_G']={str(G('Calib',f'{k}90')):dict(eta_d=G('Calib',f'{k}95'),layer_us=G('Calib',f'{k}96')) for k in 'CDE'}
# (2) 端點擾動
MET=[('IF_TokGW_Sol（VR200）','Interface','M31'),('IF_CostDec_Sol（VR200 基準）','Interface','M35'),('IF_CostPre_Sol（VR200 基準）','Interface','M33'),
 ('IF_AmortBU_Sol（VR200 基準）','Interface','M113'),('IF_AmortTD_Sol（VR200 基準）','Interface','M114'),('IF_FullCost_Sol（VR200 基準）','Interface','M115'),
 ('IF_AmortDefault_Sol（VR200 基準）','Interface','M116'),('IF_FullCostDefault_Sol（VR200 基準）','Interface','M118'),
 ('IF_AmortBU_Luna（Hopper 基準）','Interface','D95'),('IF_FullCostDefault_Luna（Hopper 基準）','Interface','D100'),
 ('IFW_TokGW_Sol_Prod（VR200）','Interface','M280'),('IFW_RevGW_Sol_Prod（VR200）','Interface','M240'),('IFW_RevGWFleet_Prod（Hopper 基準）','Interface','D250'),
 ('IFW_RevGWFleet_Prod（VR200 基準）','Interface','M250'),('IF_TrainGPUh_Sol（VR200）','Interface','M63'),('IF_ProgCost_Sol（VR200 基準）','Interface','M69'),
 ('IF_TokPerJ_Sol（VR200）','Interface','M37'),('L1_TokMW_Gen_ratio_VR200','L1','D60'),('L1_TokMW_Gen_ratio_GB200','L1','D58'),('縮放倍數 Amortize!M41','Amortize','M41')]
def read(): return {n:G(s,a) for n,s,a in MET}
base=read(); out['base']=base
SC=[('A01／Y11 快取命中 χ（Cap_In C13）',{('Cap_In','C13'):0.3},{('Cap_In','C13'):0.75},'0.3／0.75'),
 ('A02／Y11 對外服務占機隊（Cap_In C28）',{('Cap_In','C28'):0.3},{('Cap_In','C28'):0.6},'0.3／0.6'),
 ('A03／Y11 免費占服務（Cap_In C29）',{('Cap_In','C29'):0.35},{('Cap_In','C29'):0.6},'0.35／0.6'),
 ('A02 研發倍數（Train_In C13）',{('Train_In','C13'):4.4},{('Train_In','C13'):10.4},'4.4／10.4'),
 ('A04／Y10 生產折減（Serving C28）',{('Serving','C28'):0.7},{('Serving','C28'):1.0},'0.7／1.0'),
 ('A06／Y12 η_p（Calib C5）',{('Calib','C5'):0.15},{('Calib','C5'):0.45},'0.15／0.45'),
 ('A10／Y12 批次口徑 η_d 倍數 VR200（Calib F156）',{('Calib','F156'):0.7},{('Calib','F156'):1.0},'0.7／1.0'),
 ('A12 儲存層（Cap_In C36）',{('Cap_In','C36'):1},{('Cap_In','C36'):3},'1 SSD／3 HBM'),
 ('A13 運算功率比例（Energy C5）',{('Energy','C5'):0.4},{('Energy','C5'):0.8},'0.4／0.8'),
 ('A07 平均用電 ÷ 設計功率（Inputs E10）',{('Inputs','E10'):0.7},{('Inputs','E10'):0.9},'0.7／0.9')]
res=[]
def pct(x,y):
    if isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool) and y: return (x/y-1)*100
    return None
for nm,lo,hi,ep in SC:
    b.set(lo); L=read(); b.set(hi); H=read(); b.set({})
    sw={n:(pct(L[n],base[n]),pct(H[n],base[n])) for n,_,_ in MET}
    res.append(dict(item=nm,endpoints=ep,swing=sw))
    print(nm,ep,{n:('/'.join('—' if v is None else f'{v:+.1f}' for v in s)) for n,s in sw.items() if any(v and abs(v)>0.05 for v in s)})
out['perturb']=res
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False,indent=1,default=str)
for k in ['closure_TD']: print([ (x['gen'],round(x['ratio'],3),round(x['scale'],2)) for x in out[k]][::3])
print('BU ratio',{t:{k:round(v,2) for k,v in d.items()} for t,d in pf.items()})
print('Prod',{n:{k:round(v,3) for k,v in d.items()} for n,d in prod.items()})
print('Life',{n:{k:round(v,3) for k,v in d.items()} for n,d in out['Life_IF_vs_IFW'].items()})
print('CalibG',out['Calib_G'])

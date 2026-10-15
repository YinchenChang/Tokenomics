"""3B 傳遞強度：嚴重度「高」各項的輸入，單一擾動到工作簿內的區間端點（Gov_Map 低高、Sens_Train／Sens_Har 情境倍數或
工作表內明列的區間），其餘不變；以第 2 段 20_eval.py（工作簿公式原文求值，未改）重算下游契約名稱。只讀，不新增機制。
用法：python3 30_s3.py <wb.pkl> <out.json>"""
import sys,importlib.util,json
spec=importlib.util.spec_from_file_location('ev','docs/evidence/20261015_稽核2/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[1])
T=[('IF_AllocQ1','Interface','C195'),('IF_AllocQ2','Interface','C197'),('IF_AllocRDGW','Interface','C199'),('IF_AllocImpliedNk','Interface','C201'),
   ('L1_Ans3（研發算力成本）','L1','D39'),('L1_ScaleRD','L1','D68'),('IF_ProgGWyr_Astra（VR200）','Interface','N79'),
   ('IF_PostShareGPUh_Sol（VR200）','Interface','M66'),('IF_AmortBU_Sol（VR200）','Interface','M113'),('IF_FullCostDefault_Sol（VR200）','Interface','M118'),
   ('L1_RLshare_Astra_VR200','L1','D33'),('L1_AstraScale','L1','D67'),
   ('IF_HarR_Sol（Coding）','Interface','G174'),('IF_FrontSuccVR（Coding）','Interface','G190'),('IF_CostSuccVR_Sol（Coding）','Interface','G171'),
   ('L1_PriceReqBE','L1','D93'),('L1_FleetBreakeven','L1','D52'),('L1_TokMW_Gen_ratio_VR200','L1','D60')]
def read(): return {n:b.get(s,a) for n,s,a in T}
def sc(cells,val): return {c:val for c in cells}
def mul(cells,k): return {c:b.cells[c]['v']*k for c in cells}
TI=lambda *cs:[('Train_In',c) for c in cs]
HI=lambda *cs:[('Har_In',c) for c in cs]
S=[  # (編號, 說明, 端點說明, lo 覆寫, hi 覆寫)
 ('H01','訓練世代（Train_In C16；基準 4＝VR200）','1 Hopper／2 GB200',{('Train_In','C16'):1},{('Train_In','C16'):2}),
 ('H01b','訓練世代（Train_In C16）','3 GB300／5 RU',{('Train_In','C16'):3},{('Train_In','C16'):5}),
 ('H02','RL rollout 輸出 token（Train_In C34:E34）','× 0.3／× 3（Sens_Train 情境倍數）',mul(TI('C34','D34','E34'),0.3),mul(TI('C34','D34','E34'),3)),
 ('H03','研發倍數（Train_In C13）','4.4／10.4（Gov_Map）',{('Train_In','C13'):4.4},{('Train_In','C13'):10.4}),
 ('H04','Astra 預訓練 token（Train_In E25）','30／100 T（列內區間）',{('Train_In','E25'):30},{('Train_In','E25'):100}),
 ('H05','預訓練 MFU（Train_In C6）','0.18／0.35（Gov_Map）',{('Train_In','C6'):0.18},{('Train_In','C6'):0.35}),
 ('H05b','goodput（Train_In C7）','0.80／0.95（列內區間）',{('Train_In','C7'):0.8},{('Train_In','C7'):0.95}),
 ('H05c','rollout 效率（Train_In C11）','0.6／0.95（Gov_Map）',{('Train_In','C11'):0.6},{('Train_In','C11'):0.95}),
 ('H05d','RL trainer MFU 係數（Train_In C9）','0.4／0.9（列內區間）',{('Train_In','C9'):0.4},{('Train_In','C9'):0.9}),
 ('H05e','MFU 世代倍數 VR200（Train_In F21）','0.7／1.1（列內區間）',{('Train_In','F21'):0.7},{('Train_In','F21'):1.1}),
 ('H06','基準利用率 IF_Util（Serving C17）','0.4／0.8（Gov_Map）',{('Serving','C17'):0.4},{('Serving','C17'):0.8}),
 ('H07','合成資料生成層級（Train_In C15）','2 Sol／（基準 3）',{('Train_In','C15'):2},None),
 ('H07b','合成資料 token（Train_In C37:E37）','0.5 T／10 T（列內區間；三層級同設）',sc(TI('C37','D37','E37'),0.5),sc(TI('C37','D37','E37'),10)),
 ('H08','家族計畫數 N_major（Alloc_In C6）','1／2',{('Alloc_In','C6'):1},{('Alloc_In','C6'):2}),
 ('H08b','改版計畫數 N_refresh（Alloc_In C7）','0／6',{('Alloc_In','C7'):0},{('Alloc_In','C7'):6}),
 ('H08c','計畫規模倍數 k（Alloc_In C8）','0.5／7',{('Alloc_In','C8'):0.5},{('Alloc_In','C8'):7}),
 ('H09','輪數倍數（選定檔案，Har_In E12:G12）','0.5／1（Har_In 第 61 列）',sc(HI('E12','F12','G12'),0.5),sc(HI('E12','F12','G12'),1)),
 ('H09b','時間範圍倍數（選定檔案，Har_In E19:G19）','1／4（Har_In 第 65 列）',sc(HI('E19','F19','G19'),1),sc(HI('E19','F19','G19'),4)),
 ('H09c','斜率 β（Har_In C51）','0.65／1（同列 D、E）',{('Har_In','C51'):0.65},{('Har_In','C51'):1}),
 ('H09d','50% 時間範圍（Har_In C48:E48）','低／高列（Har_In 第 49、50 列）',{('Har_In','C48'):0.5,('Har_In','D48'):4,('Har_In','E48'):11},{('Har_In','C48'):4,('Har_In','D48'):12,('Har_In','E48'):40}),
 ('H09e','歷史保留比 c（選定，Har_In E15:G15）','0.5／1（Har_In 第 64 列）',sc(HI('E15','F15','G15'),0.5),sc(HI('E15','F15','G15'),1)),
 ('H10','服務世代組合（Alloc_In C9:C12）','全 GB200／全 VR200（Alloc 第 85、86 列的端點）',{('Alloc_In','C9'):0,('Alloc_In','C10'):1,('Alloc_In','C11'):0,('Alloc_In','C12'):0},{('Alloc_In','C9'):0,('Alloc_In','C10'):0,('Alloc_In','C11'):0,('Alloc_In','C12'):1}),
]
b.set({}); base=read()
def pct(x,y):
    if isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool) and y: return (x/y-1)*100
    return None
res=[]
for sid,lab,ep,lo,hi in S:
    rec=dict(id=sid,label=lab,endpoints=ep,vals={},pct={})
    for tag,ov in (('lo',lo),('hi',hi)):
        if ov is None: continue
        b.set(ov); v=read(); rec['vals'][tag]=v; rec['pct'][tag]={k:pct(v[k],base[k]) for k in v}
    b.set({}); res.append(rec)
json.dump(dict(base=base,res=res),open(sys.argv[2],'w'),ensure_ascii=False,indent=1,default=str)
print({k:(round(v,4) if isinstance(v,float) else v) for k,v in base.items()})
for r in res:
    out=[]
    for n,_,_ in T:
        lo=r['pct'].get('lo',{}).get(n); hi=r['pct'].get('hi',{}).get(n)
        if (lo is None or abs(lo)<0.05) and (hi is None or abs(hi)<0.05): continue
        f=lambda x:'—' if x is None else f'{x:+.1f}'
        out.append(f'{n} {f(lo)}/{f(hi)}')
    print(r['id'],r['label'][:22],'|','; '.join(out))

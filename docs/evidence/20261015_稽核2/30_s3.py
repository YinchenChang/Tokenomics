"""S3 傳遞強度：第 1 段 m 路徑「高」嚴重度輸入（同一列合併），單一輸入取 Gov_Map 區間端點、其他不變，
用 20_eval.py（工作簿公式原文求值）重算 m 指標。只讀；不新增機制。
用法：python3 30_s3.py <evdir> <wb.pkl> <稽核1明細.xlsx> <out.json>"""
import sys,importlib.util,json,collections,re,openpyxl
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2])
wb=openpyxl.load_workbook(sys.argv[3],read_only=True)
hi=[r for r in wb['高嚴重度'].iter_rows(min_row=3,values_only=True) if r[16]=='是']
sysrows=list(wb['系統性問題'].iter_rows(min_row=3,values_only=True))
ymap=collections.defaultdict(set)
for r in sysrows:
    for part in str(r[6]).split('；'):
        if '!' not in part: continue
        sh,cs=part.split('!',1)
        for c in cs.split(','): ymap[(sh.strip(),c.strip())].add(r[0])
METRICS=[('L1_MImplied','L1','D76'),('L1_MFleet','L1','D78'),('L1_MAPI','L1','D80'),('m 下限（Cap_In C121）','Cap_In','C121'),
 ('缺口＝機隊÷需求（1÷Cap_In C174）','Cap_In','C174'),('L1_GapProduct','L1','D74'),('L1_ScaleServe','L1','D69'),('L1_LReqFleet','L1','D89'),
 ('L1_FleetBreakeven','L1','D52'),('IFW_RevGWFleet_Life（VR200 基準）','Interface','M251')]
def read():
    out={}
    for n,s,a in METRICS:
        v=b.get(s,a)
        if n.startswith('缺口') and isinstance(v,(int,float)): v=1/v
        out[n]=v
    return out
b.set({}); base=read()
# 依列合併
groups=collections.OrderedDict()
for r in hi:
    groups.setdefault((r[1],re.sub('[A-Z]','',r[2])),[]).append(r)
res=[]
for (sh,row),rs in groups.items():
    cells=[(r[2],r[5],r[8],r[9]) for r in rs]
    # 以有低高的格為「本列的被擾動格」；本身為端點（低高空白）者不擾動
    pert=[(c,v,lo,hi_) for c,v,lo,hi_ in cells if lo is not None and hi_ is not None]
    ys=sorted(set().union(*[ymap.get((sh,c),set()) for c,_,_,_ in cells]))
    lab=rs[0][3]
    rec=dict(sheet=sh,row=int(row),label=lab,cells=','.join(c for c,_,_,_ in cells),Y=','.join(ys),pert=','.join(c for c,_,_,_ in pert))
    if sh=='Alloc_In' and row in('9','10','11'):
        g={'9':'C9','10':'C10','11':'C11'}[row]
        lo={('Alloc_In','C9'):0.0,('Alloc_In','C10'):0.0,('Alloc_In','C11'):0.0,('Alloc_In','C12'):0.0}
        hi1=dict(lo); hi1[('Alloc_In',g)]=1.0
        lo1={('Alloc_In','C9'):0.6,('Alloc_In','C10'):0.4,('Alloc_In','C11'):0.0,('Alloc_In','C12'):0.0}
        # 低端＝本世代 0、其餘按原比例放大；高端＝本世代 100%
        base_mix={'C9':0.6,'C10':0.4,'C11':0.0,'C12':0.0}
        rest=sum(v for k,v in base_mix.items() if k!=g)
        lo2={('Alloc_In',k):(0.0 if k==g else (v/rest if rest>0 else 0)) for k,v in base_mix.items()}
        if base_mix[g]==0: lo2=None
        rec['endpoint_lo']='本世代 0%（其餘依原比例放大至 100%）' if lo2 else '＝基準（基準即 0%）'
        rec['endpoint_hi']='本世代 100%（其餘 0%）'
        scen=[('lo',lo2),('hi',hi1)]
        rec['note']='組合須合計 100%，端點以「本世代 0%／100%」表示（Gov_Map 區間 0–1）'
    elif not pert:
        rec['note']='無法定量：本列格在 Gov_Map 沒有數值低高（本身為端點格或無區間）'
        res.append(rec); continue
    else:
        scen=[('lo',{(sh,c):lo for c,v,lo,hi_ in pert}),('hi',{(sh,c):hi_ for c,v,lo,hi_ in pert})]
        rec['endpoint_lo']='；'.join(f'{c}={lo}' for c,v,lo,hi_ in pert); rec['endpoint_hi']='；'.join(f'{c}={hi_}' for c,v,lo,hi_ in pert)
        rec['base']='；'.join(f'{c}={v}' for c,v,lo,hi_ in pert)
    for tag,ov in scen:
        if ov is None: rec[tag]=None; continue
        b.set(ov); rec[tag]=read()
    b.set({})
    res.append(rec)
def pct(x,y):
    if isinstance(x,(int,float)) and isinstance(y,(int,float)) and not isinstance(x,bool): return (x/y-1)*100 if y else None
    return None
for r in res:
    sw={}
    for n,_,_ in METRICS:
        lo=(r.get('lo') or {}).get(n); hi_=(r.get('hi') or {}).get(n)
        sw[n]=(pct(lo,base[n]),pct(hi_,base[n]),lo,hi_)
    r['swing']=sw
    mf=[abs(v) for k in('L1_MImplied','L1_MFleet') for v in sw[k][:2] if v is not None]
    r['max_m_pct']=max(mf) if mf else None
    life=[abs(v) for v in sw['IFW_RevGWFleet_Life（VR200 基準）'][:2] if v is not None]
    r['max_life_pct']=max(life) if life else None
json.dump(dict(base=base,res=res,fallback=sorted({str(k) for k,_ in b.fallback})),open(sys.argv[4],'w'),ensure_ascii=False,indent=1,default=str)
rank=sorted(res,key=lambda r:-(max(r['max_m_pct'] or 0,r['max_life_pct'] or 0)))
print('base',{k:(round(v,4) if isinstance(v,float) else v) for k,v in base.items()})
for r in rank:
    s=r['swing']
    f=lambda n:'/'.join('—' if v is None else f'{v:+.1f}' for v in s[n][:2]) if 'swing' in r else ''
    print(f"{r['sheet']}!{r['row']} {r['label'][:16]} Y={r['Y']} | MImp {f('L1_MImplied')} | MFleet {f('L1_MFleet')} | MAPI {f('L1_MAPI')} | gap {f('缺口＝機隊÷需求（1÷Cap_In C174）')} | GapProd {f('L1_GapProduct')} | LReq {f('L1_LReqFleet')} | Life {f('IFW_RevGWFleet_Life（VR200 基準）')} {r.get('note','')}")

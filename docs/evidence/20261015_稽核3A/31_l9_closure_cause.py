"""3A：(a) L9 物理合理性表（Perf 15 欄；由工作簿值計算的衍生物理量，不新增機制）；
(b) 由上而下攤提閉合比 < 1 的原因測試（χ＝0、儲存層＝SSD 時重算）。用法：python3 31_l9_closure_cause.py <evdir2> <wb.pkl> <out.json>"""
import sys,importlib.util,json
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2]);G=b.get;COLS='CDEFGHIJKLMNOPQ'
rows=[]
for k in COLS:
    g=G('Perf',f'{k}4');t=G('Perf',f'{k}5')
    peak=G('Perf',f'{k}14')*1e15;bw=G('Perf',f'{k}16')*1e12
    dec=G('Perf',f'{k}88');pre=G('Perf',f'{k}75');B=G('Perf',f'{k}87')
    acc=G('Perf',f'{k}49');dr=G('Perf',f'{k}47')
    fl_d=G('Perf',f'{k}65')*1e9;fl_p=G('Perf',f'{k}67')*1e9
    mfu_d=dec*fl_d*(dr+1)/acc/peak
    mfu_p=pre*fl_p/peak
    hbm=dec*G('Perf',f'{k}110')*1e9/bw if isinstance(G('Perf',f'{k}110'),float) else None
    rows.append(dict(col=k,gen=g,tier=t,B_star=B,decode_tok_s_gpu=dec,prefill_tok_s_gpu=pre,user_speed=G('Perf',f'{k}89'),
        decode_MFU_incl_draft=mfu_d,prefill_MFU=mfu_p,decode_HBM_BW_util=hbm,TTFT_s=G('Perf',f'{k}76'),TTFT_ok=G('Perf',f'{k}77'),
        rack_tok_s=G('Perf',f'{k}95'),tok_per_J=G('Perf',f'{k}117'),J_per_decode_tok=G('Perf',f'{k}118'),closure_ratio=G('Perf',f'{k}116'),
        rack_kW_avg=G('Perf',f'{k}115'),weights_share_HBM=G('Perf',f'{k}73')))
for r in rows: print(r['gen'][:12],r['tier'][:4],'B*',round(r['B_star'],2),'dec/GPU',round(r['decode_tok_s_gpu']),'MFUd',f"{r['decode_MFU_incl_draft']:.3%}",'MFUp',f"{r['prefill_MFU']:.1%}",'HBMbw',f"{r['decode_HBM_BW_util']:.1%}",'tok/J',round(r['tok_per_J'],2),'J/dec',round(r['J_per_decode_tok'],3),'close',f"{r['closure_ratio']:.1%}")
def clo(ov):
    b.set(ov);o=[]
    for k in 'DGJMP':
        o.append(round(G('Amortize',f'{k}39')/1000/(G('Fleet_1GW',f'{k}13')*G('Interface',f'{k}13')),4))
    b.set({});return o
cause=dict(base=clo({}),chi0=clo({('Cap_In','C13'):0.0}),chi0_ssd=clo({('Cap_In','C13'):0.0,('Cap_In','C36'):1}))
print(cause)
json.dump(dict(L9=rows,closure_cause=cause),open(sys.argv[3],'w'),ensure_ascii=False,indent=1,default=str)

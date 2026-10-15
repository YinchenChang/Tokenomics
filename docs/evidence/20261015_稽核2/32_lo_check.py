"""以 LibreOffice headless 重算 3 個端點情境（複本放 docs/evidence/20261015_稽核2/lo/，不碰 model/），
與 20_eval.py 結果比對，驗證 S3 的 Python 求值。重算 3 次。"""
import sys,shutil,json,importlib.util,time
sys.path.insert(0,'tests/parity')
import parity_lib as P
from pathlib import Path
spec=importlib.util.spec_from_file_location('ev','docs/evidence/20261015_稽核2/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[1])
SRC=Path('model/20261015_Tokenomics_v5.36.xlsx'); D=Path('docs/evidence/20261015_稽核2/lo')
SC={'s1_spendbasis_lo':{'Alloc_In!C23':1.0},'s2_arch_e7_lo':{'Arch!E7':60},'s3_derate_07':{'Serving!C18':0.7}}
T=[('L1',f'D{r}') for r in (52,69,70,74,76,78,80,84,89)]+[('Cap_In','C121'),('Cap_In','C174'),('Interface','M251'),('Interface','E143'),('Alloc','C24')]
out={}
for nm,inp in SC.items():
    t=time.time()
    src=D/f'{nm}.xlsx'; P.set_inputs(SRC,src,inp)
    rec=P.lo_recalc(src,D/'out')
    lv=P.excel_values(rec,T)
    b.set({tuple(k.split('!')):v for k,v in inp.items()})
    pv={k:b.get(*k) for k in T}
    diff=[(f'{s}!{a}',pv[(s,a)],lv[(s,a)]) for s,a in T if not ((pv[(s,a)]==lv[(s,a)]) or (isinstance(pv[(s,a)],(int,float)) and isinstance(lv[(s,a)],(int,float)) and abs(pv[(s,a)]-lv[(s,a)])<=1e-9*max(1,abs(lv[(s,a)]))))]
    out[nm]=dict(inputs=inp,seconds=round(time.time()-t,1),n=len(T),diff=diff,lo={f'{s}!{a}':lv[(s,a)] for s,a in T})
    print(nm,'秒',out[nm]['seconds'],'不一致',diff,flush=True)
json.dump(out,open('docs/evidence/20261015_稽核2/32_lo_check.json','w'),ensure_ascii=False,indent=1,default=str)

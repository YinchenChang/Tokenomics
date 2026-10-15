"""以 LibreOffice headless 重算 1 個情境（Cap_In C13 χ＝0；複本放 docs/evidence/20261015_稽核3A/lo/，不提交、不碰 model/），
與 20_eval.py 結果比對，交叉驗證 G01 閉合與 S3 求值。用法：python3 32_lo_check.py <wb.pkl>"""
import sys,json,importlib.util,time
sys.path.insert(0,'tests/parity')
import parity_lib as P
from pathlib import Path
spec=importlib.util.spec_from_file_location('ev','docs/evidence/20261015_稽核2/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[1])
SRC=Path('model/20261015_Tokenomics_v5.36.xlsx');D=Path('docs/evidence/20261015_稽核3A/lo')
inp={'Cap_In!C13':0.0}
T=[('Amortize',f'{k}39') for k in 'DGJMP']+[('Interface',f'{k}{r}') for k in 'DM' for r in (95,96,98,100,113,114,116,118,240,250,280)]
t=time.time();src=D/'chi0.xlsx';P.set_inputs(SRC,src,inp);rec=P.lo_recalc(src,D/'out');lv=P.excel_values(rec,T)
b.set({tuple(k.split('!')):v for k,v in inp.items()});pv={k:b.get(*k) for k in T}
diff=[(f'{s}!{a}',pv[(s,a)],lv[(s,a)]) for s,a in T if not(isinstance(pv[(s,a)],(int,float)) and isinstance(lv[(s,a)],(int,float)) and abs(pv[(s,a)]-lv[(s,a)])<=1e-9*max(1,abs(lv[(s,a)])))]
out=dict(inputs=inp,seconds=round(time.time()-t,1),n=len(T),diff=diff,lo={f'{s}!{a}':lv[(s,a)] for s,a in T})
json.dump(out,open('docs/evidence/20261015_稽核3A/32_lo_check.json','w'),ensure_ascii=False,indent=1,default=str)
print('秒',out['seconds'],'目標',len(T),'不一致',diff)

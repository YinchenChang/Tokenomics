import sys, openpyxl
from pathlib import Path
sys.path.insert(0, str(Path('tests/parity').resolve()))
from parity_lib import set_inputs, lo_recalc
src=Path('model/20261025_Tokenomics_v21.7.xlsx')
base=[1.2,1.15,1,1,1]
out=['L1_TokLedger_GW25','L1_RevGW_PQ_VR200','L1_LReqFleet_Full','L1_LTotalFleetVDisc','L1_PriceReqBE','L1_M','L1_TokLedger','IF_FleetProdRatio_VR200']
cells=[('Perf','F88'),('Perf','G88'),('Perf','J88'),('Perf','K88'),('Perf','L88'),('Perf','F75')]
for k in [1,3,5]:
    inp={f'Calib!{c}67':base[i]*k for i,c in enumerate('CDEFG')}
    dst=Path(f'/tmp/sens_k{k}.xlsx'); set_inputs(src,dst,inp)
    r=lo_recalc(dst, Path(f'/tmp/sens_out{k}'))
    wb=openpyxl.load_workbook(r,data_only=True)
    res={}
    for n in out:
        s,ref=list(wb.defined_names[n].destinations)[0]; res[n]=wb[s][ref.replace('$','')].value
    for s,c in cells: res[f'{s}!{c}']=wb[s][c].value
    print('k=',k,res,flush=True)

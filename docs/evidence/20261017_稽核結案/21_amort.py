"""Hopper 欄預設攤提 ×2.69（2-1b 待判斷第 2 項）在各版的演變；J1 倍數現值。"""
import os, sys
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
R = lib.ROOT
files = {'v5.36': '20261015_Tokenomics_v5.36.xlsx', 'v6.1': '20261015_Tokenomics_v6.1.xlsx', 'v6.2': '20261016_Tokenomics_v6.2.xlsx',
         'v6.3': '20261016_Tokenomics_v6.3.xlsx', 'v9.0': '20261016_Tokenomics_v9.0.xlsx', 'v14.1': None}


def nv(wb, n):
    dn = wb.defined_names.get(n)
    if not dn:
        return None
    for sh, ref in dn.destinations:
        ws = wb[sh]
        c = ws[ref.replace('$', '')]
        if isinstance(c, tuple):
            row = c[0] if isinstance(c[0], tuple) else c
            return [x.value for x in row]
        return c.value


names = ['IF_AmortDefault_Luna', 'IF_AmortDefault_Sol', 'IF_FullCostDefault_Luna', 'IF_FullCostDefault_Sol', 'IF_AmortBU_Luna', 'L1_LReqFleet', 'L1_MFleet', 'IF_AllocQ1', 'IF_AllocRDGW']
for k, f in files.items():
    wb = lib.val() if f is None else openpyxl.load_workbook(os.path.join(R, 'model', 'archive', f), data_only=True)
    print(k)
    for n in names:
        v = nv(wb, n)
        if isinstance(v, list):
            v = [round(x, 4) if isinstance(x, (int, float)) else x for x in v[:4]]
        elif isinstance(v, float):
            v = round(v, 4)
        print('  ', n, v)
    if f is None:
        for n in ['ARCH_ScaleGen', 'ARCH_ScaleGen_Lo', 'ARCH_ScaleGen_Hi']:
            print('  ', n, nv(wb, n))

"""show.py 頁 列[,列…] [欄…]：印出 v5.36 與現行的標籤、公式、值（診斷用）。"""
import sys, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
old_f = openpyxl.load_workbook(os.path.join(lib.ROOT, 'model', 'archive', '20261015_Tokenomics_v5.36.xlsx'), data_only=False)
old_v = openpyxl.load_workbook(os.path.join(lib.ROOT, 'model', 'archive', '20261015_Tokenomics_v5.36.xlsx'), data_only=True)
sheet = sys.argv[1]
rows = [int(x) for x in sys.argv[2].split(',')]
cols = sys.argv[3].split(',') if len(sys.argv) > 3 else ['A', 'C']
W = int(os.environ.get('W', '150'))
for r in rows:
    for c in cols:
        a = f'{c}{r}'
        of, ov = old_f[sheet][a].value, old_v[sheet][a].value
        cf, cv = lib.frm()[sheet][a].value, lib.val()[sheet][a].value
        print(f'{sheet}!{a}')
        print('   v5.36:', str(of)[:W], '=>', str(ov)[:60])
        print('   v14.1:', str(cf)[:W], '=>', str(cv)[:60])

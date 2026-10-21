"""L 閱讀版的換版核對：確認閱讀版裡取自 Tokenomics 的數字與指定版本一致。

v18.0 起只核對 L 閱讀版（Andy 2026-10-21：m 閱讀版不再使用、日後重做；原 m 閱讀版已移到 docs/plan/_待刪除/）。
用法：
    python3 check_reading.py <Tokenomics.xlsx> <L閱讀版.xlsx>
L 閱讀版需先用 LibreOffice 重算（讀公式結果）。全部通過時結束碼 0，否則 1。
"""
import csv, math, re, sys
from pathlib import Path
import openpyxl

if len(sys.argv) != 3:
    sys.exit('用法：python3 check_reading.py <Tokenomics.xlsx> <L閱讀版.xlsx>')
TK, LW = sys.argv[1:3]
T = openpyxl.load_workbook(TK, data_only=True)
TF = openpyxl.load_workbook(TK)
fails = []


def same(a, b):
    try:
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-12)
    except (TypeError, ValueError):
        return a == b


def cell(ref):
    sh, c = ref.split('!')
    return T[sh.strip("'")][c].value


def named(n):
    d = TF.defined_names.get(n)
    sh, rng = list(d.destinations)[0]
    return T[sh][rng.replace('$', '')].value


def check(label, ok, detail=''):
    if not ok:
        fails.append(f'{label} {detail}')


# 0. 規格：必須有需求公式樹
L = openpyxl.load_workbook(LW, data_only=True)
check('規格', '1_公式樹' in L.sheetnames, 'L 閱讀版缺 1_公式樹')

# 1. L 閱讀版：情境摘要對具名範圍；所需 L
ws = L['3_L逐世代']
for r in range(6, 13):
    d, nm, c = ws.cell(r, 4).value, ws.cell(r, 6).value, ws.cell(r, 3).value
    check('L 摘要原值', same(d, named(nm)), f'{nm} {d} → {named(nm)}')
    check('L 摘要重算', same(c, named(nm)), f'{nm} 本簿 {c} → {named(nm)}')
check('所需 L', same(L['1_公式樹']['C8'].value, named('L1_LReqFleet_IdNoK')), '')

# 2. 「差異」欄與錯誤值
for name, W in (('L', L),):
    F = openpyxl.load_workbook(LW)
    for wsf in F.worksheets:
        wv = W[wsf.title]
        for row in wsf.iter_rows():
            for c in row:
                v = wv[c.coordinate].value
                if isinstance(v, str) and re.match(r'^(#(REF|VALUE|DIV/0|NAME|N/A)|Err:)', v):
                    fails.append(f'{name} 錯誤值 {wsf.title}!{c.coordinate} {v}')
                f = c.value
                if isinstance(f, str) and f.startswith('=') and re.search(r'/[A-Z]+\d+-1', f) and isinstance(v, (int, float)) and abs(v) > 1e-9:
                    fails.append(f'{name} 差異 {wsf.title}!{c.coordinate} {v}')

print('通過' if not fails else f'未通過 {len(fails)} 項')
for x in fails[:50]:
    print(' -', x)
sys.exit(1 if fails else 0)

"""m／L 閱讀版的換版核對：確認閱讀版裡取自 Tokenomics 的數字與指定版本一致。

用法：
    python3 check_reading.py <Tokenomics.xlsx> <m閱讀版.xlsx> <L閱讀版.xlsx>
兩份閱讀版需先用 LibreOffice 重算（讀公式結果）。全部通過時結束碼 0，否則 1。
"""
import csv, math, re, sys
from pathlib import Path
import openpyxl

TK, MW, LW = sys.argv[1:4]
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


# 0. 規格：兩份都必須有需求公式樹
M = openpyxl.load_workbook(MW, data_only=True)
L = openpyxl.load_workbook(LW, data_only=True)
check('規格', '1A_需求公式樹' in M.sheetnames, 'm 閱讀版缺 1A_需求公式樹')
check('規格', '1_公式樹' in L.sheetnames, 'L 閱讀版缺 1_公式樹')

# 1. m 的前置格：CSV 記錄上一版的值；全部相同 → m 鏈上的數字不需重算
pre = Path(__file__).with_name('m_precursors_v17.0.csv')
n = bad = 0
with open(pre, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        n += 1
        x = T[row['工作表']][row['格']].value
        v = row['v17.0 值']
        if not (same(v, x) or str(v) == str(x) or (v == '' and x is None)):
            bad += 1
            fails.append(f"m 前置格不同 {row['工作表']}!{row['格']} {v} → {x}")
print(f'm 前置格 {n} 格，不同 {bad}')

# 2. m 閱讀版：輸入、3_m重算 原值
ws = M['2_輸入']
for r in range(5, ws.max_row + 1):
    id_, v, loc = ws.cell(r, 1).value, ws.cell(r, 4).value, ws.cell(r, 9).value
    if id_ and str(id_).startswith('IN_') and loc and '!' in str(loc):
        x = cell(str(loc).split('；')[0].split(' ')[0])
        check('m 輸入', same(v, x), f'{id_} {loc} {v} → {x}')
ws = M['3_m重算']
for r in range(5, ws.max_row + 1):
    loc, v = ws.cell(r, 6).value, ws.cell(r, 7).value
    if loc and '!' in str(loc) and isinstance(v, (int, float)):
        check('m 3_m重算 原值', same(v, cell(loc)), f'{loc} {v} → {cell(loc)}')
check('m', same(M['3_m重算']['D28'].value, named('L1_MFleet')), 'm ≠ L1_MFleet')

# 3. L 閱讀版：情境摘要對具名範圍；所需 L
ws = L['3_L逐世代']
for r in range(6, 13):
    d, nm, c = ws.cell(r, 4).value, ws.cell(r, 6).value, ws.cell(r, 3).value
    check('L 摘要原值', same(d, named(nm)), f'{nm} {d} → {named(nm)}')
    check('L 摘要重算', same(c, named(nm)), f'{nm} 本簿 {c} → {named(nm)}')
check('所需 L', same(L['1_公式樹']['C8'].value, named('L1_LReqFleet_IdNoK')), '')

# 4. 兩份的「差異」欄與錯誤值
for name, W in (('m', M), ('L', L)):
    F = openpyxl.load_workbook(MW if name == 'm' else LW)
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

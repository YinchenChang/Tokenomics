"""其餘輕量查證：Gov_Map 旗標、敏感度端點、標記、區間引用等。"""
import os, sys, re, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
R = lib.ROOT
old = openpyxl.load_workbook(os.path.join(R, 'model', 'archive', '20261015_Tokenomics_v5.36.xlsx'), data_only=True)
cur = lib.val()

# 1. Gov_Map 旗標
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    ws = wb['Gov_Map']
    hdr = [c.value for c in ws[4]]
    flagcols = [i for i, h in enumerate(hdr) if h and re.match(r'E\d+|W\d+', str(h))]
    cnt = {hdr[i][:22]: 0 for i in flagcols}
    n = nosrc = 0
    for r in ws.iter_rows(min_row=5, values_only=True):
        if not r[0]:
            continue
        n += 1
        if r[7] in ('—', None) and r[9] in ('—', None):
            nosrc += 1
        for i in flagcols:
            v = r[i]
            if isinstance(v, (int, float)) and v:
                cnt[hdr[i][:22]] += 1
    print(tag, 'Gov_Map 列', n, '無來源也無決策', nosrc)
    print('   ', {k: v for k, v in cnt.items() if v})

# 2. Y9 敏感度端點
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    print(tag, 'Sens_Rev B9', wb['Sens_Rev']['B9'].value, wb['Sens_Rev']['A9'].value)
    print(tag, 'Cap_In C23:E24', [[wb['Cap_In'][f'{c}{r}'].value for c in 'CDE'] for r in (23, 24)])
    print(tag, 'Sens_Train row13', [wb['Sens_Train'][f'{c}13'].value for c in 'ABEFGH'])
    print(tag, 'Sens_Rev B20/B21', wb['Sens_Rev']['B20'].value, wb['Sens_Rev']['B21'].value)

# 3. Arch F 標記
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    print(tag, 'Arch F6:F19', [str(wb['Arch'][f'F{r}'].value)[:40] for r in range(6, 20)])

# 4. 推論支出區間引用
F = lib.frm()
pat = re.compile(r'SRC_DEM_004(_Lo|_Hi)?(?![A-Za-z0-9_])')
used = {}
for ws in F.worksheets:
    if ws.title in ('Gov_Map', 'Decisions', 'README', 'DB_Evidence', 'SRC_Index'):
        continue
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('=') and 'SRC_DEM_004' in c.value:
                m = pat.findall(c.value)
                for x in m:
                    used[(ws.title, x)] = used.get((ws.title, x), 0) + 1
print('SRC_DEM_004 引用', used)
for n in ['AL_ServeGWSpend', 'AL_ServeGWSpend_Lo', 'AL_RngServeSpend_Lo']:
    print(n, n in cur.defined_names)

# 5. Calib C69 / C67
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    print(tag, 'Calib C67..C69', [(wb['Calib'][f'A{r}'].value, wb['Calib'][f'C{r}'].value) for r in (67, 68, 69)])

# 6. Cap_In 87/88
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    print(tag, 'Cap_In 87', str(wb['Cap_In']['A87'].value)[:100], wb['Cap_In']['C87'].value)
    print(tag, 'Cap_In 88', str(wb['Cap_In']['A88'].value)[:100], wb['Cap_In']['C88'].value)
Fo = openpyxl.load_workbook(os.path.join(R, 'model', 'archive', '20261015_Tokenomics_v5.36.xlsx'), data_only=False)
print('Cap_In C87 v5.36', Fo['Cap_In']['C87'].value, '| v14.1', F['Cap_In']['C87'].value)
# 7. Har_In E12 / Harness 45 / 151
for tag, wb in (('v5.36', old), ('v14.1', cur)):
    print(tag, 'Har_In E12:G12', [wb['Har_In'][f'{c}12'].value for c in 'EFG'], str(wb['Har_In']['A12'].value)[:60])
    print(tag, 'Har_In C61:D61', [wb['Har_In'][f'{c}61'].value for c in 'CD'])
print('Harness C151', Fo['Harness']['C151'].value[:200] if Fo['Harness']['C151'].value else None)
print('Harness C151 now', str(F['Harness']['C151'].value)[:200])
# 8. B20: Training reference model forward
for r in range(1, 3):
    pass
# 14. G22 Tech_Registry 25
print('TechReg 25', str(Fo['Tech_Registry']['C25'].value)[:120], '|', str(F['Tech_Registry']['C25'].value)[:120])
# 13. G18
print('Price_Frontier 24', str(Fo['Price_Frontier']['C24'].value)[:120], '|', str(F['Price_Frontier']['C24'].value)[:120])

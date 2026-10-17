"""逐項輕量查證現行活頁簿（對應原發現）。輸出 checks.json。"""
import sys, os, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
F = lib.frm()
V = lib.val()
out = {}


def count_refs(name, exclude=('Gov_Map', 'Decisions', 'README', 'DB_Evidence', 'SRC_Index')):
    n = 0
    where = {}
    pat = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(name) + r'(?![A-Za-z0-9_])')
    for ws in F.worksheets:
        if ws.title in exclude:
            continue
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('=') and pat.search(c.value):
                    n += 1
                    where[ws.title] = where.get(ws.title, 0) + 1
    return n, where


for nm in ['SRC_DEM_004_Lo', 'SRC_DEM_004_Hi', 'AL_Kappa', 'CST_TokPerPromptV528', 'B4_Serve', 'B4_Free', 'IF_Util', 'AL_UtilActual', 'L1_GapUnexplained']:
    out['refs_' + nm] = count_refs(nm)
    print(nm, out['refs_' + nm])


def gov(sheet, cell):
    ws = V['Gov_Map']
    from openpyxl.utils import range_boundaries, get_column_letter
    for r in ws.iter_rows(min_row=5, values_only=True):
        if r[2] == sheet and r[3]:
            try:
                c1, r1, c2, r2 = range_boundaries(str(r[3]).replace('$', ''))
            except Exception:
                continue
            from openpyxl.utils.cell import coordinate_from_string, column_index_from_string
            col, row = coordinate_from_string(cell)
            ci = column_index_from_string(col)
            if c1 <= ci <= c2 and r1 <= row <= r2:
                return dict(gm=r[0], cat=r[5], src=r[7], dec=r[9], lo=r[10], hi=r[11], label=r[4], reason=str(r[13])[:120])


for sh, c in [('Alloc_In', 'C26'), ('Calib', 'C67'), ('Calib', 'C68'), ('Serving', 'C18'), ('Serving', 'C28'), ('Train_In', 'E25'), ('Alloc_In', 'C24'), ('Calib', 'C5')]:
    print(sh, c, gov(sh, c))
# 現值
for nm in ['IF_AllocQ1', 'IF_AllocQ1_R2', 'IF_AllocRDGW', 'IF_AllocServeGW', 'L1_MFleet', 'L1_MImplied', 'L1_LReqFleet', 'L1_ScaleRD', 'L1_ScaleServe', 'L1_GapUnexplained', 'IF_AllocImpliedNk', 'IF_AllocServeGW_Tok', 'IF_AllocQ1_Tok']:
    v = lib.name_value(nm)
    print(nm, str(v)[:200])

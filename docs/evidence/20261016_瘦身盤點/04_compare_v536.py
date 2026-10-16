"""死格與 v5.36 比對。用法：python3 04_compare_v536.py <a.pkl> <out.pkl>
v5.36 的死格清單取自 docs/reports/20261015_稽核0_明細.xlsx 的 C3_死格頁。
比對鍵：(頁, 列標籤, 欄)，因為 v5.36→v10.0 之間列位置可能移動；另附同格位址比對。"""
import pickle, collections, openpyxl, re, sys
a = pickle.load(open(sys.argv[1], 'rb'))
ws = openpyxl.load_workbook('docs/reports/20261015_稽核0_明細.xlsx', read_only=True)['C3_死格']
old = [r for r in ws.iter_rows(min_row=3, values_only=True) if r[0]]
oldc = {(r[0], r[1]) for r in old}
newc = {(z['sheet'], z['cell']) for z in a['dead']}
print('v5.36 dead', len(old), 'v10 dead', len(newc))
print('同格位址：兩版皆死', len(oldc & newc), '僅舊', len(oldc - newc), '僅新', len(newc - oldc))
def key(s, cell, label):
    return (s, str(label).strip(), re.match(r'[A-Z]+', cell).group())
oldl = {key(r[0], r[1], r[3]) for r in old}
newl = {key(z['sheet'], z['cell'], z['label']) for z in a['dead']}
print('頁＋標籤＋欄：兩版皆死', len(oldl & newl), '僅舊', len(oldl - newl), '僅新', len(newl - oldl))
print('僅新 依頁', collections.Counter(s for s, _, _ in newl - oldl).most_common())
print('僅舊 依頁', collections.Counter(s for s, _, _ in oldl - newl).most_common())
pickle.dump(dict(old=old, oldl=oldl), open(sys.argv[2], 'wb'))

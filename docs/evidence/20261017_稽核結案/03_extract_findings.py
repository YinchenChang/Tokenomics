"""從原稽核明細抽出每個 F/G/B 編號的代表描述、涉及列數與嚴重度分布。"""
import openpyxl, os, re, json, collections
REP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'reports')
OUT = os.path.dirname(os.path.abspath(__file__))
cfg = [('稽核2', 'F', 'F 編號'), ('稽核3A', 'G', 'G 編號'), ('稽核3B', 'B', 'B 編號')]
res = {}
for seg, p, idcol in cfg:
    wb = openpyxl.load_workbook(os.path.join(REP, f'20261015_{seg}_明細.xlsx'), read_only=True)
    rows = list(wb['逐列檢查'].iter_rows(values_only=True))
    h = list(rows[1])
    ii = h.index(idcol)
    si = h.index('嚴重度')
    for r in rows[2:]:
        ids = r[ii]
        if not ids:
            continue
        for fid in str(ids).replace('，', ',').split(','):
            fid = fid.strip()
            d = res.setdefault(fid, {'seg': seg, 'n': 0, 'sev': collections.Counter(), 'sample': None, 'rows': []})
            d['n'] += 1
            d['sev'][r[si]] += 1
            txt = ' '.join(str(c) for c in r if c and re.search(r'\[?' + fid + r'\]?[：:]', str(c)))
            if d['sample'] is None and txt:
                d['sample'] = txt[:420]
            d['rows'].append([r[0], r[1], r[2], r[si], str(ids)])
for k in sorted(res):
    d = res[k]
    print(k, d['seg'], d['n'], dict(d['sev']), '|', (d['sample'] or '')[:300])
    d['sev'] = dict(d['sev'])
json.dump(res, open(os.path.join(OUT, 'findings_raw.json'), 'w'), ensure_ascii=False)

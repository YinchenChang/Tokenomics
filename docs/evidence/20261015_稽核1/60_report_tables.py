"""產生報告中的統計表與「高」清單（markdown 片段）。用法：python3 60_report_tables.py <40_判讀逐格.json> <10_overlap.csv>"""
import json, sys, collections, csv
x=json.load(open(sys.argv[1]))
out=[]
for zone,flag in (('m 路徑內','是'),('m 路徑外','否')):
    t=collections.defaultdict(collections.Counter); cellsev=collections.Counter()
    for i in x:
        if i['m']!=flag: continue
        cellsev[i['sev']]+=1
        for c in (i['c'].split(',') if i['c']!='—' else []): t[c][i['sev']]+=1
    out.append(f"\n**{zone}**（{sum(cellsev.values())} 格；有問題 {sum(v for k,v in cellsev.items() if k!='—')} 格：高 {cellsev['高']}、中 {cellsev['中']}、低 {cellsev['低']}；沒有問題 {cellsev['—']}）\n")
    out.append('| 類別 | 高 | 中 | 低 | 合計 |\n|---|---:|---:|---:|---:|')
    for c,name in zip('TGUSERD',['T 時點','G 應分世代／時間','U 單位或口徑','S 來源薄弱且敏感','E 未處理證據','R 數值可疑','D 定義不清']):
        a=t[c]; out.append(f"| {name} | {a['高']} | {a['中']} | {a['低']} | {sum(a.values())} |")
out.append('\n（一格可同時屬多個類別，各類別分別計數，所以類別合計大於有問題的格數。）\n')
# 高清單
out.append('\n| # | 頁 | 格 | 列標籤 | m 路徑 | 類別 | 理由 |\n|---:|---|---|---|---|---|---|')
g=collections.OrderedDict()
for i in x:
    if i['sev']=='高': g.setdefault((i['sheet'],i['row']),[]).append(i)
for n,((s,r),v) in enumerate(g.items(),1):
    out.append(f"| {n} | {s} | {','.join(i['cell'] for i in v)} | {v[0]['label'][:40]} | {'是' if any(i['m']=='是' for i in v) else '否'} | {v[0]['c']} | {v[0]['r']} |")
# 重疊清單摘要
rows=list(csv.DictReader(open(sys.argv[2])))
gg=collections.OrderedDict()
for r in rows: gg.setdefault(r['頁'],collections.OrderedDict()).setdefault(r['列標籤'],[]).append(r['格'])
out.append('\n| 頁 | 格數 | 列（格） |\n|---|---:|---|')
for s,d in gg.items():
    out.append(f"| {s} | {sum(len(v) for v in d.values())} | "+'；'.join(f"{k[:22]}（{','.join(v) if len(v)<=5 else v[0]+'…'+v[-1]}）" for k,v in d.items())+' |')
print('\n'.join(out))

"""合併判讀檔，逐格展開並計算嚴重度。
用法：python3 30_build.py <ctx.json> <out.json> [判讀檔 ...]
嚴重度規則（工作單第 2 節）：
  高＝本格在 m 路徑上，或屬 Load_Bearing 頁所列／Gov_Map「CC 敏感度分段」＝高的輸入，而且類別含 T、G、U、S 任一項；
  中＝類別含 T、G、U、S 任一項但不屬上述高敏感範圍；或在 m 路徑／高敏感範圍而類別只有 E、R、D；
  低＝其餘有問題者（不在 m 路徑也非高敏感，類別只有 E、R、D）；無問題填「—」。"""
import json, sys, collections
ctx=json.load(open(sys.argv[1])); J={}
for p in sys.argv[3:]:
    ns={}; exec(open(p,encoding='utf-8').read(),ns); J.update(ns['J'])
out=[]; missing=[]
for g in ctx:
    k=(g['sheet'],g['row']); jj=J.get(k)
    if jj is None: missing.append(k)
    for c in g['cells']:
        gv=g['gov'].get(c['gm']) if c['gm'] else None
        tier=(gv or {}).get('tier')
        hs = c['m']=='是' or g['lb'] or tier=='高'
        cats=set() if not jj or jj['c'] in ('—','') else set(jj['c'].split(','))
        core=cats & set('TGUS')
        if not cats: sev='—'
        elif core and hs: sev='高'
        elif core or hs: sev='中'
        else: sev='低'
        out.append(dict(sheet=g['sheet'],row=g['row'],cell=c['cell'],gm=c['gm'],label=g['label'],m=c['m'],lb=g['lb'],tier=tier,
                        judged=jj is not None,sev=sev,**({} if not jj else jj),covers=','.join(x['cell'] for x in g['cells'])))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
print('cells',len(out),'judged',sum(o['judged'] for o in out),'missing groups',len(missing))
mm=[o for o in out if o['m']=='是']
print('m cells',len(mm),'m judged',sum(o['judged'] for o in mm))
print('m missing',[ (o['sheet'],o['cell']) for o in mm if not o['judged']][:20])
print(collections.Counter(o['sev'] for o in mm))

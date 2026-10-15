"""說明欄寫死數字對照現值（3B 列）：說明文字中「現值／基準／約／＝」後的數字，與本列公式格現值比對；
相差 >5% 且找不到任何同列公式值可對上的，列為候選（人工再看）。用法：python3 12_notes.py <wb.pkl> <out.json>"""
import pickle,sys,re,json
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells']
rows=json.load(open('docs/evidence/20261015_稽核3B/00_rows.json'))
SUP={'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9'}
def num(s):
    m=re.match(r'([0-9.]+)\s*×\s*10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)',s)
    if m: return float(m.group(1))*10**int(''.join(SUP[c] for c in m.group(2)))
    try: return float(s)
    except: return None
out=[]
for x in rows:
    sh,r=x['sh'],x['r']
    vals=[c['v'] for (s,a),c in cells.items() if s==sh and c['r']==r and isinstance(c['f'],str) and c['f'].startswith('=') and isinstance(c['v'],(int,float)) and not isinstance(c['v'],bool)]
    notes=[(a,c['v']) for (s,a),c in cells.items() if s==sh and c['r']==r and isinstance(c['v'],str) and not (isinstance(c['f'],str) and c['f'].startswith('=')) and re.match('[A-Z]+',a).group() not in('A','B','C','D','E')]
    if not vals: continue
    for a,t in notes:
        for m in re.finditer(r'(現值|基準約?|約)\s*([0-9.]+(?:\s*×\s*10[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?)\s*(T|%)?',t):
            v=num(m.group(2))
            if v is None or v==0: continue
            cand=[v, v*1e12/365/1e6 if m.group(3)=='T' else v, v/100 if m.group(3)=='%' else v]
            ok=any(abs(c/w-1)<=0.05 for c in cand for w in vals if w)
            if not ok: out.append(dict(cell=f'{sh}!{a}',text=m.group(0),row_vals=[f'{w:.4g}' for w in vals[:4]],ctx=t[max(0,m.start()-30):m.end()+30]))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
for o in out: print(o['cell'],o['text'],o['row_vals'],'|',o['ctx'])

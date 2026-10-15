"""逐列閱讀用：列印 3A 列的標籤、單位、每種公式結構（第一格公式與值）、同列各欄值、說明欄文字。
用法：python3 11_dump.py <wb.pkl> <mech.pkl> <sheet> [maxpat]"""
import pickle,sys,re
d=pickle.load(open(sys.argv[1],'rb'));cells=d['cells'];M=pickle.load(open(sys.argv[2],'rb'))
sh=sys.argv[3]; mp=int(sys.argv[4]) if len(sys.argv)>4 else 3
def fmt(v):
    if isinstance(v,float): return f'{v:.4g}'
    return str(v)[:60]
for x in M['rows']:
    if x['sheet']!=sh: continue
    r=x['row']
    row=sorted([(a,c) for (s,a),c in cells.items() if s==sh and c['r']==r],key=lambda t:(len(re.match('[A-Z]+',t[0]).group()),t[0]))
    vals=' '.join(f"{re.match('[A-Z]+',a).group()}={fmt(c['v'])}" for a,c in row if re.match('[A-Z]+',a).group() not in('A',) and not(isinstance(c['v'],str) and len(c['v'])>40))
    notes=[c['v'] for a,c in row if isinstance(c['v'],str) and len(c['v'])>40 and not(isinstance(c['f'],str) and c['f'].startswith('='))]
    print(f"## {sh}!{r} 〔{x['label']}〕 u={x['unit']} users={x['users']} upY={','.join(x['upY'])} dY={','.join(x['directY'])}")
    for p,cs in x['patterns'][:mp]:
        a=cs[0]; print(f"   [{len(cs)}] {a}: {cells[(sh,a)]['f'][:330]}")
    if len(x['patterns'])>mp: print(f"   ...+{len(x['patterns'])-mp} patterns")
    print('   V:',vals[:420])
    for n in notes: print('   N:',n[:400])

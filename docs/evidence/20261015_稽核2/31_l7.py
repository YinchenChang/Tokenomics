"""L7：在會產生「SLO 不可達」等文字回傳的端點情境下重算 m 路徑全部公式格，找出
(a) 變成錯誤值（文字被當數字運算）的格；(b) 數值為 0 而同列其他欄為正（文字或不可達被當成 0）的格。"""
import sys,importlib.util,pickle,collections,re,json
spec=importlib.util.spec_from_file_location('ev',sys.argv[1]+'/20_eval.py');ev=importlib.util.module_from_spec(spec);spec.loader.exec_module(ev)
b=ev.Book(sys.argv[2]); M=pickle.load(open(sys.argv[3],'rb'))
rows={(x['sheet'],x['row']) for x in M['rows']}
tg=[k for k,x in b.cells.items() if (k[0],x['r']) in rows and isinstance(x['f'],str) and x['f'].startswith('=') and re.match('[A-Z]+',k[1]).group() not in ('R','S','T','U','V','W','X','Y')]
SCEN={'Serving!C18=0.7':{('Serving','C18'):0.7},'Arch!E8=160':{('Arch','E8'):160},'Calib!C68=3':{('Calib','C68'):3},'Serving!D21=100（SLO 高）':{('Serving','D21'):100,('Serving','E21'):100}}
out={}
for nm,ov in SCEN.items():
    b.set(ov)
    err=[];zero=[];txt=[]
    for k in tg:
        v=b.get(*k); c=b.cells[k]['v']
        if isinstance(v,str) and v.startswith('#'): err.append((k,v))
        elif isinstance(v,str) and isinstance(c,(int,float)) and not isinstance(c,bool): txt.append((k,v))
        elif isinstance(v,(int,float)) and not isinstance(v,bool) and v==0 and isinstance(c,(int,float)) and c!=0: zero.append(k)
    out[nm]=dict(err=[f'{a}!{b_}:{v}' for (a,b_),v in err],txt=sorted({f'{a}!{re.sub("[A-Z]+","",b_)}' for (a,b_),v in txt}),zero=sorted({f'{a}!{re.sub("[A-Z]+","",b_)}' for a,b_ in zero}),
        zero_cells=[f'{a}!{b_}' for a,b_ in zero])
    print(nm,'錯誤值',len(err),'變文字列',len(out[nm]['txt']),'變 0 的列',out[nm]['zero'])
    print('   錯誤樣本',out[nm]['err'][:6])
json.dump(out,open(sys.argv[4],'w'),ensure_ascii=False,indent=1)

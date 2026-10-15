"""S3 用：以工作簿本身的公式文字在 Python 中逐格求值（只讀；不新增任何機制）。
做法：openpyxl Tokenizer 把每個公式轉成 Python 運算式，依需要（從目標格往上游）遞迴求值並快取；
可覆寫任一輸入格後重算。先以「不覆寫」重算目標格，與檔內 LibreOffice 快取值比對，確認一致後才用於敏感度。
用法：from 20_eval import Book；b=Book(wb.pkl)；b.get('L1','D78')；b.set({('Alloc_In','C23'):1.0})"""
import pickle, re, math, sys
from openpyxl.formula import Tokenizer
from openpyxl.utils import range_boundaries, get_column_letter as L, column_index_from_string as CI
sys.setrecursionlimit(200000)
class XlErr(Exception): pass
class Rng:
    def __init__(s,book,sh,c1,r1,c2,r2): s.b=book;s.sh=sh;s.c1,s.r1,s.c2,s.r2=c1,r1,c2,r2
    def cell(s,i,j): return s.b.val(s.sh,f'{L(s.c1+j-1)}{s.r1+i-1}')
    def flat(s): return [s.b.val(s.sh,f'{L(c)}{r}') for r in range(s.r1,s.r2+1) for c in range(s.c1,s.c2+1)]
    @property
    def nr(s): return s.r2-s.r1+1
    @property
    def nc(s): return s.c2-s.c1+1
def num(x):
    if isinstance(x,Rng): x=_isect(x)
    if x is None: return 0.0
    if isinstance(x,bool): return 1.0 if x else 0.0
    if isinstance(x,(int,float)): return float(x)
    if isinstance(x,str):
        if x.startswith('#'): raise XlErr(x)
        try: return float(x)
        except: raise XlErr('#VALUE!')
    raise XlErr('#VALUE!')
CUR=[None]
def _isect(r):
    if r.nr==1 and r.nc==1: return r.cell(1,1)
    sh,a=CUR[0]; m=re.match(r'([A-Z]+)(\d+)',a); c=CI(m.group(1)); rr=int(m.group(2))
    if r.nr==1 and r.c1<=c<=r.c2: return r.cell(1,c-r.c1+1)
    if r.nc==1 and r.r1<=rr<=r.r2: return r.cell(rr-r.r1+1,1)
    raise XlErr('#VALUE!')
def sc(x): return _isect(x) if isinstance(x,Rng) else x
def txt(x):
    x=sc(x)
    if x is None: return ''
    if isinstance(x,bool): return 'TRUE' if x else 'FALSE'
    if isinstance(x,float) and x.is_integer(): return str(int(x))
    return str(x)
def _arr(x):
    """二元運算元：可做隱含交集就取單值，否則視為陣列（SUMPRODUCT 內的陣列運算）。"""
    if isinstance(x,list): return x
    if isinstance(x,Rng):
        try: return _isect(x)
        except XlErr: return x.flat()
    return x
def _bin(a,b,f):
    x,y=_arr(a),_arr(b)
    if isinstance(x,list) or isinstance(y,list):
        n=len(x) if isinstance(x,list) else len(y)
        xs=x if isinstance(x,list) else [x]*n; ys=y if isinstance(y,list) else [y]*n
        out=[]
        for p,q in zip(xs,ys):
            try: out.append(f(p,q))
            except XlErr as e: out.append(e.args[0])
        return out
    return f(x,y)
class V:
    __slots__=('x',)
    def __init__(s,x): s.x=x
    def __add__(a,b): return V(_bin(a.x,b.x,lambda p,q:num(p)+num(q)))
    def __sub__(a,b): return V(_bin(a.x,b.x,lambda p,q:num(p)-num(q)))
    def __mul__(a,b): return V(_bin(a.x,b.x,lambda p,q:num(p)*num(q)))
    def __truediv__(a,b):
        d=num(b.x)
        if d==0: raise XlErr('#DIV/0!')
        return V(num(a.x)/d)
    def __pow__(a,b):
        try: return V(float(num(a.x)**num(b.x)))
        except Exception: raise XlErr('#NUM!')
    def __neg__(a): return V(-num(a.x))
    def __pos__(a): return a
    def __and__(a,b): return V(txt(a.x)+txt(b.x))
    def _c(a,b):
        x,y=sc(a.x),sc(b.x)
        if isinstance(x,str) and x.startswith('#'): raise XlErr(x)
        if isinstance(y,str) and y.startswith('#'): raise XlErr(y)
        if x is None: x=0.0 if not isinstance(y,str) else ''
        if y is None: y=0.0 if not isinstance(x,str) else ''
        if isinstance(x,bool): x=float(x)
        if isinstance(y,bool): y=float(y)
        if isinstance(x,str) and isinstance(y,str): return (x.lower()>y.lower())-(x.lower()<y.lower())
        if isinstance(x,str): return 1
        if isinstance(y,str): return -1
        return (x>y)-(x<y)
    def __eq__(a,b):
        if isinstance(_arr(a.x),list) or isinstance(_arr(b.x),list): return V(_bin(a.x,b.x,lambda p,q:V(p)._c(V(q))==0))
        return V(a._c(b)==0)
    def __ne__(a,b): return V(a._c(b)!=0)
    def __lt__(a,b): return V(a._c(b)<0)
    def __le__(a,b): return V(a._c(b)<=0)
    def __gt__(a,b): return V(a._c(b)>0)
    def __ge__(a,b): return V(a._c(b)>=0)
    def __bool__(s): raise RuntimeError('use truth()')
def truth(x):
    x=sc(x.x if isinstance(x,V) else x)
    if isinstance(x,str):
        if x.startswith('#'): raise XlErr(x)
        if x.upper()=='TRUE': return True
        if x.upper()=='FALSE': return False
        raise XlErr('#VALUE!')
    return bool(num(x))
def U(x): return x.x if isinstance(x,V) else x
def ev(th):
    return U(th())
def F_IF(c,a,b=None):
    if truth(ev(c)): return V(ev(a))
    return V(ev(b) if b is not None else False)
def F_ISNUMBER(a):
    try: x=sc(ev(a))
    except XlErr: return V(False)
    return V(isinstance(x,(int,float)) and not isinstance(x,bool))
def F_ISTEXT(a):
    try: x=sc(ev(a))
    except XlErr: return V(False)
    return V(isinstance(x,str) and not x.startswith('#'))
def F_IFERROR(a,b):
    try:
        x=ev(a); x2=sc(x)
        if isinstance(x2,str) and x2.startswith('#'): raise XlErr(x2)
        return V(x)
    except XlErr: return V(ev(b))
def vals(args):
    out=[]
    for a in args:
        x=ev(a)
        if isinstance(x,Rng):
            for y in x.flat():
                if isinstance(y,str) and y.startswith('#'): raise XlErr(y)
                if isinstance(y,(int,float)) and not isinstance(y,bool): out.append(float(y))
        else: out.append(num(x))
    return out
def F_AND(*a): return V(all([truth(ev(x)) if not isinstance(ev(x),Rng) else all(truth(y) for y in ev(x).flat()) for x in a]))
def F_OR(*a): return V(any([truth(ev(x)) for x in a]))
def F_NOT(a): return V(not truth(ev(a)))
def F_MAX(*a): v=vals(a); return V(max(v) if v else 0.0)
def F_MIN(*a): v=vals(a); return V(min(v) if v else 0.0)
def F_SUM(*a): return V(sum(vals(a)))
def F_AVERAGE(*a): v=vals(a); return V(sum(v)/len(v))
def F_ABS(a): return V(abs(num(ev(a))))
def F_EXP(a): return V(math.exp(num(ev(a))))
def F_LN(a):
    x=_arr(ev(a))
    if isinstance(x,list): return V([math.log(num(y)) if num(y)>0 else '#NUM!' for y in x])
    x=num(x)
    if x<=0: raise XlErr('#NUM!')
    return V(math.log(x))
def F_SQRT(a): return V(math.sqrt(num(ev(a))))
def F_CEILING(a,b=None):
    x=num(ev(a)); s=num(ev(b)) if b is not None else 1.0
    if s==0: return V(0.0)
    return V(math.ceil(x/s-1e-12)*s)
def F_FLOOR(a,b=None):
    x=num(ev(a)); s=num(ev(b)) if b is not None else 1.0
    return V(math.floor(x/s+1e-12)*s)
def F_ROUND(a,b): n=int(num(ev(b))); return V(round(num(ev(a)),n))
def F_CHOOSE(i,*a): return V(ev(a[int(num(ev(i)))-1]))
def F_INDEX(r,i,j=None):
    R=ev(r); i=int(num(ev(i))); j=int(num(ev(j))) if j is not None else None
    if not isinstance(R,Rng): return V(R)
    if j is None:
        if R.nr==1: return V(R.cell(1,i))
        if R.nc==1: return V(R.cell(i,1))
        raise XlErr('#REF!')
    if i==0 or j==0: raise XlErr('#REF!')
    if i>R.nr or j>R.nc: raise XlErr('#REF!')
    return V(R.cell(i,j))
def F_SUMPRODUCT(*a):
    arrs=[ev(x) for x in a]
    fl=[x.flat() if isinstance(x,Rng) else (x if isinstance(x,list) else [x]) for x in arrs]
    n=len(fl[0]); s=0.0
    for k in range(n):
        p=1.0
        for f in fl:
            y=f[k]
            if isinstance(y,str) and y.startswith('#'): raise XlErr(y)
            p*=float(y) if isinstance(y,(int,float)) else 0.0
        s+=p
    return V(s)
def F_MATCH(x,r,t=None):
    X=sc(ev(x)); R=ev(r).flat()
    for k,y in enumerate(R):
        if y==X or (isinstance(y,(int,float)) and isinstance(X,(int,float)) and abs(y-X)<=1e-12*max(1,abs(X))): return V(float(k+1))
    raise XlErr('#N/A')
def F_COUNTIF(r,c):
    R=ev(r).flat(); C=sc(ev(c)); m=re.match(r'([<>=]+)(.*)',str(C))
    op,val=m.group(1),float(m.group(2))
    import operator
    f={'<':operator.lt,'>':operator.gt,'<=':operator.le,'>=':operator.ge,'=':operator.eq}[op]
    return V(float(sum(1 for y in R if isinstance(y,(int,float)) and f(y,val))))
def F_TEXT(a,f): return V(txt(ev(a)))
def F_LEFT(a,n=None): return V(txt(ev(a))[:int(num(ev(n))) if n is not None else 1])
def F_RIGHT(a,n=None): k=int(num(ev(n))) if n is not None else 1; return V(txt(ev(a))[-k:] if k else '')
def F_MID(a,s,n): s=int(num(ev(s)));n=int(num(ev(n))); return V(txt(ev(a))[s-1:s-1+n])
def F_FIND(a,b,s=None):
    i=txt(ev(b)).find(txt(ev(a)))
    if i<0: raise XlErr('#VALUE!')
    return V(float(i+1))
def F_LEN(a): return V(float(len(txt(ev(a)))))
FUNCS={k[2:]:v for k,v in globals().items() if k.startswith('F_')}
class Book:
    def __init__(s,pkl):
        d=pickle.load(open(pkl,'rb')); s.cells=d['cells']; s.names={k:v for k,v in d['names'].items() if '!' not in k or not k.split('!')[0] in [x[0] for x in d['sheets']]}
        s.lnames={n.lower():n for n in d['names']}; s.allnames=d['names']
        s.over={}; s.memo={}; s.code={}; s.fallback=set()
    def set(s,over): s.over=dict(over); s.memo={}
    def refobj(s,t,cur):
        if t.lower() in s.lnames:
            tgt=s.allnames[s.lnames[t.lower()]].lstrip('=')
            return s.refobj(tgt,cur)
        if '!' in t: sh,rg=t.rsplit('!',1); sh=sh.strip("'").replace("''","'")
        else: sh,rg=cur,t
        rg=rg.replace('$','')
        if ':' in rg:
            c1,r1,c2,r2=range_boundaries(rg); return Rng(s,sh,c1,r1,c2,r2)
        return ('C',sh,rg)
    def compile(s,sh,a,f):
        toks=Tokenizer(f).items; out=[]; refs=[]
        stack=[]
        for t in toks:
            ty,st,v=t.type,t.subtype,t.value
            if ty=='WHITE-SPACE': continue
            if ty=='OPERAND':
                if st=='RANGE':
                    refs.append(s.refobj(v,sh)); out.append(f'_R({len(refs)-1})')
                elif st=='NUMBER': out.append(f'V({float(v)!r})')
                elif st=='TEXT': out.append(f'V({v[1:-1].replace(chr(34)*2,chr(34))!r})')
                elif st=='LOGICAL': out.append(f'V({v.upper()=="TRUE"})')
                elif st=='ERROR': out.append(f'_E({v!r})')
            elif ty=='FUNC':
                if st=='OPEN':
                    fn=v[:-1].upper(); 
                    if fn not in FUNCS: raise NotImplementedError(fn)
                    out.append(f'F_{fn}(lambda:('); stack.append('F')
                else: out.append('))'); stack.pop()
            elif ty=='SEP':
                if st=='ARG': out.append('),lambda:(' if stack and stack[-1]=='F' else ',')
                else: raise NotImplementedError('row sep')
            elif ty=='PAREN':
                if st=='OPEN': out.append('('); stack.append('P')
                else: out.append(')'); stack.pop()
            elif ty=='OPERATOR-INFIX':
                out.append({'=':'==','<>':'!=','^':'**','&':'&'}.get(v,v))
            elif ty=='OPERATOR-PREFIX': out.append(v)
            elif ty=='OPERATOR-POSTFIX': out.append('/V(100.0)')
        src=''.join(out)
        return compile(src,f'{sh}!{a}','eval'),refs,src
    def R(s,refs,i):
        o=refs[i]
        if isinstance(o,Rng): return V(o)
        return V(s.val(o[1],o[2]))
    def val(s,sh,a):
        k=(sh,a)
        if k in s.over: return s.over[k]
        if k in s.memo:
            m=s.memo[k]
            if isinstance(m,XlErr): return m.args[0]
            return m
        x=s.cells.get(k)
        if x is None: return None
        f=x['f']
        if not(isinstance(f,str) and f.startswith('=')): return x['v']
        if k not in s.code:
            try: s.code[k]=s.compile(sh,a,f)
            except NotImplementedError as e:
                s.code[k]=None; s.fallback.add((k,str(e)))
        if s.code[k] is None: return x['v']   # 不支援的函數：沿用檔內快取值（記錄於 fallback；只出現在治理欄）
        co,refs,src=s.code[k]
        prev=CUR[0]; CUR[0]=k
        try:
            r=eval(co,dict(FUNCS_G,_R=lambda i:s.R(refs,i)))
            r=U(r)
            if isinstance(r,Rng): r=_isect(r)
            if isinstance(r,bool): pass
            s.memo[k]=r
        except XlErr as e:
            s.memo[k]=e; r=e.args[0]
        finally: CUR[0]=prev
        return r
    def get(s,sh,a): return s.val(sh,a)
def _E(v): raise XlErr(v)
FUNCS_G=dict({f'F_{k}':v for k,v in FUNCS.items()},V=V,_E=_E)

"""L8：每個 m 路徑「頁＋列」的上游含哪些第 1 段 Y1–Y9 輸入格（依賴圖，不穿越登錄頁）。"""
import pickle,sys,collections,openpyxl,json,re
d=pickle.load(open(sys.argv[1],'rb'));G=pickle.load(open(sys.argv[2],'rb'));M=pickle.load(open(sys.argv[3],'rb'))
cells=d['cells'];edges=G['edges']
wb=openpyxl.load_workbook(sys.argv[4],read_only=True)
ymap=collections.defaultdict(set)
for r in list(wb['系統性問題'].iter_rows(min_row=3,values_only=True)):
    for part in str(r[6]).split('；'):
        if '!' not in part: continue
        sh,cs=part.split('!',1)
        for c in cs.split(','): ymap[(sh.strip(),c.strip())].add(r[0])
SKIP={'Gov_Map','Decisions','DB_Evidence','Load_Bearing','SRC_Index','Checks'}
memo={}
def up(node):
    if node in memo: return memo[node]
    memo[node]=frozenset()
    acc=set()
    if node[0] not in('NAME','RANGE') and node in ymap: acc|=ymap[node]
    for p in edges.get(node,()):
        if p[0] in SKIP: continue
        acc|=up(p)
    memo[node]=frozenset(acc); return memo[node]
byrow=collections.defaultdict(list)
for k,x in cells.items(): byrow[(k[0],x['r'])].append(k)
out={}
for r in M['rows']:
    ys=set()
    for k in byrow[(r['sheet'],r['row'])]: ys|=up(k)
    out[f"{r['sheet']}!{r['row']}"]=sorted(ys)
json.dump(out,open(sys.argv[5],'w'),ensure_ascii=False)
c=collections.Counter(y for v in out.values() for y in v); print(c, sum(1 for v in out.values() if v))

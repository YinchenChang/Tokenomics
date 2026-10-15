"""S2 逐列判讀：561 個 m 路徑「頁＋列」× L1–L8。
機械部分：L3（11_align.py 同欄對位、INDEX 常數）、L7（31_l7.py 文字／0 分支情境）、L8（40_upY.py 上游 Y 類與直接引用）。
人工部分：FIND 字典（逐列讀公式後寫入；每項附依據與量化，量化來自 20_eval.py 與 30_s3.json）。
只標問題，不判定對錯、不提修法。用法：python3 50_judge.py <wb.pkl> <graph.pkl> <mech.pkl> <upY.json> <稽核1明細.xlsx> <out.json>"""
import pickle,sys,json,re,collections,openpyxl
from openpyxl.formula import Tokenizer
d=pickle.load(open(sys.argv[1],'rb'));G=pickle.load(open(sys.argv[2],'rb'));M=pickle.load(open(sys.argv[3],'rb'))
upY=json.load(open(sys.argv[4]));cells=d['cells'];edges=G['edges']
wb=openpyxl.load_workbook(sys.argv[5],read_only=True)
ymap=collections.defaultdict(set)
for r in list(wb['系統性問題'].iter_rows(min_row=3,values_only=True)):
    for part in str(r[6]).split('；'):
        if '!' not in part: continue
        sh,cs=part.split('!',1)
        for c in cs.split(','): ymap[(sh.strip(),c.strip())].add(r[0])
# ---- 人工判讀（代號 → 說明）；F 編號對應報告第 3 節 ----
FIND=collections.defaultdict(list)
def add(keys,code,fid,txt):
    for k in keys: FIND[k].append((code,fid,txt))
add([('Calib',69)],'L6','F01','Hopper η_p 倍數＝SRC_HW_019 ÷ SRC_HW_040（BF16 ÷ FP8 峰值＝0.4997）；J 欄說明「v5.5 峰值更正後維持 prefill 產出不變」——倍數由「維持舊產出」倒推，不是效率估計')
add([('Calib',69)],'L1','F01','以峰值單位換算比（BF16÷FP8）充當效率倍數：口徑是「峰值定義」而非「達成率」')
add([('Calib',67)],'L6','F01','Hopper η_d 倍數 1.5：J 欄「峰值更正為 FP8 後倍數同步減半為 1.5，使 Hopper 產出不變」——由維持舊產出倒推；GB200／VR200 沿用 GB300（1）')
add([('Calib',72),('Calib',70),('Perf',51),('Perf',53)],'L8','F01','承接 Calib 第 67、69 列的倒推倍數（Y8）；乘數')
for r in (94,97,119,144,145,146):
    add([('Cap_In',r)],'L5','F02','m＝營收 ÷（token × 混合單價）是殘差型定義：token 數、單價、營收任一項的誤差 1:1 進入 m；不是對「實收 ÷ 牌價」的獨立估計')
add([('Cap_In',137)],'L5','F02','API 營收＝營收 − 消費訂閱 − 商用席次（餘額）；席次占比 Assumed 0.10，m_API 為「殘差的殘差」（S3：席次占比 ±0.05 → m_API ∓25%）')
for r in (76,77,78,80,81,82,83):
    add([('L1',r)],'L5','F02','直接連結 Cap_In 的殘差型 m（見 Cap_In 第 94／97／119／144–146、151 列）')
add([('Cap_In',151)],'L5','F02','組合因子＝m_API ÷ 折讓因子，折讓因子基準恆為 1 → 組合因子＝m_API（同一殘差改名）')
add([('Cap_In',255)],'L5','F03','缺口恆等式：ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））＝2.207；三項都是輸入格原值，剩下的 2.207 是未被解釋的殘差（＝1 ÷ 第 174 列）')
add([('Cap_In',256)],'L5','F03','驗算差＝恆等式 − 1 ÷ 第 174 列：兩邊由同一組輸入代數展開，恆為 0（Checks M5）；只能驗證公式抄寫，不能驗證閉合')
add([('L1',71)],'L5','F03','落差分解 2＝AL_SpendBasis 原值（輸入改名），不是由資料估出的分項')
add([('L1',72)],'L5','F03','落差分解 3＝1 ÷ AL_Kappa 原值；κ 本身為活頁簿外算出的常數（見 F12）')
add([('L1',73)],'L5','F03','落差分解 4＝IF_Util ÷ AL_UtilActual（兩個 Assumed 輸入之比）')
add([('L1',70),('Cap_In',251),('Cap_In',250)],'L5','F03','落差分解 1 的大小取決於比較基準 CST_TokPerPromptV528＝2,000（Decision 常數）；換基準即改變「解釋比例」')
add([('L1',74)],'L5','F03','四項之積 2.900 對 ScaleServe2000 6.401：只解釋 45%；殘差 2.207 未在 L1 以具名列呈現（只在 Cap_In C255）')
add([('L1',90),('Cap_In',253)],'L5','F03','落差分解的對照分母（τ＝2,000 的支出 ÷ token 路線）；三欄同值')
add([('Cap_In',121)],'L2','F04','m 下限的「上限讀法」以 CTL_ProdDerate 0.85 線性縮放產能；同簿 Interface G 節（_Prod）是重解 SLO 的折減，2025 組合下付費產能只剩 100% 的 0.712（Hopper 0.560、GB200 0.758）。同一個 0.85 有兩種作用方式；改用重解值 m 下限 0.542 → 約 0.647')
add([('Cap_In',115),('Cap_In',118)],'L4','F04','產能已是 100% 效率（Serving C18＝1），此處乘 0.85 為線性折減；與 _Prod 頁的重解 SLO 折減不同')
for r in (255,260,265,270):
    add([('Interface',r)],'L4','F04','前緣單價列的生產折減＝Util 列 × CTL_ProdDerate（線性；標籤自述「G 節無對應」），同節 OpenAI 單價列用重解 SLO 的 _Prod 值；兩列比值不再等於單價比（Hopper Luna 1.24、Astra 1.68，VR200 Sol 1.05）')
add([('Cap_In',240)],'L2','F05','回本所需 L＝L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m_fleet）：利用率用 0.6 × 0.85＝0.51，而 m_fleet 的 token 是以實際利用率 0.35 算出；同列兩個量的利用率口徑不同（改用 0.35 所需 L 0.374 → 0.545；Cap_In 第 264 列說明自述 0.72 的另一讀法）')
add([('Cap_In',240)],'L2','F05','損益兩平取 VR200 欄（L1_FleetBreakeven），m_fleet 取 2025 Hopper 60%／GB200 40% 機隊；世代不同')
add([('L1',89)],'L2','F05','＝Cap_In C240（利用率口徑與世代不一致，見 F05）')
add([('L1',52)],'L2','F05','VR200、基準成本欄的損益兩平乘積，被用來與 2025 Hopper／GB200 組合的 m_fleet 比較（Cap_In 240）')
add([('Alloc',61)],'L2','F06','支出路線服務 GW＝OpenAI 推論支出（會計帳上的營業成本）÷ 經濟口徑持有成本（含 WACC 資本回收；會計 ÷ 經濟＝0.73）')
add([('Cap_In',109),('Cap_In',218)],'L2','F06','÷ 計價倍數 1.3：依據為 Oracle 出租毛利（價格 ÷ 會計成本約 1.16），分母卻是經濟口徑持有成本；換到經濟口徑約 0.85。計價倍數的口徑與分母口徑不同')
add([('Cap_In',217),('Alloc',30)],'L2','F06','經濟口徑持有成本（IF_HoldEcon）作為支出 ÷ 成本的分母；與計價倍數依據的會計口徑不同')
add([('Cap_In',90),('Price_Frontier',45)],'L2','F07','m 分母單價＝2026-09 牌價快照 ×（1 − 折扣）× 參考請求（ISL／OSL、χ）混合；分子為 2025 營收、token 為 2025 實際流量總 token（Y2、Y6）。L1_PriceRho 1.165 只顯示、不進計算')
add([('Cap_In',90),('Cap_In',119),('Perf',98)],'L4','F08','快取命中 χ 0.55 只進價格（快取輸入 1/10 價），不進產能：Perf 第 98 列 prefill 以全部 ISL 為新鮮輸入計算（快取 prefill 第 102 列只供 Unit_Cost）；χ 改變時 m 變 −17%／+19%，缺口不變')
add([('Cap_In',109),('Cap_In',119)],'L4','F08','κ（實際流量形狀）只乘在產能端（服務 GW），價格端仍用參考請求混合單價（Y6）')
add([('Alloc',5),('Alloc',6)],'L2','F07','需求 token 為「總 token」（含重送上下文、快取輸入、思考），單價為參考請求混合單價；兩者對輸入／輸出比的假設不同（Y6）')
add([('Perf',87),('Perf',88)],'L7','F09','B*＝MAX(0,…)：SLO 不可達時回傳 0 而非文字；基準下 Hopper Astra B*＝0.45 序列/GPU（< 1）仍視為可服務')
add([('Perf',98)],'L7','F09','SLO 不可達時每 GW 產出為 0（數值），下游須自行檢查 > 0')
add([('Perf',98)],'L7','F09','TTFT 檢查（Perf 第 77 列）Hopper Astra 為「否」（6.08 s > 上限 5 s），該列無任何引用；產能照算，付費組合 Astra 15% 進 Hopper 產能')
for k in [('Theory_Rev',46),('Theory_Rev',48),('Interface',41),('Interface',138),('Interface',246),('Interface',266),('Theory_Rev',10),('Theory_Rev',12),('Theory_Rev',28),('Theory_Rev',30),('Interface',21),('Interface',31)]:
    add([k],'L7','F09','單一層級列沒有可服務守衛：SLO 不可達時輸出 0（數值）而非「SLO 不可達」，下游可能讀成零營收（情境 Serving C18＝0.7：Hopper Astra 每 GW 營收 0）')
for k in [('Cap_In',63),('Cap_In',64)]:
    add([k],'L4','F10','基準 1（不跌價、全額變現），活頁簿自算 L_total 0.643、m_fleet 0.790 只並列、不作用在 _Life 輸出')
for r in (236,241,246,251,256,261,266,271):
    add([('Interface',r)],'L4','F10','× L × m 以 CTL 基準 1 作用 → 本列＝Prod 列；活頁簿自算的 L、m 未進入（以自算值相乘約為 0.507 倍）。另 Theory_Rev D 節 _Life（不含折減）與本列（含折減）並存')
add([('Cap_In',87),('Cap_In',88)],'L2','F11','付費占比＝1 − IF_FreeShare（支出口徑 0.46）乘在 Epoch token 數上（token 口徑）（Y3）')
add([('L1',77)],'L2','F11','＝Cap_In C97：外部 token 分母用支出口徑的付費占比（Y3）')
add([('Fleet_1GW',11)],'L2','F11','1 GW 參考機隊的付費／免費 GW 以 2025 支出比（B4_Serve 0.41、B4_Free 0.46）切分，套用到全部世代（Y3）')
add([('Alloc_In',26),('Cap_In',245)],'L5','F12','κ 標為 Derived，但活頁簿內是常數 1.0；推導（Sens_Perf 第 93–94 列校準、線性內插、流量加權 1.035）在 v5.36A 報告，不在活頁簿')
add([('Cap_In',245)],'L3','F13','本列 D＝AL_Kappa_Lo、E＝AL_Kappa_Hi（數值低／高）；同頁第 109 列 D 欄用 AL_Kappa_Hi、E 欄用 AL_Kappa_Lo（m 低端／高端）——同頁 D／E 欄語意不同')
add([('Cap_In',178),('Cap_In',179),('L1',84)],'L6','F14','閉合解 τ*：令需求 token 佔滿機隊產能倒推的每則 token（明示為倒推；無任何下游公式使用）')
add([('Cap_In',181)],'L6','F14','以 τ* 倒推的閉合下免費算力占比（顯示用，無下游）')
add([('Alloc_In',24)],'L6','F15','實際利用率 0.35 與落差分解在 v5.29 同時引入（X14 (m)），說明自述「無直接證據」；沒查到由閉合倒推的紀錄，但也沒有獨立來源')
add([('Alloc_In',23)],'L2','F06','計價倍數 1.3（1.0–1.6）：依據為出租毛利（會計成本口徑），使用處的分母為經濟口徑持有成本')
add([('Cap_In',81)],'L3','F16','低／高欄為角落組合（τ 高 × 免費占比低 → m 低端）；方向正確，但同欄其他列（第 82 列 API 比例）也同向取端點，m 低端／高端是多輸入同時取極值')
add([('Cap_In',114)],'L2','F05','利用率修正＝實際利用率 ÷ IF_Util；實際利用率標籤含「× 生產折減」，IF_Util 不含折減（產能為 100% 效率）——比值同時含利用率與折減兩個效應')
add([('Alloc',61)],'L4','F17','SRC_DEM_004 有 Lo 7.5／Hi 8.8（v5.36 B1 補登），但沒有任何公式引用 SRC_DEM_004_Lo／_Hi；m_fleet、m 下限、缺口的低高欄都不含推論支出區間（S3：7.5 → m_fleet +12.0%；8.8 → −4.5%）')
add([('Cap_In',118),('Cap_In',121)],'L2','F04','上限讀法的付費產能含 IF_Util（AL_BlendPaid），點估計則以 AL_UtilActual ÷ IF_Util 抵銷；因此 m 下限隨 IF_Util 變（S3：IF_Util 0.4／0.8 → m 下限 +50%／−25%），m_fleet 不變')
# ---- 直接引用 Y 輸入的列與傳遞方式（機械） ----
def expand(n,seen=None):
    out=set()
    for p in edges.get(n,()):
        if p[0] in('NAME','RANGE'): out|=expand(p)
        else: out.add(p)
    return out
mode_rx=lambda f:f
res=[]
byrow=collections.defaultdict(list)
for k,x in cells.items(): byrow[(k[0],x['r'])].append(k)
align=pickle.load(open(sys.argv[3].replace('mech.pkl','align.pkl'),'rb')) if False else None
l7=json.load(open('docs/evidence/20261015_稽核2/31_l7.json'))
zero_rows=collections.defaultdict(set)
for sc,v in l7.items():
    for z in v['zero']: zero_rows[z].add(sc)
for r in M['rows']:
    key=(r['sheet'],r['row'])
    direct=set();modes=set()
    for k in byrow[key]:
        x=cells[k]; f=x['f']
        if not(isinstance(f,str) and f.startswith('=')): 
            if k in ymap: direct|=ymap[k]; modes.add('本列即輸入')
            continue
        for p in edges.get(k,()):
            tg=expand(p) if p[0] in('NAME','RANGE') else {p}
            ys=set().union(*[ymap.get(t,set()) for t in tg]) if tg else set()
            if ys:
                direct|=ys
                nm=p[1] if p[0]=='NAME' else (p[1] if p[0]=='RANGE' else f'{p[0]}!{p[1]}')
                short=nm.split('!')[-1].replace('$','')
                i=f.replace('$','').find(short)
                pre=f.replace('$','')[:i].rstrip()[-1:] if i>0 else ''
                post=f.replace('$','')[i+len(short):].lstrip()[:1] if i>=0 else ''
                if key in [('Cap_In',137)]: modes.add('倒算（餘額）')
                elif pre=='/': modes.add('除數')
                elif pre in('*',) or post=='*': modes.add('乘數')
                elif pre in('+','-') or post in('+','-'): modes.add('加數')
                elif 'INDEX(' in f or 'CHOOSE(' in f: modes.add('選取（INDEX／CHOOSE）')
                elif post=='/' : modes.add('被除數（乘數）')
                else: modes.add('引用')
    rec=dict(sheet=r['sheet'],row=r['row'],label=r['label'],unit=r['unit'],nform=r['nform'],npat=len(r['patterns']),
             rep_cell=r['rep'][0] if r['rep'] else '',rep_f=r['rep'][1] if r['rep'] else '',rep_v=r['rep'][2] if r['rep'] else '',
             upY=','.join(upY.get(f"{r['sheet']}!{r['row']}",[])),directY=','.join(sorted(direct)),mode='、'.join(sorted(modes)))
    L={f'L{i}':[] for i in range(1,9)}
    for code,fid,txt in FIND.get(key,[]): L[code].append(f'{fid}：{txt}')
    zr=zero_rows.get(f"{r['sheet']}!{r['row']}")
    if zr and not any(fid=='F09' for _,fid,_ in FIND.get(key,[])):
        guarded=r['sheet'] in('Alloc','Fleet_1GW','Fleet_1GW_Prod')
        if not guarded and r['sheet'] not in ('Sens_Perf',):
            L['L7'].append('機械（31_l7.py）：端點情境 '+'／'.join(sorted(zr))+' 下本列變 0（數值）；同類問題見 F09')
    if direct and not L['L8']:
        L['L8'].append(f'直接引用第 1 段 {",".join(sorted(direct))} 的輸入格；方式：{rec["mode"] or "引用"}')
    rec.update({k:('；'.join(v) if v else '—') for k,v in L.items()})
    fids=sorted({fid for _,fid,_ in FIND.get(key,[])})
    rec['fids']=','.join(fids)
    core={'F01','F02','F03','F04','F05','F06','F07','F08'}
    if set(fids)&core: rec['sev']='高'
    elif fids or any(v!='—' for k,v in rec.items() if k in('L1','L2','L3','L4','L5','L6','L7')): rec['sev']='中'
    elif rec['L8']!='—': rec['sev']='資訊（只有 L8）'
    else: rec['sev']='—'
    res.append(rec)
json.dump(res,open(sys.argv[6],'w'),ensure_ascii=False,indent=0,default=str)
cnt={f'L{i}':sum(1 for x in res if x[f'L{i}']!='—') for i in range(1,9)}
print(cnt, collections.Counter(x['sev'] for x in res))
print('L8 上游（間接）含 Y 的列',sum(1 for x in res if x['upY']))

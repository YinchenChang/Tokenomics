"""3A 逐列判讀：510 個「頁＋列」× L1–L9。
機械部分：L3（10_mech.py 同欄對位、層級常數）、L7（20_l7_closure.py 4 個端點情境）、L8（10_mech.py 上游／直接 Y 類）。
人工部分：FIND（逐列讀公式後寫入；G 編號對應報告第 3 節；量化來自 20／30／31 腳本）。只標問題，不判定對錯、不提修法。
用法：python3 50_judge.py <mech.pkl> <20_l7_closure.json> <out.json>"""
import pickle,sys,json,collections,re
M=pickle.load(open(sys.argv[1],'rb'));L7=json.load(open(sys.argv[2]))
FIND=collections.defaultdict(list)
def add(sheet,rows,code,gid,sev,txt):
    for r in rows: FIND[(sheet,r)].append((code,gid,sev,txt))
# G01 由上而下攤提閉合（Y13）
T01='由上而下年化總額（Amortize 第 39 列）＝Σ（由上而下溢價 × 服務 token），溢價＝訓練占比 ÷（1 − 訓練占比）× 服務成本 $/M（含快取命中混合）。總額 ÷（訓練＋研發 GW × 經濟持有成本）＝0.82（Hopper）、0.87（GB200）、0.88（GB300）、0.86（VR200）、0.86（RU），不等於 1；χ 設 0 時恰為 1.00（31_l9.json）。原因：服務成本按快取混合計價（快取 prefill 很便宜），服務 token 產能卻以全部輸入為新鮮 prefill 算出（第 2 段 F08），兩者相乘小於服務 GW × 持有成本'
add('Amortize',[39],'L5','G01','高',T01)
add('Amortize',[15,24,34],'L4','G01','高','由上而下溢價＝訓練占比 ÷（1 − 訓練占比）× 服務成本（快取混合）；因服務成本 × 服務 token ≠ 服務 GW × 持有成本，攤提總額少計 12–18%（見 Amortize 第 39 列）')
add('Amortize',[41,43,45,47],'L4','G01','高','縮放倍數與 (c) 預設攤提承接 Amortize 第 39 列的少計（12–18%）')
add('Amortize',[44,46,48],'L4','G01','中','(d) 營收權重攤提同樣以 Amortize 第 39 列總額為基礎（少計 12–18%）')
add('Interface',[96,114,132,98,116,134],'L4','G01','高','下游契約名稱（IF_AmortTD_*、IF_AmortDefault_*）承接由上而下總額的閉合差 0.82–0.88')
add('Interface',[99,117,135,100,118,136],'L4','G01','中','承接由上而下總額的閉合差（IF_AmortRev_*、IF_FullCostDefault_*）')
# G02 自下而上分母（Y14）
T02='自下而上攤提＝研發計畫成本 ÷ 壽命內「付費＋免費」token，列標籤卻是「回本所需單價溢價」：免費 token 不付費，以付費 token 為分母時 Luna 溢價為 8.4 倍（Hopper）／7.5 倍（VR200）、Sol 1.6–1.8 倍、Astra 1.0 倍（免費組合 Astra 0%）（30_s3.json BU_denominator_ratio）'
add('Amortize',[13,22,32],'L2','G02','高',T02)
add('Amortize',[11,12,20,21,30,31],'L2','G02','中','服務 token 合計含免費 token（B4_Free 0.46 支出口徑切分），作為攤提分母')
add('Amortize',[44,46,48],'L2','G02','中','(d) 營收權重：分子用付費營收占比，分母卻除以付費＋免費 token；同一列分子分母口徑不同')
add('Interface',[95,113,131],'L2','G02','高','IF_AmortBU_*＝Amortize 第 13／22／32 列：以付費＋免費 token 為分母的「回本所需溢價」')
add('Interface',[97,115,133],'L2','G02','中','IF_FullCost_*＝服務成本＋自下而上攤提（分母含免費 token）')
# G03 _Prod 層兩種折減（Y10）
T03='每 GW 產出的 _Prod 層＝Util 列 × CTL_ProdDerate（線性 0.85），同一瀑布的營收 _Prod 層（第 235／240／245／250 列）＝重解 SLO 後的值，比 Util 低 0.49–0.81 倍（Hopper Astra 0.486、VR200 Sol 0.808）。同一層名稱，token 與營收的折減方式不同，_Prod 層的營收 ÷ token 不再等於單價。契約第 2 條寫「_Prod＝_Util × CTL_ProdDerate」（線性）'
add('Interface',[275,280,285],'L2','G03','高',T03)
add('Interface',[276,281,286],'L4','G03','中','token 的 _Life 層＝Prod × 1（標籤自述 L、m 不作用於產能）；契約第 2 條寫「_Life＝_Prod × L × m」，名稱相同但定義不同')
add('Interface',[300,301,302,303,304,305,306,307,308,309,310],'L5','G03','低','單調檢查只驗證 _100 ≥ _Util ≥ _Prod ≥ _Life，無法偵測兩種折減方式的差異；無下游使用（只進 Checks D120）')
add('Interface',[204,205,206],'L2','G03','中','IF_FullCost_*_Prod 來自 Theory_Rev_Prod（重解 SLO），與 IFW_TokGW_*_Prod（線性）並存')
# G04 兩種 _Life（Y10）
add('Interface',[213,214,215,216],'L4','G04','高','IF_RevGW_*_Life＝Theory_Rev D 節 × L × m（不含生產折減）；同為契約名稱的 IFW_RevGW_*_Life（第 236／241／246／251 列）含重解折減。兩組 _Life 比值 0.49–0.81（Hopper Astra 0.486、Fleet Hopper 0.560、VR200 Sol 0.808）（第 2 段 F10 已列並存，本段量化）')
# G05 校準恰好決定、η_p／η_d 互補（Y12）
T05='Calib D 節以兩個擬合點聯立解兩個未知數（η_d、每層延遲），F 節擬合點「模型 ÷ 實測」恆為 1.00（Checks B14），是代數恆等，不是驗證。η_d＝3.58% 是吸收未建模開銷的擬合係數，比一般 GEMM 達成率低一個數量級以上（L9）。J5 說明「擬合結果對 η_p 不敏感」，但 G 節顯示 η_p 0.15／0.3／0.45 → η_d 0.055／0.036／0.032、每層延遲 175／161／157 µs；S3：η_p 端點 → IF_CostPre_Sol（VR200）+100%／−33%、IF_CostDec_Sol −33%／+11%、IFW_RevGWFleet_Prod（Hopper）−30%／+8%'
add('Calib',[86],'L5','G05','高',T05)
add('Calib',[86],'L9','G05','高','擬合 η_d 3.58%（GB300、Sol）；Perf 推出的 decode 有效 MFU（含草稿驗證）全部 15 欄 1.0–2.5%')
add('Calib',[75,76,77,78,79,80,81,82,83,84,85],'L6','G05','中','驗證點以擬合值重算；擬合點本身恆等，樣本外點 E／H／I 為 0.99／1.00／0.88，F／G（舊軟體）2.18／4.11；七點全部同一平台（J19）')
add('Perf',[84,90],'L9','G05','中','綁定項 15 欄全部為「算力」；同欄 decode HBM 頻寬利用率只有 1.9–34%（31_l9.json）。綁定判斷取決於擬合 η_d（3.58%），η_d 吸收了權重讀取以外的所有開銷')
# G06 L7 不對稱（Y15）
T06='組合列的可服務旗標（Fleet_1GW 第 18 列）：任一層級 SLO 不可達即令整欄變文字。L7 情境（Serving C18＝0.7、Arch E8＝160、Calib C68＝3、SLO 100）下，Luna 仍可達，但 IF_AmortBU_Luna、IF_AmortDefault_*、IF_FullCostDefault_* 全部層級變「SLO 不可達」；同時單一層級列（Interface 39／40／42／47、137、243／244、283–286；Perf 96／97／103／110／114／116／117／120；Unit_Cost 41）變 0（數值）'
add('Fleet_1GW',[20,22,23,25,26,28,29,30],'L7','G06','中',T06)
add('Amortize',[11,12,13,14,15,20,21,22,23,24,30,31,32,33,34,39,41,42,43,44,45,46,47,48],'L7','G06','中','組合旗標使本列在任一層級不可達時變文字，包括可達層級（20_l7_closure.json）')
add('Interface',[95,96,98,99,100,113,114,115,116,117,118,131,132,133,134,135,136,97],'L7','G06','高','下游契約名稱：一個層級不可達即令可達層級的攤提與全成本也變文字（例：Serving C18＝0.7 時 Interface 第 100 列 Luna 變文字）')
add('Interface',[39,40,42,47,137,215,243,244,263,283,284,285,286,19,20,22,27,29,30,32,37,101,119,213,214,233,234,238,239,253,258,273,274,275,276,278,279,280,281],'L7','G06','中','單一層級列不可達時輸出 0（數值）而非文字；與組合列的文字處理方式相反（第 2 段 F09）')
add('Perf',[96,97,103,110,114,116,117,120],'L7','G06','中','不可達時本列為 0；tok/J、VR-eq、能量閉合比也變 0，Checks B26（MAX）不受影響')
add('Unit_Cost',[15,28,41],'L7','G06','低','GPU 秒為 0 時，成本列已用 IF(>0) 改為文字；本列本身為 0')
# G07 MLPerf 對照口徑
add('Calib',[120,151,152],'L2','G07','中','MLPerf 對照混用不同輪次：GB300 interactive v6.1（2026-09）、GB200 interactive v6.0（2026-04）、VR200 v6.1 預覽類、GB300 server v6.0；Calib D152「GB300 ÷ GB200＝1.055」是 v6.1 對 v6.0')
add('Calib',[149],'L9','G07','中','模型 ÷ MLPerf＝0.70／0.49／0.69／0.62：服務產能用的同一套效率，比稽核過的基準低 30–51%；Checks B23 只顯示')
add('Calib',[150],'L5','G07','低','VR200 ÷ GB300 模型 2.525 對 MLPerf 2.575：VR200 用預覽類提交（利害關係方）')
# G08 批次口徑倒推
add('Calib',[156],'L6','G08','中','VR200 0.75＝MLPerf v6.1 Offline 比值（1.62–1.74）÷ 模型高批次比值（2.33）：由目標比值反推的校準值；其餘世代為 1（說明自述「無批次口徑實測」）。S3：0.7／1.0 → IF_ProgCost_Sol（VR200）+2.8%／−9.8%')
add('Perf_Batch',[53],'L8','G08','低','承接 Calib 第 156 列的批次口徑倍數（只在 L–N 欄＝VR200）')
# G09 Perf_Batch R/S
add('Perf_Batch',[53],'L3','G09','中','R、S 欄（VR200 FP8 rollout 情境）公式不含 CAL_BatchEtaD，同世代 L–N 欄含 0.75；兩組 VR200 欄的 η_d 口徑不同（只供 Sens_Train 使用）')
add('Perf_Batch',[14],'L3','G09','低','R、S 欄峰值改用 Spec_Rack F40（FP8 17.5），C–Q 欄用計算用峰值（第 35 列）；屬情境設計')
# G10 Cache_Store 不套 H_KV
add('Cache_Store',[16,22,28],'L4','G10','中','KV bytes/token 直接取 Arch 第 25 列，不乘 Tech_Registry H_KV；Perf 第 34 列有乘。基準 H_KV＝1，影響 0；啟用 KV 壓縮類技術時，快取儲存成本不隨之改變')
# G11 能量閉合
add('Perf',[116],'L5','G11','中','能量閉合比 3.7–6.7%：物理下限只解釋平均用電的 7% 以下；「≤ 100%」檢查實際上無法失敗（Checks B26）')
add('Perf',[112,113,114],'L9','G11','中','decode 物理下限能量 × 產出 ÷ 平均用電差一個數量級以上（15–27 倍）；與 decode MFU 1–2.5% 一致。Energy C5 端點對所有契約名稱影響 0（只進閉合檢查）')
add('Perf',[107],'L2','G11','低','pJ/FLOP＝GPU 功率 × 0.6 ÷ 計算用峰值；Hopper 峰值為 FP8，其他世代為 FP4（第 35 列），跨世代的每 FLOP 能量不同精度')
# G12 tok/J
add('Perf',[117],'L2','G12','中','分子為 100% 利用率的每架產出，分母為平均用電（配電設計 × 0.8，Inputs E10）；第 118 列按 GPU 數比例把機架電力分給 decode')
add('Interface',[27,37,47],'L2','G12','中','IF_TokPerJ_*：100% 產出 ÷ 平均用電；Inputs E10 0.7／0.9 → +14%／−11%')
# G13 訓練成本 100% 口徑
add('Interface',[55,60,64,69,73,78],'L2','G13','中','訓練與研發計畫成本 × Unit_Cost 第 8 列（經濟、100% 利用率，不除 IF_Util）；服務成本除 IF_Util 0.6。兩者對「閒置」的口徑不同')
add('Amortize',[10,19,29,40],'L2','G13','中','自下而上總額用 100% 利用率的計畫成本；由上而下總額用訓練 GW 的全額持有成本，縮放倍數（第 41 列）因此部分反映利用率口徑差')
# G14 縮放倍數與 Y11
add('Fleet_1GW',[33,34],'L9','G14','高','隱含每 GW 年家族研發計畫 3.4（Hopper）–12.1（VR200），活頁簿自己的參考範圍 1–3（Checks B51，只顯示）')
add('Amortize',[41],'L9','G14','高','縮放倍數（由上而下 ÷ 自下而上）2.2（Hopper）／4.7／5.1／8.2（VR200）／12.0（RU）；(c) 下游預設攤提＝自下而上 × 本倍數，大小由 B4_Serve（2025 支出比 0.41）決定。S3：B4_Serve 0.3／0.6 → IF_AmortDefault_Sol +62%／−54%、IF_FullCostDefault_Sol +20%／−18%；研發倍數 4.4／10.4 → 本倍數 +82%／−23%，但 IF_AmortDefault 不變')
add('Interface',[98,100,116,118,134,136],'L2','G14','高','下游預設（K6 (c)）攤提的總額由 2025 支出比 B4_Serve 決定，並套到全部世代（Y11）')
# G15 Fleet 配置（Y11）
add('Fleet_1GW',[10,12,13],'L2','G15','高','1 GW 參考機隊的服務／免費／訓練占比＝2025 OpenAI 支出比（B4_Serve 0.41、B4_Free 0.46），全部世代同值（Y11；與第 1 段 Y3 同源）')
add('Interface',[140,141,142,144,145,146,248,249,268],'L2','G15','高','付費組合營收（IF_RevGWFleet*／IFW_RevGWFleet*）＝付費 GW（B4_Serve ×（1 − B4_Free））× 產能 × 單價；B4_Serve 0.3／0.6 → −27%／+46%，B4_Free 0.35／0.6 → +20%／−26%（30_s3.json）')
add('Interface',[148],'L2','G15','中','IF_ServeShare＝B4_Serve（2025 支出比），標示「下游覆寫」')
# G16 Workload vs Serving 參考請求
add('Workload',[26,27,28,29,30,35],'L2','G16','中','任務 token 結構（例：一般聊天輸入 2,500、輸出 500、思考 0）與 Serving 參考請求（Luna ISL 8,192／OSL 1,024 含思考）是兩套獨立定義，分別進每成功任務成本與每 M token 單價（與 Y6 同類）')
add('Interface',[156,157,158,159,160],'L2','G16','低','任務 token 來自 Workload／Harness，與 IF_PriceRef／IF_Cost* 的參考請求口徑不同')
add('Workload',[13],'L5','G16','低','harness token 倍數標為「殘差倍數」（基準 1）')
add('Workload',[21],'L7','G16','低','MIN(1,MAX(0,…)) 截斷：harness 檔案 Δχ 使 χ 超出 0–1 時無提示')
# G17 恆等檢查
add('Interface',[229],'L5','G17','低','加總核對＝DeprIT＋DeprFac＋Opex − HoldAcct，而 HoldAcct 本身就是三者之和（DC_Cost 第 49 列）：恆為 0')
add('Interface',[289,290,291,292,293,294,295,296,297,298,299],'L5','G17','低','連結一致性檢查：比較的兩格中一格直接等於另一格（例：第 234 列＝第 101 列），恆為 0')
add('Fleet_1GW',[30],'L5','G17','低','各層級服務 GW 合計 − 服務 GW：由 token 反算 GW，代數上恆為 0（Checks B52）')
# G18 Price_Frontier
add('Price_Frontier',[24],'L3','G18','低','INDEX($H$6:$H$18,1／2／3) 以表內位置取 OpenAI 層級列；表格列順序改變即錯位')
add('Price_Frontier',[26],'L3','G18','低','MATCH(最低價, …, 0) 取第一個最低價模型；同價時取表內先出現者')
add('Price_Frontier',[31,33],'L7','G18','低','Sol／Astra 為「無合格」，Checks B50 只讀 Luna（C33）')
# G19 會計口徑含折現
add('Interface',[224],'L2','G19','低','IF_MaintIT＝IT 資本 × 壽命期等值費率（Inputs 第 30 列以 WACC 折現兩段費率），此值同時進會計口徑持有成本（DC_Cost 48→49 → IF_HoldAcct）')
# G20 明示倒推
add('Interface',[201],'L6','G20','低','IF_AllocImpliedNk：列標籤自述「2025 支出比反推」（明示倒推）')
# G21 L1
add('Calib',[112,113],'L1','G21','低','每專家參數＝（總 − 啟用）÷（層數 ×（routed − 啟用））假設 61 層全為 MoE 層；DeepSeek-R1 前 3 層為 dense。只影響 H 節 MLPerf 對照')
# G24 Tech_Registry
add('Tech_Registry',[25,26,27,28],'L7','G22','低','EXP(SUMPRODUCT(LN(P)))：任一 P ≤ 0 即 #NUM!；基準 P 全為 1')
# Spec_Rack／Serving
add('Spec_Rack',[33],'L9','G23','低','RU 3,600 W／封裝為推估（Interested-party；只進能量下限）；F 欄以 SRC_HW_046×1000，其他欄為單一 SRC')
SEVORD={'高':3,'中':2,'低':1}
out=[]
for x in M['rows']:
    k=(x['sheet'],x['row']);fs=FIND.get(k,[])
    cols={c:[] for c in ['L1','L2','L3','L4','L5','L6','L7','L9']}
    for code,gid,sev,txt in fs:
        if code in cols: cols[code].append(f'[{gid}] {txt}')
    l8=''
    if x['directY']: l8=f"直接引用 {','.join(x['directY'])} 類輸入"
    elif x['upY']: l8=f"上游含 {','.join(x['upY'])}"
    for code,gid,sev,txt in fs:
        if code=='L8': l8=(l8+'；' if l8 else '')+f'[{gid}] {txt}'
    sev=max([SEVORD[s] for _,_,s,_ in fs if _ !='L8'] or [0])
    sevs={3:'高',2:'中',1:'低',0:('資訊（只有 L8）' if l8 else '—')}[sev]
    out.append(dict(sheet=x['sheet'],row=x['row'],label=x['label'],unit=x['unit'],nform=x['nform'],npat=len(x['patterns']),
        rep_cell=x['rep'][0] if x['rep'] else '',rep_f=x['rep'][1] if x['rep'] else '',rep_v=x['rep'][2] if x['rep'] else '',
        **{c:('；'.join(v) if v else '—') for c,v in cols.items()},L8=l8 or '—',upY=','.join(x['upY']),directY=','.join(x['directY']),
        gids=','.join(sorted({g for _,g,_,_ in fs})),sev=sevs,users=x['users']))
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False,indent=0,default=str)
c=collections.Counter()
for o in out:
    for k in ['L1','L2','L3','L4','L5','L6','L7','L9']:
        if o[k]!='—': c[k]+=1
    if o['L8']!='—': c['L8']+=1
    if o['directY']: c['L8直接']+=1
print(dict(c),collections.Counter(o['sev'] for o in out))
missing=[k for k in FIND if k not in {(o['sheet'],o['row']) for o in out}]
print('FIND keys not in list',missing)

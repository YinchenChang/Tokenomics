"""3B 逐列判讀：441 頁＋列 × L1–L9。機械部分取自 10_mech.json（結構、文字／0 分支、上游 Y、下游契約名稱、引用數）；
人工部分為 FIND（逐列讀公式後寫入；B 編號對應報告第 3 節；量化來自 30_s3.json、31_extra.json 與 20_eval.py）。
只標問題，不判定對錯、不提修法。用法：python3 50_judge.py <out.json>"""
import json,sys,collections
M={(v['sh'],v['r']):v for v in json.load(open('docs/evidence/20261015_稽核3B/10_mech.json'))}
FIND=collections.defaultdict(list)
def add(keys,code,bid,txt):
    for k in keys: FIND[k].append((code,bid,txt))
R=lambda sh,*rs:[(sh,r) for r in rs]
HIGH=set()
# B01 Q1／Q2 分子分母口徑
add(R('Alloc',47,48,49),'L2','B01','研發 GW（自下而上物理下限，未乘 L1_ScaleRD 10.8）與服務 GW（token 路線 0.183，為支出路線 0.898 的 1/4.9）相加相除；兩者相對 OpenAI 2025 實際的偏小倍數不同。改用支出路線服務 GW，Q1 由 0.332 → 0.092；研發端 × ScaleRD、服務端用支出路線，Q1＝0.522（對照支出比 0.588）')
add(R('Alloc',47,48),'L2','B01','服務 GW 以 IF_Util 0.6 的產能換算；若用實際利用率 0.35（Alloc_In C24），Q1 0.332 → 0.225')
add(R('Alloc',29),'L2','B01','各世代服務 GW＝token 路線合計 × 世代占比，進 Q2 的成本分母（同 B01 口徑）')
HIGH|={'B01'}
# B02 隱含 N×k
add(R('Alloc',56,57),'L6','B02','由 2025 支出比反推研發 GW（「使支出比相等」型倒推），再 ÷ 家族計畫 GW 年得隱含 N×k 5.36；服務 GW 用 token 路線。改用支出路線服務 GW，隱含 N×k＝26.4（×4.9）')
add(R('Alloc',55),'L2','B02','訓練支出 ÷（推論＋訓練支出）是會計支出比，對照的是 GW 比（經濟持有成本口徑；Y 類 F06 同型）')
add(R('L1',68),'L5','B02','L1_ScaleRD＝SRC_DEM_006 ÷ L1_Ans3：殘差型係數（12 $B ÷ 1.11 $B）；分母取 VR200 持有成本與自下而上研發 GW，訓練世代改 Hopper／GB200 → −66%／−20%')
HIGH|={'B02'}
# B03 訓練世代 VR200 用於 2025
add(R('Alloc',33,34,37,38,39,40,41,43,44),'L2','B03','2025 穩態年度的研發 GW 與研發成本以訓練世代 IF_TrainGenDefault＝VR200（2026 起出貨）計算；同頁服務端用 2025 的 Hopper 0.6／GB200 0.4。訓練世代改 Hopper／GB200：IF_AllocQ1 +95%／+40%，IF_AllocRDGW +267%／+74%，L1_Ans3 +191%／+25%，L1_ScaleRD −66%／−20%')
add(R('Train_In',16,17),'L2','B03','J13 決定的「下游預設訓練世代 VR200」同時被 Alloc（2025 年度）引用；同一格兼作「未來預設」與「2025 實際」')
add(R('L1',37,38,39),'L2','B03','問 1–3 標為「2025 穩態年度」，研發端用 VR200（見 Alloc 第 33–44 列）')
HIGH|={'B03'}
# B04 RL rollout token 倒推
add(R('Train_In',34),'L6','B04','說明自述「基準值校到 VR200 上 RL ÷ 預訓練 GPU 小時約 Luna／Sol 0.3、Astra 1.0」，v5.6 又「為使 GPU 小時不變」上調 2/2/8 → 2.36/2.36/9.6：輸入由目標比值倒推')
add(R('L1',33),'L6','B04','L1_RLshare_Astra_VR200 1.127 對外部 Grok 4「約 1 倍」判「±20% 內」；但輸入本身就是校到 1.0（Train_In C34），屬循環驗證')
add(R('L1',32),'L6','B04','Sol 0.371 由同一校準（目標 0.3）產生；與 R1 0.055 比較「差距 >20%」')
add(R('Training',53,78),'L6','B04','承接 Train_In C34 的倒推值；× 0.3／× 3 → IF_AllocQ1 −38%／+62%，IF_AllocRDGW −47%／+135%，IF_PostShareGPUh_Sol −56%／+87%')
HIGH|={'B04'}
# B05 Perf_Batch 0＝不可達被當數值 0
add(R('Training',59,60,84,95),'L7','B05','引用 Perf_Batch 第 103（或 101）列，該列以 0 表示「SLO 不可達」（IF(C88>0,1e6/C88,0)），本列照用 0，沒有守衛')
add(R('Training',65,75,86,90,97,100,104,105,106,120,123,78,77,111),'L7','B05','不可達時 rollout／合成資料／評測 GPU 小時變成 0（成本變小而非不可算）。批次速度下限 Train_In E31：20→80 時 Hopper Astra 為 0；→100 時 Hopper–GB300 Astra 全 0；→150 全 0。IF_AllocQ1 隨之 0.332→0.459→0.612→0.225（非單調）；L1_RLshare_Astra 1.13→2.19→4.40→0.51')
add(R('Training',77),'L7','B05','RL 有效 MFU 在 rollout GPU 小時為 0 時會失真（分母只剩 trainer）')
HIGH|={'B05'}
# B06 回本所需實收單價 世代口徑
add(R('L1',93),'L2','B06','回本所需實收單價用 VR200 欄損益兩平乘積 0.1505，對照的機隊實收 1.548 $/M 是 2025 Hopper／GB200 機隊（m_fleet × C90）。同式改用 2025 組合 0.6／0.4：所需 3.21 $/M（> 1.55，P 欄判讀「回本」反轉）；Hopper 8.70、GB200 1.57、GB300 1.49')
add(R('L1',53),'L2','B06','L1_FleetMargin 3.39 為 VR200 欄、L＝m＝1；同式代入 L_total 0.643 與 m_fleet 0.790：VR200 1.72、2025 組合 0.48（< 1）')
add(R('L1',93),'L2','B06','L_total 為未折現的壽命期平均；持有成本含 WACC 10% 資本回收。以 10% 現值加權，L_total 0.643 → 0.683（+6%）')
HIGH|={'B06'}
# B07 L1 外部對照口徑（每架 vs 每 GW）
add(R('L1',59),'L1','B07','模型值是每 GW 產出比（1.456）；外部 M 欄是 MLPerf 72 GPU 系統（每架）輸出 tok/s 比 1.043。換成每 GW（× 機架數 6,764 ÷ 6,969）＝1.012；P 欄「差距 >20%」含單位差')
add(R('L1',60),'L1','B07','外部 2.575 是每架比；換成每 GW（× 4,052 ÷ 6,764）＝1.542，對模型 1.565 在 ±2% 內；P 欄判「差距 >20%」來自單位不同。本名稱在下游契約第 3 節列為每 MW 收入的 q')
add(R('L1',31),'L2','B07','模型為 100% 時數持有成本；外部 3.57 為 85% 利用率、9.12% 資金成本、6 年的租金門檻。只對齊利用率：2.552 ÷ 0.85＝3.00（比值 0.84，在 ±20% 內），P 欄判「差距 >20%」')
add(R('L1',61,62,63,64,65),'L2','B07','本列＝harness 成本比 ÷ 世代成本比（比值的比值）；外部 M 欄＝ARC-AGI-3 Provider Adapter ÷ 標準 harness 的成本比 0.664（單純 harness 比，且是成本不是每成功任務成本）。Har_In 第 19 列說明亦寫「ARC 結果無法換算為此倍數」')
add(R('L1',35),'L2','B07','模型值＝付費服務每 GW 理論營收（IF_Util 0.6、2026 單價、Hopper 0.57）；外部＝OpenAI 2025 總營收 ÷ 平均總 GW（含訓練，GW 口徑未明）。判「±20% 內」、說明「同量級即可閉合」；同簿 m_fleet 路線缺口 2.2 倍')
add(R('L1',35),'L2','B07','Hopper 占機隊 0.57（Checks I46 對帳常數）與 Alloc_In C9 的 0.60 是同一 2025 機隊的兩個值')
HIGH|={'B07'}
# B08 harness 輪數倍數以對照證據校準
add(R('Har_In',12),'L6','B08','選定檔案輪數倍數 0.7 說明「以 ARC-AGI-3『少用約 49% token』校準」；Harness 第 45 列再拿 0.51 作對照（循環）。Har_In E72 自述「適用範圍不明」')
add(R('Harness',45),'L6','B08','選定 ÷ 標準 token 比 0.589／0.493 與 ARC 0.51 對照；輸入（Har_In 第 12 列）已依此校準')
add(R('Harness',136,137,138,147,151,152,153),'L6','B08','選定檔案的 R 與前緣受校準輸入支配：輪數倍數 0.5／1 → IF_HarR_Sol（Coding）−31%／+49%；時間範圍倍數 1／4 → +25%／−15%。基準 w＝0，_現行_ 列不受影響')
HIGH|={'B08'}
# B09 Astra 預訓練算力一個數量級
add(R('L1',36),'L9','B09','L9：Astra 預訓練 6.84e25 FLOP，對 Epoch 估計 1e27（SRC_MOD_055，區間 5e26–2e27）低 14.6 倍（一個數量級以上）；已知為 J8 缺口，L1_AstraScale 並列')
add(R('Train_In',25),'L9','B09','Astra 預訓練 token 60 T（Assumed，區間 30–100T）× 啟用 180B → 低於外部錨點一個數量級；若取 60 × 14.6 T：IF_AllocQ1 +92%、IF_AllocRDGW +252%、IF_ProgGWyr_Astra +571%、L1_ScaleRD −72%')
add(R('Training',31,35,36,106,120),'L9','B09','Astra 欄預訓練量承接 Train_In E25（低於外部錨點 14.6 倍）')
add(R('L1',67),'L5','B09','L1_AstraScale＝外部 ÷ 自下而上（殘差型係數；說明「下游校準用，不得當產能」）')
HIGH|={'B09'}
# 中
add(R('Alloc',72,73,74,75,76,77,78,81,82,83,84,85,86,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102),'L4','B10','敏感度表以閉式公式重寫 A–D 節推導鏈（O、P 欄用 IF(占比>0,…,0) 加總）；W 欄自我檢查只驗「輸入全為基準」的重算（全 0），不驗端點情境；機制有兩份')
add(R('Alloc',72,73,74,75,76,77,78,81,82,83,84,85,86),'L7','B10','O／P 欄：世代占比 > 0 且不可達時回傳文字；占比 0 的不可達世代以 0 略過（屬設計）')
add(R('Harness',151,152,153),'L7','B11','p_min（Har_In C8）0.5 時前緣＝Sol｜選定 0.0213；0.7 → Astra｜選定 0.0877（4.1 倍）；≥ 0.75 → 文字「無合格」，IF_FrontSuccVR 變文字（下游契約名稱）')
add(R('Harness',126,129,132),'L7','B11','IF(p>0, 營收 ÷ p, 0)：p＝0 時每成功任務營收回 0（數值），同頁成本列回文字')
add(R('L1',48),'L5','B12','說明「基準約 11.5T」「低端約 7.7T」與現值 16.48、重算低端 10.18 不符（說明數字未隨輸入更新）')
add(R('L1',49),'L5','B12','說明「與兩路線差約 15 倍同源」；現 L1_ScaleServe＝4.92')
add(R('Cap_In',172,174),'L5','B12','說明「8.23 × 10⁹」「現值 0.465」與現值 8.44e9、0.453 不符')
add(R('Cap_In',228),'L2','B13','ρ 低端＝Luna ÷ Sol 每 token 單價 0.05；降級後硬體的價值比應以每 GW 營收計時為 0.163（Luna 每 GW 產出較高）；L_total 低端 0.342 → 0.358')
add(R('Cap_In',232,233,234),'L2','B13','L 為未折現的連續平均（見 B06）；且只並列、未作用（第 2 段 F10）')
add(R('L1',86,87,88),'L5','B13','L 拆分只顯示；P88 判讀以 Gov_Map K597:L597 區間 0.3–1.0')
add(R('Train_In',13),'L2','B14','研發倍數取自 Epoch「最終訓練占研發支出」（支出口徑）乘在 GPU 小時上（第 1 段 U 類）')
add(R('L1',34),'L6','B14','L1_FinalTrainShare＝1 ÷ Train_In C13；C13 本身取自同一組 Epoch 比例（4.4–10.4 倍），「落在外部區間」為定義上成立')
add(R('Theory_Rev',18,20,36,38,54,56),'L2','B15','全成本＝服務成本＋攤提；攤提（Amortize）把單一模型的研發計畫成本分到「1 GW 參考機隊 × 商業壽命」的 token 上，模型實際服務多少 GW 沒有輸入（由上而下縮放倍數 VR200 8.18）')
add(R('Theory_Rev',90,91,92,93),'L4','B16','H 節 _Life（不含折減）與 Interface G 節 IFW_*_Life（含折減）並存，VR200 機隊 48.72 對 38.11（0.78 倍）；兩個名稱都在下游可取（第 2 段 F10 同源）')
add(R('Theory_Rev',96,97,98,99),'L5','B16','自我檢查比較的是同一公式的兩個引用（Interface _Life ＝ Theory_Rev × L × m），恆為 0；只能驗證連結')
add(R('Theory_Rev',11,29,47),'L7','B17','單一層級列無可服務守衛：Perf 產能為 0（不可達）時營收輸出 0（第 2 段 F09 同源）')
add(R('Cap_In',115,118),'L4','B18','第 2 段 F04：生產折減線性 × 0.85，與 _Prod 頁的重解 SLO 不同（本段只確認列仍在）')
add(R('L1',79),'L4','B18','L1_TokCeiling 承接 Cap_In C118（第 2 段 F04）')
add(R('Cap_In',256),'L5','B18','第 2 段 F03：驗算差恆為 0')
add(R('Cap_In',106,107),'L2','B19','程式代理實收用 2026-09 Sol 牌價 × 2025 前後的 Requesty／Pegatron 組合（第 1 段 Y2 同型）；只作對照（Cap_In 152、L1 83）')
add(R('Cap_In',263),'L5','B19','ρ 只顯示、不進 m（第 2 段 F07）')
add(R('Training',74),'L2','B20','標為「推論型」，但以 trainer GPU 小時 ÷ 3（訓練 MFU）計價')
add(R('Training',97,100),'L4','B20','合成資料與評測 token 全數以 decode GPU 秒計（沒有 prefill 項）')
add(R('Training',36),'L9','B21','L9 對照：以本頁公式代入 DeepSeek V3（啟用 37B、14.8T、序列 4,096、H800 FP8）得 2.37M GPU 小時，對實際 2.664M 為 0.89 倍（MFU 取 0.20 時 1.11 倍）；量級相符')
add(R('Training',77),'L9','B21','L9：RL 有效 MFU 6.5%–10.6%（rollout 以批次 SLO 計價）；無外部對照，未標出')
add(R('L1',30),'L9','B21','L9：持有成本 2.0 對 CoreWeave 隨需牌價 10.5（5 倍）；說明已解釋（利潤、閒置、風險），未標出')
add(R('Har_In',48),'L2','B22','第 1 段：Sol 50% 時間範圍 8 h 低於 GPT-5.6 Sol 實測 11.3 h；Astra 16 h 為量測上限附近')
add(R('Har_In',19,31),'L6','B22','時間範圍倍數為 Assumed，說明自述「ARC 結果無法換算」「只作對照」')
SEVHIGH=HIGH
res=[]
for (sh,r),m in M.items():
    L={f'L{i}':[] for i in range(1,10)}
    for code,bid,txt in FIND.get((sh,r),[]): L[code].append(f'{bid}：{txt}')
    if m['Y']:
        dn=m['down']; ex=[x for x in dn if not x.endswith(('_Lo','_Hi'))][:4]
        L['L8'].append(f"上游含第 1 段 {','.join(m['Y'])}；"+(f"傳到下游契約名稱 {m['ndown']} 個（例：{'、'.join(ex)}）" if dn else '未傳到任何 IF_／IFW_／IFC_／L1_ 名稱'))
    bids=sorted({b for _,b,_ in FIND.get((sh,r),[])})
    if set(bids)&SEVHIGH: sev='高'
    elif bids: sev='中'
    elif m['Y'] and m['down']: sev='資訊（只有 L8）'
    else: sev='—'
    res.append(dict(sheet=sh,row=r,label=m['label'],nform=m['nform'],npat=m['npat'],nusers=m['nusers'],users='、'.join(m['users'][:6]),
        upY=','.join(m['Y']),ndown=m['ndown'],down='、'.join(m['down'][:10]),bids=','.join(bids),sev=sev,**{k:('；'.join(v) if v else '—') for k,v in L.items()}))
json.dump(res,open(sys.argv[1],'w'),ensure_ascii=False,indent=0)
cnt={f'L{i}':sum(1 for x in res if x[f'L{i}']!='—') for i in range(1,10)}
print(cnt,collections.Counter(x['sev'] for x in res))
print('高 by B',collections.Counter(b for x in res if x['sev']=='高' for b in x['bids'].split(',') if b in SEVHIGH))

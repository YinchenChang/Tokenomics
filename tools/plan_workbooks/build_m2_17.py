# 第二部分：3_m重算、1_總覽、6_敏感度、7／8 不確定清單、9_前置格清單、0_說明
import json as _j
T = "'5_每GW產出'"
Hs = "'4_持有成本'"
def tok(col): return f"{T}!{col}${PR['tokgw']}"
M = sheet('3_m重算', [7, 40, 62, 20, 12, 22, 18, 12])
M['A1'] = 'm 的逐步重算（全部為公式；改 2_輸入 的藍字即可看到每一步怎麼變）'; M['A1'].font = TITLE
M['A2'] = 'm（L1_MFleet，機隊變現率）＝ OpenAI 2025 營收 ÷（機隊付費 token × 2025 機隊口徑單價）。每一步列出對應的 Tokenomics 格與原值，最後一欄為差異。'; M['A2'].font = NOTE
hdr(M, 4, ['步驟', '項目', '白話說明與公式', '值', '單位', '原活頁簿位置', '原活頁簿值', '差異'])
mr = [5]; MR = {}
def mrow(key, lab, expl, f, unit, src=None, sect=None, fmt='#,##0.0000'):
    if sect:
        r = mr[0]; mr[0] += 1; M.cell(r, 1, sect).font = BOLD
        for i in range(1, 9): M.cell(r, i).fill = SEC
    r = mr[0]; mr[0] += 1; MR[key] = r
    M.cell(r, 1, key).font = NOTE
    M.cell(r, 2, lab).font = BLACK; M.cell(r, 2).alignment = WRAP
    M.cell(r, 3, expl).font = NOTE; M.cell(r, 3).alignment = WRAP
    c = M.cell(r, 4, f); c.font = BLACK; c.number_format = fmt
    M.cell(r, 5, unit).font = BLACK
    if src:
        sh, a = src
        M.cell(r, 6, f'{sh}!{a}').font = NOTE
        ov = V(sh, a); c2 = M.cell(r, 7, ov); c2.font = BLUE; c2.number_format = fmt
        if isinstance(ov, (int, float)):
            d = M.cell(r, 8, f'=IF(G{r}=0,D{r}-G{r},D{r}/G{r}-1)'); d.number_format = '0.000%'
    return r
def m(k): return f'D{MR[k]}'
mrow('S1', 'Hopper 每 GW 年產能（付費，基準利用率）', '＝IF_Util ÷ Σ（付費層級組合 ÷ 該層級每 GW 產出）。調和平均：每 GW 時間按層級組合分給 Luna／Sol／Astra，大模型每 token 耗時多。',
     f'=IN_Util/(IN_MixP_L/{tok("D")}+IN_MixP_S/{tok("E")}+IN_MixP_A/{tok("F")})', 'M tok/年', ('Alloc', 'C29'), sect='第 4 層：每 GW 產能（由 5_每GW產出 的 roofline 結果組合）', fmt='#,##0')
mrow('S2', 'GB200 每 GW 年產能（付費）', '同上，GB200 欄', f'=IN_Util/(IN_MixP_L/{tok("G")}+IN_MixP_S/{tok("H")}+IN_MixP_A/{tok("I")})', 'M tok/年', ('Alloc', 'D29'), fmt='#,##0')
mrow('S3', 'Hopper 每 GW 年產能（免費）', '同上，用免費層級組合（Luna 0.9、Sol 0.1）', f'=IN_Util/(IN_MixF_L/{tok("D")}+IN_MixF_S/{tok("E")}+IN_MixF_A/{tok("F")})', 'M tok/年', ('Alloc', 'C30'), fmt='#,##0')
mrow('S4', 'GB200 每 GW 年產能（免費）', '同上', f'=IN_Util/(IN_MixF_L/{tok("G")}+IN_MixF_S/{tok("H")}+IN_MixF_A/{tok("I")})', 'M tok/年', ('Alloc', 'D30'), fmt='#,##0')
mrow('S5', '機隊每 GW 年產能（付費）', '＝Σ 世代 GW 占比 × 各世代產能（Hopper 0.6、GB200 0.4）', f'=(IN_ShareH*{m("S1")}+IN_ShareG*{m("S2")})/(IN_ShareH+IN_ShareG)', 'M tok/年', ('Alloc', 'C33'), fmt='#,##0')
mrow('S6', '機隊每 GW 年產能（免費）', '同上', f'=(IN_ShareH*{m("S3")}+IN_ShareG*{m("S4")})/(IN_ShareH+IN_ShareG)', 'M tok/年', ('Alloc', 'C34'), fmt='#,##0')
mrow('S7', 'API 需求 token（全年）', '＝API 每分鐘 token × 525,600 分鐘 × 全年平均比', '=IN_APItpm*1000000000*525600*IN_APIratio/1000000', 'M tok/年', ('Alloc', 'C5'), sect='第 3 層：免費 ÷ 付費 token 比 r（需求面）', fmt='#,##0')
mrow('S8', 'ChatGPT 需求 token（全年）', '＝每日訊息數 × 每則 token τ × 365', '=IN_Prompts*1000000000*IN_Tau*365/1000000', 'M tok/年', ('Alloc', 'C6'), fmt='#,##0')
mrow('S9', 'ChatGPT 免費 token', '＝ChatGPT token × 免費占比', f'={m("S8")}*IN_FreeShare', 'M tok/年', ('Alloc', 'C7'), fmt='#,##0')
mrow('S10', '付費 token（API＋ChatGPT 付費）', '＝API ＋ ChatGPT − 免費', f'={m("S7")}+{m("S8")}-{m("S9")}', 'M tok/年', ('Alloc', 'C9'), fmt='#,##0')
mrow('S11', '免費 ÷ 付費 token 比 r', '機隊產能要先扣掉服務免費用戶的部分；r 越大，留給付費 token 的產能越少', f'={m("S9")}/{m("S10")}', 'x', ('Cap_In', 'C112'))
mrow('S12', '機隊每 GW 年持有成本（世代加權）', '＝Σ 世代占比 × 各世代每 GW 年經濟持有成本（4_持有成本）', f"=(IN_ShareH*{Hs}!D${HR['hold']}+IN_ShareG*{Hs}!E${HR['hold']})/(IN_ShareH+IN_ShareG)", '$B/GW·年', None, sect='第 2 層：服務 GW（支出路線）與利用率')
mrow('S13', '支出路線服務 GW', '＝推論支出 ÷ 每 GW 年持有成本：OpenAI 花在服務推論的錢，等於擁有多少 GW 的持有成本', f'=IN_Spend/{m("S12")}', 'GW', ('Alloc', 'C70'))
mrow('S14', '有效服務 GW（經計價倍數與 κ）', '＝服務 GW ÷ 計價倍數 × κ。計價倍數 <1 表示 Azure 計價低於經濟持有成本，所以同樣的錢買到更多 GW', f'={m("S13")}/IN_SpendBasis*IN_Kappa', 'GW', ('Cap_In', 'C109'))
mrow('S15', '利用率修正', '＝實際利用率 × 生產折減 ÷ IF_Util（把每 GW 產能的「基準利用率」口徑換成實際）', '=IN_UtilAct*IN_ProdDerate/IN_Util', 'x', ('Cap_In', 'C114'))
mrow('S16', '機隊付費 token', '＝有效服務 GW × 利用率修正 ÷（1 ÷ 付費產能 ＋ r ÷ 免費產能）。分母：每產出 1 個付費 token，同時要產出 r 個免費 token，各自耗用 GW 年', f'={m("S14")}*{m("S15")}/(1/{m("S5")}+{m("S11")}/{m("S6")})', 'M tok/年', ('Cap_In', 'C116'), fmt='#,##0')
mrow('S17', '各世代付費 token 2025 混合有效單價', '＝Σ 付費層級組合 × 2025 層級單價 ×（1 − 有效折扣）', '=(IN_MixP_L*IN_Px_L+IN_MixP_S*IN_Px_S+IN_MixP_A*IN_Px_A)*(1-IN_Disc)', '$/M tok', ('Alloc', 'C148'), sect='第 1 層：單價、token 與 m')
mrow('S18', '機隊口徑 2025 混合有效單價', '＝以各世代付費產能加權的 S17（所有層級皆可達時，各世代同值）', f'=(IN_ShareH*{m("S1")}*{m("S17")}+IN_ShareG*{m("S2")}*{m("S17")})/(IN_ShareH*{m("S1")}+IN_ShareG*{m("S2")})', '$/M tok', ('Alloc', 'C151'))
mrow('S19', '營收折合的 token（按 2025 牌價扣折扣）', '＝營收 ÷ 混合有效單價：如果每個 token 都照牌價收費，營收只買得到這麼多 token', f'=IN_Rev*1000000000/{m("S18")}', 'M tok/年', None, fmt='#,##0')
mrow('m', 'm（機隊變現率）', '＝營收 ÷（機隊付費 token × 混合有效單價）＝ S19 ÷ S16', f'=IN_Rev*1000000000/({m("S16")}*{m("S18")})', 'x', ('Cap_In', 'C119'))
M.cell(MR['m'], 2).font = BOLD; M.cell(MR['m'], 4).font = Font(name=F, bold=True, size=11)
for i in range(1, 9): M.cell(MR['m'], i).fill = KEY
mrow('floor', '對照：m 的物理下限（機隊付費 token 上限讀法）', 'Tokenomics 以 MAX(m, 下限) 輸出；基準下 m 高於下限，所以下限不綁定', '=G' + str(mr[0]), 'x', ('Cap_In', 'C121'))
M.cell(MR['floor'], 4).value = f'=G{MR["floor"]}'
mrow('L1', '對照：L1 頁 L1_MFleet', '', f'={m("m")}', 'x', ('L1', 'D78'))
M.freeze_panes = 'D5'

# ---------------------------------------------------------------- 6_敏感度
S = sheet('6_敏感度', [6, 30, 40, 12, 12, 12, 12, 12, 12, 10, 50])
S['A1'] = 'm 的單變數敏感度（v15.3 執行；m 的前置格 v16.0／v17.0 未變，結果仍適用；每個輸入改到 Gov_Map 低端與高端，各以 LibreOffice 重算整本 Tokenomics 一次）'; S['A1'].font = TITLE
S['A2'] = '藍字＝重算結果（數值）；承重度＝弧彈性 ln(m高/m低) ÷ ln(輸入高/輸入低)；擺動＝|m高 − m低| ÷ m 基準。只測單一變數，未測交互作用。'; S['A2'].font = NOTE
hdr(S, 4, ['#', '輸入', '活頁簿位置', '低值', '高值', 'm（低值）', 'm（高值）', '承重度', '擺動', '排名', '說明'])
sj = _j.load(open('sens.json', encoding='utf-8'))
res = sj['res']; base = res['0_base'][0]
S['B5'] = 'm 基準（v15.3 重算重現；＝v17.0 值）'; S['F5'] = base; S['F5'].font = BLUE; S['B5'].font = BOLD
notes = {1: '用量加權（B2）；推理占比曲線為 Assumed', 2: 'MLPerf v6.0 同軟體配對（B3）', 3: '證據範圍 0.67–1.05', 4: '無實測', 5: 'Microsoft 對 OpenAI 計價未找到', 9: '情境值，非估計值', 8: 'Sol 參考請求輸入長度；與 κ 同屬流量形狀（7 頁第 1 項）', 10: '同上（輸出長度）', 6: '頂層模型參數未揭露', 7: 'Batch 半價為牌價；占比與企業折扣找不到',
         11: '無區間；chat 端暫設 0.5–0.7，不算彈性', 12: '查核營業成本 7.5～投資人文件 8.8', 20: '點估計不變（IF_Util 約掉）；低端 0.4 時 Tokenomics 的物理下限（上限讀法）0.509 高於點估計而綁定（m＝MAX(點估計, 下限)）', 21: '無正式區間；暫設，不算彈性', 27: '批次口徑不進機隊產能'}
SROW = {}
r = 6
for no, nm, lo, hi in sj['cases']:
    SROW[no] = r
    k = list(lo.keys())
    S.cell(r, 1, no); S.cell(r, 2, nm); S.cell(r, 3, '；'.join(k))
    lv = list(lo.values()); hv = list(hi.values())
    S.cell(r, 4, lv[0] if len(lv) == 1 else '；'.join(str(x) for x in lv)); S.cell(r, 5, hv[0] if len(hv) == 1 else '；'.join(str(x) for x in hv))
    ml = res[f'{no}_lo'][0]; mh = res[f'{no}_hi'][0]
    S.cell(r, 6, ml).font = BLUE; S.cell(r, 7, mh).font = BLUE
    if len(lv) == 1:
        S.cell(r, 8, f'=IF(OR(D{r}<=0,E{r}<=0,F{r}<=0,G{r}<=0),"—",LN(G{r}/F{r})/LN(E{r}/D{r}))').number_format = '0.00'
    else:
        S.cell(r, 8, '—')
    S.cell(r, 9, f'=ABS(G{r}-F{r})/$F$5').number_format = '0%'
    S.cell(r, 11, notes.get(no, '')).font = NOTE
    for i in (2, 3, 11): S.cell(r, i).alignment = WRAP
    for i in (6, 7): S.cell(r, i).number_format = '0.000'
    r += 1
last = r - 1
for rr in range(6, last + 1):
    S.cell(rr, 10, f'=RANK(I{rr},$I$6:$I${last})')
S.freeze_panes = 'C6'

# ---------------------------------------------------------------- 7／8 不確定清單
def swing(no): return f"='6_敏感度'!I{SROW[no]}"
def elas(no): return f"='6_敏感度'!H{SROW[no]}"
U7 = sheet('7_不確定_搜尋', [6, 22, 18, 10, 10, 40, 46, 40, 40, 30, 14])
U7['A1'] = '最不確定、可以「搜尋」解決的假設（公開資料或付費報導）'; U7['A1'].font = TITLE
U7['A2'] = '排序依據：對 m 的擺動 × 證據強度。分工：C＝chat 端可在公開網路找到；A線上＝Andy 在付費牆或需登入的來源找。擺動與承重度連結 6_敏感度。'; U7['A2'].font = NOTE
hdr(U7, 4, ['優先', '假設', '現值（區間）', '擺動', '承重度', '為什麼不確定', '要找的證據（找到就能定案的口徑）', '可能來源與管道', '本串已做過的搜尋', '找到後要改的格', '分工'])
items7 = [
 (4, 'Astra 2025 單價（用量加權）', '4.5（3.3–5.9）$/M', 1, '各模型 token 占比完全未公開；目前以 Azure 季別支出當量指數、再假設 GPT-5 後推理占比 ×2', '2025 年 OpenAI API 與 ChatGPT 中 o1／o3／GPT-5 thinking 對 4o／4.1／GPT-5 的 token 或訊息占比，按月或按季', 'The Information、FT、SemiAnalysis（付費；後者不可單獨使用）；OpenRouter 模型排行歷史（代理值）；OpenAI 官方部落格與 DevDay 數字', 'Altman 2025-08 推理模型日用比例（用戶比例，非 token）；OpenRouter 推理模型占比年初≈0→年底 >50%；各模型 token 占比：已搜尋，未找到', 'Cap_In C280／D280／E280', 'A線上＋C'),
 (2, '計價倍數（推論支出 ÷ 持有成本）', '0.85（0.73–1.17）', 5, 'Microsoft 對 OpenAI 的實際計價（牌價、折扣或成本加成）未公開；現值由 Oracle 出租毛利 14% 與經濟／會計成本比推得', 'Microsoft 對 OpenAI 的 GPU 時價或折扣、Azure AI 毛利；OpenAI–Oracle、OpenAI–CoreWeave 合約的每 GW 年單價', 'The Information、FT（付費）；Microsoft 10-K／法說會（Azure 毛利）；Oracle RPO 揭露；CoreWeave 10-K', '只找到 Zitron 文件與 The Register 轉述；計價條款在付費報導', 'Alloc_In C23', 'A線上'),
 (1, '請求形狀 κ 與實際流量形狀（含參考 ISL／OSL、快取命中）', 'κ 1.0（0.65–1.2）；Sol ISL 16,384、OSL 2,048；χ 0.55', 3, '擺動前五中的第一名。κ 由各類流量的 ISL／OSL／快取命中與 token 占比決定；API 與 ChatGPT 的 token 占比、agent 型流量比重都沒有一手數字', 'OpenAI 2025 年 API 與 ChatGPT 的 token 占比；各類請求平均輸入／輸出長度與快取命中率', 'OpenRouter《State of AI》與週報（代理值）；OpenAI DevDay；Anthropic Economic Index；NBER《How people use ChatGPT》', 'OpenRouter：prompt 1.5K→6K、completion 150→400、agent 快取約 88%（2026）；ChatGPT token 長度：已搜尋，未找到', 'Alloc_In C26（另有結構題：κ 與單價須同一流量形狀）', 'C'),
 (7, 'Hopper η_d 倍數', '1.2（0.8–1.6）', 19, 'Hopper 吞吐被判為保守下界（獨立對照約實測 0.26–0.27 倍）；MLPerf closed 組沒有 DeepSeek-R1 的 H100／H200 提交', '同模型、同軟體的 H100／H200 對 GB200 decode 實測（中段互動性）', 'MLPerf 下一輪；vLLM／SGLang 部落格；InferenceX（不可單獨使用）', 'MLPerf closed 組確認無 H100／H200 DSR1 提交；405B 跨精度推算 1.3–1.8', 'Calib C67', 'C'),
 (6, '推論支出的記帳口徑', '8.4（7.5–8.8）$B', 12, '營收分成記在營業成本或營收減項不明；免費推論是否在營業成本外不明', 'OpenAI 營收分成的會計處理；營業成本組成；免費用戶推論的科目', 'OpenAI 若 IPO 的招股文件；FT／The Information 對查核財報的後續報導；Microsoft 10-K 附註', '查核財報分項（付 Microsoft 172 億）已取得；營收分成記帳位置：已搜尋，未找到', 'SRC_Demand C8（SRC_DEM_004）', 'A線上'),
 (3, 'Astra 啟用參數', '180B（60–250B）', 6, '頂層模型參數從未揭露', '第三方對 GPT-5／GPT-6 級頂層模型啟用參數的估計，或延遲／價格反推', 'Epoch AI；學術估計；推理速度反推', 'Epoch 1.0e27 FLOP（叢集總算力上限）；啟用參數：只有第三方估計', 'Arch E7（Perf Astra 欄）', 'C（專家意見）'),
 (8, '每則提示 token τ 與免費占比', 'τ 4,000（2,000–11,000）；免費 0.6（0.4–0.8）', 18, 'τ 只影響 r（免費 ÷ 付費 token 比）；token 口徑的免費占比與支出口徑 46% 混用', 'ChatGPT 每則對話的平均 token（含推理）；免費用戶 token 占比', 'NBER《How people use ChatGPT》（訊息數，無 token）；OpenAI 官方；WildChat 類比', 'WildChat 每回合約 296 入／441 出（類比）；ChatGPT token 長度：已搜尋，未找到', 'Alloc_In C15、C16', 'C'),
 (5, 'Sol 2025 單價的加權', '2.184（1.672–2.338）$/M', 14, 'ChatGPT 預設與 API 主力的 token 比例是 Assumed（2,365：1,460）', '2025 年 ChatGPT 付費 token 對 API token 的比例', '同第 1、3 項', '同第 1 項', 'Cap_In C279', 'C'),
]
items7.sort(key=lambda x: x[0])
for i, it in enumerate(items7):
    rr = 5 + i
    pr_, nm, cur, no, why, ev, srcs, done, cell, who = it
    vals = [pr_, nm, cur, swing(no), elas(no), why, ev, srcs, done, cell, who]
    for j, v in enumerate(vals, 1):
        c = U7.cell(rr, j, v); c.font = BLACK; c.alignment = WRAP
    U7.cell(rr, 4).number_format = '0%'; U7.cell(rr, 5).number_format = '0.00'
    if pr_ <= 3:
        for j in range(1, 12): U7.cell(rr, j).fill = YEL
U8 = sheet('8_不確定_實地調研', [6, 22, 18, 10, 10, 40, 46, 44, 30, 14])
U8['A1'] = '最不確定、需要「實地調研」的假設（業者訪談、供應鏈查核；公開資料找不到）'; U8['A1'].font = TITLE
U8['A2'] = 'A線下＝Andy 線下調研。資料放 Drive 02-算力收支/Tokenomics/inbox/，chat 端直接讀。'; U8['A2'].font = NOTE
hdr(U8, 4, ['優先', '假設', '現值（區間）', '擺動', '承重度', '為什麼不確定', '要問的問題（可直接用於訪談）', '訪談或查核對象', '找到後要改的格', '分工'])
items8 = [
 (1, '實際利用率（純）', '0.41（0.30–0.65）', 4, '沒有任何實驗室公開「token 吞吐 ÷ 容量」實測；上端只有 DeepSeek 2025-02 單一模型代理值', '大型推論叢集的平均 GPU 利用率（以 token 吞吐 ÷ 理論容量計，不是 GPU busy%）？日夜與尖離峰差多少？多模型部署時下降多少？', '雲端或 neocloud 營運人員（CoreWeave、Nebius、Azure、Oracle）；推論平台（Fireworks、Together、Baseten）；台灣雲端業者', 'Alloc_In C24', 'A線下'),
 (4, '2025 服務世代組合（Hopper／GB200）', 'Hopper 0.6／GB200 0.4（暫設 0.5–0.7）', 11, '無公開數字；GB200 在 2025 年各季的上線量與 OpenAI 分到的比例都不明', 'Microsoft、Oracle、CoreWeave 為 OpenAI 部署的 GB200 機櫃在 2025 年各季的出貨與上線數？同期 Hopper 機隊規模？', '台灣 ODM／機櫃供應鏈（廣達、緯穎、鴻海）；機房業者；SemiAnalysis 付費報告（不可單獨使用）', 'Alloc_In C9、C10', 'A線下＋A線上'),
 (3, '生產折減（SLO 預留、故障、重啟）', '0.85（0.70–1.00）', 9, '情境值，非估計值；只有訓練端的公開可靠度論文可類比', '推論叢集為了守住 SLO 預留多少容量？節點故障、重啟、升級造成的產能損失約多少？', '雲端 SRE／推論平台營運；GPU 雲業者', 'Serving C28', 'A線下'),
 (5, '機架價格（GB200 NVL72、H100）', 'H100 1.1（0.9–1.3）$M；GB200 3.1（2.8–3.4）$M（擺動欄為 H100）', 24, '產業報導與 ODM 報價差異大；直接決定每 GW 持有成本（m 對持有成本彈性 +1）', '2025 年 GB200 NVL72 整櫃成交價（含 NVLink、液冷）？大客戶折扣？', 'ODM、通路與系統整合商；伺服器採購人員', 'Spec_Rack C12、D12', 'A線下'),
 (2, 'Batch／Flex 占比與企業折扣', '有效折扣 0.2（0.1–0.4）', 7, 'Batch 半價是公開牌價，但占比與企業議價找不到', 'API 用量中 Batch／Flex 的占比？大型企業合約相對牌價的平均折扣？', 'API 大客戶（企業、新創）；OpenAI 業務；雲端市集', 'Cap_In C12', 'A線下'),
 (6, 'Hopper 實際 decode 效率', 'η_d 倍數 1.2（0.8–1.6）', 19, '模型 Hopper 吞吐約為獨立實測的 0.26–0.27 倍（保守下界）', '同一模型在 H100／H200 與 GB200 上，生產環境的 decode tok/s/GPU 比？', '推論平台工程師；雲端效能團隊', 'Calib C67', 'A線下'),
]
items8.sort(key=lambda x: x[0])
for i, it in enumerate(items8):
    rr = 5 + i
    pr_, nm, cur, no, why, q, who_, cell, who = it
    vals = [pr_, nm, cur, swing(no), elas(no), why, q, who_, cell, who]
    for j, v in enumerate(vals, 1):
        c = U8.cell(rr, j, v); c.font = BLACK; c.alignment = WRAP
    U8.cell(rr, 4).number_format = '0%'; U8.cell(rr, 5).number_format = '0.00'
    if pr_ <= 3:
        for j in range(1, 11): U8.cell(rr, j).fill = YEL

# ---------------------------------------------------------------- 9_前置格清單
Q = sheet('9_前置格清單', [14, 9, 6, 50, 16, 80, 10, 14])
Q['A1'] = 'L1_MFleet 的全部前置格（從 Cap_In!C119 遞迴展開；Tokenomics v17.0）'; Q['A1'].font = TITLE
Q['A2'] = '共 2,993 格；常數格（輸入）426 格。「深度」＝距 m 的步數。公式前的「＝」為文字顯示，非可執行公式。供查找：在 Tokenomics 開同一格即可看原式。'; Q['A2'].font = NOTE
hdr(Q, 4, ['工作表', '格', '深度', '列標籤', '值', '公式（原文）', '類型', 'Gov_Map 類別'])
tr = _j.load(open('trace.json', encoding='utf-8'))['nodes']
def lab(sh, a):
    rown = re.sub(r'[A-Z]+', '', a.split(':')[0])
    for c in ('A', 'B'):
        t = wv[sh][f'{c}{rown}'].value
        if isinstance(t, str) and t.strip(): return t.replace('\n', ' ')[:120]
    return ''
rr = 5
for sh, a, d in sorted(tr, key=lambda x: (x[2], x[0], x[1])):
    if ':' in a:
        vals = [sh, a, d, '（範圍）', '', '', '範圍', '']
    else:
        v = wv[sh][a].value; fo = wfm[sh][a].value
        isf = isinstance(fo, str) and fo.startswith('=')
        vals = [sh, a, d, lab(sh, a), v if not isinstance(v, str) else v[:60], ('＝' + fo[1:300]) if isf else '', '公式' if isf else '常數（輸入）', GM.get((sh, a), {}).get('cat', '')]
    for j, v in enumerate(vals, 1):
        Q.cell(rr, j, v).font = BLACK if vals[6] != '常數（輸入）' else BLUE
    rr += 1
Q.auto_filter.ref = f'A4:H{rr-1}'
Q.freeze_panes = 'A5'

# ---------------------------------------------------------------- 1_總覽
O = sheet('1_總覽', [4, 46, 18, 14, 70])
wb.move_sheet('1_總覽', offset=-(len(wb.sheetnames) - 1))
O['B1'] = 'm（機隊變現率）推導總覽'; O['B1'].font = Font(name=F, bold=True, size=15)
O['B2'] = 'Tokenomics v17.0（master 5ef0f7e，2026-10-20；m 自 v15.2 起未變，v16.0／v17.0 只改 L 與回本判讀）。本頁數字全部連結到 3_m重算，改 2_輸入 會一起變。'; O['B2'].font = NOTE
O['B4'] = '一句話'; O['B4'].font = BOLD
O['B5'] = 'm ＝ OpenAI 2025 營收能「買到」的 token（按 2025 牌價扣折扣）÷ OpenAI 機隊實際產出的付費 token。m < 1 表示機隊產出的付費 token 比營收按牌價折算的多——每個 token 實收低於牌價（訂閱、免費額度、折扣），或模型高估了機隊產出。'
O['B5'].alignment = WRAP; O.merge_cells('B5:E5'); O.row_dimensions[5].height = 48
def orow(r, lab_, f, unit, expl, bold=False, fmt='#,##0.0000'):
    O.cell(r, 2, lab_).font = BOLD if bold else BLACK
    c = O.cell(r, 3, f); c.font = GREEN; c.number_format = fmt
    O.cell(r, 4, unit).font = BLACK
    O.cell(r, 5, expl).font = NOTE; O.cell(r, 5).alignment = WRAP
hdr(O, 7, ['', '層級與項目', '值', '單位', '怎麼算（細節頁）'])
M3 = "'3_m重算'"
rows = [
 ('第 0 層：m', f"={M3}!D{MR['m']}", 'x', '＝ 營收 ÷（機隊付費 token × 混合有效單價）（3_m重算 步驟 m）', True, '0.0000'),
 ('　營收', '=IN_Rev', '$B', 'SRC_DEM_007，查核財報', False, '#,##0.00'),
 ('　營收折合的 token', f"={M3}!D{MR['S19']}", 'M tok/年', '營收 ÷ 混合有效單價（步驟 S19）', False, '#,##0'),
 ('　機隊付費 token', f"={M3}!D{MR['S16']}", 'M tok/年', '有效服務 GW × 利用率修正 ÷（1/付費產能 ＋ r/免費產能）（步驟 S16）', False, '#,##0'),
 ('第 1 層：單價', f"={M3}!D{MR['S18']}", '$/M tok', '付費層級組合 × 2025 層級單價 ×（1 − 折扣）（步驟 S17–S18）', True, '0.0000'),
 ('第 2 層：有效服務 GW', f"={M3}!D{MR['S14']}", 'GW', '推論支出 ÷ 每 GW 持有成本 ÷ 計價倍數 × κ（步驟 S12–S14；持有成本見 4_持有成本）', True, '0.0000'),
 ('　推論支出', '=IN_Spend', '$B', 'SRC_DEM_004（主口徑 84 億；126 億為對照）', False, '#,##0.00'),
 ('　機隊每 GW 年持有成本', f"={M3}!D{MR['S12']}", '$B/GW·年', '資本回收年金＋營運費用（4_持有成本）', False, '0.000'),
 ('　利用率修正', f"={M3}!D{MR['S15']}", 'x', '實際利用率 × 生產折減 ÷ IF_Util（步驟 S15）', False, '0.0000'),
 ('第 3 層：免費 ÷ 付費 token 比 r', f"={M3}!D{MR['S11']}", 'x', 'ChatGPT 免費 token ÷（API ＋ ChatGPT 付費）（步驟 S7–S11）', True, '0.0000'),
 ('第 4 層：機隊每 GW 年產能（付費）', f"={M3}!D{MR['S5']}", 'M tok/年', '世代加權的調和平均（步驟 S1–S6）', True, '#,##0'),
 ('　機隊每 GW 年產能（免費）', f"={M3}!D{MR['S6']}", 'M tok/年', '同上', False, '#,##0'),
 ('第 5 層：每 GW 年產出（roofline）', f"='5_每GW產出'!H{PR['tokgw']}", 'M tok/年', '例：GB200 Sol。每請求 GPU 秒 ← prefill（算力）＋ decode（SLO 下的批次 B*）（5_每GW產出）', True, '#,##0'),
]
r = 8
for lab_, f, unit, expl, b, fmt in rows:
    orow(r, lab_, f, unit, expl, b, fmt)
    if b:
        for i in range(2, 6): O.cell(r, i).fill = SEC
    r += 1
r += 1
O.cell(r, 2, '閉式解（IF_Util 會約掉）').font = BOLD; r += 1
O.cell(r, 2, 'm ＝ 營收 × 持有成本 × 計價倍數 ×（1/C付 ＋ r/C免）÷（推論支出 × κ × 實際利用率 × 生產折減 × 單價）').font = BLACK
O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5); r += 1
O.cell(r, 2, 'C付、C免＝100% 利用率下的每 GW 年產能（＝S5、S6 ÷ IF_Util）。IF_Util 同時出現在利用率修正的分母與產能的分子，所以 m 與它無關。').font = NOTE
O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5); r += 1
cf = (f"=IN_Rev*{M3}!D{MR['S12']}*IN_SpendBasis*(1/({M3}!D{MR['S5']}/IN_Util)+{M3}!D{MR['S11']}/({M3}!D{MR['S6']}/IN_Util))"
      f"/(IN_Spend*IN_Kappa*IN_UtilAct*IN_ProdDerate*{M3}!D{MR['S18']})*1000000000")
O.cell(r, 2, '閉式解計算的 m'); c = O.cell(r, 3, cf); c.number_format = '0.0000'
O.cell(r, 5, '應等於第 0 層的 m（單位：營收 $B × 持有成本 $B/GW ÷ 支出 $B → 只剩 $/token 與 token 的比）').font = NOTE; CFR = r; r += 1
O.cell(r, 2, '差異'); c = O.cell(r, 3, f'=C{CFR}/C8-1'); c.number_format = '0.0000%'; r += 2
O.cell(r, 2, '彈性（m 對各輸入，閉式解直接可讀）').font = BOLD; r += 1
for a_, b_ in [('營收、持有成本、計價倍數', '+1'), ('推論支出、κ、實際利用率、生產折減、單價', '−1'), ('每 GW 產能（付費與免費一起放大時）', '−1'), ('IF_Util', '0（約掉）'), ('免費 ÷ 付費 token 比 r', '＋（r 越大，留給付費的產能越少，m 越高）')]:
    O.cell(r, 2, a_); O.cell(r, 3, b_); r += 1
r += 1
O.cell(r, 2, '驗證').font = BOLD; r += 1
checks = [('3_m重算 的 m ÷ Tokenomics 原值 − 1', f"={M3}!H{MR['m']}"),
          ('5_每GW產出 六個案例的最大絕對差異', f"=MAX(ABS('5_每GW產出'!D{P_DIFF}),ABS('5_每GW產出'!E{P_DIFF}),ABS('5_每GW產出'!F{P_DIFF}),ABS('5_每GW產出'!G{P_DIFF}),ABS('5_每GW產出'!H{P_DIFF}),ABS('5_每GW產出'!I{P_DIFF}))"),
          ('4_持有成本 兩個世代的最大絕對差異', f"=MAX(ABS('4_持有成本'!D{H_DIFF}),ABS('4_持有成本'!E{H_DIFF}))")]
for a_, f in checks:
    O.cell(r, 2, a_); c = O.cell(r, 3, f); c.number_format = '0.0000%'; r += 1
r += 1
O.cell(r, 2, '最不確定的八項（依 6_敏感度 擺動排序；細節見 7、8 頁）').font = BOLD; r += 1
hdr(O, r, ['', '輸入', '擺動', '承重度', '去哪裡解決']); r += 1
where_map = {1: '7_不確定_搜尋 第 4 項', 2: '已用 MLPerf 定為 Derived；Hopper 見 7 頁第 7 項', 3: '7_不確定_搜尋 第 1 項', 4: '8_不確定_實地調研 第 1 項',
             5: '7_不確定_搜尋 第 2 項', 6: '7_不確定_搜尋 第 3 項', 7: '8_不確定_實地調研 第 2 項', 8: '7_不確定_搜尋 第 1 項（流量形狀）', 9: '8_不確定_實地調研 第 3 項',
             10: '7_不確定_搜尋 第 1 項（流量形狀）', 11: '8_不確定_實地調研 第 4 項', 12: '7_不確定_搜尋 第 6 項', 14: '7_不確定_搜尋 第 5 項', 18: '7_不確定_搜尋 第 8 項',
             19: '7 頁第 7 項／8 頁第 6 項', 24: '8_不確定_實地調研 第 5 項', 25: '8_不確定_實地調研 第 5 項'}
sw = sorted([(abs(res[f'{no}_hi'][0]-res[f'{no}_lo'][0])/base, no) for no, *_ in sj['cases'] if no not in (20, 27)], reverse=True)
top = [(no, where_map.get(no, '')) for _, no in sw[:8]]
for no, where in top:
    O.cell(r, 2, f"='6_敏感度'!B{SROW[no]}"); c = O.cell(r, 3, f"='6_敏感度'!I{SROW[no]}"); c.number_format = '0%'
    c = O.cell(r, 4, f"='6_敏感度'!H{SROW[no]}"); c.number_format = '0.00'
    O.cell(r, 5, where).font = NOTE; r += 1

# ---------------------------------------------------------------- 0_說明
Z = sheet('0_說明', [4, 110])
wb.move_sheet('0_說明', offset=-(len(wb.sheetnames) - 1))
lines = [
 ('m 推導檢核（Tokenomics v17.0）', TITLE),
 ('建立：2026-10-18，chat 端（Claude）。用途：讓 Andy 自行檢核 m 從總覽到最細的數學推導。', NOTE),
 ('', None),
 ('分頁', BOLD),
 ('1_總覽：m 的一句話定義、五層結構、閉式解（IF_Util 約掉）、彈性、驗證、最不確定的五項。', None),
 ('2_輸入：全部輸入（藍字，可改）。黃底＝不確定度「高」。每列附標記（Gov_Map）、區間、原活頁簿位置與說明。', None),
 ('3_m重算：m 的逐步計算（S1–S19 → m），每步附白話說明、原活頁簿格與原值、差異。', None),
 ('4_持有成本：每 GW 年經濟持有成本（Hopper、GB200），資本回收年金＋營運費用。', None),
 ('5_每GW產出：roofline——由規格、架構、SLO 與校準係數推出每 GW 年 token 產出（6 個案例）。', None),
 ('6_敏感度：27 個輸入的單變數敏感度（v15.3，LibreOffice 整本重算 55 次）。', None),
 ('7_不確定_搜尋：可以搜尋（公開或付費）解決的最不確定假設，附要找的證據與來源。', None),
 ('8_不確定_實地調研：需要訪談或供應鏈查核的假設，附可直接使用的訪談問題。', None),
 ('9_前置格清單：m 在 Tokenomics 中的全部 2,993 個前置格（含 426 個常數輸入），供查找原式。', None),
 ('', None),
 ('顏色', BOLD),
 ('藍字＝輸入或外部結果（可改）；黑字＝本簿公式；綠字＝連結到其他分頁；黃底＝最不確定、優先調研；淺綠底＝m。', None),
 ('', None),
 ('範圍與限制', BOLD),
 ('1. 本簿重寫了 m 的計算鏈到「規格、架構、校準係數、成本輸入」這一層；更底層的校準擬合（Calib 頁以 GB300 實測聯立解出 η_d 與每層延遲）以擬合結果作為輸入，未重寫。', None),
 ('2. 2025 服務世代只有 Hopper 與 GB200（GB300、VR200 占比為 0），所以只列這兩個世代；Tokenomics 的「層級不可達」旗標在基準下全部為可達，本簿未重寫旗標邏輯。', None),
 ('3. m 在 Tokenomics 以 MAX(m, 物理下限) 輸出；基準下 m 0.460 高於下限 0.339，下限不綁定。', None),
 ('4. 敏感度為單變數測試，未測交互作用；兩種組合（世代、層級）沒有正式區間，為 chat 端暫設。', None),
 ('5. 回本判讀不在本簿範圍：回本由 L（壽命期價格係數）與恆等式所需 L 決定，不經 m（v17.0 主口徑：世代起點＋折現 L 0.759 對 不含 κ 所需 L 0.756，判讀「未定」）。', None),
]
for i, (t, fnt) in enumerate(lines, 1):
    c = Z.cell(i, 2, t); c.alignment = WRAP
    c.font = fnt or BLACK

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.font is None or c.font.name != F:
                c.font = Font(name=F, size=c.font.size if c.font else 10, bold=c.font.bold if c.font else False, color=c.font.color if c.font else None)
order=['0_說明','1_總覽','2_輸入','3_m重算','4_持有成本','5_每GW產出','6_敏感度','7_不確定_搜尋','8_不確定_實地調研','9_前置格清單']
wb._sheets=[wb[n] for n in order]
wb.active=1
out = 'm推導檢核_v17.0.xlsx'
wb.save(out)
print('saved', out, wb.sheetnames)

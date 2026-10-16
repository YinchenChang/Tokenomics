"""D1 死格逐列建議處置。用法：python3 06_recommend_dead.py <wb.pkl> <rows.pkl> <out.pkl>
規則式（由上而下第一個命中者生效）；規則寫在 RULES，明細頁「規則」欄標出命中的規則編號，供 4-1 覆核。"""
import pickle, re, sys, collections
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']
R = pickle.load(open(sys.argv[2], 'rb'))
rows = R['rows']

HEADER = {'世代', '層級', '成本情境', '項目', '點位標籤（世代｜用途｜速度）', '層級 × 任務', '參數', '實驗室'}
INDEX = re.compile(r'^(欄索引|世代索引|層級索引)$')
VERIFY = re.compile(r'檢查|核對|判讀|÷ MLPerf|模型 ÷ 實測|上限檢查|一致性')
CMP = re.compile(r'對照|外部|揭露|參照|Requesty|Plus|Pro 方案|方案上限')
DISPLAY_TAG = '保留並標「顯示用」'

def v(s, a):
    x = cells.get((s, a)); return None if x is None else x['v']

out = []
for x in rows:
    s, r, lab = x['sheet'], x['row'], str(x['label'] or '')
    whole = not x['row_has_core']
    has_in = any(k != '公式' for k in x['kinds'])
    uu = set(x['users_union'])
    cols = x['cols']; colrange = cols[0] + ('–' + cols[-1] if len(cols) > 1 else '')
    cat = '死格（整列無人用）' if whole else '死格（同列其他欄有核心格）'
    rule = ''; act = ''; why = ''; nat = '工程類'
    def set_(rl, a, w, n='工程類'):
        global rule, act, why, nat
        rule, act, why, nat = rl, a, w, n
    if s == 'Capability':
        set_('R01', '刪除（整頁）', '工作單 6b 第 4-1 步已決定刪 Capability 頁；整頁無任何下游引用。')
    elif s == 'NonNV':
        set_('R02', '保留，標「未接線」', '工作單 6b 第 4-1 步已決定 NonNV 頁保留並標「未接線」（非 NVIDIA 對照，目前不進任何輸出）。')
    elif uu & {'敏感度', '鏡像'}:
        set_('R03', '保留（被 Sens_／_Prod 複本讀取，非真死格）', '依 6b(a) 敏感度頁與 _Prod 鏡像保留；此列對「根節點」是死格，但被複本頁引用。4-1 的永久測試應把複本頁納入根節點，這列才不會被誤判為死格。')
    elif s == 'Perf_Batch' and set(cols) <= {'R', 'S'}:
        set_('R04', '待判斷：保留並標「情境對照（未接線）」或刪除 R–S 欄', 'R、S 欄是「VR200 以 FP8 rollout」情境（J12 替代，頁首說明），整欄 64 列公式＋4 個索引輸入沒有任何下游讀取：Training 與 Interface 都沒有接。若 J12 情境仍要保留，須先接線；否則整欄刪除。', '判斷類')
    elif s == 'Tech_Registry' and x['row'] in range(5, 17) and cols[0] == 'I':
        set_('R05', '待判斷：K 欄（主流判定）與 T 欄（一致性檢查）未接線', 'K＝IF(J≥CST_MainMin,…) 的判定結果與 T 欄一致性檢查沒有任何下游（有效倍數 P 欄只讀 M「已在基準」）。建議把 T 欄接進 Checks（讓檢查能失敗，6b 原則 4），或標「顯示用」；I、J 輸入隨之決定。', '判斷類')
    elif s == 'L1' and cols == ['O']:
        ext = v('L1', f'M{r}')
        if ext in ('—', None, ''):
            set_('R06', '刪除 O 欄公式（該列無外部值）', '該列外部值 M／N 為「—」，O 欄「推算 ÷ 外部」恆為「—」，沒有資訊；P 欄已寫「無外部對照」。')
        else:
            set_('R07', DISPLAY_TAG + '（對照欄：推算 ÷ 外部）', '有外部值，O 欄是人讀的對照比值（口徑＝D 欄基準值 ÷ 外部值），不進任何輸出；標明為顯示用。')
    elif s == 'L1':
        set_('R07', DISPLAY_TAG + '（對照欄：外部值與推算 ÷ 外部）', 'L1 的 M／N／O 欄是外部對照（SRC 連結）與比值，只供閱讀；標明口徑。')
    elif s == 'Interface' and VERIFY.search(lab):
        set_('R08', DISPLAY_TAG + '（驗證列），並建議接入 Checks', '加總核對列沒有任何下游讀取；6b 原則 4「驗證材料不刪，讓檢查能失敗」，建議接進 Checks。', '工程類')
    elif s == 'Cap_In' and r in (23, 24):
        set_('R09b', '建議合併：Sens_Rev 的商業壽命 6／24 改讀本列低／高（或刪本列）', 'Cap_In 商業壽命 低／高（GM451／GM452）沒有任何公式引用，而 Sens_Rev B20／B21 另帶 6、24 兩個值，同一物理量兩處各自輸入（稽核 0 的 C1.6）。', '判斷類')
    elif s == 'Cap_In' and not whole and cols == ['D', 'E'] and all(k != '公式' for k in x['kinds']):
        set_('R09', DISPLAY_TAG + '（區間端點；僅供 Gov_Map 範圍檢查）或刪除', '參數的低／高欄只被 Gov_Map 讀取，模型公式與敏感度頁都不用。若敏感度頁要用，應改讀這些格（避免 Sens_Rev 另帶一份）；否則標顯示用。', '判斷類')
    elif s == 'Cap_In' and has_in and 'B' in cols[:1]:
        set_('R10', DISPLAY_TAG + '（候選模型輸入表；Price_Frontier 單價表的來源）', '模型候選清單的廠商、國別、開放權重等文字輸入；單價表 Price_Frontier 部分欄接核心、其餘欄只供閱讀。', '判斷類')
    elif whole and has_in and s != 'Cap_In':
        set_('R11', '待判斷：刪除或保留並標「備用輸入」', '藍字輸入沒有任何公式引用；刪除會連帶要刪 Gov_Map／SRC 登錄（6b 原則 4 不刪治理材料），故屬判斷類。預設：若 Gov_Map 無 SRC／決策 ID 則刪除，否則保留並標備用。', '判斷類')
    elif whole and (lab in HEADER or lab.startswith('世代') and len(lab) < 6):
        set_('R12', DISPLAY_TAG + '（欄頭／表頭標籤）', '欄頭用來讓人讀表，本身不計算；刪除會讓表看不懂。標「顯示用」即可。')
    elif whole and INDEX.match(lab):
        set_('R13', '刪除（索引常數）', '無任何公式引用的索引常數列；留著只會讓人誤以為有用到。')
    elif whole and VERIFY.search(lab):
        set_('R14', DISPLAY_TAG + '（驗證列），並建議接入 Checks', '驗證材料不列入瘦身（6b 原則 4）；但沒有下游代表檢查失敗時沒人會知道，建議接進 Checks。', '判斷類')
    elif whole and CMP.search(lab):
        set_('R15', DISPLAY_TAG + '（對照列；標明口徑）', '對照列不進輸出，是人讀的外部對照（6b 原則 2：對照欄要標明口徑）。', '工程類')
    elif s == 'Cap_In' and whole:
        set_('R16', '待判斷：H／I／J 節 m 追蹤閱讀列——與 L1_ 的 m 名稱重複者建議合併（見「重複定義」頁），其餘保留並標顯示用', 'm 值已由 L1_MImplied／L1_MFleet／L1_MAPI 等名稱輸出；Cap_In 同一物理量的逐步閱讀列沒有下游。是否合併屬判斷（涉及推導鏈要不要留在 Excel 可見處）。', '判斷類')
    elif s == 'Alloc' and not whole and r < 135:
        set_('R17', DISPLAY_TAG + '（G 節敏感度表；閉式重寫 A–D 推導鏈）', 'G 節每列以閉式公式重寫 A–D 節推導鏈，輸出只供閱讀；屬敏感度表，依 6b(a) 的精神保留，但需有「基準列＝A–D 節結果」的永久測試（見重複定義 D07）。', '工程類')
    elif s == 'Alloc' and whole:
        set_('R18', '刪除', '整列沒有任何下游引用的中間或診斷量（v8.0–v10.0 新增的世代缺口、未服務占比等診斷列）；若這些列是 Checks 的輸入來源則不會被判為死格，故確定為無人使用。', '工程類')
    elif s == 'Calib' and not whole:
        set_('R19', DISPLAY_TAG + '（校準點逐步重現）', '校準頁 D–I 欄是擬合點的逐步重現與「模型 ÷ 實測」；Calibration 屬驗證材料（6b 原則 4）。建議把「模型 ÷ 實測」接進 Checks。', '工程類')
    elif s == 'Calib':
        set_('R20', DISPLAY_TAG + '（校準擬合步驟）', '擬合點的中間量，由 Calib 輸入反推；不進模型輸出但屬校準的可稽核推導，標顯示用。', '工程類')
    elif not whole:
        set_('R21', DISPLAY_TAG + '（同表其他世代／層級欄）', '同一列的核心格只有一部分欄（被下游取用的世代×層級）；其餘欄是同表的其他世代或層級，整表是人讀的對照表。刪欄會破壞表形，故標顯示用。', '工程類')
    elif s in ('Perf', 'Perf_Batch') and re.search(r'速覽', lab):
        set_('R22c', '刪除（與 Unit_Cost 重複的速覽列）', '「速覽 $/M」與 Unit_Cost 同一口徑的單價重複計算（見重複定義 D01）；單價的唯一定義應在 Unit_Cost。', '工程類')
    elif '無任何格引用' in uu:
        set_('R22a', '待判斷：結果列（無下游）——建議刪除，除非要升級為 IF_ 輸出', '整列公式沒有任何格引用，是該頁推導鏈的末端結果（成本、營收、毛利率、成功率等）。刪除不改變任何輸出，但這類列是人最可能抽查的結論；請 Andy 決定：升級成 IF_／L1_ 具名輸出（使其成為唯一來源）、保留標「顯示用」、或刪除。', '判斷類')
    else:
        set_('R22b', '待判斷：中間量，與其下游結果列同進退', '此列只被其他死格引用（中間量）；是否刪除取決於下游結果列（R22a）的決定。', '判斷類')
    out.append(dict(sheet=s, row=r, label=lab, cell=f'{colrange}{r}' if len(cols) == 1 else f'{cols[0]}{r}:{cols[-1]}{r}', n=x['n'], nform=x['nform'], nin=x['nin'],
                    value=x['value'], cat=cat, act=act, why=why, nat=nat, rule=rule, status=x['status'], users='、'.join(x['users_union']), formula=x['formula']))
print(len(out))
c = collections.Counter((z['act'].split('（')[0].split('：')[0], z['nat']) for z in out); print(c)
cell_c = collections.Counter()
for z in out: cell_c[z['rule']] += z['nform']
print('公式格 by rule', sorted(cell_c.items()))
pickle.dump(out, open(sys.argv[3], 'wb'))

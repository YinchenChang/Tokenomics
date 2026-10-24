# build_reading_m.py 的後半（由前半 exec 載入；共用同一組變數）
# 1A_需求公式樹、1_總覽、5_敏感度、6_不確定與證據、0_說明、9_核對對照，並存檔。


def px_expr(ov=None):
    ov = ov or {}
    d = ov.get('d', 'IN_Disc')
    k = ov.get('kappa', 'IN_Kappa')
    chi = ov.get('chi', 'IN_Chi')
    mixA = ov.get('mixA')
    mix = {'L': 'IN_MixP_L', 'S': 'IN_MixP_S', 'A': 'IN_MixP_A'}
    if mixA:
        mix = {'A': mixA, 'L': f'(1-{mixA})*IN_MixP_L/(IN_MixP_L+IN_MixP_S)', 'S': f'(1-{mixA})*IN_MixP_S/(IN_MixP_L+IN_MixP_S)'}
    terms = []
    for t in 'LSA':
        isl = ov.get('isl_' + t, f'IN_ISL_{t}')
        osl = ov.get('osl_' + t, f'IN_OSL_{t}')
        terms.append(f'({mix[t]})*IN_CapMult_{t}*({isl}*((1-{chi})*IN_PIn_{t}+{chi}*IN_PCache_{t})+{osl}*IN_POut_{t})/({isl}+{osl})')
    return f'{k}*(1-{d})*(' + '+'.join(terms) + ')'


def m26(ov=None):
    ov = ov or {}
    rev = ov.get('rev', 'IN_RevQ2*4')
    ad = ov.get('ad', 'IN_Ad_Q2')
    tau = ov.get('tau', 'IN_Tau')
    free = ov.get('free', 'IN_FreeShare')
    return (f'=({rev}-{ad})*1000000000/((IN_APItpm26*1000000000*525600/1000000+IN_Prompts_Q2*1000000000*{tau}*365/1000000*(1-{free}))'
            f'*({px_expr(ov)}))')


def m25_d(d):
    f = f"{q(S3)}!F{R3['num']}*1000000000/({q(S3)}!F{R3['tok']}*(IN_Kappa*(1-{d})*(IN_MixP_L*IN_Px_L+IN_MixP_S*IN_Px_S+IN_MixP_A*IN_Px_A)))"
    return '=' + f


def c3(key, col):
    return f"{q(S3)}!{col}{R3[key]}"


def c4(key, col):
    return f"{q(S4)}!{col}{R4[key]}"


# ───────────────────────── 1A_需求公式樹 ─────────────────────────
ws = WS['1A_需求公式樹']
widths(ws, {'A': 6, 'B': 40, 'C': 14, 'D': 14, 'E': 14, 'F': 66, 'G': 24, 'H': 14, 'I': 14, 'J': 10, 'K': 10})
put(ws, 'A1', 'm 的需求公式樹：從「誰付錢、誰用 token」推到 m（付費服務 token 的有效牌價變現率）', F_T1, wrap=False)
put(ws, 'A2', '讀法：由上往下，每一層把上一層的一個量拆開。全部是公式，連到 2_輸入（藍字）、3_m重算、4_分路線；改輸入，本頁一起變。'
    '左邊兩欄值＝2025 與 2026 Q2（主口徑）；Q1、FY2026 在 3_m重算。H／I 欄＝Tokenomics v21.3 原值（貼上），J／K 欄＝差異。', F_T2, wrap=False)
put(ws, 'A3', 'token 單位一律為「兆 token/年」（10¹² token；3_m重算 的 M tok ÷ 10⁶）。單價一律為「$/M token」（每百萬 token 美元）。'
    'm 的定義（Andy 2026-10-21）：m＝實收單價 ÷ 有效牌價；有效牌價＝表列牌價 ×（1 − d），d 預設 20%、可調；m 只有收入面，免費與成本都不進 m。', F_T2, wrap=False)
hdr(ws, 5, ['層', '項目', '值 2025', '值 2026 Q2', '單位', '怎麼算（白話＋公式）', '標記', '原值 2025', '原值 2026 Q2', '差異 2025', '差異 2026 Q2'])
ws.freeze_panes = 'C6'
T = 1e6
tree = []


def TG(text):
    tree.append(('g', text))


def TS(layer, name, f25, fq2, unit, desc, mark, o25=None, oq2=None, fmt='#,##0.000', hl=False, key=None):
    tree.append(('s', layer, name, f25, fq2, unit, desc, mark, o25, oq2, fmt, hl, key))


TG('L0　m 是什麼：每個付費 token 實收多少，除以有效牌價')
TS('', 'm 分子營收（營收 − 廣告）', f"={c3('num', 'F')}", f"={c3('num', 'H')}", '$B', '付費服務實際收到的錢（毛額、不含廣告）。', 'Interested-party', 'Cap_In!C69', 'Cap_In!E187')
TS('', '需求面付費 token', f"={c3('tok', 'F')}/1000000", f"={c3('tok', 'H')}/1000000", '兆 token/年', 'API token ＋ ChatGPT 付費 token（L3 加總）。免費 token 不進 m。', 'Derived',
   'Cap_In!C83/1000000', '(Cap_In!E196+Cap_In!E198)/1000000')
TS('', '實收單價（每百萬付費 token 實收）', f"={c3('act', 'F')}", f"={c3('act', 'H')}", '$/M token', '＝m 分子營收 × 1000 ÷ 付費 token（兆）。', 'Derived', fmt='0.0000')
TS('', '表列混合牌價（未折扣）', f"={c3('pl', 'F')}", f"={c3('pl', 'H')}", '$/M token', '＝有效牌價 ÷（1 − d）。層級組合加權的 OpenAI 官方牌價。', 'Derived', None, 'L1_PxList_2026', fmt='0.0000')
TS('', 'd：預設折扣（可調）', '=IN_Disc', '=IN_Disc', '%', 'Batch／Flex 半價＋企業議價的加權；Assumed，區間 0.1–0.4。改 2_輸入 的 IN_Disc 即可。', 'Assumed', 'Cap_In!C12', 'Cap_In!C12', fmt='0.00')
TS('', '有效牌價', f"={c3('px', 'F')}", f"={c3('px', 'H')}", '$/M token', '＝表列牌價 ×（1 − d）；L4 展開。2025 與 2026 的牌價基準不同（2025 用 2025 年度層級單價，2026 用 2026-09 的 GPT-6 牌價）。', 'Derived',
   'CAP_Price25Mix', 'L1_PxEff_2026', fmt='0.0000')
TS('', 'm ＝ 實收單價 ÷ 有效牌價', f"={c3('m', 'F')}", f"={c3('m', 'H')}", '倍', 'm＞1：付費 token 平均實收高於有效牌價（主要來自定額訂閱）；m＜1：實收低於有效牌價。', 'Derived',
   'Cap_In!C209', 'L1_M_2026Q2', fmt='0.0000', hl=True)
TG('L1　分子與分母：m ＝ 分子營收 ÷（付費 token × 有效單價）')
TS('', '營收（年化）', f"={c3('rev', 'F')}", f"={c3('rev', 'H')}", '$B', '2025 全年；2026 Q2＝季營收 × 4。', 'Interested-party', 'Cap_In!C69', 'Cap_In!E185')
TS('', '廣告營收（年化）', f"={c3('ad', 'F')}", f"={c3('ad', 'H')}", '$B', '不進分子（Andy：m 單純看收費業務）。2025 無廣告。', 'Assumed', 'Cap_In!C186', 'Cap_In!E186')
TS('', '分子：m 分子營收', f"={c3('num', 'F')}", f"={c3('num', 'H')}", '$B', '＝營收 − 廣告。', 'Derived', 'Cap_In!C69', 'Cap_In!E187')
TS('', '分母：付費 token 按有效牌價折算的營收', f"={c3('tok', 'F')}*{c3('px', 'F')}/1000000000", f"={c3('tok', 'H')}*{c3('px', 'H')}/1000000000", '$B',
   '＝付費 token × 有效單價：如果每個付費 token 都照有效牌價收費，營收會是這麼多。', 'Derived')
TS('', '檢查：分子 ÷ 分母', f"=C{{n}}/C{{d}}", f"=D{{n}}/D{{d}}", '倍', '應等於 L0 的 m（恆等式）。', 'Derived', fmt='0.0000', key='l1chk')
TG('L2　營收從哪裡來：三條收費路線，各自的 m（分子拆開；細節見 4_分路線）')
TS('', 'API 營收', f"={c4('rapi', 'F')}", f"={c4('rapi', 'H')}", '$B', '＝m 分子營收 × API 份額（餘額）。', 'Derived', 'Cap_In!C137', 'Cap_In!E193')
TS('', '消費訂閱營收', f"={c4('rsub', 'F')}", f"={c4('rsub', 'H')}", '$B', '＝m 分子營收 × 消費訂閱份額（2025 約 70%；2026 Q2 0.55）。', 'Derived／Assumed', 'Cap_In!C135', 'Cap_In!E191')
TS('', '商用席次營收', f"={c4('rseat', 'F')}", f"={c4('rseat', 'H')}", '$B', '＝m 分子營收 × 商用席次份額（2025 0.10；2026 Q2 0.25，Assumed）。', 'Assumed', 'Cap_In!C136', 'Cap_In!E192')
TS('', 'm_API', f"={c4('mapi', 'F')}", f"={c4('mapi', 'H')}", '倍', '按量計費路線：實收低於有效牌價。', 'Derived', 'L1_MAPI', 'L1_M_API', fmt='0.0000')
TS('', 'm_消費訂閱', f"={c4('msub', 'F')}", f"={c4('msub', 'H')}", '倍', '定額月費 ÷ 實際用量：遠大於 1，是整體 m 偏高的主因。', 'Derived', 'L1_MSub', 'L1_M_Sub', fmt='0.0000')
TS('', 'm_商用席次', f"={c4('mseat', 'F')}", f"={c4('mseat', 'H')}", '倍', '按席次定額收費，同上。', 'Derived', 'L1_MSeat', 'L1_M_Seat', fmt='0.0000')
TG('L3　付費 token 由誰用：API 與 ChatGPT 付費（二分）；ChatGPT 付費再分消費訂閱／商用席次')
TS('', 'API 每分鐘 token', '=IN_APItpm', '=IN_APItpm26', '十億 token/分鐘', '2025：OpenAI 2025-10-06 公告 60 億；2026：2026-03-31 融資公告「超過」150 億（Q2 當期值未找到）。', 'Interested-party', 'SRC_DEM_010', 'SRC_DEM_011', fmt='0.0')
TS('', 'API 全年平均 ÷ 時點值', '=IN_APIratio', None, '倍', '只 2025 欄：把 10 月時點值換成全年平均（Assumed 0.6–0.9）；2026 Q1／Q2 不打折，FY2026 另乘 1.3。', 'Assumed', 'Alloc_In!C14', None, fmt='0.00')
TS('', '→ API token', f"={c3('api', 'F')}/1000000", f"={c3('api', 'H')}/1000000", '兆 token/年', '＝每分鐘 token × 525,600 分鐘 ×（2025：年均比例；2026：1）。', 'Derived', 'AL_DAPI/1000000', 'Cap_In!E196/1000000')
TS('', 'ChatGPT 每日訊息數', '=IN_Prompts', '=IN_Prompts_Q2', '十億則/日', '2025：OpenAI 自述 25 億；2026 Q2：3.6（週活比例放大，Assumed）。', 'Interested-party／Assumed', 'SRC_DEM_012', 'Cap_In!E197', fmt='0.00')
TS('', '每則訊息 token 數 τ', '=IN_Tau', '=IN_Tau', 'token/則', '含輸入、輸出、思考；無公開數字（Assumed 2,000–11,000）。', 'Assumed', 'Alloc_In!C15', 'Alloc_In!C15', fmt='#,##0')
TS('', '免費用戶占 ChatGPT token 比', '=IN_FreeShare', '=IN_FreeShare', '%', 'token 口徑（Assumed 0.4–0.8）。只用來把 ChatGPT 總量扣成付費部分；免費服務本身不進 m。', 'Assumed', 'Alloc_In!C16', 'Alloc_In!C16', fmt='0.00')
TS('', 'ChatGPT token 總量', f"={c3('chat', 'F')}/1000000", f"={c3('chat', 'H')}/1000000", '兆 token/年', '＝每日訊息 × τ × 365。', 'Derived', 'AL_DChat/1000000', '(Cap_In!E198+Cap_In!E199)/1000000')
TS('', '　其中免費 token（扣除，不進 m）', f"={c3('free', 'F')}/1000000", f"={c3('free', 'H')}/1000000", '兆 token/年', '＝總量 × 免費占比。', 'Derived', 'AL_DChatFree/1000000', 'Cap_In!E199/1000000')
TS('', '→ ChatGPT 付費 token', f"={c3('paid', 'F')}/1000000", f"={c3('paid', 'H')}/1000000", '兆 token/年', '＝總量 × （1 − 免費占比）。', 'Derived', 'AL_DChatPaid/1000000', 'Cap_In!E198/1000000')
TS('', '　消費訂閱 token', f"={c4('tsub', 'F')}/1000000", f"={c4('tsub', 'H')}/1000000", '兆 token/年', '＝ChatGPT 付費 × 消費份額（2025 0.75；2026 0.65，Assumed）。', 'Assumed（份額）', 'Cap_In!C141/1000000', 'Cap_In!E201/1000000')
TS('', '　商用席次 token', f"={c4('tseat', 'F')}/1000000", f"={c4('tseat', 'H')}/1000000", '兆 token/年', '＝ChatGPT 付費 ×（1 − 消費份額）。', 'Assumed（份額）', 'Cap_In!C142/1000000', 'Cap_In!E202/1000000')
TS('', '需求面付費 token 合計', f"={c3('tok', 'F')}/1000000", f"={c3('tok', 'H')}/1000000", '兆 token/年', '＝API ＋ ChatGPT 付費。', 'Derived', 'Cap_In!C83/1000000', '(Cap_In!E196+Cap_In!E198)/1000000')
TG('L4　有效單價：Σ 層級占比 × 層級有效單價 × κ；層級有效單價 ＝ 表列牌價 × 請求形狀 ×（1 − d）× 能力倍數')
for t, nm in (('L', 'Luna'), ('S', 'Sol'), ('A', 'Astra')):
    col = {'L': 'F', 'S': 'G', 'A': 'H'}[t]
    TS('', f'{nm} 付費 token 占比', f"={c3('t_mix', col)}", f"={c3('t_mix', col)}", '%', 'Assumed（Cap_In 第 31 列）；2025、2026 用同一組。', 'Assumed',
       f"Cap_In!{ {'L': 'C', 'S': 'D', 'A': 'E'}[t] }31", f"Cap_In!{ {'L': 'C', 'S': 'D', 'A': 'E'}[t] }31", fmt='0.00')
for t, nm in (('L', 'Luna'), ('S', 'Sol'), ('A', 'Astra')):
    col = {'L': 'F', 'S': 'G', 'A': 'H'}[t]
    TS('', f'{nm} 層級有效單價', f"={c3('t_px25', col)}", f"={c3('t_ref', col)}", '$/M token',
       '2025＝2025 年度表列單價 ×（1 − d）。2026＝[ISL ×（（1 − χ）× 新鮮 ＋ χ × 快取）＋ OSL × 輸出] ÷（ISL ＋ OSL）×（1 − d）× 能力倍數（現值 1）。展開見 3_m重算 下方。',
       'Derived', None, f"IF_PriceRef_{nm}", fmt='0.0000')
TS('', 'κ：請求形狀修正', '=IN_Kappa', '=IN_Kappa', '倍', '實際流量每 GPU 秒總 token ÷ 參考請求（Derived 0.65–1.2）；乘入混合有效單價。', 'Derived', 'Alloc_In!C26', 'Alloc_In!C26', fmt='0.00')
TS('', '→ 混合有效單價 ＝ Σ 占比 × 層級單價 × κ', f"={c3('px', 'F')}", f"={c3('px', 'H')}", '$/M token', '＝L0 的有效牌價。', 'Derived', 'CAP_Price25Mix', 'L1_PxEff_2026', fmt='0.0000', hl=True)
TS('', '試算用 d（2_輸入 IN_DTest，可改）', '=IN_DTest', '=IN_DTest', '%', '只用在下兩列；不影響其他頁。', '本簿試算', fmt='0.00')
TS('', 'd 改成試算值後的 m', m25_d('IN_DTest'), m26({'d': 'IN_DTest'}), '倍',
   '用同一組輸入、只把 d 換成試算值，整套有效單價重算（營收與 token 是觀測值，不隨 d 動）。', 'Derived', fmt='0.0000', key='dtest')
TS('', 'm 變動倍數（試算 ÷ 基準）', 'C{dt}/C{m}', 'D{dt}/D{m}', '倍', '＝(1 − 基準 d) ÷ (1 − 試算 d)。', 'Derived', fmt='0.0000', key='dtest_ratio')
TS('', '不變的是 m ×（1 − d）', '=C{m}*(1-IN_Disc)', '=D{m}*(1-IN_Disc)', '倍', '＝實收單價 ÷ 表列牌價。d 只是改「用哪個價當基準」，營收不變，所以不變的是實收對表列牌價的比，不是 m。', 'Derived', fmt='0.0000')
TG('L5　若要 m＝1，需要什麼為真（實收＝有效牌價；每次只動一個假設，其他不動）')
TS('', '(a) 每則 token τ 要多大', f"=({c3('num', 'F')}*1000000000/{c3('px', 'F')}-{c3('api', 'F')})/({c3('pr', 'F')}*1000000000*365/1000000*(1-IN_FreeShare))",
   f"=({c3('num', 'H')}*1000000000/{c3('px', 'H')}-{c3('api', 'H')})/({c3('pr', 'H')}*1000000000*365/1000000*(1-IN_FreeShare))", 'token/則',
   '令 ChatGPT 付費 token ＝（營收 ÷ 有效單價）− API token，反解 τ。現值 4,000，Tokenomics 區間 2,000–11,000。', 'Derived', fmt='#,##0', key='ra')
TS('', '(b) 付費 token 要多少', f"={c3('num', 'F')}*1000000000/{c3('px', 'F')}/1000000", f"={c3('num', 'H')}*1000000000/{c3('px', 'H')}/1000000", '兆 token/年',
   '＝m 分子營收 ÷ 有效單價。', 'Derived', fmt='#,##0')
TS('', '　　相對現有付費 token 的倍數', '=C{rb}/C{tokrow}', '=D{rb}/D{tokrow}', '倍', '＝m（因為 m ＝ 營收折算 token ÷ 實際付費 token）。', 'Derived', fmt='0.000')
TS('', '(c) d 要是多少', '=1-(1-IN_Disc)*C{m}', '=1-(1-IN_Disc)*D{m}', '%', '令有效牌價＝實收單價，反解 d＝1 −（1 − d）× m。負值代表連不打折的表列牌價都低於實收，d 不可能解釋 m＞1。', 'Derived', fmt='0.0%')
tree.append(('t', 'Q2 需每則 token ≈10,752（在 Tokenomics 區間 2,000–11,000 內、接近上緣）；實收 $2.634／M 高於未打折的表列牌價 $2.429／M，所以 d＝0 也得不到 m＝1（v21.3 值；v21.2 為 ≈10,521、$2.451）。'))
TG('下鑽')
for t in ['牌價與有效單價（L0、L4）→ 3_m重算 S10–S11 與層級單價展開表', '付費 token（L3）→ 3_m重算 S4–S9', '分路線 m（L2）→ 4_分路線',
          '各輸入的區間與擺動 → 5_敏感度；要找的證據 → 6_不確定與證據', '本頁每個原值與 Tokenomics 的對應 → 9_核對對照']:
    tree.append(('t', t))

# 先指派列號，再寫入（部分公式需要列號）
rr = 6
rows_idx = {}
for it in tree:
    it_row = rr
    rr += 1
    rows_idx[id(it)] = it_row
names_row = {}
for it in tree:
    if it[0] == 's':
        names_row[it[2]] = rows_idx[id(it)]
m_row = names_row['m ＝ 實收單價 ÷ 有效牌價']
tok_row = names_row['需求面付費 token']
chk_n = names_row['分子：m 分子營收']
chk_d = names_row['分母：付費 token 按有效牌價折算的營收']
dt_row = names_row['d 改成試算值後的 m']
rb_row = names_row['(b) 付費 token 要多少']
fmtmap = dict(m=m_row, dt=dt_row, rb=rb_row, tokrow=tok_row, n=chk_n, d=chk_d)
for it in tree:
    r = rows_idx[id(it)]
    if it[0] == 'g':
        grp(ws, r, it[1], 11)
    elif it[0] == 't':
        put(ws, f'B{r}', it[1])
    else:
        _, _lay, name, f25, fq2, unit, desc, mark, o25, oq2, fmt, hl, key = it
        fill = FILL_M if hl else None
        fnt = F_BOLD if hl else F_BASE
        put(ws, f'B{r}', name, fnt, fill)
        for col, f in (('C', f25), ('D', fq2)):
            if f is not None:
                f = f.format(**fmtmap) if '{' in f else f
                if not f.startswith('='):
                    f = '=' + f
                lnk = re.fullmatch(r"=('?[^'!]+'?!)\$?[A-Z]+\$?\d+", f) is not None
                put(ws, f'{col}{r}', f, F_GREEN if (lnk and not hl) else fnt, fill, fmt, wrap=False)
        put(ws, f'E{r}', unit, fnt, fill)
        put(ws, f'F{r}', desc, F_GRAY, fill)
        put(ws, f'G{r}', mark, F_GRAY, fill)
        put(ws, f'A{r}', '', fnt, fill)
        for vcol, ocol, dcol, o in (('C', 'H', 'J', o25), ('D', 'I', 'K', oq2)):
            if o is not None:
                paste(ws, f'{ocol}{r}', o, '原值', fmt, fill)
                put(ws, f'{dcol}{r}', diff(f'{vcol}{r}', f'{ocol}{r}'), F_BASE, fill, '0.000%', wrap=False)
                MAPROWS.append((ws.title, f'{dcol}{r}', '', '差異'))
            elif fill:
                for cc in (ocol, dcol):
                    ws[f'{cc}{r}'].fill = fill
# d 可調驗證的一句話
r_sent = max(rows_idx.values()) + 2
put(ws, f'B{r_sent}', 'd 可調驗證（一句話）', F_BOLD)
put(ws, f'C{r_sent}',
    f'="把 d 從 "&TEXT(IN_Disc,"0.00")&" 改成 "&TEXT(IN_DTest,"0.00")&" 重算：2026 Q2 的 m 由 "&TEXT(D{m_row},"0.000")&" 變成 "&TEXT(D{dt_row},"0.000")'
    f'&"（×"&TEXT(D{dt_row}/D{m_row},"0.000")&"）；2025 由 "&TEXT(C{m_row},"0.000")&" 變成 "&TEXT(C{dt_row},"0.000")'
    f'&"。m 會變：營收與 token 是觀測值，d 只改有效牌價的基準，所以 m 隨 1/(1 − d) 變；不變的是 m ×（1 − d）＝實收單價 ÷ 表列牌價。"',
    F_BASE, wrap=False)

# ───────────────────────── 5_敏感度 ─────────────────────────
ws = WS['5_敏感度']
widths(ws, {'A': 5, 'B': 30, 'C': 34, 'D': 22, 'E': 11, 'F': 11, 'G': 12, 'H': 12, 'I': 11, 'J': 11, 'K': 10, 'L': 9, 'M': 6, 'N': 44})
put(ws, 'A1', 'L1_M（2026 Q2，主口徑）的單變數敏感度', F_T1, wrap=False)
put(ws, 'A2', '每個有 Tokenomics 區間的輸入，各取低端與高端，其餘不動，用本簿公式重算 m（m 是乘除式，直接寫出）。承重度＝弧彈性 ln(m高/m低) ÷ ln(輸入高/輸入低)；'
    '擺動＝|m高 − m低| ÷ m 基準。只測單一變數，未測交互作用。Tokenomics 沒有區間的輸入寫「TK 無區間」，不自訂區間。', F_T2, wrap=False)
hdr(ws, 4, ['#', '輸入', '怎麼擺動', 'Tokenomics 位置', '低值', '高值', 'm（低值）', 'm（高值）', '相對變化（低）', '相對變化（高）', '承重度', '擺動', '排名', '說明'])
put(ws, 'B5', 'm 基準（2026 Q2）', F_BOLD, FILL_M)
put(ws, 'G5', f"={c3('m', 'H')}", F_GREEN, FILL_M, '0.0000', wrap=False)
put(ws, 'B6', '檢查：公式在基準值重算 − 基準', F_GRAY)
put(ws, 'G6', m26() + '-G5', F_BASE, None, '0.0E+00', wrap=False)
SENS = [
    ('每則 token τ', 'IN_Tau', {'tau': '{v}'}, 'Alloc_In C15', 'τ 大→付費 token 多→m 小。'),
    ('ChatGPT 免費占比', 'IN_FreeShare', {'free': '{v}'}, 'Alloc_In C16', '免費占比大→付費 token 少→m 大。'),
    ('有效折扣 d', 'IN_Disc', {'d': '{v}'}, 'Cap_In C12', 'd 大→有效牌價低→m 大（m×(1 − d) 不變）。'),
    ('請求形狀 κ', 'IN_Kappa', {'kappa': '{v}'}, 'Alloc_In C26', 'κ 乘進有效單價，m 與 κ 成反比。'),
    ('快取命中 χ', 'IN_Chi', {'chi': '{v}'}, 'Cap_In C13', 'χ 大→輸入多按便宜的快取價→有效單價低→m 大。'),
    ('2026 Q2 廣告營收（年化）', 'IN_Ad_Q2', {'ad': '{v}'}, 'Cap_In E186', '廣告從分子扣除；影響小。'),
    ('Astra 層級占比', 'IN_MixP_A', {'mixA': '{v}'}, 'Cap_In E31（區間來自 Gov_Map GM457 文字）', 'Luna 與 Sol 依 0.40：0.45 補足；Astra 貴，占比大→有效單價高→m 小。'),
    ('Luna 參考輸入長度 ISL', 'IN_ISL_L', {'isl_L': '{v}'}, 'Serving C23', ''),
    ('Sol 參考輸入長度 ISL', 'IN_ISL_S', {'isl_S': '{v}'}, 'Serving D23', 'ISL 長→新鮮／快取輸入價權重大→Sol 有效價低。'),
    ('Astra 參考輸入長度 ISL', 'IN_ISL_A', {'isl_A': '{v}'}, 'Serving E23', ''),
    ('Luna 參考輸出長度 OSL', 'IN_OSL_L', {'osl_L': '{v}'}, 'Serving C24', ''),
    ('Sol 參考輸出長度 OSL', 'IN_OSL_S', {'osl_S': '{v}'}, 'Serving D24', 'OSL 長→貴的輸出價權重大→有效價高→m 小。'),
    ('Astra 參考輸出長度 OSL', 'IN_OSL_A', {'osl_A': '{v}'}, 'Serving E24', ''),
]
r = 7
first = r
for i, (lab, nm, ov, loc, note) in enumerate(SENS, 1):
    if nm not in INLO:
        continue
    put(ws, f'A{r}', i)
    put(ws, f'B{r}', lab)
    put(ws, f'C{r}', f'{nm} 取 {nm}_Lo／{nm}_Hi', F_GRAY)
    put(ws, f'D{r}', loc, F_GRAY)
    put(ws, f'E{r}', f'={nm}_Lo', F_GREEN, None, '0.####', wrap=False)
    put(ws, f'F{r}', f'={nm}_Hi', F_GREEN, None, '0.####', wrap=False)
    put(ws, f'G{r}', m26({k: v.format(v=f'{nm}_Lo') for k, v in ov.items()}), F_BASE, None, '0.0000', wrap=False)
    put(ws, f'H{r}', m26({k: v.format(v=f'{nm}_Hi') for k, v in ov.items()}), F_BASE, None, '0.0000', wrap=False)
    put(ws, f'I{r}', f'=G{r}/$G$5-1', F_BASE, None, '0%', wrap=False)
    put(ws, f'J{r}', f'=H{r}/$G$5-1', F_BASE, None, '0%', wrap=False)
    put(ws, f'K{r}', f'=IF(OR(E{r}<=0,F{r}<=0,G{r}<=0,H{r}<=0),"—",LN(H{r}/G{r})/LN(F{r}/E{r}))', F_BASE, None, '0.00', wrap=False)
    put(ws, f'L{r}', f'=ABS(H{r}-G{r})/$G$5', F_BASE, None, '0%', wrap=False)
    put(ws, f'N{r}', note, F_GRAY)
    r += 1
last = r - 1
for rr_ in range(first, last + 1):
    put(ws, f'M{rr_}', f'=RANK(L{rr_},$L${first}:$L${last})', F_BASE, None, None, wrap=False)
SENS_ROWS = {lab: first + k for k, lab in enumerate([s[0] for s in SENS if s[1] in INLO])}
r += 1
put(ws, f'B{r}', '對照：τ 與免費占比同向取端點（Tokenomics 的 L1_M_2026Q2 區間）', F_BOLD)
put(ws, f'G{r}', f"={c3('e_m', 'H')}", F_GREEN, None, '0.0000', wrap=False)
put(ws, f'H{r}', f"={c3('e_m', 'I')}", F_GREEN, None, '0.0000', wrap=False)
put(ws, f'N{r}', '兩個輸入同時取端點的包絡（最寬情形），不是機率區間；連結 3_m重算 E9。', F_GRAY)
r += 2
put(ws, f'A{r}', 'Tokenomics 無區間的 Assumed／單值輸入（不自訂區間，不計算擺動）', F_BOLD, wrap=False)
r += 1
for lab, nm, note in [('2026 Q2 季營收', 'IN_RevQ2', 'Interested-party 單值（WSJ 轉述）；m 近似與營收成正比（扣廣告後）。'),
                      ('2026 API 每分鐘 token', 'IN_APItpm26', '2026-03 時點值，Q2 當期值未找到（E399）。'),
                      ('2026 Q2 ChatGPT 每日訊息數', 'IN_Prompts_Q2', 'Assumed，週活比例放大；TK 無區間。'),
                      ('2026 營收份額、消費訂閱 token 份額', 'IN_SubShare_Q2', '只影響分路線 m，不影響整體 m。'),
                      ('能力單價倍數 ε', 'IN_CapMult_S', 'ε 的區間 0–0.5 存在，但倍數＝(H_CAP × 算力倍數)^ε，現值兩者皆為 1，ε 怎麼動倍數都是 1，m 不受影響。')]:
    put(ws, f'B{r}', lab)
    put(ws, f'E{r}', f'={nm}', F_GREEN, None, '0.####', wrap=False)
    put(ws, f'F{r}', 'TK 無區間' if nm != 'IN_CapMult_S' else '不影響', F_BASE, wrap=False)
    put(ws, f'N{r}', note, F_GRAY)
    r += 1
ws.freeze_panes = 'C5'
SENS_LAST = last

# ───────────────────────── 6_不確定與證據 ─────────────────────────
ws = WS['6_不確定與證據']
widths(ws, {'A': 5, 'B': 24, 'C': 24, 'D': 8, 'E': 9, 'F': 40, 'G': 44, 'H': 38, 'I': 30, 'J': 22, 'K': 10})
put(ws, 'A1', '最不確定的輸入：為什麼不確定、要找什麼證據、找到後 m 往哪個方向動', F_T1, wrap=False)
put(ws, 'A2', '排序依據：5_敏感度 的擺動 × 證據取得難度。分工：C＝chat 端可在公開網路找；A線上＝Andy 在付費牆或需登入的來源找；A線下＝Andy 線下調研。'
    '另列 Tokenomics 交接檔「證據 (4) m」三項（2026 API token 當期值、訂閱用量分布、企業折扣）；交接檔本文本次未能讀取，三項名稱引自工作單。', F_T2, wrap=False)
hdr(ws, 4, ['優先', '輸入', '現值（區間）', '擺動', '承重度', '為什麼不確定', '要找的證據（找到就能定案的口徑）／可直接用的問題', '建議管道', '對 m 的影響方向', '找到後要改的格', '分工'])


def srow(lab):
    return SENS_ROWS.get(lab)


def lk(lab, col):
    rr_ = srow(lab)
    return f"='5_敏感度'!{col}{rr_}" if rr_ else '—'


UNC = [
    ('一、可以「搜尋」解決', None),
    ('每則訊息 token τ', '4,000（2,000–11,000）', '每則 token τ', 'Alloc_In C15 → 3_m重算 S6',
     '無公開數字；含輸入、上下文、推理與輸出，agent 與長文件使用會大幅拉高。', 'ChatGPT 每則對話（含推理）的平均 token；付費與免費用戶分開。',
     'OpenRouter《State of AI》（每請求 token 代理值）；NBER《How people use ChatGPT》（訊息數、無 token）；OpenAI DevDay。本串已搜尋：ChatGPT token 長度未找到。',
     'τ↑→付費 token↑→m↓。', 'C'),
    ('ChatGPT 免費占比（token 口徑）', '0.6（0.4–0.8）', 'ChatGPT 免費占比', 'Alloc_In C16 → S7',
     'token 口徑與支出口徑混用過；Tokenomics 另有 2026 投資人資料的免費算力占比預估（L1_FreeShare_2026 0.34，算力口徑，Interested-party），口徑不同、未進 m。',
     '免費與付費用戶各自的 token 占比（不是用戶數、不是算力支出）。', 'OpenAI 投資人資料（The Information）；招股文件若 IPO；第三方流量統計。', '免費占比↑→付費 token↓→m↑。', 'A線上＋C'),
    ('2026 每日訊息數', '3.2／3.6／3.8 十億則/日（TK 無區間）', None, 'Cap_In 第 197 列 → S5',
     '2026 值是由週活比例放大推得（Assumed），沒有 OpenAI 對 2026 訊息數的直接揭露。', 'ChatGPT 2026 每日提示數或每週活躍用戶的官方更新。', 'OpenAI 公告、Axios／TechCrunch 轉述。', '訊息數↑→付費 token↑→m↓（近似反比，因 API token 是固定部分）。', 'C'),
    ('2026 API token 當期值', '15 B tok/分鐘（2026-03 時點；Q2 沿用）', None, 'Cap_In 第 196 列 → S4',
     'Q2、Q3 當期值已搜尋，未找到（DB_Evidence E399）；時點值「超過」15B，年化後不打折，可能高估或低估全年。Tokenomics 交接檔證據 (4) 項。', 'OpenAI 2026 Q2／Q3 API 每分鐘 token 的最新揭露。',
     'OpenAI 官方部落格、DevDay 2026、第三方統計頁。', 'API token↑→付費 token↑→m↓。', 'C'),
    ('層級組合（Astra 占比）', 'Luna 0.40／Sol 0.45／Astra 0.15（Astra 0.10–0.30）', 'Astra 層級占比', 'Cap_In 第 31 列 → T12',
     '各模型 token 占比未公開；Assumed。Astra 單價約為 Sol 的 5 倍，占比對有效單價影響大。', '付費 token 在 Luna／Sol／Astra（及舊模型）的占比，按季。', 'The Information、FT；OpenRouter 模型排行（代理值）；OpenAI 官方數字。',
     'Astra↑→有效單價↑→m↓。', 'A線上＋C'),
    ('快取命中率 χ 與請求形狀（ISL／OSL）', 'χ 0.55（0.3–0.75）；Sol ISL 16,384／OSL 2,048', '快取命中 χ', 'Cap_In C13；Serving 第 23–24 列 → T5–T7',
     '決定新鮮輸入、快取輸入、輸出三種價在混合價裡的權重；2026 agent 流量快取約 88%，高於現值。', '各類流量（API、ChatGPT、agent）的平均輸入／輸出長度與快取命中率。',
     'OpenRouter（prompt 1.5K→6K、completion 150→400、agent 快取約 88%）；OpenAI DevDay。', 'χ↑→有效單價↓→m↑；輸出越長→有效單價↑→m↓。', 'C'),
    ('請求形狀 κ', '1.0（0.65–1.2）', '請求形狀 κ', 'Alloc_In C26（AL_Kappa）→ 3_m重算 S10',
     '實際流量每 GPU 秒總 token ÷ 參考請求；由各類流量的輸入／輸出長度、快取命中與 token 占比決定，API 與 ChatGPT 的 token 占比、agent 型流量比重都沒有一手數字。擺動全表最大。',
     '各類請求（API、ChatGPT、agent）的平均輸入／輸出長度、快取命中率與各自的 token 占比。', 'OpenRouter《State of AI》（代理值）；OpenAI DevDay；Anthropic Economic Index；NBER《How people use ChatGPT》。',
     'κ↑→有效單價↑→m↓（m 與 κ 成反比，彈性 −1）。', 'C'),
    ('廣告營收', '2026 Q2 0.5 $B（0.3–0.8）', '2026 Q2 廣告營收（年化）', 'Cap_In E186 → S2',
     '依據 SRC_DEM_072（2026-08 廣告年化達 $1B）；Q2 年化值為推定。', '廣告營收的季度揭露。', 'OpenAI／媒體報導。', '廣告↑→分子↓→m↓（影響小）。', 'C'),
    ('二、需要「實地調研」或付費資料', None),
    ('有效折扣 d（Batch／Flex 占比與企業折扣）', '0.20（0.1–0.4）', '有效折扣 d', 'Cap_In C12 → IN_Disc',
     'Batch 半價是公開牌價，但占比與企業議價找不到（DB_Evidence E359：三輪搜尋未找到）。Tokenomics 交接檔證據 (4) 項「企業折扣」。',
     '問：API 用量中 Batch／Flex 的占比？大型企業承諾用量合約相對牌價的平均折扣？優先處理溢價與快取計價如何影響實收？', 'API 大客戶（企業、新創）；OpenAI 業務；雲端市集（Azure）。',
     'd↑→有效牌價↓→m↑；但 m×(1 − d) 不變（見 1A 的 d 可調驗證）。', 'A線下'),
    ('訂閱用量分布（重度與輕度用戶）', '消費訂閱占 ChatGPT 付費 token 0.75（2025）／0.65（2026）（0.5–0.9）', None, 'Cap_In C132、D200 → 4_分路線 R10',
     'm_消費訂閱＞1 的根本原因是定額月費遠高於多數用戶的 token 用量等值；但用量分布（重度用戶人數與比例）沒有揭露。Tokenomics 交接檔證據 (4) 項。',
     '問：Plus／Pro 用戶 token 用量的分布（中位數、p90、p99）？重度用戶占訂閱人數與占 token 的比例？方案上限（速率限制）實際觸頂比例？', '前員工與業者訪談；第三方用量調查；OpenAI 研究報告（用戶行為）。',
     '不影響整體 m（只影響訂閱與席次的分路線 m）；整體 m 的訂閱貢獻要靠 τ 與免費占比。', 'A線下'),
    ('商用席次定價與實際用量', '席次營收份額 2026 Q2 0.25（Assumed）', None, 'Cap_In E189 → 4_分路線',
     '「企業」口徑 OpenAI 未定義（席次＋API？）；席次實際用量只有 p95／中位數（SRC_DEM_045）。', '企業席次單價、席次數、企業年約折扣、承諾用量。', '企業客戶採購人員；OpenAI 業務；雲端市集。', '只影響分路線 m_商用席次與 m_API 的分攤。', 'A線下'),
    ('其他收入面變數（尚未進模型）', 'README 列出，Tokenomics 未量化', None, '—',
     '訂閱方案用量上限與速率限制、年繳與月繳折扣、促銷與試用額度、區域定價、經雲端市集或合作夥伴的營收分成（毛額與淨額口徑）、退款與壞帳。', '各項對實收營收（m 分子）的調整幅度。', '財報附註；招股文件若 IPO；業者訪談。', '多為分子（實收）調整：實收↓→m↓。', 'A線下'),
]
r = 5
n = 0
for it in UNC:
    if it[1] is None:
        for c in range(1, 12):
            ws[f'{CL(c)}{r}'].fill = FILL_GRP
        put(ws, f'A{r}', it[0], F_BOLD, FILL_GRP, wrap=False)
        r += 1
        continue
    n += 1
    name, cur, lab, loc, why, ev, chan, direction, who = it
    put(ws, f'A{r}', n, F_BASE, FILL_Y)
    put(ws, f'B{r}', name, F_BASE, FILL_Y)
    put(ws, f'C{r}', cur, F_BASE, FILL_Y)
    if lab and srow(lab):
        put(ws, f'D{r}', f"='5_敏感度'!L{srow(lab)}", F_GREEN, FILL_Y, '0%', wrap=False)
        put(ws, f'E{r}', f"='5_敏感度'!K{srow(lab)}", F_GREEN, FILL_Y, '0.00', wrap=False)
    else:
        put(ws, f'D{r}', 'TK 無區間', F_GRAY, FILL_Y)
        put(ws, f'E{r}', '—', F_GRAY, FILL_Y)
    put(ws, f'F{r}', why, F_BASE, FILL_Y)
    put(ws, f'G{r}', ev, F_BASE, FILL_Y)
    put(ws, f'H{r}', chan, F_BASE, FILL_Y)
    put(ws, f'I{r}', direction, F_BASE, FILL_Y)
    put(ws, f'J{r}', loc, F_BASE, FILL_Y)
    put(ws, f'K{r}', who, F_BASE, FILL_Y)
    r += 1
ws.freeze_panes = 'C5'

# ───────────────────────── 1_總覽 ─────────────────────────
ws = WS['1_總覽']
widths(ws, {'A': 3, 'B': 40, 'C': 14, 'D': 14, 'E': 16, 'F': 14, 'G': 12, 'H': 70})
put(ws, 'B1', 'm（付費服務 token 的有效牌價變現率）總覽', Font(name=FN, size=15, bold=True), wrap=False)
put(ws, 'B2', 'Tokenomics v21.3（20261024_Tokenomics_v21.3.xlsx，master aa17328）。本頁數字全部連結到 3、4 頁，改 2_輸入 會一起變。', F_T2, wrap=False)
put(ws, 'B4', '一句話', F_BOLD, wrap=False)
put(ws, 'B5', 'm ＝ 實收單價 ÷ 有效牌價。實收單價＝付費業務（扣廣告）的營收 ÷ 付費 token（API ＋ ChatGPT 付費）；有效牌價＝表列牌價 ×（1 − d），d 預設 20%、可調。'
    '只有收入面：免費服務與訓練研發算力不產生營收，不進 m；也不經成本鏈反推。m＞1 表示每個付費 token 平均實收高於有效牌價，主要來自定額訂閱。', F_BASE)
ws.merge_cells('B5:H5')
ws.row_dimensions[5].height = 58
hdr(ws, 7, ['項目', '2025', '2026 Q1', '2026 Q2（主口徑）', 'FY2026', '單位', '怎麼算（細節頁）'], c0=2)
OV = [
    ('m', 'm', '倍', '＝實收單價 ÷ 有效牌價（3_m重算 S13）', '0.000', True),
    ('num', 'm 分子營收（營收 − 廣告）', '$B', '營收年化 − 廣告（S1–S3）', '0.00', False),
    ('tok', '需求面付費 token', 'M tok/年', 'API ＋ ChatGPT 付費（S4–S9）', '#,##0', False),
    ('act', '實收單價', '$/M tok', '分子營收 ÷ 付費 token（S12）', '0.000', False),
    ('px', '有效牌價（混合有效單價）', '$/M tok', 'Σ 層級占比 × 層級有效單價 × κ（S10）', '0.000', False),
    ('pl', '表列混合牌價（未折扣）', '$/M tok', '有效牌價 ÷（1 − d）（S11）', '0.000', False),
]
r = 8
OVR = {}
for key, lab, unit, how, fmt, hl in OV:
    fill = FILL_M if hl else None
    put(ws, f'B{r}', lab, F_BOLD if hl else F_BASE, fill)
    for i, col in enumerate('FGHI'):
        put(ws, f'{CL(3 + i)}{r}', f"={c3(key, col)}", F_GREEN if not hl else F_BOLD, fill, fmt, wrap=False)
    put(ws, f'G{r}', unit, F_BASE, fill)
    put(ws, f'H{r}', how, F_GRAY, fill)
    OVR[key] = r
    r += 1
r += 1
put(ws, f'B{r}', '區間（Tokenomics 的 L1_M 區間；低端＝token 取高、高端＝token 取低）', F_BOLD, wrap=False)
r += 1
hdr(ws, r, ['', '低', '基準', '高', '', '', '說明'], c0=2)
r += 1
put(ws, f'B{r}', '2025（L1_M_2025）')
put(ws, f'C{r}', f"={c3('e_m', 'F')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'D{r}', f"={c3('m', 'F')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'E{r}', f"={c3('e_m', 'G')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'H{r}', '每則 token、免費占比、API 全年比例同向取端點（最寬情形，不是機率區間）。', F_GRAY)
r += 1
put(ws, f'B{r}', '2026 Q2（L1_M，主口徑）')
put(ws, f'C{r}', f"={c3('e_m', 'H')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'D{r}', f"={c3('m', 'H')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'E{r}', f"={c3('e_m', 'I')}", F_GREEN, None, '0.000', wrap=False)
put(ws, f'H{r}', '每則 token、免費占比同向取端點；營收、API token、單價、每日訊息數不變。', F_GRAY)
r += 1
put(ws, f'B{r}', '2026 Q1、FY2026')
put(ws, f'C{r}', '無區間', F_GRAY, wrap=False)
put(ws, f'H{r}', 'Tokenomics 的 L1_M_2026Q1、L1_M_FY2026 區間欄為「無區間」：2026 欄的輸入是 Assumed 單值，區間待補（單值原因＝無 SRC 區間）。', F_GRAY)
r += 2
put(ws, f'B{r}', '分路線（細節見 4_分路線）', F_BOLD, wrap=False)
r += 1
hdr(ws, r, ['路線', '2025', '2026 Q1', '2026 Q2', 'FY2026', '單位', '讀法'], c0=2)
r += 1
for key, lab, how in [('mapi', 'm_API', 'API 按量計費：實收約為有效牌價的三分之一（2026 Q2），因為 2026 的 API token 用的是 2026-03 時點值、營收份額 0.20 是餘額。'),
                      ('msub', 'm_消費訂閱', '定額月費：每個 token 實收是有效牌價的 5 倍以上，是整體 m＞1 的主因。'),
                      ('mseat', 'm_商用席次', '席次定額收費，同上；倍數在 Q1、Q2 小於消費訂閱，但 FY2026（8.12）大於消費訂閱（5.62）。')]:
    put(ws, f'B{r}', lab)
    for i, col in enumerate('FGHI'):
        put(ws, f'{CL(3 + i)}{r}', f"={c4(key, col)}", F_GREEN, None, '0.000', wrap=False)
    put(ws, f'G{r}', '倍')
    put(ws, f'H{r}', how, F_GRAY)
    r += 1
r += 1
put(ws, f'B{r}', 'm 從 2025 到 2026 Q2 為什麼變：三個因子', F_BOLD, wrap=False)
r += 1
hdr(ws, r, ['因子', '2025', '2026 Q2', '倍數（Q2 ÷ 2025）', '', '', '怎麼讀'], c0=2)
r += 1
f1 = r
for lab, key, fmt, how in [('分子：m 分子營收（$B）', 'num', '0.00', '營收成長：m 的分子變大，m 變大。'),
                           ('分母之一：付費 token（M tok/年）', 'tok', '#,##0', 'token 增加：分母變大，m 變小。2026 的 API token 與每日訊息數都明顯增加。'),
                           ('分母之二：有效牌價（$/M tok）', 'px', '0.000', '牌價基準不同（2025 年度層級單價對 2026-09 GPT-6 牌價）：分母變大，m 變小。')]:
    put(ws, f'B{r}', lab)
    put(ws, f'C{r}', f"={c3(key, 'F')}", F_GREEN, None, fmt, wrap=False)
    put(ws, f'D{r}', f"={c3(key, 'H')}", F_GREEN, None, fmt, wrap=False)
    put(ws, f'E{r}', f'=D{r}/C{r}', F_BASE, None, '0.000', wrap=False)
    put(ws, f'H{r}', how, F_GRAY)
    r += 1
put(ws, f'B{r}', 'm 倍數＝分子倍數 ÷（token 倍數 × 有效牌價倍數）', F_BOLD, FILL_M)
put(ws, f'E{r}', f'=E{f1}/(E{f1 + 1}*E{f1 + 2})', F_BOLD, FILL_M, '0.000', wrap=False)
put(ws, f'H{r}', f'="應等於 m 的 Q2 ÷ 2025："&TEXT(E{OVR["m"]}/C{OVR["m"]},"0.000")&"；差 "&TEXT(E{r}-E{OVR["m"]}/C{OVR["m"]},"0.0E+00")', F_GRAY)
r += 1
put(ws, f'B{r}', '註：「有效牌價 ×1.43」是世代與層級單價基準的更換（2025 年度層級單價 → 2026-09 GPT-6 快照），不是同一產品漲價；m 的下降有一部分來自基準更換。', F_GRAY, wrap=False)
r += 2
put(ws, f'B{r}', '與 token 帳診斷的區別（以下三項不是 m）', F_BOLD, wrap=False)
r += 1
hdr(ws, r, ['名稱', 'Tokenomics 原值', '', '', '', '單位', '一句話'], c0=2)
r += 1
for nm, expr, how in [('L1_MFleet（2025）', 'L1_MFleet', '舊的「機隊 m」：成本鏈（推論支出 → 持有成本 → GW → token）推出的付費 token 當分母。＝m ×（真實 token ÷ 模型 token），混有 token 帳誤差，不是 m。'),
                      ('L1_TokLedger（2025）', 'L1_TokLedger', '模型付費 token ÷ 需求面付費 token（＝L1_M_2025 ÷ L1_MFleet）。token 帳係數，歸數量 Q 側。'),
                      ('L1_TokLedger_2026Q2', 'L1_TokLedger_2026Q2', '同上，2026 Q2。')]:
    put(ws, f'B{r}', nm)
    paste(ws, f'C{r}', expr, '原值', '0.000')
    put(ws, f'G{r}', '倍')
    put(ws, f'H{r}', how, F_GRAY)
    r += 1
r += 1
put(ws, f'B{r}', '驗證', F_BOLD, wrap=False)
r += 1
put(ws, f'B{r}', '3_m重算 的 m ÷ Tokenomics 原值 − 1（四欄最大絕對值）')
mr = R3['m']
put(ws, f'C{r}', f"=MAX(ABS({q(S3)}!N{mr}),ABS({q(S3)}!O{mr}),ABS({q(S3)}!P{mr}),ABS({q(S3)}!Q{mr}))", F_BASE, None, '0.0000%', wrap=False)
r += 1
put(ws, f'B{r}', '4_分路線 三路線合計 − 整體 m（四欄最大絕對值）')
put(ws, f'C{r}', f"=MAX(ABS({q(S4)}!F{R4['mchk']}),ABS({q(S4)}!G{R4['mchk']}),ABS({q(S4)}!H{R4['mchk']}),ABS({q(S4)}!I{R4['mchk']}))", F_BASE, None, '0.0E+00', wrap=False)
r += 2
put(ws, f'B{r}', '最不確定的輸入（依 5_敏感度 擺動由大到小取前 8 名；細節見 6 頁）', F_BOLD, wrap=False)
r += 1
hdr(ws, r, ['輸入', '擺動', '承重度'], c0=2)
r += 1
TOP8 = r
for k in range(1, 9):
    rngL = f"'5_敏感度'!$L${first}:$L${last}"
    put(ws, f'C{r}', f'=LARGE({rngL},{k})', F_BASE, None, '0.0%', wrap=False)
    put(ws, f'B{r}', f"=INDEX('5_敏感度'!$B${first}:$B${last},MATCH(C{r},{rngL},0))", F_BASE)
    put(ws, f'D{r}', f"=INDEX('5_敏感度'!$K${first}:$K${last},MATCH(C{r},{rngL},0))", F_BASE, None, '0.00', wrap=False)
    r += 1
put(ws, f'B{r}', '註：d 的擺動是定義上的機械擺動（m ∝ 1/(1 − d)），不代表實收對表列牌價的不確定；m ×（1 − d）＝實收單價 ÷ 表列牌價，不受 d 影響。', F_GRAY, wrap=False)

# ───────────────────────── 0_說明 ─────────────────────────
ws = WS['0_說明']
widths(ws, {'A': 4, 'B': 120})
lines = [
    ('B1', 'm 閱讀版（Tokenomics v21.3）', F_T1),
    ('B2', '建立：2026-10-24（依 Andy 2026-10-21 新定義重做；同日換版到 v21.3）。用途：讓 Andy 讀懂 m（付費服務 token 的有效牌價變現率）從總覽到最細的推導。本簿每個取自 Tokenomics 的數字都已對 Tokenomics v21.3（master aa17328）逐格核對。', F_T2),
    ('B4', '定義（Andy 原話，2026-10-21）', F_BOLD),
    ('B5', '14:17「我認為m要定義成『付費服務token的有效牌價(1-折扣20%)變現率』。」 14:37「…m的定義和計算就不要牽涉到免費了…m單純只看收費業務token有效牌價變現率。」 '
           '15:39「我認知的m是有效牌價的進一步打折程度，跟營收有關，跟成本無關。」 15:59「那個(1-20%)的20%是預設折扣，不要寫死，要可以調整」「當然要拆，m本來就只有收入面」。', F_BASE),
    ('B6', '→ m＝實收單價 ÷ 有效牌價；有效牌價＝表列牌價 ×（1 − d），d＝預設折扣（Tokenomics B4_Disc，預設 0.20，可調，本簿 2_輸入 的 IN_Disc）。只有收入面。', F_BASE),
    ('B8', '分頁', F_BOLD),
    ('B9', '1_總覽：m 的一句話定義、2025／2026 Q1／Q2／FY2026 的 m 與區間、分路線、2025→2026 Q2 變化的三因子拆解、與 token 帳診斷的區別、最不確定的輸入。', F_BASE),
    ('B10', '1A_需求公式樹：從營收與付費 token 出發，逐層（L0–L5）推到 m，含 d 可調驗證與「m＝1 必須為真」。建議先讀本頁，細節再看 3–5 頁。', F_BASE),
    ('B11', '2_輸入：全部葉輸入（藍字，可改）。黃底＝不確定度高且對 m 影響大。每列附標記、區間、Tokenomics 位置與說明。', F_BASE),
    ('B12', '3_m重算：m 的逐步計算（S1–S14，四欄＝2025／2026 Q1／Q2／FY2026；另有層級單價展開表與區間端點表），每步附白話說明、原活頁簿位置、原值、差異。', F_BASE),
    ('B13', '4_分路線：m_API／m_消費訂閱／m_商用席次（營收三分 × token 三分）。', F_BASE),
    ('B14', '5_敏感度：2026 Q2 的 m 對每個有 Tokenomics 區間的輸入的單變數擺動。', F_BASE),
    ('B15', '6_不確定與證據：最不確定的輸入、要找的證據、建議管道、對 m 的影響方向（合併 v17.0 的第 7、8 頁）。', F_BASE),
    ('B16', '9_核對對照：本簿每個貼上的 Tokenomics 數字對應到 Tokenomics 的哪一格（check_reading_m.py 逐格核對用）。', F_BASE),
    ('B18', '顏色', F_BOLD),
    ('B19', '藍字＝輸入或 Tokenomics 原值（貼上）；黑字＝本簿公式；綠字＝連結到其他分頁；黃底＝最不確定、優先調研；淺綠底＝m。', F_BASE),
    ('B21', '範圍與限制', F_BOLD),
    ('B22', '1. m 只有收入面，不含成本、不經成本鏈。免費服務與訓練研發算力不進 m；免費 token 只在把 ChatGPT 總量扣成付費部分時出現。', F_BASE),
    ('B23', '2. token 帳診斷不是 m：L1_MFleet、L1_TokLedger、L1_TokLedger_2026Q2 是舊成本鏈的診斷值，在 1_總覽 只作對照並標明「不是 m」。', F_BASE),
    ('B24', '3. 回本不在本簿：回本由 L（壽命期價格係數）與所需 L 決定，見 L 閱讀版。', F_BASE),
    ('B25', '4. 2026 有效單價的牌價前緣只展開到「表列牌價 × 請求形狀 ×（1 − d）× 能力倍數」；能力倍數（ε＝0）現值為 1，只列原值，不展開。', F_BASE),
    ('B26', '5. 敏感度為單變數測試，未測交互作用；Tokenomics 無區間的輸入不自訂區間。2026 Q1／FY2026 與 2026 的分路線 m 在 Tokenomics 為單值，無區間；2025 的分路線 m（L1_MAPI／MSub／MSeat）有低／高（Cap_In D144:E146），已列在 4_分路線。', F_BASE),
    ('B28', '修訂紀錄', F_BOLD),
    ('B29', 'r2（2026-10-20）：新增 1A_需求公式樹；2_輸入 新增 K 群三個輸入（IN_SubShare、IN_SeatShare、IN_SubTokShare，取自 Tokenomics v15.3 Cap_In C70、C131、C132）。其餘頁未改。', F_BASE),
    ('B30', 'v17.0（2026-10-20）：改名為「m 閱讀版」；數字全部對 Tokenomics v17.0 核對（前置格 2,993、輸入 139、Gov_Map 區間 74、各頁原值、公式樹 42 個原值，全部相同；重算差異 < 10⁻¹⁴）；IN_SubShare 低端改為 Tokenomics 原值 0.612、標記改為 Derived（N10）；移除 9_前置格清單（閱讀用不到，另存於 repo 供換版核對）。另補推論支出、Hopper、GB200 三個輸入的 Tokenomics 區間（原本空白）。經未參與製作的代理獨立核對，不一致 0（僅限 v17.0）。', F_BASE),
    ('B31', 'v21.2 r0（2026-10-24）：依 Andy 10-21 新定義重做；舊 m（成本鏈 L1_MFleet）改列 token 帳診斷；移除 4_持有成本、5_每GW產出（屬成本鏈，新 m 不用）。新增 4_分路線，7、8 頁合併為 6_不確定與證據，新增 9_核對對照。', F_BASE),
    ('B32', 'v21.2 r1（2026-10-24）：經未參與製作的代理獨立核對（2026-10-24）：數值不符 0，文字 7 項已修（r1）；另在 4_分路線 加 2025 低／高，核對程式加檢查。', F_BASE),
    ('B33', 'v21.3 r0（2026-10-24）：對 Tokenomics v21.3 重產（GPT-6.1 Sol 快取價 0.20→0.10：有效牌價 1.961→1.943、m 1.343→1.355，+0.9%）；建檔程式改版本字樣與 1A、1_總覽 共三句寫死的數值（每則 token 10,752、FY2026 分路線 8.12／5.62、有效牌價 ×1.43）；check_reading_m.py 通過；經未參與製作的代理獨立核對。', F_BASE),
    ('B34', '本簿是 Tokenomics v21.3 的版本快照，不會隨基準模型自動同步。姊妹檔：20261024_L閱讀版_v21.3.xlsx（L 閱讀版另行維護）。', F_T2),
]
for a, t, f in lines:
    put(ws, a, t, f)

# ───────────────────────── 9_核對對照 ─────────────────────────
ws = WS['9_核對對照']
widths(ws, {'A': 16, 'B': 10, 'C': 44, 'D': 10})
put(ws, 'A1', '核對對照：本簿貼上的 Tokenomics 數字 ↔ Tokenomics 位置', F_T1, wrap=False)
put(ws, 'A2', '類型：輸入／區間低／區間高／原值＝貼上自 Tokenomics v21.3，tools/reading_workbooks/check_reading_m.py 逐格比對（相對容差 1e-9）；差異＝須 ≤ 1e-9 的差異格。閱讀時可略過本頁。', F_T2, wrap=False)
hdr(ws, 4, ['本簿頁', '本簿格', 'Tokenomics 位置（具名範圍或 頁!格；可為四則運算）', '類型'])
for i, (sh, ad, ex, kd) in enumerate(MAPROWS):
    rr_ = 5 + i
    put(ws, f'A{rr_}', sh, F_BASE, wrap=False)
    put(ws, f'B{rr_}', ad, F_BASE, wrap=False)
    put(ws, f'C{rr_}', ex, F_BASE, wrap=False)
    put(ws, f'D{rr_}', kd, F_BASE, wrap=False)

wb.save(OUTP)
print('已建檔', OUTP, '對照列', len(MAPROWS))

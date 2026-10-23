# 建 20261023_利用率服務占比_A段.xlsx（四頁：定義／證據／建議區間／待判斷）。
# 證據列讀自兩份原稿 md；模型數值讀自 model/CURRENT；換算一律用 Excel 公式（藍字＝輸入，黑字＝公式）。
import openpyxl, re, sys
from openpyxl.styles import Font, PatternFill, Alignment
D = 'docs/evidence/20261023_利用率服務占比_A段/'
MODEL = 'model/' + open('model/CURRENT').read().strip()
mv = openpyxl.load_workbook(MODEL, data_only=True)
BLUE = Font(color='0000FF'); BOLD = Font(bold=True)
HDR = PatternFill('solid', fgColor='DDEBF7'); SEC = PatternFill('solid', fgColor='F2F2F2'); WARN = PatternFill('solid', fgColor='FFF2CC')
WR = Alignment(wrap_text=True, vertical='top')
wb = openpyxl.Workbook()

def hdr(ws, r, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(r, i, v); c.font = BOLD; c.fill = HDR; c.alignment = WR
def sec(ws, r, t, n=8):
    for i in range(1, n + 1): ws.cell(r, i).fill = SEC
    ws.cell(r, 1, t).font = BOLD
def widths(ws, ws_):
    for i, w in enumerate(ws_, 1): ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

# ---------------- 頁 1 定義 ----------------
d = wb.active; d.title = '定義'
d['A1'] = '三個輸入的精確定義（對照 ' + MODEL + '）'; d['A1'].font = Font(bold=True, size=13)
hdr(d, 3, ['項目', 'AL_UtilActual（實際利用率）', 'B4_Serve（對外服務占機隊）', 'B4_Free（免費占服務）'])
al, cap = mv['Alloc_In'], mv['Cap_In']
rows = [
 ('儲存格 / 名稱', 'Alloc_In!C24:E24；Interface IF_UtilActual（C354）', 'Cap_In!C28:E28；Interface IF_ServeShare（C148）', 'Cap_In!C29:E29；Interface IF_FreeShare（C149）'),
 ('現值（基準）', al['C24'].value, cap['C28'].value, cap['C29'].value),
 ('現區間（低）', al['D24'].value, cap['D28'].value, cap['D29'].value),
 ('現區間（高）', al['E24'].value, cap['E28'].value, cap['E29'].value),
 ('現有標記', al['F24'].value, cap['F28'].value, cap['F29'].value),
 ('一句話定義', '推論服務機隊在整段營運期間（含尖峰、離峰、為尖峰預留的閒置、多模型分散部署、故障與路由不均）的「時間平均實際 token 產出 ÷ 同硬體在服務延遲目標（SLO）下可達的 100% 理論產能」。',
  '模型商機隊算力中，用於對外推論服務（付費＋免費）的比例；現值以 2025 年 OpenAI 的「推論支出 ÷（推論＋訓練支出）」代替 GW 比。',
  '對外推論服務中，免費用戶推論所占的比例；現值以 2025 年 OpenAI「非付費用戶推論支出 ÷ 推論支出」代替。'),
 ('分子', '期間內實際產出的 token 吞吐（模型內為「平均 token 吞吐」）', '用於對外服務的算力（現以支出 $8.4B 代）', '免費用戶推論算力（現以支出 $3.9B 代）'),
 ('分母', '同批 GPU 在 SLO 下的 100% 產能（Perf 頁的 roofline 吞吐，尚未乘 IF_Util 0.6）', '全部算力＝研發（預訓練、後訓練／RL、實驗、合成資料、評測）＋推論（現以 $8.4B＋$12B 代）', '全部對外推論（付費＋免費）'),
 ('口徑', '營運口徑，無單位（0–1）', '支出口徑（Derived），不是 GW 口徑；模型把它直接乘在 GW 上（L1_ServeGW_GW25 = AL_FleetGW25 × B4_Serve）', '支出口徑；與 Alloc_In C16 的 token 口徑免費占比（AL_FreeShare）尚未對齊（Decisions SL46-28）'),
 ('模型如何使用', 'Cap_In 第 114、218、255 列：有效利用率 = AL_UtilActual × CTL_ProdDerate(0.85) ÷ IF_Util(0.6)；基準 0.41×0.85=0.3485；任何「真實 token」換算都乘它',
  'IF_ServeShare → 2025 服務 GW；付費機隊占比 = B4_Serve × (1 − B4_Free) = 0.2214（Decisions SL52-06）', 'IF_FreeShare；付費機隊占比 (1 − B4_Free)'),
 ('不等於', 'GPU 分配率（被指派給服務的比例）；MFU（FLOPs ÷ 峰值 FLOPs）；nvidia-smi GPU-util（SM 有活動的時間比）；訂閱／帳號利用率；Serving!C17 IF_Util 0.6（基準測試到穩態的假設）；Serving!C28 生產折減 0.85（另乘）',
  '用戶數占比；token 占比；GW 占比（需再換算雲端加價、利用率、世代）', '免費用戶數占比（約 81%–95%）；token 占比；訊息占比'),
 ('證據轉換原則', '尖峰／平均比 → 時間平均負載；再乘「尖峰時段實際滿載度」；請求率不等於 token 吞吐，標「口徑不同」', '只有支出口徑證據可直接用；GW 口徑證據未找到', '只有 The Information 單一來源（未能核對原文）'),
]
for i, r in enumerate(rows):
    for j, v in enumerate(r, 1):
        c = d.cell(4 + i, j, v); c.alignment = WR
        if j == 1: c.font = BOLD
        if i in (1, 2, 3) and j > 1: c.font = BLUE
widths(d, [18, 55, 55, 50])
d.cell(4 + len(rows) + 1, 1, '注意').font = BOLD
d.cell(4 + len(rows) + 1, 2, '模型另有 IF_Util = Serving!C17 = 0.6（Assumed）與 CTL_ProdDerate = 0.85（Assumed）。本段只查 AL_UtilActual；兩者是否與下列證據重複計入，見「待判斷」J3。').alignment = WR

# ---------------- 頁 2 證據 ----------------
e = wb.create_sheet('證據')
e['A1'] = '證據表（每筆對應定義；口徑不同者寫換算或「口徑不同，只作參考」）'; e['A1'].font = Font(bold=True, size=13)
cols = ['編號', '變數', '來源（URL、日期）', '原文關鍵句（逐字／轉述）', '數字', '量測口徑（分子／分母）', '與定義差異／換算', '標籤與來源誘因', '讀取狀態', '採用度']
hdr(e, 3, cols)
def parse_md(path, heads):
    out = []; sect = None
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('##'): sect = line
        if line.startswith('|') and not line.startswith('|---') and not re.match(r'\|\s*(#|來源|查詢詞)', line):
            cells = [x.strip() for x in line.strip().strip('|').split('|')]
            out.append((sect, cells))
    return out
r = 4
FIX = [('2026（頁面未顯示確切日）', '2026-02-04（獨立查核確認頁面日期）'), ('頁面未顯示確切日', '頁面日期 2026-02-04（獨立查核確認）'),
       ('另一站稱免費層約占活躍用戶 81%', '另一站稱免費層約占活躍用戶 81%（獨立查核無法復現，只找到約 94%–95%）'),
       ('引 SemiAnalysis 與其他估計，非公司揭露', 'Lambda Finance 彙整，SemiAnalysis 只是其輸入之一，非公司揭露')]
def put(vals, use):
    global r
    vals = [(__import__('functools').reduce(lambda t, f: t.replace(f[0], f[1]), FIX, v) if isinstance(v, str) else v) for v in vals]
    for j, v in enumerate(vals, 1):
        c = e.cell(r, j, v); c.alignment = WR
    if use is not None: e.cell(r, 10, use).alignment = WR
    r += 1
USE_U = {'1': '採用（換算主依據）', '2': '參考', '3': '參考', '4': '參考（已有 repo 推導）', '5': '參考（低端 0.30 旁證）', '6': '不採用', '7': '不採用', '8': '不採用（口徑差大）', '9': '不採用', '10': '定性'}
sec(e, r, 'A. AL_UtilActual（來源：利用率證據_原稿.md，子代理蒐集，主代理整合）', 10); r += 1
for sect, c in parse_md(D + '利用率證據_原稿.md', 7):
    if len(c) >= 7 and c[0].isdigit():
        # 欄位：# | 來源 | 關鍵句 | 數字 | 量測口徑 | 與定義差異 | 標籤與誘因
        status = '已讀原文' if '已讀' in c[1] and '未讀' not in c[1] else ('僅搜尋摘要，未讀原文' if ('未讀' in c[1] or '僅搜尋摘要' in c[1] or '僅讀' in c[1]) else '見來源欄')
        put(['U' + c[0], 'AL_UtilActual', c[1], c[2], c[3], c[4], c[5], c[6], status], USE_U.get(c[0], '參考'))
# 本段推導列
put(['U11', 'AL_UtilActual', 'repo：docs/evidence/20261021_token帳閉合A段/吞吐實測查證.md 第 5.1 節（DeepSeek 原文自行推算，本段只引用）', '—', '輸出日均／服務期間速率 ≈ 0.58；輸入 ≈ 0.42（每節點）；節點數均值／尖峰 = 226.75/278 = 0.82', '分子：24 小時平均每節點吞吐；分母：揭露的服務期間每節點速率（不是 SLO 理論產能）', '分母是 DeepSeek 自己的服務期間速率，低於理論產能，故對本定義是上限參考；且節點數已隨負載調度', '[Derived] 由 [Interested-party] DeepSeek 自揭', '已讀（前案）', '參考（上限）'], None)
sec(e, r, 'B. B4_Serve（來源：服務占比證據_原稿.md）', 10); r += 1
USE_S = {'S1': '採用（2024 下緣）', 'S2': '參考（分母定義）', 'S3': '採用（2025 主依據）', 'S4': '採用（Anthropic 對照）', 'S5': '採用（現值出處疑點）', 'S6': '參考', 'S7': '不採用（未證實）', 'S8': '不採用（SemiAnalysis 二手）', 'S9': '不採用（未證實）', 'S10': '參考（理論）', 'S11': '參考', 'S12': '參考（分母 GW）', 'S13': '定性', 'S14': '參考', 'S15': '定性', 'S16': '定性', 'S17': '定性'}
sf = parse_md(D + '服務占比證據_原稿.md', 7)
for sect, c in sf:
    if len(c) >= 7 and re.match(r'S\d+$', c[0]):
        put([c[0], 'B4_Serve', c[1], c[2], c[3], '見數字欄', c[4], c[5], c[6]], USE_S.get(c[0], '參考'))
put(['S18', 'B4_Serve', 'repo：model/20261023_Tokenomics_v20.1.xlsx SRC_Demand 第 10 列（SRC_DEM_006）', '來源欄僅寫 openai_token_revenue.json（內部檔）', '訓練支出 $12B（約值）', '支出口徑，OpenAI 2025 年度', '現值 0.41 的分母之一；原始外部出處本段查不到（子代理搜尋亦同）。活頁簿 v17.2 已記載「15 組查詢未找到」，非本段新發現', '[Interested-party]，等級 2；出處待補', '已讀（活頁簿）', '採用（現值出處疑點）'], None)
put(['S19', 'B4_Serve', 'repo：SRC_Demand 第 22 列（SRC_DEM_018，Azure 帳單，Where\'s Your Ed At 2025-11-12，二手）', '—', '推論 $12.6B（12.3–13.0）', '支出口徑，含 Microsoft 利潤與資本回收；Q1–Q3 實際 8.67，Q4 推估', '若代入 B4_Serve：12.6/(12.6+12)=0.51；與 S3「約各半」同向。**雙重計入警告**（獨立查核指出；活頁簿 SRC_DEM_018 備註 v5.36／v15.2）：12.6 中約 $6.55B（65.5 億美元）未進 OpenAI 營業成本，最可能是研究推論，分子含研究、分母又含訓練；且含 Microsoft 加價。故 0.51 只作方向，不作範圍上緣的證據', '[Interested-party]，二手', '已讀（活頁簿）', '參考'], None)
sec(e, r, 'C. B4_Free（來源：服務占比證據_原稿.md）', 10); r += 1
for sect, c in sf:
    if len(c) >= 7 and re.match(r'F\d+$', c[0]):
        put([c[0], 'B4_Free', c[1], c[2], c[3], '見數字欄', c[4], c[5], c[6]], '參考' if c[0] != 'F1' else '採用（唯一直接證據，未獨立驗證；二手×2 同源）')
put(['F7', 'B4_Free', 'repo：DB_Evidence E231（2026-10-06）', '免費用戶約占週活躍用戶 95%（5.6% 付費）', '用戶數占比 95%', '人數口徑', '已判定口徑不同（用戶數≠算力占比），不改區間；本段維持', '[Interested-party] 聚合部落格', '已讀（活頁簿）', '參考'], None)
r += 1
sec(e, r, 'D. 已搜尋，未找到（不等於不存在）', 10); r += 1
for sect, c in parse_md(D + '利用率證據_原稿.md', 1):
    pass
nf = [l.strip('- ').strip() for l in open(D + '利用率證據_原稿.md', encoding='utf-8').read().split('## 已搜尋，未找到')[1].split('##')[0].strip().split('\n') if l.strip().startswith('-')]
for t in nf:
    put(['N', 'AL_UtilActual', t, '', '', '', '', '', '已搜尋，未找到', ''], '')
for sect, c in parse_md(D + '服務占比證據_原稿.md', 2):
    if len(c) == 2 and not c[0].startswith('S') and not c[0].startswith('F'):
        put(['N', 'B4_Serve／B4_Free', '查詢詞：' + c[0], c[1], '', '', '', '', '已搜尋，未找到', ''], '')
widths(e, [7, 14, 45, 50, 28, 32, 45, 28, 18, 18])
e.freeze_panes = 'A4'
EV_LAST = r

# ---------------- 頁 3 建議區間 ----------------
g = wb.create_sheet('建議區間')
g['A1'] = '建議區間與換算（藍字＝輸入，黑字＝公式；所有換算在此頁可逐格檢查）'; g['A1'].font = Font(bold=True, size=13)
def lab(rr, a, b='', c=None, fmt=None, blue=False, note=''):
    g.cell(rr, 1, a).alignment = WR
    if b != '':
        x = g.cell(rr, 2, b)
        if fmt: x.number_format = fmt
        if blue: x.font = BLUE
    if c is not None:
        x = g.cell(rr, 3, c); x.alignment = WR
    if note: g.cell(rr, 4, note).alignment = WR
sec(g, 3, '1. AL_UtilActual — 由尖峰／平均比換算（Azure DynamoLLM 生產 trace；請求率口徑，非 token 吞吐）', 6)
hdr(g, 4, ['項目', '值', '', '說明'])
lab(5, '尖峰÷平均：Conversation', 1.7, fmt='0.00', blue=True, note='U1 原文 "1.7× higher than its average"')
lab(6, '尖峰÷平均：Coding', 2.8, fmt='0.00', blue=True, note='U1 原文 "2.8×"')
lab(7, '平均÷尖峰：Conversation', '=1/B5', fmt='0.000')
lab(8, '平均÷尖峰：Coding', '=1/B6', fmt='0.000')
lab(9, '尖峰時段實際滿載度（低／中／高）', 0.7, blue=True, fmt='0.00', note='[Assumed]：區間 0.7–1.0；機隊為突發與故障預留餘裕。無來源，僅作敏感度')
lab(10, '', 0.85, blue=True, fmt='0.00'); lab(11, '', 1.0, blue=True, fmt='0.00')
hdr(g, 12, ['換算結果＝平均÷尖峰 × 滿載度', '滿載度 0.70', '滿載度 0.85', '滿載度 1.00'])
for i, (nm, ref) in enumerate([('Conversation', 'B7'), ('Coding', 'B8')]):
    rr = 13 + i; g.cell(rr, 1, nm)
    for j, f in enumerate(['B9', 'B10', 'B11']):
        c = g.cell(rr, 2 + j, f'=${ref[0]}${ref[1:]}*{f}'.replace('$B$', '$B$')); c.number_format = '0.000'
lab(15, '網格最小／中位／最大', '=MIN(B13:D14)', fmt='0.000')
g['C15'] = '=MEDIAN(B13:D14)'; g['D15'] = '=MAX(B13:D14)'
for c in ('C15', 'D15'): g[c].number_format = '0.000'
lab(16, 'DeepSeek 每節點日均÷服務期間速率（輸出／輸入）', 0.58, blue=True, fmt='0.00', note='U11（repo 前案推導）；分母非理論產能，視為上限參考')
g['C16'] = 0.42; g['C16'].font = BLUE; g['C16'].number_format = '0.00'
lab(17, '現值（基準／低／高）', mv['Alloc_In']['C24'].value, fmt='0.00', blue=True)
g['C17'] = mv['Alloc_In']['D24'].value; g['D17'] = mv['Alloc_In']['E24'].value
for c in ('C17', 'D17'): g[c].font = BLUE; g[c].number_format = '0.00'
lab(18, '現值是否在網格範圍內（基準）', '=IF(AND(B17>=B15,B17<=D15),"在範圍內","不在")')
lab(19, '建議（低／基準／高）', 0.30, fmt='0.00', blue=True, note='基準保留 0.41；標記由 Assumed 維持，但說明改為「類比 Azure 2023 前後 trace 的尖谷換算，非量測」。網格 0.25–0.59 支持低端 0.30 與基準；高端 0.65 仍需「離峰縮減」才成立（U4 DeepSeek 單一模型代理）。B 段旁證：U5 Aegaeon 原文實測長尾模型專屬實例 GPU 利用率 13.3–33.9%（70 小時；非機隊平均，口徑為 GPU 利用率），支持低端 0.30 合理，熱門模型無數字')
g['C19'] = 0.41; g['D19'] = 0.65
for c in ('C19', 'D19'): g[c].font = BLUE; g[c].number_format = '0.00'
g['E19'] = '標籤：Assumed／Analogy（置信度：低；無任何來源直接量到本定義）'

sec(g, 21, '2. AL_UtilActual → 回本判讀（方向與粗估；不改模型）', 6)
hdr(g, 22, ['項目', '低 0.30', '基準 0.41', '高 0.65'])
lab(23, '利用率 AL_UtilActual', '=C19-0.11', fmt='0.00'); g['B23'] = '=B19'; g['C23'] = '=C19'; g['D23'] = '=D19'
lab(24, '生產折減 CTL_ProdDerate（Serving!C28）', mv['Serving']['C28'].value, fmt='0.00', blue=True)
g['C24'] = '=B24'; g['D24'] = '=B24'
lab(25, '有效利用率＝利用率×折減', '=B23*B24', fmt='0.0000'); g['C25'] = '=C23*C24'; g['D25'] = '=D23*D24'
for c in ('C25', 'D25'): g[c].number_format = '0.0000'
lab(26, '2025 機隊損益兩平乘積 AL_FleetBE25（L1_FleetBreakeven2025）', mv['L1']['D105'].value, fmt='0.000', blue=True, note='需滿足：有效利用率 × L × m ≥ 此值（Alloc!C158）；區間 0.334–0.782 為成本角落')
g['C26'] = '=B26'; g['D26'] = '=B26'
lab(27, '所需「L×m」＝兩平乘積 ÷ 有效利用率', '=B26/B25', fmt='0.00', note='越低越容易回本；利用率每高一倍，所需 L×m 減半')
g['C27'] = '=C26/C25'; g['D27'] = '=D26/D25'
for c in ('C27', 'D27'): g[c].number_format = '0.00'
lab(28, '相對基準', '=B27/$C$27', fmt='0.00'); g['C28'] = '=C27/$C$27'; g['D28'] = '=D27/$C$27'
for c in ('C28', 'D28'): g[c].number_format = '0.00'
g['E28'] = '方向：利用率越高，同樣收入所需的價格實現度越低，回本越容易；0.30→0.65 使所需 L×m 由約 1.8 降到約 0.8（約 2.2 倍）。另：L1_MFleet（token 帳診斷）∝ 1/利用率（產出 token 增加，m 診斷值同比下降）。'

sec(g, 30, '3. B4_Serve — 支出口徑推導', 6)
hdr(g, 31, ['項目', '研發／訓練 $B', '推論 $B', '服務占比＝推論÷(研發+推論)', '說明'])
ev = [
 ('OpenAI 2024（Epoch S1；推論 $1.8B）', 5, 1.8, 'S1：研發 $5B（訓練 3＋研究 2）；B 段已讀 Epoch CSV：R&D 50 億、推論 18 億，18÷68=0.265；Interested-party → Epoch 推估'),
 ('OpenAI 2024（Epoch S1；推論 $2B 頁面小計）', 5, 2, 'S1 同源另一讀法'),
 ('OpenAI 2025（現值：SRC_DEM_004／006）', 12, 8.4, '現值；訓練 $12B 出處只到 json（S18）'),
 ('OpenAI 2025（SRC_DEM_018 推論 12.6 Azure 帳單）', 12, 12.6, 'S19：含 Microsoft 加價；分子分母口徑不同，只作方向'),
 ('Anthropic 2025（Epoch S4；毛利反推）', 4.1, 2.7, 'S4：Epoch 稱 somewhat speculative'),
]
for i, (nm, a, b, nt) in enumerate(ev):
    rr = 32 + i; g.cell(rr, 1, nm).alignment = WR
    g.cell(rr, 2, a).font = BLUE; g.cell(rr, 3, b).font = BLUE
    g.cell(rr, 4, f'=C{rr}/(B{rr}+C{rr})').number_format = '0.000'
    g.cell(rr, 5, nt).alignment = WR
lab(37, 'OpenAI 2025（Epoch S3，文字）', 0.5, fmt='0.00', blue=True, note='S3：2025 研發與推論「roughly evenly」；無精確數字，我把「各半」記為 0.50（Derived，±0.1 不確定）')
lab(38, '證據範圍（扣除 S19 後）', '=MIN(D32:D34,D36,B37)', fmt='0.000'); g['C38'] = '=MAX(D32:D34,D36,B37)'; g['C38'].number_format = '0.000'
lab(39, '建議（低／基準／高）', 0.30, fmt='0.00', blue=True, note='基準保留 0.41（扣除 S19 後證據範圍 0.26–0.50）；高 0.60 **沒有直接證據支持**（上緣證據只有 S3 文字「各半」0.50 與理論最適 0.5；短缺期服務擠壓研究 S13 為定性），僅因「不放寬也不收窄」而保留；低 0.30 由 2024 實測 0.26–0.29 支持。不提議放寬區間。口徑：支出，不是 GW')
g['C39'] = 0.41; g['D39'] = 0.60
for c in ('C39', 'D39'): g[c].font = BLUE; g[c].number_format = '0.00'
lab(40, '替代基準（Epoch「約各半」）', '=B37', fmt='0.00', note='若 Andy 選此替代（待判斷 J4），2025 服務 GW 由 0.462 升到 0.564')

sec(g, 42, '4. B4_Free — 支出口徑', 6)
hdr(g, 43, ['項目', '值', '', '說明'])
lab(44, '免費用戶推論 $B（SRC_DEM_005）', mv['SRC_Demand']['C9'].value, fmt='0.0', blue=True)
lab(45, '總推論 $B（SRC_DEM_004）', mv['SRC_Demand']['C8'].value, fmt='0.0', blue=True)
lab(46, '免費占服務', '=B44/B45', fmt='0.000', note='F1：單一來源（The Information〈Why OpenAI, Anthropic Missed Their Own Gross Margin Forecasts〉約 2026-02-24，付費牆），本段與子代理皆未能讀到原文；B 段可依此篇名取原文')
lab(47, '用戶數占比（上限參考）', 0.95, fmt='0.00', blue=True, note='F2／F7：免費約 81%–95% 的用戶，但免費用戶訊息少、有上限、模型較便宜，故算力占比應低於此')
lab(48, '建議（低／基準／高）', 0.35, fmt='0.00', blue=True, note='全部保留；證據不足以移動基準。下行訊號：免費層成本下降（F3）、改用較便宜模型（F4，低可信）')
g['C48'] = 0.46; g['D48'] = 0.60
for c in ('C48', 'D48'): g[c].font = BLUE; g[c].number_format = '0.00'

sec(g, 50, '5. B4_Serve／B4_Free → 回本判讀（方向與粗估；不改模型）', 6)
hdr(g, 51, ['項目', 'B4_Serve 低 0.30', '基準 0.41', '高 0.60', '說明'])
lab(52, 'B4_Serve', '=B39', fmt='0.00'); g['C52'] = '=C39'; g['D52'] = '=D39'
lab(53, '2025 平均上線 GW（AL_FleetGW25）', mv['Cap_In']['C331'].value, fmt='0.000', blue=True); g['C53'] = '=B53'; g['D53'] = '=B53'
lab(54, '服務 GW＝GW × B4_Serve', '=B53*B52', fmt='0.000'); g['C54'] = '=C53*C52'; g['D54'] = '=D53*D52'
lab(55, '2025 營收 $B（SRC_DEM_007）', mv['SRC_Demand']['C11'].value, fmt='0.00', blue=True); g['C55'] = '=B55'; g['D55'] = '=B55'
lab(56, '每服務 GW 營收 $B/GW', '=B55/B54', fmt='0.0'); g['C56'] = '=C55/C54'; g['D56'] = '=D55/D54'
lab(57, '機隊持有成本 $B/GW·年（AL_FleetHold）', mv['Alloc']['C157'].value, fmt='0.000', blue=True); g['C57'] = '=B57'; g['D57'] = '=B57'
lab(58, '營收 ÷（服務 GW×持有成本）', '=B56/B57', fmt='0.00'); g['C58'] = '=C56/C57'; g['D58'] = '=D56/D57'
lab(59, '相對基準', '=B58/$C$58', fmt='0.00'); g['C59'] = '=C58/$C$58'; g['D59'] = '=D58/$C$58'
for c in ('C54','D54','C56','D56','C58','D58','C59','D59'): g[c].number_format = '0.000' if c[1:] in ('54',) else '0.00'
g['E58'] = '粗估：只看服務端成本能否被營收覆蓋（研發算力視為另計），未含利用率與免費占比；不是模型輸出。方向：B4_Serve 越高，同營收分攤到越多 GW，覆蓋倍數越低（回本越難）。0.30→0.60 使覆蓋倍數約降為一半。'
g['E56'] = '營收固定、GW 變動'
hdr(g, 61, ['項目', 'B4_Free 低 0.35', '基準 0.46', '高 0.60', '說明'])
lab(62, 'B4_Free', '=B48', fmt='0.00'); g['C62'] = '=C48'; g['D62'] = '=D48'
lab(63, '付費機隊占比＝B4_Serve(基準 0.41)×(1−B4_Free)', '=$C$39*(1-B62)', fmt='0.0000'); g['C63'] = '=$C$39*(1-C62)'; g['D63'] = '=$C$39*(1-D62)'
for c in ('C63','D63'): g[c].number_format = '0.0000'
lab(64, '相對基準', '=B63/$C$63', fmt='0.00'); g['C64'] = '=C63/$C$63'; g['D64'] = '=D63/$C$63'
for c in ('C64','D64'): g[c].number_format = '0.00'
g['E63'] = '方向：免費占比越高，付費機隊越小，付費 token 的收入分母越小，m 診斷值（營收÷付費 token×牌價）越高；回本壓力越大（營收由較少付費算力承擔，但也代表免費成本為行銷費用）。0.35→0.60 使付費機隊占比由 0.27 降到 0.16。'
widths(g, [48, 18, 18, 18, 60, 40])

# ---------------- 頁 4 待判斷 ----------------
j = wb.create_sheet('待判斷')
j['A1'] = '待 Project 判斷（每題附預設與替代；本段不改模型）'; j['A1'].font = Font(bold=True, size=13)
hdr(j, 3, ['編號', '題目', '預設（建議）', '替代', '預設理由', '影響方向', '何時需決定'])
items = [
 ('J1', 'AL_UtilActual 基準 0.41 是否調整？', '保留 0.41，標記維持 Assumed，說明改寫為「類比 Azure 尖谷換算 0.25–0.59，非量測」', '改 0.36（Coding 型尖谷）或 0.50（Conversation × 滿載 0.85）', '0.41 落在換算網格中位 0.38 附近；無任何來源能支持更精確的值', '利用率 0.30→0.65，所需 L×m 由 1.8 降到 0.8；見建議區間第 2 節', '下一次改 Alloc_In C24 說明時'),
 ('J2', 'AL_UtilActual 高端 0.65 是否保留？', '保留（需「離峰縮減」才成立，DeepSeek 式；U4）', '下修到 0.60（Conversation 純平均÷尖峰 0.59）', '0.65 為單一模型代理，不是機隊；下修會使上界回本判讀更保守', '高端下修 → 所需 L×m 上界由 0.84 升到約 0.91', '與 J1 同時'),
 ('J3', '換算網格與 IF_Util 0.6、生產折減 0.85 是否重複計入？', '視網格為「相對 SLO 產能的時間平均」，生產折減 0.85 仍另乘（與現公式一致）', '若認為 Azure trace 已含餘裕與路由不均，則不再乘 0.85（有效利用率由 0.349 升到 0.41）', '尖谷換算只含時間平均，不含故障／路由；但滿載度 0.7–1.0 與折減有部分重疊，無法分離', '替代使有效利用率 +17%，所需 L×m 由 1.33 降到 1.13', '需 Project 決定口徑，B 段可補 Serving C18 的證據'),
 ('J4', 'B4_Serve 基準 0.41 是否改 0.50？', '保留 0.41（證據範圍 0.26–0.51，中位約 0.41；0.50 為 Epoch 文字「約各半」而非數字）', '改 0.50；2025 服務 GW 由 0.462 升到 0.564（+22%），每服務 GW 營收下降 18%', '現值與 Anthropic 反推 0.40、OpenAI 2024→2025 趨勢一致；且分母訓練 $12B 未驗證，不宜用不確定分母移動基準', '服務占比越高 → 覆蓋倍數越低', '取得 The Information 原文後'),
 ('J5', 'SRC_DEM_006（訓練 $12B）出處標示', '標記為「出處待補」並列入 B 段：取 The Information 或其他一手來源原文', '改以 Epoch S3「約各半」為唯一依據，並把 $12B 降為對照', '本段與子代理皆查不到 $12B 的外部原文；可能與 $12.43B Azure 推論累計混淆（S5，未證實）', '若 $12B 錯誤，B4_Serve 現值可能偏低（若訓練較小）或偏高', '建議 B 段處理（先於任何改值）'),
 ('J6', 'B4_Serve 是支出口徑卻乘在 GW 上，是否換算？', '維持（Derived），說明已寫；本段證據無 GW 口徑', '以利用率與雲端加價換算成 GW 占比', '無 GW 口徑證據可驗證換算；換算本身又引入 Assumed', '方向不定：舊世代多用於推論 → GW 占比高於支出占比', '需 Project 決定是否值得做'),
 ('J7', 'B4_Free 0.46 與 Alloc_In C16（token 口徑免費占比）是否對齊？', '不對齊（Decisions SL46-28 已接受）；B4_Free 維持 Interested-party', '把兩者統一成 token 口徑', '本段對 token 口徑免費占比未找到任何來源（只有用戶數占比）', '免費占比越高 → 付費機隊越小', '有 token 口徑證據之後'),
 ('J8', '是否發 B 段？', '發：只做取原文（The Information 2026-02、Aegaeon SOSP 2025、Cast AI、Epoch CSV），不改模型', '不發，三項都保留現值', 'A 段的主要缺口是原文未讀與分母出處，不是搜尋範圍', '—', 'Andy 決定'),
]
for i, it in enumerate(items):
    for k, v in enumerate(it, 1):
        c = j.cell(4 + i, k, v); c.alignment = WR
        if k == 1: c.font = BOLD
widths(j, [6, 38, 48, 44, 48, 44, 26])
wb.save(D + '20261023_利用率服務占比_A段.xlsx')
print('saved; evidence rows end', EV_LAST)

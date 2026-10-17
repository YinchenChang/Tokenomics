"""建立稽核結案總帳：讀原稽核明細＋catalog.py（主題判定）＋s1_cells.json（第 1 段逐格比對），
輸出 docs/reports/20261017_稽核結案對帳_明細.xlsx 與 ledger.json（供報告引用）。唯讀；不改 model/ builder/ tests/。"""
import os, sys, json, collections, re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
from catalog import FINDINGS, S0, FIX, DEC, KEEP, OPEN, RANK
from judgments import J
SUF = os.environ.get('LEDGER_SUFFIX', '')      # v15.0：非空時套用 resolve_v15（O1–O22 結案後狀態），輸出另存帶後綴新檔，不覆寫原結案報告與總帳
if SUF:
    import resolve_v15
    resolve_v15.apply_findings(FINDINGS)
REP = os.path.join(lib.ROOT, 'docs', 'reports')
SEVR = {'高': 0, '中': 1, '低': 2}

ledger = []   # 一列＝一個發現單元


def worst(ids):
    return max(ids, key=lambda i: RANK[FINDINGS[i]['status']])


def add(**k):
    ledger.append(k)


# ---------- 第 0 段 ----------
for sid, title, sev, st, how, ev, res, op in S0:
    add(seg='稽核0', uid=sid, ids=sid, sheet='（全簿）', cell='', label=title, sev=sev, desc=title,
        status=st, how=how, evidence=ev, residual=res, open=op)

# ---------- 第 1 段：186 格 ----------
s1 = json.load(open(os.path.join(HERE, 's1_cells.json')))
Y_OVERRIDE = []   # (判斷函式, 主題 ID)


def y_theme(c):
    sh, cl = c['sheet'], c['cell']
    col = re.match(r'[A-Z]+', cl).group(); row = int(re.search(r'\d+', cl).group())
    if sh == 'Spec_Rack' and row in (11, 12, 13):
        return 'Y7'
    if sh == 'Cap_In' and cl in ('C63', 'C64'):
        return 'F10'
    if sh == 'Serving' and cl in ('C17', 'C18', 'C28'):
        return 'Y5'
    if sh.startswith('Sens_'):
        return 'Y9'
    return None


for c in s1:
    go, gc = c['gov_old'] or {}, c['gov_cur'] or {}
    changed = c['old_val'] != c['cur_val']
    cat_changed = go.get('cat') != gc.get('cat')
    dec_new = gc.get('dec') not in (None, '—', '') and gc.get('dec') != go.get('dec')
    dec_pre = gc.get('dec') not in (None, '—', '') and gc.get('dec') == go.get('dec')
    rng_new = (go.get('lo'), go.get('hi')) != (gc.get('lo'), gc.get('hi'))
    th = y_theme(c)
    if th:
        F = FINDINGS[th]
        st, how, ev, res, op = F['status'], F['how'], '依主題 %s：%s' % (th, F['evidence']), F['residual'], F['open']
    elif changed or cat_changed:
        st, how = FIX, '值或標記已改（v5.36→v14.1）'
        ev = 'v5.36 值 %s → 現行 %s；Gov_Map 類別 %s → %s；決策 %s' % (str(c['old_val'])[:20], str(c['cur_val'])[:20], go.get('cat'), gc.get('cat'), gc.get('dec'))
        res, op = '', ''
    elif dec_new:
        st, how = DEC, '決策 %s（自稽核後新登錄）' % gc.get('dec')
        ev = 'Gov_Map 決策欄 %s → %s；SRC %s → %s' % (go.get('dec'), gc.get('dec'), go.get('src'), gc.get('src'))
        res, op = '值與區間未變', ''
    elif dec_pre and c['sev'] != '高':
        st, how = KEEP, '稽核時已有決策 %s 且嚴重度 %s，無處理工作單' % (gc.get('dec'), c['sev'])
        ev = 'Gov_Map 決策欄 %s 未變；值未變' % gc.get('dec'); res, op = '', 'O19'
    else:
        st, how = OPEN, '—'
        ev = '值與 Gov_Map 登錄皆未變（決策 %s／SRC %s）' % (gc.get('dec'), gc.get('src')); res = ''
        op = {'Calib': 'O8', 'Train_In': 'O17' if c['cell'].startswith('E') else ('O18' if c['cell'].startswith('C13') else 'O19'),
              'Cap_In': 'O12' if c['cell'][1:] in ('28', '29', '31', '32') else 'O19', 'Alloc_In': 'O19'}.get(c['sheet'], 'O15')
    add(seg='稽核1', uid='S1-%s' % c['gm'], ids=c['cls'], sheet=c['sheet'], cell=c['cell'], label=c['label'], sev=c['sev'],
        desc=c['reason'], status=st, how=how, evidence=ev, residual=res, open=op)

# ---------- 第 2、3A、3B：逐列檢查 ----------
SEGS = [('稽核2', '20261015_稽核2_明細.xlsx', 'F 編號'), ('稽核3A', '20261015_稽核3A_明細.xlsx', 'G 編號'), ('稽核3B', '20261015_稽核3B_明細.xlsx', 'B 編號')]
unknown = collections.Counter()
for seg, fn, idcol in SEGS:
    wb = openpyxl.load_workbook(os.path.join(REP, fn), read_only=True)
    rows = list(wb['逐列檢查'].iter_rows(values_only=True))
    h = list(rows[1]); ix = {k: i for i, k in enumerate(h) if k}
    for r in rows[2:]:
        idv = r[ix[idcol]]
        sev = r[ix['嚴重度']]
        if not idv or sev not in SEVR:
            continue
        ids = [x.strip() for x in str(idv).replace('，', ',').split(',') if x.strip()]
        for i in ids:
            if i not in FINDINGS:
                unknown[i] += 1
        ids = [i for i in ids if i in FINDINGS]
        if not ids:
            continue
        w = worst(ids)
        F = FINDINGS[w]
        add(seg=seg, uid='%s-%s-%s' % (seg, r[ix['頁']], r[ix['列']]), ids=','.join(ids), sheet=r[ix['頁']], cell='第 %s 列' % r[ix['列']],
            label=r[ix['列標籤']], sev=sev, desc='；'.join('%s：%s' % (i, FINDINGS[i]['title']) for i in ids),
            status=F['status'], how=F['how'], evidence=F['evidence'], residual=F['residual'], open=F['open'])
print('unknown ids', dict(unknown))

# ---------- 統計 ----------
if SUF:
    resolve_v15.apply_rows(ledger)
def cnt(rows):
    c = collections.Counter(r['status'] for r in rows)
    return {s: c.get(s, 0) for s in (FIX, DEC, KEEP, OPEN)}

stats = {'all': cnt(ledger), 'n': len(ledger)}
for sev in ('高', '中', '低'):
    rs = [r for r in ledger if r['sev'] == sev]
    stats[sev] = cnt(rs); stats[sev]['n'] = len(rs)
stats['by_seg'] = {}
for seg in ('稽核0', '稽核1', '稽核2', '稽核3A', '稽核3B'):
    rs = [r for r in ledger if r['seg'] == seg]
    d = cnt(rs); d['n'] = len(rs)
    d['高'] = len([r for r in rs if r['sev'] == '高']); d['高未處理'] = len([r for r in rs if r['sev'] == '高' and r['status'] == OPEN])
    stats['by_seg'][seg] = d
hi_open = [r for r in ledger if r['sev'] == '高' and r['status'] == OPEN]
stats['hi_open_n'] = len(hi_open)
# 高嚴重度未處理依 (主題, 頁) 分組
grp = collections.OrderedDict()
for r in hi_open:
    key = (r['ids'] if r['seg'] != '稽核1' else 'S1:' + r['sheet'] + ':' + re.sub(r'\d+', '', r['cell'])[:0], r['sheet'], r['open'])
    grp.setdefault(key, []).append(r)
stats['hi_open_groups'] = [dict(ids=k[0], sheet=k[1], open=k[2], n=len(v), cells=[(x['cell'] + ' ' + x['label'])[:40] for x in v][:8]) for k, v in grp.items()]
# 以主題 ID 計（F/G/B 主題）
topic = collections.Counter(FINDINGS[i]['status'] for i in FINDINGS if i[0] in 'FGB')
stats['topics'] = dict(topic); stats['n_topics'] = sum(topic.values())
ytopic = collections.Counter(FINDINGS[i]['status'] for i in FINDINGS if i[0] == 'Y')
stats['ytopics'] = dict(ytopic)
json.dump(dict(stats=stats, ledger=ledger), open(os.path.join(HERE, 'ledger%s.json' % SUF), 'w'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in stats.items() if k != 'hi_open_groups'}, ensure_ascii=False, indent=1))
print(len(stats['hi_open_groups']), 'high-open groups')

for j in J:
    j['blocks'] = '是' if j['id'] in {r['open'] for r in hi_open} else '否'

# ---------- D1–D16、Z1–Z10 ----------
D = [
 ('D1', '世代欄定義（模型規模倍數）', FIX, 'v6.2(#66) AF2-D1c', 'ARCH_ScaleGen 基準 1，情境 Lo／Hi；截面欄加註', 'J1 區間選擇見 O1'),
 ('D2', '年度計算一律用該年度口徑', FIX, 'v8.0(#70) AF2d-L1/L3/L4', 'Cap_In M 節 2025 單價；AL_RDMix；L1_FleetBreakeven2025', ''),
 ('D3', '2025 機隊世代組合', FIX, 'v6.1(#62)＋3A 查證', '區間放寬含 GB300；Alloc 世代組合', ''),
 ('D4', '殘差與倒推明示', FIX, 'v10.0(#74) AF2f-N2', 'L1「性質」欄；L1_GapUnexplained', ''),
 ('D5', '驗證必須能失敗', DEC, 'v10.0(#74) N3；v11.0／v12.0 軟上限', '驗證 22＝14 通過／7 失敗／1 警示', 'V16、V23、V24 仍是恆等式（O9）'),
 ('D6', 'Hopper 效率倍數 1.2（Derived）', DEC, 'v6.1(#62) AF3B-D6', 'Calib C67 1.2，區間 0.8–1.6', '獨立驗證失敗（O8）'),
 ('D7', '_Life／_Prod 統一', FIX, 'v6.0(#59) AF1-D7', 'Interface!C275 重解；IFW 為唯一 _Life，IF_*_Life 為過渡別名', '別名待下一主版刪除'),
 ('D8', '不可達＝文字旗標', FIX, 'v6.0(#59)／v6.2(#66)／v6.3(#67)', '單一層級、TTFT、整代不可達皆文字', ''),
 ('D9', 'm 的單價與 token 同口徑', FIX, 'v9.0(#71) AF2e-M1/M2/M3', '快取入產能；免費占比 token 口徑；κ 套價格端', 'Cap_In C28/C29 機隊切分仍支出口徑（O12）'),
 ('D10', '計價倍數經濟口徑 0.85', FIX, 'v6.1(#62) AF3B-D10', 'Alloc_In C23:E23 0.85／0.73／1.17', ''),
 ('D11', '回本溢價分母改付費 token', FIX, 'v6.0(#59) AF1-D11', 'Amortize!C13 讀付費', ''),
 ('D12', 'L、m 控制值 1＋自算並列（b）', DEC, 'v10.0(#74) AF2f-N1', '8 個 IFW_*_LifeSelf', ''),
 ('D13', '暫定值接受為 Assumed 區間中點', DEC, 'v6.1(#62) AF3B-D13', 'Decisions「暫定、待證據」；Alloc_In C24 0.41', '證據仍待補（O19、O20）'),
 ('D14', '研發與服務 GW 以支出路線為主', FIX, 'v8.0(#70) AF2d-L5', 'IF_AllocQ1/Q2/ServeGW 支出路線；token 路線並列', 'SRC_DEM_004 區間未被引用（O13）'),
 ('D15', '來源補齊與積壓', DEC, 'v13.1(#98) D15-01…12', 'Gov_Map 無來源也無決策 311→0；積壓 106 列有建議處置', '6 列待查、積壓規則（O16）'),
 ('D16', 'Hopper 設施與價格／利用率口徑／瘦身', OPEN, 'v6.1 AF3B-Q6（PUE、價格已記）；v10.1–v14.1（死格）', 'PUE 與價格、死格已處理', '訓練與服務利用率口徑尚未寫明（G13，O12）'),
]
Z = [
 ('Z1', '同一時點層級模型套用全部世代', 'Y1', DEC, '無'), ('Z2', '年度計算時點混用', 'Y2、B03、B06、F05、G15', FIX, 'G15（O12）'),
 ('Z3', '殘差與倒推被當估計', 'F01–F03、B02、B04、G08', DEC, 'Hopper 無解（O8）'),
 ('Z4', '循環驗證與無法失敗的檢查', 'G05、B04、B08', DEC, 'V16／V23／V24（O9）'), ('Z5', '同名兩種定義（_Life／_Prod）', 'G03、G04、B16、F04', FIX, '別名待刪除'),
 ('Z6', '分母與口徑', 'G01、G02、F11、F06', FIX, 'G13、G14（O12）'), ('Z7', '不可達處理不對稱', 'F09、G06、B05', FIX, '無'),
 ('Z8', '暫定值以基準身分進入模型', 'Y5、F15', DEC, '證據待補（O19、O20）'), ('Z9', '來源與文件', 'S0-C1、B07、B12、Y9', OPEN, 'B07、Y9（O14、O15）'),
 ('Z10', 'Hopper 欄設施與價格時點', 'Y4、Y7', DEC, '無'),
]

# ---------- 驗證項（假設對現實） ----------
V = lib.val()['Checks']
vrows = []
for r in V.iter_rows(min_row=1, max_row=V.max_row, values_only=True):
    a = r[0]
    if isinstance(a, str) and re.fullmatch(r'V\d{1,2}', a):
        vrows.append(r[:9])

# ---------- Excel ----------
OUT = os.path.join(REP, '20261017_稽核結案對帳_明細%s.xlsx' % SUF)
wb = openpyxl.Workbook()
HF = PatternFill('solid', fgColor='DDE6F0'); BOLD = Font(bold=True)
FILL = {FIX: 'E2F0D9', DEC: 'DDEBF7', KEEP: 'FFF2CC', OPEN: 'F8CBAD'}


def sheet(title, header, rows, widths=None, status_col=None, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    ws.append(header)
    for c in ws[1]:
        c.font = BOLD; c.fill = HF; c.alignment = Alignment(wrap_text=True, vertical='top')
    for r in rows:
        ws.append(list(r))
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    if status_col:
        for row in ws.iter_rows(min_row=2):
            c = row[status_col - 1]
            if c.value in FILL:
                c.fill = PatternFill('solid', fgColor=FILL[c.value])
            for x in row:
                x.alignment = Alignment(wrap_text=True, vertical='top')
    return ws


readme = [
 ['稽核結案對帳明細（2026-10-17）'], ['對照基準：model/CURRENT＝' + lib.CUR + '；稽核時版本 v5.36（2026-10-15）。'],
 ['狀態四種：已修正／已記為決策／刻意保留／未處理。同一列有多個發現編號時，取最差的狀態。'],
 ['「總帳」頁一列＝一個發現單元：第 0 段機械項（13 項）、第 1 段逐格（186 格）、第 2／3A／3B 段逐列（flagged 列）。'],
 ['第 1 段判定規則：值或類別已改→已修正；稽核後新登錄決策→已記為決策；稽核時已有決策且嚴重度中低→刻意保留；高嚴重度且值與登錄皆未變→未處理（含稽核時已有決策者，因稽核看到決策後仍標高）；另有 Y 主題覆蓋 4 組（Spec_Rack 11–13、Cap_In C63／C64、Serving C17／C18／C28、Sens_*）。'],
 ['第 2／3A／3B 段判定：依發現編號（F／G／B）逐一判定（見「發現主題」頁），列繼承該列編號中最差的狀態。'],
 ['「8 of 11 verified assumptions」在 repo 與稽核明細中找不到出處；本檔以「驗證項」頁（Checks V1–V26 現況）呈現假設對現實的對照，並在報告揭露此缺口。'],
 ['查證方式：開現行活頁簿（openpyxl，LibreOffice 存檔值）與 v5.36 逐格比對；腳本在 docs/evidence/20261017_稽核結案/。'],
]
ws = wb.active; ws.title = '說明'
for r in readme:
    ws.append(r)
ws.column_dimensions['A'].width = 140
sheet('總帳', ['單元ID', '段', '發現編號', '頁', '格／列', '列標籤', '嚴重度', '描述', '狀態', '處理（版本／PR／決策）', '查證依據', '殘餘', '待判斷編號'],
      [[r['uid'], r['seg'], r['ids'], r['sheet'], r['cell'], r['label'], r['sev'], r['desc'], r['status'], r['how'], r['evidence'], r['residual'], r['open']] for r in ledger],
      [20, 8, 12, 12, 10, 28, 7, 50, 10, 34, 44, 30, 9], status_col=9)
cat_rows = [[k, v['title'], v['status'], v['how'], v['evidence'], v['residual'], v['open']] for k, v in FINDINGS.items()]
sheet('發現主題', ['編號', '主題', '狀態', '處理（版本／PR／決策）', '現行活頁簿查證', '殘餘', '待判斷編號'], cat_rows, [8, 40, 10, 40, 60, 40, 9], status_col=3)
sheet('D1-D16', ['決定', '內容', '狀態', '處理', '現行簿證據', '殘餘'], D, [6, 36, 10, 36, 50, 40], status_col=3)
sheet('Z1-Z10', ['系統性問題', '內容', '涵蓋發現', '主體狀態', '殘餘（未處理者）'], Z, [8, 36, 30, 10, 30], status_col=4)
sheet('驗證項', ['編號', '內容', '模型值', '實測／目標', '比值或結果', '判定', '類型', '下限', '上限'], vrows, [6, 70, 12, 12, 12, 14, 14, 8, 8])
sheet('待判斷', ['編號', '事項', '阻擋結案', '相關發現', '背景', '選項', '建議預設', '理由', '影響'],
      [[j['id'], j['title'], j['blocks'], j['refs'], j['bg'], j['opts'], j['default'], j['reason'], j['impact']] for j in J],
      [6, 34, 8, 20, 70, 40, 24, 36, 40])
sheet('高嚴重度未處理', ['單元ID', '段', '發現編號', '頁', '格／列', '列標籤', '描述', '殘餘', '待判斷編號'],
      [[r['uid'], r['seg'], r['ids'], r['sheet'], r['cell'], r['label'], r['desc'], r['evidence'], r['open']] for r in hi_open],
      [22, 8, 12, 12, 10, 28, 50, 44, 9])
wb.save(OUT)
print('saved', OUT)

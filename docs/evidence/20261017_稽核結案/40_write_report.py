"""由 ledger.json 與 judgments.py 產生 docs/reports/20261017_稽核結案對帳.md。"""
import os, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
from catalog import FINDINGS, FIX, DEC, KEEP, OPEN
from judgments import J
d = json.load(open(os.path.join(HERE, 'ledger.json')))
S, L = d['stats'], d['ledger']
ST = (FIX, DEC, KEEP, OPEN)
blocking = {r['open'] for r in L if r['sev'] == '高' and r['status'] == OPEN}
for j in J:
    j['blocks'] = '是' if j['id'] in blocking else '否'


def row(label, c, n=None):
    n = n if n is not None else sum(c[s] for s in ST)
    return '| %s | %d | %d | %d | %d | %d |' % (label, c[FIX], c[DEC], c[KEEP], c[OPEN], n)


o = []
w = o.append
w('# 稽核結案對帳（2026-10-17）')
w('')
w('- 分支：`claude/audit-close`（從 origin/master 起）')
w('- 報告檔：`docs/reports/20261017_稽核結案對帳.md`；明細：`docs/reports/20261017_稽核結案對帳_明細.xlsx`；證據與腳本：`docs/evidence/20261017_稽核結案/`')
w('- 最新提交 SHA：見 PR 最後一則 comment（本報告在同一提交內，無法自引 SHA）')
w('- 對照版本：現行 `%s`（model/CURRENT）對稽核時 v5.36。本輪只讀，沒有改 model/、builder/、tests/、docs/builder/。' % lib.CUR)
w('')
w('## 0. 結論與計數')
w('')
hi = S['高']
w('**一句話**：稽核共 %d 個發現單元，%d 個（%d%%）已修正或已記為決策，%d 個刻意保留，**%d 個未處理**；其中**高嚴重度未處理 %d 個**（原高嚴重度共 %d 個）。這 %d 個高嚴重度未處理全部收斂到 %d 項待判斷事項（見第 3、4 節），這 %d 項都需要 Andy 表態後才可宣告稽核結案；其餘待判斷不阻擋。' % (
    S['n'], S['all'][FIX] + S['all'][DEC], round(100 * (S['all'][FIX] + S['all'][DEC]) / S['n']), S['all'][KEEP], S['all'][OPEN], S['hi_open_n'], hi['n'], S['hi_open_n'], len(blocking), len(blocking)))
w('')
w('### 0.1 依狀態與嚴重度（一列＝一個發現單元，口徑見第 1 節）')
w('')
w('| 嚴重度 | 已修正 | 已記為決策 | 刻意保留 | 未處理 | 合計 |')
w('|---|---|---|---|---|---|')
for sev in ('高', '中', '低'):
    w(row(sev, S[sev], S[sev]['n']))
w(row('**全部**', S['all'], S['n']))
w('')
w('### 0.2 依稽核段')
w('')
w('| 段 | 已修正 | 已記為決策 | 刻意保留 | 未處理 | 合計 | 其中高嚴重度 | 高嚴重度未處理 |')
w('|---|---|---|---|---|---|---|---|')
names = {'稽核0': '0 機械檢查（13 項）', '稽核1': '1 輸入判讀（186 格）', '稽核2': '2 m 路徑邏輯（flagged 列）', '稽核3A': '3A 其餘推導列', '稽核3B': '3B 下游推導列'}
for k, v in S['by_seg'].items():
    w('| %s | %d | %d | %d | %d | %d | %d | %d |' % (names[k], v[FIX], v[DEC], v[KEEP], v[OPEN], v['n'], v['高'], v['高未處理']))
w('')
t = S['topics']
w('### 0.3 依發現主題（F／G／B 共 %d 個編號，不論列數）' % S['n_topics'])
w('')
w('已修正 %d、已記為決策 %d、刻意保留 %d、未處理 %d。另外第 1 段的九個系統性問題 Y1–Y9：已修正 %d、已記為決策 %d、未處理 %d（Y9 敏感度端點）。' % (
    t.get(FIX, 0), t.get(DEC, 0), t.get(KEEP, 0), t.get(OPEN, 0), S['ytopics'].get(FIX, 0), S['ytopics'].get(DEC, 0), S['ytopics'].get(OPEN, 0)))
w('')
w('### 0.4 高嚴重度未處理（%d 個單元，分 %d 組）' % (S['hi_open_n'], len(S['hi_open_groups'])))
w('')
w('| 組 | 頁 | 單元數 | 發現編號或範圍 | 內容舉例 | 待判斷 |')
w('|---|---|---|---|---|---|')
for i, g in enumerate(S['hi_open_groups'], 1):
    ids = g['ids'].replace('S1:', '第 1 段 ').rstrip(':')
    w('| H%d | %s | %d | %s | %s | %s |' % (i, g['sheet'], g['n'], ids, '；'.join(g['cells'][:3]).replace('|', '／'), g['open']))
w('')
w('逐單元清單在明細 xlsx 的「高嚴重度未處理」頁。')
w('')
w('### 0.5 能不能宣告稽核結案')
w('')
nb = [j for j in J if j['blocks'] == '是']
w('可以，但有條件：第 4 節的 %s 共 %d 項各含高嚴重度未處理單元，需要 Andy 對每一項回「接受並記為決策／刻意保留／要求修正」其中之一；其餘 %d 項不阻擋。我建議的預設見第 4 節；若全部採用建議，需要實際動手的只有 O13、O14、O15 的 B 部分（皆為小型工程類工作單，不改基準值）。' % (
    '、'.join(j['id'] for j in nb), len(nb), len(J) - len(nb)))
w('')
w('## 1. 怎麼數的（口徑與限制）')
w('')
w('1. **單元**：第 0 段 13 個機械項；第 1 段 186 個被標嚴重度的輸入格；第 2、3A、3B 段「逐列檢查」頁凡帶 F／G／B 編號的列（%d + %d + %d = %d 列，其中高嚴重度 %d 列，與稽核報告的 171 相符）。簡報所說「約 441 列」與本檔 %d 列的差距來自我只收帶編號且有嚴重度的列；沒有編號的列是檢查通過列。' % (
    S['by_seg']['稽核2']['n'], S['by_seg']['稽核3A']['n'], S['by_seg']['稽核3B']['n'], S['by_seg']['稽核2']['n'] + S['by_seg']['稽核3A']['n'] + S['by_seg']['稽核3B']['n'],
    S['by_seg']['稽核2']['高'] + S['by_seg']['稽核3A']['高'] + S['by_seg']['稽核3B']['高'], S['by_seg']['稽核2']['n'] + S['by_seg']['稽核3A']['n'] + S['by_seg']['稽核3B']['n']))
w('2. **狀態繼承**：F／G／B 列的狀態由它的發現編號決定（62 個編號逐一判定，見明細「發現主題」頁）；一列帶多個編號時取最差的。所以「列」的計數會把一個沒解決的編號放大成它影響的所有列，這是保守做法。')
w('3. **第 1 段逐格規則**：值或類別已改→已修正；稽核之後才登錄決策→已記為決策（D15 把 m 路徑高嚴重度格補決策編號，即屬此類）；稽核時就有決策、嚴重度中或低→刻意保留；**高嚴重度且值與登錄皆未變→未處理**（即使稽核時已有決策編號，因為稽核看過決策後仍標高）。另有四組由主題覆蓋：Spec_Rack 11–13 列（Y7，稽核誤讀已更正）、Cap_In C63／C64（D12(b) 並列自算值）、Serving C17／C18／C28（D13 暫定）、Sens_* 頁（Y9）。')
w('4. **「已修正」是否真修正**：我用現行活頁簿核對了公式與數值，不是只相信報告，例如 Interface!C275、Theory_Rev!C90、Cap_In C87（0.54→0.40）、Alloc_In C23:E23、Alloc_In C24（0.41）、Fleet_1GW!C18、IF_AllocQ1_R2（=AL_Q1R2）、Cap_In 第 245 列已清空、Perf 第 93 列；腳本 `20_checks.py`、`22_more_checks.py`、`show.py`。第 1 段「值已改」只確認值與標記有變，沒有逐格重審新值是否合理。')
w('5. **找不到的出處**：任務敘述的「11 個已驗證假設中 8 個與現實不符」在 repo 的稽核報告與明細中沒有出處（全文搜尋 0 筆）。本檔改以現行 Checks 的 V1–V26 對照（驗證項 22＝14 通過、7 失敗、1 警示；V18、V23、V24 為恆等式），明細有「驗證項」頁。**請 chat 端確認那句話的出處**；若它指的是另一份文件，請提供，我再對。')
w('6. **現行健康度**：GOV_Errors 0、GOV_Warnings 280、GOV_Info 184、RNG_OutCount 0；CHK_SoftCapFail 2。這些讀自 LibreOffice 存檔後的值。')
w('')
w('## 2. 主要發現的處理對照（D1–D16 與 Z1–Z10）')
w('')
w('| 決定 | 內容 | 狀態 | 處理 | 殘餘 |')
w('|---|---|---|---|---|')
import importlib.util
src = open(os.path.join(HERE, '30_build_ledger.py'), encoding='utf-8').read()
ns = {}
start = src.index('D = ['); end = src.index('# ---------- 驗證項')
exec(src[start:end], {'FIX': FIX, 'DEC': DEC, 'KEEP': KEEP, 'OPEN': OPEN}, ns)
for x in ns['D']:
    w('| %s | %s | %s | %s | %s |' % (x[0], x[1], x[2], x[3], x[5] or '—'))
w('')
w('系統性問題：')
w('')
w('| 編號 | 內容 | 主體狀態 | 殘餘 |')
w('|---|---|---|---|')
for x in ns['Z']:
    w('| %s | %s | %s | %s |' % (x[0], x[1], x[3], x[4]))
w('')
w('Z9 標未處理是因為其中 B07（L1 外部對照單位錯配）與 Y9（敏感度端點）仍在；Z9 的 311 列無來源也無決策已由 D15（v13.1）降為 0。')
w('')
w('## 3. 高嚴重度未處理的原因（逐組）')
w('')
why = {
 'Calib': '稽核時就是 Analogy／無 SRC 的效率校準格（η_p、η_d 倍數 GB200／VR200／RU 沿用）；登錄與值皆未變。Hopper 部分已由 D6 記為決策，但這些是「其他世代沿用」的格。',
 'Train_In': '預訓練 MFU、goodput 說明仍標「待查」，Analogy 來源；研發倍數 J10；預訓練 token 60T（J8）。',
 'Cap_In': '機隊切分（C28／C29）、層級組合（C31／C32）仍支出口徑或無 SRC；儲存層索引、席次占比（J18）、消費訂閱份額無證據。皆已有 K7／K10／X38／X39 類決策編號，稽核看過後仍標高。',
 'Alloc_In': 'API 全年平均÷10 月（C14）、每則提示 token（C15，閉合差距維持「未解釋」）、免費用戶占比（C16）、實際利用率×折減（D24）無直接來源。',
 'Alloc': '第 61 列支出路線服務 GW 的錨點 SRC_DEM_004 為利害關係方，區間 _Lo／_Hi 全簿 0 個公式引用（F17）。',
 'Fleet_1GW': '機隊占比取 2025 OpenAI 支出比、隱含每 GW 年家族計畫 3.07 高於參考（G14／G15）。',
 'Amortize': '縮放倍數 2.42 由 B4_Serve 決定（G14）。',
 'Interface': '上列縮放倍數與付費組合營收的下游包裝列（G14／G15），契約名稱 IF_AmortDefault_*、IF_FullCostDefault_*、IFW_RevGW_* 受影響。',
 'Training': '合成資料與評測 GPU 小時用訓練 MFU 計價（B20）。',
 'Harness': '前緣可靠度門檻提高時名稱變文字（B11）。',
 'L1': '外部對照每架對每 GW（B07），P 欄判讀失真。',
}
for i, g in enumerate(S['hi_open_groups'], 1):
    w('- **H%d（%s，%d 個單元，%s）**：%s' % (i, g['sheet'], g['n'], g['open'], why.get(g['sheet'], '')))
w('')
w('## 4. 待 Andy 判斷（O1–O22）')
w('')
w('「阻擋結案」＝該項含高嚴重度未處理單元；Andy 只需對它選一個處置（接受並記為決策／刻意保留／要求修正）即可。所有「建議預設」都不改變任何基準契約數值，除非另外註明。')
w('')
w('| 編號 | 事項 | 阻擋結案 | 建議預設 |')
w('|---|---|---|---|')
for j in J:
    w('| %s | %s | %s | %s |' % (j['id'], j['title'], j['blocks'], j['default']))
w('')
for j in J:
    w('### %s　%s' % (j['id'], j['title']))
    w('')
    w('- **阻擋結案**：%s　**相關發現**：%s' % (j['blocks'], j['refs']))
    w('- **背景**：%s' % j['bg'])
    w('- **選項**：%s' % j['opts'])
    w('- **建議預設**：%s %s' % (j['default'], '理由：' + j['reason']))
    w('- **影響**：%s' % j['impact'])
    w('')
w('## 5. 結案建議（給 chat 端）')
w('')
w('1. 若 Andy 對第 4 節的阻擋項採用建議預設，稽核可在三張小工作單後宣告結案：(a) O13（讓 SRC_DEM_004 區間進名稱）、(b) O14（L1 外部對照單位）、(c) O15 B（Alloc／Harness／Training 守衛與標籤、Y9 敏感度端點）。三者皆不改基準值。')
w('2. O12、O17、O18、O19、O8 建議「接受並補一筆總決策進 Decisions」，這是判斷類，需 chat 端發工作單由 CC 寫入。')
w('3. 已自然解決、可從待判斷清單移除：O2（Hopper 2.69 倍已不存在）、O7（IF_AllocQ1_R2 已走支出路線）。')
w('4. 第 1 段「已記為決策」109 格多數是 D15 補決策編號，其本質仍是 Assumed；這些格的證據查證（外部搜尋）才是長期工作，不影響結案。')
w('')
w('## 6. 預期變動 vs 實際變動')
w('')
w('本輪是唯讀對帳，未產生新 Excel 版本。表 1：不適用（無工作單項目改 Excel）。表 2：model/、builder/、tests/、docs/builder/ 的差異 0。parity 全套未跑（無 model 變動，docs-only）。GOV 三項為讀現行簿：0／280／184。')
w('')
w('## 7. 待 Project 判斷')
w('')
w('見第 4 節 O1–O22。另有兩點屬本輪方法：(1) 「8 of 11」出處（第 1 節第 5 點）；(2) 狀態繼承與第 1 段規則是否接受（第 1 節第 2、3 點）。')
w('')
w('## 8. 成本')
w('')
w('| 項目 | 數值 |')
w('|---|---|')
w('| 代理模型 | Claude Sonnet 5.5（含一次上下文壓縮續接） |')
w('| 工具呼叫 | 未精確統計（約 150 次） |')
w('| 數值檢查 | 未跑（docs-only） |')
open(os.path.join(lib.ROOT, 'docs', 'reports', '20261017_稽核結案對帳.md'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print('ok', len(o))

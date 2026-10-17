"""v15.1：由 ledger_v15.1.json 產生 docs/reports/20261017_稽核結案對帳_v15.1.md（不改 40_write_report.py，v15.0 檔不覆寫）。"""
import os, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib, resolve_v15
from catalog import FIX, DEC, KEEP, OPEN

d = json.load(open(os.path.join(HERE, 'ledger_v15.1.json')))
S, L = d['stats'], d['ledger']
ST = (FIX, DEC, KEEP, OPEN)


def row(label, c, n=None):
    n = n if n is not None else sum(c[s] for s in ST)
    return '| %s | %d | %d | %d | %d | %d |' % (label, c[FIX], c[DEC], c[KEEP], c[OPEN], n)


o = []
w = o.append
hi = S['高']
fixed_dec = S['all'][FIX] + S['all'][DEC]
w('# 稽核結案對帳 v15.1（2026-10-17）——逐單元重判')
w('')
w('- 分支：`claude/v15-1`；最新提交 SHA：見 PR 最後一則 comment（本檔在同一提交內，無法自引）')
w('- 報告檔：`docs/reports/20261017_稽核結案對帳_v15.1.md`；明細：`docs/reports/20261017_稽核結案對帳_明細_v15.1.xlsx`；腳本與證據：`docs/evidence/20261017_稽核結案/`（`resolve_v151.py`、`30_build_ledger.py`、`41_write_report_v151.py`、`ledger_v15.1.json`）')
w('- 對照版本：`%s`（model/CURRENT）；前一版對帳 `20261017_稽核結案對帳_v15.0.md` 與其明細保持不變，不覆寫。' % lib.CUR)
w('')
w('## 0. 結論與計數')
w('')
w('**一句話**：稽核共 %d 個單元，已修正 %d、已記為決策 %d、刻意保留 %d、未處理 %d；高嚴重度 %d 個中未處理 %d。**但「未處理 0」不等於「證據補齊」**：高嚴重度的輸入格中，仍有 %d 個（共 %d 個高嚴重度輸入格）標 Assumed 且沒有外部來源 SRC，另有 %d 個是其他類別也沒有 SRC；這些格的狀態是「已記為決策」（有人決定接受它），不是「已找到來源」。' % (
    S['n'], S['all'][FIX], S['all'][DEC], S['all'][KEEP], S['all'][OPEN], hi['n'], hi[OPEN], S['hi_assumed_nosrc'], S['hi_s1_n'], S['hi_nosrc_other']))
w('')
w('### 0.1 依狀態與嚴重度')
w('')
w('| 嚴重度 | 已修正 | 已記為決策 | 刻意保留 | 未處理 | 合計 |')
w('|---|---|---|---|---|---|')
for sev in ('高', '中', '低'):
    w(row(sev, S[sev], S[sev]['n']))
w(row('**全部**', S['all'], S['n']))
w('')
w('### 0.2 高嚴重度未處理清單')
w('')
unres = [r for r in L if r['sev'] == '高' and r['status'] == OPEN]
if unres:
    w('| 單元 | 頁 | 位置 | 說明 |')
    w('|---|---|---|---|')
    for r in unres:
        w('| %s | %s | %s | %s |' % (r['uid'], r['sheet'], r['cell'], r['desc'][:60]))
else:
    w('無（0 個）。')
w('')
w('### 0.3 判定依據的種類（每個單元都要有一個具體證據指標）')
w('')
w('| 證據種類 | 單元數 | 說明 |')
w('|---|---|---|')
expl = {
    '決策逐字涵蓋': '本版重判：Decisions 的 SL46-* 決議或影響範圍文字，逐字點名這個頁與列（或格）',
    '列自帶決策標註': '本版重判：該列自己的說明欄已引用 SL46-nn（v14.2 時沒有）',
    '格差異＋決策': '本版重判：v14.2→v15.1 該格公式或值有實質差異，且有決策涵蓋',
    '修正點在他處（探針）': '本版重判：修正在別的格（F17、F12、G11），以探針逐一確認',
    '沿用前版判定＋核對': '前版已結案的單元；本版只核對 S1 值未變、決策編號存在、列標籤相符',
    '沿用前版判定': '前版已結案的第 0 段機械檢查項，未重核',
}
for k, v in sorted(S['ev_kinds'].items(), key=lambda x: -x[1]):
    w('| %s | %d | %s |' % (k, v, expl.get(k, '')))
w('')
w('本版重判的單元共 %d 個（原未結案者）；其餘 %d 個沿用前版。判定規則：實質差異→已修正；否則屬保留類決策（SL46-07、SL46-30、SL46-03 的「維持／刻意保留」）→刻意保留；否則有決策或自帶標註→已記為決策；否則維持未處理（本版 0 個）。不按 O 編號整批翻轉。「附加說明文字」只算標註，不算實質修正。' % (
    sum(1 for r in L if r['rejudged'] == '是'), sum(1 for r in L if r['rejudged'] != '是')))
w('')
w('### 0.4 與 v15.0 對帳的狀態差異')
w('')
w('| 嚴重度 | 單元 | 位置 | v15.0 | v15.1 | 依據 |')
w('|---|---|---|---|---|---|')
for c in S['changed_vs_v150']:
    w('| %s | %s | %s %s | %s | %s | %s %s |' % (c['sev'], c['uid'], c['sheet'], c['cell'], c['old'], c['new'], c['kind'], c['ptr'][:60]))
w('')
w('這 4 個單元的原因：Harness 126、129、132 在 v15.0 因 O12 的 SL46-03 被判已修正，實際是「刻意保留」（該列的文字經確認後不改，只記決策）；L1 第 35 列沒有公式或值的實質差異，只有 SL46-02 的決策，改判已記為決策。其餘 627 個單元的狀態不變，但 161 個原未結案單元已逐一附上證據指標（明細「證據指標」欄）。')
w('')
w('### 0.5 外部來源缺口（高嚴重度輸入格）')
w('')
w('| 項目 | 數量 |')
w('|---|---|')
w('| 高嚴重度輸入格（第 1 段） | %d |' % S['hi_s1_n'])
w('| 其中有 SRC 外部來源 | %d |' % S['hi_with_src'])
w('| 其中標 Assumed 且沒有 SRC | %d |' % S['hi_assumed_nosrc'])
w('| 其中其他類別且沒有 SRC | %d |' % S['hi_nosrc_other'])
w('')
w('v15.0 的檢查同樣是 98／146。這代表本版沒有「找到」新來源；稽核結案的意思是每一項都有人決定，不是每一項都有外部證據。明細新增「有無外部來源」欄可逐格篩選。')
w('')
w('### 0.6 依稽核段')
w('')
w('| 段 | 已修正 | 已記為決策 | 刻意保留 | 未處理 | 合計 | 其中高嚴重度 |')
w('|---|---|---|---|---|---|---|')
names = {'稽核0': '0 機械檢查', '稽核1': '1 輸入判讀', '稽核2': '2 m 路徑邏輯', '稽核3A': '3A 其餘推導列', '稽核3B': '3B 下游推導列'}
for k, v in S['by_seg'].items():
    w('| %s | %d | %d | %d | %d | %d | %d |' % (names[k], v[FIX], v[DEC], v[KEEP], v[OPEN], v['n'], v['高']))
w('')
t = S['topics']
w('發現主題（F／G／B 共 %d 個編號）：已修正 %d、已記為決策 %d、刻意保留 %d；系統性問題 Y1–Y9 中 Y9 在主題頁仍標未處理（它沒有對應的單元，v15.0 O15 與本版 U2-4 已處理 Sens_Rev／Sens_Train 端點，見 SL46-05、SL46-31；主題頁標記未翻，列待 Project 判斷）。' % (
    S['n_topics'], t.get(FIX, 0), t.get(DEC, 0), t.get(KEEP, 0)))
w('')
w('## 1. 「怎麼處理」欄的決策編號更正')
w('')
w('v15.0 對帳的 Harness 第 151–153 列、L1 第 31、35、61–65 列指向錯誤的決策編號。本版已改為：')
w('')
w('| 單元 | 現在的處理指標 |')
w('|---|---|')
for r in L:
    if (r['sheet'] == 'Harness' and r['cell'] in ('第 151 列', '第 152 列', '第 153 列')) or (r['sheet'] == 'L1' and r['cell'] in ('第 31 列', '第 35 列', '第 61 列', '第 62 列', '第 63 列', '第 64 列', '第 65 列')):
        w('| %s %s | %s |' % (r['sheet'], r['cell'], r['ev_ptr']))
w('')
w('## 2. 主要發現的處理對照（D1–D16 與 Z1–Z10）')
w('')
w('| 決定 | 內容 | 狀態 | 處理 | 殘餘 |')
w('|---|---|---|---|---|')
src = open(os.path.join(HERE, '30_build_ledger.py'), encoding='utf-8').read()
ns = {}
start = src.index('D = ['); end = src.index('# ---------- 驗證項')
exec(src[start:end], {'FIX': FIX, 'DEC': DEC, 'KEEP': KEEP, 'OPEN': OPEN}, ns)
resolve_v15.patch_DZ(ns)
for x in ns['D']:
    w('| %s | %s | %s | %s | %s |' % (x[0], x[1], x[2], x[3], x[5] or '—'))
w('')
w('| 編號 | 內容 | 主體狀態 | 殘餘 |')
w('|---|---|---|---|')
for x in ns['Z']:
    w('| %s | %s | %s | %s |' % (x[0], x[1], x[3], x[4]))
w('')
w('## 3. 限制')
w('')
w('1. 沿用前版的 470 個單元只做輕量核對（值相同、決策編號存在、列標籤相符），沒有逐一重新讀證據。')
w('2. 部分單元的證據是「列層級」或「只有標註」的決策，而非針對格的實質修正；明細的「證據種類」欄可篩出。')
w('3. 「已記為決策」不改變該格仍是 Assumed 的事實。')
open(os.path.join(lib.ROOT, 'docs', 'reports', '20261017_稽核結案對帳_v15.1.md'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print('ok', len(o))

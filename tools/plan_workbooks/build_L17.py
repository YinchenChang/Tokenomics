# 建立「L 推導檢核」活頁簿：L（壽命期價格係數）、所需 L（恆等式讀法）、回本判讀，全部為 Excel 公式
import openpyxl, json, re, math
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as CL
from openpyxl.formatting.rule import CellIsRule

SRC = 'v170.xlsx'
wv = openpyxl.load_workbook(SRC, data_only=True)
wfm = openpyxl.load_workbook(SRC)
GM = {}
for row in wv['Gov_Map'].iter_rows(min_row=5):
    GM[(row[2].value, str(row[3].value))] = dict(cat=row[5].value, lo=row[10].value, hi=row[11].value)
def V(sh, a): return wv[sh][a].value

F = 'Arial'
BLUE = Font(name=F, color='0000FF', size=10); BLACK = Font(name=F, size=10); GREEN = Font(name=F, color='008000', size=10)
BOLD = Font(name=F, bold=True, size=10); HEAD = Font(name=F, bold=True, size=10, color='FFFFFF')
TITLE = Font(name=F, bold=True, size=13); NOTE = Font(name=F, size=9, color='555555')
HFILL = PatternFill('solid', fgColor='305496'); SEC = PatternFill('solid', fgColor='D9E1F2')
YEL = PatternFill('solid', fgColor='FFF2CC'); KEY = PatternFill('solid', fgColor='E2EFDA')
GOOD = PatternFill('solid', fgColor='C6EFCE'); BAD = PatternFill('solid', fgColor='FFC7CE')
WRAP = Alignment(wrap_text=True, vertical='top')
wb = openpyxl.Workbook(); wb.remove(wb.active)
def sheet(name, widths):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, 1): ws.column_dimensions[CL(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws
def hdr(ws, r, labels):
    for i, t in enumerate(labels, 1):
        c = ws.cell(r, i, t); c.font = HEAD; c.fill = HFILL; c.alignment = WRAP
def name(nm, ref): wb.defined_names[nm] = DefinedName(nm, attr_text=ref)
def secrow(ws, r, t, n):
    ws.cell(r, 1, t).font = BOLD
    for i in range(1, n + 1): ws.cell(r, i).fill = SEC

# ------------------------------------------------------------------ 2_輸入（基準／低／高三欄）
I = sheet('2_輸入', [10, 44, 12, 12, 12, 10, 18, 20, 70, 10])
I['A1'] = 'L 與所需 L 的全部輸入（藍字＝可改；三欄＝基準／低端／高端，取自 Tokenomics v17.0 的 Cap_In、Alloc_In、SRC_Demand）'; I['A1'].font = TITLE
I['A2'] = '「低端」「高端」是各輸入自己的區間端點，不一定使 L 變小或變大（例如 g 低端使 L 變小，ρ 低端也使 L 變小）。'; I['A2'].font = NOTE
hdr(I, 4, ['ID', '項目', '基準', '低端', '高端', '單位', '標記（Gov_Map）', '原活頁簿位置', '說明與證據', '不確定度'])
rp = [5]
def inp(nid, label, sh, cells, unit, note, unc, vals=None):
    r = rp[0]; rp[0] += 1
    vs = vals if vals is not None else [V(sh, a) if a else None for a in cells]
    g = GM.get((sh, cells[0]), {})
    row = [nid, label, vs[0], vs[1], vs[2], unit, g.get('cat', '—'), f"{sh}!{'／'.join(a for a in cells if a)}", note, unc]
    for i, x in enumerate(row, 1):
        c = I.cell(r, i, x); c.font = BLACK; c.alignment = WRAP
    for i in (3, 4, 5):
        if I.cell(r, i).value is not None: I.cell(r, i).font = BLUE
    if unc == '高':
        for i in range(1, 11): I.cell(r, i).fill = YEL
    name(nid, f"'2_輸入'!$C${r}"); name(nid + '_Lo', f"'2_輸入'!$D${r}"); name(nid + '_Hi', f"'2_輸入'!$E${r}")
    return r
secrow(I, rp[0], 'A. L 的輸入（壽命期價格係數）', 10); rp[0] += 1
inp('IN_g', '中階 token 牌價年變化率 g', 'Cap_In', ['C226', 'D226', 'E226'], '/年',
    'v15.3 E1：2024-05～2026-10 中階牌價（參考請求混合價）月階梯法、三家合併各自截距回歸 −9.1%／年；分廠商 OpenAI −4.4%、Anthropic −19.4%、Google −2.6%；去除快取折扣引入約 0%；窗口敏感（2024-10 起 +16.8%）。2026-10 三家中階同價 $2／$0.10／$10；Google 已公告 Argon 自 2026-12 漲價一倍', '高')
inp('IN_T1', '降級前服務中階的年數 T1', 'Cap_In', ['C227', 'D227', 'E227'], '年', '前沿訓練約 2.5–3 年；服務收入年限較長（A100 合約到 2029，利害關係方說法）；Nadella「不想一代折舊四五年」偏短', '中')
r_rho = inp('IN_rho', '降級後價值比 ρ（同一張 GPU 降級後的價值 ÷ 降級前）', 'Cap_In', ['C228', 'D228', 'E228'], 'x',
    '兩種讀法：甲（降級服務自家最低層 Luna）＝Luna 單價 ÷ Sol 單價 × Luna 每 GPU 吞吐倍數 ≈ 0.17（低端欄為公式，見下兩列）；乙（市場機會價值，轉租或轉作他用）≈ A100／H100 租金比 0.55–0.67（2026，供給吃緊時量到）。基準 0.5 偏向讀法乙', '高')
inp('IN_T', '壽命 T（IT 折舊年限）', 'Inputs', ['E23', 'E23', 'E23'], '年', '雲端業者 GPU 折舊 5–6 年（MSFT 2–6、GOOGL 6、ORCL 6、CRWV 6、META 5.5、AMZN 部分 6→5）；Burry 主張經濟壽命 2–3 年（放空者）。本欄三格同值（Tokenomics 取基準欄）', '中')
inp('IN_PxL', '　ρ 讀法甲的輸入：Luna 參考單價（2026 快照）', 'Interface', ['C90', None, None], '$/M', 'IF_PriceRef_Luna（Price_Frontier 第 45 列）', '低')
inp('IN_PxS', '　ρ 讀法甲的輸入：Sol 參考單價（2026 快照）', 'Interface', ['C108', None, None], '$/M', 'IF_PriceRef_Sol', '低')
inp('IN_TokL', '　ρ 讀法甲的輸入：GB200 每 GW 年產出 Luna', 'Interface', ['G21', None, None], 'M tok/年', 'IF_TokGW_Luna 第 4 格（GB200 基準）；roofline 推導見 m 推導檢核 5_每GW產出', '中',
    vals=[wv['Interface']['G21'].value, None, None])
inp('IN_TokS', '　ρ 讀法甲的輸入：GB200 每 GW 年產出 Sol', 'Interface', ['G31', None, None], 'M tok/年', 'IF_TokGW_Sol 第 4 格（GB200 基準）', '中', vals=[wv['Interface']['G31'].value, None, None])
I.cell(r_rho, 4, '=IN_PxL/IN_PxS*IN_TokL/IN_TokS').font = BLACK  # 低端＝讀法甲公式（同 Tokenomics Cap_In D228）
inp('IN_WACC', 'WACC（折現版 L 用；與持有成本年金相同）', 'Inputs', ['E28', 'D28', 'F28'], '%', '持有成本以 WACC 計資本回收年金；為使收入與成本口徑一致，另算折現版 L（見 3_L重算、1_總覽 發現二）', '中')
secrow(I, rp[0], 'A2. 世代起點（本簿新增；11_世代起點 用）', 10); rp[0] += 1
_r = inp('IN_t0H', 'Hopper 機隊在 2025 年中時已服務的年數 t0（基準／低端組合／高端組合）', 'Cap_In', ['C305', 'C306', 'C307'], '年', 'Assumed：H100 雲端 2023-03 起供應，OpenAI 的 Hopper 機隊多在 2023 年中至 2024 年建成 → 2025 年中約已服務 1.5–2.5 年', '高')
I.cell(_r, 7, 'Assumed')
_r = inp('IN_t0G', 'GB200 機隊在 2025 年中時已服務的年數 t0（基準／低端組合／高端組合）', 'Cap_In', ['D305', 'D306', 'D307'], '年', 'Assumed：GB200 雲端 2025-02 起供應、2025 年中以後放量 → 0–0.5 年', '中')
I.cell(_r, 7, 'Assumed')
_r = inp('IN_gpre', '2025 年以前的中階牌價年變化率 g_pre（基準／低／高；Tokenomics 低端組合取高 −0.09、高端組合取低 −0.30）', 'Cap_In', ['C304', 'D304', 'E304'], '/年', 'Assumed：基準＝與 g 相同（−9%）；實際 2023–24 中階牌價曾一次性重估（GPT-4 $33 → GPT-4o $2.7，年化約 −55%），但當時量很小，「量固定、只動價格」的假設往回推最不成立，所以只作敏感度', '高')
I.cell(_r, 7, 'Assumed')
secrow(I, rp[0], 'B. 所需 L 的輸入（恆等式讀法：機隊經濟持有成本 ÷ 2025 營收）', 10); rp[0] += 1
inp('IN_Rev', 'OpenAI 2025 營收', 'SRC_Demand', ['C11', 'C11', 'C11'], '$B', 'SRC_DEM_007；查核財報（外流、FT 核實）', '低')
inp('IN_Spend', 'OpenAI 2025 推論支出（服務用戶）', 'SRC_Demand', ['C8', 'D8', 'E8'], '$B', 'SRC_DEM_004；Tokenomics 的所需 L 區間沒有納入本項區間（只納入計價倍數與 κ）', '中')
inp('IN_SB', '計價倍數（推論支出 ÷ 持有成本）', 'Alloc_In', ['C23', 'D23', 'E23'], 'x', 'Microsoft 對 OpenAI 的實際計價未找到；現值由 Oracle 出租毛利與經濟／會計成本比推得', '高')
inp('IN_Kappa', '請求形狀修正 κ', 'Alloc_In', ['C26', 'D26', 'E26'], 'x', '流量形狀修正（每 GPU 秒 token），出現在所需 L 中是否合理，見 1_總覽 發現一', '高')
inp('IN_Hold', '機隊每 GW 年經濟持有成本（世代加權；只用來展示會約掉）', 'Alloc', ['C157', 'D157', 'E157'], '$B/GW·年', '推導見 m 推導檢核 4_持有成本；在所需 L 中約掉', '低')
secrow(I, rp[0], 'C. 字面讀法（對照，不作判讀）的輸入', 10); rp[0] += 1
inp('IN_RevGW', '機隊每 GW 付費營收（2025 單價，基準利用率口徑）', 'Alloc', ['C156', None, None], '$B/GW·年', 'IF_RevGWFleet × 2025 單價 ÷ 2026 單價，世代加權', '低')
inp('IN_Util', '基準利用率 IF_Util', 'Serving', ['C17', None, None], '%', '', '低')
inp('IN_PD', '生產折減', 'Serving', ['C28', None, None], 'x', '', '中')
inp('IN_m', 'm（機隊變現率）', 'Cap_In', ['C119', None, None], 'x', '推導見 m 推導檢核', '中')

# ------------------------------------------------------------------ 3_L重算
def Lexpr(g, T1, rho, T):
    k = f'LN(1+{g})'
    return f'IF(ABS({k})<0.000000000001,({T1}+{rho}*({T}-{T1}))/{T},(((1+{g})^{T1}-1)+{rho}*((1+{g})^{T}-(1+{g})^{T1}))/({T}*{k}))'
def Ldisc(g, T1, rho, T, r):
    a = f'(LN(1+{g})-LN(1+{r}))'; d = f'(-LN(1+{r}))'
    return f'(((EXP({a}*{T1})-1)+{rho}*(EXP({a}*{T})-EXP({a}*{T1})))/{a})/((EXP({d}*{T})-1)/{d})'
Ls = sheet('3_L重算', [7, 46, 64, 14, 14, 14, 18, 14, 14, 14, 12])
Ls['A1'] = 'L（壽命期價格係數）的重算：基準／低端／高端'; Ls['A1'].font = TITLE
Ls['A2'] = 'L＝硬體壽命期內，該 GPU 每年可收的 token 單價相對第 0 年（2025）的平均。前 T1 年服務中階（價格每年 ×(1+g)），之後降級，價值打 ρ 折。連續時間積分的閉式解，與 Tokenomics Cap_In 第 232–234 列相同。'; Ls['A2'].font = NOTE
hdr(Ls, 4, ['列', '項目', '公式（白話）', '基準', '低端欄', '高端欄', '原活頁簿位置', '原基準', '原低端', '原高端', '差異（最大）'])
LR = {}
def lrow(r, key, lab, expl, fn, src=None, fmt='0.0000'):
    LR[key] = r
    Ls.cell(r, 1, key).font = NOTE; Ls.cell(r, 2, lab).font = BLACK; Ls.cell(r, 3, expl).font = NOTE
    for i in (2, 3): Ls.cell(r, i).alignment = WRAP
    for j, suf in enumerate(['', '_Lo', '_Hi']):
        c = Ls.cell(r, 4 + j, '=' + fn(suf)); c.number_format = fmt
    if src:
        sh, row = src
        Ls.cell(r, 7, f'{sh}!C{row}:E{row}').font = NOTE
        for j, col in enumerate('CDE'):
            c = Ls.cell(r, 8 + j, V(sh, f'{col}{row}')); c.font = BLUE; c.number_format = fmt
        Ls.cell(r, 11, f'=MAX(ABS(D{r}-H{r}),ABS(E{r}-I{r}),ABS(F{r}-J{r}))').number_format = '0.0E+00'
secrow(Ls, 5, 'A. 不折現（Tokenomics 現行口徑）', 11)
lrow(6, 'k', 'k＝ln(1＋g)', '連續複利的價格變化率', lambda s: f'LN(1+IN_g{s})')
lrow(7, 'Lp', 'L_price（只有跌價、不降級）', '＝[(1＋g)^T − 1] ÷（T × k）：(1＋g)^t 在 [0, T] 的平均', lambda s: f"IF(ABS(D$6)<1E-12,1,((1+IN_g{s})^IN_T{s}-1)/(IN_T{s}*LN(1+IN_g{s})))".replace('D$6', {'': 'D6', '_Lo': 'E6', '_Hi': 'F6'}[s]), ('Cap_In', 232))
lrow(8, 'Lt', 'L_total（跌價＋降級）', '＝{[(1＋g)^T1 − 1] ＋ ρ ×[(1＋g)^T −(1＋g)^T1]} ÷（T × k）：前 T1 年全價、之後 ρ 倍的平均', lambda s: Lexpr(f'IN_g{s}', f'IN_T1{s}', f'IN_rho{s}', f'IN_T{s}'), ('Cap_In', 233))
lrow(9, 'Ld', 'L_demote（降級造成的折減）', '＝L_total ÷ L_price', lambda s: {'': 'D8/D7', '_Lo': 'E8/E7', '_Hi': 'F8/F7'}[s], ('Cap_In', 234))
for c in 'DEF': Ls[f'{c}8'].font = BOLD
for i in range(1, 12): Ls.cell(8, i).fill = KEY
secrow(Ls, 11, 'B. 折現版（以 WACC 折現收入，與持有成本年金同口徑；本簿新增，Tokenomics 無此列）', 11)
lrow(12, 'Ltd', 'L_total（折現）', '＝∫ 價格(t) × e^(−δt) dt ÷ ∫ e^(−δt) dt，δ＝ln(1＋WACC)。早年價格較高、權重也較大，所以跌價時折現版 L 較高', lambda s: Ldisc(f'IN_g{s}', f'IN_T1{s}', f'IN_rho{s}', f'IN_T{s}', f'IN_WACC{s}'))
lrow(13, 'dd', '折現版 ÷ 不折現版', '', lambda s: {'': 'D12/D8', '_Lo': 'E12/E8', '_Hi': 'F12/F8'}[s])
Ls['B15'] = '註：低端欄＝g −20%、T1 3、ρ 讀法甲（0.17）、WACC 8%；高端欄＝g +5%、T1 5、ρ 0.7、WACC 13%（各輸入自己的端點，同向組合）。'; Ls['B15'].font = NOTE
Ls.freeze_panes = 'D5'

# ------------------------------------------------------------------ 4_逐年路徑
Y = sheet('4_逐年路徑', [8, 14, 16, 16, 12, 16, 14, 16, 60])
Y['A1'] = '逐年路徑：把 L 的積分拆成每一年，讓「平均」看得見（基準輸入；改 2_輸入 會重算）'; Y['A1'].font = TITLE
Y['A2'] = '每年平均價格指數＝(1＋g)^t 在該年內的平均＝[(1＋g)^(t＋1) −(1＋g)^t] ÷ k。降級後乘 ρ。各年加總 ÷ T＝L（T1、T 為整數時與閉式解完全相同）。'; Y['A2'].font = NOTE
hdr(Y, 4, ['年', '年初價格指數', '該年平均價格指數', '是否已降級', '價值係數', '該年價值（相對第 0 年）', '折現因子（年中）', '折現後價值', '說明'])
for t in range(10):
    r = 5 + t
    Y.cell(r, 1, t)
    Y.cell(r, 2, f'=IF(A{r}<IN_T,(1+IN_g)^A{r},"—")')
    Y.cell(r, 3, f'=IF(A{r}<IN_T,IF(ABS(LN(1+IN_g))<1E-12,1,((1+IN_g)^(A{r}+1)-(1+IN_g)^A{r})/LN(1+IN_g)),"—")')
    Y.cell(r, 4, f'=IF(A{r}<IN_T,IF(A{r}>=IN_T1,"是","否"),"—")')
    Y.cell(r, 5, f'=IF(A{r}<IN_T,IF(A{r}>=IN_T1,IN_rho,1),"—")')
    Y.cell(r, 6, f'=IF(A{r}<IN_T,C{r}*E{r},0)')
    Y.cell(r, 7, f'=IF(A{r}<IN_T,1/(1+IN_WACC)^(A{r}+0.5),0)')
    Y.cell(r, 8, f'=F{r}*G{r}')
    for c in range(2, 9): Y.cell(r, c).number_format = '0.0000'
Y['A16'] = '合計'; Y['A16'].font = BOLD
Y['F16'] = '=SUM(F5:F14)'; Y['G16'] = '=SUM(G5:G14)'; Y['H16'] = '=SUM(H5:H14)'
Y['B17'] = 'L（逐年加總 ÷ T）'; Y['F17'] = '=F16/IN_T'; Y['F17'].font = BOLD
Y['B18'] = '對照：閉式解 L_total（3_L重算）'; Y['F18'] = "='3_L重算'!D8"; Y['F18'].font = GREEN
Y['B19'] = '差異'; Y['F19'] = '=F17-F18'
Y['B20'] = '折現版 L（年中折現的離散近似）'; Y['F20'] = '=H16/G16'
Y['B21'] = '對照：折現版閉式解'; Y['F21'] = "='3_L重算'!D12"; Y['F21'].font = GREEN
Y['I17'] = 'T1、T 為整數時兩者相同；非整數時逐年表以年為單位降級，會有小差異。'; Y['I17'].font = NOTE
Y['I20'] = '離散年中折現與連續折現略有差異（約千分之幾）。'; Y['I20'].font = NOTE
for a in ('F17', 'F18', 'F19', 'F20', 'F21'): Y[a].number_format = '0.0000'

# ------------------------------------------------------------------ 5_所需L
Q = sheet('5_所需L', [7, 48, 66, 14, 14, 14, 18, 14, 14, 14, 12])
Q['A1'] = '所需 L：要回本，壽命期平均價格至少要是 2025 年的幾成'; Q['A1'].font = TITLE
Q['A2'] = '回本條件：2025 營收 × L ≥ 機隊年經濟持有成本（服務機隊；訓練與研發不在內）。所以所需 L＝持有成本 ÷ 營收。低端欄＝計價倍數高端 × κ 低端；高端欄＝計價倍數低端 × κ 高端（同 Tokenomics Cap_In 第 289 列）。'; Q['A2'].font = NOTE
hdr(Q, 4, ['列', '項目', '公式（白話）', '基準', '低端欄', '高端欄', '原活頁簿位置', '原基準', '原低端', '原高端', '差異（最大）'])
QR = {}
def qrow(r, key, lab, expl, fb, fl, fh, src=None, fmt='0.0000'):
    QR[key] = r
    Q.cell(r, 1, key).font = NOTE; Q.cell(r, 2, lab).font = BLACK; Q.cell(r, 3, expl).font = NOTE
    for i in (2, 3): Q.cell(r, i).alignment = WRAP
    for j, f in enumerate((fb, fl, fh)):
        c = Q.cell(r, 4 + j, '=' + f); c.number_format = fmt
    if src:
        sh, row, cols = src
        Q.cell(r, 7, f'{sh}!{cols[0]}{row}:{cols[-1]}{row}').font = NOTE
        for j, col in enumerate(cols):
            c = Q.cell(r, 8 + j, V(sh, f'{col}{row}')); c.font = BLUE; c.number_format = fmt
        Q.cell(r, 11, f'=MAX(ABS(D{r}-H{r}),ABS(E{r}-I{r}),ABS(F{r}-J{r}))').number_format = '0.0E+00'
secrow(Q, 5, 'A. 恆等式讀法（判讀用；Tokenomics L1_LReqFleet_Id）', 11)
qrow(6, 'GW', '支出路線服務 GW', '＝推論支出 ÷ 每 GW 年持有成本', 'IN_Spend/IN_Hold', 'IN_Spend/IN_Hold', 'IN_Spend/IN_Hold', ('Alloc', 70, 'CCC'))
qrow(7, 'GWe', '有效服務 GW', '＝服務 GW ÷ 計價倍數 × κ', 'D6/IN_SB*IN_Kappa', 'E6/IN_SB_Hi*IN_Kappa_Lo', 'F6/IN_SB_Lo*IN_Kappa_Hi', ('Cap_In', 109, 'CED'))
qrow(8, 'Hc', '機隊年經濟持有成本', '＝有效服務 GW × 每 GW 年持有成本', 'D7*IN_Hold', 'E7*IN_Hold', 'F7*IN_Hold', None)
qrow(9, 'LR', '所需 L（恆等式讀法）', '＝機隊年經濟持有成本 ÷ 2025 營收', 'D8/IN_Rev', 'E8/IN_Rev', 'F8/IN_Rev', ('Cap_In', 289, 'CDE'))
for c in 'DEF': Q[f'{c}9'].font = BOLD
for i in range(1, 12): Q.cell(9, i).fill = KEY
qrow(10, 'LRc', '同上，約分後的閉式解', '＝推論支出 × κ ÷（計價倍數 × 營收）——每 GW 持有成本在分子分母約掉', 'IN_Spend*IN_Kappa/(IN_SB*IN_Rev)', 'IN_Spend*IN_Kappa_Lo/(IN_SB_Hi*IN_Rev)', 'IN_Spend*IN_Kappa_Hi/(IN_SB_Lo*IN_Rev)')
secrow(Q, 12, 'B. 替代讀法（本簿新增，供判斷；Tokenomics 無此列）', 11)
qrow(13, 'LRnk', '不含 κ（發現一）', '＝推論支出 ÷（計價倍數 × 營收）。κ 是 token 流量形狀的修正，不改變 OpenAI 花多少錢養機隊', 'IN_Spend/(IN_SB*IN_Rev)', 'IN_Spend/(IN_SB_Hi*IN_Rev)', 'IN_Spend/(IN_SB_Lo*IN_Rev)')
qrow(14, 'LRsp', '不含 κ，且納入推論支出區間', '低端＝支出 7.5 ÷ 計價倍數 1.17；高端＝支出 8.8 ÷ 計價倍數 0.73', 'IN_Spend/(IN_SB*IN_Rev)', 'IN_Spend_Lo/(IN_SB_Hi*IN_Rev)', 'IN_Spend_Hi/(IN_SB_Lo*IN_Rev)')
secrow(Q, 16, 'C. 字面讀法（對照，口徑不一致，不作判讀；Tokenomics L1_LReqFleet）', 11)
qrow(17, 'BE', '機隊損益兩平乘積', '＝每 GW 持有成本 ÷（每 GW 付費營收 ÷ IF_Util）', 'IN_Hold/(IN_RevGW/IN_Util)', 'IN_Hold/(IN_RevGW/IN_Util)', 'IN_Hold/(IN_RevGW/IN_Util)', ('Alloc', 158, 'CCC'))
qrow(18, 'LRl', '所需 L（字面讀法）', '＝損益兩平乘積 ÷（IF_Util × 生產折減 × m）。分子是整個機隊，分母只含付費服務營收（約 22%），所以偏高', 'D17/(IN_Util*IN_PD*IN_m)', 'D17/(IN_Util*IN_PD*IN_m)', 'D17/(IN_Util*IN_PD*IN_m)', ('Cap_In', 240, 'CCC'))
Q['B20'] = '註：字面讀法只列基準（三欄同值）；Tokenomics 的 D／E 欄改用 m 的高低端，口徑不同，不在此比較。'; Q['B20'].font = NOTE
Q.freeze_panes = 'D5'

# ------------------------------------------------------------------ 6_回本判讀
B = sheet('6_回本判讀', [6, 30, 13, 13, 13, 13, 13, 13, 4, 50])
B['A1'] = '回本判讀與「必須為真」'; B['A1'].font = TITLE
B['A2'] = '三態判讀：L 區間全在所需 L 區間之下＝未回本；全在之上＝回本；重疊＝未定（同 Tokenomics Cap_In 第 242 列）。下方格點與「必須為真」表沿用 2025＝第 0 年、不折現、含 κ 的舊口徑（閉式解較簡單，用來看 g、ρ、T1 的方向）；主口徑判讀以第 4–6 列為準。綠＝L ≥ 所需 L（基準），紅＝L < 所需 L。'; B['A2'].font = NOTE
L3 = "'3_L重算'"; Q5 = "'5_所需L'"
B['B4'] = 'L（v17.0 主口徑：世代起點＋折現；基準、低、高）'; B['C4'] = "='11_世代起點'!D33"; B['D4'] = "='11_世代起點'!E33"; B['E4'] = "='11_世代起點'!F33"
B['B5'] = '所需 L（v17.0 主口徑：不含 κ；基準、低、高）'; B['C5'] = "='11_世代起點'!D34"; B['D5'] = "='11_世代起點'!E34"; B['E5'] = "='11_世代起點'!F34"
B['B6'] = '判讀（v17.0 主口徑）'
B['C6'] = '=IF(MAX(D4,E4)<MIN(D5,E5),"未回本",IF(MIN(D4,E4)>MAX(D5,E5),"回本","未定（區間重疊）"))'
B['B7'] = '對照：判讀（2025＝第 0 年折現版 L 對 不含 κ 所需 L）'
B['C7'] = f'=IF(MAX({L3}!E12,{L3}!F12)<MIN({Q5}!E14,{Q5}!F14),"未回本",IF(MIN({L3}!E12,{L3}!F12)>MAX({Q5}!E14,{Q5}!F14),"回本","未定（區間重疊）"))'
B['B8'] = '基準差距：L ÷ 所需 L（v17.0 主口徑）'; B['C8'] = '=C4/C5'
B['B9'] = '對照：2025＝第 0 年折現版 L ÷ 不含 κ 所需 L'; B['C9'] = f'={L3}!D12/{Q5}!D13'
B['B10'] = '對照：Tokenomics Cap_In!C242'; B['C10'] = V('Cap_In', 'C242'); B['C10'].font = BLUE
for a in ('C4', 'D4', 'E4', 'C5', 'D5', 'E5', 'C8', 'C9'): B[a].number_format = '0.000'
for a in ('C4', 'D4', 'E4', 'C5', 'D5', 'E5'): B[a].font = GREEN
B['C6'].font = BOLD; B['C7'].font = BOLD
# 格點：g × ρ（T1 可選）
B['B12'] = '格點一：L（不折現）對 g × ρ；T1＝'; B['B12'].font = BOLD
B['C12'] = 4; B['C12'].font = BLUE; B['D12'] = '（可改）'; B['D12'].font = NOTE
B['B13'] = 'g ＼ ρ'
rhos = [0.17, 0.3, 0.5, 0.67, 0.7, 1.0]; gs = [-0.20, -0.15, -0.12, -0.10, -0.09, -0.07, -0.05, -0.037, -0.02, 0.0, 0.02, 0.05]
for j, rho in enumerate(rhos):
    c = B.cell(13, 3 + j, rho); c.font = BLUE; c.number_format = '0.00'
for i, g in enumerate(gs):
    r = 14 + i
    c = B.cell(r, 2, g); c.font = BLUE; c.number_format = '0.0%'
    for j in range(len(rhos)):
        col = CL(3 + j)
        f = Lexpr(f'$B{r}', '$C$12', f'{col}$13', 'IN_T')
        cc = B.cell(r, 3 + j, '=' + f.replace('IF(ABS(LN(1+$B' + str(r) + '))<0.000000000001', 'IF(ABS(LN(1+$B' + str(r) + '))<0.000000000001'))
        cc.number_format = '0.000'
g1_end = 14 + len(gs) - 1
B.conditional_formatting.add(f'C14:{CL(2+len(rhos))}{g1_end}', CellIsRule(operator='greaterThanOrEqual', formula=['$C$5'], fill=GOOD))
B.conditional_formatting.add(f'C14:{CL(2+len(rhos))}{g1_end}', CellIsRule(operator='lessThan', formula=['$C$5'], fill=BAD))
r0 = g1_end + 2
B.cell(r0, 2, '格點二：折現版 L 對 g × ρ（同 T1；對照不含 κ 的所需 L）').font = BOLD
B.cell(r0, 10, '綠／紅以「不含 κ 的所需 L 基準」為門檻').font = NOTE
B.cell(r0 + 1, 2, 'g ＼ ρ')
for j, rho in enumerate(rhos):
    c = B.cell(r0 + 1, 3 + j, rho); c.font = BLUE; c.number_format = '0.00'
for i, g in enumerate(gs):
    r = r0 + 2 + i
    c = B.cell(r, 2, g); c.font = BLUE; c.number_format = '0.0%'
    for j in range(len(rhos)):
        col = CL(3 + j)
        cc = B.cell(r, 3 + j, '=' + Ldisc(f'$B{r}', '$C$12', f'{col}${r0+1}', 'IN_T', 'IN_WACC')); cc.number_format = '0.000'
g2_end = r0 + 2 + len(gs) - 1
B.cell(r0, 9, '門檻').font = NOTE
B.cell(r0 + 1, 9, f"={Q5}!D13").number_format = '0.000'
thr2 = f'$I${r0+1}'
B.conditional_formatting.add(f'C{r0+2}:{CL(2+len(rhos))}{g2_end}', CellIsRule(operator='greaterThanOrEqual', formula=[thr2], fill=GOOD))
B.conditional_formatting.add(f'C{r0+2}:{CL(2+len(rhos))}{g2_end}', CellIsRule(operator='lessThan', formula=[thr2], fill=BAD))
# 必須為真：回本所需 g（Python 二分法計算，數值）
def Lund(g, T1, rho, T=6):
    k = math.log(1 + g)
    return (T1 + rho * (T - T1)) / T if abs(k) < 1e-12 else (((1 + g) ** T1 - 1) + rho * ((1 + g) ** T - (1 + g) ** T1)) / (T * k)
def Ldis(g, T1, rho, T=6, r=0.10):
    a = math.log(1 + g) - math.log(1 + r); d = -math.log(1 + r)
    if abs(a) < 1e-12: a = 1e-12
    return (((math.exp(a * T1) - 1) + rho * (math.exp(a * T) - math.exp(a * T1))) / a) / ((math.exp(d * T) - 1) / d)
def gneed(fn, T1, rho, target):
    lo, hi = -0.9, 0.9
    for _ in range(200):
        mid = (lo + hi) / 2
        if fn(mid, T1, rho) < target: lo = mid
        else: hi = mid
    return mid
LREQ = V('Cap_In', 'C289'); LREQNK = 8.4 / (0.85 * 13.07)
r3 = g2_end + 2
B.cell(r3, 2, '必須為真：回本所需的最低 g（Python 二分法計算，數值；改輸入不會自動更新）').font = BOLD
B.cell(r3 + 1, 2, 'T1 ＼ ρ');
for j, rho in enumerate(rhos):
    c = B.cell(r3 + 1, 3 + j, rho); c.font = BLUE; c.number_format = '0.00'
for i, T1 in enumerate([3, 4, 5]):
    r = r3 + 2 + i
    B.cell(r, 2, f'T1＝{T1}（不折現，所需 L {LREQ:.3f}）')
    for j, rho in enumerate(rhos):
        c = B.cell(r, 3 + j, gneed(Lund, T1, rho, LREQ)); c.font = BLUE; c.number_format = '0.0%'
for i, T1 in enumerate([3, 4, 5]):
    r = r3 + 5 + i
    B.cell(r, 2, f'T1＝{T1}（折現、不含 κ，所需 L {LREQNK:.3f}）')
    for j, rho in enumerate(rhos):
        c = B.cell(r, 3 + j, gneed(Ldis, T1, rho, LREQNK)); c.font = BLUE; c.number_format = '0.0%'
B.cell(r3 + 9, 2, '讀法：表中為「回本所需 g 的下限」；實際 g 高於此值即回本。證據：2024-05～2026-10 三家合併 −9.1%／年（窗口 −20%～+17%）。').font = NOTE
B.freeze_panes = 'C14'

# ------------------------------------------------------------------ 7_敏感度（公式）
S = sheet('7_敏感度', [6, 30, 12, 12, 12, 13, 13, 13, 13, 10, 44])
S['A1'] = '敏感度：每次只把一個輸入改到它的低端或高端，看 L、所需 L 與兩者的比（全部為公式）'; S['A1'].font = TITLE
S['A2'] = 'L ÷ 所需 L ≥ 1 即回本（Tokenomics 口徑：不折現、含 κ）。擺動＝|比值（高）− 比值（低）| ÷ 比值（基準）。'; S['A2'].font = NOTE
hdr(S, 4, ['#', '輸入', '基準', '低端', '高端', 'L ÷ 所需 L（低端）', 'L ÷ 所需 L（高端）', '翻轉？（低）', '翻轉？（高）', '擺動', '說明'])
base_L = Lexpr('IN_g', 'IN_T1', 'IN_rho', 'IN_T'); base_R = 'IN_Spend*IN_Kappa/(IN_SB*IN_Rev)'
def ratio(over):
    g = over.get('g', 'IN_g'); t1 = over.get('T1', 'IN_T1'); rho = over.get('rho', 'IN_rho'); T = over.get('T', 'IN_T')
    sp = over.get('Spend', 'IN_Spend'); k = over.get('Kappa', 'IN_Kappa'); sb = over.get('SB', 'IN_SB')
    return f'({Lexpr(g, t1, rho, T)})/({sp}*{k}/({sb}*IN_Rev))'
items = [('g', '中階牌價年變化率 g', 'IN_g', '高', '最承重；窗口敏感'), ('rho', '降級後價值比 ρ', 'IN_rho', '高', '低端＝讀法甲 0.17'),
         ('T1', '降級前服務中階年數 T1', 'IN_T1', '中', ''), ('SB', '計價倍數', 'IN_SB', '高', '所需 L 的分母'),
         ('Kappa', 'κ（所需 L 中是否應出現，見發現一）', 'IN_Kappa', '高', ''), ('Spend', '推論支出', 'IN_Spend', '中', 'Tokenomics 區間未納入此項')]
S['B5'] = '基準'; S['F5'] = '=' + ratio({}); S['F5'].number_format = '0.000'; S['B5'].font = BOLD
for i, (k_, lab, nm, unc, note) in enumerate(items):
    r = 6 + i
    S.cell(r, 1, i + 1); S.cell(r, 2, lab)
    for j, suf in enumerate(['', '_Lo', '_Hi']):
        c = S.cell(r, 3 + j, f'={nm}{suf}'); c.font = GREEN; c.number_format = '0.000'
    c = S.cell(r, 6, '=' + ratio({k_: nm + '_Lo'})); c.number_format = '0.000'
    c = S.cell(r, 7, '=' + ratio({k_: nm + '_Hi'})); c.number_format = '0.000'
    S.cell(r, 8, f'=IF((F{r}>=1)<>($F$5>=1),"翻轉","—")'); S.cell(r, 9, f'=IF((G{r}>=1)<>($F$5>=1),"翻轉","—")')
    c = S.cell(r, 10, f'=ABS(G{r}-F{r})/$F$5'); c.number_format = '0%'
    S.cell(r, 11, note).font = NOTE
r = 6 + len(items)
S.cell(r, 1, len(items) + 1); S.cell(r, 2, '壽命 T（4 年，Inputs 高成本欄）')
S.cell(r, 3, '=IN_T').font = GREEN; S.cell(r, 4, 4).font = BLUE; S.cell(r, 5, '=IN_T').font = GREEN
S.cell(r, 6, '=' + ratio({'T': '4'})).number_format = '0.000'; S.cell(r, 7, '=' + ratio({})).number_format = '0.000'
S.cell(r, 8, f'=IF((F{r}>=1)<>($F$5>=1),"翻轉","—")'); S.cell(r, 9, '—'); S.cell(r, 10, f'=ABS(G{r}-F{r})/$F$5').number_format = '0%'
S.cell(r, 11, 'T 縮短時，降級後的低價年數減少，L 反而上升；但持有成本（資本回收年金）同時上升，本表只動 L 側').font = NOTE
S.freeze_panes = 'C5'

# ------------------------------------------------------------------ 8／9 不確定清單
U = sheet('8_不確定_搜尋', [6, 24, 20, 9, 42, 46, 42, 40, 22, 12])
U['A1'] = '最不確定、可以「搜尋」解決的假設（L 與所需 L）'; U['A1'].font = TITLE
U['A2'] = '分工：C＝chat 端可在公開網路找到；A線上＝付費或需登入的來源；J＝Andy 判斷（不需蒐集）。擺動連結 7_敏感度。'; U['A2'].font = NOTE
hdr(U, 4, ['優先', '假設', '現值（區間）', '擺動', '為什麼不確定', '要找的證據', '可能來源與管道', '本串已做過的搜尋', '找到後要改的格', '分工'])
SROW = {k_: 6 + i for i, (k_, *_rest) in enumerate(items)}
u8 = [
 (1, '中階牌價年變化率 g', '−9%（−20%～+5%）', 'g', '回歸結果對取樣窗口極敏感（−31% 到 +17%）；2024 年後的降幅多來自一次性事件（快取折扣引入、個別新世代降價）；2026 年首次出現漲價公告', '持續追蹤中階牌價（OpenAI Sol、Anthropic Sonnet、Google Pro／Argon）的調價；Google 2026-12 漲價是否落地、另兩家是否跟進；同價但模型變大的世代更替頻率', '官方定價頁與公告；Artificial Analysis 價格序列；Simon Willison 牌價紀錄；Epoch AI', 'L 證據 A 段：三家 2023–2026 牌價序列、Epoch／a16z（固定能力價格，不可代入）', 'Cap_In C226:E226', 'C（每月追蹤）'),
 (4, 'ρ 的讀法（甲 0.17／乙約 0.6）', '0.5（0.17～0.7）', 'rho', '實驗室把舊 GPU 用在哪裡決定 ρ：只服務自家最低層（甲）或轉租、轉給研發與其他客戶（乙）；兩者差 3～4 倍；但 ρ 只影響降級後的最後 T − T1 年，對「L ÷ 所需 L」的擺動約 17%，小於 g、κ、計價倍數', 'OpenAI／Microsoft／Meta／Google 對舊世代 GPU（A100、H100）用途的說法；二手 GPU 與兩代前 GPU 的租金對新世代的比', 'Microsoft、Meta 法說會；CoreWeave 10-K（續約價）；二手市場報價（Silicon Data、Ornn 指數）', 'A100／H100 租金比 0.55～0.67（2026）；CoreWeave H100 續約約原價 95%（管理層說法）', 'Cap_In C228:E228', 'C＋J'),
 (3, '計價倍數', '0.85（0.73～1.17）', 'SB', '所需 L 的分母；Microsoft 對 OpenAI 的實際計價未公開', 'Microsoft 對 OpenAI 的 GPU 時價或折扣；Azure AI 毛利；OpenAI–Oracle／CoreWeave 合約每 GW 年單價', 'The Information、FT（付費）；Microsoft 10-K；Oracle RPO', '只找到 Zitron 文件與 The Register 轉述', 'Alloc_In C23:E23', 'A線上'),
 (2, '所需 L 是否應含 κ（結構）', 'κ 1.0（0.65～1.2）', 'Kappa', 'κ 是 token 流量形狀的修正；放在成本側使所需 L 區間擴大近一倍（0.357～1.056 → 不含 κ 0.549～0.880）', '不需搜尋：模型結構判斷', '—', '本簿 5_所需L 第 13–14 列已並列', 'Cap_In C289 公式', 'J'),
 (5, '壽命 T（經濟壽命對會計壽命）', '6 年', None, '會計折舊 5～6 年；放空方主張經濟壽命 2～3 年；同時影響 L 與持有成本', '各世代 GPU 實際退役或轉用的時間；雲端業者折舊年限變更', '六家 10-K；Burry 等反方分析（利害關係方）', '折舊年限 6 家已查（2026 無新變更）', 'Inputs E23（同時影響持有成本）', 'C'),
 (6, '推論支出', '8.4（7.5～8.8）$B', 'Spend', '所需 L 的分子；Tokenomics 的所需 L 區間未納入', '營收分成記帳位置；營業成本組成', '招股文件（若 IPO）；FT／The Information', '查核財報分項已取得', 'SRC_Demand C8', 'A線上'),
]
u8.sort(key=lambda x: x[0])
for i, it in enumerate(u8):
    r = 5 + i
    pr_, nm, cur, key, why, ev, srcs, done, cell, who = it
    sw = f"='7_敏感度'!J{SROW[key]}" if key else "='7_敏感度'!J" + str(6 + len(items))
    vals = [pr_, nm, cur, sw, why, ev, srcs, done, cell, who]
    for j, v in enumerate(vals, 1):
        c = U.cell(r, j, v); c.font = BLACK; c.alignment = WRAP
    U.cell(r, 4).number_format = '0%'
    if pr_ <= 3:
        for j in range(1, 11): U.cell(r, j).fill = YEL
W = sheet('9_不確定_實地調研', [6, 24, 20, 9, 42, 50, 44, 22, 12])
W['A1'] = '最不確定、需要「實地調研」的假設（訪談、供應鏈或二手市場查核）'; W['A1'].font = TITLE
W['A2'] = 'A線下＝Andy 線下調研。資料放 Drive 02-算力收支/Tokenomics/inbox/。'; W['A2'].font = NOTE
hdr(W, 4, ['優先', '假設', '現值（區間）', '擺動', '為什麼不確定', '要問的問題（可直接用於訪談）', '訪談或查核對象', '找到後要改的格', '分工'])
u9 = [
 (1, 'ρ：舊世代 GPU 的實際去處與價值', '0.5（0.17～0.7）', 'rho', '公開資料只有租金比，看不到實驗室內部如何安排舊 GPU', '新世代（GB200／GB300）上線後，H100 叢集多半拿去做什麼：降級服務小模型、給研發與評測、轉租第三方，或退役？轉租時相對原價打幾折？', '雲端與 neocloud 營運人員；GPU 經紀商與二手交易商；實驗室基礎設施人員', 'Cap_In C228:E228', 'A線下'),
 (2, 'T1：一個世代在中階服務幾年', '4（3～5）', 'T1', '前沿訓練 2.5～3 年有公開說法，但服務中階模型的年數沒有', '一個 GPU 世代從上線到不再承載主力（中階）模型，通常幾年？A100 現在還在服務哪一層模型？', '推論平台工程師；雲端產品經理', 'Cap_In C227:E227', 'A線下'),
 (3, '二手與續約價格（ρ、L 的市場對照）', '—', None, '二手 H100／A100 成交價與 2～3 年期續約價沒有公開序列', '二手 H100（HGX 8 卡）的成交價走勢？2023 年簽的 H100 合約到期續約時，價格相對原約幾成？', 'GPU 經紀商；伺服器二手商；neocloud 業務', 'Cap_In C228、C226（交叉檢查）', 'A線下'),
]
for i, it in enumerate(u9):
    r = 5 + i
    pr_, nm, cur, key, why, q, who_, cell, who = it
    sw = f"='7_敏感度'!J{SROW[key]}" if key else '—'
    vals = [pr_, nm, cur, sw, why, q, who_, cell, who]
    for j, v in enumerate(vals, 1):
        c = W.cell(r, j, v); c.font = BLACK; c.alignment = WRAP
    W.cell(r, 4).number_format = '0%'
    if pr_ <= 1:
        for j in range(1, 10): W.cell(r, j).fill = YEL

# ------------------------------------------------------------------ 10_前置格清單
exec(open('trace.py').read().split("start=('Cap_In','C119')")[0].replace("f='v153.xlsx'", "f='v170.xlsx'"))
seen = {}; order = []
stack = [(('Cap_In', a), 0) for a in ('C242', 'C233', 'C289', 'C240')]
while stack:
    (sh, addr), d = stack.pop()
    if (sh, addr) in seen: continue
    seen[(sh, addr)] = d; order.append((sh, addr))
    if ':' in addr: continue
    pre, _ = precedents(sh, addr)
    for p_ in pre:
        if p_[0] == 'Cap_In' and p_[1] in ('C119', 'D119', 'E119'):   # m 的前置格另見 m 推導檢核
            seen.setdefault(p_, d + 1); order.append(p_); continue
        stack.append((p_, d + 1))
Pq = sheet('10_前置格清單', [14, 9, 6, 50, 16, 80, 10, 14])
Pq['A1'] = 'L、所需 L 與回本判讀的前置格（從 Cap_In C242、C233、C289、C240 遞迴展開；m 的前置格見 m 推導檢核 9_前置格清單）'; Pq['A1'].font = TITLE
hdr(Pq, 3, ['工作表', '格', '深度', '列標籤', '值', '公式（原文）', '類型', 'Gov_Map 類別'])
def lab(sh, a):
    rown = re.sub(r'[A-Z]+', '', a.split(':')[0])
    for c in ('A', 'B'):
        t = wv[sh][f'{c}{rown}'].value
        if isinstance(t, str) and t.strip(): return t.replace('\n', ' ')[:120]
    return ''
rr = 4
for (sh, a) in sorted(set(order), key=lambda x: (seen[x], x[0], x[1])):
    if ':' in a: vals = [sh, a, seen[(sh, a)], '（範圍）', '', '', '範圍', '']
    else:
        v = wv[sh][a].value; fo = wfm[sh][a].value; isf = isinstance(fo, str) and fo.startswith('=')
        vals = [sh, a, seen[(sh, a)], lab(sh, a), v if not isinstance(v, str) else v[:60], ('＝' + fo[1:300]) if isf else '', '公式' if isf else '常數（輸入）', GM.get((sh, a), {}).get('cat', '')]
    for j, v in enumerate(vals, 1): Pq.cell(rr, j, v).font = BLUE if vals[6] == '常數（輸入）' else BLACK
    rr += 1
NPRE = rr - 4
Pq['A2'] = f'共 {NPRE} 格。「深度」＝距判讀格的步數。公式前的「＝」為文字顯示。'; Pq['A2'].font = NOTE
Pq.auto_filter.ref = f'A3:H{rr-1}'; Pq.freeze_panes = 'A4'

# ------------------------------------------------------------------ 1_總覽
O = sheet('1_總覽', [4, 50, 16, 16, 16, 60])
O['B1'] = 'L（壽命期價格係數）與回本判讀總覽'; O['B1'].font = Font(name=F, bold=True, size=15)
O['B2'] = 'Tokenomics v17.0（master 5ef0f7e，2026-10-20）。v17.0 回本判讀主口徑＝世代起點＋折現的機隊 L 對 不含 κ 的所需 L（F1、F2、G1 已採用）。本頁數字全部連結到 3、5、6 頁，改 2_輸入 會一起變。'; O['B2'].font = NOTE
O['B4'] = '一句話'; O['B4'].font = BOLD
O['B5'] = '回本條件：2025 營收 × L ≥ 服務機隊的年經濟持有成本。L＝每個世代硬體在自己壽命期內 token 單價相對該世代起點的平均（跌價＋降級；2025 只是校準錨點；v17.0 起用折現平均，與持有成本年金同口徑）；所需 L＝持有成本 ÷ 營收。L 由中階牌價年變化率 g、降級前年數 T1、降級後價值比 ρ、壽命 T 決定；所需 L 約分後只剩推論支出、計價倍數與營收（v17.0 起不含 κ）。'
O['B5'].alignment = WRAP; O.merge_cells('B5:F5'); O.row_dimensions[5].height = 58
hdr(O, 7, ['', '項目', '基準', '低端欄', '高端欄', '說明'])
rows = [('L（世代起點＋折現；v17.0 主口徑 L1_LTotalFleetVDisc）', "='11_世代起點'!D33", "='11_世代起點'!E33", "='11_世代起點'!F33", '11_世代起點 第 33 列'),
        ('所需 L（不含 κ；v17.0 主口徑 L1_LReqFleet_IdNoK）', "='11_世代起點'!D34", "='11_世代起點'!E34", "='11_世代起點'!F34", '＝推論支出 ÷（計價倍數 × 營收）'),
        ('判讀（v17.0 主口徑，三態）', "='11_世代起點'!D37", '', '', '區間重疊＝未定；Tokenomics Cap_In C242 同'),
        ('主口徑 L ÷ 所需 L（基準）', "='11_世代起點'!D35", '', '', '≥ 1＝基準下回本；1.003 貼近邊界'),
        ('對照：L（2025＝第 0 年，不折現；L1_LTotal）', f'={L3}!D8', f'={L3}!E8', f'={L3}!F8', 'v15.3 口徑'),
        ('對照：L（世代起點，不折現；L1_LTotalFleetV）', "='11_世代起點'!D30", "='11_世代起點'!E30", "='11_世代起點'!F30", 'v16.0 口徑'),
        ('對照：L（2025＝第 0 年，折現；L1_LTotalDisc）', f'={L3}!D12', f'={L3}!E12', f'={L3}!F12', ''),
        ('對照：所需 L（含 κ；L1_LReqFleet_Id）', f'={Q5}!D9', f'={Q5}!E9', f'={Q5}!F9', 'v17.0 起非主口徑（F1）')]
for i, (lab_, b, l, h, note) in enumerate(rows):
    r = 8 + i
    O.cell(r, 2, lab_).font = BOLD if i < 4 else BLACK
    for j, f in enumerate((b, l, h)):
        if f:
            c = O.cell(r, 3 + j, f); c.font = GREEN; c.number_format = '0.000'
    O.cell(r, 6, note).font = NOTE
for i in range(2, 7): O.cell(10, i).fill = KEY
r = 17
O.cell(r, 2, '公式').font = BOLD; r += 1
fl = [('L（壽命期價格係數）', 'L ＝ { [(1＋g)^T1 − 1] ＋ ρ ×[(1＋g)^T −(1＋g)^T1] } ÷（T × ln(1＋g)）', f"={L3}!D8"),
      ('　其中 L_price（不降級）', 'L_price ＝ [(1＋g)^T − 1] ÷（T × ln(1＋g)）', f"={L3}!D7"),
      ('所需 L（恆等式讀法）', '所需 L ＝ 推論支出 × κ ÷（計價倍數 × 營收）（每 GW 持有成本約掉）', f"={Q5}!D10"),
      ('回本條件', '營收 × L ≥ 推論支出 × κ ÷ 計價倍數　⇔　L × 營收 × 計價倍數 ÷（推論支出 × κ）≥ 1', f"={L3}!D8*IN_Rev*IN_SB/(IN_Spend*IN_Kappa)"),
      ('L（折現版；發現二，v17.0 起採用）', 'L_disc ＝ ∫₀^T 價格(t) e^(−δt) dt ÷ ∫₀^T e^(−δt) dt，δ＝ln(1＋WACC)', f"={L3}!D12"),
      ('L（世代起點；發現三，v16.0 起採用）', 'L_v ＝ { [1 −(1＋g_pre)^(−t0)] ÷ ln(1＋g_pre) ＋ [(1＋g)^(T1−t0) − 1 ＋ ρ((1＋g)^(T−t0) −(1＋g)^(T1−t0))] ÷ ln(1＋g) } ÷ T；機隊＝2025 營收加權', "='11_世代起點'!F8")]
for lab_, txt, f in fl:
    O.cell(r, 2, lab_).font = BLACK
    O.cell(r, 3, f).font = GREEN; O.cell(r, 3).number_format = '0.0000'
    O.cell(r, 4, txt).font = NOTE; O.merge_cells(start_row=r, start_column=4, end_row=r, end_column=6); O.cell(r, 4).alignment = WRAP
    O.row_dimensions[r].height = 30; r += 1
O.cell(r, 2, '符號：g＝中階牌價年變化率；T1＝降級前服務中階的年數；ρ＝降級後價值比；T＝壽命；κ＝請求形狀修正；t0＝世代在 2025 年中已服務的年數；g_pre＝2025 年以前的牌價變化率。').font = NOTE
O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); r += 2
O.cell(r, 2, '發現三：為什麼用 2025 年當第 0 年？（已採用：Andy 2026-10-18 定義 L 按世代起點，v16.0）').font = BOLD; r += 1
t3 = ('因為能觀察到的整年營收（130.7 億）與推論支出（84 億）都是 2025 年，模型就把 2025 當成整個機隊的第 0 年——隱含假設「2025 年機隊全新」。'
      '但占服務 GW 60% 的 Hopper 在 2025 年已服務約 2 年，之前單價較高；用各世代自己的起點算、以 2025 營收加權（GB200 占約 77%），機隊 L 由 0.660 升到約 0.716（敏感度 0.68–0.75），L ÷ 所需 L 由 0.87 升到約 0.95（0.90–0.99）（11_世代起點）。'
      'v16.0 已實作；世代起點 t0 仍為 Assumed，需查各世代上線時程。三項合起來（v17.0 主口徑）：L 0.759 對所需 L 0.756，比值 1.003，判讀「未定」。')
O.cell(r, 2, t3).alignment = WRAP; O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); O.row_dimensions[r].height = 80; r += 2
O.cell(r, 2, '發現一：所需 L 中的 κ（已採用：F1 未回應依預設，v17.0 拿掉 κ；可撤回）').font = BOLD; r += 1
t1 = ('所需 L＝有效服務 GW × 每 GW 持有成本 ÷ 營收，而有效服務 GW 含 κ（請求形狀修正）。約分後所需 L＝推論支出 × κ ÷（計價倍數 × 營收），每 GW 持有成本完全約掉。'
      'κ 調整的是「每 GPU 秒產出多少 token」，不改變 OpenAI 花多少錢養機隊，所以放在成本側看起來不對。目前所需 L 的區間 0.357～1.056 有一大半是 κ（0.65～1.2）撐開的；拿掉 κ 後為 0.549～0.880（納入支出區間為 0.490～0.922）。'
      '建議預設：下一版改為不含 κ（判斷類，屬公式邏輯）。')
O.cell(r, 2, t1).alignment = WRAP; O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); O.row_dimensions[r].height = 80; r += 2
O.cell(r, 2, '發現二：L 不折現，但持有成本有折現（已採用：F2 未回應依預設，v17.0 以折現版為主；可撤回）').font = BOLD; r += 1
t2 = ('持有成本用 WACC 10% 的資本回收年金計，等於把未來成本折現；L 卻是不折現的平均。價格逐年下跌時，早年收入較多、較有價值，所以同口徑（折現）的 L 較高：基準 0.660 → 0.699。'
      '建議預設：下一版並列折現版 L，判讀以折現版為主（判斷類）。')
O.cell(r, 2, t2).alignment = WRAP; O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); O.row_dimensions[r].height = 50; r += 2
O.cell(r, 2, '範圍提醒：本判讀只問「服務機隊能否靠營收回收自己的持有成本」，不含訓練與研發支出（全公司口徑另計）；營收按 2025 年固定量、只讓價格走 L 的路徑。').font = NOTE
O.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6); r += 2
O.cell(r, 2, '驗證').font = BOLD; r += 1
for lab_, f in [('3_L重算 對原值的最大差異', f"=MAX({L3}!K7,{L3}!K8,{L3}!K9)"), ('5_所需L 對原值的最大差異', f"=MAX({Q5}!K6,{Q5}!K7,{Q5}!K9,{Q5}!K17,{Q5}!K18)"),
                ('4_逐年路徑 逐年加總 對 閉式解', "='4_逐年路徑'!F19"), ('5_所需L 約分前後差異', f"=MAX(ABS({Q5}!D9-{Q5}!D10),ABS({Q5}!E9-{Q5}!E10),ABS({Q5}!F9-{Q5}!F10))")]:
    O.cell(r, 2, lab_); c = O.cell(r, 3, f); c.number_format = '0.0E+00'; r += 1
r += 1
O.cell(r, 2, '最不確定的輸入（依 7_敏感度 擺動；細節見 8、9 頁）').font = BOLD; r += 1
hdr(O, r, ['', '輸入', 'L÷所需L（低端）', 'L÷所需L（高端）', '擺動', '去哪裡解決']); r += 1
for k_, where in [('Kappa', '發現一（結構判斷）；8 頁第 2 項'), ('g', '8 頁第 1 項（每月追蹤）'), ('SB', '8 頁第 3 項'), ('T1', '9 頁第 2 項'), ('rho', '8 頁第 4 項＋9 頁第 1 項'), ('Spend', '8 頁第 6 項')]:
    sr = SROW[k_]
    O.cell(r, 2, f"='7_敏感度'!B{sr}")
    for j, col in enumerate('FGJ'):
        c = O.cell(r, 3 + j, f"='7_敏感度'!{col}{sr}"); c.number_format = '0%' if col == 'J' else '0.000'
    O.cell(r, 6, where).font = NOTE; r += 1


# ------------------------------------------------------------------ 11_世代起點
VG = sheet('11_世代起點', [6, 46, 66, 14, 14, 14, 40])
VG['A1'] = '世代起點：每個世代用「自己的第 0 年」算 L，而不是把 2025 當成整個機隊的第 0 年（本簿新增）'; VG['A1'].font = TITLE
VG['A2'] = 'Tokenomics 把 2025 年營收當第 0 年，等於假設 2025 年機隊全新。Hopper 在 2025 年已服務約 2 年，之前的單價較高，用 2025 當起點會低估它一生的收入。下面把每個世代的一生收入換算成「相對 2025 年」的平均，再以 2025 營收加權。'; VG['A2'].font = NOTE
hdr(VG, 4, ['列', '項目', '公式（白話）', 'Hopper', 'GB200', '機隊（營收加權）', '說明'])
def vrow(r, key, lab, expl, fh, fg, ff='', fmt='0.0000', note=''):
    VG.cell(r, 1, key).font = NOTE; VG.cell(r, 2, lab); VG.cell(r, 3, expl).font = NOTE
    for i in (2, 3): VG.cell(r, i).alignment = WRAP
    for j, f in enumerate((fh, fg, ff)):
        if f:
            c = VG.cell(r, 4 + j, '=' + f); c.number_format = fmt
    VG.cell(r, 7, note).font = NOTE; VG.cell(r, 7).alignment = WRAP
vrow(5, 't0', '2025 年中時已服務的年數 t0', '輸入', 'IN_t0H', 'IN_t0G')
vrow(6, 'past', '過去段：∫₀^t0 價格(t) ÷ 價格(t0) dt', '＝[1 −(1＋g_pre)^(−t0)] ÷ ln(1＋g_pre)；2025 年以前每年價格較高', 'IF(D5>0,(1-(1+IN_gpre)^(-D5))/LN(1+IN_gpre),0)', 'IF(E5>0,(1-(1+IN_gpre)^(-E5))/LN(1+IN_gpre),0)')
vrow(7, 'fut', '未來段：∫_t0^T 價格(t) ÷ 價格(t0) dt（含降級）', '＝{[(1＋g)^(T1−t0) − 1] ＋ ρ ×[(1＋g)^(T−t0) −(1＋g)^(T1−t0)]} ÷ ln(1＋g)（假設 t0 ≤ T1）', '(((1+IN_g)^(IN_T1-D5)-1)+IN_rho*((1+IN_g)^(IN_T-D5)-(1+IN_g)^(IN_T1-D5)))/LN(1+IN_g)', '(((1+IN_g)^(IN_T1-E5)-1)+IN_rho*((1+IN_g)^(IN_T-E5)-(1+IN_g)^(IN_T1-E5)))/LN(1+IN_g)')
vrow(8, 'Lv', 'L（相對 2025 年；世代起點）', '＝（過去段 ＋ 未來段）÷ T', '(D6+D7)/IN_T', '(E6+E7)/IN_T', '(D9*D8+E9*E8)/(D9+E9)', note='t0＝0 時與 Tokenomics 的 L 相同')
vrow(9, 'w', '權重：該世代的 2025 營收（每 GW 付費營收 × GW 占比）', '回本條件是 Σ 世代營收 × 世代 L ≥ 總持有成本，所以機隊 L 以營收加權。GB200 每 GW 產出約為 Hopper 的 5 倍，約 77% 的營收來自 GB200', '0.6*' + str(V('Alloc', 'C153')), '0.4*' + str(V('Alloc', 'D153')), fmt='0.000', note='占比 0.6／0.4 與每 GW 付費營收（Alloc 第 153 列）取自 Tokenomics v15.3（數值）')
vrow(11, 'Lb', '對照：Tokenomics 的 L（2025＝第 0 年）', '', "'3_L重算'!D8", "'3_L重算'!D8", "'3_L重算'!D8")
vrow(12, 'LR', '所需 L（恆等式讀法）', '', "'5_所需L'!D9", "'5_所需L'!D9", "'5_所需L'!D9")
vrow(13, 'ratio', 'L（世代起點）÷ 所需 L', '≥ 1＝基準下回本', 'D8/D12', 'E8/E12', 'F8/F12', fmt='0.000')
for c in 'DEF': VG[f'{c}8'].font = BOLD; VG[f'{c}13'].font = BOLD
for i in range(1, 8): VG.cell(13, i).fill = KEY
VG['B15'] = '敏感度（機隊 L ÷ 所需 L；Python 計算，數值）'; VG['B15'].font = BOLD
hdr(VG, 16, ['', 'Hopper t0 ／ GB200 t0 ／ g_pre', '', 'Hopper L', 'GB200 L', '機隊 L', 'L ÷ 所需 L'])
import math as _m
def _Lrel(g, gpre, t0, T1, rho, T=6):
    past = (1 - (1 + gpre) ** (-t0)) / _m.log(1 + gpre) if t0 > 0 else 0
    k = _m.log(1 + g); fut = (((1 + g) ** (T1 - t0) - 1) + rho * ((1 + g) ** (T - t0) - (1 + g) ** (T1 - t0))) / k
    return (past + fut) / T
wH = 0.6 * V('Alloc', 'C153'); wG = 0.4 * V('Alloc', 'D153'); LRb = V('Cap_In', 'C289')
for i, (tH, tG, gp) in enumerate([(2, 0.5, -0.09), (1.5, 0, -0.09), (2.5, 0.5, -0.09), (2, 0, -0.09), (2, 0.5, -0.2), (2, 0.5, -0.3)]):
    r = 17 + i
    lh = _Lrel(-0.09, gp, tH, 4, 0.5); lg = _Lrel(-0.09, gp, tG, 4, 0.5); lf = (wH * lh + wG * lg) / (wH + wG)
    VG.cell(r, 2, f'{tH} 年 ／ {tG} 年 ／ g_pre {gp:+.0%}')
    for j, v in enumerate((lh, lg, lf, lf / LRb)):
        c = VG.cell(r, 4 + j, v); c.font = BLUE; c.number_format = '0.000'
VG['B24'] = '讀法：世代起點使機隊 L 由 0.660 升到約 0.716（敏感度 0.68–0.75，L ÷ 所需 L 0.90–0.99）；因為 77% 的營收來自 2025 才上線的 GB200，修正幅度有限。g_pre 取更陡（2023–24 實際重估）會再提高，但當時量很小，這個方向的證據最弱。'; VG['B24'].font = NOTE
VG.merge_cells('B24:G24'); VG.row_dimensions[24].height = 40; VG['B24'].alignment = WRAP

VG['B26'] = 'v17.0 主口徑：世代起點＋折現（折現到各世代起點，與持有成本年金同口徑）'; VG['B26'].font = BOLD
hdr(VG, 27, ['列', '項目', '公式（白話）', '基準', '低端組合', '高端組合', '對照：Tokenomics'])
def seg(a, x0, x1): return f'IF(ABS({a})<1E-12,({x1})-({x0}),(EXP(({a})*({x1}))-EXP(({a})*({x0})))/({a}))'
def lrd(g, gp, t0, T1, rho, T, r):
    d = f'LN(1+{r})'; kp = f'LN(1+{gp})'; k = f'LN(1+{g})'
    past = f'IF({t0}>0,EXP(-{kp}*{t0})*{seg(kp+"-"+d,"0",t0)},0)'
    mid = f'EXP(-{k}*{t0})*{seg(k+"-"+d,t0,T1)}'
    late = f'{rho}*EXP(-{k}*{t0})*{seg(k+"-"+d,T1,T)}'
    return f'({past}+{mid}+{late})/{seg("-"+d,"0",T)}'
def lru(g, gp, t0, T1, rho, T):
    past = f'IF({t0}>0,(1-(1+{gp})^(-{t0}))/LN(1+{gp}),0)'
    fut = f'(((1+{g})^({T1}-{t0})-1)+{rho}*((1+{g})^({T}-{t0})-(1+{g})^({T1}-{t0})))/LN(1+{g})'
    return f'({past}+{fut})/{T}'
combos = {'b': ('IN_g', 'IN_gpre', 'IN_T1', 'IN_rho', 'IN_T', 'IN_WACC', ''), 'lo': ('IN_g_Lo', 'IN_gpre_Hi', 'IN_T1_Lo', 'IN_rho_Lo', 'IN_T', 'IN_WACC_Lo', '_Lo'), 'hi': ('IN_g_Hi', 'IN_gpre_Lo', 'IN_T1_Hi', 'IN_rho_Hi', 'IN_T', 'IN_WACC_Hi', '_Hi')}
rowsdef = [(28, 'Hopper L_rel（不折現）', 'u', 'H'), (29, 'GB200 L_rel（不折現）', 'u', 'G'), (30, '機隊 L（世代起點，不折現）', 'uf', None),
           (31, 'Hopper L_rel（折現）', 'd', 'H'), (32, 'GB200 L_rel（折現）', 'd', 'G'), (33, '機隊 L（世代起點＋折現）＝v17.0 主口徑', 'df', None),
           (34, '所需 L（不含 κ；v17.0 主口徑）', 'req', None), (35, '主口徑 L ÷ 所需 L', 'ratio', None)]
wH = f"0.6*{V('Alloc','C153')}"; wG = f"0.4*{V('Alloc','D153')}"
tok = {'u': ('Cap_In', 312), 'd': ('Cap_In', 325)}
for r, lab_, kind, gen in rowsdef:
    VG.cell(r, 2, lab_)
    for j, key in enumerate(('b', 'lo', 'hi')):
        g, gp, T1, rho, T, w, suf = combos[key]
        col = CL(4 + j)
        if kind in ('u', 'd'):
            t0 = f'IN_t0{gen}{suf}'
            f = lru(g, gp, t0, T1, rho, T) if kind == 'u' else lrd(g, gp, t0, T1, rho, T, w)
        elif kind == 'uf': f = f'({wH}*{col}28+{wG}*{col}29)/({wH}+{wG})'
        elif kind == 'df': f = f'({wH}*{col}31+{wG}*{col}32)/({wH}+{wG})'
        elif kind == 'req': f = {'b': "'5_所需L'!D14", 'lo': "'5_所需L'!E14", 'hi': "'5_所需L'!F14"}[key]
        else: f = f'{col}33/{col}34'
        c = VG.cell(r, 4 + j, '=' + f); c.number_format = '0.0000'
    VG.cell(r, 3, {'u': '同上半部公式', 'd': '＝(past＋mid＋late) ÷ seg(−d,0,T)，past＝e^(−kp·t0)·seg(kp−d,0,t0)、mid＝e^(−k·t0)·seg(k−d,t0,T1)、late＝ρ·e^(−k·t0)·seg(k−d,T1,T)', 'uf': '2025 營收加權', 'df': '2025 營收加權', 'req': '推論支出 ÷（計價倍數 × 營收）', 'ratio': '≥ 1＝基準下回本'}[kind]).font = NOTE
    VG.cell(r, 3).alignment = WRAP
for r, src in ((30, 312), (33, 325)):
    VG.cell(r, 7, f"{V('Cap_In', f'C{src}'):.6f}／{V('Cap_In', f'D{src}'):.6f}／{V('Cap_In', f'E{src}'):.6f}").font = BLUE
for c in 'DEF':
    VG[f'{c}33'].font = BOLD; VG[f'{c}35'].font = BOLD
for i in range(1, 8): VG.cell(33, i).fill = KEY
VG['B37'] = '判讀（v17.0 主口徑，三態）'; VG['B37'].font = BOLD
VG['D37'] = '=IF(MAX(E33,F33)<MIN(E34,F34),"未回本",IF(MIN(E33,F33)>MAX(E34,F34),"回本","未定（區間重疊）"))'
VG['B38'] = '對照：Tokenomics Cap_In C242'; VG['D38'] = V('Cap_In', 'C242'); VG['D38'].font = BLUE

# ------------------------------------------------------------------ 0_說明
Z = sheet('0_說明', [4, 110])
lines = [('L 推導檢核（Tokenomics v17.0）', TITLE),
 ('建立：2026-10-18，chat 端（Claude）。用途：讓 Andy 自行檢核 L（壽命期價格係數）、所需 L 與回本判讀的完整推導。姊妹檔：m 推導檢核（20261018_m推導檢核_v15.3.xlsx）。', NOTE), ('', None),
 ('分頁', BOLD),
 ('1_總覽：回本條件、L 與所需 L、三態判讀、兩個待判斷的發現（所需 L 含 κ；L 不折現）、驗證、最不確定的輸入。', None),
 ('2_輸入：全部輸入（藍字，可改；基準／低端／高端三欄）。黃底＝不確定度「高」。', None),
 ('3_L重算：L_price、L_total、L_demote 的閉式解（基準／低／高），與原值比對；另加折現版 L。', None),
 ('4_逐年路徑：把 L 的積分拆成每一年的價格指數、降級、折現，加總後等於閉式解。', None),
 ('5_所需L：恆等式讀法的逐步推導與約分（持有成本約掉）；替代讀法（不含 κ、含支出區間）；字面讀法（對照）。', None),
 ('6_回本判讀：三態判讀；g × ρ 的 L 格點（綠＝回本、紅＝未回本，T1 可改）；回本所需 g 的「必須為真」表。', None),
 ('7_敏感度：每次動一個輸入，看 L ÷ 所需 L 與是否翻轉（全部公式）。', None),
 ('8_不確定_搜尋、9_不確定_實地調研：最不確定的假設，附要找的證據、來源、訪談問題。', None),
 ('10_前置格清單：判讀格在 Tokenomics 中的前置格（m 的前置格見姊妹檔）。', None),
 ('11_世代起點：每個世代用自己的第 0 年算 L，再以持有成本加權（發現三）。', None), ('', None),
 ('顏色', BOLD), ('藍字＝輸入或外部結果（可改）；黑字＝公式；綠字＝連結其他分頁；黃底＝最不確定；淺綠底＝主要結果。', None), ('', None),
 ('範圍與限制', BOLD),
 ('1. 「6_回本判讀」的「必須為真」表是 Python 二分法算出的數值（Excel 沒有不迭代的解法），改輸入不會自動更新；格點與其他各頁皆為公式。', None),
 ('2. 本簿的判讀只看服務機隊，不含訓練與研發；營收量固定在 2025 年，只讓價格走 L 的路徑（量的成長不在 L 裡）。', None),
 ('3. 折現版 L、不含 κ 的所需 L 是本簿新增的對照，Tokenomics 目前沒有；是否改模型待 Andy 判斷（發現一、二）。', None),
 ('4. Tokenomics Cap_In G226、G232、G233 的說明文字仍寫舊值（g −0.10／−0.25、L 0.7412／0.6426），屬過期標籤，數值格本身正確。', None)]
for i, (t, fnt) in enumerate(lines, 1):
    c = Z.cell(i, 2, t); c.alignment = WRAP; c.font = fnt or BLACK

order = ['0_說明', '1_總覽', '2_輸入', '3_L重算', '4_逐年路徑', '5_所需L', '6_回本判讀', '7_敏感度', '8_不確定_搜尋', '9_不確定_實地調研', '10_前置格清單', '11_世代起點']
wb._sheets = [wb[n] for n in order]; wb.active = 1
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.font is None or c.font.name != F:
                c.font = Font(name=F, size=(c.font.size if c.font else 10) or 10, bold=c.font.bold if c.font else False, color=c.font.color if c.font else None)
wb.save('L推導檢核_v17.0.xlsx'); print('saved', NPRE)

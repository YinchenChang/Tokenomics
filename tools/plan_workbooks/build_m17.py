# 建立「m 推導檢核」活頁簿：輸入（藍字）→ 每 GW 產出（roofline）、持有成本 → m，全部為 Excel 公式
import openpyxl, json, re
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as CL

SRC = 'v170.xlsx'
wv = openpyxl.load_workbook(SRC, data_only=True)
wfm = openpyxl.load_workbook(SRC)
gm = wv['Gov_Map']
GM = {}
for row in gm.iter_rows(min_row=5):
    k = (row[2].value, str(row[3].value))
    GM[k] = dict(id=row[0].value, cat=row[5].value, lo=row[10].value, hi=row[11].value, why=row[13].value)

def V(sh, a): return wv[sh][a].value

F = 'Arial'
BLUE = Font(name=F, color='0000FF', size=10)
BLACK = Font(name=F, color='000000', size=10)
GREEN = Font(name=F, color='008000', size=10)
BOLD = Font(name=F, bold=True, size=10)
HEAD = Font(name=F, bold=True, size=10, color='FFFFFF')
TITLE = Font(name=F, bold=True, size=13)
NOTE = Font(name=F, size=9, color='555555')
HFILL = PatternFill('solid', fgColor='305496')
SEC = PatternFill('solid', fgColor='D9E1F2')
YEL = PatternFill('solid', fgColor='FFF2CC')
KEY = PatternFill('solid', fgColor='E2EFDA')
WRAP = Alignment(wrap_text=True, vertical='top')
thin = Side(style='thin', color='BFBFBF')

wb = openpyxl.Workbook()
wb.remove(wb.active)

def sheet(name, widths):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, 1): ws.column_dimensions[CL(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws

def hdr(ws, r, labels):
    for i, t in enumerate(labels, 1):
        c = ws.cell(r, i, t); c.font = HEAD; c.fill = HFILL; c.alignment = WRAP

def name(nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)

# ---------------------------------------------------------------- 2_輸入
INP = sheet('2_輸入', [8, 14, 46, 14, 12, 18, 11, 11, 22, 70, 10])
INP['A1'] = 'm 推導的全部輸入（藍字＝輸入值，可改；改動後 3_m重算、4、5 頁會自動重算）'; INP['A1'].font = TITLE
INP['A2'] = '值取自 Tokenomics v17.0（20261020_Tokenomics_v17.0.xlsx，master 5ef0f7e）；m 的所有前置格自 v15.3 起未變。標記與區間取自該簿 Gov_Map；「—」＝Gov_Map 無此格的登錄（多為硬體規格或模型架構的原始數據）。'; INP['A2'].font = NOTE
hdr(INP, 4, ['ID', '群組', '項目', '值', '單位', '標記（Gov_Map）', '區間低', '區間高', '原活頁簿位置', '說明與來源', '不確定度'])
rowp = [5]
names_rows = {}
def inp(nid, grp, label, sh, a, unit, note, unc='', val=None):
    r = rowp[0]; rowp[0] += 1
    v = V(sh, a) if val is None else val
    g = GM.get((sh, a), {})
    cells = [nid, grp, label, v, unit, g.get('cat', '—'), g.get('lo'), g.get('hi'), f'{sh}!{a}', note, unc]
    for i, x in enumerate(cells, 1):
        c = INP.cell(r, i, x); c.font = BLACK; c.alignment = WRAP
    INP.cell(r, 4).font = BLUE
    if unc == '高':
        for i in range(1, 12): INP.cell(r, i).fill = YEL
    name(nid, f"'2_輸入'!$D${r}")
    names_rows[nid] = r
    return r
def sec(t):
    r = rowp[0]; rowp[0] += 1
    INP.cell(r, 1, t).font = BOLD
    for i in range(1, 12): INP.cell(r, i).fill = SEC

sec('A. 營收與推論支出（OpenAI 2025）')
inp('IN_Rev', 'A', 'OpenAI 2025 營收', 'SRC_Demand', 'C11', '$B', 'SRC_DEM_007；2025 查核財報營收 130.7 億美元（外流、FT 核實）', '低')
inp('IN_Spend', 'A', 'OpenAI 2025 推論支出（服務用戶，所有供應商）', 'SRC_Demand', 'C8', '$B', 'SRC_DEM_004；OpenAI 投資人資料（經 The Information）；低 7.5＝查核營業成本、高 8.8＝調整後毛利率 33% 換算。Microsoft 端 126 億為對照（含研究推論），不採（調和分析 2026-10-17）', '中')
sec('B. 機隊配置與利用率')
inp('IN_ShareH', 'B', '2025 服務世代組合：Hopper（GW 占比）', 'Alloc_In', 'C9', '%', '無公開數字；chat 端暫設區間 0.5–0.7。Andy 線上／線下調研項', '高')
inp('IN_ShareG', 'B', '2025 服務世代組合：GB200（GW 占比）', 'Alloc_In', 'C10', '%', '＝1 − Hopper（GB300、VR200 在 2025 為 0）', '高')
inp('IN_SpendBasis', 'B', '計價倍數＝推論支出 ÷ 持有成本', 'Alloc_In', 'C23', 'x', '經濟口徑：價格 ÷ 會計成本 1.16 × 會計 ÷ 經濟持有成本 0.73；Microsoft 對 OpenAI 的實際計價未找到', '高')
inp('IN_Kappa', 'B', '請求形狀修正 κ（實際流量每 GPU 秒 token ÷ 參考請求）', 'Alloc_In', 'C26', 'x', '證據範圍 0.67–1.05（2025 流量形狀，A 段第 3 節）；重算值 0.852（Alloc_In 第 41 列）；v15.3 擺動第一名', '高')
inp('IN_UtilAct', 'B', '實際利用率（純；平均 token 吞吐 ÷ 容量）', 'Alloc_In', 'C24', '%', '無實測；上端 DeepSeek 2025-02 單一模型代理值 0.54–0.65', '高')
inp('IN_ProdDerate', 'B', '生產折減（SLO 預留、故障、重啟）', 'Serving', 'C28', 'x', '情境值，非估計值；只有訓練端公開論文可類比', '高')
inp('IN_Util', 'B', '基準利用率 IF_Util（模型內部的每 GW 產能口徑）', 'Serving', 'C17', '%', '在 m 中會約掉（服務 GW 的利用率修正 ÷ IF_Util，產能 × IF_Util）；見 1_總覽', '低（約掉）')
sec('C. 2025 價格與層級組合')
inp('IN_Px_L', 'C', '2025 年度單價：Luna（參考請求混合價，表列）', 'Cap_In', 'C278', '$/M', 'nano 線在售天數加權；牌價 Verified', '低')
inp('IN_Px_S', 'C', '2025 年度單價：Sol', 'Cap_In', 'C279', '$/M', 'API 主力與 ChatGPT 預設按付費 token 加權', '中')
inp('IN_Px_A', 'C', '2025 年度單價：Astra（推理旗艦）', 'Cap_In', 'C280', '$/M', 'v15.2 B2：用量加權 4.5（Azure 季別量指數 × GPT-5 後推理占比 ×2）；各模型 token 占比未公開', '高')
inp('IN_Disc', 'C', '有效折扣（Batch／Flex 半價＋企業議價，加權）', 'Cap_In', 'C12', '%', 'Batch 半價 Verified；占比與企業折扣找不到', '高')
inp('IN_MixP_L', 'C', '付費 token 層級組合：Luna', 'Cap_In', 'C31', '%', 'OpenAI 模型 v0.5 tokenMix（Assumed）；三者合計 1', '中')
inp('IN_MixP_S', 'C', '付費 token 層級組合：Sol', 'Cap_In', 'D31', '%', '同上', '中')
inp('IN_MixP_A', 'C', '付費 token 層級組合：Astra', 'Cap_In', 'E31', '%', '同上；v15.2 B6 區間 0.10–0.30', '中')
inp('IN_MixF_L', 'C', '免費 token 層級組合：Luna', 'Cap_In', 'C32', '%', 'OpenAI 模型 v0.5 免費方案組合（Assumed）', '中')
inp('IN_MixF_S', 'C', '免費 token 層級組合：Sol', 'Cap_In', 'D32', '%', '同上', '中')
inp('IN_MixF_A', 'C', '免費 token 層級組合：Astra', 'Cap_In', 'E32', '%', '同上', '低')
sec('D. 需求 token（決定免費 ÷ 付費 token 比 r）')
inp('IN_APItpm', 'D', 'API token 吞吐（2025-10 時點）', 'SRC_Demand', 'C14', 'B tok/分', 'SRC_DEM_010；OpenAI 2025-10-06 公告 60 億 token／分（Interested-party）', '低')
inp('IN_APIratio', 'D', 'API 全年平均 ÷ 10 月時點值', 'Alloc_In', 'C14', 'x', 'Assumed', '中')
inp('IN_Prompts', 'D', 'ChatGPT 每日訊息數', 'SRC_Demand', 'C16', 'B 則/日', 'SRC_DEM_012；OpenAI 自述 25 億則／日', '低')
inp('IN_Tau', 'D', '每則提示 token 數 τ', 'Alloc_In', 'C15', 'tok', 'Assumed；閉合解遠高於區間（L1_TokPerPromptClose）', '中')
inp('IN_FreeShare', 'D', 'ChatGPT token 中免費用戶占比', 'Alloc_In', 'C16', '%', 'Assumed；token 口徑與支出口徑混用（Decisions SL46-28）', '中')
sec('E. 服務與快取參數（全層級共用）')
inp('IN_Chi', 'E', '參考請求快取命中率 χ', 'Cap_In', 'C13', '%', 'Assumed；DeepSeek 2025-03 為 56.3%；2026 agent 流量約 88%', '中')
inp('IN_MTP_N', 'E', 'MTP 草稿數 N', 'Serving', 'C6', 'tok', '原始數據', '低')
inp('IN_MTP_a', 'E', '草稿 token 接受率 α', 'Serving', 'C7', '%', '原始數據', '低')
inp('IN_HBMres', 'E', 'HBM 保留比例', 'Serving', 'C9', '%', '', '低')
inp('IN_NEcap', 'E', '非專家權重占可用 HBM 上限', 'Serving', 'C10', '%', '', '低')
inp('IN_Ecap', 'E', '專家權重占可用 HBM 上限', 'Serving', 'C11', '%', '', '低')
inp('IN_EPbytes', 'E', 'EP 啟用值 bytes／元素', 'Serving', 'C12', 'B', '', '低')
inp('IN_KVeff', 'E', 'KV 讀取頻寬效率', 'Serving', 'C13', '%', '', '低')
inp('IN_EPeff', 'E', 'EP 通訊效率', 'Serving', 'C14', '%', '', '低')
sec('F. 校準係數（Calib 頁以 GB300 實測擬合；Hopper／GB200 以倍數換算）')
inp('IN_EtaD0', 'F', 'η_d 擬合值（GB300，decode 每序列算力效率）', 'Calib', 'C60', '%', '以 InferenceX GB300 兩個實測點聯立解出（SemiAnalysis，Interested-party）', '中')
inp('IN_Lat0', 'F', '每層每次前向固定延遲擬合值（GB300）', 'Calib', 'C62', 'µs', '同上', '中')
inp('IN_EtaP0', 'F', 'η_p：prefill 達成峰值比例（基準）', 'Calib', 'C5', '%', 'Analogy', '中')
inp('IN_EtaDm_H', 'F', 'η_d 倍數：Hopper', 'Calib', 'C67', 'x', '吞吐為保守下界（獨立對照約實測 0.26–0.27 倍）', '高')
inp('IN_EtaDm_G', 'F', 'η_d 倍數：GB200', 'Calib', 'D67', 'x', 'v15.2 B3：MLPerf v6.0 同軟體配對 1.13–1.27', '中')
inp('IN_Latm_H', 'F', '每層延遲倍數：Hopper', 'Calib', 'C68', 'x', 'Assumed', '中')
inp('IN_Latm_G', 'F', '每層延遲倍數：GB200', 'Calib', 'D68', 'x', '沿用 GB300', '中')
inp('IN_EtaPm_H', 'F', 'η_p 倍數：Hopper（＝SRC_HW_019 ÷ SRC_HW_040）', 'Calib', 'C69', 'x', '原為公式（規格比），此處以值輸入', '低')
inp('IN_EtaPm_G', 'F', 'η_p 倍數：GB200', 'Calib', 'D69', 'x', '', '低')
sec('G. 硬體規格（Spec_Rack；H＝Hopper H100、G＝GB200 NVL72）')
spec = [('Peak', '計算用峰值', 'PF/GPU', 35), ('HBM', 'HBM 容量', 'GB/GPU', 25), ('BW', 'HBM 頻寬', 'TB/s/GPU', 26),
        ('EPBW', 'EP 通訊頻寬（單向）', 'TB/s/GPU', 27), ('EPW', 'decode EP 基準寬度', 'GPU', 29), ('EB', '專家權重 bytes/param', 'B', 30),
        ('NEB', '非專家權重 bytes/param', 'B', 31), ('PFG', '每 prefill 實例 GPU 數', 'GPU', 32), ('GPR', 'GPU 封裝／架', '顆', 6),
        ('RackKW', '每架配電設計功率（基準）', 'kW', 9), ('RackPx', '機架價格（基準）', '$M', 12)]
for key, lab, unit, r in spec:
    for g, col, gn in (('H', 'C', 'Hopper'), ('G', 'D', 'GB200')):
        u = '高' if key == 'RackPx' else '低'
        inp(f'IN_{key}_{g}', 'G', f'{lab}：{gn}', 'Spec_Rack', f'{col}{r}', unit, '原始數據（規格表；NVIDIA 為利害關係方）' if key != 'RackPx' else '機架價格：產業報導與 ODM 報價區間（利害關係方）', u)
sec('H. 模型架構（Arch；L＝Luna、S＝Sol、A＝Astra）——頂層模型參數未揭露')
arch = [('Act', '啟用參數', 'B', 28), ('Lay', '層數', '層', 29), ('Dm', 'd_model', '', 30), ('Exp', '啟用 routed experts', '', 31),
        ('NEP', '非專家參數', 'B', 32), ('EP', '專家參數', 'B', 33), ('KV', 'KV bytes/token', 'B', 34), ('AF', '注意力 FLOPs／被注意 token', 'FLOP', 35),
        ('FA', '全注意力層比例', '%', 36), ('Span', '全注意力跨度上限（0＝不設限）', 'tok', 37), ('Cmp', '其他層壓縮比', 'x', 38), ('Win', '其他層滑動窗', 'tok', 39)]
for key, lab, unit, r in arch:
    for t, col, tn in (('L', 'C', 'Luna'), ('S', 'D', 'Sol'), ('A', 'E', 'Astra')):
        u = '高' if (t == 'A' and key in ('Act', 'NEP', 'EP')) else '中'
        inp(f'IN_{key}_{t}', 'H', f'{lab}：{tn}', 'Perf', f'{col}{r}', unit, '代表架構（Sol＝DeepSeek V4-Pro 型）；Astra 啟用參數 180B 為 Assumed（60–250B）' if key == 'Act' else '代表架構參數（Arch 頁）', u)
sec('I. 服務等級（SLO）與參考請求（Serving；各層級）')
for key, lab, unit, r in (('SLO', 'SLO：每用戶 decode 速度下限', 'tok/s', 41), ('TTFT', 'TTFT 上限', 's', 42), ('ISL', '參考 ISL（每次請求輸入）', 'tok', 43), ('OSL', '參考 OSL（含思考）', 'tok', 44)):
    for t, col, tn in (('L', 'C', 'Luna'), ('S', 'D', 'Sol'), ('A', 'E', 'Astra')):
        u = '中' if key in ('ISL', 'OSL') else '低'
        inp(f'IN_{key}_{t}', 'I', f'{lab}：{tn}', 'Perf', f'{col}{r}', unit, 'SLO＝兩個第三方量測商中位數的幾何平均' if key == 'SLO' else 'Assumed（×0.5–×2）' if key in ('ISL', 'OSL') else '', u)
sec('J. 資料中心成本（Inputs，基準欄 E）')
dc = [('ITout', '機架外 IT 電力占比', 'Inputs', 'E8', '%'), ('PUE', 'PUE', 'Inputs', 'E9', 'x'), ('Load', '平均用電 ÷ 配電設計功率', 'Inputs', 'E10', '%'),
      ('Elec', '電價', 'Inputs', 'E11', '$/kWh'), ('Net', 'Scale-out 網路 ÷ 機架價格', 'Inputs', 'E13', '%'), ('Stor', '儲存與管理設備', 'Inputs', 'E14', '$/GPU'),
      ('Land', '土地', 'Inputs', 'E16', '$M/MW'), ('Bldg', '建物與基地工程', 'Inputs', 'E17', '$M/MW'), ('Pwr', '電力設施', 'Inputs', 'E18', '$M/MW'),
      ('Mech', '機械與散熱', 'Inputs', 'E19', '$M/MW'), ('Fib', '光纖、佈線、保全', 'Inputs', 'E20', '$M/MW'), ('Soft', '設計、管理與預備費', 'Inputs', 'E21', '% 廠房'),
      ('ITlife', 'IT 設備折舊年限', 'Inputs', 'E23', '年'), ('L_bldg', '建物年限', 'Inputs', 'E24', '年'), ('L_pwr', '電力設施年限', 'Inputs', 'E25', '年'),
      ('L_mech', '機械與散熱年限', 'Inputs', 'E26', '年'), ('L_fib', '光纖與保全年限', 'Inputs', 'E27', '年'), ('WACC', 'WACC（經濟口徑）', 'Inputs', 'E28', '%'),
      ('ITmaint', 'IT 維護', 'Inputs', 'E30', '% IT 資本/年'), ('Fmaint', '廠房維護', 'Inputs', 'E31', '% 廠房資本/年'), ('Staff', '人員', 'Inputs', 'E32', '$M/GW/年'),
      ('SW', '軟體授權與連線', 'Inputs', 'E33', '$M/GW/年'), ('Water', '水與耗材', 'Inputs', 'E34', '$M/MW/年'), ('Tax', '財產稅與保險', 'Inputs', 'E35', '% 總資本/年')]
for key, lab, sh, a, unit in dc:
    u = '中' if key in ('WACC', 'ITlife') else '低'
    inp(f'IN_{key}', 'J', lab, sh, a, unit, '', u)

# ---------------------------------------------------------------- 5_每GW產出（roofline，6 個案例）
P = sheet('5_每GW產出', [8, 52, 11, 15, 15, 15, 15, 15, 15, 70])
P['A1'] = '每 GW 年產出（roofline）：每請求 GPU 秒 → 每架 tok/s → 每 GW M tok/年（100% 利用率）'; P['A1'].font = TITLE
P['A2'] = '六個案例＝Hopper／GB200 × Luna／Sol／Astra。公式與 Tokenomics Perf 頁逐列相同；最後兩列與原活頁簿比對。綠字＝連結 2_輸入；黑字＝本頁公式。'; P['A2'].font = NOTE
hdr(P, 4, ['列', '項目', '單位', 'Hopper Luna', 'Hopper Sol', 'Hopper Astra', 'GB200 Luna', 'GB200 Sol', 'GB200 Astra', '公式說明（物理意義）'])
cases = [('H', 'L'), ('H', 'S'), ('H', 'A'), ('G', 'L'), ('G', 'S'), ('G', 'A')]
COLS = ['D', 'E', 'F', 'G', 'H', 'I']
perfcol = {('H', 'L'): 'C', ('H', 'S'): 'D', ('H', 'A'): 'E', ('G', 'L'): 'F', ('G', 'S'): 'G', ('G', 'A'): 'H'}
pr = [5]; PR = {}
def prow(key, lab, unit, fn, note='', link=False, sect=None):
    if sect:
        r = pr[0]; pr[0] += 1
        P.cell(r, 1, sect).font = BOLD
        for i in range(1, 11): P.cell(r, i).fill = SEC
    r = pr[0]; pr[0] += 1; PR[key] = r
    P.cell(r, 1, key).font = NOTE; P.cell(r, 2, lab).font = BLACK; P.cell(r, 3, unit).font = BLACK
    for (g, t), col in zip(cases, COLS):
        f = fn(g, t, col)
        c = P.cell(r, COLS.index(col) + 4, f); c.font = GREEN if link else BLACK
        c.number_format = '#,##0.000###'
    c = P.cell(r, 10, note); c.font = NOTE; c.alignment = WRAP
    P.cell(r, 2).alignment = WRAP
    return r
def R(k): return PR[k]
L = lambda nm: (lambda g, t, col: f'={nm}')
LG = lambda key: (lambda g, t, col: f'=IN_{key}_{g}')
LT = lambda key: (lambda g, t, col: f'=IN_{key}_{t}')
prow('peak', '計算用峰值', 'PF/GPU', LG('Peak'), link=True, sect='A. 規格（每 GPU）')
prow('hbm', 'HBM 容量', 'GB', LG('HBM'), link=True)
prow('bw', 'HBM 頻寬', 'TB/s', LG('BW'), link=True)
prow('epbw', 'EP 通訊頻寬', 'TB/s', LG('EPBW'), link=True)
prow('epw', 'decode EP 基準寬度', 'GPU', LG('EPW'), link=True)
prow('eb', '專家權重 bytes/param', 'B', LG('EB'), link=True)
prow('neb', '非專家權重 bytes/param', 'B', LG('NEB'), link=True)
prow('pfg', '每 prefill 實例 GPU 數', 'GPU', LG('PFG'), link=True)
prow('gpr', 'GPU 封裝／架', '顆', LG('GPR'), link=True)
prow('rpg', '每 GW 機架數', '架', lambda g, t, col: f"='4_持有成本'!{'C' if g=='H' else 'D'}$9", '來自 4_持有成本（機架可用 IT 電力 ÷ 每架功率，取整）', link=True)
prow('act', '啟用參數', 'B', LT('Act'), link=True, sect='B. 架構')
prow('lay', '層數', '層', LT('Lay'), link=True)
prow('dm', 'd_model', '', LT('Dm'), link=True)
prow('exp', '啟用 routed experts', '', LT('Exp'), link=True)
prow('nep', '非專家參數', 'B', LT('NEP'), link=True)
prow('ep', '專家參數', 'B', LT('EP'), link=True)
prow('kv', 'KV bytes/token', 'B', LT('KV'), link=True)
prow('af', '注意力 FLOPs／被注意 token', 'FLOP', LT('AF'), link=True)
prow('fa', '全注意力層比例', '%', LT('FA'), link=True)
prow('span', '全注意力跨度上限', 'tok', LT('Span'), link=True)
prow('cmp', '其他層壓縮比', 'x', LT('Cmp'), link=True)
prow('win', '其他層滑動窗', 'tok', LT('Win'), link=True)
prow('slo', 'SLO 每用戶 decode 速度下限', 'tok/s', LT('SLO'), link=True, sect='C. 服務等級、參考請求、校準')
prow('ttft', 'TTFT 上限', 's', LT('TTFT'), link=True)
prow('isl', '參考 ISL', 'tok', LT('ISL'), link=True)
prow('osl', '參考 OSL（含思考）', 'tok', LT('OSL'), link=True)
prow('ctx', 'decode 平均上下文', 'tok', lambda g, t, c: f'={c}{R("isl")}+{c}{R("osl")}/2', 'ISL ＋ OSL ÷ 2（輸出過程中上下文由 ISL 長到 ISL＋OSL）')
prow('ppos', 'prefill 平均位置', 'tok', lambda g, t, c: f'={c}{R("isl")}/2', 'ISL ÷ 2')
prow('acc', '每步期望接受 token a', 'tok', lambda g, t, c: '=(1-IN_MTP_a^(IN_MTP_N+1))/(1-IN_MTP_a)', 'MTP 推測解碼：(1 − α^(N+1)) ÷ (1 − α)')
prow('etap', 'η_p（prefill 占峰值）', '%', lambda g, t, c: f'=IN_EtaP0*IN_EtaPm_{g}', 'η_p 基準 × 世代倍數（生產折減在本頁＝1，另於 3_m重算乘入）')
prow('etad', 'η_d（decode 每序列算力效率）', '%', lambda g, t, c: f'=IN_EtaD0*IN_EtaDm_{g}', 'GB300 擬合值 × 世代倍數（GB200＝Calib D67）')
prow('lat', '每層每次前向固定延遲', 'µs', lambda g, t, c: f'=IN_Lat0*IN_Latm_{g}', 'GB300 擬合值 × 世代倍數')
prow('dat', 'decode 被注意 token 數', 'tok', lambda g, t, c: f'={c}{R("fa")}*IF({c}{R("span")}=0,{c}{R("ctx")},MIN({c}{R("ctx")},{c}{R("span")}))+(1-{c}{R("fa")})*({c}{R("ctx")}/{c}{R("cmp")}+{c}{R("win")})', '全注意力層看 min(上下文, 跨度上限)；其他層看 上下文 ÷ 壓縮比 ＋ 滑動窗', sect='D. 每 token 計算量')
prow('dfl', 'decode FLOPs/token', 'GFLOP', lambda g, t, c: f'=(2*{c}{R("act")}*1000000000+{c}{R("af")}*{c}{R("dat")})/1000000000', '2 × 啟用參數（矩陣乘）＋ 注意力 FLOPs × 被注意 token')
prow('pat', 'prefill 被注意 token 數', 'tok', lambda g, t, c: f'={c}{R("fa")}*IF({c}{R("span")}=0,{c}{R("ppos")},MIN({c}{R("ppos")},{c}{R("span")}))+(1-{c}{R("fa")})*({c}{R("ppos")}/{c}{R("cmp")}+{c}{R("win")})', '同上，以 prefill 平均位置計')
prow('pfl', 'prefill FLOPs/token', 'GFLOP', lambda g, t, c: f'=(2*{c}{R("act")}*1000000000+{c}{R("af")}*{c}{R("pat")})/1000000000', '')
prow('hbmu', '可用 HBM', 'GB', lambda g, t, c: f'={c}{R("hbm")}*(1-IN_HBMres)', 'HBM 容量 ×（1 − 保留比例）', sect='E. 記憶體配置（每 GPU）')
prow('tp', '注意力 TP 度', '', lambda g, t, c: f'=MAX(1,CEILING({c}{R("nep")}*{c}{R("neb")}/(IN_NEcap*{c}{R("hbmu")}),1))', '非專家權重放得下所需的最小切分數')
prow('epx', 'decode EP 寬度', 'GPU', lambda g, t, c: f'=MAX({c}{R("epw")},CEILING({c}{R("ep")}*{c}{R("eb")}/(IN_Ecap*{c}{R("hbmu")}),1))', '專家權重放得下所需的最小 EP 寬度，不低於基準寬度')
prow('wpg', '每 GPU 權重', 'GB', lambda g, t, c: f'={c}{R("nep")}*{c}{R("neb")}/{c}{R("tp")}+{c}{R("ep")}*{c}{R("eb")}/{c}{R("epx")}', '')
prow('ptok', 'prefill tok/s（每 prefill GPU）', 'tok/s', lambda g, t, c: f'={c}{R("etap")}*{c}{R("peak")}*1000000000000000/({c}{R("pfl")}*1000000000)', 'η_p × 峰值 ÷ 每 token FLOPs（prefill 為算力受限）', sect='F. Prefill')
prow('ttftv', 'TTFT（只計新鮮輸入）', 's', lambda g, t, c: f'=({c}{R("isl")}*(1-IN_Chi))*{c}{R("pfl")}*1000000000/({c}{R("etap")}*{c}{R("peak")}*1000000000000000*{c}{R("pfg")})', 'ISL ×（1 − χ）× FLOPs ÷（η_p × 峰值 × prefill 實例 GPU 數）')
prow('ttok', 'TTFT 符合上限', '', lambda g, t, c: f'=IF({c}{R("ttftv")}<={c}{R("ttft")},"是","否")', '')
prow('fix', '每步固定延遲（權重讀取＋逐層延遲）', 'ms', lambda g, t, c: f'={c}{R("wpg")}/{c}{R("bw")}+({c}{R("lay")}+IN_MTP_N)*{c}{R("lat")}/1000', '每 GPU 權重 ÷ HBM 頻寬 ＋（層數 ＋ 草稿數）× 每層延遲', sect='G. Decode：每步時間＝固定延遲 ＋ B ×每序列時間；在 SLO 下解出批次 B*')
prow('sc', '每序列每步：算力項', 'ms', lambda g, t, c: f'=(IN_MTP_N+1)*{c}{R("dfl")}/({c}{R("peak")}*{c}{R("etad")})/1000', '（N＋1）× decode FLOPs ÷（峰值 × η_d）——η_d 在這裡起作用')
prow('skv', '每序列每步：KV 讀取項', 'ms', lambda g, t, c: f'={c}{R("kv")}*{c}{R("ctx")}/({c}{R("bw")}*IN_KVeff)/1000000000', 'KV bytes × 上下文 ÷（頻寬 × 效率）')
prow('sep', '每序列每步：EP 通訊項', 'ms', lambda g, t, c: f'=(IN_MTP_N+1)*{c}{R("lay")}*{c}{R("exp")}*{c}{R("dm")}*IN_EPbytes*({c}{R("epx")}-1)/{c}{R("epx")}/({c}{R("epbw")}*IN_EPeff)/1000000000', '')
prow('sq', '每序列每步（三者取最大，假設可重疊）', 'ms', lambda g, t, c: f'=MAX({c}{R("sc")},{c}{R("skv")},{c}{R("sep")})', '')
prow('bslo', 'SLO 允許的批次上限', '序列/GPU', lambda g, t, c: f'=(1000*{c}{R("acc")}/{c}{R("slo")}-{c}{R("fix")})/{c}{R("sq")}', '每用戶速度 ≥ SLO：a ÷（固定＋B×每序列）≥ SLO → B ≤（1000a/SLO − 固定）÷ 每序列')
prow('bhbm', 'HBM 容量允許的批次上限', '序列/GPU', lambda g, t, c: f'=({c}{R("hbmu")}-{c}{R("wpg")})*1000000000/({c}{R("kv")}*{c}{R("ctx")})', '（可用 HBM − 權重）÷ 每序列 KV')
prow('bst', '採用批次 B*', '序列/GPU', lambda g, t, c: f'=MAX(0,MIN({c}{R("bslo")},{c}{R("bhbm")}))', '')
prow('dtok', 'decode tok/s（每 decode GPU）', 'tok/s', lambda g, t, c: f'=IF({c}{R("bst")}>0,{c}{R("bst")}*{c}{R("acc")}/(({c}{R("fix")}+{c}{R("bst")}*{c}{R("sq")})/1000),0)', 'B* × a ÷ 每步時間')
prow('gps', '每請求 GPU 秒', 'GPU-s', lambda g, t, c: f'=({c}{R("isl")}*(1-IN_Chi))/{c}{R("ptok")}+{c}{R("osl")}/{c}{R("dtok")}', '新鮮輸入 ÷ prefill 速度 ＋ 輸出 ÷ decode 速度（快取命中的輸入不計 prefill）', sect='H. 每架與每 GW（100% 利用率）')
prow('rack', '每架總 tok/s（輸入＋輸出）', 'tok/s', lambda g, t, c: f'={c}{R("gpr")}*({c}{R("isl")}+{c}{R("osl")})/{c}{R("gps")}', 'GPU 數 ×（ISL＋OSL）÷ 每請求 GPU 秒')
prow('tokgw', '每 GW 年總產出（100% 利用率）', 'M tok/年', lambda g, t, c: f'={c}{R("rack")}*{c}{R("rpg")}*8760*3600/1000000', '每架 tok/s × 每 GW 機架數 × 一年秒數 ÷ 10^6　→ 即 Tokenomics 的 IF_TokGW_*')
for k in ('tokgw',): P.cell(R(k), 2).font = BOLD
r = pr[0]; pr[0] += 1
P.cell(r, 2, '對照：Tokenomics v15.3 原值（Perf 第 98 列）').font = NOTE
for (g, t), col in zip(cases, COLS):
    c = P.cell(r, COLS.index(col) + 4, V('Perf', f'{perfcol[(g, t)]}98')); c.font = BLUE; c.number_format = '#,##0'
REFR = r
r = pr[0]; pr[0] += 1
P.cell(r, 2, '差異（本頁 ÷ 原值 − 1）').font = BOLD
for col in COLS:
    c = P.cell(r, COLS.index(col) + 4, f'={col}{R("tokgw")}/{col}{REFR}-1'); c.font = BLACK; c.number_format = '0.0000%'
P_DIFF = r
P.freeze_panes = 'D5'

# ---------------------------------------------------------------- 4_持有成本
H = sheet('4_持有成本', [8, 50, 12, 16, 16, 70])
H['A1'] = '每 GW 年經濟持有成本（資本回收年金＋營運費用）'; H['A1'].font = TITLE
H['A2'] = '公式與 Tokenomics DC_Cost 頁（基準成本欄）相同；1 GW IT 電力。'; H['A2'].font = NOTE
hdr(H, 4, ['列', '項目', '單位', 'Hopper H100', 'GB200 NVL72', '公式說明'])
hr = [5]; HR = {}
def hrow(key, lab, unit, fn, note='', sect=None):
    if sect:
        r = hr[0]; hr[0] += 1; H.cell(r, 1, sect).font = BOLD
        for i in range(1, 7): H.cell(r, i).fill = SEC
    r = hr[0]; hr[0] += 1; HR[key] = r
    H.cell(r, 1, key).font = NOTE; H.cell(r, 2, lab).font = BLACK; H.cell(r, 3, unit).font = BLACK
    for g, col in (('H', 'D'), ('G', 'E')):
        c = H.cell(r, 4 if g == 'H' else 5, fn(g, col)); c.font = BLACK; c.number_format = '#,##0.000###'
    H.cell(r, 6, note).font = NOTE; H.cell(r, 6).alignment = WRAP
def X(k): return HR[k]
hrow('mw', 'IT 電力', 'MW', lambda g, c: '=1000', '1 GW', sect='A. 規模')
hrow('rmw', '機架可用 IT 電力', 'MW', lambda g, c: f'={c}{X("mw")}*(1-IN_ITout)', '扣除機架外 IT 電力')
hrow('racks', '機架數', '架', lambda g, c: f'=FLOOR({c}{X("rmw")}*1000/IN_RackKW_{g},1)', '可用 IT 電力 ÷ 每架功率，取整')
# 讓 5_每GW產出 的 rpg 讀到 C9／D9：把機架數放在固定位置
hrow('gpus', 'GPU 數', '顆', lambda g, c: f'={c}{X("racks")}*IN_GPR_{g}', '')
hrow('rack', '機架', '$B', lambda g, c: f'={c}{X("racks")}*IN_RackPx_{g}/1000', '機架數 × 機架單價', sect='B. 資本支出')
hrow('net', 'Scale-out 網路', '$B', lambda g, c: f'={c}{X("rack")}*IN_Net', '')
hrow('stor', '儲存與管理', '$B', lambda g, c: f'={c}{X("gpus")}*IN_Stor/1000000000', '')
hrow('it', 'IT 設備小計', '$B', lambda g, c: f'={c}{X("rack")}+{c}{X("net")}+{c}{X("stor")}', '')
hrow('land', '土地', '$B', lambda g, c: f'={c}{X("mw")}*IN_Land/1000', '')
hrow('bldg', '建物與基地', '$B', lambda g, c: f'={c}{X("mw")}*IN_Bldg/1000', '')
hrow('pwr', '電力設施', '$B', lambda g, c: f'={c}{X("mw")}*IN_Pwr/1000', '')
hrow('mech', '機械與散熱', '$B', lambda g, c: f'={c}{X("mw")}*IN_Mech/1000', '')
hrow('fib', '光纖與保全', '$B', lambda g, c: f'={c}{X("mw")}*IN_Fib/1000', '')
hrow('soft', '設計、管理與預備費', '$B', lambda g, c: f'=({c}{X("bldg")}+{c}{X("pwr")}+{c}{X("mech")}+{c}{X("fib")})*IN_Soft', '')
hrow('fac', '廠房小計', '$B', lambda g, c: f'={c}{X("land")}+{c}{X("bldg")}+{c}{X("pwr")}+{c}{X("mech")}+{c}{X("fib")}+{c}{X("soft")}', '')
hrow('capex', '總資本支出', '$B', lambda g, c: f'={c}{X("it")}+{c}{X("fac")}', '')
hrow('elec', '電費', '$B', lambda g, c: f'={c}{X("mw")}*1000*IN_Load*IN_PUE*8760*IN_Elec/1000000000', 'IT 電力 × 平均負載 × PUE × 8760 × 電價', sect='C. 營運費用（年）')
hrow('itm', 'IT 維護', '$B', lambda g, c: f'={c}{X("it")}*IN_ITmaint', '')
hrow('fm', '廠房維護', '$B', lambda g, c: f'={c}{X("fac")}*IN_Fmaint', '')
hrow('ops', '人員、軟體、水與耗材', '$B', lambda g, c: f'=(IN_Staff*{c}{X("mw")}/1000+IN_SW*{c}{X("mw")}/1000+IN_Water*{c}{X("mw")})/1000', '')
hrow('tax', '財產稅與保險', '$B', lambda g, c: f'={c}{X("capex")}*IN_Tax', '')
hrow('opex', '營運費用小計', '$B', lambda g, c: f'={c}{X("elec")}+{c}{X("itm")}+{c}{X("fm")}+{c}{X("ops")}+{c}{X("tax")}', '')
hrow('crf', 'IT 資本回收係數', 'x', lambda g, c: '=IN_WACC/(1-(1+IN_WACC)^(-IN_ITlife))', 'WACC ÷（1 −（1＋WACC）^−年限）：把 IT 資本攤成等額年金', sect='D. 經濟口徑年持有成本')
hrow('itrec', 'IT 資本回收', '$B', lambda g, c: f'={c}{X("it")}*{c}{X("crf")}', '')
hrow('facrec', '廠房資本回收（土地按 WACC 計機會成本）', '$B', lambda g, c: f'=({c}{X("bldg")}*IN_WACC/(1-(1+IN_WACC)^(-IN_L_bldg))+{c}{X("pwr")}*IN_WACC/(1-(1+IN_WACC)^(-IN_L_pwr))+{c}{X("mech")}*IN_WACC/(1-(1+IN_WACC)^(-IN_L_mech))+{c}{X("fib")}*IN_WACC/(1-(1+IN_WACC)^(-IN_L_fib)))*(1+IN_Soft)+{c}{X("land")}*IN_WACC', '')
hrow('hold', '每 GW 年經濟持有成本', '$B/GW·年', lambda g, c: f'={c}{X("itrec")}+{c}{X("facrec")}+{c}{X("opex")}', '＝ Tokenomics 的 IF_HoldEcon（AL_HoldGen）')
H.cell(X('hold'), 2).font = BOLD
r = hr[0]; hr[0] += 1
H.cell(r, 2, '對照：Tokenomics v15.3 原值（Alloc 第 39 列）').font = NOTE
H.cell(r, 4, V('Alloc', 'C39')).font = BLUE; H.cell(r, 5, V('Alloc', 'D39')).font = BLUE
HREF = r
r = hr[0]; hr[0] += 1
H.cell(r, 2, '差異（本頁 ÷ 原值 − 1）').font = BOLD
for c in 'DE':
    x = H[f'{c}{r}']; x.value = f'={c}{X("hold")}/{c}{HREF}-1'; x.number_format = '0.0000%'
H_DIFF = r
# 回填 5_每GW產出 的每 GW 機架數連結
for (g,t),col in zip(cases,COLS):
    P.cell(PR['rpg'], COLS.index(col)+4, f"='4_持有成本'!{'D' if g=='H' else 'E'}${HR['racks']}").font=GREEN

json.dump(dict(PR=PR, HR=HR, names_rows=names_rows, P_DIFF=P_DIFF, H_DIFF=H_DIFF), open('layout.json', 'w'))
wb._mbuild = dict(P=P, H=H, INP=INP)
import pickle
STATE = dict(PR=PR, HR=HR)
exec(open('build_m2_17.py', encoding='utf-8').read())

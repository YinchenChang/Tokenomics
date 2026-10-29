"""m 閱讀版：說明句公式化（v21.4）。由 build_reading_m_part2.py 在 9_核對對照 之前 exec，共用其命名空間（WS、IN 等）。
把說明句裡寫死的現行值數字換成公式（formula_text.apply_text）；句子的顯示文字不變。
歷史敘述（修訂紀錄、各版舊值）與外部來源的事實不在此改。清單見 text_inventory_m.csv。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__.replace('build_reading_m.py', 'formula_text.py'))))
from formula_text import apply_text, num, numn, pct, gen, REPLACED

_S = lambda n: WS[n]
_t = lambda *a: apply_text(*a)
D1 = lambda ref: num(ref, '0.0')
D2 = lambda ref: num(ref, '0.00')
G2 = lambda ref: num(ref, '0.0#')
K = lambda ref: num(ref, '#,##0')
Y = lambda ref: num(f'{ref}*10', '0')            # 十億 → 億（×10）
YI = lambda ref: Y(ref) + '&" 億"'

# 0_說明、1_總覽
_t(_S('0_說明'), 'B6', [('0.20', D2('IN_Disc'))])
o = _S('1_總覽')
_t(o, 'B5', [('20%', num('IN_Disc', '0%'))])
_t(o, 'H23', [('0.20', D2("'4_分路線'!H9"))])
_t(o, 'H25', [('8.12', D2('F25')), ('5.62', D2('F24'))])
_t(o, 'B33', [('1.43', D2('E31'))])

# 1A_需求公式樹
t = _S('1A_需求公式樹')
_t(t, 'A3', [('20%', num('IN_Disc', '0%'))])
_t(t, 'F11', [('0.1', D1('IN_Disc_Lo')), ('0.4', D1('IN_Disc_Hi'))])
_t(t, 'F22', [('70%', num('IN_SubShare', '0%')), ('0.55', D2('IN_SubShare_Q2'))])
_t(t, 'F23', [('0.10', D2('IN_SeatShare')), ('0.25', D2('IN_SeatShare_Q2'))])
_t(t, 'F28', [('60', Y('IN_APItpm')), ('150', Y('IN_APItpm26'))])
_t(t, 'F29', [('0.6', D1('IN_APIratio_Lo')), ('0.9', D1('IN_APIratio_Hi')), ('1.3', D1('IN_APImultFY'))])
_t(t, 'F31', [('25 億', YI('IN_Prompts')), ('3.6', D1('IN_Prompts_Q2'))])
_t(t, 'F32', [('2,000', K('IN_Tau_Lo')), ('11,000', K('IN_Tau_Hi'))])
_t(t, 'F33', [('0.4', D1('IN_FreeShare_Lo')), ('0.8', D1('IN_FreeShare_Hi'))])
_t(t, 'F37', [('0.75', D2('IN_SubTokShare')), ('0.65', D2('IN_SubTokShare26'))])
for a, nm in (('F44', 'IN_CapMult_L'), ('F45', 'IN_CapMult_S'), ('F46', 'IN_CapMult_A')):
    _t(t, a, [('現值 1', '"現值 "&' + gen(nm))])
_t(t, 'F47', [('0.65', G2('IN_Kappa_Lo')), ('1.2', G2('IN_Kappa_Hi'))])
_t(t, 'F54', [('4,000', K('IN_Tau')), ('2,000', K('IN_Tau_Lo')), ('11,000', K('IN_Tau_Hi'))])
_t(t, 'B58', [('10,752', K('D54')), ('2,000', K('IN_Tau_Lo')), ('11,000', K('IN_Tau_Hi')), ('2.634', num('D9', '0.000')), ('2.429', num('D10', '0.000'))])

# 2_輸入
i = _S('2_輸入')
_t(i, 'J6', [('130.7', D1('IN_Rev*10'))])
_t(i, 'J9', [('36', num('IN_RevFY', '0'))])
_t(i, 'J11', [('0.5', D1('IN_Ad_Q2'))])
_t(i, 'J12', [('1.0', D1('IN_Ad_FY'))])
_t(i, 'J14', [('0.612', num('IN_SubShare_Lo', '0.000')), ('0.82', D2('IN_SubShare_Hi'))])
_t(i, 'J15', [('0.10', D2('IN_SeatShare')), ('0.05', D2('IN_SeatShare_Lo')), ('0.15', D2('IN_SeatShare_Hi'))])
_t(i, 'J19', [('0.20', D2("'4_分路線'!G9"))])
_t(i, 'J23', [('60', Y('IN_APItpm'))])
_t(i, 'J25', [('15', num('IN_APItpm26', '0'))])
_t(i, 'J26', [('1.3', D1('IN_APImultFY'))])
_t(i, 'J27', [('25 億', YI('IN_Prompts'))])
_t(i, 'J34', [('0.65', D2('IN_SubTokShare26'))])
_t(i, 'J39', [('10%', num('IN_PCache_L/IN_PIn_L', '0%'))])
_t(i, 'J59', [('0.10', D2('IN_MixP_A_Lo')), ('0.30', D2('IN_MixP_A_Hi')), ('0.4', D1('IN_MixP_L')), ('0.45', D2('IN_MixP_S'))])

# 3_m重算、4_分路線、5_敏感度
m3 = _S('3_m重算')
_t(m3, 'C10', [('1.3', D1('IN_APImultFY'))])
_t(m3, 'C11', [('25 億', YI('IN_Prompts'))])
_t(m3, 'C12', [('4,000', K('IN_Tau'))])
_t(m3, 'C24', [('360', Y('IN_RevFY'))])
_t(_S('4_分路線'), 'C7', [('70%', num('IN_SubShare', '0%'))])
_t(_S('4_分路線'), 'C16', [('0.65', D2('IN_SubTokShare26'))])
_t(_S('5_敏感度'), 'N13', [('0.40', D2('IN_MixP_L')), ('0.45', D2('IN_MixP_S'))])

# 6_不確定與證據
u = _S('6_不確定與證據')
_t(u, 'C6', [('4,000', K('IN_Tau')), ('2,000', K('IN_Tau_Lo')), ('11,000', K('IN_Tau_Hi'))])
_t(u, 'C7', [('0.6', D1('IN_FreeShare')), ('0.4', D1('IN_FreeShare_Lo')), ('0.8', D1('IN_FreeShare_Hi'))])
_t(u, 'C8', [('3.2', D1('IN_Prompts_Q1')), ('3.6', D1('IN_Prompts_Q2')), ('3.8', D1('IN_Prompts_FY'))])
_t(u, 'C9', [('15', num('IN_APItpm26', '0'))])
_t(u, 'F9', [('15', num('IN_APItpm26', '0'))])
_t(u, 'C10', [('0.40', D2('IN_MixP_L')), ('0.45', D2('IN_MixP_S')), ('0.15', D2('IN_MixP_A')), ('0.10', D2('IN_MixP_A_Lo')), ('0.30', D2('IN_MixP_A_Hi'))])
_t(u, 'F10', [('5 倍', num('IN_POut_A/IN_POut_S', '0') + '&" 倍"')])
_t(u, 'C11', [('0.55', D2('IN_Chi')), ('0.3', G2('IN_Chi_Lo')), ('0.75', G2('IN_Chi_Hi')), ('16,384', K('IN_ISL_S')), ('2,048', K('IN_OSL_S'))])
_t(u, 'C12', [('1.0', D1('IN_Kappa')), ('0.65', G2('IN_Kappa_Lo')), ('1.2', G2('IN_Kappa_Hi'))])
_t(u, 'C13', [('0.5', D1('IN_Ad_Q2')), ('0.3', D1('IN_Ad_Q2_Lo')), ('0.8', D1('IN_Ad_Q2_Hi'))])
_t(u, 'C15', [('0.20', D2('IN_Disc')), ('0.1', D1('IN_Disc_Lo')), ('0.4', D1('IN_Disc_Hi'))])
_t(u, 'C16', [('0.75', D2('IN_SubTokShare')), ('0.65', D2('IN_SubTokShare26')), ('0.5', D1('MIN(IN_SubTokShare_Lo,IN_SubTokShare26_Lo)')), ('0.9', D1('MAX(IN_SubTokShare_Hi,IN_SubTokShare26_Hi)'))])
_t(u, 'C17', [('0.25', D2('IN_SeatShare_Q2'))])
_t(u, 'F7', [('0.34', D2('IN_FreeShare26'))])

import json
json.dump([list(x) for x in REPLACED], open(OUTP + '.replaced.json', 'w'), ensure_ascii=False)
print('說明句公式化', len(REPLACED), '格')

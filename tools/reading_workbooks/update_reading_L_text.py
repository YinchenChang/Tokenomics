"""L 閱讀版換版腳本（v21.4，說明句公式化）。L 閱讀版沒有建檔程式，以上一版為底稿。
用法：python3 update_reading_L_text.py <上一版L閱讀版.xlsx> <Tokenomics.xlsx> <輸出.xlsx>
輸出尚未重算；請再用 LibreOffice 重算存檔，並跑 check_reading.py。
"""
import copy, json, sys
import openpyxl
from openpyxl.workbook.defined_name import DefinedName
from formula_text import apply_text, replace_label, num, numn, pct, gen, REPLACED

SRC, TKP, OUT = sys.argv[1:4]
wb = openpyxl.load_workbook(SRC)
tkv = openpyxl.load_workbook(TKP, data_only=True)
ft, wi, w4, w0 = wb['1_公式樹'], wb['2_輸入'], wb['4_必須為真'], wb['0_說明']

# 一、2_輸入 新增第 35 列 IN_GW（Cap_In 第 331 列：2025 平均上線 GW；基準／低端／高端）
cap = tkv['Cap_In']
assert 'AL_FleetGW25' in cap['A331'].value
for col in 'ABCDEFGHI':
    s, d = wi[f'{col}34'], wi[f'{col}35']
    d.font, d.fill, d.alignment, d.number_format, d.border = (copy.copy(s.font), copy.copy(s.fill), copy.copy(s.alignment), s.number_format, copy.copy(s.border))
wi['A35'] = 'IN_GW'
wi['B35'] = '2025 平均上線 GW（AL_FleetGW25；只供說明句引用 GW 端點，所需 L 的持有成本已含在 IN_Hold）'
for col, tc in (('C', 'C'), ('D', 'D'), ('E', 'E')):
    wi[f'{col}35'] = cap[f'{tc}331'].value
wi['F35'] = 'GW'
wi['G35'] = 'Derived（貼上值）'
wi['H35'] = 'Cap_In!C331:E331（AL_FleetGW25）'
wi['I35'] = '低端 1.0、高端 1.25 是持有成本端點的 GW；本列為 v21.4 新增，只為讓說明句的 GW 數字由公式帶出'
for suf, col in (('', 'C'), ('_Lo', 'D'), ('_Hi', 'E')):
    wb.defined_names['IN_GW' + suf] = DefinedName('IN_GW' + suf, attr_text=f"'2_輸入'!${col}$35")

GWL, GWH = num('IN_GW_Lo', '0.0#'), num('IN_GW_Hi', '0.0#')
g1 = lambda ref: gen(ref) + '&" 年"'

# 二、說明句公式化（現行值）
A = lambda ws, a, subs: apply_text(ws, a, subs)
A(ft, 'B25', [('−9%', pct('IN_g'))])
A(ft, 'E30', [('−9%', pct('IN_g')), ('6', num('IN_T', '0')), ('76%', num('LS_L_price', '0%'))])
A(ft, 'E31', [('4', num('IN_T1', '0')), ('0.5', num('IN_rho', '0.0#'))])
A(ft, 'E33', [('10%', num('IN_WACC', '0%'))])
A(ft, 'E35', [('2 年', g1('C41'))])
A(ft, 'E37', [('0.660', num('C31', '0.000')), ('0.716', num('C37', '0.000')), ('0.759', num('C35', '0.000'))])
A(ft, 'E40', [('60%', num('IN_sh_H', '0%')), ('47.0', num('IN_rg_H*10', '0.0'))])
A(ft, 'E41', [('2025.5', num('IN_A', '0.0'))])
A(ft, 'E44', [('2025.5', num('IN_A', '0.0'))])
A(ft, 'E43', [('4.9', num('IN_rg_G/IN_rg_H', '0.0')), ('40%', num('IN_sh_G', '0%')), ('77%', num('C43', '0%'))])
for a in ('E49', 'E52'):
    A(ft, a, [('2 年', g1('C41')), ('0.5 年', g1('C44'))])
for a in ('E51', 'E54'):
    A(ft, a, [('−9%', pct('IN_g'))])
A(ft, 'B59', [('2025.5', num('IN_A', '0.0'))])
A(ft, 'E62', [('−9%', pct('IN_g')), ('−20%', pct('IN_g_Lo')), ('+5%', pct('IN_g_Hi', plus=True))])
A(ft, 'E63', [('0.5', num('IN_rho', '0.0#')), ('0.21', num('IN_rho_Lo', '0.0#')), ('0.7', num('IN_rho_Hi', '0.0#'))])
A(ft, 'E64', [('4', num('IN_T1', '0')), ('3', num('IN_T1_Lo', '0')), ('5', num('IN_T1_Hi', '0'))])
A(ft, 'E65', [('105.5', num('IN_Hold*10', '0.0')), ('93.5', num('IN_Hold_Lo*10', '0.0')), ('116.9', num('IN_Hold_Hi*10', '0.0'))])
A(ft, 'E66', [('130.7', num('IN_Rev*10', '0.0'))])
A(ft, 'E77', [('1.8', num('IN_SB', '0.0#')), ('0.85', num('IN_SB_Hi', '0.0#')), ('2.3', num('IN_SB_Lo', '0.0#'))])
A(ft, 'E79', [('1.8', num('IN_SB', '0.0#')), ('0.357', num('C79', '0.000'))])
A(ft, 'E80', [('75', num('IN_Spend_Lo*10', '0')), ('2.3', num('IN_SB_Lo', '0.0#')), ('88', num('IN_Spend_Hi*10', '0')), ('0.85', num('IN_SB_Hi', '0.0#'))])
A(ft, 'E81', [('1.8', num('IN_SB', '0.0#'))])
A(ft, 'E13', [('1.0', GWL), ('1.25', GWH)])
A(ft, 'E20', [('1.0', GWL)])
A(ft, 'E21', [('1.25', GWH)])
A(ft, 'B20', [('1.0', GWL)])
A(ft, 'B21', [('1.25', GWH)])
A(wi, 'I8', [('2.3', num('IN_SB_Lo', '0.0#')), ('0.85', num('IN_SB_Hi', '0.0#')), ('1.8', num('IN_SB', '0.0#')),
             ('0.85', num('IN_SB_Hi', '0.0#')), ('2.3', num('IN_SB_Lo', '0.0#'))])
A(wi, 'I14', [('−0.09', numn('IN_gpre_Lo', '0.00')), ('−0.30', numn('IN_gpre_Hi', '0.00'))])
A(wi, 'I34', [('1.0', GWL), ('1.25', GWH)])
A(w4, 'B20', [('−9%', pct('IN_gpre'))])

# 三、版本標籤與修訂紀錄
replace_label(w0, 'B1', 'v21.3', 'v21.4')
replace_label(w0, 'B2', '2026-10-24 換版到 Tokenomics v21.3', '2026-10-25 換版到 Tokenomics v21.4')
replace_label(w0, 'B2', '對 Tokenomics v21.3 逐項檢查', '對 Tokenomics v21.4 逐項檢查')
replace_label(w0, 'B2', '1_公式樹 的推導說明文字與 4_必須為真 的格點結果不在逐格核對範圍內',
              '1_公式樹 的推導說明文字：現行值數字已改為公式帶出（v21.4），check_reading.py 檢查「說明句數字」；4_必須為真 的格點結果不在逐格核對範圍內')
replace_label(w0, 'B7', 'v21.3', 'v21.4')
replace_label(w0, 'B14', '基準模型 v21.3 已合併（master aa17328，model/20261024_Tokenomics_v21.3.xlsx）',
              '基準模型 v21.4 已合併（master 3ac70ac，model/20261024_Tokenomics_v21.4.xlsx）')
replace_label(ft, 'A2', 'v21.3', 'v21.4')
replace_label(wi, 'A1', '值取自 Tokenomics v21.3（model/20261024_Tokenomics_v21.3.xlsx，master aa17328）',
              '值取自 Tokenomics v21.4（model/20261024_Tokenomics_v21.4.xlsx，master 3ac70ac）')
replace_label(wb['3_L逐世代'], 'D5', 'v21.3', 'v21.4')
N = len(REPLACED)
w0['B22'] = (f'修訂紀錄：v21.4 r0（2026-10-25）：只改呈現方式、數值不變——1_公式樹、2_輸入、4_必須為真 的說明句裡寫死的現行值數字（{N} 格）改為公式帶出，句子的顯示文字與原文相同；'
             '2_輸入 新增第 35 列 IN_GW（Cap_In 第 331 列，平均上線 GW），供 GW 端點說明句引用。歷史敘述（修訂紀錄、各版舊值）與外部事實原樣保留。'
             '對 Tokenomics v21.4（只改文字，具名範圍的值不變）重核對，check_reading.py 通過並新增「說明句數字檢查」。盤點表見 tools/reading_workbooks/text_inventory_L.csv。')
for p in ('font', 'alignment', 'fill', 'border'):
    setattr(w0['B22'], p, copy.copy(getattr(w0['B20'], p)))
w0.row_dimensions[22].height = w0.row_dimensions[20].height
wb.save(OUT)
json.dump([list(x) for x in REPLACED], open(OUT + '.replaced.json', 'w'), ensure_ascii=False)
print('公式化', N, '格')

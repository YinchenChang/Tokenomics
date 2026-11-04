# 方法三（修正）：TPU v7 規格放 Hopper 欄（非校準錨點；Hopper 原本即 FP8 服務）。只寫暫存副本。
import sys, openpyxl
sys.path.insert(0,'tests/parity')
from pathlib import Path
from parity_lib import lo_recalc
SRC=Path('model/20261103_Tokenomics_v21.9.xlsx'); OUT=Path('/home/claude/tpu_check')
pw=64*1.0850694
def make(name, edits):
    wb=openpyxl.load_workbook(SRC); ws=wb['Spec_Rack']
    for c,v in edits.items(): ws[c].value=v
    p=OUT/f'{name}_in.xlsx'; wb.save(p); return lo_recalc(p, OUT/name)
print(make('tpu_in_hopper',{'C6':64,'C8':pw,'C9':pw,'C10':pw,'C23':4.614,'C24':4.614,'C25':192,'C26':7.37,'C27':0.6,'C28':64,'C29':32,'C30':1,'C33':1000,'C40':4.614,'C41':4.614,'C12':1.6}))
# 對照：Hopper 欄放 H100 原規格（不動）＝基準檔，用來看 TK 對 Hopper 的已知低估

# 方法三試算：TK roofline 引擎代入 TPU v7 規格（放 GB300 欄）；對照：VR200 改 FP8。只寫暫存副本，不改模型。
import sys, openpyxl
sys.path.insert(0,'tests/parity')
from pathlib import Path
from parity_lib import lo_recalc
SRC=Path('model/20261103_Tokenomics_v21.9.xlsx'); OUT=Path('/home/claude/tpu_check')
def make(name, edits):
    wb=openpyxl.load_workbook(SRC); ws=wb['Spec_Rack']
    for c,v in edits.items(): ws[c].value=v
    p=OUT/f'{name}_in.xlsx'; wb.save(p); return lo_recalc(p, OUT/name)
tpu_pw=64*1.0850694  # kW/架（pod 10 MW ÷ 9,216 顆 × 64 顆）
runs={
 'tpu_in_gb300': {'E6':64,'E8':tpu_pw,'E9':tpu_pw,'E10':tpu_pw,'E22':'FP8','E23':4.614,'E24':4.614,'E25':192,'E26':7.37,'E27':0.6,'E28':64,'E30':1,'E33':1000,'E40':4.614,'E41':4.614,'E12':1.6},
 'vr200_fp8': {'F22':'FP8','F23':17.5,'F24':17.5,'F30':1,'F41':17.5},
}
for k,e in runs.items(): print(k, make(k,e))

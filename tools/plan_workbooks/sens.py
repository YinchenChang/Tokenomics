# v15.3 m 敏感度：每個輸入改到低端與高端，各以 LibreOffice 重算，讀 Cap_In!C119（L1_MFleet）
import sys,json,shutil,openpyxl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'.')
import parity_lib as pl
BASE=Path('v153.xlsx').resolve()
cases=[ # (編號, 名稱, {格:低}, {格:高})
 (1,'Astra 2025 單價',{'Cap_In!C280':3.3},{'Cap_In!C280':5.9}),
 (2,'GB200 η_d 倍數',{'Calib!D67':0.9},{'Calib!D67':1.45}),
 (3,'請求形狀 κ',{'Alloc_In!C26':0.65},{'Alloc_In!C26':1.2}),
 (4,'實際利用率',{'Alloc_In!C24':0.3},{'Alloc_In!C24':0.65}),
 (5,'計價倍數',{'Alloc_In!C23':0.73},{'Alloc_In!C23':1.17}),
 (6,'Astra 啟用參數',{'Arch!E7':60},{'Arch!E7':250}),
 (7,'有效折扣',{'Cap_In!C12':0.1},{'Cap_In!C12':0.4}),
 (8,'Sol 參考 ISL',{'Serving!D23':8192},{'Serving!D23':68000}),
 (9,'生產折減',{'Serving!C28':0.7},{'Serving!C28':1.0}),
 (10,'Sol 參考 OSL',{'Serving!D24':1024},{'Serving!D24':4096}),
 (11,'服務世代組合 Hopper',{'Alloc_In!C9':0.5,'Alloc_In!C10':0.5},{'Alloc_In!C9':0.7,'Alloc_In!C10':0.3}),
 (12,'推論支出 SRC_DEM_004',{'SRC_Demand!C8':7.5},{'SRC_Demand!C8':8.8}),
 (13,'快取命中 χ',{'Cap_In!C13':0.3},{'Cap_In!C13':0.75}),
 (14,'Sol 2025 單價',{'Cap_In!C279':1.672},{'Cap_In!C279':2.338}),
 (15,'免費占 ChatGPT token',{'Alloc_In!C16':0.4},{'Alloc_In!C16':0.8}),
 (16,'WACC',{'Inputs!E28':0.08},{'Inputs!E28':0.13}),
 (17,'η_p',{'Calib!C5':0.15},{'Calib!C5':0.45}),
 (18,'每則提示 token τ',{'Alloc_In!C15':2000},{'Alloc_In!C15':11000}),
 (19,'Hopper η_d 倍數',{'Calib!C67':0.8},{'Calib!C67':1.6}),
 (20,'基準利用率 IF_Util',{'Serving!C17':0.4},{'Serving!C17':0.8}),
 (21,'付費層級組合',{'Cap_In!C31':0.5,'Cap_In!D31':0.4,'Cap_In!E31':0.1},{'Cap_In!C31':0.3,'Cap_In!D31':0.5,'Cap_In!E31':0.2}),
 (22,'Hopper 每層延遲倍數',{'Calib!C68':1.0},{'Calib!C68':1.5}),
 (23,'Luna 2025 單價',{'Cap_In!C278':0.0669},{'Cap_In!C278':0.3026}),
 (24,'Hopper 機架單價',{'Spec_Rack!C12':0.9},{'Spec_Rack!C12':1.3}),
 (25,'GB200 機架單價',{'Spec_Rack!D12':2.8},{'Spec_Rack!D12':3.4}),
 (26,'API 全年平均比',{'Alloc_In!C14':0.6},{'Alloc_In!C14':0.9}),
 (27,'GB200 批次 η_d（不進機隊）',{'Calib!D156':1.59},{'Calib!D156':2.64}),
]
jobs=[]
for no,name,lo,hi in cases:
    jobs.append((no,'lo',lo)); jobs.append((no,'hi',hi))
jobs.append((0,'base',{}))
work=Path('sens_work'); work.mkdir(exist_ok=True)
def run(job):
    no,side,inp=job
    src=work/f'c{no}_{side}.xlsx'
    if inp: pl.set_inputs(BASE,src,inp)
    else: shutil.copy(BASE,src)
    out=pl.lo_recalc(src,work/f'o{no}_{side}')
    wb=openpyxl.load_workbook(out,data_only=True,read_only=True)
    v=wb['Cap_In']['C119'].value
    s=wb['Cap_In']['C242'].value
    return no,side,v,s
res={}
with ThreadPoolExecutor(3) as ex:
    for no,side,v,s in ex.map(run,jobs):
        res[f'{no}_{side}']=[v,s]; print(no,side,v,flush=True)
json.dump({'cases':[[c[0],c[1],c[2],c[3]] for c in cases],'res':res},open('sens.json','w'),ensure_ascii=False)
print('done')

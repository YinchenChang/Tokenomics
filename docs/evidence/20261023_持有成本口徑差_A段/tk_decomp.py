# 讀 model/CURRENT 活頁簿（LibreOffice 已重算的快取值），拆解每 GW(IT) 年經濟持有成本
import openpyxl, json, sys
f='model/'+open('model/CURRENT').read().strip()
wb=openpyxl.load_workbook(f,data_only=True)
dc=wb['DC_Cost']; inp=wb['Inputs']
gens={'Hopper':'D','GB200':'G','GB300':'J','VR200':'M'}
crf=lambda w,n: w/(1-(1+w)**-n)
w=inp['E28'].value
fac_life={'建物與基地':('26','E24'),'電力設施':('27','E25'),'機械與散熱':('28','E26'),'光纖與保全':('29','E27')}
out={'file':f,'WACC':w,'IT_life':inp['E23'].value,'PUE':inp['E9'].value,'gens':{}}
for g,c in gens.items():
    d={}
    def cell(r): return dc[f'{c}{r}'].value
    d['rack_capex']=(cell(19),f'DC_Cost!{c}19')
    d['net_capex']=(cell(21),f'DC_Cost!{c}21')
    d['stor_capex']=(cell(23),f'DC_Cost!{c}23')
    d['IT_capex']=(cell(24),f'DC_Cost!{c}24')
    d['fac_capex']=(cell(32),f'DC_Cost!{c}32')
    d['CRF_IT']=(cell(52),f'DC_Cost!{c}52')
    d['IT_annuity']=(cell(53),f'DC_Cost!{c}53')
    d['fac_annuity']=(cell(54),f'DC_Cost!{c}54')
    d['power']=(cell(43),f'DC_Cost!{c}43')
    d['IT_maint']=(cell(44),f'DC_Cost!{c}44')
    d['fac_maint']=(cell(45),f'DC_Cost!{c}45')
    d['staff_sw_water']=(cell(46),f'DC_Cost!{c}46')
    d['tax_ins']=(cell(47),f'DC_Cost!{c}47')
    d['opex']=(cell(48),f'DC_Cost!{c}48')
    d['total']=(cell(55),f'DC_Cost!{c}55')
    # 廠房年金分項（複算）
    c_=f'{c}'
    cont=cell(30)
    parts={}
    for k,(r,lifecell) in fac_life.items():
        parts[k]=cell(int(r))*crf(w,inp[lifecell].value)*(1+cont)
    parts['土地(按WACC)']=cell(25)*w
    d['fac_parts']=parts
    out['gens'][g]=d
mix={'Hopper':wb['Alloc_In']['C9'].value,'GB200':wb['Alloc_In']['C10'].value,'GB300':wb['Alloc_In']['C11'].value,'VR200':wb['Alloc_In']['C12'].value}
out['mix']=mix
out['blend_AL_FleetHold']=wb['Alloc']['C157'].value
out['blend_L1_HoldFleet25']=wb['L1']['D137'].value
out['AL_FleetGW25']=wb['Cap_In']['C331'].value
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False,indent=1)
for g,d in out['gens'].items():
    print(g,{k:round(v[0],4) for k,v in d.items() if k!='fac_parts'}, 'chk',round(d['IT_annuity'][0]+d['fac_annuity'][0]+d['opex'][0],4), 'facparts',round(sum(d['fac_parts'].values()),4))
print(mix,out['blend_AL_FleetHold'],sum(mix[g]*out['gens'][g]['total'][0] for g in mix), out['AL_FleetGW25'], out['blend_L1_HoldFleet25'])

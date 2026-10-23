# 建 20261023_持有成本口徑差_A段.xlsx（五頁）。TK 數值讀自 model/CURRENT 活頁簿；其餘為外部證據輸入。
# 計算一律用 Excel 公式，藍字＝輸入，黑字＝公式。
import openpyxl, sys
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
MODEL='model/'+open('model/CURRENT').read().strip()
m=openpyxl.load_workbook(MODEL,data_only=True)
dc,inp,sp,al=m['DC_Cost'],m['Inputs'],m['Spec_Rack'],m['Alloc_In']
wb=openpyxl.Workbook()
BLUE=Font(color='0000FF'); BOLD=Font(bold=True); HDR=PatternFill('solid',fgColor='DDEBF7'); SEC=PatternFill('solid',fgColor='F2F2F2'); WARN=PatternFill('solid',fgColor='FFF2CC')
def hdr(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=BOLD; c.fill=HDR; c.alignment=Alignment(wrap_text=True,vertical='top')
def sec(ws,r,t,n=10):
    for i in range(1,n+1): ws.cell(r,i).fill=SEC
    ws.cell(r,1,t).font=BOLD
# ---------------- 頁 1 TK 拆解 ----------------
t=wb.active; t.title='TK 拆解'
t['A1']='Tokenomics 每 IT-GW·年 經濟口徑持有成本拆解（$B/GW·年）'; t['A1'].font=Font(bold=True,size=13)
t['A2']=f'來源活頁簿：{MODEL}（model/CURRENT）。藍字＝自模型讀入的輸入（附儲存格位置）；黑字＝本頁公式重算；「模型值」列為 DC_Cost!第55列，差列應為 0。GW 口徑＝IT 關鍵電力（CLAUDE.md 第 7 節）。'
hdr(t,4,['項目','單位','Hopper H100','GB200 NVL72','GB300 NVL72','VR200 NVL72','2025 機隊組合（0.6/0.4）','模型儲存格位置','標記','說明'])
gc=['C','D','E','F']; dcg=['D','G','J','M']; spc=['C','D','E','F']
R={}
def row(r,key,label,unit,vals=None,formula=None,loc='',tag='',note='',fmt='0.0000',blend=None,same=False):
    R[key]=r; t.cell(r,1,label); t.cell(r,2,unit)
    for i,c in enumerate(gc):
        if vals is not None:
            v=vals[i] if isinstance(vals,(list,tuple)) else vals
            if same and i>0: cell=t[f'{c}{r}']; cell.value=f'=$C{r}'
            else: cell=t[f'{c}{r}']; cell.value=v; cell.font=BLUE
        else:
            t[f'{c}{r}']=formula.replace('{c}',c)
        t[f'{c}{r}'].number_format=fmt
    if blend=='sp': t[f'G{r}']=f'=SUMPRODUCT($C$6:$F$6,C{r}:F{r})'; t[f'G{r}'].number_format=fmt
    elif blend: t[f'G{r}']=blend; t[f'G{r}'].number_format=fmt
    t.cell(r,8,loc); t.cell(r,9,tag); t.cell(r,10,note)
sec(t,5,'A. 輸入（自模型讀入）')
row(6,'mix','服務世代組合（2025 全年平均）','%',[al[f'C{i}'].value for i in (9,10,11,12)],loc='Alloc_In!C9:C12',tag='Derived',note='3A 查證 Q1；Blackwell 自 Q2 線性爬升',fmt='0.00')
t['G6']='=SUM(C6:F6)'
row(7,'MW','IT 電力','MW',inp['E5'].value*1000,loc='Inputs!E5×1000',tag='Decision',same=True,fmt='0')
row(8,'nonrack','機架外 IT 電力占比','%',inp['E8'].value,loc='Inputs!E8',tag='Assumed',same=True,fmt='0.00')
row(9,'PUE','PUE','x',inp['E9'].value,loc='Inputs!E9',tag='Analogy（區間 1.1–1.3）',same=True,fmt='0.00')
row(10,'W','WACC','%',inp['E28'].value,loc='Inputs!E28',tag='Assumed（區間 8–13%）',same=True,fmt='0.00%')
row(11,'life','IT 折舊年限','年',inp['E23'].value,loc='Inputs!E23',tag='Verified（區間 4–6）',same=True,fmt='0')
row(12,'kw','每架配電設計功率（基準）','kW',[sp[f'{c}9'].value for c in spc],loc='Spec_Rack!C9:F9',tag='Verified/Analogy',fmt='0')
row(13,'gpr','GPU 封裝／架','顆',[sp[f'{c}6'].value for c in spc],loc='Spec_Rack!C6:F6',tag='Verified',fmt='0')
row(14,'rackpx','機架單價（基準）','$M',[sp[f'{c}12'].value for c in spc],loc='Spec_Rack!C12:F12',tag='Analogy',fmt='0.0')
row(15,'netp','Scale-out 網路 ÷ 機架價格','%',inp['E13'].value,loc='Inputs!E13',tag='Analogy（5–15%）',same=True,fmt='0.00')
row(16,'stor','儲存與管理','$/GPU',inp['E14'].value,loc='Inputs!E14',tag='Assumed（300–800）',same=True,fmt='0')
row(17,'util','平均用電 ÷ 配電設計功率','%',inp['E10'].value,loc='Inputs!E10',tag='Assumed（0.7–0.9）',same=True,fmt='0.00')
row(18,'pxkwh','電價','$/kWh',inp['E11'].value,loc='Inputs!E11',tag='Verified/Analogy',same=True,fmt='0.000')
row(19,'itmr','IT 維護費率（壽命期等值）','%/年',inp['E30'].value,loc='Inputs!E30',tag='Derived',same=True,fmt='0.0000%',note='0.5% 保固期內 3 年、3% 保固後；以 WACC 折現成單一費率')
row(20,'fmr','廠房維護率','%/年',inp['E31'].value,loc='Inputs!E31',tag='Analogy',same=True,fmt='0.00%')
row(21,'staff','站點營運（人員＋軟體＋水耗材）','$B/GW·年',(inp['E32'].value*1000/1000+inp['E33'].value*1000/1000+inp['E34'].value*1000)/1000,loc='Inputs!E32:E34',tag='Assumed',same=True,fmt='0.000',note='人員 75＋軟體 200＋水耗材 50 $M/GW·年')
row(22,'taxr','財產稅與保險率','%/年（總資本）',inp['E35'].value,loc='Inputs!E35',tag='Analogy',same=True,fmt='0.00%')
row(23,'land','土地','$M/MW',inp['E16'].value,loc='Inputs!E16',tag='Assumed',same=True,fmt='0.000')
row(24,'bldg','建物與基地','$M/MW',inp['E17'].value,loc='Inputs!E17',tag='Assumed（JLL 校準）',same=True,fmt='0.00')
row(25,'pwr','電力設施','$M/MW',inp['E18'].value,loc='Inputs!E18',tag='Assumed',same=True,fmt='0.00')
row(26,'mech','機械與散熱','$M/MW',inp['E19'].value,loc='Inputs!E19',tag='Assumed',same=True,fmt='0.00')
row(27,'fib','光纖、佈線、保全','$M/MW',inp['E20'].value,loc='Inputs!E20',tag='Assumed',same=True,fmt='0.00')
row(28,'cont','設計、管理與預備費率','%',inp['E21'].value,loc='Inputs!E21',tag='Assumed',same=True,fmt='0.00')
row(29,'Lb','建物年限','年',inp['E24'].value,loc='Inputs!E24',tag='Analogy',same=True,fmt='0')
row(30,'Lp','電力設施年限','年',inp['E25'].value,loc='Inputs!E25',tag='Analogy',same=True,fmt='0')
row(31,'Lm','機械與散熱年限','年',inp['E26'].value,loc='Inputs!E26',tag='Analogy',same=True,fmt='0')
row(32,'Lf','光纖與保全年限','年',inp['E27'].value,loc='Inputs!E27',tag='Analogy',same=True,fmt='0')
sec(t,33,'B. 規模與資本支出（$B／GW IT）')
row(34,'racks','機架數','架',formula='=FLOOR({c}7*(1-{c}8)*1000/{c}12,1)',loc='DC_Cost!第12列',fmt='#,##0',blend='sp')
row(35,'gpus','GPU 數','顆',formula='={c}34*{c}13',loc='DC_Cost!第14列',fmt='#,##0',blend='sp',note='外部價格換算頁用此數把「每 GPU 小時」轉成「每 GW」')
row(36,'cap_rack','機架 capex','$B',formula='={c}34*{c}14/1000',loc='DC_Cost!第19列',blend='sp')
row(37,'cap_net','Scale-out 網路 capex','$B',formula='={c}36*{c}15',loc='DC_Cost!第21列',blend='sp')
row(38,'cap_stor','儲存與管理 capex','$B',formula='={c}35*{c}16/1000000000',loc='DC_Cost!第23列',blend='sp')
row(39,'cap_it','IT 設備 capex 小計','$B',formula='={c}36+{c}37+{c}38',loc='DC_Cost!第24列',blend='sp')
row(40,'cap_land','土地','$B',formula='={c}7*{c}23/1000',loc='DC_Cost!第25列',blend='sp')
row(41,'cap_b','建物與基地','$B',formula='={c}7*{c}24/1000',loc='DC_Cost!第26列',blend='sp')
row(42,'cap_p','電力設施','$B',formula='={c}7*{c}25/1000',loc='DC_Cost!第27列',blend='sp')
row(43,'cap_m','機械與散熱','$B',formula='={c}7*{c}26/1000',loc='DC_Cost!第28列',blend='sp')
row(44,'cap_f','光纖與保全','$B',formula='={c}7*{c}27/1000',loc='DC_Cost!第29列',blend='sp')
row(45,'cap_c','設計、管理與預備費','$B',formula='=({c}41+{c}42+{c}43+{c}44)*{c}28',loc='DC_Cost!第31列',blend='sp')
row(46,'cap_fac','廠房 capex 小計','$B',formula='=SUM({c}40:{c}45)',loc='DC_Cost!第32列',blend='sp')
row(47,'cap_tot','總 capex（IT＋廠房）','$B',formula='={c}39+{c}46',loc='DC_Cost!第33列',blend='sp')
row(48,'cap_mw','每 MW IT 總 capex','$M/MW',formula='={c}47*1000/{c}7',loc='DC_Cost!第35列',blend='sp',fmt='0.00',note='對照 Epoch Abilene 資本成本 15.9B／421 MW IT ＝ 37.8 $M/MW')
sec(t,49,'C. 年持有成本（經濟口徑；$B／GW IT·年）')
CRF='{c}10/(1-(1+{c}10)^(-{c}11))'
row(50,'a_it','IT 資本回收（年金）','$B',formula='={c}39*'+CRF,loc='DC_Cost!第53列',blend='sp')
row(51,'a_rack','  其中機架','$B',formula='={c}36*'+CRF,blend='sp')
row(52,'a_net','  其中網路','$B',formula='={c}37*'+CRF,blend='sp')
row(53,'a_stor','  其中儲存','$B',formula='={c}38*'+CRF,blend='sp')
def ann(x,Lc): return f'{{c}}{x}*{{c}}10/(1-(1+{{c}}10)^(-{{c}}{Lc}))*(1+{{c}}28)'
row(54,'a_fac','廠房資本回收（年金；土地按 WACC）','$B',formula='='+'+'.join([ann(41,29),ann(42,30),ann(43,31),ann(44,32)])+'+{c}40*{c}10',loc='DC_Cost!第54列',blend='sp')
row(55,'a_b','  其中建物（含預備費）','$B',formula='='+ann(41,29),blend='sp')
row(56,'a_p','  其中電力設施（含預備費）','$B',formula='='+ann(42,30),blend='sp')
row(57,'a_m','  其中機械散熱（含預備費）','$B',formula='='+ann(43,31),blend='sp')
row(58,'a_f','  其中光纖保全（含預備費）','$B',formula='='+ann(44,32),blend='sp')
row(59,'a_l','  其中土地（機會成本）','$B',formula='={c}40*{c}10',blend='sp')
row(60,'o_pw','電費','$B',formula='={c}7*1000*{c}17*{c}9*8760*{c}18/1000000000',loc='DC_Cost!第43列',blend='sp',note='設施電力＝IT×PUE；平均負載 80%')
row(61,'o_it','IT 維護','$B',formula='={c}39*{c}19',loc='DC_Cost!第44列',blend='sp')
row(62,'o_fm','廠房維護','$B',formula='={c}46*{c}20',loc='DC_Cost!第45列',blend='sp')
row(63,'o_st','站點營運（人員、軟體、水、耗材）','$B',formula='={c}21',loc='DC_Cost!第46列',blend='sp')
row(64,'o_tx','財產稅與保險','$B',formula='={c}47*{c}22',loc='DC_Cost!第47列',blend='sp')
row(65,'o_tot','營運費用小計（不含折舊）','$B',formula='=SUM({c}60:{c}64)',loc='DC_Cost!第48列',blend='sp')
row(66,'hold','年持有成本（經濟口徑）＝IT 年金＋廠房年金＋營運','$B/GW·年',formula='={c}50+{c}54+{c}65',loc='DC_Cost!第55列；組合＝Alloc!C157（AL_FleetHold）',blend='sp')
for c in 'CDEFG': t[f'{c}66'].font=BOLD
row(67,'mv','模型值（DC_Cost 第55列；G 欄＝Alloc!C157）','$B/GW·年',[dc[f'{c}55'].value for c in dcg],loc='DC_Cost!D55,G55,J55,M55；Alloc!C157',tag='Verified（模型快取值）',blend=None)
t['G67']=al.parent['Alloc']['C157'].value; t['G67'].font=BLUE; t['G67'].number_format='0.0000'
row(68,'diff','差（本頁公式 − 模型值）','$B',formula='={c}66-{c}67',blend='=G66-G67',fmt='0.0E+00',note='應為 0（浮點誤差內）')
sec(t,69,'D. 結構占比')
row(70,'s_it','IT 資本回收占比','%',formula='={c}50/{c}66',blend='=G50/G66',fmt='0.0%')
row(71,'s_fac','廠房資本回收占比','%',formula='={c}54/{c}66',blend='=G54/G66',fmt='0.0%')
row(72,'s_pw','電費占比','%',formula='={c}60/{c}66',blend='=G60/G66',fmt='0.0%')
row(73,'s_mt','維護（IT＋廠房）占比','%',formula='=({c}61+{c}62)/{c}66',blend='=(G61+G62)/G66',fmt='0.0%')
row(74,'s_ot','其他營運（站點＋稅保）占比','%',formula='=({c}63+{c}64)/{c}66',blend='=(G63+G64)/G66',fmt='0.0%')
row(75,'s_cap','資本回收合計占比','%',formula='=({c}50+{c}54)/{c}66',blend='=(G50+G54)/G66',fmt='0.0%')
row(76,'phr','每 GPU 小時持有成本（經濟）','$/GPU-hr',formula='={c}66*1000000000/({c}35*8760)',blend='=G66*1000000000/(G35*8760)',fmt='0.000',note='組合欄＝加權成本 ÷ 加權 GPU 數（總成本 ÷ 總 GPU 小時；非 $/hr 直接加權 1.729）')
sec(t,77,'E. 敏感度：同一資本結構下，持有成本隨 WACC 與 IT 年限的變化（營運費用固定；IT 維護率不隨 WACC 重算）')
hdr(t,78,['情境','','Hopper','GB200','GB300','VR200','組合 0.6/0.4','','WACC','IT 年限'])
sens=[('WACC 3.31%（IREN GPU 融資平均成本）',0.0331,6),('WACC 5%',0.05,6),('WACC 8%（模型低端）',0.08,6),('WACC 10%（基準）',0.10,6),('WACC 13%（模型高端）',0.13,6),('WACC 10%、IT 年限 5 年（對齊 5 年合約）',0.10,5),('WACC 8%、IT 年限 5 年',0.08,5),('WACC 3.31%、IT 年限 5 年',0.0331,5)]
for i,(lab,w,n) in enumerate(sens):
    r=79+i; t.cell(r,1,lab); t.cell(r,2,'$B/GW·年'); t.cell(r,9,w).font=BLUE; t.cell(r,10,n).font=BLUE; t.cell(r,9).number_format='0.00%'
    for c in gc:
        fac='+'.join([f'{c}{x}*$I{r}/(1-(1+$I{r})^(-{c}{Lc}))*(1+{c}28)' for x,Lc in((41,29),(42,30),(43,31),(44,32))])+f'+{c}40*$I{r}'
        t[f'{c}{r}']=f'={c}39*$I{r}/(1-(1+$I{r})^(-$J{r}))+{fac}+{c}65'; t[f'{c}{r}'].number_format='0.000'
    t[f'G{r}']=f'=SUMPRODUCT($C$6:$F$6,C{r}:F{r})'; t[f'G{r}'].number_format='0.000'
t.column_dimensions['A'].width=46; t.column_dimensions['B'].width=12
for c in 'CDEFG': t.column_dimensions[c].width=14
t.column_dimensions['H'].width=34; t.column_dimensions['I'].width=22; t.column_dimensions['J'].width=60
t.freeze_panes='C5'
TK=lambda key,c: f"'TK 拆解'!{c}{R[key]}"
# ---------------- 頁 2 外部價格換算 ----------------
e=wb.create_sheet('外部價格換算')
e['A1']='外部價格 → 每 IT-GW·年（$B）換算，及其包含／不包含的項目'; e['A1'].font=Font(bold=True,size=13)
e['A2']='藍字＝外部證據輸入（出處見「證據」頁 ID）；黑字＝公式。倍數＝外部價 ÷ TK 同口徑持有成本（分母指定於「對照 TK」欄）。'
H=['ID','項目','總額／數值','單位','年數／係數','容量（GW）','容量口徑','→ 每年 $B','→ 每 IT-GW·年 $B（點估）','低','高','對照 TK 項','TK 值','倍數（點估）','倍數 低','倍數 高','電費','廠房','網路／儲存','維運','出租方利潤／毛利','利用率／付款假設','GPU 世代','標記','品質與限制','證據 ID']
hdr(e,4,H)
E={}
def erow(r,key,vals):
    E[key]=r
    for i,v in enumerate(vals,1):
        if v is None: continue
        c=e.cell(r,i,v)
        if i in(3,5,6) and not (isinstance(v,str) and v.startswith('=')): c.font=BLUE
        if i in(8,9,10,11,13): c.number_format='0.00'
        if i in(14,15,16): c.number_format='0.00'
        c.alignment=Alignment(wrap_text=True,vertical='top')
sec(e,5,'A. 合約／財報營收型（已是每年金額，除以容量）',26)
# IREN
erow(6,'iren',['X1','IREN–Microsoft（2025-11-03；GB300；5 年）',9.7,'$B 合約總額',5,0.2,'IT（約 200MW critical IT load）','=C6/E6','=H6/F6','=I6','=I6','GB300（E 欄）',f'={TK("hold","E")}','=I6/M6','=J6/M6','=K6/M6',
  '含：EBITDA 85% 定義為扣除電力、維修與直接營運成本，故電費由 IREN 負擔（公司估計）','含：IREN 自建 Childress Horizon 1–4（含電力、冷卻）','含：GPU 與輔助設備（Dell 約 $5.8B）','含','含；公司估計專案 EBITDA 85%（資本前）；20% 預付款於第 3–5 年抵扣（現金時點，非降價）','5 年固定期限；Microsoft 可因延遲交付終止；未披露保證利用率','GB300','Verified（公司 8-K／新聞稿）；利害關係：賣方','高：IT 口徑明確、單一原始來源（各媒體轉述同一份公告）。5 年合約短於 GPU 經濟壽命，殘值歸出租方。','E1–E3'])
# CoreWeave
erow(7,'crwv_a',['X2a','CoreWeave 2025Q4 營收年化 ÷ 平均 active power（照字面當 IT）',1.572,'$B 季營收',4,'=(590+850)/2/1000','不明（active power 定義未找到）；590 為由「+260 → >850」反推','=C7*E7','=H7/F7','=I7','=I7','2025 組合 0.6/0.4（G 欄）',f'={TK("hold","G")}','=I7/M7','=J7/M7','=K7/M7',
  '含','含（CoreWeave 自租／自建混合，租賃費用在其成本內）','含','含','含；Q4 調整後營業利益率 6%、GAAP 營業虧損 $89M','包含新容量爬坡期（電已通但尚未計費）→ 營收偏低；承諾使用量不明','Hopper 為主＋GB200 爬坡（推測，未揭露）','Verified（營收、MW 為公司揭露）；平均 MW 為 Derived','中低：全公司彙總、混合世代、MW 為期初期末平均','E4–E5'])
erow(8,'crwv_b',['X2b','同上，若 active power 為設施口徑，換成 IT（÷PUE 1.2）',1.572,'$B 季營收',4,'=(590+850)/2/1000/\'TK 拆解\'!C9','IT（由設施換算；假設）','=C8*E8','=H8/F8','=I8','=I8','2025 組合 0.6/0.4（G 欄）',f'={TK("hold","G")}','=I8/M8','=J8/M8','=K8/M8','同 X2a','同 X2a','同 X2a','同 X2a','同 X2a','同 X2a','同 X2a','Derived（口徑假設 Assumed）','中低：僅用於區間上端','E4–E5'])
# Nebius MSFT
erow(9,'neb_ms',['X3','Nebius–Microsoft（2025-09；5 年；基本 $17.4B，含選擇權 $19.4B）— 下界',17.4,'$B 合約總額',5,0.3,'未明（Vineland 目標 300MW，單一來源 GCN）','=C9/E9','=H9/F9','=I9','=I9*19.4/17.4','GB300（E 欄；世代未揭露）',f'={TK("hold","E")}','=I9/M9','=J9/M9','=K9/M9','不明','不明','不明（專屬 GPU 容量）','不明','不明','分階段 2025–2026 上線，分子含未上線期間','未揭露','Interested-party（Nebius 公告／媒體）','只是下界：合約容量 ≤ 300MW 且未計爬坡；300MW 只見單一來源。不進分布。','E6'])
erow(10,'neb_new',['X4a','Nebius 2026Q2 新簽四筆合約收益率（營收認列基礎）',20,'$M／MW·年',1,0.001,'未明（每 MW 未說 IT 或設施）','=C10*E10/1000','=H10/F10','=C10','=25','GB300（E 欄）',f'={TK("hold","E")}','=I10/M10','=J10/M10','=K10/M10','不明','不明','不明（全含雲服務）','不明','不明；客戶為 Reflection、Cohere 等非 hyperscaler，信用風險溢價','預付款涵蓋 capex 50–60%（不計入營收認列）','未揭露（2026 簽）','Interested-party（管理層電話會議；二手轉述）','不可直接比：2026 年定價、非投資級客戶、含預付款融資。顯示 2026 年定價已高於 2025 年合約。','E7'])
erow(11,'neb_st',['X4b','Nebius 短期（≤6 個月）議價中的收益率',40,'$M／MW·年',1,0.001,'未明','=C11*E11/1000','=H11/F11','=C11','=50','GB300（E 欄）',f'={TK("hold","E")}','=I11/M11','=J11/M11','=K11/M11','不明','不明','不明','不明','不明','短約，非 take-or-pay 長約','未揭露','Interested-party（管理層；「議價中」非已簽）','僅作現貨端參考；非合約價。','E7'])
erow(12,'orc_f',['X5a','Oracle–OpenAI（WSJ 轉述：約 $300B／5 年，4.5GW，2027 起）— 4.5GW 當設施口徑，換 IT',300,'$B 合約總額',5,'=4.5/\'TK 拆解\'!C9','設施 4.5GW ÷ PUE 1.2 ＝ IT','=C12/E12','=H12/F12','=C12/E12/4.5','=I12','VR200（F 欄；2027 起交付世代，Assumed）',f'={TK("hold","F")}','=I12/M12','=J12/M12','=K12/M12','含（Oracle 轉租整套設施）','含','含','含','含；Oracle AI 雲毛利「極薄」（2020 年代報導 ≈ 16%，單一轉述，見 20261020 筆記）','合約總額含爬坡與選擇權不明；非 SEC 具約束揭露','2027 起；世代未揭露','Interested-party（匿名消息；Oracle 未逐項確認）','低：口徑（IT／設施）與爬坡未明；$60B／年是除法，非揭露數字。','E8'])
erow(13,'orc_i',['X5b','同上，4.5GW 當 IT 口徑',300,'$B 合約總額',5,4.5,'IT','=C13/E13','=H13/F13','=I13','=I13','VR200（F 欄）',f'={TK("hold","F")}','=I13/M13','=J13/M13','=K13/M13','同 X5a','同 X5a','同 X5a','同 X5a','同 X5a','同 X5a','同 X5a','Interested-party','低','E8'])
erow(14,'orc_30',['X5c','Oracle–OpenAI 早期報導：年約 $30B／4.5GW（與 X5a 的 $60B／年互相矛盾，未解）',30,'$B／年',1,'=4.5/\'TK 拆解\'!C9','設施 ÷ PUE ＝ IT','=C14/E14','=H14/F14','=C14/4.5','=H14/F14','VR200（F 欄；與規格一致，世代實際未揭露）',f'={TK("hold","F")}','=I14/M14','=J14/M14','=K14/M14','含','含','含','含','含','同 X5a','GB200 為主（推測）','Interested-party（匿名消息）','低：與 X5a 差一倍，哪個為真未知；列出僅為完整。','E8'])
sec(e,15,'B. 支出 ÷ 機隊 GW 型（不是價格）',26)
erow(16,'epoch_user',['X6a','OpenAI 2025 雲端算力支出 $16.3B ÷ 1.25GW（使用者算式；1.25GW 來源未知）',16.3,'$B／年（研究＋訓練＋推論）',1,1.25,'未明（Epoch 資料集口徑未確認）','=C16/E16','=H16/F16','=H16/1.5','=H16/1.0','2025 組合 0.6/0.4（G 欄）',f'={TK("hold","G")}','=I16/M16','=J16/M16','=K16/M16','視供應商','視供應商','視供應商','視供應商','視供應商；含 Microsoft 授予的非現金 Azure 額度（The Register 提醒）','支出不等於已用容量；含預留與預付','Hopper＋GB200','Interested-party（二手；OpenAI 內部文件轉述）','低：這是「花多少」÷「平均多少 GW」，不是單價；分母與分子時間窗不一定一致。低／高欄為分母 1.5／1.0GW 的敏感度（Assumed）。','E9'])
erow(17,'epoch_tk',['X6b','同上，分母改用模型 AL_FleetGW25（2025 平均上線 GW，指數內插 0.6→1.9）',16.3,'$B／年',1,m['Cap_In']['C331'].value,'模型 Cap_In!C331（Derived）','=C17/E17','=H17/F17','=I17','=I17','2025 組合 0.6/0.4（G 欄）',f'={TK("hold","G")}','=I17/M17','=J17/M17','=K17/M17','同 X6a','同 X6a','同 X6a','同 X6a','同 X6a','同 X6a','同 X6a','Derived','低：與 X6a 同。','E9'])
erow(18,'epoch_capex',['X6c','（對照，不是價格）Epoch Abilene 資本成本 $15.9B ÷ 421MW IT → $M／MW IT',15.9,'$B 資本成本（Epoch 估計）',1,0.421,'IT（Epoch 頁面未精確定義 IT power）','=C18/E18','=H18/F18','=I18','=I18','TK GB200 每 MW IT 總 capex（D 欄，$M）',f'={TK("cap_mw","D")}','=I18/M18','=J18/M18','=K18/M18','—','含（Epoch 資本成本口徑未詳）','含','—','—','—','B200／GB200（Epoch 估計）','Derived／Analogy（衛星影像＋冷卻模型的估計）','此列單位是 $M／MW 的 capex，不是年價；用來檢查 TK 資本支出，不進價格倍數。⚠ 與 X6a 的 $16B 是兩個不同的量。','E10'])
e.cell(18,8).number_format='0.00'
sec(e,19,'C. GPU 小時價 → 每 IT-GW·年（價格 × TK 每 GW GPU 數 × 8760 ×利用率）',26)
G=lambda c: TK('gpus',c)
def hr(r,key,iid,name,price,gen_c,gen_name,tag,qual,eid,lo=0.7,hi=1.0,incl='不明（零售／指數價）'):
    erow(r,key,[iid,name,price,'$/GPU-hr',8760,f'={G(gen_c)}/1000000000','GPU 數／GW 為 TK 值（IT GW）；單位＝十億顆',f'=C{r}*E{r}*F{r}',f'=H{r}*{hi}',f'=H{r}*{lo}',f'=H{r}*{hi}',f'{gen_name}（{gen_c} 欄）',f'={TK("hold",gen_c)}',f'=I{r}/M{r}',f'=J{r}/M{r}',f'=K{r}/M{r}',incl,incl,incl,incl,'含出租方利潤','低／高＝利用率 0.7／1.0（Assumed）','',tag,qual,eid])
    e.cell(r,7).value='TK 每 IT-GW GPU 數（見 TK 拆解第35列）'
    e.cell(r,6).number_format='0.0000'
hr(20,'h_sd','X7a','H100：Silicon Data 新雲指數 2026-10-22',2.53,'C','Hopper','Interested-party（指數商）','中：跨供應商標準化現貨型指數，2026 年 10 月；2025 年同期較低（報導 2025-10→2026-03 漲約 40%）','E11')
hr(21,'h_ornn','X7b','H100：Ornn OCPI 成交結算價 2026-10-22',3.15,'C','Hopper','Interested-party（指數商）','中：成交價，但單日、短約','E11')
hr(22,'h_cw','X7c','H100：CoreWeave 公開牌價 HGX H100',6.16,'C','Hopper','Interested-party（賣方牌價）','低：牌價；大客戶多簽多年約，不付牌價','E12')
hr(23,'h_lam','X7d','H100：Lambda 隨選',3.29,'C','Hopper','Interested-party（賣方牌價）','低：牌價（另一來源 $3.99）','E12')
hr(24,'g200_cw','X7e','GB200 NVL72：CoreWeave 牌價 $42/4 GPU',10.5,'D','GB200','Interested-party（賣方牌價）','低：牌價','E12')
hr(25,'g200_bit','X7f','GB200：Bitdeer 3 年預留（彙整站列價）',5.0,'D','GB200','Interested-party（彙整站，未對照原頁）','低：單一彙整站列價','E13')
hr(26,'g300_ns','X7g','GB300：Nscale–Microsoft Narvik 隱含 $6.2B／5 年／52,000 GPU（第三方推算）','=6200000000/5/52000/8760','E','GB300','Derived（CV Research Substack 推算；合約價非原文）','低中：單一第二手；用 TK 每 GW GPU 數換算，若 Nscale 實際 kW／GPU 不同則偏','E14',incl='不明；含 Microsoft 長約')
hr(27,'g300_stn','X7h','GB300：STN 3 年預留（彙整站列價）',7.15,'E','GB300','Interested-party（彙整站）','低','E13')
# 說明
e['A29']='註：B200／B300 單卡價（Silicon Data 5.93／6.71、Ornn 9.32）未換算，因 TK 世代欄位為 NVL72 機架且 B200 HGX 的每 GW GPU 數不同（缺 B200 HGX 的 kW／機架輸入）。'
e['A30']='註：X7 列的「低／高」＝利用率 0.7／1.0。長約 take-or-pay 以 1.0 為宜；隨選／現貨應打折。'
for c,w in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',[6,48,10,16,9,10,28,10,12,8,8,24,9,10,9,9,34,34,26,12,34,30,18,22,44,8]): e.column_dimensions[c].width=w
e.freeze_panes='C5'
EX=lambda key,c: f"'外部價格換算'!{c}{E[key]}"
# ---------------- 頁 3 對帳 ----------------
q=wb.create_sheet('對帳')
q['A1']='對帳：TK 拆解項 × 外部價格'; q['A1'].font=Font(bold=True,size=13)
sec(q,3,'A. 唯一可逐項拆開的外部價格：IREN–Microsoft（GB300）對 TK GB300（$B/GW IT·年）',8)
hdr(q,4,['項目','TK GB300','IREN 隱含','差（IREN − TK）','比（IREN ÷ TK）','IREN 輸入／推導','標記','說明'])
q['A5']='IREN 年租金（每 IT-GW）'; q['B5']=f'={TK("hold","E")}'; q['C5']=f'={EX("iren","I")}'
q['A6']='IT 設備 capex（$B/GW）'; q['B6']=f'={TK("cap_it","E")}'; q['C6']='=5.8/0.2'; q['F6']='Dell 約 $5.8B（GPU＋輔助設備）÷ 0.2 GW'; q['G6']='Verified（公司公告）'
q['A7']='廠房 capex（$B/GW）'; q['B7']=f'={TK("cap_fac","E")}'; q['C7']=15; q['F7']='公司簡報「資料中心基礎設施 $14–16M/MW」（二手轉述）→ 取 15；低 14／高 16'; q['G7']='Interested-party／口徑待確認'
q['H7']='搜尋摘要同時出現「all-in $14–16M/MW」與「$9–11M 為資料中心」兩句，口徑未能對上原簡報；因 $14–16M×200MW＝$2.8–3.2B，與第三方估計吻合，本頁採 14–16 為資料中心基礎設施。'
q['A8']='總 capex（$B/GW）'; q['B8']=f'={TK("cap_tot","E")}'; q['C8']='=C6+C7'
q['A9']='營運費用（不含資本）'; q['B9']=f'={TK("o_tot","E")}'; q['C9']='=(1-0.85)*C5'; q['F9']='營收 ×(1−85%)；85%＝公司估計專案 EBITDA 率（扣電力、維修、直接營運成本，未扣公司管理費與融資）'; q['G9']='Interested-party'; q['H9']='是下界：85% 是公司對專案 EBITDA 率的估計（偏樂觀的上限），實際營運費用可能更高。'
q['A10']='資本回收（租金 − 營運）'; q['B10']=f'={TK("a_it","E")}+{TK("a_fac","E")}'; q['C10']='=C5-C9'; q['F10']='IREN 隱含＝租金 − 營運費用'; q['G10']='Derived'
for r in range(5,11):
    q[f'D{r}']=f'=C{r}-B{r}'; q[f'E{r}']=f'=C{r}/B{r}'
    for c in 'BCD': q[f'{c}{r}'].number_format='0.00'
    q[f'E{r}'].number_format='0.00'
q['A11']='租金差額拆解：營運費用貢獻'; q['D11']='=C9-B9'; q['H11']='負值＝IREN 隱含營運費用低於 TK；占總差額比例見右欄'; q['E11']='=D11/D5'
q['A12']='租金差額拆解：資本回收貢獻'; q['D12']='=C10-B10'; q['E12']='=D12/D5'
for r in(11,12): q[f'D{r}'].number_format='0.00'; q[f'E{r}'].number_format='0%'
q['A13']='檢查：兩項貢獻合計 − 總差額（應為 0）'; q['D13']='=D11+D12-D5'; q['D13'].number_format='0.0E+00'
sec(q,15,'B. 資本回收口徑：IREN 的 5 年租金是否足以回收其 capex？（以 IREN 隱含資本回收與總 capex 估算）',8)
hdr(q,16,['折現率','5 年淨租金現值 ($B/GW)','總 capex ($B/GW)','5 年末所需殘值／重新出租價值現值之外 ($B，年末價值)','殘值占總 capex','說明'])
for i,(lab,w) in enumerate([('3.31%（IREN GPU 融資平均成本）',0.0331),('6%',0.06),('8%',0.08),('10%（TK WACC）',0.10),('13%',0.13)]):
    r=17+i; q.cell(r,1,lab); q.cell(r,7,w).font=BLUE; q.cell(r,7).number_format='0.00%'
    q.cell(r,2,f'=$C$10*(1-(1+G{r})^(-5))/G{r}'); q.cell(r,3,'=$C$8'); q.cell(r,4,f'=(C{r}-B{r})*(1+G{r})^5'); q.cell(r,5,f'=D{r}/C{r}')
    for c in(2,3,4): q.cell(r,c).number_format='0.00'
    q.cell(r,5).number_format='0%'
q['H17']='廠房取 14／16 時（10%）所需殘值 18.9／22.1；（3.31%）6.6／8.9 $B/GW。'
q['F17']='殘值＝第 5 年末資產仍須有的價值（含續約租金或轉售），才能在該折現率下回本。'
q['F20']='TK 10% 下需約一半 capex 的 5 年末價值；廠房（30 年壽命）本身就能承擔一部分，GPU（已用 5 年）承擔有限。→ 租金低於 TK 持有成本，主要是「出租方折現率較低＋把廠房後段價值算在合約外」，而非成本結構相異。'
q['G16']='折現率'

# 隱含 WACC（Derived：二分法；以 TK 拆解頁同一公式複核）
def _hold(w,n,opex_adj=0.0):
    g='J'
    itc=dc[g+'24'].value; fac=[(dc[g+str(r)].value,inp['E'+str(k)].value) for r,k in((26,24),(27,25),(28,26),(29,27))]
    cont=dc[g+'30'].value; land=dc[g+'25'].value
    crf=lambda w,n: w/(1-(1+w)**-n)
    return itc*crf(w,n)+sum(a*crf(w,l) for a,l in fac)*(1+cont)+land*w+dc[g+'48'].value+opex_adj
def _solve(target,n,adj):
    lo,hi=0.0001,0.5
    for _ in range(80):
        mid=(lo+hi)/2
        if _hold(mid,n,adj)>target: hi=mid
        else: lo=mid
    return mid
iw=[_solve(9.7,6,0),_solve(9.7,5,0),_solve(9.7,6,1.455-dc['J48'].value),_solve(9.7,5,1.455-dc['J48'].value)]
q['A22']='隱含 WACC（使 TK GB300 持有成本＝IREN 租金 9.70；Derived）：'
q['B22']=iw[0]; q['C22']=iw[1]; q['D22']=iw[2]; q['E22']=iw[3]
q['F22']='依序：IT 6 年＋TK 營運費；IT 5 年＋TK 營運費；IT 6 年＋IREN 隱含營運費；IT 5 年＋IREN 隱含營運費'
for c in 'BCDE': q[c+'22'].number_format='0.0%'
sec(q,23,'C. 其他外部價格：能對到哪一項、差額多少、不可分離之處',8)
hdr(q,24,['外部價格','每 IT-GW·年（點估）','TK 對照（同世代）','差額 $B（外部−TK）','倍數','可歸因到的 TK 拆解項','不可分離的部分','缺哪個輸入'])
rows=[('X2a CoreWeave 2025Q4 彙總','crwv_a','G','無法歸因到單項。可知：CoreWeave 調整後營業利益率 6%（Q4），表示營收約等於含折舊與利息前的成本；但折舊、利息、租賃費沒有在搜尋摘要中。','世代組合、active power 是 IT 或設施、爬坡中容量','CoreWeave 季報 10-Q 的 cost of revenue／折舊／租賃費；active power 定義；分世代營收'),
('X3 Nebius–Microsoft（下界）','neb_ms','E','只能說 ≥ 此值；若容量全用上，倍數 ≥ 1.07（對 GB300）。','容量實際分配、爬坡、世代、MW 口徑','合約 MW、各階段上線日、GPU 世代'),
('X4a Nebius 2026Q2 新約（低）','neb_new','E','不可分離：2026 定價、信用溢價、預付融資三者疊加。','定價趨勢 vs 客戶信用 vs 預付款','每筆合約的 MW 口徑、世代、年期、預付金額'),
('X5a Oracle（設施→IT）','orc_f','F','與 VR200 持有成本相比差距小（見倍數）；差額可能來自爬坡平均、選擇權與 Oracle 毛利。','爬坡與選擇權、毛利、世代','合約逐年 GW 與金額、Oracle 該合約毛利'),
('X5b Oracle（IT 口徑）','orc_i','F','同上','同上','同上'),
('X6b 支出 ÷ 平均上線 GW','epoch_tk','G','不可分離：分子為 OpenAI 全部雲端支出（含研究、訓練、預留與非現金額度），分母為模型內插值。','訓練／研究／推論用量、額度、預付、機隊 GW 時間序','OpenAI 付費 GPU-hour 或各供應商實際上線 MW 的月度序列'),
('X7a H100 Silicon Data 現貨型（u=1）','h_sd','C','現貨價高於 2025 長約價；TK Hopper 持有成本代表「持有」，不含出租方利潤與稀缺租金。','出租方利潤、稀缺租金、2026 與 2025 差','2025 年同口徑現貨序列、利用率'),
('X7g Nscale GB300（u=1）','g300_ns','E','隱含 $2.7／GPU-hr，與 IREN 隱含值同量級。','kW／GPU 與 GPU 數','Nscale Narvik 實際 MW 與 GPU 數')]
for i,(lab,key,gc_,att,sep,miss) in enumerate(rows):
    r=25+i
    q.cell(r,1,lab); q.cell(r,2,f'={EX(key,"I")}'); q.cell(r,3,f'={TK("hold",gc_)}'); q.cell(r,4,f'=B{r}-C{r}'); q.cell(r,5,f'=B{r}/C{r}')
    q.cell(r,6,att); q.cell(r,7,sep); q.cell(r,8,miss)
    for c in(2,3,4,5): q.cell(r,c).number_format='0.00'
    for c in(6,7,8): q.cell(r,c).alignment=Alignment(wrap_text=True,vertical='top')
sec(q,34,'D. 世代對齊：同一個外部價，分別除以不同 TK 世代（說明「12–12.8 對 9.35」與「0.9 對 10.89」為何方向相反）',8)
hdr(q,35,['外部價格','每 IT-GW·年','÷ Hopper','÷ GB200','÷ GB300','÷ VR200','÷ 2025 組合 0.6/0.4','說明'])
mrows=[('X1 IREN（GB300 實簽）','iren'),('X5a Oracle 設施→IT（2027 起）','orc_f'),('X5b Oracle IT 口徑','orc_i'),('X6a 支出÷1.25GW（使用者算式）','epoch_user'),('X6b 支出÷模型 GW','epoch_tk'),('X2a CoreWeave 2025Q4','crwv_a')]
for i,(lab,key) in enumerate(mrows):
    r=36+i; q.cell(r,1,lab); q.cell(r,2,f'={EX(key,"I")}'); q.cell(r,2).number_format='0.00'
    for j,c in enumerate('CDEFG'):
        q.cell(r,3+j,f'=$B{r}/{TK("hold",c)}'); q.cell(r,3+j).number_format='0.00'
q['H36']='對 GB300 0.89；對 2025 組合 1.04（因組合偏 Hopper／GB200，持有成本較低）。'
q['H37']='Oracle 2027 起的合約若交付 GB300／VR200 世代，倍數 1.1–1.5；拿 2025 組合 9.35 當分母會被放大到 1.4–1.7。'
q['H39']='分母 9.35 是 2025 年舊世代組合；若同一支出對應的是更新世代，倍數降低。'
sec(q,43,'E. 結論用區間（同口徑＝外部價 ÷ 同世代 TK 持有成本；公式引用上方各列）',8)
hdr(q,44,['類別','低','高','納入項目','是否同口徑','說明'])
q['A45']='1 已簽長約、已上線資產（2025 年份）'; q['B45']=f'=MIN({EX("iren","N")},{EX("crwv_a","N")})'; q['C45']=f'=MAX({EX("iren","N")},{EX("crwv_b","N")},{EX("g300_ns","N")}*1)'; q['D45']='X1 IREN、X2a／b CoreWeave、X7g Nscale（u=1）'; q['E45']='是（IT GW；世代對齊）'
q['A46']='2 遠期大合約（2027 起，世代未揭露）對 VR200'; q['B46']=f'=MIN({EX("orc_f","N")},{EX("orc_i","N")})'; q['C46']=f'=MAX({EX("orc_f","N")},{EX("orc_i","N")})'; q['D46']='X5a／b Oracle'; q['E46']='部分（口徑與世代均為假設）'
q['A47']='3 現貨／短約（2026-10）對 Hopper'; q['B47']=f'={EX("h_sd","O")}'; q['C47']=f'={EX("h_ornn","P")}'; q['D47']='X7a、X7b（u 0.7–1.0）'; q['E47']='否（時點、期限不同）'
q['A48']='4 2026 年新簽（Nebius）對 GB300'; q['B48']=f'={EX("neb_new","N")}'; q['C48']=f'={EX("neb_st","P")}'; q['D48']='X4a／b'; q['E48']='否（MW 口徑未明）'
q['A49']='5 支出÷GW（非價格）'; q['B49']=f'=MIN({EX("epoch_tk","N")},{EX("epoch_user","N")})'; q['C49']=f'=MAX({EX("epoch_tk","N")},{EX("epoch_user","N")})'; q['D49']='X6a／b'; q['E49']='否'
for r in range(45,50):
    q[f'B{r}'].number_format='0.00'; q[f'C{r}'].number_format='0.00'
q['F45']='同口徑長約倍數集中在 0.9–1.1，與 TK 10% WACC 的持有成本大致相符，不支持「市場價 ≈ 1.3 倍 TK」。'
q['F47']='現貨與 2026 年新約高於長約是時點與稀缺性，不等於 2025 年持有成本偏低。'
q['F49']='「12–12.8」型數字屬第 5 類或第 2 類；它們用 2025 組合 9.35 當分母才顯得高。'
q.column_dimensions['A'].width=40
for c in 'BCDEG': q.column_dimensions[c].width=16
q.column_dimensions['F'].width=60; q.column_dimensions['H'].width=50
# ---------------- 頁 4 證據 ----------------
v=wb.create_sheet('證據')
hdr(v,1,['ID','項目','事實（含原文／數字）','來源 URL','日期／存取','標記','搜尋狀態','限制'])
EV=[
('E1','IREN–Microsoft 條款','總額約 $9.7B、5 年（至 2031）、20% 預付款於各批交付前支付並於第 3–5 年抵扣；GB300 裝於 Childress Horizon 1–4，合計約 200MW IT load，2026 年交付；IREN 向 Dell 購買 GPU 與輔助設備約 $5.8B。','https://www.sec.gov/Archives/edgar/data/1878848/000114036125040072/ef20058139_8k.htm','2025-11-03；搜尋摘要（本環境直接抓取被擋）','Verified（公司 8-K／新聞稿）；賣方＝利害關係人','已找到（摘要）；原文未直接讀','sec.gov 與 IR 網站在本環境 ENOTFOUND，只能引用搜尋摘要。GPU 顆數搜尋未找到（「76,000」查無來源）。'),
('E2','IREN 專案經濟','預期年化營收 $1.94B；公司估計專案 EBITDA 率 85%（扣電力、維修、直接營運成本；未扣公司管理費與融資）；資料中心基礎設施約 $14–16M/MW IT（簡報，二手轉述）；GPU 融資：$3.65B 設施涵蓋 $5.81B GPU capex 的 96%，平均成本 3.31%。','https://iren.gcs-web.com/static-files/a421bb34-0156-4687-be7d-19f53a5236e5','2025-11；2026-06 融資新聞','Interested-party','已找到（搜尋摘要）','$14–16M 與 $9–11M 兩個數字在摘要中口徑混在一起；以 $14–16M×200MW＝$2.8–3.2B 與第三方估計吻合而採用。'),
('E3','IREN 交付進度','Horizon 1（50MW critical IT）已交付 Microsoft，共四個 50MW 於 2026 年交付。','https://finance.yahoo.com/technology/ai/articles/iren-delivers-first-50mw-microsoft-133130586.html','2026','Verified（二手轉述公司公告）','已找到','—'),
('E4','CoreWeave 2025Q4 營收與 active power','Q4 營收 $1,572M（年增 110%）；調整後營業利益 $88M（6%）、GAAP 營業虧損 $89M；Q4 新增約 260MW active power，期末 >850MW；contracted power 約 3.1GW；backlog $66.8B。','https://www.businesswire.com/news/home/20260226281661/en/CoreWeave-Reports-Strong-Fourth-Quarter-and-Fiscal-Year-2025-Results','2026-02-26；搜尋摘要','Verified（公司揭露）','已找到（摘要）','期初 590MW 由 850−260 反推（Derived）。cost of revenue、折舊、租賃費未找到。'),
('E5','CoreWeave active power 定義','公司正式定義未找到；第三方描述為「已通電、可跑營收工作負載的資料中心電力容量」，是 IT 或設施未明。State of AI 報告指出 active 與 contracted 重疊、非 GPU 數。','https://www.stateof.ai/2026-explore/data/compute','2026','Analogy／二手','已搜尋，未找到（一手定義）','這決定 X2a／X2b 差 20%。'),
('E6','Nebius–Microsoft','基本 $17.4B、5 年（至 2031），選擇權可至約 $19.4B；Vineland NJ，分階段 2025–2026；300MW 僅 GCN 一處提及（引 6-K 為 Nebius 目標）。','https://www.verdict.co.uk/nebius-agreement-microsoft-gpu-services/','2025-09','Interested-party','已找到；容量單一來源','容量實際分配未揭露，只用於下界。'),
('E7','Nebius 2026Q2 電話會議','四筆新 AI 雲合約平均 >$1B，收益率 $20–25M/MW（營收認列基礎，不含預付款），預付款涵蓋 capex 50–60%；短約（≤6 個月）議價 $40–50M/MW；Q2 營收約 $582M，ARR $3B（6 月底）；2026 capex $20–25B；contracted power 目標 5GW；connected 800MW–1GW。','https://www.marketbeat.com/instant-alerts/nebius-group-q2-earnings-call-highlights-2026-08-12/','2026-08-12','Interested-party（管理層）','已找到（二手摘要）','MW 是 IT 還是設施、世代皆未說明。'),
('E8','Oracle–OpenAI','WSJ（2025-09）：約 $300B／約 5 年、需約 4.5GW、2027 起；$60B／年是除法。較早（2025-07）報導「年約 $30B」。均為匿名消息，Oracle 未逐項確認；Gartner 稱「非鐵板釘釘的第一天數字」。Oracle RPO $664B（2026-08 底）。','https://www.techmeme.com/250910/p43','2025-09；2026','Interested-party（匿名消息）','已找到；口徑（IT／設施）未找到','使用者提到的「Oracle 算術 12–12.8」我複算不出：$60B／4.5GW＝13.3；若 4.5GW 為設施、換 IT 為 16.0。'),
('E9','OpenAI 2025 雲端算力支出','Epoch 方法頁引用 OpenAI 雲端算力支出 2024 年 $6.8B、2025 年 $16.3B（亦有「>$15B」「$16B」不同說法）；The Information 轉述 2025 推論 $8.4B。','https://epoch.ai/data/ai-chip-users-documentation/methodology','2025-10 起','Interested-party／二手','已找到','這是「全部雲端支出」，不是 GW 單價；「1.25GW」分母的來源我沒找到。'),
('E10','Epoch Abilene 資本成本','現況（2026-07）：IT power 421MW、H100e 509k、資本成本 $15.9B；預計 2026Q4：843MW、$31.9B。估計值，IT power 未精確定義；晶片估為 B200／B300，Oracle 自 2025-06 交付 GB200。','https://epoch.ai/data/data-centers/satellite-explorer/OpenAIStargateAbilene','2026-07','Derived／Analogy（Epoch 估計）','已找到（原頁讀到）','$15.9B 是資本成本，不是年租；與 X6a 的 $16.3B 是不同的量，兩者數字相近，需防混淆。'),
('E11','H100 租價指數','Silicon Data 新雲指數 $2.53／GPU-hr（2026-10-22；另報 2026-10-07 為 $2.81）；Ornn OCPI 成交結算 H100 SXM $3.15、B200 $9.32（2026-10-22）。報導稱 2025-10→2026-03 租價漲約 40%（$1.70→$2.35）。','https://www.silicondata.com/products/silicon-index/h100','2026-10-22','Interested-party（指數商）','已找到（搜尋摘要）','SemiAnalysis 價格儀表板未採用（付費牆、且不得為單一來源）。'),
('E12','賣方牌價','CoreWeave 牌價：HGX H100 $6.16、H200 $6.31、B200 $8.60、GB200 NVL72 $10.50／GPU-hr（$42／4 GPU）；Lambda H100 $3.29–3.99、B200 $6.69（8 卡）。','https://www.spheron.network/blog/coreweave-gpu-pricing-2026/','2026','Interested-party','已找到（彙整部落格）','牌價非實付價；大客戶多年約不付牌價。'),
('E13','預留價彙整','Bitdeer GB200 3 年預留從 $5.00、1 年 $6.04；STN GB300 3 年預留從 $7.15；彙整站 GB200 雲價從 $6.50（Oct 2026）。','https://www.amcompute.com/gpu-cloud-prices/gb200','2026-10','Interested-party（彙整站）','已找到（單一彙整站）','與 IREN／Nscale 隱含的 $2.3–2.7 差 2–3 倍：零售與批發不同層。'),
('E14','Nscale–Microsoft Narvik 隱含價','$6.2B／5 年／約 52,000 顆 GB300 ⇒ 約 $2.72／GPU-hr（第三方推算）。','https://cvresearch.substack.com/p/nscale-deep-dive','2026','Derived（單一第二手）','已找到','不入分布，僅作旁證。'),
('E15','未找到：OpenAI 向 Microsoft 的每 GPU 小時實付價','已搜尋（沿用 20261020_回本側證據A段 筆記），未找到公開報導。≠ 不存在。','docs/reports/20261020_回本側證據A段_查證筆記.md','2026-10-20','—','已搜尋，未找到','—'),
('E16','未找到：Hopper／GB200 世代的容量與金額同時揭露的合約','沿用 20261020 筆記：找不到。','同上','2026-10-20','—','已搜尋，未找到','—'),
('E17','未找到：Epoch「160 億 ÷ 1.25GW」的原始出處','本次搜尋找到 $16.3B（OpenAI 2025 雲端支出）與 $15.9B（Abilene 資本成本），但沒有找到「1.25GW」與此配對的 Epoch 頁面。','—','2026-10-23','—','已搜尋，未找到','請使用者提供出處以確認分母。'),
('E18','環境限制','sec.gov、businesswire、IR 網站、rcrwireless 等直接抓取 ENOTFOUND（proxy）；僅 epoch.ai 可抓。所有其他數字來自搜尋摘要，建議人工開原頁複核關鍵數字（E1、E2、E4、E7）。','—','2026-10-23','—','—','—')]
for i,rw in enumerate(EV,2):
    for j,x in enumerate(rw,1):
        c=v.cell(i,j,x); c.alignment=Alignment(wrap_text=True,vertical='top')
for c,w in zip('ABCDEFGH',[6,26,70,50,22,22,22,50]): v.column_dimensions[c].width=w
# ---------------- 頁 5 待判斷 ----------------
p=wb.create_sheet('待判斷')
hdr(p,1,['#','問題','預設（建議）','替代','影響','依據'])
Q=[
(1,'「計價倍數」的基準：以 IT 口徑、同世代對比，還是用 2025 機隊組合 9.35 當通用分母？','同世代對比（IREN→GB300、Oracle→VR200）；機隊層級才用 9.35','一律用 9.35','使用 9.35 時 Oracle／支出÷GW 倍數虛高 1.1–1.4 倍（見對帳 D 節）','對帳 D 節'),
(2,'TK 的 WACC 10% 是否應下調或分「持有者」？','不改模型；在報告區分「經濟持有成本（10%）」與「出租方折現率（3–8%）」，倍數同時以兩個 WACC 呈現','WACC 改 8%','TK 拆解敏感度：GB300 在 WACC 8% 約 −0.9；在 3.31% 約 −2.7（見 TK 拆解第79列起）','TK 拆解 E 節；IREN 融資成本 3.31%'),
(3,'IREN 隱含營運費用（≥1.46，下界）低於 TK（1.98）：以誰為準？','TK 不動；列入待查，要求取得 IREN 或 CoreWeave 的分項營運費','TK 營運費下調 0.3–0.5','影響約 −0.5 $B/GW（約 5%）','對帳 A 節'),
(4,'廠房 capex：TK 12.67 $M/MW 是否偏低（IREN 簡報 14–16）？','列為「可能偏低」，不改；先確認簡報原口徑','提高到 14–16','每 +1 $M/MW 約 +0.12 $B/GW·年（含預備費攤銷）','對帳 A 節'),
(5,'Epoch「160 億 ÷ 1.25GW」是否採用為市場價？','不採用為價格，只作「支出÷GW」的對照；請使用者提供 1.25GW 出處','採用並與 IREN 並列','若採用，倍數 1.4–1.6，與同口徑長約相反','證據 E9、E10、E17'),
(6,'Oracle 12–12.8 的算式我複算不出（13.3 或 16.0）。','請使用者提供算式；暫用 13.3（4.5GW=IT）與 16.0（設施）兩種','只用 13.3','不影響結論：對 VR200 為 1.1–1.3 倍','對帳 D 節'),
(7,'2026-10 現貨與 Nebius 新約高於 2025 長約：是否視為「2025 年持有成本偏低」的證據？','否：屬 2026 年稀缺租金與期限差異；另取 2025 年同口徑現貨序列再議','是','若是，TK 持有成本應上調約 1.3–2 倍，與 IREN／CoreWeave 長約矛盾','對帳 E 節'),
(8,'下一步（B 段）是否取得原始文件（IREN 簡報、CoreWeave 10-Q、Nebius 6-K）？','是：以可連線環境取原文，補 cost of revenue／折舊／租賃費、active power 定義','維持二手摘要','可把「不可分離」項減少至少 3 項','證據 E18')]
for i,rw in enumerate(Q,2):
    for j,x in enumerate(rw,1):
        c=p.cell(i,j,x); c.alignment=Alignment(wrap_text=True,vertical='top')
for c,w in zip('ABCDEF',[4,50,50,28,48,28]): p.column_dimensions[c].width=w
out=sys.argv[1]; wb.save(out); print('saved',out)

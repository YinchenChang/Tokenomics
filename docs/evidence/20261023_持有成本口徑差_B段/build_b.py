# B 段：在 A 段 xlsx 上新增「B 段」頁並更新「證據」「待判斷」「對帳」註記。公式引用 TK 拆解頁。
import openpyxl, sys
from openpyxl.styles import Font, PatternFill, Alignment
src,out=sys.argv[1],sys.argv[2]
wb=openpyxl.load_workbook(src)
import openpyxl as _o
_m=_o.load_workbook('model/'+open('model/CURRENT').read().strip(),data_only=True)
dc=_m['DC_Cost']
BLUE=Font(color='0000FF'); BOLD=Font(bold=True); HDR=PatternFill('solid',fgColor='DDEBF7'); SEC=PatternFill('solid',fgColor='F2F2F2')
T="'TK 拆解'!"
s=wb.create_sheet('B 段')
s['A1']='B 段補充：Oracle 並列、Epoch 12.8 矛盾評估、IREN 原文對帳、每 GPU 小時視角、CoreWeave／Nebius 財報結構'; s['A1'].font=Font(bold=True,size=13)
s['A2']='藍字＝外部輸入（出處見「證據」頁 E19 以後）；黑字＝公式。TK 值一律引用「TK 拆解」頁。'
r=[4]
def sec(t):
    r[0]+=1
    for i in range(1,10): s.cell(r[0],i).fill=SEC
    s.cell(r[0],1,t).font=BOLD; r[0]+=1
def hdr(vals):
    for i,v in enumerate(vals,1):
        c=s.cell(r[0],i,v); c.font=BOLD; c.fill=HDR; c.alignment=Alignment(wrap_text=True,vertical='top')
    r[0]+=1
def put(vals,fmts=None,blue=()):
    for i,v in enumerate(vals,1):
        if v is None: continue
        c=s.cell(r[0],i,v); c.alignment=Alignment(wrap_text=True,vertical='top')
        if i in blue: c.font=BLUE
        if fmts and i in fmts: c.number_format=fmts[i]
    r[0]+=1; return r[0]-1
N='0.00'
# ---- 1 Oracle
sec('1. Oracle–OpenAI：5 GW 與 4.5 GW 並列（$300B／5 年；匿名消息，Interested-party）')
hdr(['版本','總額 $B','年數','GW','GW 口徑假設','每年 $B','每 IT-GW·年 $B','倍數 ÷VR200','倍數 ÷GB300','倍數 ÷組合 9.35','出處'])
rows={}
def ora(label,gw,basis,src_):
    rr=r[0]
    f=f'=F{rr}/D{rr}' if basis=='IT' else f'=F{rr}/(D{rr}/{T}C9)'
    rows[label]=put([label,300,5,gw,basis,f'=B{rr}/C{rr}',f,f'=G{rr}/{T}F66',f'=G{rr}/{T}E66',f'=G{rr}/{T}G66',src_],{6:N,7:N,8:N,9:N,10:N},blue=(2,3,4))
ora('5GW 當 IT（Andy 的 12.0）',5,'IT','The Register 2025-09-11 轉述 WSJ："$300 billion ... five gigawatts ... over the course of five years ... begin in 2027"；repo docs/evidence/20261021_token帳閉合A段/供給側查證.md 第59列')
ora('5GW 當設施，換 IT',5,'設施','同上')
ora('4.5GW 當 IT',4.5,'IT','A 段所用報導（WSJ 經 Techmeme 2025-09-10 摘要："requiring 4.5 gigawatts"）；https://www.techmeme.com/250910/p43')
ora('4.5GW 當設施，換 IT',4.5,'設施','同上')
s.cell(r[0],1,'兩份報導的 GW 數不同（5 對 4.5）且 IT／設施口徑均未明：每 IT-GW·年介於 12.0–16.0，對 VR200 倍數 0.98–1.31。A 段「複算不出 12.0」是因我只用了 4.5GW 的報導；Andy 的 12.0＝5GW 當 IT。').alignment=Alignment(wrap_text=True); r[0]+=1
# ---- 2 Epoch
sec('2. Epoch／OpenAI 2025 雲端支出 ÷ GW（機隊層級對照；保留，不當單價）')
hdr(['項目','16.3（Epoch 方法頁，原文值）','16.0（10-21 筆記約值；Andy 記錄 12.8／1.37／1.52）','單位','標記／來源'])
a=put(['雲端算力支出 2025',16.3,16.0,'$B','Interested-party；二手。兩個分子並列，全檔以 16.3 為主、16.0 對照 Andy 的記錄'],blue=(2,3))
b0=put(['上線 GW 2024 年底',0.6,None,'GW','官方（OpenAI 財務長揭露，供給側查證.md 第27–31列）'],blue=(2,))
b1=put(['上線 GW 2025 年底',1.9,None,'GW','同上'],blue=(2,))
lin=put(['全年平均 GW：線性內插',f'=(B{b0}+B{b1})/2',None,'GW','Derived（=1.25＝(0.6+1.9)/2）'],{2:N})
exp_=put(['全年平均 GW：指數內插',f'=(B{b1}-B{b0})/LN(B{b1}/B{b0})',None,'GW','Derived（=1.13）'],{2:'0.000'})
pl=put(['每 GW·年：線性（$B）',f'=B{a}/B{lin}',f'=C{a}/B{lin}','$B/GW·年','Derived（16.0 版＝12.8）'],{2:N,3:N})
pe=put(['每 GW·年：指數（$B）',f'=B{a}/B{exp_}',f'=C{a}/B{exp_}','$B/GW·年','Derived（16.0 版＝14.19）'],{2:N,3:N})
put(['倍數 ÷ 2025 組合 9.35：線性',f'=B{pl}/{T}G66',f'=C{pl}/{T}G66','x','16.3：1.39；16.0：1.37'],{2:N,3:N})
put(['倍數 ÷ 2025 組合 9.35：指數',f'=B{pe}/{T}G66',f'=C{pe}/{T}G66','x','16.3：1.55；16.0：1.52'],{2:N,3:N})
s.cell(r[0],1,'若要把倍數拉回 0.93，分子須為多少（「必須為真」是反推，不是證據）').font=BOLD; r[0]+=1
hdr(['反推項目','16.3 版','16.0 版','單位','說明'])
n1=put(['分子須為（線性 GW）',f'=0.93*{T}G66*B{lin}',f'=0.93*{T}G66*B{lin}','$B','同一個數，與分子版本無關'],{2:N,3:N})
x1=put(['  須排除的支出（線性 GW）',f'=B{a}-B{n1}',f'=C{a}-C{n1}','$B','不是 GPU 容量租金的部分'],{2:N,3:N})
put(['  占全年支出',f'=B{x1}/B{a}',f'=C{x1}/C{a}','%',''],{2:'0%',3:'0%'})
n2=put(['分子須為（指數 GW 1.13）',f'=0.93*{T}G66*B{exp_}',f'=0.93*{T}G66*B{exp_}','$B',''],{2:N,3:N})
x2=put(['  須排除的支出（指數 GW）',f'=B{a}-B{n2}',f'=C{a}-C{n2}','$B','16.0 版＝6.19'],{2:N,3:N})
put(['  占全年支出',f'=B{x2}/B{a}',f'=C{x2}/C{a}','%',''],{2:'0%',3:'0%'})
s.cell(r[0],1,'與長約 0.89–0.93 矛盾的可能原因逐項評估').font=BOLD; r[0]+=1
hdr(['可能原因','方向','量級','評估','證據狀態','能解決它的輸入'])
put(['(a) 非 GPU 雲端服務與研究實驗（儲存、CPU、網路出口、推論以外的雲端帳單）','降低倍數','須排除約 $5.1–6.5B（占 32–40%，見上表）','合理但無數字：OpenAI 營業成本 75 億 vs 推論 84 億已顯示口徑不整齊（出處見證據 E25）；若這類占 30–40% 即可解釋','搜尋未找到分項','OpenAI 雲端帳單分項（GPU 時數 vs 其他服務）'])
put(['(b) 2025 年初 Hopper 舊約','提高（Hopper 租金 > TK Hopper 持有成本）',f'=B{pl}*1000000000/({T}G35*8760)','隱含每 GPU 小時 ($，16.3 版)；若 2025 Hopper 約定價 $2.0–2.5 即與 13.0 一致；GB300 長約隱含 $2.27，兩者同量級→租金不隨世代上升，TK 持有成本隨世代上升','Derived','OpenAI 各供應商實付 $/GPU-hr（已搜尋，未找到）'],{3:N})
put(['(c) 雲端商加價（Azure 轉售）','提高','倍數 ×(1+加價)：1.0–1.3（Assumed）','IREN 賣給 Microsoft 是批發價；Microsoft 轉給 OpenAI 若加價 20% → 0.89×1.2＝1.07；與 Microsoft–OpenAI 關係（持股、額度）交織','Assumed','OpenAI 向 Microsoft 的實付價（找不到）'])
put(['(d) GW 口徑','若 1.25 為設施口徑 → IT GW 較小（÷PUE）→ 每 IT-GW 支出較高 → 倍數更高；若為 IT 口徑則維持',f'=B{a}/(B{lin}/{T}C9)','設施口徑下每 IT-GW 支出（$B，16.3 版）；不能降低倍數，只會更高','Derived','OpenAI 財務長 GW 的定義（IT 或設施）'],{3:N})
put(['(e) 非現金額度','降低現金口徑，但「支出」若含額度則提高','無數字','The Register 提醒 Microsoft 端數字可能含額度','二手','OpenAI 現金支付表'])
put(['(f) 時間窗與預付','分子含預留未上線容量→提高','無數字','分母用年底上線 GW 內插，未含「已付費但未上線」容量','Assumed','各供應商合約生效與上線日'])
put(['綜合','',None,'(a) 與 (b)(c)(d)(f) 方向相反且量級都能到 ±20–30%；現有資料無法分離 → 列為「不可分離」。補記：OpenAI 揭露支出分項，或揭露對 Azure 的實付價，才能分開。','',''])
# ---- 3 IREN
sec('3. IREN 原文對帳（sec.gov 8-K 附件 99-1、99-2；chat 端 WebFetch 取得，[Verified]；IREN＝Interested-party）')
hdr(['項目','IREN 值','單位','TK 值','IREN ÷ TK','說明'])
g=put(['GPU 與周邊 capex（含部署服務、伺服器、InfiniBand、線材、軟體授權）',5.8,'$B',None,None,'原文'],blue=(2,))
mw=put(['容量（critical IT load）',0.2,'GW IT',None,None,'原文'],blue=(2,))
perg=put(['  GPU 與周邊 capex 每 IT-GW',f'=B{g}/B{mw}','$B/GW',f'={T}E39',f'=B{r[0]}/D{r[0]}','TK GB300 IT 設備（機架＋網路＋儲存）'],{2:N,4:N,5:N})
body_lo=put(['資料中心本體 低',9,'$M/MW',f'={T}E46*1000/{T}E7',f'=B{r[0]}/D{r[0]}','Tier III 同級；TK 廠房 capex 每 MW＝12.67（土地、建物、電力、機械、光纖保全、預備費）'],{2:'0',4:N,5:N},blue=(2,))
body_hi=put(['資料中心本體 高',11,'$M/MW',f'={T}E46*1000/{T}E7',f'=B{r[0]}/D{r[0]}',''],{2:'0',4:N,5:N},blue=(2,))
cl=put(['100MW 超級叢集架構部署',3,'$M/MW',None,None,'是否已含在 5.8B 的 GPU 周邊內：原文未明（不可分離）'],blue=(2,))
ac=put(['2026 年交付 200MW 的加速費用',2,'$M/MW',None,None,'一次性，非穩態'],blue=(2,))
put(['每 MW 全部 capex（不含 GPU）：低／高','=B%d+B%d+B%d'%(body_lo,cl,ac),'$M/MW','=B%d+B%d+B%d'%(body_hi,cl,ac),None,'低 14、高 16，與原文一致'],{2:'0',4:'0'})
s.cell(r[0],1,'TK 廠房 capex 是否含網路與叢集部署？—不含。DC_Cost 第25–31列只有土地、建物、電力設施、機械散熱、光纖保全、預備費；網路在第21列（機架價 ×10%）、儲存在第23列，都屬 IT 設備；機架價含機架內冷卻。').alignment=Alignment(wrap_text=True); r[0]+=1
hdr(['配置方式（資本支出配置有兩種讀法）','IREN IT 側 $B/GW','IREN 廠房側 $B/GW','TK IT','TK 廠房','IT 比','廠房比','廠房 capex 若改為 IREN 值，TK GB300 持有成本變化 $B/GW·年'])
k=f'(({T}E54+{T}E62+0.005*{T}E46)/{T}E46)'
rA=put(['A. 叢集部署歸 IT 側（29.0＋3）；廠房＝本體 10（中點）',f'=B{perg}+B{cl}',10,f'={T}E39',f'={T}E46','=B%d/D%d'%(r[0],r[0]),'=C%d/E%d'%(r[0],r[0]),f'=(C{r[0]}-E{r[0]})*{k}'],{2:N,3:N,4:N,5:N,6:N,7:N,8:N},blue=(3,))
rB=put(['B. 叢集部署歸廠房側（29.0；10＋3）',f'=B{perg}',13,f'={T}E39',f'={T}E46','=B%d/D%d'%(r[0],r[0]),'=C%d/E%d'%(r[0],r[0]),f'=(C{r[0]}-E{r[0]})*{k}'],{2:N,3:N,4:N,5:N,6:N,7:N,8:N},blue=(3,))
rC=put(['C. 全包（A 段用法）：29.0＋15',f'=B{perg}',15,f'={T}E39',f'={T}E46','=B%d/D%d'%(r[0],r[0]),'=C%d/E%d'%(r[0],r[0]),f'=(C{r[0]}-E{r[0]})*{k}'],{2:N,3:N,4:N,5:N,6:N,7:N,8:N},blue=(3,))
s.cell(r[0],1,'讀法：IT 設備與 IREN 一致（A 配置 0.99、B/C 配置 0.90）；廠房本體 TK 12.67 高於 IREN 9–11（高 15–41%），但加上叢集部署 3 後（12–14）TK 落在區間內。→ A 段「廠房可能偏低」應撤回：以原文的本體 9–11 比，TK 偏高；以含叢集部署比，TK 持平。總 capex：C 配置（29＋15）為 44.0、0.98 倍；A、B 配置（32＋10＝29＋13）為 42.0、0.935 倍（對 TK 44.9）。租金差額的分解方式不受影響。').alignment=Alignment(wrap_text=True); r[0]+=1
put(['營運費用下界','=0.15*9.7','$B/GW·年',f'={T}E65',f'=B{r[0]}/D{r[0]}','15%×9.70＝1.455；扣電費、維修、其他直接營運費，不含企業管理費、財務費用、非現金項目 → 是下界（原文有依據）；TK 1.98 含站點營運與財產稅'],{2:'0.000',4:N,5:N})
# ---- 4 per GPU hour
sec('4. 每 GPU 小時視角：長約租金是否不隨世代上升，而 TK 持有成本隨世代上升？（Derived）')
hdr(['世代','TK 每 GW GPU 數','TK 持有成本 $/GPU-hr','外部租金 $/GPU-hr（隱含）','外部 ÷ TK','外部來源'])
def ph(lab,col,ext,src_,fmt='0.00'):
    rr=r[0]; return put([lab,f'={T}{col}35',f'={T}{col}76',ext.replace('#',str(rr)),f'=D{rr}/C{rr}',src_],{2:'#,##0',3:N,4:N,5:N})
ph('Hopper：Silicon Data H100 指數（2026-10）','C','2.53','Interested-party（指數商）')
ph('Hopper：Ornn H100 成交價（2026-10）','C','3.15','Interested-party')
ph('機隊層級（2025 組合，含 Hopper）：16.3÷1.25＝13.04 隱含（16.0 版 12.8 → $2.31）','G',f'=B{pl}*1000000000/(B#*8760)','Derived：機隊層級，非單一世代')
ph('GB300：IREN 9.70','E',f'=9.7*1000000000/(B#*8760)','Interested-party（8-K）')
ph('GB300：Nscale Narvik（第三方推算）','E','=6200000000/5/52000/8760','Derived（單一第二手）')
ph('VR200：Oracle 12.0（5GW 當 IT）','F',f'=G{rows["5GW 當 IT（Andy 的 12.0）"]}*1000000000/(B#*8760)','Interested-party（匿名消息）')
s.cell(r[0],1,'觀察：外部隱含租金約 $2.3–2.7／GPU-hr，幾乎不隨世代變；TK 持有成本由 Hopper 1.54 升到 VR200 4.78。→ 倍數隨世代由 >1（Hopper、舊世代組合）降到 <1（GB300）。這同時解釋「機隊層級 1.37」與「GB300 長約 0.89」，但依賴「租金不隨世代變」，且資料點少。反例：Oracle→VR200 隱含 $4.7（匿名消息、且假設交付 VR200；若交付 GB300 則隱含約 $2.8，與「租金不隨世代變」一致）。CoreWeave 2026Q2 隱含 $1.5（見第5節）則低於此區間，與假設不合，原因不可分離。').alignment=Alignment(wrap_text=True); r[0]+=1
# ---- 5 CRWV / Nebius
sec('5. CoreWeave 2026Q2（10-Q 部分）與 Nebius 2026Q2（6-K）財報結構（百萬美元）')
hdr(['項目','CoreWeave Q2 2026','Nebius Q2 2026','說明'])
rv=put(['營收',2575,582.3,'10-Q／6-K'],blue=(2,3))
cr=put(['營業成本（cost of revenue）',879,133.6,''],blue=(2,3))
ti=put(['技術與基礎設施',1507,None,'CoreWeave 項目'],blue=(2,))
dp=put(['折舊',1400,259.7,'CoreWeave：是否含在技術與基礎設施內，部分 10-Q 未明（假設含）'],blue=(2,3))
put(['營業成本 ÷ 營收',f'=B{cr}/B{rv}',f'=C{cr}/C{rv}',''],{2:'0%',3:'0%'})
put(['折舊 ÷ 營收',f'=B{dp}/B{rv}',f'=C{dp}/C{rv}',''],{2:'0%',3:'0%'})
put(['營收 − 營業成本 − 技術與基礎設施（SG&A 前）',f'=B{rv}-B{cr}-B{ti}',None,'若折舊含於技術與基礎設施：營業利益率'],{2:'0'})
put(['  ÷ 營收',f'=B{r[0]-1}/B{rv}',None,''],{2:'0.0%'})
put(['TK 對照：廠房側成本占持有成本（廠房年金＋電費＋廠房維護＋站點營運＋廠房財產稅）',f'=({T}G54+{T}G60+{T}G62+{T}G63+0.005*{T}G46)/{T}G66',None,'CoreWeave 營業成本含租賃機房與電力 → 與此對照（34% vs 約 30%），量級吻合；營業成本內容未逐項揭露（Derived）'],{2:'0%'})
put(['TK 對照：IT 帳面折舊 ÷ 持有成本（組合）',f'={T}G39/{T}E11/{T}G66',None,'CoreWeave 折舊占營收 54%；TK 組合 IT 折舊約 47%（以 9.35 為營收）；差距可由新世代較貴、含租賃改良折舊解釋（Derived）'],{2:'0%'})
put(['CoreWeave active power Q1 末（GW）',1.0,None,'由 Q2 末 1.5GW 與「Q2 淨增近 500MW」反推（與「Q1 突破 1GW」一致）；IT 或設施口徑未取得'],{2:'0.0'},blue=(2,))
put(['CoreWeave active power Q2 末（GW）',1.5,None,'Q2 新聞稿（搜尋摘要，二手）'],{2:'0.0'},blue=(2,))
avgr=put(['平均 active power Q2（GW）',f'=(B{r[0]-2}+B{r[0]-1})/2',None,''],{2:'0.00'})
put(['營收年化 ÷ 平均 active power（$B/GW·年）',f'=B{rv}*4/1000/B{r[0]-1}',None,'Q4 2025 為 8.73（A 段）；新容量爬坡拉低比值'],{2:N})
put(['  ÷ TK 組合 9.35',f'=B{r[0]-1}/{T}G66',None,''],{2:N})
put(['  隱含 $/GPU-hr（用 TK 組合每 GW GPU 數）',f'=B{r[0]-2}*1000000000/({T}G35*8760)',None,'明顯低於 H100 指數 2.5–3.2：爬坡落差（電通但未計費）＋舊約低價＋口徑；不可分離'],{2:N})
put(['Nebius 設備耐用年限','4 → 5 年（2026Q1 起）','','折舊率下降約 20%，抬高帳面利潤，不改現金成本；MW 定義未揭露'])
put(['未取得（待 Drive inbox 的 10-Q 全文）','active power 定義、GPU 耐用年限、債務利率','','→ 有了債務利率才能把「出租方折現率 3–8%」落到 CoreWeave 實值'])
# ---- 6 資金成本依公司分列
sec('6. 出租方資金成本依公司分列；IREN 租金差額重新拆解（CoreWeave 10-Q Note 10；IREN 8-K）')
s.cell(r[0],1,'注意：10-Q 只讀到 181 頁中的前約 80 頁（財報本文、附註 1–15、MD&A 前半）；active power 與 contracted power 定義、GPU 耐用年限未找到。').alignment=Alignment(wrap_text=True); r[0]+=1
hdr(['CoreWeave 債務（2026-06-30；$M）','有效利率','餘額 $M','類別','說明'])
debt=[('DDTL 1.0',.15,1300,'DDTL'),('DDTL 2.0',.11,3190,'DDTL'),('DDTL 2.1',.09,3000,'DDTL'),('DDTL 3.0',.09,2215,'DDTL'),('DDTL 5.0（SOFR+4.50%）',.09,1101,'DDTL'),('DDTL 4.0（non-recourse；SOFR+2.25% 或 Treasury+2.00%）',.07,2837,'DDTL'),('2030 Senior Notes',.10,2000,'其他'),('2031 9.00% Notes',.10,1750,'其他'),('2031 9.75% Notes',.10,2750,'其他'),('2032 9.625% Notes',.10,1250,'其他'),('2032 EUR Notes',.09,2279,'其他'),('2031 Convertible',.02,2588,'可轉債'),('2032 Convertible',.02,4000,'可轉債'),('OEM／Software financing（recourse）',.11,4220,'其他'),('OEM／Software financing（non-recourse）',.09,882,'其他'),('Magnetar Loan',.12,189,'其他')]
d0=r[0]
for nm,rt,bal,ty in debt: put([nm,rt,bal,ty,'10-Q Note 10「Effective Interest Rates」'],{2:'0%',3:'#,##0'},blue=(2,3))
d1=r[0]-1
rg=lambda c: f'{c}{d0}:{c}{d1}'
wa=put(['加權平均（全部，按餘額）',f'=SUMPRODUCT({rg("B")},{rg("C")})/SUM({rg("C")})',f'=SUM({rg("C")})','','Derived（10-Q 無整體加權平均；原文只有 OEM 短期工具 9%）'],{2:'0.0%',3:'#,##0'})
wb_=put(['加權平均（不含可轉債）',f'=SUMPRODUCT(({rg("D")}<>"可轉債")*{rg("B")}*{rg("C")})/SUMPRODUCT(({rg("D")}<>"可轉債")*{rg("C")})',None,'','Derived'],{2:'0.0%'})
wc=put(['加權平均（DDTL 系列，GPU 擔保）',f'=SUMPRODUCT(({rg("D")}="DDTL")*{rg("B")}*{rg("C")})/SUMPRODUCT(({rg("D")}="DDTL")*{rg("C")})',None,'','Derived'],{2:'0.0%'})
put(['Q2 利息費用淨額年化 ÷ 債務餘額',f'=640*4/C{wa}',None,'','Derived；利息費用 (640)，含資本化等影響'],{2:'0.0%'})
put(['IREN GPU 融資平均成本',0.0331,None,'','8-K 後續融資新聞：$3.65B 投資級設施＋客戶預付款，涵蓋 $5.81B 的 96%；債務以 Microsoft 長約為擔保（個案）'],{2:'0.00%'},blue=(2,))
put(['Tokenomics WACC（基準）',f'={T}E10',None,'','Assumed（區間 8–13%）'],{2:'0.0%'})
s.cell(r[0],1,'讀法：出租方資金成本依公司而異——IREN 3.31%（Microsoft 擔保＋預付款）；CoreWeave 債務 9.6–9.9%，接近 TK 的 10%。先前「出租方折現率 3–8%」只適用 IREN 個案，不能推廣為市場常態。').alignment=Alignment(wrap_text=True); r[0]+=2
hdr(['IREN 租金差額（GB300，$B/GW·年）重新拆解','IREN IT capex','IREN 廠房 capex','IT capex 效果','廠房 capex 效果','營運費用效果','折現率與其他殘差','租金差額（IREN 9.70 − TK）','殘差占差額'])
CR=f'{T}E10/(1-(1+{T}E10)^(-{T}E11))'
def gaprow(lab,it,fac):
    rr=r[0]
    put([lab,it,fac,f'=(B{rr}-{T}E39)*{CR}',f'=(C{rr}-{T}E46)*{T}E54/{T}E46',f'=0.15*9.7-{T}E65',f'=H{rr}-D{rr}-E{rr}-F{rr}',f'=9.7-{T}E66',f'=G{rr}/H{rr}'],{2:N,3:N,4:'0.000',5:'0.000',6:'0.000',7:'0.000',8:'0.000',9:'0%'},blue=(2,3))
gaprow('A. 叢集部署歸 IT 側（32.0）；廠房＝本體 10',f'=B{perg}+B{cl}',10)
gaprow('B. 叢集部署歸廠房側（29.0；廠房 13）',f'=B{perg}',13)
gaprow('C. 全包（29.0；廠房 15）',f'=B{perg}',15)
s.cell(r[0],1,'效果＝以 TK 的 WACC 10%、IT 6 年、廠房年金率計算「IREN 的 capex 相對 TK 的 capex」造成的年持有成本差；營運效果＝IREN 營運下界 1.455 減 TK 營運 1.98；殘差＝其餘（含折現率差與配置誤差）。結論：差額主要來自 IT 設備單價（B、C 配置約 −0.74，占 63%）與營運費用（約 −0.53，占 44%）；折現率與其他殘差只占 −4% 至 24%，隨叢集部署歸屬而變，不是主因。').alignment=Alignment(wrap_text=True); r[0]+=1
hdr(['隱含 WACC（使年持有成本＝IREN 租金 9.70；Derived，二分法）','用 IREN 營運 1.455','用 TK 營運 1.98','說明'])
import math
def crf_(w,n): return w/(1-(1+w)**-n)
def fa(w,fac):
    parts=[(3.6,30),(4.5,20),(2.5,15),(0.4,10)]
    tot=sum(a for a,_ in parts)*1.15+.02
    return (sum(a*crf_(w,n) for a,n in parts)*1.15+.02*w)/tot*fac
def solv(it,fac,opex):
    lo,hi=.0001,.5
    for _ in range(80):
        m=(lo+hi)/2
        if it*crf_(m,6)+fa(m,fac)+opex>9.7: hi=m
        else: lo=m
    return m
tko=dc['J48'].value
for lab,it,fac in (('A（IT 32.0；廠房 10）',32,10),('B（IT 29.0；廠房 13）',29,13),('C（IT 29.0；廠房 15）',29,15)):
    put([lab,solv(it,fac,1.455),solv(it,fac,tko),'廠房年金依 TK 各分項年限比例縮放'],{2:'0.0%',3:'0.0%'})
s.cell(r[0],1,'讀法：以 IREN 自己的 capex 與營運下界計算，隱含 WACC 約 9–10%，與 TK 的 10% 相當。IREN 的 0.89 倍不需要「低折現率」來解釋；A 段「使 TK 等於 IREN 租金需 WACC 6.2–7.9%」是在固定 TK 的 capex 與營運下求得，混入了 capex 與營運差異。').alignment=Alignment(wrap_text=True); r[0]+=2
hdr(['CoreWeave 2026Q2 觀察（單家、單季，待驗證）','值','','說明'])
cw=put(['營收年化 ÷ 平均 active power（照字面當 IT）',f'=B{rv}*4/1000/B{avgr}',None,'同第5節；分母為反推值（Q1 末 1.0、Q2 末 1.5 的平均），IT 或設施口徑未取得'],{2:N})
cwg=put(['  若 active power 為設施口徑，換 IT（×PUE）',f'=B{cw}*{T}C9',None,'未取得定義，此為上界情境'],{2:N})
put(['  ÷ TK 組合 9.35：IT 情境／設施情境',f'=B{cw}/{T}G66',f'=B{cwg}/{T}G66',''],{2:N,3:N})
put(['  使 TK 組合持有成本＝此營收的隱含 WACC：IT 情境',f'=0.05+(B{cw}-{T}G80)/({T}G81-{T}G80)*0.03',None,'線性內插 TK 拆解第80–81列（5%、8%）；債務成本 9.6–9.9% → 租金低於以該資金成本的全成本'],{2:'0.0%'})
put(['  同上：設施情境',f'=0.10+(B{cwg}-{T}G82)/({T}G83-{T}G82)*0.03',None,'線性內插第82–83列（10%、13%）'],{2:'0.0%'})
put(['營收 − 營業成本 − 技術與基礎設施',f'=B{rv}-B{cr}-B{ti}',None,'$M'],{2:'0'})
put(['  其他營業費用（反推）＝上列 − 營業損失 (49)',f'=B{r[0]-1}+49',f'=B{r[0]}/B{rv}','$M；占營收（SG&A 等，TK 範圍不含平台研發與管理費）'],{2:'0',3:'0.0%'})
put(['利息費用淨額 (640) ÷ 營收',f'=640/B{rv}',None,'營業損失 (49) 之後再扣利息，淨損 (626)'],{2:'0%'})
s.cell(r[0],1,'觀察（待驗證）：在資金成本相近的情況下，CoreWeave 每 GW 年化營收 8.24（為 TK 組合 9.35 的 0.88 倍）且營業損失，較符合「出租價格目前低於以 10% 資金成本計的全成本」，而不是「Tokenomics 持有成本偏高」。保留：(1) 營收含爬坡落差（電已通、尚未計費），分母偏大；(2) active power 若為設施口徑，倍數變 1.06；(3) 營業損失含 SG&A 等不屬 TK 範圍的費用（約占營收 9%）；(4) 只有一家公司、一季資料；(5) 98% 營收來自承諾合約，客戶集中（A 36%、B 26%、C 10%），RPO $103.7B（41% 在 24 個月內），加權平均合約期未找到。').alignment=Alignment(wrap_text=True); r[0]+=1
for c,w in zip('ABCDEFGHIJK',[58,16,16,22,22,18,14,22,16,16,80]): s.column_dimensions[c].width=w
# ---- 證據
z=wb['證據']
EV=[('E19','Oracle–OpenAI（5GW 版本）','The Register 2025-09-11 轉述 WSJ："$300 billion ... five gigawatts ... over the course of five years ... begin in 2027"；GW 口徑未明。','https://www.theregister.com/2025/09/11/openai_reportedly_on_the_hook/','2025-09-11（chat 端提供）','Interested-party（匿名消息）','已找到（chat 端）','與 E8 的 4.5GW 版本並列於 B 段頁'),
('E20','Epoch 12.8 的算式','$16B ÷ 1.25 GW；1.25＝(0.6+1.9)/2，為 OpenAI 財務長揭露 2024、2025 年底上線 GW 的線性內插；指數內插 1.13。','docs/evidence/20261021_token帳閉合A段/供給側查證.md（第27–31列）','2026-10-21','官方（GW 端點）＋Derived','已找到','1.25 非 Epoch 揭露的 GW，是內插值；A 段「出處未知」更正為此'),
('E21','IREN 8-K 附件 99-1、99-2（原文）','$9.7B／5 年、20% 預付款（抵第 3–5 年）；200MW critical IT load；GPU 與周邊 capex $5.8B（含部署、伺服器、InfiniBand、線材、軟體授權）；每 MW 全部 capex $14–16M（IT 口徑）＝資料中心本體 9–11＋100MW 超級叢集架構部署 3＋加速費用 2；年化營收 $1.94B；專案 EBITDA 率 85%（扣電費、維修、其他直接營運費後；扣企業管理費、財務費用、非現金項目前）。','sec.gov/Archives/edgar/data/1878848/000114036125040072/（ex99-1、ex99-2）','2026-10-23（chat 端 WebFetch）','Verified（原文）；IREN＝Interested-party','已找到（原文）','取代 A 段 E2 的二手摘要；A 段把 14–16 當「資料中心基礎設施」是誤讀，見 B 段頁第3節'),
('E22','CoreWeave 2026Q2 10-Q（部分）','季營收 2,575、營業成本 879、技術與基礎設施 1,507、折舊 1,400（百萬美元）；RPO 1,037 億，41% 於 24 個月內認列。','chat 端提供（10-Q 部分）','2026-10-23','Verified（公司申報）','部分','active power 定義、GPU 耐用年限、債務利率待 10-Q 全文（Drive inbox）'),
('E23','Nebius 2026Q2 6-K','營收 582.3、營業成本 133.6、折舊 259.7（百萬美元）；伺服器與網路設備耐用年限 2026Q1 起 4→5 年。MW 定義未揭露。','chat 端提供','2026-10-23','Verified（公司申報）','已找到；MW 定義已搜尋，未找到','—'),
('E24','CoreWeave active power 2026Q1／Q2','Q1：營收約 $2.08B、active power 突破 1GW、contracted >3.5GW；Q2：active power 增近 500MW 至 1.5GW，contracted 約 3.7GW（6 月底）、4.2GW（8 月 11 日），backlog $104.2B。','https://www.businesswire.com/news/home/20260507558197/en/ ；Q2 新聞稿（搜尋摘要）','2026-05／08','Verified（公司揭露，二手摘要）','已找到（摘要）','Q1 末 1.0GW 是反推；口徑未明')]
for i,rw in enumerate(EV):
    for j,x in enumerate(rw,1):
        c=z.cell(z.max_row+1 if j==1 else z.max_row,j,x); c.alignment=Alignment(wrap_text=True,vertical='top')
# 更正 E2、E8 註記
Z=lambda rid: next(rw for rw in z.iter_rows(min_row=2) if rw[0].value==rid)
rw=Z('E2'); rw[2].value=rw[2].value.replace('GPU 融資：$3.65B 設施涵蓋 $5.81B GPU capex 的 96%，平均成本 3.31%。','GPU 融資：$3.65B 投資級設施（約占 $5.81B GPU capex 的 62.8%）加客戶預付款，合計融資 $5.59B（約 96%），平均成本 3.31%。')
rw=Z('E9'); rw[7].value='這是「全部雲端支出」，不是 GW 單價；「1.25GW」＝(0.6+1.9)/2 線性內插（見 E20，供給側查證.md 第27–31列）。分子 16.3（方法頁）與約值 16.0 並存，見 B 段頁。'
rw=Z('E17'); rw[2].value='原本未找到「1.25GW」出處。B 段已由 chat 端提供：1.25＝OpenAI 財務長揭露 2024、2025 年底上線 GW（0.6、1.9）的線性內插，見 E20。'; rw[7].value='已解決'
z.append(['E25','OpenAI 營業成本與推論數字','營業成本（cost of revenue）2025 約 75 億；推論 84 億（The Information 轉述，另 Sacra）；兩者不可能同口徑。','docs/reports/20261020_回本側證據A段_查證筆記.md（任務2 §2.1–2.2）','2026-10-20','Interested-party／二手','已找到','引自既有筆記；來源為 Zitron 取得文件與 The Information 轉述'])
for c in z[z.max_row]: c.alignment=Alignment(wrap_text=True,vertical='top')
for row in z.iter_rows(min_row=2):
    if row[0].value=='E2': row[7].value=str(row[7].value)+'｜B 段更正：原文顯示 $14–16M/MW 為「全部 capex（IT 口徑）」＝本體 9–11＋叢集部署 3＋加速 2，不是資料中心本體。'
    if row[0].value=='E8': row[7].value='A 段僅用 4.5GW 版本（13.3；設施換 IT 為 16.0）。B 段補：5GW 版本（E19）12.0＝300÷5÷5（5GW 當設施換 IT 為 14.4）；四種讀法並列於外部價格換算 X5a–X5e 與 B 段頁。'
    if row[0].value=='E17': row[6].value='已解決（B 段）：1.25＝(0.6+1.9)/2 內插，見 E20'
# 對帳 註記
q=wb['對帳']
q['H7']='B 段更正：原文 $14–16M/MW 是不含 GPU 的全部 capex（本體 9–11＋叢集部署 3＋加速 2）。C7=15 沿用為「全包」；與 TK 廠房的 like-for-like 比較見「B 段」頁第3節。'
q['H9']='是下界：15%×9.70；原文確認扣電費、維修、其他直接營運費，不含企業管理費、財務費用、非現金項目。'
# 待判斷
p=wb['待判斷']
dec={2:'決定（Andy，2026-10-23）：同世代對比；9.35 只用於機隊層級',3:'決定：不改模型；同列 10% 與出租方 3–8%',4:'決定：先不改；B 段原文已取得：IREN 營運下界 1.455 有依據',5:'決定：先不改；B 段原文：IREN 本體 9–11、含叢集 12–14；TK 12.67 不含叢集部署，結論見 B 段頁第3節（廠房偏低的說法撤回）',6:'決定：保留作機隊層級對照；算式 160÷1.25，1.25 為內插（E20）',7:'決定：已有算式 300÷5÷5＝12.0（5GW）；B 段並列 5GW 與 4.5GW',8:'決定：不作為 2025 年持有成本偏低的證據',9:'決定：讀原文；已取得 IREN、CoreWeave 部分、Nebius；CoreWeave 10-Q 全文待 Drive inbox'}
for i in range(2,p.max_row+1):
    n=p.cell(i,1).value
    mp={1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9}
    if n in mp:
        p.cell(i,7,dec[mp[n]]); p.cell(i,7).alignment=Alignment(wrap_text=True,vertical='top')
p.cell(1,7,'決定／B 段狀態').font=BOLD; p.cell(1,7).fill=HDR; p.column_dimensions['G'].width=60
nq=[(9,'Epoch 機隊對照的矛盾（1.37 對 0.89–0.93）要不要進一步拆？','維持「不可分離」，並以「每 GPU 小時租金不隨世代變」作為最可能的解釋方向，列 B 段頁第4節','要求 OpenAI 雲端帳單分項','影響機隊層級 9.35 的使用方式','B 段頁第2、4節'),
(10,'CoreWeave 取得 10-Q 全文後，是否用其債務利率與折舊年限回填「出租方折現率」？','是（待 inbox）','維持 3–8% 區間','把 WACC 差異從假設變成實值','B 段頁第5節'),
(11,'IREN 叢集部署 3 $M/MW 是否已在 5.8B 內？','原文未明，A/B 兩配置並列','向 IREN 簡報原頁確認','不影響總 capex；影響 IT／廠房側拆分','B 段頁第3節')]
for rw in nq:
    for j,x in enumerate(rw,1):
        c=p.cell(p.max_row+1 if j==1 else p.max_row,j,x); c.alignment=Alignment(wrap_text=True,vertical='top')
D2={9:'決定（Andy）：維持「不可分離」。補記：OpenAI 揭露支出分項，或揭露對 Azure 的實付價，才能分開。',10:'決定（Andy）：要；只寫進查證檔，不改模型（Tokenomics 維持 10%）。',11:'決定（Andy）：A／B 兩種配置並列即可，不再追；影響 GB300 持有成本 −0.38 至 +0.33（約 ±3%），不改結論。'}
for i in range(2,p.max_row+1):
    if p.cell(i,1).value in D2:
        p.cell(i,7,D2[p.cell(i,1).value]); p.cell(i,7).alignment=Alignment(wrap_text=True,vertical='top')

# ---- 審查修正（PR #150 查核 13 項）
e=wb['外部價格換算']
import copy
def clone(src,dst,gw,label,iid,low_div):
    for col in range(1,27):
        c0=e.cell(src,col); c=e.cell(dst,col); v=c0.value
        if isinstance(v,str) and v.startswith('='): v=v.replace(str(src),str(dst))
        c.value=v
        if c0.has_style: c.font=copy.copy(c0.font); c.number_format=c0.number_format; c.alignment=copy.copy(c0.alignment)
    e.cell(dst,1,iid); e.cell(dst,2,label); e.cell(dst,26,'E19')
    e.cell(dst,25).value='低：5GW 版本（The Register 轉述 WSJ，供給側查證.md 第59列）；口徑未明'
clone(13,31,5,'Oracle–OpenAI（The Register 轉述 WSJ：$300B／5 年／5GW）— 5GW 當 IT 口徑（=Andy 的 12.0）','X5d',5)
e['F31']=5
clone(12,32,5,'同上，5GW 當設施口徑，換 IT（÷PUE）','X5e',5)
e['F32']="=5/'TK 拆解'!C9"; e['J32']='=C32/E32/5'
e['B16']=e['B16'].value.replace('（使用者算式；1.25GW 來源未知）','（Andy 算式；1.25GW＝(0.6+1.9)/2 線性內插，見證據 E20）')
q=wb['對帳']
q['B46']="=MIN(外部價格換算!N12,外部價格換算!N13,外部價格換算!N31,外部價格換算!N32)"
q['C46']="=MAX(外部價格換算!N12,外部價格換算!N13,外部價格換算!N31,外部價格換算!N32)"
q['D46']='X5a／b（4.5GW）、X5d／e（5GW）Oracle'
q['A7']='IREN 不含 GPU 的全部 capex（$B/GW；本體 9–11＋叢集部署 3＋加速 2）對 TK 廠房 capex'
q['F7']='原文：每 MW 14–16 百萬美元（取 15）＝資料中心本體 9–11＋叢集部署 3＋加速 2；TK 廠房不含叢集部署與網路。like-for-like（對本體 9–11 或 12–14）見「B 段」頁第3節'
q['G7']='Verified（8-K 原文）；Interested-party'
q['H7']='B 段更正：此列比值 1.18 是「全包 vs TK 廠房」，不是 like-for-like。對本體 9–11，TK 廠房偏高 15–41%；本體加叢集部署（12–14）則持平。「TK 廠房可能偏低」撤回。'
p=wb['待判斷']
def setp(n,col,val):
    for i in range(2,p.max_row+1):
        if p.cell(i,1).value==n: p.cell(i,col,val); p.cell(i,col).alignment=Alignment(wrap_text=True,vertical='top')
setp(2,5,'TK 拆解敏感度：GB300 在 WACC 8% 約 −0.63；在 3.31% 約 −2.01（見 TK 拆解第79列起，營運費用固定）')
setp(4,2,'廠房 capex：TK 12.67 $M/MW 相對 IREN 原文如何？（原問題誤以 14–16 為資料中心本體）')
setp(4,3,'不改。B 段撤回「偏低」：對 IREN 本體 9–11，TK 偏高；加叢集部署 12–14 則持平')
setp(4,4,'廠房改為 IREN 值')
setp(4,5,'每 +1 $M/MW（＝+1 $B/GW）約 +0.1436 $B/GW·年＝廠房資本回收 1.5019＋廠房維護 0.2534＋財產稅 0.0634（0.5% 總資本）÷ 廠房 capex 12.67（GB300；含土地年金與預備費攤銷）。改用 9–11／12–14／15 → −0.38／+0.05／+0.33')
setp(5,3,'保留作機隊層級對照，不當價格；1.25GW 已確認為 (0.6+1.9)/2 線性內插')
setp(5,5,'若採用，倍數 1.37–1.55（分子 16.0／16.3 × 線性／指數 GW），與同口徑長約相反')
setp(6,2,'Oracle 算式：300÷5 年÷5GW＝12.0（Andy）；4.5GW 版本 13.3')
setp(6,3,'並列 5GW（IT 12.0／設施 14.4）與 4.5GW（IT 13.3／設施 16.0），標明各自出處；不影響結論：對 VR200 為 0.98–1.31 倍')
setp(6,4,'只用單一 GW 版本')
setp(6,5,'對 VR200 倍數 0.98–1.31')

# ---- 第二輪：CoreWeave 10-Q 債務與查核修正
e=wb['外部價格換算']; q=wb['對帳']; p=wb['待判斷']; z=wb['證據']
e['G32']="設施 5GW ÷ PUE 1.2 ＝ IT"
e['B16']=e['B16'].value.replace('Andy 算式；','分子取 Epoch 方法頁 16.3（Andy 記錄的約值 16.0 為 12.8／1.37，見 B 段頁第2節）；')
for row in q.iter_rows():
    for c in row:
        if isinstance(c.value,str):
            if c.value.startswith('X6a 支出÷1.25GW（使用者算式）'): c.value='X6a 支出 16.3÷1.25GW（16.0 版＝12.8）'
            if '「12–12.8」型數字' in c.value: c.value=c.value.replace('「12–12.8」型數字','「12–13」型數字（16.0 版 12.8，倍數 1.37／1.52；16.3 版 13.04，倍數 1.39／1.55）')
            if '缺 CoreWeave 10-Q 的 cost of revenue／折舊／租賃費' in c.value: c.value=c.value.replace('缺 CoreWeave 10-Q 的 cost of revenue／折舊／租賃費','2026Q2 已有營業成本與折舊（證據 E22、E26），仍缺租賃費明細與 2025Q4 同口徑資料')
            if '缺 CoreWeave 季報 10-Q 的 cost of revenue／折舊／租賃費' in c.value: c.value=c.value.replace('缺 CoreWeave 季報 10-Q 的 cost of revenue／折舊／租賃費','2026Q2 已有營業成本與折舊（證據 E22、E26），仍缺租賃費明細與 2025Q4 同口徑資料')
q['F20']='修正（B 段第二輪）：先前稱「租金低於 TK 主要是出租方折現率較低」不成立。以 IREN 自己的 capex 與營運下界反推，隱含 WACC 約 9–10%；差額主要來自 IT 設備單價與營運費用（見 B 段頁第6節）。IREN 3.31% 融資只是個案，CoreWeave 債務 9.6–9.9%。'
for row in z.iter_rows(min_row=2):
    if row[0].value=='E20': row[2].value=row[2].value.replace('$16B','$16.0B（約值；方法頁為 16.3）')
    if row[0].value=='E22': row[7].value=str(row[7].value)+'｜已補：E26（債務、損益、客戶）；仍缺 active power 定義（10-Q 只讀前約 80/181 頁）'
z.append(['E26','CoreWeave 2026Q2 10-Q 續（chat 端由 Drive PDF 讀取；僅讀前約 80/181 頁）','(1) active power／contracted power 在已讀範圍內未找到定義與數值；租約附註只有站點電力：393MW、355MW（2026–2028 交付）、DCSP 最多 78MW，只寫 electrical power，未標 IT 或 gross。(2) GPU 耐用年限未找到（附註1空白）。PP&E（$M，6/30/26 對 12/31/25）：Technology equipment 33,823／20,903；Data center equipment & leasehold 5,997／2,842；CIP 11,918／9,376；淨額 46,736／30,557；Q2 折舊 $1.4B。(3) 債務 Note 10 有效利率與餘額：見 B 段頁第6節 16 列；原文唯一加權平均：OEM 短期工具 9%。DDTL 4.0 為 SOFR+2.25% 或 Treasury+2.00%，DDTL 5.0 為 SOFR+4.50%。(4) 損益：營收 2,575；營業成本 879（含資料中心租金、電力、電力系統折舊；增加額中租金約 +335、電力約 +87、電力系統折舊約 +79）；技術與基礎設施 1,507（折舊約 1,300）；營業損失 (49)；利息費用淨額 (640)；淨損 (626)。(5) 客戶 A 36%、B 26%、C 10%；98% 營收來自承諾合約；RPO $103.7B（41% 在 24 個月內、39% 在 25–48 個月）；加權平均合約期間未找到；資料中心租約期 5–15 年。','Drive 02-算力收支/Tokenomics/inbox/（10-Q PDF）','2026-10-23','Verified（公司申報）；加權平均為 Derived','部分（後半未讀到）','加權平均利率為 chat 端按餘額加權：全部 8.4%、不含可轉債 9.9%、DDTL 9.6%；本檔重算一致'])
for c in z[z.max_row]: c.alignment=Alignment(wrap_text=True,vertical='top')
def setp(n,col,val):
    for i in range(2,p.max_row+1):
        if p.cell(i,1).value==n: p.cell(i,col,val); p.cell(i,col).alignment=Alignment(wrap_text=True,vertical='top')
setp(1,5,'使用 9.35 時，Oracle／支出÷GW 的倍數相對同世代分母虛高約 1.16–1.31 倍（÷GB300 對 ÷組合 1.16；÷VR200 對 ÷組合 1.31；見對帳 D 節）')
setp(2,3,'不改模型。TK 以 10% 為基準；出租方資金成本依公司分列：IREN 3.31%（Microsoft 擔保＋預付款，個案）、CoreWeave 債務 9.6–9.9%。先前「出租方 3–8%」只適用 IREN 個案')
setp(4,5,'每 +1 $M/MW（＝+1 $B/GW）約 +0.1436 $B/GW·年＝廠房資本回收 1.5019＋廠房維護 0.2534＋財產稅 0.0634（0.5% 總資本）÷ 廠房 capex 12.67（GB300；含土地年金與預備費攤銷）。廠房取 10／13／15 $M/MW（本體中點／含叢集中點／全包）→ −0.38／+0.05／+0.33')
for rw in [(12,'是否把 Project 決定第 2 題的「出租方折現率 3–8%」改為依公司分列？','是：IREN 3.31%（個案）、CoreWeave 債務 9.6–9.9%；README 已據此撤回「WACC 是主因」','維持 3–8% 區間','「WACC 主因」結論被推翻：以 IREN 自己的 capex 與營運反推，隱含 WACC 約 9–10%；差額主因為 IT 設備單價與營運費用','B 段頁第6節；證據 E26'),
(13,'TK GB300 的 IT 設備（32.2 $B/GW）比 IREN（29.0）高 11%，且營運費用高 36%：要查嗎？','先不改模型；列為待查（機架單價 $4.3M、GPU 密度 kW／GPU、Dell 大單折扣、營運範圍定義）','TK 下調','兩項合計約 1.27 $B/GW（約 12%）','B 段頁第6節')]:
    for j,x in enumerate(rw,1):
        c=p.cell(p.max_row+1 if j==1 else p.max_row,j,x); c.alignment=Alignment(wrap_text=True,vertical='top')
# B 段 D80 說明
bs=wb['B 段']
for row in bs.iter_rows():
    for c in row:
        if isinstance(c.value,str) and c.value.startswith('CoreWeave 營業成本含租賃機房與電力'): c.value=c.value+'；分母不同（營收 vs 持有成本）：34%×營收 8.24≈2.81，30%×持有成本 9.35≈2.82，絕對值吻合'

# ---- 第三輪：決定 #12/#13 與第二輪查核修正
setp(2,7,'決定（Andy，2026-10-23）：不改模型；同列 10% 與出租方折現率。「3–8%」已被 #12 取代，改依公司分列（IREN 3.31%、CoreWeave 債務 9.6–9.9%）')
setp(10,3,'要，只寫進查證檔不改模型；債務利率已取得（B 段第6節），active power 定義與 GPU 耐用年限待 10-Q 後半')
setp(10,7,'決定（Andy）：要，只寫查證檔不改模型。狀態：部分完成（10-Q 只讀前約 80/181 頁；債務利率已取得）')
setp(12,7,'決定（Andy，2026-10-23）：改為依公司分列。IREN 3.31% 是 Microsoft 擔保加預付款的個案，不能代表出租方')
setp(13,7,'決定（Andy）：先不改模型，列為證據待查。兩項合計約占持有成本 12%，目前只有 IREN 一個對照點，營運 1.455 只是下界（不含企業管理費）；等有第二個對照點再判斷')
for row in bs.iter_rows():
    for c in row:
        if c.value=='未取得（待 Drive inbox 的 10-Q 全文）': c.value='部分取得（10-Q 只讀前約 80/181 頁）'
        elif c.value=='active power 定義、GPU 耐用年限、債務利率': c.value='債務利率已取得（第6節）；active power 定義、GPU 耐用年限仍未取得'
        elif isinstance(c.value,str) and c.value.startswith('→ 有了債務利率才能'): c.value='→ 債務利率已用於第6節：出租方折現率改依公司分列（待判斷 #12，已決定）'
q['F22']='已被 B 段第6節取代：此值是固定 TK 的 capex 與營運下求得，混入了 capex 與營運差異。以 IREN 自己的 capex 反推：營運取下界 1.455 時 9.0–10.2%（上限），取 TK 營運 1.98 時 7.2–8.4%。'

wb.save(out); print('saved')

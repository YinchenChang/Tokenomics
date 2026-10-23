# 由證據清單同時產生 證據原稿.md 與 Q側缺口_A段.xlsx（數字用公式可追溯）
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

D = os.path.dirname(os.path.abspath(__file__))
HDR = ["編號","項目","主張原句／內容","數值","單位","口徑","期間","出處網址","出處日期","取得方式","等級","立場","對應名稱","支持或反駁"]
OA = "https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/"
EP = "https://epoch.ai/data-insights/openai-compute-spend"
EF = "https://epoch.ai/gradient-updates/frontier-labs-dont-use-most-ai-compute"
EM = "https://epoch.ai/data/ai-chip-users-documentation/methodology"
# 編號, 項目, 內容, 數值, 單位, 口徑, 期間, 網址, 日期, 取得, 等級, 立場, 名稱, 因子
E = [
("W1-01","W1","The Information 報導（付費牆未讀）：2025 推論成本約 84 億，約為 2024 的 4 倍，高於夏季預測 66 億；其中免費用戶約 39 億、付費用戶約 45 億。 / Inference costs ~$8.4B, ~4x 2024, above the $6.6B summer forecast; ~$3.9B free users, ~$4.5B paying.","8.4","$B","推論成本（用於毛利率分子）；含免費用戶；是否含 RL／內部使用未明","2025 全年（報導於 2026-02 前後，為實際）","https://finance.biggo.com/news/mRiPlZwBTwP6zY3HRxp-（及 aiafterhours、controlplane、safeguard 同源轉述）","約 2026-02-24","二手（同源算 1 個）","3","The Information 為媒體；OpenAI 無誘因誇大成本","SRC_DEM_004","口徑：84 億含免費；不含 Microsoft 自家產品推論（Epoch 推定）"),
("W1-02","W1","毛利率 2025 為 33%，低於 2024 的 40% 與內部目標 46%；原因：需求超預期，後期以較貴價格買算力。 / adjusted gross margin 33% vs 40% (2024), target 46%; 'buy more expensive compute at the last minute'.","33 / 46","%","adjusted gross margin（營收減推論成本）","2025","同 W1-01","約 2026-02","二手","3","同上","SRC_DEM_004","價格因子：隨需加價，但無金額或比例"),
("W1-03","W1","內部指標 compute margin 2025-10 約 70%（2024 底 52%），不含訓練與管銷；OpenAI 發言人稱未公開。 / 'compute margin' ~70% Oct 2025, excludes training and overhead.","70","%","不同於 33%","2025-10","https://fortune.com/2025/12/21/openai-compute-margins-revenue-chatgpt-earnings-sam-altman/（搜尋摘要）","2025-12-21","二手","3","The Information 轉述","—","說明 84 億僅為推論，不含訓練"),
("W1-04","W1","Sacra：2025 推論 84 億，2026 預測 141 億（+68%）；多站轉述同一 Sacra 估計。 / Sacra: inference $8.4B 2025, $14.1B 2026.","8.4 / 14.1","$B","推論；2026 為預測","2025／2026","https://sacra.com/c/openai/（搜尋摘要；本環境 DNS 失敗）","2026","二手（同源）","3–4","Sacra 為研究賣方","SRC_DEM_004","與 W1-01 同數，非獨立"),
("W1-05","W1","某電子報引 The Information：OpenAI「預期去年花 94 億美元於訓練模型的算力」（日期不明，可能為預測）。 / 'expected to spend $9.4 billion on compute for training its AI models last year'.","9.4","$B","訓練算力；預測 vs 實際不明","2025（推定）","https://aiafterhours.substack.com/p/openai-vs-anthropic-the-121-billion（搜尋摘要；頁面本環境無法開啟）","未明","二手","4","—","SRC_DEM_006","反駁 120 億：最接近的外部訓練數為 94 億，非 120 億"),
("W1-06","W1","2025 訓練 120 億的外部原文：已搜尋，未找到（見「未找到」）。20261023 利用率 A 段另有 15 組查詢亦未找到。","—","—","—","—","—","—","—","—","—","SRC_DEM_006","無外部背書"),
("W1-07","W1","Epoch 對 2024：訓練 30 億、推論 18 億、研究算力 10 億（分攤兩年得 20 億）；R&D 算力合計 50 億；推論 'likely excludes Microsoft's own inference spending on licensed OpenAI models'。","30 / 18 / 10","$B","2024 投資人文件經記者轉述","2024",EP,"2025","原文","3","獨立研究機構","SRC_DEM_004/006 口徑","口徑：R&D 算力含大量實驗；訓練與研究的邊界 OpenAI 未公開"),
("W1-08","W1","The Information（經 The Decoder）：OpenAI 計畫 2026 訓練花 320 億、2027 約 650 億。 / plans to spend $32B on model training in 2026 and ~$65B in 2027.","32 / 65","$B","訓練；預測","2026／2027","https://the-decoder.com/openai-adds-111-billion-to-its-cash-burn-forecast-as-ai-costs-spiral-beyond-projections/","2026-02","二手","3","—","—","W4：2026 訓練預測"),
("W1-09","W1","H1 2025 研發費用 67 億（營收 43 億；現金燃燒約 25 億），來自 The Information 對股東文件的報導。 / R&D cost $6.7B in the first half.","6.7","$B","研發費用整體（非僅算力）","2025 H1","https://finance.yahoo.com/news/openais-first-half-revenue-rises-043012507.html（搜尋摘要）","2025-09-29","二手（Reuters 轉述）","3","—","—","無法由此推全年算力；只可作研發費用方向"),
("W1-10","W1","OpenAI 2025 查核財報（chat 端已查，不重查）：營業成本 75、研發 191.8、付 Microsoft 172.1 億，其中研發 105.9。Zitron 另報付 Microsoft 項目：研發 10.59、營業成本 6.047、銷售 0.527、管理 0.042 十億。","75 / 191.8 / 172.1 / 105.9","億$","chat 端已查","2025","見 Drive 筆記（chat 端併入）","2026-06","chat 端已查","—","—","—","（見 README）"),
("W1-11","W1","研發付 Microsoft 105.9 億中訓練與研究推論的拆分：已搜尋，未找到任何報導拆分。Zitron 僅稱『研發』『最可能是訓練模型成本』（其個人推論）。","—","—","—","2025","—","—","—","—","—","SRC_DEM_006","無拆分"),
("W1-12","W1","沿用 20261023 利用率 A 段：SRC_DEM_018（Azure 推論累計 12.6）中約 65.5 億未進 OpenAI 營業成本，最可能是研究推論（模型 v5.36 備註）。本段未重新驗證。","65.5","億$","沿用，未驗證","2025","docs/evidence/20261023_利用率服務占比_A段/抽查報告.md","2026-10-23","沿用（repo）","—","—","SRC_DEM_018","研究推論約 65 億屬研發付費，不在 84 億（營業成本口徑）內"),
("W3-01","W3","Oracle：OpenAI 同意每年付 Oracle 約 300 億美元數據中心服務（Oracle 申報：FY2028 起年收入逾 300 億）；容量 4.5 GW。換算 300／4.5＝66.7 億／GW·年；若 5 年 3000 億則 133 億／GW·年。 / agreed to pay Oracle ~$30B a year.","30 / 4.5","$B/年；GW","雲端合約（含硬體與服務）；GW 口徑未明；2027 年中起，非 2025 價格","FY2028 起","https://techcrunch.com/2025/07/22/openai-agreed-to-pay-oracle-30b-a-year-for-data-center-services（搜尋摘要）","2025-07-22","二手","2","Oracle 申報事實；4.5 GW 為媒體","—","價格因子：下限 0.72（6.7／9.353）至 1.42（13.3／9.353）"),
("W3-02","W3","CoreWeave：OpenAI 合約 2025-03 最多 119 億、2025-05 +40 億、2025-09 +65 億，合計約 224 億；無 MW。 / total contract value up to ~$22.4B.","22.4","$B","合約上限；無容量","至 2030-10","https://investors.coreweave.com/news/news-details/2025/CoreWeave-Expands-Agreement-with-OpenAI-by-up-to-6-5B/default.aspx","2025-09","原文（公司新聞稿，搜尋摘要）","1","公司申報","—","無法換算（只有金額）"),
("W3-03","W3","CoreWeave 2025Q3：活躍電力約 590 MW（+120 MW）、合約電力約 2.9 GW、營收 13.65 億。以平均活躍約 530 MW 計，約 1000 萬美元／MW·年（本段自算，全客戶混合）。","≈10","$B/GW·年","全客戶；活躍電力口徑公司未明（本段視為 IT 的近似）","2025Q3","https://investors.coreweave.com/news/news-details/2025/CoreWeave-Reports-Strong-Third-Quarter-2025-Results/","2025-11","原文＋自算","1（原數）／Derived","公司申報","—","價格因子參考 1.07（含 GPU 租賃全服務）"),
("W3-04","W3","Cerebras：750 MW、至 2028、價值逾 100 億（『people close to the company』，非公告值）。若期間 2–3 年：44–67 億／GW·年。","10 / 0.75","$B；GW","晶圓級系統，不同硬體；起始 2026","2026–2028","https://www.cnbc.com/2026/01/14/cerebras-scores-openai-deal-worth-over-10-billion.html（搜尋摘要）","2026-01-14","二手","3","—","—","非同類硬體，僅作範圍"),
("W3-05","W3","AWS：380 億美元、7 年；約 54 億／年；無 MW（『數十萬 GB200／GB300』僅單一部落格）。","38","$B/7年","合約；無容量","2025-11 起 7 年","https://tomtunguz.com/openai-hardware-spending-2025-2035/（搜尋摘要）","2025-11","二手","2–3","—","—","無法換算"),
("W3-06","W3","Azure 牌價（第三方追蹤站）：ND H100 v5 隨需約 12.29 美元／小時，1 年預留 7.93，3 年預留 5.47；另一站稱承諾折扣上限 1 年 38%、3 年 62%。SKU 是否為每 GPU 價未確認。","12.29 / 7.93 / 5.47","$/小時","公開牌價，非 OpenAI 實付","2026","https://www.thundercompute.com/blog/azure-gpu-instances（搜尋摘要）","2026","二手","3","第三方比價站","—","預留／隨需＝0.65（1年）、0.45（3年）；僅示範隨需價差規模"),
("W3-07","W3","OpenAI 實付每 GPU 小時或對 Azure／Oracle／CoreWeave 的折扣率：已搜尋，未找到任何官方、洩漏或可靠報導。Microsoft 對 OpenAI 的關聯方定價：未找到。","—","—","—","—","—","—","—","—","—","—","價格因子無直接證據"),
("W3-08","W3","『OpenAI 因需求超預期購買隨需算力』：僅見毛利率下滑歸因（W1-02），無金額或比例。","—","—","—","2025","同 W1-02","—","二手","3","—","—","價格因子方向向上，量不明"),
("W3-09","W3","同口徑長約 ÷ TK（沿用 20261023 持有成本口徑差 B 段）：0.89–1.12。","0.89–1.12","倍","沿用，未重驗","—","docs/evidence/20261023_持有成本口徑差_B段/","2026-10-23","沿用（repo）","—","—","AL_FleetHold","價格因子主區間"),
("W4-01","W4","Brockman 法庭證詞：OpenAI 2026 預計算力支出 500 億美元（Reuters 2026-05-05）；報導並稱為 2025 的三倍。 / expects to spend $50 billion on computing power this year.","50","$B","算力支出（口徑未明）；證詞，無文件","2026","https://seekingalpha.com/news/4586132-brockman-says-openai-to-spend-50b-on-computing-power-in-2026","2026-05-05","二手（Reuters）","2","證詞當事人","—","W4"),
("W4-02","W4","Epoch 引報導：OpenAI 2025 雲端算力支出 160 億；Brockman『triple what it spent in 2025』→ 隱含 2025 約 167 億，與 160 億一致。","16","$B","雲端算力總支出","2025",EF,"2026","二手（原文頁）","3","獨立研究機構引媒體","—","口徑因子：2025 總算力支出 160 億 < 84＋120＝204 億"),
("W4-03","W4","2026 平均上線 GW：已搜尋，未找到官方或可信數字。僅有交易層級資料（Nvidia 50 億瓦含推論 3、訓練 2 GW 等）與 2027『low-double-digit GW』內部預測。","—","—","—","2026","—","—","—","—","—","AL_FleetGW26","無"),
("W4-04","W4","Sacra 2026 推論預測 141 億；The Information 2026 訓練計畫 320 億 → 合計 461 億，對 500 億支出（W4-01）約 0.92。","46.1","$B","預測加總","2026","見 W1-04、W1-08","—","Derived","—","—","—","2026 兩項合計≈總支出；2025 兩項（204）＞總支出（160）"),
]
NF = [
("N01","W1 訓練 120 億原文","OpenAI 2025 training compute $12 billion；OpenAI 2025 training compute spending actual vs projected；OpenAI training compute 2025 $9.4 billion OR $12 billion The Information","最近為 94 億（W1-05，日期不明）；120 億未找到"),
("N02","W1 84 億原文","The Information Why OpenAI Anthropic Missed Their Own Gross Margin Forecasts；OpenAI inference $8.4 billion","只見二手轉述；原文付費牆"),
("N03","W1(c) 研發付 Microsoft 105.9 拆分","OpenAI paid Microsoft 10.59 billion research development training inference split","無報導拆分"),
("N04","W1 H1 2025 算力拆分","OpenAI H1 2025 R&D compute 6.7 billion compute-only breakdown","只有研發費用 67 億，無算力分項"),
("N05","W3 OpenAI 實付每 GPU 小時","OpenAI price per GPU hour Azure discount rate H100 GB200 OpenAI pays Microsoft below list price","無"),
("N06","W3 Microsoft 對 OpenAI 的關聯方定價","同上","無"),
("N07","W3 CoreWeave／AWS 合約 MW","CoreWeave OpenAI contract MW capacity；OpenAI AWS 38 billion capacity","無 MW"),
("N08","W3 隨需購買金額或比例","OpenAI bought on-demand compute 2025 higher prices amount","無"),
("N09","W4 2026 平均上線 GW","OpenAI 2026 year-end gigawatts target compute capacity end of 2026；Brockman testimony 2026 average capacity GW","無"),
("N10","W2 Azure 占比（承接上一輪）","見 W2_優先查證.md","無"),
]
CHAT = ["openai.com 原文（HTTP 403）","sec.gov：Microsoft 10-Q／10-K、CoreWeave、Oracle 申報","wheresyoured.at、nextplatform.com、deepquarry.substack.com、sacra.com、aiafterhours.substack.com、safeguard.sh、controlplane.news、techcrunch.com、cnbc.com、finance.yahoo.com（本環境 DNS 失敗，改用搜尋摘要）","The Information 原文（付費牆）"]
JD = [
("J1","SRC_DEM_006（訓練 120 億）出處標『待補』，數值先不改","只標記，不改值","本段未找到原文；最近外部數為 94 億（日期不明）"),
("J2","口徑因子：204 億（84＋120）超過 Epoch 引的 2025 雲端總支出 160 億，是否要在 B4_Serve 分母改用 160 或 84＋76","維持現值 0.41，於報告標註敏感度","改動屬判斷類；兩條路對 0.41 的影響請見 README 敏感度"),
("J3","價格因子是否由 0.85 改採 1.0–1.4 區間","等 chat 端讀 SEC 與 Drive 筆記後定","本段無 OpenAI 實付 $/GPU·小時"),
("J4","GW 因子","維持 AL_FleetGW25=1.128（你已決定 GW 不調）","官方端點內插已落在 1.0–1.25"),
]

# ---- 證據原稿.md
L = ["# 證據原稿（Q 側缺口 A 段）","","基準 master `4ef0b0a`；分支 `claude/evidence-q-gap-a`。W2 部分見 `W2_優先查證.md`。等級：1 官方申報…4 傳聞。同源只算 1 個來源。","","| "+" | ".join(HDR)+" |","|"+"---|"*len(HDR)]
for r in E:
    L.append("| "+" | ".join(str(x).replace("|","/") for x in r)+" |")
L += ["","## 已搜尋，未找到","","| 編號 | 項目 | 查詢字串 | 結果 |","|---|---|---|---|"]
for r in NF: L.append("| "+" | ".join(r)+" |")
L += ["","## 交 chat 端（本環境讀不到）",""]+["- "+c for c in CHAT]
open(os.path.join(D,"證據原稿.md"),"w",encoding="utf-8").write("\n".join(L)+"\n")

# ---- xlsx
wb = Workbook(); hf = Font(bold=True); fill = PatternFill("solid", fgColor="DDEBF7"); blue = Font(color="0000FF")
def head(ws, row, vals):
    for i,v in enumerate(vals,1):
        c = ws.cell(row=row, column=i, value=v); c.font = hf; c.fill = fill
ws = wb.active; ws.title = "三因子"
ws["A1"] = "輸入（藍字＝來自 Tokenomics 或證據；其餘為公式）"; ws["A1"].font = hf
inp = [("推論支出 SRC_DEM_004（$B）",8.4),("訓練支出 SRC_DEM_006（$B）",12),("服務 GW（L1_ServeGW_GW25）",0.4624),("機隊每 GW 年持有成本 AL_FleetHold（$B）",9.353),("機隊平均上線 GW AL_FleetGW25",1.128),("Epoch 引 2025 雲端算力總支出（$B）",16)]
for i,(k,v) in enumerate(inp,2):
    ws.cell(row=i,column=1,value=k); c = ws.cell(row=i,column=2,value=v); c.font = blue
ws["A9"]="TK 服務算力成本（$B）"; ws["B9"]="=B4*B5"
ws["A10"]="9a 缺口（推論÷TK 服務成本）"; ws["B10"]="=B2/B9"
ws["A11"]="推論＋訓練（$B）"; ws["B11"]="=B2+B3"
ws["A12"]="總缺口（204÷(平均GW×持有成本)）"; ws["B12"]="=B11/(B6*B5)"
ws["A13"]="Epoch 160 ÷ 204（s 的上限代理）"; ws["B13"]="=B7/B11"
ws["A15"]="(b) 平均 GW 取不同值時，扣除 GW 後剩餘缺口 R＝總缺口÷GW因子"; ws["A15"].font = hf
head(ws,16,["平均 GW 情境","GW（實際）","GW 因子＝GW÷1.128","剩餘缺口 R＝B12÷GW因子"])
for i,g in enumerate([1.0,1.128,1.25],17):
    ws.cell(row=i,column=1,value=["低（1.0）","模型（1.128）","高（1.25）"][i-17]); c=ws.cell(row=i,column=2,value=g); c.font=blue
    ws.cell(row=i,column=3,value=f"=B{i}/$B$6"); ws.cell(row=i,column=4,value=f"=$B$12/C{i}")
ws["A21"]="(c) 必須為真：價格因子 P 給定時，口徑因子 1/s＝R÷P，s＝204 億中屬當年上線算力費用的比例"; ws["A21"].font = hf
head(ws,22,["價格因子 P（OpenAI 實付÷9.353）","依據","1/s（GW=1.0）","s（GW=1.0）","1/s（GW=1.128）","s（GW=1.128）","1/s（GW=1.25）","s（GW=1.25）"])
prices=[(0.89,"同口徑長約低端（B 段）"),(1.07,"CoreWeave 全客戶約 10 億／GW·年（W3-03，Derived）"),(1.12,"同口徑長約高端（B 段）"),(1.42,"Oracle 3000 億／5 年／4.5 GW 高端（W3-01）")]
for i,(p,t) in enumerate(prices,23):
    c=ws.cell(row=i,column=1,value=p); c.font=blue; ws.cell(row=i,column=2,value=t)
    for j,(gr,col) in enumerate([(17,3),(18,5),(19,7)]):
        ws.cell(row=i,column=col,value=f"=$D${gr}/$A{i}"); ws.cell(row=i,column=col+1,value=f"=1/{chr(64+col)}{i}")
ws["A28"]="(d) 獨立證據相乘能否重現總缺口"; ws["A28"].font=hf
head(ws,29,["情境","GW因子","價格因子","口徑因子 1/s","乘積","對照總缺口(B12)","乘積÷總缺口"])
sc=[("低",0.887,0.89,1.0),("中",1.0,1.07,"=1/B13"),("高",1.108,1.42,"=1/B13")]
for i,(n,g,p,k) in enumerate(sc,30):
    ws.cell(row=i,column=1,value=n)
    for col,v in [(2,g),(3,p),(4,k)]:
        c=ws.cell(row=i,column=col,value=v); 
        if not (isinstance(v,str) and v.startswith("=")): c.font=blue
    ws.cell(row=i,column=5,value=f"=B{i}*C{i}*D{i}"); ws.cell(row=i,column=6,value="=$B$12"); ws.cell(row=i,column=7,value=f"=E{i}/F{i}")
ws["A34"]="註：口徑因子中檔／高檔取 1/s＝204÷160（Epoch 雲端總支出），為 Derived 且與總支出口徑同源，僅示範量級。"
ws["A36"]="(e) 兩年一致性（Assumed 區間，不是來源值）"; ws["A36"].font=hf
head(ws,37,["項目","低","高","備註"])
rows=[("2025 總算力支出（$B）","=B7","=B7","Epoch 引報導"),("2025 平均 GW",1.0,1.25,"官方端點內插區間"),("2025 支出÷GW（$B/GW·年）","=B38/C39","=C38/B39","高＝支出÷低GW"),
      ("2026 總算力支出（$B）",50,50,"Brockman 證詞"),("2026 平均 GW（Assumed）",3.0,4.5,"無來源；沿用上一輪粗估 3.5–4，這裡放寬"),("2026 支出÷GW（$B/GW·年）","=B41/C42","=C41/B42",""),("÷9.353 持有成本（2025）","=B40/$B$5","=C40/$B$5",""),("÷9.353 持有成本（2026）","=B43/$B$5","=C43/$B$5","")]
for i,r in enumerate(rows,38):
    for j,v in enumerate(r,1):
        c=ws.cell(row=i,column=j,value=v)
        if j in (2,3) and not (isinstance(v,str)): c.font=blue
ws.column_dimensions["A"].width=48
for col in "BCDEFGH": ws.column_dimensions[col].width=22

w2 = wb.create_sheet("證據"); head(w2,1,HDR)
for i,r in enumerate(E,2):
    for j,v in enumerate(r,1):
        c=w2.cell(row=i,column=j,value=v); c.alignment=Alignment(wrap_text=True,vertical="top")
for col,wd in zip("ABCDEFGHIJKLMN",[8,6,60,10,8,26,14,36,12,12,8,18,14,28]): w2.column_dimensions[col].width=wd

w3 = wb.create_sheet("合約換算"); head(w3,1,["合約","金額（$B）","年數","容量（GW）","每年金額","每 GW·年（$B）","÷9.353 持有成本","備註"])
ct=[("Oracle（300 億／年版）",30,1,4.5,"W3-01；FY2028 起"),("Oracle（3000 億／5 年版）",300,5,4.5,"W3-01 另一版本；兩版互相矛盾，未解"),("Cerebras（3 年）",10,3,0.75,"W3-04；不同硬體"),("Cerebras（2 年）",10,2,0.75,"W3-04"),("AWS（7 年，無容量）",38,7,None,"W3-05；無法換算")]
for i,(n,a,y,g,nt) in enumerate(ct,2):
    w3.cell(row=i,column=1,value=n); 
    for col,v in [(2,a),(3,y),(4,g)]:
        c=w3.cell(row=i,column=col,value=v); c.font=blue
    w3.cell(row=i,column=5,value=f"=B{i}/C{i}")
    if g: w3.cell(row=i,column=6,value=f"=E{i}/D{i}"); w3.cell(row=i,column=7,value=f"=F{i}/三因子!$B$5")
    else: w3.cell(row=i,column=6,value="無法換算")
    w3.cell(row=i,column=8,value=nt)
w3.cell(row=8,column=1,value="CoreWeave（Q3 營收 $B，平均活躍 GW）"); w3.cell(row=8,column=2,value=1.365).font=blue; w3.cell(row=8,column=3,value=0.25).font=blue; w3.cell(row=8,column=4,value=0.53).font=blue
w3.cell(row=8,column=5,value="=B8/C8"); w3.cell(row=8,column=6,value="=E8/D8"); w3.cell(row=8,column=7,value="=F8/三因子!$B$5"); w3.cell(row=8,column=8,value="季營收×4÷平均活躍電力；全客戶；W3-03（Derived）")
w3.column_dimensions["A"].width=34; w3.column_dimensions["H"].width=50

w4 = wb.create_sheet("未找到"); head(w4,1,["編號","項目","查詢字串","結果"])
for i,r in enumerate(NF,2):
    for j,v in enumerate(r,1): w4.cell(row=i,column=j,value=v)
w4.cell(row=len(NF)+3,column=1,value="交 chat 端").font=hf
for i,c in enumerate(CHAT,len(NF)+4): w4.cell(row=i,column=1,value=c)
w4.column_dimensions["B"].width=34; w4.column_dimensions["C"].width=70; w4.column_dimensions["D"].width=40

w5 = wb.create_sheet("待判斷"); head(w5,1,["編號","事項","建議預設","理由"])
for i,r in enumerate(JD,2):
    for j,v in enumerate(r,1): w5.cell(row=i,column=j,value=v).alignment=Alignment(wrap_text=True,vertical="top")
w5.column_dimensions["B"].width=60; w5.column_dimensions["C"].width=40; w5.column_dimensions["D"].width=50
wb.save(os.path.join(D,"Q側缺口_A段.xlsx"))

# -*- coding: utf-8 -*-
RET='2026-10-15'
IP='Interested-party'
SELL='賣方（模型商）自家牌價；價格事實以官方頁確認，立場為銷售方'
CSELL='賣方（雲端商）自家牌價；立場為銷售方'
rows=[]
def add(**k):
    d=dict(group='',series='',item='',tier='',kind='',value=None,unit='',date='',source='',url='',docdate='',marker=IP,interest='',note='')
    d.update(k); d['ret']=RET; rows.append(d)

# ---------- (b) 層級牌價：每筆輸入、輸出各一列合併成 in/out 欄 ----------
B=[]  # (provider, tier, model, date, in, out, source, url, docdate, note)
def b(prov,tier,model,date,i,o,src,url,note='',marker=IP,interest=SELL):
    B.append(dict(prov=prov,tier=tier,model=model,date=date,i=i,o=o,src=src,url=url,note=note,marker=marker,interest=interest))
O='OpenAI'
b(O,'中階','GPT-4 (8K)','2023-03-14',30,60,'openai.com/index/gpt-4-research/','https://openai.com/index/gpt-4-research/','當時為旗艦')
b(O,'中階','GPT-4 Turbo','2023-11-06',10,30,'openai.com DevDay 公告','https://openai.com/index/new-models-and-developer-products-announced-at-devday/','當時為旗艦')
b(O,'中階','GPT-4o','2024-05-13',5,15,'OpenAI Developer Community 官方公告貼文','https://community.openai.com/t/announcing-gpt-4o-in-the-api/744700','當時為旗艦；openai.com 本站頁無絕對價')
b(O,'中階','GPT-4o-2024-08-06','2024-08-06',2.5,10,'openai.com structured outputs 公告','https://openai.com/index/introducing-structured-outputs-in-the-api/','新快照降價')
b(O,'中階','GPT-4.1','2025-04-14',2,8,'openai.com/index/gpt-4-1/','https://openai.com/index/gpt-4-1/','')
b(O,'中階','GPT-5','2025-08-07',1.25,10,'openai.com GPT-5 for developers','https://openai.com/index/introducing-gpt-5-for-developers/','')
b(O,'中階','GPT-5.2','2025-12-11',1.75,14,'openai.com/index/introducing-gpt-5-2/','https://openai.com/index/introducing-gpt-5-2/','')
b(O,'中階','GPT-5.4','2026-03-05',2.5,15,'openai.com/index/introducing-gpt-5-4/','https://openai.com/index/introducing-gpt-5-4/','')
b(O,'中階','GPT-5.6 Terra（上市價）','2026-07-09',2.5,15,'openai.com/index/gpt-5-6/','https://openai.com/index/gpt-5-6/','2026-07-30 降 20%')
b(O,'中階','GPT-5.6 Terra（降價後）','2026-07-30',2.0,12,'openai.com/index/gpt-5-6/ 與 developers.openai.com changelog','https://developers.openai.com/api/docs/changelog','由 20% 降幅推得（Derived）',marker='Derived')
b(O,'中階','GPT-6 Sol','2026-09-22',2,10,'openai.com/index/introducing-gpt-6-sol-and-luna/；changelog','https://openai.com/index/introducing-gpt-6-sol-and-luna/','層級名換位：GPT-6 的 Sol 為中階')
b(O,'中階','GPT-6.1 Sol','2026-09-29',2,10,'developers.openai.com changelog','https://developers.openai.com/api/docs/changelog','快取 0.10')
b(O,'旗艦','GPT-4 (8K)','2023-03-14',30,60,'openai.com/index/gpt-4-research/','https://openai.com/index/gpt-4-research/','')
b(O,'旗艦','GPT-4 Turbo','2023-11-06',10,30,'openai.com DevDay','https://openai.com/index/new-models-and-developer-products-announced-at-devday/','')
b(O,'旗艦','GPT-4o','2024-05-13',5,15,'OpenAI Developer Community 官方公告','https://community.openai.com/t/announcing-gpt-4o-in-the-api/744700','')
b(O,'旗艦','GPT-5','2025-08-07',1.25,10,'openai.com GPT-5 for developers','https://openai.com/index/introducing-gpt-5-for-developers/','')
b(O,'旗艦','GPT-5.2','2025-12-11',1.75,14,'openai.com GPT-5.2','https://openai.com/index/introducing-gpt-5-2/','')
b(O,'旗艦','GPT-5.4','2026-03-05',2.5,15,'openai.com GPT-5.4','https://openai.com/index/introducing-gpt-5-4/','')
b(O,'旗艦','GPT-5.6 Sol（上市價）','2026-07-09',5,30,'openai.com/index/gpt-5-6/','https://openai.com/index/gpt-5-6/','2026-08-21 起促銷 4/20，至少至 2026-11-21')
b(O,'旗艦','GPT-6 Astra','2026-09-03',10,50,'developers.openai.com changelog（上市日）、openai.com/index/gpt-6-astra/（價格）','https://openai.com/index/gpt-6-astra/','')
A='Anthropic'
b(A,'中階（Sonnet）','Claude 3 Sonnet','2024-03-04',3,15,'anthropic.com/news/claude-3-family','https://www.anthropic.com/news/claude-3-family','')
b(A,'中階（Sonnet）','Claude 3.5 Sonnet','2024-06-21',3,15,'anthropic.com/news/claude-3-5-sonnet','https://www.anthropic.com/news/claude-3-5-sonnet','')
b(A,'中階（Sonnet）','Claude 3.7 Sonnet','2025-02-24',3,15,'anthropic.com/news/claude-3-7-sonnet','https://www.anthropic.com/news/claude-3-7-sonnet','')
b(A,'中階（Sonnet）','Claude Sonnet 4','2025-05-22',3,15,'anthropic.com/news/claude-4','https://www.anthropic.com/news/claude-4','')
b(A,'中階（Sonnet）','Claude Sonnet 4.5','2025-09-29',3,15,'anthropic.com/news/claude-sonnet-4-5','https://www.anthropic.com/news/claude-sonnet-4-5','')
b(A,'中階（Sonnet）','Claude Sonnet 4.6','2026-02-17',3,15,'anthropic.com/news/claude-sonnet-4-6','https://www.anthropic.com/news/claude-sonnet-4-6','')
b(A,'中階（Sonnet）','Claude Sonnet 5','2026-06-30',2,10,'anthropic.com/news/claude-sonnet-5','https://www.anthropic.com/news/claude-sonnet-5','2026-08-10 起「introductory 2/10 變永久」；新 tokenizer（同文字約 1.0–1.35× token）')
b(A,'中階（Sonnet）','Claude Sonnet 5.5','2026-09-28',2,10,'anthropic.com/news/claude-sonnet-5-5','https://www.anthropic.com/news/claude-sonnet-5-5','')
b(A,'旗艦（Opus）','Claude 3 Opus','2024-03-04',15,75,'anthropic.com/news/claude-3-family','https://www.anthropic.com/news/claude-3-family','')
b(A,'旗艦（Opus）','Claude Opus 4','2025-05-22',15,75,'anthropic.com/news/claude-4','https://www.anthropic.com/news/claude-4','')
b(A,'旗艦（Opus）','Claude Opus 4.5','2025-11-24',5,25,'anthropic.com/news/claude-opus-4-5','https://www.anthropic.com/news/claude-opus-4-5','頁面未標輸入／輸出，$5/$25 依 platform.claude.com 定價頁')
b(A,'旗艦（Opus）','Claude Opus 5','2026-07-24',5,25,'anthropic.com/news/claude-opus-5','https://www.anthropic.com/news/claude-opus-5','與 Opus 4.8 同價')
b(A,'旗艦（Opus）','Claude Opus 5.5','2026-09-22',4,20,'platform.claude.com/docs/en/models/opus-5-5/overview','https://platform.claude.com/docs/en/models/opus-5-5/overview','')
b(A,'頂層（Fable）','Claude Fable 5','2026-06-09',10,50,'platform.claude.com/docs/en/models/fable-5/overview','https://platform.claude.com/docs/en/models/fable-5/overview','Fable 價高於 Opus 5.5')
G='Google'
b(G,'旗艦（Pro）','Gemini 1.5 Pro（≤128K）','2024-05-23',3.5,10.5,'Google AI Developers Forum 使用者貼文（輸入 3.50）；輸出 10.5 由 2024-09-24 降幅（輸入 −64%、輸出 −52%）與降後 1.25/5 反推','https://discuss.ai.google.dev/t/pay-as-you-go-plan-of-gemini-pro-1-5-3-5-million-tokens-meaning/3375','找不到官方頁絕對價；輸出為 Derived',marker='Derived',interest='賣方牌價；官方一手頁缺，輸入來自社群貼文')
b(G,'旗艦（Pro）','Gemini 1.5 Pro（降價後，≤128K）','2024-10-01',1.25,5,'developers.googleblog.com（2024-09-24）降幅 + 反推','https://developers.googleblog.com/en/updated-production-ready-gemini-models-reduced-15-pro-pricing-increased-rate-limits-and-more/','官方只給降幅；1.25/5 為推算相符值',marker='Derived')
b(G,'旗艦（Pro）','Gemini 2.5 Pro（≤200K）','2025-04-04',1.25,10,'ai.google.dev 現行定價頁（價）；blog.google 2025-04-04（開始計費日，價為圖片）','https://ai.google.dev/gemini-api/docs/pricing','日期為首次公開計費日；2025-06-17 GA 同價')
b(G,'旗艦（Pro）','Gemini 3 Pro（≤200K）','2025-11-18',2,12,'blog.google/technology/developers/gemini-3-developers/；changelog（上市日）','https://blog.google/technology/developers/gemini-3-developers/','')
b(G,'旗艦（Pro）','Gemini 3.1 Pro Preview（≤200K）','2026-02-19',2,12,'ai.google.dev 定價頁；changelog（上市日）','https://ai.google.dev/gemini-api/docs/pricing','')
b(G,'旗艦（Pro）','Gemini 4 Argon（導入價）','2026-10-13',2,10,'blog.google Gemini 4 Argon；ai.google.dev 定價頁','https://ai.google.dev/gemini-api/docs/pricing','導入價至 2026-11-30，之後 4/20')
b(G,'中階（Flash）','Gemini 2.5 Flash（GA）','2025-06-17',0.30,2.50,'developers.googleblog.com Gemini 2.5 更新','https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/','')
b(G,'中階（Flash）','Gemini 3 Flash','2025-12-17',0.50,3.00,'blog.google/products/gemini/gemini-3-flash/','https://blog.google/products/gemini/gemini-3-flash/','')
b(G,'中階（Flash）','Gemini 3.6 Flash（原價，由 3.7 公告反推）','2026-07-21',1.50,7.50,'blog.google Gemini 3.7 Flash（「導入價為 3.6 Flash 原價的一半」）；changelog 上市日','https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/','Derived；3.6 Flash 現行頁標導入價 0.75/3.75',marker='Derived')
b(G,'中階（Flash）','Gemini 3.7 Flash（導入價）','2026-08-13',0.75,3.75,'blog.google Gemini 3.7 Flash','https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/','2027-01-01 起 1.5/7.5')

# ---------- (a) 同等能力 token 價格 ----------
A_=[]  # dict
EP='Epoch AI（Cottier 等）2025-03-12'
EPU='https://epoch.ai/data-insights/llm-inference-price-trends'
def a(series,model,date,val,unit,note,marker='Derived',src=EP,url=EPU,docdate='2025-03-12',interest='非銷售方（研究機構）；價格為 3:1 輸入:輸出混合（由 GPT-4 30/60→37.5 驗證）'):
    A_.append(dict(series=series,model=model,date=date,val=val,unit=unit,note=note,marker=marker,src=src,url=url,docdate=docdate,interest=interest))
S1='a1 MMLU≥GPT-4-0314（86.0）最低價'
for m,d,v,n in [('GPT-4-0314','2023-03-14',37.50,'計算：(3×30+60)/4'),('GPT-4 Turbo','2023-11-06',15.00,'計算：(3×10+30)/4'),('GPT-4o-2024-05','2024-05-13',7.50,'計算：(3×5+15)/4'),('Gemini-1.5-Pro-2024-05','2024-05-23',2.19,'計算：(3×1.25+5)/4；用的是 2024-10 降價後的價格，日期卻是模型發布日；時點與價格不同步'),('Gemini 2.0 Flash','2025-02-05',0.18,'')]:
    a(S1,m,d,v,'$/M（3:1 混合）',n)
S2='a2 GPQA Diamond≥33（GPT-4-0314 水準）最低價'
for m,d,v,n in [('GPT-4-0314','2023-03-14',37.50,''),('GPT-4 Turbo','2023-11-06',15.00,''),('Mistral-Large-2024-02','2024-02-26',6.00,''),('Claude-3-Haiku','2024-03-04',0.50,'計算：(3×0.25+1.25)/4'),('Gemini-1.5-Flash-2024-05','2024-05-10',0.13,'同上，價格可能為降價後'),('Phi 4','2024-12-13',0.12,'')]:
    a(S2,m,d,v,'$/M（3:1 混合）',n)
# 速率型
a('a3 彙總速率（Epoch 2025）','GPQA 達 GPT-4-0314 水準','2023-03→2025-02',40,'倍／年','Epoch：價格每年下降 40 倍；各門檻範圍 9–900 倍／年；「最快的下降發生在最近一年，不確定是否持續」',marker='Derived')
a('a3 彙總速率（Epoch 2026）','五個基準平均（AIME、棋題、FrontierMath 1–3、GPQA Diamond、Mystery Game）','2023→2026',13,'倍／年（≈每季 −47%）','成本＝達到固定準確度的實際花費（含推理 token，由測試逐題紀錄計算），不是牌價；最前沿 −66%／季（75 倍／年）；SOTA 後兩年 −32%／季（4.7 倍／年）；開源模型以租用硬體計價',marker='Derived',src='Epoch AI「The plunging price of thought」（Emberson、Roodman）',url='https://epoch.ai/publications/the-plunging-price-of-thought',docdate='2026-09-22（2026-09-23 更新）',interest='研究機構；成本口徑含推理 token')
a('a3 彙總速率（Epoch 2026）','o3（2025-01-31）→ GPT-5.6 Luna（約 18 個月後）達 GPQA Diamond 75%','2025-01→2026-07',725,'倍（每題成本 $0.30→$0.0004）','Epoch 舉例',marker='Derived',src='Epoch AI「The plunging price of thought」',url='https://epoch.ai/publications/the-plunging-price-of-thought',docdate='2026-09-22')
a('a3 彙總速率（學術）','前沿模型達固定基準分數的成本（知識、推理、數學、軟體工程基準）','2022→2025',7.5,'倍／年（5–10 倍）','Gundlach、Lynch、Mertens、Thompson（arXiv 2511.23455v2）：演算法效率約 3 倍／年；前沿模型的執行價格另以每年 3–18 倍上升',marker='Derived',src='arXiv 2511.23455v2「The Price of Progress」',url='https://arxiv.org/abs/2511.23455v2',docdate='2026-03-23（v2）',interest='學術研究')
# 同一模型壽命內降價
C_=[]
def c_(model,date,old,new,unit,note,src,url,docdate,marker=IP,interest=SELL):
    C_.append(dict(model=model,date=date,old=old,new=new,unit=unit,note=note,src=src,url=url,docdate=docdate,marker=marker,interest=interest))
c_('o3','2025-06-10','10/40（圖說）','2/8','$/M 輸入／輸出（−80%）','舊價僅見於圖說（AI 產生圖說），官方文字只給新價 2/8','OpenAI Developer Community「o3 is 80% cheaper」','https://community.openai.com/t/o3-is-80-cheaper-and-introducing-o3-pro/1284925','2025-06-10')
c_('Gemini 1.5 Pro','2024-10-01','3.5/10.5（推算）','1.25/5（推算）','輸入 −64%／輸出 −52%','官方只給降幅','developers.googleblog.com','https://developers.googleblog.com/en/updated-production-ready-gemini-models-reduced-15-pro-pricing-increased-rate-limits-and-more/','2024-09-24')
c_('GPT-5.6 Luna','2026-07-30','—','—','−80%','官方只給降幅','developers.openai.com changelog','https://developers.openai.com/api/docs/changelog','2026-07-30')
c_('GPT-5.6 Terra','2026-07-30','2.5/15','2/12（推算）','−20%','','openai.com/index/gpt-5-6/','https://openai.com/index/gpt-5-6/','2026-07-30')
c_('GPT-5.6 Sol','2026-08-21','5/30','4/20','輸入 −20%／輸出 −33%（促銷，至少至 2026-11-21）','','developers.openai.com changelog','https://developers.openai.com/api/docs/changelog','2026-08-21')
c_('AWS P5（H100）on-demand','2025-06-01','~12.29/GPU-hr（推算：55.04÷0.56÷8）','6.88/GPU-hr','−44%（Savings Plans −25% 至 −45%）','此項屬算力租賃，列此供對照','AWS 部落格「up to 45% price reduction」；instances.vantage.sh（現價）','https://aws.amazon.com/blogs/aws/announcing-up-to-45-price-reduction-for-amazon-ec2-nvidia-gpu-accelerated-instances/','2025-06',marker='Derived',interest=CSELL)
c_('Claude Sonnet 5','2026-08-10','（原訂 9/1 起 3/15）','2/10 轉為永久','未實現的漲價取消','','anthropic.com/news/claude-sonnet-5','https://www.anthropic.com/news/claude-sonnet-5','2026-08-10')

# ---------- (c) 算力租賃價格 ----------
Cc=[]
def cc(gpu,layer,gen,date,val,unit,vendor,src,url,docdate,marker=IP,interest=CSELL,note=''):
    Cc.append(dict(gpu=gpu,layer=layer,gen=gen,date=date,val=val,unit=unit,vendor=vendor,src=src,url=url,docdate=docdate,marker=marker,interest=interest,note=note))
# A100
cc('A100 80GB','隨需','Ampere（A100）','現價（頁面未標日）',2.79,'$/GPU-hr','Lambda','lambda.ai/pricing','https://lambda.ai/pricing','（無）')
cc('A100 80GB','隨需','Ampere（A100）','現價（頁面未標日）',2.70,'$/GPU-hr','CoreWeave','coreweave.com/pricing（8 卡 $21.60÷8）','https://www.coreweave.com/pricing','（無）')
cc('A100 8 卡 p4d','隨需','Ampere（A100）','2025-06 降價後現價',2.745,'$/GPU-hr','AWS','instances.vantage.sh（彙整 AWS 牌價 $21.958÷8）；AWS 部落格確認 2025-06-01 降 33%','https://instances.vantage.sh/aws/ec2/p4d.24xlarge','2026-10-15',marker='Derived',note='二手彙整站')
cc('A100 8 卡 p4d','預留 1 年','Ampere（A100）','2025-06 降價後現價',1.740,'$/GPU-hr','AWS','instances.vantage.sh（$13.921÷8）','https://instances.vantage.sh/aws/ec2/p4d.24xlarge','2026-10-15',marker='Derived',note='二手彙整站')
cc('A100 8 卡 p4d','預留 3 年','Ampere（A100）','2025-06 降價後現價',1.172,'$/GPU-hr','AWS','instances.vantage.sh（$9.374÷8）','https://instances.vantage.sh/aws/ec2/p4d.24xlarge','2026-10-15',marker='Derived',note='二手彙整站')
# H100
cc('H100 PCIe','隨需','Hopper（H100）','2023-05-10',2.40,'$/GPU-hr','Lambda','lambda.ai/blog/lambda-cloud-deploys-nvidia-h100-tensor-core-gpus（上市後約 1–2 個月）','https://lambda.ai/blog/lambda-cloud-deploys-nvidia-h100-tensor-core-gpus','2023-05-10',note='1 卡 PCIe')
cc('H100 SXM 8x','隨需','Hopper（H100）','2023-08-02',2.59,'$/GPU-hr','Lambda','lambda.ai 部落格（8x H100 SXM 隨需）','https://lambda.ai/blog/lambda-cloud-deploys-on-demand-nvidia-hgx-h100-with-8x-h100-sxm-instances','2023-08-02')
cc('H100 SXM 8x','隨需','Hopper（H100）','2024-10-07',2.99,'$/GPU-hr','Lambda','lambda.ai 部落格（1x $3.29／2x $3.19／4x $3.09／8x $2.99）','https://lambda.ai/blog/creating-more-options-for-ai-developers-new-1x-2x-and-4x-sxm','2024-10-07')
cc('H100 SXM','隨需','Hopper（H100）','現價（頁面未標日）',3.99,'$/GPU-hr','Lambda','lambda.ai/pricing','https://lambda.ai/pricing','（無）',note='高於 2024-10 的 2.99')
cc('H100 1-Click Cluster','預留（最短 1 週）','Hopper（H100）','2024-06-03',4.49,'$/GPU-hr','Lambda','lambda.ai 1-Click Clusters 公告','https://lambda.ai/blog/introducing-lambda-1-click-clusters-a-new-way-to-train-large-ai-models','2024-06-03（2024-08-16 更新）')
cc('H100 8 卡 HGX','隨需','Hopper（H100）','現價（頁面未標日）',6.16,'$/GPU-hr','CoreWeave','coreweave.com/pricing（$49.24÷8）；另稱預留承諾最高折 60%','https://www.coreweave.com/pricing','（無）')
cc('H100','隨需','Hopper（H100）','現價（頁面頁尾 2026，圖檔 2024-12）',4.50,'$/GPU-hr','Nebius','nebius.com/prices（可能過時）；稱大型叢集承諾折扣最高約 35%','https://nebius.com/prices','（無）',note='頁面日期不明')
cc('H100 p5.48xlarge','隨需','Hopper（H100）','2025-06 降價後現價',6.88,'$/GPU-hr','AWS','instances.vantage.sh（$55.04÷8）；降幅出自 AWS 部落格','https://instances.vantage.sh/aws/ec2/p5.48xlarge','2026-10-15',marker='Derived',note='二手彙整站')
cc('H100 p5.48xlarge','隨需（降價前）','Hopper（H100）','2023-07-26 上市價（推算）',12.29,'$/GPU-hr','AWS','由 $55.04÷(1−0.44)÷8 推算；P5 GA 日 2023-07-26 見 AWS What\'s New；上市原價未直接讀到','https://aws.amazon.com/about-aws/whats-new/2023/07/amazon-ec2-p5-instances-generative-ai-hpc-generally-available/','2023-07-26',marker='Derived',note='推算值')
cc('H100 p5.48xlarge','預留 3 年','Hopper（H100）','2025-06 降價後現價',2.972,'$/GPU-hr','AWS','instances.vantage.sh（$23.777÷8）','https://instances.vantage.sh/aws/ec2/p5.48xlarge','2026-10-15',marker='Derived',note='二手彙整站')
cc('H100（Silicon Data 指數）','隨需（指數，超大規模雲）','Hopper（H100）','2023-08～2023-12',7.76,'$/GPU-hr（中位）','Silicon Data','Silicon Data 部落格「H100 Rental Price Over Time」','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='指數供應商自家文章；方法不透明、與資料來源無法獨立驗證',note='區間 7.62–7.77')
cc('H100（Silicon Data 指數）','隨需（指數，超大規模雲）','Hopper（H100）','2025-07～2025-12',6.26,'$/GPU-hr（中位）','Silicon Data','同上','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='同上')
cc('H100（Silicon Data 指數）','隨需（指數，新雲）','Hopper（H100）','2024-06～2024-12',2.99,'$/GPU-hr（中位）','Silicon Data','同上','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='同上')
cc('H100（Silicon Data 指數）','隨需（指數，新雲）','Hopper（H100）','2025-07～2025-12',3.33,'$/GPU-hr（中位）','Silicon Data','同上','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='同上')
cc('H100（Silicon Data 指數）','隨需（指數，市集）','Hopper（H100）','2024-06～2024-12',2.58,'$/GPU-hr（中位）','Silicon Data','同上','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='同上')
cc('H100（Silicon Data 指數）','隨需（指數，市集）','Hopper（H100）','2025-07～2025-12',1.95,'$/GPU-hr（中位）','Silicon Data','同上','https://www.silicondata.com/blog/h100-rental-price-over-time','2025-12-21',interest='同上')
cc('H100 SDH100RT 指數','隨需（指數，新雲）','Hopper（H100）','2026-10-14',2.85,'$/GPU-hr','Silicon Data','silicondata.com/products/silicon-index/h100','https://www.silicondata.com/products/silicon-index/h100','2026-10-14',interest='同上；同頁 FAQ 寫 2.53，頁內不一致',note='頁內兩個數字不一致（2.85／2.53）')
# B200
cc('B200 SXM6 8x','隨需','Blackwell（B200）','2025-08-12',4.99,'$/GPU-hr','Lambda','lambda.ai/blog/nvidia-b200-lambda-on-demand-cloud（頁面 2025-11-05 更新）','https://lambda.ai/blog/nvidia-b200-lambda-on-demand-cloud','2025-08-12',note='Lambda 的 B200 上市日；CoreWeave 在 2025-02 已上線 GB200')
cc('B200 SXM6','隨需','Blackwell（B200）','現價（頁面未標日）',6.69,'$/GPU-hr','Lambda','lambda.ai/pricing','https://lambda.ai/pricing','（無）',note='高於 2025-08 的 4.99；getdeploying 稱 B200 中位隨需價 12 個月 +19%')
cc('B200 1-Click Cluster','預留（2 週～1 年，16／64／256+ 卡）','Blackwell（B200）','現價（頁面未標日）','9.86／9.36／8.87','$/GPU-hr','Lambda','lambda.ai/service/gpu-cloud/1-click-clusters','https://lambda.ai/service/gpu-cloud/1-click-clusters','（無）')
cc('B200 HGX 8 卡','隨需','Blackwell（B200）','現價（頁面未標日）',8.60,'$/GPU-hr','CoreWeave','coreweave.com/pricing（$68.80÷8）','https://www.coreweave.com/pricing','（無）')
cc('B200','隨需','Blackwell（B200）','現價（頁面日期不明）',8.50,'$/GPU-hr','Nebius','nebius.com/prices','https://nebius.com/prices','（無）')
cc('B200 p6-b200.48xlarge','隨需','Blackwell（B200）','現價',14.24,'$/GPU-hr','AWS','instances.vantage.sh（$113.933÷8）','https://instances.vantage.sh/aws/ec2/p6-b200.48xlarge','2026-10-15',marker='Derived',note='二手彙整站')
cc('B200（多家業者中位）','隨需','Blackwell（B200）','2026-10-15',7.94,'$/GPU-hr（中位數，67 組）','getdeploying.com 彙整','getdeploying.com/gpus/nvidia-b200','https://getdeploying.com/gpus/nvidia-b200','2026-10-15',marker='Analogy',interest='彙整站含贊助商標示；僅作橫斷面對照',note='預留中位 5.62；隨需中位 90 天 +4%、12 個月 +19%')
# GB200
cc('GB200 NVL72（4 GPU 單位）','隨需','GB200','現價（頁面未標日）',10.50,'$/GPU-hr','CoreWeave','coreweave.com/pricing（$42.00÷4）；與 SRC_PRC_001 同一牌價，勿重複計入獨立來源','https://www.coreweave.com/pricing','（無）',note='SRC_PRC_001 經 spheron 轉述 2026-05 為同值 $42/4 GPU')
# GB300 / B300
cc('GB300 NVL72（4 GPU 單位）','隨需','GB300','2026-10-14',18.00,'$/GPU-hr','Oracle Cloud','getdeploying.com 彙整 OCI 公開價（BM.GPU.GB300.42）','https://getdeploying.com/gpus/nvidia-gb300','2026-10-14',marker='Analogy',note='OCI 官方頁價格欄未擷取到（頁面更新 2026-08-25）；此值為二手彙整')
cc('GB300（1x 配置）','隨需','GB300','2026-10-14',11.28,'$/GPU-hr','Verda','getdeploying.com 彙整','https://getdeploying.com/gpus/nvidia-gb300','2026-10-14',marker='Analogy',note='標示缺貨')
cc('GB300（1x 配置）','預留 24 個月','GB300','2026-10-14',8.46,'$/GPU-hr','Verda','getdeploying.com 彙整','https://getdeploying.com/gpus/nvidia-gb300','2026-10-14',marker='Analogy',note='標示缺貨')
cc('B300','隨需','GB300 世代（單卡 B300）','現價（頁面日期不明）',9.50,'$/GPU-hr','Nebius','nebius.com/prices','https://nebius.com/prices','（無）',note='B300 單卡，非 NVL72')
cc('GB300 NVL72','隨需／預留','GB300','2026-10-14','（聯絡業務）','','CoreWeave、Nebius、AWS、Together AI、Gcore','getdeploying.com 彙整與各家定價頁','https://getdeploying.com/gpus/nvidia-gb300','2026-10-14',note='已搜尋，未找到公開標價')
# VR200
cc('VR200 NVL72','隨需／預留','VR200','—','（無）','','CoreWeave 2026-09-30 宣布供應，未載價格','coreweave.com/news（Cognition 首位客戶）','https://www.coreweave.com/news/coreweave-delivers-nvidia-vera-rubin-nvl72-performance-at-production-scale-starting-with-cognition','2026-09-30',note='已搜尋，未找到公開價格')

cc('GB300 長約（IREN—Microsoft，5 年、200 MW 關鍵 IT 負載）','長約（5 年；含 20% 預付）','GB300','2025-11-03',9.70,'$M/MW-IT/年（= $9.7B ÷ 5 年 ÷ 200 MW；Derived）','IREN（賣方揭露）','iren.com 公告（合約價值約 $9.7B、五年、200 MW 關鍵 IT 負載、20% 預付）','https://iren.com/resources/blog/iren-signs97-billion-agreement-with-microsoft-to-deploy-ai-cloud-infrastructure','2025-11-03',marker='Interested-party',interest='賣方公司自行揭露；只記單價，不記合約組合、客戶細節或公司指引',note='與 Excel 契約第 4 節對帳提醒 9.70 一致；公告未載 GPU 數')
cc('GB300 長約（Nebius—Microsoft，5 年）','長約（5 年）','GB300','2025-09-09','（無法換算）','','Nebius（賣方揭露）','DCD 轉述（合約 $17.4B，至多 $19.4B；公告未載 MW 與 GPU 數）','https://datacenterdynamics.com/en/news/microsoft-to-use-nebius-gpu-data-centers-in-deal-worth-174bn-over-five-years','2025-09-09',marker='Interested-party',interest='賣方揭露；二手轉述',note='缺 MW／GPU 數，無法換算單價；不列入實算')

# DeepInfer vs TK v21.7 核算（所有輸入見註解出處）
# DeepSeek 公布（Interested-party）
pre_total=1.5e6; pre_fresh=60e3; dec=14e3        # tok/s/卡：prefill 含快取、prefill 未快取、decode 輸出
p_hit,p_miss,p_out=0.003,0.15,0.60               # 谷價 $/M（官方價目，經二手轉述）
rev_pair=(pre_fresh*p_miss+(pre_total-pre_fresh)*p_hit+dec*p_out)*3600/1e6  # 1 prefill卡+1 decode卡 每小時
print("每卡時營收重建 $", rev_pair/2, "分項(每卡):", pre_fresh*p_miss*3600/1e6/2,(pre_total-pre_fresh)*p_hit*3600/1e6/2,dec*p_out*3600/1e6/2)
tok_s=155e12/86400; pairs=tok_s/(pre_total+dec); print("155T/日 → tok/s",tok_s," 推得卡數",2*pairs)
print("日營收 $M",2*pairs*38*24/1e6, " 若用 Latent Space $0.14/M 全量：",155e12*0.14/1e6/1e6)
print("輸入:輸出", (pre_total)/dec, " 每請求輸出(77K輸入)", 77e3*dec/pre_total)
# TK v21.7 GB200 Luna（Perf F 欄、Theory_Rev、Spec）
gpu_gw=6969*72; hold=8.82816556596761e9
print("TK GB200 每 GW GPU", gpu_gw, " 持有成本 $/GPU-hr", hold/(gpu_gw*8760))
rack_dec=332263.857377723; rack_pre=2658110.85902178; chi=0.55
d=rack_dec/72; pr=rack_pre/72
rt=(pr*(1-chi)*p_miss+pr*chi*p_hit+d*p_out)*3600/1e6
print("TK Luna GB200 每卡平均 decode",d," prefill",pr," 以DS谷價每卡時營收",rt, "分項",pr*(1-chi)*p_miss*3600/1e6,pr*chi*p_hit*3600/1e6,d*p_out*3600/1e6)
print("DS 每卡平均 decode",dec/2," fresh",pre_fresh/2," cached",(pre_total-pre_fresh)/2)
print("38 ÷ 持有成本", 38/(hold/(gpu_gw*8760)), " 每 GW 年營收 $B", 38*gpu_gw*8760/1e9)
# decode 前緣：TK 每序列每步 0.319ms vs DeepInfer 斜率
tau=3.25; pts={8:(325,2600),16:(314.5,5050),32:(297,9500),64:(246,15700),128:(178.5,22800),256:(103,26300)}
st={b:tau/v*1000 for b,(v,t) in pts.items()}
print("步時 ms", {b:round(s,2) for b,s in st.items()})
for a,b in [(8,64),(64,128),(128,256)]: print(a,b,"每序列 ms",(st[b]-st[a])/(b-a))
flops=4*32.82e9  # TK Luna 每步 4 token 算力（TK 架構）
for ms in (0.05,0.104): print("隱含 η_d", flops/(ms/1000)/10e15)
print("TK η_d 0.0411；TK 固定延遲 8.70ms；DeepInfer 外推固定約", st[8]-8*(st[64]-st[8])/56)
# 同 per-user 速度比較 + τ 調整
print("TK GB200 Luna 84 tok/s/user → 5,636；DeepInfer 103 tok/s/user → 26,300；倍數", 26300/5636, " τ 調整後", 26300/5636/(3.25/2.533))
print("生產/基準：14K/15.7K", 14/15.7)
# 儲存
print("SSD 每卡 $/hr (TK SSD 單價, 14.4TB×1.2)", 14.4e3*1.2*2.28310502283105e-06)

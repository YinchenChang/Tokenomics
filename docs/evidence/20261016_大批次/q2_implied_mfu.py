"""Q2／Q3：各實測點隱含的整步有效 MFU（Derived），以及 Hopper 中等互動速度點的模型同條件值（工作簿同一條式的 Python 重現）。

用法：python3 q2_implied_mfu.py <v10.2.xlsx> <輸出 json>
隱含 MFU＝每 GPU 輸出 tok/s × 每輸出 token 的 FLOPs（decode＋分攤的 prefill）÷ 計算用峰值。
FLOPs 用工作簿 Calib 第 101、109 列的 DeepSeek-V3／R1 架構（37B 啟用；MLA 注意力 4,997,120 FLOP／被注意 token）。
"""
import json
import sys

import openpyxl

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
C = wb["Calib"]
ACT = C["C101"].value * 1e9
ATT = C["C109"].value


def dflops(ctx):
    return (2 * ACT + ATT * ctx) / 1e9


def pflops(isl):
    return (2 * ACT + ATT * isl / 2) / 1e9


def per_out(isl, osl, agg):
    """每輸出 token 的 GFLOP；agg＝True 表示同一批 GPU 也做 prefill（MLPerf、trtllm-bench）。"""
    f = dflops(isl + osl / 2)
    if agg:
        f += isl / osl * pflops(isl)
    return f


PEAK = {"H100/H800/H200": 1.979, "H20": 0.296, "GB200": 10.0, "GB300": 15.0}
pts = [
    # 名稱, 硬體, 每 GPU tok/s, ISL, OSL（decode-only 點以 decode 平均上下文換算）, 是否含 prefill, 每用戶 tok/s, 每 GPU 序列（約）
    ("MLPerf v6.0 GB200 NVIDIA interactive", "GB200", 3337.8, 800, 3880, True, 66.7, 50),
    ("MLPerf v6.0 GB200 NVIDIA server", "GB200", 4668.1, 800, 3880, True, 12.5, 373),
    ("MLPerf v6.0 GB200 NVIDIA offline", "GB200", 6752.0, 800, 3880, True, None, None),
    ("MLPerf v6.0 GB300 NVIDIA interactive", "GB300", 3481.0, 800, 3880, True, 66.7, 52),
    ("MLPerf v6.0 GB300 NVIDIA server", "GB300", 5561.6, 800, 3880, True, 12.5, 445),
    ("MLPerf v6.0 GB300 NVIDIA offline", "GB300", 8987.2, 800, 3880, True, None, None),
    ("TRT-LLM H200 8GPU batch 1（MTP）", "H100/H800/H200", 19.7584, 1000, 2000, True, 158.1, 1),
    ("TRT-LLM H200 8GPU 並行 1024（128/rank）", "H100/H800/H200", 1436.16, 1000, 2000, True, 11.35, 128),
    ("DeepSeek profile（H800，decode-only）", "H100/H800/H200", 2324, 4096, 0, False, 18.2, 128),
    ("DeepSeek 線上（H800，decode-only）", "H100/H800/H200", 1850, 4989, 0, False, 21, 88),
    ("LMSYS 96×H100（decode-only）", "H100/H800/H200", 2785, 2000, 2000, False, 10, 278),
    ("vLLM GB200 WideEP（decode-only）", "GB200", 10100, 2000, 2000, False, None, None),
    ("LMSYS GB200 NVL72（decode-only，NVFP4）", "GB200", 13386, 2000, 2000, False, 10, 1339),
    ("Ant H20 InferX Base（TPOT<70 ms，MTP）", "H20", 714, 3000, 0, False, 14.9, 48),
    ("Ant H20 InferX Pro（TPOT<50 ms，MTP）", "H20", 675, 3000, 0, False, 21.1, 32),
    ("Ant H20 InferX Max（TPOT<30 ms，MTP）", "H20", 423, 3000, 0, False, 35.3, 12),
]
out = []
for name, hw, tps, isl, osl, agg, spu, b in pts:
    gf = per_out(isl, osl, agg)
    mfu = tps * gf * 1e9 / (PEAK[hw] * 1e15)
    out.append(dict(點=name, 硬體=hw, tok_s_GPU=tps, 每輸出token_GFLOP=round(gf, 2), 隱含MFU=round(mfu, 4),
                    每用戶tok_s=spu, 每GPU序列約=b))
    print(f"{name:42s} {hw:15s} {tps:9.1f}  {gf:6.1f} GF  MFU {mfu*100:5.2f}%")

# Q3：InferenceX H200（旁證）8K／1K、SGLang FP8；模型同條件值以 Calib J 節公式重現（H200 規格、EP8、無 MTP）
eta_h = C["C70"].value
lat_h = C["C71"].value
L = C["C102"].value
hbm, bw, epbw = 141 * 0.9, 4.8, 0.05
ctx = 8192 + 1024 / 2
q3 = []
F = c = kv = ep = cap = None
for EP, d in ((8, 0), (64, 0), (64, 3)):
    a = (1 - 0.7 ** (d + 1)) / (1 - 0.7) if d else 1.0
    w = C["C113"].value * 1 + C["C114"].value * 1 / EP
    F = w / bw + (L + d) * lat_h / 1000
    c = (d + 1) * dflops(ctx) / (1.979 * eta_h) / 1000
    kv = C["C108"].value * ctx / (bw * 0.7) / 1e9
    ep = (d + 1) * L * C["C105"].value * C["C103"].value * 3 * (EP - 1) / EP / (epbw * 0.7) / 1e9
    cap = (hbm - w) * 1e9 / (C["C108"].value * ctx)
    for S, meas in ((30, 1582), (50, 1235), (75, 932), (100, 739)):
        per = max(c, kv, ep)
        B = max(0, min((1000 * a / S - F) / per, cap))
        dec = B * a / ((F + B * per) / 1000) if B > 0 else 0
        pre = C["C72"].value * 1.979e15 / (pflops(8192) * 1e9)  # Hopper η_p × 峰值 ÷ prefill FLOPs
        tot = (8192 + 1024) / (8192 / pre + 1024 / dec) if dec > 0 else 0  # InferenceX 口徑：每 GPU 總 token（輸入＋輸出）
        q3.append(dict(EP=EP, 草稿數=d, 每用戶tok_s=S, InferenceX_總token_tok_s_GPU=meas, 模型B=round(B, 1),
                       模型decode輸出=round(dec, 1), 模型總token=round(tot, 1), 模型除以InferenceX=round(tot / meas, 3)))
        print(EP, d, S, meas, round(B, 1), round(dec, 1), round(tot, 1), round(tot / meas, 3))
json.dump({"implied_mfu": out, "q3_inferencex_h200": q3,
           "model_params": dict(eta_d_hopper=eta_h, lat_us_hopper=lat_h, F_ms=F, c_ms=c, kv_ms=kv, ep_ms=ep, cap=cap)},
          open(sys.argv[2], "w"), ensure_ascii=False, indent=1)

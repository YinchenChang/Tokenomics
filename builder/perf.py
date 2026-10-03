# Perf-like column generator: same row logic for Perf (15 cols) and Sens_Perf (scenario cols)
from common import *

def perf_rows(SP, AR, CAL, TR):
    """Row spec: (key, label, unit, fmt, template) ; '§' key = section header. Templates use {X} and row keys."""
    I = lambda sheet, rng, idx: f"=INDEX({sheet}!{rng},{{X}}${idx})"
    sp = lambda r: I("Spec_Rack", f"$C${r}:$G${r}", 6)
    ar = lambda r: I("Arch", f"$C${r}:$E${r}", 7)
    sv = lambda r: I("Serving", f"$C${r}:$E${r}", 7)
    return [
      ("§", "0. Tech_Registry 掛鉤（基準＝1；Registry 未啟用任何條目時與 v5.4 相同）"),
      ("hflop", "FLOPs/token 倍數（H_FLOP）", "x", "0.00", f"={TR['H_FLOP']}"),
      ("hkv", "KV bytes/token 倍數（H_KV）", "x", "0.00", f"={TR['H_KV']}"),
      ("hwb", "權重 bytes/param 倍數（H_WB）", "x", "0.00", f"={TR['H_WB']}"),
      ("§", "A. 規格（連結 Spec_Rack、DC_Cost）"),
      ("P", "計算用峰值", "PF/GPU", "#,##0.000", sp(SP["pk"])),
      ("hbm", "HBM 容量", "GB/GPU", "#,##0", sp(SP["hbm"])),
      ("bw", "HBM 頻寬", "TB/s/GPU", "#,##0.00", sp(SP["bw"])),
      ("link", "EP 通訊頻寬（單向）", "TB/s/GPU", "#,##0.00", sp(SP["link"])),
      ("epb", "decode EP 基準寬度", "GPU", "#,##0", sp(SP["ep"])),
      ("be", "專家權重 bytes/param（含 H_WB）", "B", "0.0000", sp(SP["be"]) + "*{X}{hwb}"),
      ("bn", "非專家權重 bytes/param（含 H_WB）", "B", "0.00", sp(SP["bn"]) + "*{X}{hwb}"),
      ("ninst", "每 prefill 實例 GPU 數", "GPU", "#,##0", sp(SP["ninst"])),
      ("gpus", "GPU 封裝／架", "顆", "#,##0", sp(6)),
      ("gpuw", "GPU 功率", "W", "#,##0", sp(SP["gpuw"])),
      ("ehbm", "HBM 存取能量", "pJ/B", "#,##0", sp(SP["ehbm"])),
      ("racks", "每 GW 機架數（功率情境）", "架", "#,##0", "=INDEX(DC_Cost!$C$12:$Q$12,3*({X}$6-1)+2)/CTL_GW"),   # v5.11 F14: DC_Cost is the facility total
      ("kw", "每架配電設計功率", "kW", "#,##0", "=INDEX(DC_Cost!$C$11:$Q$11,3*({X}$6-1)+2)"),
      ("§", "B. 架構（連結 Arch）"),
      ("A", "啟用參數", "B", "#,##0", ar(AR["A"])),
      ("L", "層數", "層", "#,##0", ar(AR["L"])),
      ("d", "d_model", "", "#,##0", ar(AR["d"])),
      ("k", "啟用 routed experts", "", "#,##0", ar(AR["k"])),
      ("ne", "非專家參數", "B", "#,##0.0", ar(AR["ne"])),
      ("ex", "專家參數", "B", "#,##0", ar(AR["ex"])),
      ("kv", "KV bytes/token（含 H_KV）", "B", "#,##0", ar(AR["kv"]) + "*{X}{hkv}"),
      ("attc", "注意力 FLOPs／被注意 token", "FLOP", "#,##0", ar(AR["attc"])),
      ("ff", "全注意力層比例", "%", "0%", ar(AR["ff"])),
      ("cap", "全注意力跨度上限", "tok", "#,##0", ar(AR["cap"])),
      ("comp", "其他層壓縮比", "x", "#,##0", ar(AR["comp"])),
      ("win", "其他層滑動窗", "tok", "#,##0", ar(AR["win"])),
      ("§", "C. 服務、SLO 與校準參數"),
      ("s", "SLO：每用戶 decode 速度下限", "tok/s", "#,##0", sv(21)),
      ("ttft", "TTFT 上限", "s", "0.0", sv(22)),
      ("isl", "參考 ISL", "tok", "#,##0", sv(23)),
      ("osl", "參考 OSL（含思考）", "tok", "#,##0", sv(24)),
      ("ctxd", "decode 平均上下文", "tok", "#,##0", "={X}{isl}+{X}{osl}/2"),
      ("ctxp", "prefill 平均位置", "tok", "#,##0", "={X}{isl}/2"),
      ("N", "MTP 草稿數", "tok", "0", "=Serving!$C$6"),
      ("alpha", "草稿接受率", "%", "0%", "=Serving!$C$7"),
      ("a", "每步期望接受 token", "tok", "0.00", "=(1-{X}{alpha}^({X}{N}+1))/(1-{X}{alpha})"),
      ("prod", "實測→生產效率折減", "x", "0.00", "=Serving!$C$18"),
      ("etap", "η_p（prefill 占峰值；含折減）", "%", "0.0%", f"=INDEX(Calib!$C${CAL['etap']}:$G${CAL['etap']},{{X}}$6)*{{X}}{{prod}}"),
      ("etadm", "η_d 倍數（Tech_Registry H_ETAD；Sens_Perf 情境覆寫）", "x", "0.00", f"={TR['H_ETAD']}"),
      ("etad", "η_d（decode 每序列算力效率；含折減）", "%", "0.00%", f"=INDEX(Calib!$C${CAL['etad']}:$G${CAL['etad']},{{X}}$6)*{{X}}{{etadm}}*{{X}}{{prod}}"),
      ("tlm", "每層延遲倍數（Tech_Registry H_TL；Sens_Perf 情境覆寫）", "x", "0.00", f"={TR['H_TL']}"),
      ("tl", "每層每次前向固定延遲（含折減）", "µs", "#,##0", f"=INDEX(Calib!$C${CAL['tl']}:$G${CAL['tl']},{{X}}$6)*{{X}}{{tlm}}/{{X}}{{prod}}"),
      ("res", "HBM 保留比例", "%", "0%", "=Serving!$C$9"),
      ("shne", "非專家權重占 HBM 上限", "%", "0%", "=Serving!$C$10"),
      ("shex", "專家權重占 HBM 上限", "%", "0%", "=Serving!$C$11"),
      ("act", "EP 啟用值 bytes/元素", "B", "0.0", "=Serving!$C$12"),
      ("etam", "KV 讀取效率", "%", "0%", "=Serving!$C$13"),
      ("etal", "EP 通訊效率", "%", "0%", "=Serving!$C$14"),
      ("loadbw", "快取載入頻寬", "TB/s", "0.00", "=Serving!$C$15"),
      ("§", "D. 每 token 計算量"),
      ("attd", "decode 被注意 token 數", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxd},MIN({X}{ctxd},{X}{cap}))+(1-{X}{ff})*({X}{ctxd}/{X}{comp}+{X}{win})"),
      ("Fd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attd})*{X}{hflop}/1E9"),
      ("attp", "prefill 被注意 token 數", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxp},MIN({X}{ctxp},{X}{cap}))+(1-{X}{ff})*({X}{ctxp}/{X}{comp}+{X}{win})"),
      ("Fp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attp})*{X}{hflop}/1E9"),
      ("§", "E. 記憶體配置（attention DP＋wide EP；每 GPU）"),
      ("usable", "可用 HBM", "GB", "#,##0", "={X}{hbm}*(1-{X}{res})"),
      ("tpa", "注意力 TP 度（自動）", "", "0", "=MAX(1,CEILING({X}{ne}*{X}{bn}/({X}{shne}*{X}{usable}),1))"),
      ("epw", "decode EP 寬度（自動）", "GPU", "#,##0", "=MAX({X}{epb},CEILING({X}{ex}*{X}{be}/({X}{shex}*{X}{usable}),1))"),
      ("W", "每 GPU 權重", "GB", "#,##0.0", "={X}{ne}*{X}{bn}/{X}{tpa}+{X}{ex}*{X}{be}/{X}{epw}"),
      ("wsh", "權重占可用 HBM", "%", "0%", "={X}{W}/{X}{usable}"),
      ("§", "F. Prefill（算力受限）"),
      ("Pp", "prefill tok/s（每 prefill GPU）", "tok/s", "#,##0", "={X}{etap}*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("ttftv", "TTFT（計算部分）", "s", "0.00", "={X}{isl}*{X}{Fp}*1E9/({X}{etap}*{X}{P}*1E15*{X}{ninst})"),
      ("ttok", "TTFT 符合上限", "", None, "=IF({X}{ttftv}<={X}{ttft},\"是\",\"否\")"),
      ("§", "G. Decode：每步時間＝固定延遲＋B × 每序列時間；B* ＝ min(SLO 上限, HBM 容量上限)"),
      ("tfix", "每步固定延遲（權重讀取＋逐層延遲）", "ms", "#,##0.00", "={X}{W}/{X}{bw}+({X}{L}+{X}{N})*{X}{tl}/1000"),
      ("ccmp", "每序列每步 — 算力項", "ms", "0.0000", "=({X}{N}+1)*{X}{Fd}/({X}{P}*{X}{etad})/1000"),
      ("ckv", "每序列每步 — KV 讀取項", "ms", "0.0000", "={X}{kv}*{X}{ctxd}/({X}{bw}*{X}{etam})/1E9"),
      ("ccom", "每序列每步 — EP 通訊項", "ms", "0.0000", "=({X}{N}+1)*{X}{L}*{X}{k}*{X}{d}*{X}{act}*({X}{epw}-1)/{X}{epw}/({X}{link}*{X}{etal})/1E9"),
      ("ceff", "每序列每步（取最大，假設三者可重疊）", "ms", "0.0000", "=MAX({X}{ccmp},{X}{ckv},{X}{ccom})"),
      ("cbind", "每序列綁定項", "", None, "=IF({X}{ceff}={X}{ccmp},\"算力\",IF({X}{ceff}={X}{ckv},\"KV 頻寬\",\"EP 通訊\"))"),
      ("bslo", "SLO 允許的批次上限", "序列/GPU", "#,##0.0", "=(1000*{X}{a}/{X}{s}-{X}{tfix})/{X}{ceff}"),
      ("bcap", "HBM 容量允許的批次上限", "序列/GPU", "#,##0", "=({X}{usable}-{X}{W})*1E9/({X}{kv}*{X}{ctxd})"),
      ("B", "採用批次 B*", "序列/GPU", "#,##0.0", "=MAX(0,MIN({X}{bslo},{X}{bcap}))"),
      ("D", "decode tok/s（每 decode GPU）", "tok/s", "#,##0", "=IF({X}{B}>0,{X}{B}*{X}{a}/(({X}{tfix}+{X}{B}*{X}{ceff})/1000),0)"),
      ("spd", "實際每用戶速度", "tok/s", "#,##0", "=IF({X}{B}>0,{X}{a}/(({X}{tfix}+{X}{B}*{X}{ceff})/1000),0)"),
      ("bind", "綁定約束", "", None, "=IF({X}{B}<=0,\"SLO 不可達\",IF({X}{bslo}<={X}{bcap},\"SLO（\"&{X}{cbind}&\"）\",\"HBM 容量\"))"),
      ("kvsh", "KV 占可用 HBM", "%", "0%", "={X}{B}*{X}{kv}*{X}{ctxd}/1E9/{X}{usable}"),
      ("§", "H. 每架與每 GW（參考任務；P:D 依工作量配比；100% 利用率）"),
      ("gsr", "每請求 GPU 秒", "GPU-s", "0.000", "=IF({X}{D}>0,{X}{isl}/{X}{Pp}+{X}{osl}/{X}{D},0)"),
      ("psh", "prefill GPU 占比", "%", "0%", "=IF({X}{gsr}>0,({X}{isl}/{X}{Pp})/{X}{gsr},0)"),
      ("rtot", "每架總 tok/s", "tok/s", "#,##0", "=IF({X}{gsr}>0,{X}{gpus}*({X}{isl}+{X}{osl})/{X}{gsr},0)"),
      ("rdec", "每架 decode tok/s", "tok/s", "#,##0", "={X}{rtot}*{X}{osl}/({X}{isl}+{X}{osl})"),
      ("rpre", "每架 prefill tok/s", "tok/s", "#,##0", "={X}{rtot}-{X}{rdec}"),
      ("gwtot", "每 GW 總產出", "M tok/年", "#,##0", "={X}{rtot}*{X}{racks}*8760*3600/1E6"),
      ("gwdec", "每 GW decode 產出", "M tok/年", "#,##0", "={X}{rdec}*{X}{racks}*8760*3600/1E6"),
      ("§", "I. 每 M token GPU 秒（供 Unit_Cost）與速覽成本"),
      ("gsf", "新鮮 prefill", "GPU-s/M", "#,##0.0", "=1E6/{X}{Pp}"),
      ("gsc", "快取命中 prefill（KV 載入）", "GPU-s/M", "#,##0.000", "=1E6*{X}{kv}/({X}{loadbw}*1E12)"),
      ("gsd", "decode（含思考 token；0＝SLO 不可達）", "GPU-s/M", "#,##0.0", "=IF({X}{D}>0,1E6/{X}{D},0)"),
      ("cfq", "速覽：新鮮 prefill $/M（經濟、基準成本、100%）", "$/M", "#,##0.000", "=INDEX(DC_Cost!$C$58:$Q$58,3*({X}$6-1)+2)/3600*{X}{gsf}"),
      ("cdq", "速覽：decode $/M（經濟、基準成本、100%）", "$/M", "#,##0.000", "=IF({X}{gsd}>0,INDEX(DC_Cost!$C$58:$Q$58,3*({X}$6-1)+2)/3600*{X}{gsd},0)"),
      ("§", "J. 能量下限與閉合（能量閉合：物理下限功率 ≤ 機架平均用電）"),
      ("eflop", "運算能量", "pJ/FLOP", "0.000", "={X}{gpuw}*Energy!$C$5/({X}{P}*1E15)*1E12"),
      ("elink", "EP 通訊能量", "pJ/B", "0", "=IF({X}$6=1,Energy!$C$7,Energy!$C$6)"),
      ("fpt", "decode FLOPs/接受 token（含草稿驗證）", "GFLOP", "#,##0.0", "=({X}{N}+1)*{X}{Fd}/{X}{a}"),
      ("bpt", "decode HBM 讀取/接受 token", "GB", "0.000", "=IF({X}{B}>0,({X}{W}+{X}{B}*{X}{kv}*{X}{ctxd}/1E9)/({X}{B}*{X}{a}),0)"),
      ("cpt", "decode EP 傳輸/接受 token", "GB", "0.0000", "=({X}{N}+1)*{X}{L}*{X}{k}*{X}{d}*{X}{act}/{X}{a}/1E9"),
      ("Edec", "decode 物理下限能量", "J/tok", "0.0000", "=({X}{fpt}*{X}{eflop}+{X}{bpt}*{X}{ehbm}+{X}{cpt}*{X}{elink})/1000"),
      ("Epre", "prefill 物理下限能量", "J/tok", "0.0000", "={X}{Fp}*{X}{eflop}/1000"),
      ("pphys", "物理下限功率（每架）", "kW", "#,##0.0", "=({X}{rpre}*{X}{Epre}+{X}{rdec}*{X}{Edec})/1000"),
      ("pavg", "機架平均用電（Block 1 假設）", "kW", "#,##0.0", "={X}{kw}*Inputs!$E$10"),
      ("close", "閉合比（下限 ÷ 平均用電；須 ≤ 100%）", "%", "0%", "=IF({X}{pavg}>0,{X}{pphys}/{X}{pavg},0)"),
      ("tpj", "tokens／焦耳（總 token，平均用電口徑）", "tok/J", "#,##0.00", "={X}{rtot}/({X}{pavg}*1000)"),
      ("jdec", "每 decode token 實際能量（平均用電口徑）", "J/tok", "0.000", "=IF({X}{rdec}>0,{X}{pavg}*1000*(1-{X}{psh})/{X}{rdec},0)"),
    ]

KEY_ROWS = {"D", "rtot", "gwtot", "cdq", "cfq", "bind", "close", "tpj", "B"}

def write_perf(ws, cols, SP, AR, CAL, TR, start=9, overrides=None, label_col_width=42, ov_link=False):
    """cols: list of column letters; header rows 4-7 already written. overrides: {col: {key: value}}.
    ov_link=True: overrides are standing links (green, no fill) rather than scenario changes (blue on yellow)."""
    overrides = overrides or {}
    R = {}; r = start
    spec = perf_rows(SP, AR, CAL, TR)
    for item in spec:
        if item[0] == "§":
            section(ws, r, item[1], 2 + len(cols)); r += 1; continue
        key, lab, unit, fmt, tpl = item
        R[key] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in cols:
            ov = overrides.get(X, {})
            if key in ov:
                v = ov[key].replace("{X}", X) if isinstance(ov[key], str) else ov[key]
                if ov_link and isinstance(v, str):
                    put(ws, f"{X}{r}", v, F_LINK, fmt=fmt)
                else:   # v5.11: a formula override (cross-sheet scenario link) is not an input -> link font, yellow scenario fill kept
                    put(ws, f"{X}{r}", v, F_LINK if isinstance(v, str) and v.startswith("=") else F_IN, fmt=fmt,
                        fill=PatternFill("solid", fgColor="FFFFFF00"))
                continue
            if isinstance(tpl, (int, float)):
                put(ws, f"{X}{r}", tpl, F_IN, fmt=fmt); continue
            m = dict(R); m["X"] = X
            f = tpl.format(**m)
            put(ws, f"{X}{r}", f, fmt=fmt, fill=FILL_KEY if key in KEY_ROWS else None)
        r += 1
    ws.column_dimensions["A"].width = label_col_width
    ws.column_dimensions["B"].width = 10
    return R, r

from common import *

PTS = [  # col, use, gen idx, engine/date, MTP, s, ISL, OSL, measured, source
 ("C", "擬合點 1", 3, "InferenceX 最佳前緣（約 2026-07）", 1, 72, 8192, 1024, 9384.4, "S22"),
 ("D", "擬合點 2", 3, "InferenceX 最佳前緣（約 2026-07）", 1, 130, 8192, 1024, 3473.9, "S22"),
 ("E", "驗證", 3, "SGLang＋MTP，2026-06", 1, 50, 8192, 1024, 11200, "S21"),
 ("F", "驗證（舊軟體）", 3, "vLLM 無 MTP，2026-05-22", 0, 27, 8192, 1024, 6182, "S20"),
 ("G", "驗證（舊軟體）", 2, "vLLM 無 MTP，2026-05-22", 0, 27, 8192, 1024, 2189, "S20"),
 ("H", "驗證（口徑待查）", 2, "InferenceX 比較頁（0813）", 1, 110, 8192, 1024, 3795.5, "S23"),
 ("I", "驗證（口徑待查）", 3, "InferenceX 比較頁（0813）", 1, 110, 8192, 1024, 6522.4, "S23"),
]

def calib(wb, SP, AR):
    ws = wb.create_sheet("Calib", 5)
    title(ws, "Calib — 以實測錨點校準效率係數（實測只校準係數，不取代推導）",
          "錨點：DeepSeek V4-Pro（＝Sol 代表架構）、FP4、8K/1K、分離式 P/D，tok/s/GPU 為總 token 口徑。GB300 同一前緣上兩點聯立解出 η_d 與每層延遲；其餘各點為樣本外驗證")
    for c, w in zip("ABCDEFGHIJ", [44, 12, 16, 16, 16, 16, 16, 16, 16, 60]): ws.column_dimensions[c].width = w
    C = {}
    section(ws, 4, "A. 輸入", 10)
    put(ws, "A5", "η_p：prefill 達成峰值比例"); put(ws, "B5", "%"); put(ws, "C5", 0.30, fmt="0%")
    put(ws, "J5", "Analogy：DeepSeek H800 線上 prefill 約 0.37（S30，待查）；區間 0.15–0.45。擬合結果對此不敏感（見 G 節）", F_NOTE)
    section(ws, 7, "B. 錨點（每欄一個實測點）", 10)
    hdr = [("A8", "項目"), ("B8", "單位")]
    for a, b in hdr: put(ws, a, b, F_BOLD)
    rows = [("use", "用途", ""), ("g", "世代索引", ""), ("gn", "世代", ""), ("eng", "軟體／日期", ""),
            ("mtp", "MTP（1＝有）", ""), ("s", "每用戶速度", "tok/s"), ("isl", "ISL", "tok"), ("osl", "OSL", "tok"),
            ("T", "實測 tok/s/GPU（總 token）", "tok/s"), ("src", "來源", ""), ("indep", "量測平台（獨立性）", ""), ("lab", "點位標籤（世代｜用途｜速度）", ""), ("basis", "口徑", "")]
    r = 9
    for key, lab, unit in rows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); r += 1
    for col, use, g, eng, mtp, s, isl, osl, T, src in PTS:
        put(ws, f"{col}{C['use']}", use, F_BOLD)
        put(ws, f"{col}{C['g']}", g, fmt="0")
        put(ws, f"{col}{C['gn']}", f"=INDEX(Spec_Rack!$C$4:$G$4,{col}{C['g']})")
        put(ws, f"{col}{C['eng']}", eng, F_NOTE, wrap=True)
        put(ws, f"{col}{C['mtp']}", mtp, fmt="0")
        put(ws, f"{col}{C['s']}", s, fmt="#,##0")
        put(ws, f"{col}{C['isl']}", isl, fmt="#,##0"); put(ws, f"{col}{C['osl']}", osl, fmt="#,##0")
        put(ws, f"{col}{C['T']}", T, fmt="#,##0", fill=FILL_KEY)
        put(ws, f"{col}{C['src']}", src, F_NOTE)
        put(ws, f"{col}{C['indep']}", "InferenceX（SemiAnalysis）", F_NOTE, wrap=True)
        put(ws, f"{col}{C['lab']}", f'={col}{C["gn"]}&"｜"&{col}{C["use"]}&"｜"&TEXT({col}{C["s"]},"0")&" tok/s"', wrap=True)
        put(ws, f"{col}{C['basis']}", "總 token（輸入＋輸出）", F_NOTE, wrap=True)
    put(ws, f"J{C['indep']}", "七個點全部來自同一平台（S21 為 SGLang 作者轉述 InferenceX 資料，不構成獨立來源）。第二來源見 H 節", F_NOTE, wrap=True)
    ws.row_dimensions[C["eng"]].height = 30; ws.row_dimensions[C["lab"]].height = 30
    section(ws, r, "C. 各點的模型量（Sol 架構；與 Perf 同一套公式）", 10); r += 1
    g = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}{C['g']})"
    a = lambda row: f"=Arch!$D${row}"
    mrows = [
      ("P", "計算用峰值", "PF/GPU", "#,##0.000", g(SP["pk"])),
      ("hbm", "HBM 容量", "GB", "#,##0", g(SP["hbm"])),
      ("bw", "HBM 頻寬", "TB/s", "#,##0.00", g(SP["bw"])),
      ("link", "EP 通訊頻寬", "TB/s", "#,##0.00", g(SP["link"])),
      ("epb", "EP 基準寬度", "", "#,##0", g(SP["ep"])),
      ("be", "專家 bytes/param", "B", "0.0000", g(SP["be"])),
      ("bn", "非專家 bytes/param", "B", "0.00", g(SP["bn"])),
      ("A", "啟用參數", "B", "#,##0", a(AR["A"])), ("L", "層數", "", "#,##0", a(AR["L"])),
      ("d", "d_model", "", "#,##0", a(AR["d"])), ("k", "啟用專家", "", "#,##0", a(AR["k"])),
      ("ne", "非專家參數", "B", "#,##0.0", a(AR["ne"])), ("ex", "專家參數", "B", "#,##0", a(AR["ex"])),
      ("kv", "KV bytes/token", "B", "#,##0", a(AR["kv"])), ("attc", "注意力 FLOPs／被注意 token", "", "#,##0", a(AR["attc"])),
      ("ff", "全注意力層比例", "%", "0%", a(AR["ff"])), ("cap", "跨度上限", "", "#,##0", a(AR["cap"])),
      ("comp", "壓縮比", "", "#,##0", a(AR["comp"])), ("win", "滑動窗", "", "#,##0", a(AR["win"])),
      ("ctxd", "decode 平均上下文", "tok", "#,##0", "={X}{isl}+{X}{osl}/2"),
      ("attd", "decode 被注意 token", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxd},MIN({X}{ctxd},{X}{cap}))+(1-{X}{ff})*({X}{ctxd}/{X}{comp}+{X}{win})"),
      ("Fd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attd})/1E9"),
      ("ctxp", "prefill 平均位置", "tok", "#,##0", "={X}{isl}/2"),
      ("attp", "prefill 被注意 token", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxp},MIN({X}{ctxp},{X}{cap}))+(1-{X}{ff})*({X}{ctxp}/{X}{comp}+{X}{win})"),
      ("Fp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attp})/1E9"),
      ("usable", "可用 HBM", "GB", "#,##0", "={X}{hbm}*(1-Serving!$C$9)"),
      ("tpa", "注意力 TP 度", "", "0", "=MAX(1,CEILING({X}{ne}*{X}{bn}/(Serving!$C$10*{X}{usable}),1))"),
      ("epw", "EP 寬度", "", "#,##0", "=MAX({X}{epb},CEILING({X}{ex}*{X}{be}/(Serving!$C$11*{X}{usable}),1))"),
      ("W", "每 GPU 權重", "GB", "#,##0.0", "={X}{ne}*{X}{bn}/{X}{tpa}+{X}{ex}*{X}{be}/{X}{epw}"),
      ("n", "草稿數（無 MTP＝0）", "", "0", "=Serving!$C$6*{X}{mtp}"),
      ("a", "每步接受 token", "", "0.00", "=IF({X}{mtp}=1,Serving!$C$8,1)"),
      ("Pp", "prefill tok/s/GPU（η_p 基準）", "tok/s", "#,##0", "=$C$5*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("c1", "每序列算力時間（η＝1）", "ms", "0.00000", "=({X}{n}+1)*{X}{Fd}/{X}{P}/1000"),
      ("Dm", "實測反推 decode tok/s（每 decode GPU）", "tok/s", "#,##0", "={X}{osl}/(({X}{isl}+{X}{osl})/{X}{T}-{X}{isl}/{X}{Pp})"),
      ("Bm", "實測反推批次", "序列/GPU", "#,##0.0", "={X}{Dm}/{X}{s}"),
    ]
    for key, lab, unit, fmt, tpl in mrows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for col, *_ in PTS:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt)
        r += 1
    put(ws, f"J{C['Dm']}", "只對擬合點有意義；假設 P:D GPU 依工作量配比", F_NOTE)
    r += 1
    section(ws, r, "D. 擬合（擬合點 1、2 聯立；假設兩點皆為算力項綁定，見下列檢查）", 10); r += 1
    C["etad_fit"] = r
    put(ws, f"A{r}", "η_d：decode 每序列算力效率"); put(ws, f"B{r}", "%")
    put(ws, f"C{r}", f"=(C{C['Bm']}-D{C['Bm']})*C{C['c1']}/(1000*(C{C['a']}/C{C['s']}-D{C['a']}/D{C['s']}))", fmt="0.00%", fill=FILL_KEY)
    put(ws, f"J{r}", "B×c/η＝1000×a/s − 固定延遲；兩點相減消去固定延遲", F_NOTE); r += 1
    C["tfix_fit"] = r
    put(ws, f"A{r}", "每步固定延遲（GB300、Sol、含 MTP）"); put(ws, f"B{r}", "ms")
    put(ws, f"C{r}", f"=1000*C{C['a']}/C{C['s']}-C{C['Bm']}*C{C['c1']}/C{C['etad_fit']}", fmt="#,##0.00"); r += 1
    C["tl_fit"] = r
    put(ws, f"A{r}", "每層每次前向固定延遲"); put(ws, f"B{r}", "µs")
    put(ws, f"C{r}", f"=(C{C['tfix_fit']}-C{C['W']}/C{C['bw']})*1000/(C{C['L']}+C{C['n']})", fmt="#,##0", fill=FILL_KEY)
    put(ws, f"J{r}", "（固定延遲 − 權重讀取時間）÷（層數＋草稿數）：涵蓋 all-to-all 延遲、kernel 啟動、同步", F_NOTE); r += 1
    C["chk"] = r
    put(ws, f"A{r}", "檢查：擬合點 1 算力項為綁定")
    put(ws, f"C{r}", f"=IF(C{C['c1']}/C{C['etad_fit']}>=MAX(C{C['kv']}*C{C['ctxd']}/(C{C['bw']}*Serving!$C$13)/1E9,(C{C['n']}+1)*C{C['L']}*C{C['k']}*C{C['d']}*Serving!$C$12/(C{C['link']}*Serving!$C$14)/1E9),\"成立\",\"不成立\")")
    r += 2
    section(ws, r, "E. 各世代採用參數（GB300＝擬合值；其他世代＝擬合值 × 倍數）", 10); r += 1
    for c, v in zip("CDEFG", range(1, 6)):
        put(ws, f"{c}{r}", f"=Spec_Rack!{c}4", F_HLINK)
    put(ws, f"A{r}", "世代", F_BOLD); r += 1
    mult = [("etadm", "η_d 倍數", [1.5, 1, 1, 1, 1], "Hopper：v5.4 取 3（DeepSeek H800 線上 decode 約達峰值 18%，S30；當時峰值誤用 989 TF）。v5.5 峰值更正為 FP8 1,979 TF，倍數同步減半為 1.5，使 Hopper 產出不變；S30 口徑查核後重推 [Analogy，區間 0.5–2.5]；GB200、VR200 沿用 GB300 [Analogy]；RU [Assumed]"),
            ("tlm", "每層延遲倍數", [1.5, 1, 1, 1, 1], "Hopper EP 跨節點走 IB [Assumed 1.5，區間 1–3]"),
            ("etapm", "η_p 倍數", [0.5, 1, 1, 1, 1], "Hopper 0.5：v5.5 峰值更正（989→1,979 TF）後維持 prefill 產出不變（誤差 0.05%）；S30 口徑查核後重推")]
    for key, lab, vals, note in mult:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", "x")
        for c, v in zip("CDEFG", vals): put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"J{r}", note, F_NOTE, wrap=True); r += 1
    for key, lab, unit, fmt, base, m in [("etad", "η_d（採用）", "%", "0.00%", f"$C${C['etad_fit']}", "etadm"),
                                        ("tl", "每層延遲（採用）", "µs", "#,##0", f"$C${C['tl_fit']}", "tlm"),
                                        ("etap", "η_p（採用）", "%", "0.0%", "$C$5", "etapm")]:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDEFG":
            put(ws, f"{c}{r}", f"={base}*{c}{C[m]}", fmt=fmt, fill=FILL_KEY)
        r += 1
    r += 1
    section(ws, r, "F. 樣本外驗證（以採用參數重算各點）", 10); r += 1
    vrows = [
      ("ved", "η_d（該世代）", "%", "0.00%", f"=INDEX($C${C['etad']}:$G${C['etad']},{{X}}{C['g']})"),
      ("vtl", "每層延遲（該世代）", "µs", "#,##0", f"=INDEX($C${C['tl']}:$G${C['tl']},{{X}}{C['g']})"),
      ("vep", "η_p（該世代）", "%", "0.0%", f"=INDEX($C${C['etap']}:$G${C['etap']},{{X}}{C['g']})"),
      ("vPp", "prefill tok/s/GPU", "tok/s", "#,##0", "={X}{vep}*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("vtf", "每步固定延遲", "ms", "#,##0.00", "={X}{W}/{X}{bw}+({X}{L}+{X}{n})*{X}{vtl}/1000"),
      ("vce", "每序列每步時間", "ms", "0.0000", "=MAX({X}{c1}/{X}{ved},{X}{kv}*{X}{ctxd}/({X}{bw}*Serving!$C$13)/1E9,({X}{n}+1)*{X}{L}*{X}{k}*{X}{d}*Serving!$C$12*({X}{epw}-1)/{X}{epw}/({X}{link}*Serving!$C$14)/1E9)"),
      ("vbs", "SLO 批次上限", "序列", "#,##0.0", "=(1000*{X}{a}/{X}{s}-{X}{vtf})/{X}{vce}"),
      ("vbc", "容量批次上限", "序列", "#,##0", "=({X}{usable}-{X}{W})*1E9/({X}{kv}*{X}{ctxd})"),
      ("vB", "B*", "序列", "#,##0.0", "=MAX(0,MIN({X}{vbs},{X}{vbc}))"),
      ("vD", "decode tok/s/GPU", "tok/s", "#,##0", "=IF({X}{vB}>0,{X}{vB}*{X}{a}/(({X}{vtf}+{X}{vB}*{X}{vce})/1000),0)"),
      ("vT", "模型 tok/s/GPU（總 token）", "tok/s", "#,##0", "=IF({X}{vD}>0,({X}{isl}+{X}{osl})/({X}{isl}/{X}{vPp}+{X}{osl}/{X}{vD}),0)"),
      ("ratio", "模型 ÷ 實測", "x", "0.00", "={X}{vT}/{X}{T}"),
    ]
    for key, lab, unit, fmt, tpl in vrows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for col, *_ in PTS:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt, fill=FILL_KEY if key == "ratio" else None)
        r += 1
    notes = {"C": "擬合點：應為 1.00", "D": "擬合點：應為 1.00", "E": "同世代、不同日期與引擎：檢驗前緣形狀",
             "F": "舊軟體：模型應高於實測（軟體差距）", "G": "舊軟體＋GB200 記憶體限制配方（S20 說明）",
             "H": "工作負載標示不明（頁面預設為 agentic）", "I": "同上"}
    C["vnote"] = r; put(ws, f"A{r}", "判讀")
    for col, t in notes.items(): put(ws, f"{col}{r}", t, F_NOTE, wrap=True)
    ws.row_dimensions[r].height = 42
    r += 2
    section(ws, r, "G. η_p 敏感度：擬合結果隨 η_p 的變化（η_p 僅影響 prefill／decode GPU 分攤）", 10); r += 1
    put(ws, f"A{r}", "η_p", F_BOLD)
    for c, v in zip("CDE", [0.15, 0.30, 0.45]): put(ws, f"{c}{r}", v, fmt="0%")
    ep_r = r; r += 1
    srows = [
      ("Pp1", "擬合點 1 prefill tok/s", "=${c}$" if False else "={c}{ep}*$C${P}*1E15/($C${Fp}*1E9)", "#,##0"),
      ("Pp2", "擬合點 2 prefill tok/s", "={c}{ep}*$D${P}*1E15/($D${Fp}*1E9)", "#,##0"),
      ("B1", "擬合點 1 反推批次", "=$C${osl}/(($C${isl}+$C${osl})/$C${T}-$C${isl}/{c}{Pp1})/$C${s}", "#,##0.0"),
      ("B2", "擬合點 2 反推批次", "=$D${osl}/(($D${isl}+$D${osl})/$D${T}-$D${isl}/{c}{Pp2})/$D${s}", "#,##0.0"),
      ("ed", "η_d", "=({c}{B1}-{c}{B2})*$C${c1}/(1000*($C${a}/$C${s}-$D${a}/$D${s}))", "0.00%"),
      ("tl", "每層延遲 µs", "=((1000*$C${a}/$C${s}-{c}{B1}*$C${c1}/{c}{ed})-$C${W}/$C${bw})*1000/($C${L}+$C${n})", "#,##0"),
    ]
    SR = {}
    for key, lab, tpl, fmt in srows:
        SR[key] = r; put(ws, f"A{r}", lab)
        for c in "CDE":
            m = dict(C); m.update(SR); m["c"] = c; m["ep"] = ep_r
            put(ws, f"{c}{r}", tpl.format(**m), fmt=fmt)
        r += 1

    r += 1
    section(ws, r, "H. 第二來源驗證：MLPerf Inference DeepSeek-R1（MLCommons 稽核；提交者 NVIDIA 為利害關係方）", 10); r += 1
    put(ws, f"A{r}", "R1 架構與工作負載（驗證專用輸入）", F_BOLD); r += 1
    rin = [("rT", "總參數", "B", 671, "#,##0"), ("rA", "啟用參數", "B", 37, "#,##0"), ("rL", "層數", "", 61, "#,##0"),
           ("rd", "d_model", "", 7168, "#,##0"), ("rE", "routed experts", "", 256, "#,##0"), ("rk", "啟用 experts", "", 8, "#,##0"),
           ("rs", "shared experts", "", 1, "#,##0"), ("rV", "vocab", "", 129280, "#,##0"),
           ("rkv", "KV bytes/token（MLA 576 × 61 層，FP8）", "B", 35136, "#,##0"),
           ("rac", "注意力 FLOPs／被注意 token（MLA：2×128×192＋2×128×128，× 61）", "FLOP", 4997120, "#,##0"),
           ("risl", "平均 ISL（MLCommons 資料集）", "tok", 800, "#,##0"), ("rosl", "平均 OSL", "tok", 3880, "#,##0")]
    for key, lab, unit, v, fmt in rin:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt); r += 1
    put(ws, f"J{C['rT']}", "Verified：DeepSeek-V3/R1 模型卡；ISL／OSL 800／3,880（MLCommons 2025-09，S33）", F_NOTE, wrap=True)
    for key, lab, f, fmt in [("rpe", "每 routed expert 參數", "=(C{rT}-C{rA})/(C{rL}*(C{rE}-C{rk}))", "0.0000"),
                             ("rne", "非專家參數", "=C{rA}-C{rL}*(C{rk}+C{rs})*C{rpe}", "#,##0.0"),
                             ("rex", "專家參數", "=C{rT}-C{rne}", "#,##0")]:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", "B"); put(ws, f"C{r}", f.format(**C), fmt=fmt); r += 1
    r += 1
    MP = [("C", "GB300 interactive（v6.1）", 3, 1, "=1000/15", "=253506/72"),
          ("D", "GB200 interactive（v6.0）", 2, 1, "=1000/15", "=240318/72"),
          ("E", "VR200 interactive（v6.1 預覽）", 4, 1, "=1000/15", "=652750/72"),
          ("F", "GB300 server（v6.0）", 3, 0, "=1000/80", 8064)]
    hdr = r; C["mhdr"] = r; put(ws, f"A{r}", "驗證點", F_BOLD)
    for col, lab, *_ in MP: put(ws, f"{col}{r}", lab, F_BOLD, wrap=True)
    ws.row_dimensions[r].height = 30; r += 1
    base = [("mg", "世代索引", "0"), ("ms", "每用戶速度下限（1000 ÷ TPOT）", "#,##0.0"), ("mm", "推測解碼（1＝有）", "0"),
            ("mT", "MLPerf 實測輸出 tok/s/GPU（總量 ÷ 72）", "#,##0")]
    UNITS = {"ms": "tok/s", "mT": "tok/s/GPU"}
    for key, lab, fmt in base:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", UNITS.get(key, ""))
        for (col, _, g, mtp, s, T) in MP:
            v = {"mg": g, "ms": s, "mm": mtp, "mT": T}[key]
            put(ws, f"{col}{r}", v, F_IN if not isinstance(v, str) else None, fmt=fmt,   # v5.11: formulas are not inputs (SRC links via gov.FORMULA_MAP)
                fill=FILL_KEY if key == "mT" else None)
        r += 1
    C["mplat"] = r; put(ws, f"A{r}", "量測平台（獨立性）")
    for col, lab, *_ in MP:
        put(ws, f"{col}{r}", "MLPerf（MLCommons 稽核）／NVIDIA 提交" + ("（預覽類）" if "預覽" in lab else ""), F_NOTE, wrap=True)
    ws.row_dimensions[r].height = 30; r += 1
    C["mgn"] = r; put(ws, f"A{r}", "世代")
    for col, *_ in MP: put(ws, f"{col}{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,{col}{C['mg']})")
    r += 1
    C["mbasis"] = r; put(ws, f"A{r}", "口徑")
    for col, *_ in MP: put(ws, f"{col}{r}", "輸出 token", F_NOTE)
    r += 1
    put(ws, f"J{C['mm']}", "MLCommons 規則表只在 interactive 列出 MTP 推測解碼（3 步），server 設為無", F_NOTE, wrap=True)
    put(ws, f"J{C['mT']}", "MLPerf 指標為輸出 token；interactive 的 TPOT 15 ms 為 p99，平均速度更高，本模型以下限計算，偏保守", F_NOTE, wrap=True)
    gl = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}{C['mg']})"
    cl = lambda row: f"=INDEX($C${row}:$G${row},{{X}}{C['mg']})"
    mrows2 = [
      ("mP", "計算用峰值", "PF", "#,##0.000", gl(SP["pk"])), ("mH", "HBM", "GB", "#,##0", gl(SP["hbm"])),
      ("mB", "HBM 頻寬", "TB/s", "#,##0.00", gl(SP["bw"])), ("mLk", "EP 頻寬", "TB/s", "#,##0.00", gl(SP["link"])),
      ("mEb", "EP 基準", "", "#,##0", gl(SP["ep"])), ("mbe", "專家 B/param", "", "0.0000", gl(SP["be"])), ("mbn", "非專家 B/param", "", "0.00", gl(SP["bn"])),
      ("mU", "可用 HBM", "GB", "#,##0", "={X}{mH}*(1-Serving!$C$9)"),
      ("mTP", "注意力 TP", "", "0", "=MAX(1,CEILING($C${rne}*{X}{mbn}/(Serving!$C$10*{X}{mU}),1))"),
      ("mEP", "EP 寬度", "", "#,##0", "=MAX({X}{mEb},CEILING($C${rex}*{X}{mbe}/(Serving!$C$11*{X}{mU}),1))"),
      ("mW", "每 GPU 權重", "GB", "#,##0.0", "=$C${rne}*{X}{mbn}/{X}{mTP}+$C${rex}*{X}{mbe}/{X}{mEP}"),
      ("mcd", "decode 平均上下文", "tok", "#,##0", "=$C${risl}+$C${rosl}/2"),
      ("mFd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*$C${rA}*1E9+$C${rac}*{X}{mcd})/1E9"),
      ("mFp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*$C${rA}*1E9+$C${rac}*$C${risl}/2)/1E9"),
      ("mn", "草稿數", "", "0", "=Serving!$C$6*{X}{mm}"), ("ma", "每步接受", "", "0.00", "=IF({X}{mm}=1,Serving!$C$8,1)"),
      ("med", "η_d（該世代）", "%", "0.00%", cl(C["etad"])), ("mtl", "每層延遲（該世代）", "µs", "#,##0", cl(C["tl"])), ("mep", "η_p（該世代）", "%", "0.0%", cl(C["etap"])),
      ("mPp", "prefill tok/s/GPU", "tok/s", "#,##0", "={X}{mep}*{X}{mP}*1E15/({X}{mFp}*1E9)"),
      ("mtf", "每步固定延遲", "ms", "#,##0.00", "={X}{mW}/{X}{mB}+($C${rL}+{X}{mn})*{X}{mtl}/1000"),
      ("mce", "每序列每步時間", "ms", "0.0000", "=MAX(({X}{mn}+1)*{X}{mFd}/({X}{mP}*{X}{med})/1000,$C${rkv}*{X}{mcd}/({X}{mB}*Serving!$C$13)/1E9,({X}{mn}+1)*$C${rL}*$C${rk}*$C${rd}*Serving!$C$12*({X}{mEP}-1)/{X}{mEP}/({X}{mLk}*Serving!$C$14)/1E9)"),
      ("mBs", "B*", "序列", "#,##0.0", "=MAX(0,MIN((1000*{X}{ma}/{X}{ms}-{X}{mtf})/{X}{mce},({X}{mU}-{X}{mW})*1E9/($C${rkv}*{X}{mcd})))"),
      ("mD", "decode tok/s/GPU", "tok/s", "#,##0", "=IF({X}{mBs}>0,{X}{mBs}*{X}{ma}/(({X}{mtf}+{X}{mBs}*{X}{mce})/1000),0)"),
      ("mO", "模型輸出 tok/s/GPU（含 prefill 分攤）", "tok/s", "#,##0", "=IF({X}{mD}>0,$C${rosl}/($C${risl}/{X}{mPp}+$C${rosl}/{X}{mD}),0)"),
      ("mR", "模型 ÷ MLPerf", "x", "0.00", "={X}{mO}/{X}{mT}"),
    ]
    for key, lab, unit, fmt, tpl in mrows2:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for (col, *_ ) in MP:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt, fill=FILL_KEY if key == "mR" else None)
        r += 1
    C["mVR"] = r
    put(ws, f"A{r}", "VR200 ÷ GB300（interactive）：模型"); put(ws, f"C{r}", f"=E{C['mO']}/C{C['mO']}", fmt="0.00", fill=FILL_KEY); r += 1
    C["mVRm"] = r
    put(ws, f"A{r}", "VR200 ÷ GB300（interactive）：MLPerf v6.1"); put(ws, f"C{r}", f"=E{C['mT']}/C{C['mT']}", fmt="0.00", fill=FILL_KEY); r += 1
    C["mGB"] = r
    put(ws, f"A{r}", "GB300 ÷ GB200（interactive）：模型 ／ MLPerf"); put(ws, f"C{r}", f"=C{C['mO']}/D{C['mO']}", fmt="0.00"); put(ws, f"D{r}", f"=C{C['mT']}/D{C['mT']}", fmt="0.00"); r += 1
    put(ws, f"J{C['mVR']}", "VR200 沿用 GB300 效率係數的檢驗：兩者接近即支持此 Analogy（MLPerf VR 為 NVIDIA 預覽類提交）", F_NOTE, wrap=True)
    put(ws, f"J{C['mGB']}", "來源衝突：InferenceX 顯示 GB300 對 GB200 約 1.7–2.8 倍，MLPerf 約 1.05 倍；GB200 的 VR-eq 應視為區間", F_NOTE, wrap=True)
    ws.freeze_panes = "C9"
    return C

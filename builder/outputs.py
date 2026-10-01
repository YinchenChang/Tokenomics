from common import *
from perf import write_perf

GEN_NAMES_IDX = [1, 2, 3, 4, 5]
COLS15 = [L(i) for i in range(3, 18)]  # C..Q

def perf_sheet(wb, SP, AR, CAL, TR):
    ws = wb.create_sheet("Perf", 6)
    title(ws, "Perf — 每架產出引擎（世代 × 層級；各層級 SLO 與參考任務；100% 利用率）",
          "decode：每步時間＝固定延遲＋B × 每序列時間；在 SLO 下解出批次 B*，再受 HBM 容量限制。prefill 為算力受限。黃底為關鍵輸出")
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD); put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    for i, X in enumerate(COLS15):
        g, t = i // 3 + 1, i % 3 + 1
        put(ws, f"{X}6", g, fmt="0"); put(ws, f"{X}7", t, fmt="0")
        put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
        put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
        ws.column_dimensions[X].width = 13
    R, r = write_perf(ws, COLS15, SP, AR, CAL, TR)
    # VR-eq row (15-col layout only)
    section(ws, r, "K. VR-eq（每 GW 產出 ÷ VR200 同層級）", 17); r += 1
    R["vreq"] = r
    put(ws, f"A{r}", "VR-eq 係數"); put(ws, f"B{r}", "x")
    for X in COLS15:
        put(ws, f"{X}{r}", f"=IF(INDEX($C${R['gwtot']}:$Q${R['gwtot']},9+{X}$7)>0,{X}{R['gwtot']}/INDEX($C${R['gwtot']}:$Q${R['gwtot']},9+{X}$7),0)", fmt="0.00", fill=FILL_KEY)
    ws.freeze_panes = "C8"
    return R

SCEN = [  # label, vr overrides, gb overrides, tier
 ("基準", {}, {}, 2),
 ("VR η_d × 0.5（新世代軟體未成熟）", {"etadm": 0.5}, {}, 2),
 ("VR η_d × 1.5", {"etadm": 1.5}, {}, 2),
 ("VR 每層延遲 × 0.7", {"tlm": 0.7}, {}, 2),
 ("VR 每層延遲 × 1.5", {"tlm": 1.5}, {}, 2),
 ("VR 峰值 50 PF（J2 高情境）", {"P": 50}, {}, 2),
 ("SLO 40 tok/s", {"s": 40}, {"s": 40}, 2),
 ("SLO 100 tok/s", {"s": 100}, {"s": 100}, 2),
 ("MTP 接受率 0.60", {"alpha": 0.6}, {"alpha": 0.6}, 2),
 ("MTP 接受率 0.80", {"alpha": 0.8}, {"alpha": 0.8}, 2),
 ("ISL 4K", {"isl": 4096}, {"isl": 4096}, 2),
 ("ISL 64K", {"isl": 65536}, {"isl": 65536}, 2),
 ("生產折減 0.7（兩世代）", {"prod": 0.7}, {"prod": 0.7}, 2),
 ("Astra KV 情境 1（混合）", {"kv": "=Arch!$E$21"}, {"kv": "=Arch!$E$21"}, 3),
 ("Astra KV 情境 2（全層 MLA，基準）", {"kv": "=Arch!$E$22"}, {"kv": "=Arch!$E$22"}, 3),
 ("Astra KV 情境 3（GQA-8）", {"kv": "=Arch!$E$23"}, {"kv": "=Arch!$E$23"}, 3),
]

def sens_sheet(wb, SP, AR, CAL, TR):
    ws = wb.create_sheet("Sens_Perf", 7)
    title(ws, "Sens_Perf — VR200 對 GB300 的單變數敏感度（先看敏感度，再看基準）",
          "每組兩欄：左 VR200、右 GB300。黃底藍字＝該情境改動的輸入。GB300 為校準世代，VR200 的 η_d 與每層延遲為沿用值 [Analogy]，故 VR 專屬情境只動 VR 欄")
    cols, ov = [], {}
    for i, (lab, vo, go, t) in enumerate(SCEN):
        xv, xg = L(3 + 2 * i), L(4 + 2 * i)
        cols += [xv, xg]; ov[xv] = vo; ov[xg] = go
        put(ws, f"{xv}3", lab, F_BOLD, wrap=True)
        ws.merge_cells(f"{xv}3:{xg}3")
        for X, g in ((xv, 4), (xg, 3)):
            put(ws, f"{X}6", g, fmt="0"); put(ws, f"{X}7", t, fmt="0")
            put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
            put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
            ws.column_dimensions[X].width = 12.5
    ws.row_dimensions[3].height = 44
    put(ws, "A3", "情境", F_BOLD); put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD)
    put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    R, r = write_perf(ws, cols, SP, AR, CAL, TR, overrides=ov)
    section(ws, r, "L. VR200 ÷ GB300（同一情境；每 GW 口徑）", 2 + len(cols)); r += 1
    R["rgw"], R["rcost"] = r, r + 1
    put(ws, f"A{r}", "VR200 ÷ GB300：每 GW 總產出"); put(ws, f"B{r}", "x")
    put(ws, f"A{r+1}", "VR200 ÷ GB300：decode $/M（經濟、基準）"); put(ws, f"B{r+1}", "x")
    for i in range(len(SCEN)):
        xv, xg = L(3 + 2 * i), L(4 + 2 * i)
        put(ws, f"{xv}{r}", f"=IF({xg}{R['gwtot']}>0,{xv}{R['gwtot']}/{xg}{R['gwtot']},0)", fmt="0.00", fill=FILL_KEY)
        put(ws, f"{xv}{r+1}", f"=IF(AND({xg}{R['cdq']}>0,{xv}{R['cdq']}>0),{xv}{R['cdq']}/{xg}{R['cdq']},0)", fmt="0.00", fill=FILL_KEY)
    ws.freeze_panes = "C8"
    return R

def unit_cost(wb, PR):
    ws = wb.create_sheet("Unit_Cost", 8)
    title(ws, "Unit_Cost — 每 M token 成本（世代 × 成本情境；依層級分區；新鮮 prefill／快取 prefill／decode）",
          "成本＝每 GPU 小時持有成本（DC_Cost）× 每 M token GPU 秒（Perf）。思考 token 在物理上與可見輸出同為 decode，成本相同，差異只在計費（Block 4）。100% 為理想上限；基準利用率版＝100% 版 ÷ 利用率。快取命中只計 KV 載入 GPU 時間，未計儲存成本")
    ws.column_dimensions["A"].width = 46; ws.column_dimensions["B"].width = 10
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "成本情境", F_BOLD); put(ws, "A6", "世代索引", F_BOLD)
    for i, X in enumerate(COLS15):
        put(ws, f"{X}4", f"=DC_Cost!{X}4", F_HLINK); put(ws, f"{X}5", f"=DC_Cost!{X}5", F_HLINK)
        put(ws, f"{X}6", i // 3 + 1, fmt="0"); ws.column_dimensions[X].width = 12.5
    U = {}
    section(ws, 7, "共用", 17)
    for r, lab, unit, f, fmt in [(8, "每 GPU 小時持有成本 — 經濟", "$/GPU-hr", "=DC_Cost!{X}58", "#,##0.00"),
                                 (9, "每 GPU 小時持有成本 — 會計", "$/GPU-hr", "=DC_Cost!{X}57", "#,##0.00"),
                                 (10, "基準利用率", "%", "=Serving!$C$17", "0%")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in COLS15: put(ws, f"{X}{r}", f.format(X=X), fmt=fmt)
    r = 12
    tiers = ["Luna（低層）", "Sol（中層）", "Astra（頂層）"]
    for t in (1, 2, 3):
        section(ws, r, f"{tiers[t-1]}", 17); r += 1
        pl = lambda key: f"=INDEX(Perf!$C${PR[key]}:$Q${PR[key]},3*({{X}}$6-1)+{t})"
        rows = [
          ("gsf", "GPU 秒／M 新鮮 prefill", "GPU-s", "#,##0.0", pl("gsf")),
          ("gsc", "GPU 秒／M 快取命中 prefill", "GPU-s", "#,##0.000", pl("gsc")),
          ("gsd", "GPU 秒／M decode（含思考 token；0＝SLO 不可達）", "GPU-s", "#,##0.0", pl("gsd")),
          ("cf", "新鮮 prefill $/M — 經濟、100%", "$/M", "#,##0.000", "={X}$8/3600*{X}{gsf}"),
          ("cc", "快取命中 prefill $/M — 經濟、100%", "$/M", "#,##0.0000", "={X}$8/3600*{X}{gsc}"),
          ("cd", "decode（含思考 token）$/M — 經濟、100%", "$/M", "#,##0.000", "=IF({X}{gsd}>0,{X}$8/3600*{X}{gsd},\"SLO 不可達\")"),
          ("cfu", "新鮮 prefill $/M — 經濟、基準利用率", "$/M", "#,##0.000", "={X}{cf}/{X}$10"),
          ("ccu", "快取命中 prefill $/M — 經濟、基準利用率", "$/M", "#,##0.0000", "={X}{cc}/{X}$10"),
          ("cdu", "decode（含思考 token）$/M — 經濟、基準利用率", "$/M", "#,##0.000", "=IF(ISNUMBER({X}{cd}),{X}{cd}/{X}$10,{X}{cd})"),
          ("cda", "decode（含思考 token）$/M — 會計、100%", "$/M", "#,##0.000", "=IF({X}{gsd}>0,{X}$9/3600*{X}{gsd},\"SLO 不可達\")"),
          ("cref", "參考請求混合 $/M 總 token — 經濟、100%", "$/M", "#,##0.000",
           f"=IF(ISNUMBER({{X}}{{cd}}),(Serving!${'CDE'[t-1]}$23*{{X}}{{cf}}+Serving!${'CDE'[t-1]}$24*{{X}}{{cd}})/(Serving!${'CDE'[t-1]}$23+Serving!${'CDE'[t-1]}$24),{{X}}{{cd}})"),
        ]
        for key, lab, unit, fmt, tpl in rows:
            U[(t, key)] = r
            put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
            m = {k2: U[(t, k2)] for (tt, k2) in U if tt == t}
            for X in COLS15:
                mm = dict(m); mm["X"] = X
                put(ws, f"{X}{r}", tpl.format(**mm), fmt=fmt, fill=FILL_KEY if key in ("cd", "cf", "cdu") else None)
            r += 1
        r += 1
    ws.freeze_panes = "C7"
    return U

def workload(wb, U):
    ws = wb.create_sheet("Workload", 5)
    title(ws, "Workload — 任務制工作負載（每任務的 token 結構；思考 token 在物理上屬 decode）",
          "任務組合權重不在第 0 層（J5）；本頁只定義標準任務。harness token 倍數預設 1.0，Block 5 接手")
    for c, w in zip("ABCDEFGH", [40, 10, 14, 14, 16, 16, 18, 70]): ws.column_dimensions[c].width = w
    tasks = ["一般聊天", "推理聊天", "單代理（工具迴圈）", "多代理研究", "Coding agent（長程）"]
    put(ws, "A4", "參數", F_BOLD); put(ws, "B4", "單位", F_BOLD)
    for c, t in zip("CDEFG", tasks): put(ws, f"{c}4", t, F_BOLD, wrap=True)
    put(ws, "H4", "說明", F_BOLD); ws.row_dimensions[4].height = 30
    ins = [
      (5, "輪數 T", "輪", [1, 1, 4, 4, 30], "#,##0", "Assumed"),
      (6, "初始上下文 S（系統提示、歷史、工具定義）", "tok", [2000, 2000, 3000, 3000, 12000], "#,##0", "Assumed"),
      (7, "每輪新輸入 u（使用者或工具結果）", "tok", [500, 500, 1200, 1200, 2000], "#,##0", "Assumed"),
      (8, "每輪思考 token h", "tok", [0, 3000, 400, 400, 600], "#,##0", "Assumed；服務端思考占比待查"),
      (9, "每輪可見輸出 o", "tok", [500, 700, 200, 200, 400], "#,##0", "Assumed"),
      (10, "思考保留於上下文比例 ρ", "%", [0, 0, 0, 0, 0], "0%", "Assumed：多數 API 不保留前輪思考"),
      (11, "歷史快取命中率 χ", "%", [0.5, 0.5, 0.9, 0.9, 0.9], "0%", "Assumed；代理迴圈前綴重用高"),
      (12, "並行子代理數 m", "個", [0, 0, 0, 3, 0], "0", "Assumed：子代理沿用單代理參數"),
      (13, "harness token 倍數", "x", [1, 1, 1, 1, 1], "0.00", "預設 1.0（Block 5）"),
    ]
    for r, lab, unit, vals, fmt, note in ins:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDEFG", vals): put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE)
    section(ws, 15, "導出（每任務）", 8)
    der = [
      (16, "每輪上下文增量 u＋o＋ρh", "tok", "={c}7+{c}9+{c}10*{c}8", "#,##0"),
      (17, "單代理輸入總量", "tok", "={c}5*({c}6+{c}7)+{c}16*{c}5*({c}5-1)/2", "#,##0"),
      (18, "其中可快取（前綴）", "tok", "={c}11*({c}5*{c}6+{c}16*{c}5*({c}5-1)/2)", "#,##0"),
      (19, "其中新鮮", "tok", "={c}17-{c}18", "#,##0"),
      (20, "單代理 decode（思考＋可見）", "tok", "={c}5*({c}8+{c}9)", "#,##0"),
      (21, "系統倍數（1＋m）× harness", "x", "=(1+{c}12)*{c}13", "0.00"),
      (22, "任務新鮮 prefill", "tok", "={c}19*{c}21", "#,##0"),
      (23, "任務快取 prefill", "tok", "={c}18*{c}21", "#,##0"),
      (24, "任務 decode", "tok", "={c}20*{c}21", "#,##0"),
      (25, "任務總 token", "tok", "={c}22+{c}23+{c}24", "#,##0"),
      (26, "decode 平均上下文", "tok", "={c}6+{c}7+({c}5-1)/2*{c}16+({c}8+{c}9)/2", "#,##0"),
      (27, "思考占 decode", "%", "=IF({c}8+{c}9>0,{c}8/({c}8+{c}9),0)", "0%"),
      (28, "總 token ÷ 一般聊天", "x", "={c}25/$C$25", "0.0"),
      (29, "總 token ÷ 推理聊天", "x", "={c}25/$D$25", "0.0"),
    ]
    for r, lab, unit, f, fmt in der:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDEFG": put(ws, f"{c}{r}", f.format(c=c), fmt=fmt, fill=FILL_KEY if r in (25, 28) else None)
    put(ws, "A30", "參照：Anthropic 揭露倍數（相對聊天）"); put(ws, "B30", "x")
    put(ws, "C30", 1, fmt="0"); put(ws, "E30", 4, fmt="0"); put(ws, "F30", 15, fmt="0")
    put(ws, "H30", "Interested-party：Anthropic 2025-06 多代理研究系統文章，agent 約 4 倍、多代理約 15 倍聊天 token（S25）。其『聊天』口徑未說明是否含思考，故兩個倍數並列", F_NOTE, wrap=True)
    put(ws, "H26", "Unit_Cost 的 decode 成本取各層級參考上下文；本列顯示任務實際上下文，差距大時看 Sens_Perf 的 ISL 情境", F_NOTE, wrap=True)
    section(ws, 32, "每任務成本（$／任務；經濟口徑、基準成本情境、基準利用率）", 8)
    r = 33
    for gname, col in (("VR200", "M"), ("GB300", "J")):
        for t, tn in zip((1, 2, 3), ("Luna", "Sol", "Astra")):
            put(ws, f"A{r}", f"{gname} × {tn}"); put(ws, f"B{r}", "$")
            cf, cc, cd = U[(t, "cfu")], U[(t, "ccu")], U[(t, "cdu")]
            for c in "CDEFG":
                put(ws, f"{c}{r}", f"=IF(ISNUMBER(Unit_Cost!{col}{cd}),({c}22*Unit_Cost!{col}{cf}+{c}23*Unit_Cost!{col}{cc}+{c}24*Unit_Cost!{col}{cd})/1E6,\"SLO 不可達\")",
                    fmt="$#,##0.0000", fill=FILL_KEY if tn == "Sol" else None)
            r += 1
    ws.freeze_panes = "C5"
    return ws

def nonnv(wb):
    ws = wb.create_sheet("NonNV")
    title(ws, "NonNV — 非 NVIDIA 世代比例列（D2；全部 [Assumed]，以區間表示）",
          "每 GW 產出比與每 GW 持有成本比皆相對 VR200（同層級、同 SLO）。持有成本比預設接近 1，依 Block 1 結論：每 GW 持有成本幾乎不隨世代改變")
    hdr = ["候選", "產出比 低", "產出比 基準", "產出比 高", "持有比 低", "持有比 基準", "持有比 高",
           "每 token 成本比 基準", "最佳角落", "最差角落", "標記", "說明"]
    for i, h in enumerate(hdr): put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True)
    ws.row_dimensions[4].height = 30
    data = [
      ("AMD MI455X（Helios）", 0.5, 0.7, 1.0, 0.8, 0.9, 1.0, "MI355X 在 V4-Pro 上 26 天內吞吐提升 110 倍（S20 所屬部落格），軟體成熟度為主要不確定"),
      ("Google TPU v7 Ironwood", 0.6, 0.8, 1.1, 0.7, 0.8, 1.0, "自用為主，無公開同口徑實測"),
      ("AWS Trainium3", 0.3, 0.5, 0.8, 0.6, 0.7, 0.9, "OpenAI v0.5 以 2GW Trainium 合約為輸入"),
      ("Cerebras WSE-3", 0.2, 0.4, 0.8, 0.8, 1.0, 1.2, "高互動性利基；每 GW 吞吐低、單用戶速度高"),
      ("OpenAI／Broadcom 客製", 0.4, 0.6, 0.9, 0.7, 0.8, 1.0, "無公開規格；沿用 v0.5「自研／其他 0.6（0.4–1.0）」"),
    ]
    for i, (n, ol, ob, oh, hl, hb, hh, note) in enumerate(data):
        r = 5 + i
        put(ws, f"A{r}", n)
        for c, v in zip("BCDEFG", [ol, ob, oh, hl, hb, hh]): put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"H{r}", f"=F{r}/C{r}", fmt="0.00", fill=FILL_KEY)
        put(ws, f"I{r}", f"=E{r}/D{r}", fmt="0.00"); put(ws, f"J{r}", f"=G{r}/B{r}", fmt="0.00")
        put(ws, f"K{r}", "Assumed", F_NOTE); put(ws, f"L{r}", note, F_NOTE)
    for c, w in zip("ABCDEFGHIJKL", [26, 9, 9, 9, 9, 9, 9, 11, 9, 9, 10, 70]): ws.column_dimensions[c].width = w
    return ws

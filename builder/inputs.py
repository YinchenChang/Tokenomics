# Input sheets: Spec_Rack (Block 2 rows), Arch, Serving, Energy inputs
from common import *

GENS = ["C", "D", "E", "F", "G"]          # Hopper, GB200, GB300, VR200, RU in Spec_Rack

def spec_rack(wb):
    ws = wb["Spec_Rack"]
    R = {}
    section(ws, 21, "B2. 效能規格（Block 2；藍字＝輸入；每 GPU 封裝）", 8)
    put(ws, "H4", "標記／來源", F_BOLD)
    rows = [
      ("prec",  "服務精度", None, ["FP8", "NVFP4", "NVFP4", "NVFP4", "NVFP4"], None,
       "Hopper 不支援 FP4，以 FP8 服務"),
      ("pk_b",  "峰值 dense（基準）PF/GPU", "#,##0.000", [1.979, 10, 15, 35, 73], None,
       "Interested-party（NVIDIA 規格）：H100 FP8 dense 1,979 TF（v5.5 更正；v5.4 誤填 BF16 的 989）；GB200 FP4 10 PF（HGX B200 為 9）；B300 15；Rubin NVFP4 訓練 35；RU＝104×35/50 推估 [Derived]。S28"),
      ("pk_h",  "峰值（高情境：NVFP4 推論口徑）PF/GPU", "#,##0.000", [1.979, 10, 15, 50, 104], None,
       "Rubin 50 PF 含自適應壓縮；RU NVL576 15 EF ÷ 144。J2：只作高情境"),
      ("hbm",   "HBM 容量 GB/GPU", "#,##0", [80, 186, 288, 288, 1024], None,
       "GB200 NVL72 13.4 TB ÷ 72；InferenceX 以 192 計。RU HBM4e 約 1 TB/封裝。S28"),
      ("bw",    "HBM 頻寬 TB/s/GPU", "#,##0.00", [3.35, 8, 8, 22, 32], None,
       "Rubin 22 TB/s（NVIDIA 2026 上修）；RU 4.6 PB/s ÷ 144。S28"),
      ("link",  "EP 通訊頻寬 TB/s/GPU（單向）", "#,##0.00", [0.05, 0.9, 0.9, 1.8, 1.8], None,
       "Hopper EP 跨節點走 400G IB；NVLink 5＝900 GB/s；NVLink 6＝1.8 TB/s（InferenceX 規格表 S20）；RU 取同 VR [Assumed]"),
      ("dom",   "Scale-up 域 GPU 數", "#,##0", [8, 72, 72, 72, 144], None, ""),
      ("ep",    "decode EP 基準寬度", "#,##0", [64, 32, 32, 32, 64], None,
       "GB300 公開配方 dep32（S21）；Hopper 跨節點 [Analogy DeepSeek]；RU [Assumed]。權重放不下時自動加寬"),
      ("be",    "專家權重 bytes/param", "0.0000", [1.0, 0.5625, 0.5625, 0.5625, 0.5625], None,
       "NVFP4＝4 bit＋每 16 值 8 bit scale＝0.5625 B；Hopper FP8"),
      ("bn",    "非專家權重 bytes/param", "0.00", [1, 1, 1, 1, 1], None, "注意力、路由、embedding 以 FP8 存放 [Analogy V4]"),
      ("ninst", "每 prefill 實例 GPU 數（算 TTFT）", "#,##0", [8, 4, 4, 4, 8], None,
       "GB300 配方 dep4 prefill（S21）"),
      ("gpuw",  "GPU 功率 W/封裝（能量用）", "#,##0", [700, 1200, 1400, 1800, 3600], None,
       "Interested-party；Rubin 約 1.8 kW、RU 推估。僅用於能量下限估算"),
      ("ehbm",  "HBM 存取能量 pJ/byte", "#,##0", [31, 25, 25, 20, 18], None,
       "Analogy：HBM3 約 3.9 pJ/bit、HBM3e 約 3、HBM4 約 2.5；區間 ±30%（S29）"),
    ]
    r = 22
    for key, lab, fmt, vals, _, note in rows:
        put(ws, f"A{r}", lab)
        for col, v in zip(GENS, vals):
            put(ws, f"{col}{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE)
        R[key] = r; r += 1
    # effective peak per J2 selector
    put(ws, f"A{r}", "計算用峰值 PF/GPU（依 Serving 峰值情境）", F_BOLD)
    for col in GENS:
        put(ws, f"{col}{r}", f"=IF(Serving!$C$16=2,{col}{R['pk_h']},{col}{R['pk_b']})", fmt="#,##0.000", fill=FILL_KEY)
    R["pk"] = r; r += 1
    put(ws, f"A{r}", "Ridge point（FLOP/byte）")
    for col in GENS:
        put(ws, f"{col}{r}", f"={col}{R['pk']}*1000/{col}{R['bw']}", fmt="#,##0")
    R["ridge"] = r; r += 2
    # ---- Block 3: training peaks (dense, per package) ----
    section(ws, r, "B3. 訓練峰值（Block 3；dense；每 GPU 封裝；MFU 以 FP8 列為分母，J7）", 8); r += 1
    trows = [
      ("tbf16", "BF16 dense PF/GPU", [0.989, 2.5, 2.5, 4.0, 8.0],
       "Interested-party（NVIDIA）：H100 989 TF；GB200／GB300 2.5；VR NVL72 288 PF ÷ 72＝4.0（S36）；RU 取 VR×2 [Assumed]"),
      ("tfp8", "FP8 dense PF/GPU（訓練基準，J7）", [1.979, 5, 5, 17.5, 34.7],
       "Interested-party（NVIDIA）：H100 1,979 TF；GB200／GB300 FP8 5 PF（B300 未提升 FP8）；VR NVL72 1,260 PF ÷ 72＝17.5（S36）；RU NVL576 5 EF ÷ 144 [模型內建知識，待查]"),
      ("tfp4", "NVFP4 訓練 dense PF/GPU（Tech_Registry 情境）", [1.979, 10, 15, 35, 73],
       "Hopper 無 FP4，取 FP8；GB200 10（NVIDIA：Rubin 為 Blackwell 3.5 倍）；GB300 15 [Assumed，區間 10–15]；VR 2,520 PF ÷ 72＝35（S36）；RU＝VR × 104/50 [Derived]"),
    ]
    for key, lab, vals, note in trows:
        put(ws, f"A{r}", lab)
        for col, v in zip(GENS, vals):
            put(ws, f"{col}{r}", v, fmt="#,##0.000")
        put(ws, f"H{r}", note, F_NOTE)
        R[key] = r; r += 1
    ws.column_dimensions["H"].width = 70
    return R

def arch(wb):
    ws = wb.create_sheet("Arch", 3)
    title(ws, "Arch — 三層級代表架構（D5：每層級一個代表；參數為公開模型卡或推估）",
          "Luna／Sol 以公開權重模型為物理代表 [Analogy：對應封閉層級]；Astra 為封閉前沿代理，KV 以情境處理（J1）")
    for c, w in zip("ABCDEFG", [30, 12, 16, 16, 18, 16, 80]): ws.column_dimensions[c].width = w
    for c, v in zip("ABCDEFG", ["參數", "單位", "Luna（低層）", "Sol（中層）", "Astra（頂層）", "標記", "來源／說明"]):
        put(ws, f"{c}4", v, F_BOLD)
    R = {}
    rows = [
      ("rep", "代表架構", "", ["DeepSeek V4-Flash 類", "DeepSeek V4-Pro 類", "封閉前沿代理"], None, "Decision", "D5；Andy 2026-09-30 確認"),
      ("T", "總參數", "B", [284, 1600, 4000], "#,##0", "Verified／Assumed", "V4-Flash 284B、V4-Pro 1.6T（模型卡，S27）；Astra 4T [Assumed，區間 2–10T]"),
      ("A", "啟用參數", "B", [13, 49, 180], "#,##0", "Verified／Assumed", "V4-Flash 13B、V4-Pro 49B；Astra 180B [Assumed，區間 60–250B]"),
      ("L", "層數", "層", [43, 61, 100], "#,##0", "Verified／Assumed", "V4-Pro 61（config.json）；V4-Flash 43（二手）；Astra [Assumed]"),
      ("d", "d_model", "", [4096, 7168, 12288], "#,##0", "Verified／Derived", "V4-Pro 7168；V4-Flash 由專家維度反推；Astra [Assumed]"),
      ("hq", "query heads", "", [64, 128, 96], "#,##0", "Verified／Analogy", "V4-Pro 128；V4-Flash 取 Pro 一半 [Analogy]"),
      ("hd", "head_dim", "", [512, 512, 128], "#,##0", "Verified／Assumed", "V4 單一 512 維 KV head；Astra 128"),
      ("E", "routed experts", "", [256, 384, 512], "#,##0", "Verified／Assumed", ""),
      ("k", "每 token 啟用 routed experts", "", [6, 6, 16], "#,##0", "Verified／Assumed", ""),
      ("s", "shared experts", "", [1, 1, 1], "#,##0", "Verified", ""),
      ("V", "vocab", "", [129280, 129280, 200000], "#,##0", "Verified／Assumed", ""),
      ("ff", "全注意力層比例", "%", [0.5, 0.5, 1], "0%", "Verified／Assumed", "V4：CSA 與 HCA 約各半；Astra 全層注意力"),
      ("cap", "全注意力層跨度上限（0＝全上下文）", "tok", [4224, 4224, 0], "#,##0", "Derived", "V4 CSA：top-k 1,024 壓縮塊 × 4 ＋ 128 窗口"),
      ("comp", "其他層壓縮比", "x", [128, 128, 1], "#,##0", "Verified", "V4 HCA 128× 壓縮"),
      ("win", "其他層滑動窗", "tok", [128, 128, 0], "#,##0", "Verified", ""),
      ("kvsel", "Astra KV 情境（1 混合／2 全層 MLA／3 GQA-8）", "選擇", [None, None, 2], "0", "Decision", "J1：基準 2（Andy 2026-09-30 確認）"),
      ("kv1", "KV bytes/token — 情境 1", "B", [2795, 3965, 14976], "#,##0", "Derived／Assumed", "Luna 65×43、Sol 65×61（v4 推導，FP8 KV）；Astra 混合：26% 層 × 576 × 100 層（類 K3）"),
      ("kv2", "KV bytes/token — 情境 2", "B", [2795, 3965, 57600], "#,##0", "Derived／Assumed", "Astra 全層 MLA：576 × 100"),
      ("kv3", "KV bytes/token — 情境 3", "B", [2795, 3965, 204800], "#,##0", "Derived／Assumed", "Astra GQA-8：8 × 128 × 2 × 100"),
    ]
    r = 5
    for key, lab, unit, vals, fmt, tag, note in rows:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDE", vals):
            if v is not None: put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE)
        R[key] = r; r += 1
    section(ws, r, "導出", 7); r += 1
    der = [
      ("kv", "KV bytes/token（採用）", "B", "=CHOOSE(IF({c}{kvsel}=\"\",1,{c}{kvsel}),{c}{kv1},{c}{kv2},{c}{kv3})", "#,##0"),
      ("emb", "Embedding＋LM head 參數", "B", "={c}{V}*{c}{d}*2/1E9", "#,##0.00"),
      ("pe", "每 routed expert 參數", "B", "=({c}{T}-{c}{A})/({c}{L}*({c}{E}-{c}{k}))", "0.0000"),
      ("ne", "非專家參數（注意力、路由、embedding）", "B", "={c}{A}-{c}{L}*({c}{k}+{c}{s})*{c}{pe}", "#,##0.0"),
      ("ex", "專家參數", "B", "={c}{T}-{c}{ne}", "#,##0.0"),
      ("attc", "注意力 FLOPs／每個被注意的 token", "FLOP", "=4*{c}{hq}*{c}{hd}*{c}{L}", "#,##0"),
      ("kv128", "128K 上下文每序列 KV", "GB", "={c}{kv}*128000/1E9", "#,##0.00"),
    ]
    for key, lab, unit, f, fmt in der:
        R[key] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDE":
            m = {k: v for k, v in R.items()}; m["c"] = c
            put(ws, f"{c}{r}", f.format(**m), fmt=fmt, fill=FILL_KEY if key == "kv" else None)
        r += 1
    put(ws, f"G{R['pe']}", "由公開總參數與啟用參數反推，確保總數吻合（v4 方法）", F_NOTE)
    ws.freeze_panes = "C5"
    return R

def serving(wb):
    ws = wb.create_sheet("Serving", 4)
    title(ws, "Serving — 服務設定與各層級 SLO（主流：分離式 P/D、wide EP、attention DP、NVFP4、MTP、前綴快取）",
          "藍字＝輸入。SLO 依 J3 採市場觀測輸出速度（Artificial Analysis 2026-09，S26）")
    for c, w in zip("ABCDEF", [44, 14, 16, 16, 16, 90]): ws.column_dimensions[c].width = w
    put(ws, "A4", "全域設定", F_BOLD); put(ws, "B4", "單位", F_BOLD); put(ws, "C4", "值", F_BOLD); put(ws, "D4", "標記", F_BOLD); put(ws, "E4", "", F_BOLD); put(ws, "F4", "說明", F_BOLD)
    g = [
      (5, "服務架構", "", "分離式 P/D＋wide EP＋attention DP", None, "Decision", "D6 與 Block 2 命題"),
      (6, "MTP 草稿數 N", "tok", 3, "0", "Analogy", "DeepSeek MTP；區間 1–5"),
      (7, "每個草稿 token 接受率 α", "%", 0.70, "0%", "Verified-measured", "SGLang 修正後 0.57→0.70（S21）；區間 0.6–0.8"),
      (8, "每步期望接受 token a", "tok", "=(1-C7^(C6+1))/(1-C7)", "0.00", "Derived", "(1−α^(N+1))/(1−α)"),
      (9, "HBM 保留比例（啟用值、工作區）", "%", 0.10, "0%", "Assumed", "區間 5–20%"),
      (10, "非專家權重占可用 HBM 上限", "%", 0.20, "0%", "Assumed", "超過時自動以注意力 TP 切分"),
      (11, "專家權重占可用 HBM 上限", "%", 0.40, "0%", "Assumed", "超過時自動加寬 EP"),
      (12, "EP 啟用值 bytes/元素（dispatch＋combine）", "B", 3, "0.0", "Analogy", "FP8 dispatch 1 B＋BF16 combine 2 B"),
      (13, "KV 讀取頻寬效率 η_mem", "%", 0.70, "0%", "Analogy", "區間 0.5–0.85"),
      (14, "EP 通訊效率 η_link", "%", 0.70, "0%", "Analogy", "區間 0.5–0.85"),
      (15, "快取命中 KV 載入頻寬", "TB/s/GPU", 0.10, "0.00", "Assumed", "主機記憶體／SSD 經 NIC 載入；區間 0.05–0.4。未計快取儲存成本"),
      (16, "峰值情境（1＝dense 基準／2＝NVFP4 推論高）", "選擇", 1, "0", "Decision", "J2：基準 1"),
      (17, "基準利用率（第 0 層）", "%", 0.60, "0%", "Assumed", "J6：Andy 尚未給值，暫沿用 OpenAI v0.5 的 60%（區間 40–80%）。Unit_Cost 同時輸出 100% 版"),
      (18, "實測→生產效率折減", "x", 1.0, "0.00", "Assumed", "待 Andy 決定。基準測試為固定長度、穩態負載；生產環境另有長度變異、路由不均、故障。1.0＝不折減。作用：η_p、η_d 乘此值，每層延遲除以此值。第二來源（MLPerf、DeepSeek 自揭）目前均高於本模型，見 Calib H 節"),
    ]
    for r, lab, unit, v, fmt, tag, note in g:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt)
        put(ws, f"D{r}", tag, F_NOTE); put(ws, f"F{r}", note, F_NOTE)
    ws["C17"].fill = PatternFill("solid", fgColor="FFFFFF00"); ws["C18"].fill = PatternFill("solid", fgColor="FFFFFF00")
    section(ws, 19, "各層級 SLO 與參考任務", 6)  # row 18 used by derating
    for c, v in zip("ABCDEF", ["項目", "單位", "=Arch!C4", "=Arch!D4", "=Arch!E4", "說明"]):
        put(ws, f"{c}20", v, F_HLINK if "!" in v else F_BOLD)
    t = [
      (21, "SLO：每用戶 decode 速度下限", "tok/s", [120, 65, 55], "#,##0", "Verified-measured（市場觀測）：GPT-5.6 Luna 約 120、GPT-5.6 Sol 約 68、GPT-6 Astra 約 52–56、Opus 5 約 54 tok/s（S26）。區間 Luna 100–300、Sol 50–100、Astra 30–75"),
      (22, "TTFT 上限（只作檢查）", "s", [2, 3, 5], "0.0", "Assumed"),
      (23, "參考 ISL（每次請求輸入）", "tok", [8192, 16384, 32768], "#,##0", "Assumed：Astra 用於長任務；上下文敏感度見 Sens_Perf"),
      (24, "參考 OSL（含思考）", "tok", [1024, 2048, 4096], "#,##0", "Assumed"),
      (25, "decode 平均上下文", "tok", ["=C23+C24/2", "=D23+D24/2", "=E23+E24/2"], "#,##0", "Derived"),
      (26, "prefill 平均位置", "tok", ["=C23/2", "=D23/2", "=E23/2"], "#,##0", "Derived"),
    ]
    for r, lab, unit, vals, fmt, note in t:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDE", vals): put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"F{r}", note, F_NOTE)
    for c in "CDE": ws[f"{c}21"].fill = FILL_KEY
    return ws

def energy_inputs(wb):
    ws = wb.create_sheet("Energy")
    title(ws, "Energy — 逐步能量下限與閉合檢查",
          "物理下限＝FLOPs × pJ/FLOP ＋ HBM bytes × pJ/byte ＋ EP bytes × pJ/byte；閉合：下限功率 ≤ 機架平均用電（Block 1 輸入 Inputs!E10）")
    for c, w in zip("ABCDEF", [44, 14, 14, 14, 16, 80]): ws.column_dimensions[c].width = w
    put(ws, "A4", "輸入", F_BOLD)
    put(ws, "A5", "GPU 功率中可歸於運算的比例"); put(ws, "B5", "%"); put(ws, "C5", 0.6, fmt="0%")
    put(ws, "F5", "Assumed：pJ/FLOP＝GPU 功率 × 此比例 ÷ 峰值（滿載上限口徑），區間 0.4–0.8", F_NOTE)
    put(ws, "A6", "EP 通訊能量 NVLink"); put(ws, "B6", "pJ/byte"); put(ws, "C6", 10, fmt="0")
    put(ws, "F6", "Analogy：SerDes＋交換約 1–2 pJ/bit；區間 5–20", F_NOTE)
    put(ws, "A7", "EP 通訊能量 IB（Hopper）"); put(ws, "B7", "pJ/byte"); put(ws, "C7", 40, fmt="0")
    put(ws, "F7", "Analogy：含光模組與網卡；區間 20–80", F_NOTE)
    return ws

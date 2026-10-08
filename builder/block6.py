# Block 6 (v5.15): Alloc_In (inputs) and Alloc (derivation) — lab compute allocation between R&D and serving.
# Work order docs/workorders/20261004_v5.15.md (B3–B5, B8, H). Decisions A1–A10 (A9 demand route, A10 tokens per prompt).
# Alloc_In: every number is an Excel-owned blue input (restored by preserve.py from the base workbook).
# Alloc: formulas only; key quantities are named ranges (AL_ = display only, IF_Alloc* = downstream via Interface F).
from common import *
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

SLO = "SLO 不可達"
SPEND_SID = "SRC_DEM_018"    # v5.29 X14 (k): OpenAI 2025 inference spend (Azure billing, full-year estimate) replaces SRC_DEM_004 (Superseded; 8.4 -> 12.6 $B)
GENS = [("Hopper", 1), ("GB200", 2), ("GB300", 3), ("VR200", 4)]          # service-mix generations and their generation index (Spec_Rack order)
TIERS = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]


def nm(wb, n, ref):
    if n in wb.defined_names: del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


def _row_of(ws, label):
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, 1).value == label: return r
    raise KeyError(f"{ws.title}: row label not found: {label}")


# ---------------------------------------------------------------- Alloc_In
# (label, unit, base, low, high, tag, decision／source, name stem)   — labels are the preserve.py keys (column A)
IN_ROWS = [
    ("實驗室", "選擇", "OpenAI", None, None, "Decision", "A8（只放 OpenAI 一組；Anthropic 待來源查核後加入）", "Lab"),
    ("家族計畫數 N_major（個／年）", "個／年", 1, 1, 2, "Assumed", "8f 驅動表：前沿實驗室每年約 1–2 個旗艦家族", "Nmajor"),
    ("改版計畫數 N_refresh（個／年）", "個／年", 2, 0, 4, "Assumed", "8f 驅動表、A2：改版計畫計入", "Nrefresh"),
    ("計畫規模倍數 k（相對 Block 3）", "x", 1, 0.5, 7, "Assumed", "A3：不以 59% 校準 k；校準值只反推隱含 N × k（E 節）", "k"),
    ("服務世代組合：Hopper", "%", 0, 0, 1, "Assumed", "補充 2：2025 機隊含 Hopper（基準 0；h_alloc_mix_2025 情境為 Hopper 60%／GB200 40%）", "MixHopper"),
    ("服務世代組合：GB200", "%", 0.4, 0, 1, "Assumed", "8f 驅動表：服務機隊的世代組合（四者合計 100%）", "MixGB200"),
    ("服務世代組合：GB300", "%", 0.4, 0, 1, "Assumed", "同上", "MixGB300"),
    ("服務世代組合：VR200", "%", 0.2, 0, 1, "Assumed", "同上", "MixVR200"),
    ("機隊年成長率 g", "%", 0, 0, 1, "Assumed（情境）", "A6：成長只作情境；基準為穩態年度（A1）", "g"),
    ("API 全年平均 ÷ 10 月時點值", "x", 0.75, 0.6, 0.9, "Assumed", "A9：API 處理量為 2025-10 時點值，換成全年平均", "APIratio"),
    ("每則提示 token 數", "tok", 2000, 1000, 6000, "Assumed", "A10：含輸入、上下文、推理與輸出 token；上限 6,000 無直接來源（Q1 最弱輸入）", "TokPerPrompt"),
    ("ChatGPT token 中免費用戶占比", "%", 0.6, 0.4, 0.8, "Assumed", "新增；以 L1 外部對照（免費服務算力占比）檢查", "FreeShare"),
]


def alloc_in(wb):
    ws = wb.create_sheet("Alloc_In")
    title(ws, "Alloc_In — Block 6 輸入（藍字＝輸入；全部 Assumed 或 Decision，附區間；登錄於 Gov_Map）",
          "研發與服務的算力配置（A1–A10）：實驗室年度算力＝研發需求＋服務需求。研發占比的物理部分只給下限，實際占比由策略變數決定。訓練世代不設輸入，沿用 Interface IF_TrainGenDefault（J13）")
    for i, h in enumerate(["標籤", "單位", "基準", "低", "高", "標記", "決策／來源"]):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True)
    for c, w in zip("ABCDEFG", [40, 9, 11, 9, 9, 16, 70]): ws.column_dimensions[c].width = w
    R = {}
    for j, (lab, unit, base, lo, hi, tag, src, stem) in enumerate(IN_ROWS):
        r = 5 + j; R[stem] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        fmt = "0%" if unit == "%" else ("#,##0" if unit == "tok" else "0.0")
        put(ws, f"C{r}", base, F_IN, fmt=fmt if stem != "Lab" else None, fill=FILL_KEY)
        if lo is not None:
            put(ws, f"D{r}", lo, F_IN, fmt=fmt); put(ws, f"E{r}", hi, F_IN, fmt=fmt)
        else:
            put(ws, f"D{r}", "—"); put(ws, f"E{r}", "—")
        put(ws, f"F{r}", tag); put(ws, f"G{r}", src, F_NOTE, wrap=True)
        nm(wb, f"AL_{stem}", f"Alloc_In!$C${r}")
        if lo is not None:
            nm(wb, f"AL_{stem}_Lo", f"Alloc_In!$D${r}"); nm(wb, f"AL_{stem}_Hi", f"Alloc_In!$E${r}")
    nm(wb, "AL_MixGen", f"Alloc_In!$C${R['MixHopper']}:$C${R['MixVR200']}")
    dv = DataValidation(type="list", formula1='"OpenAI"', allow_blank=False); ws.add_data_validation(dv); dv.add(f"C{R['Lab']}")
    r = 5 + len(IN_ROWS) + 1
    put(ws, f"A{r}", "服務世代組合合計（應為 100%；Checks H1）", F_BOLD)
    put(ws, f"C{r}", "=SUM(AL_MixGen)", fmt="0%"); R["mixsum"] = r
    put(ws, f"A{r+2}", "訓練世代不設輸入：沿用 IF_TrainGenDefault（J13，目前為 VR200）。實驗室選擇器目前只有 OpenAI（A8）。", F_NOTE)
    ws.freeze_panes = "A5"
    return R


# ---------------------------------------------------------------- Alloc
def alloc(wb, AIN):
    ws = wb.create_sheet("Alloc")
    title(ws, "Alloc — 研發與服務的算力配置（需求 D → 服務 GW → 研發 GW → Q1、Q2；A1–A10；基準為 2025 穩態年度）",
          "每列顯示推導：C 欄為數值（世代、層級分列者為 C–E 欄）；G 欄為算式說明（向右延伸顯示）。需求以 token 路線為基準（A9），支出路線在 F 節並列為外部對照。"
          "SLO 不可達時各格回傳文字「SLO 不可達」（比照 Fleet_1GW 第 18 列）。")
    for c, w in zip("ABCDEFGH", [58, 11, 15, 15, 15, 15, 15, 12]): ws.column_dimensions[c].width = w
    R = {}; r = 4

    def hdr(text):
        nonlocal r
        section(ws, r, text, 7); r += 1

    def line(key, lab, unit, f, fmt="#,##0.000", name=None, note=None, key_fill=False, cols="C", span=None):
        """one row; f is a formula string, or a dict col->formula for multi-column rows"""
        nonlocal r
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        if isinstance(f, dict):
            for c, v in f.items(): put(ws, f"{c}{r}", v, fmt=fmt, fill=FILL_KEY if key_fill else None)
        else:
            put(ws, f"C{r}", f, fmt=fmt, fill=FILL_KEY if key_fill else None)
        if note: put(ws, f"G{r}", note, F_NOTE)
        R[key] = r
        if name:
            nm(wb, name, f"Alloc!$C${r}" if not span else f"Alloc!${span[0]}${r}:${span[1]}${r}")
        r += 1

    # ---------------- A. demand D (token route, A9)
    hdr("A. 需求 D（2025；M tok/年；token 路線為基準，A9）")
    line("api", "API token（SRC_DEM_010 × 525,600 分鐘 × 全年平均比例）", "M tok/年",
         "=SRC_DEM_010*1E9*525600*AL_APIratio/1E6", "#,##0", "AL_DAPI",
         "SRC_DEM_010（B tok/min，2025-10 時點值）× 1e9 × 525,600 × 全年平均比例 ÷ 1e6")
    line("chat", "ChatGPT token（SRC_DEM_012 × 每則提示 token 數 × 365）", "M tok/年",
         "=SRC_DEM_012*1E9*AL_TokPerPrompt*365/1E6", "#,##0", "AL_DChat",
         "SRC_DEM_012（B 則/日，2025-07 時點值視同全年平均：年內近似線性成長；不乘比例）× 1e9 × 每則 token × 365 ÷ 1e6")
    line("chatfree", "ChatGPT 免費 token", "M tok/年", "=AL_DChat*AL_FreeShare", "#,##0", "AL_DChatFree", "ChatGPT token × 免費占比")
    line("chatpaid", "ChatGPT 付費 token", "M tok/年", "=AL_DChat-AL_DChatFree", "#,##0", "AL_DChatPaid", "ChatGPT token − 免費 token")
    line("dpaid", "付費 D（API＋ChatGPT 付費）", "M tok/年", "=AL_DAPI+AL_DChatPaid", "#,##0", "AL_DPaid")
    line("dfree", "免費 D（ChatGPT 免費）", "M tok/年", "=AL_DChatFree", "#,##0", "AL_DFree")
    line("dtot", "D 合計", "M tok/年", "=AL_DPaid+AL_DFree", "#,##0", "AL_D", key_fill=True)
    line("ddaily", "每日 token 合計（供 Epoch 對照）", "T tok/日", "=AL_D/365/1E6", "#,##0.00", "AL_DDaily",
         "D 合計 ÷ 365 ÷ 1e6（M → T）；對照 SRC_DEM_013（10–100 T/日）")
    r += 1

    # ---------------- B. serving GW
    hdr("B. 服務 GW（token 路線；欄 C–F＝服務世代 Hopper／GB200／GB300／VR200）")
    put(ws, f"A{r}", "世代", F_BOLD)
    for c, (g, gi) in zip("CDEF", GENS): put(ws, f"{c}{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,{c}{r+1})", F_HLINK)
    R["gen"] = r; r += 1
    line("genidx", "世代索引（Spec_Rack 順序）", "索引", {c: gi for c, (g, gi) in zip("CDEF", GENS)}, "0")
    for c in "CDEF": ws[f"{c}{R['genidx']}"].font = F_CALC
    line("col", "Interface 欄索引（基準成本欄；與 L1 第 5–8 列 INDEX 用法一致）", "索引",
         {c: f"=3*({c}{R['genidx']}-1)+2" for c in "CDEF"}, "0", "AL_GenCol", span=("C", "F"))
    line("share", "世代占比（Alloc_In）", "%",
         {"C": "=AL_MixHopper", "D": "=AL_MixGB200", "E": "=AL_MixGB300", "F": "=AL_MixVR200"}, "0%", "AL_ShareGen", span=("C", "F"))
    mp, mf = "B4_MixPaid", "B4_MixFree"
    def reach(mix, c):
        return "AND(" + ",".join(f"OR(INDEX({mix},1,{t})=0,INDEX(IF_TokGW_{tn},1,{c}${R['col']})>0)" for t, (tn, _) in enumerate(TIERS, 1)) + ")"
    line("ok", "可服務（付費與免費組合內各層級皆 SLO 可達＝1；同 Fleet_1GW 第 18 列）", "旗標",
         {c: f"=IF(AND({reach(mp, c)},{reach(mf, c)}),1,0)" for c in "CDEF"}, "0", "AL_GenOK", span=("C", "F"))
    def invsum(mix, c):
        return "+".join(f"INDEX({mix},1,{t})/INDEX(IF_TokGW_{tn},1,{c}${R['col']})" for t, (tn, _) in enumerate(TIERS, 1))
    line("ip", "Σ（付費層級組合 ÷ 每 GW 總產出）", "GW·年／M tok", {c: f'=IF({c}{R["ok"]}=1,{invsum(mp, c)},"{SLO}")' for c in "CDEF"}, "0.00E+00",
         note="付費 token 的層級組合（Cap_In）依各層級每 GW 總產出（IF_TokGW_*）加權：每 M tok 佔用的 GW·年（100% 利用率）")
    line("if", "Σ（免費層級組合 ÷ 每 GW 總產出）", "GW·年／M tok", {c: f'=IF({c}{R["ok"]}=1,{invsum(mf, c)},"{SLO}")' for c in "CDEF"}, "0.00E+00")
    line("capp", "每 GW 年產能（付費；基準利用率）", "M tok/GW/年",
         {c: f'=IF({c}{R["ok"]}=1,IF_Util/{c}{R["ip"]},"{SLO}")' for c in "CDEF"}, "#,##0", "AL_CapPaid", "利用率 IF_Util ÷ Σ；與 Fleet_1GW 第 19 列同式（每 GW）", span=("C", "F"))
    line("capf", "每 GW 年產能（免費；基準利用率）", "M tok/GW/年",
         {c: f'=IF({c}{R["ok"]}=1,IF_Util/{c}{R["if"]},"{SLO}")' for c in "CDEF"}, "#,##0", "AL_CapFree", "與 Fleet_1GW 第 20 列同式（每 GW）", span=("C", "F"))
    def blend(caprow, sharecells=("C", "D", "E")):
        ss = [f"{c}${R['share']}" for c in "CDEF"]; cc = [f"{c}${caprow}" for c in "CDEF"]
        bad = "OR(" + ",".join(f"AND({s}>0,NOT(ISNUMBER({k})))" for s, k in zip(ss, cc)) + ")"
        return f'=IF({bad},"{SLO}",' + "+".join(f"IF({s}>0,{s}*{k},0)" for s, k in zip(ss, cc)) + ")"
    line("bp", "世代組合後每 GW 年產能（付費）＝Σ 世代占比 × 各世代產能", "M tok/GW/年", blend(R["capp"]), "#,##0", "AL_BlendPaid")
    line("bf", "世代組合後每 GW 年產能（免費）", "M tok/GW/年", blend(R["capf"]), "#,##0", "AL_BlendFree")
    line("sgp", "服務 GW（付費）＝付費 D ÷ 付費產能", "GW", f'=IF(AND(ISNUMBER(AL_BlendPaid),AL_DPaid>=0),IF(AL_BlendPaid>0,AL_DPaid/AL_BlendPaid,"{SLO}"),"{SLO}")', "0.0000", "AL_ServeGWPaid")
    line("sgf", "服務 GW（免費）＝免費 D ÷ 免費產能", "GW", f'=IF(AND(ISNUMBER(AL_BlendFree),AL_DFree>=0),IF(AL_BlendFree>0,AL_DFree/AL_BlendFree,"{SLO}"),"{SLO}")', "0.0000", "AL_ServeGWFree")
    line("sg", "服務 GW 合計", "GW", f'=IF(AND(ISNUMBER(AL_ServeGWPaid),ISNUMBER(AL_ServeGWFree)),AL_ServeGWPaid+AL_ServeGWFree,"{SLO}")', "0.0000", "AL_ServeGW", key_fill=True)
    line("sgg", "各世代服務 GW＝合計 × 世代占比", "GW",
         {c: f'=IF(ISNUMBER(AL_ServeGW),AL_ServeGW*{c}{R["share"]},"{SLO}")' for c in "CDEF"}, "0.0000", "AL_ServeGen", span=("C", "F"))
    line("hold", "各世代每 GW 年經濟持有成本（IF_HoldEcon，基準成本）", "$B/GW/年",
         {c: f"=INDEX(IF_HoldEcon,1,{c}{R['col']})" for c in "CDEF"}, "0.000", "AL_HoldGen", span=("C", "F"))
    r += 1

    # ---------------- C. R&D GW-years (physical floor)
    hdr("C. 研發 GW 年（物理下限；訓練世代＝IF_TrainGenDefault；欄 C–E＝層級 Luna／Sol／Astra，F＝合計）")
    line("tg", "訓練世代索引（IF_TrainGenDefault，J13）", "索引", "=IF_TrainGenDefault", "0", "AL_TrainGen")
    line("tc", "Interface／Training 欄索引（基準成本欄；Training 另加層級索引）", "索引", "=3*(AL_TrainGen-1)+2", "0", "AL_TrainCol")
    put(ws, f"A{r}", "層級", F_BOLD)
    for c, (tk, tn) in zip("CDE", TIERS): put(ws, f"{c}{r}", tn, F_BOLD)
    put(ws, f"F{r}", "合計", F_BOLD); r += 1
    line("tier", "層級索引", "索引", {"C": 1, "D": 2, "E": 3}, "0")
    for c in "CDE": ws[f"{c}{R['tier']}"].font = F_CALC
    line("fam", "家族計畫 GW 年（IF_ProgGWyr；含研發倍數；等同 Fleet_1GW 第 33 列）", "GW·年",
         {**{c: f"=INDEX(IF_ProgGWyr_{tk},1,AL_TrainCol)" for c, (tk, tn) in zip("CDE", TIERS)}, "F": f"=SUM(C{r}:E{r})"}, "0.0000", "AL_FamGWyr",
         "每個家族計畫：三層級最終訓練 GPU 小時 × 研發倍數，換算為訓練世代的 GW 年", key_fill=False)
    nm(wb, "AL_FamGWyr", f"Alloc!$F${R['fam']}")
    tr = wb["Training"]
    r104 = _row_of(tr, "後訓練 GPU 小時（SFT＋RL＋蒸餾）"); r18 = _row_of(tr, "每 GW GPU 數")
    line("post", "後訓練 GPU 小時（SFT＋RL＋蒸餾；單一模型；Training 頁）", "GPU-hr",
         {**{c: f"=INDEX(Training!$C${r104}:$Q${r104},3*(AL_TrainGen-1)+{c}{R['tier']})" for c in "CDE"}, "F": f"=SUM(C{r}:E{r})"}, "#,##0",
         note="Training 第 104 列「後訓練 GPU 小時（SFT＋RL＋蒸餾）」，不含第 105 列；依訓練世代與層級取值；依欄 A 標籤定位（工作單 r3 更正 2）")
    line("gpugw", "每 GW GPU 數（訓練世代）", "顆", {c: f"=INDEX(Training!$C${r18}:$Q${r18},3*(AL_TrainGen-1)+{c}{R['tier']})" for c in "CDE"}, "#,##0")
    line("ref", "改版計畫 GW 年＝後訓練 GPU 小時 × 研發倍數 ÷（每 GW GPU 數 × 8,760）", "GW·年",
         {**{c: f"={c}{R['post']}*IF_RDMult/({c}{R['gpugw']}*8760)" for c in "CDE"}, "F": f"=SUM(C{r}:E{r})"}, "0.0000",
         note="改版（refresh）計畫：後訓練 GPU 小時 × 研發倍數（IF_RDMult，A2）；GW 年換算同 Training「占 1 GW 一年」")
    nm(wb, "AL_RefGWyr", f"Alloc!$F${R['ref']}")
    line("rd", "研發 GW 年＝k ×（N_major × 家族計畫＋N_refresh × 改版計畫）", "GW·年",
         "=AL_k*(AL_Nmajor*AL_FamGWyr+AL_Nrefresh*AL_RefGWyr)", "0.0000", "AL_RDGW", key_fill=True)
    line("rdg", "研發 GW 年（成長情境，A6）＝研發 GW 年 ×（1＋g）；服務 GW 不變", "GW·年", "=AL_RDGW*(1+AL_g)", "0.0000", "AL_RDGWg")
    line("ht", "訓練世代每 GW 年經濟持有成本（IF_HoldEcon，基準成本）", "$B/GW/年", "=INDEX(IF_HoldEcon,1,AL_TrainCol)", "0.000", "AL_HoldTrain")
    line("rdcost", "研發算力成本（研發 GW × 訓練世代持有成本；Q3 的算力部分）", "$B/年", "=AL_RDGW*AL_HoldTrain", "0.000", "AL_RDCost")
    r += 1

    # ---------------- D. Q1, Q2
    hdr("D. Q1、Q2（R1 基準，R2 並列；A7）")
    line("q1", "Q1（R1）研發算力占比＝研發 GW ÷（研發 GW＋服務 GW）", "%", f'=IF(ISNUMBER(AL_ServeGW),AL_RDGW/(AL_RDGW+AL_ServeGW),"{SLO}")', "0.0%", "AL_Q1", key_fill=True)
    line("q1b", "Q1（R2，免費服務算作產品改良）＝（研發 GW＋免費服務 GW）÷ 總 GW", "%",
         f'=IF(ISNUMBER(AL_ServeGW),(AL_RDGW+AL_ServeGWFree)/(AL_RDGW+AL_ServeGW),"{SLO}")', "0.0%", "AL_Q1R2")
    line("q2", "Q2 研發算力成本占比＝研發 GW × 持有成本 ÷（研發 GW × 持有成本＋Σ 各世代服務 GW × 各世代持有成本）", "%",
         f'=IF(ISNUMBER(AL_ServeGW),AL_RDGW*AL_HoldTrain/(AL_RDGW*AL_HoldTrain+SUMPRODUCT(AL_ServeGen,AL_HoldGen)),"{SLO}")', "0.0%", "AL_Q2", "利用率不進入成本占比（A5）", key_fill=True)
    line("q1g", "Q1（R1；成長情境 g）", "%", f'=IF(ISNUMBER(AL_ServeGW),AL_RDGWg/(AL_RDGWg+AL_ServeGW),"{SLO}")', "0.0%", "AL_Q1g")
    line("q2g", "Q2（成長情境 g）", "%",
         f'=IF(ISNUMBER(AL_ServeGW),AL_RDGWg*AL_HoldTrain/(AL_RDGWg*AL_HoldTrain+SUMPRODUCT(AL_ServeGen,AL_HoldGen)),"{SLO}")', "0.0%", "AL_Q2g")
    line("r3", "R3（內部使用）", "", "缺口：無參數（A7）", None, note="R3 不設公式")
    r += 1

    # ---------------- E. calibration back-solve (A3)
    hdr("E. 校準反推（A3；2025 支出比不用來校準 k，只反推隱含 N × k）")
    line("sr", "2025 支出比＝訓練支出 ÷（推論支出＋訓練支出）", "%", f"=SRC_DEM_006/({SPEND_SID}+SRC_DEM_006)", "0.0%", "AL_SpendRatio", f"SRC_DEM_006 ÷（{SPEND_SID}＋SRC_DEM_006）（v5.29 X14 (k)：推論支出改連 {SPEND_SID}，約 48.8%；v5.28 前為 SRC_DEM_004，約 58.8%）")
    line("irdg", "隱含研發 GW＝支出比 ÷（1 − 支出比）× 服務 GW 合計", "GW", f'=IF(ISNUMBER(AL_ServeGW),AL_SpendRatio/(1-AL_SpendRatio)*AL_ServeGW,"{SLO}")', "0.0000", "AL_ImpliedRDGW")
    line("ink", "隱含 N × k（以家族計畫當量）＝隱含研發 GW ÷ 家族計畫 GW 年", "個", f'=IF(ISNUMBER(AL_ImpliedRDGW),AL_ImpliedRDGW/AL_FamGWyr,"{SLO}")', "0.00", "AL_ImpliedNk", key_fill=True)
    line("j8", "J8 落差＝隱含 N × k ÷（N_major＋N_refresh × 改版÷家族）", "x",
         f'=IF(ISNUMBER(AL_ImpliedNk),AL_ImpliedNk/(AL_Nmajor+AL_Nrefresh*AL_RefGWyr/AL_FamGWyr),"{SLO}")', "0.00", "AL_J8Gap",
         "相對 Alloc_In 基準的規模落差：1 表示基準 N、k 已吻合支出比")
    r += 1

    # ---------------- F. external comparisons
    hdr("F. 外部對照（同時寫入 L1；支出路線與 SRC_DEM_013）")
    line("sgx", f"支出路線服務 GW＝{SPEND_SID}（$B；Azure 計價）÷ Σ（世代占比 × 各世代持有成本）", "GW", f"={SPEND_SID}/SUMPRODUCT(AL_ShareGen,AL_HoldGen)", "0.0000", "AL_ServeGWSpend",
         f"單位：$B ÷ ($B/GW/年) ＝ GW（不乘 1e9；工作單 r3 更正 1，Andy／chat 2026-10-04）；v5.29 X14 (k)：SRC_DEM_004 → {SPEND_SID}")
    line("fsh", "免費服務算力占比（token 路線）＝免費服務 GW ÷ 服務 GW 合計", "%", f'=IF(ISNUMBER(AL_ServeGW),AL_ServeGWFree/AL_ServeGW,"{SLO}")', "0.0%", "AL_FreeServeShare")
    line("fsx", f"免費推論支出占比（支出口徑）＝SRC_DEM_005 ÷ {SPEND_SID}", "%", f"=SRC_DEM_005/{SPEND_SID}", "0.0%", "AL_FreeSpendShare",
         f"v5.29 X14 (k)：分母改連 {SPEND_SID}（Azure 計價 12.6）；分子 SRC_DEM_005（3.9，json 口徑）未變，兩者口徑是否一致待 Project 判斷")
    line("dlo", "Epoch 每日 token 低（SRC_DEM_013_Lo）", "T tok/日", "=SRC_DEM_013_Lo", "#,##0.0")
    line("dhi", "Epoch 每日 token 高（SRC_DEM_013_Hi）", "T tok/日", "=SRC_DEM_013_Hi", "#,##0.0")
    line("din", "每日 token 合計是否在 Epoch 區間內", "", '=IF(AL_DDaily<SRC_DEM_013_Lo,"區間外（低於）",IF(AL_DDaily>SRC_DEM_013_Hi,"區間外（高於）","區間內"))', None)
    r += 1

    # ---------------- G. sensitivity table (closed-form; one input at a time; self-check block)
    hdr("G. 敏感度表（一次動一個輸入，取區間低與高；每列以閉式公式重寫 A–D 節推導鏈；端點值引用 Alloc_In 的區間格）")
    put(ws, f"A{r}", "左側 C–L 為該列輸入；M–V 為推導鏈；W 為自我檢查（同一公式、輸入全改回基準，須等於 D 節 Q1、Q2；容差 1e-12；0＝通過）。"
                     "不使用運算列表，也不在 Python 端計算。", F_NOTE); r += 1
    heads_in = ["N_major", "N_refresh", "k", "API 比例", "每則 token", "免費占比", "Hopper", "GB200", "GB300", "VR200"]
    heads_ch = ["付費 D", "免費 D", "付費產能", "免費產能", "服務 GW", "研發 GW", "Q1（R1）", "Q2", "研發算力成本 $B", "每日 T tok"]
    put(ws, f"A{r}", "情境", F_BOLD); put(ws, f"B{r}", "動的輸入", F_BOLD)
    for i, h in enumerate(heads_in + heads_ch + ["自我檢查"]): put(ws, f"{L(3+i)}{r}", h, F_BOLD, wrap=True)
    for i in range(3, 3 + len(heads_in) + len(heads_ch) + 1): ws.column_dimensions[L(i)].width = max(ws.column_dimensions[L(i)].width or 0, 13)
    R["gh"] = r; r += 1
    base = {"Nmaj": "AL_Nmajor", "Nref": "AL_Nrefresh", "k": "AL_k", "ratio": "AL_APIratio", "tok": "AL_TokPerPrompt", "free": "AL_FreeShare",
            "m0": "AL_MixHopper", "m1": "AL_MixGB200", "m2": "AL_MixGB300", "m3": "AL_MixVR200"}
    # (label, input key varied, end label, replacement names (key->name))
    def endp(stem, side): return f"AL_{stem}_{side}"
    scen = [("基準", "—", {})]
    for lab, key, stem in (("N_major", "Nmaj", "Nmajor"), ("N_refresh", "Nref", "Nrefresh"), ("k", "k", "k"), ("每則提示 token 數", "tok", "TokPerPrompt"),
                           ("API 全年平均比例", "ratio", "APIratio"), ("免費占比", "free", "FreeShare")):
        scen.append((f"{lab} 低", lab, {key: endp(stem, "Lo")})); scen.append((f"{lab} 高", lab, {key: endp(stem, "Hi")}))
    scen.append(("服務世代組合：全 GB200", "世代組合", {"m0": "AL_MixHopper_Lo", "m1": "AL_MixGB200_Hi", "m2": "AL_MixGB300_Lo", "m3": "AL_MixVR200_Lo"}))
    scen.append(("服務世代組合：全 VR200", "世代組合", {"m0": "AL_MixHopper_Lo", "m1": "AL_MixGB200_Lo", "m2": "AL_MixGB300_Lo", "m3": "AL_MixVR200_Hi"}))
    keys = ["Nmaj", "Nref", "k", "ratio", "tok", "free", "m0", "m1", "m2", "m3"]
    capp = [f"${c}${R['capp']}" for c in "CDEF"]
    capf = [f"${c}${R['capf']}" for c in "CDEF"]
    holds = [f"${c}${R['hold']}" for c in "CDEF"]

    def chain(rr, ic):
        """chain formulas for row rr; ic maps input key -> column letter (the row's own input cells)"""
        m = [f"{ic['m0']}{rr}", f"{ic['m1']}{rr}", f"{ic['m2']}{rr}", f"{ic['m3']}{rr}"]
        dchat = f"SRC_DEM_012*1E9*{ic['tok']}{rr}*365/1E6"
        dapi = f"SRC_DEM_010*1E9*525600*{ic['ratio']}{rr}/1E6"
        out = {}
        out["dp"] = f"={dapi}+{dchat}*(1-{ic['free']}{rr})"
        out["df"] = f"={dchat}*{ic['free']}{rr}"
        def bl(cap):
            bad = "OR(" + ",".join(f"AND({s}>0,NOT(ISNUMBER({k})))" for s, k in zip(m, cap)) + ")"
            return f'=IF({bad},"{SLO}",' + "+".join(f"IF({s}>0,{s}*{k},0)" for s, k in zip(m, cap)) + ")"
        out["cp"] = bl(capp); out["cf"] = bl(capf)
        return m, out

    sens_cells = {}
    r0 = r
    # main rows then check rows (same builder → same formulas)
    for blk in ("main", "check"):
        rows_here = []
        for lab, varied, rep in scen:
            rr = r
            if blk == "main":
                put(ws, f"A{rr}", lab); put(ws, f"B{rr}", varied)
            else:
                put(ws, f"A{rr}", f"檢查：{lab}（輸入全為基準）", F_NOTE); put(ws, f"B{rr}", varied, F_NOTE)
            ic = {}
            for i, k in enumerate(keys):
                col = L(3 + i); ic[k] = col
                src = rep.get(k) if blk == "main" else None
                fmt = {"m0": "0%", "m1": "0%", "m2": "0%", "m3": "0%", "free": "0%", "ratio": "0.00", "tok": "#,##0", "k": "0.0"}.get(k, "0.0")
                put(ws, f"{col}{rr}", f"={src or base[k]}", fmt=fmt, fill=FILL_KEY if src else None)
            m, ch = chain(rr, ic)
            base_c = 3 + len(keys)                      # first chain column
            cols = {n: L(base_c + i) for i, n in enumerate(["dp", "df", "cp", "cf", "sg", "rd", "q1", "q2", "cost", "daily"])}
            put(ws, f"{cols['dp']}{rr}", ch["dp"], fmt="#,##0"); put(ws, f"{cols['df']}{rr}", ch["df"], fmt="#,##0")
            put(ws, f"{cols['cp']}{rr}", ch["cp"], fmt="#,##0"); put(ws, f"{cols['cf']}{rr}", ch["cf"], fmt="#,##0")
            cp, cf, dp, df_ = (f"{cols[x]}{rr}" for x in ("cp", "cf", "dp", "df"))
            put(ws, f"{cols['sg']}{rr}", f'=IF(AND(ISNUMBER({cp}),ISNUMBER({cf})),IF(AND({cp}>0,{cf}>0),{dp}/{cp}+{df_}/{cf},"{SLO}"),"{SLO}")', fmt="0.0000")
            sg = f"{cols['sg']}{rr}"
            put(ws, f"{cols['rd']}{rr}", f"={ic['k']}{rr}*({ic['Nmaj']}{rr}*AL_FamGWyr+{ic['Nref']}{rr}*AL_RefGWyr)", fmt="0.0000")
            rd = f"{cols['rd']}{rr}"
            put(ws, f"{cols['q1']}{rr}", f'=IF(ISNUMBER({sg}),{rd}/({rd}+{sg}),"{SLO}")', fmt="0.0%")
            hmix = "+".join(f"{s}*{h}" for s, h in zip(m, holds))
            put(ws, f"{cols['q2']}{rr}", f'=IF(ISNUMBER({sg}),{rd}*AL_HoldTrain/({rd}*AL_HoldTrain+{sg}*({hmix})),"{SLO}")', fmt="0.0%")
            put(ws, f"{cols['cost']}{rr}", f"={rd}*AL_HoldTrain", fmt="0.000")
            put(ws, f"{cols['daily']}{rr}", f"=({dp}+{df_})/365/1E6", fmt="#,##0.00")
            rows_here.append((rr, cols))
            r += 1
        sens_cells[blk] = rows_here
        if blk == "main": r += 1
    main_rows, chk_rows = sens_cells["main"], sens_cells["check"]
    ckcol = L(3 + len(keys) + 10)
    for (rr, cols), (rc, colsc) in zip(main_rows, chk_rows):
        q1, q2, q1c, q2c = f"{cols['q1']}{rc}", f"{cols['q2']}{rc}", f"{cols['q1']}{rc}", f"{cols['q2']}{rc}"
        q1c, q2c = f"{colsc['q1']}{rc}", f"{colsc['q2']}{rc}"
        f = (f'=IF(AND(ISNUMBER({q1c}),ISNUMBER({q2c}),ISNUMBER(AL_Q1),ISNUMBER(AL_Q2)),'
             f'IF(AND(ABS({q1c}-AL_Q1)<=1E-12,ABS({q2c}-AL_Q2)<=1E-12),0,1),'
             f'IF(AND(NOT(ISNUMBER({q1c})),NOT(ISNUMBER(AL_Q1))),0,1))')
        put(ws, f"{ckcol}{rr}", f, fmt="0")
    first, last = main_rows[0][0], main_rows[-1][0]
    cols0 = main_rows[0][1]
    nm(wb, "AL_SensQ1", f"Alloc!${cols0['q1']}${first}:${cols0['q1']}${last}")
    nm(wb, "AL_SensQ2", f"Alloc!${cols0['q2']}${first}:${cols0['q2']}${last}")
    nm(wb, "AL_SensCost", f"Alloc!${cols0['cost']}${first}:${cols0['cost']}${last}")
    nm(wb, "AL_SensDaily", f"Alloc!${cols0['daily']}${first}:${cols0['daily']}${last}")
    nm(wb, "AL_SensCheck", f"Alloc!${ckcol}${first}:${ckcol}${last}")
    R["sens_first"], R["sens_last"] = first, last
    ws.freeze_panes = "C4"
    return R


# ---------------------------------------------------------------- Interface F
def interface_b6(wb, start):
    ws = wb["Interface"]; r = start; names = []
    section(ws, r, "F. Block 6 產出（研發與服務的算力配置；2025 穩態年度；服務世代組合與訓練世代見 Alloc_In／Alloc；SLO 不可達時為文字）", 17); r += 1
    rows = [("IF_AllocQ1", "研發算力占比 Q1（R1：研發 GW ÷ 研發＋服務 GW）", "%", "=AL_Q1", "0.0%", True),
            ("IF_AllocQ1_R2", "研發算力占比 Q1（R2：免費服務算作產品改良）", "%", "=AL_Q1R2", "0.0%", False),
            ("IF_AllocQ2", "研發算力成本占比 Q2（已裝 GW × 各世代每 GW 年持有成本；利用率不進入）", "%", "=AL_Q2", "0.0%", True),
            ("IF_AllocServeGW", "服務 GW 合計（token 路線；付費＋免費；IT 關鍵電力）", "GW", "=AL_ServeGW", "0.0000", False),
            ("IF_AllocRDGW", "研發 GW 年（k ×（N_major × 家族＋N_refresh × 改版）；訓練世代＝IF_TrainGenDefault）", "GW·年", "=AL_RDGW", "0.0000", False),
            ("IF_AllocDemand", "需求 D 合計（API＋ChatGPT；付費＋免費 token；2025）", "M tok/年", "=AL_D", "#,##0", False),
            ("IF_AllocImpliedNk", "隱含 N × k（2025 支出比反推；以家族計畫當量；A3）", "個", "=AL_ImpliedNk", "0.00", False)]
    for n, lab, unit, f, fmt, key in rows:
        put(ws, f"A{r}", f"{lab}　[{n}]"); put(ws, f"B{r}", unit); put(ws, f"C{r}", f, fmt=fmt, fill=FILL_KEY if key else None)
        names.append((n, f"Interface!$C${r}")); r += 1
    for n, ref in names: nm(wb, n, ref)
    return {n: ref for n, ref in names}


# ---------------------------------------------------------------- Checks H (appended after the G section; counted in GOV_Errors)
def checks_h(wb):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "H. Alloc 與 L1 檢查（Block 6，v5.15；H3 v5.16）：H1、H2 為 ERROR 計入 GOV_Errors；H3 為 WARN 計入 GOV_Warnings", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    h1 = r
    put(ws, f"A{r}", "H1"); put(ws, f"B{r}", "服務世代組合 Hopper＋GB200＋GB300＋VR200 合計 ≠ 100%（容差 1e-9）"); put(ws, f"C{r}", "ERROR", F_BOLD)
    put(ws, f"D{r}", "=IF(ABS(SUM(AL_MixGen)-1)>1E-9,1,0)", fmt="0"); put(ws, f"E{r}", "Alloc_In 世代組合四格", F_NOTE); r += 1
    h2 = r
    put(ws, f"A{r}", "H2"); put(ws, f"B{r}", "Alloc G 節自我檢查不等於基準的列數（兩邊皆為文字時不報錯）"); put(ws, f"C{r}", "ERROR", F_BOLD)
    put(ws, f"D{r}", "=SUM(AL_SensCheck)", fmt="0"); put(ws, f"E{r}", f"Alloc 敏感度表 {wb.defined_names['AL_SensCheck'].attr_text.split('$')[1]} 欄（容差 1e-12）", F_NOTE); r += 1
    # v5.16 H3 (WARN): L1 rows (from row 5) whose D, E, F are all numbers but E <= D <= F fails (tolerance 1e-12); baseline expected 0
    h3 = r
    D, E, F = (f"L1!${c}$5:${c}$200" for c in "DEF")
    put(ws, f"A{r}", "H3"); put(ws, f"B{r}", "L1 的 D、E、F 皆為數字，但不滿足 E ≤ D ≤ F 的列數"); put(ws, f"C{r}", "WARN", F_BOLD)
    put(ws, f"D{r}", f"=SUMPRODUCT(ISNUMBER({D})*ISNUMBER({E})*ISNUMBER({F})*((({E}>{D})+({D}>{F}))>0))", fmt="0")
    put(ws, f"E{r}", "L1 D、E、F 欄（D＝基準、E＝低、F＝高；只用比較、不做算術，故含文字的列不會產生錯誤值，也不套容差）；情境下利用率或成本參數改變時可能合理翻轉，不計入 GOV_Errors", F_NOTE); r += 1
    nm(wb, "CHK_L1Order", f"Checks!$D${h3}")        # v5.16: named so tests read H3 without a label lookup (the engine cache holds no constant labels)
    # GOV_Warnings (G section WARN total) also counts H3
    wref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    wc = ws[wref]
    if f"D{h3}" not in str(wc.value): wc.value = f"{wc.value}+D{h3}"
    ws[f"B{int(wref[1:])}"].value = "WARN 合計（含 H3）"
    # GOV_Errors (G section total) now also counts H1 and H2
    ref = wb.defined_names["GOV_Errors"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{h1}" not in str(cell.value): cell.value = f"{cell.value}+D{h1}+D{h2}"
    ws[f"B{int(ref[1:])}"].value = "ERROR 合計（CI 讀取 GOV_Errors；含 G 與 H 節）"
    return h1, h2, h3


# ---------------------------------------------------------------- L1 rows (Answers 1–9 and three external comparisons; B6)
def l1_rows_b6(R, DASH, COST_RNG, UTIL_RNG):
    """R: the existing L1 row tuples (key, lab, cond, base, lo, hi, unit, rdef, read, drv, weak, sid, elo, ehi, nmref, where, gap).
    Returns the new tuples. Answers 4–9 only link existing names (no new calculation)."""
    at = {row[0]: i + 5 for i, row in enumerate(R)}        # L1 row of each existing key (rows start at 5)
    out = []
    A = "OpenAI；2025 穩態年度；基準輸入見 Alloc_In"
    def ans(n, q, cond, base, lo, hi, unit, rdef, read, drv, weak, nmref, where, gap):
        out.append((f"Ans{n}", f"問 {n}：{q}", cond, base, lo, hi, unit, rdef, read, drv, weak, DASH, None, None, nmref, where, gap))
    ans(1, "研發算力占比 Q1（R1）", A + "；R1＝研發 GW ÷（研發 GW＋服務 GW）", "=IF_AllocQ1",
        '=IF(ISNUMBER(IF_AllocQ1),MIN(AL_SensQ1),"—")', '=IF(ISNUMBER(IF_AllocQ1),MAX(AL_SensQ1),"—")', "%",
        "Alloc G 節：一次動一個輸入（區間低與高）的最小與最大 Q1（R1）；R2（免費服務算作產品改良）見 IF_AllocQ1_R2",
        "物理部分只給下限（家族＋改版計畫的 GW 年）；實際占比由策略變數決定（N、k）。R2 另列於 IF_AllocQ1_R2（A7）",
        "k、N_refresh、每則提示 token 數、API 全年平均比例", "每則提示 token 數（Assumed，A10）", "IF_AllocQ1", "Alloc 第 D 節；Interface F 節",
        "R3（內部使用）無參數（A7）；本題為單一實驗室（OpenAI）、2025 穩態年度；成長情境見 Alloc D 節")
    ans(2, "研發算力成本占比 Q2", A + "；已裝 GW × 各世代每 GW 年持有成本；利用率不進入（A5）", "=IF_AllocQ2",
        '=IF(ISNUMBER(IF_AllocQ2),MIN(AL_SensQ2),"—")', '=IF(ISNUMBER(IF_AllocQ2),MAX(AL_SensQ2),"—")', "%",
        "Alloc G 節：一次動一個輸入的最小與最大 Q2",
        "研發 GW × 訓練世代持有成本 ÷（同＋Σ 各世代服務 GW × 各世代持有成本）；雲端與自有的差異留在下游",
        "k、N_refresh、每則提示 token 數、服務世代組合", "每則提示 token 數（Assumed，A10）", "IF_AllocQ2", "Alloc 第 D 節；Interface F 節",
        "雲端租用與自有的成本差異在下游（A5）")
    ans(3, "研發占整體成本 Q3（算力部分）", A, "=AL_RDCost", '=IF(ISNUMBER(AL_RDCost),MIN(AL_SensCost),"—")',
        '=IF(ISNUMBER(AL_RDCost),MAX(AL_SensCost),"—")', "$B/年",
        "Alloc G 節：一次動一個輸入的研發算力成本最小與最大值",
        "D 欄＝研發 GW × 訓練世代每 GW 年經濟持有成本（算力部分）；整體成本需加非算力成本",
        "k、N_major、N_refresh", "計畫規模 k：Assumed（A3）", "AL_RDCost", "Alloc 第 C 節",
        "未能回答：非算力成本（人事、資料、評測、非 GPU 費用）不在第 0 層，歸 OpenAI 模型 v0.6")
    ans(4, "各層級每 M token 成本（VR200；本列為 Sol decode 含思考，Luna、Astra 在另兩列）",
        "VR200；經濟口徑、100% 利用率、SLO 下；decode（含思考）",
        "=L1_CostDec_Sol_VR200", "=L1_CostDec_Sol_VR200_Lo", "=L1_CostDec_Sol_VR200_Hi", "$/M", COST_RNG,
        f"本列為 Sol；Luna 見 L1 第 {at['CostDec_Luna_VR200']} 列（L1_CostDec_Luna_VR200）、Astra 見第 {at['CostDec_Astra_VR200']} 列（L1_CostDec_Astra_VR200）。"
        "新鮮輸入與快取輸入見 IF_CostPre_*、IF_CostCache_*",
        "η_d、每層延遲、SLO、生產折減", "生產折減 1.0：Assumed（K11）；VR200 η_d：Analogy", "L1_CostDec_Sol_VR200", f"L1 第 {at['CostDec_Sol_VR200']} 列",
        "VR200 無實測，η_d 沿用 GB300；本題只連結既有 L1 列，未新增計算")
    ans(5, "每 GW 理論營收（Sol，VR200）", "OpenAI 有效單價、基準成本、基準利用率；單一層級滿載的上限",
        "=L1_RevGW_Sol_VR200", "=L1_RevGW_Sol_VR200_Lo", "=L1_RevGW_Sol_VR200_Hi", "$B/GW/年", UTIL_RNG,
        "連結 L1_RevGW_*（Luna、Sol、Astra、機隊各一列）；毛利率見 L1_Ans5_GM、L1_Ans5_FullMargin；全成本 $/M 見 IF_FullCost_*",
        "利用率、折扣、快取命中 χ、單價快照",
        "利用率 60%：Assumed（K11）", "IF_RevGW_Sol", f"L1 第 {at['RevGW_Sol_VR200']} 列；Interface D 節", DASH)
    ans(6, "後訓練占比（FLOPs 口徑；Sol；訓練世代＝IF_TrainGenDefault）", "單一模型最終訓練；Block 3 基準",
        "=INDEX(IF_PostShareFLOP_Sol,1,AL_TrainCol)", "=INDEX(IF_PostShareFLOP_Sol,1,AL_TrainCol)", "=INDEX(IF_PostShareFLOP_Sol,1,AL_TrainCol)", "%",
        "無區間",
        "GPU 小時口徑見 L1_Ans6_GPUh；RL 以推論型運算計價，兩種口徑的後訓練占比不同；Luna、Astra 見 IF_PostShare*_Luna／_Astra",
        "RL rollout token（J9）、rollout 效率、RL trainer MFU", "rollout token：Assumed（J9 校準值）", "IF_PostShareFLOP_Sol", "Interface C 節",
        "本題只連結既有名稱")
    ans(7, "OpenAI 單價 ÷ 前緣單價（Sol；參考請求混合）", "OpenAI 有效單價 ÷ 前緣有效單價；2026-09／10 快照",
        '=IF(AND(ISNUMBER(IF_PriceRef_Sol),ISNUMBER(IF_FrontRef_Sol)),IF_PriceRef_Sol/IF_FrontRef_Sol,"—")',
        '=IF(AND(ISNUMBER(IF_PriceRef_Sol),ISNUMBER(IF_FrontRef_Sol)),IF_PriceRef_Sol/IF_FrontRef_Sol,"—")',
        '=IF(AND(ISNUMBER(IF_PriceRef_Sol),ISNUMBER(IF_FrontRef_Sol)),IF_PriceRef_Sol/IF_FrontRef_Sol,"—")', "x", "無區間",
        "依定義 ≥ 1（前緣＝能力指數不低於 OpenAI 該層級模型的最便宜模型，集合含 OpenAI 本身，K2 (i)）；＝1 表示 OpenAI 該層級即在前緣上，> 1 表示 OpenAI 高於前緣；兩個單價見 IF_PriceRef_Sol、IF_FrontRef_Sol（$/M）。Luna、Astra 見 IF_PriceRef_*、IF_FrontRef_*",
        "能力指數、中國廠商單價、前緣定義（K2）", "AA 指數：2 級、改版頻繁", "IF_PriceRef_Sol", "Interface D 節",
        "本題只連結既有名稱")
    ans(8, "harness 是否降低每成功任務成本：選定 ÷ 標準（Coding agent，Sol，VR200）",
        "VR200；任務＝Coding agent（長程，第 5 欄）；選定 harness 檔案全採用 對 標準 harness",
        "=INDEX(IF_HarR_Sol,1,5)", "=INDEX(IF_HarR_Sol,1,5)", "=INDEX(IF_HarR_Sol,1,5)", "x", "無區間",
        "< 1 表示 harness 降低每成功任務成本；各任務見 IF_HarR_Sol 各欄、其他層級見 IF_HarR_Luna／_Astra",
        "任務 token、成功率 p、harness 檔案", "harness 成功率：Assumed 或 3 級", "IF_HarR_Sol", "Interface E 節", DASH)
    ans(9, "成功任務成本前緣（p ≥ p_min；Coding agent；VR200）",
        "VR200；任務＝Coding agent（第 5 欄）；層級與 harness 檔案見 IF_FrontSuccVRName",
        "=INDEX(IF_FrontSuccVR,1,5)", "=INDEX(IF_FrontSuccVR,1,5)", "=INDEX(IF_FrontSuccVR,1,5)", "$", "無區間（單一前緣值）",
        "前緣組合名稱見 IF_FrontSuccVRName、成功率見 IF_FrontSuccVRP；『無合格』表示無組合達 p_min", "p_min、任務成功率、單價",
        "p_min 50%：Assumed", "IF_FrontSuccVR", "Interface E 節", "任務欄（目前取 Coding agent）未由工作單指定；其他任務見 IF_FrontSuccVR 各欄")
    out.append(("ExtServeGW", "服務 GW：token 路線 對 支出路線", "OpenAI 2025；token 路線＝需求 D ÷ 每 GW 產能；支出路線＝推論支出 ÷ 持有成本",
                "=IF_AllocServeGW", "=IF_AllocServeGW", "=IF_AllocServeGW", "GW", "無區間（單一對照值）",
                "兩路線差距指出需求 D、每 GW 產能或支出口徑之一偏離；對照列落在 ±20% 外是預期結果之一，不調整輸入",
                "每則提示 token 數、服務世代組合、每 GW 產能", "每則提示 token 數（Assumed，A10）", SPEND_SID,
                "=AL_ServeGWSpend", "=AL_ServeGWSpend", "IF_AllocServeGW", "Alloc F 節",
                "支出路線以經濟持有成本換算 GW，與外部揭露的 GW 口徑（D1）無關"))
    out.append(("ExtFreeShare", f"免費服務算力占比：token 路線 對 支出口徑（SRC_DEM_005 ÷ {SPEND_SID}）", "OpenAI 2025",
                "=AL_FreeServeShare", "=AL_FreeServeShare", "=AL_FreeServeShare", "%", "無區間（單一對照值）",
                "token 路線＝免費服務 GW ÷ 服務 GW；支出口徑＝免費推論支出 ÷ 推論支出", "免費占比、層級組合（Cap_In）", "免費用戶占比：Assumed",
                f"SRC_DEM_005；{SPEND_SID}", f"=SRC_DEM_005/{SPEND_SID}", f"=SRC_DEM_005/{SPEND_SID}", "AL_FreeServeShare", "Alloc F 節", "兩口徑不同（算力 vs 支出）；v5.29 分母改連 SRC_DEM_018（Azure 計價），與分子 json 口徑是否一致待 Project 判斷"))
    out.append(("ExtDaily", "每日 token 合計 對 Epoch 估計（SRC_DEM_013 低、高）", "OpenAI 2025；API＋ChatGPT", "=AL_DDaily", "=AL_DDaily", "=AL_DDaily", "T tok/日",
                "無區間（單一對照值）", "基準約 11.5T，只略高於 Epoch 下限 10T；每則 token 數與 API 比例同取低端時約 7.7T，落在區間外（預期，不是錯誤）",
                "每則提示 token 數、API 全年平均比例", "每則提示 token 數（Assumed，A10）", "SRC_DEM_013", "=SRC_DEM_013_Lo", "=SRC_DEM_013_Hi",
                "AL_DDaily", "Alloc A、F 節", "Epoch 為由算力推估的區間"))
    # ---- v5.16 (U1, U2, U4): gross margin (two caliber rows) and the GPU-hour share; columns 10／11／12 = VR200 low／base／high cost
    fc = lambda c: f"INDEX(IF_FullCost_Sol,1,{c})"; ab = lambda c: f"INDEX(IF_AmortBU_Sol,1,{c})"; fd = lambda c: f"INDEX(IF_FullCostDefault_Sol,1,{c})"
    def gm_formula(c):                 # 毛利口徑：服務＋快取儲存，不含訓練攤提＝IF_FullCost − IF_AmortBU
        return (f'=IF(AND(ISNUMBER(IF_PriceRef_Sol),ISNUMBER({fc(c)}),ISNUMBER({ab(c)})),1-({fc(c)}-{ab(c)})/IF_PriceRef_Sol,"{DASH}")')
    def fm_formula(c):                 # 全成本口徑：含 K6 預設攤提
        return (f'=IF(AND(ISNUMBER(IF_PriceRef_Sol),ISNUMBER({fd(c)})),1-{fd(c)}/IF_PriceRef_Sol,"{DASH}")')
    cond = "OpenAI 有效單價；VR200；Sol；基準利用率；SLO 下單一層級滿載（理想上限）"
    rdef = "成本角落情境（高成本／低成本欄；毛利率隨成本反向）"
    out.append(("Ans5_GM", "問 5：理論毛利率（毛利口徑：服務＋快取儲存，不含訓練攤提；Sol，VR200）", cond,
                gm_formula(11), gm_formula(12), gm_formula(10), "%", rdef,
                "1 −（IF_FullCost_Sol − IF_AmortBU_Sol）÷ IF_PriceRef_Sol：推論算力計入營業成本、訓練計入研發（不含攤提）。理論毛利率是 SLO 下單一層級滿載、基準利用率的上限；"
                "與 2025 隱含值約 36% 的差距，與「兩路線差約 15 倍」同源（物理產能上限 對 實際營運），屬預期，不調整輸入。E＝高成本欄、F＝低成本欄",
                "機架價格、IT 折舊年限、WACC、利用率、單價快照", "利用率 60%：Assumed（K11）", f"{SPEND_SID}；SRC_DEM_007",
                f"=1-{SPEND_SID}/SRC_DEM_007", f"=1-{SPEND_SID}/SRC_DEM_007", "L1_Ans5_GM", "Interface D 節（IF_FullCost_Sol、IF_AmortBU_Sol、IF_PriceRef_Sol）",
                "外部為 2025 推論毛利隱含值＝1 − 推論支出 ÷ 營收（Derived；兩者皆 Interested-party），與本列的物理上限口徑不同"))
    out.append(("Ans5_FullMargin", "問 5：理論毛利率（全成本口徑：含 K6 預設訓練攤提；Sol，VR200）", cond,
                fm_formula(11), fm_formula(12), fm_formula(10), "%", rdef,
                "1 − IF_FullCostDefault_Sol ÷ IF_PriceRef_Sol：含 K6 預設攤提（自下而上總額 × 權重）的全成本口徑，為第二列。E＝高成本欄、F＝低成本欄",
                "機架價格、IT 折舊年限、WACC、利用率、訓練攤提（K6）", "利用率 60%：Assumed（K11）", DASH, None, None,
                "L1_Ans5_FullMargin", "Interface D 節（IF_FullCostDefault_Sol、IF_PriceRef_Sol）", DASH))
    out.append(("Ans6_GPUh", "問 6：後訓練占比（GPU 小時口徑；Sol；訓練世代＝IF_TrainGenDefault）", "單一模型最終訓練；Block 3 基準",
                "=INDEX(IF_PostShareGPUh_Sol,1,AL_TrainCol)", "=INDEX(IF_PostShareGPUh_Sol,1,AL_TrainCol)", "=INDEX(IF_PostShareGPUh_Sol,1,AL_TrainCol)", "%",
                "無區間", "FLOPs 口徑見 L1_Ans6；Luna、Astra 見 IF_PostShareGPUh_Luna／_Astra",
                "RL rollout token（J9）、rollout 效率、RL trainer MFU", "rollout token：Assumed（J9 校準值）", DASH, None, None,
                "IF_PostShareGPUh_Sol", "Interface C 節", DASH))
    return out

# v5.36 (work order docs/workorders/20261015_v5.36.md r0): token-denominator closure — the inference spend of the spend route moves to the OpenAI side
# (SRC_DEM_004 8.4, range 7.5–8.8; SRC_DEM_073 audited cost of revenue 7.5), the pricing multiple is lowered (Alloc_In 2.0 -> 1.3, range 1.0–1.6), the request-shape
# correction κ replaces the ISL 4K reading in the gap decomposition, and the gap decomposition is corrected (effective prompt multiple, utilisation, identity).
# (chat-side judgements J25–J27 = Decisions X45–X47; Andy 2026-10-15 07:37, 14:19, 14:25.)
#   B1 Alloc F: AL_ServeGWSpend = SRC_DEM_004 / Σ(share × hold); new display row for the Microsoft-side figure (SRC_DEM_018); Cap_In H10 2025 spend = SRC_DEM_004;
#      SRC_DEM_004 low 7.5 / high 8.8 and notes (guarded); SRC_DEM_073 (audited FY2025 cost of revenue).
#   B2 Alloc_In pricing multiple 2.0 -> 1.3 (1.5–3.0 -> 1.0–1.6) with the new label (guarded value writes; label moved with SNAP_MOVES).
#   B3 no change (Alloc_In C15 stays 4,000; range 2,000–11,000).
#   B4 Alloc_In κ (AL_Kappa／_Lo／_Hi); Cap_In H7 row 109 and H10 row 218 multiply by κ; L1_GapISL = 1 ÷ κ; the ISL 4K reading is kept as a Cap_In comparison row.
#   B5 L1_GapPrompt = effective multiple (token-route serving GW at τ ÷ at 2,000; closed form in Cap_In J), L1_GapUtil = IF_Util ÷ AL_UtilActual, L1_GapProduct external
#      column = L1_ScaleServe2000; Cap_In J rows for the gap identity and its check (Checks M5, INFO).
#   B6 L1_PriceRealFleet／PriceRealDemand／PriceReqBE／PriceRho (display only), Cap_In J price rows (blue inputs).
#   B7 DB_Evidence E344–E365, Decisions X45–X47, README.
# Placement note (engineering, no numeric effect): the work order puts the two identity rows in Cap_In H9; to avoid moving every H10／I-section cell that Gov_Map
# registers by address, the new Cap_In rows are appended as section J after the I section (same columns as H).
# Every write to an Excel-owned cell is guarded (ID absent ／ text not yet appended ／ cell still at its v5.35 value), like v518–v535.
from copy import copy
from openpyxl.utils import get_column_letter as L
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY
import v518
import v529
import v533
import v534
import v535

VERSION = "20261015_Tokenomics_v5.36"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-15"
V = "v5.36"
DASH = "—"
SLO = "SLO 不可達"
WO = "工作單 v5.36 r0"
ANDY_0737 = "Andy 2026-10-15 07:37「'下一版建議：v5.36 處理「token 分母閉合」':同意」"
ANDY_1419 = "Andy 2026-10-15 14:19「早上我跟Copilot討論過，我們更傾向84億。但如你所說，請先在追一下一手來源，再來決定」"
ANDY_1425 = "Andy 2026-10-15 14:25「我找到的基本與你一致。同意你的建議。」"
ANDY = f"{ANDY_0737}；{ANDY_1419}；{ANDY_1425}（文字，未改字）；可撤回"
SPEND_SID = "SRC_DEM_004"                 # OpenAI-side inference spend (spend route from v5.36)
MS_SID = "SRC_DEM_018"                    # Microsoft-side Azure inference (comparison row only from v5.36)
_NN = [f"N{i:02d}" for i in range(1, 18)] + ["S1", "S2", "S3", "S4", "ORCL"]
EV = {n: f"E{344 + i}" for i, n in enumerate(_NN)}          # N01–N17 -> E344–E360; S1–S4 -> E361–E364; Oracle -> E365 (next free number after E343)


def S(n): return f"SRC_DEM_{n:03d}"


# ================================================================== B1: SRC_Demand SRC_DEM_073 (next free number at v5.35: 073) and SRC_DEM_004 / 018 updates
SRC_NEW = [
    dict(id=S(73), sheet="SRC_Demand", metric="OpenAI 2025 營業成本（查核財報）", val=7.5, lo=None, hi=None, unit="$B",
         basis="年度；經會計師查核之 2025 財務報表的營業成本（含所有供應商）；其中付 Microsoft 6.047；研發 191.8 中付 Microsoft 10.59；付 Microsoft 合計 17.2",
         applies="OpenAI", date="2026-06-16", src="Zitron 取得之查核財報，FT 獨立核實（2026-06-16）；TechFlow、Quartz／Yahoo 轉述", grade=2,
         stance="中立", stance_note="查核報表（外流，FT 獨立核實）；公司自身數字但經會計師查核，OpenAI 未評論", hand="二手（外流查核報表）",
         status="Active", ev=EV["S3"], s="U-V536", use="Alloc F 節推論支出的 Lo 端對照（SRC_DEM_004 低端 7.5）；v5.36A 補充第 2 節交叉核對",
         note=f"v5.36 新增（{EV['S3']}）：OpenAI 端推論支出的最接近一手來源；營業成本 7.5 含所有供應商（非 Microsoft 部分僅 1.45），與 SRC_DEM_004（8.4）同量級；"
              f"{WO} B1"),
]
SRC_LAST_ID = SRC_NEW[-1]["id"]


def src_new_records():
    return SRC_NEW


_N004_W = (f" ｜v5.36 B1：Lo＝OpenAI 2025 查核財報營業成本 75 億（含所有供應商；付 Microsoft 60.47 億；{S(73)}）；Hi＝投資人文件調整後毛利率 33% 換算 13.07×0.67＝8.76（約 8.8）；"
           f"v5.36 起本筆為支出路線的推論支出（Alloc C61、Cap_In H10 2025 欄）；Microsoft 端 {MS_SID} 12.6 改為對照列（{WO} B1；{EV['S1']}、{EV['S2']}、{EV['S3']}）")
_N004_V = " ｜v5.36：Alloc!F 節（AL_ServeGWSpend，支出路線服務 GW）；Cap_In H10 2025 欄推論支出"
_N018_W = (f" ｜v5.36 B1：維持 Active，改為對照列、不進機隊路線（Alloc F 節對照列「Microsoft 端 Azure 推論」）；Microsoft 稱為推論的 126 億中約一半未進 OpenAI 營業成本"
           f"（付 Microsoft 營業成本 60.47 億，{S(73)}），最可能是研究用推論列在研發（v5.36A 補充第 2 節）；Microsoft 向 FT 表示數字「不太正確」（{EV['N07']}）")
SRC_UPD = {
    SPEND_SID: ("SRC_Demand", {"D": (None, 7.5), "E": (None, 8.8), "W": ("+", _N004_W), "V": ("+", _N004_V)}),
    MS_SID: ("SRC_Demand", {"W": ("+", _N018_W)}),
}


def src_update(wb):
    n = 0; log = []
    for sid, (sh, fields) in SRC_UPD.items():
        ws = wb[sh]
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row is None: log.append(f"{sid}: record not found"); continue
        for col, spec in fields.items():
            cell = ws[f"{col}{row}"]
            if v518._apply(cell, spec):
                n += 1
                if col in ("D", "E"): cell.font = copy(F_IN)
            else: log.append(f"{sid}!{col}: kept (already applied)")
    return n, log


# ================================================================== B2: Alloc_In pricing multiple (value writes guarded), label, B4 κ row
LAB_SPEND_OLD = "推論支出計價 ÷ 持有成本（v5.29 X14 (m)）"
LAB_SPEND = "推論支出 ÷ 持有成本（計價倍數；含供應商利潤與資本回收）"
SNAP_MOVES = [(("Alloc_In", (LAB_SPEND_OLD, 0), c), ("Alloc_In", (LAB_SPEND, 0), c)) for c in (3, 4, 5)]      # build.py: the Excel values follow the label
LAB_KAPPA = "請求形狀修正 κ（實際流量每 GPU 秒總 token ÷ 參考請求）"
KAPPA = (LAB_KAPPA, "x", 1.0, 0.65, 1.2, "Derived",
         "v5.36 B4（X47）：以 Sens_Perf 第 93、94 列校準 prefill／decode 成本，代入實際輸入輸出比與快取命中（API 6,000／400、ChatGPT 3,500／800 等），各類流量按 GW 加權 κ＝1.035（全 χ 0.55 為 0.976、API χ 0.9 為 1.17、DeepSeek 型推理 0.66）；"
         "基準 1.0、區間 0.65–1.2（v5.36A 第 3.2 節；驗證：同公式算 ISL 4K 得 0.4336＝1 ÷ 2.3065）。取代 L1_GapISL 的 ISL 4K 讀法；乘入有效服務 GW（Cap_In 第 109、218 列）；"
         "注意：此處 token 為總 token（含快取輸入）")


def alloc_in_kappa(wb):
    """Appended after the existing Alloc_In content (nothing moves): AL_Kappa／_Lo／_Hi."""
    ws = wb["Alloc_In"]
    r = v529._last_row(ws) + 1
    lab, unit, base, lo, hi, tag, note = KAPPA
    put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
    put(ws, f"C{r}", base, F_IN, fmt="0.00", fill=FILL_KEY); put(ws, f"D{r}", lo, F_IN, fmt="0.00"); put(ws, f"E{r}", hi, F_IN, fmt="0.00")
    put(ws, f"F{r}", tag); put(ws, f"G{r}", note, F_NOTE, wrap=True)
    v529._nm(wb, "AL_Kappa", f"Alloc_In!$C${r}"); v529._nm(wb, "AL_Kappa_Lo", f"Alloc_In!$D${r}"); v529._nm(wb, "AL_Kappa_Hi", f"Alloc_In!$E${r}")
    return r


def inputs_update(wb):
    """Alloc_In pricing multiple 2 -> 1.3, low 1.5 -> 1.0, high 3.0 -> 1.6 (each only while the cell still holds the v5.35 value)."""
    ws = wb["Alloc_In"]; log = []
    r = v529._row_by_label(ws, LAB_SPEND)
    for col, old, new in (("C", 2, 1.3), ("D", 1.5, 1.0), ("E", 3, 1.6)):
        c = ws[f"{col}{r}"]
        if c.value == old:
            c.value = new; log.append(f"Alloc_In!{col}{r}: {old} -> {new} (v5.36 B2)")
    return log


# ================================================================== spec patches (applied in place before v533／v534 write their rows)
_PATCHED = False
LAB_GW = "支出路線服務 GW（經計價倍數與請求形狀修正）＝AL_ServeGWSpend ÷ AL_SpendBasis × AL_Kappa"
LAB_SPEND_H10 = "推論支出（$B；OpenAI 端；2025＝SRC_DEM_004、2026＝SRC_DEM_070）"
LAB_GW_H10 = "支出路線服務 GW ÷ 計價倍數 × 利用率修正 × κ＝推論支出 ÷ 持有成本 ÷ AL_SpendBasis × AL_UtilActual ÷ IF_Util × AL_Kappa"


def patch_specs():
    """v5.36 B1／B4: Cap_In H7 row gw_az (÷ SpendBasis × κ; D (token-high end, SpendBasis_Lo) takes κ_Hi, E takes κ_Lo) and H10 rows q_spend (2025 = SRC_DEM_004), q_gw (× κ)."""
    global _PATCHED
    if _PATCHED: return
    sp = v533.SPEC
    i = next(i for i, it in enumerate(sp) if it[0] == "gw_az")
    t = sp[i]
    sp[i] = ("gw_az", LAB_GW, t[2], "=AL_ServeGWSpend/AL_SpendBasis*AL_Kappa", "=AL_ServeGWSpend/AL_SpendBasis_Lo*AL_Kappa_Hi", "=AL_ServeGWSpend/AL_SpendBasis_Hi*AL_Kappa_Lo", t[6],
             f"Alloc 第 61 列（{SPEND_SID} ÷ 世代組合持有成本；v5.36 起 OpenAI 端 8.4）÷ Alloc_In 計價倍數（1.3；D 欄取低端 1.0＝GW 取高、E 欄取高端 1.6）× 請求形狀修正 κ（1.0；D 欄取高端 1.2、E 欄取低端 0.65，與 token 取高／取低同向）")
    sp = v534.SPEC_H10
    for k, it in enumerate(sp):
        if it[0] is None and "推論支出 2025＝SRC_DEM_018" in it[1]:
            sp[k] = (None, it[1].replace("推論支出 2025＝SRC_DEM_018", f"推論支出 2025＝{SPEND_SID}（v5.36 起 OpenAI 端）"))
    j = next(i for i, it in enumerate(sp) if it[0] == "q_spend")
    t = sp[j]
    sp[j] = ("q_spend", LAB_SPEND_H10, t[2], f"={SPEND_SID}", t[4], t[5], t[6], t[7], f"2025＝{SPEND_SID} 8.4（v5.36 起 OpenAI 端；v5.35 為 Microsoft 端 {MS_SID} 12.6）；2026＝SRC_DEM_070 14.1（Alt，預測值）")
    j = next(i for i, it in enumerate(sp) if it[0] == "q_gw")
    t = sp[j]
    sp[j] = ("q_gw", LAB_GW_H10, t[2], *v534._h10_cols("={c}{q_spend}/{c}{q_hold}/AL_SpendBasis*AL_UtilActual/IF_Util*AL_Kappa"), t[7],
             "2025 欄＝H9 (i) 有效服務 GW 0.4030（v5.35 為 0.3929）；2026 欄 ×0.65 於計價倍數 2.0 → 1.3")
    _PATCHED = True


# ================================================================== Cap_In J section (after I; the reading row is cleared and rewritten after it)
FMT = {"$B": "#,##0.000", "%": "0.0%", "x": "0.000", "GW": "0.0000", "$/M": "#,##0.0000", "月": "0"}
TIERS_NOTE = "牌價等級 3（G0-7），待一手確認"
_GW_TAU = ('=IF(AND(ISNUMBER(AL_BlendPaid),ISNUMBER(AL_BlendFree)),AL_DAPI/AL_BlendPaid+{tau}*SRC_DEM_012*1000000000*365/1000000*((1-AL_FreeShare)/AL_BlendPaid+AL_FreeShare/AL_BlendFree),"' + SLO + '")')
_ISL = lambda w: f'=IF(ISNUMBER(Sens_Perf!${w}$98),IF(Sens_Perf!${w}$98>0,INDEX(IF_TokGW_Sol,1,11)/Sens_Perf!${w}$98,"{SLO}"),"{SLO}")'
_IDENT = lambda sb, ua, kp: (f'=IF(AND(ISNUMBER(L1_ScaleServe),ISNUMBER({sb}),ISNUMBER({ua}),ISNUMBER({kp})),L1_ScaleServe/({sb}*IF_Util/({ua}*{kp})),"{SLO}")')
_DIFF = lambda c: f'=IF(AND(ISNUMBER({c}{{j_ident}}),ISNUMBER({c}{{res}})),{c}{{j_ident}}-1/{c}{{res}},"{SLO}")'
# (key, label, unit, C, D, E, tag, note); key None = sub-header. In the κ／ISL／τ rows D＝low end and E＝high end as in L1; in the identity rows the columns are those of H7／H9 (D＝m low end).
SPEC_J = [
    (None, f"J. v5.36 補列（{WO} B4／B5／B6；工作單把缺口恆等式兩列置於 H9，為不移動 H10／I 節已登錄 Gov_Map 的 Cap_In 儲存格，本版附於本節）。欄位：C 基準、D／E 依各列說明（τ 與 κ 列＝L1 低／高；恆等式列＝H 節 D 欄 m 低端、E 欄 m 高端）"),
    ("j_kappa", "請求形狀修正 κ（Alloc_In；AL_Kappa）　→ L1_GapISL＝1 ÷ κ", "x", "=AL_Kappa", "=AL_Kappa_Lo", "=AL_Kappa_Hi", "Derived（連結 Alloc_In）",
     "基準 1.0、區間 0.65–1.2；Cap_In 第 109、218 列乘入有效服務 GW"),
    ("j_isl4k", "對照：ISL 4K 讀法（v5.35 以前的 L1_GapISL；Sens_Perf W98／Y98）；v5.36 起不進落差分解", "x", _ISL("W"), _ISL("Y"), _ISL("W"), "Derived（對照）",
     "固定輸出 2K 下縮短輸入到 4K 的讀法 2.3065（C）、64K 端 0.5182（D）；改用實際輸入輸出比後消失（κ 取代，v5.36A 第 3.2 節）"),
    (None, "J-1. 落差分解 1 的閉式（B5.1）：token 路線服務 GW 隨每則提示 token 數 τ 變動——GW(τ)＝AL_DAPI ÷ 付費產能 ＋ τ × SRC_DEM_012 × 365 ×［(1 − 免費占比) ÷ 付費產能 ＋ 免費占比 ÷ 免費產能］（Alloc 第 5–11、24–28 列同式）"),
    ("j_tau", "τ：C＝Alloc_In 每則提示 token 數（AL_TokPerPrompt）、D＝低端（_Lo）、E＝高端（_Hi）", "tok", "=AL_TokPerPrompt", "=AL_TokPerPrompt_Lo", "=AL_TokPerPrompt_Hi", "Assumed（連結）", "區間 2,000–11,000"),
    ("j_gw", "token 路線服務 GW（τ 同上列）", "GW", _GW_TAU.replace("{tau}", "C{j_tau}"), _GW_TAU.replace("{tau}", "D{j_tau}"), _GW_TAU.replace("{tau}", "E{j_tau}"), "Derived",
     "基準欄＝AL_ServeGW（0.1826）"),
    ("j_gw2000", "token 路線服務 GW（τ＝CST_TokPerPromptV528＝2,000）", "GW", _GW_TAU.replace("{tau}", "CST_TokPerPromptV528"), _GW_TAU.replace("{tau}", "CST_TokPerPromptV528"),
     _GW_TAU.replace("{tau}", "CST_TokPerPromptV528"), "Derived", "v5.28 基準 2,000；0.1403"),
    ("j_prompt", "落差分解 1＝有效倍數：GW(τ) ÷ GW(2,000)　→ L1_GapPrompt", "x", '=IF(AND(ISNUMBER(C{j_gw}),ISNUMBER(C{j_gw2000})),C{j_gw}/C{j_gw2000},"' + SLO + '")',
     '=IF(AND(ISNUMBER(D{j_gw}),ISNUMBER(D{j_gw2000})),D{j_gw}/D{j_gw2000},"' + SLO + '")', '=IF(AND(ISNUMBER(E{j_gw}),ISNUMBER(E{j_gw2000})),E{j_gw}/E{j_gw2000},"' + SLO + '")',
     "Derived", "基準 1.3013（API 不隨 τ 變，故小於 τ 比值 2.0）；v5.35 為 τ 比值 2.0（把 τ 的 2.0 算了兩次，v5.36A 第 3.1 節）"),
    ("j_selfchk", "自我檢查：基準欄 GW(τ) 對 AL_ServeGW 的相對差（應為 0；容差 1e-9）", "x", '=IF(AND(ISNUMBER(C{j_gw}),ISNUMBER(AL_ServeGW)),ABS(C{j_gw}/AL_ServeGW-1),"' + SLO + '")', DASH, DASH, "Derived", "閉式與 Alloc 逐列推導一致"),
    ("j_scale2000", "ScaleServe（τ＝2,000）＝AL_ServeGWSpend ÷ GW(2,000)　→ L1_ScaleServe2000", "x",
     '=IF(AND(ISNUMBER(C{j_gw2000}),ISNUMBER(AL_ServeGWSpend)),AL_ServeGWSpend/C{j_gw2000},"' + SLO + '")', "=C{j_scale2000}", "=C{j_scale2000}", "Derived",
     "6.401；L1_GapProduct 的外部對照（τ＝2,000 基準）；L1_ScaleServe（τ＝Alloc_In C15）4.919"),
    (None, "J-2. 缺口恆等式（B5.4）：ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））＝1 ÷ 第 174 列（需求 ÷ 機隊的倒數）；驗算差須為 0（基準欄；D／E 欄的需求 token 隨 τ 區間端點改變，恆等式只在基準欄成立）"),
    ("j_ident", "缺口恆等式：L1_ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））", "x", _IDENT("AL_SpendBasis", "AL_UtilActual", "AL_Kappa"),
     DASH, DASH, "Derived",
     "基準 2.207＝1 ÷ 閉合比 0.4531（v5.35 為 2.152）；只算基準欄：H 節 D／E 欄的需求 token 隨 τ 區間端點改變，ScaleServe 以基準 τ 計，D／E 欄不成立"),
    ("j_diff", "驗算差：恆等式 − 1 ÷ 第 174 列（須為 0；容差 1e-9；Checks M5）", "x", _DIFF("C"), DASH, DASH, "Derived", "Info 檢查 M5（基準欄）"),
    (None, "J-3. 價格時間錯配 ρ（B6；顯示用，不進任何計算）：ρ＝2025 中階牌價（時間加權）÷ 2026-09 快照 Sol。單價為參考請求（16K 入／2K 出／χ 0.55）的未折扣單價（$/M），來源 v5.36A 第 3.3 節；C＝單價、D＝2025 年在線月數"),
    ("j_p4o", "2025 中階牌價：GPT-4o（C＝參考請求單價 $/M；D＝2025 年在線月數）", "$/M", 2.722, 7, DASH, "Derived（輸入；牌價等級 3）", TIERS_NOTE + "；7 月（2025-01～07，GPT-5 發布前）"),
    ("j_p5", "2025 中階牌價：GPT-5（C＝參考請求單價 $/M；D＝2025 年在線月數）", "$/M", 1.672, 4, DASH, "Derived（輸入；牌價等級 3）", TIERS_NOTE + "；4 月（2025-08～11）"),
    ("j_p52", "2025 中階牌價：GPT-5.2（C＝參考請求單價 $/M；D＝2025 年在線月數）", "$/M", 2.341, 1, DASH, "Derived（輸入；牌價等級 3）", TIERS_NOTE + "；1 月（2025-12）"),
    ("j_psol", "2026-09 快照 Sol 參考請求單價（未折扣）＝IF_PriceRef_Sol ÷ (1 − B4_Disc)", "$/M", "=IF_PriceRef_Sol/(1-B4_Disc)", DASH, DASH, "Derived（公式）",
     "2.009＝1.6071 ÷ 0.8（折扣 B4_Disc 兩邊約掉）；v5.36A 第 3.3 節"),
    ("j_p2025", "2025 中階牌價（時間加權）", "$/M", "=(C{j_p4o}*D{j_p4o}+C{j_p5}*D{j_p5}+C{j_p52}*D{j_p52})/(D{j_p4o}+D{j_p5}+D{j_p52})", DASH, DASH, "Derived", "2.340"),
    ("j_rho", "價格時間錯配 ρ＝2025 中階牌價（時間加權）÷ 快照 Sol　→ L1_PriceRho（D＝下限：三者最低 ÷ Sol；E＝上限：三者最高 ÷ Sol）", "x",
     "=C{j_p2025}/C{j_psol}", "=MIN(C{j_p4o},C{j_p5},C{j_p52})/C{j_psol}", "=MAX(C{j_p4o},C{j_p5},C{j_p52})/C{j_psol}", "Derived",
     "基準 1.165（區間 0.83–1.36；下限 GPT-5、上限 GPT-4o）；實收單價（美元）本身是 2025 營收 ÷ 2025 token 的觀測，不受 ρ 影響；ρ 只改變「m 是定價打折」或「牌價下降」的解讀（v5.36A 第 3.3 節）"),
]
BLUE_J = {("j_p4o", "C"), ("j_p4o", "D"), ("j_p5", "C"), ("j_p5", "D"), ("j_p52", "C"), ("j_p52", "D")}
KEY_FILL = {"j_prompt", "j_ident", "j_rho"}
NOTE_V536 = (" ｜v5.36 補充：(9) 推論支出改 OpenAI 端 8.4（SRC_DEM_004；區間 7.5–8.8）、計價倍數 2.0 → 1.3（1.0–1.6）、新增 κ（1.0；0.65–1.2）：AL_ServeGWSpend 1.3471 → 0.8981、"
             "有效服務 GW（第 109 列）0.6736 → 0.6909、閉合比（第 174 列）0.4647 → 0.4531、τ* 13,950 → 14,426、m_fleet 0.8098 → 0.7896、m 下限 0.5558 → 0.5419；"
             "H10 2025 欄 m_fleet ×0.975、2026 欄 ×0.65（計價倍數）。J 節：缺口恆等式與驗算差、落差分解 1 的閉式、價格時間錯配 ρ 的輸入列。")
ROWS = {}


def cap_in_j(wb, h35):
    """Rows start where v5.35 wrote the reading row (h35['end']); that row is cleared and rewritten after J (no defined name there)."""
    ws = wb["Cap_In"]
    r0 = h35["end"]
    assert str(ws[f"A{r0}"].value).startswith("讀法") and ws.max_row == r0, (r0, ws.max_row)
    ws[f"A{r0}"].value = None
    r = r0
    for item in SPEC_J:
        if item[0] is not None: ROWS[item[0]] = r
        r += 1
    ctx = dict(ROWS); ctx["res"] = v534.ROWS["res_fleet"]      # H9 residual row (demand ÷ fleet; row 174)
    assert ws[f"A{ctx['res']}"].value.startswith("殘差：需求 ÷ 機隊（點估計）"), ws[f"A{ctx['res']}"].value
    r = r0
    for item in SPEC_J:
        if item[0] is None:
            put(ws, f"A{r}", item[1], F_BOLD); r += 1; continue
        key, lab, unit, c, d, e, tag, note = item
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        fmt = FMT.get(unit) or ("#,##0" if unit == "tok" else None)
        for col, v in (("C", c), ("D", d), ("E", e)):
            if isinstance(v, str) and v.startswith("="):
                put(ws, f"{col}{r}", v.format(**ctx), F_CALC, fmt=fmt, fill=FILL_KEY if key in KEY_FILL and col == "C" else None)
            elif isinstance(v, (int, float)) and type(v) is not bool:
                put(ws, f"{col}{r}", v, F_IN if (key, col) in BLUE_J else F_CALC, fmt=("0" if col == "D" and key in ("j_p4o", "j_p5", "j_p52") else fmt))
            else:
                put(ws, f"{col}{r}", v, F_CALC)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True)
        r += 1
    put(ws, f"A{r}", v533.NOTE_END + v534.NOTE_V534 + v535.NOTE_V535 + NOTE_V536, F_NOTE)
    return dict(start=r0, rows=dict(ROWS), end=r)


# ================================================================== Checks M5 (INFO; appended after M4, counted in GOV_Info)
def checks_m5(wb):
    ws = wb["Checks"]
    r4 = next(r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value == "M4")
    assert ws[f"A{r4 + 1}"].value is None
    r = r4 + 1; j = ROWS["j_diff"]
    f = f'=IF(ISNUMBER(Cap_In!$C${j}),IF(ABS(Cap_In!$C${j})>0.000000001,1,0),0)'
    put(ws, f"A{r}", "M5"); put(ws, f"B{r}", "缺口恆等式驗算差（Cap_In J 節：ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））− 1 ÷ 第 174 列）（基準欄）絕對值 > 1e-9：1＝恆等式不成立", wrap=True)
    put(ws, f"C{r}", "INFO"); put(ws, f"D{r}", f, F_CALC, fmt="0")
    put(ws, f"E{r}", f"Cap_In J 節第 {j} 列（基準欄 C）；現值 0（v5.36 B5.4）", F_NOTE)
    ref = wb.defined_names["GOV_Info"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "INFO 合計（含 K4–K7、M5）"
    return r


# ================================================================== B5／B6: L1 — patches of existing rows (gap decomposition) and new rows (appended last)
READ_GAP = ("v5.36 落差分解改正（X47）：1 有效倍數（GW(τ) ÷ GW(2,000)，API 不隨 τ 變）× 2 計價倍數 × 3 請求形狀（1 ÷ κ）× 4 利用率（IF_Util ÷ 實際利用率）；"
            "對 τ＝2,000 基準的 ScaleServe（L1_ScaleServe2000）解釋一部分，其餘＝缺口恆等式的剩餘 1 ÷ 閉合比（Cap_In J 節）。")


def l1_patch(R):
    out = []
    for row in R:
        key = row[0]
        row = list(row)
        if key == "GapPrompt":
            row[1] = "落差分解 1：每則提示 token 數的有效倍數（token 路線服務 GW：τ＝Alloc_In C15 ÷ τ＝v5.28 基準 2,000；v5.36 B5 取代 τ 比值）"
            row[2] = "Cap_In J 節閉式（Alloc 第 5–11、24–28 列同式）；X47"
            row[3], row[4], row[5] = (f"=Cap_In!${c}${ROWS['j_prompt']}" for c in "CDE")
            row[7] = "區間端點 τ 的有效倍數（τ 2,000 → 1.0；τ 11,000 → 2.36）"
            row[8] = "基準 1.3013（v5.35 的 τ 比值 2.0 把 τ 的 2.0 算了兩次；API token 不隨 τ 變）。" + READ_GAP + "外部欄仍為 OpenRouter 每請求 6,400 ÷ 2,000＝3.2（τ 比值口徑，非有效倍數）"
        elif key == "GapSpendBasis":
            row[2] = "Alloc_In 計價倍數（Assumed）；X46"
            row[7] = "1.0–1.6（Assumed）"
            row[8] = ("基準 1.3；v5.36 B2（X46）：Oracle 出租 Nvidia 伺服器毛利率略低於 14%（The Information 引 Oracle 內部文件；二手）→ 價格 ÷ 成本約 1.16，未含資本成本；"
                      "Microsoft 對 OpenAI 的計價未找到，高端保留 1.6；無外部對照（已搜尋，未找到 OpenAI 對 Azure 實付單價；E262）")
            row[10] = "本列：Assumed（E262；X46）"
        elif key == "GapISL":
            row[1] = "落差分解 3：請求形狀（1 ÷ κ；v5.36 起取代 ISL 4K 讀法）"
            row[2] = "Alloc_In 請求形狀修正 κ（Derived）；X47；原 ISL 4K 讀法見 Cap_In J 節對照列"
            row[3], row[4], row[5] = "=1/AL_Kappa", "=1/AL_Kappa_Hi", "=1/AL_Kappa_Lo"
            row[7] = "低＝1 ÷ κ 高端（1.2）、高＝1 ÷ κ 低端（0.65）"
            row[8] = ("基準 1.0（κ＝1.0；0.65–1.2）：實際流量輸出占比低（API 6%）→ 每 GPU 秒的總 token 反而較參考請求多，ISL 4K 讀法（2.3065，固定輸出 2K）改用實際輸入輸出比後消失（v5.36A 第 3.2 節）；"
                      "token 為總 token（含快取輸入）")
            row[9] = "請求形狀（輸入輸出比、快取命中）"
            row[10] = "κ：Derived（Sens_Perf 第 93、94 列校準）"
            row[14] = "AL_Kappa"
            row[15] = "Alloc_In 請求形狀修正 κ 列；Cap_In J 節"
        elif key == "GapUtil":
            row[1] = "落差分解 4：利用率（IF_Util ÷ 實際利用率；與機隊路線 Cap_In 第 114 列一致，不再乘 CTL_ProdDerate）"
            row[2] = "Alloc_In 新輸入（Assumed）；X47"
            row[3], row[4], row[5] = "=IF_Util/AL_UtilActual", "=IF_Util/AL_UtilActual_Hi", "=IF_Util/AL_UtilActual_Lo"
            row[8] = "基準 1.7143（0.6 ÷ 0.35）；v5.35 為 1.4571（誤乘 CTL_ProdDerate 0.85，與機隊路線的 IF_Util ÷ 實際利用率 不一致）"
            row[10] = "IF_Util：Assumed（K11）；實際利用率 × 生產折減：Assumed"
        elif key == "GapProduct":
            row[1] = "落差分解乘積：四項口徑差之積（對照 L1_ScaleServe2000＝τ 2,000 基準的支出 ÷ token 路線服務 GW）"
            row[8] = "區間涵蓋外部對照即表示落差可由四項口徑差解釋（Checks K7，仍比對 L1_ScaleServe）；v5.36 乘積 2.90 對 τ＝2,000 的 6.40 解釋 45%，其餘＝缺口恆等式剩餘（Cap_In J 節）"
            row[11] = "L1_ScaleServe2000"
            row[12], row[13] = "=L1_ScaleServe2000", "=L1_ScaleServe2000"
            row[14] = "L1_ScaleServe2000"
        out.append(tuple(row))
    return out


READ_PRICE = ("價格口徑（B6；顯示用，不進任何計算）：實收單價＝m × Cap_In 第 90 列（混合有效單價）；機隊口徑用 L1_MFleet、需求口徑用 L1_MImplied；回本所需實收單價＝L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate）× 單價 ÷ L_total。"
              "判讀：機隊實收 ≥ 回本所需 → 回本。")


def l1_rows_new():
    R = ROWS
    c90 = "Cap_In!$C$90"
    none = ("無外部對照", DASH, DASH)
    TXT = "m 非數字（本情境）"
    px = lambda m: f'=IF(ISNUMBER({m}),{m}*{c90},"{TXT}")'          # m is text when a generation in the mix cannot serve (SLO), like L1_LReqFleet
    req = lambda lt: f'=IF(AND(ISNUMBER(L1_FleetBreakeven),ISNUMBER({lt})),L1_FleetBreakeven/(IF_Util*CTL_ProdDerate)*{c90}/{lt},"{TXT}")'
    return [
        ("ScaleServe2000", "服務端規模係數（τ＝2,000 基準）：支出路線服務 GW ÷ token 路線服務 GW（τ＝CST_TokPerPromptV528）", "Decision Use＝下游校準用，不得當產能；X47",
         f"=Cap_In!$C${R['j_scale2000']}", f"=Cap_In!$D${R['j_scale2000']}", f"=Cap_In!$E${R['j_scale2000']}", "x", "無區間（τ 固定 2,000；支出路線不隨 τ 變）",
         "L1_GapProduct 的外部對照；與 L1_ScaleServe（τ＝Alloc_In C15）的差＝GapPrompt 有效倍數 1.3013", "每則提示 token 數（2,000 固定）、推論支出口徑、世代組合", "推論支出：二手（SRC_DEM_004／073）",
         "SRC_DEM_004（分子）", None, None, "AL_ServeGWSpend", f"Cap_In 第 {R['j_scale2000']} 列", "本列本身即對照（分子為外部值），外部欄不另填"),
        ("PriceRealFleet", "實收單價（機隊口徑，2025）＝L1_MFleet × 混合有效單價", "OpenAI 2025；m_fleet × Cap_In 第 90 列；v5.36 B6",
         px("L1_MFleet"), px("L1_MFleet_Lo"), px("L1_MFleet_Hi"), "$/M", "低／高＝L1_MFleet 低／高 × 單價", READ_PRICE,
         "機隊 m、混合有效單價", "L1_MFleet：Assumed 分母（計價倍數、實際利用率、κ）", *none, "L1_MFleet", "L1 本頁；Cap_In 第 90 列", "顯示用"),
        ("PriceRealDemand", "實收單價（需求口徑，2025）＝L1_MImplied × 混合有效單價", "OpenAI 2025；m_整體 × Cap_In 第 90 列；v5.36 B6",
         px("L1_MImplied"), px("L1_MImplied_Lo"), px("L1_MImplied_Hi"), "$/M", "低／高＝L1_MImplied 低／高 × 單價", READ_PRICE,
         "需求路線 m、混合有效單價", "分母為模型 token 需求（Assumed）；已知偏低（L1_ScaleServe）", *none, "L1_MImplied", "L1 本頁；Cap_In 第 90 列", "顯示用"),
        ("PriceReqBE", "回本所需實收單價（L＝L1_LTotal）", "L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate）× 混合有效單價 ÷ L_total；v5.36 B6",
         req("L1_LTotal"), req("L1_LTotal_Hi"), req("L1_LTotal_Lo"), "$/M", "低＝L 取高端（0.498）、高＝L 取低端（1.692）", READ_PRICE,
         "機隊回本門檻、利用率、生產折減、L_total", "L_total：Assumed（g、T1、ρ）", "機隊實收單價（L1_PriceRealFleet）", "=L1_PriceRealFleet", "=L1_PriceRealFleet",
         "L1_FleetBreakeven；L1_LTotal；L1_PriceRealFleet", "L1 本頁；Cap_In 第 90 列", "顯示用；與 L1_LReqFleet（所需 L）等價的美元口徑"),
        ("PriceRho", "價格時間錯配 ρ＝2025 中階牌價（時間加權）÷ 2026-09 快照 Sol", "參考請求（16K 入／2K 出／χ 0.55）未折扣單價；v5.36A 第 3.3 節；v5.36 B6",
         f"=Cap_In!$C${R['j_rho']}", f"=Cap_In!$D${R['j_rho']}", f"=Cap_In!$E${R['j_rho']}", "x", "區間 0.83–1.36：下限 GPT-5、上限 GPT-4o（Cap_In J 節）",
         "實收單價（美元）本身是 2025 營收 ÷ 2025 token 的觀測，不受 ρ 影響；ρ 只改變「m 是定價打折」或「牌價下降」的解讀（顯示用，不進 m）。對 ScaleServe 的貢獻＝0（v5.36A 第 3.1 節第 5 點）",
         "2025 中階牌價序列、快照 Sol", "牌價等級 3（G0-7），待一手確認", *none, "IF_PriceRef_Sol", f"Cap_In 第 {R['j_rho']} 列", "層級對映無法由價格決定（情境 3 不採）"),
    ]


def l1_judge(wb):
    """L1 P column of L1_PriceReqBE: mechanical reading (fleet real price >= required price -> payback)."""
    ws = wb["L1"]
    r = int(wb.defined_names["L1_PriceReqBE"].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == "L1_PriceReqBE", (r, ws[f"A{r}"].value)
    ws[f"P{r}"].value = (f'=IF(AND(ISNUMBER(D{r}),ISNUMBER(M{r})),IF(M{r}>=D{r},"回本：機隊實收 "&TEXT(M{r},"0.00")&" ≥ 所需 "&TEXT(D{r},"0.00")&" $/M",'
                         f'"未回本：機隊實收 "&TEXT(M{r},"0.00")&" < 所需 "&TEXT(D{r},"0.00")&" $/M"),"推算值非數字（本情境）")')
    return r


# ================================================================== B7: Gov_Map rows for the new blue cells, range text of the pricing multiple (guarded)
GM_SPEND_RTEXT_OLD = "1.5–3.0（chat 端提案，Andy 2026-10-08「依建議」）"
GM_SPEND_RTEXT = f"1.0–1.6（v5.36：基準 2.0 → 1.3；chat 端提案，{ANDY_1425}）"
GM_SPEND_TAIL = (f" ｜v5.36 B2（X46）：基準 2.0 → 1.3、區間 1.5–3.0 → 1.0–1.6。依據：Oracle 出租 Nvidia 伺服器毛利率略低於 14%（The Information 引 Oracle 內部文件；二手，{EV['ORCL']}）→ 價格 ÷ 成本約 1.16（1 ÷ (1 − 0.14)），"
                 f"毛利率成本含折舊與營運、不含資本成本，故此倍數為早期 Blackwell 的上限讀法；Microsoft 對 OpenAI 的計價未找到，高端保留 1.6；{WO}")


def _gm_row(ws, sheet, cell):
    rows = [r for r in range(5, ws.max_row + 1) if (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sheet, cell)]
    assert len(rows) == 1, (sheet, cell, rows)
    return rows[0]


def gov_update(ws, append_text):
    n = 0
    r = _gm_row(ws, "Alloc_In", "C23"); assert ws[f"A{r}"].value == "GM596", ws[f"A{r}"].value
    if ws[f"M{r}"].value == GM_SPEND_RTEXT_OLD: ws[f"M{r}"].value = GM_SPEND_RTEXT; n += 1
    if ws[f"E{r}"].value == LAB_SPEND_OLD: ws[f"E{r}"].value = LAB_SPEND; n += 1
    n += append_text(ws[f"N{r}"], GM_SPEND_TAIL)
    r = _gm_row(ws, "Alloc_In", "D23:E23"); assert ws[f"A{r}"].value == "GM597", ws[f"A{r}"].value
    if ws[f"E{r}"].value == LAB_SPEND_OLD: ws[f"E{r}"].value = LAB_SPEND; n += 1
    n += append_text(ws[f"N{r}"], GM_SPEND_TAIL)
    return n


def gov_map_rows(wb):
    if not ROWS: return []
    out = []
    ai = wb["Alloc_In"]; cap = wb["Cap_In"]
    rk = v529._row_by_label(ai, LAB_KAPPA)
    sc = "切片三（v5.36 κ）"
    reason = (f"v5.36 B4（X47）：請求形狀修正 κ Derived 1.0（0.65–1.2）；依 Sens_Perf 第 93、94 列校準 prefill／decode 成本代入實際輸入輸出比與快取命中，GW 加權 1.035；"
              f"驗證：同公式算 ISL 4K 得 0.4336＝1 ÷ L1_GapISL(v5.35)；乘入 Cap_In 第 109、218 列的有效服務 GW（κ＝1 時數值不變），L1_GapISL＝1 ÷ κ（{EV['N13']}）")
    out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'C{rk}', 'label': LAB_KAPPA, 'check': LAB_KAPPA, 'cls': 'Derived', 'role': '基準', 'src': '', 'rel': '',
                'dec': 'X47', 'lo': f'=Alloc_In!D{rk}', 'hi': f'=Alloc_In!E{rk}', 'rtext': '0.65–1.2（v5.36A 第 3.2 節：API χ 0.9 為 1.17、DeepSeek 型推理 0.66）', 'reason': reason, 'retag': '', 'seg': '中'})
    out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'D{rk}:E{rk}', 'label': LAB_KAPPA, 'check': LAB_KAPPA, 'cls': 'Derived', 'role': '低／高', 'src': '', 'rel': '',
                'dec': 'X47', 'lo': None, 'hi': None, 'rtext': f'C{rk} 的低、高端點', 'reason': reason, 'retag': '', 'seg': '—'})
    sc = "切片三（v5.36 價格時間錯配）"
    for key, nm_, mo in (("j_p4o", "GPT-4o", "7 月（2025-01～07）"), ("j_p5", "GPT-5", "4 月（2025-08～11）"), ("j_p52", "GPT-5.2", "1 月（2025-12）")):
        r = ROWS[key]; lab = cap[f"A{r}"].value
        rs = (f"v5.36 B6（X47）：{nm_} 參考請求（16K 入／2K 出／χ 0.55）未折扣單價（Derived，牌價等級 3，待一手確認；快取價為假設）與 2025 年在線月數 {mo}；"
              f"只進 Cap_In J 節 ρ 與 L1_PriceRho，顯示用，不進任何計算（{EV['N14']}、{EV['N15']}）")
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '單值', 'src': '', 'rel': '', 'dec': 'X47',
                    'lo': cap[f'C{r}'].value, 'hi': cap[f'C{r}'].value, 'rtext': '單值（牌價序列，等級 3；ρ 區間由三者最低／最高決定）', 'reason': rs, 'retag': '', 'seg': '無'})
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'D{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '單值', 'src': '', 'rel': '', 'dec': 'X47',
                    'lo': cap[f'D{r}'].value, 'hi': cap[f'D{r}'].value, 'rtext': f'單值（{mo}）', 'reason': rs, 'retag': '', 'seg': '無'})
    return out


# ================================================================== B7: DB_Evidence E344–E365 (17 columns A..Q; layout of v531–v535)
def _ev(n, claim, src, tag, param, cur, new, verdict, note, sids, affected, grade, stance):
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, f"{note}｜暫編 {n}｜{ANDY}｜讀取者：chat 端（{WO} B7）", "已處理", sids, DASH, affected, grade, stance]


AFF = "Alloc_In 計價倍數／κ；Alloc F 節 AL_ServeGWSpend；L1_ScaleServe／L1_Gap*／L1_MFleet 等（見 Decisions X45–X47）"
EVIDENCE_V536 = [
    _ev("N01", "OpenAI 與 Anthropic 在 2026-10-12 後無新 token／訊息數揭露（已搜尋，未找到）", "v5.36A 第 2.1 節", "缺口紀錄", "v5.32 第 4 節新揭露規則", DASH, DASH, "登錄（缺口紀錄）", "已搜尋，未找到 ≠ 不存在", DASH, DASH, DASH, "中立"),
    _ev("N02", "Google 每月處理 3.2e15 token（2026-05），一年前 4.8e14", "https://blog.google/innovation-and-ai/sundar-pichai-io-2026/", "Interested-party（Google）", "Alloc 第 12 列對照（補強 D180）", DASH, "3.2e15／月",
        "登錄 DB_Evidence；補強既有紀錄", "Google 自述", DASH, DASH, "2", "利害關係方"),
    _ev("N03", "Oracle AI 雲端（Nvidia 出租）毛利率 14%（2025-06～08 季）", "Sherbrooke Record 2025-10-07（二手轉述 The Information）", "Interested-party（二手）；等級 3", "Alloc_In 計價倍數（C23）", "2.0", "1.3（上限讀法 1.16）",
        "登錄，等級 3；與 Oracle 毛利率一筆（補充檔 Sherwood）互證", "二手轉述", DASH, "Alloc_In 計價倍數；L1_GapSpendBasis", "3", "利害關係方"),
    _ev("N04", "CoreWeave 2026 Q2 調整後營業利益率 5%、EBITDA 率 59%、活躍 1.5 GW", "MarketBeat 2026-08-11（二手摘要）", "Interested-party；等級 3", "Alloc_In 計價倍數（C23）對照", DASH, DASH, "登錄，等級 3", "二手摘要", DASH, DASH, "3", "利害關係方"),
    _ev("N05", "OpenAI–Oracle 3,000 億美元／5 年／2027 起／約 4.5–5 GW（≈每 GW 年 12–13.3B）", "The Register 2025-09-11 引 WSJ", "Interested-party（匿名）", "Alloc_In 計價倍數（C23）對照", DASH, "12–13.3 $B／GW／年",
        "登錄；GW 口徑未明", "GW 口徑（IT／設施）未明", DASH, DASH, "3", "利害關係方"),
    _ev("N06", "H100 租價指數 2025：超大雲 6.2–9.0、neocloud 3.0–3.5、市集 1.9–2.5 $/GPU-hr", "Silicon Data 部落格", "Interested-party（賣指數）；等級 3", "Alloc_In 計價倍數（C23）；L1_GPUhr_Hopper", DASH, DASH, "登錄，等級 3", "賣指數者", DASH, DASH, "3", "利害關係方"),
    _ev("N07", "OpenAI 2025 前三季 Azure 推論支出 8.7B；Microsoft 稱數字不準；抵用金可能未反映；不含其他供應商", "The Register 2025-11-12", "Interested-party（洩漏）", MS_SID, "12.6（全年推估）", "12.6（對照列）",
        f"補註（既有紀錄附加爭議）：{MS_SID} v5.36 起為對照列，不進機隊路線", "文件未公開；Microsoft 向 FT 表示不太正確", MS_SID, "Alloc F 節對照列", "2", "利害關係方"),
    _ev("N08", "OpenAI 計算毛利（paying）：2024 年底 52%、2025-10 約 70%", "Fortune／Bloomberg 2025-12-21；SaaStr 2025-12-24", "Interested-party（洩漏的內部指標）；等級 3", "SRC_DEM_004／005 交叉檢查", DASH, "70%",
        f"登錄，等級 3；與補充檔算力毛利 70%（{EV['S4']}）為同一主張", "OpenAI 方；未證實", DASH, DASH, "3", "利害關係方"),
    _ev("N09", "DeepSeek：日均 226.75／尖峰 278 節點（0.816）；快取命中 56.3%；輸入 608B：輸出 168B／日", "DeepSeek open-infra-index（2025-02-27）", "Verified（一手）；對 OpenAI 為 Analogy", "Alloc_In C24；Cap_In B4_CacheHit", DASH, DASH,
        "登錄", "對 OpenAI 為類比", DASH, DASH, "1", "中立"),
    _ev("N10", "無伺服器平台一年追蹤：輸入 35.8 T：輸出 2.5 T（14.3：1）；99% 重用在 15 分鐘內", "arXiv 2608.13573", "Analogy", "Sens_Perf ISL／OSL；κ", DASH, "14.3：1", "登錄", "類比", DASH, DASH, "3", "第三方"),
    _ev("N11", "OpenRouter 代理型流量快取 87–90%（2026-09），2026-01 約 60%", "OpenRouter Inferred 03（2026-10-08）", "Analogy（2026 現象）；等級 3", "Cap_In B4_CacheHit 對照", DASH, "87–90%", "登錄，等級 3（只登 DB_Evidence）", "2026 現象，非 2025 基準", DASH, DASH, "3", "第三方"),
    _ev("N12", "OpenAI 內部 Codex 占輸出 token 99.8%（2026-06）；2025-08 前 <10%", "OpenAI「How agents are transforming work」", "Interested-party；等級 3", "2025 流量結構判讀", DASH, "99.8%（2026-06）", "登錄，等級 3（只登 DB_Evidence）", "OpenAI 自述", DASH, DASH, "3", "利害關係方"),
    _ev("N13", "請求形狀修正 κ（基準 1.0；0.65–1.2）：Sens_Perf 第 93、94 列校準，實際流量 GW 加權 1.035；ISL 4K 重現值 0.4336＝1 ÷ 2.3065", "v5.36A 第 3.2 節（chat 端 Derived）", "Derived", "Alloc_In κ；L1_GapISL", "L1_GapISL 2.3065", "κ 1.0（L1_GapISL 1.0）",
        "採用（X47）：L1_GapISL 改為 1 ÷ κ；ISL 4K 讀法保留於 Cap_In J 節對照列", "token 為總 token（含快取輸入）；計費等值 token 需另算", DASH, "Alloc_In κ；L1_GapISL；Cap_In 第 109、218 列", DASH, "中立"),
    _ev("N14", "價格時間錯配 ρ：中階 1.165（0.83–1.36）；中階＋低階 1.22（0.82–1.47）", "v5.36A 第 3.3 節（Derived；牌價取自 benchlm 2026-10-14）", "Derived", "新顯示列 L1_PriceRho", DASH, "1.165（0.83–1.36）",
        "採用（X47）：只採情境 1（全用中階）；顯示用，不進 m", "牌價等級 3；快取價為假設；層級對映無法由價格決定", DASH, "L1_PriceRho；Cap_In J 節", DASH, "中立"),
    _ev("N15", "OpenAI 牌價序列（4o／4.1／o3／GPT-5／5.2／mini／nano／o1／o3-pro）補全", "https://benchlm.ai/openai/api-pricing（2026-10-14）", "Analogy（二手彙整，等級 3）", "補強 E338／E340；Cap_In J 節 ρ 輸入", DASH, "序列",
        "登錄；快取價為假設，註明", "二手彙整", DASH, "L1_PriceRho", "3", "第三方"),
    _ev("N16", "A5：Batch／Flex 占比與企業折扣——三輪搜尋仍未找到", "v5.36A 第 2.5 節", "缺口紀錄", "B4_Disc", "0.2", DASH, "登錄（缺口紀錄，只登 DB_Evidence）", "已搜尋，未找到 ≠ 不存在", DASH, DASH, DASH, "中立"),
    _ev("N17", "缺口恆等式：缺口＝L1_ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））；v5.35 為 2.152＝7.378 ÷（2.0 × 1.714）；GapPrompt 重複計入（有效 1.30）", "v5.36A 第 3.1 節（Derived）", "Derived", "L1_ScaleServe；L1_GapProduct", "2.152", "見 Cap_In J 節",
        "採用（X47）：Cap_In J 節恆等式與驗算差（Checks M5）", "僅登 DB_Evidence 與 Derived 紀錄", DASH, "L1_GapPrompt；L1_GapUtil；L1_GapProduct；L1_ScaleServe2000", DASH, "中立"),
    _ev("S1", "Azure 推論 2025 Q1 20.75、Q2 29.47、Q3 36.48 億美元，前三季 86.7 億；2024 全年 37.7 億；全年外推 126 億（SRC_DEM_018）", "Where's Your Ed At《OpenAI documents》https://www.wheresyoured.at/oai_docs/（Microsoft 內部財務文件；FT 看過）",
        "Interested-party（Zitron 長期主張 AI 泡沫；Microsoft 稱不太正確；可能含抵用金；不含 CoreWeave、Google 等其他供應商）", MS_SID, "12.6（支出路線）", "12.6（對照列）",
        "採用（X45）：Microsoft 端 126 億改為對照列；其中約一半未進 OpenAI 營業成本，最可能是研究用推論列在研發", "文件本身未公開；二手轉述", MS_SID, "Alloc F 節對照列；L1_Ans1–Ans3（待 Project 判斷）", "2", "利害關係方"),
    _ev("S2", "推論成本 2025 年「約四倍」成長、調整後毛利率 33%（2024 年 40%）；2026 推論約 141 億", "OpenAI 給投資人的文件，The Information 報導（2026-02、2026-06 再被引用）；Reuters 無法證實；Control Plane",
        "Interested-party（OpenAI，募資與 IPO 前有呈現較佳毛利的誘因）", f"{SPEND_SID} 高端", "8.4", "Hi 8.8（13.07 × 0.67＝8.76）", f"採用（X45）：{SPEND_SID} Hi 8.8", "二手", SPEND_SID, "AL_ServeGWSpend", "2", "利害關係方"),
    _ev("S3", "OpenAI 2025 經會計師查核財報：營業成本 75 億（其中付 Microsoft 60.47 億）；研發 191.8 億（其中付 Microsoft 105.9 億）；付 Microsoft 合計 172 億", "TechFlow 32082；Quartz／Yahoo（FT 2026-06-16 獨立核實）",
        "查核報表（外流，FT 獨立核實）；OpenAI 未評論", f"{SPEND_SID} 低端", "8.4", "Lo 7.5", f"採用（X45）：{S(73)}；{SPEND_SID} Lo 7.5；推論支出主值 84 億（區間 75–88 億）", "外流報表；營業成本含所有供應商，非 Microsoft 部分僅 14.5 億", f"{S(73)}；{SPEND_SID}",
        "AL_ServeGWSpend；Cap_In H10 2025 欄", "2", "中立"),
    _ev("S4", "付費用戶「算力毛利」70%（2025-10），2024 年底 52%；付費推論約 39 億＋免費 39 億＝約 78 億，落在 75–88 億之間", "Fortune 2025-12-21；The Information（知情人士）",
        "Interested-party（OpenAI 方；未證實）；等級 3", f"{SPEND_SID} 交叉檢查", DASH, "70%", "登錄，等級 3；交叉檢查用，不入 SRC", "二手", DASH, DASH, "3", "利害關係方"),
    _ev("ORCL", "Oracle 出租 Nvidia 伺服器：2025 年 6–8 月毛利率略低於 14%、毛利 1.25 億美元（The Information 引 Oracle 內部文件）；毛利率成本含折舊與營運、不含資本成本，故價格 ÷ 成本上限約 1 ÷ (1 − 0.14)＝1.16",
        "Sherwood（https://sherwood.news/markets/oracle-tumbles-after-report-that-its-lost-nearly-usd100-million-from-renting）；原文（付費）未讀到，兩則二手轉述一致", "Interested-party（二手）；等級 3",
        "Alloc_In 計價倍數（C23）", "2.0", "1.3（區間 1.0–1.6）", "採用（X46）：計價倍數基準 2.0 → 1.3，區間 1.0–1.6；Microsoft 對 OpenAI 的計價未找到，高端保留 1.6", "早期 Blackwell 情況，部分是時差造成", DASH, "Alloc_In 計價倍數；L1_GapSpendBasis", "3", "利害關係方"),
]


def evidence_rows():
    return EVIDENCE_V536


# ================================================================== B7: Decisions X45–X47 (10 columns; layout of v531–v535)
_X = [
    ("X45", "B1 推論支出改用 OpenAI 端", f"支出路線的推論支出由 Microsoft 端 {MS_SID}（12.6）改為 OpenAI 端 {SPEND_SID}（8.4；低 7.5＝查核財報營業成本 {S(73)}、高 8.8＝投資人文件調整後毛利率 33% 換算）。"
     f"理由：OpenAI 端三個來源（查核報表營業成本 75 億、投資人文件毛利率換算 88 億、算力毛利 70% 換算約 78 億）互相一致；Microsoft 端 126 億有一半無法對應到 OpenAI 的營業成本，最可能是研究用推論列在研發。"
     f"改動：Alloc C61（AL_ServeGWSpend）＝{SPEND_SID} ÷ Σ（世代占比 × 持有成本）；新增對照列「Microsoft 端 Azure 推論」；Cap_In 第 216 列 2025 欄＝{SPEND_SID}；{MS_SID} 維持 Active 為對照列。"
     f"原話：{ANDY_1419}；{ANDY_1425}", "Alloc F 節；Cap_In H10；SRC_DEM_004／018／073；L1_ScaleServe；L1_MFleet 等", "B1"),
    ("X46", "B2 計價倍數下修", "Alloc_In 計價倍數基準 2.0 → 1.3，區間 1.5–3.0 → 1.0–1.6（Gov_Map GM596／597）。依據：Oracle 出租 Nvidia 伺服器毛利率略低於 14%（The Information 引 Oracle 內部文件；二手）→ 價格 ÷ 成本約 1.16，未含資本成本；"
     f"Microsoft 對 OpenAI 計價未找到，高端保留 1.6。標籤改為「{LAB_SPEND}」。原話：{ANDY_1425}", "Alloc_In 計價倍數；Gov_Map GM596／597；L1_GapSpendBasis", "B2"),
    ("X47", "B4 κ 與 B5 落差分解改正", "(1) Alloc_In 新增請求形狀修正 κ（基準 1.0；0.65–1.2；Derived），乘入有效服務 GW（Cap_In 第 109、218 列）；L1_GapISL＝1 ÷ κ，ISL 4K 讀法移到 Cap_In J 節對照列；"
     "(2) L1_GapPrompt 改為有效倍數（GW(τ) ÷ GW(2,000)，基準 1.3013）；L1_GapUtil＝IF_Util ÷ AL_UtilActual（不再乘 CTL_ProdDerate，1.7143）；L1_GapProduct 外部欄改對照 L1_ScaleServe2000；"
     "(3) Cap_In J 節缺口恆等式與驗算差（Checks M5，INFO）；(4) B6 顯示列 L1_PriceRealFleet／PriceRealDemand／PriceReqBE／PriceRho。"
     f"原話：{ANDY_0737}；{ANDY_1425}", "Alloc_In κ；Cap_In 第 109、218 列與 J 節；L1_Gap*；L1_ScaleServe2000；L1_Price*；Checks M5", "B4、B5、B6"),
]
DECISIONS_V536 = [[i, V, f"{i} {t}", txt, DATE, f"{ANDY}；chat 端建議，可撤回", "v5.36 已建", where, f"{WO} {sec}", "否"] for i, t, txt, where, sec in _X]


# ================================================================== README (version string is built from VERSION; v5.35 text is kept after it)
README_VERSION = (VERSION + "（判斷類，工作單 docs/workorders/20261015_v5.36.md r0：token 分母閉合——推論支出改 OpenAI 端 SRC_DEM_004 8.4（區間 7.5–8.8；SRC_DEM_073 查核財報營業成本 7.5），"
                  "Microsoft 端 SRC_DEM_018 12.6 改為對照列；計價倍數 2.0 → 1.3（1.0–1.6）；新增請求形狀修正 κ（1.0；0.65–1.2）取代 GapISL；落差分解改正（GapPrompt 有效倍數 1.3013、GapUtil 1.7143）"
                  "與缺口恆等式（Cap_In J 節、Checks M5）；L1 新增 L1_ScaleServe2000、L1_PriceRealFleet／PriceRealDemand／PriceReqBE／PriceRho；DB_Evidence E344–E365、Decisions X45–X47；"
                  "AL_ServeGWSpend 1.3471 → 0.8981、L1_ScaleServe 7.378 → 4.919、L1_MFleet 0.8098 → 0.7896；全部 IF_ 不變）。以下為 " + v535.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v535.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v535.VERSION.split("_")[-1]):]
README_ROW = ("token 分母閉合（v5.36）",
              f"支出路線推論支出改 OpenAI 端：Alloc C61＝{SPEND_SID}（8.4；7.5–8.8）÷ Σ（世代占比 × 持有成本）＝0.8981 GW；Microsoft 端 {MS_SID}（12.6）為對照列（約一半未進 OpenAI 營業成本，最可能是研究用推論列在研發）。"
              "計價倍數（Alloc_In）2.0 → 1.3（1.0–1.6）；請求形狀修正 κ（1.0；0.65–1.2）乘入有效服務 GW（Cap_In 第 109、218 列）。"
              "落差分解：GapPrompt＝有效倍數 GW(τ) ÷ GW(2,000)（1.3013）、GapSpendBasis 1.3、GapISL＝1 ÷ κ（1.0）、GapUtil＝IF_Util ÷ 實際利用率（1.7143）；L1_ScaleServe2000＝6.401。"
              "Cap_In J 節：缺口恆等式 ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））＝1 ÷ 第 174 列，驗算差須為 0（Checks M5，INFO）；價格時間錯配 ρ 的輸入列（顯示用）。"
              "L1 顯示列：實收單價（機隊 1.548、需求 3.417 $/M）、回本所需實收單價 0.9007 $/M（L 0.342 → 1.692、1.162 → 0.498）、ρ 1.165（0.83–1.36）。")

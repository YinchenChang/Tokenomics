# v21.12 (= v22.0 segment B2「結構二」; design docs/plan/20261105_v22.0_Terra第四層級_設計.md, section 6.1 row B2; branch claude/v22-b2).
# Module name v21120 (= v21.12.0): builder/v2112*.py would read as v21.1.x (same rule as v21100／v21110).
# Andy's authorization (2026-11-05): 「完整第四層級」; the J1–J15 recommendations of the design are adopted as defaults (「照建議」).
#
# STRUCTURAL version: every existing value stays the same because the Terra paid／free mix shares are 0 and the Terra family-R&D switch is 0.
# No IF_／IFW_／L1_／RNG_／CAP_Px25_ Terra name is created (v22.0 B3). What changes:
#   S1  Cap_In rows 5–8／21–24／30–32: Terra in F (prices 1.00／0.05／5.00, life 9 (4–18), mixes 0); 標記／說明 F／G -> G／H on these rows only (J2 (a));
#       B4_PriceIn／_PriceCache／_PriceOut／_Life／_MixPaid／_MixFree, B4_ISL／_OSL (Serving), B5_H50／_Lo／_Hi (Har_In) become 1×4.
#       F section: row 59 = GPT-6.1 Terra candidate, capability index blank (J7 (b)); note 59 -> 60.
#   S2  Cap_In R section (below Q; nothing above moves): B4_MixPaid25／B4_MixFree25 (2025 tier mix, Terra 0, = the v21.11 values; J5), B4_TerraFam
#       (Terra in the 2026 family R&D, 0 = not counted; J9), CAP_TokGWPaidMix25 (2025-basis paid capacity per GW, same formula as IF_TokGWPaidMix on
#       B4_MixPaid25; read by Cap_In row 333 -> L1_TokPaid_GW25).
#   S3  Price_Frontier: Terra column (A: H–K mixed, L–O qualified, P–S China-qualified; B–D: F); thresholds through a tier → candidate-row map (R6);
#       a tier with no qualifying candidate falls back to its own OpenAI model (R7).
#   S4  Cache_Store／Fleet_1GW／Amortize Terra blocks (block4); Theory_Rev／Harness／Sens_Har Terra blocks (terra_late, below every existing row).
#       Four-term sums: Fleet_1GW Σ／weight sums／closure／family R&D (COUNT 4, Terra × B4_TerraFam); Amortize K6 totals (Terra BU × B4_TerraFam);
#       Theory_Rev fleet revenue (OpenAI and front); Interface J IFW_RevGWFleetFront_Prod; Cap_In row 90; Checks Block 4 fleet closure row.
#   S5  2025 basis (J5): Alloc B／I／K sections read B4_MixPaid25／B4_MixFree25; CAP_Price25Mix (Cap_In 281); Cap_In 333 reads CAP_TokGWPaidMix25;
#       Alloc K row 153 (AL_RevGW25) = paid share × 2025-mix paid capacity × 2025 price (v21.11: IF_RevGWFleet × 2025 price ÷ 2026 price; equal when
#       the two mixes are equal).
#   S6  Checks Z3: four-tier mix sums = 1 (2026 paid, 2026 free, 2025 paid, 2025 free); ERROR, counted in GOV_Errors.
#   S7  Version files: README B5／A1, Load_Bearing!C3, Decisions SL69-01; 用途 marks 「預備」 on the Terra blocks (R8).
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

from common import put, section, F_IN, F_CALC, F_NOTE, F_BOLD, FILL_KEY
import tiers
import v1410
import v21110

VERSION = "20261105_Tokenomics_v21.12"      # single source of the version string: README!B5 and README!A1 (finish.readme); Load_Bearing!C3 (load_bearing_date)
DATE = "2026-11-05"
DASH = "—"
V = "v21.12"
DESIGN = v21110.DESIGN
WO = f"v22.0 B2 段（結構二）：設計文件 {DESIGN} 第 6.1 節 B2 列（chat 端派工）"
DEC_ID = "SL69-01"
DEC_BY = v21110.DEC_BY.replace("本段（B1）為結構變更", "本段（B2）為結構變更（Terra 付費組合＝0、家族研發計入開關＝0）")
PREP = tiers.PREP_B2
NA = '"SLO 不可達"'
TK, TL = tiers.TERRA_KEY, tiers.TERRA_LAB
TT = tiers.TERRA


def _nm(wb, n, ref):
    if n in wb.defined_names:
        del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


# ---------------------------------------------------------------- S2 Cap_In R section
CAP_R0 = 350
MIX25 = {"paid": (0.40, 0.45, 0.15, 0.0), "free": (0.90, 0.10, 0.0, 0.0)}      # = Cap_In C31:E32 of v21.10／v21.11 (J5: 逐字等於 v21.10), Terra 0
GEN_COLS = (2, 5, 8, 11)      # Interface base-cost columns of Hopper, GB200, GB300, VR200 (as Cap_In row 333 and Alloc B)


def cap_in_r(wb, prev):
    ws = wb["Cap_In"]
    assert ws.max_row == CAP_R0 - 2, f"Cap_In ends at row {ws.max_row}; R section expects it to start at row {CAP_R0}"
    r = CAP_R0
    section(ws, r, "R. 2025 口徑層級組合與 Terra 開關（v21.12，v22.0 B2；J5／J9）：Alloc（2025 基準年）、CAP_Price25Mix 與 L1_TokPaid_GW25 讀本節，"
                   "不讀 D 節 2026 組合，使 Terra（2026-10 上市）不進 2025 錨點", 8); r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for c, h in zip("CDEFGH", ("Luna", "Sol", "Astra", "Terra", "標記", "說明")): put(ws, f"{c}{r}", h, F_BOLD)
    r += 1
    K = {}
    for key, lab, vals, note in [
        ("paid", "2025 付費服務 token 層級組合　→ B4_MixPaid25", MIX25["paid"],
         "J5 (a)：2025 校準口徑不含 Terra（Terra＝0）；數值逐字等於 v21.10 的 D 節付費組合（Cap_In C31:E31）。四項合計須為 1（Checks Z3）"),
        ("free", "2025 免費服務 token 層級組合　→ B4_MixFree25", MIX25["free"],
         "J5 (a)：同上，等於 v21.10 的 D 節免費組合（Cap_In C32:E32）；Terra＝0")]:
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", "%")
        for c, v in zip("CDEF", vals): put(ws, f"{c}{r}", v, F_IN, fmt="0%")
        put(ws, f"G{r}", "Decision（J5）", F_NOTE); put(ws, f"H{r}", note, F_NOTE, wrap=True)
        K[key] = r; r += 1
    _nm(wb, "B4_MixPaid25", f"Cap_In!$C${K['paid']}:$F${K['paid']}")
    _nm(wb, "B4_MixFree25", f"Cap_In!$C${K['free']}:$F${K['free']}")
    put(ws, f"A{r}", "Terra 計入 2026 起的家族研發（1＝計入；0＝不計入）　→ B4_TerraFam", wrap=True); put(ws, f"B{r}", "選擇")
    put(ws, f"C{r}", 0, F_IN, fmt="0")
    put(ws, f"G{r}", "Decision（J9）", F_NOTE)
    put(ws, f"H{r}", "J9 (a)：2026 起家族含 Terra（四層）、2025 Alloc 家族三層。v21.12 先設 0（既有值不變）；v22.0 B3 啟用時改 1。"
                     "作用在 Fleet_1GW 第 33 列（家族研發計畫占 1 GW 年）與 Amortize K6 自下而上年化總額的 Terra 項", F_NOTE, wrap=True)
    _nm(wb, "B4_TerraFam", f"Cap_In!$C${r}"); K["fam"] = r; r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for c, g in zip("CDEF", ("Hopper", "GB200", "GB300", "VR200")): put(ws, f"{c}{r}", g, F_BOLD)
    r += 1
    tiers3 = [k for k, _ in tiers.TIERS_ROWS]      # v22.0: 2025 basis stays three-tier (J5)
    for i, c in enumerate("CDEF"):
        k = GEN_COLS[i]
        tg = {t: f"INDEX(IF_TokGW_{t},1,{k})" for t in tiers3}
        mx = {t: f"INDEX(B4_MixPaid25,1,{j})" for j, t in enumerate(tiers3, 1)}
        ok = ",".join([f"ISNUMBER({mx[t]})" for t in tiers3] + [f"ISNUMBER({tg[t]})" for t in tiers3])
        pos = ",".join(f"{tg[t]}>0" for t in tiers3)
        den = "+".join(f"{mx[t]}/{tg[t]}" for t in tiers3)
        put(ws, f"{c}{r}", f"=IF(AND({ok}),IF(AND({pos}),1/({den}),AL_UnavailTxt),AL_UnavailTxt)", F_CALC, fmt="#,##0")
    put(ws, f"A{r}", "2025 口徑層級組合下每 GW 年付費產能（100% 利用、全部付費；B4_MixPaid25 調和平均，三層級；同 IF_TokGWPaidMix 寫法）　→ CAP_TokGWPaidMix25", wrap=True)
    put(ws, f"B{r}", "M tok/GW/年")
    put(ws, f"G{r}", "Derived", F_NOTE)
    put(ws, f"H{r}", "J5：第 333 列（L1_TokPaid_GW25 的 Σ）讀本列，不讀 IF_TokGWPaidMix（2026 組合，v22.0 起含 Terra）。欄＝Interface 基準成本欄第 2、5、8、11 欄；"
                     "2025 組合與 2026 組合相同時兩者逐值相等（v21.12）", F_NOTE, wrap=True)
    _nm(wb, "CAP_TokGWPaidMix25", f"Cap_In!$C${r}:$F${r}"); K["cap25"] = r
    return K


# ---------------------------------------------------------------- S4 late Terra blocks (Theory_Rev, Harness, Sens_Har) and the Checks closure row
def _row15(ws, r, lab, unit, tpl, fmt, key=False):
    from block4 import row15
    row15(ws, r, lab, unit, tpl, fmt, key=key)


def theory_rev_terra(wb, F, A, T):
    ws = wb["Theory_Rev"]
    from block4 import IF as IFX
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    r = r0
    section(ws, r, f"F. {TL}（v21.12 建置；v22.0 啟用：契約名稱 IF_RevGW_Terra、IF_FullCost_Terra 等在 Interface R 節；1 GW 只服務本層級）", 17); r += 1
    t3 = TT - 1
    tg = tiers.terra_src("TokGW", "{X}$6")
    _row15(ws, r, "每 GW 產出（基準利用率；SLO 不可達時為文字）", "M tok/年", f"=IF(ISNUMBER({tg}),{tg}*IF_Util,{tg})", "#,##0"); tok = r; r += 1
    _row15(ws, r, "理論營收 — OpenAI 有效單價（→ IF_RevGW_Terra）", "$B/年", f"=IF(ISNUMBER({{X}}{tok}),{{X}}{tok}*INDEX(B4_EffRef,1,{TT})/1E9,{{X}}{tok})", "#,##0.0", key=True)
    rev = r; r += 1
    _row15(ws, r, "理論營收 — 前緣單價（→ IF_RevGWFront_Terra）", "$B/年", f"=IF(ISNUMBER({{X}}{tok}),{{X}}{tok}*INDEX(B4_FrontRef,1,{TT})/1E9,{{X}}{tok})", "#,##0.0")
    revf = r; r += 1
    _row15(ws, r, "年持有成本 — 經濟（IF_HoldEcon）", "$B/年", f"={IFX('IF_HoldEcon')}", "#,##0.0"); hold = r; r += 1
    _row15(ws, r, "理論營收 ÷ 持有成本", "x", f"=IF(ISNUMBER({{X}}{rev}),{{X}}{rev}/{{X}}{hold},{{X}}{rev})", "0.0", key=True); r += 1
    _row15(ws, r, "前緣營收 ÷ 持有成本", "x", f"=IF(ISNUMBER({{X}}{revf}),{{X}}{revf}/{{X}}{hold},{{X}}{revf})", "0.0"); r += 1
    _row15(ws, r, "服務成本 $/M（參考請求，含快取儲存，基準利用率）", "$/M", f"=Amortize!{{X}}{A[f'sc{t3}']}", "#,##0.0000"); sc = r; r += 1
    g = lambda am: f"=IF(AND(ISNUMBER({{X}}{sc}),ISNUMBER(Amortize!{{X}}{am})),{{X}}{sc}+Amortize!{{X}}{am},{NA})"
    _row15(ws, r, "全成本 $/M（服務＋自下而上攤提；→ IF_FullCost_Terra）", "$/M", g(A[f'bu{t3}']), "#,##0.0000", key=True); fc = r; r += 1
    _row15(ws, r, "全成本 $/M（服務＋由上而下攤提）", "$/M", g(A[f'td{t3}']), "#,##0.0000"); fct = r; r += 1
    _row15(ws, r, "全成本 $/M（服務＋K6 預設 (c) 攤提；→ IF_FullCostDefault_Terra）", "$/M", g(A[f'dc{t3}']), "#,##0.0000", key=True); fcd = r; r += 1
    gm = lambda x, price: f"=IF(ISNUMBER({{X}}{x}),1-{{X}}{x}/INDEX({price},1,{TT}),{NA})"
    _row15(ws, r, "理論毛利率（OpenAI 單價；不含攤提，可與公司揭露毛利率比較）", "%", gm(sc, "B4_EffRef"), "0%"); r += 1
    _row15(ws, r, "理論毛利率（OpenAI 單價；自下而上全成本）", "%", gm(fc, "B4_EffRef"), "0%"); r += 1
    _row15(ws, r, "理論毛利率（OpenAI 單價；由上而下全成本）", "%", gm(fct, "B4_EffRef"), "0%"); r += 1
    _row15(ws, r, "理論毛利率（OpenAI 單價；K6 預設 (c) 全成本）", "%", gm(fcd, "B4_EffRef"), "0%", key=True); gmd = r; r += 1
    _row15(ws, r, "理論毛利率（前緣單價；由上而下全成本）", "%", gm(fct, "B4_FrontRef"), "0%"); r += 1
    ok = f"Fleet_1GW!{{X}}{F['ok']}=1"
    p3 = f"Fleet_1GW!{{X}}{F['p3']}"
    _row15(ws, r, f"機隊付費服務營收 {TL} 貢獻 — OpenAI 有效單價（→ IF_RevGWFleet_Terra；已計入 B 節第 {T['fl']} 列合計）", "$B/年",
           f"=IF(AND({ok},ISNUMBER({p3})),{p3}*INDEX(B4_EffRef,1,{TT})/1E9,{NA})", "#,##0.00"); flt = r; r += 1
    _row15(ws, r, f"機隊付費服務營收 {TL} 貢獻 — 前緣單價（→ IF_RevGWFleetFront_Terra；已計入 B 節第 {T['flf']} 列合計）", "$B/年",
           f"=IF(AND({ok},ISNUMBER({p3})),{p3}*INDEX(B4_FrontRef,1,{TT})/1E9,{NA})", "#,##0.00"); flft = r; r += 1
    put(ws, f"A{r}", "註：本節不建「理論營收 — 100% 利用率」與 C 節每任務營收列（既有三層級的同類列於 v14.0 刪除，Workload 亦無 Terra 每任務成本）", F_NOTE)
    return {"first": r0, "last": r, "tok": tok, "rev": rev, "revf": revf, "fc": fc, "fcd": fcd, "gmd": gmd, "flt": flt, "flft": flft}


def checks_closure(wb, T, TT_rows):
    """Checks Block 4『機隊各層級貢獻合計 − 機隊合計』: add the Terra contribution (0 while the Terra paid share is 0)."""
    ws = wb["Checks"]
    lab = "機隊各層級貢獻合計 − 機隊合計（VR200；應為 0）"
    rows = [r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == lab]
    assert len(rows) == 1, rows
    c = ws.cell(rows[0], 2)
    old = f"=Theory_Rev!M{T['flt0']}+Theory_Rev!M{T['flt1']}+Theory_Rev!M{T['flt2']}-Theory_Rev!M{T['fl']}"
    new = f"=Theory_Rev!M{T['flt0']}+Theory_Rev!M{T['flt1']}+Theory_Rev!M{T['flt2']}+Theory_Rev!M{TT_rows['flt']}-Theory_Rev!M{T['fl']}"
    assert c.value in (old, new), c.value
    c.value = new
    ws.cell(rows[0], 1).value = lab.replace("機隊各層級貢獻合計", "機隊各層級貢獻合計（Luna＋Sol＋Astra＋Terra，v21.12 起四項）")
    return rows[0]


def harness_terra(wb, U, S, R):
    """Harness section J (below every existing row): Terra success rate, attempt／success cost, revenue, R, effective horizon (columns C–G = tasks)."""
    import block5
    ws = wb["Harness"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    r = r0
    section(ws, r, f"J. {TL}（v21.12 建置；v22.0 啟用：契約名稱 IF_TaskSucc_Terra、IF_CostSucc*_Terra、IF_HarR_Terra 等在 Interface R 節；H 節成功任務成本前緣仍只比較 Luna／Sol／Astra）", 8); r += 1
    out = {}
    for sk, sn in block5.SETS:
        out[f"p_{sk}"] = r
        block5.trow(ws, r, f"成功率 p：{TL}｜{sn}", "%",
                    f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{TK},1,{{k}})),INDEX(B5_SuccOvr_{TK},1,{{k}}),"
                    f"1/(1+(INDEX(B5_TaskLen,1,{{k}})/(INDEX(B5_H50,1,{TT})*{{c}}{R[sk+'_hz']}))^B5_Beta))", "0.0%", key=(sk == "cur")); r += 1
    cf, cc, cd = U[(TT, "cfu")], U[(TT, "ccu")], U[(TT, "cdu")]
    for gname, col in block5.GENS:
        for sk, sn in block5.SETS:
            out[f"c_{gname}{sk}"] = r
            block5.trow(ws, r, f"每次嘗試成本：{gname} × {TL}｜{sn}", "$",
                        f"=IF(ISNUMBER(Unit_Cost!{col}{cd}),({{c}}{R[sk+'_fp']}*Unit_Cost!{col}{cf}+{{c}}{R[sk+'_cp']}*(Unit_Cost!{col}{cc}"
                        f"+Cache_Store!{col}{S[TK]}*{{c}}{R[sk+'_ret']}/B4_Retain)+{{c}}{R[sk+'_dp']}*Unit_Cost!{col}{cd})/1E6,{NA})", "$#,##0.0000"); r += 1
    for gname, col in block5.GENS:
        for sk, sn in block5.SETS:
            cref, pref = f"{{c}}{out[f'c_{gname}{sk}']}", f"{{c}}{out[f'p_{sk}']}"
            out[f"cs_{gname}{sk}"] = r
            block5.trow(ws, r, f"每成功任務成本：{gname} × {TL}｜{sn}", "$", f"=IF(AND(ISNUMBER({cref}),{pref}>0),{cref}/{pref},{NA})", "$#,##0.0000",
                        key=(sk == "cur" and gname == "VR200")); r += 1
    out["rv_cur"] = r
    block5.trow(ws, r, f"每次嘗試營收：{TL}｜現行（依 T12 混合）", "$",
                f"=({{c}}{R['cur_fp']}*INDEX(B4_EffIn,1,{TT})+{{c}}{R['cur_cp']}*INDEX(B4_EffCache,1,{TT})+{{c}}{R['cur_dp']}*INDEX(B4_EffOut,1,{TT}))/1E6", "$#,##0.0000"); r += 1
    out["rs_cur"] = r
    block5.trow(ws, r, f"每成功任務營收：{TL}｜現行（依 T12 混合）", "$", f"=IF({{c}}{out['p_cur']}>0,{{c}}{out['rv_cur']}/{{c}}{out['p_cur']},0)", "$#,##0.0000"); r += 1
    for gname, col in block5.GENS:
        a, b = f"{{c}}{out[f'cs_{gname}sel']}", f"{{c}}{out[f'cs_{gname}std']}"
        out[f"R_{gname}"] = r
        block5.trow(ws, r, f"R（選定 ÷ 標準）：{gname} × {TL}", "x", f"=IF(AND(ISNUMBER({a}),ISNUMBER({b})),{a}/{b},{NA})", "0.00", key=(gname == "VR200")); r += 1
    out["hz"] = r
    block5.trow(ws, r, f"有效 50% 時間範圍：{TL}｜現行", "hr", f"=INDEX(B5_H50,1,{TT})*{{c}}{R['cur_hz']}", "0.00"); r += 1
    put(ws, f"A{r}", "註：每成功任務 token、標準／選定檔案的營收列與成功率比不建（既有三層級的同類列於 v14.0 刪除）", F_NOTE)
    out["first"], out["last"] = r0, r
    return out


def sens_har_terra(wb, U, S, SH, HT):
    """Sens_Har Terra rows (below every existing row): 50% horizon, attempt cost, p, R for the Coding agent column set."""
    ws = wb["Sens_Har"]
    cols = []
    for c in range(3, ws.max_column + 1):
        if ws.cell(4, c).value not in (None, ""):
            cols.append(c)
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    r = r0
    put(ws, f"A{r}", f"{TL}（v21.12 建置，v22.0 啟用；各欄同上方情境）", F_BOLD); r += 1
    rows = {}
    k = 5
    col = "M"
    cf, cc, cd = U[(TT, "cfu")], U[(TT, "ccu")], U[(TT, "cdu")]
    g = lambda key, X: f"{X}{SH[key]}"

    def drow(key, lab, fx, fmt, fill=False):
        nonlocal r
        put(ws, f"A{r}", lab)
        for ci in cols:
            X = L(ci)
            put(ws, f"{X}{r}", fx(X), fmt=fmt, fill=FILL_KEY if fill else None)
        rows[key] = r; r += 1

    def h50(X):
        lab = ws[f"{X}4"].value
        n = {"50% 時間範圍 低": "B5_H50Lo", "50% 時間範圍 高": "B5_H50Hi"}.get(lab, "B5_H50")
        return f"=INDEX({n},1,{TT})"
    drow("h", f"50% 時間範圍：{TL}（hr）", h50, "0.0")
    drow("cs", f"{TL}：選定每次嘗試成本 $",
         lambda X: f"=IF(ISNUMBER(Unit_Cost!${col}${cd}),({g('fp', X)}*Unit_Cost!${col}${cf}+{g('cp', X)}*(Unit_Cost!${col}${cc}+Cache_Store!${col}${S[TK]}*{g('Ret', X)}/B4_Retain)"
                   f"+{g('dp', X)}*Unit_Cost!${col}${cd})/1E6,{NA})", "$#,##0.0000")
    L_ = f"INDEX(B5_TaskLen,1,{k})"
    drow("p0", f"{TL}：p 標準", lambda X: f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{TK},1,{k})),INDEX(B5_SuccOvr_{TK},1,{k}),1/(1+({L_}/{X}{rows['h']})^{g('beta', X)}))", "0.0%")
    drow("p1", f"{TL}：p 選定", lambda X: f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{TK},1,{k})),INDEX(B5_SuccOvr_{TK},1,{k}),1/(1+({L_}/({X}{rows['h']}*{g('Hz', X)}))^{g('beta', X)}))", "0.0%")
    std = f"Harness!$G${HT['c_VR200std']}"
    drow("R", f"{TL}：R（每成功任務成本 選定 ÷ 標準）",
         lambda X: f"=IF(AND(ISNUMBER({X}{rows['cs']}),ISNUMBER({std})),({X}{rows['cs']}/{X}{rows['p1']})/({std}/{X}{rows['p0']}),{NA})", "0.00")
    rows["first"], rows["last"] = r0, r - 1
    return rows


def terra_late(wb, F, A, T, U, S, R5, SH5):
    tr = theory_rev_terra(wb, F, A, T)
    ck = checks_closure(wb, T, tr)
    ht = harness_terra(wb, U, S, R5)
    sh = sens_har_terra(wb, U, S, SH5, ht)
    return {"theory_rev": tr, "checks_row": ck, "harness": ht, "sens_har": sh}


# ---------------------------------------------------------------- S6 Checks Z3
def checks_z3(wb):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "Z3. 四層級組合合計檢查（v21.12，v22.0 B2 R4）：Z3 為 ERROR 計入 GOV_Errors", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{'ABCDE'[i]}{r}", h, F_BOLD)
    r += 1
    rows = []
    for code, lab, name in [("Z3a", "2026 付費 token 層級組合 Luna＋Sol＋Astra＋Terra 合計 ≠ 1（容差 1e-9）", "B4_MixPaid"),
                            ("Z3b", "2026 免費 token 層級組合四項合計 ≠ 1", "B4_MixFree"),
                            ("Z3c", "2025 付費 token 層級組合四項合計 ≠ 1（2025 口徑，J5）", "B4_MixPaid25"),
                            ("Z3d", "2025 免費 token 層級組合四項合計 ≠ 1（2025 口徑，J5）", "B4_MixFree25")]:
        put(ws, f"A{r}", code); put(ws, f"B{r}", lab); put(ws, f"C{r}", "ERROR", F_BOLD)
        terms = "+".join(f"INDEX({name},1,{t})" for t in range(1, tiers.NT + 1))
        put(ws, f"D{r}", f"=IF(ABS({terms}-1)>1E-9,1,0)", fmt="0")
        put(ws, f"E{r}", f"{name}（1×4：Luna、Sol、Astra、Terra）", F_NOTE)
        rows.append(r); r += 1
    ref = wb.defined_names["GOV_Errors"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    for x in rows:
        if f"D{x}" not in str(cell.value):
            cell.value = f"{cell.value}+D{x}"
    b = ws[f"B{int(ref[1:])}"]
    if "Z3" not in str(b.value):
        b.value = str(b.value).replace("Z2 節）", "Z2、Z3 節）")
    return rows


# ---------------------------------------------------------------- S7 用途 marks (R8)
def purpose_marks(wb, terra):
    """「預備」 marks on every formula row of the Terra blocks that no contract name reads yet. Existing marks are kept (the mark is appended)."""
    import v1400
    spans = {"Cache_Store": terra["cache"], "Fleet_1GW": terra["fleet"], "Amortize": terra["amort"],
             "Theory_Rev": (terra["late"]["theory_rev"]["first"], terra["late"]["theory_rev"]["last"]),
             "Harness": (terra["late"]["harness"]["first"], terra["late"]["harness"]["last"]),
             "Sens_Har": (terra["late"]["sens_har"]["first"], terra["late"]["sens_har"]["last"])}
    n = 0
    for sh, (a, b) in spans.items():
        ws = wb[sh]
        pc = v1400._purpose_col(ws)
        for r in range(a, b + 1):
            if not any(isinstance(ws.cell(r, c).value, str) and str(ws.cell(r, c).value).startswith("=") for c in range(3, pc)):
                continue
            c = ws.cell(r, pc)
            if c.value in (None, ""):
                put(ws, f"{L(pc)}{r}", PREP, F_NOTE); n += 1
            elif PREP not in str(c.value):
                c.value = f"{c.value} ｜{PREP}"; n += 1
    # Sens_Har: the Terra horizon row carries the yellow fill of the Astra horizon row on the scenario cells that differ from the base column
    #           (the live rows get their fill late in the build, so this runs at the end)
    from copy import copy
    ws = wb["Sens_Har"]
    sh = terra["late"]["sens_har"]
    src_r = next(r for r in range(1, sh["first"]) if str(ws.cell(r, 1).value).startswith("50% 時間範圍：Astra"))
    for ci in range(3, ws.max_column + 1):
        if ws.cell(src_r, ci).fill.fill_type and ws.cell(sh["h"], ci).value is not None:
            ws.cell(sh["h"], ci).fill = copy(ws.cell(src_r, ci).fill)
    # Price_Frontier: Terra candidate row (A section) and the Terra cells of B／D rows that only the live tiers' readers use (frontier model, thinking price)
    P = terra["pf"]
    ws = wb["Price_Frontier"]
    pc = v1400._purpose_col(ws)
    for r, txt in ((P["t1"], PREP + "（Terra 候選列：能力指數空白，不參與其他層級前緣，J7 (b)）"),
                   (P["frm"], PREP + f"（{tiers.TC[-1]}{P['frm']}：Terra 前緣模型）"), (P["eth"], PREP + f"（{tiers.TC[-1]}{P['eth']}：Terra 思考有效價）")):
        c = ws.cell(r, pc)
        if c.value in (None, ""):
            put(ws, f"{L(pc)}{r}", txt, F_NOTE); n += 1
        elif PREP not in str(c.value):
            c.value = f"{c.value} ｜{txt}"; n += 1
    return n


# ---------------------------------------------------------------- Load_Bearing!C3 (same rule as v21.10／v21.11)
def load_bearing_date(wb):
    ws = wb["Load_Bearing"]
    assert str(ws["A3"].value).startswith("建置日"), ws["A3"].value
    d = VERSION.split("_", 1)[0]
    put(ws, "C3", f"{d[:4]}-{d[4:6]}-{d[6:]}", F_CALC)


# ---------------------------------------------------------------- Decisions SL69-01
def _decisions():
    return [[DEC_ID, V, "v22.0 B2（結構二）：GPT-6.1 Terra 第四層級進入 Block 4–6（價格、壽命、組合、前緣、機隊、攤提、營收、harness），付費組合 Terra＝0，既有值逐值不變",
             "依設計文件 " + DESIGN + "（J2 (a)、J5 (a)、J6、J7 (b)、J9 (a)、J10、J14 (a)；R3–R8、R12）：Cap_In 第 5–8／21–24／30–32 列 F 欄放 Terra（牌價 1.00／0.05／5.00，"
             "商業壽命 9（4–18），付費／免費組合 Terra＝0、Sol 維持 0.45），標記／說明移 G／H（只限這些列；藍字格不移位）；B4_PriceIn／_PriceCache／_PriceOut／_Life／_MixPaid／_MixFree、"
             "B4_ISL／_OSL、B4_EffIn／_EffCache／_EffOut／_EffRef／_FrontRef、B5_H50／_Lo／_Hi 改 1×4。F 節第 59 列 GPT-6.1 Terra 候選（能力指數空白，J7 (b)），註記移第 60 列。"
             "新增 Cap_In R 節：B4_MixPaid25／B4_MixFree25（2025 口徑，Terra＝0，數值等於 v21.10）、B4_TerraFam（家族研發 Terra 計入開關，0）、CAP_TokGWPaidMix25。"
             "Price_Frontier 加 Terra 欄與第 14 列候選；門檻改由層級 → 候選列對照（R6）；無合格者取該層級 OpenAI 模型本身（R7）。"
             "Cache_Store、Fleet_1GW（E 節）、Amortize、Theory_Rev（E 節）、Harness（J 節）、Sens_Har 加 Terra 區（用途標「預備」，R8）；Har_In 第 58 列 Terra 成功率覆寫（B5_SuccOvr_Terra）。"
             "加總改四項（Fleet_1GW Σ、權重合計、閉合；家族研發 COUNT＝4、Terra × B4_TerraFam；Amortize K6 總額；Theory_Rev 機隊營收；Interface J 前緣機隊 _Prod；Cap_In 第 90 列；Checks 機隊閉合）。"
             "2025 口徑（J5）：Alloc B／I／K 節改讀 B4_MixPaid25／B4_MixFree25；CAP_Price25Mix；Cap_In 第 333 列讀 CAP_TokGWPaidMix25（→ L1_TokPaid_GW25）；"
             "Alloc K 節第 153 列（AL_RevGW25）改為付費服務占比 × 2025 口徑每 GW 付費產能 × 2025 單價（組合相同時與原式相等）。Checks Z3：四層組合合計＝1（2026／2025 × 付費／免費）。"
             "不建立 Terra 的 IF_／IFW_／L1_／RNG_ 名稱；Interface N 節 IF_TokGWPaidMix／IF_PxEffMix 與 L1 第 127 列 L1_TokGW_PaidCap_VR200 需 IF_TokGW_Terra 等名稱，仍三項（v22.0 B3）。依據：" + DEC_BY,
             DATE, DEC_BY, "v21.12 已建",
             "Cap_In F5:H8、F21:H24、F30:H32、第 59–60 列、R 節（第 350–356 列）；Price_Frontier；Cache_Store／Fleet_1GW／Amortize／Theory_Rev／Harness／Sens_Har Terra 區；Har_In 第 58 列；Alloc 第 22–28、119、148–150、153 列；Checks Z3",
             WO, "否"]]


def apply(wb, append_text):
    log = {"z3": checks_z3(wb)}
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ---------------------------------------------------------------- README
_prev = v21110.README_VERSION.split("_Tokenomics_", 1)[1]
README_VERSION = (VERSION + "（結構版，底版 v21.11：" + WO + "——v21.12：GPT-6.1 Terra 第四層級進入 Block 4–6；Terra 付費、免費組合＝0、家族研發計入開關＝0，"
                  "所有既有具名範圍與契約名稱的值不變；B4_Price*／_Life／_Mix*／_ISL／_OSL／_Eff*／_FrontRef、B5_H50* 由 1×3 改 1×4；新增 B4_MixPaid25／B4_MixFree25（2025 口徑，J5）、"
                  "B4_TerraFam、CAP_TokGWPaidMix25、B5_SuccOvr_Terra；Price_Frontier 第 14 列 Terra 候選（能力指數空白，J7 (b)）；Alloc 與 2025 錨點改讀 2025 口徑組合；Checks Z3；"
                  "Terra 尚無 IF_／L1_ 名稱（v22.0 啟用）；Decisions SL69-01。）以下為 " + _prev)
README_TITLE = V + v21110.README_TITLE[len(v21110.V):]

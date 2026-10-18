# v16.0 (work order docs/workorders/20261018_v16.0_L世代起點.md r0, branch claude/v16-0): L measured from each generation's own start (major version: new contract names).
#   W1  Cap_In section N "L 世代起點（v16.0）" below the M section (nothing above moves): generation service start s_v (base/low/high), calibration anchor A, pre-anchor price change g_pre,
#       t0 = MAX(0, A - s_v), L_rel (relative to the anchor), revenue weights, fleet L -> L1_LTotalFleetV (+_Lo/_Hi), per-generation L -> L1_LTotalV (4 cells),
#       discounted L -> L1_LTotalDisc (+_Lo/_Hi), required L without kappa -> L1_LReqFleet_IdNoK (+_Lo/_Hi).
#   W2  Cap_In row 242 reads L1_LTotalFleetV (three-state); three comparison rows (2025 = year 0 / fleet L vs no-kappa required L / discounted L vs no-kappa required L);
#       L1 row 89 P reads L1_LTotalFleetV; four L1 rows appended after the last row.
#   W3  Decisions SL49-01..04, DB_Evidence E398, README, contract document (outside the workbook).
# Every write to an Excel-owned cell is guarded (old text); no existing input value changes. Cap_In 242 is rewritten from the v15.3 text (v1530 writes it first on every build), so the edit is deterministic.
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY
import v1000
import v1020
import v1400
import v1410
import v1530

VERSION = "20261018_Tokenomics_v16.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-18"
V = "v16.0"
WO = "工作單 docs/workorders/20261018_v16.0_L世代起點.md（r0）"
DASH = "—"
DEC_BY = ("Andy 2026-10-18 10:20「L 应该就是衡量在这个硬体的生命周期里，token 的价格的下跌趋势…本来就是 L 本来就是应该用自己每个世代来算的。我们用二零二五，其实是只是一个锚点，因为二零二五已经过去了，"
          "而且有比较多的一个数据，所以我们是当做一个锚点了。…不然你不可能未来几年，我们都还是用二零二五年来算，毕竟我们这东西算出来之后是要去预期或预估未来的一个状况嘛。」；10:24「合併」"
          "（同意 chat 端 10:21 提出的 v15.4 方向，合併後開工）；數值為 chat 端建議，可撤回")
DEF_TXT = ("L＝某一世代硬體在其壽命期 T 內，token 單價相對該世代『起點』單價的平均（跌價＋降級）。每個世代從自己的起點算。2025 年是校準錨點（觀察營收與支出的年度），不是 L 的起點。"
           "現行 L1_LTotal 的公式就是『新世代、起點＝第 0 年』的 L，保留不改。")

GENS = ("Hopper", "GB200", "GB300", "VR200")
SV_BASE = (2023.5, 2025.0, 2025.5, 2026.75)
SV_LO = (2023.0, 2025.0, 2025.5, 2026.75)      # earlier
SV_HI = (2024.0, 2025.5, 2025.6, 2027.0)       # later
ANCHOR = 2025.5
GPRE = (-0.09, -0.30, -0.09)                    # C base, D low, E high

ROWS = {}      # key -> Cap_In row (filled by cap_in_n)
PURPOSE_MARKS = {}      # Cap_In row -> 用途 text for the dead display cells (written in apply)
SEC_TITLE = "N. L 世代起點（v16.0；" + WO + "）：" + DEF_TXT

# ---------------------------------------------------------------- formulas
def _ln(x): return f"LN(1+{x})"


def lrel_formula(col, t0cell, c, gp):
    """L_rel of generation column `col`: t0cell = that generation's t0 (Cap_In cell), c = scenario column (C base / D low / E high) of the g, T1, rho, T rows, gp = g_pre cell."""
    g, t1, rho, T = f"${c}$226", f"${c}$227", f"${c}$228", f"${c}$229"
    t0 = t0cell
    past = f"IF({t0}>0,IF(ABS({_ln(gp)})<0.000000000001,{t0},(1-(1+{gp})^(-{t0}))/{_ln(gp)}),0)"
    a, b = f"({t1}-{t0})", f"({T}-{t0})"
    fut = (f"IF(ABS({_ln(g)})<0.000000000001,{a}+{rho}*({b}-{a}),(((1+{g})^{a}-1)+{rho}*((1+{g})^{b}-(1+{g})^{a}))/{_ln(g)})")
    return f'=IF({t0}>{t1},"t0 > T1（已降級，未支援）",({past}+{fut})/{T})'


def fleet_formula(lrow, wrow):
    w, l = f"$C${wrow}:$F${wrow}", f"$C${lrow}:$F${lrow}"
    return (f'=IF(COUNT({w})<4,AL_UnavailTxt,IF(SUM({w})<=0,AL_UnavailTxt,IF(SUMPRODUCT(ISTEXT({l})*({w}>0))>0,'
            f'"含 t0 > T1 的世代（已降級，未支援）",SUMPRODUCT({w},{l})/SUM({w}))))')


def disc_formula(c, wacc):
    g, t1, rho, T = f"{c}$226", f"{c}$227", f"{c}$228", f"{c}$229"
    a = f"({_ln(g)}-LN(1+{wacc}))"
    d = f"(-LN(1+{wacc}))"
    num = f"IF(ABS({a})<0.000000000001,{t1}+{rho}*({T}-{t1}),((EXP({a}*{t1})-1)+{rho}*(EXP({a}*{T})-EXP({a}*{t1})))/{a})"
    den = f"IF(ABS({d})<0.000000000001,{T},(EXP({d}*{T})-1)/{d})"
    return f"={num}/{den}"


def idnok_formula(num, den_basis):
    return (f'=IF(AND(ISNUMBER({num}),ISNUMBER({den_basis}),ISNUMBER(SRC_DEM_007)),IF({den_basis}*SRC_DEM_007>0,{num}/({den_basis}*SRC_DEM_007),AL_UnavailTxt),AL_UnavailTxt)')


def tri(lb, llo, lhi, rb, rlo, rhi, lname="L"):
    num = ",".join(f"ISNUMBER({x})" for x in (lb, llo, lhi, rb, rlo, rhi))
    return (f'=IF(AND({num}),IF({lhi}<{rlo},"未回本（L 區間全在所需 L 之下）",IF({llo}>{rhi},"回本（L 區間全在所需 L 之上）",'
            f'"未定（區間重疊；基準 {lname} "&TEXT({lb},"0.000")&" 對所需 L "&TEXT({rb},"0.000")&"）")),"所需 L 或 L 非數字（本情境）")')


# ---------------------------------------------------------------- Cap_In N section
LAB = dict(
    sv="世代服務起點 s_v（年，小數；基準；N-1）　Hopper／GB200／GB300／VR200",
    sv_lo="世代服務起點 s_v 低（較早）",
    sv_hi="世代服務起點 s_v 高（較晚）",
    anchor="校準錨點年 A（年；2025 營收與支出的年中；N-1）",
    gpre="錨點前中階牌價年變化率 g_pre（C 基準／D 低／E 高；N-1）",
    t0="錨點時已服務年數 t0＝MAX(0, A − s_v)（基準；N-2）",
    t0_lo="t0（低端組合：s_v 取高＝較晚，t0 小）",
    t0_hi="t0（高端組合：s_v 取低＝較早，t0 大）",
    lrel="L_rel（相對錨點；基準；各世代，N-3）",
    lrel_lo="L_rel（低端組合：g、T1、ρ 取 D 欄，g_pre 取 E 欄 −0.09，t0 取低端組合）",
    lrel_hi="L_rel（高端組合：g、T1、ρ 取 E 欄，g_pre 取 D 欄 −0.30，t0 取高端組合）",
    w="2025 營收權重 w_v＝AL_ShareGen_v × 該世代每 GW 付費營收（2025 單價，AL_RevGW25）",
    fleet="機隊 L（世代起點，錨點 2025）＝Σ w_v × L_rel_v ÷ Σ w_v　→ L1_LTotalFleetV（D 欄＝低端組合、E 欄＝高端組合）",
    lv="各世代 L（相對自身起點）＝L1_LTotal　→ L1_LTotalV（4 格：Hopper／GB200／GB300／VR200）",
    disc="折現版 L（F2 對照；WACC＝Inputs E28／D28／F28）　→ L1_LTotalDisc",
    idnok="所需 L 不含 κ（F1 對照）＝SRC_DEM_004 ÷（AL_SpendBasis × SRC_DEM_007）　→ L1_LReqFleet_IdNoK",
    j_a="對照：2025＝第 0 年（v15.3 口徑）：L1_LTotal 區間 對 所需 L（L1_LReqFleet_Id）區間；三態",
    j_b="對照：世代起點 L 對 不含 κ 所需 L：L1_LTotalFleetV 區間 對 L1_LReqFleet_IdNoK 區間；三態",
    j_c="對照：折現版 L 對 不含 κ 所需 L：L1_LTotalDisc 區間 對 L1_LReqFleet_IdNoK 區間；三態",
)
NOTE = dict(
    sv=("依據 Cap_In 第 272–274 列已登錄的雲端供應日期（H100 2023-03-21；GB200 2025-02-04；GB300 2025-07-03；VR200 2026-09-30），OpenAI 機隊放量取其後；Hopper 機隊多在 2023 年中至 2024 年建成。"
        "基準 2023.5／2025.0／2025.5／2026.75。標記 Assumed；DB_Evidence E398；Decisions SL49-04"),
    sv_lo="較早：2023.0／2025.0／2025.5／2026.75（高端組合用，t0 大）",
    sv_hi="較晚：2024.0／2025.5／2025.6／2027.0（低端組合用，t0 小）",
    anchor="Decision：2025 營收與支出的年中（校準錨點，不是 L 的起點）。Decisions SL49-01",
    gpre=("基準 −0.09（同 g）；D 欄 −0.30 反映 2023–24 一次性重估（年化約 −55% 的一部分），當時量小，證據最弱；E 欄 −0.09。低端組合取 E 欄、高端組合取 D 欄（錨點前跌得越多，錨點時越便宜，之後相對錨點價格的 L 越大）。"
          "只在 t0 > 0 的世代進入 L_rel 的『已服務段』"),
    t0="t0 ＝ 錨點年 − 該世代服務起點（不小於 0）。t0 = 0 的世代（GB200 的低端組合、GB300 的基準與低端組合、VR200）L_rel 等於 L1_LTotal",
    t0_lo="低端組合用 s_v 高（較晚）：t0 較小",
    t0_hi="高端組合用 s_v 低（較早）：t0 較大",
    lrel_lo="低端組合：g、T1、ρ 取第 226／227／228／229 列的 D 欄（−0.20／3／D228／6）、g_pre 取 E 欄（−0.09）、t0 取低端組合；其餘公式同基準列",
    lrel_hi="高端組合：g、T1、ρ 取 E 欄（+0.05／5／0.7／6）、g_pre 取 D 欄（−0.30）、t0 取高端組合；其餘公式同基準列",
    lrel=("L_rel＝（past ＋ fut）÷ T；past＝IF(t0>0,(1−(1+g_pre)^(−t0))÷LN(1+g_pre),0)；fut＝(((1+g)^(T1−t0)−1)＋ρ×((1+g)^(T−t0)−(1+g)^(T1−t0)))÷LN(1+g)；"
          "g、T1、ρ、T 取第 226／227／228／229 列的 C 欄。若 t0 > T1 輸出文字『t0 > T1（已降級，未支援）』（目前沒有）"),
    w="只含占比 > 0 的世代；占比 AL_ShareGen 與每 GW 付費營收（Alloc 第 153 列）皆為既有名稱，不在此新增輸入",
    fleet=("C 基準；D 低端組合（g −0.20、T1 3、ρ D228、s_v 高、g_pre −0.09）；E 高端組合（g +0.05、T1 5、ρ 0.7、s_v 低、g_pre −0.30）。chat 端事前計算 0.7159／0.4265／1.1190。"
           "定義的主口徑：判讀（第 242 列、L1 第 89 列）改讀本列"),
    lv="目前四世代 g／T1／ρ 輸入相同，故四格同值；日後 g／T1／ρ 分世代輸入時才會不同。D／E 欄＝四世代的低端與高端同為 L1_LTotal_Lo／_Hi",
    disc="a＝LN(1+g)−LN(1+WACC)，d＝−LN(1+WACC)；L＝(((EXP(a·T1)−1)＋ρ(EXP(a·T)−EXP(a·T1)))÷a)÷((EXP(d·T)−1)÷d)。WACC：C 欄 Inputs E28、D 欄 D28、E 欄 F28。只作對照，不進判讀。事前計算 0.6988／0.4401／1.0941",
    idnok="C＝SRC_DEM_004 ÷（AL_SpendBasis × SRC_DEM_007）；D（低）＝SRC_DEM_004_Lo ÷（AL_SpendBasis_Hi × SRC_DEM_007）；E（高）＝SRC_DEM_004_Hi ÷（AL_SpendBasis_Lo × SRC_DEM_007）。只作對照，不進判讀。事前計算 0.7561／0.4905／0.9223",
    j_a="原 v15.3 第 242 列邏輯（L 側讀 L1_LTotal）；文字三態；只作對照",
    j_b="文字三態；只作對照（F1：是否改以不含 κ 的所需 L 為主，待 Andy）",
    j_c="文字三態；只作對照（F2：是否改以折現版 L 為主，待 Andy）",
)


def cap_in_n(wb, m_sec):
    ws = wb["Cap_In"]
    r0 = m_sec["end"] + 2
    assert ws.max_row == m_sec["end"], (ws.max_row, m_sec["end"])
    put(ws, f"A{r0}", SEC_TITLE, F_BOLD, wrap=True)
    r = r0 + 1
    put(ws, f"A{r}", "欄位：世代列 C Hopper／D GB200／E GB300／F VR200（與 Alloc 第 16–18 列世代順序一致）；情境列 C 基準／D 低端／E 高端；G 標記、H 說明、O 用途", F_NOTE, wrap=True)
    for col, g in zip("CDEF", GENS):
        put(ws, f"{col}{r}", g, F_BOLD)
    r += 1
    order = ["sv", "sv_lo", "sv_hi", "anchor", "gpre", "t0", "t0_lo", "t0_hi", "lrel", "lrel_lo", "lrel_hi", "w", "fleet", "lv", "disc", "idnok", "j_a", "j_b", "j_c"]
    for k in order:
        ROWS[k] = r; r += 1
    R = ROWS

    def row(k, unit, vals, tag, fmt, blue=False, key=False, purpose=None):
        rr = R[k]
        put(ws, f"A{rr}", LAB[k], wrap=True); put(ws, f"B{rr}", unit)
        for col, v in zip("CDEF", vals):
            if v is None:
                continue
            isf = isinstance(v, str) and v.startswith("=")
            put(ws, f"{col}{rr}", v, (F_IN if blue else (F_LINK if isf and "!" in v else F_CALC)), fmt=fmt, fill=FILL_KEY if (key and col == "C") else None)
        put(ws, f"G{rr}", tag, F_NOTE); put(ws, f"H{rr}", NOTE[k], F_NOTE, wrap=True)
        if purpose:
            PURPOSE_MARKS[rr] = purpose      # written by apply() into the 用途 column (created by v1010／v1400 later in the build)

    row("sv", "年", SV_BASE, "Assumed", "0.00", blue=True, key=True)
    row("sv_lo", "年", SV_LO, "Assumed", "0.00", blue=True)
    row("sv_hi", "年", SV_HI, "Assumed", "0.00", blue=True)
    row("anchor", "年", (ANCHOR,), "Decision", "0.00", blue=True)
    row("gpre", "%", GPRE, "Assumed", "0.0%", blue=True)
    A = f"$C${R['anchor']}"
    row("t0", "年", [f"=MAX(0,{A}-{c}{R['sv']})" for c in "CDEF"], "Derived", "0.00")
    row("t0_lo", "年", [f"=MAX(0,{A}-{c}{R['sv_hi']})" for c in "CDEF"], "Derived", "0.00")
    row("t0_hi", "年", [f"=MAX(0,{A}-{c}{R['sv_lo']})" for c in "CDEF"], "Derived", "0.00")
    gp = lambda c: f"${c}${R['gpre']}"
    row("lrel", "x", [lrel_formula(c, f"{c}{R['t0']}", "C", gp("C")) for c in "CDEF"], "Derived", "0.0000")
    row("lrel_lo", "x", [lrel_formula(c, f"{c}{R['t0_lo']}", "D", gp("E")) for c in "CDEF"], "Derived", "0.0000")
    row("lrel_hi", "x", [lrel_formula(c, f"{c}{R['t0_hi']}", "E", gp("D")) for c in "CDEF"], "Derived", "0.0000")
    row("w", "$B/GW/年", [f'=IF(AND(ISNUMBER(INDEX(AL_ShareGen,1,{i})),ISNUMBER(INDEX(AL_RevGW25,1,{i}))),INDEX(AL_ShareGen,1,{i})*INDEX(AL_RevGW25,1,{i}),IF(AND(ISNUMBER(INDEX(AL_ShareGen,1,{i})),INDEX(AL_ShareGen,1,{i})=0),0,AL_UnavailTxt))'
                           for i in (1, 2, 3, 4)], "Derived", "0.000")
    row("fleet", "x", [fleet_formula(R["lrel"], R["w"]), fleet_formula(R["lrel_lo"], R["w"]), fleet_formula(R["lrel_hi"], R["w"])], "Derived", "0.0000", key=True)
    row("lv", "x", ["=L1_LTotal"] * 4, "Derived", "0.0000")
    row("disc", "x", [disc_formula("C", "Inputs!$E$28"), disc_formula("D", "Inputs!$D$28"), disc_formula("E", "Inputs!$F$28")], "Derived", "0.0000")
    row("idnok", "x", [idnok_formula("SRC_DEM_004", "AL_SpendBasis"), idnok_formula("SRC_DEM_004_Lo", "AL_SpendBasis_Hi"), idnok_formula("SRC_DEM_004_Hi", "AL_SpendBasis_Lo")], "Derived", "0.0000")
    row("j_a", "x", [tri("L1_LTotal", "L1_LTotal_Lo", "L1_LTotal_Hi", "L1_LReqFleet_Id", "L1_LReqFleet_Id_Lo", "L1_LReqFleet_Id_Hi", "L（2025＝第 0 年）")], "Derived", None,
        purpose="顯示用：C%d（對照列：2025＝第 0 年，v15.3 口徑）" % R["j_a"])
    row("j_b", "x", [tri("L1_LTotalFleetV", "L1_LTotalFleetV_Lo", "L1_LTotalFleetV_Hi", "L1_LReqFleet_IdNoK", "L1_LReqFleet_IdNoK_Lo", "L1_LReqFleet_IdNoK_Hi", "世代起點 L")], "Derived", None,
        purpose="顯示用：C%d（對照列：世代起點 L 對不含 κ 所需 L）" % R["j_b"])
    row("j_c", "x", [tri("L1_LTotalDisc", "L1_LTotalDisc_Lo", "L1_LTotalDisc_Hi", "L1_LReqFleet_IdNoK", "L1_LReqFleet_IdNoK_Lo", "L1_LReqFleet_IdNoK_Hi", "折現版 L")], "Derived", None,
        purpose="顯示用：C%d（對照列：折現版 L 對不含 κ 所需 L）" % R["j_c"])
    for col in "CDEF":
        pass
    return dict(start=r0, end=r - 1, rows=dict(R))


# ---------------------------------------------------------------- Gov_Map rows (blue inputs)
def gov_map_rows(wb):
    if not ROWS:
        return []
    ws = wb["Cap_In"]
    R = ROWS
    out = []
    sc = "切片三（v16.0 L 世代起點）"
    basis = ("v16.0 W1（" + WO + "；Decisions SL49-04）：世代服務起點依 Cap_In 第 272–274 列已登錄的雲端供應日期（H100 2023-03-21；GB200 2025-02-04；GB300 2025-07-03；VR200 2026-09-30），"
             "OpenAI 機隊放量取其後；Hopper 機隊多在 2023 年中至 2024 年建成。只進 Cap_In N 節與 L1_LTotalFleetV／LTotalV；DB_Evidence E398")

    def ent(k, cell, role, cls, dec, lo, hi, rtext, reason, seg="無"):
        lab = ws[f"A{R[k]}"].value
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': cell.format(r=R[k]), 'label': lab, 'check': lab, 'cls': cls, 'role': role, 'src': '', 'rel': '', 'dec': dec,
                    'lo': (lo.format(r=R[k]) if isinstance(lo, str) else lo), 'hi': (hi.format(r=R[k]) if isinstance(hi, str) else hi), 'rtext': rtext, 'reason': reason, 'retag': '', 'seg': seg})

    ent("sv", "C{r}:F{r}", "單值", "Assumed", "SL49-04", None, None, "基準 2023.5／2025.0／2025.5／2026.75（區間見 s_v 低／高兩列）", basis)
    ent("sv_lo", "C{r}:F{r}", "低", "Assumed", "SL49-04", None, None, "較早端 2023.0／2025.0／2025.5／2026.75（s_v 基準的低端）", basis, seg="—")
    ent("sv_hi", "C{r}:F{r}", "高", "Assumed", "SL49-04", None, None, "較晚端 2024.0／2025.5／2025.6／2027.0（s_v 基準的高端）", basis, seg="—")
    ent("anchor", "C{r}", "單值", "Decision", "SL49-01", None, None, "單值 2025.5（Decision）",
        "v16.0 W1（SL49-01）：校準錨點年 A＝2025 營收與支出的年中；2025 是校準錨點（觀察營收與支出的年度），不是 L 的起點；Andy 2026-10-18 10:20 語音。只進 Cap_In N 節 t0")
    reason_gp = ("v16.0 W1（Decisions SL49-04）：錨點前中階牌價年變化率 g_pre，基準 −0.09（同 g）、低 −0.30（2023–24 一次性重估，年化約 −55% 的一部分；當時量小，證據最弱）、高 −0.09；"
                 "低端組合取 −0.09、高端組合取 −0.30；只在 t0 > 0 的世代進入 L_rel；只進 Cap_In N 節與 L1_LTotalFleetV")
    ent("gpre", "C{r}", "基準", "Assumed", "SL49-04", "=Cap_In!D{r}", "=Cap_In!E{r}", "−0.30～−0.09（D 欄＝低 −0.30、E 欄 −0.09）", reason_gp)
    ent("gpre", "D{r}:E{r}", "低／高", "Assumed", "SL49-04", None, None, "C{r} 的低（−0.30）、高（−0.09）端點".replace("{r}", str(R["gpre"])), reason_gp, seg="—")
    return out


# ---------------------------------------------------------------- Cap_In row 242 / A242 / G242 (before gov_all)
A242_OLD = v1530.A242_NEW
A242_NEW = "判讀：世代起點 L 區間 對 所需 L 區間（恆等式讀法 L1_LReqFleet_Id；三態：未回本／未定／回本；v16.0 起 L 側讀 L1_LTotalFleetV）"
G242_ADD = ("｜v16.0 W2：本列 L 側改讀 L1_LTotalFleetV（世代起點 L，區間 [L1_LTotalFleetV_Lo, L1_LTotalFleetV_Hi]）；所需 L 側不變（L1_LReqFleet_Id）；三態規則同 v15.3 D1。"
            "v15.3 口徑（2025＝第 0 年，L 側讀 L1_LTotal）保留為 Cap_In N 節對照列；Andy 2026-10-18 10:20 定義見 Decisions SL49-01／02")


def inputs_update(wb, append_text):
    log = []
    ws = wb["Cap_In"]
    assert ws["A242"].value in (v1530.A242_NEW, A242_NEW), ws["A242"].value
    n = 0
    for c in "CDE":
        cur = ws[f"{c}242"].value
        assert isinstance(cur, str) and cur.startswith("=IF(AND(ISNUMBER(L1_LTotal"), cur[:60]
        if "L1_LTotalFleetV" not in cur:
            ws[f"{c}242"].value = cur.replace("L1_LTotal", "L1_LTotalFleetV"); n += 1
    ws["A242"].value = A242_NEW
    n += int(append_text(ws["G242"], G242_ADD))
    log.append(f"Cap_In row 242 reads L1_LTotalFleetV ({n} edits)")
    return log


# ---------------------------------------------------------------- L1 rows (appended after the last existing row)
READ_FV = ("L 的新定義（Andy 2026-10-18）：L＝某世代硬體在其壽命期 T 內，token 單價相對該世代起點單價的平均（跌價＋降級）；每個世代從自己的起點算，2025 年只是校準錨點。"
           "機隊 L 把每個世代在 2025 年錨點時已服務 t0 年（Cap_In N 節）折成相對錨點的 L_rel，再以 2025 營收（占比 × 每 GW 付費營收）加權。判讀（Cap_In 第 242 列、L1 第 89 列）改讀本列。")
NONE_EXT = ("無外部對照", DASH, DASH)


def l1_rows_new():
    R = ROWS
    def cap(col, key): return f"=Cap_In!${col}${R[key]}"
    return [
        ("LTotalFleetV", "壽命期價格係數 L — 機隊 L（世代起點；錨點 2025）", "各世代從自己的服務起點 s_v 算 L；錨點年 A＝2025.5；以 2025 營收（AL_ShareGen × AL_RevGW25）加權；v16.0",
         cap("C", "fleet"), cap("D", "fleet"), cap("E", "fleet"), "x",
         "低＝低端組合（g −0.20、T1 3、ρ 0.17、s_v 較晚、g_pre −0.09）；高＝高端組合（g +0.05、T1 5、ρ 0.7、s_v 較早、g_pre −0.30）", READ_FV,
         "g、T1、ρ、s_v、g_pre、2025 營收權重", "s_v、g_pre：Assumed；g、ρ：Derived；T1：Assumed", *NONE_EXT, "AL_ShareGen；AL_RevGW25；IF_DeprLifeIT", f"Cap_In 第 {R['fleet']} 列",
         "各世代服務起點無一手資料（以雲端供應日期推定）；Hopper 的錨點前跌價證據最弱"),
        ("LTotalV", "各世代 L（相對自身起點；D 欄＝VR200 欄、E／F 欄＝四世代最小／最大）", "＝L1_LTotal（新世代、起點＝第 0 年）；目前四世代 g／T1／ρ 輸入相同故同值；L1_LTotalV 具名範圍為 Cap_In 四格（Hopper／GB200／GB300／VR200）；v16.0",
         f"=INDEX(Cap_In!$C${R['lv']}:$F${R['lv']},1,4)", f"=MIN(Cap_In!$C${R['lv']}:$F${R['lv']})", f"=MAX(Cap_In!$C${R['lv']}:$F${R['lv']})", "x",
         "E／F＝四世代的最小／最大值（目前相同）；具名範圍 L1_LTotalV 是四格橫列，不是本列 D 欄", READ_FV,
         "g、T1、ρ、IT 折舊年限", "同 L1_LTotal", *NONE_EXT, "L1_LTotal", f"Cap_In 第 {R['lv']} 列",
         "日後 g／T1／ρ 分世代輸入時四格才會不同"),
        ("LTotalDisc", "壽命期價格係數 L — 折現版（F2 對照；WACC 折現）", "＝(((EXP(a·T1)−1)＋ρ(EXP(a·T)−EXP(a·T1)))÷a)÷((EXP(d·T)−1)÷d)，a＝LN(1+g)−LN(1+WACC)，d＝−LN(1+WACC)；新世代、起點＝第 0 年；v16.0",
         cap("C", "disc"), cap("D", "disc"), cap("E", "disc"), "x", "低＝g −0.20、T1 3、ρ 0.17、WACC 8%；高＝g +0.05、T1 5、ρ 0.7、WACC 13%", READ_FV + " 本列為折現口徑對照，不進判讀。",
         "g、T1、ρ、WACC", "WACC：Assumed（Inputs E28）", *NONE_EXT, "Inputs E28／D28／F28", f"Cap_In 第 {R['disc']} 列", "只作對照；主口徑是否改折現版待 Andy（F2）"),
        ("LReqFleet_IdNoK", "回本所需 L — 恆等式讀法、不含 κ（F1 對照）", "＝SRC_DEM_004 ÷（AL_SpendBasis × SRC_DEM_007）；低＝SRC_DEM_004_Lo ÷（AL_SpendBasis_Hi × SRC_DEM_007）；高＝SRC_DEM_004_Hi ÷（AL_SpendBasis_Lo × SRC_DEM_007）；v16.0",
         cap("C", "idnok"), cap("D", "idnok"), cap("E", "idnok"), "x", "低＝推論支出取低端、支出口徑取高端；高＝推論支出取高端、支出口徑取低端",
         "回本所需 L 的恆等式讀法（持有成本 ÷ 實收營收）去掉請求形狀修正 κ；只作對照，不進判讀（F1：是否改以不含 κ 為主，待 Andy）。",
         "SRC_DEM_004、AL_SpendBasis、SRC_DEM_007", "SRC_DEM_004：3 級來源（利害關係方）；AL_SpendBasis：Assumed", *NONE_EXT, "SRC_DEM_004；AL_SpendBasis；SRC_DEM_007", f"Cap_In 第 {R['idnok']} 列",
         "只作對照；κ 為 1.0 時基準值與 L1_LReqFleet_Id 相同"),
    ]


v1000._n(v1000.E_, "壽命期價格係數 L 的世代起點定義（v16.0）：機隊 L 與各世代 L（價格迴歸與降級假設；起點、前期跌價為 Assumed）", "LTotalFleetV", "LTotalV")
v1000._n(v1000.E_, "折現版 L：L 的折現口徑對照（WACC 折現；不進判讀）", "LTotalDisc")
v1000._n(v1000.I_, "機隊持有成本 ÷ 實收營收（去掉 κ）：恆等式讀法的對照，不進判讀", "LReqFleet_IdNoK")


def late_names(wb):
    """After l1_sheet: L1_LTotalV is the 4-cell Cap_In row (not the L1 D cell); the auto-created _Lo／_Hi names of that row are dropped (work order names L1_LTotalV only)."""
    r = ROWS["lv"]
    wb.defined_names["L1_LTotalV"] = DefinedName("L1_LTotalV", attr_text=f"Cap_In!$C${r}:$F${r}")
    for n in ("L1_LTotalV_Lo", "L1_LTotalV_Hi"):
        if n in wb.defined_names:
            del wb.defined_names[n]


# ---------------------------------------------------------------- L1 P89 (late: needs the final L1 row number of L1_LTotalFleetV)
def l1_p89(wb):
    ws = wb["L1"]
    fv = int(wb.defined_names["L1_LTotalFleetV"].attr_text.split("$")[-1])
    assert ws[f"A{fv}"].value == "L1_LTotalFleetV", (fv, ws[f"A{fv}"].value)
    assert ws["A89"].value == "L1_LReqFleet", ws["A89"].value
    cur = ws["P89"].value
    if f"D{fv}" in cur:
        return 0
    reps = [
        ("ISNUMBER(D89),ISNUMBER(D107),ISNUMBER(M89)", f"ISNUMBER(D89),ISNUMBER(D107),ISNUMBER(D{fv})", 1),
        ("AND(ISNUMBER(E88),ISNUMBER(F88),ISNUMBER(E107),ISNUMBER(F107))", f"AND(ISNUMBER(E{fv}),ISNUMBER(F{fv}),ISNUMBER(E107),ISNUMBER(F107))", 2),
        ('IF(F88<E107,"未回本",IF(E88>F107,"回本","未定"))', f'IF(F{fv}<E107,"未回本",IF(E{fv}>F107,"回本","未定"))', 2),
        ('IF(M89>=D107,"回本","未回本")', f'IF(D{fv}>=D107,"回本","未回本")', 2),
        ("AND(ISNUMBER(D107),ISNUMBER(M89))", f"AND(ISNUMBER(D107),ISNUMBER(D{fv}))", 1),
        ('&"）；字面讀法 "&TEXT(D89,"0.00")', '&"；v15.3 口徑 2025＝第 0 年：L "&TEXT(L1_LTotal,"0.000")&"）；字面讀法 "&TEXT(D89,"0.00")', 1),
        ('"（L_total "&TEXT(M89,"0.00")&" 對所需 L "&TEXT(D107,"0.00")', f'"（世代起點 L "&TEXT(D{fv},"0.00")&" 對所需 L "&TEXT(D107,"0.00")', 1),
        ('"（恆等式讀法：L_total "&TEXT(M89,"0.00")&" 對所需 L "&TEXT(D107,"0.00")&"；字面讀法非數字）"',
         f'"（恆等式讀法：世代起點 L "&TEXT(D{fv},"0.00")&" 對所需 L "&TEXT(D107,"0.00")&"；v15.3 口徑 2025＝第 0 年：L "&TEXT(L1_LTotal,"0.000")&"；字面讀法非數字）"', 1),
    ]
    for old, new, cnt in reps:
        assert cur.count(old) == cnt, (old, cur.count(old))
        cur = cur.replace(old, new)
    assert "M89" not in cur and "E88" not in cur
    ws["P89"].value = cur
    return 1


# ================================================================== Decisions SL49-01..04, DB_Evidence E398
def _decisions():
    D = [
        ("L 的定義：按各世代自己的起點計算；2025 只是校準錨點（Andy 原話）",
         "L＝某一世代硬體在其壽命期 T 內，token 單價相對該世代起點單價的平均（跌價＋降級）。每個世代從自己的起點算。2025 年是校準錨點（觀察營收與支出的年度），不是 L 的起點。"
         "現行 L1_LTotal 的公式就是『新世代、起點＝第 0 年』的 L，保留不改。新增 Cap_In N 節『L 世代起點』與 L1_LTotalFleetV／LTotalV。"
         "Andy 2026-10-18 10:20 原話（語音轉寫，未改字）：" + "L 应该就是衡量在这个硬体的生命周期里，token 的价格的下跌趋势…本来就是 L 本来就是应该用自己每个世代来算的。我们用二零二五，其实是只是一个锚点，因为二零二五已经过去了，"
         "而且有比较多的一个数据，所以我们是当做一个锚点了。…不然你不可能未来几年，我们都还是用二零二五年来算，毕竟我们这东西算出来之后是要去预期或预估未来的一个状况嘛。」。"
         "（Decisions SL48-01 已於 v15.3 補登 C1，本版確認、不重複。）",
         DEC_BY, "Cap_In N 節（第 %d–%d 列）；L1_LTotalFleetV、L1_LTotalV；README" % (ROWS["sv"], ROWS["j_c"])),
        ("回本判讀主口徑改 L1_LTotalFleetV（Cap_In 第 242 列、L1 第 89 列）",
         "Cap_In 第 242 列三態判讀的 L 側由 L1_LTotal 改讀 L1_LTotalFleetV（所需 L 側不變，仍為 L1_LReqFleet_Id）；L1 第 89 列 P 欄的恆等式讀法同步改讀 L1_LTotalFleetV，並附『v15.3 口徑 2025＝第 0 年：L 0.660』。"
         "基準下仍為『未定』（基準 L 0.716 對所需 L 0.756）。v15.3 口徑（L1_LTotal）保留為 Cap_In N 節對照列。",
         DEC_BY, "Cap_In 第 242 列（A、C、D、E、G）、N 節對照列；L1 P89"),
        ("F1、F2 只列對照；主口徑是否改待 Andy",
         "F1：恆等式讀法的所需 L 是否改為不含 κ（L1_LReqFleet_IdNoK）；F2：L 是否改為折現版（L1_LTotalDisc）。兩者本版只列對照（Cap_In N 節三列對照、L1 新增列），不進判讀。"
         "建議預設：F1 改不含 κ、F2 以折現版為主；Andy 未回應前不改主口徑（判讀仍讀 L1_LTotalFleetV 對 L1_LReqFleet_Id）。",
         "chat 端建議（工作單 W3），Andy 尚未回應；可撤回", "Cap_In N 節；L1_LTotalDisc、L1_LReqFleet_IdNoK"),
        ("新輸入登錄：s_v（世代服務起點）、錨點年 A、g_pre（錨點前牌價年變化率）",
         "s_v 基準 2023.5／2025.0／2025.5／2026.75，低（較早）2023.0／2025.0／2025.5／2026.75，高（較晚）2024.0／2025.5／2025.6／2027.0（Assumed）；依據 Cap_In 第 272–274 列已登錄的雲端供應日期，不新增外部來源（DB_Evidence E398）。"
         "錨點年 A 2025.5（Decision）。g_pre 基準／低／高 −0.09／−0.30／−0.09（Assumed；低端反映 2023–24 一次性重估，當時量小，證據最弱）。數值為工作單 W1 所列。",
         DEC_BY, "Cap_In N 節輸入列；Gov_Map 新列；DB_Evidence E398"),
    ]
    return [[f"SL49-{i + 1:02d}", V, f"v16.0 L 世代起點：{t}", txt, DATE, who, "v16.0 已建", where, f"{WO} W3-{i + 1}", "否"]
            for i, (t, txt, who, where) in enumerate(D)]


EV_COMMON = "讀取者：chat 端（" + WO + "）｜Andy 2026-10-18 10:20／10:24（見 Decisions SL49-01）；數值為 chat 端建議，可撤回"
EVIDENCE = [
    ("E398", "世代服務起點 s_v 的依據：雲端供應日期 H100 2023-03-21、GB200 2025-02-04、GB300 2025-07-03、VR200 2026-09-30（Cap_In 第 272–274 列已登錄）；OpenAI 機隊放量取其後；Hopper 機隊多在 2023 年中至 2024 年建成",
     "Cap_In 第 272–274 列（v7.0 世代價格 A 段已登錄；docs/reports/20261015_世代價格A_查證.md 第 5 節）；不新增外部來源", "Analogy（單一樣本）／Assumed（s_v 推定）",
     "Cap_In N 節 s_v（基準／低／高）、錨點年 A、g_pre", "—", "s_v 基準 2023.5／2025.0／2025.5／2026.75；低 2023.0／2025.0／2025.5／2026.75；高 2024.0／2025.5／2025.6／2027.0；A 2025.5；g_pre −0.09／−0.30／−0.09",
     "採用（W1；不新增來源）", "s_v 為推定值，非一手資料；OpenAI 各世代放量時間無公開資料；Hopper 錨點前跌價證據最弱（2023–24 一次性重估，當時量小）", "L1_LTotalFleetV*；L1_LTotalV（Cap_In N 節）；不改任何既有 IF_／L1_ 值", "—"),
]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    have = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
    n = 0
    for (eid, claim, src, mark, param, cur, new, verdict, note, affected, stance) in EVIDENCE:
        if eid in have:
            continue
        vals = [eid, DATE, claim, src, mark, param, cur, new, verdict, V, note + "｜" + EV_COMMON, "已處理", "—", "—", affected, "—", stance,
                f"{verdict}｜v16.0 新增列（非 106 列積壓）"]
        for i, v in enumerate(vals):
            put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 17))
        r += 1; n += 1
    return n


def purpose_marks(wb):
    ws = wb["Cap_In"]
    pc = v1400._purpose_col(ws, create=False)
    assert pc is not None, "用途 column of Cap_In not found"
    for rr, txt in PURPOSE_MARKS.items():
        put(ws, f"{L(pc)}{rr}", txt, F_NOTE)
    return len(PURPOSE_MARKS)


def clear_l1_ratio(wb):
    """L1 column O (推算 ÷ 外部) has no external value on the four new rows: cleared like the other external-less rows (v10.1 L1_O_ROWS), so they are not dead formula cells."""
    ws = wb["L1"]; n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value in ("L1_LTotalFleetV", "L1_LTotalV", "L1_LTotalDisc", "L1_LReqFleet_IdNoK") and ws[f"O{r}"].value is not None:
            ws[f"O{r}"].value = None; n += 1
    return n


def apply(wb, append_text):
    log = {}
    log["l1_o_cleared"] = clear_l1_ratio(wb)
    log["purpose"] = purpose_marks(wb)
    log["p89"] = l1_p89(wb)
    log["evidence"] = evidence_append(wb)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == "SL49-01" for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README
README_VERSION = (VERSION + "（主版：" + WO + "——L 按世代起點計算：新增 Cap_In N 節『L 世代起點』（世代服務起點 s_v、錨點年 A＝2025.5、錨點前牌價年變化率 g_pre）與契約名稱 "
                  "L1_LTotalFleetV／_Lo／_Hi（機隊 L，世代起點）、L1_LTotalV（各世代 L，4 格）、L1_LTotalDisc／_Lo／_Hi（折現版對照）、L1_LReqFleet_IdNoK／_Lo／_Hi（不含 κ 所需 L 對照）；"
                  "回本判讀（Cap_In 第 242 列、L1 第 89 列）改讀 L1_LTotalFleetV，v15.3 口徑保留為對照；Decisions SL49-01…04；DB_Evidence E398。既有名稱的值全部不變。）以下為 "
                  + v1530.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1530.README_TITLE
README_TITLE = V + _T[len(v1530.V):]
README_ROW = ("v16.0 L 世代起點",
              "L＝某世代硬體在壽命期 T 內，token 單價相對該世代起點單價的平均（跌價＋降級）；每個世代從自己的起點算，2025 年只是校準錨點（Andy 2026-10-18）。新增 Cap_In N 節與 L1_LTotalFleetV／LTotalV／LTotalDisc／LReqFleet_IdNoK；"
              "回本判讀改讀 L1_LTotalFleetV（基準仍為『未定』）。現行 L1_LTotal（新世代、起點＝第 0 年）保留不改。細節見 Decisions SL49-01…04。")

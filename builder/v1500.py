# v15.0 (work order docs/workorders/20261017_v14.3_稽核結案.md r1, branch claude/v14-3): audit close-out (O1–O22 as default, Andy 2026-10-17 13:39) + T3 (O4／O5, Andy 13:52).
# MAJOR version (CLAUDE.md section 4): new contract names — RNG_Dem004_* (O13), IF_FrontSuccVRQual (B11), RNG_<12 names>_Lo／_Hi (T3-2 VR200 ranges).  No existing IF_／IFW_／L1_ base value and no existing RNG_* endpoint changes.
#   T1-1 O13  SRC_DEM_004_Lo／_Hi enter the spend route: Alloc section Q (formulas) -> RNG_Dem004_IF_AllocServeGW／IF_AllocQ1／IF_AllocQ2 _Lo／_Hi (+ RNG_Dem004_OutCount, Checks RG4).
#   T1-2 O14  L1 external comparison rows 31, 59–65 put on the model's unit (formulas; D column untouched); row 35 annotated (unit already $B/GW/yr; remaining gap is definitional).
#   T1-3 O15  B11 guard flag IF_FrontSuccVRQual; B20 caliber labels (no number moves); Y9 sensitivity endpoints; F16 annotation; the other small items recorded as kept (Decisions).
#   T1-4 O9   V16 -> identity (not a verification).  T1-5 O6  SRC_Index sentinel rows labelled by formula.  T1-6 O20  kappa derivation block (display) on Alloc_In + Checks KP row.
#   T2        Decisions SL46-*.   T3-1 O5  SRC_PERF_060 register correction (revision 9: original wording kept).   T3-2 O4  VR200 batch-multiplier ranges (builder/v1300_ranges.json, tools/gen_ranges.py).
# Every write to an Excel-owned cell is guarded (old value / old text).
from copy import copy
import re

from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY, section
import v1000
import v1300
import v1400
import v1410
import v1420

VERSION = "20261017_Tokenomics_v15.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-17"
V = "v15.0"
WO = "工作單 docs/workorders/20261017_v14.3_稽核結案.md（r1）"
DEC_BY = ("Andy 2026-10-17 13:39（回覆『照預設』：對帳報告 docs/reports/20261017_稽核結案對帳.md 第 4 節 O1–O22 全部採建議預設）；"
          "O4、O5：Andy 2026-10-17 13:52（回覆『照建議』：docs/reports/20261017_查證_O4O5.md）")
REP = "docs/reports/20261017_稽核結案對帳.md"
REP_NEW = "docs/reports/20261017_v14.3_稽核結案.md"
TOL = "1E-9"


def _purpose_col(ws):
    return v1400._purpose_col(ws, create=False)


def _norm(s):
    return str(s).replace("1E+9", "1000000000").replace("1e9", "1000000000").replace("1E9", "1000000000")


def _set_guarded(cell, old, new):
    """Write `new` only while the cell still holds `old` (or already holds `new`)."""
    if cell.value == new:
        return 0
    assert cell.value == old, (cell.parent.title, cell.coordinate, cell.value, old)
    cell.value = new
    return 1


# ================================================================== T1-1 O13: SRC_DEM_004 range on the spend route (Alloc section Q, Excel formulas)
Q_TITLE = ("Q. 推論支出區間（v15.0 O13，工作單 r1 T1-1）：SRC_DEM_004_Lo／_Hi（OpenAI 端推論支出 $B 的來源區間）接進支出路線——"
           "服務 GW（IF_AllocServeGW）、Q1（IF_AllocQ1）、Q2（IF_AllocQ2）各取低／高端。全部是公式（隨 SRC_DEM_004 區間即時更新，不是貼值）；"
           "RNG_Dem004_<名稱>_Lo／_Hi＝兩個端點每格的較小／較大者（支出高則服務 GW 高、Q1／Q2 低，故不是『來源低端』對『名稱低端』）。"
           "這是『推論支出』一條軸的區間，與 O 節的批次口徑倍數區間是兩條不同的軸，兩者沒有合併（基準的 RDGW 在本節不變）。基準值不變。")
Q_ROWS = [  # key, label, unit, formula
    ("den", "服務持有成本分母 Σ（世代占比 × 各世代持有成本）", "$B/GW/年", "=SUMPRODUCT(AL_ShareGen,AL_HoldGen)"),
    ("srv_a", "服務 GW @ SRC_DEM_004_Lo（支出低端）", "GW", '=IF(AL_ServeGW="整代不可達","整代不可達",SRC_DEM_004_Lo/{den})'),
    ("srv_b", "服務 GW @ SRC_DEM_004_Hi（支出高端）", "GW", '=IF(AL_ServeGW="整代不可達","整代不可達",SRC_DEM_004_Hi/{den})'),
    ("q1_a", "Q1（R1）@ 支出低端", "%", '=IF(AL_ServeGW="整代不可達","整代不可達",IF(AND(ISNUMBER({srv_a}),ISNUMBER(AL_RDGW)),AL_RDGW/(AL_RDGW+{srv_a}),"SLO 不可達"))'),
    ("q1_b", "Q1（R1）@ 支出高端", "%", '=IF(AL_ServeGW="整代不可達","整代不可達",IF(AND(ISNUMBER({srv_b}),ISNUMBER(AL_RDGW)),AL_RDGW/(AL_RDGW+{srv_b}),"SLO 不可達"))'),
    ("q2_a", "Q2 @ 支出低端", "%", '=IF(AL_ServeGW="整代不可達","整代不可達",IF(AND(ISNUMBER({srv_a}),ISNUMBER(AL_RDGW)),AL_RDGW*AL_HoldTrain/(AL_RDGW*AL_HoldTrain+{srv_a}*{den}),"SLO 不可達"))'),
    ("q2_b", "Q2 @ 支出高端", "%", '=IF(AL_ServeGW="整代不可達","整代不可達",IF(AND(ISNUMBER({srv_b}),ISNUMBER(AL_RDGW)),AL_RDGW*AL_HoldTrain/(AL_RDGW*AL_HoldTrain+{srv_b}*{den}),"SLO 不可達"))'),
]
Q_NAMES = (("IF_AllocServeGW", "srv"), ("IF_AllocQ1", "q1"), ("IF_AllocQ2", "q2"))


def o13_alloc_q(wb):
    ws = wb["Alloc"]
    if any(str(ws.cell(r, 1).value or "").startswith("Q. 推論支出區間") for r in range(1, ws.max_row + 1)):
        return {}
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, Q_TITLE, 18)
    r = r0 + 1
    at = {}
    for key, lab, unit, f in Q_ROWS:
        at[key] = f"C{r}"
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        put(ws, f"C{r}", f.format(**at), F_CALC)
        r += 1
    r += 1
    put(ws, f"A{r}", "區間端點（名稱）", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD); put(ws, f"C{r}", "值", F_BOLD)
    put(ws, f"D{r}", "對照：基準（Interface）", F_BOLD); put(ws, f"E{r}", "基準落在區間外（1＝是）", F_BOLD)
    r += 1
    out_cells = []
    for nm, k in Q_NAMES:
        a, b = at[f"{k}_a"], at[f"{k}_b"]
        unit = "GW" if k == "srv" else "%"
        for tag, fn in (("Lo", "MIN"), ("Hi", "MAX")):
            put(ws, f"A{r}", f"RNG_Dem004_{nm}_{tag}"); put(ws, f"B{r}", unit)
            put(ws, f"C{r}", f"=IF(AND(ISNUMBER({a}),ISNUMBER({b})),{fn}({a},{b}),{a})", F_CALC)
            wb.defined_names[f"RNG_Dem004_{nm}_{tag}"] = DefinedName(f"RNG_Dem004_{nm}_{tag}", attr_text=f"Alloc!$C${r}")
            if tag == "Lo":
                rl = r
            else:
                put(ws, f"D{r}", f"={nm}", F_LINK)
                put(ws, f"E{r}", f'=IF(AND(ISNUMBER(D{r}),ISNUMBER(C{rl}),ISNUMBER(C{r})),IF(OR(D{r}<C{rl}-{TOL}*ABS(C{rl})-1E-12,D{r}>C{r}+{TOL}*ABS(C{r})+1E-12),1,0),0)', F_CALC, fmt="0")
                out_cells.append(f"E{r}")
            r += 1
    put(ws, f"A{r}", "基準落在區間外的格數（三個名稱合計）", F_BOLD)
    put(ws, f"C{r}", "=" + "+".join(out_cells), F_CALC, fmt="0")
    put(ws, f"D{r}", "RNG_Dem004_OutCount：不為 0＝SRC_DEM_004 的低／高端不再涵蓋基準（Checks RG4，WARN）", F_NOTE)
    wb.defined_names["RNG_Dem004_OutCount"] = DefinedName("RNG_Dem004_OutCount", attr_text=f"Alloc!$C${r}")
    return {"row0": r0, "out_row": r, "den": at["den"]}


def o13_checks_rg4(wb):
    ws = wb["Checks"]
    if any(ws.cell(r, 1).value == "RG4" for r in range(1, ws.max_row + 1)):
        return 0
    r3 = next(r for r in range(1, ws.max_row + 1) if ws.cell(r, 1).value == "RG3")
    r4 = r3 + 1
    assert ws.cell(r4, 1).value in (None, ""), (r4, ws.cell(r4, 1).value)
    put(ws, f"A{r4}", "RG4")
    put(ws, f"B{r4}", "推論支出區間（SRC_DEM_004_Lo／_Hi；Alloc Q 節）：IF_AllocServeGW／IF_AllocQ1／IF_AllocQ2 任一基準落在 RNG_Dem004_*_Lo／_Hi 之外：1＝是（容差 1e-9）", wrap=True)
    put(ws, f"C{r4}", "WARN")
    put(ws, f"D{r4}", "=IF(RNG_Dem004_OutCount>0,1,0)", F_CALC, fmt="0")
    put(ws, f"E{r4}", "RNG_Dem004_OutCount；Alloc Q 節（公式區間，沒有指紋：來源區間改動時端點即時更新）", F_NOTE)
    ref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    f = str(cell.value)
    if f"D{r4}" not in f:
        cell.value = f + f"+D{r4}"
    lab = ws[f"B{int(ref[1:])}"]
    if "RG4" not in str(lab.value):
        lab.value = str(lab.value).replace("、RG1、RG2、RG3）", "、RG1、RG2、RG3、RG4）") if "、RG1、RG2、RG3）" in str(lab.value) else f"{lab.value}、RG4"
    return 1


# ================================================================== T1-2 O14: L1 external comparison on the model's unit
L1_ROWS = {
    31: ("=SRC_PRC_002", "=SRC_PRC_002*SRC_PRC_047",
         "；v15.0 O14：外部租金門檻（85% 利用率）乘 SRC_PRC_047（0.85）換算為 100% 時數口徑後再與本模型（100% 時數持有成本）比；原外部值 SRC_PRC_002 未換算＝3.57（比值 0.715）。9.12% 資金成本與 6 年折舊兩個前提仍未對齊"),
    59: ("=SRC_PERF_024/SRC_PERF_025", "=SRC_PERF_024/SRC_PERF_025*INDEX(IF_RacksPerGW,1,8)/INDEX(IF_RacksPerGW,1,5)",
         "；v15.0 O14：外部是 72 GPU 整架 tok/s 比，已乘（GB300 ÷ GB200 的每 GW 機架數比，IF_RacksPerGW）換成每 GW 比再比；原未換算外部比＝1.0429。換算後仍與模型有差距屬實質差異（MLPerf interactive 單點對模型 Sol 參考請求），不是單位問題"),
    60: ("=SRC_PERF_027/SRC_PERF_028", "=SRC_PERF_027/SRC_PERF_028*INDEX(IF_RacksPerGW,1,11)/INDEX(IF_RacksPerGW,1,8)",
         "；v15.0 O14：外部是 72 GPU 整架 tok/s 比，已乘（VR200 ÷ GB300 的每 GW 機架數比，IF_RacksPerGW）換成每 GW 比再比；原未換算外部比＝2.5749"),
}
HAR_G = "INDEX(IF_CostDec_Sol,1,11)/INDEX(IF_CostDec_Sol,1,8)"
HAR_OLD = "=SRC_HAR_006/SRC_HAR_004"
HAR_NEW = f'=IF(AND(ISNUMBER(INDEX(IF_CostDec_Sol,1,11)),ISNUMBER(INDEX(IF_CostDec_Sol,1,8))),SRC_HAR_006/SRC_HAR_004/({HAR_G}),"—")'
HAR_NOTE = ("；v15.0 O14：外部（ARC-AGI-3 Adapter ÷ 標準成本比）只含 harness 效果、未除以世代比；本列模型值是『harness 比 ÷ 世代比』，"
            "外部值已同樣除以（VR200 ÷ GB300 decode $/M，Sol）後再比（即比較 harness 比本身）；原外部值 SRC_HAR_006 ÷ SRC_HAR_004＝0.6641")
R35_NOTE = ("；v15.0 O14：單位已一致（外部＝2025 營收 ÷ 平均總 GW；模型＝1 GW 參考機隊付費營收，皆 $B/GW/年），不改公式與基準。"
            "剩餘差異是定義差：Hopper 占比 0.57（Checks 對帳常數）對 0.60（Alloc_In）、理論上限（理想）對實際營收；見 Decisions SL46-02")


def o14_l1(wb, append_text):
    ws = wb["L1"]
    n = 0
    for r, (old, new, note) in L1_ROWS.items():
        assert str(ws[f"A{r}"].value).startswith("L1_"), (r, ws[f"A{r}"].value)
        for c in "MN":
            n += _set_guarded(ws[f"{c}{r}"], old, new)
        n += append_text(ws[f"S{r}"], note)
    for r in range(61, 66):
        assert str(ws[f"A{r}"].value).startswith("L1_HarVsGen_"), (r, ws[f"A{r}"].value)
        for c in "MN":
            n += _set_guarded(ws[f"{c}{r}"], HAR_OLD, HAR_NEW)
        n += append_text(ws[f"S{r}"], HAR_NOTE)
    assert ws["A35"].value == "L1_RevGWFleet_OAI2025"
    n += append_text(ws["S35"], R35_NOTE)
    return n


SRC_NEW = [
    v1000._rec("SRC_PRC_047", "SRC_Price", "新雲損益兩平租金的利用率前提（Cape Fear；SRC_PRC_002 的 85%）", 0.85, None, None, "x（時數利用率）",
               "與 SRC_PRC_002 同一計算前提：85% 利用率、9.12% 資金成本、6 年", "機型未明（同 SRC_PRC_002）", "2026-09", "capefearadvisors.substack.com（同 SRC_PRC_002）",
               2, "中立", "獨立部落客推算的前提參數，非實測；與 SRC_PRC_002 同源，無獨立第二來源", "一手（作者自算）",
               "L1 第 31 列外部對照（v15.0 O14：把外部租金換算為 100% 時數口徑）",
               "v15.0 O14 新增：把 SRC_PRC_002 口徑欄已公開的 85% 拆成可引用的數值紀錄（無新證據；Evidence 沿用 E149）；不改 SRC_PRC_002"),
]
SRC_NEW[0]["ev"] = "E149"
SRC_NEW[0]["s"] = "U-V1500"


def src_new_records():
    return SRC_NEW


# ================================================================== T1-3 O15 B part
def b11_guard(wb, append_text):
    ws = wb["Interface"]
    n = 0
    if ws["A193"].value in (None, ""):
        assert ws["A194"].value.startswith("F. Block 6"), ws["A194"].value
        src = {c.column_letter: c for c in ws[192] if c.value is not None}
        put(ws, "A193", "VR200 前緣是否有合格組合（1＝有；0＝無合格：IF_FrontSuccVR／Name／P 回傳『無合格』文字；下游讀前緣前先看本列；v15.0 B11 守衛）　[IF_FrontSuccVRQual]")
        put(ws, "B193", "旗標")
        for c in "CDEFG":
            put(ws, f"{c}193", f"=IF(ISNUMBER({c}190),1,0)", F_CALC, fmt="0")
        for col, cell in src.items():
            if col in "RSTUVW":
                v = cell.value
                if isinstance(v, str) and v.startswith("="):
                    v = re.sub(r"(?<![A-Z$])([A-Z])192(?![0-9])", r"\g<1>193", v)
                ws[f"{col}193"].value = v
                ws[f"{col}193"].font = copy(cell.font); ws[f"{col}193"].number_format = cell.number_format
                ws[f"{col}193"].alignment = copy(cell.alignment); ws[f"{col}193"].fill = copy(cell.fill)
        for col in "ABCDEFG":
            ws[f"{col}193"].fill = copy(ws[f"{col}192"].fill)
        n += 1
    wb.defined_names["IF_FrontSuccVRQual"] = DefinedName("IF_FrontSuccVRQual", attr_text="Interface!$C$193:$G$193")
    hs = wb["Harness"]
    for r in (151, 152, 153):
        n += append_text(hs[f"{_note_col(hs)}{r}"], "；v15.0 B11：可靠度下限 p_min 高到沒有組合合格時，本列回『無合格』文字（原行為不變）；數值或文字的判斷請先讀 Interface 第 193 列 IF_FrontSuccVRQual（1＝有合格組合，0＝無）")
    return n


def _note_col(ws):
    pc = _purpose_col(ws)
    return L(pc) if pc else "J"


B20_NOTE = ("；v15.0 B20 口徑：本列只計『生成 decode』的 GPU 小時（Perf_Batch 第 103 列，SLO 批次下 decode GPU 秒／M × token），"
            "不含 prefill（提示詞）與參考模型前向；屬推論型計價（不是訓練 MFU 計價）。若要含 prefill 或改以訓練 MFU 計價，會改變數值，列待 Project 判斷（Decisions SL46-04）")
B20_NOTE74 = "；v15.0 B20 口徑：本列『推論型』標籤下以 trainer GPU 小時 ÷ 3（訓練 MFU 折回前向）計價，與第 97、100 列的 decode 計價不同口徑；基準為 0（Train_In C10＝0 關閉），保留不改（Decisions SL46-04）"


def b20_labels(wb, append_text):
    ws = wb["Training"]
    n = 0
    for r, txt in ((74, B20_NOTE74), (97, B20_NOTE), (100, B20_NOTE)):
        n += append_text(ws[f"R{r}"], txt)
    return n


Y9_OLD_ROW13 = {"E": 0.15, "F": 0.15, "G": 0.4, "H": 0.4}
Y9_NEW_ROW13 = {"E": 0.18, "F": 0.18, "G": 0.35, "H": 0.35}


def y9_sens(wb, append_text):
    n = 0
    sr = wb["Sens_Rev"]
    assert sr["A8"].value == "折扣 10%" or str(sr["A8"].value).startswith("="), sr["A8"].value
    n += _set_guarded(sr["B8"], 0.1, "=Cap_In!D12") if sr["B8"].value == 0.1 else 0
    if sr["B9"].value == 0.3:
        sr["B9"].value = "=Cap_In!E12"; n += 1
    for r in (8, 9):
        if sr[f"B{r}"].value != f"=Cap_In!{'D' if r == 8 else 'E'}12":
            continue
        sr[f"A{r}"].value = f'="折扣 "&TEXT(B{r},"0%")'
    st = wb["Sens_Train"]
    for c, old in Y9_OLD_ROW13.items():
        cell = st[f"{c}13"]
        if cell.value == old:
            cell.value = Y9_NEW_ROW13[c]; n += 1
        else:
            assert cell.value == Y9_NEW_ROW13[c], (c, cell.value)
    for c, old, new in (("E3", "預訓練 MFU 基準 0.15", "預訓練 MFU 基準 0.18"), ("G3", "預訓練 MFU 基準 0.40", "預訓練 MFU 基準 0.35")):
        if st[c].value == old:
            st[c].value = new; n += 1
        else:
            assert st[c].value == new, (c, st[c].value)
    n += append_text(st["A2"], "；v15.0 Y9：第 13 列『預訓練 MFU 基準』低／高端由 0.15／0.40 改為 0.18／0.35（Gov_Map GM519 區間，Andy 2026-10-03 確認；原值見 Decisions SL46-05）；Sens_Rev 折扣 10%／30% 兩列改連結 Cap_In D12／E12（0.1／0.4，原高端 0.3）")
    return n


F16_NOTE = ("；v15.0 F16：低／高欄是『多個輸入同時取端點』的角落組合（每則提示 token × 免費占比同向取極值），是包絡（最寬情形），不是機率區間；"
            "改成獨立加總或逐輸入敏感度會改數值，列待 Project 判斷（Decisions SL46-06）")


def f16_note(wb, append_text):
    ws = wb["Cap_In"]
    assert str(ws["A81"].value).startswith("(i) 模型 token：ChatGPT 付費 token")
    return append_text(ws["G81"], F16_NOTE)


# ================================================================== T1-4 O9: V16 identity
V16_B = "【恆等式（非驗證）；v15.0 O9】"
V16_J = ("v15.0 O9（Andy 2026-10-17 13:39 照預設）：比照 V23、V24 標『恆等式（非驗證）』並移出驗證計數（22 → 21）。理由：能量閉合比是物理下限功率 ÷ 機架平均用電，"
         "基準 0.085 距門檻 1 很遠，輸入在合理範圍內改變無法使其失敗（結構上近似恆成立），不符合 D5『驗證必須能失敗』；原 v10.2 E3『改回驗證計數』的判斷由本筆取代（原文保留在本欄前段）")
V16_F_OLD = '=IF(AND(ISNUMBER(E164),ISNUMBER(H164)),IF(AND(E164>=H164,IF(ISNUMBER(I164),E164<=I164,TRUE)),1,0),"—")'
V16_F_NEW = '=IF(AND(ISNUMBER(E164),ISNUMBER(H164)),IF(AND(E164>=H164,IF(ISNUMBER(I164),E164<=I164,TRUE())),"恆等式（非驗證）","恆等式不成立"),"—")'


def o9_v16(wb, append_text):
    ws = wb["Checks"]
    assert ws["A164"].value == "V16", ws["A164"].value
    n = _set_guarded(ws["F164"], V16_F_OLD, V16_F_NEW)
    if ws["G164"].value == "驗證":
        ws["G164"].value = "恆等式（非驗證）"; n += 1
    else:
        assert ws["G164"].value == "恆等式（非驗證）", ws["G164"].value
    n += append_text(ws["B164"], V16_B)
    n += append_text(ws["J164"], "｜" + V16_J)
    assert str(ws["A143"].value).startswith("判準寫在 H"), ws["A143"].value
    n += append_text(ws["A143"], "｜v15.0 O9：V16 亦為恆等式（非驗證），F 欄為文字，不計入驗證項目數（驗證計數 22 → 21）")
    return n


# ================================================================== T1-5 O6: SRC_Index sentinel rows labelled by formula
O6_NOTE = "；v15.0 O6：哨兵列 B 欄改為公式標示：此列的 SRC_ID 若已在上方 SRC 頁，標『已在上方 SRC 頁，查詢不會命中本列』；只有 SRC 頁查無的 ID 才是真哨兵（A、D、E 欄與 MATCH 結果不變）"


def o6_sentinel(wb, append_text):
    ws = wb["SRC_Index"]
    rows = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 2).value == "（哨兵）" or str(ws.cell(r, 2).value or "").startswith("=IF(A")]
    assert rows, "no sentinel rows"
    first = min(rows)
    n = 0
    for r in rows:
        f = (f'=IF(A{r}="","（哨兵：Gov_Map 該列無 SRC_ID）",IF(COUNTIF($A$5:$A${first - 1},A{r})>0,"（哨兵：此 SRC_ID 已在上方 SRC 頁，查詢不會命中本列）","（哨兵：SRC 頁查無此 ID）"))')
        if ws.cell(r, 2).value != f:
            ws.cell(r, 2).value = f; ws.cell(r, 2).font = copy(F_NOTE); n += 1
    n += append_text(ws["A2"], O6_NOTE)
    return n


# ================================================================== T1-6 O20: kappa derivation (display; reaches Checks KP row)
KAP_TITLE = ("κ 推導（v15.0 O20；顯示用，不連結 AL_Kappa；Derived）：v5.36A 第 3.2 節的方法在簿內重算——每請求 GPU 秒＝I×[(1−χ)×新鮮 prefill GPU 秒/M＋χ×快取命中 prefill GPU 秒/M]÷10^6＋O×decode GPU 秒/M÷10^6，"
             "容量＝(I＋O)÷每請求 GPU 秒，κ_i＝容量_i÷容量_參考（16,384＋2,048，χ＝Cap_In 快取命中 B4_CacheHit）；按需求 token 加權的調和平均＝1÷Σ(w_i÷κ_i)。"
             "GPU 秒/M 取 Sens_Perf 第 101–103 列 C 欄（Sol、VR200）；限制：prefill 單價固定於 ISL 16K（v5.36A 用 4K／16K 線性內插，簿內已無 4K 欄），短輸入的 prefill 成本略偏高。"
             "這是核對 AL_Kappa 基準 1.0（區間 0.65–1.2）的重算，不改 AL_Kappa；結果與區間比對見 Checks KP 列。")
KAP_TYPES = [  # label, I, O, chi (None -> B4_CacheHit), weight formula
    ("參考請求（16,384／2,048）", 16384, 2048, None, None),
    ("API（6,000／400，χ 0.55）", 6000, 400, 0.55, "AL_DAPI"),
    ("ChatGPT 付費（3,500／800，χ 0.8）", 3500, 800, 0.8, "AL_DChatPaid"),
    ("ChatGPT 免費（2,000／500，χ 0.8）", 2000, 500, 0.8, "AL_DChatFree"),
]


def o20_kappa(wb):
    ws = wb["Alloc_In"]
    if any(str(ws.cell(r, 1).value or "").startswith("κ 推導（v15.0 O20") for r in range(1, ws.max_row + 1)):
        return {}
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, KAP_TITLE, 10)
    r = r0 + 1
    for i, h in enumerate(["請求類型", "輸入 token I", "輸出 token O", "快取命中 χ", "需求 token（M tok/年）", "每請求 GPU 秒", "容量 tok/GPU 秒", "κ_i", "權重 w_i÷κ_i"]):
        put(ws, f"{L(i + 1)}{r}", h, F_BOLD, wrap=True)
    r += 1
    first = r
    ref = r
    for lab, I, O, chi, w in KAP_TYPES:
        put(ws, f"A{r}", lab)
        put(ws, f"B{r}", I, F_CALC); put(ws, f"C{r}", O, F_CALC)
        put(ws, f"D{r}", "=B4_CacheHit" if chi is None else chi, F_LINK if chi is None else F_CALC)
        put(ws, f"E{r}", f"={w}" if w else "—", F_LINK if w else F_CALC)
        put(ws, f"F{r}", f"=B{r}*((1-D{r})*Sens_Perf!$C$101+D{r}*Sens_Perf!$C$102)/1000000+C{r}*Sens_Perf!$C$103/1000000", F_CALC, fmt="0.000000")
        put(ws, f"G{r}", f"=(B{r}+C{r})/F{r}", F_CALC, fmt="#,##0")
        put(ws, f"H{r}", "（基準 1）" if r == ref else f"=G{r}/$G${ref}", F_NOTE if r == ref else F_CALC, fmt="0.000")
        put(ws, f"I{r}", f"=E{r}/H{r}" if w else "—", F_CALC, fmt="#,##0")
        r += 1
    last = r - 1
    put(ws, f"A{r}", "κ 重算值（需求加權調和平均＝Σw ÷ Σ(w÷κ_i)）", F_BOLD)
    put(ws, f"H{r}", f"=SUM(E{first + 1}:E{last})/SUM(I{first + 1}:I{last})", F_CALC, fmt="0.000")
    put(ws, f"I{r}", "重算值對 AL_Kappa 區間：", F_NOTE)
    r_kap = r
    r += 1
    put(ws, f"A{r}", "重算值落在 AL_Kappa 區間（0.65–1.2）內？（1＝是）", F_BOLD)
    put(ws, f"H{r}", f"=IF(AND(H{r_kap}>=AL_Kappa_Lo,H{r_kap}<=AL_Kappa_Hi),1,0)", F_CALC, fmt="0")
    r_in = r
    put(ws, f"A{r + 1}", "輸入欄 I、O、χ（黑字常數：方法常數，不是模型輸入，不登錄藍字輸入；改動請走工作單）取自 v5.36A 第 3.2 節的請求類型表（Analogy：OpenRouter／無伺服器平台追蹤、v5.33A 五組成基準）；權重為簿內 Alloc 第 5–7 列需求 token。v5.36A 的 1.035 所用 GW 權重未存於簿內，本表以需求 token 權重重算，數值可能與 1.035 不同。", F_NOTE)
    wb.defined_names["AL_KappaCalc"] = DefinedName("AL_KappaCalc", attr_text=f"Alloc_In!$H${r_kap}")
    wb.defined_names["AL_KappaCalcIn"] = DefinedName("AL_KappaCalcIn", attr_text=f"Alloc_In!$H${r_in}")
    return {"row0": r0, "kap_row": r_kap, "in_row": r_in}


def o20_checks_kp(wb):
    ws = wb["Checks"]
    if any(ws.cell(r, 1).value == "KP" for r in range(1, ws.max_row + 1)):
        return 0
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "KP. κ 重算對照（v15.0 O20；顯示用，不計入 GOV_*）：Alloc_In 的 κ 推導區塊重算值對 AL_Kappa（基準 1.0）與其區間", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "值", "說明"]): put(ws, f"{L(i + 1)}{r}", h, F_BOLD)
    r += 1
    put(ws, f"A{r}", "KP1"); put(ws, f"B{r}", "κ 重算值 ÷ AL_Kappa（基準）", wrap=True); put(ws, f"C{r}", "INFO")
    put(ws, f"D{r}", "=AL_KappaCalc/AL_Kappa", F_CALC, fmt="0.000"); put(ws, f"E{r}", "Alloc_In κ 推導區塊；不改 AL_Kappa", F_NOTE); r += 1
    put(ws, f"A{r}", "KP2"); put(ws, f"B{r}", "κ 重算值落在 AL_Kappa 區間內（1＝是）", wrap=True); put(ws, f"C{r}", "INFO")
    put(ws, f"D{r}", "=AL_KappaCalcIn", F_CALC, fmt="0"); put(ws, f"E{r}", "0＝重算值在 0.65–1.2 之外，須由 Project 判斷是否更新 AL_Kappa", F_NOTE)
    return 1


# ================================================================== T2: O8／O12 labels (Hopper lower bound; fleet-share caliber)
O8_NOTE = "；v15.0 O8：Hopper 吞吐為保守下界（獨立對照 V7、V8、V15 顯示模型約為實測 0.26–0.27 倍；Hopper η 倍數無獨立依據，Decisions SL46-13）；對外引用 Hopper 欄請標『保守下界』"
O8_IF_A2 = "；v15.0 O8：Hopper 欄的吞吐與營收為保守下界（模型約為獨立實測的 0.26–0.27 倍，V7、V8、V15 失敗已揭露；Decisions SL46-13）"
O12_TAG = ("｜v15.0 O12 口徑：機隊占比取 2025 OpenAI 推論 ÷（推論＋訓練）支出比（B4_Serve×(1−B4_Free)，全部世代同值，Assumed）；"
           "訓練成本以 100% 利用率計、服務以 ÷IF_Util 計；縮放倍數與隱含家族計畫數為 Assumed，接受為決策（Decisions SL46-16）")
O12_ROWS = {"Fleet_1GW": (10, 12, 13, 33, 34), "Amortize": (41,),
            "Interface": (98, 100, 116, 118, 134, 136, 140, 141, 142, 144, 145, 146, 248, 249, 268)}


def o8_o12_labels(wb, append_text):
    n = 0
    for sh, rows in O12_ROWS.items():
        ws = wb[sh]
        for r in rows:
            assert ws[f"A{r}"].value not in (None, ""), (sh, r)
            n += append_text(ws[f"A{r}"], O12_TAG)
    ci = wb["Cap_In"]
    for r in (28, 29, 31, 32):
        assert ci[f"A{r}"].value not in (None, ""), r
        n += append_text(ci[f"G{r}"], O12_TAG)
    cal = wb["Calib"]
    for r in (5, 67):
        n += append_text(cal[f"J{r}"], O8_NOTE)
    n += append_text(wb["Interface"]["A2"], O8_IF_A2)
    return n


# ================================================================== T3-1 O5: SRC_PERF_060 register correction (revision 9: original wording kept)
O5_URL = "https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut"
O5_TAIL = ("｜v15.0 更正（修訂九，Decisions SL46-23）：原出處欄＝『{j}』；原一手／二手欄＝『{n}』；原立場說明＝『{m}』；原口徑欄＝『{g}』。"
           "回查結果（docs/reports/20261017_查證_O4O5.md）：數字 556 在 NVIDIA 技術部落格表 2（DGX H200，8 GPU，Server，DeepSeek-R1）找到，非 MLCommons 正式結果，"
           "NVIDIA 表下註明 Hopper results not verified by MLCommons Association；『待回查』結案")
O5_NEW = dict(
    J=O5_URL + "（表 2：DGX H200，Server，556 tok/s/GPU；MLPerf v5.1 Closed 規則下 NVIDIA 自測；2026-10-17 已讀原文）",
    N="一手（已讀；NVIDIA 技術部落格；非 MLCommons 提交）",
    M="Interested-party：NVIDIA 自測，未經 MLCommons 驗證；NVIDIA 是 Blackwell 的賣方，此表用途是凸顯 Blackwell 相對 Hopper 的倍數，誘因偏向壓低舊世代數字（若 556 偏低，V1 比值偏高）",
    G="server；MLPerf v5.1 Closed 規則下 NVIDIA 自測；NVIDIA 註明 Hopper 結果未經 MLCommons 驗證（非 MLCommons 稽核結果）",
)


def t3_src060(wb, append_text):
    ws = wb["SRC_Perf"]
    r = next(x for x in range(5, ws.max_row + 1) if ws.cell(x, 1).value == "SRC_PERF_060")
    n = 0
    note = ws[f"W{r}"]
    if "v15.0 更正" not in str(note.value or ""):
        old = {k: ws[f"{k}{r}"].value for k in "JNMG"}
        assert old["N"] == "二手（3A 查證轉引）", old["N"]
        tail = O5_TAIL.format(j=old["J"], n=old["N"], m=old["M"], g=old["G"])
        for k, v in O5_NEW.items():
            ws[f"{k}{r}"].value = v; n += 1
        note.value = f"{note.value}{tail}"; n += 1
    cal = wb["Calib"]
    old = "MLPerf（MLCommons 稽核）／NVIDIA 提交（v5.1；3A 查證轉引）"
    if cal["G121"].value == old:
        cal["G121"].value = "NVIDIA 自測（Interested-party；未經 MLCommons 驗證；NVIDIA 技術部落格表 2，v5.1 DGX H200）"; n += 1
        n += append_text(cal["J121"], "｜v15.0 更正（修訂九，Decisions SL46-23）：G121 原文＝『" + old + "』；SRC_PERF_060 實為 NVIDIA 自測值，非 MLCommons 稽核結果")
    ck = wb["Checks"]
    n += append_text(ck["J149"], "｜v15.0 更正：SRC_PERF_060＝556 已回查（NVIDIA 技術部落格表 2，非 MLCommons 結果；NVIDIA 自測未經驗證），上句『對照值未回查』結案；V1 判定不變（1.22，警示）；Decisions SL46-23")
    de = wb["DB_Evidence"]
    rr = next((x for x in range(5, de.max_row + 1) if de.cell(x, 1).value == "E384"), None)
    if rr:
        n += append_text(de[f"R{rr}"], "｜v15.0 回查結案：556 出自 NVIDIA 技術部落格表 2（非 MLCommons 提交）；欄 I、L 不改（CLAUDE.md 第 6 節），判定請 Project 於下一輪更新")
    return n


# ================================================================== T3-2 O4: VR200 range notes (original wording kept, correction appended)
VR_NOTE_A = ("｜v15.0 更正（修訂九，T3-2）：上列『本版區間只涵蓋 GB200／Hopper 倍數，未涵蓋 VR200 倍數』所指的 12 個名稱（L1_Ans5_FullMargin、L1_Ans6_GPUh、L1_RLshare_Astra_VR200、L1_RLshare_Sol_VR200 及各自的 _Lo／_Hi）"
             "v15.0 起已建 VR200 倍數區間（RNG_<名稱>_Lo／_Hi，本表 O 節）：端點＝VR200 倍數 0.70（Nebius）與 1.0（Assumed）兩個情境每格的較小／較大者，基準 0.75 在其內")
VR_NOTE_C = ("｜v15.0 更正（修訂九，T3-2）：『VR200 批次倍數無證據』不正確——有證據：MLPerf v6.1 offline 的 VR200 由 NVIDIA 與 Nebius 各一筆（皆 Interested-party、preview 類）；用 Calib L 節公式反推，相對 GB300 口徑得 0.70–0.76，"
             "與基準 0.75、Gov_Map GM595 區間 0.70–1.0 一致（docs/reports/20261017_查證_O4O5.md）。只經 VR200 欄的 12 個名稱已建區間；上述 36 個名稱（IF_ 的 15 格名稱）的 VR200 欄 108 格維持點值（既有端點不變，列待 Project 判斷）。"
             "結構風險：0.75 是相對 GB300（倍數 1，未校準）之值；若日後校準 GB300，VR200 須改絕對口徑（約 1.20–1.28），否則重複折減")
VR_NOTE_TITLE = "｜v15.0 T3-2：另有 12 個只經 VR200 欄的名稱（見下方（a）更正），端點＝VR200 倍數 0.70／1.0 兩個情境（tools/gen_ranges.py 的 vr200_lo／vr200_hi）每格較小／較大者"


def t3_vr_notes(wb, append_text):
    ws = wb["Alloc"]
    n = 0
    for r in range(1, ws.max_row + 1):
        s = str(ws.cell(r, 1).value or "")
        if s.startswith("O. 批次口徑倍數區間端點"):
            n += append_text(ws.cell(r, 1), VR_NOTE_TITLE)
        elif s.startswith("（a）只經 VR200 欄"):
            n += append_text(ws.cell(r, 1), VR_NOTE_A)
        elif s.startswith("（c）v13.1 P2-1：VR200 欄無區間"):
            n += append_text(ws.cell(r, 1), VR_NOTE_C)
    return n


# ================================================================== Decisions SL46-*
def _decisions():
    A = "Andy 2026-10-17 13:39 照預設"
    R = REP + " 第 4 節"
    D = [
        ("O13 推論支出區間 SRC_DEM_004_Lo／_Hi 接進支出路線",
         f"{A}（{R} O13，建議 B）。Alloc 新增 Q 節（全部 Excel 公式）：服務 GW @ SRC_DEM_004_Lo／_Hi、Q1、Q2 各兩端；新契約名稱 RNG_Dem004_IF_AllocServeGW／IF_AllocQ1／IF_AllocQ2 的 _Lo／_Hi（取兩端每格較小／較大者）與 RNG_Dem004_OutCount；Checks RG4（WARN，計入 GOV_Warnings，基準為 0）。"
         "基準值、既有 RNG_* 端點不變。這是『推論支出』一條軸；與 O 節批次倍數區間是不同的軸，未合併。未納入：IF_AllocQ1_R2（需另定免費占比隨支出的處理）與 L1_MFleet_Lo／Hi（m 的支出敏感度 +12%／−4.5% 仍在區間外），列待 Project 判斷。"
         "新舊值見 docs/reports/20261017_v14.3_稽核結案.md。", "Alloc Q 節；Checks RG4；RNG_Dem004_*"),
        ("O14 L1 外部對照換算為同一單位",
         f"{A}（{R} O14，建議 A）。L1 第 31 列外部租金 SRC_PRC_002（85% 利用率）× 新紀錄 SRC_PRC_047（0.85）換算為 100% 時數口徑；第 59、60 列外部整架 tok/s 比乘每 GW 機架數比（IF_RacksPerGW）換成每 GW 比；第 61–65 列外部 ARC 成本比除以世代比，與模型『harness 比 ÷ 世代比』同單位；"
         "第 35 列單位本來一致（$B/GW/年），只加註剩餘差異是定義差（Hopper 占比 0.57 對 0.60、理論上限對實際營收），不改。D 欄基準不變；M、N、O、P 欄與 S 欄說明隨之更新。新增 SRC_PRC_047（把 SRC_PRC_002 口徑欄已公開的 85% 拆成數值紀錄，無新證據，Evidence 沿用 E149）。", "L1 第 31、35、59–65 列；SRC_Price SRC_PRC_047"),
        ("O15 B11 前緣可靠度門檻守衛",
         f"{A}（{R} O15，建議 B）。Interface 第 193 列新增 IF_FrontSuccVRQual（1＝VR200 前緣有合格組合，0＝無合格；IF_FrontSuccVR／Name／P 在 0 時仍回『無合格』文字，原行為不變），下游讀前緣前先看此旗標。"
         "Harness 第 126／129／132 列（中嚴重度，p＝0 時每成功任務營收回 0）維持：沒有任何成功的任務其營收為 0 是定義，成本列回文字是因成本無定義，兩者語意不同，刻意保留。", "Interface 第 193 列；Harness 第 151–153 列說明"),
        ("O15 B20 合成資料、評測與參考模型前向的計價口徑",
         f"{A}（{R} O15，建議 B）。Training 第 97、100 列（合成資料、評測 GPU 小時）以 Perf_Batch 第 103 列的 decode GPU 秒／M 計價，只含 decode、不含 prefill；第 74 列（參考模型前向，基準關閉＝0）以訓練 MFU 折回前向計價。"
         "改為含 prefill 或統一計價會改變數值，故只標註口徑、不改機制；是否改列待 Project 判斷。", "Training 第 74、97、100 列 R 欄"),
        ("O15 Y9 敏感度端點跟隨輸入",
         f"{A}（{R} O15，建議 B）。Sens_Rev 折扣兩列改連結 Cap_In D12／E12（0.1／0.4）：原『折扣 30%』（B9＝0.3）→ 現隨 Cap_In 高端 0.4；標籤改為公式。Sens_Train 第 13 列『預訓練 MFU 基準』低／高端 E–H 欄由 0.15／0.40 改為 0.18／0.35"
         "（Gov_Map GM519 區間，Claude 提議、Andy 2026-10-03 確認；原值 0.15／0.15／0.40／0.40，標籤 E3『預訓練 MFU 基準 0.15』、G3『預訓練 MFU 基準 0.40』）。Train_In H6 說明仍寫『區間 0.15–0.40』（Excel 擁有，未改），與 Gov_Map 不一致，列待 Project 判斷。"
         "這些是敏感度頁的情境端點，不在 IF_／IFW_／L1_ 基準路徑上（依賴圖：下游契約名稱 0 個）。", "Sens_Rev B8／B9／A8／A9；Sens_Train E13:H13、E3、G3"),
        ("O15 F16 Cap_In 第 81 列角落組合",
         f"{A}（{R} O15）。第 81 列低／高欄是『每則提示 token × 免費占比同向取端點』的角落組合（包絡，非機率區間）。標註於 Cap_In G81；改成獨立加總會改數值，列待 Project 判斷。", "Cap_In G81"),
        ("O15 其餘小項記為刻意保留",
         f"{A}（{R} O15，建議：其餘 A）。逐項理由——G10 Cache_Store 不套 H_KV：基準影響 0，啟用 KV 壓縮技術時才有差；G12 tok/J 以平均用電口徑：影響 IF_TokPerJ_* +14%／−11%，口徑已於 Perf!A117 標示；"
         "G16 任務 token 與參考請求兩套定義：兩者用途不同（任務成本 vs 容量），換算需新機制；G18 Price_Frontier!C24 以位置取列：目前列序固定，改列序時測試會抓到；G19 IF_MaintIT 同時進會計口徑：註記性，不影響數值；"
         "G21 每專家參數假設 61 層全 MoE：只影響 MLPerf 對照（H 節）；G22 Tech_Registry 無 P≤0 守衛：基準 P 全為 1，非 1 時才有差；G23 RU 封裝功率為推估：只進能量下限；"
         "B13 ρ 低端取每 token 單價比：L_total 低端 0.342→0.358，屬判斷；B14 最終訓練占比同源：屬判斷；B19 程式代理實收時點：只作對照；B22 時間範圍倍數無法換算：說明已自述；"
         "S0 機械項（藍字文字 122 格與非藍字常數 370 格未登錄、日期過舊 110 項、單位欄空白等）：不影響數值，由後續 Gov_Map 維護逐步補。以上多數基準影響為 0，修了也不改數字。", "（全簿）"),
        ("O9 V16 能量閉合改標恆等式（非驗證）",
         f"{A}（{R} O9，建議 A）。Checks V16 比照 V23、V24 標『恆等式（非驗證）』並移出驗證計數：CHK_VerifyTotal／Pass 22／14 → 21／13（Fail 7、Warn 1 不變）。對帳報告所稱『22 → 19』是 V16、V23、V24 三項，V23、V24 已於 v14.1 移出（24／16 → 22／14），本版只剩 V16。"
         "取代 v10.2 E3『改回驗證計數』的判斷（原文保留於 Checks J164）。C 列（長期）：另找能由輸入失敗的獨立量。", "Checks V16（F164、G164）；CHK_Verify*"),
        ("O6 SRC_Index 哨兵列整理",
         f"{A}（{R} O6，建議 B，工程類）。哨兵列 B 欄由常數『（哨兵）』改為公式，標示該列的 SRC_ID 是否已在上方 SRC 頁（『查詢不會命中本列』）；A、D、E 欄與 MATCH 結果不變，無數值影響。", "SRC_Index B 欄"),
        ("O20 κ 的推導搬進活頁簿",
         f"{A}（{R} O20，建議 B，不改值）。Alloc_In 新增『κ 推導』區塊（公式：Sens_Perf 第 101–103 列 C 欄、需求 token 權重）與 Checks KP1／KP2（INFO，不計入 GOV_*）；AL_Kappa 維持 1.0（Derived，區間 0.65–1.2）。"
         "限制：v5.36A 用 4K／16K 兩個 Sens_Perf 欄內插，簿內已無 4K 欄；GW 權重未存簿內，改用需求 token 權重。重算值與 1.035 的差異見報告。", "Alloc_In κ 推導區塊；Checks KP"),
        ("O1 J1 模型規模倍數維持現狀",
         f"{A}（{R} O1，建議 A）。維持每世代一個倍數（ARCH_ScaleGen）、基準一律 1、只作情境（d1_model_scale）；分層級三列與 R-a／R-b 年度錨點留作後續。基準名稱 0 變動。", "Arch／Spec_Rack ARCH_ScaleGen"),
        ("O3 RNG_* 全部接受為契約名稱",
         f"{A}（{R} O3，建議 A）。v13.0 的 110 個 RNG_* 與 v14.0 連帶升級的 12 個名稱（IF_GMDefault_*、IF_TrainInferShare_*）全部接受為契約名稱；RG2 維持『最多算 1』，格數見 RNG_OutCount。下游須知它們是靜態端點（改上游後須重跑 tools/gen_ranges.py）。", "下游契約文件；Alloc O 節"),
        ("O8 Hopper 對外標『保守下界』",
         f"{A}（{R} O8，建議 A，B 排在證據有進展時）。Hopper 的 η 倍數 1.2（Derived）與獨立驗證失敗（V7、V8、V15、V14）已被揭露與計數；對外引用 Hopper 吞吐標『保守下界』，另找獨立依據（外部搜尋待辦）。"
         "標籤加註：Calib J5、J67；Interface A2。數值不改。", "Calib 第 5、67 列；Interface A2"),
        ("O10 回本兩種讀法並列，對外引用採機隊實收單價讀法",
         f"{A}（{R} O10，建議 B；對外 A）。L1_LReqFleet（恆等式讀法 0.756、字面讀法 2.01）兩種讀法維持並列；對外引用以機隊實收單價（AL_PriceFleet25）讀法為準。口徑是定義問題，契約已要求下游註明讀法。", "L1_LReqFleet／L1_FleetBreakeven2025／L1_PriceReqBE"),
        ("O11 v14.1 修補餘下事項",
         f"{A}（{R} O11，建議 A）。接受 v14.1 報告餘下的顯示與登錄細節；P25 顯示區間已於 v14.2 比照截斷（SL45-1）。", "docs/reports/20261017_v14.1修補.md"),
        ("O12 縮放倍數、家族計畫數、機隊占比接受為 Assumed",
         f"{A}（{R} O12，建議 A 加標籤口徑）。縮放倍數 2.42（Hopper）、隱含家族計畫 3.07 個、機隊占比取 2025 OpenAI 支出比（B4_Serve×(1−B4_Free)，全部世代同值），接受為 Assumed；公式不改。"
         "相關 21 列（Fleet_1GW 5 列、Amortize 1 列、Interface 15 列）與 12 格（Cap_In 第 28、29、31、32 列的 C／D／E）標籤已寫明口徑（訓練成本 100% 利用率、服務 ÷IF_Util）。", "Fleet_1GW／Amortize／Interface／Cap_In 標籤"),
        ("O16 DB_Evidence 積壓規則與 6 列待查",
         f"{A}（{R} O16，建議 A）。採排除遷移列規則並接受建議處置（R 欄）；E015、E020、E147、E278、E335、E338 六列維持待查。", "DB_Evidence R 欄"),
        ("O17 Astra 預訓練 token 基準維持 60T，Epoch 區間並列",
         f"{A}（{R} O17，建議 A）。Train_In E25 基準 60T 不改（J8 為 Andy 先前決定）；Epoch 估計並列為 L1_AstraExtTok_*，差距顯示為『未解釋』。", "Train_In E25；L1_AstraExtTok_*"),
        ("O18 研發倍數 J10 接受",
         f"{A}（{R} O18，建議 A）。Train_In C13 研發倍數（研發總 GPU 小時 ÷ 最終訓練）接受 J10；支出口徑換成 GPU 小時口徑時單位成本差異的方向不明、沒有證據，不補換算列。", "Train_In C13"),
        ("O19 無來源高敏感 Assumed 輸入的總決策",
         f"{A}（{R} O19，建議 A）。以下 Assumed 輸入接受為 Assumed、區間已涵蓋：Train_In C6（預訓練 MFU）、C7（goodput）；Cap_In C36:E36（儲存層）、C131:E131（商用席次占比）、C132:E132（消費訂閱占付費 token 份額）；Alloc_In C14（API 全年平均比例）、C15（每則提示 token 數）、C16（免費用戶占比）、D24（實際利用率）。"
         "沒有新證據就不改值；席次占比（Cap_In C131）與每則提示 token 數（Alloc_In C15）列入下一輪外部搜尋待辦（不另發工作單，記在報告『後續』）。", "上列各格（Gov_Map 已有決策編號）"),
        ("O21 Hopper 氣冷 PUE 與機架價",
         f"{A}（{R} O21，建議 A）。維持現狀並記錄：液冷設施參數套到氣冷 Hopper 的影響小於 1.3%（m_fleet）；機架價稽核誤讀已更正。", "L1_HoldEconMW_Hopper"),
        ("O22 2Q 查證的層級對應與單價口徑追認",
         f"{A}（{R} O22，建議 A）。追認：Luna 對應 nano 線（基準）、Astra 對應推理旗艦序列（基準 7.17）、2025 單價用牌價（唯一不使 m 恆等於 1 的選擇）；v8.0 採用的 Cap_In M 節基準值寫入決策。", "Cap_In M 節"),
        ("O5 SRC_PERF_060 來源登錄更正（修訂九）",
         "Andy 2026-10-17 13:52 照建議（docs/reports/20261017_查證_O4O5.md 第 1 節）。556 tok/s/GPU 出自 NVIDIA 技術部落格表 2（DGX H200，Server，DeepSeek-R1，MLPerf v5.1 Closed 規則下自測），"
         f"不是 MLCommons 正式結果（表下註明 Hopper results not verified by MLCommons Association）。更正：出處改為 {O5_URL}；一手／二手改『一手（已讀）』；立場說明與口徑欄改寫；"
         "Calib G121『MLPerf（MLCommons 稽核）／NVIDIA 提交』改『NVIDIA 自測（Interested-party；未經 MLCommons 驗證）』。依 CLAUDE.md 第 6 節修訂九：原字樣逐字保留於 SRC_Perf W64（備註）與 Calib J121。"
         "數值 556 不變；V1 判定不變（1.22，警示）；V1 是否接受『未經 MLCommons 驗證』的對照值列待 Project 判斷。", "SRC_Perf 第 64 列；Calib G121／J121；Checks J149"),
        ("O4 VR200 批次倍數區間",
         "Andy 2026-10-17 13:52 照建議（docs/reports/20261017_查證_O4O5.md 第 2 節）。基準 0.75 不變；區間採 Gov_Map GM595 既有的 0.70–1.0（下端 0.70 由 MLPerf v6.1 offline NVIDIA 0.76、Nebius 0.70 支持，皆 Interested-party；上端 1.0 為 Andy 2026-10-07 的假設，Assumed）。"
         "新增情境 batch_vr200_lo（0.70）、batch_vr200_hi（1.0）；只經 VR200 欄的 12 個名稱（L1_Ans5_FullMargin、L1_Ans6_GPUh、L1_RLshare_Astra_VR200、L1_RLshare_Sol_VR200 及各自 _Lo／_Hi）新增 RNG_* 端點（規則同既有區間，納入指紋與快照）。"
         "既有 59 個名稱的端點與其 VR200 欄（108 格點值）不變，列待 Project 判斷。更正『VR200 批次倍數無證據』字樣（原字樣保留於 Alloc 說明列與契約文件，更正附後）。"
         "結構風險：0.75 是相對 GB300（倍數 1，未校準）之值；若日後校準 GB300，VR200 須改絕對口徑（約 1.20–1.28），避免重複折減。", "Alloc O 節；builder/v1300_ranges.json；tools/gen_ranges.py"),
    ]
    DEC_T3 = "Andy 2026-10-17 13:52（回覆『照建議』：docs/reports/20261017_查證_O4O5.md）"
    return [[f"SL46-{i:02d}", V, f"v15.0 稽核結案：{t}", txt, DATE, DEC_T3 if t.startswith(("O5 ", "O4 ")) else DEC_BY, "v15.0 已建", where, f"{WO} {t[:3]}", "否"] for i, (t, txt, where) in enumerate(D, 1)]


# ================================================================== entry points
def apply(wb, append_text):
    log = {}
    log["o13_q"] = o13_alloc_q(wb)
    log["o13_rg4"] = o13_checks_rg4(wb)
    log["o14"] = o14_l1(wb, append_text)
    log["b11"] = b11_guard(wb, append_text)
    log["b20"] = b20_labels(wb, append_text)
    log["y9"] = y9_sens(wb, append_text)
    log["f16"] = f16_note(wb, append_text)
    log["o9"] = o9_v16(wb, append_text)
    log["o6"] = o6_sentinel(wb, append_text)
    log["o20"] = o20_kappa(wb)
    log["o20_kp"] = o20_checks_kp(wb)
    log["labels"] = o8_o12_labels(wb, append_text)
    log["t3_src060"] = t3_src060(wb, append_text)
    log["t3_vr_notes"] = t3_vr_notes(wb, append_text)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == "SL46-01" for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README
README_VERSION = (VERSION + "（主版：" + WO + "——O13 推論支出區間（Alloc Q 節、RNG_Dem004_*、Checks RG4）；O14 L1 外部對照換算同一單位；O15 B11 守衛 IF_FrontSuccVRQual、B20 口徑、Y9 敏感度端點、F16 註記；"
                  "O9 V16 改標恆等式（驗證計數 22 → 21）；O6 SRC_Index 哨兵列；O20 κ 推導區塊；O5 SRC_PERF_060 來源登錄更正（556 為 NVIDIA 自測、非 MLCommons 結果）；O4 VR200 批次倍數區間（12 個名稱）；Decisions SL46-*）。以下為 "
                  + v1420.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1420.README_TITLE
README_TITLE = V + _T[len(v1420.V):]
README_ROW = ("v15.0 稽核結案",
              "O1–O22 依預設結案：推論支出區間 RNG_Dem004_*、VR200 批次倍數區間（12 個名稱）、L1 外部對照換算同一單位、IF_FrontSuccVRQual 守衛、V16 改標恆等式（驗證計數 21）、SRC_PERF_060 來源更正、κ 推導區塊。基準值不變。細節見 Decisions SL46-*。")

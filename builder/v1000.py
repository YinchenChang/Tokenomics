# v10.0 (work order docs/workorders/20261016_稽核修正2.md r1, section 6r1 = segment 2-5): D12 self-computed L／m scenario names (not fed back), D4 nature column and
# explained／unexplained gap split, D5 verification that can fail (verification counters, MLPerf upper bounds, independent LMSYS points, RL and harness cross-checks),
# 2-4 follow-ups (label notes), downstream contract text.  Major version: new contract names (Interface L section IFW_*_LifeSelf).
#   N1 Interface L section: IFW_*_LifeSelf = IFW_*_Prod x L1_LTotal x L1_MFleet (revenue names only; capacity names have no L／m layer). No formula reads these names
#      (parity test: references outside Interface／Load_Bearing／Gov_Map must be 0).
#   N2 L1 column T "性質" (估計／殘差／倒推／恆等式／未解釋) with column U reasons; L1_GapUnexplained row (actual gap ÷ four-factor product); Train_In H34, Alloc, Interface tags.
#   N3 Checks column G "性質"; Checks V section (CHK_VerifyTotal／Pass／Fail; failures are NOT in GOV_Errors); Calib H section gains two MLPerf v5.1 server points
#      (Hopper H200, GB200); SRC_Perf／SRC_Harness records for the new reference values.
#   N4 label notes (Perf_Batch, Perf TTFT, kappa, free share), literal payback reading marked inconsistent.
# Every write to an Excel-owned cell is guarded (text not yet present ／ cell still holds its v9.0 value).
import re
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY, section
import v810
import v800

VERSION = "20261016_Tokenomics_v10.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-16"
V = "v10.0"
WO = "工作單 docs/workorders/20261016_稽核修正2.md r1 第 6r1 節"
Q3A = "docs/reports/20261015_稽核修正3A_查證.md"
CHAT_DEF = "chat 端預設（N1–N5 見工作單 6r1），可撤回"
DASH = "—"
_row = v800._row

# ================================================================== N1: Interface L section (IFW_*_LifeSelf)
REVS = ["RevGW_Luna", "RevGW_Sol", "RevGW_Astra", "RevGWFleet", "RevGWFront_Luna", "RevGWFront_Sol", "RevGWFront_Astra", "RevGWFleetFront"]
LIFESELF_NOTE = "情境：自算 L、m（L1_LTotal、L1_MFleet）；不回流，不建議下游作為基準"
IFL_TITLE = ("L. 情境：自算 L、m（v10.0 N1，D12）：IFW_*_LifeSelf ＝ IFW_*_Prod × L1_LTotal × L1_MFleet；控制值 CTL_PriceLife、CTL_Monetize 仍為 1（IFW_*_Life 不變）。"
             "本節名稱不得被任何公式讀取（parity 測試：Interface、Load_Bearing、Gov_Map 以外引用數＝0）；只供讀者並列比較，不是下游基準")


def _name_row(wb, name):
    ref = wb.defined_names[name].attr_text
    sh, rng = ref.split("!")
    return sh, int(re.findall(r"\$(\d+)", rng)[0])


def interface_l(wb):
    ws = wb["Interface"]
    start = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, start, IFL_TITLE, 17)
    r = start + 1; made = []
    for stem in REVS:
        sh, p = _name_row(wb, f"IFW_{stem}_Prod"); assert sh == "Interface", sh
        base = str(ws.cell(p, 1).value).split("｜")[0]
        put(ws, f"A{r}", f"{base}｜{LIFESELF_NOTE}　[IFW_{stem}_LifeSelf]"); put(ws, f"B{r}", "$B/年")
        for k in range(3, 18):
            X = ws.cell(row=1, column=k).column_letter
            put(ws, f"{X}{r}", f'=IF(ISNUMBER({X}{p}),IF(AND(ISNUMBER(L1_LTotal),ISNUMBER(L1_MFleet)),{X}{p}*L1_LTotal*L1_MFleet,"L、m 非數字（本情境）"),{X}{p})',
                fmt=ws.cell(p, 3).number_format)
        wb.defined_names[f"IFW_{stem}_LifeSelf"] = DefinedName(f"IFW_{stem}_LifeSelf", attr_text=f"Interface!$C${r}:$Q${r}")
        made.append((f"IFW_{stem}_LifeSelf", r)); r += 1
    return dict(start=start, made=made)


# ================================================================== N2: L1 gap split (explained／unexplained), nature column
def l1_rows_new():
    return [_row("GapUnexplained", "落差分解 5：未解釋＝實際缺口 ÷ 四項乘積（L1_ScaleServe2000 ÷ L1_GapProduct）；本分解不是定義式，未解釋部分的來源不可由本表得知",
                 "v10.0 N2（D4）：已解釋／未解釋；四項口徑差之積對實際缺口的剩餘倍數",
                 "=IF(AND(ISNUMBER(L1_ScaleServe2000),ISNUMBER(L1_GapProduct)),IF(L1_GapProduct>0,L1_ScaleServe2000/L1_GapProduct,AL_UnavailTxt),AL_UnavailTxt)",
                 "=IF(AND(ISNUMBER(L1_ScaleServe2000),ISNUMBER(L1_GapProduct_Hi)),IF(L1_GapProduct_Hi>0,L1_ScaleServe2000/L1_GapProduct_Hi,AL_UnavailTxt),AL_UnavailTxt)",
                 "=IF(AND(ISNUMBER(L1_ScaleServe2000),ISNUMBER(L1_GapProduct_Lo)),IF(L1_GapProduct_Lo>0,L1_ScaleServe2000/L1_GapProduct_Lo,AL_UnavailTxt),AL_UnavailTxt)",
                 "x", "低＝實際缺口 ÷ 四項乘積高端、高＝÷ 低端（實際缺口 L1_ScaleServe2000 無區間）",
                 "1＝四項完全解釋；大於 1＝四項只解釋缺口的 1 ÷ 該值（基準約 3.7 倍：四項只解釋約 27%）；剩餘部分來源不明，是未解釋（不是已查明的原因）",
                 "L1_ScaleServe2000、L1_GapProduct", "同 L1_GapProduct：Assumed 分母", DASH, "L1_GapUnexplained", "L1 本頁（第 70–74 列分解的並列）", "顯示用")]


def l1_patch(R):
    out = []
    for row in R:
        row = list(row)
        if row[0] == "GapProduct" and "已解釋部分" not in row[1]:
            row[1] = row[1].replace("落差分解乘積：", "落差分解乘積（已解釋部分）：", 1) + "；未解釋部分見 L1_GapUnexplained（本分解不是定義式）"
        out.append(tuple(row))
    return out


E_, R_, B_, I_, U_ = "估計", "殘差", "倒推", "恆等式", "未解釋"
NATURE = {}
def _n(cls, reason, *keys):
    for k in keys: NATURE[f"L1_{k}"] = (cls, reason)
_n(E_, "由輸入、規格與物理推導直接算出（自下而上），沒有以目標值反解", "CapexGW_Hopper", "CapexGW_GB200", "CapexGW_GB300", "CapexGW_VR200", "NvContentGW_VR200", "FacCapexMW",
   "HoldEconGW_Hopper", "HoldEconGW_GB200", "HoldEconGW_GB300", "HoldEconGW_VR200", "GPUhr_Hopper", "GPUhr_GB200", "GPUhr_GB300", "GPUhr_VR200", "CapexITMW_GB300_vsIREN")
_n(E_, "roofline 推導的每 token 成本（自下而上）", "CostDec_Luna_VR200", "CostDec_Luna_GB300", "CostDec_Sol_VR200", "CostDec_Sol_GB300", "CostDec_Astra_VR200", "CostDec_Astra_GB300", "CostTotTokIX_GB300")
_n(E_, "理論營收上限＝每 GW 產出 × 牌價（物理量 × 單價），不含 L、m", "RevGW_Luna_VR200", "RevGW_Sol_VR200", "RevGW_Astra_VR200", "RevGW_Fleet_VR200", "RevGWFleet_OAI2025")
_n(E_, "模型值對外部牌價／租金的對照（外部值為參照，不用於反解）", "GPUhr_GB200_vsCW", "GPUhr_GB300_vsBE")
_n(B_, "RL rollout token 由「RL ÷ 預訓練 GPU 小時＝目標值（J9：Luna／Sol 約 0.3、Astra 1.0）」反解；校準目標不是證據（3A：Olmo 3 約 0.11、DeepSeek-V3.2 ≥ 0.1）", "RLshare_Sol_VR200", "RLshare_Astra_VR200")
_n(I_, "輸入的倒數（Train_In C13 的研發倍數），只驗算一致，沒有新資訊", "FinalTrainShare")
_n(E_, "預訓練 FLOPs＝6 × 啟用參數 × token（自下而上；啟用參數、token 為 Assumed）", "PretrainFLOP_Astra")
_n(E_, "Q1／Q2／研發成本：服務 GW 為支出路線（SRC_DEM_004 ÷ 持有成本）、研發 GW 為計畫規模 × 單位 GW 年（Assumed）；乘除皆為模型推導", "Ans1", "Ans2", "Ans3")
_n(E_, "各層級成本、理論營收、後訓練占比、牌價比、毛利率、harness 與成功任務成本：由輸入推導的輸出", "Ans4", "Ans5", "Ans6", "Ans7", "Ans8", "Ans9", "Ans5_GM", "Ans5_FullMargin", "Ans6_GPUh")
_n(B_, "主口徑服務 GW＝推論支出（SRC_DEM_004）÷ 持有成本：由外部支出除以模型成本反推容量；與外部對照同源，比值恆為 1（不是獨立檢驗）", "ExtServeGW")
_n(E_, "兩路線的免費占比對照（token 路線對支出口徑）", "ExtFreeShare")
_n(E_, "模型每日 token 對 Epoch 估計的對照", "ExtDaily")
_n(B_, "令機隊營收＝持有成本所需的乘積（使某值不變而反解）", "FleetBreakeven", "FleetBreakeven2025")
_n(E_, "機隊營收 ÷ 持有成本（比值輸出）", "FleetMargin", "FleetProdRatio")
_n(I_, "每 GW 的 $B 與每 MW 的 $M 數值相同（單位換算）", "HoldEconMW_Hopper", "HoldEconMW_GB200", "HoldEconMW_GB300", "HoldEconMW_VR200")
_n(E_, "相鄰世代每 GW 總產出比（物理推導）；harness 對世代比為兩個推導比值之比", "TokMW_Gen_ratio_GB200", "TokMW_Gen_ratio_GB300", "TokMW_Gen_ratio_VR200",
   "HarVsGen_Chat", "HarVsGen_ReasonChat", "HarVsGen_SingleAgent", "HarVsGen_MultiAgent", "HarVsGen_Coding")
_n(E_, "外部估計值（Epoch 硬體推估；單一外部錨點，不是模型推導）", "PretrainFLOP_Astra_Ext")
_n(U_, "差距沒有被分解（工作單 D4：標「未解釋」）：Astra 啟用參數、token、後訓練都可能", "AstraScale")
_n(U_, "OpenAI 訓練支出 ÷ 模型研發算力成本：差距未分解（校準用，不得當產能）", "ScaleRD")
_n(U_, "支出路線 ÷ token 路線：兩路線的差距，由 L1_GapProduct 只解釋一部分，其餘見 L1_GapUnexplained", "ScaleServe", "ScaleServe2000")
_n(E_, "落差分解的四個已解釋因子（各自由 Assumed 輸入算出）；乘積＝已解釋部分", "GapPrompt", "GapSpendBasis", "GapISL", "GapUtil", "GapProduct")
_n(U_, "實際缺口 ÷ 四項乘積：四項之外未被解釋的倍數（本分解不是定義式）", "GapUnexplained")
_n(R_, "m＝營收 ÷（token × 單價）：由營收與 token 算出的殘差，吸收所有未建模的口徑差", "MImplied", "MImplied_Ext", "MFleet", "MAPI", "MSub", "MSeat", "MAPI_Anthropic", "MFleet_Px2026", "MixFactorAPI")
_n(R_, "實收單價＝m × 混合有效單價＝營收 ÷ token（m 的殘差性質沿用）", "PriceRealFleet", "PriceRealDemand")
_n(E_, "機隊付費 token 上限（支出路線服務 GW × 最大產出）：上限讀法的推導值", "TokCeiling")
_n(B_, "令需求 token 佔滿機隊有效產能所需的每則 token 數（閉合解，使某值不變）", "TokPerPromptClose")
_n(E_, "壽命期價格係數 L 的兩個分項與乘積（價格迴歸與降級假設；三者皆 Assumed）", "LPrice", "LDemote", "LTotal", "PriceRho")
_n(B_, "回本所需的 L 或實收單價：令營收＝成本所需的量（倒推）", "LReqFleet", "LReqFleet_VR200", "PriceReqBE")
_n(I_, "機隊持有成本 ÷ 實收營收：同一支出路線的恆等式讀法，不受容量口徑影響", "LReqFleet_Id")
_n(E_, "2025 年度牌價指數與機隊口徑單價（牌價 × 加權，Derived）", "Price25Mix", "PriceFleet25")
_n(B_, "令世代間每 MW 收入（或回本餘裕）持平所需的年價格變化率（使某值不變而反解）", "GenPxThr_Rev_GB200", "GenPxThr_Rev_GB300", "GenPxThr_Rev_VR200", "GenPxThr_Pay_GB200", "GenPxThr_Pay_GB300", "GenPxThr_Pay_VR200")
_n(B_, "Epoch 1.0e27 FLOP ÷（6 × 啟用參數）：由外部 FLOP 反推隱含 token（情境，不進計算）", "AstraExtTok_180B", "AstraExtTok_400B", "AstraExtTok_800B")


def l1_nature(wb):
    """Column T (性質) and U (理由) on every L1 data row; every row must be classified."""
    ws = wb["L1"]
    put(ws, "T4", "性質（v10.0 N2：估計／殘差／倒推／恆等式／未解釋）", F_BOLD, wrap=True); put(ws, "U4", "性質的判斷理由（v10.0）", F_BOLD, wrap=True)
    ws.column_dimensions["T"].width = 12; ws.column_dimensions["U"].width = 60
    stats = {}; missing = []
    for r in range(5, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if not (isinstance(a, str) and a.startswith("L1_")): continue
        if a not in NATURE: missing.append(a); continue
        cls, why = NATURE[a]
        put(ws, f"T{r}", cls, F_BOLD); put(ws, f"U{r}", why, F_NOTE, wrap=True)
        stats[cls] = stats.get(cls, 0) + 1
    assert not missing, missing
    ids = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    unused = [k for k in NATURE if k not in ids]
    assert not unused, unused
    return stats


# ================================================================== N2/N4: marker and label text (guarded appends)
TAIL_NK = " ｜v10.0 N2（D4）：性質＝倒推（隱含 N × k／J8 落差由 2025 支出反推研發 GW，再除以計畫當量；不是觀測值）"
TAIL_RL = " ｜v10.0 N2（D4）：性質＝倒推——RL rollout token 由「RL ÷ 預訓練 GPU 小時＝目標值」反解，校準目標不是證據；獨立對照見 Checks V 節（Olmo 3 約 0.11、DeepSeek-V3.2 ≥ 0.1，通過帶 0.1–0.3）"
TAIL_KAPPA = " ｜v10.0 N4：κ＝（實際流量每 GPU 秒總 token）÷（參考請求每 GPU 秒總 token）；價格端乘 κ（v9.0 M3），維持乘法（定義如此，基準 1）"
TAIL_FREE = " ｜v10.0 N4：產業總量（Epoch 全體 token，L1_MImplied_Ext）的免費占比未必等於 ChatGPT 的免費占比；本格只量 ChatGPT"
TAIL_LREQ = ("｜v10.0 N4：字面讀法（L1_LReqFleet）口徑不一致，僅供對照——分子是整個機隊的損益兩平，分母卻只含付費服務占比（約 22%）的營收；判讀只用恆等式讀法 L1_LReqFleet_Id")
TAIL_ID229 = "｜v10.0 N3：性質＝恆等式（非驗證）"
TAIL_PERFB = "；Perf_Batch 為訓練端批次推論，無服務快取（prefill 計全 ISL，不乘 1 − B4_CacheHit；v10.0 N4）"


def text_update(wb, append_text):
    log = []
    ws = wb["Alloc"]
    for name, tail in (("AL_ImpliedNk", TAIL_NK), ("AL_J8Gap", TAIL_NK)):
        r = _name_row(wb, name)[1]
        if append_text(ws[f"A{r}"], tail): log.append(f"Alloc!A{r}: nature tag ({name})")
    r = _name_row(wb, "IF_AllocImpliedNk")[1]
    if append_text(wb["Interface"][f"A{r}"], TAIL_NK): log.append(f"Interface!A{r}: nature tag")
    if append_text(wb["Train_In"]["H34"], TAIL_RL): log.append("Train_In!H34: 倒推 tag")
    if append_text(wb["Alloc_In"]["G26"], TAIL_KAPPA): log.append("Alloc_In!G26: kappa definition")
    if append_text(wb["Alloc_In"]["G16"], TAIL_FREE): log.append("Alloc_In!G16: free share scope")
    r = _name_row(wb, "L1_LReqFleet")[1]
    if append_text(wb["L1"][f"B{r}"], TAIL_LREQ): log.append(f"L1!B{r}: literal reading inconsistent")
    for rr in range(200, 240):                      # Interface identity row: IF_DeprIT＋IF_DeprFac＋IF_OpexGW − IF_HoldAcct
        a = wb["Interface"].cell(rr, 1).value
        if isinstance(a, str) and a.startswith("加總核對：IF_DeprIT"):
            if append_text(wb["Interface"].cell(rr, 1), TAIL_ID229): log.append(f"Interface!A{rr}: identity tag")
    return log


def l1_judge(wb):
    """v10.0 N4-8: payback reading uses the identity reading only; the literal reading is shown beside it, marked inconsistent (v9.0 M5 switched to the literal reading when the two agreed within 10%)."""
    ws = wb["L1"]
    r = _name_row(wb, "L1_LReqFleet")[1]; ri = _name_row(wb, "L1_LReqFleet_Id")[1]
    D, I, M = f"D{r}", f"D{ri}", f"M{r}"
    ws[f"P{r}"].value = (
        f'=IF(AND(ISNUMBER({D}),ISNUMBER({I}),ISNUMBER({M})),IF({I}>0,'
        f'"恆等式讀法："&IF({M}>={I},"回本","未回本")&"（L_total "&TEXT({M},"0.00")&" 對所需 L "&TEXT({I},"0.00")&"）；字面讀法 "&TEXT({D},"0.00")&"（口徑不一致，僅供對照）；兩種讀法差 "&TEXT({D}/{I},"0.00")&" 倍＝付費服務占比倒數 "&TEXT(1/(B4_Serve*(1-B4_Free)),"0.00")&" × 付費 token 占比 "&TEXT({D}/{I}/(1/(B4_Serve*(1-B4_Free)))/(AL_UtilActual/IF_Util),"0.000")&" × 實際÷模型利用率 "&TEXT(AL_UtilActual/IF_Util,"0.000"),"所需 L 為 0"),'
        f'IF(AND(ISNUMBER({I}),ISNUMBER({M})),IF({M}>={I},"回本","未回本")&"（恆等式讀法：L_total "&TEXT({M},"0.00")&" 對所需 L "&TEXT({I},"0.00")&"；字面讀法非數字）","推算值非數字（本情境）"))')
    return r


# ================================================================== N3: Checks column G (nature), V section (verification counters)
CK_V, CK_ID, CK_CMP, CK_GOV, CK_HINT = "驗證（能失敗；計入 V 節）", "恆等式（非驗證）", "對照（無通過條件）", "治理（結構檢查）", "對照（觸發＝提示）"
# row (v9.0 layout) -> (label prefix, nature); labels are asserted so a layout change stops the build
CK_NATURE = {
    4: ("VR200 每 GW 總資本支出", CK_CMP), 5: ("VR200 每 GW NVIDIA", CK_CMP), 6: ("每 MW IT 廠房", CK_CMP), 7: ("GB200 經濟口徑", CK_CMP), 8: ("GB300 經濟口徑", CK_CMP),
    9: ("GB200 市場牌價", CK_CMP), 10: ("新雲損益兩平", CK_CMP),
    14: ("校準：擬合點重現", CK_ID), 15: ("樣本外：GB300 SGLang", CK_V), 16: ("樣本外：GB300 vLLM", CK_V), 17: ("樣本外：GB200 vLLM", CK_V), 18: ("樣本外：GB200／GB300 110", CK_CMP),
    19: ("GB300 Sol 經濟成本 vs InferenceX", CK_CMP), 20: ("VR200 ÷ GB300 每 GW 產出", CK_CMP), 21: ("GB300 每 GPU 功率", CK_CMP), 22: ("VR200 ÷ GB300 decode", CK_CMP),
    23: ("第二來源：GB300 interactive", CK_V), 24: ("第二來源：VR200 ÷ GB300", CK_CMP), 25: ("來源衝突：GB300 ÷ GB200", CK_CMP),
    26: ("能量閉合", CK_V), 27: ("SLO 或 TTFT 不可達", CK_CMP), 28: ("牌價空間", CK_CMP),
    32: ("DeepSeek V3 推導 MFU", CK_CMP), 33: ("RL ÷ 預訓練 GPU 小時：VR200 Astra", CK_CMP), 34: ("RL ÷ 預訓練 GPU 小時：VR200 Sol", CK_CMP), 35: ("RL 有效 MFU", CK_CMP),
    36: ("後訓練占比：GPU 小時口徑", CK_V), 37: ("最終訓練 ÷ 研發計畫", CK_CMP), 38: ("前沿錨點中值", CK_CMP), 39: ("Astra 最終訓練占 1 GW", CK_CMP),
    43: ("OpenAI 2025 對帳", CK_CMP), 44: ("DeepSeek V4-Pro 尖峰", CK_CMP), 45: ("DeepSeek V4-Pro 離峰", CK_CMP), 46: ("DeepSeek V4.1-Flash", CK_CMP),
    47: ("單價前緣模型：Luna", CK_CMP), 48: ("單價前緣模型：Sol", CK_CMP), 49: ("單價前緣模型：Astra", CK_CMP), 50: ("中國合格者最低", CK_CMP), 51: ("隱含每 GW 年家族研發", CK_CMP),
    52: ("Fleet_1GW 服務 GW 閉合", CK_ID), 53: ("自下而上攤提", CK_CMP), 54: ("K6 縮放倍數", CK_CMP), 55: ("K6 (c)", CK_CMP), 56: ("機隊各層級貢獻合計", CK_ID),
    60: ("混合權重 w", CK_ID), 61: ("Workload 總 token", CK_ID), 62: ("ARC 重現（token）", CK_CMP), 63: ("ARC 重現（R）", CK_CMP), 64: ("ARC 成功率換算", CK_CMP), 65: ("METR 隱含", CK_CMP),
    66: ("Astra 標準 harness", CK_CMP), 67: ("每成功任務", CK_CMP), 68: ("Sens_Har：Astra R", CK_CMP), 69: ("可靠度下限", CK_CMP), 70: ("前緣『無合格』", CK_CMP),
}
CK_GOV_ROWS = {  # governance tables: A column holds the ID
    **{r: (i, CK_GOV) for r, i in zip(range(74, 87), [f"E{n}" for n in range(1, 14)])},
    87: ("W1", CK_GOV), 88: ("W2", CK_GOV), 89: ("I1", CK_GOV), 90: ("I2", CK_GOV), 91: ("I3", CK_GOV), 92: ("I4", CK_GOV), 93: ("I5", CK_GOV), 94: ("I6", CK_GOV), 95: ("I7", CK_GOV), 96: ("I8", CK_GOV),
    104: ("H1", CK_ID), 105: ("H2", CK_ID), 106: ("H3", CK_GOV), 110: ("X1", CK_ID), 114: ("X7", CK_ID), 118: ("K1", CK_GOV), 119: ("K2", CK_GOV), 120: ("K3", CK_ID), 121: ("K4", CK_ID),
    122: ("K5", CK_GOV), 123: ("K6", CK_GOV), 124: ("K7", CK_CMP), 128: ("M1", CK_HINT), 129: ("M2", CK_HINT), 130: ("M3", CK_HINT), 131: ("M4", CK_HINT), 132: ("M5", CK_ID),
    136: ("Z1", CK_ID), 140: ("Z2", CK_ID),
}
CK_HDR_ROWS = (3, 13, 31, 42, 59, 73, 103, 109, 113, 117, 127, 135)
NOTE_NAT = ("性質（v10.0 N3）說明：驗證＝能失敗的檢查，計入 V 節的 CHK_VerifyTotal／Pass／Fail；恆等式（非驗證）＝由建構或定義恆成立、擬合點重現或輸入加總，不計入；"
            "對照＝只列外部參照、判讀為文字、沒有通過條件；治理＝資料登錄與結構完整性（ERROR 計入 GOV_Errors）")


def _check_nature(wb):
    ws = wb["Checks"]
    cnt = {}
    for r, (pref, nat) in CK_NATURE.items():
        a = str(ws[f"A{r}"].value or ""); assert a.startswith(pref), (r, pref, a[:40])
        put(ws, f"G{r}", nat, F_BOLD if nat == CK_V else F_NOTE); cnt[nat] = cnt.get(nat, 0) + 1
    for r, (i, nat) in CK_GOV_ROWS.items():
        a = str(ws[f"A{r}"].value or ""); assert a == i, (r, i, a)
        put(ws, f"G{r}", nat, F_NOTE); cnt[nat] = cnt.get(nat, 0) + 1
    for r in CK_HDR_ROWS:
        put(ws, f"G{r}", "性質（v10.0 N3）", F_BOLD)
    put(ws, "A2", NOTE_NAT, F_NOTE)
    ws.column_dimensions["G"].width = 24
    return cnt


SOFT_CAP = ("V1", "V2", "V3")       # v11.0 G4: MLPerf server items (soft upper bound); interactive items V4–V6 stay hard caps


def checks_v(wb, CAL):
    ws = wb["Checks"]
    cnt = _check_nature(wb)
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "V. 驗證計數（工作單 稽核修正2 6r1 N3，D5，v10.0）：只計能失敗的檢查；驗證失敗不進 GOV_Errors（不阻擋合併），報告必須列出", 10); r += 1
    put(ws, f"A{r}", "判準寫在 H（下限）與 I（上限）兩格（chat 端 J2 決定；黑字，不登錄 Gov_Map）。F 欄＝1 通過、0 失敗、警示（v11.0 G4：只用於 V1–V3）、—＝不適用（任一側非數字）。MLPerf interactive 為廠商最佳化後的可達上限（模型高於 MLPerf 才判失敗）；"
                   "MLPerf server（V1–V3）為軟上限（v11.0 G4；v12.0 H1 加失敗門檻）：比值 ≤ 1 通過；1 至 CHK_SoftCapFail（基準 2，Calib M 節）之間判『警示』，不計失敗；> CHK_SoftCapFail 判失敗（server 的 TPOT 80 ms 是 p99 口徑，模型取平均；超過 2 倍表示模型高估，不再只是口徑差；同條件 TensorRT-LLM H200 為 MLPerf v5.1 的 2.6 倍）；"
                   "V18 為恆等式（非驗證，v12.0 H7）、V20 為校準相關（非獨立，v12.0 H2）：兩者的 F 欄為文字，不計入驗證項目數；"
                   "LMSYS 兩點口徑不嚴（無明確 SLO，模型 Sol 級≠DeepSeek-V3 規模），帶寬 0.5–2.0；RL 帶 0.1–0.3；harness 輪數倍數 ≥ 1（SWE Atlas 方向證據，只判方向）", F_NOTE); r += 1
    sum_rows = {}
    for key, lab in (("T", "驗證項目數（F 欄為數字或『警示』者）"), ("P", "通過"), ("F", "失敗"), ("W", "警示（MLPerf server 軟上限：模型高於 1 但未超過 CHK_SoftCapFail，不計失敗；v11.0 G4、v12.0 H1）")):
        sum_rows[key] = r; put(ws, f"A{r}", f"V{key}"); put(ws, f"B{r}", lab, F_BOLD); r += 1
    for i, h in enumerate(["編號", "驗證項目", "模型值", "對照值（實測或上限）", "模型 ÷ 對照（或模型值）", "結果（1 通過／0 失敗／警示／—）", "性質", "通過帶下限", "通過帶上限", "口徑與來源"]):
        put(ws, f"{'ABCDEFGHIJ'[i]}{r}", h, F_BOLD, wrap=True)
    r += 1
    first = r
    ratio = lambda rr: f'=IF(AND(ISNUMBER(C{rr}),ISNUMBER(D{rr})),IF(D{rr}>0,C{rr}/D{rr},"—"),"—")'
    items = []
    mT, mO = CAL["mT"], CAL["mO"]
    _tr = wb["Tech_Registry"]
    _trr = [rr for rr in range(5, _tr.max_row + 1) if re.fullmatch(r"T\d\d", str(_tr.cell(rr, 1).value or ""))]
    TR_FIRST, TR_LAST = min(_trr), max(_trr)       # v10.3 F3: Tech_Registry entry rows (T01–T12)
    _R = lambda col: f"Tech_Registry!${col}${TR_FIRST}:${col}${TR_LAST}"
    # v12.0 H7: V19 recomputes the verdict T should show from I, J, L, M and CST_MainMin (it does not read the T formulas' results), then compares it with column T.
    # main = L has a value ? L = 主流 : J >= CST_MainMin；bad = (main and M = 否) or (non-main and M = 是 and I <> 早期採用)；1/0 per row, mutually exclusive
    _BAD = (f'((({_R("L")}="")*({_R("J")}>=CST_MainMin)+({_R("L")}<>"")*({_R("L")}="主流"))*({_R("M")}="否"))'
            f'+((({_R("L")}="")*({_R("J")}<CST_MainMin)+({_R("L")}<>"")*({_R("L")}="非主流"))*({_R("M")}="是")*({_R("I")}<>"早期採用"))')
    for vid, col, lab, src in (
            ("V1", "G", "MLPerf v5.1 server（DeepSeek-R1）：Hopper——模型 ÷ MLPerf ≤ 1（軟上限：> 1 警示；> CHK_SoftCapFail 失敗）", "SRC_PERF_060；DGX H200（8 GPU，NVIDIA 提交，NVIDIA 註明 Hopper 結果未經 MLCommons 驗證）；模型為 H100 規格（頻寬較 H200 低，上限偏寬）"),
            ("V2", "H", "MLPerf v6.0 server：GB200 NVL72（NVIDIA 72 GPU）——模型 ÷ MLPerf ≤ 1（軟上限：> 1 警示；> CHK_SoftCapFail 失敗）", "SRC_PERF_075（4,668，NVIDIA，Interested-party；v10.2 E3 取代 v5.1 的 SRC_PERF_061＝2,327）；第二來源 CoreWeave 64 GPU 4,868（SRC_PERF_077）"),
            ("V3", "F", "MLPerf v6.0 server：GB300 NVL72（NVIDIA 72 GPU 機櫃）——模型 ÷ MLPerf ≤ 1（軟上限：> 1 警示；> CHK_SoftCapFail 失敗）", "SRC_PERF_076（5,562，NVIDIA 72 GPU；v10.2 E3 取代 Nebius 8 GPU 單機 8,064＝SRC_PERF_026）；同輪機櫃範圍 5,562–7,994（Nebius 72 GPU 7,994＝SRC_PERF_078）"),
            ("V4", "C", "MLPerf v6.1 interactive：GB300 NVL72——模型 ÷ MLPerf ≤ 1", "SRC_PERF_028／SRC_HW_047；Calib H 節第 1 驗證點"),
            ("V5", "D", "MLPerf v6.0 interactive：GB200 NVL72——模型 ÷ MLPerf ≤ 1", "SRC_PERF_025／SRC_HW_047；Calib H 節第 2 驗證點"),
            ("V6", "E", "MLPerf v6.1 interactive：VR200 NVL72（預覽類）——模型 ÷ MLPerf ≤ 1", "SRC_PERF_027／SRC_HW_047；預覽類提交，Calib H 節第 3 驗證點")):
        items.append((vid, lab, f"=Calib!{col}{mO}", f"=Calib!{col}{mT}", None, 0, 1, "MLPerf（Interested-party）；" + src))
    items += [
        ("V7", "LMSYS H100 decode（條件對齊）：Hopper——模型 decode tok/s/GPU ÷ 實測，通過帶 0.5–2.0", f"=Calib!F{CAL['J']['jD']}", "=SRC_PERF_062", None, 0.5, 2.0,
         "SRC_PERF_062（LMSYS／SGLang，96×H100，輸入 2,000，ITL 約 100 ms；Atlas Cloud 有商業動機）；v10.2 E3：模型值改為 Calib J 節 F 欄（條件對齊：DeepSeek-V3 規模、輸入 2,000、ITL 100 ms＝10 tok/s/user，批次由速度下限與 HBM 決定）；不用於校準"),
        ("V8", "LMSYS GB200 decode（條件對齊）：GB200——模型 decode tok/s/GPU ÷ 實測，通過帶 0.5–2.0", f"=Calib!G{CAL['J']['jD']}", "=SRC_PERF_063", None, 0.5, 2.0,
         "SRC_PERF_063（LMSYS／SGLang，GB200 NVL72，NVFP4，輸入 2,000，decode 48 rank，無 TPOT；與 NVIDIA 合作，Interested-party 成分高）；v10.2 E3：模型值改為 Calib J 節 G 欄（條件對齊，同 V7）；不用於校準"),
        ("V9", "RL ÷ 預訓練 GPU 小時：Luna（VR200）——通過帶 0.1–0.3", "=INDEX(TRN_RLRatioH,1,10)", "=SRC_PERF_064", "=C{r}", 0.1, 0.3,
         "對照值＝Olmo 3（AI2）RL ÷ 預訓練約 0.11（SRC_PERF_064）；DeepSeek-V3.2 ≥ 0.1（SRC_PERF_065）；帶 0.1–0.3（3A 第 3 節）；模型值＝Training 第 78 列（J9 目標約 0.3，基準校準值，不是證據）"),
        ("V10", "RL ÷ 預訓練 GPU 小時：Sol（VR200）——通過帶 0.1–0.3", "=INDEX(TRN_RLRatioH,1,11)", "=SRC_PERF_064", "=C{r}", 0.1, 0.3, "同上；Sol"),
        ("V11", "harness 輪數倍數 ≥ 1（Coding agent；選定檔案；SWE Atlas：原生 scaffold 工具呼叫多 1.5–2 倍，只判方向）", "=INDEX(B5_SelT,1,5)", "=SRC_HAR_016_Lo", "=C{r}", 1, None,
         "SRC_HAR_016（SWE Atlas arXiv 2605.08366：原生 scaffold 對 mini-SWE-agent 工具呼叫 1.5–2 倍）；基準 0.7（Har_In 第 12 列，Q3＝R1）預期失敗，如實顯示，不調輸入；工具呼叫數不等於輪數，只作方向證據"),
        ("V12", "樣本外：GB300 SGLang＋MTP 50 tok/s——模型 ÷ 實測 ±10%（Checks B15）", "—", "=Checks!C15", "=Checks!B15", 0.9, 1.1, "SRC_PERF_004；Checks B15 原判準「±10% 內視為前緣形狀成立」"),
        ("V13", "樣本外：GB300 vLLM 無 MTP 27 tok/s——模型 ÷ 實測 > 1（Checks B16）", "—", "=Checks!C16", "=Checks!B16", 1, 3, "SRC_PERF_001；Checks B16 原判準「應 >1：舊軟體」；v10.2 E3 加上限 ≤ 3（chat 端預設，可撤回）：舊軟體點模型應高於實測，但不應高出數倍"),
        ("V14", "樣本外：GB200 vLLM 無 MTP 27 tok/s——模型 ÷ 實測 > 1（Checks B17）", "—", "=Checks!C17", "=Checks!B17", 1, 3, "SRC_PERF_002；Checks B17 原判準「應 >1：舊軟體＋記憶體限制配方」；v10.2 E3 加上限 ≤ 3（同 V13，可撤回）"),
        ("V15", "DeepSeek 線上服務 decode（條件對齊）：Hopper H800——模型 ÷ 實測，通過帶 0.5–2.0", f"=Calib!E{CAL['J']['jD']}", "=SRC_PERF_073", None, 0.5, 2.0,
         "SRC_PERF_073（1,850 tok/s/GPU，24 小時平均）；與校準點 2,324 同一家公司，相關性高；模型值＝Calib J 節 E 欄（KV 4,989、EP144、約 21 tok/s/user）；不用於校準"),
        ("V16", "能量閉合：各欄最大閉合比 ≤ 100%（Checks B26）", "—", "—", "=Checks!B26", 0, 1, "原『恆等式（非驗證）』；單邊界限，輸入改變時可能失敗，v10.2 E3 改回驗證計數"),
        ("V17", "後訓練占比：GPU 小時口徑 − FLOPs 口徑 ≥ 0（Checks B36）", "—", "—", "=Checks!B36", 0, None, "原『恆等式（非驗證）』；單邊界限，輸入改變時可能失敗，v10.2 E3 改回驗證計數"),
        ("V18", "Tech_Registry K 欄（主流判定）：每一列 K＝『主流』與『公開採用實驗室數 J ≥ 門檻（CST_MainMin）』一致——不一致列數＝0【恆等式（非驗證）】",
         f'=COUNTIF(Tech_Registry!$K${TR_FIRST}:$K${TR_LAST},"主流")', f'=COUNTIF(Tech_Registry!$J${TR_FIRST}:$J${TR_LAST},">="&CST_MainMin)',
         f'=IF(AND(ISNUMBER(C{{r}}),ISNUMBER(D{{r}})),SUMPRODUCT(--((Tech_Registry!$K${TR_FIRST}:$K${TR_LAST}="主流")<>(Tech_Registry!$J${TR_FIRST}:$J${TR_LAST}>=CST_MainMin))),"—")', 0, 0,
         "v10.3 F3 新增；v12.0 H7 改標恆等式（非驗證）：K 欄的公式本身就是 J ≥ CST_MainMin，本項重述同一條件，只有 K 被手填覆寫時才會不等；無法改成獨立於 K 的檢查（判定依據只有 J 與門檻），"
         "故移出驗證計數（F 欄顯示文字，不計入驗證項目數／通過／失敗）。模型值＝K 為『主流』的條目數，對照值＝J ≥ 門檻的條目數，結果欄＝逐列不一致的列數（K 被改寫而與 J 脫節時，F 欄改顯示『恆等式不成立』）。"
         "不比對狀態欄 I：T06（狀態『早期採用』、J＝2 ≥ 門檻 2）K 為『主流』而 I 不是，屬狀態欄口徑差，列『待 Project 判斷』"),
        ("V19", "Tech_Registry T 欄（一致性檢查）：由公式自行重算每列應有的判定，與 T 欄比對——不符列數＋實質不一致列數＝0",
         f'=SUMPRODUCT({_BAD})', f'=SUMPRODUCT(--({_R("T")}<>"一致"))',
         f'=IF(AND(ISNUMBER(C{{r}}),ISNUMBER(D{{r}})),SUMPRODUCT(--(({_R("T")}<>"一致")<>(({_BAD})>0)))+C{{r}},"—")', 0, 0,
         "v10.3 F3 新增；v12.0 H7（查核 #87 觀察 1）：舊版以 COUNTA 對 COUNTIF(…,\"一致\")，T 欄被清空或手填『一致』時兩者同步改變、差值仍為 0。現改為不讀 T 公式的結果，直接由 I、J、L、M 欄與 CST_MainMin 重算每列應有的判定"
         "（主流＝L 有值取 L、否則 J ≥ CST_MainMin；主流但 M＝否，或非主流但 M＝是且狀態非『早期採用』，即實質不一致）。"
         "模型值＝重算後實質不一致的列數；對照值＝T 欄非『一致』（含空白）的列數；結果欄＝（T 欄是否一致與重算判定不符的列數）＋模型值，為 0 才通過：T 欄被清空、手填，或實質不一致（『主流但未入基準：須 Andy 判定』、『非主流卻在基準』）都會失敗。T 欄用 Andy 覆寫 L 欄（有值時取代 K）判讀"),
        ("V20", "MLPerf v6.0 offline：GB200 NVL72（NVIDIA 72 GPU，無 SLO，大批次）——模型 ÷ 實測，通過帶 0.5–2.0（批次口徑：η_d × CAL_BatchEtaD）【校準相關（非獨立），不計入驗證】", f"=Calib!C{CAL['L']['lout']}", "=SRC_PERF_079", None, 0.5, 2.0,
         "v11.0 G3：SRC_PERF_079（6,752；第二來源 CoreWeave 64 GPU 7,323＝SRC_PERF_082；Google 72 GPU 4,276 未登錄）；模型值＝Calib L 節 C 欄（輸入 800／輸出 3,880、無 SLO、批次填滿 HBM、η_d × CAL_BatchEtaD、含 prefill 分攤）；"
         "GB200 的 CAL_BatchEtaD 由 vLLM 10.1K 校準（Calib J 節 D 欄），本點不用於校準"
         "｜v12.0 H2：【校準相關（非獨立）】D156＝2.36＝√(1.83 × 3.04)，1.83 正是本點（MLPerf v6.0 offline 6,752）反推的倍數、3.04 由 vLLM 10.1K 反推，兩個校準點同時被用到，本點因此不再是獨立驗證點；"
         "F 欄顯示文字（帶內／帶外），不計入驗證項目數／通過／失敗"),
        ("V21", "MLPerf v6.0 offline：GB300 NVL72（NVIDIA 72 GPU，無 SLO，大批次）——模型 ÷ 實測，通過帶 0.5–2.0（批次口徑）", f"=Calib!D{CAL['L']['lout']}", "=SRC_PERF_080", None, 0.5, 2.0,
         "v11.0 G3：SRC_PERF_080（8,987；第二來源 Nebius 72 GPU 9,360＝SRC_PERF_083）；模型值＝Calib L 節 D 欄（同 V20；GB300 的 CAL_BatchEtaD＝1，未另校準）"),
        ("V22", "TensorRT-LLM H200 8 GPU（ISL 1K／OSL 2K，並行 1,024＝每 rank 128，EP8，無 SLO）：Hopper——模型 ÷ 實測，通過帶 0.5–2.0（批次口徑）", f"=Calib!E{CAL['L']['lout']}", "=SRC_PERF_081", None, 0.5, 2.0,
         "v11.0 G3：SRC_PERF_081（1,436；NVIDIA TensorRT-LLM 0.21.0rc1 文件，單一來源）；模型值＝Calib L 節 E 欄（H200 規格 141 GB／4.8 TB/s、EP8、固定批次 128、無 MTP、η_d × CAL_BatchEtaD、含 prefill 分攤）；"
         "Hopper 的 CAL_BatchEtaD 在 C68＝1.5 下無解而未寫入（＝1），此項的結果隨之偏低；不用於校準")
    ]
    import v1400                                      # v14.0 (4-3B Q4): V23–V26
    items += v1400.v_items(wb)
    for vid, lab, c, d, e, lo, hi, note in items:
        put(ws, f"A{r}", vid); put(ws, f"B{r}", lab, wrap=True)
        put(ws, f"C{r}", c, fmt="#,##0.000"); put(ws, f"D{r}", d, fmt="#,##0.000")
        put(ws, f"E{r}", (e or ratio(r)).replace("{r}", str(r)), fmt="0.000")
        if vid in SOFT_CAP:       # v11.0 G4: MLPerf server (V1–V3) is a soft cap: ratio > upper bound is a warning, not a failure
            # v12.0 H1: second line CHK_SoftCapFail (Calib M section): ratio <= I (1) pass; I < ratio <= CHK_SoftCapFail warn; ratio > CHK_SoftCapFail fail
            put(ws, f"F{r}", f'=IF(AND(ISNUMBER(E{r}),ISNUMBER(H{r})),IF(E{r}<H{r},0,IF(IF(ISNUMBER(I{r}),E{r}<=I{r},TRUE),1,IF(E{r}>CHK_SoftCapFail,0,"警示"))),"—")', F_BOLD, fmt="0")
        elif vid == "V18":        # v12.0 H7: identity (not a verification): text result, not counted
            put(ws, f"F{r}", f'=IF(ISNUMBER(E{r}),IF(E{r}=0,"恆等式（非驗證）","恆等式不成立（K 被改寫）"),"—")', F_BOLD)
        elif vid == "V20":        # v12.0 H2: calibration-related (not independent): text result, not counted
            put(ws, f"F{r}", f'=IF(AND(ISNUMBER(E{r}),ISNUMBER(H{r})),"校準相關（非獨立）："&IF(AND(E{r}>=H{r},IF(ISNUMBER(I{r}),E{r}<=I{r},TRUE)),"帶內","帶外"),"—")', F_BOLD)
        else:
            put(ws, f"F{r}", f'=IF(AND(ISNUMBER(E{r}),ISNUMBER(H{r})),IF(AND(E{r}>=H{r},IF(ISNUMBER(I{r}),E{r}<=I{r},TRUE)),1,0),"—")', F_BOLD, fmt="0")
        put(ws, f"G{r}", {"V18": "恆等式（非驗證）", "V20": "校準相關（非獨立）"}.get(vid, "驗證"), F_NOTE); put(ws, f"H{r}", lo, F_CALC, fmt="0.00")
        if hi is not None: put(ws, f"I{r}", hi, F_CALC, fmt="0.00")
        put(ws, f"J{r}", note, F_NOTE, wrap=True); r += 1
    last = r - 1
    for key, f in (("T", f'=COUNT(F{first}:F{last})+COUNTIF(F{first}:F{last},"警示")'), ("P", f"=SUM(F{first}:F{last})"),
                   ("F", f"=COUNT(F{first}:F{last})-F{sum_rows['P']}"), ("W", f'=COUNTIF(F{first}:F{last},"警示")')):      # v11.0 G4: T = numeric + warnings; F = numeric − pass; identity P + F + W = T
        put(ws, f"F{sum_rows[key]}", f, F_BOLD, fmt="0")
    wb.defined_names["CHK_VerifyTotal"] = DefinedName("CHK_VerifyTotal", attr_text=f"Checks!$F${sum_rows['T']}")
    wb.defined_names["CHK_VerifyPass"] = DefinedName("CHK_VerifyPass", attr_text=f"Checks!$F${sum_rows['P']}")
    wb.defined_names["CHK_VerifyFail"] = DefinedName("CHK_VerifyFail", attr_text=f"Checks!$F${sum_rows['F']}")
    wb.defined_names["CHK_VerifyWarn"] = DefinedName("CHK_VerifyWarn", attr_text=f"Checks!$F${sum_rows['W']}")      # v11.0 G4 (major version: new contract name)
    return dict(first=first, last=last, sums=sum_rows, nature=cnt)


# ================================================================== N3: new source records (SRC_Perf 060–065, SRC_Harness 016) and DB_Evidence
EID = "E378"
_MLP = "NVIDIA 提交；MLPerf Inference v5.1（2025-09）DeepSeek-R1，每 GPU（系統總量 ÷ GPU 數，3A 查證報告表）"


def _rec(i, sheet, metric, val, lo, hi, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note):
    return dict(id=i, sheet=sheet, metric=metric, val=val, lo=lo, hi=hi, unit=unit, basis=basis, applies=applies, date=date, src=src, grade=grade,
                stance=stance, stance_note=stance_note, hand=hand, status="Active", ev=EID, s="U-V1000", use=use, note=note)


_SRCTXT = f"{Q3A} 第 2 節（2026-10-15 CC 查證；原始出處見該表；本欄值轉引，未逐一回到原文重讀）"
SRC_NEW = [
    _rec("SRC_PERF_060", "SRC_Perf", "MLPerf v5.1 DeepSeek-R1 server：DGX H200（8 GPU）每 GPU", 556, None, None, "tok/s/GPU（輸出 token）", "server；Closed；NVIDIA 註明 Hopper 結果未經 MLCommons 驗證",
         "DGX H200（8 GPU；NVIDIA 提交）", "2025-09", _SRCTXT, 2, "利害關係方", "MLCommons 稽核為中立；提交者 NVIDIA 自行挑選配置；Hopper 結果 NVIDIA 註明未經 MLCommons 驗證", "二手（3A 查證轉引）",
         "Calib H 節 G 欄（Hopper 驗證點）；Checks V1", f"v10.0 N3 新增（{EID}）：Hopper 的 MLPerf 上限（v5.1 H200 server）；v6.0 的 Hopper 提交已搜尋未找到；H200 頻寬高於模型的 H100，上限偏寬"),
    _rec("SRC_PERF_061", "SRC_Perf", "MLPerf v5.1 DeepSeek-R1 server：GB200 NVL72（72 GPU）每 GPU", 2327, None, None, "tok/s/GPU（輸出 token）", "server；Closed",
         "GB200 NVL72（NVIDIA 提交）", "2025-09", _SRCTXT, 2, "利害關係方", "MLCommons 稽核為中立；提交者 NVIDIA 自行挑選配置", "二手（3A 查證轉引）",
         "Calib H 節 H 欄（GB200 驗證點）；Checks V2", f"v10.0 N3 新增（{EID}）：GB200 的 MLPerf 上限（v5.1 server）；同輪 offline 4,024"),
    _rec("SRC_PERF_062", "SRC_Perf", "LMSYS／SGLang DeepSeek-V3 decode：96×H100 每 GPU", 2785, None, None, "tok/s/GPU（輸出 token，decode GPU）", "輸入 2,000；ITL 約 100 ms；TTFT 2–5 秒；無明確 SLO；PD 分離",
         "Hopper H100（Atlas Cloud 機器）", "2025-05", _SRCTXT, 2, "利害關係方", "獨立複現，但 Atlas Cloud 有商業動機；SLO 寬鬆", "二手（3A 查證轉引）",
         "Checks V7（獨立驗證點，不用於校準）", f"v10.0 N3 新增（{EID}）：Hopper × Sol 級獨立驗證點；prefill 約 6,540 輸入 tok/s/GPU（未使用）"),
    _rec("SRC_PERF_063", "SRC_Perf", "LMSYS／SGLang DeepSeek decode：GB200 NVL72 每 GPU（NVFP4）", 13386, None, None, "tok/s/GPU（輸出 token，decode GPU）", "NVFP4；輸入 2,000；decode 48 rank；無 TPOT；原精度為 9,087",
         "GB200 NVL72", "2025-09", _SRCTXT, 2, "利害關係方", "與 NVIDIA 合作，Interested-party 成分高；無明確 SLO", "二手（3A 查證轉引）",
         "Checks V8（獨立驗證點，不用於校準）", f"v10.0 N3 新增（{EID}）：GB200 × Sol 級獨立驗證點；原精度 9,087、prefill 26,156／18,471（未使用）"),
    _rec("SRC_PERF_064", "SRC_Perf", "Olmo 3 32B Think：RL ÷ 預訓練 GPU 時間", 0.11, None, None, "x", "GPU 天比（RL continuation 21 天 × 224 GPU ÷ 預訓練約 43,300 GPU 天，3A 本表相除）",
         "Olmo 3 32B Think（AI2）", "2025-12", _SRCTXT, 2, "中立", "開放實驗室，可核對；GPU 天口徑與模型的 GPU 小時口徑一致", "二手（3A 查證轉引）",
         "Checks V9、V10（RL 對照，不用於校準）", f"v10.0 N3 新增（{EID}）：RL 對照；首輪 RL 約 5 天、GPU 數未寫"),
    _rec("SRC_PERF_065", "SRC_Perf", "DeepSeek-V3.2：後訓練預算 ÷ 預訓練成本（下限式）", None, 0.1, None, "x", "成本口徑（下限式：超過 10%）", "DeepSeek-V3.2", "2025-12", _SRCTXT, 2, "利害關係方", "公司自述",
         "二手（3A 查證轉引）", "Checks V9、V10（RL 對照，不用於校準）", f"v10.0 N3 新增（{EID}）：RL 對照下限；成本口徑，非 GPU 小時"),
    _rec("SRC_HAR_016", "SRC_Harness", "SWE Atlas：原生 scaffold ÷ mini-SWE-agent 工具呼叫數", None, 1.5, 2.0, "x", "Opus 4.6：Claude Code 約 100 對 56；GPT-5.4：Codex 約 82 對 58（讀自圖上標籤）；工具呼叫數不等於輪數",
         "SWE Atlas（arXiv 2605.08366）", "2026-05", _SRCTXT, 2, "中立", "論文，無廠商利益；數字讀自圖上標籤", "二手（3A 查證轉引）",
         "Checks V11（方向證據，只判方向）", f"v10.0 N3 新增（{EID}）：harness 輪數方向對照；原生 scaffold 傾向呼叫更多而非更少，與模型 0.7 方向相反"),
]


def src_new_records():
    return SRC_NEW


_IDS = "；".join(x["id"] for x in SRC_NEW)
EVIDENCE_V1000 = [[
    EID, DATE,
    "D5 獨立驗證材料：MLPerf v5.1 的 H200（server 556）與 GB200 NVL72（server 2,327）每 GPU；LMSYS／SGLang 的 H100 decode 2,785 與 GB200 decode 13,386（NVFP4）；Olmo 3 RL ÷ 預訓練約 0.11、DeepSeek-V3.2 後訓練 ≥ 10%；SWE Atlas 原生 scaffold 工具呼叫多 1.5–2 倍",
    f"{Q3A} 第 2、3 節（CC 查證，2026-10-15；各項原始出處見該報告）", "二手轉引（3A 查證）", "Checks V 節；Calib H 節 G、H 欄",
    "Calib H 節只有 4 個 MLPerf 驗證點（GB300、GB200 v6.0、VR200）；無 Hopper；Checks 無獨立吞吐驗證點", "新增 Hopper／GB200 的 v5.1 server 上限、兩個 LMSYS 獨立驗證點、RL 與 harness 對照",
    "採納為驗證材料（不用於校準）；MLPerf 為上限檢查（模型 ÷ MLPerf ≤ 1），LMSYS 帶 0.5–2.0，RL 帶 0.1–0.3，harness 輪數 ≥ 1 只判方向", V,
    f"讀取者：chat 端（3A 查證）；CC 轉入｜{CHAT_DEF}｜LMSYS 兩點無明確 SLO、NVIDIA 關係；MLPerf 提交者多為廠商，一律 Interested-party；v6.0 的 Hopper 提交已搜尋未找到",
    "已處理", _IDS, DASH, "Checks V 節（驗證計數）；L1／IF_／IFW_ 數值不變", "2（轉引）", "利害關係方"]]


def evidence_rows():
    return EVIDENCE_V1000


# ================================================================== Decisions (10 columns; layout of v800／v810)
_D = [
    ("N1", "D12 自算 L、m 情境欄（不回流）", "Interface 新增 L 節：IFW_*_LifeSelf＝IFW_*_Prod × L1_LTotal × L1_MFleet（8 個營收名稱：RevGW 三層級、RevGWFleet、RevGWFront 三層級、RevGWFleetFront）；控制值 CTL_PriceLife、CTL_Monetize 仍為 1，IFW_*_Life 不變。"
     "不得有任何公式讀取這些名稱（parity 測試：Interface、Load_Bearing、Gov_Map 以外引用數＝0）。標籤「情境：自算 L、m（L1_LTotal、L1_MFleet）；不回流，不建議下游作為基準」。"
     "產能名稱 IFW_TokGW_*_Life 沒有 L、m 作用層（Prod × 1），不建 LifeSelf——列待 Project 判斷。", "Interface L 節；tests/parity", "v10.0 已建"),
    ("N2", "D4 殘差與倒推明示", "L1 新增 T 欄「性質」（估計、殘差、倒推、恆等式、未解釋）與 U 欄理由，逐列填寫；m 各分項為殘差，L1_ScaleRD／ScaleServe／AstraScale 為未解釋，AL_ImpliedNk／AL_J8Gap 為倒推，L1_LReqFleet_Id 為恆等式。"
     "缺口分解新增 L1_GapUnexplained（L1_ScaleServe2000 ÷ L1_GapProduct；四項乘積≠實際缺口，故未解釋≠1），第 74 列改標「已解釋部分」。Calib C67／C68 標記沿用（Derived（粗略）、倒推）；Train_In H34 補「倒推」。",
     "L1 T／U 欄；L1_GapUnexplained；Train_In H34；Alloc 隱含 N × k／J8 落差", "v10.0 已建"),
    ("N3", "D5 驗證必須能失敗", "Checks 新增 G 欄「性質」（驗證／恆等式（非驗證）／對照／治理）與 V 節驗證計數 CHK_VerifyTotal／CHK_VerifyPass／CHK_VerifyFail，只計能失敗的檢查；失敗不進 GOV_Errors，報告列出。"
     "恆等式移出計數（Checks B14、B26、B52、B56、B61、D105、D110、D114、D120、D121、D132、D136、Interface 第 229 列，另找出 B36、B60、D104、D140）。"
     "MLPerf 改上限檢查（模型 ÷ MLPerf ≤ 1）：Calib H 節新增 G、H 欄（Hopper H200 v5.1 server、GB200 v5.1 server），共 6 點；LMSYS 兩點（Hopper Sol、GB200 Sol）通過帶 0.5–2.0；RL（Luna、Sol）通過帶 0.1–0.3；"
     "harness 輪數倍數 ≥ 1（基準 0.7 預期失敗，如實顯示）；另納入 Checks B15–B17 三個樣本外點。新增 SRC_PERF_060–065、SRC_HAR_016，DB_Evidence E378。", "Checks G 欄、V 節；Calib H 節；SRC_Perf／SRC_Harness", "v10.0 已建"),
    ("N4", "2-4 後續（報告第 9 節）", "第 2 項 Perf_Batch 標「訓練端批次推論，無服務快取」；第 3 項 Perf TTFT 列註明新鮮 token 位於後段、本式略低估 prefill 時間；第 4 項 κ 維持乘法、寫明定義；第 5 項 AL_FreeShare 說明欄註明產業總量未必同；"
     "第 6 項 H10 C 欄 2025 口徑（已在 v9.0）；第 7 項 Hopper 服務 Astra 保留（SLO 判定的物理結果）；第 8 項字面讀法改標「口徑不一致，僅供對照」，L1 判讀欄只用恆等式讀法（取消 ≤10% 自動改用字面讀法）；"
     "第 9 項 B4_CacheHit 區間下限不動，情境 d9_cache_cap_off 說明欄註明會觸發 Checks E10。", "Perf／Sens_Perf／Perf_Prod 第 76 列；Perf_Batch A2；Alloc_In G16／G26；L1_LReqFleet；scenarios.yaml", "v10.0 已建"),
    ("N5", "下游契約", "契約新增 N1 名稱（IFW_*_LifeSelf，不回流）、N3 驗證計數（CHK_Verify*，只供讀取）、N4 第 8 項回本讀法；第 5 節補 v9.0、v10.0 條目。", "docs/plan/Tokenomics_downstream_contract.md", "v10.0 已建"),
]
DECISIONS_V1000 = [[f"AF2f-{i}", V, f"稽核修正第 2 批 2-5：{t}", txt, DATE, CHAT_DEF, st, where, f"{WO} {i}", "否"] for i, t, txt, where, st in _D]

# ================================================================== README
README_VERSION = (VERSION + "（主版：稽核修正第 2 批 2-5 段，" + WO + "——D12：Interface L 節 IFW_*_LifeSelf（自算 L、m 情境，不回流）；D4：L1 性質欄與未解釋列；D5：Checks 性質欄、V 節驗證計數 CHK_Verify*、"
                  "MLPerf 上限檢查（Calib H 節新增 Hopper／GB200 v5.1 server）、LMSYS 獨立驗證點、RL 與 harness 對照；2-4 後續標籤；Decisions AF2f-*）。以下為 " + v810.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v810.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v810.VERSION.split("_")[-1]):]
README_ROW = ("D12／D4／D5：自算 L、m 情境、性質欄、驗證計數（v10.0）",
              "稽核修正 2-5：IFW_*_LifeSelf（不回流）；L1 性質欄與未解釋列；Checks 驗證計數（能失敗的檢查）與 MLPerf 上限、LMSYS、RL、harness 對照。標記與理由見 Decisions AF2f-*。")

# v5.29 (work order docs/workorders/20261008_v5.29.md r1): output contract columns, four-layer waterfall, fleet break-even and
# per-MW rows, Load_Bearing sheet, gap decomposition; X14 (a)–(m), G16 (work order says G15; that ID already exists).
#   0 (k) SRC_DEM_018 (OpenAI 2025 inference spend, Azure billing, full-year estimate) replaces SRC_DEM_004 (Superseded);
#         builder-owned formulas that read the inference spend (Alloc E／F, L1 external columns) now read SRC_DEM_018
#   0 (l) Alloc_In 每則提示 token 數 2,000 -> 4,000 (range 2,000–6,400); written only while the cells still hold the v5.28 values
#   1   Interface R–U (Confidence／Decision Use／口徑層／最弱輸入更新日) + helpers V–Y; Gov_Map helper columns AG–AJ; SRC_Index F
#   2   Interface J: IFW_<name>_100／_Util／_Prod／_Life for 8 revenue rows and 3 IF_TokGW rows, with self-check flags (Checks K3)
#   3／3b L1 rows (fleet break-even／margin, per-MW holding cost, generation ratios, harness vs generation, Astra external anchor,
#         scale factors, gap decomposition); two new Assumed inputs and one constant on Alloc_In (Gov_Map rows)
#   4   Load_Bearing sheet (static expansion: the engine, pycel, has no FILTER)
#   5   SRC_Price X–AB (five empty tier columns; check columns move to AC–AE／AM)
#   6   DB_Evidence E256–E262, Decisions X14a–X14m／G16, Gov_Map notes, README, Checks K
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v527, so a rebuild never overwrites a later Excel edit.
import re
from copy import copy
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY, FILL_SEC, section, title
import v518
import v527

VERSION = "20261008_Tokenomics_v5.29"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-08"
V = "v5.29"
DASH = "—"
SLO = "SLO 不可達"
COLS = range(3, 18)                         # C:Q
ANDY_DESIGN = "Andy 2026-10-08：同意你的設計／三件一起做（整合版評估報告 docs/reports/20261008_eval_integrated.md）"
ANDY_ADVICE = "Andy 2026-10-08「依建議」（docs/evidence/20261008/summary.md 待 Andy 判定 3 項）"

SPEND_SID = "SRC_DEM_018"                   # inference spend record used by builder-owned formulas from v5.29 on
OLD_SPEND_SID = "SRC_DEM_004"


def _nm(wb, n, ref):
    if n in wb.defined_names: del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


def _last_row(ws):
    return max(c.row for row in ws.iter_rows() for c in row if c.value is not None)


def _row_by_label(ws, label, col=1):
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, col).value == label: return r
    raise KeyError(f"{ws.title}: label not found: {label}")


def _name_row(wb, name):
    m = re.match(r"^(?:'([^']+)'|([^!]+))!\$?([A-Z]+)\$?(\d+)", wb.defined_names[name].attr_text)
    return (m.group(1) or m.group(2)), int(m.group(4))


# ================================================================== 0 (k): SRC_DEM_018 and SRC_DEM_004 superseded
E259_SRC = ("Where's Your Ed At《The OpenAI documents》（https://www.wheresyoured.at/oai_docs/，2025-11-12；文件為該刊所見，未公開；FT 報導雙方未評論）；"
            "chat 端 2026-10-08 讀取（二手）")
SRC_DEM = [dict(
    id=SPEND_SID, sheet="SRC_Demand", metric="OpenAI 2025 推論支出（Azure 帳單，全年推估）", val=12.6, lo=12.3, hi=13.0, unit="$B",
    basis="Azure 計價，含 Microsoft 利潤與資本回收；Q1–Q3 實際 8.67（Q1 2.075、Q2 2.947、Q3 3.648）＋ Q4 以 Q3 run-rate 至 +15% 推估",
    applies="OpenAI", date="2025", src=E259_SRC, grade=2, stance="利害關係方", stance_note="OpenAI 內部文件經媒體轉述（文件未公開）；Microsoft 分成 20%",
    hand="二手（文件未公開）", status="Active", ev="E259", s="U-V529",
    use="Alloc!E 節（AL_SpendRatio）、F 節（AL_ServeGWSpend、AL_FreeSpendShare）；L1 外部對照（L1_ExtServeGW、L1_ExtFreeShare、L1_Ans5_GM、L1_FleetMargin）｜換算",
    note=f"v5.29 X14 (k) 新增，取代 {OLD_SPEND_SID}（8.4，openai_token_revenue.json）；全年 12.6＝8.67＋Q4 3.648 × 1.075（區間：Q4＝Q3 run-rate 12.3 至 +15% 13.0）；"
         "口徑為 Azure 計價，不等於持有成本口徑（L1_GapSpendBasis 另以 Assumed 倍數換算）")]
DEM004_NOTE = f" ｜v5.29 X14 (k)：{DATE} 改 Superseded，取代者 {SPEND_SID}（E259：2025 Q1–Q3 實際 8.67 $B 已高於本筆 8.4）；Cap_In C28 換算仍以本筆為據（G0-2 保留）"


def src_new_records():
    return SRC_DEM


def src_update(wb):
    """SRC_DEM_004: O Active -> Superseded, P — -> SRC_DEM_018 (only while still at the old values); W note appended once."""
    ws = wb["SRC_Demand"]; n = 0; log = []
    row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == OLD_SPEND_SID), None)
    if row is None: return 0, [f"{OLD_SPEND_SID} not found"]
    for col, spec in (("O", ("Active", "Superseded")), ("P", (DASH, SPEND_SID)), ("W", ("+", DEM004_NOTE))):
        if v518._apply(ws[f"{col}{row}"], spec): n += 1; log.append(f"SRC_Demand!{col}{row} {OLD_SPEND_SID} updated")
        else: log.append(f"{OLD_SPEND_SID}!{col}: kept (already applied or edited)")
    return n, log


# ================================================================== 0 (l): Alloc_In 每則提示 token 數 (Excel-owned; old-value guards)
TOK_LABEL = "每則提示 token 數"
TOK_UPD = [("C", 2000, 4000), ("D", 1000, 2000), ("E", 6000, 6400)]
TOK_NOTE = ("｜v5.29 X14 (l)：E261——OpenRouter 2025 年末每請求 6,400（含推理，SRC_DEM_014／015）與 Robonomics 假設 800–2,000 的幾何中點；"
            "上限改為 OpenRouter 實測")


def inputs_update(wb):
    ws = wb["Alloc_In"]; log = []
    r = _row_by_label(ws, TOK_LABEL)
    for col, old, new in TOK_UPD:
        c = ws[f"{col}{r}"]
        if c.value == old and type(c.value) is not bool:
            c.value = new; c.font = copy(F_IN); c.fill = PatternFill(fill_type=None)
            log.append(f"Alloc_In!{col}{r}: {old!r} -> {new!r} (v5.29 X14 l)")
    if v518._append_text(ws[f"G{r}"], TOK_NOTE): log.append(f"Alloc_In!G{r}: note appended (v5.29 X14 l)")
    return log


# ================================================================== 3b inputs: Alloc_In new rows (code defaults apply only to NEW input rows)
LAB_SPEND = "推論支出計價 ÷ 持有成本（v5.29 X14 (m)）"
LAB_UTIL = "實際利用率 × 生產折減（v5.29 X14 (m)）"
LAB_CST = "每則提示 token 數 v5.28 基準（常數，落差分解分母；CST_TokPerPromptV528）"
NEW_IN = [  # (label, unit, base, lo, hi, tag, note, stem)
    (LAB_SPEND, "x", 2.0, 1.5, 3.0, "Assumed",
     "X14 (m)／E262：支出路線的推論支出為 Azure 計價（含 Microsoft 利潤與資本回收），對持有成本口徑的倍數無公開數字；已搜尋未找到 OpenAI 對 Azure 實付單價", "SpendBasis"),
    (LAB_UTIL, "x", 0.35, 0.3, 0.4, "Assumed",
     "X14 (m)／E262：實際利用率 × 生產折減低於模型的 IF_Util × CTL_ProdDerate（0.6 × 0.85）；無直接證據，Serving C17／C18 為 Assumed", "UtilActual"),
]
CST_VAL = 2000


def alloc_in_rows(wb):
    """Appended after the existing Alloc_In content (nothing moves). Returns dict stem -> row."""
    ws = wb["Alloc_In"]
    r = _last_row(ws) + 2
    section(ws, r, "v5.29 X14 (m)：token 對帳落差分解的輸入（Assumed，附區間；登錄 Gov_Map）與 v5.28 基準常數", 7); r += 1
    R = {}
    for lab, unit, base, lo, hi, tag, note, stem in NEW_IN:
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        put(ws, f"C{r}", base, F_IN, fmt="0.00", fill=FILL_KEY); put(ws, f"D{r}", lo, F_IN, fmt="0.00"); put(ws, f"E{r}", hi, F_IN, fmt="0.00")
        put(ws, f"F{r}", tag); put(ws, f"G{r}", note, F_NOTE, wrap=True)
        _nm(wb, f"AL_{stem}", f"Alloc_In!$C${r}"); _nm(wb, f"AL_{stem}_Lo", f"Alloc_In!$D${r}"); _nm(wb, f"AL_{stem}_Hi", f"Alloc_In!$E${r}")
        R[stem] = r; r += 1
    put(ws, f"A{r}", LAB_CST, wrap=True); put(ws, f"B{r}", "tok"); put(ws, f"C{r}", CST_VAL, F_IN, fmt="#,##0")
    put(ws, f"D{r}", DASH); put(ws, f"E{r}", DASH); put(ws, f"F{r}", "Decision（X14m）")
    put(ws, f"G{r}", "L1_GapPrompt 的分母：每則提示 token 數的 v5.28 基準值 2,000（X14 (l) 改為 4,000 之前的值）；固定常數，不隨區間變動", F_NOTE, wrap=True)
    _nm(wb, "CST_TokPerPromptV528", f"Alloc_In!$C${r}"); R["CST"] = r
    return R


def gov_map_rows(wb):
    """Gov_Map rows for the three new Alloc_In cells (same dict format as v522.GOV_MAP_V522; appended by gov.gm_append_c when absent)."""
    ws = wb["Alloc_In"]
    rs, ru, rc = _row_by_label(ws, LAB_SPEND), _row_by_label(ws, LAB_UTIL), _row_by_label(ws, LAB_CST)
    sc = "切片三（v5.29 X14 (m)）"
    out = []
    for r, lab, lo, hi, reason in ((rs, LAB_SPEND, 1.5, 3.0, NEW_IN[0][6]), (ru, LAB_UTIL, 0.3, 0.4, NEW_IN[1][6])):
        out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '基準', 'src': '', 'rel': '',
                    'dec': 'X14m', 'lo': f'=Alloc_In!D{r}', 'hi': f'=Alloc_In!E{r}', 'rtext': f'{lo}–{hi}（chat 端提案，Andy 2026-10-08「依建議」）',
                    'reason': reason + "；只進 L1 落差分解列，不進任何 IF_ 輸出", 'retag': '', 'seg': '中'})
        out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'D{r}:E{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '低／高', 'src': '', 'rel': '',
                    'dec': 'X14m', 'lo': None, 'hi': None, 'rtext': f'C{r} 的低、高端點', 'reason': reason, 'retag': '', 'seg': '—'})
    out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'C{rc}', 'label': LAB_CST, 'check': LAB_CST, 'cls': 'Decision', 'role': '單值', 'src': '', 'rel': '',
                'dec': 'X14m', 'lo': None, 'hi': None, 'rtext': '固定常數（v5.28 基準值 2,000；不隨區間變動）',
                'reason': 'X14 (l)／(m)：L1_GapPrompt＝新每則 token 數 ÷ v5.28 基準 2,000；分母固定，使落差分解可逐項驗證', 'retag': '', 'seg': '無'})
    return out


# ================================================================== 6: Gov_Map notes (guarded append) and GM453 link 004 -> 018
NOTE_BE = " ｜v5.29：進 L1_FleetBreakeven／L1_FleetMargin，X14 (c)"
NOTE_TOK = " ｜v5.29 X14 (l)：基準 2,000 → 4,000、區間 2,000 → 6,400（E261）；L1_GapPrompt 以 v5.28 基準 2,000 為分母"
NOTE_453 = (f" ｜v5.29 X14 (k)：SRC_ID {OLD_SPEND_SID} → {SPEND_SID}（12.6 $B，Azure 計價）；換算 12.6 ÷（12.6＋12）＝0.512，C28 0.41 不改（G0-2 保留，待 Stage 2 判斷）")
GOV_CHECK = {"GM236": ("Serving", "C17"), "GM237": ("Serving", "C18"), "GM593": ("Cap_In", "C63"), "GM594": ("Cap_In", "C64"),
             "GM586": ("Alloc_In", "C15"), "GM453": ("Cap_In", "C28")}
GM586_M = (DASH, "2,000–6,400（X14 (l)：下限 Robonomics 假設上緣，上限 OpenRouter 實測 6,400，E261）")


def gov_update(ws, append_text):
    rows = {ws[f"A{r}"].value: r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value}
    for gm, (sh, cell) in GOV_CHECK.items():
        r = rows[gm]
        assert (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sh, cell), f"Gov_Map {gm} is {ws[f'C{r}'].value}!{ws[f'D{r}'].value}, expected {sh}!{cell}"
    n = 0
    for gm in ("GM236", "GM237", "GM593", "GM594"):
        if append_text(ws[f"N{rows[gm]}"], NOTE_BE): n += 1
    r = rows["GM586"]
    if ws[f"M{r}"].value == GM586_M[0]: ws[f"M{r}"].value = GM586_M[1]; n += 1
    if append_text(ws[f"N{r}"], NOTE_TOK): n += 1
    r = rows["GM453"]
    if ws[f"H{r}"].value == OLD_SPEND_SID: ws[f"H{r}"].value = SPEND_SID; n += 1
    if append_text(ws[f"N{r}"], NOTE_453): n += 1
    return n


# ================================================================== 6: DB_Evidence E256–E262 (17 columns A..Q; same layout as v527)
_CSV = "docs/evidence/20261008/candidates.csv"
EVIDENCE_V529 = [
    ["E256", DATE,
     "Google 每月處理 token：2024 年 9.7T／2025-05 480T／2025-06 980T／2025-10 1.3Q／2026-05 3.2Q（Pichai，I/O 與 Cloud 活動）",
     "https://www.shacknews.com/article/149205/google-3-2-quadrillion-monthly-ai-tokens；https://the-decoder.com/google-boasts-1-3-quadrillion-tokens-each-month-but-the-figure-is-mostly-window-dressing/",
     "Interested-party／2 級（轉述；原文為 keynote）", "SRC_DEM_013 對照（前沿實驗室每日 token 量級）", "OpenAI 推估 10–100T/日",
     "Google 2025 平均約 1Q/月＝33T/日；2026-05 達 107T/日", "並列（Alt）", V,
     f"非 OpenAI 數字，不取代；作為前沿實驗室量級的中立對照：OpenAI 2025 需求 D 11.5T/日約為 Google 同期的 1/3，落在合理量級，不支持「D 低估 14 倍」｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", "SRC_DEM_013", DASH, "無（對照）", "2", "利害關係方"],
    ["E257", DATE,
     "Microsoft FY25 Q3：本季處理逾 100T token（YoY 5x），上月 50T；FY26 Q3：300 家客戶年處理逾 1T，AI ARR $37B",
     "https://www.microsoft.com/en-us/investor/events/fy-2025/earnings-fy-2025-q3；https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q3",
     "Interested-party／1 級（一手已讀）", "SRC_DEM_010 對照（API 處理量）", "6B tok/min（8.6T/日）", "Azure AI 2025-03 約 1.7T/日", "並列（Alt）", V,
     f"Azure 經銷的 OpenAI 流量只占 OpenAI API 的一小部分（約 1/5）；不改 SRC_DEM_010｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", "SRC_DEM_010", DASH, "無（對照）", "1", "利害關係方"],
    ["E258", DATE,
     "中國：2026-02 主流模型日均 180T token；國家數據局 2025-06 底日均逾 30T；Doubao 逾 50T/日",
     "https://robonomics.substack.com/p/token-tracker-and-implications（轉述新浪財經、國新辦）", "2 級／二手", "SRC_DEM_013 對照", DASH, DASH, "並列（Alt）", V,
     f"量級對照：單一領先實驗室 2025 底至 2026 初日均 10–50T；OpenAI 11.5T（2025 平均）在範圍內｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", "SRC_DEM_013", DASH, "無（對照）", "2", "未明（轉述）"],
    ["E259", DATE,
     "OpenAI 推論支出（Azure）：2024 全年 $3.767B；2025 Q1 $2.075B、Q2 $2.947B、Q3 $3.648B，至 2025-09 累計 $8.67B；Microsoft 營收分成 20%",
     "https://www.wheresyoured.at/oai_docs/（2025-11-12，文件為該刊所見，FT 報導雙方未評論）", "Interested-party／2 級（文件未公開）",
     f"{OLD_SPEND_SID}（OpenAI 2025 推論支出 $8.4B）", "8.4 $B", "Q1–Q3 已 8.67；全年依 Q3 run-rate 約 12.3–13（區間）",
     f"採納（X14 (k)）：新增 {SPEND_SID}＝12.6（12.3–13.0），{OLD_SPEND_SID} 改 Superseded", V,
     f"新值高於現值；採用後支出路線服務 GW 由 0.74 升至約 1.1。此支出為 Azure 計價（含 Microsoft 利潤與資本回收），不等於持有成本口徑；見 summary 的分解（L1_GapSpendBasis）｜{ANDY_ADVICE}｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", f"{SPEND_SID}；{OLD_SPEND_SID}", SPEND_SID, "L1_ExtServeGW、L1_ExtFreeShare、L1_Ans5_GM 外部欄；Alloc E／F 節（AL_SpendRatio、AL_ServeGWSpend、AL_FreeSpendShare）；IF_AllocImpliedNk", "2", "利害關係方"],
    ["E260", DATE,
     "OpenAI API 處理量 2026-03 逾 15B tok/min（SRC_DEM_011 已登錄）對 2025-10 6B：6 個月 2.5 倍；2025 全年平均 ÷ 10 月時點值 0.75（Alloc_In Assumed）隱含 1–10 月成長約 1.5 倍，與此成長率一致",
     "SRC_DEM_010、SRC_DEM_011（既有）", DASH, "Alloc_In「API 全年平均 ÷ 10 月時點值」", "0.75（0.6–0.9）", "不改", "不採納（維持）", V,
     f"既有證據已支持現值，只記錄核對｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄", "已處理", "SRC_DEM_010；SRC_DEM_011", DASH, "無", DASH, DASH],
    ["E261", DATE,
     "每則提示 token 數：OpenRouter 2025 年末每請求平均 6,000 輸入＋400 輸出（含推理）（SRC_DEM_014／015 已登錄）；Robonomics 作者假設 ChatGPT 每則 800–2,000",
     "SRC_DEM_014、SRC_DEM_015；https://robonomics.substack.com/p/token-tracker-and-implications", "1 級（OpenRouter 一手已讀）；2 級（作者假設）",
     "Alloc_In「每則提示 token 數」（GM586 高段 Assumed）", "2,000（1,000–6,000）", "建議基準改 4,000、區間 2,000–6,400（上限改為 OpenRouter 實測）",
     "採納（X14 (l)）：Alloc_In C15 4,000、D15 2,000、E15 6,400", V,
     f"ChatGPT 每則提示含多輪上下文重新 prefill 與推理 token，OpenRouter 6,400 為 API 代理流量（偏長）、800–2,000 為無來源假設；取兩者幾何中點。影響：ChatGPT token 5T/日 → 10T/日，D 11.5 → 16.5T/日，token 路線服務 GW 0.052 → 0.075｜{ANDY_ADVICE}｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", "SRC_DEM_014；SRC_DEM_015；SRC_DEM_012", DASH, "IF_AllocQ1、IF_AllocQ1_R2、IF_AllocQ2、IF_AllocServeGW、IF_AllocDemand、IF_AllocImpliedNk；L1_Ans1–3、L1_ExtServeGW、L1_ExtDaily、L1_ExtFreeShare", "1", "利害關係方"],
    ["E262", DATE,
     "token 對帳落差分解（chat 端推導，非外部證據）：落差＝每則 token（×1.5–2）× 支出口徑含 Azure 利潤與資本回收（×1.5–3，Assumed）× 參考請求 ISL 16K 對實際混合（×1.5–2.3，Sens_Perf ISL 4K 欄）× 實際利用率低於 60%（×1.5–2）；乘積 5–28，涵蓋觀測 14",
     "docs/evidence/20261008/summary.md", "Derived／Assumed", "L1_ExtServeGW；輸出契約第 2 條、第 5 條", "比值 0.07", DASH,
     "採納（X14 (m)）：L1 新增 L1_GapPrompt／GapSpendBasis／GapISL／GapUtil／GapProduct；Alloc_In 新增兩個 Assumed 輸入", V,
     f"結論：落差不是單一錯誤，而是四個口徑差的乘積；契約須寫明 IF_TokGW 為「參考請求、100%／60% 口徑」，下游以自身請求組合與利用率換算｜{ANDY_ADVICE}｜讀取者：chat 端（{_CSV}）；CC 依 CSV 登錄",
     "已處理", DASH, DASH, "L1_GapPrompt、L1_GapSpendBasis、L1_GapISL、L1_GapUtil、L1_GapProduct（新列；IF_ 不變）", DASH, DASH],
]


def evidence_rows():
    return EVIDENCE_V529


# ================================================================== 6: Decisions X14a–X14m, G16 (10 columns; same layout as v527)
_X14 = [
    ("a", "輸出契約欄", "Interface 每一列附 Confidence（A／B／C）、Decision Use、口徑層、最弱輸入更新日四欄（R–U），全部由公式自 Gov_Map 與 SRC 徙出，不手填；依賴的 Gov_Map 列由 builder 建置時反查（靜態展開），判斷欄仍即時讀 Gov_Map"),
    ("b", "四層瀑布", "四層瀑布為正式口徑：100% → × IF_Util → × CTL_ProdDerate → × L × m。既有 D／G／H 節列不動，新增 J 節把同一指標的四層並列（IFW_），供下游一次取齊"),
    ("c", "機隊損益兩平列", "L1_FleetBreakeven＝IF_HoldEcon ÷（IF_RevGWFleet ÷ IF_Util）（VR200 基準欄；令機隊營收等於持有成本所需的「利用率 × 折減 × L × m」乘積）與 L1_FleetMargin＝IF_Util × CTL_ProdDerate × CTL_PriceLife × CTL_Monetize ÷ L1_FleetBreakeven"),
    ("d", "每 MW 介面", "新增 L1_HoldEconMW_*（每世代，＝L1_HoldEconGW_* ÷ 1000）與 L1_TokMW_Gen_ratio_*（相鄰世代 Sol 每 GW 總產出比，附低高）；Tokenomics 不輸出每 MW 收入，下游依 q × p × c × 簽約率自算"),
    ("e", "harness 對世代比較", "L1_HarVsGen_<task>＝（選定 ÷ 標準 每成功任務成本，VR200）÷（VR200 ÷ GB300 decode $/M，Sol）；依 Workload 五個任務分列；基準仍 L3（w＝0）、L4 不動"),
    ("f", "Astra 雙基準", "L1 第 36 列保留 bottom-up，新增 L1_PretrainFLOP_Astra_Ext＝SRC_MOD_055（external-anchor，低高＝_Lo／_Hi）與 L1_AstraScale＝Ext ÷ bottom-up；不改 Train_In、Arch 任何輸入（X13 (e)）"),
    ("g", "規模係數", "新增 L1_ScaleRD＝SRC_DEM_006 ÷ L1_Ans3 與 L1_ScaleServe＝支出路線服務 GW ÷ token 路線服務 GW；兩列進輸出契約，Decision Use＝「下游校準用，不得當產能」"),
    ("h", "Load_Bearing 頁", "由 Gov_Map 篩出「CC 敏感度分段＝高」且類別為 Assumed／Analogy 的格（engine 不支援 FILTER，builder 靜態展開，各欄即時連結 Gov_Map），加反轉門檻欄（本版空白）"),
    ("i", "Block 6 代表性實驗室", "Decisions 新增 G16（工作單稱 G15，該 ID 已被 Stage 2 等級規則使用）：Block 6 以 OpenAI 為代表性實驗室代理；其他實驗室模型須自行覆寫 Alloc_In（P2-3）"),
    ("j", "每 MW 收入 50/50 平均停用", "屬下游模型事項（Nebius／Oracle 現行）：只在 Decisions 登錄 X14 (d) 供下游引用，不在 Tokenomics 內處理"),
    ("k", "SRC_DEM_004 取代", f"新增 {SPEND_SID}「OpenAI 2025 推論支出（Azure 帳單，全年推估）」＝12.6 $B、低 12.3、高 13.0（等級 2、利害關係方、二手、Evidence E259）；{OLD_SPEND_SID} 改 Superseded、取代者 018（G5）；Gov_Map GM453 與 builder 擁有的推論支出公式（Alloc E／F 節、L1 外部欄）改連 018"),
    ("l", "每則提示 token 數", "Alloc_In「每則提示 token 數」2,000 → 4,000，區間 2,000–6,400（E261：OpenRouter 6,400 與 Robonomics 800–2,000 的幾何中點；上限改為 OpenRouter 實測）；標記維持 Assumed"),
    ("m", "token 對帳落差分解列", "L1 新增 L1_GapPrompt、L1_GapSpendBasis、L1_GapISL、L1_GapUtil、L1_GapProduct（第 3b 節；兩個新 Assumed 輸入：推論支出計價 ÷ 持有成本 2.0［1.5–3.0］、實際利用率 × 生產折減 0.35［0.3–0.4］）；契約第 2 條第 5 項改寫為四項口徑差的逐項換算"),
]
DECISIONS_V529 = [
    [f"X14{k}", V, f"X14 ({k}) {t}", txt, DATE, ANDY_ADVICE if k in "klm" else ANDY_DESIGN, "v5.29 已建",
     {"a": "Interface R–U（IFC_）、Gov_Map AG–AJ、SRC_Index F、Checks K1／K2", "b": "Interface J 節（IFW_）、Checks K3",
      "c": "L1_FleetBreakeven、L1_FleetMargin；Gov_Map GM236／GM237／GM593／GM594 理由欄；Checks K4", "d": "L1_HoldEconMW_*、L1_TokMW_Gen_ratio_*",
      "e": "L1_HarVsGen_*（5 列）", "f": "L1_PretrainFLOP_Astra_Ext、L1_AstraScale", "g": "L1_ScaleRD、L1_ScaleServe", "h": "Load_Bearing；Checks K5／K6",
      "i": "Decisions G16", "j": "無（下游）", "k": f"SRC_Demand {SPEND_SID}／{OLD_SPEND_SID}；Gov_Map GM453；Alloc E／F 節；L1 外部欄；DB_Evidence E259",
      "l": "Alloc_In C15:E15、G15；Gov_Map GM586；DB_Evidence E261", "m": "Alloc_In 新列（AL_SpendBasis、AL_UtilActual、CST_TokPerPromptV528）；L1 3b 節 5 列；Gov_Map 5 列；Checks K7；DB_Evidence E262"}[k],
     "工作單 v5.29 第 0 節", "否"]
    for k, t, txt in _X14
] + [["G16", V, "Block 6 代表性實驗室（P2-3；工作單稱 G15）", "Block 6 以 OpenAI 為代表性實驗室代理；其他實驗室模型須自行覆寫 Alloc_In（P2-3）。ID 由 G15 改為 G16：G15 已於 v5.18 登錄為區間型紀錄等級規則",
       DATE, ANDY_DESIGN, "v5.29 已建", "Alloc_In（實驗室選擇器 A8）", "工作單 v5.29 第 0 節 (i)", "否"]]


# ================================================================== 5: SRC_Price tier columns (X–AB; check columns move to AC–AE／AM)
PRICE_HDR = ["價格層（隨需／預留／長約）", "合約期（月）", "客戶規模", "可中斷性（是／否）", "計價單位（token／GPU-hr／MW-year）"]
OLD_X_HDR = "同指標同口徑 Active 數（公式）"


def src_price_columns(wb):
    """Insert five empty tier columns at X once (guard: X4 still holds the old check header). Existing records keep X–AB empty."""
    ws = wb["SRC_Price"]
    if ws["X4"].value != OLD_X_HDR: return 0
    ws.insert_cols(24, 5)
    for i, h in enumerate(PRICE_HDR):
        put(ws, f"{L(24 + i)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(24 + i)].width = 14
    ws["A3"].value = (str(ws["A3"].value or "") + " ｜v5.29：X–AB 為價格分層欄（價格層、合約期、客戶規模、可中斷性、計價單位；既有紀錄留空，待 chat 端填）；檢查公式欄移至 AC–AE、鍵欄 AM")
    return 5


# ================================================================== README (version string is built from VERSION; v5.27 text is kept after it)
README_VERSION = (VERSION + "（X14 (a)–(m)：Interface 新增 R–U 輸出契約欄 Confidence／Decision Use／口徑層／最弱輸入更新日（IFC_；由公式自 Gov_Map 徙出，依賴列由 builder 反查）"
                  "與 J 節四層瀑布 IFW_<name>_100／_Util／_Prod／_Life（8 個營收列、3 個 IF_TokGW 列）；L1 新增 L1_FleetBreakeven、L1_FleetMargin、L1_HoldEconMW_*、"
                  "L1_TokMW_Gen_ratio_*、L1_HarVsGen_*、L1_PretrainFLOP_Astra_Ext、L1_AstraScale、L1_ScaleRD、L1_ScaleServe 與 token 對帳落差分解 L1_Gap*；"
                  "新頁 Load_Bearing（高段 Assumed／Analogy 格清單）；SRC_Price 新增 X–AB 分層欄；Checks K 節；"
                  f"判斷類：{SPEND_SID} 取代 {OLD_SPEND_SID}（推論支出 8.4 → 12.6 $B）、Alloc_In 每則提示 token 數 2,000 → 4,000（2,000–6,400）——"
                  "L1_Ans1–3、L1_ExtServeGW／ExtDaily／ExtFreeShare 與 IF_Alloc* 連動改變；其餘 IF_ 與模型頁數值不變；DB_Evidence E256–E262；Decisions X14a–m、G16；"
                  "工作單 docs/workorders/20261008_v5.29.md r1）。以下為 " + v527.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v527.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v527.VERSION.split("_")[-1]):]
README_NAMES_ADD = ("；IFC_（v5.29）＝Interface R–U 輸出契約欄（IFC_Conf、IFC_Use、IFC_Layer、IFC_Updated），下游可引用；"
                    "IFW_（v5.29）＝Interface J 節四層瀑布（IFW_<name>_100／_Util／_Prod／_Life），下游可引用；"
                    "IDX_SrcDate（v5.29）為 SRC_Index 審查日欄，下游不得連結")
README_ROW = ("輸出契約與四層瀑布（v5.29 X14）",
              "Interface R 欄 Confidence：該列公式鏈上（builder 建置時反查，含所有被引用的 Gov_Map 格）的 Gov_Map 格中，取「CC 敏感度分段＝高」者的最弱標記——"
              "含 3 級紀錄或 Analogy／Assumed 缺區間 → C；含非「原始數據且 SRC 等級 1」者 → B；其餘 → A；反查不到任何 Gov_Map 格 → 「—」（Checks K1）。"
              "S 欄 Decision Use 由 R 映射（A 基準輸入／B 情境、相對比較、反轉門檻／C 探索），B 節 100% 產出列與 D 節理論營收列另附「上限，不得作預測」（Checks K2）。"
              "T 欄口徑層：100%／IF_Util／CTL_ProdDerate／L×m，依節與標籤判定；U 欄＝R 欄取用的高段 GM 列對應 SRC 審查日的最大值（V 欄為數值暫存，W 欄列出反查到的 GM 列）。"
              "J 節 IFW_：同一指標四層並列（100% ＝ D 節 ÷ IF_Util 或 B 節直取；Util ＝ D 節；Prod ＝ G 節或 Interface_Prod；Life ＝ H 節；無對應者為「—」或 Prod × 1），自我檢查見 Checks K3。"
              "Gov_Map AG–AJ、SRC_Index F 為 builder 每次重建的輔助欄。")


# ================================================================== 1: Gov_Map helper columns AG–AJ and SRC_Index date column
GM_HELP_HDR = {"AG": "IFC：C 級旗標（高段且 3 級或缺區間；公式，v5.29）", "AH": "IFC：B 級旗標（高段且非原始數據 1 級；公式，v5.29）",
               "AI": "IFC：SRC 審查日（高段；公式，v5.29）", "AJ": "IFC：審查日數值 yyyymmdd（公式，v5.29）"}


def gov_map_helpers(wb):
    ws = wb["Gov_Map"]; n = 0
    for col, h in GM_HELP_HDR.items():
        put(ws, f"{col}4", h, F_BOLD, wrap=True); ws.column_dimensions[col].width = 9
    for r in range(5, ws.max_row + 1):
        if not ws[f"C{r}"].value or not ws[f"D{r}"].value: continue
        put(ws, f"AG{r}", f'=IF(AND($P{r}="高",OR($AD{r}=1,$X{r}=1)),1,0)', fmt="0")
        put(ws, f"AH{r}", f'=IF(AND($P{r}="高",$AG{r}=0,OR($F{r}<>"原始數據",$T{r}<>1)),1,0)', fmt="0")
        put(ws, f"AI{r}", f'=IF(AND($P{r}="高",ISNUMBER($AF{r})),INDEX(IDX_SrcDate,$AF{r}),"{DASH}")')
        put(ws, f"AJ{r}", f'=IF(AND(ISTEXT($AI{r}),LEN($AI{r})=10),IF(ISNUMBER(VALUE(SUBSTITUTE($AI{r},"-",""))),VALUE(SUBSTITUTE($AI{r},"-","")),0),0)', fmt="0")
        n += 1
    return n


# ================================================================== 1: Interface R–U contract columns (+ helpers V–Y)
_SEC = re.compile(r"^([A-Z])\. ")
IFC_HDR = {"R": "Confidence（A／B／C；公式，v5.29）", "S": "Decision Use（公式）", "T": "口徑層", "U": "最弱輸入更新日（SRC 審查日最大值；公式）",
           "V": "（U 欄數值暫存 yyyymmdd）", "W": "依賴的 Gov_Map 列（builder 反查，靜態；高段／全部）", "X": "（S 欄含「上限」旗標；公式）", "Y": "（應附「上限」旗標；靜態）"}
USE_MAP = '=IF({R}="{d}","{d}",IF({R}="A","基準輸入",IF({R}="B","情境、相對比較、反轉門檻","探索")))'


def _ranges(rows, col, sheet="Gov_Map"):
    """Compress sorted row numbers into contiguous ranges of one column: Gov_Map!$AG$5:$AG$9,…"""
    out = []; rows = sorted(rows)
    i = 0
    while i < len(rows):
        j = i
        while j + 1 < len(rows) and rows[j + 1] == rows[j] + 1: j += 1
        out.append(f"{sheet}!${col}${rows[i]}" if i == j else f"{sheet}!${col}${rows[i]}:${col}${rows[j]}")
        i = j + 1
    return ",".join(out)


def _layer(sec, label):
    if "[IF_Util]" in label: return "IF_Util"
    if sec == "B": return "100%"
    if sec == "G": return "CTL_ProdDerate"
    if sec == "H": return "L×m"
    if sec == "J":
        m = re.search(r"\[IFW_\w+_(100|Util|Prod|Life)\]", label)
        return {"100": "100%", "Util": "IF_Util", "Prod": "CTL_ProdDerate", "Life": "L×m"}[m.group(1)] if m else DASH
    if "100%" in label: return "100%"
    if "基準利用率" in label or "理論營收" in label or "付費服務營收" in label: return "IF_Util"
    if sec == "F" and ("服務 GW" in label or "Q1" in label or "Q2" in label or "隱含" in label): return "IF_Util"
    return DASH


def interface_contract(wb, deps, gm_cells):
    """R–U on every Interface data row (column C holds a formula or number; rows 4–5 are headers). Returns dict."""
    ws = wb["Interface"]
    last = _last_row(ws)
    for col, h in IFC_HDR.items():
        put(ws, f"{col}4", h, F_BOLD, wrap=True); ws.column_dimensions[col].width = {"R": 10, "S": 24, "T": 12, "U": 12, "V": 9, "W": 30, "X": 7, "Y": 7}[col]
    gm = wb["Gov_Map"]
    sec = None; rows = []; no_dep = []; stats = {}
    for r in range(6, last + 1):
        a = ws.cell(r, 1).value
        m = _SEC.match(str(a)) if isinstance(a, str) else None
        if m: sec = m.group(1); continue
        c = ws.cell(r, 3).value
        if c is None or (isinstance(c, str) and not c.startswith("=")): continue
        if isinstance(a, str) and (a.startswith("自我檢查") or a.startswith("IFW_") and "：Interface" in a): continue   # J-section flag rows
        if isinstance(a, str) and "[IF_Hdr" in a:                                    # display header (IF_HdrTask): not a downstream value
            put(ws, f"R{r}", "（表頭）", F_NOTE); put(ws, f"S{r}", DASH); put(ws, f"T{r}", DASH); put(ws, f"U{r}", DASH); continue
        keys = [("Interface", f"{L(k)}{r}") for k in range(3, 18) if isinstance(ws.cell(r, k).value, str) and ws.cell(r, k).value.startswith("=")]
        cl = deps.closure_many(keys) if keys else set()
        dep_rows = sorted({g for k in cl for g in gm_cells.get(k, ())})
        hi = [g for g in dep_rows if gm[f"P{g}"].value == "高"]
        label = str(a or "")
        layer = _layer(sec, label)
        should = 1 if (sec == "B" and layer == "100%") or (sec == "D" and ("理論營收" in label or "付費服務營收" in label)) else 0
        note = "；上限，不得作預測" if should else ""
        if not dep_rows:
            put(ws, f"R{r}", DASH); put(ws, f"S{r}", DASH); put(ws, f"V{r}", 0, F_CALC, fmt="0"); put(ws, f"U{r}", DASH)
            put(ws, f"W{r}", "反查不到 Gov_Map 格（Checks K1）", F_NOTE); no_dep.append(r)
        else:
            put(ws, f"R{r}", f'=IF(SUM({_ranges(dep_rows, "AG")})>0,"C",IF(SUM({_ranges(dep_rows, "AH")})>0,"B","A"))')
            put(ws, f"S{r}", USE_MAP.format(R=f"R{r}", d=DASH) + (f'&"{note}"' if note else ""))
            put(ws, f"V{r}", f"=MAX({_ranges(dep_rows, 'AJ')})", fmt="0")
            put(ws, f"U{r}", f'=IF(V{r}=0,"{DASH}",LEFT(TEXT(V{r},"0"),4)&"-"&MID(TEXT(V{r},"0"),5,2)&"-"&RIGHT(TEXT(V{r},"0"),2))')
            ids = [gm[f"A{g}"].value for g in hi]
            put(ws, f"W{r}", f"高段 {len(hi)}／全部 {len(dep_rows)}：" + ("、".join(ids) if ids else "（無高段）"), F_NOTE)
        put(ws, f"T{r}", layer)
        put(ws, f"X{r}", f'=IF(ISNUMBER(FIND("上限",S{r})),1,0)', fmt="0")
        put(ws, f"Y{r}", should, F_CALC, fmt="0")
        rows.append(r); stats[r] = (len(hi), len(dep_rows))
    for n, col in (("IFC_Conf", "R"), ("IFC_Use", "S"), ("IFC_Layer", "T"), ("IFC_Updated", "U")):
        _nm(wb, n, f"Interface!${col}$6:${col}${last}")
    return dict(rows=rows, no_dep=no_dep, last=last, stats=stats)


# ================================================================== 2: Interface J section (four-layer waterfall) with self-check flags
REV = ["IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet", "IF_RevGWFront_Luna", "IF_RevGWFront_Sol", "IF_RevGWFront_Astra", "IF_RevGWFleetFront"]
TOK = ["IF_TokGW_Luna", "IF_TokGW_Sol", "IF_TokGW_Astra"]
TAG = re.compile(r"　\[[A-Za-z0-9_]+\]\s*$")
LAYERS = [("100", "100%"), ("Util", "× IF_Util"), ("Prod", "× CTL_ProdDerate"), ("Life", "× L × m")]


def interface_j(wb):
    ws = wb["Interface"]
    start = _last_row(ws) + 2
    section(ws, start, "J. 四層瀑布並列（X14 (b)，v5.29）：同一指標的 100% → × IF_Util → × CTL_ProdDerate → × L × m 四層；全部引用既有列（D／G／H 節、B 節、Interface_Prod），"
                       "供下游一次取齊；無對應列者為「—」或 Prod × 1（附註）；自我檢查見本節末與 Checks K3", 17)
    r = start + 1; made = []; checks = []; at = {}
    def base_row(name):
        sh, row = _name_row(wb, name); assert sh == "Interface", (name, sh); return row
    def fmt_of(row): return ws.cell(row, 3).number_format
    for base in REV + TOK:
        b = base_row(base); lab = TAG.sub("", ws.cell(b, 1).value); stem = base[3:]
        prod = f"{base}_Prod" if f"{base}_Prod" in wb.defined_names else None
        life = f"{base}_Life" if f"{base}_Life" in wb.defined_names else None
        is_tok = base in TOK
        put(ws, f"A{r}", lab, F_BOLD); r += 1
        for suf, ltxt in LAYERS:
            name = f"IFW_{stem}_{suf}"
            note = ""
            if is_tok:
                if suf == "100": f = lambda X: f"={X}{b}"; src = ("Interface", b)
                elif suf == "Util": f = lambda X: f"=IF(ISNUMBER({X}{b}),{X}{b}*IF_Util,{X}{b})"; src = None; note = "（B 節 100% 列 × IF_Util；無 D 節對應）"
                elif suf == "Prod": f = lambda X: f"=Interface_Prod!{X}{b}"; src = ("Interface_Prod", b); note = "（＝Interface_Prod 同列：Perf_Prod 鏈）"
                else: p = at[f"IFW_{stem}_Prod"]; f = lambda X, p=p: f"=IF(ISNUMBER({X}{p}),{X}{p}*1,{X}{p})"; src = None; note = "（無 H 節對應：＝Prod 列 × 1）"
            else:
                if suf == "100": f = lambda X: f"=IF(ISNUMBER({X}{b}),{X}{b}/IF_Util,{X}{b})"; src = None; note = "（D 節列 ÷ IF_Util）"
                elif suf == "Util": f = lambda X: f"={X}{b}"; src = ("Interface", b)
                elif suf == "Prod":
                    if prod: g = base_row(prod); f = lambda X, g=g: f"={X}{g}"; src = ("Interface", g)
                    else: f = None; src = None; note = "（G 節無對應 _Prod 列）"
                else:
                    if life: h = base_row(life); f = lambda X, h=h: f"={X}{h}"; src = ("Interface", h)
                    else: f = None; src = None; note = "（H 節無對應 _Life 列）"
            put(ws, f"A{r}", f"{lab}｜{ltxt}{note}　[{name}]"); put(ws, f"B{r}", ws.cell(b, 2).value)
            for c in COLS:
                X = L(c)
                if f is None: put(ws, f"{X}{r}", DASH)
                else: put(ws, f"{X}{r}", f(X), fmt=fmt_of(b))
            made.append((name, f"Interface!$C${r}:$Q${r}")); at[name] = r
            if src: checks.append((name, r, src))
            r += 1
    r += 1
    put(ws, f"A{r}", "自我檢查（Checks K3）：IFW_ 列 − 來源列（D 節／G 節／H 節／B 節／Interface_Prod）的絕對差 ≤ 1e-9（兩邊皆為文字時須相同）；0＝相符，1＝不符", F_BOLD); r += 1
    f0 = r
    for name, rr, (sh, sr) in checks:
        put(ws, f"A{r}", f"{name}：Interface 列 vs {sh} 第 {sr} 列", F_NOTE)
        for c in COLS:
            X = L(c); a, b = f"{X}{rr}", f"{sh}!{X}{sr}" if sh != "Interface" else f"{X}{sr}"
            put(ws, f"{X}{r}", f"=IF(AND(ISNUMBER({a}),ISNUMBER({b})),IF(ABS({a}-{b})<=0.000000001,0,1),IF(AND(NOT(ISNUMBER({a})),NOT(ISNUMBER({b}))),IF({a}={b},0,1),1))", fmt="0")
        r += 1
    f1 = r - 1
    for n, ref in made: _nm(wb, n, ref)
    return dict(start=start, made=made, flags=(f0, f1), at=at)


# ================================================================== 3／3b: L1 rows (appended to gov._rows_l1; builder-owned, live formulas)
TASKS = ["一般聊天", "推理聊天", "單代理（工具迴圈）", "多代理研究", "Coding agent（長程）"]      # IF_HdrTask order (Workload C4:G4)
TASK_KEYS = ["Chat", "ReasonChat", "SingleAgent", "MultiAgent", "Coding"]                   # ASCII name stems (L1_HarVsGen_<task>)
GENCOL = {"Hopper": 1, "GB200": 4, "GB300": 7, "VR200": 10}
COST_RNG = "成本角落情境（低成本／高成本欄）"


def _alloc_sens(wb):
    """(row of 每則提示 token 數 低, row of 高, column letter of 服務 GW) in the Alloc G-section table."""
    ws = wb["Alloc"]
    m = re.match(r"Alloc!\$([A-Z]+)\$(\d+):\$[A-Z]+\$(\d+)", wb.defined_names["AL_SensQ1"].attr_text)
    first = int(m.group(2)); hdr = first - 1
    col = next(L(c) for c in range(1, ws.max_column + 1) if ws.cell(hdr, c).value == "服務 GW")
    lo = next(r for r in range(first, int(m.group(3)) + 1) if ws.cell(r, 1).value == "每則提示 token 數 低")
    hi = next(r for r in range(first, int(m.group(3)) + 1) if ws.cell(r, 1).value == "每則提示 token 數 高")
    return lo, hi, col


def l1_rows_new(wb):
    R = []
    g = GENCOL["VR200"]; glo, gb, ghi = g, g + 1, g + 2
    def be(c): return f"IF(ISNUMBER(INDEX(IF_RevGWFleet,1,{c})),INDEX(IF_HoldEcon,1,{c})/(INDEX(IF_RevGWFleet,1,{c})/IF_Util),\"{SLO}\")"
    R.append(("FleetBreakeven", "機隊損益兩平乘積：令機隊營收＝持有成本所需的「利用率 × 折減 × L × m」（VR200）", "VR200 基準成本欄；IF_HoldEcon ÷（IF_RevGWFleet ÷ IF_Util）；X14 (c)",
              "=" + be(gb), "=" + be(glo), "=" + be(ghi), "x", COST_RNG,
              "100% 口徑的機隊營收乘以本乘積即等於持有成本；基準約 0.157（v5.25）。E＝低成本欄、F＝高成本欄",
              "持有成本（機架價格、折舊年限、WACC）、單價快照、層級組合", "利用率 60%：Assumed（K11）；機架價格：3 級", DASH, None, None,
              "IF_HoldEcon；IF_RevGWFleet", "Interface 第 13 列、D 節機隊合計列", DASH))
    fm = lambda ref: f'=IF(ISNUMBER({ref}),IF_Util*CTL_ProdDerate*CTL_PriceLife*CTL_Monetize/{ref},"{SLO}")'
    R.append(("FleetMargin", "機隊營收 ÷ 持有成本（四層口徑：IF_Util × CTL_ProdDerate × L × m ÷ 損益兩平乘積；VR200）", "VR200 基準成本欄；X14 (c)",
              fm("L1_FleetBreakeven"), fm("L1_FleetBreakeven_Hi"), fm("L1_FleetBreakeven_Lo"), "x", "成本角落情境（高成本／低成本欄；倍數隨成本反向）",
              "＝CTL_ProdDerate × Theory_Rev「機隊營收 ÷ 持有成本」（折減 1 時相等；Checks K4）；外部欄依工作單連 L1_Ans5_GM 的外部值（2025 推論毛利隱含值，口徑不同：毛利率 對 倍數）",
              "利用率、生產折減、L、m、持有成本、單價快照", "利用率 60%：Assumed（K11）；CTL_ProdDerate 0.85：情境值",
              f"{SPEND_SID}；SRC_DEM_007", f"=1-{SPEND_SID}/SRC_DEM_007", f"=1-{SPEND_SID}/SRC_DEM_007", "L1_FleetBreakeven", "L1 本頁；Theory_Rev 第 73 列",
              "外部為毛利率口徑（1 − 推論支出 ÷ 營收），與本列倍數口徑不同，判讀欄僅供方向參考"))
    for gen in ("Hopper", "GB200", "GB300", "VR200"):
        ext = ("SRC_PRC_002", "=SRC_PRC_002", "=SRC_PRC_002") if gen == "GB300" else (DASH, None, None)
        R.append((f"HoldEconMW_{gen}", f"每 MW 年經濟持有成本（{gen}；＝每 GW ÷ 1,000）", "基準成本情境；IT 關鍵電力；X14 (d)",
                  f"=L1_HoldEconGW_{gen}/1000", f"=L1_HoldEconGW_{gen}_Lo/1000", f"=L1_HoldEconGW_{gen}_Hi/1000", "$M/MW/年", COST_RNG,
                  "下游每 MW 介面：Tokenomics 不輸出每 MW 收入，下游依 q × p × c × 簽約率自算", "IT 折舊年限、機架價格、WACC", "機架價格：3 級",
                  *ext, f"L1_HoldEconGW_{gen}", "L1 第 11–14 列", "外部（GB300 列）為 $/GPU-hr 的新雲損益兩平租金，口徑不同，判讀欄僅供方向參考" if gen == "GB300" else DASH))
    tok = lambda c: f"INDEX(IF_TokGW_Sol,1,{c})"
    div = lambda a, b: f'=IF(ISNUMBER({b}),IF({b}>0,{a}/{b},"{SLO}"),"{SLO}")'      # 每 GW 產出在 SLO 不可達時為 0：分母為 0 回傳文字，不出現 #DIV/0!
    pairs = [("GB200", "Hopper", None), ("GB300", "GB200", ("SRC_PERF_024", "SRC_PERF_025")), ("VR200", "GB300", ("SRC_PERF_027", "SRC_PERF_028"))]
    for gen, prev, ml in pairs:
        c1, c0 = GENCOL[gen] + 1, GENCOL[prev] + 1
        base = div(tok(c1), tok(c0))
        if gen == "VR200":
            lo, hi = div("Sens_Perf!$E$98", "Sens_Perf!$F$98"), div("Sens_Perf!$G$98", "Sens_Perf!$H$98")
            rng = "Sens_Perf VR η_d × 0.5／× 1.5 欄（E:F、G:H 第 98 列）的比值"
        else:
            lo, hi = base, base; rng = "無區間（Sens_Perf 只涵蓋 VR200 對 GB300）"
        ext = (f"{ml[0]}；{ml[1]}", f"={ml[0]}/{ml[1]}", f"={ml[0]}/{ml[1]}") if ml else (DASH, None, None)
        R.append((f"TokMW_Gen_ratio_{gen}", f"相鄰世代每 GW（每 MW）總產出比：{gen} ÷ {prev}（Sol，100%）", "基準成本欄；Sol 參考請求；X14 (d)",
                  base, lo, hi, "x", rng, "每 MW 口徑與每 GW 相同（同除 1,000）；比值 >1 表示新世代每 MW 產出較高",
                  "η_d、每層延遲、HBM、峰值", "VR200 η_d：Analogy（沿用 GB300）", *ext, "IF_TokGW_Sol", "Interface 第 31 列",
                  "外部為 MLPerf DeepSeek-R1 interactive 整架 tok/s 比（工作單寫 SRC_PERF_031／032，該兩筆為 TPOT 上限；CC 改連 MLPerf 產出紀錄，待 Project 確認）" if ml else "Hopper 對 GB200 無同條件 MLPerf 對照"))
    ratio = f"(INDEX(IF_CostDec_Sol,1,{gb})/INDEX(IF_CostDec_Sol,1,{GENCOL['GB300'] + 1}))"
    for k, (task, tkey) in enumerate(zip(TASKS, TASK_KEYS), start=1):
        har = f"INDEX(IF_HarR_Sol,1,{k})"
        guard = f"AND(ISNUMBER({har}),ISNUMBER(INDEX(IF_CostDec_Sol,1,{gb})),ISNUMBER(INDEX(IF_CostDec_Sol,1,{GENCOL['GB300'] + 1})),ISNUMBER({ratio}),{ratio}>0)"
        base = f'=IF({guard},{har}/{ratio},"{SLO}")'
        if k == 5:
            lo = f'=IF({guard},MIN(Sens_Har!$C$33:$S$33)/{ratio},"{SLO}")'; hi = f'=IF({guard},MAX(Sens_Har!$C$33:$S$33)/{ratio},"{SLO}")'
            rng = "Sens_Har 第 33 列（Sol R）最小／最大 ÷ 同一世代比"
        else:
            lo, hi = base, base; rng = "無區間（Sens_Har 只涵蓋 Coding agent）"
        R.append((f"HarVsGen_{tkey}", f"harness 對世代：（選定 ÷ 標準 每成功任務成本，VR200）÷（VR200 ÷ GB300 decode $/M，Sol）— {task}", "Sol；VR200；任務欄 " + str(k) + "；X14 (e)",
                  base, lo, hi, "x", rng, "<1 表示 harness 的成本降幅大於換代（VR200 對 GB300）的成本降幅；基準仍 L3（w＝0）、L4 不動",
                  "harness 參數組、成功率 p、η_d 世代倍數", "harness 成功率：Assumed 或 3 級", "SRC_HAR_004；SRC_HAR_006", "=SRC_HAR_006/SRC_HAR_004", "=SRC_HAR_006/SRC_HAR_004",
                  "IF_HarR_Sol；IF_CostDec_Sol", "Interface E 節第 174 列、B 節第 35 列", "外部為 ARC-AGI-3 Adapter ÷ 標準成本比（方向；未除以世代比）"))
    R.append(("PretrainFLOP_Astra_Ext", "Astra 預訓練算力（external-anchor：Epoch GPT-6 Astra 估計）", "SRC_MOD_055（低高＝_Lo／_Hi）；X14 (f)",
              "=SRC_MOD_055", "=SRC_MOD_055_Lo", "=SRC_MOD_055_Hi", "FLOP", "Epoch notebook CI ~[5e26, 2e27]", "與第 36 列 bottom-up 並列為雙基準；不改 Train_In、Arch（X13 (e)）",
              "Epoch 硬體推估（GB200 數為下限、90 天、25% MFU）", "Epoch：1 級、中立", "SRC_MOD_055", "=SRC_MOD_055", "=SRC_MOD_055", "L1_PretrainFLOP_Astra", "L1 第 36 列", DASH))
    R.append(("AstraScale", "Astra 規模係數：external-anchor ÷ bottom-up", "X14 (f)", "=L1_PretrainFLOP_Astra_Ext/L1_PretrainFLOP_Astra",
              "=L1_PretrainFLOP_Astra_Ext_Lo/L1_PretrainFLOP_Astra", "=L1_PretrainFLOP_Astra_Ext_Hi/L1_PretrainFLOP_Astra", "x", "低高同比（Ext 區間 ÷ bottom-up）",
              "約 14.6：J8 缺口；下游校準用，不得當產能", "Astra 啟用參數、預訓練 token", "Astra 架構：Assumed", DASH, None, None, "L1_PretrainFLOP_Astra_Ext", "L1 本頁", DASH))
    R.append(("ScaleRD", "研發端規模係數：OpenAI 2025 訓練支出 ÷ 模型研發算力成本（SRC_DEM_006 ÷ L1_Ans3）", "Decision Use＝下游校準用，不得當產能；X14 (g)",
              '=IF(ISNUMBER(L1_Ans3),SRC_DEM_006/L1_Ans3,"—")', '=IF(ISNUMBER(L1_Ans3_Hi),SRC_DEM_006/L1_Ans3_Hi,"—")', '=IF(ISNUMBER(L1_Ans3_Lo),SRC_DEM_006/L1_Ans3_Lo,"—")', "x",
              "以 L1_Ans3 低高反向", "約 10：兩端同幅度偏小的證據（X13 (c)）；校準用，不得當產能", "k、N_major、N_refresh", "計畫規模 k：Assumed（A3）",
              "SRC_DEM_006（分子）", None, None, "L1_Ans3", "L1 第 39 列", "本列本身即對照（分子為外部值），外部欄不另填"))
    lo_r, hi_r, scol = _alloc_sens(wb)
    sv = lambda ref: f'=IF(AND(ISNUMBER({ref}),ISNUMBER(AL_ServeGWSpend)),AL_ServeGWSpend/{ref},"{SLO}")'
    R.append(("ScaleServe", "服務端規模係數：支出路線服務 GW ÷ token 路線服務 GW（Alloc F 節 ÷ B 節）", "Decision Use＝下游校準用，不得當產能；X14 (g)",
              sv("AL_ServeGW"), sv(f"Alloc!${scol}${hi_r}"), sv(f"Alloc!${scol}${lo_r}"), "x", "以 Alloc_In 每則提示 token 數低高反向（Alloc G 節服務 GW 欄）",
              "＝1 ÷ L1_ExtServeGW 的推算÷外部比值；約 14：四項口徑差的乘積（L1_GapProduct）", "每則提示 token 數、推論支出口徑、世代組合", "每則提示 token 數（Assumed）",
              f"{SPEND_SID}（分子）", None, None, "IF_AllocServeGW；AL_ServeGWSpend", "Alloc 第 28、61 列", "本列本身即對照（分子為外部值），外部欄不另填"))
    # ---- 3b: gap decomposition (X14 (m))
    R.append(("GapPrompt", "落差分解 1：每則提示 token 數 ÷ v5.28 基準 2,000", "Alloc_In C15 ÷ CST_TokPerPromptV528；X14 (m)",
              "=AL_TokPerPrompt/CST_TokPerPromptV528", "=AL_TokPerPrompt_Lo/CST_TokPerPromptV528", "=AL_TokPerPrompt_Hi/CST_TokPerPromptV528", "x", "區間端點 ÷ 2,000",
              "基準 2.0（4,000 ÷ 2,000）；外部為 OpenRouter 每請求 6,400 ÷ 2,000＝3.2（換成同口徑倍數）", "每則提示 token 數", "每則提示 token 數：Assumed（E261）",
              "SRC_DEM_014；SRC_DEM_015", "=(SRC_DEM_014+SRC_DEM_015)/CST_TokPerPromptV528", "=(SRC_DEM_014+SRC_DEM_015)/CST_TokPerPromptV528", "AL_TokPerPrompt", "Alloc_In 第 15 列", DASH))
    R.append(("GapSpendBasis", "落差分解 2：推論支出計價 ÷ 持有成本（Azure 計價含利潤與資本回收）", "Alloc_In 新輸入（Assumed）；X14 (m)",
              "=AL_SpendBasis", "=AL_SpendBasis_Lo", "=AL_SpendBasis_Hi", "x", "1.5–3.0（Assumed）", "基準 2.0；無外部對照（已搜尋，未找到 OpenAI 對 Azure 實付單價；E262）",
              "推論支出口徑", "本列：Assumed（E262）", DASH, None, None, "AL_SpendBasis", "Alloc_In 新列", "無外部對照（已搜尋，未找到 OpenAI 對 Azure 實付單價；E262）"))
    tv = f"INDEX(IF_TokGW_Sol,1,{gb})"
    R.append(("GapISL", "落差分解 3：參考請求 ISL 16K 對實際混合（Sol 每 GW 總產出 基準 ÷ ISL 4K）", "Sens_Perf 第 98 列 W 欄（ISL 4K，VR200）；X14 (m)",
              div(tv, "Sens_Perf!$W$98"), div(tv, "Sens_Perf!$Y$98"), div(tv, "Sens_Perf!$W$98"), "x",
              "低＝基準 ÷ ISL 64K 欄（Y98，<1）；高＝基準（ISL 4K 端）", "總產出隨 ISL 上升（prefill token 便宜）：實際混合偏短時每 GW 產出低於參考請求", "參考 ISL／OSL、η_p", "參考 ISL：Assumed（GM245–247）",
              DASH, None, None, "IF_TokGW_Sol", "Interface 第 31 列；Sens_Perf 第 98 列", DASH))
    R.append(("GapUtil", "落差分解 4：模型利用率 × 折減（IF_Util × CTL_ProdDerate）÷ 實際利用率 × 生產折減", "Alloc_In 新輸入（Assumed）；X14 (m)",
              "=IF_Util*CTL_ProdDerate/AL_UtilActual", "=IF_Util*CTL_ProdDerate/AL_UtilActual_Hi", "=IF_Util*CTL_ProdDerate/AL_UtilActual_Lo", "x", "依新輸入區間 0.3–0.4 反向",
              "基準約 1.46（0.6 × 0.85 ÷ 0.35）", "利用率、生產折減", "Serving C17／C18：Assumed（GM236／GM237）", "GM236；GM237（Serving C17、C18，Assumed）", None, None,
              "AL_UtilActual", "Alloc_In 新列；Serving 第 17、28 列", DASH))
    gp = lambda s: f'=IF(AND(ISNUMBER(L1_GapISL{s}),ISNUMBER(L1_GapPrompt{s})),L1_GapPrompt{s}*L1_GapSpendBasis{s}*L1_GapISL{s}*L1_GapUtil{s},"{SLO}")'
    R.append(("GapProduct", "落差分解乘積：四項口徑差之積（對照 1 ÷ L1_ExtServeGW 比值＝L1_ScaleServe）", "X14 (m)", gp(""), gp("_Lo"), gp("_Hi"), "x", "四者低高乘積",
              "區間涵蓋外部對照即表示落差可由四項口徑差解釋（Checks K7）", "四項分解列", "推論支出計價 ÷ 持有成本：Assumed", "L1_ScaleServe（1 ÷ L1_ExtServeGW 比值）",
              "=L1_ScaleServe", "=L1_ScaleServe", "L1_ScaleServe", "L1 本頁", DASH))
    return R


# ================================================================== 4: Load_Bearing (static expansion; every cell links Gov_Map live)
LB_HDR = ["GM_ID", "工作表", "格", "列標籤", "類別", "低", "高", "CC 敏感度分段", "SRC 等級", "影響的 L1 列（builder 反查，靜態）", "反轉門檻（本版空白，待 chat 端）",
          "審查日（SRC）", "更新方式", "審查日距建置日（天；公式）"]


def load_bearing(wb, deps, gm_cells):
    if "Load_Bearing" in wb.sheetnames: del wb["Load_Bearing"]
    ws = wb.create_sheet("Load_Bearing")
    gm = wb["Gov_Map"]
    title(ws, "Load_Bearing — 高段（CC 敏感度分段＝高）的 Assumed／Analogy 輸入格清單（X14 (h)，v5.29）",
          "builder 每次重建：engine（pycel）不支援 FILTER，故列的篩選在建置時靜態展開（條件：Gov_Map P＝高 且 F∈{Assumed, Analogy}），各欄以公式即時連結 Gov_Map；"
          "Gov_Map 判斷欄改動後須重建本頁（Checks K5 比對即時篩選數與本頁列數）。反轉門檻欄本版空白，待 chat 端填。")
    put(ws, "A3", "建置日（本頁靜態展開的日期；K6 以此計算審查日距今天數）", F_NOTE); put(ws, "C3", DATE, F_CALC)
    for i, h in enumerate(LB_HDR):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = [8, 11, 9, 30, 10, 9, 9, 8, 7, 36, 18, 11, 26, 10][i]
    # reverse map: Gov_Map row -> L1 keys whose D cell depends on a cell of that row
    l1 = wb["L1"]; rev = {}
    for r in range(5, l1.max_row + 1):
        key = l1.cell(r, 1).value
        if not key: continue
        for g in {x for k in deps.closure(("L1", f"D{r}")) for x in gm_cells.get(k, ())}:
            rev.setdefault(g, []).append(key)
    r = 5; n = 0
    for g in range(5, gm.max_row + 1):
        if gm[f"P{g}"].value != "高" or gm[f"F{g}"].value not in ("Assumed", "Analogy"): continue
        put(ws, f"A{r}", f"=Gov_Map!$A${g}"); put(ws, f"B{r}", f"=Gov_Map!$C${g}"); put(ws, f"C{r}", f"=Gov_Map!$D${g}")
        put(ws, f"D{r}", f"=Gov_Map!$E${g}", wrap=True); put(ws, f"E{r}", f"=Gov_Map!$F${g}")
        put(ws, f"F{r}", f"=Gov_Map!$K${g}"); put(ws, f"G{r}", f"=Gov_Map!$L${g}"); put(ws, f"H{r}", f"=Gov_Map!$P${g}"); put(ws, f"I{r}", f"=Gov_Map!$T${g}")
        keys = rev.get(g, [])
        put(ws, f"J{r}", "、".join(keys) if keys else DASH, F_NOTE, wrap=True)
        put(ws, f"K{r}", None); put(ws, f"L{r}", f'=IF(ISNUMBER(Gov_Map!$AF${g}),INDEX(IDX_SrcDate,Gov_Map!$AF${g}),"{DASH}")')
        put(ws, f"M{r}", f"改 Excel 藍字格 {gm[f'C{g}'].value}!{gm[f'D{g}'].value}（Gov_Map {gm[f'A{g}'].value} 的區間、理由同步）；不改 builder", F_NOTE, wrap=True)
        d = f"L{r}"
        put(ws, f"N{r}", f'=IF(AND(ISTEXT({d}),LEN({d})=10),IF(ISNUMBER(VALUE(SUBSTITUTE({d},"-",""))),'
                         f'DATE(VALUE(LEFT($C$3,4)),VALUE(MID($C$3,6,2)),VALUE(RIGHT($C$3,2)))-DATE(VALUE(LEFT({d},4)),VALUE(MID({d},6,2)),VALUE(RIGHT({d},2))),"{DASH}"),"{DASH}")', fmt="0")
        r += 1; n += 1
    last = r - 1
    put(ws, f"A{r + 1}", f"本頁列數（builder 靜態展開）：{n}；Gov_Map 即時篩選數（應相等，否則重建）：", F_BOLD)
    put(ws, f"J{r + 1}", '=SUMPRODUCT((Gov_Map!$P$5:$P$700="高")*((Gov_Map!$F$5:$F$700="Assumed")+(Gov_Map!$F$5:$F$700="Analogy")))', fmt="0")
    _nm(wb, "LB_Rows", f"Load_Bearing!$A$5:$A${last}"); _nm(wb, "LB_Days", f"Load_Bearing!$N$5:$N${last}"); _nm(wb, "LB_LiveCount", f"Load_Bearing!$J${r + 1}")
    ws.freeze_panes = "E5"
    return dict(rows=n, last=last)


# ================================================================== 6: Checks K section
def checks_k(wb, ifc, ifj, lb):
    ws = wb["Checks"]
    r = _last_row(ws) + 2
    section(ws, r, "K. 輸出契約、四層瀑布、損益兩平與 Load_Bearing 檢查（工作單 v5.29）：K2、K3 為 ERROR 計入 GOV_Errors；K1 為 WARN 計入 GOV_Warnings；K4–K7 為 INFO 計入 GOV_Info", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    last = ifc["last"]; f0, f1 = ifj["flags"]
    tr = wb["Theory_Rev"]; m73 = _row_by_label(tr, "機隊營收 ÷ 持有成本")
    rows = [
        ("K1", "Confidence 為「—」的 Interface 列數（反查不到 Gov_Map 格）", "WARN", f'=COUNTIF(Interface!$R$6:$R${last},"{DASH}")', f"Interface R6:R{last}"),
        ("K2", "R 欄為 A 但 S 欄缺「上限」附註的 B 節 100% 產出列與 D 節理論營收列數", "ERROR",
         f'=SUMPRODUCT((Interface!$R$6:$R${last}="A")*(Interface!$Y$6:$Y${last}=1)*(Interface!$X$6:$X${last}=0))', "Interface R／X／Y 欄（Y＝應附上限的靜態旗標，X＝S 含「上限」）"),
        ("K3", "四層瀑布自我檢查：IFW_ 列不等於來源列的格數（絕對差 > 1e-9；文字列須相同）", "ERROR", f"=SUM(Interface!C{f0}:Q{f1})", f"Interface 第 {f0}–{f1} 列 × C:Q"),
        ("K4", "L1_FleetMargin 與 Theory_Rev「機隊營收 ÷ 持有成本」VR200 基準欄之差 > 1e-9（1＝不等；基準下等於 CTL_ProdDerate 倍，見報告）", "INFO",
         f'=IF(AND(ISNUMBER(L1_FleetMargin),ISNUMBER(Theory_Rev!$M${m73})),IF(ABS(L1_FleetMargin-Theory_Rev!$M${m73})<=0.000000001,0,1),1)', f"L1_FleetMargin；Theory_Rev!M{m73}"),
        ("K5", "Load_Bearing 列數（Gov_Map 即時篩選：P＝高 且 F∈{Assumed, Analogy}；本頁靜態展開 " + str(lb["rows"]) + " 列）", "INFO", "=LB_LiveCount", "Load_Bearing；Gov_Map P、F 欄"),
        ("K6", "Load_Bearing 中審查日超過 90 天（距建置日）者", "INFO", '=COUNTIF(LB_Days,">90")', "Load_Bearing N 欄（無審查日者不計）"),
        ("K7", "L1_GapProduct 的低高區間未涵蓋外部對照（L1_ScaleServe）：1＝未涵蓋", "INFO",
         '=IF(AND(ISNUMBER(L1_GapProduct_Lo),ISNUMBER(L1_GapProduct_Hi),ISNUMBER(L1_ScaleServe)),IF(AND(L1_GapProduct_Lo<=L1_ScaleServe,L1_ScaleServe<=L1_GapProduct_Hi),0,1),1)', "L1_GapProduct_Lo／_Hi；L1_ScaleServe"),
    ]
    at = {}
    for code, lab, lvl, f, note in rows:
        put(ws, f"A{r}", code); put(ws, f"B{r}", lab, wrap=True); put(ws, f"C{r}", lvl, F_BOLD if lvl == "ERROR" else None)
        put(ws, f"D{r}", f, F_CALC, fmt="0"); put(ws, f"E{r}", note, F_NOTE); at[code] = r; r += 1
    for n, codes, label in (("GOV_Errors", ("K2", "K3"), "ERROR 合計（CI 讀取 GOV_Errors；含 G、H、X、Y、K 節）"),
                            ("GOV_Warnings", ("K1",), "WARN 合計（含 H3、K1）"), ("GOV_Info", ("K4", "K5", "K6", "K7"), "INFO 合計（含 K4–K7）")):
        ref = wb.defined_names[n].attr_text.split("!")[1].replace("$", "")
        cell = ws[ref]
        for c in codes:
            if f"D{at[c]}" not in str(cell.value): cell.value = f"{cell.value}+D{at[c]}"
        ws[f"B{int(ref[1:])}"].value = label
    return at


# ================================================================== SRC_Index date column (called from gov.src_index)
def src_index_dates(wb, spans_rows, sentinel_rows):
    """F column: SRC 審查日 per stacked row; '—' for the sentinel block. Name IDX_SrcDate over the whole stack."""
    ws = wb["SRC_Index"]
    put(ws, "F4", "審查日（v5.29）", F_BOLD); ws.column_dimensions["F"].width = 11
    for r, (sh, rr) in spans_rows.items(): put(ws, f"F{r}", f"={sh}!$S{rr}")
    for r in sentinel_rows: put(ws, f"F{r}", DASH)
    last = max(list(spans_rows) + list(sentinel_rows))
    _nm(wb, "IDX_SrcDate", f"SRC_Index!$F$5:$F${last}")

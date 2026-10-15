# v6.2 (work order docs/workorders/20261016_稽核修正2.md r0, section 2 = segment 2-1): D1(c) model-scale multiplier, TTFT in the reachability judgement, Alloc renormalisation (minor version).
#   2-1-a Spec_Rack new section "模型規模倍數（D1(c)…）": three Assumed input rows (baseline／low／high) = ARCH_ScaleGen／_Lo／_Hi (1x5: Hopper, GB200, GB300, VR200, Rubin Ultra; Rubin Ultra fixed at 1,
#         because Perf columns carry five generations and INDEX(…,1,gen) must not fall off the range). Multiplied into Perf／Perf_Batch／Sens_Perf rows 28 (active), 32／33 (non-expert／expert)
#         and Training／Sens_Train row 22 (perf.py／training.py); Calib row 30 is NOT multiplied. Baseline = 1, so all values are unchanged. Scenario d1_model_scale (tests/parity/scenarios.yaml).
#   2-1-b Perf-family row 93 (decode GPU-s per request) and the binding-constraint row read row 77 (TTFT): text flag "TTFT 不可達" (after the SLO check, perf.py); Checks B27 counts both flags (finish.py).
#   2-1-c Alloc section B／G／H and Cap_In H10 `_CAP`: tiers that are unreachable drop out and the tier weights are renormalised over the reachable ones; a generation with no reachable tier
#         is a text flag and the generation mix is renormalised over the rest (block6.py, v600.py, v534.py). New display rows 未服務需求占比 (Alloc section B).
# Every write to an Excel-owned cell is guarded (cell still holds its v6.1 value／text) so a rebuild never overwrites a later Excel edit.
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, section
import v600
import v601

VERSION = "20261016_Tokenomics_v6.2"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-16"
V = "v6.2"
WO = "工作單 docs/workorders/20261016_稽核修正2.md r0"
ANDY = "Andy 2026-10-15 稽核判斷會議決定 D1(c)、D8（docs/reports/20261015_稽核判斷會議_決定.md 第 1、4 節）；J1 情境值為 chat 端預設，待 Andy 確認"
DASH = "—"
GENS = ["C", "D", "E", "F", "G"]

SCALE_NOTE = ("固定模型口徑（2026 Arch 快照，跨世代同一模型）；模型隨世代變大見 `ARCH_ScaleGen` 與情境 `d1_model_scale`")

SCALE_ROWS = [
    # (label, values, name, note)
    ("模型規模倍數：基準（ARCH_ScaleGen）", [1, 1, 1, 1, 1], "ARCH_ScaleGen",
     "Assumed｜D1(c)：基準 1＝固定模型口徑（截面比較）；情境 d1_model_scale 為 J1 預設（R-a：GB300＝2026 快照）。只放大參數（每 token FLOPs、權重 bytes），KV 與層數不變，所以是模型變大效果的下限。"
     "第 5 欄（Rubin Ultra）固定 1，只為讓具名範圍與 Perf 的世代索引（1–5）一致；J1 只定義前四代"),
    ("模型規模倍數：低（ARCH_ScaleGen_Lo）", [0.1, 0.3, 1, 1, 1], "ARCH_ScaleGen_Lo",
     "Assumed｜區間低端（相對 2026 Arch 快照的啟用參數倍數）：Hopper 數百億 ÷ 180B ≈ 0.1；GB200 0.3；GB300 與 VR200 為 1（J1）"),
    ("模型規模倍數：高（ARCH_ScaleGen_Hi）", [0.5, 1.0, 1, 4.4, 1], "ARCH_ScaleGen_Hi",
     "Assumed｜區間高端：Hopper 0.5；GB200 1.0；GB300 1；VR200 400–800B ÷ 180B ≈ 4.4（J1）；R-b 讀法（快照對應 GB200）由 Project 另發 r1"),
]
SEC_TITLE = "模型規模倍數（D1(c)，啟用參數倍數，相對 2026 Arch 快照）"


def spec_rack_scale(wb, R):
    """Called right after inputs.spec_rack(): writes the section below the B3 rows, returns {'sec': row, 'rows': [r_base, r_lo, r_hi]}."""
    ws = wb["Spec_Rack"]
    r0 = R["tfp4"] + 2
    section(ws, r0, SEC_TITLE, 8)
    rows = []
    for i, (lab, vals, name, note) in enumerate(SCALE_ROWS):
        r = r0 + 1 + i
        put(ws, f"A{r}", lab)
        for col, v in zip(GENS, vals):
            put(ws, f"{col}{r}", v, F_IN, fmt="0.00")
        put(ws, f"H{r}", note, F_NOTE)
        wb.defined_names[name] = DefinedName(name, attr_text=f"Spec_Rack!$C${r}:$G${r}")
        rows.append(r)
    return {"sec": r0, "rows": rows}


# ================================================================== labels / notes (Interface、L1: labels only)
def notes_patch(wb, append_text):
    """Fixed-model-basis note on the Interface per-generation output block headers (B／C／D sections) and on L1 rows L1_TokMW_Gen_ratio_*."""
    log = []
    ws = wb["Interface"]
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if isinstance(v, str) and v[:2] in ("B.", "C.", "D.") and ws.cell(r, 3).value is None and ws.cell(r, 2).value is None:
            if append_text(ws.cell(r, 1), "｜" + SCALE_NOTE): log.append(f"Interface!A{r}: note (v6.2 D1(c))")
    l1 = wb["L1"]
    for r in range(1, l1.max_row + 1):
        v = l1.cell(r, 1).value
        if isinstance(v, str) and v.startswith("L1_TokMW_Gen_ratio_"):
            if append_text(l1.cell(r, 2), "｜" + SCALE_NOTE): log.append(f"L1!B{r}: note (v6.2 D1(c))")
    return log


# ================================================================== Decisions: AF1-D8 marked as superseded (not deleted)
def decisions_update(wb):
    ws = wb["Decisions"]; log = []
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "AF1-D8":
            if ws.cell(r, 7).value == "v6.0 已建":
                ws.cell(r, 7).value = "v6.0 已建；「TTFT 未納入」部分由第 2 批 2-1 段（AF2-TTFT，v6.2）取代"; log.append("Decisions AF1-D8: status (v6.2)")
    return log


def gov_update(ws, append_text):
    return 0      # no existing Gov_Map row changes in 2-1


def gov_map_rows(wb):
    """Three Gov_Map rows for the Spec_Rack scale section (appended by gov.gm_append_c when absent)."""
    ws = wb["Spec_Rack"]
    r0 = next(r for r in range(20, ws.max_row + 1) if ws.cell(r, 1).value == SEC_TITLE)
    out = []
    spec = [("基準", "ARCH_ScaleGen", "單值", 1, 1, "基準 1（固定模型口徑）"),
            ("低", "ARCH_ScaleGen_Lo", "低", 0.1, 1, "低端：Hopper 0.1、GB200 0.3、GB300 1、VR200 1"),
            ("高", "ARCH_ScaleGen_Hi", "高", 0.5, 4.4, "高端：Hopper 0.5、GB200 1.0、GB300 1、VR200 4.4")]
    for i, (tag, name, role, lo, hi, rt) in enumerate(spec):
        r = r0 + 1 + i
        out.append({'scope': '切片三（v6.2 D1(c)）', 'sheet': 'Spec_Rack', 'cell': f'C{r}:G{r}', 'label': f'模型規模倍數（{tag}；{name}）', 'check': ws.cell(r, 1).value,
                    'cls': 'Assumed', 'role': role, 'src': '', 'rel': '', 'dec': 'AF2-D1c', 'lo': None, 'hi': None, 'rtext': rt,
                    'reason': ("D1(c)（AF2-D1c）：每世代的層級代表模型會變大，用啟用參數倍數作情境，不重建 Arch；基準 1＝固定模型口徑。"
                               "J1 兩種讀法 R-a（預設：2026 快照對應 GB300）／R-b（快照對應 GB200）；幅度取啟用參數：Hopper 數百億 ÷ 180B ≈ 0.1–0.5、VR200 400–800B ÷ 180B ≈ 2.2–4.4，"
                               "中間以幾何內插；原話的『例如』是舉例不是邊界，只作區間不作證據；已搜尋：2Q 查證段進行中；可比對象無；區間依據即本列"),
                    'retag': '', 'seg': '高'})
    return out


# ================================================================== Decisions (10 columns; layout of v530–v601)
_D = [
    ("D1c", "D1(c) 模型規模倍數（啟用參數倍數，情境）", "Spec_Rack 新增三列（基準 1／低 0.1,0.3,1,1／高 0.5,1.0,1,4.4；具名範圍 ARCH_ScaleGen／_Lo／_Hi，Assumed）。倍數乘入 Perf／Perf_Batch／Sens_Perf 第 28、32、33 列與 "
     "Training／Sens_Train 第 22 列；Calib 第 30 列不乘（校準固定讀 Arch!$D$7）。基準一律 1，基準輸出不變；新增 parity 情境 d1_model_scale＝[0.25,0.5,1.0,2.5]（J1 預設）。"
     "兩種讀法：R-a（預設）2026 快照對應 GB300，GB300 倍數＝1；R-b 快照對應 GB200，GB200 倍數＝1、其餘依比例前移。只放大參數（每 token FLOPs、權重 bytes），KV 與層數不變，因此是模型變大效果的下限。"
     "Interface 各世代區塊標題與 L1_TokMW_Gen_ratio_* 說明加註『固定模型口徑』。",
     "Spec_Rack 模型規模倍數節；Perf／Perf_Batch／Sens_Perf 第 28、32、33 列；Training／Sens_Train 第 22 列；Gov_Map（新增 3 列）；Interface B／C／D 節標題；L1 第 58–60 列；tests/parity/scenarios.yaml d1_model_scale",
     "第 1 節 J1；第 2 節 2-1-a"),
    ("TTFT", "TTFT 納入可達判斷（取代 AF1-D8 的『TTFT 未納入』）", "Perf／Perf_Batch／Sens_Perf 的『每請求 GPU 秒』（第 93 列）與『綁定約束』（第 90 列）讀第 77 列 TTFT：TTFT 不為『是』時輸出文字旗標『TTFT 不可達』，不輸出 0（D8）。"
     "判斷順序：先判 decode（B ≤ 0 或每 GPU decode token ≤ 0 → 『SLO 不可達』），再判 TTFT（→『TTFT 不可達』）；兩者皆不符時顯示『SLO 不可達』。Perf_Prod 鏡像同步。Checks B27 同時計兩種旗標。"
     "基準下變動：Hopper 欄 Astra 層（TTFT＝否）的每請求 GPU 秒與 IF_TokGW_Astra（Hopper）由數值變為文字旗標；其餘層級與世代不變。",
     "Perf／Perf_Batch／Sens_Perf／Perf_Prod 第 90、93 列及其下游（Unit_Cost、Fleet_1GW、Theory_Rev、Interface）；Checks B27", "決定紀錄第 4 節；第 2 節 2-1-b"),
    ("ALLOC", "Alloc 排除不可達層級後重新正規化", "每世代 AL_TokGW_g ＝ IF_Util ÷ Σ_{t 可達}（w_t ÷ Σ_{t 可達} w_t ÷ IF_TokGW_{g,t}），層級權重 B4_Mix 只在可達層級間重新正規化（比照 Fleet_1GW）；"
     "某世代全部層級不可達則該世代輸出文字旗標，跨世代 AL_Mix* 在其餘世代間重新正規化。新增顯示列『未服務需求占比』（每世代被排除層級的權重合計；基準 Hopper＝Astra 的權重）。"
     "AL_BlendPaid／AL_BlendFree、Cap_In H10 `_CAP` 與 Alloc G、H 節照此重算。取代 v6.0 『組合內任一層級不可達 → 整欄文字』。",
     "Alloc B、G、H 節；Cap_In H10 世代混合列；AL_ServeGW、AL_Q1／Q2、AL_ImpliedRDGW、AL_J8Gap；L1_ScaleServe、L1_MFleet、L1_Gap*", "第 2 節 2-1-c"),
]
DECISIONS_V602 = [[f"AF2-{i}", V, f"稽核修正第 2 批 2-1：{t}", txt, DATE, ANDY, "v6.2 已建", where, f"{WO} {sec}", "否"] for i, t, txt, where, sec in _D]

# ================================================================== README
README_VERSION = (VERSION + "（次版：稽核修正第 2 批 2-1 段，" + WO + "——D1(c) 模型規模倍數（Spec_Rack 三列＋ARCH_ScaleGen*，基準 1，乘入 Perf 系第 28、32、33 列與 Training 系第 22 列）；"
                  "TTFT 接進可達判斷（文字旗標『TTFT 不可達』）；Alloc 排除不可達層級後重新正規化（新增『未服務需求占比』）；Decisions AF2-D1c／AF2-TTFT／AF2-ALLOC）。以下為 "
                  + v601.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v601.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v601.VERSION.split("_")[-1]):]
README_ROW = ("模型規模、TTFT、Alloc（v6.2）",
              "稽核修正 2-1：模型規模倍數（Spec_Rack，基準 1，情境 d1_model_scale）；TTFT 不達標的欄輸出『TTFT 不可達』並自 Alloc 排除、其餘層級重新正規化（基準下 Hopper Astra），"
              "Alloc 顯示『未服務需求占比』。標記與理由見 Gov_Map 與 Decisions AF2-*。")

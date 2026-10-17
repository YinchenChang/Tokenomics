# v14.0 (work order docs/workorders/20261017_4-3B.md, branch claude/4-3b; slimming 4-3 B: execute the A-stage recommendations).
# Major version: new contract names (11 IF_ on Interface M, 7 L1_ series on Cap_In) are added; no existing IF_／IFW_／L1_／RNG_ value changes.
#   Q1  delete the cells of 73 rows (72 A-stage rows with disposition 刪除 + Har_In 44; builder/v1400_data.json, tools/gen_v1400_data.py):
#       only value cells are cleared (rows and columns are not shifted); the 用途 column of each deleted row carries the deletion note.
#       Names B5_TaskTok (Harness C44:G44) and B5_SelVendor (Har_In C44:G44) pointed only at deleted cells and are removed; Harness A157 loses the sentence about the vendor flag.
#   Q2  18 names: Interface M (IF_TaskTokMult, IF_TrainFLOP_／IF_TrainInferShare_／IF_GMDefault_ × Luna／Sol／Astra, IF_AmortRevShare)
#       and series names on Cap_In (L1_MAPI_Ser, L1_MSub_Ser, L1_MSeat_Ser, L1_MImplied_Ser, L1_MFleet_Ser, L1_MFleet_P25Lo, L1_MFleet_P25Hi).
#       Luna／Sol／Astra are 層級 (tiers), not generations. L1_MFleetFloor is NOT upgraded (Q3: definition open, see report).
#   Q4  Checks V23–V26 (counted in the verification count) and Checks D104／D140 re-pointed to Alloc_In C18／C33 (single definition).
#   Q5  用途 marks for the 155 kept display rows (builder/v1400_data.json) and for the cells that became dead through Q1 (v1400_marks.json).
# Every write to an Excel-owned cell is guarded (old value / old text).
import json
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.styles import PatternFill

from common import put, F_NOTE, F_BOLD, F_CALC, section
import v1310

VERSION = "20261017_Tokenomics_v14.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-17"
V = "v14.0"
WO = "工作單 docs/workorders/20261017_4-3B.md"
DEC_BY = "Andy 2026-10-17 09:18（Har_In 44 刪除）；其餘依 4-3 A 段建議與本工作單（chat 端 2026-10-17 定案，可撤回）"
DASH = "—"
HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "v1400_data.json").read_text(encoding="utf-8"))
_MJ = HERE / "v1400_marks.json"
EXTRA = json.loads(_MJ.read_text(encoding="utf-8")) if _MJ.exists() else {}      # marks for cells that became dead through Q1 (written after the first build)
NO_FILL = PatternFill(fill_type=None)
PURPOSE = "用途"
PURPOSE_HDR_ROW = 3
DEL_NOTE = "已刪除（v14.0，4-3B Q1）：功能未接線，已移除，需要時再接線；原範圍 {rng}；見 Decisions SL43-1"
FLOPS_FMT = "0.00E+00"

REMOVE_NAMES = {"B5_TaskTok": "Harness!$C$44:$G$44", "B5_SelVendor": "Har_In!$C$44:$G$44"}
H157_OLD = "選定檔案『供應商專屬』時，前緣組合綁定該供應商 API（Har_In 旗標）。"
H157_NEW = ""
H157_A = "前緣只比較成本，不含延遲；"
H157_A_NEW = "前緣只比較成本，不含延遲。"      # the sentence about the vendor flag is dropped; the clause before it now ends the sentence


# ================================================================== Q1: delete cells
def _cells(rng):
    c1, r1, c2, r2 = openpyxl.utils.range_boundaries(rng)
    return [(r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def _purpose_col(ws, create=True):
    last = 0
    for row in ws.iter_rows():
        for cell in row:
            if cell.value is not None:
                last = max(last, cell.column)
    for c in range(3, last + 1):
        if ws.cell(PURPOSE_HDR_ROW, c).value == PURPOSE:
            return c
    if not create:
        return None
    col = last + 1
    put(ws, f"{L(col)}{PURPOSE_HDR_ROW}", PURPOSE, F_BOLD)
    ws.column_dimensions[L(col)].width = 46
    return col


def delete_cells(wb):
    n_cells = n_rows = 0
    for e in DATA["delete"]:
        ws = wb[e["sheet"]]
        for r, c in _cells(e["range"]):
            cell = ws.cell(r, c)
            if cell.value is not None:
                cell.value = None; cell.fill = NO_FILL; n_cells += 1
        pc = _purpose_col(ws)
        put(ws, f"{L(pc)}{e['row']}", DEL_NOTE.format(rng=e["range"]), F_NOTE)
        n_rows += 1
    removed = []
    for n, ref in REMOVE_NAMES.items():
        if n in wb.defined_names:
            assert wb.defined_names[n].attr_text == ref, (n, wb.defined_names[n].attr_text)
            del wb.defined_names[n]; removed.append(n)
    ws = wb["Harness"]
    t = ws["A157"].value
    if isinstance(t, str) and H157_OLD in t:
        t = t.replace(H157_A + H157_OLD, H157_A_NEW)
        assert H157_OLD not in t, "Harness A157 sentence not removed"
        ws["A157"].value = t
    return dict(rows=n_rows, cells=n_cells, names=removed)


# ================================================================== Q5: 用途 marks
def purpose_marks(wb):
    n = 0
    plan = {sh: dict(rows) for sh, rows in DATA["marks"].items()}
    for sh, rows in EXTRA.get("marks", {}).items():
        plan.setdefault(sh, {}).update(rows)
    for sh, rows in NAME_MARKS.items():
        plan.setdefault(sh, {}).update(rows)
    deleted = {(e["sheet"], e["row"]) for e in DATA["delete"]}
    for sh, rows in plan.items():
        ws = wb[sh]
        pc = _purpose_col(ws)
        for r, txt in rows.items():
            assert (sh, int(r)) not in deleted, ("mark on a deleted row", sh, r)
            put(ws, f"{L(pc)}{int(r)}", txt, F_NOTE); n += 1
    return n


# ================================================================== Q2: names
M_TITLE = ("M. 契約補名（v14.0，工作單 4-3B Q2）：18 個名稱中的 11 個 IF_ 名稱；其餘 7 個 L1_ 序列名稱在 Cap_In（見下游契約文件）。"
           "Luna／Sol／Astra 是模型層級（低／中／頂），不是世代；欄＝世代 × 成本情境（任務別列：欄 C–G＝Workload 任務）。"
           "每列標明層級與 token 類型；『混合』＝該值本身是跨 token 類型的混合比值，不能拆回單一類型")
TIERS = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
GM_ROW = {"Luna": 24, "Sol": 42, "Astra": 60}


def interface_m(wb):
    ws = wb["Interface"]
    start = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, start, M_TITLE, 17)
    r = start + 1
    made = []

    def name_it(name, ref):
        wb.defined_names[name] = DefinedName(name, attr_text=ref)

    # task-level multiple (columns C–G = Workload tasks)
    put(ws, f"A{r}", "任務總 token ÷ 一般聊天總 token（欄 C–G＝Workload 任務，同 E 節 IF_HdrTask；任務別，非模型層級；"
                     "token 類型＝總 token：新鮮輸入＋快取輸入＋decode，混合）　[IF_TaskTokMult]"); put(ws, f"B{r}", "x")
    for k in range(3, 8):
        X = L(k); put(ws, f"{X}{r}", f"=Workload!{X}38", fmt="0.0")
    name_it("IF_TaskTokMult", f"Interface!$C${r}:$G${r}"); made.append(("IF_TaskTokMult", r)); r += 1
    for t, (tk, tn) in enumerate(TIERS, start=1):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        pick = lambda row: "=INDEX(Training!$C${0}:$Q${0},3*(Unit_Cost!{{X}}$6-1)+{1})".format(row, t)
        rows = [
            (f"IF_TrainFLOP_{tk}", f"最終訓練 FLOPs（{tn[:tn.index('（')]}層級；單一模型；預訓練側＋後訓練＋合成資料＋評測；訓練側，無 token 類型；不隨成本情境變動）",
             "FLOP", FLOPS_FMT, pick(109)),
            (f"IF_TrainInferShare_{tk}", f"推論型占最終訓練（GPU 小時口徑；{tn[:tn.index('（')]}層級；rollout 等推論型工作占最終訓練 GPU 小時；訓練側，無 token 類型）",
             "%", "0.0%", pick(114)),
            (f"IF_GMDefault_{tk}", f"理論毛利率（{tn[:tn.index('（')]}層級；OpenAI 有效單價；K6 預設 (c) 全成本口徑；token 類型＝付費 token 混合：新鮮輸入＋快取輸入＋輸出）",
             "%", "0.0%", "=Theory_Rev!{X}" + str(GM_ROW[tk])),
        ]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for k in range(3, 18):
                X = L(k); put(ws, f"{X}{r}", tpl.replace("{X}", X), fmt=fmt)
            name_it(name, f"Interface!$C${r}:$Q${r}"); made.append((name, r)); r += 1
    put(ws, f"A{r}", "攤提占付費營收（K6 (d) 口徑：由上而下年化總額 ÷ 付費營收合計（OpenAI 有效單價，可達層級）；各層級相同；"
                     "營收類型＝付費營收，混合）　[IF_AmortRevShare]"); put(ws, f"B{r}", "%")
    for k in range(3, 18):
        X = L(k); put(ws, f"{X}{r}", f"=Amortize!{X}49", fmt="0.0%")
    name_it("IF_AmortRevShare", f"Interface!$C${r}:$Q${r}"); made.append(("IF_AmortRevShare", r))
    return dict(start=start, made=made)


# L1_ series names on Cap_In (columns: C＝2025 年度、D＝2026 Q1 年化、E＝2026 Q2 年化、F＝FY2026 預測；P25 兩列：C 基準、D token 取高、E token 取低)
SER_NAMES = [
    ("L1_MAPI_Ser", "Cap_In!$C$206:$F$206", 206, "m_API 序列（倍）｜口徑：API 營收 ÷（API token × 付費 token 混合有效單價）｜token 類型：付費 token（混合）"),
    ("L1_MSub_Ser", "Cap_In!$C$207:$F$207", 207, "m_消費訂閱 序列（倍）｜口徑：消費訂閱營收 ÷（ChatGPT 付費 token 中消費訂閱部分 × 混合有效單價）｜token 類型：付費 token（混合）"),
    ("L1_MSeat_Ser", "Cap_In!$C$208:$F$208", 208, "m_商用席次 序列（倍）｜口徑：商用席次營收 ÷（商用席次 token × 混合有效單價）；席次占比為 Assumed、帶區間｜token 類型：付費 token（混合）"),
    ("L1_MImplied_Ser", "Cap_In!$C$209:$F$209", 209, "m_整體 序列（倍）｜口徑：整體（token 加權）｜token 類型：付費 token（混合）"),
    ("L1_MFleet_Ser", "Cap_In!$C$223:$F$223", 223, "m_fleet 序列（倍）｜口徑：機隊口徑（機隊付費 token × 機隊口徑單價 B4_PriceFleet）｜token 類型：付費 token（混合）"),
    ("L1_MFleet_P25Lo", "Cap_In!$C$285:$E$285", 285, "m_fleet（2025 單價取低端）（倍）｜欄 C 基準、D token 取高、E token 取低｜口徑：機隊，2025 年度單價低端 AL_PriceFleet25_Lo｜token 類型：付費 token（混合）；顯示用區間，不乘入 L1_MFleet 的 _Lo／_Hi"),
    ("L1_MFleet_P25Hi", "Cap_In!$C$286:$E$286", 286, "m_fleet（2025 單價取高端）（倍）｜欄 C 基準、D token 取高、E token 取低｜口徑：機隊，2025 年度單價高端 AL_PriceFleet25_Hi｜token 類型：付費 token（混合）；顯示用區間，不乘入 L1_MFleet 的 _Lo／_Hi"),
]
NAME_MARKS = {"Cap_In": {str(r): f"契約名稱 {n}（v14.0）：{txt}；欄 C＝2025 年度、D＝2026 Q1 年化、E＝2026 Q2 年化、F＝FY2026 預測" if r not in (285, 286) else f"契約名稱 {n}（v14.0）：{txt}"
                         for n, _, r, txt in SER_NAMES}}
NAME_MARKS["Cap_In"]["121"] = "顯示用：C121:E121（待定義，見 4-3B 報告）｜物理下限 0.301 與 L1_MFleet_Lo 0.184 的定義不同，三種處理待 Project 判斷；本版不升級為契約名稱"


def series_names(wb):
    for n, ref, r, _ in SER_NAMES:
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return [n for n, *_ in SER_NAMES]


# ================================================================== Q4: Checks V23–V26 and D104／D140
def v_items(wb):
    """Items in the format of v1000.checks_v: (id, label, C, D, E, lower, upper, note). F = 1 if lower <= E <= upper."""
    E_NUM = '=IF(ISNUMBER(C{r}),C{r},"—")'
    return [
        ("V23", "實際每用戶 decode 速度 ≥ SLO（Perf 與 Perf_Batch 第 89 列對第 41 列；可達欄中低於 SLO 的欄數＝0；全部層級，token 類型＝decode token）【恆等式（非驗證）；v14.1 R2】",
         "=IFERROR(SUMPRODUCT((Perf!$C$87:$Q$87>0)*(Perf!$C$89:$Q$89<Perf!$C$41:$Q$41*(1-0.000000001)))"
         "+SUMPRODUCT((Perf_Batch!$C$87:$S$87>0)*(Perf_Batch!$C$89:$S$89<Perf_Batch!$C$41:$S$41*(1-0.000000001))),1)",
         "=SUMPRODUCT(--(Perf!$C$87:$Q$87>0))+SUMPRODUCT(--(Perf_Batch!$C$87:$S$87>0))",
         '=IF(AND(ISNUMBER(C{r}),ISNUMBER(D{r})),IF(D{r}>0,C{r},1),"—")', 0, 0,
         "v14.0 4-3B Q4（A 段第 4 節）：模型值＝低於 SLO 的可達欄數（Perf 15 欄＋Perf_Batch 17 欄；B*＝0 的不可達欄不計）；對照值＝可達欄數（為 0 時本項判失敗，防止空轉）。"
         "結構性恆成立（B* ＝ MIN(SLO 限制批次, 記憶體限制批次)），程式或公式被改壞時才會失敗；專屬測試改寫 Perf!C87 公式（無法只靠改輸入使其失敗，見報告）"),
        ("V24", "m_整體一致：Cap_In 第 147 列（Σ營收 ÷（Σtoken × 單價））＝ L1_MImplied（基準／_Lo／_Hi 三格的最大絕對差，容差 1e-9）；層級＝整體，token 類型＝付費 token（混合）【恆等式（非驗證）；v14.1 R2】",
         "=IFERROR(MAX(ABS(Cap_In!$C$147-L1_MImplied),ABS(Cap_In!$D$147-L1_MImplied_Lo),ABS(Cap_In!$E$147-L1_MImplied_Hi)),1)", 0, E_NUM, 0, 0.000000001,
         "v14.0 4-3B Q4：兩條路徑各自算 m_整體（Cap_In 第 147 列用 H8 三分合計；L1_MImplied 取 Cap_In 第 94 列用合併 token）；差異＝0 才通過。"
         "目前兩者由同一組輸入恆等；公式被改寫（例如分子或分母漏項）時才會失敗；專屬測試改寫 Cap_In!C147 公式（見報告）"),
        ("V25", "需求 ÷ 上限讀法 ≤ 1：Cap_In 第 175 列三格（C 基準、D、E）的最大值；層級＝機隊，token 類型＝付費 token（混合）",
         "=IF(COUNT(Cap_In!$C$175:$E$175)=3,MAX(Cap_In!$C$175:$E$175),\"—\")", 1, None, 0, 1,
         "v14.0 4-3B Q4：需求路線付費 token ÷ 上限路線付費 token（L1_TokCeiling）；> 1 代表需求超過物理上限。Checks M4 只比點估計（0.5–2），本項補上限讀法。"
         "上限路線為文字（SLO 不可達）時本項不適用（—）；專屬測試把 Alloc_In 的 ChatGPT 每日則數調高使比值 > 1"),
        ("V26", "2026 服務世代組合合計＝100%：Cap_In 第 215 列四格（C–F）與 1 的最大絕對差（容差 1e-9）；層級＝全部，無 token 類型",
         "=IFERROR(MAX(ABS(Cap_In!$C$215-1),ABS(Cap_In!$D$215-1),ABS(Cap_In!$E$215-1),ABS(Cap_In!$F$215-1)),1)", 0, E_NUM, 0, 0.000000001,
         "v14.0 4-3B Q4：與 Checks H1（2025 服務世代組合，恆等式）並列；2026 三欄的組合是 Cap_In D211:F214 的 Assumed 輸入，合計不為 100% 時 m_fleet 的權重失真；"
         "專屬測試把 Cap_In!D214 由 0.05 改為 0.10"),
    ]


def checks_fix(wb):
    """D104／D140 read Alloc_In C18／C33 (single definition); V-row number formats for the tolerance bands."""
    ws = wb["Checks"]
    n = 0
    for r, old, new, eold, enew in (
            (104, "=IF(ABS(SUM(AL_MixGen)-1)>0.000000001,1,0)", "=IF(ABS(Alloc_In!$C$18-1)>0.000000001,1,0)",
             "Alloc_In 世代組合四格", "Alloc_In 第 18 列（服務世代組合合計；C18＝SUM(AL_MixGen)，單一定義；v14.0）"),
            (140, "=IF(ABS(AL_RDMixHopper+AL_RDMixGB200+AL_RDMixGB300+AL_RDMixVR200-1)>0.000000001,1,0)", "=IF(ABS(Alloc_In!$C$33-1)>0.000000001,1,0)",
             "Alloc_In 研發世代組合四格（基準欄）", "Alloc_In 第 33 列（研發世代組合合計；C33＝四格之和，單一定義；v14.0）")):
        assert ws[f"A{r}"].value in ("H1", "Z2"), (r, ws[f"A{r}"].value)
        cur = ws[f"D{r}"].value
        nm = lambda x: str(x).replace("0.000000001", "1E-9")      # the builder writes 1E-9, LibreOffice saves 0.000000001
        assert nm(cur) in (nm(old), nm(new)), (r, cur)
        if nm(cur) == nm(old):
            ws[f"D{r}"].value = new; n += 1
        if ws[f"E{r}"].value == eold:
            ws[f"E{r}"].value = enew
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if a == "V24":
            ws[f"H{r}"].number_format = "0.0E+00"; ws[f"I{r}"].number_format = "0.0E+00"
        if a == "V26":
            ws[f"H{r}"].number_format = "0.0E+00"; ws[f"I{r}"].number_format = "0.0E+00"
        if a == "V23":
            ws[f"H{r}"].number_format = "0"; ws[f"I{r}"].number_format = "0"
    return n


# ================================================================== Decisions
_D = [
    ("1", "Q1 刪除：73 列（509＋5 格）未接線，已移除",
     "A 段明細處置＝刪除的 72 列（509 格）加 Har_In 第 44 列（C44:G44，供應商專屬旗標；Andy 2026-10-17 09:18 決定刪除）。做法：只清空數值格，不刪列欄、不移動參照；各列『用途』欄寫刪除註記。"
     "刪除前逐列再確認：公式、具名範圍、Checks、Sens_* 比對、鏡像測試皆不讀這些格，唯一的讀者是名稱 B5_TaskTok（Harness C44:G44）與 B5_SelVendor（Har_In C44:G44），兩個名稱無人使用，一併移除；"
     "Harness A157 說明刪去『供應商專屬』一句。理由：功能未接線，已移除，需要時再接線。",
     "各頁（見報告刪除清單）；具名範圍 B5_TaskTok、B5_SelVendor；Harness A157", "v14.0 已建"),
    ("2", "Q2 升級 18 個名稱（Interface M 節 11 個、Cap_In 序列 7 個）",
     "新增 IF_TaskTokMult、IF_TrainFLOP_／IF_TrainInferShare_／IF_GMDefault_ × Luna／Sol／Astra、IF_AmortRevShare（Interface M 節）；L1_MAPI_Ser、L1_MSub_Ser、L1_MSeat_Ser、L1_MImplied_Ser、L1_MFleet_Ser、L1_MFleet_P25Lo、L1_MFleet_P25Hi（Cap_In 第 206–209、223、285–286 列）。"
     "Luna／Sol／Astra 是層級，不是世代；每個名稱的說明帶層級與 token 類型，值本身為混合比值者註明『混合』。主版升級（新增契約名稱）；既有 IF_／IFW_／L1_／RNG_ 數值全部不變。"
     "27 列『升級（隨附上游）』保留為核心。批次口徑區間：新名稱中隨 CAL_BatchEtaD 變動者依 v13.0 K1 規則補 RNG_<名稱>_Lo／_Hi（見報告）。",
     "Interface M 節；Cap_In 第 206–209、223、285–286 列；下游契約文件；契約快照", "v14.0 已建"),
    ("3", "Q3 L1_MFleetFloor 不升級（定義待 Project 判斷）",
     "Cap_In 第 121 列（m 下限，上限讀法）C 欄 0.301 為『機隊付費 token 上限 × 2025 年度混合單價』下的物理下限；L1_MFleet_Lo（0.184）取 token 取高情境（含 τ 區間），兩者區間定義不同，0.184 低於 0.301。"
     "本版只查明、不改數值；Cap_In 第 121 列保留為顯示用，用途標記『待定義，見 4-3B 報告』。三種處理（截在下限／修正下限定義／改寫標籤）列報告『待 Project 判斷』。",
     "Cap_In 第 119、121 列；L1 第 78 列", "待判斷"),
    ("4", "Q4 接進 Checks：V23–V26 與 D104／D140 單一定義",
     "新增 Checks V23（Perf／Perf_Batch 實際速度 ≥ SLO）、V24（Cap_In 第 147 列 ＝ L1_MImplied）、V25（Cap_In 第 175 列 ≤ 1）、V26（Cap_In 第 215 列＝100%），計入驗證項目數；"
     "Checks D104、D140 改讀 Alloc_In C18、C33（不再自己重算）。每條新檢查各有專屬必須失敗測試（tests/parity/test_v1400.py）；V23、V24 為結構性恆等式，只能靠改寫公式格使其失敗，已在報告說明。",
     "Checks V 節；Checks D104、D140；tests/parity/test_v1400.py", "v14.0 已建"),
    ("5", "Q5 用途標記與死格基準",
     "保留：顯示用 155 列補『用途』標記（文字由 CC 依 A 段理由擬寫，報告附清單供 Andy 抽查）；刪除後新增的死格（上游只被已刪除的列讀取者）補標記；DEAD_BASELINE（test_slim.py）與無標記死格 fixture 依刪除、升級、標記更新，新舊值見報告；目標無標記 B 級＝0。",
     "各頁『用途』欄；tests/parity/test_slim.py；tests/parity/fixtures", "v14.0 已建"),
]
DECISIONS_V1400 = [[f"SL43-{i}", V, f"瘦身 4-3B：{t}", txt, DATE, DEC_BY, st, where, f"{WO} Q{i}", "否"] for i, t, txt, where, st in _D]


def decisions_append(wb):
    ws = wb["Decisions"]
    have = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    r = max([rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")] or [4]) + 1
    n = 0
    for row in DECISIONS_V1400:
        if row[0] in have:
            continue
        for i, v in enumerate(row):
            put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 5, 7))
        r += 1; n += 1
    return n


# ================================================================== README
README_VERSION = (VERSION + "（主版：" + WO + "——4-3 B 段依 A 段建議執行瘦身：刪除 73 列未接線的計算格（509＋5 格）與兩個無人使用的名稱；新增 18 個契約名稱"
                  "（Interface M 節 IF_TaskTokMult、IF_TrainFLOP_／IF_TrainInferShare_／IF_GMDefault_ 三層級、IF_AmortRevShare；Cap_In 序列 L1_*_Ser 與 L1_MFleet_P25Lo／Hi）；"
                  "Checks 新增 V23–V26 並計入驗證項目數、D104／D140 改讀 Alloc_In；保留的顯示用 155 列與新增死格補用途標記；既有 IF_／IFW_／L1_／RNG_ 數值不變）。以下為 "
                  + v1310.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1310.README_TITLE
README_TITLE = V + _T[len(v1310.V):]
README_ROW = ("瘦身 4-3B（v14.0）",
              "刪除未接線的計算格；新增 18 個契約名稱（層級與 token 類型標明）；Checks 新增 V23–V26；用途標記補齊。既有名稱的數值不變。細節見 Decisions SL43-*。")


def apply(wb, append_text):
    log = {}
    log["delete"] = delete_cells(wb)
    log["checks_fix"] = checks_fix(wb)
    log["marks"] = purpose_marks(wb)
    log["decisions"] = decisions_append(wb)
    return log

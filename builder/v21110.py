# v21.11 (= v22.0 segment B1「結構一」; design docs/plan/20261105_v22.0_Terra第四層級_設計.md, section 6.1 row B1; branch claude/v22-b1).
# Module name v21110 (= v21.11.0): builder/v2111*.py would read as v21.1.x (v21.10 report, 待 Project 判斷 1).
# Andy's authorization (2026-11-05): 「完整第四層級」; the J1–J15 recommendations of the design are adopted as defaults (「照建議」).
#
# STRUCTURAL version: every existing value stays the same; no IF_／IFW_／L1_／RNG_／CAP_ name is added or removed; the shapes of DRV_* (16) and
# TRN_* (15) names change from 1×15 to 1×20. What the builder now does differently lives where the tier dimension lives (builder/tiers.py is the
# single source of the tier list):
#   S1  Arch: Terra column F (design 3.1, J4 V4-family interpolation); 標記／說明 move F／G -> G／H. Gov_Map reason formulas =Arch!$G$6／$G$7／$G$10
#       follow to $H$ (gov_update below; guarded: only formulas still pointing at $G$ of an Arch row).
#   S2  Serving rows 20-24: Terra in F (design 3.2, J11／J12); 說明 F -> G on those rows.  Train_In rows 23-38: Terra in F (design 3.4), Terra mark
#       and range in G.  Har_In rows 47-50: Terra in F (design 3.7). Row 58 (Terra success override, B5_SuccOvr_Terra) is v21.12 (B2) scope.
#   S3  Perf, Perf_Batch, Training (and their *_Prod copies): 20 generation × tier columns C..V, index 4*(g-1)+t (J3 (a)); Perf_Batch FP8 scenario
#       R／S -> W／X; *_Prod check copies from column X (SHIFT 16 -> 21). Sens_Perf／Sens_Train keep their scenario layout (Sol／Astra only).
#   S4  Readers of those sheets switch to the generation × tier index (Unit_Cost, Interface B／C／M, Alloc C／J, Training, Sens_Train, L1, Cap_In M-4,
#       Checks); the cost-scenario 3*(g-1)+k uses are untouched (design R1).
#   S5  preserve: blue inputs of the re-laid sheets follow their (generation, tier) when the base has the old 15-column layout (R2／R13; build.py).
#   S6  Unit_Cost Terra block (rows 51-61); no reader yet -> 用途 marks「預備」(R8).
#   S7  Version files: README B5／A1, Load_Bearing!C3, Decisions SL68-01; ranges／fingerprint JSON regenerated.
from openpyxl.utils import get_column_letter as L

from common import put, F_CALC, F_NOTE
import tiers
import v1410
import v21100

VERSION = "20261105_Tokenomics_v21.11"      # single source of the version string: README!B5 and README!A1 (finish.readme); Load_Bearing!C3 (load_bearing_date)
DATE = "2026-11-05"
DASH = "—"
V = "v21.11"
DESIGN = "docs/plan/20261105_v22.0_Terra第四層級_設計.md"
WO = f"v22.0 B1 段（結構一）：設計文件 {DESIGN} 第 6.1 節 B1 列（chat 端派工）"
DEC_ID = "SL68-01"
DEC_BY = ("Andy 2026-11-05：「完整第四層級」；設計文件第 4 節 J1–J15 依建議預設值執行（「照建議」）。"
          "本段（B1）為結構變更：既有值逐值不變")

# ---------------------------------------------------------------- Gov_Map (Excel-owned A–P; guarded, idempotent)
# Registered ranges of the re-laid sheets (column D). The old keys stay in gov.gm_append's "have" set so a rebuild never re-registers them.
GM_RANGES = [("Perf", "C6:Q6", "C6:V6"), ("Perf", "C7:Q7", "C7:V7"), ("Training", "C6:Q6", "C6:V6"), ("Training", "C7:Q7", "C7:V7"),
             ("Perf_Batch", "C6:S6", "C6:X6"), ("Perf_Batch", "C7:S7", "C7:X7"), ("Perf_Batch", "R19:S20", "W19:X20")]
GM_OLD_KEYS = {(sh, old) for sh, old, _ in GM_RANGES}
ARCH_ROWS = range(5, 39)


def gm_key(sheet, cell):
    """The current Gov_Map key of a registration that v21.11 moved (for lookups written against the v21.10 key)."""
    for sh, old, new in GM_RANGES:
        if (sh, old) == (sheet, cell):
            return new
    return cell


def gov_update(ws, append_text):
    n = 0
    for r in range(5, ws.max_row + 1):
        sh, cell = ws[f"C{r}"].value, ws[f"D{r}"].value
        for s2, old, new in GM_RANGES:
            if (sh, cell) == (s2, old):
                ws[f"D{r}"].value = new; n += 1
                append_text(ws[f"N{r}"], f" ｜{V}：登錄範圍 {old} → {new}（世代 × 層級頁改為 20 欄，Terra 第四層級；{DECISION_REF}）")
        c = ws[f"N{r}"]
        if isinstance(c.value, str) and c.value.startswith("=") and "Arch!$G$" in c.value:
            import re
            m = re.findall(r"Arch!\$G\$(\d+)", c.value)
            if m and all(int(x) in ARCH_ROWS for x in m):
                c.value = re.sub(r"Arch!\$G\$(\d+)", r"Arch!$H$\1", c.value); n += 1
    return n


DECISION_REF = f"Decisions {DEC_ID}"


# ---------------------------------------------------------------- 用途 marks for the Terra cells nobody reads yet (R8)
PREP = "預備（v21.11 結構一）：Terra 第四層級，v22.0 啟用前尚無下游讀取"


def purpose_marks(wb):
    import v1400
    n = 0
    ws = wb["Unit_Cost"]
    pc = v1400._purpose_col(ws)
    first = None
    for r in range(1, ws.max_row + 1):
        if isinstance(ws.cell(r, 1).value, str) and ws.cell(r, 1).value.startswith(tiers.TIERS[-1][1]):
            first = r; break
    assert first, "Unit_Cost Terra block not found"
    for r in range(first + 1, ws.max_row + 1):
        if ws.cell(r, 3).value is not None:
            put(ws, f"{L(pc)}{r}", PREP + f"（C{r}:Q{r}）", F_NOTE); n += 1
    return n


# ---------------------------------------------------------------- Load_Bearing!C3 (same rule as v21.10: the date of the version file name)
def load_bearing_date(wb):
    ws = wb["Load_Bearing"]
    assert str(ws["A3"].value).startswith("建置日"), ws["A3"].value
    d = VERSION.split("_", 1)[0]
    assert len(d) == 8 and d.isdigit(), VERSION
    put(ws, "C3", f"{d[:4]}-{d[4:6]}-{d[6:]}", F_CALC)


# ---------------------------------------------------------------- Decisions SL68-01
def _decisions():
    return [[DEC_ID, V, "v22.0 B1（結構一）：GPT-6.1 Terra 第四層級的計算結構（Block 1–3），既有值逐值不變",
             "依設計文件 " + DESIGN + "（J1 (a) 索引 4、J2 (a) F 欄、J3 (a) 20 欄、J4 (a) V4 家族內插、J11 (a)、J12）："
             "builder 以 builder/tiers.py 為層級清單單一來源（Luna、Sol、Astra、Terra；NT＝4；契約與跨層級合計仍為 3 層，NT_LIVE＝3，v22.0 B3 改 4）。"
             "Arch 插入 Terra 欄 F（標記／說明移 G／H；Gov_Map 理由欄 =Arch!$G$6／$G$7／$G$10 隨之改 $H$）；Serving 第 21–24 列、Train_In 第 25–38 列、"
             "Har_In 第 48–50 列 F 欄寫入 Terra 輸入（藍字，設計第 3 節基準值；區間寫在說明欄）；Perf、Perf_Batch、Training 及其 _Prod 鏡像改為 5 世代 × 4 層級 20 欄（C–V，"
             "索引 4×(世代−1)＋層級），Perf_Batch FP8 情境欄 R／S → W／X，_Prod 檢查副本自 X 欄起；讀取這些頁的公式改用新索引（成本情境的 3×(世代−1)＋k 不動）；"
             "Unit_Cost 新增 Terra 區（無下游讀取，用途標「預備」）；輸入保存（preserve）在舊 15 欄底稿時依（世代、層級）對照欄位。"
             "不建立任何 Terra 的 IF_／L1_ 名稱；Cap_In、Price_Frontier、Fleet_1GW、Amortize、Theory_Rev、Alloc 與組合不加 Terra（B2）。"
             "Sens_Perf／Sens_Train 維持 Sol／Astra 情境（Terra 不在敏感度表，頁首註明，待 Project 判斷 R11）。"
             "DRV_*（16）與 TRN_*（15）形狀 1×15 → 1×20；其餘具名範圍值逐值不變。依據：" + DEC_BY,
             DATE, DEC_BY, "v21.11 已建",
             "builder/tiers.py；Arch F–H；Serving F21:G24；Train_In F25:G38；Har_In F47:F50；Perf／Perf_Batch／Training C–V（＋W／X）；*_Prod；Unit_Cost 第 51–61 列；Gov_Map N／D 欄",
             WO, "否"]]


def apply(wb, append_text):
    log = {"marks": purpose_marks(wb)}
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ---------------------------------------------------------------- README
_prev = v21100.README_VERSION.split("_Tokenomics_", 1)[1]
README_VERSION = (VERSION + "（結構版，底版 v21.10：" + WO + "——v21.11：GPT-6.1 Terra 第四層級的計算結構（Block 1–3）；所有既有具名範圍與契約名稱的值不變，"
                  "DRV_／TRN_ 名稱由 15 欄改 20 欄（5 世代 × 4 層級）；Arch、Serving、Train_In、Har_In 加 Terra 欄 F（設計第 3 節輸入值）；"
                  "Perf、Perf_Batch、Training 與 _Prod 鏡像改為 20 欄；Unit_Cost 加 Terra 區（預備）；Terra 尚無 IF_／L1_ 名稱（v22.0 啟用）；Decisions SL68-01。）以下為 " + _prev)
README_TITLE = V + v21100.README_TITLE[len(v21100.V):]

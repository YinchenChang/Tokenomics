# v5.23 (work order docs/workorders/20261007_v5.23.md r0): X10 Perf_Batch-side VR200 batch-basis eta_d multiplier (CAL_BatchEtaD);
# SRC_Perf note wording fix (rows 56-63, column W only); Decisions X10.
#
# X10 adds one row of five generation multipliers to Calib (section I, after the existing content; nothing moves) and multiplies
# Perf_Batch row 53 (eta_d, C:Q) by INDEX(CAL_BatchEtaD,1,gen). Perf_Batch_Prod row 53 is a mirror of Perf_Batch built by v519.x1
# from the final formulas, so it picks the factor up without a separate edit. Perf (serving side), Calib rows 67/70 and the R/S
# columns (VR200 FP8 rollout) are untouched. Every write to an Excel-owned cell is guarded (old value / presence), like v518 and v522.
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_NOTE, F_BOLD, F_CALC, F_LINK, section

VERSION = "20261007_Tokenomics_v5.23"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-07"
V = "v5.23"
COLS15 = [chr(c) for c in range(ord("C"), ord("Q") + 1)]    # Perf_Batch C:Q (5 generations x 3 tiers)

# ------------------------------------------------------------------ X10: Calib section I (five generation multipliers)
CALIB_PREV_END = 152                        # Calib ends at row 152 in v5.22; section I starts after one blank row
ROW_SEC = CALIB_PREV_END + 2
ROW_HDR, ROW_VAL = ROW_SEC + 1, ROW_SEC + 2
LAB_VAL = "批次口徑 η_d 倍數（X10；CAL_BatchEtaD）"
VR_COL = "F"                                # generation index 4 = VR200 (Calib row 66 header: C Hopper, D GB200, E GB300, F VR200, G Rubin Ultra)
K_DEFAULT = 0.75
DESC = ("Perf_Batch（高批次：RL rollout、蒸餾、合成資料、評測）專用的 η_d 倍數；服務側 Perf 不受影響。"
        "VR200＝MLPerf v6.1 Offline（1.62–1.74×）÷ 模型高批次比值（2.33×）≈ 0.70–0.75，取 0.75。"
        "1＝未另做批次口徑校準（無批次口徑實測）。")
TAG_VR = "Derived（SRC_PERF_052／053／056／057；區間 0.70–1.0）"


def calib_i(wb):
    """Five-cell generation row; only VR200 is a blue input (Derived), the other four are constant 1 (black)."""
    ws = wb["Calib"]
    assert ws.max_row == CALIB_PREV_END, f"Calib ends at row {ws.max_row}; X10 section expects it to start at row {ROW_SEC}"
    section(ws, ROW_SEC, "I. 批次口徑 η_d 倍數（X10，v5.23）：Perf_Batch 第 53 列的世代倍數（服務側 Perf 不受影響；基準 1＝不另校準）", 10)
    put(ws, f"A{ROW_HDR}", "世代", F_BOLD); put(ws, f"B{ROW_HDR}", "單位", F_BOLD)
    for i, col in enumerate("CDEFG"):
        put(ws, f"{col}{ROW_HDR}", f"=Spec_Rack!{col}4", F_LINK)
    put(ws, f"A{ROW_VAL}", LAB_VAL); put(ws, f"B{ROW_VAL}", "x")
    for col in "CDEFG":
        if col == VR_COL: put(ws, f"{col}{ROW_VAL}", K_DEFAULT, fmt="0.00")
        else: put(ws, f"{col}{ROW_VAL}", 1, F_CALC, fmt="0.00")
    put(ws, f"H{ROW_VAL}", TAG_VR, F_NOTE)
    put(ws, f"J{ROW_VAL}", DESC, F_NOTE, wrap=True)
    n = "CAL_BatchEtaD"
    if n in wb.defined_names: del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=f"Calib!$C${ROW_VAL}:$G${ROW_VAL}")


# ------------------------------------------------------------------ X10: Perf_Batch row 53, C:Q (the only existing formulas this work order changes)
ROW_ETAD = 53
SUFFIX = "*INDEX(CAL_BatchEtaD,1,{X}$6)"


def perf_batch_etad(wb):
    """Append the multiplier to the 15 base cells. Asserts the formula is still the v5.22 one (or already carries the suffix)."""
    ws = wb["Perf_Batch"]; n = 0
    for X in COLS15:
        c = ws[f"{X}{ROW_ETAD}"]; old = f"=INDEX(Calib!$C$70:$G$70,{X}$6)*{X}52*{X}50"; add = SUFFIX.format(X=X)
        if c.value == old + add: continue
        assert c.value == old, f"Perf_Batch!{X}{ROW_ETAD} is {c.value!r}, expected {old!r}"
        c.value = old + add; n += 1
    return n


# ------------------------------------------------------------------ Gov_Map row (VR200 cell only; same dict format as v522.GOV_MAP_V522)
GOV_MAP_V523 = [
    {'scope': '切片三（v5.23 X10）', 'sheet': 'Calib', 'cell': f'{VR_COL}{ROW_VAL}', 'label': LAB_VAL, 'check': LAB_VAL,
     'cls': 'Derived', 'role': '單值',
     'src': 'SRC_PERF_056',
     'rel': '換算（MLPerf v6.1 DeepSeek-R1 Offline VR200÷GB300 每 GPU：Nebius 1.62＝SRC_PERF_052÷054、NVIDIA 1.74＝SRC_PERF_056÷058；÷ 模型高批次比值 2.33＝0.70–0.75，基準取上端 0.75；'
            'Server 1.96–1.97＝SRC_PERF_053÷055、057÷059；Gov_Map SRC_ID 欄只放一個 ID，取對應基準的 056）',
     'dec': 'X10', 'lo': 0.7, 'hi': 1.0,
     'rtext': '區間 0.70–1.0（Andy 2026-10-07，X10；上端 1.0＝v5.22 現值）',
     'reason': 'X10：Perf_Batch 側 VR200 批次口徑 η_d 倍數；Server 口徑 VR200÷GB300 為 1.96–1.97（SRC_PERF_053／055、057／059）；兩提交者互為第二來源（v5.22 X9 Q2）；'
               '主要反面：VR200 軟體早期，後續 MLPerf 比值可能回升（Blackwell 前例）；Calib F67（服務側）不動',
     'retag': '', 'seg': '高'},
]

# ------------------------------------------------------------------ Decisions X10 (10 columns; same layout as v522)
DECISIONS_V523 = [
    ["X10", V, "Perf_Batch 側 VR200 批次口徑 η_d 倍數",
     f"v5.22 報告第七節第 1 項選 (b)：Perf_Batch 側另立 VR200 批次口徑 η_d 倍數 k（CAL_BatchEtaD，Calib!{VR_COL}{ROW_VAL}），基準 0.75、區間 0.70–1.0；Calib F67（服務側，與 MLPerf Interactive 相符）不動。"
     "依據：MLPerf v6.1 DeepSeek-R1 每 GPU 的 VR200÷GB300 Offline 1.62（Nebius，SRC_PERF_052／054）至 1.74（NVIDIA，056／058），Server 1.96–1.97（053／055、057／059），兩提交者互為第二來源（v5.22 X9 Q2）；"
     "模型高批次口徑（Perf_Batch 第 88 列）VR200÷GB300 為 2.35–2.56，約高出 Offline 四成，等於系統性低估 VR200 的訓練成本；k＝1.62–1.74÷2.33≈0.70–0.75，基準取上端 0.75，保留 VR200 首次提交後軟體優化的空間，區間上端 1.0＝v5.22 現值。"
     "主要反面：VR200 軟體早期，後續 MLPerf 比值可能回升（Blackwell 前例）。Perf_Batch 與 Perf_Batch_Prod 第 53 列 C:Q 乘以該倍數；R、S 欄（FP8 rollout）與 Rubin Ultra 不改",
     DATE, "「選(b)」", "v5.23 已建",
     f"Calib!C{ROW_VAL}:G{ROW_VAL}（CAL_BatchEtaD）；Perf_Batch、Perf_Batch_Prod 第 53 列 C:Q；Gov_Map X10 一列", "工作單 v5.23 第 0、1 節", "否"],
]

# ------------------------------------------------------------------ SRC_Perf note wording (column W, rows 56-63; nothing else on those rows)
OLD_PHRASE = "（第二來源欄依 W1 規則不手動填）"                                   # v5.21 leftover; removed from the Nebius rows 56-59 only (work order 2)
OLD_TAIL = " ｜第二來源：不同提交者同情境（v5.22 X9 Q2）；Nebius VR200 為 36 GPU"      # v5.22 appended sentence (same on all 8 rows)
TAIL_VR = " ｜第二來源：不同提交者同情境（v5.22 X9 Q2）；VR200 Nebius 為 36 GPU、NVIDIA 為 72 GPU，比較以每 GPU 計"
TAIL_GB = " ｜第二來源：不同提交者同情境（v5.22 X9 Q2）"
NOTE_ROWS = {56: ("SRC_PERF_052", TAIL_VR, True), 57: ("SRC_PERF_053", TAIL_VR, True), 58: ("SRC_PERF_054", TAIL_GB, True), 59: ("SRC_PERF_055", TAIL_GB, True),
             60: ("SRC_PERF_056", TAIL_VR, False), 61: ("SRC_PERF_057", TAIL_VR, False), 62: ("SRC_PERF_058", TAIL_GB, False), 63: ("SRC_PERF_059", TAIL_GB, False)}


def src_note_fix(wb):
    """Replace the old wording only while it is still present (a later Excel edit or a rebuild from v5.23 is left alone). Returns (n cells changed, log)."""
    ws = wb["SRC_Perf"]; n = 0; log = []
    for r, (sid, tail, drop_old) in NOTE_ROWS.items():
        assert ws.cell(r, 1).value == sid, f"SRC_Perf row {r} is {ws.cell(r, 1).value!r}, expected {sid}"
        c = ws.cell(r, 23); t = c.value
        if not isinstance(t, str): log.append(f"{sid}!W: not text, kept"); continue
        new = t
        if drop_old and OLD_PHRASE in new: new = new.replace(OLD_PHRASE, "")
        if new.endswith(OLD_TAIL): new = new[:-len(OLD_TAIL)] + tail
        if new != t: c.value = new; n += 1
        else: log.append(f"{sid}!W: unchanged (already v5.23 wording or edited in Excel)")
    return n, log


# ------------------------------------------------------------------ README (version string is built from VERSION; v5.22 text is kept after it)
import v522
README_VERSION = (VERSION + "（X10：Perf_Batch 側新增 VR200 批次口徑 η_d 倍數 CAL_BatchEtaD（Calib I 節，VR200 基準 0.75、區間 0.70–1.0，其餘世代 1），"
                  "Perf_Batch 與 Perf_Batch_Prod 第 53 列 C:Q 乘以該倍數（訓練相關輸出數值改變，營收與服務側 Perf 不變）；Decisions X10；SRC_Perf 第 56–63 列備註文字修正；"
                  "工作單 docs/workorders/20261007_v5.23.md）。以下為 " + v522.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v522.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v522.VERSION.split("_")[-1]):]

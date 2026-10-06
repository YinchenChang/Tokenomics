# v5.21 (work order docs/workorders/20261006_v5.21.md): X6 — X4 closed with the MLPerf Inference v6.1 primary results.
# Judgement part (X6): SRC_Perf 027／028 upgraded to grade 1 (primary, read), eight new SRC_Perf records (SRC_PERF_052–059), DB_Evidence E245
# (replaces E244), Gov_Map GM344 note, Decisions X6 and X4 status. Calib F67 and every numeric cell are untouched.
# Engineering part: Alloc_In!G7 note tail, README version string (single source: VERSION below; finish.py reads it).
# Every write is guarded by the old value / presence, like v518 and v520, so a rebuild never overwrites a later Excel edit.
import v518
import v520

VERSION = "20261006_Tokenomics_v5.21"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-06"
V = "v5.21"
EID = "E245"

# ------------------------------------------------------------------ primary source (read by CC 2026-10-06; summary.csv SHA-256 checked)
HEAD = "4bb63cd28eb136be221bc801a9e38c66c8a7553f"
SHA256 = "87980a2dfba85139ca806b63634305bcbc4ad6803bf2d520351e022ba905065a"
SRC_TEXT = (f"MLCommons inference_results_v6.1 根目錄 summary.csv（repo HEAD {HEAD}，2026-09-29；SHA-256 {SHA256}；"
            f"https://github.com/mlcommons/inference_results_v6.1/blob/{HEAD}/summary.csv；{DATE} CC 讀原文並逐列核對）")
INFERRED = "summary.csv 欄 inferred；含義未查得（repo 內 MLPerf Inference v6.1 Supplemental Discussion .pdf 未定義）"

# ------------------------------------------------------------------ SRC_Perf: 027／028 grade 2 -> 1 (old-value guards)
OLD_J = "shattered.io 轉述 NVIDIA 對照表"
OLD_M = "MLCommons 稽核；NVIDIA 對照表經 shattered.io 轉述；VR 為預覽類"
NEW_M = "MLCommons 稽核；NVIDIA 提交並挑選配置；VR 為預覽類（summary.csv Availability＝preview）"
SRC_UPD = {
    "SRC_PERF_027": f" ｜v5.21 X6：等級 2→1、二手→一手（已讀）（{EID}）；summary.csv Result＝652750.1447708113，SRC 值 652750 為取整；inferred=1（{INFERRED}）",
    "SRC_PERF_028": f" ｜v5.21 X6：等級 2→1、二手→一手（已讀）（{EID}）；summary.csv Result＝253506；inferred=1（{INFERRED}）",
}

def src_update(wb):
    """Called from gov.gov_all after v518.src_update. Returns (changed fields, log)."""
    ws = wb["SRC_Perf"]; n = 0; log = []
    for sid, note in SRC_UPD.items():
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row is None: log.append(f"{sid}: record not found"); continue
        fields = {"K": [2, 1], "N": ["二手", "一手（已讀）"], "J": [OLD_J, SRC_TEXT], "M": [OLD_M, NEW_M],
                  "Q": ["+", f"；{EID}"], "S": ["—", DATE], "W": ["+", note]}
        for col, spec in fields.items():
            if v518._apply(ws[f"{col}{row}"], spec): n += 1
            else: log.append(f"{sid}!{col}: kept (not at v5.20 value or already applied)")
    return n, log

# ------------------------------------------------------------------ SRC_Perf: eight new records (SRC_PERF_052–059)
# (submitter, system short, scenario, Result, GPUs, Availability, inferred)
_ROWS = [("Nebius", "VR200 NVL72", "offline", 558802.8, 36, "preview", 1),
         ("Nebius", "VR200 NVL72", "server", 591368.3, 36, "preview", 1),
         ("Nebius", "GB300 NVL72", "offline", 689961, 72, "available", 0),
         ("Nebius", "GB300 NVL72", "server", 603023, 72, "available", 0),
         ("NVIDIA", "VR200 NVL72", "offline", 1183326.9, 72, "preview", 1),
         ("NVIDIA", "VR200 NVL72", "server", 1175890.2, 72, "preview", 1),
         ("NVIDIA", "GB300 NVL72", "offline", 679740, 72, "available", 0),
         ("NVIDIA", "GB300 NVL72", "server", 596944, 72, "available", 0)]
_SYS = {("Nebius", "VR200 NVL72"): "Nebius VR200 NVL72", ("Nebius", "GB300 NVL72"): "Nebius GB300 NVL72",
        ("NVIDIA", "VR200 NVL72"): "NVIDIA Vera Rubin NVL72", ("NVIDIA", "GB300 NVL72"): "NVIDIA GB300 NVL72"}

def _rec(i, who, sys_, scen, val, n, avail, inf):
    pre = avail == "preview"
    pair = "NVIDIA" if who == "Nebius" else "Nebius"
    return dict(id=f"SRC_PERF_{52 + i:03d}", sheet="SRC_Perf",
                metric=f"MLPerf v6.1 DeepSeek-R1 {scen}：{sys_}（{who}）", val=val, lo=None, hi=None,
                unit=f"tok/s（{n} GPU；輸出 token）",
                basis=f"{scen}；{'預覽類（preview）' if pre else 'available'}；inferred={inf}",
                applies=f"{_SYS[(who, sys_)]}（{who} 提交；{n} GPU）", date="2026-09-29", src=SRC_TEXT, grade=1,
                stance="利害關係方", stance_note=("MLCommons 稽核為中立；提交者自行挑選配置" + ("；VR 為預覽類" if pre else "")),
                hand="一手（已讀）", status="Active", ev=EID, s="U-V521", use="—",
                note=(f"v5.21 X6 新增（純證據，不連結任何模型格）；每 GPU＝Result ÷ {n}；同硬體、同情境的另一提交者（{pair}）見 SRC_PERF_052–059 與 027／028，"
                      f"互為第二來源（第二來源欄依 W1 規則不手動填）；inferred={inf}（{INFERRED}）"))

def src_new_records():
    return [_rec(i, *r) for i, r in enumerate(_ROWS)]

# ------------------------------------------------------------------ DB_Evidence (17 columns A..Q; same layout as v518／v520)
_IDS = "；".join(["SRC_PERF_027", "SRC_PERF_028"] + [f"SRC_PERF_{52 + i:03d}" for i in range(8)])
EVIDENCE_V521 = [[
    EID, DATE,
    "MLPerf v6.1 一手結果：VR200 ÷ GB300 每 GPU，Nebius Offline 1.62×／Server 1.96×（Nebius 無 interactive）；NVIDIA Offline 1.74×／Server 1.97×／Interactive 2.575×。"
    "延遲限制越嚴，VR200 優勢越大",
    SRC_TEXT, "一手（已讀原文）", "Calib F67 η_d 倍數（GM344）",
    "1.0（區間 0.5–1.5）；模型 interactive 2.525×，MLPerf v6.1 interactive 2.575×（Calib 第 150／151 列）；E244：第三方換算 1.6–2×（情境未讀到）",
    "VR200／GB300 每 GPU：Nebius Offline 1.620×／Server 1.961×；NVIDIA Offline 1.741×／Server 1.970×／Interactive 2.575×（每 GPU＝Result ÷ GPU 數；Nebius VR200 36 GPU、GB300 72 GPU）",
    "E244 的 1.6–2× 為 Offline／Server 情境，與模型 interactive 對照（模型 2.525×、MLPerf 2.575×）不衝突；F67 不改（X6）",
    V,
    f"讀取者：CC｜讀取日 {DATE}｜工作單 v5.21 X6（Andy 2026-10-06「沒意見」）｜summary.csv SHA-256 已核對（{SHA256}）｜"
    "數字與工作單第 1 節 10 列逐列相符｜Nebius 與 NVIDIA 互為第二來源（同硬體、同情境、不同提交者）｜"
    f"VR 為 preview（預覽類）；inferred 欄含義未查得｜取代 E244（第三方換算、原文未讀）",
    "已處理", _IDS, "—", "Calib F67（數值與區間不改）；IF_／L1_ 數值不變", "1", "利害關係方"]]

def evidence_rows():
    return EVIDENCE_V521

def evidence_update(wb):
    """E244: the replacement column gets E245 (only while it is still empty). Status stays 已處理 (existing convention: replaced rows keep it)."""
    ws = wb["DB_Evidence"]; n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "E244" and ws.cell(r, 14).value in ("—", None, ""):
            ws.cell(r, 14).value = EID; n += 1
    return n

# ------------------------------------------------------------------ Gov_Map GM344 note (guarded append)
GOV_NOTES = [("GM344", f" ｜v5.21 X6：X4 結案——情境不同、非衝突（DB_Evidence {EID}；MLPerf v6.1 一手）；F67 不改")]

def gov_update(ws, append_text):
    rows = {ws[f"A{r}"].value: r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value}
    n = 0
    for gm, txt in GOV_NOTES:
        if append_text(ws[f"N{rows[gm]}"], txt): n += 1
    return n

# ------------------------------------------------------------------ Decisions
DECISIONS_V521 = [
    ["X6", V, "X4 結案：MLPerf v6.1 一手結果寫入；Calib F67 維持",
     "X4 結案：Calib F67 維持基準 1.0、區間 0.5–1.5；Nebius「1.6–2×」判定為情境不同（Offline／Server），非與 interactive 對照衝突；證據改為一手已讀並登錄"
     "（DB_Evidence E245；SRC_Perf 027／028 升為 1 級、新增 052–059）；做一次唯讀的高批次對照，只報告不改值。",
     DATE, "「沒意見」（回覆 chat 端 X4 判讀與建議）", "v5.21 已建",
     "DB_Evidence E245（取代 E244）；SRC_Perf SRC_PERF_027／028／052–059；Gov_Map GM344（N 欄）；Decisions X4", "工作單 v5.21 第 0、1、2 節", "否"]]

X4_STATUS = ("v5.20 已建", "v5.21 結案（X6）")

def decisions_update(ws):
    n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "X4" and ws.cell(r, 7).value == X4_STATUS[0]:
            ws.cell(r, 7).value = X4_STATUS[1]; n += 1
    return n

# ------------------------------------------------------------------ engineering: Alloc_In!G7 note tail (only while it still holds the v5.20 text)
G7_OLD = "8f 驅動表、A2：改版計畫計入"
G7_NEW = G7_OLD + "；區間 0–6（v5.20 X3）"

def text_update(wb):
    c = wb["Alloc_In"]["G7"]
    if c.value == G7_OLD:
        c.value = G7_NEW; return [f"Alloc_In!G7: note tail added ({V})"]
    return []

# ------------------------------------------------------------------ README (version string is built from VERSION; v5.20 text is kept after it)
README_VERSION = (VERSION + "（X6：X4 結案——MLPerf Inference v6.1 一手結果（summary.csv，repo HEAD " + HEAD[:7] + "）寫入：SRC_Perf 027／028 升為 1 級、新增 SRC_PERF_052–059，"
                  "DB_Evidence E245 取代 E244，Gov_Map GM344、Decisions X4／X6；Calib F67 與所有數值不改；Alloc_In G7 備註補區間；"
                  "工作單 docs/workorders/20261006_v5.21.md）。以下為 " + v520.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v520.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v520.VERSION.split("_")[-1]):]

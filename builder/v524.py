# v5.24 (work order docs/workorders/20261007_v5.24.md r0, engineering only): SRC_Perf rows 60-63 (SRC_PERF_056-059, NVIDIA),
# column W: remove the v5.21 leftover phrase "（第二來源欄依 W1 規則不手動填）", which contradicts the second source already filled in
# column R (v5.23 report section 8). Only that substring is removed; the rest of each note is kept as is. No value or formula changes.
# Same guarded pattern as v523.src_note_fix: the cell is changed only while the old phrase is still present (Excel first; rebuild idempotent),
# and every row's column A ID is checked first.
VERSION = "20261007_Tokenomics_v5.24"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-07"
V = "v5.24"

# ------------------------------------------------------------------ SRC_Perf note wording (column W, rows 60-63; nothing else on those rows)
OLD_PHRASE = "（第二來源欄依 W1 規則不手動填）"          # v5.21 leftover (v5.23 removed it from the Nebius rows 56-59 only)
NOTE_ROWS = {60: "SRC_PERF_056", 61: "SRC_PERF_057", 62: "SRC_PERF_058", 63: "SRC_PERF_059"}


def src_note_fix(wb):
    """Remove OLD_PHRASE only while it is still present (a later Excel edit or a rebuild from v5.24 is left alone). Returns (n cells changed, log)."""
    ws = wb["SRC_Perf"]; n = 0; log = []
    for r, sid in NOTE_ROWS.items():
        assert ws.cell(r, 1).value == sid, f"SRC_Perf row {r} is {ws.cell(r, 1).value!r}, expected {sid}"
        c = ws.cell(r, 23); t = c.value
        if not isinstance(t, str): log.append(f"{sid}!W: not text, kept"); continue
        if OLD_PHRASE in t: c.value = t.replace(OLD_PHRASE, ""); n += 1
        else: log.append(f"{sid}!W: unchanged (old phrase already removed or edited in Excel)")
    return n, log


# ------------------------------------------------------------------ README (version string is built from VERSION; v5.23 text is kept after it)
import v523
README_VERSION = (VERSION + "（SRC_Perf 第 60–63 列（SRC_PERF_056–059）W 欄刪除 v5.21 遺留句「（第二來源欄依 W1 規則不手動填）」；"
                  "數值與公式不變；工作單 docs/workorders/20261007_v5.24.md）。以下為 " + v523.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v523.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v523.VERSION.split("_")[-1]):]

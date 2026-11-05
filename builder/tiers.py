# v21.11 (v22.0 segment B1, design docs/plan/20261105_v22.0_Terra第四層級_設計.md J1／J3): single source of the model-tier list.
# Computation order Luna, Sol, Astra, Terra (Terra appended as index 4, J1 (a)); display order by price is a reading-version／site matter (B4).
#
#   TIERS      every tier the physical engine computes (Arch, Serving, Train_In, Perf, Perf_Batch, Training and their *_Prod copies, Unit_Cost blocks)
#   TIERS_LIVE the tiers whose outputs feed contract names and cross-tier aggregates. v21.11 (B1) and v21.12 (B2) keep it at 3 so every existing
#              value stays the same (Terra is computed but read by nothing that a contract name reads); v22.0 (B3) raises NT_LIVE to 4.
#   GT_COLS    generation × tier columns of Perf／Perf_Batch／Training (C..V = 5 generations × 4 tiers; index NT*(g-1)+t, J3 (a))
from openpyxl.utils import get_column_letter as L, column_index_from_string as CI

TIERS = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）"), ("Terra", "Terra（中低層）")]
TIER_KEYS = [k for k, _ in TIERS]
NT = len(TIERS)                     # 4
NG = 5                              # generations (Hopper, GB200, GB300, VR200, Rubin Ultra)
NT_LIVE = 3                         # v21.11／v21.12: 3; v22.0 B3: 4
TIERS_LIVE = TIERS[:NT_LIVE]
TC = "".join(L(3 + i) for i in range(NT))          # "CDEF": tier columns on the input sheets (Arch, Serving rows 20-24, Train_In rows 24-38, Har_In rows 47-50)
TC_LIVE = TC[:NT_LIVE]                              # "CDE"
TC_LAST = TC[-1]                                    # "F"
GT_COLS = [L(i) for i in range(3, 3 + NG * NT)]     # C..V
GT_LAST = GT_COLS[-1]                               # "V"
GT_GENS_TIERS = [(i // NT + 1, i % NT + 1) for i in range(NG * NT)]
GT_SPAN = f"$C${{r}}:${GT_LAST}${{r}}"             # format with r=row


def gt_pos(g, t):
    """1-based position of (generation g, tier t) in a generation × tier row (J3: NT*(g-1)+t)."""
    return NT * (g - 1) + t


def gt_col(g, t):
    """Column letter of (g, t) on Perf／Perf_Batch／Training."""
    return L(2 + gt_pos(g, t))


def gt_index(gexpr, texpr):
    """Excel index expression NT*(g-1)+t (texpr may be a number or a cell reference)."""
    return f"{NT}*({gexpr}-1)+{texpr}"


def gt_row(sheet, r):
    """Absolute generation × tier range of one row, e.g. Perf!$C$95:$V$95."""
    return f"{sheet}!$C${r}:${GT_LAST}${r}"


# ---- old (v21.10 and earlier) 15-column layout: C..Q = 5 generations × 3 tiers, index 3*(g-1)+t
OLD_NT = 3
OLD_LAST = "Q"


def old_to_new_col(c):
    """Column number on the v21.10 15-column layout (3..17) -> column number on the 20-column layout (J3 mapping
    3 + NT*floor((c-3)/3) + (c-3) mod 3)."""
    i = c - 3
    return 3 + NT * (i // OLD_NT) + i % OLD_NT


# Perf_Batch scenario columns (FP8 rollout on VR200, Sol and Astra): R, S on the old layout -> W, X
PB_SCEN_OLD = ["R", "S"]
PB_SCEN = [L(3 + NG * NT), L(4 + NG * NT)]          # W, X
PB_SCEN_TIERS = [2, 3]


def old_col_map(sheet):
    """{old column number: new column number} for the blue-input columns of a re-laid sheet (preserve mapping, R2)."""
    m = {c: old_to_new_col(c) for c in range(3, 18)}
    if sheet == "Perf_Batch":
        for o, n in zip(PB_SCEN_OLD, PB_SCEN):
            m[CI(o)] = CI(n)
    return m


RELAID = ("Perf", "Perf_Batch", "Training")          # generation × tier sheets re-laid to 20 columns (their *_Prod copies follow)


def old_layout(wb):
    """R13: the 15-column layout is detected from the width of DRV_Tier (Perf!$C$5:$Q$5 on v21.10 and earlier)."""
    if "DRV_Tier" not in wb.defined_names:
        return False
    return wb.defined_names["DRV_Tier"].attr_text.endswith(f"${OLD_LAST}$5")


def live_ranges(sheet, r):
    """Comma-joined ranges of the live-tier columns of one generation × tier row (one contiguous block per generation),
    e.g. Perf!C116:E116,Perf!G116:I116,… — for MAX／MIN-type checks that must keep their v21.10 value while Terra is not live."""
    out = []
    for g in range(1, NG + 1):
        a, b = gt_col(g, 1), gt_col(g, NT_LIVE)
        out.append(f"{sheet}!{a}{r}:{b}{r}")
    if NT_LIVE == NT:
        return f"{sheet}!C{r}:{GT_LAST}{r}"
    return ",".join(out)

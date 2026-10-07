# v5.26 (work order docs/workorders/20261007_v5.26.md r1, engineering only): Interface section I — DC_Cost components for
# downstream company models (CoreWeave etc.). Ten new IF_ names, each row a link to the same DC_Cost row and generation x cost
# column, written like the existing section A rows (IF_PowerCost: "=(DC_Cost!X43)/CTL_GW"; $B rows per GW, rate rows unscaled
# like IF_GPUhrEcon "=DC_Cost!X58"). Appended after the last Interface row (after section H), so no existing name moves.
# One display-only sum check row (no name): IF_DeprIT + IF_DeprFac + IF_OpexGW - IF_HoldAcct, 0 in every column.
# No input value, formula logic, SRC, Gov_Map or Decisions change.
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_NOTE, section

VERSION = "20261007_Tokenomics_v5.26"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-07"
V = "v5.26"
COLS = range(3, 18)                         # C:Q (5 generations x 3 cost cases; same columns as IF_HdrGen／IF_HdrCost)

# (name, DC_Cost column-A label used to locate the row, Interface label, unit, per GW?, number format)
ROWS = [
    ("IF_DeprLifeIT", "IT 折舊年限", "IT 折舊年限", "年", False, "0"),
    ("IF_DeprIT", "IT 折舊", "每 GW IT 折舊", "$B/年", True, "#,##0.000"),
    ("IF_DeprFac", "廠房折舊（土地不折舊）", "每 GW 廠房折舊（土地不折舊）", "$B/年", True, "#,##0.000"),
    ("IF_AvgDraw", "平均用電 ÷ 配電設計功率", "平均用電 ÷ 配電設計功率", "%", False, "0.0%"),
    ("IF_PowerPrice", "電價", "電價", "$/kWh", False, "0.000"),
    ("IF_MaintIT", "IT 維護", "每 GW IT 維護", "$B/年", True, "#,##0.000"),
    ("IF_MaintFac", "廠房維護", "每 GW 廠房維護", "$B/年", True, "#,##0.000"),
    ("IF_StaffSW", "人員、軟體、水與耗材", "每 GW 人員、軟體、水與耗材", "$B/年", True, "#,##0.000"),
    ("IF_TaxIns", "財產稅與保險", "每 GW 財產稅與保險", "$B/年", True, "#,##0.000"),
    ("IF_OpexGW", "營運費用小計（不含折舊）", "每 GW 營運費用小計（不含折舊；含電費）", "$B/年", True, "#,##0.000"),
]
EXPECTED_ROWS = {"IF_DeprLifeIT": 38, "IF_DeprIT": 39, "IF_DeprFac": 40, "IF_AvgDraw": 41, "IF_PowerPrice": 42,
                 "IF_MaintIT": 44, "IF_MaintFac": 45, "IF_StaffSW": 46, "IF_TaxIns": 47, "IF_OpexGW": 48}   # work order table
NAMES = [r[0] for r in ROWS]


def _dc_rows(wb):
    """Locate each DC_Cost row by its column-A label (the work order says the label wins over the row number)."""
    ws = wb["DC_Cost"]
    lab = {}
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if isinstance(a, str): lab.setdefault(a.strip(), r)
    out = {}
    for name, dlab, *_ in ROWS:
        assert dlab in lab, f"DC_Cost label not found: {dlab}"
        out[name] = lab[dlab]
    return out


def interface_i(wb):
    """Interface section I (after the last used row + 1 blank row). Returns dict(start, rows, made, check_row)."""
    ws = wb["Interface"]
    hold = wb.defined_names["IF_HoldAcct"].attr_text
    assert hold == "Interface!$C$12:$Q$12", hold
    dcr = _dc_rows(wb)
    start = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, start, "I. DC_Cost 構件（下游公司模型用，v5.26）：每列連結 DC_Cost 同世代 × 成本情境欄的同一列；"
                       "金額除以 CTL_GW（Inputs!E5）換算為每 GW（IT 關鍵電力），比率與年限不換算", 17)
    r = start + 1; made = []; at = {}
    for name, _dlab, lab, unit, per_gw, fmt in ROWS:
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
        for c in COLS:
            src = f"DC_Cost!{L(c)}{dcr[name]}"
            put(ws, f"{L(c)}{r}", f"=({src})/CTL_GW" if per_gw else f"={src}", fmt=fmt)
        made.append((name, f"Interface!$C${r}:$Q${r}")); at[name] = r; r += 1
    put(ws, f"A{r}", "加總核對：IF_DeprIT＋IF_DeprFac＋IF_OpexGW − IF_HoldAcct（每欄應為 0；顯示用，不設名稱）"); put(ws, f"B{r}", "$B/年")
    for c in COLS:
        X = L(c)
        put(ws, f"{X}{r}", f"={X}{at['IF_DeprIT']}+{X}{at['IF_DeprFac']}+{X}{at['IF_OpexGW']}-{X}12", fmt="0.000;-0.000;0", font=F_NOTE)
    check_row = r
    for n, ref in made:
        if n in wb.defined_names: del wb.defined_names[n]
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return dict(start=start, dc_rows=dcr, made=made, check_row=check_row)


# ------------------------------------------------------------------ README (version string is built from VERSION; v5.25 text is kept after it)
import v525
README_VERSION = (VERSION + "（Interface 新增 I 節「DC_Cost 構件」：IF_DeprLifeIT、IF_DeprIT、IF_DeprFac、IF_AvgDraw、IF_PowerPrice、IF_MaintIT、IF_MaintFac、"
                  "IF_StaffSW、IF_TaxIns、IF_OpexGW（DC_Cost 第 38–42、44–48 列，下游公司模型用）與加總核對列；數值與既有公式不變；"
                  "工作單 docs/workorders/20261007_v5.26.md）。以下為 " + v525.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v525.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v525.VERSION.split("_")[-1]):]
README_NAMES = ("Interface I 節（v5.26）", "下游名稱（IF_ 開頭且非 IF_Hdr）共 192 個（v5.25 為 182 個，v5.26 加 10 個）。I 節為 DC_Cost 構件，供下游公司模型"
                "（neocloud 每 MW 營運成本）使用：IF_DeprLifeIT（IT 折舊年限，年）、IF_DeprIT（IT 折舊）、IF_DeprFac（廠房折舊，土地不折舊）、"
                "IF_AvgDraw（平均用電 ÷ 配電設計功率，%）、IF_PowerPrice（電價，$/kWh）、IF_MaintIT（IT 維護）、IF_MaintFac（廠房維護）、"
                "IF_StaffSW（人員、軟體、水與耗材）、IF_TaxIns（財產稅與保險）、IF_OpexGW（營運費用小計，不含折舊、含電費）；金額為 $B/GW/年。"
                "IF_DeprIT＋IF_DeprFac＋IF_OpexGW＝IF_HoldAcct（I 節末列核對）。")

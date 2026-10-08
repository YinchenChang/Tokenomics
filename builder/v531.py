# v5.31 (work order docs/workorders/20261008_v5.31.md r1, B section): judgement-class input changes from the A-section evidence
# report (docs/reports/20261008_v5.31A_查證.md, PR #34; J1–J6 adopted, Andy 2026-10-08 22:31「不反對，請繼續」).
#   B1 (J1) Spec_Rack GB300 rack price low／base／high 4.0／5.0／6.5 -> 4.0／4.3／5.0 ($M):
#           E11 keeps =SRC_HW_052 (MS BOM 推算 4.0); E12 becomes the Derived constant 4.3 (= 4.0 x (1 + 7.5%), the VR200 F12 method;
#           formula-map link SRC_HW_010 dropped); E13 links SRC_HW_010 (Data Gravity 5.0, was SRC_HW_007_Hi 6.5). SRC_HW_007 -> Alt.
#   B2 (J2, J3) IT maintenance in two age segments: Inputs rows 36–38 (warranty years =SRC_DC_015, in-warranty and post-warranty
#           rates, Analogy); Inputs D30:F30 become the life-equivalent single rate (annuity-weighted with the same column's WACC
#           (row 28) and IT depreciation life (row 23)); DC_Cost row 44 is unchanged. Interface I continuation (after J, so no
#           existing name moves): IF_MaintITWarr, IF_MaintITPost, IF_WarrantyYrs.
#   B3 (J4, J5) Spec_Rack F14 note (Bernstein includes networking); IF_StaffSW label and DC_Cost row 46 label (站點營運；不含平台研發).
#   B4 (J6) SRC_DC_014 (IREN) and L1_CapexITMW_GB300_vsIREN.
#   B5 DB_Evidence E263–E278 (A-section N01–N16), Decisions X16–X20, SRC_HW_065／066, SRC_DC_014–017, SRC field updates.
# Every write to an Excel-owned cell is guarded (old value / presence), like v518–v530, so a rebuild never overwrites a later Excel edit.
from copy import copy
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_CALC, F_LINK, F_NOTE, section
import v518
import v530

VERSION = "20261008_Tokenomics_v5.31"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-08"
V = "v5.31"
DASH = "—"
COLS = range(3, 18)                         # C:Q
ANDY = "chat 端建議（A 段查證報告 PR #34 J1–J6），Andy 2026-10-08 22:31「不反對，請繼續」；可撤回"
REPORT_A = "docs/reports/20261008_v5.31A_查證.md"

# ================================================================== SRC ids (next free numbers at v5.30: SRC_HW_064, SRC_DC_013)
SID_WOLFE, SID_TF = "SRC_HW_065", "SRC_HW_066"
SID_IREN, SID_HPE, SID_SMC, SID_DGX = "SRC_DC_014", "SRC_DC_015", "SRC_DC_016", "SRC_DC_017"
# Evidence ids: A-section N01–N16 -> E263–E278 (next free number after E262)
EV = {f"N{i:02d}": f"E{262 + i}" for i in range(1, 17)}

# ================================================================== B1: Spec_Rack GB300 price
RACK_BASE = 4.3
RACK_TEXT = [  # (cell, old, new) — Spec_Rack rows 1–20 are Excel-owned (Block 1); written only while the old text is present
    ("E16", "MS 約 $4M；2026-08 採購單約 $5M；媒體 $6–6.5M（S4、S6）",
     "v5.31 J1：低 4.0＝Morgan Stanley BOM 推算（VR200 BOM 7.8 ÷ 1.95，SRC_HW_052）；基準 4.3＝BOM ×（1＋代工毛利 7.5%），與 VR200 F12 算法相同，"
     f"與 Wolfe Research 4.3（{SID_WOLFE}，Alt）相符；高 5.0＝Data Gravity 2026-08 採購單（不含 CDU，SRC_HW_010）；媒體 $6–6.5M（SRC_HW_007）改列 Alt；"
     f"公司揭露對照：IREN 每 IT MW 29.0（{SID_IREN}，L1_CapexITMW_GB300_vsIREN）"),
    ("E17", "Interested-party", "Derived／Interested-party"),
]
F14_TAIL = "；Bernstein 平均約 $9.1M 含網路約 $1.2M；本模型另計 Scale-out 網路，高情境約重複 2%（v5.31 J4）"


def formula_map(fm):
    """Builder-owned links: E12 is no longer a link (Derived constant), E13 links SRC_HW_010, Inputs E36 links the HPE warranty record."""
    fm = dict(fm)
    fm.pop("Spec_Rack!E12", None)
    fm["Spec_Rack!E13"] = "=SRC_HW_010"
    fm["Inputs!E36"] = f"={SID_HPE}"
    return fm


# ================================================================== B2: Inputs (Excel-owned Block 1 page; guarded writes)
LAB_MAINT_OLD = "IT 維護"
LAB_MAINT = "IT 維護（壽命期等值；由兩段費率計算）"
LAB_WARR = "IT 原廠保固年限"
LAB_IN = "IT 維護（保固期內）"
LAB_POST = "IT 維護（保固期滿後）"
UNIT_RATE = "% IT 資本/年"
NOTE_MAINT = ("v5.31 X17：壽命期等值單一費率＝Σ r_y ÷ (1＋WACC)^y ÷ Σ 1 ÷ (1＋WACC)^y（y＝1…IT 折舊年限；r_y＝保固期內費率（y ≤ 保固年限）或保固期滿後費率，"
              "第 36–38 列）；各欄用同欄 WACC（第 28 列）與 IT 折舊年限（第 23 列）。DC_Cost 第 44 列仍為 IT 資本 × 本列。v5.30 以前為 2%／3%／4%（v4 沿用，Analogy→Assumed）")
NOTE_WARR = (f"v5.31 X18：HPE GB300 NVL72 QuickSpecs（2026-09-08）3 年零件、3 年人工、3 年到場（{SID_HPE}）；Supermicro GPU 系統人工 3 年、零件 1 年"
             f"（{SID_SMC}；零件 1 年由保固期內高情境 1% 涵蓋）；Dell XE9680 經銷頁 3 年 ProSupport。單值（低、高＝基準）")
NOTE_IN = ("v5.31 X17：保固期內零件與人工由原廠負擔（保固費已含在機架售價），只剩備品、物流與保固外損壞；CoreWeave 2026 Q2 營運成本反推約 0–0.8%"
           f"（{EV['N14']}，Derived）；區間 0.25–1%（高端涵蓋 Supermicro 零件 1 年）")
NOTE_POST = (f"v5.31 X17：NVIDIA DGX B200 原廠支援續約 1 年 ≈ 系統價 3.8%（{SID_DGX}，英國經銷牌價）；Introl 企業 TCO 5%（Interested-party，{EV['N13']}）作高端；"
             "大型買家應低於零售牌價 → 基準 3%")
NEW_ROWS = [  # (label, unit, D, E, F, tag, note)
    (LAB_WARR, "年", "=E{r}", f"={SID_HPE}", "=E{r}", "Verified", NOTE_WARR),
    (LAB_IN, UNIT_RATE, 0.0025, 0.005, 0.01, "Analogy", NOTE_IN),
    (LAB_POST, UNIT_RATE, 0.02, 0.03, 0.05, "Analogy", NOTE_POST),
]
OLD_MAINT = {"D": 0.02, "E": 0.03, "F": 0.04}


def _row_by_label(ws, label, col=1):
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, col).value == label: return r
    return None


def _equiv(c, rw, ri, rp):
    """Life-equivalent rate for Inputs column c (D／E／F): closed form of the annuity-weighted sum (integer years)."""
    w, n, m = f"{c}28", f"{c}23", f"MIN({c}{rw},{c}23)"
    return (f"=IF({w}=0,({c}{ri}*{m}+{c}{rp}*({n}-{m}))/{n},"
            f"({c}{ri}*(1-(1+{w})^(-{m}))+{c}{rp}*((1+{w})^(-{m})-(1+{w})^(-{n})))/(1-(1+{w})^(-{n})))")


def inputs_rows(wb):
    """Rows 36–38 of Inputs (appended after the last row, created only when absent). Returns dict label -> row."""
    ws = wb["Inputs"]; out = {}; log = []
    have = {lab: _row_by_label(ws, lab) for lab, *_ in NEW_ROWS}
    if all(have.values()):
        return have, log
    assert not any(have.values()), f"Inputs: v5.31 rows partly present {have}"
    r = max(rr for rr in range(1, ws.max_row + 1) if any(ws.cell(rr, c).value is not None for c in range(1, 9))) + 1
    for lab, unit, d, e, f, tag, note in NEW_ROWS:
        put(ws, f"A{r}", lab, F_CALC); put(ws, f"B{r}", unit, copy(ws["B30"].font))
        for col, v in (("D", d), ("E", e), ("F", f)):
            v = v.format(r=r) if isinstance(v, str) else v
            font = F_IN if isinstance(v, (int, float)) else (F_LINK if "SRC_" in str(v) else F_CALC)
            put(ws, f"{col}{r}", v, font, fmt="0" if unit == "年" else "0.00%")
        put(ws, f"G{r}", tag, copy(ws["G30"].font)); put(ws, f"H{r}", note, F_CALC)
        out[lab] = r; log.append(f"Inputs!A{r}:H{r} created ({lab})"); r += 1
    return out, log


def inputs_update(wb):
    """Called after restore() and before gov_all(). Spec_Rack GB300 price and text, Inputs rows 30 and 36–38, DC_Cost row 46 label."""
    log = []
    sr = wb["Spec_Rack"]
    if sr["E12"].value == "=SRC_HW_010":
        sr["E12"].value = RACK_BASE; sr["E12"].font = copy(F_IN); sr["E12"].fill = PatternFill(fill_type=None)
        log.append(f"Spec_Rack!E12: '=SRC_HW_010' -> {RACK_BASE} (v5.31 X16)")
    for cell, old, new in RACK_TEXT:
        if sr[cell].value == old: sr[cell].value = new; log.append(f"Spec_Rack!{cell}: text updated (v5.31 X16)")
    if v518._append_text(sr["F14"], F14_TAIL): log.append("Spec_Rack!F14: note appended (v5.31 X19 J4)")
    rows, l2 = inputs_rows(wb); log += l2
    ws = wb["Inputs"]
    rw, ri, rp = rows[LAB_WARR], rows[LAB_IN], rows[LAB_POST]
    if ws["A30"].value == LAB_MAINT_OLD and all(ws[f"{c}30"].value == v for c, v in OLD_MAINT.items()):
        for c in "DEF":
            ws[f"{c}30"].value = _equiv(c, rw, ri, rp); ws[f"{c}30"].font = copy(F_CALC); ws[f"{c}30"].fill = PatternFill(fill_type=None)
        ws["A30"].value = LAB_MAINT
        log.append("Inputs!D30:F30: 2%/3%/4% -> life-equivalent formula; A30 label (v5.31 X17)")
    if ws["G30"].value == "Analogy": ws["G30"].value = "Derived"; log.append("Inputs!G30: Analogy -> Derived")
    if ws["H30"].value == "v4＝3%": ws["H30"].value = NOTE_MAINT; log.append("Inputs!H30: note (v5.31 X17)")
    dc = wb["DC_Cost"]
    if dc["A46"].value == "人員、軟體、水與耗材":
        dc["A46"].value = "人員、軟體、水與耗材（站點營運；不含平台研發）"; log.append("DC_Cost!A46: label (v5.31 X19 J5)")
    return log


# ================================================================== B2／B3: Interface I continuation (after J; nothing moves)
STAFF_TAIL = "（站點營運；不含平台研發）"


def interface_i2(wb):
    ws = wb["Interface"]
    # B3 (J5): IF_StaffSW label (row built by v526.interface_i)
    ref = wb.defined_names["IF_StaffSW"].attr_text
    rs = int(ref.split("$")[-1])
    a = ws[f"A{rs}"].value
    if STAFF_TAIL not in a:
        ws[f"A{rs}"].value = a.replace("　[IF_StaffSW]", STAFF_TAIL + "　[IF_StaffSW]")
    rin = wb["Inputs"]
    rw, ri, rp = (_row_by_label(rin, lab) for lab in (LAB_WARR, LAB_IN, LAB_POST))
    start = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, start, "I. DC_Cost 構件（續，v5.31 X17）：IT 維護兩段費率（下游公司模型依自身機隊年齡取用）；金額除以 CTL_GW 換算為每 GW；"
                       "IF_MaintIT 為壽命期等值（Inputs 第 30 列），兩段值不加總", 17)
    r = start + 1; made = []
    for name, lab, rr in (("IF_MaintITWarr", "每 GW IT 維護 — 保固期內（＝IT 資本 × 保固期內費率）", ri),
                          ("IF_MaintITPost", "每 GW IT 維護 — 保固期滿後（＝IT 資本 × 保固期滿後費率）", rp)):
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", "$B/年")
        for c in COLS:
            X = L(c); ic = "DEF"[(c - 3) % 3]
            put(ws, f"{X}{r}", f"=(DC_Cost!{X}24*Inputs!${ic}${rr})/CTL_GW", fmt="#,##0.000")
        made.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "IT 原廠保固年限（單格；保固期內費率適用的年數）　[IF_WarrantyYrs]"); put(ws, f"B{r}", "年")
    put(ws, f"C{r}", f"=Inputs!E{rw}", fmt="0")
    made.append(("IF_WarrantyYrs", f"Interface!$C${r}"))
    for n, t in made:
        if n in wb.defined_names: del wb.defined_names[n]
        wb.defined_names[n] = DefinedName(n, attr_text=t)
    return dict(start=start, made=made)


# ================================================================== B4: L1 row (appended after every existing L1 row)
def l1_rows_new():
    return [("CapexITMW_GB300_vsIREN", "每 IT MW 的 IT 資本支出（GB300）對 IREN 公司揭露",
             "基準功率情境；IT 設備（機架＋Scale-out 網路＋儲存與管理），不含廠房；$B/GW＝$M/MW",
             "=INDEX(IF_CapexIT,1,8)", "=INDEX(IF_CapexIT,1,7)", "=INDEX(IF_CapexIT,1,9)", "$M/IT MW", "成本角落情境（低成本／高成本欄）",
             "IREN 揭露含伺服器、InfiniBand、線材、軟體授權與部署服務；本模型網路另計、不含軟體與部署；比值以 ±20% 判讀",
             "機架價格、每架配電設計功率、Scale-out 網路比率", "機架價格：Derived／Interested-party（2 級）",
             SID_IREN, f"={SID_IREN}", f"={SID_IREN}", "IF_CapexIT", "Interface 第 9 列",
             "IREN 未揭露 GPU 數與每架 kW；$5.8bn 與 200 MW 的對應原文未明寫（v5.31 X20／J6）")]


# ================================================================== B5: SRC records (appended when the ID is absent)
_A = f"A 段查證（{REPORT_A}）"
SRC_NEW = [
    dict(id=SID_WOLFE, sheet="SRC_HW", metric="GB300 NVL72 機架價格（Wolfe Research）", val=4.3, lo=None, hi=None, unit="$M/架",
         basis="分析師轉述「reported prices」（口徑未明）", applies="GB300 NVL72", date="2026-01-30",
         src="Wolfe Research，經 Investing.com 於 Yahoo Finance 轉載 https://ca.finance.yahoo.com/news/wolfe-lifts-nvidia-target-25-145211458.html",
         grade=2, stance="利害關係方", stance_note="賣方研究引述「reported」，底層出處不明", hand="二手", status="Alt", ev=EV["N02"], s="U-V531",
         use="Spec_Rack!E12 佐證（不直接連結）",
         note=f"v5.31 新增（{EV['N02']}，部分採用）：GB300 4.3 作基準 4.3 的佐證（同來源 GB200 約 3、Rubin $5–6M 早於記憶體漲價，不採用）；{_A}"),
    dict(id=SID_TF, sheet="SRC_HW", metric="Vera Rubin 對 GB300 系統 ASP 比值（TrendForce）", val=2, lo=None, hi=None, unit="x",
         basis="比值（系統 ASP）", applies="VR200 NVL72 ÷ GB300 NVL72", date="2026-08-28",
         src="TrendForce 新聞稿 https://www.trendforce.com/presscenter/news/20260828-13204.html（科技新報轉載）",
         grade=1, stance="中立", stance_note="市調機構", hand="一手（已讀）", status="Active", ev=EV["N06"], s="U-V531",
         use="（比值對照；不連結模型格）",
         note=f"v5.31 新增（{EV['N06']}，部分採用）：「roughly double」；模型 VR200 ÷ GB300 基準 8.4 ÷ 4.3＝1.95；{_A}"),
    dict(id=SID_IREN, sheet="SRC_DC", metric="每 IT MW 的 GPU 與附屬設備資本支出（IREN 公司揭露）", val=29.0, lo=None, hi=None, unit="$M/IT MW",
         basis="公司揭露：向 Dell 採購 GB300 設備 $5.8bn（含伺服器、InfiniBand、線材、軟體授權、部署服務）÷ 200 MW 關鍵 IT",
         applies="GB300 NVL72（IREN／Microsoft 合約）", date="2025-11-03",
         src="IREN 新聞稿 https://iren.gcs-web.com/news-releases/news-release-details/iren-secures-97bn-ai-cloud-contract-microsoft（另 irisenergy.gcs-web.com、DCD 轉載）",
         grade=1, stance="利害關係方", stance_note="買方公司揭露（合約宣傳）", hand="一手（已讀）", status="Active", ev=EV["N04"], s="U-V531",
         use="L1!M／N（L1_CapexITMW_GB300_vsIREN 外部欄）｜直接",
         note=f"v5.31 新增（{EV['N04']}，採用）：總額與 MW 為 Verified，每 MW 為 Derived（$5.8bn ÷ 200）；GPU 數未揭露，$5.8bn 與 200 MW 的對應原文未明寫；{_A}"),
    dict(id=SID_HPE, sheet="SRC_DC", metric="GPU 機架原廠標準保固年限（HPE GB300 NVL72）", val=3, lo=None, hi=None, unit="年",
         basis="原廠標準保固：3 年零件、3 年人工、3 年到場（含在售價）", applies="GB300 NVL72（HPE）", date="2026-09-08",
         src="HPE QuickSpecs「NVIDIA GB300 NVL72 by HPE」V3 https://www.hpe.com/us/en/collaterals/collateral.a50009244enw.html",
         grade=1, stance="利害關係方", stance_note="賣方條款", hand="一手（已讀）", status="Active", ev=EV["N10"], s="U-V531",
         use="Inputs!E36｜直接",
         note=f"v5.31 新增（{EV['N10']}，採用）：保固年限依據；Dell XE9680 經銷頁 3 年 ProSupport 併入本筆備註，不另登錄；第二來源 {SID_SMC}（人工 3 年同值，零件 1 年不同）；{_A}"),
    dict(id=SID_SMC, sheet="SRC_DC", metric="GPU 系統原廠標準保固年限（Supermicro，人工）", val=3, lo=None, hi=None, unit="年",
         basis="原廠通則（發票無特約時）：人工 3 年（本筆值）、零件 1 年、預先換貨 1 年", applies="Supermicro GPU 系統", date="2026-10-08",
         src="Supermicro 保固頁 https://www.supermicro.com/en/support/warranty（讀取日 2026-10-08）",
         grade=1, stance="利害關係方", stance_note="賣方條款", hand="一手（已讀）", status="Active", ev=EV["N11"], s="U-V531",
         use=f"（{SID_HPE} 的第二來源；Inputs 第 37 列高情境依據，不直接連結）",
         note=f"v5.31 新增（{EV['N11']}，採用）：零件 1 年由保固期內高情境 1% 涵蓋；{_A}"),
    dict(id=SID_DGX, sheet="SRC_DC", metric="GPU 系統原廠支援續約年費 ÷ 系統價（NVIDIA DGX B200）", val=0.038, lo=None, hi=None, unit="% 系統價/年",
         basis="英國經銷牌價：1 年續約 £18,599.99 ÷ 系統（含 3 年 Business Standard 支援）£489,999（皆含 VAT）", applies="DGX B200 8 GPU", date="2026-10-08",
         src="Scan UK https://www.scan.co.uk/products/dgx-b200-8x-180gb-full-with-business-std-support-3y；https://www.scan.co.uk/products/dgx-b200-8x-180gb-full-business-std-support-renew-1-year",
         grade=2, stance="利害關係方", stance_note="經銷商牌價（零售）", hand="二手（經銷頁已讀）", status="Active", ev=EV["N12"], s="U-V531",
         use="（Inputs 第 38 列保固期滿後費率的可比對象；不直接連結）",
         note=f"v5.31 新增（{EV['N12']}，採用）：續約為支援、韌體、軟體授權；大型買家應低於牌價 → 基準 3%、上緣參考；{_A}"),
]


def src_new_records():
    return SRC_NEW


SRC_UPD = {  # sid -> (sheet, {col: spec}); spec = (old, new) or ("+", text) — v518._apply
    "SRC_HW_052": ("SRC_HW", {"I": (DASH, "2026-05-21"),
                              "J": ("分析師報價（模型頁說明文字引用，未登錄 Sources）",
                                    "Morgan Stanley「Nvidia NVL72 Bill of Materials」表，經 wccftech https://wccftech.com/nvidia-vera-rubin-rack-hit-with-memory-price-surge-pushing-hbm4-lpddr5x-bill-to-2m-of-7-8m-total/amp/"),
                              "K": (3, 2), "G": ("分析師估計", "分析師估計（成本 BOM 推算）"), "Q": ("+", f"；{EV['N03']}"), "S": (DASH, DATE),
                              "V": ("Spec_Rack!E11｜直接", "Spec_Rack!E11｜直接；Spec_Rack!E12｜換算（× 1.075）"),
                              "W": ("+", f" ｜v5.31 X16（{EV['N03']}）：4.0＝VR200 BOM 7.8（SRC_HW_015）÷ 1.95（MS 表「total cost difference of 95%」；圖片替代文字已讀，GB300 總額未讀到文字）；"
                                         "等級 3→2；Spec_Rack E12 基準 4.3＝本筆 ×（1＋代工毛利 7.5%）")}),
    "SRC_HW_010": ("SRC_HW", {"J": ("+", "；原文 https://www.datagravity.dev/p/how-much-does-an-nvidia-nvl72-cost（2026-08-31，v5.31 A 段已讀）"),
                              "Q": ("+", f"；{EV['N01']}"), "S": ("2026-10-05", DATE),
                              "V": ("Spec_Rack!E12｜直接", "Spec_Rack!E13｜直接"),
                              "W": ("+", f" ｜v5.31 X16（{EV['N01']}）：原文已讀（略低於 $5.0M、不含 250 kW CDU 約 $32K、部署合計約 $5.7M）；由基準改作高情境依據（Spec_Rack E13）")}),
    "SRC_HW_007": ("SRC_HW", {"O": ("Active", "Alt"), "Q": ("+", f"；{EV['N07']}"),
                              "V": ("Spec_Rack!E13｜直接", "—（v5.31 起不連結；高情境改連 SRC_HW_010）"),
                              "W": ("+", f" ｜v5.31 X16（{EV['N07']}，待查）：J1 (a) 採用後不再是高情境，改列 Alt（底層出處不明、本輪未讀原文）")}),
    "SRC_HW_017": ("SRC_HW", {"K": (3, 2), "G": ("分析師估計", "分析師估計（平均成本；含網路約 $1.2M）"), "Q": ("+", f"；{EV['N05']}"), "S": (DASH, DATE),
                              "J": ("+", "；Bernstein 原文轉載：https://wccftech.com/bernstein-warns-nvidias-vera-rubin-racks-will-hit-9-1-million-as-hbm4-prices-triple-to-53-per-gigabyte/amp/、https://news.cnyes.com/news/id/6498402（同一底層來源）"),
                              "W": ("+", f" ｜v5.31 X19（{EV['N05']}）：等級 3→2；拆項 GPU 系統約 4.0、HBM 與儲存約 3.2、網路約 1.2、散熱與電力各約 0.15；"
                                         "含網路，與 Spec_Rack 第 14 列口徑不同，高情境 F13 9.1 與模型另加的 Scale-out 網路約重複 2%（J4，數值不改）")}),
}


def src_update(wb):
    n = 0; log = []
    for sid, (sh, fields) in SRC_UPD.items():
        ws = wb[sh]
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row is None: log.append(f"{sid}: record not found"); continue
        for col, spec in fields.items():
            if v518._apply(ws[f"{col}{row}"], spec): n += 1
            else: log.append(f"{sid}!{col}: kept (not at v5.30 value or already applied)")
    # second sources (R) of the two warranty records: written only while R is empty
    ws = wb["SRC_DC"]
    for sid, other in ((SID_HPE, SID_SMC), (SID_SMC, SID_HPE)):
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row and ws[f"R{row}"].value in (None, "", DASH): ws[f"R{row}"].value = other; n += 1
    return n, log


# ================================================================== B5: Gov_Map (judgement updates, guarded; new rows via gov.gm_append_c)
def _gm_text_maint():
    return ("v5.31 X17：壽命期等值單一費率（公式）＝保固期內費率（第 37 列）與保固期滿後費率（第 38 列）以同欄 WACC、IT 折舊年限年金加權；"
            "保固年限第 36 列（SRC_DC_015）")


GM_UPD = [  # (sheet, cell, {col: (old, new) or ("+", text)})
    ("Inputs", "E30", {"E": ("IT 維護", LAB_MAINT), "F": ("Assumed", "Derived（公式）"), "J": (DASH, "X17"),
                       "N": ("v4＝3% ｜補充旗標（IF 全欄分段，非分段依據）：中", _gm_text_maint() + " ｜補充旗標（IF 全欄分段，非分段依據）：中"),
                       "O": ("+", "；v5.31 X17：Assumed→Derived（公式）")}),
    ("Inputs", "D30", {"E": ("IT 維護", LAB_MAINT), "F": ("Assumed", "Derived（公式）"), "J": (DASH, "X17"),
                       "N": ("v4＝3% ｜補充旗標（IF 全欄分段，非分段依據）：中", _gm_text_maint() + "（低成本欄） ｜補充旗標（IF 全欄分段，非分段依據）：中"),
                       "O": ("+", "；v5.31 X17：Assumed→Derived（公式）")}),
    ("Inputs", "F30", {"E": ("IT 維護", LAB_MAINT), "F": ("Assumed", "Derived（公式）"), "J": (DASH, "X17"),
                       "N": ("v4＝3% ｜補充旗標（IF 全欄分段，非分段依據）：中", _gm_text_maint() + "（高成本欄） ｜補充旗標（IF 全欄分段，非分段依據）：中"),
                       "O": ("+", "；v5.31 X17：Assumed→Derived（公式）")}),
    ("Spec_Rack", "E12", {"F": ("原始數據", "Derived"), "G": ("單值", "基準"), "H": ("SRC_HW_010", "SRC_HW_052"),
                          "I": ("直接", "Derived：MS BOM 推算 4.0 ×（1＋代工毛利 7.5%，Assumed）＝4.3；Wolfe 4.3（SRC_HW_065，Alt）相符"),
                          "J": (DASH, "X16"), "K": (None, "=Spec_Rack!E11"), "L": (None, "=Spec_Rack!E13"),
                          "N": ("連結 SRC（G1）", "v5.31 X16（J1 (a)）：基準 4.3＝4.0 × (1＋7.5%)，與 VR200 F12 算法相同；4.0 為 Morgan Stanley 成本（BOM）推算，不是售價；低 4.0、高 5.0（Data Gravity 採購單）"),
                          "O": (DASH, "原始數據→Derived（v5.31 X16）")}),
    ("Spec_Rack", "E13", {"H": ("SRC_HW_007", "SRC_HW_010"), "J": (DASH, "X16"),
                          "N": ("+", " ｜v5.31 X16：高情境改連 SRC_HW_010（Data Gravity 2026-08 採購單 5.0，原文已讀）；SRC_HW_007（媒體 6.0–6.5）改列 Alt")}),
    ("Spec_Rack", "E11", {"J": (DASH, "X16"), "N": ("+", " ｜v5.31 X16：SRC_HW_052 等級 3→2（MS BOM 表推算，換算式見該筆備註）")}),
]


def gov_update(ws, append_text):
    loc = {(ws[f"C{r}"].value, ws[f"D{r}"].value): r for r in range(5, ws.max_row + 1) if ws[f"C{r}"].value}
    n = 0
    for sh, cell, cols in GM_UPD:
        r = loc.get((sh, cell))
        assert r is not None, f"Gov_Map: {sh}!{cell} not registered"
        for col, spec in cols.items():
            c = ws[f"{col}{r}"]
            if isinstance(spec, tuple) and spec[0] == "+":
                if append_text(c, spec[1]): n += 1
            elif c.value == spec[0]:
                c.value = spec[1]; n += 1
                if isinstance(spec[1], str) and spec[1].startswith("="): c.font = copy(F_LINK)
    return n


def gov_map_rows(wb):
    """Gov_Map rows for the new Inputs cells (dict format of v529.gov_map_rows; appended by gov.gm_append_c when absent)."""
    ws = wb["Inputs"]
    rw, ri, rp = (_row_by_label(ws, lab) for lab in (LAB_WARR, LAB_IN, LAB_POST))
    sc = "切片一（v5.31 X17／X18）"
    out = [{'scope': sc, 'sheet': 'Inputs', 'cell': f'E{rw}', 'label': LAB_WARR, 'check': LAB_WARR, 'cls': '原始數據', 'role': '單值', 'src': SID_HPE,
            'rel': '直接', 'dec': 'X18', 'lo': None, 'hi': None, 'rtext': '單值（低、高欄＝基準）', 'reason': '連結 SRC（G1）；' + NOTE_WARR, 'retag': '', 'seg': '低'}]
    for r, lab, sid, rel, lo, hi, reason in (
            (ri, LAB_IN, SID_HPE, "類比：保固期內零件與人工由原廠負擔（HPE 3 年）；CoreWeave Q2 反推約 0–0.8%（" + EV["N14"] + "）", "0.25%", "1%", NOTE_IN),
            (rp, LAB_POST, SID_DGX, "類比：NVIDIA DGX B200 續約 ≈ 3.8%／年（零售牌價）；Introl 5%（" + EV["N13"] + "）", "2%", "5%", NOTE_POST)):
        out.append({'scope': sc, 'sheet': 'Inputs', 'cell': f'E{r}', 'label': lab, 'check': lab, 'cls': 'Analogy', 'role': '基準', 'src': sid, 'rel': rel,
                    'dec': 'X17', 'lo': f'=Inputs!$D${r}', 'hi': f'=Inputs!$F${r}', 'rtext': f'{lo}–{hi}（A 段建議，{ANDY}）',
                    'reason': reason, 'retag': '', 'seg': '低'})
        for col, role in (("D", "低"), ("F", "高")):
            out.append({'scope': sc, 'sheet': 'Inputs', 'cell': f'{col}{r}', 'label': lab, 'check': lab, 'cls': 'Analogy', 'role': role, 'src': sid, 'rel': rel,
                        'dec': 'X17', 'lo': None, 'hi': None, 'rtext': f'E{r} 的{role}端點', 'reason': reason, 'retag': '', 'seg': '低'})
    return out


# ================================================================== B5: DB_Evidence E263–E278 (17 columns A..Q; layout of v529)
def _ev(n, claim, src, tag, param, cur, new, verdict, note, sids, affected, grade, stance):
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, f"{note}｜A 段暫編 {n}｜{ANDY}｜讀取者：CC（A 段，{REPORT_A}）",
            "已處理", sids, DASH, affected, grade, stance]


GB300 = "IF_CapexIT、IF_HoldAcct、IF_HoldEcon、IF_GPUhrEcon（GB300）"
MAINT = "IF_MaintIT、IF_HoldAcct、IF_HoldEcon、IF_GPUhrEcon（全世代）；IF_MaintITWarr、IF_MaintITPost"
EVIDENCE_V531 = [
    _ev("N01", "Data Gravity 原文：GB300 NVL72 採購單略低於 $5.0M（不含 250 kW CDU 約 $32K）、部署合計約 $5.7M（不含 DC 建造、叢集核心交換、儲存）",
        "https://www.datagravity.dev/p/how-much-does-an-nvidia-nvl72-cost（2026-08-31；wing.vc 為同文轉載）", "Interested-party／2 級",
        "Spec_Rack E12（基準）→ E13（高）", "5.0（基準）", "略低於 5.0", "採用（X16）：SRC_HW_010 補「原文已讀」，改作高情境依據（E13＝5.0）",
        "未具名交易方", "SRC_HW_010", GB300, "2", "利害關係方"),
    _ev("N02", "Wolfe Research（reported prices）：GB300 約 $4.3M、GB200 約 $3M、Rubin $5–6M",
        "https://ca.finance.yahoo.com/news/wolfe-lifts-nvidia-target-25-145211458.html（Investing.com 轉載，2026-01-30）", "Interested-party／2 級",
        "Spec_Rack E12", "5.0", "4.3", f"部分採用（X16）：GB300 4.3 作基準佐證，新登錄 {SID_WOLFE}（Alt）；Rubin 5–6 早於記憶體漲價，不採用",
        "自稱 reported，底層出處不明；gpuperhour 彙整頁引同一筆，不另算", SID_WOLFE, GB300, "2", "利害關係方"),
    _ev("N03", "Morgan Stanley NVL72 BOM 表推算 GB300 ≈ $4.0M（＝VR200 BOM 7.8 ÷ 1.95；表載記憶體 $373,939 → $2,001,600、total cost difference of 95%）",
        "https://wccftech.com/nvidia-vera-rubin-rack-hit-with-memory-price-surge-pushing-hbm4-lpddr5x-bill-to-2m-of-7-8m-total/amp/（2026-05-21）", "Derived（中立賣方研究）／2 級",
        "Spec_Rack E11、E12", "4.0（低）", "4.0", "採用（X16）：SRC_HW_052 等級 3→2，換算式寫入備註；E12 基準＝4.0 × 1.075",
        "表為圖片，GB300 總額未讀到文字", "SRC_HW_052；SRC_HW_015", GB300, "2", "中立"),
    _ev("N04", "IREN 向 Dell 採購 GB300 設備 $5.8bn（含伺服器、InfiniBand、線材、軟體授權、部署服務），對應 200 MW 關鍵 IT → 每 IT MW $29.0M",
        "https://iren.gcs-web.com/news-releases/news-release-details/iren-secures-97bn-ai-cloud-contract-microsoft（2025-11-03；DCD 轉載）", "Verified／Derived／1 級",
        "L1 新對照列（IF_CapexIT）", DASH, "29.0 $M/IT MW", f"採用（X20）：新登錄 {SID_IREN}；L1_CapexITMW_GB300_vsIREN 外部對照，不直接進模型",
        "GPU 數未揭露；以 136 kW／架推算每架（含網路）≈ $4.3M", SID_IREN, "L1_CapexITMW_GB300_vsIREN（新列）", "1", "利害關係方"),
    _ev("N05", "Bernstein：VR200 平均成本 $9.1M（GPU 系統約 4.0、HBM 與儲存約 3.2、網路約 1.2、散熱約 0.15、電力約 0.15）；1 GW 約 $47bn",
        "https://wccftech.com/bernstein-warns-nvidias-vera-rubin-racks-will-hit-9-1-million-as-hbm4-prices-triple-to-53-per-gigabyte/amp/；https://news.cnyes.com/news/id/6498402（同一底層來源，2026-06）",
        "Interested-party（中立賣方研究）／2 級", "Spec_Rack F13", "9.1", "9.1（含網路）", "採用（X19）：SRC_HW_017 等級 3→2；口徑欄註明含網路；Spec_Rack F14 補註（數值不改，J4）",
        "高情境與模型另加的 Scale-out 網路約重複 2%", "SRC_HW_017", "IF_CapexIT（VR200 高成本欄；數值不變）", "2", "中立"),
    _ev("N06", "TrendForce：Vera Rubin 系統 ASP 約為 GB300 的 2 倍", "https://www.trendforce.com/presscenter/news/20260828-13204.html（2026-08-28）",
        "Interested-party（市調，中立）／1 級", "Spec_Rack E12／F12 比值檢查", "1.68（8.4 ÷ 5.0）", "約 2（改後 8.4 ÷ 4.3＝1.95）",
        f"部分採用（X16）：新登錄 {SID_TF}（比值，不進數值）", "比值對照", SID_TF, DASH, "1", "中立"),
    _ev("N07", "Tom's Hardware：GB300 NVL72 $6.0–6.5M（媒體報價）", "Tom's Hardware（經 Yahoo Finance，2026-03；本輪未讀原文）", "Interested-party／3 級",
        "Spec_Rack E13（高）", "6.5（高）", "6.0–6.5", "待查（X16）：J1 (a) 採用後不再是高情境，SRC_HW_007 改列 Alt",
        "底層出處不明", "SRC_HW_007", GB300, "3", "利害關係方"),
    _ev("N08", "FT：Oracle 約 $40bn 購買約 40 萬顆 GB200 → $50K–100K／顆", "https://www.datacenterdynamics.com/en/news/oracle-to-spend-40bn-on-nvidia-chips-for-openai-texas-data-center/（2025-05）",
        "Interested-party／2 級", DASH, DASH, "$50K–100K／顆", "不採用：「GB200」指 GPU 或 superchip 不明", "匿名消息", DASH, DASH, "2", "利害關係方"),
    _ev("N09", "CoreWeave 1H26 每新增 MW 資本支出 24.8 $M（16.139bn ÷ 650 MW）；技術設備毛額 19.9", "CRWV 10-Q 2026-06-30 附註 5（CoreWeave W5 報告已讀，A 段未重讀）",
        "Derived／2 級", "IF_CapexIT 對照", "34.8（CRWV 機隊組合）", "24.8／19.9", "部分採用：登錄為已看過；active power 的 IT／設施口徑未明，不作對照列",
        "19.9 若為 IT 口徑等於每架 GB300 約 $2.7M，低於所有價格證據 → 口徑問題可能性較大", DASH, "IF_CapexIT（對照）", "2", "利害關係方"),
    _ev("N10", "HPE GB300 NVL72 標準保固：3 年零件、3 年人工、3 年到場", "https://www.hpe.com/us/en/collaterals/collateral.a50009244enw.html（QuickSpecs V3，2026-09-08）",
        "Verified（賣方條款）／1 級", "Inputs 第 36 列（新）", "3%（第 1 年起固定）", "保固 3 年", f"採用（X18）：新登錄 {SID_HPE}，Inputs E36 連結",
        "Dell XE9680 經銷頁 3 年 ProSupport（https://www.servermonkey.com/poweredge-xe9680-ss-1.html）併入本筆", SID_HPE, MAINT, "1", "利害關係方"),
    _ev("N11", "Supermicro GPU 系統標準保固：人工 3 年、零件 1 年、預先換貨 1 年", "https://www.supermicro.com/en/support/warranty（讀取日 2026-10-08）",
        "Verified（賣方條款）／1 級", "Inputs 第 37 列（高情境）", "3%", "人工 3／零件 1", f"採用（X18）：新登錄 {SID_SMC}（{SID_HPE} 的第二來源）",
        "零件 1 年由保固期內高情境 1% 涵蓋", SID_SMC, MAINT, "1", "利害關係方"),
    _ev("N12", "NVIDIA DGX B200 原廠支援續約 1 年 £18,599.99 ÷ 系統（含 3 年支援）£489,999 ≈ 每年 3.8%",
        "https://www.scan.co.uk/products/dgx-b200-8x-180gb-full-with-business-std-support-3y；…-renew-1-year（讀取日 2026-10-08）", "Analogy／Derived／2 級",
        "Inputs 第 38 列（保固期滿後）", "3%", "3.8%", f"採用（X17）：新登錄 {SID_DGX}；保固期滿後基準 3%、上緣參考",
        "續約為支援、韌體、軟體授權；零售牌價", SID_DGX, MAINT, "2", "利害關係方"),
    _ev("N13", "Introl 企業 GPU 叢集 TCO：維護每年 5% 硬體價值；文中另稱原廠支援合約「typically cost 8-12%」",
        "https://introl.com/blog/gpu-infrastructure-tco-model-5-year-enterprise-ai-deployment（2026-04-28）", "Interested-party（基礎設施服務商）／2 級",
        "Inputs 第 38 列高情境", "4%（高）", "5%；8–12%", "部分採用（X17）：5% 作保固期滿後高情境；8–12% 不採用（企業小規模、與自身模型矛盾）",
        "兩數自相矛盾", DASH, MAINT, "2", "利害關係方"),
    _ev("N14", "CoreWeave 2026 Q2 營運成本反推維護 ≈ 0–0.25 $M/MW·年（約 IT 資本 0–0.8%；機隊多在保固期內）",
        "CRWV 10-Q 2026-06-30；CoreWeave W5 報告 coreweave/docs/reports/20261008_coreweave_v4.7_公司實況驗證.md", "Derived／2 級",
        "Inputs 第 37 列（保固期內）", "3%", "0–0.8%", "採用（X17）：保固期內低值依據；不單獨定值（含爬坡期用電偏低）",
        "營運成本 1.357 − 研發 0.374 − 電費 0.673 − 人員軟體 0.325 − 稅險 0.156 ≤ 0", DASH, MAINT, "2", "利害關係方"),
    _ev("N15", "超大型資料中心常駐人員 0.2–0.5 人／MW", "https://www.irecruit.co/insights/data-center-staffing-ratios-people-per-mw-2026（2026-04-24，引 poweredbywho.com）",
        "Interested-party（人力仲介）／3 級", "Inputs E32（人員）", "500 FTE／GW", "200–500 FTE／GW", "不採用：二手、出處不全；僅確認模型在上緣",
        "數值不改", DASH, "IF_StaffSW", "3", "利害關係方"),
    _ev("N16", "NVIDIA AI Enterprise 牌價 $4,500／GPU／年（CSP 市集 $1／GPU·時）", "https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/pricing.html",
        "Verified（賣方牌價）／1 級", "Inputs E33（軟體授權與連線）", "$200M／GW（≈ $410／GPU·年）", "$4,500／GPU·年", "待查：neocloud 裸機出租是否付此授權找不到",
        "IF_StaffSW 範圍為站點營運、不含平台研發（X19 J5 標籤）", DASH, "IF_StaffSW", "1", "利害關係方"),
]


def evidence_rows():
    return EVIDENCE_V531


# ================================================================== B5: Decisions X16–X20 (10 columns; layout of v530)
_X = [
    ("X16", "J1 GB300 機架價格", "Spec_Rack GB300 機架價格 低／基準／高 4.0／5.0／6.5 → 4.0／4.3／5.0 $M：低＝SRC_HW_052（MS BOM 推算，等級 3→2）；"
     "基準＝4.0 ×（1＋代工毛利 7.5%）＝4.3（Derived 常數，與 VR200 F12 算法相同；Wolfe 4.3 相符）；高＝SRC_HW_010（Data Gravity 採購單 5.0）；SRC_HW_007（媒體 6.0–6.5）改 Alt；"
     "價格涵蓋範圍（第 14 列）維持「同上」", "Spec_Rack E11:E13、E16、E17；SRC_HW_007／010／052／065／066；Gov_Map E11／E12／E13", "B1"),
    ("X17", "J2 IT 維護機齡兩段＋壽命期等值費率", "Inputs 新增「IT 維護（保固期內）」0.25%／0.5%／1.0% 與「IT 維護（保固期滿後）」2%／3%／5%（Analogy）；Inputs 第 30 列改為公式："
     "等值費率＝[Σ r_y ÷ (1＋WACC)^y] ÷ [Σ 1 ÷ (1＋WACC)^y]（y＝1…IT 折舊年限，各欄用同欄 WACC 與年限），標記 Derived；DC_Cost 第 44 列公式不變；"
     "Interface I 節（續）新增 IF_MaintITWarr、IF_MaintITPost（下游依機隊年齡取用）", "Inputs D30:H30、第 37–38 列；Interface I 節（續）；Gov_Map", "B2"),
    ("X18", "J3 IT 原廠保固 3 年", "Inputs 新增「IT 原廠保固年限」＝SRC_DC_015（HPE GB300 NVL72 QuickSpecs：3 年零件、人工、到場）；Supermicro 人工 3、零件 1 年（SRC_DC_016）由保固期內高情境 1% 涵蓋；"
     "Interface 單格名稱 IF_WarrantyYrs", "Inputs 第 36 列；SRC_DC_015／016；IF_WarrantyYrs", "B2"),
    ("X19", "J4／J5 口徑註記", "J4：Spec_Rack F14 補「Bernstein 平均約 $9.1M 含網路約 $1.2M；本模型另計 Scale-out 網路，高情境約重複 2%」，VR200 數值不改；SRC_HW_017 等級 3→2。"
     "J5：IF_StaffSW 的 Interface 標籤與 DC_Cost 第 46 列標籤補「（站點營運；不含平台研發）」，數值不改", "Spec_Rack F14；SRC_HW_017；Interface IF_StaffSW 列 A 欄；DC_Cost A46", "B3"),
    ("X20", "J6 IREN 外部對照", "新增 SRC_DC_014（IREN 2025-11-03：向 Dell 採購 GB300 設備 $5.8bn，含 InfiniBand、軟體、部署，對應 200 MW 關鍵 IT → 29.0 $M/IT MW）與 "
     "L1_CapexITMW_GB300_vsIREN（模型 GB300 IF_CapexIT 對 IREN 的比值與判讀）；CoreWeave 24.8 口徑不明，不加對照列", "SRC_DC_014；L1 新列", "B4"),
]
DECISIONS_V531 = [[i, V, f"{i} {t}", txt, DATE, ANDY, "v5.31 已建", where, f"工作單 v5.31 r1 {sec}", "否"] for i, t, txt, where, sec in _X]


# ================================================================== README (version string is built from VERSION; v5.30 text is kept after it)
README_VERSION = (VERSION + "（判斷類，工作單 docs/workorders/20261008_v5.31.md r1；A 段查證 PR #34：J1 GB300 機架價格 4.0／5.0／6.5 → 4.0／4.3／5.0 $M；"
                  "J2／J3 IT 維護改為機齡兩段（保固 3 年，保固期內 0.25／0.5／1.0%、期滿後 2／3／5%），Inputs 第 30 列改為壽命期等值費率公式（WACC、IT 折舊年限年金加權），"
                  "Interface I 節（續）新增 IF_MaintITWarr、IF_MaintITPost、IF_WarrantyYrs；J4／J5 註記；J6 SRC_DC_014（IREN 29.0 $M/IT MW）與 L1_CapexITMW_GB300_vsIREN；"
                  "DB_Evidence E263–E278；Decisions X16–X20）。以下為 " + v530.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v530.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v530.VERSION.split("_")[-1]):]
README_ROW = ("Interface I 節（續）與 IT 維護兩段（v5.31）",
              "下游名稱（IF_ 開頭且非 IF_Hdr）共 195 個（v5.30 為 192 個，v5.31 加 3）。IT 維護（v5.31 X17／X18）：保固期內費率（Inputs 第 37 列）適用於前 IF_WarrantyYrs 年"
              "（Inputs 第 36 列＝SRC_DC_015，3 年），之後為保固期滿後費率（第 38 列）；IF_MaintIT（DC_Cost 第 44 列）用 Inputs 第 30 列的壽命期等值單一費率"
              "（以同欄 WACC 與 IT 折舊年限年金加權），所以 Tokenomics 的穩態持有成本不隨機齡變動。下游公司模型依自身機隊年齡取 IF_MaintITWarr（＝IT 資本 × 保固期內費率）"
              "或 IF_MaintITPost（＝IT 資本 × 期滿後費率），兩者不加總；金額為 $B/GW/年。IF_StaffSW 為站點營運（人員、軟體授權與連線、水與耗材），不含平台研發，"
              "下游另列。L1_CapexITMW_GB300_vsIREN：GB300 IF_CapexIT（$M/IT MW）對 IREN 公司揭露 29.0（SRC_DC_014）。")

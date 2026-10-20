# Usage: python3 build.py <base.xlsx> <out.xlsx>
#   chat:  python3 build.py /mnt/project/<latest>.xlsx /home/claude/b2/<new>.xlsx   (or base downloaded from the repo)
#   repo:  python3 builder/build.py model/<current>.xlsx <new>.xlsx
import sys, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if len(sys.argv) != 3:
    sys.exit("usage: build.py <base.xlsx> <out.xlsx>")
BASE, out = sys.argv[1], sys.argv[2]
OUTDIR = os.path.dirname(os.path.abspath(out))
from inputs import spec_rack, arch, serving, energy_inputs
from calib import calib
from outputs import perf_sheet, sens_sheet, unit_cost, workload, nonnv
from finish import interface, checks, sources, readme, interface_b3, checks_b3, write_checks_b3
from training import tech_registry, train_in, perf_batch, training_sheet, sens_train
from finish import evidence_sheet
from preserve import snapshot, restore
from v519 import PROD_SHEETS

wb = openpyxl.load_workbook(BASE)
# ---- v5.12 (A): the pre-Source register is frozen as Sources_Legacy (no formula or name refers to it) ----
if "Sources" in wb.sheetnames and "Sources_Legacy" not in wb.sheetnames:
    wb["Sources"].title = "Sources_Legacy"
    wb["Sources_Legacy"]["A1"].value = ("Sources_Legacy — v5.11 以前的來源清單（v5.12 起凍結，只供追溯原 S 編號；"
                                        "新來源一律先登錄 DB_Evidence，擇優寫入 SRC_*）")
# ---- v5.7 Excel-first: snapshot every input cell (blue font) before the rebuild ----
SNAP = snapshot(wb)
# ---- v5.12 (A): inputs that moved to another row keep their Excel value (restore stays unmatched 0) ----
from training import SNAP_MOVES
for _old, _new in SNAP_MOVES:
    if _old in SNAP and _new not in SNAP: SNAP[_new] = SNAP.pop(_old)
# ---- v5.13 (D): input cells retired because the cell is now a formula (Arch KV rows 21–23, Cap_In N column). Their Excel
#      values are logged, not restored; the new formulas reproduce them with the default inputs (verified by recalculation).
from block4 import PRICE_ROWS
SNAP_RETIRED = [("Arch", (lab, 0), c) for lab in ("KV bytes/token — 情境 1", "KV bytes/token — 情境 2", "KV bytes/token — 情境 3")
                for c in (3, 4, 5)] + [("Cap_In", (row[0], 0), 14) for row in PRICE_ROWS]
import v535
SNAP_RETIRED += v535.SNAP_RETIRED       # v5.35 B2: Cap_In H10 mid-tier price index row (four blue 1s) is now a link to I-section L_price
import v1020
import v1030
SNAP_RETIRED += v1030.SNAP_RETIRED       # v10.3 D08: Sens_Rev B20／B21 (blue 6／24) are now links to Cap_In D23／D24
SNAP_RETIRED += v1020.SNAP_RETIRED       # v10.2 E3: Calib F120 (MLPerf v6.0 GB300 server reference, a blue literal 8,064) is now a link to SRC_PERF_076
import v536
for _old, _new in v536.SNAP_MOVES:      # v5.36 B2: the Alloc_In pricing-multiple label was renamed; the Excel values follow it
    if _old in SNAP and _new not in SNAP: SNAP[_new] = SNAP.pop(_old)
import v601
for _old, _new in v601.SNAP_MOVES:      # v6.1 D13: the Alloc_In pure-utilisation label was renamed; the Excel values follow it
    if _old in SNAP and _new not in SNAP: SNAP[_new] = SNAP.pop(_old)
import v1520
for _old, _new in v1520.SNAP_MOVES:      # v15.2 B2: Cap_In A280 label renamed (days-on-sale -> volume weighted); the Excel values follow it back to the builder's label
    if _old in SNAP and _new not in SNAP: SNAP[_new] = SNAP.pop(_old)
import v1530
for _old, _new in v1530.SNAP_MOVES:      # v15.3 r1: Cap_In A226/A228 marks relabelled (Assumed -> Derived); the Excel values follow the label back to the builder's key
    if _old in SNAP and _new not in SNAP: SNAP[_new] = SNAP.pop(_old)
RETIRED = {k: SNAP.pop(k) for k in SNAP_RETIRED if k in SNAP}
# ---- strip Block 2/3 content to recover the Block 1 base, then rebuild deterministically ----
for n in ["Arch","Serving","Workload","Calib","Perf","Sens_Perf","Unit_Cost","Energy","NonNV",
          "Tech_Registry","Train_In","Perf_Batch","Training","Sens_Train",
          "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
          "Har_In","Harness","Sens_Har","Alloc_In","Alloc",
          *PROD_SHEETS]:
    if n in wb.sheetnames: del wb[n]
def clear(ws, r0, c1=1, c2=30):
    for r in range(r0, ws.max_row + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.value = None; cell.fill = openpyxl.styles.PatternFill(fill_type=None)
clear(wb["Spec_Rack"], 21); 
for r in range(1, 21): wb["Spec_Rack"].cell(row=r, column=8).value = None
clear(wb["Interface"], 17); clear(wb["Checks"], 12); clear(wb["Sources_Legacy"], 23); clear(wb["README"], 4, 1, 2)
for n in list(wb.defined_names.keys()):
    if n not in ("CTL_GW","CTL_PowerCase","IF_CapexFacility","IF_CapexIT","IF_CapexTotal","IF_FacilityGW",
                 "IF_GPUhrEcon","IF_GPUsPerGW","IF_HoldAcct","IF_HoldEcon","IF_PowerCost","IF_RacksPerGW"):
        del wb.defined_names[n]
SP = spec_rack(wb)
import v602
V602_SC = v602.spec_rack_scale(wb, SP)       # v6.2 D1(c): Spec_Rack model-scale section (ARCH_ScaleGen／_Lo／_Hi)
V1030_SR = v1030.spec_rack_ru(wb, V602_SC)       # v10.3 F1: Spec_Rack Rubin Ultra price multipliers SR_RU_PxMultLo／Hi (G11／G13 read them after restore)
AR = arch(wb)
serving(wb)
CAL = calib(wb, SP, AR)
import v523
v523.calib_i(wb)       # v5.23 X10: Calib I section, CAL_BatchEtaD (after the existing content, nothing moves)
CAL["J"] = v1020.calib_j(wb, CAL, SP)       # v10.2 E1／E3: Calib J section (calibration copy rows and aligned conditions; below section I, nothing moves)
CAL["K"] = v1030.calib_k(wb)       # v10.3 F1: Calib K section (L1_JudgeTol; below J, nothing moves)
import v1100
CAL["L"] = v1100.calib_l(wb, CAL, SP)       # v11.0 G2／G3: Calib J C／D η_d carries CAL_BatchEtaD; Calib L section (V20–V22 batch-path validation points; below K, nothing moves)
import v1200
CAL["M"] = v1200.calib_m(wb)       # v12.0 H1: Calib M section (CHK_SoftCapFail, blue input; below L, nothing moves)
energy_inputs(wb)
TR = tech_registry(wb)
TI = train_in(wb)
PR = perf_sheet(wb, SP, AR, CAL, TR)
SR = sens_sheet(wb, SP, AR, CAL, TR)
PB = perf_batch(wb, SP, AR, CAL, TR, TI)
v523.perf_batch_etad(wb)      # v5.23 X10: Perf_Batch row 53 C:Q x INDEX(CAL_BatchEtaD,1,gen) (before v519.x1 mirrors the chain)
TRN = training_sheet(wb, SP, AR, TI, PB, TR)
STR = sens_train(wb, SP, AR, TI, PB, TR)
U = unit_cost(wb, PR)
WL = workload(wb, U)
nonnv(wb)
interface(wb, PR, U)
def last_row(ws):
    return max(c.row for row in ws.iter_rows() for c in row if c.value is not None)
ifr = last_row(wb["Interface"]) + 2
interface_b3(wb, TRN, ifr, TI)
checks(wb, CAL, PR, SR, U)
_r, _rows = checks_b3(wb, TRN, TI, CAL, PB)
write_checks_b3(wb, _r, _rows, SP)
# ---- v5.8: Block 4 ----
from block4 import cap_in, price_frontier, capability, cache_store, fleet, amortize, theory_rev, sens_rev, interface_b4, checks_b4, sources_b4, evidence_b4
K4 = cap_in(wb)
import v522
v522.cap_in_g(wb)      # v5.22 X7: CTL_PriceLife／CTL_Monetize (Cap_In G section, after the existing content)
import v532
v536.patch_specs()      # v5.36 B1／B4: Cap_In H7 row 109 (÷ SpendBasis × κ), H10 rows 216 (2025 = SRC_DEM_004) and 218 (× κ) patched in place before they are written
v601.patch_specs()      # v6.1 D13-2: Cap_In rows 114 (H7 corr_pt), 218 (H10 q_gw) and 255 (J j_ident) read (AL_UtilActual*CTL_ProdDerate) — patched in place after v536 and before any of them is written
import v603
v603.patch_specs()      # v6.3 K1: Cap_In H7 / H10 m_fleet read the fleet-basis price (patched in place after v601, before they are written)
import v800
v800.patch_specs()      # v8.0 L1／L4: the same rows read the 2025 fleet-basis price AL_PriceFleet25; Cap_In I-7 required L reads L1_FleetBreakeven2025 (patched after v603, before they are written)
import v810
v810.patch_specs()      # v9.0 M6: demand-route m (H5／H8) on the 2025 price CAP_Price25Mix; Cap_In I-7 required L (m = L1_MAPI) on L1_FleetBreakeven2025 (patched after v800, before they are written)
import v1410
v1410.patch_specs()      # v14.1 R1: Cap_In row 119 (m_fleet) = MAX(point estimate, same-column floor row 121) (patched after v810, before H7 is written)
V532_CAP = v532.cap_in_h(wb)      # v5.32 B2: Cap_In H section「m 追蹤」(after G; no defined name, nothing moves)
import v533
V533_CAP = v533.cap_in_h7(wb, V532_CAP)      # v5.33 B3: Cap_In H7「機隊口徑」(before the H reading row, which is rewritten after it; no defined name moves)
import v534
v535.patch_h10()      # v5.35 B1 (J23): H10 spec patched in place before it is written (ads per column, revenue rows on the m numerator, 0.65 share row, L_price link row)
V534_CAP = v534.cap_in_h8_h10(wb, V532_CAP, V533_CAP)      # v5.34 B2／B3／B5: Cap_In H8–H10 (before the H reading row, which is rewritten after them; B4_Disc_Lo／_Hi names added; no defined name moves)
V535_CAP = v535.cap_in_i(wb, V534_CAP)      # v5.35 B2 (J22): Cap_In I section「L 拆分」(before the H reading row, which is rewritten after it; no defined name moves)
V536_CAP = v536.cap_in_j(wb, V535_CAP)      # v5.36 B4／B5／B6: Cap_In J section (kappa, tau closed form, gap identity, rho inputs; before the reading row, which is rewritten after it)
V603_K = v603.cap_in_k(wb, V536_CAP)      # v6.3 K1: Cap_In K section (fleet-basis price for H10; below the reading row, nothing above moves)
import v700
V700_L = v700.cap_in_l(wb, V603_K)      # v7.0 B-1: Cap_In L section (CAP_GenGap_*; below K, nothing above moves)
V1030_CAP = v1030.cap_in_patch(wb)      # v10.3 D09: Cap_In H10 2025 column C reads the H-section cells (patched after every Cap_In section is built, before contract tracing)
V800_M = v800.cap_in_m(wb, V700_L)      # v8.0 L1／L4／D14: Cap_In M section (2025 annual tier prices, m／required-L comparisons, Astra Epoch implied tokens; below L, nothing above moves)
import v1600
V1600_N = v1600.cap_in_n(wb, V800_M)      # v16.0 W1: Cap_In N section (L from each generation's own start; below M, nothing above moves)
import v1700
V1700_O = v1700.cap_in_o(wb, V1600_N)      # v17.0 W1: Cap_In O section (discounted generation-start fleet L; below N, nothing above moves)
P4 = price_frontier(wb, K4, TR)
C4 = capability(wb, K4, P4, TRN, TI)
S4 = cache_store(wb)
F4 = fleet(wb, K4)
A4 = amortize(wb, F4, P4, S4)
T4 = theory_rev(wb, F4, A4, S4, WL)
v522.theory_rev_life(wb)      # v5.22 X7: Theory_Rev D section (base row x L x m) and self-check rows
K4["_capf"] = P4["capf"]
sens_rev(wb, K4, T4, A4)
interface_b4(wb, last_row(wb["Interface"]) + 2, P4, S4, A4, T4)
checks_b4(wb, P4, F4, A4, T4, U)
# ---- v5.9: Block 5 (harness); v5.10: M1 (b) reliability floor + Interface E additions (inside block5.py) ----
from block5 import har_in, harness, sens_har, interface_b5, checks_b5, sources_b5, evidence_b5
H5 = har_in(wb, TR)
R5 = harness(wb, U, S4, WL)
SH5 = sens_har(wb, U, S4, WL, H5, R5)
interface_b5(wb, last_row(wb["Interface"]) + 2, R5)
checks_b5(wb, R5, H5, SH5)
# ---- v5.15: Block 6 (Alloc_In inputs, Alloc derivation, Interface F) ----
from block6 import alloc_in, alloc, interface_b6, checks_h
AIN = alloc_in(wb)
import v529
AIN_529 = v529.alloc_in_rows(wb)       # v5.29 X14 (m): two Assumed inputs and the v5.28 constant (appended after the existing content; restored by preserve)
AIN_536 = v536.alloc_in_kappa(wb)       # v5.36 B4: Alloc_In request-shape correction κ (AL_Kappa／_Lo／_Hi; appended after the existing content)
AIN_800 = v800.alloc_in_rd_mix(wb)       # v8.0 L3: Alloc_In 2025 R&D generation mix (AL_RDMix*; appended after the existing content)
AL6 = alloc(wb, AIN)
import v600
v600.alloc_prod_ratio(wb, AL6, F4)       # v6.0 D7-2: Alloc H section (paid-capacity ratio at the production derate; Cap_In row 115 reads AL_ProdRatioPaid)
v603.alloc_fleet_price(wb, AL6)       # v6.3 K1: Alloc I section (AL_PriceGen／AL_PriceFleet; appended after H)
v800.alloc_sections(wb, AL6)       # v8.0: Alloc J (R&D mix), K (2025 price and fleet breakeven), L (token-route comparison) sections (appended after I)
V800_LOG = v800.alloc_patch(wb, AL6)       # v8.0 L3: Alloc rows 46／49／52 read the J section
interface_b6(wb, last_row(wb["Interface"]) + 2)
sources(wb)
sources_b4(wb)
sources_b5(wb)
readme(wb)
# ---- v5.7: write back Excel-owned inputs, then the evidence register (created only if absent) ----
_m, _c, _d = restore(wb, SNAP, os.path.join(OUTDIR, "restore_log.txt"))
print(f"restore: matched {_m}, Excel kept over code {_c}, unmatched {len(_d)}")
import v518
V518_LOG = v518.inputs_update(wb)       # v5.18: Excel-owned input writes, each only while the cell still holds its v5.17 value
print("v518 inputs:", len(V518_LOG))
import v520
V518_LOG += v520.inputs_update(wb)       # v5.20 X3: Alloc_In!E7 4 -> 6 (old-value guard)
import v521
V518_LOG += v521.text_update(wb)         # v5.21: Alloc_In!G7 note tail (old-text guard)
V518_LOG += v529.inputs_update(wb)       # v5.29 X14 (l): Alloc_In 每則提示 token 數 2000/1000/6000 -> 4000/2000/6400 (old-value guards) and the G note
import v531
V518_LOG += v531.inputs_update(wb)       # v5.31 X16–X19: Spec_Rack E12 4.3 and text, Inputs rows 30／36–38, DC_Cost A46 label (old-value guards)
V518_LOG += v533.inputs_update(wb)       # v5.33 J8／J9: Alloc_In C9 0 -> 0.6, C11 0.4 -> 0, C12 0.2 -> 0, E15 6400 -> 11000 (old-value guards) and G notes
V518_LOG += v534.inputs_update(wb)       # v5.34 J20: Cap_In E12 0.3 -> 0.4 (old-value guard)
V518_LOG += v536.inputs_update(wb)       # v5.36 B2: Alloc_In pricing multiple 2 -> 1.3 (1.5–3.0 -> 1.0–1.6) (old-value guards)
V518_LOG += v601.inputs_update(wb)       # v6.1 3B: D3 Alloc_In D9:E12, D10 C23:E23, D13-1 C24:E24, D6 Calib C67, Q3 Har_In C61:D61 (old-value guards)
_t601, _ = v601.text_update(wb)
V518_LOG += _t601       # v6.1 3B: notes and markers (old-text guards), Serving notes appended once
V518_LOG += v601.decisions_update(wb)
V518_LOG += v602.decisions_update(wb)       # v6.2: AF1-D8 status (TTFT part superseded)
V518_LOG += v603.inputs_update(wb)       # v6.3 J1 r1: Spec_Rack ARCH_ScaleGen_Lo／_Hi (old-value guards)
V518_LOG += v603.decisions_update(wb)       # v6.3: AF2-D1c r1 note
V518_LOG += v1030.inputs_update(wb)       # v10.3 F1: Spec_Rack G11／G13 read SR_RU_PxMultLo／Hi (old-formula guards), G14 note
V518_LOG += v1100.inputs_update(wb)       # v11.0 G2: Calib D156 (CAL_BatchEtaD GB200) 1 -> 3.04 (old-value guard)
V518_LOG += v1200.inputs_update(wb)       # v12.0 H2: Calib D156 3.04 -> 2.36 (old-value guard)
import v1530
V518_LOG += v1530.inputs_update(wb, v518._append_text)       # v15.3: E1／E2 Cap_In C226:E228 (inputs, D228 formula, marks), D1 rows 242／243, C2 Calib D156 = SQRT(C254*D201) (before gov_all so the contract tracing sees the final formulas)
V518_LOG += v1600.inputs_update(wb, v518._append_text)       # v16.0 W2: Cap_In row 242 reads L1_LTotalFleetV (after v1530 wrote the v15.3 text; before gov_all)
V518_LOG += v1700.inputs_update(wb, v518._append_text)       # v17.0 W2: Cap_In row 242 reads L1_LTotalFleetVDisc / L1_LReqFleet_IdNoK (after v1600; before gov_all)
evidence_sheet(wb)
print("evidence rows added:", evidence_b4(wb), evidence_b5(wb))
order = ["README","Inputs","Spec_Rack","Arch","Serving","Workload","Calib","Tech_Registry","Perf","Sens_Perf","Unit_Cost","DC_Cost",
         "Train_In","Perf_Batch","Training","Sens_Train",
         "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
         "Har_In","Harness","Sens_Har","Interface","Energy","NonNV","Sensitivity","Checks","Sources_Legacy","DB_Evidence"]
wb._sheets = [wb[n] for n in order] + [s for s in wb._sheets if s.title not in order]   # v5.11: keep Excel-owned governance sheets
# ---- v5.3: Block 1 Checks — reference cells instead of literals (CC 第 1 輪第 6 節第 5 項) ----
from common import put, F_IN
ck = wb["Checks"]
# v5.11: C4–C8 now link to SRC (gov.checks_block1); C9–C10 (SRC_Price) remain literals until slice two (v5.12)
for r, v in [(9, 10.5), (10, 3.57)]:
    put(ck, f"C{r}", v, F_IN, fmt="#,##0.00")
ck["E7"].value = '=IF(B7>C7,"高於參照（參照假設未知）","低於參照")'
ck["E8"].value = '=IF(B8>C8,"高於參照（參照假設未知）","低於參照")'
ck["E9"].value = '="牌價 ÷ 持有成本＝"&TEXT(C9/B9,"0.0")&" 倍"'
ck["E10"].value = '="參照 ÷ 本模型＝"&TEXT(C10/B10,"0.00")'
# ---- v5.3: display-only named ranges (DRV_／CAL_／IF_Hdr；CC 第 1 輪第 6 節第 2、3 項) ----
from openpyxl.workbook.defined_name import DefinedName
def nm(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
nm("IF_HdrGen", "Interface!$C$4:$Q$4"); nm("IF_HdrCost", "Interface!$C$5:$Q$5")
nm("DRV_Gen", "Perf!$C$4:$Q$4"); nm("DRV_Tier", "Perf!$C$5:$Q$5")
for n, k in [("DRV_FlopDec","Fd"),("DRV_FlopPre","Fp"),("DRV_WeightGB","W"),("DRV_TfixMs","tfix"),("DRV_SeqMs","ceff"),
             ("DRV_SeqBind","cbind"),("DRV_Batch","B"),("DRV_Bind","bind"),("DRV_DecTokGPU","D"),("DRV_PreTokGPU","Pp"),
             ("DRV_PreShare","psh"),("DRV_RackTok","rtot"),("DRV_GWTok","gwtot"),("DRV_Close","close")]:
    nm(n, f"Perf!$C${PR[k]}:$Q${PR[k]}")
nm("CAL_EtaD", f"Calib!$C${CAL['etad_fit']}"); nm("CAL_TlayerUs", f"Calib!$C${CAL['tl_fit']}")
nm("CAL_F_Label", f"Calib!$C${CAL['lab']}:$I${CAL['lab']}")
for n, k in [("CAL_F_Gen","gn"),("CAL_F_Eng","eng"),("CAL_F_Speed","s"),("CAL_F_Meas","T"),("CAL_F_Model","vT"),("CAL_F_Basis","basis")]:
    nm(n, f"Calib!$C${CAL[k]}:$I${CAL[k]}")
for n, k in [("CAL_H_Gen","mgn"),("CAL_H_Speed","ms"),("CAL_H_Meas","mT"),("CAL_H_Model","mO"),("CAL_H_Basis","mbasis")]:
    nm(n, f"Calib!$C${CAL[k]}:$F${CAL[k]}"); nm("CAL_F_Platform", f"Calib!$C${CAL['indep']}:$I${CAL['indep']}")
nm("CAL_F_Ratio", f"Calib!$C${CAL['ratio']}:$I${CAL['ratio']}")
nm("CAL_H_Label", f"Calib!$C${CAL['mhdr']}:$F${CAL['mhdr']}"); nm("CAL_H_Platform", f"Calib!$C${CAL['mplat']}:$F${CAL['mplat']}")
nm("CAL_H_Ratio", f"Calib!$C${CAL['mR']}:$F${CAL['mR']}")
# ---- v5.5: Block 3 display-only named ranges (TRN_；網站推導鏈用，下游不得連結) ----
for n, k in [("TRN_FlopTokPre","Fpt"),("TRN_FlopPre","Cp"),("TRN_GPUhPre","Hp"),("TRN_GPUhRL","Hrl"),("TRN_RLMFU","rlmfu"),
             ("TRN_RLRatioH","rlH"),("TRN_RLRatioF","rlF"),("TRN_GPUhFinal","Hfin"),("TRN_PostShareF","psF"),("TRN_PostShareH","psH"),
             ("TRN_InferShare","Ish"),("TRN_GPUhProg","Hprog"),("TRN_GWyrProg","GWp")]:
    nm(n, f"Training!$C${TRN[k]}:$Q${TRN[k]}")
nm("TRN_Gen", "Training!$C$4:$Q$4"); nm("TRN_Tier", "Training!$C$5:$Q$5")
# ---- v5.6: Tech_Registry display-only named ranges (TR_；網站唯讀表用，下游不得連結) ----
r0, r1 = TR["_rows"]; h0, h1 = TR["_hooks"]
for n, c in [("TR_ID","A"),("TR_Tech","B"),("TR_Hook","C"),("TR_Acts","D"),("TR_Lo","E"),("TR_Base","F"),("TR_Hi","G"),
             ("TR_Sel","H"),("TR_Status","I"),("TR_Labs","J"),("TR_Main","K"),("TR_Override","L"),("TR_InBase","M"),
             ("TR_Adopt","N"),("TR_Switch","O"),("TR_Eff","P"),("TR_Tag","Q"),("TR_Source","R"),("TR_Trigger","S"),("TR_Check","T")]:
    nm(n, f"Tech_Registry!${c}${r0}:${c}${r1}")
nm("TR_HookCode", f"Tech_Registry!$A${h0}:$A${h1}"); nm("TR_HookName", f"Tech_Registry!$B${h0}:$B${h1}")
nm("TR_HookVal", f"Tech_Registry!$E${h0}:$E${h1}")
# ---- v5.11: Stage 1 slice one (Source layer, Evidence upgrade, Decisions, Gov_Map, L1, governance Checks, F14); v5.13: slice two ----
from gov import gov_all
GOV = gov_all(wb)
v1600.late_names(wb)      # v16.0: L1_LTotalV is the four-cell Cap_In row; drop the stray _Lo／_Hi names of that L1 row
checks_h(wb)        # v5.15: Checks H section (after the G section; counted in GOV_Errors)
V532_L1P = v532.l1_judge(wb)      # v5.32 B3: L1_MImplied／_Ext judgement column (inside／outside the CTL_Monetize Gov_Map range)
V533_L1P = v533.l1_judge(wb)      # v5.33 B4: L1_MFleet (range) and L1_TokCeiling (demand ÷ ceiling) judgement columns
V534_L1P = v534.l1_judge(wb)      # v5.34 B4: L1_MAPI／MSub／MSeat (range) and L1_MixFactorAPI (ratio to the agent extreme) judgement columns
V535_L1P = v535.l1_judge(wb)      # v5.35 B4: L1_LTotal (CTL_PriceLife range) and L1_LReqFleet (L_total ≥ required L) judgement columns
import v519
X1 = v519.x1(wb)    # v5.19 X1: *_Prod mirror sheets, Interface G, Checks I1 (after gov_all: reads the final formulas of the chain)
print("x1 chain cells:", X1['cells'], "sheets:", X1['sheets'])
X7 = v522.interface_h(wb)      # v5.22 X7: Interface H section (after G; IF_*_Life names)
X7["check_row"] = v522.checks_y(wb)
print("x7 interface rows from:", X7["start"], "check row:", X7["check_row"])
import v526
X26 = v526.interface_i(wb)     # v5.26: Interface I section (after H; DC_Cost components IF_DeprLifeIT … IF_OpexGW, sum check row)
print("v526 interface I from:", X26["start"], "dc rows:", X26["dc_rows"], "check row:", X26["check_row"])
# ---- v5.29: Gov_Map helper columns, Interface J (waterfall), Interface R–U (contract; static precedent tracing), Load_Bearing, Checks K ----
from deps import Deps, gov_map_cells
N_GMH = v529.gov_map_helpers(wb)
import v530
IFJ = v530.interface_j(wb, v600.prod_override(wb, F4))            # v5.30 X15 (a): running-product waterfall; v6.0 D7: _Prod token／Front rows read the re-solved SLO source
v600.patch_j_header(wb, IFJ)
v600.life_alias(wb, IFJ)               # v6.0 D7-3: IF_*_Life／Theory_Rev D section become aliases of IFW_*_Life
ID_ROWS = v600.prod_identity(wb, IFJ)    # v6.0 D7-1: _Prod revenue / _Prod token = tier price (flags on Theory_Rev; Checks Z1 is written after Checks M so no Checks row moves)
I2 = v531.interface_i2(wb)            # v5.31 X17／X18: Interface I continuation after J (IF_MaintITWarr, IF_MaintITPost, IF_WarrantyYrs); IF_StaffSW label (X19)
IFK = v800.interface_k(wb)            # v8.0 L5: Interface K section (IF_AllocServeGW_Tok; appended last, before the contract columns are built)
import v1000
IFL = v1000.interface_l(wb)            # v10.0 N1: Interface L section (IFW_*_LifeSelf; appended last, before the contract columns are built; nothing reads these names)
import v1400
IFM = v1400.interface_m(wb)            # v14.0 (4-3B Q2): Interface M section (11 IF_ names) before the contract columns are built
SER14 = v1400.series_names(wb)         # v14.0 (4-3B Q2): L1_*_Ser／L1_MFleet_P25Lo／Hi series names on Cap_In
print("v531 interface I2 from:", I2["start"], "names:", [n for n, _ in I2["made"]])
DEPS = Deps(wb); GMC = gov_map_cells(wb)                 # built after every formula sheet exists (J rows included; R–U formulas are not precedents)
IFC = v529.interface_contract(wb, DEPS, GMC, v530.should_cap)      # v5.30 X15 (c): "上限" flag extended to IFW_ revenue rows and IFW_TokGW_*_100
LB = v529.load_bearing(wb, DEPS, GMC)
CK_K = v530.checks_k(wb, IFC, IFJ, LB)    # v5.29 Checks K with the v5.30 K2／K3 wording
CK_M = v532.checks_m(wb)                  # v5.32 B3 (J4 (a)): Checks M1, WARN (after K; counted in GOV_Warnings)
CK_M23 = v533.checks_m23(wb)              # v5.33 B4: Checks M2／M3, WARN (after M1; counted in GOV_Warnings)
CK_M4 = v534.checks_m4(wb)                # v5.34 B3: Checks M4, WARN (after M3; counted in GOV_Warnings)
CK_M5 = v536.checks_m5(wb)                # v5.36 B5: Checks M5, INFO (gap identity check; after M4; counted in GOV_Info)
V536_L1P = v536.l1_judge(wb)              # v5.36 B6: L1_PriceReqBE judgement column
V810_L1P = v810.l1_judge(wb)              # v9.0 M5: L1_LReqFleet judgement column (identity reading as the main reading, literal reading beside it)
V1000_L1P = v1000.l1_judge(wb)              # v10.0 N4-8: payback reading uses the identity reading only (literal reading beside it, marked inconsistent)
V1000_NAT = v1000.l1_nature(wb)           # v10.0 N2: L1 column T (nature) and U (reason) for every row
print("v1000 L1 nature counts:", V1000_NAT)
Z1 = v600.checks_z(wb, ID_ROWS)                # v6.0 D7-1: Checks Z1 (ERROR, counted in GOV_Errors; after M)
print("v600 Checks Z1 row:", Z1)
Z2 = v800.checks_z2(wb)                # v8.0 L3: Checks Z2 (ERROR, counted in GOV_Errors; research mix sums to 100%)
print("v800 Checks Z2 row:", Z2)
V518_LOG += v603.unavail_text(wb)       # v6.3 K2: Cap_In H7 onward and L1 fallbacks read AL_UnavailTxt (整代不可達 propagates)
V518_LOG += v700.interface_a231(wb, IFJ["start"])       # v7.0 2-2-b: Interface A231 title text
print("v700 Checks K4 row:", v700.checks_k4(wb))       # v7.0 2-2-b: Checks K4 reads the re-solved fleet revenue
V518_LOG += v700.text_update(wb, v518._append_text)       # v7.0: Serving F18, Calib J68, Cap_In g note, DB_Evidence E338/E339/E341 notes
V518_LOG += v800.text_update(wb, v518._append_text) + V800_LOG       # v8.0: Cap_In K section 2025 price link and labels; Alloc rows 46／49／52
V518_LOG += v1000.text_update(wb, v518._append_text)       # v10.0 N2／N4: nature tags (Alloc, Interface, Train_In H34), kappa／free-share notes, literal payback reading, Interface identity row
CK_V = v1000.checks_v(wb, CAL)           # v10.0 N3: Checks G column (nature) and V section (CHK_VerifyTotal／Pass／Fail; not counted in GOV_Errors)
print("v1000 Interface L from:", IFL["start"], "names:", len(IFL["made"]), "| Checks V rows:", CK_V["first"], "-", CK_V["last"], "| nature:", CK_V["nature"])
V518_LOG += v602.notes_patch(wb, v518._append_text)       # v6.2 D1(c): fixed-model-basis note on Interface B／C／D headers and L1 TokMW_Gen_ratio rows
print("v536 Cap_In J from:", V536_CAP["start"], "to:", V536_CAP["end"], "| Alloc_In kappa row:", AIN_536, "| L1 PriceReqBE row:", V536_L1P, "| Checks M5 row:", CK_M5)
print("v535 Cap_In I from:", V535_CAP["start"], "to:", V535_CAP["end"], "| L1 rows:", V535_L1P, "| H10 L_price link row:", v534.ROWS["q_idx"], "| Gov_Map updated (incl. v5.35 re-pointing):", GOV.get("gm_updated"))
print("v534 Cap_In H8–H10 from:", V534_CAP["start"], "to:", V534_CAP["end"], "| L1 rows:", V534_L1P, "| Checks M4 row:", CK_M4)
print("v533 Cap_In H7 from:", V533_CAP["start"], "to:", V533_CAP["end"], "| L1 rows:", V533_L1P, "| Checks M2/M3 rows:", CK_M23)
print("v532 Cap_In H from:", V532_CAP["start"], "to:", V532_CAP["end"], "| L1 rows:", V532_L1P, "| Checks M1 row:", CK_M)
print("v529 interface J from:", IFJ["start"], "names:", len(IFJ["made"]), "flags:", IFJ["flags"], "| contract rows:", len(IFC["rows"]), "no-dep rows:", IFC["no_dep"],
      "| Load_Bearing rows:", LB["rows"], "| Gov_Map helper rows:", N_GMH, "| Checks K rows:", CK_K)
GOV["snap_retired"] = len(RETIRED)
GOV["v529"] = dict(contract_rows=len(IFC["rows"]), contract_no_dep=IFC["no_dep"], waterfall_names=len(IFJ["made"]), load_bearing_rows=LB["rows"], gov_map_helper_rows=N_GMH)
GOV["fm_log"] = GOV["fm_log"] + [f"v518 input {x}" for x in V518_LOG] + [f"retired input (now formula) {k[0]} [{k[1][0]}] col {k[2]}: Excel value {v!r}" for k, v in RETIRED.items()]
open(os.path.join(OUTDIR, "gov_log.txt"), "w").write("\n".join([f"{k}: {v}" for k, v in GOV.items() if k != "fm_log"] + ["-- formula map changes --"] + GOV["fm_log"]))
print("gov:", {k: v for k, v in GOV.items() if k != "fm_log"})
import v1010
V1010 = v1010.apply(wb)       # v10.1 (4-1): slimming that does not change any output; runs last so it is applied on top of everything else
print("v1010 slimming:", V1010)
V1020 = v1020.apply(wb, v518._append_text)       # v10.2: Perf_Batch R-S labels (E4), SRC notes and second sources, Decisions status
print("v1020 eta calibration:", V1020)
V1030 = v1030.apply(wb, v518._append_text)       # v10.3 (4-2a): notes and 用途 marks, Gov_Map notes, Decisions SL42-*
print("v1030 slimming 4-2a:", V1030)
V1100 = v1100.apply(wb, v518._append_text)       # v11.0: notes (J156, J68, Gov_Map C68), Calib L 用途 marks, Decisions BB-*
print("v1100 big-batch fix:", V1100)
V1200 = v1200.apply(wb, v518._append_text)       # v12.0: notes (J156, J68, H156), Alloc N range section, Decisions BB2-*
print("v1200 v11.1 patch:", V1200)
import v1300
V1300 = v1300.apply(wb, v518._append_text)       # v13.0 (4-2b-1): RNG_ range section (Alloc O), range freshness check (Checks RG), K4 label, Decisions BB3-*
print("v1300 4-2b-1:", {k: v for k, v in V1300.items() if k != "table"})
import v1310
V1310 = v1310.apply(wb, v518._append_text)       # v13.1 (D15 B): P1 notes／DB_Evidence R／Decisions D15-*, P2 fingerprint block (Alloc P), Checks RG3
print("v1310 D15 B:", V1310)
V1400 = v1400.apply(wb, v518._append_text)       # v14.0 (4-3B): Q1 deletion, D104／D140, 用途 marks, Decisions SL43-*
print("v1400 4-3B:", V1400)
V1410 = v1410.apply(wb, v518._append_text)       # v14.1: R1 texts, R3 Har_In flags, R4 labels, R5 Cap_In cells, R6 small items, Decisions SL44-*
print("v1410 v14.1:", {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ("list", "orig", "anchor_orig")}) for k, v in V1410.items()})
import v1420
V1420 = v1420.apply(wb, v518._append_text)       # v14.2: S1 Cap_In 285／286 (P25Lo／P25Hi) floor like R1, S2 Har_In 20／32 A／B labels, Decisions SL45-*
print("v1420 v14.2:", V1420)
import v1500
V1500 = v1500.apply(wb, v518._append_text)       # v15.0: audit close-out O13/O14/O15/O9/O6/O20, T3 O5/O4 notes, Decisions SL46-*
print("v1500 v15.0:", V1500)
import v1510
V1510 = v1510.apply(wb, v518._append_text)       # v15.1: U1/U2 text corrections after the v15.0 independent check, Sens_Rev A17 label formula, Decisions SL46-25…31
print("v1510 v15.1:", V1510)
import v1520
V1520 = v1520.apply(wb, v518._append_text)       # v15.2: B2 Cap_In C280:E280, B3 Calib D67, B4／J2 labels, notes, Decisions SL47-*, DB_Evidence E387…E392 (Gov_Map edits run in gov.py)
print("v1520 v15.2:", V1520)
V1530 = v1530.apply(wb, v518._append_text)       # v15.3: L1 H86–H88 labels, Decisions SL48-*, DB_Evidence E393…E397 (Gov_Map edits run in gov.py)
print("v1530 v15.3:", V1530)
V1600 = v1600.apply(wb, v518._append_text)       # v16.0: L1 P89 (reads L1_LTotalFleetV), Decisions SL49-*, DB_Evidence E398 (Gov_Map rows are appended in gov.py)
print("v1600 v16.0:", V1600)
V1700 = v1700.apply(wb, v518._append_text)       # v17.0: L1 P89 (reads the new main basis), L1 B107 label, Decisions SL50-*
print("v1700 v17.0:", V1700)
order = [n for n in ["README","Inputs","Spec_Rack","Arch","Serving","Workload","Calib","Tech_Registry","Perf","Sens_Perf","Unit_Cost","DC_Cost",
         "Train_In","Perf_Batch","Training","Sens_Train",
         "Cap_In","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
         "Har_In","Harness","Sens_Har","Alloc_In","Alloc",*PROD_SHEETS,"Interface","L1","Load_Bearing","Energy","NonNV","Sensitivity","Checks","Gov_Map","Decisions",
         "SRC_HW","SRC_DC","SRC_Model","SRC_Perf","SRC_Price","SRC_Cap","SRC_Harness","SRC_Demand","SRC_Index","Sources_Legacy","DB_Evidence"]]
assert sorted(order) == sorted(ws.title for ws in wb.worksheets), set(ws.title for ws in wb.worksheets) ^ set(order)
wb._sheets = [wb[n] for n in order]
wb.save(out)
import json; json.dump({"WL":WL,"H5":H5,"R5":R5,"SH5":SH5,"K4":K4,"P4":P4,"C4":C4,"S4":S4,"F4":F4,"A4":{k:v for k,v in A4.items() if not k.startswith("cost")},"T4":T4,"PR":PR,"CAL":CAL,"SR":SR,"PB":PB,"TRN":TRN,"STR":STR,"TI":TI,"TR":{k:v for k,v in TR.items() if not k.startswith("_")},"U":{f"{k[0]}_{k[1]}":v for k,v in U.items()},"SP":SP,"AR":AR}, open(os.path.join(OUTDIR, "rows.json"),"w"))
print("saved")

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

wb = openpyxl.load_workbook(BASE)
# ---- v5.7 Excel-first: snapshot every input cell (blue font) before the rebuild ----
SNAP = snapshot(wb)
# ---- strip Block 2/3 content to recover the Block 1 base, then rebuild deterministically ----
for n in ["Arch","Serving","Workload","Calib","Perf","Sens_Perf","Unit_Cost","Energy","NonNV",
          "Tech_Registry","Train_In","Perf_Batch","Training","Sens_Train",
          "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
          "Har_In","Harness","Sens_Har"]:
    if n in wb.sheetnames: del wb[n]
def clear(ws, r0, c1=1, c2=30):
    for r in range(r0, ws.max_row + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.value = None; cell.fill = openpyxl.styles.PatternFill(fill_type=None)
clear(wb["Spec_Rack"], 21); 
for r in range(1, 21): wb["Spec_Rack"].cell(row=r, column=8).value = None
clear(wb["Interface"], 17); clear(wb["Checks"], 12); clear(wb["Sources"], 23); clear(wb["README"], 4, 1, 2)
for n in list(wb.defined_names.keys()):
    if n not in ("CTL_GW","CTL_PowerCase","IF_CapexFacility","IF_CapexIT","IF_CapexTotal","IF_FacilityGW",
                 "IF_GPUhrEcon","IF_GPUsPerGW","IF_HoldAcct","IF_HoldEcon","IF_PowerCost","IF_RacksPerGW"):
        del wb.defined_names[n]
SP = spec_rack(wb)
AR = arch(wb)
serving(wb)
CAL = calib(wb, SP, AR)
energy_inputs(wb)
TR = tech_registry(wb)
TI = train_in(wb)
PR = perf_sheet(wb, SP, AR, CAL, TR)
SR = sens_sheet(wb, SP, AR, CAL, TR)
PB = perf_batch(wb, SP, AR, CAL, TR, TI)
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
P4 = price_frontier(wb, K4, TR)
C4 = capability(wb, K4, P4, TRN, TI)
S4 = cache_store(wb)
F4 = fleet(wb, K4)
A4 = amortize(wb, F4, P4, S4)
T4 = theory_rev(wb, F4, A4, S4, WL)
K4["_capf"] = P4["capf"]
sens_rev(wb, K4, T4, A4)
interface_b4(wb, last_row(wb["Interface"]) + 2, P4, S4, A4, T4)
checks_b4(wb, P4, F4, A4, T4, U)
# ---- v5.9: Block 5 (harness) ----
from block5 import har_in, harness, sens_har, interface_b5, checks_b5, sources_b5, evidence_b5
H5 = har_in(wb, TR)
R5 = harness(wb, U, S4, WL)
SH5 = sens_har(wb, U, S4, WL, H5, R5)
interface_b5(wb, last_row(wb["Interface"]) + 2, R5)
checks_b5(wb, R5, H5, SH5)
sources(wb)
sources_b4(wb)
sources_b5(wb)
readme(wb)
# ---- v5.7: write back Excel-owned inputs, then the evidence register (created only if absent) ----
_m, _c, _d = restore(wb, SNAP, os.path.join(OUTDIR, "restore_log.txt"))
print(f"restore: matched {_m}, Excel kept over code {_c}, unmatched {len(_d)}")
evidence_sheet(wb)
print("evidence rows added:", evidence_b4(wb), evidence_b5(wb))
order = ["README","Inputs","Spec_Rack","Arch","Serving","Workload","Calib","Tech_Registry","Perf","Sens_Perf","Unit_Cost","DC_Cost",
         "Train_In","Perf_Batch","Training","Sens_Train",
         "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
         "Har_In","Harness","Sens_Har","Interface","Energy","NonNV","Sensitivity","Checks","Sources","DB_Evidence"]
wb._sheets = [wb[n] for n in order]
# ---- v5.3: Block 1 Checks — reference cells instead of literals (CC 第 1 輪第 6 節第 5 項) ----
from common import put, F_IN
ck = wb["Checks"]
for r, v in [(5, 35), (7, 2.21), (8, 2.65), (9, 10.5), (10, 3.57)]:
    put(ck, f"C{r}", v, F_IN, fmt="#,##0.00")
ck["E5"].value = '=IF(ABS(B5-C5)/C5<=0.2,"±20% 內","差距 >20%")'
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
wb.save(out)
import json; json.dump({"WL":WL,"H5":H5,"R5":R5,"SH5":SH5,"K4":K4,"P4":P4,"C4":C4,"S4":S4,"F4":F4,"A4":{k:v for k,v in A4.items() if not k.startswith("cost")},"T4":T4,"PR":PR,"CAL":CAL,"SR":SR,"PB":PB,"TRN":TRN,"STR":STR,"TI":TI,"TR":{k:v for k,v in TR.items() if not k.startswith("_")},"U":{f"{k[0]}_{k[1]}":v for k,v in U.items()},"SP":SP,"AR":AR}, open(os.path.join(OUTDIR, "rows.json"),"w"))
print("saved")

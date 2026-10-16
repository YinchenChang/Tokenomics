# v13.0 (work order docs/workorders/20261017_4-2b.md section 1 = 4-2b-1, branch claude/4-2b-1; K1–K5).
#   K1  Batch-multiplier ranges for every contract name that moves with CAL_BatchEtaD[GB200] / [Hopper]: RNG_<name>_Lo / RNG_<name>_Hi (Alloc section O; same shape as <name>).
#       Endpoints are scenario recalculations (tools/gen_ranges.py -> builder/v1300_ranges.json), written as black constants; the list of names is derived from the recalculation itself.
#   K2  Freshness: RNG_Version (version at which the endpoints were generated) vs RNG_Current (README!B5) and a base-inside-range count; RNG_StaleFlag shows 一致／區間過期; Checks RG1／RG2 (WARN, counted in GOV_Warnings).
#       tests/parity (test_v1300_*) recompute all endpoints from scenarios and require equality (1e-9).
#   K3  Calib C68 category (Gov_Map col F) 倒推 -> Assumed (enters Load_Bearing); the old category and the pre-v12.0 interval are kept in a new Gov_Map column AL; note appended to col N and O.
#   K4  Checks V: "Pass + Fail + Warn = Total" is labelled a structural identity (not a verification); it was never in the verification count, so only labels change.
#   K5  Name-count reconciliation of the v12.0 build report (text only: docs/reports/20261016_v11.1修補.md, appended correction).
# Major version: new contract names RNG_* (CLAUDE.md section 4). Every write to an Excel-owned cell is guarded (old value / old text); existing values of IF_／IFW_／L1_／CHK_ names do not change.
import json
from copy import copy
from pathlib import Path

from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY, section
import v1020
import v1200

VERSION = "20261017_Tokenomics_v13.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-17"
V = "v13.0"
WO = "工作單 docs/workorders/20261017_4-2b.md 第 1 節（4-2b-1）"
DEC_BY = "Andy 2026-10-17 01:46「開始」（工作單 4-2b；K1–K5 的處理方式為 chat 端預設，可撤回）"
DASH = "—"
RANGES_JSON = Path(__file__).resolve().parent / "v1300_ranges.json"


def load_ranges():
    if not RANGES_JSON.exists():
        return {"version": "", "names": {}, "graph_only_vr200": [], "graph_only_static": [], "display_names_moved": []}
    return json.loads(RANGES_JSON.read_text(encoding="utf-8"))


RNG = load_ranges()

SEC_TITLE = ("O. 批次口徑倍數區間端點（v13.0 K1／K2）：凡隨 CAL_BatchEtaD 的 GB200（Calib D156）或 Hopper（Calib C156）倍數變動的契約名稱 X，各有 RNG_X_Lo／RNG_X_Hi（形狀同 X）。"
             "端點＝情境重算（高端：GB200 1.83；低端：GB200 3.04、Hopper 3.74）兩者每格的較小／較大者，不是情境的『低端／高端』；以黑字數值寫入（不是公式，改輸入後不會自動更新）。"
             "時效：RNG_Version 必須等於現行版本，且基準落在區間內，否則 RNG_StaleFlag 顯示『區間過期』（Checks RG1／RG2，WARN）；tests/parity 以情境重算逐格比對全部端點（容差 1e-9）。重新產生：python3 tools/gen_ranges.py")
HDR = ["名稱 X", "列", "（以下每格＝X 的同一格；15 格名稱依序為 5 個世代 × 低成本／基準／高成本）"]
WIDTH_COLS = 15


# ================================================================== K1／K2: Alloc section O
def _last_row(ws):
    return max(c.row for row in ws.iter_rows() for c in row if c.value is not None)


def alloc_ranges(wb):
    """Section O of the Alloc sheet below section N. Names: RNG_<X>_Lo／_Hi (X ordered), RNG_Version, RNG_Current, RNG_OutCount, RNG_StaleFlag."""
    ws = wb["Alloc"]
    names = RNG["names"]
    r0 = _last_row(ws) + 2
    section(ws, r0, SEC_TITLE, 18)
    r = r0 + 1
    gens = [wb["Spec_Rack"].cell(4, c).value for c in range(3, 8)]
    gens = [g if isinstance(g, str) else f"世代{i + 1}" for i, g in enumerate(gens)]
    var = ["低成本", "基準", "高成本"]
    # control cells
    put(ws, f"A{r}", "區間計算版本（寫入端點時的版本）", F_BOLD); put(ws, f"C{r}", RNG["version"], F_CALC)
    put(ws, f"D{r}", "RNG_Version：tools/gen_ranges.py 產生端點檔時的活頁簿版本（builder/v1300_ranges.json 的 version）；改版後若未重新產生，與下一格不一致", F_NOTE)
    r_ver = r; r += 1
    put(ws, f"A{r}", "現行版本（README!B5 開頭的檔名）", F_BOLD); put(ws, f"C{r}", '=IFERROR(LEFT(README!$B$5,FIND("（",README!$B$5)-1),README!$B$5)', F_LINK)
    put(ws, f"D{r}", "RNG_Current：與 model/CURRENT 的檔名主幹相同（test_readme_version_consistency 守護）", F_NOTE)
    r_cur = r; r += 1
    r_out = r; r += 1
    r_flag = r; r += 1
    r += 1      # blank row
    # table header
    hdr_row = r
    put(ws, f"A{r}", HDR[0], F_BOLD); put(ws, f"B{r}", HDR[1], F_BOLD)
    for k in range(WIDTH_COLS):
        put(ws, f"{L(3 + k)}{r}", f"{gens[k // 3]}｜{var[k % 3]}", F_BOLD, wrap=True)
    put(ws, f"{L(3 + WIDTH_COLS)}{r}", "基準落在區間外的格數（容差 1e-9）", F_BOLD, wrap=True)
    ws.row_dimensions[r].height = 44
    r += 1
    first = r
    made = []
    out_rows = []
    for n in sorted(names):
        rec = names[n]; cnt = rec["n"]
        rl, rb, rh = r, r + 1, r + 2
        put(ws, f"A{rl}", n, F_BOLD); put(ws, f"A{rb}", n); put(ws, f"A{rh}", n)
        put(ws, f"B{rl}", "下限 Lo", F_CALC); put(ws, f"B{rb}", "基準（即時）", F_CALC); put(ws, f"B{rh}", "上限 Hi", F_CALC)
        for k in range(cnt):
            col = L(3 + k)
            put(ws, f"{col}{rl}", rec["lo"][k], F_CALC)
            put(ws, f"{col}{rh}", rec["hi"][k], F_CALC)
            put(ws, f"{col}{rb}", f"={n}" if cnt == 1 else f"=INDEX({n},1,{k + 1})", F_CALC)
        lc = L(2 + cnt)
        b = f"C{rb}:{lc}{rb}" if cnt > 1 else f"C{rb}"
        lo = f"C{rl}:{lc}{rl}" if cnt > 1 else f"C{rl}"
        hi = f"C{rh}:{lc}{rh}" if cnt > 1 else f"C{rh}"
        put(ws, f"{L(3 + WIDTH_COLS)}{rb}",
            f"=SUMPRODUCT(({b}<{lo}-1E-9*ABS({lo})-1E-12)+({b}>{hi}+1E-9*ABS({hi})+1E-12))", F_CALC, fmt="0")
        out_rows.append(rb)
        for tag, row in (("Lo", rl), ("Hi", rh)):
            ref = f"Alloc!$C${row}:${lc}${row}" if cnt > 1 else f"Alloc!$C${row}"
            wb.defined_names[f"RNG_{n}_{tag}"] = DefinedName(f"RNG_{n}_{tag}", attr_text=ref)
        made.append(n)
        r += 3
    last = r - 1
    oc = L(3 + WIDTH_COLS)
    put(ws, f"A{r_out}", "基準落在區間外的格數（全部名稱合計）", F_BOLD)
    put(ws, f"C{r_out}", f"=SUM({oc}{first}:{oc}{last})", F_CALC, fmt="0")
    put(ws, f"D{r_out}", "RNG_OutCount：不為 0 表示上游輸入已改動、端點不再涵蓋基準（需重新產生端點檔）", F_NOTE)
    put(ws, f"A{r_flag}", "區間時效旗標", F_BOLD)
    put(ws, f"C{r_flag}", f'=IF(AND(C{r_ver}=C{r_cur},C{r_out}=0),"一致","區間過期")', F_BOLD, fill=FILL_KEY)
    put(ws, f"D{r_flag}", "RNG_StaleFlag：『一致』＝端點產生於現行版本且基準仍在區間內；『區間過期』＝請勿使用 RNG_*，須重新產生（Checks RG1／RG2 WARN）", F_NOTE)
    for nm, ref in (("RNG_Version", f"Alloc!$C${r_ver}"), ("RNG_Current", f"Alloc!$C${r_cur}"), ("RNG_OutCount", f"Alloc!$C${r_out}"), ("RNG_StaleFlag", f"Alloc!$C${r_flag}")):
        wb.defined_names[nm] = DefinedName(nm, attr_text=ref)
    # excluded names (upstream contains CAL_BatchEtaD but the two endpoint scenarios do not move them): listed so that nobody reads their absence as 'certain'
    r = last + 2
    vr = RNG["graph_only_vr200"]; st = RNG["graph_only_static"]
    put(ws, f"A{r}", "未建區間的名稱（依賴圖上游含 CAL_BatchEtaD，但兩個端點情境下值不變）：", F_BOLD); r += 1
    put(ws, f"A{r}", f"（a）只經 VR200 欄（CAL_BatchEtaD 第 4 格＝0.75；Gov_Map H156 區間 0.70–1.0）{len(vr)} 個，GB200／Hopper 倍數改變時不動，VR200 倍數改變時會動；"
                     f"本版區間只涵蓋 GB200／Hopper 倍數，未涵蓋 VR200 倍數：{'、'.join(vr) if vr else '（無）'}", F_NOTE); r += 1
    put(ws, f"A{r}", f"（b）依賴圖上有路徑、但任何倍數改變都不動（計數、守衛或不選用的欄）{len(st)} 個：{'、'.join(st) if st else '（無）'}", F_NOTE); r += 1
    return {"first": first, "last": last, "names": len(made), "cells": sum(names[n]["n"] for n in made), "ver_row": r_ver, "cur_row": r_cur, "out_row": r_out, "flag_row": r_flag,
            "out_rows": out_rows, "end": r}


# ================================================================== K2: Checks RG section
def checks_rg(wb, A):
    ws = wb["Checks"]
    r = _last_row(ws) + 2
    section(ws, r, "RG. 批次口徑區間時效檢查（v13.0 K2，工作單 4-2b-1）：RG1、RG2 為 WARN，計入 GOV_Warnings（不阻擋）；端點本身由 tests/parity 以情境重算逐格比對", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i + 1)}{r}", h, F_BOLD)
    r += 1
    rows = [("RG1", "批次口徑區間的計算版本（RNG_Version）不等於現行版本（RNG_Current）：1＝區間過期", f'=IF(RNG_Version=RNG_Current,0,1)', "RNG_Version；RNG_Current（README!B5）；Alloc O 節"),
            ("RG2", "批次口徑區間：基準值落在 RNG_*_Lo／_Hi 之外的格數（容差 1e-9；上游輸入改動後區間不再涵蓋基準）", "=RNG_OutCount", "RNG_OutCount；Alloc O 節 R 欄")]
    at = {}
    for code, lab, f, note in rows:
        put(ws, f"A{r}", code); put(ws, f"B{r}", lab, wrap=True); put(ws, f"C{r}", "WARN")
        put(ws, f"D{r}", f, F_CALC, fmt="0"); put(ws, f"E{r}", note, F_NOTE); at[code] = r; r += 1
    ref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    for c in ("RG1", "RG2"):
        if f"D{at[c]}" not in str(cell.value): cell.value = f"{cell.value}+D{at[c]}"
    lab = ws[f"B{int(ref[1:])}"]
    if "RG1" not in str(lab.value): lab.value = (str(lab.value)[:-1] + "、RG1、RG2）") if str(lab.value).endswith("）") else f"{lab.value}、RG1、RG2"
    return at


# ================================================================== K3: Gov_Map C68 (called from gov.py's update chain)
GM_NEW_COL = "AL"
GM_NEW_HDR = "v13.0 前的類別與區間（保留原文；工作單 4-2b K3）"
N_ADD = (" ｜v13.0（4-2b-1 K3）：類別由『倒推』更正為 Assumed（無來源，見 Decisions BB2-H4）；原類別字樣與 v12.0 以前的區間文字保留於本列 AL 欄。C68 隨之進入 Load_Bearing（高段 Assumed）")
O_ADD = " ｜v13.0 K3：類別欄由『倒推』改為 Assumed，原字樣保留於 AL 欄"


def gov_update(ws, append_text):
    n = 0
    r = v1020._gm_row(ws, "Calib", "C68")
    hdr = ws[f"{GM_NEW_COL}4"]
    if hdr.value in (None, ""):
        hdr.value = GM_NEW_HDR
        src = ws["AK4"]
        hdr.font = copy(src.font); hdr.fill = copy(src.fill); hdr.alignment = copy(src.alignment)
        ws.column_dimensions[GM_NEW_COL].width = 46
        n += 1
    if ws[f"F{r}"].value == "倒推":
        old_m = "1–3（原註）"      # v11.0 and earlier: 區間文字; K／L were 1／3
        ws[f"{GM_NEW_COL}{r}"].value = ("v13.0 前：類別＝倒推（v5.11 起；v12.0 H4 已註明無證據，Decisions BB2-H4）｜v12.0 前：區間文字＝" + old_m + "（低 1、高 3）｜"
                                         "v12.0：區間 1.0–1.5（低 1、高 1.5）；現行區間 1.0–1.5 維持")
        ws[f"F{r}"].value = "Assumed"; n += 2
    n += append_text(ws[f"N{r}"], N_ADD)
    n += append_text(ws[f"O{r}"], O_ADD)
    return n


# ================================================================== K4: labels in Checks V
def k4_labels(wb, append_text):
    ws = wb["Checks"]
    n = 0
    vt = next(r for r in range(100, ws.max_row + 1) if ws.cell(r, 1).value == "VT")
    n += append_text(ws[f"B{vt}"], "｜恆等式（非驗證）：Pass＋Fail＋Warn＝Total 是結構恆等式（Fail 以 COUNT(F)−Pass 算出，Total 以 COUNT(F)＋警示數算出），不能失敗，不是驗證項目，也不在本計數內（v13.0 K4）")
    intro = vt - 1
    n += append_text(ws[f"A{intro}"], "｜v13.0 K4：『Pass＋Fail＋Warn＝Total』是結構恆等式（恆等式（非驗證）），不計入驗證項目數；它由 tests/parity 以斷言守護。")
    return n


# ================================================================== end of build
def apply(wb, append_text):
    log = {}
    log["table"] = alloc_ranges(wb)
    A = log["table"]
    log["checks_rg"] = checks_rg(wb, A)
    log["k4_labels"] = k4_labels(wb, append_text)
    log["decisions"] = decisions_append(wb)
    return {**{k: v for k, v in log.items() if k != "table"}, "ranges": {k: v for k, v in A.items() if k not in ("out_rows",)}, "table": A}


# ================================================================== Decisions (10 columns; layout of v1200)
_D = [
    ("K1", "批次口徑倍數區間：全部受影響的契約名稱補低／高端（RNG_<名稱>_Lo／_Hi）",
     f"查核 #92 第 1 項：v12.0 只給 IF_AllocRDGW、IF_AllocQ1 區間，其餘隨 GB200／Hopper 倍數變動的名稱仍是點值。本版依賴圖＋情境重算決定名單：納入 {len(RNG['names'])} 個契約名稱（IF_／L1_），"
     f"共 {sum(v['n'] for v in RNG['names'].values())} 格；端點＝兩個端點情境（高端：GB200 1.83；低端：GB200 3.04、Hopper 3.74）每格的較小／較大者，並確認其他三個角落（1.83×3.74、3.04×1、Hopper 3.74 單獨）與基準都落在端點之內。"
     f"有 {sum(1 for v in RNG['names'].values() if v.get('inverted_cells'))} 個名稱隨倍數增加而下降或反向（_Lo 對應情境的高端），故 _Lo／_Hi 一律指數值較小／較大端。依賴圖上游含 CAL_BatchEtaD 但兩個端點情境下值不變者另列於 Alloc O 節末（只經 VR200 欄或與倍數無關的路徑），本版不建區間。"
     "IF_AllocRDGW、IF_AllocQ1 的舊表 AL_RngRDGW／Q1_Lo／Hi（6 位小數、v12.0）保留不動，新表 RNG_IF_AllocRDGW／Q1_* 為全精度，兩者差異 < 5e-7。",
     "Alloc O 節；RNG_*；tools/gen_ranges.py；builder/v1300_ranges.json；下游契約文件", "v13.0 已建"),
    ("K2", "區間時效保證（RNG_Version、RNG_StaleFlag、Checks RG1／RG2、parity 逐格重算）",
     "查核 #92 第 2 項（原則 2：搜得到的數字不得是陷阱）：區間端點是情境重算結果，只能以數值寫入 Excel，輸入改動後會悄悄過期。四道保證：（1）RNG_Version 記錄產生端點時的版本；（2）RNG_Current 讀 README!B5，兩者不同或基準落在區間外時 RNG_StaleFlag 顯示『區間過期』；"
     "（3）Checks RG1／RG2（WARN）計入 GOV_Warnings；（4）tests/parity 的 test_v1300_ranges_equal_scenarios 以情境重算全部端點並要求等於 Excel 內的值（容差 1e-9），名單也由重算結果決定（新出現受倍數影響的契約名稱而沒有區間，測試失敗）；"
     "（5）全部 RNG_*_Lo／_Hi 與 AL_Rng* 納入契約快照。（4）才是真正的時效保證；（1）–（3）是使用者在 Excel 內看得到的警告。",
     "Alloc O 節；Checks RG；tests/parity", "v13.0 已建"),
    ("K3", "C68 類別欄更正為 Assumed，進入 Load_Bearing；原類別與 v12.0 以前區間保留於 Gov_Map AL 欄",
     "查核 #92 第 3 項：v12.0 H4 把 C68 的正確標記說成 Assumed，但 Gov_Map F 欄仍是『倒推』，所以 C68 不在 Load_Bearing（類別∈{Assumed, Analogy} 且高段）。本版依工作單把 F 欄改為 Assumed，"
     "並在新增的 Gov_Map AL 欄保留『v13.0 前：類別＝倒推』與『v12.0 前：區間文字 1–3（原註）、低 1、高 3』，N 欄理由與 O 欄標記變更追加更正說明。現行區間 1.0–1.5 維持。"
     "注意：這是改動標記欄（CLAUDE.md 第 6 節），原字樣已保留，依工作單明文處理，見報告待 Project 判斷。Calib J68 的『倒推』舊字樣不動（v12.0 H4 已加更正註記）。",
     "Gov_Map 第 350 列（GM346）F／N／O／AL；Load_Bearing；LB_Rows／LB_LiveCount", "v13.0 已建"),
    ("K4", "『Pass＋Fail＋Warn＝Total』標為恆等式（非驗證）",
     "查核 #92 第 4 項：Fail 以 COUNT(F)−Pass 算出，故恆等式在結構上不可能失敗，不是獨立檢查。它本來就不是 Checks V 的 F 欄項目，不在驗證計數內，所以只改標籤：Checks VT 列與 V 節說明追加『恆等式（非驗證）』。"
     "CHK_VerifyTotal／Pass／Fail／Warn 的數值與公式不變（20／12／7／1）。是否另設獨立計數使其可失敗，列待 Project 判斷。",
     "Checks V 節 A／B 欄標籤", "v13.0 已建"),
    ("K5", "v12.0 建置報告的名稱數更正（文字，不改模型）",
     "查核 #92 第 5 項：v12.0 報告寫『新增 6 個名稱、73 個值有變動』。重算：（i）活頁簿具名範圍 1,370 → 1,375，新增 5 個（CHK_SoftCapFail、AL_Rng*_Lo／Hi 四個）；『6』是契約快照的條目數（637 → 643），"
     "其中 3 個是真正的新名稱（CHK_SoftCapFail、AL_RngRDGW_Lo、AL_RngQ1_Lo），3 個是既有名稱首次被快照收錄（CAL_BatchEtaD、SRC_HW_067、SRC_PERF_079）；（ii）值有變動：快照名稱 57 個（IF_ 41、L1_ 12、CHK_Verify 2、GOV_ 2，共 129 格），"
     "全部具名範圍 87 個（另含 AL_ 17、TRN_ 8、LB_ 3、IDX_ 1、CAL_ 1）；『73』在任何口徑下都無法重現，判定為報告筆誤。更正註記已追加於 docs/reports/20261016_v11.1修補.md。",
     "docs/reports/20261016_v11.1修補.md（追加更正）", "v13.0 已建"),
]
DECISIONS_V1300 = [[f"BB3-{i}", V, f"4-2b-1：{t}", txt, DATE, DEC_BY, st, where, f"{WO} {i}", "否"] for i, t, txt, where, st in _D]


def decisions_append(wb):
    ws = wb["Decisions"]
    have = {ws.cell(r, 1).value for r in range(5, ws.max_row + 1)}
    r = max([rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")] or [4]) + 1
    n = 0
    for row in DECISIONS_V1300:
        if row[0] in have: continue
        for i, v in enumerate(row): put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 5, 7))
        r += 1; n += 1
    return n


# ================================================================== README
README_VERSION = (VERSION + "（主版：" + WO + "——K1 批次口徑倍數區間（RNG_<名稱>_Lo／_Hi，Alloc O 節）；K2 區間時效（RNG_Version、RNG_StaleFlag、Checks RG1／RG2、parity 逐格重算）；"
                  "K3 C68 類別更正為 Assumed 並進入 Load_Bearing；K4 『Pass＋Fail＋Warn＝Total』標恆等式；K5 名稱數更正；Decisions BB3-*）。以下為 "
                  + v1200.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1200.README_TITLE
README_TITLE = V + _T[len(v1200.V):]
README_ROW = ("區間完整化與時效（v13.0）",
              "全部隨 GB200／Hopper 批次倍數變動的契約名稱補低／高端（RNG_<名稱>_Lo／_Hi，Alloc O 節）；區間時效旗標 RNG_StaleFlag 與 Checks RG1／RG2；C68 類別更正為 Assumed。細節見 Decisions BB3-*。")

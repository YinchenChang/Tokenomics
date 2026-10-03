# v5.11 (Stage 1 slice one): Source layer (SRC_HW／SRC_DC／SRC_Model／SRC_Perf), DB_Evidence upgrade, Decisions,
# Gov_Map (blue-cell registry), L1 (first batch), governance Checks, F14 (per-GW outputs divided by Inputs!E5).
#
# Ownership (Excel-first, same rule as DB_Evidence since v5.7):
#   - SRC_*, Decisions, DB_Evidence, and the judgment columns of Gov_Map are Excel-owned: created from gov_seed /
#     gov_decisions only when absent, never overwritten afterwards.
#   - Builder-owned (rewritten on every build): FORMULA_MAP links on model pages, helper formulas in SRC_* (X–Z),
#     Gov_Map formula / status columns (Q–AE), the L1 sheet, the Checks governance section, SRC_/L1_/GOV_ names.
import re
from openpyxl.styles import PatternFill
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_TITLE, F_NOTE, FILL_SEC, FILL_KEY, WRAP, L, title, section
from gov_seed import SRC_RECORDS, PERF_ATTR, EVID_MIG, EVID_UPD, FORMULA_MAP, GOV_MAP
from gov_decisions import DECISIONS

SRC_SHEETS = ["SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf"]
SRC_LAST = 400                      # record rows 5..SRC_LAST (formula ranges)
SRC_HDR = ["SRC_ID", "指標", "數值", "低", "高", "單位", "口徑", "適用對象", "日期", "出處", "來源等級", "立場", "立場說明",
           "一手／二手", "狀態", "取代者", "Evidence ID", "第二來源 SRC_ID", "審查日", "Andy 原話", "原 S 編號", "模型使用位置", "備註",
           "同指標同口徑 Active 數（公式）", "缺 Evidence（公式）", "利害關係方缺第二來源（公式）"]
PERF_HDR = ["平台", "軟體／日期", "ISL", "OSL", "每用戶速度 tok/s", "MTP（1＝有）", "token 口徑"]
PERF_NAMES = {"AC": "_ISL", "AD": "_OSL", "AE": "_Spd", "AF": "_MTP"}
SRC_TITLE = {"SRC_HW": "晶片與機架的規格、功率、價格", "SRC_DC": "廠房資本支出、電價、折舊慣例、外部成本參照",
             "SRC_Model": "模型架構與訓練揭露", "SRC_Perf": "推論與訓練量測（InferenceX、MLPerf、自揭）及量測條件"}
DASH = "—"


def _nm(wb, n, ref):
    if n in wb.defined_names: del wb.defined_names[n]
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


# ---------------------------------------------------------------- 1. Source sheets (Excel-owned after creation)
def src_sheets(wb):
    made = []
    for sh in SRC_SHEETS:
        if sh in wb.sheetnames: continue
        ws = wb.create_sheet(sh); made.append(sh)
        title(ws, f"{sh} — 第 0 層 Source：{SRC_TITLE[sh]}",
              "只存已取得的原始訊息（非計算、非假設；G1）。藍字＝原始值，由本活頁簿擁有；模型頁以公式連結 SRC_ID 具名範圍。"
              "新訊息先登錄 DB_Evidence，比較後擇優寫入（G2–G6）。X–Z 欄為檢查公式（builder 每次重建）。")
        put(ws, "A3", "來源等級：A＝Andy、1＝一手且已讀原文、2＝二手已讀或一手文件轉載、3＝模型內建知識、只見摘錄或待查核（G0-7）。"
                      "狀態：Active／Alt（口徑不同或多家獨立估計並列，G13）／Superseded。", F_NOTE)
        hdr = SRC_HDR + (PERF_HDR if sh == "SRC_Perf" else [])
        widths = [13, 40, 11, 9, 9, 13, 22, 20, 11, 40, 6, 10, 30, 12, 10, 10, 16, 14, 9, 12, 8, 30, 36, 10, 10, 10] + [16, 22, 7, 7, 9, 8, 14]
        for i, h in enumerate(hdr):
            put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = widths[i]
        r = 5
        for rec in [x for x in SRC_RECORDS if x["sheet"] == sh]:
            vals = [rec["id"], rec["metric"], rec["val"], rec["lo"], rec["hi"], rec["unit"], rec["basis"] or DASH, rec["applies"] or DASH,
                    str(rec["date"]), rec["src"] or DASH, rec["grade"], rec["stance"], rec["stance_note"] or DASH, rec["hand"] or DASH,
                    rec["status"], DASH, rec["ev"], DASH, DASH, DASH, rec["s"], rec["use"] or DASH, rec["note"] or DASH]
            for i, v in enumerate(vals):
                f = F_IN if i in (2, 3, 4) and isinstance(v, (int, float)) else F_CALC
                put(ws, f"{L(i+1)}{r}", v, f, wrap=i in (1, 9, 12, 21, 22))
            if sh == "SRC_Perf" and rec["id"] in PERF_ATTR:
                a = PERF_ATTR[rec["id"]]
                for col, k in zip(["AA", "AB", "AC", "AD", "AE", "AF", "AG"], ["platform", "software", "isl", "osl", "spd", "mtp", "tok"]):
                    put(ws, f"{col}{r}", a[k], F_IN if isinstance(a[k], (int, float)) else F_CALC)
            r += 1
        ws.freeze_panes = "C5"
    return made


def src_refresh(wb):
    """Helper formulas (X–Z) for every record row, and SRC_ names (value／_Lo／_Hi／Perf attributes)."""
    n_names = 0; index = {}
    for sh in SRC_SHEETS:
        ws = wb[sh]
        for r in range(5, ws.max_row + 1):
            sid = ws.cell(r, 1).value
            if not (isinstance(sid, str) and sid.startswith("SRC_")): continue
            index[sid] = (sh, r)
            rng = lambda c: f"${c}$5:${c}${SRC_LAST}"
            put(ws, f"X{r}", f'=IF($O{r}="Active",SUMPRODUCT(({rng("B")}=$B{r})*({rng("G")}=$G{r})*({rng("H")}=$H{r})*({rng("O")}="Active")),0)', fmt="0")
            put(ws, f"Y{r}", f'=IF(AND($O{r}="Active",OR($Q{r}="{DASH}",$Q{r}="")),1,0)', fmt="0")
            put(ws, f"Z{r}", f'=IF(AND($O{r}="Active",$L{r}="利害關係方",OR($R{r}="{DASH}",$R{r}="")),1,0)', fmt="0")
            _nm(wb, sid, f"{sh}!$C${r}"); n_names += 1
            for col, suf in (("D", "_Lo"), ("E", "_Hi")):
                if ws[f"{col}{r}"].value is not None: _nm(wb, sid + suf, f"{sh}!${col}${r}"); n_names += 1
            if sh == "SRC_Perf":
                for col, suf in PERF_NAMES.items():
                    if ws[f"{col}{r}"].value is not None: _nm(wb, sid + suf, f"{sh}!${col}${r}"); n_names += 1
    return n_names, index


# ---------------------------------------------------------------- 2. DB_Evidence upgrade (Excel-owned)
EV_NEW_HDR = ["狀態（已處理／待判定／待 Andy）", "相關 SRC_ID", "取代者", "受影響 IF_／L1_", "來源等級", "立場"]

def evidence_upgrade(wb):
    ws = wb["DB_Evidence"]; added = 0
    if ws["L4"].value is None:
        for i, h in enumerate(EV_NEW_HDR):
            put(ws, f"{L(12+i)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(12+i)].width = [14, 30, 12, 20, 8, 12][i]
        put(ws, "A3", "v5.11：新增 L–Q 欄（G2 流程的狀態、相關 SRC_ID、取代者、受影響名稱、等級、立場）；E101 起為 Stage 1 遷移紀錄。", F_NOTE)
    have = {ws.cell(r, 1).value: r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value}
    for eid, vals in EVID_UPD.items():
        r = have.get(eid)
        if r and ws.cell(r, 12).value is None:
            for i, v in enumerate(vals):
                put(ws, f"{L(12+i)}{r}", v if v != "" else DASH, F_CALC, wrap=i in (1, 5))
    r = max(have.values()) + 1 if have else 5
    for row in EVID_MIG:
        if row[0] in have: continue
        for i, v in enumerate(row):
            put(ws, f"{L(i+1)}{r}", v if v != "" else DASH, F_IN if i < 11 else F_CALC, wrap=i in (2, 10, 12))
        r += 1; added += 1
    return added


# ---------------------------------------------------------------- 3. Decisions (Excel-owned)
DEC_HDR = ["決策 ID", "類別", "項目", "決議", "日期", "Andy 原話／依據", "狀態", "影響範圍（工作表、格、名稱）", "出處", "原話待 Andy 確認"]

def decisions_sheet(wb):
    if "Decisions" in wb.sheetnames: return False
    ws = wb.create_sheet("Decisions")
    title(ws, "Decisions — 決策登錄（G11：交接文件第 2 節移入；之後交接文件只保留決策 ID）",
          "Excel 擁有：builder 只在本頁不存在時建立。模型頁的 Decision 格以決策 ID 引用（見 Gov_Map J 欄）；Checks 檢查 ID 是否存在。"
          "「原話待 Andy 確認」＝是：轉錄自交接文件，Andy 確認原話後改為否。")
    widths = [8, 14, 24, 70, 14, 30, 14, 34, 22, 10]
    for i, h in enumerate(DEC_HDR):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = widths[i]
    for j, row in enumerate(DECISIONS):
        for i, v in enumerate(row):
            v = v.replace("**", "").replace("`", "") if isinstance(v, str) else v
            put(ws, f"{L(i+1)}{5+j}", v, F_CALC, wrap=i in (2, 3, 5, 7))
    ws.freeze_panes = "B5"
    return True


# ---------------------------------------------------------------- 4. Model-page links (builder-owned)
def apply_formula_map(wb):
    n = 0; log = []
    for key, f in FORMULA_MAP.items():
        sh, co = key.split("!")
        c = wb[sh][co]
        if c.value != f:
            log.append(f"{key}: {c.value!r} -> {f}")
            c.value = f; n += 1
        c.font = F_LINK if ("SRC_" in f or "!" in f) else F_CALC
        c.fill = PatternFill(fill_type=None)
    return n, log


# ---------------------------------------------------------------- 5. F14: every "每 GW" output divided by Inputs!E5
def f14(wb):
    n = 0
    def wrap(ws, ref):
        nonlocal n
        v = ws[ref].value
        if isinstance(v, str) and v.startswith("=") and not v.endswith("/CTL_GW"):
            ws[ref].value = "=(" + v[1:] + ")/CTL_GW"; n += 1
    itf = wb["Interface"]
    for r in (6, 7, 8, 9, 10, 11, 12, 13, 15):
        for c in range(3, 18): wrap(itf, f"{L(c)}{r}")
    wrap(wb["Checks"], "B4"); wrap(wb["Checks"], "B5")
    sen = wb["Sensitivity"]
    for c in range(3, 26):
        if sen.cell(7, c).value == "=Inputs!$E$5*1000": sen.cell(7, c).value = "=1000"; n += 1
    sen["A7"].value = "IT 電力（每 GW 基準；F14）"
    # v5.11 (G0-5 scan): scenario values written as formulas (=0.05 etc.) become plain inputs (value unchanged)
    for ref in ("X8", "Y8", "N37"):
        v = sen[ref].value
        if isinstance(v, str) and re.fullmatch(r"=-?\d+(\.\d+)?", v):
            sen[ref].value = float(v[1:]) if "." in v else int(v[1:]); sen[ref].font = F_IN; n += 1
    dc = wb["DC_Cost"]
    dc["A1"].value = "DC_Cost — 設施合計（IT 規模＝Inputs!E5 GW，基準 1）：資本支出與年持有成本；5 世代 × 3 成本情境。每 GW 值見 Interface（F14）"
    for r, t in [(12, "機架數（設施）"), (14, "GPU 數（設施）"), (17, "B. 資本支出（$B；設施）"), (33, "總資本支出（設施）"),
                 (37, "C. 年持有成本 — 會計口徑（$B／年；設施）"), (50, "D. 年持有成本 — 經濟口徑（資本回收年金；設施）")]:
        dc[f"A{r}"].value = t
    wb["Inputs"]["H5"].value = "口徑：IT 關鍵電力。v5.11 起 DC_Cost 為設施合計；Interface、L1 與模型頁的「每 GW」一律已除以本格（F14）"
    return n


# ---------------------------------------------------------------- 6. Gov_Map
GM_HDR = ["GM_ID", "範圍", "工作表", "格", "列標籤", "類別", "區間角色", "SRC_ID（來源或可比對象）", "關係", "決策 ID", "低", "高", "區間文字",
          "理由", "標記變更（v5.11）", "CC 敏感度分段",
          "模型值", "SRC 值", "SRC 狀態", "SRC 等級", "實際狀態（建置時）",
          "E1 原始寫死", "E2 Analogy 缺可比", "E3 缺區間", "E4 缺理由", "E5 Decision 缺 ID", "E6 決策 ID 不存在", "E9 SRC 非 Active",
          "E10 區間順序", "W2 3 級×高段", "E12 SRC 不存在"]
GM_LAST = 700

def _lookup(h, col):
    parts = []
    for sh in SRC_SHEETS:
        parts.append((f"ISNUMBER(MATCH({h},{sh}!$A$5:$A${SRC_LAST},0))", f"INDEX({sh}!${col}$5:${col}${SRC_LAST},MATCH({h},{sh}!$A$5:$A${SRC_LAST},0))"))
    f = '"不存在"'
    for cond, val in reversed(parts): f = f"IF({cond},{val},{f})"
    return f

def gov_map(wb, src_index):
    ws = wb["Gov_Map"] if "Gov_Map" in wb.sheetnames else None
    if ws is None:
        ws = wb.create_sheet("Gov_Map")
        title(ws, "Gov_Map — 模型頁藍字格登錄（Stage 1 切片一：Inputs、Spec_Rack、Arch、Serving、Workload、Calib、Energy、NonNV 與其敏感度情境格）",
              "A–P 欄為判斷（Excel 擁有；類別、SRC_ID、決策 ID、區間、理由）；Q–AE 欄為 builder 每次重建的公式與建置時狀態。"
              "Checks G 節加總 V–AE 欄。區間角色＝低／高者為另一格的端點，不另檢查區間。")
        for i, h in enumerate(GM_HDR):
            put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True)
            ws.column_dimensions[L(i+1)].width = [8, 10, 11, 9, 26, 16, 7, 14, 22, 8, 9, 9, 18, 36, 22, 7][i] if i < 16 else 9
        for j, g in enumerate(GOV_MAP):
            r = 5 + j
            vals = [f"GM{j+1:03d}", g["scope"], g["sheet"], g["cell"], g["label"], g["cls"], g["role"], g["src"] or DASH, g["rel"] or DASH,
                    g["dec"] or DASH, g["lo"], g["hi"], g["rtext"] or DASH, g["reason"] or DASH, g["retag"] or DASH, g["seg"] or DASH]
            for i, v in enumerate(vals):
                font = F_IN if i in (10, 11) and isinstance(v, (int, float)) else (F_LINK if isinstance(v, str) and v.startswith("=") else F_CALC)
                put(ws, f"{L(i+1)}{r}", v, font, wrap=i in (4, 8, 13, 14))
        ws.freeze_panes = "E5"
    # ---- builder-owned columns Q..AE
    n = 0; static_raw_hard = 0
    for r in range(5, ws.max_row + 1):
        sh, cell = ws[f"C{r}"].value, ws[f"D{r}"].value
        if not sh or not cell: continue
        n += 1
        single = ":" not in str(cell)
        h = f"$H{r}"
        put(ws, f"Q{r}", f"='{sh}'!{cell}" if single else DASH, F_LINK)
        sid = ws[f"H{r}"].value
        if isinstance(sid, str) and sid in src_index:
            s2, rr = src_index[sid]
            # value field: the one the model cell links to, else the record value, else its low end
            fm = FORMULA_MAP.get(f"{sh}!{cell}", "")
            m = re.search(re.escape(sid) + r"(_Lo|_Hi|_Spd|_ISL|_OSL|_MTP)?\b", fm)
            suf = m.group(1) if m and m.group(1) else ("" if wb[s2][f"C{rr}"].value is not None else "_Lo")
            put(ws, f"R{r}", f"={sid}{suf}", F_LINK)
        else:
            put(ws, f"R{r}", DASH)
        put(ws, f"S{r}", f'=IF(OR({h}="{DASH}",{h}=""),"{DASH}",{_lookup(h, "O")})')
        put(ws, f"T{r}", f'=IF(OR({h}="{DASH}",{h}=""),"{DASH}",{_lookup(h, "K")})')
        if single:
            v = wb[sh][cell].value
            st = ("連結 SRC" if "SRC_" in v else "公式") if isinstance(v, str) and v.startswith("=") else ("藍字（常數）" if v is not None else "空白")
        else:
            st = DASH
        put(ws, f"U{r}", st)
        F = f"$F{r}"; G = f"$G{r}"
        put(ws, f"V{r}", f'=IF(AND({F}="原始數據",$U{r}<>"連結 SRC"),1,0)', fmt="0")
        put(ws, f"W{r}", f'=IF(AND({F}="Analogy",OR({h}="{DASH}",{h}="")),1,0)', fmt="0")
        put(ws, f"X{r}", f'=IF(AND(OR({F}="Analogy",{F}="Assumed"),{G}<>"低",{G}<>"高",NOT(ISNUMBER($K{r})),NOT(ISNUMBER($L{r})),OR($M{r}="{DASH}",$M{r}="")),1,0)', fmt="0")
        put(ws, f"Y{r}", f'=IF(AND(OR({F}="Analogy",{F}="Assumed",{F}="Derived（待改公式）",{F}="Derived（公式）"),OR($N{r}="{DASH}",$N{r}="",$N{r}=0)),1,0)', fmt="0")
        put(ws, f"Z{r}", f'=IF(AND({F}="Decision",OR($J{r}="{DASH}",$J{r}="")),1,0)', fmt="0")
        put(ws, f"AA{r}", f'=IF(OR($J{r}="{DASH}",$J{r}=""),0,IF(COUNTIF(Decisions!$A$5:$A$300,$J{r})=0,1,0))', fmt="0")
        put(ws, f"AB{r}", f'=IF(AND({F}="原始數據",$S{r}<>"Active"),1,0)', fmt="0")
        put(ws, f"AC{r}", f'=IF(AND(ISNUMBER($K{r}),ISNUMBER($L{r}),ISNUMBER($Q{r})),IF(OR($Q{r}<MIN($K{r},$L{r}),$Q{r}>MAX($K{r},$L{r})),1,0),0)', fmt="0")
        put(ws, f"AD{r}", f'=IF(AND(ISNUMBER($T{r}),$P{r}="高"),IF($T{r}=3,1,0),0)', fmt="0")
        put(ws, f"AE{r}", f'=IF(AND($S{r}="不存在",$B{r}="切片一"),1,0)', fmt="0")
        if st == "藍字（常數）" and ws[f"F{r}"].value == "原始數據": static_raw_hard += 1
    return n, static_raw_hard


# ---------------------------------------------------------------- 7. L1 (builder-owned; every value a live formula)
L1_HDR = ["L1_ID", "指標或問題", "條件", "基準值", "低", "高", "單位", "區間的定義", "讀法", "主要驅動", "最弱輸入的標記",
          "外部 SRC_ID", "外部值（低）", "外部值（高）", "推算 ÷ 外部", "判讀", "具名範圍", "所在頁與列", "未能回答的部分"]
GENCOL = {"Hopper": 1, "GB200": 4, "GB300": 7, "VR200": 10}     # Interface column index of the low-cost column (base = +1)
COST_RNG = "成本角落情境（低成本／高成本欄）"
UTIL_RNG = "利用率 40–80%（Sens_Rev 情境值；J6 區間）"

def _rows_l1():
    R = []
    for g, c0 in GENCOL.items():
        ext = ("SRC_DC_010", "=SRC_DC_010_Lo", "=SRC_DC_010_Hi") if g == "VR200" else (DASH, None, None)
        R.append((f"CapexGW_{g}", f"每 GW 資本支出（{g}）", "基準功率情境；含廠房", f"=INDEX(IF_CapexTotal,1,{c0+1})",
                  f"=INDEX(IF_CapexTotal,1,{c0})", f"=INDEX(IF_CapexTotal,1,{c0+2})", "$B/GW", COST_RNG,
                  "IT 設備＋廠房；GW＝IT 關鍵電力（D1）", "機架價格、配電設計功率（Block 1 敏感度）", "機架價格：3 級、Interested-party",
                  *ext, "IF_CapexTotal", "Interface 第 11 列", "外部 $50–60B 的 GW 口徑未明（IT 或設施）" if g == "VR200" else DASH))
    R.append(("NvContentGW_VR200", "每 GW NVIDIA 內容（機架，VR200）", "基準功率情境", "=DC_Cost!M19/CTL_GW", "=DC_Cost!L19/CTL_GW",
              "=DC_Cost!N19/CTL_GW", "$B/GW", COST_RNG, "機架取得價 × 每 GW 機架數", "機架價格、配電設計功率", "機架價格：3 級、Interested-party",
              "SRC_DC_011", "=SRC_DC_011", "=SRC_DC_011", "DC_Cost!M19（÷ CTL_GW）", "DC_Cost 第 19 列", "外部值 GW 口徑未明"))
    R.append(("FacCapexMW", "每 MW IT 廠房資本支出", "基準成本情境；與世代無關", "=DC_Cost!M36", "=DC_Cost!L36", "=DC_Cost!N36", "$M/MW",
              COST_RNG, "建物、電力、機械、光纖與預備費（不含 IT 設備）", "電力設施、建物分項（Assumed）", "分項皆 Assumed",
              "SRC_DC_003", "=SRC_DC_003*(1+SRC_DC_004_Lo)", "=SRC_DC_003*(1+SRC_DC_004_Hi)", "DC_Cost!M36", "DC_Cost 第 36 列",
              "外部：JLL 全球平均 × 液冷溢價 7–10%；JLL 的 MW 口徑（IT 或設施）待查"))
    for g, c0 in GENCOL.items():
        R.append((f"HoldEconGW_{g}", f"每 GW 年經濟持有成本（{g}）", "資本回收年金（WACC 10%）＋營運費用", f"=INDEX(IF_HoldEcon,1,{c0+1})",
                  f"=INDEX(IF_HoldEcon,1,{c0})", f"=INDEX(IF_HoldEcon,1,{c0+2})", "$B/GW/年", COST_RNG,
                  "資本回收占 77–81%，電費 4–7%", "IT 折舊年限、機架價格", "機架價格：3 級", DASH, None, None,
                  "IF_HoldEcon", "Interface 第 13 列", DASH))
    for g, c0 in GENCOL.items():
        ext = {"GB200": ("SRC_DC_012", "=SRC_DC_012", "=SRC_DC_012"), "GB300": ("SRC_DC_013", "=SRC_DC_013", "=SRC_DC_013")}.get(g, (DASH, None, None))
        R.append((f"GPUhr_{g}", f"每 GPU 小時持有成本 — 經濟（{g}）", "100% 時數；不含利潤", f"=INDEX(IF_GPUhrEcon,1,{c0+1})",
                  f"=INDEX(IF_GPUhrEcon,1,{c0})", f"=INDEX(IF_GPUhrEcon,1,{c0+2})", "$/GPU-hr", COST_RNG,
                  "每 GW 年持有成本 ÷（GPU 數 × 8,760）", "機架價格、IT 折舊年限、WACC", "機架價格：3 級", *ext, "IF_GPUhrEcon", "Interface 第 14 列",
                  "外部為 SemiAnalysis TCO（假設未公開，須第二來源）；CoreWeave 公開價對照於 v5.12（SRC_Price）" if ext[0] != DASH else DASH))
    for tier in ("Luna", "Sol", "Astra"):
        for g in ("VR200", "GB300"):
            c0 = GENCOL[g]
            R.append((f"CostDec_{tier}_{g}", f"decode（含思考）每 M token 成本 — {tier}（{g}）", "經濟口徑、100% 利用率、SLO 下", f"=INDEX(IF_CostDec_{tier},1,{c0+1})",
                      f"=INDEX(IF_CostDec_{tier},1,{c0})", f"=INDEX(IF_CostDec_{tier},1,{c0+2})", "$/M", COST_RNG,
                      "基準利用率版＝100% 版 ÷ 利用率（IF_Util）", "η_d、每層延遲、SLO、生產折減", "生產折減 1.0：Assumed（K11）；VR200 η_d：Analogy",
                      DASH, None, None, f"IF_CostDec_{tier}", "Interface Block 2 產出", "VR200 無實測，η_d 沿用 GB300" if g == "VR200" else DASH))
    R.append(("CostTotTokIX_GB300", "GB300 每 M 總 token 成本（以 InferenceX 72 tok/s 實測產出計）", "本模型 TCO × 外部實測產出；8K/1K",
              "=DC_Cost!J58/(Calib!C17*3600)*1000000", "=DC_Cost!I58/(Calib!C17*3600)*1000000", "=DC_Cost!K58/(Calib!C17*3600)*1000000", "$/M 總 token",
              COST_RNG, "差異只來自每 GPU 小時 TCO（產出相同）", "每 GPU 小時持有成本", "InferenceX：3 級、Interested-party",
              "SRC_PERF_011", "=SRC_PERF_011", "=SRC_PERF_011", DASH, "Checks 第 19 列（同式）", "SemiAnalysis TCO 假設未公開"))
    for tier, c in (("Luna", "IF_RevGW_Luna"), ("Sol", "IF_RevGW_Sol"), ("Astra", "IF_RevGW_Astra"), ("機隊", "IF_RevGWFleet")):
        key = "RevGW_" + ("Fleet" if tier == "機隊" else tier) + "_VR200"
        lab = f"每 GW 理論營收（理想上限）— {tier}（VR200）" if tier != "機隊" else "1 GW 參考機隊付費營收（理想上限，VR200）"
        R.append((key, lab, "OpenAI 有效單價、基準成本、基準利用率", f"=INDEX({c},1,11)", f"=INDEX({c},1,11)*Sens_Rev!$B$6/IF_Util",
                  f"=INDEX({c},1,11)*Sens_Rev!$B$7/IF_Util", "$B/GW/年", UTIL_RNG, "單一層級滿載的上限；實際營收（需求、市占）在下游",
                  "利用率、折扣、快取命中 χ（Sens_Rev）", "利用率 60%：Assumed（K11）；生產折減 1.0：Assumed",
                  DASH, None, None, c, "Interface D 節", "需求與市占不在第 0 層（D7）"))
    return R

def l1_sheet(wb):
    if "L1" in wb.sheetnames: del wb["L1"]
    ws = wb.create_sheet("L1")
    title(ws, "L1 — 第 1 層常用推算值（G9；即時公式、不貼值；附條件、區間與外部對照）",
          "下游取標準推算值時引用 L1_ 名稱；完整構件仍在 Interface（IF_）。外部值一律連結 SRC。判讀：外部為區間時看是否落在區間內；外部為單一值時以 ±20% 判讀。"
          "Block 6 的 9 題於 v5.13 補入。")
    widths = [22, 38, 26, 10, 10, 10, 10, 24, 30, 24, 26, 12, 10, 10, 9, 14, 18, 18, 30]
    for i, h in enumerate(L1_HDR):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = widths[i]
    r = 5; nonformula = 0
    for row in _rows_l1():
        key, lab, cond, base, lo, hi, unit, rdef, read, drv, weak, sid, elo, ehi, nmref, where, gap = row
        vals = [f"L1_{key}", lab, cond, base, lo, hi, unit, rdef, read, drv, weak, sid, elo, ehi, None, None, f"L1_{key}", where, gap]
        for i, v in enumerate(vals):
            if i == 14 or i == 15: continue
            fmt = "#,##0.000" if i in (3, 4, 5, 12, 13) else None
            put(ws, f"{L(i+1)}{r}", v if v is not None else DASH, F_LINK if isinstance(v, str) and v.startswith("=") and i in (12, 13) else None,
                fmt=fmt, wrap=i in (1, 2, 7, 8, 9, 10, 18), fill=FILL_KEY if i == 3 else None)
        for c in "DEF":
            if not str(ws[f"{c}{r}"].value).startswith("="): nonformula += 1
        put(ws, f"O{r}", f'=IF(AND(ISNUMBER(M{r}),ISNUMBER(N{r})),D{r}/((M{r}+N{r})/2),"{DASH}")', fmt="0.00")
        put(ws, f"P{r}", f'=IF(AND(ISNUMBER(M{r}),ISNUMBER(N{r})),IF(M{r}=N{r},IF(ABS(D{r}/M{r}-1)<=0.2,"±20% 內","差距 >20%"),'
                         f'IF(D{r}<M{r},"低於外部區間",IF(D{r}>N{r},"高於外部區間","落在外部區間"))),"無外部對照")')
        _nm(wb, f"L1_{key}", f"L1!$D${r}"); _nm(wb, f"L1_{key}_Lo", f"L1!$E${r}"); _nm(wb, f"L1_{key}_Hi", f"L1!$F${r}")
        r += 1
    ws.freeze_panes = "C5"
    return r - 5, nonformula


# ---------------------------------------------------------------- 8. Checks governance section (builder-owned)
def checks_gov(wb, l1_rows, l1_nonformula, static_raw_hard):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "G. 治理檢查（Stage 1 切片一，v5.11；規劃書第 5 節）：ERROR 合計必須為 0 才可合併", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]):
        put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    GM = lambda col: f"Gov_Map!${col}$5:${col}${GM_LAST}"
    srcsum = lambda col, crit: "+".join(f'COUNTIF({s}!${col}$5:${col}${SRC_LAST},"{crit}")' for s in SRC_SHEETS)
    rows = [
      ("E1", "模型頁原始數據寫死（未連結 SRC）", "ERROR", f'=COUNTIF({GM("V")},1)', "Gov_Map 類別＝原始數據、建置時狀態≠連結 SRC（G0-2 保留與切片二另計）"),
      ("E2", "Analogy 缺可比對象 SRC_ID", "ERROR", f'=COUNTIF({GM("W")},1)', "Gov_Map"),
      ("E3", "Analogy／Assumed 缺區間", "ERROR", f'=COUNTIF({GM("X")},1)', "Gov_Map；端點格（區間角色＝低／高）不另檢查"),
      ("E4", "Analogy／Assumed／Derived 缺理由", "ERROR", f'=COUNTIF({GM("Y")},1)', "Gov_Map"),
      ("E5", "Decision 格缺決策 ID", "ERROR", f'=COUNTIF({GM("Z")},1)', "Gov_Map"),
      ("E6", "決策 ID 不在 Decisions 頁", "ERROR", f'=COUNTIF({GM("AA")},1)', "Gov_Map × Decisions"),
      ("E7", "同指標、同口徑、同對象有兩筆以上 Active", "ERROR", "=" + srcsum("X", ">1"), "SRC_* X 欄（逐筆計數，重複者每筆各計 1）"),
      ("E8", "Active SRC 缺 Evidence ID", "ERROR", "=" + srcsum("Y", "1"), "SRC_* Y 欄"),
      ("E9", "模型連結的 SRC 紀錄不是 Active", "ERROR", f'=COUNTIF({GM("AB")},1)', "Gov_Map 類別＝原始數據"),
      ("E10", "基準值不在低／高之間", "ERROR", f'=COUNTIF({GM("AC")},1)', "Gov_Map 數值區間（低、高不分方向）"),
      ("E11", "L1 數值欄不是公式（貼值）", "ERROR", l1_nonformula, "建置時靜態檢查（builder）"),
      ("E12", "引用的 SRC_ID 不存在（切片一）", "ERROR", f'=COUNTIF({GM("AE")},1)', "Gov_Map"),
      ("W1", "利害關係方 Active 紀錄缺第二來源", "WARN", "=" + srcsum("Z", "1"), "SRC_* Z 欄（SemiAnalysis 規則推廣；Stage 2 補）"),
      ("W2", "3 級紀錄被 CC 高段敏感度參數使用", "WARN", f'=COUNTIF({GM("AD")},1)', "Gov_Map（CC 第 10 輪分段）"),
      ("I1", "DB_Evidence 待判定", "INFO", '=COUNTIF(DB_Evidence!$L$5:$L$500,"待判定")', "DB_Evidence L 欄"),
      ("I2", "DB_Evidence 待 Andy", "INFO", '=COUNTIF(DB_Evidence!$L$5:$L$500,"待 Andy")', "DB_Evidence L 欄"),
      ("I3", "L1 落在外部區間外或差距 >20% 的列", "INFO",
       '=COUNTIF(L1!$P$5:$P$200,"低於外部區間")+COUNTIF(L1!$P$5:$P$200,"高於外部區間")+COUNTIF(L1!$P$5:$P$200,"差距 >20%")', "L1 P 欄"),
      ("I4", "原始數據 G0-2 保留藍字（Stage 2 佇列）", "INFO", f'=COUNTIF({GM("F")},"原始數據（G0-2 保留）")', "Gov_Map"),
      ("I5", "Derived 寫死待改公式", "INFO", f'=COUNTIF({GM("F")},"Derived（待改公式）")', "Gov_Map（Arch 21–23 於 v5.12）"),
      ("I6", "結構選擇（無數值區間）", "INFO", f'=COUNTIF({GM("M")},"結構選擇（無數值區間）")', "Gov_Map"),
      ("I7", "原始數據待切片二連結", "INFO", f'=COUNTIF({GM("F")},"原始數據（切片二）")', "Gov_Map（Workload 40；Cap_In、Har_In 等頁於 v5.12 登錄）"),
      ("I8", "v5.11 標記變更（Analogy→Assumed 等）", "INFO", f'=COUNTIF({GM("O")},"<>{DASH}")-COUNTIF({GM("O")},"")', "Gov_Map O 欄；請 Andy 過目"),
    ]
    first = r; err_rows = []; warn_rows = []; info_rows = []
    for code, lab, lvl, f, note in rows:
        put(ws, f"A{r}", code); put(ws, f"B{r}", lab); put(ws, f"C{r}", lvl, F_BOLD if lvl == "ERROR" else None)
        put(ws, f"D{r}", f, F_CALC, fmt="0"); put(ws, f"E{r}", note, F_NOTE)
        {"ERROR": err_rows, "WARN": warn_rows, "INFO": info_rows}[lvl].append(r); r += 1
    put(ws, f"B{r}", "ERROR 合計（CI 讀取 GOV_Errors）", F_BOLD); put(ws, f"D{r}", "=" + "+".join(f"D{x}" for x in err_rows), F_BOLD, fmt="0", fill=FILL_KEY)
    _nm(wb, "GOV_Errors", f"Checks!$D${r}"); r += 1
    put(ws, f"B{r}", "WARN 合計", F_BOLD); put(ws, f"D{r}", "=" + "+".join(f"D{x}" for x in warn_rows), fmt="0"); _nm(wb, "GOV_Warnings", f"Checks!$D${r}"); r += 1
    put(ws, f"B{r}", "INFO 合計", F_BOLD); put(ws, f"D{r}", "=" + "+".join(f"D{x}" for x in info_rows), fmt="0"); _nm(wb, "GOV_Info", f"Checks!$D${r}"); r += 1
    put(ws, f"B{r}", f"建置時靜態檢查：Gov_Map 類別＝原始數據且為藍字常數的格數＝{static_raw_hard}（應為 0；與 E1 一致）", F_NOTE); r += 1
    _nm(wb, "GOV_Table", f"Checks!$A${first}:$D${r-5}")
    return first


# ---------------------------------------------------------------- 9. Block 1 Checks rows 4–8: external refs link to SRC (no literals)
def checks_block1(wb):
    ck = wb["Checks"]
    ck["C4"].value = '=TEXT(SRC_DC_010_Lo,"0")&"–"&TEXT(SRC_DC_010_Hi,"0")'
    ck["E4"].value = '=IF(AND(B4>=SRC_DC_010_Lo,B4<=SRC_DC_010_Hi),"落在區間",IF(B4<SRC_DC_010_Lo,"低於參照","高於參照"))'
    ck["C5"].value = "=SRC_DC_011"
    ck["E5"].value = '=IF(ABS(B5-C5)/C5<=0.2,"±20% 內","差距 >20%")'
    ck["C6"].value = '=TEXT(SRC_DC_003,"0.0")&" × "&TEXT(1+SRC_DC_004_Lo,"0.00")&"–"&TEXT(1+SRC_DC_004_Hi,"0.00")'
    ck["E6"].value = '=IF(AND(B6>=SRC_DC_003*(1+SRC_DC_004_Lo)*0.9,B6<=SRC_DC_003*(1+SRC_DC_004_Hi)*1.3),"合理區間","需檢查")'
    ck["C7"].value = "=SRC_DC_012"; ck["C8"].value = "=SRC_DC_013"
    for ref in ("C4", "C5", "C6", "C7", "C8"): ck[ref].font = F_LINK
    for r, s in ((4, "SRC_DC_010"), (5, "SRC_DC_011"), (6, "SRC_DC_003、SRC_DC_004"), (7, "SRC_DC_012"), (8, "SRC_DC_013")):
        v = str(ck[f"F{r}"].value or "")
        if "SRC_" not in v: ck[f"F{r}"].value = f"{v}［{s}］"
    ck["F19"].value = str(ck["F19"].value or "") + ("［SRC_PERF_011］" if "SRC_" not in str(ck["F19"].value or "") else "")
    ck["C19"].value = "=SRC_PERF_011"; ck["C19"].font = F_LINK


def gov_all(wb):
    made = src_sheets(wb)
    n_src_names, idx = src_refresh(wb)
    ev_added = evidence_upgrade(wb)
    dec_made = decisions_sheet(wb)
    n_fm, fm_log = apply_formula_map(wb)
    n_f14 = f14(wb)
    checks_block1(wb)
    n_gm, hard = gov_map(wb, idx)
    n_l1, nonf = l1_sheet(wb)
    checks_gov(wb, n_l1, nonf, hard)
    return dict(src_made=made, src_names=n_src_names, src_records=len(idx), evidence_added=ev_added, decisions_made=dec_made,
                formula_map_changed=n_fm, f14_changed=n_f14, gov_rows=n_gm, gov_raw_hardcoded=hard, l1_rows=n_l1, l1_nonformula=nonf,
                fm_log=fm_log)

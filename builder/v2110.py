# v21.1 (work order docs/workorders/20261023_v21.1_NonNV與免費占比路徑.md r0, branch claude/v21-1): NonNV Ascend／Maia rows, free-share time path, text fixes, contract AIM reader.
# New contract names only (10): IF_NonNV_Out_{Ascend,Maia}, IF_NonNV_Hold_{Ascend,Maia} (1x3 each), L1_FreeShare_2026／_2030, L1_RevGW_PQ_VR200_F2026／_F2030 (each + _Lo／_Hi).
#   Each is a reference to a new cell; no existing named value or formula cell changes value.
#   W1  NonNV rows 10 (Huawei Ascend 910C / CloudMatrix 384) and 11 (Microsoft Maia 200): blue inputs B:G, H:J formulas as rows 5-9, K/L/M text; rows 5-9 L tail; A1 title tail.
#   W2  Interface P section rows 379-382 (after row 378; nothing moves); A368 title tail.
#   W3  SRC_DEM_089 / SRC_DEM_090 (free share of inference compute, 2026 / 2030), DB_Evidence E402, Cap_In Q section (rows 344-348), L1 rows 145-148.
#   W4  Text only: Alloc_In G24, SRC_Demand SRC_DEM_006 W column, Interface A364.
#   W5  (outside the workbook) contract v0.25 with the AIM reader section; Decisions SL58-01; README.
# Every write to an Excel-owned cell is guarded (old text / already-applied test); the new blue inputs are restored from the workbook on rebuild.
import re

from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName

from common import put, F_NOTE, F_BOLD, F_CALC, F_LINK, F_IN, FILL_KEY
import v1000
import v1400
import v1410
import v1720
import v2000
import v2100

VERSION = "20261023_Tokenomics_v21.1"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-23"
V = "v21.1"
WO = "工作單 docs/workorders/20261023_v21.1_NonNV與免費占比路徑.md（r0）"
DEC_ID = "SL58-01"
EID = "E402"
SRC26, SRC30 = "SRC_DEM_089", "SRC_DEM_090"
U = "AL_UnavailTxt"
DASH = "—"
DEC_BY = ("Andy 2026-10-23 13:52–13:56（經雲端 CC 轉達）NonNV Q1–Q4；14:22 利用率／服務占比 J1–J8 照預設；14:51「當然要放」（免費占比時間路徑）；"
          "13:12「J one J two 都同意」（AIM 外部單向連接，契約加 AIM 讀者）；交接檔 0m（v21.1 範圍 1–5）。"
          "證據：docs/evidence/20261023_NonNV昇騰Maia_A段（PR #149）、docs/evidence/20261023_利用率服務占比_A段（PR #151、#152）。"
          "判斷題 J1（免費占比區間）、J2（情境列兩列）於 15:40 提給 Andy，未回應，依工作單預設建置（可撤回）")

# ================================================================== W1: NonNV rows 10 and 11
NONNV_NEW = [      # (row, display name, out low/base/high, hold low/base/high, mark, L text, M text)
    (10, "華為昇騰 910C（CloudMatrix 384）", (0.05, 0.08, 0.15), (0.45, 0.55, 0.70),
     "代表 910C／CloudMatrix 384（Andy 2026-10-23 Q1；950 世代已發表但無實測、功率與出貨確證，待資料齊備另列）。"
     "產出比：每 kW 峰值算力比 × 效率因子，與實測錨定法（模型 Hopper × 每 kW 顆數比 × 每顆實測 token 比）兩法同源，基準取平均、區間取包絡。"
     "整機功率 559 kW 為單一來源（SemiAnalysis 系），各轉述 559–600 kW；China Research Collective 估計 350–500 kW（官方未揭露；取低值時產出比可達約 0.13），"
     "未經第二來源驗證，故保留寬區間、基準暫維持 0.08。持有比依每 kW 設備價推導（1 − 0.77 ×（1 − 每 GW IT capex ÷ VR200））。"
     "證據：docs/evidence/20261023_NonNV昇騰Maia_A段（PR #149）。",
     "已接 Interface P 節（v21.1）：IF_NonNV_Out_Ascend／IF_NonNV_Hold_Ascend（第 10 列）；H:J 欄未接線"),
    (11, "Microsoft Maia 200", (0.25, 0.55, 0.75), (0.40, 0.50, 0.60),
     "產出比＝每 kW 峰值算力比（約 VR200 的 0.68）× 軟體效率因子 0.45–1.0（無第三方實測，主要不確定）。"
     "機架價格無公開資料，以 Assumed 區間 $0.5／0.8／1.2M 每機架推導持有比（Andy 2026-10-23 Q3）；持有比依每 kW 設備價推導。"
     "微軟自述『每瓦 token 為領先 GPU 的 1.7 倍』視為行銷口徑，未採用。證據：同上（PR #149）。",
     "已接 Interface P 節（v21.1）：IF_NonNV_Out_Maia／IF_NonNV_Hold_Maia（第 11 列）；H:J 欄未接線"),
]
ROWS_5_9_TAIL = "持有比為慣例值（Block 1『接近 1』），未推導；找到 TPU v7、Trainium3 機架功率後以每 kW 設備價法重推（Andy 2026-10-23 Q2）。"
NONNV_A1_OLD = "未接線（MAG、智譜、AI 半導體待用；目前不進任何輸出）"
NONNV_A1_NEW = "B:G 已接 Interface P 節；H:J 未接線"


def nonnv_rows(wb):
    """Called right after nonnv(wb) (before restore, so the new blue inputs are restored from the workbook on a rebuild)."""
    ws = wb["NonNV"]
    for r, name, out, hold, note, _m in NONNV_NEW:
        assert ws[f"A{r}"].value is None, (r, ws[f"A{r}"].value)
        put(ws, f"A{r}", name)
        for c, v in zip("BCDEFG", list(out) + list(hold)):
            put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"H{r}", f"=F{r}/C{r}", fmt="0.00", fill=FILL_KEY)
        put(ws, f"I{r}", f"=E{r}/D{r}", fmt="0.00"); put(ws, f"J{r}", f"=G{r}/B{r}", fmt="0.00")
        put(ws, f"K{r}", "Assumed", F_NOTE); put(ws, f"L{r}", note, F_NOTE)
    return len(NONNV_NEW)


def nonnv_text(wb, append_text):
    ws = wb["NonNV"]
    n = 0
    for r, _name, _o, _h, _note, mtxt in NONNV_NEW:
        if ws[f"M{r}"].value != mtxt:
            ws[f"M{r}"].value = mtxt; n += 1
    for r in range(5, 10):
        n += int(bool(append_text(ws[f"L{r}"], "｜" + ROWS_5_9_TAIL)))
    a1 = str(ws["A1"].value)
    if NONNV_A1_NEW not in a1:
        assert NONNV_A1_OLD in a1, a1
        ws["A1"].value = a1.replace(NONNV_A1_OLD, NONNV_A1_NEW); n += 1
    return n


# ================================================================== W2: Interface P section rows 379-382, A368 / A364 text
P_TITLE_OLD = "昇騰、Maia 待證據後於 v21.1 加入"
P_TITLE_NEW = "昇騰（910C／CM384）、Maia 200 於 v21.1 加入（第 379–382 列；持有比依每 kW 設備價推導，既有五列為慣例值）"
NEW_IF = [("Out", "Ascend", 10), ("Out", "Maia", 11), ("Hold", "Ascend", 10), ("Hold", "Maia", 11)]
NEW_NAMES_IF = [f"IF_NonNV_{k}_{s}" for k, s, _ in NEW_IF]


def interface_op_ext(wb):
    ws = wb["Interface"]
    r = wb.defined_names["IF_NonNV_Hold_OAI"].attr_text
    last = int(r.split("$")[-1])
    assert last == 378 and ws.max_row == 378, (last, ws.max_row)
    made = []
    row = last + 1
    for kind, stem, nrow in NEW_IF:
        nm = f"IF_NonNV_{kind}_{stem}"
        full = wb["NonNV"][f"A{nrow}"].value
        c0, ulab = (("B", "產出比（每 GW 產出 ÷ VR200）") if kind == "Out" else ("E", "持有成本比（每 GW 持有成本 ÷ VR200）"))
        put(ws, f"A{row}", f"{full}：{ulab}（NonNV 第 {nrow} 列 {'B:D' if kind == 'Out' else 'E:G'}；同層級、同 SLO；Assumed；C＝低、D＝基準、E＝高）　[{nm}]")
        put(ws, f"B{row}", "比（÷ VR200）")
        for j in range(3):
            put(ws, f"{L(3 + j)}{row}", f"=NonNV!${L(ord(c0) - 64 + j)}${nrow}", fmt="0.00")
        wb.defined_names[nm] = DefinedName(nm, attr_text=f"Interface!$C${row}:$E${row}")
        made.append((nm, row)); row += 1
    t = str(ws["A368"].value)
    if P_TITLE_NEW not in t:
        assert P_TITLE_OLD in t, t
        ws["A368"].value = t.replace(P_TITLE_OLD, P_TITLE_NEW)
    return dict(made=made)


def rack_label_fix(wb):
    """W4-3: Interface A364 (IF_RackPrice) mark sentence by generation, from Spec_Rack C17:G17 as they stand; Rubin Ultra multiplier base."""
    sr, ws = wb["Spec_Rack"], wb["Interface"]
    marks = [sr[f"{c}17"].value for c in "CDEFG"]
    assert all(isinstance(m, str) and m for m in marks), marks
    gens = ("Hopper", "GB200", "GB300", "VR200", "Rubin Ultra")
    new_sent = "標記（Spec_Rack 第 17 列，依世代）：" + "；".join(f"{g} {m}" for g, m in zip(gens, marks))
    r = int(wb.defined_names["IF_RackPrice"].attr_text.split("$")[-1])
    assert r == 364
    t = str(ws[f"A{r}"].value)
    if new_sent in t:
        return 0
    m = re.search(r"標記沿用 Spec_Rack 第 17 列：[^；]*；", t)
    assert m, t
    t = t.replace(m.group(0), new_sent + "；")
    ru_old = "價格為 VR200 機架價 × 倍數（Assumed，無公開報價）"
    ru_new = "價格為 VR200 機架價 × 倍數（Assumed，無公開報價）；基準倍數 2.0（Spec_Rack G12＝F12 × 2）"
    assert ru_old in t, t
    ws[f"A{r}"].value = t.replace(ru_old, ru_new)
    return 1


# ================================================================== W4: Alloc_In G24, SRC_DEM_006
G24_OLD_START = "純利用率＝平均 token 吞吐 ÷ 容量；0.41＝原 0.35 ÷ 生產折減 0.85。區間 0.3–0.65"
G24_NEW = ("純利用率＝平均 token 吞吐 ÷ 容量；0.41＝原 0.35 ÷ 生產折減 0.85。無直接量測（2026-10-23 查證，PR #151／#152）："
           "類比 Azure 尖峰／平均換算 0.25–0.59，非量測；Aegaeon 長尾專屬實例 0.13–0.34 為低端旁證；上端 0.65 為單一模型集中式服務代理值（DeepSeek 2025-02，0.54–0.65）。"
           "消費端（Cap_In 第 114、218、255 列）乘 CTL_ProdDerate。暫定、待證據。")
DEM006_PREFIX = "出處待補；已排除 The Information 2026-02〈Why OpenAI, Anthropic Missed Their Own Gross Margin Forecasts〉（2026-10-23 查證 J5）｜"


def text_fixes(wb):
    n = 0
    ws = wb["Alloc_In"]
    assert ws["A24"].value == "實際利用率（純；不含生產折減）", ws["A24"].value
    if ws["G24"].value != G24_NEW:
        assert str(ws["G24"].value).startswith(G24_OLD_START), ws["G24"].value
        ws["G24"].value = G24_NEW; n += 1
    sd = wb["SRC_Demand"]
    rr = [r for r in range(5, sd.max_row + 1) if sd.cell(r, 1).value == "SRC_DEM_006"]
    assert len(rr) == 1 and rr[0] == 10, rr
    w = str(sd["W10"].value)
    if not w.startswith(DEM006_PREFIX):
        sd["W10"].value = DEM006_PREFIX + w; n += 1
    n += rack_label_fix(wb)
    return n


# ================================================================== W3-2: Cap_In Q section
ROWS = {}
PURPOSE_MARKS = {}
SEC_TITLE = ("Q. 免費占比時間路徑（v21.1；" + WO + "）：OpenAI 投資人資料預估的非付費用戶推論占比隨時間下降（2026 約 34%、2030 約 6%）；"
             "口徑同 B4_Free（本頁 C29）；只供情境與下游讀取，不回流 B4_Free。欄位：C 基準／D 低端／E 高端；F 標記、G 說明")
G_FREE = ("口徑同 B4_Free（Cap_In C29，支出口徑：非付費用戶推論 ÷ 推論）。2026 高端＝2025 值 0.46（不下降）；2030 區間放寬，因四年外的利害關係方預估。"
          "不回流：B4_Free 0.46 不變（本節只供情境與下游讀取）。抵銷提醒：『付費』可能含 5–8 美元廣告方案，付費占比上升時 m 可能同時下降。")
G_MULT = ("(1 − F_t) ÷ (1 − B4_Free)：把 2025 支出口徑的付費占比換成預估年的倍數。方向：F 高 → 付費占比低 → 倍數低，所以 D（低）欄用 F 的高端（E 欄）、E（高）欄用 F 的低端（D 欄）。"
          "L1 第 147／148 列只乘 C 欄基準（利用率區間另計），D／E 欄供讀者核對倍數區間")


def _num(*xs):
    return ",".join(f"ISNUMBER({x})" for x in xs)


def cap_in_q(wb, p_sec):
    ws = wb["Cap_In"]
    r0 = p_sec["end"] + 1
    assert ws.max_row == p_sec["end"] == 343, (ws.max_row, p_sec["end"])
    put(ws, f"A{r0}", SEC_TITLE, F_BOLD, wrap=True)
    R = ROWS
    R["f26"], R["f30"], R["m26"], R["m30"] = r0 + 1, r0 + 2, r0 + 3, r0 + 4
    assert R["f26"] == 345 and R["m30"] == 348, R
    for k, yr, sid, lo, hi in (("f26", 2026, SRC26, 0.25, 0.46), ("f30", 2030, SRC30, 0.03, 0.30)):
        r = R[k]
        put(ws, f"A{r}", f"免費服務占服務 — {yr}（投資人資料預估）　→ L1_FreeShare_{yr}", wrap=True); put(ws, f"B{r}", "%")
        put(ws, f"C{r}", f"={sid}", F_LINK, fmt="0%")
        put(ws, f"D{r}", lo, F_IN, fmt="0%"); put(ws, f"E{r}", hi, F_IN, fmt="0%")
        put(ws, f"F{r}", "Interested-party（區間：Assumed）", F_NOTE); put(ws, f"G{r}", G_FREE, F_NOTE, wrap=True)
    for k, yr, fk in (("m26", 2026, "f26"), ("m30", 2030, "f30")):
        r, f = R[k], R[fk]
        d = lambda x: f"IF(AND({_num(x, 'B4_Free')}),IF(1-B4_Free>0,(1-{x})/(1-B4_Free),{U}),{U})"
        put(ws, f"A{r}", f"付費服務倍數 (1 − F{yr}) ÷ (1 − B4_Free) — {yr}（D 欄用 F 高端、E 欄用 F 低端：F 高 → 倍數低）　→ L1_RevGW_PQ_VR200_F{yr}", wrap=True)
        put(ws, f"B{r}", "x")
        put(ws, f"C{r}", "=" + d(f"C{f}"), F_CALC, fmt="0.0000", fill=FILL_KEY)
        put(ws, f"D{r}", "=" + d(f"E{f}"), F_CALC, fmt="0.0000"); put(ws, f"E{r}", "=" + d(f"D{f}"), F_CALC, fmt="0.0000")
        put(ws, f"F{r}", "Derived", F_NOTE); put(ws, f"G{r}", G_MULT, F_NOTE, wrap=True)
        PURPOSE_MARKS[r] = f"C{r} 進 L1 第 {145 + 2 + (0 if yr == 2026 else 1)} 列；D／E 欄顯示用（倍數區間，不進任何輸出）"
    return dict(start=r0, end=R["m30"], rows=dict(R))


def purpose_marks(wb):
    ws = wb["Cap_In"]
    pc = v1400._purpose_col(ws, create=False)
    assert pc is not None, "用途 column of Cap_In not found"
    for rr, txt in PURPOSE_MARKS.items():
        put(ws, f"{L(pc)}{rr}", txt, F_NOTE)
    return len(PURPOSE_MARKS)


# ================================================================== Gov_Map rows (blue inputs)
def gov_map_rows(wb):
    if not ROWS:
        return []
    out = []
    sc = "切片三（v21.1 NonNV 昇騰／Maia、免費占比路徑）"

    def ent(sheet, row, cell, role, cls, lo, hi, rtext, reason, dec=DEC_ID):
        lab = wb[sheet][f"A{row}"].value
        out.append({'scope': sc, 'sheet': sheet, 'cell': cell, 'label': lab, 'check': lab, 'cls': cls, 'role': role, 'src': '', 'rel': '', 'dec': dec,
                    'lo': lo, 'hi': hi, 'rtext': rtext, 'reason': reason, 'retag': '', 'seg': '無'})

    # NonNV rows 10, 11: same registration shape as GM385–GM414 (rows 5–9): base cells carry the ends as formulas, end cells point to the L note
    for r, *_ in NONNV_NEW:
        ent("NonNV", r, f"C{r}", "基準", "Assumed", f"=NonNV!B{r}", f"=NonNV!D{r}", '', f"=NonNV!$L${r}")
        ent("NonNV", r, f"F{r}", "基準", "Assumed", f"=NonNV!E{r}", f"=NonNV!G{r}", '', f"=NonNV!$L${r}")
        for c, role in (("B", "低"), ("D", "高"), ("E", "低"), ("G", "高")):
            ent("NonNV", r, f"{c}{r}", role, "Assumed", None, None, '', f"=NonNV!$L${r}")
    for k, yr in (("f26", 2026), ("f30", 2030)):
        r = ROWS[k]
        ent("Cap_In", r, f"D{r}:E{r}", "低／高", "Assumed", None, None, f"C{r} 的低、高端點",
            f"v21.1 W3（{DEC_ID}）：免費占比 {yr} 預估的區間端點（Assumed）。" + ("2026 高端＝2025 值 0.46（不下降）；低端 0.25 為預設。" if yr == 2026 else "2030 區間放寬（0.03–0.30），因四年外的利害關係方預估。")
            + "區間端點值以判斷題 J1 的答覆為準（未答覆用此預設）。只進 L1_FreeShare_* 的低／高，不回流 B4_Free")
    return out


# ================================================================== SRC (SRC_Demand) records
def src_new_records(wb):
    base = ("The Information（付費牆，未讀原文）；二手轉述：BigGo 2026-02-25、WallStreetCN 2026-02-26")
    recs = []
    for sid, yr, val, pay in ((SRC26, 2026, 0.34, 66), (SRC30, 2030, 0.06, 94)):
        rec = v1720._rec(
            sid, "SRC_Demand", f"OpenAI 非付費用戶占推論算力（{yr} 預估）", val, None, None, "比例", f"{yr} 預估；非付費用戶推論 ÷ 推論（付費 {pay}%）", "OpenAI",
            f"{yr}（預估；來源發表 2026-02）", base, 3, "利害關係方", "投資人資料，有呈現付費率上升的誘因",
            "二手", f"Cap_In!C{345 if yr == 2026 else 346}｜情境列（L1_FreeShare_{yr}；不回流 B4_Free）",
            f"{V} W3：OpenAI 投資人資料預估，非付費用戶占推論算力 {yr} 約 {round(val * 100)}%（付費 {pay}%）；兩份轉述同引一個原文，不互為獨立；"
            f"原文付費牆未讀。只作免費占比時間路徑的情境列，不改 B4_Free（0.46）（{WO}）")
        rec.update(status="Active", s="U-V2110", ev=EID)
        recs.append(rec)
    return recs


# ================================================================== L1 rows 145-148
NONE_EXT = ("無外部對照", DASH, DASH)
FREE_READ = ("v21.1：利害關係方預估的免費占比時間路徑（口徑同 B4_Free：非付費用戶推論 ÷ 推論）；不回流 B4_Free（0.46 不變），只供情境與下游讀取。"
             "『付費』可能含 5–8 美元廣告方案，付費占比上升時 m 可能同時下降（未建模）。")
SCEN_H = ("情境列（F 隨時間下降）；只把（1 − F）換成 {y} 預估，其餘同 L1_RevGW_PQ_VR200；低／高＝利用率 0.30／0.65（同第 129 列），"
          "F 的區間見 L1_FreeShare_* 與 Cap_In 第 347–348 列 D／E 欄")
SCEN_S = "token 帳未閉合；m 可能隨廣告方案下降（未建模）；利害關係方預估"


def _guard(args, expr):
    return f"=IF(AND({_num(*args)}),{expr},{U})"


def l1_rows_new():
    R = ROWS
    rows = []
    for k, yr, sid in (("f26", 2026, SRC26), ("f30", 2030, SRC30)):
        r = R[k]
        rng = "低 0.25／高 0.46（2026 高端＝2025 值，不下降）" if yr == 2026 else "低 0.03／高 0.30（四年外預估，區間放寬）"
        rows.append((f"FreeShare_{yr}", f"免費服務占服務 — {yr}（OpenAI 投資人資料預估；情境輸入）",
                     f"＝Cap_In 第 {r} 列（C 基準＝{sid}）；口徑同 B4_Free", f"=Cap_In!$C${r}", f"=Cap_In!$D${r}", f"=Cap_In!$E${r}", "比例",
                     f"Cap_In 第 {r} 列 D／E 欄（Assumed 區間）：{rng}", FREE_READ, f"Cap_In 第 {r} 列（{sid}）", "Interested-party（區間：Assumed）",
                     *NONE_EXT, sid, f"Cap_In 第 {r} 列", "利害關係方預估；The Information 原文付費牆未讀；兩份轉述同源"))
    for k, yr, mk, fk in (("m26", 2026, "m26", "f26"), ("m30", 2030, "m30", "f30")):
        r, fr = R[mk], R[fk]
        base = "L1_RevGW_PQ_VR200"
        f = lambda nm: _guard((nm, f"Cap_In!$C${r}"), f"{nm}*Cap_In!$C${r}")
        rows.append((f"RevGW_PQ_VR200_F{yr}", f"VR200 每 GW 營收 P × Q — 第一年（情境：免費占比 {yr} 預估；主口徑 m）",
                     f"＝L1_RevGW_PQ_VR200 × Cap_In 第 {r} 列 C 欄（(1 − F{yr}) ÷ (1 − B4_Free)）", f(base), f(base + "_Lo"), f(base + "_Hi"), "$B/GW/年",
                     SCEN_H.format(y=yr),
                     f"v21.1：把主列 L1_RevGW_PQ_VR200 的（1 − 免費占比）由 2025 的 B4_Free 換成 {yr} 預估（Cap_In 第 {fr} 列），其餘（單價、m、利用率、生產折減、服務占比）同主列。"
                     "(1) 不回流：不改任何既有名稱；(2) 僅情境，非預測：免費占比取利害關係方預估；(3) 付費占比上升時 m 可能同時下降（廣告方案），未建模，故本列可能高估。",
                     f"L1_RevGW_PQ_VR200、Cap_In 第 {r} 列 C 欄", "免費占比：Interested-party（區間：Assumed）；利用率：Assumed",
                     *NONE_EXT, f"{base}；Cap_In 第 {r} 列", "L1 本頁", SCEN_S))
    return rows


KEYS = ["FreeShare_2026", "FreeShare_2030", "RevGW_PQ_VR200_F2026", "RevGW_PQ_VR200_F2030"]
NEW_L1 = [f"L1_{k}{s}" for k in KEYS for s in ("", "_Lo", "_Hi")]
SCENARIO = "情境"
v1000._n(v1000.E_, "利害關係方預估值（輸入轉讀；免費占比時間路徑），非推導", "FreeShare_2026", "FreeShare_2030")
v1000._n(SCENARIO, "情境：主列 L1_RevGW_PQ_VR200 只把（1 − 免費占比）換成預估年的值；預估為利害關係方資料，不是觀測或推導（v21.1）",
         "RevGW_PQ_VR200_F2026", "RevGW_PQ_VR200_F2030")


def clear_l1_ratio(wb):
    """L1 column O (推算 ÷ 外部) has no external value on the new rows: cleared like the other external-less rows (no dead formula cells)."""
    ws = wb["L1"]; n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value in {f"L1_{k}" for k in KEYS} and ws[f"O{r}"].value is not None:
            ws[f"O{r}"].value = None; n += 1
    return n


def l1_header(wb):
    ws = wb["L1"]
    t4 = str(ws["T4"].value)
    if SCENARIO not in t4:
        ws["T4"].value = t4.replace("觀測比值）", "觀測比值／情境）") if "觀測比值）" in t4 else t4 + "（v21.1 增情境）"
        return 1
    return 0


# ================================================================== DB_Evidence E402, Decisions SL58-01
EVIDENCE = [EID, DATE, "OpenAI 非付費用戶占推論算力：2026 約 34%（付費 66%）、2030 約 6%（付費 94%）（投資人資料預估）",
            "The Information（付費牆，未讀原文）；二手轉述：BigGo 2026-02-25、WallStreetCN 2026-02-26；chat 端查證 2026-10-23（本代理依工作單，未外部搜尋）",
            "Interested-party（OpenAI 投資人資料）", "Cap_In 第 345–348 列；L1_FreeShare_2026／_2030、L1_RevGW_PQ_VR200_F2026／_F2030（情境列，不回流）",
            "B4_Free 0.46（2025，支出口徑；SRC_DEM_004／005）", "2026：0.34（SRC_DEM_089）；2030：0.06（SRC_DEM_090）", "採用（情境列；V21.1 W3）",
            V, "投資人資料有呈現付費率上升的誘因；兩份轉述同引一個原文，不互為獨立；不回流 B4_Free；『付費』可能含廣告方案，m 可能同時下降｜" + WO, "已處理",
            f"{SRC26}／{SRC30}", DASH, "L1_FreeShare_2026／_2030；L1_RevGW_PQ_VR200_F2026／_F2030", 3, "利害關係方", "採用（情境列）｜v21.1 新增列"]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    if any(ws.cell(r, 1).value == EID for r in range(5, ws.max_row + 1)):
        return 0
    r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
    assert ws.cell(r - 1, 1).value == "E401", ws.cell(r - 1, 1).value
    for i, v in enumerate(EVIDENCE):
        put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 17))
    return 1


def _decisions():
    return [[DEC_ID, V, "v21.1 NonNV 新增昇騰／Maia、免費占比時間路徑、說明欄修正、契約加 AIM 讀者",
             "W1：NonNV 第 10 列（華為昇騰 910C／CloudMatrix 384；產出 0.05／0.08／0.15、持有 0.45／0.55／0.70）與第 11 列（Microsoft Maia 200；產出 0.25／0.55／0.75、持有 0.40／0.50／0.60），皆 Assumed；"
             "W2：Interface P 節第 379–382 列 IF_NonNV_Out_／Hold_ × Ascend／Maia；"
             "W3：SRC_DEM_089／090（免費占比 2026 約 34%、2030 約 6%）、Cap_In Q 節（第 344–348 列）、L1_FreeShare_2026／_2030、L1_RevGW_PQ_VR200_F2026／_F2030（情境列，不回流，B4_Free 0.46 不變）；"
             "W4（只改文字）：Alloc_In G24、SRC_DEM_006 出處待補、Interface A364 標記依世代；W5（活頁簿外）：下游契約 v0.25（AIM 讀者一節）。"
             "新增 10 個契約名稱，既有名稱數值不變。Andy 原話與依據：" + DEC_BY,
             DATE, DEC_BY, "v21.1 已建", "NonNV 第 10–11 列；Interface 第 379–382 列；Cap_In 第 344–348 列；L1 第 145–148 列；SRC_Demand SRC_DEM_089／090；DB_Evidence E402",
             f"{WO} W1–W5", "否"]]


def apply(wb, append_text):
    log = {}
    log["nonnv_text"] = nonnv_text(wb, append_text)
    log["text_fixes"] = text_fixes(wb)
    log["purpose"] = purpose_marks(wb)
    log["l1_o_cleared"] = clear_l1_ratio(wb)
    log["l1_header"] = l1_header(wb)
    log["evidence"] = evidence_append(wb)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README
NEW_NAMES = NEW_NAMES_IF + NEW_L1
README_VERSION = (VERSION + "（主版：" + WO + "——NonNV 新增第 10 列（華為昇騰 910C／CloudMatrix 384）與第 11 列（Microsoft Maia 200）；Interface P 節第 379–382 列 IF_NonNV_Out_／IF_NonNV_Hold_ × Ascend／Maia；"
                  "Cap_In Q 節「免費占比時間路徑」（第 344–348 列；SRC_DEM_089／090）；L1 第 145–148 列 L1_FreeShare_2026／_2030 與情境列 L1_RevGW_PQ_VR200_F2026／_F2030；"
                  "Alloc_In G24、SRC_DEM_006、Interface A364 說明文字修正；Decisions SL58-01；DB_Evidence E402。新增 10 個契約名稱，既有名稱的值全部不變。）以下為 "
                  + v2100.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v2100.README_TITLE
README_TITLE = V + _T[len(v2100.V):]
README_ROW = ("v21.1 NonNV 昇騰／Maia 與免費占比路徑",
              "NonNV 第 10 列昇騰 910C（CloudMatrix 384）、第 11 列 Maia 200（Assumed）；Interface P 節新增 IF_NonNV_Out_／IF_NonNV_Hold_ × Ascend／Maia（第 379–382 列）。"
              "Cap_In Q 節（第 344–348 列）與 L1 第 145–148 列：OpenAI 投資人資料預估的免費占比時間路徑（2026 約 34%、2030 約 6%；L1_FreeShare_*）與情境列 L1_RevGW_PQ_VR200_F2026／_F2030"
              "（只把 1 − 免費占比換成預估年的值；不回流，B4_Free 0.46 不變）。細節見工作單 docs/workorders/20261023_v21.1_NonNV與免費占比路徑.md 與 Decisions SL58-01。")

# v6.1 (work order docs/workorders/20261015_稽核修正3B.md r0): audit-fix batch 3B — input values D3, D6, D10, D13, Q3, Q6 (minor version).
#   D3  Alloc_In rows 9–12 low／high = 2025 full-year average ranges (base 0.6／0.4／0／0 unchanged); marker Derived; new parity scenario h_alloc_mix_2025ye.
#   D6  Calib C67 (Hopper eta_d multiple) 1.5 -> 1.2, range 0.8–1.6, Gov_Map row 345 Analogy -> Derived. Calib C68 is NOT changed (listed for Project).
#   D10 Alloc_In pricing multiple 1.3／1／1.6 -> 0.85／0.73／1.17 (economic basis), marker Derived.
#   D13 (1) Alloc_In pure utilisation 0.35／0.3／0.4 -> 0.41／0.3／0.65 (label renamed); (2) THE ONLY FORMULA CHANGE: Cap_In rows 114／218／255 read
#       (AL_UtilActual*CTL_ProdDerate) instead of AL_UtilActual (builder-owned formulas, so the builder specs are patched: patch_specs()); (3) Serving C17／C18／C28
#       keep their values, markers Assumed, ranges registered, "暫定、待證據（D13）".
#   Q3  Har_In C61／D61 0.5／1 -> 0.7／1.7; Train_In row 34 and Har_In row 12 only get their ranges registered (bases unchanged, R1).
#   Q6  Y7: Spec_Rack C16 note rewritten (values unchanged); Y4: Inputs H9／H17／H19 notes (no new parameter). SRC_HW is NOT extended (see report: 待 Project 判斷).
# Every write to an Excel-owned cell is guarded (cell still holds its v6.0 value／text), like v518–v600, so a rebuild never overwrites a later Excel edit.
from openpyxl.styles import PatternFill
from common import put, F_IN
import v518
import v529
import v533
import v534
import v536
import v600

VERSION = "20261015_Tokenomics_v6.1"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-15"
V = "v6.1"
WO = "工作單 docs/workorders/20261015_稽核修正3B.md r0"
DEC = "docs/reports/20261015_稽核判斷會議_決定.md"
EVID = "docs/reports/20261015_稽核修正3A_查證.md"
ANDY = "Andy 2026-10-15 稽核判斷會議逐題決定與補充決定（" + DEC + " 第 1、4 節）"
DASH = "—"

# ================================================================== labels / notes of the D13-2 formula change
LAB_UTIL_NEW = "實際利用率（純；不含生產折減）"
LAB_CORR = "利用率修正（點估計）＝AL_UtilActual × CTL_ProdDerate ÷ IF_Util"
NOTE_CORR = ("Alloc 第 22 列已含 IF_Util（0.6），換成純利用率（Alloc_In C24）× 生產折減（CTL_ProdDerate，Serving C28）；"
             "m 低端取 C24 高端、高端取 C24 低端（D13；v6.1 起乘生產折減，v6.0 的 C24 為已含折減的 0.35）")
LAB_GW_H10 = "支出路線服務 GW ÷ 計價倍數 × 利用率修正 × κ＝推論支出 ÷ 持有成本 ÷ AL_SpendBasis ×（AL_UtilActual × CTL_ProdDerate）÷ IF_Util × AL_Kappa"
LAB_IDENT = "缺口恆等式：L1_ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × 生產折減 × κ））"
UC = "(AL_UtilActual*CTL_ProdDerate)"
UC_Hi = "(AL_UtilActual_Hi*CTL_ProdDerate)"
UC_Lo = "(AL_UtilActual_Lo*CTL_ProdDerate)"

SNAP_MOVES = [(("Alloc_In", (v529.LAB_UTIL_OLD, 0), c), ("Alloc_In", (v529.LAB_UTIL, 0), c)) for c in (3, 4, 5)]      # build.py: the Excel values follow the renamed label

_PATCHED = False


def patch_specs():
    """D13-2: Cap_In row 114 (v533.SPEC corr_pt), row 218 (v534.SPEC_H10 q_gw, already patched by v536.patch_specs) and row 255 (v536.SPEC_J j_ident) multiply by CTL_ProdDerate."""
    global _PATCHED
    if _PATCHED: return
    sp = v533.SPEC
    i = next(k for k, it in enumerate(sp) if it[0] == "corr_pt")
    t = sp[i]
    assert t[3] == "=AL_UtilActual/IF_Util", t[3]
    sp[i] = ("corr_pt", LAB_CORR, t[2], f"={UC}/IF_Util", f"={UC_Hi}/IF_Util", f"={UC_Lo}/IF_Util", t[6], NOTE_CORR)
    sp = v534.SPEC_H10
    j = next(k for k, it in enumerate(sp) if it[0] == "q_gw")
    t = sp[j]
    assert "AL_UtilActual/IF_Util*AL_Kappa" in t[3] and t[1] == v536.LAB_GW_H10, (t[1], t[3])
    sp[j] = ("q_gw", LAB_GW_H10, t[2], *v534._h10_cols("={c}{q_spend}/{c}{q_hold}/AL_SpendBasis*" + UC + "/IF_Util*AL_Kappa"), t[7],
             t[8] + "；v6.1 D13：利用率修正乘 CTL_ProdDerate")
    sp = v536.SPEC_J
    k = next(k for k, it in enumerate(sp) if it[0] == "j_ident")
    t = sp[k]
    SLO = v536.SLO
    f = (f'=IF(AND(ISNUMBER(L1_ScaleServe),ISNUMBER(AL_SpendBasis),ISNUMBER(AL_UtilActual),ISNUMBER(CTL_ProdDerate),ISNUMBER(AL_Kappa)),'
         f'L1_ScaleServe/(AL_SpendBasis*IF_Util/({UC}*AL_Kappa)),"{SLO}")')
    sp[k] = ("j_ident", LAB_IDENT, t[2], f, t[4], t[5], t[6], t[7] + "；v6.1 D13：分母的實際利用率乘 CTL_ProdDerate（與第 114 列一致，驗算差仍須為 0）")
    _PATCHED = True


# ================================================================== guarded value writes (Excel-owned cells)
def _chk(ws, addr, label):
    assert ws[f"A{addr[1:]}"].value == label, (ws.title, addr, ws[f"A{addr[1:]}"].value, label)


def inputs_update(wb):
    """Each value is written only while the cell still holds its v6.0 value (gov.gm_update rule)."""
    log = []

    def setv(sh, addr, old, new, tag):
        c = wb[sh][addr]
        if c.value is not None and type(c.value) is not bool and c.value == old:
            c.value = new; log.append(f"{sh}!{addr}: {old} -> {new} ({tag})")

    ai = wb["Alloc_In"]
    mixlab = ["服務世代組合：Hopper", "服務世代組合：GB200", "服務世代組合：GB300", "服務世代組合：VR200"]
    D3 = [(9, 0, 0.5, 1, 0.7), (10, 0, 0.25, 1, 0.4), (11, 0, 0, 1, 0.1), (12, 0, 0, 1, 0)]
    for (r, dold, dnew, eold, enew), lab in zip(D3, mixlab):
        _chk(ai, f"C{r}", lab)
        setv("Alloc_In", f"D{r}", dold, dnew, "v6.1 D3"); setv("Alloc_In", f"E{r}", eold, enew, "v6.1 D3")
    rs = v529._row_by_label(ai, v529.LAB_SPEND)
    for col, old, new in (("C", 1.3, 0.85), ("D", 1, 0.73), ("E", 1.6, 1.17)):
        setv("Alloc_In", f"{col}{rs}", old, new, "v6.1 D10")
    ru = v529._row_by_label(ai, v529.LAB_UTIL)
    for col, old, new in (("C", 0.35, 0.41), ("D", 0.3, 0.3), ("E", 0.4, 0.65)):
        setv("Alloc_In", f"{col}{ru}", old, new, "v6.1 D13-1")
    cb = wb["Calib"]
    _chk(cb, "C67", "η_d 倍數")
    setv("Calib", "C67", 1.5, 1.2, "v6.1 D6")
    hi = wb["Har_In"]
    _chk(hi, "C61", "輪數倍數")
    setv("Har_In", "C61", 0.5, 0.7, "v6.1 Q3"); setv("Har_In", "D61", 1, 1.7, "v6.1 Q3")
    return log


# ================================================================== guarded text writes: (sheet, cell, old, new)
G_MIX = ("2025 全年平均（3A 查證 Q1；Blackwell 自 Q2 線性爬升、GB300 只有 Q4 有量）；年底組合見情境 h_alloc_mix_2025ye；無 OpenAI 直接揭露"
         "｜本列低／高：{lohi}（v6.1 D3；基準 0.6／0.4／0／0 不變）")
_G9_OLD = "補充 2：2025 機隊含 Hopper（基準 0；h_alloc_mix_2025 情境為 Hopper 60%／GB200 40%） ｜v5.33 J8：2025 基準年實際組合（VR200 2025 未出貨；h_alloc_mix_2025 情境轉為基準：Hopper 60／GB200 40／GB300 0／VR200 0；低／高區間不改）"
_G10_OLD = "8f 驅動表：服務機隊的世代組合（四者合計 100%）"
_G11_OLD = "同上 ｜v5.33 J8：2025 基準年實際組合（VR200 2025 未出貨；h_alloc_mix_2025 情境轉為基準：Hopper 60／GB200 40／GB300 0／VR200 0；低／高區間不改）"
G23_OLD = "X14 (m)／E262：支出路線的推論支出為 Azure 計價（含 Microsoft 利潤與資本回收），對持有成本口徑的倍數無公開數字；已搜尋未找到 OpenAI 對 Azure 實付單價"
G23_NEW = ("經濟口徑：依據的價格 ÷ 會計成本 1.16 × 會計 ÷ 經濟持有成本 0.73 ≈ 0.85（區間 0.73–1.17）；分母維持經濟口徑持有成本。"
           "小於 1 表示 Azure 計價未涵蓋全部資本成本，這本身是 m 的一項實質命題（決定紀錄 D10）")
G24_OLD = "X14 (m)／E262：實際利用率 × 生產折減低於模型的 IF_Util × CTL_ProdDerate（0.6 × 0.85）；無直接證據，Serving C17／C18 為 Assumed"
G24_NEW = ("純利用率＝平均 token 吞吐 ÷ 容量；0.41＝原 0.35 ÷ 生產折減 0.85。區間 0.3–0.65：上端為單一模型集中式服務的代理值（DeepSeek 2025-02，0.54–0.65），"
           "下端保留多模型部署的可能（3A 查證 Q5）。消費端（Cap_In 第 114、218、255 列）乘 CTL_ProdDerate。暫定、待證據。")
J67_OLD = ("Hopper：v5.4 取 3（DeepSeek H800 線上 decode 約達峰值 18%，S30；當時峰值誤用 989 TF）。v5.5 峰值更正為 FP8 1,979 TF，倍數同步減半為 1.5，使 Hopper 產出不變；"
           "S30 口徑查核後重推 [Analogy，區間 0.5–2.5]；GB200、VR200 沿用 GB300 [Analogy]；RU [Assumed]")
J67_NEW = ("Derived（粗略）：k ≈ 峰值比 7.58 ÷ 實測比；MLPerf v5.1 推得 1.45–1.63，LMSYS／NVIDIA 推得約 1.1–1.3，InferenceX 約 0.8–1.0；區間 0.8–1.6（3A 查證 Q4）。"
           "原 1.5 為 v5.5 為使 Hopper 產出不變而倒推。GB200、VR200 沿用 GB300 [Analogy]；RU [Assumed]")
I12_OLD = "保留推理狀態後重複探索減少；以 ARC-AGI-3『少用約 49% token』校準（Checks Block 5）；區間見 D 節"
I12_NEW = ("保留推理狀態後重複探索減少；以 ARC-AGI-3『少用約 49% token』校準（Checks Block 5）；"
           "區間 0.7–1.7（3A Q3：SWE Atlas 顯示原生 scaffold 工具呼叫多 1.5–2 倍，與 0.7 方向相反；0.7 只有 ARC token 比一個來源）。基準位於區間下端。")
H34_TAIL_OLD = "區間：Luna／Sol 0.3–6T、Astra 2.5–25T"
H34_TAIL_NEW = ("區間：開放實驗室 0.1–0.2（Olmo 3）、DeepSeek-V3.2 ≥0.1；Astra 只給區間 0.1–2（Epoch 假設，非證據）。"
                "以 RL ÷ 預訓練 GPU 小時與 rollout token 成正比近似，換算：Luna／Sol 0.1–0.3 ≈ 0.79–2.36T、Astra 0.1–2 ≈ 0.96–19.2T。"
                "基準仍為原校準值，位於區間上端（Luna／Sol）；Astra 基準 1.0 在區間內（v6.1 Q3）")
C16_OLD = "HGX H100 8 GPU 伺服器約 $220–320K（S2，弱證據）"
C16_NEW = ("部署當時 8 GPU HGX 伺服器約 $250–320K（Raymond James 2023-08，每顆 H100 2.5–3 萬；SemiAnalysis 2023-05 DGX H100 約 27 萬，旁證；HPCwire 2024-09 約 2.5 萬／顆）；×4＝一架。"
           "原 S2（clusterbid 2026 報價）降為對照。超大規模業者實付價：已搜尋，未找到（3A Q6b）。")
IN_TAIL = "全機型共用；未分氣冷 Hopper。3A Q6a：超大規模業者 1.10–1.17、colo 1.4–1.6；影響 m_fleet ≤ ±1.3%（稽核 2，Y4）。"
H9_OLD, H17_OLD, H19_OLD = "液冷 AI 設施；v4＝1.2。S14", "分項為假設；總額以 JLL 校準（S12）", "機架內冷板與 manifold 含在機架價格"
SERV_TAIL = " ｜暫定、待證據（D13）；區間 {rng}{extra}"

TEXT_UPD = []      # filled by _build_text_updates (needs nothing from the workbook)


def _text_updates():
    t = []
    for r, old, lohi in ((9, _G9_OLD, "Hopper 0.5／0.7"), (10, _G10_OLD, "GB200 0.25／0.4"), (11, _G11_OLD, "GB300 0／0.1"), (12, _G11_OLD, "VR200 0／0")):
        t.append(("Alloc_In", f"G{r}", old, G_MIX.format(lohi=lohi)))
        t.append(("Alloc_In", f"F{r}", "Assumed", "Derived"))
    t += [("Alloc_In", "F23", "Assumed", "Derived"), ("Alloc_In", "G23", G23_OLD, G23_NEW), ("Alloc_In", "G24", G24_OLD, G24_NEW)]
    t += [("Calib", "J67", J67_OLD, J67_NEW), ("Har_In", "I12", I12_OLD, I12_NEW)]
    t += [("Serving", "D28", "情境值", "Assumed")]
    t += [("Spec_Rack", "C16", C16_OLD, C16_NEW)]
    t += [("Inputs", "H9", H9_OLD, H9_OLD + " ｜" + IN_TAIL),
          ("Inputs", "H17", H17_OLD, H17_OLD + " ｜" + IN_TAIL.replace("全機型共用；未分氣冷 Hopper。", "各世代同值；建物造價未分氣冷 Hopper。")),
          ("Inputs", "H19", H19_OLD, H19_OLD + " ｜" + IN_TAIL.replace("全機型共用；未分氣冷 Hopper。", "各世代同值；機械與散熱未分氣冷 Hopper。"))]
    return t


def text_update(wb):
    log = []
    for sh, addr, old, new in _text_updates():
        c = wb[sh][addr]
        if c.value == old:
            c.value = new; log.append(f"{sh}!{addr}: text (v6.1)")
    ai = wb["Alloc_In"]
    ru = v529._row_by_label(ai, v529.LAB_UTIL)
    # Train_In H34: only the interval tail is replaced
    c = wb["Train_In"]["H34"]
    if isinstance(c.value, str) and H34_TAIL_OLD in c.value:
        c.value = c.value.replace(H34_TAIL_OLD, H34_TAIL_NEW); log.append("Train_In!H34: interval tail (v6.1 Q3)")
    # Serving notes: appended once (append_text keeps it idempotent)
    for addr, rng, extra in (("F17", "0.4–0.8", ""), ("F18", "0.7–1.0", "；基準 1.0 在區間端點（1.0＝主路徑不折減，折減改由 C28 表達；C18 與 C28 是否合併留第 2 批）"),
                             ("F28", "0.7–1.0（C18 區間的中點）", "；v6.1 起同時作為 Alloc_In C24 純利用率的生產折減（D13）")):
        if v518._append_text(wb["Serving"][addr], SERV_TAIL.format(rng=rng, extra=extra)): log.append(f"Serving!{addr}: note appended (v6.1 D13)")
    return log, ru


def decisions_update(wb):
    """Decisions X14m (the 0.35 = utilisation x production derate decision) is kept and marked as superseded for that part."""
    ws = wb["Decisions"]; log = []
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "X14m":
            if ws.cell(r, 7).value == "v5.29 已建":
                ws.cell(r, 7).value = "v5.29 已建；0.35 部分由 AF3B-D13（v6.1）取代"; log.append("Decisions X14m: status (v6.1)")
    return log


# ================================================================== Gov_Map: updates to existing rows (A–P are Excel-owned; each field only while it holds its v6.0 value)
def _gm_row(ws, sheet, cell):
    return v536._gm_row(ws, sheet, cell)


def gov_update(ws, append_text):
    n = 0

    def rep(sheet, cell, col, old, new):
        nonlocal n
        r = _gm_row(ws, sheet, cell)
        if ws[f"{col}{r}"].value == old:
            ws[f"{col}{r}"].value = new; n += 1
        return r

    # D6: Calib C67 (Gov_Map row 345): Analogy -> Derived, 0.8–1.6
    r = _gm_row(ws, "Calib", "C67"); assert ws[f"A{r}"].value == "GM341", ws[f"A{r}"].value
    rep("Calib", "C67", "F", "Analogy", "Derived")
    rep("Calib", "C67", "K", 0.5, 0.8); rep("Calib", "C67", "L", 2.5, 1.6)
    rep("Calib", "C67", "M", "0.5–2.5（原註）", "0.8–1.6（3A Q4；決定紀錄第 4 節 D6）")
    # D3
    for cell in ("C9:C12", "D9:E12"):
        rep("Alloc_In", cell, "F", "Assumed", "Derived")
    r = rep("Alloc_In", "D9:E12", "M", "C9:C12 的低、高端點（各 0–100%）", "C9:C12 的低、高端點：Hopper 50–70%、GB200 25–40%、GB300 0–10%、VR200 0（3A Q1，2025 全年平均；v6.1 D3）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D3（AF3B-D3）：低／高改為 2025 全年平均區間；年底組合 37／40／23／0 為敏感度（情境 h_alloc_mix_2025ye）；無 OpenAI 直接揭露")
    r = rep("Alloc_In", "C9:C12", "M", "各 0–100%，合計 100%（Checks H1）", "基準 0.6／0.4／0／0（不變）；區間見 D9:E12；各 0–100%，合計 100%（Checks H1）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D3（AF3B-D3）：標記 Derived（3A 推導）；基準值不變")
    # D10
    r = _gm_row(ws, "Alloc_In", "C23"); assert ws[f"A{r}"].value == "GM596"
    rep("Alloc_In", "C23", "F", "Assumed", "Derived")
    rep("Alloc_In", "C23", "M", "1.0–1.6（v5.36：基準 2.0 → 1.3；chat 端提案，Andy 2026-10-15 14:25「我找到的基本與你一致。同意你的建議。」）",
        "0.73–1.17（v6.1 D10：經濟口徑，1.16 × 0.73 ≈ 0.85；v5.36 為 1.0–1.6）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D10（AF3B-D10）：經濟口徑 1.16（價格 ÷ 會計成本）× 0.73（會計 ÷ 經濟持有成本）≈ 0.85，區間 0.73–1.17；分母維持經濟口徑持有成本；小於 1＝Azure 計價未涵蓋全部資本成本（m 的實質命題）；標記 Assumed → Derived")
    r = _gm_row(ws, "Alloc_In", "D23:E23")
    rep("Alloc_In", "D23:E23", "F", "Assumed", "Derived")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D10（AF3B-D10）：區間 0.73–1.17（經濟口徑）")
    # D13-1
    lab_old, lab_new = "實際利用率 × 生產折減（v5.29 X14 (m)）", LAB_UTIL_NEW
    r = _gm_row(ws, "Alloc_In", "C24"); assert ws[f"A{r}"].value == "GM598"
    rep("Alloc_In", "C24", "E", lab_old, lab_new)
    rep("Alloc_In", "C24", "M", "0.3–0.4（chat 端提案，Andy 2026-10-08「依建議」）", "0.3–0.65（v6.1 D13：純利用率；上端 DeepSeek 2025-02 單一模型代理值 0.54–0.65；暫定、待證據）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D13（AF3B-D13）：改為純利用率 0.41（＝原 0.35 ÷ 生產折減 0.85），區間 0.3–0.65；生產折減由 CTL_ProdDerate 在消費端（Cap_In 第 114、218、255 列）乘入；暫定、待證據")
    r = _gm_row(ws, "Alloc_In", "D24:E24")
    rep("Alloc_In", "D24:E24", "E", lab_old, lab_new)
    n += append_text(ws[f"N{r}"], " ｜v6.1 D13（AF3B-D13）：區間 0.3–0.65（純利用率）")
    # D13-3: Serving C17／C18／C28 (ranges already registered; M text and reasons refreshed, C28 class Assumed)
    r = _gm_row(ws, "Serving", "C17")
    rep("Serving", "C17", "M", "40–80%（J6 原註）", "40–80%（J6 原註；v6.1 D13：暫定、待證據）")
    r = _gm_row(ws, "Serving", "C18")
    rep("Serving", "C18", "M", "0.7–1.0（Claude 提議，Andy 2026-10-03 確認；交接以 0.7 示範影響）", "0.7–1.0（Claude 提議，Andy 2026-10-03 確認；v6.1 D13：暫定、待證據；基準 1.0 在區間端點）")
    r = _gm_row(ws, "Serving", "C28"); assert ws[f"A{r}"].value == "GM592"
    rep("Serving", "C28", "F", "情境值", "Assumed")
    rep("Serving", "C28", "M", "區間 0.7–1.0（同 Serving!C18 的區間）", "區間 0.7–1.0（C18 區間的中點；v6.1 D13：暫定、待證據）")
    rep("Serving", "C28", "N", "X1：C18 區間中點，非估計值；C18 依 G0-11 維持 1.0", "X1：C18 區間中點；C18 依 G0-11 維持 1.0")
    n += append_text(ws[f"N{r}"], " ｜v6.1 D13（AF3B-D13）：標記 情境值 → Assumed（區間中點為假設）；暫定、待證據；同時作為 Alloc_In C24 純利用率的生產折減")
    # Q3: group rows
    r = rep("Train_In", "C34:E34", "M", "×0.3–×3（Sens_Train 第 53 列情境倍數）", "RL ÷ 預訓練：Luna／Sol 0.1–0.3、Astra 0.1–2（Q3；三格個別區間見 C34、D34、E34 各列；Sens_Train 第 53 列情境倍數 ×0.3–×3 另計）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 Q3（AF3B-Q3）：只登錄區間，基準不變（R1：基準在區間上端／Astra 區間內）")
    r = rep("Har_In", "C12:G12", "M", "0.5–1（Sens_Har 第 61 列）", "0.7–1.7（Sens_Har 第 61 列；v6.1 Q3）")
    n += append_text(ws[f"N{r}"], " ｜v6.1 Q3（AF3B-Q3）：基準 0.7 不變，位於區間下端（3A Q3：SWE Atlas 原生 scaffold 工具呼叫多 1.5–2 倍）")
    r = _gm_row(ws, "Har_In", "C61:D66")
    n += append_text(ws[f"N{r}"], " ｜v6.1 Q3（AF3B-Q3）：輪數倍數 C61／D61 由 0.5／1 改為 0.7／1.7")
    return n


def gov_map_rows(wb):
    """Gov_Map rows for the Q3 ranges (Train_In C34／D34／E34 individually, Har_In E12:G12); appended by gov.gm_append_c when absent."""
    out = []
    ti, hi = wb["Train_In"], wb["Har_In"]
    assert ti["A34"].value == "RL rollout 輸出 token（含各領域專家）" and hi["A12"].value == "輪數倍數"
    sc = "切片三（v6.1 Q3）"
    base = ("Q3（AF3B-Q3）：RL ÷ 預訓練 GPU 小時與 rollout token 成正比的近似，把比值區間換算為 token；開放實驗室 0.1–0.2（Olmo 3）、DeepSeek-V3.2 ≥0.1；"
            "已搜尋（3A Q3）、可比對象 Olmo 3／DeepSeek-V3.2、區間依據即本列；基準維持原校準值（R1），見 Train_In H34")
    for col, tier, lo, hi_, rt, extra in (
            ("C", "Luna", 0.787, 2.36, "0.1–0.3 × 預訓練 ≈ 0.79–2.36T", "基準 2.36T（比值約 0.3）位於區間上端"),
            ("D", "Sol", 0.787, 2.36, "0.1–0.3 × 預訓練 ≈ 0.79–2.36T", "基準 2.36T（比值約 0.3）位於區間上端"),
            ("E", "Astra", 0.96, 19.2, "0.1–2 × 預訓練 ≈ 0.96–19.2T（Epoch 假設，非證據）", "基準 9.6T（比值約 1.0）在區間內；Astra 只給區間")):
        out.append({'scope': sc, 'sheet': 'Train_In', 'cell': f'{col}34', 'label': f'RL rollout 輸出 token（{tier}）', 'check': ti["A34"].value, 'cls': 'Assumed', 'role': '單值',
                    'src': '', 'rel': '', 'dec': 'AF3B-Q3', 'lo': lo, 'hi': hi_, 'rtext': rt, 'reason': base + "；" + extra, 'retag': '', 'seg': '高'})
    out.append({'scope': sc, 'sheet': 'Har_In', 'cell': 'E12:G12', 'label': '輪數倍數（檔案 2：單代理、多代理研究、Coding agent）', 'check': hi["A12"].value, 'cls': 'Assumed', 'role': '群組',
                'src': '', 'rel': '', 'dec': 'AF3B-Q3', 'lo': 0.7, 'hi': 1.7, 'rtext': '0.7–1.7（3A Q3）；基準 0.7 在區間下端',
                'reason': "Q3（AF3B-Q3）：3A 查證 Q3：SWE Atlas 顯示原生 scaffold 工具呼叫多 1.5–2 倍，與 0.7 方向相反；0.7 只有 ARC token 比一個來源；已搜尋、可比對象 SWE Atlas／ARC-AGI-3、區間依據即本列；"
                          "基準維持 0.7（R1），Sens_Har 第 61 列區間由 0.5–1 改為 0.7–1.7", 'retag': '', 'seg': '無'})
    return out


# ================================================================== Decisions (10 columns; layout of v530–v600)
_D = [
    ("D3", "2025 服務世代組合", "Alloc_In 第 9–12 列低／高改為 2025 全年平均區間：Hopper 0.5／0.7、GB200 0.25／0.4、GB300 0／0.1、VR200 0／0；基準 0.6／0.4／0／0 不變；標記 Derived（3A 推導）。"
     "2025 年底組合（Hopper 37／GB200 40／GB300 23／VR200 0）作為敏感度，新增 parity 情境 h_alloc_mix_2025ye。無 OpenAI 直接揭露。",
     "Alloc_In D9:E12；Gov_Map GM590／GM591；tests/parity/scenarios.yaml h_alloc_mix_2025ye；Alloc 第 85、86 列（世代組合敏感度）、AL_Mix*_Lo／_Hi 讀取者", "第 1 節 D3；第 2 節 D3"),
    ("D6", "Hopper η_d 倍數", "Calib C67 1.5 → 1.2，區間 0.8–1.6，標 Derived（粗略）；Gov_Map 345 Analogy → Derived。Calib C68（每層延遲倍數 1.5）同為倒推值、與 C67 共同作用，本批不改，列待 Project 判斷。",
     "Calib C67、J67；Gov_Map GM341；所有 Hopper 欄 decode 產出與下游（2025 組合下的 AL_Blend*、AL_ServeGW、L1_ScaleServe、L1_MFleet、Q1、Q2）", "第 1 節 D6；第 2 節 D6"),
    ("D10", "計價倍數（經濟口徑）", "Alloc_In 計價倍數 1.3／1／1.6 → 0.85／0.73／1.17：經濟口徑 1.16（價格 ÷ 會計成本）× 0.73（會計 ÷ 經濟持有成本）≈ 0.85；分母維持經濟口徑持有成本；"
     "小於 1 表示 Azure 計價未涵蓋全部資本成本，這本身是 m 的實質命題。標記 Assumed → Derived。",
     "Alloc_In C23:E23；Gov_Map GM596／GM597；Cap_In 第 109、218 列；L1_GapSpendBasis*", "第 1 節 D10；第 2 節 D10"),
    ("D13", "暫定值與純利用率", "(1) Alloc_In C24 改為純利用率 0.41（區間 0.3–0.65；標籤『實際利用率（純；不含生產折減）』），生產折減另由 CTL_ProdDerate（Serving C28 0.85）處理，避免重複計算；"
     "(2) 消費公式改乘 CTL_ProdDerate：Cap_In 第 114、218、255 列的 AL_UtilActual（含 _Hi／_Lo）改為 (AL_UtilActual*CTL_ProdDerate)，基準 0.35 → 0.3485（−0.43%）、區間 0.3–0.4 → 0.255–0.553；"
     "(3) Serving C17 0.6（0.4–0.8）、C18 1.0（0.7–1.0；基準在端點）、C28 0.85（0.7–1.0）數值不變，標記 Assumed，區間登錄 Gov_Map；全部『暫定、待證據』。"
     "原 X14m 對 0.35 的決定由本決策取代（保留不刪）。L1_GapUtil 的定義改寫留第 2 批。",
     "Alloc_In C24:E24；Cap_In 第 114、218、255 列；Serving C17／C18／C28；Gov_Map GM236／GM237／GM592／GM598／GM599；L1_GapUtil*", "第 1 節 D13；第 2 節 D13-1／D13-2／D13-3"),
    ("Q3", "RL 與 harness 輪數區間", "只登錄區間，基準不變（讀法 R1）：Train_In C34／D34／E34 以 RL ÷ 預訓練 0.1–0.3（Astra 0.1–2）換算為 token 區間 0.79–2.36T／0.96–19.2T；基準在區間上端（Luna／Sol）；"
     "Har_In 敏感度區間 C61／D61 0.5／1 → 0.7／1.7，E12:G12 基準 0.7 不變（區間下端）。是否改採 R2（基準移到中點）由 Andy 決定。",
     "Train_In C34:E34、H34；Har_In C61:D61、I12；Sens_Har 第 5 列；Gov_Map（新增 4 列）", "第 1 節 Q3；第 2 節 Q3"),
    ("Q6", "Hopper 設施與價格（稽核 Y4、Y7）", "Y7：Spec_Rack C11:C13（0.9／1.1／1.3）數值不變，C16 說明改為部署當時價證據（原 S2 clusterbid 2026 報價降為對照）；超大規模業者實付價已搜尋未找到。"
     "Y4：不新增 Hopper 專屬參數，Inputs H9／H17／H19 補說明（影響 m_fleet ≤ ±1.3%），數值不改。SRC_HW 未新增（待 Project 判斷）。",
     "Spec_Rack C16；Inputs H9／H17／H19", "第 1 節 Q6；第 2 節 Q6"),
]
DECISIONS_V601 = [[f"AF3B-{i}", V, f"稽核修正 3B {i}：{t}", txt, DATE, ANDY, "v6.1 已建", where, f"{WO} {sec}；{EVID}", "否"] for i, t, txt, where, sec in _D]

# ================================================================== README
README_VERSION = (VERSION + "（次版：稽核修正第 3B 批輸入值，" + WO + "——D3 Alloc_In 世代組合低／高改 2025 全年平均區間；D6 Calib C67 1.5 → 1.2（0.8–1.6，Derived）；D10 計價倍數 0.85（0.73–1.17）；"
                  "D13 純利用率 0.41（0.3–0.65）並於 Cap_In 第 114、218、255 列改乘 CTL_ProdDerate（唯一公式修改），Serving C17／C18／C28 區間登錄、標記 Assumed；Q3 RL／輪數倍數只登錄區間（輪數敏感度區間 0.7–1.7）；"
                  "Q6 Spec_Rack C16 與 Inputs H9／H17／H19 說明；Decisions AF3B-D3／D6／D10／D13／Q3／Q6）。以下為 " + v600.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v600.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v600.VERSION.split("_")[-1]):]
README_ROW = ("輸入值修正（v6.1）",
              "稽核修正 3B：2025 服務世代組合區間（Alloc_In 第 9–12 列）、Hopper η_d 倍數 1.2（Calib C67）、計價倍數經濟口徑 0.85、純利用率 0.41 與生產折減分開（Cap_In 第 114、218、255 列乘 CTL_ProdDerate）、"
              "Serving C17／C18／C28 暫定區間、RL 與 harness 輪數區間。標記與理由見 Gov_Map 與 Decisions AF3B-*。")

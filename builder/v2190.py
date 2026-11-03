# v21.9 (work order docs/workorders/20261103_v21.9_Q1原生精度與文字治理修正.md r0, branch claude/v21-9): NonNV Q1 settled (TPU, Trainium3 output ratios on each
# chip's highest native precision) + text／governance fixes from the v21.8 independent check (docs/reports/20261103_v21.8_獨立核對.md).
# MINOR version: input values change (NonNV B6:D6, B7:D7), written only while they still hold the v21.8 value (like v2170.inputs_update); contract v0.27 unchanged;
# no IF_／L1_ name added or removed; SRC_HW_100 changes status (Superseded), no SRC name removed.
#   W1  NonNV B6:D6 (TPU v7 output ratio) 0.6／0.8／1.1 -> 0.25／0.35／0.40;  B7:D7 (Trainium3 output ratio) 0.3／0.5／0.8 -> 0.06／0.14／0.25.
#   W2  Text (revision 9: replaced wording kept verbatim after the existing "｜原：" segment, tagged "｜原（v21.9 前）："): NonNV L6, L7, L8, L9, A2; Interface A368.
#   W3  Governance／text fixes, no value change: SRC_HW_100 Superseded (duplicate of SRC_HW_010; SRC_HW_010 Evidence + E450); README B5 v21.8 paragraph,
#       Decisions SL65-01 and CHANGELOG v21.8 add the B4_MktCache／IFC_* side effects; Inputs!H23 wording; Load_Bearing!C3 = build date (engineering, build.py);
#       SRC_DC_004 source／applies-to; SRC_PRC_074 grade 1 -> 2 (L already Derived); SRC_DEM_091 "近（nearly）".
#   W4  DB_Evidence E559 (after E558), Decisions SL66-01, README B5 opening paragraph.
# Contract names whose values change: IF_NonNV_Out_TPU, IF_NonNV_Out_Trn (3 cells each) and the version strings.
# Excel-owned cells are written only while they still hold the old value／text (or the new text is absent); NonNV／Interface text cells are rewritten by the
# builder on every build, so those fixes are re-applied deterministically. Idempotent.
from openpyxl.utils import get_column_letter as L

from common import put, F_CALC
import v1410
import v1720
import v2170
import v2180

VERSION = "20261103_Tokenomics_v21.9"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-11-03"                         # build date: also Load_Bearing!C3 (W3 point 4; build.py)
DASH = "—"
V = "v21.9"
WO = "工作單 docs/workorders/20261103_v21.9_Q1原生精度與文字治理修正.md（r0）"
DEC_ID = "SL66-01"
EVD = "docs/evidence/20261025_NonNV_TPU_Trainium/"
OLD_TAG = "｜原（v21.9 前）："       # revision 9: wording replaced in v21.9, kept verbatim after the existing 原 segment
DEC_BY = ("Andy 2026-11-03 14:23：「#2照預設。」→ PR #172 待判斷 Q1 預設「各晶片最高原生精度」（VR200 以 NVFP4；TPU v7 只有 FP8；Trainium3 FP4＝FP8 同速，"
          "精度差由效率因子 f 吸收，同模型對 Hopper 的處理）；PR #176 Q3、Q6、Q8（Cerebras、OpenAI 客製數值不改）；"
          "v21.8 獨立核對 docs/reports/20261103_v21.8_獨立核對.md → docs/workorders/20261103_v21.9_文字與治理修正_待辦.md（chat 端定案）")

# ---------------------------------------------------------------- W1 inputs (old-value guards)
TPU_OLD, TPU_NEW = (0.6, 0.8, 1.1), (0.25, 0.35, 0.40)
TRN_OLD, TRN_NEW = (0.3, 0.5, 0.8), (0.06, 0.14, 0.25)


def inputs_update(wb):
    log = []
    ws = wb["NonNV"]
    assert ws["A6"].value == "Google TPU v7 Ironwood", ws["A6"].value
    assert ws["A7"].value == "AWS Trainium3", ws["A7"].value
    for r, old, new, what in ((6, TPU_OLD, TPU_NEW, "TPU v7"), (7, TRN_OLD, TRN_NEW, "Trainium3")):
        cells = [ws[f"{c}{r}"] for c in "BCD"]
        if all(v2170._same(c, o) for c, o in zip(cells, old)):
            for c, n in zip(cells, new):
                c.value = n
            log.append(f"NonNV!B{r}:D{r} ({what} output ratio): {old} -> {new} (v21.9 W1, PR #172 Q1)")
    return log


# ---------------------------------------------------------------- W2 text
Q1_OLD = ("產出比仍為慣例值，待精度口徑判斷（PR #172 Q1：各晶片最高原生精度時 TPU 0.25／0.35／0.40、Trn3 0.06／0.14／0.25；"
          "FP8 對齊時 TPU 0.48／0.66／0.84、Trn3 0.13／0.28／0.50）")
Q1_NEW = ("產出比 v21.9 依各晶片最高原生精度推導（PR #172 Q1 預設，Andy 2026-11-03 照預設）：VR200 以 NVFP4 dense 35 PF；TPU v7 只有 FP8（4.614 PF）、"
          "Trn3 FP4＝FP8（2.517 PF），精度差由效率因子吸收（同 Hopper）；TPU 0.25／0.35／0.40、Trn3 0.06／0.14／0.25；"
          "替代 FP8 對齊口徑 TPU 0.48／0.66／0.84、Trn3 0.13／0.28／0.50 只列說明")
NO_DATA = "本列尚無機架功率與價格資料，維持慣例值。"
L8_ADD = ("v21.9：PR #176 查過——晶圓級系統無同口徑機架價，每 kW 設備價法不適用、只得界線；CS-4／WSE-3T（2026 Q3）每 kW 峰值約 0.54 PF/kW，"
          "與 WSE-3 相近；數值維持（#176 Q3）")
L9_OPEN_OLD = "無公開規格；沿用 v0.5「自研／其他 0.6（0.4–1.0）」"
L9_OPEN_NEW = ("v21.9：Jalapeño 規格推導產出比 0.35／0.60／1.15（方法一，PR #176），基準與現值 0.6 相同；持有比界線 0.64／0.82／1.27"
               "（Broadcom 執行長每 GW 內容 $20–30B，口徑未說明）與現值 0.8 相容；數值維持（Project Q6、Q8）")
A2_ANCHOR = "Cerebras、OpenAI 客製仍為慣例值（Block 1『接近 1』）"
A2_ADD = "；產出比：AMD、昇騰、Maia、TPU、Trn3 已推導（TPU、Trn3 為 v21.9 原生精度口徑），Cerebras、OpenAI 客製維持慣例值（#176 推導值與現值相容）"
A368_OLD = "產出比已推導：AMD、昇騰、Maia（TPU、Trn3 待精度口徑）"
A368_NEW = "產出比已推導：AMD、昇騰、Maia、TPU、Trn3（v21.9 原生精度口徑）"
ORIG = "｜原："


def text_fixes(wb):
    ws = wb["NonNV"]
    n = 0
    # L6, L7: Q1 sentence replaced; the old sentence kept after the 原 segment
    for r in (6, 7):
        cell = ws[f"L{r}"]
        cur = str(cell.value)
        if Q1_NEW in cur:
            continue
        assert cur.count(Q1_OLD) == 1 and cur.count(ORIG) == 1 and cur.index(Q1_OLD) < cur.index(ORIG), (r, cur[-200:])
        cell.value = cur.replace(Q1_OLD, Q1_NEW) + OLD_TAG + Q1_OLD
        n += 1
    # L8: v21.9 sentence before 原; the "no data" sentence moved after 原
    cell = ws["L8"]
    cur = str(cell.value)
    if L8_ADD not in cur:
        assert cur.count("；" + NO_DATA + ORIG) == 1, cur[-200:]
        cell.value = cur.replace("；" + NO_DATA + ORIG, "｜" + L8_ADD + ORIG) + OLD_TAG + NO_DATA
        n += 1
    # L9: opening replaced, "no data" sentence removed; both kept after 原
    cell = ws["L9"]
    cur = str(cell.value)
    if not cur.startswith(L9_OPEN_NEW):
        assert cur.startswith(L9_OPEN_OLD) and cur.count("；" + NO_DATA + ORIG) == 1, cur
        cur = L9_OPEN_NEW + cur[len(L9_OPEN_OLD):]
        cell.value = cur.replace("；" + NO_DATA + ORIG, ORIG) + OLD_TAG + L9_OPEN_OLD + "；" + NO_DATA
        n += 1
    # A2: output-ratio sentence added after the holding-ratio sentence (insertion only)
    a2 = ws["A2"]
    cur = str(a2.value)
    if A2_ADD not in cur:
        assert cur.count(A2_ANCHOR + ORIG) == 1, cur
        a2.value = cur.replace(A2_ANCHOR + ORIG, A2_ANCHOR + A2_ADD + ORIG)
        n += 1
    # Interface A368
    wi = wb["Interface"]
    t = str(wi["A368"].value)
    if A368_NEW not in t:
        assert t.count(A368_OLD) == 1 and t.index(A368_OLD) < t.index(ORIG), t[-200:]
        wi["A368"].value = t.replace(A368_OLD, A368_NEW) + OLD_TAG + A368_OLD
        n += 1
    return n


# ---------------------------------------------------------------- W3 text／governance
H23_OLD_PART = "v21.8 起高成本由 4 改 5：2026Q3 四家 hyperscaler 10-Q 皆無 4 年"
H23_NEW_PART = "v21.8 起高成本由 4 改 5：2026Q3 Amazon、Meta、Microsoft、SpaceX 10-Q 皆無 4 年，Alphabet 6 年見其法說（10-Q 未讀）"
H23_NEW = v2180.H23_NEW.replace(H23_OLD_PART, H23_NEW_PART)
HIGH_ANCHOR = "以及 L1_*_Hi／對應 _Lo 毛利名稱）"
HIGH_ADD = "；另有 B4_MktCache（1-G）與 IFC_Conf／IFC_Use／IFC_Updated（IF_DeprLifeIT 信心 B→A）連帶（v21.9 補）"
HW100_NOTE = "重複：與 SRC_HW_010 同一原文（Data Gravity／wing.vc，5.0 $M）"
DC004_J = "Turner & Townsend 原文（同 E452 出處）｜https://www.turnerandtownsend.com/en-us/news/ai-data-center-rush-raises-alarm-over-construction-supply-chain/；https://reports.turnerandtownsend.com/data-centre-construction-cost-index-2026-us/ai-data-centers"
DC004_J_OLD = "archdesk.com、gigacapacity.com 轉述 JLL"
DC004_H, DC004_H_OLD = "AI 資料中心", "液冷設施"
DEM091_G_OLD = "第一方模型 API（不含 Gemini App 與 Search）；時點值；季增 40%、年增逾 4 倍"
DEM091_G_NEW = "第一方模型 API（不含 Gemini App 與 Search）；時點值；近（nearly）；季增 40%、年增逾 4 倍"
FIX = f"｜{V} 更正（修訂九；Decisions {DEC_ID}；{WO}）："


def _w(ws, r, txt):
    w = ws[f"W{r}"].value
    ws[f"W{r}"].value = (str(w) if w not in (None, "") else DASH) + txt


def src_fixes(wb):
    rows = v1720._rows(wb)
    n = 0
    # 1. SRC_HW_100 -> Superseded (replaced by SRC_HW_010); SRC_HW_010 Evidence + E450
    ws, r = rows["SRC_HW_100"]
    if ws[f"O{r}"].value != "Superseded":
        assert ws[f"O{r}"].value == "Alt" and ws[f"P{r}"].value == DASH and ws[f"Q{r}"].value == "E450", (ws[f"O{r}"].value, ws[f"P{r}"].value)
        ws[f"O{r}"].value = "Superseded"
        ws[f"P{r}"].value = "SRC_HW_010"
        ws[f"W{r}"].value = HW100_NOTE + FIX + "原狀態＝Alt；原取代者＝—｜" + str(ws[f"W{r}"].value)
        n += 1
    ws, r = rows["SRC_HW_010"]
    n += v2180._append_q(ws, r, "E450")
    # 1. (check only) E550 is the SRC_HW_101 record
    ws, r = rows["SRC_HW_101"]
    assert ws[f"Q{r}"].value == "E550", ws[f"Q{r}"].value
    # 5. SRC_DC_004 source (J) and applies-to (H)
    ws, r = rows["SRC_DC_004"]
    if ws[f"J{r}"].value != DC004_J:
        assert ws[f"J{r}"].value == DC004_J_OLD and ws[f"H{r}"].value == DC004_H_OLD, (ws[f"J{r}"].value, ws[f"H{r}"].value)
        ws[f"J{r}"].value = DC004_J
        ws[f"H{r}"].value = DC004_H
        _w(ws, r, FIX + f"原出處＝『{DC004_J_OLD}』；原適用對象＝『{DC004_H_OLD}』（與 v21.8 更正後的指標名同步，E452）")
        n += 1
    # 6. SRC_PRC_074 grade 1 -> 2 (L is already Derived); SRC_DEM_091 "近（nearly）"
    ws, r = rows["SRC_PRC_074"]
    assert ws[f"L{r}"].value == "Derived", ws[f"L{r}"].value
    if ws[f"K{r}"].value != 2:
        assert ws[f"K{r}"].value == 1, ws[f"K{r}"].value
        ws[f"K{r}"].value = 2
        _w(ws, r, FIX + "等級 1 → 2（推算粗估：10-Q 加口頭「約各半」推出的 Derived 倍數）；原等級＝1；標記（L 欄）已是 Derived")
        n += 1
    ws, r = rows["SRC_DEM_091"]
    if ws[f"G{r}"].value != DEM091_G_NEW:
        assert ws[f"G{r}"].value == DEM091_G_OLD, ws[f"G{r}"].value
        ws[f"G{r}"].value = DEM091_G_NEW
        _w(ws, r, FIX + "口徑加「近（nearly）」（原文 nearly 32 billion）；原口徑＝『" + DEM091_G_OLD + "』")
        n += 1
    return n


def gov_text_fixes(wb):
    n = 0
    # 3. Inputs!H23 (Excel-owned; v2180.text_fixes accepts this text)
    ws = wb["Inputs"]
    if ws["H23"].value != H23_NEW:
        assert ws["H23"].value == v2180.H23_NEW, ws["H23"].value
        ws["H23"].value = H23_NEW
        n += 1
    # 2. Decisions SL65-01 (Excel-owned)
    d = wb["Decisions"]
    for r in range(5, d.max_row + 1):
        if d.cell(r, 1).value == v2180.DEC_ID:
            t = str(d.cell(r, 4).value)
            if HIGH_ADD not in t:
                assert t.count(HIGH_ANCHOR) == 1, t[-300:]
                d.cell(r, 4).value = t.replace(HIGH_ANCHOR, HIGH_ANCHOR + HIGH_ADD)
                n += 1
            break
    else:
        raise AssertionError("Decisions SL65-01 missing")
    return n


def load_bearing_date(wb):
    """W3 point 4 (engineering): Load_Bearing!C3 (build date read by LB_Days) was the static v5.29 date 2026-10-08; it now carries the version's build date."""
    ws = wb["Load_Bearing"]
    assert str(ws["A3"].value).startswith("建置日"), ws["A3"].value
    put(ws, "C3", DATE, F_CALC)


# ---------------------------------------------------------------- W4 DB_Evidence E559
_OLD_OUT = "NonNV 第 6、7 列產出比 TPU v7 0.6／0.8／1.1、Trainium3 0.3／0.5／0.8（慣例值）；每 token 成本比基準 TPU 0.875、Trn3 1.22"
E559 = [
    "E559", DATE,
    "NonNV Q1 定案——TPU v7 產出比 0.25／0.35／0.40、Trainium3 產出比 0.06／0.14／0.25（各晶片最高原生精度；採用，v21.9 W1）；每 token 成本比基準 TPU 2.0、Trn3 4.357",
    "NonNV B 段查證 " + EVD + "（PR #172）README 第 1 節表與 r1 修正",
    "Assumed（每 kW 峰值算力比 × 效率因子 f；f 由模型 Hopper／Blackwell 還原，Trn3 無第三方實測）",
    "NonNV B6:D7；Interface 第 370、371 列（IF_NonNV_Out_TPU／IF_NonNV_Out_Trn）",
    _OLD_OUT,
    "TPU v7 0.25／0.35／0.40、Trainium3 0.06／0.14／0.25（採用）；替代 FP8 對齊口徑 TPU 0.48／0.66／0.84、Trn3 0.13／0.28／0.50 只列說明",
    "採用（PR #172 Q1 預設，Andy 2026-11-03 照預設，" + V + " W1）", V,
    "判定依據：Andy 2026-11-03「#2照預設。」；精度：VR200 以 NVFP4 dense 35 PF；TPU v7 只有 FP8（4.614 PF）、Trn3 FP4＝FP8（2.517 PF），精度差由效率因子吸收（同 Hopper）｜" + WO,
    "已處理", DASH, DASH, "IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（值改變，各 3 格）；其餘契約名稱不變", 3, "利害關係方",
    "採用（產出比改原生精度口徑）｜" + V + " 新增列"]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    if any(ws.cell(r, 1).value == E559[0] for r in range(5, ws.max_row + 1)):
        return 0
    r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
    assert ws.cell(r - 1, 1).value == "E558", ws.cell(r - 1, 1).value
    for i, v in enumerate(E559):
        put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 17))
    return 1


# ---------------------------------------------------------------- W4 Decisions SL66-01
def _decisions():
    return [[DEC_ID, V, "v21.9 NonNV Q1 定案（TPU、Trainium3 產出比改各晶片最高原生精度）與 v21.8 核對的文字治理修正",
             "W1：NonNV B6:D6（TPU v7 產出比）0.6／0.8／1.1 → 0.25／0.35／0.40；B7:D7（Trainium3 產出比）0.3／0.5／0.8 → 0.06／0.14／0.25"
             "（PR #172 Q1 預設：各晶片最高原生精度，VR200 NVFP4、TPU v7 FP8、Trn3 FP4＝FP8，精度差由效率因子吸收；Assumed；E559）。"
             "方向計數：W1 下修（不利方向）、改基準 2 列；每 token 成本比基準 TPU 0.875 → 2.0、Trn3 1.22 → 4.357。"
             "W2：NonNV L6、L7、L8、L9、A2 與 Interface A368 說明更新（Cerebras、OpenAI 客製依 PR #176 Q3、Q6、Q8 數值不改，只更新說明），"
             "被改寫的原文逐字保留於「｜原（v21.9 前）：」之後（修訂九）。"
             "W3（不動數值）：SRC_HW_100 改 Superseded（取代者 SRC_HW_010；重複登錄同一原文），SRC_HW_010 Evidence 加 E450；"
             "README B5 v21.8 段、Decisions SL65-01、CHANGELOG v21.8 段補 B4_MktCache 與 IFC_Conf／IFC_Use／IFC_Updated 連帶；Inputs!H23 改寫 10-Q 措辭；"
             "Load_Bearing!C3 改為建置日；SRC_DC_004 出處改 Turner & Townsend 原文、適用對象改 AI 資料中心；SRC_PRC_074 等級 1 → 2；SRC_DEM_091 口徑加「近（nearly）」"
             "（各原值保留於 W 欄，修訂九）。W4：DB_Evidence E559；README B5 加 v21.9 段。"
             "契約名稱的值改變只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串；契約不升版（v0.27）。Andy 原話與依據：" + DEC_BY,
             DATE, DEC_BY, "v21.9 已建",
             "NonNV B6:D7、L6／L7／L8／L9／A2；Interface 第 370、371 列與 A368；SRC_HW_100／010、SRC_DC_004、SRC_PRC_074、SRC_DEM_091；Inputs H23；Load_Bearing C3；"
             "Decisions SL65-01；DB_Evidence E559；README B5",
             f"{WO} W1–W4", "否"]]


def apply(wb, append_text):
    log = {"text_fixes": text_fixes(wb), "src_fixes": src_fixes(wb), "gov_text_fixes": gov_text_fixes(wb)}
    log["evidence"] = evidence_append(wb)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ---------------------------------------------------------------- README
_prev = v2180.README_VERSION.split("_Tokenomics_", 1)[1]
assert _prev.count(HIGH_ANCHOR) == 1
_prev = _prev.replace(HIGH_ANCHOR, HIGH_ANCHOR + HIGH_ADD)      # W3 point 2: v21.8 paragraph completed
README_VERSION = (VERSION + "（次版，底版 v21.8：" + WO + "——v21.9：契約名稱值改變者只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串；"
                  "NonNV TPU v7 產出比 0.6／0.8／1.1 → 0.25／0.35／0.40、Trainium3 0.3／0.5／0.8 → 0.06／0.14／0.25（PR #172 Q1 預設：各晶片最高原生精度；Assumed；E559）；"
                  "NonNV L6／L7／L8／L9／A2 與 Interface A368 說明更新（原文保留於「｜原（v21.9 前）：」後）；"
                  "v21.8 核對的文字與治理修正（SRC_HW_100 Superseded、SRC_DC_004 出處、SRC_PRC_074 等級、SRC_DEM_091 口徑、Inputs!H23、Load_Bearing!C3 建置日；不動數值）；"
                  "Decisions SL66-01。）以下為 " + _prev)
README_TITLE = V + v2180.README_TITLE[len(v2180.V):]

# v21.10 (work order docs/workorders/20261104_v21.10_TPU產出比改FP8對齊與文字修正.md r0, branch claude/v21-10): TPU v7 and Trainium3 output ratios move
# to an FP8-aligned baseline (VR200 also compared at FP8; PR #172 section E method 1), the v21.9 native-precision values become the low end; plus the
# text／governance follow-ups 11–16 of the v21.9 independent check (docs/workorders/20261103_v21.9_文字與治理修正_待辦.md).
# Module name v21100 (= v21.10.0): builder/v2110.py is already v21.1.
# MINOR version: input values change (NonNV B6:D6, B7:D7), written only while they still hold the v21.9 value (like v2190.inputs_update); contract v0.27
# unchanged; no IF_／L1_ name added or removed; no SRC name added or removed.
#   W1  NonNV B6:D6 (TPU v7 output ratio) 0.25／0.35／0.40 -> 0.35／0.66／0.84;  B7:D7 (Trainium3 output ratio) 0.06／0.14／0.25 -> 0.14／0.28／0.50.
#   W2  Text (revision 9: replaced wording kept verbatim after "｜原（v21.10 前）："): NonNV L6, L7 (precision basis), A2, L8 (follow-up 11);
#       Interface A368; Inputs!H23 (follow-up 13: the v21.8 sentence replaced in v21.9 is appended after "｜原（v21.9 前）："); NonNV L9 (follow-up 16, insertion).
#   W3  Governance, no value change: Load_Bearing!C3 = date of the version file name (follow-up 14; build.py); DB_Evidence E450 related SRC + SRC_HW_010,
#       SRC_DC_004 grade 3 -> 1, 二手 -> 一手, stance note -> Turner & Townsend (follow-up 15; E452 is the first-hand read of the T&T original);
#       DB_Evidence E560 (after E559); Decisions SL67-01; README B5 opening paragraph.
# Contract names whose values change: IF_NonNV_Out_TPU, IF_NonNV_Out_Trn (3 cells each) and the version strings.
# Excel-owned cells are written only while they still hold the old value／text (or the new text is absent). Idempotent.
from openpyxl.utils import get_column_letter as L

from common import put, F_CALC
import v1410
import v1720
import v2170
import v2190

VERSION = "20261104_Tokenomics_v21.10"      # single source of the version string: README!B5 and README!A1 (finish.readme); Load_Bearing!C3 (load_bearing_date)
DATE = "2026-11-04"
DASH = "—"
V = "v21.10"
WO = "工作單 docs/workorders/20261104_v21.10_TPU產出比改FP8對齊與文字修正.md（r0）"
DEC_ID = "SL67-01"
EVD = "docs/evidence/20261104_TPU產出比查核/"
OLD_TAG = "｜原（v21.10 前）："      # revision 9: wording replaced in v21.10, kept verbatim at the end of the cell
ORIG = v2190.ORIG
DEC_BY = ("Andy 2026-11-04 12:55：「需要我决定的都按照你的建议去执行」→ 採建議甲：TPU、Trainium3 產出比基準改 FP8 對齊（PR #172 E 節方法一），"
          "各晶片最高原生精度降為低端；依據查核 " + EVD + "（Andy 11-04「這個要優先查核，莫非我們'各晶片最高原生精度'的假設錯了?還是有其他原因」）；"
          "v21.9 獨立核對 docs/reports/20261103_v21.9_獨立核對.md → docs/workorders/20261103_v21.9_文字與治理修正_待辦.md 追加 11–16")

# ---------------------------------------------------------------- W1 inputs (old-value guards)
TPU_OLD, TPU_NEW = v2190.TPU_NEW, (0.35, 0.66, 0.84)
TRN_OLD, TRN_NEW = v2190.TRN_NEW, (0.14, 0.28, 0.50)


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
            log.append(f"NonNV!B{r}:D{r} ({what} output ratio): {old} -> {new} (v21.10 W1, FP8-aligned baseline)")
    return log


# ---------------------------------------------------------------- W2 text
Q1_NEW = ("產出比 v21.10：基準＝FP8 對齊（VR200 也以 FP8 比，PR #172 E 節方法一），低端＝各晶片最高原生精度基準值（v21.9 基準），高端＝FP8 對齊高端。"
          "理由（" + EVD + "）：TK 引擎把推論當算力受限，原生精度等於固定 2 倍懲罰；外部實測 Blackwell FP4 對 FP8 吞吐 2.2–8.2 倍含省頻寬效果、"
          "每 kW HBM 頻寬 TPU v7 約為 VR200 0.97–1.11；TPU v7 的同代是 GB300（VR200 同代為 TPU 8）。Andy 2026-11-04 照建議")
A2_PREC_OLD = "（TPU、Trn3 為 v21.9 原生精度口徑）"
A2_PREC_NEW = "（TPU、Trn3 為 v21.10 FP8 對齊口徑，原生精度為低端）"
A2_176_OLD = "（#176 推導值與現值相容）"
A2_176_NEW = "（OpenAI 客製推導基準 0.60 與現值相同；Cerebras 無推導值、證據偏不利（#176 Q3 替代下修 0.05／0.15／0.45），維持慣例值）"
A2_NEW = v2190.A2_ADD.replace(A2_PREC_OLD, A2_PREC_NEW).replace(A2_176_OLD, A2_176_NEW)
A368_PREC_OLD = "（v21.9 原生精度口徑）"
A368_PREC_NEW = "（v21.10：FP8 對齊作基準、原生精度為低端）"
A368_NEW = v2190.A368_NEW.replace(A368_PREC_OLD, A368_PREC_NEW)
L8_OLD_PART = "每 kW 設備價法不適用、只得界線"      # follow-up 11
L8_NEW_PART = "無官方售價；每 kW 法（記者估價，持有比 2.5／3.1／3.9）與 OpenAI 合約法相差 3.7–7.7 倍、互相衝突；產出比只得界線"
L8_NEW = v2190.L8_ADD.replace(L8_OLD_PART, L8_NEW_PART)
L9_ADD = "；Jalapeño 機架與規格證據見 #176 §3"      # follow-up 16 (insertion after the v21.9 sentence)
H23_V218 = "v21.8 起高成本由 4 改 5：2026Q3 四家 hyperscaler 10-Q 皆無 4 年"      # follow-up 13: verbatim from the v21.8 workbook (Inputs!H23)
H23_TAIL = v2190.OLD_TAG + H23_V218
H23_NEW = v2190.H23_NEW + H23_TAIL


def _head(t):
    """Text before the first 原 segment (the live wording)."""
    return t.split(ORIG)[0]


def text_fixes(wb):
    ws = wb["NonNV"]
    n = 0
    # L6, L7: the v21.9 precision sentence replaced; kept after the v21.10 tag
    for r in (6, 7):
        cell = ws[f"L{r}"]
        cur = str(cell.value)
        if Q1_NEW in cur:
            continue
        assert _head(cur).count(v2190.Q1_NEW) == 1 and OLD_TAG not in cur, (r, cur[-200:])
        cell.value = cur.replace(v2190.Q1_NEW, Q1_NEW, 1) + OLD_TAG + v2190.Q1_NEW
        n += 1
    # A2: precision basis and the #176 clause (follow-up 12); the whole v21.9 sentence kept after the v21.10 tag
    a2 = ws["A2"]
    cur = str(a2.value)
    if A2_NEW not in cur:
        assert _head(cur).count(v2190.A2_ADD) == 1 and OLD_TAG not in cur, cur
        a2.value = cur.replace(v2190.A2_ADD, A2_NEW, 1) + OLD_TAG + v2190.A2_ADD[1:]
        n += 1
    # L8 (follow-up 11; Gov_Map N407–N412 mirror it by formula)
    cell = ws["L8"]
    cur = str(cell.value)
    if L8_NEW not in cur:
        assert _head(cur).count(v2190.L8_ADD) == 1 and OLD_TAG not in cur, cur[-200:]
        cell.value = cur.replace(v2190.L8_ADD, L8_NEW, 1) + OLD_TAG + v2190.L8_ADD
        n += 1
    # L9 (follow-up 16): insertion after the v21.9 sentence
    cell = ws["L9"]
    cur = str(cell.value)
    if not cur.startswith(v2190.L9_OPEN_NEW + L9_ADD):
        assert cur.startswith(v2190.L9_OPEN_NEW), cur[:200]
        cell.value = v2190.L9_OPEN_NEW + L9_ADD + cur[len(v2190.L9_OPEN_NEW):]
        n += 1
    # Interface A368
    wi = wb["Interface"]
    t = str(wi["A368"].value)
    if A368_NEW not in t:
        assert _head(t).count(v2190.A368_NEW) == 1 and OLD_TAG not in t, t[-200:]
        wi["A368"].value = t.replace(v2190.A368_NEW, A368_NEW, 1) + OLD_TAG + v2190.A368_NEW
        n += 1
    # Inputs!H23 (follow-up 13): the v21.8 sentence rewritten in v21.9 kept after "｜原（v21.9 前）："
    wh = wb["Inputs"]
    if wh["H23"].value != H23_NEW:
        assert wh["H23"].value == v2190.H23_NEW, wh["H23"].value
        wh["H23"].value = H23_NEW
        n += 1
    return n


# ---------------------------------------------------------------- W3 governance (follow-up 15)
DC004_M_OLD = "JLL、Turner & Townsend：不動產與工程顧問（產業研究）"
DC004_M_NEW = "Turner & Townsend：工程顧問（產業研究；建造成本指數原文，E452 已讀）"
FIX = f"｜{V} 更正（修訂九；Decisions {DEC_ID}；{WO}）："


def src_fixes(wb):
    rows = v1720._rows(wb)
    n = 0
    ws, r = rows["SRC_DC_004"]
    if ws[f"M{r}"].value != DC004_M_NEW:
        assert (ws[f"K{r}"].value, ws[f"N{r}"].value, ws[f"M{r}"].value) == (3, "二手", DC004_M_OLD), (ws[f"K{r}"].value, ws[f"N{r}"].value, ws[f"M{r}"].value)
        assert ws[f"J{r}"].value == v2190.DC004_J, ws[f"J{r}"].value
        ws[f"K{r}"].value = 1
        ws[f"N{r}"].value = "一手"
        ws[f"M{r}"].value = DC004_M_NEW
        v2190._w(ws, r, FIX + "等級 3 → 1、二手 → 一手、立場說明改 Turner & Townsend（出處已是 T&T 原文，E452 為 1 級一手、逐字引文）；"
                 f"原等級＝3；原一手／二手＝二手；原立場說明＝『{DC004_M_OLD}』")
        n += 1
    # DB_Evidence E450: related SRC + SRC_HW_010 (SRC_HW_100 is its duplicate, v21.9)
    ev = wb["DB_Evidence"]
    for rr in range(5, ev.max_row + 1):
        if ev.cell(rr, 1).value == "E450":
            m = str(ev.cell(rr, 13).value)
            if "SRC_HW_010" not in m:
                assert m == "SRC_HW_052、SRC_HW_100", m
                ev.cell(rr, 13).value = m + "、SRC_HW_010"
                n += 1
            break
    else:
        raise AssertionError("DB_Evidence E450 missing")
    return n


def load_bearing_date(wb):
    """Follow-up 14 (engineering): Load_Bearing!C3 (build date read by LB_Days) = the date in the version file name (VERSION), not a separate constant."""
    ws = wb["Load_Bearing"]
    assert str(ws["A3"].value).startswith("建置日"), ws["A3"].value
    d = VERSION.split("_", 1)[0]
    assert len(d) == 8 and d.isdigit(), VERSION
    put(ws, "C3", f"{d[:4]}-{d[4:6]}-{d[6:]}", F_CALC)


# ---------------------------------------------------------------- W3 DB_Evidence E560
E560 = [
    "E560", DATE,
    "TPU v7／Trainium3 產出比查核：v21.9 原生精度口徑值與 TK roofline 一致，但 TK 引擎把推論當算力受限（VR200 改 FP8 產出減半；TPU 只改權重 4 bit 產出 0.30→0.31），"
    "原生精度等於固定 2 倍懲罰；外部證據不支持「4 bit 好處只歸 NVIDIA」；另有世代錯配（TPU v7 對 VR200）→ 基準改 FP8 對齊、原生精度降為低端（採用，v21.10 W1）；"
    "每 token 成本比基準 TPU 2.0 → 1.061、Trn3 4.357 → 2.179",
    "查核 " + EVD + "（README、外部查核、m3／m3b 試算）",
    "Assumed（每 kW 峰值算力比 × 效率因子 f；基準與高端為 FP8 對齊，PR #172 E 節方法一；低端為各晶片最高原生精度）",
    "NonNV B6:D7；Interface 第 370、371 列（IF_NonNV_Out_TPU／IF_NonNV_Out_Trn）",
    "TPU v7 0.25／0.35／0.40、Trainium3 0.06／0.14／0.25（v21.9 原生精度口徑）；每 token 成本比基準 TPU 2.0、Trn3 4.357",
    "TPU v7 0.35／0.66／0.84、Trainium3 0.14／0.28／0.50（基準＝FP8 對齊；低端＝原生精度基準值；高端＝FP8 對齊高端）",
    "採用（建議甲，Andy 2026-11-04 照建議，" + V + " W1）", V,
    "判定依據：Andy 2026-11-04 12:55「需要我决定的都按照你的建议去执行」；外部證據：InferenceX 實測 Blackwell FP4 對 FP8 吞吐 2.2–8.2 倍、"
    "每 kW HBM 頻寬 TPU v7 為 VR200 的 0.97–1.11、SemiAnalysis AgentX（Preview）與 InferenceX 結果分歧｜" + WO,
    "已處理", DASH, DASH, "IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（值改變，各 3 格）；其餘契約名稱不變", 3,
    "利害關係方（Google、NVIDIA）＋第三方（SemiAnalysis，Preview）",
    "採用（產出比基準改 FP8 對齊，原生精度降為低端）｜" + V + " 新增列"]


def evidence_append(wb):
    ws = wb["DB_Evidence"]
    if any(ws.cell(r, 1).value == E560[0] for r in range(5, ws.max_row + 1)):
        return 0
    r = max(rr for rr in range(5, ws.max_row + 1) if ws.cell(rr, 1).value not in (None, "")) + 1
    assert ws.cell(r - 1, 1).value == "E559", ws.cell(r - 1, 1).value
    for i, v in enumerate(E560):
        put(ws, f"{L(i + 1)}{r}", v, F_CALC, wrap=i in (2, 3, 4, 5, 6, 7, 8, 10, 14, 16, 17))
    return 1


# ---------------------------------------------------------------- W3 Decisions SL67-01
def _decisions():
    return [[DEC_ID, V, "v21.10 TPU、Trainium3 產出比基準改 FP8 對齊（原生精度降為低端）與 v21.9 核對的文字治理修正",
             "W1：NonNV B6:D6（TPU v7 產出比）0.25／0.35／0.40 → 0.35／0.66／0.84；B7:D7（Trainium3 產出比）0.06／0.14／0.25 → 0.14／0.28／0.50"
             "（建議甲：基準＝FP8 對齊，VR200 也以 FP8 比，PR #172 E 節方法一；低端＝各晶片最高原生精度基準值（v21.9 基準）；高端＝FP8 對齊高端；Assumed；E560）。"
             "方向計數：W1 放寬 2 列（基準上移、區間擴大，保留原生精度為低端），縮窄 0；每 token 成本比基準 TPU 2.0 → 1.061、Trn3 4.357 → 2.179。"
             "W2：NonNV L6、L7、A2、L8 與 Interface A368 說明更新，Inputs!H23 補 v21.8 原句、NonNV L9 補 Jalapeño 證據出處（追加 11、12、13、16），"
             "被改寫的原文逐字保留於「｜原（v21.10 前）：」（H23 為「｜原（v21.9 前）：」）之後（修訂九）。"
             "W3（不動數值）：Load_Bearing!C3 改由版本檔名日期帶出（追加 14）；DB_Evidence E450 相關 SRC 加 SRC_HW_010；SRC_DC_004 等級 3 → 1、二手 → 一手、"
             "立場說明改 Turner & Townsend（追加 15；原值保留於 W 欄）；DB_Evidence E560；README B5 加 v21.10 段。"
             "契約名稱的值改變只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串；契約不升版（v0.27）。Andy 原話與依據：" + DEC_BY,
             DATE, DEC_BY, "v21.10 已建",
             "NonNV B6:D7、L6／L7／L8／L9／A2；Interface 第 370、371 列與 A368；Inputs H23；Load_Bearing C3；SRC_DC_004；DB_Evidence E450、E560；README B5",
             f"{WO} W1–W3", "否"]]


def apply(wb, append_text):
    log = {"text_fixes": text_fixes(wb), "src_fixes": src_fixes(wb)}
    log["evidence"] = evidence_append(wb)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ---------------------------------------------------------------- README
_prev = v2190.README_VERSION.split("_Tokenomics_", 1)[1]
README_VERSION = (VERSION + "（次版，底版 v21.9：" + WO + "——v21.10：契約名稱值改變者只有 IF_NonNV_Out_TPU、IF_NonNV_Out_Trn（各 3 格）與版本字串；"
                  "NonNV TPU v7 產出比 0.25／0.35／0.40 → 0.35／0.66／0.84、Trainium3 0.06／0.14／0.25 → 0.14／0.28／0.50（基準改 FP8 對齊，各晶片最高原生精度降為低端；"
                  "Andy 2026-11-04 照建議；Assumed；E560）；NonNV L6／L7／L8／L9／A2、Interface A368 與 Inputs H23 說明更新（原文保留於「｜原（v21.10 前）：」後）；"
                  "v21.9 核對的治理修正（Load_Bearing!C3 取版本檔名日期、DB_Evidence E450 相關 SRC 加 SRC_HW_010、SRC_DC_004 等級 3 → 1 與一手；不動數值）；"
                  "Decisions SL67-01。）以下為 " + _prev)
README_TITLE = V + v2190.README_TITLE[len(v2190.V):]

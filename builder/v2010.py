# v20.1 (work order docs/workorders/20261023_v20.1_LifeSelf主口徑.md r0, branch claude/v20-1): Interface LifeSelf rows read the per-generation discounted L and the revenue-side m;
# L1_PriceReqBE (+_Lo/_Hi) switches to the main-basis L.
# MINOR version: no new contract names (L1_LDiscGen is an engineering name, not in the downstream contract); 8 IFW_*_LifeSelf names and L1_PriceReqBE (+_Lo/_Hi) change value and formula.
#   W1  New defined name L1_LDiscGen = Cap_In!$C$322:$F$322 (per-generation discounted L_rel, base).  Interface rows 321-328 (C:Q) = _Prod x INDEX(L1_LDiscGen,1,g) x L1_M
#       (g = 1 Hopper, 2 GB200, 3 GB300, 4 VR200, Rubin Ultra uses 4); section title (row 320) and the 8 A labels.  Built right after v1000.interface_l (before contract columns / dependency tracing).
#   W2  L1 row 93 L1_PriceReqBE (+_Lo/_Hi): L1_LTotal -> L1_LTotalFleetVDisc (_Hi/_Lo likewise), error text "L 非數字（本情境）", B/C label text (via gov._rows_l1 hook).
#   W3  Text only: Cap_In row 238 reads L1_LTotalFleetVDisc (C233 itself is untouched), Cap_In A313 label, Interface K title tail.
#   W4  Decisions SL56-01, README row/version.
# Every write to an Excel-owned cell is guarded (old text / already-applied test).
import re

from openpyxl.workbook.defined_name import DefinedName

import v1000
import v1410
import v2000

VERSION = "20261023_Tokenomics_v20.1"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-23"
V = "v20.1"
WO = "工作單 docs/workorders/20261023_v20.1_LifeSelf主口徑.md（r0）"
DEC_ID = "SL56-01"
DEC_BY = ("Andy 2026-10-18 10:20 L 定義「本来就是应该用自己每个世代来算的」；2026-10-21 14:17／15:39／15:59 m 定義（m＝實收單價 ÷ 有效牌價，只有收入面）；"
          "2026-10-22 07:34 公式「P＝token 牌價 × m × L ×（1 − 預設折扣）」；2026-10-23 02:17「下一步是 v20.1：Interface LifeSelf（A321–A328）改用主口徑 L 與新 m（L1_M），並併入交接檔第 5 節的小項」；"
          "2026-10-23 08:54「請繼續」＝J1–J6 全部採預設")
NAME = "L1_LDiscGen"
NAME_REF = "Cap_In!$C$322:$F$322"
G_OF = {"C": 1, "D": 1, "E": 1, "F": 2, "G": 2, "H": 2, "I": 3, "J": 3, "K": 3, "L": 4, "M": 4, "N": 4, "O": 4, "P": 4, "Q": 4}      # Hopper, GB200, GB300, VR200, Rubin Ultra uses VR200 (g = 4)
OLD_LBL = "（L1_LTotal、L1_MFleet）"
NEW_LBL = "（L1_LDiscGen、L1_M）"
OLD_FRM = "IF(AND(ISNUMBER(L1_LTotal),ISNUMBER(L1_MFleet)),"
NEW_TITLE = ("L. 情境：自算 L、m（v20.1 起）：IFW_*_LifeSelf ＝ IFW_*_Prod × 該世代折現 L（L1_LDiscGen；Andy 2026-10-18 L 定義：各世代相對自身起點）× 收入面 m（L1_M，2026 Q2 年化；Andy 2026-10-21 定義）。"
             "_Prod 已含有效牌價（表列 ×（1 − B4_Disc））。仍為理想上限：Q 是模型產能（IF_Util × CTL_ProdDerate、全部付費），未扣服務占比、免費占比與實際利用率；實際口徑見 L1_RevGW_PQ_VR200。"
             "m 以 OpenAI 有效牌價定義，套到前緣單價列（325–328）為近似。假設 m 在壽命期內不變（v18.0 待判斷 2）。控制值 CTL_PriceLife、CTL_Monetize 仍為 1（IFW_*_Life 不變）。"
             "本節名稱不得被任何公式讀取（parity：Interface、Load_Bearing、Gov_Map 以外引用數＝0）；只供並列比較，不是下游基準。"
             "v10.0–v20.0 口徑（× L1_LTotal × L1_MFleet，後者為 token 帳診斷，不是 m）已停用。")
NOTE_Z = ("v20.1：C–N 欄＝_Prod × 該世代折現 L（L1_LDiscGen 的 Hopper／GB200／GB300／VR200 格）× L1_M；O–Q 欄（Rubin Ultra）起點晚於錨點的世代，"
          "相對自身起點的 L 公式與 VR200 相同，不另設輸入，故取 VR200 格（g＝4）")
Z_HDR = "說明（v20.1）"
TAIL_K = "（v20.0 起 2025 校準主口徑改為 GW 優先 L1_ServeGW_GW25；支出路線為對照）"
K_HEAD = "IF_AllocServeGW 為支出路線主口徑"
A238_OLD = "判讀：L_total 對 Gov_Map CTL_PriceLife 區間（GM593 低／高）"
A238_NEW = "判讀：主口徑 L（L1_LTotalFleetVDisc，世代起點＋折現）對 Gov_Map CTL_PriceLife 區間（GM593 低／高）；v20.1 前讀 L_total"
A313_OLD = "各世代 L（相對自身起點）＝L1_LTotal　→ L1_LTotalV（4 格：Hopper／GB200／GB300／VR200）"
A313_NEW = "各世代 L（現行：四格皆為 L1_LTotal，2025＝第 0 年，非各世代自身起點；各世代自身起點、折現版見第 322 列／L1_LDiscGen）　→ L1_LTotalV"
PRICE_B_OLD = "回本所需實收單價（L＝L1_LTotal）"
PRICE_B_NEW = "回本所需實收單價（L＝L1_LTotalFleetVDisc，世代起點＋折現主口徑；v20.1 起）"
PRICE_C_TAIL = "｜成本範圍仍為 L1_FleetBreakeven2025（v20.0 全部算力口徑未套用，見待判斷）"
PRICE_H_OLD = "低＝L 取高端（0.498）、高＝L 取低端（1.692）"
PRICE_H_NEW = "低＝L 取高端（1.138）、高＝L 取低端（0.479）"


# ================================================================== W1: Interface LifeSelf rows (called right after v1000.interface_l)
def interface_l_patch(wb, ifl):
    ws = wb["Interface"]
    assert "L1_LDiscGen" not in wb.defined_names or wb.defined_names[NAME].attr_text == NAME_REF
    c322 = wb["Cap_In"]["A322"].value
    assert isinstance(c322, str) and "折現 L_rel" in c322 and "各世代" in c322, c322
    wb.defined_names[NAME] = DefinedName(NAME, attr_text=NAME_REF)
    ws.cell(ifl["start"], 1).value = NEW_TITLE
    ws[f"Z4"].value = Z_HDR
    n = 0
    for nm, r in ifl["made"]:
        base = nm.replace("IFW_", "").replace("_LifeSelf", "")
        sh, p = v1000._name_row(wb, f"IFW_{base}_Prod")
        a = str(ws.cell(r, 1).value)
        assert OLD_LBL in a, a
        ws.cell(r, 1).value = a.replace(OLD_LBL, NEW_LBL)
        for X, g in G_OF.items():
            cur = ws[f"{X}{r}"].value
            assert isinstance(cur, str) and OLD_FRM in cur, (X, r, cur)
            ws[f"{X}{r}"].value = (f'=IF(ISNUMBER({X}{p}),IF(AND(ISNUMBER(INDEX({NAME},1,{g})),ISNUMBER(L1_M)),{X}{p}*INDEX({NAME},1,{g})*L1_M,"L、m 非數字（本情境）"),{X}{p})')
            n += 1
        ws[f"Z{r}"].value = NOTE_Z
    assert n == 120, n
    return n


# ================================================================== W2: L1 row PriceReqBE (hook in gov._rows_l1, like v2000.l1_patch)
def l1_patch(R):
    out = []
    for row in R:
        row = list(row)
        if row[0] == "PriceReqBE":
            assert row[1] == PRICE_B_OLD, row[1]
            row[1] = PRICE_B_NEW
            assert row[2].endswith("÷ L_total；v8.0 L4"), row[2]
            row[2] = row[2] + PRICE_C_TAIL
            for k in (3, 4, 5):
                new = re.sub(r"\bL1_LTotal(_Hi|_Lo)?\b", lambda m: "L1_LTotalFleetVDisc" + (m.group(1) or ""), row[k])
                assert new != row[k] and "m 非數字（本情境）" in new
                row[k] = new.replace("m 非數字（本情境）", "L 非數字（本情境）")
            assert row[7] == PRICE_H_OLD, row[7]
            row[7] = PRICE_H_NEW
        out.append(tuple(row))
    return out


# ================================================================== W3: text-only edits
def text_fixes(wb):
    n = 0
    ci = wb["Cap_In"]
    for col, nm in (("C", "L1_LTotalFleetVDisc"), ("D", "L1_LTotalFleetVDisc_Lo"), ("E", "L1_LTotalFleetVDisc_Hi")):
        cur = ci[f"{col}238"].value
        if isinstance(cur, str) and nm in cur:
            continue
        assert isinstance(cur, str) and f"{col}233" in cur and cur.startswith("=IF(AND("), cur[:80]
        new = f"=IF(ISNUMBER({nm})," + cur[1:].replace(f"{col}233", nm) + ",AL_UnavailTxt)"
        ci[f"{col}238"].value = new; n += 1
    if ci["A238"].value != A238_NEW:
        assert ci["A238"].value == A238_OLD, ci["A238"].value
        ci["A238"].value = A238_NEW; n += 1
    if ci["A313"].value != A313_NEW:
        assert ci["A313"].value == A313_OLD, ci["A313"].value
        ci["A313"].value = A313_NEW; n += 1
    ws = wb["Interface"]
    r = next(rr for rr in range(300, 330) if isinstance(ws.cell(rr, 1).value, str) and ws.cell(rr, 1).value.startswith("K. 服務 GW 的 token 路線對照"))
    a = ws.cell(r, 1).value
    if TAIL_K not in a:
        assert K_HEAD in a, a
        ws.cell(r, 1).value = a.replace(K_HEAD, K_HEAD + TAIL_K, 1); n += 1
    return n


# ================================================================== Decisions
def _decisions():
    return [[DEC_ID, V, "v20.1 Interface LifeSelf 改用世代折現 L × 收入面 m；回本所需實收單價改主口徑 L",
             "W1：新工程類具名範圍 L1_LDiscGen（Cap_In C322:F322，各世代折現 L_rel）；Interface 第 321–328 列 8 個 IFW_*_LifeSelf 改為 _Prod × 該世代 L1_LDiscGen × L1_M"
             "（Rubin Ultra 欄取 VR200 的 L）。W2：L1_PriceReqBE（＋_Lo／_Hi）的 L 由 L1_LTotal 改為主口徑 L1_LTotalFleetVDisc（成本範圍仍為 L1_FleetBreakeven2025）。"
             "W3：Cap_In 第 238 列判讀改讀主口徑 L（C233 不改）；第 313 列標籤；Interface K 節標題。判斷採預設：J1 各世代折現 L、J2 m＝L1_M、J3 前緣單價列同樣乘 L×m（近似）、"
             "J4 只換 L、J5 第 238 列改讀主口徑 L、J6 不新增 LifeSelf 的 _Lo／_Hi。Andy 原話：" + DEC_BY,
             DATE, DEC_BY, "v20.1 已建", "Interface 第 320–328 列；L1 第 93 列；Cap_In 第 238、313 列；Interface K 節標題；具名範圍 L1_LDiscGen", f"{WO} W1–W5", "否"]]


def apply(wb, append_text):
    log = {"text_fixes": text_fixes(wb)}
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == DEC_ID for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README
README_VERSION = (VERSION + "（次版，底版 v20.0：" + WO + "——Interface LifeSelf（8 個 IFW_*_LifeSelf）改為 _Prod × 該世代折現 L（新工程類具名範圍 L1_LDiscGen）× L1_M；"
                  "L1_PriceReqBE（＋_Lo／_Hi）的 L 改主口徑 L1_LTotalFleetVDisc；Cap_In 第 238 列判讀改讀主口徑 L；Decisions SL56-01。無新增或刪除契約名稱。）以下為 "
                  + v2000.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v2000.README_TITLE
README_TITLE = V + _T[len(v2000.V):]
README_ROW = ("v20.1 LifeSelf 主口徑",
              "Interface L 節 IFW_*_LifeSelf 的讀法改為「_Prod × 世代折現 L（L1_LDiscGen）× L1_M」（Andy 2026-10-18 L 定義、2026-10-21 m 定義）；Rubin Ultra 欄取 VR200 的 L。仍為理想上限，不回流。"
              "L1_PriceReqBE（回本所需實收單價）的 L 改主口徑 L1_LTotalFleetVDisc（世代起點＋折現）。"
              "細節見工作單 docs/workorders/20261023_v20.1_LifeSelf主口徑.md 與 Decisions SL56-01。")

# v6.0 (work order docs/workorders/20261015_稽核修正1.md r0): downstream-contract definitions (major version; governance plan §8).
#   D7  `_Prod` is the capacity re-solved at the production derate (Theory_Rev_Prod／Fleet_1GW_Prod), not _Util x CTL_ProdDerate; `_Life` has one
#       definition (IFW_*_Life) and IF_*_Life becomes a transitional alias; the m floor / frontier-price rows use the re-solved paid-capacity ratio.
#   D8  "SLO 不可達" is text, never 0 (Perf decode rows, Unit_Cost, Theory_Rev, Training, Perf_Batch consumers); an unreachable tier is excluded and the remaining
#       mix weights are renormalised (Fleet_1GW section D); all tiers unreachable -> text.
#   D11 the pay-back premium (IF_AmortBU_*, hence IF_FullCost_*, IF_FullCostDefault_*) divides by paid tokens only.
# Decisions AF1-D7／AF1-D8／AF1-D11 (IDs D7／D8／D11 already exist in Decisions from Block 1) are appended only through gov.py (DECISIONS_V600); no input cell is changed.
import re
from copy import copy
from openpyxl.utils import get_column_letter as L
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_BOLD, F_NOTE, F_CALC, F_LINK, FILL_KEY, section
import v519
import v530
import v536

VERSION = "20261015_Tokenomics_v6.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-15"
V = "v6.0"
WO = "工作單 docs/workorders/20261015_稽核修正1.md r0"
DEC = "docs/reports/20261015_稽核判斷會議_決定.md"
ANDY = "Andy 2026-10-15 稽核判斷會議逐題決定（" + DEC + "）"
SLO = "SLO 不可達"
COLS = range(3, 18)
TIERS = ["Luna", "Sol", "Astra"]
NOTE_ALIAS = "過渡別名＝IFW_{}_Life；下一個主版刪除"


# ================================================================== D7-1／D7-2: _Prod layer rows of Interface J (re-solved SLO source)
def prod_override(wb, F):
    """name -> (formula builder, note) for IFW_TokGW_*_Prod and IFW_RevGWFront*_Prod. Rows come from the v519 targets (Theory_Rev revenue rows 11／29／47)."""
    ws = wb["Theory_Rev"]
    tok_row = {}
    for t, (trow, base) in enumerate(v519.TARGETS[3:6]):
        assert base == f"IF_RevGW_{TIERS[t]}", base
        assert str(ws.cell(trow - 1, 1).value).startswith("每 GW 產出"), (trow - 1, ws.cell(trow - 1, 1).value)
        tok_row[t] = trow - 1
    ov = {}
    for t, tk in enumerate(TIERS):
        tr = tok_row[t]
        ov[f"IFW_TokGW_{tk}_Prod"] = (lambda X, tr=tr: f"=Theory_Rev_Prod!{X}{tr}",
                                      f"（＝Theory_Rev_Prod 第 {tr} 列：生產折減 CTL_ProdDerate 下重解 SLO 後的產出 × IF_Util，與營收 _Prod 同源；v6.0 D7-1）")
        ov[f"IFW_RevGWFront_{tk}_Prod"] = (
            lambda X, tr=tr, t=t: f"=IF(ISNUMBER(Theory_Rev_Prod!{X}{tr}),Theory_Rev_Prod!{X}{tr}*INDEX(B4_FrontRef,1,{t+1})/1E9,Theory_Rev_Prod!{X}{tr})",
            f"（＝Theory_Rev_Prod 第 {tr} 列重解後產出 × 前緣單價；v6.0 D7-2）")
    pay = lambda X: "+".join(f"IF(ISNUMBER(Fleet_1GW_Prod!{X}{F[f'p{t}']}),Fleet_1GW_Prod!{X}{F[f'p{t}']}*INDEX(B4_FrontRef,1,{t+1}),0)" for t in range(3))
    ov["IFW_RevGWFleetFront_Prod"] = (lambda X: f'=IF(Fleet_1GW_Prod!{X}{F["ok"]}=1,({pay(X)})/1E9,"{SLO}")',
                                      "（＝Fleet_1GW_Prod 付費 token（重解後）× 前緣單價；v6.0 D7-2）")
    return ov


def patch_j_header(wb, IFJ):
    ws = wb["Interface"]
    cell = ws.cell(IFJ["start"], 1)
    old = "營收 _Prod 讀 G 節（重解 SLO 後的值）、token 產能 _Prod 為線性乘法"
    assert old in cell.value
    cell.value = cell.value.replace(old, "_Prod 一律為重解 SLO 後的值（營收讀 G 節；token 產能與前緣營收讀 Theory_Rev_Prod／Fleet_1GW_Prod；v6.0 D7-1／D7-2）") \
        .replace("H 節 _Life（不含折減", "H 節 IF_*_Life 為本節 IFW_*_Life 的過渡別名（下一個主版刪除）；原 H 節 _Life（不含折減")


# ================================================================== D7-3: IF_*_Life becomes an alias of IFW_*_Life
def life_alias(wb, IFJ):
    import v522
    tr = wb["Theory_Rev"]; itf = wb["Interface"]
    for trow, base in v522.TARGETS:
        rr = v522.TR_ROWS[base]; stem = base[3:]
        for k, c in enumerate(COLS, start=1):
            tr.cell(rr, c).value = f"=INDEX(IFW_{stem}_Life,1,{k})"
        lab = tr.cell(rr, 1).value
        tr.cell(rr, 1).value = lab.replace("（× 壽命期價格係數 L × 變現率 m）", "（過渡別名＝IFW_%s_Life；下一個主版刪除）" % stem)
        brow = int(re.match(r"Interface!\$C\$(\d+):", wb.defined_names[base + "_Life"].attr_text).group(1))
        a = itf.cell(brow, 1).value
        assert "（× L × m）" in a, a
        itf.cell(brow, 1).value = a.replace("（× L × m）", "（× L × m；" + NOTE_ALIAS.format(stem) + "）")
        # self-check rows: Interface alias vs IFW (identity)
        fr = v522.TR_FLAGS[base]
        tr.cell(fr, 1).value = f"{base}_Life：Interface 別名 vs IFW_{stem}_Life（應相同）"
        for k, c in enumerate(COLS, start=1):
            a_, b_ = f"INDEX({base}_Life,1,{k})", f"INDEX(IFW_{stem}_Life,1,{k})"
            tr.cell(fr, c).value = (f"=IF(AND(ISNUMBER({a_}),ISNUMBER({b_})),IF(ABS({a_}-{b_})<=0.000000001,0,1),"
                                    f"IF(AND(NOT(ISNUMBER({a_})),NOT(ISNUMBER({b_}))),IF({a_}={b_},0,1),1))")
    tr.cell(v522.TR_START + 6, 1).value = ("自我檢查（Checks Y／X7；v6.0 D7-3 起）：Interface 的 IF_*_Life 別名列 − 對應 IFW_*_Life 的絕對差 ≤ 1e-9（兩邊皆為文字時須文字相同）；0＝相符，1＝不符")
    tr.cell(v522.TR_START, 1).value = ("D. 營收實現（X7，v5.22；v6.0 D7-3 起為 IFW_*_Life 的過渡別名，下一個主版刪除）：IFW_*_Life＝重解 SLO 的 _Prod 列 × 壽命期價格係數 L（CTL_PriceLife）× 變現率 m（CTL_Monetize）；"
                                       "基準列為文字（SLO 不可達）時輸出相同文字")
    for r in range(1, itf.max_row + 1):
        v = itf.cell(r, 1).value
        if isinstance(v, str) and v.startswith("H. 營收實現並列輸出"):
            itf.cell(r, 1).value = v.replace("H. 營收實現並列輸出（X7，v5.22）", "H. 營收實現並列輸出（X7，v5.22；v6.0 D7-3 起 IF_*_Life＝IFW_*_Life 的過渡別名，下一個主版刪除）")
            break
    ck = wb["Checks"]
    for r in range(1, ck.max_row + 1):
        if ck.cell(r, 1).value == "X7":
            ck.cell(r, 2).value = "營收實現別名：Interface 的 IF_*_Life 不等於對應 IFW_*_Life 的格數（絕對差 > 1e-9；文字列須相同；v6.0 D7-3）"


# ================================================================== D7-1: _Prod identity (Checks Z1)
def prod_identity(wb, IFJ):
    """Theory_Rev rows 101+: _Prod revenue ÷ _Prod token = tier price (OpenAI and Front), 1e-9 relative. Returns (first, last)."""
    tr = wb["Theory_Rev"]
    r0 = tr.max_row + 2
    section(tr, r0, "E. _Prod 恆等式自我檢查（v6.0 D7-1；Checks Z1）：IFW_RevGW*_Prod × 1E9 ÷ IFW_TokGW_*_Prod ＝ 該層級單價（B4_EffRef／B4_FrontRef），相對差 ≤ 1e-9；"
                      "兩邊皆為文字須相同；0＝相符，1＝不符", 17)
    r = r0 + 1; first = r
    for kind, rev, ref in (("OpenAI 有效單價", "IFW_RevGW_{}_Prod", "B4_EffRef"), ("前緣單價", "IFW_RevGWFront_{}_Prod", "B4_FrontRef")):
        for t, tk in enumerate(TIERS):
            put(tr, f"A{r}", f"{tk}｜{kind}：_Prod 營收 ÷ _Prod token vs {ref}", F_NOTE)
            for k, c in enumerate(COLS, start=1):
                rv, tok, px = f"INDEX({rev.format(tk)},1,{k})", f"INDEX(IFW_TokGW_{tk}_Prod,1,{k})", f"INDEX({ref},1,{t+1})"
                put(tr, f"{L(c)}{r}",
                    f"=IF(AND(ISNUMBER({rv}),ISNUMBER({tok})),IF({tok}>0,IF(ABS({rv}*1E9/{tok}-{px})<=0.000000001*{px},0,1),1),"
                    f"IF(AND(NOT(ISNUMBER({rv})),NOT(ISNUMBER({tok}))),IF({rv}={tok},0,1),1))", fmt="0")
            r += 1
    return first, r - 1


def checks_z(wb, rows):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "Z. 契約定義檢查（工作單 稽核修正1，v6.0）：Z1 為 ERROR 計入 GOV_Errors", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{L(i+1)}{r}", h, F_BOLD)
    r += 1
    first, last = rows
    put(ws, f"A{r}", "Z1"); put(ws, f"B{r}", "_Prod 恆等式：同一層級 _Prod 營收 ÷ _Prod token 不等於該層級單價（OpenAI 有效單價與前緣單價）的格數（相對差 > 1e-9；v6.0 D7-1）"); put(ws, f"C{r}", "ERROR", F_BOLD)
    put(ws, f"D{r}", f"=SUM(Theory_Rev!C{first}:Q{last})", fmt="0")
    put(ws, f"E{r}", f"Theory_Rev 第 {first}–{last} 列 × C:Q（6 × 15＝90 格）", F_NOTE)
    ref = wb.defined_names["GOV_Errors"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "ERROR 合計（CI 讀取 GOV_Errors；含 G、H、X、Y、Z 節）"
    return r


# ================================================================== D7-2: paid-capacity ratio at the production derate (Alloc H section)
def alloc_prod_ratio(wb, R, F):
    """Appends Alloc section H: per-generation paid capacity re-solved at CTL_ProdDerate (Fleet_1GW_Prod ÷ Fleet_1GW paid tokens x AL_CapPaid), the generation blend
    and the ratio AL_ProdRatioPaid. Nothing above moves."""
    ws = wb["Alloc"]
    r = ws.max_row + 2
    section(ws, r, "H. 生產折減下的付費產能比（v6.0 D7-2；欄 C–F＝服務世代 Hopper／GB200／GB300／VR200）：以 CTL_ProdDerate 重解 SLO 後的付費產能 ÷ 基準；取代線性的 CTL_ProdDerate", 7); r += 1
    col = lambda c: f"{c}${R['col']}"
    tp_b = lambda c: f"INDEX(Fleet_1GW!$C${F['Tp']}:$Q${F['Tp']},1,{col(c)})"
    tp_p = lambda c: f"INDEX(Fleet_1GW_Prod!$C${F['Tp']}:$Q${F['Tp']},1,{col(c)})"
    put(ws, f"A{r}", "各世代每 GW 年付費產能（生產折減；重解 SLO）＝基準產能 × Fleet_1GW_Prod ÷ Fleet_1GW 的付費 token 總量", wrap=True); put(ws, f"B{r}", "M tok/GW/年")
    for c in "CDEF":
        put(ws, f"{c}{r}", f'=IF(AND(ISNUMBER({c}{R["capp"]}),ISNUMBER({tp_b(c)}),ISNUMBER({tp_p(c)})),{c}{R["capp"]}*{tp_p(c)}/{tp_b(c)},"{SLO}")', fmt="#,##0")
    put(ws, f"G{r}", "付費 token 總量同式於 Fleet_1GW 第 %d 列（兩邊 GW 配置相同，比值即每 GW 產能比）" % F["Tp"], F_NOTE)
    wb.defined_names["AL_CapPaidProd"] = DefinedName("AL_CapPaidProd", attr_text=f"Alloc!$C${r}:$F${r}")
    cap = r; r += 1
    ss = [f"{c}${R['share']}" for c in "CDEF"]; cc = [f"{c}${cap}" for c in "CDEF"]
    # v6.2 2-1-c: a generation whose re-solved capacity is text (no reachable tier) drops out and the mix is renormalised over the rest (same rule as Alloc section B)
    den = "(" + "+".join(f"IF(AND({s}>0,ISNUMBER({k})),{s},0)" for s, k in zip(ss, cc)) + ")"
    num = "+".join(f"IF(AND({s}>0,ISNUMBER({k})),{s}*{k},0)" for s, k in zip(ss, cc))
    put(ws, f"A{r}", "世代組合後每 GW 年付費產能（生產折減）＝Σ 世代占比 × 各世代產能（只含可服務世代，占比重新正規化）", wrap=True); put(ws, f"B{r}", "M tok/GW/年")
    put(ws, f"C{r}", f'=IF({den}>0,({num})/{den},"{SLO}")', fmt="#,##0")
    wb.defined_names["AL_BlendPaidProd"] = DefinedName("AL_BlendPaidProd", attr_text=f"Alloc!$C${r}"); r += 1
    put(ws, f"A{r}", "付費產能比（生產折減重解 ÷ 基準）　→ Cap_In 第 115 列「利用率修正（上限）」", wrap=True); put(ws, f"B{r}", "x")
    put(ws, f"C{r}", f'=IF(AND(ISNUMBER(AL_BlendPaidProd),ISNUMBER(AL_BlendPaid)),IF(AL_BlendPaid>0,AL_BlendPaidProd/AL_BlendPaid,"{SLO}"),"{SLO}")', fmt="0.0000", fill=FILL_KEY)
    put(ws, f"G{r}", "2025 世代組合下約 0.712（線性 CTL_ProdDerate 為 0.85）；m 下限 ∝ 1 ÷ 此比", F_NOTE)
    wb.defined_names["AL_ProdRatioPaid"] = DefinedName("AL_ProdRatioPaid", attr_text=f"Alloc!$C${r}")
    R["prodratio"] = r
    return r


# ================================================================== Decisions D7／D8／D11 (10 columns; layout of v530–v536)
_D = [
    ("D7", "`_Prod`／`_Life` 統一定義",
     "(1) IFW_TokGW_*_Prod 改讀 Theory_Rev_Prod 第 10／28／46 列（生產折減 CTL_ProdDerate 下重解 SLO 後的產出），與營收 _Prod 同源；同層級 _Prod 營收 ÷ _Prod token＝層級單價（Checks Z1，1e-9）；"
     "(2) m 下限（Cap_In 第 115 列）與前緣單價 _Prod（IFW_RevGWFront*、IFW_RevGWFleetFront_Prod）改用重解後的付費產能比（Alloc H 節 AL_ProdRatioPaid），不再用線性 CTL_ProdDerate；"
     "(3) IFW_*_Life 為唯一定義，IF_RevGW_*_Life、IF_RevGWFleet_Life 改為過渡別名（下一個主版刪除）；(4) 下游契約第 2 條改寫。" ,
     "Interface J 節（IFW_TokGW_*_Prod／_Life、IFW_RevGWFront*_Prod）；Interface H 節；Theory_Rev D、E 節；Cap_In 第 115 列；Alloc H 節；Checks X7、Z1；docs/plan/Tokenomics_downstream_contract.md 第 2、5 節", "D7-1–D7-4"),
    ("D8", "「不可達」的語意",
     "SLO 不可達時輸出文字「SLO 不可達」，不輸出 0：(1) Perf／Perf_Batch／Sens_Perf 的 decode 每請求 GPU 秒、每架與每 GW 產出、每 M decode GPU 秒改為文字，Unit_Cost、Theory_Rev 單一層級列隨之；"
     "(2) Fleet_1GW 只排除不可達的層級、其餘層級權重依原比例重新正規化（D 節列出排除層級與重新正規化前的權重合計），全部層級不可達才整欄文字；Amortize、Theory_Rev 機隊列只計可達層級；"
     "(3) Training、Perf_Batch 消費端遇文字讓該列輸出文字，不當作 0 GPU 小時；Alloc 的研發 GW、Q1、Q2 遇文字輸出文字；(4) 契約第 2 條新增「名稱輸出為文字時，代表不可用」。"
     "Perf 第 77 列（TTFT）仍未納入可達判斷：基準下 Hopper Astra 為「否」，納入會改變基準值，列待 Project 判斷。",
     "Perf／Perf_Batch／Sens_Perf 第 93–99、103、105 列；Unit_Cost；Fleet_1GW 第 18–30 列與 D 節；Amortize；Theory_Rev A、B 節；Training／Sens_Train；Alloc B–E 節", "D8-1–D8-5"),
    ("D11", "回本溢價與攤提的分母",
     "IF_AmortBU_*（回本所需單價溢價）的分母由付費＋免費 token 改為只計付費 token（Amortize 第 12／21／31 列；列標籤寫明）；IF_FullCost_*、IF_FullCostDefault_* 隨之。"
     "快取命中造成的攤提閉合 0.82–0.88（G01）屬 D9，本版不處理。",
     "Amortize 第 12、13、21、22、31、32 列；IF_AmortBU_*、IF_FullCost_*、IF_FullCostDefault_*", "D11-1、D11-2"),
]
DECISIONS_V600 = [[f"AF1-{i}", V, f"稽核判斷會議 {i}：{t}", txt, DATE, f"{ANDY}", "v6.0 已建", where, f"{WO} {sec}", "否"] for i, t, txt, where, sec in _D]


# ================================================================== README
README_VERSION = (VERSION + "（主版：下游契約定義變更，工作單 docs/workorders/20261015_稽核修正1.md r0——D7 `_Prod` 為重解 SLO 後的產能（IFW_TokGW_*_Prod 讀 Theory_Rev_Prod；m 下限與前緣單價改用重解後的付費產能比 AL_ProdRatioPaid），"
                  "`_Life` 唯一定義為 IFW_*_Life（IF_*_Life 為過渡別名，下一個主版刪除），Checks Z1 為 _Prod 恆等式；D8 SLO 不可達輸出文字、不輸出 0（Perf／Training 消費端），"
                  "Fleet_1GW 排除不可達層級並重新正規化；D11 回本溢價分母改為付費 token（IF_AmortBU_*／IF_FullCost_*／IF_FullCostDefault_* 上升）；Decisions D7／D8／D11）。以下為 "
                  + v536.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v536.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v536.VERSION.split("_")[-1]):]
README_ROW = ("契約定義變更（v6.0）",
              "`_Prod`＝生產折減（CTL_ProdDerate）下重解 SLO 後的值：營收讀 Interface G 節，token 產能讀 Theory_Rev_Prod，前緣單價營收＝重解後 token × 前緣單價；不再是 _Util × CTL_ProdDerate（線性）。"
              "同層級 _Prod 營收 ÷ _Prod token＝層級單價（Checks Z1）。`_Life`＝_Prod × CTL_PriceLife × CTL_Monetize，唯一定義為 IFW_*_Life；IF_RevGW_*_Life、IF_RevGWFleet_Life 為過渡別名（下一個主版刪除）。"
              "名稱輸出為文字（SLO 不可達）時代表不可用，下游不得以 0 代入；Fleet_1GW D 節：不可達層級被排除，其餘層級權重重新正規化，並列出排除層級與重新正規化前的權重合計。"
              "回本所需單價溢價（IF_AmortBU_*）分母＝付費 token。")

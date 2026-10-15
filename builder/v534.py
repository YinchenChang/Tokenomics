# v5.34 (work order docs/workorders/20261014_v5.34.md r0.1): monetisation rate m split by charging model, token-account closure and the
# quarterly m series (chat-side judgements J15–J21; Andy 2026-10-14 15:35「我能說甚麼呢，你已經包括我的想法了。關於第6點，這個m當然是實驗室(OAI)視角」、
# 15:39「同意，請進行。」、15:49 r0.1「兩件事我都同意。」).
#   B1 SRC_Demand SRC_DEM_069–071 (N01 2026 Q1 revenue, N03 2026 inference spend forecast (Alt), N04 API share 0.15–0.20); SRC_DEM_042／060 notes;
#      DB_Evidence E325–E337 (N01–N13).
#   B2 Cap_In H8「m 分拆」: three-way 2025 revenue split (consumer subscription SRC_DEM_039 ／ business seats Assumed 0.10 ／ API = remainder, J18),
#      token split (AL_DAPI ／ AL_DChatPaid × consumer share 0.75 ／ remainder, J19), m_API／m_消費訂閱／m_商用席次／m_整體 (self-check = L1_MImplied),
#      m_API decomposition into discount factor × implied mix factor (J16 display), subscription m floor from plan caps (N06), must-be-true row,
#      J21 Anthropic comparison rows (usage-billing share, cloud revenue share; the m_API(Anthropic) row states the missing denominator).
#   B3 Cap_In H9「token 帳三路線」: demand ／ fleet (H7) ／ ceiling tokens, residuals, closure τ* (tokens per prompt that fill the fleet), closure free
#      share; Checks M4 (demand ÷ fleet outside 0.5–2, WARN).
#   B4 L1_MAPI／L1_MSub／L1_MSeat／L1_MixFactorAPI／L1_TokPerPromptClose／L1_MAPI_Anthropic (each with _Lo／_Hi; judgement columns).
#   B5 Cap_In H10「m 季度序列」: 2025 ／ 2026 Q1 ／ 2026 Q2 ／ FY2026 columns, per-column three-way shares (r0.1), API tokens, ChatGPT prompts,
#      m by charging model, m_整體, m_fleet with the 2026 generation mix (Assumed) and the 2026 inference spend forecast (N03). Display only.
#   B6 Gov_Map rows for every new blue cell; GM441／GM442 (B4_Disc) range text 0.1–0.4 (J20) and Cap_In E12 0.3 -> 0.4 (old-value guard);
#      Decisions X35–X41; README rows; Checks M header.
# Every write to an Excel-owned cell is guarded (ID absent ／ text not yet appended ／ blue cell still at its v5.33 value), like v518–v533.
from copy import copy
from openpyxl.styles import PatternFill
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter as L
from common import put, F_IN, F_CALC, F_LINK, F_BOLD, F_NOTE, FILL_KEY, section
import v518
import v532
import v533

VERSION = "20261014_Tokenomics_v5.34"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-14"
V = "v5.34"
DASH = "—"
WO = "工作單 v5.34 r0.1"
ANDY_1535 = "Andy 2026-10-14 15:35「我能說甚麼呢，你已經包括我的想法了。關於第6點，這個m當然是實驗室(OAI)視角」（文字，未改字）"
ANDY_1539 = "Andy 2026-10-14 15:39「Gemini還沒設定好。請先自己做。」「同意，請進行。」（文字，未改字）"
ANDY_1549 = "Andy 2026-10-14 15:49「我確認一下，三個數字是OAI 2025年的營收部門佔比嗎?因為2026年OAI號稱企業營收已超過消費端」「兩件事我都同意。」（文字，未改字；r0.1）"
ANDY = f"chat 端建議（「1 GW DC 收入：L 與 m」對話串 2026-10-14），{ANDY_1535}；{ANDY_1539}；可撤回"
_N = ["N01", "N02", "N03", "N04", "N05", "N06", "N07", "N08", "N09", "N10", "N11", "N12", "N13"]
EV = {n: f"E{325 + i}" for i, n in enumerate(_N)}          # N01–N13 -> E325–E337 (next free number after E324)


def S(n): return f"SRC_DEM_{n:03d}"


# ================================================================== B1: SRC_Demand records (next free number at v5.33: SRC_DEM_069)
def _rec(n, ev, metric, val, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note, lo=None, hi=None, status="Active"):
    return dict(id=S(n), sheet="SRC_Demand", metric=metric, val=val, lo=lo, hi=hi, unit=unit, basis=basis, applies=applies, date=date,
                src=src, grade=grade, stance=stance, stance_note=stance_note, hand=hand, status=status, ev=EV[ev], s="U-V534", use=use,
                note=f"v5.34 新增（{EV[ev]}，暫編 {ev}）：{note}；{WO} B1")


_OAI_MEDIA = "OpenAI 數字經媒體轉述；有呈現成長的誘因"
SRC_NEW = [
    _rec(69, "N01", "OpenAI 季營收", 5.7, "$B", "2026 Q1；季度（確認值）", "OpenAI", "2026-05-22", "The Information 2026-05-22（二手）", 2, "利害關係方", _OAI_MEDIA, "二手",
         "Cap_In H10 2026 Q1 欄（× 4 年化）", "採用：2026 Q1 確認值；與 SRC_DEM_042（2026 Q2 6.7）成序列"),
    _rec(70, "N03", "OpenAI 2026 推論支出（預測）", 14.1, "$B", "2026 全年預測；Sacra 預測值（區間 12–18）；Azure 計價口徑視同 SRC_DEM_018", "OpenAI", "2026", "Sacra（二手預測）", 3,
         "利害關係方", "Sacra 以研究報告為業；預測值", "二手", "Cap_In H10 2026 三欄的機隊 m 推論支出（Alt：預測值）", "部分採用（Alt）：預測值，不入 2025 平均；只用於 H10 2026 欄",
         lo=12, hi=18, status="Alt"),
    _rec(71, "N04", "OpenAI API 占營收", 0.2, "%", "2026 初；Sacra 15–20%（本筆值＝高端 0.20，J18 的 API 份額依據；低欄 0.15）", "OpenAI", "2026", "Sacra（二手）", 3, "利害關係方",
         "Sacra 以研究報告為業", "二手", "Cap_In H8 2025 三分（API＝餘額 0.20）與 H10 各欄 API 份額的依據（份額為 Assumed 藍字，不連結）", "採用：J18 的 0.20 依據；2025 與 2026 的 API 份額區間 0.15–0.25／0.15–0.20",
         lo=0.15, hi=0.2),
]
SRC_LAST_ID = SRC_NEW[-1]["id"]          # SRC_DEM_071


def src_new_records():
    return SRC_NEW


SRC_UPD = {
    "SRC_DEM_042": ("SRC_Demand", {"W": ("+", f" ｜v5.34（{EV['N02']}，N02 不重登）：季營收序列 2026 Q1 5.7（{S(69)}，The Information 2026-05-22）→ Q2 6.7；年化 22.8 → 26.8")}),
    "SRC_DEM_060": ("SRC_Demand", {"W": ("+", f" ｜v5.34（{EV['N08']}，N08 不新增）：序列補點 2026-08-21 20 M、08-31 25 M（Sottiaux X 貼文；口徑未定義）")}),
}


def src_update(wb):
    n = 0; log = []
    for sid, (sh, fields) in SRC_UPD.items():
        ws = wb[sh]
        row = next((r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid), None)
        if row is None: log.append(f"{sid}: record not found"); continue
        for col, spec in fields.items():
            if v518._apply(ws[f"{col}{row}"], spec): n += 1
            else: log.append(f"{sid}!{col}: kept (already applied)")
    return n, log


# ================================================================== B6: Cap_In E12 (B4_Disc high end) 0.3 -> 0.4 (J20; written only while still 0.3)
def inputs_update(wb):
    ws = wb["Cap_In"]; log = []
    assert ws["A12"].value == "有效折扣（Batch／Flex 半價＋企業議價，加權）", ws["A12"].value
    c = ws["E12"]
    if c.value == 0.3:
        c.value = 0.4; c.font = copy(F_IN); c.fill = PatternFill(fill_type=None)
        log.append("Cap_In!E12: 0.3 -> 0.4 (v5.34 J20)")
    return log


# ================================================================== B2／B3／B5: Cap_In H8–H10 (inserted before the H-section reading row; nothing named moves)
FMT = {"$B": "#,##0.000", "%": "0.0%", "M tok/年": "#,##0", "x": "0.000", "$/M": "#,##0.0000", "GW": "0.0000", "tok": "#,##0", "$／月": "#,##0",
       "M tok/人·年": "#,##0.0", "$／人·年": "#,##0", "B 則/日": "0.00", "$B/GW/年": "0.000", "M tok/GW/年": "#,##0"}
LAB = dict(
    seat="2025 營收中商用席次占比（J18；Assumed）",
    cts="消費訂閱占 ChatGPT 付費 token 份額（J19；Assumed）",
    ads="2026 廣告營收年化（不進任何 m 的分子；H10 顯示用；Assumed）",
    fee_plus="方案上限讀法：Plus 月費（N06；對照用）",
    cap_plus="方案上限讀法：Plus 週額度 API 等值換算月額（N06；對照用）",
    fee_pro="方案上限讀法：Pro 月費（N06；對照用）",
    cap_pro="方案上限讀法：Pro 週額度 API 等值換算月額（N06；對照用）",
    q_rev="營收（$B／年；2026 欄＝季營收 × 4；FY2026 為內部預測 Assumed）",
    q_sh_cons="營收份額：消費訂閱（每欄各自輸入；2025 連結 H1）",
    q_sh_seat="營收份額：商用席次（每欄各自輸入；2025 連結 H8）",
    q_mult="FY2026 API token ÷ 2026 Q2 時點值（年均倍數；Assumed）",
    q_msgs="ChatGPT 每日則數（B 則/日；2026 為 Derived：週活比例放大）",
    q_idx="中階牌價指數（預留列，v5.35 候選；先填 1，不進任何計算）",
    q_mix_h="2026 服務世代組合：Hopper（Assumed；2025 連結 Alloc_In）",
    q_mix_gb200="2026 服務世代組合：GB200（Assumed；2025 連結 Alloc_In）",
    q_mix_gb300="2026 服務世代組合：GB300（Assumed；2025 連結 Alloc_In）",
    q_mix_vr="2026 服務世代組合：VR200（Assumed；2025 連結 Alloc_In）",
)
# H8／H9 rows: (key, label, unit, C, D, E, tag, note); key None = sub-header. {k} = this module's rows; {P_k} = v5.32 rows; {Q_k} = v5.33 rows.
# C＝基準、D＝m 低端、E＝m 高端（同 H5／H7 慣例：營收取低、token 取高；商用席次份額取低、消費 token 份額取高）。
_ANTH_TOT = f"({S(34)}+{S(35)})"
SPEC_H8 = [
    (None, f"H8. m 分拆（v5.34；{WO} B2，J16–J21）：營收三分（消費訂閱／商用席次／API）× token 三分 → m_API、m_消費訂閱、m_商用席次、m_整體（＝L1_MImplied）；"
           "m_API＝折讓因子 × 隱含組合因子（J16 顯示用）；訂閱 m 下限（方案上限讀法）；「必須為真」；J21 Anthropic 對照。欄位同 H5：C 基準、D m 低端、E m 高端"),
    ("seat", LAB["seat"], "%", 0.10, 0.05, 0.15, "Assumed", "藍字三格（登錄 Gov_Map）：基準 0.10、區間 0.05–0.15（J18）；D 欄＝席次營收取低 0.05、E 欄 0.15；API＝1 − 消費訂閱占比 − 席次占比（餘額 0.20，SRC_DEM_071 Sacra 15–20%）"),
    ("cts", LAB["cts"], "%", 0.75, 0.90, 0.60, "Assumed", "藍字三格（登錄 Gov_Map）：基準 0.75、區間 0.60–0.90（J19）；D 欄＝消費 token 取高 0.90（m_消費訂閱低端）、E 欄 0.60；商用席次 token＝餘額"),
    ("ads", LAB["ads"], "$B", 0.5, 0, 1.0, "Assumed", "藍字三格（登錄 Gov_Map）：基準 0.5、區間 0–1.0；只在 H10 2026 欄從 m_整體／m_fleet 分子扣除（J18：廣告不進任何 m 的分子）；D／E 為區間端點（不進 H8 計算）"),
    (None, "H8-1. 營收三分（2025，$B；基準欄：消費訂閱 9.149、商用席次 1.307、API 2.614）"),
    ("rev_cons", "消費訂閱營收＝營收 × 訂閱占比（H1 第 {P_share} 列）", "$B", "=C{P_rev}*C{P_share}", "=D{P_rev}*D{P_share}", "=E{P_rev}*E{P_share}", "Derived", "與 H1 訂閱營收同值；H8 起「訂閱」限定為消費訂閱"),
    ("rev_seat", "商用席次營收＝營收 × 席次占比", "$B", "=C{P_rev}*C{seat}", "=D{P_rev}*D{seat}", "=E{P_rev}*E{seat}", "Derived", ""),
    ("rev_api", "API 營收＝營收 − 消費訂閱 − 商用席次（餘額）", "$B", "=C{P_rev}-C{rev_cons}-C{rev_seat}", "=D{P_rev}-D{rev_cons}-D{rev_seat}", "=E{P_rev}-E{rev_cons}-E{rev_seat}", "Derived",
     "取代 H1 第 {P_api_share} 列的二分法（API＝1 − 訂閱占比）；H1 既有列不改，只作 L1_MImplied 的分子路徑"),
    ("sh_api", "API 占比（顯示；＝API 營收 ÷ 營收）", "%", "=C{rev_api}/C{P_rev}", "=D{rev_api}/D{P_rev}", "=E{rev_api}/E{P_rev}", "Derived", "基準 0.20（0.15–0.25）；D／E 欄為餘額，非 m 低高端的同向組合"),
    (None, "H8-2. token 三分（M tok/年；基準欄：API＝AL_DAPI、消費訂閱＝AL_DChatPaid × 0.75、商用席次＝餘額）"),
    ("tok_api", "API token（＝H3 第 {P_tok_api} 列）", "M tok/年", "=C{P_tok_api}", "=D{P_tok_api}", "=E{P_tok_api}", "Derived（輸入 Assumed）", "AL_DAPI；D／E 依 API 全年平均比例區間"),
    ("tok_cons", "消費訂閱 token＝ChatGPT 付費 token（H3 第 {P_tok_chat} 列）× 消費份額", "M tok/年", "=C{P_tok_chat}*C{cts}", "=D{P_tok_chat}*D{cts}", "=E{P_tok_chat}*E{cts}", "Derived（輸入 Assumed）", ""),
    ("tok_seat", "商用席次 token＝ChatGPT 付費 token ×（1 − 消費份額）", "M tok/年", "=C{P_tok_chat}*(1-C{cts})", "=D{P_tok_chat}*(1-D{cts})", "=E{P_tok_chat}*(1-E{cts})", "Derived（輸入 Assumed）", ""),
    (None, "H8-3. m 按收費模式（＝各自營收 × 1e9 ÷（各自 token × H4 單價第 {P_price} 列））；基準錨點 m_API 0.56、m_消費訂閱 4.26、m_商用席次 1.83、m_整體 1.743"),
    ("m_api", "m_API（2025，三分法）　→ L1_MAPI", "x", "=C{rev_api}*1000000000/(C{tok_api}*C{P_price})", "=D{rev_api}*1000000000/(D{tok_api}*D{P_price})", "=E{rev_api}*1000000000/(E{tok_api}*E{P_price})", "Derived",
     "付費 token 平均實收單價 ÷ OpenAI 有效單價（J17：實驗室視角）；H5 第 {P_m_api} 列二分法為 0.85"),
    ("m_cons", "m_消費訂閱（2025）　→ L1_MSub", "x", "=C{rev_cons}*1000000000/(C{tok_cons}*C{P_price})", "=D{rev_cons}*1000000000/(D{tok_cons}*D{P_price})", "=E{rev_cons}*1000000000/(E{tok_cons}*E{P_price})", "Derived",
     "H5 第 {P_m_sub} 列（全部 ChatGPT 付費 token）為 3.20；分母改為消費份額後上升"),
    ("m_seat", "m_商用席次（2025）　→ L1_MSeat", "x", "=C{rev_seat}*1000000000/(C{tok_seat}*C{P_price})", "=D{rev_seat}*1000000000/(D{tok_seat}*D{P_price})", "=E{rev_seat}*1000000000/(E{tok_seat}*E{P_price})", "Derived",
     "席次用量占比缺證據（SRC_DEM_045 只有 p95／中位數）"),
    ("m_all", "m_整體（token 加權）＝Σ營收 ÷（Σtoken × 單價）", "x", "=(C{rev_cons}+C{rev_seat}+C{rev_api})*1000000000/((C{tok_api}+C{tok_cons}+C{tok_seat})*C{P_price})",
     "=(D{rev_cons}+D{rev_seat}+D{rev_api})*1000000000/((D{tok_api}+D{tok_cons}+D{tok_seat})*D{P_price})", "=(E{rev_cons}+E{rev_seat}+E{rev_api})*1000000000/((E{tok_api}+E{tok_cons}+E{tok_seat})*E{P_price})", "Derived",
     "分子＝SRC_DEM_007、分母＝AL_DPaid × 單價，與 H5 第 {P_m_all} 列（L1_MImplied）必須相等"),
    ("m_chk", "自我檢查：m_整體 − L1_MImplied（H5 第 {P_m_all} 列）的絕對差（三欄）；須 ≤ 1e-9", "x", "=ABS(C{m_all}-C{P_m_all})", "=ABS(D{m_all}-D{P_m_all})", "=ABS(E{m_all}-E{P_m_all})", "Derived",
     "三分法只是把同一分子、同一分母拆開；差 > 1e-9 代表 H8 公式有誤"),
    (None, "H8-4. m_API 分解（J16 顯示用）：m_API＝折讓因子 × 隱含組合因子；折讓因子＝(1 − d) ÷ (1 − B4_Disc)（基準 d＝B4_Disc → 1.0；D 用 B4_Disc_Hi、E 用 B4_Disc_Lo）"),
    ("disc", "折讓因子＝(1 − 實際折讓 d) ÷ (1 − B4_Disc)", "x", "=(1-B4_Disc)/(1-B4_Disc)", "=(1-B4_Disc_Hi)/(1-B4_Disc)", "=(1-B4_Disc_Lo)/(1-B4_Disc)", "Derived（輸入 Assumed）",
     "基準 1.0；D 欄＝d 取高端 0.4（J20）→ 0.75；E 欄＝d 取低端 0.1 → 1.125。工作單寫 (1 − 0.2)，分母以 B4_Disc（基準 0.2）表示，不寫死常數"),
    ("mix", "隱含組合因子＝m_API ÷ 折讓因子　→ L1_MixFactorAPI", "x", "=C{m_api}/C{disc}", "=D{m_api}/D{disc}", "=E{m_api}/E{disc}", "Derived",
     "token 組合偏離參考請求（快取讀取、輸入占比）的效應；基準 0.56＝m_API（折讓因子 1）"),
    ("mix_agent", "對照：代理型極端組合因子（H6 第 {P_cc_ratio} 列；Requesty χ 0.919、輸入占 0.995）", "x", "=C{P_cc_ratio}", "=D{P_cc_ratio}", "=E{P_cc_ratio}", "Derived",
     "0.196；隱含組合因子 0.56 介於參考請求（1）與代理型極端（0.20）之間"),
    (None, "H8-5. 訂閱 m 下限（方案上限讀法；N06，Analogy／二手，只作上限用量；D／E 欄同值）：若所有訂閱者用滿額度，m＝月費 ÷ 方案上限 API 等值"),
    ("fee_plus", LAB["fee_plus"], "$／月", 20, "=C{fee_plus}", "=C{fee_plus}", "Assumed", "藍字（登錄 Gov_Map）：ChatGPT Plus $20／月（N06 對照用；未另登錄 SRC）"),
    ("cap_plus", LAB["cap_plus"], "$／月", 700, "=C{cap_plus}", "=C{cap_plus}", "Assumed", f"藍字（登錄 Gov_Map）：$20 方案約 $700／月 API 等值（N06，{EV['N06']}：SemiAnalysis 轉述，不可單獨引用；只作上限）"),
    ("fee_pro", LAB["fee_pro"], "$／月", 200, "=C{fee_pro}", "=C{fee_pro}", "Assumed", "藍字（登錄 Gov_Map）：ChatGPT Pro $200／月（N06 對照用）"),
    ("cap_pro", LAB["cap_pro"], "$／月", 14000, "=C{cap_pro}", "=C{cap_pro}", "Assumed", f"藍字（登錄 Gov_Map）：$200 方案週額度約 $2,600 → 約 $14,000／月 API 等值（N06，{EV['N06']}；只作上限）"),
    ("floor_plus", "訂閱 m 下限 — Plus＝月費 ÷ 方案上限（若所有訂閱者用滿額度）", "x", "=C{fee_plus}/C{cap_plus}", "=D{fee_plus}/D{cap_plus}", "=E{fee_plus}/E{cap_plus}", "Analogy", "0.03；方案上限由程式工作負載跑到週上限推得（N06）"),
    ("floor_pro", "訂閱 m 下限 — Pro＝月費 ÷ 方案上限（若所有訂閱者用滿額度）", "x", "=C{fee_pro}/C{cap_pro}", "=D{fee_pro}/D{cap_pro}", "=E{fee_pro}/E{cap_pro}", "Analogy", "0.014"),
    (None, "H8-6. 「必須為真」補列：m_消費訂閱＝1 所需的每訂閱者年 token＝訂閱 ARPU ÷ 單價；對照 N06 上限與 H2 現值（第 {P_tok_per_sub} 列）"),
    ("arpu", "消費訂閱 ARPU（$／人·年）＝消費訂閱營收 ÷ 2025 期間平均訂閱數（H2 第 {P_subs_avg} 列）", "$／人·年", "=C{rev_cons}*1000000000/(C{P_subs_avg}*1000000)", "=D{rev_cons}*1000000000/(D{P_subs_avg}*1000000)",
     "=E{rev_cons}*1000000000/(E{P_subs_avg}*1000000)", "Derived", "期間平均 32.75 M（J6 (a)）"),
    ("need_tok", "m_消費訂閱＝1 所需每訂閱者年 token＝ARPU ÷ 單價", "M tok/人·年", "=C{arpu}/C{P_price}", "=D{arpu}/D{P_price}", "=E{arpu}/E{P_price}", "Derived", "M tok／人·年"),
    ("cap_tok", "對照：Plus 方案上限換算年 token＝方案上限 × 12 ÷ 單價", "M tok/人·年", "=C{cap_plus}*12/C{P_price}", "=D{cap_plus}*12/D{P_price}", "=E{cap_plus}*12/E{P_price}", "Analogy", "N06 上限（Plus）"),
    ("cur_tok", "對照：H2 現值每付費訂閱者年 token（第 {P_tok_per_sub} 列；全部 ChatGPT 付費 token ÷ 訂閱數）", "M tok/人·年", "=C{P_tok_per_sub}", "=D{P_tok_per_sub}", "=E{P_tok_per_sub}", "Derived", "約 44"),
    ("need_judge", "判讀：所需 token 對現值的倍數；對 Plus 上限的比例", "x", '="所需＝現值 × "&TEXT(C{need_tok}/C{cur_tok},"0.00")&"；＝Plus 上限 × "&TEXT(C{need_tok}/C{cap_tok},"0.00")',
     '="所需＝現值 × "&TEXT(D{need_tok}/D{cur_tok},"0.00")&"；＝Plus 上限 × "&TEXT(D{need_tok}/D{cap_tok},"0.00")', '="所需＝現值 × "&TEXT(E{need_tok}/E{cur_tok},"0.00")&"；＝Plus 上限 × "&TEXT(E{need_tok}/E{cap_tok},"0.00")', "Derived", "文字"),
    (None, "H8-7. J21 Anthropic 第二方程式（對照列；不新增 Alloc_In 實驗室選項）：Anthropic token 分母未揭露，m_API（Anthropic）缺分母"),
    ("anth_share", f"Anthropic 2025 用量計費占營收＝{S(34)} ÷（{S(34)} ＋ {S(35)}）", "%", f"={S(34)}/{_ANTH_TOT}", f"={S(34)}/{_ANTH_TOT}", f"={S(34)}/{_ANTH_TOT}", "Derived（連結 SRC）",
     "0.83；SRC_DEM_036（經雲端市集）為用量計費的一部分（營收為總額），不另加"),
    ("anth_rs", f"Anthropic 雲端分潤比＝{S(37)} ÷ {S(36)}", "%", f"={S(37)}/{S(36)}", f"={S(37)}/{S(36)}", f"={S(37)}/{S(36)}", "Derived（連結 SRC）", "0.16；J16：分潤進 m（只改營收）"),
    ("anth_m", "m_API（Anthropic）　→ L1_MAPI_Anthropic", "x", '="缺分母（需 Anthropic 年 API token）"', '="缺分母（需 Anthropic 年 API token）"', '="缺分母（需 Anthropic 年 API token）"', "缺口",
     "所需輸入：Anthropic 年 API token（或每分鐘處理量時點值 × 全年平均比例）、Anthropic 有效單價（表列 ×（1 − 折扣））；有了分母即＝用量計費營收 × 1e9 ÷（token × 單價）"),
]
SPEC_H9 = [
    (None, f"H9. token 帳三路線（v5.34；{WO} B3）：需求路線（AL_DPaid）／支出路線（H7 第 {{Q_tok_fleet}} 列）／上限路線（L1_TokCeiling）並列、殘差、閉合解 τ*。欄位同 H7：C 基準、D m 低端、E m 高端"),
    ("t_dem", "付費 token — 需求路線＝AL_DPaid（H3 第 {P_tok_paid} 列）", "M tok/年", "=C{P_tok_paid}", "=D{P_tok_paid}", "=E{P_tok_paid}", "Derived（輸入 Assumed）", "3.83 × 10⁹"),
    ("t_fleet", "付費 token — 支出路線（機隊點估計；H7 第 {Q_tok_fleet} 列）", "M tok/年", "=C{Q_tok_fleet}", "=D{Q_tok_fleet}", "=E{Q_tok_fleet}", "Derived", "8.23 × 10⁹；SLO 不可達時為文字"),
    ("t_ceil", "付費 token — 上限路線（H7 第 {Q_tok_ceil} 列；L1_TokCeiling）", "M tok/年", "=C{Q_tok_ceil}", "=D{Q_tok_ceil}", "=E{Q_tok_ceil}", "Derived", "1.20 × 10¹⁰"),
    ("res_fleet", "殘差：需求 ÷ 機隊（點估計）　→ Checks M4（< 0.5 或 > 2 為 WARN）", "x", '=IF(ISNUMBER(C{t_fleet}),C{t_dem}/C{t_fleet},"SLO 不可達")', '=IF(ISNUMBER(D{t_fleet}),D{t_dem}/D{t_fleet},"SLO 不可達")',
     '=IF(ISNUMBER(E{t_fleet}),E{t_dem}/E{t_fleet},"SLO 不可達")', "Derived", "現值 0.465 → M4 觸發（預期）：需求路線只數到機隊產出的一半"),
    ("res_ceil", "殘差：需求 ÷ 上限", "x", '=IF(ISNUMBER(C{t_ceil}),C{t_dem}/C{t_ceil},"SLO 不可達")', '=IF(ISNUMBER(D{t_ceil}),D{t_dem}/D{t_ceil},"SLO 不可達")', '=IF(ISNUMBER(E{t_ceil}),E{t_dem}/E{t_ceil},"SLO 不可達")',
     "Derived", "現值 0.319（＝L1_TokCeiling 判讀）"),
    (None, "閉合解：令需求 token（付費＋免費）佔滿機隊有效產能所需的每則 token 數 τ*（三步）；錨點 τ* ≈ 13,950"),
    ("eff_gw", "(i) 有效服務 GW＝支出路線服務 GW（H7 第 {Q_gw_az} 列）× 利用率修正（第 {Q_corr_pt} 列）", "GW", "=C{Q_gw_az}*C{Q_corr_pt}", "=D{Q_gw_az}*D{Q_corr_pt}", "=E{Q_gw_az}*E{Q_corr_pt}", "Derived", "0.6736 × 0.5833＝0.3929"),
    ("tchat", "(ii) ChatGPT 年 token 閉合值 T_chat*＝[(i) − API token ÷ 付費產能] ÷ [(1 − 免費占比) ÷ 付費產能 ＋ 免費占比 ÷ 免費產能]", "M tok/年",
     '=IF(AND(ISNUMBER(C{Q_cap_paid}),ISNUMBER(C{Q_cap_free})),(C{eff_gw}-C{tok_api}/C{Q_cap_paid})/((1-AL_FreeShare)/C{Q_cap_paid}+AL_FreeShare/C{Q_cap_free}),"SLO 不可達")',
     '=IF(AND(ISNUMBER(D{Q_cap_paid}),ISNUMBER(D{Q_cap_free})),(D{eff_gw}-D{tok_api}/D{Q_cap_paid})/((1-AL_FreeShare)/D{Q_cap_paid}+AL_FreeShare/D{Q_cap_free}),"SLO 不可達")',
     '=IF(AND(ISNUMBER(E{Q_cap_paid}),ISNUMBER(E{Q_cap_free})),(E{eff_gw}-E{tok_api}/E{Q_cap_paid})/((1-AL_FreeShare)/E{Q_cap_paid}+AL_FreeShare/E{Q_cap_free}),"SLO 不可達")', "Derived",
     "錨點 1.273 × 10¹⁰；API token 取 H8-2 各欄；免費占比 AL_FreeShare（0.6，單值）"),
    ("tau", "(iii) τ*＝T_chat* × 1e6 ÷（SRC_DEM_012 × 1e9 × 365）　→ L1_TokPerPromptClose", "tok", '=IF(ISNUMBER(C{tchat}),C{tchat}*1000000/(SRC_DEM_012*1000000000*365),"SLO 不可達")',
     '=IF(ISNUMBER(D{tchat}),D{tchat}*1000000/(SRC_DEM_012*1000000000*365),"SLO 不可達")', '=IF(ISNUMBER(E{tchat}),E{tchat}*1000000/(SRC_DEM_012*1000000000*365),"SLO 不可達")', "Derived",
     "每則提示 token 數（含回覆）；對照 Alloc_In C15 基準 4,000、區間 2,000–11,000"),
    ("tau_judge", "τ* 對 Alloc_In C15 區間（AL_TokPerPrompt_Lo–_Hi）的判讀", "x",
     '=IF(ISNUMBER(C{tau}),IF(C{tau}>AL_TokPerPrompt_Hi,"高於區間（"&TEXT(AL_TokPerPrompt_Lo,"#,##0")&"–"&TEXT(AL_TokPerPrompt_Hi,"#,##0")&"）",IF(C{tau}<AL_TokPerPrompt_Lo,"低於區間","區間內")),"SLO 不可達")',
     '=IF(ISNUMBER(D{tau}),IF(D{tau}>AL_TokPerPrompt_Hi,"高於區間（"&TEXT(AL_TokPerPrompt_Lo,"#,##0")&"–"&TEXT(AL_TokPerPrompt_Hi,"#,##0")&"）",IF(D{tau}<AL_TokPerPrompt_Lo,"低於區間","區間內")),"SLO 不可達")',
     '=IF(ISNUMBER(E{tau}),IF(E{tau}>AL_TokPerPrompt_Hi,"高於區間（"&TEXT(AL_TokPerPrompt_Lo,"#,##0")&"–"&TEXT(AL_TokPerPrompt_Hi,"#,##0")&"）",IF(E{tau}<AL_TokPerPrompt_Lo,"低於區間","區間內")),"SLO 不可達")', "Derived", "文字"),
    ("free_close", "閉合下免費算力占比＝免費 GW ÷ 有效服務 GW（以 T_chat* 重算；對照 IF_FreeShare 0.46）", "%",
     '=IF(ISNUMBER(C{tchat}),(C{tchat}*AL_FreeShare/C{Q_cap_free})/C{eff_gw},"SLO 不可達")', '=IF(ISNUMBER(D{tchat}),(D{tchat}*AL_FreeShare/D{Q_cap_free})/D{eff_gw},"SLO 不可達")',
     '=IF(ISNUMBER(E{tchat}),(E{tchat}*AL_FreeShare/E{Q_cap_free})/E{eff_gw},"SLO 不可達")', "Derived", "錨點 ≈ 0.21；低於支出口徑 IF_FreeShare（0.46）：免費 token 每 GW 產能高（Luna 為主）"),
]
# H10 rows: (key, label, unit, C, D, E, F, tag, note); columns C＝2025 年度、D＝2026 Q1 年化、E＝2026 Q2 年化、F＝FY2026 預測。
def _CAP(col, kind, m):
    """Generation blend of the per-generation capacity (AL_CapPaid／AL_CapFree) at this column's mix. v6.2 2-1-c: a generation whose capacity is text
    (no reachable tier) drops out and the mix is renormalised over the remaining generations (same rule as Alloc section B); all text -> "SLO 不可達"."""
    sh = [f"{col}{{{k}}}" for k in m]
    cp = [f"INDEX(AL_Cap{kind},1,{i + 1})" for i in range(4)]
    den = "(" + "+".join(f"IF(AND({s}>0,ISNUMBER({c})),{s},0)" for s, c in zip(sh, cp)) + ")"
    num = "+".join(f"IF(AND({s}>0,ISNUMBER({c})),{s}*{c},0)" for s, c in zip(sh, cp))
    return f'=IF({den}>0,({num})/{den},"SLO 不可達")'
_MIX = ("q_mix_h", "q_mix_gb200", "q_mix_gb300", "q_mix_vr")
_HOLD = lambda col: "=" + "+".join(f"{col}{{{k}}}*INDEX(AL_HoldGen,1,{i + 1})" for i, k in enumerate(_MIX))


def _h10_cols(f_c, f_d=None, f_e=None, f_f=None):
    """Expand a per-column formula template: {c} = own column letter; same template for D／E／F unless given."""
    return (f_c.replace("{c}", "C"), (f_d if f_d is not None else f_c).replace("{c}", "D"),
            (f_e if f_e is not None else (f_d if f_d is not None else f_c)).replace("{c}", "E"),
            (f_f if f_f is not None else (f_e if f_e is not None else (f_d if f_d is not None else f_c))).replace("{c}", "F"))


SPEC_H10 = [
    (None, f"H10. m 季度序列（v5.34；{WO} B5，r0.1：營收三分份額每欄各自輸入）：顯示用，不進 L1、不進任何 IF_。欄位：C＝2025 年度、D＝2026 Q1 年化、E＝2026 Q2 年化、F＝FY2026 預測。"
           "其餘輸入（每則提示 token 數、免費占比、單價、Azure 倍數、利用率修正）沿用 2025 列"),
    ("q_hdr", "項目", "單位", "2025 年度", "2026 Q1 年化", "2026 Q2 年化", "FY2026 預測", "", ""),
    (None, "H10-1. 營收與份額"),
    ("q_rev", LAB["q_rev"], "$B", "=SRC_DEM_007", f"={S(69)}*4", "=SRC_DEM_042*4", 36, "Interested-party（連結 SRC）／Assumed（F）", "C＝SRC_DEM_007 13.07；D＝SRC_DEM_069 5.7 × 4；E＝SRC_DEM_042 6.7 × 4；F＝36（藍字，內部預測，登錄 Gov_Map，不登 SRC）"),
    ("q_ads", "廣告營收（2026 起；H8 第 {ads} 列；不進任何 m 的分子）", "$B", 0, "=C{ads}", "=C{ads}", "=C{ads}", "Assumed（連結 H8）", "2025 為 0（常數，非輸入）；2026 三欄連結 H8 基準 0.5"),
    ("q_rev_m", "m 分子營收＝營收 − 廣告", "$B", *_h10_cols("={c}{q_rev}-{c}{q_ads}"), "Derived", "m_整體與 m_fleet 的分子；三分份額仍以營收（含廣告）為基底（依工作單錨點；見報告「待 Project 判斷」）"),
    ("q_sh_cons", LAB["q_sh_cons"], "%", "=C{P_share}", 0.60, 0.55, 0.45, "Interested-party（C 連結 SRC）／Assumed（D–F）", "C＝SRC_DEM_039 0.70；D 0.60（消費約 60%、企業 >40%：SRC_DEM_023 2026-03）；E 0.55；F 0.45（企業 2026-07 超過消費、7–9 月翻倍：N05）；藍字三格登錄 Gov_Map"),
    ("q_sh_seat", LAB["q_sh_seat"], "%", "=C{seat}", 0.20, 0.25, 0.35, "Assumed", "C＝H8 0.10；D 0.20、E 0.25、F 0.35（企業增量歸席次；API 份額依 N04 維持 0.15–0.20）；藍字三格登錄 Gov_Map。「企業」口徑 OpenAI 未定義（SRC_DEM_023 備註），本表視為席次＋API"),
    ("q_sh_api", "營收份額：API（＝1 − 消費訂閱 − 商用席次）", "%", *_h10_cols("=1-{c}{q_sh_cons}-{c}{q_sh_seat}"), "Derived", "各欄 0.20"),
    ("q_rev_cons", "消費訂閱營收", "$B", *_h10_cols("={c}{q_rev}*{c}{q_sh_cons}"), "Derived", "份額 × 營收（含廣告）"),
    ("q_rev_seat", "商用席次營收", "$B", *_h10_cols("={c}{q_rev}*{c}{q_sh_seat}"), "Derived", ""),
    ("q_rev_api", "API 營收", "$B", *_h10_cols("={c}{q_rev}*{c}{q_sh_api}"), "Derived", "2026 Q2：5.36；API 實收單價＝÷ API token（0.68 $/M）"),
    (None, "H10-2. token"),
    ("q_mult", LAB["q_mult"], "x", DASH, DASH, DASH, 1.3, "Assumed", "藍字（登錄 Gov_Map）：FY2026 API token＝2026 Q2 時點值年化 × 1.3"),
    ("q_tok_api", "API token（M tok/年）：2025＝AL_DAPI；2026 Q1／Q2＝SRC_DEM_011 時點值年化；FY2026＝× 年均倍數", "M tok/年", "=AL_DAPI", "=SRC_DEM_011*1000000000*525600/1000000",
     "=SRC_DEM_011*1000000000*525600/1000000", "=E{q_tok_api}*F{q_mult}", "Derived（連結 SRC）", "SRC_DEM_011 15 B tok/min（2026-03）；2026 Q1／Q2 同值"),
    ("q_msgs", LAB["q_msgs"], "B 則/日", "=SRC_DEM_012", 3.2, 3.6, 3.8, "Interested-party（C 連結 SRC）／Assumed（D–F，Derived 自週活比例）", "C＝SRC_DEM_012 2.5；D 3.2、E 3.6（2.5 × 1.0 B ÷ 0.7 B 週活）、F 3.8；藍字三格登錄 Gov_Map"),
    ("q_tok_chat", "ChatGPT 付費 token＝則數 × 1e9 × AL_TokPerPrompt × 365 ÷ 1e6 ×（1 − AL_FreeShare）", "M tok/年", *_h10_cols("={c}{q_msgs}*1000000000*AL_TokPerPrompt*365/1000000*(1-AL_FreeShare)"), "Derived（輸入 Assumed）",
     "2025 欄＝AL_DChatPaid（Alloc 第 8 列同式）；每則 4,000、免費占比 0.6 沿用"),
    ("q_tok_free", "ChatGPT 免費 token＝則數 × 1e9 × AL_TokPerPrompt × 365 ÷ 1e6 × AL_FreeShare", "M tok/年", *_h10_cols("={c}{q_msgs}*1000000000*AL_TokPerPrompt*365/1000000*AL_FreeShare"), "Derived（輸入 Assumed）", "m_fleet 的 r 用"),
    ("q_tok_cons", "消費訂閱 token＝ChatGPT 付費 token × 消費份額（H8 第 {cts} 列，沿用 0.75）", "M tok/年", *_h10_cols("={c}{q_tok_chat}*$C${cts}"), "Derived（輸入 Assumed）", "2026 席次用量占比缺證據（待 Project 判斷）"),
    ("q_tok_seat", "商用席次 token＝ChatGPT 付費 token ×（1 − 消費份額）", "M tok/年", *_h10_cols("={c}{q_tok_chat}*(1-$C${cts})"), "Derived（輸入 Assumed）", ""),
    (None, "H10-3. 單價與 m"),
    ("q_idx", LAB["q_idx"], "x", 1, 1, 1, 1, "Assumed（預留）", "藍字四格（登錄 Gov_Map）：L 的牌價序列另案（v5.35 候選）；本版不乘入單價"),
    ("q_price", "付費 token 混合有效單價（H4 第 {P_price} 列；四欄同值，2026 快照）", "$/M", *_h10_cols("=$C${P_price}"), "Derived", "牌價指數列尚未乘入（待 v5.35）"),
    ("q_m_api", "m_API", "x", *_h10_cols("={c}{q_rev_api}*1000000000/({c}{q_tok_api}*{c}{q_price})"), "Derived", "錨點：2025 0.56、2026 Q2 0.35"),
    ("q_m_cons", "m_消費訂閱", "x", *_h10_cols("={c}{q_rev_cons}*1000000000/({c}{q_tok_cons}*{c}{q_price})"), "Derived", "錨點：2025 4.26、2026 Q2 ≈ 4.77"),
    ("q_m_seat", "m_商用席次", "x", *_h10_cols("={c}{q_rev_seat}*1000000000/({c}{q_tok_seat}*{c}{q_price})"), "Derived", "錨點：2025 1.83、2026 Q2 ≈ 6.50"),
    ("q_m_all", "m_整體＝m 分子營收 ÷（(API token ＋ ChatGPT 付費 token) × 單價）", "x", *_h10_cols("={c}{q_rev_m}*1000000000/(({c}{q_tok_api}+{c}{q_tok_chat})*{c}{q_price})"), "Derived",
     "錨點：2025 1.743（＝L1_MImplied）、2026 Q2 1.34（分子扣廣告 0.5）"),
    (None, "H10-4. m_fleet（機隊點估計；2025 用 Alloc_In 組合，2026 用下列四格 Assumed 組合；推論支出 2025＝SRC_DEM_018、2026＝SRC_DEM_070）"),
    ("q_mix_h", LAB["q_mix_h"], "%", "=AL_MixHopper", 0.25, "=D{q_mix_h}", "=D{q_mix_h}", "Assumed", "藍字（D；登錄 Gov_Map）：2026 Hopper 0.25；E／F 連結 D"),
    ("q_mix_gb200", LAB["q_mix_gb200"], "%", "=AL_MixGB200", 0.45, "=D{q_mix_gb200}", "=D{q_mix_gb200}", "Assumed", "藍字（D；登錄 Gov_Map）：2026 GB200 0.45"),
    ("q_mix_gb300", LAB["q_mix_gb300"], "%", "=AL_MixGB300", 0.25, "=D{q_mix_gb300}", "=D{q_mix_gb300}", "Assumed", "藍字（D；登錄 Gov_Map）：2026 GB300 0.25"),
    ("q_mix_vr", LAB["q_mix_vr"], "%", "=AL_MixVR200", 0.05, "=D{q_mix_vr}", "=D{q_mix_vr}", "Assumed", "藍字（D；登錄 Gov_Map）：2026 VR200 0.05；四格合計須為 1（第 {q_mix_sum} 列）"),
    ("q_mix_sum", "世代組合合計（應為 100%）", "%", *_h10_cols("={c}{q_mix_h}+{c}{q_mix_gb200}+{c}{q_mix_gb300}+{c}{q_mix_vr}"), "Derived", ""),
    ("q_spend", "推論支出（$B；Azure 計價）", "$B", "=SRC_DEM_018", f"={S(70)}", f"={S(70)}", f"={S(70)}", "Interested-party（連結 SRC）", "2025＝SRC_DEM_018 12.6；2026＝SRC_DEM_070 14.1（Alt，預測值）"),
    ("q_hold", "世代組合持有成本＝Σ 組合 × IF_HoldEcon（AL_HoldGen）", "$B/GW/年", "=SUMPRODUCT(AL_ShareGen,AL_HoldGen)", _HOLD("D"), _HOLD("E"), _HOLD("F"), "Derived", "2025 欄＝Alloc 第 61 列分母"),
    ("q_gw", "支出路線服務 GW ÷ Azure 倍數 × 利用率修正＝推論支出 ÷ 持有成本 ÷ AL_SpendBasis × AL_UtilActual ÷ IF_Util", "GW", *_h10_cols("={c}{q_spend}/{c}{q_hold}/AL_SpendBasis*AL_UtilActual/IF_Util"), "Derived（輸入 Assumed）",
     "2025 欄＝H9 (i) 有效服務 GW 0.3929"),
    ("q_bp", "世代組合後每 GW 年產能（付費；AL_CapPaid 加權）", "M tok/GW/年", "=AL_BlendPaid", _CAP("D", "Paid", _MIX), _CAP("E", "Paid", _MIX), _CAP("F", "Paid", _MIX), "Derived", "Alloc 第 24 列同式；2026 欄以 2026 組合加權"),
    ("q_bf", "世代組合後每 GW 年產能（免費；AL_CapFree 加權）", "M tok/GW/年", "=AL_BlendFree", _CAP("D", "Free", _MIX), _CAP("E", "Free", _MIX), _CAP("F", "Free", _MIX), "Derived", "Alloc 第 25 列同式"),
    ("q_r", "免費 ÷ 付費 token 比 r＝ChatGPT 免費 token ÷（API token ＋ ChatGPT 付費 token）", "x", *_h10_cols("={c}{q_tok_free}/({c}{q_tok_api}+{c}{q_tok_chat})"), "Derived", "2025 欄＝H7 第 {Q_r_model} 列 0.573"),
    ("q_tok_fleet", "機隊付費 token（點估計）＝服務 GW × 修正 ÷（1 ÷ 付費產能 ＋ r ÷ 免費產能）", "M tok/年",
     *_h10_cols('=IF(AND(ISNUMBER({c}{q_bp}),ISNUMBER({c}{q_bf})),{c}{q_gw}/(1/{c}{q_bp}+{c}{q_r}/{c}{q_bf}),"SLO 不可達")'), "Derived", "2025 欄＝H7 第 {Q_tok_fleet} 列"),
    ("q_m_fleet", "m_fleet＝m 分子營收 ÷（機隊付費 token × 單價）", "x", *_h10_cols('=IF(ISNUMBER({c}{q_tok_fleet}),{c}{q_rev_m}*1000000000/({c}{q_tok_fleet}*{c}{q_price}),"SLO 不可達")'), "Derived",
     "錨點：2025 0.81（＝L1_MFleet）、2026 Q2 0.78"),
    ("q_chk", "自我檢查：2025 欄 m_整體 對 H5 第 {P_m_all} 列、m_fleet 對 H7 第 {Q_m_fleet} 列（相對差 ≤ 1e-9 為「一致」）", "x",
     '=IF(AND(ISNUMBER(C{q_m_fleet}),ISNUMBER(C{Q_m_fleet})),IF(AND(ABS(C{q_m_all}/C{P_m_all}-1)<=0.000000001,ABS(C{q_m_fleet}/C{Q_m_fleet}-1)<=0.000000001),"一致","不一致"),IF(ABS(C{q_m_all}/C{P_m_all}-1)<=0.000000001,"一致（m_fleet 為文字）","不一致"))',
     DASH, DASH, DASH, "Derived", "2025 欄只是 H5／H7 的重排"),
]
NOTE_V534 = (" ｜v5.34 補充：(4) m 按收費模式拆開後（H8），API 路線 m_API 0.56 大部分來自 token 組合偏離參考請求（隱含組合因子 0.56，折讓因子 1），不是折讓；消費訂閱 m 4.3 與商用席次 m 1.8 都 > 1，"
             "需求路線的 m > 1 主要落在訂閱分子。(5) token 帳三路線（H9）：需求 ÷ 機隊 0.465（Checks M4 WARN，預期）、需求 ÷ 上限 0.319；閉合解 τ* ≈ 13,950 每則 token，高於 Alloc_In C15 區間 2,000–11,000，"
             "代表需求路線要與機隊產出閉合，每則 token 數要到 1.4 萬，或機隊產出假設偏高。(6) 季度序列（H10）：2026 Q2 年化 m_API 0.35、m_整體 1.34、m_fleet 0.78；只作追蹤，CTL_Monetize 不改（J15）。"
             "J16 分工規則：同時改變成本的因子（快取命中率 χ、層級組合、ISL/OSL）進 Q 側，只改變營收的因子（折讓、訂閱用量落差、雲端分潤）進 m。J17：m 為實驗室視角，交付物是區間與「必須為真」。")
BLUE_H8 = {("seat", "C"), ("seat", "D"), ("seat", "E"), ("cts", "C"), ("cts", "D"), ("cts", "E"), ("ads", "C"), ("ads", "D"), ("ads", "E"),
           ("fee_plus", "C"), ("cap_plus", "C"), ("fee_pro", "C"), ("cap_pro", "C")}
BLUE_H10 = {("q_rev", "F"), ("q_sh_cons", "D"), ("q_sh_cons", "E"), ("q_sh_cons", "F"), ("q_sh_seat", "D"), ("q_sh_seat", "E"), ("q_sh_seat", "F"), ("q_mult", "F"),
            ("q_msgs", "D"), ("q_msgs", "E"), ("q_msgs", "F"), ("q_idx", "C"), ("q_idx", "D"), ("q_idx", "E"), ("q_idx", "F"),
            ("q_mix_h", "D"), ("q_mix_gb200", "D"), ("q_mix_gb300", "D"), ("q_mix_vr", "D")}
KEY_FILL = {"m_api", "m_cons", "m_seat", "m_all", "mix", "tau", "q_m_api", "q_m_all", "q_m_fleet"}
ROWS = {}


def _write(ws, r, key, lab, unit, vals, tag, note, ctx, blue):
    put(ws, f"A{r}", lab.format(**ctx), wrap=True); put(ws, f"B{r}", unit)
    fmt = FMT.get(unit)
    for col, v in vals:
        if isinstance(v, str) and v.startswith("="):
            v = v.format(**ctx)
            font = F_LINK if (v.startswith("=SRC_") or v.startswith("=AL_")) and "*" not in v and "/" not in v and "+" not in v and "-" not in v else F_CALC
            put(ws, f"{col}{r}", v, font, fmt=fmt, fill=FILL_KEY if key in KEY_FILL and col == "C" else None)
        elif isinstance(v, (int, float)) and type(v) is not bool:
            if (key, col) in blue: put(ws, f"{col}{r}", v, F_IN, fmt=fmt)
            else: put(ws, f"{col}{r}", v, F_CALC, fmt=fmt)        # builder-owned constant (e.g. 2025 ads = 0), not an input
        else:
            put(ws, f"{col}{r}", v, F_CALC)
    put(ws, f"F{r}" if len(vals) == 3 else f"G{r}", tag, F_NOTE)
    put(ws, f"G{r}" if len(vals) == 3 else f"H{r}", note.format(**ctx), F_NOTE, wrap=True)


def cap_in_h8_h10(wb, h32, h33):
    """Rows start where v5.33 wrote its reading row (h33['end']); that row is cleared and rewritten after H10 (no defined name there)."""
    ws = wb["Cap_In"]
    r0 = h33["end"]
    assert str(ws[f"A{r0}"].value).startswith("讀法") and ws.max_row == r0, (r0, ws.max_row)
    ws[f"A{r0}"].value = None
    ctx = {f"P_{k}": v for k, v in h32["rows"].items()}
    ctx.update({f"Q_{k}": v for k, v in h33["rows"].items()})
    r = r0
    for spec in (SPEC_H8, SPEC_H9, SPEC_H10):
        for item in spec:
            if item[0] is not None: ROWS[item[0]] = r
            r += 1
    ctx.update(ROWS)
    r = r0
    for item in SPEC_H8 + SPEC_H9:
        if item[0] is None:
            put(ws, f"A{r}", item[1].format(**ctx), F_BOLD); r += 1; continue
        key, lab, unit, c, d, e, tag, note = item
        _write(ws, r, key, lab, unit, [("C", c), ("D", d), ("E", e)], tag, note, ctx, BLUE_H8)
        r += 1
    for item in SPEC_H10:
        if item[0] is None:
            put(ws, f"A{r}", item[1].format(**ctx), F_BOLD); r += 1; continue
        key, lab, unit, c, d, e, f, tag, note = item
        if key == "q_hdr":
            for col, h in zip("ABCDEFGH", [lab, unit, c, d, e, f, "標記", "說明"]): put(ws, f"{col}{r}", h, F_BOLD)
            r += 1; continue
        _write(ws, r, key, lab, unit, [("C", c), ("D", d), ("E", e), ("F", f)], tag, note, ctx, BLUE_H10)
        r += 1
    put(ws, f"A{r}", v533.NOTE_END + NOTE_V534, F_NOTE)
    for n, ref in (("B4_Disc_Lo", "Cap_In!$D$12"), ("B4_Disc_Hi", "Cap_In!$E$12")):      # v5.34: range endpoints of B4_Disc (display-only names, H8-4)
        if n not in wb.defined_names: wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return dict(start=r0, rows=dict(ROWS), end=r)


# ================================================================== B6: Gov_Map rows for the new blue cells (gov.gm_append_c; appended when absent)
def gov_map_rows(wb):
    if not ROWS: return []
    ws = wb["Cap_In"]; sc = "切片三（v5.34 m 分拆）"; out = []
    def chk(key):
        r = ROWS[key]; lab = ws[f"A{r}"].value
        assert lab == LAB[key], (key, lab)
        return r, lab
    def row(key, cell, role, src, rel, dec, lo, hi, rtext, reason, cls="Assumed"):
        r, lab = chk(key)
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': cell.format(r=r), 'label': lab, 'check': lab, 'cls': cls, 'role': role, 'src': src,
                    'rel': rel, 'dec': dec, 'lo': (lo.format(r=r) if isinstance(lo, str) else lo), 'hi': (hi.format(r=r) if isinstance(hi, str) else hi),
                    'rtext': rtext.format(r=r), 'reason': reason, 'retag': '', 'seg': '無'})
    # H8 three inputs with ranges (C = base, D:E = endpoints)
    rs = f"v5.34 J18：2025 營收三分，商用席次份額 Assumed 0.10（0.05–0.15），API＝餘額 0.20（{S(71)} Sacra 15–20%）；只進 Cap_In H8／H10 與 L1_MAPI／MSub／MSeat，不進任何 IF_"
    row("seat", "C{r}", "基準", S(71), f"對照：API 餘額 0.20 落在 Sacra 15–20%（{EV['N04']}）", "X38", "=Cap_In!D{r}", "=Cap_In!E{r}", "0.05–0.15（D 欄＝席次營收取低 0.05、E 欄 0.15）", rs)
    row("seat", "D{r}:E{r}", "低／高", "", "", "X38", None, None, "C{r} 的低（0.05）、高（0.15）端點", rs)
    rc = "v5.34 J19：消費訂閱占 ChatGPT 付費 token 份額 Assumed 0.75（0.60–0.90）；席次用量占比缺證據（SRC_DEM_045 只有 p95／中位數＝6）；只進 Cap_In H8／H10 與 L1_MSub／MSeat"
    row("cts", "C{r}", "基準", "", "", "X39", "=Cap_In!E{r}", "=Cap_In!D{r}", "0.60–0.90（D 欄＝消費 token 取高 0.90、E 欄 0.60）", rc)
    row("cts", "D{r}:E{r}", "低／高", "", "", "X39", None, None, "C{r} 的 m 低端（0.90）、m 高端（0.60）端點", rc)
    ra = "v5.34 J18：2026 廣告營收年化 Assumed 0.5 $B（0–1.0）；廣告不進任何 m 的分子，只在 H10 2026 欄自 m_整體／m_fleet 分子扣除；顯示用"
    row("ads", "C{r}", "基準", "", "", "X38", "=Cap_In!D{r}", "=Cap_In!E{r}", "0–1.0（D 欄 0、E 欄 1.0）", ra)
    row("ads", "D{r}:E{r}", "低／高", "", "", "X38", None, None, "C{r} 的低（0）、高（1.0）端點", ra)
    rf = f"v5.34 B2 第 6 項（J17）：方案上限讀法只作訂閱 m 的下限（若所有訂閱者用滿額度）；N06（{EV['N06']}）為 SemiAnalysis 轉述、不可單獨引用，不登 SRC；對照用，不進任何 IF_／L1_ 數值"
    for key, rtext in (("fee_plus", "單值（ChatGPT Plus 月費 $20）"), ("cap_plus", "單值（$20 方案約 $700／月 API 等值）"), ("fee_pro", "單值（ChatGPT Pro 月費 $200）"), ("cap_pro", "單值（$200 方案約 $14,000／月 API 等值）")):
        row(key, "C{r}", "單值", "", "", "X37", None, None, rtext, rf)
    # H10 inputs
    row("q_rev", "F{r}", "單值", "SRC_DEM_042", f"對照：2026 Q2 年化 26.8（{S(42)} × 4）與 Q1 年化 22.8（{S(69)} × 4）", "X38", None, None, "單值 36（FY2026 內部預測；不登 SRC）",
        "v5.34 B5：FY2026 營收預測 36 $B（Assumed：內部預測，SRC 不登）；只進 H10 FY2026 欄")
    row("q_sh_cons", "D{r}:F{r}", "單值", "SRC_DEM_023", f"對照：2026-03 企業 >40%（{S(23)}）、2024-10 消費 75%（{S(38)}）、2025 70%（{S(39)}）", "X38", None, None,
        "三個單值：2026 Q1 0.60、Q2 0.55、FY2026 0.45（r0.1：每欄各自輸入）",
        f"v5.34 r0.1（Andy 15:49 提醒 2026 企業營收已超過消費）：消費份額序列 0.70 → 0.60 → 0.55 → 0.45；依據 {S(23)}（2026-03 企業 >40%）與 N05（2026-07 企業超過消費，{EV['N05']}、{EV['N13']}）；「企業」口徑未定義")
    row("q_sh_seat", "D{r}:F{r}", "單值", S(71), f"對照：API 份額依 Sacra 15–20% 維持 0.20（{S(71)}），企業增量歸席次", "X38", None, None,
        "三個單值：2026 Q1 0.20、Q2 0.25、FY2026 0.35（r0.1）", "v5.34 r0.1：席次份額 0.10 → 0.20 → 0.25 → 0.35，API＝餘額各欄 0.20；企業（席次＋API）增量全歸席次")
    row("q_mult", "F{r}", "單值", "SRC_DEM_011", f"對照：{S(11)} 2026-03 時點值 15 B tok/min", "X38", None, None, "單值 1.3", "v5.34 B5：FY2026 API token＝2026 Q2 時點值年化 × 1.3（Assumed：API 全年再成長）")
    row("q_msgs", "D{r}:F{r}", "單值", "SRC_DEM_012", f"Derived：{S(12)} 2.5 B／日 × 週活比例（1.0 B ÷ 0.7 B）", "X38", None, None, "三個單值：2026 Q1 3.2、Q2 3.6、FY2026 3.8 B 則／日",
        f"v5.34 B5：ChatGPT 每日則數 2026 三點為 Derived（週活比例放大；{S(12)} 2.5 × 1.0 ÷ 0.7 ≈ 3.6）；每則 token 數與免費占比沿用 Alloc_In")
    row("q_idx", "C{r}:F{r}", "單值", "", "", "X38", None, None, "四個單值皆為 1（預留列；v5.35 候選 L_price）", "v5.34 B5：中階牌價指數預留列，先填 1；本版不乘入任何計算（L 的牌價序列另案 v5.35）")
    rm = "v5.34 B5：2026 服務世代組合 Hopper 0.25／GB200 0.45／GB300 0.25／VR200 0.05（Assumed；只進 H10 2026 欄的 m_fleet；Alloc_In 2025 組合不改）"
    for key, v in (("q_mix_h", 0.25), ("q_mix_gb200", 0.45), ("q_mix_gb300", 0.25), ("q_mix_vr", 0.05)):
        row(key, "D{r}", "單值", "", "", "X38", None, None, f"單值 {v}（四格合計 1）", rm)
    return out


# ================================================================== B6: Gov_Map GM441／GM442 (B4_Disc) range text 0.1–0.4 (J20; guarded)
GM441_TAIL = (" ｜v5.34 J20：高端 0.3 → 0.4（Cap_In E12）；依據：企業議價折扣顧問自述中位數 27%、20–35%（對開價，未驗證）與公開牌價特性（Batch 五折、Flex、快取 90% 折）；"
              f"Batch／Flex 占 token 比例與企業平均折扣未找到（{EV['N09']}、{EV['N10']}）；基準 0.2、低端 0.1 不改，IF_Price* 不變")
GM441_RANGE = ("0.1–0.4（v5.34 J20：高端 0.3 → 0.4；基準 0.2 不改）")


def _gm_row(ws, sheet, cell):
    rows = [r for r in range(5, ws.max_row + 1) if (ws[f"C{r}"].value, ws[f"D{r}"].value) == (sheet, cell)]
    assert len(rows) == 1, (sheet, cell, rows)
    return rows[0]


def gov_update(ws, append_text):
    n = 0
    r = _gm_row(ws, "Cap_In", "C12"); assert ws[f"A{r}"].value == "GM441", ws[f"A{r}"].value
    n += append_text(ws[f"N{r}"], GM441_TAIL)
    if ws[f"M{r}"].value in (DASH, None, ""): ws[f"M{r}"].value = GM441_RANGE; n += 1
    r = _gm_row(ws, "Cap_In", "D12:E12"); assert ws[f"A{r}"].value == "GM442", ws[f"A{r}"].value
    n += append_text(ws[f"N{r}"], GM441_TAIL)
    return n


# ================================================================== B4: L1 rows (appended after every existing L1 row; no L1 name moves)
READ_M = ("m 按收費模式拆開（J19）：分母 token 為模型自身需求（Assumed），三者分子之和＝SRC_DEM_007、分母之和＝AL_DPaid，所以 token 加權平均＝L1_MImplied（1.74）。"
          "m 是實驗室視角的「付費 token 平均實收單價 ÷ OpenAI 有效單價」（J17），用途是回本條件 L·m ≥ 門檻，不乘進每 GW 營收；交付物是區間與「必須為真」，不是點估計。")
READ_MIX = ("m_API＝折讓因子 × 隱含組合因子（J16 顯示用）：折讓因子＝(1 − d) ÷ (1 − B4_Disc)，基準 d＝B4_Disc → 1；隱含組合因子＝token 組合偏離參考請求（快取讀取、輸入占比）的效應。"
            "基準 0.56 大部分是組合、少部分是折讓（d＝0.4 時組合因子 0.47、0.5 時 0.56）。J16：會同時改變成本的因子（χ、層級組合、ISL/OSL）進 Q 側，本單不改 Q 側輸入。")
READ_TAU = ("閉合解：令需求 token（付費＋免費）佔滿支出路線的機隊有效產能（服務 GW ÷ Azure 倍數 × AL_UtilActual ÷ IF_Util）所需的每則 token 數。高於 Alloc_In C15 區間（2,000–11,000）代表"
            "需求路線（每則 4,000）與機隊產出不閉合：每則 token 要到約 1.4 萬，或機隊產出假設（Azure 倍數、實際利用率、世代組合）偏高。Checks M4 以需求 ÷ 機隊 < 0.5 或 > 2 提示。")
READ_ANTH = ("J21：本版只建對照列。Anthropic 2025 用量計費占營收（SRC_DEM_034 ÷（034 ＋ 035））約 0.83、雲端分潤比（SRC_DEM_037 ÷ 036）約 0.16（外部欄 M／N）；"
             "m_API（Anthropic）需要 Anthropic 年 API token 與有效單價，兩者未揭露，本列顯示「缺分母」。不新增 Alloc_In 實驗室選項。")


def l1_rows_new():
    R = ROWS
    ext = ("CTL_Monetize（模型假設；Gov_Map GM594 區間）", "=CTL_Monetize", "=CTL_Monetize")
    def cap(col, key): return f"=Cap_In!${col}${R[key]}"
    def mn(key): return f"=MIN(Cap_In!$D${R[key]},Cap_In!$E${R[key]})"
    def mx(key): return f"=MAX(Cap_In!$D${R[key]},Cap_In!$E${R[key]})"
    return [
        ("MAPI", "變現率 m — API 路線（2025，三分法）", "OpenAI 2025；API 營收（營收 − 消費訂閱 − 商用席次）÷（AL_DAPI × Cap_In 第 31 列層級組合混合有效單價）；v5.34 J18／J19",
         cap("C", "m_api"), mn("m_api"), mx("m_api"), "x", "低／高＝Cap_In H8 D／E 欄的最小／最大值（API 為餘額，D／E 不是同向組合）", READ_M,
         "訂閱占比（SRC_DEM_039 區間）、商用席次份額（Assumed）、API 全年平均比例、付費層級組合", "商用席次份額：Assumed（Cap_In H8）；API 份額只有 Sacra 15–20%（二手）",
         *ext, "CTL_Monetize；AL_DAPI；SRC_DEM_007；SRC_DEM_039；IF_PriceRef_*", f"Cap_In 第 {R['m_api']} 列", "API 營收為餘額（OpenAI 未揭露 API 營收）；分母為模型 token 需求（Assumed）"),
        ("MSub", "變現率 m — 消費訂閱路線（2025）", "OpenAI 2025；消費訂閱營收（SRC_DEM_007 × SRC_DEM_039）÷（AL_DChatPaid × 消費份額 0.75 × 混合有效單價）；v5.34 J19",
         cap("C", "m_cons"), cap("D", "m_cons"), cap("E", "m_cons"), "x", "低＝營收取低（訂閱占比 0.61）、token 取高（每則 token 高、免費占比低、消費份額 0.90）；高反之", READ_M,
         "訂閱占比、每則提示 token 數、ChatGPT 免費占比、消費訂閱占付費 token 份額、付費層級組合", "消費份額：Assumed（Cap_In H8）；每則 token 數、免費占比：Assumed（Alloc_In）",
         *ext, "CTL_Monetize；AL_DChatPaid；SRC_DEM_007；SRC_DEM_039；IF_PriceRef_*", f"Cap_In 第 {R['m_cons']} 列", "OpenAI 未揭露 ChatGPT token 數與訂閱者用量分布"),
        ("MSeat", "變現率 m — 商用席次路線（2025）", "OpenAI 2025；商用席次營收（SRC_DEM_007 × 席次份額 0.10）÷（AL_DChatPaid ×（1 − 消費份額）× 混合有效單價）；v5.34 J18／J19",
         cap("C", "m_seat"), mn("m_seat"), mx("m_seat"), "x", "低／高＝Cap_In H8 D／E 欄的最小／最大值（席次份額與消費份額同列變動，不是同向組合）", READ_M,
         "商用席次份額、消費訂閱占付費 token 份額、每則提示 token 數、免費占比", "席次份額與席次用量占比：Assumed（Cap_In H8）；SRC_DEM_045 只有 p95／中位數",
         *ext, "CTL_Monetize；AL_DChatPaid；SRC_DEM_007；IF_PriceRef_*", f"Cap_In 第 {R['m_seat']} 列", "席次營收與席次 token 皆為 Assumed 份額（OpenAI「企業」口徑未定義）"),
        ("MixFactorAPI", "m_API 的隱含組合因子（＝m_API ÷ 折讓因子）", "OpenAI 2025；折讓因子＝(1 − d) ÷ (1 − B4_Disc)，基準 d＝B4_Disc（1.0）；v5.34 J16（顯示用）",
         cap("C", "mix"), mn("mix"), mx("mix"), "x", "低／高＝Cap_In H8 D／E 欄的最小／最大值（d 取 B4_Disc 高端 0.4／低端 0.1）", READ_MIX,
         "m_API、有效折扣 B4_Disc 區間", "折讓 d 區間：Assumed（Cap_In C12，0.1–0.4，J20）",
         f"代理型極端組合因子（Cap_In H6 第 {v532.ROWS['cc_ratio']} 列：Requesty χ 0.919、輸入占 0.995）", f"=Cap_In!$C${v532.ROWS['cc_ratio']}", f"=Cap_In!$C${v532.ROWS['cc_ratio']}",
         "B4_Disc；AL_DAPI；SRC_DEM_007；IF_PriceRef_*", f"Cap_In 第 {R['mix']} 列", "組合因子無直接觀測（OpenAI 未揭露 API token 的快取／輸入占比）"),
        ("TokPerPromptClose", "閉合解：需求 token 佔滿機隊有效產能所需的每則 token 數 τ*", "OpenAI 2025；T_chat*＝[有效服務 GW − AL_DAPI ÷ AL_BlendPaid] ÷ [(1 − AL_FreeShare) ÷ AL_BlendPaid ＋ AL_FreeShare ÷ AL_BlendFree]；τ*＝T_chat* ÷（SRC_DEM_012 × 365）；v5.34 B3",
         cap("C", "tau"), cap("E", "tau"), cap("D", "tau"), "tok", "低＝Azure 倍數取高（3）、實際利用率取低（0.3）；高反之（Cap_In H9 E／D 欄）", READ_TAU,
         "推論支出 SRC_DEM_018、Azure 計價倍數、實際利用率、世代組合、免費占比、API token", "Azure 倍數、實際利用率：Assumed（Alloc_In C23、C24）",
         "Alloc_In C15 區間（每則提示 token 數 2,000–11,000）", "=AL_TokPerPrompt_Lo", "=AL_TokPerPrompt_Hi", "AL_ServeGWSpend；AL_SpendBasis；AL_UtilActual；AL_BlendPaid；AL_BlendFree；AL_FreeShare；AL_DAPI；SRC_DEM_012",
         f"Cap_In 第 {R['tau']} 列", "閉合解由 C23、C24 決定，不是獨立證據"),
        ("MAPI_Anthropic", "變現率 m — API 路線（Anthropic；J21 對照，缺分母）", "Anthropic 2025；需要 Anthropic 年 API token 與有效單價（未揭露）；v5.34 J21",
         cap("C", "anth_m"), cap("D", "anth_m"), cap("E", "anth_m"), "x", "無（文字）", READ_ANTH,
         "Anthropic 用量計費營收 SRC_DEM_034、token 分母（缺）、有效單價（缺）", "token 分母未揭露",
         f"Anthropic 用量計費占營收（M，Cap_In 第 {R['anth_share']} 列）／雲端分潤比（N，第 {R['anth_rs']} 列）", cap("C", "anth_share"), cap("C", "anth_rs"),
         "SRC_DEM_034；SRC_DEM_035；SRC_DEM_036；SRC_DEM_037", f"Cap_In 第 {R['anth_m']} 列", "缺分母：Anthropic 年 API token、有效單價"),
    ]


def l1_judge(wb):
    """L1 P column: L1_MAPI／MSub／MSeat = inside／outside the Gov_Map range of CTL_Monetize (as L1_MFleet); L1_MixFactorAPI = ratio to the agent extreme."""
    ws = wb["L1"]; lo, hi = v532._gm_ref(wb); out = []
    for name in ("L1_MAPI", "L1_MSub", "L1_MSeat"):
        r = int(wb.defined_names[name].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == name, (name, r)
        rng = f'"落在 "&TEXT({lo},"0.0")&"–"&TEXT({hi},"0.0")&" 區間'
        ws[f"P{r}"].value = f'=IF(ISNUMBER(D{r}),IF(AND(D{r}>={lo},D{r}<={hi}),{rng}內",{rng}外"),"推算值非數字（本情境）")'
        out.append(r)
    r = int(wb.defined_names["L1_MixFactorAPI"].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == "L1_MixFactorAPI"
    ws[f"P{r}"].value = (f'=IF(AND(ISNUMBER(D{r}),ISNUMBER(M{r})),"代理型極端組合因子 "&TEXT(M{r},"0.00")&"；本值為其 "&TEXT(D{r}/M{r},"0.0")&" 倍（1＝參考請求）","推算值非數字（本情境）")')
    out.append(r)
    return out


# ================================================================== B3: Checks M4 (WARN; appended after M3, counted in GOV_Warnings)
def checks_m4(wb):
    ws = wb["Checks"]
    r3 = next(r for r in range(5, ws.max_row + 1) if ws[f"A{r}"].value == "M3")
    assert ws[f"A{r3 + 1}"].value is None
    rr = ROWS["res_fleet"]; r = r3 + 1
    f = f'=IF(ISNUMBER(Cap_In!$C${rr}),IF(OR(Cap_In!$C${rr}<0.5,Cap_In!$C${rr}>2),1,0),0)'
    put(ws, f"A{r}", "M4"); put(ws, f"B{r}", "需求路線付費 token ÷ 機隊付費 token（點估計）< 0.5 或 > 2：1＝兩路線不閉合", wrap=True); put(ws, f"C{r}", "WARN")
    put(ws, f"D{r}", f, F_CALC, fmt="0"); put(ws, f"E{r}", f"Cap_In H9 第 {rr} 列（AL_DPaid ÷ H7 機隊付費 token 點估計）；現值 0.465 → 觸發，屬預期（v5.34 B3）", F_NOTE)
    ref = wb.defined_names["GOV_Warnings"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "WARN 合計（含 H3、K1、M1–M4）"
    r1 = next(x for x in range(5, ws.max_row + 1) if ws[f"A{x}"].value == "M1")
    ws[f"A{r1 - 2}"].value = "M. 變現率 m 追蹤檢查（工作單 v5.32 r1 B3，J4 (a)；v5.33 r1 B4 加 M2、M3；v5.34 加 M4）：M1–M4 為 WARN 計入 GOV_Warnings（不阻擋）"
    return r


# ================================================================== B1: DB_Evidence E325–E337 (17 columns A..Q; layout of v531–v533)
def _ev(n, claim, src, tag, param, cur, new, verdict, note, sids, affected, grade, stance):
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, f"{note}｜暫編 {n}｜{ANDY}｜讀取者：chat 端（{WO} 0.5 節外部搜尋）",
            "已處理", sids, DASH, affected, grade, stance]


SECOND = "二手轉述，未取得一手"
EVIDENCE_V534 = [
    _ev("N01", "OpenAI 2026 Q1 營收 5.7 $B（確認）", "The Information 2026-05-22", "Interested-party／2 級（二手）", "Cap_In H10 2026 Q1 欄", DASH, "5.7 $B／季",
        f"採用（X38）：新登錄 {S(69)}；Active；H10 Q1 年化 22.8", SECOND, S(69), DASH, "2", "利害關係方"),
    _ev("N02", "OpenAI 2026 Q2 營收 6.7 $B", "WSJ 2026-08-18", "Interested-party／2 級（二手）", "Cap_In H10 2026 Q2 欄", "6.7（SRC_DEM_042）", "6.7",
        f"不重登：已有 SRC_DEM_042；備註補 N01 序列（{S(69)}）", "—", "SRC_DEM_042", DASH, "2", "利害關係方"),
    _ev("N03", "OpenAI 2026 推論支出預測 14.1 $B（12–18）", "Sacra（2026）", "Interested-party／二手／3 級", "Cap_In H10 2026 欄 m_fleet 的推論支出", "12.6（SRC_DEM_018，2025）", "14.1（12–18）",
        f"部分採用（X38）：新登錄 {S(70)}，狀態 Alt（預測值）；只進 H10 2026 欄", "預測值；Azure 計價口徑視同 SRC_DEM_018", S(70), DASH, "3", "利害關係方"),
    _ev("N04", "OpenAI API 占營收 0.15–0.20（2026 初）", "Sacra", "二手／3 級", "Cap_In H8 API 份額（餘額）與 H10 各欄 API 份額", "0.30（H1 二分法 1 − 0.70）", "0.15–0.20",
        f"採用（X38）：新登錄 {S(71)}（值 0.20、低 0.15）；J18 的 0.20 依據；份額為 Assumed 藍字，不連結", SECOND, S(71), "L1_MAPI（v5.34 新列）", "3", "利害關係方"),
    _ev("N05", "OpenAI 企業營收 2026-07 超過消費端（事件；7–9 月翻倍）", "OpenAI 經媒體（2026-07）", "Interested-party／2 級", "Cap_In H10 2026 份額序列", DASH, "事件",
        "登錄 DB_Evidence，不登 SRC；H10 2026 Q2 消費 0.55、FY2026 0.45 的依據（r0.1）", "「企業」口徑未定義", "SRC_DEM_023", DASH, "2", "利害關係方"),
    _ev("N06", "$200 方案週額度約 $2,600 GPT-5.5 API 等值 → Pro 約 $14,000／月（70×）、Claude Max 20x 約 $8,000／月（40×）、$20 方案約 $700／月（35×）", "SemiAnalysis 2026-06-10 X 貼文的轉述",
        "Analogy／二手（SemiAnalysis 不可單獨引用）", "Cap_In H8-5 訂閱 m 下限（方案上限讀法）", DASH, "700／14,000 $／月", "登錄 DB_Evidence，只作上限（Plus 20÷700＝0.03、Pro 200÷14,000＝0.014）；不登 SRC",
        "方法＝以程式工作負載跑到週上限；SemiAnalysis 規則：須第二來源", DASH, DASH, "3", "利害關係方"),
    _ev("N07", "ChatGPT Plus 5 小時視窗訊息上限：Astra 5–45、Sol 15–160、Luna 350–3,000；1 credit＝$0.04（第三方由牌價推得）", "第三方彙整 2026-10-07", "二手彙整／3 級", "每用戶 token 上限（對照）", DASH, "5–3,000 則／5 小時",
        "登錄 DB_Evidence；待一手（OpenAI 幫助中心）確認後才登 SRC", SECOND, DASH, DASH, "3", "第三方"),
    _ev("N08", "Codex 用戶序列補點：2026-08-21 20 M、08-31 25 M（口徑未定義）", "Sottiaux X 貼文（2026-08）", "Interested-party／2 級", "SRC_DEM_060 序列", "8 M（07-14）", "20 M／25 M",
        "不新增：SRC_DEM_060 備註補；無 token 量", "口徑未定義", "SRC_DEM_060", DASH, "2", "利害關係方"),
    _ev("N09", "企業議價折扣（顧問自述）：25 件談判中位數省 27%、區間 20–35%（對開價，非牌價；未驗證）；worked example 用 API 折扣 15%（假設值）", "redresscompliance（2024–2025）", "Interested-party／3 級（顧問以議價服務為業）",
        "Cap_In C12 B4_Disc 區間（J20）", "0.1–0.3", "0.1–0.4", "登錄 DB_Evidence；J20 依據（高端 0.3 → 0.4）；不登 SRC", "對開價而非牌價；未驗證", DASH, "Cap_In E12（區間端點；IF_Price* 不變）", "3", "利害關係方"),
    _ev("N10", "OpenAI Batch／Flex 占 API token 的比例：未找到", "搜尋範圍：OpenAI 定價頁、Flex／Priority 文件、DevDay 2026 報導、顧問議價文章", DASH, "折讓因子（Cap_In H8-4）", DASH, "未找到",
        "缺口登錄（「未找到」，含搜尋範圍，避免重搜）；方向性代理：折讓因子 (1 − d)/(1 − 0.2) 在 d＝0.2–0.4 時 1.0–0.75", "—", DASH, DASH, DASH, DASH),
    _ev("N11", "典型（中位數）付費用戶每月 token 用量、Codex 每用戶 token：未找到", "搜尋範圍：SemiAnalysis 2026-06-10 轉述、OpenAI Codex 定價頁、Claude Code 文件轉述、Codex 統計彙整", DASH, "訂閱 m 上限（用量分布）", DASH, "未找到",
        "缺口登錄；方向性代理：訂閱 m 下限＝月費 ÷ 方案上限（N06）；上限需用量分布（SRC_DEM_045 p95/中位數＝6 為唯一分布證據，企業端）", "—", "SRC_DEM_045", DASH, DASH, DASH),
    _ev("N12", "chat 端 2026-10-14 計算：m 分拆（2025 m_API 0.56／m_訂閱 3.65 二分法；2026 Q2 m_API 0.35、m_整體 1.34、m_fleet 0.78）、閉合解 τ* 13,950／14,650、LP 配置 ±1–5%、龍捲風（實收單價 P̄×m 55%、L 20%）",
        f"{WO} 0.3–0.4 節（Python 手算，輸入為 v5.33 快取值）", "Derived（chat 端）", "Cap_In H8–H10 驗收錨點", DASH, "見工作單 0.3 節", "登錄 DB_Evidence；H8／H9／H10 錨點來源；LP 配置不納入本單（第二階效應）", "—", DASH,
        "L1_MAPI、L1_MSub、L1_MSeat、L1_MixFactorAPI、L1_TokPerPromptClose（v5.34 新列）", DASH, "中立"),
    _ev("N13", "OpenAI 營收份額序列（消費／企業）：2024-10 消費 75%（SRC_DEM_038）→ 2025 70%（SRC_DEM_039）→ 2026-03 企業 >40%（SRC_DEM_023）→ 2026-07 企業超過消費（N05）", "SRC_DEM_038／039／023；N05",
        "Interested-party（「企業」口徑未定義）", "Cap_In H10 營收三分份額（每欄各自輸入，r0.1）", "0.70（2025）", "0.70 → 0.60 → 0.55 → 0.45", "登錄 DB_Evidence；H10 份額的依據（r0.1，Andy 15:49）", "「企業」口徑 OpenAI 未定義，本表視為席次＋API",
        "SRC_DEM_038；SRC_DEM_039；SRC_DEM_023", DASH, "2", "利害關係方"),
]


def evidence_rows():
    return EVIDENCE_V534


# ================================================================== B6: Decisions X35–X41 (10 columns; layout of v531–v533)
_ANDY_ALL = f"{ANDY_1535}；{ANDY_1539}；{ANDY_1549}；chat 端建議（「1 GW DC 收入：L 與 m」對話串），可撤回"
_X = [
    ("X35", "J15 CTL_Monetize 不改", "CTL_Monetize 基準 1 與 Gov_Map 區間 0.3–1.0 不改（m 序列穩定前不改；X26 J1 (a′) 延續）；本單新增的 m 分拆（H8）與序列（H10）只作追蹤", "Cap_In C64（不改）；Gov_Map GM594（不改）", "第 1 節"),
    ("X36", "J16 分工規則", "會同時改變成本的因子進 Q（每 GW 產出）側——快取命中率 χ、層級組合、ISL/OSL；只改變營收的因子進 m——折讓、訂閱用量落差、雲端分潤。理由：快取讀取 token 幾乎不耗 GPU 算力，"
     "若把組合效應放進 m 而 Q 仍按參考請求（χ＝0.55）算，等於對同一件事扣兩次。本單不改任何 Q 側輸入，只在 Cap_In H8-4 顯示 m_API 的組合因子 vs 折讓因子分解", "Cap_In H8-4；Excel README；本頁", "第 1 節、B2"),
    ("X37", "J17 m 的視角與用途", "m 是實驗室（OpenAI）視角的「付費 token 平均實收單價 ÷ OpenAI 有效單價」（Andy 15:35：「這個m當然是實驗室(OAI)視角」）。下游用途是 L1_FleetBreakeven 的回本條件（L·m ≥ 門檻），"
     "不是乘進每 GW 營收的係數；交付物是區間與「必須為真」條件，L1 新名稱以 _Lo／_Hi 並列，不給單一「建議值」", "L1_MAPI／MSub／MSeat／MixFactorAPI／TokPerPromptClose；Cap_In H8-5／H8-6", "第 1 節、B4"),
    ("X38", "J18 營收三分法", "Cap_In H1 第 71 列「API 占比＝1 − 訂閱占比」改為三分（H8）：消費訂閱（SRC_DEM_039 0.70）／商用席次 Assumed 0.10（0.05–0.15）／API＝餘額 0.20（0.15–0.25；SRC_DEM_071 Sacra 15–20%）。"
     "廣告 2026 起另列（H8 藍字 0.5，0–1.0），不進任何 m 的分子。H10 份額每欄各自輸入（r0.1：2026 Q1 0.60／0.20／0.20、Q2 0.55／0.25／0.20、FY2026 0.45／0.35／0.20）", "Cap_In H8 第 1 列、H10；Gov_Map 新列；SRC_DEM_069–071", "第 1 節、B1、B2、B5"),
    ("X39", "J19 m 按收費模式拆分", "新增 m_API、m_消費訂閱、m_商用席次三列與 token 加權的 m_整體（自我檢查＝L1_MImplied）；分母：API token＝AL_DAPI；消費訂閱 token＝AL_DChatPaid × 消費占付費 token 份額（Assumed 0.75，0.6–0.9）；商用席次 token＝餘額",
     "Cap_In H8-2／H8-3；L1_MAPI／MSub／MSeat；Gov_Map 新列", "第 1 節、B2、B4"),
    ("X40", "J20 B4_Disc 區間", "高端 0.3 → 0.4（0.5 節折讓證據：顧問議價中位數 27%、20–35%，E333）；基準 0.2、低端 0.1 不改。只動 Gov_Map GM441／GM442 區間文字與 Cap_In E12（藍字，只在仍為 0.3 時寫），不動基準值，IF_Price* 數值不變",
     "Cap_In E12；Gov_Map GM441／GM442", "第 1 節、B6"),
    ("X41", "J21 Anthropic 第二方程式", "本單只建對照列（Cap_In H8-7）：Anthropic 2025 用量計費 ÷ 總營收（SRC_DEM_034 ÷（034 ＋ 035）≈ 0.83）與雲端分潤比（SRC_DEM_037 ÷ 036 ≈ 0.16）；Anthropic token 分母未揭露，"
     "L1_MAPI_Anthropic 顯示「缺分母（需 Anthropic 年 API token）」並列出所需輸入。不新增 Alloc_In 實驗室選項", "Cap_In H8-7；L1_MAPI_Anthropic", "第 1 節、B2、B4"),
]
DECISIONS_V534 = [[i, V, f"{i} {t}", txt, DATE, _ANDY_ALL, "v5.34 已建", where, f"{WO} {sec}", "否"] for i, t, txt, where, sec in _X]


# ================================================================== README (version string is built from VERSION; v5.33 text is kept after it)
README_VERSION = (VERSION + "（判斷類，工作單 docs/workorders/20261014_v5.34.md r0.1：變現率 m 細化——Cap_In 新增 H8「m 分拆」（營收三分 消費訂閱／商用席次／API × token 三分 → m_API 0.56、m_消費訂閱 4.26、"
                  "m_商用席次 1.83、m_整體 1.743＝L1_MImplied；m_API＝折讓因子 × 隱含組合因子；訂閱 m 下限（方案上限讀法）；「必須為真」；J21 Anthropic 對照）、H9「token 帳三路線」（需求／機隊／上限、殘差、"
                  "閉合解 τ* ≈ 13,950）、H10「m 季度序列」（2025／2026 Q1／Q2／FY2026；份額每欄各自輸入）；L1 新增 L1_MAPI、L1_MSub、L1_MSeat、L1_MixFactorAPI、L1_TokPerPromptClose、L1_MAPI_Anthropic；"
                  "Checks M4；B4_Disc 高端 0.3 → 0.4（Cap_In E12；IF_Price* 不變）；SRC_DEM_069–071、DB_Evidence E325–E337、Decisions X35–X41；既有 IF_、L1_ 數值全部不變；CTL_Monetize 不改）。以下為 "
                  + v533.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v533.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v533.VERSION.split("_")[-1]):]
README_ROW = ("變現率 m 細化（v5.34）",
              "Cap_In H8：營收三分（消費訂閱＝SRC_DEM_007 × SRC_DEM_039；商用席次＝× Assumed 0.10；API＝餘額）× token 三分（API＝AL_DAPI；消費訂閱＝AL_DChatPaid × 0.75；席次＝餘額）→ m_API、m_消費訂閱、m_商用席次、"
              "m_整體（token 加權，自我檢查＝L1_MImplied）；m_API＝折讓因子 (1 − d)/(1 − B4_Disc) × 隱含組合因子（J16 顯示用）；訂閱 m 下限＝月費 ÷ 方案上限（N06）；「必須為真」：m_消費訂閱＝1 所需每訂閱者年 token。"
              "H9：需求／機隊／上限三路線付費 token、殘差（Checks M4）、閉合解 τ*（需求 token 佔滿機隊有效產能所需的每則 token 數）。H10：2025／2026 Q1／Q2／FY2026 的 m 序列（顯示用）。"
              "J16 分工規則：會同時改變成本的因子（χ、層級組合、ISL/OSL）進 Q 側，只改變營收的因子（折讓、訂閱用量落差、雲端分潤）進 m。J17：m 為實驗室視角、回本條件用，交付物為區間與「必須為真」。"
              "CTL_Monetize 不改（X35）；B4_Disc 高端 0.4（X40）；Anthropic 只建對照列（X41）。")

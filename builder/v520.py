# v5.20 (work order docs/workorders/20261006_v5.20.md): X3 (X2 high-segment rows: DB_Evidence, GM578 range, C2 list),
# X4 (Calib F67 conflicting evidence, no value change), X5 (amortization coupling note). Excel-owned writes use old-value guards
# (same rule as gov.gm_update), so a rebuild from v5.20 never overwrites a later Excel edit.
from common import put, F_IN, F_CALC, L

DATE = "2026-10-06"
READER = "讀取者：CC（v5.19 查核）＋chat 端（2026-10-06 搜尋）；摘要級，原文未讀（依 R5／R6 不得標為已讀；搜尋工具只回彙整摘要，未標逐項出處，故不指定網址）"
NO_URL = "搜尋結果摘要（WebSearch；未標逐項出處，依 R5 不指定網址）"


def _row(eid, claim, src, param, cur, new, verdict, note, affected, stance="—"):
    # DB_Evidence columns: ID, 日期, 主張, 來源, 標記, 對應參數, 當時值, 新資訊值, 判定, 處理版本, 備註, 狀態, SRC_ID, 取代者, 受影響, 來源等級, 立場
    return [eid, DATE, claim, src, "Analogy（摘要級，原文未讀）", param, cur, new, verdict, "v5.20", f"{note}｜{READER}", "已處理", "—", "—", affected, "3", stance]


EVID_V520 = [
    _row("E236", "Arch E6 層數（Astra；現 100，區間 80–160）：開放權重旗艦的層數", NO_URL, "Arch E8（GM205）", "100（80–160）",
         "Llama 3.1 405B 126 層；DeepSeek-V3 61 層（開放權重，稠密與 MoE 架構不同）",
         "已讀摘要，作為區間依據；區間不改（X3 A1）",
         "查詢詞：「frontier LLM number of transformer layers largest models Llama 3.1 405B 126 layers DeepSeek V3 61 layers」｜不得寫入『405B 為 80 層』（誤植，80 層為 70B）｜Andy 2026-10-06 核准（X3）",
         "IF_FullCost_*（Astra 欄）"),
    _row("E237", "Arch E6 總參數（Astra；區間 2,000–10,000 B）：前沿旗艦總參數", NO_URL, "Arch E6（GM203）", "基準（2,000–10,000 B）",
         "Kimi K3 2.8T（2026-07-16，開放權重）；Llama 4 Behemoth 2T（288B 啟用）；xAI 約 2T（另有 4–6T 估計，Interested-party）；Anthropic、OpenAI 旗艦未揭露",
         "已讀摘要，支持區間下端；上端 10T 無可比；區間不改（X3 A1）",
         "查詢詞：「frontier lab flagship model total parameters estimate 2026 trillion parameters Kimi K2 1T Grok 4 Behemoth 2T」｜Andy 2026-10-06 核准（X3）",
         "IF_RevGW_Astra、IF_FullCost_Astra", "xAI：利害關係方"),
    _row("E238", "Cap_In C36 儲存層代碼：公開快取條款與推測的儲存分層", NO_URL, "Cap_In C36（GM459）", "基準（D36–E36）",
         "公開快取條款保留時間（5 分鐘至 1 小時、延長至 24 小時）與推測的 HBM／DRAM／NVMe 分層一致；分層實作非官方揭露",
         "已讀摘要，支持現值；不改（X3 A1）",
         "查詢詞：「prompt caching storage tier KV cache offload DRAM SSD retention 5 minutes 1 hour pricing Anthropic OpenAI cache write」｜Andy 2026-10-06 核准（X3）",
         "L1_Ans9"),
    _row("E239", "Workload G8 每輪思考 token h（Coding agent；現 600）", "arXiv 2606.24820（SHERLOC；搜尋結果摘要，原文未讀）", "Workload G8（GM270）", "600（×0.5–×2）",
         "SWE-bench Verified 每條軌跡推理 token 平均 19.5k（Qwen3-235B-A22B-Thinking）；以 Workload G5 輪數 T＝30 換算約 650／輪（chat 端換算）",
         "已讀摘要，支持基準 600；不改（X3 A1）",
         "查詢詞：「coding agent reasoning tokens per turn thinking tokens SWE-bench trajectory」｜每軌跡非每輪，換算依賴 T＝30（Assumed）；模型與 harness 不同（Analogy）｜Andy 2026-10-06 核准（X3）",
         "L1_Ans9"),
    _row("E240", "Workload G12 並行子代理數 m（Coding agent；現 0）", NO_URL, "Workload G12（GM290）", "0（0 至 max(1,×2)）",
         "Claude Code subagent 同時最多 10、workflow 同時 16（產品上限）；Kimi 300 agent（宣傳數字）；典型使用的平均並行數無統計",
         "上限有可比、典型值無；不改（X3 A2）。基準 0＝標準 harness 為單代理，屬定義",
         "查詢詞：「coding agent sub-agents parallel number Claude Code subagents concurrent max parallel 10 agents Codex」｜GM290 不列入 C2（有上限可比對象）｜Andy 2026-10-06 核准（X3）",
         "L1_Ans9"),
    _row("E241", "Alloc_In C7 改版計畫數 N_refresh（現 2；區間 0–4）：OpenAI 公開點版本節奏", NO_URL, "Alloc_In C7（GM578）", "2（0–4）",
         "OpenAI GPT-5.x 點版本：5.1（2025-11）、5.2（2025-12）、5.4（2026-03-05）、5.5（2026-04-23）、5.6（約 2026-07）；過去 12 個月約 5 個。『改版計畫』為相對家族計畫的研發運算當量，不等於對外版本號，只作上界參考",
         "區間上限 4 → 6，基準 2 不變（X3 A3；Andy 2026-10-06）",
         "查詢詞：「OpenAI number of model releases per year GPT-5 5.1 5.2 refresh cadence pretraining runs per year」｜媒體轉述，非官方揭露",
         "IF_AllocQ1、IF_AllocQ2、IF_AllocRDGW、L1_Ans1–3（高端）", "媒體轉述"),
    _row("E242", "Workload G9 每輪可見輸出 o（Coding agent；現 400）", NO_URL, "Workload G9（GM275）", "400（×0.5–×2）",
         "只得『agentic coding 輸出約占總 token 0.5%』的單一工作階段樣本；無每輪分布",
         "已搜尋，判定無可比對象（X3 A4；適用 C2）",
         "查詢詞：「agentic coding average output tokens per turn visible response tokens OpenRouter state of AI programming completion tokens」｜理由：只有輸出占總 token 比，無每輪可見輸出的分布｜Andy 2026-10-06 核准（X3，C2）",
         "L1_Ans9"),
    _row("E243", "Calib F69 η_p 倍數（VR200；現 1；區間 0.5–1.5）", NO_URL, "Calib F69（GM354）", "1（0.5–1.5）",
         "MLPerf Inference v6.1 的 VR200 結果只有整體吞吐，無 prefill 拆分",
         "已搜尋，判定無可比對象（現有資料無法分離）（X3 A4；適用 C2）",
         "查詢詞：「Vera Rubin NVL72 inference benchmark prefill throughput MLPerf Inference InferenceX VR200 results」｜『現有資料無法分離』屬對象性質，非『不存在』｜Andy 2026-10-06 核准（X3，C2）",
         "L1_Ans9"),
    _row("E244", "Calib F67 η_d 倍數（VR200；現 1.0；區間 0.5–1.5）：第三方 MLPerf v6.1 換算", NO_URL, "Calib F67（GM344）", "1.0（0.5–1.5）",
         "Nebius 公布之 MLPerf Inference v6.1 DeepSeek-R1 數據，第三方換算 VR200 每 GPU 約 GB300 的 1.6–2×；Nebius 量測 VR200 36 GPU、GB300 72 GPU；情境（offline／server／interactive）未讀到",
         "待查證；指向 F67 低端；與模型內 MLPerf v6.1 interactive（Calib 第 151 列 2.575×，模型 2.525×）衝突未解（X4；F67 數值與區間不改）",
         "查詢詞：「Rubin NVL72 first MLPerf Inference v6.1 submission Vera Rubin tokens per second DeepSeek-R1」｜Nebius 原文未讀（只見 remio.ai 摘要轉述）；NVIDIA 宣稱最高 2.5×（Interested-party）｜Andy 手動下載 MLCommons v6.1 結果表後另開工作單處理｜Andy 2026-10-06 決定（X4）",
         "IF_FullCost_*、IF_RevGW_*（VR200、Rubin Ultra 欄）", "NVIDIA：利害關係方"),
]


def evidence_rows():
    return EVID_V520


# ------------------------------------------------------------------ Decisions
DECISIONS_V520 = [
    ['X3', 'v5.20', 'X2 新高段 8 列的 6.2 完成檢查',
     '第 2.3 節 8 列：A1 GM205、GM203、GM459、GM270 判齊備；A2 GM290 判齊備（基準 0＝標準 harness 為單代理，屬定義）；A3 GM578 區間上限 4 → 6，基準 2 不變；'
     'A4 GM275、GM354 核准為「已搜尋、無可比對象」（C2 適用列名清單附加此二列）。DB_Evidence E236–E243（全部 Analogy，摘要級，原文未讀）',
     '2026-10-06', '「all ok」（回覆 chat 端 A1–A4 建議）', 'v5.20 已建',
     'DB_Evidence E236–E243；Alloc_In!E7（AL_Nrefresh_Hi）；Gov_Map GM205、GM203、GM459、GM270、GM290、GM578、GM275、GM354；Decisions C2', '工作單 v5.20 第 0、1 節', '否'],
    ['X4', 'v5.20', 'Calib F67 衝突證據（VR200 η_d 倍數）',
     'Calib F67 維持基準 1.0 與區間 0.5–1.5；記錄衝突證據（DB_Evidence E244：Nebius 換算每 GPU 1.6–2×，與模型內 MLPerf v6.1 interactive 2.575× 對 2.525× 衝突未解）；'
     '原文補查由 Andy 手動下載 MLCommons v6.1 結果表，另開工作單處理。GM345（Rubin Ultra G67）不動',
     '2026-10-06', '「all ok」（回覆 chat 端 B (a)＋(c)）', 'v5.20 已建', 'Calib F67（Gov_Map GM344）；DB_Evidence E244', '工作單 v5.20 第 0、2 節', '否'],
    ['X5', 'v5.20', 'Hopper 攤提耦合維持並加註',
     'IF_FullCost_* 含自下而上攤提，攤提分母為層級組合的機隊 token；同一世代任一層級 SLO 不可達時，該世代所有層級的 FullCost 均回傳文字；IF_RevGW_* 只依自身層級，可能仍為數值。設計維持，只加註（Interface 說明列、README）',
     '2026-10-06', '「all ok」（回覆 chat 端 C (a)）', 'v5.20 已建', 'Interface A2 說明；README', '工作單 v5.20 第 0、3 節', '否'],
]
C2_OLD = "（Andy 2026-10-06 追認，K1）。不作概括適用"
C2_NEW = "（Andy 2026-10-06 追認，K1）；GM275（Workload G9）、GM354（Calib F69）（Andy 2026-10-06 核准，X3）。不作概括適用"
C2_QUOTE = "；Andy 2026-10-06 核准 GM275、GM354（X3，「all ok」，經 chat 端轉達）"


def decisions_update(wb):
    """C2: append GM275 / GM354 to the applicable-rows list (once)."""
    ws = wb["Decisions"]; n = 0
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value == "C2":
            d = ws.cell(r, 4)
            if isinstance(d.value, str) and C2_OLD in d.value and "GM275" not in d.value:
                d.value = d.value.replace(C2_OLD, C2_NEW); n += 1
            f = ws.cell(r, 6)
            if isinstance(f.value, str) and "GM275" not in f.value:
                f.value = f.value + C2_QUOTE; n += 1
    return n


# ------------------------------------------------------------------ Gov_Map: reason-column notes, GM578 range text
def _ok(eid): return f"｜v5.20 X3：6.2 齊備（DB_Evidence {eid}；摘要級）"
def _none(eid): return f"｜v5.20 X3：已搜尋、無可比對象（Andy 2026-10-06 核准，C2；DB_Evidence {eid}）"
NOTES = [
    ("Arch", "E8", _ok("E236")),
    ("Arch", "E6", _ok("E237")),
    ("Cap_In", "C36", _ok("E238")),
    ("Workload", "G8", _ok("E239")),
    ("Workload", "G12", _ok("E240") + "｜基準 0＝標準 harness 為單代理，屬定義"),
    ("Alloc_In", "C7", _ok("E241") + "｜區間上限 4 → 6（Andy 2026-10-06，X3；基準 2 不變）"),
    ("Workload", "G9", _none("E242")),
    ("Calib", "F69", _none("E243")),
    ("Calib", "F67", "｜v5.20 X4：低端有一筆未查證第三方換算（DB_Evidence E244），原文補查中"),
]
GM578_M = ("—", "0–6（上限依 GPT-5.x 點版本節奏，Andy 2026-10-06，X3）")


def gov_update(ws, append_text):
    loc = {(ws[f"C{r}"].value, ws[f"D{r}"].value): r for r in range(5, ws.max_row + 1) if ws[f"C{r}"].value}
    n = 0
    for sh, cell, txt in NOTES:
        r = loc.get((sh, cell))
        assert r is not None, f"v5.20: Gov_Map row {sh}!{cell} not found"
        if append_text(ws[f"N{r}"], txt): n += 1
    r = loc[("Alloc_In", "C7")]
    if ws[f"M{r}"].value == GM578_M[0]:
        ws[f"M{r}"].value = GM578_M[1]; n += 1
    return n


# ------------------------------------------------------------------ Excel-owned input (old-value guard)
def inputs_update(wb):
    log = []
    ws = wb["Alloc_In"]
    if ws["E7"].value == 4 and ws["A7"].value.startswith("改版計畫數 N_refresh"):
        ws["E7"].value = 6; log.append("Alloc_In!E7: 4 -> 6 (X3 A3)")
    return log


# ------------------------------------------------------------------ X5 text
X5 = ("　｜X5（v5.20）：IF_FullCost_* 含自下而上攤提，攤提分母為層級組合的機隊 token；同一世代任一層級 SLO 不可達時，該世代所有層級的 FullCost 均回傳文字"
      "（例：Hopper 在 C18 或 CTL_ProdDerate ≤ 約 0.72）。IF_RevGW_* 只依自身層級，可能仍為數值（Andy 2026-10-06 維持此設計）")


def interface_note(wb):
    ws = wb["Interface"]
    if X5 not in str(ws["A2"].value):
        ws["A2"].value = f"{ws['A2'].value}{X5}"

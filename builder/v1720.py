# v17.2 (work order docs/workorders/20261020_W1第二來源_B1.md, branch claude/w1-b1): W1 second sources, B1 segment (governance writes).
# PATCH version (CLAUDE.md 4: only Evidence／SRC records and marks; no model cell value changes).  Andy 2026-10-20 17:17 (C rules), 17:29 (Q1–Q14 as default).
#   1   A 86: one Alt record per original (src_new_records, appended by gov.src_append before src_refresh so X–Z／names／SRC_Index cover it);
#             the original's R = new SRC_ID, S = 2026-10-20 (apply, guarded: only while R is '—').
#   2   C1 53: R = "免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）".
#   3   Q11: SRC_HAR_003／004／005／006／008／010／011／012 L = 中立, M = ARC Prize 官方自測 (originals kept in W, revision 9).
#   4   Q1: SRC_DEM_004／005 J (The Information), M without "FT"; 005／006 notes.  5 Q3: SRC_PRC_049／050 (gpt-6.1-sol cached input, Alt), 006–008 notes.
#   6   Q4: SRC_HW_096／097 (Alt).  7 Q6: SRC_DC_021 (Alt).  8 Q7: SRC_DC_022 (Alt); SRC_DC_010 D／E are already 50／60 (nothing to write).
#   9   Q5: SRC_HW_046 note.  10 Q8–Q10, Q12, Q13, B0 text fields.  11 Q14: nothing written (see the report: D／E already hold the values).
# Every write to an existing (Excel-owned) SRC cell is guarded by its old value; a re-run is a no-op (idempotent).  Decisions SL51-01／02.
import json
import os

import v1710
import v1410
DASH = "—"

V = "v17.2"
VERSION = "20261020_Tokenomics_v17.2"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-20"
WO = "工作單 docs/workorders/20261020_W1第二來源_B1.md"
EVD = "docs/evidence/20261020_W1第二來源A段/"
DEC_BY = "Andy 2026-10-20 17:17「合理，同意」（C 類規則）；17:29「照預設」（審閱檔 Q1–Q14）"
DATA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1720_data.json"), encoding="utf-8"))
C1_TEXT = "免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）"
TAG = f"｜{V} 更正（修訂九；Decisions SL51-01）：原"


def _rows(wb):
    out = {}
    for sh in ("SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Cap", "SRC_Harness", "SRC_Demand"):
        ws = wb[sh]
        for r in range(5, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if isinstance(v, str) and v.startswith("SRC_"):
                out[v] = (ws, r)
    return out


def _rec(i, sheet, metric, val, lo, hi, unit, basis, applies, date, src, grade, stance, stance_note, hand, use, note):
    return dict(id=i, sheet=sheet, metric=metric, val=val, lo=lo, hi=hi, unit=unit, basis=basis, applies=applies, date=date, src=src,
                grade=grade, stance=stance, stance_note=stance_note, hand=hand, status="Alt", ev=DASH, s="U-V1720", use=use, note=note)


# ================================================================== new Alt records (A 86 + Q3／Q4／Q6／Q7)
Q_NEW = [
    _rec("SRC_PRC_049", "SRC_Price", "gpt-6.1-sol 快取輸入（短上下文）", 0.10, None, None, "$/M", "Standard；短上下文", "gpt-6.1-sol", "2026-10-20（讀取日）",
         "OpenAI 官方牌價頁 developers.openai.com/api/docs/pricing（2026-10-20 讀取，WebFetch）", 2, "利害關係方", "OpenAI 牌價（牌價本身即事實，誤報誘因低）",
         "一手（WebFetch 讀取，非逐字原文）", "—（未連結模型格；主值 SRC_PRC_007 不改）",
         f"{V} W1 B1 Q3：官方頁 2026-10-20 已改列 gpt-6.1-sol，快取輸入短上下文 0.10、長上下文 0.20（SRC_PRC_050），新鮮輸入與輸出值不變；"
         f"原紀錄 SRC_PRC_006／007／008（GPT-6 Sol）保留為當時有效值；是否改主值、是否視為一次 L 觀測點由 Andy 判斷，未回應則不改（審閱檔 Q3；{EVD}）"),
    _rec("SRC_PRC_050", "SRC_Price", "gpt-6.1-sol 快取輸入（長上下文）", 0.20, None, None, "$/M", "Standard；長上下文", "gpt-6.1-sol", "2026-10-20（讀取日）",
         "OpenAI 官方牌價頁 developers.openai.com/api/docs/pricing（2026-10-20 讀取，WebFetch）", 2, "利害關係方", "OpenAI 牌價（牌價本身即事實，誤報誘因低）",
         "一手（WebFetch 讀取，非逐字原文）", "—（未連結模型格；主值 SRC_PRC_007 不改）",
         f"{V} W1 B1 Q3：同 SRC_PRC_049（短上下文 0.10）；本筆為長上下文 0.20（審閱檔 Q3；{EVD}）"),
    _rec("SRC_HW_096", "SRC_HW", "GB300 NVL72 採購單價（Loop Capital 估計，訓練級機架）", None, 3.7, 4.0, "$M/架", "分析師估計（訓練級機架）；經轉述，原文未讀", "GB300 NVL72",
         "2026（報導）", "Loop Capital 估計，經 gpusmith 資料表與 spheron.network 轉述｜https://gpusmith.com/datasheets/nvidia-gb300-nvl72-datasheet.pdf", 2, "中立",
         "賣方分析師估計（非成交價）；經轉述（R3）", "二手（WebFetch 讀取，非逐字原文）", "—（未連結模型格；主值 SRC_HW_010＝5 不改）",
         f"{V} W1 B1 Q4：作 SRC_HW_010 區間參考；摘錄「$3.7M to $4.0M per training class rack, reported.」（2026-10-20）；Loop Capital 原文未讀（R3）（審閱檔 Q4；{EVD}）"),
    _rec("SRC_HW_097", "SRC_HW", "GB300 NVL72 採購單價（gpusmith 列示，推論最佳化）", None, 6.0, 6.5, "$M/架", "估計；未註明來源", "GB300 NVL72",
         "2026（報導）", "gpusmith 資料表（未註明來源；A 段原標 Tom's Hardware 有誤）｜https://gpusmith.com/datasheets/nvidia-gb300-nvl72-datasheet.pdf", 3, "中立",
         "資料表整理站；6.0–6.5 未註明來源（待查核）", "二手（WebFetch 讀取，非逐字原文）", "—（未連結模型格；主值 SRC_HW_010＝5 不改）",
         f"{V} W1 B1 Q4：作 SRC_HW_010 區間參考；值未註來源，等級 3（審閱檔 Q4；{EVD}）"),
    _rec("SRC_DC_021", "SRC_DC", "Nebius 伺服器與網路設備使用年限", 5, None, None, "年",
         "會計政策；servers and network equipment（未單獨寫 GPU）；2026-01-01 起往後適用（prospective）", "Nebius", "2026Q1（6-K）",
         "Nebius 2026Q1 6-K 附件（SEC EDGAR）｜https://www.sec.gov/Archives/edgar/data/0001513845/000110465926064092/nbis-20260331xex99d2.htm；"
         "https://www.sec.gov/Archives/edgar/data/0001513845/000110465926064092/nbis-20260331xex99d1.htm", 2, "利害關係方",
         "公司自定會計政策：延長年限可提高帳面獲利", "一手（WebFetch 讀取，非逐字原文）", "—（Inputs!F23 不改；列入下次 Nebius 模型工作單）",
         f"{V} W1 B1 Q6：4 → 5 年，2026-01-01 起未來適用；摘錄「applied this change in accounting estimate prospectively beginning January 1, 2026」；"
         f"Q1 2026 折舊減 US$43.1M（WebFetch 摘要，未獨立核對）；FY2025 20-F 附註未讀到；原文見 {EVD}B0/Q2Q5Q6.md；與 SRC_DC_008（4 年，2025 口徑）時序不同"),
    _rec("SRC_DC_022", "SRC_DC", "每 GW 建置成本（Bernstein）", 35, None, None, "$B/GW", "AI 資料中心總建置成本（Bernstein）；口徑待查（是否與 SRC_DC_010 含同樣項目未確認）", "—",
         "2025（報導）", "Investing.com 轉述 Bernstein 分析｜https://www.investing.com/news/stock-market-news/how-much-does-a-gw-of-data-center-capacity-actually-cost-4314046",
         2, "中立", "賣方研究（Bernstein）經財經媒體轉述；口徑待查", "二手（WebFetch 讀取，非逐字原文）", "—（未連結模型格；只作 Checks!C4 對照的參考）",
         f"{V} W1 B1 Q7：摘錄「Building one gigawatt ... costs around $35 billion」（2026-10-20）；比 SRC_DC_010（黃仁勳 50–60）低 30–42%，口徑未確認；"
         f"注意 SRC_DC_011「NVIDIA 含量約 35」是另一個量，數字碰巧相同（審閱檔 Q7；{EVD}）"),
]


def src_new_records(wb):
    """A-class Alt records: 指標／口徑／適用對象 copied from the original record (read from the workbook before any v17.2 edit)."""
    rows = _rows(wb); out = []
    for a in DATA["A"]:
        if a["id"] in rows:
            continue
        ws, r = rows[a["orig"]]
        assert ws.title == a["sheet"] and r == a["row"], (a["orig"], ws.title, r)
        note = (f"{V} W1 第二來源 B1（A 類，{a['orig']} 的第二來源）：讀取結果 {a['read']}；摘錄「{a['excerpt']}」（{a['date']}）；"
                f"讀取通道 {a['channel']}；A 段備註：{a['note']}；B0 複核：{a['b0']}；值為頁面原文照錄（單位見 F 欄），未換算；依據 {EVD}B1_動作清單.csv")
        out.append(_rec(a["id"], a["sheet"], ws[f"B{r}"].value, a["val"], None, None, a["unit"], ws[f"G{r}"].value, ws[f"H{r}"].value,
                        f"{a['date']}（讀取日）", a["src"], a["grade"], a["stance"], a["stance_note"], a["hand"],
                        f"—（{a['orig']} 的第二來源；不連結模型格）", note))
    return out + [q for q in Q_NEW if q["id"] not in rows]


# ================================================================== edits of existing records (guarded)
def _set(cell, old, new):
    """Replace an exact old value; already-new is a no-op."""
    if cell.value == new:
        return 0
    assert cell.value == old, (cell.parent.title, cell.coordinate, cell.value, old)
    cell.value = new
    return 1


def _keep(append_text, ws, r, col, label):
    """Revision 9: keep the original wording verbatim in the note column (W) before a mark／source column is rewritten."""
    return append_text(ws[f"W{r}"], f"{TAG} {col} 欄（{label}）＝『{ws[f'{col}{r}'].value}』")


# (SRC_ID, column, label, old, new) for mark／source rewrites (revision 9: the old value goes to W first)
RELABEL = [
    *[(f"SRC_HAR_{n:03d}", c, lab, old, new) for n in (3, 4, 5, 6, 8, 10, 11, 12) for c, lab, old, new in (
        ("L", "立場", "利害關係方", "中立"),
        ("M", "立場說明", "ARC Prize 自測為中立；99.9% 由 OpenAI 發布", "ARC Prize 官方自測（官方頁已讀 2026-10-20）"))],
    *[(f"SRC_DEM_00{n}", c, lab, old, new) for n in (4, 5) for c, lab, old, new in (
        ("J", "出處", "openai_token_revenue.json",
         "The Information〈Why OpenAI, Anthropic Missed Their Own Gross Margin Forecasts〉（約 2026-02-24，付費牆未讀，R4）；BigGo、Longbridge、Sacra 轉述同值（R3，同源）"),
        ("M", "立場說明", "OpenAI 投資人資料（經 The Information、FT）：有呈現成長的誘因", "OpenAI 投資人資料（經 The Information）：有呈現成長的誘因"))],
    ("SRC_PERF_040", "J", "出處", "arxiv 2510.11345；inclusionai.github.io/AReaL",
     "AReaL 論文 arXiv 2505.24298（up to 2.77x）；原出處 ROLL Flash（arxiv 2510.11345）未比較 AReaL（其自身為 2.12–2.13x）"),
    ("SRC_PERF_040", "M", "立場說明", "阿里淘天、螞蟻：框架作者自測", "Alibaba／上海交大／港科大：框架作者自測"),
    ("SRC_DEM_060", "G", "口徑", "時點 2026-07-14；序列 2026-02-05 1M → 03-05 2M → 04-21 4M → 05-31 5M → 07-14 8M",
     "Codex＋ChatGPT Work 合計；時點 2026-07-14；序列 2026-02-05 1M → 03-05 2M → 04-21 4M → 05-31 5M → 07-14 8M（序列各點口徑可能混用）"),
    ("SRC_MOD_015", "F", "單位", "%", "比例"),
    ("SRC_MOD_054", "F", "單位", "%", "比例"),
    ("SRC_DC_017", "F", "單位", "% 系統價/年", "比例（系統價/年）"),
    ("SRC_MOD_054", "B", "指標", "DeepSeek V4-Pro 全注意力層比例（壓縮比 4 層／（壓縮比 4＋128 層）＝30/61）",
     "DeepSeek V4-Pro c4a 壓縮注意力（CSA）層比例（壓縮比 4 層／（壓縮比 4＋128 層）＝30/61）"),
    ("SRC_MOD_046", "B", "指標", "Kimi 完全非同步 rollout 加速", "Turn-level Partial Rollout 加速下限"),
    ("SRC_HW_009", "B", "指標（廠商）", "Supermicro GB300 NVL72 機架功率", "HPE（NVIDIA 參考機架）GB300 NVL72 機架功率"),
    ("SRC_DC_013", "B", "指標", "GB300 NVL72 每 GPU 小時 TCO（SemiAnalysis）", "GB300 NVL72 每 GPU 小時 TCO"),
    ("SRC_DC_013", "J", "出處", "SemiAnalysis AI Cloud TCO（經 InferenceX 部落格）",
     "Data Gravity（Chris Zeoli，2026-08-31）｜https://www.datagravity.dev/p/how-much-does-an-nvidia-nvl72-cost"),
    ("SRC_DC_013", "M", "立場說明", "SemiAnalysis：販售 TCO 模型、平台受晶片商贊助；須第二來源", "Data Gravity 自行推算（頁面未提 SemiAnalysis）"),
]

NOTES = [  # (SRC_ID, appended note)
    ("SRC_DEM_005", f"｜{V} Q1：免費 3.9＋付費 4.5＝8.4 為報導直接值（The Information，付費牆未讀；轉述頁同值）"),
    ("SRC_DEM_006", f"｜{V} Q1：15 組查詢未找到（R6）；仍為利害關係方、無第二來源（留在 W1）"),
    *[(f"SRC_PRC_00{n}", f"｜{V} Q3：官方頁 2026-10-20 已改列 gpt-6.1-sol（快取輸入短上下文 0.10、長上下文 0.20 見 SRC_PRC_049／050；新鮮輸入與輸出值不變）；本筆為當時有效值，主值不改") for n in (6, 7, 8)],
    ("SRC_HW_046", f"｜{V} Q5：1.8 kW＝Max-Q；Max-P 2.3 kW。Spec_Rack!F33 只用於每 FLOP 能耗，公式不分 Max-Q／P（{EVD}B0/Q2Q5Q6.md）"),
    *[(f"SRC_PERF_0{n}", f"｜{V} Q10：本值為 I 欄日期當時的快照；2026-10-20 同一發布者現行頁數值已變（成本低 11–15%；吞吐的預設口徑改為 agentic-traces，差異極大），"
                          "同源不算第二來源；是否改用新快照另案判斷") for n in range(11, 18)],
    ("SRC_PERF_025", f"｜{V} Q12：疑抄自 v6.1（240,274，差 −0.02%），待核；v6.0 結果庫本環境讀不到"),
    ("SRC_MOD_034", f"｜{V} Q13：147K 含 SFT 資料產生 5K；純 RL 142K（R1-Zero 101K＋R1 41K）"),
    ("SRC_DEM_016", f"｜{V} Q13：基準 3.5 [Assumed]：論文為 3–4 倍，3.5 為中點"),
    ("SRC_DEM_071", f"｜{V} Q13：第二來源查證時 Sacra 頁只讀到約 15%（15–20% 這句未讀到，R6）"),
    ("SRC_DEM_055", f"｜{V} Q13：網址錯配：所引 Help 文章 11909943 實為「GPT-5 in ChatGPT」，該頁與 GPT-6 文章 20001354 皆未列上下文數字；數字應在 chatgpt.com/pricing，待核"),
]


def apply(wb, append_text):
    rows = _rows(wb); log = dict(a_r=0, a_s=0, c1=0, relabel=0, notes=0)
    for a in DATA["A"]:
        ws, r = rows[a["orig"]]
        assert a["id"] in rows, a["id"]
        log["a_r"] += _set(ws[f"R{r}"], DASH, a["id"])
        s = ws[f"S{r}"].value
        if ws[f"R{r}"].value == a["id"] and s != DATE:
            if s not in (None, "", DASH):
                append_text(ws[f"W{r}"], f"｜{V} W1 B1：審查日 {s} → {DATE}（第二來源 {a['id']}）")
            ws[f"S{r}"].value = DATE; log["a_s"] += 1
    for c in DATA["C1"]:
        ws, r = rows[c["id"]]
        log["c1"] += _set(ws[f"R{r}"], DASH, C1_TEXT)
    for sid, col, lab, old, new in RELABEL:
        ws, r = rows[sid]
        if ws[f"{col}{r}"].value == new:
            continue
        assert ws[f"{col}{r}"].value == old, (sid, col, ws[f"{col}{r}"].value)
        _keep(append_text, ws, r, col, lab)
        log["relabel"] += _set(ws[f"{col}{r}"], old, new)
    for sid, txt in NOTES:
        ws, r = rows[sid]
        log["notes"] += int(bool(append_text(ws[f"W{r}"], txt)))
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == "SL51-01" for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== Decisions SL51-*
def _decisions():
    D = [
        ("W1 第二來源 B1：標記與來源欄更正（修訂九）",
         "W1 第二來源 A 段查證（含 B0 複核）發現標記或來源欄有誤，依工作單第 3、4、10 項更正：SRC_HAR_003／004／005／006／008／010／011／012 立場改中立（ARC Prize 官方自測；SRC_HAR_007 的 99.9% 源自 OpenAI 自報，不改）；"
         "SRC_DEM_004／005 出處改為 The Information（付費牆未讀，R4）並刪除「FT」；SRC_PERF_040 出處與作者單位；SRC_DEM_060 口徑；SRC_MOD_015／054、SRC_DC_017 單位「%」改「比例」；SRC_MOD_054、SRC_MOD_046 指標名稱；SRC_HW_009 廠商；SRC_DC_013 出處改 Data Gravity、刪 SemiAnalysis 標示。"
         "原值逐字保留在各列 W 欄（「v17.2 更正」）。數值欄與任何模型格不變。",
         "SRC_Harness、SRC_Demand、SRC_Perf、SRC_Model、SRC_DC、SRC_HW 各列 B／F／G／J／L／M 欄與 W 欄"),
        ("W1 第二來源 B1：第二來源登錄與 C1 免除",
         "A 類 86 筆各新增一筆 Alt 第二來源紀錄（值照頁面原文、單位見 F 欄、等級依 stage2 規則且 WebFetch 讀取者最高 2），原紀錄 R 欄填新 SRC_ID、S 欄 2026-10-20；"
         "C1 類 53 筆（官方牌價／規格表）R 欄填「免」；Q3／Q4／Q6／Q7 另新增 6 筆 Alt（SRC_PRC_049／050、SRC_HW_096／097、SRC_DC_021／022），主值不改；"
         "SRC_DC_010 的 50–60 已在低／高欄；Q14 未寫入（見報告）。B 類 18 筆不填 R 欄。",
         "SRC_* 各頁 R／S 欄與新增列；Checks W1"),
    ]
    return [[f"SL51-{i:02d}", V, t, txt, DATE, DEC_BY, "v17.2 已建", where, f"{WO}；{EVD}", "否"] for i, (t, txt, where) in enumerate(D, 1)]


# ================================================================== README
README_VERSION = (VERSION + "（修補版：" + WO + "——W1 第二來源 B1 段：A 類 86 筆新增 Alt 第二來源紀錄並填原紀錄 R 欄、C1 類 53 筆 R 欄填「免」、ARC Prize 8 筆立場改中立；"
                  "Q1／Q3／Q4／Q5／Q6／Q7／Q8–Q13 的來源、標記與備註更正（原值保留於 W 欄）；新增 Alt SRC_PRC_049／050、SRC_HW_096／097、SRC_DC_021／022；Decisions SL51-01／02。"
                  "模型格數值、公式、藍字輸入不變）。以下為 " + v1710.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1710.README_TITLE
README_TITLE = V + _T[len(v1710.V):]
README_ROW = ("v17.2 W1 第二來源 B1",
              "治理寫入、模型數值不變：利害關係方紀錄配第二來源（新增 Alt 紀錄，原紀錄 R 欄填 SRC_ID）、官方牌價／規格表免除第二來源、ARC Prize 自測改標中立、"
              "若干來源與標記更正（原值保留於備註）。細節見工作單 docs/workorders/20261020_W1第二來源_B1.md 與 Decisions SL51-*。")

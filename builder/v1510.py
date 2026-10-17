# v15.1 (work order docs/workorders/20261017_v15.1_結案收尾.md r0, branch claude/v15-1): close-out clean-up after the v15.0 independent check
#   (docs/reports/20261017_v15.0_獨立查核.md, Part B).  MINOR version: text, labels, Decisions and one label formula only.  No named-range value changes.
#   U1-1  Decisions SL46-20 said "區間已涵蓋" for Alloc_In C15; the workbook's own closure (L1_TokPerPromptClose 38,186) and Checks M4 contradict it
#         -> correction appended (original wording kept, revision 9), Alloc_In G15 note, new Decision SL46-25.
#   U1-2  Alloc row (a) of the "未建區間" list: v15.0 replaced "12 個"/name list without keeping the original verbatim -> original text appended back (revision 9), SL46-26.
#   U1-3  Calib D67:G67: SL46-13 only covered Hopper -> new Decision SL46-27 (+ Calib J67, Interface A2 notes).
#   U1-4  Alloc_In C16: token-basis vs spend-basis free share stated (accepted as Assumed), SL46-28.
#   U2-1  O12 caliber label added to the 17 rows the independent check found untouched (Amortize 10/19/29/40, Interface 55/60/64/69/73/78/148, Theory_Rev 18/20/36/38/54/56); SL46-16 extended, SL46-29.
#   U2-2  O15 kept items: Spec_Rack G26, D41 and Har_In C48:E48 added to SL46-07 (new Decision SL46-30) together with the row-by-row mapping of the other kept items.
#   U2-4  Sens_Rev A17 (S1-GM566, Y9 scope): the hard-coded "ε＝0.5" label becomes a formula that follows CST_Eps (same method as Y9 on Sens_Rev A8／A9); SL46-31.
# Every write to an Excel-owned cell is guarded (old value / old text); appended texts keep the original wording (CLAUDE.md section 6, revision 9).
import json
import os

import v1410
import v1500

VERSION = "20261017_Tokenomics_v15.1"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-17"
V = "v15.1"
WO = "工作單 docs/workorders/20261017_v15.1_結案收尾.md（r0）"
DEC_BY = ("Andy 2026-10-17 13:04（『继续把稽核任務完成』）；13:39／13:52 對 O1–O22 的預設（本版只把已同意的預設正確落實，不新增判斷）；"
          "依據 docs/reports/20261017_v15.0_獨立查核.md Part B")
HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = json.load(open(os.path.join(HERE, "v1510_orig.json"), encoding="utf-8"))

O12_TAG = v1500.O12_TAG
O12_ROWS_V151 = {"Amortize": (10, 19, 29, 40), "Interface": (55, 60, 64, 69, 73, 78, 148), "Theory_Rev": (18, 20, 36, 38, 54, 56)}


def _row_of(ws, rid, col=1, first=5):
    rows = [r for r in range(first, ws.max_row + 1) if ws.cell(r, col).value == rid]
    assert len(rows) == 1, (ws.title, rid, rows)
    return rows[0]


# ================================================================== U1-1
U11_DEC = ("｜v15.1 更正（修訂九，Decisions SL46-25）：上文『區間已涵蓋』一句，對 Alloc_In C15（每則提示 token 數）不成立——"
           "閉合值 L1_TokPerPromptClose＝38,186（L1 第 84 列 D 欄；區間 11,121–89,220）高於 C15 區間上限 11,000，且 Checks M4（需求路線付費 token ÷ 機隊付費 token）＝0.200，觸發『兩路線不閉合』。"
           "更正後的說法：C15 區間未涵蓋閉合值；差距屬未解釋（沿用 D15 B 段 Decisions D15-12 與 L1_GapPrompt 列的說明）；C15 維持 Assumed、數值不改；每則提示 token 數列入外部搜尋。"
           "C14、C16、D24 與 C15 同屬需求路線：M4 的差距（約五倍）不是任何單一輸入的區間所能涵蓋，上文『區間已涵蓋』對它們只應讀作『輸入區間已給』，不表示兩路線閉合。")
U11_AI = ("｜v15.1 更正（修訂九，Decisions SL46-25）：C15 區間 2,000–11,000 未涵蓋閉合值 L1_TokPerPromptClose＝38,186（區間 11,121–89,220），Checks M4＝0.200 觸發；"
          "差距屬未解釋（Decisions D15-12）；Decisions SL46-20 所稱『區間已涵蓋』對本格更正如上；每則提示 token 數列入外部搜尋")


def u11(wb, append_text):
    d = wb["Decisions"]
    r = _row_of(d, "SL46-20")
    n = int(append_text(d[f"D{r}"], U11_DEC))
    n += int(append_text(wb["Alloc_In"]["G15"], U11_AI))
    return n


# ================================================================== U1-2
U12_TAIL = "｜v15.1 補回原文（修訂九，Decisions SL46-26；v15.0 更正時未逐字保留）：原文＝『" + ORIG["alloc_a_orig"] + "』"


def u12(wb, append_text):
    ws = wb["Alloc"]
    rows = [r for r in range(1, ws.max_row + 1) if str(ws.cell(r, 1).value or "").startswith("（a）只經 VR200 欄") and "v15.0 更正（修訂九，T3-2）" in str(ws.cell(r, 1).value)]
    assert len(rows) == 1, rows
    return int(append_text(ws[f"A{rows[0]}"], U12_TAIL))


# ================================================================== U1-3
U13_CALIB = ("；v15.1 O8（Decisions SL46-27）：D67（GB200）、F67（VR200）的倍數 1 是沿用 GB300，G67（RU）為 Assumed，E67（GB300）是被沿用的基準欄（倍數 1 與其校準點同為擬合，不是獨立驗證）；"
             "Gov_Map GM342–GM345 類別為 Analogy。對外引用這四欄的吞吐與營收，與 Hopper 一樣標『未獨立驗證』。DB_Evidence E245（MLPerf v6.1 VR200÷GB300，一手）已依 X6 處理，F67 不改；GB200、RU 尚無獨立依據。數值不改")
U13_IF = "；v15.1 O8：GB200、GB300、VR200、Rubin Ultra 欄的吞吐與營收亦屬『未獨立驗證』（Calib D67:G67 倍數沿用 1；Decisions SL46-27）；數值不改"
U13_DEC13 = "｜v15.1：Calib D67:G67（GB200–RU）見 Decisions SL46-27"


def u13(wb, append_text):
    n = int(append_text(wb["Calib"]["J67"], U13_CALIB))
    n += int(append_text(wb["Interface"]["A2"], U13_IF))
    d = wb["Decisions"]
    n += int(append_text(d[f"D{_row_of(d, 'SL46-13')}"], U13_DEC13))
    return n


# ================================================================== U1-4
U14_AI = ("；v15.1 口徑說明（Decisions SL46-28；原 O19／SL46-20）：本格是 token 口徑（ChatGPT 免費用戶占 ChatGPT token 的比例），具名範圍 AL_FreeShare，進 m 計算；"
          "機隊切分的免費占比 B4_Free（Cap_In C29，0.46）是 2025 年 OpenAI 推論支出口徑（$3.9B ÷ $8.4B），外部對照 SRC_DEM_005 ÷ SRC_DEM_004 亦為支出口徑；"
          "同一套 m 計算混用兩種口徑，尚未對齊。本格接受為 Assumed（區間 0.4–0.8 是輸入區間，不表示兩口徑已對齊）；數值不改")


def u14(wb, append_text):
    return int(append_text(wb["Alloc_In"]["G16"], U14_AI))


# ================================================================== U2-1
U21_DEC16 = ("｜v15.1 補列（Decisions SL46-29）：口徑標籤補到 Amortize 第 10、19、29、40 列；Interface 第 55、60、64、69、73、78、148 列；Theory_Rev 第 18、20、36、38、54、56 列，共 17 列"
             "（v15.0 的 SL46-16 只列了其他 21 列與 12 格；這 17 列的內容與 v14.2 相同，經 v15.0 獨立查核指出）")


def u21(wb, append_text):
    n = 0
    for sh, rows in O12_ROWS_V151.items():
        ws = wb[sh]
        for r in rows:
            assert ws[f"A{r}"].value not in (None, ""), (sh, r)
            n += int(append_text(ws[f"A{r}"], O12_TAG))
            mp = sh + "_Prod"          # 鏡像頁的標籤是核心頁標籤的文字複本，須同步（test_slim 鏡像檢查）
            if mp in wb.sheetnames:
                n += int(append_text(wb[mp][f"A{r}"], O12_TAG))
    d = wb["Decisions"]
    n += int(append_text(d[f"D{_row_of(d, 'SL46-16')}"], U21_DEC16))
    return n


# ================================================================== U2-2
U22_DEC07 = "｜v15.1 補列：Spec_Rack G26、D41；Har_In C48:E48 及其餘小項的逐列對應，見 Decisions SL46-30"


def u22(wb, append_text):
    d = wb["Decisions"]
    return int(append_text(d[f"D{_row_of(d, 'SL46-07')}"], U22_DEC07))


# ================================================================== U2-4 (Y9 scope): Sens_Rev A17 label follows CST_Eps
A17_OLD = "ε＝0.5、有效算力 ×7（J8 缺口全數轉為能力）"
A17_NEW = '="ε＝"&TEXT(CST_Eps,"0.0#")&"、有效算力 ×"&B17&"（J8 缺口全數轉為能力）"'
G18_TAIL = "；v15.1（Decisions SL46-31）：上一列 A17 的標籤已改為公式，ε 隨本格（B18＝具名範圍 CST_Eps）更新，上句『上一列標籤文字的「ε＝0.5」不隨本格更新』至此不再成立（D17 一直讀 CST_Eps）"


def u24(wb, append_text):
    ws = wb["Sens_Rev"]
    assert ws["A18"].value.startswith("ε（上一列量級情境的指數"), ws["A18"].value
    cur = ws["A17"].value
    n = 0
    if cur != A17_NEW:
        assert cur == A17_OLD, cur
        ws["A17"].value = A17_NEW
        n += 1
    n += int(append_text(ws["G18"], G18_TAIL))
    return n


# ================================================================== Decisions SL46-25..31
def _decisions():
    A = DEC_BY
    B = "Andy 2026-10-17 13:04 起『继续把稽核任務完成』；13:39 對 O1–O22 照預設"
    D = [
        ("U1-1 更正 SL46-20 對 Alloc_In C15 的『區間已涵蓋』（修訂九）",
         f"依據：{A}。原文逐字保留於 SL46-20 的 D 欄，更正附在其後：C15 區間 2,000–11,000 未涵蓋閉合值 L1_TokPerPromptClose＝38,186（區間 11,121–89,220），Checks M4＝0.200 觸發『兩路線不閉合』；"
         "差距屬未解釋（沿用 Decisions D15-12 與 L1_GapPrompt 列說明）；C15 維持 Assumed；每則提示 token 數列入外部搜尋。更正理由：原文與活頁簿自己的閉合解與檢查矛盾（v15.0 獨立查核 2.2）。數值不改。",
         "Decisions SL46-20 D 欄；Alloc_In C15（G15）", "Alloc_In C15（G15）；Decisions SL46-20"),
        ("U1-2 Alloc 第 398 列（a）段原文逐字補回（修訂九）",
         f"依據：{A}。v15.0 為更正 T3-2（O4）而改寫 Alloc『未建區間』清單（a）段，把原句『12 個』改為『0 個』、12 個名稱清單改為『（無）』，原句沒有逐字保留，違反 CLAUDE.md 第 6 節修訂九。"
         "v15.1 把 v14.2 的原文逐字補在同一格（A 欄）之後；更正內容與數值不變。",
         "Alloc 第 398 列（A398）", "Alloc 第 398 列"),
        ("U1-3 Calib D67:G67 η_d 倍數的沿用與對外標示",
         f"依據：{A}。SL46-13 只涵蓋 Hopper（C67）。補：D67（GB200）、F67（VR200）的倍數 1 沿用 GB300，G67（RU）為 Assumed，E67（GB300）為被沿用的基準欄；Gov_Map GM342–GM345 類別為 Analogy（來源 SRC_PERF_009），本決策不改類別。"
         "對外引用這四欄的吞吐與營收，與 Hopper 一樣標『未獨立驗證』。F67 與 DB_Evidence E245（MLPerf v6.1 VR200÷GB300，一手）的對照已依 X6 處理，不改；GB200、RU 尚無獨立依據，列外部搜尋待辦。數值不改。標註於 Calib J67、Interface A2。",
         "Calib D67:G67（J67）；Interface A2", "Calib D67:G67；Interface A2"),
        ("U1-4 Alloc_In C16 token 口徑與支出口徑混用的說明",
         f"依據：{A}。Alloc_In C16（ChatGPT token 中免費用戶占比，AL_FreeShare）是 token 口徑；Cap_In C29（B4_Free，0.46）與外部對照 SRC_DEM_005 ÷ SRC_DEM_004 是 2025 年 OpenAI 推論支出口徑；同一套 m 計算混用，尚未對齊。"
         "接受為 Assumed（區間 0.4–0.8），口徑寫在 Alloc_In G16；不表示兩口徑已對齊。數值不改。",
         "Alloc_In C16（G16）", "Alloc_In C16（G16）"),
        ("U2-1 O12 口徑標籤補列 17 列",
         f"依據：{A}。v15.0 的 SL46-16 沒有列到的 17 列補上口徑標籤（與 SL46-16 其他列同一段文字）：Amortize 第 10、19、29、40 列；Interface 第 55、60、64、69、73、78、148 列；Theory_Rev 第 18、20、36、38、54、56 列。公式與數值不改。",
         "Amortize 第 10、19、29、40 列；Interface 第 55、60、64、69、73、78、148 列；Theory_Rev 第 18、20、36、38、54、56 列", "A 欄標籤"),
        ("U2-2 O15 刻意保留補列（Spec_Rack G26、D41；Har_In C48:E48）與其餘小項逐列對應",
         f"依據：{A}（O15 其餘小項記為刻意保留，SL46-07）。補列三組並寫明理由，不改值——"
         "(1) Spec_Rack G26（RU 欄 HBM 頻寬 32 TB/s/GPU，Gov_Map GM119）：RU 欄沿用舊路線圖總頻寬 ÷ 144，與單架 72 封裝定義是否同口徑未確認；網路查證只找到二手規格整理（SRC_HW_044）。維持現值（沒有一手來源可改）；依賴圖計下游契約名稱 352 個，對外引用 RU 欄請標『規格口徑未確認』。"
         "(2) Spec_Rack D41（NVFP4 訓練 dense PF/GPU，Gov_Map GM171）：只在 Tech_Registry T07 情境才使用，區間對應哪一欄不清楚；基準路徑無讀取（依賴圖計下游契約名稱 0 個）。維持現值。"
         "(3) Har_In C48:E48（50% 時間範圍基準 1.5／8／16 小時，Gov_Map GM499，Analogy，SRC_CAP_020）：DB_Evidence E018 指出 GPT-6 各層級未有 METR 實測，Sol 8 小時低於 GPT-5.6 Sol 實測 11.3 小時；時間範圍倍數無法換算（B22）。"
         "維持現值（沒有 GPT-6 實測可換）；依賴圖計下游契約名稱 47 個（IF_TaskSucc_*、IF_CostSucc*、IF_FrontSucc* 等），對外引用任務成功率請標『時間範圍為 Analogy 基準』。"
         "其餘小項逐列對應（SL46-07 原文只列發現編號，這裡補上對應的列，決定不變，皆為刻意保留）：G10 → Cache_Store 第 16、22、28 列；G12 → Perf 第 117 列、Interface 第 27、37、47 列；"
         "G16 → Workload 第 13、21、26、27、28、29、30、35 列、Interface 第 156、157、158、159、160 列；G18 → Price_Frontier 第 24、26、31、33 列；G19 → Interface 第 224 列；G21 → Calib 第 112、113 列；"
         "G22 → Tech_Registry 第 25、26、27、28 列；G23 → Spec_Rack 第 33 列；B13 → Cap_In 第 228、232、233、234 列、L1 第 86、87、88 列；B14 → Train_In 第 13 列、L1 第 34 列；"
         "B19 → Cap_In 第 106、107、263 列；B22 → Har_In 第 19、31、48 列。Harness 第 126、129、132 列的『刻意保留』見 SL46-03。",
         "Spec_Rack G26、D41；Har_In C48:E48（及上列逐列對應）", "（全簿；逐列對應見決議）"),
        ("U2-4 Sens_Rev A17 標籤隨 CST_Eps（Y9）",
         f"依據：{A}。Sens_Rev A17『ε＝0.5、有效算力 ×7（J8 缺口全數轉為能力）』寫死 ε（S1-GM566），屬 Y9『敏感度頁未跟隨輸入』範圍。照 Y9 對 Sens_Rev A8／A9 的做法，標籤改為公式："
         f"=\"ε＝\"&TEXT(CST_Eps,\"0.0#\")&\"、有效算力 ×\"&B17&\"（J8 缺口全數轉為能力）\"；基準值下顯示文字與原文完全相同。CST_Eps 即 Sens_Rev B18，D17 本來就讀它，數值不改。原文逐字保留於本筆：『{A17_OLD}』。",
         "Sens_Rev A17、B17；G18", "Sens_Rev A17；G18"),
    ]
    return [[f"SL46-{25 + i:02d}", V, f"v15.1 稽核結案收尾：{t}", txt, DATE, B, "v15.1 已建", where, f"{WO} {t[:4]}", "否"] for i, (t, txt, where, _) in enumerate(D)]


def apply(wb, append_text):
    log = {}
    log["u11"] = u11(wb, append_text)
    log["u12"] = u12(wb, append_text)
    log["u13"] = u13(wb, append_text)
    log["u14"] = u14(wb, append_text)
    log["u21"] = u21(wb, append_text)
    log["u22"] = u22(wb, append_text)
    log["u24"] = u24(wb, append_text)
    ws = wb["Decisions"]
    if not any(ws.cell(r, 1).value == "SL46-25" for r in range(5, ws.max_row + 1)):
        log["decisions"] = v1410.decisions_append(wb, _decisions())
    return log


# ================================================================== README
README_VERSION = (VERSION + "（次版：" + WO + "——依 v15.0 獨立查核補正文字：SL46-20 對 Alloc_In C15『區間已涵蓋』更正（閉合值 38,186 在區間外，Checks M4 觸發）；Alloc 第 398 列原文逐字補回；Calib D67:G67 沿用與對外標示；"
                  "Alloc_In C16 口徑說明；O12 口徑標籤補 17 列；O15 刻意保留補列（Spec_Rack G26、D41；Har_In C48:E48）與逐列對應；Sens_Rev A17 標籤改公式；Decisions SL46-25…31。基準數值與具名範圍不變）。以下為 "
                  + v1500.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1500.README_TITLE
README_TITLE = V + _T[len(v1500.V):]
README_ROW = ("v15.1 稽核結案收尾",
              "依 v15.0 獨立查核補正：Decisions 更正（修訂九，原字樣保留）、標籤口徑補列、Sens_Rev A17 標籤改公式。只動文字、標籤、Decisions；所有具名範圍的數值不變。細節見 Decisions SL46-25…31。")

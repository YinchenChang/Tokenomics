# 用法：python3 tools/build_closure_study.py <輸出.xlsx> docs/reports/20261015_v5.36A_查證.xlsx，再以 LibreOffice 重算。研究用活頁簿，不屬 Tokenomics 主檔。
# 產生「token 分母閉合」研究活頁簿（全部計算以 Excel 公式寫入；數值輸入集中在「輸入」頁）
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.comments import Comment

OUT = sys.argv[1]
AEVID = sys.argv[2]          # v5.36A 查證 xlsx（證據頁來源）

F = "Arial"
f_title = Font(name=F, size=14, bold=True)
f_h = Font(name=F, size=10, bold=True, color="FFFFFF")
f_sec = Font(name=F, size=11, bold=True, color="1F3864")
f_txt = Font(name=F, size=10)
f_in = Font(name=F, size=10, color="0000FF")
f_link = Font(name=F, size=10, color="008000")
f_calc = Font(name=F, size=10, color="000000")
f_key = Font(name=F, size=10, bold=True)
fill_h = PatternFill("solid", fgColor="1F3864")
fill_sec = PatternFill("solid", fgColor="DDEBF7")
fill_y = PatternFill("solid", fgColor="FFFF00")
fill_key = PatternFill("solid", fgColor="E2EFDA")
wrap = Alignment(wrap_text=True, vertical="top")
thin = Side(style="thin", color="BFBFBF")
box = Border(top=thin, bottom=thin, left=thin, right=thin)

wb = openpyxl.Workbook()
wb.remove(wb.active)

def sheet(name, widths):
    ws = wb.create_sheet(name)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[CL(i)].width = w
    ws.sheet_view.showGridLines = False
    return ws

def put(ws, r, c, v, font=f_txt, fmt=None, fill=None, al=wrap, border=True):
    cell = ws.cell(r, c, v)
    cell.font = font
    if fmt: cell.number_format = fmt
    if fill: cell.fill = fill
    if al: cell.alignment = al
    if border: cell.border = box
    return cell

def header(ws, r, labels):
    for i, t in enumerate(labels, 1):
        put(ws, r, i, t, f_h, fill=fill_h)

def section(ws, r, text, ncol):
    for c in range(1, ncol + 1):
        put(ws, r, c, text if c == 1 else None, f_sec, fill=fill_sec)

SC = ["D", "E", "F", "G", "H"]          # 五個情境欄
SC_NAME = ["模型現值（v5.35）", "A 段證據：計價倍數 1.5", "A 段證據＋推論支出 84 億", "閉合例：支出 84 億＋κ 0.75", "自訂（黃底輸入格可改）"]

# ───────────────────────── 輸入 ─────────────────────────
wi = sheet("輸入", [9, 40, 12, 14, 14, 14, 14, 14, 11, 11, 22, 70])
put(wi, 1, 1, "輸入：本活頁簿唯一的數值來源（藍字＝輸入；H 欄黃底＝你可以改的自訂情境）", f_title, border=False, al=None)
put(wi, 2, 1, "D–G 欄是四個固定情境（只有少數輸入不同）；H 欄預設等於模型現值，改它即可看全部頁面的 H 欄如何變化。I／J 欄是證據或模型的合理區間，供「敏感度」頁使用。", f_txt, border=False)
wi.merge_cells("A2:L2"); wi.row_dimensions[2].height = 30
header(wi, 4, ["代號", "項目", "單位"] + SC_NAME + ["區間低", "區間高", "標記", "來源與說明"])
wi.row_dimensions[4].height = 42

INPUTS = [
    # key, label, unit, [D,E,F,G], lo, hi, tag, source, fmt
    ("sec", "A. 營收與單價"),
    ("R", "OpenAI 2025 營收（毛額）", "$B", [13.07]*4, None, None, "Interested-party", "SRC_DEM_007（OpenAI 外流財報；有吹高營收的誘因）", "0.00"),
    ("mixL", "付費層級組合：Luna（低階）", "%", [0.40]*4, None, None, "Assumed", "B4_MixPaid（Tokenomics v5.35）", "0%"),
    ("mixS", "付費層級組合：Sol（中階）", "%", [0.45]*4, None, None, "Assumed", "B4_MixPaid", "0%"),
    ("mixA", "付費層級組合：Astra（高階）", "%", [0.15]*4, None, None, "Assumed", "B4_MixPaid", "0%"),
    ("pL", "參考請求有效單價：Luna", "$/M", [0.0803555555555556]*4, None, None, "Derived", "IF_PriceRef_Luna＝GPT-6 牌價快照（16K 入／2K 出、快取命中 0.55）× (1 − 折讓 0.2)", "0.0000"),
    ("pS", "參考請求有效單價：Sol", "$/M", [1.60711111111111]*4, None, None, "Derived", "IF_PriceRef_Sol（同上）", "0.0000"),
    ("pA", "參考請求有效單價：Astra", "$/M", [8.03555555555555]*4, None, None, "Derived", "IF_PriceRef_Astra（同上）", "0.0000"),
    ("sec", "B. 需求端（token 從使用量算）"),
    ("tpm", "API token 量（2025-10 時點）", "B tok/分鐘", [6]*4, None, None, "Interested-party", "SRC_DEM_010（OpenAI DevDay 2025；有誇大用量的誘因）", "0.0"),
    ("apir", "API 全年平均 ÷ 10 月時點值", "x", [0.75]*4, 0.6, 0.9, "Assumed", "Alloc_In C14；區間為本活頁簿設定（A 段同向極端角點用 0.6／0.9）", "0.00"),
    ("ppd", "ChatGPT 每日訊息數", "B 則/日", [2.5]*4, 2.2, 2.7, "Interested-party", "SRC_DEM_012（OpenAI 2025-07）；區間＝v5.33A 內插 2.2–2.7", "0.00"),
    ("tau", "每則訊息 token 數 τ（輸入＋上下文＋推理＋輸出）", "tok", [4000]*4, 2000, 11000, "Assumed", "Alloc_In C15；v5.33A 五組成法證據中心 4,300（1,650–11,300），Analogy／Assumed；OpenAI 未揭露", "#,##0"),
    ("fs", "ChatGPT token 中免費用戶占比", "%", [0.6]*4, 0.4, 0.8, "Assumed", "Alloc_In C16；付費占比無揭露（v5.33A 1.2）", "0%"),
    ("sec", "C. 機隊產能與成本（每 GW；2025 服務機隊）"),
    ("mixH", "服務世代組合：Hopper", "%", [0.6]*4, None, None, "Assumed", "Alloc_In C9", "0%"),
    ("mixG", "服務世代組合：GB200", "%", [0.4]*4, None, None, "Assumed", "Alloc_In C10（兩者合計須為 100%）", "0%"),
    ("cPH", "付費組合每 GW 年產能 @100% 利用率：Hopper", "M tok/GW/年", [9225862913.20409/0.6]*4, None, None, "Derived", "Tokenomics Alloc!C22 ÷ IF_Util 0.6（由 Perf 頁 roofline 推導）", "#,##0"),
    ("cPG", "付費組合每 GW 年產能 @100%：GB200", "M tok/GW/年", [46475270191.3169/0.6]*4, None, None, "Derived", "Alloc!D22 ÷ 0.6", "#,##0"),
    ("cFH", "免費組合每 GW 年產能 @100%：Hopper", "M tok/GW/年", [35705033654.1941/0.6]*4, None, None, "Derived", "Alloc!C23 ÷ 0.6（免費組合 Luna 0.9／Sol 0.1，較便宜所以產能高）", "#,##0"),
    ("cFG", "免費組合每 GW 年產能 @100%：GB200", "M tok/GW/年", [174192642344.907/0.6]*4, None, None, "Derived", "Alloc!D23 ÷ 0.6", "#,##0"),
    ("hH", "每 GW 年經濟持有成本：Hopper", "$B/GW/年", [9.70308728611469]*4, None, None, "Derived", "L1_HoldEconGW_Hopper（資本回收 WACC 10%＋營運費用）", "0.000"),
    ("hG", "每 GW 年經濟持有成本：GB200", "$B/GW/年", [8.82816556596761]*4, None, None, "Derived", "L1_HoldEconGW_GB200", "0.000"),
    ("sec", "D. 機隊端（token 從推論支出反推）"),
    ("spend", "OpenAI 2025 推論支出", "$B", [12.6, 12.6, 8.4, 8.4], 8.4, 13.0, "Interested-party", "12.6＝SRC_DEM_018（Microsoft 外流 Azure 帳單推估；Microsoft 稱不準確，可能含抵用金）；8.4＝SRC_DEM_004（與營收 13.07、免費推論 3.9 同一組 OpenAI 數字；與「計算毛利約 70%」吻合）", "0.00"),
    ("SB", "計價倍數：推論支出 ÷ 持有成本", "x", [2.0, 1.5, 1.5, 2.0], 1.2, 3.0, "Assumed", "Alloc_In C23（模型 2.0，1.5–3.0）；A 段證據中心 1.5（1.2–2.0）：Oracle 出租 GPU 毛利約 14%、CoreWeave 營業利益率約 5%、H100 市場價約持有成本 1.3–1.5 倍（皆二手）", "0.00"),
    ("U", "模型基準利用率 IF_Util", "%", [0.6]*4, None, None, "Assumed", "Serving!C17；產能列已乘上它", "0%"),
    ("Ua", "實際利用率 × 生產折減", "%", [0.35]*4, 0.30, 0.50, "Assumed", "Alloc_In C24（模型 0.30–0.40）；無實測（A3 已搜尋未找到）；高端 0.50 為本活頁簿放寬", "0%"),
    ("kap", "請求形狀修正 κ（實際流量每 GPU 秒總 token ÷ 參考請求）", "x", [1.0, 1.0, 1.0, 0.75], 0.65, 1.2, "Derived", "v5.36A 3.2：以 Sens_Perf 第 93–94 列校準 prefill／decode 成本，代入實際輸入輸出比與快取；Analogy 輸入。模型現值未建此項（等於 1）", "0.00"),
    ("fsRep", "對照：免費推論支出占比（支出口徑）", "%", [0.46]*4, None, None, "Interested-party", "IF_FreeShare＝SRC_DEM_005 3.9 ÷ SRC_DEM_004 8.4", "0%"),
    ("sec", "E. 回本"),
    ("Bk", "回本乘積（VR200）：持有成本 ÷ 100% 利用率營收", "x", [0.150548548387624]*4, None, None, "Derived", "L1_FleetBreakeven＝IF_HoldEcon 122.3 億 ÷ (IF_RevGWFleet 487 億 ÷ 0.6)", "0.0000"),
    ("dl", "生產折減 δ", "%", [0.85]*4, None, None, "Assumed", "CTL_ProdDerate", "0%"),
    ("L", "壽命期價格係數 L（基準）", "x", [0.642602366208498]*4, 0.342, 1.162, "Assumed", "L1_LTotal（牌價每年 −10%、前 4 年中階後降級、保留一半價值）", "0.000"),
]
ROW = {}
r = 5
for item in INPUTS:
    if item[0] == "sec":
        section(wi, r, item[1], 12); r += 1; continue
    key, label, unit, vals, lo, hi, tag, src, fmt = item
    ROW[key] = r
    put(wi, r, 1, key, f_txt); put(wi, r, 2, label); put(wi, r, 3, unit)
    for j, v in enumerate(vals):
        put(wi, r, 4 + j, v, f_in, fmt)
    put(wi, r, 8, vals[0], f_in, fmt, fill_y)
    put(wi, r, 9, lo, f_in, fmt); put(wi, r, 10, hi, f_in, fmt)
    put(wi, r, 11, tag); put(wi, r, 12, src)
    r += 1
put(wi, r + 1, 1, "情境差異：E 欄只把計價倍數改 1.5；F 欄再把推論支出改 84 億；G 欄（閉合例）支出 84 億、計價倍數維持 2.0、κ 0.75。其他輸入四欄相同。", f_txt, border=False)
wi.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=12)
wi.row_dimensions[r + 1].height = 30
wi.freeze_panes = "D5"

def I(key, col):            # 引用輸入頁
    return f"輸入!${col}${ROW[key]}"

# ───────────────────────── 推導鏈 ─────────────────────────
wd = sheet("推導鏈", [7, 44, 13, 15, 15, 15, 15, 15, 66])
put(wd, 1, 1, "推導鏈：需求端與機隊端各算一次「付費 token」，再看兩者為何對不上", f_title, border=False, al=None)
put(wd, 2, 1, "每列一個步驟；I 欄用文字寫出公式。綠字＝引用「輸入」頁，黑字＝本頁計算。五欄情境同一公式。", f_txt, border=False)
wd.merge_cells("A2:I2")
header(wd, 4, ["步驟", "項目", "單位"] + SC_NAME + ["公式（文字）"])
wd.row_dimensions[4].height = 42
D = {}                        # 推導鏈列號
rr = [5]

def dsec(text):
    section(wd, rr[0], text, 9); rr[0] += 1

def drow(key, step, label, unit, ftemp, words, fmt, key_row=False):
    r = rr[0]; D[key] = r
    put(wd, r, 1, step); put(wd, r, 2, label, f_key if key_row else f_txt); put(wd, r, 3, unit)
    for c in SC:
        fml = ftemp(c)
        is_link = fml.startswith("=輸入!") and all(ch not in fml[1:] for ch in "+-*/(")
        put(wd, r, SC.index(c) + 4, fml, f_link if is_link else f_calc, fmt, fill_key if key_row else None)
    put(wd, r, 9, words)
    rr[0] += 1

def dc(key, c):               # 引用推導鏈本頁
    return f"{c}{D[key]}"

dsec("A. 單價")
drow("Pbar", "A1", "付費 token 混合有效單價 P̄", "$/M",
     lambda c: f"={I('mixL',c)}*{I('pL',c)}+{I('mixS',c)}*{I('pS',c)}+{I('mixA',c)}*{I('pA',c)}",
     "P̄＝Σ 層級組合 × 該層級參考請求有效單價（Tokenomics Cap_In 第 90 列）", "0.0000")
dsec("B. 需求端：付費 token 從使用量算")
drow("API", "B1", "API token（全年）", "M tok/年",
     lambda c: f"={I('tpm',c)}*1E9*525600*{I('apir',c)}/1E6", "每分鐘 token × 1e9 × 525,600 分鐘 × 全年平均比例 ÷ 1e6（Alloc 第 5 列）", "#,##0")
drow("Chat", "B2", "ChatGPT token（全年）", "M tok/年",
     lambda c: f"={I('ppd',c)}*1E9*{I('tau',c)}*365/1E6", "每日訊息 × 1e9 × 每則 token τ × 365 ÷ 1e6（Alloc 第 6 列）", "#,##0")
drow("Df", "B3", "免費 token D_free", "M tok/年", lambda c: f"={dc('Chat',c)}*{I('fs',c)}", "B2 × 免費占比", "#,##0")
drow("Dp", "B4", "付費 token D_paid（需求端）", "M tok/年", lambda c: f"={dc('API',c)}+{dc('Chat',c)}*(1-{I('fs',c)})", "API ＋ ChatGPT ×（1 − 免費占比）（Alloc 第 9 列）", "#,##0", True)
drow("r", "B5", "免費 ÷ 付費 token 比 r", "x", lambda c: f"={dc('Df',c)}/{dc('Dp',c)}", "B3 ÷ B4；機隊端沿用同一個 r 分配免費與付費（Cap_In 第 112 列）", "0.000")
drow("mD", "B6", "m_整體（需求端）", "x", lambda c: f"={I('R',c)}*1E9/({dc('Dp',c)}*{dc('Pbar',c)})", "營收 ÷（需求端付費 token × P̄）→ L1_MImplied", "0.000", True)
drow("pD", "B7", "實收單價（需求端）", "$/M", lambda c: f"={I('R',c)}*1E9/{dc('Dp',c)}", "營收 ÷ 需求端付費 token ＝ m_整體 × P̄", "0.00")
dsec("C. 每 GW 產能與 token 路線服務 GW")
drow("capP", "C1", "付費每 GW 年產能（世代組合，含基準利用率）", "M tok/GW/年",
     lambda c: f"={I('U',c)}*({I('mixH',c)}*{I('cPH',c)}+{I('mixG',c)}*{I('cPG',c)})", "IF_Util × Σ 世代占比 × 世代產能@100%（Alloc 第 24 列）", "#,##0")
drow("capF", "C2", "免費每 GW 年產能（世代組合，含基準利用率）", "M tok/GW/年",
     lambda c: f"={I('U',c)}*({I('mixH',c)}*{I('cFH',c)}+{I('mixG',c)}*{I('cFG',c)})", "同上，免費層級組合（Alloc 第 25 列）", "#,##0")
drow("hold", "C3", "世代組合後每 GW 年持有成本", "$B/GW/年", lambda c: f"={I('mixH',c)}*{I('hH',c)}+{I('mixG',c)}*{I('hG',c)}", "Σ 世代占比 × 持有成本（Alloc 第 61 列分母）", "0.000")
drow("GWt", "C4", "token 路線服務 GW（需求端需要多少 GW）", "GW", lambda c: f"={dc('Dp',c)}/{dc('capP',c)}+{dc('Df',c)}/{dc('capF',c)}", "付費 D ÷ 付費產能 ＋ 免費 D ÷ 免費產能（Alloc 第 28 列）", "0.0000")
dsec("D. 機隊端：付費 token 從推論支出反推")
drow("GWs", "D1", "支出路線服務 GW（帳面）", "GW", lambda c: f"={I('spend',c)}/{dc('hold',c)}", "推論支出 ÷ 每 GW 持有成本（Alloc 第 61 列）", "0.0000")
drow("GWc", "D2", "扣除計價倍數後的 GW", "GW", lambda c: f"={dc('GWs',c)}/{I('SB',c)}", "D1 ÷ 計價倍數（支出含雲端利潤與資本回收，不全是算力）", "0.0000")
drow("uf", "D3", "利用率修正", "x", lambda c: f"={I('Ua',c)}/{I('U',c)}", "實際利用率 ÷ IF_Util（產能列已含 IF_Util，故換成實際值）", "0.000")
drow("GWe", "D4", "有效服務 GW", "GW", lambda c: f"={dc('GWc',c)}*{dc('uf',c)}*{I('kap',c)}", "D2 × D3 × κ（Cap_In 第 177 列；κ 為 A 段新增）", "0.0000")
drow("Tf", "D5", "付費 token T_fleet（機隊端）", "M tok/年", lambda c: f"={dc('GWe',c)}/(1/{dc('capP',c)}+{dc('r',c)}/{dc('capF',c)})", "有效 GW ÷（1 ÷ 付費產能 ＋ r ÷ 免費產能）：每 1 個付費 token 連帶 r 個免費 token 一起占 GW（Cap_In 第 116 列）", "#,##0", True)
drow("mF", "D6", "m_fleet（機隊端）", "x", lambda c: f"={I('R',c)}*1E9/({dc('Tf',c)}*{dc('Pbar',c)})", "營收 ÷（機隊端付費 token × P̄）→ L1_MFleet", "0.000", True)
drow("pF", "D7", "實收單價（機隊端）", "$/M", lambda c: f"={I('R',c)}*1E9/{dc('Tf',c)}", "營收 ÷ 機隊端付費 token ＝ m_fleet × P̄", "0.00")
dsec("E. 閉合：兩端是否一致")
drow("cr", "E1", "閉合比：需求 ÷ 機隊", "x", lambda c: f"={dc('Dp',c)}/{dc('Tf',c)}", "B4 ÷ D5（Cap_In 第 174 列；1＝閉合；Checks M4 在 <0.5 或 >2 時警告）", "0.000", True)
drow("gap", "E2", "缺口：機隊 ÷ 需求（＝m_整體 ÷ m_fleet）", "x", lambda c: f"={dc('Tf',c)}/{dc('Dp',c)}", "D5 ÷ B4；同一營收、同一 P̄，所以兩個 m 的比值只剩 token 比", "0.000", True)
drow("SS", "E3", "服務端規模係數（ScaleServe）", "x", lambda c: f"={dc('GWs',c)}/{dc('GWt',c)}", "D1 ÷ C4（L1_ScaleServe）", "0.000")
drow("gapId", "E4", "恆等式驗算：ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））", "x",
     lambda c: f"={dc('SS',c)}/({I('SB',c)}*{I('U',c)}/({I('Ua',c)}*{I('kap',c)}))", "應等於 E2（見「代數推導」第 4 步）", "0.000")
drow("chk", "E5", "驗算差", "x", lambda c: f"={dc('gapId',c)}-{dc('gap',c)}", "應為 0", "0.0E+00")
drow("Tc", "E6", "閉合所需 ChatGPT 年 token T_chat*", "M tok/年",
     lambda c: f"=({dc('GWe',c)}-{dc('API',c)}/{dc('capP',c)})/((1-{I('fs',c)})/{dc('capP',c)}+{I('fs',c)}/{dc('capF',c)})",
     "令需求端用滿有效 GW：[有效 GW − API ÷ 付費產能] ÷ [(1−免費占比) ÷ 付費產能 ＋ 免費占比 ÷ 免費產能]（Cap_In 第 178 列）", "#,##0")
drow("tauS", "E7", "閉合所需每則 token τ*", "tok", lambda c: f"={dc('Tc',c)}*1E6/({I('ppd',c)}*1E9*365)", "T_chat* ÷（每日訊息 × 365）→ L1_TokPerPromptClose", "#,##0", True)
drow("tauJ", "E8", "τ* 是否在證據區間（1,650–11,300）", "", lambda c: f'=IF({dc("tauS",c)}>11300,"高於證據區間",IF({dc("tauS",c)}<1650,"低於證據區間","在證據區間內"))', "v5.33A 五組成法區間", None)
drow("fsC", "E9", "閉合下的免費算力占比", "%", lambda c: f"=({dc('Tc',c)}*{I('fs',c)}/{dc('capF',c)})/{dc('GWe',c)}", "以 T_chat* 重算免費 GW ÷ 有效 GW；對照支出口徑 0.46（Cap_In 第 181 列）", "0.0%")
drow("fsR", "E10", "對照：免費推論支出占比（支出口徑）", "%", lambda c: f"={I('fsRep',c)}", "IF_FreeShare；與 E9 不一致是第二個不閉合（v5.34 檢核 C6）", "0.0%")
dsec("F. 回本（L × m ≥ 門檻；以實收單價表示）")
drow("thr", "F1", "回本門檻 L × m（線性口徑）", "x", lambda c: f"={I('Bk',c)}/({I('U',c)}*{I('dl',c)})", "回本乘積 ÷（IF_Util × δ）＝0.1505 ÷ 0.51", "0.000")
drow("pReq", "F2", "回本所需實收單價（L 基準）", "$/M", lambda c: f"={dc('thr',c)}*{dc('Pbar',c)}/{I('L',c)}", "門檻 × P̄ ÷ L", "0.00", True)
drow("pReqLo", "F3", "回本所需實收單價（L 低端）", "$/M", lambda c: f"={dc('thr',c)}*{dc('Pbar',c)}/{I('L','I')}", "門檻 × P̄ ÷ L 低端（輸入頁 I 欄）", "0.00")
drow("jF", "F4", "機隊端判讀（L 基準）", "", lambda c: f'=IF({dc("pF",c)}>={dc("pReq",c)},"回本","不回本")', "D7 ≥ F2", None)
drow("jFlo", "F5", "機隊端判讀（L 低端）", "", lambda c: f'=IF({dc("pF",c)}>={dc("pReqLo",c)},"回本","不回本")', "D7 ≥ F3", None)
drow("jD", "F6", "需求端判讀（L 基準）", "", lambda c: f'=IF({dc("pD",c)}>={dc("pReq",c)},"回本","不回本")', "B7 ≥ F2", None)
drow("jDlo", "F7", "需求端判讀（L 低端）", "", lambda c: f'=IF({dc("pD",c)}>={dc("pReqLo",c)},"回本","不回本")', "B7 ≥ F3", None)
drow("Lreq", "F8", "回本所需 L（m＝m_fleet）", "x", lambda c: f"={dc('thr',c)}/{dc('mF',c)}", "門檻 ÷ m_fleet（對照 L1_LReqFleet 0.3645）", "0.000")
drow("Lm", "F9", "L × m_fleet", "x", lambda c: f"={I('L',c)}*{dc('mF',c)}", "對照門檻 F1", "0.000")
wd.freeze_panes = "D5"

# ───────────────────────── 閉合條件 ─────────────────────────
wc = sheet("閉合條件", [7, 46, 13, 15, 15, 15, 15, 15, 60])
put(wc, 1, 1, "閉合條件：其他輸入不動，單獨改一個輸入要改到多少才能閉合（缺口＝1）", f_title, border=False, al=None)
put(wc, 2, 1, "因為缺口 ＝ 支出 × 實際利用率 × κ ÷（計價倍數 × 常數）÷ 需求 token，前四項是乘除關係，單獨改一項所需的值可以直接解出；τ 另由 E7 解。", f_txt, border=False)
wc.merge_cells("A2:I2"); wc.row_dimensions[2].height = 30
header(wc, 4, ["#", "單獨調整的輸入", "單位"] + SC_NAME + ["解法與判讀"])
wc.row_dimensions[4].height = 42
CC = [
    ("推論支出 需降到", "$B", lambda c: f"={I('spend',c)}/推導鏈!{c}{D['gap']}", "支出 ÷ 缺口；證據下限 8.4（SRC_DEM_004）", "0.00"),
    ("計價倍數 需升到", "x", lambda c: f"={I('SB',c)}*推導鏈!{c}{D['gap']}", "計價倍數 × 缺口；證據 1.2–2.0，模型上限 3.0", "0.00"),
    ("實際利用率×折減 需降到", "%", lambda c: f"={I('Ua',c)}/推導鏈!{c}{D['gap']}", "實際利用率 ÷ 缺口；模型區間 0.30–0.40", "0.0%"),
    ("κ 需降到", "x", lambda c: f"={I('kap',c)}/推導鏈!{c}{D['gap']}", "κ ÷ 缺口；A 段區間 0.65–1.2", "0.00"),
    ("每則 token τ 需升到", "tok", lambda c: f"=推導鏈!{c}{D['tauS']}", "τ*（推導鏈 E7）；證據 1,650–11,300", "#,##0"),
]
for k, (lab, unit, fn, words, fmt) in enumerate(CC, 1):
    r = 4 + k
    put(wc, r, 1, k); put(wc, r, 2, lab); put(wc, r, 3, unit)
    for c in SC:
        put(wc, r, SC.index(c) + 4, fn(c), f_calc, fmt)
    put(wc, r, 9, words)
r = 11
section(wc, r, "判讀（模型現值欄）", 9); r += 1
judg = [
    ("推論支出", f'=IF(D5<8.4,"需低於 84 億：超出證據","可在證據內閉合")'),
    ("計價倍數", f'=IF(D6>3,"需高於 3.0：超出模型上限",IF(D6>2.2,"需高於 2.2：超出 A 段證據","可在證據內閉合"))'),
    ("實際利用率", f'=IF(D7<0.3,"需低於 0.30：超出模型區間","可在區間內閉合")'),
    ("κ", f'=IF(D8<0.65,"需低於 0.65：超出 A 段區間","可在區間內閉合")'),
    ("τ", f'=IF(D9>11300,"需高於 11,300：超出證據","可在證據內閉合")'),
]
for lab, fml in judg:
    put(wc, r, 2, lab); put(wc, r, 4, fml, f_calc); wc.merge_cells(start_row=r, start_column=4, end_row=r, end_column=8); r += 1
r += 1
section(wc, r, "結論", 9); r += 1
for t in [
    "1. 模型現值下，五個輸入沒有一個能「單獨」在證據範圍內閉合：支出要低於 84 億、計價倍數要高於 3、實際利用率要低於 0.30、κ 要低於 0.65 或 τ 要高於 11,300，五者都在邊界之外（數值見上表 D 欄）。",
    "2. 兩項以上同時移動才閉合，例如「推論支出 84 億＋κ 0.75」（G 欄）缺口約 1.08，所需 τ 約 4,700，與需求證據中心 4,300 一致。",
    "3. A 段證據把計價倍數拉低到 1.5（E 欄），缺口反而變大到約 2.9：這是「新證據讓問題更難閉合」的方向。",
    "4. 缺口只影響「m 該取哪個值」，不影響營收與實收單價的美元觀測；回本判讀見「推導鏈」F 節與「回本」頁。",
]:
    put(wc, r, 1, t, border=False); wc.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9); wc.row_dimensions[r].height = 30; r += 1

# ───────────────────────── 代數推導 ─────────────────────────
wa = sheet("代數推導", [6, 120])
put(wa, 1, 1, "代數推導：缺口從哪裡來、為什麼價格不影響缺口", f_title, border=False, al=None)
steps = [
    ("符號", "R＝營收；P̄＝混合有效單價；D_p、D_f＝需求端付費、免費 token；r＝D_f ÷ D_p；cap_P、cap_F＝付費、免費每 GW 年產能（含 IF_Util）；S＝推論支出；H＝每 GW 持有成本；SB＝計價倍數；U＝IF_Util；U_a＝實際利用率×折減；κ＝請求形狀修正。"),
    ("1", "需求端需要的 GW：GW_token ＝ D_p ÷ cap_P ＋ D_f ÷ cap_F ＝ D_p ×（1 ÷ cap_P ＋ r ÷ cap_F）。（推導鏈 C4）"),
    ("2", "機隊端有效 GW：GW_eff ＝（S ÷ H）÷ SB ×（U_a ÷ U）× κ。（推導鏈 D1–D4）"),
    ("3", "機隊端付費 token：T_fleet ＝ GW_eff ÷（1 ÷ cap_P ＋ r ÷ cap_F）。因為機隊端沿用需求端的 r，分母與第 1 步相同。（推導鏈 D5）"),
    ("4", "缺口 ＝ T_fleet ÷ D_p ＝ GW_eff ÷ GW_token ＝［（S ÷ H）÷ GW_token］÷［SB × U ÷（U_a × κ）］＝ ScaleServe ÷（SB × U ÷（U_a × κ））。模型現值：7.378 ÷（2.0 × 0.6 ÷ 0.35）＝ 7.378 ÷ 3.429 ＝ 2.152。（推導鏈 E3–E5 驗算）"),
    ("5", "兩個 m：m_整體 ＝ R ÷（D_p × P̄）；m_fleet ＝ R ÷（T_fleet × P̄）。相除得 m_整體 ÷ m_fleet ＝ T_fleet ÷ D_p ＝ 缺口。R 與 P̄ 都約掉，所以「價格時間錯配」（2025 實際單價 ≠ 2026 牌價快照）只會讓兩個 m 同比例變動，對缺口的貢獻為 0。（見「價格時間錯配」頁）"),
    ("6", "閉合條件：缺口＝1 ⇔ D_p ＝ T_fleet ⇔ S × U_a × κ ÷ SB ＝ H × U × GW_token。左邊是機隊端的四個輸入，右邊由需求端決定。單獨改一項所需的值：S* ＝ S ÷ 缺口、SB* ＝ SB × 缺口、U_a* ＝ U_a ÷ 缺口、κ* ＝ κ ÷ 缺口。（閉合條件頁第 1–4 列）"),
    ("7", "改需求端的 τ：令（D_p ＋ D_f）剛好用滿 GW_eff。ChatGPT 年 token T_chat 滿足 API ÷ cap_P ＋ T_chat ×［(1 − f) ÷ cap_P ＋ f ÷ cap_F］＝ GW_eff，解得 T_chat* ＝（GW_eff − API ÷ cap_P）÷［(1 − f) ÷ cap_P ＋ f ÷ cap_F］，τ* ＝ T_chat* ÷（每日訊息 × 365）。f＝免費占比。（推導鏈 E6–E7）"),
    ("8", "τ 為何要變很多：API 部分不隨 τ 變，所以 τ 加倍時需求 token 不會加倍。模型現值下 τ 由 2,000 加到 4,000，GW_token 只由 0.1403 增為 0.1826（×1.30）。這也是「四項口徑差」把 τ 的倍數記成 2.0 會高估的原因。（見「四項口徑差」頁）"),
    ("9", "第二個不閉合：閉合後免費算力只占約 21%（推導鏈 E9），但 OpenAI 自己的支出數字顯示免費推論占 46%（E10）。若要同時滿足，免費 token 必須多很多，m 會再往上修。這一項本活頁簿只列出，未解。"),
    ("10", "回本：L × m ≥ 門檻，門檻 ＝ 回本乘積 ÷（U × δ）＝ 0.1505 ÷ 0.51 ＝ 0.295。換成實收單價：L × 實收單價 ≥ 0.295 × P̄ ＝ 0.579 $/M。L＝0.643 時需實收 0.90 $/M，L＝0.342 時需 1.69 $/M。注意：門檻用的是新建 VR200 每 GW 的成本與產出，m 量的是 2025 年 Hopper／GB200 機隊的實收；兩者時點不同，本活頁簿沿用模型的做法並列，不做調整。"),
]
r = 3
for k, t in steps:
    put(wa, r, 1, k, f_key); put(wa, r, 2, t); wa.row_dimensions[r].height = 15 * (1 + len(t) // 70); r += 1

# ───────────────────────── 敏感度 ─────────────────────────
VARS = [("tau", "每則 token τ"), ("fs", "免費占比"), ("apir", "API 全年比例"), ("ppd", "每日訊息"),
        ("spend", "推論支出"), ("SB", "計價倍數"), ("Ua", "實際利用率×折減"), ("kap", "κ")]
ws_ = sheet("敏感度", [16, 8, 10, 9, 9, 9, 9, 9, 9, 9, 13, 13, 13, 13, 11, 11, 11, 11, 10, 11, 12])
put(ws_, 1, 1, "敏感度：從模型現值出發，一次只把一個輸入移到區間低或高（區間在「輸入」頁 I／J 欄）", f_title, border=False, al=None)
put(ws_, 2, 1, "C–J 欄是該列實際使用的輸入（被調整的那一格為藍字，其餘引用模型現值）；K 欄起是同一條推導鏈的閉式公式。最右欄「ln 寬度」＝ ln(高端缺口 ÷ 低端缺口) 的絕對值，數字越大越重要。", f_txt, border=False)
ws_.merge_cells("A2:U2"); ws_.row_dimensions[2].height = 30
cols = ["調整的輸入", "端點"] + [v[1] for v in VARS] + ["需求付費 token", "免費 token", "有效 GW", "機隊付費 token", "缺口", "m_fleet", "實收單價 $/M", "τ*", "L 基準判讀", "缺口 ln 寬度"]
header(ws_, 4, cols); ws_.row_dimensions[4].height = 42
vcol = {k: 3 + i for i, (k, _) in enumerate(VARS)}
def X(k, r): return f"{CL(vcol[k])}{r}"
r = 5
def srow(r, label, end, var=None, which=None):
    put(ws_, r, 1, label); put(ws_, r, 2, end)
    for k, _ in VARS:
        if k == var:
            put(ws_, r, vcol[k], f"={I(k, which)}", f_in)
        else:
            put(ws_, r, vcol[k], f"={I(k, 'D')}", f_link)
        ws_.cell(r, vcol[k]).number_format = "#,##0.00"
    api = f"{I('tpm','D')}*1E9*525600*{X('apir',r)}/1E6"
    chat = f"{X('ppd',r)}*1E9*{X('tau',r)}*365/1E6"
    capP = f"推導鏈!$D${D['capP']}"; capF = f"推導鏈!$D${D['capF']}"; hold = f"推導鏈!$D${D['hold']}"
    put(ws_, r, 11, f"={api}+{chat}*(1-{X('fs',r)})", f_calc, "#,##0.0E+0")
    put(ws_, r, 12, f"={chat}*{X('fs',r)}", f_calc, "#,##0.0E+0")
    put(ws_, r, 13, f"={X('spend',r)}/{hold}/{X('SB',r)}*({X('Ua',r)}/{I('U','D')})*{X('kap',r)}", f_calc, "0.0000")
    put(ws_, r, 14, f"=M{r}/(1/{capP}+(L{r}/K{r})/{capF})", f_calc, "#,##0.0E+0")
    put(ws_, r, 15, f"=N{r}/K{r}", f_calc, "0.000")
    put(ws_, r, 16, f"={I('R','D')}*1E9/(N{r}*推導鏈!$D${D['Pbar']})", f_calc, "0.000")
    put(ws_, r, 17, f"={I('R','D')}*1E9/N{r}", f_calc, "0.00")
    put(ws_, r, 18, f"=(M{r}-({api})/{capP})/((1-{X('fs',r)})/{capP}+{X('fs',r)}/{capF})*1E6/({X('ppd',r)}*1E9*365)", f_calc, "#,##0")
    put(ws_, r, 19, f'=IF(Q{r}>=推導鏈!$D${D["pReq"]},"回本","不回本")', f_calc)
srow(r, "（基準：模型現值）", "基準"); r += 1
for k, lab in VARS:
    srow(r, lab, "低", k, "I"); srow(r + 1, lab, "高", k, "J")
    put(ws_, r, 20, f"=ABS(LN(O{r+1}/O{r}))", f_calc, "0.00")
    ws_.merge_cells(start_row=r, start_column=20, end_row=r + 1, end_column=20)
    r += 2
put(ws_, r + 1, 1, "讀法：缺口 ln 寬度最大的輸入，就是最值得先查證的輸入。m_fleet 與實收單價只隨機隊端與營收變動，需求端輸入（τ、免費占比、API 比例、每日訊息）只改變缺口，不改變 m_fleet。", f_txt, border=False)
ws_.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=21); ws_.row_dimensions[r + 1].height = 30
ws_.freeze_panes = "C5"

# ───────────────────────── 四項口徑差 ─────────────────────────
wq = sheet("四項口徑差", [7, 52, 13, 15, 15, 70])
put(wq, 1, 1, "四項口徑差：模型 L1 的落差分解，以及為何乘積 13.4 會超過 ScaleServe 7.38", f_title, border=False, al=None)
header(wq, 3, ["#", "項目", "單位", "模型 L1 現值", "本活頁簿重算", "說明"])
gwt2000 = (f"=({I('tpm','D')}*1E9*525600*{I('apir','D')}/1E6+{I('ppd','D')}*1E9*2000*365/1E6*(1-{I('fs','D')}))/推導鏈!$D${D['capP']}"
           f"+({I('ppd','D')}*1E9*2000*365/1E6*{I('fs','D')})/推導鏈!$D${D['capF']}")
Q = [
    ("1", "GapPrompt：每則 token ÷ 2,000", "x", 2.0, f"=推導鏈!D{D['GWt']}/E11", "模型直接用 τ ÷ 2,000＝2.0。但 API 不隨 τ 變，GW 只增加 1.30 倍（E 欄＝τ 4,000 的 GW ÷ τ 2,000 的 GW）。", "0.000"),
    ("2", "GapSpendBasis：計價倍數", "x", 2.0, f"={I('SB','D')}", "與推導鏈 D2 相同；A 段證據中心 1.5", "0.000"),
    ("3", "GapISL：參考請求 ISL 16K 對 4K", "x", 2.307, f"=1/{I('kap','D')}", "模型取「輸入縮成 4K、輸出仍 2K」的產出比；A 段以實際輸入輸出比重算 κ≈1.0，即本項≈1.0", "0.000"),
    ("4", "GapUtil：IF_Util × δ ÷ 實際利用率", "x", 1.457, f"={I('U','D')}/{I('Ua','D')}", "模型乘了 δ 0.85，但機隊路線（推導鏈 D3）只用 IF_Util ÷ 實際利用率＝1.714；兩處口徑不同", "0.000"),
    ("5", "乘積", "x", "=D4*D5*D6*D7", "=E4*E5*E6*E7", "模型 13.44；本活頁簿以有效 τ 倍數與機隊口徑重算", "0.00"),
    ("6", "ScaleServe（τ＝4,000）", "x", 7.378, f"=推導鏈!D{D['SS']}", "支出路線 GW ÷ token 路線 GW", "0.000"),
    ("7", "ScaleServe（τ＝2,000；v5.28 基準）", "x", None, f"=推導鏈!D{D['GWs']}/E11", "乘積應對照的對象是 τ＝2,000 的 ScaleServe", "0.000"),
    ("—", "（輔助）τ＝2,000 時 token 路線 GW", "GW", None, gwt2000, "計算第 1、7 列用", "0.0000"),
    ("8", "只改正 τ 重複計入、其餘維持模型值的乘積", "x", None, "=E4*D5*D6*D7", "1.30 × 2.0 × 2.307 × 1.457", "0.00"),
    ("9", "第 8 列對 ScaleServe（τ＝2,000）的解釋比例", "%", None, "=E12/E10", "第 8 列 ÷ 第 7 列", "0%"),
    ("10", "再改用實際流量（κ）與機隊利用率口徑的乘積", "x", None, "=E8", "＝第 5 列 E 欄", "0.00"),
    ("11", "第 10 列的解釋比例", "%", None, "=E14/E10", "第 10 列 ÷ 第 7 列；剩下的部分就是推導鏈 E2 的缺口", "0%"),
]
r = 4
for k, lab, unit, mv, fml, words, fmt in Q:
    put(wq, r, 1, k); put(wq, r, 2, lab); put(wq, r, 3, unit)
    put(wq, r, 4, mv, f_in if isinstance(mv, (int, float)) else f_calc, fmt)
    put(wq, r, 5, fml, f_calc, fmt); put(wq, r, 6, words); wq.row_dimensions[r].height = 30
    r += 1
r += 1
for t in ["讀法：模型的乘積 13.44 超過 7.38，是因為 (a) τ 的倍數 2.0 被重複計入（ScaleServe 7.38 已經是 τ＝4,000 下的值，應對照 τ＝2,000 的 9.60），(b) GapISL 2.31 用了不符實際流量的假設。只改正 (a) 時乘積可解釋約九成（第 9 列）；再改正 (b) 與利用率口徑後只解釋不到一半（第 11 列），剩下的就是推導鏈 E2 的缺口。",
          "四項口徑差只是說明工具；本活頁簿以推導鏈 E4 的恆等式為準：缺口＝ScaleServe ÷（計價倍數 × IF_Util ÷（實際利用率 × κ））。"]:
    put(wq, r, 1, t, border=False); wq.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6); wq.row_dimensions[r].height = 45; r += 1

# ───────────────────────── 價格時間錯配 ─────────────────────────
wp = sheet("價格時間錯配", [34, 14, 12, 14, 60])
put(wp, 1, 1, "價格時間錯配：2025 年實際牌價 ÷ 2026-09 快照（ρ），以及對 m 的影響", f_title, border=False, al=None)
put(wp, 2, 1, "參考請求單價 ref＝[0.45 × 輸入價 × 16,000 ＋ 0.55 × 快取價 × 16,000 ＋ 輸出價 × 2,000] ÷ 18,000（未折扣；兩邊同乘 0.8 約掉）。數值取自 v5.36A 第 3.3 節（Derived；牌價為二手彙整，等級 3）。", f_txt, border=False)
wp.merge_cells("A2:E2"); wp.row_dimensions[2].height = 30
header(wp, 4, ["模型", "ref $/M", "2025 月數", "加權", "說明"])
P = [("GPT-4o（中階，2025-01～07）", 2.722, 7), ("GPT-5（中階，2025-08～11）", 1.672, 4), ("GPT-5.2（中階，2025-12）", 2.341, 1),
     ("GPT-4o mini（低階，2025-01～07）", 0.163, 7), ("GPT-5 mini（低階，2025-08～12）", 0.334, 5),
     ("快照 Sol（GPT-6 中階）", 2.009, None), ("快照 Luna（GPT-6 低階）", 0.100, None)]
r = 5
for lab, v, mth in P:
    put(wp, r, 1, lab); put(wp, r, 2, v, f_in, "0.000"); put(wp, r, 3, mth, f_in)
    put(wp, r, 4, f"=B{r}*C{r}" if mth else None, f_calc, "0.000"); r += 1
put(wp, 13, 1, "2025 中階時間加權 ref", f_key); put(wp, 13, 2, "=SUM(D5:D7)/SUM(C5:C7)", f_calc, "0.000")
put(wp, 14, 1, "2025 低階時間加權 ref", f_key); put(wp, 14, 2, "=SUM(D8:D9)/SUM(C8:C9)", f_calc, "0.000")
put(wp, 15, 1, "ρ 情境 1：全用中階", f_key); put(wp, 15, 2, "=B13/B10", f_calc, "0.000"); put(wp, 15, 5, "2025 中階 ÷ 快照 Sol；A 段區間 0.83–1.36")
put(wp, 16, 1, "ρ 情境 2：中階＋低階各半", f_key); put(wp, 16, 2, "=(0.5*B13+0.5*B14)/(0.5*B10+0.5*B11)", f_calc, "0.000"); put(wp, 16, 5, "A 段區間 0.82–1.47")
put(wp, 18, 1, "修正後 m（模型現值欄）", f_sec, fill=fill_sec); put(wp, 18, 2, "ρ 情境 1", f_h, fill=fill_h); put(wp, 18, 3, "ρ 情境 2", f_h, fill=fill_h)
put(wp, 19, 1, "m_fleet ÷ ρ"); put(wp, 19, 2, f"=推導鏈!D{D['mF']}/B15", f_calc, "0.000"); put(wp, 19, 3, f"=推導鏈!D{D['mF']}/B16", f_calc, "0.000")
put(wp, 20, 1, "m_整體 ÷ ρ"); put(wp, 20, 2, f"=推導鏈!D{D['mD']}/B15", f_calc, "0.000"); put(wp, 20, 3, f"=推導鏈!D{D['mD']}/B16", f_calc, "0.000")
put(wp, 21, 1, "缺口（修正後 m_整體 ÷ 修正後 m_fleet）"); put(wp, 21, 2, "=B20/B19", f_calc, "0.000"); put(wp, 21, 3, "=C20/C19", f_calc, "0.000")
put(wp, 23, 1, "讀法：ρ 讓兩個 m 都下降 14–18%，但缺口不變（第 21 列＝推導鏈 E2）。實收單價（美元）是 2025 營收 ÷ 2025 token 的觀測，也不受 ρ 影響，所以回本判讀不變。ρ 只改變「m 低於 1 是打折還是牌價下降」的解讀。", f_txt, border=False)
wp.merge_cells("A23:E23"); wp.row_dimensions[23].height = 45

# ───────────────────────── 證據 ─────────────────────────
we = sheet("證據", [9, 34, 26, 14, 40, 14, 26, 40, 12])
put(we, 1, 1, "證據：v5.36A 查證（2026-10-15）的原始紀錄，原樣複製；「已搜尋，未找到」與「不存在」不同", f_title, border=False, al=None)
src = openpyxl.load_workbook(AEVID, data_only=True)
r = 3
for name in src.sheetnames:
    if not (name.startswith("2.") or name.startswith("6_")):
        continue
    section(we, r, name, 9); r += 1
    for row in src[name].iter_rows(values_only=True):
        if all(v is None for v in row): continue
        for c, v in enumerate(row[:9], 1):
            put(we, r, c, v)
        r += 1
    r += 1

# ───────────────────────── 說明（放第一頁） ─────────────────────────
wx = wb.create_sheet("說明", 0)
wx.column_dimensions["A"].width = 22; wx.column_dimensions["B"].width = 110; wx.sheet_view.showGridLines = False
put(wx, 1, 1, "token 分母不閉合：研究用活頁簿（Tokenomics v5.35 數值；v5.36 A 段查證）", f_title, border=False, al=None)
lines = [
    ("要回答的問題", "OpenAI 2025 年的變現率 m 有兩個讀法：用使用量算付費 token 得 m_整體 1.74；用推論支出反推付費 token 得 m_fleet 0.81。兩者差 2.15 倍。差在哪裡？要怎樣才能一致（閉合）？對「1 GW 能不能回本」有什麼影響？"),
    ("一句話結論", "差距全部來自「付費 token 數」的兩種算法；價格不影響差距。模型現值下，沒有任何一個輸入能單獨在證據範圍內把差距補平；最大的單一不確定項是推論支出取 126 億還是 84 億。回本判讀在 L 基準 0.643 下各情境都成立，在 L 低端 0.342 下取決於機隊端的 m。"),
    ("建議閱讀順序", "1 推導鏈（看兩條路線各怎麼算）→ 2 代數推導（為何差距是這個恆等式）→ 3 閉合條件（每個輸入要改多少）→ 4 敏感度（哪個輸入最重要）→ 5 四項口徑差、價格時間錯配（兩個常見誤解）→ 6 證據。"),
    ("怎麼自己試", "改「輸入」頁 H 欄（黃底）任何一格，所有頁面的 H 欄（自訂）會跟著重算。D–G 欄是固定情境，建議不要改。"),
    ("顏色", "藍字＝輸入數值；黑字＝公式；綠字＝引用其他頁；黃底＝可改的自訂輸入；淺綠底＝重點結果列。"),
    ("數字來源", "所有輸入取自 Tokenomics v5.35（model/CURRENT＝20261014_Tokenomics_v5.35.xlsx）的具名範圍或 SRC 列，以及 v5.36 A 段查證（PR #48）。每個輸入的來源與標記在「輸入」頁 L／K 欄。"),
    ("與 Tokenomics 的關係", "本活頁簿是研究用副本，不是 Tokenomics 的一部分；公式逐列對照 Tokenomics 的 Alloc 與 Cap_In H 節（列號寫在推導鏈 I 欄）。模型現值欄應與 Tokenomics 一致：m_fleet 0.810、m_整體 1.743、τ* 13,950、閉合比 0.465。"),
    ("限制", "(1) 計價倍數、84 億、計算毛利 70% 的佐證多為二手報導，原文未讀到。(2) κ 的輸入全是類比。(3) 回本門檻用新建 VR200 的成本與產出，m 量的是 2025 年 Hopper／GB200 機隊，兩者時點不同。(4) 免費算力占比的第二個不閉合（21% 對 46%）只列出未解。"),
    ("待你決定（B 段）", "推論支出主值用 126 億或 84 億；計價倍數區間；每則 token 區間上緣；是否以 κ 取代 GapISL；L1 是否加實收單價列；DB_Evidence 登錄。詳見 PR #48 報告第 5 節。"),
]
r = 3
for k, t in lines:
    put(wx, r, 1, k, f_key); put(wx, r, 2, t); wx.row_dimensions[r].height = 15 * (1 + len(t) // 75); r += 1
r += 1
section(wx, r, "頁面", 2); r += 1
for n, t in [("輸入", "全部數值輸入、四個固定情境＋一個自訂情境、區間、標記、來源"), ("推導鏈", "需求端 → 機隊端 → 閉合 → 回本，逐步公式"),
             ("閉合條件", "單獨改一個輸入所需的值，與是否落在證據範圍"), ("代數推導", "恆等式與閉合條件的推導文字"),
             ("敏感度", "一次動一個輸入的缺口、m_fleet、實收單價與 ln 寬度"), ("四項口徑差", "模型 L1 落差分解的重算與重複計入說明"),
             ("價格時間錯配", "ρ 的計算與對 m、缺口的影響"), ("證據", "v5.36A 查證原始紀錄")]:
    put(wx, r, 1, n); put(wx, r, 2, t); r += 1

for ws in wb.worksheets:
    ws.sheet_properties.tabColor = {"說明": "808080", "輸入": "0000FF", "推導鏈": "000000", "閉合條件": "008000",
                                    "代數推導": "008000", "敏感度": "C65911", "四項口徑差": "7F7F7F", "價格時間錯配": "7F7F7F", "證據": "BF8F00"}.get(ws.title)
for ws in wb.worksheets:
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
wb.save(OUT)
print("saved", OUT, D)

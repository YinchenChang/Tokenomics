# v10.1 1-c: stale explanatory text. A number in a note that moves with the model becomes a formula that reads the current value;
# a number that is really history says which version it belonged to. Every patch is guarded: the cell is changed only while it still holds the
# text the builder (or v10.0) wrote, so a rebuild from v10.1 leaves the cell as it is (idempotent) and a drifted cell is reported, never overwritten.
import re


def F(*parts):
    """Build a text formula: str -> literal, (expr, fmt) -> TEXT of a number (a dash if the value is not a number)."""
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append('"' + p.replace('"', '""') + '"')
        else:
            expr, fmt = p
            out.append(f'IF(ISNUMBER({expr}),TEXT({expr},"{fmt}"),"—")')
    return "=" + "&".join(out)


HIST = "【各版演進記錄：括號內與各段數字為該版當時值，現值以各列公式為準】"

# (sheet, cell, old fragment that must be present, new value or a function of the old value)
FIXES = [
    # ---- L1 (4-0 sheet 5: SL01-SL05) ----
    ("L1", "I48", "基準約 11.5T", F("基準 ", ("D48", "0.0"), "T（現值，隨輸入變動），Epoch 區間 ", ("M48", "0"), "–", ("N48", "0"),
                                    "T；判讀見 P 欄。v5.36 當時基準約 11.5T、每則 token 數與 API 比例同取低端時約 7.7T（歷史值，已不適用）")),
    ("L1", "I49", "兩路線差約 15 倍", F("1 −（IF_FullCost_Sol − IF_AmortBU_Sol）÷ IF_PriceRef_Sol：推論算力計入營業成本、訓練計入研發（不含攤提）。理論毛利率是 SLO 下單一層級滿載、基準利用率的上限；與 2025 隱含值約 ",
                                       ("M49", "0%"), " 的差距，與「兩路線差約 ", ("D69", "0.0"), " 倍」同源（物理產能上限 對 實際營運），屬預期，不調整輸入。E＝高成本欄、F＝低成本欄")),
    ("L1", "I52", "基準約 0.157（v5.25）", F("100% 口徑的機隊營收乘以本乘積即等於持有成本；基準 ", ("D52", "0.000"), "（現值；v5.25 當時約 0.157）。E＝低成本欄、F＝高成本欄。"
                                              "v7.0 起本列維持 _Util 層（未乘生產折減）；L1_FleetMargin 以重解比 L1_FleetProdRatio 代入生產折減。v8.0 L4：維持 VR200 截面（Checks K4 比對的恆等式、契約內已列）；"
                                              "2025 機隊口徑見 L1_FleetBreakeven2025，所需 L 讀後者")),
    ("L1", "I68", "約 10：兩端同幅度偏小的證據", F("基準 ", ("D68", "0.0"), "（低 ", ("E68", "0.00"), "、高 ", ("F68", "0.0"), "）：兩端同幅度偏小的證據（X13 (c)）；校準用，不得當產能")),
    ("L1", "I69", "約 14：四項口徑差的乘積", F("＝1 ÷ L1_ExtServeGW 的推算÷外部比值，現值 ", ("D69", "0.00"), "；四項口徑差的乘積 L1_GapProduct 現值 ", ("D74", "0.00"),
                                              "，兩者之比的未解釋部分見 L1_GapUnexplained")),
    ("L1", "I71", "基準 1.3；v5.36 B2", F("基準 ", ("D71", "0.00"), "（低 ", ("E71", "0.00"), "、高 ", ("F71", "0.00"), "；2-4 起改經濟口徑，v5.36 當時為 1.3）；v5.36 B2（X46，當時的依據）：Oracle 出租 Nvidia 伺服器毛利率略低於 14%"
                                           "（The Information 引 Oracle 內部文件；二手）→ 價格 ÷ 成本約 1.16，未含資本成本；Microsoft 對 OpenAI 的計價未找到（當時高端保留 1.6）；"
                                           "無外部對照（已搜尋，未找到 OpenAI 對 Azure 實付單價；E262）")),
    ("L1", "I102", "v7.0 的 L1_MFleet 值", F("v7.0 當時的 L1_MFleet 值為 0.5565（歷史值）；本列現值 ", ("D102", "0.0000"), "（公式，隨輸入變動）；D2 之前把 2025 營收配 2026 牌價。保留作對照，不進回本比較")),
    # ---- Cap_In (SL07-SL14) ----
    ("Cap_In", "A176", "錨點 τ* ≈ 13,950", F("閉合解：令需求 token（付費＋免費）佔滿機隊有效產能所需的每則 token 數 τ*（三步）；錨點 τ* ≈ ", ("C179", "#,##0"))),
    ("Cap_In", "G174", "現值 0.465", F("現值 ", ("C174", "0.000"), "（舊說明寫 0.465，為歷史值）；M4 在 < 0.5 或 > 2 時觸發（見 Checks M4）：需求路線只數到機隊產出的 ", ("C174", "0%"))),
    ("Cap_In", "G175", "現值 0.319", F("現值 ", ("C175", "0.000"), "（舊說明寫 0.319，為歷史值）（＝L1_TokCeiling 判讀）")),
    ("Cap_In", "G255", "基準 2.207", F("基準 ", ("C255", "0.000"), "（現值，隨輸入變動；舊說明寫 2.207＝1 ÷ 閉合比 0.4531、v5.35 為 2.152，皆為歷史值）；只算基準欄：H 節 D／E 欄的需求 token 隨 τ 區間端點改變，"
                                              "ScaleServe 以基準 τ 計，D／E 欄不成立；v6.1 D13：分母的實際利用率乘 CTL_ProdDerate（與第 114 列一致，驗算差仍須為 0）")),
    ("Cap_In", "G116", "約 8.2 × 10⁹", F("r 取模型（第 r 列）；A 段 3.2 節 2025 組合變體約 8.2 × 10⁹（報告當時值；現值 ", ("C116/1E9", "0.0"), " × 10⁹）")),
    ("Cap_In", "G118", "約 12.0 × 10⁹", F("A 段 3.2 節約 12.0 × 10⁹（報告當時值；現值 ", ("C118/1E9", "0.0"), " × 10⁹）；上限 ÷ 需求路線＝L1_ScaleServe ÷（L1_GapSpendBasis × L1_GapUtil）")),
    ("Cap_In", "G119", "A 段 2025 組合約 0.81", F("分子同 H1（毛額，SRC_DEM_007）；單價同 H4；A 段 2025 組合約 0.81（報告當時值；現值 ", ("C119", "0.00"), "）")),
    ("Cap_In", "G121", "A 段 2025 組合約 0.56", F("A 段 2025 組合約 0.56（報告當時值；現值 ", ("C121", "0.00"), "）；m 不可能低於此值（除非 C23、C24 改）")),
    ("Cap_In", "G109", "Alloc_In 計價倍數（1.3；D 欄取低端 1.0", F("Alloc 第 61 列（SRC_DEM_004 ÷ 世代組合持有成本；v5.36 起 OpenAI 端 ", ("SRC_DEM_004", "0.0"), "）÷ Alloc_In 計價倍數（現值 ", ("AL_SpendBasis", "0.00"), "；D 欄取低端 ",
                                                                  ("AL_SpendBasis_Lo", "0.00"), "＝GW 取高、E 欄取高端 ", ("AL_SpendBasis_Hi", "0.00"), "；舊說明寫 1.3／1.0／1.6，為 v5.36 歷史值）× 請求形狀修正 κ（現值 ", ("AL_Kappa", "0.00"),
                                                                  "；D 欄取高端 ", ("AL_Kappa_Hi", "0.00"), "、E 欄取低端 ", ("AL_Kappa_Lo", "0.00"), "，與 token 取高／取低同向）")),
    ("Cap_In", "G284", "v7.0 的 L1_MFleet 值（0.5565）", F("v7.0 當時的 L1_MFleet 值為 0.5565（歷史值）；本列現值 ", ("C284", "0.0000"), "（公式，隨輸入變動）；D2 之前的混用口徑，只作對照 → L1_MFleet_Px2026")),
    ("Cap_In", "G288", "v7.0 的 L1_LReqFleet 值（0.5304）", F("v7.0 當時的 L1_LReqFleet 值為 0.5304（歷史值，原樣保留作對照）；本列現值 ", ("C288", "0.000"), "（公式）；VR200 損益兩平（2026 單價）對 2025 的 m（2026 牌價）混用世代與年度，"
                                                        "故不再作為所需 L 的主口徑（v8.0 L4）")),
    ("Cap_In", "G240", "v7.0 的 VR200 口徑（0.530）保留於 M 節對照列", F("v8.0 L4：L1_FleetBreakeven2025（Alloc K 節）÷（IF_Util × CTL_ProdDerate × m）；基準值見 L1_LReqFleet；v7.0 的 VR200 口徑（當時 0.530，現值 ",
                                                                        ("C288", "0.000"), "）保留於 M 節對照列")),
    ("Cap_In", "H218", "2025 欄＝H9 (i)", lambda old: old if old.startswith(HIST) else HIST + old),
    ("Cap_In", "A264", "讀法（v5.33 改寫）", lambda old: old if old.startswith(HIST) else HIST + old),
    # ---- Checks (SL08, SL15, query C item 4) ----
    ("Checks", "E131", "現值 0.465 → 觸發",
     '="Cap_In H9 第 174 列（AL_DPaid ÷ H7 機隊付費 token 點估計）；現值 "&IF(ISNUMBER(Cap_In!$C$174),TEXT(Cap_In!$C$174,"0.000"),"—")&IF(D131=1," → 觸發，屬預期"," → 未觸發")&"（舊說明寫 0.465，為歷史值；v5.34 B3）"'),
]
CHECKS_C = '="約 "&TEXT(MIN(B44:B46),"0.0")&"–"&TEXT(MAX(B44:B46),"0.0")&"（對照，無通過條件）"'
CHECKS_E44 = ('="本列現值 "&IF(ISNUMBER(B44),TEXT(B44,"0.00"),"—")&"（舊說明寫「≈1」；三列比值 "&TEXT(MIN(B44:B46),"0.00")&"–"&TEXT(MAX(B44:B46),"0.00")&'
              '"，同量級）：中國廠商定價與 Hopper 級物理成本同量級；前緣由接近成本者決定（K4 理由 2）"')
for _c in ("C44", "C45", "C46"):
    FIXES.append(("Checks", _c, "≈1", CHECKS_C))
FIXES.append(("Checks", "E44", "≈1：中國廠商定價接近", CHECKS_E44))


def apply_fixes(wb):
    done, same, drift = 0, 0, []
    for sh, ref, frag, new in FIXES:
        c = wb[sh][ref]
        old = c.value
        if not isinstance(old, str):
            drift.append((sh, ref, "empty or not text"))
            continue
        target = new(old) if callable(new) else new
        if old == target:
            same += 1
        elif frag in old:
            c.value = target
            done += 1
        else:
            drift.append((sh, ref, "old fragment not found"))
    return done, same, drift


# ---- Interface A300-A310: the names of the four-layer monotonic rows carry no suffix in the label (SL17) ----
def interface_labels(wb):
    ws = wb["Interface"]; n = 0
    for r in range(290, 330):
        v = ws.cell(r, 1).value
        if isinstance(v, str):
            m = re.match(r"^(IFW_[A-Za-z0-9]+(?:_[A-Za-z]+)?)：Interface 四層單調", v)
            if m and not m.group(1).endswith("_*"):
                ws.cell(r, 1).value = v.replace(m.group(1) + "：", m.group(1) + "_*：", 1); n += 1
    return n


# ---- Harness: rows 67-84 (cost per attempt) and 87-104 (cost per successful task) carry identical labels (SL19) ----
def harness_labels(wb):
    ws = wb["Harness"]; n = 0
    for rows, pre in ((range(67, 85), "每次嘗試成本："), (range(87, 105), "每成功任務成本：")):
        for r in rows:
            v = ws.cell(r, 1).value
            if isinstance(v, str) and v and not v.startswith(pre) and v.startswith(("VR200 ×", "GB300 ×")):
                ws.cell(r, 1).value = pre + v; n += 1
    return n


# ---- SRC records of the RL / harness cross-checks cite section 3 of the 3A report, not section 2 (query C item 4) ----
SRC_CITE = [("SRC_Perf", "J68"), ("SRC_Perf", "J69"), ("SRC_Harness", "J20")]


def src_cites(wb):
    n = 0
    for sh, ref in SRC_CITE:
        v = wb[sh][ref].value
        if isinstance(v, str) and "稽核修正3A_查證.md 第 2 節" in v:
            wb[sh][ref].value = v.replace("稽核修正3A_查證.md 第 2 節", "稽核修正3A_查證.md 第 3 節"); n += 1
    return n


def checks_header(wb):
    ws = wb["Checks"]
    if ws["G139"].value in (None, ""):
        ws["G139"].value = ws["G42"].value; return 1
    return 0

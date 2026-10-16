# v9.0 (work order docs/workorders/20261016_稽核修正2.md r1, section 5r1 = segment 2-4): D9 (cache hit in capacity, free share on one token basis, kappa on the price end,
# amortisation denominator) and the 2-3 follow-ups.  The file keeps the name v810 (the segment was planned as v8.1); the version is v9.0 because contract names change definition
# (IF_AllocQ1_R2 spend route, L1_MImplied／MAPI／MSub／MSeat 2025 price, IF_AmortRev_* paid-token denominator, L1_ExtServeGW main basis; CLAUDE.md section 4: contract change = major).
#   M1 cache hit enters prefill capacity: perf.py (Perf, Sens_Perf and their _Prod mirrors; Perf_Batch keeps the full ISL so Training is untouched)
#   M2 free share on one basis: v532 paid_share (Cap_In row 87) 1 - AL_FreeShare (token basis); the other readers of IF_FreeShare/B4_Free multiply GW or spend, not tokens (left as is)
#   M3 kappa on the price end: v532 price row (Cap_In C90) and v800 CAP_Price25Mix
#   M4 IF_AmortRev_*: block4 amortize (d) denominator = the tier's paid tokens
#   M6 2-3 follow-ups: demand-route m (H5, H8 and their display rows) and Cap_In I-7 required L (m = L1_MAPI) on the 2025 basis; IF_AllocQ1_R2 on the spend route; L1_ExtServeGW back to main basis
#   M7 text flag wording kept per cause; downstream contract text rewritten (docs/plan)
# Every write to an Excel-owned cell is guarded (text not yet present ／ cell still holds its v8.0 value).
import re
import v532
import v533
import v534
import v535
import v800

VERSION = "20261016_Tokenomics_v9.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-16"
V = "v9.0"
WO = "工作單 docs/workorders/20261016_稽核修正2.md r1 第 5r1 節"
CHAT_DEF = "chat 端預設（M1–M7 見工作單 5r1），可撤回"
_PATCHED = False
P25 = "CAP_Price25Mix"
_DEM = re.compile(r"[CDE]\{(?:P_)?price\}")


def _sub_price(it):
    """Demand-route m rows: the H4 price cell (2026 snapshot) -> the 2025 mixed price (kappa included); low／high columns read the base cell (price range is not crossed into m)."""
    it = list(it)
    for k in range(1, len(it)):
        if isinstance(it[k], str) and _DEM.search(it[k]):
            it[k] = _DEM.sub(P25, it[k])
    return tuple(it)


def patch_specs():
    """Call right after v800.patch_specs() and before the Cap_In H sections are written."""
    global _PATCHED
    if _PATCHED: return
    # M6 (a): demand-route m on the 2025 price
    for sp, keys in ((v532.SPEC, ("m_sub", "m_api", "m_all", "m_api_ext", "m_all_ext")),
                     (v533.SPEC, ("m_sub_ex", "m_all_ex")),
                     (v534.SPEC_H8, ("m_api", "m_cons", "m_seat", "m_all", "need_tok", "cap_tok"))):
        for i, it in enumerate(sp):
            if it[0] in keys:
                new = _sub_price(it)
                assert new != it, it[0]
                sp[i] = new
    # M6 (a): H10 2025 column (C) price row on the 2025 price, so that its m rows agree with H5 (self-check row "自我檢查：2025 欄")
    sp = v534.SPEC_H10
    for i, it in enumerate(sp):
        if it[0] == "q_price":
            it = list(it)
            assert it[3] == "=$C${P_price}", it[3]
            it[3] = "=CAP_Price25Mix"
            it[1] = "付費 token 混合有效單價（C 欄＝2025 年度 CAP_Price25Mix（v9.0 M6，與 H5 同口徑）；D–F 欄＝H4 第 {P_price} 列，2026 快照）"
            sp[i] = tuple(it)
    # M6 (a): Cap_In I-7 required L (m = L1_MAPI) on the 2025 fleet breakeven, as the fleet row in v800
    sp = v535.SPEC_I
    for i, it in enumerate(sp):
        if it[0] == "i_req_api":
            it = list(it)
            for k in (3, 4, 5): it[k] = re.sub(r"\bL1_FleetBreakeven\b", "L1_FleetBreakeven2025", it[k])
            it[1] = "回本所需 L（2025 機隊口徑；m＝L1_MAPI；D 欄 m＝L1_MAPI_Hi、E 欄 L1_MAPI_Lo）"
            it[7] = "v9.0 M6：L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate × m）；m_API 亦用 2025 單價（CAP_Price25Mix）；基準值見 L1 對應列"
            sp[i] = tuple(it)
    _PATCHED = True


# ================================================================== L1 rows (M6: ExtServeGW back to the main basis; labels of the demand-route m rows)
M6_TAIL = "｜v9.0 M6：單價改 2025 年度混合有效單價 CAP_Price25Mix（× κ；與機隊 m 同年度口徑）；m 的低／高只反映 token 端，價格區間不交叉"


def l1_patch(R):
    out = []
    for row in R:
        row = list(row)
        key = row[0]
        if key in ("MImplied", "MImplied_Ext", "MAPI", "MSub", "MSeat") and M6_TAIL not in row[2]:
            row[2] = row[2] + M6_TAIL
        elif key == "ExtServeGW":
            row[1] = "服務 GW：模型主口徑（支出路線）對 外部對照（推論支出 ÷ 持有成本）"
            row[2] = ("OpenAI 2025；v9.0 M6：恢復「模型主口徑對外部」——推算值＝IF_AllocServeGW（支出路線，D14 主口徑），外部對照＝推論支出 ÷ 持有成本；"
                      "token 路線（需求 D ÷ 每 GW 產能）改為對照，見 IF_AllocServeGW_Tok 與 L1_ScaleServe")
            assert row[3] == "=IF_AllocServeGW_Tok", row[3]
            row[3] = row[4] = row[5] = "=IF_AllocServeGW"
            row[8] = ("主口徑與外部對照同源（SRC_DEM_004 ÷ 持有成本），比值必為 1；本列不再是獨立檢驗。token 路線對支出路線的差距（未解釋）見 L1_ScaleServe，token 路線值見 IF_AllocServeGW_Tok"
                      if len(row) > 8 else "")
        out.append(tuple(row))
    return out


# ================================================================== L1 judgement column (M5): identity reading as the main reading, literal reading beside it
def l1_judge(wb):
    ws = wb["L1"]
    r = int(wb.defined_names["L1_LReqFleet"].attr_text.split("$")[-1]); assert ws[f"A{r}"].value == "L1_LReqFleet", (r, ws[f"A{r}"].value)
    ri = int(wb.defined_names["L1_LReqFleet_Id"].attr_text.split("$")[-1]); assert ws[f"A{ri}"].value == "L1_LReqFleet_Id", (ri, ws[f"A{ri}"].value)
    D, I, M = f"D{r}", f"D{ri}", f"M{r}"
    verdict = lambda x: f'IF({M}>={x},"回本","未回本")'
    ws[f"P{r}"].value = (
        f'=IF(AND(ISNUMBER({D}),ISNUMBER({I}),ISNUMBER({M})),IF({I}>0,'
        f'IF(ABS({D}/{I}-1)<=0.1,'
        f'"字面讀法為主："&{verdict(D)}&"（L_total "&TEXT({M},"0.00")&" 對所需 L "&TEXT({D},"0.00")&"）；恆等式讀法 "&TEXT({I},"0.00")&" 並列；兩種讀法差 "&TEXT({D}/{I},"0.00")&" 倍（≤10%），來源見 2-4 報告",'
        f'"恆等式讀法為主："&{verdict(I)}&"（L_total "&TEXT({M},"0.00")&" 對所需 L "&TEXT({I},"0.00")&"）；字面讀法 "&TEXT({D},"0.00")&"（"&{verdict(D)}&"）並列；兩種讀法差 "&TEXT({D}/{I},"0.0")&" 倍，來源見 2-4 報告"),'
        f'"所需 L 為 0"),'
        f'IF(AND(ISNUMBER({D}),ISNUMBER({M})),IF({M}>={D},"回本（L_total 口徑，字面讀法）：L_total "&TEXT({M},"0.00")&" ≥ 所需 L "&TEXT({D},"0.00"),'
        f'"未回本（L_total 口徑，字面讀法）：L_total "&TEXT({M},"0.00")&" < 所需 L "&TEXT({D},"0.00")),"推算值非數字（本情境）"))')
    return [r]


# ================================================================== Decisions (10 columns; layout of v800)
_D = [
    ("M1", "快取命中進產能（D9）", "Perf、Sens_Perf 與 _Prod 鏡像頁的 prefill 計算量與時間只計新鮮輸入 ISL × (1 − B4_CacheHit)：TTFT（第 76 列）、每請求 GPU 秒（第 93 列）、prefill GPU 占比（第 94 列）。"
     "IF_TokGW_* 計入的 token 定義不變（每請求 ISL＋OSL，快取輸入仍算作已服務的 token，以快取價計價）；快取輸入的讀取成本維持在成本端（Cache_Store、Perf 第 102 列），不重複計入。"
     "Perf_Batch（RL rollout、蒸餾等批次推論，Training 頁讀它）維持全 ISL：工作單另規定 Training 全部數值不得變，兩者衝突時取後者；批次推論無對外服務的快取命中率（B4_CacheHit 是對外參考請求的值）。"
     "prefill 平均位置（第 46 列＝ISL ÷ 2）不隨快取調整（新鮮 token 實際位置在 ISL 後段，平均注意跨度略大；影響為二階，列待 Project 判斷）。"
     "基準下 Hopper Astra 的 TTFT 6.08 s → 2.74 s，恢復可達；IF_TokGW_* 全部上升。情境 d9_cache_cap_off（B4_CacheHit＝0）的產能端與 v8.0 一致。",
     "Perf／Sens_Perf／_Prod 第 76、93、94 列（perf.py）；Perf_Batch 不變", "v9.0 已建"),
    ("M2", "免費占比統一口徑（D9）", "乘在 token 上的占比一律用 token 口徑、乘在支出（或 GW）上的占比用支出口徑。逐格判斷：Cap_In 第 87 列（外部 Epoch token × 付費占比）原用支出口徑 IF_FreeShare（0.46），改用 token 口徑 1 − AL_FreeShare（0.4）；"
     "Cap_In 第 113 列（r 的支出口徑換算）本來就是把支出占比經付費產能倍數換成 token 比，口徑正確，不改；Fleet_1GW 第 11、12 列與 Sens_Rev F14／F15 乘的是 GW 或營收占比，口徑正確，不改。"
     "AL_FreeShare（0.6）是 ChatGPT token 中免費用戶占比，Epoch 為前沿實驗室總量（含 API）——全體適用與否列待 Project 判斷。",
     "Cap_In 第 87、88、97 列；L1_MImplied_Ext", "v9.0 已建"),
    ("M3", "κ 套到價格端（D9）", "Cap_In 第 90 列（2026 混合有效單價）與 CAP_Price25Mix（2025）乘上 AL_Kappa（C、D、E 三欄同乘 AL_Kappa，價格區間不與 κ 區間交叉）；基準 κ＝1，基準值不變。"
     "機隊口徑單價 AL_PriceFleet25／AL_PriceFleet 未乘 κ（工作單只列前兩者），κ 情境下機隊 m 的價格端仍不隨 κ；乘或除 κ 的方向亦列待 Project 判斷（κ＝每 GPU 秒總 token 比；token 多的流量單價通常較低）。",
     "Cap_In 第 90 列；Cap_In M 節 CAP_Price25Mix", "v9.0 已建"),
    ("M4", "IF_AmortRev_* 分母改付費 token（第 1 批遺留）", "Amortize 第 44、46、48 列（及 Amortize_Prod 同列）的分母由「付費＋免費 token」改為該層級付費 token，與 D11 的 BU 分母一致；總額（由上而下年化總額）與營收權重不變。",
     "Amortize 第 44、46、48 列；IF_AmortRev_Luna／Sol／Astra", "v9.0 已建"),
    ("M5", "回本判讀的讀法", "L1_LReqFleet（字面讀法：L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate × m））與 L1_LReqFleet_Id（恆等式讀法：支出路線服務 GW 的持有成本 ÷ 營收）並列。"
     "M1–M4 後兩者仍差約 2.7 倍（>10%），判讀欄（L1 P 欄）改以恆等式讀法為主、字面讀法並列並寫明差幾倍；兩者相差 ≤10% 時自動改以字面讀法為主。差距來源見 2-4 報告第 5 節。",
     "L1!P（L1_LReqFleet 列）", "v9.0 已建"),
    ("M6", "2-3 口徑後續（D2、D14）", "需求路線的 m（Cap_In H5 的 L1_MImplied／L1_MImplied_Ext 與 H8 的 L1_MAPI／MSub／MSeat，含非文字扣除與「必須為真」顯示列）改用 2025 年度混合有效單價 CAP_Price25Mix；Cap_In 第 241 列（m＝L1_MAPI 的所需 L）改讀 L1_FleetBreakeven2025；"
     "IF_AllocQ1_R2 的服務 GW 改支出路線，免費服務 GW＝服務 GW × AL_FreeSpendShare；L1_ExtServeGW 改回「模型主口徑（支出路線）對外部」，token 路線另見 IF_AllocServeGW_Tok／L1_ScaleServe；"
     "價格區間（_Lo／_Hi）不交叉進 m 的低／高（與世代價格 B 段的不交叉組合一致）。注意：L1_ExtServeGW 的主口徑與外部對照同源，比值恆為 1，不再是獨立檢驗。",
     "Cap_In H5／H8／I-7；Alloc 第 57 列；Interface 第 196 列；L1_ExtServeGW", "v9.0 已建"),
    ("M7", "文字旗標與契約文件", "文字旗標字樣依成因保留「SLO 不可達」「TTFT 不可達」「整代不可達」；下游契約第 2 節第 2 條改寫為『凡文字＝不可用，下游以是否為數字判斷，不以字串比對』；契約第 5 節補 v6.2、v6.3、v8.0、v9.0 條目；"
     "過渡別名 IF_RevGWFleet_Life、IF_RevGW_*_Life 延後到下游同步（Andy 跑完 CoreWeave）之後的第一個主版刪除。",
     "docs/plan/Tokenomics_downstream_contract.md", "v9.0 已建"),
]
DECISIONS_V810 = [[f"AF2e-{i}", V, f"稽核修正第 2 批 2-4：{t}", txt, DATE, CHAT_DEF, st, where, f"{WO} {i}", "否"] for i, t, txt, where, st in _D]

# ================================================================== README
README_VERSION = (VERSION + "（主版：稽核修正第 2 批 2-4 段，" + WO + "——D9：快取命中進產能（Perf／Sens_Perf／_Prod 的 prefill 只計新鮮輸入；Perf_Batch 不變）、免費占比 token 口徑（Cap_In 第 87 列）、"
                  "κ 套到價格端（Cap_In 第 90 列、CAP_Price25Mix）、IF_AmortRev_* 分母改付費 token；2-3 後續：需求路線 m 與 Cap_In 第 241 列改 2025 口徑、IF_AllocQ1_R2 改支出路線、"
                  "L1_ExtServeGW 改回主口徑、L1_LReqFleet 判讀以恆等式讀法為主；Decisions AF2e-*）。以下為 " + v800.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v800.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v800.VERSION.split("_")[-1]):]
README_ROW = ("D9 快取進產能與 2-3 後續（v9.0）",
              "稽核修正 2-4：快取命中進產能（IF_TokGW_* 全部上升，Hopper Astra 恢復可達）；免費占比、κ、攤提分母同口徑；需求路線 m 與回本比較用 2025 口徑；"
              "回本判讀以恆等式讀法為主、字面讀法並列。標記與理由見 Decisions AF2e-*。")

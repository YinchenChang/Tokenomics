"""4-3 A 段逐列處置表（人工判斷，依 v13.1 列的內容、下游契約、L1 名稱表、已知問題清單）。
輸出 DEC：{(頁, 列): dict(act, q, name, why, andy, attach)}。act 取值：
  升級／升級（隨附上游）／保留：顯示用／接進 Checks／刪除／需 Andy 判斷
q＝工作單『已知問題清單』編號（1–11），— 表示不回答任何一題。andy＝是／否（定義見工作單第 2 節）。"""

LB_PAGES = {"Workload", "Calib", "Serving", "Train_In", "Spec_Rack", "Alloc_In", "Arch", "Cap_In"}   # Load_Bearing 有登錄的頁
DEC = {}


def put(sheet, rows, act, q, why, name="", andy=None, attach=False):
    for r in ([rows] if isinstance(rows, int) else rows):
        a = andy
        if a is None:
            a = "是" if (act == "刪除" and sheet in LB_PAGES) or (act == "升級") or act == "需 Andy 判斷" else "否"
        DEC[(sheet, r)] = dict(act=act, q=q, name=name, why=why, andy=a)


KEEP = "保留：顯示用"
UP = "升級"
UPA = "升級（隨附上游）"
CHK = "接進 Checks"
DEL = "刪除"
ASK = "需 Andy 判斷"

# ---------------- Spec_Rack／Arch／Serving／Workload／Tech_Registry ----------------
put("Spec_Rack", 28, KEEP, "—", "規格表列（Scale-up 域 GPU 數＝SRC_HW_053，Gov_Map 登錄）；刪除會讓 Gov_Map 登錄落空（原則 4 治理材料不刪）。補『用途』標記。")
put("Spec_Rack", 36, KEEP, "—", "roofline 推導鏈的讀數（ridge point＝峰值÷頻寬；建模精神 1a 要求露出推導鏈）；同表其他列是核心格。")
put("Arch", 15, KEEP, "—", "架構規格列（vocab＝SRC_MOD_014，Gov_Map 登錄）；刪除會讓 Gov_Map 登錄落空。補『用途』標記。")
put("Arch", 26, DEL, "—", "Embedding＋LM head 參數：只由 vocab 推出、無任何下游、不回答任何一題；非專家參數另由第 28 列推導。Arch 為承重頁，刪除需 Andy 確認。")
put("Arch", 31, DEL, "—", "128K 上下文每序列 KV：衍生診斷，無下游；Perf 用 KV bytes/token 自行乘上下文長度（單一定義在 Perf）。Arch 為承重頁，需 Andy 確認。")
put("Serving", 25, DEL, "—", "decode 平均上下文＝ISL＋OSL/2：與 Perf 第 45 列同式（Perf 才是被取用者）；原則 1 同一定義只存一處。Serving 為承重頁，需 Andy 確認。")
put("Serving", 26, DEL, "—", "prefill 平均位置＝ISL/2：與 Perf 第 46 列同式。同上。")
put("Workload", 17, DEL, "—", "harness 混合權重 w 的顯示複本（＝B5_W＝IF_HarW 已具名輸出）；原則 1。Workload 為承重頁，需 Andy 確認。")
put("Workload", 36, DEL, "—", "任務 decode 平均上下文：無下游，Perf 不讀 Workload 的上下文；不回答任何一題。需 Andy 確認（承重頁）。")
put("Workload", 37, DEL, "—", "思考占 decode：衍生比例，可由 Workload 第 19 與 9 列推得；無下游。需 Andy 確認（承重頁）。")
put("Workload", 38, UP, "9", "各任務總 token ÷ 一般聊天＝harness 與 agent 用量對 token 的放大倍數（本模型 1／2.07／9.2／36.8／498 對 Anthropic 揭露 4／15，第 40 列已標對照）。目前下游只能自行加總 IF_TaskTok* 再相除。",
    name="IF_TaskTokMult")
put("Workload", 39, DEL, "—", "總 token ÷ 推理聊天：第 38 列換一個分母，沒有獨立資訊。需 Andy 確認（承重頁）。")
put("Workload", range(43, 49), DEL, "—", "每任務服務成本（VR200／GB300 × 三層級，不含快取儲存）：Harness 第 67–84 列已有含儲存的現行版，且 IF_CostSuccVR／GB_* 已具名；此為較舊的簡化版，原則 1。Theory_Rev 第 81–86 列隨之刪除。需 Andy 確認（承重頁）。")
put("Tech_Registry", 30, KEEP, "—", "掛鉤彙總表（E20–E29 是核心格）的形狀；H_HAR 的實際作用在 Workload 的 B5_W（T12 開關），此格為同表一致的彙總讀數。")

# ---------------- Perf（鏡像：Perf_Batch、Perf_Prod、Sens_Perf 同構）----------------
put("Perf", [73, 91], KEEP, "—", "記憶體配置（E 節）的讀數：權重／KV 占可用 HBM；建模精神 1a 的推導鏈；與 Perf_Batch 同列鏡像（D13 常設測試），刪單邊會使鏡像測試失敗。")
put("Perf", 89, CHK, "—", "實際每用戶速度須 ≥ Serving SLO（B* 取 SLO 與 HBM 上限的較小者，故恆成立；程式或輸入出錯時才會失敗）。屬驗證材料，可寫成能失敗的檢查（原則 4）。Perf 與 Perf_Batch 合為一條檢查。")
put("Perf", 94, KEEP, "—", "P:D 配比（prefill GPU 占比，內部名稱 DRV_PreShare）：每架產出推導鏈的讀數；Perf 第 118 列讀它；與 Perf_Batch 鏡像。")
put("Perf", 99, KEEP, "5", "每 GW decode 產出：token 類型拆分的讀數（IF_TokRackD_* 具名、IF_RacksPerGW 具名，下游可相乘）；因與 Perf_Batch 第 99 列鏡像（D13），單邊刪除會破壞鏡像測試，故保留。")
put("Perf", 118, KEEP, "—", "每 decode token 實際能量（平均用電口徑）：能量閉合（J 節）的讀數；與 Perf_Batch 鏡像。")

# ---------------- Unit_Cost／DC_Cost ----------------
put("Unit_Cost", [23, 36, 49], DEL, "6", "『參考請求混合 $/M 總 token（經濟、100%）』：混合數字，Amortize 第 14／23／33 列已有含快取儲存的『參考請求混合服務成本』（IF_FullCost* 的基礎），單價的唯一定義在那裡（原則 1）；三層級分項成本 IF_CostPre／CostDec／CostCache 已具名。")
put("DC_Cost", [34, 35], DEL, "5", "每 GPU／每 MW IT 資本支出：IF_CapexTotal、IF_CapexIT（每 GW）、IF_GPUsPerGW 已具名，單位換算即得（1 $B/GW＝1 $M/MW）；L1_CapexGW_*、L1_CapexITMW_GB300_vsIREN 已有答案。")
put("DC_Cost", [59, 60], DEL, "—", "每架小時持有成本、年用電（設施端）：可由 IF_HoldEcon／IF_RacksPerGW、IF_AvgDraw 推得，不回答已知問題；IF_PowerCost 已具名（用電成本）。")
put("DC_Cost", [61, 62], KEEP, "5", "成本結構讀數（資本回收占經濟口徑、電費占經濟口徑）：同節第 57–58 列為核心格；供人讀取成本組成，下游以 IF_Depr*／IF_PowerCost 自算。")

# ---------------- Train_In ----------------
put("Train_In", [44, 45], KEEP, "8", "RL 占比的外部對照（DeepSeek R1 RL 為 V3 預訓練 0.055、Grok 4 宣稱 1.0）；Gov_Map 登錄，Checks 第 157–158 列已拿模型 RL 占比對外部。Train_In 為承重頁，不刪。", name="")

# ---------------- Perf_Batch（鏡像 Perf；D13）----------------
PB_WHY = "與 Perf 逐列鏡像（D13；test_perf_batch_differs_only_on_whitelist_rows 以 Perf 為準逐格比對）：批次引擎沿用同一條推導鏈，Training 只取其中幾列，其餘列不進輸出但屬鏡像形狀；刪除須連同 Perf／Perf_Prod 同列並改白名單，收益小。補『用途』標記。"
put("Perf_Batch", 12, KEEP, "—", "R–S 欄（VR200 以 FP8 rollout 的未接線情境，4-0 R04）該列的 H_WB 讀取；其餘 R–S 列已標『情境對照（未接線）』，此列補齊同一標記。")
put("Perf_Batch", [22, 23, 24, 25, 26, 62, 73, 84, 90, 91, 93, 94, 95, 96, 97, 98, 99, 102], KEEP, "—", PB_WHY)
put("Perf_Batch", 89, CHK, "—", "實際每用戶速度須 ≥ 速度下限；與 Perf 第 89 列合為一條檢查（見該列）。")
put("Perf_Batch", list(range(107, 119)), KEEP, "—", "能量閉合（J 節）的逐步讀數；Perf_Batch 的能量閉合不進 Checks（Checks B26 只讀 Perf 第 116 列）。" + PB_WHY)
put("Perf_Batch", [120, 121], KEEP, "8", "Perf_Batch 專屬閱讀列（D13 白名單）：decode 有效 MFU（對 Perf 峰值／對 FP8 訓練峰值），用來解讀 IF_RLMFU_*（RL 有效 MFU 只有幾 %）為何偏低。")

# ---------------- Training ----------------
put("Training", [19, 20], DEL, "—", "每 GPU 小時持有成本（基準成本）：Interface 已有 IF_GPUhrEcon（具名）與 L1_GPUhr_*；此兩列只供下列已刪除的成本列使用。")
put("Training", 79, KEEP, "8", "RL ÷ 預訓練（FLOPs 口徑，內部名稱 TRN_RLRatioF）：與 GPU 小時口徑（TRN_RLRatioH＝第 78 列，已進 L1_RLshare_*）並列的對照；Grok 4 宣稱值（Train_In 第 45 列）為算力口徑，需此列對照。")
put("Training", 96, UPA, "8", "合成資料 FLOPs 的上游（生成層級 decode FLOPs/token）；隨 Training 第 109 列升級而成為核心。")
put("Training", [98, 101], UPA, "8", "最終訓練 FLOPs（第 109 列）的加項（合成資料、評測）；隨第 109 列升級而成為核心。")
put("Training", 109, UP, "8", "最終訓練 FLOPs（預訓練＋長上下文＋後訓練＋合成資料＋評測）：『訓練一個模型要多少算力』的 FLOPs 表達；Epoch 的 Astra 估計（L1_PretrainFLOP_Astra_Ext）為含後訓練的叢集總算力，需同口徑的模型端對照（現有 L1_PretrainFLOP_Astra 只含預訓練）。",
    name="IF_TrainFLOP_Luna／_Sol／_Astra")
put("Training", 112, UPA, "8", "推論型 GPU 小時：第 114 列『推論型占最終訓練』的分子；隨第 114 列升級。")
put("Training", 113, DEL, "—", "反向傳播型 GPU 小時＝最終訓練 − 推論型（IF_TrainGPUh_* 減第 112 列）；可推得，無下游。")
put("Training", 114, UP, "8", "推論型（rollout、合成資料、評測、蒸餾教師）占最終訓練 GPU 小時 0.62：『訓練 GPU 小時主要是推論還是反向傳播』是 J11 的設計輸出，屬訓練構成（問 8 同類）；目前只有內部名稱 TRN_InferShare。",
    name="IF_TrainInferShare_Luna／_Sol／_Astra")
put("Training", 115, DEL, "8", "最終訓練成本（經濟）：IF_TrainCost_* 已具名（Interface 第 55／64／73 列依成本情境重算）；原則 1。")
put("Training", 116, DEL, "—", "最終訓練成本（會計口徑）：不回答已知問題，經濟口徑才是下游取用口徑。")
put("Training", 121, KEEP, "8", "『其中：研發實驗（型態未拆分）』：K 節用途×型態表（第 125–129 列）的上游；K 節保留（見該列）。")
put("Training", 122, DEL, "3", "研發計畫成本（經濟）：IF_ProgCost_* 已具名；原則 1。家族成本列（第 133 列）隨之刪除。")
put("Training", [125, 126, 127, 128, 129], KEEP, "8", "K 節『用途×型態』GPU 小時表（預訓練／後訓練推論型／後訓練反向傳播型／合成資料與評測／研發實驗）：J11 的設計輸出，表的各列合計等於 IF_TrainGPUh 與 IF_ProgGPUh（具名）；為表的形狀整體保留，下游以 IF_ 名稱取總量。")
put("Training", [131, 132, 133, 134], DEL, "3", "模型家族合計（三層級加總）：IF_TrainGPUh_*／IF_ProgGPUh_*／IF_ProgCost_*／IF_ProgGWyr_* 皆已具名，加總即得；第 134 列與 Fleet_1GW 第 33 列同值（原則 1）。")

# ---------------- Cap_In ----------------
put("Cap_In", [71, 72, 73], KEEP, "1", "H1 營收二分（訂閱／API）：第 96 列（外部 token 的 API 路線 m，已標用途）與 J11 非文字對照（第 128、129 列）的分子；與 H8-1 三分法（第 135–137 列）口徑不同（舊法把席次算入訂閱），兩者並存是設計（H5 表列出多個 m 讀法）。")
put("Cap_In", [75, 76, 77, 78, 79], KEEP, "1", "H2 訂閱人數（SRC_DEM_024／025／026／019 的複本與 2025 期間平均）：訂閱 m 的每人直覺檢查（第 84 列）與 ARPU（第 161 列）的上游，Gov_Map 登錄；J6 設計。")
put("Cap_In", [92, 93], KEEP, "1", "H5 兩路線隱含 m（模型 token；訂閱 3.73／API 0.99）：H5 表的形狀（第 94、97 列為核心 L1_MImplied／MImplied_Ext，第 96 列已標用途），且是 J11 非文字對照（第 128 列）的基礎；主口徑為 H8-3 三分法（L1_MSub／MAPI／MSeat），此兩列為 v5.32 舊分法的對照，標明口徑。")
put("Cap_In", [99, 101], KEEP, "1", "H6 程式代理對照鏈（Claude Code 企業平均花費、每開發者每月列價用量）：第 103 列『程式代理訂閱 m』對照的上游。")
put("Cap_In", [109, 116, 118, 119], KEEP, "—", "說明欄的動態文字公式（以 TEXT() 帶出現值，取代寫死的過時數字；4-0 SL13／SL14 的修法）；屬原則 2。")
put("Cap_In", 121, UP, "1", "m 下限（上限讀法）0.301：『m 不可能低於此值』的物理下界，目前只出現在說明文字。注意 L1_MFleet_Lo（0.184）低於這個下限，兩者的區間定義不同（前者含 τ 區間），升級後下游才看得到這個衝突。",
    name="L1_MFleetFloor（含 _Lo／_Hi）")
put("Cap_In", [123, 124, 125], KEEP, "1", "『必須為真』補列（m＝1／0.6／0.3 所需付費 token）：Andy 要求的反向檢查，對照機隊 token 判斷 m 是否可能；v5.33 B3。")
put("Cap_In", [128, 129], KEEP, "1", "J11 非文字服務份額對照（訂閱 m 扣除非文字後 3.36、合併 1.89）：敏感度讀數，Assumed 0.05／0.10／0.20 的影響。")
put("Cap_In", 138, DEL, "1", "API 占比（顯示）：與 H10-1 第 190 列、H8-1 第 137 列÷第 69 列同義；原則 1。需 Andy 確認（承重頁）。")
put("Cap_In", 147, CHK, "1", "m_整體（token 加權）須等於 L1_MImplied（第 94 列）：第 148 列已有『自我檢查』但只顯示、不進 Checks；寫成 Checks 的能失敗檢查（容差 1e-9）。")
put("Cap_In", [161, 162], KEEP, "1", "H8-6 『必須為真』補列（訂閱 ARPU 279 $/人·年；m_訂閱＝1 需每訂閱者年 token 166）：與第 84 列、第 164 列並列的每人檢查。")
put("Cap_In", 173, KEEP, "4", "H9 token 帳三路線（需求／支出／上限）的上限路線：與 L1_TokCeiling 同值，但為三路線表的形狀（第 171–172 列已標用途），並供第 175 列。")
put("Cap_In", 175, CHK, "4", "殘差：需求 ÷ 上限須 ≤ 1（需求 token 不可能超過機隊有效產能上限；現值 0.148）。現有 Checks M4 只檢查需求÷點估計（0.5–2 之外為 WARN）；上限讀法可寫成必然失敗的檢查。G175 為說明文字（同類動態文字，保留）。")
put("Cap_In", 176, KEEP, "10", "閉合解標題的動態文字（以 TEXT() 帶出 τ* 現值，取代過時的 13,950；4-0 SL07 的修法）。")
put("Cap_In", [185, 187, 188, 189, 190, 191, 192, 193, 196, 197, 198, 199, 200, 201, 202, 205, 216, 217, 218, 219, 220, 221, 222], UPA, "1",
    "H10 m 季度序列（2025／2026 Q1／Q2／FY2026）的分子、分母、單價與機隊 token 推導；隨第 206–209、223 列升級為 L1_M*_Ser 後成為核心。")
put("Cap_In", 204, DEL, "—", "L_price 逐期複本（四欄都等於第 232 列；『顯示用，不進 m』）；L1_LPrice 已具名；原則 1。需 Andy 確認（承重頁）。")
put("Cap_In", 206, UP, "1", "m_API 的季度序列（2025 0.66／2026 Q1 0.29／Q2 0.34／FY 0.35）：『m 是多少、由哪些分項組成』的時間序列，目前 L1_MAPI 只有 2025 單點。", name="L1_MAPI_Ser")
put("Cap_In", 207, UP, "1", "m_消費訂閱的季度序列。", name="L1_MSub_Ser")
put("Cap_In", 208, UP, "1", "m_商用席次的季度序列（FY2026 8.04，席次占比與 token 份額為 Assumed）。", name="L1_MSeat_Ser")
put("Cap_In", 209, UP, "1", "m_整體（合併）的季度序列。", name="L1_MImplied_Ser")
put("Cap_In", 215, CHK, "—", "2026 服務世代組合合計須為 100%（D–F 欄是藍字輸入，可能被改壞）；寫成 Checks 的能失敗檢查，與 Checks D104（Alloc_In 2025 組合）並列。")
put("Cap_In", 223, UP, "1", "m_fleet（機隊口徑）的季度序列（2025 0.41／2026 Q1 0.20／Q2 0.23／FY 0.30）：問 1『由哪些分項組成』中的機隊項，目前 L1_MFleet 只有 2025 單點。", name="L1_MFleet_Ser")
put("Cap_In", 231, DEL, "—", "k＝LN(1＋g)：中間量；第 232 列的 L_price 公式自帶 LN，沒有讀它。需 Andy 確認（承重頁）。")
put("Cap_In", 240, KEEP, "2", "說明欄動態文字（現值取代過時的 0.530；4-0 SL11 的修法）。")
put("Cap_In", 241, KEEP, "2", "I-7 『必須為真』：回本所需 L 以 m＝L1_MAPI 計（1.25，另有 D／E 欄 m 高低端）；第 243 列判讀讀它。契約已定回本結論取恆等式讀法 L1_LReqFleet_Id，第三種讀法不升級，留作對照。")
put("Cap_In", 245, DEL, "—", "請求形狀修正 κ 的複本（＝AL_Kappa；L1_GapISL＝1÷κ 已具名）；原則 1。需 Andy 確認（承重頁）。")
put("Cap_In", 255, KEEP, "4", "缺口恆等式的說明動態文字（現值取代過時的 2.207；4-0 SL12）。")
put("Cap_In", 269, KEEP, "4", "機隊口徑單價 ÷ 完整層級組合單價（D10 的保留處；Alloc 側已合併）：顯示排除不可達層級對單價的影響（<1＝被排除層級單價較高）。")
put("Cap_In", 282, DEL, "—", "2025 混合有效單價 ÷ 2026 快照：L1_Price25Mix（具名）與第 90 列相除即得。需 Andy 確認（承重頁）。")
put("Cap_In", 284, KEEP, "1", "說明動態文字（v7.0 歷史值標示為歷史，現值隨公式）。")
put("Cap_In", 285, UP, "1", "m 以 2025 單價低端計（0.78，D／E 欄為 τ 區間端點）。契約第 4 節明定『價格區間不交叉進 m 的 _Lo／_Hi』，所以價格不確定性造成的 m 範圍（0.24–0.78）目前下游完全看不到。", name="L1_MFleet_P25Lo")
put("Cap_In", 286, UP, "1", "m 以 2025 單價高端計（0.24）。同上。", name="L1_MFleet_P25Hi")
put("Cap_In", 288, KEEP, "2", "說明動態文字（現值取代過時的 0.5304；4-0 SL11）。")

# ---------------- Price_Frontier／Cache_Store ----------------
put("Price_Frontier", 23, DEL, "—", "層級能力門檻複本（＝第 6–8 列）：第 24 列以 INDEX 自取，沒有讀它。")
put("Price_Frontier", [27, 28, 29], KEEP, "6", "前緣模型的新鮮輸入／快取輸入／輸出分項牌價（表列、時段加權）：B 節前緣表的形狀（第 24–26 列是核心格），按 token 類型的前緣單價；下游以 IF_FrontRef_*（混合）取用。")
put("Price_Frontier", 30, DEL, "7", "OpenAI 溢價（OpenAI ÷ 前緣）：L1_Ans7 已答 Sol，IF_PriceRef_*／IF_FrontRef_* 皆具名，其餘層級相除即得。")
put("Price_Frontier", [32, 34], KEEP, "11", "中國廠商合格者最低（模型名、合格家數）：與已標用途的第 31、33 列同一組對照讀數。")
put("Cache_Store", [18, 19, 24, 25, 30, 31], DEL, "6", "儲存成本 ÷ 快取命中載入成本、÷ OpenAI 快取輸入有效價：IF_CacheStore_*、IF_CostCache_*、IF_PriceCached_* 皆已具名，相除即得；不回答已知問題。")

# ---------------- Fleet_1GW／Amortize ----------------
put("Fleet_1GW", [14, 15], KEEP, "3", "A 節用途配置（最終訓練、研發實驗各占 1 GW 多少）：與第 10–13 列同表（服務／訓練＋研發是核心格）；研發占總算力的參考機隊讀數（B4_Serve、IF_RDMult 皆具名）。")
put("Fleet_1GW", 43, KEEP, "—", "排除層級（SLO 不可達者）的文字讀數：D 節可達旗標（核心）的人讀摘要；稽核修正 2 引用。")
put("Amortize", [16, 25, 35], KEEP, "2", "由上而下 ÷ 自下而上攤提：K6 並列兩種攤提口徑的比值（3.1／4.2／0.86），是選預設口徑 (c) 的依據，稽核修正 2-1b 引用。")
put("Amortize", [26, 36], KEEP, "2", "回本所需溢價 ÷ 觀測層級價差：層級版的回本讀數（<1＝觀測價差足以回本）；IF_AmortBU_* 與 IF_PriceRef_* 皆具名，下游可自算。")
put("Amortize", 49, UP, "2", "(d) 攤提占付費營收 0.60：訓練攤提吃掉付費營收多少，是『回本嗎』在營收側的直接讀法（各層級相同，故為合計口徑）。目前下游只能自行用 IF_AmortRev_* 與營收相除。", name="IF_AmortRevShare")

# ---------------- Theory_Rev ----------------
put("Theory_Rev", [13, 31, 49], DEL, "5", "『理論營收 — 100% 利用率（OpenAI）』：Interface 的 IFW_RevGW_*_100（＝第 11／29／47 列 ÷ IF_Util）已是同一量的唯一定義（契約第 2 條要求下游取四層瀑布）；原則 1。")
put("Theory_Rev", [14, 32, 50], KEEP, "5", "年持有成本複本（IF_HoldEcon）：同表『營收 ÷ 持有成本』比值列（15／16、33／34、51／52）的分母。B 段可改讓比值列直接讀 IF_HoldEcon 再刪此三列。")
put("Theory_Rev", 72, KEEP, "5", "整個 GW 年持有成本複本：第 73 列（已標用途）的分母。")
put("Theory_Rev", [15, 16, 34, 51, 52], KEEP, "5", "理論營收（OpenAI／前緣單價）÷ 持有成本：與已標用途的第 33、73 列同一族（回本讀數）；IF_RevGW_*／IF_HoldEcon 皆具名。")
put("Theory_Rev", [19, 37, 55], KEEP, "5", "全成本 $/M（服務＋由上而下攤提）：K6 三口徑並列中非預設的一支（BU＝IF_FullCost_*、預設＝IF_FullCostDefault_*），稽核修正 1 引用。")
put("Theory_Rev", [22, 23, 25, 40, 41, 43, 58, 59, 61], KEEP, "5", "理論毛利率的非預設口徑（自下而上、由上而下、前緣單價）：K6 並列比較，稽核修正 1 引用；預設口徑另升級為 IF_GMDefault_*。")
put("Theory_Rev", 24, UP, "5", "理論毛利率（OpenAI 單價；K6 預設 (c) 全成本）：問 5『毛利，分世代與層級』的預設口徑；目前只有 L1_Ans5_FullMargin 一個格（Sol、VR200）。",
    name="IF_GMDefault_Luna")
put("Theory_Rev", 42, UP, "5", "同上（Sol）。", name="IF_GMDefault_Sol")
put("Theory_Rev", 60, UP, "5", "同上（Astra）。", name="IF_GMDefault_Astra")
put("Theory_Rev", 74, DEL, "6", "服務 token 加權平均有效單價：跨層級混合、不帶層級與 token 類型標籤，違反 CLAUDE.md 第 1a 節『沒有層級的單一混合數字不得作為輸出』；也沒有下游。")
put("Theory_Rev", [78, 79, 80], DEL, "9", "每任務營收（Luna／Sol／Astra）：Harness 第 116–124 列（每次嘗試營收）與 IF_RevSucc_*（每成功任務營收）已涵蓋；原則 1。")
put("Theory_Rev", range(81, 87), DEL, "9", "每任務營收 ÷ 服務成本：兩個分量（Theory_Rev 第 78–80 列、Workload 第 43–48 列）皆為重複的舊簡化版，隨之刪除；Harness 的 IF_RevSucc_*／IF_CostSucc*_* 已具名，相除即得。")

# ---------------- Har_In／Harness ----------------
put("Har_In", 44, ASK, "9", "『供應商專屬（1＝是）』（內部名稱 B5_SelVendor）沒有任何公式讀取，但 Harness 第 157 列說明稱『選定檔案供應商專屬時，前緣組合綁定該…』。若說明為真，這是未接線的功能（應接進前緣列）；若功能已放棄，應刪除此列與說明。")
put("Har_In", 52, KEEP, "—", "任務名稱欄頭（＝Workload 第 4 列）：讓 C 節成功率表能讀；欄頭標籤。")
put("Har_In", [73, 74, 75], KEEP, "11", "E 節證據點中非中立方或非同條件者（Claude Opus 5 標準／Nvidia 所建 harness；Anthropic 多代理 3.75 倍）：L7 明訂只作對照，同表第 70–72 列為核心；Gov_Map／SRC 登錄。")
put("Harness", 44, DEL, "9", "任務總 token（現行）複本（＝Workload 第 35 列）：只供下列『每成功任務 token』列使用，IF_TaskTok* 已具名。")


put("Harness", list(range(105, 114)), DEL, "9", "每成功任務 token（標準／現行／選定 × 三層級）＝任務總 token ÷ 成功率；IF_TaskTok*、IF_TaskSucc_*、IF_TaskSuccSel_* 皆已具名，相除即得。")
put("Harness", [116, 118, 119, 121, 122, 124], DEL, "9", "每次嘗試營收（標準／選定）：現行版（第 117／120／123 列）已進 IF_RevSucc_*；標準／選定版沒有下游。")
put("Harness", [125, 127, 128, 130, 131, 133], DEL, "9", "每成功任務營收（標準／選定）：同上。")

put("Harness", [142, 143, 144], DEL, "9", "成功率比（選定 ÷ 標準）：IF_TaskSuccSel_*／IF_TaskSucc_* 皆已具名，相除即得。")


# ---------------- Alloc_In／L1 ----------------
put("Alloc_In", 18, CHK, "3", "服務世代組合合計（應為 100%）：Checks D104 目前自行重算 SUM(AL_MixGen)；改讓 Checks 讀本格，單一定義（原則 1）且保留失敗能力。")
put("Alloc_In", 33, CHK, "3", "研發世代組合合計（應為 100%）：Checks D140 目前自行重算四格和；改讓 Checks 讀本格。")
put("L1", [52, 68, 69, 71, 102], KEEP, "—", "說明欄的動態文字公式（以 TEXT() 帶出現值；4-0 SL01–SL04、SL10 的修法）；屬原則 2。")

# GB300 孿生區塊（與 VR200 區塊同構；第 149–150 列『對照（不設下限）GB300 最低成本』已標用途且讀取這些列，故上游不能刪）
put("Harness", [76, 78, 79, 81, 82, 84, 96, 98, 99, 101, 102, 104, 139, 140, 141, 154, 155, 156], KEEP, "9",
    "GB300 孿生區塊（每次嘗試成本、每成功任務成本、選定÷標準的 R、前緣）：與 VR200 區塊（IF_HarR_*、L1_Ans8／9 取用）同構；第 149–150 列已標用途並讀取這些列，上游不能單獨刪。下游取 GB300 的現行列（IF_CostSuccGB_*）。")

# ---------------- 覆寫：敏感度頁以『同列同標籤』的核心列為比對基準（test_sens_core_no_undocumented_difference；6b(a)）----------------
SENS_WHY = "敏感度頁（{p}）有同列同標籤的列，常設測試以此核心列為逐格比對基準；刪核心列＝該敏感度列失去比對、變成孤兒定義（6b(a) 敏感度頁保留）。下游已有 {n} 具名輸出，核心列保留並補『用途』標記。"
put("DC_Cost", [34, 35, 59, 60], KEEP, "5", SENS_WHY.format(p="Sensitivity", n="IF_Capex*／IF_HoldEcon／IF_AvgDraw 等"))
put("Training", [19, 20, 113, 115, 116, 122], KEEP, "8", SENS_WHY.format(p="Sens_Train", n="IF_TrainCost_*／IF_ProgCost_*／IF_GPUhrEcon"))

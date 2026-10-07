from common import *
from openpyxl.workbook.defined_name import DefinedName
from outputs import COLS15
import v520
import v521
import v522
import v523
import v524

def interface(wb, PR, U):
    ws = wb["Interface"]
    for r in range(17, 23):
        for c in range(1, 19): ws.cell(row=r, column=c).value = None
    put(ws, "A2", "每一列為一個具名範圍（IF_…），欄＝世代 × 成本情境；Block 2 產出依層級分區（物理量不隨成本情境變動）", F_NOTE)
    put(ws, "A3", v520.X5_NOTE, F_NOTE)     # v5.20 X5: row 3 was empty, no row moves
    section(ws, 17, "B. Block 2 產出（依層級；100%＝理想上限；下游以自身利用率換算）", 17)
    r = 18; names = []
    tiers = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
    for t, (tk, tn) in enumerate(tiers, start=1):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        pl = lambda key: f"=INDEX(Perf!$C${PR[key]}:$Q${PR[key]},3*(Unit_Cost!{{X}}$6-1)+{t})"
        rows = [
          (f"IF_TokRack_{tk}", "每架總 tok/s（參考任務 P:D）", "tok/s", "#,##0", pl("rtot")),
          (f"IF_TokRackD_{tk}", "每架 decode tok/s", "tok/s", "#,##0", pl("rdec")),
          (f"IF_TokGW_{tk}", "每 GW 總產出（100%）", "M tok/年", "#,##0", pl("gwtot")),
          (f"IF_VReq_{tk}", "VR-eq 係數（每 GW 產出 ÷ VR200）", "x", "0.00", pl("vreq")),
          (f"IF_CostPre_{tk}", "新鮮 prefill $/M（經濟、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cf')]}"),
          (f"IF_CostCache_{tk}", "快取命中 prefill $/M（經濟、100%）", "$/M", "#,##0.0000", f"=Unit_Cost!{{X}}{U[(t,'cc')]}"),
          (f"IF_CostDec_{tk}", "decode（含思考 token）$/M（經濟、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cd')]}"),
          (f"IF_CostDecAcct_{tk}", "decode（含思考 token）$/M（會計、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cda')]}"),
          (f"IF_TokPerJ_{tk}", "tokens／焦耳（平均用電口徑）", "tok/J", "#,##0.00", pl("tpj")),
        ]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for X in COLS15:
                put(ws, f"{X}{r}", tpl.format(X=X), fmt=fmt, fill=FILL_KEY if "CostDec_" in name or "TokGW" in name else None)
            names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "基準利用率（第 0 層；下游可覆寫）　[IF_Util]"); put(ws, f"B{r}", "%")
    put(ws, f"C{r}", "=Serving!$C$17", fmt="0%"); names.append(("IF_Util", f"Interface!$C${r}")); r += 2
    put(ws, f"A{r}", "每 GW 理論營收"); put(ws, f"C{r}", "待 Block 4（Capability、單價前緣）", F_NOTE)
    for n, ref in names:
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    ws.column_dimensions["A"].width = 52
    return names

def checks(wb, CAL, PR, SR, U):
    ws = wb["Checks"]
    section(ws, 12, "Block 2 檢查", 6)
    rows = [
      ("校準：擬合點重現（應為 1.00）", f"=Calib!C{CAL['ratio']}", "1.00", "x", "擬合正確性", "Calib F 節"),
      ("樣本外：GB300 SGLang＋MTP 50 tok/s", f"=Calib!E{CAL['ratio']}", "11,200 實測", "模型÷實測", "±10% 內視為前緣形狀成立", "S21"),
      ("樣本外：GB300 vLLM 無 MTP 27 tok/s", f"=Calib!F{CAL['ratio']}", "6,182 實測", "模型÷實測", "應 >1：舊軟體", "S20"),
      ("樣本外：GB200 vLLM 無 MTP 27 tok/s", f"=Calib!G{CAL['ratio']}", "2,189 實測", "模型÷實測", "應 >1：舊軟體＋記憶體限制配方", "S20"),
      ("樣本外：GB200／GB300 110 tok/s", f"=Calib!H{CAL['ratio']}", "3,795 實測", "模型÷實測", "口徑待查", "S23"),
      ("GB300 Sol 經濟成本 vs InferenceX（72 tok/s，8K/1K）", f"=DC_Cost!J58/(Calib!C{CAL['T']}*3600)*1E6", "0.078", "$/M 總 token", "差異來自每 GPU 小時 TCO（本模型 2.99 對 2.65）", "S22"),
      ("VR200 ÷ GB300 每 GW 產出（Sol 基準）", f"=Sens_Perf!C{SR['rgw']}", "=DC_Cost!M55/DC_Cost!J55", "x", "外部參照欄＝損益兩平（每 GW 持有成本比）；高於此值時 VR200 每 token 較便宜", "Sens_Perf"),
      ("GB300 每 GPU 功率：本模型 IT 平均用電", "=DC_Cost!J11*Inputs!$E$10/72", "2.12", "kW/GPU", "InferenceX 內部常數（GB300 2.12 kW/GPU），非獨立對照：該頁 tok/s/MW＝tok/s/GPU÷此常數（9,506.83÷4,484,352＝2,120 W），由 9,384 與 4.43M 反推 2.12 是循環；常數是否含設施頁面未載明；不作外部驗證（v5.18）", "S22"),
      ("VR200 ÷ GB300 decode $/M（Sol 基準）", f"=Sens_Perf!C{SR['rcost']}", "<1 較便宜", "x", "", "Sens_Perf"),
      ("第二來源：GB300 interactive 模型 ÷ MLPerf（DeepSeek-R1）", f"=Calib!C{CAL['mR']}", "1.00", "x", "<1：本模型低於 MLPerf，InferenceX 校準未比 MLPerf 樂觀", "S31、S32"),
      ("第二來源：VR200 ÷ GB300 模型 對 MLPerf", f"=Calib!C{CAL['mVR']}", f"=Calib!C{CAL['mVRm']}", "x", "兩者接近即支持 VR 沿用 GB300 效率係數", "S32"),
      ("來源衝突：GB300 ÷ GB200 模型 對 MLPerf", f"=Calib!C{CAL['mGB']}", f"=Calib!D{CAL['mGB']}", "x", "InferenceX 1.7–2.8、MLPerf 約 1.05、模型居中", "S20、S31"),
      ("能量閉合：各欄最大閉合比", f"=MAX(Perf!C{PR['close']}:Q{PR['close']})", "≤ 100%", "%", "超過代表產出或能量常數有誤", "Perf J 節"),
      ("SLO 不可達的欄數（15 欄中）", f"=COUNTIF(Perf!C{PR['bind']}:Q{PR['bind']},\"SLO 不可達\")", "—", "欄", "0＝15 欄在 SLO 下皆可達；Hopper × Astra 每 GPU 僅約 25 tok/s，物理上可達但經濟上不可行", "Perf G 節"),
      ("牌價空間：V4-Pro 8K/1K 牌價 ÷ GB300 Sol 成本（基準利用率）", f"=((8*1.32+3.96)/9)/((8*Unit_Cost!J{U[(2,'cfu')]}+Unit_Cost!J{U[(2,'cdu')]})/9)", "—", "x", "DeepSeek V4-Pro API 牌價 $1.32／$3.96（2026-09 價格追蹤站；記錄於 Tokenomics v4 活頁簿預設表）；只說明空間，不代表 DeepSeek 毛利", "S27"),
    ]
    put(ws, "A13", "項目", F_BOLD); put(ws, "B13", "本模型", F_BOLD); put(ws, "C13", "外部參照", F_BOLD)
    put(ws, "D13", "單位", F_BOLD); put(ws, "E13", "判讀", F_BOLD); put(ws, "F13", "來源", F_BOLD)
    for i, (a, b, c, d, e, f) in enumerate(rows):
        r = 14 + i
        put(ws, f"A{r}", a, wrap=True); put(ws, f"B{r}", b, fmt="#,##0.00" if "%" not in d else "0%", fill=FILL_KEY)
        put(ws, f"C{r}", c); put(ws, f"D{r}", d); put(ws, f"E{r}", e, F_NOTE, wrap=True); put(ws, f"F{r}", f, F_NOTE)

def sources(wb):
    ws = wb["Sources_Legacy"]
    data = [
      ("S20", "InferenceX GB300 對 GB200（V4-Pro）", "vLLM、無 MTP、2026-05-22：27 tok/s 時 6,182 對 2,189 tok/s/GPU；GB300 峰值 11,056@13.1；GB300 多 50% HBM 使配方更寬", "Interested-party（SemiAnalysis：平台受晶片商贊助、另售 TCO 模型）；單一來源須佐證", "2026-05", "inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4", "已核對原文（交接錨點即此，屬舊軟體）"),
      ("S21", "SGLang／NVIDIA：V4 on GB300", "SGLang＋MTP 2026-06：約 50 tok/s/user 時約 11,200 tok/s/GPU；草稿接受率 0.57→0.70；配方 10p1d dep4／dep32", "Interested-party（SGLang、NVIDIA 作者）", "2026-06-23", "pytorch.org/blog/serving-deepseek-v4-on-gb300-with-sglang-…", "已核對原文"),
      ("S22", "InferenceX 每美元比較（B300 對 GB300，V4-Pro）", "GB300：72 tok/s 時 9,384 tok/s/GPU、$0.078/M；130 tok/s 時 3,474、$0.216/M；187 tok/s 時 $1.436/M", "Interested-party（SemiAnalysis）；擬合所用，第二來源見 S31、S32", "約 2026-07", "inferencex.semianalysis.com/compare-per-dollar/deepseek-v4-b300-vs-gb300", "已核對搜尋摘錄；軟體與日期待確認"),
      ("S23", "InferenceX 比較（GB200 對 GB300，V4-Pro 0813）", "110 tok/s：GB200 3,795、GB300 6,522 tok/s/GPU", "Interested-party（SemiAnalysis）", "2026-08／09", "inferencex.semianalysis.com/compare/deepseek-v4-gb200-vs-gb300", "口徑待查：頁面預設為 agentic traces"),
      ("S24", "InferenceX H200（V4-Pro，FP8）", "75 tok/s 時 4,036、100 tok/s 時 3,102 tok/s/GPU", "Interested-party（SemiAnalysis）", "2026-08", "inferencex.semianalysis.com/run/deepseek-v4-on-h200", "口徑待查；未入驗證"),
      ("S25", "Anthropic 多代理研究系統", "agent 約 4 倍、多代理約 15 倍聊天 token", "Interested-party（Anthropic）", "2025-06", "Anthropic Engineering Blog（經多方轉述核對）", "已核對二手"),
      ("S26", "Artificial Analysis 輸出速度", "GPT-5.6 Luna 約 120、GPT-5.6 Sol 約 68、GPT-6 Astra 約 52–56、Opus 5 約 54、Gemini 3.8 Flash 約 290–350 tok/s", "Verified-measured（反映供應商自身服務選擇）", "2026-09", "artificialanalysis.ai", "已核對"),
      ("S27", "DeepSeek V4 模型卡與 v4 架構預設表", "V4-Pro 1.6T／49B、61 層、d 7168；V4-Flash 284B／13B", "Verified", "2026", "Tokenomics v4 活頁簿（20260922）預設表；morphllm.com 2026-09-07 彙整", "待以 config.json 核對"),
      ("S28", "NVIDIA 規格", "H100 FP8 989 TF、80 GB、3.35 TB/s；GB200 FP4 10 PF、186 GB、8 TB/s；B300 15 PF、288 GB；Rubin 50／35 PF、288 GB、22 TB/s；RU NVL576 15 EF、HBM4e", "Interested-party（NVIDIA）", "2025–26", "模型內建知識", "待以規格表核對"),
      ("S29", "能量常數", "HBM3 約 3.9 pJ/bit、HBM3e 約 3、HBM4 約 2.5；SerDes 1–2 pJ/bit", "Analogy", "—", "文獻常見值（模型內建知識）", "待查核"),
      ("S31", "MLPerf Inference v6.0（DeepSeek-R1）", "GB300 NVL72 interactive 250,634、GB200 NVL72 240,318 tok/s（72 GPU）；GB300 server 8,064 tok/s/GPU", "Verified-measured（MLCommons 稽核）／Interested-party（NVIDIA 提交並挑選配置）", "2026-04-01", "NVIDIA 資料中心推論效能頁；NVIDIA 技術部落格", "已核對二手"),
      ("S32", "MLPerf Inference v6.1（VR200 首次提交）", "DeepSeek-R1 interactive：VR200 NVL72 652,750 對 GB300 NVL72 253,506 tok/s（2.58 倍）；VR 為預覽類", "Verified-measured（MLCommons）／Interested-party（NVIDIA 對照表）", "2026-09-16", "shattered.io 轉述 NVIDIA 對照表", "待以 MLCommons 原始結果核對"),
      ("S33", "MLCommons DeepSeek-R1 基準規格", "平均 ISL 800、OSL 3,880；server TTFT 2 s／TPOT 80 ms；interactive TTFT 1.5 s／TPOT 15 ms（p99），允許 3 步 MTP", "Verified", "2025-09／2026-03", "mlcommons.org；inference_rules", "已核對"),
      ("S34", "AMD：InferenceX 資料的選擇性使用", "NVIDIA GTC 2026 以 InferenceX 資料比較時選 FP4、MTP=3 等有利設定；同條件下 MI355X 可能更便宜", "Interested-party（AMD）", "2026-03", "amd.com 技術文章", "提醒：同一平台資料可因設定選擇而偏向"),
      ("S35", "DeepSeek-V4 技術報告（arXiv 2606.19348）", "V4-Flash 32T、V4-Pro 33T token 預訓練；4K→16K dense 注意力後切換稀疏；後訓練：專家 SFT＋GRPO，再以 on-policy 蒸餾整合；FP8 計算＋FP4 QAT，rollout 用原生 FP4 權重；未揭露訓練算力", "Interested-party（DeepSeek）", "2026-06", "arxiv.org/abs/2606.19348", "已核對原文摘錄"),
      ("S36", "NVIDIA Vera Rubin NVL72 規格表", "NVFP4 推論 3,600 PF、NVFP4 訓練 2,520 PF、FP8/FP6 訓練 1,260 PF、BF16 288 PF（72 GPU）", "Interested-party（NVIDIA）", "2026", "NVIDIA 規格表（Gigabyte 轉載 PDF）；spheron.network 轉述", "已核對兩處轉載"),
      ("S37", "Meta Llama 3 技術報告", "405B：16K H100、BF16 MFU 38–43%；有效訓練時間 >90%", "Interested-party（Meta）", "2024-07", "arXiv 2407.21783（模型內建知識）", "待查核"),
      ("S38", "Epoch：最終訓練占研發算力少數", "最終訓練占研發支出：OpenAI 9.6%、MiniMax 22.6%、Z.ai 12.3%；實驗利用率低於最終訓練", "Analogy（Epoch 推估；資料源為 The Information 等報導）", "2026-03", "epoch.ai/gradient-updates/r-and-d-vs-training-compute", "已核對"),
      ("S39", "Epoch：超過 1e25 FLOP 的模型", "Grok-3 約 4.6e26 FLOP；估計誤差 2–5 倍", "Analogy（Epoch 推估）", "2025-06", "epoch.ai/data-insights/models-over-1e25-flop", "已核對"),
      ("S40", "R1 RL 算力（Lambert《RLHF》書）", "R1 RL 147K H800 GPU 小時，約 V3 預訓練 2.8M 的 5%", "Interested-party（DeepSeek，經轉述）", "2025／2026", "arxiv.org/pdf/2504.12501", "已核對轉述"),
      ("S41", "Epoch：推理模型能擴展多遠", "Nemotron Ultra RL 14 萬 H100 小時，不到預訓練 1%", "Analogy（Epoch 轉述 NVIDIA）", "2025-05", "epoch.ai/gradient-updates/how-far-can-reasoning-models-scale", "已核對"),
      ("S42", "xAI Grok 4 發表", "以 20 萬 GPU 叢集做預訓練規模的 RL；RL 算力為前次 10 倍以上", "Interested-party（xAI，宣傳誘因）", "2025-07", "x.ai/news/grok-4", "已核對原文；口徑不明"),
      ("S43", "verl DeepSeek V4 RL 配方（PR #7895）", "TE FP8 訓練＋MXFP4 專家 QAT；vLLM rollout FP8、KV FP8", "Verified（開源程式碼）", "2026", "github.com/verl-project/verl/pull/7895", "已核對；J12 替代情境依據"),
      ("S44", "DeepSeek-V3 技術報告", "預訓練 14.8T token、2.664M H800 GPU 小時（全部 2.788M）；FP8 混合精度訓練；序列長 4K", "Interested-party（DeepSeek）", "2024-12", "arxiv.org/abs/2412.19437", "GPU 小時為模型內建知識，待以原文核對"),
      ("S45", "DeepSeek-V4.1-Flash 技術報告（arXiv 2609.19969）", "合成任務以大規模非同步 RL；rollout 在 DSec 沙箱、與可搶占訓練池分離；非同步已用於幾乎全部 RL 與 OPD，rollout 與訓練共置分時", "Interested-party（DeepSeek）", "2026-09", "arxiv.org/pdf/2609.19969", "已核對原文摘錄"),
      ("S46", "GLM-5 技術報告（arXiv 2602.15763）", "以 slime 框架建新非同步 RL 基礎設施，進一步解耦生成與訓練；非同步 Agent RL 演算法", "Interested-party（Zhipu）", "2026-02", "arxiv.org/abs/2602.15763", "已核對原文摘錄"),
      ("S47", "Kimi-Researcher（Moonshot）", "完全非同步 rollout＋回合層級部分 rollout，rollout 至少加速 1.5 倍；K1.5 為迭代同步＋部分 rollout", "Interested-party（Moonshot）", "2025", "Moonshot 技術部落格（經 Medium 轉述）", "已核對轉述"),
      ("S48", "LlamaRL（Meta，arXiv 2505.24034）", "Llama 3 後訓練使用非同步 off-policy RL；405B 相對 DeepSpeed-Chat 類系統最高 10.7 倍（基準線較弱）", "Interested-party（Meta）", "2025-07", "arxiv.org/pdf/2505.24034", "已核對"),
      ("S49", "ROLL Flash（阿里淘天）、AReaL（螞蟻）框架", "ROLL Flash：同 GPU 預算下 RLVR 2.24 倍、agentic 2.72 倍；AReaL：同步約慢 2 倍。僅框架，未證實用於 Qwen／Ling 旗艦模型", "Analogy（框架基準測試）", "2025–2026", "arxiv 2510.11345；inclusionai.github.io/AReaL", "已核對；不計入 J14 採用數"),
      ("S30", "DeepSeek 推論系統公開統計（H800）", "V3/R1 線上：prefill 與 decode 節點吞吐、每用戶約 20 tok/s；本模型用於 η_p 與 Hopper η_d 倍數", "Interested-party（DeepSeek）", "2025-02", "DeepSeek Open Source Week 第 6 天（模型內建知識）", "待查核"),
    ]
    for i, row in enumerate(data):
        r = 23 + i
        for c, v in zip("ABCDEFG", row): put(ws, f"{c}{r}", v, wrap=True)

def readme(wb):
    ws = wb["README"]
    rows = [
      ("用途", "回答：每 1 GW IT 電力，各世代可容納多少機架、資本支出與持有成本（Block 1）；各層級 SLO 下的產出與依『世代 × 層級 × token 類型』的每 M token 成本（Block 2）；各層級代表模型的訓練與研發計畫需要多少 GPU 小時、成本與 1 GW 年，其中後訓練占多少（Block 3）；每 GW 的理論營收（理想上限）、含中國廠商的單價前緣、訓練攤提、快取儲存與 1 GW 參考機隊（Block 4）；harness 對每個成功任務的 token、成本與成功率的影響（Block 5）。實際營收（需求、市占、訂閱方案）在下游。"),
      ("版本", v524.README_VERSION + "X1：Interface G 節新增七列生產折減並列輸出 IF_FullCost_Luna／Sol／Astra_Prod、IF_RevGW_Luna／Sol／Astra_Prod、IF_RevGWFleet_Prod，由新輸入格 CTL_ProdDerate（Serving!C28，預設 0.85）驅動，推導鏈以 8 個 *_Prod 鏡像頁重算，Checks X1 自我檢查；Serving!C18 維持 1.0（G0-11）；X2：Gov_Map P 欄升段 11 格；Decisions 新增 X1、X2；既有模型頁、Interface 既有列、L1 數值逐格不變；工作單 docs/workorders/20261006_v5.19.md）。以下為 v5.18（Stage 2 第一批寫入，工作單 docs/workorders/20261005_v5.18.md r2：SRC 等級依 S1 (a)、G15、H1 規則升級並登錄 DB_Evidence；Train_In C44、Calib C69 改公式；SRC_PERF_009／010 改為內插值；Arch KV 區間、Hopper 占機隊 0.57、Train_In C21 Hopper 倍數 1.0、SRC_MOD_015 拆為 Flash／Pro 兩筆；VR200 機架功率與價格、GB200／GB300 機架功率更新；Rubin Ultra 欄改為單架 72 封裝並新增 SRC_HW_061–064、SRC_MOD_054；Workload／Serving 區間依 Copilot 追蹤擴大；Gov_Map P 欄改 B 法「O＋L1」分段；Checks 第 21 列改述為 InferenceX 內部常數）。以下為 v5.17（收尾小項：L1!I43 讀法文字改為「依定義 ≥ 1」；數值與公式不變）。以下為 v5.16（L1 Answers 修正：第 5 題新增理論毛利率兩列（L1_Ans5_GM 毛利口徑、L1_Ans5_FullMargin 全成本口徑；毛利口徑附 2025 推論毛利隱含值對照）；第 6 題拆為 FLOPs 口徑（L1_Ans6）與 GPU 小時口徑（L1_Ans6_GPUh）；第 7 題改為 OpenAI 單價 ÷ 前緣單價；第 8 題改連 IF_HarR_Sol（選定 ÷ 標準）；L1 欄位約定：D＝基準、E＝低、F＝高，無區間時 E＝F＝D；Checks 新增 H3（L1 的 E ≤ D ≤ F 檢查，WARN）。模型頁、Interface、SRC、Gov_Map 不動）。以下為 v5.15（Block 6 Alloc：研發與服務的算力配置。新增 Alloc_In（輸入：N_major、N_refresh、k、服務世代組合、g、API 全年平均比例、每則提示 token 數、免費占比；全部 Assumed 或 Decision，附區間，登錄 Gov_Map）與 Alloc（需求 D → 服務 GW → 研發 GW → Q1、Q2 → 校準反推 → 外部對照 → 敏感度表）；Interface F 節新增 IF_AllocQ1、IF_AllocQ1_R2、IF_AllocQ2、IF_AllocServeGW、IF_AllocRDGW、IF_AllocDemand、IF_AllocImpliedNk；L1 新增 Answers 9 題（L1_Ans1–9）與外部對照 3 列；SRC_Demand 新增 SRC_DEM_010–013，DB_Evidence 新增 E166–E169，Decisions 新增 A9、A10 並將 A1–A8 狀態改為「v5.15 已建」；Checks 新增 H 節（H1 世代組合合計、H2 敏感度自我檢查），計入 GOV_Errors；既有模型頁、Interface 既有列、既有 L1 列的數值逐格不變）。以下為 v5.14（L1 第 O、P 欄加檢查 D 欄是否為數字：v5.13 在 SLO 不可達情境（生產折減 0.7、Tech_Registry T07–T09 開啟）下 L1!O35、P35 出現錯誤值，CC 第 13 輪發現；SRC 各頁 X 欄的比對範圍改為與 SRC_Index 相同（最後一筆紀錄＋50 列），全簿重算約減三成；基準數值不變；Block 6 改為 v5.15）。以下為 v5.13（切片二 B–E 包：Source 遷入、Gov_Map 擴及切片二頁、模型邏輯、寫回 Andy 審閱；v5.13 E：v5.11、C 包、D 包審閱檔 Andy 2026-10-03 全部依建議，寫入 Gov_Map 與 Decisions（原話 83 項確認、CV1 維持 4×HGX、G0-9 文字修正、輪數下限與快取命中區間修正）；Block 6 於 v5.14。v5.13 D：Arch 第 21–23 列 KV bytes 改公式（新增「KV 推導輸入」5 列），Arch C9、C10 連結 V4-Flash 官方 config（SRC_MOD_052、053），Cap_In 中國廠商旗標改公式，Checks 的外部比對移入 L1（新增 7 列）、樣本外實測值連結 SRC_Perf；數值不變。v5.13 C：切片二頁 515 個數值藍字格登錄 Gov_Map 129 列（分類、可比 SRC、區間、理由；Andy 2026-10-03 審閱「all ok」），Checks E12 擴及全部範圍。v5.13 B：新增 SRC_Price 44、SRC_Cap 21、SRC_Harness 15、SRC_Demand 9 筆（Stage 0 審閱的等級與立場），S30 一手原文補登 SRC_Perf 11 筆；Cap_In、Har_In、Workload 第 40 列 75 格改連結 SRC（值相等者），Checks C9:C10、最終訓練占研發區間、OpenAI 2025 對帳常數改連結 SRC_Price／SRC_Demand；數值逐格不變。以下為 v5.12（工程基礎）：新增 SRC_Index（各 SRC 頁 ID 依序堆疊），Gov_Map 的 SRC 狀態與等級改為每列 1 次 MATCH；SRC 各頁 X 欄改以 AH 同指標鍵比對；Checks 加 E13；Sources 更名 Sources_Legacy；公式內常數移到具名輸入格（CST_CtxKV、CST_STMult、CST_Eps、CST_MainMin），Sens_Train 情境倍數統一放在第 8 列；數值逐格不變。以下為 v5.11：Block 1＋2＋3＋4＋5＋治理 Stage 1 切片一；v5.11 建第 0 層 Source：SRC_HW、SRC_DC、SRC_Model、SRC_Perf（164 筆），模型頁原始數據改以公式連結 SRC_ID（數值逐格不變），DB_Evidence 加狀態與 SRC_ID 欄並登錄遷移紀錄，新增 Decisions、Gov_Map、L1 與 Checks G 節治理檢查；F14：Interface 與模型頁的每 GW 值除以 Inputs!E5，DC_Cost 改標為設施合計；v5.10 加成功任務成本前緣的可靠度下限 p_min（M1 (b)），Interface E 節增列每次嘗試成本、有效時間範圍與前緣；v5.9 加 Block 5：Har_In、Harness、Sens_Har，Workload 改為 harness 參數組，Block 4 補 SLO 不可達保護、K6 預設 (c)、機隊層級貢獻列、中國廠商旗標；v5.8 加 Block 4：Cap_In、Capability、Price_Frontier、Cache_Store、Fleet_1GW、Amortize、Theory_Rev、Sens_Rev；v5.2 加第二來源驗證與生產折減；v5.3、v5.4 依 CC 回饋補具名範圍與驗證表；v5.5 加 Block 3：Tech_Registry、Train_In、Perf_Batch、Training、Sens_Train，並更正 Hopper FP8 峰值；v5.6 非同步 RL 併入基準、補 TR_ 與訓練世代具名範圍；v5.7 改為 Excel 優先：輸入值由 Excel 擁有，新增 DB_Evidence 證據登錄表）。v4 的 Config／TL_Param／WP_Param／Revenue_Model 由 Arch、Serving、Workload、Calib、Perf、Unit_Cost 取代。"),
      ("電力口徑", "GW＝IT 關鍵電力（Andy 2026-09-30 確認）。設施電力＝IT × PUE，於 DC_Cost 與 Interface 並列。v5.11 起 DC_Cost 為設施合計（Inputs!E5 GW）；Interface、L1 與模型頁的每 GW 值一律除以 E5（F14）。"),
      ("資料架構（v5.11）", "DB_Evidence（所有新訊息入口）→ 擇優 → SRC_*（第 0 層：只存原始訊息；SRC_ID 具名範圍）→ 模型頁（原始數據以公式連結 SRC；Analogy、Assumed、Decision 留在模型頁並登錄於 Gov_Map）→ Checks G 節（治理檢查，ERROR 必須為 0）→ L1（常用推算值，即時公式，附外部對照）／Interface（推算構件）→ 下游。規劃書：repo docs/plan/Tokenomics_governance_plan.md。"),
      ("Excel 擁有的治理頁（v5.11）", "SRC_HW、SRC_DC、SRC_Model、SRC_Perf、SRC_Price、SRC_Cap、SRC_Harness、SRC_Demand（v5.13）、Decisions、DB_Evidence，以及 Gov_Map 的 A–P 欄：builder 只在不存在時建立，之後不覆寫（v5.13 起既有 SRC 頁的新紀錄只在 ID 不存在時附加；Gov_Map 判斷欄的更新只在該格仍為舊值時寫入）。builder 每次重建：模型頁的 SRC 連結（gov_seed.FORMULA_MAP、gov_seed2.FORMULA_MAP2）、SRC 的 X–Z 與 AH 檢查欄、Gov_Map 的 Q–AF 欄、SRC_Index（v5.12）、L1、Checks G 節，以及 SRC_／L1_／GOV_／IDX_ 具名範圍；v5.12 起新輸入格的 Gov_Map 列只在未登錄時附加。"),
      ("工作表", "Inputs → Spec_Rack → Arch → Serving → Workload → Calib → Tech_Registry → Perf → Sens_Perf → Unit_Cost → DC_Cost → Train_In → Perf_Batch → Training → Sens_Train → Cap_In → Capability → Price_Frontier → Cache_Store → Fleet_1GW → Amortize → Theory_Rev → Sens_Rev → Har_In → Harness → Sens_Har → Alloc_In → Alloc → Perf_Prod → Perf_Batch_Prod → Training_Prod → Unit_Cost_Prod → Interface_Prod → Fleet_1GW_Prod → Amortize_Prod → Theory_Rev_Prod（v5.19 X1 鏡像頁）→ Interface → L1；Energy、NonNV、Sensitivity、Checks、Gov_Map、Decisions、SRC_HW、SRC_DC、SRC_Model、SRC_Perf、SRC_Price、SRC_Cap、SRC_Harness、SRC_Demand、SRC_Index（builder 擁有的查找索引）、Sources_Legacy（v5.12 起凍結）、DB_Evidence。"),
      ("Block 6 推導（v5.15）", "實驗室年度算力＝研發需求＋服務需求。需求 D（token 路線，A9）：API＝SRC_DEM_010 × 525,600 × 全年平均比例；ChatGPT＝SRC_DEM_012 × 每則提示 token 數 × 365。服務 GW＝D ÷ 世代組合後每 GW 年產能（依 Cap_In 層級組合與 IF_TokGW_*、IF_Util，寫法同 Fleet_1GW 第 19–29 列）。研發 GW 年＝k ×（N_major × 家族計畫＋N_refresh × 改版計畫），家族計畫＝IF_ProgGWyr 三層級合計，改版計畫＝後訓練 GPU 小時 × 研發倍數換算 GW 年（訓練世代＝IF_TrainGenDefault）。Q1＝研發 GW ÷（研發＋服務 GW）；Q2 以各世代 IF_HoldEcon 加權，利用率不進入。研發占比的物理部分只給下限，實際占比由策略變數決定。隱含 N × k 由 2025 支出比反推（A3）。SLO 不可達時回傳文字。決策 A1–A10 見 Decisions。"),
      ("Block 3 推導", "預訓練：FLOPs＝3 ×（2 × 啟用參數＋注意力 FLOPs × 被注意 token）× token；GPU 小時＝FLOPs ÷（FP8 訓練峰值 × MFU × goodput）。RL、蒸餾、合成資料、評測的推論型運算以 Perf_Batch（與 Perf 同公式，只換速度下限與參考任務）計價；RL 有效 MFU 為推導值。研發計畫＝最終訓練 GPU 小時 × 研發倍數。"),
      ("Block 3 決策", "J7 訓練精度 FP8（NVFP4 預訓練在 Tech_Registry）；J8 Astra 預訓練與 Arch 一致，前沿錨點列 Checks；J9 RL 由下而上，基準校到 RL÷預訓練 GPU 小時 Luna／Sol 0.3、Astra 1.0；J10 研發倍數 8，家族合計、依最終訓練比例分攤；J11 用途 × 型態只列單一計畫；J12 rollout NVFP4（FP8 為情境）；J13 下游預設 VR200、GB300 並列；J14 主流＝至少兩家實驗室公開採用，可覆寫。"),
      ("Excel 優先（v5.7）", "藍字＝輸入，由本活頁簿擁有：要改輸入，直接改 Excel。builder 重建 Block 2、3 時會先讀取所有藍字輸入，重建後依『工作表＋欄 A 標籤＋欄位』寫回，程式內的預設值只用於新增的輸入列。公式頁不要手改（重建時會被覆寫）。"),
      ("DB_Evidence（v5.7）", "證據登錄表：所有比對過的新資訊（含不採納者），記錄主張、來源、標記、對應參數、當時值、新值、判定與處理版本。builder 只在本頁不存在時建立。"),
      ("Tech_Registry", "每列＝技術 × 作用物理量；有效倍數＝1＋開關 × 採用比例 ×（倍數−1）；已在基準者不套倍數。掛鉤彙總表連到 Perf、Perf_Batch、Training。全部開關為 0 時 Block 2 數值與 v5.4 相同。"),
      ("Block 2 推導", "prefill：tok/s＝η_p × 峰值 ÷ FLOPs/token。decode：每步時間＝固定延遲（權重讀取＋每層延遲 ×（層數＋草稿數））＋B × 每序列時間；在 SLO 下解出批次 B*，再受 HBM 容量限制。η_d 與每層延遲由 GB300 同一前緣兩點聯立解出（Calib）。"),
      ("成本情境", "低成本／基準／高成本為角落情境。單一變數影響看 Sensitivity（Block 1）與 Sens_Perf（Block 2）。"),
      ("功率情境", "Inputs!E6 選 1／2／3，決定每架配電設計功率與每 GW 機架數。"),
      ("顏色", "藍字＝輸入；黑字＝公式；綠字＝跨頁連結；淡黃底＝關鍵輸出；亮黃底＝待 Andy 決定或情境改動。"),
      ("來源標記", "Verified／Interested-party／Analogy／Assumed／Derived。Analogy 與 Assumed 一律給區間。"),
      ("網站同步", "本檔為事實來源；repo 以公式引擎直接計算本檔，parity 測試比對 Interface 全部格（新增 IF_ 具名範圍見 Interface B 節）。"),
      ("具名範圍", "SRC_＝第 0 層原始值（值、_Lo、_Hi；SRC_Perf 另有 _ISL、_OSL、_Spd、_MTP），下游可直接引用 Active 紀錄（G8）；L1_＝第 1 層常用推算值（_Lo、_Hi 為區間），下游可引用；GOV_＝治理檢查合計（CI 讀 GOV_Errors）；IF_＝下游模型連結用；IF_Hdr／DRV_／CAL_／TRN_／TR_＝網站顯示用，下游不得連結；B4_／B5_＝Block 4／5 公式內部引用的關鍵量（v5.8 起新公式以具名範圍引用，使公式可讀），下游不得連結；IF_HdrTask 為顯示用表頭；CST_＝原寫在公式內的常數移出後的輸入格（v5.12），IDX_＝SRC_Index 查找欄（v5.12），兩者下游不得連結。"),
      ("Block 4 推導", "理論營收＝每 GW 產出 × 利用率 × 參考請求混合有效單價（OpenAI 牌價 ×（1−折扣）× 能力單價倍數）。單價前緣＝能力指數 ≥ OpenAI 層級模型者之中，參考請求混合單價最低者（含中國廠商）。快取儲存＝KV bytes × 儲存層 $/GB-hr × 保留時間 ÷ 命中次數。攤提：自下而上＝研發計畫成本 ÷ 商業壽命內服務 token（＝回本所需溢價）；由上而下＝機隊訓練占比 X ÷（1−X）× 服務成本。"),
      ("Block 4 決策", "K1 OpenAI 單價為基準；K2 (i) 前緣＝同能力最低價；K3 AA 指數為主、METR 檢查；K4 (c)＋(d) 能力→單價彈性基準 0＋回本溢價反解；K5 壽命 Luna／Sol 12、Astra 9 個月；K6 兩種攤提並列，v5.9 起下游預設 (c)＝由上而下總額 × 自下而上權重、(d) 營收權重並列；K7 機隊以 OpenAI 2025 校準；K8 只計 API 單價；K9 各世代共用 2026-09 單價快照；K10 快取儲存比照公開條款；K11 利用率 60%、折減 1.0 暫用；K12 尖峰離峰並列、前緣用時數加權；K13 中國廠商全納入並標示開放權重；K14 國際站美元價。"),
      ("Block 5 推導", "harness＝作用在標準任務上的參數組（輪數、思考保留 ρ、每輪思考、歷史壓縮、快取命中、子代理、狀態保留時間）加成功率。Workload 有效參數＝標準＋w ×（Har_In 選定檔案−標準），w＝Tech_Registry T12 開關 × 採用比例。成功率 p＝1 ÷（1＋（任務長度 ÷（層級 50% 時間範圍 × harness 倍數））^β）（METR 型）；每成功任務成本＝每次嘗試成本 ÷ p。每 GW 理論營收不受 harness 影響。"),
      ("Block 5 決策", "L1 參數組取代單一 token 倍數；L2 METR 型成功率＋覆寫欄；L3 增強檔不入基準（w＝0）；L4 harness 不影響每 GW 營收；L5 每成功任務成本＝每次嘗試 ÷ p；L6 非 GPU 成本不入第 0 層；L7 情境值只採中立方同條件實測；M1 (b) 成功任務成本前緣只比較成功率 ≥ 可靠度下限 p_min（基準 50%）者，無合格時回傳「無合格」，不設下限的前緣列為對照。"),
      ("來源原則", "SemiAnalysis（含 InferenceX）資料一律須有第二來源佐證並標記 Interested-party；目前第二來源為 MLPerf（MLCommons 稽核，NVIDIA 提交）與 DeepSeek 自揭（待查）。"),
      ("未結事項", "(1) VR200 報價是否含網路（S11）。(2) 所有來源待 Andy 查核。(3) Rubin Ultra 為推估。(4) J6 基準利用率暫用 60%、生產折減暫用 1.0，皆待 Andy 給值。(5) VR200 無實測，η_d 與每層延遲沿用 GB300。(6) 交接錨點 6,182 屬舊軟體（vLLM 無 MTP），已改為 GB300 最新前緣兩點校準。(7) 快取儲存成本已於 v5.8 Cache_Store 加入（儲存層與保留時間為 Assumed）。(8) Hopper 峰值更正為 FP8 1,979 TF，η_d 與 η_p 倍數同步減半以維持產出；S30 口徑待查後重推。(9) Block 3 的 Astra token、RL rollout 量、研發倍數皆為 Analogy／Assumed，看 Sens_Train。(10) v5.6：非同步 RL 併入基準（rollout 效率 0.85），RL rollout token 重校以維持 GPU 小時錨點（J9 (a)）。(11) v5.8：K6 下游攤提預設於 v5.9 定為 (c)；Claude Opus 5.5、Kimi K3、MiniMax M3 的能力指數未取得，不參與前緣；Anthropic、Moonshot、Alibaba、MiniMax 價格為二手；METR 檢查未入表；Google 未列入候選。(12) v5.9：METR 尚未發布 GPT-6 各層級時間範圍（以 GPT-5.6 Sol、Mythos Preview 類比）；任務長度為 Assumed；ARC 金額衝突與 Opus 5 harness 歸屬待核；harness 用於 RL rollout 與非 GPU 成本延後。"),
      ("生產折減並列輸出（v5.19 X1）", "Serving!C18（J15）維持 1.0（G0-11），模型的基準輸出不變。Interface G 節並列七列 _Prod 輸出，以 CTL_ProdDerate（Serving!C28，預設 0.85＝區間 0.7–1.0 的中點，情境值）重算：從 Serving!C18 進入模型的兩處（Perf、Perf_Batch 第 50 列）起，到 Theory_Rev 七個輸出列為止的公式鏈，逐格鏡像到 *_Prod 頁（同位置；只改兩處：鏈上參照改讀 *_Prod、第 50 列改讀 CTL_ProdDerate）。右側 S:AG 為檢查副本（第 50 列＝Serving!C18），Checks X1 比對七列是否等於基準列。_Prod 輸出的口徑同 D 節對應列；SLO 不可達時為文字。"),
      ("Interface 攤提耦合（v5.20 X5）", v520.X5_NOTE),
    ]
    for i, (a, b) in enumerate(rows):
        r = 4 + i
        put(ws, f"A{r}", a, F_BOLD); put(ws, f"B{r}", b, wrap=True)
    put(ws, "A1", "Tokenomics " + v524.README_TITLE, F_TITLE)     # v5.24: version from v524.VERSION (same source as B5); Block 6, L1, Interface added
    put(ws, "A2", "第 0 層規格來源。理論營收為理想上限；實際營收在下游模型。", F_NOTE)

# ---------------------------------------------------------------- Block 3 additions (v5.5)
def interface_b3(wb, TRN, start, TI):
    ws = wb["Interface"]
    r = start
    section(ws, r, "C. Block 3 產出（依層級；欄＝世代 × 成本情境；GPU 小時不隨成本情境變動；下游預設 VR200、GB300 並列，J13）", 17); r += 1
    names = []
    tiers = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
    for t, (tk, tn) in enumerate(tiers, start=1):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        tl = lambda key: f"=INDEX(Training!$C${TRN[key]}:$Q${TRN[key]},3*(Unit_Cost!{{X}}$6-1)+{t})"
        rows = [
          (f"IF_TrainGPUh_{tk}", "最終訓練 GPU 小時（單一模型）", "GPU-hr", "#,##0", tl("Hfin")),
          (f"IF_TrainCost_{tk}", "最終訓練成本 — 經濟（依成本情境）", "$M", "#,##0.0", tl("Hfin") + "*Unit_Cost!{X}$8/1E6"),
          (f"IF_PostShareFLOP_{tk}", "後訓練占比（FLOPs 口徑）", "%", "0.0%", tl("psF")),
          (f"IF_PostShareGPUh_{tk}", "後訓練占比（GPU 小時口徑）", "%", "0.0%", tl("psH")),
          (f"IF_RLMFU_{tk}", "RL 有效 MFU（訓練峰值分母）", "%", "0.0%", tl("rlmfu")),
          (f"IF_ProgGPUh_{tk}", "研發計畫 GPU 小時（含研發倍數分攤）", "GPU-hr", "#,##0", tl("Hprog")),
          (f"IF_ProgCost_{tk}", "研發計畫成本 — 經濟（依成本情境）", "$M", "#,##0", tl("Hprog") + "*Unit_Cost!{X}$8/1E6"),
          (f"IF_ProgGWyr_{tk}", "研發計畫占 1 GW 一年", "%", "0.00%", tl("GWp")),
        ]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for X in COLS15:
                put(ws, f"{X}{r}", tpl.format(X=X), fmt=fmt, fill=FILL_KEY if "Prog" in name or "PostShareGPUh" in name else None)
            names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "研發倍數（第 0 層基準；下游可覆寫）　[IF_RDMult]"); put(ws, f"B{r}", "x")
    put(ws, f"C{r}", f"=Train_In!$C${TI['rdm']}", fmt="0.0"); names.append(("IF_RDMult", f"Interface!$C${r}")); r += 1
    put(ws, f"A{r}", "下游預設訓練世代（索引；J13）　[IF_TrainGenDefault]"); put(ws, f"B{r}", "索引")
    put(ws, f"C{r}", f"=Train_In!$C${TI['gdef']}", fmt="0"); put(ws, f"D{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,C{r})", F_HLINK)
    names.append(("IF_TrainGenDefault", f"Interface!$C${r}")); r += 1
    put(ws, f"A{r}", "並列訓練世代（索引；J13）　[IF_TrainGenAlt]"); put(ws, f"B{r}", "索引")
    put(ws, f"C{r}", f"=Train_In!$C${TI['galt']}", fmt="0"); put(ws, f"D{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,C{r})", F_HLINK)
    names.append(("IF_TrainGenAlt", f"Interface!$C${r}"))
    names.append(("IF_TrainGenDefaultName", f"Interface!$D${r-1}")); names.append(("IF_TrainGenAltName", f"Interface!$D${r}")); r += 1
    for n, ref in names:
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return names

def checks_b3(wb, TRN, TI, CAL, PB):
    ws = wb["Checks"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, "Block 3 檢查（VR200＝N 欄 Astra、M 欄 Sol；GB300＝K、J）", 6)
    put(ws, f"A{r0+1}", "項目", F_BOLD); put(ws, f"B{r0+1}", "本模型", F_BOLD); put(ws, f"C{r0+1}", "外部參照", F_BOLD)
    put(ws, f"D{r0+1}", "單位", F_BOLD); put(ws, f"E{r0+1}", "判讀", F_BOLD); put(ws, f"F{r0+1}", "來源", F_BOLD)
    T = lambda k, col: f"Training!{col}{TRN[k]}"
    v3 = (f"=3*(2*Calib!$C${CAL['rA']}*1E9+Calib!$C${CAL['rac']}*Train_In!$C${TI['v3seq']}/2)*Train_In!$C${TI['v3tok']}*1E12"
          f"/(Train_In!$C${TI['v3h']}*1E6*3600*Spec_Rack!$C${{tfp8}}*1E15)")
    rows = [
      ("DeepSeek V3 推導 MFU（H800、FP8 分母）", v3, "=Training!C" + str(TRN["mfu"]), "%",
       "外部參照欄＝本模型 Hopper 採用 MFU；兩者接近即 Hopper 倍數 0.8 成立", "S44"),
      ("RL ÷ 預訓練 GPU 小時：VR200 Astra", f"={T('rlH','N')}", f"=Train_In!$C${TI['grok']}", "x",
       "J9 基準 1.0；參照為 Grok 4 宣稱（口徑不明）", "S42"),
      ("RL ÷ 預訓練 GPU 小時：VR200 Sol", f"={T('rlH','M')}", f"=Train_In!$C${TI['r1rl']}", "x",
       "J9 基準 0.3；參照為 R1（2025-01）", "S40"),
      ("RL 有效 MFU：VR200 Astra", f"={T('rlmfu','N')}", "0.01–0.10", "%", "交接第 3 節區間；本模型為推導值", "交接"),
      ("後訓練占比：GPU 小時口徑 − FLOPs 口徑（VR200 Astra）", f"={T('psH','N')}-{T('psF','N')}", "≥ 0", "%",
       "RL 有效 MFU 低於預訓練，GPU 小時占比必然較高", "Training I 節"),
      ("最終訓練 ÷ 研發計畫", f"=1/Train_In!$C${TI['rdm']}", "9.6%–22.6%", "%", "Epoch 三家公司區間", "S38"),
      ("前沿錨點中值（5e26）反推 Astra 預訓練 token", f"=Train_In!$C${TI['an2']}/({T('Fpt','N')}*1E9)/1E12",
       f"=Training!N{TRN['Dp']}", "T", "J8：差距大代表 Astra 啟用參數或 token 假設偏低；錨點低／高值見 Train_In", "S39"),
      ("Astra 最終訓練占 1 GW 一年：VR200 ／ GB300", f"={T('GWf','N')}", f"={T('GWf','K')}", "%", "本模型 VR200 值；外部參照欄為 GB300", "Training"),
    ]
    return r0 + 2, rows

def write_checks_b3(wb, r, rows, SP):
    ws = wb["Checks"]
    for i, (a, b, c, d, e, f) in enumerate(rows):
        rr = r + i
        b = b.replace("{tfp8}", str(SP["tfp8"]))
        put(ws, f"A{rr}", a, wrap=True); put(ws, f"B{rr}", b, fmt="0.0%" if d == "%" else "#,##0.00", fill=FILL_KEY)
        put(ws, f"C{rr}", c, fmt="0.0%" if d == "%" else "#,##0.00"); put(ws, f"D{rr}", d)
        put(ws, f"E{rr}", e, F_NOTE, wrap=True); put(ws, f"F{rr}", f, F_NOTE)

# ---------------------------------------------------------------- v5.7: evidence register
EVID_HDR = ["ID", "日期", "主張（摘要）", "來源（S 編號或出處）", "標記", "對應參數（工作表與列）", "Tokenomics 當時值",
            "新資訊值", "判定", "處理版本", "備註"]
EVID_SEED = [
  ("E001", "2026-09-30", "H100 FP8 dense 峰值為 1,979 TF，非 989 TF", "NVIDIA H100 規格（S36 交叉核對）", "Interested-party",
   "Spec_Rack 峰值 Hopper", "0.989 PF", "1.979 PF", "採納", "v5.5", "η_d、η_p 倍數同步減半維持產出；S30 口徑待查"),
  ("E002", "2026-09-30", "DeepSeek V4-Flash／Pro 預訓練 32T／33T token", "S35", "Verified", "Train_In 預訓練 token",
   "—（新增）", "32／33T", "採納", "v5.5", ""),
  ("E003", "2026-09-30", "Rubin NVL72 FP8 訓練 17.5、NVFP4 訓練 35 PF/GPU", "S36", "Interested-party", "Spec_Rack B3 訓練峰值",
   "—（新增）", "17.5／35 PF", "採納", "v5.5", ""),
  ("E004", "2026-09-30", "最終訓練占研發算力支出 9.6–22.6%（OpenAI、MiniMax、Z.ai）", "S38", "Analogy", "Train_In 研發倍數",
   "—（新增）", "4.4–10.4 倍", "採納（取 8）", "v5.5", "支出口徑，乘在 GPU 小時上"),
  ("E005", "2026-09-30", "Grok 4 以預訓練規模做 RL", "S42", "Interested-party", "Train_In RL rollout token（J9 錨點）",
   "—", "RL ≈ 1 × 預訓練", "部分採納", "v5.5", "口徑不明，只作 Astra 錨點上緣參考"),
  ("E006", "2026-09-30", "前沿預訓練算力約 2e26–2e27 FLOP（Grok-3 約 4.6e26）", "S39", "Analogy", "Train_In Astra 預訓練 token",
   "60T（約 7e25 FLOP）", "需約 438T（5e26）", "待查", "—", "J8 差距；Block 4 以能力錨點檢驗"),
  ("E007", "2026-10-01", "非同步 RL 已用於 DeepSeek、Zhipu、Moonshot、Meta 旗艦模型", "S45–S48", "Interested-party",
   "Tech_Registry T10；Train_In rollout 效率", "0.60（未入基準）", "0.85（入基準）", "採納", "v5.6", "Andy 決定 (a)：rollout token 重校"),
  ("E008", "2026-10-01", "開源 RL 框架（verl）DeepSeek V4 配方以 FP8 rollout", "S43", "Verified", "Sens_Train rollout 精度情境",
   "NVFP4（基準）", "FP8", "不採納為基準", "v5.5", "列為 J12 替代情境"),
  ("E009", "2026-10-01", "ROLL Flash、AReaL 非同步增益約 2–2.7 倍", "S49", "Analogy", "Train_In rollout 效率區間",
   "—", "增益 2–2.7 倍", "部分採納", "v5.6", "僅框架，不計入 J14 採用數；只用於區間"),
]

def evidence_sheet(wb):
    if "DB_Evidence" in wb.sheetnames:
        return False
    ws = wb.create_sheet("DB_Evidence")
    title(ws, "DB_Evidence — 證據登錄表：所有比對過的新資訊（含不採納者）",
          "每一筆新發現先與 Tokenomics 現值比對，再判定採納／部分採納／不採納／待查。本頁由 Andy 與 Claude 直接在 Excel 維護；builder 只在本頁不存在時建立，之後不再覆寫")
    widths = [7, 11, 46, 26, 15, 30, 18, 18, 14, 9, 44]
    for i, (h, w) in enumerate(zip(EVID_HDR, widths)):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = w
    for j, row in enumerate(EVID_SEED):
        for i, v in enumerate(row):
            put(ws, f"{L(i+1)}{5+j}", v, F_IN, wrap=i in (2, 5, 10))
        ws.row_dimensions[5 + j].height = 30
    ws.freeze_panes = "C5"
    return True

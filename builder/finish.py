from common import *
from openpyxl.workbook.defined_name import DefinedName
from outputs import COLS15

def interface(wb, PR, U):
    ws = wb["Interface"]
    for r in range(17, 23):
        for c in range(1, 19): ws.cell(row=r, column=c).value = None
    put(ws, "A2", "每一列為一個具名範圍（IF_…），欄＝世代 × 成本情境；Block 2 產出依層級分區（物理量不隨成本情境變動）", F_NOTE)
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
      ("GB300 每 GPU 功率：本模型 IT 平均用電", "=DC_Cost!J11*Inputs!$E$10/72", "2.12", "kW/GPU", "InferenceX 72 tok/s 時 9,384 tok/s/GPU ÷ 4.43M tok/s/MW 反推（provisioned，口徑可能含設施）", "S22"),
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
    ws = wb["Sources"]
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
      ("用途", "回答：每 1 GW IT 電力，各世代可容納多少機架、資本支出與持有成本（Block 1）；各層級 SLO 下的產出與依『世代 × 層級 × token 類型』的每 M token 成本（Block 2）；各層級代表模型的訓練與研發計畫需要多少 GPU 小時、成本與 1 GW 年，其中後訓練占多少（Block 3）。不含營收（Block 4）。"),
      ("版本", "20261001_Tokenomics_v5.7（Block 1＋2＋3；v5.2 加第二來源驗證與生產折減；v5.3、v5.4 依 CC 回饋補具名範圍與驗證表；v5.5 加 Block 3：Tech_Registry、Train_In、Perf_Batch、Training、Sens_Train，並更正 Hopper FP8 峰值；v5.6 非同步 RL 併入基準、補 TR_ 與訓練世代具名範圍；v5.7 改為 Excel 優先：輸入值由 Excel 擁有，新增 DB_Evidence 證據登錄表）。v4 的 Config／TL_Param／WP_Param／Revenue_Model 由 Arch、Serving、Workload、Calib、Perf、Unit_Cost 取代。"),
      ("電力口徑", "GW＝IT 關鍵電力（Andy 2026-09-30 確認）。設施電力＝IT × PUE，於 DC_Cost 與 Interface 並列。"),
      ("工作表", "Inputs → Spec_Rack → Arch → Serving → Workload → Calib → Tech_Registry → Perf → Sens_Perf → Unit_Cost → DC_Cost → Train_In → Perf_Batch → Training → Sens_Train → Interface；Energy、NonNV、Sensitivity、Checks、Sources。"),
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
      ("具名範圍", "IF_＝下游模型連結用；IF_Hdr／DRV_／CAL_＝網站顯示推導鏈與驗證表用，下游不得連結。"),
      ("來源原則", "SemiAnalysis（含 InferenceX）資料一律須有第二來源佐證並標記 Interested-party；目前第二來源為 MLPerf（MLCommons 稽核，NVIDIA 提交）與 DeepSeek 自揭（待查）。"),
      ("未結事項", "(1) VR200 報價是否含網路（S11）。(2) 所有來源待 Andy 查核。(3) Rubin Ultra 為推估。(4) J6 基準利用率暫用 60%、生產折減暫用 1.0，皆待 Andy 給值。(5) VR200 無實測，η_d 與每層延遲沿用 GB300。(6) 交接錨點 6,182 屬舊軟體（vLLM 無 MTP），已改為 GB300 最新前緣兩點校準。(7) 快取命中只計載入時間，未計儲存成本。(8) Hopper 峰值更正為 FP8 1,979 TF，η_d 與 η_p 倍數同步減半以維持產出；S30 口徑待查後重推。(9) Block 3 的 Astra token、RL rollout 量、研發倍數皆為 Analogy／Assumed，看 Sens_Train。(10) v5.6：非同步 RL 併入基準（rollout 效率 0.85），RL rollout token 重校以維持 GPU 小時錨點（J9 (a)）。"),
    ]
    for i, (a, b) in enumerate(rows):
        r = 4 + i
        put(ws, f"A{r}", a, F_BOLD); put(ws, f"B{r}", b, wrap=True)
    put(ws, "A1", "Tokenomics v5.7 — Block 1＋2＋3：機架規格、每 GW 成本、各層級產出與每 token 成本、訓練與研發計畫", F_TITLE)
    put(ws, "A2", "第 0 層規格來源。能力與理論營收於 Block 4 加入。", F_NOTE)

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

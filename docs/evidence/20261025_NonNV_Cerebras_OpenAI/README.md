# NonNV D 段：Cerebras WSE-3、OpenAI／Broadcom 客製（Jalapeño）（唯讀查證；r1）

- 分支：`claude/evidence-nonnv-cs-oai`（base：master `0c8c1b7`，CURRENT v21.7）；PR #176
- 工作單：`docs/workorders/20261025_NonNV_Cerebras_OpenAI客製.md`；承接 A 段 `docs/evidence/20261023_NonNV昇騰Maia_A段/`、B 段 `docs/evidence/20261025_NonNV_TPU_Trainium/`、C 段 `docs/evidence/20261025_NonNV_AMD/`
- 審閱檔：`NonNV_Cerebras_OpenAI.xlsx`（四頁：建議值、推導、證據、待判斷；換算全用公式 234 格，LibreOffice 重算錯誤 0）；重建程式 `build_xlsx.py`、`evidence_data.py`；原文引句 `證據原稿.md`
- 分母：`model/20261025_Tokenomics_v21.7.xlsx`（VR200 NVL72 基準欄；數值與 C 段 v21.6 相同）
- 範圍：只寫入本資料夾；未改 `model/`、`builder/`、`tests/`
- **r1**：已依獨立核對修正（見檔尾「r1（獨立核對後）」）；以下數字皆為 r1 後的值

## 1. 結論（先看這裡）

| 候選 | 產出比 低／基準／高 | 持有比 低／基準／高 | 每 token 成本比（基準） | TK v21.7 現值 |
|---|---|---|---|---|
| Cerebras WSE-3（CS-3） | **維持** 0.2／0.4／0.8 | **維持** 0.8／1.0／1.2 | 2.5（不變） | 同左 |
| OpenAI／Broadcom 客製（Jalapeño） | **維持** 0.4／0.6／0.9（推導區間 0.35／0.60／1.15） | **維持** 0.7／0.8／1.0（界線 0.64–1.27） | 1.33（不變） | 同左 |

（原始公式結果：Jalapeño 推導區間 0.327／0.594／1.135（只用方法一）；方法二（OpenAI 自測，對照）0.646／0.770／0.949；持有比界線 0.638／0.818／1.269。Cerebras 只有方向界線。）

白話：
- **兩列 TK 數值都不改。** OpenAI 客製：Project 決定（Q6、Q8）——推導基準 0.60 與現值 0.6 相同，且證據以利害關係方為主；下一版只更新第 9 列說明欄。Cerebras：預設同樣只更新第 8 列說明欄（Q3）。
- **Cerebras：TK 的每 kW 法不適用，不推點值。** CS-3 每台 23 kW（Next Platform、The Register；Flopper「up to 27 kW」），FP16 dense 12.5 PF（Cerebras 只公布 125 PF sparse；dense 為 The Register 以 10 倍稀疏換算），44 GB SRAM、無 HBM。瓶頸是記憶體**容量**：每 kW 記憶體只有 VR200 的約 2%，權重與 KV 都要放 SRAM，GPU 世代還原的效率因子 f 不能類比。
- **Cerebras 產出比方向：現值偏樂觀，但不硬改。** (a) 最高原生精度（FP16 對 VR200 NVFP4）每 kW 峰值比 0.04–0.05；(b) FP16 對齊（對 VR200 BF16 4 PF）0.36–0.43——f＝1 的上限，只與現值基準 0.4 相當；(c) Cerebras 自述「4,000 萬 Llama-70B tok/s、數千台」換算每 kW 吞吐，對 MLPerf GB300 再乘 TK GB300 VR-eq → 0.04／0.07／0.13（在 Cerebras 自己 450–2,100 tok/s/user 的工作點）。現值高端 0.8 超出全部證據。Cerebras 的用途是 TK 沒有的超高速層（OpenAI Ultrafast：750 tok/s/user；TK 三層 55–120 tok/s/user）。
- **Cerebras 持有比：兩法差 3.7–7.7 倍，互相衝突。** (i) 每 kW 設備價法：每台 $2.5／3.2／4.0M（皆記者估計）→ 持有比 2.5／3.1／3.9。(ii) OpenAI 合約（S-1：>$20B、750 MW；10-Q 摘要：每期 3–4 年）：750 MW 為 CS-3 系統 IT 功率，換到 TK 每 GW 的 919.8 MW 機架 IT（與 (i) 同基準）→ 每 TK GW 年營收約 $6.1–8.2B，為 VR200 年持有成本的 **0.50／0.57／0.67**，即持有比上限。**但不是硬上限**：OpenAI 取得認股權（3,345 萬股、行使價近 0）與約 $1B 低息貸款，Cerebras Q2 2026 GAAP 毛利率 14.2%，合約可能低於成本定價。依工作單允許，**維持慣例值**。
- **Jalapeño 規格**（2026-06 交付、2026-08 Hot Chips）：MXFP4 13.4 PF（未標 dense）、FP8 dense 3.4 PF、HBM4 216 GB／15.4 TB/s、封裝 TDP 700 W（實測 ≤550 W）。**機架**（SemiAnalysis 免費段落，單一來源、只作佐證）：每 ASIC 機架 128 顆、130 kW，另配主機機架 50 kW 配電（31 kW 實際）→ 機架÷晶片倍數：配電口徑 2.01（與 TK VR200 227 kW 同口徑）、實際 1.80、只算 ASIC 機架 1.45。Broadcom 法說：2027 部署 1.3 GW、2028 超過 5 GW。
- **Jalapeño 推導區間只用方法一（不依賴 InferenceX）**：低＝6.8 PF（FP4＝2×FP8）、倍數 2.01、f 0.75 → 0.33；基準＝10.2 PF（FP4＝3×FP8，比照 TK GB300 FP4 15 對 FP8 5）、倍數 1.66（1.52 與 1.80 的中間）、f 0.75 → 0.59；高＝13.4 PF（dense 讀法）、倍數 1.52、f 1.0 → 1.13。取 0.05 整數倍為 **0.35／0.60／1.15**。（核對意見寫高端 1.00；照指定參數公式為 1.135，1.00 需倍數約 1.72 或 f 約 0.88——交 Project 確認。）
- **方法二降為對照。** OpenAI 自測（InferenceX，每封裝 kW 吞吐對 GB300：DeepSeek R1 1.67×、Kimi K2.5 1.53×）的數據全由 OpenAI 提供，SemiAnalysis「all numbers are provided to us by OpenAI」「We verified the InferenceX runs in person in the lab」；TechRadar 的 1.5× 是同批數據改算，不是獨立佐證。換算後 0.65／0.77／0.95，只撐高端，不進平均。
- **dense 讀法的弱旁證**：SemiAnalysis 把 13.4 PF 與「17.5 PFLOPs of dense Rubin NVFP4 for a single Rubin compute die」並比。
- **OpenAI 客製持有比：界線與現值相容，維持。** Broadcom 執行長：每 GW 內容「$20 to $30 billion」（全部 XPU 客戶；GW 口徑、是否含 HBM／CPU／ODM 皆未說明）→ 界線 0.64／0.82／1.27。
- 標記維持 **Assumed**（與 A–C 段一致）。

## 2. 規格與功率（工作單第 1、2 題；原文口徑）

### Cerebras CS-3（WSE-3）

| 項目 | 數值 | 口徑與來源 |
|---|---|---|
| 峰值 | FP16 **sparse 125 PF**；**dense 12.5 PF** | Cerebras 只發布 125 PF（Flopper「FLOPS are shown as sparse」）；dense 為 The Register 2026-08 規格表（「10x sparsity」）。Next Platform 2024 的「25.6 exaflops」是記者假設情境（稀疏關閉、除以十），與 The Register 同口徑，不是第二來源 |
| FP8／FP4 | 未公布 | Cerebras：推論「in the 16-bit domain for the entire inference run」（2024-08）；本表以 FP16 為最高原生精度 |
| 記憶體 | 44 GB 片上 SRAM、21.6 PB/s；無 HBM／DRAM | The Register、Flopper |
| 系統功率 | **23 kW**（晶圓 15 kW） | The Register「around 23 kW at the system level」；Next Platform「A CS-3 system weighs in at 23 kilowatts」；Flopper「drawing up to 27 kW」（只作產出低端）。不含 MemoryX、SwarmX、主機（未公布） |
| 機架 | 每架 2 台 | Next Platform：OpenAI 750 MW ≈ 32,768 台、16,384 架、753.7 MW（→ 750 MW 為 CS-3 系統 IT 功率） |
| 推論速度（每用戶） | Llama 3.1 70B 450（2024）→ 2,100 tok/s（2025）；gpt-oss-120B 2,700+ | Cerebras（Artificial Analysis）；非整機總吞吐 |
| 整機容量宣稱 | 六座新資料中心「over 40 million Llama 70B tokens per second」、「thousands」台 | Cerebras 2025-03-11；The Register：全部新站「more than a thousand」台 |
| 售價 | **未公布**；記者估 $2.5M（2024）、$3.2M（2026，依 G42 交易）、含配套 $4M；CG-1 $100M／32 台 | Next Platform（記者推論）；S-1 未揭露每台售價與台數 |
| 合約 | OpenAI 750 MW、>$20B（S-1）；每期 3–4 年、另選擇權 1.25 GW（10-Q 摘要）；早期報導 $10B（2026-01）；OpenAI 認股權 33,445,026 股、行使價 $0.00001；OpenAI 工作資金貸款 $1.005B、6% | S-1、10-Q（公司本人說） |
| 新一代 | WSE-3T／CS-4：dense 25 PF、系統約 46 kW（估）、每台 3 片、機架 120–140 kW（記者估），2026 Q3 上線 | The Register 2026-08；TK 第 8 列仍為 WSE-3 |

### OpenAI／Broadcom Jalapeño

| 項目 | 數值 | 口徑與來源 |
|---|---|---|
| 峰值 | **MXFP4 13.4 PF**（未標 dense／sparse）；**FP8 dense 3.4 PF** | OpenAI Hot Chips 2026 投影片（經 STH、Flopper 轉述，「Vendor claimed」）；FP4÷FP8＝3.94（VR200、MI455X 為 2:1；TK GB300 為 3:1，Spec_Rack E40／E41） |
| HBM | HBM4 216 GB、6 堆疊、15.4 TB/s | 同上 |
| 功率 | **封裝 TDP 700 W**；實測持續 ≤550 W | 同上；OpenAI 正規化用 700 W |
| 製程 | TSMC N3P（B0）；A0 矽量測；B0 每瓦 +25%，2027 爬坡 | SemiAnalysis；TechRadar |
| 機架 | **每 ASIC 機架 128 顆**（16 托盤 × 8）＋8 交換托盤；**ASIC 機架 130 kW**；主機機架 **50 kW 配電（31 kW 實際）**；128 顆 600 GB/s 局部域、最多 2,048 顆；Celestica 整合 | SemiAnalysis 2026-08-25 免費段落（單一來源，只作佐證；另經 remio.ai／AI Weekly 轉述）；OpenAI 本人未公布機架功率 |
| 時程與規模 | 2026-06 交付；2026 年底首批部署；2027 1.3 GW；2028 >5 GW（含下一代）；10 GW 至 2029 年底 | OpenAI、Broadcom 法說（2026-09-02）、2025-10-13 新聞稿（GW 口徑未明） |
| 金額 | 無合約金額；Broadcom 每 GW 內容 $20–30B（全部 XPU 客戶）；「half the cost of a GPU」 | Broadcom 執行長（Interested-party） |

## 3. 推導方法（同 A–C 段；逐格在「推導」頁）

1. **產出比**＝`（候選每 kW 峰值算力 ÷ VR200 每 kW 峰值算力）× f`；VR200 NVFP4 35 PF ÷ 3.153 kW ＝ 11.10 PF/kW（FP8 5.55、BF16 1.27）。
2. **Cerebras**：只算界線（C 節）。(a) 12.5 ÷ 23 ＝ 0.543 PF/kW → 0.049；(b) ÷ 1.27 → 0.428；(c) 4,000 萬 tok/s ÷ 1,000–3,000 台 ÷ 23–27 kW ＝ 494–1,739 tok/s/kW，對 GB300 MLPerf Llama2-70B Server 8,470 tok/s/kW（C 段 M05）→ 0.058–0.205，× GB300 VR-eq 0.641 → 0.037–0.132。
3. **Jalapeño 機架倍數**（D4a–D4s）：配電（130＋50）÷（128×0.7）＝2.01；實際（130＋31）÷89.6＝1.80；只算 ASIC 機架 1.45；TK 四世代平均 1.52。產出低／基準／高用 2.01／1.80／1.52。
4. **Jalapeño 推導區間（D16，只用方法一）**：見 §1；f 0.75／0.75／1.0 為 Assumed（GPU 世代 0.66–1.04、C 段 AMD 0.66–0.99）。
5. **Jalapeño 方法二（對照，D14）**：`OpenAI 每封裝 kW 吞吐比 × GB300 倍數 1.349 ÷ Jalapeño 倍數 × GB300 VR-eq 0.641`。峰值吞吐點、單 token 預測。
6. **持有比**＝`1 − s ×（1 − k）`，s＝0.774。Cerebras (i) 每 GW 台數 ＝ 919.8 MW ÷ 23 kW ＝ 39,991 台，乘 VR200 網路加成 1.104；(ii) 每 TK GW 年營收 ＝ 合約值 ÷ 750 MW × 919.8 MW ÷ 年數，再 ÷ VR200 年持有成本 $12.23B。OpenAI：Broadcom 每 GW 內容 × 其他內容加成 × GW 口徑換算。
7. **價格口徑**：Cerebras 估價是記者對售價的估計，與 TK 買方取得價（$8.4M）的關係不明，且無同源 VR200 價可算比值——也是不推點值的原因之一。Broadcom 每 GW 內容是賣方營收，只當界線。

## 4. 敏感度（一次動一個參數）

| 參數 | 變動 | 結果 |
|---|---|---|
| Cerebras (b) × f | 0.5／0.75／1.0 | 產出比 0.21／0.32／0.43 |
| Cerebras 合約值改 $25.4B（剩餘履約義務全數） | 每期 4／3.5／3 年 | 持有比上限 0.64／0.73／0.85 |
| Cerebras 每台價 | $2.5／3.2／4.0M | 持有比 2.50／3.14／3.86 |
| Jalapeño 方法一基準（10.2 PF、f 0.75）改倍數 | 2.01／1.80／1.52 | 0.49／0.55／0.65 |
| Jalapeño 只算 ASIC 機架倍數 1.45 | — | 方法一基準 0.68 |
| Jalapeño 全用 13.4 PF dense（倍數 2.01／1.80／1.52、f 0.5／0.75／1.0） | — | 0.43／0.72／1.13 |
| Jalapeño 全用 6.8 PF | — | 0.22／0.37／0.58 |
| Jalapeño 以持續功率 0.55 kW 計（6.8 PF、倍數 1.80、f 0.75） | — | 0.46 |
| 方法二（對照）改用 Astra 層 VR-eq 0.564 | — | 0.68 |
| 方法二 B0 每瓦 +25%（OpenAI 自述） | — | 0.96（只作上行參考） |
| Jalapeño 持有比：Rasgon $11.5B/GW | — | 0.46（只作下界） |

「必須成立什麼」：
- Cerebras 產出比要到現值基準 0.4：FP16 對齊口徑下需 f≈0.93（接近上限）；現值高端 0.8 需 f≈1.87，不可能。
- Jalapeño：方法一基準 0.59 已等於現值 0.6；方法二（對照）要回到 0.6 需打 0.78 折。

## 5. 交叉檢核（不進建議值）

| 檢核 | 本表 | 外部說法 | 判讀 |
|---|---|---|---|
| Jalapeño vs Broadcom「comparable to Vera Rubin」 | 0.60（基準） | ≈1.0（OpenAI 工作負載） | 本表較保守；Broadcom 轉述 OpenAI，Interested-party |
| Jalapeño 每顆吞吐 | 方法二隱含每顆約 GB300 的 0.83 | 記者：GB300 每顆高 20–25% | 一致（同批數據，非獨立） |
| Jalapeño「half the cost of a GPU」 | 持有比維持 0.8 | 每顆成本一半；每 GW 顆數為 GB300 的 1.5 倍、VR200 的 2.5 倍（每顆所攤 1.26 kW） | 反向證據：k 約 0.64（對 GB300 每顆 $4.3M÷72）–1.25（對 VR200 每顆 $8.4M÷72）→ 持有比約 0.72–1.20；「GPU」指哪一代、是否含 HBM 皆未說明（Q7 替代 c） |
| Cerebras「1/3 lower power、32% lower cost」對 DGX B200 | — | 每 token 成本較低 | 與本表方向相反；Cerebras 自述、無瓦數與條件，且是在其高速工作點比 |
| Cerebras 估價 vs 硬體財報 | 每台 $3.2M | 2025 硬體營收 $358M、毛利約 43% | 若每台 $3.2M，2025 約出貨 110 台——與「數千台」部署規模（多為自用雲端，不計營收）無法核對 |

## 6. 證據強弱與「未找到」

- **強**：Jalapeño FP8 dense、HBM、TDP（OpenAI 投影片）；Cerebras S-1 財務數字與 OpenAI 合約（SEC 文件）。
- **中**：CS-3 23 kW、12.5 PF dense（兩家媒體；源自 Cerebras，dense 為同一換算）；Broadcom 每 GW 內容（執行長說，口徑未明）。
- **弱／只作佐證**：OpenAI 自測（Interested-party，數據由 OpenAI 提供、SemiAnalysis 到場核驗；方法二只作對照）；Jalapeño 機架數字（SemiAnalysis 單一來源）；CS-3 售價（全為記者估計）；Cerebras 容量宣稱與台數；f（Assumed）。
- **互相衝突**：Cerebras 估價 vs OpenAI 合約經濟（差 3.7–7.7 倍）；Cerebras 合約值 $10B（2026-01 報導）vs >$20B（S-1）；CS-3 功率 23 vs 27 kW；Jalapeño 6.8 PF 讀法 vs OpenAI 自測（需 f≈1.6）；Irrational Analysis「五台 $3–5M」（不採用）。
- **已搜尋，未找到**（非「不存在」；證據頁 C11、O08）：CS-3 官方售價、出貨台數、含配套每台功率、整機總吞吐第三方實測、MLPerf、OpenAI 合約每 MW 單價；Jalapeño 機架功率的 OpenAI 本人說法、13.4 PF 的 dense／sparse 明文、每顆或每架價格、OpenAI 對 Broadcom 合約金額、Vera Rubin 對照、非 OpenAI 提供數據的實測；ServeTheHome Hot Chips 原文（只讀到轉述）；SemiAnalysis 付費段落（未讀）。
- **不存在／不可分離**：Jalapeño 為自用晶片，「cannot be rented or bought」（Flopper）——不會有市場價格，只能從 Broadcom 營收端推。

## 7. 方向檢查與覆蓋檢查

- **方向**：本段對 Cerebras 證據**偏不利**（產出界線都不高於現值基準），但不改數值；OpenAI 客製推導基準與現值相同，不改。主動找過反方向證據：(1) Jalapeño：方法二單一來源（降為對照）、記者 MTP 修正（同批改算，不再當佐證）、每 kW 正規化偏向小晶片（改用 SemiAnalysis 機架倍數 1.80–2.01）、A0 矽與首代風險（f 0.75）、6.8 PF 讀法（進低端）；(2) Cerebras：自述成本較低（交叉檢核）、合約可能低於成本定價（(ii) 非硬上限）、超高速層 GPU 吞吐崩潰（OpenAI 自測 GPU 在 169–535 tok/s/user 只剩 118–427 tok/s/kW）——TK 三層 55–120 tok/s/user 不適用，但若 TK 日後加超高速層，Cerebras 在該層可能 >1。
- **覆蓋**：已涵蓋規格、功率（晶片、系統、機架）、精度（2:1、3:1、dense 三種讀法）、公司自述（標 Interested-party）、合約與財報、價格估計。**未涵蓋**：CS-4／WSE-3T（TK 第 8 列仍為 WSE-3；(b) 口徑每 kW 峰值約不變：25 PF ÷ 46 kW ≈ 0.54 PF/kW）；Jalapeño 第二代（Titan 2／A16）；OpenAI 用 Cerebras 超高速層對 TK 層級設計的影響（屬 Project 層級設計）。

## 8. 待 Project 判斷（完整見「待判斷」頁）

1. **Q1 Cerebras 產出比方法**：預設「每 kW 法不適用，只給界線」。替代：(b) × f → 0.21／0.32／0.43；容量換算 0.04／0.07／0.13。
2. **Q2 Cerebras 持有比**：預設維持 0.8／1.0／1.2（兩法衝突）。替代：(i) 2.5／3.1／3.9；(ii) 上限 0.50–0.67（非硬上限）；$25.4B 時上限 0.64–0.85。
3. **Q3 Cerebras 是否寫進 TK 下一版**：預設**數值不改，只更新第 8 列說明欄**。替代：產出比下修為 0.05／0.15／0.45（每 token 成本比 2.5→約 6.7）。
4. **Q4 Jalapeño 13.4 PF 讀法**：r1 三種讀法分端（6.8／10.2／13.4 PF）。
5. **Q5 Jalapeño 機架倍數**：2.01／1.80／1.52（SemiAnalysis 單一來源，只作佐證）；替代全用 2.01 → 基準 0.49；只算 ASIC 機架 1.45 → 0.68。
6. **Q6 OpenAI 客製產出比**：**已決定**——方法二降為對照；推導區間 0.35／0.60／1.15。**待確認**：高端照公式為 1.135（取 1.15），與核對意見的 1.00 不同。
7. **Q7 OpenAI 客製持有比**：預設維持 0.7／0.8／1.0（界線 0.64–1.27）。替代：界線值 0.65／0.80／1.25；「half the cost of a GPU」→ 0.72–1.20。
8. **Q8 OpenAI 客製是否寫進 TK 下一版**：**已決定**——數值不改；只更新第 9 列說明欄（推導區間、Jalapeño 規格、機架證據、Broadcom 界線，移除「無公開規格」）。

## 9. 獨立查核

- 本代理用獨立 Python 腳本（不讀 xlsx 公式）重算。r0：s、Cerebras (a)(b)、容量換算、(i)(ii)、Jalapeño 兩法、持有比界線，一致到小數第 4 位。r1 再對一次：倍數 2.0089／1.7969／1.4509；推導區間 0.3267／0.5936／1.1346；方法二 0.6457／0.7702／0.9486；(ii) 0.5016／0.5732／0.6688；$25.4B 時 0.6370／0.7280／0.8493——全部一致。
- chat 端派出的獨立核對（r0）：數字與重算全部符合；本 r1 依其必修 1–7 修正。

## r1（獨立核對後）

| # | 核對意見 | 修正位置 | 改後 |
|---|---|---|---|
| 1 | 方法二單一來源 | 推導 D14 標記與說明、D16 改公式；證據 O04、O05、新增 O09；建議值第 4–8 列；README §1、§3、§6 | 方法二（0.65／0.77／0.95）降為對照、不進平均，標 Interested-party＋SemiAnalysis 只作佐證；§6 不再列為「強」。推導區間只用方法一：0.327／0.594／1.135 → **0.35／0.60／1.15**。高端照指定參數（13.4 PF、f 1.0、倍數 1.52）為 1.135，不是 1.00（1.00 需倍數約 1.72 或 f 約 0.88），交 Project 確認 |
| 2 | Project 決定 Q6、Q8 | 建議值第 12 列與說明、待判斷 Q6、Q8；README §1、§8 | OpenAI 客製數值不改（0.4／0.6／0.9、0.7／0.8／1.0，每 token 成本比 1.33）；下一版只更新第 9 列說明欄。r0 建議 0.45／0.65／1.05 撤回 |
| 3 | 刪「其他晶片皆 2:1」 | 證據 O03；待判斷 Q4；README §2；推導新增 D2c | 改為「VR200、MI455X 為 2:1，TK GB300 為 3:1（Spec_Rack E40／E41）」；補 SemiAnalysis 13.4 PF 與「17.5 PF dense Rubin NVFP4（單一運算晶粒）」並比，作 dense 讀法弱旁證 |
| 4 | Jalapeño 機架證據 | 推導新增 D4a–D4s、D4 改公式；證據 O09、O03、O08；待判斷 Q5；README §1–§4 | 128 顆／架、ASIC 機架 130 kW、主機機架 50 kW 配電（31 kW 實際）→ 倍數 2.01（配電，同 TK 口徑）／1.80（實際）／1.45（只算 ASIC）；區間 2.01／1.80／1.52；SemiAnalysis 單一來源只作佐證。「機架未公布」改為「OpenAI 本人未公布」 |
| 5 | Cerebras (ii) 口徑對齊 | 推導 C33、C34、F1；證據 C05；待判斷 Q2；README §1、§3、§4、§8 | 750 MW 為 CS-3 系統 IT 功率，換到 TK 每 GW 的 919.8 MW 機架 IT（與 (i) 同基準）：上限 0.545／0.623／0.727 → **0.502／0.573／0.669**；$25.4B 時 0.637／0.728／0.849。**與核對意見的 0.59／0.68／0.79 方向相反**：對齊到 919.8 MW 是把每 MW 營收乘 919.8（同一 TK GW 只有 919.8 MW 的系統），比值變小；0.59 相當於除以 0.92。若 Project 認為 750 MW 含非系統 IT（即對應 TK 的 1,000 MW），則維持 r0 的 0.55／0.62／0.73。補註：OpenAI 認股權（3,345 萬股、行使價近 0）、約 $1B 低息貸款、Q2 毛利率 14.2%，合約可能低於成本定價，不是硬上限 |
| 6 | C04 25.6 EF | 證據 C04；推導 C1 來源；README §2、§6 | 改標「記者假設（if … cut by a factor of ten），與 C01 同口徑」；刪「有第二來源」 |
| 7 | 檔尾 r1、重算、留言 | 本表；審閱檔重建；§9；PR 留言 | LibreOffice 錯誤 0（公式 234 格）；獨立腳本再對一次一致 |

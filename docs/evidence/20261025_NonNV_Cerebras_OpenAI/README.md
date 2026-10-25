# NonNV D 段：Cerebras WSE-3、OpenAI／Broadcom 客製（Jalapeño）（唯讀查證；r0）

- 分支：`claude/evidence-nonnv-cs-oai`（base：master `0c8c1b7`，CURRENT v21.7）；PR #176（draft → ready）
- 工作單：`docs/workorders/20261025_NonNV_Cerebras_OpenAI客製.md`；承接 A 段 `docs/evidence/20261023_NonNV昇騰Maia_A段/`、B 段 `docs/evidence/20261025_NonNV_TPU_Trainium/`、C 段 `docs/evidence/20261025_NonNV_AMD/`
- 審閱檔：`NonNV_Cerebras_OpenAI.xlsx`（四頁：建議值、推導、證據、待判斷；換算全用公式 220 格，LibreOffice 重算錯誤 0）；重建程式 `build_xlsx.py`、`evidence_data.py`；原文引句 `證據原稿.md`
- 分母：`model/20261025_Tokenomics_v21.7.xlsx`（VR200 NVL72 基準欄；數值與 C 段 v21.6 相同）
- 範圍：只寫入本資料夾；未改 `model/`、`builder/`、`tests/`

## 1. 結論（先看這裡）

| 候選 | 產出比 低／基準／高 | 持有比 低／基準／高 | 每 token 成本比（基準） | TK v21.7 現值（產出／持有／成本比） |
|---|---|---|---|---|
| Cerebras WSE-3（CS-3） | **維持** 0.2／0.4／0.8 | **維持** 0.8／1.0／1.2 | 2.5（不變） | 同左 |
| OpenAI／Broadcom 客製（Jalapeño） | 0.45／**0.65**／1.05 | **維持** 0.7／0.8／1.0 | 約 1.23 | 0.4–**0.6**–0.9／0.7–**0.8**–1.0／1.33 |

（原始公式結果：Jalapeño 產出 0.432／0.671／1.068；持有比界線 0.638／0.818／1.269。Cerebras 只有方向界線，見下。）

白話：
- **Cerebras：TK 的每 kW 法不適用，不推點值。** CS-3 每台 23 kW（記者，Next Platform、The Register；Flopper「up to 27 kW」），FP16 dense 12.5 PF（Cerebras 公布的 125 PF 是 10 倍稀疏；兩家媒體同此換算），44 GB SRAM、無 HBM。WSE-3 的瓶頸是記憶體**容量**：每 kW 記憶體只有 VR200 的約 2%，權重與 KV 都要放 SRAM，所以 GPU 世代還原的效率因子 f 不能類比。
- **Cerebras 產出比的方向：現值偏樂觀，但不硬改。** 三個界線：(a) 最高原生精度（FP16 對 VR200 NVFP4）每 kW 峰值比 0.04–0.05；(b) FP16 對齊（對 VR200 BF16 4 PF）0.36–0.43——這是 f＝1 的上限，只與現值基準 0.4 相當；(c) Cerebras 自述「六座資料中心 4,000 萬 Llama-70B tok/s、數千台」換算每 kW 吞吐，對 MLPerf GB300 再乘 TK GB300 的 VR-eq，得 0.04／0.07／0.13（在 Cerebras 自己 450–2,100 tok/s/user 的工作點）。現值高端 0.8 超出全部證據。Cerebras 的用途是 TK 沒有的超高速層（OpenAI Ultrafast：750 tok/s/user；TK 三層 55–120 tok/s/user）。
- **Cerebras 持有比：兩種方法差 3.4–7 倍，資料互相衝突。** (i) 每 kW 設備價法：每台 $2.5／3.2／4.0M（皆為記者估計）→ 每 kW 設備價約 VR200 的 3.7 倍 → 持有比 2.5／3.1／3.9。(ii) OpenAI 合約（S-1：>$20B、750 MW；10-Q 摘要：每期 3–4 年）→ 每 GW 年營收約 $6.7–8.9B，只有 VR200 年持有成本 $12.2B 的 0.55–0.73；營收還要負擔電費、營運與毛利，所以合約隱含的持有比**上限**是 0.55–0.73。Next Platform 記者自己也指出照估價 750 MW 硬體要 $100–131B，與合約規模對不起來。依工作單允許，**維持慣例值**。
- **OpenAI 客製：有新資料，可以推（但全是 Interested-party）。** Jalapeño（2026-06 交付、2026-08 Hot Chips）：MXFP4 13.4 PF（未標 dense）、FP8 dense 3.4 PF、HBM4 216 GB／15.4 TB/s、封裝 TDP 700 W（實測 ≤550 W）；機架未公布。Broadcom 法說：2027 部署 1.3 GW、2028 超過 5 GW。
- **Jalapeño 兩種方法。** 方法一（每 kW 峰值 × f）：保守讀法（dense FP4＝2×FP8＝6.8 PF；機架÷晶片倍數 1.35–1.75）每 kW 峰值比 0.58，f 取 0.5／0.75／1.0（Assumed）→ 0.25／0.43／0.65；若 13.4 為 dense → 0.49／0.85／1.28。方法二（OpenAI 自測 InferenceX，每封裝 kW 吞吐對 GB300：DeepSeek R1 1.67×、Kimi K2.5 1.53×；記者指出對有 MTP 的 GB300 約 1.5×）改成機架功率口徑、再乘 TK 的 GB300 VR-eq 0.641 → 0.74／0.91／1.07。建議：低＝方法一保守 0.43、基準＝兩法平均 0.67、高＝方法二高端 1.07 → **0.45／0.65／1.05**。
- **兩法的一致性檢查。** 保守讀法要與 OpenAI 自測相符需 f≈1.58，超出所有 GPU 世代（0.66–1.04）；dense 讀法只需 f≈0.80。所以「13.4 為 sparse」與「OpenAI 自測可信」不能同時成立——兩者之一偏離，本表各取一半。
- **OpenAI 客製持有比：界線與現值相容，維持。** Broadcom 執行長：每 GW 內容「$20 to $30 billion」（全部 XPU 客戶；GW 口徑、是否含 HBM／CPU／ODM 都未說明）。只算 Broadcom 內容 → 0.64；加 15% 其他內容 → 0.82；設施 GW 且加 35% → 1.27。現值 0.7／0.8／1.0 在其中。
- 標記維持 **Assumed**（與 A–C 段一致）。

## 2. 規格與功率（工作單第 1、2 題；原文口徑）

### Cerebras CS-3（WSE-3）

| 項目 | 數值 | 口徑與來源 |
|---|---|---|
| 峰值 | FP16 **sparse 125 PF**；**dense 12.5 PF** | Cerebras 只發布 125 PF（Flopper「FLOPS are shown as sparse」）；dense 為 The Register 2026-08 規格表（「10x sparsity」）；Next Platform 2024：2,048 台「256 exaflops FP16 with sparse」、關閉稀疏「25.6 exaflops」→ 每台 12.5 PF（第二來源） |
| FP8／FP4 | 未公布 | Cerebras：推論「in the 16-bit domain for the entire inference run」（2024-08）；本表以 FP16 為最高原生精度 |
| 記憶體 | 44 GB 片上 SRAM、21.6 PB/s；無 HBM／DRAM | The Register、Flopper |
| 系統功率 | **23 kW**（晶圓 15 kW） | The Register「around 23 kW at the system level」；Next Platform「A CS-3 system weighs in at 23 kilowatts」；Flopper「drawing up to 27 kW」（本表只作產出低端）。不含 MemoryX、SwarmX、主機（未公布） |
| 機架 | 每架 2 台 | Next Platform：OpenAI 750 MW ≈ 32,768 台、16,384 架、753.7 MW（記者推算 → 750 MW 為 IT 口徑） |
| 推論速度（每用戶） | Llama 3.1 70B 450（2024）→ 2,100 tok/s（2025）；gpt-oss-120B 2,700+ | Cerebras（Artificial Analysis）；非整機總吞吐 |
| 整機容量宣稱 | 六座新資料中心「over 40 million Llama 70B tokens per second」、「thousands」台 | Cerebras 2025-03-11；The Register：全部新站「more than a thousand」台、Minneapolis 512 台 |
| 售價 | **未公布**；記者估 $2.5M（2024）、$3.2M（2026，依 G42 交易）、含配套 $4M；CG-1 $100M／32 台 | Next Platform（記者推論）；S-1 未揭露每台售價與台數 |
| 合約 | OpenAI 750 MW、>$20B（S-1）；每期 3–4 年、另選擇權 1.25 GW（10-Q 摘要）；早期報導 $10B（2026-01） | S-1 為公司本人說；MW 口徑未明 |
| 新一代 | WSE-3T／CS-4：dense 25 PF、系統約 46 kW（估）、每台 3 片、機架 120–140 kW（記者估），2026 Q3 上線 | The Register 2026-08；TK 第 8 列仍為 WSE-3 |

### OpenAI／Broadcom Jalapeño

| 項目 | 數值 | 口徑與來源 |
|---|---|---|
| 峰值 | **MXFP4 13.4 PF**（未標 dense／sparse）；**FP8 dense 3.4 PF** | OpenAI Hot Chips 2026 投影片（經 STH、Flopper 轉述，「Vendor claimed」）；FP4÷FP8＝3.94（其他晶片皆 2:1） |
| HBM | HBM4 216 GB、6 堆疊、15.4 TB/s | 同上 |
| 功率 | **封裝 TDP 700 W**；實測持續 ≤550 W | 同上；OpenAI 正規化用 700 W |
| 製程 | TSMC N3P（B0）；A0 矽量測；B0 每瓦 +25%，2027 爬坡 | AI Weekly 轉述 SemiAnalysis；TechRadar |
| 系統 | 128 顆 600 GB/s 局部域、最多 2,048 顆；機架 Celestica 整合；**機架配置與功率未公布** | OpenAI |
| 時程與規模 | 2026-06 交付；2026 年底首批部署；2027 1.3 GW；2028 >5 GW（含下一代）；10 GW 至 2029 年底 | OpenAI、Broadcom 法說（2026-09-02）、2025-10-13 新聞稿（GW 口徑未明） |
| 金額 | 無合約金額；Broadcom 每 GW 內容 $20–30B（全部 XPU 客戶）；「half the cost of a GPU」 | Broadcom 執行長（Interested-party） |

## 3. 推導方法（同 A–C 段；逐格在「推導」頁）

1. **產出比**＝`（候選每 kW 峰值算力 ÷ VR200 每 kW 峰值算力）× f`；VR200 NVFP4 35 PF ÷ 3.153 kW ＝ 11.10 PF/kW（FP8 5.55、BF16 1.27）。
2. **Cerebras**：只算界線（C 節）。(a) 12.5 ÷ 23 ＝ 0.543 PF/kW → 0.049；(b) ÷ 1.27 → 0.428；(c) 4,000 萬 tok/s ÷ 1,000–3,000 台 ÷ 23–27 kW ＝ 494–1,739 tok/s/kW，對 GB300 MLPerf Llama2-70B Server 8,470 tok/s/kW（15,998 ÷ 1.889 kW；C 段 M05）→ 0.058–0.205，× GB300 VR-eq 0.641 → 0.037–0.132。
3. **Jalapeño 方法一**：每顆所攤 ＝ 0.7 kW × 倍數（1.75／1.52／1.35；1.52＝TK GB200、GB300、VR200 Max-P、Max-Q 四值平均，同 B 段 Trn3）。
4. **Jalapeño 方法二**：`OpenAI 每封裝 kW 吞吐比 × GB300 倍數 1.349 ÷ Jalapeño 倍數 × GB300 VR-eq 0.641`。峰值吞吐點、單 token 預測。
5. **持有比**＝`1 − s ×（1 − k）`，s＝0.774；Cerebras (i) 每 GW 台數 ＝ 919.8 MW ÷ 23 kW ＝ 39,991 台，乘 VR200 網路加成 1.104；(ii) 合約每 GW 年營收 ÷ VR200 年持有成本（上限）。OpenAI：Broadcom 每 GW 內容 × 其他內容加成 × GW 口徑換算。
6. **價格口徑**（工作單規則）：Cerebras 估價是記者對售價的估計，與 TK 買方取得價（$8.4M）的關係不明，且無同源 VR200 價可算比值——這也是不推點值的原因之一。Broadcom 每 GW 內容是賣方營收，口徑最接近「買方取得價的一部分」，所以只當界線。

## 4. 敏感度（一次動一個參數）

| 參數 | 變動 | 結果 |
|---|---|---|
| Cerebras (b) × f | 0.5／0.75／1.0 | 產出比 0.21／0.32／0.43 |
| Cerebras 合約值改 $25.4B（剩餘履約義務全數） | 每期 4／3.5／3 年 | 持有比上限 0.69／0.79／0.92 |
| Cerebras 每台價 | $2.5／3.2／4.0M | 持有比 2.50／3.14／3.86 |
| Jalapeño 倍數 2.0（小晶片固定負載） | — | 方法二 0.69 |
| Jalapeño 方法二改用 Astra 層 VR-eq 0.564 | — | 0.80 |
| Jalapeño 以持續功率 0.55 kW 計（保守讀法） | — | 方法一 0.55 |
| Jalapeño B0 每瓦 +25%（OpenAI 自述） | — | 方法二 1.14（只作上行參考） |
| Jalapeño 持有比：Rasgon $11.5B/GW | — | 0.46（只作下界） |

「必須成立什麼」：
- Cerebras 產出比要到現值基準 0.4：在 FP16 對齊口徑下需 f≈0.93（接近上限）；現值高端 0.8 需 f≈1.87，不可能。
- Jalapeño 產出比維持現值基準 0.6：需方法一保守讀法 f≈1.04，或方法二打 0.66 折。

## 5. 交叉檢核（不進建議值）

| 檢核 | 本表 | 外部說法 | 判讀 |
|---|---|---|---|
| Jalapeño vs Broadcom「comparable to Vera Rubin」 | 0.65（基準） | ≈1.0（OpenAI 工作負載） | 本表較保守；Broadcom 轉述 OpenAI，Interested-party |
| Jalapeño 每顆吞吐 | 方法二隱含每顆約 GB300 的 0.83 | 記者：GB300 每顆高 20–25% | 一致 |
| Jalapeño「half the cost of a GPU」 | 持有比維持 0.8 | 每顆成本一半；每 GW 顆數為 GB300 的 1.8 倍、VR200 的 3.0 倍（每顆所攤 1.06 kW） | 反向證據：k 約 0.76（對 GB300 每顆 $4.3M÷72）–1.48（對 VR200 每顆 $8.4M÷72）→ 持有比約 0.81–1.37，高於現值基準；「GPU」指哪一代、是否含 HBM 皆未說明，只列交叉檢核（Q7 替代 c） |
| Cerebras「1/3 lower power、32% lower cost」對 DGX B200 | — | 每 token 成本較低 | 與本表方向相反；Cerebras 自述、無瓦數與條件，且是在其高速工作點比 |
| Cerebras 估價 vs 硬體財報 | 每台 $3.2M | 2025 硬體營收 $358M、毛利約 43% | 若每台 $3.2M，2025 約出貨 110 台——與「數千台」的部署規模（多為自用雲端，不計營收）無法核對 |

## 6. 證據強弱與「未找到」

- **強**：Jalapeño FP8 dense、HBM、TDP（OpenAI 投影片）；OpenAI 自測數字（公開頁面；工具為第三方公開基準）；Cerebras S-1 財務數字與 OpenAI 合約（SEC 文件）。
- **中**：CS-3 23 kW、12.5 PF dense（兩家媒體；源自 Cerebras）；Broadcom 每 GW 內容（執行長說，口徑未明）。
- **弱**：CS-3 售價（全為記者估計）；Cerebras 容量宣稱與台數；Jalapeño 機架倍數（Analogy）。
- **互相衝突**：Cerebras 估價 vs OpenAI 合約經濟（差 3.4–7 倍）；Cerebras 合約值 $10B（2026-01 報導）vs >$20B（S-1）；CS-3 功率 23 vs 27 kW；Jalapeño 13.4 PF 保守讀法 vs OpenAI 自測（需 f≈1.6）；Irrational Analysis「五台 $3–5M」（不採用）。
- **已搜尋，未找到**（非「不存在」；證據頁 C11、O08）：CS-3 官方售價、出貨台數、含配套每台功率、整機總吞吐第三方實測、MLPerf、OpenAI 合約每 MW 單價與 MW 口徑；Jalapeño 機架配置與功率、13.4 PF 的 dense／sparse 原文、每顆或每架價格、OpenAI 對 Broadcom 合約金額、Vera Rubin 對照、非 OpenAI 的實測；ServeTheHome Hot Chips 原文（只讀到轉述）。
- **不存在／不可分離**：Jalapeño 為自用晶片，「cannot be rented or bought」（Flopper）——不會有市場價格，只能從 Broadcom 營收端推。

## 7. 方向檢查與覆蓋檢查

- **方向**：本段對 Cerebras 證據**偏不利**（產出界線都不高於現值基準），但建議不改數值；對 OpenAI 客製**偏有利**（產出 0.6→0.65；每 token 成本比 1.33→1.23）。主動找過反方向證據：(1) Jalapeño：記者 MTP 修正（1.5×，進低端）、每 kW 正規化偏向小晶片（改機架倍數，進方法二）、A0 矽與首代風險（f 低端 0.5）、OpenAI 時機可疑（記者），以及保守讀法本身（進低端）；(2) Cerebras：Cerebras 自述成本較低（列交叉檢核）、超高速層 GPU 吞吐崩潰（OpenAI 自測 GPU 在 169–535 tok/s/user 只剩 118–427 tok/s/kW）——在 TK 三層 55–120 tok/s/user 不適用，但若 TK 日後加超高速層，Cerebras 在該層可能 >1。
- **覆蓋**：已涵蓋規格、功率（晶片與系統）、精度（兩種口徑）、公司自述（標 Interested-party）、合約與財報、價格估計。**未涵蓋**：CS-4／WSE-3T（2026 Q3 上線，TK 第 8 列仍為 WSE-3；若改列新一代，(b) 口徑每 kW 峰值比約不變：25 PF ÷ 46 kW ≈ 0.54 PF/kW）；Jalapeño 第二代（Titan 2／A16）；OpenAI 使用 Cerebras 的超高速層對 TK 層級設計的影響（屬 Project 層級設計，不在本段）。

## 8. 待 Project 判斷（完整見「待判斷」頁，每題附預設與替代）

1. **Q1 Cerebras 產出比方法**：預設「每 kW 法不適用，只給界線」。替代：(b) 口徑 × f → 0.21／0.32／0.43；容量換算點值 0.04／0.07／0.13。
2. **Q2 Cerebras 持有比**：預設維持 0.8／1.0／1.2（兩法衝突）。替代：(i) 2.5／3.1／3.9；(ii) 上限 0.55–0.73；$25.4B 時上限 0.69–0.92。
3. **Q3 Cerebras 是否寫進 TK 下一版**：預設**數值不改，只更新第 8 列說明欄**（引本資料夾、每 kW 法不適用原因、產出界線、持有比衝突）。替代：產出比下修為 0.05／0.15／0.45（每 token 成本比 2.5→約 6.7）。
4. **Q4 Jalapeño 13.4 PF 讀法**：預設保守讀法（6.8 PF dense）進低端、與方法二平均進基準。替代：dense 讀法 0.49／0.85／1.28。
5. **Q5 Jalapeño 機架倍數**：預設 1.75／1.52／1.35。替代：2.0 → 方法二 0.69。
6. **Q6 OpenAI 客製產出比是否以自測進基準**：預設 0.45／0.65／1.05。替代：維持 0.4／0.6／0.9；只用方法二 0.74／0.91／1.07。
7. **Q7 OpenAI 客製持有比**：預設維持 0.7／0.8／1.0（界線 0.64–1.27 相容）。替代：界線值 0.65／0.80／1.25；反向交叉檢核「half the cost of a GPU」→ 0.81–1.37（口徑不明）。
8. **Q8 OpenAI 客製是否寫進 TK 下一版**：預設**產出比換成 0.45／0.65／1.05、持有比維持**（說明欄引本資料夾、補 Broadcom 界線、移除「無公開規格」）；每 token 成本比約 1.23。保守替代：數值全不改，只更新說明欄。

## 9. 獨立查核

- 本代理用獨立 Python 腳本（不讀 xlsx 公式）重算 s、Cerebras (a)(b) 峰值比、容量換算、(i)(ii) 持有比、Jalapeño 方法一（兩種讀法）與方法二、建議基準 0.6712、持有比界線，與 LibreOffice 重算值一致到小數第 4 位。
- 依工作單，合併前由未參與的代理獨立核對（索引 0b）。

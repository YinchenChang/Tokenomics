# DeepInfer 對 Tokenomics v21.7 的檢核與啟示（2026-10-26）

模式：LIGHT（技術假設檢核）。本檔只並排與推算，**不改模型**；改模型的判斷題放第 5 節，附預設。

## 0. 一句話結論

DeepInfer 公布的 GB200（推定）實測顯示：**TK 的 prefill 大致對得上，decode 每卡產出低估約 3.6–4.7 倍**（主因是每序列算力效率 η_d：TK 4.1%，DeepInfer 隱含約 13–23%）。但這**不能直接改 TK**：同一個軟體效率若套到所有層級，TK 的 token 帳缺口會從 1.52 擴大到 3.4–4.5 倍，與需求面證據衝突；而且效率提升在競爭下會透過價格下跌（L）回吐。好消息是：**TK 的主判讀（回本比值 0.94）對 η_d 幾乎不敏感**（η_d ×5 時 0.934），會翻的是「回本所需單價」這類以產能推的指標。DeepSeek 的「每卡時 38 美元」可由公開數字完整重建（39.1 美元），它是「生產吞吐 × 谷價牌價、全部計費」的**產能營收**，不是實收營收，不能當 m 或回本證據。

## 1. 來源與標記

| # | 內容 | 標記 | 出處 |
|---|---|---|---|
| S1 | DeepInfer repo（commit `553741557a`，2026-10-25）：README、`doc/inference_deployment_qa.md`、三張 Pareto 圖、`examples/sweep/run_sweep.sh` | [Interested-party] DeepSeek；程式開源可重現，基準為離線測試 | github.com/deepseek-ai/DeepInfer |
| S2 | 「單一集群 155 兆 token／日」「每卡每小時 38 美元（按谷價）」 | [Interested-party] DeepSeek 本人說（QA 文件原文） | S1 |
| S3 | 生產數字：平均輸入 77K、快取命中 96%、prefill 每卡未快取 60K tok/s（含快取 1.5M）、decode 每卡 14K tok/s、每用戶 230 tok/s、TTFT 400 ms | [Interested-party] DeepSeek 知乎官方文章（2026-10-20）「實際線上運行數據」表，**一手已讀**（10-26 19:20 以內建瀏覽器開啟原圖）；另有 TTFT P99 1,000 ms、KV「不活躍後保存 72 小時」；表頭註「機器已經預留了一定冗餘度，以應對流量的波動」；表尾註「實際部署 P:D 接近 1:1，不考慮波峰波谷，整體收入是平均每卡每小時 38 美金（按谷價）」。表內**未寫硬體**。 | zhuanlan.zhihu.com/p/2095560295930508953 |
| S4 | V4.1 Flash 價目（每 M）：快取命中 0.003／未命中 0.15／輸出 0.60（谷價；峰價 2 倍；峰時 UTC 01–04、06–10 週一至五） | [Verified] 官方價目頁，經二手轉述（eesel、SiliconFlow 兩家一致）；TK `Price_Frontier` 第 12 列已有同價（時段係數 0.604） | eesel.ai、siliconflow.com |
| S5 | V4.1 Flash 架構：552B＋196B Engram；啟用 prefill 8B／decode 16B；CED 20＋20 層；全域 KV 890 B/token | [Interested-party]，經二手轉述 | siliconflow.com |
| S6 | 評論者推算（Latent Space 彙整）：日營收約 2,200 萬美元、每 GW 約 1,660 億美元、毛利 >80%；Teortaxes 昇騰 950 對 GB200 每卡比 | 二手推論，非 DeepSeek 說 | latent.space |

硬體推定：README 寫「NVIDIA SM100」、decode 64 卡「在同一 scale-up domain」→ 只有 NVL72 機櫃能做到，推定 **GB200 NVL72** [Derived]；vLLM 團隊稱「DeepInfer 公布的 GB200 結果」（二手）方向一致。

## 2. 數字檢核（先算，後判讀）

### 2.1 「38 美元／卡時」重建 [Derived，輸入 S3、S4]

以 1 張 prefill 卡＋1 張 decode 卡（DeepSeek 說 P:D 約 1:1）每小時計：

| 分項 | 每卡平均量 | 谷價 $/M | 每卡時營收 | 占比 |
|---|---|---|---|---|
| 未快取輸入 | 30,000 tok/s | 0.15 | 16.20 | 41% |
| 快取命中輸入 | 720,000 tok/s | 0.003 | 7.78 | 20% |
| 輸出 | 7,000 tok/s | 0.60 | 15.12 | 39% |
| **合計** | | | **39.10** | 對 DeepSeek 38：1.03 倍 |

- 155 兆／日 ÷（1.514M tok/s 每對）→ 約 **2,370 張卡**（Latent Space 寫約 2,400，一致）。
- 日營收（谷價、全部計費）＝ 2,370 × 38 × 24 ≈ **216 萬美元／日**。**Latent Space 寫「約 2,200 萬美元／日」錯了 10 倍**（把 155 兆 token 全以混合 0.14 計，忽略 95% 是 0.003 的快取命中）。其「每 GW 1,660 億」則與 38 × 每 GW 卡數一致。
- 判讀：38 美元可用「生產吞吐 × 谷價牌價」完整重建 → 它是**產能營收（假設全部按 API 谷價計費）**。同一系統也服務 chatbot 流量（QA 文件：TTL 7 天）；DeepSeek App 免費，故推論其中有未付費流量 [Derived]，所以不是實收。讀法二（實收）需要「全部流量付費且無折扣」，不成立。**一手佐證**：知乎原表註明「不考慮波峰波谷」，即 38 美元未計流量起伏造成的閒置；表頭又說機器已預留冗餘度——兩者合讀：38 美元是「忙碌時的每卡吞吐 × 谷價」，不是時間平均的實收。

### 2.2 decode 吞吐：TK 對 DeepInfer（同為 V4-Flash 類、GB200）

| 項目 | TK v21.7（Perf F 欄，Luna、GB200） | DeepInfer（S1 圖，EP64、131K 上下文） | 標記 |
|---|---|---|---|
| 每用戶速度 | 84.3 tok/s（SLO） | 103（256 req）／178／246／297／315／325（8 req） | |
| decode tok/s/卡 | **5,636** | **26,300**（103 tok/s/user）／22,800／15,700／9,500／5,050／2,600 | [Interested-party] |
| 每步接受 token | 2.533（N=3、α=0.70） | 3.25（基準設定）；生產 3.2–3.3（N=5 動態） | |
| 每步固定延遲 | 8.70 ms | 約 9.5 ms（由 8–64 req 外推） | [Derived] |
| 每序列每步時間 | **0.319 ms** | **0.057–0.104 ms**（隨批次與長上下文注意力上升） | [Derived] |
| 隱含 η_d | 4.11% | **約 13–23%**（同 TK 公式：4 token × 32.8 GFLOP ÷（10 PF × 0.104–0.057 ms）） | [Derived] |

- 在**更嚴格**的每用戶速度（103 > 84）下，DeepInfer 已達 26,300 → **4.67 倍**；扣除接受長度差（3.25 ÷ 2.533 = 1.28）後仍 **3.64 倍**。
- 差距幾乎全在 η_d；固定延遲兩邊接近。V4.1 Flash decode 啟用 16B（TK Luna 13B）且上下文 131K（TK 8.7K），這兩點都讓 DeepInfer 更難，所以 3.6 倍偏保守。
- 生產核對：用 DeepInfer 參數（固定 9.5 ms、每序列 0.078 ms、τ 3.25）推 230 tok/s/user → 約 59 序列／卡、13,600 tok/s，對上 DeepSeek 說的生產 14K（約 60 序列／卡）。
- **生產 ÷ 基準（讀法依方法而異）**：同每用戶速度比（230 tok/s/user 內插 17,370）→ 0.81；同並行數比（約 60 序列／卡，QA 表估 14,466）→ 約 0.97；14K ÷ 15.7K（64 序列點）→ 0.89。DeepSeek 自述「負載平衡約達完美平衡離線基準的 80%」指的是負載平衡。另：生產集群硬體 Latent Space 寫「SM100／A950」，**可能部分是昇騰**，與 GB200 基準相比有硬體口徑風險。→ 對 TK `CTL_ProdDerate` 0.85（Assumed，0.72–0.95）是**佐證範圍 0.80–0.97**，不是量測點。
- TK 的 η_d 是用 InferenceX 2026-07「最佳前緣」（V4-Pro、GB300）擬合的；vLLM 現稱距 DeepInfer GB200 結果 6% 內（二手、競爭方自報）。**TK 的 decode 效率反映的是開源軟體 2026 年中的前緣，已被追上並超越。** TK 現有 η_d 敏感度只到 ×0.5／×1.5（Sens_Perf），DeepInfer 在區間外。

### 2.3 prefill：大致對得上

| | TK（Luna、GB200） | DeepInfer |
|---|---|---|
| prefill tok/s/卡 | 91,689（ISL 8K、平均位置 4K、η_p 0.30） | 60K–89K（131K 上下文、批次 4K–64K、bounded replay）；生產 60K（平均輸入 77K） |

TK 在短上下文下 9.2 萬、DeepInfer 在長上下文下 6–9 萬，方向與量級一致。V4.1 的 CED／bounded replay「prefill 計算近乎減半」是架構改變，TK 可用 Tech_Registry `H_FLOP` 掛鉤表達，不必動 η_p。

### 2.4 工作負載：真實流量遠比 TK 參考請求「重輸入、重快取」

| | TK | DeepSeek 生產 |
|---|---|---|
| 快取命中率 | `B4_CacheHit` 0.55；Workload χ 聊天 0.5、代理 0.9 | **0.96**（按 token） |
| 輸入：輸出（含快取） | Luna 參考 8:1；coding agent 49:1 | **107:1**（每請求約 77K 入、約 720 出） |
| prefill 卡占比 | Luna GB200 18% | **約 50%** |

### 2.5 同一把尺：TK 用 DeepSeek 價目算每卡時營收

TK Luna、GB200、100% 利用、全部計費、套 DeepSeek 谷價：

| 分項 | TK 每卡平均量 | 每卡時營收 | DeepSeek | 差額 |
|---|---|---|---|---|
| 未快取輸入 | 16,613 tok/s | 8.97 | 16.20 | +7.23 |
| 快取命中 | 20,305 tok/s | 0.22 | 7.78 | +7.56 |
| 輸出 | 4,615 tok/s | 9.97 | 15.12 | +5.15 |
| 合計 | | **19.16** | **39.10** | **+19.94（2.04 倍）** |

差距三分：輸出吞吐（decode 效率）、未快取輸入（P:D 配比與長輸入）、快取命中量（96% 命中、每請求 77K）分別約占差額 26%、36%、38%。**TK 的 Luna 單位營收約為 DeepSeek 產能營收的一半，主因不只是 η_d，還有工作負載形狀。**

### 2.6 營收／持有成本

- TK GB200 經濟持有成本：8.83 $B/GW·年 ÷ 501,768 卡 ÷ 8,760 h ＝ **2.01 美元／卡時** [Derived]。
- DeepSeek 38 ÷ 2.01 ＝ **18.9 倍**；TK 同口徑（Luna、DeepSeek 谷價、100%）19.16 ÷ 2.01 ＝ 9.5 倍；TK 現行（OpenAI Luna 有效價、利用 0.6）3.59 倍。
- 評論者用 5–8 美元／卡時（「全成本」）得毛利 >80%；用 TK 持有成本則約 95%。兩者都只是產能毛利，不含免費、閒置、訓練。

### 2.7 KV 快取儲存

- DeepSeek：3FS 全 SSD 約 100 PiB；TTL 代理 3 天、聊天 7 天；每卡邏輯 14.4 TB；10+2 糾刪碼。
- TK `Cache_Store`：採 DRAM 層，等效保留約 1 分鐘，每 M 命中 $0.000013（Luna）。
- 以 TK 自己的 SSD 單價（$20/TB·年）× 14.4 TB × 1.2 → **約 $0.04／卡時，占 GB200 持有成本約 2%**；若以 100 PiB ÷ 2,370 卡（每卡約 47 TB 實體）→ 約 $0.11，約 5%。結構與 TK 不同（容量型、按卡計，不是按命中 token 計），但量級仍屬次要。

## 3. η_d 敏感度（只改 Calib 第 67 列各世代 η_d 倍數 × k，LibreOffice 重算）

k＝1 重算後與模型快取值逐位相同（LibreOffice 口徑確認）。k＝5 時 Luna GB200 decode 28,180，與 DeepInfer 26,300 同量級（DeepInfer 對應 k 約 4.7）。

| 輸出 | k＝1（現行） | k＝3 | k＝5 | 讀法 |
|---|---|---|---|---|
| Luna GB200 decode tok/s/卡（Perf F88） | 5,636 | 16,908 | 28,180 | 對 DeepInfer 26,300 |
| Sol GB300 decode（J88） | 1,836 | 5,507 | 9,179 | |
| `L1_TokLedger_GW25`（模型付費 token ÷ 需求面） | **1.52** | **3.43** | **4.52** | 缺口擴大 |
| `L1_RevGW_PQ_VR200`（$B/GW·年） | 49.5 | 116.0 | 152.3 | |
| `L1_PriceReqBE`（回本所需單價 $/M；對照有效牌價 1.359） | **1.634** | **0.725** | **0.553** | **在 k 約 1.25 時翻轉**（粗估） |
| `L1_LTotalFleetVDisc` ÷ `L1_LReqFleet_Full`（主判讀） | 0.940 | 0.938 | 0.934 | **幾乎不動** |
| `L1_M` | 1.355 | 1.355 | 1.355 | 不動（m 只看收入面） |

讀法：
- **主判讀（回本比值 0.94、未定）對 η_d 不敏感**：L 與所需 L 都錨在實際價格與實際營收，不經過理論產能。這是 TK 1.4、1.5 規格的好處。
- **會翻的是以產能推的指標**：`L1_PriceReqBE` 只要 η_d 提高約 25% 就從「現價不夠」變成「現價足夠」。這類指標在 TK 文件中要標明「依賴 η_d」。
- **token 帳是衝突所在**：η_d 若是 DeepInfer 量級且適用 OpenAI，模型付費 token 會是需求面的 3.4–4.5 倍。要讓兩者相容，必須至少一項為真：(i) OpenAI 實際利用率只有 TK 0.41 的約 1/2.3–1/3（約 0.13–0.18）；(ii) OpenAI 的每 token 算力遠重於 TK 的 Sol／Astra 代表架構；(iii) 需求面 token 計數低估 2–3 倍（例如未含快取命中）；(iv) 閉源方的服務效率遠低於 DeepInfer。目前沒有證據能分辨四者。

## 4. 啟示（依 [P] 物理、[A] 會計恆等式、[I] 誘因／資訊 三類）

**[P] 物理／產能**
1. **decode 效率（η_d）是 TK 最過時的參數**：DeepInfer 隱含約 13–23%，TK 4.1%。但它不是孤立參數：TK 的 token 帳與 P×Q 都建在它上面（見第 3 節）。
2. **生產折減有了佐證範圍 0.80–0.97**（依比較方法；且生產硬體可能混有昇騰）；TK 0.85 在其中，不需改。
3. **P:D 配比由工作負載決定**：decode 變便宜後，prefill（新鮮輸入、長上下文）成為成本主體，快取命中率成為一級經濟變數。
4. **架構漂移**：V4.1 Flash（CED、KV 890 B/token、decode 16B／prefill 8B）已取代 TK Luna 代表架構 V4-Flash（KV 2,795）；V4-Pro 是否在 9 月 14 日起轉給 Flash **來源互相矛盾**（TechNode：「requests to V4 Pro will be routed to V4.1 Flash」；SiliconFlow：「deepseek-v4-pro will continue」），待官方公告確認。
5. **NonNV 昇騰**：DeepInfer 同一程式碼跑 GB200 與昇騰 950，是目前最乾淨的同軟體跨硬體比較來源（TK 規則：跨晶片先對齊精度）。評論者數字（950DT 約 GB200 的 0.135–0.20）屬二手；**DeepSeek 知乎原文只有 NVIDIA 的兩張基準圖，沒有昇騰數據**（10-26 已查）→ 昇騰列暫無可用的一手來源，要等 DeepSeek 或第三方以 DeepInfer 在 950 上跑出曲線。

**[A] 會計恆等式**
6. **每卡時營收＝Σ（各類 token 吞吐 × 各類單價）**：DeepSeek 的 38 美元中 41% 來自未快取輸入、只有 39% 來自輸出。TK 的 P 是單一混合價 × 總 token，混合權重（ISL/OSL、χ）一變，P 就變；P 與 Q 必須同一 token 口徑。
7. **token 計數口徑**：155 兆／日中約 95% 是快取命中輸入。TK 需求面付費 token（`AL_DPaid`）所引用的公開 token 量，要逐一標明是否含快取命中，否則 token 帳 1.52 的意義不明。
8. **谷價／峰價**：TK `Price_Frontier` 時段係數 0.604（峰時占週時數 20.8%）與官方時段一致，無須改。

**[I] 誘因／資訊**
9. **把互補品商品化**：DeepSeek 賣模型與 API，開源推理框架讓任何雲都能以接近 DeepSeek 的成本服務 V4.1 Flash（vLLM 數週內追上）→ 低層級 token 的成本與價格地板同步下移。**效率提升會透過 L（壽命期價格下跌）回吐**；TK 若只調 η_d（Q 上升）而不同步看 L，會重複計算好處。
10. **揭露誘因**：38 美元選谷價（較保守的牌價）但假設全部計費、滿載（產能口徑），與 2025-02「理論成本利潤率 545%」同一種揭露法：方向上有利於展示效率。數字可重建、程式可重現，可信度高於一般自報，但口徑要照本檔 2.1 讀。

**涵蓋檢查**：三類各有候選；未涵蓋的層：需求面（DeepSeek 未揭露實收、付費占比、利用率）——屬資料不可得，非遺漏。方向檢查：本檔 4 個口徑選擇中，3 個保留 Andy 原有的自由度（不改 m、不改 L、不改 η_d），1 個收窄（把 38 美元讀為產能營收、排除實收讀法；理由見 2.1）。

## 5. 判斷題（附預設；未回應即照預設，可撤回）

| 題 | 選項 | 預設 |
|---|---|---|
| D1 η_d 是否改用 DeepInfer 量級 | (a) 不改，只加敏感度情境 ×3、×5；(b) 只改 Luna 層級；(c) 全層級改 | **(a)**：理由是第 3 節 token 帳衝突與 L 回吐；先把 ×3、×5 情境加進 Sens_Perf，等 OpenAI 等閉源方有第二來源再定 |
| D2 `CTL_ProdDerate` 基準 | 0.85 維持／改 0.80 | **維持 0.85**，說明加「DeepInfer 佐證 0.80–0.97」；標記仍 Assumed；區間 0.72–0.95 不變 |
| D3 Luna 代表架構換 V4.1 Flash | 換／不換 | **下一主版換**（KV 890、啟用 16B／8B、CED prefill 減半用 `H_FLOP`）；Sol 代表架構維持；V4-Pro 是否已轉給 Flash 先查官方公告 |
| D4 `B4_CacheHit` 0.55 | 維持／提高 | **維持**，加 DeepSeek 0.96 為對照（單一廠商、代理流量占比高，不能直接外推 OpenAI） |
| D5 快取儲存改按卡計 | 改／不改 | **不改**（2–5%，次要）；記錄於證據檔 |

## 5b. 獨立核對
未參與製作的代理已逐項核對（repo、v21.7 活頁簿、重算紀錄、五個網址）：數字全數重現；更正 2 處（V4-Pro 轉向說法、η_d 上緣 26%→23%），收斂 4 處過度推論（生產折減、免費流量、5–8 美元口徑、生產硬體可能含昇騰），均已改入本檔。

## 6. 下一步

1. ~~讀 DeepSeek 知乎原文~~（10-26 完成：生產數字已改一手；無昇騰數據）。可用 `examples/sweep/run_sweep.sh` 在 950 上重跑的第三方結果出現時，再更新 NonNV 昇騰列。
2. 把本檔與 `calc.py` 放進 Tokenomics `docs/evidence/20261026_DeepInfer/`（本串無 repo 寫入權限，下次有權限的串處理）。
3. D1 照預設時：下一版 TK 在 Sens_Perf 加「η_d × 3／× 5（DeepInfer 量級）」兩組情境。
4. 交接檔第 4 節 E「Blackwell 實測吞吐」：本檔提供第一筆（DeepSeek 自報、GB200 推定）。

## 來源

- [DeepSeek 知乎：DeepSeek V4.1 Flash 大規模推理部署實踐](https://zhuanlan.zhihu.com/p/2095560295930508953)
- [DeepInfer repo](https://github.com/deepseek-ai/DeepInfer)
- [Latent Space AINews：DeepSeek DeepInfer open source](https://latent.space/p/ainews-deepseek-deepinfer-open-source)
- [人人都是產品經理：DeepSeek 开源推理框架：96% 的输入都不用重新计算](https://www.woshipm.com/ai/6481653.html)
- [第一財經](https://www.yicai.com/news/103401110.html)
- [eesel：DeepSeek V4.1 Flash pricing](https://www.eesel.ai/blog/deepseek-v4-1-flash-pricing)
- [TechNode：V4 Pro 請求轉給 V4.1 Flash](https://technode.com/2026/09/10/deepseek-formally-launches-v4-1-flash-routes-v4-pro-requests-to-flash/)
- [SiliconFlow：DeepSeek V4.1 Flash architecture and pricing](https://www.siliconflow.com/zh-tw/blog/deepseek-v4-1-flash-api-migration)

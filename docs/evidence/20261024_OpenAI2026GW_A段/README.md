# OpenAI 2026 年上線算力 A 段：2026 平均 GW 與回本比值趨勢

分支 `claude/evidence-openai-2026-gw`　基準 master `45ce1ca`　唯讀查證，未改 `model/`、`builder/`、`tests/`。
檔案：`OpenAI2026GW_A段.xlsx`（換算與比值全用公式，LibreOffice 重算錯誤 0）、`證據原稿.md`、`進度.md`。
承接：`docs/evidence/20261023_Q側缺口_A段/`、`claude/evidence-azure-price` 分支的 Azure 實付價 A 段（不重查）。

## 結論先行

1. **找不到任何 OpenAI 自己公布的 2026 年「上線」GW。** OpenAI 只公布了 2025 年底 1.9 GW（Friar，利害關係方）與 2026-04-29 的「已簽約 10GW」（DCD 判斷為簽約而非上線）；內部備忘錄對自己的 2026 年底寫「未載」。所以 2026 GW **沒有直接來源**，只能用旁證框出 Derived 區間，輸入仍是 Assumed。
2. **區間（Derived，輸入含 Assumed）**：
   - **2026 平均上線 GW：2.5–3.8，基準 2.8（後重）–3.2（線性）。** 支出法交叉檢查（Brockman：2026 年算力支出 500 億）為 2.2–3.9，平價且用 204 億基準時 2.8。你現用的 Assumed 2.5／3.0／3.5 落在區間中段，**沒有被推翻，也沒有被證實**。
   - **2026 Q2 末時點 GW：2.3–3.8，基準 2.6（後重）–3.2（線性）**；Q2 季平均 2.2–3.3。
   - 方法：2025 年底 1.9 GW 起算，2026 年底取三種（低 3.5＝OpenAI 對 Anthropic 的估計中點，Analogy；基準 4.6＝以 2027「low double-digit」11 GW 做幾何插值，Assumed；高 5.7＝Friar 的 3 倍／年延續），再配兩種季別形狀（線性；後重＝AMD、Nvidia、Cerebras、新站都在下半年起）。
3. **趨勢方向：偏向下降，但只有 Q2 時點口徑能判定，全年口徑判不了。**
   - **Q2 年化營收 263 億配 Q2 末 GW**：持平門檻 2.17 GW；六情境的 Q2 末 GW 最低 2.30，倍數 **0.57–0.94（比值全部低於 2025 的 1.239）**。若改配 Q2 季平均，最低 2.18 剛好等於門檻（0.99），其餘更低。要翻成上升，H1 新增必須 ≤0.27 GW，與 CoreWeave、Oracle、Microsoft 的全客戶交付量（見下表）不相容，但這是旁證，不是證明。
   - **FY2026 營收 350 億配全年平均 GW**：持平門檻 2.88 GW，正好落在區間中央。六情境倍數 **0.76–1.17，基準 0.89–1.02**。低情境會上升（1.07–1.17），線性與高情境會下降（0.76–0.89）。**方向不可判定**，中心略偏下。
   - h 取 9.731 或 9.796 差 0.5% 以內，不影響方向（xlsx「比值」兩欄並列）。
4. **API token（SRC_DEM_011）**：沒有 2026 Q2 或之後的新數字。「>15B token／分鐘」是 **2026 Q1 末**時點，OpenAI 於 2026 年 4 月揭露（Exponential View 2026-04-06：自 2025-10 的 6B 成長 2.5 倍），與現用 150 億／分（2026-03）是同一個數。**ChatGPT 每日訊息數**：最新可核實仍是 2025-07 的 2.5B+，2026 新值與你現用的 3.6B／日**都未找到出處**。另記：每週活躍用戶 900M（2026-02）→ >1B（OpenAI 2026-09-08 確認）。
5. **決定趨勢的單一變數仍是 2026 平均 GW**，而它目前沒有直接證據。最能判定的新資料：OpenAI 或 Epoch 公布 2026 年中的全體上線 GW、或 Microsoft／Oracle／CoreWeave／AWS 揭露 OpenAI 專屬交付（皆已搜尋，未找到）。

## 證據表（完整見 xlsx「證據表」；同源算一筆）

| 編號 | 項目 | 數值與口徑 | 標記 | 用途 |
|---|---|---|---|---|
| G01＋G02 | Friar：2025 年底 1.9 GW；Epoch 換成 1.743M H100e（CI 1.25–2.19M）| 年底時點；IT 或設施未明（Epoch 假設 IT）| Interested-party：OpenAI CFO，募資／IPO 誘因（G02 同源，不另計）| 基點 E0 |
| G03 | Altman：2025 年底前 well over 1M GPUs | 預告 | Interested-party：OpenAI CEO（沿用前段）| 與 1.9 GW×63 萬顆／GW＝120 萬顆相容 |
| G04 | OpenAI 2026-04-29：已超過 10GW，90 天 added >3GW | **簽約，非上線**，美國 | Interested-party：OpenAI | 不能用於上線量 |
| G05 | 投資人備忘錄（Tae Kim 二手）：已識別 >8GW；估 Anthropic 2026 年底 3–4 GW；OpenAI 自己 2026 年底未載 | 規劃／對手估計 | Interested-party；二手 | 低情境弱下界 |
| G06＋G07 | Epoch：Abilene 2026-04 上線 0.3 GW（約 8 棟中 4 棟），2026-10 為 509k H100e（≈0.61 GW 設施、0.47 IT）；完工 1.2 GW 預計 Q4；其餘六站 2028 Q4 | 設施電力；上線；僅新建 Stargate 站，不含 Azure／CoreWeave／AWS | Analogy（衛星＋模型；同源算一筆）| 新站 2026 貢獻小、後重 |
| G08＋G19 | 新站交付：Shackelford 首棟 2026 年底、Milam 首棟約 10 月；Jupiter（2.45 GW）目標 2028、Oracle 發不可抗力通知 | 交付≠上線 | Analogy；Verified（報導）| 後重形狀依據 |
| G15＋G16＋G17 | AMD「Q3 起 ramp、Q4 加速、2027 Q1 再加速」；Nvidia 首個 1GW 目標 2026 下半年；Cerebras OpenAI 營收「back-end loaded in 2026」 | 目標 | Interested-party：AMD、Nvidia、Cerebras | 後重形狀依據 |
| G09／G10／G11 | Oracle FY26 交付 >1.2 GW（Q1 FY27 近 1 GW）；CoreWeave active 1.5 GW（2026-06 底，年底指引 >1.85 GW）；Microsoft 單季 +1 GW | **全客戶**；OpenAI 占比未揭露 | Verified（公司申報／法說，部分二手）；OpenAI 占比：不可分離 | 背景，不入區間 |
| G12 | Friar：「In 26 we still won't have enough compute」 | 定性 | Interested-party | 方向：供不應求 |
| G13 | Brockman 證詞：2026 年算力支出 500 億 | 計畫支出 | Interested-party | 支出法交叉檢查 |
| G14 | 2027 年「low double-digit」GW（Epoch 引；FutureSearch 稱 2 位匿名來源）| 目標；原始出處未找到 | Interested-party＋匿名；11 為 Assumed 中點 | 基準情境插值 |
| G18 | Huang：計畫 40 萬顆 GPU 上線（無日期）| 計畫；≈0.8 GW（GB200 級）| Interested-party：Nvidia | 無時程，不入區間 |
| R01 | Q2 GAAP 營收 67 億（WSJ 經 Crypto Briefing）| 年化 268 億，與你的 263 億差 2%；Q1 57 億 | Verified／報導 | 營收基準 |

## 已搜尋，未找到 ／ 不存在或不可分離

**已搜尋，未找到**：OpenAI 2026 任一時點的上線 GW 或 GPU 顆數；OpenAI 2026 年底上線官方目標；Microsoft、Oracle、CoreWeave、AWS、Google Cloud 對 OpenAI 的專屬交付 GW；Epoch 對 OpenAI 全體 2026 年的估計（本環境 epoch.ai 的 CSV 被代理封鎖，只能讀頁面摘述）；The Information、FT、Reuters 付費牆原文；2026 Q2 之後的 API 每分鐘 token；2026 的 ChatGPT 每日訊息數與 3.6B／日出處。

**不存在／不可分離**：「10GW」是簽約量；Oracle、CoreWeave、Microsoft 的 GW 是全客戶；Codex 占內部輸出 token 99.8% 是內部使用，不是 API 總量。

## 換算要點（xlsx 公式）

- 持平門檻：Q2 年化 263 億 ÷（1.239 × 9.796）＝ **2.17 GW**（h 9.731 為 2.18）；FY 350 億為 **2.88 GW**（2.90）。倍數＝門檻 ÷ GW，所以 GW 3.0 對應 Q2 口徑 0.72、全年口徑 0.96。
- GPU 換算（TK 每 GW：Hopper 718,048、GB200 501,768；2025 年底 Hopper 0.6、GB200 0.4，Assumed）：1.9 GW ≈ 120 萬顆，與 Altman「well over 1 million」相容；Epoch 1.743M H100e ÷ 1.9 GW ＝ 91.7 萬 H100e／GW。2026 年底三情境以 Hopper 0.4 計，約 206 萬／269 萬／335 萬顆（僅示意，世代比例是假設）。
- 支出法：平均 GW ＝ 2025 平均 GW × (500 億 ÷ 2025 支出) ÷ 單價比。平價、204 億：2.77；單價 +25%：2.21；160 億：3.5–3.9。注意支出倍數與你的 h 共線，只是對照，不是獨立證據。

## 待 Project 判斷（附建議預設）

| 編號 | 事項 | 建議預設 | 理由 |
|---|---|---|---|
| J1 | 2026 平均 GW 的 Assumed 2.5／3.0／3.5 是否調整 | 維持，說明欄改註「Derived 區間 2.5–3.8，無直接來源；基準 2.8–3.2」 | 區間涵蓋現值；沒有證據要求調動 |
| J2 | Q2 口徑比值用哪個 GW | Q2 末 GW 2.3–3.2（基準 2.6），並列 Q2 季平均 | Q2 營收是區間流量，配季平均更一致；兩者結論同向 |
| J3 | 趨勢判斷要不要先掛「偏降，全年口徑不可判定」 | 是 | Q2 口徑六情境全降；全年口徑跨過持平門檻 |
| J4 | 營收基準：Q2 實際 67 億（年化 268 億）與 FY 350 億是否更新 | 只記錄，不改 | Q2 差 2%；run-rate 已報 8 月 >400 億、9 月底約 500 億（二手，口徑不同），FY 350 億是否偏低由 chat 端判斷 |
| J5 | SRC_DEM_011 標註 | 維持 150 億／分，註記「OpenAI 2026-04 揭露，Q1 末時點，Q2 後未更新」 | 無新數字 |
| J6 | 每日訊息數 3.6B | 標「出處待補」，不改值 | 最新可核實為 2025-07 的 2.5B |
| J7 | 是否派能讀 epoch.ai CSV／付費牆原文的環境，取 OpenAI 相關站點的 MW 與日期 | 是（低成本，最可能產出直接證據）| 本環境被封鎖 |

## 本段限制
- 網頁多由工具摘述，逐字引用限於引號內；Oracle、Microsoft 為二手轉述，CoreWeave 為 SEC 新聞稿原文。
- 2026 年底三情境與季別形狀是情境假設，不是來源值；結論的區間寬度主要來自這兩個假設。
- 未使用 SemiAnalysis／InferenceX。

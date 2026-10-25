# 決定變數證據 B 段：Fairwater 占比、token 帳需求面（唯讀查證）

分支 `claude/evidence-decisive-vars`　基準 master `693792f`（CURRENT v21.4）　工作單 `docs/workorders/20261025_決定變數證據_B段.md`
檔案：`決定變數_B段.xlsx`（審閱檔；換算全用公式，LibreOffice 重算錯誤 0）、`證據原稿.md`。未改 `model/`、`builder/`、`tests/`。
承接：J7（PR #162）、token 帳缺口 A 段（PR #164）、OpenAI 2026 GW A 段。只用 2026-10-25 前已公開資料；Microsoft FY27 Q1 法說（10-28）留給 C 段。
模式：LIGHT（資料判讀）。已經未參與代理獨立核對（2026-10-25）：來源存在、數字重現；修正 5 處（r1，見文末）。

## 結論先行

1. **Q1 Fairwater 占比：沒有任何一手來源給出比例（不可分離），但定性證據偏向 f ≥ 0.4。**
   - 本段判斷區間 **f＝0.4–0.9，中心約 0.65**（Assumed，證據等級 Low–Medium）。f ≥ 0.4 的粗略機率約 70%（Assumed）。
   - 支持「高」的證據：OpenAI 自己寫明在 Fairwater 上訓練（F06）；Nadella 說 Wisconsin 提前上線使 Microsoft 得以「提前認列營收」，代表有付費的外部客戶承接，而 MAI 是內部單位（F05，推論；只能說明有外部付費客戶，不能分辨是 OpenAI 還是 Anthropic 等）；SemiAnalysis 稱 Wisconsin 完全供 OpenAI（F08，依規不單獨使用，只與 F05、F06 並用）。MAI 已揭露的最大預訓練只用 1.6 萬顆 GB200，約為兩站 GPU 的 3%、Wisconsin 的 9%，而且在 8–9 月（F10）。
   - 支持「低」的證據：Microsoft 官方只說供 OpenAI、MAI、Copilot 與其他工作負載（F01，無比例，不得換算）；Hood 說新 GPU 先給第一方，再給 R&D 與產品創新，其餘才給 Azure（F04）；Nadella 說不想只當單一公司的託管商（F03）；Anthropic 的 Azure 合約含至多 1 GW（Microsoft 稿：在 300 億美元 Azure 之外「另簽」至多 1 GW；NVIDIA 段落：「初期」至多 1 GW、用 Grace Blackwell／Vera Rubin；兩種說法應指同一個 1 GW，報導未明確對應，不可加總為 2 GW），站點未揭露（可能分走部分容量）。
2. **換算（沿用 J7 算法，其他站低占比、Epoch 日期）：**
   - f＝0.4／0.65／0.9 → Q2 季平均 GW **2.17／2.26／2.35**，Q2 倍數 **0.999／0.959／0.921**；用早日期為 0.925／0.881／0.841。
   - 持平所需 f 仍為 **0.395**（營收 268 億時 0.507）。其他站改中占比時降到 0.278。
   - **讀法：** Q2 口徑由「條件式下降」改為「**偏下降（中心 0.96），但下緣貼在持平線上**」。f 在 0.4 附近時倍數約 1.00，營收用 268 億則需 f > 0.51 才下降。
3. **Q2 token 帳需求面：2026 年沒有新的 API 每分鐘 token 數字。** 最新仍是 OpenAI 2026-03-31／04-08 的「逾 150 億／分」（時點值）。DevDay 2026（09-29）只公布速度與週活 12 億，沒有 token 量。
   - **D1（API 季平均 ÷ 3 月底）：** 已搜尋，未找到。token 帳維持 A 段的 1.87（基準）。
   - **D2（Codex 在 API 外）：** 沒有絕對量，但 OpenAI 研究論文給出截至 2026-06-11 前 28 天窗口的份額：Codex 占（Codex＋ChatGPT）輸出 token，組織用戶 63.3%、個人用戶 16.5%（T03）。依 TK 的 ChatGPT token 量與 Assumed 的組織權重推算，**Q2 平均約 5.1 T／日（3.5–6.6；輸入／輸出比加倍時 10.1）**，低於 A 段基準 8。前提：以 TK 每則 4,000 token 為底；每則改 6,000 時同比放大為約 7.6。token 帳 **1.77（1.69–1.86；k＝2 為 1.53）**，A 段基準 8 T／日為 1.62。
   - **Codex 是否已含在 API 的 150 億／分：** 透過 ChatGPT 登入的 Codex 走 ChatGPT 方案額度，以 API 單價折算 credit，但不是 api.openai.com 的流量；用 API key 的 Codex 按 API 計費出自 WorkOS 第三方部落格，OpenAI 說明頁未直接寫明（推論）。所以**用 ChatGPT 登入的 Codex 不在 API 數字內（推論，標 Derived）**，用 API key 的部分在。OpenAI 沒有公布兩者比例，屬於不可分離。
   - **D3（每則 token）：** 已搜尋，未找到。維持 A 段 1.90。
   - **ChatGPT 每日訊息數：** 2026 年沒有新值，最新仍是 2025-07 的 25 億＋（另有 2025-08 的 30 億，全產品）。週活：2026-02 逾 9 億 → 07 底近 10 億 → 09-08 逾 10 億 → 09-29 12 億。改用 Q2 平均週活 0.95B 時，每日則數 3.39B，token 帳 **2.12**（缺口小幅變大）。
4. **組合（r1 更正）：** 組合中 D3 取 6,000，D2 必須依同一每則 token 重推，得約 7.6 T／日（接近 A 段基準 8）。A 段基準組合 1.01，換入一致的 D2 後為 **1.02**，再加週活 0.95 為 **1.04**；k＝2 時 0.87。**結論：單一因子層面 Codex 推算值低於 A 段假設（每則 4,000 時 5.1 對 8）；組合層面幾乎不變。單一因子解釋不了缺口。**

## Facts & Data

### Q1 證據（完整見 xlsx「證據表」）

| 編號 | 來源（日期） | 內容（改寫） | 標記與誘因 | 方向 |
|---|---|---|---|---|
| F01 | Microsoft Source（2025-11-12） | 網路供 OpenAI、MAI 超級智慧團隊、Copilot 及其他工作負載 | Interested-party：Microsoft（強調多客戶） | 定性；不得換算比例 |
| F03 | Nadella，Dwarkesh 訪談（2025-11） | 「didn't want to just be a hoster」；Fairwater 2 不只跑單一工作負載 | Interested-party：Microsoft（淡化對 OpenAI 依賴） | 偏低 |
| F04 | Hood，FY26 Q2 法說（2026-01-28；roic.ai 轉載，二手） | 新 GPU 先給 Copilot 等第一方，再給 R&D 與產品創新，其餘給 Azure；問到 Fairwater 時答不聚焦特定地點 | Interested-party：Microsoft CFO | 偏低（第一方優先） |
| F05 | Nadella，FY26 Q3 法說（2026-04-29） | Wisconsin 提前約六週上線，得以「recognize revenue earlier」；沒說是誰的營收 | Interested-party：Microsoft（展示執行力） | 偏高（推論：只能說明有外部付費客戶，不能分辨是 OpenAI 還是 Anthropic 等） |
| F06 | OpenAI〈MRC supercomputer networking〉（2026-05-05） | MRC 部署在 OpenAI 最大的 GB200 超級電腦，包括 Microsoft Fairwater | Interested-party：OpenAI（展示算力） | f > 0 的直接證據；沒有份額 |
| F07 | Epoch 目錄頁（2026-07-17／07-25） | OpenAI、Microsoft 皆為 likely 使用者；可能提供 OpenAI 訓練算力 | Analogy：Epoch | 定性 |
| F08 | SemiAnalysis（2025-11-12） | 稱 Wisconsin「fully dedicated to OpenAI」 | Analogy：第三方產業研究；依規不單獨使用 | 偏高；與 F05、F06 並用 |
| F10 | Microsoft AI 部落格（2026-10-15） | MAI-Base-2 用 16k GB200、38 天、8–9 月；未載站點 | Interested-party：Microsoft AI（展示自研能力） | 量級：約兩站 GPU 的 3% |
| F11 | Microsoft FY26 Q4 法說（2026-07-29） | 當季新增 1 GW；Maia 200 同時跑 OpenAI 與 MAI 模型；未提 Fairwater | Interested-party：Microsoft | 未找到分配 |
| F12 | Microsoft 新聞稿（2026-06-23） | Mount Pleasant 第一棟全面運轉；未載使用者 | Interested-party：Microsoft | 上線時點 |

### Q1 換算（xlsx「Fairwater」頁）

| f | Q2 GW（晚） | Q2 倍數（晚） | 倍數（268 億） | Q2 GW（早） | 倍數（早） | 倍數（晚，其他站中占比） |
|---|---|---|---|---|---|---|
| 0 | 2.022 | 1.072 | 1.092 | 2.157 | 1.005 | 1.049 |
| 0.4 | 2.169 | 0.999 | 1.018 | 2.344 | 0.925 | 0.980 |
| 0.65 | 2.261 | 0.959 | 0.977 | 2.461 | 0.881 | 0.941 |
| 0.9 | 2.352 | 0.921 | 0.939 | 2.577 | 0.841 | 0.905 |
| 1 | 2.389 | 0.907 | 0.924 | 2.624 | 0.826 | 0.891 |

持平所需 f：晚 0.395；268 億 0.507；早 0.022；其他站中占比 0.278。f＝0 列與 J7 結果頁 B41:H41 完全相同（xlsx B7、B8 對照）。

### Q2 證據與換算（xlsx「token帳」頁）

| 項目 | 最新可查值 | 標記 | token 帳（起點 2.10，只動此項） |
|---|---|---|---|
| D1 API 每分鐘 token | 逾 150 億（2026-03-31、04-08，同一數字）；之後未更新 | Interested-party：OpenAI（募資、成長宣傳；「逾」為時點） | 無新值；沿用 A 段 1.87 |
| D2 Codex 在 API 外 | 份額：組織 63.3%、個人 16.5%（截至 06-11 前 28 天窗口，arXiv 2606.26959）；推算 Q2 平均 5.1 T／日（3.5–6.6；前提每則 4,000） | 份額 Interested-party（OpenAI 研究團隊）；推算 Derived；w、時點比 0.7、k 為 Assumed | **1.77**（1.69–1.86）；k＝2 為 1.53 |
| D3 每則 token | 未找到 | — | 沿用 A 段 1.90 |
| ChatGPT 每日則數 | 未找到 2026 值；週活 Q2 平均約 0.95B | 週活：Interested-party（OpenAI）；7 月值為 The Information 二手 | **2.12**（3.39B 則／日） |
| 組合（A 段基準組合，換入依每則 6,000 重推的 D2 約 7.6 T／日與週活） | — | Assumed 組合 | 1.01 → **1.02**（加週活 **1.04**；k＝2 為 0.87）；r0 不一致的 1.09 留作對照 |

D2 推算式：Codex token／日＝ChatGPT 全部 token（TK：3.6B 則 × 4,000＝14.4 T）×［(1−w)×16.5/83.5＋w×63.3/36.7］× k × Q2 平均÷截至 06-11 的 28 天窗口（0.7）。組合中每則改 6,000 時，14.4 T 改為 21.6 T。w＝組織用戶占 ChatGPT token 的比例，低／基準／高 0.1／0.2／0.3。

## Judgment（LIGHT）

- **Stance：**
  - Q1：OpenAI 用了 Fairwater 的多數容量，機率偏高，但沒有比例。Q2 口徑偏下降，中心倍數 0.96，區間 0.92–1.00（晚日期）；最保守端貼著持平線。
  - Q2：需求面的新證據沒有縮小缺口。Codex 份額推算值低於 A 段基準，週活略低於 TK 假設，兩者都讓 token 帳略升。
- **Confidence：** Q1 Low–Medium（三個偏高證據中，一個是推論、一個是不可單獨使用的第三方）；Q2 推算 Low（D2 依賴 TK 自己的每則 token 4,000，屬循環；w 無來源）。
- **基準情境與替代（粗略機率，Assumed）：**
  - f ≥ 0.4（Q2 比值低於或等於 2025）：約 70%。
  - f 在 0.25–0.4（約持平，1.00–1.03）：約 20%。
  - f < 0.25（Microsoft 自用為主，比值略升）：約 10%。
- **最強反向證據與處理：**
  1. **Hood 的第一方優先順序（F04）。** 這是 Microsoft 全機隊的分配，不是 Fairwater 專屬；Copilot 是推論工作負載，Fairwater 是為大型訓練設計的。只當作下修方向的定性證據，已反映在區間下緣 0.4。
  2. **Anthropic 的 Azure 合約（至多 1 GW（Microsoft 稿：在 300 億美元 Azure 之外「另簽」至多 1 GW；NVIDIA 段落：「初期」至多 1 GW、用 Grace Blackwell／Vera Rubin；兩種說法應指同一個 1 GW，報導未明確對應，不可加總為 2 GW））。** 站點未揭露；若部分落在 Fairwater，OpenAI 的份額會比「OpenAI 對 MAI」二分法低。已搜尋，未找到站點資訊。
  3. **Codex 推算的循環性。** D2 以 TK 的 ChatGPT token 量為底；若每則 token 實際高於 4,000（D3 方向），Codex 推算值會同比放大。所以 D2 與 D3 不是獨立因子，不能疊加為兩次閉合；組合已改為依同一每則 token 重推（r1）。
- **方向檢查（第 10 條）：**
  - 不利於「下降」的選擇 2 個：其他站沿用低占比；D2 的時點比取 0.7（Codex 用量月增約 70%，季平均可能更低）。
  - 有利於「下降」的選擇 1 個：F05 的「提前認列營收」被讀成外部客戶（且外部客戶也可能是 Anthropic 等），而 Copilot 營收也可能受惠於容量。
  - 中性 1 個：k 取 1 為基準、2 只作敏感度。
  - 都沒有收窄 Andy 留下的選項。
- **覆蓋檢查（第 11 條）：**
  - [P] 容量分配（訓練對推論、內部對外部）：已做，定性。
  - [A] 恆等式「比值＝營收 ÷（GW × h）」、「需求 token＝API＋Codex 外＋則數×每則」：已做。
  - [I] Microsoft 淡化依賴、OpenAI 展示算力與成長、SemiAnalysis 付費客戶導向：已標。
  - 未做：Fairwater 之外的 Azure 機隊中 OpenAI 份額（不可分離）。
- **判定性證據（Invalidation）：**
  - Microsoft 或 OpenAI 揭露 Fairwater 的分配比例；或 FY27 Q1 法說（10-28）提到 Fairwater 客戶。
  - OpenAI 公布 2026 年中以後的 API 每分鐘 token，或 Codex 的絕對 token 量。
  - ChatGPT 的 2026 每日訊息數。
- **實務意涵：** A2 的 Q2 讀法可改為「偏下降（中心 0.96，0.92–1.00；營收 268 億時下緣 1.02）」，附 f 判斷區間 0.4–0.9。token 帳仍寫「GW 路線 2.0–2.1，單一因子無法閉合」；D2 基準可由 8 改為約 5（Derived，附循環性註記）。

## 已搜尋，未找到 ／ 不存在或不可分離

**已搜尋，未找到：**
- Fairwater 任一站的 OpenAI／MAI／其他客戶分配比例（Microsoft 新聞稿與部落格、FY26 Q2–Q4 法說、Nadella、Hood、Suleyman 公開發言、OpenAI 部落格、Epoch、computeatlas、SemiAnalysis、The Information／FT 公開摘要）。
- Kevin Scott 2026 年對 Fairwater 或 OpenAI 容量的發言。
- Fairwater 第三站以後的名稱與上線時間（Wisconsin 第二棟 2028 年完工）。
- Anthropic 的 Azure 容量所在站點。
- 2026-04 之後的 API 每分鐘 token；DevDay 2026 的 token 量。
- Codex 的絕對 token 量（日、週、累計）。
- 2026 年的 ChatGPT 每日訊息數；每則 token 的官方數字。
- FY26 Q3 法說逐字稿官方檔（microsoft.com 下載失敗，改用 roic.ai 轉載）。

**不存在或不可分離：**
- 「供 OpenAI 與 MAI 超級智慧團隊使用」不含比例，依口徑規則只作定性。
- Microsoft 的「當季新增 1 GW」是全公司，不是 Fairwater。
- Codex 的「99.8%」是 OpenAI 員工內部，不是對外量。
- ChatGPT 登入的 Codex 與 API key 的 Codex 在 OpenAI 揭露中不分開。
- 週活 12 億（DevDay）是 Q2 之後的時點，不能直接當 Q2 平均。

## 待 Project 判斷（附預設）

| 編號 | 事項 | 建議預設 |
|---|---|---|
| B1 | A2 的 Q2 讀法是否由「條件式下降（f ≥ 0.4）」改為「偏下降，中心 0.96（0.92–1.00），f 判斷區間 0.4–0.9」 | 改寫交接檔與 A2 說明；不改 TK 數值；保留「營收 268 億時需 f > 0.51」註記 |
| B2 | token 帳候選 D2 的表示方式 | 改為「份額 × ChatGPT token 量」的推導式，不再給獨立絕對值：每則 4,000 時約 5（3.5–10），每則 6,000 時約 7.6；A 段組合因此由 1.01 變 1.02 |
| B3 | ChatGPT 每日則數 3.6B 是否改為 3.39B（Q2 平均週活 0.95B） | 不改；只記錄（差 6%，方向使缺口略大），等 OpenAI 公布 2026 則數 |
| B4 | 是否在 FY27 Q1 法說（10-28）後做 C 段 | 是；只看 Fairwater 客戶與 OpenAI 容量說法，以及 OpenAI 是否同期公布 token 量 |
| B5 | SemiAnalysis（F08）是否可列為證據 | 只作佐證，不單獨支撐結論（現行規則） |

## OpenAI 模型下一版要改的輸入（不在本段改）
- 2026 Q2 季平均 GW：中心由 J7 的 2.34（中占比、晚）改為 2.26（f＝0.65、其他站低占比、晚），區間 2.17–2.35；倍數 0.959（0.921–0.999）。
- token 帳候選 D2：改為由份額與每則 token 推導（若 B2 照預設），每則 6,000 時約 7.6 T／日。
- 其餘（API 150 億／分、每日則數、每則 token）不變。

## 本段限制
- 網頁多由工具摘述；引號內為原文短句，其餘為改寫。
- f 的區間是判斷，不是來源值；換算只動 Fairwater 兩站，其他站沿用 J7 低占比。
- D2 推算用截至 06-11 的 28 天窗口份額與 TK 的 ChatGPT token 量，份額是彙總比或使用者平均未明（圖說讀作彙總比）。
- 未登入付費牆；未使用 SemiAnalysis 以外的付費資料。

## r1（獨立核對後）
獨立核對：來源全部存在、數字全部重現、LibreOffice 錯誤 0。修正如下：
1. **組合與循環性（實質）：** 組合中 D2 改依 D3 同一每則 token（6,000）重推，約 7.6 T／日；組合 1.09 → 1.02，加週活 1.11 → 1.04，k＝2 為 0.87。單一因子表保留 D2＝5.07（註明前提每則 4,000）。結論改為「單一因子成立，組合層面幾乎不變」。xlsx「token帳」頁第 30–35 列同步。
2. **Hood（F04）：** 「R&D 的 AI 人才」改為「R&D 與產品創新」；標明為 roic.ai 轉載（二手）。
3. **Codex 計費：** 「API key 按 API 計費」改歸 WorkOS（第三方），標為推論。
4. **Anthropic、arXiv：** Anthropic 改為「至多 1 GW（Microsoft 稿：在 300 億美元 Azure 之外「另簽」至多 1 GW；NVIDIA 段落：「初期」至多 1 GW、用 Grace Blackwell／Vera Rubin；兩種說法應指同一個 1 GW，報導未明確對應，不可加總為 2 GW）」；arXiv 2606.26959 份額改為「截至 06-11 前 28 天窗口」（README、證據原稿、xlsx 同步）。
5. **F05：** 加註只能說明有外部付費客戶，不能分辨是 OpenAI 還是 Anthropic 等。

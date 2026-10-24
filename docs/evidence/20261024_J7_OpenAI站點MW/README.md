# J7：OpenAI 2026 各站點上線 MW 與日期（B 段，唯讀查證）

分支 `claude/evidence-j7-openai-sites`　基準 master `48b949b`（CURRENT v21.2）　工作單 `docs/workorders/20261024_J7_OpenAI站點MW.md`
檔案：`J7_站點MW.xlsx`（審閱檔；換算全用公式，LibreOffice 重算錯誤 0）、`epoch_openai_sites_timelines.csv`（Epoch 原始資料：Users 含 OpenAI 的 21 站，121 列，數值欄全收）、`證據原稿.md`。未改 `model/`、`builder/`、`tests/`。
模式：LIGHT（資料判讀）。r1：已依獨立核對修正（見文末）。

## 結論先行

1. **取得方法已解決一半。** Epoch 的原始 CSV 可以用 Andy 電腦上 Claude 桌面版的內建瀏覽器逐字讀取（雲端環境 shell 仍被擋）。付費牆原文（Bloomberg Law、The Information）在內建瀏覽器顯示未登入，**讀不到**，需要 Andy 的訂閱帳號（判斷題 J2）。
2. **Epoch 沒有 OpenAI 全體的 2026 估計。** 全體估計只到 2025-12（174.3 萬 H100e）。所以本段改用由下而上：取 Epoch 追蹤的 21 個 OpenAI 相關站點在 2025 年底之後的 IT 電力增量，加在 Friar 的 2025 年底 1.9 GW 上。Epoch 沒追蹤的增量都不加（Azure 其他機房、Oracle 其他、Google、AWS、AMD、Cerebras），加了只會讓 GW 更高、倍數更低。
3. **Q2 口徑（主）：偏下降，但取決於一個假設——OpenAI 在 Microsoft Fairwater 兩站用了多少。**
   - 6 組情境（3 種占比 × 2 種上線時點）下，Q2 季平均 GW 為 2.21–2.85，高於持平門檻 2.17，倍數 0.76–0.98。營收改用 WSJ 的 268 億時，最保守一組為 1.001。
   - Q2 的增量約 58% 來自 Fairwater Wisconsin 與 Atlanta（晚日期 628 MW 中的 367 MW）。這兩站由 Microsoft 擁有，OpenAI 與 Microsoft 都在用，分配比例沒有揭露，屬於**不可分離**。
   - 持平所需的 OpenAI 占比：用 Epoch 日期時至少 **0.40**（營收 268 億時 0.51）；用證據未排除的最早日期時只要 **0.02**。
   - 所以結論是：「若 OpenAI 用到 Fairwater 四成以上，或新站實際上線早於 Epoch 快照日，Q2 比值低於 2025。」兩個條件都不成立時，比值約持平到略升（1.03–1.07）。
4. **2025 基準檢查支持現用 1.239 或更高。** 同一批站點顯示 2025 年新增集中在 9–12 月，2025 平均 GW 估 1.06–1.11，低於 TK 內插 1.128，也低於線性 1.25。對應的 2025 比值為 1.25–1.32。A 段擔心的「基準 1.118」（線性內插）因此不太成立。基準越高，門檻越低，越偏向下降。
5. **全年與年底口徑仍不可判定。** 只算 Epoch 站點時，全年倍數 0.98–1.21、年底 1.04–1.30。但下半年的主要增量都不在 Epoch 站點內：AMD 首批 1 GW 自 Q3 起、Nvidia Vera Rubin 首批在 2026 下半年、Cerebras、AWS、Azure 其他。低占比時，全年平均只要再多約 0.49 GW 就會越過門檻 2.88；高占比且早上線時已經越過（2.95）。

## Facts & Data

### 輸入與標記

| 輸入 | 值 | 標記 |
|---|---|---|
| 2025 年底 OpenAI 上線 GW | 1.9 | Interested-party：OpenAI CFO Friar，有募資與 IPO 誘因。Epoch 估此數接近 IT 電力（係數中位 0.99，0.73–1.05） |
| 各站點 IT 電力與上線日期 | 見 csv | Analogy：Epoch 以衛星影像加公司揭露推估；上線日期多為快照日 |
| OpenAI 是否為使用者 | confident／likely／speculative | Epoch 自標：confident 8 站、likely 4 站、speculative 9 站 |
| OpenAI 占比情境（confident／likely／speculative） | 低 1／0.5／0；中 1／0.75／0.25；高 1／1／1 | Assumed |
| OpenAI 在 Fairwater 兩站的占比 f | 0–1 敏感度 | Assumed；不可分離。Microsoft 只說供 OpenAI 與 Microsoft AI 超級智慧團隊使用 |
| 早上線日期 | 5 個步階改用「證據未排除的最早日期」（xlsx「站點時間表」I 欄有依據） | Derived；屬極端界線，不是證據直接支持的日期 |
| 營收、h、2025 比值 | 263 億／350 億／500 億；9.796；1.239 | 沿用交接檔第 4 節 A2 與 PR #160 |

### 2026 年 Epoch 站點增量（IT MW；相對 2025 年底）

| 站點 | Epoch 標記 | Q2 平均增量（晚／早） | 2026 年底增量 | 上線證據 |
|---|---|---|---|---|
| Microsoft Fairwater Wisconsin | likely | 308／308 | 369 | Epoch：2026-04-16「Building 1 is operational.」（依 Nadella X 貼文）。TechNews 2026-04-19 轉引 Nadella：「Our Fairwater datacenter in Wisconsin is going live, ahead of schedule.」（X 原文本段未讀到） |
| OpenAI Stargate Abilene | confident | 90／159 | 632 | 第 3–4 棟 Epoch 估 2026-05-23。Oracle 04-22：「In Abilene, 200MW is already operational」，即 1–2 棟。第 5–8 棟 Epoch 預測 2026-11-01 |
| Microsoft Fairwater Atlanta | likely | 59／159 | 315 | 第 3–4 棟在 2026-06-14 快照判定上線；05-15 時仍在試運轉 |
| CoreWeave Denton TX | likely | 64／195 | 195 | 2026-03-02 法說：「Denton South partially running」；Q2 簡報：年中全園區上線 |
| CoreWeave Marble、Dalton、Chester | speculative | 107／107 | 148 | Core Scientific 揭露 |
| CoreWeave Helios、Muskogee、Ellendale；Stargate UAE | speculative／confident | 0／19 | 422 | 都在 2026-08 之後，只影響全年與年底 |
| 合計（100% 計入） | | 628／948 | 2,081 | |

Q2 季平均 GW（＝1.9＋按占比加權的增量），晚／早：低 2.21／2.39、中 2.34／2.59、高 2.53／2.85。

### 敏感度（xlsx「結果」頁）

| 變數 | 範圍 | Q2 倍數（以低占比、晚日期為底） | 翻轉條件 |
|---|---|---|---|
| OpenAI 在 Fairwater 的占比 f | 0／0.25／0.4／0.5／1 | 1.072／1.025／0.999／0.982／0.907 | f < 0.40（營收 268 億時 < 0.51）；用早日期時 f < 0.02 |
| 營收：263 億改為 WSJ 268 億 | — | 0.982 → 1.001 | 單獨成立即到持平線 |
| Friar 1.9 GW 的縮放 k（2025、2026 同步縮放） | 0.9／1.0／1.1／1.2 | 0.968／0.983／0.995／1.006 | 1.9 GW 低估約 20% |
| 1–3 月才記錄的新增其實已含在 1.9 GW 內（扣除） | 低／中／高扣 0.03／0.06／0.13 GW | 0.997（中 0.952、高 0.903） | 方向不變，但更接近持平 |
| 2025 比值 | 1.118–1.397 | 1.089–0.871 | 基準低於約 1.217（站點分布估計為 1.25–1.32） |

## Judgment（LIGHT）

- **Stance：** Q2 口徑偏下降。A 段的結論是「方向不可判定，中心略偏下」；本段把 Q2 口徑推進到「條件式下降」，條件是 OpenAI 在 Fairwater 的占比 ≥ 0.4，或新站實際上線早於 Epoch 快照日。全年與年底口徑維持不可判定。
- **Confidence：** Low–Medium。決定方向的變數（Fairwater 占比）沒有直接證據，屬 Assumed。
- **基準情境與替代（粗略機率，Assumed）：**
  - Q2 比值低於 2025：約 65%。理由是 OpenAI 為 Fairwater 首列使用者，且 Epoch 快照日通常晚於實際上線。
  - 約持平（0.98–1.03）：約 25%。
  - 高於 2025：約 10%。需要 Fairwater 主要給 Microsoft 自用、上線偏晚，且 Epoch 外沒有增量同時成立。
- **最強反向證據與處理：**
  1. **Fairwater 占比（決定性）。** Microsoft 只寫「供 OpenAI 與 Microsoft AI 超級智慧團隊」，沒有比例。已寫成條件式結論，並列出持平所需的占比。
  2. **翻轉條件不只一組，下列任一組成立就到持平或略升：**
     - Fairwater 占比 < 0.4；
     - 營收用 268 億，且占比取低、日期取晚；
     - 1.9 GW 低估約 20%，且占比取低、日期取晚。
  3. **汰除：** 若 2026 上半年有舊容量退租，GW 會低於本表。已搜尋，未找到 OpenAI 的退租揭露。
- **方向檢查（第 10 條；r1 更正）：**
  - 偏向不利於「下降」的選擇有 3 個：GW 只加 Epoch 站；用 Epoch 快照日當上線日；likely 低占比只算一半。
  - 偏向有利於「下降」的選擇有 2 個：
    - 上線即全額計入，沒有計 GPU 安裝與爬坡期，GW 偏高；
    - 1–3 月才記錄的新增可能已含在 1.9 GW 內，有重複計算的可能（已做扣除敏感度，方向不變）。
  - 中性的選擇有 1 個：用 IT 電力、不換成設施電力（1.9 GW 本身接近 IT 電力）。
  - 都沒有收窄 Andy 留下的選項。
- **覆蓋檢查（第 11 條）：**
  - [P] 電力與上線時點：已做。
  - [A] 恆等式「比值＝營收 ÷（GW × h）」：已做。
  - [I] Epoch、OpenAI、Oracle、Microsoft 的揭露誘因：已標，未量化。
  - 未做：Epoch 外的 Azure 既有機隊變動。屬不可分離，Microsoft 只揭露全公司「單季 +1 GW」。
- **判定性證據（Invalidation）：**
  - OpenAI 或 Epoch 公布 2026 年中的全體上線 GW：低於 2.17 GW 則推翻「下降」（以 2025 比值 1.239 計）；高於 2.40 GW 則連 2025 比值取最低的 1.118 時也是下降。
  - 或 Microsoft、OpenAI 揭露 Fairwater 的分配比例。
- **實務意涵：** A2 序列的 Q2 讀法可寫為「條件式下降」，並附 Fairwater 占比門檻。依 Tokenomics 優先與分層原則（交接 1.6），公司層級的 GW 序列放在 company-models 的 OpenAI 模型。監控重點：Epoch 每月更新、Microsoft FY27 Q1 法說（10 月底）。

## 待 Project 判斷（附預設）

**已定：Andy 2026-10-24 15:32「全部其他的都用预设的建议去做」→ J1–J5 照預設。** J1 已改寫交接檔第 4 節 A2；J2 不登入；J3 只追 Fairwater 分配比例；J4 不改 1.128；J5 交 OpenAI 串取用。合併仍等 Andy 指示。

| 編號 | 事項 | 建議預設 |
|---|---|---|
| J1 | A2 趨勢結論是否改寫為「Q2：條件式下降（OpenAI 的 Fairwater 占比 ≥ 0.4 時倍數 0.76–0.98；否則約持平到 1.07）；全年、年底：不可判定」 | 改寫；只改交接檔與 A2 說明，不改 TK 數值 |
| J2 | 是否由 Andy 在 Claude 桌面版的內建瀏覽器登入 Bloomberg 或 The Information 一次（登入後本串可讀全文） | 不登入；本結論不依賴付費牆原文（A 段 G20、G25、G26 仍待查） |
| J3 | 是否續查 Fairwater 分配比例與 Epoch 外的下半年增量 | 只追 Fairwater 占比（決定 Q2 方向）；下半年增量等 Epoch 下次更新 |
| J4 | 2025 平均 GW 是否由 1.128 改為站點分布估值 1.06–1.11 | 不改；記錄為「1.128 偏高、基準 1.239 偏保守」 |
| J5 | 本段的 2026 GW 序列放在哪裡 | 放 company-models 的 OpenAI 模型（公司層級），由 OpenAI 串下次換版時取用 |

## 本段限制
- Epoch 的上線日期多數是衛星快照日或 Epoch 推估，不是公司公告日；本段以「晚／早」兩種日期框住。「早」是證據未排除的最早日期，屬極端界線。
- 年底口徑的營收是 9 月底 run-rate（500 億），與 12-31 的 GW 時點不一致。年底 run-rate 若更高，倍數會更高（更偏上升）。
- 未使用 SemiAnalysis／InferenceX。

## r1（獨立核對後）
獨立核對：原始資料逐格 784 格不符 0；21 站與標記不符 0；xlsx 314 格不符 0；共約 1,170 項。修正如下：
1. **C1 須修：** 新增 Fairwater 占比敏感度與持平所需占比，結論改為條件式。
2. **C2 須修：** 翻轉條件改為多條件並列。
3. **C3：** 方向檢查補上兩個有利於下降的偏誤；新增 1–3 月重複計算的扣除敏感度；IT／設施改列為中性。
4. **C4：** 年底口徑加註時點不一致。
5. **C5–C7：** Nadella 句改標 TechNews 轉引；證據原稿中 Fairwater 使用者那句拿掉引號；Denton 引文標出省略。
6. **A1：** csv 補齊 Shackelford 2027-10 到 2028-11 的 9 列（112 → 121 列），對 2025、2026 的計算沒有影響。

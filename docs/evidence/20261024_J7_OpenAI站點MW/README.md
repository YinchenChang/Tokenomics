# J7：OpenAI 2026 各站點上線 MW 與日期（B 段，唯讀查證）

分支 `claude/evidence-j7-openai-sites`　基準 master `48b949b`（CURRENT v21.2）　工作單 `docs/workorders/20261024_J7_OpenAI站點MW.md`
檔案：`J7_站點MW.xlsx`（換算全用公式，LibreOffice 重算錯誤 0）、`epoch_openai_sites_timelines.csv`（Epoch 原始資料節錄）、`證據原稿.md`。未改 `model/`、`builder/`、`tests/`。
模式：LIGHT（資料判讀）。

## 結論先行

1. **取得方法已解決一半。** Epoch 的原始 CSV 可以用 Andy 電腦上 Claude 桌面版的內建瀏覽器逐字讀取（雲端環境 shell 仍被擋）；付費牆原文（Bloomberg Law、The Information）在內建瀏覽器顯示未登入，**讀不到**，需要 Andy 的訂閱帳號登入一次（見判斷題 J2）。
2. **Epoch 沒有 OpenAI 全體的 2026 估計**（全體估計只到 2025-12：174.3 萬 H100e）。所以本段改用由下而上：Epoch 追蹤的 21 個 OpenAI 相關站點，取 2025 年底之後的 IT 電力增量，加在 Friar 的 2025 年底 1.9 GW 上。Epoch 沒追蹤的增量（Azure 其他機房、Oracle 其他、Google、AWS、AMD、Cerebras）一律不加——它們只會讓 GW 更高。所以本表的 GW 是**下界**，倍數是**上界**。
3. **Q2 口徑（主）：方向為下降，至多持平。** Q2 季平均 GW 在 12 組情境（3 種 OpenAI 占比 × 2 種上線時點 × 2 種營收）中為 2.21–2.85，持平門檻 2.17。倍數 0.76–0.98；只有最保守的一組（低占比、Epoch 日期、營收用 WSJ 268 億）為 1.001，剛好在持平線上。這還沒加 Epoch 未追蹤的增量。
4. **2025 基準檢查支持「下降」。** 同一批站點顯示 2025 年新增集中在 9–12 月（Abilene、Fairwater Atlanta、Goodyear），2025 平均 GW 估 1.06–1.11，低於 TK 內插 1.128，更低於線性 1.25。對應 2025 比值 1.25–1.32，不低於現用 1.239。A 段擔心的「基準 1.118」（線性內插）因此不太成立；基準越高，門檻越低，下降越明確。
5. **全年口徑與年底口徑仍不可判定。** 僅 Epoch 站點時，全年倍數 0.98–1.21、年底倍數 1.04–1.30（偏上升），但下半年主要增量（AMD 首批 1 GW 自 Q3、Nvidia Vera Rubin 首批 2026 下半年、Cerebras、AWS、Azure 其他）都不在 Epoch 站點內。全年平均在低占比時只要再多約 0.49 GW 就越過門檻 2.88；高占比＋早上線已越過（2.95）。這兩個口徑本段只能給上界。

## Facts & Data

### 輸入與標記

| 輸入 | 值 | 標記 |
|---|---|---|
| 2025 年底 OpenAI 上線 GW | 1.9 | Interested-party：OpenAI CFO Friar（募資、IPO 誘因）；Epoch 估此數接近 IT 電力（係數中位 0.99，0.73–1.05） |
| 各站點 IT 電力與上線日期 | 見 csv | Analogy：Epoch 以衛星影像＋公司揭露推估；上線日期多為快照日（偏晚） |
| OpenAI 為使用者 | confident／likely／speculative | Epoch 自標；likely 站（Fairwater Atlanta、Wisconsin、Goodyear、CoreWeave Denton）多與 Microsoft 共用或未經 OpenAI 確認 |
| OpenAI 占比情境 | 低 1／0.5／0；中 1／0.75／0.25；高 1／1／1（confident／likely／speculative） | Assumed |
| 早上線日期 | 5 個步階改用證據下限日期（見 xlsx「站點時間表」I 欄依據） | Derived |
| 營收、h、2025 比值 | 263 億／350 億／500 億；9.796；1.239 | 沿用交接檔第 4 節 A2 與 PR #160 |

### 2026 年 Epoch 站點增量（IT MW；相對 2025 年底）

| 站點 | Epoch 標記 | Q2 平均增量（晚／早） | 2026 年底增量 | 上線證據 |
|---|---|---|---|---|
| Microsoft Fairwater Wisconsin | likely | 308／308 | 369 | 2026-04-16 Nadella：「Our Fairwater datacenter in Wisconsin is going live, ahead of schedule.」 |
| OpenAI Stargate Abilene | confident | 90／159 | 632 | 3–4 棟 Epoch 估 2026-05-23（Oracle 04-22：「In Abilene, 200MW is already operational」＝1–2 棟）；5–8 棟 Epoch 預測 2026-11-01 |
| Microsoft Fairwater Atlanta | likely | 59／159 | 315 | 3–4 棟 2026-06-14 快照判定上線（05-15 仍在試運轉） |
| CoreWeave Denton TX | likely | 64／195 | 195 | 2026-03-02 法說「Denton South partially running」；Q2 deck：年中全園區上線 |
| CoreWeave Marble、Dalton、Chester | speculative | 107／107 | 148 | Core Scientific 揭露 |
| CoreWeave Helios、Muskogee、Ellendale；Stargate UAE | speculative／confident | 0／19 | 422 | 皆 2026-08 之後，影響全年與年底 |
| 合計（100% 計入） | | 628／948 | 2,081 | |

Q2 季平均 GW（＝1.9＋占比加權增量）：低 2.21／2.39、中 2.34／2.59、高 2.53／2.85（晚／早）。

## Judgment（LIGHT）

- **Stance：** 回本比值 2025→2026 在 Q2 口徑**下降**（A 段為「方向不可判定，中心略偏下」；本段把 Q2 口徑推進到「下降，至多持平」）。全年、年底口徑維持不可判定。
- **Confidence：** Medium。依據：GW 是下界、倍數是上界，結論方向對未計入的增量穩健；不穩健的地方在下列三項。
- **最強反向證據與處理：**
  1. Friar 1.9 GW 若低估（Epoch 準確度係數上端 1.2）：2025、2026 同步放大後，最保守組合 Q2 倍數 1.006，中占比 0.956。只有「1.9 低估 20%」加「低占比」加「晚上線」同時成立才翻轉。
  2. 營收口徑：用 WSJ 268 億時最保守組合 1.001。
  3. 汰除：若 2026 上半年有舊容量退租（例如 Azure 上的舊 A100／H100 叢集），GW 會低於本表。已搜尋，未找到 OpenAI 退租揭露。
- **方向一致性檢查（第 10 條）：** 本段 4 個口徑選擇——GW 只加 Epoch 站（偏低 GW，偏不利於「下降」）、IT 電力不換設施電力（同向）、Epoch 快照日當上線日（同向）、低占比 likely 只算一半（同向）——全部朝「不利於下降」方向收斂，沒有收窄 Andy 留下的選項；結論仍是下降。
- **覆蓋檢查（第 11 條）：** [P] 電力與上線時點：已做；[A] 營收 ÷（GW × h）恆等式：已做；[I] Epoch、OpenAI、Oracle、Microsoft 的揭露誘因：已標，未量化。未做：Epoch 外的 Azure 既有機隊變動（不可分離：Microsoft 只揭露全公司「單季 +1 GW」）。
- **判定性證據（Invalidation）：** OpenAI 或 Epoch 公布 2026 年中全體上線 GW 低於約 2.2 GW；或證據顯示 Fairwater 兩站主要不供 OpenAI 使用。
- **實務意涵：** A2 序列的 Q2 讀法可改寫為「2026 Q2 低於 2025」。是否寫進 TK 或 OpenAI 公司模型屬判斷題 J1；依 Tokenomics 優先與分層（交接 1.6），公司層級 GW 序列應放在 company-models 的 OpenAI 模型。

## 待 Project 判斷（附預設）

| 編號 | 事項 | 建議預設 |
|---|---|---|
| J1 | A2 趨勢結論是否改寫為「Q2 口徑：下降（倍數 0.76–0.98，最保守 1.00）；全年、年底：不可判定」 | 改寫；只改交接檔與 A2 說明，不改 TK 數值 |
| J2 | 付費牆原文：是否由 Andy 在 Claude 桌面版內建瀏覽器登入 Bloomberg 或 The Information 一次（登入後本串可讀全文） | 不登入；本結論不依賴付費牆原文（A 段 G20、G25、G26 仍待查） |
| J3 | 全年口徑要不要再查 Epoch 外的下半年增量（AMD、Nvidia、Cerebras、AWS、Azure） | 先不查；等 OpenAI 或 Epoch 的下一次揭露（Epoch 約每月更新） |
| J4 | 2025 平均 GW 是否由 1.128 改為站點時間分布估值 1.06–1.11 | 不改；只記錄為「1.128 偏高、基準 1.239 偏保守」 |
| J5 | 本段的 2026 GW 序列放哪裡 | 放 company-models OpenAI 模型（公司層級）；由 OpenAI 串下次換版時取用 |

## 本段限制
- Epoch 的上線日期多數是衛星快照日或 Epoch 推估，不是公司公告日；本段以「晚／早」兩種日期框住。
- csv 由內建瀏覽器讀取原檔後節錄數值欄（全檔 SHA-256 記於證據原稿），由未參與代理另行重讀比對。
- 未使用 SemiAnalysis／InferenceX。

# IREN Q1 FY27（2026-09-30 季）財報證據段（唯讀查證）

分支 `claude/evidence-iren-q1fy27`　基準 master `ca56af4`（CURRENT `20261105_Tokenomics_v21.12.xlsx`）　查證日 2026-11-06（台北）
範圍：IREN 2026-11-05（美東）發布的 Q1 FY27 新聞稿（8-K 附件）、10-Q、法說（17:00 ET）。只登錄證據，**未改 `model/`、`builder/`、`tests/`、任何 Excel**。
TK 數值取自 v21.12（`openpyxl data_only=True`）：`IF_HoldEcon`／`AL_HoldGen` 經濟持有成本（$B／IT GW·年）基準 Hopper 9.70、GB200 8.83、GB300 10.89、VR200 12.23；GB300 低／高 8.43／16.69，VR200 低／高 9.22／17.75。
非財務項目（Childress Horizon 時程、MW 管線）屬 Wattonomics，見第 5 節交叉引用，本檔不重複。
狀態：已經未參與代理獨立核對（有條件通過，已修正；見第 6 節）。候選編號暫用 `IR-01`～`IR-14`，正式 E 編號（v21.12 最後為 E560）由建置工作單分配。

## 結論先行

1. **本季財報沒有任何數字達到改 TK 基準值的門檻。** 14 筆候選：只並列 8、不改值（確認、無資料或口徑不同）6、建議改值 0。
2. **計價倍數（`AL_SpendBasis` 1.8）：IREN 本季新約價全部落在既有「新約群 1.36–2.30」內，機隊層落在「機隊群 0.65–1.32」內。**
   - 本季 3 年約每 MW (IT) 年營收 1,900–2,300 萬美元 → ÷ GB300 1.75–2.11（÷ VR200 1.55–1.88）。
   - 本季 5 年約約 1,700 萬 → 1.56（VR200 1.39）；季後 5 年約約 2,200 萬 → 2.02（VR200 1.80）。
   - 季後短約 >4,000 萬 → 3.67（VR200 3.27），與 Nebius 短約 3.7–4.6 同一群，屬短約現貨上緣。
   - 機隊層：9 月底 operating ARR 約 10 億美元 ÷ 0.1 GW 運轉容量 → 每 GW 約 100 億 → ÷ GB300 0.92、÷ Hopper 1.03。
   - Microsoft 長約仍是 0.89（2025 年簽，GB300）。
   - **新進展：** CEO 本季原話寫明「annualized revenue per megawatt of IT load」，上一段（20261025 第二出租方錨點）IREN 單價的「年額讀法」由 Derived 升為公司自述。
3. **折舊年限：** 公司稱資料中心資產 20 年（新聞稿原文），與 TK 廠房加權年限約 20 年一致。GPU 年限本季三份文件都沒寫；二手彙整頁引 FY26 10-K 為 5 年（原文未開到），與 TK 高成本 5 年相同、低於基準 6 年 → 不改值。
4. **利用率、服務占比、免費占比、生產折減：IREN 都沒有揭露，也不可能揭露（出租方按容量收費，看不到租戶怎麼用）。** 四個輸入都「不改值」。
5. **資本支出：** Microsoft 案（2025-11）GPU 每 MW 2,900 萬；「all-in」資料中心 1,400–1,600 萬，但簡報第 5 頁拆成資料中心基礎設施 900–1,100 萬＋超級叢集架構／彈性機架密度 300 萬＋加速 200 萬，**只有 900–1,100 萬與 TK 廠房同口徑，為 TK 12.67 的 0.71–0.87 倍（落在 TK 低端到基準之間）**。本季 CFO「示意例」每 MW 約 6,000 萬（三分之一資料中心、三分之二 GPU），資料中心約 2,000 萬很可能也含同類非廠房項目，不能直接比；只並列。
6. **Microsoft 合約金額沒有在本季文件重述**，但 10-Q 租賃收入可以對帳：Horizon 1（50 MW）8-13 交付到季底 48 天 × 年 4.85 億＝6,380 萬，對 10-Q 租賃收入 6,500 萬，相符 → US$9.7B／5 年仍是有效數字（Derived）。

## 1. 事實與數據（Facts & Data）

標記：[Verified] 監理文件數字；[Interested-party] 公司新聞稿或法說自述；[Analogy] 第三方或媒體；[Assumed] 本檔假設；[Derived] 本檔換算。
「公司說」＝公司文件或管理層原話；「轉述」＝媒體或彙整站的說法或推論。英文引文皆不超過 15 字。

### 1.1 AI 雲營收、ARR、GPU、MW

| # | 項目 | 數值 | 標記 | 出處（查閱 2026-11-06） | 誰說的 |
|---|---|---|---|---|---|
| F1 | AI 雲營收（季） | 2.00 億美元（上季 0.71 億）；其中服務 1.35 億、租賃 0.65 億（上季 0） | Verified（10-Q）／Interested-party（新聞稿） | 新聞稿 S1、10-Q S2 | 公司說 |
| F2 | 租賃收入組成 | 固定與實質固定 4,900 萬、依可用性條件 1,600 萬（占 24.6%） | Verified | 10-Q Note 4（S2） | 公司說 |
| F3 | 租賃未來最低收款（不含可用性部分） | FY27 剩餘 2.71 億、FY28–FY31 每年 3.62–3.63 億、FY32 1.21 億，合計 18.41 億；全部租賃合約剩餘總值約 139.57 億（含尚未交付容量） | Verified | 10-Q Note 4／Note 2（S2） | 公司說 |
| F4 | ASC 606 剩餘履約義務 | 63.47 億（12 個月內 15.29 億、13–24 個月 16.52 億、其餘 25–60 個月） | Verified | 10-Q（S2） | 公司說 |
| F5 | 營收 backlog | 203 億美元，季增 22%；約三分之二為投資等級對手 | Interested-party | 新聞稿（S1） | 公司說 |
| F6 | ARR | operating ARR 9 月底約 10 億（「operating ARR doubled to a billion」）；>40 億 ARR 目標「fully contracted and fully funded」，上線時點由 2026 年底延到 2027-01，可能到 2 月底 | Interested-party | 新聞稿（S1）；法說（S3） | 公司說 |
| F7 | 運轉容量 | 「Operating capacity rose 127% in the quarter to 0.1 GW」；0.3 GW (IT) 計畫支撐 40 億 ARR；2027 年底目標 0.8 GW | Interested-party | 0.1 GW 與 +127% 只見於法說 CEO（S3、S4），新聞稿沒有；0.3 GW、0.8 GW 見新聞稿（S1） | 公司說（0.1 GW 未寫 IT 或設施，本檔以 IT 計：Assumed） |
| F8 | GPU 世代 | Horizon 1 為 GB300 NVL72（NVIDIA Exemplar Cloud）；Prince George 為 H100；CEO：「pricing backdrop for contracting our Vera Rubin capacity」 | Interested-party | 新聞稿（S1）；法說（S3） | 公司說 |
| F9 | GPU 數量（依世代） | **未揭露**（新聞稿、10-Q 擷取段、法說皆無） | — | S1–S4 | — |
| F10 | 帳面 GPU 硬體原值 | 58.19 億（2026-09-30），上季 20.35 億 | Verified | 10-Q Note 11（S2） | 公司說 |

### 1.2 利用率

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F11 | GPU 利用率 | **未揭露** | — | S1–S4 | — |
| F12 | 用電相對銘牌 | 「GPUs are actually operating under 100% of their nameplate power draw」；以 NVIDIA 軟體超額配置電力，近銘牌時降頻 | Interested-party | 法說 Q&A 約 45:54（S4，自動逐字稿、講者未標，推定 Kent Draper） | 公司說（講者為推定） |

### 1.3 價格

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F13 | 本季 3 年約 | 每 MW IT 負載 1,900–2,300 萬美元（「three year pricing was at 19 to 23 million per megawatt of IT load」） | Interested-party（單一來源：自動逐字稿；以官方 replay 為準） | 法說 CFO 約 15:34（S4） | 公司說。張力：FY26 新聞稿（2026-08，S6）已寫「Recent 3-year contracts >$20m revenue per MW (IT)」，本季又稱 3 年約價 +11%，但逐字稿下緣只有 19，可能誤聽或不同加權 |
| F14 | 本季 5 年約 | 約 1,700 萬／MW | Interested-party（單一來源：自動逐字稿） | 法說 CFO（S4 原句「five year pricing at approximately 17」，未說單位；依前句 3 年約讀作每 MW IT 負載百萬美元：Assumed） | 公司說 |
| F15 | 季後 5 年約 | 約 2,200 萬／IT-MW，客戶預付約 90% 對應 GPU 資本支出；CEO：「$22 million of annualized revenue per megawatt of IT load」 | Interested-party | 價格與預付：新聞稿（S1）；「annualized」只見於法說 CEO 約 5:09（S3、S4），新聞稿沒有這個字 | 公司說 |
| F16 | 季後短約 | 「$40 million per IT-MW of revenue」（新聞稿）；CEO「in excess of $40 million」 | Interested-party | S1；S3 | 公司說 |
| F17 | 價格漲幅 | 「+11% on 3-year deals and +12% on 5-year deals」；新聞稿註 6：Q1 FY27 簽約的 3 年與 5 年約對比 Q4 FY26，依公司內部用電假設換算每 IT-MW，並以 ARR 加權 | Interested-party | 新聞稿（S1）註 6 | 公司說。**注意：IREN 各每 MW 單價（F13–F16）是用公司內部用電假設換算，不是合約約定的 MW** |
| F18 | H100 重簽 | 「Contracted H100 GPUs at double previous pricing」，相對 Prince George 前一張 H100 合約；多年期；無絕對價格 | Interested-party | 新聞稿註腳（S1）；法說（S4） | 公司說 |
| F19 | 小時價 | 未揭露 $/GPU·時；Q&A：「any price increases flow through immediately to hourly pricing」 | Interested-party | 法說約 1:00:30（S4，講者未標） | 公司說 |
| F20 | Microsoft 合約 | US$9.7B、5 年平均期、200 MW (IT)、GB300、20% 預付（credited to years 3–5）、年 ARR 19.4 億；本季文件未重述金額 | Interested-party | 2025-11-03 簡報（S5） | 公司說 |
| F21 | Microsoft 設計變更 | CEO：Microsoft 要求重新配置、升級網路，使 200 MW 能服務最新前緣模型；「small delay. We're targeting January」；增量資本支出「entirely immaterial」 | Interested-party | 法說約 24:42–27:50（S4） | 公司說（S4 講者部分為推定） |
| F22 | 預付 | 新聞稿：「Prepayment terms vary by contract」；10-Q：預付含重大融資成分 5,000 萬，計入 RPO；AI 雲服務遞延收入 4.48 億（上季 2.19 億） | Verified（10-Q）／Interested-party | S1、S2 | 公司說 |

### 1.4 折舊年限

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F23 | 資料中心資產 | 「$6 billion of data center assets with 20-year useful lives」 | Interested-party（新聞稿；10-Q 擷取段未見政策表） | 新聞稿（S1）；CEO「20-year assets that can carry several generations of compute」（S4） | 公司說 |
| F24 | GPU 年限 | 本季新聞稿、10-Q 擷取段、法說皆未寫；二手彙整頁「5 years」、「HPC hardware (GPUs)」，引 FY26 10-K | Analogy（二手；10-K 原文未讀到，擷取工具在 Item 1 截斷） | S7 | 轉述 |
| F25 | 本季年限變更 | 擷取到的 10-Q 段落無估計變更揭露（只有礦機減損 200 萬）；但 PP&E 政策註腳未讀到 → 不能斷言「沒有變更」 | Verified（部分） | 10-Q（S2） | 公司說 |
| F26 | 折舊費用 | PP&E 折舊 1.43 億、D&A 合計 1.48 億（上季 1.12 億） | Verified | 10-Q（S2） | 公司說 |

### 1.5 資本支出

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F27 | Microsoft 案 | GPU 資本支出 58 億（含周邊）÷ 200 MW＝2,900 萬／MW；資料中心「all-in capex $14-16m per MW (IT load)」，簡報第 5 頁拆分：資料中心基礎設施 9–11＋超級叢集架構／彈性機架密度 3＋加速 2 | Interested-party／Derived（每 MW GPU） | S5 第 5 頁；E266 已登錄 GPU 部分 | 公司說 |
| F28 | 本季示意例 | 1 MW 約 6,000 萬資本支出，三分之一資料中心、三分之二 GPU；50% GPU 預付、5 年約 → GPU 回本約 18 個月，含資料中心約 3 年；**公司稱為示意** | Interested-party | 法說 CFO 約 16:27–17:13（S4） | 公司說 |
| F29 | FY27 剩餘資本支出 | 約 150 億；季資本支出約 50 億（現金流：PP&E 21.31 億＋電腦硬體 26.93 億） | Verified（現金流）／Interested-party | S1、S2、S4 | 公司說 |

### 1.6 融資

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F30 | GPU 融資 | 「six and a half billion of GPU financing since May at six to nine and a half percent」 | Interested-party | 法說 CEO 約 6:19（S3、S4） | 公司說 |
| F31 | 個別融資（FY26 已揭露） | Microsoft 案投資等級 GPU 融資 36 億、6.0%，連同預付涵蓋 96% GPU 資本支出；PIMCO／Blue Owl 24 億、9.0% 固定，涵蓋 90% | Interested-party | FY26 新聞稿（S6） | 公司說 |
| F32 | 融資比率 | 投資等級與非投資等級 GPU 融資分別約 95% 與 >100%（含預付）；目標 90% | Interested-party | 法說 CFO 約 20:33（S4） | 公司說 |
| F33 | 資產負債 | 本季融資額度提領 23.60 億；負債 98.97 億（流動 9.50、非流動 89.47）；含融資租賃 102.08 億；財務費用 7,300 萬；資本承諾 189.47 億（以上 Verified，10-Q）；淨負債 44.30 億＝102.08 − 現金 35.22 − 受限現金 22.56（新聞稿，非 GAAP） | Verified（10-Q 各項）／Interested-party（淨負債） | 10-Q（S2）；新聞稿（S1） | 公司說 |
| F34 | 期限、擔保、LTV | **未揭露於讀到的段落**（借款附註在擷取截斷之後） | — | S2 | — |

### 1.7 營運費用與毛利

| # | 項目 | 數值 | 標記 | 出處 | 誰說的 |
|---|---|---|---|---|---|
| F35 | AI 雲毛利（不含 D&A） | 86%，與上季持平；營收成本 2,800 萬（服務 1,700 萬、租賃 1,100 萬） | Verified（10-Q）／Interested-party | S1、S2 | 公司說 |
| F36 | AI 雲電費 | 700 萬（服務 300 萬、租賃 400 萬） | Verified | 10-Q Note 5（S2） | 公司說 |
| F37 | 全公司 | Adjusted EBITDA 6,600 萬（29%）；現金營運費用 1.18 億；下季現金營運費用約增 5,000–6,000 萬 | Interested-party | S1、S4 | 公司說 |
| F38 | 客戶集中 | 三家客戶占營收 28%、24%、18%，全在 AI 雲 | Verified | 10-Q（S2） | 公司說 |

## 2. 對應 Tokenomics 的換算（Derived）

| 換算 | 算式 | 結果 | 對照 TK |
|---|---|---|---|
| D1 本季 3 年約倍數 | 19–23 ÷ GB300 10.89 | 1.75–2.11（÷ VR200 1.55–1.88；÷ GB300 高成本 1.14–1.38） | `AL_SpendBasis` 1.8（0.85–2.3） |
| D2 本季 5 年約倍數 | 17 ÷ 10.89 | 1.56（÷ VR200 1.39） | 同上 |
| D3 季後 5 年約倍數 | 22 ÷ 10.89 | 2.02（÷ VR200 1.80） | 同上 |
| D4 季後短約倍數 | 40 ÷ 10.89 | 3.67（÷ VR200 3.27） | 區間外；與 SpaceX（E482，4.6–5.2）、Nebius 短約（3.7–4.6）同群 |
| D5 機隊層倍數（年底口徑） | operating ARR 10 億 ÷ 0.1 GW＝10.0 $B/GW·年 | ÷ Hopper 1.03、GB300 0.92 | 既有機隊群 0.65–1.32 |
| D6 機隊層倍數（季營收口徑） | 季營收 2.00 億 × 4 ÷ 平均容量 0.072 GW（期初 0.1 ÷ 2.27＝0.044，線性平均）＝11.1 | ÷ Hopper 1.14、GB300 1.02 | 同上；線性平均是 Assumed（Horizon 1 只計 48 天，偏高估容量 → 倍數偏低） |
| D7 Microsoft 對帳 | 19.4 億 ÷ 200 MW × 50 MW × 48／365 | 6,380 萬 vs 10-Q 租賃收入 6,500 萬 | 確認 9.70 $M/MW·年仍有效（0.89 倍） |
| D8 租賃固定占比 | 3.62 億 ÷ (4,900 ÷ 6,500) | 年 4.80 億 ≈ Microsoft 50 MW 年 4.85 億 | 可用性條件約占四分之一（服務水準扣款風險） |
| D9 AI 雲營收成本每 GW | 2,800 萬 × 4 ÷ 0.072–0.1 GW | 1.12–1.55 $B/GW·年 | TK GB300 營運費用 `IF_OpexGW` 1.98（1.21–3.19） |
| D10 電費每 GW | 700 萬 × 4 ÷ 0.072–0.1 GW | 0.28–0.39 $B/GW·年 | TK 電價 0.08 $/kWh、PUE 1.2：1 GW 滿載約 0.84；IREN 為低價電＋未滿載，不可分離 |
| D11 資料中心每 MW | Microsoft all-in 14–16＝基礎設施 9–11＋叢集架構／機架密度 3＋加速 2；同口徑只取 9–11。示意例 60 × 1/3＝20 | 同口徑 9–11 ÷ 12.67＝**0.71–0.87**（all-in 1.10–1.26 不同口徑）；示意例 1.58 倍（很可能含同類非廠房項目） | TK 廠房 12.67（10.21–16.19）；Microsoft 同口徑落在低端到基準之間 |
| D12 GPU 每 MW | Microsoft 29.0（GB300）；示意例 60 × 2/3＝40 | ÷ TK GB300 IT 32.2＝0.90；40 ÷ VR200 37.6＝1.06 | TK IT：GB300 32.2（28.6–39.3）、VR200 37.6（32.0–42.6） |
| D13 回本期反推 | 示意例：GPU 淨投入 40 × 50%＝20；年現金 ≈ 17–22 × 86%＝14.6–18.9 → 1.06–1.37 年；含資料中心 40 ÷ 14.6–18.9＝2.1–2.7 年 | 公司說約 18 個月、約 3 年 | 量級相符；公司示意例未給單價，以 F13–F15 代入（Assumed） |
| D14 資料中心年限 | TK 建物 30、電力 20、機械 15、光纖 10（基準資本 3.6／4.5／2.5／0.4） | **折舊等值年限**（調和：可折舊廠房 ÷ 年折舊）約 19.9 年；算術資本加權為 21.8 年；`IF_DeprFac` 反推含土地 19.97、不含土地 19.94 | IREN 20 年 |

## 3. 候選表（DB_Evidence 格式，暫編號）

| 候選 | 日期 | 主張 | 出處 | 標記 | 對應參數 | 現值 | 證據值 | 建議判定 | 理由 |
|---|---|---|---|---|---|---|---|---|---|
| IR-01 | 2026-11-05 | 本季 3 年約 1,900–2,300 萬／IT-MW·年；5 年約約 1,700 萬 | 法說 CFO（S4） | Interested-party／一手口頭 | Alloc_In C23 `AL_SpendBasis` | 1.8（0.85–2.3） | 1.56–2.11（÷GB300） | **只並列** | 出租方新約價，不是 OpenAI 新舊約混合支出，口徑不同；落在既有新約群 1.36–2.30 內 |
| IR-02 | 2026-11-05 | 季後 5 年約約 2,200 萬／IT-MW，預付約 90% GPU 資本支出；CEO 明說 annualized | 價格：新聞稿（S1）；annualized：只見於法說（S3、S4），E408 升等以法說為依據 | Interested-party／一手 | 同上；E408 | 同上 | 2.02（÷GB300）、1.80（÷VR200） | **只並列**；E408「IREN 年額讀法」由 Derived 改為公司自述（依據為法說原話，非新聞稿） | 同 IR-01；可能為 Vera Rubin 容量（Assumed），以 VR200 計恰為 1.80 |
| IR-03 | 2026-11-05 | 季後短約 >4,000 萬／IT-MW | S1、S3 | Interested-party | 同上；E482 | 同上 | 3.27–3.67 | **只並列**（短約上緣） | 與 E482、Nebius 短約同群；不是機隊平均 |
| IR-04 | 2026-11-05 | 9 月底 operating ARR 約 10 億、運轉 0.1 GW | S1、S3 | Interested-party／Derived | 同上 | 同上 | 0.92–1.14 | **只並列**（第五個機隊點） | 落在機隊群 0.65–1.32 內；0.1 GW 以 IT 計（Assumed） |
| IR-05 | 2026-11-05 | 3 年約價 +11%、5 年約價 +12%；H100 重簽為原價 2 倍 | S1 | Interested-party | Cap_In g（−0.09）；E485、E486、E490 | −0.09 | 方向：租價上升 | **只並列**（反方證據，不改） | 同 Q3 E485 群；比較基期未寫，H100 無絕對價 |
| IR-06 | 2026-11-05 | 10-Q 租賃收入 6,500 萬與 Microsoft 50 MW × 48 天換算 6,380 萬相符 | 10-Q（S2）＋S5 | Verified／Derived | 契約第 4 節 IREN 9.70；E373 | 9.70 | 9.70 | **不改值**（確認） | 合約金額本季未重述，但會計數字對得上 |
| IR-07 | 2026-11-05 | 利用率未揭露；只說 GPU 多數時間低於銘牌功率 | S1–S4 | Interested-party（質性） | `AL_UtilActual`／`IF_UtilActual` 0.41（0.30–0.65）；`IF_Util` 0.60 | 0.41 | 無 | **不改值** | 出租方按容量計費，看不到租戶利用率；「低於銘牌功率」是電力口徑，不是 GPU 時數口徑 |
| IR-08 | — | 服務占比、免費占比未揭露 | — | — | Cap_In C28 `B4_Serve` 0.41（0.30–0.60）、C29 `B4_Free` 0.46（0.35–0.60） | — | 無 | **不改值** | 不可分離（租戶內部用途） |
| IR-09 | — | 生產折減未揭露 | — | — | Serving C28 `CTL_ProdDerate` 0.85 | 0.85 | 無 | **不改值** | 無任何對應數字；可用性條件收入占 24.6%（F2）是合約扣款風險，不是產出折減 |
| IR-10 | 2026-11-05 | 資料中心資產 20 年 | 新聞稿（S1）、CEO（S4） | Interested-party／一手 | Inputs E24–E27（30／20／15／10，加權約 20） | 約 20 | 20 | **只並列**（第一個公司揭露的廠房年限錨點） | 與 TK 加權年限一致；IREN 未分建物與機電 |
| IR-11 | 2026-10-10（彙整頁） | GPU 年限 5 年（引 FY26 10-K） | S7 | Analogy（二手；原文未開到） | Inputs E23／F23（`IF_DeprLifeIT` 基準 6、高成本 5；SRC_DC_008） | 6／5 | 5 | **不改值** | 與高成本 5 相同，加強 v21.8 改 5 的依據；須讀到 10-K 原文才能升等 |
| IR-12 | 2025-11-03／2026-11-05 | 資料中心 all-in 每 MW 1,400–1,600 萬（Microsoft 案，含叢集架構／機架密度 3 與加速 2）；同口徑基礎設施 900–1,100 萬；本季示意例約 2,000 萬 | S5 第 5 頁、S4 | Interested-party（示意例公司自稱示意） | Inputs D16–F21（廠房 12.67；10.21–16.19） | 12.67 | 同口徑 9–11（0.71–0.87 倍） | **只並列** | 只有基礎設施 9–11 與 TK 廠房同口徑，落在 TK 低端到基準之間，不構成 TK 偏低的證據；示意例很可能同樣含非廠房項目，且非實績，不作反向證據 |
| IR-13 | 2025-11-03／2026-11-05 | GPU 每 MW：Microsoft GB300 2,900 萬；示意例約 4,000 萬 | S5、S4；E266 | Interested-party／Derived | Interface 第 9 列 IT 資本（GB300 32.2、VR200 37.6） | 32.2／37.6 | 29.0／40 | **只並列** | 都在 TK 區間內 |
| IR-14 | 2026-11-05 | GPU 融資 6.5B、6–9.5%；投資等級 6.0%、非投資等級 9.0%；融資＋預付涵蓋 90–>100% GPU 資本支出 | S3、S4、S6 | Interested-party | Inputs E28 WACC 10%（8–13%） | 10% | 債務成本 6–9.5% | **不改值** | 債務成本不是 WACC；預付讓租戶承擔資金成本，出租方 WACC 下降屬出租方利潤，TK 持有成本已含資金成本 |

## 4. 判斷（LIGHT）

- **立場：** IREN 本季是「新約價續漲、機隊平均仍約 1 倍」的又一個點。對 TK 的意義是把既有兩群（機隊 0.65–1.32、新約 1.36–2.30）各加一個點，不是推翻 1.8。
- **信心：** 價格點 Medium（公司口頭、一手，但正在募資與洽約）；機隊點 Medium–Low（0.1 GW 口徑未定義、季內爬坡）。
- **最強反向證據與處理：**
  1. **新約價高於 1.8 的趨勢。** 季後 5 年約以 GB300 計 2.02；若 OpenAI 2027 年新增容量都按這個價，1.8 會偏低。處理：本季 5 年約 1,700 萬（1.56）與季後 2,200 萬（2.02）並存，加上以 VR200 計為 1.80，仍在區間內，不改。
  2. **預付改變經濟分配。** 預付 90% GPU 資本支出時，出租方的資金成本移給租戶；10-Q 已把 5,000 萬融資成分計入 RPO，代表營收含融資毛額。租戶的實際經濟成本因此不低於營收，倍數讀法不需下修。
  3. **資料中心造價。** 示意例每 MW 約 2,000 萬看似高於 TK 廠房高端 16.19，但 Microsoft 案 all-in 14–16 拆開後，與 TK 同口徑的基礎設施只有 9–11（TK 的 0.71–0.87 倍），其餘是叢集架構／機架密度與加速；示意例很可能含同類項目，且公司自稱示意。處理：不作反向證據，只並列；下次廠房成本 A 段可向 IREN 拆分口徑求證。
- **方向檢查：** 不利於「1.8 偏高」的選擇 2 個（新約以 GB300 為主分母；0.1 GW 以 IT 計）。有利於「1.8 偏高」的選擇 1 個（機隊層以線性平均容量，爬坡未計費會低估）。都沒有收窄 Andy 留下的選項。
- **判定性證據（Invalidation）：** IREN 揭露 GPU 數量與利用率；IREN 全部新約平均價（不是代表性大單）；10-K／10-Q 借款附註（期限、擔保、LTV）；FY26 10-K PP&E 年限表原文。

## 5. 與 Wattonomics 的交叉引用（不重複）

company-models `wattonomics/evidence_raw/E_earnings_20261105.md`（origin/main，唯讀）已有：
- **EQ#7**（Childress Horizon 4 年底交付風險，Aterio 衛星，Analogy）。本季公司自述：Horizon 1 已交付 Microsoft；Horizon 2–4「late-stage construction」；Horizon 3「all the GPUs on site. All three halls energized」；>40 億 ARR 目標延到 2027-01（可能 2 月底），原因是 Microsoft 要求的網路設計變更與供應商時程（F6、F21）。**這是公司自揭的時程延後，交 Wattonomics 判斷是否更新 cp_neo_iren 的 M 欄；本檔不入 TK。**
- **EQ#9**（Q1 FY27「未公布」）。本檔第 1.1 節 F6、F7 可作為該列的補件來源（0.1 GW 運轉、0.3 GW 計畫、2027 年底 0.8 GW；>5 GW 已取得電力、>35 GW 開發管線、Sweetwater 2 GW、西班牙 Badajoz 300 MW、Mackenzie 100 MW 液冷）。MW 管線屬 Wattonomics，本檔不換算。

## 6. 獨立核對

- 2026-11-06 由未參與製作的代理核對 PR #199：**有條件通過 → 已依意見修正**（本次 commit）。
- 數值錯誤 0、算術錯誤 0。
- 修正項目：IR-12／D11／F27 Microsoft all-in 資料中心造價拆分（同口徑 0.71–0.87）；F17 比較基期與「每 MW 以內部用電假設換算」；F13 與 FY26「>$20m」的張力、單一來源；F14 原句；F33 淨負債改 Interested-party（非 GAAP）；F7、F12、F15、F30、F32 時間戳與來源；IR-02 E408 升等依據改為法說；D14 年限定義（折舊等值 19.9 vs 算術 21.8）。

## 7. 已搜尋，未找到 ／ 未揭露

| 項目 | 狀態 | 說明 |
|---|---|---|
| GPU 數量（H100／H200／B200／B300／GB300） | **未揭露** | 新聞稿、10-Q 擷取段、法說（自動逐字稿全段）都沒有；上次揭露是 2025-09 約 23k 顆，本檔不用 |
| AI 雲使用的 MW（IT 或設施） | **部分揭露** | 只有「operating capacity 0.1 GW」，未定義 IT／設施（法說另有媒體轉述 93 MW，未用） |
| GPU 利用率 | **未揭露** | 只有用電低於銘牌的質性說法 |
| $/GPU·時 | **未揭露** | 公司一律以每 MW (IT) 報價 |
| Microsoft 合約金額本季重述 | **未揭露**（以 10-Q 租賃收入對帳，D7） | 新聞稿與法說都沒有寫 9.7B |
| 本季新約的 GPU 世代 | **未揭露** | 只說「Vera Rubin capacity」在洽約中；新約對應世代為 Assumed |
| GPU 折舊年限、本季是否變更 | **未找到原文** | 10-Q 與 FY26 10-K 經擷取工具都在政策附註前截斷；sec.gov 直連被擋（未申報自動工具）；只有二手 5 年（S7） |
| 借款期限、擔保、LTV、各融資額度 | **未找到原文** | 10-Q 借款附註在截斷段之後；只有法說與 FY26 新聞稿的利率與涵蓋率 |
| 資本承諾明細（Note 24） | **未找到原文** | 只知合計 189.47 億 |
| 法說完整人工逐字稿 | **未找到** | Benzinga、fourweekmba、aistockwire 開啟失敗；stockanalysis 尚未上架；只用 6ix 自動逐字稿（官方 replay 為準）與 stocknow 前 12 分鐘 |
| 服務占比、免費占比、生產折減 | **不可能由出租方揭露** | 屬租戶內部 |

## 8. 來源（查閱日皆為 2026-11-06）

- S1 IREN Q1 FY27 新聞稿（8-K 附件，2026-11-05）：https://www.sec.gov/Archives/edgar/data/0001878848/000187884826000065/irenreportsq1-fy27result.htm ；同文 PDF：https://iren.gcs-web.com/static-files/8b5ff1cc-4a7c-444d-a3bf-bf5a621cf4b7
- S2 IREN 10-Q（2026-09-30 季）：https://www.sec.gov/Archives/edgar/data/0001878848/000187884826000066/iren-20260930.htm （擷取工具只讀到前約 11 萬字，至 Note 11）
- S3 stocknow.ai 法說頁（前約 12 分鐘逐字稿＋AI 摘要）：https://stocknow.ai/en/calls/mrb0nv2gm578dp0jdnvbqxjh/iren_q1-2027-earnings-call
- S4 6ix 法說頁（自動逐字稿，講者未逐行標示，可能誤聽數字）：https://6ix.com/event/iren-limited-iren-q1-2027-earnings-call
- S5 IREN「$9.7bn AI Cloud Contract with Microsoft」簡報（2025-11-03）：https://iren.gcs-web.com/static-files/a421bb34-0156-4687-be7d-19f53a5236e5
- S6 IREN FY26 新聞稿（2026-08-27）：https://www.globenewswire.com/news-release/2026/08/27/3352401/0/en/iren-reports-fy26-results.html
- S7 amcompute GPU 折舊年限彙整（2026-10-10 更新，二手）：https://www.amcompute.com/gpu-depreciation-schedules
- 參考（未作數字來源）：panabee 摘要 https://www.panabee.com/news/iren-earnings-q1-2027 （AI 生成，內部數字不一致）；IREN 10-Q（2026-03-31 季）https://irisenergy.gcs-web.com/static-files/349ea960-38d3-40c6-aa19-4c7cfe0fb67f （GPU 融資租賃 24／36 個月、加權折現率 9.7%、可轉債利率）。
- TK：`model/20261105_Tokenomics_v21.12.xlsx`（Interface 第 7–14、48、219、228、354 列；Alloc_In C23–C24；Cap_In C28–C29；Serving C28；Inputs 第 16–28 列）。

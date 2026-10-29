# 決定變數證據 C 段：Microsoft FY27 Q1 法說後的 Fairwater 占比、OpenAI 同期揭露（唯讀查證）

分支 `claude/evidence-decisive-vars-c`　基準 master `6621bc5`（經 `730441d` 合併；CURRENT v21.7）　工作單 `docs/workorders/20261029_決定變數證據_C段.md`
檔案：`決定變數_C段.xlsx`（審閱檔；以 B 段活頁簿為底，新增「C段判定」「C段證據」兩頁，換算全用公式，LibreOffice 重算錯誤 0）、`證據原稿.md`。未改 `model/`、`builder/`、`tests/`。
承接：B 段（PR #168，`docs/evidence/20261025_決定變數_B段/`）。資料截至 2026-10-29。
模式：LIGHT（資料判讀）。尚待未參與代理獨立核對。

## 結論先行

1. **f 區間不改：仍為 0.4–0.9，中心 0.65（Assumed）。**
   - FY27 Q1 新聞稿、10-Q、法說逐字稿（兩份轉載）都沒有提到 Fairwater、Atlanta、Wisconsin、GW 或 MW。
   - 沒有任何說法給出 Fairwater 的客戶、用途或分配比例；也沒有 RPO 中 OpenAI 的占比。
   - 12 則相關說法逐句判定：偏高 0、偏低 1（弱，全機隊）、中性 6、不可換算 2、無相關說法或未找到 3（xlsx「C段判定」B4:B9）。
   - 唯一帶方向的是 Nadella「we have one pool」（容量依需求訊號在全機隊調度）。它是全機隊說法，與 B 段 F03 同類，已反映在區間下緣 0.4。不足以改區間。
2. **Q2 季平均 GW 與倍數維持 B 段值：** f＝0.4／0.65／0.9 → **2.17／2.26／2.35 GW**，倍數 **0.999／0.959／0.921**（晚日期；早日期 0.925／0.881／0.841）；持平所需 f 仍為 0.395。xlsx「C段判定」B13:D16 直接引用「Fairwater」頁，與 B 段 README 的差值為 0。
3. **新的一手數字（不可換算成 f）：** 10-Q 依關係人規定（ASC 850）揭露（是否為首次，未確認）：**當季來自 OpenAI 的營收 100 億美元（含分潤）**，約占總營收 10.8%，年化 400 億。它沒有拆分 Azure 消費與分潤，也沒有站點；是全公司營收，不是 Fairwater 容量。只記錄，供 OpenAI 模型成本面對照（見 C1）。
4. **OpenAI 同期揭露（10-21～10-29）：無。** API 每分鐘 token、Codex 絕對量、ChatGPT 每日訊息數、每則 token 都已搜尋，未找到。10-26 的 Signals 資料只有份額。**token 帳不變：起點 2.10；B 段各因子結果（D2 1.77、週活 2.12、組合 1.02／1.04）照舊。**
5. **連帶（只記錄）：** capex 452 億（含融資租賃 74 億；二手逐字稿）、PP&E 現金 394 億（10-Q）、Q2 capex 逾 500 億、曆年約 1,700 億；第三方 GPU 容量交付延到下半財年；需求仍超過供給；Azure 成長 48%（Q2 指引 49–50%）；當季新增 24 座資料中心（無 GW）；尚未起租租賃 3,646 億；商業 RPO 6,770 億。

## Facts & Data

### Q1 逐句判定（完整見 xlsx「C段證據」）

| 編號 | 來源（日期） | 內容（改寫） | 標記與誘因 | 對 f 的方向 |
|---|---|---|---|---|
| C01 | 新聞稿（10-28；一手） | 營收 923 億；Azure ＋48%；商業 RPO 6,770 億；無 Fairwater、GW；OpenAI 只在非 GAAP 調整 | Interested-party：Microsoft（財報宣傳） | 無相關說法 |
| C02 | 10-Q 關係人附註（一手） | 當季來自 OpenAI 營收 100 億（「inclusive of revenue-sharing payments」）；應收 72 億；持股約 24% | Interested-party：Microsoft（ASC 850 強制揭露，誘因較低） | 不可換算（全公司營收） |
| C03 | 10-Q RPO 附註（一手） | 商業 RPO 6,770 億、期間 2.3 年；未揭露 OpenAI 占比 | Interested-party：Microsoft | 已搜尋，未找到 |
| C04 | 10-Q 風險因子（一手） | 容量受限時可能調整分配與優先順序；策略夥伴也是 Azure 大客戶 | Interested-party：Microsoft（風險揭露） | 中性（定性） |
| C05 | 10-Q 租賃與現金流（一手） | PP&E 現金 394 億；未起租租賃 3,646 億；融資租賃使用權資產 51.9 億 | Interested-party：Microsoft | 連帶（全公司） |
| C06 | Nadella 開場（逐字稿轉載，二手） | 新增 24 座資料中心；Vera Rubin 上架；無 MW／GW | Interested-party：Microsoft CEO（展示執行力） | 中性（全公司，不得當 Fairwater） |
| C07 | Nadella 答 Morgan Stanley（二手） | 「we have one pool」；依需求訊號動態分配 | Interested-party：Microsoft（淡化專屬） | 偏低（弱；全機隊） |
| C08 | Hood 開場與展望（二手） | 需求超過供給；第三方 GPU-as-a-Service 延到下半年；capex 452 億 | Interested-party：Microsoft CFO | 中性（第三方容量非 Fairwater） |
| C09 | Hood 答問（二手） | 更多配額放進 Foundry；CPU 閒置容量變現 | Interested-party：Microsoft CFO | 中性（Foundry 是推論服務） |
| C10 | Borges 提問（二手） | OpenAI 占當季營收 11%；回答談模型路由 | 分析師引 10-Q | 不可換算 |
| C11 | Nadella 談 MAI（二手） | MAI-Base-2 預訓練完成；無 GPU 數、站點 | Interested-party：Microsoft（展示自研） | 中性（已在 B 段 F10） |
| C12 | Nadella 答 Borges（二手） | 希望 Anthropic 與 OpenAI 競爭每個工作負載 | Interested-party：Microsoft | 中性（非容量） |

### Q1 換算（不變；xlsx「C段判定」引用「Fairwater」頁）

| f | Q2 GW（晚） | 倍數（晚） | 倍數（268 億） | 倍數（早） |
|---|---|---|---|---|
| 0.4 | 2.169 | 0.999 | 1.018 | 0.925 |
| 0.65 | 2.261 | 0.959 | 0.977 | 0.881 |
| 0.9 | 2.352 | 0.921 | 0.939 | 0.841 |

### Q2：OpenAI 同期揭露（10-21～10-29）

| 項目 | 結果 | token 帳 |
|---|---|---|
| D1 API 每分鐘 token | 已搜尋，未找到；最新仍為 03-31 逾 150 億／分 | 不變（A 段 1.87） |
| D2 Codex 絕對量 | 已搜尋，未找到；最新明確週活仍為 06-02 逾 500 萬 | 不變（B 段 1.77） |
| ChatGPT 每日訊息數 | 已搜尋，未找到；Signals（10-26）只有份額，樣本每月 100 萬則 | 不變（週活版 2.12） |
| D3 每則 token | 已搜尋，未找到 | 不變（A 段 1.90） |

### 連帶（xlsx「C段判定」第 20–39 列）
OpenAI 營收占比 10.8%（Derived；與 Borges「11%」一致）；Azure 年增 48.2%（10-Q 產品別營收 331.65 ÷ 223.84，與新聞稿 48% 一致）；capex 452 億 − PP&E 現金 394 億 − 融資租賃 74 億＝ −15.7 億（口徑未對帳，只記錄）；10-Q 的融資租賃使用權資產 51.9 億與 Hood 的 74 億口徑不同。

## Judgment（LIGHT）

- **Stance：** f 區間維持 0.4–0.9、中心 0.65。法說沒有給出 Fairwater 的任何資訊，新證據只有一則全機隊、方向偏低的弱定性說法，以及一則不可換算的 OpenAI 營收。改區間需要有比例或站點的說法，本季為 0 則。
- **Confidence：** 維持 B 段 Low–Medium。C 段沒有提高也沒有降低信心；「法說會提到 Fairwater 客戶」這個判定性證據沒有出現。
- **基準情境與替代（粗略機率，Assumed，沿用 B 段）：** f ≥ 0.4 約 70%；0.25–0.4 約 20%；< 0.25 約 10%。C07 的方向不足以移動機率。
- **最強反向證據與處理：**
  1. **C07「one pool」。** 是全機隊說法，談的是推論與產品之間的調度；Fairwater 是為大型訓練設計的站。依口徑規則只作定性，已由區間下緣 0.4 涵蓋。
  2. **C02 的 100 億可能被讀成「OpenAI 用很多 Azure，所以 f 高」。** 它含分潤，未拆 Azure 消費，且是全 Azure 機隊（不只 Fairwater）；把它換算成 GW 需要價格與分潤假設，屬推論過頭，本段不做。
  3. **C08 第三方容量延遲。** 延遲的是第三方 GPU-as-a-Service（非 Microsoft 自建的 Fairwater），對 Q2（4～6 月）的 Fairwater 占比無資訊。
- **方向檢查（第 10 條）：**
  - 不利於「下降」的選擇 1 個：C07 判為偏低（也可判中性）。
  - 有利於「下降」的選擇 0 個：C02 未被用來上修 f。
  - 中性：維持 B 段區間與其他站低占比。
  - 都沒有收窄 Andy 留下的選項。
- **覆蓋檢查（第 11 條）：**
  - [P] 容量分配：已逐句檢查新聞稿、10-Q、法說；無 Fairwater 分配。
  - [A] 恆等式「比值＝營收 ÷（GW × h）」：f 不變，換算沿用 B 段公式。
  - [I] Microsoft 淡化依賴（C07）、強制揭露誘因較低（C02）、轉載逐字稿可能有轉錄錯誤（TradingKey 的 RPO 單位錯）：已標。
  - 未做：官方逐字稿原檔核對（未取得）；10-Q 風險因子與 FY26 10-K 的逐字比對。
- **判定性證據（Invalidation）：** 與 B 段相同，另加：Microsoft 在後續 10-Q／10-K 拆分 OpenAI 營收中的 Azure 消費；OpenAI 公布 2026 年中以後的 API 每分鐘 token 或 Codex 絕對量。
- **實務意涵：** A2 的 Q2 讀法維持 B 段的「偏下降（中心 0.96，0.92–1.00）」；token 帳讀法不變。

## 已搜尋，未找到 ／ 不存在或不可分離

**已搜尋，未找到：**
- 法說、新聞稿、10-Q 中的 Fairwater、Atlanta、Wisconsin、superfactory、gigawatt、megawatt、superintelligence。
- RPO 中 OpenAI 占比，或「排除 OpenAI」的 RPO 成長（FY26 Q4 有，本季沒有）。
- 當季新增 GW（FY26 Q4 有「約 1 GW」，本季只說 24 座資料中心）。
- Anthropic 容量的站點或規模（10-Q 無 Anthropic 字樣）。
- 官方逐字稿檔與投資人簡報（IR 頁只列檔名，連結未取得；展望簡報為圖片）。
- 10-21～10-29 的 OpenAI API 每分鐘 token、Codex 絕對量或新週活、ChatGPT 每日訊息數、每則 token。
- 未讀：Benzinga、Alphastreet、CNBC、GeekWire（網站拒絕）；aka.ms/FY27Q1Blog（權限逾時）；openai.com Signals 原文（抓取失敗，用二手轉述）。

**不存在或不可分離：**
- 100 億 OpenAI 營收：Azure 消費與分潤不分開；是全公司，不是 Fairwater。
- 24 座新資料中心、capex、未起租租賃：全公司，不得當 Fairwater。
- 「one pool」：全機隊，不含比例，只作定性。
- Signals：份額資料，不含企業版與 Codex，無總量。

## 待 Project 判斷（附預設）

| 編號 | 事項 | 建議預設 |
|---|---|---|
| C1 | 10-Q 的 OpenAI 營收 100 億／季（年化 400 億，含分潤）是否進 OpenAI 模型作成本面對照 | 只作對照註記，不當算力成本輸入；等 Microsoft 拆分或 OpenAI 揭露 Azure 支出 |
| C2 | f 區間 | 不改（0.4–0.9，中心 0.65）；Q2 讀法維持 B 段 |
| C3 | 是否等官方逐字稿上線後補核 | 是；交由獨立核對代理順便確認官方檔無 Fairwater 字樣，結果不同才改 |
| C4 | 是否做 D 段 | 不排；改為事件觸發：OpenAI 公布 token 量、Microsoft 揭露 Fairwater 分配，或 FY27 Q2 法說（2027-01）時再看 |

## OpenAI 模型 v0.6.4 要改的輸入
- **2026 Q2 季平均 GW：不改。** 中心 2.26（f＝0.65、其他站低占比、晚日期），區間 2.17–2.35；倍數 0.959（0.921–0.999）。若 v0.6.4 尚未採用 B 段值（仍為 J7 的 2.34），則照 B 段改為 2.26。
- **token 帳：不改。** API 150 億／分、每日則數、每則 token 照舊；D2 照 B 段 B2 的決定。
- **新增（建議，非必要）：** 註記「Microsoft FY27 Q1 自 OpenAI 認列營收 100 億（含分潤，10-Q 關係人附註）」作成本面對照（C1）。

## 本段限制
- 逐字稿為兩份轉載互相核對，非官方檔；引號內為原文短句，其餘為改寫。
- 新聞稿與 10-Q 讀自 company-models 的抽取檔，未另行從 SEC EDGAR 下載比對。
- f 的區間是判斷，不是來源值。

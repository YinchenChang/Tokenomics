# 9a Q 側缺口：chat 端查證筆記（2026-10-23 21:20；唯讀，不改模型）

- 範圍：雲端 CC 讀不到的部分（SEC、Drive 既有分析）＋三因子的第一輪量化。雲端 CC A 段（W1–W4）完成後，與本筆記合併成 Excel 審閱檔，再由未參與代理獨立核數字。
- 模式：LIGHT。Tokenomics 現行 v21.1（master `4ef0b0a`）。
- 定錨聲明：本 Project 前次（2026-10-17 推論支出調和分析）已主張「84 億為服務推論最佳點估計」；本筆記可能受其錨定。

## 1. 系統定義

- 9a 比值＝84 ÷（`L1_ServeGW_GW25` 0.4624 × `AL_FleetHold` 9.353）＝1.94。
- `B4_Serve` 0.41（Cap_In C28，常數）的說明欄寫明＝84 ÷（84＋訓練約 120）。代入後 9a 比值＝（84＋120）÷（`AL_FleetGW25` 1.128 × 9.353）× 0.4118／0.41 ≈ 1.93 ×1.004。
- 所以 9a 是「OpenAI 2025 全部算力支出 ÷ Tokenomics 對其機隊估的持有成本 105.5 億」，可拆成三個相乘因子：GW（實際平均上線 GW ÷ 1.128）× 價格（實付每 GW·年 ÷ 9.353）× 口徑（204 中屬當年算力使用費的比例）。只有 GW 因子改變 Q（token 帳 `L1_TokLedger_GW25` 1.52）。

## 2. 事實與數據

| # | 數值 | 內容 | 標記 | 來源 |
|---|---|---|---|---|
| C1 | 營業成本 7.5、研發 19.18、行銷 5.73；營收 13.07（2025） | OpenAI 2025 查核財報（外流，FT 核實） | [Verified-ish]；OpenAI 未評論 | techstrong.ai 轉述；Drive `證據研究/20261017_推論支出調和分析.md` F4 |
| C2 | 付 Microsoft 合計 17.21（營業成本 6.05、研發 10.59、行銷 0.53、管理 0.04） | 同 C1 | 同上 | TechFlow（前次分析 F5） |
| C3 | Azure「推論」2025 前三季 8.67（Q1 2.075、Q2 2.947、Q3 3.648）；全年外推 12.3–13.2 | Microsoft 內部文件，權責基礎 | [Interested-party]：Zitron；Microsoft 稱「數字不太正確」 | wheresyoured.at、The Register |
| C4 | Microsoft 對 OpenAI 投資淨損失 41 億（FY26 Q1，2025-07–09；前年同期 6.88 億）；權益法；承諾 130 億、已撥 116 億 | Microsoft 10-Q（2025-09-30） | [Verified] | sec.gov msft-20250930.htm |
| C5 | 隱含 OpenAI 單季淨損：稅後 31 億 ÷ 27%＝約 115 億（heise）；稅前 41 億 ÷ 27–32.5%＝126–152 億 | 由 C4 推 | [Derived]；含非現金與非算力項，只作總量對照 | heise.de；本筆記 |
| C6 | 2024 Epoch：總雲端算力約 70 億（研發約 50、推論約 18） | OpenAI 2024-09 投資人文件 | [Interested-party] | epoch.ai |

## 3. 量化（先敏感度）

**口徑因子（21:30 更正）：** 查核帳把全部算力支出框在約 161–217 億：付 Microsoft 172 億（若營收分成約 26 億在內則 146）＋非 Microsoft 算力（營業成本約 14.5 億＋研發非 Microsoft 算力 0–30 億）。對照 204 億 → s 約 0.79–1.0。（原寫「172–210」漏扣營收分成。）**結論：204 不是高估；約 2 倍的缺口是真實支出，必須由 GW 或價格吸收。**（研發 19.18 扣 10.59 後的 8.6 億×10 含人員與股份酬勞，H1 股份酬勞約 25 億，上限因此不高。）

| 2025 全部算力支出（$B） | ÷ TK 機隊持有成本 10.55 | 若價格＝持有成本，所需平均 GW |
|---|---|---|
| 17.2 | 1.63 | 1.84 |
| 18.7 | 1.77 | 2.00 |
| 20.4（現行 84＋120） | 1.93 | 2.18 |
| 21.0 | 1.99 | 2.25 |

**價格因子（只看 Microsoft 帳）：** 2025 年底 1.9 GW 是時點值，平均約 1.0–1.25 GW；平均 GW 不太可能達 1.84–2.25，所以價格因子應是主因。以 Azure 占 OpenAI 平均算力 70%／85%／100% 試算：

| Microsoft 帳（$B） | Azure 占比 | Azure GW | 每 GW·年（$B） | ÷ 9.353 |
|---|---|---|---|---|
| 14.6（扣營收分成） | 0.70 | 0.79 | 18.5 | 1.98 |
| 14.6 | 0.85 | 0.96 | 15.2 | 1.63 |
| 14.6 | 1.00 | 1.13 | 12.9 | 1.38 |
| 17.21 | 0.70 | 0.79 | 21.8 | 2.33 |
| 17.21 | 0.85 | 0.96 | 18.0 | 1.92 |
| 17.21 | 1.00 | 1.13 | 15.3 | 1.63 |

換成每 GPU 小時（2025 機隊 Hopper 0.6／GB200 0.4，`IF_GPUsPerGW` 718,048／501,768 → 約 63.1 萬顆／GW）：TK 持有成本約 1.69 美元；Azure 隱含約 2.3–3.9 美元。

## 4. 判斷（初步，待 CC 結果）

- **口徑因子約 1.0–1.27（支持，中）**：查核帳總額與 204 相容；Epoch 160 億落在下界。所需價格因子 1.37–2.18。
- **主因在價格因子（部分支持，中低）**：OpenAI 在 Azure 的隱含單價約為 TK 持有成本的 1.4–2.3 倍；這與「同口徑長約 ÷ TK 0.89–1.12」（10-23 持有成本查證）並不矛盾——那是 neocloud 新世代長約，Azure 對 OpenAI 2025 多為 Hopper 世代、可能含隨需與抵用金計價。
- **GW 因子次要（不確定）**：要讓價格因子＝1，平均 GW 須 1.84–2.25，高於年底值 1.9 的大部分區間；只有「1.9 GW 只計自有／Stargate、不含 Azure」這種讀法才成立 → 交 CC W2 查。
- **對 Q 的含義**：若主因是價格，服務 GW 0.46 與 token 帳 1.52 大致不變，9a 不構成 Q 側修正；`B4_Serve` 的支出比代 GW 比需加註「價格倍數兩邊相同才成立」。
- **證偽條件**：(a) 找到 OpenAI 2025 平均或季度 GW ≥ 1.8；(b) Azure 對 OpenAI 的單價揭露 ≤ 2 美元／GPU 小時；(c) 營收分成確認在營業成本中而研發另有大額非 Microsoft 算力。

## 來源
- [Microsoft 10-Q（2025-09-30）](https://www.sec.gov/Archives/edgar/data/789019/000119312525256321/msft-20250930.htm)
- [heise：Microsoft 季報顯示 OpenAI 單季虧損](https://heise.de/-10966190)
- [Where's Your Ed At：OpenAI 文件](https://www.wheresyoured.at/oai_docs/)
- [The Register：OpenAI 在 Microsoft 的推論支出](https://www.theregister.com/software/2025/11/12/openai-has-spent-12b-on-inference-with-microsoft-report/1901006)
- [techstrong.ai：OpenAI 2025 查核財報](https://techstrong.ai/articles/openais-fast-growing-revenues-outpaced-by-massive-scale-of-losses-ahead-of-expected-ipo/)
- [Epoch AI：OpenAI 2024 算力支出](https://epoch.ai/data-insights/openai-compute-spend)
- Drive `02-算力收支/Tokenomics/證據研究/20261017_推論支出調和分析.md`


## 更正（2026-10-27 證據引述回查）

> 來源：API 自動回查（`tools/evidence_audit/`）＋未參與代理人工複核（`docs/evidence/20261027_證據引述回查_人工複核_r1.md`）。原文保留不改，以本節為準。

- **（R9）C6「Epoch：2024 研發算力約 50 億」**：Epoch 原文為 reportedly，50 億是報導的訓練 30 億加 Epoch 自訂研究算力兩年攤提 20 億，不是 OpenAI 投資人文件的原數。只影響文字。

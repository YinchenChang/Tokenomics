# 證據更新 20261008｜P0-1 token 對帳落差的證據蒐集（人工首輪，月度任務的示範）

- 執行：chat 端（Claude，2026-10-08）。範圍：整合版報告 P0-1「服務 GW token 路線 0.052 對支出路線 0.743，落差 14 倍」。
- 本輪只做搜尋、登錄、比對、提案；不寫 SRC、不改輸入、不產生新版 Excel。候選列見 `candidates.csv`（E256–E262，接在 v5.27 的 E255 之後；若 v5.27 尚未合併，編號由 CC 順延）。
- 所有外部來源均開到原文或可追溯的轉述；標記與等級逐筆記於 CSV。

## 結論：落差不是單一錯誤，是四個口徑差的乘積

| 分解項 | 證據 | 倍數（區間） | 標記 |
|---|---|---|---|
| 每則提示 token 數 2,000 偏低 | OpenRouter 2025 年末每請求 6,400（含推理；SRC_DEM_014／015）；Robonomics 假設 800–2,000 | ×1.5–2 | 1 級／Assumed |
| 支出路線用 Azure 計價，非持有成本 | OpenAI 2025 Q1–Q3 推論支出 $8.67B（E259）為 Azure 帳單，含 Microsoft 利潤與資本回收；對持有成本的倍數無公開數字 | ×1.5–3 | Assumed |
| 參考請求 ISL 16K 對實際混合 | Sens_Perf：ISL 4K 時 Sol 每 GW 產出 103T 對 237T | ×1.5–2.3 | Derived（工作簿） |
| 實際利用率 × 生產折減低於 0.6 × 1.0 | 無直接證據；Serving C17／C18 為 Assumed | ×1.5–2 | Assumed |
| 乘積 | — | 5–28（觀測 14 在範圍內） | — |

需求 D 本身的量級有中立對照支持：Google 2025 平均約 33T/日（E256）、中國 2026-02 全部主流模型 180T/日、單一領先實驗室 10–50T/日（E258）；OpenAI 2025 平均 11.5T/日（E261 採用後 16.5T/日）落在合理量級。因此「D 低估 14 倍」的解讀（整合版報告解讀 (a)）不成立；落差主要來自口徑，其次才是生產效率。

## 受影響的 L1 與 Interface

| 名稱 | 方向 | 幅度估計 |
|---|---|---|
| L1_ExtServeGW | 採 E261 後比值 0.07 → 0.10；再採 E259 後回到約 0.07 | 口徑分解後剩餘約 3.5–7 倍歸生產效率與 ISL |
| L1_ExtDaily | 11.5 → 16.5 T tok/日 | 仍在 Epoch 10–100T 區間 |
| L1_Ans1（Q1 研發算力占比） | 服務 GW 增加 → Q1 下降 | 0.64 → 約 0.55（E261）；再採 E259 不影響 token 路線 |
| L1_Ans3 外部對照（SRC_DEM_006 訓練支出） | 不變 | — |
| IF_TokGW_*、IF_RevGW_* | 不變（口徑不改） | 契約須標「參考請求、100%／60% 口徑」 |

## 待 Andy 判定（判斷類）

1. E259：SRC_DEM_004 是否由 $8.4B 改為 2025 全年推估 12.3–13（區間），或維持 8.4 並在備註記錄 Q1–Q3 $8.67B。差異來源：json 的 8.4 可能是不同口徑（例如不含 Microsoft 分成或為年初預算）。
2. E261：Alloc_In「每則提示 token 數」基準 2,000 → 4,000、區間 2,000–6,400。這是 Gov_Map 高段 Assumed，改值屬判斷類。
3. E262：是否在 L1 新增四項分解列（併入 v5.29 第 3 節），把 14 倍落差做成可逐項驗證的乘積，並在契約第 5 條改寫為「落差由四項口徑差構成，下游以自身口徑逐項換算」。

## 已搜尋、未找到

- OpenAI 自揭的每日總 token（API＋ChatGPT）：未找到 2025–2026 任何一手數字；只有 API tok/min（已登錄）與 ChatGPT 每日訊息數（已登錄）。
- OpenAI 對 Microsoft Azure 的實付單價或折扣：未找到；E259 的文件只有總額。
- ChatGPT 每則提示的平均上下文長度：未找到一手數字。
- Anthropic 每日 token：未找到。

## 下次建議搜尋

- OpenAI、Anthropic 的 IPO 文件（若已公開）中的 token 量與推論成本口徑（CNBC 2026-06-10 報導提及，頁面 403 未讀）。
- Microsoft FY26 Q4／FY27 Q1 財報電話會的 token 數（FY26 Q3 未給總量）。
- Google 2026 Q3 財報的每月 token（I/O 後是否再更新）。

## 來源

- Shacknews 2026-05-19：Google 3.2 quadrillion tokens/month（Pichai I/O 2026）
- The Decoder 2025-10：Google 1.3 quadrillion tokens/month 與 980T 的比較
- Microsoft FY25 Q3（2025-04-30）與 FY26 Q3（2026-04-29）財報電話會逐字稿
- Where's Your Ed At 2025-11-12：OpenAI 推論支出與 Microsoft 分成（文件未公開）
- Robonomics《Token Tracker & Implications》：各家 token 揭露彙整（含中國數字的轉述）
- arXiv 2601.10088v1 OpenRouter State of AI（SRC_DEM_014–017，既有）

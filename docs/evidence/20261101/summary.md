# 月度證據更新 20261101｜比較摘要

- 執行：Claude 排程任務（雲端，2026-11-01 00:50 UTC 起）。Excel：`model/20261025_Tokenomics_v21.7.xlsx`（master `90f7deb`）。
- 範圍（依 `docs/reports/20261008_eval_integrated.md` P1-6 與工作簿 Decisions G2、G6）：只做搜尋、登錄、比對、提案。**不寫 SRC_\*、不改任何輸入值、不產生新版 Excel。**
- 11 月週期：SRC_Price 每月必做；SRC_Perf／HW／DC／Demand／Harness／Cap 只做事件觸發；SRC_Model 只做事件觸發；低信心清單每月必做。Drive `外部搜尋/intake/` 為空，無已通過 G1 的外部搜尋結果可先讀。
- 搜尋清單 40 項（SRC_Price 11、低信心清單 29：3 級 Active 69 筆合併為 20 項、利害關係方缺第二來源的高敏感度紀錄 19 筆合併為 10 項；審查日超過 90 天者 0 筆）＋ 1 項事件掃描。清單全文見 PR 說明末尾附錄。
- 候選列：`candidates.csv` **E412–E475，共 64 筆**（接在 DB_Evidence 最大編號 E411 之後）。建議判定：取代 21（其中 18 筆為「等級升級、值不變」）、並列 22、不採納 15、**待 Andy 6**。
- 其他產出：`workorder_draft.md`（草稿，判斷類待 chat 端定案）、`research_directions.md`（Andy 調研方向，參考非結論）。

## 一句話結論

API 牌價全部未變（13 個模型逐一核對，8 筆由「未直接讀取」升為一手已讀）；GPU-hour 牌價與 10 月前相同；9–10 月沒有新的大型 AI 基礎設施長約。**三件事需要判斷：**（1）Nebius 自 2026-01-01 起把 GPU 折舊年限由 4 年延長到 5 年（20-F 與兩份 6-K 一手），工作簿高成本情境仍用 4 年；（2）NVIDIA 現行 Vera Rubin NVL72 規格頁把 HBM4 頻寬寫成 19.2 TB/s（工作簿 22）、NVLink 每 GPU 3 TB/s（工作簿對應 3.6 雙向），與同公司 1 月／3 月說法不同；（3）Artificial Analysis Intelligence Index 已改版 v5.0，Cap_In F 節 11 筆 v4.3／v4.3.2 分數在來源頁已不存在且跨版本不可比（GPT-6 Luna 由 37 變 21，開放權重 DeepSeek V4.1 Flash 1017 為 32）。

## 受影響的 L1 列與 Interface 名稱（方向與幅度估計）

幅度全部為本月以工作簿現值做的外推，標 [Derived]；正式數字以 chat 端定案後 LibreOffice 重算為準。

| 候選 | 變動 | 受影響名稱 | 方向 | 幅度估計 | 標記 |
|---|---|---|---|---|---|
| E467 | Inputs!F23 IT 設備折舊年限 4 → 5（高成本情境欄） | `IF_HoldEcon*`、`L1_HoldEconMW_*`、`IF_Depr*`、`IF_MaintIT`（高成本欄）、`IF_FullCost*_Hi`、`IF_Amort*_Hi` | 高成本情境持有成本**下降**；基準與低成本欄不變 | 以 DC_Cost 第 53／55 列現值與 WACC 13% 重算：IT 資本回收係數 0.3362 → 0.2843（−15.4%）；經濟口徑年持有成本 Hopper −10.6%、GB200 −10.0%、GB300 −11.0%、VR200 −11.2%、Rubin Ultra −12.1%；會計口徑 IT 折舊 −20% | [Derived]，[Verified] 20-F／6-K |
| E445 | SRC_HW_030 22 → 19.2 TB/s；SRC_HW_049 1.8 → 1.5 TB/s（單向） | `IF_TokGW_*`（VR200 欄）、`IF_Cost*`／`IF_RevGW*`（VR200）、`L1_TokMW_Gen_ratio_VR200`、`L1_GenPxThr_*_VR200`、`L1_HarVsGen` | VR200 decode 記憶體受限區段產出**下降**；GB300→VR200 世代產出比下降，持平門檻 `L1_GenPxThr_Rev_VR200` 向 0 靠近（所需年降價變小） | 記憶體受限上限 ∝ 頻寬：最多 −12.7%；EP 通訊項 ∝ NVLink：最多 −16.7%；實際為 roofline 取 min 後的結果，可能小於上限 | [Interested-party] NVIDIA 一手，內部前後不一 |
| E438／E462 | Cap_In F 節 I 欄能力指數改版 v5.0 | `Price_Frontier` 前緣選取、`CAP_Price25Mix`、`L1_MImplied*`（若前緣候選改變） | 方向**未定**：v5.0 下 Luna (High) 21 低於開放權重 Flash 1017 (Max) 32，前緣可能由開放權重模型重排 | 無法在不重基準 13 個模型前估計；需一次查齊 | [Verified] 中立一手 |
| E450 | Spec_Rack!E12 GB300 機架價 4.0 → 約 5.0（採購單說法） | `IF_HoldEcon*_GB300`、`L1_HoldEconMW_GB300`、`IF_FullCost*`（GB300 欄） | **上升** | 機架占 GB300 總資本支出 29.1／44.9＝65%（DC_Cost 基準）；機架 +25% → 資本支出 +16%，經濟持有成本約 +13–14%（資本回收占 82%） | [Analogy] 二手無原件，建議只進區間高端 |
| E428 | Cap_In!F58 MiniMax M3 快取價空白 → 0.06 | Price_Frontier 候選表 MiniMax 混合單價 | 下降（原以新鮮價 0.3 代入） | MiniMax 非 OpenAI 層級代表；不影響 `IF_`／`L1_` | [Interested-party] 一手 |
| E424 | SRC_PRC_028 每週尖峰 35 小時未扣中國假日 | `Cap_In!C17` 尖峰時數 → DeepSeek 有效折扣 | 有效尖峰時數**下降**約 4–5%（每年約 11–13 個工作日假日 ÷ 250） | 小 | [Verified] 官方頁 |
| E470 | CAL_BatchEtaD GB200 校準第二來源 SGLang 13,386（vLLM 10,100） | `RNG_*` 區間（GB200 倍數 1.83–3.04）、`IF_AllocRDGW`、`IF_AllocQ1` | 若以 SGLang 校準，GB200 倍數上端**上修**；`IF_AllocRDGW`／`IF_AllocQ1` 低端再降 | 13,386 ÷ 10,100＝1.33；倍數上端 3.04 × 1.33 ≈ 4.0（線性外推，未重解） | [Interested-party] 框架團隊 |
| E429、E417–E420、E427、E442–E444、E448、E451、E454、E456–E460、E466、E469 | 等級升級、值不變 | 無數值變動；`GOV_Warnings`（3 級×高段、利害關係方缺第二來源）下降 | — | 3 級 Active 69 筆中約 30 筆可結案；缺第二來源清單結案 1 筆（SRC_DC_007），補第二來源 4 筆（SRC_MOD_029、PERF_037、PERF_074、DEM_012） | — |

## 待 Andy（6 筆）

| 候選 | 事項 | 為何不能自動判定 |
|---|---|---|
| E438、E462 | AA Intelligence Index v5.0 整欄重基準 | 一級中立證據落在現值外（G6）；跨版本不可比，必須 13 個模型同時換版 |
| E445 | VR200 HBM4 19.2 TB/s、NVLink 3 TB/s（NVIDIA 現行頁）對 1 月／3 月的 22／3.6 | 同一廠商前後不一；高敏感度世代欄的直接輸入 |
| E450 | GB300 機架價採購單「just under $5.0M」對 MS 4.0 | 二手無原件；高敏感度 GM092 |
| E455 | JPM AM「網路占 AI 支出 15%」原文找不到 | Active 紀錄出處無法核實，且 Inputs!F13 直接使用 |
| E464 | Codex 每日 2 兆 token 的「40 兆」原文找不到 | 3 級 Active 紀錄無法核實（僅對照列） |

## 衝突調和（第 9 條）

- E438 說 Luna 能力指數 37 → 21，E415 說新層級 Terra 介於 Luna 與 Sol 之間：兩者都指向 Cap_In F 節的層級代表與前緣要一起重看，不是各自改一格。
- E445（NVIDIA 現行頁 19.2／3.0）對 E446／SRC_HW_046 備註（Hashrate Index 3 月：22／3.6）：以日期較新的 NVIDIA 一手為準是 G4 順序（等級 → 立場 → 口徑 → 日期）的結果，但頁面標「Preliminary」，所以列待 Andy 而非直接取代。
- E467（Nebius 5 年）對 Inputs 第 23 列說明「高成本情境取 4」：延長後高成本情境失去「4 年」的實證錨點；Lambda 5 年（SRC_DC_009）成為新的高成本錨點，與 Nebius 一致。
- E461 現行 InferenceX 成本低於工作簿快照約 10 倍：口徑（agentic-traces 對 8K/1K）、模型版本（preview 對 0813）、GPU 價來源（2026-07 調查）三項同時變，不是數據錯誤；維持快照、更新備註（v17.2 Q10 既有處置）。

## 已搜尋，未找到

- Kimi K3 官方 API 價格數字（官方頁為 JS 渲染，三次抓取空表；platform.kimi.ai／platform.kimi.com 同）。
- 2026-09～10 月 IREN、Cipher、TeraWulf、Applied Digital、Nebius、CoreWeave、Nscale、Crusoe、Core Scientific、Hut 8、Riot、Galaxy 任何含金額＋MW＋年期的新長約。
- Verda、Nebius、Lambda 的 GB200 公開牌價（只有 CoreWeave 有）；Verda／Nebius／Lambda 的預留**牌價**（只有折扣率或「報價」）。
- NVIDIA 一手的 Rubin GPU 功率（1.8 kW）、Rubin Ultra NVL576 規格（15 EF、4.6 PB/s）。
- 黃仁勳「每 GW 50–60 B、NVIDIA 35 B」的 CNBC 原文（只有 Forbes 轉述）。
- J.P. Morgan AM Eye on the Market「網路占 AI 支出 15%」（兩份 EOTM PDF 皆無）。
- OpenAI Codex 每日 2 兆 token 或「40 兆 token」的官方原文；OpenAI 2026 年的 ChatGPT 每日訊息數；OpenAI 10 月任何 token 量自揭。
- OpenAI 2025 推論支出 $8.4B／免費 $3.9B 的獨立第二來源（Reuters 只給「4 倍」與毛利 33%）。
- OpenRouter 每請求 6,000 token 的獨立量測。
- InferenceX GB300／GB200 V4-Pro @72／110／130 tok/s/user 各點在現行來源頁；非 SemiAnalysis 的 GB300／GB200 同模型同 tok/s/user 量測（只有 MLPerf DeepSeek-R1 可作區間對照）。
- Llama 3 MFU 38–43% 的獨立第二來源（只有 >90% goodput 有）。
- NVIDIA 10 月 Vera Rubin 出貨量數字（只有 OCI GA 公告）。

## 事件掃描結果（決定其他分區是否觸發）

- MLPerf：v6.1 於 2026-09-16 發布，已登錄（SRC_PERF_052–055）；10 月無新輪 → SRC_Perf 不觸發。
- 新世代出貨：Vera Rubin NVL72 於 OCI GA（10-27），無量化數字 → SRC_HW 不觸發；但規格頁更新（E445）另列待 Andy。
- 新旗艦：Gemini 4 Argon GA（10-13）、GPT-6.1 Terra（10-26，中階）、DeepSeek V4.1-Flash-1017（10-17）、Kimi K3.1 Pro（10-23）、MiniMax M3.1 Flash、Claude Haiku 5.5（10-07）；OpenAI／Anthropic 無新旗艦 → SRC_Model 不觸發（K3.1 Pro 權重釋出後下月查 config）。
- 自揭：Anthropic S-1（10-26）已由 chat 端 2026-10-26 處理（`docs/evidence/20261026_Anthropic_S1`）；OpenAI 年化 $50B 已登錄（SRC_DEM_062）→ SRC_Demand 不觸發。

## 方向與覆蓋檢查（第 10、11 條）

- 方向：本月 6 筆待 Andy 中，3 筆（E438、E445、E450）的解讀若採新值會**縮小**現有區間或改變基準，3 筆（E455、E464、E462）是「來源無法核實」的降級；18 筆「等級升級、值不變」不改任何自由度。沒有把 Andy 開放的區間自行收窄。
- 覆蓋：SRC_Price 11 項全部執行；低信心清單 29 項全部執行；SRC_Harness、SRC_Cap（METR）本月依週期未搜尋（1、4、7、10 月做），**刻意排除**而非遺漏；AA 指數改版是在 SRC_Price 牌價核對時連帶發現。層別：[P] 物理（規格、吞吐）、[A] 會計（折舊年限、牌價、長約）、[I] 誘因（付費新聞稿、投資人揭露）三類都有候選。

## 下次建議搜尋（2026-12-01）

1. Artificial Analysis v5.0：一次查齊 Cap_In F 節 13 個模型（含 Terra、Haiku 5.5、K3.1 Pro）的分數與版本，供 E438 定案。
2. Kimi K3／K3.1 Pro 官方價格：改用瀏覽器工具渲染 platform.kimi.ai；K3.1 Pro 權重釋出後讀 config.json（SRC_MOD_059–062 更新）。
3. NVIDIA Vera Rubin NVL72 正式 datasheet（是否仍 19.2 TB/s、3 TB/s）；Rubin GPU TGP 一手。
4. Nebius Q3 2026 6-K（11 月）：折舊年限 5 年是否再變；CoreWeave Q3 10-Q。
5. JPM AM EOTM「smothering-heights」「the-blob」（2025-09-24）兩份未查 PDF，確認 15% 是否存在。
6. OpenAI Codex「40 兆 token」原始出處（可能為 Codex 週年或 DevDay 2026 投影片）。
7. GB300 NVL72 採購價原件（Wing VC 所稱 purchase orders）。
8. 1 月為季度月：SRC_Perf（MLPerf v6.1 完整 per-GPU 表、InferenceX dashboard 現行點）、SRC_Harness（METR 新版）、SRC_Cap 全部重做。

## 來源（可開啟者）

主要一手頁面：developers.openai.com/api/docs/pricing；platform.claude.com/docs/en/about-claude/pricing；api-docs.deepseek.com/quick_start/pricing；docs.z.ai/guides/overview/pricing；alibabacloud.com/help/en/model-studio/qwen3-8-max；platform.minimax.io/docs/guides/pricing；coreweave.com/pricing；verda.com/pricing；nebius.com/prices；lambda.ai/pricing；nvidia.com（H100、GB200 NVL72、Vera Rubin NVL72、NVLink）；developer.nvidia.com Blackwell Ultra 技術部落格；SEC EDGAR（CoreWeave 10-K／10-Q、Nebius 20-F／6-K、Anthropic S-1）；huggingface.co/deepseek-ai（V3、R1、V4-Pro、V4-Flash config.json）；arXiv 2412.19437、2407.21783；github.com/deepseek-ai/open-infra-index；jll.com Global Data Center Outlook 2026；turnerandtownsend.com；hedgehog.cloud；artificialanalysis.ai；inferencex.semianalysis.com；vllm.ai；lmsys.org；nber.org w34255。各筆 URL 見 `candidates.csv` 出處欄。

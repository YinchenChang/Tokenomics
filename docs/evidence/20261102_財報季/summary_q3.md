# 2026 Q3 財報證據登錄（TK 每 GW 基準）｜摘要（子代理報告，chat 端代存）

- 範圍：MSFT FY27Q1 10-Q／新聞稿／逐字稿；Alphabet 新聞稿、簡報、逐字稿（10-Q 未提供）；Amazon、Meta 10-Q 與逐字稿（含 Meta 追加說明會）；SpaceX 10-Q 與逐字稿。對照 v21.7 與 20261101 候選。
- 候選 E476–E507 共 32 筆：並列 14、不採納 16（轉 Wattonomics 3、轉 company-models 2）、待 Andy 2。英文引句 32 筆皆以程式比對原文找到。
- **一句話結論：本季財報沒有推翻任何 TK 每 GW 基準。** Alphabet 一手確認伺服器與網路設備 6 年；四份 10-Q 都沒有耐用年限估計變更；短壽資產占資本支出 0.65–0.75 包住 TK IT 占比 0.655–0.748。

| 候選 | TK 名稱 | 現值 | 證據值 | 判定 |
|---|---|---|---|---|
| E476 | Inputs!E23 IT 折舊（基準） | 6 | Alphabet CFO「six years」 | 並列：補一手來源，值不變 |
| E477–E479 | Inputs!F23（高成本） | 4 | 本季無任何公司用 4 年（Amazon 口頭 5–6、Meta 隱含 5.4–6.3） | 加強 20261101 E467 改 5 的論點 |
| E482 | AL_SpendBasis 1.8（0.85–2.3） | — | SpaceX CFO：現貨約 $50/W·年＝GB300 經濟持有成本 4.6 倍（3 年、可 90 天終止的短約，短缺期） | 待 Andy；預設並列不改 |
| E483 | 同上 | — | 已實現粗估 1.4–2.8 | 並列（與既有新約群重疊） |
| E488 | SRC_Demand | — | Google API 32B tok/min | 並列，第二錨點（OpenAI 15B） |
| E489 | AL_APIratio 0.75 | — | Google 0.72–0.73；Bedrock 0.60 | 不改 |
| E494 | NonNV | Maia 200 0.55 | Maia 300「每瓦 token +40%」→ 0.93–1.4 | 待 Andy；預設不新增列（未出貨） |
| E495 | TPU 每 token 成本比 0.875 | — | TPU 8i 1.8 倍說法 → 0.49 | 類比，不改 |
| E485、E486、E490 | Cap_In g −0.09 | — | 租價、每 token 營收上升（方向） | 反方證據，不改 |
| E497 | — | — | 「30–40% 性價比」是 Graviton 對 x86，不是 Trainium | 不採納 |

- 已搜尋未找到（原文不存在）：每 GW／MW 建置成本、機架價、加速器單價；利用率百分比；Azure／Meta／Grok token 量；MTIA（13 份 0 次）；Trainium／TPU 對 NVIDIA 數字；GPU 小時牌價、backlog 每 MW 單價、免費用戶占比；每 token 成本年降實績；電價、PUE。
- 互證：E467（Nebius 5 年）＋CoreWeave 6、Lambda 5、Alphabet 6 → 已無 4 年錨點。E507 Gemini 4 Carbon 59 分與 E438（AA v5.0）一致。

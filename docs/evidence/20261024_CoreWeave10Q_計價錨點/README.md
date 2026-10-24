# CoreWeave 2026 Q2 10-Q：計價倍數的出租方錨點（唯讀查證）

分支 `claude/evidence-crwv-10q-anchor`　基準 master `ba784f4`　來源：Drive `Tokenomics/inbox/CoreWeave 2026 Q2 10-Q.pdf`（SEC 原文 PDF，crwv-20260630）
檔案：`CoreWeave10Q_錨點.xlsx`（審閱檔，全用公式，LibreOffice 錯誤 0）。未改 `model/`、`builder/`、`tests/`。模式：LIGHT。

## 結論先行
1. **10-Q 沒有兩項原本要找的東西。** 全文沒有 active power 的定義（「active」只出現在 8-K 新聞稿與法說），也沒有列 GPU 耐用年限（「重大會計政策無重大變更」，指向 2025 年 10-K）。所以 active power 是 IT 電力還是設施電力，仍未證實。
2. **出租方價格錨點：每 active GW 年營收 ÷ TK 持有成本＝0.76–1.42，中心約 0.9–1.0。**
   - Q2 營收 25.75 億美元，年化 103 億美元。
   - Q2 平均 active GW 為 1.15–1.25（6 月底約 1.5 GW，Q2 新增約 0.5 GW，其中 6 月逾 0.3 GW）。
   - 每 GW 年營收：IT 口徑 8.2–9.0；若 active power 是設施電力（PUE 1.2–1.4），則為 9.9–12.5（$B）。
   - 對照 TK 持有成本 GB200 8.83、GB300 10.89 $B/GW·年。
   - **讀法：** CoreWeave 這種出租方，向全部客戶收的單價約等於 TK 的持有成本，沒有出現 1.8 倍。這與 Azure A 段的「獨立錨點重心 1.0–1.5」同向，偏向 `AL_SpendBasis` 1.8 的下緣。但 1.8 是 OpenAI 的跨供應商混合殘差（含 Azure），這筆不能直接推翻它。
3. **耐用年限交叉檢查：** 由 H1 折舊 25 億美元與折舊資產毛額推回，平均耐用年限約 6.5 年，與 TK `IF_DeprLifeIT` 6 年一致。新資產集中在後段時，簡單平均會偏長。

## 標記
- 營收、PP&E、折舊：Verified（10-Q）。
- active power 1.5 GW：Verified（8-K），但口徑未定義。
- Q2 新增 0.5 GW、6 月 0.3 GW：報導（法說摘要，二手）。
- PUE：Assumed。
- **反向因素：** 新上線容量通常還沒全額計費（爬坡），這會讓每 GW 營收偏低，使錨點低估價格；另外 98% 營收來自承諾合約，比隨需價低。

## 待 Project 判斷（附預設）
| 編號 | 事項 | 預設 |
|---|---|---|
| J1 | `AL_SpendBasis` 1.8 | 不改；DB_Evidence 記一筆「出租方錨點 0.76–1.42，弱反對 1.8 上緣」，併入下一版 TK |
| J2 | active power 口徑 | 下次讀 CoreWeave 10-K（2026 年報）或法說逐字稿時查 |

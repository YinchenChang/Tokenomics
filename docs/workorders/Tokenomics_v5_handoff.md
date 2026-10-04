# Tokenomics v5 交接文件（2026-10-04，PR #13 審查通過、等 CI；v5.15 工作單修訂版 r2 待交 CC；分工改為 CLAUDE.md 修訂五）

新對話串開始時請先讀本文件；程式與現行 Excel 從 repo 取得（見 Tokenomics_builder_v5.md 還原步驟第 1 點：`model/CURRENT`、`builder/` 或 `docs/builder/Tokenomics_builder_v5.md`），現行 Excel 為 `20261002_Tokenomics_v5.11.xlsx`（chat 端 2026-10-02 交付；SHA-256 941b78ad…b103；CC 第 11 輪分支 `claude/new-session-r21jsl` 已將 `CURRENT` 指向 v5.11，合併前 master 仍指向 v5.10）。CC 回報可直接以報告開頭的 SHA 從 raw.githubusercontent.com 讀取。

## 0. 新對話串的起點（2026-10-04，PR #13 審查與 v5.15 工作單 r2 後更新）

**分工（Andy 2026-10-04 指示；第 4 節已改寫）**：凡 CC 能做的都交給 CC。chat 端只做三件事：與 Andy 討論、規劃（寫工作單）、審查 CC 的成果（讀報告、diff 與抽查，不重建整本）。chat 端不再交付 Excel 或 builder md。
**目前狀態**：PR #13（CC 第 13 輪續，v5.14 同步）chat 端審查通過（第 8w 節），未合併；合併條件為 CI 在最新提交 `1a939472` 全綠，並從該次 job summary 讀出 CI 重算秒數。v5.15 工作單初版已在 master `docs/workorders/`，**尚未交給 CC**；修訂版 r2（第 8w 節）由 Andy 上傳取代初版，PR #13 合併、master `CURRENT`＝v5.14 後再交給 CC。
**等待 CI 的規則（2026-10-04，第 8v 節）**：CI 不再是序列中的等待點。CC 推報告後，chat 端即可審查；CC 在 CI 執行期間可在新分支續做下一份工作單；合併仍以 CI 全綠為門檻。CC 另做 CI 提速（分片並行、引擎編譯快取），見第 8v 節指令。
**chat 端下一步**：審查 v5.15 報告的「預期變動 vs 實際變動」兩張表，並抽查 Q1、Q2、隱含 N × k、三列外部對照、敏感度表自我檢查與 parity 結構期望值的舊新值。之後是 Stage 2 查核與 OpenAI v0.6。

（歷史）

**v5.14（chat 端 2026-10-04 交付；結果見第 8s 節；CC 指令見第 8t 節）**：Excel `20261004_Tokenomics_v5.14.xlsx`（SHA-256 dc4ef406…2b56）與 `Tokenomics_builder_v5.md`（v5.14，15 檔，SHA-256 95f78f89…dc43）。修 CC 第 13 輪發現的 L1 錯誤值（O、P 欄未檢查 D 欄），並把 SRC 各頁 X 欄的比對範圍縮到 SRC_Index 的範圍（全簿重算約減三成）；基準數值不變。
**版號（工程類，chat 端定案）**：依 CLAUDE.md 版本規則（每版加 0.1、檔名 vN），公式修正即一個次版，故為 v5.14；**Block 6 Alloc 改為 v5.15**（第 8f 節設計不變）。
**交付順序**：PR #13（CC 第 13 輪，v5.13 同步）**不以紅燈合併** → Andy 上傳 v5.14 Excel 到 repo `model/`、builder md 取代 `docs/builder/Tokenomics_builder_v5.md`（master 直接上傳）→ 把第 8t 節指令交給 CC，在同一分支（PR #13）續做 v5.14 同步 → CI 全綠後合併。合併後 master `CURRENT`＝v5.14，v5.12、v5.13 皆在 `model/archive/`。
**之後**：v5.15 Block 6 Alloc（Answers 寫入 L1）→ Stage 2 查核（優先序同下方「（歷史）v5.13」段）→ OpenAI v0.6（Stage 3）。
**留意（工程類）**：全簿強制重算在 v5.13 已逼近 2 秒門檻（CC 本機 1.76 秒；2026-10-04 chat 端這台較慢的機器 2.44–2.71 秒）。v5.14 縮小 X 欄範圍後，同一台機器 1.68–1.76 秒（約減三成）。剩餘最大項為 Gov_Map AF 欄（574 個 MATCH，約 0.44 秒，占約四分之一）。v5.15 新增 Block 6 公式後須再量；若接近門檻，先改 AF（例如依 SRC_ID 前綴只查該頁區段），不放寬門檻。CI 秒數以第 13 輪續做的報告為準。

（歷史）
**v5.13（chat 端 2026-10-03 交付）**：見下段原文；CC 第 13 輪驗收見第 8s 節。

**v5.13（chat 端 2026-10-03 交付；結果見第 8m、8n、8o、8q 節；CC 指令見第 8r 節）**：Excel `20261003_Tokenomics_v5.13.xlsx`（SHA-256 9b76f1e5…6540）與 `Tokenomics_builder_v5.md`（v5.13，15 檔，SHA-256 760d09d0…739f）。Andy 2026-10-03 對三份審閱檔（v5.11、C 包、D 包）皆回覆全部依建議，已全部寫回；原話確認後第 2 節已縮為決策 ID 清單（G11）。
**交付順序（工程類）**：先等 PR #12（CC 第 12 輪，v5.12 同步）合併 → Andy 上傳 v5.13 Excel 與 builder md 到 repo（取代 `docs/builder/Tokenomics_builder_v5.md`）→ 把第 8r 節指令交給 CC。合併前 Project 內的 builder md 檢查點保留；v5.13 上傳 repo 後，Project 內的 builder md 可刪除（依原規則 repo 為準）。
**之後**：v5.14 Block 6 Alloc（第 8f 節設計不變；Answers 改寫入 L1）→ Stage 2 查核（優先序：審閱檔 Stage2_優先、Checks W2 33 格；另列：V4-Flash config 已讀可升級的 7 筆 3 級 SRC_Model、Arch C34 每層 KV 以結構重算、Train_In C44 與 Calib C69 改公式、Checks 第 21 列 2.12 與 Hopper 占機隊 0.6 的來源）→ OpenAI v0.6（Stage 3）。

（歷史）
**v5.13 E 包（部分，2026-10-03，見第 8p 節）**：Andy 對 D 包審閱檔回覆「BOTH ok」，已寫回。檢查點改為 `Tokenomics_builder_v5.md`（SHA-256 3a56a831…0ef1）與 `20261003_Tokenomics_v5.13BCDE_wip.xlsx`（SHA-256 db1479dd…92d0），取代 D 包檢查點。**剩下的唯一待辦**：`20261003_v5.11_待Andy_審閱檔.xlsx` 尚未回填（chat 端找不到回填檔，該檔不在 Project 與 repo）。Andy 回填（或回覆「全部依建議」並列例外）後寫入 Gov_Map O／M 欄與 Decisions J 欄；若選擇延後，v5.13 即可交付，v5.11 審閱移到下一版。另：repo 已出現 PR #12（CC 第 12 輪，2026-10-03 chat 端以 git ls-remote 看到 refs/pull/12；master 仍為 8d232db、`CURRENT` 仍指向 v5.11），v5.13 交付仍須等 PR #12 合併。


**v5.13 D 包（模型邏輯；chat 端 2026-10-03 完成，結果見第 8o 節）**：Andy 2026-10-03 對 C 包審閱檔回覆「all ok」（提議區間 16 列、標記變更 14 列全部採用，已寫入 Gov_Map）。檢查點改為 `Tokenomics_builder_v5.md`（v5.13 B＋C＋D；SHA-256 ca07fc42…1289）與 `20261003_Tokenomics_v5.13BCD_wip.xlsx`（SHA-256 7524ffde…20f3），取代 C 包檢查點。新審閱檔 `20261003_v5.13D_待Andy_審閱檔.xlsx`（提議區間 2 列）。（歷史）續做時一律以 master 的 v5.12 為底稿、以本 Project 的 builder md 還原 15 檔重建（Gov_Map 新列為 Excel 擁有，wip 檔只供檢視，不作底稿）。


（歷史）**v5.13 C 包（Gov_Map 擴及切片二頁；chat 端 2026-10-03 完成，結果見第 8n 節）**：檢查點改為 `Tokenomics_builder_v5.md`（v5.13 B＋C；SHA-256 82a0d6c7…7d48）與 `20261003_Tokenomics_v5.13BC_wip.xlsx`（SHA-256 4399d20e…57bd3），取代 B 包檢查點。新審閱檔 `20261003_v5.13C_待Andy_審閱檔.xlsx`（提議區間 16 列、標記變更 14 列）。下一步 D 包。

**v5.13 B 包（切片二 Source 遷入；chat 端 2026-10-03 完成，結果見第 8m 節）**：開工時 repo 尚無 PR #12（master `CURRENT` 仍為 v5.11），但 Andy 已上傳 v5.12 Excel（SHA-256 d04fac3b…0926，chat 端核對一致）與 v5.12 builder md（chat 端以其還原 builder、以 v5.12 為底稿重建，逐格不符 0）；判定（工程類）以此底稿先做 B 包。B 包檢查點（builder SHA-256 9155c261…6d6e、`20261003_Tokenomics_v5.13B_wip.xlsx` 8039e81a…f73a）已由 C 包檢查點取代。**PR #12 合併前，v5.13 的 builder md 不得上傳 repo**（CC 第 12 輪以 repo `docs/builder/` 的 md 作為 v5.12 builder）；檢查點暫存本 Project，v5.13 交付後刪除。新對話串續做 C 包時：從本 Project 的 builder md 還原 15 檔，以 wip 檔為底稿重建（或以 master 的 v5.12 為底稿，結果相同）。

**v5.12（chat 端 2026-10-03 交付，待 CC 第 12 輪同步）**：原規劃的 A 包（工程基礎）獨立成版，結果見第 8k 節，CC 指令見第 8l 節。Excel `20261003_Tokenomics_v5.12.xlsx`（SHA-256 d04fac3b…0926）與 `Tokenomics_builder_v5.md` 由 Andy 上傳 repo，Project 不存。**版號調整（2026-10-03，工程類，chat 端定案）**：A 包改公式且數值不變，依版本規則本身即一個次版；獨立同步可讓 CC 的 CI 先驗收重算門檻，B 包之後照常從 master 還原。因此原 v5.12 的 B–E 包改為 **v5.13 切片二**（第 8j 節工作包內容不變），Block 6 Alloc 改為 **v5.14**。v5.13 開工條件：PR #12 合併後，從 master 還原 builder 與 v5.12。


**repo 狀態（2026-10-03 chat 端確認）**
- PR #11 已合併（a9bc1061，2026-10-03 12:25 UTC）：master `model/CURRENT`＝`20261002_Tokenomics_v5.11.xlsx`（SHA-256 941b78ad…b103），`builder/` 含 `gov.py` 等 14 檔。合併後 CI parity 第 67 次於本文件更新時仍在執行。報告 `docs/reports/20261002_v5.11_sync.md`、`20261002_gate1.md`。
- chat 端已從 master 還原 builder 並以 v5.11 為底稿重建：restore 對應 1,021、Excel 保留 0、unmatched 0；gov 164 筆、Gov_Map 435 列、寫死 0、L1 25 列。
- `docs/plan/Tokenomics_governance_plan.md`（v0.3）不變。

**v5.11（chat 端，2026-10-02；詳見第 8h 節）**：第 0 層 Source（SRC_HW 60、SRC_DC 13、SRC_Model 51、SRC_Perf 40，共 164 筆）；模型頁 159 格改以公式連結 SRC；DB_Evidence 67 筆（含 E101–E147）；Decisions 90 項；Gov_Map 435 列；L1 第一批 25 列；Checks G 節；F14；藍字公式格 0。

**CC 第 11 輪：驗收與收尾皆通過（第 8i 節）**。重算時間改兩條門檻（增量 < 2 秒硬性、全簿 < 5 秒暫行至 v5.12）；公式內常數判定 11 格＋決策門檻 12 格，值都不變，v5.12 移到具名輸入格。

**下一步**
1. **（已完成 A 包，見上方與第 8k 節）新對話串**：v5.12 在新對話串建置（本串上下文已長；builder md 約 59 萬字元，建置需大量工具呼叫）。開頭讀本節與第 8j 節。
2. **Andy 待判斷**：審閱檔 `20261003_v5.11_待Andy_審閱檔.xlsx`（4 張表：標記變更 13 項、區間 19 項、CV1、原話 10 類）。含 Claude 自查 6 項（T01 PUE 與 G0-9 矛盾；T06／T11／T12 有可比來源 S30 卻降為 Assumed；R12 輪數下限 0.5；R17 χ 區間不對稱；R19 Hopper η_p 倍數應為 Derived）。不阻擋合併。
3. **chat 端 v5.13（原 v5.12 的 B–E 包；以 master 的 v5.12 為底稿；工作包見第 8j 節；A 包已於 v5.12 完成；B 包見第 8m 節、C 包見第 8n 節、D 包見第 8o 節，下一步 E 包）**：切片二（Price 44、Cap 21、Harness 15、Demand 9 筆候選；Training 來源需逐格核對是否已在 Model／Perf）；Cap_In、Har_In、Train_In、Tech_Registry 登錄 Gov_Map；Checks 外部比對移入 L1、C9:C10 改連 SRC_Price；Arch 21–23 改公式；Sources 更名 Sources_Legacy；**另加**：S30 一手來源補登 SRC_Perf（第 8i 節）、公式內常數 11 格與 Tech_Registry 主流門檻移出（第 8i 節）、Sens_Train 情境倍數統一寫法、Gov_Map 查找改寫（SRC 索引）、寫回 Andy 審閱結果；Andy 確認原話後第 2 節縮為決策 ID 清單。

**之後**（規劃書第 7 節，方案甲）：v5.12 工程基礎 → v5.13 切片二 → v5.14 Block 6 Alloc（第 8f 節設計不變；Answers 改寫入 L1）→ Stage 2 查核持續（優先序見審閱檔「Stage2_優先」與 Checks G 節 W2 的 31 格）→ OpenAI v0.6（Stage 3：原始數據取 Source、標準值取 L1、構件取 Interface，並承接 Q3）。

## 1. 定位與命題

- **目標**（Andy 2026-10-02）：Tokenomics 是「AI 技術 → AI 算力需求（投入／支出）→ AI 算力收入」這條供應鏈的事實基礎。所有已取得的原始訊息（未經計算、不是假設）集中在第 0 層 Source；Tokenomics 各頁與以後所有用到 AI 技術或算力數據的產業與個股模型，都從 Source 取用或推算；Source 沒有的就去找；所有新訊息（含 Andy 提供者）先登錄 DB_Evidence，與 Source 比較後擇優更新 Source。詳見第 11 節與 repo `docs/plan/Tokenomics_governance_plan.md`。
- **定位**：Tokenomics 是本 Project 的共同底座，也是下游 OpenAI、CRWV、Nebius 等模型唯一的事實來源。下游取數：原始數據取 Source（SRC_ID）、標準推算值取 L1（L1_）、推算構件取 Interface（IF_）；只自算公司特有的那一步（G8、G9）。
- **命題**：在目前主流技術下，1 GW（IT）算力用於訓練與推論的成本、產能、能力與理論營收是多少，並追蹤新一代技術對這些數字的影響。
- **營收的分工**：
  - 第 0 層只放「理論營收」，並明確標示為理想上限：SLO 下的產能 × 利用率 × 依層級的有效單價。
  - 實際營收（需求、市占、方案組合）在下游模型處理。

## 2. 已定案決策（v5.13 起只列決策 ID；全文見活頁簿 Decisions 頁）

> G11：Andy 2026-10-03 確認 Decisions 頁原話（v5.11 審閱檔「all OK」），本節依決議縮為 ID 清單（共 90 項）。決議全文、日期、Andy 原話、影響範圍與狀態一律以活頁簿 `Decisions` 頁為準；新增或修改決策時改 Decisions 頁（Excel 擁有，判斷類只在 chat 端改），本節只補 ID。
> 仍待 Andy 給值：J6 利用率（暫用 60%）、J15 生產折減（暫用 1.0）；依 K11／G0-11 維持暫用值，Andy 給值時以 A 級寫入 Source。

- **D**：D1 電力口徑；D2 世代；D3 VR 機架功率；D4 持有成本；D5 代表架構；D6 每架產出；D7 營收；D8 下游介面；D9 零組件成本；D10 WACC；D11 已移除
- **J**：J1 Astra KV；J2 VR 峰值；J3 SLO；J4 VR-eq；J5 任務組合；J6 利用率（暫用值）；J15 生產折減（暫用值）；J7 訓練精度；J8 Astra 預訓練規模；J9 RL 規模；J10 研發倍數；J11 用途 × 型態；J12 rollout 精度；J13 下游預設訓練世代；J14 主流判定
- **P**：P1 來源原則；P2 唯一事實來源；P3 Excel 優先（v5.7）；P4 Excel 修改分工（2026-10-01）；P5 檔案存放（2026-10-01）；P6 具名公式（Block 4 起）
- **K**：K1 單價基準（Block 4）；K2 單價前緣；K3 能力指標；K4 能力 → 單價；K5 商業壽命；K6 攤提口徑；K7 1 GW 參考配置；K8 營收範圍；K9 世代 × 單價；K10 快取儲存；K11 利用率與折減（暫用值）；K12 尖峰離峰；K13 中國廠商；K14 幣別
- **L**：L1 harness 表達；L2 成功率機制；L3 增強檔入基準；L4 harness 與每 GW 營收；L5 每成功任務成本；L6 非 GPU harness 成本；L7 harness 證據規則
- **M**：M0 機隊層級標示；M1 成功任務成本前緣可靠度下限
- **T**：T10 非同步 RL（T10）
- **G**：G1 Source 第 0 層；G2 新訊息流程；G3 來源等級；G4 比較規則；G5 舊資料保留；G6 A 級證偽；G7 SRC 分頁；G8 下游取數與邊界；G9 第 1 層 L1；G10 排序；G11 決策登錄；G12 資料範圍；G14 Stage 0 Gate 0；G13 多家獨立估計
- **A**：A1 基準年度（v5.14 建置；版號調整見交接第 0 節）；A2 改版計畫（v5.14 建置；版號調整見交接第 0 節）；A3 59% 校準（v5.14 建置；版號調整見交接第 0 節）；A4 服務 GW（v5.14 建置；版號調整見交接第 0 節）；A5 Q2 算力成本（v5.14 建置；版號調整見交接第 0 節）；A6 成長情境（v5.14 建置；版號調整見交接第 0 節）；A7 研發口徑（v5.14 建置；版號調整見交接第 0 節）；A8 實驗室選擇器（v5.14 建置；版號調整見交接第 0 節）
- **G0**：G0-1 遷移粒度；G0-2 Stage 1 數值不變與「值不等於來源」的格；G0-3 J3 Sol SLO 65 對來源 68；G0-4 能力指數版本；G0-5 公式內嵌原始數據納入 Stage 1 範圍；G0-6 Tech_Registry 採用數；G0-7 來源等級對應規則；G0-8 同指標的多家獨立估計（例：VR200 機架價格 MS 7.8、Bernstein 9.09）；G0-9 不遷入 Source 的 Sources 條目；G0-10 未登錄來源；G0-11 J6 利用率、生產折減的 Andy 值
- **CV**：CV1 Hopper 機架定義


## 3. 建模原則

- **由下而上的物理推導**：從 token、維度、層數、參數、bytes、FLOPs，經 MFU、roofline、延遲與批次，推到每架 M tok 與每 GW 的收入和成本。
  - 推理、訓練、harness 都用同一組物理量表達。
  - 實測數據只用來校準效率係數，不取代推導。
- **層級標籤**：每 token 成本一律依「世代 × 層級 × token 類型」列出，不輸出沒有層級的混合數字。
- **新技術追蹤**：新技術寫入 `Tech_Registry`，內容包括作用在哪個物理量、倍數、狀態、採用比例與證據標記。Looped transformer 只是其中一例。
- **Harness**：做成可開關的追蹤項。
  - 能力提升：預設 0，分短程與長程任務。
  - token 倍數：預設 1.0。
  - 情境值依證據填入。ARC-AGI-3 案例：GPT-6 Astra 在標準 harness 得 62.7%，換成 OpenAI 的 Provider Adapter 得 99.9%；Opus 5 原分數 30.2%，搭配 Strands harness 得 99.95%。
- **算力分類**：
  - 用途分三類：對外服務（再分付費與免費）、訓練（含其中的推論型運算，例如 rollout、合成資料、蒸餾教師、評測）、研發實驗。
  - 運算型態分兩類：推論型與反向傳播型。
  - 兩個軸交叉列出。坊間說的「推論」指的是對外服務。
- **後訓練占比**列為一級追蹤指標，同時看 FLOPs 比與 GPU 小時比。RL 的 MFU 約 0.01–0.10，預訓練約 0.15–0.35，所以以 GPU 小時計的比率會高於以 FLOPs 計的比率。
- **研發實驗倍數**：Epoch 指出最終訓練只占研發算力的少數，因此 Training 頁需要加上這個倍數。
- **來源獨立性**：校準錨點逐點標記量測平台；同一平台的多個點不算互相佐證。基準測試（InferenceX、MLPerf）都是固定長度、穩態負載，與生產環境的差距以「生產折減」處理。

## 4. 工作分工與流程（2026-10-04 改；CLAUDE.md 修訂五）

- **Andy 與 Claude（本 Project）**：判斷類事項的決定（輸入值、機制、來源與標記、假設與區間）；命題與驅動對照表；把決定寫成工作單（`docs/workorders/YYYYMMDD_vN.md`）；審查 CC 的報告與 diff。
- **Claude Code（repo：YinchenChang/Tokenomics）**：依工作單改 builder、產生新版 Excel 與 builder md、LibreOffice 重算、逐格比較、冪等、parity 全套、效能、網站、CHANGELOG、報告、PR。工作單沒寫清楚的地方列為「待 Project 判斷」，不自行決定。
- **審查重點**：報告的「預期變動 vs 實際變動」兩張表；chat 端只在表與 diff 對不上或數字可疑時做局部重現。
- **Excel 是事實來源**：Andy 能讀懂並掌握推導是最高優先，效率其次。
- **每個區塊的流程**：命題與驅動對照表 → Andy 確認 → 工作單 → CC 建置與驗收 → chat 端審查 → Andy 確認合併。

## 5. 區塊進度

| 區塊 | 內容 | 狀態 |
|---|---|---|
| 0 | 公式引擎、parity 測試、CI（CC） | 已完成（pycel 引擎、全格 parity、CI；CC 第 1–5 輪） |
| 1 | 機架規格、DC 成本、Interface 前段 | 已交付（v5.0） |
| 2 | 模型架構、任務制工作負載（含推理與 agent）、服務設定、校準、能量閉合、Unit_Cost | 已交付 v5.4；CC 同步於 repo PR #3、#4（PR #4 合併後結束） |
| 3 | Tech_Registry、Train_In、Perf_Batch、Training、Sens_Train | 已交付 v5.7；v5.5、v5.6 由 CC 第 4、5 輪同步於 PR #5；v5.7 由 CC 第 6 輪於 PR #6（已合併） |
| 4 | Cap_In、Capability、Price_Frontier、Cache_Store、Fleet_1GW、Amortize、Theory_Rev、Sens_Rev | **已交付 `20261001_Tokenomics_v5.8.xlsx`**；CC 第 7 輪已同步並合併（PR #7，e59bf4f；見第 8c 節） |
| 5 | Harness 參數化（Har_In、Harness、Sens_Har；改 Workload、Tech_Registry T12、Amortize）；K6 下游預設 | v5.9 已交付並由 CC 第 8 輪同步（PR #8）；M1 (b) 於 v5.10 實作（第 8e 節），CC 第 9 輪同步並合併（PR #9） |
| 治理 Stage 0 | 唯讀盤點：輸入分類、依賴圖、敏感度排序；Sources 拆解為候選 SRC 紀錄 | 已完成（CC 第 10 輪，PR #10 已合併；Gate 0 全部核准） |
| 治理 Stage 1 | Source 第 0 層上線（數值不變）、DB_Evidence 升級、Decisions、L1、治理 Checks | **切片一已交付 `20261002_Tokenomics_v5.11.xlsx`**（第 8h 節），待 CC 第 11 輪同步與 Gate 1 驗收；切片二待建 v5.13（v5.12 為工程基礎）|
| 6 | Alloc（研發／服務的算力與算力成本占比；策略變數 N、k；需求 D）＋Answers（改寫入 L1，G9） | **設計已定案（第 8f 節）**；待建 v5.14（建在 Source 與 L1 之上；原 v5.13） |
| 之後 | OpenAI v0.6（治理 Stage 3 第一個下游）：原始數據取 Source、標準值取 L1、構件取 Interface；承接 Q3（研發占整體成本，含非 GPU 成本）；之後 CRWV 改接 | 待辦 |

## 6. Block 1 結論與未結事項

- **VR200 基準（每 GW IT）**：
  - 機架數 4,052（v4 為 5,263）。
  - 資本支出 $47.6B（v4 為 $43.2B）。
  - 經濟口徑年持有成本 $12.05B，每 GPU 小時 $4.72。
- **每 GW 持有成本幾乎不隨世代改變**：Hopper 到 VR200 約 $9–13B/年。各世代的經濟差異幾乎全看每 GW 產出，也就是 Block 2 的重心。
- **成本結構**：資本回收占 77–81%，電費只占 4–7%。
- **敏感度**：
  - 資本支出受機架價格影響最大（擺幅 $10.7B），其次是配電設計功率（$7.3B）。
  - 持有成本受 IT 折舊年限影響最大（擺幅 $3.8B/年），其次是機架價格（$2.8B/年）。
- **交叉檢查**：
  - GB200 每 GPU 小時 $2.08，SemiAnalysis 為 $2.21。
  - GB300 每 GPU 小時 $2.99，SemiAnalysis 為 $2.65。
  - VR200 每 GW 資本支出略低於黃仁勳所說的 $50–60B。
- **未結事項**：
  1. VR200 報價是否已含網路設備（Sources 頁 S11）；若含，網路成本會重複計算。
  2. 所有來源都待 Andy 查核。
  3. Rubin Ultra 為推估，不進基準比較。

## 7. Block 2 結論與未結事項（v5.2）

**推導結構**
- prefill：每 GPU tok/s ＝ η_p × 峰值 ÷ FLOPs/token（算力受限）。
- decode：每步時間 ＝ 固定延遲（權重讀取 ＋ 每層延遲 ×（層數＋MTP 草稿數））＋ B × 每序列時間；SLO 下解出批次 B*，再受 HBM 容量限制。封閉解，無迭代。
- 每架產出以參考任務（ISL/OSL）按工作量配 P:D GPU。

**校準（Calib）**
- 交接原錨點 GB300 6,182／GB200 2,189 tok/s/GPU @27 屬舊軟體（vLLM、無 MTP、2026-05-22），不再作擬合用，改列驗證。
- 擬合：GB300 最新前緣兩點（72 tok/s → 9,384；130 tok/s → 3,474，S22）聯立 → η_d ≈ 3.6%、每層延遲 ≈ 160 µs（η_p 0.30；η_p 0.15–0.45 時 η_d 3.2–5.6%、延遲 156–175 µs）。
- 樣本外：GB300 SGLang＋MTP 50 tok/s（11,200，S21）模型 ÷ 實測 0.99；GB200 110 tok/s 1.01；GB300 110 tok/s 0.88。舊軟體點 2.2×／4.1×（預期 >1）。
- VR200、GB200 沿用 GB300 的 η_d 與延遲 [Analogy]；Hopper η_d ×3、延遲 ×1.5 [Analogy／Assumed]。

**第二來源（Calib H 節）**
- 七個校準點全部來自 InferenceX 單一平台（S21 的 SGLang 部落格也是轉述 InferenceX 資料），不構成互相佐證。
- 第二來源用 MLPerf Inference DeepSeek-R1（MLCommons 稽核；NVIDIA 提交，利害關係方），以同一套係數推算 R1（ISL 800／OSL 3,880）：
  - 模型 ÷ MLPerf：GB300 interactive 0.71、VR200 interactive 0.70、GB200 interactive 0.50、GB300 server 0.63。本模型低於 MLPerf，即 InferenceX 校準未比 MLPerf 樂觀。
  - VR200 ÷ GB300（interactive）：模型 2.52 對 MLPerf v6.1 的 2.57。VR 沿用 GB300 效率係數這個最大的 Analogy 獲得支持（MLPerf VR 為 NVIDIA 預覽類提交）。
  - 衝突：GB300 ÷ GB200，InferenceX 1.7–2.8、MLPerf 約 1.05、模型 1.5。GB200 的 VR-eq 視為區間。
- 兩類基準都偏向最佳情境；非基準的生產證據只有 DeepSeek 自揭（H800，待查），也高於本模型的 Hopper 推算。
- 生產折減 0.7 的影響：GB300 Sol decode $/M 0.557 → 0.987，VR200 0.323 → 0.552（固定延遲占掉 SLO 預算，折減被放大）。

**基準結果（經濟口徑、基準成本、100% 利用率；Sol）**
- decode $/M：GB300 0.557、VR200 0.323、GB200 0.581、Hopper 2.60、Rubin Ultra 0.273。新鮮 prefill $/M 約 0.017–0.026（Hopper 0.20）；快取命中只計載入，約 0。
- VR200 ÷ GB300 每 GW 產出 1.58（損益兩平＝持有成本比 0.95）；decode 成本比 0.58。
- VR-eq（Sol）：Hopper 0.09、GB200 0.45、GB300 0.63、Rubin Ultra 1.62。Astra 層級 GB300 只有 0.47。
- 15 欄全部為「SLO（算力項）」綁定；HBM 容量在目前軟體效率下不綁定，因此 Astra KV 情境（J1）不改變產出，只改變 KV 占用（VR 上 3%／11%／39%）。
- 能量：物理下限功率只占機架平均用電 5–7%，閉合成立但無法驗證 Inputs!E10（0.8）；GB300 IT 平均 1.52 kW/GPU 對 InferenceX provisioned 約 2.12 kW/GPU。

**敏感度（Sens_Perf，VR200 ÷ GB300 每 GW 產出）**
- 最大驅動：VR η_d 倍數（×0.5 → 0.92，翻轉結論；×1.5 → 2.06）、VR 峰值 50 PF（2.25）、SLO（40 → 1.48；100 → 1.86）、VR 每層延遲（×1.5 → 1.35）。

**未結事項**
1. VR200 無實測；η_d 沿用 GB300 是全模型最大的 Analogy。InferenceX 已有 VR200 頁面但尚無同點資料，出現後第一優先重校。
2. J6 基準利用率（暫 60%）與生產折減（暫 1.0）待 Andy 給值。
3. S23／S24 工作負載口徑待查；S28、S29、S30 為模型內建知識，待查核；S32（MLPerf v6.1 VR 數字）待以 MLCommons 原始結果核對。
4. 快取命中未計儲存成本（HBM／DRAM／SSD 保留 KV 的容量時間成本），Block 4 定價時需處理。
5. Workload 的每任務成本取各層級參考上下文的 decode 成本，長程 coding agent（平均上下文 49K）略低估。

**CC 同步（repo PR #3）**
- 第 1 輪（v5.2）：引擎改用 pycel（formulas 套件全簿重算 5.9 秒，未達 2 秒門檻）；8,427 格在基準與 5 個情境下與 LibreOffice 逐格一致（不符 0 格）；舊 v4 手抄程式移入 legacy/；網站新增 Block 2 頁與 Calib 驗證表。
- CC 回饋、v5.3 已處理：Calib H 節補量測平台列；新增顯示用具名範圍 IF_HdrGen／IF_HdrCost、DRV_*（Perf 推導鏈 17 列）、CAL_*（校準與驗證表）；decode 標示「含思考 token」；Checks 參照數字改為儲存格引用。
- 第 2 輪（v5.3）：8,427 格、5 情境不符 0 格；67 個具名範圍通過；網站 Block 2 頁加推導鏈，驗證表與表頭改讀具名範圍，不再以欄 A 標籤定位。第 1 輪 CI 4 次全綠。
- v5.4 依第 2 輪回饋：Calib 驗證表補 CAL_F_／CAL_H_ 的世代、軟體、速度、實測值、模型值、口徑（F 節為總 token、H 節為輸出 token），F 節點位標籤改為「世代｜用途｜速度」；具名範圍 78 個、公式 8,438 格。DRV_CostDec 維持只有基準成本情境；網站推導鏈的成本列若要跟隨成本情境，改讀 IF_CostDec_*。
- 第 3 輪（v5.4）：PR #3 已於第 2 輪後合併（afb22c9），第 3 輪改開 PR #4。8,438 格、5 情境不符 0 格；78 個具名範圍通過；驗證表拆成 F（InferenceX，總 token）與 H（MLPerf，輸出 token）兩張，兩節比值不可並列比較；推導鏈成本列改讀 IF_CostDec_*。master 上 v5.4 上傳時的 2 次紅燈為測試期望值仍是 v5.3（公式數、具名範圍數），PR #4 更新後恢復。
- 延到下次升版（v5.5，不影響數值；builder 已改好）：README 版本文字、Calib H 節速度與實測列補單位、移除已無用途的 DRV_CostDec 具名範圍（Perf 速覽列保留）。
- 讀取回報：Gmail 搜尋只回傳 thread 最舊 5 封，第 2 輪起改讀 repo 的 docs/reports/ 原檔（repo 公開，以 commit SHA 取 raw 檔）；thread 未滿 5 封時可直接讀 PR comment（get_message）。
- 第 5 輪（v5.6，PR #5 同分支，2026-10-01）：v5.5 以 git mv 移入 model/archive/；16,251 格在基準與 7 個情境下不符 0 格；142 個具名範圍通過；Block 1、2 與 v5.5 逐格一致，34 個變動名稱全在 Block 3；網站 Tech_Registry 改讀 TR_、預設訓練世代改讀 IF_TrainGen*。CC 建議為世代名稱格補具名範圍（v5.7 已補）。master 紅燈原因推測為 model/ 同時有兩版（PR 整理後應恢復）。
- 第 4 輪（v5.5，PR #5，2026-10-01）：16,245 格在基準與 7 個情境（新增 Tech_Registry!O11:O13＝1、Train_In!C13＝4.4）下不符 0 格；117 個具名範圍通過；pycel 支援 EXP(SUMPRODUCT(LN)) 與 SUMPRODUCT 條件加總，全簿重算 0.1–0.4 秒；網站新增 Block 3 頁。CC 提出：Hopper 差異 0.0506% 略超 0.05%（待 Andy 確認）；Tech_Registry 與 J13 缺具名範圍（v5.6 已補）。CI 結果與合併待確認。
- 決定：v4 的「逐步能量模型」不恢復（違反 Excel 為唯一事實來源），由 Perf J 節能量閉合取代。
- 管道：GitHub 通知已恢復進收件匣；搜尋 `from:notifications@github.com Tokenomics`。

## 8. Block 3 結論與未結事項（v5.6）

**推導結構**
- 預訓練：每 token 訓練 FLOPs＝3 ×（2 × 啟用參數＋注意力 FLOPs × 被注意 token）；預訓練期間 dense 注意力（V4 做法），長上下文延伸、SFT、RL trainer 用 Arch 的稀疏公式。GPU 小時＝FLOPs ÷（FP8 訓練峰值 × MFU × goodput）。
- 推論型訓練運算（RL rollout、蒸餾學生 rollout 與教師評分、合成資料、評測）以 Perf_Batch 計價：與 Perf 同一套 write_perf 公式，只把 SLO 換成批次速度下限（20 tok/s）與 rollout 參考任務（ISL 4K/8K/16K、OSL 8K/16K/32K）。
- RL 有效 MFU、後訓練占比（FLOPs 與 GPU 小時兩種口徑）、推論型占比皆為推導值。
- 研發計畫＝最終訓練 GPU 小時 × 研發倍數；家族合計列於 Training L 節。
- Tech_Registry：每列＝技術 × 作用物理量；有效倍數＝1＋開關 × 採用比例 ×（倍數−1），已在基準者恆為 1。掛鉤：H_ETAD、H_TL、H_FLOP、H_KV、H_WB（Perf、Perf_Batch）；H_TPK、H_MFU、H_TOK、H_ROLL（Training）；H_CAP、H_HAR 為 Block 4、5 占位。全部開關為 0 時 Block 2 與 v5.4 相同。

**基準結果（v5.6；經濟口徑、基準成本；VR200 預設，GB300 並列）**

| 層級 | 最終訓練 GPU 小時 | 最終訓練 $ | 後訓練占比 FLOPs／GPU 小時 | RL 有效 MFU | 研發計畫 $ | 研發計畫占 1 GW 年 |
|---|---|---|---|---|---|---|
| Luna VR200 | 0.61M | $2.9M | 13.0%／25.8% | 8.6% | $23M | 0.19% |
| Sol VR200 | 1.85M | $8.7M | 12.7%／25.6% | 8.4% | $70M | 0.58% |
| Astra VR200 | 11.7M | $55M | 26.9%／48.3% | 7.9% | $441M | 3.7% |
| Astra GB300 | 34.9M | $104M | 26.9%／46.0% | 9.7% | $834M | 6.6% |

- 家族（三層級）研發計畫：VR200 約 $533M、1 GW 年的 4.4%；GB300 約 $1.0B、8.0%。
- 推論型運算占最終訓練：VR200 Sol 32%、Astra 28%。
- rollout decode 有效 MFU 對 NVFP4 峰值約 2%，受 Block 2 校準的 η_d（約 3.6%）封頂：批次再大也無法超過。RL 有效 MFU 5.9–10.7%（FP8 分母）。
- v5.6 對 v5.5：非同步 RL 併入基準後，VR200 的 GPU 小時與成本不變（J9 (a)），同樣的 GPU 小時完成約 18–20% 更多 rollout；後訓練 FLOPs 占比上升（Astra 23.6% → 26.9%），RL 有效 MFU 上升（Astra 6.6% → 7.9%）。GB300 未校準，研發計畫 +0.6%。

**敏感度（Sens_Train，VR200 研發計畫 ÷ 基準；Sol／Astra）**
- RL rollout token × 3：1.36／1.89；× 0.3：0.88／0.69。
- 預訓練 MFU 0.15：1.45／1.48；0.40：0.75／0.73。
- 預訓練 token × 1.67：1.37／1.31；× 0.5：0.73／0.77。
- 研發倍數 10.4：1.30；4.4：0.55。
- rollout 精度 FP8：1.09／1.22。NVFP4 訓練峰值：0.66／0.64。
- rollout 效率 0.6（rollout token 不變）：1.04／1.09；0.95：0.99／0.98。
- 合成資料 × 3：1.47／1.11；× 0：0.76／0.94（Sol 對合成資料敏感：由 Astra 生成，單位成本高）。goodput 0.8：1.08／1.09。

**檢查**
- DeepSeek V3 推導 MFU（H800、FP8 分母）19.7%，本模型 Hopper 採用 20%。
- 前沿錨點中值 5e26 在 Astra 架構下需約 438T token，基準為 60T：Astra 的啟用參數或 token 假設可能偏低，是 J8 的主要未結點。
- Tech_Registry 一致性欄全部「一致」（T10 已處理）。

**v5.5、v5.6 其他修正**
- Spec_Rack：Hopper 峰值由 0.989（誤為 BF16）更正為 FP8 1.979 PF；Calib 的 Hopper η_d 倍數 3→1.5、η_p 倍數 1→0.5，使 Hopper 產出幾乎不變（CC 實測差異 0.0505–0.0506%，來自倍數取整；建議接受，待 Andy 確認）；Hopper 能量閉合比因 pJ/FLOP 更正由 6.5% 降為 3.7%。S30 口徑查核後重推。
- 已含 v5.4 延後的三項：README 版本、Calib H 節單位、移除 DRV_CostDec。
- v5.6 依 CC 第 4 輪：Tech_Registry 補顯示用具名範圍 TR_（20 欄＋掛鉤 3 個，共 23 個）；J13 改為數值索引並補 IF_TrainGenDefault（4＝VR200）、IF_TrainGenAlt（3＝GB300），可供下游連結。
- v5.6 來源新增 S45–S49（非同步 RL）。
- v5.7：Excel 優先改制（builder 新增 preserve.py：重建前讀取 770 個藍字輸入、重建後寫回；數值與 v5.6 逐格一致）；新增 DB_Evidence 證據登錄表（種子 9 筆：E001–E009）；依 CC 第 5 輪補 IF_TrainGenDefaultName、IF_TrainGenAltName（世代名稱格）。

**未結事項**
1. J8 差距（見檢查）；Astra 啟用參數與 token 待 Block 4 能力錨點一併處理。
2. RL rollout 量、研發倍數、Astra token、合成資料量皆為 Analogy／Assumed；以 Sens_Train 讀。
3. 訓練 MFU 的第二來源：MLPerf Training（MLCommons 稽核）GB200／GB300 Llama 3.1 405B 結果尚未查核入表。
4. S37（Llama 3）、S44（V3 GPU 小時）、S30 為模型內建知識，待查核。
5. Perf 掛鉤作用於全部世代與層級；若需只作用於特定世代的技術，需加世代遮罩欄。
6. rollout 牆鐘時間與叢集規模未建模（只算 GPU 小時）。


## 8a. Block 4 結論與未結事項（v5.8）

**推導結構**
- 理論營收（理想上限）＝每 GW 產出 × 利用率 × 參考請求混合有效單價；有效單價＝OpenAI 牌價 ×（1−折扣 20%）× 能力單價倍數（基準 1）。思考 token 依輸出價計費。參考請求混合用 Serving 的 ISL／OSL（三層級皆 8:1）與快取命中 χ 55%。
- 單價前緣（K2 (i)）：Cap_In F 節 13 個候選（OpenAI 3、Anthropic 3、中國 7），能力指數 ≥ 層級門檻（GPT-6 Luna 37／Sol 48／Astra 53）者取混合單價最低。
- 快取儲存＝KV bytes × 儲存層 $/GB-hr × 保留時間 ÷ 命中次數。
- 攤提：自下而上＝層級研發計畫成本 ÷ 1 GW 參考機隊在商業壽命內服務的該層級 token（＝回本所需溢價）；由上而下＝X ÷（1−X）× 服務成本，X＝訓練＋研發占機隊（59%）。
- 新公式以 B4_ 具名範圍引用（38 個）；下游連結 Interface D 節 IF_ 名稱（新增 46 個）。

**基準結果（經濟口徑、基準成本、利用率 60%）**

| 項目 | Hopper | GB200 | GB300 | VR200 |
|---|---|---|---|---|
| 理論營收 Luna／Sol／Astra（$B／GW 年） | 3.6／20.8／19.0 | 18.0／102／99 | 25.6／146／117 | 37.8／230／249 |
| ÷ 持有成本：Luna／Sol／Astra | 0.36／2.1／1.9 | 1.9／11.0／10.7 | 2.0／11.5／9.3 | 3.1／19.1／20.7 |
| 1 GW 參考機隊付費營收（$B） | 4.1 | 20.7 | 26.3 | 49.1 |
| 機隊營收 ÷ 持有成本 | 0.40 | 2.23 | 2.08 | 4.07 |
| 隱含每 GW 年家族研發計畫數 | 3.0 | 7.0 | 7.4 | 13.3 |

- OpenAI 2025 對帳：Hopper 60%／GB200 40% 加權的機隊付費營收 $10.7B/GW 年，對實際 $13.07B ÷ 平均 1.25 GW＝$10.5B（GW 口徑未明）。量級閉合。
- 有效混合單價（OpenAI）：Luna $0.080、Sol $1.61、Astra $8.04／M。前緣：Luna、Sol 為 OpenAI 本身；Astra 為 Claude Fable 5.1（OpenAI 溢價 1.04，全來自 Fable 5.1 快取讀取 $0.25，單一二手來源待核）。
- 中國廠商：只在 Luna 層級合格（4 家；最低 GLM-5.3-Flash，混合單價為 GPT-6 Luna 的 1.30 倍）；Sol、Astra 層級無合格者（最高 GLM-5.3 指數 45 < 48）。Andy 的「集中在低端」在能力軸上成立，但低端價格前緣由 OpenAI 自己壓出。
- DeepSeek 價 ÷ 本模型 Hopper 同架構成本：V4-Pro 尖峰÷基準利用率 0.91、離峰÷100% 0.76；V4.1-Flash 0.96。中國廠商定價接近 Hopper 級物理成本。
- 層級價差 vs 成本差：Luna→Sol 單價 20 倍、decode 成本 3.2 倍；Sol→Astra 單價 5 倍、成本 5.1 倍。Sol 層級的溢價最大。
- 攤提（VR200）：自下而上 Luna $0.0003、Sol $0.0038、Astra $0.156／M；由上而下 $0.031、$0.102、$0.497；兩者相差 3–100 倍。回本所需溢價占觀測層級價差：Sol 0.25%、Astra 2.4%。
- 快取儲存（DRAM、5 分鐘、5 次）：可忽略（Astra $0.00027／M）；改 HBM 上限約 57 倍。
- 理論毛利率（OpenAI 單價、由上而下全成本，VR200）：Luna 34%、Sol 89%、Astra 90%；Hopper × Luna 為負。

**敏感度（Sens_Rev，VR200 × Sol）**：利用率 40／80% → 0.67／1.33 倍；折扣 10／30% → 1.13／0.88；χ 30／75% → 1.20／0.84；服務占機隊 30／60%（機隊）→ 0.73／1.46；免費占服務 35／60%（機隊）→ 1.20／0.74；ε 0.5 且有效算力 ×7 → 2.65（K4 (a) 的量級，不入基準）。

**未結事項**
1. K6：已決定下游預設採 (c)（見第 2 節、第 8b 節）。自下而上與由上而下總額相差約 9 倍（VR200：$0.68B 對 $6.10B／GW 年）。
2. 隱含每 GW 年 13 個家族研發計畫（VR200）遠高於實際 1–3：與 J8（Astra 算力約低 5 倍）同源，待以能力錨點重估 Astra 規模。
3. 能力指數缺：Claude Opus 5.5（$4／$20，Anthropic 自稱達 Fable 5.1 水準；若 ≥ 53，Astra 前緣下移）、Kimi K3、MiniMax M3。METR 檢查未入表。Google 未列入候選。
4. 二手價格待以官方頁核對：Anthropic（含 Fable 5.1 快取 $0.25）、Moonshot、Alibaba（$2／$6 與 $2.5／$7.5 附五折衝突）、MiniMax。
5. Artificial Analysis 指數一週改版三次；跨版本不可比，更新時須整欄同版本替換。
6. OpenAI 2025 機隊配置以支出比代 GW 比（Derived）；免費 46% 與服務 41% 皆為 Interested-party。

## 8b. Block 5 命題與驅動對照表（2026-10-01 定案；v5.9 已建）

**命題**：Harness 不是新的物理量，而是作用在標準任務上的一組參數變換（輪數、思考保留 ρ、歷史壓縮、快取命中、子代理數、狀態保留時間）加上任務成功率。第 0 層輸出「每個成功任務的 token 與成本」，依世代 × 層級 × 任務 × harness 檔案列出；每 GW 理論營收上限不變（L4）。

**v5.8 現況（建表前提）**
- Workload 列 13 為單一標量，經列 21（(1＋m)× harness）同乘三類 token，無法改變 token 組合。
- Workload 只被 Theory_Rev C 節（每任務營收，50 格）引用；Theory_Rev A、B 節用 Serving 參考請求，不受 Workload 影響。
- Tech_Registry T12／H_HAR 無任何公式讀取。Workload 列 10 ρ 全為 0。
- Workload 列 28 的倍數（單代理 9.2、多代理 36.8，相對一般聊天）高於列 30 的 Anthropic 參照（4、15）約 2.3–2.5 倍：Block 2 既有落差，只列出，Har_In 標準檔校準時處理。

**證據（建表時以原頁核對）**
- ARC-AGI-3（ARC Prize 自測，經二手轉述）：標準 harness 最高推理 62.7%、$26,098；Provider Adapter 高推理 99.9%、$18,817（另一來源 $19,302，衝突）；同為最高推理 98.6%、$17,332；耗時約快 3.66 倍；「少用 49% token」適用範圍不明。Adapter 機制＝保留不透明推理狀態＋壓縮上下文，使用公開 API 功能。
- 同檔比較：成本 0.664 倍、成功率 1.57 倍 → 每成功任務成本 R ≈ 0.42；兩平點 m* ＝ 1.57。
- Opus 5：30.2% → 全部通關（交接原寫 Strands，報導寫 Nvidia 所建 harness，待核）；成本未找到。
- Anthropic 多代理：token 約單代理 4 倍、聊天 15 倍；評測分數較單代理高 90.2%（內建知識，待查核；非成功率）→ R ≈ 2.0。harness 的 token 倍數區間須同時涵蓋 <1 與 >1（約 0.5–15）。

**會計恆等式與下游含義**
- 每 GW 營收＝每 GW token × 利用率 × 單價；harness 改變每任務 token，不改變每 GW token，故第 0 層 harness 不是營收槓桿，而是每成功任務成本、每任務 token 需求與層級替代的槓桿。
- 示例（Derived）：R＝0.42、任務價格彈性 −0.7（借用 OpenAI v0.5，Assumed）→ 任務數 1.83 倍、token 營收約 0.77 倍。harness 效率對按 token 計價營收是通縮的，除非彈性絕對值 >1；於下游驗證。

**驅動對照表**

| 工作表 | 輸入（藍字） | 推導量 | 方向 | 下游 |
|---|---|---|---|---|
| Har_In（新） | A：harness 檔案（標準中立／供應商原生增強／多代理編排）× 5 任務：輪數倍數、ρ、每輪思考倍數、歷史壓縮比、χ、m、狀態保留時間、供應商專屬；B：各層級 50% 時間範圍、斜率 β、各任務長度、時間範圍倍數（短程／長程）、成功率覆寫欄；C：證據點 | — | → Workload、Harness、Cache_Store | — |
| Tech_Registry T12（改） | 開關、採用比例（既有） | 混合權重 w；作用位置改為 Har_In 檔案 | → Workload | 開關 0 時全簿與 v5.8 逐格一致 |
| Workload（改） | 列 13 改讀「標準檔＋w ×（增強檔−標準檔）」；新增壓縮比列 | 每任務各類 token | → Harness、Theory_Rev C | 不影響 Block 1–4 |
| Cache_Store（改） | 狀態保留時間改讀 Har_In | 跨輪保留推理狀態的儲存成本 | → Harness | ARC 任務約 40 分鐘，遠超 5 分鐘 TTL |
| Harness（新） | — | 每次嘗試 token／成本（接 Unit_Cost）、成功率 p、每成功任務成本／token／營收、R、成功任務成本前緣（達目標 p 的最便宜層級＋檔案） | → Interface E、Sens_Har | 層級替代 |
| Amortize（改） | K6 方法選擇 | 新增 (c)、(d) 與 IF_AmortDefault_* | → Interface D | OpenAI v0.6 |
| Sens_Har（新） | — | R 與每成功任務成本 tornado | — | — |
| Checks | ARC 重現 | adapter 檔重算 R 對觀測 0.42（只看方向） | — | — |

**K6 各方案數值（VR200、基準成本、利用率 60%；$/M；全成本毛利率 Luna／Sol／Astra）**

| 方案 | 總額 $B／GW 年 | Luna | Sol | Astra | 毛利率 |
|---|---|---|---|---|---|
| (a) 自下而上 | 0.68 | 0.0003 | 0.0038 | 0.156 | 72%／95%／94% |
| (b) 由上而下 × 服務成本 | 6.10 | 0.031 | 0.102 | 0.497 | 34%／89%／90% |
| **(c) 由上而下總額 × 自下而上權重（預設）** | 6.10 | 0.0028 | 0.034 | 1.40 | 69%／93%／78% |
| (d) 由上而下總額 × 營收權重 | 6.10 | 各層級扣營收 12.4% | 同左 | 同左 | 服務毛利率各減 12.4 個百分點 |

- 縮放倍數 8.97 與第 8a 節未結 2（隱含 13 個研發計畫／GW 年）同源；若 J8 低估集中於 Astra，(c) 對 Astra 仍偏低。

**工程約定**：新頁 Har_In、Harness、Sens_Har；新公式以 B5_ 具名範圍引用；下游接口在 Interface E 節（IF_）；開關 0 時 Block 1–4 與 v5.8 逐格一致，作為 CC parity 情境；建表時查 METR 各層級時間範圍與斜率、ARC Prize 原頁。

**未結事項**
1. METR 時間範圍與斜率未檢索；5 個 Workload 任務的任務長度為新增 Assumed。
2. ARC 金額衝突、Opus 5 harness 歸屬、Anthropic 90.2% 待查核。
3. 延後：harness 用於 RL rollout（缺 rollout harness token 結構）、非 GPU 成本（L6）。

## 8c. CC 第 7 輪（v5.8）結果與 v5.9 待修項

**結果**：builder 以 v5.7 與 v5.8 為底稿重建皆與 v5.8 逐格一致（24,093 格，不符 0；restore_log 未對應 0）；公式 18,596、具名範圍 228（IF_ 115：IF_Hdr 2、下游 113；B4_ 38）；parity 109 項全過，基準與 11 個情境不符 0 格；全簿重算 0.33 秒，首次載入約 47 秒（v5.7 為 10–15 秒）；網站新增 Block 4 頁，K6 兩種攤提並排、未選預設。pycel 支援 MATCH 等新函數，無旁路；engine 補 pycel 與 openpyxl 3.1 具名範圍相容轉接（不涉計算）。情境 i（Opus 5.5 指數＝53）使 Astra 前緣改為 Opus 5.5、前緣混合單價 7.742 → 3.136 $/M。

**v5.9 待修項（Excel 端；v5.9 已全部處理）**
1. SLO 不可達時 Block 4 出錯：某世代 Astra 產出為 0 時，Fleet_1GW!C18 等以 0 為分母，連鎖至 Amortize、Theory_Rev、Interface（IF_FullCost_*、IF_AmortTD_*）與 Checks!B43（情境 b：Interface 27 格、全簿 145 格；情境 f：60／339 格；基準無錯）。比照 Block 2 回傳「SLO 不可達」或以 IF 保護分母。
2. Cap_In F 節加「中國廠商」旗標欄與具名範圍（網站目前以國別字串判斷）。
3. B4_Chi 易誤讀為「中國」，可改名（B4_ 不供下游，改名不影響下游）。
4. K6 預設 (c)、(d) 與 IF_AmortDefault_*（第 8b 節），網站改顯示預設。
5. 機隊兩列（IF_RevGWFleet、IF_RevGWFleetFront）的層級標示：Andy 選 (b)，v5.9 已加各層級貢獻列。

**CC 提出的事項與處理**
- 兩邊皆為錯誤值、僅錯誤代碼不同（引擎 #VALUE!、LibreOffice #DIV/0!，兩錯相加時回傳哪一個）：同意本輪單獨列帳、不計入不符；v5.9 消除待修項 1 後，改回「此類格數須為 0」的嚴格標準（工程判斷，2026-10-01）。
- 首次載入 47 秒：可接受（網站有快取；選型標準是單次重算 < 2 秒，已達成）；Block 5 後再量。
- 機隊兩列層級標示：Andy 選 (b)（2026-10-01）。

## 8d. Block 5 結論與未結事項（v5.9）

**建置**：新頁 Har_In、Harness、Sens_Har；Workload 改為參數組（列 5–14 標準檔、列 16–23 有效參數＝標準＋w ×（選定檔案−標準）、導出列 26–39、每任務成本列 43–48）；Tech_Registry T12 開關 × 採用比例＝w（基準 0）。公式 20,686 格、LibreOffice 重算零錯誤；具名範圍 294（IF_ 157，下游 154；B4_ 39；B5_ 23）。v5.8 的 227 個既有名稱（B4_Chi 改名 B4_CacheHit）逐格同值；Block 1–3 各頁逐格一致。情境 b（折減 0.7）、f（Tech_Registry O11:O13＝1）、w＝1、w＝1 且檔案 3 皆零錯誤（v5.8 b、f 分別 145、339 格）。冪等 27,190 格不符 0。

**參數**：檔案 2（供應商原生增強）在代理任務：輪數 × 0.7、ρ 1、每輪思考 × 0.8、歷史保留比 0.7、狀態保留 0.67 hr、時間範圍倍數 短程 1.2／長程 2（皆 Assumed，區間在 Har_In D 節）；檔案 3（多代理）：單代理與 coding 子代理 +3、時間範圍 1.2／1.5。成功率：50% 時間範圍 Luna 1.5（0.5–4）、Sol 8（4–12）、Astra 16（11–40）小時 [Analogy：METR GPT-5.6 Sol 11.3、Mythos Preview 17.4]；β 0.75（0.65–1.0）[Derived：METR 50%／80% 比，四模型平均 0.80]；任務長度 0.02／0.1／0.5／2／8 小時 [Assumed]。

**基準結果（VR200、經濟、基準成本、利用率 60%；Coding agent（長程））**

| 層級 | p 標準 | p 檔案 2 | 每成功任務成本（現行） | 每成功任務營收（OpenAI） | R（檔案 2 ÷ 標準） |
|---|---|---|---|---|---|
| Luna | 22% | 32% | $0.030 | $0.17 | 0.41 |
| Sol | 50% | 63% | $0.044 | $1.53 | 0.48 |
| Astra | 63% | 74% | $0.165 | $6.08 | 0.52 |

- 檔案 2 總 token ÷ 標準：Coding 0.49（ARC「少用約 49%」0.51）、單代理與多代理 0.59。ARC 重現 R：模型 0.52 對觀測 0.42（同方向）。
- Sens_Har：Astra R 0.36–0.77、Sol 0.33–0.71、Luna 0.29–0.62；最大驅動為輪數倍數（0.5–1.0），其次時間範圍倍數；全部 < 1，即檔案 2 在區間內一律降低每成功任務成本（主要來自 token 減少，成功率次之）。
- ARC 的成功率提升若用 METR 型曲線換算，時間範圍倍數約 146 倍（β 0.75）：ARC 無法校準時間範圍倍數，只作方向檢查（Checks）。
- 成功任務成本前緣（Harness H 節）：所有任務皆為 Luna（Coding：Luna｜檔案 2，$0.0125）。原因：Luna 每次嘗試成本約 Astra 的 1／60，即使 p 22–32% 仍最便宜；METR 型曲線（β 0.75）尾部平緩，使低層級長任務 p 不趨近 0。此前緣未設可靠度下限，見未結 1。
- K6（VR200）：(c) 預設 Luna $0.0028、Sol $0.034、Astra $1.40／M；縮放 8.97 倍；(d) 攤提占付費營收 12.4%。理論毛利率（OpenAI 單價）不含攤提 73%／96%／96%，K6 預設全成本 69%／93%／78%。機隊付費營收 $49.1B／GW 年＝Luna 0.81＋Sol 18.11＋Astra 30.19。

**未結事項**
1. ~~成功任務成本前緣的可靠度下限~~：**Andy 2026-10-02 選 (b)**，v5.10 已實作（第 8e 節）。(c) 不可偵測失敗成本未做，仍可作為 L5 的敏感度。
2. Tech_Registry T12 的公開採用實驗室數（J14）未評估，仍為 0；L3 已決定不入基準。
3. METR 原頁、ARC Prize 原頁未直接讀取（皆二手）；ARC 金額衝突、Opus 5 harness 歸屬待核；Anthropic 90.2% 待查核。
4. Luna 時間範圍無錨點；任務長度為新增 Assumed；檔案參數全為 Assumed／Analogy。
5. 延後：harness 用於 RL rollout；非 GPU 成本（L6）；Workload 列 38 對 Anthropic 參照的 2.3–2.5 倍落差（未調整）。

## 8e. CC 第 8 輪（v5.9）驗收與 v5.10（M1 (b)）

**第 8 輪驗收（2026-10-02，chat 端）**：五項期望值全部符合。builder 三項驗證 27,190 格不符 0、restore_log 未對應 0、藍字 1,151；公式 20,686、具名範圍 294 各前綴一致；parity 121 項全過，13 情境不符 0、錯誤 0，嚴格比對已恢復；網站 Block 4（K6 預設 (c)、機隊三層級＋合計、`B4_MktChina`）與 Block 5 頁以截圖確認；機隊加總（H100 4.062、Rubin Ultra 82.09、VR200 前緣 48.0）與 Block 5 token 比（Coding 0.4925）獨立驗算一致。CC 另發現 v5.9 新增 90 處 `OR`，pycel 支援。PR #8 已合併（7627a82），合併後 master CI 兩次成功（CC 回報）。
- 顯示瑕疵（工程類，排入第 9 輪）：Block 5 推導鏈成功率單位 % 但顯示 0.9622；Block 4 攤提對照圖混入兩條全成本序列；Block 5 檔案名稱截斷。
- CC 第 8 節：每次嘗試成本（Harness D 節第 67–84 列已有，缺名稱）與有效時間範圍（需新增乘積列）→ v5.10 提供；CHANGELOG 雜湊併入第 9 輪。

**v5.10（2026-10-02，以 v5.9 為底稿）**
- M1 (b)：Har_In!C8 可靠度下限 p_min（`B5_PFloor`，基準 50%，Decision；0＝不設下限＝(a)）。Harness H 節：原前緣改標「對照（不設下限）」；新增 p ≥ p_min 的前緣成本、組合、組合成功率（VR200、GB300），無合格回傳「無合格」。
- Harness I 節：有效 50% 時間範圍＝層級 H50 × 時間範圍倍數（現行）。
- Interface E 節末尾：`IF_CostAttVR_*`、`IF_HzEff_*`、`IF_PFloor`、`IF_FrontSuccVR`、`IF_FrontSuccVRName`、`IF_FrontSuccVRP`。Checks Block 5 前緣列改讀 p ≥ p_min 版（對照欄為不設下限），加 p_min 與「無合格任務數」兩列。
- 驗證：公式 20,780、零錯誤；具名範圍 305；對 v5.9 差異 157 格全在預期位置；冪等 27,334 格不符 0；藍字 1,151 全數對應＋新增 1。三種下限的前緣皆以 Python 獨立重算一致。

**v5.10 基準結果（VR200、經濟、基準成本；前緣組合｜每成功任務成本｜p）**

| 任務 | p_min＝0（(a)，對照） | p_min＝50%（基準） | p_min＝80% |
|---|---|---|---|
| 一般聊天 | Luna｜標準 | Luna｜標準（96.2%） | Luna｜標準 |
| 推理聊天 | Luna｜標準 | Luna｜標準（88.4%） | Luna｜標準 |
| 單代理 | Luna｜選定 | Luna｜選定（72.3%） | Sol｜選定（90.2%） |
| 多代理研究 | Luna｜選定 | Luna｜選定（57.5%） | Sol｜選定（82.6%） |
| Coding agent | Luna｜選定 $0.0125（32.4%） | Sol｜選定 $0.0209（62.7%） | 無合格 |

- 讀法：50% 下限只改變 Coding agent 的前緣（成本 1.67 倍）；多代理研究 Luna 的 p 57.5% 距下限僅 7.5 個百分點，下限調到 60% 即改為 Sol。p 皆來自 METR 型曲線，H50 為 Analogy、β 為 Derived、任務長度為 Assumed，前緣組合對這三者敏感。
- 前緣比較的「選定」為選定檔案全採用（情境），基準 w＝0。

**CC 第 9 輪驗收（2026-10-02，chat 端）**：全部符合 `CC_round9_v5.10.md` 期望值。三項驗證 27,334 格不符 0（README 亦一致）、restore_log 未對應 0（1,151／1,152）；公式 20,780；具名範圍 305 各前綴一致；v5.9→v5.10 差異 157 格位置一致；新增 11 名稱位址（B5_PFloor＝Har_In!C8；Interface 第 183–192 列）。parity 124 項全過；15 情境錯誤 0、不符 0、最大相對誤差 4.9e-15；floor_0、floor_80 與基準前緣期望值測試皆通過。網站：推導鏈補每次嘗試成本與有效時間範圍、成功率百分比、前緣表、檔名換行、Block 4 攤提圖拆出全成本圖。CHANGELOG 已補 e59bf4f、7627a82。本輪報告未附截圖檔（CC 稱以瀏覽器截圖確認），網站變更未經 chat 端目視；不阻擋合併。

## 8f. Block 6（Alloc）與 Answers：命題與決定（Andy 2026-10-02「All OK」「OK」）

> **2026-10-02 後續變更**：Block 6 改在 v5.13 建置（G10；2026-10-03 再順延為 v5.14），需求 D 等原始數據先進 SRC_Demand；Answers 頁不另建，第一批 9 題寫入 L1 頁、名稱前綴改為 L1_（G9）。以下命題、驅動對照表與 A1–A8 不變。

**起因**：Andy 問「前沿實驗室的算力、算力成本、整體成本各有多少比例用在訓練及研發」。v5.10 的回答能力：Q1 算力占比＝Fleet_1GW 59%（Cap_In 第 28 列 41% 的補數），是輸入而非推導（OpenAI 2025 訓練約 $12B 對推論 $8.4B，Interested-party；以支出比代 GW 比，Derived）；Q2 算力成本占比與 Q1 同數同源（同世代每 GW 成本相同；且該輸入本來就是成本比，有循環）；Q3 不在範圍（L6）。理論路線：研發占比＝N × P × k ÷（N × P × k ＋ S）；VR200 家族研發計畫 P＝0.0443 GW 年（Fleet_1GW 第 33 列）；校準值 59% 對應 N × k ≈ 13（即 J8 落差：Amortize 第 41 列縮放 8.97 倍）。

**命題**：實驗室年度算力＝研發需求（家族計畫＋改版計畫）＋服務需求（需求 token ÷ 每 GW 年產能）。研發占比的物理部分只給下限；實際占比由策略變數（家族數、改版數、計畫規模）決定，屬激勵 [I] 而非物理 [P]。本頁推導 Q1、Q2，把校準值反推為隱含 N × k，並列敏感度。

**驅動對照表**

| 項目 | 定義 | 基準（區間） | 標記 | 來源 |
|---|---|---|---|---|
| 家族計畫數 N_major | 每年完整家族計畫（三層級，含研發倍數 8） | 1（1–2） | Assumed | — |
| 改版計畫數 N_refresh | 每年只做後訓練的改版（x.1、x.2） | 2（0–4） | Assumed | — |
| 改版計畫規模 | 家族後訓練 GPU 小時 × 研發倍數 | Block 3 推導 | Derived | Training 第 110–111、119 列 |
| 計畫規模倍數 k | 相對 Block 3 自下而上 | 1（0.5–7） | Assumed | Cap_In 第 15 列 |
| 需求 D | 年服務 token（層級 × 付費／免費） | 連結 OpenAI 模型 v0.5（API FY2025 2,628T，2,000–3,200T） | Interested-party／Derived | openai_token_revenue.json |
| 每 GW 年產能 | 依層級組合 | Block 2 推導 | Derived | Perf、Fleet_1GW |
| 訓練世代 | 研發計畫所用世代 | VR200 | Decision（J13） | — |
| 服務世代組合 | 服務機隊的世代分布 | GB200 40%／GB300 40%／VR200 20% | Assumed | — |
| 每 GW 年成本 | 經濟持有成本（依世代） | Block 1 推導 | Derived | DC_Cost |
| 機隊年成長率 g | 情境用 | 0（0–100%） | Assumed | — |

**決定（全部依建議）**
- A1 基準為穩態年度（研發＋服務）；成長效應另列情境（A6）。
- A2 計入改版計畫。
- A3 不以 59% 校準 k；基準 k＝1（Block 3 理論值），校準值只反推隱含 N × k 並列 J8 落差。
- A4 以需求 D 推導服務 GW；實驗室總 GW 只作檢查。
- A5 Q2＝已裝 GW × 各世代每 GW 年持有成本；訓練用最新世代、服務用世代組合；利用率不影響成本占比；雲端與自有差異留在下游（WACC 維持單一）。
- A6 成長只作情境：為下一代準備的研發計畫依未來需求定規模，使當年研發占比上升。
- A7 基準輸出 R1（最終訓練＋研發實驗，含訓練內推論型運算）；R2（免費服務算作產品改良）並列；R3（內部使用）列為缺口、不設參數。
- A8 建「實驗室」選擇器，只放 OpenAI 一組；Anthropic（免費占比、層級組合）待來源查核後加入。

**Answers 頁**：欄位＝問題｜答案（基準）｜區間｜讀法｜主要驅動｜最弱輸入的標記｜具名範圍｜所在頁與列｜未能回答的部分；答案欄一律以公式連結具名範圍；網站新增「問答」頁讀 AN_ 名稱。第一批 9 題：(1) 研發算力占比 Q1；(2) 研發算力成本占比 Q2；(3) 研發占整體成本 Q3（答案＝下游 OpenAI v0.6，並列 Tokenomics 提供的算力部分）；(4) 各層級每 M token 成本（VR200）；(5) 每 GW 理論營收與理論毛利率；(6) 後訓練占比（FLOPs 對 GPU 小時）；(7) 單價前緣與 OpenAI 單價差距；(8) harness 是否降低每成功任務成本（R）；(9) 成功任務成本前緣（p ≥ p_min）。

**Q3 歸屬**：OpenAI 模型 v0.6（非 GPU 成本：人事含股權報酬、資料與標註、行銷、管理）；Tokenomics 以 IF_ 名稱提供依用途拆分的算力成本。

## 8g. CC 第 10 輪（Stage 0）驗收（2026-10-02，chat 端）

- **全部符合** `CC_round10_stage0.md` 第 10 節：v5.10 SHA-256 前後一致（d7d59ab8…497f；chat 端另以分支上的檔案比對）；藍字 324 列／1,491 格／31 個藍字公式格；初步分類九類計數、主標記分布、多標記 27、S 編號 108 皆相同，INV_ID 與 chat 端逐列對齊；OFFSET／INDIRECT 0；engine 基準對快取值 1.9e-15；觀測 ⊆ 靜態違反 0；LibreOffice 抽驗前 10 列 4.0e-15；308 次擾動還原不一致 0；parity 124 項全過、15 情境錯誤 0、不符 0；Block 5 任務表 1280 px 截圖目視通過；CHANGELOG 補 PR #9 合併雜湊 fcbb384（chat 端確認為 PR #9 合併提交）。執行約 193 秒。
- **chat 端獨立重算**：以 LibreOffice 對生產折減、VR200 機架價格、歷史快取命中率 χ 各 +10%，主要輸出的 ε₊ 與 CC 敏感度頁逐項相同。
- 敏感度：高段 30 列、中段 34、低段 44、無 216（其中 169 列未擾動）。生產折減 ±10% 使 VR200 Astra decode 成本 −14%／+20%、Sol 每 GW 理論營收 ±12.7%。5 列只經前緣翻轉影響結果（Cap_In 37、Har_In 12、14、18、19）。
- 處置：指令外的總覽頁崩潰修正（v5.10 新增 10 個 IF_ 名稱未列入 Block 5 前綴）保留；CC 第 8 節詮釋全部接受；390 px 手機版任務表暫不做；CC 第 7 節 Excel 問題併入 v5.11（第 0 節第 4 點）或列為發現（審閱檔 F13–F16）。

## 8h. v5.11（治理 Stage 1 切片一）結果與待辦（2026-10-02，chat 端）

**做法**
- **SRC 紀錄**：Stage 0 審閱檔「SRC_候選」中屬 HW、DC、Model、Perf 的 153 筆遷入，等級、立場、狀態照審閱結果；另補登 11 筆（3 級、模型內建知識，原始 S 編號記為 U-V511）：HGX NVLink 域 8（SRC_HW_053）、Rubin Ultra 144 封裝（054）、FP8 1 byte（055）、H100／GB200／GB300 GPU 功率 700／1,200／1,400 W（056–058）、B300 HBM 頻寬 8 TB/s（059）、IB NDR 400 Gb/s（060）、DeepSeek-V3 注意力 heads 128、qk 192、v 128（SRC_MOD_049–051）。補登原因：Gate 1 要求模型頁原始數據 0 格寫死，而這些格原本沒有任何來源紀錄。
- **SRC_Perf 量測條件**：InferenceX 七個錨點的平台、軟體、ISL、OSL、每用戶速度、MTP 寫入 SRC_Perf AA–AG 欄，Calib 第 13–16 列改連結（`_ISL`、`_OSL`、`_Spd`、`_MTP`）。
- **連結規則**（G0-2）：值相等者改連結（含改公式後值不變者，例：Spec_Rack F39:F41＝全架峰值 ÷ 72、F33＝1.8 kW × 1000、F34＝2.5 pJ/bit × 8、C27＝400 Gb/s ÷ 8 ÷ 1000、Arch C17:D17＝1,024 × 4＋128、Calib C108:C109、Tech_Registry J14＝四筆採用紀錄加總）；值不等者保留藍字，登錄為「原始數據（G0-2 保留）」17 格（Stage 2 佇列）。Spec_Rack!F11（MS 自購記憶體 6.7，Alt）依 G13 保留藍字。
- **Gov_Map**：切片一 8 頁（Inputs、Spec_Rack、Arch、Serving、Workload、Calib、Energy、NonNV）全部藍字格，與 Perf、Sens_Perf、Unit_Cost 的情境格，另加 Train_In、Tech_Registry 中已連結的 9 格，共 435 列；類別：Assumed 194、原始數據 157、Analogy 20、Decision 17、G0-2 保留 17、Derived（待改公式）10、情境 15、切片二 3、Derived（公式）2。A–P 欄為判斷（Excel 擁有），Q–AE 欄由 builder 重建。
- **Checks G 節**：E1–E12（ERROR）、W1–W2、I1–I8。實作時避開 COUNTIFS、IFERROR、LEFT（parity 未測），改用 SUMPRODUCT、COUNTIF、ISNUMBER(MATCH())；種子資料空欄一律填「—」，避免空白＝"" 的引擎差異。結果：ERROR 0；W1 利害關係方缺第二來源 133；W2 3 級紀錄被高段參數使用 31；I1 待判定 4、I3 L1 外部區間外 2、I4 G0-2 保留 17、I5 待改公式 10、I6 結構選擇 5、I7 切片二 3、I8 標記變更 28。
- **L1 第一批 25 列**：每 GW 資本支出（4 世代）、VR200 每 GW NVIDIA 內容、每 MW IT 廠房資本支出、每 GW 年經濟持有成本（4）、每 GPU 小時持有成本（4）、decode 每 M token 成本（3 層級 × VR200／GB300）、GB300 以 InferenceX 產出計的每 M 總 token 成本、VR200 每 GW 理論營收（3 層級＋機隊）。外部對照：VR200 資本支出 47.6 低於黃仁勳 $50–60B；每 MW 廠房 12.67 高於 JLL × 液冷溢價 12.09–12.43；其餘有對照者在 ±20% 內。
- **F14**：DC_Cost 改為設施合計（Inputs!E5 GW）；Interface、L1 與模型頁的每 GW 值一律除以 E5。E5＝2 時每 GW 名稱變動 ≤1.52e-4（設施機架數 FLOOR 取整殘差；原記 1.2e-4 有誤，CC 第 11 輪實測、chat 端重算確認，最大在 IF_AmortBU_* VR200 欄）。基準 E5＝1 數值不變。
- **builder 所有權**：SRC_*、Decisions、DB_Evidence 與 Gov_Map A–P 欄只在不存在時建立；模型頁 SRC 連結清單（`gov_seed.FORMULA_MAP`）、SRC X–Z 欄、Gov_Map Q–AE 欄、L1、Checks G 節每次重建。

**待 Andy（不影響數值）**
1. **標記變更 28 格**（Gov_Map O 欄；Checks I8）：沒有可比 SRC 的 Analogy 改為 Assumed，例如 PUE（S14 不遷入）、Inputs 24–27 年限與 30、31、35（可比對象為 v4）、Serving 12–14、Spec_Rack 29 Hopper 與 31 列、Calib 5、67 Hopper、Energy 7。
2. **Claude 提議的區間**（Gov_Map M 欄含「Claude 提議」）：Inputs 24–27 年限、Spec_Rack Rubin Ultra 欄 ±30%、Astra 架構參數、Serving 10、11、18（生產折減 0.7–1.0）與 22–24、Workload 5–12、Calib 69。
3. **CV1** Hopper 機架定義（第 2 節）。
4. **Decisions 頁原話**：J 欄「原話待 Andy 確認」＝是者，確認後改為否。

**延到 v5.12**：Arch 21–23 改公式（需新增 Assumed 輸入列：每層 KV bytes、Astra 混合比例）；Arch C9 V4-Flash d_model 反推所需參數；Checks C9:C10 與其餘外部比對移入 L1；Workload 40 連結 SRC_Harness；Sources 更名 Sources_Legacy；Gov_Map 擴及切片二頁。

## 8i. CC 第 11 輪（v5.11 同步、Gate 1）驗收（2026-10-03，chat 端）

**依據**：CC 報告、`20261002_gate1.md`，與 chat 端對 v5.11 的獨立重算（LibreOffice）。`CC_round11_v5.11.md` 不在 repo 與 Project 內，對照數字取自本文件第 0、8h 節。

- **檔案**：分支上 v5.11 的 SHA-256 與 master 相同（941b78ad…b103）；CC 以 v5.10 為底稿重建，46,869 格不符 0，表示 builder 能重現交付檔。
- **計數一致**：公式 27,700；具名範圍 604（SRC 220、IF 167、L1 75、B4 39、B5 24、TR 23、CAL 19、DRV 16、TRN 15、GOV 4、CTL 2）；DB_Evidence 67；SRC 匯出 60／13／51／40；Checks ERROR 0、WARN 164（W1 133＋W2 31）、INFO 69（4＋2＋17＋10＋5＋3＋28）；parity 18 情境不符 0（最大 5e-15）；restore 未對應 0。
- **Gate 1**：3.1、3.2（寫死 0）、3.3、3.4、3.5（99 格、33 名稱，觀測 ⊆ 靜態）、3.6 全部通過。
- **chat 端記錄更正**：(1) E5＝2 最大相對差為 1.52e-4（121 格超過原記的 1.2e-4，皆 ≤2e-4），第 8h 節已改；(2) 藍字常數格 2,203（含文字 855），CC 計數正確，原記 2,200 有誤。
- **3.2 公式內常數（chat 端判定；收尾後共 11 格）**：全部值不變，v5.12 移到具名輸入格並登錄 Gov_Map。
  - Arch C31:E31 的 128000：「128K 上下文每序列 KV」顯示列，無任何引用；類別「結構選擇」，並在說明註明 128,000 而非 131,072。
  - Sens_Train O53:P53 的 ×0.3 與 Q53:R53 的 ×3（CC 漏列，誤歸為單位換算）：情境倍數，只寫在第 3 列標題文字；移到情境輸入格（黃底藍字），類別「情境」。
  - Sens_Rev D17、F17 的指數 0.5：ε（K4 (a) 量級情境），與 B17（×7）同列；移到獨立格，類別「情境」。
  - Sens_Train AA93:AB93 的 ×3（CC 收尾時自行補列）：合成資料 token 的情境倍數，與 Q53:R53 同性質。同列 Y93:Z93 的 ×0 情境是直接寫入的藍字 0，寫法與 ×3 不一致；v5.12 把 Sens_Train 所有情境倍數統一放到一列倍數輸入格。
  - Tech_Registry K5:K16 的「≥2」（CC 列為留意項）：J14「至少兩家實驗室採用」的決策門檻寫在公式內；v5.12 移到一個具名輸入格，Gov_Map 類別「Decision」、決策 ID J14。
  - Spec_Rack C35:E35 的 `Serving!C16=2`：峰值情境選擇器的選項代碼，不是參數，維持原狀。
- **重算時間**：CC 把原因歸於 SUMPRODUCT，實際上 Gov_Map 沒有 SUMPRODUCT；負載來自 S、T 欄每列 16 個 MATCH（共 6,960 個），各在 4 個 SRC 頁的 A5:A400 查找，掃描上限約 276 萬列次（CC 收尾實測；chat 端原記 426 萬是把 INDEX 回傳範圍一併計入，不是 MATCH 掃描量）。這個寫法隨「Gov_Map 列數 × SRC 頁數」成長，切片二（頁數 4→8、列數約倍增）估計會到十秒級，所以單純放寬門檻不夠。判定（工程類）：
  - 本輪：測試改為增量 < 2 秒（硬性）、全簿 < 5 秒（暫行，防止更惡化）；
  - v5.12：新增 builder 擁有的 SRC_Index 頁（各 SRC 頁 A 欄依序堆疊，附頁名、狀態、等級），Gov_Map 每列只做 1 個 MATCH，恢復全簿 < 2 秒。
- **S30 一手來源（2026-10-03 已取回）**：DeepSeek `open-infra-index` 202502OpenSourceWeek day 6（統計期間 2025-02-27 12:00 至 02-28 12:00，UTC+8）。prefill 路由專家 EP32（4 節點）、decode EP144（18 節點）；每台 H800 節點平均輸入約 73.7k tok/s（含快取命中）、輸出約 14.8k tok/s；輸入 608B 中 342B（56.3%）命中磁碟 KV 快取；輸出 168B、平均每用戶 20–22 tok/s、每輸出 token 平均 KV 長度 4,989。等級：一手、利害關係方（DeepSeek 自述）。v5.13（B 包）補登 SRC_Perf，供 Spec_Rack C29、Calib C5、C67 恢復 Analogy，並作為 Workload χ 與 SLO 的外部對照。

**補充指令（交給 CC，第 11 輪收尾）**
```
[Tokenomics 指令] 第 11 輪收尾｜2026-10-03
1. 重算時間測試改為兩項：增量重算 < 2 秒（每情境）、全簿強制重算 < 5 秒。
   在測試與 CLAUDE.md 註明「暫行至 v5.12；v5.12 以 SRC_Index 改寫 Gov_Map 查找後恢復全簿 < 2 秒」。
2. 報告第三節更正原因：Gov_Map 無 SUMPRODUCT，負載來自 S、T 欄的多重 MATCH（約 6,960 個）。
3. 報告第五節 3.2 清單補 Sens_Train Q53:R53（×3，情境倍數，非單位換算），共 9 格；chat 端判定見交接第 8i 節。
4. 建 PR，回報 GitHub Actions 結果（含 export_csv 的 GOV_Errors＝0）。不改 Excel。
```

**收尾結果（2026-10-03，chat 端核對 PR #11 與 Actions 頁）**：最新提交 1e979a0f 的 parity 第 65 次成功（47 分鐘），PR 觸發的第 66 次亦成功；第 64 次（56a0aab3，收尾前）失敗屬預期。CI 跑 `tests/parity` 127 項全過（本機原 139 項＝126＋網站 13；拆門檻後多 1 項）；18 情境全過；增量、全簿兩條重算測試皆過（CI 未記秒數，以斷言通過為準；本機增量 ≤0.5 秒、全簿 3.4–3.7 秒）；GOV_Errors 0、WARN 164、INFO 69；匯出列數與第 11 輪相同。最大相對誤差 5e-15 為本機值（CI artifact 無法下載），parity 斷言門檻 1e-9 已在 CI 通過。報告第三、五、九節與 CHANGELOG 已更正。

## 8j. 切片二工作包與規模（2026-10-03，chat 端規劃；A 包已成為 v5.12，B–E 包為 v5.13）

**盤點（v5.11，chat 端計數）**
- 尚未登錄 Gov_Map 的數值藍字格：Cap_In 142、Har_In 139、Tech_Registry 83、Train_In 58；情境與敏感度頁 Sens_Train 84、Sens_Perf 82、Perf_Batch 38、Perf 30、Training 30、Unit_Cost 15、Calib 14、Sens_Rev 13、Sensitivity 3（後者多為世代或層級索引，屬情境選擇器）。
- Stage 0 審閱檔「格對照」已有切片二的格與 SRC 對應：SRC_PRC→Cap_In 47、Checks 2；SRC_CAP→Cap_In 10、Har_In 8；SRC_HAR→Har_In 10、Workload 2、Checks 1；SRC_DEM→Cap_In 3、Checks 5。其中 74 格「一致」、14 格「—」需逐格看。
- **Training 不需新 SRC 頁**：Train_In 的 12 格對應 SRC_MOD、1 格對應 SRC_PERF，都在切片一已遷入的紀錄中；v5.13 只需連結與登錄 Gov_Map。

**工作包（依序）**
1. **A 工程基礎（先做，避免切片二使重算惡化）**：新增 builder 擁有的 SRC_Index 頁，Gov_Map S、T 欄改為每列 1 個 MATCH，目標全簿重算 < 2 秒、恢復原門檻；Sources 更名 Sources_Legacy；11 格公式內常數與 Tech_Registry K5:K16 門檻移到具名輸入格；Sens_Train 情境倍數統一一列。全部值不變。
2. **B Source 遷入**：SRC_Price 44、SRC_Cap 21、SRC_Harness 15、SRC_Demand 9，共 89 筆，等級與立場照 Stage 0 審閱；S30 補登 SRC_Perf（第 8i 節數據）；依格對照連結模型格（G0-2：值相等改連結，不等保留藍字並登錄 G0-2 保留）；Checks C9:C10 改連 SRC_Price；Workload 40 連 SRC_Harness。
3. **C Gov_Map 擴及切片二頁**：上列各頁的數值藍字格逐格分類、標記與區間（判斷類）。依 v5.11 經驗會產生新一批「Claude 提議區間／標記變更」，交 Andy 審閱。
4. **D 模型邏輯**：Arch 21–23 改公式（新增 Assumed 輸入：每層 KV bytes、Astra 混合比例），值須與現值一致；Arch C9 反推；Checks 外部比對移入 L1。
5. **E 寫回 Andy 審閱結果**：`20261003_v5.11_待Andy_審閱檔.xlsx` 回填後寫入 Gov_Map O、M 欄與 Decisions J 欄；若 v5.13 交付時仍未回填，延到下一版，不阻擋。

**驗收門檻（沿用 v5.11）**：LibreOffice 零錯誤；模型頁與 Interface 對 v5.11 逐格一致（D 包改公式者值相同）；冪等 0；Checks G 節 ERROR 0；restore unmatched 0；全簿重算時間由 CC 量測。

## 8k. v5.12（工程基礎，原 A 包）結果（2026-10-03，chat 端）

**做法（全部數值不變；工程類，chat 端定案）**
- **SRC_Index**（builder 擁有，每次重建）：4 個 SRC 頁的 A（ID）、O（狀態）、K（等級）依序堆疊，各頁範圍＝第 5 列到最後一筆紀錄＋50 列（目前 364 列）；末段 696 列為 Gov_Map!H5:H700 的鏡像（哨兵）。具名範圍 IDX_SrcID、IDX_SrcStat、IDX_SrcGrade。
- **Gov_Map**：新增 AF 欄「SRC_Index 列」＝每列 1 個 MATCH；S、T 改為 INDEX(IDX_…, AF)。找不到的 SRC_ID 落在哨兵段，回傳「不存在」，與 v5.11 相同。因規則不用 IFERROR（parity 未測），以哨兵取代錯誤處理，無 #N/A、無新函數。435 列 S、T 值逐格相同。
- **SRC 各頁 X 欄**（計畫外，同屬重算時間）：只做 SRC_Index 時全簿仍 2.2–2.4 秒；逐頁計時顯示 SRC 各頁 X 欄（每筆 4 個 396 列陣列相乘）約占六成。新增 builder 擁有的 AH 欄「同指標鍵」（Active 時＝指標¦口徑¦適用對象，否則空白），X 改為單一陣列比對；264 格 X 值相同。
- **Checks G 節新增 E13**（ERROR）：SRC 紀錄超出 SRC_Index 範圍（需重建）。E13 插在 E12 之後，其後各列下移 1 列（GOV_ 名稱隨之移動）。
- **Sources 更名 Sources_Legacy**（A1 改為凍結說明；無公式或名稱引用）。
- **公式內常數移到具名輸入格**（第 8i 節 11 格＋J14 門檻），並由 `gov.GOV_MAP_V512A` 在未登錄時附加 Gov_Map 列（Excel 擁有，之後不覆寫）：
  - Arch C32＝128,000（CST_CtxKV；GM436，Assumed、結構選擇）；C31:E31 改引用。
  - Sens_Train 第 8 列「情境倍數」（CST_STMult）：O:R＝0.3、0.3、3、3（GM437）；Y:AB＝0、0、3、3（GM438）；其餘欄「—」。O53:R53、Y93:AB93 一律為「基準 × 第 8 列」；v5.11 Y93:Z93 直接寫入的藍字 0 由 `training.SNAP_MOVES` 轉到第 8 列（Excel 值會帶過去，restore unmatched 仍 0）。
  - Sens_Rev B18＝0.5（CST_Eps；GM439，情境值）；D17、F17 改引用。A17 標籤文字的「ε＝0.5」不隨 B18 更新（G18 已註明）。
  - Tech_Registry J17＝2（CST_MainMin；GM440，Decision、J14）；K5:K16 改引用。
- **既有問題修正**：v5.9 起具名範圍為 `B5_Selrho`，Workload 第 20 列與 Harness、Sens_Har 公式寫 `B5_SelRho`（25 格）。Excel／LibreOffice 不分大小寫，過去交付的 LibreOffice 存檔已正規化，故數值與 CC parity 皆不受影響；但 builder 直接輸出、未經 LibreOffice 的檔案在 pycel（分大小寫）會出現「Table Name not found」。已把公式改為與名稱一致的 `B5_Selrho`（名稱不改，app 與測試不受影響）。

**驗證**
- LibreOffice 重算錯誤 0；公式 27,700 → 30,158；具名範圍 604 → 611（CST_ 4、IDX_ 3；SRC_ 仍 220）。
- 對 v5.11 逐格比較 47,669 格：模型頁、Interface、L1、Gov_Map S／T、SRC X 數值全部一致；差異只在 README 4 格、Sens_Rev!G17 說明、Sources_Legacy!A1、Checks G 節（E13 插入與下移）與新增格。
- Checks G 節：ERROR 0、WARN 164、INFO 70（I6 結構選擇 5→6，因 Arch C32）。
- restore：以 v5.11 為底稿 1,021 格全數對應；以 v5.12 為底稿 1,030 格（＋11 新輸入、−2 轉移）全數對應。冪等：52,982 格公式與字型不符 0、名稱 611 個相同。
- Excel 優先與連動：改 C32、O8、Y8、B18、J17 後重建，5 格保留，C31、O53、Y93、D17、K 欄隨之變動。E13：在 SRC_HW 範圍外加假紀錄，E13＝1，重建後歸 0；Gov_Map 指向不存在的 ID 時 S／T＝「不存在」。
- 全簿強制重算（repo `engine`／pycel，本機，同 `test_full_recalc_time` 做法）：v5.11 3.37–3.61 秒 → v5.12 1.21–1.30 秒。
- 本機以 repo 測試（`tests/parity`；暫存複本中期望值改為 formula_cells 30158、defined_names 611、sheets 加 SRC_Index 與 Sources_Legacy，`FULL_RECALC_LIMIT_S` 改回 2.0）：**127 項全過**（工作表與名稱期望、CURRENT、全簿重算 < 2 秒 5 項；情境 parity、函數語意、增量重算 < 2 秒等 122 項，37 分鐘）。

**CC 同步**：見第 8l 節指令（第 12 輪）。

**對 v5.13（B 包）的影響**：新增 SRC 頁時 `gov.SRC_SHEETS` 加頁名，SRC_Index、AH 鍵欄與 E13 自動涵蓋；Gov_Map 新列查找成本隨列數線性、不再隨 SRC 頁數倍增。

## 8l. CC 第 12 輪指令（v5.12 同步，2026-10-03）

```
[Tokenomics 指令] 第 12 輪｜v5.12 同步（工程基礎）｜2026-10-03
依據：交接文件第 8k 節（Project）、repo docs/builder/Tokenomics_builder_v5.md（Andy 上傳的新版）。

1. 依 CLAUDE.md 第 4 節同步：
   - model/ 放入 20261003_Tokenomics_v5.12.xlsx（SHA-256 d04fac3b…0926），v5.11 以 git mv 移到 model/archive/，更新 model/CURRENT。
   - 依 md 的「## <檔名>.py」區塊逐字覆寫 builder/（14 檔）。
   - 驗證：python3 builder/build.py model/archive/20261002_Tokenomics_v5.11.xlsx /tmp/check.xlsx，LibreOffice 重算後與 v5.12 逐格一致
     （README 除外）；restore_log unmatched 0。另以 v5.12 為底稿重建，冪等 0。
2. tests/parity/scenarios.yaml 期望值：formula_cells 30158；defined_names 611（新增 CST_ 4、IDX_ 3；SRC_ 仍 220）；
   sheets 於 SRC_Perf 之後為 SRC_Index、Sources_Legacy、DB_Evidence。
3. 全簿重算門檻恢復：FULL_RECALC_LIMIT_S = 2.0；刪除測試與 CLAUDE.md 中「暫行至 v5.12」的註記。增量 < 2 秒不變。
   報告記錄 CI 實測秒數（chat 端本機：全簿 1.21–1.30 秒）。
4. app 與工具：凡寫死 "Sources" 頁名處改 "Sources_Legacy"（含 tools/stage0_inventory.py 的 GOVERNANCE_SHEETS，並加 SRC_Index）；
   CST_、IDX_ 前綴不顯示為下游名稱（下游不得連結）。數值與機制不改。
5. Checks：GOV_Errors 0、GOV_Warnings 164、GOV_Info 70（I6 由 5 變 6）；G 節新增 E13，其後各列下移 1 列，以名稱讀取者不受影響。
6. 發現 Excel 問題時依第 4 節第 5 點列在 PR，不在 Python 修補。
   已知且已修正：v5.9 起公式 B5_SelRho 與名稱 B5_Selrho 大小寫不一致（25 格），v5.12 已把公式改為 B5_Selrho；
   請確認 pycel 載入不再出現「Table Name not found」。
7. 可選、不阻擋合併：parity 測試總時長（本機約 37 分鐘、CI 約 47 分鐘）主要來自每個情境重新建 Engine（每次 44–50 秒）。
   可評估以 pycel 編譯結果存檔再讀回、各情境共用，但不得改變比對範圍、容差與情境。若做，報告前後時長。
8. CHANGELOG、docs/reports/20261003_v5.12_sync.md、PR；回報 GitHub Actions 結果（parity 項數、18 情境、兩條重算測試、export_csv 的 GOV_Errors）。
   本輪屬同步，不改 Excel。
```

## 8m. v5.13 B 包（切片二 Source 遷入）結果（2026-10-03，chat 端）

**做法（數值逐格不變）**
- **新 SRC 頁**：SRC_Price 44、SRC_Cap 21、SRC_Harness 15、SRC_Demand 9，共 89 筆；等級、立場、狀態照 Stage 0 審閱檔「SRC_候選」，出處取 Sources_Legacy F 欄（與切片一同法）。資料在新檔 `gov_seed2.py`；`gov.SRC_SHEETS` 4→8，SRC_Index、AH 鍵欄、E7／E8／W1、E13 自動涵蓋。
- **S30 一手來源**：chat 端 2026-10-03 直接讀 DeepSeek `open-infra-index` 202502OpenSourceWeek day 6 原文，補登 SRC_Perf `SRC_PERF_041`–`051`（1 級、利害關係方）：每節點 prefill 約 73.7k、decode 約 14.8k tok/s；24 小時輸入 608B、輸出 168B tok；快取命中 56.3%；每用戶 20–22 tok/s（_Lo／_Hi）；每輸出 token 平均 KV 長度 4,989；尖峰 278、平均 226.75 節點；部署單元 prefill 4 節點（EP32）、decode 18 節點（EP144）。原文的日成本 $87,072 與成本毛利率 545% 以 DeepSeek 假設的 $2/GPU-hr 與 R1 全額計價推算，非實測，不登錄。
- **機制（Excel 擁有規則延伸）**：既有 SRC 頁的新紀錄由 `gov.src_append` 只在 ID 不存在時附加；Gov_Map 判斷欄更新（`GOV_MAP_UPD`）由 `gov.gm_update` 只在該格仍為 v5.12 原值時寫入，之後不覆寫 Andy 的修改。
- **DB_Evidence**：E148–E163（依原 S 編號的遷移紀錄：S18、S19、S25、S38、S50–S61）、E164（S30 一手補登），共 17 列（67→84）。
- **模型格改連結（FORMULA_MAP2，75 格，值相等者）**：Cap_In 55、Har_In 17、Workload E40:F40；Har_In E75＝SRC_HAR_002/SRC_HAR_001（15÷4＝3.75）。
- **Checks**：C9＝SRC_PRC_001/4（÷4＝每執行個體 GPU 數，單位換算）、C10＝SRC_PRC_002、最終訓練 ÷ 研發計畫的外部區間由 SRC_DEM_001–003 的 MIN／MAX 組成、OpenAI 2025 對帳常數 I 欄（營收、2024／2025 年底 GW）連結 SRC_DEM_007–009；F 欄加［SRC_ID］註記。以標籤定位列。其餘外部比對移入 L1 仍屬 D 包。
- **保留藍字（C 包登錄）**：Cap_In C28（0.41；來源換算 0.4118）、C29（0.46；0.4643）依 G0-2；Cap_In I53、I56 值相等，但來源模型版本不同（V4 Pro 對 V4-Pro-0813；Qwen3.8 2.4T 對 Max），連結等於宣稱同一模型，比照切片一 Train_In C7 先例保留，C 包按 Analogy 登錄。Train_In 無新連結格：8 格已於 v5.11 連結，C7、C44、C46–C48 為選取／換算，於 C 包登錄。
- **Gov_Map 判斷更新（6 列 27 格）**：GM301 Workload C40（聊天＝1 的比較基準）改為 Assumed、結構選擇；GM302／303 E40、F40 改為原始數據、已連結；GM130 Spec_Rack C29、GM304 Calib C5、GM341 Calib C67 依第 8i 節規劃恢復 Analogy，可比對象 SRC_PERF_051／041／042，O 欄標記變更清為「—」（審閱檔 T06、T11、T12 相應項目因此已處理，E 包寫回時略過）。Workload C11 χ 仍為 Assumed（S30 只作對照）。

**驗證**
- LibreOffice 重算錯誤 0；公式 30,158 → 31,544；具名範圍 611 → 713（SRC_ 220 → 322）。
- 對 v5.12 逐格比較 66,583 格：模型頁、Interface、L1 數值全部一致；差異只在 README、DB_Evidence、SRC_Perf 新列、SRC_Index、Gov_Map 52 格、Checks 11 格。
- Checks G 節：ERROR 0；WARN 164 → 234（W1 133 → 203，新增 70 筆利害關係方紀錄缺第二來源；W2 31）；INFO 70 → 65（I6 6→7、I7 3→0、I8 28→25）。
- restore：以 v5.12 為底稿 1,030 格全數對應；以 wip 檔為底稿 955 格（＝1,030－75 連結）全數對應。冪等：70,153 格公式與數值不符 0。
- repo engine（pycel 1.0b30，本機）：31,544 個公式格對 LibreOffice 不符 0（最大相對誤差 4.8e-15，同 v5.12）；全簿強制重算 1.42–1.50 秒（v5.12 同機 1.05–1.15 秒）。仍低於 2 秒門檻，但 C 包將使 Gov_Map 增加約 600 列，交付前須量測；若逼近門檻，需再精簡 Gov_Map 公式欄。

**CC 同步（v5.13 交付時併入指令）**：builder 由 14 檔變 15 檔（`gov_seed2.py`）；scenarios.yaml 的 sheets 於 SRC_Perf 之後加 SRC_Price、SRC_Cap、SRC_Harness、SRC_Demand；app 與 `tools/stage0_inventory.py` 的治理頁清單加這 4 頁；export_csv 的 SRC 匯出加 4 頁（44／21／15／9；SRC_Perf 40→51）。數字以 v5.13 最終交付為準。

## 8n. v5.13 C 包（Gov_Map 擴及切片二頁）結果（2026-10-03，chat 端）

**範圍**：B 包之後尚未登錄的數值藍字格 515 格／133 列：Har_In 121、Cap_In 87、Tech_Registry 83、Sens_Train 82、Train_In 58、Perf_Batch 38、Training 30、Sens_Rev 13、Sensitivity 3（第 8j 節的 Cap_In 142、Har_In 139 已扣除 B 包連結的 55、18 格；Sens_Perf、Perf、Unit_Cost、Calib 的情境格 v5.11 已登錄）。

**做法（數值不變；判斷由 chat 端，區間與標記變更交 Andy）**
- 登錄為 Gov_Map **129 列**（GM441–GM569），逐格覆蓋檢查：515 格全數涵蓋、重疊 0、範圍外 0。同列同性質（任務欄、層級欄、情境欄、索引列）以範圍登錄；同列「基準／低／高」者：基準格一列（低、高以公式連結同列端點，E10 檢查生效），端點一列（區間角色「低／高」）。
- 類別：Assumed 71、Analogy 18、情境值 18、Decision 8、情境選擇 7、原始數據（切片二，尚無 SRC 紀錄）3、原始數據（G0-2 保留）2、Derived（待改公式）2。
- 重點判定：Cap_In C28／C29 為 G0-2 保留（SRC_DEM_004／005，K7）；Cap_In I53／I56 為 Analogy（SRC_CAP_007／006，版本或模型未確認）；Cap_In N46:N58 中國廠商旗標可由國別改公式（Derived 待改公式）；Cap_In H46:H58 尖峰離峰屬性與 Tech_Registry 採用數 J 欄（T10 除外）為「原始數據（尚無 SRC 紀錄）」，G0-6 於 Stage 2 補紀錄；Tech_Registry T07（SRC_HW_037）、T10（SRC_MOD_046）倍數改為 Analogy；Train_In C6（SRC_PERF_036）、C7（SRC_PERF_037，選取值）、C11（SRC_MOD_046）、C13（SRC_DEM_001，J10）、C46–C48（SRC_MOD_033，J8）為 Analogy；Train_In C44 為 Derived 待改公式（0.055 對 0.0552）；Har_In 第 48–51 列以 METR（SRC_CAP_012、020、021）為可比；Har_In 第 18、29 列以 SRC_HAR_003、002 為可比。
- 決策 ID 引用：K4、K5、K7、K10、K12、K13、L3、M1、J8、J9、J10、J12、J13、J14、G0-6。
- 機制：`gov_seed2.GOV_MAP_V513C`＋`gov.gm_append_c`：只在（工作表、格）未登錄時附加；該列 A 欄標籤須與登錄時相同，否則停止建置（避免列移動後登錄錯格）。Checks E12 改為全部範圍（切片二 SRC 已存在；全表「不存在」0 筆）；I7 改名「原始數據待連結（尚無 SRC 紀錄）」，I8 改名「標記變更（v5.11 起）」。

**待 Andy（不阻擋；`20261003_v5.13C_待Andy_審閱檔.xlsx`）**
1. **提議區間 16 列**：Cap_In 付費／免費層級組合、Opus 5／5.5 快取價、I53／I56 指數 ±3；Har_In 快取命中變動 0–20 百分點、子代理數、任務長度 ×0.5–×2；Train_In 預訓練 MFU 18%–35%、MFU 世代倍數 ±0.2、rollout 輸入／輸出與評測 token ×0.5–×2。
2. **標記變更 14 列**：例如 Cap_In F50／F51 Interested-party→Assumed（快取價無來源）、Har_In C51 Derived→Analogy（β 為選取值）、Train_In C12 Analogy→Assumed（GRPO 16 無 SRC）。

**驗證**
- LibreOffice 零錯誤；公式 33,317；具名範圍 713；Gov_Map 440→569 列。
- 對 v5.12：模型頁、Interface、L1 數值全部一致。Checks G 節 ERROR 0；WARN 236（W1 203、W2 33：Train_In C6、C7 連 3 級 SRC 且 CC 分段高）；INFO 102（I4 19、I5 12、I6 23、I7 3、I8 39）。
- 冪等 74,281 格（公式與數值）不符 0；以 v5.12 或 B 包中間檔為底稿重建，逐格相同；Excel 優先：改 Gov_Map 新列的判斷欄後重建，保留且不重複附加。
- pycel 33,317 格不符 0（最大相對誤差 4.8e-15）；全簿強制重算本機 1.26–1.57 秒（低於 2 秒）。

**D 包（下一步）**：Arch 21–23 改公式（新增 Assumed 輸入：每層 KV bytes、Astra 混合比例；值須不變）；Arch C9 反推；Checks 外部比對移入 L1（含 CoreWeave 牌價對 L1 GPUhr 列、OpenAI 2025 對帳、最終訓練占研發）；可順帶把 Cap_In N46:N58 改公式（值不變）。

## 8o. v5.13 D 包（模型邏輯）結果（2026-10-03，chat 端）

**Andy 決定**：C 包審閱檔「all ok」（2026-10-03）。C 包 16 列提議區間的文字改為「Claude 提議，Andy 2026-10-03 確認」；14 列標記變更照登錄。

**做法（數值不變）**
- **Arch 第 21–23 列改公式**：新增「KV 推導輸入」5 列（第 33 列標題、第 34–38 列）：每層 KV bytes/token（Luna／Sol 65，Assumed）、MLA 每層 KV 元素（Astra 576，Analogy SRC_MOD_028）、MLA 層比例（Astra 26%，Assumed）、GQA KV heads（Astra 8，Assumed 結構選擇）、KV 每元素 bytes（＝SRC_HW_055，1）。Luna／Sol＝每層 KV × 層數；Astra 情境 1＝比例 × 576 × 層數 × bytes、情境 2＝576 × 層數 × bytes、情境 3＝KV heads × head_dim × 2 × 層數 × bytes。九格值與 v5.12 相同（浮點完全相等）。
- **Arch C9、C10（原「反推」與 Analogy）**：chat 端 2026-10-03 讀 DeepSeek V4-Flash 官方 config.json（Hugging Face，commit fd53f94）：hidden_size 4096、num_attention_heads 64，補登 SRC_MOD_052、053（1 級、利害關係方，E165）並改連結；值不變。同檔亦確認 SRC_MOD_007、009、010、012、013、014、017（目前 3 級，升級留 Stage 2），並載 compress_ratios（4／128 交替）、num_key_value_heads 1，可供 Luna 每層 KV 結構重算（會改值，Stage 2）。
- **Cap_In N46:N58**：中國廠商旗標改為 `=IF(國別="中國",1,0)`，值不變；Gov_Map 類別改為 Derived（公式）。
- **改公式的舊輸入格**：`build.SNAP_RETIRED`（Arch 第 21–23 列 9 格、Cap_In N 欄 13 格，共 22 格）在 snapshot 後移除，Excel 值記入 gov_log，不還原；restore 以 v5.12 為底稿 1,008 格全數對應（1,030－22），unmatched 0。
- **Checks 外部比對移入 L1**（G9）：L1 新增 7 列（第 30–36 列）：GB200 持有成本對 CoreWeave 隨需牌價（SRC_PRC_001；牌價約 5 倍）、GB300 持有成本對新雲損益兩平租金（SRC_PRC_002；±20% 內）、RL ÷ 預訓練 GPU 小時 Sol（0.32；對 R1 的 0.055）與 Astra（0.97；對 Grok 4 的 1）、最終訓練 ÷ 研發（12.5%；落在 Epoch 9.6%–22.6%）、OpenAI 2025 每 GW 機隊付費營收（10.70；對 13.07 ÷ 平均 GW 1.25＝10.46）、Astra 預訓練算力（6.8e25；對 Grok-3 4.6e26，即 J8 缺口）。RL 兩列區間取 Sens_Train rollout ×0.3／×3。Checks 對應列（第 9、10、33、34、37、43 列）的外部參照改讀 L1 外部欄，F 欄註［→ L1_…］；第 15–18 列樣本外實測值由文字改為連結 SRC_PERF_004、001、002、014。第 34 列外部參照由 0.055（Train_In C44 取整）變為 0.0552（SRC 計算），只在 Checks。
- **未動**：Checks 第 21 列 2.12（由 InferenceX 9,384 tok/s/GPU 與 4.43M tok/s/MW 反推；後者無 SRC 紀錄）、第 35 列 0.01–0.10（交接文件區間）、對帳常數 Hopper 占機隊 0.6（Checks I 欄，Assumed）——列 Stage 2。

**待 Andy（不阻擋；`20261003_v5.13D_待Andy_審閱檔.xlsx`）**：提議區間 2 列：Arch C34:D34 每層 KV bytes 4–128 B（全 HCA 至全 CSA）、Arch E36 MLA 層比例 15%–50%。

**驗證**
- LibreOffice 零錯誤；公式 33,481；Gov_Map 574 列；L1 32 列。
- 對 v5.12：模型頁、Interface、既有 L1 25 列數值全部一致；差異只在文字、新增格、Checks（上述）與治理頁。
- Checks G 節 ERROR 0；WARN 238（W1 205、W2 33）；INFO 97（I3 5、I4 19、I5 1、I6 25、I7 3、I8 40）。
- 冪等 74,711 格不符 0；Excel 優先：改 Arch E36＝0.3、C34＝70 後重建，兩格保留，E21＝17,280、C21＝3,010。
- pycel 33,481 格不符 0；全簿強制重算本機 1.46–1.55 秒。

**E 包（下一步）**：寫回 `20261003_v5.11_待Andy_審閱檔.xlsx`（標記變更 13、區間 19、CV1、原話 10 類；T06、T11、T12 已於 B 包處理）與 D 包審閱檔；若 Andy 尚未回填，延到下一版，不阻擋 v5.13 交付。v5.13 交付時一併準備 CC 第 13 輪指令（builder 15 檔、sheets 加 4 個 SRC 頁、SRC 匯出列數、公式與名稱計數）。

## 8p. v5.13 E 包（寫回 Andy 審閱）結果（2026-10-03，chat 端；部分）

- **C 包審閱檔**：Andy「all ok」，已於 D 包寫回（16 列區間文字改為「Claude 提議，Andy 2026-10-03 確認」）。
- **D 包審閱檔**：Andy「BOTH ok」：Arch C34:D34（每層 KV bytes 4–128 B）、E36（MLA 層比例 15%–50%）改為已確認（Gov_Map M 欄）。對 D 包檔逐格比較 74,711 格，差異只有這 2 格與 README 版本列；LibreOffice 零錯誤；restore 以 v5.12 為底稿 1,008 格全數對應。
- **v5.11 審閱檔（未回填）**：標記變更 13 項、區間 19 項、CV1、原話 10 類；其中 T06、T11、T12 已於 B 包依 S30 恢復 Analogy。寫回位置：Gov_Map O、M、K、L 欄（以 GOV_MAP_UPD 的「仍為舊值才寫」機制）與 Decisions J 欄；CV1 若改定義會動 Spec_Rack 顯示，基準數值不變（v5.11 時已實測）。
- **原話確認後**：交接文件第 2 節縮為決策 ID 清單（G11）。


## 8q. v5.13 E 包（寫回 Andy 審閱）完成（2026-10-03，chat 端）

**Andy 決定**：v5.11 審閱檔「all OK」＝全部依 Claude 建議（內容取自 2026-10-03「Tokenomics更新11-CC11」對話串的審閱檔產生程式）；C 包「all ok」、D 包「BOTH ok」。
**寫回（`gov_seed2.GOV_MAP_UPD_E`、`DEC_UPD`；只在仍為 v5.12 原值時寫入）**
- Gov_Map 95 列 114 欄位：74 格「Claude 提議（v5.11）」區間改為「Claude 提議，Andy 2026-10-03 確認」；R12 輪數下限改為 max(1, ×0.5)（Workload 第 5 列）；R17 快取命中 χ 分任務（聊天 30–70%、代理 70–95%）；R19 Calib C69 Hopper η_p 倍數改為 Derived（待改公式；≈989÷1,979，不另給區間）；標記變更 25 格 O 欄註記「Andy 2026-10-03 同意」（T01–T05、T07–T10、T13）；T06、T11、T12 已於 B 包恢復 Analogy。
- Decisions 98 欄位：原話待確認 83 項 J 欄改「否」；G0-9 文字改為 PUE 改標 Assumed；CV1 選 (a) 維持 4 台 HGX（32 GPU）為一架、狀態改生效；K1、K2、K13 補逐字原話（K1「我們意見」為「我沒意見」之誤）；A1–A8 狀態改「v5.14 建置」；G10 排序文字更新為 v5.12 工程基礎 → v5.13 切片二 → v5.14 Block 6。
- 第 2 節縮為決策 ID 清單（G11）。

**v5.13 交付檔驗證（以 v5.12 為底稿）**
- LibreOffice 零錯誤；公式 33,480；具名範圍 736（SRC 324、L1 96、IF 167、B4 39、B5 24、TR 23、CAL 19、DRV 16、TRN 15、CST 4、GOV 4、IDX 3、CTL 2）；工作表 46（SRC_Perf 之後為 SRC_Price、SRC_Cap、SRC_Harness、SRC_Demand、SRC_Index、Sources_Legacy、DB_Evidence）。
- SRC 紀錄 266：HW 60、DC 13、Model 53、Perf 51、Price 44、Cap 21、Harness 15、Demand 9；DB_Evidence 85；Gov_Map 574；L1 32；Decisions 90（J＝是 0）。
- 對 v5.12 逐格比較 71,141 格：模型頁、Interface 與既有 L1 25 列數值全部一致；差異只在治理頁、SRC、L1 新列、Arch 新輸入列與說明、Checks（外部參照改讀 L1 或 SRC；第 34 列 0.055→0.0552）、README。
- Checks G 節：ERROR 0；WARN 238（W1 205、W2 33）；INFO 99（I1 4、I3 5、I4 19、I5 2、I6 25、I7 3、I8 41）。
- restore：以 v5.12 為底稿 1,008 格全數對應，unmatched 0；22 格舊輸入（Arch 第 21–23 列、Cap_In N 欄）改為公式，Excel 值記入 gov_log。冪等 74,711 格不符 0。
- repo engine（pycel 1.0b30，本機）：33,480 格對 LibreOffice 不符 0（最大相對誤差 4.8e-15）；全簿強制重算 1.34–1.50 秒。

## 8r. CC 第 13 輪指令（v5.13 同步，2026-10-03；PR #12 合併後交給 CC）

```
[Tokenomics 指令] 第 13 輪｜v5.13 同步（切片二）｜2026-10-03
依據：交接文件第 8m–8q 節（Project）、repo docs/builder/Tokenomics_builder_v5.md（Andy 上傳的 v5.13 版）。
前提：PR #12（第 12 輪）已合併；從 master 開新分支。

1. 依 CLAUDE.md 第 4 節同步：
   - model/ 放入 20261003_Tokenomics_v5.13.xlsx（SHA-256 9b76f1e5…6540），v5.12 以 git mv 移到 model/archive/，更新 model/CURRENT。
   - 依 md 的「## <檔名>.py」區塊逐字覆寫 builder/：15 檔（新增 gov_seed2.py）。
   - 驗證：python3 builder/build.py model/archive/20261003_Tokenomics_v5.12.xlsx /tmp/check.xlsx，LibreOffice 重算後與 v5.13 逐格一致；
     restore_log unmatched 0（matched 1,008）；gov_log 列出 22 格「retired input (now formula)」屬預期。另以 v5.13 為底稿重建，冪等 0。
2. tests/parity/scenarios.yaml 期望值：formula_cells 33480；defined_names 736（SRC_ 324、L1_ 96，其餘前綴計數不變）；
   sheets 於 SRC_Perf 之後為 SRC_Price、SRC_Cap、SRC_Harness、SRC_Demand、SRC_Index、Sources_Legacy、DB_Evidence。
   若任何情境或測試把 Arch 第 21–23 列（KV bytes/token）、Arch C9:C10、Cap_In N46:N58 當作輸入改值：這些格 v5.13 起是公式。
   KV 情境改設 Arch 第 34–37 列（每層 KV bytes、MLA 每層元素、MLA 層比例、GQA KV heads），並在報告列出改動；不得改比對範圍與容差。
3. Checks：GOV_Errors 0、GOV_Warnings 238、GOV_Info 99。E12 已擴及全部範圍。
4. 工具與 app：
   - tools/export_csv.py 的 SRC 匯出加 4 頁（Price 44、Cap 21、Harness 15、Demand 9；Model 53、Perf 51）；tools/stage0_inventory.py 的治理頁清單加這 4 頁。
   - app：SRC 頁清單加 4 頁；L1 由 25 列增為 32 列（第 30–36 列為 Checks 移入的外部比對）；IDX_、CST_ 仍不顯示為下游名稱。數值與機制不改。
5. 重算時間：全簿 < 2 秒、增量 < 2 秒；報告 CI 實測秒數（chat 端本機全簿 1.34–1.50 秒）。
6. 發現 Excel 問題時依第 4 節第 5 點列在 PR，不在 Python 修補。
7. CHANGELOG、docs/reports/20261003_v5.13_sync.md、PR；回報 GitHub Actions 結果（parity 項數、情境數、兩條重算測試、export_csv 的 GOV_Errors 與各 SRC 頁列數）。
   本輪屬同步，不改 Excel。
```

## 8s. CC 第 13 輪（v5.13 同步）驗收與 v5.14（2026-10-04，chat 端）

**依據**：CC 報告 `docs/reports/20261003_v5.13_sync.md`（分支 `claude/dazzling-franklin-iz90ak`，最新提交 cd8340fa）、PR #13 頁、Actions 頁，與 chat 端獨立重建。
- **repo 狀態**：PR #12 已合併（a466307）；Andy 已把 v5.13 Excel（7597a0f）與 builder md（78473da）上傳 master；PR #13 未合併，parity 第 79、80 次 CI 失敗（與 CC 本機結果一致：2 項）。
- **一致項（chat 端核對與交付數字相同）**：v5.13 SHA-256 9b76f1e5…6540；以 v5.12 重建 61,184 格不符 0；restore matched 1,008、unmatched 0、retired 22；公式 33,480、名稱 736、46 頁；GOV 0／238／99；export_csv SRC 八頁列數相符；網站 13 項全過；CC 改動限於 CHANGELOG、報告、測試期望值、tools 與 app 的 SRC 頁清單（diff 已逐檔核對，數值與機制未改）。branch 的 builder 15 檔與 master md 逐字相同。
- **失敗 2 項（CC 判斷正確，屬 chat 端 v5.13 的缺陷）**：b_prod_derate、f_registry_t07_t09_on 下 L1!O35、P35 為錯誤值。原因：D 包把 Checks 對帳列移入 L1 時，L1_RevGWFleet_OAI2025 的 D 欄連到 Checks!B43，而 B43 在 SLO 不可達時回傳文字；L1 的 O、P 模板只檢查 M、N。chat 端 v5.13 驗證只跑基準與 Excel 優先測試，未跑 parity 的 17 個情境，所以沒抓到。**今後 chat 端交付前，凡新增或改動可能回傳文字的連結，至少用 LibreOffice 跑 b_prod_derate 與 f_registry_t07_t09_on 兩個情境確認零錯誤值。**
- **CC 回報的「冪等公式原始文字 3,895 格不同」**：chat 端重現為 3,959 格（含 v5.14 修改的 L1 64 格，扣除後 3,895 格），全部是 builder 直接輸出（如 `/1E9`）與 LibreOffice 存檔（展開為 `/1000000000`）的數字常數寫法差異；兩邊皆經 LibreOffice 存檔再比，公式文字不符 0。不是問題，已在 builder md 驗證紀錄註明比較方法。
- **v5.14 修正一（錯誤值，工程類，chat 端定案）**：L1 全部 32 列 O 欄改為 `IF(AND(ISNUMBER(D),ISNUMBER(M),ISNUMBER(N)), D/((M+N)/2), "—")`；P 欄外層加 `IF(ISNUMBER(D), 原判讀, "推算值非數字（本情境）")`。套用全部列而非只改第 35 列：模板統一，日後新增 L1 列的 D 欄若可能為文字也不會再犯。
- **v5.14 修正二（重算時間，工程類，chat 端定案）**：chat 端這台機器上 v5.13 全簿重算 2.44–2.71 秒，表示門檻餘裕已不足（與機器快慢有關）。逐頁計時：SRC 各頁 X 欄（同指標鍵的陣列比對，每筆比 396 列）約 1.05 秒、Gov_Map AF 約 0.42 秒，模型頁合計很小。X 欄的比對範圍改為第 5 列到最後一筆紀錄＋50 列（與 SRC_Index 共用 `gov._span_end`）；超出此範圍的紀錄本來就由 Checks E13 報錯（重建即可），所以計數不變。未採用 COUNTIF：SRC_Perf 的同指標鍵含「~」（原文「~73.7k」），COUNTIF／MATCH 會把 ~、*、? 當萬用字元，結果可能不同。
- **v5.14 驗證（以 v5.13 為底稿）**：LibreOffice 零錯誤；公式 33,480、名稱 736、46 頁；GOV 0／238／99。對 v5.13 逐格 74,711 格：數值差異只有 README!B5、L1!A2；公式文字差異 332 格（L1 O、P 64 格、SRC X 266 格與上述 2 格）。restore matched 936、unmatched 0；冪等 0 不符。E7 偵測測試：SRC_HW 第 6 列指標、口徑、對象改成與第 5 列相同 → X5、X6＝2、E7＝2、GOV_Errors＝2。全簿重算（同一台機器）v5.13 2.44–2.71 秒 → v5.14 1.68–1.76 秒；剖析後剩餘最大項為 Gov_Map AF（約 0.44 秒）。
- **repo parity（chat 端本機，pycel 1.0b30，v5.14 為 CURRENT）**：9 項全過——CURRENT、工作表期望值、具名範圍、名稱對 LibreOffice、情境 base、b_prod_derate、f_registry_t07_t09_on、增量重算、全簿重算（< 2 秒）。其餘 16 個情境與函數語意測試未在本機跑（本機 15 分鐘跑 9 項，全套估計超過一小時），由 CC 與 CI 跑全套。

## 8t. CC 第 13 輪續做指令（v5.14 同步，2026-10-04；在 PR #13 同一分支）

```
[Tokenomics 指令] 第 13 輪續｜v5.14 同步（L1 錯誤值修正）｜2026-10-04
依據：交接文件第 8s 節（Project）、repo docs/builder/Tokenomics_builder_v5.md（Andy 上傳的 v5.14 版）。
前提：Andy 已把 20261004_Tokenomics_v5.14.xlsx 上傳到 master 的 model/，builder md 已取代。PR #13 不先合併。

1. 在分支 claude/dazzling-franklin-iz90ak 合併（或 rebase）最新 master，續用 PR #13：
   - model/ 放 20261004_Tokenomics_v5.14.xlsx（SHA-256 dc4ef406…2b56），v5.13 以 git mv 移到 model/archive/，更新 model/CURRENT。
     model/ 只能留一份 xlsx。
   - 依 md 的「## <檔名>.py」區塊逐字覆寫 builder/（15 檔；只有 gov.py、finish.py 有變動：L1 的 O、P 欄，與 SRC 各頁 X 欄的比對範圍）。
   - 驗證：python3 builder/build.py model/archive/20261003_Tokenomics_v5.13.xlsx /tmp/check.xlsx，LibreOffice 重算後與 v5.14 逐格一致
     （README 除外）；restore_log matched 936、unmatched 0。冪等：以 v5.14 為底稿重建，兩邊都經 LibreOffice 重算存檔後再比公式文字
     （builder 直接輸出會把 1E9 等寫成科學記號，與 LibreOffice 存檔寫法不同，這不是不一致）。
2. tests/parity/scenarios.yaml 期望值不變（公式 33,480、名稱 736、46 頁）。parity 127 項須全過，含 b_prod_derate、f_registry_t07_t09_on 的
   「錯誤值 0」閘門。不得改情境、比對範圍或容差。
3. Checks：GOV_Errors 0、GOV_Warnings 238、GOV_Info 99（不變）。
4. 網站：L1 的 O、P 欄在 SLO 不可達情境顯示「—」與「推算值非數字（本情境）」（chat 端查過 app 與 tests 沒有寫死 P 欄判讀文字）。數值與機制不改。
5. 重算時間：全簿 < 2 秒、增量 < 2 秒。v5.14 縮小 SRC X 欄範圍（chat 端同機 v5.13 2.44–2.71 秒 → v5.14 1.68–1.76 秒），
   請報告本機與 CI 實測秒數，並與第 13 輪本機 1.76 秒比較。
   若 CI 讀不到秒數，在 workflow 的 pytest 加 -rA 或把 results_store 寫入 job summary，屬測試輸出改動，不改斷言。
6. CHANGELOG 加 v5.14 一節（v5.13 一節保留，註明 v5.13 未單獨合併、與 v5.14 同一 PR）；報告 docs/reports/20261004_v5.14_sync.md。
7. 回報 GitHub Actions 結果（parity 項數、18 情境、兩條重算測試秒數、export_csv 的 GOV_Errors 與各 SRC 頁列數）。本輪屬同步，不改 Excel。
```

## 8u. v5.15 工作單：需求 D 的來源與 Block 6 規格（2026-10-04，chat 端）

**網路搜尋結果（2026-10-04）**：沒有 ChatGPT 端的 token 量揭露。新資訊：
- OpenAI 2026-03-31 融資公告：API 每分鐘超過 150 億 token（2025-10 為 60 億）；企業營收超過四成。利害關係方，原文未取得，先以二手登錄。
- ChatGPT 每日提示 25 億則（OpenAI 告知 Axios，2025-07）；之後無更新的官方則數。2026-08 每週用戶 10 億。
- Epoch AI 由算力推估前沿實驗室（OpenAI）每天 10–100 兆 token（中立）。
- 粗算閉合：2.5B 則 × 2,000 token ≈ 5 兆／日，加 API 8.6 兆／日 ≈ 14 兆，落在 Epoch 區間低端。

**決定（Andy 2026-10-04）**：
- A9：D 採 token 路線為基準、支出路線並列對照（(c)）；ChatGPT token＝每日提示數（SRC）× 每則 token 數；2,628T（OpenAI 模型 v0.5 推導值）不進 Source。原話：「D: 先做網路搜索，看看有沒有新的資訊，若無:(c)」。
- A10：每則提示 token 數基準 2,000、區間 1,000–6,000，Assumed，Q1 的最弱輸入。原話：「我沒意見，請繼續」。
- 基準年 2025（與支出資料、59% 校準值同年）；API 全年平均＝10 月時點 × 比例 0.75（0.6–0.9，Assumed）。
- 另新增輸入：ChatGPT token 免費占比 0.6（0.4–0.8，Assumed），以支出口徑免費占比（SRC_DEM_005 ÷ 004，約 46%）作 L1 對照。

**工作單**：`20261004_v5.15.md`（A：CLAUDE.md 修訂五；B：SRC_DEM_010–013、Alloc_In、Alloc、Interface F 節、L1 Answers 9 題與對照 3 列、網站問答頁、parity 新增 4 情境、預期變動範圍、待 Project 判斷清單）。

## 8v. CI 等待時間與提速（2026-10-04，工程類，chat 端定案）

**問題（Andy 2026-10-04）**：parity CI 一次 42–47 分鐘，期間 chat 端與 CC 都在等。
**原因**：18 個情境各自重新建 pycel 引擎（每次 44–50 秒），另加每個情境一次 LibreOffice 重算；第 12 輪試過以 deepcopy 共用引擎，複本偶發錯誤且重算變慢，未採用。
**定案**：
1. **流程**：CI 只作合併門檻，不作工作的等待點。CC 推出報告後 chat 端立即審查（審查不需 CI 結果）；CI 期間 CC 可在新分支續做下一份工作單（以未合併分支為底時，在報告註明依賴的 PR）。CI 失敗時，修正一律在原 PR 處理。
2. **提速（CC 執行，不改比對範圍、容差與情境）**：
   - 分片並行：GitHub Actions matrix 把情境分到多個 job（目標 6 片），結構性測試與兩條重算測試另成一個 job；合併門檻為全部 job 通過。
   - 引擎編譯快取：以 pycel 的序列化（`ExcelCompiler.to_file`／`from_file`）在 CI 內建一次、各情境從檔案載入新實例（每個情境仍是獨立實例，與 deepcopy 不同）；須先證明載入的實例在 18 情境結果與重新建置逐格相同，否則不採用。
   - 目標：CI 牆鐘時間 ≤ 15 分鐘；報告前後時間。

**交給 CC 的指令（可在 v5.15 工作單執行前或期間做；獨立 PR）**
```
[Tokenomics 指令] CI 提速｜工程類（CC 執行）｜2026-10-04
目的：parity CI 由約 45 分鐘降到 ≤ 15 分鐘；不得改比對範圍、容差、情境與斷言。
1. Actions matrix 分片：情境分 6 片並行；結構性測試（工作表、名稱、CURRENT、函數語意）與兩條重算測試另成一個 job。
   合併門檻＝全部 job 通過；各 job 的結果與重算秒數寫入 job summary。
2. 評估 pycel 序列化快取（ExcelCompiler.to_file／from_file）：每個情境從檔案載入獨立實例。
   先跑 18 情境，與重新建置的結果逐格比較（不符 0 才可採用）；不符或偶發錯誤則不採用，報告原因。
3. 報告 docs/reports/YYYYMMDD_ci_speedup.md：前後牆鐘時間、各 job 時間、快取是否採用。獨立 PR，合併前請 Andy 確認。
4. 之後的規則：推出報告後即通知（PR comment），不必等 CI；CI 期間可在新分支續做下一份工作單，報告註明依賴的 PR。
```

## 8w. PR #13（v5.14 同步）審查與 v5.15 工作單 r2（2026-10-04，chat 端）

**repo 狀態（chat 端 git ls-remote 與 raw 核對）**：PR #13 未合併（head `1a939472`，有 `refs/pull/13/merge`）；master `3b6d47d`，`CURRENT` 仍為 v5.12（Andy 上傳的 v5.13、v5.14 Excel 在 master，CURRENT 由 PR #13 改為 v5.14）；工作單初版在 master；master CLAUDE.md 仍為修訂四。
**PR #13 審查（報告 `docs/reports/20261004_v5.14_sync.md`）**：第 8t 節 7 項逐項對照，通過。以 v5.13 重建對 v5.14 61,184 格不符 0；restore 936／0；冪等 61,715 格不符 0；公式 33,480、名稱 736、46 頁；GOV 0／238／99；parity 本機 127 項全過，CI 在 `ba37475` 127 項全過（2,534 秒）；網站 13 項；重算本機全簿 1.44 秒、增量 0.59 秒（第 13 輪 1.76／0.86）。未完成：CI 重算秒數（workflow 已加 job summary）、CI 在最新提交的結果。兩者為合併前程序條件，不需回到 CC 修改。
**v5.15 工作單 r2（交付前審查）**：
- 工程類（chat 端定案）：開工前核對 CURRENT＝v5.14；敏感度表以閉式公式重寫推導鏈（不得用運算列表或 Python），每列附自我檢查；Checks 新增 H 節（世代組合合計 100%、敏感度自我檢查，計入 GOV_Errors）；授權更新 parity 結構期望值（46 → 48 頁、公式與名稱計數、SRC_Demand export 10 → 14 列）；B9 允許範圍補 Gov_Map AF（若優化）、Checks H 節、測試檔。
- 判斷類（Andy 2026-10-04 決定）：ChatGPT 2025-07 每日提示數為年中時點值，視同全年平均，不另設輸入；理由寫入 SRC_DEM_012 的 Gov_Map 理由欄，標記 Assumed。原話：「(a) 保留，Gov_Map 写明理由（建议）」。
- 審查預期：每日 token 合計基準約 11.5T（API 6.48T＋ChatGPT 5.00T），略高於 Epoch 下限 10T；低端（比例 0.6、每則 1,000）約 7.7T 落在區間外，高端（0.9、6,000）約 22.8T。對照列區間外屬預期，不是缺陷。

## 9. Block 4 需要的材料（已完成，保留紀錄）

- 下游訓練成本連結具名範圍（* ＝ Luna／Sol／Astra；欄＝世代 × 成本情境）：IF_TrainGPUh_*、IF_TrainCost_*、IF_PostShareFLOP_*、IF_PostShareGPUh_*、IF_RLMFU_*、IF_ProgGPUh_*、IF_ProgCost_*、IF_ProgGWyr_*，以及 IF_RDMult、IF_TrainGenDefault、IF_TrainGenAlt、IF_TrainGenDefaultName、IF_TrainGenAltName。
- 顯示用具名範圍（網站推導鏈，下游不得連結）：TRN_Gen、TRN_Tier、TRN_FlopTokPre、TRN_FlopPre、TRN_GPUhPre、TRN_GPUhRL、TRN_RLMFU、TRN_RLRatioH、TRN_RLRatioF、TRN_GPUhFinal、TRN_PostShareF、TRN_PostShareH、TRN_InferShare、TRN_GPUhProg、TRN_GWyrProg；Tech_Registry 唯讀表：TR_ID、TR_Tech、TR_Hook、TR_Acts、TR_Lo、TR_Base、TR_Hi、TR_Sel、TR_Status、TR_Labs、TR_Main、TR_Override、TR_InBase、TR_Adopt、TR_Switch、TR_Eff、TR_Tag、TR_Source、TR_Trigger、TR_Check、TR_HookCode、TR_HookName、TR_HookVal。
- Block 4 需處理：研發計畫成本 ÷ 模型商業壽命內服務 token → 每 M token 攤提；能力增量掛鉤 H_CAP；1 GW 機隊參考配置（對外服務付費／免費、訓練、研發）；快取儲存成本（Block 2 未結 4）。
- J8 的差距應在 Block 4 以能力錨點（例如同代前沿模型的評測分數對算力）檢驗。

## 9a. Block 5 與 OpenAI v0.6 需要的材料

- 下游連結具名範圍（Block 4；* ＝ Luna／Sol／Astra）：單一格 IF_PriceFresh_*、IF_PriceCached_*、IF_PriceThink_*、IF_PriceOut_*、IF_PriceRef_*、IF_FrontRef_*、IF_FrontModel_*（文字）、IF_Life_*、IF_ServeShare、IF_FreeShare；15 欄（世代 × 成本情境）IF_CacheStore_*、IF_AmortBU_*、IF_AmortTD_*、IF_FullCost_*、IF_RevGW_*、IF_RevGWFront_*、IF_RevGWFleet、IF_RevGWFleetFront。
- B4_ 具名範圍（38 個）只供 Block 4 公式內部引用與網站顯示，下游不得連結。
- Block 5（v5.9 已建）：harness 能力增量不經 H_CAP／ε 進單價，改經成功率進每成功任務成本。OpenAI v0.6：攤提連結 IF_AmortDefault_*／IF_FullCostDefault_*；每任務 token 與成功率連結 Interface E 節（IF_TaskTok*、IF_TaskSucc_*、IF_CostSuccVR_*、IF_HarR_*）；機隊營收用 IF_RevGWFleet_* 拆解。
- Block 5 v5.10 增列（下游可連結）：IF_CostAttVR_*、IF_HzEff_*（5 欄）、IF_PFloor（單格）、IF_FrontSuccVR、IF_FrontSuccVRName、IF_FrontSuccVRP（5 欄；無合格時為文字）。
- CC 第 9 輪：已驗收（第 8e 節），待 CI 綠燈合併。CC 第 8 輪：已驗收並合併。
- OpenAI v0.6 另需：Block 6 依用途拆分的算力與算力成本（v5.14 的 IF_ 名稱，待建），並承接 Q3；原始數據改取 Source（G8）。
- CC 第 7 輪（已完成，見第 8c 節）：新函數 MATCH；公式 18,596 格、具名範圍 228 個；新頁 8 張；Checks 的 OpenAI 對帳常數在 Checks I 欄（非藍字重建頁，由 builder 寫入）。

## 10. 過去的 Block 3 準備材料（已完成，保留紀錄）

- Perf 引擎可直接重用於推論型訓練運算（rollout、合成資料、評測）：rollout 為高批次、低互動性的 decode，可用 Sens_Perf 的 SLO 情境延伸。
- 反向傳播型運算需新增訓練 MFU（預訓練約 0.15–0.35、RL 約 0.01–0.10，交接第 3 節），以 Spec_Rack 峰值與 DC_Cost 每 GPU 小時成本計價。
- Tech_Registry 掛鉤已預留：Perf 的 η_d 情境倍數、每層延遲情境倍數，以及 Arch／Serving 的藍字輸入。
- CC 同步（v5.4）：下游連結用具名範圍 IF_TokRack_*、IF_TokRackD_*、IF_TokGW_*、IF_VReq_*、IF_CostPre_*、IF_CostCache_*、IF_CostDec_*、IF_CostDecAcct_*、IF_TokPerJ_*（* ＝ Luna／Sol／Astra）與 IF_Util；parity 測試需涵蓋 Interface 全部格。
- OpenAI v0.6：〈輸入〉列 71–94、136–143 改連結上述 IF_ 名稱（對照見 Block 2 命題回覆第六節）。

## 11. 資料架構與治理（2026-10-02 定案）

**完整規劃**：repo `docs/plan/Tokenomics_governance_plan.md`（v0.3）。決策編號 G1–G12 見第 2 節。

**起因**：Andy 提供一份外部《Tokenomics 從 MVP 到理想完整版規劃建議書》，請 Claude 評估後自擬規劃。評估結論：建議書的方向（風險導向、stage gate、資料分層、「改一個參數能追出完整影響」的驗收測試）可用；但它假設工程基礎最後才建，而本 Project 已有可重現引擎、parity、CI、git 與 Interface，真正缺的是第 0 層 Source。v0.1 偏差過大作廢；v0.2 以 Andy 的架構說明為主幹；v0.3 補上第 1 層 L1 後定案。

**架構**：DB_Evidence（所有新訊息入口）→ 擇優 → SRC_*（第 0 層，原始訊息）→ 模型頁（Block 1–6）→ Checks（完整性＋佇列）→ L1（常用推算值，含 Answers 與外部對照）／Interface（推算構件）→ 下游。

**v5.10 起點量測**
- 藍字輸入 324 列：同列有標記 71%、有來源編號 35%（下限估計）；標記分布 Assumed 97、Verified 52、Interested-party 35、Analogy 34、Decision 11、Derived 2，未標記 93。
- Sources 61 筆：0 格數值（全為文字摘要），約 29 筆待查核、16 筆二手、5 筆模型內建知識；全簿沒有任何公式引用 Sources 或 DB_Evidence。
- Checks 外部參照寫死 45 格、公式 14 格。DB_Evidence 20 筆。決策 63 項只在本文件。
- 溯源：1 GW VR200 建置成本 23 公式格、16 個輸入；1 GW VR200 Sol 理論營收 1,189 公式格、最多 290 個輸入（G9 的依據）。

**階段與驗收**
- Stage 0：唯讀盤點（2026-10-02 完成；Gate 0 全部核准，見 G14）。
- Stage 1：切片一 v5.11 已交付（第 8h 節），待 CC 第 11 輪同步與 Gate 1 驗收；切片二 v5.13（v5.12 為工程基礎）。SRC 上線、數值逐格不變。Gate 1＝parity 逐格一致；原始數據寫死在模型頁 0 格；每筆 Active SRC 有 Evidence ID；Checks ERROR 0；改 SRC_HW 的 VR200 FP8 訓練峰值，Checks 與 CC 差異報告列出的受影響範圍完全一致。
- Stage 2：依敏感度排序查核，load-bearing 參數所連 SRC 不得為 3 級；Andy 待給值（J6 利用率、生產折減）以 A 級寫入。
- Stage 3：Interface、SRC_ID、L1_ 契約（已發布名稱不改義，改定義另立新名、舊名標 Deprecated）；下游使用登錄；OpenAI v0.6、CRWV 改接；下游覆蓋矩陣。
- Stage 4 以後（多 AI 分工、外部資料庫、發布包）：只在觸發條件成立時建。

**下游可引用的新名稱（v5.11）**：`SRC_xxx_nnn`（只取 Active；`_Lo`、`_Hi`，SRC_Perf 另有 `_ISL`、`_OSL`、`_Spd`、`_MTP`）；`L1_<鍵>`、`L1_<鍵>_Lo`、`L1_<鍵>_Hi`（25 列，見 L1 頁 Q 欄）；`GOV_Errors`、`GOV_Warnings`、`GOV_Info` 只供 CI 與網站。

**版本規則**：只新增 Evidence → 修補版（v5.x.y）；SRC Active 值或公式改變 → 次版；指標定義或 IF_／SRC_／L1_ 契約改變 → 主版。


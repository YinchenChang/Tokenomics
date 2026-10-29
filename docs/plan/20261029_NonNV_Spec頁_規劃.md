# NonNV_Spec 頁規劃（2026-10-29；規劃，尚未執行）

> Andy 2026-10-29 21:18：「好，就先新增一頁，然後把它把規劃做出來就好。今天就先不去把它完整做出來。」
> 本檔是規劃，不是工作單；建置前另寫 `docs/workorders/<日期>_v<版>.md`，數值以屆時重新逐格核對的證據為準。

## 1. 為什麼要這一頁
- NVIDIA 各代的單顆規格（各精度峰值、HBM 容量與頻寬、互連、功率、機架功率與價格）在 `Spec_Rack` 頁，是 roofline 推導的輸入。
- 非 NVIDIA 七種晶片在主模型只有兩個比例（`NonNV` 頁：每 GW 產出比、持有比，相對 VR200）。單顆規格散在四個證據資料夾：
  `docs/evidence/20261023_NonNV昇騰Maia_A段/`、`20261025_NonNV_AMD/`、`20261025_NonNV_TPU_Trainium/`、`20261025_NonNV_Cerebras_OpenAI/`。
- 因此：(1) 無法檢查產出比是否被 HBM 頻寬限制；(2) 精度口徑 Q1 的影響看不到全貌；(3) Wattonomics v0.2（C2 晶片顆數）需要的「每顆功率」「每 GW 顆數」沒有主模型來源。

## 2. 頁面設計（階段 1：只顯示與核對，不改任何既有數值）
**欄：** VR200（參照欄，公式讀 `Spec_Rack` F 欄，不另抄）＋七種晶片，順序同 `NonNV` 頁第 5–11 列：AMD MI455X（Helios）、Google TPU v7 Ironwood、AWS Trainium3、Cerebras WSE-3、OpenAI／Broadcom 客製（Jalapeño）、華為昇騰 910C（CloudMatrix 384）、Microsoft Maia 200。

**列（對齊 Spec_Rack 欄位，每格三件：值、標記、來源 ID）：**
| 區 | 列 | 說明 |
|---|---|---|
| A 平台 | 平台／機架形式、封裝數／架、scale-up 域顆數、冷卻、量產時點 | 文字或數字 |
| B 功率與價格 | 晶片功率 W、機架功率 低／基準／高 kW、機架價格 低／基準／高 $M（買方取得價口徑，見 §4 規則 3） | 輸入 |
| C 算力 | 最高原生精度；FP4（含 MXFP4）、FP8、BF16／FP16 峰值 PF；各值是否標 dense | 輸入；未標 dense 的格標註 |
| D 記憶體 | 記憶體類型（HBM 世代或 SRAM）、容量 GB、頻寬 TB/s | 輸入 |
| E 衍生（公式） | 每 kW 峰值（最高原生精度、FP8 對齊兩口徑）及其對 VR200 比；ridge point（FLOP/byte）；每 kW HBM 頻寬及其對 VR200 比；每 GW 顆數＝919.8 MW IT ÷（機架功率 ÷ 封裝數） | 只讀本頁與 Spec_Rack |
| F 對照 | `NonNV` 頁現行產出比、持有比（讀取，不改）；由本頁 E 區重現的「每 kW 峰值比」與證據檔推導值的差 | Checks 用 |

**不做：** 本頁不被任何計算頁讀取；`NonNV` 頁產出比、持有比不改；roofline 不套用到非 NVIDIA（屬階段 2）。

## 3. 已有資料與缺口（依證據原稿檢索；建置前須逐格對原稿與來源再核一次）
| 晶片 | 算力 | 記憶體 | 功率 | 缺口 |
|---|---|---|---|---|
| AMD MI455X | MXFP4 40.27、FP8 20.13、FP16 5.03 PF（dense） | HBM4 432 GB、23.3 TB/s | 有機架功率與價格推導 | 少 |
| OpenAI Jalapeño | MXFP4 13.4（未標 dense）、FP8 dense 3.4 PF | HBM4 216 GB、15.4 TB/s | TDP 700 W（實測 ≤550 W） | 機架功率、dense 讀法 |
| TPU v7 | FP8 dense 4.6 PF（無 FP4） | 192 GB、7.37 TB/s | 依每 kW 設備價推導 | 晶片功率一手來源 |
| Trainium3 | FP8＝MXFP4 2.52 PF | 未見 | 約 1,000 W | HBM 容量、頻寬 |
| Maia 200 | FP8 5.07 PF | 原稿有用於價格推算，頻寬未見 | 750 W；機架 64 kW（單一轉述） | HBM 頻寬 |
| 昇騰 910C | 不完整（定性：7nm、無 FP4） | HBM2e（數字未見） | CM384 整機約 559 kW（第三方） | 各精度峰值、HBM 數字 |
| Cerebras WSE-3 | FP16 dense 12.5 PF（廠商只公布 sparse 125） | 44 GB SRAM、21.6 PB/s，無 HBM | CS-3 每台 23 kW | 不適用 roofline，D 區另註 |

補資料方式：先 WebSearch／WebFetch 官方規格頁（官方規格表免第二來源，§4 規則 4），不用 API；SemiAnalysis／InferenceX 只作佐證。

## 4. 規則（沿用現行固定規格）
1. 每格標記 Verified／Interested-party／Analogy／Assumed／Derived；Analogy、Assumed 給區間。
2. 精度以「各晶片最高原生精度」為主列、「FP8 對齊」為對照列（Q1 未定案前兩者並陳）。
3. 外部絕對價格須與 TK VR200 買方取得價（Spec_Rack F12）同口徑；不明時用同源比值 × TK 價（#174）。
4. 官方規格頁、官方規格表免第二來源；公司自揭用量、營收類仍需第二來源。
5. 新來源登錄 `SRC_HW_`，Gov_Map 登記具名範圍。

## 5. 建置與驗收（階段 1）
- 版本：併入下一版 TK（Q1 定案那一版）；若 Wattonomics v0.2 先需要，單獨出 v21.8。
- 預期變動：既有格數值 0 變動；只新增一頁、具名範圍與 `SRC_HW_` 列。
- 具名範圍增加 → 合併前跑 `python -m pytest tests/app` 與全套 parity。
- 新增 Checks（只警告）：E 區每 kW 峰值比重現值與證據檔推導值相差 >1%。
- 未參與代理逐格對證據原稿與來源核對；閱讀版核對程式照跑（預期不受影響）。

## 6. 階段 2（Q1 定案後另議）
- 是否讓 `NonNV` 產出比改由「min（算力上限，HBM 頻寬上限）× f」推導，取代現行「每 kW 峰值比 × f」。
- 是否把 E 區「每 GW 顆數」「晶片功率」開成 Interface 契約名稱，供 Wattonomics C2、Siliconomics 讀取。

## 7. 判斷題（附預設）
| 題 | 預設 |
|---|---|
| J1 階段 1 是否同時開 Interface 契約名稱（`IF_NonNV_ChipW_*`、`IF_NonNV_ChipsPerGW_*`） | 不開；等 Wattonomics v0.2 動工時與階段 2 一起開（避免契約先上、值後改） |
| J2 VR200 參照欄要不要也放 GB300 | 只放 VR200（NonNV 比例的基準） |
| J3 昇騰缺峰值時是否用第三方估計填 | 填，標 Interested-party 或 Analogy 並給區間；查不到就留空並標「未找到」 |
| J4 Cerebras 是否放進 roofline 欄 | 放規格、衍生區標「不適用」 |

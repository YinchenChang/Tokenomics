# Tokenomics v5 建檔程式（v5.9 產生器：Block 2＋Block 3＋Block 4＋Block 5；Excel 優先）

用途：Block 2、Block 3、Block 4、Block 5 的公式頁由程式產生，確保公式一致、可重建。**v5.7 起輸入值由 Excel 擁有**：要改輸入，直接改 Excel（藍字格）；builder 重建時會讀回所有藍字輸入。程式內的數值只是「新增輸入列時的預設值」。

還原步驟：
1. 取得最新程式與 Excel（2026-10-01 起以 repo 為準）：
   - 程式：repo `builder/` 各檔，或本檔（repo 內位於 `docs/builder/Tokenomics_builder_v5.md`）；以 Python 解析本檔 ```python 區塊，依標題檔名寫入 `/home/claude/b2/`。
   - Excel：讀 `https://raw.githubusercontent.com/YinchenChang/Tokenomics/master/model/CURRENT` 取得現行檔名，再下載 `model/<檔名>`。
2. 執行 `python3 build.py <底稿.xlsx> <輸出.xlsx>`（v5.7 起路徑以參數傳入，不再寫死在程式中）；`restore_log.txt` 與 `rows.json` 寫在輸出檔同一資料夾。
3. `build.py` 流程：(1) `preserve.snapshot` 讀取 Block 2、3、4、5 各頁與 Spec_Rack 第 21 列以下所有藍字輸入，以「工作表＋欄 A 標籤（含重複序號）＋欄位」為鍵；(2) 刪除並重建 Block 2、3、4、5 各頁，清除 Interface 第 17 列、Checks 第 12 列、Sources 第 23 列、README 第 4 列以下；(3) `preserve.restore` 把 Excel 的輸入值寫回，並輸出 `restore_log.txt`（列出 Excel 值與程式預設不同的格、以及找不到對應的輸入）；(4) `DB_Evidence` 只在不存在時建立，之後不覆寫。Block 1 其餘內容與 12 個 Block 1 具名範圍保留。
4. 執行 `python3 build.py`，再以 `/mnt/skills/public/xlsx/scripts/recalc.py` 重算，須為零錯誤；檢查 restore_log 的「unmatched」應為 0，若不為 0，代表有輸入列改名或刪除，需逐筆確認。

修改輸入的方式（v5.7 起）：
- 改既有輸入：直接改 Excel（或在 chat 端以 openpyxl 改 Excel 後重建），不要改程式中的預設值。
- 新增輸入列：在程式中加列並給預設值；重建後該列取程式預設。
- 改列標籤（欄 A）：會使該列失去對應，restore_log 會列為 unmatched；改標籤時須同步確認數值。

驗證紀錄：
- v5.5（2026-09-30）：公式 16,245 格；具名範圍 117 個。Block 2 Hopper 欄對 v5.4 差異 0.0505–0.0506%（Andy 接受，門檻 0.06%）。
- v5.6（2026-10-01）：公式 16,251 格；具名範圍 142 個。Block 1、2 與 v5.5 逐格一致。
- v5.7 builder 參數化（2026-10-01）：以 repo master 的 v5.7 為底稿重建，與 repo 檔逐格一致（20,539 格不符 0；repo 檔與 chat 交付檔位元組完全相同）。
- v5.7（2026-10-01，以 v5.6 為底稿）：公式 16,251 格、零錯誤；具名範圍 144 個（＋IF_TrainGenDefaultName、IF_TrainGenAltName）。藍字輸入 770 格全數對應、Excel 與程式預設差異 0 格；除 README 與新頁 DB_Evidence 外，對 v5.6 逐格一致（20,391 格不符 0）。Excel 優先測試：在 Excel 改 Train_In rollout 效率 0.85→0.8、Arch!E20 2→3、DB_Evidence 新增一列，重建後三者皆保留。冪等：以 v5.7 重跑 20,539 格不符 0。
- v5.8（2026-10-01，以 v5.7 為底稿）：新增 `block4.py`（Cap_In、Capability、Price_Frontier、Cache_Store、Fleet_1GW、Amortize、Theory_Rev、Sens_Rev；Interface D 節、Checks Block 4、Sources S50–S57、DB_Evidence E010–E015）。公式 18,596 格、LibreOffice 重算零錯誤；具名範圍 228 個（IF_ 115、B4_ 38）。Block 1–3 與 v5.7 逐格一致（20,501 格不符 0；唯一差異為 Interface C50 占位文字改為指向 D 節）。藍字輸入 770 格全數對應；新增輸入 220 格。冪等：以 v5.8 重建 24,093 格不符 0。新函數：MATCH（Price_Frontier 前緣模型查找）。DB_Evidence 為 Excel 擁有，E010–E015 由 `evidence_b4` 只在 ID 不存在時附加。
- v5.9（2026-10-01，以 v5.8 為底稿）：新增 `block5.py`（Har_In、Harness、Sens_Har；Interface E 節、Checks Block 5、Sources S58–S61、DB_Evidence E016–E020）；`outputs.workload` 改為 harness 參數組（新增列 14 歷史保留比與有效參數 B 節，列號下移，回傳列號供 Theory_Rev C 節使用）；`block4.py` 補 SLO 不可達保護（Fleet_1GW、Amortize、Theory_Rev、Checks）、K6 (c)／(d) 與 IF_AmortDefault_*／IF_AmortRev_*／IF_FullCostDefault_*、機隊層級貢獻列 IF_RevGWFleet_*／IF_RevGWFleetFront_*、Cap_In F 節中國廠商旗標欄（B4_MktChina）、B4_Chi 改名 B4_CacheHit。公式 20,686 格、LibreOffice 重算零錯誤；具名範圍 294 個（IF_ 157，其中下游 154；B4_ 39；B5_ 23）。v5.8 的 228 個具名範圍中 227 個（B4_Chi 已改名）在 v5.9 逐格同值（2,285 格），唯一差異為 Tech_Registry T12 與 H_HAR 的說明文字；Block 1–3 各頁與 Block 4 的 Capability、Price_Frontier、Cache_Store、Sens_Rev 逐格一致；Workload 移位後逐格同值。藍字輸入 990 格全數對應；新增輸入 161 格。情境測試（LibreOffice）：生產折減 0.7、Tech_Registry O11:O13＝1、T12 開關＝1、T12 開關＝1 且檔案 3，皆零錯誤（v5.8 前兩者分別 145、339 格錯誤）。冪等：以 v5.9 重建 27,190 格不符 0。新函數：AVERAGE。

## common.py

```python
# Shared styling + helpers for Tokenomics v5.1 builder
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

BLUE, BLACK, GREEN = "FF0000FF", "FF000000", "FF008000"
F_IN   = Font(name="Arial", size=10, color=BLUE)
F_CALC = Font(name="Arial", size=10, color=BLACK)
F_LINK = Font(name="Arial", size=10, color=GREEN)
F_BOLD = Font(name="Arial", size=10, bold=True)
F_HLINK= Font(name="Arial", size=10, bold=True, color=GREEN)
F_TITLE= Font(name="Arial", size=13, bold=True)
F_NOTE = Font(name="Arial", size=9, color="FF595959")
FILL_SEC = PatternFill("solid", fgColor="FFD9E1F2")
FILL_KEY = PatternFill("solid", fgColor="FFFFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")

def put(ws, ref, v, font=None, fmt=None, fill=None, wrap=False):
    c = ws[ref]; c.value = v
    if font is None:
        if isinstance(v, str) and v.startswith("="):
            font = F_LINK if "!" in v else F_CALC
        elif isinstance(v, (int, float)):
            font = F_IN
        else:
            font = F_CALC
    c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if wrap: c.alignment = WRAP
    return c

def section(ws, row, text, ncols):
    for i in range(1, ncols + 1):
        ws.cell(row=row, column=i).fill = FILL_SEC
    put(ws, f"A{row}", text, F_BOLD, fill=FILL_SEC)

def title(ws, t1, t2):
    put(ws, "A1", t1, F_TITLE)
    put(ws, "A2", t2, F_NOTE)
```

## inputs.py

```python
# Input sheets: Spec_Rack (Block 2 rows), Arch, Serving, Energy inputs
from common import *

GENS = ["C", "D", "E", "F", "G"]          # Hopper, GB200, GB300, VR200, RU in Spec_Rack

def spec_rack(wb):
    ws = wb["Spec_Rack"]
    R = {}
    section(ws, 21, "B2. 效能規格（Block 2；藍字＝輸入；每 GPU 封裝）", 8)
    put(ws, "H4", "標記／來源", F_BOLD)
    rows = [
      ("prec",  "服務精度", None, ["FP8", "NVFP4", "NVFP4", "NVFP4", "NVFP4"], None,
       "Hopper 不支援 FP4，以 FP8 服務"),
      ("pk_b",  "峰值 dense（基準）PF/GPU", "#,##0.000", [1.979, 10, 15, 35, 73], None,
       "Interested-party（NVIDIA 規格）：H100 FP8 dense 1,979 TF（v5.5 更正；v5.4 誤填 BF16 的 989）；GB200 FP4 10 PF（HGX B200 為 9）；B300 15；Rubin NVFP4 訓練 35；RU＝104×35/50 推估 [Derived]。S28"),
      ("pk_h",  "峰值（高情境：NVFP4 推論口徑）PF/GPU", "#,##0.000", [1.979, 10, 15, 50, 104], None,
       "Rubin 50 PF 含自適應壓縮；RU NVL576 15 EF ÷ 144。J2：只作高情境"),
      ("hbm",   "HBM 容量 GB/GPU", "#,##0", [80, 186, 288, 288, 1024], None,
       "GB200 NVL72 13.4 TB ÷ 72；InferenceX 以 192 計。RU HBM4e 約 1 TB/封裝。S28"),
      ("bw",    "HBM 頻寬 TB/s/GPU", "#,##0.00", [3.35, 8, 8, 22, 32], None,
       "Rubin 22 TB/s（NVIDIA 2026 上修）；RU 4.6 PB/s ÷ 144。S28"),
      ("link",  "EP 通訊頻寬 TB/s/GPU（單向）", "#,##0.00", [0.05, 0.9, 0.9, 1.8, 1.8], None,
       "Hopper EP 跨節點走 400G IB；NVLink 5＝900 GB/s；NVLink 6＝1.8 TB/s（InferenceX 規格表 S20）；RU 取同 VR [Assumed]"),
      ("dom",   "Scale-up 域 GPU 數", "#,##0", [8, 72, 72, 72, 144], None, ""),
      ("ep",    "decode EP 基準寬度", "#,##0", [64, 32, 32, 32, 64], None,
       "GB300 公開配方 dep32（S21）；Hopper 跨節點 [Analogy DeepSeek]；RU [Assumed]。權重放不下時自動加寬"),
      ("be",    "專家權重 bytes/param", "0.0000", [1.0, 0.5625, 0.5625, 0.5625, 0.5625], None,
       "NVFP4＝4 bit＋每 16 值 8 bit scale＝0.5625 B；Hopper FP8"),
      ("bn",    "非專家權重 bytes/param", "0.00", [1, 1, 1, 1, 1], None, "注意力、路由、embedding 以 FP8 存放 [Analogy V4]"),
      ("ninst", "每 prefill 實例 GPU 數（算 TTFT）", "#,##0", [8, 4, 4, 4, 8], None,
       "GB300 配方 dep4 prefill（S21）"),
      ("gpuw",  "GPU 功率 W/封裝（能量用）", "#,##0", [700, 1200, 1400, 1800, 3600], None,
       "Interested-party；Rubin 約 1.8 kW、RU 推估。僅用於能量下限估算"),
      ("ehbm",  "HBM 存取能量 pJ/byte", "#,##0", [31, 25, 25, 20, 18], None,
       "Analogy：HBM3 約 3.9 pJ/bit、HBM3e 約 3、HBM4 約 2.5；區間 ±30%（S29）"),
    ]
    r = 22
    for key, lab, fmt, vals, _, note in rows:
        put(ws, f"A{r}", lab)
        for col, v in zip(GENS, vals):
            put(ws, f"{col}{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE)
        R[key] = r; r += 1
    # effective peak per J2 selector
    put(ws, f"A{r}", "計算用峰值 PF/GPU（依 Serving 峰值情境）", F_BOLD)
    for col in GENS:
        put(ws, f"{col}{r}", f"=IF(Serving!$C$16=2,{col}{R['pk_h']},{col}{R['pk_b']})", fmt="#,##0.000", fill=FILL_KEY)
    R["pk"] = r; r += 1
    put(ws, f"A{r}", "Ridge point（FLOP/byte）")
    for col in GENS:
        put(ws, f"{col}{r}", f"={col}{R['pk']}*1000/{col}{R['bw']}", fmt="#,##0")
    R["ridge"] = r; r += 2
    # ---- Block 3: training peaks (dense, per package) ----
    section(ws, r, "B3. 訓練峰值（Block 3；dense；每 GPU 封裝；MFU 以 FP8 列為分母，J7）", 8); r += 1
    trows = [
      ("tbf16", "BF16 dense PF/GPU", [0.989, 2.5, 2.5, 4.0, 8.0],
       "Interested-party（NVIDIA）：H100 989 TF；GB200／GB300 2.5；VR NVL72 288 PF ÷ 72＝4.0（S36）；RU 取 VR×2 [Assumed]"),
      ("tfp8", "FP8 dense PF/GPU（訓練基準，J7）", [1.979, 5, 5, 17.5, 34.7],
       "Interested-party（NVIDIA）：H100 1,979 TF；GB200／GB300 FP8 5 PF（B300 未提升 FP8）；VR NVL72 1,260 PF ÷ 72＝17.5（S36）；RU NVL576 5 EF ÷ 144 [模型內建知識，待查]"),
      ("tfp4", "NVFP4 訓練 dense PF/GPU（Tech_Registry 情境）", [1.979, 10, 15, 35, 73],
       "Hopper 無 FP4，取 FP8；GB200 10（NVIDIA：Rubin 為 Blackwell 3.5 倍）；GB300 15 [Assumed，區間 10–15]；VR 2,520 PF ÷ 72＝35（S36）；RU＝VR × 104/50 [Derived]"),
    ]
    for key, lab, vals, note in trows:
        put(ws, f"A{r}", lab)
        for col, v in zip(GENS, vals):
            put(ws, f"{col}{r}", v, fmt="#,##0.000")
        put(ws, f"H{r}", note, F_NOTE)
        R[key] = r; r += 1
    ws.column_dimensions["H"].width = 70
    return R

def arch(wb):
    ws = wb.create_sheet("Arch", 3)
    title(ws, "Arch — 三層級代表架構（D5：每層級一個代表；參數為公開模型卡或推估）",
          "Luna／Sol 以公開權重模型為物理代表 [Analogy：對應封閉層級]；Astra 為封閉前沿代理，KV 以情境處理（J1）")
    for c, w in zip("ABCDEFG", [30, 12, 16, 16, 18, 16, 80]): ws.column_dimensions[c].width = w
    for c, v in zip("ABCDEFG", ["參數", "單位", "Luna（低層）", "Sol（中層）", "Astra（頂層）", "標記", "來源／說明"]):
        put(ws, f"{c}4", v, F_BOLD)
    R = {}
    rows = [
      ("rep", "代表架構", "", ["DeepSeek V4-Flash 類", "DeepSeek V4-Pro 類", "封閉前沿代理"], None, "Decision", "D5；Andy 2026-09-30 確認"),
      ("T", "總參數", "B", [284, 1600, 4000], "#,##0", "Verified／Assumed", "V4-Flash 284B、V4-Pro 1.6T（模型卡，S27）；Astra 4T [Assumed，區間 2–10T]"),
      ("A", "啟用參數", "B", [13, 49, 180], "#,##0", "Verified／Assumed", "V4-Flash 13B、V4-Pro 49B；Astra 180B [Assumed，區間 60–250B]"),
      ("L", "層數", "層", [43, 61, 100], "#,##0", "Verified／Assumed", "V4-Pro 61（config.json）；V4-Flash 43（二手）；Astra [Assumed]"),
      ("d", "d_model", "", [4096, 7168, 12288], "#,##0", "Verified／Derived", "V4-Pro 7168；V4-Flash 由專家維度反推；Astra [Assumed]"),
      ("hq", "query heads", "", [64, 128, 96], "#,##0", "Verified／Analogy", "V4-Pro 128；V4-Flash 取 Pro 一半 [Analogy]"),
      ("hd", "head_dim", "", [512, 512, 128], "#,##0", "Verified／Assumed", "V4 單一 512 維 KV head；Astra 128"),
      ("E", "routed experts", "", [256, 384, 512], "#,##0", "Verified／Assumed", ""),
      ("k", "每 token 啟用 routed experts", "", [6, 6, 16], "#,##0", "Verified／Assumed", ""),
      ("s", "shared experts", "", [1, 1, 1], "#,##0", "Verified", ""),
      ("V", "vocab", "", [129280, 129280, 200000], "#,##0", "Verified／Assumed", ""),
      ("ff", "全注意力層比例", "%", [0.5, 0.5, 1], "0%", "Verified／Assumed", "V4：CSA 與 HCA 約各半；Astra 全層注意力"),
      ("cap", "全注意力層跨度上限（0＝全上下文）", "tok", [4224, 4224, 0], "#,##0", "Derived", "V4 CSA：top-k 1,024 壓縮塊 × 4 ＋ 128 窗口"),
      ("comp", "其他層壓縮比", "x", [128, 128, 1], "#,##0", "Verified", "V4 HCA 128× 壓縮"),
      ("win", "其他層滑動窗", "tok", [128, 128, 0], "#,##0", "Verified", ""),
      ("kvsel", "Astra KV 情境（1 混合／2 全層 MLA／3 GQA-8）", "選擇", [None, None, 2], "0", "Decision", "J1：基準 2（Andy 2026-09-30 確認）"),
      ("kv1", "KV bytes/token — 情境 1", "B", [2795, 3965, 14976], "#,##0", "Derived／Assumed", "Luna 65×43、Sol 65×61（v4 推導，FP8 KV）；Astra 混合：26% 層 × 576 × 100 層（類 K3）"),
      ("kv2", "KV bytes/token — 情境 2", "B", [2795, 3965, 57600], "#,##0", "Derived／Assumed", "Astra 全層 MLA：576 × 100"),
      ("kv3", "KV bytes/token — 情境 3", "B", [2795, 3965, 204800], "#,##0", "Derived／Assumed", "Astra GQA-8：8 × 128 × 2 × 100"),
    ]
    r = 5
    for key, lab, unit, vals, fmt, tag, note in rows:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDE", vals):
            if v is not None: put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE)
        R[key] = r; r += 1
    section(ws, r, "導出", 7); r += 1
    der = [
      ("kv", "KV bytes/token（採用）", "B", "=CHOOSE(IF({c}{kvsel}=\"\",1,{c}{kvsel}),{c}{kv1},{c}{kv2},{c}{kv3})", "#,##0"),
      ("emb", "Embedding＋LM head 參數", "B", "={c}{V}*{c}{d}*2/1E9", "#,##0.00"),
      ("pe", "每 routed expert 參數", "B", "=({c}{T}-{c}{A})/({c}{L}*({c}{E}-{c}{k}))", "0.0000"),
      ("ne", "非專家參數（注意力、路由、embedding）", "B", "={c}{A}-{c}{L}*({c}{k}+{c}{s})*{c}{pe}", "#,##0.0"),
      ("ex", "專家參數", "B", "={c}{T}-{c}{ne}", "#,##0.0"),
      ("attc", "注意力 FLOPs／每個被注意的 token", "FLOP", "=4*{c}{hq}*{c}{hd}*{c}{L}", "#,##0"),
      ("kv128", "128K 上下文每序列 KV", "GB", "={c}{kv}*128000/1E9", "#,##0.00"),
    ]
    for key, lab, unit, f, fmt in der:
        R[key] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDE":
            m = {k: v for k, v in R.items()}; m["c"] = c
            put(ws, f"{c}{r}", f.format(**m), fmt=fmt, fill=FILL_KEY if key == "kv" else None)
        r += 1
    put(ws, f"G{R['pe']}", "由公開總參數與啟用參數反推，確保總數吻合（v4 方法）", F_NOTE)
    ws.freeze_panes = "C5"
    return R

def serving(wb):
    ws = wb.create_sheet("Serving", 4)
    title(ws, "Serving — 服務設定與各層級 SLO（主流：分離式 P/D、wide EP、attention DP、NVFP4、MTP、前綴快取）",
          "藍字＝輸入。SLO 依 J3 採市場觀測輸出速度（Artificial Analysis 2026-09，S26）")
    for c, w in zip("ABCDEF", [44, 14, 16, 16, 16, 90]): ws.column_dimensions[c].width = w
    put(ws, "A4", "全域設定", F_BOLD); put(ws, "B4", "單位", F_BOLD); put(ws, "C4", "值", F_BOLD); put(ws, "D4", "標記", F_BOLD); put(ws, "E4", "", F_BOLD); put(ws, "F4", "說明", F_BOLD)
    g = [
      (5, "服務架構", "", "分離式 P/D＋wide EP＋attention DP", None, "Decision", "D6 與 Block 2 命題"),
      (6, "MTP 草稿數 N", "tok", 3, "0", "Analogy", "DeepSeek MTP；區間 1–5"),
      (7, "每個草稿 token 接受率 α", "%", 0.70, "0%", "Verified-measured", "SGLang 修正後 0.57→0.70（S21）；區間 0.6–0.8"),
      (8, "每步期望接受 token a", "tok", "=(1-C7^(C6+1))/(1-C7)", "0.00", "Derived", "(1−α^(N+1))/(1−α)"),
      (9, "HBM 保留比例（啟用值、工作區）", "%", 0.10, "0%", "Assumed", "區間 5–20%"),
      (10, "非專家權重占可用 HBM 上限", "%", 0.20, "0%", "Assumed", "超過時自動以注意力 TP 切分"),
      (11, "專家權重占可用 HBM 上限", "%", 0.40, "0%", "Assumed", "超過時自動加寬 EP"),
      (12, "EP 啟用值 bytes/元素（dispatch＋combine）", "B", 3, "0.0", "Analogy", "FP8 dispatch 1 B＋BF16 combine 2 B"),
      (13, "KV 讀取頻寬效率 η_mem", "%", 0.70, "0%", "Analogy", "區間 0.5–0.85"),
      (14, "EP 通訊效率 η_link", "%", 0.70, "0%", "Analogy", "區間 0.5–0.85"),
      (15, "快取命中 KV 載入頻寬", "TB/s/GPU", 0.10, "0.00", "Assumed", "主機記憶體／SSD 經 NIC 載入；區間 0.05–0.4。未計快取儲存成本"),
      (16, "峰值情境（1＝dense 基準／2＝NVFP4 推論高）", "選擇", 1, "0", "Decision", "J2：基準 1"),
      (17, "基準利用率（第 0 層）", "%", 0.60, "0%", "Assumed", "J6：Andy 尚未給值，暫沿用 OpenAI v0.5 的 60%（區間 40–80%）。Unit_Cost 同時輸出 100% 版"),
      (18, "實測→生產效率折減", "x", 1.0, "0.00", "Assumed", "待 Andy 決定。基準測試為固定長度、穩態負載；生產環境另有長度變異、路由不均、故障。1.0＝不折減。作用：η_p、η_d 乘此值，每層延遲除以此值。第二來源（MLPerf、DeepSeek 自揭）目前均高於本模型，見 Calib H 節"),
    ]
    for r, lab, unit, v, fmt, tag, note in g:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt)
        put(ws, f"D{r}", tag, F_NOTE); put(ws, f"F{r}", note, F_NOTE)
    ws["C17"].fill = PatternFill("solid", fgColor="FFFFFF00"); ws["C18"].fill = PatternFill("solid", fgColor="FFFFFF00")
    section(ws, 19, "各層級 SLO 與參考任務", 6)  # row 18 used by derating
    for c, v in zip("ABCDEF", ["項目", "單位", "=Arch!C4", "=Arch!D4", "=Arch!E4", "說明"]):
        put(ws, f"{c}20", v, F_HLINK if "!" in v else F_BOLD)
    t = [
      (21, "SLO：每用戶 decode 速度下限", "tok/s", [120, 65, 55], "#,##0", "Verified-measured（市場觀測）：GPT-5.6 Luna 約 120、GPT-5.6 Sol 約 68、GPT-6 Astra 約 52–56、Opus 5 約 54 tok/s（S26）。區間 Luna 100–300、Sol 50–100、Astra 30–75"),
      (22, "TTFT 上限（只作檢查）", "s", [2, 3, 5], "0.0", "Assumed"),
      (23, "參考 ISL（每次請求輸入）", "tok", [8192, 16384, 32768], "#,##0", "Assumed：Astra 用於長任務；上下文敏感度見 Sens_Perf"),
      (24, "參考 OSL（含思考）", "tok", [1024, 2048, 4096], "#,##0", "Assumed"),
      (25, "decode 平均上下文", "tok", ["=C23+C24/2", "=D23+D24/2", "=E23+E24/2"], "#,##0", "Derived"),
      (26, "prefill 平均位置", "tok", ["=C23/2", "=D23/2", "=E23/2"], "#,##0", "Derived"),
    ]
    for r, lab, unit, vals, fmt, note in t:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDE", vals): put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"F{r}", note, F_NOTE)
    for c in "CDE": ws[f"{c}21"].fill = FILL_KEY
    return ws

def energy_inputs(wb):
    ws = wb.create_sheet("Energy")
    title(ws, "Energy — 逐步能量下限與閉合檢查",
          "物理下限＝FLOPs × pJ/FLOP ＋ HBM bytes × pJ/byte ＋ EP bytes × pJ/byte；閉合：下限功率 ≤ 機架平均用電（Block 1 輸入 Inputs!E10）")
    for c, w in zip("ABCDEF", [44, 14, 14, 14, 16, 80]): ws.column_dimensions[c].width = w
    put(ws, "A4", "輸入", F_BOLD)
    put(ws, "A5", "GPU 功率中可歸於運算的比例"); put(ws, "B5", "%"); put(ws, "C5", 0.6, fmt="0%")
    put(ws, "F5", "Assumed：pJ/FLOP＝GPU 功率 × 此比例 ÷ 峰值（滿載上限口徑），區間 0.4–0.8", F_NOTE)
    put(ws, "A6", "EP 通訊能量 NVLink"); put(ws, "B6", "pJ/byte"); put(ws, "C6", 10, fmt="0")
    put(ws, "F6", "Analogy：SerDes＋交換約 1–2 pJ/bit；區間 5–20", F_NOTE)
    put(ws, "A7", "EP 通訊能量 IB（Hopper）"); put(ws, "B7", "pJ/byte"); put(ws, "C7", 40, fmt="0")
    put(ws, "F7", "Analogy：含光模組與網卡；區間 20–80", F_NOTE)
    return ws
```

## calib.py

```python
from common import *

PTS = [  # col, use, gen idx, engine/date, MTP, s, ISL, OSL, measured, source
 ("C", "擬合點 1", 3, "InferenceX 最佳前緣（約 2026-07）", 1, 72, 8192, 1024, 9384.4, "S22"),
 ("D", "擬合點 2", 3, "InferenceX 最佳前緣（約 2026-07）", 1, 130, 8192, 1024, 3473.9, "S22"),
 ("E", "驗證", 3, "SGLang＋MTP，2026-06", 1, 50, 8192, 1024, 11200, "S21"),
 ("F", "驗證（舊軟體）", 3, "vLLM 無 MTP，2026-05-22", 0, 27, 8192, 1024, 6182, "S20"),
 ("G", "驗證（舊軟體）", 2, "vLLM 無 MTP，2026-05-22", 0, 27, 8192, 1024, 2189, "S20"),
 ("H", "驗證（口徑待查）", 2, "InferenceX 比較頁（0813）", 1, 110, 8192, 1024, 3795.5, "S23"),
 ("I", "驗證（口徑待查）", 3, "InferenceX 比較頁（0813）", 1, 110, 8192, 1024, 6522.4, "S23"),
]

def calib(wb, SP, AR):
    ws = wb.create_sheet("Calib", 5)
    title(ws, "Calib — 以實測錨點校準效率係數（實測只校準係數，不取代推導）",
          "錨點：DeepSeek V4-Pro（＝Sol 代表架構）、FP4、8K/1K、分離式 P/D，tok/s/GPU 為總 token 口徑。GB300 同一前緣上兩點聯立解出 η_d 與每層延遲；其餘各點為樣本外驗證")
    for c, w in zip("ABCDEFGHIJ", [44, 12, 16, 16, 16, 16, 16, 16, 16, 60]): ws.column_dimensions[c].width = w
    C = {}
    section(ws, 4, "A. 輸入", 10)
    put(ws, "A5", "η_p：prefill 達成峰值比例"); put(ws, "B5", "%"); put(ws, "C5", 0.30, fmt="0%")
    put(ws, "J5", "Analogy：DeepSeek H800 線上 prefill 約 0.37（S30，待查）；區間 0.15–0.45。擬合結果對此不敏感（見 G 節）", F_NOTE)
    section(ws, 7, "B. 錨點（每欄一個實測點）", 10)
    hdr = [("A8", "項目"), ("B8", "單位")]
    for a, b in hdr: put(ws, a, b, F_BOLD)
    rows = [("use", "用途", ""), ("g", "世代索引", ""), ("gn", "世代", ""), ("eng", "軟體／日期", ""),
            ("mtp", "MTP（1＝有）", ""), ("s", "每用戶速度", "tok/s"), ("isl", "ISL", "tok"), ("osl", "OSL", "tok"),
            ("T", "實測 tok/s/GPU（總 token）", "tok/s"), ("src", "來源", ""), ("indep", "量測平台（獨立性）", ""), ("lab", "點位標籤（世代｜用途｜速度）", ""), ("basis", "口徑", "")]
    r = 9
    for key, lab, unit in rows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); r += 1
    for col, use, g, eng, mtp, s, isl, osl, T, src in PTS:
        put(ws, f"{col}{C['use']}", use, F_BOLD)
        put(ws, f"{col}{C['g']}", g, fmt="0")
        put(ws, f"{col}{C['gn']}", f"=INDEX(Spec_Rack!$C$4:$G$4,{col}{C['g']})")
        put(ws, f"{col}{C['eng']}", eng, F_NOTE, wrap=True)
        put(ws, f"{col}{C['mtp']}", mtp, fmt="0")
        put(ws, f"{col}{C['s']}", s, fmt="#,##0")
        put(ws, f"{col}{C['isl']}", isl, fmt="#,##0"); put(ws, f"{col}{C['osl']}", osl, fmt="#,##0")
        put(ws, f"{col}{C['T']}", T, fmt="#,##0", fill=FILL_KEY)
        put(ws, f"{col}{C['src']}", src, F_NOTE)
        put(ws, f"{col}{C['indep']}", "InferenceX（SemiAnalysis）", F_NOTE, wrap=True)
        put(ws, f"{col}{C['lab']}", f'={col}{C["gn"]}&"｜"&{col}{C["use"]}&"｜"&TEXT({col}{C["s"]},"0")&" tok/s"', wrap=True)
        put(ws, f"{col}{C['basis']}", "總 token（輸入＋輸出）", F_NOTE, wrap=True)
    put(ws, f"J{C['indep']}", "七個點全部來自同一平台（S21 為 SGLang 作者轉述 InferenceX 資料，不構成獨立來源）。第二來源見 H 節", F_NOTE, wrap=True)
    ws.row_dimensions[C["eng"]].height = 30; ws.row_dimensions[C["lab"]].height = 30
    section(ws, r, "C. 各點的模型量（Sol 架構；與 Perf 同一套公式）", 10); r += 1
    g = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}{C['g']})"
    a = lambda row: f"=Arch!$D${row}"
    mrows = [
      ("P", "計算用峰值", "PF/GPU", "#,##0.000", g(SP["pk"])),
      ("hbm", "HBM 容量", "GB", "#,##0", g(SP["hbm"])),
      ("bw", "HBM 頻寬", "TB/s", "#,##0.00", g(SP["bw"])),
      ("link", "EP 通訊頻寬", "TB/s", "#,##0.00", g(SP["link"])),
      ("epb", "EP 基準寬度", "", "#,##0", g(SP["ep"])),
      ("be", "專家 bytes/param", "B", "0.0000", g(SP["be"])),
      ("bn", "非專家 bytes/param", "B", "0.00", g(SP["bn"])),
      ("A", "啟用參數", "B", "#,##0", a(AR["A"])), ("L", "層數", "", "#,##0", a(AR["L"])),
      ("d", "d_model", "", "#,##0", a(AR["d"])), ("k", "啟用專家", "", "#,##0", a(AR["k"])),
      ("ne", "非專家參數", "B", "#,##0.0", a(AR["ne"])), ("ex", "專家參數", "B", "#,##0", a(AR["ex"])),
      ("kv", "KV bytes/token", "B", "#,##0", a(AR["kv"])), ("attc", "注意力 FLOPs／被注意 token", "", "#,##0", a(AR["attc"])),
      ("ff", "全注意力層比例", "%", "0%", a(AR["ff"])), ("cap", "跨度上限", "", "#,##0", a(AR["cap"])),
      ("comp", "壓縮比", "", "#,##0", a(AR["comp"])), ("win", "滑動窗", "", "#,##0", a(AR["win"])),
      ("ctxd", "decode 平均上下文", "tok", "#,##0", "={X}{isl}+{X}{osl}/2"),
      ("attd", "decode 被注意 token", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxd},MIN({X}{ctxd},{X}{cap}))+(1-{X}{ff})*({X}{ctxd}/{X}{comp}+{X}{win})"),
      ("Fd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attd})/1E9"),
      ("ctxp", "prefill 平均位置", "tok", "#,##0", "={X}{isl}/2"),
      ("attp", "prefill 被注意 token", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxp},MIN({X}{ctxp},{X}{cap}))+(1-{X}{ff})*({X}{ctxp}/{X}{comp}+{X}{win})"),
      ("Fp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attp})/1E9"),
      ("usable", "可用 HBM", "GB", "#,##0", "={X}{hbm}*(1-Serving!$C$9)"),
      ("tpa", "注意力 TP 度", "", "0", "=MAX(1,CEILING({X}{ne}*{X}{bn}/(Serving!$C$10*{X}{usable}),1))"),
      ("epw", "EP 寬度", "", "#,##0", "=MAX({X}{epb},CEILING({X}{ex}*{X}{be}/(Serving!$C$11*{X}{usable}),1))"),
      ("W", "每 GPU 權重", "GB", "#,##0.0", "={X}{ne}*{X}{bn}/{X}{tpa}+{X}{ex}*{X}{be}/{X}{epw}"),
      ("n", "草稿數（無 MTP＝0）", "", "0", "=Serving!$C$6*{X}{mtp}"),
      ("a", "每步接受 token", "", "0.00", "=IF({X}{mtp}=1,Serving!$C$8,1)"),
      ("Pp", "prefill tok/s/GPU（η_p 基準）", "tok/s", "#,##0", "=$C$5*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("c1", "每序列算力時間（η＝1）", "ms", "0.00000", "=({X}{n}+1)*{X}{Fd}/{X}{P}/1000"),
      ("Dm", "實測反推 decode tok/s（每 decode GPU）", "tok/s", "#,##0", "={X}{osl}/(({X}{isl}+{X}{osl})/{X}{T}-{X}{isl}/{X}{Pp})"),
      ("Bm", "實測反推批次", "序列/GPU", "#,##0.0", "={X}{Dm}/{X}{s}"),
    ]
    for key, lab, unit, fmt, tpl in mrows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for col, *_ in PTS:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt)
        r += 1
    put(ws, f"J{C['Dm']}", "只對擬合點有意義；假設 P:D GPU 依工作量配比", F_NOTE)
    r += 1
    section(ws, r, "D. 擬合（擬合點 1、2 聯立；假設兩點皆為算力項綁定，見下列檢查）", 10); r += 1
    C["etad_fit"] = r
    put(ws, f"A{r}", "η_d：decode 每序列算力效率"); put(ws, f"B{r}", "%")
    put(ws, f"C{r}", f"=(C{C['Bm']}-D{C['Bm']})*C{C['c1']}/(1000*(C{C['a']}/C{C['s']}-D{C['a']}/D{C['s']}))", fmt="0.00%", fill=FILL_KEY)
    put(ws, f"J{r}", "B×c/η＝1000×a/s − 固定延遲；兩點相減消去固定延遲", F_NOTE); r += 1
    C["tfix_fit"] = r
    put(ws, f"A{r}", "每步固定延遲（GB300、Sol、含 MTP）"); put(ws, f"B{r}", "ms")
    put(ws, f"C{r}", f"=1000*C{C['a']}/C{C['s']}-C{C['Bm']}*C{C['c1']}/C{C['etad_fit']}", fmt="#,##0.00"); r += 1
    C["tl_fit"] = r
    put(ws, f"A{r}", "每層每次前向固定延遲"); put(ws, f"B{r}", "µs")
    put(ws, f"C{r}", f"=(C{C['tfix_fit']}-C{C['W']}/C{C['bw']})*1000/(C{C['L']}+C{C['n']})", fmt="#,##0", fill=FILL_KEY)
    put(ws, f"J{r}", "（固定延遲 − 權重讀取時間）÷（層數＋草稿數）：涵蓋 all-to-all 延遲、kernel 啟動、同步", F_NOTE); r += 1
    C["chk"] = r
    put(ws, f"A{r}", "檢查：擬合點 1 算力項為綁定")
    put(ws, f"C{r}", f"=IF(C{C['c1']}/C{C['etad_fit']}>=MAX(C{C['kv']}*C{C['ctxd']}/(C{C['bw']}*Serving!$C$13)/1E9,(C{C['n']}+1)*C{C['L']}*C{C['k']}*C{C['d']}*Serving!$C$12/(C{C['link']}*Serving!$C$14)/1E9),\"成立\",\"不成立\")")
    r += 2
    section(ws, r, "E. 各世代採用參數（GB300＝擬合值；其他世代＝擬合值 × 倍數）", 10); r += 1
    for c, v in zip("CDEFG", range(1, 6)):
        put(ws, f"{c}{r}", f"=Spec_Rack!{c}4", F_HLINK)
    put(ws, f"A{r}", "世代", F_BOLD); r += 1
    mult = [("etadm", "η_d 倍數", [1.5, 1, 1, 1, 1], "Hopper：v5.4 取 3（DeepSeek H800 線上 decode 約達峰值 18%，S30；當時峰值誤用 989 TF）。v5.5 峰值更正為 FP8 1,979 TF，倍數同步減半為 1.5，使 Hopper 產出不變；S30 口徑查核後重推 [Analogy，區間 0.5–2.5]；GB200、VR200 沿用 GB300 [Analogy]；RU [Assumed]"),
            ("tlm", "每層延遲倍數", [1.5, 1, 1, 1, 1], "Hopper EP 跨節點走 IB [Assumed 1.5，區間 1–3]"),
            ("etapm", "η_p 倍數", [0.5, 1, 1, 1, 1], "Hopper 0.5：v5.5 峰值更正（989→1,979 TF）後維持 prefill 產出不變（誤差 0.05%）；S30 口徑查核後重推")]
    for key, lab, vals, note in mult:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", "x")
        for c, v in zip("CDEFG", vals): put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"J{r}", note, F_NOTE, wrap=True); r += 1
    for key, lab, unit, fmt, base, m in [("etad", "η_d（採用）", "%", "0.00%", f"$C${C['etad_fit']}", "etadm"),
                                        ("tl", "每層延遲（採用）", "µs", "#,##0", f"$C${C['tl_fit']}", "tlm"),
                                        ("etap", "η_p（採用）", "%", "0.0%", "$C$5", "etapm")]:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDEFG":
            put(ws, f"{c}{r}", f"={base}*{c}{C[m]}", fmt=fmt, fill=FILL_KEY)
        r += 1
    r += 1
    section(ws, r, "F. 樣本外驗證（以採用參數重算各點）", 10); r += 1
    vrows = [
      ("ved", "η_d（該世代）", "%", "0.00%", f"=INDEX($C${C['etad']}:$G${C['etad']},{{X}}{C['g']})"),
      ("vtl", "每層延遲（該世代）", "µs", "#,##0", f"=INDEX($C${C['tl']}:$G${C['tl']},{{X}}{C['g']})"),
      ("vep", "η_p（該世代）", "%", "0.0%", f"=INDEX($C${C['etap']}:$G${C['etap']},{{X}}{C['g']})"),
      ("vPp", "prefill tok/s/GPU", "tok/s", "#,##0", "={X}{vep}*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("vtf", "每步固定延遲", "ms", "#,##0.00", "={X}{W}/{X}{bw}+({X}{L}+{X}{n})*{X}{vtl}/1000"),
      ("vce", "每序列每步時間", "ms", "0.0000", "=MAX({X}{c1}/{X}{ved},{X}{kv}*{X}{ctxd}/({X}{bw}*Serving!$C$13)/1E9,({X}{n}+1)*{X}{L}*{X}{k}*{X}{d}*Serving!$C$12*({X}{epw}-1)/{X}{epw}/({X}{link}*Serving!$C$14)/1E9)"),
      ("vbs", "SLO 批次上限", "序列", "#,##0.0", "=(1000*{X}{a}/{X}{s}-{X}{vtf})/{X}{vce}"),
      ("vbc", "容量批次上限", "序列", "#,##0", "=({X}{usable}-{X}{W})*1E9/({X}{kv}*{X}{ctxd})"),
      ("vB", "B*", "序列", "#,##0.0", "=MAX(0,MIN({X}{vbs},{X}{vbc}))"),
      ("vD", "decode tok/s/GPU", "tok/s", "#,##0", "=IF({X}{vB}>0,{X}{vB}*{X}{a}/(({X}{vtf}+{X}{vB}*{X}{vce})/1000),0)"),
      ("vT", "模型 tok/s/GPU（總 token）", "tok/s", "#,##0", "=IF({X}{vD}>0,({X}{isl}+{X}{osl})/({X}{isl}/{X}{vPp}+{X}{osl}/{X}{vD}),0)"),
      ("ratio", "模型 ÷ 實測", "x", "0.00", "={X}{vT}/{X}{T}"),
    ]
    for key, lab, unit, fmt, tpl in vrows:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for col, *_ in PTS:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt, fill=FILL_KEY if key == "ratio" else None)
        r += 1
    notes = {"C": "擬合點：應為 1.00", "D": "擬合點：應為 1.00", "E": "同世代、不同日期與引擎：檢驗前緣形狀",
             "F": "舊軟體：模型應高於實測（軟體差距）", "G": "舊軟體＋GB200 記憶體限制配方（S20 說明）",
             "H": "工作負載標示不明（頁面預設為 agentic）", "I": "同上"}
    C["vnote"] = r; put(ws, f"A{r}", "判讀")
    for col, t in notes.items(): put(ws, f"{col}{r}", t, F_NOTE, wrap=True)
    ws.row_dimensions[r].height = 42
    r += 2
    section(ws, r, "G. η_p 敏感度：擬合結果隨 η_p 的變化（η_p 僅影響 prefill／decode GPU 分攤）", 10); r += 1
    put(ws, f"A{r}", "η_p", F_BOLD)
    for c, v in zip("CDE", [0.15, 0.30, 0.45]): put(ws, f"{c}{r}", v, fmt="0%")
    ep_r = r; r += 1
    srows = [
      ("Pp1", "擬合點 1 prefill tok/s", "=${c}$" if False else "={c}{ep}*$C${P}*1E15/($C${Fp}*1E9)", "#,##0"),
      ("Pp2", "擬合點 2 prefill tok/s", "={c}{ep}*$D${P}*1E15/($D${Fp}*1E9)", "#,##0"),
      ("B1", "擬合點 1 反推批次", "=$C${osl}/(($C${isl}+$C${osl})/$C${T}-$C${isl}/{c}{Pp1})/$C${s}", "#,##0.0"),
      ("B2", "擬合點 2 反推批次", "=$D${osl}/(($D${isl}+$D${osl})/$D${T}-$D${isl}/{c}{Pp2})/$D${s}", "#,##0.0"),
      ("ed", "η_d", "=({c}{B1}-{c}{B2})*$C${c1}/(1000*($C${a}/$C${s}-$D${a}/$D${s}))", "0.00%"),
      ("tl", "每層延遲 µs", "=((1000*$C${a}/$C${s}-{c}{B1}*$C${c1}/{c}{ed})-$C${W}/$C${bw})*1000/($C${L}+$C${n})", "#,##0"),
    ]
    SR = {}
    for key, lab, tpl, fmt in srows:
        SR[key] = r; put(ws, f"A{r}", lab)
        for c in "CDE":
            m = dict(C); m.update(SR); m["c"] = c; m["ep"] = ep_r
            put(ws, f"{c}{r}", tpl.format(**m), fmt=fmt)
        r += 1

    r += 1
    section(ws, r, "H. 第二來源驗證：MLPerf Inference DeepSeek-R1（MLCommons 稽核；提交者 NVIDIA 為利害關係方）", 10); r += 1
    put(ws, f"A{r}", "R1 架構與工作負載（驗證專用輸入）", F_BOLD); r += 1
    rin = [("rT", "總參數", "B", 671, "#,##0"), ("rA", "啟用參數", "B", 37, "#,##0"), ("rL", "層數", "", 61, "#,##0"),
           ("rd", "d_model", "", 7168, "#,##0"), ("rE", "routed experts", "", 256, "#,##0"), ("rk", "啟用 experts", "", 8, "#,##0"),
           ("rs", "shared experts", "", 1, "#,##0"), ("rV", "vocab", "", 129280, "#,##0"),
           ("rkv", "KV bytes/token（MLA 576 × 61 層，FP8）", "B", 35136, "#,##0"),
           ("rac", "注意力 FLOPs／被注意 token（MLA：2×128×192＋2×128×128，× 61）", "FLOP", 4997120, "#,##0"),
           ("risl", "平均 ISL（MLCommons 資料集）", "tok", 800, "#,##0"), ("rosl", "平均 OSL", "tok", 3880, "#,##0")]
    for key, lab, unit, v, fmt in rin:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt); r += 1
    put(ws, f"J{C['rT']}", "Verified：DeepSeek-V3/R1 模型卡；ISL／OSL 800／3,880（MLCommons 2025-09，S33）", F_NOTE, wrap=True)
    for key, lab, f, fmt in [("rpe", "每 routed expert 參數", "=(C{rT}-C{rA})/(C{rL}*(C{rE}-C{rk}))", "0.0000"),
                             ("rne", "非專家參數", "=C{rA}-C{rL}*(C{rk}+C{rs})*C{rpe}", "#,##0.0"),
                             ("rex", "專家參數", "=C{rT}-C{rne}", "#,##0")]:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", "B"); put(ws, f"C{r}", f.format(**C), fmt=fmt); r += 1
    r += 1
    MP = [("C", "GB300 interactive（v6.1）", 3, 1, "=1000/15", "=253506/72"),
          ("D", "GB200 interactive（v6.0）", 2, 1, "=1000/15", "=240318/72"),
          ("E", "VR200 interactive（v6.1 預覽）", 4, 1, "=1000/15", "=652750/72"),
          ("F", "GB300 server（v6.0）", 3, 0, "=1000/80", 8064)]
    hdr = r; C["mhdr"] = r; put(ws, f"A{r}", "驗證點", F_BOLD)
    for col, lab, *_ in MP: put(ws, f"{col}{r}", lab, F_BOLD, wrap=True)
    ws.row_dimensions[r].height = 30; r += 1
    base = [("mg", "世代索引", "0"), ("ms", "每用戶速度下限（1000 ÷ TPOT）", "#,##0.0"), ("mm", "推測解碼（1＝有）", "0"),
            ("mT", "MLPerf 實測輸出 tok/s/GPU（總量 ÷ 72）", "#,##0")]
    UNITS = {"ms": "tok/s", "mT": "tok/s/GPU"}
    for key, lab, fmt in base:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", UNITS.get(key, ""))
        for (col, _, g, mtp, s, T) in MP:
            v = {"mg": g, "ms": s, "mm": mtp, "mT": T}[key]
            put(ws, f"{col}{r}", v, F_IN if not isinstance(v, str) or "/" in v else None, fmt=fmt,
                fill=FILL_KEY if key == "mT" else None)
        r += 1
    C["mplat"] = r; put(ws, f"A{r}", "量測平台（獨立性）")
    for col, lab, *_ in MP:
        put(ws, f"{col}{r}", "MLPerf（MLCommons 稽核）／NVIDIA 提交" + ("（預覽類）" if "預覽" in lab else ""), F_NOTE, wrap=True)
    ws.row_dimensions[r].height = 30; r += 1
    C["mgn"] = r; put(ws, f"A{r}", "世代")
    for col, *_ in MP: put(ws, f"{col}{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,{col}{C['mg']})")
    r += 1
    C["mbasis"] = r; put(ws, f"A{r}", "口徑")
    for col, *_ in MP: put(ws, f"{col}{r}", "輸出 token", F_NOTE)
    r += 1
    put(ws, f"J{C['mm']}", "MLCommons 規則表只在 interactive 列出 MTP 推測解碼（3 步），server 設為無", F_NOTE, wrap=True)
    put(ws, f"J{C['mT']}", "MLPerf 指標為輸出 token；interactive 的 TPOT 15 ms 為 p99，平均速度更高，本模型以下限計算，偏保守", F_NOTE, wrap=True)
    gl = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}{C['mg']})"
    cl = lambda row: f"=INDEX($C${row}:$G${row},{{X}}{C['mg']})"
    mrows2 = [
      ("mP", "計算用峰值", "PF", "#,##0.000", gl(SP["pk"])), ("mH", "HBM", "GB", "#,##0", gl(SP["hbm"])),
      ("mB", "HBM 頻寬", "TB/s", "#,##0.00", gl(SP["bw"])), ("mLk", "EP 頻寬", "TB/s", "#,##0.00", gl(SP["link"])),
      ("mEb", "EP 基準", "", "#,##0", gl(SP["ep"])), ("mbe", "專家 B/param", "", "0.0000", gl(SP["be"])), ("mbn", "非專家 B/param", "", "0.00", gl(SP["bn"])),
      ("mU", "可用 HBM", "GB", "#,##0", "={X}{mH}*(1-Serving!$C$9)"),
      ("mTP", "注意力 TP", "", "0", "=MAX(1,CEILING($C${rne}*{X}{mbn}/(Serving!$C$10*{X}{mU}),1))"),
      ("mEP", "EP 寬度", "", "#,##0", "=MAX({X}{mEb},CEILING($C${rex}*{X}{mbe}/(Serving!$C$11*{X}{mU}),1))"),
      ("mW", "每 GPU 權重", "GB", "#,##0.0", "=$C${rne}*{X}{mbn}/{X}{mTP}+$C${rex}*{X}{mbe}/{X}{mEP}"),
      ("mcd", "decode 平均上下文", "tok", "#,##0", "=$C${risl}+$C${rosl}/2"),
      ("mFd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*$C${rA}*1E9+$C${rac}*{X}{mcd})/1E9"),
      ("mFp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*$C${rA}*1E9+$C${rac}*$C${risl}/2)/1E9"),
      ("mn", "草稿數", "", "0", "=Serving!$C$6*{X}{mm}"), ("ma", "每步接受", "", "0.00", "=IF({X}{mm}=1,Serving!$C$8,1)"),
      ("med", "η_d（該世代）", "%", "0.00%", cl(C["etad"])), ("mtl", "每層延遲（該世代）", "µs", "#,##0", cl(C["tl"])), ("mep", "η_p（該世代）", "%", "0.0%", cl(C["etap"])),
      ("mPp", "prefill tok/s/GPU", "tok/s", "#,##0", "={X}{mep}*{X}{mP}*1E15/({X}{mFp}*1E9)"),
      ("mtf", "每步固定延遲", "ms", "#,##0.00", "={X}{mW}/{X}{mB}+($C${rL}+{X}{mn})*{X}{mtl}/1000"),
      ("mce", "每序列每步時間", "ms", "0.0000", "=MAX(({X}{mn}+1)*{X}{mFd}/({X}{mP}*{X}{med})/1000,$C${rkv}*{X}{mcd}/({X}{mB}*Serving!$C$13)/1E9,({X}{mn}+1)*$C${rL}*$C${rk}*$C${rd}*Serving!$C$12*({X}{mEP}-1)/{X}{mEP}/({X}{mLk}*Serving!$C$14)/1E9)"),
      ("mBs", "B*", "序列", "#,##0.0", "=MAX(0,MIN((1000*{X}{ma}/{X}{ms}-{X}{mtf})/{X}{mce},({X}{mU}-{X}{mW})*1E9/($C${rkv}*{X}{mcd})))"),
      ("mD", "decode tok/s/GPU", "tok/s", "#,##0", "=IF({X}{mBs}>0,{X}{mBs}*{X}{ma}/(({X}{mtf}+{X}{mBs}*{X}{mce})/1000),0)"),
      ("mO", "模型輸出 tok/s/GPU（含 prefill 分攤）", "tok/s", "#,##0", "=IF({X}{mD}>0,$C${rosl}/($C${risl}/{X}{mPp}+$C${rosl}/{X}{mD}),0)"),
      ("mR", "模型 ÷ MLPerf", "x", "0.00", "={X}{mO}/{X}{mT}"),
    ]
    for key, lab, unit, fmt, tpl in mrows2:
        C[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for (col, *_ ) in MP:
            m = dict(C); m["X"] = col
            put(ws, f"{col}{r}", tpl.format(**m), fmt=fmt, fill=FILL_KEY if key == "mR" else None)
        r += 1
    C["mVR"] = r
    put(ws, f"A{r}", "VR200 ÷ GB300（interactive）：模型"); put(ws, f"C{r}", f"=E{C['mO']}/C{C['mO']}", fmt="0.00", fill=FILL_KEY); r += 1
    C["mVRm"] = r
    put(ws, f"A{r}", "VR200 ÷ GB300（interactive）：MLPerf v6.1"); put(ws, f"C{r}", f"=E{C['mT']}/C{C['mT']}", fmt="0.00", fill=FILL_KEY); r += 1
    C["mGB"] = r
    put(ws, f"A{r}", "GB300 ÷ GB200（interactive）：模型 ／ MLPerf"); put(ws, f"C{r}", f"=C{C['mO']}/D{C['mO']}", fmt="0.00"); put(ws, f"D{r}", f"=C{C['mT']}/D{C['mT']}", fmt="0.00"); r += 1
    put(ws, f"J{C['mVR']}", "VR200 沿用 GB300 效率係數的檢驗：兩者接近即支持此 Analogy（MLPerf VR 為 NVIDIA 預覽類提交）", F_NOTE, wrap=True)
    put(ws, f"J{C['mGB']}", "來源衝突：InferenceX 顯示 GB300 對 GB200 約 1.7–2.8 倍，MLPerf 約 1.05 倍；GB200 的 VR-eq 應視為區間", F_NOTE, wrap=True)
    ws.freeze_panes = "C9"
    return C
```

## perf.py

```python
# Perf-like column generator: same row logic for Perf (15 cols) and Sens_Perf (scenario cols)
from common import *

def perf_rows(SP, AR, CAL, TR):
    """Row spec: (key, label, unit, fmt, template) ; '§' key = section header. Templates use {X} and row keys."""
    I = lambda sheet, rng, idx: f"=INDEX({sheet}!{rng},{{X}}${idx})"
    sp = lambda r: I("Spec_Rack", f"$C${r}:$G${r}", 6)
    ar = lambda r: I("Arch", f"$C${r}:$E${r}", 7)
    sv = lambda r: I("Serving", f"$C${r}:$E${r}", 7)
    return [
      ("§", "0. Tech_Registry 掛鉤（基準＝1；Registry 未啟用任何條目時與 v5.4 相同）"),
      ("hflop", "FLOPs/token 倍數（H_FLOP）", "x", "0.00", f"={TR['H_FLOP']}"),
      ("hkv", "KV bytes/token 倍數（H_KV）", "x", "0.00", f"={TR['H_KV']}"),
      ("hwb", "權重 bytes/param 倍數（H_WB）", "x", "0.00", f"={TR['H_WB']}"),
      ("§", "A. 規格（連結 Spec_Rack、DC_Cost）"),
      ("P", "計算用峰值", "PF/GPU", "#,##0.000", sp(SP["pk"])),
      ("hbm", "HBM 容量", "GB/GPU", "#,##0", sp(SP["hbm"])),
      ("bw", "HBM 頻寬", "TB/s/GPU", "#,##0.00", sp(SP["bw"])),
      ("link", "EP 通訊頻寬（單向）", "TB/s/GPU", "#,##0.00", sp(SP["link"])),
      ("epb", "decode EP 基準寬度", "GPU", "#,##0", sp(SP["ep"])),
      ("be", "專家權重 bytes/param（含 H_WB）", "B", "0.0000", sp(SP["be"]) + "*{X}{hwb}"),
      ("bn", "非專家權重 bytes/param（含 H_WB）", "B", "0.00", sp(SP["bn"]) + "*{X}{hwb}"),
      ("ninst", "每 prefill 實例 GPU 數", "GPU", "#,##0", sp(SP["ninst"])),
      ("gpus", "GPU 封裝／架", "顆", "#,##0", sp(6)),
      ("gpuw", "GPU 功率", "W", "#,##0", sp(SP["gpuw"])),
      ("ehbm", "HBM 存取能量", "pJ/B", "#,##0", sp(SP["ehbm"])),
      ("racks", "每 GW 機架數（功率情境）", "架", "#,##0", "=INDEX(DC_Cost!$C$12:$Q$12,3*({X}$6-1)+2)"),
      ("kw", "每架配電設計功率", "kW", "#,##0", "=INDEX(DC_Cost!$C$11:$Q$11,3*({X}$6-1)+2)"),
      ("§", "B. 架構（連結 Arch）"),
      ("A", "啟用參數", "B", "#,##0", ar(AR["A"])),
      ("L", "層數", "層", "#,##0", ar(AR["L"])),
      ("d", "d_model", "", "#,##0", ar(AR["d"])),
      ("k", "啟用 routed experts", "", "#,##0", ar(AR["k"])),
      ("ne", "非專家參數", "B", "#,##0.0", ar(AR["ne"])),
      ("ex", "專家參數", "B", "#,##0", ar(AR["ex"])),
      ("kv", "KV bytes/token（含 H_KV）", "B", "#,##0", ar(AR["kv"]) + "*{X}{hkv}"),
      ("attc", "注意力 FLOPs／被注意 token", "FLOP", "#,##0", ar(AR["attc"])),
      ("ff", "全注意力層比例", "%", "0%", ar(AR["ff"])),
      ("cap", "全注意力跨度上限", "tok", "#,##0", ar(AR["cap"])),
      ("comp", "其他層壓縮比", "x", "#,##0", ar(AR["comp"])),
      ("win", "其他層滑動窗", "tok", "#,##0", ar(AR["win"])),
      ("§", "C. 服務、SLO 與校準參數"),
      ("s", "SLO：每用戶 decode 速度下限", "tok/s", "#,##0", sv(21)),
      ("ttft", "TTFT 上限", "s", "0.0", sv(22)),
      ("isl", "參考 ISL", "tok", "#,##0", sv(23)),
      ("osl", "參考 OSL（含思考）", "tok", "#,##0", sv(24)),
      ("ctxd", "decode 平均上下文", "tok", "#,##0", "={X}{isl}+{X}{osl}/2"),
      ("ctxp", "prefill 平均位置", "tok", "#,##0", "={X}{isl}/2"),
      ("N", "MTP 草稿數", "tok", "0", "=Serving!$C$6"),
      ("alpha", "草稿接受率", "%", "0%", "=Serving!$C$7"),
      ("a", "每步期望接受 token", "tok", "0.00", "=(1-{X}{alpha}^({X}{N}+1))/(1-{X}{alpha})"),
      ("prod", "實測→生產效率折減", "x", "0.00", "=Serving!$C$18"),
      ("etap", "η_p（prefill 占峰值；含折減）", "%", "0.0%", f"=INDEX(Calib!$C${CAL['etap']}:$G${CAL['etap']},{{X}}$6)*{{X}}{{prod}}"),
      ("etadm", "η_d 倍數（Tech_Registry H_ETAD；Sens_Perf 情境覆寫）", "x", "0.00", f"={TR['H_ETAD']}"),
      ("etad", "η_d（decode 每序列算力效率；含折減）", "%", "0.00%", f"=INDEX(Calib!$C${CAL['etad']}:$G${CAL['etad']},{{X}}$6)*{{X}}{{etadm}}*{{X}}{{prod}}"),
      ("tlm", "每層延遲倍數（Tech_Registry H_TL；Sens_Perf 情境覆寫）", "x", "0.00", f"={TR['H_TL']}"),
      ("tl", "每層每次前向固定延遲（含折減）", "µs", "#,##0", f"=INDEX(Calib!$C${CAL['tl']}:$G${CAL['tl']},{{X}}$6)*{{X}}{{tlm}}/{{X}}{{prod}}"),
      ("res", "HBM 保留比例", "%", "0%", "=Serving!$C$9"),
      ("shne", "非專家權重占 HBM 上限", "%", "0%", "=Serving!$C$10"),
      ("shex", "專家權重占 HBM 上限", "%", "0%", "=Serving!$C$11"),
      ("act", "EP 啟用值 bytes/元素", "B", "0.0", "=Serving!$C$12"),
      ("etam", "KV 讀取效率", "%", "0%", "=Serving!$C$13"),
      ("etal", "EP 通訊效率", "%", "0%", "=Serving!$C$14"),
      ("loadbw", "快取載入頻寬", "TB/s", "0.00", "=Serving!$C$15"),
      ("§", "D. 每 token 計算量"),
      ("attd", "decode 被注意 token 數", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxd},MIN({X}{ctxd},{X}{cap}))+(1-{X}{ff})*({X}{ctxd}/{X}{comp}+{X}{win})"),
      ("Fd", "decode FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attd})*{X}{hflop}/1E9"),
      ("attp", "prefill 被注意 token 數", "tok", "#,##0", "={X}{ff}*IF({X}{cap}=0,{X}{ctxp},MIN({X}{ctxp},{X}{cap}))+(1-{X}{ff})*({X}{ctxp}/{X}{comp}+{X}{win})"),
      ("Fp", "prefill FLOPs/token", "GFLOP", "#,##0.0", "=(2*{X}{A}*1E9+{X}{attc}*{X}{attp})*{X}{hflop}/1E9"),
      ("§", "E. 記憶體配置（attention DP＋wide EP；每 GPU）"),
      ("usable", "可用 HBM", "GB", "#,##0", "={X}{hbm}*(1-{X}{res})"),
      ("tpa", "注意力 TP 度（自動）", "", "0", "=MAX(1,CEILING({X}{ne}*{X}{bn}/({X}{shne}*{X}{usable}),1))"),
      ("epw", "decode EP 寬度（自動）", "GPU", "#,##0", "=MAX({X}{epb},CEILING({X}{ex}*{X}{be}/({X}{shex}*{X}{usable}),1))"),
      ("W", "每 GPU 權重", "GB", "#,##0.0", "={X}{ne}*{X}{bn}/{X}{tpa}+{X}{ex}*{X}{be}/{X}{epw}"),
      ("wsh", "權重占可用 HBM", "%", "0%", "={X}{W}/{X}{usable}"),
      ("§", "F. Prefill（算力受限）"),
      ("Pp", "prefill tok/s（每 prefill GPU）", "tok/s", "#,##0", "={X}{etap}*{X}{P}*1E15/({X}{Fp}*1E9)"),
      ("ttftv", "TTFT（計算部分）", "s", "0.00", "={X}{isl}*{X}{Fp}*1E9/({X}{etap}*{X}{P}*1E15*{X}{ninst})"),
      ("ttok", "TTFT 符合上限", "", None, "=IF({X}{ttftv}<={X}{ttft},\"是\",\"否\")"),
      ("§", "G. Decode：每步時間＝固定延遲＋B × 每序列時間；B* ＝ min(SLO 上限, HBM 容量上限)"),
      ("tfix", "每步固定延遲（權重讀取＋逐層延遲）", "ms", "#,##0.00", "={X}{W}/{X}{bw}+({X}{L}+{X}{N})*{X}{tl}/1000"),
      ("ccmp", "每序列每步 — 算力項", "ms", "0.0000", "=({X}{N}+1)*{X}{Fd}/({X}{P}*{X}{etad})/1000"),
      ("ckv", "每序列每步 — KV 讀取項", "ms", "0.0000", "={X}{kv}*{X}{ctxd}/({X}{bw}*{X}{etam})/1E9"),
      ("ccom", "每序列每步 — EP 通訊項", "ms", "0.0000", "=({X}{N}+1)*{X}{L}*{X}{k}*{X}{d}*{X}{act}*({X}{epw}-1)/{X}{epw}/({X}{link}*{X}{etal})/1E9"),
      ("ceff", "每序列每步（取最大，假設三者可重疊）", "ms", "0.0000", "=MAX({X}{ccmp},{X}{ckv},{X}{ccom})"),
      ("cbind", "每序列綁定項", "", None, "=IF({X}{ceff}={X}{ccmp},\"算力\",IF({X}{ceff}={X}{ckv},\"KV 頻寬\",\"EP 通訊\"))"),
      ("bslo", "SLO 允許的批次上限", "序列/GPU", "#,##0.0", "=(1000*{X}{a}/{X}{s}-{X}{tfix})/{X}{ceff}"),
      ("bcap", "HBM 容量允許的批次上限", "序列/GPU", "#,##0", "=({X}{usable}-{X}{W})*1E9/({X}{kv}*{X}{ctxd})"),
      ("B", "採用批次 B*", "序列/GPU", "#,##0.0", "=MAX(0,MIN({X}{bslo},{X}{bcap}))"),
      ("D", "decode tok/s（每 decode GPU）", "tok/s", "#,##0", "=IF({X}{B}>0,{X}{B}*{X}{a}/(({X}{tfix}+{X}{B}*{X}{ceff})/1000),0)"),
      ("spd", "實際每用戶速度", "tok/s", "#,##0", "=IF({X}{B}>0,{X}{a}/(({X}{tfix}+{X}{B}*{X}{ceff})/1000),0)"),
      ("bind", "綁定約束", "", None, "=IF({X}{B}<=0,\"SLO 不可達\",IF({X}{bslo}<={X}{bcap},\"SLO（\"&{X}{cbind}&\"）\",\"HBM 容量\"))"),
      ("kvsh", "KV 占可用 HBM", "%", "0%", "={X}{B}*{X}{kv}*{X}{ctxd}/1E9/{X}{usable}"),
      ("§", "H. 每架與每 GW（參考任務；P:D 依工作量配比；100% 利用率）"),
      ("gsr", "每請求 GPU 秒", "GPU-s", "0.000", "=IF({X}{D}>0,{X}{isl}/{X}{Pp}+{X}{osl}/{X}{D},0)"),
      ("psh", "prefill GPU 占比", "%", "0%", "=IF({X}{gsr}>0,({X}{isl}/{X}{Pp})/{X}{gsr},0)"),
      ("rtot", "每架總 tok/s", "tok/s", "#,##0", "=IF({X}{gsr}>0,{X}{gpus}*({X}{isl}+{X}{osl})/{X}{gsr},0)"),
      ("rdec", "每架 decode tok/s", "tok/s", "#,##0", "={X}{rtot}*{X}{osl}/({X}{isl}+{X}{osl})"),
      ("rpre", "每架 prefill tok/s", "tok/s", "#,##0", "={X}{rtot}-{X}{rdec}"),
      ("gwtot", "每 GW 總產出", "M tok/年", "#,##0", "={X}{rtot}*{X}{racks}*8760*3600/1E6"),
      ("gwdec", "每 GW decode 產出", "M tok/年", "#,##0", "={X}{rdec}*{X}{racks}*8760*3600/1E6"),
      ("§", "I. 每 M token GPU 秒（供 Unit_Cost）與速覽成本"),
      ("gsf", "新鮮 prefill", "GPU-s/M", "#,##0.0", "=1E6/{X}{Pp}"),
      ("gsc", "快取命中 prefill（KV 載入）", "GPU-s/M", "#,##0.000", "=1E6*{X}{kv}/({X}{loadbw}*1E12)"),
      ("gsd", "decode（含思考 token；0＝SLO 不可達）", "GPU-s/M", "#,##0.0", "=IF({X}{D}>0,1E6/{X}{D},0)"),
      ("cfq", "速覽：新鮮 prefill $/M（經濟、基準成本、100%）", "$/M", "#,##0.000", "=INDEX(DC_Cost!$C$58:$Q$58,3*({X}$6-1)+2)/3600*{X}{gsf}"),
      ("cdq", "速覽：decode $/M（經濟、基準成本、100%）", "$/M", "#,##0.000", "=IF({X}{gsd}>0,INDEX(DC_Cost!$C$58:$Q$58,3*({X}$6-1)+2)/3600*{X}{gsd},0)"),
      ("§", "J. 能量下限與閉合（能量閉合：物理下限功率 ≤ 機架平均用電）"),
      ("eflop", "運算能量", "pJ/FLOP", "0.000", "={X}{gpuw}*Energy!$C$5/({X}{P}*1E15)*1E12"),
      ("elink", "EP 通訊能量", "pJ/B", "0", "=IF({X}$6=1,Energy!$C$7,Energy!$C$6)"),
      ("fpt", "decode FLOPs/接受 token（含草稿驗證）", "GFLOP", "#,##0.0", "=({X}{N}+1)*{X}{Fd}/{X}{a}"),
      ("bpt", "decode HBM 讀取/接受 token", "GB", "0.000", "=IF({X}{B}>0,({X}{W}+{X}{B}*{X}{kv}*{X}{ctxd}/1E9)/({X}{B}*{X}{a}),0)"),
      ("cpt", "decode EP 傳輸/接受 token", "GB", "0.0000", "=({X}{N}+1)*{X}{L}*{X}{k}*{X}{d}*{X}{act}/{X}{a}/1E9"),
      ("Edec", "decode 物理下限能量", "J/tok", "0.0000", "=({X}{fpt}*{X}{eflop}+{X}{bpt}*{X}{ehbm}+{X}{cpt}*{X}{elink})/1000"),
      ("Epre", "prefill 物理下限能量", "J/tok", "0.0000", "={X}{Fp}*{X}{eflop}/1000"),
      ("pphys", "物理下限功率（每架）", "kW", "#,##0.0", "=({X}{rpre}*{X}{Epre}+{X}{rdec}*{X}{Edec})/1000"),
      ("pavg", "機架平均用電（Block 1 假設）", "kW", "#,##0.0", "={X}{kw}*Inputs!$E$10"),
      ("close", "閉合比（下限 ÷ 平均用電；須 ≤ 100%）", "%", "0%", "=IF({X}{pavg}>0,{X}{pphys}/{X}{pavg},0)"),
      ("tpj", "tokens／焦耳（總 token，平均用電口徑）", "tok/J", "#,##0.00", "={X}{rtot}/({X}{pavg}*1000)"),
      ("jdec", "每 decode token 實際能量（平均用電口徑）", "J/tok", "0.000", "=IF({X}{rdec}>0,{X}{pavg}*1000*(1-{X}{psh})/{X}{rdec},0)"),
    ]

KEY_ROWS = {"D", "rtot", "gwtot", "cdq", "cfq", "bind", "close", "tpj", "B"}

def write_perf(ws, cols, SP, AR, CAL, TR, start=9, overrides=None, label_col_width=42, ov_link=False):
    """cols: list of column letters; header rows 4-7 already written. overrides: {col: {key: value}}.
    ov_link=True: overrides are standing links (green, no fill) rather than scenario changes (blue on yellow)."""
    overrides = overrides or {}
    R = {}; r = start
    spec = perf_rows(SP, AR, CAL, TR)
    for item in spec:
        if item[0] == "§":
            section(ws, r, item[1], 2 + len(cols)); r += 1; continue
        key, lab, unit, fmt, tpl = item
        R[key] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in cols:
            ov = overrides.get(X, {})
            if key in ov:
                v = ov[key].replace("{X}", X) if isinstance(ov[key], str) else ov[key]
                if ov_link and isinstance(v, str):
                    put(ws, f"{X}{r}", v, F_LINK, fmt=fmt)
                else:
                    put(ws, f"{X}{r}", v, F_IN, fmt=fmt, fill=PatternFill("solid", fgColor="FFFFFF00"))
                continue
            if isinstance(tpl, (int, float)):
                put(ws, f"{X}{r}", tpl, F_IN, fmt=fmt); continue
            m = dict(R); m["X"] = X
            f = tpl.format(**m)
            put(ws, f"{X}{r}", f, fmt=fmt, fill=FILL_KEY if key in KEY_ROWS else None)
        r += 1
    ws.column_dimensions["A"].width = label_col_width
    ws.column_dimensions["B"].width = 10
    return R, r
```

## outputs.py

```python
from common import *
from perf import write_perf

GEN_NAMES_IDX = [1, 2, 3, 4, 5]
COLS15 = [L(i) for i in range(3, 18)]  # C..Q

def perf_sheet(wb, SP, AR, CAL, TR):
    ws = wb.create_sheet("Perf", 6)
    title(ws, "Perf — 每架產出引擎（世代 × 層級；各層級 SLO 與參考任務；100% 利用率）",
          "decode：每步時間＝固定延遲＋B × 每序列時間；在 SLO 下解出批次 B*，再受 HBM 容量限制。prefill 為算力受限。黃底為關鍵輸出")
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD); put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    for i, X in enumerate(COLS15):
        g, t = i // 3 + 1, i % 3 + 1
        put(ws, f"{X}6", g, fmt="0"); put(ws, f"{X}7", t, fmt="0")
        put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
        put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
        ws.column_dimensions[X].width = 13
    R, r = write_perf(ws, COLS15, SP, AR, CAL, TR)
    # VR-eq row (15-col layout only)
    section(ws, r, "K. VR-eq（每 GW 產出 ÷ VR200 同層級）", 17); r += 1
    R["vreq"] = r
    put(ws, f"A{r}", "VR-eq 係數"); put(ws, f"B{r}", "x")
    for X in COLS15:
        put(ws, f"{X}{r}", f"=IF(INDEX($C${R['gwtot']}:$Q${R['gwtot']},9+{X}$7)>0,{X}{R['gwtot']}/INDEX($C${R['gwtot']}:$Q${R['gwtot']},9+{X}$7),0)", fmt="0.00", fill=FILL_KEY)
    ws.freeze_panes = "C8"
    return R

SCEN = [  # label, vr overrides, gb overrides, tier
 ("基準", {}, {}, 2),
 ("VR η_d × 0.5（新世代軟體未成熟）", {"etadm": 0.5}, {}, 2),
 ("VR η_d × 1.5", {"etadm": 1.5}, {}, 2),
 ("VR 每層延遲 × 0.7", {"tlm": 0.7}, {}, 2),
 ("VR 每層延遲 × 1.5", {"tlm": 1.5}, {}, 2),
 ("VR 峰值 50 PF（J2 高情境）", {"P": 50}, {}, 2),
 ("SLO 40 tok/s", {"s": 40}, {"s": 40}, 2),
 ("SLO 100 tok/s", {"s": 100}, {"s": 100}, 2),
 ("MTP 接受率 0.60", {"alpha": 0.6}, {"alpha": 0.6}, 2),
 ("MTP 接受率 0.80", {"alpha": 0.8}, {"alpha": 0.8}, 2),
 ("ISL 4K", {"isl": 4096}, {"isl": 4096}, 2),
 ("ISL 64K", {"isl": 65536}, {"isl": 65536}, 2),
 ("生產折減 0.7（兩世代）", {"prod": 0.7}, {"prod": 0.7}, 2),
 ("Astra KV 情境 1（混合）", {"kv": "=Arch!$E$21"}, {"kv": "=Arch!$E$21"}, 3),
 ("Astra KV 情境 2（全層 MLA，基準）", {"kv": "=Arch!$E$22"}, {"kv": "=Arch!$E$22"}, 3),
 ("Astra KV 情境 3（GQA-8）", {"kv": "=Arch!$E$23"}, {"kv": "=Arch!$E$23"}, 3),
]

def sens_sheet(wb, SP, AR, CAL, TR):
    ws = wb.create_sheet("Sens_Perf", 7)
    title(ws, "Sens_Perf — VR200 對 GB300 的單變數敏感度（先看敏感度，再看基準）",
          "每組兩欄：左 VR200、右 GB300。黃底藍字＝該情境改動的輸入。GB300 為校準世代，VR200 的 η_d 與每層延遲為沿用值 [Analogy]，故 VR 專屬情境只動 VR 欄")
    cols, ov = [], {}
    for i, (lab, vo, go, t) in enumerate(SCEN):
        xv, xg = L(3 + 2 * i), L(4 + 2 * i)
        cols += [xv, xg]; ov[xv] = vo; ov[xg] = go
        put(ws, f"{xv}3", lab, F_BOLD, wrap=True)
        ws.merge_cells(f"{xv}3:{xg}3")
        for X, g in ((xv, 4), (xg, 3)):
            put(ws, f"{X}6", g, fmt="0"); put(ws, f"{X}7", t, fmt="0")
            put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
            put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
            ws.column_dimensions[X].width = 12.5
    ws.row_dimensions[3].height = 44
    put(ws, "A3", "情境", F_BOLD); put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD)
    put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    R, r = write_perf(ws, cols, SP, AR, CAL, TR, overrides=ov)
    section(ws, r, "L. VR200 ÷ GB300（同一情境；每 GW 口徑）", 2 + len(cols)); r += 1
    R["rgw"], R["rcost"] = r, r + 1
    put(ws, f"A{r}", "VR200 ÷ GB300：每 GW 總產出"); put(ws, f"B{r}", "x")
    put(ws, f"A{r+1}", "VR200 ÷ GB300：decode $/M（經濟、基準）"); put(ws, f"B{r+1}", "x")
    for i in range(len(SCEN)):
        xv, xg = L(3 + 2 * i), L(4 + 2 * i)
        put(ws, f"{xv}{r}", f"=IF({xg}{R['gwtot']}>0,{xv}{R['gwtot']}/{xg}{R['gwtot']},0)", fmt="0.00", fill=FILL_KEY)
        put(ws, f"{xv}{r+1}", f"=IF(AND({xg}{R['cdq']}>0,{xv}{R['cdq']}>0),{xv}{R['cdq']}/{xg}{R['cdq']},0)", fmt="0.00", fill=FILL_KEY)
    ws.freeze_panes = "C8"
    return R

def unit_cost(wb, PR):
    ws = wb.create_sheet("Unit_Cost", 8)
    title(ws, "Unit_Cost — 每 M token 成本（世代 × 成本情境；依層級分區；新鮮 prefill／快取 prefill／decode）",
          "成本＝每 GPU 小時持有成本（DC_Cost）× 每 M token GPU 秒（Perf）。思考 token 在物理上與可見輸出同為 decode，成本相同，差異只在計費（Block 4）。100% 為理想上限；基準利用率版＝100% 版 ÷ 利用率。快取命中只計 KV 載入 GPU 時間，未計儲存成本")
    ws.column_dimensions["A"].width = 46; ws.column_dimensions["B"].width = 10
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "成本情境", F_BOLD); put(ws, "A6", "世代索引", F_BOLD)
    for i, X in enumerate(COLS15):
        put(ws, f"{X}4", f"=DC_Cost!{X}4", F_HLINK); put(ws, f"{X}5", f"=DC_Cost!{X}5", F_HLINK)
        put(ws, f"{X}6", i // 3 + 1, fmt="0"); ws.column_dimensions[X].width = 12.5
    U = {}
    section(ws, 7, "共用", 17)
    for r, lab, unit, f, fmt in [(8, "每 GPU 小時持有成本 — 經濟", "$/GPU-hr", "=DC_Cost!{X}58", "#,##0.00"),
                                 (9, "每 GPU 小時持有成本 — 會計", "$/GPU-hr", "=DC_Cost!{X}57", "#,##0.00"),
                                 (10, "基準利用率", "%", "=Serving!$C$17", "0%")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in COLS15: put(ws, f"{X}{r}", f.format(X=X), fmt=fmt)
    r = 12
    tiers = ["Luna（低層）", "Sol（中層）", "Astra（頂層）"]
    for t in (1, 2, 3):
        section(ws, r, f"{tiers[t-1]}", 17); r += 1
        pl = lambda key: f"=INDEX(Perf!$C${PR[key]}:$Q${PR[key]},3*({{X}}$6-1)+{t})"
        rows = [
          ("gsf", "GPU 秒／M 新鮮 prefill", "GPU-s", "#,##0.0", pl("gsf")),
          ("gsc", "GPU 秒／M 快取命中 prefill", "GPU-s", "#,##0.000", pl("gsc")),
          ("gsd", "GPU 秒／M decode（含思考 token；0＝SLO 不可達）", "GPU-s", "#,##0.0", pl("gsd")),
          ("cf", "新鮮 prefill $/M — 經濟、100%", "$/M", "#,##0.000", "={X}$8/3600*{X}{gsf}"),
          ("cc", "快取命中 prefill $/M — 經濟、100%", "$/M", "#,##0.0000", "={X}$8/3600*{X}{gsc}"),
          ("cd", "decode（含思考 token）$/M — 經濟、100%", "$/M", "#,##0.000", "=IF({X}{gsd}>0,{X}$8/3600*{X}{gsd},\"SLO 不可達\")"),
          ("cfu", "新鮮 prefill $/M — 經濟、基準利用率", "$/M", "#,##0.000", "={X}{cf}/{X}$10"),
          ("ccu", "快取命中 prefill $/M — 經濟、基準利用率", "$/M", "#,##0.0000", "={X}{cc}/{X}$10"),
          ("cdu", "decode（含思考 token）$/M — 經濟、基準利用率", "$/M", "#,##0.000", "=IF(ISNUMBER({X}{cd}),{X}{cd}/{X}$10,{X}{cd})"),
          ("cda", "decode（含思考 token）$/M — 會計、100%", "$/M", "#,##0.000", "=IF({X}{gsd}>0,{X}$9/3600*{X}{gsd},\"SLO 不可達\")"),
          ("cref", "參考請求混合 $/M 總 token — 經濟、100%", "$/M", "#,##0.000",
           f"=IF(ISNUMBER({{X}}{{cd}}),(Serving!${'CDE'[t-1]}$23*{{X}}{{cf}}+Serving!${'CDE'[t-1]}$24*{{X}}{{cd}})/(Serving!${'CDE'[t-1]}$23+Serving!${'CDE'[t-1]}$24),{{X}}{{cd}})"),
        ]
        for key, lab, unit, fmt, tpl in rows:
            U[(t, key)] = r
            put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
            m = {k2: U[(t, k2)] for (tt, k2) in U if tt == t}
            for X in COLS15:
                mm = dict(m); mm["X"] = X
                put(ws, f"{X}{r}", tpl.format(**mm), fmt=fmt, fill=FILL_KEY if key in ("cd", "cf", "cdu") else None)
            r += 1
        r += 1
    ws.freeze_panes = "C7"
    return U

def workload(wb, U):
    # v5.9：harness 參數組（L1）。列 5–14 為標準檔（中立 harness）輸入；B 節為有效參數＝標準＋w ×（選定檔案−標準），
    # w＝Tech_Registry T12 開關 × 採用比例（B5_W）。w＝0 時與 v5.8 逐格一致
    ws = wb.create_sheet("Workload", 5)
    title(ws, "Workload — 任務制工作負載（每任務的 token 結構；思考 token 在物理上屬 decode）",
          "任務組合權重不在第 0 層（J5）；本頁只定義標準任務。列 5–14＝標準 harness；harness 檔案在 Har_In，依 Tech_Registry T12 混合（Block 5，L1）")
    for c, w in zip("ABCDEFGH", [40, 10, 14, 14, 16, 16, 18, 70]): ws.column_dimensions[c].width = w
    tasks = ["一般聊天", "推理聊天", "單代理（工具迴圈）", "多代理研究", "Coding agent（長程）"]
    put(ws, "A4", "參數", F_BOLD); put(ws, "B4", "單位", F_BOLD)
    for c, t in zip("CDEFG", tasks): put(ws, f"{c}4", t, F_BOLD, wrap=True)
    put(ws, "H4", "說明", F_BOLD); ws.row_dimensions[4].height = 30
    ins = [
      (5, "輪數 T", "輪", [1, 1, 4, 4, 30], "#,##0", "Assumed"),
      (6, "初始上下文 S（系統提示、歷史、工具定義）", "tok", [2000, 2000, 3000, 3000, 12000], "#,##0", "Assumed"),
      (7, "每輪新輸入 u（使用者或工具結果）", "tok", [500, 500, 1200, 1200, 2000], "#,##0", "Assumed"),
      (8, "每輪思考 token h", "tok", [0, 3000, 400, 400, 600], "#,##0", "Assumed；服務端思考占比待查"),
      (9, "每輪可見輸出 o", "tok", [500, 700, 200, 200, 400], "#,##0", "Assumed"),
      (10, "思考保留於上下文比例 ρ", "%", [0, 0, 0, 0, 0], "0%", "Assumed：多數 API 不保留前輪思考（標準 harness）"),
      (11, "歷史快取命中率 χ", "%", [0.5, 0.5, 0.9, 0.9, 0.9], "0%", "Assumed；代理迴圈前綴重用高"),
      (12, "並行子代理數 m", "個", [0, 0, 0, 3, 0], "0", "Assumed：子代理沿用單代理參數"),
      (13, "harness token 倍數", "x", [1, 1, 1, 1, 1], "0.00", "v5.9 起為殘差倍數（預設 1.0）；harness 效果改由 Har_In 參數組表達（L1）"),
      (14, "歷史保留比 c（壓縮後保留的歷史比例；1＝不壓縮）", "x", [1, 1, 1, 1, 1], "0.00", "標準 harness 不壓縮；v5.9 新增（L1）"),
    ]
    for r, lab, unit, vals, fmt, note in ins:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDEFG", vals): put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE)
    section(ws, 16, "有效參數（標準＋w ×（Har_In 選定檔案−標準）；w＝B5_W）", 8)
    eff = [  # row, label, unit, formula, fmt
      (17, "harness 混合權重 w（Tech_Registry T12 開關 × 採用比例）", "x", "=B5_W", "0.00"),
      (18, "有效輪數 T", "輪", "={c}5*(1+B5_W*(INDEX(B5_SelT,1,{k})-1))", "#,##0.0"),
      (19, "有效每輪思考 h", "tok", "={c}8*(1+B5_W*(INDEX(B5_SelH,1,{k})-1))", "#,##0"),
      (20, "有效思考保留 ρ", "%", "={c}10+B5_W*(INDEX(B5_SelRho,1,{k})-{c}10)", "0%"),
      (21, "有效快取命中 χ", "%", "=MIN(1,MAX(0,{c}11+B5_W*INDEX(B5_SelDChi,1,{k})))", "0%"),
      (22, "有效子代理數 m", "個", "={c}12+B5_W*INDEX(B5_SelDM,1,{k})", "0.0"),
      (23, "有效歷史保留比 c", "x", "={c}14+B5_W*(INDEX(B5_SelC,1,{k})-{c}14)", "0.00"),
    ]
    for r, lab, unit, f, fmt in eff:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for i, c in enumerate("CDEFG"):
            put(ws, f"{c}{r}", f.format(c=c, k=i + 1), fmt=fmt)
    section(ws, 25, "導出（每任務；用有效參數）", 8)
    der = [
      (26, "每輪上下文增量 u＋o＋ρh", "tok", "={c}7+{c}9+{c}20*{c}19", "#,##0"),
      (27, "單代理輸入總量", "tok", "={c}18*({c}6+{c}7)+{c}23*{c}26*{c}18*({c}18-1)/2", "#,##0"),
      (28, "其中可快取（前綴）", "tok", "={c}21*({c}18*{c}6+{c}23*{c}26*{c}18*({c}18-1)/2)", "#,##0"),
      (29, "其中新鮮", "tok", "={c}27-{c}28", "#,##0"),
      (30, "單代理 decode（思考＋可見）", "tok", "={c}18*({c}19+{c}9)", "#,##0"),
      (31, "系統倍數（1＋m）× harness 殘差倍數", "x", "=(1+{c}22)*{c}13", "0.00"),
      (32, "任務新鮮 prefill", "tok", "={c}29*{c}31", "#,##0"),
      (33, "任務快取 prefill", "tok", "={c}28*{c}31", "#,##0"),
      (34, "任務 decode", "tok", "={c}30*{c}31", "#,##0"),
      (35, "任務總 token", "tok", "={c}32+{c}33+{c}34", "#,##0"),
      (36, "decode 平均上下文", "tok", "={c}6+{c}7+({c}18-1)/2*{c}23*{c}26+({c}19+{c}9)/2", "#,##0"),
      (37, "思考占 decode", "%", "=IF({c}19+{c}9>0,{c}19/({c}19+{c}9),0)", "0%"),
      (38, "總 token ÷ 一般聊天", "x", "={c}35/$C$35", "0.0"),
      (39, "總 token ÷ 推理聊天", "x", "={c}35/$D$35", "0.0"),
    ]
    for r, lab, unit, f, fmt in der:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in "CDEFG": put(ws, f"{c}{r}", f.format(c=c), fmt=fmt, fill=FILL_KEY if r in (35, 38) else None)
    put(ws, "A40", "參照：Anthropic 揭露倍數（相對聊天）"); put(ws, "B40", "x")
    put(ws, "C40", 1, fmt="0"); put(ws, "E40", 4, fmt="0"); put(ws, "F40", 15, fmt="0")
    put(ws, "H40", "Interested-party：Anthropic 2025-06 多代理研究系統文章，agent 約 4 倍、多代理約 15 倍聊天 token（S25）。其『聊天』口徑未說明是否含思考，故兩個倍數並列。"
                   "本頁列 38 的單代理、多代理倍數高於此參照約 2.3–2.5 倍（Block 2 既有假設，未調整）", F_NOTE, wrap=True)
    put(ws, "H36", "Unit_Cost 的 decode 成本取各層級參考上下文；本列顯示任務實際上下文，差距大時看 Sens_Perf 的 ISL 情境", F_NOTE, wrap=True)
    section(ws, 42, "每任務成本（$／任務；經濟口徑、基準成本情境、基準利用率；不含快取儲存，含儲存者見 Harness 頁）", 8)
    r = 43
    for gname, col in (("VR200", "M"), ("GB300", "J")):
        for t, tn in zip((1, 2, 3), ("Luna", "Sol", "Astra")):
            put(ws, f"A{r}", f"{gname} × {tn}"); put(ws, f"B{r}", "$")
            cf, cc, cd = U[(t, "cfu")], U[(t, "ccu")], U[(t, "cdu")]
            for c in "CDEFG":
                put(ws, f"{c}{r}", f"=IF(ISNUMBER(Unit_Cost!{col}{cd}),({c}32*Unit_Cost!{col}{cf}+{c}33*Unit_Cost!{col}{cc}+{c}34*Unit_Cost!{col}{cd})/1E6,\"SLO 不可達\")",
                    fmt="$#,##0.0000", fill=FILL_KEY if tn == "Sol" else None)
            r += 1
    ws.freeze_panes = "C5"
    return {"fp": 32, "cp": 33, "dp": 34, "tot": 35, "cost0": 43, "S": 6, "u": 7, "h": 8, "o": 9, "rho": 10, "chi": 11, "m": 12,
            "res": 13, "c": 14, "T": 5}

def nonnv(wb):
    ws = wb.create_sheet("NonNV")
    title(ws, "NonNV — 非 NVIDIA 世代比例列（D2；全部 [Assumed]，以區間表示）",
          "每 GW 產出比與每 GW 持有成本比皆相對 VR200（同層級、同 SLO）。持有成本比預設接近 1，依 Block 1 結論：每 GW 持有成本幾乎不隨世代改變")
    hdr = ["候選", "產出比 低", "產出比 基準", "產出比 高", "持有比 低", "持有比 基準", "持有比 高",
           "每 token 成本比 基準", "最佳角落", "最差角落", "標記", "說明"]
    for i, h in enumerate(hdr): put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True)
    ws.row_dimensions[4].height = 30
    data = [
      ("AMD MI455X（Helios）", 0.5, 0.7, 1.0, 0.8, 0.9, 1.0, "MI355X 在 V4-Pro 上 26 天內吞吐提升 110 倍（S20 所屬部落格），軟體成熟度為主要不確定"),
      ("Google TPU v7 Ironwood", 0.6, 0.8, 1.1, 0.7, 0.8, 1.0, "自用為主，無公開同口徑實測"),
      ("AWS Trainium3", 0.3, 0.5, 0.8, 0.6, 0.7, 0.9, "OpenAI v0.5 以 2GW Trainium 合約為輸入"),
      ("Cerebras WSE-3", 0.2, 0.4, 0.8, 0.8, 1.0, 1.2, "高互動性利基；每 GW 吞吐低、單用戶速度高"),
      ("OpenAI／Broadcom 客製", 0.4, 0.6, 0.9, 0.7, 0.8, 1.0, "無公開規格；沿用 v0.5「自研／其他 0.6（0.4–1.0）」"),
    ]
    for i, (n, ol, ob, oh, hl, hb, hh, note) in enumerate(data):
        r = 5 + i
        put(ws, f"A{r}", n)
        for c, v in zip("BCDEFG", [ol, ob, oh, hl, hb, hh]): put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"H{r}", f"=F{r}/C{r}", fmt="0.00", fill=FILL_KEY)
        put(ws, f"I{r}", f"=E{r}/D{r}", fmt="0.00"); put(ws, f"J{r}", f"=G{r}/B{r}", fmt="0.00")
        put(ws, f"K{r}", "Assumed", F_NOTE); put(ws, f"L{r}", note, F_NOTE)
    for c, w in zip("ABCDEFGHIJKL", [26, 9, 9, 9, 9, 9, 9, 11, 9, 9, 10, 70]): ws.column_dimensions[c].width = w
    return ws
```

## training.py

```python
# Block 3 (v5.5): Tech_Registry, Train_In, Perf_Batch, Training, Sens_Train
from common import *
from perf import write_perf
from outputs import COLS15

# ---------------------------------------------------------------- Tech_Registry
HOOKS = [  # code, meaning, where it acts
    ("H_ETAD", "decode η_d 倍數", "Perf／Perf_Batch：etadm 列"),
    ("H_TL", "每層延遲倍數", "Perf／Perf_Batch：tlm 列"),
    ("H_FLOP", "每 token FLOPs 倍數（推論與訓練）", "Perf／Perf_Batch：hflop 列；Training：hflop 列"),
    ("H_KV", "KV bytes/token 倍數", "Perf／Perf_Batch：hkv 列"),
    ("H_WB", "權重 bytes/param 倍數", "Perf／Perf_Batch：hwb 列"),
    ("H_TPK", "訓練峰值倍數", "Training：htpk 列"),
    ("H_MFU", "訓練 MFU 倍數", "Training：hmfu 列"),
    ("H_TOK", "達同等預訓練品質所需 token 倍數", "Training：htok 列"),
    ("H_ROLL", "rollout 效率倍數", "Training：hroll 列"),
    ("H_CAP", "能力增量（Block 4 占位，尚無作用）", "Block 4"),
    ("H_HAR", "harness（v5.9 起不作倍數；T12 的開關 × 採用比例＝Har_In 混合權重 w）", "Har_In → Workload B 節、Harness"),
]

# id, tech, hook, acts-on, lo, base, hi, sel, status, labs, override, in-base, adopt, switch, tag, source/note, trigger
ENTRIES = [
 ("T01", "MTP 推測解碼", "—", "Serving!C6:C8（N、α）", 1, 1, 1, 2, "主流", 3, "", "是", 1, 1, "Verified",
  "DeepSeek V3／V4、GLM-4.5、MiMo 公開採用；已在 Serving 基準", "—"),
 ("T02", "壓縮／稀疏注意力（CSA/HCA 類）", "—", "Arch 列 16–19", 1, 1, 1, 2, "主流", 3, "", "是", 1, 1, "Verified",
  "DeepSeek V4 CSA/HCA、DeepSeek／GLM 稀疏注意力、Qwen3-Next 混合注意力；Luna／Sol 基準已含（S27、S35）", "—"),
 ("T03", "FP4 權重推論（NVFP4／MXFP4）", "—", "Spec_Rack 專家 bytes/param", 1, 1, 1, 2, "主流", 2, "", "是", 1, 1, "Verified",
  "DeepSeek V4 原生 FP4 專家權重、OpenAI gpt-oss MXFP4；已在基準", "—"),
 ("T04", "FP4 量化感知訓練（後訓練）", "—", "Spec_Rack 專家 bytes/param", 1, 1, 1, 2, "主流", 2, "", "是", 1, 1, "Interested-party",
  "DeepSeek V4：主權重量化到 FP4 再反量化到 FP8 計算，沿用 FP8 訓練框架（S35）", "—"),
 ("T05", "On-policy 蒸餾（多專家整合）", "—", "Training G 節", 1, 1, 1, 2, "主流", 2, "", "是", 1, 1, "Interested-party",
  "DeepSeek V4（專家 SFT＋GRPO 後以 on-policy 蒸餾整合，S35）、Qwen3；已在 Training 基準", "—"),
 ("T06", "Muon 優化器", "H_TOK", "預訓練所需 token", 0.7, 0.85, 1, 2, "早期採用", 2, "", "是", 1, 0, "Interested-party",
  "Moonshot Kimi K2、DeepSeek V4 採用；Luna／Sol 的 token 數為實際值，已隱含其效果，故不套倍數", "第三家前沿實驗室採用，或公開同品質 token 節省的對照實驗"),
 ("T07", "NVFP4 預訓練", "H_TPK", "訓練峰值", 1.5, 2, 3, 2, "早期採用", 1, "", "否", 1, 0, "Interested-party",
  "倍數＝NVFP4 訓練峰值 ÷ FP8（VR 35/17.5＝2；GB300 15/5＝3 [Assumed]）。NVIDIA 公開 12B 模型 10T token NVFP4 預訓練；前沿實驗室未見公開採用。MFU 可能同步下降，未計", "任一前沿實驗室公開以 FP4 完成主預訓練"),
 ("T08", "Looped transformer（權重共享迴圈）— 計算量", "H_FLOP", "每 token FLOPs", 1.5, 2, 4, 2, "研究", 0, "", "否", 1, 0, "Assumed",
  "同一組權重迴圈 k 次：FLOPs × k、權重 bytes × 1；能力增量於 Block 4（H_CAP）處理", "前沿模型卡或技術報告揭露迴圈深度"),
 ("T09", "Looped transformer — 每層延遲", "H_TL", "每步逐層延遲", 1.5, 2, 4, 2, "研究", 0, "", "否", 1, 0, "Assumed",
  "迴圈使有效層數 × k，逐層延遲同比增加；與 T08 同時開關", "同 T08"),
 ("T10", "非同步 RL（rollout 與訓練解耦、部分 rollout）", "H_ROLL", "rollout 效率", 1.2, 1.4, 1.6, 2, "主流", 4, "", "是", 1, 0, "Interested-party",
  "旗艦模型公開採用：DeepSeek V4.1（幾乎全部 RL 與 OPD，S45）、Zhipu GLM-5（slime，S46）、Moonshot Kimi-Researcher（完全非同步 rollout，S47）、Meta Llama 3（LlamaRL，S48）。閉源四家未找到披露。v5.6 起併入基準：Train_In rollout 效率 0.85（Andy 2026-10-01 決定 (a)）", "閉源實驗室披露同步做法，或前沿規模對照實驗顯示 off-policy 偏差抵銷吞吐增益"),
 ("T11", "KV 快取壓縮（FP4 KV 等）", "H_KV", "KV bytes/token", 0.5, 0.5, 0.75, 2, "早期採用", 1, "", "否", 1, 0, "Assumed",
  "FP8 → FP4 KV：bytes × 0.5；準確率損失待查", "第二家實驗室在生產服務公開採用"),
 ("T12", "Harness（代理框架）", "H_HAR", "Har_In 選定檔案（混合權重 w＝開關 × 採用比例）", 1, 1, 1, 2, "追蹤中", 0, "", "否", 1, 0, "Assumed",
  "v5.9：harness 以參數組表達（輪數、思考保留、思考量、歷史壓縮、快取命中、子代理、狀態保留）加成功率（L1、L2）；倍數欄不使用。基準不開（L3）。"
  "ARC-AGI-3（ARC Prize 自測）：GPT-6 Astra 標準 harness 最高推理 62.7%、$26,098 → OpenAI Provider Adapter 同檔 98.6%、$17,332（S58）。主流判定（J14）尚未評估", 
  "中立方（ARC Prize、METR、Artificial Analysis）在同條件下測得第二個 harness 對照"),
]

def tech_registry(wb):
    ws = wb.create_sheet("Tech_Registry")
    title(ws, "Tech_Registry — 新技術登錄與掛鉤（每列＝技術 × 作用物理量；基準值只在『已在基準＝否』且開關＝1 時套用）",
          "有效倍數＝1＋開關 × 採用比例 ×（所選倍數−1）；已在基準者恆為 1，避免重複計算。主流判定（J14）：至少兩家實驗室公開採用；L 欄可由 Andy 覆寫")
    hdr = ["ID", "技術", "掛鉤代碼", "作用物理量", "倍數 低", "倍數 基準", "倍數 高", "情境（1／2／3）", "狀態",
           "公開採用實驗室數", "主流判定（J14）", "Andy 覆寫", "已在基準", "採用比例", "開關（0／1）", "有效倍數",
           "證據標記", "來源／說明", "下次檢查觸發", "一致性檢查"]
    widths = [6, 30, 10, 22, 8, 8, 8, 9, 10, 9, 10, 9, 8, 8, 8, 9, 14, 70, 36, 26]
    for i, (h, w) in enumerate(zip(hdr, widths)):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = w
    ws.row_dimensions[4].height = 30
    r0 = 5
    for i, e in enumerate(ENTRIES):
        r = r0 + i
        (eid, tech, hook, acts, lo, ba, hi, sel, st, labs, ovr, inb, adopt, sw, tag, src, trig) = e
        for c, v in zip("ABCD", (eid, tech, hook, acts)): put(ws, f"{c}{r}", v, wrap=(c == "B"))
        for c, v in zip("EFG", (lo, ba, hi)): put(ws, f"{c}{r}", v, fmt="0.00")
        put(ws, f"H{r}", sel, fmt="0"); put(ws, f"I{r}", st, F_IN); put(ws, f"J{r}", labs, fmt="0")
        put(ws, f"K{r}", f'=IF(J{r}>=2,"主流","非主流")')
        put(ws, f"L{r}", ovr if ovr else None, F_IN)
        put(ws, f"M{r}", inb, F_IN); put(ws, f"N{r}", adopt, fmt="0%"); put(ws, f"O{r}", sw, fmt="0")
        put(ws, f"P{r}", f'=IF(M{r}="是",1,1+O{r}*N{r}*(CHOOSE(H{r},E{r},F{r},G{r})-1))', fmt="0.00", fill=FILL_KEY)
        put(ws, f"Q{r}", tag, F_NOTE); put(ws, f"R{r}", src, F_NOTE, wrap=True); put(ws, f"S{r}", trig, F_NOTE, wrap=True)
        put(ws, f"T{r}", f'=IF(AND(IF(L{r}="",K{r},L{r})="主流",M{r}="否"),"主流但未入基準：須 Andy 判定",'
                         f'IF(AND(IF(L{r}="",K{r},L{r})="非主流",M{r}="是",I{r}<>"早期採用"),"非主流卻在基準","一致"))', wrap=True)
        ws.row_dimensions[r].height = 42
    r1 = r0 + len(ENTRIES) - 1
    r = r1 + 2
    section(ws, r, "掛鉤彙總（同一掛鉤多條目時取乘積；Perf、Perf_Batch、Training 連結本表 E 欄）", 20); r += 1
    for c, v in zip("ABCDE", ["代碼", "意義", "", "作用位置", "倍數"]): put(ws, f"{c}{r}", v, F_BOLD)
    r += 1
    TR = {}
    for code, meaning, where in HOOKS:
        put(ws, f"A{r}", code, F_BOLD); put(ws, f"B{r}", meaning); put(ws, f"D{r}", where, F_NOTE, wrap=True)
        put(ws, f"E{r}", f'=EXP(SUMPRODUCT(($C${r0}:$C${r1}="{code}")*LN($P${r0}:$P${r1})))', fmt="0.000", fill=FILL_KEY)
        TR[code] = f"Tech_Registry!$E${r}"; r += 1
    r += 1
    put(ws, f"A{r}", "注意", F_BOLD)
    put(ws, f"B{r}", "掛鉤作用於全部世代與層級。新條目：在表中插入一列（範圍內），填倍數、狀態與證據；開關預設 0。"
                     "Sens_Perf 的 η_d 與每層延遲情境為覆寫值，不受 Registry 影響。", F_NOTE, wrap=True)
    ws.merge_cells(f"B{r}:R{r}"); ws.row_dimensions[r].height = 30
    ws.freeze_panes = "C5"
    TR["_rows"] = (r0, r1)
    TR["_hooks"] = (r1 + 4, r1 + 3 + len(HOOKS))
    return TR

# ---------------------------------------------------------------- Train_In
ROUT_LUNA, ROUT_SOL, ROUT_ASTRA = 2.36, 2.36, 9.6   # v5.6: 由 v5.5 的 2, 2, 8 重校，維持 VR200 上 RL ÷ 預訓練 GPU 小時（J9 (a)）

def train_in(wb):
    ws = wb.create_sheet("Train_In")
    title(ws, "Train_In — 訓練輸入（藍字＝輸入；Analogy／Assumed 一律附區間）",
          "Block 3 命題：各層級代表模型從預訓練到可發布、以及含研發實驗的整個計畫，需要多少 GPU 小時、美元與 1 GW 年。決策 J7–J14 見 README")
    for c, w in zip("ABCDEFGH", [46, 12, 14, 14, 14, 14, 14, 90]): ws.column_dimensions[c].width = w
    T = {}
    put(ws, "A4", "全域設定", F_BOLD); put(ws, "B4", "單位", F_BOLD); put(ws, "C4", "值", F_BOLD); put(ws, "D4", "標記", F_BOLD); put(ws, "H4", "說明", F_BOLD)
    g = [
      ("prec", "訓練精度（MFU 分母）", "", "FP8 dense", None, "Decision", "J7：基準 FP8（DeepSeek V4 以 FP8 計算＋FP4 QAT，S35）；NVFP4 預訓練列於 Tech_Registry T07"),
      ("mfub", "預訓練 MFU 基準（FP8 分母；GB200／GB300）", "%", 0.25, "0%", "Analogy",
       "DeepSeek V3 推導 H800 FP8 口徑約 20%（Checks）；Llama 3 405B BF16 口徑 38–43%＝FP8 口徑約 19–22%（S37，待查）；NVL72 域大、EP 通訊較佳取 0.25。區間 0.15–0.40"),
      ("gp", "goodput（扣除故障、重啟、checkpoint 的有效時間比）", "%", 0.90, "0%", "Analogy", "Meta Llama 3：有效訓練時間 >90%（S37，待查）；區間 0.80–0.95"),
      ("sftk", "SFT MFU 係數（× 預訓練 MFU）", "x", 0.8, "0.00", "Assumed", "較短批次、較多變長序列；區間 0.6–1.0"),
      ("rlk", "RL trainer MFU 係數（× 預訓練 MFU）", "x", 0.6, "0.00", "Assumed", "長序列、小批次、與 rollout 交替；區間 0.4–0.9。蒸餾學生更新沿用"),
      ("ref", "參考模型前向（KL 懲罰；0＝無、1＝有）", "選擇", 0, "0", "Assumed", "GRPO 原版含 KL；DAPO 等後續做法移除。取 0，區間 0–1"),
      ("reff", "rollout 效率（長尾等待、權重同步、閒置）", "%", 0.85, "0%", "Analogy",
       "v5.6：非同步 RL 已屬主流（Tech_Registry T10）。各家報告非同步增益 1.5–2.7 倍（S45–S49）；同步約 0.4–0.5 → 非同步 0.85，區間 0.7–0.95。v5.5 為 0.6（混合）"),
      ("G", "GRPO 每題取樣數（共用 prompt，prefill 只算一次）", "個", 16, "0", "Analogy", "DeepSeekMath／R1 GRPO 群組 16；區間 8–64"),
      ("rdm", "研發倍數（研發總 GPU 小時 ÷ 最終訓練）", "x", 8, "0.0", "Analogy",
       "J10。Epoch：最終訓練占研發支出 OpenAI 9.6%、MiniMax 22.6%、Z.ai 12.3%（S38）＝4.4–10.4 倍；取 8。以支出為口徑，已含實驗的低利用率，故乘在 GPU 小時上"),
      ("rdmode", "研發歸屬", "", "家族合計乘一次，依最終訓練 GPU 小時比例分攤", None, "Decision",
       "J10。比例分攤下，各層級分得＝該層級最終訓練 × 倍數；Training J 節另列家族合計"),
      ("gtier", "合成資料生成層級（1 Luna／2 Sol／3 Astra）", "選擇", 3, "0", "Assumed", "以頂層模型生成；區間 2–3"),
      ("gdef", "下游預設訓練世代（世代索引）", "索引", 4, "0", "Decision", "J13：Andy 2026-09-30 決定 VR200（索引 4）；具名範圍 IF_TrainGenDefault"),
      ("galt", "並列訓練世代（世代索引）", "索引", 3, "0", "Decision", "J13：GB300（索引 3）並列；具名範圍 IF_TrainGenAlt"),
    ]
    r = 5
    for key, lab, unit, v, fmt, tag, note in g:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt, font=F_IN)
        put(ws, f"D{r}", tag, F_NOTE); put(ws, f"H{r}", note, F_NOTE, wrap=True)
        T[key] = r; r += 1
    for k in ("gdef", "galt"):
        put(ws, f"E{T[k]}", f"=INDEX(Spec_Rack!$C$4:$G$4,$C${T[k]})", F_HLINK)
    r += 1
    section(ws, r, "各世代", 8); r += 1
    put(ws, f"A{r}", "世代", F_BOLD)
    for c in "CDEFG": put(ws, f"{c}{r}", f"=Spec_Rack!{c}4", F_HLINK)
    r += 1
    T["mfug"] = r
    put(ws, f"A{r}", "預訓練 MFU 世代倍數"); put(ws, f"B{r}", "x")
    for c, v in zip("CDEFG", [0.8, 1, 1, 0.9, 0.9]): put(ws, f"{c}{r}", v, fmt="0.00")
    put(ws, f"H{r}", "Hopper 0.8 使 MFU＝20%，對應 V3 推導值 [Derived]；VR200 峰值 3.5 倍而 HBM 頻寬 2.75 倍，取 0.9 [Assumed，區間 0.7–1.1]；RU 同 VR [Assumed]", F_NOTE, wrap=True)
    r += 2
    section(ws, r, "各層級", 8); r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for c, t in zip("CDE", "CDE"): put(ws, f"{c}{r}", f"=Arch!{t}4", F_HLINK)
    put(ws, f"H{r}", "說明", F_BOLD); r += 1
    t = [
      ("ptok", "預訓練 token", "T", [32, 33, 60], "#,##0.0", "Verified：V4-Flash 32T、V4-Pro 33T（S35）；Astra [Assumed，區間 30–100T；J8 以 Arch 一致為基準，前沿錨點見 Checks]"),
      ("pseq", "預訓練序列長（dense 注意力）", "tok", [4096, 4096, 8192], "#,##0", "V4：4K → 16K 漸增，其間以 dense 注意力訓練（S35）；多數 token 在 4K [Assumed，區間 4K–16K]"),
      ("ltok", "長上下文延伸 token", "T", [1, 1, 2], "#,##0.0", "Assumed，區間 0.3–3T（V4 未揭露）"),
      ("lseq", "長上下文延伸序列長（稀疏注意力路徑）", "tok", [131072, 131072, 131072], "#,##0", "Assumed"),
      ("stok", "SFT token", "T", [0.05, 0.05, 0.1], "#,##0.00", "Assumed，區間 0.01–0.3T"),
      ("sseq", "SFT 序列長", "tok", [16384, 16384, 16384], "#,##0", "Assumed"),
      ("bs", "批次推論速度下限（rollout、合成、評測）", "tok/s", [20, 20, 20], "#,##0", "取代互動 SLO；過低時長尾拉長牆鐘時間 [Assumed，區間 10–40]"),
      ("risl", "rollout 參考輸入（prompt＋工具結果）", "tok", [4096, 8192, 16384], "#,##0", "Assumed"),
      ("rosl", "rollout 參考輸出（含思考）", "tok", [8192, 16384, 32768], "#,##0", "Assumed：推理與代理任務的長輸出"),
      ("rout", "RL rollout 輸出 token（含各領域專家）", "T", [ROUT_LUNA, ROUT_SOL, ROUT_ASTRA], "#,##0.00",
       "J9：由下而上輸入；基準值校到 VR200 上 RL ÷ 預訓練 GPU 小時約 Luna／Sol 0.3、Astra 1.0（結果見 Training rlH 列與 Checks）；v5.6 因 rollout 效率 0.6→0.85 由 2／2／8 上調為 2.36／2.36／9.6，GPU 小時不變（Andy 決定 (a)）。外部點：R1 約 5%、Grok 4 約 1 倍（S40、S42；GPU 小時或預算口徑）。區間：Luna／Sol 0.3–6T、Astra 2.5–25T"),
      ("dtok", "On-policy 蒸餾：學生 rollout 輸出 token", "T", [0.2, 0.2, 0.2], "#,##0.00", "Assumed，區間 0.05–1T"),
      ("dtea", "蒸餾教師層級（1／2／3）", "選擇", [1, 2, 3], "0", "V4 做法：同尺寸各領域專家為教師 [Interested-party，S35]"),
      ("syn", "合成資料生成 token", "T", [1, 2, 3], "#,##0.0", "Assumed，區間 0.5–10T"),
      ("ev", "評測 token", "T", [0.02, 0.05, 0.1], "#,##0.00", "Assumed"),
    ]
    for key, lab, unit, vals, fmt, note in t:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c, v in zip("CDE", vals): put(ws, f"{c}{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE, wrap=True)
        T[key] = r; r += 1
    for c in "CDE": ws[f"{c}{T['rout']}"].fill = FILL_KEY
    r += 1
    section(ws, r, "外部錨點（Checks 用；不進推導）", 8); r += 1
    a = [
      ("v3tok", "DeepSeek V3 預訓練 token", "T", 14.8, "#,##0.0", "Interested-party：DeepSeek V3 技術報告（S44）"),
      ("v3h", "DeepSeek V3 預訓練 H800 GPU 小時", "M", 2.664, "#,##0.000", "S44（全部 2.788M，含長上下文 0.119M、後訓練 0.005M）"),
      ("v3seq", "DeepSeek V3 預訓練序列長", "tok", 4096, "#,##0", "S44"),
      ("r1rl", "DeepSeek R1 RL GPU 小時 ÷ V3 預訓練", "x", 0.055, "0.0%", "147K ÷ 2.664M（S40，Lambert 轉述；GPU 小時口徑）"),
      ("grok", "Grok 4 RL ÷ 預訓練（宣稱）", "x", 1.0, "0.0", "Interested-party：xAI『預訓練規模』（S42）；口徑不明"),
      ("an1", "前沿預訓練錨點 低", "FLOP", 2e26, "0.0E+00", "Analogy：Epoch 估計（Grok-3 約 4.6e26，S39）；誤差 2–5 倍"),
      ("an2", "前沿預訓練錨點 中", "FLOP", 5e26, "0.0E+00", "同上"),
      ("an3", "前沿預訓練錨點 高", "FLOP", 2e27, "0.0E+00", "同上"),
    ]
    for key, lab, unit, v, fmt, note in a:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit); put(ws, f"C{r}", v, fmt=fmt)
        put(ws, f"H{r}", note, F_NOTE, wrap=True); T[key] = r; r += 1
    ws.freeze_panes = "C5"
    return T

# ---------------------------------------------------------------- Perf_Batch
def perf_batch(wb, SP, AR, CAL, TR, TI):
    ws = wb.create_sheet("Perf_Batch")
    title(ws, "Perf_Batch — 批次推論引擎（RL rollout、蒸餾、合成資料、評測）：與 Perf 同一套公式，只換速度下限與參考任務",
          "C–Q 欄＝世代 × 層級基準；R、S 欄＝VR200 以 FP8 rollout 的情境（J12 替代）。綠字＝連結 Train_In（非情境改動）；黃底＝情境改動")
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD); put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    put(ws, "A3", "欄位", F_BOLD)
    cols = COLS15 + ["R", "S"]
    for i, X in enumerate(cols):
        if i < 15: gi, t = i // 3 + 1, i % 3 + 1
        else: gi, t = 4, i - 13
        put(ws, f"{X}6", gi, fmt="0"); put(ws, f"{X}7", t, fmt="0")
        put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
        put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
        ws.column_dimensions[X].width = 13
    put(ws, "R3", "情境：FP8 rollout", F_BOLD); put(ws, "S3", "情境：FP8 rollout", F_BOLD)
    link = {"s": f"=INDEX(Train_In!$C${TI['bs']}:$E${TI['bs']},{{X}}$7)",
            "isl": f"=INDEX(Train_In!$C${TI['risl']}:$E${TI['risl']},{{X}}$7)",
            "osl": f"=INDEX(Train_In!$C${TI['rosl']}:$E${TI['rosl']},{{X}}$7)"}
    ov = {X: dict(link) for X in COLS15}
    R, r = write_perf(ws, COLS15, SP, AR, CAL, TR, overrides=ov, ov_link=True)
    # scenario columns (FP8 rollout on VR200): re-write the same rows into R, S with extra overrides
    fp8 = {"P": f"=Spec_Rack!$F${SP['tfp8']}", "be": 1, "bn": 1}
    for X in ("R", "S"):
        rr = 9
        from perf import perf_rows
        spec = perf_rows(SP, AR, CAL, TR)
        m = {}
        for item in spec:
            if item[0] == "§": rr += 1; continue
            key, lab, unit, fmt, tpl = item
            m[key] = rr
            if key in link:
                put(ws, f"{X}{rr}", link[key].replace("{X}", X), F_LINK, fmt=fmt)
            elif key in fp8:
                put(ws, f"{X}{rr}", fp8[key], F_IN, fmt=fmt, fill=PatternFill("solid", fgColor="FFFFFF00"))
            elif isinstance(tpl, (int, float)):
                put(ws, f"{X}{rr}", tpl, F_IN, fmt=fmt)
            else:
                mm = dict(m); mm["X"] = X
                put(ws, f"{X}{rr}", tpl.format(**mm), fmt=fmt)
            rr += 1
    section(ws, r, "L. 批次推論的有效 MFU（接受 token 的模型 FLOPs ÷ 峰值）", 19); r += 1
    R["mfu4"], R["mfu8"] = r, r + 1
    put(ws, f"A{r}", "decode 有效 MFU（對 Perf 計算用峰值）"); put(ws, f"B{r}", "%")
    put(ws, f"A{r+1}", "decode 有效 MFU（對 FP8 訓練峰值）"); put(ws, f"B{r+1}", "%")
    for X in cols:
        put(ws, f"{X}{r}", f"=IF({X}{R['D']}>0,{X}{R['D']}*{X}{R['Fd']}*1E9/({X}{R['P']}*1E15),0)", fmt="0.0%")
        put(ws, f"{X}{r+1}", f"=IF({X}{R['D']}>0,{X}{R['D']}*{X}{R['Fd']}*1E9/(INDEX(Spec_Rack!$C${SP['tfp8']}:$G${SP['tfp8']},{X}$6)*1E15),0)", fmt="0.0%", fill=FILL_KEY)
    ws.freeze_panes = "C8"
    return R

# ---------------------------------------------------------------- Training engine
def train_rows(SP, AR, TI, PB, TR):
    ti = lambda k: f"=INDEX(Train_In!$C${TI[k]}:$E${TI[k]},{{X}}$7)"
    tg = lambda k: f"=INDEX(Train_In!$C${TI[k]}:$G${TI[k]},{{X}}$6)"
    tgl = lambda k: f"=Train_In!$C${TI[k]}"
    sp = lambda row: f"=INDEX(Spec_Rack!$C${row}:$G${row},{{X}}$6)"
    ar = lambda row: f"=INDEX(Arch!$C${row}:$E${row},{{X}}$7)"
    dc = lambda row: f"=INDEX(DC_Cost!$C${row}:$Q${row},3*({{X}}$6-1)+2)"
    pb = lambda k: f"=INDEX(Perf_Batch!$C${PB[k]}:$Q${PB[k]},3*({{X}}$6-1)+{{X}}$7)"
    pbt = lambda k, tier: f"=INDEX(Perf_Batch!$C${PB[k]}:$Q${PB[k]},3*({{X}}$6-1)+{{X}}{{{tier}}})"
    hk = lambda code: f"={TR[code]}"
    sparse = lambda pos: ("={X}{ff}*IF({X}{cap}=0," + pos + ",MIN(" + pos + ",{X}{cap}))+(1-{X}{ff})*(" + pos + "/{X}{comp}+{X}{win})")
    gpuh = lambda C, k="1": "={X}{" + C + "}/({X}{pk}*1E15*{X}{mfu}*" + k + "*{X}{gp})/3600"
    return [
      ("§", "A. 規格、成本與 Tech_Registry 掛鉤"),
      ("pk8", "FP8 dense 峰值", "PF/GPU", "#,##0.000", sp(SP["tfp8"])),
      ("htpk", "訓練峰值倍數（H_TPK）", "x", "0.00", hk("H_TPK")),
      ("pk", "訓練用峰值（MFU 分母）", "PF/GPU", "#,##0.000", "={X}{pk8}*{X}{htpk}"),
      ("mfub", "預訓練 MFU 基準", "%", "0%", tgl("mfub")),
      ("mfug", "MFU 世代倍數", "x", "0.00", tg("mfug")),
      ("hmfu", "訓練 MFU 倍數（H_MFU）", "x", "0.00", hk("H_MFU")),
      ("mfu", "預訓練 MFU（採用）", "%", "0.0%", "={X}{mfub}*{X}{mfug}*{X}{hmfu}"),
      ("gp", "goodput", "%", "0%", tgl("gp")),
      ("gpus", "每 GW GPU 數", "顆", "#,##0", dc(14)),
      ("ce", "每 GPU 小時持有成本 — 經濟（基準成本）", "$/GPU-hr", "#,##0.00", dc(58)),
      ("ca", "每 GPU 小時持有成本 — 會計（基準成本）", "$/GPU-hr", "#,##0.00", dc(57)),
      ("§", "B. 架構（連結 Arch）"),
      ("A", "啟用參數", "B", "#,##0", ar(AR["A"])),
      ("attc", "注意力 FLOPs／被注意 token", "FLOP", "#,##0", ar(AR["attc"])),
      ("ff", "全注意力層比例", "%", "0%", ar(AR["ff"])),
      ("cap", "全注意力跨度上限", "tok", "#,##0", ar(AR["cap"])),
      ("comp", "其他層壓縮比", "x", "#,##0", ar(AR["comp"])),
      ("win", "其他層滑動窗", "tok", "#,##0", ar(AR["win"])),
      ("hflop", "FLOPs/token 倍數（H_FLOP）", "x", "0.00", hk("H_FLOP")),
      ("§", "C. 預訓練（反向傳播型；每 token 訓練 FLOPs＝3 × 前向）"),
      ("htok", "所需 token 倍數（H_TOK）", "x", "0.00", hk("H_TOK")),
      ("Dp", "預訓練 token", "T", "#,##0.0", ti("ptok") + "*{X}{htok}"),
      ("Sp", "序列長", "tok", "#,##0", ti("pseq")),
      ("attp", "平均被注意 token（dense 注意力＝平均位置）", "tok", "#,##0", "={X}{Sp}/2"),
      ("Fpt", "訓練 FLOPs/token", "GFLOP", "#,##0.0", "=3*(2*{X}{A}*1E9+{X}{attc}*{X}{attp})*{X}{hflop}/1E9"),
      ("Cp", "預訓練 FLOPs", "FLOP", "0.00E+00", "={X}{Fpt}*1E9*{X}{Dp}*1E12"),
      ("Hp", "預訓練 GPU 小時", "GPU-hr", "#,##0", gpuh("Cp")),
      ("§", "D. 長上下文延伸（反向傳播型；稀疏注意力路徑）"),
      ("Dl", "延伸 token", "T", "#,##0.0", ti("ltok")),
      ("Sl", "序列長", "tok", "#,##0", ti("lseq")),
      ("attl", "平均被注意 token", "tok", "#,##0", sparse("{X}{Sl}/2")),
      ("Flt", "訓練 FLOPs/token", "GFLOP", "#,##0.0", "=3*(2*{X}{A}*1E9+{X}{attc}*{X}{attl})*{X}{hflop}/1E9"),
      ("Cl", "延伸 FLOPs", "FLOP", "0.00E+00", "={X}{Flt}*1E9*{X}{Dl}*1E12"),
      ("Hl", "延伸 GPU 小時", "GPU-hr", "#,##0", gpuh("Cl")),
      ("§", "E. SFT（反向傳播型）"),
      ("Ds", "SFT token", "T", "#,##0.00", ti("stok")),
      ("Ss", "序列長", "tok", "#,##0", ti("sseq")),
      ("atts", "平均被注意 token", "tok", "#,##0", sparse("{X}{Ss}/2")),
      ("Fst", "訓練 FLOPs/token", "GFLOP", "#,##0.0", "=3*(2*{X}{A}*1E9+{X}{attc}*{X}{atts})*{X}{hflop}/1E9"),
      ("Cs", "SFT FLOPs", "FLOP", "0.00E+00", "={X}{Fst}*1E9*{X}{Ds}*1E12"),
      ("sftk", "SFT MFU 係數", "x", "0.00", tgl("sftk")),
      ("Hs", "SFT GPU 小時", "GPU-hr", "#,##0", gpuh("Cs", "{X}{sftk}")),
      ("§", "F. RL（rollout＝推論型，以 Perf_Batch 計價；trainer＝反向傳播型）"),
      ("Rout", "rollout 輸出 token", "T", "#,##0.0", ti("rout")),
      ("isl", "每樣本輸入", "tok", "#,##0", pb("isl")),
      ("osl", "每樣本輸出", "tok", "#,##0", pb("osl")),
      ("ns", "樣本數", "個", "#,##0", "={X}{Rout}*1E12/{X}{osl}"),
      ("G", "GRPO 每題取樣數", "個", "0", tgl("G")),
      ("pref", "新鮮 prefill token（每題一次）", "T", "#,##0.00", "={X}{ns}*{X}{isl}/{X}{G}/1E12"),
      ("gsdr", "rollout decode GPU 秒／M（Perf_Batch 本層級）", "GPU-s/M", "#,##0.0", pb("gsd")),
      ("gsfr", "rollout prefill GPU 秒／M", "GPU-s/M", "#,##0.0", pb("gsf")),
      ("fdb", "rollout decode FLOPs/token", "GFLOP", "#,##0.0", pb("Fd")),
      ("fpb", "rollout prefill FLOPs/token", "GFLOP", "#,##0.0", pb("Fp")),
      ("hroll", "rollout 效率倍數（H_ROLL）", "x", "0.00", hk("H_ROLL")),
      ("reff", "rollout 效率（採用）", "%", "0%", tgl("reff") + "*{X}{hroll}"),
      ("Hro", "rollout GPU 小時（含閒置）", "GPU-hr", "#,##0", "=({X}{Rout}*1E6*{X}{gsdr}+{X}{pref}*1E6*{X}{gsfr})/3600/{X}{reff}"),
      ("Cro", "rollout FLOPs（接受 token）", "FLOP", "0.00E+00", "={X}{Rout}*1E12*{X}{fdb}*1E9+{X}{pref}*1E12*{X}{fpb}*1E9"),
      ("Tt", "trainer 處理 token（輸入＋輸出）", "T", "#,##0.0", "={X}{ns}*({X}{isl}+{X}{osl})/1E12"),
      ("attr", "trainer 平均被注意 token", "tok", "#,##0", sparse("({X}{isl}+{X}{osl})/2")),
      ("Frt", "trainer FLOPs/token", "GFLOP", "#,##0.0", "=3*(2*{X}{A}*1E9+{X}{attc}*{X}{attr})*{X}{hflop}/1E9"),
      ("Crt", "trainer FLOPs", "FLOP", "0.00E+00", "={X}{Frt}*1E9*{X}{Tt}*1E12"),
      ("rlk", "RL trainer MFU 係數", "x", "0.00", tgl("rlk")),
      ("Hrt", "trainer GPU 小時", "GPU-hr", "#,##0", gpuh("Crt", "{X}{rlk}")),
      ("refk", "參考模型前向（0／1）", "", "0", tgl("ref")),
      ("Hrf", "參考模型前向 GPU 小時（推論型）", "GPU-hr", "#,##0", "={X}{refk}*{X}{Hrt}/3"),
      ("Hrl", "RL GPU 小時合計", "GPU-hr", "#,##0", "={X}{Hro}+{X}{Hrt}+{X}{Hrf}"),
      ("Crl", "RL FLOPs 合計", "FLOP", "0.00E+00", "={X}{Cro}+{X}{Crt}*(1+{X}{refk}/3)"),
      ("rlmfu", "RL 有效 MFU（FLOPs ÷ GPU 小時 ÷ 訓練峰值）", "%", "0.0%", "={X}{Crl}/({X}{Hrl}*3600*{X}{pk}*1E15)"),
      ("rlH", "RL ÷ 預訓練（GPU 小時）", "x", "0.00", "={X}{Hrl}/{X}{Hp}"),
      ("rlF", "RL ÷ 預訓練（FLOPs）", "x", "0.00", "={X}{Crl}/{X}{Cp}"),
      ("§", "G. On-policy 蒸餾（學生 rollout＋教師評分＝推論型；學生更新＝反向傳播型）"),
      ("Dd", "學生 rollout 輸出 token", "T", "#,##0.00", ti("dtok")),
      ("dt", "教師層級", "", "0", ti("dtea")),
      ("Td", "教師評分 token（輸入＋輸出）", "T", "#,##0.00", "={X}{Dd}*1E12/{X}{osl}*({X}{isl}+{X}{osl})/1E12"),
      ("gsft", "教師 prefill GPU 秒／M", "GPU-s/M", "#,##0.0", pbt("gsf", "dt")),
      ("fpt", "教師 prefill FLOPs/token", "GFLOP", "#,##0.0", pbt("Fp", "dt")),
      ("Hds", "學生 rollout GPU 小時", "GPU-hr", "#,##0", "={X}{Dd}*1E6*{X}{gsdr}/3600/{X}{reff}"),
      ("Hdt", "教師評分 GPU 小時", "GPU-hr", "#,##0", "={X}{Td}*1E6*{X}{gsft}/3600"),
      ("Cdu", "學生更新 FLOPs", "FLOP", "0.00E+00", "={X}{Frt}*1E9*{X}{Td}*1E12"),
      ("Hdu", "學生更新 GPU 小時", "GPU-hr", "#,##0", gpuh("Cdu", "{X}{rlk}")),
      ("Hd", "蒸餾 GPU 小時合計", "GPU-hr", "#,##0", "={X}{Hds}+{X}{Hdt}+{X}{Hdu}"),
      ("Cd", "蒸餾 FLOPs 合計", "FLOP", "0.00E+00", "={X}{Dd}*1E12*{X}{fdb}*1E9+{X}{Td}*1E12*{X}{fpt}*1E9+{X}{Cdu}"),
      ("§", "H. 合成資料與評測（推論型）"),
      ("Dsy", "合成資料 token", "T", "#,##0.0", ti("syn")),
      ("gt", "生成層級", "", "0", tgl("gtier")),
      ("gsdg", "生成層級 decode GPU 秒／M", "GPU-s/M", "#,##0.0", pbt("gsd", "gt")),
      ("fdg", "生成層級 decode FLOPs/token", "GFLOP", "#,##0.0", pbt("Fd", "gt")),
      ("Hsy", "合成資料 GPU 小時", "GPU-hr", "#,##0", "={X}{Dsy}*1E6*{X}{gsdg}/3600"),
      ("Csy", "合成資料 FLOPs", "FLOP", "0.00E+00", "={X}{Dsy}*1E12*{X}{fdg}*1E9"),
      ("Dev", "評測 token", "T", "#,##0.00", ti("ev")),
      ("Hev", "評測 GPU 小時", "GPU-hr", "#,##0", "={X}{Dev}*1E6*{X}{gsdr}/3600"),
      ("Cev", "評測 FLOPs", "FLOP", "0.00E+00", "={X}{Dev}*1E12*{X}{fdb}*1E9"),
      ("§", "I. 最終訓練合計（單一模型）"),
      ("Hpre", "預訓練側 GPU 小時（預訓練＋長上下文）", "GPU-hr", "#,##0", "={X}{Hp}+{X}{Hl}"),
      ("Hpost", "後訓練 GPU 小時（SFT＋RL＋蒸餾）", "GPU-hr", "#,##0", "={X}{Hs}+{X}{Hrl}+{X}{Hd}"),
      ("Hoth", "合成資料與評測 GPU 小時", "GPU-hr", "#,##0", "={X}{Hsy}+{X}{Hev}"),
      ("Hfin", "最終訓練 GPU 小時", "GPU-hr", "#,##0", "={X}{Hpre}+{X}{Hpost}+{X}{Hoth}"),
      ("Cpre", "預訓練側 FLOPs", "FLOP", "0.00E+00", "={X}{Cp}+{X}{Cl}"),
      ("Cpost", "後訓練 FLOPs", "FLOP", "0.00E+00", "={X}{Cs}+{X}{Crl}+{X}{Cd}"),
      ("Cfin", "最終訓練 FLOPs", "FLOP", "0.00E+00", "={X}{Cpre}+{X}{Cpost}+{X}{Csy}+{X}{Cev}"),
      ("psF", "後訓練占比（FLOPs 口徑）", "%", "0.0%", "={X}{Cpost}/({X}{Cpre}+{X}{Cpost})"),
      ("psH", "後訓練占比（GPU 小時口徑）", "%", "0.0%", "={X}{Hpost}/({X}{Hpre}+{X}{Hpost})"),
      ("HI", "推論型 GPU 小時", "GPU-hr", "#,##0", "={X}{Hro}+{X}{Hrf}+{X}{Hds}+{X}{Hdt}+{X}{Hsy}+{X}{Hev}"),
      ("HB", "反向傳播型 GPU 小時", "GPU-hr", "#,##0", "={X}{Hp}+{X}{Hl}+{X}{Hs}+{X}{Hrt}+{X}{Hdu}"),
      ("Ish", "推論型占最終訓練", "%", "0.0%", "={X}{HI}/{X}{Hfin}"),
      ("Ufin", "最終訓練成本 — 經濟", "$M", "#,##0.0", "={X}{Hfin}*{X}{ce}/1E6"),
      ("Ufa", "最終訓練成本 — 會計", "$M", "#,##0.0", "={X}{Hfin}*{X}{ca}/1E6"),
      ("GWf", "最終訓練占 1 GW 一年", "%", "0.000%", "={X}{Hfin}/({X}{gpus}*8760)"),
      ("§", "J. 研發計畫（J10：研發倍數乘在 GPU 小時上；依最終訓練比例分攤＝各層級最終 × 倍數）"),
      ("rdm", "研發倍數", "x", "0.0", tgl("rdm")),
      ("Hprog", "研發計畫 GPU 小時", "GPU-hr", "#,##0", "={X}{Hfin}*{X}{rdm}"),
      ("Hexp", "其中：研發實驗（型態未拆分）", "GPU-hr", "#,##0", "={X}{Hprog}-{X}{Hfin}"),
      ("Uprog", "研發計畫成本 — 經濟", "$M", "#,##0", "={X}{Hprog}*{X}{ce}/1E6"),
      ("GWp", "研發計畫占 1 GW 一年", "%", "0.00%", "={X}{Hprog}/({X}{gpus}*8760)"),
      ("§", "K. 用途 × 型態（GPU 小時；單一模型計畫；對外服務不在第 0 層，J11）"),
      ("xPreB", "預訓練（含長上下文）｜反向傳播型", "GPU-hr", "#,##0", "={X}{Hpre}"),
      ("xPostI", "後訓練｜推論型（rollout、參考、蒸餾學生與教師）", "GPU-hr", "#,##0", "={X}{Hro}+{X}{Hrf}+{X}{Hds}+{X}{Hdt}"),
      ("xPostB", "後訓練｜反向傳播型（SFT、RL trainer、學生更新）", "GPU-hr", "#,##0", "={X}{Hs}+{X}{Hrt}+{X}{Hdu}"),
      ("xOthI", "合成資料與評測｜推論型", "GPU-hr", "#,##0", "={X}{Hoth}"),
      ("xExp", "研發實驗｜未拆分", "GPU-hr", "#,##0", "={X}{Hexp}"),
    ]

TKEY = {"Hp", "Hrl", "Hfin", "psF", "psH", "rlmfu", "Ufin", "GWf", "Hprog", "Uprog", "GWp", "rlH"}

def write_train(ws, cols, SP, AR, TI, PB, TR, start=9, overrides=None):
    overrides = overrides or {}
    R = {}; r = start
    for item in train_rows(SP, AR, TI, PB, TR):
        if item[0] == "§":
            section(ws, r, item[1], 2 + len(cols)); r += 1; continue
        key, lab, unit, fmt, tpl = item
        R[key] = r
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in cols:
            ov = overrides.get(X, {})
            if key in ov:
                v = ov[key].replace("{X}", X) if isinstance(ov[key], str) else ov[key]
                put(ws, f"{X}{r}", v, F_IN, fmt=fmt, fill=PatternFill("solid", fgColor="FFFFFF00")); continue
            m = dict(R); m["X"] = X
            put(ws, f"{X}{r}", tpl.format(**m), fmt=fmt, fill=FILL_KEY if key in TKEY else None)
        r += 1
    ws.column_dimensions["A"].width = 46; ws.column_dimensions["B"].width = 10
    return R, r

def hdr15(ws, cols, gens_tiers):
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "層級", F_BOLD); put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "層級索引", F_BOLD)
    for X, (g, t) in zip(cols, gens_tiers):
        put(ws, f"{X}6", g, fmt="0"); put(ws, f"{X}7", t, fmt="0")
        put(ws, f"{X}4", f"=INDEX(Spec_Rack!$C$4:$G$4,{X}6)", F_HLINK)
        put(ws, f"{X}5", f"=INDEX(Arch!$C$4:$E$4,{X}7)", F_HLINK)
        ws.column_dimensions[X].width = 13

def training_sheet(wb, SP, AR, TI, PB, TR):
    ws = wb.create_sheet("Training")
    title(ws, "Training — 訓練與研發計畫的 GPU 小時、成本、1 GW 年占比（世代 × 層級；下游預設 VR200，GB300 並列，J13）",
          "推論型運算以 Perf_Batch 計價；反向傳播型以訓練峰值 × MFU × goodput 計價。後訓練占比同時列 FLOPs 與 GPU 小時口徑（一級追蹤指標）")
    hdr15(ws, COLS15, [(i // 3 + 1, i % 3 + 1) for i in range(15)])
    R, r = write_train(ws, COLS15, SP, AR, TI, PB, TR)
    section(ws, r, "L. 模型家族合計（同世代三層級；J10 研發歸屬的總額）", 17); r += 1
    for key, lab, unit, fmt, src in [("fHfin", "家族最終訓練 GPU 小時", "GPU-hr", "#,##0", "Hfin"),
                                     ("fHprog", "家族研發計畫 GPU 小時", "GPU-hr", "#,##0", "Hprog"),
                                     ("fUprog", "家族研發計畫成本 — 經濟", "$M", "#,##0", "Uprog"),
                                     ("fGWp", "家族研發計畫占 1 GW 一年", "%", "0.00%", "GWp")]:
        R[key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for X in COLS15:
            put(ws, f"{X}{r}", f"=SUMPRODUCT(($C$6:$Q$6={X}$6)*$C${R[src]}:$Q${R[src]})", fmt=fmt, fill=FILL_KEY)
        r += 1
    ws.freeze_panes = "C8"
    return R

SCEN_T = [  # label, overrides applied to both columns (Sol, Astra); special "fp8" flag
 ("基準", {}),
 ("預訓練 MFU 基準 0.15", {"mfub": 0.15}),
 ("預訓練 MFU 基準 0.40", {"mfub": 0.40}),
 ("NVFP4 訓練峰值（J7 替代）", {"pk8": "=INDEX(Spec_Rack!$C${tfp4}:$G${tfp4},{X}$6)"}),
 ("預訓練 token × 0.5", {"htok": 0.5}),
 ("預訓練 token × 1.67", {"htok": 1.67}),
 ("RL rollout token × 0.3", {"Rout": "=INDEX(Train_In!$C${rout}:$E${rout},{X}$7)*0.3"}),
 ("RL rollout token × 3", {"Rout": "=INDEX(Train_In!$C${rout}:$E${rout},{X}$7)*3"}),
 ("rollout 效率 0.6（v5.5 混合現況；rollout token 不變）", {"reff": 0.6}),
 ("rollout 效率 0.95（rollout token 不變）", {"reff": 0.95}),
 ("rollout 精度 FP8（J12 替代）", "fp8"),
 ("合成資料 token × 0", {"Dsy": 0}),
 ("合成資料 token × 3", {"Dsy": "=INDEX(Train_In!$C${syn}:$E${syn},{X}$7)*3"}),
 ("研發倍數 4.4（MiniMax）", {"rdm": 4.4}),
 ("研發倍數 10.4（OpenAI）", {"rdm": 10.4}),
 ("goodput 0.80", {"gp": 0.8}),
]

def sens_train(wb, SP, AR, TI, PB, TR):
    ws = wb.create_sheet("Sens_Train")
    title(ws, "Sens_Train — 訓練與研發計畫的單變數敏感度（VR200；每組左 Sol、右 Astra；先看敏感度，再看基準）",
          "黃底藍字＝該情境改動的輸入。L 節為對基準欄（C、D）的比值")
    cols, ov, gt = [], {}, []
    for i, (lab, o) in enumerate(SCEN_T):
        xs, xa = L(3 + 2 * i), L(4 + 2 * i)
        cols += [xs, xa]; gt += [(4, 2), (4, 3)]
        if o == "fp8":
            ov[xs] = {k: f"=Perf_Batch!R{PB[k2]}" for k, k2 in (("gsdr", "gsd"), ("gsfr", "gsf"), ("fdb", "Fd"), ("fpb", "Fp"))}
            ov[xa] = {k: f"=Perf_Batch!S{PB[k2]}" for k, k2 in (("gsdr", "gsd"), ("gsfr", "gsf"), ("fdb", "Fd"), ("fpb", "Fp"))}
        else:
            oo = {k: (v.replace("{tfp4}", str(SP["tfp4"])).replace("{rout}", str(TI["rout"])).replace("{syn}", str(TI["syn"])) if isinstance(v, str) else v)
                  for k, v in o.items()}
            ov[xs] = dict(oo); ov[xa] = dict(oo)
        put(ws, f"{xs}3", lab, F_BOLD, wrap=True); ws.merge_cells(f"{xs}3:{xa}3")
    ws.row_dimensions[3].height = 44; put(ws, "A3", "情境", F_BOLD)
    hdr15(ws, cols, gt)
    R, r = write_train(ws, cols, SP, AR, TI, PB, TR, overrides=ov)
    section(ws, r, "L. 對基準的比值（同層級）", 2 + len(cols)); r += 1
    for key, lab in [("Hfin", "最終訓練 GPU 小時 ÷ 基準"), ("Hprog", "研發計畫 GPU 小時 ÷ 基準"), ("psH", "後訓練占比（GPU 小時）÷ 基準")]:
        R["r_" + key] = r; put(ws, f"A{r}", lab); put(ws, f"B{r}", "x")
        for i, X in enumerate(cols):
            base = "C" if i % 2 == 0 else "D"
            put(ws, f"{X}{r}", f"={X}{R[key]}/${base}${R[key]}", fmt="0.00", fill=FILL_KEY)
        r += 1
    ws.freeze_panes = "C8"
    return R
```

## finish.py

```python
from common import *
from openpyxl.workbook.defined_name import DefinedName
from outputs import COLS15

def interface(wb, PR, U):
    ws = wb["Interface"]
    for r in range(17, 23):
        for c in range(1, 19): ws.cell(row=r, column=c).value = None
    put(ws, "A2", "每一列為一個具名範圍（IF_…），欄＝世代 × 成本情境；Block 2 產出依層級分區（物理量不隨成本情境變動）", F_NOTE)
    section(ws, 17, "B. Block 2 產出（依層級；100%＝理想上限；下游以自身利用率換算）", 17)
    r = 18; names = []
    tiers = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
    for t, (tk, tn) in enumerate(tiers, start=1):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        pl = lambda key: f"=INDEX(Perf!$C${PR[key]}:$Q${PR[key]},3*(Unit_Cost!{{X}}$6-1)+{t})"
        rows = [
          (f"IF_TokRack_{tk}", "每架總 tok/s（參考任務 P:D）", "tok/s", "#,##0", pl("rtot")),
          (f"IF_TokRackD_{tk}", "每架 decode tok/s", "tok/s", "#,##0", pl("rdec")),
          (f"IF_TokGW_{tk}", "每 GW 總產出（100%）", "M tok/年", "#,##0", pl("gwtot")),
          (f"IF_VReq_{tk}", "VR-eq 係數（每 GW 產出 ÷ VR200）", "x", "0.00", pl("vreq")),
          (f"IF_CostPre_{tk}", "新鮮 prefill $/M（經濟、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cf')]}"),
          (f"IF_CostCache_{tk}", "快取命中 prefill $/M（經濟、100%）", "$/M", "#,##0.0000", f"=Unit_Cost!{{X}}{U[(t,'cc')]}"),
          (f"IF_CostDec_{tk}", "decode（含思考 token）$/M（經濟、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cd')]}"),
          (f"IF_CostDecAcct_{tk}", "decode（含思考 token）$/M（會計、100%）", "$/M", "#,##0.000", f"=Unit_Cost!{{X}}{U[(t,'cda')]}"),
          (f"IF_TokPerJ_{tk}", "tokens／焦耳（平均用電口徑）", "tok/J", "#,##0.00", pl("tpj")),
        ]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for X in COLS15:
                put(ws, f"{X}{r}", tpl.format(X=X), fmt=fmt, fill=FILL_KEY if "CostDec_" in name or "TokGW" in name else None)
            names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "基準利用率（第 0 層；下游可覆寫）　[IF_Util]"); put(ws, f"B{r}", "%")
    put(ws, f"C{r}", "=Serving!$C$17", fmt="0%"); names.append(("IF_Util", f"Interface!$C${r}")); r += 2
    put(ws, f"A{r}", "每 GW 理論營收"); put(ws, f"C{r}", "待 Block 4（Capability、單價前緣）", F_NOTE)
    for n, ref in names:
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    ws.column_dimensions["A"].width = 52
    return names

def checks(wb, CAL, PR, SR, U):
    ws = wb["Checks"]
    section(ws, 12, "Block 2 檢查", 6)
    rows = [
      ("校準：擬合點重現（應為 1.00）", f"=Calib!C{CAL['ratio']}", "1.00", "x", "擬合正確性", "Calib F 節"),
      ("樣本外：GB300 SGLang＋MTP 50 tok/s", f"=Calib!E{CAL['ratio']}", "11,200 實測", "模型÷實測", "±10% 內視為前緣形狀成立", "S21"),
      ("樣本外：GB300 vLLM 無 MTP 27 tok/s", f"=Calib!F{CAL['ratio']}", "6,182 實測", "模型÷實測", "應 >1：舊軟體", "S20"),
      ("樣本外：GB200 vLLM 無 MTP 27 tok/s", f"=Calib!G{CAL['ratio']}", "2,189 實測", "模型÷實測", "應 >1：舊軟體＋記憶體限制配方", "S20"),
      ("樣本外：GB200／GB300 110 tok/s", f"=Calib!H{CAL['ratio']}", "3,795 實測", "模型÷實測", "口徑待查", "S23"),
      ("GB300 Sol 經濟成本 vs InferenceX（72 tok/s，8K/1K）", f"=DC_Cost!J58/(Calib!C{CAL['T']}*3600)*1E6", "0.078", "$/M 總 token", "差異來自每 GPU 小時 TCO（本模型 2.99 對 2.65）", "S22"),
      ("VR200 ÷ GB300 每 GW 產出（Sol 基準）", f"=Sens_Perf!C{SR['rgw']}", "=DC_Cost!M55/DC_Cost!J55", "x", "外部參照欄＝損益兩平（每 GW 持有成本比）；高於此值時 VR200 每 token 較便宜", "Sens_Perf"),
      ("GB300 每 GPU 功率：本模型 IT 平均用電", "=DC_Cost!J11*Inputs!$E$10/72", "2.12", "kW/GPU", "InferenceX 72 tok/s 時 9,384 tok/s/GPU ÷ 4.43M tok/s/MW 反推（provisioned，口徑可能含設施）", "S22"),
      ("VR200 ÷ GB300 decode $/M（Sol 基準）", f"=Sens_Perf!C{SR['rcost']}", "<1 較便宜", "x", "", "Sens_Perf"),
      ("第二來源：GB300 interactive 模型 ÷ MLPerf（DeepSeek-R1）", f"=Calib!C{CAL['mR']}", "1.00", "x", "<1：本模型低於 MLPerf，InferenceX 校準未比 MLPerf 樂觀", "S31、S32"),
      ("第二來源：VR200 ÷ GB300 模型 對 MLPerf", f"=Calib!C{CAL['mVR']}", f"=Calib!C{CAL['mVRm']}", "x", "兩者接近即支持 VR 沿用 GB300 效率係數", "S32"),
      ("來源衝突：GB300 ÷ GB200 模型 對 MLPerf", f"=Calib!C{CAL['mGB']}", f"=Calib!D{CAL['mGB']}", "x", "InferenceX 1.7–2.8、MLPerf 約 1.05、模型居中", "S20、S31"),
      ("能量閉合：各欄最大閉合比", f"=MAX(Perf!C{PR['close']}:Q{PR['close']})", "≤ 100%", "%", "超過代表產出或能量常數有誤", "Perf J 節"),
      ("SLO 不可達的欄數（15 欄中）", f"=COUNTIF(Perf!C{PR['bind']}:Q{PR['bind']},\"SLO 不可達\")", "—", "欄", "0＝15 欄在 SLO 下皆可達；Hopper × Astra 每 GPU 僅約 25 tok/s，物理上可達但經濟上不可行", "Perf G 節"),
      ("牌價空間：V4-Pro 8K/1K 牌價 ÷ GB300 Sol 成本（基準利用率）", f"=((8*1.32+3.96)/9)/((8*Unit_Cost!J{U[(2,'cfu')]}+Unit_Cost!J{U[(2,'cdu')]})/9)", "—", "x", "DeepSeek V4-Pro API 牌價 $1.32／$3.96（2026-09 價格追蹤站；記錄於 Tokenomics v4 活頁簿預設表）；只說明空間，不代表 DeepSeek 毛利", "S27"),
    ]
    put(ws, "A13", "項目", F_BOLD); put(ws, "B13", "本模型", F_BOLD); put(ws, "C13", "外部參照", F_BOLD)
    put(ws, "D13", "單位", F_BOLD); put(ws, "E13", "判讀", F_BOLD); put(ws, "F13", "來源", F_BOLD)
    for i, (a, b, c, d, e, f) in enumerate(rows):
        r = 14 + i
        put(ws, f"A{r}", a, wrap=True); put(ws, f"B{r}", b, fmt="#,##0.00" if "%" not in d else "0%", fill=FILL_KEY)
        put(ws, f"C{r}", c); put(ws, f"D{r}", d); put(ws, f"E{r}", e, F_NOTE, wrap=True); put(ws, f"F{r}", f, F_NOTE)

def sources(wb):
    ws = wb["Sources"]
    data = [
      ("S20", "InferenceX GB300 對 GB200（V4-Pro）", "vLLM、無 MTP、2026-05-22：27 tok/s 時 6,182 對 2,189 tok/s/GPU；GB300 峰值 11,056@13.1；GB300 多 50% HBM 使配方更寬", "Interested-party（SemiAnalysis：平台受晶片商贊助、另售 TCO 模型）；單一來源須佐證", "2026-05", "inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4", "已核對原文（交接錨點即此，屬舊軟體）"),
      ("S21", "SGLang／NVIDIA：V4 on GB300", "SGLang＋MTP 2026-06：約 50 tok/s/user 時約 11,200 tok/s/GPU；草稿接受率 0.57→0.70；配方 10p1d dep4／dep32", "Interested-party（SGLang、NVIDIA 作者）", "2026-06-23", "pytorch.org/blog/serving-deepseek-v4-on-gb300-with-sglang-…", "已核對原文"),
      ("S22", "InferenceX 每美元比較（B300 對 GB300，V4-Pro）", "GB300：72 tok/s 時 9,384 tok/s/GPU、$0.078/M；130 tok/s 時 3,474、$0.216/M；187 tok/s 時 $1.436/M", "Interested-party（SemiAnalysis）；擬合所用，第二來源見 S31、S32", "約 2026-07", "inferencex.semianalysis.com/compare-per-dollar/deepseek-v4-b300-vs-gb300", "已核對搜尋摘錄；軟體與日期待確認"),
      ("S23", "InferenceX 比較（GB200 對 GB300，V4-Pro 0813）", "110 tok/s：GB200 3,795、GB300 6,522 tok/s/GPU", "Interested-party（SemiAnalysis）", "2026-08／09", "inferencex.semianalysis.com/compare/deepseek-v4-gb200-vs-gb300", "口徑待查：頁面預設為 agentic traces"),
      ("S24", "InferenceX H200（V4-Pro，FP8）", "75 tok/s 時 4,036、100 tok/s 時 3,102 tok/s/GPU", "Interested-party（SemiAnalysis）", "2026-08", "inferencex.semianalysis.com/run/deepseek-v4-on-h200", "口徑待查；未入驗證"),
      ("S25", "Anthropic 多代理研究系統", "agent 約 4 倍、多代理約 15 倍聊天 token", "Interested-party（Anthropic）", "2025-06", "Anthropic Engineering Blog（經多方轉述核對）", "已核對二手"),
      ("S26", "Artificial Analysis 輸出速度", "GPT-5.6 Luna 約 120、GPT-5.6 Sol 約 68、GPT-6 Astra 約 52–56、Opus 5 約 54、Gemini 3.8 Flash 約 290–350 tok/s", "Verified-measured（反映供應商自身服務選擇）", "2026-09", "artificialanalysis.ai", "已核對"),
      ("S27", "DeepSeek V4 模型卡與 v4 架構預設表", "V4-Pro 1.6T／49B、61 層、d 7168；V4-Flash 284B／13B", "Verified", "2026", "Tokenomics v4 活頁簿（20260922）預設表；morphllm.com 2026-09-07 彙整", "待以 config.json 核對"),
      ("S28", "NVIDIA 規格", "H100 FP8 989 TF、80 GB、3.35 TB/s；GB200 FP4 10 PF、186 GB、8 TB/s；B300 15 PF、288 GB；Rubin 50／35 PF、288 GB、22 TB/s；RU NVL576 15 EF、HBM4e", "Interested-party（NVIDIA）", "2025–26", "模型內建知識", "待以規格表核對"),
      ("S29", "能量常數", "HBM3 約 3.9 pJ/bit、HBM3e 約 3、HBM4 約 2.5；SerDes 1–2 pJ/bit", "Analogy", "—", "文獻常見值（模型內建知識）", "待查核"),
      ("S31", "MLPerf Inference v6.0（DeepSeek-R1）", "GB300 NVL72 interactive 250,634、GB200 NVL72 240,318 tok/s（72 GPU）；GB300 server 8,064 tok/s/GPU", "Verified-measured（MLCommons 稽核）／Interested-party（NVIDIA 提交並挑選配置）", "2026-04-01", "NVIDIA 資料中心推論效能頁；NVIDIA 技術部落格", "已核對二手"),
      ("S32", "MLPerf Inference v6.1（VR200 首次提交）", "DeepSeek-R1 interactive：VR200 NVL72 652,750 對 GB300 NVL72 253,506 tok/s（2.58 倍）；VR 為預覽類", "Verified-measured（MLCommons）／Interested-party（NVIDIA 對照表）", "2026-09-16", "shattered.io 轉述 NVIDIA 對照表", "待以 MLCommons 原始結果核對"),
      ("S33", "MLCommons DeepSeek-R1 基準規格", "平均 ISL 800、OSL 3,880；server TTFT 2 s／TPOT 80 ms；interactive TTFT 1.5 s／TPOT 15 ms（p99），允許 3 步 MTP", "Verified", "2025-09／2026-03", "mlcommons.org；inference_rules", "已核對"),
      ("S34", "AMD：InferenceX 資料的選擇性使用", "NVIDIA GTC 2026 以 InferenceX 資料比較時選 FP4、MTP=3 等有利設定；同條件下 MI355X 可能更便宜", "Interested-party（AMD）", "2026-03", "amd.com 技術文章", "提醒：同一平台資料可因設定選擇而偏向"),
      ("S35", "DeepSeek-V4 技術報告（arXiv 2606.19348）", "V4-Flash 32T、V4-Pro 33T token 預訓練；4K→16K dense 注意力後切換稀疏；後訓練：專家 SFT＋GRPO，再以 on-policy 蒸餾整合；FP8 計算＋FP4 QAT，rollout 用原生 FP4 權重；未揭露訓練算力", "Interested-party（DeepSeek）", "2026-06", "arxiv.org/abs/2606.19348", "已核對原文摘錄"),
      ("S36", "NVIDIA Vera Rubin NVL72 規格表", "NVFP4 推論 3,600 PF、NVFP4 訓練 2,520 PF、FP8/FP6 訓練 1,260 PF、BF16 288 PF（72 GPU）", "Interested-party（NVIDIA）", "2026", "NVIDIA 規格表（Gigabyte 轉載 PDF）；spheron.network 轉述", "已核對兩處轉載"),
      ("S37", "Meta Llama 3 技術報告", "405B：16K H100、BF16 MFU 38–43%；有效訓練時間 >90%", "Interested-party（Meta）", "2024-07", "arXiv 2407.21783（模型內建知識）", "待查核"),
      ("S38", "Epoch：最終訓練占研發算力少數", "最終訓練占研發支出：OpenAI 9.6%、MiniMax 22.6%、Z.ai 12.3%；實驗利用率低於最終訓練", "Analogy（Epoch 推估；資料源為 The Information 等報導）", "2026-03", "epoch.ai/gradient-updates/r-and-d-vs-training-compute", "已核對"),
      ("S39", "Epoch：超過 1e25 FLOP 的模型", "Grok-3 約 4.6e26 FLOP；估計誤差 2–5 倍", "Analogy（Epoch 推估）", "2025-06", "epoch.ai/data-insights/models-over-1e25-flop", "已核對"),
      ("S40", "R1 RL 算力（Lambert《RLHF》書）", "R1 RL 147K H800 GPU 小時，約 V3 預訓練 2.8M 的 5%", "Interested-party（DeepSeek，經轉述）", "2025／2026", "arxiv.org/pdf/2504.12501", "已核對轉述"),
      ("S41", "Epoch：推理模型能擴展多遠", "Nemotron Ultra RL 14 萬 H100 小時，不到預訓練 1%", "Analogy（Epoch 轉述 NVIDIA）", "2025-05", "epoch.ai/gradient-updates/how-far-can-reasoning-models-scale", "已核對"),
      ("S42", "xAI Grok 4 發表", "以 20 萬 GPU 叢集做預訓練規模的 RL；RL 算力為前次 10 倍以上", "Interested-party（xAI，宣傳誘因）", "2025-07", "x.ai/news/grok-4", "已核對原文；口徑不明"),
      ("S43", "verl DeepSeek V4 RL 配方（PR #7895）", "TE FP8 訓練＋MXFP4 專家 QAT；vLLM rollout FP8、KV FP8", "Verified（開源程式碼）", "2026", "github.com/verl-project/verl/pull/7895", "已核對；J12 替代情境依據"),
      ("S44", "DeepSeek-V3 技術報告", "預訓練 14.8T token、2.664M H800 GPU 小時（全部 2.788M）；FP8 混合精度訓練；序列長 4K", "Interested-party（DeepSeek）", "2024-12", "arxiv.org/abs/2412.19437", "GPU 小時為模型內建知識，待以原文核對"),
      ("S45", "DeepSeek-V4.1-Flash 技術報告（arXiv 2609.19969）", "合成任務以大規模非同步 RL；rollout 在 DSec 沙箱、與可搶占訓練池分離；非同步已用於幾乎全部 RL 與 OPD，rollout 與訓練共置分時", "Interested-party（DeepSeek）", "2026-09", "arxiv.org/pdf/2609.19969", "已核對原文摘錄"),
      ("S46", "GLM-5 技術報告（arXiv 2602.15763）", "以 slime 框架建新非同步 RL 基礎設施，進一步解耦生成與訓練；非同步 Agent RL 演算法", "Interested-party（Zhipu）", "2026-02", "arxiv.org/abs/2602.15763", "已核對原文摘錄"),
      ("S47", "Kimi-Researcher（Moonshot）", "完全非同步 rollout＋回合層級部分 rollout，rollout 至少加速 1.5 倍；K1.5 為迭代同步＋部分 rollout", "Interested-party（Moonshot）", "2025", "Moonshot 技術部落格（經 Medium 轉述）", "已核對轉述"),
      ("S48", "LlamaRL（Meta，arXiv 2505.24034）", "Llama 3 後訓練使用非同步 off-policy RL；405B 相對 DeepSpeed-Chat 類系統最高 10.7 倍（基準線較弱）", "Interested-party（Meta）", "2025-07", "arxiv.org/pdf/2505.24034", "已核對"),
      ("S49", "ROLL Flash（阿里淘天）、AReaL（螞蟻）框架", "ROLL Flash：同 GPU 預算下 RLVR 2.24 倍、agentic 2.72 倍；AReaL：同步約慢 2 倍。僅框架，未證實用於 Qwen／Ling 旗艦模型", "Analogy（框架基準測試）", "2025–2026", "arxiv 2510.11345；inclusionai.github.io/AReaL", "已核對；不計入 J14 採用數"),
      ("S30", "DeepSeek 推論系統公開統計（H800）", "V3/R1 線上：prefill 與 decode 節點吞吐、每用戶約 20 tok/s；本模型用於 η_p 與 Hopper η_d 倍數", "Interested-party（DeepSeek）", "2025-02", "DeepSeek Open Source Week 第 6 天（模型內建知識）", "待查核"),
    ]
    for i, row in enumerate(data):
        r = 23 + i
        for c, v in zip("ABCDEFG", row): put(ws, f"{c}{r}", v, wrap=True)

def readme(wb):
    ws = wb["README"]
    rows = [
      ("用途", "回答：每 1 GW IT 電力，各世代可容納多少機架、資本支出與持有成本（Block 1）；各層級 SLO 下的產出與依『世代 × 層級 × token 類型』的每 M token 成本（Block 2）；各層級代表模型的訓練與研發計畫需要多少 GPU 小時、成本與 1 GW 年，其中後訓練占多少（Block 3）；每 GW 的理論營收（理想上限）、含中國廠商的單價前緣、訓練攤提、快取儲存與 1 GW 參考機隊（Block 4）；harness 對每個成功任務的 token、成本與成功率的影響（Block 5）。實際營收（需求、市占、訂閱方案）在下游。"),
      ("版本", "20261001_Tokenomics_v5.9（Block 1＋2＋3＋4＋5；v5.9 加 Block 5：Har_In、Harness、Sens_Har，Workload 改為 harness 參數組，Block 4 補 SLO 不可達保護、K6 預設 (c)、機隊層級貢獻列、中國廠商旗標；v5.8 加 Block 4：Cap_In、Capability、Price_Frontier、Cache_Store、Fleet_1GW、Amortize、Theory_Rev、Sens_Rev；v5.2 加第二來源驗證與生產折減；v5.3、v5.4 依 CC 回饋補具名範圍與驗證表；v5.5 加 Block 3：Tech_Registry、Train_In、Perf_Batch、Training、Sens_Train，並更正 Hopper FP8 峰值；v5.6 非同步 RL 併入基準、補 TR_ 與訓練世代具名範圍；v5.7 改為 Excel 優先：輸入值由 Excel 擁有，新增 DB_Evidence 證據登錄表）。v4 的 Config／TL_Param／WP_Param／Revenue_Model 由 Arch、Serving、Workload、Calib、Perf、Unit_Cost 取代。"),
      ("電力口徑", "GW＝IT 關鍵電力（Andy 2026-09-30 確認）。設施電力＝IT × PUE，於 DC_Cost 與 Interface 並列。"),
      ("工作表", "Inputs → Spec_Rack → Arch → Serving → Workload → Calib → Tech_Registry → Perf → Sens_Perf → Unit_Cost → DC_Cost → Train_In → Perf_Batch → Training → Sens_Train → Cap_In → Capability → Price_Frontier → Cache_Store → Fleet_1GW → Amortize → Theory_Rev → Sens_Rev → Har_In → Harness → Sens_Har → Interface；Energy、NonNV、Sensitivity、Checks、Sources。"),
      ("Block 3 推導", "預訓練：FLOPs＝3 ×（2 × 啟用參數＋注意力 FLOPs × 被注意 token）× token；GPU 小時＝FLOPs ÷（FP8 訓練峰值 × MFU × goodput）。RL、蒸餾、合成資料、評測的推論型運算以 Perf_Batch（與 Perf 同公式，只換速度下限與參考任務）計價；RL 有效 MFU 為推導值。研發計畫＝最終訓練 GPU 小時 × 研發倍數。"),
      ("Block 3 決策", "J7 訓練精度 FP8（NVFP4 預訓練在 Tech_Registry）；J8 Astra 預訓練與 Arch 一致，前沿錨點列 Checks；J9 RL 由下而上，基準校到 RL÷預訓練 GPU 小時 Luna／Sol 0.3、Astra 1.0；J10 研發倍數 8，家族合計、依最終訓練比例分攤；J11 用途 × 型態只列單一計畫；J12 rollout NVFP4（FP8 為情境）；J13 下游預設 VR200、GB300 並列；J14 主流＝至少兩家實驗室公開採用，可覆寫。"),
      ("Excel 優先（v5.7）", "藍字＝輸入，由本活頁簿擁有：要改輸入，直接改 Excel。builder 重建 Block 2、3 時會先讀取所有藍字輸入，重建後依『工作表＋欄 A 標籤＋欄位』寫回，程式內的預設值只用於新增的輸入列。公式頁不要手改（重建時會被覆寫）。"),
      ("DB_Evidence（v5.7）", "證據登錄表：所有比對過的新資訊（含不採納者），記錄主張、來源、標記、對應參數、當時值、新值、判定與處理版本。builder 只在本頁不存在時建立。"),
      ("Tech_Registry", "每列＝技術 × 作用物理量；有效倍數＝1＋開關 × 採用比例 ×（倍數−1）；已在基準者不套倍數。掛鉤彙總表連到 Perf、Perf_Batch、Training。全部開關為 0 時 Block 2 數值與 v5.4 相同。"),
      ("Block 2 推導", "prefill：tok/s＝η_p × 峰值 ÷ FLOPs/token。decode：每步時間＝固定延遲（權重讀取＋每層延遲 ×（層數＋草稿數））＋B × 每序列時間；在 SLO 下解出批次 B*，再受 HBM 容量限制。η_d 與每層延遲由 GB300 同一前緣兩點聯立解出（Calib）。"),
      ("成本情境", "低成本／基準／高成本為角落情境。單一變數影響看 Sensitivity（Block 1）與 Sens_Perf（Block 2）。"),
      ("功率情境", "Inputs!E6 選 1／2／3，決定每架配電設計功率與每 GW 機架數。"),
      ("顏色", "藍字＝輸入；黑字＝公式；綠字＝跨頁連結；淡黃底＝關鍵輸出；亮黃底＝待 Andy 決定或情境改動。"),
      ("來源標記", "Verified／Interested-party／Analogy／Assumed／Derived。Analogy 與 Assumed 一律給區間。"),
      ("網站同步", "本檔為事實來源；repo 以公式引擎直接計算本檔，parity 測試比對 Interface 全部格（新增 IF_ 具名範圍見 Interface B 節）。"),
      ("具名範圍", "IF_＝下游模型連結用；IF_Hdr／DRV_／CAL_／TRN_／TR_＝網站顯示用，下游不得連結；B4_／B5_＝Block 4／5 公式內部引用的關鍵量（v5.8 起新公式以具名範圍引用，使公式可讀），下游不得連結；IF_HdrTask 為顯示用表頭。"),
      ("Block 4 推導", "理論營收＝每 GW 產出 × 利用率 × 參考請求混合有效單價（OpenAI 牌價 ×（1−折扣）× 能力單價倍數）。單價前緣＝能力指數 ≥ OpenAI 層級模型者之中，參考請求混合單價最低者（含中國廠商）。快取儲存＝KV bytes × 儲存層 $/GB-hr × 保留時間 ÷ 命中次數。攤提：自下而上＝研發計畫成本 ÷ 商業壽命內服務 token（＝回本所需溢價）；由上而下＝機隊訓練占比 X ÷（1−X）× 服務成本。"),
      ("Block 4 決策", "K1 OpenAI 單價為基準；K2 (i) 前緣＝同能力最低價；K3 AA 指數為主、METR 檢查；K4 (c)＋(d) 能力→單價彈性基準 0＋回本溢價反解；K5 壽命 Luna／Sol 12、Astra 9 個月；K6 兩種攤提並列，v5.9 起下游預設 (c)＝由上而下總額 × 自下而上權重、(d) 營收權重並列；K7 機隊以 OpenAI 2025 校準；K8 只計 API 單價；K9 各世代共用 2026-09 單價快照；K10 快取儲存比照公開條款；K11 利用率 60%、折減 1.0 暫用；K12 尖峰離峰並列、前緣用時數加權；K13 中國廠商全納入並標示開放權重；K14 國際站美元價。"),
      ("Block 5 推導", "harness＝作用在標準任務上的參數組（輪數、思考保留 ρ、每輪思考、歷史壓縮、快取命中、子代理、狀態保留時間）加成功率。Workload 有效參數＝標準＋w ×（Har_In 選定檔案−標準），w＝Tech_Registry T12 開關 × 採用比例。成功率 p＝1 ÷（1＋（任務長度 ÷（層級 50% 時間範圍 × harness 倍數））^β）（METR 型）；每成功任務成本＝每次嘗試成本 ÷ p。每 GW 理論營收不受 harness 影響。"),
      ("Block 5 決策", "L1 參數組取代單一 token 倍數；L2 METR 型成功率＋覆寫欄；L3 增強檔不入基準（w＝0）；L4 harness 不影響每 GW 營收；L5 每成功任務成本＝每次嘗試 ÷ p；L6 非 GPU 成本不入第 0 層；L7 情境值只採中立方同條件實測。"),
      ("來源原則", "SemiAnalysis（含 InferenceX）資料一律須有第二來源佐證並標記 Interested-party；目前第二來源為 MLPerf（MLCommons 稽核，NVIDIA 提交）與 DeepSeek 自揭（待查）。"),
      ("未結事項", "(1) VR200 報價是否含網路（S11）。(2) 所有來源待 Andy 查核。(3) Rubin Ultra 為推估。(4) J6 基準利用率暫用 60%、生產折減暫用 1.0，皆待 Andy 給值。(5) VR200 無實測，η_d 與每層延遲沿用 GB300。(6) 交接錨點 6,182 屬舊軟體（vLLM 無 MTP），已改為 GB300 最新前緣兩點校準。(7) 快取儲存成本已於 v5.8 Cache_Store 加入（儲存層與保留時間為 Assumed）。(8) Hopper 峰值更正為 FP8 1,979 TF，η_d 與 η_p 倍數同步減半以維持產出；S30 口徑待查後重推。(9) Block 3 的 Astra token、RL rollout 量、研發倍數皆為 Analogy／Assumed，看 Sens_Train。(10) v5.6：非同步 RL 併入基準（rollout 效率 0.85），RL rollout token 重校以維持 GPU 小時錨點（J9 (a)）。(11) v5.8：K6 下游攤提預設於 v5.9 定為 (c)；Claude Opus 5.5、Kimi K3、MiniMax M3 的能力指數未取得，不參與前緣；Anthropic、Moonshot、Alibaba、MiniMax 價格為二手；METR 檢查未入表；Google 未列入候選。(12) v5.9：METR 尚未發布 GPT-6 各層級時間範圍（以 GPT-5.6 Sol、Mythos Preview 類比）；任務長度為 Assumed；ARC 金額衝突與 Opus 5 harness 歸屬待核；harness 用於 RL rollout 與非 GPU 成本延後。"),
    ]
    for i, (a, b) in enumerate(rows):
        r = 4 + i
        put(ws, f"A{r}", a, F_BOLD); put(ws, f"B{r}", b, wrap=True)
    put(ws, "A1", "Tokenomics v5.9 — Block 1＋2＋3＋4＋5：機架規格、每 GW 成本、各層級產出與每 token 成本、訓練與研發計畫、理論營收與單價前緣、harness 與每成功任務成本", F_TITLE)
    put(ws, "A2", "第 0 層規格來源。理論營收為理想上限；實際營收在下游模型。", F_NOTE)

# ---------------------------------------------------------------- Block 3 additions (v5.5)
def interface_b3(wb, TRN, start, TI):
    ws = wb["Interface"]
    r = start
    section(ws, r, "C. Block 3 產出（依層級；欄＝世代 × 成本情境；GPU 小時不隨成本情境變動；下游預設 VR200、GB300 並列，J13）", 17); r += 1
    names = []
    tiers = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
    for t, (tk, tn) in enumerate(tiers, start=1):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        tl = lambda key: f"=INDEX(Training!$C${TRN[key]}:$Q${TRN[key]},3*(Unit_Cost!{{X}}$6-1)+{t})"
        rows = [
          (f"IF_TrainGPUh_{tk}", "最終訓練 GPU 小時（單一模型）", "GPU-hr", "#,##0", tl("Hfin")),
          (f"IF_TrainCost_{tk}", "最終訓練成本 — 經濟（依成本情境）", "$M", "#,##0.0", tl("Hfin") + "*Unit_Cost!{X}$8/1E6"),
          (f"IF_PostShareFLOP_{tk}", "後訓練占比（FLOPs 口徑）", "%", "0.0%", tl("psF")),
          (f"IF_PostShareGPUh_{tk}", "後訓練占比（GPU 小時口徑）", "%", "0.0%", tl("psH")),
          (f"IF_RLMFU_{tk}", "RL 有效 MFU（訓練峰值分母）", "%", "0.0%", tl("rlmfu")),
          (f"IF_ProgGPUh_{tk}", "研發計畫 GPU 小時（含研發倍數分攤）", "GPU-hr", "#,##0", tl("Hprog")),
          (f"IF_ProgCost_{tk}", "研發計畫成本 — 經濟（依成本情境）", "$M", "#,##0", tl("Hprog") + "*Unit_Cost!{X}$8/1E6"),
          (f"IF_ProgGWyr_{tk}", "研發計畫占 1 GW 一年", "%", "0.00%", tl("GWp")),
        ]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for X in COLS15:
                put(ws, f"{X}{r}", tpl.format(X=X), fmt=fmt, fill=FILL_KEY if "Prog" in name or "PostShareGPUh" in name else None)
            names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "研發倍數（第 0 層基準；下游可覆寫）　[IF_RDMult]"); put(ws, f"B{r}", "x")
    put(ws, f"C{r}", f"=Train_In!$C${TI['rdm']}", fmt="0.0"); names.append(("IF_RDMult", f"Interface!$C${r}")); r += 1
    put(ws, f"A{r}", "下游預設訓練世代（索引；J13）　[IF_TrainGenDefault]"); put(ws, f"B{r}", "索引")
    put(ws, f"C{r}", f"=Train_In!$C${TI['gdef']}", fmt="0"); put(ws, f"D{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,C{r})", F_HLINK)
    names.append(("IF_TrainGenDefault", f"Interface!$C${r}")); r += 1
    put(ws, f"A{r}", "並列訓練世代（索引；J13）　[IF_TrainGenAlt]"); put(ws, f"B{r}", "索引")
    put(ws, f"C{r}", f"=Train_In!$C${TI['galt']}", fmt="0"); put(ws, f"D{r}", f"=INDEX(Spec_Rack!$C$4:$G$4,C{r})", F_HLINK)
    names.append(("IF_TrainGenAlt", f"Interface!$C${r}"))
    names.append(("IF_TrainGenDefaultName", f"Interface!$D${r-1}")); names.append(("IF_TrainGenAltName", f"Interface!$D${r}")); r += 1
    for n, ref in names:
        wb.defined_names[n] = DefinedName(n, attr_text=ref)
    return names

def checks_b3(wb, TRN, TI, CAL, PB):
    ws = wb["Checks"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, "Block 3 檢查（VR200＝N 欄 Astra、M 欄 Sol；GB300＝K、J）", 6)
    put(ws, f"A{r0+1}", "項目", F_BOLD); put(ws, f"B{r0+1}", "本模型", F_BOLD); put(ws, f"C{r0+1}", "外部參照", F_BOLD)
    put(ws, f"D{r0+1}", "單位", F_BOLD); put(ws, f"E{r0+1}", "判讀", F_BOLD); put(ws, f"F{r0+1}", "來源", F_BOLD)
    T = lambda k, col: f"Training!{col}{TRN[k]}"
    v3 = (f"=3*(2*Calib!$C${CAL['rA']}*1E9+Calib!$C${CAL['rac']}*Train_In!$C${TI['v3seq']}/2)*Train_In!$C${TI['v3tok']}*1E12"
          f"/(Train_In!$C${TI['v3h']}*1E6*3600*Spec_Rack!$C${{tfp8}}*1E15)")
    rows = [
      ("DeepSeek V3 推導 MFU（H800、FP8 分母）", v3, "=Training!C" + str(TRN["mfu"]), "%",
       "外部參照欄＝本模型 Hopper 採用 MFU；兩者接近即 Hopper 倍數 0.8 成立", "S44"),
      ("RL ÷ 預訓練 GPU 小時：VR200 Astra", f"={T('rlH','N')}", f"=Train_In!$C${TI['grok']}", "x",
       "J9 基準 1.0；參照為 Grok 4 宣稱（口徑不明）", "S42"),
      ("RL ÷ 預訓練 GPU 小時：VR200 Sol", f"={T('rlH','M')}", f"=Train_In!$C${TI['r1rl']}", "x",
       "J9 基準 0.3；參照為 R1（2025-01）", "S40"),
      ("RL 有效 MFU：VR200 Astra", f"={T('rlmfu','N')}", "0.01–0.10", "%", "交接第 3 節區間；本模型為推導值", "交接"),
      ("後訓練占比：GPU 小時口徑 − FLOPs 口徑（VR200 Astra）", f"={T('psH','N')}-{T('psF','N')}", "≥ 0", "%",
       "RL 有效 MFU 低於預訓練，GPU 小時占比必然較高", "Training I 節"),
      ("最終訓練 ÷ 研發計畫", f"=1/Train_In!$C${TI['rdm']}", "9.6%–22.6%", "%", "Epoch 三家公司區間", "S38"),
      ("前沿錨點中值（5e26）反推 Astra 預訓練 token", f"=Train_In!$C${TI['an2']}/({T('Fpt','N')}*1E9)/1E12",
       f"=Training!N{TRN['Dp']}", "T", "J8：差距大代表 Astra 啟用參數或 token 假設偏低；錨點低／高值見 Train_In", "S39"),
      ("Astra 最終訓練占 1 GW 一年：VR200 ／ GB300", f"={T('GWf','N')}", f"={T('GWf','K')}", "%", "本模型 VR200 值；外部參照欄為 GB300", "Training"),
    ]
    return r0 + 2, rows

def write_checks_b3(wb, r, rows, SP):
    ws = wb["Checks"]
    for i, (a, b, c, d, e, f) in enumerate(rows):
        rr = r + i
        b = b.replace("{tfp8}", str(SP["tfp8"]))
        put(ws, f"A{rr}", a, wrap=True); put(ws, f"B{rr}", b, fmt="0.0%" if d == "%" else "#,##0.00", fill=FILL_KEY)
        put(ws, f"C{rr}", c, fmt="0.0%" if d == "%" else "#,##0.00"); put(ws, f"D{rr}", d)
        put(ws, f"E{rr}", e, F_NOTE, wrap=True); put(ws, f"F{rr}", f, F_NOTE)

# ---------------------------------------------------------------- v5.7: evidence register
EVID_HDR = ["ID", "日期", "主張（摘要）", "來源（S 編號或出處）", "標記", "對應參數（工作表與列）", "Tokenomics 當時值",
            "新資訊值", "判定", "處理版本", "備註"]
EVID_SEED = [
  ("E001", "2026-09-30", "H100 FP8 dense 峰值為 1,979 TF，非 989 TF", "NVIDIA H100 規格（S36 交叉核對）", "Interested-party",
   "Spec_Rack 峰值 Hopper", "0.989 PF", "1.979 PF", "採納", "v5.5", "η_d、η_p 倍數同步減半維持產出；S30 口徑待查"),
  ("E002", "2026-09-30", "DeepSeek V4-Flash／Pro 預訓練 32T／33T token", "S35", "Verified", "Train_In 預訓練 token",
   "—（新增）", "32／33T", "採納", "v5.5", ""),
  ("E003", "2026-09-30", "Rubin NVL72 FP8 訓練 17.5、NVFP4 訓練 35 PF/GPU", "S36", "Interested-party", "Spec_Rack B3 訓練峰值",
   "—（新增）", "17.5／35 PF", "採納", "v5.5", ""),
  ("E004", "2026-09-30", "最終訓練占研發算力支出 9.6–22.6%（OpenAI、MiniMax、Z.ai）", "S38", "Analogy", "Train_In 研發倍數",
   "—（新增）", "4.4–10.4 倍", "採納（取 8）", "v5.5", "支出口徑，乘在 GPU 小時上"),
  ("E005", "2026-09-30", "Grok 4 以預訓練規模做 RL", "S42", "Interested-party", "Train_In RL rollout token（J9 錨點）",
   "—", "RL ≈ 1 × 預訓練", "部分採納", "v5.5", "口徑不明，只作 Astra 錨點上緣參考"),
  ("E006", "2026-09-30", "前沿預訓練算力約 2e26–2e27 FLOP（Grok-3 約 4.6e26）", "S39", "Analogy", "Train_In Astra 預訓練 token",
   "60T（約 7e25 FLOP）", "需約 438T（5e26）", "待查", "—", "J8 差距；Block 4 以能力錨點檢驗"),
  ("E007", "2026-10-01", "非同步 RL 已用於 DeepSeek、Zhipu、Moonshot、Meta 旗艦模型", "S45–S48", "Interested-party",
   "Tech_Registry T10；Train_In rollout 效率", "0.60（未入基準）", "0.85（入基準）", "採納", "v5.6", "Andy 決定 (a)：rollout token 重校"),
  ("E008", "2026-10-01", "開源 RL 框架（verl）DeepSeek V4 配方以 FP8 rollout", "S43", "Verified", "Sens_Train rollout 精度情境",
   "NVFP4（基準）", "FP8", "不採納為基準", "v5.5", "列為 J12 替代情境"),
  ("E009", "2026-10-01", "ROLL Flash、AReaL 非同步增益約 2–2.7 倍", "S49", "Analogy", "Train_In rollout 效率區間",
   "—", "增益 2–2.7 倍", "部分採納", "v5.6", "僅框架，不計入 J14 採用數；只用於區間"),
]

def evidence_sheet(wb):
    if "DB_Evidence" in wb.sheetnames:
        return False
    ws = wb.create_sheet("DB_Evidence")
    title(ws, "DB_Evidence — 證據登錄表：所有比對過的新資訊（含不採納者）",
          "每一筆新發現先與 Tokenomics 現值比對，再判定採納／部分採納／不採納／待查。本頁由 Andy 與 Claude 直接在 Excel 維護；builder 只在本頁不存在時建立，之後不再覆寫")
    widths = [7, 11, 46, 26, 15, 30, 18, 18, 14, 9, 44]
    for i, (h, w) in enumerate(zip(EVID_HDR, widths)):
        put(ws, f"{L(i+1)}4", h, F_BOLD, wrap=True); ws.column_dimensions[L(i+1)].width = w
    for j, row in enumerate(EVID_SEED):
        for i, v in enumerate(row):
            put(ws, f"{L(i+1)}{5+j}", v, F_IN, wrap=i in (2, 5, 10))
        ws.row_dimensions[5 + j].height = 30
    ws.freeze_panes = "C5"
    return True
```

## block4.py

```python
# Block 4 (v5.8): Cap_In, Capability, Price_Frontier, Cache_Store, Fleet_1GW, Amortize, Theory_Rev, Sens_Rev
# Decisions (Andy 2026-10-01): K1 OpenAI price = base; K2 (i) price frontier = cheapest model whose capability
# index >= the OpenAI tier model; Chinese vendors in the candidate table; K3 AA Intelligence Index (METR check);
# K4 (c)+(d): capability->price elasticity base 0 + break-even premium; K5 life Luna/Sol 12, Astra 9 months;
# K6 both amortization bases; v5.9: downstream default (c) = top-down total x bottom-up weights, (d) revenue weights; K7 fleet calibrated to OpenAI 2025; K8 API prices only;
# K9 one price snapshot for all generations; K10 cache storage by analogy to public cache terms;
# K11 utilization 60% / derate 1.0 kept; K12 peak & off-peak both, frontier on hour-weighted;
# K13 all Chinese vendors (open-weight flag); K14 international USD prices.
# New formulas reference key quantities through named ranges (B4_ = Block 4 internal / display; IF_ = downstream).
from common import *
from outputs import COLS15
from openpyxl.workbook.defined_name import DefinedName

TIERS = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
TC = "CDE"                      # tier columns on Cap_In / Price_Frontier summary

def nm(wb, n, ref):
    wb.defined_names[n] = DefinedName(n, attr_text=ref)

def head15(ws, note_row=None):
    """rows 4–7: generation, cost case, generation index, column index (C..Q)."""
    put(ws, "A4", "世代", F_BOLD); put(ws, "A5", "成本情境", F_BOLD)
    put(ws, "A6", "世代索引", F_BOLD); put(ws, "A7", "欄索引", F_BOLD)
    for i, X in enumerate(COLS15):
        put(ws, f"{X}4", f"=Unit_Cost!{X}4", F_HLINK); put(ws, f"{X}5", f"=Unit_Cost!{X}5", F_HLINK)
        put(ws, f"{X}6", i // 3 + 1, F_CALC, fmt="0"); put(ws, f"{X}7", i + 1, F_CALC, fmt="0")
        ws.column_dimensions[X].width = 12
    ws.column_dimensions["A"].width = 50; ws.column_dimensions["B"].width = 11
    ws.freeze_panes = "C8"

def row15(ws, r, lab, unit, tpl, fmt="#,##0.000", key=False):
    put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
    for X in COLS15:
        put(ws, f"{X}{r}", tpl.replace("{X}", X), fmt=fmt, fill=FILL_KEY if key else None)

IF = lambda name: f"INDEX({name},1,{{X}}$7)"          # one-row 15-column IF_ range at this column

# ---------------------------------------------------------------- Cap_In
PRICE_ROWS = [  # model, vendor, country, open weights, fresh, cached, out, peak(1/0), AA index, index ver, price date, tag, source
  ("GPT-6 Luna", "OpenAI", "美國", "否", 0.1, 0.01, 0.5, 0, 37, "v4.3.2", "2026-09-25", "Verified", "S50（價格）；S56（指數）"),
  ("GPT-6 Sol", "OpenAI", "美國", "否", 2.0, 0.2, 10.0, 0, 48, "v4.3.2", "2026-09-25", "Verified", "S50；S56"),
  ("GPT-6 Astra", "OpenAI", "美國", "否", 10.0, 1.0, 50.0, 0, 53, "v4.3", "2026-09-25", "Verified", "S50；S55"),
  ("Claude Fable 5.1", "Anthropic", "美國", "否", 10.0, 0.25, 50.0, 0, 53, "v4.3", "2026-09", "Interested-party", "S51（快取讀取 0.25 僅單一二手來源，待以官方頁核對）；S55"),
  ("Claude Opus 5", "Anthropic", "美國", "否", 5.0, 0.5, 25.0, 0, 51, "v4.3", "2026-08", "Interested-party", "S51；S55"),
  ("Claude Opus 5.5", "Anthropic", "美國", "否", 4.0, 0.2, 20.0, 0, None, "待查", "2026-09-22", "Interested-party", "S51；指數未取得（Anthropic 自稱達 Fable 5.1 水準，未經獨立評測前不納入前緣）"),
  ("DeepSeek V4.1-Flash", "DeepSeek", "中國", "是", 0.30, 0.006, 1.20, 1, 39, "v4.3.2", "2026-10-01", "Verified", "S52（官方頁，尖峰價；離峰半價）；S56"),
  ("DeepSeek V4-Pro-0813", "DeepSeek", "中國", "是", 1.32, 0.044, 3.96, 1, 36, "v4.3", "2026-10-01", "Verified", "S52；S55（指數為『DeepSeek V4 Pro』）"),
  ("GLM-5.3", "Z.ai", "中國", "否（預定開放）", 1.40, 0.26, 4.40, 0, 45, "v4.3.2", "2026-10-01", "Verified", "S53（官方頁）；S56"),
  ("GLM-5.3-Flash", "Z.ai", "中國", "是", 0.15, 0.03, 0.50, 0, 42, "v4.3", "2026-10-01", "Verified", "S53；S55"),
  ("Qwen3.8-Max", "Alibaba", "中國", "預定開放", 2.00, 0.25, 6.00, 0, 40, "v4.3", "2026-09", "Interested-party", "S54（國際站；多個二手來源一致，另一來源載 $2.5／$7.5 附五折，待核）；S55"),
  ("Kimi K3", "Moonshot", "中國", "有爭議", 3.00, 0.30, 15.00, 0, None, "待查", "2026-07-16", "Interested-party", "S54；v4.3 指數未取得（報導僅稱與 GLM-5.3 並列開放權重領先，≥43）"),
  ("MiniMax M3", "MiniMax", "中國", "否", 0.30, None, 1.20, 0, None, "待查", "2026-08", "Interested-party", "S54（≤512K 輸入；快取價未取得）；指數未取得"),
]

def cap_in(wb):
    ws = wb.create_sheet("Cap_In")
    title(ws, "Cap_In — Block 4 輸入（藍字＝輸入；Analogy／Assumed 一律附區間；價格為 2026-09／10 快照）",
          "Block 4 命題：每 1 GW 的理論營收（理想上限）＝SLO 產能 × 利用率 × 層級別有效單價；另列中國廠商在內的單價前緣、訓練攤提、快取儲存與 1 GW 參考機隊。決策 K1–K14 見 README")
    for c, w in zip("ABCDEFGHIJKLM", [44, 10, 12, 12, 12, 16, 70, 10, 10, 9, 11, 15, 60]): ws.column_dimensions[c].width = w
    K = {}
    def hdr(r, cols=("值／Luna", "Sol", "Astra", "標記", "說明")):
        put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
        for c, h in zip("CDEFG", cols): put(ws, f"{c}{r}", h, F_BOLD)
    r = 4
    section(ws, r, "A. OpenAI 層級牌價（K1 基準；2026-09-25，短上下文 Standard）", 7); r += 1; hdr(r); r += 1
    for key, lab, vals, note in [
        ("pin", "新鮮輸入", (0.1, 2.0, 10.0), "GPT-6 Luna／Sol／Astra"),
        ("pc", "快取輸入", (0.01, 0.2, 1.0), "＝輸入價 10%"),
        ("pout", "輸出（含思考 token）", (0.5, 10.0, 50.0), "思考 token 依輸出價計費（S50、S51、S54：OpenAI、Anthropic、Moonshot 皆同）")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", "$/M")
        for c, v in zip(TC, vals): put(ws, f"{c}{r}", v, fmt="#,##0.000")
        put(ws, f"F{r}", "Verified", F_NOTE); put(ws, f"G{r}", note + "（S50）", F_NOTE, wrap=True); K[key] = r; r += 1
    r += 1
    section(ws, r, "B. 計費與工作負載（單一值；D、E 欄＝低、高）", 7); r += 1
    hdr(r, ("基準", "低", "高", "標記", "說明")); r += 1
    singles = [
      ("disc", "有效折扣（Batch／Flex 半價＋企業議價，加權）", "%", 0.2, 0.1, 0.3, "Assumed", "與 OpenAI 模型 v0.5 一致；Batch 半價為 Verified，企業折扣為 Analogy"),
      ("chi", "參考請求快取命中率 χ（輸入中屬快取命中的比例）", "%", 0.55, 0.3, 0.75, "Assumed", "與 OpenAI 模型 v0.5 一致；成本與營收用同一 χ"),
      ("eps", "能力 → 單價彈性 ε（單價 ∝ 有效算力倍數^ε）", "x", 0, 0, 0.5, "Assumed", "K4 (c)：機制保留、基準 0。斜率無法由公開資料分離（價格由廠商策略與成本決定，見 Capability C 節）"),
      ("cmult", "有效訓練算力倍數（相對 Block 3 基準；情境用）", "x", 1, 0.5, 7, "Assumed", "與 Tech_Registry H_CAP 相乘後代入 ε；高值 7＝J8 前沿錨點中值相對 Astra 基準的倍數"),
      ("pkmode", "尖峰／離峰口徑（1＝尖峰價；2＝依時數加權）", "選擇", 2, 1, 2, "Decision", "K12：兩者並列，前緣基準用 2"),
      ("pkhr", "尖峰時數（每週）", "hr", 35, None, None, "Verified", "DeepSeek：週一至五 UTC 01–04、06–10，共 7 hr × 5（S52）"),
      ("offr", "離峰價 ÷ 尖峰價", "x", 0.5, None, None, "Verified", "DeepSeek（S52）"),
    ]
    for key, lab, unit, b, lo, hi, tag, note in singles:
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        fmt = "0%" if unit == "%" else ("0.00" if unit == "x" else "0")
        put(ws, f"C{r}", b, fmt=fmt)
        if lo is not None: put(ws, f"D{r}", lo, fmt=fmt); put(ws, f"E{r}", hi, fmt=fmt)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True); K[key] = r; r += 1
    r += 1
    section(ws, r, "C. 模型商業壽命（K5；月）", 7); r += 1; hdr(r); r += 1
    for key, lab, vals, tag, note in [
        ("life", "商業壽命 基準", (12, 12, 9), "Assumed", "旗艦更替快：GPT-5.6（2026-07）→ GPT-6（2026-09）"),
        ("lifelo", "商業壽命 低", (6, 6, 6), "Assumed", ""), ("lifehi", "商業壽命 高", (24, 24, 18), "Assumed", "")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", "月")
        for c, v in zip(TC, vals): put(ws, f"{c}{r}", v, fmt="0")
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE); K[key] = r; r += 1
    r += 1
    section(ws, r, "D. 1 GW 參考機隊配置（K7：以 OpenAI 2025 算力支出校準；D、E 欄＝低、高）", 7); r += 1
    hdr(r, ("基準", "低", "高", "標記", "說明")); r += 1
    for key, lab, b, lo, hi, tag, note in [
        ("serve", "對外服務占機隊", 0.41, 0.30, 0.60, "Interested-party／Derived",
         "OpenAI 2025 推論 $8.4B ÷（推論 $8.4B＋訓練約 $12B）；以支出比代 GW 比（硬體與雲端加價不同，故為 Derived）"),
        ("free", "其中免費服務占服務", 0.46, 0.35, 0.60, "Interested-party", "OpenAI 2025 非付費用戶推論 $3.9B ÷ $8.4B（The Information 2026-02）")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", "%"); put(ws, f"C{r}", b, fmt="0%"); put(ws, f"D{r}", lo, fmt="0%")
        put(ws, f"E{r}", hi, fmt="0%"); put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True); K[key] = r; r += 1
    hdr(r); r += 1
    for key, lab, vals, note in [
        ("mixp", "付費服務 token 層級組合", (0.40, 0.45, 0.15), "OpenAI 模型 v0.5 API tokenMix 2026（Assumed）；三者合計須為 1"),
        ("mixf", "免費服務 token 層級組合", (0.90, 0.10, 0.0), "OpenAI 模型 v0.5 免費方案模型組合（Assumed）")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", "%")
        for c, v in zip(TC, vals): put(ws, f"{c}{r}", v, fmt="0%")
        put(ws, f"F{r}", "Assumed", F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True); K[key] = r; r += 1
    r += 1
    section(ws, r, "E. 快取儲存（K10：比照公開快取條款；D、E 欄＝低、高）", 7); r += 1
    hdr(r, ("基準", "低", "高", "標記", "說明")); r += 1
    for key, lab, unit, b, lo, hi, fmt, tag, note in [
        ("stier", "儲存層（1＝SSD；2＝DRAM；3＝HBM）", "選擇", 2, 1, 3, "0", "Assumed", "公開條款：預設保留 5 分鐘、可選 1 小時（S51）；長保留通常下放 DRAM／SSD"),
        ("ret", "保留時間", "hr", 0.0833333333333333, 0.0833333333333333, 1, "0.000", "Analogy", "5 分鐘（預設 TTL）至 1 小時（延長 TTL，寫入價 2 倍，S51）"),
        ("hits", "每次寫入在保留期內的平均命中次數", "次", 5, 1, 20, "0", "Assumed", "代理迴圈多輪重用前綴時高；單次問答低"),
        ("dram", "DRAM 取得成本", "$/GB", 10, 5, 20, "0.00", "Assumed", "2026 記憶體漲價期；含伺服器分攤"),
        ("dlife", "DRAM 折舊年限", "年", 4, 3, 6, "0", "Assumed", ""),
        ("ssd", "SSD 取得成本", "$/GB", 0.10, 0.05, 0.30, "0.00", "Assumed", "企業級 NVMe"),
        ("slife", "SSD 折舊年限", "年", 5, 3, 6, "0", "Assumed", "")]:
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        put(ws, f"C{r}", b, fmt=fmt); put(ws, f"D{r}", lo, fmt=fmt); put(ws, f"E{r}", hi, fmt=fmt)
        put(ws, f"F{r}", tag, F_NOTE); put(ws, f"G{r}", note, F_NOTE, wrap=True); K[key] = r; r += 1
    r += 1
    section(ws, r, "F. 市場價格與能力候選表（K2 (i)、K13、K14：國際站美元牌價；能力＝Artificial Analysis Intelligence Index）", 13); r += 1
    h = ["模型", "廠商", "國別", "開放權重", "新鮮輸入 $/M", "快取輸入 $/M", "輸出 $/M", "尖峰離峰（1＝有）",
         "能力指數", "指數版本", "價格日期", "標記", "來源", "中國廠商（1＝是）"]
    for i, t in enumerate(h): put(ws, f"{L(i+1)}{r}", t, F_BOLD, wrap=True)
    r += 1; K["tab0"] = r
    for row in PRICE_ROWS:
        for i, v in enumerate(row):
            if v is None: continue
            fmt = "#,##0.000" if i in (4, 5, 6) else ("0" if i in (7, 8) else None)
            put(ws, f"{L(i+1)}{r}", v, F_IN if i < 12 else F_NOTE, fmt=fmt, wrap=(i == 12))
        put(ws, f"N{r}", 1 if row[2] == "中國" else 0, F_IN, fmt="0")   # v5.9：中國廠商旗標（CC 第 7 輪）
        r += 1
    K["tab1"] = r - 1
    put(ws, f"A{r}", "註：前 3 列為 OpenAI 層級模型，其能力指數即各層級門檻。快取價空白者以新鮮輸入價計。能力指數空白者不參與前緣（不代表能力不足）。"
                    "Artificial Analysis 一週內改版三次（v4.1→4.3），跨版本分數不可比；本表全部取 v4.3／v4.3.2（S55、S56）", F_NOTE)
    ws.freeze_panes = "C4"
    # ---- named ranges
    nm(wb, "B4_PriceIn", f"Cap_In!$C${K['pin']}:$E${K['pin']}"); nm(wb, "B4_PriceCache", f"Cap_In!$C${K['pc']}:$E${K['pc']}")
    nm(wb, "B4_PriceOut", f"Cap_In!$C${K['pout']}:$E${K['pout']}")
    for k, n in [("disc", "B4_Disc"), ("chi", "B4_CacheHit"), ("eps", "B4_Eps"), ("cmult", "B4_CompMult"), ("pkmode", "B4_PeakMode"),
                 ("pkhr", "B4_PeakHrs"), ("offr", "B4_OffPeak"), ("serve", "B4_Serve"), ("free", "B4_Free"),
                 ("stier", "B4_StoreTier"), ("ret", "B4_Retain"), ("hits", "B4_Hits"), ("dram", "B4_DRAMcost"),
                 ("dlife", "B4_DRAMlife"), ("ssd", "B4_SSDcost"), ("slife", "B4_SSDlife")]:
        nm(wb, n, f"Cap_In!$C${K[k]}")
    nm(wb, "B4_Life", f"Cap_In!$C${K['life']}:$E${K['life']}")
    nm(wb, "B4_MixPaid", f"Cap_In!$C${K['mixp']}:$E${K['mixp']}"); nm(wb, "B4_MixFree", f"Cap_In!$C${K['mixf']}:$E${K['mixf']}")
    nm(wb, "B4_ISL", "Serving!$C$23:$E$23"); nm(wb, "B4_OSL", "Serving!$C$24:$E$24")
    a, b = K["tab0"], K["tab1"]
    for col, n in zip("ABCDEFGHI", ["B4_MktModel", "B4_MktVendor", "B4_MktCountry", "B4_MktOpen", "B4_MktIn",
                                    "B4_MktCache", "B4_MktOut", "B4_MktPeak", "B4_MktIndex"]):
        nm(wb, n, f"Cap_In!${col}${a}:${col}${b}")
    nm(wb, "B4_MktChina", f"Cap_In!$N${a}:$N${b}")
    ws.column_dimensions["N"].width = 10
    return K

# ---------------------------------------------------------------- Price_Frontier
def price_frontier(wb, K, TR):
    ws = wb.create_sheet("Price_Frontier")
    title(ws, "Price_Frontier — 單價前緣（K2 (i)：能力 ≥ OpenAI 層級模型者之中，參考請求混合單價最低者）",
          "混合單價＝（ISL ×〔(1−χ) 新鮮＋χ 快取〕＋ OSL × 輸出）÷（ISL＋OSL），用各層級參考任務（Serving 列 23–24）。前緣以『整筆請求』比較，不逐 token 類型取最低（避免拼出不存在的組合）。牌價為表列價（未折扣），折扣在 Theory_Rev 對所有廠商一致套用")
    for c, w in zip("ABCDEFGHIJKLMNOP", [24, 10, 8, 10, 10, 10, 9, 11, 11, 11, 11, 11, 11, 11, 11, 11]): ws.column_dimensions[c].width = w
    a, b = K["tab0"], K["tab1"]
    r = 4
    section(ws, r, "A. 候選模型的有效牌價與各層級參考請求混合單價", 16); r += 1
    hdr = ["模型", "國別", "能力指數", "時段係數", "新鮮輸入", "快取輸入", "輸出", "混合 Luna", "混合 Sol", "混合 Astra",
           "合格 Luna", "合格 Sol", "合格 Astra", "中國合格 Luna", "中國合格 Sol", "中國合格 Astra"]
    for i, t in enumerate(hdr): put(ws, f"{L(i+1)}{r}", t, F_BOLD, wrap=True)
    ws.row_dimensions[r].height = 30; r += 1
    P = {"t0": r}
    for j in range(a, b + 1):
        put(ws, f"A{r}", f"=Cap_In!A{j}", F_LINK); put(ws, f"B{r}", f"=Cap_In!C{j}", F_LINK)
        put(ws, f"C{r}", f"=IF(ISNUMBER(Cap_In!I{j}),Cap_In!I{j},\"—\")", F_LINK, fmt="0")
        put(ws, f"D{r}", f"=IF(Cap_In!H{j}=1,IF(B4_PeakMode=1,1,(B4_PeakHrs+(168-B4_PeakHrs)*B4_OffPeak)/168),1)", fmt="0.000")
        put(ws, f"E{r}", f"=Cap_In!E{j}*D{r}", F_LINK, fmt="#,##0.000")
        put(ws, f"F{r}", f"=IF(ISNUMBER(Cap_In!F{j}),Cap_In!F{j},Cap_In!E{j})*D{r}", F_LINK, fmt="#,##0.000")
        put(ws, f"G{r}", f"=Cap_In!G{j}*D{r}", F_LINK, fmt="#,##0.000")
        for t in range(3):
            put(ws, f"{'HIJ'[t]}{r}", f"=(INDEX(B4_ISL,1,{t+1})*((1-B4_CacheHit)*E{r}+B4_CacheHit*F{r})+INDEX(B4_OSL,1,{t+1})*G{r})"
                                      f"/(INDEX(B4_ISL,1,{t+1})+INDEX(B4_OSL,1,{t+1}))", fmt="#,##0.000")
            thr = f"$C${P['t0']+t}"   # first three candidate rows = OpenAI tier models
            put(ws, f"{'KLM'[t]}{r}", f"=IF(AND(ISNUMBER(C{r}),ISNUMBER({thr})),IF(C{r}>={thr},{'HIJ'[t]}{r},1E9),1E9)", fmt="#,##0.000")
            put(ws, f"{'NOP'[t]}{r}", f"=IF(Cap_In!N{j}=1,{'KLM'[t]}{r},1E9)", fmt="#,##0.000")
        r += 1
    P["t1"] = r - 1; t0, t1 = P["t0"], P["t1"]
    put(ws, f"A{r}", "合格欄 1E9＝不合格（能力指數低於該層級 OpenAI 模型或未取得）", F_NOTE); r += 2
    section(ws, r, "B. 各層級前緣（欄＝Luna／Sol／Astra）", 16); r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for t, (tk, tn) in enumerate(TIERS): put(ws, f"{TC[t]}{r}", tn, F_BOLD)
    r += 1
    def srow(key, lab, unit, f, fmt="#,##0.000", fill=None):
        nonlocal r
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
        for t in range(3):
            put(ws, f"{TC[t]}{r}", f.format(t=t + 1, H="HIJ"[t], Q="KLM"[t], N="NOP"[t], C=TC[t]), fmt=fmt, fill=fill)
        P[key] = r; r += 1
    rng = lambda c: f"${c}${t0}:${c}${t1}"
    srow("thr", "層級能力門檻（OpenAI 層級模型的指數）", "指數", "", "0")
    for t in range(3): ws[f"{TC[t]}{P['thr']}"].value = f"=$C${t0+t}"
    srow("oai", "OpenAI 層級模型 混合單價（表列）", "$/M", "=INDEX(" + rng("{H}") + ",{t})")
    srow("fr", "前緣 混合單價（表列）", "$/M", "=MIN(" + rng("{Q}") + ")", fill=FILL_KEY)
    srow("frm", "前緣模型", "", "")
    for t in range(3): ws[f"{TC[t]}{P['frm']}"].value = f"=INDEX({rng('A')},MATCH({TC[t]}{P['fr']},{rng('KLM'[t])},0))"
    for key, lab, col in [("frin", "前緣 新鮮輸入（表列、時段加權）", "E"), ("frc", "前緣 快取輸入", "F"), ("frout", "前緣 輸出（含思考）", "G")]:
        srow(key, lab, "$/M", "")
        for t in range(3): ws[f"{TC[t]}{P[key]}"].value = f"=INDEX({rng(col)},MATCH({TC[t]}{P['fr']},{rng('KLM'[t])},0))"
    srow("prem", "OpenAI 溢價（OpenAI ÷ 前緣；1＝OpenAI 即前緣）", "x", "", "0.00", FILL_KEY)
    for t in range(3): ws[f"{TC[t]}{P['prem']}"].value = f"={TC[t]}{P['oai']}/{TC[t]}{P['fr']}"
    srow("cn", "中國廠商 合格者最低 混合單價", "$/M", "")
    for t in range(3): ws[f"{TC[t]}{P['cn']}"].value = f"=IF(MIN({rng('NOP'[t])})>=1E9,\"無合格\",MIN({rng('NOP'[t])}))"
    srow("cnm", "中國廠商 合格者最低 模型", "", "")
    for t in range(3): ws[f"{TC[t]}{P['cnm']}"].value = f"=IF(ISNUMBER({TC[t]}{P['cn']}),INDEX({rng('A')},MATCH({TC[t]}{P['cn']},{rng('NOP'[t])},0)),\"—\")"
    srow("cnr", "中國合格者最低 ÷ OpenAI 層級模型", "x", "", "0.00")
    for t in range(3): ws[f"{TC[t]}{P['cnr']}"].value = f"=IF(ISNUMBER({TC[t]}{P['cn']}),{TC[t]}{P['cn']}/{TC[t]}{P['oai']},\"—\")"
    srow("cnk", "中國廠商 合格家數（候選表中）", "個", "", "0")
    for t in range(3): ws[f"{TC[t]}{P['cnk']}"].value = f"=COUNTIF({rng('NOP'[t])},\"<1E9\")"
    r += 1
    section(ws, r, "C. 能力 → 單價倍數（K4 (c)：基準 ε＝0，倍數恆為 1）", 16); r += 1
    srow("hcap", "Tech_Registry H_CAP 有效倍數（能力增量，以有效算力表示）", "x", f"={TR['H_CAP']}", "0.00")
    srow("capf", "能力單價倍數＝（H_CAP × 有效訓練算力倍數）^ε", "x", "", "0.000", FILL_KEY)
    for t in range(3): ws[f"{TC[t]}{P['capf']}"].value = f"=EXP(B4_Eps*LN({TC[t]}{P['hcap']}*B4_CompMult))"
    r += 1
    section(ws, r, "D. OpenAI 有效單價（表列 ×（1−折扣）× 能力單價倍數；依 token 類型；下游連結 IF_Price*）", 16); r += 1
    for key, lab, rngname in [("ein", "新鮮輸入 $/M（有效）", "B4_PriceIn"), ("ec", "快取輸入 $/M（有效）", "B4_PriceCache"),
                              ("eth", "思考 $/M（有效；依輸出價計費）", "B4_PriceOut"), ("eout", "可見輸出 $/M（有效）", "B4_PriceOut")]:
        srow(key, lab, "$/M", "", "#,##0.000", FILL_KEY)
        for t in range(3): ws[f"{TC[t]}{P[key]}"].value = f"=INDEX({rngname},1,{t+1})*(1-B4_Disc)*{TC[t]}{P['capf']}"
    srow("eref", "參考請求混合 $/M 總 token（OpenAI 有效）", "$/M", "", "#,##0.000", FILL_KEY)
    for t in range(3):
        c = TC[t]
        ws[f"{c}{P['eref']}"].value = (f"=(INDEX(B4_ISL,1,{t+1})*((1-B4_CacheHit)*{c}{P['ein']}+B4_CacheHit*{c}{P['ec']})+INDEX(B4_OSL,1,{t+1})*{c}{P['eout']})"
                                       f"/(INDEX(B4_ISL,1,{t+1})+INDEX(B4_OSL,1,{t+1}))")
    srow("fref", "參考請求混合 $/M 總 token（前緣有效＝前緣表列 ×（1−折扣））", "$/M", "", "#,##0.000", FILL_KEY)
    for t in range(3): ws[f"{TC[t]}{P['fref']}"].value = f"={TC[t]}{P['fr']}*(1-B4_Disc)"
    for key, n in [("ein", "B4_EffIn"), ("ec", "B4_EffCache"), ("eout", "B4_EffOut"), ("eref", "B4_EffRef"), ("fref", "B4_FrontRef")]:
        nm(wb, n, f"Price_Frontier!$C${P[key]}:$E${P[key]}")
    ws.freeze_panes = "B6"
    return P

# ---------------------------------------------------------------- Capability
def capability(wb, K, P, TRN, TI):
    ws = wb.create_sheet("Capability")
    title(ws, "Capability — 算力 → 能力 → 單價（K3：AA 指數為主、METR 為檢查；K4：只作檢查與反解，不驅動基準營收）",
          "本頁回答三件事：(1) 各層級門檻模型的能力位置；(2) 本模型各層級的訓練算力與能力的對應（檢查用，Tokenomics 架構為代理，不等於 OpenAI 實際模型）；(3) 為何不由斜率驅動單價")
    for c, w in zip("ABCDEFG", [52, 10, 14, 14, 14, 14, 70]): ws.column_dimensions[c].width = w
    C = {}
    r = 4
    section(ws, r, "A. 各層級（VR200 欄；FLOPs 與世代無關）", 7); r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for t, (tk, tn) in enumerate(TIERS): put(ws, f"{TC[t]}{r}", tn, F_BOLD)
    put(ws, f"G{r}", "說明", F_BOLD); r += 1
    tcol = "LMN"   # Training VR200 base columns: L/M/N = VR200 Luna/Sol/Astra
    rows = [
      ("flop", "最終訓練 FLOPs（預訓練＋後訓練；Training Cfin）", "FLOP", lambda t: f"=Training!{tcol[t]}{TRN['Cfin']}", "0.00E+00", "Block 3"),
      ("lflop", "log10 FLOPs", "", lambda t: f"=LN({TC[t]}{{flop}})/LN(10)", "0.00", ""),
      ("idx", "門檻模型能力指數（AA）", "指數", lambda t: f"=Price_Frontier!{TC[t]}{P['thr']}", "0", "Cap_In F 節前 3 列"),
      ("slope", "相鄰層級：每 10 倍算力的指數增量", "點／10x", lambda t: "=\"—\"" if t == 0 else
           f"=({TC[t]}{{idx}}-{TC[t-1]}{{idx}})/({TC[t]}{{lflop}}-{TC[t-1]}{{lflop}})", "0.0", "Derived；代理架構，僅示意"),
      ("pgap", "相鄰層級：OpenAI 混合單價倍數", "x", lambda t: "=\"—\"" if t == 0 else
           f"=Price_Frontier!{TC[t]}{P['oai']}/Price_Frontier!{TC[t-1]}{P['oai']}", "0.0", "Price_Frontier B 節"),
      ("cgap", "相鄰層級：本模型 decode 成本倍數（VR200 基準）", "x", lambda t: "=\"—\"" if t == 0 else
           f"=INDEX(IF_CostDec_{TIERS[t][0]},1,11)/INDEX(IF_CostDec_{TIERS[t-1][0]},1,11)", "0.0", "價格倍數 ≈ 成本倍數時，層級價差主要反映服務成本"),
    ]
    for key, lab, unit, f, fmt, note in rows:
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit); C[key] = r
        for t in range(3):
            put(ws, f"{TC[t]}{r}", f(t).replace("{flop}", str(C.get("flop", 0))).replace("{lflop}", str(C.get("lflop", 0)))
                .replace("{idx}", str(C.get("idx", 0))), fmt=fmt)
        put(ws, f"G{r}", note, F_NOTE, wrap=True); r += 1
    r += 1
    section(ws, r, "B. J8 檢查：前沿預訓練錨點 vs Astra", 7); r += 1
    put(ws, f"A{r}", "前沿錨點中值 ÷ Astra 最終訓練 FLOPs"); put(ws, f"B{r}", "x")
    put(ws, f"C{r}", f"=Train_In!$C${TI['an2']}/E{C['flop']}", fmt="0.0", fill=FILL_KEY)
    put(ws, f"G{r}", "若 Astra 對標 GPT-6 Astra，算力可能低估約此倍數（E006 待查）；Cap_In 有效訓練算力倍數高值即取此量級", F_NOTE, wrap=True)
    C["j8"] = r; r += 2
    section(ws, r, "C. 為何 K4 不採 (a)（摘要；數字見 Checks Block 4 與 Price_Frontier）", 7); r += 1
    for txt in [
        "1. 識別：同層級牌價跨廠商差距大（例：Sol 級輸出價 DeepSeek V4-Pro 離峰 $1.98 至 Kimi K3 $15），主要由廠商策略與成本決定，斜率無法與能力分離。",
        "2. 循環：前緣由接近成本定價的廠商決定（Checks：DeepSeek 價 ÷ 本模型 Hopper 同架構成本約 0.8–1.0），前緣斜率≈服務成本斜率，已由 Unit_Cost 計算。",
        "3. 重複：層級牌價已含能力；只有增量（H_CAP）可再進入，故以 ε 乘在增量上，基準 0。",
        "4. 誤差相乘：J8 算力缺口約 7 倍 × ε 0–0.5 → 單價倍數 1.0–2.6，大於利用率區間的影響。",
        "(d) 反解：Amortize 頁『回本所需單價溢價』與觀測層級價差並列，回答『訓練能否回本』而不假設斜率。",
        "METR 時間長度（K3 檢查）：尚未入表，待查。"]:
        put(ws, f"A{r}", txt, F_NOTE); r += 1
    return C

# ---------------------------------------------------------------- Cache_Store
def cache_store(wb):
    ws = wb.create_sheet("Cache_Store")
    title(ws, "Cache_Store — 快取儲存成本（Block 2 未結事項 4；每 M 快取命中 token；加在 IF_CostCache 之上）",
          "儲存 $/M 快取命中＝KV bytes/token × 10⁶ ÷ 10⁹ × 儲存層 $/GB-hr × 保留時間 ÷ 每次寫入命中次數。HBM 以每 GPU 小時持有成本 ÷ HBM 容量計（把整顆 GPU 成本歸給 HBM，為上限）")
    head15(ws)
    S = {}
    r = 9
    section(ws, r, "共用（儲存層 $/GB-hr）", 17); r += 1
    row15(ws, r, "SSD", "$/GB-hr", "=B4_SSDcost/(B4_SSDlife*8760)", "0.000000"); S["ssd"] = r; r += 1
    row15(ws, r, "DRAM", "$/GB-hr", "=B4_DRAMcost/(B4_DRAMlife*8760)", "0.000000"); S["dram"] = r; r += 1
    row15(ws, r, "HBM（上限）", "$/GB-hr", "=Unit_Cost!{X}$8/INDEX(Spec_Rack!$C$25:$G$25,1,{X}$6)", "0.000000"); S["hbm"] = r; r += 1
    row15(ws, r, "採用儲存層", "$/GB-hr", f"=CHOOSE(B4_StoreTier,{{X}}{S['ssd']},{{X}}{S['dram']},{{X}}{S['hbm']})", "0.000000"); S["sel"] = r; r += 2
    for t, (tk, tn) in enumerate(TIERS):
        section(ws, r, tn, 17); r += 1
        row15(ws, r, "KV bytes/token（Arch 採用列）", "B", f"=Arch!${TC[t]}$25", "#,##0"); kv = r; r += 1
        row15(ws, r, f"儲存 $/M 快取命中 token　[IF_CacheStore_{tk}]", "$/M",
              f"={{X}}{kv}*1E6/1E9*{{X}}${S['sel']}*B4_Retain/B4_Hits", "#,##0.00000", key=True); S[tk] = r; r += 1
        row15(ws, r, "儲存 ÷ 快取命中載入成本（IF_CostCache）", "x", f"=IF({IF(f'IF_CostCache_{tk}')}>0,{{X}}{S[tk]}/{IF(f'IF_CostCache_{tk}')},0)", "0.00"); r += 1
        row15(ws, r, "儲存 ÷ OpenAI 快取輸入有效價", "%", f"={{X}}{S[tk]}/INDEX(B4_EffCache,1,{t+1})", "0.00%"); r += 2
    return S

# ---------------------------------------------------------------- Fleet_1GW
def fleet(wb, K):
    ws = wb.create_sheet("Fleet_1GW")
    title(ws, "Fleet_1GW — 1 GW（IT）參考機隊配置（J11、K7）",
          "用途：對外服務（付費／免費）、最終訓練、研發實驗；服務 GW 依層級 token 組合分配：服務 token 總量 T＝服務 GW × 利用率 ÷ Σ（組合ₜ ÷ 每 GW 產出ₜ）。訓練＋研發＝1−服務；其中最終訓練＝÷ 研發倍數")
    head15(ws)
    F = {}
    r = 9
    section(ws, r, "A. 用途配置（GW）", 17); r += 1
    for key, lab, f in [("sv", "對外服務", "=B4_Serve"), ("pd", "  付費服務", "=B4_Serve*(1-B4_Free)"), ("fr", "  免費服務", "=B4_Serve*B4_Free"),
                        ("tr", "訓練＋研發", "=1-B4_Serve"), ("fin", "  最終訓練", "=(1-B4_Serve)/IF_RDMult"),
                        ("rd", "  研發實驗（不含最終訓練）", "=(1-B4_Serve)*(1-1/IF_RDMult)")]:
        row15(ws, r, lab, "GW", f, "0.000", key=(key in ("pd", "tr"))); F[key] = r; r += 1
    r += 1
    section(ws, r, "B. 服務 token（基準利用率；M tok/年）", 17); r += 1
    inv = lambda mix: "+".join(f"INDEX({mix},1,{t+1})/{IF(f'IF_TokGW_{tk}')}" for t, (tk, _) in enumerate(TIERS))
    # v5.9：SLO 不可達保護（CC 第 7 輪第 6 節第 1 項）——組合權重 > 0 的層級若每 GW 產出為 0，該欄機隊無法服務
    ok = lambda mix: "AND(" + ",".join(f"OR(INDEX({mix},1,{t+1})=0,{IF(f'IF_TokGW_{tk}')}>0)" for t, (tk, _) in enumerate(TIERS)) + ")"
    row15(ws, r, "可服務（組合內各層級皆 SLO 可達＝1）", "旗標", f"=IF(AND({ok('B4_MixPaid')},{ok('B4_MixFree')}),1,0)", "0"); F["ok"] = r; r += 1
    row15(ws, r, "付費服務 token 總量", "M tok/年", f"=IF({{X}}{F['ok']}=1,{{X}}{F['pd']}*IF_Util/({inv('B4_MixPaid')}),\"SLO 不可達\")", "#,##0"); F["Tp"] = r; r += 1
    row15(ws, r, "免費服務 token 總量", "M tok/年", f"=IF({{X}}{F['ok']}=1,{{X}}{F['fr']}*IF_Util/({inv('B4_MixFree')}),\"SLO 不可達\")", "#,##0"); F["Tf"] = r; r += 1
    for t, (tk, tn) in enumerate(TIERS):
        row15(ws, r, f"{tn} 付費 token", "M tok/年", f"=IF({{X}}{F['ok']}=1,{{X}}{F['Tp']}*INDEX(B4_MixPaid,1,{t+1}),\"SLO 不可達\")", "#,##0"); F[f"p{t}"] = r; r += 1
        row15(ws, r, f"{tn} 免費 token", "M tok/年", f"=IF({{X}}{F['ok']}=1,{{X}}{F['Tf']}*INDEX(B4_MixFree,1,{t+1}),\"SLO 不可達\")", "#,##0"); F[f"f{t}"] = r; r += 1
        row15(ws, r, f"{tn} 服務 GW", "GW", f"=IF({{X}}{F['ok']}=1,IF({IF(f'IF_TokGW_{tk}')}>0,({{X}}{F[f'p{t}']}+{{X}}{F[f'f{t}']})/({IF(f'IF_TokGW_{tk}')}*IF_Util),0),\"SLO 不可達\")", "0.000"); F[f"g{t}"] = r; r += 1
    row15(ws, r, "檢查：各層級服務 GW 合計 − 對外服務 GW（應為 0）", "GW",
          f"=IF({{X}}{F['ok']}=1,{{X}}{F['g0']}+{{X}}{F['g1']}+{{X}}{F['g2']}-{{X}}{F['sv']},\"SLO 不可達\")", "0.000000"); F["chk"] = r; r += 2
    section(ws, r, "C. 與 Block 3 一致性", 17); r += 1
    row15(ws, r, "家族研發計畫占 1 GW 年（三層級合計）", "%",
          "=" + "+".join(IF(f"IF_ProgGWyr_{tk}") for tk, _ in TIERS), "0.00%"); F["fam"] = r; r += 1
    row15(ws, r, "隱含每 GW 年可容納的家族研發計畫數（訓練＋研發 ÷ 家族計畫）", "個", f"={{X}}{F['tr']}/{{X}}{F['fam']}", "0.0", key=True)
    F["nprog"] = r; r += 1
    put(ws, f"A{r}", "解讀：前沿實驗室每年約 1–3 個旗艦家族；遠高於此代表 Block 3 單一計畫規模偏小（J8）或機隊訓練占比偏高", F_NOTE)
    return F

# ---------------------------------------------------------------- Amortize
def amortize(wb, F, P, S):
    ws = wb.create_sheet("Amortize")
    title(ws, "Amortize — 訓練攤提（K6：自下而上、由上而下並列；下游預設 (c)＝由上而下總額 × 自下而上權重，Andy 2026-10-01）",
          "自下而上＝層級研發計畫成本 ÷（1 GW 參考機隊在商業壽命內服務的該層級 token）；由上而下＝機隊訓練占比 X ÷（1−X）× 服務成本。"
          "前者同時是『回本所需單價溢價』（K4 (d)）。(c)、(d) 只改變層級間分配，總額同由上而下")
    head15(ws)
    A = {}
    NA = '"SLO 不可達"'
    num = lambda *refs: "AND(" + ",".join(f"ISNUMBER({x})" for x in refs) + ")"
    r = 9
    for t, (tk, tn) in enumerate(TIERS):
        section(ws, r, tn, 17); r += 1
        row15(ws, r, "研發計畫成本（IF_ProgCost）", "$M", f"={IF(f'IF_ProgCost_{tk}')}", "#,##0.0"); pc = r; A[f"pc{t}"] = r; r += 1
        p_, f_ = f"Fleet_1GW!{{X}}{F[f'p{t}']}", f"Fleet_1GW!{{X}}{F[f'f{t}']}"
        row15(ws, r, "年服務 token（付費＋免費）", "M tok/年", f"=IF({num(p_, f_)},{p_}+{f_},{NA})", "#,##0"); A[f"yr{t}"] = r; r += 1
        row15(ws, r, "商業壽命內服務 token（付費＋免費）", "M tok",
              f"=IF(ISNUMBER({{X}}{A[f'yr{t}']}),{{X}}{A[f'yr{t}']}*INDEX(B4_Life,1,{t+1})/12,{NA})", "#,##0"); sv = r; r += 1
        row15(ws, r, f"自下而上攤提＝回本所需單價溢價　[IF_AmortBU_{tk}]", "$/M",
              f"=IF(ISNUMBER({{X}}{sv}),IF({{X}}{sv}>0,{{X}}{pc}*1E6/{{X}}{sv},0),{NA})", "#,##0.00000", key=True)
        A[f"bu{t}"] = r; r += 1
        cost = (f"(INDEX(B4_ISL,1,{t+1})*((1-B4_CacheHit)*{IF(f'IF_CostPre_{tk}')}+B4_CacheHit*({IF(f'IF_CostCache_{tk}')}+Cache_Store!{{X}}{S[tk]}))"
                f"+INDEX(B4_OSL,1,{t+1})*{IF(f'IF_CostDec_{tk}')})/(INDEX(B4_ISL,1,{t+1})+INDEX(B4_OSL,1,{t+1}))/IF_Util")
        A[f"cost{t}"] = cost
        row15(ws, r, "服務成本（參考請求混合，含快取儲存，基準利用率）", "$/M",
              f"=IF(ISNUMBER({IF(f'IF_CostDec_{tk}')}),{cost},{NA})", "#,##0.0000"); A[f"sc{t}"] = r; r += 1
        row15(ws, r, f"由上而下攤提　[IF_AmortTD_{tk}]", "$/M",
              f"=IF(ISNUMBER({{X}}{A[f'sc{t}']}),Fleet_1GW!{{X}}{F['tr']}/(1-Fleet_1GW!{{X}}{F['tr']})*{{X}}{A[f'sc{t}']},{NA})", "#,##0.0000", key=True)
        A[f"td{t}"] = r; r += 1
        row15(ws, r, "由上而下 ÷ 自下而上", "x",
              f"=IF({num('{X}'+str(A[f'bu{t}']), '{X}'+str(A[f'td{t}']))},IF({{X}}{A[f'bu{t}']}>0,{{X}}{A[f'td{t}']}/{{X}}{A[f'bu{t}']},0),{NA})", "#,##0.0"); r += 1
        if t > 0:
            row15(ws, r, "回本所需溢價 ÷ 觀測層級價差（本層級 − 下一層級 OpenAI 有效混合單價）", "%",
                  f"=IF(ISNUMBER({{X}}{A[f'bu{t}']}),{{X}}{A[f'bu{t}']}/(INDEX(B4_EffRef,1,{t+1})-INDEX(B4_EffRef,1,{t})),{NA})", "0.000%"); r += 1
        r += 1
    # ---- v5.9 K6：(c)、(d) 與下游預設
    section(ws, r, "K6 下游預設（Andy 2026-10-01）：(c) 由上而下總額 × 自下而上權重（預設）；(d) 由上而下總額 × 營收權重（並列）", 17); r += 1
    allnum = lambda key: num(*[f"{{X}}{A[f'{key}{t}']}" for t in range(3)])
    tdsum = "+".join(f"{{X}}{A[f'td{t}']}*{{X}}{A[f'yr{t}']}" for t in range(3))
    row15(ws, r, "由上而下年化總額（三層級合計）", "$M/年", f"=IF({allnum('td')},({tdsum})/1E6,{NA})", "#,##0.0")
    A["tdtot"] = r; r += 1
    row15(ws, r, "自下而上年化總額（研發計畫成本 × 12 ÷ 商業壽命，合計）", "$M/年",
          "=" + "+".join(f"{{X}}{A[f'pc{t}']}*12/INDEX(B4_Life,1,{t+1})" for t in range(3)), "#,##0.0"); A["butot"] = r; r += 1
    row15(ws, r, "縮放倍數（由上而下 ÷ 自下而上總額）", "x",
          f"=IF(ISNUMBER({{X}}{A['tdtot']}),IF({{X}}{A['butot']}>0,{{X}}{A['tdtot']}/{{X}}{A['butot']},0),{NA})", "0.00", key=True); A["scale"] = r; r += 1
    pay = lambda t: f"Fleet_1GW!{{X}}{F[f'p{t}']}*INDEX(B4_EffRef,1,{t+1})"
    paidrefs = [f"Fleet_1GW!{{X}}{F[f'p{t}']}" for t in range(3)]
    paysum = "+".join(pay(t) for t in range(3))
    row15(ws, r, "付費營收合計（OpenAI 有效單價）", "$M/年", f"=IF({num(*paidrefs)},({paysum})/1E6,{NA})", "#,##0.0")
    A["revtot"] = r; r += 1
    for t, (tk, tn) in enumerate(TIERS):
        row15(ws, r, f"{tn}：(c) 由上而下總額 × 自下而上權重（下游預設）　[IF_AmortDefault_{tk}]", "$/M",
              f"=IF({num('{X}'+str(A[f'bu{t}']), '{X}'+str(A['scale']))},{{X}}{A[f'bu{t}']}*{{X}}{A['scale']},{NA})", "#,##0.00000", key=True)
        A[f"dc{t}"] = r; r += 1
        row15(ws, r, f"{tn}：(d) 由上而下總額 × 營收權重　[IF_AmortRev_{tk}]", "$/M",
              f"=IF({num('{X}'+str(A['revtot']), '{X}'+str(A[f'yr{t}']))},IF(AND({{X}}{A['revtot']}>0,{{X}}{A[f'yr{t}']}>0),"
              f"{{X}}{A['tdtot']}*({pay(t)}/1E6/{{X}}{A['revtot']})*1E6/{{X}}{A[f'yr{t}']},0),{NA})", "#,##0.00000")
        A[f"dd{t}"] = r; r += 1
    row15(ws, r, "(d) 攤提占付費營收（各層級相同）", "%",
          f"=IF(ISNUMBER({{X}}{A['revtot']}),IF({{X}}{A['revtot']}>0,{{X}}{A['tdtot']}/{{X}}{A['revtot']},0),{NA})", "0.0%"); A["dshare"] = r; r += 1
    put(ws, f"A{r}", "註：(c) 保留由上而下的總額（與觀測支出一致），層級間依物理計畫成本分配；縮放倍數與 Fleet_1GW『隱含家族研發計畫數』同源（J8）。"
                     "若 J8 低估集中於 Astra，(c) 對 Astra 仍偏低。(d) 為聯合成本的相對售價法。毛利率另列不含攤提口徑，以便與公司揭露比較", F_NOTE)
    return A

# ---------------------------------------------------------------- Theory_Rev
def theory_rev(wb, F, A, S, WL=None):
    NA = '"SLO 不可達"'
    WL = WL or {"fp": 22, "cp": 23, "dp": 24, "cost0": 33}
    ws = wb.create_sheet("Theory_Rev")
    title(ws, "Theory_Rev — 每 GW 理論營收（理想上限：SLO 產能 × 利用率 × 層級有效單價；不含需求、市占、訂閱方案）",
          "A 節＝單一層級滿載 1 GW；B 節＝1 GW 參考機隊（付費服務 token × 單價；免費服務營收 0）。OpenAI 單價為主線（K1），前緣單價並列（K2 (i)）。成本＝經濟口徑")
    head15(ws)
    T = {}
    r = 9
    for t, (tk, tn) in enumerate(TIERS):
        cs = S[tk]
        section(ws, r, f"A. {tn}：1 GW 只服務本層級", 17); r += 1
        row15(ws, r, "每 GW 產出（基準利用率）", "M tok/年", f"={IF(f'IF_TokGW_{tk}')}*IF_Util", "#,##0"); tok = r; r += 1
        row15(ws, r, f"理論營收 — OpenAI 有效單價　[IF_RevGW_{tk}]", "$B/年", f"={{X}}{tok}*INDEX(B4_EffRef,1,{t+1})/1E9", "#,##0.0", key=True)
        T[f"rev{t}"] = r; r += 1
        row15(ws, r, f"理論營收 — 前緣單價　[IF_RevGWFront_{tk}]", "$B/年", f"={{X}}{tok}*INDEX(B4_FrontRef,1,{t+1})/1E9", "#,##0.0"); T[f"revf{t}"] = r; r += 1
        row15(ws, r, "理論營收 — 100% 利用率（OpenAI）", "$B/年", f"={IF(f'IF_TokGW_{tk}')}*INDEX(B4_EffRef,1,{t+1})/1E9", "#,##0.0"); r += 1
        row15(ws, r, "年持有成本 — 經濟（IF_HoldEcon）", "$B/年", f"={IF('IF_HoldEcon')}", "#,##0.0"); hold = r; r += 1
        row15(ws, r, "理論營收 ÷ 持有成本", "x", f"={{X}}{T[f'rev{t}']}/{{X}}{hold}", "0.0", key=True); T[f"rh{t}"] = r; r += 1
        row15(ws, r, "前緣營收 ÷ 持有成本", "x", f"={{X}}{T[f'revf{t}']}/{{X}}{hold}", "0.0"); r += 1
        row15(ws, r, "服務成本 $/M（參考請求，含快取儲存，基準利用率）", "$/M", f"=Amortize!{{X}}{A[f'sc{t}']}", "#,##0.0000"); sc = r; r += 1
        g = lambda am: f"=IF(AND(ISNUMBER({{X}}{sc}),ISNUMBER(Amortize!{{X}}{am})),{{X}}{sc}+Amortize!{{X}}{am},{NA})"
        row15(ws, r, f"全成本 $/M（服務＋自下而上攤提）　[IF_FullCost_{tk}]", "$/M", g(A[f'bu{t}']), "#,##0.0000", key=True); T[f"fc{t}"] = r; r += 1
        row15(ws, r, "全成本 $/M（服務＋由上而下攤提）", "$/M", g(A[f'td{t}']), "#,##0.0000"); T[f"fct{t}"] = r; r += 1
        row15(ws, r, f"全成本 $/M（服務＋K6 預設 (c) 攤提）　[IF_FullCostDefault_{tk}]", "$/M", g(A[f'dc{t}']), "#,##0.0000", key=True); T[f"fcd{t}"] = r; r += 1
        gm = lambda fc, price: f"=IF(ISNUMBER({{X}}{fc}),1-{{X}}{fc}/INDEX({price},1,{t+1}),{NA})"
        row15(ws, r, "理論毛利率（OpenAI 單價；不含攤提，可與公司揭露毛利率比較）", "%", gm(sc, "B4_EffRef"), "0%"); r += 1
        row15(ws, r, "理論毛利率（OpenAI 單價；自下而上全成本）", "%", gm(T[f'fc{t}'], "B4_EffRef"), "0%"); r += 1
        row15(ws, r, "理論毛利率（OpenAI 單價；由上而下全成本）", "%", gm(T[f'fct{t}'], "B4_EffRef"), "0%"); r += 1
        row15(ws, r, "理論毛利率（OpenAI 單價；K6 預設 (c) 全成本）", "%", gm(T[f'fcd{t}'], "B4_EffRef"), "0%", key=True); r += 1
        row15(ws, r, "理論毛利率（前緣單價；由上而下全成本）", "%", gm(T[f'fct{t}'], "B4_FrontRef"), "0%"); r += 2
    section(ws, r, "B. 1 GW 參考機隊（Fleet_1GW 配置）", 17); r += 1
    ok = f"Fleet_1GW!{{X}}{F['ok']}=1"
    pay = lambda ref: "+".join(f"Fleet_1GW!{{X}}{F[f'p{t}']}*INDEX({ref},1,{t+1})" for t in range(3))
    # v5.9（Andy 決定 (b)）：機隊合計保留，另列各層級貢獻，使混合數字可拆解（CLAUDE.md 1a）
    for t, (tk, tn) in enumerate(TIERS):
        row15(ws, r, f"{tn} 貢獻 — OpenAI 有效單價　[IF_RevGWFleet_{tk}]", "$B/年",
              f"=IF({ok},Fleet_1GW!{{X}}{F[f'p{t}']}*INDEX(B4_EffRef,1,{t+1})/1E9,{NA})", "#,##0.00"); T[f"flt{t}"] = r; r += 1
    row15(ws, r, "付費服務營收合計（層級組合：付費 token 依 B4_MixPaid）— OpenAI 有效單價　[IF_RevGWFleet]", "$B/年",
          f"=IF({ok},({pay('B4_EffRef')})/1E9,{NA})", "#,##0.0", key=True); T["fl"] = r; r += 1
    for t, (tk, tn) in enumerate(TIERS):
        row15(ws, r, f"{tn} 貢獻 — 前緣單價　[IF_RevGWFleetFront_{tk}]", "$B/年",
              f"=IF({ok},Fleet_1GW!{{X}}{F[f'p{t}']}*INDEX(B4_FrontRef,1,{t+1})/1E9,{NA})", "#,##0.00"); T[f"flft{t}"] = r; r += 1
    row15(ws, r, "付費服務營收合計（層級組合）— 前緣單價　[IF_RevGWFleetFront]", "$B/年", f"=IF({ok},({pay('B4_FrontRef')})/1E9,{NA})", "#,##0.0"); T["flf"] = r; r += 1
    row15(ws, r, "整個 GW 年持有成本（服務＋訓練＋研發）", "$B/年", f"={IF('IF_HoldEcon')}", "#,##0.0"); fh = r; r += 1
    row15(ws, r, "機隊營收 ÷ 持有成本", "x", f"=IF(ISNUMBER({{X}}{T['fl']}),{{X}}{T['fl']}/{{X}}{fh},{NA})", "0.00", key=True); T["flr"] = r; r += 1
    row15(ws, r, "服務 token 加權平均有效單價", "$/M",
          f"=IF({ok},({pay('B4_EffRef')})/(Fleet_1GW!{{X}}{F['Tp']}+Fleet_1GW!{{X}}{F['Tf']}),{NA})", "#,##0.000"); r += 2
    section(ws, r, "C. 每任務營收（OpenAI 有效單價；欄＝Workload 任務類型 C–G；與 Workload 每任務成本對照；harness 依 Tech_Registry T12 混合）", 17); r += 1
    put(ws, f"A{r}", "層級 × 任務", F_BOLD)
    for c in "CDEFG": put(ws, f"{c}{r}", f"=Workload!{c}4", F_HLINK)
    r += 1
    T["task0"] = r
    for t, (tk, tn) in enumerate(TIERS):
        put(ws, f"A{r}", f"{tn} 每任務營收"); put(ws, f"B{r}", "$")
        for c in "CDEFG":
            put(ws, f"{c}{r}", f"=(Workload!{c}{WL['fp']}*INDEX(B4_EffIn,1,{t+1})+Workload!{c}{WL['cp']}*INDEX(B4_EffCache,1,{t+1})+Workload!{c}{WL['dp']}*INDEX(B4_EffOut,1,{t+1}))/1E6",
                fmt="0.0000", fill=FILL_KEY)
        r += 1
    for g, (lab, wr) in enumerate([("VR200", WL["cost0"]), ("GB300", WL["cost0"] + 3)]):
        for t, (tk, tn) in enumerate(TIERS):
            put(ws, f"A{r}", f"{lab} × {tk} 每任務營收 ÷ 服務成本（Workload）"); put(ws, f"B{r}", "x")
            for c in "CDEFG":
                put(ws, f"{c}{r}", f"=IF(ISNUMBER(Workload!{c}{wr+t}),IF(Workload!{c}{wr+t}>0,{c}{T['task0']+t}/Workload!{c}{wr+t},0),\"SLO 不可達\")", fmt="0.0")
            r += 1
    put(ws, f"A{r}", "註：Workload 每任務成本未含快取儲存與攤提；任務的快取命中率取 Workload 列 11，與 A 節參考請求的 χ 不同", F_NOTE)
    return T

# ---------------------------------------------------------------- Sens_Rev
def sens_rev(wb, K, T, A):
    ws = wb.create_sheet("Sens_Rev")
    title(ws, "Sens_Rev — Block 4 敏感度（VR200 × Sol、基準成本；單一輸入變動，其餘不變）",
          "營收 ∝ 利用率 ×（1−折扣）× 混合單價（χ）；攤提 ∝ 1 ÷ 商業壽命。本頁以封閉式重算，不改動 Cap_In")
    for c, w in zip("ABCDEFG", [56, 12, 14, 14, 14, 14, 50]): ws.column_dimensions[c].width = w
    for c, h in zip("ABCDEFG", ["變動", "值", "Sol 營收 ÷ 持有成本", "相對基準", "機隊營收 ÷ 持有成本", "相對基準", "說明"]):
        put(ws, f"{c}4", h, F_BOLD, wrap=True)
    col = "M"   # VR200 base
    base_rh = f"Theory_Rev!{col}{T['rh1']}"; base_fl = f"Theory_Rev!{col}{T['flr']}"
    isl, osl = "INDEX(B4_ISL,1,2)", "INDEX(B4_OSL,1,2)"
    def mix(chi): return f"(({isl}*((1-{chi})*INDEX(B4_PriceIn,1,2)+{chi}*INDEX(B4_PriceCache,1,2))+{osl}*INDEX(B4_PriceOut,1,2))/({isl}+{osl}))"
    rows = [
      ("基準", "—", "1", "1", "Cap_In 基準"),
      ("利用率 40%", 0.4, "B{r}/IF_Util", "B{r}/IF_Util", "營收與服務 token 同比；持有成本不變"),
      ("利用率 80%", 0.8, "B{r}/IF_Util", "B{r}/IF_Util", ""),
      ("折扣 10%", 0.1, "(1-B{r})/(1-B4_Disc)", "(1-B{r})/(1-B4_Disc)", ""),
      ("折扣 30%", 0.3, "(1-B{r})/(1-B4_Disc)", "(1-B{r})/(1-B4_Disc)", ""),
      ("快取命中 χ 30%", 0.3, mix("B{r}") + "/" + mix("B4_CacheHit"), "—", "只算 Sol 混合單價；機隊需重算各層級"),
      ("快取命中 χ 75%", 0.75, mix("B{r}") + "/" + mix("B4_CacheHit"), "—", ""),
      ("對外服務占機隊 30%", 0.3, "1", "B{r}/B4_Serve", "單一層級滿載不受影響"),
      ("對外服務占機隊 60%", 0.6, "1", "B{r}/B4_Serve", ""),
      ("免費占服務 35%", 0.35, "1", "(1-B{r})/(1-B4_Free)", ""),
      ("免費占服務 60%", 0.6, "1", "(1-B{r})/(1-B4_Free)", ""),
      ("前緣單價取代 OpenAI（Sol）", "—", "INDEX(B4_FrontRef,1,2)/INDEX(B4_EffRef,1,2)", "—", "K2 (i)：前緣即 OpenAI 時為 1"),
      ("ε＝0.5、有效算力 ×7（J8 缺口全數轉為能力）", 7, "EXP(0.5*LN(B{r}))/Price_Frontier!D{capf}", "EXP(0.5*LN(B{r}))/Price_Frontier!D{capf}", "K4 (a) 若採用的量級；不入基準"),
    ]
    r = 5
    for lab, v, fr, ff, note in rows:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", v, fmt="0%" if isinstance(v, float) else "0")
        fr2 = fr.replace("{r}", str(r)).replace("{capf}", str(K.get("_capf", 0)))
        ff2 = ff.replace("{r}", str(r)).replace("{capf}", str(K.get("_capf", 0)))
        put(ws, f"D{r}", f"={fr2}", fmt="0.00"); put(ws, f"C{r}", f"={base_rh}*D{r}", fmt="0.0", fill=FILL_KEY)
        if ff2 == "—":
            put(ws, f"F{r}", "—"); put(ws, f"E{r}", "—")
        else:
            put(ws, f"F{r}", f"={ff2}", fmt="0.00"); put(ws, f"E{r}", f"={base_fl}*F{r}", fmt="0.00", fill=FILL_KEY)
        put(ws, f"G{r}", note, F_NOTE, wrap=True); r += 1
    r += 1
    put(ws, f"A{r}", "攤提（自下而上，Sol）對商業壽命", F_BOLD); r += 1
    for lab, m in [("壽命 6 個月", 6), ("壽命 24 個月", 24)]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", m, fmt="0")
        put(ws, f"C{r}", f"=Amortize!{col}{A['bu1']}*INDEX(B4_Life,1,2)/B{r}", fmt="0.00000", fill=FILL_KEY)
        put(ws, f"D{r}", f"=C{r}/Amortize!{col}{A['bu1']}", fmt="0.00"); put(ws, f"G{r}", "$/M；與 Sol 有效混合單價相比仍極小", F_NOTE); r += 1
    put(ws, f"A{r+1}", "未列入：生產折減（Serving!C18）與利用率之外的產能變動需重算 Perf，見 Sens_Perf；本頁不重算物理產能", F_NOTE)

# ---------------------------------------------------------------- Interface D, Checks, Sources
def interface_b4(wb, start, P, S, A, T):
    ws = wb["Interface"]; r = start; names = []
    section(ws, r, "D. Block 4 產出（理想上限；單價為 2026-09／10 快照、各世代共用（K9）；IF_RevGW 等欄＝世代 × 成本情境）", 17); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        singles = [(f"IF_PriceFresh_{tk}", "新鮮輸入 $/M — OpenAI 有效", "ein"), (f"IF_PriceCached_{tk}", "快取輸入 $/M — OpenAI 有效", "ec"),
                   (f"IF_PriceThink_{tk}", "思考 $/M — OpenAI 有效（依輸出計費）", "eth"), (f"IF_PriceOut_{tk}", "可見輸出 $/M — OpenAI 有效", "eout"),
                   (f"IF_PriceRef_{tk}", "參考請求混合 $/M — OpenAI 有效", "eref"), (f"IF_FrontRef_{tk}", "參考請求混合 $/M — 前緣有效", "fref")]
        for name, lab, key in singles:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", "$/M")
            put(ws, f"C{r}", f"=Price_Frontier!{TC[t]}{P[key]}", fmt="#,##0.000", fill=FILL_KEY if key == "eref" else None)
            names.append((name, f"Interface!$C${r}")); r += 1
        put(ws, f"A{r}", f"前緣模型（顯示）　[IF_FrontModel_{tk}]"); put(ws, f"C{r}", f"=Price_Frontier!{TC[t]}{P['frm']}")
        names.append((f"IF_FrontModel_{tk}", f"Interface!$C${r}")); r += 1
        put(ws, f"A{r}", f"商業壽命　[IF_Life_{tk}]"); put(ws, f"B{r}", "月"); put(ws, f"C{r}", f"=INDEX(B4_Life,1,{t+1})", fmt="0")
        names.append((f"IF_Life_{tk}", f"Interface!$C${r}")); r += 1
        rows = [(f"IF_CacheStore_{tk}", "快取儲存 $/M 快取命中 token", "$/M", "#,##0.00000", f"=Cache_Store!{{X}}{S[tk]}"),
                (f"IF_AmortBU_{tk}", "訓練攤提 自下而上＝回本所需溢價", "$/M", "#,##0.00000", f"=Amortize!{{X}}{A[f'bu{t}']}"),
                (f"IF_AmortTD_{tk}", "訓練攤提 由上而下（機隊訓練占比）", "$/M", "#,##0.0000", f"=Amortize!{{X}}{A[f'td{t}']}"),
                (f"IF_FullCost_{tk}", "全成本 $/M（服務＋快取儲存＋自下而上攤提；基準利用率）", "$/M", "#,##0.0000", f"=Theory_Rev!{{X}}{T[f'fc{t}']}"),
                (f"IF_AmortDefault_{tk}", "訓練攤提 K6 預設 (c)：由上而下總額 × 自下而上權重（下游預設）", "$/M", "#,##0.00000", f"=Amortize!{{X}}{A[f'dc{t}']}"),
                (f"IF_AmortRev_{tk}", "訓練攤提 (d)：由上而下總額 × 營收權重", "$/M", "#,##0.00000", f"=Amortize!{{X}}{A[f'dd{t}']}"),
                (f"IF_FullCostDefault_{tk}", "全成本 $/M（服務＋快取儲存＋K6 預設攤提；基準利用率；下游預設）", "$/M", "#,##0.0000", f"=Theory_Rev!{{X}}{T[f'fcd{t}']}"),
                (f"IF_RevGW_{tk}", "每 GW 理論營收 — OpenAI 有效單價（理想上限）", "$B/年", "#,##0.0", f"=Theory_Rev!{{X}}{T[f'rev{t}']}"),
                (f"IF_RevGWFront_{tk}", "每 GW 理論營收 — 前緣單價（理想上限）", "$B/年", "#,##0.0", f"=Theory_Rev!{{X}}{T[f'revf{t}']}")]
        for name, lab, unit, fmt, tpl in rows:
            put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
            for X in COLS15: put(ws, f"{X}{r}", tpl.replace("{X}", X), fmt=fmt, fill=FILL_KEY if ("RevGW_" in name or "Default" in name) else None)
            names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    put(ws, f"A{r}", "1 GW 參考機隊（合計為層級組合：付費 token 依 Cap_In 組合；各層級貢獻另列，合計＝三層級貢獻之和）", F_BOLD); r += 1
    fleet_rows = [(f"IF_RevGWFleet_{tk}", f"付費服務營收 {tn} 貢獻 — OpenAI 有效單價", "$B/年", "#,##0.00", f"=Theory_Rev!{{X}}{T[f'flt{t}']}")
                  for t, (tk, tn) in enumerate(TIERS)]
    fleet_rows += [("IF_RevGWFleet", "付費服務營收合計（層級組合）— OpenAI 有效單價（理想上限）", "$B/年", "#,##0.0", f"=Theory_Rev!{{X}}{T['fl']}")]
    fleet_rows += [(f"IF_RevGWFleetFront_{tk}", f"付費服務營收 {tn} 貢獻 — 前緣單價", "$B/年", "#,##0.00", f"=Theory_Rev!{{X}}{T[f'flft{t}']}")
                   for t, (tk, tn) in enumerate(TIERS)]
    fleet_rows += [("IF_RevGWFleetFront", "付費服務營收合計（層級組合）— 前緣單價（理想上限）", "$B/年", "#,##0.0", f"=Theory_Rev!{{X}}{T['flf']}")]
    for name, lab, unit, fmt, tpl in fleet_rows:
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
        for X in COLS15: put(ws, f"{X}{r}", tpl.replace("{X}", X), fmt=fmt, fill=FILL_KEY)
        names.append((name, f"Interface!$C${r}:$Q${r}")); r += 1
    for name, lab, ref in [("IF_ServeShare", "對外服務占機隊（第 0 層參考；下游覆寫）", "=B4_Serve"), ("IF_FreeShare", "免費占服務（第 0 層參考；下游覆寫）", "=B4_Free")]:
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", "%"); put(ws, f"C{r}", ref, fmt="0%")
        names.append((name, f"Interface!$C${r}")); r += 1
    for n, ref in names: nm(wb, n, ref)
    # replace the old placeholder row
    for row in ws.iter_rows(min_row=17, max_row=start):
        if row[0].value == "每 GW 理論營收":
            row[0].value = "每 GW 理論營收"; ws.cell(row=row[0].row, column=3).value = "見 D 節（IF_RevGW_*、IF_RevGWFleet）"
    return names

def checks_b4(wb, P, F, A, T, U):
    ws = wb["Checks"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, "Block 4 檢查（D＝Hopper 基準、G＝GB200 基準、M＝VR200 基準）", 6)
    put(ws, f"A{r0+1}", "項目", F_BOLD); put(ws, f"B{r0+1}", "本模型", F_BOLD); put(ws, f"C{r0+1}", "外部參照", F_BOLD)
    put(ws, f"D{r0+1}", "單位", F_BOLD); put(ws, f"E{r0+1}", "判讀", F_BOLD); put(ws, f"F{r0+1}", "來源", F_BOLD)
    r = r0 + 2
    # constants (blue) for the OpenAI reconciliation
    put(ws, f"H{r0+1}", "對帳常數", F_BOLD)
    consts = [("OpenAI 2025 營收 $B", 13.07), ("2024 年底 GW", 0.6), ("2025 年底 GW", 1.9), ("2025 Hopper 占機隊", 0.6)]
    cr = {}
    for i, (lab, v) in enumerate(consts):
        put(ws, f"H{r0+2+i}", lab, F_NOTE); put(ws, f"I{r0+2+i}", v, F_IN, fmt="0.00"); cr[i] = f"$I${r0+2+i}"
    ucd = lambda t, key: f"Unit_Cost!D{U[(t, key)]}"
    pf = lambda j: f"INDEX(B4_MktOut,{j},1)"
    rows = [
      ("OpenAI 2025 對帳：機隊付費營收（Hopper／GB200 加權、OpenAI 有效單價）",
       f"=IF(AND(ISNUMBER(Theory_Rev!D{T['fl']}),ISNUMBER(Theory_Rev!G{T['fl']})),{cr[3]}*Theory_Rev!D{T['fl']}+(1-{cr[3]})*Theory_Rev!G{T['fl']},\"SLO 不可達\")", f"={cr[0]}/(({cr[1]}+{cr[2]})/2)", "$B/GW 年",
       "外部參照＝2025 營收 ÷ 平均 GW（GW 口徑未明，D1）；同量級即機隊配置與單價可閉合。2025 實際單價高於 2026 快照", "Cap_In D 節；E010"),
      ("DeepSeek V4-Pro 尖峰輸出價 ÷ 本模型 Hopper Sol decode 成本（基準利用率）",
       f"=IF(ISNUMBER({ucd(2,'cdu')}),{pf(8)}/{ucd(2,'cdu')},\"SLO 不可達\")", "≈1", "x", "≈1：中國廠商定價接近 Hopper 級物理成本；前緣由接近成本者決定（K4 理由 2）", "S52；E011"),
      ("DeepSeek V4-Pro 離峰輸出價 ÷ Hopper Sol decode 成本（100%）",
       f"=IF(ISNUMBER({ucd(2,'cd')}),{pf(8)}*B4_OffPeak/{ucd(2,'cd')},\"SLO 不可達\")", "≈1", "x", "", "S52"),
      ("DeepSeek V4.1-Flash 尖峰輸出價 ÷ Hopper Luna decode 成本（基準利用率）",
       f"=IF(ISNUMBER({ucd(1,'cdu')}),{pf(7)}/{ucd(1,'cdu')},\"SLO 不可達\")", "≈1", "x", "V4.1 架構未必同於 V4-Flash；硬體與中國資本、電力成本不同", "S52"),
      ("單價前緣模型：Luna", f"=Price_Frontier!C{P['frm']}", "—", "", "K2 (i)", "Price_Frontier"),
      ("單價前緣模型：Sol", f"=Price_Frontier!D{P['frm']}", "—", "", "", "Price_Frontier"),
      ("單價前緣模型：Astra", f"=Price_Frontier!E{P['frm']}", "—", "", "Claude Opus 5.5（$4／$20）指數未取得；若 ≥ Astra 門檻，前緣將下移", "Price_Frontier"),
      ("中國合格者最低 ÷ OpenAI（Luna）", f"=Price_Frontier!C{P['cnr']}", ">1", "x", ">1：同能力下中國廠商未比 OpenAI 便宜", "Price_Frontier"),
      ("隱含每 GW 年家族研發計畫數（VR200）", f"=Fleet_1GW!M{F['nprog']}", "1–3", "個", "遠高於 1–3：J8 單一計畫規模偏小或訓練占比偏高", "Fleet_1GW"),
      ("Fleet_1GW 服務 GW 閉合（VR200；應為 0）", f"=Fleet_1GW!M{F['chk']}", "0", "GW", "", "Fleet_1GW"),
      ("自下而上攤提 ÷ Sol 有效混合單價（VR200）", f"=Amortize!M{A['bu1']}/INDEX(B4_EffRef,1,2)", "—", "%", "回本所需溢價占單價的比例", "Amortize"),
      ("K6 縮放倍數：由上而下 ÷ 自下而上年化總額（VR200）", f"=Amortize!M{A['scale']}", "1–3 個計畫時約 1", "x", "與『隱含家族研發計畫數』同源（J8）；(c) 以此倍數放大自下而上攤提", "Amortize"),
      ("K6 (c)：Astra 預設攤提 ÷ Astra 有效混合單價（VR200）", f"=Amortize!M{A['dc2']}/INDEX(B4_EffRef,1,3)", "—", "%", "預設口徑下 Astra 單價中訓練攤提所占比例", "Amortize"),
      ("機隊各層級貢獻合計 − 機隊合計（VR200；應為 0）", f"=Theory_Rev!M{T['flt0']}+Theory_Rev!M{T['flt1']}+Theory_Rev!M{T['flt2']}-Theory_Rev!M{T['fl']}", "0", "$B/年", "", "Theory_Rev B 節"),
    ]
    for i, (a, b, c, d, e, f) in enumerate(rows):
        rr = r + i
        put(ws, f"A{rr}", a, wrap=True); put(ws, f"B{rr}", b, fmt="0.00%" if d == "%" else "#,##0.00", fill=FILL_KEY)
        put(ws, f"C{rr}", c, fmt="#,##0.00"); put(ws, f"D{rr}", d); put(ws, f"E{rr}", e, F_NOTE, wrap=True); put(ws, f"F{rr}", f, F_NOTE)

SOURCES_B4 = [
  ("S50", "OpenAI API 定價頁（GPT-6 Astra／Sol／Luna）", "Standard：Astra $10／$1／$50、Sol $2／$0.2／$10、Luna $0.1／$0.01／$0.5（輸入／快取／輸出）；推理 token 依輸出計費",
   "Verified", "2026-09-25", "developers.openai.com/api/docs/pricing（OpenAI 模型 v0.5 已核對）", "已核對"),
  ("S51", "Anthropic API 定價（二手）", "Fable 5／5.1 $10／$50；Opus 5 $5／$25；Opus 5.5 $4／$20（2026-09-22）；快取寫入 5 分鐘 1.25 倍、1 小時 2 倍；思考 token 依輸出計費",
   "Interested-party（Anthropic 定價；經 dev.to、g2、eesel、orcarouter 轉述）", "2026-07／09", "docs.claude.com 定價頁（未直接讀取）", "多個二手來源一致；Fable 5.1 快取讀取 $0.25 僅單一來源"),
  ("S52", "DeepSeek API 官方定價頁", "V4.1-Flash 尖峰 $0.30／$0.006／$1.20；V4-Pro-0813 尖峰 $1.32／$0.044／$3.96；離峰半價；尖峰＝週一至五 UTC 01–04、06–10",
   "Verified", "2026-10-01", "api-docs.deepseek.com/quick_start/pricing", "已核對原文；第三方頁多為過時價"),
  ("S53", "Z.ai 官方定價頁", "GLM-5.3 $1.4／$0.26／$4.4；GLM-5.3-Flash $0.15／$0.03／$0.5；快取儲存限時免費", "Verified", "2026-10-01",
   "docs.z.ai/guides/overview/pricing", "已核對原文"),
  ("S54", "Moonshot、Alibaba、MiniMax 定價（二手）", "Kimi K3 $3／$0.30／$15；Qwen3.8-Max 國際站 $2／$0.25／$6；MiniMax M3 $0.30／$1.20",
   "Interested-party（廠商定價，經彙整站轉述）", "2026-07／09", "benchlm、morphllm、developersdigest、aireiter 等", "官方頁未直接讀取；Qwen 有 $2.5／$7.5 附五折之衝突記載"),
  ("S55", "Artificial Analysis Intelligence Index v4.3（經報導）", "GPT-6 Astra 53、Fable 5.1 53、Opus 5 51、GPT-5.6 Sol 47、GLM-5.3-Flash 42、Qwen3.8 2.4T 40、DeepSeek V4 Pro 36；一週內三次改版",
   "Verified-measured（獨立評測；改版頻繁，跨版本不可比）", "2026-09", "trendingtopics.eu 報導", "已核對報導原文"),
  ("S56", "Artificial Analysis 發布比較頁 v4.3.2", "GPT-6 Sol 48、GPT-6 Luna 37、DeepSeek V4.1-Flash 39、GLM-5.3 45（max 設定）", "Verified-measured", "2026-09",
   "artificialanalysis.ai/models/releases/comparisons/…", "已核對搜尋摘錄"),
  ("S57", "OpenAI 2025 推論與訓練支出（OpenAI 模型 v0.5 已收錄）", "推論 $8.4B（非付費 $3.9B）、訓練約 $12B；營收 $13.07B；GW 0.6（2024 底）→ 約 1.9（2025 底）",
   "Interested-party（OpenAI 投資人資料，經 The Information、FT、CFO 部落格）", "2026", "openai_token_revenue.json", "待查核（報導）"),
]

def sources_b4(wb):
    ws = wb["Sources"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 1
    for i, row in enumerate(SOURCES_B4):
        for c, v in zip("ABCDEFG", row): put(ws, f"{c}{r+i}", v, wrap=True)

EVID_B4 = [
  ("E010", "2026-10-01", "OpenAI 2025 機隊：服務約 41%、免費占服務約 46%（支出比）", "S57", "Interested-party", "Cap_In D 節", "—（新增）", "41%／46%", "採納", "v5.8", "以支出比代 GW 比，為 Derived"),
  ("E011", "2026-10-01", "DeepSeek 官方現價：V4.1-Flash $0.30／$1.20、V4-Pro $1.32／$3.96（尖峰），離峰半價", "S52", "Verified", "Cap_In F 節；Checks", "第三方頁 $0.14／$0.28", "官方 $0.30／$1.20", "採納", "v5.8", "第三方彙整頁多為過時價；只採官方頁"),
  ("E012", "2026-10-01", "中國廠商 2026 年調漲價格（DeepSeek Flash、GLM 5.1、Kimi K2.5、MiniMax）", "S52、S54", "Interested-party", "Cap_In F 節", "—", "上漲約 30% 至 4 倍", "部分採納", "v5.8", "說明單價非單向下降；年降幅（K9 (b)）不入基準"),
  ("E013", "2026-10-01", "Artificial Analysis 指數一週改版三次，GPT-6 Astra 由第五升至第一", "S55", "Verified-measured", "Cap_In F 節 能力指數", "—", "v4.3／v4.3.2", "部分採納", "v5.8", "全表固定同一版本；跨版本不比較"),
  ("E014", "2026-10-01", "Claude Opus 5.5 $4／$20，Anthropic 自稱達 Fable 5.1 水準", "S51", "Interested-party", "Price_Frontier Astra 前緣", "—", "未納入前緣", "待查", "—", "待獨立評測指數；若 ≥ 53，Astra 前緣下移至 $4／$20"),
  ("E015", "2026-10-01", "Kimi K3 為開放權重（Artificial Analysis 標示）／閉源（另一來源）", "S54", "Interested-party", "Cap_In F 節 開放權重欄", "—", "有爭議", "待查", "—", ""),
]

def evidence_b4(wb):
    ws = wb["DB_Evidence"]
    have = {ws.cell(row=r, column=1).value for r in range(5, ws.max_row + 1)}
    r = max(r for r in range(1, ws.max_row + 1) if ws.cell(row=r, column=1).value is not None) + 1
    n = 0
    for row in EVID_B4:
        if row[0] in have: continue
        for i, v in enumerate(row): put(ws, f"{L(i+1)}{r}", v, F_IN, wrap=i in (2, 5, 10))
        ws.row_dimensions[r].height = 30; r += 1; n += 1
    return n
```

## block5.py

```python
# Block 5 (v5.9): Har_In, Harness, Sens_Har; Interface E; Checks Block 5; Sources S58–S61; DB_Evidence E016–E020
# Decisions (Andy 2026-10-01, "都OK"): L1 harness = per-task parameter set (turns, thinking retention rho, thinking per turn,
# history compaction, cache hit, sub-agents, state retention, vendor flag) replacing the single token multiplier;
# L2 METR-type success rate p = 1/(1+(L/(H50 x horizon multiplier))^beta) with a tier x task override;
# L3 enhanced profiles off in the base (Tech_Registry T12 switch 0) — scenarios only; L4 per-GW theoretical revenue unchanged
# (harness acts on the per-task layer only); L5 cost per success = cost per attempt / p (independent retries, failure detectable);
# L6 non-GPU harness cost excluded (to-do); L7 scenario values only from neutral parties measured under the same conditions.
# New formulas reference key quantities through named ranges (B5_ = Block 5 internal / display; IF_ = downstream).
from common import *
from openpyxl.workbook.defined_name import DefinedName

TIERS = [("Luna", "Luna（低層）"), ("Sol", "Sol（中層）"), ("Astra", "Astra（頂層）")]
TK = "CDEFG"                                   # task columns (Workload C–G)
NA = '"SLO 不可達"'
GENS = [("VR200", "M"), ("GB300", "J")]         # Unit_Cost / Cache_Store base-cost columns (J13: VR200 default, GB300 alongside)
SETS = [("std", "標準 harness"), ("cur", "現行（依 T12 混合）"), ("sel", "選定檔案全採用")]

def nm(wb, n, ref):
    wb.defined_names[n] = DefinedName(n, attr_text=ref)

def taskhead(ws, r, lab="項目"):
    put(ws, f"A{r}", lab, F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for c in TK: put(ws, f"{c}{r}", f"=Workload!{c}4", F_HLINK, wrap=True)
    ws.row_dimensions[r].height = 30

def trow(ws, r, lab, unit, f, fmt, key=False, note=None):
    """one row across the 5 task columns; f may use {c} (column) and {k} (1..5)"""
    put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", unit)
    for k, c in enumerate(TK, start=1):
        v = f(c, k) if callable(f) else f.format(c=c, k=k)
        put(ws, f"{c}{r}", v, fmt=fmt, fill=FILL_KEY if key else None)
    if note: put(ws, f"H{r}", note, F_NOTE, wrap=True)

# ---------------------------------------------------------------- Har_In
PROFILES = {  # rows: key, label, unit, fmt, values for 5 tasks, tag, note
 2: ("供應商原生增強（保留推理狀態＋上下文壓縮）", [
   ("T", "輪數倍數", "x", "0.00", [1, 1, 0.7, 0.7, 0.7], "Assumed", "保留推理狀態後重複探索減少；以 ARC-AGI-3『少用約 49% token』校準（Checks Block 5）；區間見 D 節"),
   ("rho", "思考保留 ρ", "%", "0%", [0, 0, 1, 1, 1], "Verified（機制）", "Provider Adapter 在請求之間保留不透明推理狀態（S58）；單輪任務無作用"),
   ("H", "每輪思考倍數", "x", "0.00", [1, 1, 0.8, 0.8, 0.8], "Assumed", "前輪推理可見，每輪重推減少"),
   ("C", "歷史保留比 c（壓縮後）", "x", "0.00", [1, 1, 0.7, 0.7, 0.7], "Assumed", "壓縮較長的對話（S58）；壓縮比例未揭露"),
   ("DChi", "快取命中變動", "百分點", "0%", [0, 0, 0, 0, 0], "Assumed", "加在 Workload 列 11 之上"),
   ("DM", "子代理數增量", "個", "0", [0, 0, 0, 0, 0], "Assumed", "加在 Workload 列 12 之上"),
   ("Ret", "狀態保留時間", "hr", "0.000", [0.0833333333333333, 0.0833333333333333, 0.67, 0.67, 0.67], "Analogy",
    "ARC-AGI-3 每局約 40 分鐘（S58）；單輪任務沿用 5 分鐘 TTL"),
   ("Hz", "時間範圍倍數（本任務）", "x", "0.00", [1, 1, 1.2, 2, 2], "Assumed",
    "L2：harness 乘在層級 50% 時間範圍上；短程 1.2、長程 2（區間 1–4，D 節）。ARC 結果無法換算為此倍數（Checks）"),
   ("Vendor", "供應商專屬（1＝是）", "旗標", "0", [1, 1, 1, 1, 1], "Verified", "不透明推理狀態只能在原廠 API 使用（轉換成本，[I]）"),
 ]),
 3: ("多代理編排（主代理＋並行子代理）", [
   ("T", "輪數倍數", "x", "0.00", [1, 1, 1, 1, 1], "Assumed", ""),
   ("rho", "思考保留 ρ", "%", "0%", [0, 0, 0, 0, 0], "Assumed", ""),
   ("H", "每輪思考倍數", "x", "0.00", [1, 1, 1, 1, 1], "Assumed", ""),
   ("C", "歷史保留比 c（壓縮後）", "x", "0.00", [1, 1, 1, 1, 1], "Assumed", ""),
   ("DChi", "快取命中變動", "百分點", "0%", [0, 0, 0, 0, 0], "Assumed", ""),
   ("DM", "子代理數增量", "個", "0", [0, 0, 3, 0, 3], "Analogy", "Anthropic 多代理：token 約單代理 4 倍（S25；Interested-party）；多代理研究已含 3 個子代理"),
   ("Ret", "狀態保留時間", "hr", "0.000", [0.0833333333333333] * 5, "Assumed", ""),
   ("Hz", "時間範圍倍數（本任務）", "x", "0.00", [1, 1, 1.2, 1.5, 1.5], "Assumed",
    "Anthropic 自報評測分數 +90.2%（內建知識，待查核；非成功率）只作對照（L7）"),
   ("Vendor", "供應商專屬（1＝是）", "旗標", "0", [0] * 5, "Assumed", "編排框架多為開源或開發者自建"),
 ]),
}

def har_in(wb, TR):
    ws = wb.create_sheet("Har_In")
    title(ws, "Har_In — Block 5 輸入：harness 檔案、成功率參數、敏感度區間、證據（藍字＝輸入；Analogy／Assumed 附區間）",
          "命題：harness 不是新的物理量，而是作用在標準任務上的一組參數變換加上任務成功率。標準檔＝Workload 列 5–14；"
          "選定檔案依 Tech_Registry T12 的開關 × 採用比例（w）混合進 Workload。基準 w＝0（L3）。每 GW 理論營收不受影響（L4）")
    for c, w in zip("ABCDEFGHI", [44, 9, 13, 13, 15, 15, 17, 16, 70]): ws.column_dimensions[c].width = w
    H = {}
    t12 = TR["_rows"][0] + 11          # T12 is the 12th registry entry
    r = 4
    section(ws, r, "A. 選擇與混合", 9); r += 1
    put(ws, f"A{r}", "情境檔案（2＝供應商原生增強；3＝多代理編排）"); put(ws, f"B{r}", "選擇"); put(ws, f"C{r}", 2, fmt="0")
    put(ws, f"H{r}", "Decision", F_NOTE); put(ws, f"I{r}", "只在 w > 0 或 Harness 頁『選定檔案全採用』欄起作用", F_NOTE); H["prof"] = r; r += 1
    put(ws, f"A{r}", "選定檔案名稱"); put(ws, f"C{r}", f"=CHOOSE(C{H['prof']}-1,\"{PROFILES[2][0]}\",\"{PROFILES[3][0]}\")"); H["pname"] = r; r += 1
    put(ws, f"A{r}", "混合權重 w＝T12 開關 × 採用比例"); put(ws, f"B{r}", "x")
    put(ws, f"C{r}", f"=Tech_Registry!O{t12}*Tech_Registry!N{t12}", F_LINK, fmt="0.00", fill=FILL_KEY)
    put(ws, f"I{r}", "w＝0：Workload 與標準檔相同，Block 1–4 與 v5.8 一致", F_NOTE); H["w"] = r; r += 2
    nm(wb, "B5_Profile", f"Har_In!$C${H['prof']}"); nm(wb, "B5_ProfileName", f"Har_In!$C${H['pname']}"); nm(wb, "B5_W", f"Har_In!$C${H['w']}")
    section(ws, r, "B. harness 檔案參數（欄＝Workload 任務；標準檔見 Workload 列 5–14，保留時間＝Cap_In 保留時間、時間範圍倍數＝1）", 9); r += 1
    for p in (2, 3):
        pname, rows = PROFILES[p]
        put(ws, f"A{r}", f"檔案 {p}：{pname}", F_BOLD); r += 1
        taskhead(ws, r, "參數"); put(ws, f"H{r}", "標記", F_BOLD); put(ws, f"I{r}", "說明", F_BOLD); r += 1
        for key, lab, unit, fmt, vals, tag, note in rows:
            put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
            for c, v in zip(TK, vals): put(ws, f"{c}{r}", v, fmt=fmt)
            put(ws, f"H{r}", tag, F_NOTE); put(ws, f"I{r}", note, F_NOTE, wrap=True); H[f"p{p}{key}"] = r; r += 1
        r += 1
    put(ws, f"A{r}", "選定檔案（依 A 節；公式）", F_BOLD); r += 1
    taskhead(ws, r, "參數"); r += 1
    for key, lab, unit, fmt, *_ in PROFILES[2][1]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", unit)
        for c in TK: put(ws, f"{c}{r}", f"=CHOOSE(B5_Profile-1,{c}{H[f'p2{key}']},{c}{H[f'p3{key}']})", fmt=fmt)
        nm(wb, f"B5_Sel{key}", f"Har_In!$C${r}:$G${r}"); H[f"sel{key}"] = r; r += 1
    r += 1
    section(ws, r, "C. 成功率（L2：METR 型 p＝1 ÷（1＋（任務長度 ÷（層級 50% 時間範圍 × harness 倍數））^β））", 9); r += 1
    put(ws, f"A{r}", "項目", F_BOLD); put(ws, f"B{r}", "單位", F_BOLD)
    for c, h in zip("CDE", [tn for _, tn in TIERS]): put(ws, f"{c}{r}", h, F_BOLD)
    put(ws, f"H{r}", "標記", F_BOLD); put(ws, f"I{r}", "說明", F_BOLD); r += 1
    for key, lab, vals, tag, note in [
        ("h50", "50% 時間範圍 基準", (1.5, 8, 16), "Analogy",
         "METR TH1.1：GPT-5.6 Sol 11.3 小時、Claude Mythos Preview 17.4 小時（最高；套件 16 小時以上量不準）（S59）。GPT-6 各層級未發布；Luna 無對應錨點"),
        ("h50lo", "50% 時間範圍 低", (0.5, 4, 11), "Analogy", ""),
        ("h50hi", "50% 時間範圍 高", (4, 12, 40), "Analogy", "Astra 高值參照 Mythos 級以 ECI 推估 18.8–40 小時（第三方，S59）")]:
        put(ws, f"A{r}", lab); put(ws, f"B{r}", "hr")
        for c, v in zip("CDE", vals): put(ws, f"{c}{r}", v, fmt="0.0")
        put(ws, f"H{r}", tag, F_NOTE); put(ws, f"I{r}", note, F_NOTE, wrap=True); H[key] = r; r += 1
    put(ws, f"A{r}", "斜率 β（C＝基準、D＝低、E＝高）"); put(ws, f"B{r}", "x")
    for c, v in zip("CDE", (0.75, 0.65, 1.0)): put(ws, f"{c}{r}", v, fmt="0.00")
    put(ws, f"H{r}", "Derived", F_NOTE)
    put(ws, f"I{r}", "由 METR 50% ÷ 80% 時間範圍比反推：β＝ln4 ÷ ln（比值）；GPT-5、5.2、5.4 約 0.70–0.75，Gemini 3.1 Pro 約 1.0（見 E 節）", F_NOTE, wrap=True)
    H["beta"] = r; r += 1
    nm(wb, "B5_H50", f"Har_In!$C${H['h50']}:$E${H['h50']}"); nm(wb, "B5_H50Lo", f"Har_In!$C${H['h50lo']}:$E${H['h50lo']}")
    nm(wb, "B5_H50Hi", f"Har_In!$C${H['h50hi']}:$E${H['h50hi']}"); nm(wb, "B5_Beta", f"Har_In!$C${H['beta']}")
    taskhead(ws, r, "任務"); r += 1
    put(ws, f"A{r}", "任務長度（人類完成時間）"); put(ws, f"B{r}", "hr")
    for c, v in zip(TK, [0.02, 0.1, 0.5, 2, 8]): put(ws, f"{c}{r}", v, fmt="0.00")
    put(ws, f"H{r}", "Assumed", F_NOTE); put(ws, f"I{r}", "新增假設（L2）；一般聊天約 1 分鐘、長程 coding 約一個工作日", F_NOTE); H["len"] = r
    nm(wb, "B5_TaskLen", f"Har_In!$C${r}:$G${r}"); r += 1
    put(ws, f"A{r}", "任務期程類別"); put(ws, f"B{r}", "")
    for c, v in zip(TK, ["短程", "短程", "短程", "長程", "長程"]): put(ws, f"{c}{r}", v, F_IN)
    put(ws, f"I{r}", "≥ 1 小時為長程；只作標示，倍數在 B 節逐任務輸入", F_NOTE); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        put(ws, f"A{r}", f"成功率覆寫：{tn}（空白＝用公式）"); put(ws, f"B{r}", "%")
        for c in TK: ws[f"{c}{r}"].number_format = "0%"; ws[f"{c}{r}"].font = F_IN
        put(ws, f"I{r}", "有中立方實測時填入（L7）", F_NOTE); H[f"ovr{t}"] = r
        nm(wb, f"B5_SuccOvr_{tk}", f"Har_In!$C${r}:$G${r}"); r += 1
    r += 1
    section(ws, r, "D. 敏感度區間（Sens_Har；作用於選定檔案的 Coding agent（長程））", 9); r += 1
    put(ws, f"A{r}", "參數", F_BOLD); put(ws, f"C{r}", "低", F_BOLD); put(ws, f"D{r}", "高", F_BOLD); put(ws, f"I{r}", "說明", F_BOLD); r += 1
    for key, lab, lo, hi, fmt, note in [
        ("T", "輪數倍數", 0.5, 1.0, "0.00", ""), ("H", "每輪思考倍數", 0.6, 1.0, "0.00", ""),
        ("rho", "思考保留 ρ", 0.5, 1.0, "0%", ""), ("C", "歷史保留比 c", 0.5, 1.0, "0.00", ""),
        ("Hz", "時間範圍倍數（長程）", 1.0, 4.0, "0.00", "1＝harness 不提高成功率"), ("Ret", "狀態保留時間", 0.0833333333333333, 2, "0.000", "hr")]:
        put(ws, f"A{r}", lab); put(ws, f"C{r}", lo, fmt=fmt); put(ws, f"D{r}", hi, fmt=fmt); put(ws, f"H{r}", "Assumed", F_NOTE)
        put(ws, f"I{r}", note, F_NOTE); H[f"rg{key}"] = r; r += 1
    r += 1
    section(ws, r, "E. 證據點（L7：只有中立方同條件測得者可作情境值；其餘只作對照）", 9); r += 1
    for c, h in zip("ABCDEHI", ["證據", "單位", "成功率", "成本 $", "token 比", "標記", "來源／說明"]): put(ws, f"{c}{r}", h, F_BOLD)
    r += 1
    ev = [
      ("arc0", "ARC-AGI-3：GPT-6 Astra 標準 harness（最高推理）", 0.627, 26098, None, "Verified-measured（ARC Prize 自測，經二手轉述）", "S58"),
      ("arc1", "ARC-AGI-3：GPT-6 Astra Provider Adapter（最高推理，同檔）", 0.986, 17332, None, "Verified-measured（同上）", "S58"),
      ("arc2", "ARC-AGI-3：GPT-6 Astra Provider Adapter（高推理）", 0.999, 18817, 0.51, "Verified-measured（同上）",
       "S58；另一來源 $19,302（衝突）；『少用約 49% token』適用範圍不明，本表記為 token 比 0.51"),
      ("opus0", "ARC-AGI-3：Claude Opus 5 標準 harness", 0.302, None, None, "Verified-measured（同上）", "S58"),
      ("opus1", "ARC-AGI-3：Claude Opus 5 + Nvidia 所建 harness", 1.0, None, None, "Interested-party（Nvidia）",
       "S61；交接原記 Strands，報導為 Nvidia，待核；成本未找到"),
      ("ma", "Anthropic 多代理研究系統（相對單代理）", None, None, 3.75, "Interested-party（Anthropic）",
       "S25：token 約聊天 15 倍、單代理 4 倍 → 3.75；內部評測分數 +90.2%（內建知識，待查核；非成功率）")]
    for key, lab, p, cost, tok, tag, src in ev:
        put(ws, f"A{r}", lab, wrap=True)
        if p is not None: put(ws, f"C{r}", p, fmt="0.0%")
        if cost is not None: put(ws, f"D{r}", cost, fmt="#,##0")
        if tok is not None: put(ws, f"E{r}", tok, fmt="0.00")
        put(ws, f"H{r}", tag, F_NOTE, wrap=True); put(ws, f"I{r}", src, F_NOTE, wrap=True); H[key] = r; r += 1
    for c, h in zip("ABCDEFHI", ["METR TH1.1 50% ÷ 80% 時間範圍", "", "50%（hr）", "80%（hr）", "比值", "隱含 β", "標記", "來源"]): put(ws, f"{c}{r}", h, F_BOLD)
    r += 1
    H["metr0"] = r
    for lab, h50, h80 in [("GPT-5", 3.5667, 0.5333), ("GPT-5.2（high）", 6.5667, 0.9167),        # 3h34／32m、6h34／55m
                          ("GPT-5.4（xhigh）", 5.7, 0.9), ("Gemini 3.1 Pro", 5.8333, 1.5)]:           # 5h42／54m、5h50／1h30
        put(ws, f"A{r}", lab); put(ws, f"C{r}", h50, fmt="0.00"); put(ws, f"D{r}", h80, fmt="0.00")
        put(ws, f"E{r}", f"=C{r}/D{r}", fmt="0.0"); put(ws, f"F{r}", f"=LN(4)/LN(E{r})", fmt="0.00")
        put(ws, f"H{r}", "Verified-measured（METR）", F_NOTE); put(ws, f"I{r}", "S59", F_NOTE); r += 1
    H["metr1"] = r - 1
    ws.freeze_panes = "C4"
    return H

# ---------------------------------------------------------------- Harness
def harness(wb, U, S, WL):
    ws = wb.create_sheet("Harness")
    title(ws, "Harness — 每成功任務的 token、成本與營收（世代 × 層級 × 任務 × harness 檔案；L1–L5）",
          "每次嘗試成本＝新鮮 × prefill 成本＋快取 ×（載入＋儲存 × 保留時間 ÷ Cap_In 保留時間）＋ decode × decode 成本（經濟、基準成本、基準利用率）；"
          "每成功任務＝每次嘗試 ÷ 成功率 p（L5：重試獨立、失敗可偵測）。harness 不改變每 GW 產出與理論營收（L4）。非 GPU 成本未計（L6）")
    for c, w in zip("ABCDEFGH", [52, 10, 14, 14, 16, 16, 18, 60]): ws.column_dimensions[c].width = w
    R = {}
    r = 4
    taskhead(ws, r, "項目"); r += 1
    W = lambda key: f"Workload!{{c}}{WL[key]}"
    section(ws, r, "A. 每次嘗試的 token（標準與選定檔案全採用由本頁計算；現行＝Workload 有效參數）", 8); r += 1
    for sk, sn in (("std", "標準 harness"), ("sel", "選定檔案全採用")):
        put(ws, f"A{r}", sn, F_BOLD); r += 1
        if sk == "std":
            pT, pH, pRho, pChi, pM, pC = W("T"), W("h"), W("rho"), W("chi"), W("m"), W("c")
        else:
            pT = W("T") + "*INDEX(B5_SelT,1,{k})"; pH = W("h") + "*INDEX(B5_SelH,1,{k})"; pRho = "INDEX(B5_SelRho,1,{k})"
            pChi = "MIN(1,MAX(0," + W("chi") + "+INDEX(B5_SelDChi,1,{k})))"; pM = W("m") + "+INDEX(B5_SelDM,1,{k})"; pC = "INDEX(B5_SelC,1,{k})"
        base = r
        rows = [("T", "輪數 T", "輪", "=" + pT, "#,##0.0"), ("h", "每輪思考 h", "tok", "=" + pH, "#,##0"),
                ("rho", "思考保留 ρ", "%", "=" + pRho, "0%"), ("chi", "快取命中 χ", "%", "=" + pChi, "0%"),
                ("m", "子代理數 m", "個", "=" + pM, "0.0"), ("cc", "歷史保留比 c", "x", "=" + pC, "0.00")]
        idx = {}
        for i, (key, lab, unit, f, fmt) in enumerate(rows):
            trow(ws, r, lab, unit, f, fmt); idx[key] = r; r += 1
        g = lambda key: f"{{c}}{idx[key]}"
        inc = r; trow(ws, r, "每輪上下文增量 u＋o＋ρh", "tok", f"={W('u')}+{W('o')}+{g('rho')}*{g('h')}", "#,##0"); r += 1
        hist = f"{g('cc')}*{{c}}{inc}*{g('T')}*({g('T')}-1)/2"
        inp = r; trow(ws, r, "單代理輸入總量", "tok", f"={g('T')}*({W('S')}+{W('u')})+{hist}", "#,##0"); r += 1
        cac = r; trow(ws, r, "其中可快取", "tok", f"={g('chi')}*({g('T')}*{W('S')}+{hist})", "#,##0"); r += 1
        dec = r; trow(ws, r, "單代理 decode", "tok", f"={g('T')}*({g('h')}+{W('o')})", "#,##0"); r += 1
        mul = r; trow(ws, r, "系統倍數（1＋m）× 殘差倍數", "x", f"=(1+{g('m')})*{W('res')}", "0.00"); r += 1
        R[f"{sk}_fp"] = r; trow(ws, r, "任務新鮮 prefill", "tok", f"=({{c}}{inp}-{{c}}{cac})*{{c}}{mul}", "#,##0"); r += 1
        R[f"{sk}_cp"] = r; trow(ws, r, "任務快取 prefill", "tok", f"={{c}}{cac}*{{c}}{mul}", "#,##0"); r += 1
        R[f"{sk}_dp"] = r; trow(ws, r, "任務 decode", "tok", f"={{c}}{dec}*{{c}}{mul}", "#,##0"); r += 1
        R[f"{sk}_tot"] = r; trow(ws, r, "任務總 token", "tok", f"={{c}}{R[sk+'_fp']}+{{c}}{R[sk+'_cp']}+{{c}}{R[sk+'_dp']}", "#,##0", key=True); r += 1
        r += 1
    put(ws, f"A{r}", "現行（Workload）", F_BOLD); r += 1
    for key, wkey, lab in (("fp", "fp", "任務新鮮 prefill"), ("cp", "cp", "任務快取 prefill"), ("dp", "dp", "任務 decode"), ("tot", "tot", "任務總 token")):
        R[f"cur_{key}"] = r; trow(ws, r, lab, "tok", f"=Workload!{{c}}{WL[wkey]}", "#,##0", key=(key == "tot")); r += 1
    R["tokratio"] = r
    trow(ws, r, "選定檔案 ÷ 標準：任務總 token", "x", f"={{c}}{R['sel_tot']}/{{c}}{R['std_tot']}", "0.00", key=True,
         note="ARC-AGI-3 對照：Provider Adapter 少用約 49% token（0.51；適用範圍不明）"); r += 2
    section(ws, r, "B. 狀態保留時間與時間範圍倍數", 8); r += 1
    R["std_ret"] = r; trow(ws, r, "保留時間：標準", "hr", "=B4_Retain", "0.000"); r += 1
    R["cur_ret"] = r; trow(ws, r, "保留時間：現行", "hr", "=B4_Retain+B5_W*(INDEX(B5_SelRet,1,{k})-B4_Retain)", "0.000"); r += 1
    R["sel_ret"] = r; trow(ws, r, "保留時間：選定檔案", "hr", "=INDEX(B5_SelRet,1,{k})", "0.000"); r += 1
    R["std_hz"] = r; trow(ws, r, "時間範圍倍數：標準", "x", "=1", "0.00"); r += 1
    R["cur_hz"] = r; trow(ws, r, "時間範圍倍數：現行", "x", "=1+B5_W*(INDEX(B5_SelHz,1,{k})-1)", "0.00"); r += 1
    R["sel_hz"] = r; trow(ws, r, "時間範圍倍數：選定檔案", "x", "=INDEX(B5_SelHz,1,{k})", "0.00"); r += 2
    section(ws, r, "C. 成功率 p（覆寫欄有值時用覆寫）", 8); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        for sk, sn in SETS:
            R[f"p_{sk}{t}"] = r
            trow(ws, r, f"{tn}｜{sn}", "%",
                 f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{tk},1,{{k}})),INDEX(B5_SuccOvr_{tk},1,{{k}}),"
                 f"1/(1+(INDEX(B5_TaskLen,1,{{k}})/(INDEX(B5_H50,1,{t+1})*{{c}}{R[sk+'_hz']}))^B5_Beta))", "0.0%", key=(sk == "cur")); r += 1
    r += 1
    section(ws, r, "D. 每次嘗試成本（$／任務；經濟、基準成本、基準利用率；含快取儲存）", 8); r += 1
    for gname, col in GENS:
        for t, (tk, tn) in enumerate(TIERS):
            cf, cc, cd = U[(t + 1, "cfu")], U[(t + 1, "ccu")], U[(t + 1, "cdu")]
            for sk, sn in SETS:
                R[f"c_{gname}{t}{sk}"] = r
                trow(ws, r, f"{gname} × {tn}｜{sn}", "$",
                     f"=IF(ISNUMBER(Unit_Cost!{col}{cd}),({{c}}{R[sk+'_fp']}*Unit_Cost!{col}{cf}+{{c}}{R[sk+'_cp']}*(Unit_Cost!{col}{cc}"
                     f"+Cache_Store!{col}{S[tk]}*{{c}}{R[sk+'_ret']}/B4_Retain)+{{c}}{R[sk+'_dp']}*Unit_Cost!{col}{cd})/1E6,{NA})", "$#,##0.0000"); r += 1
    r += 1
    section(ws, r, "E. 每成功任務成本（＝每次嘗試 ÷ p）與 token", 8); r += 1
    for gname, col in GENS:
        for t, (tk, tn) in enumerate(TIERS):
            for sk, sn in SETS:
                cref = f"{{c}}{R[f'c_{gname}{t}{sk}']}"; pref = f"{{c}}{R[f'p_{sk}{t}']}"
                R[f"cs_{gname}{t}{sk}"] = r
                trow(ws, r, f"{gname} × {tn}｜{sn}", "$", f"=IF(AND(ISNUMBER({cref}),{pref}>0),{cref}/{pref},{NA})", "$#,##0.0000",
                     key=(sk == "cur" and gname == "VR200")); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        for sk, sn in SETS:
            R[f"ts_{t}{sk}"] = r
            trow(ws, r, f"每成功任務 token：{tn}｜{sn}", "tok", f"=IF({{c}}{R[f'p_{sk}{t}']}>0,{{c}}{R[sk+'_tot']}/{{c}}{R[f'p_{sk}{t}']},0)", "#,##0"); r += 1
    r += 1
    section(ws, r, "F. 每任務營收（OpenAI 有效單價；營收以每次嘗試計費，每成功任務＝÷ p）", 8); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        for sk, sn in SETS:
            R[f"rv_{t}{sk}"] = r
            trow(ws, r, f"每次嘗試營收：{tn}｜{sn}", "$",
                 f"=({{c}}{R[sk+'_fp']}*INDEX(B4_EffIn,1,{t+1})+{{c}}{R[sk+'_cp']}*INDEX(B4_EffCache,1,{t+1})+{{c}}{R[sk+'_dp']}*INDEX(B4_EffOut,1,{t+1}))/1E6",
                 "$#,##0.0000"); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        for sk, sn in SETS:
            R[f"rs_{t}{sk}"] = r
            trow(ws, r, f"每成功任務營收：{tn}｜{sn}", "$", f"=IF({{c}}{R[f'p_{sk}{t}']}>0,{{c}}{R[f'rv_{t}{sk}']}/{{c}}{R[f'p_{sk}{t}']},0)", "$#,##0.0000"); r += 1
    r += 1
    section(ws, r, "G. R＝每成功任務成本：選定檔案全採用 ÷ 標準（<1＝harness 降低每成功任務成本）", 8); r += 1
    for gname, col in GENS:
        for t, (tk, tn) in enumerate(TIERS):
            a, b = f"{{c}}{R[f'cs_{gname}{t}sel']}", f"{{c}}{R[f'cs_{gname}{t}std']}"
            R[f"R_{gname}{t}"] = r
            trow(ws, r, f"{gname} × {tn}", "x", f"=IF(AND(ISNUMBER({a}),ISNUMBER({b})),{a}/{b},{NA})", "0.00", key=(gname == "VR200")); r += 1
    for t, (tk, tn) in enumerate(TIERS):
        trow(ws, r, f"成功率比（選定 ÷ 標準）：{tn}", "x", f"={{c}}{R[f'p_sel{t}']}/{{c}}{R[f'p_std{t}']}", "0.00"); R[f"pr{t}"] = r; r += 1
    r += 1
    section(ws, r, "H. 成功任務成本前緣（各世代：3 層級 × {標準、選定檔案} 中每成功任務成本最低者；層級替代）", 8); r += 1
    for gname, col in GENS:
        cells = [(f"{TIERS[t][0]}｜標準", R[f"cs_{gname}{t}std"]) for t in range(3)] + [(f"{TIERS[t][0]}｜選定", R[f"cs_{gname}{t}sel"]) for t in range(3)]
        R[f"fr_{gname}"] = r
        trow(ws, r, f"{gname}：最低每成功任務成本", "$", lambda c, k, cells=cells: "=MIN(" + ",".join(f"{c}{rr}" for _, rr in cells) + ")", "$#,##0.0000", key=True); r += 1
        def lab(c, k, cells=cells, fr=r - 1):
            f = '"—"'
            for name, rr in reversed(cells):
                f = f'IF({c}{rr}={c}{fr},"{name}",{f})'
            return "=" + f
        R[f"frl_{gname}"] = r; trow(ws, r, f"{gname}：前緣組合（層級｜檔案）", "", lab, None); r += 1
    put(ws, f"A{r}", "註：標準與現行在 w＝0 時相同。前緣只比較成本，不含延遲；選定檔案『供應商專屬』時，前緣組合綁定該供應商 API（Har_In 旗標）", F_NOTE)
    ws.freeze_panes = "C5"
    for key, n in [("cur_tot", "B5_TaskTok"), ("sel_tot", "B5_TaskTokSel"), ("std_tot", "B5_TaskTokStd")]:
        nm(wb, n, f"Harness!$C${R[key]}:$G${R[key]}")
    return R

# ---------------------------------------------------------------- Sens_Har
def sens_har(wb, U, S, WL, H, R):
    ws = wb.create_sheet("Sens_Har")
    title(ws, "Sens_Har — R 與每成功任務成本的敏感度（VR200、基準成本；Coding agent（長程）；選定檔案全採用 vs 標準）",
          "每欄只改一個參數（區間取 Har_In D、C 節），其餘同基準欄。R＝（選定每次嘗試成本 ÷ p 選定）÷（標準每次嘗試成本 ÷ p 標準）")
    ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 8
    k = 5; c0 = "G"                                    # Coding agent = task 5 (Workload column G)
    var = [("基準", None, None)]
    for key, lab in [("T", "輪數倍數"), ("H", "每輪思考倍數"), ("rho", "思考保留 ρ"), ("C", "歷史保留比"), ("Hz", "時間範圍倍數"), ("Ret", "保留時間")]:
        var += [(f"{lab} 低", key, f"Har_In!$C${H['rg' + key]}"), (f"{lab} 高", key, f"Har_In!$D${H['rg' + key]}")]
    var += [("β 低", "beta", "Har_In!$D$" + str(H["beta"])), ("β 高", "beta", "Har_In!$E$" + str(H["beta"])),
            ("50% 時間範圍 低", "h50", "lo"), ("50% 時間範圍 高", "h50", "hi")]
    cols = [L(3 + i) for i in range(len(var))]
    for X in cols: ws.column_dimensions[X].width = 11
    put(ws, "A4", "情境", F_BOLD)
    for X, (lab, _, _) in zip(cols, var): put(ws, f"{X}4", lab, F_BOLD, wrap=True)
    ws.row_dimensions[4].height = 42
    W = lambda key: f"Workload!${c0}${WL[key]}"
    basev = {"T": f"INDEX(B5_SelT,1,{k})", "H": f"INDEX(B5_SelH,1,{k})", "rho": f"INDEX(B5_SelRho,1,{k})", "C": f"INDEX(B5_SelC,1,{k})",
             "Hz": f"INDEX(B5_SelHz,1,{k})", "Ret": f"INDEX(B5_SelRet,1,{k})", "beta": "B5_Beta"}
    rows = {}
    r = 5
    for key, lab, fmt in [("T", "輪數倍數", "0.00"), ("H", "每輪思考倍數", "0.00"), ("rho", "思考保留 ρ", "0%"), ("C", "歷史保留比 c", "0.00"),
                          ("Hz", "時間範圍倍數", "0.00"), ("Ret", "保留時間（hr）", "0.000"), ("beta", "β", "0.00")]:
        put(ws, f"A{r}", lab)
        for X, (_, vk, ref) in zip(cols, var):
            put(ws, f"{X}{r}", f"={ref}" if vk == key else f"={basev[key]}", fmt=fmt)
        rows[key] = r; r += 1
    for t, (tk, tn) in enumerate(TIERS):
        put(ws, f"A{r}", f"50% 時間範圍：{tn}（hr）")
        for X, (_, vk, ref) in zip(cols, var):
            nmh = {"lo": "B5_H50Lo", "hi": "B5_H50Hi"}.get(ref, "B5_H50") if vk == "h50" else "B5_H50"
            put(ws, f"{X}{r}", f"=INDEX({nmh},1,{t+1})", fmt="0.0")
        rows[f"h{t}"] = r; r += 1
    r += 1
    def drow(key, lab, f, fmt, key_fill=False):
        nonlocal r
        put(ws, f"A{r}", lab)
        for X in cols: put(ws, f"{X}{r}", f.replace("{X}", X), fmt=fmt, fill=FILL_KEY if key_fill else None)
        rows[key] = r; r += 1
    g = lambda key: f"{{X}}{rows[key]}"
    drow("Tn", "選定：輪數", f"={W('T')}*{g('T')}", "0.0")
    drow("hn", "選定：每輪思考", f"={W('h')}*{g('H')}", "#,##0")
    drow("inc", "選定：每輪增量", f"={W('u')}+{W('o')}+{g('rho')}*{g('hn')}", "#,##0")
    hist = f"{g('C')}*{g('inc')}*{g('Tn')}*({g('Tn')}-1)/2"
    chi = f"MIN(1,MAX(0,{W('chi')}+INDEX(B5_SelDChi,1,{k})))"
    mul = f"(1+{W('m')}+INDEX(B5_SelDM,1,{k}))*{W('res')}"
    drow("inp", "選定：輸入總量（單代理）", f"={g('Tn')}*({W('S')}+{W('u')})+{hist}", "#,##0")
    drow("cac", "選定：可快取", f"={chi}*({g('Tn')}*{W('S')}+{hist})", "#,##0")
    drow("fp", "選定：任務新鮮 prefill", f"=({g('inp')}-{g('cac')})*{mul}", "#,##0")
    drow("cp", "選定：任務快取 prefill", f"={g('cac')}*{mul}", "#,##0")
    drow("dp", "選定：任務 decode", f"={g('Tn')}*({g('hn')}+{W('o')})*{mul}", "#,##0")
    drow("tr", "token 比（選定 ÷ 標準）", f"=({g('fp')}+{g('cp')}+{g('dp')})/Harness!${c0}${R['std_tot']}", "0.00")
    r += 1
    col = "M"
    for t, (tk, tn) in enumerate(TIERS):
        cf, cc, cd = U[(t + 1, "cfu")], U[(t + 1, "ccu")], U[(t + 1, "cdu")]
        drow(f"cs{t}", f"{tn}：選定每次嘗試成本 $",
             f"=IF(ISNUMBER(Unit_Cost!${col}${cd}),({g('fp')}*Unit_Cost!${col}${cf}+{g('cp')}*(Unit_Cost!${col}${cc}+Cache_Store!${col}${S[tk]}*{g('Ret')}/B4_Retain)"
             f"+{g('dp')}*Unit_Cost!${col}${cd})/1E6,{NA})", "$#,##0.0000")
        L_ = f"INDEX(B5_TaskLen,1,{k})"
        drow(f"p0{t}", f"{tn}：p 標準", f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{tk},1,{k})),INDEX(B5_SuccOvr_{tk},1,{k}),1/(1+({L_}/{g('h'+str(t))})^{g('beta')}))", "0.0%")
        drow(f"p1{t}", f"{tn}：p 選定", f"=IF(ISNUMBER(INDEX(B5_SuccOvr_{tk},1,{k})),INDEX(B5_SuccOvr_{tk},1,{k}),1/(1+({L_}/({g('h'+str(t))}*{g('Hz')}))^{g('beta')}))", "0.0%")
        std = f"Harness!${c0}${R[f'c_VR200{t}std']}"
        drow(f"R{t}", f"{tn}：R（每成功任務成本 選定 ÷ 標準）",
             f"=IF(AND(ISNUMBER({g('cs'+str(t))}),ISNUMBER({std})),({g('cs'+str(t))}/{g('p1'+str(t))})/({std}/{g('p0'+str(t))}),{NA})", "0.00", key_fill=(t > 0))
    put(ws, f"A{r+1}", "讀法：R 跨過 1 的欄＝harness 由省錢轉為加成本。Luna 在長程任務 p 很低，R 主要由成功率主導", F_NOTE)
    return rows

# ---------------------------------------------------------------- Interface E, Checks, Sources, Evidence
def interface_b5(wb, start, R):
    ws = wb["Interface"]; r = start; names = []
    section(ws, r, "E. Block 5 產出（每任務層；欄 C–G＝Workload 任務；現行＝依 Tech_Registry T12 混合，基準等於標準 harness；VR200／GB300 基準成本）", 17); r += 1
    put(ws, f"A{r}", "任務　[IF_HdrTask]", F_BOLD)
    for c in TK: put(ws, f"{c}{r}", f"=Workload!{c}4", F_HLINK, wrap=True)
    names.append(("IF_HdrTask", f"Interface!$C${r}:$G${r}")); r += 1
    for name, lab, unit, ref, fmt in [("IF_HarW", "harness 混合權重 w（T12 開關 × 採用比例）", "x", "=B5_W", "0.00"),
                                      ("IF_HarProfile", "選定 harness 檔案（情境）", "", "=B5_ProfileName", None)]:
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit); put(ws, f"C{r}", ref, fmt=fmt)
        names.append((name, f"Interface!$C${r}")); r += 1
    def row5(name, lab, unit, tpl, fmt, key=False):
        nonlocal r
        put(ws, f"A{r}", f"{lab}　[{name}]"); put(ws, f"B{r}", unit)
        for k, c in enumerate(TK, start=1): put(ws, f"{c}{r}", tpl.format(c=c, k=k), fmt=fmt, fill=FILL_KEY if key else None)
        names.append((name, f"Interface!$C${r}:$G${r}")); r += 1
    row5("IF_TaskLen", "任務長度（人類完成時間）", "hr", "=INDEX(B5_TaskLen,1,{k})", "0.00")
    row5("IF_TaskTokFresh", "每次嘗試 新鮮輸入 token（現行）", "tok", f"=Harness!{{c}}{R['cur_fp']}", "#,##0")
    row5("IF_TaskTokCached", "每次嘗試 快取輸入 token（現行）", "tok", f"=Harness!{{c}}{R['cur_cp']}", "#,##0")
    row5("IF_TaskTokDec", "每次嘗試 decode token（思考＋可見；現行）", "tok", f"=Harness!{{c}}{R['cur_dp']}", "#,##0")
    row5("IF_TaskTokSel", "每次嘗試 總 token（選定檔案全採用；情境）", "tok", f"=Harness!{{c}}{R['sel_tot']}", "#,##0")
    row5("IF_HarTokRatio", "總 token：選定檔案 ÷ 標準", "x", f"=Harness!{{c}}{R['tokratio']}", "0.00")
    for t, (tk, tn) in enumerate(TIERS):
        put(ws, f"A{r}", tn, F_BOLD); r += 1
        row5(f"IF_TaskSucc_{tk}", "成功率 p（現行）", "%", f"=Harness!{{c}}{R[f'p_cur{t}']}", "0.0%")
        row5(f"IF_TaskSuccSel_{tk}", "成功率 p（選定檔案全採用；情境）", "%", f"=Harness!{{c}}{R[f'p_sel{t}']}", "0.0%")
        row5(f"IF_CostSuccVR_{tk}", "每成功任務成本 — VR200（現行；經濟、基準成本、基準利用率）", "$", f"=Harness!{{c}}{R[f'cs_VR200{t}cur']}", "$#,##0.0000", key=True)
        row5(f"IF_CostSuccGB_{tk}", "每成功任務成本 — GB300（現行）", "$", f"=Harness!{{c}}{R[f'cs_GB300{t}cur']}", "$#,##0.0000")
        row5(f"IF_RevSucc_{tk}", "每成功任務營收 — OpenAI 有效單價（現行）", "$", f"=Harness!{{c}}{R[f'rs_{t}cur']}", "$#,##0.0000")
        row5(f"IF_HarR_{tk}", "R＝每成功任務成本 選定 ÷ 標準（VR200）", "x", f"=Harness!{{c}}{R[f'R_VR200{t}']}", "0.00")
    for n, ref in names: nm(wb, n, ref)
    return names

def checks_b5(wb, R, H, SH):
    ws = wb["Checks"]
    r0 = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r0, "Block 5 檢查（Coding agent（長程）＝Harness／Workload 欄 G）", 6)
    for c, h in zip("ABCDEF", ["項目", "本模型", "外部參照", "單位", "判讀", "來源"]): put(ws, f"{c}{r0+1}", h, F_BOLD)
    a0, a1, a2 = H["arc0"], H["arc1"], H["arc2"]
    rows = [
      ("混合權重 w（基準應為 0：L3）", "=B5_W", "0", "x", "w＝0 時 Workload＝標準 harness，Block 1–4 與 v5.8 逐格一致", "Tech_Registry T12"),
      ("Workload 總 token − Harness 標準總 token（5 任務絕對差合計）", "=" + "+".join(f"ABS(Workload!{c}35-Harness!{c}{R['std_tot']})" for c in TK), "0（w＝0 時）", "tok",
       "w＞0 時應 > 0", "Workload、Harness"),
      ("ARC 重現（token）：選定檔案 ÷ 標準 總 token", f"=Harness!G{R['tokratio']}", f"=Har_In!E{a2}", "x",
       "外部參照＝『少用約 49% token』；只看方向（ARC 為互動遊戲，不是 Workload 任務）", "S58"),
      ("ARC 重現（R）：Astra × Coding agent（VR200）", f"=Harness!G{R['R_VR2002']}", f"=(Har_In!D{a1}/Har_In!C{a1})/(Har_In!D{a0}/Har_In!C{a0})", "x",
       "外部參照＝同為最高推理的成本比 ÷ 成功率比（≈0.42）；方向一致即可", "S58"),
      ("ARC 成功率換算為時間範圍倍數（β 基準）", f"=((1/Har_In!C{a0}-1)/(1/Har_In!C{a1}-1))^(1/B5_Beta)", "1–4（Har_In 區間）", "x",
       "遠大於區間：ARC 的提升無法用 METR 型曲線表達，故 ARC 只作方向檢查、不校準時間範圍倍數", "S58、S59"),
      ("METR 隱含 β（四個模型平均）", f"=AVERAGE(Har_In!F{H['metr0']}:F{H['metr1']})", "=B5_Beta", "x", "外部參照欄＝本模型採用值", "S59"),
      ("Astra 標準 harness：Coding agent 成功率", f"=Harness!G{R['p_std2']}", "—", "%", "任務長度 8 小時 ÷ 時間範圍 16 小時", "Har_In C 節"),
      ("每成功任務：Coding agent 前緣組合（VR200）", f"=Harness!G{R['frl_VR200']}", "—", "", "層級替代：選定檔案全採用時較低層級能否勝出", "Harness H 節"),
      ("Sens_Har：Astra R 最小～最大（VR200、Coding agent）", f"=MIN(Sens_Har!C{SH['R2']}:Z{SH['R2']})", f"=MAX(Sens_Har!C{SH['R2']}:Z{SH['R2']})", "x",
       "最大值 > 1 即 harness 在區間內可能提高每成功任務成本", "Sens_Har"),
    ]
    for i, (a, b, c, d, e, f) in enumerate(rows):
        rr = r0 + 2 + i
        put(ws, f"A{rr}", a, wrap=True); put(ws, f"B{rr}", b, fmt="0.0%" if d == "%" else "#,##0.00", fill=FILL_KEY)
        put(ws, f"C{rr}", c, fmt="#,##0.00"); put(ws, f"D{rr}", d); put(ws, f"E{rr}", e, F_NOTE, wrap=True); put(ws, f"F{rr}", f, F_NOTE)

SOURCES_B5 = [
  ("S58", "ARC-AGI-3 harness 對照（ARC Prize 自測，經報導）",
   "GPT-6 Astra 標準 harness 最高推理 62.7%、$26,098；OpenAI Provider Adapter 高推理 99.9%、$18,817（另載 $19,302）；同為最高推理 98.6%、$17,332；耗時約快 3.66 倍；少用約 49% token（範圍不明）；adapter 保留不透明推理狀態並壓縮長對話，使用公開 API 功能",
   "Verified-measured（ARC Prize）／Interested-party（OpenAI 發布 99.9%）", "2026-09", "thenextweb、ibl.ai、ecosistemastartup 等轉述", "ARC Prize 原頁待核；金額衝突待核"),
  ("S59", "METR 時間範圍（Time Horizon 1.1）",
   "GPT-5 3h34／32m；GPT-5.2（high）6h34／55m；GPT-5.4（xhigh）5h42／54m；Gemini 3.1 Pro 5h50／1h30；GPT-5.6 Sol 11.3h；Claude Mythos Preview 17.4h（50%／80%）；套件 16 小時以上量不準",
   "Verified-measured（METR，獨立評測）", "2026-01～09", "Wikipedia METR 條目、futuresearch 轉述 metr.org", "metr.org 原頁待核；GPT-6 各層級未發布"),
  ("S60", "Artificial Analysis 每任務成本", "GPT-6 Astra 每任務約 $4.72、Claude Fable 5.1 約 $9.18（其 agent 評測）", "Verified-measured（獨立評測）", "2026-09",
   "sentisense 轉述", "只作對照：AA 的任務組合與 Workload 不同"),
  ("S61", "Claude Opus 5 + Nvidia 所建 harness 通關 ARC-AGI-3", "Opus 5 標準 30.2% → 全部關卡通關", "Interested-party（Nvidia）", "2026-09", "thenextweb 轉述", "交接原記 Strands；歸屬與成本待核"),
]

def sources_b5(wb):
    ws = wb["Sources"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 1
    for i, row in enumerate(SOURCES_B5):
        for c, v in zip("ABCDEFG", row): put(ws, f"{c}{r+i}", v, wrap=True)

EVID_B5 = [
  ("E016", "2026-10-01", "ARC-AGI-3：Provider Adapter 同檔成本 0.66 倍、成功率 1.57 倍 → 每成功任務成本約 0.42 倍", "S58", "Verified-measured／Interested-party",
   "Har_In B 節檔案 2；Checks Block 5", "—（新增）", "R≈0.42", "部分採納", "v5.9", "只作方向檢查；ARC 不是 Workload 任務"),
  ("E017", "2026-10-01", "Anthropic 多代理：token 約單代理 4 倍、評測分數 +90.2%", "S25", "Interested-party", "Har_In B 節檔案 3", "—", "R≈2.0", "部分採納", "v5.9",
   "90.2% 非成功率且為內建知識，待查核；只作對照（L7）"),
  ("E018", "2026-10-01", "METR TH1.1：GPT-5.6 Sol 50% 時間範圍 11.3 小時；Mythos Preview 17.4 小時", "S59", "Verified-measured", "Har_In C 節 時間範圍", "—", "Luna 1.5／Sol 8／Astra 16 hr", "部分採納", "v5.9",
   "GPT-6 各層級未發布，以相近模型類比"),
  ("E019", "2026-10-01", "METR 50% ÷ 80% 時間範圍比 3.9–7.2 → β 約 0.70–1.0", "S59", "Verified-measured", "Har_In C 節 β", "—", "0.75（0.65–1.0）", "採納", "v5.9", ""),
  ("E020", "2026-10-01", "Opus 5 搭配 harness 由 30.2% 至全部通關（歸屬 Nvidia 或 Strands 不一）", "S61", "Interested-party", "Har_In E 節", "Strands（交接）", "Nvidia（報導）", "待查", "—", "成本未找到"),
]

def evidence_b5(wb):
    ws = wb["DB_Evidence"]
    have = {ws.cell(row=r, column=1).value for r in range(5, ws.max_row + 1)}
    r = max(r for r in range(1, ws.max_row + 1) if ws.cell(row=r, column=1).value is not None) + 1
    n = 0
    for row in EVID_B5:
        if row[0] in have: continue
        for i, v in enumerate(row): put(ws, f"{L(i+1)}{r}", v, F_IN, wrap=i in (2, 5, 10))
        ws.row_dimensions[r].height = 30; r += 1; n += 1
    return n
```

## preserve.py

```python
# v5.7: Excel-first input preservation.
# Before Block 2/3 sheets are deleted and rebuilt, snapshot every input cell (blue font, constant value);
# after rebuild, write the Excel value back wherever the same sheet / column-A label / column still holds an input.
# Code defaults therefore apply only to NEW input rows; existing inputs are owned by the Excel file.
BLUE = "FF0000FF"
REBUILT = ["Spec_Rack", "Arch", "Serving", "Workload", "Calib", "Energy", "NonNV", "Tech_Registry", "Perf",
           "Sens_Perf", "Unit_Cost", "Train_In", "Perf_Batch", "Training", "Sens_Train",
           "Cap_In", "Capability", "Price_Frontier", "Cache_Store", "Fleet_1GW", "Amortize", "Theory_Rev", "Sens_Rev",
           "Har_In", "Harness", "Sens_Har"]

def _is_input(cell):
    v = cell.value
    if v is None or (isinstance(v, str) and v.startswith("=")):
        return False
    c = cell.font.color if cell.font else None
    return c is not None and c.type == "rgb" and c.rgb == BLUE

def _keys(ws, min_row):
    seen = {}
    for r in range(min_row, ws.max_row + 1):
        lab = ws.cell(row=r, column=1).value
        if lab is None or (isinstance(lab, str) and lab.startswith("=")):
            continue
        k = (str(lab), seen.get(str(lab), 0)); seen[str(lab)] = k[1] + 1
        yield r, k

def snapshot(wb):
    snap = {}
    for s in REBUILT:
        if s not in wb.sheetnames: continue
        ws = wb[s]; r0 = 21 if s == "Spec_Rack" else 1
        for r, k in _keys(ws, r0):
            for c in range(2, ws.max_column + 1):
                cell = ws.cell(row=r, column=c)
                if _is_input(cell):
                    snap[(s, k, c)] = cell.value
    return snap

def restore(wb, snap, log_path=None):
    matched = changed = 0; lines = []
    present = set()
    for s in REBUILT:
        ws = wb[s]; r0 = 21 if s == "Spec_Rack" else 1
        for r, k in _keys(ws, r0):
            for c in range(2, ws.max_column + 1):
                key = (s, k, c)
                if key not in snap: continue
                cell = ws.cell(row=r, column=c)
                if not _is_input(cell): continue
                present.add(key); matched += 1
                if cell.value != snap[key]:
                    lines.append(f"{s}!{cell.coordinate} [{k[0]}]: code default {cell.value!r} -> Excel {snap[key]!r}")
                    cell.value = snap[key]; changed += 1
    dropped = [f"{s} [{k[0]}] col {c}: {v!r}" for (s, k, c), v in snap.items() if (s, k, c) not in present]
    report = [f"inputs in base: {len(snap)}; restored (matched): {matched}; Excel value kept over code default: {changed}; "
              f"base inputs with no matching input cell in rebuild: {len(dropped)}"] + lines + ["-- unmatched --"] + dropped
    if log_path: open(log_path, "w").write("\n".join(report))
    return matched, changed, dropped
```

## build.py

```python
# Usage: python3 build.py <base.xlsx> <out.xlsx>
#   chat:  python3 build.py /mnt/project/<latest>.xlsx /home/claude/b2/<new>.xlsx   (or base downloaded from the repo)
#   repo:  python3 builder/build.py model/<current>.xlsx <new>.xlsx
import sys, os, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if len(sys.argv) != 3:
    sys.exit("usage: build.py <base.xlsx> <out.xlsx>")
BASE, out = sys.argv[1], sys.argv[2]
OUTDIR = os.path.dirname(os.path.abspath(out))
from inputs import spec_rack, arch, serving, energy_inputs
from calib import calib
from outputs import perf_sheet, sens_sheet, unit_cost, workload, nonnv
from finish import interface, checks, sources, readme, interface_b3, checks_b3, write_checks_b3
from training import tech_registry, train_in, perf_batch, training_sheet, sens_train
from finish import evidence_sheet
from preserve import snapshot, restore

wb = openpyxl.load_workbook(BASE)
# ---- v5.7 Excel-first: snapshot every input cell (blue font) before the rebuild ----
SNAP = snapshot(wb)
# ---- strip Block 2/3 content to recover the Block 1 base, then rebuild deterministically ----
for n in ["Arch","Serving","Workload","Calib","Perf","Sens_Perf","Unit_Cost","Energy","NonNV",
          "Tech_Registry","Train_In","Perf_Batch","Training","Sens_Train",
          "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
          "Har_In","Harness","Sens_Har"]:
    if n in wb.sheetnames: del wb[n]
def clear(ws, r0, c1=1, c2=30):
    for r in range(r0, ws.max_row + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.value = None; cell.fill = openpyxl.styles.PatternFill(fill_type=None)
clear(wb["Spec_Rack"], 21); 
for r in range(1, 21): wb["Spec_Rack"].cell(row=r, column=8).value = None
clear(wb["Interface"], 17); clear(wb["Checks"], 12); clear(wb["Sources"], 23); clear(wb["README"], 4, 1, 2)
for n in list(wb.defined_names.keys()):
    if n not in ("CTL_GW","CTL_PowerCase","IF_CapexFacility","IF_CapexIT","IF_CapexTotal","IF_FacilityGW",
                 "IF_GPUhrEcon","IF_GPUsPerGW","IF_HoldAcct","IF_HoldEcon","IF_PowerCost","IF_RacksPerGW"):
        del wb.defined_names[n]
SP = spec_rack(wb)
AR = arch(wb)
serving(wb)
CAL = calib(wb, SP, AR)
energy_inputs(wb)
TR = tech_registry(wb)
TI = train_in(wb)
PR = perf_sheet(wb, SP, AR, CAL, TR)
SR = sens_sheet(wb, SP, AR, CAL, TR)
PB = perf_batch(wb, SP, AR, CAL, TR, TI)
TRN = training_sheet(wb, SP, AR, TI, PB, TR)
STR = sens_train(wb, SP, AR, TI, PB, TR)
U = unit_cost(wb, PR)
WL = workload(wb, U)
nonnv(wb)
interface(wb, PR, U)
def last_row(ws):
    return max(c.row for row in ws.iter_rows() for c in row if c.value is not None)
ifr = last_row(wb["Interface"]) + 2
interface_b3(wb, TRN, ifr, TI)
checks(wb, CAL, PR, SR, U)
_r, _rows = checks_b3(wb, TRN, TI, CAL, PB)
write_checks_b3(wb, _r, _rows, SP)
# ---- v5.8: Block 4 ----
from block4 import cap_in, price_frontier, capability, cache_store, fleet, amortize, theory_rev, sens_rev, interface_b4, checks_b4, sources_b4, evidence_b4
K4 = cap_in(wb)
P4 = price_frontier(wb, K4, TR)
C4 = capability(wb, K4, P4, TRN, TI)
S4 = cache_store(wb)
F4 = fleet(wb, K4)
A4 = amortize(wb, F4, P4, S4)
T4 = theory_rev(wb, F4, A4, S4, WL)
K4["_capf"] = P4["capf"]
sens_rev(wb, K4, T4, A4)
interface_b4(wb, last_row(wb["Interface"]) + 2, P4, S4, A4, T4)
checks_b4(wb, P4, F4, A4, T4, U)
# ---- v5.9: Block 5 (harness) ----
from block5 import har_in, harness, sens_har, interface_b5, checks_b5, sources_b5, evidence_b5
H5 = har_in(wb, TR)
R5 = harness(wb, U, S4, WL)
SH5 = sens_har(wb, U, S4, WL, H5, R5)
interface_b5(wb, last_row(wb["Interface"]) + 2, R5)
checks_b5(wb, R5, H5, SH5)
sources(wb)
sources_b4(wb)
sources_b5(wb)
readme(wb)
# ---- v5.7: write back Excel-owned inputs, then the evidence register (created only if absent) ----
_m, _c, _d = restore(wb, SNAP, os.path.join(OUTDIR, "restore_log.txt"))
print(f"restore: matched {_m}, Excel kept over code {_c}, unmatched {len(_d)}")
evidence_sheet(wb)
print("evidence rows added:", evidence_b4(wb), evidence_b5(wb))
order = ["README","Inputs","Spec_Rack","Arch","Serving","Workload","Calib","Tech_Registry","Perf","Sens_Perf","Unit_Cost","DC_Cost",
         "Train_In","Perf_Batch","Training","Sens_Train",
         "Cap_In","Capability","Price_Frontier","Cache_Store","Fleet_1GW","Amortize","Theory_Rev","Sens_Rev",
         "Har_In","Harness","Sens_Har","Interface","Energy","NonNV","Sensitivity","Checks","Sources","DB_Evidence"]
wb._sheets = [wb[n] for n in order]
# ---- v5.3: Block 1 Checks — reference cells instead of literals (CC 第 1 輪第 6 節第 5 項) ----
from common import put, F_IN
ck = wb["Checks"]
for r, v in [(5, 35), (7, 2.21), (8, 2.65), (9, 10.5), (10, 3.57)]:
    put(ck, f"C{r}", v, F_IN, fmt="#,##0.00")
ck["E5"].value = '=IF(ABS(B5-C5)/C5<=0.2,"±20% 內","差距 >20%")'
ck["E7"].value = '=IF(B7>C7,"高於參照（參照假設未知）","低於參照")'
ck["E8"].value = '=IF(B8>C8,"高於參照（參照假設未知）","低於參照")'
ck["E9"].value = '="牌價 ÷ 持有成本＝"&TEXT(C9/B9,"0.0")&" 倍"'
ck["E10"].value = '="參照 ÷ 本模型＝"&TEXT(C10/B10,"0.00")'
# ---- v5.3: display-only named ranges (DRV_／CAL_／IF_Hdr；CC 第 1 輪第 6 節第 2、3 項) ----
from openpyxl.workbook.defined_name import DefinedName
def nm(n, ref): wb.defined_names[n] = DefinedName(n, attr_text=ref)
nm("IF_HdrGen", "Interface!$C$4:$Q$4"); nm("IF_HdrCost", "Interface!$C$5:$Q$5")
nm("DRV_Gen", "Perf!$C$4:$Q$4"); nm("DRV_Tier", "Perf!$C$5:$Q$5")
for n, k in [("DRV_FlopDec","Fd"),("DRV_FlopPre","Fp"),("DRV_WeightGB","W"),("DRV_TfixMs","tfix"),("DRV_SeqMs","ceff"),
             ("DRV_SeqBind","cbind"),("DRV_Batch","B"),("DRV_Bind","bind"),("DRV_DecTokGPU","D"),("DRV_PreTokGPU","Pp"),
             ("DRV_PreShare","psh"),("DRV_RackTok","rtot"),("DRV_GWTok","gwtot"),("DRV_Close","close")]:
    nm(n, f"Perf!$C${PR[k]}:$Q${PR[k]}")
nm("CAL_EtaD", f"Calib!$C${CAL['etad_fit']}"); nm("CAL_TlayerUs", f"Calib!$C${CAL['tl_fit']}")
nm("CAL_F_Label", f"Calib!$C${CAL['lab']}:$I${CAL['lab']}")
for n, k in [("CAL_F_Gen","gn"),("CAL_F_Eng","eng"),("CAL_F_Speed","s"),("CAL_F_Meas","T"),("CAL_F_Model","vT"),("CAL_F_Basis","basis")]:
    nm(n, f"Calib!$C${CAL[k]}:$I${CAL[k]}")
for n, k in [("CAL_H_Gen","mgn"),("CAL_H_Speed","ms"),("CAL_H_Meas","mT"),("CAL_H_Model","mO"),("CAL_H_Basis","mbasis")]:
    nm(n, f"Calib!$C${CAL[k]}:$F${CAL[k]}"); nm("CAL_F_Platform", f"Calib!$C${CAL['indep']}:$I${CAL['indep']}")
nm("CAL_F_Ratio", f"Calib!$C${CAL['ratio']}:$I${CAL['ratio']}")
nm("CAL_H_Label", f"Calib!$C${CAL['mhdr']}:$F${CAL['mhdr']}"); nm("CAL_H_Platform", f"Calib!$C${CAL['mplat']}:$F${CAL['mplat']}")
nm("CAL_H_Ratio", f"Calib!$C${CAL['mR']}:$F${CAL['mR']}")
# ---- v5.5: Block 3 display-only named ranges (TRN_；網站推導鏈用，下游不得連結) ----
for n, k in [("TRN_FlopTokPre","Fpt"),("TRN_FlopPre","Cp"),("TRN_GPUhPre","Hp"),("TRN_GPUhRL","Hrl"),("TRN_RLMFU","rlmfu"),
             ("TRN_RLRatioH","rlH"),("TRN_RLRatioF","rlF"),("TRN_GPUhFinal","Hfin"),("TRN_PostShareF","psF"),("TRN_PostShareH","psH"),
             ("TRN_InferShare","Ish"),("TRN_GPUhProg","Hprog"),("TRN_GWyrProg","GWp")]:
    nm(n, f"Training!$C${TRN[k]}:$Q${TRN[k]}")
nm("TRN_Gen", "Training!$C$4:$Q$4"); nm("TRN_Tier", "Training!$C$5:$Q$5")
# ---- v5.6: Tech_Registry display-only named ranges (TR_；網站唯讀表用，下游不得連結) ----
r0, r1 = TR["_rows"]; h0, h1 = TR["_hooks"]
for n, c in [("TR_ID","A"),("TR_Tech","B"),("TR_Hook","C"),("TR_Acts","D"),("TR_Lo","E"),("TR_Base","F"),("TR_Hi","G"),
             ("TR_Sel","H"),("TR_Status","I"),("TR_Labs","J"),("TR_Main","K"),("TR_Override","L"),("TR_InBase","M"),
             ("TR_Adopt","N"),("TR_Switch","O"),("TR_Eff","P"),("TR_Tag","Q"),("TR_Source","R"),("TR_Trigger","S"),("TR_Check","T")]:
    nm(n, f"Tech_Registry!${c}${r0}:${c}${r1}")
nm("TR_HookCode", f"Tech_Registry!$A${h0}:$A${h1}"); nm("TR_HookName", f"Tech_Registry!$B${h0}:$B${h1}")
nm("TR_HookVal", f"Tech_Registry!$E${h0}:$E${h1}")
wb.save(out)
import json; json.dump({"WL":WL,"H5":H5,"R5":R5,"SH5":SH5,"K4":K4,"P4":P4,"C4":C4,"S4":S4,"F4":F4,"A4":{k:v for k,v in A4.items() if not k.startswith("cost")},"T4":T4,"PR":PR,"CAL":CAL,"SR":SR,"PB":PB,"TRN":TRN,"STR":STR,"TI":TI,"TR":{k:v for k,v in TR.items() if not k.startswith("_")},"U":{f"{k[0]}_{k[1]}":v for k,v in U.items()},"SP":SP,"AR":AR}, open(os.path.join(OUTDIR, "rows.json"),"w"))
print("saved")
```

# 產生「20261023_NonNV昇騰Maia_A段.xlsx」審閱檔（唯讀查證，不碰 model/）
# 用法：python3 build_xlsx.py <輸出.xlsx>
# 推導頁的藍字＝輸入，黑字＝公式；欄 D/E/F＝該比值的「低端／基準／高端」取值
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

out = sys.argv[1]
wb = Workbook()
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
HDR = PatternFill("solid", fgColor="DDEBF7")
SEC = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")

# ---------------------------------------------------------------- 推導
ws = wb.active
ws.title = "推導"
ws["A1"] = "推導 — 昇騰 910C／CloudMatrix 384 與 Microsoft Maia 200 相對 VR200 NVL72 的每 GW 產出比與持有成本比"
ws["A1"].font = BOLD
ws["A2"] = ("欄 D／E／F＝該比值的低端／基準／高端取值（產出列：悲觀→樂觀；持有列：成本低→成本高）。"
            "藍字＝輸入；黑字＝公式。標記沿用 Verified／Interested-party／Analogy／Assumed／Derived。"
            "VR200 分母取自 model/20261023_Tokenomics_v20.1.xlsx（基準成本欄 Interface!M）。")
ws["A2"].alignment = WRAP
heads = ["編號", "物理量", "單位", "低端", "基準", "高端", "來源（證據編號／模型格）", "標記", "算式或說明"]
for i, h in enumerate(heads, 1):
    c = ws.cell(4, i, h)
    c.font = BOLD
    c.fill = HDR

R = {}          # key -> row
row = [5]


def sec(title):
    r = row[0]
    ws.cell(r, 1, title).font = BOLD
    for c in range(1, 10):
        ws.cell(r, c).fill = SEC
    row[0] += 1


def ref(key, col):
    return f"{col}{R[key]}"


def add(key, name, unit, vals, src, tag, note="", fmt=None):
    """vals: 3 個元素；數字＝輸入（藍），字串＝公式模板（{key.col} 以 ref 展開，col 預設同欄）"""
    r = row[0]
    R[key] = r
    ws.cell(r, 1, key)
    ws.cell(r, 2, name)
    ws.cell(r, 3, unit)
    for j, v in enumerate(vals):
        col = "DEF"[j]
        cell = ws[f"{col}{r}"]
        if isinstance(v, str) and v.startswith("="):
            f = v
            # 展開 {key} → 同欄；{key@E} → 指定欄
            import re

            def rep(m):
                k = m.group(1)
                cc = m.group(2) or col
                return ref(k, cc)
            f = re.sub(r"\{([A-Za-z0-9_]+)(?:@([DEF]))?\}", rep, f)
            cell.value = f
        else:
            cell.value = v
            cell.font = BLUE
        if fmt:
            cell.number_format = fmt
    ws.cell(r, 7, src)
    ws.cell(r, 8, tag)
    ws.cell(r, 9, note)
    ws.cell(r, 9).alignment = WRAP
    row[0] += 1


def same(v):
    return [v, v, v]


# ---- A. VR200 分母
sec("A. VR200 NVL72 分母（模型 v20.1；同層級、同 SLO）")
add("A1", "VR200 每 GPU 計算用峰值（NVFP4 dense）", "PF", same(35), "Spec_Rack!F35（＝F23）", "Interested-party（NVIDIA 規格；模型取 dense）", "模型『計算用峰值』")
add("A2", "VR200 機架配電設計功率（基準）", "kW", same(227), "Spec_Rack!F9", "Interested-party（Schneider 轉述 NVIDIA）", "")
add("A3", "每機架 GPU 封裝數", "顆", same(72), "Spec_Rack!F6", "Verified", "")
add("A4", "VR200 每顆 GPU 所攤機架功率", "kW", ["={A2}/{A3}"] * 3, "Derived", "Derived", "227÷72")
add("A5", "VR200 每 kW 峰值算力", "PF/kW", ["={A1}/{A4}"] * 3, "Derived", "Derived", "35÷3.153")
add("A6", "VR200 每 GW 機架數", "架", same(4052), "Interface!M6", "Derived（模型）", "")
add("A7", "VR200 每 GW GPU 數", "顆", same(291744), "Interface!M7", "Derived（模型）", "＝4052×72")
add("A8", "VR200 機架價格（基準）", "$M", same(8.4), "Spec_Rack!F12", "Interested-party", "")
add("A9", "VR200 每 GW IT 設備資本支出（基準）", "$B", same(37.5864), "Interface!M9", "Derived（模型）", "")
add("A10", "IT 資本支出 ÷（機架數×機架價）＝網路等加成", "x", ["={A9}/({A6}*{A8}/1000)"] * 3, "Derived", "Derived", "約 1.10；候選沿用同一加成")
add("A11", "VR200 每 GW 廠房資本支出（基準）", "$B", same(12.67), "Interface!M10", "Derived（模型）", "")
add("A12", "VR200 每 GW 年持有成本 — 經濟口徑（基準）", "$B/年", same(12.2255), "Interface!M13", "Derived（模型）", "分母")
add("A13", "VR200 每 GW 年持有成本 — 會計口徑（基準）", "$B/年", same(8.9923), "Interface!M12", "Derived（模型）", "")
add("A14", "VR200 每 GW IT 折舊（基準）", "$B/年", same(6.2644), "Interface!M220", "Derived（模型）", "")
add("A15", "VR200 每 GW IT 維護（基準）", "$B/年", same(0.591), "Interface!M224", "Derived（模型）", "")
add("A16", "VR200 每 GW 財產稅與保險（基準）", "$B/年", same(0.2513), "Interface!M227", "Derived（模型）", "")
add("A17", "資金成本（經濟 − 會計）", "$B/年", ["={A12}-{A13}"] * 3, "Derived", "Derived", "")
add("A18", "IT 設備占總資本支出比例", "—", ["={A9}/({A9}+{A11})"] * 3, "Derived", "Derived", "資金成本與財產稅依此比例分給 IT 設備（近似）")
add("A19", "持有成本中隨 IT 設備資本支出成比例的部分", "$B/年", ["={A14}+{A15}+({A16}+{A17})*{A18}"] * 3, "Derived", "Derived", "折舊＋維護＋(稅險＋資金成本)×IT 占比；廠房、電費、人員不隨之變")
add("A20", "上述部分占 VR200 持有成本比例 s", "—", ["={A19}/{A12}"] * 3, "Derived", "Derived", "候選持有比 ＝ 1 − s×(1 − k)，k＝候選 IT 資本支出 ÷ VR200")

# ---- B. 校準
sec("B. 還原既有世代：模型實際產出比 ÷ 『每 kW 峰值算力比』＝有效效率因子 f")
for key, nm, pf, kw, g, src_pf, vr in [
    ("H", "Hopper H100", 1.979, 41, 32, "Spec_Rack!C35,C9,C6", "Interface!D22/D32/D42"),
    ("G2", "GB200 NVL72", 10, 132, 72, "Spec_Rack!D35,D9,D6", "Interface!G22/G32/G42"),
    ("G3", "GB300 NVL72", 15, 136, 72, "Spec_Rack!E35,E9,E6", "Interface!J22/J32/J42"),
]:
    add(f"B_{key}_pf", f"{nm} 每 GPU 峰值", "PF", same(pf), src_pf, "Interested-party", "")
    add(f"B_{key}_kw", f"{nm} 機架配電功率（基準）", "kW", same(kw), src_pf, "Interested-party／Derived", "")
    add(f"B_{key}_n", f"{nm} 每機架 GPU", "顆", same(g), src_pf, "Verified", "")
    add(f"B_{key}_kwg", f"{nm} 每顆所攤功率", "kW", [f"={{B_{key}_kw}}/{{B_{key}_n}}"] * 3, "Derived", "Derived", "")
    add(f"B_{key}_r", f"{nm} 每 kW 峰值算力 ÷ VR200", "—", [f"=({{B_{key}_pf}}/{{B_{key}_kwg}})/{{A5}}"] * 3, "Derived", "Derived", "")
vr = {"H": (0.1075, 0.1054, 0.0978), "G2": (0.5346, 0.5132, 0.4837), "G3": (0.6932, 0.6657, 0.5638)}
for key, nm in [("H", "Hopper"), ("G2", "GB200"), ("G3", "GB300")]:
    add(f"B_{key}_v", f"{nm} VR-eq（Luna／Sol／Astra）", "—", list(vr[key]), vr["H"] and "Interface IF_VReq_*", "Derived（模型）", "欄 D/E/F＝Luna／Sol／Astra（此行不是低/基準/高）")
    add(f"B_{key}_vm", f"{nm} VR-eq 三層平均", "—", [f"=AVERAGE(D{R[f'B_{key}_v']}:F{R[f'B_{key}_v']})"] * 3, "Derived", "Derived", "")
    add(f"B_{key}_f", f"{nm} 有效效率因子 f", "—", [f"={{B_{key}_vm}}/{{B_{key}_r}}"] * 3, "Derived", "Derived", "f＝實際產出比 ÷ 峰值/kW 比；涵蓋延遲、批次、記憶體、EP 通訊、利用率")

# ---- C. 昇騰
sec("C. 華為昇騰 910C／CloudMatrix 384（CM384）")
add("C1", "每顆（雙 die 封裝）INT8 dense 峰值", "PF", same("=6688/4.45/1000"), "E13（6,688 tok/s ÷ 4.45 tok/s/TFLOPS；亦 1,943÷1.29＝1,506）", "Derived（華為論文換算；Interested-party）", "910C 無原生 FP8；INT8≈BF16 的 2 倍（BF16 752 TF，E10）。與 FP8 權重 1 B/param 同位元組，故與 VR200 的 NVFP4 比較時不另加精度修正", fmt="0.000")
add("C2", "CM384 系統功率", "kW", [559, 559, 425], "E12（559：SemiAnalysis 估，單一來源；350–500：中文分析，取中點 425 作樂觀端）", "Assumed（區間）／Interested-party 缺", "華為未公布整機功率。口徑提醒（查核）：559 kW 搭配 SemiAnalysis 的 GB200＝145 kW；模型分母的 GB200 為 132 kW。按模型口徑縮放（559×132/145≈509 kW）產出比基準約 0.088；The Register 轉述約 600 kW（GB200 120 kW）則約 0.075。故基準 0.08 落在 0.075–0.09")
add("C3", "每系統 NPU 數", "顆", same(384), "E11", "Verified（官方規格）", "12 運算機架＋4 互連機架")
add("C4", "每顆所攤系統功率", "kW", ["={C2}/{C3}"] * 3, "Derived", "Derived", "")
add("C5", "每 kW 峰值算力", "PF/kW", ["={C1}/{C4}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("C6", "÷ VR200 每 kW 峰值算力", "—", ["={C5}/{A5}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("C7", "有效效率因子 f（昇騰）", "—", [0.50, "={B_H_f@E}", 1.00], "低 0.50：Assumed，介於 Hopper 與 HBM 頻寬/kW 比 0.31 之間；基準＝Hopper 還原值（E13 顯示單顆 ≈H800）；高 1.00：≈GB200 還原值，亦≈基準×1.28（論文 tok/s/TFLOPS 1.29 vs H800 0.93–1.17 的上緣）", "Assumed（區間）／Analogy（Hopper）", "")
add("C8", "方法一：產出比 ＝ C6 × C7", "—", ["={C6}*{C7}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("C9", "Hopper VR-eq 三層平均（模型）", "—", ["={B_H_vm@E}"] * 3, "模型", "Derived", "")
add("C10", "每 kW 顆數 ÷ Hopper（Hopper 1.28 kW/顆）", "—", ["={B_H_kwg@E}/{C4}"] * 3, "Derived", "Derived", "")
add("C11", "每顆實測 token 產出 ÷ H800/H100", "—", [0.60, 1.00, 1.30], "低 0.60：DeepSeek 自測 910C≈H100 的 60%（E14，2025-02，媒體轉述）；基準 1.00：E13 decode 1,943 vs H800 1,850＝1.05、prefill 6,688 vs 4,026–7,839＝0.85–1.66；高 1.30：Assumed", "Interested-party（華為論文）＋Interested-party（DeepSeek 自測）", "兩個自述互相衝突（0.6 vs 約 1.0）：論文較新且含 CM384 專屬最佳化。6,688 為論文「完美 EPLB」投射值，預設實測 5,655（對 H800 blog 4,026＝1.40）；論文對照批次 H100/H800 為 128、昇騰為 96，非完全同條件；「60%」僅溯源到單一 WeChat 轉述鏈")
add("C12", "方法二：產出比 ＝ C9 × C10 × C11", "—", ["={C9}*{C10}*{C11}"] * 3, "Derived", "Derived", "以 Hopper 實測錨定。查核提醒：與方法一同源（皆乘模型 Hopper 還原值與同一 kW 密度比，差別僅在乘數 0.76 對 1.0），平均不是獨立交叉驗證", fmt="0.0000")
add("C13", "昇騰 910C 每 GW 產出比（原始）", "—", ["=MIN(D{r8},D{r12})".replace("{r8}", str(R["C8"])).replace("{r12}", str(R["C12"])),
                                            f"=AVERAGE(E{R['C8']},E{R['C12']})",
                                            f"=MAX(F{R['C8']},F{R['C12']})"], "Derived", "Derived（含 Assumed）", "低＝兩法低端取小；基準＝兩法平均；高＝兩法高端取大。兩法同源（見 C12），實質為 Hopper×每 GW 顆數比 0.88×(0.76–1.0)", fmt="0.0000")
add("C14", "CM384 系統價格", "$M", [6.0, 8.2, 12.0], "E16（FT 經 Benzinga：約 ¥60M≈$8.2M；與 NVL72 約 $3M 相比）；E17（單顆 ¥18–20 萬→384 顆 ≈$10M）；低 6.0／高 12.0：Assumed", "Interested-party（分析師報價）／Assumed", "中國市場價；非 CSP 全球口徑")
add("C15", "每 GW 系統數（以基準功率 559 kW）", "套", [f"={{A6}}*{{A2}}/$E${R['C2']}"] * 3, "Derived", "Derived", "與 VR200 同樣：每 GW 機架功率容量相同（含同一 1.087 機房加成）")
add("C16", "每 GW IT 設備資本支出", "$B", ["={C15}*{C14}/1000*{A10}"] * 3, "Derived", "Derived", "")
add("C17", "k ＝ ÷ VR200 每 GW IT 資本支出", "—", ["={C16}/{A9}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("C18", "昇騰 910C 每 GW 持有成本比（原始）", "—", ["=1-{A20}*(1-{C17})"] * 3, "Derived", "Derived（含 Assumed）", "", fmt="0.0000")
add("C19", "每 GW 顆數", "顆", ["={C15}*{C3}"] * 3, "Derived", "Derived", "VR200 為 291,744")

# ---- D. Maia
sec("D. Microsoft Maia 200")
add("D1", "每顆 FP4 峰值", "PF", same(10), "E01（『over 10 PFLOPS』；是否 dense 微軟未註明）", "Interested-party（Microsoft）", "FP8 >5 PF；與 VR200 比較用 FP4 對 NVFP4，FP8 比值相同（皆 1:2）")
add("D2", "Maia 200 機架功率", "kW", ["=64*1.15", 64, "=64*0.9"], "E03（單一來源；64 kW 為 Maia 300 報導中的對照值）", "Interested-party／Assumed（±15%／−10%）", "低端含 15% 不確定；高端−10%。64 kW 只有 StorageReview（轉述微軟 Maia 300 發表）一條來源鏈，是否含冷卻／配電未知（Maia 300 的 167 kW 明說含）。旁證：機架功率 ÷ 晶片 TDP＝64÷(48×0.75)＝1.78，與 VR200 的 227÷(72×1.8)＝1.75 一致")
add("D3", "每機架晶片數", "顆", same("=ROUND(10.4/0.216,0)"), "E03（StorageReview 規格表直接列 48 顆；與 HBM 10.4 TB÷216 GB、341 TB/s÷7.1、485 POPS÷10 吻合；微軟論文 arXiv 2608.24664 亦寫 48 SoC／12 托盤，據查核員）", "Derived", "報導未直接寫 48，由三個總量交叉得出")
add("D4", "每顆所攤機架功率", "kW", ["={D2}/{D3}"] * 3, "Derived", "Derived", "")
add("D5", "每 kW 峰值算力", "PF/kW", ["={D1}/{D4}"] * 3, "Derived", "Derived", "")
add("D6", "÷ VR200 每 kW 峰值算力", "—", ["={D5}/{A5}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("D7", "有效效率因子 f（Maia）", "—", [0.45, 0.80, 1.00], "Assumed：新一代自研軟體堆疊、無公開 MLPerf／第三方實測（E08）、乙太網 scale-up；基準略高於 Hopper 還原值（HBM 容量/kW 為 VR200 的 1.8 倍有助大批次）；高端＝GB200 還原值", "Assumed（區間）", "")
add("D8", "Maia 200 每 GW 產出比（原始）", "—", ["={D6}*{D7}"] * 3, "Derived", "Derived（含 Assumed）", "", fmt="0.0000")
add("D9", "每 GW 顆數", "顆", [f"={{A6}}*{{A2}}/{{D2}}*{{D3}}"] * 3, "Derived", "Derived", "")
add("D10", "Maia 200 機架價格（買方取得價，含 ASIC 夥伴利潤與 NRE 攤提）", "$M", [0.5, 0.8, 1.2], "無公開價格（E08 未找到）。Analogy 自下而上（查核後修正）：HBM 216 GB×$13–17/GB＝$2.8–3.7K（E07）；晶片＋封裝 $1.2–2.5K（晶圓 $17–22K，E07）；NRE $200–500M÷15–20 萬顆＝$1.0–3.3K（E06）；晶片合計約 $5–9.5K，系統加成約 2 倍→每顆 $10–19K、每機架（48 顆）$0.5–0.9M。基準 $0.8M 取該範圍中上段，高端 $1.2M 預留托盤／主機／交換器加成不確定", "Assumed／Analogy（區間）", "全表最不確定的輸入")
add("D11", "每 GW 機架數（以基準功率 64 kW）", "架", [f"={{A6}}*{{A2}}/$E${R['D2']}"] * 3, "Derived", "Derived", "")
add("D12", "每 GW IT 設備資本支出", "$B", ["={D11}*{D10}/1000*{A10}"] * 3, "Derived", "Derived", "")
add("D13", "k ＝ ÷ VR200 每 GW IT 資本支出", "—", ["={D12}/{A9}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("D14", "Maia 200 每 GW 持有成本比（原始）", "—", ["=1-{A20}*(1-{D13})"] * 3, "Derived", "Derived（含 Assumed）", "", fmt="0.0000")

# ---- E. 交叉檢核
sec("E. 交叉檢核（不進建議值）")
add("E1", "微軟自述『每瓦 token 1.7 倍於領先 GPU 基礎設施』若基準＝GB300 → 隱含 VR-eq", "—", ["=1.7*" + ref("B_G3_vm", "E")] * 3, "E05（基準未點名；LinkedIn 轉貼為主）", "Interested-party（Microsoft）", "若屬實，Maia 200 每 GW 產出約 VR200 的 1.1 倍，遠高於本表高端 → 視為行銷上限，不採用")
add("E2", "GB300 每 GW 持有成本比（基準 10.8864÷12.2255）", "—", same("=10.8864/12.2255"), "Interface!J13,M13", "Derived（模型）", "")
add("E3", "GB300 產出 ÷ 持有（Sol 層）", "—", same("=" + ref("B_G3_v", "E") + "/" + ref("E2", "E")), "Derived", "Derived", "")
add("E4", "微軟『每美元效能比艦隊最新硬體高 30%』→ Maia 須達到的 產出÷持有", "—", same("=1.3*" + ref("E3", "E")), "E04（基準未點名；CRN Asia 稱比對 Maia 100；微軟論文另稱 TCO −30%，語意約 1.43× perf/$，則需求升至約 1.07）", "Interested-party（Microsoft）", "以 GB300 為艦隊最新硬體的假設")
add("E5", "本表 Maia 基準 產出÷持有", "—", ["={D8}/{D14}"] * 3, "Derived", "Derived", "欄 D/E/F 為各自低/基準/高端相除，非情境配對")
add("E6", "本表 Maia 基準 ÷ 微軟自述需求", "—", ["=" + ref("E5", "E") + "/" + ref("E4", "E")] * 3, "Derived", "Derived", "≈1 表示本表基準與微軟自述的 30% 可並存；<1 表示自述較樂觀")

# ---- F. 敏感度
sec("F. 敏感度（一次動一個參數，其餘取基準；欄 D＝參數低值對應結果，F＝高值對應結果）")


def sens(key, nm, flo, fhi, note=""):
    add(key, nm, "—", [flo, f"={{{note}@E}}" if note else None, fhi], "Derived", "Derived", "")


# 昇騰產出：方法一對 f 與 kW；方法二對 token 比
base_c8 = ref("C8", "E")
add("F1", "昇騰：方法一，f 取 低/基準/高", "產出比", [f"={ref('C6','E')}*{ref('C7','D')}", f"={base_c8}", f"={ref('C6','E')}*{ref('C7','F')}"], "Derived", "Derived", "", fmt="0.0000")
add("F2", "昇騰：方法一，系統功率 559／559／425 kW", "產出比", [f"={ref('C6','D')}*{ref('C7','E')}", f"={base_c8}", f"={ref('C6','F')}*{ref('C7','E')}"], "Derived", "Derived", "功率 559→425 kW 使產出比 ×1.32", fmt="0.0000")
add("F3", "昇騰：方法二，每顆 token 比 0.6／1.0／1.3", "產出比", [f"={ref('C9','E')}*{ref('C10','E')}*{ref('C11','D')}", f"={ref('C12','E')}", f"={ref('C9','E')}*{ref('C10','E')}*{ref('C11','F')}"], "Derived", "Derived", "", fmt="0.0000")
add("F4", "昇騰：持有比，系統價格 6.0／8.2／12.0 $M", "持有比", [f"={ref('C18','D')}", f"={ref('C18','E')}", f"={ref('C18','F')}"], "Derived", "Derived", "", fmt="0.0000")
add("F5", "昇騰：持有比，系統功率 425／559／640 kW（價格取基準）", "持有比", [f"=1-{ref('A20','E')}*(1-({ref('A6','E')}*{ref('A2','E')}/425*{ref('C14','E')}/1000*{ref('A10','E')})/{ref('A9','E')})",
                                                          f"={ref('C18','E')}",
                                                          f"=1-{ref('A20','E')}*(1-({ref('A6','E')}*{ref('A2','E')}/640*{ref('C14','E')}/1000*{ref('A10','E')})/{ref('A9','E')})"], "Derived", "Derived", "功率↓使每 GW 套數↑、資本支出↑，持有比反而升", fmt="0.0000")
base_d8 = ref("D8", "E")
add("F6", "Maia：f 0.45／0.80／1.00", "產出比", [f"={ref('D6','E')}*{ref('D7','D')}", f"={base_d8}", f"={ref('D6','E')}*{ref('D7','F')}"], "Derived", "Derived", "", fmt="0.0000")
add("F7", "Maia：機架功率 73.6／64／57.6 kW", "產出比", [f"={ref('D6','D')}*{ref('D7','E')}", f"={base_d8}", f"={ref('D6','F')}*{ref('D7','E')}"], "Derived", "Derived", "", fmt="0.0000")
add("F8", "Maia：機架價格 0.5／0.8／1.2 $M", "持有比", [f"={ref('D14','D')}", f"={ref('D14','E')}", f"={ref('D14','F')}"], "Derived", "Derived", "", fmt="0.0000")
add("F9", "Maia：f 對 產出÷持有 的影響（f 低／基準／高，持有取基準）", "產出÷持有", [f"={ref('F6','D')}/{ref('D14','E')}", f"={ref('F6','E')}/{ref('D14','E')}", f"={ref('F6','F')}/{ref('D14','E')}"], "Derived", "Derived", "", fmt="0.0000")

for col, w in zip("ABCDEFGHI", [8, 52, 10, 12, 12, 12, 46, 26, 60]):
    ws.column_dimensions[col].width = w
for r in range(5, row[0]):
    for c in (4, 5, 6):
        cell = ws.cell(r, c)
        if cell.number_format == "General":
            cell.number_format = "0.0000" if ws.cell(r, 3).value in ("—", "PF/kW") else "General"
    ws.cell(r, 7).alignment = WRAP
    ws.cell(r, 8).alignment = WRAP
ws.freeze_panes = "D5"

# ---------------------------------------------------------------- 建議值
sv = wb.create_sheet("建議值", 0)
sv["A1"] = ("建議值 — 擬新增至 NonNV 頁的兩列候選（欄位同 NonNV A:L；全部相對 VR200 NVL72、同層級、同 SLO）｜A 段僅提案，未寫入 model/")
sv["A1"].font = BOLD
sv["A2"] = ("第 4–5 列＝推導頁公式的原始結果（公式）；第 8–9 列＝建議輸入值（輸入，已四捨五入至 0.05；寫入 NonNV 時為藍字輸入，標記 Assumed）；"
            "H／I／J 沿用 NonNV 的公式：H＝F÷C、I＝E÷D、J＝G÷B。")
sv["A2"].alignment = WRAP
cols = ["候選", "產出比 低", "產出比 基準", "產出比 高", "持有比 低", "持有比 基準", "持有比 高", "每 token 成本比 基準", "最佳角落", "最差角落", "標記", "說明", "B:G 屬性"]
for i, h in enumerate(cols, 1):
    c = sv.cell(3, i, h)
    c.font = BOLD
    c.fill = HDR
sv["A4"] = "華為昇騰 910C／CloudMatrix 384（原始公式結果）"
sv["A5"] = "Microsoft Maia 200（原始公式結果）"
for r, (o, h) in zip((4, 5), (("C13", "C18"), ("D8", "D14"))):
    for col, src in zip("BCD", "DEF"):
        sv[f"{col}{r}"] = f"=推導!{src}{R[o]}"
    for col, src in zip("EFG", "DEF"):
        sv[f"{col}{r}"] = f"=推導!{src}{R[h]}"
    sv[f"H{r}"] = f"=F{r}/C{r}"
    sv[f"I{r}"] = f"=E{r}/D{r}"
    sv[f"J{r}"] = f"=G{r}/B{r}"
    sv[f"M{r}"] = "B:G＝公式（連結 推導 頁）；H:J＝公式"
sv["A7"] = "建議輸入值（寫入 NonNV 第 10、11 列的內容）"
sv["A7"].font = BOLD
sv["A8"] = "華為昇騰 910C／CloudMatrix 384"
sv["A9"] = "Microsoft Maia 200"
inp = {8: (0.05, 0.08, 0.15, 0.45, 0.55, 0.70), 9: (0.25, 0.55, 0.75, 0.40, 0.50, 0.60)}
note = {
    8: "現行主力＝910C／CM384（950PR 2026-03 發表、僅 prefill 型；950DT／Atlas 950 SuperPoD 預定 2026Q4，尚無出貨證據）。單顆約等於 H800、每 GW 顆數略少於 Hopper 且無 FP4，故產出比約 Hopper 水準（0.10）以下；系統價約 NVL72 的 2.7 倍但功率約 3.9 倍，每 kW 價格遠低於 VR200。功率 559 kW 為 SemiAnalysis 單一來源。",
    9: "Maia 200（2026-01 發表，TSMC 3nm，FP4>10 PF／750 W，216 GB HBM3e，機架 48 顆／64 kW）。每 kW 峰值算力約為 VR200 的 0.68；軟體成熟度為主要不確定，無第三方實測；價格無公開資料（全表最弱輸入）；機架 64 kW 為單一來源鏈。",
}
for r in (8, 9):
    for j, v in enumerate(inp[r]):
        c = sv.cell(r, 2 + j, v)
        c.font = BLUE
    sv[f"H{r}"] = f"=F{r}/C{r}"
    sv[f"I{r}"] = f"=E{r}/D{r}"
    sv[f"J{r}"] = f"=G{r}/B{r}"
    sv[f"K{r}"] = "Assumed"
    sv[f"L{r}"] = note[r]
    sv[f"L{r}"].alignment = WRAP
    sv[f"M{r}"] = "B:G＝輸入（藍字，四捨五入自第 4–5 列）；H:J＝公式"
sv["A12"] = "與既有五列的相對位置（NonNV 第 5–9 列為模型現值；第 8、9 列為本提案）"
sv["A12"].font = BOLD
for i, h in enumerate(["候選", "產出比 基準", "持有比 基準", "每 token 成本比", "產出比 區間", "持有比 區間", "備註"], 1):
    c = sv.cell(13, i, h)
    c.font = BOLD
    c.fill = HDR
exist = [
    ("AMD MI455X（Helios）", 0.5, 0.7, 1.0, 0.8, 0.9, 1.0),
    ("Google TPU v7 Ironwood", 0.6, 0.8, 1.1, 0.7, 0.8, 1.0),
    ("AWS Trainium3", 0.3, 0.5, 0.8, 0.6, 0.7, 0.9),
    ("Cerebras WSE-3", 0.2, 0.4, 0.8, 0.8, 1.0, 1.2),
    ("OpenAI／Broadcom 客製", 0.4, 0.6, 0.9, 0.7, 0.8, 1.0),
]
r = 14
for nm, ol, ob, oh, hl, hb, hh in exist:
    sv.cell(r, 1, nm)
    sv.cell(r, 2, ob)
    sv.cell(r, 3, hb)
    sv.cell(r, 4, f"=C{r}/B{r}")
    sv.cell(r, 5, f"{ol}–{oh}")
    sv.cell(r, 6, f"{hl}–{hh}")
    sv.cell(r, 7, "模型 v20.1 NonNV 現值（輸入）")
    r += 1
for rr, nm in ((8, "華為昇騰 910C／CM384（提案）"), (9, "Microsoft Maia 200（提案）")):
    sv.cell(r, 1, nm)
    sv.cell(r, 2, f"=C{rr}")
    sv.cell(r, 3, f"=F{rr}")
    sv.cell(r, 4, f"=C{r}/B{r}")
    sv.cell(r, 5, f'=TEXT(B{rr},"0.00")&"–"&TEXT(D{rr},"0.00")')
    sv.cell(r, 6, f'=TEXT(E{rr},"0.00")&"–"&TEXT(G{rr},"0.00")')
    sv.cell(r, 7, "本提案（公式引用上方輸入列）")
    r += 1
for col, w in zip("ABCDEFGHIJKLM", [36, 11, 11, 11, 11, 11, 11, 14, 10, 10, 10, 70, 34]):
    sv.column_dimensions[col].width = w

# ---------------------------------------------------------------- 證據
ev = wb.create_sheet("證據")
eh = ["編號", "主張", "數值", "單位", "口徑", "出處網址", "來源等級", "立場", "標記", "取得方式與備註", "用於"]
for i, h in enumerate(eh, 1):
    c = ev.cell(1, i, h)
    c.font = BOLD
    c.fill = HDR
from evidence_data import EVIDENCE, QUESTIONS
for rr, rowv in enumerate(EVIDENCE, 2):
    for cc, v in enumerate(rowv, 1):
        cell = ev.cell(rr, cc, v)
        cell.alignment = WRAP
for col, w in zip("ABCDEFGHIJK", [6, 52, 22, 10, 30, 56, 18, 10, 24, 52, 10]):
    ev.column_dimensions[col].width = w
ev.freeze_panes = "C2"

# ---------------------------------------------------------------- 待判斷
qd = wb.create_sheet("待判斷")
qh = ["編號", "題目", "預設（本提案採用）", "替代方案", "影響"]
for i, h in enumerate(qh, 1):
    c = qd.cell(1, i, h)
    c.font = BOLD
    c.fill = HDR
for rr, rowv in enumerate(QUESTIONS, 2):
    for cc, v in enumerate(rowv, 1):
        cell = qd.cell(rr, cc, v)
        cell.alignment = WRAP
for col, w in zip("ABCDE", [6, 50, 50, 50, 40]):
    qd.column_dimensions[col].width = w

wb.save(out)
print("saved", out, "rows", row[0])

# 產生「NonNV_Cerebras_OpenAI.xlsx」審閱檔（唯讀查證，不碰 model/）
# 用法：python3 build_xlsx.py <輸出.xlsx>，再以 LibreOffice headless 轉存寫入計算值
# 方法沿用 C 段（docs/evidence/20261025_NonNV_AMD/build_xlsx.py）、B 段與 A 段：
#   產出比＝（候選每 kW 峰值算力 ÷ VR200）× 效率因子 f；持有比＝1 − s ×（1 − k）
# 本段：Cerebras 每 kW 法不適用（SRAM 容量瓶頸），只給方向界線；持有比兩法並列（衝突）。
#       OpenAI Jalapeño 方法一（每 kW 峰值 × f）＋方法二（OpenAI 自測每 kW 吞吐，以 TK GB300 為錨點）。
# 推導頁藍字＝輸入，黑字＝公式；欄 D/E/F＝低端／基準／高端
import re
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from evidence_data import EVIDENCE, QUESTIONS  # noqa: E402

out = sys.argv[1]
wb = Workbook()
BLUE = Font(color="0000FF")
BOLD = Font(bold=True)
HDR = PatternFill("solid", fgColor="DDEBF7")
SEC = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="top")

ws = wb.active
ws.title = "推導"
ws["A1"] = "推導 — Cerebras CS-3（WSE-3）與 OpenAI／Broadcom Jalapeño 相對 VR200 NVL72 的每 GW 產出比與持有成本比（D 段；方法同 A–C 段）"
ws["A1"].font = BOLD
ws["A2"] = ("欄 D／E／F＝低端／基準／高端（產出列：悲觀→樂觀；持有列：成本低→成本高）。藍字＝輸入；黑字＝公式。"
            "VR200 分母取自 model/20261025_Tokenomics_v21.7.xlsx（數值與 C 段 v21.6 相同）。證據編號 C01–C11、O01–O08 見『證據』頁。")
ws["A2"].alignment = WRAP
heads = ["編號", "物理量", "單位", "低端", "基準", "高端", "來源（證據編號／模型格）", "標記", "算式或說明"]
for i, h in enumerate(heads, 1):
    c = ws.cell(4, i, h)
    c.font = BOLD
    c.fill = HDR

R = {}
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
    r = row[0]
    R[key] = r
    ws.cell(r, 1, key)
    ws.cell(r, 2, name)
    ws.cell(r, 3, unit)
    for j, v in enumerate(vals):
        col = "DEF"[j]
        cell = ws[f"{col}{r}"]
        if isinstance(v, str) and v.startswith("="):
            def rep(m):
                return ref(m.group(1), m.group(2) or col)
            cell.value = re.sub(r"\{([A-Za-z0-9_]+)(?:@([DEF]))?\}", rep, v)
        else:
            cell.value = v
            cell.font = BLUE
        if fmt:
            cell.number_format = fmt
    ws.cell(r, 7, src)
    ws.cell(r, 8, tag)
    ws.cell(r, 9, note)
    row[0] += 1


def same(v):
    return [v, v, v]


# ---- A. VR200 分母
sec("A. VR200 NVL72 分母（模型 v21.7；同層級、同 SLO）")
add("A1", "VR200 每 GPU 計算用峰值（NVFP4 dense；模型服務精度）", "PF", same(35), "Spec_Rack!F35", "Interested-party（NVIDIA 規格）", "")
add("A2", "VR200 機架配電設計功率（基準）", "kW", same(227), "Spec_Rack!F9", "Interested-party", "Max-P 設計功率")
add("A3", "每機架 GPU 封裝數", "顆", same(72), "Spec_Rack!F6", "Verified", "")
add("A4", "VR200 每顆所攤機架功率", "kW", ["={A2}/{A3}"] * 3, "Derived", "Derived", "")
add("A5", "VR200 每 kW 峰值算力（NVFP4）", "PF/kW", ["={A1}/{A4}"] * 3, "Derived", "Derived", "")
add("A21", "VR200 每 GPU FP8 dense", "PF", same(17.5), "Spec_Rack!F40", "Interested-party", "")
add("A26", "VR200 每 GPU BF16 dense", "PF", same(4), "Spec_Rack!F39", "Interested-party", "Cerebras FP16 對齊口徑用")
add("A24", "VR200 每 GPU HBM 容量", "GB", same(288), "Spec_Rack!F25", "Interested-party", "")
add("A6", "VR200 每 GW 機架數", "架", same(4052), "Interface!M6", "Derived（模型）", "")
add("A7", "VR200 每 GW 機架 IT 功率（＝A6×A2）", "MW", ["={A6}*{A2}/1000"] * 3, "Derived", "Derived", "候選每 GW 台數＝此值 ÷ 候選每台功率（同 A–C 段）")
add("A8", "VR200 機架價格（基準）", "$M", same(8.4), "Spec_Rack!F12", "Interested-party", "買方取得價（MS BOM 7.8 × 1.075）")
add("A9", "VR200 每 GW IT 設備資本支出（基準）", "$B", same(37.586352), "Interface!M9", "Derived（模型）", "")
add("A10", "IT 資本支出 ÷（機架數×機架價）＝網路等加成", "x", ["={A9}/({A6}*{A8}/1000)"] * 3, "Derived", "Derived", "約 1.10")
add("A11", "VR200 每 GW 廠房資本支出", "$B", same(12.67), "Interface!M10", "Derived（模型）", "")
add("A12", "VR200 每 GW 年持有成本 — 經濟口徑", "$B/年", same(12.2254710045841), "Interface!M13", "Derived（模型）", "分母")
add("A13", "VR200 每 GW 年持有成本 — 會計口徑", "$B/年", same(8.9923042149807), "Interface!M12", "Derived（模型）", "")
add("A14", "VR200 每 GW IT 折舊", "$B/年", same(6.264392), "Interface!M220", "Derived（模型）", "")
add("A15", "VR200 每 GW IT 維護", "$B/年", same(0.591045788314028), "Interface!M224", "Derived（模型）", "")
add("A16", "VR200 每 GW 財產稅與保險", "$B/年", same(0.25128176), "Interface!M227", "Derived（模型）", "")
add("A17", "資金成本（經濟 − 會計）", "$B/年", ["={A12}-{A13}"] * 3, "Derived", "Derived", "")
add("A18", "IT 設備占總資本支出比例", "—", ["={A9}/({A9}+{A11})"] * 3, "Derived", "Derived", "")
add("A19", "持有成本中隨 IT 設備資本支出成比例的部分", "$B/年", ["={A14}+{A15}+({A16}+{A17})*{A18}"] * 3, "Derived", "Derived", "")
add("A20", "上述部分占 VR200 持有成本比例 s", "—", ["={A19}/{A12}"] * 3, "Derived", "Derived", "候選持有比 ＝ 1 − s×(1 − k)；0.774（同 A–C 段）")

# ---- B. GB300 錨點
sec("B. GB300 NVL72 錨點（TK 模型值；方法二與 Cerebras 容量換算共用）")
add("B1", "GB300 機架配電功率（基準）", "kW", same(136), "Spec_Rack!E9", "Interested-party／Derived", "")
add("B2", "GB300 每機架 GPU", "顆", same(72), "Spec_Rack!E6", "Verified", "")
add("B3", "GB300 GPU 封裝功率", "W", same(1400), "Spec_Rack!E33；OpenAI 正規化同用 1,400 W（O04）", "Interested-party", "")
add("B4", "GB300 機架 ÷ 封裝功率總和（倍數）", "x", ["={B1}*1000/({B2}*{B3})"] * 3, "Derived", "Derived", "1.35")
add("B5", "GB300 VR-eq（Luna／Sol／Astra）", "—", [0.693216239743152, 0.665656345719338, 0.563845155935545], "Interface IF_VReq_Luna/Sol/Astra（I22/I32/I42）", "Derived（模型）", "欄 D/E/F＝Luna／Sol／Astra（此行不是低/基準/高）")
add("B6", "GB300 VR-eq 三層平均（每 GW 產出 ÷ VR200）", "—", [f"=AVERAGE(D{R['B5']}:F{R['B5']})"] * 3, "Derived", "Derived", "0.641")
add("B7", "MLPerf v6.1 Llama2-70b-99.9 Server：GB300 每顆吞吐", "tok/s/GPU", same(15998), "C 段證據 M05（docs/evidence/20261025_NonNV_AMD）", "第三方實測（MLPerf）", "NVFP4；Server 情境")
add("B8", "GB300 每機架 kW 吞吐（Llama2-70B）", "tok/s/kW", ["={B7}/({B1}/{B2})"] * 3, "Derived", "Derived", "")
add("B9", "TK 倍數（機架÷晶片）：GB200／GB300／VR200 Max-P／VR200 Max-Q 平均", "x", same("=AVERAGE(132/(72*1.2),136/(72*1.4),227/(72*1.8),188/(72*1.8))"), "Spec_Rack!D–F 列 8、9、33", "Derived", "1.52（同 B 段 Trn3 基準）")

# ---- C. Cerebras
sec("C. Cerebras CS-3（1 片 WSE-3／系統；每架 2 台，C03）——每 kW 法不適用，以下為方向界線")
add("C1", "每系統 FP16 dense 峰值", "PF", same(12.5), "C01（＝125 sparse ÷ 10）；C04（記者假設，與 C01 同口徑）", "記者整理（源自 Cerebras）", "WSE-3 未公布 FP8／FP4（C08：推論全程 16-bit）")
add("C2", "每系統功率", "kW", [27, 23, 23], "低端 C02（up to 27 kW）；基準／高端 C01、C03（23 kW）", "第三方（區間）", "不含 MemoryX、SwarmX、主機（未公布，C11）")
add("C3", "每 kW FP16 dense 峰值", "PF/kW", ["={C1}/{C2}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("C4", "(a) 最高原生精度：÷ VR200 每 kW NVFP4 峰值", "—", ["={C3}/{A5}"] * 3, "Derived", "Derived", "FP16 對 NVFP4", fmt="0.0000")
add("C5", "(b) FP16 對齊：÷ VR200 每 kW BF16 峰值", "—", ["={C3}/({A26}/{A4})"] * 3, "Derived", "Derived", "f≤1 時產出比上限", fmt="0.0000")
add("C6", "每系統 SRAM", "GB", same(44), "C01", "Interested-party", "權重與 KV 都要放 SRAM")
add("C7", "每 kW 記憶體容量 ÷ VR200（HBM）", "—", ["=({C6}/{C2})/({A24}*{A3}/{A2})"] * 3, "Derived", "Derived", "約 2%：容量是瓶頸（1T 參數 4-bit 權重約 0.5 TB ⇒ 至少 12 台、約 280 kW 才放得下權重）", fmt="0.0000")
add("C10", "Cerebras 自述容量（Llama 70B）", "tok/s", same(40000000), "C07", "Interested-party（Cerebras）", "未說明是否只計輸出 token")
add("C11", "支撐該容量的系統台數", "台", [3000, 2000, 1000], "C07（『more than a thousand』／『thousands』）", "Assumed（區間）", "產出低端＝台數多")
add("C12", "每系統吞吐", "tok/s", ["={C10}/{C11}"] * 3, "Derived", "Derived", "")
add("C13", "每 kW 吞吐", "tok/s/kW", ["={C12}/{C2}"] * 3, "Derived", "Derived", "")
add("C14", "÷ GB300 每 kW（MLPerf Llama2-70B Server）", "—", ["={C13}/{B8}"] * 3, "Derived", "Derived（含 Interested-party）", "Cerebras 16-bit、約 450–2,100 tok/s/user；GPU NVFP4、Server SLO", fmt="0.0000")
add("C15", "容量換算的產出比（× GB300 VR-eq 平均）", "—", ["={C14}*{B6}"] * 3, "Derived", "Derived（方向界線）", "在 Cerebras 自己的工作點；TK 三層 55–120 tok/s/user 時 Cerebras 可加大批次，但受 SRAM 容量限制", fmt="0.0000")
add("C16", "TK 現值產出比（0.2／0.4／0.8）需要的 f（(b) 口徑）", "—", ["=0.2/{C5}", "=0.4/{C5}", "=0.8/{C5}"], "Derived", "Derived", ">1 表示超出 FP16 對齊的峰值上限", fmt="0.000")
add("C20", "每系統價格", "$M", [2.5, 3.2, 4.0], "C04（2024 猜 $2.5M）；C03（$3.2M；含 MemoryX、SwarmX $4.0M）", "記者估計（區間）", "高端已含配套，再乘 A10 為重複計算（偏高）")
add("C21", "每 GW 系統台數（以基準功率）", "台", [f"={{A7}}*1000/$E${R['C2']}"] * 3, "Derived", "Derived", "VR200 為 4,052 架")
add("C22", "每 GW IT 設備資本支出", "$B", ["={C21}*{C20}/1000*{A10}"] * 3, "Derived", "Derived", "")
add("C23", "k ＝ ÷ VR200 每 GW IT 資本支出", "—", ["={C22}/{A9}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("C24", "(i) 每 kW 設備價法持有比", "—", ["=1-{A20}*(1-{C23})"] * 3, "Derived", "Derived（記者估價）", "", fmt="0.0000")
add("C30", "OpenAI 合約總值", "$B", same(20), "C05（『more than $20 billion』）", "Interested-party（Cerebras）", "下限值；替代見 F 節（$25.4B）")
add("C31", "合約容量", "MW", same(750), "C05、C06", "Interested-party", "口徑未明（C03 推算為 IT）")
add("C32", "每期年數", "年", [4, 3.5, 3], "C06（three or four years）", "Interested-party（區間）", "欄序：上限低→高")
add("C33", "每 TK GW 年營收（＝每 MW 營收 × 919.8 MW；假設 750 MW 全期滿載）", "$B/年", ["={C30}/{C31}*{A7}/{C32}"] * 3, "Derived", "Derived", "r1：750 MW 為 CS-3 系統 IT 功率（C03），TK 每 GW 含 919.8 MW 機架 IT（同 (i) 法基準）；爬坡期 MW 不滿 ⇒ 實際更高")
add("C34", "(ii) 合約隱含持有比上限 ＝ C33 ÷ VR200 年持有成本", "—", ["={C33}/{A12}"] * 3, "Derived", "Derived（上限，非硬上限）", "營收還要負擔電費、營運與毛利；但 OpenAI 取得認股權（3,345 萬股、行使價近 0）與約 $1B 低息貸款、Q2 2026 GAAP 毛利率 14.2%，合約可能低於成本定價，所以不是硬上限", fmt="0.0000")
add("C35", "兩法差距 ＝ (i) ÷ (ii)", "x", [f"={ref('C24','D')}/{ref('C34','F')}", f"={ref('C24','E')}/{ref('C34','E')}", f"={ref('C24','F')}/{ref('C34','D')}"], "Derived", "Derived", "最接近／基準／最遠", fmt="0.00")

# ---- D. Jalapeño
sec("D. OpenAI／Broadcom Jalapeño（第一代；TSMC N3P；機架未公布）")
add("D1", "每顆 MXFP4 峰值（dense／sparse 未標）", "PF", same(13.4), "O03", "Interested-party（OpenAI）", "")
add("D2", "每顆 FP8 dense 峰值", "PF", same(3.4), "O03", "Interested-party（OpenAI）", "FP4÷FP8＝3.94")
add("D2b", "保守讀法：dense FP4 ＝ 2 × FP8", "PF", ["=2*{D2}"] * 3, "Derived", "Derived", "同 VR200、MI455X 的 2:1（TK GB300 為 3:1，見 D2c）")
add("D2c", "中間讀法：dense FP4 ＝ 3 × FP8（比照 TK GB300 FP4 15 對 FP8 5，Spec_Rack E40／E41）", "PF", ["=3*{D2}"] * 3, "Derived", "Analogy", "r1")
add("D3", "每顆封裝 TDP", "kW", same(0.7), "O03、O04", "Interested-party（OpenAI）", "實測持續 ≤0.55 kW")
add("D4a", "Jalapeño ASIC 機架功率", "kW", same(130), "O09（SemiAnalysis：『the ASIC rack draws 130kW』）", "第三方（SemiAnalysis 單一來源，只作佐證）", "16 Vindaloo 托盤 × 8 顆＝128 顆／架；另 8 個交換托盤")
add("D4b", "主機機架功率（配電）", "kW", same(50), "O09（『roughly 50kW provisioned』）", "第三方（SemiAnalysis，只作佐證）", "假設每 ASIC 機架配 1 個主機機架")
add("D4c", "主機機架功率（實際）", "kW", same(31), "O09（『31kW in production』）", "第三方（SemiAnalysis，只作佐證）", "")
add("D4d", "每 ASIC 機架顆數", "顆", same(128), "O09", "第三方（SemiAnalysis，只作佐證）", "")
add("D4p", "倍數（配電口徑）＝（130＋50）÷（128×0.7）", "x", ["=({D4a}+{D4b})/({D4d}*{D3})"] * 3, "Derived", "Derived", "與 TK VR200 227 kW（配電設計功率）同口徑", fmt="0.000")
add("D4r", "倍數（實際）＝（130＋31）÷（128×0.7）", "x", ["=({D4a}+{D4c})/({D4d}*{D3})"] * 3, "Derived", "Derived", "", fmt="0.000")
add("D4s", "倍數（只算 ASIC 機架）＝130÷（128×0.7）", "x", ["={D4a}/({D4d}*{D3})"] * 3, "Derived", "Derived", "只作對照", fmt="0.000")
add("D4", "機架 ÷ 晶片倍數（產出低／基準／高）", "x", [f"={ref('D4p','E')}", f"={ref('D4r','E')}", f"={ref('B9','E')}"], "低＝配電口徑 2.01；基準＝實際 1.80；高＝TK 四世代平均 1.52", "Analogy（區間；SemiAnalysis 只作佐證）", "r1：r0 為 1.75／1.52／1.35（機架未公布時的 TK 類比）")
add("D5", "每顆所攤機架功率", "kW", ["={D3}*{D4}"] * 3, "Derived", "Derived", "")
add("D6", "(a1) 13.4 為 dense：每 kW 峰值 ÷ VR200（NVFP4）", "—", ["=({D1}/{D5})/{A5}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("D7", "(a2) 保守讀法 6.8 PF：每 kW 峰值 ÷ VR200（NVFP4）", "—", ["=({D2b}/{D5})/{A5}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("D8", "(b) FP8 對齊：每 kW FP8 峰值 ÷ VR200 FP8", "—", ["=({D2}/{D5})/({A21}/{A4})"] * 3, "Derived", "Derived", "＝(a2)", fmt="0.0000")
add("D9", "效率因子 f", "—", [0.5, 0.75, 1.0], "無第三方實測；GPU 世代 0.66–1.04、C 段 AMD 0.66–0.99、B 段 Trn3 0.50–1.04", "Assumed（區間）", "")
add("D10", "方法一 (a1) 產出比 ＝ D6 × D9", "—", ["={D6}*{D9}"] * 3, "Derived", "Derived（含 Assumed）", "", fmt="0.0000")
add("D11", "方法一 (a2)／(b) 產出比 ＝ D7 × D9", "—", ["={D7}*{D9}"] * 3, "Derived", "Derived（含 Assumed）", "", fmt="0.0000")
add("D12a", "OpenAI 自測：DeepSeek R1 Jalapeño 峰值 TPS/kW（封裝 TDP）", "tok/s/kW", same(19641), "O04", "Interested-party（OpenAI）", "")
add("D12b", "同上：GB300", "tok/s/kW", same(11781), "O04", "Interested-party（OpenAI）", "")
add("D12c", "OpenAI 自測：Kimi K2.5 Jalapeño", "tok/s/kW", same(18195), "O04", "Interested-party（OpenAI）", "")
add("D12d", "同上：GB300", "tok/s/kW", same(11862), "O04", "Interested-party（OpenAI）", "")
add("D12e", "記者：對使用 MTP 的 GB300，峰值效率領先約", "x", same(1.5), "O05", "記者推論", "")
add("D12", "每封裝 kW 吞吐比 ÷ GB300", "x", [f"=MIN({ref('D12e','E')},{ref('D12c','E')}/{ref('D12d','E')})", f"=AVERAGE({ref('D12a','E')}/{ref('D12b','E')},{ref('D12c','E')}/{ref('D12d','E')})", f"={ref('D12a','E')}/{ref('D12b','E')}"], "低＝MTP 修正（O05）與 Kimi 取小；基準＝DS-R1、Kimi 平均；高＝DS-R1", "Derived（Interested-party）", "GPT-OSS 只對 GB200（1.9×），不用", fmt="0.000")
add("D13", "改機架功率口徑 ＝ D12 × GB300 倍數 ÷ Jalapeño 倍數", "x", [f"={{D12}}*{ref('B4','E')}/{{D4}}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("D14", "方法二產出比（對照，不進建議值）＝ D13 × GB300 VR-eq 平均", "—", [f"={{D13}}*{ref('B6','E')}"] * 3, "Derived", "Derived（Interested-party＋SemiAnalysis 只作佐證）", "r1：數據由 OpenAI 提供、SemiAnalysis 到場核驗 InferenceX 執行（O09），TechRadar 1.5× 為同批數據改算，非獨立；峰值吞吐點；TK 三層高於此點，Jalapeño 領先更多（O04：50–100×），對 TK 偏保守；GB300 未用 MTP／PD 分離，偏樂觀", fmt="0.0000")
add("D15", "一致性：方法二 ÷ 方法一峰值比 ＝ 隱含 f（(a2)／(a1)）", "—", [f"={ref('D14','E')}/{ref('D7','E')}", f"={ref('D14','E')}/{ref('D6','E')}", ""], "Derived", "Derived", "D＝保守讀法需要的 f；E＝dense 讀法需要的 f", fmt="0.000")
add("D16", "建議產出比（原始；只用方法一，不依賴 InferenceX）", "—", [f"=({ref('D2b','E')}/({ref('D3','E')}*{ref('D4p','E')}))/{ref('A5','E')}*0.75", f"=({ref('D2c','E')}/({ref('D3','E')}*AVERAGE({ref('B9','E')},{ref('D4r','E')})))/{ref('A5','E')}*0.75", f"=({ref('D1','E')}/({ref('D3','E')}*{ref('B9','E')}))/{ref('A5','E')}*1.0"], "低＝6.8 PF、倍數 2.01、f 0.75；基準＝10.2 PF（3:1）、倍數 1.52 與 1.80 的中間、f 0.75；高＝13.4 PF（dense 讀法）、倍數 1.52、f 1.0", "Assumed（區間）", "r1（核對意見 1）：方法二降為對照、不進平均", fmt="0.0000")
add("D20", "Broadcom 每 GW 內容", "$B", [20, 25, 30], "O06（Hock Tan：$20–30B per GW，全部 XPU 客戶）", "Interested-party（Broadcom）", "")
add("D21", "非 Broadcom 內容加成（HBM 若由 OpenAI 自購、CPU、ODM 整合）", "x", [1.0, 1.15, 1.35], "O07（Samsung HBM 直供報導，方向）", "Assumed（區間）", "")
add("D22", "GW 口徑換算（若為設施 GW → 每 IT GW × PUE）", "x", [1.0, 1.0, 1.25], "O01、O06 未說明口徑", "Assumed", "")
add("D23", "每 IT GW 設備資本支出", "$B", ["={D20}*{D21}*{D22}"] * 3, "Derived", "Derived", "")
add("D24", "k ＝ ÷ VR200", "—", ["={D23}/{A9}"] * 3, "Derived", "Derived", "", fmt="0.000")
add("D25", "持有比界線", "—", ["=1-{A20}*(1-{D24})"] * 3, "Derived", "Derived（界線）", "TK 現值 0.7／0.8／1.0 落在界線內", fmt="0.0000")
add("D26", "對照：Rasgon $11.5B/GW（只作下界）", "—", same("=1-{A20}*(1-11.5/{A9})"), "O06", "分析師推論", "", fmt="0.0000")

# ---- F. 敏感度
sec("F. 敏感度（一次動一個參數；D＝參數低值對應結果，F＝高值）")
add("F1", "Cerebras (ii) 改用剩餘履約義務全數 $25.4B", "持有比上限", [f"=25.4/{ref('C31','E')}*{ref('A7','E')}/{{C32}}/{ref('A12','E')}"] * 3, "C06", "Derived", "Q2 替代 c", fmt="0.0000")
add("F2", "Cerebras (b) 口徑 × f 0.5／0.75／1.0", "產出比", [f"={ref('C5','E')}*0.5", f"={ref('C5','E')}*0.75", f"={ref('C5','E')}*1.0"], "Derived", "Derived", "Q1 替代 a", fmt="0.0000")
add("F3", "Jalapeño 方法一基準（10.2 PF、f 0.75）改倍數 2.01／1.80／1.52", "產出比", [f"=({ref('D2c','E')}/({ref('D3','E')}*{ref('D4p','E')}))/{ref('A5','E')}*0.75", f"=({ref('D2c','E')}/({ref('D3','E')}*{ref('D4r','E')}))/{ref('A5','E')}*0.75", f"=({ref('D2c','E')}/({ref('D3','E')}*{ref('B9','E')}))/{ref('A5','E')}*0.75"], "Derived", "Derived", "Q5", fmt="0.0000")
add("F4", "Jalapeño 方法二改用 GB300 Astra 層 VR-eq（0.564）", "方法二產出比", [f"={ref('D13','E')}*{ref('B5','F')}"] * 3, "Derived", "Derived", "", fmt="0.0000")
add("F5", "Jalapeño 以持續功率 0.55 kW（而非 TDP）計", "方法一 (a2) 基準", [f"=({ref('D2b','E')}/(0.55*{ref('D4','E')}))/{ref('A5','E')}*{ref('D9','E')}"] * 3, "O03", "Derived", "OpenAI 正規化用 TDP，對 Jalapeño 偏保守", fmt="0.0000")
add("F6", "Jalapeño B0 每瓦 +25%（2027 爬坡，OpenAI 自述）", "方法二產出比", [f"={ref('D14','E')}*1.25"] * 3, "O03（TechRadar）", "Interested-party", "只作上行參考", fmt="0.0000")

for col, w in zip("ABCDEFGHI", [8, 58, 12, 12, 12, 12, 50, 28, 60]):
    ws.column_dimensions[col].width = w
for r in range(5, row[0]):
    for c in (4, 5, 6):
        cell = ws.cell(r, c)
        if cell.number_format == "General" and ws.cell(r, 3).value in ("—", "PF/kW", "x", "kW"):
            cell.number_format = "0.0000"
    for c in (7, 8, 9):
        ws.cell(r, c).alignment = WRAP
ws.freeze_panes = "D5"

# ---------------------------------------------------------------- 建議值
sv = wb.create_sheet("建議值", 0)
sv["A1"] = "建議值 — NonNV 第 8 列（Cerebras）與第 9 列（OpenAI 客製）｜D 段唯讀查證，未寫入 model/"
sv["A1"].font = BOLD
sv["A2"] = ("第 4–8 列＝推導頁公式的原始結果或界線；第 11–12 列＝建議輸入值；第 15–16 列＝TK v21.7 現值。"
            "H＝F÷C（每 token 成本比）、I＝E÷D（最佳角落）、J＝G÷B（最差角落），同 NonNV。")
sv["A2"].alignment = WRAP
cols = ["候選", "產出比 低", "產出比 基準", "產出比 高", "持有比 低", "持有比 基準", "持有比 高", "每 token 成本比 基準", "最佳角落", "最差角落", "標記", "說明"]
for i, h in enumerate(cols, 1):
    c = sv.cell(3, i, h)
    c.font = BOLD
    c.fill = HDR


def ratio_cols(r):
    sv[f"H{r}"] = f"=F{r}/C{r}"
    sv[f"I{r}"] = f"=E{r}/D{r}"
    sv[f"J{r}"] = f"=G{r}/B{r}"


raw = [
    ("Cerebras：(b) FP16 對齊每 kW 峰值比（f＝1 上限）／(i) 每 kW 設備價法持有比", "C5", "C24", "方向界線；不建議作輸入"),
    ("Cerebras：容量換算產出比／(ii) 合約隱含持有比上限", "C15", "C34", "方向界線；持有比為上限"),
    ("Jalapeño：方法一 (a2) 保守讀法／持有比界線", "D11", "D25", ""),
    ("Jalapeño：方法二（OpenAI 自測；對照）／持有比界線", "D14", "D25", "不進建議值"),
    ("Jalapeño：推導區間（只用方法一）／持有比界線", "D16", "D25", "寫入第 9 列說明欄，數值不改"),
]
for k, (nm, o, h, note) in enumerate(raw):
    r = 4 + k
    sv.cell(r, 1, nm)
    for col, src in zip("BCD", "DEF"):
        sv[f"{col}{r}"] = f"=推導!{src}{R[o]}"
    for col, src in zip("EFG", "DEF"):
        sv[f"{col}{r}"] = f"=推導!{src}{R[h]}"
    ratio_cols(r)
    sv[f"L{r}"] = "公式（連結推導頁）" + ("；" + note if note else "")
sv["A10"] = "建議輸入值（r1：兩列皆維持 TK 現值；Cerebras 見 Q3 預設，OpenAI 客製為 Project 決定 Q6、Q8）"
sv["A10"].font = BOLD
sv["A11"] = "Cerebras WSE-3（維持慣例值）"
sv["A12"] = "OpenAI／Broadcom 客製（Jalapeño；維持慣例值，Project 決定）"
for r, vals in ((11, (0.2, 0.4, 0.8, 0.8, 1.0, 1.2)), (12, (0.4, 0.6, 0.9, 0.7, 0.8, 1.0))):
    for j, v in enumerate(vals):
        sv.cell(r, 2 + j, v).font = BLUE
    ratio_cols(r)
    sv[f"K{r}"] = "Assumed"
sv["L11"] = ("數值不改。每 kW 法不適用（瓶頸為 44 GB SRAM 容量，每 kW 記憶體只有 VR200 的約 2%）；產出方向界線：FP16 對齊每 kW 峰值比 0.36–0.43（f≤1 上限）、Cerebras 自述容量換算約 0.04–0.13，前者只與現值基準相當、後者遠低於，現值高端 0.8 超出全部證據。"
             "持有比兩法衝突：記者估價（$2.5–4.0M／台、23 kW）→ 約 2.5–3.9；OpenAI 合約（>$20B、750 MW、3–4 年，對齊 919.8 MW）→ 上限約 0.50–0.67（合約可能低於成本定價，非硬上限）。證據：docs/evidence/20261025_NonNV_Cerebras_OpenAI。")
sv["L12"] = ("r1（Project 決定 Q6、Q8）：數值不改。推導區間 0.35／0.60／1.15（只用方法一：Jalapeño MXFP4 13.4 PF（dense 未標）、FP8 dense 3.4 PF、封裝 TDP 700 W；機架 128 顆、ASIC 機架 130 kW＋主機機架 50 kW 配電（31 kW 實際）→ 倍數 2.01／1.80，SemiAnalysis 單一來源；f 0.75–1.0 Assumed）；"
             "OpenAI 自測 InferenceX（每封裝 kW 對 GB300 1.5–1.7×）只作對照。持有比維持（Broadcom 每 GW 內容 $20–30B 推得界線 0.64–1.27）。證據：docs/evidence/20261025_NonNV_Cerebras_OpenAI。")
for r in (11, 12):
    sv[f"L{r}"].alignment = WRAP
sv["A14"] = "TK v21.7 現值（NonNV 第 8、9 列；慣例值、未推導）"
sv["A14"].font = BOLD
sv["A15"] = "Cerebras WSE-3（現值）"
sv["A16"] = "OpenAI／Broadcom 客製（現值）"
for r, vals in ((15, (0.2, 0.4, 0.8, 0.8, 1.0, 1.2)), (16, (0.4, 0.6, 0.9, 0.7, 0.8, 1.0))):
    for j, v in enumerate(vals):
        sv.cell(r, 2 + j, v)
    ratio_cols(r)
    sv[f"K{r}"] = "Assumed"
    sv[f"L{r}"] = f"model/20261025_Tokenomics_v21.7.xlsx NonNV!B{r - 7}:G{r - 7}"

sv["A18"] = "與 A–C 段並排（每 kW 峰值比為各自最高原生精度；建議值或 TK v21.7 現值）"
sv["A18"].font = BOLD
for i, h in enumerate(["候選", "每 kW 峰值 ÷ VR200（基準）", "產出比 基準", "持有比 基準", "每 token 成本比", "來源"], 1):
    c = sv.cell(19, i, h)
    c.font = BOLD
    c.fill = HDR
side = [
    ("Cerebras CS-3（本段；維持）", f"=推導!E{R['C4']}", "=C11", "=F11", "本段：(a) FP16 對 NVFP4；(b) FP16 對齊 0.43"),
    ("OpenAI Jalapeño（本段；維持）", f"=推導!E{R['D7']}", "=C12", "=F12", "本段：保守讀法（倍數 1.80）；10.2 PF 時 0.73、13.4 PF dense 時 0.96"),
    ("AMD MI455X（C 段）", 1.066, 0.80, 0.85, "TK v21.7 NonNV 第 5 列"),
    ("Google TPU v7（B 段）", 0.383, 0.80, 0.70, "TK v21.7 第 6 列（產出比仍慣例值；B 段建議 0.35）"),
    ("AWS Trainium3（B 段）", 0.176, 0.50, 0.61, "TK v21.7 第 7 列（產出比仍慣例值；B 段建議 0.14）"),
    ("Microsoft Maia 200（A 段）", 0.676, 0.55, 0.50, "TK v21.7 第 11 列"),
    ("華為昇騰 910C（A 段）", 0.093, 0.08, 0.55, "TK v21.7 第 10 列"),
]
for k, (nm, pk, ob, hb, src) in enumerate(side):
    r = 20 + k
    sv.cell(r, 1, nm)
    sv.cell(r, 2, pk)
    sv.cell(r, 3, ob)
    sv.cell(r, 4, hb)
    sv.cell(r, 5, f"=D{r}/C{r}")
    sv.cell(r, 6, src)
    if not isinstance(pk, str):
        for cc in (2, 3, 4):
            sv.cell(r, cc).font = BLUE
for r in range(4, 27):
    for c in range(2, 11):
        cell = sv.cell(r, c)
        if cell.number_format == "General":
            cell.number_format = "0.000"
for col, w in zip("ABCDEFGHIJKL", [44, 12, 11, 11, 11, 11, 11, 14, 10, 10, 10, 90]):
    sv.column_dimensions[col].width = w

# ---------------------------------------------------------------- 證據
ev = wb.create_sheet("證據")
eh = ["編號", "主張", "數值", "單位", "口徑", "出處網址", "來源等級", "立場", "標記", "取得方式與備註", "用於"]
for i, h in enumerate(eh, 1):
    c = ev.cell(1, i, h)
    c.font = BOLD
    c.fill = HDR
for rr, rowv in enumerate(EVIDENCE, 2):
    for cc, v in enumerate(rowv, 1):
        ev.cell(rr, cc, v).alignment = WRAP
for col, w in zip("ABCDEFGHIJK", [6, 60, 22, 14, 30, 56, 18, 12, 24, 52, 12]):
    ev.column_dimensions[col].width = w
ev.freeze_panes = "C2"

# ---------------------------------------------------------------- 待判斷
qd = wb.create_sheet("待判斷")
for i, h in enumerate(["編號", "題目", "預設（本提案採用）", "替代方案", "影響"], 1):
    c = qd.cell(1, i, h)
    c.font = BOLD
    c.fill = HDR
for rr, rowv in enumerate(QUESTIONS, 2):
    for cc, v in enumerate(rowv, 1):
        qd.cell(rr, cc, v).alignment = WRAP
for col, w in zip("ABCDE", [6, 50, 55, 55, 36]):
    qd.column_dimensions[col].width = w

wb.save(out)
print("saved", out, "rows", row[0])

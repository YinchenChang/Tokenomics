"""產生 builder/v1400_data.json（4-3 B 段，v14.0）：刪除清單與『保留：顯示用』用途標記。
用法：python3 tools/gen_v1400_data.py            讀 docs/reports/20261017_4-3A_建議_明細.xlsx「1_逐列建議」，寫出 builder/v1400_data.json
輸入：A 段明細（唯讀）。處置＝刪除者進刪除清單（72 列）加 Har_In 44（Andy 2026-10-17 09:18 決定刪除）；處置＝保留：顯示用者（155 列）進標記表，
用途文字由本檔的 SHORT 表依 A 段『理由』開頭比對後擬寫（CC 擬寫，報告附清單供 Andy 抽查）。
注意：不改任何模型內容；builder/v1400.py 只讀這個 JSON。"""
import json
import sys
from pathlib import Path

import openpyxl

REPO = Path(__file__).resolve().parents[1]
DETAIL = REPO / "docs" / "reports" / "20261017_4-3A_建議_明細.xlsx"
OUT = REPO / "builder" / "v1400_data.json"

# A 段『理由』開頭（前 14 字）→ 用途標記的括號內文字。順序無關；找不到對應者（RuntimeError）要補表，不得退回通用字樣。
SHORT = {
    "規格表列（Scale-up": "規格表列（Gov_Map 登錄 SRC_HW_053）；不進任何輸出",
    "roofline 推導鏈的讀數": "roofline 推導鏈讀數（ridge point＝峰值÷頻寬）；建模精神 1a 要求露出推導鏈",
    "架構規格列（vocab＝": "架構規格列（Gov_Map 登錄 SRC_MOD_014）；不進任何輸出",
    "掛鉤彙總表（E20–E29": "掛鉤彙總表的一致讀數（H_HAR 的實際作用在 Workload 的 B5_W）",
    "記憶體配置（E 節）的讀數": "記憶體配置讀數（權重／KV 占可用 HBM）；與 Perf_Batch 同列鏡像（D13 常設測試的比對對象）",
    "P:D 配比（prefill G": "P:D 配比讀數（DRV_PreShare）；Perf 第 118 列讀它；與 Perf_Batch 鏡像",
    "每 GW decode 產出：to": "每 GW decode 產出讀數（下游用 IF_TokRackD_*）；與 Perf_Batch 鏡像（D13）",
    "每 decode token 實際能量": "能量閉合（J 節）讀數；與 Perf_Batch 鏡像",
    "敏感度頁（Sensitivity": "核心列：Sensitivity 有同列同標籤的列，常設測試以此為逐格比對基準；下游用 IF_Capex*／IF_HoldEcon／IF_AvgDraw",
    "成本結構讀數（資本回收占經濟": "成本結構讀數（資本回收、電費占經濟口徑）；下游以 IF_Depr*／IF_PowerCost 自算",
    "RL 占比的外部對照": "RL 占比的外部對照（R1、Grok 4 宣稱值）；Gov_Map 登錄，Checks 第 157–158 列取用",
    "R–S 欄（VR200 以 FP8": "R–S 欄（FP8 rollout 未接線情境）的 H_WB 讀取；與其餘 R–S 列同標記",
    "與 Perf 逐列鏡像（D13；": "與 Perf 逐列鏡像（D13 常設測試的比對對象）；Training 只取其中幾列",
    "能量閉合（J 節）的逐步讀數": "能量閉合（J 節）逐步讀數；不進 Checks；與 Perf 逐列鏡像（D13）",
    "Perf_Batch 專屬閱讀列": "Perf_Batch 專屬閱讀列（D13 白名單）：decode 有效 MFU，解讀 IF_RLMFU_* 為何偏低",
    "敏感度頁（Sens_Train": "核心列：Sens_Train 有同列同標籤的列，常設測試以此為逐格比對基準；下游用 IF_TrainCost_*／IF_ProgCost_*",
    "RL ÷ 預訓練（FLOPs 口徑": "RL ÷ 預訓練（FLOPs 口徑，TRN_RLRatioF）；與 GPU 小時口徑並列，對照 Grok 4 宣稱值",
    "『其中：研發實驗（型態未拆分": "K 節『用途×型態』表的上游（研發實驗，型態未拆分）",
    "K 節『用途×型態』GPU": "K 節『用途×型態』GPU 小時表的一列；各列合計等於 IF_TrainGPUh 與 IF_ProgGPUh",
    "H1 營收二分（訂閱／API）": "H1 營收二分（訂閱／API）：第 96 列與 J11 對照的分子；與 H8-1 三分法口徑不同（設計）",
    "H2 訂閱人數（SRC_DEM": "H2 訂閱人數（SRC_DEM 複本與 2025 期間平均）：每人直覺檢查與 ARPU 的上游",
    "H5 兩路線隱含 m": "H5 兩路線隱含 m（v5.32 舊分法對照）；主口徑為 H8-3 三分法 L1_MSub／MAPI／MSeat",
    "H6 程式代理對照鏈": "H6 程式代理對照鏈：第 103 列『程式代理訂閱 m』對照的上游",
    "說明欄的動態文字公式": "說明欄動態文字公式（TEXT() 帶出現值，取代寫死的過時數字；原則 2）",
    "『必須為真』補列（m＝1": "『必須為真』補列（m＝1／0.6／0.3 所需付費 token）：反向檢查（v5.33 B3）",
    "J11 非文字服務份額": "J11 非文字服務份額對照（敏感度讀數；Assumed 0.05／0.10／0.20）",
    "H8-6 『必須為真』": "H8-6『必須為真』補列（訂閱 ARPU；m_訂閱＝1 所需每訂閱者年 token）",
    "H9 token 帳三路線": "H9 token 帳三路線的上限路線（與 L1_TokCeiling 同值）；供第 175 列",
    "閉合解標題的動態文字": "閉合解標題動態文字（TEXT() 帶出 τ* 現值）",
    "說明欄動態文字（現值取代": "說明欄動態文字（現值取代過時數字）",
    "I-7 『必須為真』": "I-7『必須為真』：回本所需 L 以 m＝L1_MAPI 計；契約已定恆等式讀法 L1_LReqFleet_Id，第三種讀法留作對照",
    "說明動態文字（現值取代": "說明動態文字（現值取代過時數字）",
    "缺口恆等式的說明動態": "缺口恆等式說明動態文字（現值取代過時數字）",
    "機隊口徑單價 ÷ 完整層級": "機隊口徑單價 ÷ 完整層級組合單價：顯示排除不可達層級對單價的影響",
    "說明動態文字（v7.0": "說明動態文字（v7.0 歷史值標示為歷史，現值隨公式）",
    "前緣模型的新鮮輸入": "前緣分項牌價（新鮮輸入／快取輸入／輸出）：B 節前緣表的形狀；下游用 IF_FrontRef_*（混合）",
    "中國廠商合格者最低": "中國廠商合格者最低（模型名、合格家數）：與已標用途的第 31、33 列同組對照",
    "A 節用途配置（最終訓練": "A 節用途配置（最終訓練、研發實驗各占 1 GW 多少）：研發占總算力的參考讀數",
    "排除層級（SLO 不可達者": "排除層級（SLO 不可達者）的文字讀數：D 節可達旗標的人讀摘要",
    "由上而下 ÷ 自下而上攤提": "由上而下 ÷ 自下而上攤提：K6 兩種攤提口徑的比值（選預設口徑 (c) 的依據）",
    "回本所需溢價 ÷ 觀測層級": "回本所需溢價 ÷ 觀測層級價差：層級版回本讀數（<1＝觀測價差足以回本）",
    "年持有成本複本（IF_Hold": "年持有成本複本（IF_HoldEcon）：同表『營收 ÷ 持有成本』比值列的分母",
    "理論營收（OpenAI／前緣單價": "理論營收 ÷ 持有成本：回本讀數，與已標用途的第 33、73 列同族",
    "全成本 $/M（服務＋由上": "全成本 $/M（服務＋由上而下攤提）：K6 三口徑並列中非預設的一支",
    "理論毛利率的非預設口徑": "理論毛利率非預設口徑（自下而上、由上而下、前緣單價）：K6 並列比較；預設口徑為 IF_GMDefault_*",
    "整個 GW 年持有成本複本": "整個 GW 年持有成本複本：第 73 列的分母",
    "任務名稱欄頭（＝Workl": "任務名稱欄頭（＝Workload 第 4 列）：讓 C 節成功率表可讀",
    "E 節證據點中非中立方": "E 節證據點（非中立方或非同條件）：只作對照；Gov_Map／SRC 登錄",
    "GB300 孿生區塊": "GB300 孿生區塊（與 VR200 區塊同構）：第 149–150 列讀取；下游取 IF_CostSuccGB_*",
}
HAR_IN_44 = ("Har_In", 44, "供應商專屬（1＝是）", "C44:G44")      # Andy 2026-10-17 09:18


def main():
    ws = openpyxl.load_workbook(DETAIL)["1_逐列建議"]
    rows = [r for r in ws.iter_rows(min_row=3, values_only=True) if r[0]]
    delete, marks, unknown = [], {}, []
    for r in rows:
        sh, row, lab, rng, disp, reason = r[0], r[1], r[2], r[5], r[7], r[10] or ""
        if disp == "刪除":
            delete.append(dict(sheet=sh, row=row, range=rng, label=lab))
        elif disp == "保留：顯示用":
            hit = [v for k, v in SHORT.items() if reason.startswith(k)]
            if len(hit) != 1:
                unknown.append((sh, row, reason[:40], len(hit)))
                continue
            marks.setdefault(sh, {})[str(row)] = f"顯示用：{rng}（{hit[0]}）"
    if unknown:
        raise RuntimeError(f"用途文字表缺項或重複：{unknown}")
    delete.append(dict(sheet=HAR_IN_44[0], row=HAR_IN_44[1], range=HAR_IN_44[3], label=HAR_IN_44[2]))
    data = dict(source=str(DETAIL.relative_to(REPO)), delete=delete, marks=marks)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("刪除列", len(delete), "標記列", sum(len(v) for v in marks.values()), "頁", len(marks))


if __name__ == "__main__":
    sys.exit(main())

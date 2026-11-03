"""產生 builder/v2180_evidence.json（v21.8 DB_Evidence 115 列：E412–E475、E476–E507、E540–E558）。

用法：python3 tools/gen_v2180_data.py
來源：docs/evidence/20261101/candidates.csv、docs/evidence/20261102_財報季/candidates_q3.csv、candidates_other.csv。
判定與狀態依工作單 docs/workorders/20261102_v21.8_財報季與月度證據.md 第 1 節與第 3 節第 3 點（本檔只做欄位對應，不做判斷；
工作單沒寫到的「並列（無 Alt 紀錄、無工作單動作）」者標「已處理」，E439、E475 因候選列自寫有後續動作標「待判定」，列報告待 Project 判斷）。
builder 不讀 docs/（chat 端與 CC 共用同一份 builder），所以先轉成 JSON 放在 builder/。"""
import csv
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRCS = [("docs/evidence/20261101/candidates.csv", "20261101 月度證據"),
        ("docs/evidence/20261102_財報季/candidates_q3.csv", "20261102 財報季（MSFT、GOOGL、AMZN、META、SpaceX）"),
        ("docs/evidence/20261102_財報季/candidates_other.csv", "20261102 財報季（其他公司）")]
OUT = REPO / "builder" / "v2180_evidence.json"
WO = "工作單 docs/workorders/20261102_v21.8_財報季與月度證據.md（r0）"

# ---- 工作單第 1 節定案（判定欄文字）與受影響名稱
FINAL = {
    "E467": ("採用：SRC_DC_008 4 → 5（1-A；高成本情境 IT 折舊年限；縮窄 1）", "IF_HoldEcon*、IF_DeprLifeIT、IF_FullCost_*、IF_Amort* 等的高成本欄（E、H、K、N、Q）；L1_*_Hi 與對應 _Lo 毛利名稱"),
    "E445": ("不改值；SRC_HW_030、SRC_HW_049 備註登錄（1-B；待正式 datasheet）", None),
    "E438": ("本版不改；A 段（唯讀查齊 Cap_In F 節 13 模型 v5.0 分數）排 12-01 月度（1-C）", None),
    "E462": ("本版不改；併 1-C（12-01 月度）", None),
    "E507": ("本版不改；併 1-C（12-01 月度）", None),
    "E450": ("不改值：Spec_Rack!E13 高端已是 5.0；新增 Alt 紀錄登錄為高端佐證（1-D）", None),
    "E550": ("不改值：4.3 × 1.15–1.17＝4.95–5.03 落在高端 5.0；新增 Alt 紀錄登錄為高端佐證（1-D；只適用 2027 起出貨）", None),
    "E455": ("延一月（1-E）", None),
    "E464": ("延一月（1-F）", None),
    "E428": ("採用：新增 MiniMax M3 快取輸入 0.06 紀錄，Cap_In!F58 改連結（1-G；只影響候選表）", "—（Price_Frontier 候選表 MiniMax 列；不影響 IF_／L1_）"),
    "E424": ("只補 SRC_PRC_028 備註（1-H）", None),
    "E452": ("採用：SRC_DC_004 指標名更正為「AI 資料中心對傳統建造溢價（Turner & Townsend）」（修訂九，原字樣保留）；新增 Alt「JLL 液冷溢價」只對照（1-I）", None),
    "E415": ("併 1-C（1-J；Alt 牌價紀錄已登錄，是否入 Cap_In F 節待 v5.0 分數）", None),
    "E421": ("併 1-C（1-J；Alt 牌價紀錄已登錄，是否入 Cap_In F 節待 v5.0 分數）", None),
    "E463": ("不改，備註登錄（1-K）", None),
    "E470": ("不改，備註登錄並填第二來源；排入下次 η 校準（1-L）", None),
    "E482": ("並列：AL_SpendBasis 1.8（0.85–2.3）不改；登錄為 2026Q3 短約現貨上緣錨點（Q3-1）", None),
    "E494": ("不新增 NonNV 列；列事件觸發清單（Maia 300 出貨、規格或第三方實測）（Q3-2）", None),
    "E476": ("採用（值不變）：新增 SRC_DC_023 並填入 SRC_DC_007 第二來源欄；Inputs!H23 說明改寫（Q3-3）", None),
    "E488": ("採用（新增 Alt）：Google API 32 B tok/min 與 SRC_DEM_011 並列；不連結模型格（Q3-4）", None),
}
ADOPT_V218 = {"E413", "E417", "E418", "E419", "E420", "E427", "E429", "E442", "E443", "E444", "E448", "E451", "E454",
              "E456", "E457", "E458", "E459", "E460", "E466", "E469", "E447", "E449", "E453", "E468", "E472",
              "E470", "E467", "E428", "E424", "E452", "E445", "E463", "E476", "E488", "E482", "E494", "E450"}
ALT_REG = {"E430", "E431", "E432", "E434", "E425", "E483", "E544", "E545", "E546", "E552", "E553"}
PENDING_1201 = {"E438", "E462", "E507", "E415", "E421", "E455", "E464"}
PENDING_OTHER = {"E439": "候選列寫明依 docs/evidence/20261026_Anthropic_S1 S4 處理（SRC_DEM_034–036 升 1 級），不在本工作單",
                 "E475": "候選列寫明 SRC_PERF_009／010／014／015 待 chat 端核對 dashboard，不在本工作單"}
# 本版新增的 SRC 紀錄（相關 SRC_ID 欄補上）
NEW_SRC = {"E428": ["SRC_PRC_051"], "E476": ["SRC_DC_023"], "E488": ["SRC_DEM_091"], "E450": ["SRC_HW_100"], "E550": ["SRC_HW_101"],
           "E451": ["SRC_DC_024"], "E452": ["SRC_DC_024"], "E430": [f"SRC_PRC_{i:03d}" for i in range(52, 57)],
           "E431": [f"SRC_PRC_{i:03d}" for i in range(57, 62)], "E432": ["SRC_PRC_062", "SRC_PRC_063"], "E434": ["SRC_PRC_064", "SRC_PRC_065"],
           "E415": ["SRC_PRC_066", "SRC_PRC_067", "SRC_PRC_068"], "E421": ["SRC_PRC_069", "SRC_PRC_070"],
           "E425": ["SRC_PRC_071", "SRC_PRC_072", "SRC_PRC_073"], "E483": ["SRC_PRC_074"], "E544": ["SRC_PRC_075"], "E545": ["SRC_PRC_076"],
           "E546": ["SRC_PRC_077"], "E552": ["SRC_HW_102"], "E553": ["SRC_DC_025", "SRC_DC_026", "SRC_DC_027"],
           "E468": ["SRC_MOD_107"], "E469": ["SRC_PERF_037", "SRC_PERF_086"], "E470": ["SRC_PERF_087"], "E472": ["SRC_DEM_092"]}


def status(eid, verdict):
    if eid == "E550":
        return "已處理（高端 5.0 已涵蓋，1-D）"
    if eid in PENDING_1201:
        return "待判定（12-01 月度）"
    if eid in PENDING_OTHER:
        return "待判定"
    if eid in ADOPT_V218:
        return "已處理（v21.8）"
    return "已處理"


def src_ids(text):
    out = []
    for m in re.finditer(r"SRC_([A-Z]+)_(\d{3})", text):
        pre = f"SRC_{m.group(1)}_"
        out.append(pre + m.group(2))
        tail = re.split(r"SRC_|；|→", text[m.end():])[0]          # bare continuations: "SRC_HW_019（989）、020（80）"
        for n in re.findall(r"(?:^|[、／])(\d{3})(?![\d.])", tail):
            out.append(pre + n)
    for m in re.finditer(r"(?<![A-Z_])(PRC|HW|DC|MOD|PERF|DEM|CAP)_(\d{3})", text):
        sid = {"PRC": "SRC_PRC_", "HW": "SRC_HW_", "DC": "SRC_DC_", "MOD": "SRC_MOD_", "PERF": "SRC_PERF_", "DEM": "SRC_DEM_", "CAP": "SRC_CAP_"}[m.group(1)] + m.group(2)
        out.append(sid)
    seen, res = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); res.append(s)
    return res


def grade(mark):
    m = re.search(r"(\d) 級", mark)
    return int(m.group(1)) if m else "—"


def stance(mark):
    if "Interested-party" in mark:
        return "利害關係方"
    if "中立" in mark:
        return "中立"
    if "Analogy" in mark:
        return "Analogy"
    if "Derived" in mark:
        return "Derived"
    if "Verified" in mark:
        return "中立"
    return "—"


def main():
    rows = []
    for path, label in SRCS:
        for x in list(csv.reader(open(REPO / path, encoding="utf-8-sig")))[1:]:
            eid, date, claim, src, mark, param, cur, new, verdict, reason = x[:10]
            fin, affected = FINAL.get(eid, (verdict, None))
            ids = src_ids(param)
            for s in NEW_SRC.get(eid, []):
                if s not in ids:
                    ids.append(s)
            note = reason
            if eid in FINAL:
                note += f"｜候選建議：{verdict}"
            if eid in PENDING_OTHER:
                note += f"｜{PENDING_OTHER[eid]}"
            note += f"｜{label}：{path}｜{WO}"
            rows.append([eid, date, claim, src, mark, param, cur or "—", new or "—", fin, "v21.8", note, status(eid, verdict),
                         "、".join(ids) if ids else "—", "—", affected or "—", grade(mark), stance(mark), f"{fin}｜v21.8 新增列"])
    assert len(rows) == 115, len(rows)
    ids = [r[0] for r in rows]
    assert ids == sorted(ids, key=lambda s: int(s[1:])) and len(set(ids)) == 115
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", OUT, len(rows))


if __name__ == "__main__":
    main()

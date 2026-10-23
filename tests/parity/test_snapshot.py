"""4-2a F5（查核 D 第 4 項）：契約名稱快照、驗證清單逐項斷言、GOV 三項計數（新基準）。
讀 LibreOffice 重算後的值（`lo.view({})`，即新 SLO 基準；其他測試的 `_vo` 會改回舊 SLO，所以 GOV 計數在新基準下需要在這裡斷言）。

快照更新規則：之後每個版本若有預期變動，必須在同一個 PR 以 `python3 tools/make_test_fixtures.py <重算後的 xlsx>` 更新
tests/parity/fixtures/contract_snapshot_v21.0.json，並在報告列出差異（名稱、舊值、新值、理由）。不得為了讓測試通過而更新快照。"""
import json
import re
from pathlib import Path

import pytest
from openpyxl.utils import get_column_letter as L, range_boundaries

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAP = json.loads((FIXTURES / "contract_snapshot_v21.0.json").read_text(encoding="utf-8"))
ROOT_PREFIX = ("IF_", "L1_", "GOV_", "IFW_", "IFC_", "CHK_", "CAP_", "RNG_", "AL_Rng")      # v13.0 K2：RNG_*（批次口徑區間端點）與 AL_Rng*（v12.0 區間表）全部納入快照


def _cells(attr):
    out = []
    for part in attr.lstrip("=").split(","):
        sh, rg = part.rsplit("!", 1)
        sh = sh.strip("'").replace("''", "'")
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        out += [(sh, f"{L(c)}{r}") for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
    return out


def _same(a, b):
    a = None if a == "" else a
    b = None if b == "" else b
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


def test_contract_snapshot_values(lo):
    """契約名稱（下游契約文件所列＋全部 IF_／IFW_／IFC_／L1_／GOV_／CHK_／CAP_）逐格值等於 v14.0 快照（相對容差 1e-9）。"""
    v = lo.view({})
    bad, ncell = [], 0
    for name, rec in SNAP["names"].items():
        assert name in v.names, f"快照中的名稱已不存在：{name}（契約名稱不得刪除）"
        assert v.names[name] == rec["ref"], (name, v.names[name], rec["ref"])
        cells = _cells(rec["ref"])
        assert len(cells) == len(rec["values"]), name
        for (sh, a), want in zip(cells, rec["values"]):
            got = v.get(sh, a)
            ncell += 1
            if not _same(got, want):
                bad.append((name, f"{sh}!{a}", want, got))
    assert ncell == SNAP["n_cells"]
    assert bad == [], (len(bad), bad[:12])


def test_snapshot_covers_every_prefix_name(lo):
    """新增的 IF_／IFW_／IFC_／L1_／GOV_／CHK_／CAP_／RNG_／AL_Rng 名稱必須同時加進快照（避免新名稱沒有人看守）。"""
    v = lo.view({})
    cur = {n for n, t in v.names.items() if n.startswith(ROOT_PREFIX) and "!" in t}
    missing = sorted(cur - set(SNAP["names"]))
    assert missing == [], missing


# 驗證清單 V1–V26（v14.0 4-3B Q4 新增 V23–V26）：模型 ÷ 對照（或模型值）與通過判定（v10.3 的 LibreOffice 重算值；列 E＝比值，F＝1 通過／0 失敗）。
# 數值與判定隨輸入改變；預期變動時在同一個 PR 更新此表並於報告列出（同快照規則）。
# v19.1：V9、V25 的比值隨 Arch!C17（Luna 跨度上限 4224 → 2176）改變；通過／失敗旗標不變（預期變動，工作單 W1 B2）
VERIFY_EXPECTED = {
    "V1": (1.21767628625269, "警示"), "V2": (0.824029673269705, 1), "V3": (0.904516154853064, 1), "V4": (0.702796711119185, 1),
    "V5": (0.567645607597399, 1), "V6": (0.689214136000581, 1), "V7": (0.267266126717592, 0), "V8": (0.30021418455033, 0),
    "V9": (0.321858869939, 0), "V10": (0.371397626434424, 0), "V11": (0.7, 0), "V12": (0.99108369917347, 1),
    "V13": (2.18428412747673, 1), "V14": (4.49289494127437, 0), "V15": (0.266287875672857, 0), "V16": (0.0852702650102943, "恆等式（非驗證）"),
    "V17": (0.252262860133895, 1), "V18": (0, "恆等式（非驗證）"), "V19": (0, 1),      # v12.0 H7：V18 改標恆等式（F 欄為文字，不計入驗證）；V19 的 E＝（T 欄與重算判定不符列數）＋實質不一致列數＝0
    "V20": (1.25405497807807, "校準相關（非獨立）：帶內"), "V21": (0.645585696466193, 1), "V22": (0.501000545281522, 1),
    "V23": (0, "恆等式（非驗證）"), "V24": (0, "恆等式（非驗證）"), "V25": (0.217680639842559, 1), "V26": (0, 1),      # v14.0（4-3B Q4）新增：V23 實際速度 ≥ SLO（低於 SLO 的可達欄數）、V24 Cap_In 147＝L1_MImplied（最大絕對差）、V25 需求÷上限（Cap_In 175 最大值）、V26 2026 世代組合合計（最大絕對差）；v14.1 R2：V23、V24 改標恆等式（F 欄為文字，不計入驗證）
         # v11.0 G3 新增；v12.0 H2：V20 比值 1.563 → 1.255（GB200 倍數 3.04 → 2.36），改標校準相關（非獨立），F 欄為文字，不計入驗證
}
# v15.2：V2、V5、V8、V14、V20、V25 的比值隨 Calib D67（GB200 η_d 倍數 1 → 1.15）與 Cap_In C280 改變；通過／失敗旗標不變（預期變動，工作單 B3）
SOFT = {"V1", "V2", "V3"}      # v11.0 G4：MLPerf server 軟上限（> 1 為「警示」；v12.0 H1：> CHK_SoftCapFail 為失敗）
UNCOUNTED = {"V16", "V18", "V20", "V23", "V24"}      # v15.0 O9：V16 恆等式（非驗證）；v12.0：V18 恆等式（非驗證）、V20 校準相關（非獨立）：F 欄為文字，不計入驗證項目數；v14.1 R2：V23、V24 恆等式（非驗證）


def _verify_rows(v):
    rows = {}
    for r in range(1, 400):
        a = v.get("Checks", f"A{r}")
        if isinstance(a, str) and re.fullmatch(r"V\d+", a):
            rows[a] = r
    return rows


@pytest.mark.parametrize("vid", sorted(VERIFY_EXPECTED, key=lambda x: int(x[1:])))
def test_verify_item(lo, vid):
    """驗證清單逐項：比值、通過判定，以及判定與通過帶（H 下限、I 上限）一致。"""
    v = lo.view({})
    r = _verify_rows(v)[vid]
    ratio, passed = VERIFY_EXPECTED[vid]
    e, f = v.get("Checks", f"E{r}"), v.get("Checks", f"F{r}")
    assert _same(e, ratio), (vid, e, ratio)
    assert f == passed, (vid, f, passed)
    lo_b, hi_b = v.get("Checks", f"H{r}"), v.get("Checks", f"I{r}")
    inside = e >= lo_b and (hi_b in ("", None) or e <= hi_b)
    if vid in SOFT:      # 軟上限：低於下限失敗；高於上限至失敗門檻之間為警示；高於失敗門檻為失敗（v12.0 H1）
        fail_t = v.get_name("CHK_SoftCapFail")
        assert (0 if e < lo_b else (1 if inside else (0 if e > fail_t else "警示"))) == f, (vid, e, lo_b, hi_b, fail_t, f)
    elif vid in UNCOUNTED:      # F 欄為文字；帶內／帶外仍須與通過帶一致
        if vid == "V16":      # v15.0 O9：V16 的 E 是能量閉合比（基準 0.085），帶 [H, I]＝[0, 1] 內才成立恆等式
            assert (f == "恆等式（非驗證）") == inside, (vid, e, lo_b, hi_b, f)
        elif vid in ("V18", "V23", "V24"):
            assert (f == "恆等式（非驗證）") == (e == 0), (vid, e, f)
        else:
            assert f == "校準相關（非獨立）：" + ("帶內" if inside else "帶外"), (vid, e, lo_b, hi_b, f)
    else:
        assert (1 if inside else 0) == f, (vid, e, lo_b, hi_b, f)


def test_verify_totals_and_list_complete(lo):
    """清單完整（V1–V26 共 26 項，無缺列；v14.0 4-3B Q4 新增 V23–V26，皆通過，CHK_Verify* 20／12／7／1 → 24／16／7／1）；CHK_VerifyTotal／Pass／Fail／Warn＝20／12／7／1（v10.3：19／11／8；v11.0：22／14／7／1，V1 改警示、新增 V20–V22 皆通過；v12.0：V18 改恆等式、V20 改校準相關，皆移出計數，Pass 14 → 12、Total 22 → 20）；恆等式 Pass＋Fail＋Warn＝Total。"""
    v = lo.view({})
    assert sorted(_verify_rows(v), key=lambda x: int(x[1:])) == [f"V{i}" for i in range(1, 27)]
    assert (v.get_name("CHK_VerifyTotal"), v.get_name("CHK_VerifyPass"), v.get_name("CHK_VerifyFail"), v.get_name("CHK_VerifyWarn")) == (21, 13, 7, 1)      # v15.0 O9：V16 移出計數（22／14／7／1 → 21／13／7／1）；v14.1 R2：V23、V24 移出計數（24／16／7／1 → 22／14／7／1）
    assert v.get_name("CHK_VerifyPass") + v.get_name("CHK_VerifyFail") + v.get_name("CHK_VerifyWarn") == v.get_name("CHK_VerifyTotal")
    assert sum(1 for _, p in VERIFY_EXPECTED.values() if p == 1) == 13      # v15.0 O9：14 → 13（V16 改標恆等式）；v14.1 R2：16 → 14
    assert sum(1 for _, p in VERIFY_EXPECTED.values() if p == 0) == 7 and sum(1 for _, p in VERIFY_EXPECTED.values() if p == "警示") == 1


def test_gov_counts_new_baseline(lo):
    """GOV 三項計數在新基準（Serving 第 21 列為兩家量測商幾何平均）下：Errors 0、Warnings 282（v11.0：+3，新增 SRC 紀錄缺第二來源 W1）、Info 182（v13.0：181 → 182，Calib C68 類別更正為 Assumed 進 Load_Bearing；v12.0：179 → 181，Gov_Map 『標記變更』欄 +1＝C68 更正註記；Load_Bearing 高段 Assumed 列 +1＝新增 Hopper C156 列）。"""
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 133, 182)      # v20.0：132 → 134（SRC_DEM_088 缺第二來源 W1 +1；L1_DPaid_Scen 的 D／E／F 為三個情境使 H3 +1；待 Project 判斷）； v19.1：133 → 132（SRC_MOD_018 填 C1 免除標記，Z22 缺第二來源 1 → 0）； v15.0：Info 184 → 182（L1 外部對照換算後，第 31、60、63 列轉為 ±20% 內、第 65 列轉為差距 >20%，淨減 2）； v13.1 D15 B 段：Warnings 282 → 280（SRC_HW_067／068 有第二來源）、Info 182 → 184（DB_Evidence 新增 2 筆待判定）； v13.0 K3：Info 181 → 182（C68 進 Load_Bearing）      # v17.2：W1 278 → 131（W1 第二來源 B1：A 86、C1 53、Q11 8 離開；預期變動）

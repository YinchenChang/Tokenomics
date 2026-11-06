"""v22.0 專屬測試（v22.0 B3「啟用」：GPT-6.1 Terra 成為第四個現行層級；設計文件 docs/plan/20261105_v22.0_Terra第四層級_設計.md 第 6.1、6.4 節）。
讀 LibreOffice 重算後存檔的現行版（model/CURRENT）與封存的 v21.12。（檔名 test_v22000＝v22.0。）

  1. V7：逐格比較 v21.12 → v22.0（tools/cmp_v22000.py）：值改變的格都在預期變動 CSV 且等於預檢值；CSV 以外的數值差異只在治理連帶格。
  2. V4：2025 錨點逐值不變——L1_MFleet_Lo 例外（+0.32%，經 AL_ProdRatioPaid 讀到 2026 組合；報告待 Project 判斷，本測試釘住現值）。
  3. V5／V6：四層組合合計＝1；Terra 每 GW 產能與 decode 成本介於 Sol 與 Luna 之間；IF_PriceRef_Terra＝0.784；五個世代皆可達。
  4. V7 目標：L1_RevGW_PQ_VR200 49.4–53.4、L1_M 約 1.44、IF_PxEffMix 約 1.825。設計第 5.4 節「不變」名稱逐值相同。
  5. 結構：新名稱＝fixtures/v22000_new_names.json；Interface R 節在既有列之下；L1 Terra 列在末端；不建 CAP_Px25_Terra*／L1_RLshare_Terra*／L1_PretrainFLOP_Terra*。
  6. GOV 計數、時效旗標、V23、版本字串、Decisions SL70-*、SRC 紀錄、README。"""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
sys.path.insert(0, str(REPO / "tools"))
import cmp_v22000  # noqa: E402
import v22000  # noqa: E402

V2112 = REPO / "model" / "archive" / "20261105_Tokenomics_v21.12.xlsx"
CSV = REPO / "docs" / "workorders" / "20261105_v22.0_預期變動.csv"
NEW = set(json.loads((Path(__file__).resolve().parent / "fixtures" / "v22000_new_names.json").read_text(encoding="utf-8"))["names"])
ANCHORS_2025 = ["L1_MFleet", "L1_MFleet_Hi", "L1_LReqFleet", "L1_LReqFleet_Full", "L1_M_2025", "CAP_Price25Mix", "IF_PxEffMix25",
                "AL_PriceFleet25", "IF_AllocQ1", "IF_AllocQ1_R2", "IF_AllocQ2", "IF_AllocServeGW", "IF_AllocImpliedNk", "IF_AllocRDGW", "L1_TokPaid_GW25",
                "L1_TokLedger_GW25", "L1_PayRatio25", "L1_HoldFleet25"]
TIERS3 = ("Luna", "Sol", "Astra")
UNCHANGED = ([f"IF_{p}_{t}" for t in TIERS3 for p in ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ",
                                                       "RevGW", "RevGWFront", "TrainGPUh", "TrainCost", "PostShareFLOP", "PostShareGPUh", "RLMFU", "ProgGPUh",
                                                       "ProgCost", "ProgGWyr", "TaskSucc", "TaskSuccSel", "HarR", "HzEff", "PriceFresh", "PriceCached",
                                                       "PriceThink", "PriceOut", "PriceRef", "FrontRef", "FrontModel", "Life", "CacheStore", "AmortTD")]
             + [f"L1_CostDec_{t}_{g}" for t in TIERS3 for g in ("VR200", "GB300")]
             + ["IF_HoldEcon", "IF_HoldAcct", "IF_GPUhrEcon", "IF_RackPrice", "IF_NonNV_Out_TPU", "IF_NonNV_Hold_TPU", "IF_NonNV_Out_Trn", "IF_NonNV_Out_AMD"])
GEN_BASE = (2, 5, 8, 11, 14)      # base-cost column of each generation inside C:Q (1-based)


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


@pytest.fixture(scope="module")
def cmp():
    out = Path(tempfile.mkdtemp()) / "cmp.json"
    old_argv = sys.argv
    sys.argv = ["cmp_v22000.py", str(V2112), str(model_path()), str(CSV), str(out)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cmp_v22000.main()
    finally:
        sys.argv = old_argv
    return json.loads(out.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def new():
    return openpyxl.load_workbook(model_path()), openpyxl.load_workbook(model_path(), data_only=True)


@pytest.fixture(scope="module")
def old():
    return openpyxl.load_workbook(V2112), openpyxl.load_workbook(V2112, data_only=True)


def val(wb, n):
    wbf, wbv = wb
    sh, rg = wbf.defined_names[n].attr_text.rsplit("!", 1)
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    v = [wbv[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
    return v if len(v) > 1 else v[0]


# ---------------------------------------------------------------- 1. V7 逐格比較
NUM_EXTRA_OK = {"Alloc", "Checks", "Gov_Map", "SRC_Index", "Load_Bearing", "SRC_Price"}


def test_v22000_cells_vs_expected_csv(cmp):
    assert len(cmp["hit"]) == 2764, len(cmp["hit"])                          # 值改變、在 CSV、等於預檢值
    assert cmp["csv_off"] == [["Checks", "D98", 129, 133, 131]]               # GOV_Warnings：預檢 131（含區間過期 +1），實際 133（重產區間 −1；SRC_PRC_066–068 Active 缺第二來源 W1 +3）
    assert cmp["csv_not_seen"] == []
    stale = {("Alloc", "C179"), ("Alloc", "C180"), ("Alloc", "C410"), ("Checks", "D179"), ("Checks", "D180")}
    assert all((s, c) in stale or (s == "Alloc" and c[0] in "RE") for s, c, *_ in cmp["csv_same"]), cmp["csv_same"]      # 區間過期旗標：重產後回原值
    for s, c, c2, x, y in cmp["extra"]:
        isnum = lambda z: z.replace(".", "", 1).replace("-", "", 1).replace("e", "", 1).isdigit()
        if isnum(x) and isnum(y):
            assert s in NUM_EXTRA_OK, (s, c, x, y)
    assert {x[0] for x in cmp["unmatched_old"]} <= {"Alloc"}                 # 指紋葉格 Cap_In F6:F8（改公式後不再是常數葉格）與（b）清單文字列


def test_v22000_names(new, old):
    nf, of = set(new[0].defined_names), set(old[0].defined_names)
    assert of <= nf and nf - of == NEW and len(NEW) == 107
    for bad in ("CAP_Px25_Terra", "L1_RLshare_Terra", "L1_PretrainFLOP_Terra"):
        assert not any(n.startswith(bad) for n in nf), bad
    terra = {n for n in NEW if "Terra" in n}
    assert sum(n.startswith("IF_") for n in terra) == 52 and sum(n.startswith("IFW_") for n in terra) == 14
    assert sum(n.startswith("L1_") for n in terra) == 9 and sum(n.startswith("RNG_") for n in terra) == 28
    assert NEW - terra == {"SRC_PERF_088", "SRC_PERF_089", "SRC_CAP_022", "SRC_CAP_023"}


# ---------------------------------------------------------------- 2. V4 2025 錨點
def test_v22000_2025_anchors(new, old):
    for n in ANCHORS_2025:
        a, b = val(old, n), val(new, n)
        assert all(same(x, y) for x, y in zip(a if isinstance(a, list) else [a], b if isinstance(b, list) else [b])), n
    # L1_MFleet_Lo：經 Alloc H 節 AL_ProdRatioPaid（生產折減下付費產能比，讀 Fleet_1GW／Fleet_1GW_Prod，即 2026 組合）移動 +0.32%；待 Project 判斷，不旁路
    a, b = val(old, "L1_MFleet_Lo"), val(new, "L1_MFleet_Lo")
    assert abs(a - 0.275034376001415) < 1e-12 and abs(b / a - 1 - 0.0032) < 0.0002


# ---------------------------------------------------------------- 3. V5／V6
def test_v22000_mix_sums(new):
    for n in ("B4_MixPaid", "B4_MixFree", "B4_MixPaid25", "B4_MixFree25"):
        v = val(new, n)
        assert len(v) == 4 and abs(sum(v) - 1) < 1e-12, (n, v)
    assert val(new, "B4_MixPaid") == [0.4, 0.3, 0.15, 0.15] and val(new, "B4_MixFree") == [0.9, 0.1, 0, 0]
    assert val(new, "B4_MixPaid25") == [0.4, 0.45, 0.15, 0] and val(new, "B4_TerraFam") == 1
    s = sum(val(new, f"IF_MixPaid_{t}") for t in ("Luna", "Sol", "Astra", "Terra"))
    assert abs(s - 1) < 1e-12 and abs(sum(val(new, f"IF_MixPaid_{t}") for t in TIERS3) - 0.85) < 1e-12      # 三項不再合計 1（契約 v0.28）


def test_v22000_terra_reasonable(new):
    tg = {t: val(new, f"IF_TokGW_{t}") for t in ("Luna", "Sol", "Terra")}
    cd = {t: val(new, f"IF_CostDec_{t}") for t in ("Luna", "Sol", "Terra")}
    for k in GEN_BASE:
        i = k - 1
        assert all(isinstance(tg[t][i], float) for t in tg), "五個世代皆可達"
        assert tg["Sol"][i] < tg["Terra"][i] < tg["Luna"][i], (k, tg["Sol"][i], tg["Terra"][i], tg["Luna"][i])
        assert cd["Luna"][i] < cd["Terra"][i] < cd["Sol"][i], k
    assert abs(val(new, "IF_PriceRef_Terra") - 0.784) < 1e-12
    assert val(new, "IF_FrontModel_Terra") == "GPT-6.1 Terra"      # J7 (b)：能力指數空白，前緣＝自身


# ---------------------------------------------------------------- 4. V7 目標與「不變」名稱
def test_v22000_targets(new):
    assert 49.4 <= val(new, "L1_RevGW_PQ_VR200") <= 53.4
    assert abs(val(new, "L1_M") - 1.443) < 0.005 and abs(val(new, "IF_PxEffMix") - 1.825) < 0.002
    assert abs(val(new, "L1_RevGW_PQ_VR200") - 51.7508) < 0.001                  # 實測；設計預估約 51.9


def test_v22000_unchanged_names(new, old):
    for n in UNCHANGED:
        a, b = val(old, n), val(new, n)
        assert all(same(x, y) for x, y in zip(a if isinstance(a, list) else [a], b if isinstance(b, list) else [b])), n


# ---------------------------------------------------------------- 5. 結構
def test_v22000_interface_r_and_l1_end(new, old):
    nf, nv = new
    of, _ = old
    ws = nf["Interface"]
    last_old = max(c.row for row in of["Interface"].iter_rows() for c in row if c.value is not None)
    r0 = [r for r in range(1, ws.max_row + 1) if str(ws.cell(r, 1).value).startswith("R. Terra")]
    assert len(r0) == 1 and r0[0] == last_old + 2
    terra_if = sorted(n for n in NEW if n.startswith(("IF_", "IFW_")))
    for n in terra_if:
        sh, rg = nf.defined_names[n].attr_text.split("!")
        assert sh == "Interface" and int(rg.split("$")[2].split(":")[0]) > r0[0], n
        luna = n.replace("_Terra", "_Luna")
        assert nf.defined_names[luna].attr_text == of.defined_names[luna].attr_text          # 既有列不位移（J14）
        assert range_boundaries(rg.replace("$", ""))[2] - range_boundaries(rg.replace("$", ""))[0] == \
            range_boundaries(nf.defined_names[luna].attr_text.split("!")[1].replace("$", ""))[2] - range_boundaries(nf.defined_names[luna].attr_text.split("!")[1].replace("$", ""))[0]
        lab = ws.cell(int(rg.split("$")[2].split(":")[0]), 1).value
        assert "（對應 " in lab and f"[{n}]" in lab, lab
    l1_old_last = max(r for r in range(5, of["L1"].max_row + 1) if of["L1"].cell(r, 1).value)
    rows = {nf["L1"].cell(r, 1).value: r for r in range(5, nf["L1"].max_row + 1)}
    assert [rows[f"L1_{k}"] for k in ("CostDec_Terra_VR200", "CostDec_Terra_GB300", "RevGW_Terra_VR200")] == [l1_old_last + 1, l1_old_last + 2, l1_old_last + 3]
    # 值的同一性：R 節名稱等於 Terra 區的對應格
    tr = nf["Theory_Rev"]
    rev_row = [r for r in range(100, tr.max_row + 1) if str(tr.cell(r, 1).value).startswith("理論營收 — OpenAI 有效單價（→ IF_RevGW_Terra）")][0]
    assert same(val(new, "IF_RevGW_Terra")[10], nv["Theory_Rev"].cell(rev_row, 13).value)
    assert all(same(x, y) for x, y in zip(val(new, "IFW_RevGW_Terra_Util"), val(new, "IF_RevGW_Terra")))
    assert all(same(x, y) for x, y in zip(val(new, "IF_RevGW_Terra_Life"), val(new, "IFW_RevGW_Terra_Life")))
    assert same(val(new, "L1_RevGW_Terra_VR200"), val(new, "IF_RevGW_Terra")[10]) and same(val(new, "L1_CostDec_Terra_VR200"), val(new, "IF_CostDec_Terra")[10])


def test_v22000_four_term_readers(new):
    nf, _ = new
    f = nf["L1"].cell([r for r in range(5, nf["L1"].max_row + 1) if nf["L1"].cell(r, 1).value == "L1_TokGW_PaidCap_VR200"][0], 4).value
    assert "INDEX(B4_MixPaid,1,4)/INDEX(IF_TokGW_Terra,1,11)" in f
    sh, rg = nf.defined_names["IF_TokGWPaidMix"].attr_text.split("!")
    c = nf["Interface"][rg.split(":")[0].replace("$", "")].value
    assert "IF_MixPaid_Terra/INDEX(IF_TokGW_Terra,1,1)" in c
    tp = nf["Train_In"]
    labs = {tp.cell(r, 1).value for r in range(1, tp.max_row + 1)}
    assert {"合成資料生成層級（1 Luna／2 Sol／3 Astra／4 Terra）", "蒸餾教師層級（1 Luna／2 Sol／3 Astra／4 Terra）"} <= labs


# ---------------------------------------------------------------- 6. GOV、版本、紀錄
def test_v22000_gov_version_records(new):
    nf, nv = new
    assert (val(new, "GOV_Errors"), val(new, "GOV_Warnings"), val(new, "GOV_Info")) == (0, 133, 183)
    assert val(new, "RNG_StaleFlag") == "一致" and val(new, "RNG_OutCount") == 0
    assert str(val(new, "RNG_Version")).endswith("v22.0") and str(val(new, "RNG_Current")).endswith("v22.0")
    stem = (REPO / "model" / "CURRENT").read_text(encoding="utf-8").strip()
    assert v22000.VERSION + ".xlsx" == stem and nf["Load_Bearing"]["C3"].value == "2026-11-05"
    ck = nf["Checks"]
    z4 = {ck.cell(r, 1).value: nv["Checks"].cell(r, 4).value for r in range(1, ck.max_row + 1) if str(ck.cell(r, 1).value).startswith("Z4")}
    assert z4["Z4a"] == 0 and z4["Z4b"] == 0 and z4["Z4c"] == 0 and z4["Z4d"] == 0 and z4["Z4e"] == "GPT-6.1 Terra"
    v23 = [r for r in range(1, ck.max_row + 1) if ck.cell(r, 1).value == "V23"][0]
    assert nv["Checks"].cell(v23, 4).value == 42 and nv["Checks"].cell(v23, 3).value == 0      # 可達欄數 32 → 42（Perf 20＋Perf_Batch 22）
    d = nf["Decisions"]
    ids = [d.cell(r, 1).value for r in range(5, d.max_row + 1)]
    assert "SL70-01" in ids and all(f"SL70-J{i:02d}" in ids for i in range(1, 16))
    r = ids.index("SL70-01") + 5
    assert "完整第四層級" in d.cell(r, 6).value and "照建議" in d.cell(r, 6).value and "機械性上升" in d.cell(r, 4).value
    sp = {nf["SRC_Price"].cell(r, 1).value: nf["SRC_Price"].cell(r, 15).value for r in range(5, nf["SRC_Price"].max_row + 1)}
    assert sp["SRC_PRC_066"] == sp["SRC_PRC_067"] == sp["SRC_PRC_068"] == "Active"
    assert nf["Cap_In"]["F6"].value == "=SRC_PRC_066" and nf["Cap_In"]["G59"].value == "=SRC_PRC_068"
    for sh, sid, v in (("SRC_Perf", "SRC_PERF_088", 77), ("SRC_Perf", "SRC_PERF_089", 59), ("SRC_Cap", "SRC_CAP_022", 51), ("SRC_Cap", "SRC_CAP_023", 48)):
        w = nf[sh]
        r = [x for x in range(5, w.max_row + 1) if w.cell(x, 1).value == sid][0]
        assert w.cell(r, 3).value == v and w.cell(r, 15).value == "Alt"
    db = nf["DB_Evidence"]
    assert {"E561", "E562", "E563", "E564", "E565"} <= {db.cell(r, 1).value for r in range(5, db.max_row + 1)}
    rm = nf["README"]
    assert str(rm["A1"].value).startswith("Tokenomics v22.0") and str(rm["B5"].value).startswith("20261105_Tokenomics_v22.0（主版，底版 v21.12：")

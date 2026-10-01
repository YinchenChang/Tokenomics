"""Excel（LibreOffice 重算）與 engine 的一致性測試（CLAUDE.md 第 3 節）。

比對範圍：全部公式格；具名範圍名稱與 attr_text；7 個情境各以獨立引擎實例重算。
"""
import time
from pathlib import Path

import pytest
import yaml

from engine import Engine, current_model_path, read_defined_names_xml
from parity_lib import compare, excel_values, format_mismatches, lo_recalc, set_inputs

HERE = Path(__file__).parent
CFG = yaml.safe_load((HERE / "scenarios.yaml").read_text(encoding="utf-8"))
SCENARIOS = CFG["scenarios"]
EXPECT = CFG["workbook_expectations"]
TIERS = ("Luna", "Sol", "Astra")
BLOCK3_PREFIX = ("TrainGPUh", "TrainCost", "PostShareFLOP", "PostShareGPUh", "RLMFU", "ProgGPUh", "ProgCost", "ProgGWyr")
BLOCK2_PREFIX = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")


@pytest.fixture(scope="module")
def model():
    return current_model_path()


def test_workbook_expectations(model):
    eng = Engine(model)
    assert len(eng.formula_cells) == EXPECT["formula_cells"]
    assert len(eng.names) == EXPECT["defined_names"]


def test_named_ranges(model):
    """142 個具名範圍：名稱存在、attr_text 與 workbook.xml 及 LibreOffice 重算版一致，且可取值。"""
    eng = Engine(model)
    xml_names = read_defined_names_xml(model)
    assert set(eng.names) == set(xml_names)
    for n, txt in eng.names.items():
        assert eng.names[n] == xml_names[n], f"{n}: {eng.names[n]} ≠ {xml_names[n]}"
    block2 = {f"IF_{p}_{t}" for p in BLOCK2_PREFIX for t in TIERS} | {"IF_Util"}
    assert len(block2) == EXPECT["block2_names"]
    assert block2 <= set(eng.names), f"缺少：{sorted(block2 - set(eng.names))}"
    display = {n for n in eng.names if n.startswith(("IF_Hdr", "DRV_", "CAL_", "TRN_", "TR_"))}
    assert len(display) == EXPECT["display_only_names"]
    assert sum(n.startswith("DRV_") for n in eng.names) == EXPECT["drv_names"] and sum(n.startswith("CAL_") for n in eng.names) == EXPECT["cal_names"]
    assert "DRV_CostDec" not in eng.names                                  # v5.5 移除
    assert sum(n.startswith("TRN_") for n in eng.names) == EXPECT["trn_names"]
    assert sum(n.startswith("TR_") for n in eng.names) == EXPECT["tr_names"]
    assert {"IF_TrainGenDefault", "IF_TrainGenAlt"} <= set(eng.names)      # v5.6：J13 預設與並列訓練世代（世代索引）
    block3 = {f"IF_{p}_{t}" for p in BLOCK3_PREFIX for t in TIERS} | {"IF_RDMult"}
    assert len(block3) == EXPECT["block3_names"] and block3 <= set(eng.names), f"缺少：{sorted(block3 - set(eng.names))}"
    assert {"IF_HdrGen", "IF_HdrCost"} <= set(eng.names)
    downstream = {n for n in eng.names if n.startswith("IF_") and not n.startswith("IF_Hdr")}
    assert len(downstream) == EXPECT["downstream_names"]
    for n in eng.names:  # 每個名稱都能取值，且非錯誤值
        v = eng.get_name(n)
        flat = v if isinstance(v, list) else [v]
        assert all(not (isinstance(x, str) and x.startswith("#")) for x in flat), f"{n} 含錯誤值"


def test_display_names_alignment(model):
    """表頭與推導鏈名稱的形狀：DRV_ 皆 15 欄且與 DRV_Gen／DRV_Tier 對齊；IF_Hdr 與 IF_ 輸出欄數一致。"""
    eng = Engine(model)
    n = EXPECT["drv_columns"]
    for name in eng.names:
        if name.startswith("DRV_"):
            v = eng.get_name(name)
            assert isinstance(v, list) and len(v) == n, f"{name} 欄數 {len(v)}"
    assert len(eng.get_name("IF_HdrGen")) == len(eng.get_name("IF_HdrCost")) == len(eng.get_name("IF_TokGW_Luna"))
    assert eng.get_name("DRV_Gen") == eng.get_name("IF_HdrGen")            # 世代欄順序一致
    for name in eng.names:                                                 # TRN_ 皆 15 欄，且與 TRN_Gen／TRN_Tier 及 DRV_ 的世代、層級順序一致
        if name.startswith("TRN_"):
            v = eng.get_name(name)
            assert isinstance(v, list) and len(v) == n, f"{name} 欄數 {len(v)}"
    assert eng.get_name("TRN_Gen") == eng.get_name("DRV_Gen") and eng.get_name("TRN_Tier") == eng.get_name("DRV_Tier")
    for name in eng.names:                                                 # TR_：登錄表 12 格、掛鉤彙總 11 格，且無錯誤值
        if name.startswith("TR_"):
            v = eng.get_name(name)
            want = EXPECT["tr_hook_rows"] if name.startswith(("TR_HookCode", "TR_HookName", "TR_HookVal")) else EXPECT["tr_rows"]
            assert isinstance(v, list) and len(v) == want, f"{name}: {len(v) if isinstance(v, list) else 1} 格，應為 {want}"
    for name in ("IF_TrainGenDefault", "IF_TrainGenAlt"):                  # 世代索引：1–5 的整數
        v = eng.get_name(name)
        assert isinstance(v, (int, float)) and v == int(v) and 1 <= v <= len(set(eng.get_name("IF_HdrGen"))), f"{name}={v!r}"
    for p in BLOCK3_PREFIX:                                                # Block 3 的 Interface 輸出：每層級 15 欄，與 IF_HdrGen 同寬
        for t in TIERS:
            assert len(eng.get_name(f"IF_{p}_{t}")) == len(eng.get_name("IF_HdrGen")), f"IF_{p}_{t}"
    for prefix, keys, n_pts in (("F", ("Label", "Gen", "Eng", "Speed", "Meas", "Model", "Basis", "Platform", "Ratio"), EXPECT["cal_f_points"]),
                                ("H", ("Label", "Gen", "Speed", "Meas", "Model", "Basis", "Platform", "Ratio"), EXPECT["cal_h_points"])):
        for k in keys:                                                   # 驗證表各欄名稱同為 7（F）／4（H）格
            v = eng.get_name(f"CAL_{prefix}_{k}")
            assert isinstance(v, list) and len(v) == n_pts, f"CAL_{prefix}_{k}: {len(v) if isinstance(v, list) else 1} 格，應為 {n_pts}"
            assert all(x != "" for x in v), f"CAL_{prefix}_{k} 含空格"
    assert set(eng.get_name("CAL_F_Gen")) <= set(eng.get_name("IF_HdrGen"))   # 驗證點的世代名稱都是 Interface 世代


def test_named_ranges_vs_libreoffice(model, tmp_path):
    """LibreOffice 存檔後的名稱範圍（正規化後）與原檔一致。"""
    src = tmp_path / model.name
    set_inputs(model, src, {})
    out = lo_recalc(src, tmp_path / "lo")
    import openpyxl
    lo = {k: v.attr_text.replace("$", "") for k, v in openpyxl.load_workbook(out).defined_names.items()}
    ours = {k: v.replace("$", "") for k, v in Engine(model).names.items()}
    assert lo == ours


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_parity(sc, model, tmp_path, results_store):
    """情境：改寫輸入 → LibreOffice 重算（基準）→ 與引擎全部公式格比對。"""
    scen_xlsx = tmp_path / model.name
    set_inputs(model, scen_xlsx, sc["inputs"])
    ref = excel_values(lo_recalc(scen_xlsx, tmp_path / "lo"), Engine(model).formula_cells)

    eng = Engine(model)                         # 每個情境獨立實例，不受前一情境影響
    for addr, v in sc["inputs"].items():
        eng.set_input(*addr.split("!"), v)
    t0 = time.perf_counter()
    got = eng.evaluate_all()
    elapsed = time.perf_counter() - t0

    res = compare(got, ref)
    results_store[sc["id"]] = {k: v for k, v in res.items() if k != "mismatches"} | {
        "n_mismatch": len(res["mismatches"]), "eval_all_seconds_after_change": round(elapsed, 2)}
    assert not res["mismatches"], f"[{sc['id']}] " + format_mismatches(res["mismatches"])


def test_scenarios_actually_change_outputs(model, tmp_path):
    """防止測試空轉：每個情境至少改變 Interface 的一個格（相對基準）。"""
    eng0 = Engine(model)
    base = eng0.evaluate_all()
    for sc in SCENARIOS[1:]:
        eng = Engine(model)
        for addr, v in sc["inputs"].items():
            eng.set_input(*addr.split("!"), v)
        cur = eng.evaluate_all()
        changed = [k for k in base if base[k] != cur[k]]
        assert changed, f"{sc['id']} 未改變任何公式格"


def test_incremental_recalc_matches_fresh_and_is_fast(model):
    """同一實例連續改輸入再還原：結果須與全新實例相同；單次全簿重算 < 2 秒。"""
    eng = Engine(model)
    base = eng.evaluate_all()
    t0 = time.perf_counter()
    eng._xl.recalculate()                      # 強制全簿（全部公式格）重算
    full = time.perf_counter() - t0
    assert full < 2.0, f"全簿強制重算 {full:.2f}s ≥ 2s"
    for sc in SCENARIOS[1:]:
        origs = {a: Engine(model).get(*a.split("!")) for a in sc["inputs"]}
        t0 = time.perf_counter()
        for addr, v in sc["inputs"].items():
            eng.set_input(*addr.split("!"), v)
        eng.evaluate_all()
        dt = time.perf_counter() - t0
        assert dt < 2.0, f"{sc['id']} 全簿重算 {dt:.2f}s ≥ 2s"
        for addr, v in origs.items():
            eng.set_input(*addr.split("!"), v)
    res = compare(eng.evaluate_all(), base)   # 還原後與基準相同（容差內；pycel 部分格以 15 位快取值回填）
    assert not res["mismatches"], format_mismatches(res["mismatches"])

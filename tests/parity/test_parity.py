"""Excel（LibreOffice 重算）與 engine 的一致性測試（CLAUDE.md 第 3 節）。

比對範圍：全部公式格；具名範圍名稱與 attr_text；5 個情境各以獨立引擎實例重算。
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
BLOCK2_PREFIX = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")


@pytest.fixture(scope="module")
def model():
    return current_model_path()


def test_workbook_expectations(model):
    eng = Engine(model)
    assert len(eng.formula_cells) == EXPECT["formula_cells"]
    assert len(eng.names) == EXPECT["defined_names"]


def test_named_ranges(model):
    """40 個具名範圍：名稱存在、attr_text 與 workbook.xml 及 LibreOffice 重算版一致，且可取值。"""
    eng = Engine(model)
    xml_names = read_defined_names_xml(model)
    assert set(eng.names) == set(xml_names)
    for n, txt in eng.names.items():
        assert eng.names[n] == xml_names[n], f"{n}: {eng.names[n]} ≠ {xml_names[n]}"
    block2 = {f"IF_{p}_{t}" for p in BLOCK2_PREFIX for t in TIERS} | {"IF_Util"}
    assert len(block2) == EXPECT["block2_names"]
    assert block2 <= set(eng.names), f"缺少：{sorted(block2 - set(eng.names))}"
    for n in eng.names:  # 每個名稱都能取值，且非錯誤值
        v = eng.get_name(n)
        flat = v if isinstance(v, list) else [v]
        assert all(not (isinstance(x, str) and x.startswith("#")) for x in flat), f"{n} 含錯誤值"


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
        "n_mismatch": len(res["mismatches"]), "eval_all_seconds_cold": round(elapsed, 2)}
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
    for sc in SCENARIOS[1:]:
        (addr, v), = sc["inputs"].items()
        sheet, coord = addr.split("!")
        orig = Engine(model).get(sheet, coord)
        t0 = time.perf_counter()
        eng.set_input(sheet, coord, v)
        eng.evaluate_all()
        dt = time.perf_counter() - t0
        assert dt < 2.0, f"{sc['id']} 全簿重算 {dt:.2f}s ≥ 2s"
        eng.set_input(sheet, coord, orig)
    assert eng.evaluate_all() == base

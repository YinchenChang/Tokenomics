"""Excel（LibreOffice 重算）與 engine 的一致性測試（CLAUDE.md 第 3 節）。

比對範圍：全部公式格；具名範圍名稱與 attr_text；17 個情境（含 v5.11 兩個治理情境）各以獨立引擎實例重算。
"""
import os
import time
from pathlib import Path

import pytest
import yaml

from engine import Engine, current_model_path, read_defined_names_xml, resolve_key
from parity_lib import compare, excel_values, format_mismatches, lo_recalc, set_inputs

HERE = Path(__file__).parent
CFG = yaml.safe_load((HERE / "scenarios.yaml").read_text(encoding="utf-8"))
SCENARIOS = CFG["scenarios"]
EXPECT = CFG["workbook_expectations"]
TIERS = ("Luna", "Sol", "Astra")
BLOCK3_PREFIX = ("TrainGPUh", "TrainCost", "PostShareFLOP", "PostShareGPUh", "RLMFU", "ProgGPUh", "ProgCost", "ProgGWyr")
BLOCK2_PREFIX = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")


ALLOC_IF = ("IF_AllocQ1", "IF_AllocQ1_R2", "IF_AllocQ2", "IF_AllocServeGW", "IF_AllocRDGW", "IF_AllocDemand", "IF_AllocImpliedNk")


@pytest.fixture(scope="module")
def model():
    return current_model_path()


@pytest.fixture(scope="module")
def base_engine(model):
    """基準引擎（只讀）：供防空轉統計與公式格清單，避免每個情境重複建圖。一律重建（不經快取）。"""
    eng = new_engine(model, fresh=True)
    return eng, eng.evaluate_all()


def new_engine(model, fresh=False):
    """回傳全新的引擎實例。預設（無快取）每次建圖並重算，約 50 秒。
    CI 設定 TOKENOMICS_ENGINE_CACHE 時改由 pycel 序列化檔載入（ExcelCompiler.from_file，約數秒），每次載入都是獨立實例；
    載入後仍強制全簿重算。第 14 輪評估：18 情境與重建逐格比對不符 0（2026-10-04 提速報告）。
    fresh=True 一律重建：效能門檻測試（兩條重算）量的是真正建出來的引擎，不經快取。
    曾評估以 deepcopy 範本共用建圖結果（第 12 輪第 7 點）：總時長可由約 37 分降至約 10 分，但複本偶發
    'NoneType' has no attribute 'get_range'，且複本的重算變慢（4.9–6.2 秒），不採用。"""
    cache = None if fresh else os.environ.get("TOKENOMICS_ENGINE_CACHE")
    return Engine(model, cache=cache or None)


@pytest.fixture(scope="module")
def template_engine(model):
    return model


def _clone(model, fresh=False):
    return new_engine(model, fresh=fresh)


def test_model_current_pointer(model):
    """CLAUDE.md 第 2、4 節：model/CURRENT 一行記錄現行檔名，且與 model/ 唯一一份 xlsx 相符。"""
    assert (model.parent / "CURRENT").read_text(encoding="utf-8").strip() == model.name


def test_workbook_expectations(model):
    eng = new_engine(model)
    assert len(eng.formula_cells) == EXPECT["formula_cells"]
    assert len(eng.names) == EXPECT["defined_names"]
    assert eng.sheetnames == EXPECT["sheets"]                              # v5.7 起含 DB_Evidence（最後一頁）；v5.8 起含 8 個 Block 4 頁
    assert not any(s == "DB_Evidence" for s, _ in eng.formula_cells)       # DB_Evidence 純輸入、無公式


def test_named_ranges(model):
    """144 個具名範圍：名稱存在、attr_text 與 workbook.xml 及 LibreOffice 重算版一致，且可取值。"""
    eng = new_engine(model)
    xml_names = read_defined_names_xml(model)
    assert set(eng.names) == set(xml_names)
    for n, txt in eng.names.items():
        assert eng.names[n] == xml_names[n], f"{n}: {eng.names[n]} ≠ {xml_names[n]}"
    block2 = {f"IF_{p}_{t}" for p in BLOCK2_PREFIX for t in TIERS} | {"IF_Util"}
    assert len(block2) == EXPECT["block2_names"]
    assert block2 <= set(eng.names), f"缺少：{sorted(block2 - set(eng.names))}"
    display = {n for n in eng.names if n.startswith(("IF_Hdr", "DRV_", "CAL_", "TRN_", "TR_", "B4_", "B5_"))}
    assert len(display) == EXPECT["display_only_names"]
    assert sum(n.startswith("B4_") for n in eng.names) == EXPECT["b4_names"]      # B4_：顯示或內部用，下游不得連結
    assert sum(n.startswith("B5_") for n in eng.names) == EXPECT["b5_names"]      # B5_：同上（v5.9 新增）
    assert "B4_Chi" not in eng.names and {"B4_CacheHit", "B4_MktChina"} <= set(eng.names)   # v5.9：改名與新增
    assert sum(n.startswith("DRV_") for n in eng.names) == EXPECT["drv_names"] and sum(n.startswith("CAL_") for n in eng.names) == EXPECT["cal_names"]
    assert sum(n.startswith("SRC_") for n in eng.names) == EXPECT["src_names"]       # v5.11：第 0 層
    assert sum(n.startswith("L1_") for n in eng.names) == EXPECT["l1_names"] and sum(n.startswith("GOV_") for n in eng.names) == EXPECT["gov_names"]
    assert sum(n.startswith("AL_") for n in eng.names) == EXPECT["al_names"]            # v5.15：Block 6 顯示名稱
    assert sum(n.startswith("CST_") for n in eng.names) == EXPECT["cst_names"] and sum(n.startswith("IDX_") for n in eng.names) == EXPECT["idx_names"]   # v5.12
    assert sum(n.startswith("CHK_") for n in eng.names) == EXPECT["chk_names"]            # v5.17：CHK_*（目前只 CHK_L1Order）
    assert not any(n.startswith(("CST_", "IDX_")) for n in eng.names if n.startswith("IF_"))          # CST_／IDX_ 不是下游名稱（下游只可連結 IF_）
    assert "DRV_CostDec" not in eng.names                                  # v5.5 移除
    assert sum(n.startswith("TRN_") for n in eng.names) == EXPECT["trn_names"]
    assert sum(n.startswith("TR_") for n in eng.names) == EXPECT["tr_names"]
    assert {"IF_TrainGenDefault", "IF_TrainGenAlt", "IF_TrainGenDefaultName", "IF_TrainGenAltName"} <= set(eng.names)      # v5.6：J13 預設與並列訓練世代（世代索引）
    block3 = {f"IF_{p}_{t}" for p in BLOCK3_PREFIX for t in TIERS} | {"IF_RDMult"}
    assert len(block3) == EXPECT["block3_names"] and block3 <= set(eng.names), f"缺少：{sorted(block3 - set(eng.names))}"
    assert {"IF_HdrGen", "IF_HdrCost"} <= set(eng.names)
    downstream = {n for n in eng.names if n.startswith("IF_") and not n.startswith("IF_Hdr")}
    assert len(downstream) == EXPECT["downstream_names"]
    if_all = [n for n in eng.names if n.startswith("IF_")]
    assert len(if_all) == EXPECT["downstream_names"] + 3 and sum(n.startswith("IF_Hdr") for n in eng.names) == 3   # 167＝164 下游＋IF_Hdr 3（IF_HdrGen、IF_HdrCost、IF_HdrTask）
    for n in eng.names:  # 每個名稱都能取值，且非錯誤值
        v = eng.get_name(n)
        flat = v if isinstance(v, list) else [v]
        assert all(not (isinstance(x, str) and x.startswith("#")) for x in flat), f"{n} 含錯誤值"


def test_display_names_alignment(model):
    """表頭與推導鏈名稱的形狀：DRV_ 皆 15 欄且與 DRV_Gen／DRV_Tier 對齊；IF_Hdr 與 IF_ 輸出欄數一致。"""
    eng = new_engine(model)
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
    gens = list(dict.fromkeys(eng.get_name("IF_HdrGen")))
    for idx, nm in (("IF_TrainGenDefault", "IF_TrainGenDefaultName"), ("IF_TrainGenAlt", "IF_TrainGenAltName")):   # v5.7：名稱＝索引所指世代
        assert eng.get_name(nm) == gens[int(eng.get_name(idx)) - 1], (nm, eng.get_name(nm))
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


def test_interface_d_e_shapes(model):
    """Interface D 節（v5.8）與 E 節（v5.9）的形狀，分開檢查：單格（數值或文字）、15 欄（5 世代 × 3 成本情境）、5 欄（任務）。"""
    eng = new_engine(model)
    ncol, ntask = len(eng.get_name("IF_HdrGen")), len(eng.get_name("IF_HdrTask"))
    assert ncol == 15 and ntask == 5
    single_num = [f"IF_{p}_{t}" for p in ("PriceFresh", "PriceCached", "PriceThink", "PriceOut", "PriceRef", "FrontRef", "Life") for t in TIERS] + ["IF_HarW"]
    single_txt = [f"IF_FrontModel_{t}" for t in TIERS] + ["IF_HarProfile"]
    wide = ([f"IF_{p}_{t}" for p in ("CacheStore", "AmortBU", "AmortTD", "FullCost", "RevGW", "RevGWFront",
                                    "AmortDefault", "AmortRev", "FullCostDefault", "RevGWFleet", "RevGWFleetFront") for t in TIERS]
            + ["IF_RevGWFleet", "IF_RevGWFleetFront"])
    task = ([f"IF_{p}_{t}" for p in ("TaskSucc", "TaskSuccSel", "CostSuccVR", "CostSuccGB", "RevSucc", "HarR") for t in TIERS]
            + ["IF_TaskLen", "IF_TaskTokFresh", "IF_TaskTokCached", "IF_TaskTokDec", "IF_TaskTokSel", "IF_HarTokRatio"])
    task += [f"IF_{p}_{t}" for p in ("CostAttVR", "HzEff") for t in TIERS]                  # v5.10：每次嘗試成本、有效時間範圍（任務 5 欄）
    single_num += ["IF_PFloor"]                                                           # v5.10：可靠度下限 p_min（單格）
    front = ["IF_FrontSuccVR", "IF_FrontSuccVRName", "IF_FrontSuccVRP"]                   # v5.10：前緣（5 欄；無合格時為文字「無合格」，數值列可能含文字）
    for n in single_num + ["IF_ServeShare", "IF_FreeShare"]:
        v = eng.get_name(n)
        assert not isinstance(v, list) and isinstance(v, (int, float)) and not isinstance(v, bool), f"{n} 應為單格數值：{v!r}"
    for n in single_txt:
        v = eng.get_name(n)
        assert isinstance(v, str) and v and not v.startswith("#"), f"{n} 應為單格文字：{v!r}"
    for names, width in ((wide, ncol), (task, ntask)):
        for n in names:
            v = eng.get_name(n)
            assert isinstance(v, list) and len(v) == width, f"{n} 欄數 {len(v) if isinstance(v, list) else 1}，應為 {width}"
            assert all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v), f"{n} 含非數值"
    for n in front:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == ntask, f"{n} 欄數應為 {ntask}"
        assert all(x != "" and not (isinstance(x, str) and x.startswith("#")) for x in v), f"{n} 含空值或錯誤值"
        if n != "IF_FrontSuccVRName":                                                     # 數值列：數值或「無合格」
            assert all(isinstance(x, (int, float)) and not isinstance(x, bool) or x == "無合格" for x in v), f"{n}: {v!r}"
        else:
            assert all(isinstance(x, str) for x in v)
    assert all(isinstance(x, str) and x for x in eng.get_name("IF_HdrTask"))              # 任務名稱（文字）
    v59_new = ({f"IF_{p}_{t}" for p in ("AmortDefault", "AmortRev", "FullCostDefault", "RevGWFleet", "RevGWFleetFront") for t in TIERS}
               | {"IF_HarW", "IF_HarProfile", "IF_TaskLen", "IF_TaskTokFresh", "IF_TaskTokCached", "IF_TaskTokDec", "IF_TaskTokSel", "IF_HarTokRatio"}
               | {f"IF_{p}_{t}" for p in ("TaskSucc", "TaskSuccSel", "CostSuccVR", "CostSuccGB", "RevSucc", "HarR") for t in TIERS})
    assert len(v59_new) == 41 and v59_new <= set(single_num + single_txt + wide + task), "v5.9 新增的 41 個下游名稱須全數涵蓋形狀檢查"
    v510_new = {f"IF_{p}_{t}" for p in ("CostAttVR", "HzEff") for t in TIERS} | {"IF_PFloor"} | set(front)
    assert len(v510_new) == 10 and EXPECT["downstream_names"] - len(v59_new) - len(v510_new) == 120   # v5.8 的下游名稱數 113＋v5.15 的 IF_Alloc* 7 個；v5.10 新增 10 個
    for n in (n for n in eng.names if n.startswith(("B4_", "B5_"))):                       # B4_／B5_：每個名稱都能取值（形狀不另規定）
        eng.get_name(n)
    mkt = eng.get_name("B4_MktChina")                                                       # v5.9：中國廠商旗標（1＝中國廠商），與國別欄同長
    assert len(mkt) == len(eng.get_name("B4_MktCountry")) and set(mkt) <= {0, 1} and 0 < sum(mkt) < len(mkt)


def _floor_engine(template, floor):
    eng = _clone(template)
    eng.set_key("B5_PFloor", floor)
    eng.evaluate_all()
    return eng


def test_floor_scenarios_expected_values(model, template_engine):
    """v5.10 M1：floor_0 與 floor_80 的期望值（與 parity 情境互補；parity 保證兩邊一致，這裡保證結果合理）。"""
    base = new_engine(model)
    names = base.get_name("IF_HdrTask")
    assert base.get_name("IF_PFloor") == 0.5                                              # 基準 p_min＝50%
    assert base.get_name("IF_FrontSuccVRName") == ["Luna｜標準", "Luna｜標準", "Luna｜選定", "Luna｜選定", "Sol｜選定"]
    assert abs(base.get_name("IF_FrontSuccVR")[4] - 0.0209) < 5e-5 and abs(base.get_name("IF_FrontSuccVRP")[4] - 0.627) < 5e-4
    f0 = _floor_engine(template_engine, 0)                                                          # 不設下限：前緣＝「對照（不設下限）」列
    cols = "CDEFG"
    assert [f0.get("Harness", f"{c}151") for c in cols] == [f0.get("Harness", f"{c}147") for c in cols]
    assert [f0.get("Harness", f"{c}152") for c in cols] == [f0.get("Harness", f"{c}148") for c in cols]
    assert f0.get_name("IF_FrontSuccVRName")[4] == "Luna｜選定" and abs(f0.get_name("IF_FrontSuccVR")[4] - 0.0125) < 5e-4
    f8 = _floor_engine(template_engine, 0.8)                                                        # 下限 80%：Coding agent 無合格
    assert f8.get_name("IF_FrontSuccVR")[4] == f8.get_name("IF_FrontSuccVRName")[4] == f8.get_name("IF_FrontSuccVRP")[4] == "無合格"
    assert f8.get_name("IF_FrontSuccVRName")[2:4] == ["Sol｜選定", "Sol｜選定"]            # 單代理、多代理研究
    assert f8.get("Checks", "B70") == 1, names                                            # 無合格任務數


def test_named_ranges_vs_libreoffice(model, tmp_path):
    """LibreOffice 存檔後的名稱範圍（正規化後）與原檔一致。"""
    src = tmp_path / model.name
    set_inputs(model, src, {})
    out = lo_recalc(src, tmp_path / "lo")
    import openpyxl
    lo = {k: v.attr_text.replace("$", "") for k, v in openpyxl.load_workbook(out).defined_names.items()}
    ours = {k: v.replace("$", "") for k, v in Engine(model).names.items()}
    assert lo == ours


FRESH_STATE = {}   # 情境 id → (全部公式格值, 全部具名範圍值)；由 test_scenario_parity 的重建實例填入


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_parity(sc, model, base_engine, template_engine, tmp_path, results_store):
    """情境：改寫輸入 → LibreOffice 重算（基準）→ 與引擎全部公式格比對。"""
    scen_xlsx = tmp_path / model.name
    set_inputs(model, scen_xlsx, sc["inputs"])
    ref = excel_values(lo_recalc(scen_xlsx, tmp_path / "lo"), base_engine[0].formula_cells)

    eng = _clone(template_engine, fresh=True)   # 每個情境獨立的重建實例；核心斷言不依賴快取（快取等價另見 test_cache_matches_fresh）
    for key, v in sc["inputs"].items():
        eng.set_key(key, v)
    t0 = time.perf_counter()
    got = eng.evaluate_all()
    elapsed = time.perf_counter() - t0
    FRESH_STATE[sc["id"]] = (got, {n: eng.get_name(n) for n in eng.names})   # 供 test_cache_matches_fresh 取用（同一個重建實例的結果）

    res = compare(got, ref)
    base = base_engine[1]                        # 防空轉：統計相對基準改變的格數（其中屬 Interface 者）
    changed = [k for k in base if base[k] != got[k]]
    results_store[sc["id"]] = {k: v for k, v in res.items() if k != "mismatches"} | {
        "n_mismatch": len(res["mismatches"]), "eval_all_seconds_after_change": round(elapsed, 2),
        "changed_cells": len(changed), "changed_interface_cells": sum(1 for s_, _ in changed if s_ == "Interface")}
    if sc["id"].startswith("h_alloc_"):          # v5.15 防空轉：Interface F 節（IF_Alloc*）至少一格改變；成長情境只改 Alloc 頁（見報告）
        sheet_ref = [base_engine[0].name_ref(n) for n in ALLOC_IF] if sc["id"] != "h_alloc_growth" else [("Alloc", None)]
        if sc["id"] != "h_alloc_growth":
            assert any(base[(s_, r_)] != got[(s_, r_)] for s_, r_ in sheet_ref if (s_, r_) in base), f"[{sc['id']}] Interface F 節未改變"
        else:
            assert any(s_ == "Alloc" for s_, _ in changed), f"[{sc['id']}] Alloc 頁未改變"
    assert elapsed < INCREMENTAL_LIMIT_S, f"[{sc['id']}] 改輸入後重算 {elapsed:.2f}s ≥ {INCREMENTAL_LIMIT_S}s"   # (a) 增量重算硬性門檻
    assert res["error_value_cells"] == 0, f"[{sc['id']}] 錯誤值 {res['error_value_cells']} 格（v5.9 起任何情境皆不得出現錯誤值；兩邊錯誤代碼不同亦視為不符）"
    if sc["id"] != "base":
        assert changed, f"[{sc['id']}] 未改變任何公式格（測試空轉）"
    assert not res["mismatches"], f"[{sc['id']}] " + format_mismatches(res["mismatches"])


@pytest.fixture(scope="session")
def cache_path(tmp_path_factory):
    """快取檔：CI 由 TOKENOMICS_ENGINE_CACHE 提供；本機未設定時建一次（約 75 秒）。"""
    env = os.environ.get("TOKENOMICS_ENGINE_CACHE")
    if env:
        return env
    p = tmp_path_factory.mktemp("cache") / "engine.pkl"
    Engine(current_model_path()).save_cache(p)
    return str(p)


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_cache_matches_fresh(sc, model, cache_path, results_store):
    """快取等價（2026-10-04 審查第 2 點）：同一組輸入，快取載入的實例與重建的實例，
    全部公式格與全部具名範圍精確比對（不用容差；型別也要相同），不符即失敗。
    重建實例即同片 test_scenario_parity 剛算完的那一個（同檔、同行程）；單獨執行本測試時才另建。"""
    if sc["id"] in FRESH_STATE:
        want_cells, want_names = FRESH_STATE[sc["id"]]
    else:
        fresh = new_engine(model, fresh=True)
        for key, v in sc["inputs"].items():
            fresh.set_key(key, v)
        want_cells = fresh.evaluate_all()
        want_names = {n: fresh.get_name(n) for n in fresh.names}
    t0 = time.perf_counter()
    eng = Engine(model, cache=cache_path)       # 每個情境獨立載入的實例
    load_s = time.perf_counter() - t0
    for key, v in sc["inputs"].items():
        eng.set_key(key, v)
    got_cells = eng.evaluate_all()
    bad_cells = [k for k in want_cells if want_cells[k] != got_cells[k] or type(want_cells[k]) is not type(got_cells[k])]
    def _same(a, b):                      # 具名範圍：值相等且型別相同（清單逐元素；PR #14 審查遺留項）
        if isinstance(a, list) or isinstance(b, list):
            return isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
        return a == b and type(a) is type(b)
    bad_names = [n for n in want_names if not _same(want_names[n], eng.get_name(n))]
    results_store.setdefault("_cache_equiv", {})[sc["id"]] = {
        "cells": len(want_cells), "names": len(want_names), "cell_mismatch": len(bad_cells),
        "name_mismatch": len(bad_names), "load_seconds": round(load_s, 1)}
    assert not bad_cells and not bad_names, (
        f"[{sc['id']}] 快取與重建不符：公式格 {len(bad_cells)}、具名範圍 {len(bad_names)}；"
        f"前 10 格 {[(k, want_cells[k], got_cells[k]) for k in bad_cells[:10]]}；前 5 名 {bad_names[:5]}")


def test_scenarios_actually_change_outputs(model, base_engine, template_engine, tmp_path):
    """防止測試空轉：每個情境至少改變 Interface 的一個格（相對基準）。"""
    base = base_engine[1]
    for sc in SCENARIOS[1:]:
        eng = _clone(template_engine)
        for key, v in sc["inputs"].items():
            eng.set_key(key, v)
        cur = eng.evaluate_all()
        changed = [k for k in base if base[k] != cur[k]]
        assert changed, f"{sc['id']} 未改變任何公式格"


# 效能門檻（CLAUDE.md 第 2 節）：兩條都是硬性。
#   (a) 增量重算 < 2 秒：每個情境改輸入後都要測。
#   (b) 全簿強制重算 < 2 秒：v5.12 以 SRC_Index 改寫 Gov_Map 查找後恢復（v5.11 暫行為 5 秒）。
FULL_RECALC_LIMIT_S = 2.0
INCREMENTAL_LIMIT_S = 2.0


def test_incremental_recalc_matches_fresh_and_is_fast(model, results_store):
    """同一實例連續改輸入再還原：結果須與全新實例相同；(a) 每個情境增量重算 < 2 秒（硬性）。"""
    eng = new_engine(model, fresh=True)
    base = eng.evaluate_all()
    names = eng.names
    base_orig = {a: eng.get(*resolve_key(names, a)) for sc in SCENARIOS[1:] for a in sc["inputs"]}   # 改動前的原值
    secs = {}                                                       # v5.17：各情境增量重算秒數（只輸出，不影響斷言）
    for sc in SCENARIOS[1:]:
        origs = {a: base_orig[a] for a in sc["inputs"]}
        t0 = time.perf_counter()
        for key, v in sc["inputs"].items():
            eng.set_key(key, v)
        eng.evaluate_all()
        dt = time.perf_counter() - t0
        secs[sc["id"]] = dt
        assert dt < INCREMENTAL_LIMIT_S, f"{sc['id']} 增量重算 {dt:.2f}s ≥ {INCREMENTAL_LIMIT_S}s"
        for key, v in origs.items():
            eng.set_key(key, v)
    worst = max(secs, key=secs.get)
    vals = sorted(secs.values())
    results_store["_incr_recalc"] = {"max_seconds": round(secs[worst], 2), "max_scenario": worst,
                                     "median_seconds": round(vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2, 2),
                                     "n": len(vals)}
    res = compare(eng.evaluate_all(), base)   # 還原後與基準相同（容差內；pycel 部分格以 15 位快取值回填）
    assert not res["mismatches"], format_mismatches(res["mismatches"])


def test_full_recalc_time(model, results_store):
    """(b) 全簿強制重算 < 2 秒（v5.12 恢復）。"""
    eng = new_engine(model, fresh=True)
    eng.evaluate_all()
    t0 = time.perf_counter()
    eng._xl.recalculate()                      # 強制全簿（全部公式格）重算
    full = time.perf_counter() - t0
    results_store["_full_recalc_seconds"] = round(full, 2)
    assert full < FULL_RECALC_LIMIT_S, f"全簿強制重算 {full:.2f}s ≥ {FULL_RECALC_LIMIT_S}s"


def test_alloc_expected_values_and_slo_text(model, template_engine):
    """v5.15 Block 6：基準值（工作單預期）與 SLO 不可達時回傳文字、無錯誤值（b_prod_derate、f_registry_t07_t09_on）。"""
    base = new_engine(model)
    assert abs(base.get_name("AL_DDaily") - 11.48) < 0.01                                 # 每日 token 約 11.5T
    assert abs(base.get_name("AL_ServeGWSpend") - 0.751) < 5e-4                           # 工作單 r3 更正 1
    assert abs(base.get_name("AL_RefGWyr") - 0.01808) < 5e-6                              # 工作單 r3 更正 2
    assert abs(base.get_name("AL_FamGWyr") - base.get("Fleet_1GW", "M33")) < 1e-12        # 家族計畫＝Fleet_1GW 第 33 列（VR200 欄）
    assert base.get_name("GOV_Errors") == 0 and sum(base.get_name("AL_SensCheck")) == 0
    for sid, inputs, text in (("f_registry_t07_t09_on", {"Tech_Registry!O11": 1, "Tech_Registry!O12": 1, "Tech_Registry!O13": 1}, True),
                              ("b_prod_derate", {"Serving!C18": 0.7}, False)):
        eng = _clone(template_engine)
        for k, v in inputs.items():
            eng.set_key(k, v)
        eng.evaluate_all()
        for n in ALLOC_IF:                                                                  # 每個 IF_Alloc*：數值或文字「SLO 不可達」，不得為錯誤值
            v = eng.get_name(n)
            assert (isinstance(v, (int, float)) and not isinstance(v, bool)) or v == "SLO 不可達", (sid, n, v)
        assert eng.get_name("GOV_Errors") == 0, sid
        if text:                                                                            # SLO 不可達：Q1、Q2、服務 GW 回傳文字
            assert eng.get_name("IF_AllocQ1") == eng.get_name("IF_AllocQ2") == eng.get_name("IF_AllocServeGW") == "SLO 不可達", sid
        else:                                                                               # 生產折減 0.7 仍可服務：回傳數值（Q1 約 48.8%）
            assert abs(eng.get_name("IF_AllocQ1") - 0.4876) < 5e-4, (sid, eng.get_name("IF_AllocQ1"))


def test_alloc_mix_2025_expected_values(model, template_engine):
    """補充 2：2025 機隊 Hopper 60%／GB200 40%（h_alloc_mix_2025）的期望值（chat 端獨立重算）。"""
    eng = _clone(template_engine)
    for k, v in {"AL_MixHopper": 0.6, "AL_MixGB200": 0.4, "AL_MixGB300": 0, "AL_MixVR200": 0}.items():
        eng.set_key(k, v)
    eng.evaluate_all()
    for n, want in (("IF_AllocServeGW", 0.13724), ("AL_ServeGWSpend", 0.86022), ("IF_AllocQ1", 0.36945), ("IF_AllocQ2", 0.41972)):
        assert abs(eng.get_name(n) - want) < 5e-6, (n, eng.get_name(n))
    assert eng.get_name("GOV_Errors") == 0


def test_l1_v516_expected_values_and_h3(model):
    """v5.16：L1 毛利率兩列、GPU 小時口徑、第 7、8 題的基準期望值（工作單第 1 節；chat 端計算，精度到小數第 5 位故容差 5e-6），H3＝0。"""
    eng = new_engine(model)
    want = {"L1_Ans5_GM": (0.95589, 0.92435, 0.96810), "L1_Ans5_FullMargin": (0.93485, 0.88826, 0.95289),
            "L1_Ans6_GPUh": (0.25576, 0.25576, 0.25576), "L1_Ans7": (1.0, 1.0, 1.0), "L1_Ans8": (0.47934, 0.47934, 0.47934)}
    for n, (d, lo, hi) in want.items():
        for suffix, v in (("", d), ("_Lo", lo), ("_Hi", hi)):
            got = eng.get_name(n + suffix)
            assert abs(got - v) < 5e-6, (n + suffix, got, v)
        assert lo <= d <= hi
    assert eng.get_name("CHK_L1Order") == 0                                              # H3（WARN）：基準 0；以具名範圍讀，不查標籤（快取不含常數標籤格）
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("GOV_Warnings") == 241 and eng.get_name("GOV_Info") == 103

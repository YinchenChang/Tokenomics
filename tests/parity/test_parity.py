"""Excel（LibreOffice 重算）與 engine 的一致性測試（CLAUDE.md 第 3 節）。

比對範圍：全部公式格；具名範圍名稱與 attr_text；17 個情境（含 v5.11 兩個治理情境）各以獨立引擎實例重算。
"""
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


@pytest.fixture(scope="module")
def model():
    return current_model_path()


@pytest.fixture(scope="module")
def base_engine(model):
    """基準引擎（只讀）：供防空轉統計與公式格清單，避免每個情境重複建圖。"""
    eng = new_engine(model)
    return eng, eng.evaluate_all()


def new_engine(model):
    """回傳全新的引擎實例（每次建圖並重算，約 50 秒）。
    曾評估以 deepcopy 範本共用建圖結果（第 12 輪第 7 點）：總時長可由約 37 分降至約 10 分，但複本偶發
    'NoneType' has no attribute 'get_range'，且複本的重算變慢（4.9–6.2 秒），不採用。"""
    return Engine(model)


@pytest.fixture(scope="module")
def template_engine(model):
    return model


def _clone(model):
    return new_engine(model)


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
    assert sum(n.startswith("CST_") for n in eng.names) == EXPECT["cst_names"] and sum(n.startswith("IDX_") for n in eng.names) == EXPECT["idx_names"]   # v5.12
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
    assert len(v510_new) == 10 and EXPECT["downstream_names"] - len(v59_new) - len(v510_new) == 113   # v5.8 的下游名稱數；v5.10 新增 10 個
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


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_parity(sc, model, base_engine, template_engine, tmp_path, results_store):
    """情境：改寫輸入 → LibreOffice 重算（基準）→ 與引擎全部公式格比對。"""
    scen_xlsx = tmp_path / model.name
    set_inputs(model, scen_xlsx, sc["inputs"])
    ref = excel_values(lo_recalc(scen_xlsx, tmp_path / "lo"), base_engine[0].formula_cells)

    eng = _clone(template_engine)               # 每個情境獨立實例（deepcopy 範本），不受前一情境影響
    for key, v in sc["inputs"].items():
        eng.set_key(key, v)
    t0 = time.perf_counter()
    got = eng.evaluate_all()
    elapsed = time.perf_counter() - t0

    res = compare(got, ref)
    base = base_engine[1]                        # 防空轉：統計相對基準改變的格數（其中屬 Interface 者）
    changed = [k for k in base if base[k] != got[k]]
    results_store[sc["id"]] = {k: v for k, v in res.items() if k != "mismatches"} | {
        "n_mismatch": len(res["mismatches"]), "eval_all_seconds_after_change": round(elapsed, 2),
        "changed_cells": len(changed), "changed_interface_cells": sum(1 for s_, _ in changed if s_ == "Interface")}
    assert elapsed < INCREMENTAL_LIMIT_S, f"[{sc['id']}] 改輸入後重算 {elapsed:.2f}s ≥ {INCREMENTAL_LIMIT_S}s"   # (a) 增量重算硬性門檻
    assert res["error_value_cells"] == 0, f"[{sc['id']}] 錯誤值 {res['error_value_cells']} 格（v5.9 起任何情境皆不得出現錯誤值；兩邊錯誤代碼不同亦視為不符）"
    if sc["id"] != "base":
        assert changed, f"[{sc['id']}] 未改變任何公式格（測試空轉）"
    assert not res["mismatches"], f"[{sc['id']}] " + format_mismatches(res["mismatches"])


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


def test_incremental_recalc_matches_fresh_and_is_fast(model):
    """同一實例連續改輸入再還原：結果須與全新實例相同；(a) 每個情境增量重算 < 2 秒（硬性）。"""
    eng = new_engine(model)
    base = eng.evaluate_all()
    names = eng.names
    base_orig = {a: eng.get(*resolve_key(names, a)) for sc in SCENARIOS[1:] for a in sc["inputs"]}   # 改動前的原值
    for sc in SCENARIOS[1:]:
        origs = {a: base_orig[a] for a in sc["inputs"]}
        t0 = time.perf_counter()
        for key, v in sc["inputs"].items():
            eng.set_key(key, v)
        eng.evaluate_all()
        dt = time.perf_counter() - t0
        assert dt < INCREMENTAL_LIMIT_S, f"{sc['id']} 增量重算 {dt:.2f}s ≥ {INCREMENTAL_LIMIT_S}s"
        for key, v in origs.items():
            eng.set_key(key, v)
    res = compare(eng.evaluate_all(), base)   # 還原後與基準相同（容差內；pycel 部分格以 15 位快取值回填）
    assert not res["mismatches"], format_mismatches(res["mismatches"])


def test_full_recalc_time(model, results_store):
    """(b) 全簿強制重算 < 2 秒（v5.12 恢復）。"""
    eng = new_engine(model)
    eng.evaluate_all()
    t0 = time.perf_counter()
    eng._xl.recalculate()                      # 強制全簿（全部公式格）重算
    full = time.perf_counter() - t0
    results_store["_full_recalc_seconds"] = round(full, 2)
    assert full < FULL_RECALC_LIMIT_S, f"全簿強制重算 {full:.2f}s ≥ {FULL_RECALC_LIMIT_S}s"

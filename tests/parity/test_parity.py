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


PROD_IF = tuple(f"{b}_Prod" for b in ("IF_FullCost_Luna", "IF_FullCost_Sol", "IF_FullCost_Astra", "IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet"))   # v5.19 X1
# v5.23 X10：VR200 欄（第 4 個）因 Perf_Batch 側 η_d 倍數 0.75 而改變（0.85：sol 0.2551→0.2567、astra 0.3313→0.3373；0.7：sol 0.6901→0.6955、astra 0.9923→1.0135），其餘欄不變
# 相對基準列的變動（LibreOffice 重算值；欄序 Hopper、GB200、GB300、VR200、Rubin Ultra 的基準成本欄；0.85 預設、0.7 區間下限）
EXPECT_PROD_085 = {"sol": (0.4900, 0.2776, 0.2775, 0.2567, 0.2497), "astra": (1.0400, 0.3938, 0.4444, 0.3373, 0.3119), "fleet": (-0.4399, -0.2424, -0.2678, -0.2177, -0.2105)}
EXPECT_PROD_070 = {"sol": (0.7763, 0.7805, 0.6955, 0.6703), "astra": (1.2922, 1.6333, 1.0135, 0.9098)}      # 欄序 GB200、GB300、VR200、Rubin Ultra（Hopper 為文字）
V526_IF = ("IF_DeprLifeIT", "IF_DeprIT", "IF_DeprFac", "IF_AvgDraw", "IF_PowerPrice", "IF_MaintIT", "IF_MaintFac", "IF_StaffSW", "IF_TaxIns", "IF_OpexGW")   # v5.26 Interface I 節
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


def test_readme_version_consistency(model):
    """v5.21：README!A1 的版本號（"Tokenomics vX.YY —"）、README!B5 開頭的檔名、model/CURRENT 的檔名三者一致。"""
    import re
    import openpyxl
    cur = (model.parent / "CURRENT").read_text(encoding="utf-8").strip()
    m_cur = re.fullmatch(r"(\d{8}_Tokenomics_)(v\d+\.\d+)\.xlsx", cur)
    assert m_cur, f"model/CURRENT 檔名格式不符：{cur}"
    ws = openpyxl.load_workbook(model, read_only=True)["README"]
    a1, b5 = ws["A1"].value, ws["B5"].value
    m_a1 = re.match(r"Tokenomics (v\d+\.\d+) —", a1)
    assert m_a1, f"README!A1 版本格式不符：{a1[:40]}"
    assert m_a1.group(1) == m_cur.group(2), f"README!A1 版本 {m_a1.group(1)} ≠ model/CURRENT 版本 {m_cur.group(2)}"
    assert b5.startswith(cur[: -len(".xlsx")]), f"README!B5 開頭應為 {cur[:-5]}，實際：{b5[:40]}"


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
    assert len(if_all) == EXPECT["downstream_names"] + 3 and sum(n.startswith("IF_Hdr") for n in eng.names) == 3   # 198＝195 下游＋IF_Hdr 3（v5.31；v5.30 為 195＝192＋3）（IF_HdrGen、IF_HdrCost、IF_HdrTask）
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
    v519_new = set(PROD_IF)                                                                   # v5.19 X1：Interface G 節 7 個 _Prod 名稱（15 欄；數值或「SLO 不可達」）
    assert len(v519_new) == 7 and v519_new <= set(eng.names)
    for n in v519_new:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == 15 and all((isinstance(x, (int, float)) and not isinstance(x, bool)) or x == "SLO 不可達" for x in v), f"{n}: {v!r}"
    v522_new = {f"{n}_Life" for n in ("IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet")}   # v5.22 X7：Interface H 節 4 個 _Life 名稱（15 欄；數值或「SLO 不可達」）
    assert len(v522_new) == 4 and v522_new <= set(eng.names)
    for n in v522_new:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == 15 and all((isinstance(x, (int, float)) and not isinstance(x, bool)) or x == "SLO 不可達" for x in v), f"{n}: {v!r}"
    v526_new = set(V526_IF)                                                                    # v5.26：Interface I 節 10 個 DC_Cost 構件名稱（15 欄；數值）
    assert len(v526_new) == 10 and v526_new <= set(eng.names)
    for n in v526_new:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == 15 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v), f"{n}: {v!r}"
    v531_new = {"IF_MaintITWarr", "IF_MaintITPost"}                                            # v5.31 X17：Interface I 節（續）2 個 15 欄名稱（數值）＋單格 IF_WarrantyYrs（X18）
    for n in v531_new:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == 15 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v), f"{n}: {v!r}"
    v = eng.get_name("IF_WarrantyYrs"); assert not isinstance(v, list) and isinstance(v, (int, float)) and not isinstance(v, bool), v
    v531_new |= {"IF_WarrantyYrs"}
    assert len(v510_new) == 10 and EXPECT["downstream_names"] - len(v59_new) - len(v510_new) - len(v519_new) - len(v522_new) - len(v526_new) - len(v531_new) == 120   # v5.31 新增 3 個； v5.8 的下游名稱數 113＋v5.15 的 IF_Alloc* 7 個；v5.10 新增 10 個；v5.19 新增 7 個；v5.22 新增 4 個；v5.26 新增 10 個
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
    # v5.31 J2：VR200 每成功任務成本隨 IT 維護下降（Coding agent 前緣 0.0222 → 0.0213；不設下限 0.0135 → 0.0129）
    assert abs(base.get_name("IF_FrontSuccVR")[4] - 0.0213) < 5e-5 and abs(base.get_name("IF_FrontSuccVRP")[4] - 0.627) < 5e-4
    f0 = _floor_engine(template_engine, 0)                                                          # 不設下限：前緣＝「對照（不設下限）」列
    cols = "CDEFG"
    assert [f0.get("Harness", f"{c}151") for c in cols] == [f0.get("Harness", f"{c}147") for c in cols]
    assert [f0.get("Harness", f"{c}152") for c in cols] == [f0.get("Harness", f"{c}148") for c in cols]
    assert f0.get_name("IF_FrontSuccVRName")[4] == "Luna｜選定" and abs(f0.get_name("IF_FrontSuccVR")[4] - 0.0129) < 5e-4
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
    if sc["id"] == "h_prod_derate_070":          # v5.19 X1 防空轉：至少一個 _Prod 列改變；基準列（IF_FullCost_*、IF_RevGW_*）一格都不變
        assert any(base_engine[0].get_name(n) != eng.get_name(n) for n in PROD_IF), f"[{sc['id']}] _Prod 列未改變"
        assert all(base_engine[0].get_name(n[:-5]) == eng.get_name(n[:-5]) for n in PROD_IF), f"[{sc['id']}] 基準列被改動（Serving!C18 未動，基準列不得變）"
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
    assert abs(base.get_name("AL_DDaily") - 16.48) < 0.01                                 # v5.29 X14 (l)：每則提示 token 數 2,000 → 4,000，每日 token 11.48 → 16.48T
    assert abs(base.get_name("AL_ServeGWSpend") - 1.21964) < 5e-5                        # v5.31 J1／J2：1.11399 → 1.21964（支出 ÷ 持有成本，持有成本下降）；v5.29 X14 (k)：支出路線服務 GW 改連 SRC_DEM_018 12.6（r2：只有這條路線用 018；004 維持 Active），0.74266 → 1.11399（LibreOffice 重算值）
    assert abs(base.get_name("AL_RefGWyr") - 0.0210207) < 5e-6                             # v5.18：0.01808→0.018153；v5.23 X10：→0.0210207（＝v5.22 暫存複本 L、M、N 欄第 53 列 ×0.75 的 LibreOffice 重算值）
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
        if sid == "b_prod_derate":                                                          # v5.30 X15 (a)：C18＝0.7 而 CTL_ProdDerate＝0.85 時，G 節（以 0.85 取代 C18 重解）> D 節（0.7），
            assert eng.get("Checks", "D120") == 57 and eng.get_name("GOV_Errors") == 57, sid  # 營收列 _Prod > _Util，K3 單調檢查依工作單計 ERROR（57 格；其餘 ERROR 0）；見 v5.30 報告「待 Project 判斷」第 1 項
        else:
            assert eng.get_name("GOV_Errors") == 0, sid
        if text:                                                                            # SLO 不可達：Q1、Q2、服務 GW 回傳文字
            assert eng.get_name("IF_AllocQ1") == eng.get_name("IF_AllocQ2") == eng.get_name("IF_AllocServeGW") == "SLO 不可達", sid
        else:                                                                               # 生產折減 0.7 仍可服務：回傳數值（Q1 約 52.1%；v5.23 X10 前為 48.5%）
            assert abs(eng.get_name("IF_AllocQ1") - 0.4570) < 5e-4, (sid, eng.get_name("IF_AllocQ1"))      # v5.29 X14 (l)：0.5213 → 0.4570（服務 GW 隨每則 token 數上升）


def test_alloc_mix_2025_expected_values(model, template_engine):
    """補充 2：2025 機隊 Hopper 60%／GB200 40%（h_alloc_mix_2025）的期望值（chat 端獨立重算）。"""
    eng = _clone(template_engine)
    for k, v in {"AL_MixHopper": 0.6, "AL_MixGB200": 0.4, "AL_MixGB300": 0, "AL_MixVR200": 0}.items():
        eng.set_key(k, v)
    eng.evaluate_all()
    for n, want in (("IF_AllocServeGW", 0.182593), ("AL_ServeGWSpend", 1.347144), ("IF_AllocQ1", 0.331841), ("IF_AllocQ2", 0.393635)):   # v5.31：AL_ServeGWSpend 1.295514 → 1.347144、IF_AllocQ2 0.394559 → 0.393635（持有成本下降；LibreOffice 重算值）； v5.29 X14 (k)(l)：0.140315／0.863676／0.392575／0.458889 → 本列（引擎重算值，與 LibreOffice 一致）
        assert abs(eng.get_name(n) - want) < 5e-6, (n, eng.get_name(n))
    assert eng.get_name("GOV_Errors") == 0


def test_l1_v516_expected_values_and_h3(model):
    """v5.16：L1 毛利率兩列、GPU 小時口徑、第 7、8 題的基準期望值（工作單第 1 節；chat 端計算，精度到小數第 5 位故容差 5e-6），H3＝0。"""
    eng = new_engine(model)
    want = {"L1_Ans5_GM": (0.95505, 0.92739, 0.96503), "L1_Ans5_FullMargin": (0.93324, 0.89216, 0.94805),     # v5.31 J1／J2：持有成本下降，毛利率上升（LibreOffice 重算值）； v5.18：LibreOffice 重算值（v5.16 為 chat 端計算）；v5.23 X10：FullMargin 與 GPUh 改為 k＝0.75 暫存複本的 LibreOffice 重算值
            "L1_Ans6_GPUh": (0.28231, 0.28231, 0.28231), "L1_Ans7": (1.0, 1.0, 1.0), "L1_Ans8": (0.47940, 0.47940, 0.47940)}      # v5.31：Ans8 0.47928 → 0.47940
    for n, (d, lo, hi) in want.items():
        for suffix, v in (("", d), ("_Lo", lo), ("_Hi", hi)):
            got = eng.get_name(n + suffix)
            assert abs(got - v) < 5e-6, (n + suffix, got, v)
        assert lo <= d <= hi
    assert eng.get_name("CHK_L1Order") == 0                                              # H3（WARN）：基準 0；以具名範圍讀，不查標籤（快取不含常數標籤格）
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("GOV_Warnings") == 221 and eng.get_name("GOV_Info") == 168      # v5.31：Warnings 220 → 221（W1：SRC_DC_014 IREN、SRC_DC_017 DGX 利害關係方無第二來源 +2，SRC_HW_007 改 Alt −1）；Info 165 → 168（I3 15 → 17：L1_GPUhr_GB300_vsBE、L1_GapProduct 判讀改「差距 >20%」；I8 53 → 54：Spec_Rack E12 標記變更）；v5.29 r2：Info 108 → 165（I3 8 → 15：新增 L1 列判讀「差距 >20%」7 列——FleetMargin 與 HoldEconMW_GB300 外部欄依 r2 第 11 項改「—」；K4 0（r2 第 2 項：比對含 CTL_ProdDerate × L × m）；K5 50；K6 0；K7 0）；Warnings 219 → 220（W1：SRC_DEM_018 利害關係方無第二來源 +1；SRC_DEM_004 依 r2 維持 Active；K1 0）；v5.27：W1 213 → 219（SRC_MOD_057–062 Kimi K3 為利害關係方、無第二來源）；I3 7 → 8（L1 第 39 列新增外部對照，判讀「差距 >20%」）；v5.25：W1 209 → 213


def _pct(eng, n, k):
    """_Prod 相對基準列的變動（第 k 欄，0 起算）；任一邊為文字時回傳 None"""
    p, b = eng.get_name(n)[k], eng.get_name(n[:-5])[k]
    return p / b - 1 if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (p, b)) else None


def test_prod_derate_expected_values(model, template_engine):
    """v5.19 X1（工作單 1.5 節；LibreOffice 重算值）：CTL_ProdDerate 預設 0.85 與 0.7 下，_Prod 列相對基準列的變動；自我檢查 X1＝0。
    欄序：5 世代 × 3 成本情境（低／基準／高），基準欄索引 1、4、7、10、13＝Hopper、GB200、GB300、VR200、Rubin Ultra。"""
    base = new_engine(model)
    assert base.get_name("CTL_ProdDerate") == 0.85 and base.get("Serving", "C18") == 1.0   # C18 維持 1.0（G0-11）
    assert base.get_name("GOV_Errors") == 0                                               # 含 Checks X1（替代值改回 C18 時七列等於基準列）
    want = {"IF_FullCost_Sol_Prod": EXPECT_PROD_085["sol"], "IF_FullCost_Astra_Prod": EXPECT_PROD_085["astra"], "IF_RevGWFleet_Prod": EXPECT_PROD_085["fleet"]}
    for n, vals in want.items():
        for k, v in zip((1, 4, 7, 10, 13), vals):
            assert abs(_pct(base, n, k) - v) < 5e-4, (n, k, _pct(base, n, k), v)
    eng = _clone(template_engine)
    eng.set_key("CTL_ProdDerate", 0.7)
    eng.evaluate_all()
    assert eng.get_name("GOV_Errors") == 0
    for n in ("IF_FullCost_Luna_Prod", "IF_FullCost_Sol_Prod", "IF_FullCost_Astra_Prod"):
        assert eng.get_name(n)[1] == "SLO 不可達", n                                      # Hopper：Astra 層 SLO 不可達 → 機隊不可服務 → 全成本為文字
    for n, vals in (("IF_FullCost_Sol_Prod", EXPECT_PROD_070["sol"]), ("IF_FullCost_Astra_Prod", EXPECT_PROD_070["astra"])):
        for k, v in zip((4, 7, 10, 13), vals):
            assert abs(_pct(eng, n, k) - v) < 5e-4, (n, k, _pct(eng, n, k), v)


LIFE_IF = ("IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet")                  # v5.22 X7：各自的 _Life 並列列
# v5.29 X14 (k)(l)：兩個核准的輸入值變動（SRC_DEM_018 新增，支出路線服務 GW 改用 12.6 $B（r2：比例類公式仍用 SRC_DEM_004）；Alloc_In 每則提示 token 數 2,000 → 4,000）連動改變的名稱——
# Alloc 鏈（AL_D*、AL_Serve*、AL_Q*、AL_Implied*、AL_J8Gap、AL_SpendRatio、AL_FreeSpendShare、AL_FreeServeShare、AL_Sens*、AL_TokPerPrompt*）、Interface F 節 IF_Alloc*、
# L1_Ans1／Ans2／ExtServeGW／ExtFreeShare／ExtDaily（含 _Lo／_Hi）；test_batch_etad_expected_values 比對 v5.22 時略過（與 X10 無關）
V529_INPUT_CHANGED = frozenset(
    ["AL_D", "AL_DChat", "AL_DChatFree", "AL_DChatPaid", "AL_DDaily", "AL_DFree", "AL_DPaid", "AL_FreeServeShare", "AL_FreeSpendShare", "AL_ImpliedNk", "AL_ImpliedRDGW",
     "AL_J8Gap", "AL_Q1", "AL_Q1R2", "AL_Q1g", "AL_Q2", "AL_Q2g", "AL_SensDaily", "AL_SensQ1", "AL_SensQ2", "AL_ServeGW", "AL_ServeGWFree", "AL_ServeGWPaid", "AL_ServeGWSpend",
     "AL_ServeGen", "AL_SpendRatio", "AL_TokPerPrompt", "AL_TokPerPrompt_Hi", "AL_TokPerPrompt_Lo"]
    + list(ALLOC_IF) + [f"L1_{k}{s}" for k in ("Ans1", "Ans2", "ExtDaily", "ExtFreeShare", "ExtServeGW") for s in ("", "_Lo", "_Hi")])


def test_price_life_expected_values(model, template_engine):
    """v5.22 X7（工作單 1.3、1.4 節）：基準 L＝m＝1 時四個 _Life 列＝基準列；h_price_life_050（L＝0.5、m＝0.8）時 60 格 _Life＝基準 × 0.4，
    基準列、L1、Interface 第 1–210 列不變；錯誤值 0；Checks X7（GOV_Errors）＝0。基準列為文字時 _Life 為相同文字。"""
    import re
    base = new_engine(model)
    assert base.get_name("CTL_PriceLife") == 1 and base.get_name("CTL_Monetize") == 1
    for n in LIFE_IF:
        assert base.get_name(n + "_Life") == base.get_name(n), n
    assert base.get_name("GOV_Errors") == 0
    base_vals = base.evaluate_all()
    eng = _clone(template_engine)
    eng.set_key("CTL_PriceLife", 0.5)
    eng.set_key("CTL_Monetize", 0.8)
    cur = eng.evaluate_all()
    assert eng.get_name("GOV_Errors") == 0
    changed = 0
    for n in LIFE_IF:
        b, life = eng.get_name(n), eng.get_name(n + "_Life")
        assert len(b) == len(life) == 15, n
        for k, (x, y) in enumerate(zip(b, life)):
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                assert abs(y - x * 0.4) <= 1e-9 * max(1.0, abs(x)), (n, k, x, y)
                changed += y != x
            else:
                assert y == x, (n, k, x, y)          # 基準列為文字（SLO 不可達）→ 相同文字
    assert changed > 0                               # 防空轉：至少一格 _Life 改變
    fm_row = int(re.sub(r"[A-Z]+", "", base.names["L1_FleetMargin"].rsplit("!", 1)[1].replace("$", "")))   # v5.29 X14 (c)：L1_FleetMargin 含 CTL_PriceLife × CTL_Monetize，該列隨情境改變
    for (sh, coord), v in cur.items():               # 基準列、L1、Interface 第 1–210 列、其他模型頁：數值不變（只允許 Theory_Rev D 節、Interface H 節、Checks X7 與其彙總；v5.29 起另允許 L1_FleetMargin 列）
        row = int(re.sub(r"[A-Z]+", "", coord))
        if (sh == "L1" and row != fm_row) or (sh == "Interface" and row <= 210):
            assert v == base_vals[(sh, coord)], (sh, coord, base_vals[(sh, coord)], v)
    assert not any(isinstance(v, str) and v.startswith("#") for v in cur.values())


# ── v5.23 X10：Perf_Batch 側 VR200 批次口徑 η_d 倍數（工作單 1.3、1.4 節） ──
BATCH_PREV = HERE.parent.parent / "model" / "archive" / "20261006_Tokenomics_v5.22.xlsx"        # v5.22（LibreOffice 重算存檔）：X10 之前的口徑
# v5.22 報告第三節 k＝0.75 的結果（VR200 欄相對 k＝1 的變動；報告取兩位小數，容差 6e-5＝0.006 個百分點）
EXPECT_BATCH_075 = {"IF_TrainCost_Luna": {10: 0.1434, 11: 0.1434, 12: 0.1434}, "IF_TrainCost_Sol": {10: 0.1082, 11: 0.1082, 12: 0.1082},
                    "IF_TrainCost_Astra": {10: 0.0921, 11: 0.0921, 12: 0.0921}, "TRN_GPUhRL": {10: 0.1426, 11: 0.1459, 12: 0.1596},
                    "IF_FullCost_Luna": {11: 0.0020}, "IF_FullCost_Sol": {11: 0.0055}, "IF_FullCost_Astra": {11: 0.0287}}
# v5.29 X14 (k)(l)：L1_Ans1 0.0452 → 0.0530（Q1 對研發 GW 的彈性隨服務 GW 上升而改變；引擎重算值 0.052959；不受 Alloc 輸入影響的其餘項不變）
EXPECT_BATCH_075_SCALAR = {"L1_Ans1": 0.0530, "L1_Ans3": 0.1241, "L1_Ans6_GPUh": 0.1039, "L1_Ans5_FullMargin": -0.0003,
                           "L1_RLshare_Sol_VR200": 0.1459, "L1_RLshare_Astra_VR200": 0.1596}
EXPECT_BATCH_075_RATIO = (1.762, 1.811, 1.923)      # Perf_Batch 第 88 列 VR200（L、M、N）÷ GB300（I、J、K）；k＝1 時為 2.350、2.414、2.564


# v5.31 J1／J2（Andy 2026-10-08「不反對，請繼續」）：GB300 機架價格與 IT 維護等值費率改變成本鏈；test_batch_etad_expected_values 比對 v5.22 時，
# 略過「v5.30 → v5.31 值有改變」的具名範圍（以兩版 LibreOffice 重算存檔逐名稱比較；與 X10 無關）
V530_PREV = HERE.parent.parent / "model" / "archive" / "20261008_Tokenomics_v5.30.xlsx"


def _names_changed_v531(model):
    import openpyxl
    from openpyxl.utils import range_boundaries
    a, b = openpyxl.load_workbook(V530_PREV, data_only=True), openpyxl.load_workbook(model, data_only=True)
    out = set()
    for n, dn in a.defined_names.items():
        if n not in b.defined_names: continue
        vals = []
        for wb, t in ((a, dn.attr_text), (b, b.defined_names[n].attr_text)):
            sh, rg = t.rsplit("!", 1)
            c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
            vals.append([wb[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)])
        if len(vals[0]) != len(vals[1]) or not all(_same(x, y) for x, y in zip(*vals)):
            out.add(n)
    return out


def _flat(v):
    if isinstance(v, list):
        return [x for r in v for x in _flat(r)]
    return [v]


def _same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return (a in (None, "") and b in (None, "")) or a == b


def test_batch_etad_expected_values(model):
    """v5.23 X10：基準 CAL_BatchEtaD＝[1,1,1,0.75,1]；h_batch_etad_100（VR200 設回 1）時，v5.22 的全部具名範圍（除 IDX_SrcID：SRC_Index 新增哨兵列）逐格相等
    ——只有 X10 造成改變；k＝0.75 相對 k＝1 的變動等於 v5.22 報告第三節；改變的具名範圍恰為 85 個（報告 82 個＋3 個對應的 _Prod）；
    IF_TrainGenDefault 仍為 4；TR_*、IF_RevGW_*、IF_RevGWFleet、_Life 不變；GOV_Errors＝0（Checks X1 的 _Prod 自我檢查維持 0）。"""
    import openpyxl
    from openpyxl.utils import range_boundaries
    base = new_engine(model)
    assert base.get_name("CAL_BatchEtaD") == [1, 1, 1, 0.75, 1]
    assert base.get_name("GOV_Errors") == 0 and base.get_name("IF_TrainGenDefault") == 4
    eng = _clone(model)
    eng.set_key("CAL_BatchEtaD[4]", 1.0)
    cur = eng.evaluate_all()
    assert not any(isinstance(v, str) and v.startswith("#") for v in cur.values()) and eng.get_name("GOV_Errors") == 0
    prev = openpyxl.load_workbook(BATCH_PREV, data_only=True)
    v531_changed = _names_changed_v531(model)
    assert "IF_HoldEcon" in v531_changed and "IF_RevGW_Sol" not in v531_changed and "TRN_GPUhRL" not in v531_changed
    bad = []
    for n, dn in prev.defined_names.items():
        # v5.25：新增 SRC 紀錄使 SRC_Index 堆疊位移、W1 計數改變；IDX_*、GOV_* 不屬 X10 範圍（GOV_Errors＝0 已於上方另行斷言）
        if n.startswith(("IDX_", "GOV_")):
            continue
        if n in V529_INPUT_CHANGED:      # v5.29 X14 (k)(l)：Andy 核准的輸入值變動（推論支出 SRC_DEM_018、每則提示 token 數 4,000）使 Alloc 鏈 50 個名稱與 v5.22 不同；與 X10 無關
            continue
        if n in v531_changed:            # v5.31 J1／J2：GB300 機架價格、IT 維護等值費率改變的成本鏈名稱；與 X10 無關
            continue
        sh, rg = dn.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(eng.get_name(n))
        if len(want) != len(got) or not all(_same(a, b) for a, b in zip(want, got)):
            bad.append(n)
    assert not bad, f"k＝1 時與 v5.22 不符的具名範圍：{bad[:20]}"
    changed = [n for n in base.names if n != "IDX_SrcID" and n in prev.defined_names
               and not all(_same(a, b) for a, b in zip(_flat(base.get_name(n)), _flat(eng.get_name(n))))]
    assert len(changed) == 85, len(changed)
    by = {p: sum(n.startswith(p) for n in changed) for p in ("IF_", "L1_", "AL_", "TRN_")}
    assert by == {"IF_": 41, "L1_": 21, "AL_": 15, "TRN_": 8} and sum(n.endswith("_Prod") for n in changed) == 3, by       # 82＝IF 38＋L1 21＋TRN 8＋AL 15
    assert not [n for n in changed if n.startswith(("TR_", "IF_RevGW")) or n.endswith("_Life") or n == "IF_TrainGenDefault"]
    for n, idx in EXPECT_BATCH_075.items():
        a, b = base.get_name(n), eng.get_name(n)
        for k, v in idx.items():
            assert abs(a[k - 1] / b[k - 1] - 1 - v) < 6e-5, (n, k, a[k - 1] / b[k - 1] - 1, v)
    for n, v in EXPECT_BATCH_075_SCALAR.items():
        a, b = base.get_name(n), eng.get_name(n)
        a, b = (a[0], b[0]) if isinstance(a, list) else (a, b)
        assert abs(a / b - 1 - v) < 6e-5, (n, a / b - 1, v)
    for col_vr, col_gb, want in zip("LMN", "IJK", EXPECT_BATCH_075_RATIO):
        assert abs(base.get("Perf_Batch", f"{col_vr}88") / base.get("Perf_Batch", f"{col_gb}88") - want) < 6e-4
    for n in ("IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet"):          # 營收不經 Perf_Batch 第 53 列
        assert all(_same(a, b) for a, b in zip(_flat(base.get_name(n)), _flat(eng.get_name(n)))), n


# ── v5.29 X14（工作單 docs/workorders/20261008_v5.29.md r1＋r2）：輸出契約欄、四層瀑布、損益兩平、Load_Bearing、落差分解 ──
IFW_BASES = ("RevGW_Luna", "RevGW_Sol", "RevGW_Astra", "RevGWFleet", "RevGWFront_Luna", "RevGWFront_Sol", "RevGWFront_Astra", "RevGWFleetFront", "TokGW_Luna", "TokGW_Sol", "TokGW_Astra")


def test_v529_contract_waterfall_expected_values(model):
    """v5.29：IFC_ 四欄與 Interface 資料列同長且值域正確；IFW_ 44 個名稱各 15 欄；有對應列的 _Util／_Prod／_Life 逐格等於來源列（Checks K3＝0）；
    L1 新列的 LibreOffice 重算值（工作單第 3、3b 節）；Checks K2、K3＝0、K4＝0（r2 第 2 項：L1_FleetMargin＝Theory_Rev 機隊比值 × CTL_ProdDerate × CTL_PriceLife × CTL_Monetize）、K5＝50；GOV_Errors＝0。"""
    eng = new_engine(model)
    conf, use, layer, upd = (eng.get_name(n) for n in ("IFC_Conf", "IFC_Use", "IFC_Layer", "IFC_Updated"))
    assert len(conf) == len(use) == len(layer) == len(upd) >= 300
    assert set(x for x in conf if x not in ("", None)) <= {"A", "B", "C", "—", "（表頭）"}
    assert set(x for x in layer if x not in ("", None)) <= {"100%", "IF_Util", "CTL_ProdDerate", "L×m", "—"}
    assert sum(1 for x in conf if x == "—") == 0 and conf.count("B") > conf.count("A") > 0
    for b in IFW_BASES:
        for suf in ("100", "Util", "Prod", "Life"):
            v = eng.get_name(f"IFW_{b}_{suf}")
            assert isinstance(v, list) and len(v) == 15, (b, suf)
        util = eng.get_name(f"IFW_{b}_Util")
        if b.startswith("TokGW"):
            assert all(abs(u - x * eng.get_name("IF_Util")) <= 1e-9 * abs(x) for u, x in zip(util, eng.get_name(f"IF_{b}")))
            assert eng.get_name(f"IFW_{b}_100") == eng.get_name(f"IF_{b}")
        else:
            assert util == eng.get_name(f"IF_{b}")
            if f"IF_{b}_Prod" in eng.names: assert eng.get_name(f"IFW_{b}_Prod") == eng.get_name(f"IF_{b}_Prod")
            # v5.30 X15 (a)：_Life 改為 _Prod × L × m（不再等於 H 節 IF_*_Life）；逐層累乘的斷言見 test_v530_waterfall_running_product
    want = {"L1_FleetBreakeven": 0.150549, "L1_FleetMargin": 3.387612, "L1_HoldEconMW_VR200": 12.225471,      # v5.31 J2（IT 維護等值費率）：0.157156 → 0.150549、3.245188 → 3.387612、12.762016 → 12.225471；v5.30 X15 (b)：HoldEconMW 不除以 1000（0.012762 → 12.762016）
            "L1_TokMW_Gen_ratio_VR200": 1.565285,
            "L1_HarVsGen_Coding": 0.697395, "L1_AstraScale": 14.616242, "L1_ScaleRD": 10.823846, "L1_ScaleServe": 18.067049,      # v5.31：HarVsGen_Coding 0.780699 → 0.697395（GB300 decode 成本下降）、ScaleRD 10.368786 → 10.823846、ScaleServe 16.502022 → 18.067049（持有成本下降）
            "L1_GapPrompt": 2.0, "L1_GapSpendBasis": 2.0, "L1_GapISL": 2.306527, "L1_GapUtil": 1.457143, "L1_GapProduct": 13.443755}   # LibreOffice 重算值（小數第 6 位）
    for n, v in want.items():
        got = eng.get_name(n)
        assert abs(got - v) < 5e-6, (n, got, v)
        lo, hi = eng.get_name(n + "_Lo"), eng.get_name(n + "_Hi")
        assert lo <= got <= hi, (n, lo, got, hi)
    assert abs(eng.get_name("L1_FleetMargin") - eng.get_name("CTL_ProdDerate") * eng.get_name("CTL_PriceLife") * eng.get_name("CTL_Monetize") * eng.get("Theory_Rev", "M73")) < 1e-9
    assert eng.get("Checks", "D121") == 0 and eng.get("Checks", "D91") == 17        # v5.31：I3 15 → 17（L1_GPUhr_GB300_vsBE、L1_GapProduct）；r2：K4＝0；I3 17 → 15（FleetMargin、HoldEconMW_GB300 外部欄改「—」）
    assert eng.get("L1", "P53") == "無外部對照" and eng.get("L1", "P56") == "無外部對照"
    assert abs(eng.get_name("L1_GapProduct") - eng.get_name("L1_GapPrompt") * eng.get_name("L1_GapSpendBasis") * eng.get_name("L1_GapISL") * eng.get_name("L1_GapUtil")) < 1e-9
    assert eng.get_name("LB_LiveCount") == 50 and len(eng.get_name("LB_Rows")) == 50
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CHK_L1Order") == 0
    assert eng.get_name("SRC_DEM_018") == 12.6 and eng.get("SRC_Demand", "O8") == "Active" and eng.get_name("SRC_DEM_004") == 8.4 and eng.get_name("AL_TokPerPrompt") == 4000   # r2 第 1 項：004 與 018 並列 Active
    assert abs(eng.get_name("AL_SpendRatio") - 0.588235) < 5e-6 and abs(eng.get_name("AL_FreeSpendShare") - 0.464286) < 5e-6 and abs(eng.get_name("AL_ServeGWSpend") - 1.219639) < 5e-6   # v5.31：1.113990 → 1.219639（支出 ÷ 持有成本，持有成本下降）；r2：C55／C63 回到 004，C61 用 018
    assert abs(eng.get("L1", "M49") - 0.357307) < 5e-6 and abs(eng.get("L1", "M46") - 1.219639) < 5e-6   # v5.31：1.113990 → 1.219639；r2：Ans5_GM 外部值回到 004 口徑；ExtServeGW 外部值用 018
    assert eng.get("Gov_Map", "AK4") is not None and eng.get("Load_Bearing", "K5") == "—" and eng.get("Load_Bearing", "K54") == "—"   # r2 第 7 項：反轉門檻欄（Gov_Map AK，Excel 擁有）；Load_Bearing K 欄以公式讀取，本版空白


# ── v5.30 X15（工作單 docs/workorders/20261008_v5.30.md r0）：四層瀑布逐層累乘、L1_HoldEconMW 單位更正、IFW_ 上限標記 ──
def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def test_v530_waterfall_running_product(model):
    """v5.30：(a) _Prod＝_Util × CTL_ProdDerate（營收列有 G 節者讀 G 節）、_Life＝_Prod × L × m（營收）／＝_Prod（token）；四層單調遞減；Checks K3＝0；
    VR200 基準欄（索引 10）LibreOffice 重算值；(b) L1_HoldEconMW_*＝L1_HoldEconGW_*（含 _Lo／_Hi）；(c) IFW_ 營收四層與 IFW_TokGW_*_100 的 IFC_Use 含「上限」，K2＝0。"""
    eng = new_engine(model)
    d, lm = eng.get_name("CTL_ProdDerate"), eng.get_name("CTL_PriceLife") * eng.get_name("CTL_Monetize")
    for b in IFW_BASES:
        v100, util, prod, life = (eng.get_name(f"IFW_{b}_{s}") for s in ("100", "Util", "Prod", "Life"))
        if b.startswith("TokGW") or f"IF_{b}_Prod" not in eng.names:
            assert all(abs(p - u * d) <= 1e-9 * abs(u) for u, p in zip(util, prod) if _num(u)), b
        if b.startswith("TokGW"):
            assert prod == life, b
        else:
            assert all(abs(x - p * lm) <= 1e-9 * abs(p) for p, x in zip(prod, life) if _num(p)), b
        for col in zip(v100, util, prod, life):
            nums = [x for x in col if _num(x)]
            assert all(a >= c - 1e-9 * max(1, abs(a)) for a, c in zip(nums, nums[1:])), (b, col)
    want = {"IFW_TokGW_Sol": (237287338734.99, 142372403240.994, 121016542754.845, 121016542754.845),
            "IFW_RevGW_Sol": (381.347118606988, 228.808271164193, 184.79597204631, 184.79597204631)}
    for n, vals in want.items():
        for s, v in zip(("100", "Util", "Prod", "Life"), vals):
            got = eng.get_name(f"{n}_{s}")[10]
            assert abs(got - v) <= 1e-9 * v, (n, s, got, v)
    assert eng.get("Checks", "D119") == 0 and eng.get("Checks", "D120") == 0 and eng.get_name("GOV_Errors") == 0      # K2、K3
    for g in ("Hopper", "GB200", "GB300", "VR200"):
        for suf in ("", "_Lo", "_Hi"):
            assert eng.get_name(f"L1_HoldEconMW_{g}{suf}") == eng.get_name(f"L1_HoldEconGW_{g}{suf}"), (g, suf)
    assert abs(eng.get_name("L1_HoldEconMW_GB300") - 10.886411) < 5e-6      # v5.31 J1＋J2：12.724746 → 10.886411
    labels, use = eng.get_name("IFC_Layer"), eng.get_name("IFC_Use")      # 同長（Interface 第 6 列起）
    import openpyxl
    ws = openpyxl.load_workbook(model, read_only=True)["Interface"]
    a_col = [r[0] for r in ws.iter_rows(min_row=6, max_row=5 + len(use), min_col=1, max_col=1, values_only=True)]
    n_cap = 0
    for lab, u in zip(a_col, use):
        if isinstance(lab, str) and ("[IFW_RevGW" in lab or ("[IFW_TokGW_" in lab and "_100]" in lab)):
            assert isinstance(u, str) and "上限，不得作預測" in u, (lab, u); n_cap += 1
    assert n_cap == 8 * 4 + 3



# ── v5.31 J1–J6（工作單 docs/workorders/20261008_v5.31.md r1）：GB300 機架價格、IT 維護機齡兩段（壽命期等值費率）、IREN 對照 ──
def test_v531_rack_price_and_it_maint(model):
    """v5.31：(J1) Spec_Rack GB300 機架價格 4.0／4.3／5.0；(J2／J3) Inputs 第 30 列＝兩段費率以同欄 WACC、IT 折舊年限年金加權（以 Python 逐年加總驗算），
    IF_MaintITWarr／IF_MaintITPost＝IT 資本 × 兩段費率，IF_WarrantyYrs＝3；IF_MaintIT＝IT 資本 × 等值費率；加總核對列仍為 0；
    (J6) L1_CapexITMW_GB300_vsIREN＝GB300 IF_CapexIT 對 SRC_DC_014；GB300／VR200 基準欄 LibreOffice 重算值。"""
    eng = new_engine(model)
    assert [eng.get("Spec_Rack", c) for c in ("E11", "E12", "E13")] == [4.0, 4.3, 5.0]
    assert eng.get_name("IF_WarrantyYrs") == 3 and eng.get_name("SRC_DC_015") == 3
    capex, maint, warr, post = (eng.get_name(n) for n in ("IF_CapexIT", "IF_MaintIT", "IF_MaintITWarr", "IF_MaintITPost"))
    for j, col in enumerate("DEF"):
        w, n, wy = eng.get("Inputs", f"{col}28"), int(eng.get("Inputs", f"{col}23")), int(eng.get("Inputs", f"{col}36"))
        ri, rp = eng.get("Inputs", f"{col}37"), eng.get("Inputs", f"{col}38")
        num = sum((ri if y <= wy else rp) / (1 + w) ** y for y in range(1, n + 1)); den = sum(1 / (1 + w) ** y for y in range(1, n + 1))
        eq = eng.get("Inputs", f"{col}30")
        assert abs(eq - num / den) < 1e-12, (col, eq, num / den)
        for g in range(5):
            k = 3 * g + j
            assert abs(maint[k] - capex[k] * eq) <= 1e-9 * capex[k], (col, g)
            assert abs(warr[k] - capex[k] * ri) <= 1e-9 * capex[k] and abs(post[k] - capex[k] * rp) <= 1e-9 * capex[k], (col, g)
    assert [round(eng.get("Inputs", f"{c}30"), 6) for c in "DEF"] == [0.010244, 0.015725, 0.018248]
    want = {"IF_CapexIT": (32.237224, 37.586352), "IF_MaintIT": (0.506931, 0.591046), "IF_HoldAcct": (7.989922, 8.992304),
            "IF_HoldEcon": (10.886411, 12.225471), "IF_GPUhrEcon": (2.551788, 4.783652)}      # LibreOffice 重算值（GB300、VR200 基準欄）
    for n, (gb, vr) in want.items():
        v = eng.get_name(n)
        assert abs(v[7] - gb) < 5e-6 and abs(v[10] - vr) < 5e-6, (n, v[7], v[10])
    hold, dep, fac, opex = (eng.get_name(n) for n in ("IF_HoldAcct", "IF_DeprIT", "IF_DeprFac", "IF_OpexGW"))
    assert all(abs(a + b + c - h) < 1e-9 for a, b, c, h in zip(dep, fac, opex, hold))
    assert abs(eng.get_name("L1_CapexITMW_GB300_vsIREN") - capex[7]) < 1e-12 and eng.get_name("SRC_DC_014") == 29.0
    r = eng.get_name("L1_CapexITMW_GB300_vsIREN") / 29.0
    assert 0.8 <= r <= 1.2
    assert eng.get("SRC_HW", "O11") == "Alt" and eng.get_name("GOV_Errors") == 0

"""數值檢查（CLAUDE.md 第 3 節；修訂八-B）：所有檢查讀 LibreOffice 重算後的值，不再使用公式引擎。

範圍：全部情境（scenarios.yaml）的錯誤值與防空轉；具名範圍與形狀；各版本的期望值測試。
`lo.view(inputs)` 回傳該組輸入重算後的唯讀檢視（介面同舊 Engine 的唯讀部分）；inputs={} 為基準。
"""
from pathlib import Path

import pytest
import yaml

from conftest import model_path
from parity_lib import lo_recalc, read_defined_names_xml, set_inputs

HERE = Path(__file__).parent
V152_CHANGED = set(__import__("json").load(open(HERE / "fixtures" / "v152_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(HERE / "fixtures" / "v153_changed_names.json", encoding="utf-8"))["names"])      # v15.3：另併入 v15.2→v15.3 的預期變動名單（E1／E2／C2／D1；test_v1530 逐名稱釘住）
CFG = yaml.safe_load((HERE / "scenarios.yaml").read_text(encoding="utf-8"))
SCENARIOS = CFG["scenarios"]
EXPECT = CFG["workbook_expectations"]
TIERS = ("Luna", "Sol", "Astra")
BLOCK3_PREFIX = ("TrainGPUh", "TrainCost", "PostShareFLOP", "PostShareGPUh", "RLMFU", "ProgGPUh", "ProgCost", "ProgGWyr")
BLOCK2_PREFIX = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")


PROD_IF = tuple(f"{b}_Prod" for b in ("IF_FullCost_Luna", "IF_FullCost_Sol", "IF_FullCost_Astra", "IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet"))   # v5.19 X1
# v5.23 X10：VR200 欄（第 4 個）因 Perf_Batch 側 η_d 倍數 0.75 而改變（0.85：sol 0.2551→0.2567、astra 0.3313→0.340920；0.7：sol 0.6901→0.6955、astra 0.9923→1.028611），其餘欄不變
# 相對基準列的變動（LibreOffice 重算值；欄序 Hopper、GB200、GB300、VR200、Rubin Ultra 的基準成本欄；0.85 預設、0.7 區間下限）
EXPECT_PROD_085 = {"sol": (0.631435, 0.276637, 0.293431, 0.2614, 0.2521), "astra": (1.159402, 0.379181, 0.453288, 0.340920, 0.314495), "fleet": (-0.479886, -0.251273, -0.278943, -0.227239, -0.219663)}      # v6.2：Hopper Astra TTFT 不可達（文字，None）並自機隊排除，Hopper 欄 Sol 0.6183 → 0.631435、機隊營收 −0.4513 → −0.2882（Astra 不再在 Hopper 機隊內）；v6.1：Hopper 欄（Calib C67 1.5 → 1.2 等）改變，其餘世代不變      # v12.0 H2：GB200 欄 sol 0.2769 → 0.279218、astra 0.377266 → 0.383408（GB200 CAL_BatchEtaD 3.04 → 2.36）； v11.0 G2：GB200 欄 sol 0.2883 → 0.2769、astra 0.401172 → 0.377266（CAL_BatchEtaD[2] 1 → 3.04；其餘欄不變）
# v6.0 D7／D11：Sol 欄（回本溢價分母改付費 token）上升，Astra、機隊營收不變（_Prod 重解 SLO 的營收端 v5.30 起已是重解值）
EXPECT_PROD_070 = {"sol": (0.778579, 0.863341, 0.7133, 0.6790), "astra": (1.242084, 1.676766, 1.028611, 0.920298)}      # 欄序 GB200、GB300、VR200、Rubin Ultra（Hopper 為文字）      # v12.0 H2：GB200 sol 0.779806 → 0.787490、astra 1.239213 → 1.257279（CAL_BatchEtaD[2] 3.04 → 2.36）； v11.0 G2：GB200 sol 0.825496 → 0.779806、astra 1.325222 → 1.239213
V526_IF = ("IF_DeprLifeIT", "IF_DeprIT", "IF_DeprFac", "IF_AvgDraw", "IF_PowerPrice", "IF_MaintIT", "IF_MaintFac", "IF_StaffSW", "IF_TaxIns", "IF_OpexGW")   # v5.26 Interface I 節
ALLOC_IF = ("IF_AllocQ1", "IF_AllocQ1_R2", "IF_AllocQ2", "IF_AllocServeGW", "IF_AllocRDGW", "IF_AllocDemand", "IF_AllocImpliedNk")


# 額外的輸入組合（測試名稱 → 輸入列表）：conftest 的 lo fixture 會在 session 開始時與情境一起並行預先重算。
PREWARM = {
    "test_floor_scenarios_expected_values": [{"B5_PFloor": 0}, {"B5_PFloor": 0.8}],
    "test_alloc_expected_values_and_slo_text": [{"Tech_Registry!O11": 1, "Tech_Registry!O12": 1, "Tech_Registry!O13": 1}, {"Serving!C18": 0.7}],
    "test_alloc_mix_2025_expected_values": [{"AL_MixHopper": 0.6, "AL_MixGB200": 0.4, "AL_MixGB300": 0, "AL_MixVR200": 0}],
    "test_prod_derate_expected_values": [{"CTL_ProdDerate": 0.7}],
    "test_price_life_expected_values": [{"CTL_PriceLife": 0.5, "CTL_Monetize": 0.8}],
    "test_batch_etad_expected_values": [{"CAL_BatchEtaD[2]": 1.0}, {"CAL_BatchEtaD[2]": 1.0, "CAL_BatchEtaD[4]": 1.0}],
    "test_v603_fleet_price_k2_k3": [{"B4_CacheHit": 0}],
    "test_v602_model_scale_ttft_alloc": [{"B4_CacheHit": 0}, {"ARCH_ScaleGen[1]": 0.8, "ARCH_ScaleGen[2]": 0.55, "ARCH_ScaleGen[3]": 1.0, "ARCH_ScaleGen[4]": 1.4, "B4_CacheHit": 0}],
    "test_v600_audit_fix1_slo_text": [{"Serving!C18": 0.7}, {"Train_In!E31": 20}, {"Train_In!E31": 80}, {"Train_In!E31": 100}, {"Train_In!E31": 150}],
}


@pytest.fixture(scope="module")
def model():
    return model_path()


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


def test_workbook_expectations(model, lo):
    eng = lo.view({})
    assert len(eng.formula_cells) == EXPECT["formula_cells"]
    assert len(eng.names) == EXPECT["defined_names"]
    assert eng.sheetnames == EXPECT["sheets"]                              # v5.7 起含 DB_Evidence（最後一頁）；v5.8 起含 8 個 Block 4 頁
    assert not any(s == "DB_Evidence" for s, _ in eng.formula_cells)       # DB_Evidence 純輸入、無公式


def test_named_ranges(model, lo):
    """144 個具名範圍：名稱存在、attr_text 與 workbook.xml 及 LibreOffice 重算版一致，且可取值。"""
    eng = lo.view({})
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
    assert sum(n.startswith("RNG_") for n in eng.names) == EXPECT["rng_names"]            # v13.0 K1／K2：RNG_*（批次口徑區間端點與時效旗標）
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


def test_display_names_alignment(model, lo):
    """表頭與推導鏈名稱的形狀：DRV_ 皆 15 欄且與 DRV_Gen／DRV_Tier 對齊；IF_Hdr 與 IF_ 輸出欄數一致。"""
    eng = lo.view({})
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


def test_interface_d_e_shapes(model, lo):
    """Interface D 節（v5.8）與 E 節（v5.9）的形狀，分開檢查：單格（數值或文字）、15 欄（5 世代 × 3 成本情境）、5 欄（任務）。"""
    eng = lo.view({})
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
            # v6.2 2-1-b：Hopper（前 3 欄）× Astra 的 TTFT 不達標，該層級的名稱輸出文字旗標（D8：文字＝不可用，不是 0）；其餘格必須是數值
            ok_txt = n.endswith("_Astra") and width == 15
            assert all((isinstance(x, (int, float)) and not isinstance(x, bool)) or (ok_txt and i < 3 and x in ("SLO 不可達", "TTFT 不可達")) for i, x in enumerate(v)), f"{n} 含非數值"
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
        assert isinstance(v, list) and len(v) == 15 and all((isinstance(x, (int, float)) and not isinstance(x, bool)) or x in ("SLO 不可達", "TTFT 不可達") for x in v), f"{n}: {v!r}"
    v522_new = {f"{n}_Life" for n in ("IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGW_Astra", "IF_RevGWFleet")}   # v5.22 X7：Interface H 節 4 個 _Life 名稱（15 欄；數值或「SLO 不可達」）
    assert len(v522_new) == 4 and v522_new <= set(eng.names)
    for n in v522_new:
        v = eng.get_name(n)
        assert isinstance(v, list) and len(v) == 15 and all((isinstance(x, (int, float)) and not isinstance(x, bool)) or x in ("SLO 不可達", "TTFT 不可達") for x in v), f"{n}: {v!r}"
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
    assert len(v510_new) == 10 and EXPECT["downstream_names"] - len(v59_new) - len(v510_new) - len(v519_new) - len(v522_new) - len(v526_new) - len(v531_new) == 133  # v15.0：132 → 133（downstream_names 207 → 208，新增 IF_FrontSuccVRQual）； v5.31 新增 3 個； v5.8 的下游名稱數 113＋v5.15 的 IF_Alloc* 7 個；v5.10 新增 10 個；v5.19 新增 7 個；v5.22 新增 4 個；v5.26 新增 10 個
    for n in (n for n in eng.names if n.startswith(("B4_", "B5_"))):                       # B4_／B5_：每個名稱都能取值（形狀不另規定）
        eng.get_name(n)
    mkt = eng.get_name("B4_MktChina")                                                       # v5.9：中國廠商旗標（1＝中國廠商），與國別欄同長
    assert len(mkt) == len(eng.get_name("B4_MktCountry")) and set(mkt) <= {0, 1} and 0 < sum(mkt) < len(mkt)

# v10.2 E2：Serving 第 21 列 SLO 改為兩家量測商的幾何平均（84.3／43.3／40.8）。下列機制測試（不可達路徑、文字旗標、文字傳遞、各期望值）
# 以 v10.1 以前的 SLO 120／65／55 為條件（＝情境 slo_v10 的輸入：SRC_PERF_066–071 兩家皆設舊值），期望值與 v10.1 相同；
# 新基準的期望值由 test_v1020_eta_calibration 另行斷言。
OLD_SLO = {"SRC_PERF_066": 120, "SRC_PERF_067": 120, "SRC_PERF_068": 65, "SRC_PERF_069": 65, "SRC_PERF_070": 55, "SRC_PERF_071": 55,
           "Gov_Map!K243": 0, "Gov_Map!L243": 200, "Gov_Map!K244": 0, "Gov_Map!L244": 200, "Gov_Map!K245": 0, "Gov_Map!L245": 200}   # 舊 SLO 超出新區間（Gov_Map GM239–GM241 的低／高）會觸發 Checks E10；機制測試放寬該區間（列號為 v10.2）


def _vo(lo, inputs=None):
    return lo.view({**OLD_SLO, **(inputs or {})})


def _floor_engine(lo, floor):
    return _vo(lo, {"B5_PFloor": floor})


def test_floor_scenarios_expected_values(model, lo):
    """v5.10 M1：floor_0 與 floor_80 的期望值（與 parity 情境互補；parity 保證兩邊一致，這裡保證結果合理）。"""
    base = _vo(lo, {})
    names = base.get_name("IF_HdrTask")
    assert base.get_name("IF_PFloor") == 0.5                                              # 基準 p_min＝50%
    assert base.get_name("IF_FrontSuccVRName") == ["Luna｜標準", "Luna｜標準", "Luna｜選定", "Luna｜選定", "Sol｜選定"]
    # v5.31 J2：VR200 每成功任務成本隨 IT 維護下降（Coding agent 前緣 0.0222 → 0.0213；不設下限 0.0135 → 0.0129）
    assert abs(base.get_name("IF_FrontSuccVR")[4] - 0.0213) < 5e-5 and abs(base.get_name("IF_FrontSuccVRP")[4] - 0.627) < 5e-4
    f0 = _floor_engine(lo, 0)                                                          # 不設下限：前緣＝「對照（不設下限）」列
    cols = "CDEFG"
    assert [f0.get("Harness", f"{c}151") for c in cols] == [f0.get("Harness", f"{c}147") for c in cols]
    assert [f0.get("Harness", f"{c}152") for c in cols] == [f0.get("Harness", f"{c}148") for c in cols]
    assert f0.get_name("IF_FrontSuccVRName")[4] == "Luna｜選定" and abs(f0.get_name("IF_FrontSuccVR")[4] - 0.0129) < 5e-4
    f8 = _floor_engine(lo, 0.8)                                                        # 下限 80%：Coding agent 無合格
    assert f8.get_name("IF_FrontSuccVR")[4] == f8.get_name("IF_FrontSuccVRName")[4] == f8.get_name("IF_FrontSuccVRP")[4] == "無合格"
    assert f8.get_name("IF_FrontSuccVRName")[2:4] == ["Sol｜選定", "Sol｜選定"]            # 單代理、多代理研究
    assert f8.get("Checks", "B70") == 1, names                                            # 無合格任務數


def test_named_ranges_vs_libreoffice(model, lo, tmp_path):
    """LibreOffice 存檔後的名稱範圍（正規化後）與原檔一致。"""
    src = tmp_path / model.name
    set_inputs(model, src, {})
    out = lo_recalc(src, tmp_path / "lo")
    import openpyxl
    lo_names = {k: v.attr_text.replace("$", "") for k, v in openpyxl.load_workbook(out).defined_names.items()}
    ours = {k: v.replace("$", "") for k, v in lo.meta.names.items()}
    assert lo_names == ours


@pytest.mark.parametrize("sc", SCENARIOS, ids=[s["id"] for s in SCENARIOS])
def test_scenario_checks(sc, lo, results_store):
    """情境：改寫輸入 → LibreOffice 重算 → 全部公式格錯誤值 0；非基準情境相對基準至少改變一個公式格（防空轉）。"""
    view, base_view = lo.view(sc["inputs"]), lo.view({})
    got, base = view.evaluate_all(), base_view.evaluate_all()
    errors = [k for k, v in got.items() if isinstance(v, str) and v.startswith("#")]
    changed = [k for k in base if base[k] != got[k]]   # 防空轉：統計相對基準改變的格數（其中屬 Interface 者）
    results_store[sc["id"]] = {"cells": len(got), "error_value_cells": len(errors), "changed_cells": len(changed),
                               "changed_interface_cells": sum(1 for s_, _ in changed if s_ == "Interface")}
    if sc["id"].startswith("h_alloc_"):          # v5.15 防空轉：Interface F 節（IF_Alloc*）至少一格改變；成長情境只改 Alloc 頁（見報告）
        sheet_ref = [base_view.name_ref(n) for n in ALLOC_IF] if sc["id"] != "h_alloc_growth" else [("Alloc", None)]
        if sc["id"] != "h_alloc_growth":
            assert any(base[(s_, r_)] != got[(s_, r_)] for s_, r_ in sheet_ref if (s_, r_) in base), f"[{sc['id']}] Interface F 節未改變"
        else:
            assert any(s_ == "Alloc" for s_, _ in changed), f"[{sc['id']}] Alloc 頁未改變"
    if sc["id"] == "h_prod_derate_070":          # v5.19 X1 防空轉：至少一個 _Prod 列改變；基準列（IF_FullCost_*、IF_RevGW_*）一格都不變
        assert any(base_view.get_name(n) != view.get_name(n) for n in PROD_IF), f"[{sc['id']}] _Prod 列未改變"
        assert all(base_view.get_name(n[:-5]) == view.get_name(n[:-5]) for n in PROD_IF), f"[{sc['id']}] 基準列被改動（Serving!C18 未動，基準列不得變）"
    assert not errors, f"[{sc['id']}] 錯誤值 {len(errors)} 格（v5.9 起任何情境皆不得出現錯誤值）；前 10 格 {[(k, got[k]) for k in errors[:10]]}"
    if sc["id"] != "base":
        assert changed, f"[{sc['id']}] 未改變任何公式格（測試空轉）"


def test_alloc_expected_values_and_slo_text(model, lo):
    """v5.15 Block 6：基準值（工作單預期）與 SLO 不可達時回傳文字、無錯誤值（b_prod_derate、f_registry_t07_t09_on）。"""
    base = _vo(lo, {})
    assert abs(base.get_name("AL_DDaily") - 16.48) < 0.01                                 # v5.29 X14 (l)：每則提示 token 數 2,000 → 4,000，每日 token 11.48 → 16.48T
    assert abs(base.get_name("AL_ServeGWSpend") - 0.898096) < 5e-5                        # v5.33 J8：組合持有成本 10.33 → 9.353，1.21964 → 1.34714（工作單 B2 驗收錨點 1.35）；v5.31 J1／J2：1.11399 → 1.21964（支出 ÷ 持有成本，持有成本下降）；v5.29 X14 (k)：支出路線服務 GW 改連 SRC_DEM_018 12.6（r2：只有這條路線用 018；004 維持 Active），0.74266 → 1.11399（LibreOffice 重算值）
    assert abs(base.get_name("AL_RefGWyr") - 0.044455) < 5e-6   # v12.0 H2：0.0432504 → 0.0450046（GB200 CAL_BatchEtaD 3.04 → 2.36）； v11.0 G2：0.0562533 → 0.0432504（GB200 CAL_BatchEtaD 1 → 3.04，研發 GB200 每 GW token 增加）；                          # v5.18：0.01808→0.018153；v5.23 X10：→0.0210207（＝v5.22 暫存複本 L、M、N 欄第 53 列 ×0.75 的 LibreOffice 重算值）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    assert abs(base.get_name("AL_FamGWyr") - 0.112250) < 5e-6        # v12.0 H2：0.110757 → 0.112938（同上）； v11.0 G2：0.127692 → 0.110757（GB200 CAL_BatchEtaD 3.04）； v8.0 L3：研發世代組合加權（Alloc J 節）；v7.0 以前＝Fleet_1GW 第 33 列（VR200 欄）0.04864  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    assert base.get_name("AL_RDShareExcl") == 0 and base.get_name("CHK_RDMixSum") == 0
    assert base.get_name("GOV_Errors") == 0 and sum(base.get_name("AL_SensCheck")) == 0
    for sid, inputs, text in (("f_registry_t07_t09_on", {"Tech_Registry!O11": 1, "Tech_Registry!O12": 1, "Tech_Registry!O13": 1}, True),
                              ("b_prod_derate", {"Serving!C18": 0.7}, True)):      # v5.33 J8：2025 組合含 Hopper 60%，C18＝0.7 時 Hopper SLO 不可達 → Alloc 回傳文字（v5.32 前組合無 Hopper，為數值 0.4570）
        eng = _vo(lo, inputs)
        for n in ALLOC_IF:                                                                  # 每個 IF_Alloc*：數值或文字「SLO 不可達」，不得為錯誤值
            v = eng.get_name(n)
            assert (isinstance(v, (int, float)) and not isinstance(v, bool)) or v in ("SLO 不可達", "整代不可達"), (sid, n, v)      # v6.3 K2：整代不可達
        if sid == "b_prod_derate":                                                          # v5.30 X15 (a)：C18＝0.7 而 CTL_ProdDerate＝0.85 時，G 節（以 0.85 取代 C18 重解）> D 節（0.7），
            assert eng.get("Checks", "D120") == 156 and eng.get_name("GOV_Errors") == 156, sid   # v6.0 D8-2：不可達層級排除後重新正規化，K3 單調檢查 57 → 156（見 v6.0 報告「待 Project 判斷」）  # 營收列 _Prod > _Util，K3 單調檢查依工作單計 ERROR（57 格；其餘 ERROR 0）；見 v5.30 報告「待 Project 判斷」第 1 項
        else:
            assert eng.get_name("GOV_Errors") == 6, sid          # v6.0 D8-2：f_registry 的 Hopper 層級排除後重新正規化，Checks K3 計 6 格（v5.36 為 0；見 v6.0 報告「待 Project 判斷」）
        # v6.2 2-1-c：Alloc 排除不可達層級後重新正規化，全不可達的世代排除、世代組合重新正規化——這兩個情境的 Q1、Q2、服務 GW 不再是文字，而是數值（v6.0／v6.1 為文字「SLO 不可達」）
        want = {"f_registry_t07_t09_on": (0.118321, 0.156718, 1.083674), "b_prod_derate": (0.209247, 0.209974, 0.898096)}[sid]      # v12.0 H2：b_prod_derate 的 Q1 0.203282 → 0.211684、Q2 0.203994 → 0.212418（GB200 CAL_BatchEtaD 3.04 → 2.36，研發 GW 隨之增加；服務 GW 0.898096 不變）； v8.0 L3／L5：研發世代組合加權、服務 GW 改支出路線（v7.0：0.248537／0.301826／0.338418）
        for n, w in zip(("IF_AllocQ1", "IF_AllocQ2", "IF_AllocServeGW"), want):
            if sid == "f_registry_t07_t09_on":          # v6.3 K2：2025 組合中占比 > 0 的世代（Hopper 0.6）整代不可達 → 文字「整代不可達」，不再把該世代權重併入其餘世代
                assert eng.get_name(n) == "整代不可達", (sid, n, eng.get_name(n))
            else:
                assert abs(eng.get_name(n) - w) < 5e-6, (sid, n, eng.get_name(n), w)
        if sid == "f_registry_t07_t09_on":                                                  # Hopper 三個層級全不可達：該世代排除（AL_GenOK＝0），其權重併入其餘世代；GB300 Astra 不可達（占付費組合 0.15）
            assert eng.get_name("AL_GenOK") == [0, 1, 1, 1] and [round(x, 9) for x in eng.get_name("AL_UnservedPaid")] == [1, 0, 0.15, 0], (eng.get_name("AL_GenOK"), eng.get_name("AL_UnservedPaid"))
            # v6.3 K2：整代不可達文字須一路傳到機隊 m、價格與 Cap_In H7 所需 token，不得出現數值、負值或 #VALUE!（K1 的 AL_PriceFleet 同為文字）
            assert eng.get_name("AL_PriceFleet") == "整代不可達" and eng.get_name("AL_GenShareOK") == 0.4 and eng.get_name("B4_PriceFleet") == ["整代不可達"] * 4
            for n in ("L1_MFleet", "L1_TokCeiling", "L1_ScaleServe", "L1_TokPerPromptClose", "L1_GapPrompt"):
                assert eng.get_name(n) == "整代不可達", (sid, n, eng.get_name(n))      # 機隊閉合名稱：文字旗標一路傳到（AL_UnavailTxt），不得為數值或負值
            for r_ in (123, 124, 125):
                assert all(isinstance(eng.get("Cap_In", f"{c_}{r_}"), str) and not eng.get("Cap_In", f"{c_}{r_}").startswith("#") for c_ in "CD"), (sid, r_)
        if sid == "b_prod_derate":                                                          # v5.33 B3 → v6.2：Cap_In H7 與 L1_MFleet 在 C18＝0.7 時改為數值（Hopper 排除 Astra 後重新正規化）
            assert abs(eng.get_name("L1_MFleet") - 1.244991) < 5e-6      # v8.0 L1：1.142711 → 1.167740（2025 年度單價）； and abs(eng.get_name("L1_TokCeiling") / 19243646212.1402 - 1) < 1e-6
            assert eng.get("Checks", "D129") == 0 and eng.get("Checks", "D130") == 1 and eng.get("Checks", "D131") == 1      # v15.2：C18＝0.7 情境下 M4（WARN）由 0 變 1（機隊 m 1.2450 使需求 ÷ 機隊付費 token 低於 0.5；基準視圖不觸發），屬 B2／B3 預期連動； v6.3 K1：m_fleet 0.960979 → 1.142711 > 1，M3（WARN）觸發，屬預期
            assert abs(eng.get_name("L1_TokPerPromptClose") / 14204.833202 - 1) < 1e-6 and abs(eng.get_name("L1_LReqFleet") - 2.013681) < 5e-6      # v8.0 L4：0.463241 → 2.009119；   # v5.34 B3／v5.35 B2：為數值
            assert abs(eng.get_name("L1_LTotal") - 0.659506) < 5e-6                      # L_total 不依賴 m
            assert abs(eng.get_name("AL_UnservedPaid")[0] - 0.15) < 1e-12 and eng.get_name("AL_GenOK") == [1, 1, 1, 1]


def test_alloc_mix_2025_expected_values(model, lo):
    """補充 2：2025 機隊 Hopper 60%／GB200 40% 的期望值（chat 端獨立重算）。v5.33 J8 起此組合即為基準（Alloc_In C9–C12），本測試改為直接設定同一組合，期望值不變；情境檔 h_alloc_mix_2025 改設 0／40／40／20。"""
    eng = _vo(lo, {"AL_MixHopper": 0.6, "AL_MixGB200": 0.4, "AL_MixGB300": 0, "AL_MixVR200": 0})
    for n, want in (("IF_AllocServeGW", 0.898096), ("AL_ServeGW", 0.150423), ("AL_ServeGWSpend", 0.898096), ("IF_AllocQ1", 0.182997), ("IF_AllocQ2", 0.183654)):   # v15.3 C2：GB200 批次倍數 2.36 → 2.198，Q1／Q2 0.181823／0.182477 → 0.182997／0.183654；   # v15.2 B3：Q1／Q2 0.184322／0.184983 →   # v12.0 H2：Q1 0.180086 → 0.184322、Q2 0.180735 → 0.184983（GB200 CAL_BatchEtaD 3.04 → 2.36）； v11.0 G2：Q1 0.211016 → 0.180086、Q2 0.211748 → 0.180735（GB200 CAL_BatchEtaD 3.04）； v6.2（2-1-b／c）：Hopper Astra TTFT 不可達並排除、Alloc 層級權重重新正規化：IF_AllocServeGW 0.189082 → 0.166128、IF_AllocQ1 0.324144 → 0.364100、IF_AllocQ2 0.385331 → 0.428053；v6.1（稽核修正 3B）：IF_AllocServeGW 0.182593 → 0.189082、IF_AllocQ1 0.331841 → 0.324144、IF_AllocQ2 0.393635 → 0.385331（D6 Hopper η_d 1.5 → 1.2、D10 計價倍數 0.85、D13 純利用率 0.41 × 生產折減）；AL_ServeGWSpend 不變（支出 ÷ 持有成本，不含計價倍數） ｜v5.31：AL_ServeGWSpend 1.295514 → 1.347144、IF_AllocQ2 0.394559 → 0.393635（持有成本下降；LibreOffice 重算值）； v5.29 X14 (k)(l)：0.140315／0.863676／0.392575／0.458889 → 本列（引擎重算值，與 LibreOffice 一致）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - want) < 5e-6, (n, eng.get_name(n))
    assert eng.get_name("GOV_Errors") == 0


def test_l1_v516_expected_values_and_h3(model, lo):
    """v5.16：L1 毛利率兩列、GPU 小時口徑、第 7、8 題的基準期望值（工作單第 1 節；chat 端計算，精度到小數第 5 位故容差 5e-6），H3＝0。"""
    eng = _vo(lo, {})
    want = {"L1_Ans5_GM": (0.955053, 0.927392, 0.965027), "L1_Ans5_FullMargin": (0.918969, 0.869108, 0.936948),     # v5.31 J1／J2：持有成本下降，毛利率上升（LibreOffice 重算值）； v5.18：LibreOffice 重算值（v5.16 為 chat 端計算）；v5.23 X10：FullMargin 與 GPUh 改為 k＝0.75 暫存複本的 LibreOffice 重算值  # v15.2 B2／B3 預期變動：期望值依重算結果更新
            "L1_Ans6_GPUh": (0.28231, 0.28231, 0.28231), "L1_Ans7": (1.0, 1.0, 1.0), "L1_Ans8": (0.479396, 0.479396, 0.479396)}      # v5.31：Ans8 0.47928 → 0.47940  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    for n, (d, lo, hi) in want.items():
        for suffix, v in (("", d), ("_Lo", lo), ("_Hi", hi)):
            got = eng.get_name(n + suffix)
            assert abs(got - v) < 5e-6, (n + suffix, got, v)
        assert lo <= d <= hi
    assert eng.get_name("CHK_L1Order") == 0                                              # H3（WARN）：基準 0；以具名範圍讀，不查標籤（快取不含常數標籤格）
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("GOV_Warnings") == 281 and eng.get_name("GOV_Info") == 182      # v15.2：舊 SLO 視圖 Info 181 → 182（I3 +1、I1 +1、K5 −1：B2／B3 使 L1 外部對照差距旗標列數與 Gov_Map 區間內外狀態改變）；  # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：舊 SLO 視圖 Info 184 → 181（L1 外部對照換算後 P 欄「差距 >20%」旗標減少）      # v13.0 K2：舊 SLO 視圖改動上游輸入，基準落在 RNG_* 區間外，Checks RG2 觸發（上限算 1）：Warnings 282 → 283； v13.0 K3：Info 181 → 182（Calib C68 類別『倒推』更正為 Assumed，列入 Load_Bearing，K5 計數 +1）； v12.0：Info 179 → 181（Gov_Map 新增 CHK_SoftCapFail、Calib C156 Hopper 兩列，皆為 Assumed 帶區間的資訊列）； v10.0：Warnings 271 → 276（W1 +5：SRC_PERF_060–064 為利害關係方 Active、無第二來源；SRC_HAR_016 為 Alt 不計）；v8.0：Warnings 271 不變、Info 174 → 177（I3 L1 區間外或差距 >20% 的列 18 → 21）；v7.0：Info 175 → 174（Calib C68 類別 Assumed → 倒推，Load_Bearing 56 → 55）；v6.1：Info 169 → 172（Load_Bearing 列數 50 → 53，K5 計入新增的 3 列高段 Assumed Gov_Map 登錄；Q3 RL 區間）；v5.35：Warnings 270 → 271（W1 +1：SRC_DEM_072 利害關係方 Active、無第二來源）；Info 不變（L1_LTotal 判讀「區間內」、L1_LReqFleet 判讀「回本」、L1_LPrice／LDemote「無外部對照」皆不計入 I3）；v5.34：Warnings 267 → 270（M4 +1：需求 ÷ 機隊 0.465 < 0.5，預期；W1 +2：SRC_DEM_069、071 為利害關係方 Active、無第二來源；070 為 Alt 不計）；Info 168 → 169（I3 +1：L1_TokPerPromptClose 判讀「高於外部區間」）；v5.33：Warnings 250 → 267（W1 +17：SRC_DEM_049–051、054–058、060–068 為利害關係方 Active、無第二來源；M2、M3 依現值 0）；v5.32：Warnings 221 → 250（M1 +1：L1_MImplied 1.74 在 0.3–1.0 外，J4 (a) 預期；W1 +28：SRC_DEM_019–045、048 為利害關係方 Active、無第二來源）；Info 不變（L1_MImplied／_Ext 判讀為「區間內／外」，不計入 I3）；v5.31：Warnings 220 → 221（W1：SRC_DC_014 IREN、SRC_DC_017 DGX 利害關係方無第二來源 +2，SRC_HW_007 改 Alt −1）；Info 165 → 168（I3 15 → 17：L1_GPUhr_GB300_vsBE、L1_GapProduct 判讀改「差距 >20%」；I8 53 → 54：Spec_Rack E12 標記變更）；v5.29 r2：Info 108 → 165（I3 8 → 15：新增 L1 列判讀「差距 >20%」7 列——FleetMargin 與 HoldEconMW_GB300 外部欄依 r2 第 11 項改「—」；K4 0（r2 第 2 項：比對含 CTL_ProdDerate × L × m）；K5 50；K6 0；K7 0）；Warnings 219 → 220（W1：SRC_DEM_018 利害關係方無第二來源 +1；SRC_DEM_004 依 r2 維持 Active；K1 0）；v5.27：W1 213 → 219（SRC_MOD_057–062 Kimi K3 為利害關係方、無第二來源）；I3 7 → 8（L1 第 39 列新增外部對照，判讀「差距 >20%」）；v5.25：W1 209 → 213      # v6.2：Info 172 → 175（Gov_Map 新增 3 列 Assumed 模型規模倍數，K5 Load_Bearing 53 → 56）      # v13.1 D15 B 段：Warnings 減 2（SRC_HW_067／068 有了第二來源，W1 −2）、Info 加 2（DB_Evidence 新增 2 筆『待判定』）；預期變動，非放寬


def _pct(eng, n, k):
    """_Prod 相對基準列的變動（第 k 欄，0 起算）；任一邊為文字時回傳 None"""
    p, b = eng.get_name(n)[k], eng.get_name(n[:-5])[k]
    return p / b - 1 if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (p, b)) else None


def test_prod_derate_expected_values(model, lo):
    """v5.19 X1（工作單 1.5 節；LibreOffice 重算值）：CTL_ProdDerate 預設 0.85 與 0.7 下，_Prod 列相對基準列的變動；自我檢查 X1＝0。
    欄序：5 世代 × 3 成本情境（低／基準／高），基準欄索引 1、4、7、10、13＝Hopper、GB200、GB300、VR200、Rubin Ultra。"""
    base = _vo(lo, {})
    assert base.get_name("CTL_ProdDerate") == 0.85 and base.get("Serving", "C18") == 1.0   # C18 維持 1.0（G0-11）
    assert base.get_name("GOV_Errors") == 0                                               # 含 Checks X1（替代值改回 C18 時七列等於基準列）
    want = {"IF_FullCost_Sol_Prod": EXPECT_PROD_085["sol"], "IF_FullCost_Astra_Prod": EXPECT_PROD_085["astra"], "IF_RevGWFleet_Prod": EXPECT_PROD_085["fleet"]}
    for n, vals in want.items():
        for k, v in zip((1, 4, 7, 10, 13), vals):
            if v is None:                                                                 # v6.2：Hopper × Astra 為文字旗標（TTFT 不可達），無百分比
                assert _pct(base, n, k) is None, (n, k, _pct(base, n, k)); continue
            assert abs(_pct(base, n, k) - v) < 5e-4, (n, k, _pct(base, n, k), v)
    eng = _vo(lo, {"CTL_ProdDerate": 0.7})
    assert eng.get_name("GOV_Errors") == 0
    assert eng.get_name("IF_FullCost_Astra_Prod")[1] == "SLO 不可達"                       # Hopper：Astra 層 SLO 不可達 → 該層全成本為文字
    for n in ("IF_FullCost_Luna_Prod", "IF_FullCost_Sol_Prod"):                          # v6.0 D8-2：只排除不可達層級，其餘層級照算（v5.36 整欄為文字）
        assert _num(eng.get_name(n)[1]), n
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


def test_price_life_expected_values(model, lo):
    """v5.22 X7（工作單 1.3、1.4 節）：基準 L＝m＝1 時四個 _Life 列＝基準列；h_price_life_050（L＝0.5、m＝0.8）時 60 格 _Life＝基準 × 0.4，
    基準列、L1、Interface 第 1–210 列不變；錯誤值 0；Checks X7（GOV_Errors）＝0。基準列為文字時 _Life 為相同文字。"""
    import re
    base = lo.view({})
    assert base.get_name("CTL_PriceLife") == 1 and base.get_name("CTL_Monetize") == 1
    for n in LIFE_IF:                    # v6.0 D7-3：IF_*_Life 為 IFW_*_Life 的過渡別名；L＝m＝1 時等於 _Prod 列（不再等於 Util 層基準列）
        assert base.get_name(n + "_Life") == base.get_name("IFW_" + n[3:] + "_Life") == base.get_name(n + "_Prod"), n
    assert base.get_name("GOV_Errors") == 0
    base_vals = base.evaluate_all()
    eng = lo.view({"CTL_PriceLife": 0.5, "CTL_Monetize": 0.8})
    cur = eng.evaluate_all()
    assert eng.get_name("GOV_Errors") == 0
    changed = 0
    for n in LIFE_IF:
        b, life = eng.get_name(n + "_Prod"), eng.get_name(n + "_Life")
        assert len(b) == len(life) == 15, n
        for k, (x, y) in enumerate(zip(b, life)):
            if isinstance(x, (int, float)) and not isinstance(x, bool):
                assert abs(y - x * 0.4) <= 1e-9 * max(1.0, abs(x)), (n, k, x, y)
                changed += y != x
            else:
                assert y == x, (n, k, x, y)          # 基準列為文字（SLO 不可達）→ 相同文字
    assert changed > 0                               # 防空轉：至少一格 _Life 改變
    fm_row = int(re.sub(r"[A-Z]+", "", base.names["L1_FleetMargin"].rsplit("!", 1)[1].replace("$", "")))   # v5.29 X14 (c)：L1_FleetMargin 含 CTL_PriceLife × CTL_Monetize，該列隨情境改變
    _row = lambda n: int(re.sub(r"[A-Z]+", "", base.names[n].rsplit("!", 1)[1].replace("$", "")))
    m_rows = {_row("L1_MImplied"), _row("L1_MImplied_Ext"), _row("L1_MFleet"), _row("L1_MAPI"), _row("L1_MSub"), _row("L1_MSeat"), _row("L1_LTotal")}   # v5.35 B4：L1_LTotal 外部欄＝CTL_PriceLife（L＝0.5 時 M／N／O／P 隨情境改變；D:F 不變）；v5.34 B4：L1_MAPI／MSub／MSeat 外部欄同為 CTL_Monetize；v5.33 B4：L1_MFleet 外部欄同為 CTL_Monetize；v5.32 B3：兩列的外部欄 M／N＝CTL_Monetize，比值 O 與判讀 P 隨情境改變；D:F（隱含 m）不變
    for (sh, coord), v in cur.items():               # 基準列、L1、Interface 第 1–210 列、其他模型頁：數值不變（只允許 Theory_Rev D 節、Interface H 節、Checks X7 與其彙總；v5.29 起另允許 L1_FleetMargin 列）
        row = int(re.sub(r"[A-Z]+", "", coord))
        if sh == "L1" and row in m_rows and re.sub(r"\d", "", coord) in ("M", "N", "O", "P"):
            continue
        if (sh == "L1" and row != fm_row) or (sh == "Interface" and row <= 210):
            assert v == base_vals[(sh, coord)], (sh, coord, base_vals[(sh, coord)], v)
    assert not any(isinstance(v, str) and v.startswith("#") for v in cur.values())


# ── v5.23 X10：Perf_Batch 側 VR200 批次口徑 η_d 倍數（工作單 1.3、1.4 節） ──
BATCH_PREV = HERE.parent.parent / "model" / "archive" / "20261006_Tokenomics_v5.22.xlsx"        # v5.22（LibreOffice 重算存檔）：X10 之前的口徑
# v5.22 報告第三節 k＝0.75 的結果（VR200 欄相對 k＝1 的變動；報告取兩位小數，容差 6e-5＝0.006 個百分點）
EXPECT_BATCH_075 = {"IF_TrainCost_Luna": {10: 0.1434, 11: 0.1434, 12: 0.1434}, "IF_TrainCost_Sol": {10: 0.1082, 11: 0.1082, 12: 0.1082},
                    "IF_TrainCost_Astra": {10: 0.0921, 11: 0.0921, 12: 0.0921}, "TRN_GPUhRL": {10: 0.1426, 11: 0.1459, 12: 0.1596},
                    "IF_FullCost_Luna": {11: 0.012013}, "IF_FullCost_Sol": {11: 0.007639}, "IF_FullCost_Astra": {11: 0.025955}}
# v5.29 X14 (k)(l)：L1_Ans1 0.0452 → 0.0530（Q1 對研發 GW 的彈性隨服務 GW 上升而改變；引擎重算值 0.052959；不受 Alloc 輸入影響的其餘項不變）
EXPECT_BATCH_075_SCALAR = {"L1_Ans1": 0.0,       # v8.0 L3：研發世代組合（VR200＝0）使 Q1 不再隨 VR200 批次 η_d 改變，0.07892 → 0；v6.2（2-1-b／c）：Hopper Astra 排除、Alloc 重新正規化後服務 GW 對 η_d 的敏感度 0.0839 → 0.07892；v5.33 J8：2025 組合 Hopper 60／GB200 40 使服務 GW 對 η_d 更敏感，0.0530 → 0.0829（LibreOffice 重算值；工作單 B2 預期連動）
                            "L1_Ans3": 0.0, "L1_Ans6_GPUh": 0.1039, "L1_Ans5_FullMargin": -0.0004,
                           "L1_RLshare_Sol_VR200": 0.1459, "L1_RLshare_Astra_VR200": 0.1596}
EXPECT_BATCH_075_RATIO = (1.762, 1.811, 1.923)      # Perf_Batch 第 88 列 VR200（L、M、N）÷ GB300（I、J、K）；k＝1 時為 2.350、2.414、2.564


# v5.31 J1／J2（Andy 2026-10-08「不反對，請繼續」）：GB300 機架價格與 IT 維護等值費率改變成本鏈；test_batch_etad_expected_values 比對 v5.22 時，
# 略過「v5.30 → v5.31 值有改變」的具名範圍（以兩版 LibreOffice 重算存檔逐名稱比較；與 X10 無關）
V530_PREV = HERE.parent.parent / "model" / "archive" / "20261008_Tokenomics_v5.30.xlsx"
V532_PREV = HERE.parent.parent / "model" / "archive" / "20261011_Tokenomics_v5.32.xlsx"      # v5.33 J8／J9：Alloc_In 世代組合與每則提示 token 數高端改變 Alloc 鏈（與 X10 無關）


def _names_changed_v531(model, prev=None):
    import openpyxl
    from openpyxl.utils import range_boundaries
    a, b = openpyxl.load_workbook(prev or V530_PREV, data_only=True), openpyxl.load_workbook(model, data_only=True)
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


def test_batch_etad_expected_values(model, lo):
    """v5.23 X10：基準 CAL_BatchEtaD＝[1,1,1,0.75,1]；h_batch_etad_100（VR200 設回 1）時，v5.22 的全部具名範圍（除 IDX_SrcID：SRC_Index 新增哨兵列）逐格相等
    ——只有 X10 造成改變；k＝0.75 相對 k＝1 的變動等於 v5.22 報告第三節；改變的具名範圍恰為 85 個（報告 82 個＋3 個對應的 _Prod）；
    IF_TrainGenDefault 仍為 4；TR_*、IF_RevGW_*、IF_RevGWFleet、_Life 不變；GOV_Errors＝0（Checks X1 的 _Prod 自我檢查維持 0）。"""
    import openpyxl
    from openpyxl.utils import range_boundaries
    true_base = _vo(lo, {})
    assert true_base.get_name("CAL_BatchEtaD")[0] == 1 and abs(true_base.get_name("CAL_BatchEtaD")[1] - 2.198284) < 1e-6 and true_base.get_name("CAL_BatchEtaD")[2:] == [1, 0.75, 1]      # v15.3 C2：D156 由常數 2.36 改為兩反推點幾何平均 2.198284；      # v12.0 H2：GB200 3.04 → 2.36（＝√(1.83×3.04) 取小數 2 位）； v11.0 G2：GB200 1 → 3.04（大批次校準）；其餘不變
    assert true_base.get_name("GOV_Errors") == 0 and true_base.get_name("IF_TrainGenDefault") == 4
    # v11.0：本測試隔離 X10（VR200 的 0.75）。為不讓 G2 的 GB200 3.04 混入「只有 X10 造成改變」的斷言，兩邊都把 GB200 設回 1（＝v10.3 的 [1,1,1,0.75,1]），其餘期望值不變。
    base = _vo(lo, {"CAL_BatchEtaD[2]": 1.0})
    eng = _vo(lo, {"CAL_BatchEtaD[2]": 1.0, "CAL_BatchEtaD[4]": 1.0})
    cur = eng.evaluate_all()
    assert not any(isinstance(v, str) and v.startswith("#") for v in cur.values()) and eng.get_name("GOV_Errors") == 1      # v11.0：D156（GB200 倍數）設回 1 落在其區間 1.5–6.7 之外，Checks E10＝1（與 B4_CacheHit＝0 同類，預期）；其餘錯誤 0
    prev = openpyxl.load_workbook(BATCH_PREV, data_only=True)
    v531_changed = _names_changed_v531(model) | _names_changed_v531(model, V532_PREV)     # v5.33：加上 v5.32 → v5.33 改變的名稱（Alloc 鏈：AL_Blend*、AL_Mix*、L1_ScaleServe、L1_GapPrompt_Hi 等）
    assert "AL_BlendPaid" in v531_changed and "IF_HoldEcon" in v531_changed      # v6.1：IF_RevGW_Sol、TRN_GPUhRL 的 Hopper 欄隨 D6（Calib C67）改變，不再斷言「不在其中」
    bad = []
    for n, dn in prev.defined_names.items():
        # v5.25：新增 SRC 紀錄使 SRC_Index 堆疊位移、W1 計數改變；IDX_*、GOV_* 不屬 X10 範圍（GOV_Errors＝0 已於上方另行斷言）
        if n.startswith(("IDX_", "GOV_")):
            continue
        if n in ("B5_TaskTok", "B5_SelVendor"):      # v14.0（4-3B Q1）：無人使用的名稱已依工作單移除
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
    assert len(changed) == 56, len(changed)      # v13.0 K2：RG2 最多算 1 後仍為 56（未改期望值）； v8.0 L3：研發世代組合 Hopper 0.6/GB200 0.38/GB300 0.02（VR200＝0），VR200 批次 η_d 不再改變研發 GW，Alloc 鏈（AL_ 15、IF_Alloc* 5）與 L1 9 列不再隨之變動；85 → 56
    by = {p: sum(n.startswith(p) for n in changed) for p in ("IF_", "L1_", "AL_", "TRN_")}
    assert by == {"IF_": 36, "L1_": 12, "AL_": 0, "TRN_": 8} and sum(n.endswith("_Prod") for n in changed) == 3, by       # 82＝IF 38＋L1 21＋TRN 8＋AL 15
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


def test_v529_contract_waterfall_expected_values(model, lo):
    """v5.29：IFC_ 四欄與 Interface 資料列同長且值域正確；IFW_ 44 個名稱各 15 欄；有對應列的 _Util／_Prod／_Life 逐格等於來源列（Checks K3＝0）；
    L1 新列的 LibreOffice 重算值（工作單第 3、3b 節）；Checks K2、K3＝0、K4＝0（r2 第 2 項：L1_FleetMargin＝Theory_Rev 機隊比值 × CTL_ProdDerate × CTL_PriceLife × CTL_Monetize）、K5＝50；GOV_Errors＝0。"""
    eng = _vo(lo, {})
    conf, use, layer, upd = (eng.get_name(n) for n in ("IFC_Conf", "IFC_Use", "IFC_Layer", "IFC_Updated"))
    assert len(conf) == len(use) == len(layer) == len(upd) >= 300
    assert set(x for x in conf if x not in ("", None)) <= {"A", "B", "C", "—", "（表頭）"}
    assert set(x for x in layer if x not in ("", None)) <= {"100%", "IF_Util", "CTL_ProdDerate", "L×m", "自算 L×m", "—"}
    assert sum(1 for x in conf if x == "—") == 0 and conf.count("B") > conf.count("A") > 0
    for b in IFW_BASES:
        for suf in ("100", "Util", "Prod", "Life"):
            v = eng.get_name(f"IFW_{b}_{suf}")
            assert isinstance(v, list) and len(v) == 15, (b, suf)
        util = eng.get_name(f"IFW_{b}_Util")
        if b.startswith("TokGW"):
            assert all((abs(u - x * eng.get_name("IF_Util")) <= 1e-9 * abs(x)) if _num(x) else u == x for u, x in zip(util, eng.get_name(f"IF_{b}")))      # v6.2：文字旗標（TTFT／SLO 不可達）原樣傳遞
            assert eng.get_name(f"IFW_{b}_100") == eng.get_name(f"IF_{b}")
        else:
            assert util == eng.get_name(f"IF_{b}")
            if f"IF_{b}_Prod" in eng.names: assert eng.get_name(f"IFW_{b}_Prod") == eng.get_name(f"IF_{b}_Prod")
            # v5.30 X15 (a)：_Life 改為 _Prod × L × m（不再等於 H 節 IF_*_Life）；逐層累乘的斷言見 test_v530_waterfall_running_product
    want = {"L1_FleetBreakeven": 0.130432, "L1_FleetMargin": 3.554764, "L1_HoldEconMW_VR200": 12.225471,      # v7.0（2-2-b）：FleetMargin 3.387612 → 3.554764（生產折減改讀重解值，L1_FleetProdRatio 0.772761，線性為 0.85）；v5.31 J2（IT 維護等值費率）：0.157156 → 0.130432、3.245188 → 3.387612、12.762016 → 12.225471；v5.30 X15 (b)：HoldEconMW 不除以 1000（0.012762 → 12.762016）
            "L1_TokMW_Gen_ratio_VR200": 1.597061,
            "L1_HarVsGen_Coding": 0.697395, "L1_AstraScale": 14.616242, "L1_ScaleRD": 6.350031, "L1_ScaleServe": 5.97049,      # v12.0 H2：L1_ScaleRD 6.475644 → 6.294125（研發 GW 0.197258 → 0.202947）； v11.0 G2：L1_ScaleRD 5.317978 → 6.475644（GB200 CAL_BatchEtaD 3.04，研發 GW 0.2402 → 0.1973）；v6.2（2-1-b／c）：4.749776 → 5.406066（Hopper Astra 排除後 Alloc 重新正規化，AL_ServeGW 0.189082 → 0.166128）；L1_GapPrompt 1.301125 → 1.298854、L1_GapProduct 1.618473 → 1.635216  # v15.2 B2／B3 預期變動：期望值依重算結果更新
                  # v5.33 J8：ScaleServe 18.067049 → 7.377857（2025 組合 Hopper 60／GB200 40：token 路線服務 GW 0.0675 → 0.1826、支出路線 1.2196 → 1.3471）；v5.31：HarVsGen_Coding 0.780699 → 0.697395（GB300 decode 成本下降）、ScaleRD 10.368786 → 10.823846、ScaleServe 16.502022 → 18.067049（持有成本下降）
            "L1_GapPrompt": 1.299156, "L1_GapSpendBasis": 0.85, "L1_GapISL": 1.0, "L1_GapUtil": 1.721664, "L1_GapProduct": 1.901204}   # LibreOffice 重算值（小數第 6 位）；v7.0（2-2-b）：GapUtil 1.463415 → 1.721664（分母乘 CTL_ProdDerate）、GapProduct 1.635216 → 1.900762  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    for n, v in want.items():
        got = eng.get_name(n)
        assert abs(got - v) < 5e-6, (n, got, v)
        lo, hi = eng.get_name(n + "_Lo"), eng.get_name(n + "_Hi")
        assert lo <= got <= hi, (n, lo, got, hi)
    assert abs(eng.get_name("L1_FleetMargin") - eng.get_name("IFW_RevGWFleet_Prod")[10] / eng.get_name("IF_HoldEcon")[10] * eng.get_name("CTL_PriceLife") * eng.get_name("CTL_Monetize")) < 1e-9      # v7.0（2-2-b）：讀重解值（Interface 第 210 列），不再線性乘 CTL_ProdDerate
    assert abs(eng.get_name("L1_FleetProdRatio") - eng.get_name("IFW_RevGWFleet_Prod")[10] / eng.get_name("IFW_RevGWFleet_Util")[10]) < 1e-12 and abs(eng.get_name("L1_FleetProdRatio") - 0.772761) < 5e-6
    assert abs(eng.get_name("L1_GapUtil") - eng.get_name("IF_Util") / (eng.get_name("AL_UtilActual") * eng.get_name("CTL_ProdDerate"))) < 1e-12
    assert eng.get("Checks", "D121") == 0 and eng.get("Checks", "D91") == 18      # v15.2：舊 SLO 視圖 I3 17 → 18（B2／B3 預期變動）；# v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：舊 SLO 視圖 I3（L1 外部對照差距 >20% 的列數）20 → 17；        # v5.34：I3 17 → 18（L1_TokPerPromptClose 判讀「高於外部區間」）；v5.31：I3 15 → 17（L1_GPUhr_GB300_vsBE、L1_GapProduct）；r2：K4＝0；I3 17 → 15（FleetMargin、HoldEconMW_GB300 外部欄改「—」）
    assert eng.get("L1", "P53") == "無外部對照" and eng.get("L1", "P56") == "無外部對照"
    assert abs(eng.get_name("L1_GapProduct") - eng.get_name("L1_GapPrompt") * eng.get_name("L1_GapSpendBasis") * eng.get_name("L1_GapISL") * eng.get_name("L1_GapUtil")) < 1e-9
    assert eng.get_name("LB_LiveCount") == 56 and len(eng.get_name("LB_Rows")) == 56      # v15.2：57 → 56（GM342 類別 Analogy → Derived 離開承重清單，修訂九更正）； v13.0 K3：56 → 57（Calib C68 類別『倒推』更正為 Assumed，高段，回到承重清單）； v12.0 H3：55 → 56（Gov_Map 新增 Calib C156 Hopper 列，Assumed、高段，列入 Load_Bearing）； v7.0：56 → 55（Calib C68 類別 Assumed → 倒推）；v6.2：53 → 56（模型規模倍數三列，高段 Assumed）
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CHK_L1Order") == 0
    assert eng.get_name("SRC_DEM_018") == 12.6 and eng.get("SRC_Demand", "O8") == "Active" and eng.get_name("SRC_DEM_004") == 8.4 and eng.get_name("AL_TokPerPrompt") == 4000   # r2 第 1 項：004 與 018 並列 Active
    assert abs(eng.get_name("AL_SpendRatio") - 0.588235) < 5e-6 and abs(eng.get_name("AL_FreeSpendShare") - 0.464286) < 5e-6 and abs(eng.get_name("AL_ServeGWSpend") - 0.898096) < 5e-6   # v5.33 J8：1.219639 → 1.347144（組合持有成本 10.33 → 9.35）；v5.31：1.113990 → 1.219639（支出 ÷ 持有成本，持有成本下降）；r2：C55／C63 回到 004，C61 用 018
    assert abs(eng.get("L1", "M49") - 0.357307) < 5e-6 and abs(eng.get("L1", "M46") - 0.898096) < 5e-6   # v5.33 J8：1.219639 → 1.347144；v5.31：1.113990 → 1.219639；r2：Ans5_GM 外部值回到 004 口徑；ExtServeGW 外部值用 018
    assert eng.get("Gov_Map", "AK4") is not None and eng.get("Load_Bearing", "K5") == "—" and eng.get("Load_Bearing", "K54") == "—"   # r2 第 7 項：反轉門檻欄（Gov_Map AK，Excel 擁有）；Load_Bearing K 欄以公式讀取，本版空白


# ── v5.30 X15（工作單 docs/workorders/20261008_v5.30.md r0）：四層瀑布逐層累乘、L1_HoldEconMW 單位更正、IFW_ 上限標記 ──
def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def test_v530_waterfall_running_product(model, lo):
    """v5.30：(a) _Prod＝_Util × CTL_ProdDerate（營收列有 G 節者讀 G 節）、_Life＝_Prod × L × m（營收）／＝_Prod（token）；四層單調遞減；Checks K3＝0；
    VR200 基準欄（索引 10）LibreOffice 重算值；(b) L1_HoldEconMW_*＝L1_HoldEconGW_*（含 _Lo／_Hi）；(c) IFW_ 營收四層與 IFW_TokGW_*_100 的 IFC_Use 含「上限」，K2＝0。"""
    eng = _vo(lo, {})
    d, lm = eng.get_name("CTL_ProdDerate"), eng.get_name("CTL_PriceLife") * eng.get_name("CTL_Monetize")
    for b in IFW_BASES:
        v100, util, prod, life = (eng.get_name(f"IFW_{b}_{s}") for s in ("100", "Util", "Prod", "Life"))
        if b.startswith("TokGW") or f"IF_{b}_Prod" not in eng.names:      # v6.0 D7-1：_Prod 為生產折減下重解 SLO 的產能，不再是 _Util × d；只要求不高於 _Util
            assert all(p <= u * (1 + 1e-9) for u, p in zip(util, prod) if _num(u) and _num(p)), b
        if b.startswith("TokGW"):
            assert prod == life, b
        else:
            assert all(abs(x - p * lm) <= 1e-9 * abs(p) for p, x in zip(prod, life) if _num(p)), b
        for col in zip(v100, util, prod, life):
            nums = [x for x in col if _num(x)]
            assert all(a >= c - 1e-9 * max(1, abs(a)) for a, c in zip(nums, nums[1:])), (b, col)
    want = {"IFW_TokGW_Sol": (282304255592.62, 169382553355.572, 135519952313.859, 135519952313.859),
            "IFW_RevGW_Sol": (453.694305876851, 272.216583526111, 217.795621140851, 217.795621140851)}
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
    assert n_cap == 8 * 4 + 3 + 8      # v10.0 N1：Interface L 節 8 個 _LifeSelf 列同樣標「上限，不得作預測」



# ── v5.31 J1–J6（工作單 docs/workorders/20261008_v5.31.md r1）：GB300 機架價格、IT 維護機齡兩段（壽命期等值費率）、IREN 對照 ──
def test_v531_rack_price_and_it_maint(model, lo):
    """v5.31：(J1) Spec_Rack GB300 機架價格 4.0／4.3／5.0；(J2／J3) Inputs 第 30 列＝兩段費率以同欄 WACC、IT 折舊年限年金加權（以 Python 逐年加總驗算），
    IF_MaintITWarr／IF_MaintITPost＝IT 資本 × 兩段費率，IF_WarrantyYrs＝3；IF_MaintIT＝IT 資本 × 等值費率；加總核對列仍為 0；
    (J6) L1_CapexITMW_GB300_vsIREN＝GB300 IF_CapexIT 對 SRC_DC_014；GB300／VR200 基準欄 LibreOffice 重算值。"""
    eng = lo.view({})
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


# ── v5.32（工作單 docs/workorders/20261011_v5.32.md r1）：變現率 m 追蹤（Cap_In H 節、L1_MImplied／_Ext、Checks M1） ──
def test_v532_m_tracking(model, lo):
    """v5.32：L1_MImplied（合併、模型 token 分母）基準＝SRC_DEM_007 ÷（AL_DPaid × 層級組合混合單價）＝2.033528（A 段第 6 節 1.74）；
    外部欄＝CTL_Monetize（1）；判讀「落在 0.3–1.0 區間外」；L1_MImplied_Ext 以 Epoch 幾何中點；Checks M1＝1（WARN）；CTL_Monetize 仍為 1；GOV_Errors＝0。
    期望值為 v5.32 LibreOffice 重算值；另以 Python 由具名範圍驗算基準式（1e-12）。"""
    import re
    eng = lo.view({})
    assert eng.get_name("CTL_Monetize") == 1 and eng.get_name("GOV_Errors") == 0
    mix = eng.get_name("B4_MixPaid")
    price = eng.get_name("CAP_Price25Mix")      # v9.0 M6：需求路線 m 用 2025 年度混合有效單價（× κ；v8.0 為 2026 快照 IF_PriceRef 加權）
    m = eng.get_name("SRC_DEM_007") * 1e9 / (eng.get_name("AL_DPaid") * price)
    assert abs(eng.get_name("L1_MImplied") - m) <= 1e-12 * m
    want = {"L1_MImplied": (2.513547, 1.085103, 4.259697), "L1_MImplied_Ext": (2.082516, 0.658549, 6.585492)}      # v5.33 J9：MImplied _Lo 1.051059 → 0.877878（每則提示 token 數高端 6,400 → 11,000）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    for n, (d, lo, hi) in want.items():
        for suf, v in (("", d), ("_Lo", lo), ("_Hi", hi)):
            assert abs(eng.get_name(n + suf) - v) < 5e-6, (n + suf, eng.get_name(n + suf), v)
    epoch = (eng.get_name("SRC_DEM_013_Lo") * eng.get_name("SRC_DEM_013_Hi")) ** 0.5
    ext = eng.get_name("SRC_DEM_007") * 1e9 / (epoch * 1e6 * 365 * (1 - eng.get_name("AL_FreeShare")) * eng.get_name("CAP_Price25Mix"))
    assert abs(eng.get_name("L1_MImplied_Ext") - ext) <= 1e-12 * ext
    for n in ("L1_MImplied", "L1_MImplied_Ext"):
        r = int(re.sub(r"[A-Z]+", "", eng.names[n].rsplit("!", 1)[1].replace("$", "")))
        assert eng.get("L1", f"M{r}") == 1 and eng.get("L1", f"N{r}") == 1 and eng.get("L1", f"P{r}") == "落在 0.3–1.0 區間外", n
    import openpyxl
    wb = openpyxl.load_workbook(model, read_only=True)                  # 標籤（常數格）以 openpyxl 讀；數值一律由引擎計算
    ck = {wb["Checks"][f"A{r}"].value: r for r in range(100, 140)}
    assert eng.get("Checks", f"D{ck['M1']}") == 1
    cap = {wb["Cap_In"][f"A{r}"].value: r for r in range(66, 109) if isinstance(wb["Cap_In"][f"A{r}"].value, str)}
    def row(prefix):
        return next(r for lab, r in cap.items() if lab.startswith(prefix))
    sub, api = row("隱含 m — 訂閱路線（模型 token）"), row("隱含 m — API 路線（模型 token）")
    assert abs(eng.get("Cap_In", f"C{sub}") - 4.609845) < 5e-6 and abs(eng.get("Cap_In", f"C{api}") - 1.219536) < 5e-6
    assert abs(eng.get("Cap_In", f"C{row('2025 期間平均訂閱數')}") - 32.75) < 1e-12
    assert abs(eng.get("Cap_In", f"C{row('對照：程式代理訂閱 m')}") - 200 / (13 * 21)) < 1e-12


# ── v5.33（工作單 docs/workorders/20261012_v5.33.md r1）：付費 token 數量校準（Alloc_In J8／J9、Cap_In H7 機隊口徑、L1_MFleet／L1_TokCeiling、Checks M2／M3） ──
def test_v533_fleet_basis(model, lo):
    """v5.33：Alloc_In 2025 組合 Hopper 0.6／GB200 0.4／GB300 0／VR200 0（J8）、每則提示 token 數高端 11,000（J9）；
    機隊付費 token 點估計＝AL_ServeGWSpend ÷ AL_SpendBasis × AL_UtilActual ÷ IF_Util ÷（1 ÷ AL_BlendPaid ＋ r ÷ AL_BlendFree），r＝AL_DFree ÷ AL_DPaid；
    上限以 CTL_ProdDerate 取代利用率修正。工作單錨點：AL_ServeGW 0.18、L1_ScaleServe 7.4、AL_ServeGWSpend 1.35、機隊付費 token 8.2e9、上限 12.0e9、機隊 m 0.81、m 下限 0.56。
    L1_MFleet 判讀「落在 0.3–1.0 區間內」、L1_TokCeiling 外部欄＝AL_DPaid；Checks M2＝M3＝0、M1 仍為 1；GOV_Errors＝0。期望值為 LibreOffice 重算值，另以 Python 驗算基準式（1e-12）。"""
    import re
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CTL_Monetize") == 1
    assert eng.get_name("AL_MixGen") == [0.6, 0.4, 0, 0] and eng.get_name("AL_TokPerPrompt_Hi") == 11000 and eng.get_name("AL_TokPerPrompt") == 4000
    assert eng.get_name("AL_GenOK") == [1, 1, 1, 1]                                  # Hopper 等四世代皆至少有一個可達層級（v6.2：Hopper 的 Astra 層 TTFT 不可達，但 Luna、Sol 可達，世代仍可服務；原 B2 硬性條件為三層皆可達）
    mix = eng.get_name("B4_MixPaid")
    price = eng.get_name("AL_PriceFleet25")      # v8.0 L1：2025 年度機隊口徑單價（v6.3 K1 為 AL_PriceFleet，2026 快照）；v6.3 K1：機隊口徑單價（可達層級重新正規化、以付費 token 加權）；v6.2 以前為全層混合 mix·IF_PriceRef
    gw = eng.get_name("AL_ServeGWSpend") / eng.get_name("AL_SpendBasis") * eng.get_name("AL_Kappa")
    r = eng.get_name("AL_DFree") / eng.get_name("AL_DPaid")
    den = 1 / eng.get_name("AL_BlendPaid") + r / eng.get_name("AL_BlendFree")
    tok = gw * eng.get_name("AL_UtilActual") * eng.get_name("CTL_ProdDerate") / eng.get_name("IF_Util") / den      # v6.1 D13-2：利用率修正乘 CTL_ProdDerate
    ceil = gw * eng.get_name("AL_ProdRatioPaid") / den      # v6.0 D7-2：上限讀付費產能比（原 CTL_ProdDerate）
    m = eng.get_name("SRC_DEM_007") * 1e9 / (tok * price)
    assert abs(eng.get_name("L1_MFleet") - m) <= 1e-12 * m and abs(eng.get_name("L1_TokCeiling") - ceil) <= 1e-12 * ceil
    for n, v in (("AL_ServeGW", 0.150423), ("L1_ScaleServe", 5.97049), ("AL_ServeGWSpend", 0.898096), ("L1_MFleet", 0.61609), ("L1_MFleet_Lo", 0.362666),      # v6.2（2-1-b／c）：AL_ServeGW 0.189082 → 0.166128、L1_ScaleServe 4.749776 → 5.406066、L1_MFleet 0.536920 → 0.449740；v6.1：D6／D10／D13 的預期連動（v6.0：0.182593、4.918571、0.789593、0.442881）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
                 ("L1_MFleet_Hi", 1.783038), ("L1_GapPrompt_Hi", 2.346201), ("L1_MImplied", 2.513547)):  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-6, (n, eng.get_name(n), v)
    for n, v in (("L1_TokCeiling", 18973895737), ("L1_TokCeiling_Lo", 8959895209), ("L1_TokCeiling_Hi", 26511470756)):      # v6.2（v6.1：15293496511、7221928908、21368995125）；v6.1（v6.0：10309020853、5444451638、16082072531）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 1, (n, eng.get_name(n), v)
    assert abs(eng.get_name("SRC_DEM_007") * 1e9 / (eng.get_name("L1_TokCeiling") * price) - 0.506739) < 5e-6      # m 下限（v6.2：0.435876 → 0.352267，Hopper Astra 排除後上限 token 上升；v6.1：0.646625 → 0.435876，D10 計價倍數 0.85 使服務 GW 上升、上限 token 上升；v6.0 D7-2：0.541878 → 0.646625）
    assert eng.get_name("AL_DPaid") < eng.get_name("L1_TokCeiling")
    for n in ("L1_MFleet", "L1_TokCeiling"):
        rr = int(re.sub(r"[A-Z]+", "", eng.names[n].rsplit("!", 1)[1].replace("$", "")))
        assert eng.get("L1", f"E{rr}") <= eng.get("L1", f"D{rr}") <= eng.get("L1", f"F{rr}"), n
        if n == "L1_MFleet":
            assert eng.get("L1", f"M{rr}") == 1 and eng.get("L1", f"P{rr}") == "落在 0.3–1.0 區間內"
        else:
            assert eng.get("L1", f"M{rr}") == eng.get_name("AL_DPaid") and eng.get("L1", f"P{rr}").startswith("需求路線 ÷ 上限＝0.20（需求在上限內）")      # v6.2：上限 token 上升（Hopper Astra 排除、Alloc 重新正規化），0.25 → 0.20
    import openpyxl
    wb = openpyxl.load_workbook(model, read_only=True)
    ck = {wb["Checks"][f"A{r}"].value: r for r in range(100, 140)}
    assert eng.get("Checks", f"D{ck['M1']}") == 1 and eng.get("Checks", f"D{ck['M2']}") == 0 and eng.get("Checks", f"D{ck['M3']}") == 0
    cap = {wb["Cap_In"][f"A{r}"].value: r for r in range(66, 135) if isinstance(wb["Cap_In"][f"A{r}"].value, str)}
    row = lambda p: next(r for lab, r in cap.items() if lab.startswith(p))
    assert abs(eng.get("Cap_In", f"C{row('機隊付費 token（點估計）')}") - tok) <= 1e-12 * tok
    assert abs(eng.get("Cap_In", f"C{row('對照：r 支出口徑換算')}") - 3.336269) < 5e-6      # v6.2（v6.1：3.226505）
    assert abs(eng.get("Cap_In", f"C{row('對照：r 支出口徑換算')}") - 3.336269) < 5e-6 and abs(eng.get("Cap_In", f"C{row('免費 ÷ 付費 token 比 r（模型）')}") - 0.572519) < 5e-6
    assert eng.get("Cap_In", f"E{row('m＝1 所需付費 token')}").startswith("低於上限") and eng.get("Cap_In", f"E{row('m＝0.3 所需付費 token')}").startswith("高於上限")
    assert abs(eng.get("Cap_In", f"D{row('m＝1 所需付費 token')}") - eng.get_name("L1_MImplied") * eng.get_name("CAP_Price25Mix") / price) < 1e-9          # m＝1 所需 token ÷ AL_DPaid＝L1_MImplied × 2025 全層單價 CAP_Price25Mix ÷ 機隊口徑單價 AL_PriceFleet25（v9.0 M6；v6.3 K1 為 Cap_In C90；v6.2 以前＝L1_MImplied）
    assert eng.get("Cap_In", f"C{row('非文字服務份額')}") == 0.1 and abs(eng.get("Cap_In", f"C{row('扣除非文字後 — 合併隱含 m')}") - 2.337598) < 5e-6


# ── v5.34（工作單 docs/workorders/20261014_v5.34.md r0.1）：變現率 m 細化（Cap_In H8 m 分拆、H9 token 帳三路線、H10 季度序列、L1 六列、Checks M4） ──
def test_v534_m_split(model, lo):
    """v5.34：三分法 m_API＝(SRC_DEM_007 −消費訂閱 −商用席次) ÷（AL_DAPI × 單價）＝0.657758（錨點 0.56）、m_消費訂閱 4.972653（4.26）、m_商用席次 2.131137（1.83）、
    m_整體＝L1_MImplied 2.033528（三分只是同一分子分母的重排）；折讓因子 D 欄 0.75（B4_Disc 高端 0.3 → 0.4，J20）；隱含組合因子＝m_API；閉合解 τ* 13,949.6（≈13,950）、
    閉合免費占比 0.213；H10 2026 Q2 欄 m_API 0.3467（0.35）、m_整體 1.3432（1.34）、m_fleet 0.7811（0.78）、m_消費訂閱 4.768、m_商用席次 6.502；Checks M4＝1（WARN，預期）；
    既有 IF_Price*、L1_MImplied、L1_MFleet 不變；GOV_Errors＝0。期望值為 LibreOffice 重算值，另以 Python 由具名範圍驗算基準式（1e-12）。"""
    import re
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CTL_Monetize") == 1
    assert eng.get_name("B4_Disc") == 0.2 and eng.get_name("B4_Disc_Lo") == 0.1 and eng.get_name("B4_Disc_Hi") == 0.4      # J20：只動高端
    assert abs(eng.get_name("IF_PriceRef_Sol") - 1.607111) < 5e-6 and abs(eng.get_name("L1_MImplied") - 2.513547) < 5e-6 and abs(eng.get_name("L1_MFleet") - 0.61609) < 5e-6      # v8.0 L1：0.471739 → 0.550473（2025 年度單價）；v6.3 K1：0.449740 → 0.471739；v6.2：0.536920 → 0.449740（Hopper Astra TTFT 排除、Alloc 重新正規化）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    mix = eng.get_name("B4_MixPaid")
    price = eng.get_name("CAP_Price25Mix")      # v9.0 M6
    rev = eng.get_name("SRC_DEM_007"); cons = rev * eng.get_name("SRC_DEM_039"); seat = rev * 0.10; api = rev - cons - seat
    t_api = eng.get_name("AL_DAPI"); t_cons = eng.get_name("AL_DChatPaid") * 0.75; t_seat = eng.get_name("AL_DChatPaid") * 0.25
    for n, v in (("L1_MAPI", api * 1e9 / (t_api * price)), ("L1_MSub", cons * 1e9 / (t_cons * price)), ("L1_MSeat", seat * 1e9 / (t_seat * price)), ("L1_MixFactorAPI", api * 1e9 / (t_api * price))):
        assert abs(eng.get_name(n) - v) <= 1e-12 * v, (n, eng.get_name(n), v)
    for n, v in (("L1_MAPI", 0.813024), ("L1_MSub", 6.146459), ("L1_MSeat", 2.634197), ("L1_MixFactorAPI", 0.813024), ("L1_MAPI_Lo", 0.152442), ("L1_MAPI_Hi", 1.144708),  # v15.2 B2／B3 預期變動：期望值依重算結果更新
                 ("L1_MSub_Lo", 1.085766), ("L1_MSub_Hi", 36.000691), ("L1_MSeat_Lo", 0.798241), ("L1_MSeat_Hi", 9.878238), ("L1_MixFactorAPI_Lo", 0.135504), ("L1_MixFactorAPI_Hi", 1.526277)):  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-6, (n, eng.get_name(n), v)
    for n, v in (("L1_TokPerPromptClose", 30749.840443), ("L1_TokPerPromptClose_Lo", 8495.527649), ("L1_TokPerPromptClose_Hi", 72872.637423)):      # v6.2（v6.1：23406.608、5978.106、56561.745）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-3, (n, eng.get_name(n), v)
    gw = eng.get_name("AL_ServeGWSpend") / eng.get_name("AL_SpendBasis") * eng.get_name("AL_Kappa") * eng.get_name("AL_UtilActual") * eng.get_name("CTL_ProdDerate") / eng.get_name("IF_Util")
    fs = eng.get_name("AL_FreeShare"); bp, bf = eng.get_name("AL_BlendPaid"), eng.get_name("AL_BlendFree")
    tchat = (gw - t_api / bp) / ((1 - fs) / bp + fs / bf)
    tau = tchat * 1e6 / (eng.get_name("SRC_DEM_012") * 1e9 * 365)
    assert abs(eng.get_name("L1_TokPerPromptClose") - tau) <= 1e-12 * tau
    assert eng.get_name("L1_MAPI_Anthropic") == "缺分母（需 Anthropic 年 API token）"
    for n in ("L1_MAPI", "L1_MSub", "L1_MSeat", "L1_MixFactorAPI", "L1_TokPerPromptClose"):
        rr = int(re.sub(r"[A-Z]+", "", eng.names[n].rsplit("!", 1)[1].replace("$", "")))
        assert eng.get("L1", f"E{rr}") <= eng.get("L1", f"D{rr}") <= eng.get("L1", f"F{rr}"), n
        if n in ("L1_MAPI", "L1_MSub", "L1_MSeat"):
            assert eng.get("L1", f"M{rr}") == 1 and eng.get("L1", f"P{rr}") == ("落在 0.3–1.0 區間內" if n == "L1_MAPI" else "落在 0.3–1.0 區間外"), n
        elif n == "L1_MixFactorAPI":
            assert abs(eng.get("L1", f"M{rr}") - 0.196164) < 5e-6 and eng.get("L1", f"P{rr}").startswith("代理型極端組合因子 0.20；本值為其 4.1 倍")
        else:
            assert eng.get("L1", f"M{rr}") == 2000 and eng.get("L1", f"N{rr}") == 11000 and eng.get("L1", f"P{rr}") == "高於外部區間"
    rr = int(re.sub(r"[A-Z]+", "", eng.names["L1_MAPI_Anthropic"].rsplit("!", 1)[1].replace("$", "")))
    assert abs(eng.get("L1", f"M{rr}") - 0.828067) < 5e-6 and abs(eng.get("L1", f"N{rr}") - 0.1625) < 1e-9 and eng.get("L1", f"P{rr}") == "推算值非數字（本情境）"
    import openpyxl
    wb = openpyxl.load_workbook(model, read_only=True)
    ck = {wb["Checks"][f"A{r}"].value: r for r in range(100, 140)}
    assert eng.get("Checks", f"D{ck['M1']}") == 1 and eng.get("Checks", f"D{ck['M2']}") == 0 and eng.get("Checks", f"D{ck['M3']}") == 0 and eng.get("Checks", f"D{ck['M4']}") == 1
    cap = {wb["Cap_In"][f"A{r}"].value: r for r in range(130, 225) if isinstance(wb["Cap_In"][f"A{r}"].value, str)}      # v5.35：H10 以第 224 列自我檢查結束，I 節另測
    row = lambda p: next(r for lab, r in cap.items() if lab.startswith(p))
    assert eng.get("Cap_In", f"C{row('自我檢查：m_整體')}") == 0 and eng.get("Cap_In", f"E{row('自我檢查：m_整體')}") == 0
    assert eng.get("Cap_In", f"C{row('折讓因子')}") == 1 and abs(eng.get("Cap_In", f"D{row('折讓因子')}") - 0.75) < 1e-12 and abs(eng.get("Cap_In", f"E{row('折讓因子')}") - 1.125) < 1e-12
    assert abs(eng.get("Cap_In", f"C{row('殘差：需求 ÷ 機隊')}") - 0.245108) < 5e-6 and abs(eng.get("Cap_In", f"C{row('殘差：需求 ÷ 上限')}") - 0.201603) < 5e-6      # v6.2（v6.1：0.308102、0.250119）
    assert abs(eng.get("Cap_In", f"C{row('閉合下免費算力占比')}") - 0.240314) < 5e-6      # v6.2（v6.1：0.236734） and eng.get("Cap_In", f"C{row('τ* 對 Alloc_In C15')}") == "高於區間（2,000–11,000）"
    assert abs(eng.get("Cap_In", f"C{row('訂閱 m 下限 — Plus')}") - 20 / 700) < 1e-12 and abs(eng.get("Cap_In", f"C{row('訂閱 m 下限 — Pro')}") - 200 / 14000) < 1e-12
    h10 = row("H10. m 季度序列")                                                                     # H10 列以本節起算（H8 另有同前綴的 m_API 列）
    cap10 = {lab: r for lab, r in cap.items() if r > h10}
    row10 = lambda p: next(r for lab, r in cap10.items() if lab.startswith(p))
    q = {"m_API": 0.340278, "m_消費訂閱": 5.398635, "m_商用席次": 4.557290, "m_整體": 1.343201, "m_fleet": 0.279813}      # 2026 Q2 年化欄（E）；v5.35 B1（J23）：三分營收以 m 分子營收 26.3 為基底、消費份額 0.65 → m_API 0.3467 → 0.3403、m_消費訂閱 4.768 → 5.399、m_商用席次 6.502 → 4.557；m_整體、m_fleet 不變
    for lab, v in q.items():
        assert abs(eng.get("Cap_In", f"E{row10(lab)}") - v) < 5e-6, (lab, eng.get("Cap_In", f"E{row10(lab)}"), v)
    assert abs(eng.get("Cap_In", f"C{row10('m_整體')}") - eng.get_name("L1_MImplied")) <= 1e-9 and abs(eng.get("Cap_In", f"C{row10('m_fleet')}") - eng.get_name("L1_MFleet")) <= 1e-9
    assert eng.get("Cap_In", f"C{row('自我檢查：2025 欄')}") == "一致"
    assert eng.get("Cap_In", f"C{row('營收份額：API')}") == "" and all(abs(eng.get("Cap_In", f"{c}{row('營收份額：API')}") - 0.2) < 1e-12 for c in "DEF")      # v14.1 R5：C 欄（2025 年度，無人讀取）已清空；D–F 欄仍須為 0.2


# ── v5.35（工作單 docs/workorders/20261014_v5.35.md r0）：m 序列三項修正（Cap_In H10）＋ L 拆分（Cap_In I 節、L1 四列） ──
def test_v535_l_split(model, lo):
    """v5.35：L_price＝((1+g)^T − 1) ÷ (T·LN(1+g))＝0.7412（g −0.10、T＝IF_DeprLifeIT 6）、L_total＝0.6426（T1 4、ρ 0.5）、L_demote＝0.867；D 欄（g −0.25、T1 3、ρ＝Luna ÷ Sol 0.05）0.4762／0.342／0.718；
    E 欄（g +0.05、T1 5、ρ 1.0）1.1618／1.1618／1.0；回本所需 L＝L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m）：m＝L1_MFleet 0.3645、m＝L1_MAPI 0.5237；H10 2026 三欄：Q1 m_API 0.295／5.744／3.556／1.192、
    Q2 0.340／5.399／4.557／1.343、FY2026 0.348／5.569／8.044／1.432；2025 欄不變；既有 L1_（含 v5.34 六個）與 IF_ 不變；CTL_PriceLife、CTL_Monetize 皆 1。期望值為 LibreOffice 重算值，另以 Python 由具名範圍驗算（1e-12）。"""
    import math, re
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CTL_PriceLife") == 1 and eng.get_name("CTL_Monetize") == 1
    T = eng.get_name("IF_DeprLifeIT")[1]; assert T == 6                                                     # Hopper 基準欄（工作單 I-4：非 6 停下）
    def lp(g): return 1 if abs(math.log(1 + g)) < 1e-12 else ((1 + g) ** T - 1) / (T * math.log(1 + g))
    def lt(g, t1, rho): return (t1 + rho * (T - t1)) / T if abs(math.log(1 + g)) < 1e-12 else (((1 + g) ** t1 - 1) + rho * ((1 + g) ** T - (1 + g) ** t1)) / (T * math.log(1 + g))
    rho_lo = eng.get_name("IF_PriceRef_Luna") / eng.get_name("IF_PriceRef_Sol") * eng.get_name("IF_TokGW_Luna")[3] / eng.get_name("IF_TokGW_Sol")[3]      # v15.3 E2：牌價比 × 低階模型每 GPU 吞吐倍數（GB200 欄）
    for suf, g, t1, rho in (("", -0.09, 4, 0.5), ("_Lo", -0.20, 3, rho_lo), ("_Hi", 0.05, 5, 0.7)):      # v15.3 E1／E2：g −0.10／−0.25 → −0.09／−0.20；ρ 高端 1.0 → 0.7
       
        for n, v in (("L1_LPrice", lp(g)), ("L1_LTotal", lt(g, t1, rho)), ("L1_LDemote", lt(g, t1, rho) / lp(g))):
            assert abs(eng.get_name(n + suf) - v) <= 1e-12 * v, (n + suf, eng.get_name(n + suf), v)
    for n, v in (("L1_LPrice", 0.763665), ("L1_LTotal", 0.659506), ("L1_LDemote", 0.863606), ("L1_LPrice_Lo", 0.551107), ("L1_LTotal_Lo", 0.396968), ("L1_LDemote_Lo", 0.720309),
                 ("L1_LPrice_Hi", 1.161763), ("L1_LTotal_Hi", 1.096367), ("L1_LDemote_Hi", 0.943709), ("L1_LReqFleet", 2.03604), ("L1_LReqFleet_Lo", 0.70351), ("L1_LReqFleet_Hi", 3.458784)):      # v14.1 R1：L1_LReqFleet_Hi 4.513165 → 3.433754（舊 SLO 視圖下低端欄下限 0.3266 高於點估計 0.2485，下限截斷生效）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-6, (n, eng.get_name(n), v)
    req = lambda m: eng.get_name("L1_FleetBreakeven2025") / (eng.get_name("IF_Util") * eng.get_name("CTL_ProdDerate") * eng.get_name(m))
    assert abs(eng.get_name("L1_LReqFleet") - req("L1_MFleet")) <= 1e-12 * req("L1_MFleet") and abs(eng.get_name("L1_LReqFleet_Lo") - req("L1_MFleet_Hi")) <= 1e-12 * req("L1_MFleet_Hi")
    for n in ("L1_LPrice", "L1_LDemote", "L1_LTotal", "L1_LReqFleet"):
        rr = int(re.sub(r"[A-Z]+", "", eng.names[n].rsplit("!", 1)[1].replace("$", "")))
        assert eng.get("L1", f"E{rr}") <= eng.get("L1", f"D{rr}") <= eng.get("L1", f"F{rr}"), n
        if n == "L1_LTotal": assert eng.get("L1", f"M{rr}") == 1 and eng.get("L1", f"P{rr}") == "落在 0.3–1.0 區間內"
        elif n == "L1_LReqFleet": assert abs(eng.get("L1", f"M{rr}") - eng.get_name("L1_LTotal")) < 1e-12 and eng.get("L1", f"P{rr}").startswith("恆等式讀法：未回本（L_total 0.66 對所需 L 0.76）")      # v6.3 K1：所需 L 0.66 → 0.53，判讀由「未回本」回到「回本」（L_total 0.6426 ≥ 0.5304）；v6.2：0.55 → 0.66，由「回本」變「未回本」
        else: assert eng.get("L1", f"P{rr}") == "無外部對照"
    # 既有 L1（v5.34 六個）與 IF_ 不變
    for n, v in (("L1_MAPI", 0.813024), ("L1_MSub", 6.146459), ("L1_MSeat", 2.634197), ("L1_MixFactorAPI", 0.813024), ("L1_MImplied", 2.513547), ("L1_MFleet", 0.61609), ("IF_PriceRef_Sol", 1.607111)):  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-6, (n, eng.get_name(n), v)
    assert abs(eng.get_name("L1_TokPerPromptClose") - 30749.840443) < 5e-3
    import openpyxl
    wb = openpyxl.load_workbook(model, read_only=True)
    cap = {wb["Cap_In"][f"A{r}"].value: r for r in range(182, 275) if isinstance(wb["Cap_In"][f"A{r}"].value, str)}
    row = lambda p: next(r for lab, r in cap.items() if re.sub(r"^【[^】]*】", "", lab).startswith(p))   # v10.1 4-1：歷史說明列加「【各版演進記錄…】」前綴
    i0 = row("I. L 拆分")
    assert row("H10. m 季度序列") < row("自我檢查：2025 欄") < i0 < row("讀法")                                   # I 節在 H10 之後、讀法列之前
    for lab, cols in (("m_API", (0.813024, 0.294994, 0.340278, 0.348339)), ("m_消費訂閱", (6.146459, 5.743864, 5.398635, 5.568844)), ("m_商用席次", (2.634197, 3.555726, 4.557290, 8.043885)),
                      ("m_整體", (2.513547, 1.192339, 1.343201, 1.431699)), ("廣告營收", (0, 0, 0.5, 1.0)), ("2026 消費訂閱占", (0.75, 0.65, 0.65, 0.65))):   # v14.0 4-3B Q1：Cap_In 第 204 列 L_price（I 節；顯示用）依工作單刪除，不再斷言
        for c, v in zip("CDEF", cols):
            if lab == "2026 消費訂閱占" and c == "C":      # v14.1 R5：Cap_In C200（2025 年度欄，無人讀取）已清空
                assert eng.get("Cap_In", f"C{row(lab)}") == "", (lab, c)
                continue
            assert abs(eng.get("Cap_In", f"{c}{row(lab)}") - v) < 5e-6, (lab, c, eng.get("Cap_In", f"{c}{row(lab)}"), v)
    r = row("m 分子營收")
    assert all(eng.get("Cap_In", f"C{row(x)}") == "" for x in ("m 分子營收", "消費訂閱營收", "商用席次營收", "API 營收"))      # v14.1 R5：C187、C191–C193 已清空，三分之和改只斷言 D–F 欄
    for c in "DEF":                                                                                                # J23 (1)：三分之和＝m 分子營收
        assert abs(eng.get("Cap_In", f"{c}{row('消費訂閱營收')}") + eng.get("Cap_In", f"{c}{row('商用席次營收')}") + eng.get("Cap_In", f"{c}{row('API 營收')}") - eng.get("Cap_In", f"{c}{r}")) < 1e-9
    assert abs(eng.get("Cap_In", f"E{row('m_fleet')}") - 0.279813) < 5e-6 and eng.get("Cap_In", f"C{row('自我檢查：2025 欄')}") == "一致"
    assert abs(eng.get("Cap_In", f"C{row('壽命 T')}") - 6) < 1e-12 and abs(eng.get("Cap_In", f"D{row('降級後價值比')}") - rho_lo) < 1e-12
    assert eng.get("Cap_In", f"C{row('判讀：L_total 對 Gov_Map')}") == "區間內（0.3–1.0）" and eng.get("Cap_In", f"E{row('判讀：L_total 對 Gov_Map')}") == "區間外（0.3–1.0）"
    assert eng.get("Cap_In", f"C{row('判讀：L_total 區間 對 所需 L 區間')}").startswith(("未回本", "未定", "回本")) and eng.get("Cap_In", f"D{row('對照（字面讀法')}").startswith("未回本")      # v15.3 D1：第 242 列改三態（區間對區間，恆等式讀法）；第 243 列退為字面讀法對照
    assert abs(eng.get("Cap_In", f"C{row('回本所需 L（2025 機隊口徑；m＝L1_MAPI')}") - 1.542863) < 5e-6


def test_v536_spend_route_kappa_price(model, lo):
    """v5.36（工作單 B1–B6）：支出路線改 SRC_DEM_004（7.5）、計價倍數 1.3、κ 納入服務 GW、GapPrompt 為有效倍數、缺口恆等式與 L1 價格列。
    錨點（工作單，相對容差 1e-3）；IF_ 名稱不變由逐格比較（報告表 2）負責。"""
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("AL_Kappa") == 1.0
    anchors = {"AL_ServeGWSpend": 0.8981, "L1_ScaleServe": 5.97049, "L1_MFleet": 0.61609, "L1_TokPerPromptClose": 30749.840443, "L1_TokCeiling": 1.89739e+10,      # v6.2（2-1-b／c）：Hopper Astra 排除、Alloc 重新正規化；v6.1 為 4.7498、0.5369、23406.6、1.52935e10、0.5498、1.3011、1.0527、6.1801  # v15.2 B2／B3 預期變動：期望值依重算結果更新
               "L1_LReqFleet": 2.03604, "L1_GapSpendBasis": 0.85, "L1_GapPrompt": 1.299156, "L1_GapISL": 1.0, "L1_GapUtil": 1.7217,      # v7.0（2-2-b）：1.4634 → 1.7217  # v15.2 B2／B3 預期變動：期望值依重算結果更新
               "L1_PriceRealFleet": 0.837489, "L1_PriceRealDemand": 4.92825, "L1_PriceReqBE": 2.585513, "L1_PriceRho": 1.165, "L1_ScaleServe2000": 7.756596}
    for n, v in anchors.items():
        assert abs(eng.get_name(n) - v) <= 1e-3 * abs(v), (n, eng.get_name(n), v)
    assert abs(eng.get_name("L1_PriceReqBE_Lo") - 1.555283) <= 1e-3 and abs(eng.get_name("L1_PriceReqBE_Hi") - 4.295464) <= 2e-3      # v15.3 E1／E2：L 改變使所需價格 1.4677／4.9859 → 1.5553／4.2955      # v6.3 K1：機隊口徑單價（0.498、1.692 → 0.4026、1.3676）  # v15.2 B2／B3 預期變動：期望值依重算結果更新
    assert abs(eng.get_name("L1_PriceRho_Lo") - 0.832) <= 1e-3 and abs(eng.get_name("L1_PriceRho_Hi") - 1.355) <= 1e-3
    assert abs(eng.get_name("SRC_DEM_073") - 7.5) < 1e-12 and eng.get_name("SRC_DEM_004_Lo") == 7.5 and eng.get_name("SRC_DEM_004_Hi") == 8.8
    for n in ("AL_Kappa", "L1_ScaleServe2000", "L1_PriceRealFleet", "L1_PriceRealDemand", "L1_PriceReqBE", "L1_PriceRho"):
        assert n + "_Lo" in eng.names and n + "_Hi" in eng.names, n
    # 缺口恆等式與 Checks M5（基準欄）
    assert eng.get("Checks", "D132") == 0



def _contract_names(eng):
    return [n for n in eng.names if n.startswith(("IF_", "IFW_")) and "!" in eng.names[n]]


def test_v600_audit_fix1_expected_values(model, lo):
    """v6.0（稽核修正1：D7、D8、D11）基準期望值。錨點為 LibreOffice 重算值（相對容差 1e-4）；工作單預期變動：
    FullCost_Luna(Hopper) +46%、FullCostDefault_Luna +94%、FullCostDefault_Sol(VR200) +21%、Astra 不變；付費產能比約 0.712、m 下限約 0.647；IF_*_Life ÷ 舊值 0.486–0.81。"""
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("GOV_Warnings") == 281 and eng.get_name("GOV_Info") == 182      # v15.2：舊 SLO 視圖 Info 181 → 182（I3 +1、I1 +1、K5 −1：B2／B3 使 L1 外部對照差距旗標列數與 Gov_Map 區間內外狀態改變）；  # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：舊 SLO 視圖 Info 184 → 181（L1 外部對照換算後 P 欄「差距 >20%」旗標減少）      # v13.0 K2：同上，Warnings 282 → 283（RG2）； v13.0 K3：Info 181 → 182（同上）； v12.0：Info 179 → 181（同上）； v8.0：Info 174 → 177（見 343 行）；v7.0：175 → 174（Calib C68 倒推，Load_Bearing 55）；v6.2：Info 172 → 175（Load_Bearing +3，模型規模倍數三列）      # v13.1 D15 B 段：Warnings 減 2（SRC_HW_067／068 有了第二來源，W1 −2）、Info 加 2（DB_Evidence 新增 2 筆『待判定』）；預期變動，非放寬
    rel = lambda got, want, tol=1e-4: abs(got - want) <= tol * abs(want)
    # D11：回本溢價分母＝付費 token（Hopper 基準欄＝第 2 欄、VR200 基準欄＝第 11 欄）
    old = {("IF_FullCost_Luna", 1): 0.184810505721705, ("IF_FullCostDefault_Luna", 1): 0.198387926107027, ("IF_FullCostDefault_Sol", 10): 0.107287815966711}
    new = {("IF_FullCost_Luna", 1): 0.319833598024594, ("IF_FullCostDefault_Luna", 1): 0.479028244992465, ("IF_FullCostDefault_Sol", 10): 0.130225106139314}      # v6.2：Hopper 欄 Luna 0.337227 → 0.259014、Default 0.472583 → 0.920305（Hopper 機隊排除 Astra，Luna 回本溢價的分母改變）
    for (n, k), want in new.items():
        assert rel(eng.get_name(n)[k], want), (n, k, eng.get_name(n)[k], want)
        assert 1.2 <= eng.get_name(n)[k] / old[(n, k)] <= 5.0      # v6.2：上限放寬到 5（FullCostDefault_Luna 0.9203/0.1984＝4.64，Astra 排除使分母改變）；v6.1：D6/D10/D13 使 Luna 回本溢價再升（0.4726/0.1984＝2.38）
    assert rel(eng.get_name("IF_AmortBU_Luna")[1], 0.112376489836008) and rel(eng.get_name("IF_AmortBU_Sol")[1], 0.277422047849995)      # v6.2（v6.1：0.12977、0.320361）
    # D7-1／D7-2：付費產能比、m 下限、_Prod 營收 ÷ _Prod token＝單價（Checks Z1＝0）
    assert rel(eng.get_name("AL_ProdRatioPaid"), 0.70617338496457) and 0.69 < eng.get_name("AL_ProdRatioPaid") < 0.71      # v6.2（v6.1：0.7155）
    assert rel(eng.get("Cap_In", "C121"), 0.506739304970016)      # v6.3 K1：m 下限 0.352267 → 0.435913（機隊口徑單價 AL_PriceFleet）
    assert rel(eng.get("Cap_In", "C115"), eng.get_name("AL_ProdRatioPaid"))
    assert rel(eng.get_name("L1_TokCeiling"), 18973895736.7806)
    col = eng.get("Checks", "A1:A200")
    z1 = [i + 1 for i, r in enumerate(col) if r[0] == "Z1"]
    assert len(z1) == 1 and eng.get("Checks", f"D{z1[0]}") == 0
    for t, tk in enumerate(TIERS):
        tok, rev, front = eng.get_name(f"IFW_TokGW_{tk}_Prod"), eng.get_name(f"IFW_RevGW_{tk}_Prod"), eng.get_name(f"IFW_RevGWFront_{tk}_Prod")
        px, fpx = eng.get_name("B4_EffRef")[t], eng.get_name("B4_FrontRef")[t]
        for k in range(15):
            if not _num(tok[k]):                                                  # v6.2：Hopper × Astra 為文字旗標（TTFT 不可達），營收、前緣營收同為文字
                assert isinstance(tok[k], str) and tok[k] == rev[k] == front[k], (tk, k, tok[k], rev[k], front[k]); continue
            assert abs(rev[k] * 1e9 / tok[k] - px) <= 1e-9 * px and abs(front[k] * 1e9 / tok[k] - fpx) <= 1e-9 * fpx, (tk, k)
            assert tok[k] <= eng.get_name(f"IFW_TokGW_{tk}_Util")[k] <= eng.get_name(f"IFW_TokGW_{tk}_100")[k]
    # D7-3：IF_*_Life 為 IFW_*_Life 的別名；比舊值 0.486–0.81
    for n, w in (("IF_RevGW_Luna", "IFW_RevGW_Luna"), ("IF_RevGW_Sol", "IFW_RevGW_Sol"), ("IF_RevGW_Astra", "IFW_RevGW_Astra"), ("IF_RevGWFleet", "IFW_RevGWFleet")):
        assert eng.get_name(n + "_Life") == eng.get_name(w + "_Life")
    assert _num(eng.get_name("IF_RevGW_Astra_Life")[1]) and rel(eng.get_name("IF_RevGW_Sol_Life")[10] / 272.216583526111, 0.800085, 1e-3)      # v6.2：Hopper × Astra 為文字旗標（v6.1 的 Astra 比值 0.399361 不再適用）
    # v6.2：基準下 Hopper 的 Astra 層 TTFT 不可達——Fleet_1GW D 節 Astra 旗標在 Hopper 三欄為 0、排除層級為「Astra」，其餘全部可達（旗標 1、排除「無」）
    rc = eng.get("Fleet_1GW", "C38:Q40"); ex = eng.get("Fleet_1GW", "C43:Q43")
    assert all(v == 1 for r in rc for v in r)      # v9.0 D9：快取命中進產能後 Hopper × Astra 的 TTFT 可達，旗標全 1、排除層級全「無」；v6.2 的不可達結構改由 B4_CacheHit＝0 情境驗證（v602 測試）
    assert all(v == "無" for v in ex[0])


def test_v600_audit_fix1_slo_text(model, lo):
    """v6.0 D8-5：Serving!C18＝0.7 與 Train_In!E31＝100 兩個情境——(1) 沒有任何 IF_／IFW_ 名稱因不可達而由非零變成數值 0；
    (2) 仍可達的層級（Luna、Sol）照常輸出數值；(3) IF_AllocQ1 隨 E31 單調（數值或「SLO 不可達」文字），不再出現 0.332 → 0.459 → 0.612 → 0.225。
    判定錯誤值只計 # 開頭（文字不算）。"""
    base = _vo(lo, {})
    names = _contract_names(base)
    for sid, inputs in (("c18_07", {"Serving!C18": 0.7}), ("e31_100", {"Train_In!E31": 100})):
        eng = _vo(lo, inputs)
        zero_from_nonzero = []
        for n in names:
            b, v = base.get_name(n), eng.get_name(n)
            b = b if isinstance(b, list) else [b]; v = v if isinstance(v, list) else [v]
            for i, (x, y) in enumerate(zip(b, v)):
                if isinstance(x, (int, float)) and x != 0 and isinstance(y, (int, float)) and not isinstance(y, bool) and y == 0:
                    zero_from_nonzero.append((n, i))
        assert not zero_from_nonzero, (sid, zero_from_nonzero[:10])
        errs = [k for k, v in eng.evaluate_all().items() if isinstance(v, str) and v.startswith("#")]
        assert not errs, (sid, errs[:5])
        for n in ("IF_TokGW_Luna", "IF_TokGW_Sol", "IF_CostDec_Luna", "IF_CostDec_Sol", "IF_RevGW_Luna", "IF_RevGW_Sol", "IF_RevGWFleet"):
            assert all(isinstance(x, (int, float)) for x in eng.get_name(n)), (sid, n)           # 仍可達的層級照常輸出數值（Fleet 排除不可達層級後重新正規化）
    c18 = _vo(lo, {"Serving!C18": 0.7})
    assert any(isinstance(x, str) for x in c18.get_name("IF_TokGW_Astra")) and any(v != "無" for v in c18.get("Fleet_1GW", "C43:Q43")[0])      # 有層級被排除，且列出排除層級
    q1 = []
    for e in (20, 80, 100, 150):
        v = _vo(lo, {"Train_In!E31": e}).get_name("IF_AllocQ1")
        q1.append(v)
    nums = [v for v in q1 if isinstance(v, (int, float))]
    assert nums == sorted(nums) and q1[0] < q1[1], q1                                              # v8.0 L3：0.211 → 0.363 → 文字 → 文字（研發世代組合 Hopper 0.6／GB200 0.38／GB300 0.02：E31＝100 時加權世代全不可達，無可重新正規化者）
    assert all(v in ("SLO 不可達", "整代不可達") for v in q1[2:]), q1                                # 不再回落到數值（v7.0：0.332 → 0.459 → 0.612 → 文字）


# ── v6.2 2-1（工作單 docs/workorders/20261016_稽核修正2.md r0）：D1(c) 模型規模倍數、TTFT 進可達判斷、Alloc 重新正規化 ──
def test_v602_model_scale_ttft_alloc(model, lo):
    """v6.2：(a) 基準 ARCH_ScaleGen＝1（1×5，Rubin Ultra 固定 1）；(b) 基準下 Hopper × Astra TTFT 不達標——第 77 列「否」、第 90、93 列「TTFT 不可達」、
    IF_TokGW_Astra Hopper 三欄為文字（不是 0），其餘 12 欄與各層級不變；Checks B27＝1；(c) Alloc：Hopper 欄「未服務需求占比」＝Astra 的付費組合權重 0.15，各世代仍可服務，
    AL_ServeGW 0.166128、L1_MFleet 0.471739（v6.3 K1）；(d) 情境 d1_model_scale（v6.3 J1 r1：0.8／0.55／1.0／1.4）下 Hopper Astra 仍 TTFT 不可達，其餘值為 LibreOffice 重算值。"""
    eng = _vo(lo, {})
    assert eng.get_name("ARCH_ScaleGen") == [1, 1, 1, 1, 1] and eng.get_name("ARCH_ScaleGen_Lo") == [0.5, 0.3, 1, 1, 1] and eng.get_name("ARCH_ScaleGen_Hi") == [1.3, 1.0, 1, 2.5, 1]      # v6.3 J1 r1（2Q 報告 Q2）：Lo 0.1／0.3 → 0.5／0.3，Hi 0.5／1.0／—／4.4 → 1.3／1.0／—／2.5
    assert eng.get_name("GOV_Errors") == 0
    # v9.0 D9：快取命中進產能（prefill 只計新鮮輸入）後，基準下 Hopper × Astra 的 TTFT 達標（約 2.7 秒）：第 77 列「是」、IF_TokGW_Astra 全 15 欄為數值、Checks B27＝0、未服務占比 0；
    # v6.2 的「TTFT 不可達」結構（文字旗標一路傳遞、Alloc 重新正規化）改由 B4_CacheHit＝0 情境驗證（等同 v8.0 的產能）
    assert eng.get("Perf", "E77") == "是" and eng.get("Perf", "E90") != "TTFT 不可達" and _num(eng.get("Perf", "E93")) and _num(eng.get("Perf_Prod", "E93"))
    assert all(_num(x) and x > 0 for x in eng.get_name("IF_TokGW_Astra"))
    for t in ("Luna", "Sol"):
        assert all(_num(x) and x > 0 for x in eng.get_name(f"IF_TokGW_{t}"))
    assert eng.get("Checks", "B27") == 0
    assert [round(x, 9) for x in eng.get_name("AL_UnservedPaid")] == [0, 0, 0, 0] and eng.get_name("AL_GenOK") == [1, 1, 1, 1]
    e0 = _vo(lo, {"B4_CacheHit": 0})
    assert e0.get_name("GOV_Errors") == 1      # B4_CacheHit＝0 在其藍字區間（Gov_Map 低／高）之外：Checks E10＝1（v8.0 同）；其餘錯誤 0
    assert e0.get("Perf", "E77") == "否" and e0.get("Perf", "E90") == "TTFT 不可達" and e0.get("Perf", "E93") == "TTFT 不可達" and e0.get("Perf_Prod", "E93") == "TTFT 不可達"
    tok = e0.get_name("IF_TokGW_Astra")
    assert tok[:3] == ["TTFT 不可達"] * 3 and all(_num(x) and x > 0 for x in tok[3:])           # D8：文字＝不可用，不是 0
    assert e0.get("Checks", "B27") == 1
    assert [round(x, 9) for x in e0.get_name("AL_UnservedPaid")] == [0.15, 0, 0, 0] and e0.get_name("AL_GenOK") == [1, 1, 1, 1]
    for n, v in (("AL_ServeGW", 0.150423), ("L1_MFleet", 0.61609), ("L1_ScaleServe", 5.97049)):  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(eng.get_name(n) - v) < 5e-6, (n, eng.get_name(n), v)
    sc = _vo(lo, {"ARCH_ScaleGen[1]": 0.8, "ARCH_ScaleGen[2]": 0.55, "ARCH_ScaleGen[3]": 1.0, "ARCH_ScaleGen[4]": 1.4, "B4_CacheHit": 0})      # v9.0：加 B4_CacheHit＝0 以維持 v6.3 的產能口徑（Hopper Astra 不可達）；v6.3 J1 r1（2Q 報告 Q2）：Hopper 0.8 仍不足以讓 Astra 達 TTFT
    assert sc.get_name("GOV_Errors") == 1 and sc.get_name("IF_TokGW_Astra")[0] == "TTFT 不可達" and [round(x, 9) for x in sc.get_name("AL_UnservedPaid")] == [0.15, 0, 0, 0]
    rel = lambda got, want: abs(got - want) <= 1e-5 * abs(want)
    for n, k, v in (("IF_TokGW_Luna", 1, 7.80572e+10), ("IF_TokGW_Sol", 1, 2.40211e+10), ("IF_TokGW_Astra", 3, 3.74048e+10), ("IF_TokGW_Luna", 10, 6.02458e+11)):
        assert rel(sc.get_name(n)[k], v), (n, k, sc.get_name(n)[k], v)
    for n, v in (("L1_TokMW_Gen_ratio_GB200", 7.764317), ("L1_TokMW_Gen_ratio_GB300", 0.812802), ("L1_TokMW_Gen_ratio_VR200", 1.18078), ("L1_MFleet", 0.434682), ("IF_AllocQ1", 0.137277985), ("L1_ScaleServe", 9.197795)):      # v12.0 H2：IF_AllocQ1 0.134629 → 0.138378（GB200 CAL_BatchEtaD 3.04 → 2.36）； v11.0 G2：IF_AllocQ1 0.162347 → 0.134629（GB200 CAL_BatchEtaD 3.04）
        got = sc.get_name(n)
        assert rel(got[0] if isinstance(got, list) else got, v), (n, got, v)


# ── v6.3 2-1b（工作單 docs/workorders/20261016_稽核修正2.md r1 第 2b 節）：K1 機隊口徑單價、K2 整代不可達、K3 TTFT 進 decode 成本列、J1 r1 ──
def test_v603_fleet_price_k2_k3(model, lo):
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0
    # K1：機隊口徑單價（可達層級重新正規化、以付費 token 加權）；Cap_In K 節第 1 欄同值，其餘三欄為各世代單價
    pf, pg, k = eng.get_name("AL_PriceFleet"), eng.get_name("AL_PriceGen"), eng.get_name("B4_PriceFleet")
    assert abs(pf - 1.960675556) < 5e-8 and all(abs(x - 1.960675556) < 5e-8 for x in pg)      # v9.0 D9：Hopper × Astra 可達，Hopper 欄不再排除 Astra（v6.3：0.888637909），機隊口徑單價＝各世代單價 1.960675556（1.607111 × κ 1.22）
    assert k[0] == eng.get_name("AL_PriceFleet25") and len(k) == 4      # v8.0 L1：Cap_In K 節 C 欄改為 2025 年度機隊口徑單價
    assert abs(eng.get_name("L1_MFleet") * eng.get_name("AL_PriceFleet25") - eng.get_name("L1_PriceRealFleet")) < 1e-12      # 實收單價＝m × 機隊口徑單價＝營收 ÷ 機隊付費 token（與 v6.2 值 0.924927 相同）
    assert abs(eng.get_name("L1_PriceRealFleet") - 0.837489) < 5e-7
    # K3：Hopper × Astra 的 decode 成本列在 B4_CacheHit＝0（v8.0 產能口徑）為文字（不可達），其餘 12 欄為數值；v9.0 基準（快取進產能）全 15 欄為數值
    e0 = _vo(lo, {"B4_CacheHit": 0})
    for n in ("IF_CostDec_Astra", "IF_CostDecAcct_Astra", "IF_AmortTD_Astra"):
        v = eng.get_name(n)
        assert all(_num(x) and x > 0 for x in v), n
        v = e0.get_name(n)
        assert all(isinstance(x, str) for x in v[:3]) and all(_num(x) and x > 0 for x in v[3:]), n
    # K2：整代不可達的文字傳遞（f_registry：Hopper 三層全不可達，2025 組合中 Hopper 占 0.6）
    f = _vo(lo, {"Tech_Registry!O11": 1, "Tech_Registry!O12": 1, "Tech_Registry!O13": 1})
    errs = [kk for kk, v in f.evaluate_all().items() if isinstance(v, str) and v.startswith("#")]
    assert not errs, errs[:10]
    for n in ("IF_AllocQ1", "IF_AllocQ2", "IF_AllocServeGW", "AL_PriceFleet", "AL_ServeGW"):
        assert f.get_name(n) == "整代不可達", n
    for n in ("L1_MFleet", "L1_TokCeiling", "L1_ScaleServe", "L1_TokPerPromptClose", "L1_GapPrompt", "AL_UnavailTxt"):
        assert f.get_name(n) == "整代不可達", n
    assert f.get_name("L1_PriceRealFleet") == "m 非數字（本情境）" and eng.get_name("AL_UnavailTxt") == "SLO 不可達"
    # C18＝0.7（各世代皆至少有一層可達）：機隊口徑單價為數值
    b = _vo(lo, {"Serving!C18": 0.7})
    assert abs(b.get_name("AL_PriceFleet") - 1.672710853) < 5e-8


# ── v7.0 2-2（工作單 docs/workorders/20261016_稽核修正2.md r0 第 3 節；世代價格 B 段 B-1／B-2、2-2-b 遺留）──
def test_v700_generation_price_thresholds(model, lo):
    """B-1：CAP_GenGap_*（基準／低／高）；B-2：L1_GenPxThr_Rev_*／_Pay_*（基準與情境 d1_model_scale）；H3 排序 E ≤ D ≤ F；門檻不含價格。"""
    eng = _vo(lo, {})
    assert eng.get_name("GOV_Errors") == 0 and eng.get_name("CHK_L1Order") == 0
    for g, (b, l, h) in {"GB200": (1.88, 1.88, 2.17), "GB300": (0.41, 0.41, 0.54), "VR200": (1.18, 1.11, 1.24)}.items():
        assert (eng.get_name(f"CAP_GenGap_{g}"), eng.get_name(f"CAP_GenGap_{g}_Lo"), eng.get_name(f"CAP_GenGap_{g}_Hi")) == (b, l, h), g
    want = {   # 名稱: (D 基準, E, F)，LibreOffice 重算值（v6.3 的 q 與持有成本；固定模型口徑）
        "Rev_GB200": (-0.615667, -0.615667, -0.563275), "Rev_GB300": (-0.464437, -0.464437, -0.377561), "Rev_VR200": (-0.327498, -0.47495, 0.13872),
        "Pay_GB200": (-0.634508, -0.634508, -0.581885), "Pay_GB300": (-0.107113, -0.107113, -0.082424), "Pay_VR200": (-0.258025, -0.423458, 0.264169)}
    for k, (d, e, f) in want.items():
        got = (eng.get_name(f"L1_GenPxThr_{k}"), eng.get_name(f"L1_GenPxThr_{k}_Lo"), eng.get_name(f"L1_GenPxThr_{k}_Hi"))
        assert all(abs(x - y) < 5e-6 for x, y in zip(got, (d, e, f))), (k, got)
        assert got[1] <= got[0] <= got[2], (k, got)
    # 定義核對：收入門檻 ＝ q^(−1/Δ) − 1；回本門檻 ＝ (HoldEcon_g ÷ HoldEcon_prev ÷ q)^(1/Δ) − 1
    prev = {"GB200": "Hopper", "GB300": "GB200", "VR200": "GB300"}
    for g in prev:
        q, dd = eng.get_name(f"L1_TokMW_Gen_ratio_{g}"), eng.get_name(f"CAP_GenGap_{g}")
        assert abs(eng.get_name(f"L1_GenPxThr_Rev_{g}") - (q ** (-1 / dd) - 1)) < 1e-12
        hc = eng.get_name(f"L1_HoldEconMW_{g}") / eng.get_name(f"L1_HoldEconMW_{prev[g]}")
        assert abs(eng.get_name(f"L1_GenPxThr_Pay_{g}") - ((hc / q) ** (1 / dd) - 1)) < 1e-12
    # 情境 d1_model_scale（ARCH_ScaleGen 0.8／0.55／1.0／1.4）：模型變大時的門檻
    sc = _vo(lo, {"ARCH_ScaleGen[1]": 0.8, "ARCH_ScaleGen[2]": 0.55, "ARCH_ScaleGen[3]": 1.0, "ARCH_ScaleGen[4]": 1.4})
    want_sc = {"Rev_GB200": (-0.657763, -0.657763, -0.605034), "Rev_GB300": (0.797447, 0.56081, 0.797447), "Rev_VR200": (-0.142878, -0.339663, 0.47674),
               "Pay_GB200": (-0.674541, -0.674541, -0.621865), "Pay_GB300": (1.996692, 1.300885, 1.996692), "Pay_VR200": (-0.054332, -0.274904, 0.639428)}
    for k, (d, e, f) in want_sc.items():
        got = (sc.get_name(f"L1_GenPxThr_{k}"), sc.get_name(f"L1_GenPxThr_{k}_Lo"), sc.get_name(f"L1_GenPxThr_{k}_Hi"))
        assert all(abs(x - y) < 5e-6 for x, y in zip(got, (d, e, f))), (k, got)
        assert got[1] <= got[0] <= got[2], (k, got)
    assert sc.get_name("GOV_Errors") == 0
    # f_registry（Hopper 整代不可達）情境：無錯誤值
    f = _vo(lo, {"Tech_Registry!O11": 1, "Tech_Registry!O12": 1, "Tech_Registry!O13": 1})
    assert not [k for k, v in f.evaluate_all().items() if isinstance(v, str) and v.startswith("#")]


def test_v700_leftovers(model, lo):
    """2-2-b：L1_FleetProdRatio／L1_FleetMargin／Checks K4 讀重解值；L1_GapUtil 乘生產折減；Interface A231 標題；J3／J4／J5。"""
    eng = _vo(lo, {})
    rev_p, rev_u = eng.get_name("IFW_RevGWFleet_Prod")[10], eng.get_name("IFW_RevGWFleet_Util")[10]
    assert abs(eng.get_name("L1_FleetProdRatio") - rev_p / rev_u) < 1e-12 and abs(eng.get_name("L1_FleetProdRatio") - 0.772761) < 5e-6
    assert abs(eng.get_name("L1_FleetMargin") - 3.554764) < 5e-6 and abs(eng.get_name("L1_FleetBreakeven") - 0.130432) < 5e-6
    assert eng.get("Checks", "D121") == 0 and "重解" in eng.get("Checks", "B121")
    assert abs(eng.get_name("L1_GapUtil") - 1.721664) < 5e-6 and abs(eng.get_name("L1_GapProduct") - 1.901204) < 5e-6
    a231 = eng.get("Interface", "A231")
    assert "重解 SLO" in a231 and "_Prod＝_Util × CTL_ProdDerate" not in a231
    # K4 在 CTL_ProdDerate＝0.7 情境仍成立（恆等式）
    p7 = _vo(lo, {"CTL_ProdDerate": 0.7})
    assert p7.get("Checks", "D121") == 0 and abs(p7.get_name("L1_FleetProdRatio") - p7.get_name("IFW_RevGWFleet_Prod")[10] / p7.get_name("IFW_RevGWFleet_Util")[10]) < 1e-12
    assert abs(p7.get_name("L1_GapUtil") - p7.get_name("IF_Util") / (p7.get_name("AL_UtilActual") * 0.7)) < 1e-12
    # J3：Serving C18 基準 1.0
    assert eng.get("Serving", "C18") == 1.0 and "J3" in eng.get("Serving", "F18")
    # J4：Calib C68 數值不變，標記改為倒推
    assert eng.get("Calib", "C68") == 1.5 and "倒推" in eng.get("Calib", "J68") and "J4" in eng.get("Calib", "J68")
    # J5：Alloc 敏感度表『全 GB200』『全 VR200』為純世代（主列）；檢查副本（輸入全為基準）仍讀基準組合
    rows = {}
    for r in range(1, 400):
        a = eng.get("Alloc", f"A{r}")
        if isinstance(a, str) and (a in ("服務世代組合：全 GB200", "服務世代組合：全 VR200") or a.startswith("檢查：服務世代組合：全")):
            rows[a] = r
    assert len(rows) == 4, rows
    mix = lambda r: [eng.get("Alloc", f"{c}{r}") for c in "IJKL"]
    assert mix(rows["服務世代組合：全 GB200"]) == [0, 1, 0, 0] and mix(rows["服務世代組合：全 VR200"]) == [0, 0, 0, 1]
    base_mix = eng.get_name("AL_MixGen")[:4]
    for k, r in rows.items():
        if k.startswith("檢查："): assert mix(r) == base_mix, (k, mix(r))


# ── v8.0 2-3（工作單 docs/workorders/20261016_稽核修正2.md 4r1 L1–L5）：2025 年度口徑、研發世代組合、2025 機隊回本、服務 GW 支出路線 ──
def test_v800_audit_fix2_3(model, lo):
    """L1：m 用 2025 年度層級單價（CAP_Px25_*、AL_PriceFleet25）；L2：2025 年度模型規模倍數（情境）；L3：研發世代組合（AL_RDMix*）加權；L4：所需 L 讀 2025 機隊損益兩平；L5：服務 GW 主口徑＝支出路線。
    基準期望值為 LibreOffice 重算值；恆等式以具名範圍驗算（1e-12）。"""
    eng = _vo(lo, {})
    n = eng.get_name
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    assert n("GOV_Errors") == 0 and n("CHK_RDMixSum") == 0 and n("AL_RDShareExcl") == 0
    # L1：2025 混合單價與機隊口徑單價
    assert abs(n("CAP_Price25Mix") - 1.35936) < 5e-6 and abs(n("AL_PriceFleet25") - 1.35936) < 5e-6 and abs(n("AL_PriceFleet") - 1.960676) < 5e-6      # 2026 快照仍保留
    assert abs(n("L1_MFleet") - 0.61609) < 5e-6 and abs(n("L1_MFleet_Px2026") - 0.427143) < 5e-6
    assert abs(n("L1_MFleet") * n("AL_PriceFleet25") - n("L1_MFleet_Px2026") * n("AL_PriceFleet")) < 1e-9      # m × 單價＝實收單價，與單價水準無關
    assert abs(n("L1_PriceRealFleet") - n("L1_MFleet") * n("AL_PriceFleet25")) < 1e-12
    for nm in ("L1_MFleet", "L1_MFleet_Px2026"):
        assert num(n(nm)) and num(n(nm + "_Lo")) and num(n(nm + "_Hi")) and n(nm + "_Lo") <= n(nm) <= n(nm + "_Hi"), nm
    # L3：研發世代組合
    mix = [n("AL_RDMixHopper"), n("AL_RDMixGB200"), n("AL_RDMixGB300"), n("AL_RDMixVR200")]
    assert mix == [0.6, 0.38, 0.02, 0] and abs(sum(mix) - 1) < 1e-12
    assert abs(n("AL_RDGW") - 0.201160) < 5e-6 and abs(n("IF_AllocRDGW") - n("AL_RDGW")) < 1e-15      # v12.0 H2：0.197258 → 0.202947（GB200 CAL_BatchEtaD 3.04 → 2.36）； v11.0 G2：0.240199 → 0.197258
    assert abs(n("AL_RefGWyr") - 0.044455) < 5e-6 and abs(n("AL_FamGWyr") - 0.112250) < 5e-6      # v12.0 H2：0.0432504／0.110757 → 0.0450046／0.112938
    # L5：服務 GW 支出路線
    assert abs(n("IF_AllocServeGW") - n("AL_ServeGWSpend")) < 1e-15 and abs(n("IF_AllocServeGW") - 0.898096) < 5e-6
    assert abs(n("IF_AllocServeGW_Tok") - n("AL_ServeGW")) < 1e-15 and abs(n("IF_AllocServeGW_Tok") - 0.150423) < 5e-6
    assert abs(n("IF_AllocQ1") - n("AL_RDGW") / (n("AL_RDGW") + n("AL_ServeGWSpend"))) < 1e-12 and abs(n("IF_AllocQ1") - 0.182997) < 5e-6      # v12.0 H2：0.180086 → 0.184322
    assert abs(n("IF_AllocQ2") - 0.183654) < 5e-6      # v12.0 H2：0.180735 → 0.184983
    assert abs(n("AL_Q1_Tok") - n("AL_RDGW") / (n("AL_RDGW") + n("AL_ServeGW"))) < 1e-12      # token 路線保留作對照
    assert abs(n("L1_ScaleServe") - 5.97049) < 5e-6      # 兩路線的未解釋差距（數值不變）
    # L4：2025 機隊損益兩平與所需 L
    assert abs(n("L1_FleetBreakeven2025") - 0.639736) < 5e-6 and abs(n("L1_FleetBreakeven") - 0.130432) < 5e-6      # VR200 截面維持
    req = n("L1_FleetBreakeven2025") / (n("IF_Util") * n("CTL_ProdDerate") * n("L1_MFleet"))
    assert abs(n("L1_LReqFleet") - req) <= 1e-12 * req and abs(n("L1_LReqFleet") - 2.03604) < 5e-6
    assert abs(n("L1_LReqFleet_VR200") - 0.598745) < 5e-6 and abs(n("L1_LReqFleet_Id") - 0.756110) < 5e-6      # 舊讀法與恆等式讀法並列
    assert num(n("L1_LTotal")) and n("L1_LTotal") < n("L1_LReqFleet") and n("L1_LTotal") < n("L1_LReqFleet_Id")      # 兩種讀法皆未回本；舊 VR200 讀法回本（0.530 < 0.643）
    assert n("L1_LReqFleet_VR200") < n("L1_LTotal")
    assert abs(n("L1_RevGWFleet_OAI2025") - 12.65255) < 5e-6      # Checks B43：Hopper 占比改讀 AL_MixHopper
    # 2025 營收＝Fleet_1GW 付費 token × 2025 單價（Alloc K 節以 IF_RevGWFleet × 單價比換算）
    rev25 = n("AL_RevGW25")
    assert all(num(x) and x > 0 for x in rev25) and num(n("AL_FleetRev25")) and n("AL_FleetRev25") > 0
    assert abs(n("AL_FleetRev25") - 8.772166) < 5e-6
    # L2：2025 年度模型規模倍數三個情境（Hopper、GB200；其餘 1）。v12.0 H2：IF_AllocQ1 0.139219／0.098928／0.191061 → 0.142722／0.101783／0.195594（GB200 CAL_BatchEtaD 3.04 → 2.36）。v11.0 G2：IF_AllocQ1 0.164989／0.119326／0.223273 → 0.139219／0.098928／0.191061（GB200 CAL_BatchEtaD 3.04；MFleet、ScaleServe 不變）
    for sid, ins, want in (("d2_model_2025", 0.65, (0.43357, 0.141695, 8.483889)), ("d2_model_2025_lo", 0.35, (0.274478, 0.100946, 13.401319)),
                           ("d2_model_2025_hi", 1.1, (0.675751, 0.194079, 5.443364))):
        sc = _vo(lo, {"ARCH_ScaleGen[1]": ins, "ARCH_ScaleGen[2]": ins, "ARCH_ScaleGen[3]": 1.0, "ARCH_ScaleGen[4]": 1.0})
        assert sc.get_name("GOV_Errors") == 0, sid
        for nm, w in zip(("L1_MFleet", "IF_AllocQ1", "L1_ScaleServe"), want):
            assert abs(sc.get_name(nm) - w) < 5e-6, (sid, nm, sc.get_name(nm), w)
        assert abs(sc.get_name("IF_AllocServeGW") - 0.898096) < 5e-6      # 支出路線不隨模型規模倍數改變
    # 單調：規模倍數越大，m 越大、Q1 越大
    ms = [_vo(lo, {"ARCH_ScaleGen[1]": v, "ARCH_ScaleGen[2]": v, "ARCH_ScaleGen[3]": 1.0, "ARCH_ScaleGen[4]": 1.0}).get_name("L1_MFleet") for v in (0.35, 0.65, 1.1)]
    assert ms[0] < ms[1] < ms[2]


def test_v1000_audit_fix2_5(model, lo):
    """v10.0 N1：IFW_*_LifeSelf＝_Prod × L1_LTotal × L1_MFleet，且不回流（除 Interface／Load_Bearing／Gov_Map 外，無公式引用 _LifeSelf）；
    N2：L1 性質欄逐列有值；N3：CHK_Verify* 只計能失敗的檢查，失敗不進 GOV_Errors。基準期望值為 LibreOffice 重算值。"""
    import openpyxl
    eng = lo.view({})
    n = eng.get_name
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    stems = ["RevGW_Luna", "RevGW_Sol", "RevGW_Astra", "RevGWFleet", "RevGWFront_Luna", "RevGWFront_Sol", "RevGWFront_Astra", "RevGWFleetFront"]
    L, m = n("L1_LTotal"), n("L1_MFleet")
    for s in stems:
        ls, pr = n(f"IFW_{s}_LifeSelf"), n(f"IFW_{s}_Prod")
        assert len(ls) == len(pr) == 15, s
        for a, b in zip(ls, pr):
            if num(b):
                assert abs(a - b * L * m) <= 1e-12 * max(1.0, abs(a)), s
            else:
                assert a == b, s      # 文字（不可達等）原樣帶過
    # 不回流：公式文字掃描
    wb = openpyxl.load_workbook(model)
    allowed = {"Interface", "Load_Bearing", "Gov_Map"}
    bad = []
    for ws in wb:
        if ws.title in allowed:
            continue
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=") and "_LifeSelf" in c.value:
                    bad.append((ws.title, c.coordinate))
    assert not bad, bad[:5]
    # N2：L1 性質欄（T）每個有數值列都有五種性質之一
    ws = wb["L1"]
    kinds = {"估計", "殘差", "倒推", "恆等式", "未解釋"}
    cnt = {}
    for r in range(5, ws.max_row + 1):
        if ws.cell(r, 1).value and ws.cell(r, 4).value is not None:
            k = eng.get("L1", f"T{r}")
            assert k in kinds, (r, k)
            cnt[k] = cnt.get(k, 0) + 1
    assert set(cnt) == kinds
    assert num(n("L1_GapUnexplained")) and abs(n("L1_GapUnexplained") - n("L1_ScaleServe2000") / n("L1_GapProduct")) < 1e-9
    # N3：驗證計數
    assert n("CHK_VerifyTotal") == 21 and n("CHK_VerifyPass") == 13 and n("CHK_VerifyFail") == 7 and n("CHK_VerifyWarn") == 1      # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：V16 移出計數 22/14/7/1 → 21/13/7/1      # v14.1 R2：V23、V24 移出計數 → 22/14/7/1； v14.0（4-3B Q4）：新增 V23–V26 → 24/16/7/1； v12.0 H1/H7：22/14/7/1 → 20/12/7/1（V18 恆等式、V20 校準相關移出計數）； v11.0 G3/G4: 19/11/8 -> 22/14/7 + 警示 1 (V20-V22 added; V1 soft cap -> warn); v10.3 4-2a F3: 17/9/8 -> 19/11/8; v10.2 E3: 14/7/7 -> 17/9/8
    assert n("CHK_VerifyPass") + n("CHK_VerifyFail") + n("CHK_VerifyWarn") == n("CHK_VerifyTotal")
    assert n("GOV_Errors") == 0      # 驗證失敗不進 GOV_Errors


def test_v1020_eta_calibration(model, lo):
    """v10.2（η 校準與驗證判準）：新基準的期望值（LibreOffice 重算值）。
    E2 SLO 為兩家量測商中位數的幾何平均；E1 的 C67／D67 未改（停損）；E3 驗證清單 17／9／8；不得變動的名稱與 v10.1 相同。"""
    base, old = lo.view({}), lo.view(OLD_SLO)
    n = base.get_name
    sl = base.get_name("SRC_PERF_066"), base.get_name("SRC_PERF_067")
    assert abs(base.get("Serving", "C21") - (116.5 * 61) ** 0.5) < 1e-9 and abs(base.get("Serving", "D21") - (50.7 * 37) ** 0.5) < 1e-9
    assert abs(base.get("Serving", "E21") - (52.1 * 32) ** 0.5) < 1e-9 and sl == (116.5, 61)
    assert base.get("Calib", "C67") == 1.2 and base.get("Calib", "D67") == 1.15          # E1：停損，未寫入（待 Project 判斷）；v15.2 B3：D67 1 → 1.15（工作單 B3）
    # E2 的效果：Sol 欄各世代 IF_TokGW 變動倍數（基準欄索引 1、4、7、10、13）；舊 SLO 的情境值＝v10.1 值
    for k, ratio in zip((1, 4, 7, 10, 13), (1.484, 1.1964, 1.201, 1.130, 1.113)):      # v15.2 B3：GB200 欄 1.201 → 1.1964（Calib D67 1 → 1.15 使 GB200 擬合 η_d 改變）
       
        assert abs(n("IF_TokGW_Sol")[k] / old.get_name("IF_TokGW_Sol")[k] - ratio) < 5e-4, (k, ratio)
    assert abs(n("L1_MFleet") - 0.460003) < 5e-6 and abs(old.get_name("L1_MFleet") - 0.61609) < 5e-6
    assert abs(n("L1_ScaleServe") - 7.996383) < 5e-6      # v15.2 B2／B3 預期變動：7.306476 → 7.996383
    # 不得變動
    for nm in ("IF_AllocServeGW", "IF_AllocRDGW", "L1_LReqFleet_Id", "L1_LTotal"):
        assert n(nm) == old.get_name(nm), nm
    assert abs(n("IF_AllocServeGW") - 0.898096) < 5e-6 and abs(n("IF_AllocRDGW") - 0.201160) < 5e-6      # v12.0 H2: 0.197258 -> 0.202947 (GB200 CAL_BatchEtaD 3.04 -> 2.36); v11.0 G2: IF_AllocRDGW 0.240199 -> 0.197258 (GB200 CAL_BatchEtaD 1 -> 3.04)
    # E3
    assert n("CHK_VerifyTotal") == 21 and n("CHK_VerifyPass") == 13 and n("CHK_VerifyFail") == 7 and n("CHK_VerifyWarn") == 1      # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：V16 移出計數 22/14/7/1 → 21/13/7/1      # v14.1 R2：V23、V24 移出計數 → 22/14/7/1； v14.0（4-3B Q4）：新增 V23–V26 → 24/16/7/1； v12.0：22/14/7/1 → 20/12/7/1（同上）； v11.0: 19/11/8 -> 22/14/7 + 警示 1
    assert n("GOV_Errors") == 0
    # 校準複本列：模型 ÷ 目標（Hopper 校準點無解、GB200 校準點 0.37）
    cal = [r for r in range(150, 260) if str(base.get("Calib", f"A{r}") or "").startswith("模型 ÷ 目標")]
    assert cal and abs(base.get("Calib", f"C{cal[0]}") - 0.338) < 5e-3 and abs(base.get("Calib", f"D{cal[0]}") - 0.8571) < 5e-3      # v12.0 H2: GB200 校準點 1.0007 -> 0.8081（模型 ÷ vLLM 10.1K 目標；CAL_BatchEtaD 3.04 -> 2.36，不再逐點吻合，V20 另列校準相關）； v11.0 G2: GB200 校準點 0.372 -> 1.0007
    # 新 SRC 名稱
    assert n("SRC_PERF_075") == 4668.1 and abs(n("SRC_PERF_076") - 5561.6) < 1e-9 and n("SRC_PERF_073") == 1850


# ── v12.0（v11.1 修補 H1–H7）：專屬測試 ──
import re

V110_PREV = HERE.parent.parent / "model" / "archive" / "20261016_Tokenomics_v11.0.xlsx"      # v11.0（LibreOffice 重算存檔）：v12.0 的「不得變」名稱對照


def _scen_inputs(sid):
    return next(sc["inputs"] for sc in SCENARIOS if sc["id"] == sid)


def _vrow(v, vid):
    for r in range(1, 400):
        if v.get("Checks", f"A{r}") == vid:
            return r
    raise AssertionError(f"Checks 找不到 {vid}")


def _vcounts(v):
    n = v.get_name
    return n("CHK_VerifyTotal"), n("CHK_VerifyPass"), n("CHK_VerifyFail"), n("CHK_VerifyWarn")


PREWARM["test_v1200_soft_cap_fail_threshold"] = [{"CHK_SoftCapFail": 1.1}, {"CHK_SoftCapFail": 1.3}]


def test_v1200_soft_cap_fail_threshold(lo):
    """H1（原則 4：檢查必須能失敗）：V1–V3 比值 ≤ 1 通過；1 至 CHK_SoftCapFail 警示；> CHK_SoftCapFail 失敗。
    情境把 V1 的比值推到約 2.5 必須判失敗、推到約 1.5 必須判警示；改門檻（1.1、1.3）也必須改變 V1 的判定；恆等式 Pass＋Fail＋Warn＝Total 在每個情境成立。"""
    base = lo.view({})
    assert base.get_name("CHK_SoftCapFail") == 2
    r = _vrow(base, "V1")
    assert abs(base.get("Checks", f"E{r}") - 1.217676) < 5e-6 and base.get("Checks", f"F{r}") == "警示"
    assert _vcounts(base) == (21, 13, 7, 1)      # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：V16 移出計數 22/14 → 21/13；      # v14.0（4-3B Q4）：新增 V23–V26（各通過）：20/12/7/1 → 24/16/7/1
    # 比值 2.5 > 2：失敗（不再只是警示）
    v = lo.view(_scen_inputs("softcap_v1_fail"))
    e, f = v.get("Checks", f"E{r}"), v.get("Checks", f"F{r}")
    assert 2.4 < e < 2.6 and f == 0, (e, f)
    assert _vcounts(v) == (21, 13, 8, 0)      # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：同上； and v.get_name("GOV_Errors") == 0      # 驗證失敗不進 GOV_Errors
    # 比值 1.5：警示
    v = lo.view(_scen_inputs("softcap_v1_warn"))
    e, f = v.get("Checks", f"E{r}"), v.get("Checks", f"F{r}")
    assert 1.4 < e < 1.6 and f == "警示", (e, f)
    assert _vcounts(v) == (21, 13, 7, 1)      # v15.0：預期變動（工作單 r1 T1-2 O14／T1-4 O9）：同上
    # 門檻本身可改：1.2177 > 1.1 失敗；< 1.3 警示
    assert lo.view({"CHK_SoftCapFail": 1.1}).get("Checks", f"F{r}") == 0
    assert lo.view({"CHK_SoftCapFail": 1.3}).get("Checks", f"F{r}") == "警示"
    for vv in (base, lo.view({"CHK_SoftCapFail": 1.1}), lo.view(_scen_inputs("softcap_v1_fail")), lo.view(_scen_inputs("softcap_v1_warn"))):
        t, pas, fail, warn = _vcounts(vv)
        assert pas + fail + warn == t


def test_v1200_gb200_geomean_and_v20_dependence(model, lo):
    """H2：CAL_BatchEtaD GB200＝兩個反推值（Calib L 節 C 欄 V20 的『所需倍數』1.83、Calib J 節 D 欄的 3.04）的幾何平均 2.36（四捨五入到小數 2 位內）；
    V20 因此不是獨立驗證點：F 欄為文字『校準相關（非獨立）』，不計入驗證項目數／通過／失敗；H3：Hopper 維持 1；H4：C68 維持 1.5。"""
    v = lo.view({})
    assert v.get_name("CAL_BatchEtaD")[0] == 1 and abs(v.get_name("CAL_BatchEtaD")[1] - 2.198284) < 1e-6 and v.get_name("CAL_BatchEtaD")[2:] == [1, 0.75, 1]      # v15.3 C2：D156 為公式（兩反推點的幾何平均）
    lrow = next(r for r in range(150, 300) if str(v.get("Calib", f"A{r}") or "").startswith("達標所需批次口徑 η_d 倍數（CAL_BatchEtaD 的解）"))
    jrow = next(r for r in range(150, 300) if str(v.get("Calib", f"A{r}") or "").startswith("達標所需 η_d 倍數（相對 CAL_EtaD"))
    c_lo, c_hi = v.get("Calib", f"C{lrow}"), v.get("Calib", f"D{jrow}")
    assert abs(c_lo - 1.5911) < 5e-4 and abs(c_hi - 3.0373) < 5e-4, (c_lo, c_hi)
    assert abs(2.1983 - (c_lo * c_hi) ** 0.5) < 0.005 and abs(v.get_name("CAL_BatchEtaD")[1] - (c_lo * c_hi) ** 0.5) < 1e-9, ((c_lo * c_hi) ** 0.5)      # v15.2 B3：D67 1 → 1.15 後兩個反推值的幾何平均 2.36 → 2.1983；CAL_BatchEtaD GB200 仍為 2.36（工作單未列），不再等於幾何平均，已列入報告「待 Project 判斷」      # 兩個反推值若移動到幾何平均不再是 2.36，這裡會失敗
    assert v.get("Calib", "C68") == 1.5 and v.get("Calib", "C156") == 1
    r20 = _vrow(v, "V20")
    assert v.get("Checks", f"G{r20}") == "校準相關（非獨立）" and str(v.get("Checks", f"F{r20}")).startswith("校準相關（非獨立）")
    numeric = sum(1 for r in range(1, 400) if re.fullmatch(r"V\d+", str(v.get("Checks", f"A{r}") or "")) and isinstance(v.get("Checks", f"F{r}"), (int, float)))
    assert numeric == 20 and v.get_name("CHK_VerifyTotal") == numeric + v.get_name("CHK_VerifyWarn")      # v15.0：V16 恆等式，數字 F 欄 21 → 20； V18、V20 的 F 欄為文字，不計入
    n = v.get_name
    for name, want in (("IF_AllocRDGW", 0.201160), ("IF_AllocQ1", 0.182997), ("IF_AllocQ2", 0.183654), ("L1_ScaleRD", 6.350031)):      # v15.3 C2：      # v11.0：0.197258／0.180086／0.180735／6.475644  # v15.2 B2／B3 預期變動：期望值依重算結果更新
        assert abs(n(name) - want) < 5e-6, (name, n(name), want)
    assert n("GOV_Errors") == 0


def test_v1200_service_side_unchanged(model, lo):
    """H2 不得變：服務端 IF_TokGW_*、L1_MFleet、IF_AllocServeGW、L1_LReqFleet_Id、L1_HoldEconMW_*、維護率 IF_MaintIT*、IF_RevGW* 與 v11.0 逐格相同。"""
    import openpyxl
    from openpyxl.utils import range_boundaries
    prev = openpyxl.load_workbook(V110_PREV, data_only=True)
    v = lo.view({})
    keep = [n for n in prev.defined_names if n.startswith(("IF_TokGW_", "L1_MFleet", "IF_AllocServeGW", "L1_LReqFleet_Id", "L1_HoldEconMW_", "IF_MaintIT", "IF_RevGW")) and n != "L1_MFleet_Lo" and n not in V152_CHANGED]      # v15.2：B2／B3 預期變動名單      # v14.1 R1：L1_MFleet_Lo 改用同欄下限（0.1839 → 0.2154），其餘（含 L1_MFleet 基準與 _Hi）仍須與 v11.0 相同
    assert len(keep) >= 19, len(keep)      # v15.2：40 → 19（B2／B3 預期變動名稱移出後的餘額；仍逐格比對）
    assert abs(v.get_name("L1_MFleet_Lo") - 0.242723485975401) < 1e-12 and abs(v.get_name("L1_MFleet_Lo") - v.get("Cap_In", "D121")) < 1e-15      # R1 的新值：＝同欄下限
    for n in keep:
        sh, rg = prev.defined_names[n].attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n


def test_v1200_range_table(lo):
    """H5：Alloc N 節『區間（情境）』的情境值（常數）逐列等於以該列輸入重算的 IF_AllocRDGW、IF_AllocQ1（容差 5e-6）；第一列為即時值；
    區間端點名稱 AL_RngRDGW_Lo／_Hi、AL_RngQ1_Lo／_Hi 為低端／高端列；基準落在區間內。同時守護 H3（Hopper 3.74 在 C68＝1.5 下仍無法達標）與 Gov_Map 區間端點不觸發 GOV_Errors。"""
    base = lo.view({})
    top = next(r for r in range(100, 400) if str(base.get("Alloc", f"A{r}") or "").startswith("N. 區間（情境）"))
    sid_by_label = {"高端": "batch_gb200_lo", "低端": "batch_range_lo", "GB200 3.04、Hopper 1": "batch_gb200_hi", "GB200 2.198、Hopper 3.74": "batch_hopper_hi", "C68＝1.0": "c68_1"}
    live = top + 2
    assert abs(base.get("Alloc", f"F{live}") - base.get_name("IF_AllocRDGW")) < 1e-15 and abs(base.get("Alloc", f"G{live}") - base.get_name("IF_AllocQ1")) < 1e-15
    assert (base.get("Alloc", f"C{live}"), base.get("Alloc", f"D{live}"), base.get("Alloc", f"E{live}")) == (base.get_name("CAL_BatchEtaD")[1], 1, 1.5)      # v15.3：即時列 C 為 D156 公式值
    seen = set()
    for r in range(live + 1, live + 12):
        lab = str(base.get("Alloc", f"A{r}") or "")
        if not lab:
            break
        key = next(k for k in sid_by_label if lab.startswith(k))
        sid = sid_by_label[key]; seen.add(sid)
        inp = _scen_inputs(sid)
        sc = lo.view(inp)
        gb, hp, c68 = base.get("Alloc", f"C{r}"), base.get("Alloc", f"D{r}"), base.get("Alloc", f"E{r}")
        want_in = {"CAL_BatchEtaD[2]": gb, "CAL_BatchEtaD[1]": hp, "Calib!C68": c68}      # 列上的輸入常數須等於情境的輸入（未列者為基準值）
        base_in = {"CAL_BatchEtaD[2]": 2.198284, "CAL_BatchEtaD[1]": 1, "Calib!C68": 1.5}
        assert all(abs(({**base_in, **inp})[k] - want_in[k]) < 1e-3 for k in want_in), (sid, inp, want_in)      # v15.3：靜態列以 3 位小數存 GB200 倍數 2.198
        rd, q1 = base.get("Alloc", f"F{r}"), base.get("Alloc", f"G{r}")
        assert abs(rd - sc.get_name("IF_AllocRDGW")) < 5e-6 and abs(q1 - sc.get_name("IF_AllocQ1")) < 5e-6, (sid, rd, sc.get_name("IF_AllocRDGW"), q1, sc.get_name("IF_AllocQ1"))
        assert sc.get_name("GOV_Errors") == 0, sid      # 區間端點（含 1.83、3.04、3.74、C68＝1.0）落在 Gov_Map 區間內
        if sid == "batch_range_lo":
            assert (base.get_name("AL_RngRDGW_Lo"), base.get_name("AL_RngQ1_Lo")) == (rd, q1)
        if sid == "batch_gb200_lo":
            assert (base.get_name("AL_RngRDGW_Hi"), base.get_name("AL_RngQ1_Hi")) == (rd, q1)
        if sid == "batch_hopper_hi":      # H3：C68＝1.5 下 Hopper 3.74 仍無法達標（產出上限約目標的 0.94；Calib J 節 C 欄）
            jr = next(x for x in range(150, 300) if str(sc.get("Calib", f"A{x}") or "").startswith("模型 ÷ 目標"))
            assert 0.93 < sc.get("Calib", f"C{jr}") < 0.95, sc.get("Calib", f"C{jr}")
        if sid == "c68_1":      # H4：C68＝1.0 試算改變服務端（情境，不是基準）
            assert abs(sc.get_name("L1_MFleet") - 0.440605) < 5e-6      # v15.2：0.388570 → 0.440605（B2/B3 預期變動）
    assert seen == set(sid_by_label.values()), seen
    lo_rd, hi_rd, lo_q1, hi_q1 = (base.get_name(x) for x in ("AL_RngRDGW_Lo", "AL_RngRDGW_Hi", "AL_RngQ1_Lo", "AL_RngQ1_Hi"))
    assert lo_rd < base.get_name("IF_AllocRDGW") < hi_rd and lo_q1 < base.get_name("IF_AllocQ1") < hi_q1
    assert abs(lo_rd - 0.160922) < 5e-6 and abs(hi_rd - 0.211628) < 5e-6 and abs(lo_q1 - 0.151954) < 5e-6 and abs(hi_q1 - 0.190703) < 5e-6      # v15.3：高端 GB200 1.83 → 1.59      # v15.2：Alloc N 節重產（原 0.162622／0.211597／0.153313／0.190680）


def _recalc_with_edits(model, tmp_path, edits):
    """複製活頁簿、改寫指定格（含公式格；此測試要模擬『T 欄被清空或手填』）、以 LibreOffice 重算，回傳唯讀值活頁簿。"""
    import openpyxl
    wb = openpyxl.load_workbook(model)
    for (sh, ref), val in edits.items():
        wb[sh][ref].value = val
    dst = tmp_path / "edit" / model.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dst)
    return openpyxl.load_workbook(lo_recalc(dst, tmp_path / "out"), data_only=True)


def _v_result(wb, vid):
    ws = wb["Checks"]
    for r in range(1, 400):
        if ws.cell(r, 1).value == vid:
            return {"C": ws.cell(r, 3).value, "D": ws.cell(r, 4).value, "E": ws.cell(r, 5).value, "F": ws.cell(r, 6).value}
    raise AssertionError(vid)


def test_v1200_v19_detects_cleared_and_handfilled_T(model, tmp_path):
    """H7（查核 #87 觀察 1）：V19 由公式自行重算 T 欄應有的判定再與 T 欄比對。
    基準通過；T 欄一格被清空必須判失敗（舊版 COUNTA／COUNTIF 同步減少、差值仍為 0）；M 欄改『否』使 T01 實質不一致，T 欄手填『一致』也必須判失敗；
    K 欄被手填覆寫時 V18 顯示『恆等式不成立』（V18 是恆等式、不計入驗證）。"""
    base = _recalc_with_edits(model, tmp_path / "a", {})
    r = _v_result(base, "V19")
    assert r["F"] == 1 and r["E"] == 0 and r["C"] == 0 and r["D"] == 0, r
    assert _v_result(base, "V18")["F"] == "恆等式（非驗證）"
    cleared = _recalc_with_edits(model, tmp_path / "b", {("Tech_Registry", "T7"): None})
    r = _v_result(cleared, "V19")
    assert r["F"] == 0 and r["E"] >= 1 and r["D"] >= 1, r
    filled = _recalc_with_edits(model, tmp_path / "c", {("Tech_Registry", "M5"): "否", ("Tech_Registry", "T5"): "一致"})
    r = _v_result(filled, "V19")
    assert r["F"] == 0 and r["C"] >= 1 and r["E"] >= 2, r      # 重算判定＝實質不一致，且 T 欄的手填值與重算判定不符
    assert _v_result(filled, "V19")["D"] == 0      # T 欄看起來全『一致』：舊版的差值檢查在這裡也會通過
    k_over = _recalc_with_edits(model, tmp_path / "d", {("Tech_Registry", "K5"): "非主流"})
    assert str(_v_result(k_over, "V18")["F"]).startswith("恆等式不成立")


# ── v13.0（4-2b-1 K1–K4）：區間完整化與時效保證 ──
V120_PREV = HERE.parent.parent / "model" / "archive" / "20261016_Tokenomics_v12.0.xlsx"      # v12.0（LibreOffice 重算存檔）：v13.0 的「既有名稱不得變」對照
CONTRACT_PREFIX = ("IF_", "IFW_", "IFC_", "L1_", "CHK_", "CAP_")
Q4_VERIFY_CHANGED = {"CHK_VerifyTotal", "CHK_VerifyPass", "L1_MFleet_Lo", "L1_PriceRealFleet_Lo", "L1_LReqFleet_Hi"}      # v14.1：加入 R1 受影響的三個名稱（L1_MFleet_Lo 同欄下限截斷及其依賴鏈；新值由 test_v1410.py 逐一斷言）；CHK_Verify* 另受 R2 影響（V23、V24 移出計數，24/16 → 22/14）
#      # v14.0（4-3B Q4）：新增 Checks V23–V26（20/12 → 24/16）；其餘既有契約名稱的值不得變
PREWARM["test_v1300_stale_flag_fires"] = [{"RNG_Version": "20261016_Tokenomics_v12.0"}, {"RNG_IF_AllocQ1_Lo": 0.5}]


def _rng_pairs(names):
    """RNG_<X>_Lo 與 RNG_<X>_Hi 成對存在的 X（X 必須是既有名稱）。"""
    return {n[4:-3] for n in names if n.startswith("RNG_") and n.endswith("_Lo") and n[4:-3] in names and f"RNG_{n[4:-3]}_Hi" in names}


def test_v1300_ranges_equal_scenarios(model, lo):
    """K2 第 3 項（真正的時效保證）：以情境重算全部區間端點，必須等於 Excel 內 RNG_<X>_Lo／_Hi 的值（容差 1e-9）。
    端點＝兩個端點情境（batch_gb200_lo：GB200 1.83；batch_range_lo：GB200 3.04、Hopper 3.74）每格的較小／較大者；
    名單也由重算決定：凡契約前綴（IF_／IFW_／IFC_／L1_／CHK_／CAP_）的名稱在任一端點情境下與基準不同，就必須有 RNG_ 區間（新出現受影響的名稱而沒有區間＝失敗）；
    基準與另外三個角落（batch_gb200_hi、batch_hopper_hi、batch_corner_x）都必須落在端點之內；AL_Rng*（v12.0 舊表，6 位小數）與新表一致（5e-6）。"""
    base = lo.view({})
    hi_v, lo_v = lo.view(_scen_inputs("batch_gb200_lo")), lo.view(_scen_inputs("batch_range_lo"))
    corners = {s: lo.view(_scen_inputs(s)) for s in ("batch_gb200_hi", "batch_hopper_hi", "batch_corner_x")}
    vr_lo_v, vr_hi_v = lo.view(_scen_inputs("batch_vr200_lo")), lo.view(_scen_inputs("batch_vr200_hi"))      # v15.0 T3-2：VR200 倍數 0.70／1.0 兩個端點情境
    contract = [n for n in base.names if n.startswith(CONTRACT_PREFIX)]
    moved = {n for n in contract if any(not _same(x, y) for sv in (hi_v, lo_v) for x, y in zip(_flat(base.get_name(n)), _flat(sv.get_name(n))))}
    moved_vr = {n for n in contract if n not in moved and any(not _same(x, y) for sv in (vr_lo_v, vr_hi_v) for x, y in zip(_flat(base.get_name(n)), _flat(sv.get_name(n))))}
    have = _rng_pairs(base.names)
    assert moved | moved_vr == have and not (moved & moved_vr), ("缺區間", sorted((moved | moved_vr) - have), "多餘區間", sorted(have - (moved | moved_vr)))
    assert len(moved) == 59 and sum(len(_flat(base.get_name(n))) for n in moved) == 647      # v14.0（4-3B）：53 → 59 個名稱、557 → 647 格（新增 IF_GMDefault_／IF_TrainInferShare_ 各 3 個；既有 53 個端點逐值不變）；v15.0：原 59 個名稱與 647 格不變
    assert len(moved_vr) == 12 and len(have) == 71 and sum(len(_flat(base.get_name(n))) for n in have) == 659      # v15.0 T3-2：+12 個只經 VR200 欄的名稱、+12 格
    bad, ncell = [], 0
    for n in sorted(moved_vr):      # v15.0：VR200 區間的端點＝兩個 VR200 情境每格的較小／較大者；基準 0.75 在其內
        b, a, c = (_flat(v.get_name(n)) for v in (base, vr_hi_v, vr_lo_v))
        lo_x, hi_x = _flat(base.get_name(f"RNG_{n}_Lo")), _flat(base.get_name(f"RNG_{n}_Hi"))
        for i in range(len(b)):
            want_lo, want_hi = min(a[i], c[i]), max(a[i], c[i])
            tol = 1e-9 * max(abs(lo_x[i]), abs(hi_x[i]), 1e-300)
            if not (_same(lo_x[i], want_lo) and _same(hi_x[i], want_hi) and lo_x[i] - tol <= b[i] <= hi_x[i] + tol):
                bad.append((n, i, lo_x[i], want_lo, hi_x[i], want_hi, b[i]))
    assert bad == [], (len(bad), bad[:8])
    for n in sorted(moved):
        b, a, c = (_flat(v.get_name(n)) for v in (base, hi_v, lo_v))
        lo_x, hi_x = _flat(base.get_name(f"RNG_{n}_Lo")), _flat(base.get_name(f"RNG_{n}_Hi"))
        assert len(lo_x) == len(hi_x) == len(b), n
        for i in range(len(b)):
            ncell += 1
            want_lo, want_hi = min(a[i], c[i]), max(a[i], c[i])
            if not (_same(lo_x[i], want_lo) and _same(hi_x[i], want_hi)):
                bad.append((n, i, lo_x[i], want_lo, hi_x[i], want_hi))
            tol = 1e-9 * max(abs(lo_x[i]), abs(hi_x[i]), 1e-300)
            if not (lo_x[i] - tol <= b[i] <= hi_x[i] + tol):
                bad.append((n, i, "基準在區間外", b[i], lo_x[i], hi_x[i]))
            for s, cv in corners.items():
                x = _flat(cv.get_name(n))[i]
                if not (lo_x[i] - tol <= x <= hi_x[i] + tol):
                    bad.append((n, i, f"角落 {s} 在區間外", x, lo_x[i], hi_x[i]))
    assert ncell == 647      # v14.0：557 → 647
    assert bad == [], (len(bad), bad[:8])
    for al, rn in (("AL_RngRDGW_Lo", "RNG_IF_AllocRDGW_Lo"), ("AL_RngRDGW_Hi", "RNG_IF_AllocRDGW_Hi"), ("AL_RngQ1_Lo", "RNG_IF_AllocQ1_Lo"), ("AL_RngQ1_Hi", "RNG_IF_AllocQ1_Hi")):
        assert abs(base.get_name(al) - base.get_name(rn)) < 5e-6, (al, rn)
    for s in (hi_v, lo_v, *corners.values()):
        assert s.get_name("GOV_Errors") == 0      # 端點與角落都在 Gov_Map 區間內


def test_v1300_range_file_matches_workbook(lo):
    """builder/v1300_ranges.json（tools/gen_ranges.py 的輸出）與 Excel 內的 RNG_* 逐值相同；版本字串等於現行版本；時效旗標為『一致』。"""
    import json
    base = lo.view({})
    d = json.loads((HERE.parent.parent / "builder" / "v1300_ranges.json").read_text(encoding="utf-8"))
    assert set(d["names"]) == _rng_pairs(base.names)
    for n, rec in d["names"].items():
        for tag in ("lo", "hi"):
            got = _flat(base.get_name(f"RNG_{n}_{tag.capitalize()}"))
            assert len(got) == len(rec[tag]) and all(_same(x, y) for x, y in zip(got, rec[tag])), (n, tag)
    cur = model_path().name[: -len(".xlsx")]
    assert d["version"] == cur == base.get_name("RNG_Version") == base.get_name("RNG_Current"), (d["version"], cur)
    assert base.get_name("RNG_OutCount") == 0 and base.get_name("RNG_StaleFlag") == "一致"
    assert base.get_name("GOV_Warnings") == 280      # RG1／RG2 在基準為 0，不改變 GOV_Warnings      # v13.1：282 → 280（W1 −2）


def _chk_row(v, code):
    for r in range(1, 400):
        if v.get("Checks", f"A{r}") == code:
            return r
    raise AssertionError(code)


def test_v1300_stale_flag_fires(lo):
    """K2 第 1、2 項：區間計算版本與現行版本不同（舊版字串），或基準落在區間之外（把 RNG_IF_AllocQ1_Lo 改成 0.5 > 基準 0.184），
    RNG_StaleFlag 必須顯示『區間過期』，Checks RG1／RG2 觸發，並計入 GOV_Warnings（282 → 283）；GOV_Errors 不變。"""
    base = lo.view({})
    assert base.get_name("RNG_StaleFlag") == "一致" and base.get_name("GOV_Warnings") == 280      # v13.1：282 → 280
    assert base.get("Checks", f"D{_chk_row(base, 'RG1')}") == 0 and base.get("Checks", f"D{_chk_row(base, 'RG2')}") == 0
    old = lo.view({"RNG_Version": "20261016_Tokenomics_v12.0"})
    assert old.get_name("RNG_StaleFlag") == "區間過期" and old.get("Checks", f"D{_chk_row(old, 'RG1')}") == 1
    assert old.get_name("GOV_Warnings") == 281 and old.get_name("GOV_Errors") == 0      # v13.1：283 → 281
    out = lo.view({"RNG_IF_AllocQ1_Lo": 0.5})
    assert out.get_name("RNG_OutCount") == 1 and out.get_name("RNG_StaleFlag") == "區間過期"
    assert out.get("Checks", f"D{_chk_row(out, 'RG2')}") == 1 and out.get_name("GOV_Warnings") == 281 and out.get_name("GOV_Errors") == 0      # v13.1：283 → 281


def test_v1300_existing_contract_names_unchanged(model, lo):
    """4-2b-1 驗收：既有 IF_／IFW_／IFC_／L1_／CHK_／CAP_ 名稱的值與 v12.0 逐格相同（容差 1e-9）；K4 只改標籤，CHK_Verify* 不變。"""
    import openpyxl
    from openpyxl.utils import range_boundaries
    prev = openpyxl.load_workbook(V120_PREV, data_only=True)
    v = lo.view({})
    keep = [n for n in prev.defined_names if n.startswith(CONTRACT_PREFIX) and n not in Q4_VERIFY_CHANGED and n not in V152_CHANGED]      # v15.2：B2／B3 預期變動名單（605 個既有契約名稱中 252 個移出對照，餘 353 個仍須與 v12.0 相同）；      # v14.0（4-3B Q4）：CHK_VerifyTotal／Pass 因新增 V23–V26 而變（見檔尾斷言）；Fail／Warn 仍須相同
    assert len(keep) >= 340, len(keep)      # v15.3：350 → 340（再扣除 v15.3 預期變動名稱後餘 343）； v15.2：500 → 350（預期變動名稱移出後的餘額 353）
    for n in keep:
        sh, rg = prev.defined_names[n].attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        if n.startswith("IFC_"):      # v14.0（4-3B Q2）：Interface 新增 M 節（第 330 列起），IFC_ 欄範圍向後延長；原有的前段逐格須相同
            skip = {193 - r1}      # v15.0：Interface 第 193 列新增（IF_FrontSuccVRQual 的 IFC_ 中繼資料）；舊版該列為空，其餘逐格須相同
            assert len(got) >= len(want) and all(_same(a, b) for i, (a, b) in enumerate(zip(want, got)) if i not in skip) and all(want[i] in (None, "") for i in skip), n
            continue
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n
    assert (v.get_name("CHK_VerifyTotal"), v.get_name("CHK_VerifyPass"), v.get_name("CHK_VerifyFail"), v.get_name("CHK_VerifyWarn")) == (21, 13, 7, 1)      # v15.0 O9：V16 移出計數（22/14 → 21/13）； v14.0（4-3B Q4）：CHK_Verify* 只因新增 V23–V26 而變（20/12/7/1 → 24/16/7/1）


def test_v1300_c68_assumed_and_identity_label(lo):
    """K3：Calib C68 的 Gov_Map 類別為 Assumed、進入 Load_Bearing；舊類別字樣『倒推』與 v12.0 以前的區間文字『1–3（原註）』保留在 AL 欄；現行區間 1.0–1.5 維持。
    K4：Checks 驗證計數的標籤標明『Pass＋Fail＋Warn＝Total』是恆等式（非驗證）。"""
    v = lo.view({})
    r = next(x for x in range(5, 800) if v.get("Gov_Map", f"C{x}") == "Calib" and v.get("Gov_Map", f"D{x}") == "C68")
    assert v.get("Gov_Map", f"F{r}") == "Assumed" and (v.get("Gov_Map", f"K{r}"), v.get("Gov_Map", f"L{r}")) == (1, 1.5)
    assert "倒推" in v.get("Gov_Map", f"AL{r}") and "1–3（原註）" in v.get("Gov_Map", f"AL{r}") and "v12.0 前" in v.get("Gov_Map", f"AL{r}")
    assert "更正為 Assumed" in v.get("Gov_Map", f"N{r}") and "倒推（v5.5 建檔時與 C67 手算配對" in v.get("Gov_Map", f"N{r}")      # 舊字樣仍在
    gm_id = v.get("Gov_Map", f"A{r}")
    assert gm_id in [v.get("Load_Bearing", f"A{x}") for x in range(5, 5 + v.get_name("LB_LiveCount"))]
    vt = _chk_row(v, "VT")
    assert "恆等式（非驗證）" in v.get("Checks", f"B{vt}") and "Pass＋Fail＋Warn＝Total" in v.get("Checks", f"B{vt}")

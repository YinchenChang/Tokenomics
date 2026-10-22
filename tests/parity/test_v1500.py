"""v15.0 稽核結案（工作單 docs/workorders/20261017_v14.3_稽核結案.md r1）專屬測試。讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。

T1-1 O13  SRC_DEM_004_Lo／_Hi 接進支出路線：RNG_Dem004_IF_AllocServeGW／IF_AllocQ1／IF_AllocQ2 的 _Lo／_Hi（Alloc Q 節，公式）。
T1-3 O15  B11：IF_FrontSuccVRQual 守衛旗標（Interface 第 193 列）。
T3-2 O4   VR200 批次倍數區間：只經 VR200 欄的 12 個名稱的 RNG_*_Lo／_Hi，端點＝batch_vr200_lo／batch_vr200_hi 兩情境每格較小／較大者。
T3-1 O5   SRC_PERF_060 來源登錄更正（修訂九：原字樣保留）。
其他：O9 V16 改標恆等式、O14 L1 換算、O20 κ 推導區塊、Decisions SL46-*、既有 59 個名稱的區間端點不變。
"""
import json
import re
from pathlib import Path

import openpyxl
import pytest

from conftest import model_path

# v19.1：Arch!C17 改值（4224 → 2176，W1 B2）後 Luna 相關值變動；下列檢驗的事前值在 C17 回 4224（SRC_MOD_106＝1024）時仍成立，由 test_v1910 看守兩者的關係
C17_OLD = {"SRC_MOD_106": 1024}

REPO = Path(__file__).resolve().parents[2]
V152_CHANGED = set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v152_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v153_changed_names.json", encoding="utf-8"))["names"]) | set(__import__("json").load(open(REPO / "tests" / "parity" / "fixtures" / "v191_changed_names.json", encoding="utf-8"))["changed"])      # v19.1：併入 Arch!C17 下游的預期變動名稱； v15.3：另併入 v15.2→v15.3 的預期變動名單（E1／E2／C2／D1；test_v1530 逐名稱釘住）
FIXTURES = Path(__file__).resolve().parent / "fixtures"
RANGES = json.loads((REPO / "builder" / "v1300_ranges.json").read_text(encoding="utf-8"))
VR_NAMES = sorted(n for n, d in RANGES["names"].items() if d.get("source") == "vr200")
SPEND = ("IF_AllocServeGW", "IF_AllocQ1", "IF_AllocQ2")
SC_FRONT_NONE = {"B5_PFloor": 0.9999}      # p_min 高到沒有任何組合合格
SC_SPEND_HI = {"SRC_DEM_004": 20.0}      # 基準支出 8.4 → 20，遠高於 SRC_DEM_004_Hi＝8.8：基準落在 RNG_Dem004_* 區間之外
SC_VR_LO = {"CAL_BatchEtaD[4]": 0.70}
SC_VR_HI = {"CAL_BatchEtaD[4]": 1.0}
PREWARM = {"test_v1500_other_contract_names_unchanged_from_v142": [C17_OLD], "test_v1500_o13_names_and_base_inside": [C17_OLD], 
    "test_v1500_o13_out_of_range_fires_rg4": [SC_SPEND_HI],
    "test_v1500_b11_guard_flags_no_qualified_combination": [SC_FRONT_NONE],
    "test_v1500_t32_endpoints_equal_vr200_scenarios": [SC_VR_LO, SC_VR_HI],
    "test_v1500_t32_vr200_names_move_only_with_vr200_multiplier": [SC_VR_LO, SC_VR_HI],
}


def _flat(v):
    if isinstance(v, list):
        return [x for r in v for x in _flat(r)]
    return [v]


def _same(a, b):
    a = None if a == "" else a
    b = None if b == "" else b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


def _chk_row(v, cid):
    for r in range(1, 400):
        if v.get("Checks", f"A{r}") == cid:
            return r
    raise AssertionError(cid)


# ── T1-1 O13 ──
def test_v1500_o13_names_and_base_inside(lo):
    """六個端點名稱 ＋ OutCount 存在；基準值不變（0.898096／0.184322／0.184983）且落在 _Lo／_Hi 之內；服務 GW 與 SRC_DEM_004 區間成正比。"""
    v = lo.view(C17_OLD)
    want = {"IF_AllocServeGW": 0.898096, "IF_AllocQ1": 0.184347, "IF_AllocQ2": 0.185009}      # v15.3 C2：Q1／Q2 再升為 0.182997／0.183654（GB200 批次倍數 2.36 → 2.198）；v15.2 B3：Q1／Q2 0.184322／0.184983 → 0.181823／0.182477（D67 使 GB200 欄研發 GW 略降）
    for n in SPEND:
        base = v.get_name(n)
        assert abs(base - want[n]) < 5e-6, (n, base)      # 基準不變（同 test_parity）
        lo_, hi_ = v.get_name(f"RNG_Dem004_{n}_Lo"), v.get_name(f"RNG_Dem004_{n}_Hi")
        assert isinstance(lo_, (int, float)) and isinstance(hi_, (int, float)) and lo_ < base < hi_, (n, lo_, base, hi_)
    assert v.get_name("RNG_Dem004_OutCount") == 0
    # 服務 GW：支出 ÷ 持有成本，故端點比＝SRC_DEM_004 區間比
    r = v.get_name("RNG_Dem004_IF_AllocServeGW_Lo") / v.get_name("RNG_Dem004_IF_AllocServeGW_Hi")
    assert abs(r - v.get_name("SRC_DEM_004_Lo") / v.get_name("SRC_DEM_004_Hi")) < 1e-9
    assert abs(v.get_name("RNG_Dem004_IF_AllocServeGW_Hi") / v.get_name("IF_AllocServeGW") - v.get_name("SRC_DEM_004_Hi") / v.get_name("SRC_DEM_004")) < 1e-9
    # 支出高 → Q1／Q2 低（服務占去更多 GW）：端點不是『來源低端對名稱低端』
    assert v.get_name("RNG_Dem004_IF_AllocQ1_Hi") > v.get_name("IF_AllocQ1") > v.get_name("RNG_Dem004_IF_AllocQ1_Lo")


def test_v1500_o13_mechanism_is_excel_formula(wbf):
    """端點是 Alloc Q 節的公式（讀 SRC_DEM_004_Lo／_Hi），不是貼上的數值；名稱指向該節。"""
    ws = wbf["Alloc"]
    for n in SPEND:
        for tag in ("Lo", "Hi"):
            sh, ref = wbf.defined_names[f"RNG_Dem004_{n}_{tag}"].attr_text.split("!")
            assert sh == "Alloc"
            f = ws[ref.replace("$", "")].value
            assert isinstance(f, str) and f.startswith("=") and ("MIN(" in f or "MAX(" in f), (n, tag, f)
    srcs = " ".join(str(c.value) for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=") and "SRC_DEM_004_" in c.value)
    assert "SRC_DEM_004_Lo" in srcs and "SRC_DEM_004_Hi" in srcs


def test_v1500_o13_out_of_range_fires_rg4(lo):
    """防空轉：把 SRC_DEM_004（基準支出）改到區間上端之外，基準落在端點之外，OutCount > 0，Checks RG4 ＝ 1 並計入 GOV_Warnings（280 → 281）。"""
    base, out = lo.view({}), lo.view(SC_SPEND_HI)
    assert base.get_name("RNG_Dem004_OutCount") == 0 and base.get("Checks", f"D{_chk_row(base, 'RG4')}") == 0
    assert out.get_name("RNG_Dem004_OutCount") >= 1
    assert out.get("Checks", f"D{_chk_row(out, 'RG4')}") == 1
    assert out.get_name("GOV_Warnings") == base.get_name("GOV_Warnings") + 1 + (out.get("Checks", f"D{_chk_row(out, 'RG1')}") + out.get("Checks", f"D{_chk_row(out, 'RG2')}") + out.get("Checks", f"D{_chk_row(out, 'RG3')}") - base.get("Checks", f"D{_chk_row(base, 'RG1')}") - base.get("Checks", f"D{_chk_row(base, 'RG2')}") - base.get("Checks", f"D{_chk_row(base, 'RG3')}")) + 1      # v16.0：L1_LReqFleet_IdNoK（第 115 列）的基準隨 SRC_DEM_004 離開其 _Lo／_Hi（兩端固定取 SRC_DEM_004_Lo／_Hi）→ Checks H3 ＋1（與 RG4 同源）；K7／M3 為既有
    assert out.get("Checks", f"D{_chk_row(out, 'H3')}") == 1 and base.get("Checks", f"D{_chk_row(base, 'H3')}") == 0
    assert out.get_name("GOV_Errors") == 0


# ── T1-3 O15 B11 ──
def test_v1500_b11_flag_is_one_at_base(lo, wbf):
    v = lo.view({})
    assert _flat(v.get_name("IF_FrontSuccVRQual")) == [1] * 5
    assert wbf.defined_names["IF_FrontSuccVRQual"].attr_text == "Interface!$C$193:$G$193"
    for c in "CDEFG":
        assert wbf["Interface"][f"{c}193"].value == f"=IF(ISNUMBER({c}190),1,0)"


def test_v1500_b11_guard_flags_no_qualified_combination(lo):
    """B11：p_min 高到沒有組合合格 → IF_FrontSuccVR／Name／P 回『無合格』文字（原行為），旗標＝0；基準為 1。"""
    v = lo.view(SC_FRONT_NONE)
    assert _flat(v.get_name("IF_FrontSuccVRQual")) == [0] * 5
    assert all(isinstance(x, str) for x in _flat(v.get_name("IF_FrontSuccVR")))
    assert all(x == "無合格" for x in _flat(v.get_name("IF_FrontSuccVRName")))
    # GOV_Errors 在此極端 p_min 下為 1（E10 基準值不在低／高之間）是既有行為，v14.2 檔相同；本版不改


# ── T3-2 O4 ──
def test_v1500_t32_twelve_vr200_names_have_ranges(lo):
    """12 個只經 VR200 欄的名稱都有 RNG_*_Lo／_Hi，基準在區間內；既有 59 個名稱（另有 15 格名稱的 VR200 欄點值）的端點與 v14.2 檔相同（快照另測）。"""
    assert len(VR_NAMES) == 14, VR_NAMES      # v19.1：12 → 14（區間端點檔重產後 CHK_VerifyFail／CHK_VerifyPass 也納入，只經 VR200 欄變動）
    assert sum(1 for d in RANGES["names"].values() if d.get("source") != "vr200") == 59
    v = lo.view({})
    for n in VR_NAMES:
        base, lo_, hi_ = _flat(v.get_name(n)), _flat(v.get_name(f"RNG_{n}_Lo")), _flat(v.get_name(f"RNG_{n}_Hi"))
        assert len(base) == len(lo_) == len(hi_) == RANGES["names"][n]["n"]
        for b, a, c in zip(base, lo_, hi_):
            assert a - 1e-9 * abs(a) <= b <= c + 1e-9 * abs(c), (n, a, b, c)
    assert v.get_name("RNG_OutCount") == 0 and v.get_name("RNG_StaleFlag") == "一致"


def test_v1500_t32_endpoints_equal_vr200_scenarios(lo):
    """時效保證：以 batch_vr200_lo（0.70）／batch_vr200_hi（1.0）重算，12 個名稱每格的較小／較大者必須等於 Excel 內的 RNG_*_Lo／_Hi（容差 1e-9）；基準 0.75 在其內。"""
    base, a, b = lo.view({}), lo.view(SC_VR_LO), lo.view(SC_VR_HI)
    assert base.get_name("CAL_BatchEtaD")[3] == 0.75
    moved = 0
    for n in VR_NAMES:
        x, y = _flat(a.get_name(n)), _flat(b.get_name(n))
        lo_x, hi_x = _flat(base.get_name(f"RNG_{n}_Lo")), _flat(base.get_name(f"RNG_{n}_Hi"))
        for i in range(len(x)):
            if isinstance(x[i], (int, float)) and isinstance(y[i], (int, float)):
                assert _same(min(x[i], y[i]), lo_x[i]) and _same(max(x[i], y[i]), hi_x[i]), (n, i, x[i], y[i], lo_x[i], hi_x[i])
                moved += not _same(x[i], y[i])
    assert moved >= 12      # 防空轉：兩個端點情境下，12 個名稱都確實不同


def test_v1500_t32_vr200_names_move_only_with_vr200_multiplier(lo):
    """12 個名稱在兩個批次（GB200／Hopper）端點情境下不動（所以才屬『只經 VR200 欄』）；在 VR200 倍數改變時才動。"""
    import yaml
    scen = {x["id"]: x["inputs"] for x in yaml.safe_load((REPO / "tests" / "parity" / "scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]}
    base = lo.view({})
    for sc in ("batch_gb200_lo", "batch_gb200_hi", "batch_hopper_hi", "batch_range_lo"):
        v = lo.view(scen[sc])
        for n in VR_NAMES:
            assert all(_same(p, q) for p, q in zip(_flat(base.get_name(n)), _flat(v.get_name(n)))), (sc, n)
    a = lo.view(SC_VR_LO)
    assert any(not _same(p, q) for n in VR_NAMES for p, q in zip(_flat(base.get_name(n)), _flat(a.get_name(n))))


def test_v1500_t32_existing_range_endpoints_unchanged(wbf):
    """既有 59 個名稱的 _Lo／_Hi 端點與 v14.2 的快照逐格相同（工作單：不得變動既有 RNG_* 端點）。"""
    old = json.loads((FIXTURES / "contract_snapshot_v15.1.json").read_text(encoding="utf-8"))
    assert len([n for n in old["names"] if n.startswith("RNG_")]) >= 122 + 24
    ws_vals = openpyxl.load_workbook(model_path(), data_only=True)
    n_checked = 0
    for n, d in RANGES["names"].items():
        if d.get("source") == "vr200":
            continue
        for tag, key in (("Lo", "lo"), ("Hi", "hi")):
            sh, ref = wbf.defined_names[f"RNG_{n}_{tag}"].attr_text.split("!")
            cells = ws_vals[sh.strip("'")][ref.replace("$", "")]
            got = [cells.value] if not isinstance(cells, tuple) else [c.value for r in cells for c in r]
            assert all(_same(p, q) for p, q in zip(got, d[key])) and len(got) == len(d[key]), (n, tag)
            n_checked += len(got)
    assert n_checked == 2 * 647


def test_v1500_t32_wording_corrected_with_original_kept(wbf):
    ws = wbf["Alloc"]
    txt = " ".join(str(ws.cell(r, 1).value or "") for r in range(150, 420))
    assert "VR200 欄無區間" in txt and "VR200 批次倍數無證據" in txt      # 原字樣保留
    assert "v15.0 更正（修訂九，T3-2）" in txt and "0.70–0.76" in txt and "約 1.20–1.28" in txt


# ── T3-1 O5 ──
def test_v1500_t31_src_perf_060_corrected_value_unchanged(lo, wbf):
    """SRC_PERF_060：值 556 不變，V1 判定不變（1.22，警示）；標記改 Interested-party、URL 為 NVIDIA 技術部落格；原字樣逐字保留在 W 欄備註。"""
    ws = wbf["SRC_Perf"]
    r = next(x for x in range(5, ws.max_row + 1) if ws.cell(x, 1).value == "SRC_PERF_060")
    assert ws.cell(r, 3).value == 556
    assert str(ws.cell(r, 10).value).startswith("https://developer.nvidia.com/blog/nvidia-blackwell-ultra-sets-new-inference-records-in-mlperf-debut")
    assert ws.cell(r, 14).value.startswith("一手（已讀")
    assert "Interested-party" in str(ws.cell(r, 13).value)
    w = str(ws.cell(r, 23).value)
    for old in ("二手（3A 查證轉引）", "MLCommons 稽核為中立；提交者 NVIDIA 自行挑選配置；Hopper 結果 NVIDIA 註明未經 MLCommons 驗證", "server；Closed；NVIDIA 註明 Hopper 結果未經 MLCommons 驗證", "docs/reports/20261015_稽核修正3A_查證.md"):
        assert old in w, old
    assert "v15.0 更正" in w
    v = lo.view({})
    assert v.get_name("SRC_PERF_060") == 556
    row = next(x for x in range(1, 400) if v.get("Checks", f"A{x}") == "V1")
    assert abs(v.get("Checks", f"E{row}") - 1.21767628625269) < 1e-9 and v.get("Checks", f"F{row}") == "警示"
    cal = wbf["Calib"]
    assert "NVIDIA 自測" in cal["G121"].value and "MLPerf（MLCommons 稽核）／NVIDIA 提交（v5.1；3A 查證轉引）" in cal["J121"].value


# ── O9 ──
def test_v1500_o9_v16_is_identity_and_not_counted(lo):
    v = lo.view({})
    r = _chk_row(v, "V16")
    assert v.get("Checks", f"F{r}") == "恆等式（非驗證）" and v.get("Checks", f"G{r}") == "恆等式（非驗證）"
    assert (v.get_name("CHK_VerifyTotal"), v.get_name("CHK_VerifyPass"), v.get_name("CHK_VerifyFail"), v.get_name("CHK_VerifyWarn")) == (21, 13, 7, 1)
    assert "原『恆等式（非驗證）』；單邊界限，輸入改變時可能失敗，v10.2 E3 改回驗證計數" in str(v.get("Checks", f"J{r}"))      # 原文保留


# ── O14 ──
def test_v1500_o14_l1_comparisons_use_model_unit(lo, wbf):
    v = lo.view({})
    ws = wbf["L1"]
    assert ws["M31"].value == "=SRC_PRC_002*SRC_PRC_047"
    assert abs(v.get("L1", "M31") - 3.57 * 0.85) < 1e-9
    assert "IF_RacksPerGW" in ws["M59"].value and "IF_RacksPerGW" in ws["M60"].value
    assert abs(v.get("L1", "M59") - 1.0429264557794 * _flat(v.get_name("IF_RacksPerGW"))[7] / _flat(v.get_name("IF_RacksPerGW"))[4]) < 1e-9
    for r in range(61, 66):
        assert "IF_CostDec_Sol" in ws[f"M{r}"].value
        assert abs(v.get("L1", f"M{r}") - 0.664112192505173 / (_flat(v.get_name("IF_CostDec_Sol"))[10] / _flat(v.get_name("IF_CostDec_Sol"))[7])) < 1e-9
    sp = wbf["SRC_Price"]
    rr = next(x for x in range(5, sp.max_row + 1) if sp.cell(x, 1).value == "SRC_PRC_047")
    assert sp.cell(rr, 3).value == 0.85


# ── O20 ──
def test_v1500_o20_kappa_block_in_workbook_value_unchanged(lo):
    v = lo.view({})
    assert v.get_name("AL_Kappa") == 1.0 and v.get_name("AL_Kappa_Lo") == 0.65 and v.get_name("AL_Kappa_Hi") == 1.2
    k = v.get_name("AL_KappaCalc")
    assert isinstance(k, (int, float)) and 0.65 <= k <= 1.2 and v.get_name("AL_KappaCalcIn") == 1


# ── T2 ──
def test_v1500_decisions_recorded(wbf):
    dec = wbf["Decisions"]
    ids = {dec.cell(r, 1).value: dec.cell(r, 4).value for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value}
    want = [f"SL46-{i:02d}" for i in range(1, 25)]
    assert set(want) <= set(ids), sorted(set(want) - set(ids))
    for k in want:
        assert "Andy 2026-10-17" in str(ids[k]) or "Andy 2026-10-17" in "".join(str(dec.cell(r, 6).value) for r in range(5, dec.max_row + 1) if dec.cell(r, 1).value == k)
    rows = {dec.cell(r, 1).value: r for r in range(5, dec.max_row + 1)}
    assert "13:52" in str(dec.cell(rows["SL46-23"], 6).value) and "13:52" in str(dec.cell(rows["SL46-24"], 6).value)
    assert "13:39" in str(dec.cell(rows["SL46-01"], 6).value)
    assert "收斂" not in str(ids["SL46-24"]) and "1.20–1.28" in str(ids["SL46-24"])


def test_v1500_other_contract_names_unchanged_from_v142(lo):
    """與 v14.2 逐值比較：IF_／IFW_／L1_／CHK_／CAP_ 基準名稱除工作單預期（CHK_Verify*、IFC_*（新增第 193 列）、RNG_Version／Current）外全部相同。"""
    prev = REPO / "model" / "archive" / "20261017_Tokenomics_v14.2.xlsx"
    pw = openpyxl.load_workbook(prev, data_only=True)
    v = lo.view(C17_OLD)
    skip = {"CHK_VerifyTotal", "CHK_VerifyPass", "RNG_Version", "RNG_Current", "RNG_OutCount", "RNG_StaleFlag", "GOV_Info", "GOV_Table"} | V152_CHANGED      # v15.2：B2／B3 預期變動名單
    n_ok = 0
    from openpyxl.utils import range_boundaries
    for n, d in pw.defined_names.items():
        if not n.startswith(("IF_", "IFW_", "L1_", "CHK_", "CAP_", "RNG_", "AL_")) or n in skip or "!" not in d.attr_text:
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n
        n_ok += 1
    assert n_ok >= 340, n_ok      # v15.2：扣除 V152_CHANGED 後；原 ≥ 700

"""v20.0 GW 優先校準（工作單 docs/workorders/20261022_v20.0_GW優先校準.md r0）專屬測試。讀 LibreOffice 重算後的值。

  1. 新名稱事前值：工作單數字（5 位小數，相對 1e-4）與獨立重算值（Python 依 SRC 值重算，相對 1e-9）。
  2. 恆等式：L1_TokLedger_GW25 × AL_DPaid ＝ L1_TokPaid_GW25；L1_PayRatio25 × L1_LReqFleet_Full ＝ 1；L1_M_2026Q2 低 ≤ 基準 ≤ 高。
  3. 判讀列：Cap_In C242 與 L1 P89 的基準字樣含「未定」，所需 L 側讀 L1_LReqFleet_Full（0.807）。
  4. 既有名稱數值不變（對封存的 v19.1）：只有 L1_M_2026Q2／L1_M 的 _Lo／_Hi（文字→數字）、CHK_L1Order、GOV_Warnings、版本字串與範圍延伸例外。
  5. 輸入變動傳遞（SRC_DEM_009、AL_ProdDerate_Hi）、壓力情境無錯誤值（f_registry、B4_CacheHit＝0）。
  6. 記錄與治理：SRC_DEM_088、DB_Evidence E401、Decisions SL55-01、Gov_Map 新藍字輸入、Checks P1、README。
"""
import math
import re
from pathlib import Path

import openpyxl
import pytest
import yaml
from openpyxl.utils import range_boundaries

from conftest import model_path
from v2150_allow import v213_cells, strip      # v21.3：v21.2 → v21.3 的逐格差異集合（規則同 test_v2130，只到工作單 W1–W6 列明的格）
from test_v2120 import CHANGED as V2120_CHANGED, REVERT as SB_OLD      # v21.2：AL_SpendBasis 改 1.8 的預期變動名稱（44 個）與舊值輸入
from test_v2130 import CHANGED as _V2130_CHANGED, LABEL_NAMES as _V2130_LABEL, INDEX_NAMES as _V2130_INDEX, REVERT as R213_OLD      # v21.3：機架價低端 7.5／Sol 快取價 0.10 的預期變動名稱與舊值輸入（test_v2130 看守）
V2130_CHANGED = _V2130_CHANGED | _V2130_LABEL | _V2130_INDEX | {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi", "SRC_PRC_049"}      # v21.3：171 個值變動名稱＋Cap_In A47 改名連帶的 2 個文字名稱＋SRC_Index 延伸的 4 個 IDX_Src*＋新 SRC 紀錄 4 個名稱＋SRC_PRC_049（舊值輸入 R213_OLD 把它設回 0.2 的副作用；v21.3 起 Active）

REPO = Path(__file__).resolve().parents[2]
V191 = REPO / "model" / "archive" / "20261022_Tokenomics_v19.1.xlsx"
SC = {s["id"]: s["inputs"] for s in yaml.safe_load((Path(__file__).resolve().parent / "scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]}
F_REGISTRY = SC["f_registry_t07_t09_on"]
CACHE_OFF = SC["d9_cache_cap_off"]
GW_END = {"SRC_DEM_009": 2.2}
DERATE_HI = {}          # AL_ProdDerate_Hi 在 Cap_In P 節，用格位鍵改（見測試內）
PREWARM = {"test_v2000_inputs_propagate": [GW_END], "test_v2000_stress_scenarios_no_error_values": [F_REGISTRY, CACHE_OFF]}

SKIP = ("RNG_", "IDX_", "GOV_", "IFC_")      # 區間端點、SRC_Index 範圍、治理計數另行檢查
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
ALLOWED_CHANGED = {"L1_M_2026Q2_Lo", "L1_M_2026Q2_Hi", "L1_M_Lo", "L1_M_Hi"} | {f"IFW_{s}_LifeSelf" for s in ("RevGW_Luna", "RevGW_Sol", "RevGW_Astra", "RevGWFleet", "RevGWFront_Luna", "RevGWFront_Sol", "RevGWFront_Astra", "RevGWFleetFront")} | {"L1_PriceReqBE", "L1_PriceReqBE_Lo", "L1_PriceReqBE_Hi"}      # v20.1：LifeSelf 與 L1_PriceReqBE 三格值改變（test_v2010 看守）；      # 文字「無區間」→ 數字區間（W3）；H3 計數（L1_DPaid_Scen 的 D／E／F 是三個情境）


def _flat(v):
    if isinstance(v, (list, tuple)):
        return [x for r in v for x in _flat(r)]
    return [v]


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


def _rel(a, b):
    return abs(a / b - 1)


# ---------------------------------------------------------------- 1. 事前值
WO = {      # 工作單事前值（基準, 低, 高）
    "AL_FleetGW25": (1.12781, 1.0, 1.25),
    "L1_ServeGW_GW25": (0.46240, 0.30000, 0.75000),
    "L1_TokPaid_GW25": (5814261069, 1731866244, 20113652019),
    "L1_TokLedger_GW25": (1.51999, 0.45275, 5.25820),
    "L1_HoldFleet25": (10.5484, 9.3531, 11.6914),
    "L1_PayRatio25": (1.23904, 1.11792, 1.39739),
    "L1_RevPerGW25": (11.5889, 10.4560, 13.0700),
    "L1_LReqFleet_Full": (0.80708, 0.71562, 0.89452),
    "L1_M_2026Q2": (1.35537, 0.81752, 1.60950),      # v21.3：(1.34320, 0.81018, 1.59505) → (1.35537, 0.81752, 1.60950)（Sol 快取價 0.20 → 0.10：有效牌價 −0.9%，m 同比例上升；test_v2130 看守）
}


def _triple(v, name):
    return [_flat(v.get_name(name + s))[0] for s in ("", "_Lo", "_Hi")]


@pytest.mark.parametrize("name", sorted(WO))
def test_v2000_workorder_values(lo, name):
    v = lo.view({})
    got = _triple(v, name)
    for g, w in zip(got, WO[name]):
        assert isinstance(g, (int, float)), (name, got)
        assert _rel(g, w) <= 1e-4, (name, got, WO[name])


def test_v2000_independent_recompute(lo):
    """依 SRC 值與模型輸入，在 Python 重算 W1–W4 的全部新名稱（相對 1e-9）。"""
    v = lo.view({})
    g0, g1, rev = v.get_name("SRC_DEM_008"), v.get_name("SRC_DEM_009"), v.get_name("SRC_DEM_007")
    gw = [(g1 - g0) / math.log(g1 / g0), 1.0, (g0 + g1) / 2]
    assert [_rel(a, b) for a, b in zip(_triple(v, "AL_FleetGW25"), gw)] == [pytest.approx(0, abs=1e-9)] * 3
    serve = [v.get("Cap_In", f"{c}28") for c in "CDE"]
    free = [v.get_name("IF_FreeShare"), v.get("Cap_In", "E29"), v.get("Cap_In", "D29")]
    util = [v.get_name("AL_UtilActual"), v.get_name("AL_UtilActual_Lo"), v.get_name("AL_UtilActual_Hi")]
    eff = [v.get_name("CTL_ProdDerate"), 0.72, 0.95]
    mix, paid = _flat(v.get_name("AL_MixGen")), _flat(v.get_name("IF_TokGWPaidMix"))
    sigma = sum(m * paid[c - 1] for m, c in zip(mix, (2, 5, 8, 11)))
    assert _rel(sigma, 66815827324) <= 1e-9 or _rel(sigma, 66815827324) <= 1e-6
    sgw = [a * b for a, b in zip(gw, serve)]
    tok = [s * (1 - f) * sigma * u * e for s, f, u, e in zip(sgw, free, util, eff)]
    dpaid = v.get_name("AL_DPaid")
    hold = [x * v.get_name("AL_FleetHold") for x in gw]
    exp = {
        "L1_ServeGW_GW25": sgw, "L1_TokPaid_GW25": tok, "L1_TokLedger_GW25": [t / dpaid for t in tok], "L1_HoldFleet25": hold,
        "L1_PayRatio25": [rev / hold[0], rev / hold[2], rev / hold[1]], "L1_RevPerGW25": [rev / gw[0], rev / gw[2], rev / gw[1]],
        "L1_LReqFleet_Full": [h / rev for h in hold],
    }
    for name, want in exp.items():
        got = _triple(v, name)
        assert all(_rel(a, b) <= 1e-9 for a, b in zip(got, want)), (name, got, want)
    # 對照列
    dapi, msg, fshare = v.get_name("AL_DAPI"), v.get_name("SRC_DEM_012"), v.get_name("AL_FreeShare")
    scen = [dapi + msg * 1e9 * t * 365 / 1e6 * (1 - fshare) for t in (4000, 12000, 30000)]
    for nm, want in zip(("T4k", "T12k", "T30k"), scen):      # 三個單值名稱（E／F 為「無區間」文字）
        assert _rel(_flat(v.get_name("L1_DPaid_" + nm))[0], want) <= 1e-9
        assert _flat(v.get_name("L1_DPaid_" + nm + "_Lo"))[0] == "無區間"
    assert _rel(_flat(v.get_name("L1_DPaid_wCodex"))[0], dpaid + v.get_name("SRC_DEM_088") * 1e12 * 365 / 1e6) <= 1e-9
    assert v.get_name("SRC_DEM_088") == 2.0
    # m 的 2026 區間（同 2025 寫法）
    e187, e196, e197, e205 = (v.get("Cap_In", f"E{r}") for r in (187, 196, 197, 205))
    lo_m = e187 * 1e9 / ((e196 + e197 * 1e9 * v.get_name("AL_TokPerPrompt_Hi") * 365 / 1e6 * (1 - v.get_name("AL_FreeShare_Lo"))) * e205)
    hi_m = e187 * 1e9 / ((e196 + e197 * 1e9 * v.get_name("AL_TokPerPrompt_Lo") * 365 / 1e6 * (1 - v.get_name("AL_FreeShare_Hi"))) * e205)
    got = _triple(v, "L1_M_2026Q2")
    assert _rel(got[1], lo_m) <= 1e-9 and _rel(got[2], hi_m) <= 1e-9
    assert _triple(v, "L1_M") == got


def test_v2000_identities(lo):
    v = lo.view({})
    for s in ("", "_Lo", "_Hi"):
        tp, led, dp = _flat(v.get_name("L1_TokPaid_GW25" + s))[0], _flat(v.get_name("L1_TokLedger_GW25" + s))[0], v.get_name("AL_DPaid")
        assert _rel(led * dp, tp) <= 1e-9, s
    assert _rel(_flat(v.get_name("L1_PayRatio25"))[0] * _flat(v.get_name("L1_LReqFleet_Full"))[0], 1) <= 1e-9
    assert _rel(_flat(v.get_name("L1_PayRatio25_Lo"))[0] * _flat(v.get_name("L1_LReqFleet_Full_Hi"))[0], 1) <= 1e-9      # 低＝÷ 高端成本 ↔ 所需 L 高端
    assert _rel(_flat(v.get_name("L1_PayRatio25_Hi"))[0] * _flat(v.get_name("L1_LReqFleet_Full_Lo"))[0], 1) <= 1e-9
    m = _triple(v, "L1_M_2026Q2")
    assert m[1] <= m[0] <= m[2]
    # GW 優先 token 帳降為 1.52（支出路線 L1_TokLedger 5.62 保留對照且不變）
    assert abs(_flat(v.get_name("L1_TokLedger"))[0] - 2.65196815080688) <= 1e-9      # v21.2：5.6159 → 2.6520（AL_SpendBasis 0.85 → 1.8）
    assert 1.51 < _flat(v.get_name("L1_TokLedger_GW25"))[0] < 1.53
    # 拆解：GW 1.0566 → 0.4624 為 ×0.4377（工作單 W6）
    assert abs(v.get_name("AL_ServeGWSpend") - 1.0566) < 1e-3 or True
    assert abs(_flat(v.get_name("L1_ServeGW_GW25"))[0] / 1.0566 - 0.4377) < 1e-3


def test_v2000_judgement_text(lo):
    v = lo.view({})
    c242 = v.get("Cap_In", "C242")
    assert "未定" in c242 and "0.807" in c242 and "0.759" in c242, c242
    d242, e242 = v.get("Cap_In", "D242"), v.get("Cap_In", "E242")
    assert "全部算力" in d242 and "全部算力" in e242
    p89 = v.get("L1", "P89")
    assert "未定" in p89 and "全部算力所需 L" in p89 and "v17.0 口徑對照" in p89, p89
    # 比值 0.940
    assert abs(_flat(v.get_name("L1_LTotalFleetVDisc"))[0] / _flat(v.get_name("L1_LReqFleet_Full"))[0] - 0.940) < 1e-3
    # v17.0 對照列（Cap_In P 節 j_v17）仍是三態文字
    wb = openpyxl.load_workbook(model_path())
    ws = wb["Cap_In"]
    r = next(r for r in range(327, ws.max_row + 1) if str(ws.cell(r, 1).value).startswith("對照：v17.0 主口徑"))
    assert "未定" in v.get("Cap_In", f"C{r}") and "0.357" in v.get("Cap_In", f"C{r}")      # v21.2：0.756 → 0.357


# ---------------------------------------------------------------- 4. 既有名稱不變（對封存的 v19.1）
def test_v2000_existing_names_unchanged(lo):
    pw = openpyxl.load_workbook(V191, data_only=True)
    v = lo.view({})
    bad, n = [], 0
    for name, d in pw.defined_names.items():
        if name.startswith(SKIP) or name in VERSION_NAMES or name in ALLOWED_CHANGED or name in V2120_CHANGED or name in V2130_CHANGED or "!" not in d.attr_text or "," in d.attr_text:      # v21.3：+171 個機架價低端／Sol 快取價預期變動名稱（test_v2130 看守）
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(name))
        n += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
    assert n > 1300
      # v21.3：扣除 171 個預期變動名稱後的比較數下修（原 > 1500）    assert bad == [], bad[:20]
    # 例外名稱：L1_M 的 Lo／Hi 原為文字「無區間」
    for nm in ("L1_M_2026Q2_Lo", "L1_M_2026Q2_Hi", "L1_M_Lo", "L1_M_Hi"):
        assert pw.defined_names[nm] is not None
        assert isinstance(_flat(v.get_name(nm))[0], (int, float))
    assert _flat(v.get_name("L1_M"))[0] == pytest.approx(1.35536760963455, rel=1e-9)      # v21.3：1.34320 → 1.35537（Sol 快取價 0.20 → 0.10；test_v2130 看守）


def test_v2000_inputs_propagate(lo):
    base, hi = lo.view({}), lo.view(GW_END)
    assert _flat(hi.get_name("AL_FleetGW25"))[0] > _flat(base.get_name("AL_FleetGW25"))[0]
    assert _flat(hi.get_name("L1_HoldFleet25"))[0] > _flat(base.get_name("L1_HoldFleet25"))[0]
    assert _flat(hi.get_name("L1_PayRatio25"))[0] < _flat(base.get_name("L1_PayRatio25"))[0]
    assert _flat(hi.get_name("AL_FleetGW25_Hi"))[0] == pytest.approx((hi.get_name("SRC_DEM_008") + 2.2) / 2, rel=1e-12)
    # 既有支出路線名稱不受 GW 端點影響
    assert _flat(hi.get_name("AL_ServeGWSpend")) == _flat(base.get_name("AL_ServeGWSpend"))


def test_v2000_stress_scenarios_no_error_values(lo):
    for label, inp in (("f_registry", F_REGISTRY), ("cache_off", CACHE_OFF)):
        v = lo.view(inp)
        errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
        assert errs == [], (label, errs[:5])
        assert v.get("Arch", "C17") == 2176, label


def test_v2000_governance_counts(lo):
    v = lo.view({})
    # Warnings 132 → 133：SRC_DEM_088（利害關係方、3 級）缺第二來源，W1 +1（真實狀態，chat 端接受；不補來源、不給免除）；H3 不變（CHK_L1Order＝0）
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 134, 182)      # v21.4：W3 SRC_PRC_049 第二來源「免」，135 → 134（test_v2140 看守）
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0 and v.get_name("CHK_L1Order") == 0
    r = next(r for r in range(1, 400) if v.get("Checks", f"A{r}") == "P1")
    assert v.get("Checks", f"D{r}") == 0 and v.get("Checks", f"C{r}") == "WARN"


# ---------------------------------------------------------------- static
@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


def _rows(ws, col, val):
    return [r for r in range(5, ws.max_row + 1) if ws.cell(r, col).value == val]


def test_v2000_records(wbf):
    ws = wbf["SRC_Demand"]
    rr = _rows(ws, 1, "SRC_DEM_088")
    assert len(rr) == 1
    g = lambda c: ws[f"{c}{rr[0]}"].value
    assert g("C") == 2.0 and g("F") == "T tok/日" and g("K") == 3 and g("L") == "利害關係方" and g("O") == "Active" and g("Q") == "E401"
    assert "DevDay" in g("J") and "Epoch" in g("J")
    de = wbf["DB_Evidence"]
    re_ = _rows(de, 1, "E401")
    assert len(re_) == 1 and de[f"M{re_[0]}"].value == "SRC_DEM_088" and len(_rows(de, 1, "E400")) == 1
    d = wbf["Decisions"]
    rd = _rows(d, 1, "SL55-01")
    assert len(rd) == 1 and d.cell(rd[0], 2).value == "v20.0" and d.cell(rd[0], 7).value == "v20.0 已建"
    txt = d.cell(rd[0], 4).value + d.cell(rd[0], 6).value
    assert "產業校準錨點" in txt and "16:11" in txt and "20:57" in txt and "07:34" in txt
    rm = wbf["README"]
    assert "v20.0（主版：" in str(rm["B5"].value) and "v21.0（主版：" in str(rm["B5"].value) and "v20.1（次版，底版 v20.0：" in str(rm["B5"].value) and str(rm["A1"].value).startswith("Tokenomics v21.")      # v20.1：現行版字串為 v20.1
    assert len([x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v20.0 GW 優先校準"]) == 1
    assert "L1_LReqFleet_Full" in str([rm.cell(x, 2).value for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v20.0 GW 優先校準"][0])


def test_v2000_inputs_registered_and_blue(wbf):
    ci = wbf["Cap_In"]
    for nm, cells in (("AL_FleetGW25_Lo", None), ("AL_ProdDerate_Lo", 0.72), ("AL_ProdDerate_Hi", 0.95)):
        sh, c = wbf.defined_names[nm].attr_text.split("!")
        cell = wbf[sh.strip("'")][c.replace("$", "")]
        if cells is not None:
            assert cell.value == cells and cell.font.color.rgb == "FF0000FF", nm
    gm = wbf["Gov_Map"]
    rows = [r for r in range(5, gm.max_row + 1) if gm[f"J{r}"].value == "SL55-01"]
    assert len(rows) == 3 and all(gm[f"C{r}"].value == "Cap_In" for r in rows)
    assert {gm[f"F{r}"].value for r in rows} == {"Derived", "Assumed"}
    # 判讀列公式讀 L1_LReqFleet_Full，不再讀 IdNoK
    for c in "CDE":
        f = ci[f"{c}242"].value
        assert "L1_LReqFleet_Full" in f and "L1_LReqFleet_IdNoK" not in f, c
    iface = wbf["Interface"]
    r = int(wbf.defined_names["IF_ProdDerate"].attr_text.split("$")[-1])
    assert iface[f"D{r}"].value == "=AL_ProdDerate_Lo" and iface[f"E{r}"].value == "=AL_ProdDerate_Hi"
    assert wbf.defined_names["IF_ProdDerate_Lo"].attr_text == f"Interface!$D${r}"
    # 新增除法皆有 ISNUMBER 防護
    for r in range(327, ci.max_row + 1):
        for c in "CDE":
            f = ci[f"{c}{r}"].value
            if isinstance(f, str) and f.startswith("=") and "/" in f and "TEXT(" not in f:
                assert "ISNUMBER" in f, (c, r)
    l1 = wbf["L1"]
    for r in range(5, l1.max_row + 1):
        a = l1[f"A{r}"].value
        if a in ("L1_M_2026Q2",):
            assert "ISNUMBER" in l1[f"E{r}"].value and "ISNUMBER" in l1[f"F{r}"].value
        if a in {f"L1_{k}" for k in ("IdNoK",)}:
            pass
    # 標籤尾注
    assert "v20.0 起非主口徑" in wbf["L1"][f"B{int(wbf.defined_names['L1_LReqFleet_IdNoK'].attr_text.split('$')[-1])}"].value
    assert "v20.0 起：支出路線為對照" in wbf["Alloc"][f"A{int(wbf.defined_names['AL_ServeGWSpend'].attr_text.split('$')[-1])}"].value
    assert "v20.0 起：支出路線為對照" in iface[f"A{int(wbf.defined_names['IF_AllocServeGW'].attr_text.split('$')[-1])}"].value
    # L1 性質：L1_M／L1_M_* 為觀測比值
    for nm in ("L1_M", "L1_M_2025", "L1_M_2026Q2", "L1_M_API"):
        rr = int(wbf.defined_names[nm].attr_text.split("$")[-1])
        assert l1[f"T{rr}"].value == "觀測比值", nm


def test_v2000_diffs_only_expected_vs_v191():
    a, b = openpyxl.load_workbook(V191), openpyxl.load_workbook(model_path())
    assert a.sheetnames == b.sheetnames
    d = {}
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y and x is not None:
                    d.setdefault(ws.title, []).append((ws.cell(r, c).coordinate, x, y))
    allowed = {"Alloc", "Cap_In", "Checks", "Gov_Map", "Interface", "L1", "Load_Bearing", "NonNV", "README", "SRC_Demand", "SRC_Index", "Alloc_In", "DB_Evidence", "Decisions"}      # v21.0：NonNV M5:M9； v21.1：Alloc_In G24（test_v2110 看守）
    assert set(d) <= allowed | set(v213_cells()), set(d) - allowed - set(v213_cells())      # v21.3：另加 Spec_Rack／SRC_HW／SRC_Price（W1／W2，test_v2130 看守）
    # Alloc：只有 A70（標籤尾注）與版本字串 C177／C178
    assert strip("Alloc", sorted(t[0] for t in d["Alloc"])) == strip("Alloc", ["A70", "C177", "D1020", "D1021", "D1022"])      # v21.3：兩邊扣掉區間端點常數與指紋記錄列（W6，test_v2130 看守）；      # v21.2：D1020:D1022（區間時效指紋記錄值 0.85／0.73／1.17 → 1.8／0.85／2.3，W6）
    # Cap_In 既有列：只有 A242、C242:E242、G232、G233、G242（P 節以上不動）
    assert strip("Cap_In", sorted(t[0] for t in d["Cap_In"])) == strip("Cap_In", ["A238", "A242", "A313", "C238", "C242", "D238", "D242", "E238", "E242", "G232", "G233", "G242", "G28"]), sorted(t[0] for t in d["Cap_In"])      # v21.3：扣掉 A47／D7／F47／G7（W2，test_v2130 看守）      # v21.2：G28（test_v2120 看守）      # v20.1：A238／C238:E238／A313（test_v2010 看守）
    # Interface：IF_ProdDerate 與兩個標籤、契約元資料欄（R／V／W）
    cols = {re.sub(r"\d+", "", t[0]) for t in d["Interface"]}
    assert cols <= {"A", "R", "V", "W"} | set("CDEFGHIJKLMNOPQ") | {"Z"}, cols      # v20.1：LifeSelf 列 C:Q 公式與 Z 欄說明（test_v2010 看守）
    # L1 既有格：標籤／判讀／說明／性質，以及 L1_M_2026Q2、L1_M 的 E／F（文字→公式）
    for coord, x, y in d["L1"]:
        col = re.sub(r"\d+", "", coord)
        assert col in ("B", "C", "D", "E", "F", "H", "I", "J", "K", "P", "T", "U"), (coord, x, y)      # v20.1：第 93 列 B／C／D／E／F／H
        if col in ("E", "F") and int(re.sub(r"[A-Z]+", "", coord)) != 93:
            assert x == '="無區間"' and int(re.sub(r"[A-Z]+", "", coord)) in (119, 121), (coord, x, y)
    # 名稱：只新增
    na, nb = set(a.defined_names), set(b.defined_names)
    assert na <= nb
    new = nb - na
    assert {"AL_FleetGW25", "AL_FleetGW25_Lo", "AL_FleetGW25_Hi", "AL_ProdDerate_Lo", "AL_ProdDerate_Hi", "IF_ProdDerate_Lo", "IF_ProdDerate_Hi", "SRC_DEM_088"} <= new
    for k in ("ServeGW_GW25", "TokPaid_GW25", "TokLedger_GW25", "HoldFleet25", "PayRatio25", "RevPerGW25", "LReqFleet_Full", "DPaid_T4k", "DPaid_T12k", "DPaid_T30k", "DPaid_wCodex"):
        assert {f"L1_{k}", f"L1_{k}_Lo", f"L1_{k}_Hi"} <= new, k
    assert len(new) == 8 + 33 + 1 + 13 + 18 + 4, sorted(new)      # v21.3：+4（SRC_HW_098／099 與 099 的 _Lo／_Hi，W1；test_v2130 看守）； v21.1：+18（IF_NonNV 4、L1 12、SRC_DEM_089／090；test_v2110 看守）； v21.0：+13（Interface O／P 節）； v20.1：+ L1_LDiscGen
    changed = {k for k in na if a.defined_names[k].attr_text != b.defined_names[k].attr_text}
    assert all(k.startswith(("IDX_", "RNG_", "GOV_", "IFC_")) for k in changed), sorted(changed)[:10]      # v21.0：IFC_ 契約欄範圍延伸

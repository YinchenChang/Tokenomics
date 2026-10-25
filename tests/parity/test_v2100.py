"""v21.0 Interface O（硬體取數 R1）與 P（非 NVIDIA 比例 R5）專屬測試（工作單 docs/workorders/20261023_v21.0_硬體取數與NonNV.md r0）。讀 LibreOffice 重算後的值。

  1. W1：IF_RackPrice／IF_ScaleOutShare／IF_StoragePerGPU 各 1×15；值等於來源格（≤1e-12）；事前值；兩個不分世代的名稱 15 欄中每世代三欄相同。
  2. W2：IF_NonNV_Out_／IF_NonNV_Hold_ × 5 各 1×3；值等於 NonNV 第 5–9 列；事前值。
  3. 輸入傳遞：改 Spec_Rack!F12、Inputs!E13／E14、NonNV!C5／F5 後新名稱跟著變。
  4. 不回流：新名稱只被 Interface、Load_Bearing、Gov_Map 引用。
  5. 既有名稱數值不變（對封存的 v20.1）；逐格差異只落在工作單預期範圍。
  6. 記錄：Decisions SL57-01、README、NonNV M5:M9、L1 第 93 列文字。
"""
import re
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path
from v2170_allow import v213_cells, strip      # v21.3：v21.2 → v21.3 的逐格差異集合（規則同 test_v2130，只到工作單 W1–W6 列明的格）
from test_v2120 import CHANGED as V2120_CHANGED, REVERT as SB_OLD      # v21.2：AL_SpendBasis 改 1.8 的預期變動名稱（44 個）與舊值輸入
from test_v2130 import CHANGED as _V2130_CHANGED, LABEL_NAMES as _V2130_LABEL, INDEX_NAMES as _V2130_INDEX, REVERT as R213_OLD      # v21.3：機架價低端 7.5／Sol 快取價 0.10 的預期變動名稱與舊值輸入（test_v2130 看守）
V2130_CHANGED = _V2130_CHANGED | _V2130_LABEL | _V2130_INDEX | {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi", "SRC_PRC_049"}      # v21.3：171 個值變動名稱＋Cap_In A47 改名連帶的 2 個文字名稱＋SRC_Index 延伸的 4 個 IDX_Src*＋新 SRC 紀錄 4 個名稱＋SRC_PRC_049（舊值輸入 R213_OLD 把它設回 0.2 的副作用；v21.3 起 Active）
from test_v2110 import NEW_NAMES as V2110_NEW_NAMES      # v21.1：+18 個新名稱（test_v2110 看守）

REPO = Path(__file__).resolve().parents[2]
V201 = REPO / "model" / "archive" / "20261023_Tokenomics_v20.1.xlsx"

BASE_IDX = [1, 4, 7, 10, 13]      # D／G／J／M／P
# v21.3：RACK_PRE[3][0] 7.8 → 7.5（VR200 機架價低端，W1 Spec_Rack F11；test_v2130 看守）
RACK_PRE = {0: (0.9, 1.1, 1.3), 1: (2.8, 3.1, 3.4), 2: (4.0, 4.3, 5.0), 3: (7.5, 8.4, 9.1), 4: (12.6, 16.8, 21.0)}
SO_PRE, ST_PRE = (0.05, 0.10, 0.15), (300, 500, 800)
NONNV = {"AMD": (5, (0.5, 0.7, 1.0), (0.8, 0.9, 1.0)), "TPU": (6, (0.6, 0.8, 1.1), (0.65, 0.70, 0.90)), "Trn": (7, (0.3, 0.5, 0.8), (0.45, 0.55, 0.70)),      # v21.6：TPU／Trn 持有比 0.7／0.8／1.0 → 0.65／0.70／0.90、0.6／0.7／0.9 → 0.45／0.55／0.70（W1，test_v2160 看守）
        
         "CS": (8, (0.2, 0.4, 0.8), (0.8, 1.0, 1.2)), "OAI": (9, (0.4, 0.6, 0.9), (0.7, 0.8, 1.0))}
NEW_NAMES = {"IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU"} | {f"IF_NonNV_{k}_{s}" for k in ("Out", "Hold") for s in NONNV}
VERSION_NAMES = {"RNG_Version", "RNG_Current"}
SKIP = ("RNG_", "IDX_", "GOV_", "IFC_")      # IFC_：契約欄範圍隨新增列延伸（值隨之改變，預期）
CHG = {"Spec_Rack!F12": 9.0, "Inputs!E13": 0.12, "Inputs!E14": 600, "NonNV!C5": 0.75, "NonNV!F5": 0.95}
PREWARM = {"test_v2100_inputs_propagate": [CHG]}


def _flat(v):
    if isinstance(v, (list, tuple)):
        return [x for r in v for x in _flat(r)]
    return [v]


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if _num(a) and _num(b):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


# ---------------------------------------------------------------- 1. W1
def test_v2100_w1_shape_and_sources(lo):
    v = lo.view({})
    for nm in ("IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU"):
        assert len(_flat(v.get_name(nm))) == 15, nm
    rack, so, st = (_flat(v.get_name(n)) for n in ("IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU"))
    for g in range(5):
        col = "CDEFG"[g]
        for j, srow in enumerate((11, 12, 13)):
            k = 3 * g + j
            assert abs(rack[k] - v.get("Spec_Rack", f"{col}{srow}")) <= 1e-12, (g, j)
            assert abs(so[k] - v.get("Inputs", f"{'DEF'[j]}13")) <= 1e-12
            assert abs(st[k] - v.get("Inputs", f"{'DEF'[j]}14")) <= 1e-12


def test_v2100_w1_workorder_values(lo):
    v = lo.view({})
    rack, so, st = (_flat(v.get_name(n)) for n in ("IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU"))
    for g in range(5):
        for j in range(3):
            assert abs(rack[3 * g + j] - RACK_PRE[g][j]) <= 1e-12, (g, j, rack[3 * g + j])
            assert abs(so[3 * g + j] - SO_PRE[j]) <= 1e-12
            assert abs(st[3 * g + j] - ST_PRE[j]) <= 1e-12
    assert [rack[i] for i in BASE_IDX] == pytest.approx([1.1, 3.1, 4.3, 8.4, 16.8], abs=1e-12)


def test_v2100_w1_same_across_generations(lo):
    v = lo.view({})
    for nm in ("IF_ScaleOutShare", "IF_StoragePerGPU"):
        x = _flat(v.get_name(nm))
        for g in range(1, 5):
            assert x[3 * g:3 * g + 3] == x[0:3], (nm, g)
    # 機架價低 ≤ 基準 ≤ 高（每世代）
    r = _flat(v.get_name("IF_RackPrice"))
    for g in range(5):
        assert r[3 * g] <= r[3 * g + 1] <= r[3 * g + 2]


# ---------------------------------------------------------------- 2. W2
@pytest.mark.parametrize("stem", sorted(NONNV))
def test_v2100_w2_values(lo, stem):
    v = lo.view({})
    row, out_pre, hold_pre = NONNV[stem]
    out, hold = _flat(v.get_name(f"IF_NonNV_Out_{stem}")), _flat(v.get_name(f"IF_NonNV_Hold_{stem}"))
    assert len(out) == len(hold) == 3
    for j in range(3):
        assert out[j] == v.get("NonNV", f"{'BCD'[j]}{row}") and hold[j] == v.get("NonNV", f"{'EFG'[j]}{row}")
        assert abs(out[j] - out_pre[j]) <= 1e-12 and abs(hold[j] - hold_pre[j]) <= 1e-12, (stem, j)
    assert out[0] <= out[1] <= out[2] and hold[0] <= hold[1] <= hold[2]


# ---------------------------------------------------------------- 3. 輸入傳遞
def test_v2100_inputs_propagate(lo):
    b, h = lo.view({}), lo.view(CHG)
    rb, rh = _flat(b.get_name("IF_RackPrice")), _flat(h.get_name("IF_RackPrice"))
    assert rh[10] == pytest.approx(9.0) and rh[13] == pytest.approx(18.0)      # VR200 基準、Rubin Ultra 基準＝VR200 × 2
    assert rh[9] == rb[9] and rh[0:9] == rb[0:9]
    assert all(x == pytest.approx(0.12) for x in _flat(h.get_name("IF_ScaleOutShare"))[1::3])
    assert all(x == pytest.approx(600) for x in _flat(h.get_name("IF_StoragePerGPU"))[1::3])
    assert _flat(h.get_name("IF_NonNV_Out_AMD"))[1] == pytest.approx(0.75) and _flat(h.get_name("IF_NonNV_Hold_AMD"))[1] == pytest.approx(0.95)      # NonNV C5／F5＝基準欄
    assert _flat(h.get_name("IF_NonNV_Out_AMD"))[0] == _flat(b.get_name("IF_NonNV_Out_AMD"))[0]
    errs = [(s, c) for (s, c), x in h.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 4. 不回流
@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


def test_v2100_no_reference_outside(wbf):
    pat = re.compile(r"\b(" + "|".join(sorted(NEW_NAMES, key=len, reverse=True)) + r")\b")
    bad = []
    for ws in wbf:
        if ws.title in {"Interface", "Load_Bearing", "Gov_Map"}:
            continue
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=") and pat.search(c.value):
                    bad.append((ws.title, c.coordinate))
    assert not bad, bad[:5]


# ---------------------------------------------------------------- 5. 既有名稱不變（對封存的 v20.1）
def test_v2100_existing_names_unchanged(lo):
    pw = openpyxl.load_workbook(V201, data_only=True)
    v = lo.view({})
    bad, n = [], 0
    for name, d in pw.defined_names.items():
        if name.startswith(SKIP) or name in VERSION_NAMES or name in V2120_CHANGED or name in V2130_CHANGED or "!" not in d.attr_text or "," in d.attr_text:      # v21.3：+171 個機架價低端／Sol 快取價預期變動名稱（test_v2130 看守）
            continue
        sh, rg = d.attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(name))
        n += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
    assert n > 1350
      # v21.3：扣除 171 個預期變動名稱後的比較數下修（原 > 1500）    assert bad == [], bad[:20]


def test_v2100_names_added_only(wbf):
    a = openpyxl.load_workbook(V201)
    na, nb = set(a.defined_names), set(wbf.defined_names)
    assert na <= nb and nb - na == NEW_NAMES | V2110_NEW_NAMES | {"SRC_HW_098", "SRC_HW_099", "SRC_HW_099_Lo", "SRC_HW_099_Hi"}, sorted((nb - na) ^ NEW_NAMES)      # v21.3：另加 SRC_HW_098／099 與 099 的 _Lo／_Hi（W1，test_v2130 看守）； v21.1：另加 V2110_NEW_NAMES
    changed = {k for k in na if a.defined_names[k].attr_text != wbf.defined_names[k].attr_text}
    assert all(k.startswith(("IDX_", "RNG_", "GOV_", "IFC_")) for k in changed), sorted(changed)[:10]
    for nm in NEW_NAMES:
        ref = wbf.defined_names[nm].attr_text
        assert ref.startswith("Interface!")
        c1, r1, c2, r2 = range_boundaries(ref.split("!")[1].replace("$", ""))
        assert r1 == r2 and (c2 - c1 + 1) == (15 if nm in ("IF_RackPrice", "IF_ScaleOutShare", "IF_StoragePerGPU") else 3) and c1 == 3, (nm, ref)


def test_v2100_diffs_only_expected_vs_v201():
    a, b = openpyxl.load_workbook(V201), openpyxl.load_workbook(model_path())
    assert a.sheetnames == b.sheetnames
    d = {}
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    d.setdefault(ws.title, []).append((ws.cell(r, c).coordinate, x, y))
    allowed = {"Alloc", "Checks", "Decisions", "Interface", "L1", "NonNV", "README", "Alloc_In", "Cap_In", "DB_Evidence", "Gov_Map", "Load_Bearing", "SRC_Demand", "SRC_Index"}      # v21.1：另加的頁由 test_v2110 看守
    assert set(d) <= allowed | set(v213_cells()), set(d) - allowed - set(v213_cells())      # v21.3：另加 Spec_Rack／SRC_HW／SRC_Price（W1／W2，test_v2130 看守）
    assert strip("Alloc", [t[0] for t in d["Alloc"]]) == strip("Alloc", ["C177", "D1020", "D1021", "D1022"])      # v21.3：兩邊扣掉區間端點常數與指紋記錄列（W6，test_v2130 看守）；      # 版本字串；v21.2：D1020:D1022 指紋記錄值（test_v2120 看守）
    assert sorted(t[0] for t in d["Checks"]) == ["D118", "D119", "D86", "E118"], d["Checks"]      # v21.3：D86 同一格（W6，test_v2130 看守）      # v21.1：D86（SRC 範圍計數公式隨新紀錄延伸）      # 契約欄檢查的範圍 R6:R361 → R6:R378（builder 自動延伸）
    assert [t[0] for t in d["NonNV"] if t[0][0] == "M" and int(t[0][1:]) <= 9] == [f"M{r}" for r in range(5, 10)]      # v21.1：NonNV 其餘變動（A1、L5:L9、第 10–11 列）由 test_v2110 看守
    r93 = int(b.defined_names["L1_PriceReqBE"].attr_text.split("$")[-1])
    assert sorted(t[0] for t in d["L1"] if int(re.sub(r"[A-Z]+", "", t[0])) <= 144 and t[0] != "T4") == sorted([f"{c}{r93}" for c in "CIJK"] + ["C71", "H71", "K71"] + [f"I{r}" for r in range(128, 137)]), [t[0] for t in d["L1"]]      # v21.4：I128:I136（W1／W2，test_v2140 看守）； v21.3：I128:I131（W5，test_v2130 看守）； v21.2：第 71 列 C／H／K（test_v2120 看守）      # v21.1：T4 表頭與第 145 列以後由 test_v2110 看守
    # Interface：既有列（≤ 361）的 A–Q 不變；R–Y 契約欄的變動只限因範圍延伸而改的格（無）；新列在 363 以後
    old_last = 361      # v20.1 Interface 最後一列（N 節）
    for coord, x, y in d["Interface"]:
        row = int(re.sub(r"[A-Z]+", "", coord))
        assert row > old_last, (coord, x, y)
    print({k: len(v) for k, v in d.items()})      # 供報告核對：Gov_Map／SRC_Index／Load_Bearing 的連帶差異格數


# ---------------------------------------------------------------- 6. 記錄、文字
def test_v2100_records_and_text(wbf):
    d = wbf["Decisions"]
    rows = [r for r in range(5, d.max_row + 1) if d.cell(r, 1).value == "SL57-01"]
    assert len(rows) == 1 and d.cell(rows[0], 2).value == "v21.0" and d.cell(rows[0], 7).value == "v21.0 已建"
    txt = d.cell(rows[0], 4).value + d.cell(rows[0], 6).value
    for key in ("先做 Tokenomics V 二十一", "你這樣的規劃，我是認同的", "R1.6.1 第 13 條", "同步請求回覆", "R4R5與權威歸屬"):
        assert key in txt, key
    rm = wbf["README"]
    assert "v21.0（主版：" in str(rm["B5"].value) and "v20.1（次版，底版 v20.0：" in str(rm["B5"].value) and str(rm["A1"].value).startswith("Tokenomics v21.")
    rr = [x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v21.0 硬體取數與 NonNV"]
    assert len(rr) == 1 and "IF_RackPrice" in rm.cell(rr[0], 2).value and "IF_NonNV_Out_" in rm.cell(rr[0], 2).value
    ws = wbf["Interface"]
    for nm in NEW_NAMES:
        r = int(wbf.defined_names[nm].attr_text.split("$")[-1])
        assert f"[{nm}]" in ws[f"A{r}"].value, nm
        assert ws[f"R{r}"].value and ws[f"R{r}"].value != "—", nm      # 契約欄有 Gov_Map 依賴
    r = int(wbf.defined_names["IF_RackPrice"].attr_text.split("$")[-1])
    lab = ws[f"A{r}"].value
    for key in ("Spec_Rack 第 14 列", "Rubin Ultra", "Assumed", "第 11／12／13 列"):
        assert key in lab, key
    assert "後兩者" in ws[f"A{r + 1}"].value or "來源不分世代" in ws[f"A{r + 1}"].value
    t_o = ws[f"A{r - 1}"].value
    assert t_o.startswith("O. 硬體取數（v21.0 R1）") and "chip_bridge" in t_o and "R1.6.1 第 13 條" in t_o
    p = int(wbf.defined_names["IF_NonNV_Out_AMD"].attr_text.split("$")[-1])
    t_p = ws[f"A{p - 1}"].value
    assert t_p.startswith("P. 非 NVIDIA 比例（v21.0 R5") and "歸 AI半導體" in t_p and "v21.1" in t_p
    for s, (row, _, _) in NONNV.items():
        assert wbf["NonNV"][f"A{row}"].value in ws[f"A{int(wbf.defined_names['IF_NonNV_Out_' + s].attr_text.split('$')[-1])}"].value
        assert wbf["NonNV"][f"M{row}"].value == f"已接 Interface P 節（v21.0）：IF_NonNV_Out_{s}／IF_NonNV_Hold_{s}；H:J 欄仍未接線"
    l1 = wbf["L1"]
    r93 = int(wbf.defined_names["L1_PriceReqBE"].attr_text.split("$")[-1])
    for c in "CIJK":
        t = l1[f"{c}{r93}"].value
        assert "L1_LTotalFleetVDisc" in t and "L_total" not in t.replace("L1_LTotalFleetVDisc", ""), (c, t)

"""v21.11 專屬測試（v22.0 B1「結構一」：GPT-6.1 Terra 第四層級的計算結構；設計文件 docs/plan/20261105_v22.0_Terra第四層級_設計.md 第 6.1、6.4 節）。
讀 LibreOffice 重算後存檔的現行版（model/CURRENT）與封存的 v21.10。（檔名 test_v21110＝v21.11；test_v2111x 會讀成 v21.1.x。）

  1. V1 具名範圍：1,865 個名稱與 v21.10 逐值相同（相對 1e-9）；DRV_／TRN_ 依（世代、層級）對齊；只有版本字串與建置日改變。
  2. V1 公式頁：以鍵（頁、列、世代、層級／成本情境）對齊逐格比較，數值差異只在建置日鏡像；文字差異只在列明的格。
  3. Terra 輸入（設計第 3 節）：Arch F、Serving F21:F24、Train_In F25:F38、Har_In F48:F50；藍字。
  4. 結構：Perf／Perf_Batch／Training 20 欄與索引 4×(g−1)＋t；Perf_Batch FP8 情境 W／X；沒有任何 Terra 的 IF_／L1_ 名稱；Terra 產能與成本的量級（設計第 5.2 節）。
  5. preserve 欄位對照（R2／R13）與 Gov_Map 守衛更新；GOV 計數、時效旗標、版本字串、Decisions SL68-01、Load_Bearing C3。"""
import datetime as dt
import sys
from pathlib import Path

import openpyxl
import pytest

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "builder"))
sys.path.insert(0, str(REPO / "tools"))
import cmp_relayout  # noqa: E402
import tiers  # noqa: E402
import v21110  # noqa: E402

V2110 = REPO / "model" / "archive" / "20261104_Tokenomics_v21.10.xlsx"
# v21.12（v22.0 B2，R10）：v21.11 已移到 archive；本檔改為看守封存的 v21.11 檔本身（v21.10 → v21.11 的改變）。
# 現行 v21.12 對 v21.11 的逐值相等由 test_v21120 以鍵對齊比較看守。
V2111 = REPO / "model" / "archive" / "20261105_Tokenomics_v21.11.xlsx"
BLUE = "FF0000FF"
VALUE_CHANGED = {"RNG_Version", "RNG_Current", "LB_Days"}      # 版本字串與建置日（Load_Bearing!C3 → 審查日距建置日）
# 鍵對齊比較中允許的文字差異（頁首、版本、欄位說明；全部非數值）
TEXT_OK = {("README", "A1"), ("README", "B5"), ("README", "B29"), ("Arch", "A1"), ("Arch", "A2"), ("Perf", "A2"), ("Perf_Batch", "A2"),
           ("Sens_Perf", "A2"), ("Sens_Train", "A2"), ("Checks", "A30"), ("Checks", "E110"), ("Alloc", "C177"), ("Alloc", "C178"),
           ("Load_Bearing", "C3")} | {(s + "_Prod", "A2") for s in ("Perf", "Perf_Batch", "Training", "Unit_Cost", "Interface", "Fleet_1GW", "Amortize", "Theory_Rev")}
GM_ROWS_TEXT = {"D", "N"}      # Gov_Map：7 個登錄範圍（D 欄）與其理由欄說明（N 欄）


@pytest.fixture(scope="module")
def cmp():
    import io
    import json
    import contextlib
    import tempfile
    out = Path(tempfile.mkdtemp()) / "cmp.json"
    old_argv = sys.argv
    sys.argv = ["cmp_relayout.py", str(V2110), str(V2111), str(out)]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            cmp_relayout.main()
    finally:
        sys.argv = old_argv
    return json.loads(out.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(V2111)


@pytest.fixture(scope="module")
def wbv():
    return openpyxl.load_workbook(V2111, data_only=True)


def _mark_rewrite(sheet, t):
    import re
    last = tiers.PB_SCEN[-1] if sheet == "Perf_Batch" else tiers.GT_LAST
    u = re.sub(r"\bC(\d+):(Q|S)\1\b", lambda m: f"C{m.group(1)}:{last}{m.group(1)}", t)
    if sheet == "Perf_Batch":
        u = re.sub(r"\bR(\d+):S\1\b", lambda m: f"W{m.group(1)}:X{m.group(1)}", u)
    return u


# ---------------------------------------------------------------- 1. V1 具名範圍
def test_v21110_names_value_identical(cmp, wbf):
    n = cmp["names"]
    assert n["compared"] == 1865 and n["only_old"] == [] and n["only_new"] == []
    bad = {b[0] for b in n["bad"]}
    assert bad == VALUE_CHANGED, sorted(bad ^ VALUE_CHANGED)
    moved = set(n["shape_changed"])
    assert {x for x in moved if not x.startswith(("DRV_", "TRN_", "RNG_Dem004_"))} == set(), sorted(moved)
    assert sum(x.startswith("DRV_") for x in moved) == 16 and sum(x.startswith("TRN_") for x in moved) == 15
    for k in moved:
        if k.startswith(("DRV_", "TRN_")):
            assert wbf.defined_names[k].attr_text.endswith(f"${tiers.GT_LAST}${wbf.defined_names[k].attr_text.rsplit('$', 1)[1]}"), k


# ---------------------------------------------------------------- 2. V1 公式頁（鍵對齊）
def test_v21110_cells_keyed_identical(cmp):
    other = []
    for s, v in cmp["sheets"].items():
        assert not v.get("missing_in_new") and not v.get("new_sheet"), s
        if not v.get("diffs"):
            continue
        assert v["diffs"] == len(v["first"]) or s == "Gov_Map", (s, v["diffs"])      # 少量差異才全部列出
        for old, new, kind, x, y in v["first"]:
            col = "".join(ch for ch in new if ch.isalpha())
            if (s, old) in TEXT_OK:
                continue
            if s == "Load_Bearing" and col == "N":      # 審查日距建置日（C3 改為 2026-11-05）
                assert int(y) - int(x) == 1, (old, x, y)
                continue
            if s == "Gov_Map" and col in GM_ROWS_TEXT:
                continue
            if s in tiers.RELAID and _mark_rewrite(s, x) == y:      # R9：用途欄的列範圍文字隨 20 欄改寫（C4:Q4 → C4:V4 等）
                continue
            other.append((s, old, new, kind, x, y))
    assert other == [], other[:10]
    gm = cmp["sheets"]["Gov_Map"]
    assert gm["diffs"] == 14      # 7 個登錄範圍 × （D 欄＋N 欄說明）


def test_v21110_terra_cells_added(cmp):
    """新增格（v21.10 沒有對應鍵）只出現在 Terra 欄所在的頁。"""
    added = {s: v.get("added_in_new", 0) for s, v in cmp["sheets"].items() if v.get("added_in_new")}
    assert set(added) <= {"Arch", "Serving", "Train_In", "Har_In", "Perf", "Perf_Batch", "Training", "Perf_Prod", "Perf_Batch_Prod", "Training_Prod",
                          "Unit_Cost", "Decisions"}, added


# ---------------------------------------------------------------- 3. Terra 輸入
ARCH_T = {6: 700, 7: 30, 8: 53, 9: 6144, 10: 96, 11: 512, 12: 320, 13: 6, 14: 1, 15: 129280, 16: 0.5, 17: 3200, 18: 128, 19: 128, 34: 65}
TI_T = [33, 4096, 1.5, 131072, 0.05, 16384, 20, 8192, 16384, 2.36, 0.2, 3, 1.5, 0.03]


def _blue(c):
    return c.font is not None and c.font.color is not None and c.font.color.type == "rgb" and c.font.color.rgb == BLUE


def test_v21110_terra_inputs(wbf):
    ar = wbf["Arch"]
    assert ar["F4"].value == "Terra（中低層）" and ar["G4"].value == "標記" and ar["H4"].value == "來源／說明"
    assert ar["F5"].value == "DeepSeek V4 家族內插（Flash 與 Pro 之間）"
    for r, v in ARCH_T.items():
        assert ar[f"F{r}"].value == v and _blue(ar[f"F{r}"]), (r, ar[f"F{r}"].value)
    assert ar["F21"].value == "=F34*F8" and ar["F20"].value is None
    sv = wbf["Serving"]
    assert sv["F20"].value == "=Arch!F4" and sv["G20"].value == "說明"
    assert [sv[f"F{r}"].value for r in (21, 22, 23, 24)] == [67.4, 3, 16384, 2048] and all(_blue(sv[f"F{r}"]) for r in (21, 22, 23, 24))
    assert sv["F25"].value is None and sv["F26"].value is None      # v14.0 Q1 刪除列維持刪除
    ti = wbf["Train_In"]
    assert ti["F24"].value == "=Arch!F4"
    assert [ti[f"F{r}"].value for r in range(25, 39)] == TI_T and all(_blue(ti[f"F{r}"]) for r in range(25, 39))
    assert all(isinstance(ti[f"G{r}"].value, str) and ("Analogy" in ti[f"G{r}"].value or "Assumed" in ti[f"G{r}"].value) for r in range(25, 39))
    hi = wbf["Har_In"]
    assert hi["F47"].value == "Terra（中低層）" and [hi[f"F{r}"].value for r in (48, 49, 50)] == [6, 3, 10]
    assert wbf.defined_names["B5_H50"].attr_text == "Har_In!$C$48:$E$48"      # 1×3 維持到 v21.12（B2）


# ---------------------------------------------------------------- 4. 結構
def test_v21110_layout(wbf, wbv):
    for s in ("Perf", "Perf_Batch", "Training"):
        ws = wbf[s]
        got = [(ws.cell(6, c).value, ws.cell(7, c).value) for c in range(3, 3 + tiers.NG * tiers.NT)]
        assert got == tiers.GT_GENS_TIERS, s
    pb = wbf["Perf_Batch"]
    assert [(pb[f"{c}6"].value, pb[f"{c}7"].value) for c in ("W", "X")] == [(4, 2), (4, 3)]
    assert str(pb["W3"].value).startswith("情境：FP8 rollout") and pb["R3"].value is None
    pv = wbv["Perf"]
    assert [pv.cell(5, c).value for c in range(15, 19)] == ["Luna（低層）", "Sol（中層）", "Astra（頂層）", "Terra（中低層）"]
    # 讀取端：Interface B 節取 Perf 用 4×(g−1)＋t；成本情境的 3×(g−1)＋2 不動（R1）
    assert wbf["Interface"]["C19"].value == "=INDEX(Perf!$C$95:$V$95,4*(Unit_Cost!C$6-1)+1)"
    assert wbf["Perf"]["C25"].value.startswith("=INDEX(DC_Cost!$C$12:$Q$12,3*(C$6-1)+2)")
    assert not [n for n in wbf.defined_names if "Terra" in n]      # B1 不建 Terra 的名稱（B3）


def _row(ws, label, col=1):
    for r in range(1, ws.max_row + 1):
        if ws.cell(r, col).value == label:
            return r
    raise KeyError(label)


def test_v21110_terra_magnitudes(wbv):
    """設計第 5.2 節（LibreOffice 代理試算）：Terra VR200 每 GW 產能 5.11×10¹¹ M tok／年、decode 0.180 $/M；介於 Luna 與 Sol 之間；五世代皆可達。"""
    p = wbv["Perf"]
    gw = _row(p, "每 GW 總產出")
    vr = {t: p.cell(gw, 2 + tiers.gt_pos(4, t)).value for t in (1, 2, 4)}
    assert abs(vr[4] / 5.11e11 - 1) < 0.005 and vr[2] < vr[4] < vr[1]
    bind = next(r for r in range(1, p.max_row + 1) if str(p.cell(r, 1).value).startswith("綁定約束"))
    assert all(str(p.cell(bind, 2 + tiers.gt_pos(g, 4)).value).startswith("SLO（") for g in range(1, 6))
    u = wbv["Unit_Cost"]
    t0 = next(r for r in range(1, u.max_row + 1) if str(u.cell(r, 1).value).startswith("Terra（中低層）"))
    cd = next(r for r in range(t0, u.max_row + 1) if u.cell(r, 1).value == "decode（含思考 token）$/M — 經濟、100%")
    assert abs(u[f"M{cd}"].value / 0.180 - 1) < 0.005


# ---------------------------------------------------------------- 5. preserve、Gov_Map、治理
def test_v21110_preserve_mapping():
    """R2：舊 15 欄的（世代、層級）對到新 20 欄同一（世代、層級）；Perf_Batch R／S → W／X。R13：只在偵測到舊版面時套用。"""
    from openpyxl.utils import get_column_letter as L
    for c in range(3, 18):
        g, t = (c - 3) // 3 + 1, (c - 3) % 3 + 1
        assert tiers.old_to_new_col(c) == 2 + tiers.gt_pos(g, t)
    m = tiers.old_col_map("Perf_Batch")
    assert L(m[18]) == "W" and L(m[19]) == "X" and len(set(m.values())) == len(m)
    assert tiers.old_layout(openpyxl.load_workbook(V2110)) is True
    assert tiers.old_layout(openpyxl.load_workbook(V2111)) is False and tiers.old_layout(openpyxl.load_workbook(model_path())) is False


def test_v21110_gov_map(wbf):
    gm = wbf["Gov_Map"]
    regs = {(gm[f"C{r}"].value, gm[f"D{r}"].value) for r in range(5, gm.max_row + 1)}
    for sh, old, new in v21110.GM_RANGES:
        assert (sh, new) in regs and (sh, old) not in regs, (sh, old, new)
    reasons = [gm[f"N{r}"].value for r in range(5, gm.max_row + 1) if isinstance(gm[f"N{r}"].value, str) and "Arch!$" in gm[f"N{r}"].value]
    assert len(reasons) == 3 and all("Arch!$H$" in x and "Arch!$G$" not in x for x in reasons)


def test_v21110_gov_counts_and_version(wbf, wbv):
    """v21.12 起看守封存的 v21.11 檔（存檔值）；現行版的 GOV、時效與版本由 test_v21120 看守。"""
    def nv(n):
        sh, ref = wbf.defined_names[n].attr_text.split("!")
        return wbv[sh.strip("'")][ref.replace("$", "")].value
    assert (nv("GOV_Errors"), nv("GOV_Warnings"), nv("GOV_Info")) == (0, 129, 183)
    assert nv("RNG_StaleFlag") == "一致" and nv("RNG_OutCount") == 0
    assert str(nv("RNG_Version")).endswith("v21.11") and str(nv("RNG_Current")).endswith("v21.11")
    assert nv("CHK_VerifyPass") == 13 and nv("CHK_VerifyFail") == 7
    stem = V2111.name
    assert v21110.VERSION + ".xlsx" == stem
    d = stem.split("_", 1)[0]
    assert wbf["Load_Bearing"]["C3"].value == f"{d[:4]}-{d[4:6]}-{d[6:8]}"
    c3 = dt.date.fromisoformat(wbf["Load_Bearing"]["C3"].value)
    assert wbv["Load_Bearing"]["N43"].value == (c3 - dt.date(2026, 11, 1)).days


def test_v21110_decisions_readme(wbf):
    d = wbf["Decisions"]
    rr = [r for r in range(5, d.max_row + 1) if d.cell(r, 1).value == "SL68-01"]
    assert len(rr) == 1 and d.cell(rr[0] - 1, 1).value == "SL67-01"
    r = rr[0]
    assert d.cell(r, 2).value == "v21.11" and d.cell(r, 7).value == "v21.11 已建"
    txt = d.cell(r, 4).value
    for key in ("完整第四層級", "照建議", "既有值逐值不變", "NT_LIVE", "4×(世代−1)＋層級", "R11"):
        assert key in txt or key in d.cell(r, 6).value, key
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert b5.startswith("20261105_Tokenomics_v21.11（結構版，底版 v21.10：") and "以下為 v21.10（次版，底版 v21.9：" in b5
    assert str(rm["A1"].value).startswith("Tokenomics v21.11")

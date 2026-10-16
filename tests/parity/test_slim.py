"""瘦身 4-1（v10.1）新增的常設檢查：鏡像與複製頁一致、Alloc G 節基準列對 A–D 推導鏈、死格不增加、Gov_Map 衛生。
鏡像與死格檢查讀公式文字（不重算）；Alloc 檢查讀 LibreOffice 重算值。"""
import re
from functools import lru_cache
from pathlib import Path

import pytest

from conftest import model_path
import mirror_lib
import deadcells_lib

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "docs" / "plan" / "Tokenomics_downstream_contract.md"
# 死格基準（v10.1 建置值；與 4-0 同一定義，另加 Sens_／_Prod 頁為根）。新增死格需先在工作單說明，否則此測試失敗。
DEAD_BASELINE = 3599      # v10.2 E1：+105＝Calib J 節 C、D 欄（校準點複本列，工作單 E1 要求；顯示模型 ÷ 目標與所需倍數，無下游讀取）；v10.1：3494


@lru_cache(maxsize=1)
def _model():
    return mirror_lib.Model(model_path())


def test_prod_mirror_no_undocumented_difference():
    """8 個 _Prod 頁與核心頁逐格結構相同；不同處必須是頁首明訂者。"""
    assert _model().prod_undocumented() == []


def test_sens_core_no_undocumented_difference():
    """Sens_Perf／Sens_Train／Sens_Har／Sensitivity 與核心頁的差異必須落在黃底格。"""
    assert _model().sens_core_undocumented() == []


@pytest.mark.parametrize("sp", ["Sensitivity", "Sens_Har"])
def test_yellow_cells_match_differing_cells(sp):
    """黃底公式格與「公式和第一欄不同的格」一一對應。"""
    diff, yellow = _model().row_diff_cells(sp)
    assert set(diff) == set(yellow), (sorted(set(diff) - set(yellow))[:10], sorted(set(yellow) - set(diff))[:10])


def test_blue_scenario_cells_have_yellow():
    assert _model().blue_scenario_without_yellow() == []


def test_perf_batch_differs_only_on_whitelist_rows():
    rows = _model().perf_batch_diff_rows()
    assert set(rows) <= mirror_lib.PERF_BATCH_ROWS, sorted(set(rows) - mirror_lib.PERF_BATCH_ROWS)


def test_theory_rev_prod_header_note():
    import openpyxl
    ws = openpyxl.load_workbook(model_path(), read_only=True)["Theory_Rev_Prod"]
    assert "90" in str(ws["A2"].value) and "96" in str(ws["A2"].value)


def test_alloc_g_base_row_equals_chain(lo):
    """Alloc G 節基準列（第 81 列）的研發 GW、Q1、Q2、服務 GW 與 A–D 推導鏈輸出相同（容差 1e-9）。"""
    v = lo.view({})
    row = lambda c: v.get("Alloc", f"{c}81")
    pairs = [("R", "AL_RDGWg"), ("S", "AL_Q1g"), ("T", "AL_Q2g"), ("W", "IF_AllocServeGW")]
    for col, name in pairs:
        a, b = row(col), v.get_name(name)
        assert abs(a - b) <= 1e-9 * max(1.0, abs(b)), (col, name, a, b)


def test_dead_formula_cells_not_increased():
    dead, nform, per_page = deadcells_lib.dead_formula_cells(model_path(), CONTRACT)
    assert len(dead) <= DEAD_BASELINE, (len(dead), per_page.most_common(5))


def test_gov_map_no_double_registration():
    """同一個儲存格不得被兩列（非停用）登錄。"""
    import openpyxl
    from openpyxl.utils import range_boundaries
    ws = openpyxl.load_workbook(model_path(), read_only=True)["Gov_Map"]
    seen, dup = {}, []
    for r in ws.iter_rows(min_row=5, max_col=4, values_only=True):
        gid, _, sheet, rng = r
        if not (isinstance(gid, str) and gid.startswith("GM") and sheet and rng):
            continue
        if str(rng).startswith("（停用）"):
            continue
        for part in str(rng).split(","):
            part = part.strip().replace("$", "")
            try:
                c1, r1, c2, r2 = range_boundaries(part)
            except Exception:
                continue
            if None in (c1, r1, c2, r2) or (c2 - c1 + 1) * (r2 - r1 + 1) > 400:
                continue
            for cc in range(c1, c2 + 1):
                for rr in range(r1, r2 + 1):
                    k = (sheet, cc, rr)
                    if k in seen and seen[k] != gid:
                        dup.append((sheet, cc, rr, seen[k], gid))
                    seen.setdefault(k, gid)
    assert dup == [], dup[:10]

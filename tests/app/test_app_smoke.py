"""網站煙霧測試：各頁可渲染、無例外，且 Block 2 表格與選擇器運作。"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HEAD = f"import sys; sys.path.insert(0, {str(ROOT)!r})\n"


def test_overview():
    at = AppTest.from_string(HEAD + "from app.views import overview; overview.render()", default_timeout=180).run()
    assert not at.exception
    assert len(at.dataframe) == 1


def test_block2_selectors_and_calib_table():
    at = AppTest.from_string(HEAD + "from app.views import block2; block2.render()", default_timeout=180).run()
    assert not at.exception
    for tier in ("Luna", "Sol", "Astra"):
        at.radio[0].set_value(tier).run()
        for case in ("低成本", "基準", "高成本"):
            at.radio[1].set_value(case).run()
            assert not at.exception
            assert all(str(i).startswith(tier) for i in at.dataframe[0].value.index)
    drv = at.dataframe[1].value
    assert len(drv) == 15 and drv.shape[1] == 5          # 15 個推導鏈量 × 5 世代
    f, h = at.dataframe[2].value, at.dataframe[3].value
    assert len(f) == 7 and len(h) == 4                    # F 節 7 點、H 節 4 點，分兩張表
    for tbl in (f, h):
        assert (tbl["量測平台"].astype(str).str.len() > 0).all() and (tbl["口徑"].astype(str).str.len() > 0).all()
        for col in ("點位", "世代", "每用戶速度", "實測", "模型", "比值"):
            assert col in tbl.columns
    assert "軟體／日期" in f.columns and "軟體／日期" not in h.columns


def test_drv_cost_row_follows_case_selector():
    """推導鏈的 decode $/M 列跟隨成本情境（讀 IF_CostDec），且與上方主表同列數值一致。"""
    at = AppTest.from_string(HEAD + "from app.views import block2; block2.render()", default_timeout=180).run()
    at.radio[0].set_value("Sol").run()
    seen = {}
    for case in ("低成本", "基準", "高成本"):
        at.radio[1].set_value(case).run()
        assert not at.exception
        main, drv = at.dataframe[0].value, at.dataframe[1].value
        drv_cost = drv[drv.index.str.contains(f"｜{case}")]
        assert len(drv_cost) == 1
        main_cost = main[main.index.str.contains("decode") & main.index.str.contains("經濟")].iloc[0]
        assert list(drv_cost.iloc[0]) == list(main_cost), (case, list(drv_cost.iloc[0]), list(main_cost))
        seen[case] = tuple(drv_cost.iloc[0])
    assert len(set(seen.values())) == 3                  # 三個成本情境的值各不相同


def test_no_label_lookup_in_app_and_engine():
    """網站與引擎不再以欄 A 標籤定位（改讀 IF_Hdr／DRV_／CAL_ 具名範圍）。"""
    for path in list((ROOT / "app").rglob("*.py")) + list((ROOT / "engine").rglob("*.py")):
        assert "column_labels" not in path.read_text(encoding="utf-8"), path

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
    calib = at.dataframe[1].value
    assert "量測平台" in calib.columns and (calib["量測平台"].astype(str).str.len() > 0).all()
    assert len(calib) == 11   # F 節 7 點＋H 節 4 點

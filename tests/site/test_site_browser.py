"""靜態網站的瀏覽器檢查（site/check_site_playwright.py）：每頁 1280 px 與 390 px 截圖、無橫向捲動、無空值、
選擇器每節恰顯示一版、無外部請求、無 JS 錯誤。沒有 Playwright／Chromium 時略過。"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytest.importorskip("playwright.sync_api")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pages_in_browser(tmp_path):
    out = tmp_path / "dist"
    _load("tokenomics_build_site", ROOT / "site" / "build_site.py").build(out)
    check = _load("tokenomics_check_site", ROOT / "site" / "check_site_playwright.py")
    try:
        problems = check.check(out, tmp_path / "shots")
    except Exception as exc:  # 沒有 Chromium 等環境因素
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright 的 Chromium 未安裝")
        raise
    assert not problems, problems
    assert len(list((tmp_path / "shots").glob("*.png"))) == 2 * 11

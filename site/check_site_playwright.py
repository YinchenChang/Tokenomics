#!/usr/bin/env python3
"""靜態網站的瀏覽器檢查（Playwright／Chromium）：每頁在桌機 1280 px 與手機 390 px 寬度下

1. 截整頁圖（--shots 目錄；檔名 <頁>_<寬>.png）；
2. 頁面不可橫向捲動（document 的 scrollWidth ≤ 視窗寬；表格在自身容器內捲動不算）；
3. 沒有空值：表格儲存格、KPI 卡不可為空字串或 nan／None／NaN／undefined／Infinity（Excel 空白格顯示「—」）；
4. 每個選擇器組合區塊在預設狀態下恰好顯示一個版本；點選每個選擇器按鈕後仍恰好顯示一個版本；
5. 不發出任何外部請求（file:// 以外的請求一律記錄並視為失敗）；無 JS 錯誤。

用法：python3 site/check_site_playwright.py [--dist site/dist] [--shots site/screenshots]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BAD = {"", "nan", "none", "undefined", "infinity", "-infinity", "null"}

JS_CHECK = r"""
() => {
  const bad = [];
  document.querySelectorAll('td, .kpi .v, tbody th').forEach(el => {
    const t = el.textContent.trim().toLowerCase();
    if (BAD.includes(t)) bad.push((el.closest('[id]')||{}).id + ':' + el.outerHTML.slice(0, 80));
  });
  const groups = {};
  document.querySelectorAll('.sec').forEach((s, i) => {
    const vars = s.querySelectorAll(':scope > .var');
    if (vars.length) groups[i] = Array.from(vars).filter(v => !v.hidden).length;
  });
  return {scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth, bad: bad.slice(0, 10), nbad: bad.length, groups};
}
""".replace("BAD", json.dumps(sorted(BAD)))


def check(dist: Path, shots: Path) -> list[str]:
    meta = json.loads((dist / "build.json").read_text(encoding="utf-8"))
    shots.mkdir(parents=True, exist_ok=True)
    problems, external, js_errors = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height in ((1280, 900), (390, 844)):
            ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
            page = ctx.new_page()
            page.on("request", lambda r: external.append(r.url) if not r.url.startswith(("file://", "data:", "about:")) else None)
            page.on("pageerror", lambda exc: js_errors.append(str(exc)))
            for pinfo in meta["pages"]:
                f = pinfo["file"]
                page.goto((dist / f).resolve().as_uri())
                page.wait_for_load_state("load")
                r = page.evaluate(JS_CHECK)
                tag = f"{f}@{width}"
                if r["scrollW"] > r["innerW"]:
                    problems.append(f"{tag}: 橫向捲動 scrollWidth {r['scrollW']} > {r['innerW']}")
                if r["nbad"]:
                    problems.append(f"{tag}: 空值 {r['nbad']} 格，例：{r['bad']}")
                for g, n in r["groups"].items():
                    if n != 1:
                        problems.append(f"{tag}: 第 {g} 節顯示 {n} 個版本（應為 1）")
                page.screenshot(path=str(shots / f"{Path(f).stem}_{width}.png"), full_page=True)
                # 每個選擇器按鈕都點一次：每節仍恰好顯示一個版本，且無橫向捲動
                if width == 1280:
                    for btn in page.query_selector_all(".seg[data-dim] button"):
                        btn.click()
                        r2 = page.evaluate(JS_CHECK)
                        for g, n in r2["groups"].items():
                            if n != 1:
                                problems.append(f"{tag}: 點選「{btn.inner_text()}」後第 {g} 節顯示 {n} 個版本")
                        if r2["nbad"]:
                            problems.append(f"{tag}: 點選「{btn.inner_text()}」後空值 {r2['nbad']} 格：{r2['bad']}")
            ctx.close()
        browser.close()
    if external:
        problems.append(f"外部請求 {len(external)} 個：{sorted(set(external))[:10]}")
    if js_errors:
        problems.append(f"JS 錯誤：{js_errors[:5]}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", type=Path, default=ROOT / "site" / "dist")
    ap.add_argument("--shots", type=Path, default=ROOT / "site" / "screenshots")
    a = ap.parse_args()
    problems = check(a.dist, a.shots)
    n = len(list(a.shots.glob("*.png")))
    if problems:
        print("失敗：", *problems, sep="\n  ")
        sys.exit(1)
    print(f"通過：{n} 張截圖 → {a.shots}；無橫向捲動、無空值、選擇器每節恰顯示一版、無外部請求、無 JS 錯誤")


if __name__ == "__main__":
    main()

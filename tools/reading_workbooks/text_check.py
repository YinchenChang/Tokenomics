"""「說明句數字檢查」（check_reading.py、check_reading_m.py 共用）。

規則（以盤點表 text_inventory_*.csv 為白名單）：
1. 盤點表列為「現行值」的格，必須是公式，且重算後是文字、不是錯誤值。
2. 其他文字格若含顯著數字（text_scan.significant_tokens）而盤點表沒有列：失敗
   （新增的說明句一律要分類：現行值就做成公式；歷史、外部事實等要登錄為保留）。
3. 盤點表列的格在活頁簿裡找不到：失敗。
"""
import csv
import re
from pathlib import Path

from text_scan import scan_static


def check_text_numbers(wb_formulas, wb_values, inventory_csv, fails):
    inv = {}
    with open(inventory_csv, encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh):
            inv[(r['頁'], r['格'])] = r['類別']
    n_cur = 0
    for (sh, a), cl in inv.items():
        if sh not in wb_formulas.sheetnames:
            fails.append(f'說明句數字 盤點表的頁不存在：{sh}')
            continue
        f = wb_formulas[sh][a].value
        if cl == '現行值':
            n_cur += 1
            if not (isinstance(f, str) and f.startswith('=')):
                fails.append(f'說明句數字 {sh}!{a} 盤點表列為現行值，但不是公式（寫死的數字）：{str(f)[:50]}')
                continue
            v = wb_values[sh][a].value
            if not isinstance(v, str) or v == '' or re.match(r'^(#|Err:)', v):
                fails.append(f'說明句數字 {sh}!{a} 公式沒有算出文字：{v!r}')
        elif f is None:
            fails.append(f'說明句數字 {sh}!{a} 盤點表有列（{cl}），活頁簿裡是空格')
    for sh, a, v, tk in scan_static(wb_formulas):
        if (sh, a) not in inv:
            fails.append(f'說明句數字 {sh}!{a} 含數字 {tk} 的文字格沒有登錄在盤點表（現行值請改公式；歷史／外部事實請登錄保留）：{v[:40]}')
    return n_cur, len(inv)

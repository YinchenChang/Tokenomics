"""閱讀版文字格掃描（說明句數字檢查與盤點表共用）。
顯著數字＝小數、千分位、百分比、或 ≥13 的整數（年份 20xx 除外）。≤12 的整數（如 T1＝4、6 年）不由掃描抓，
但盤點表列為「現行值」的格一律檢查必須是公式。
"""
import re

_SKIP = re.compile(r'v\d+\.\d+|\bL\d+(?:–L\d+)?|\bS\d+|\bN\d+|[A-Z]{1,2}\d+(?::[A-Z]{1,2}\d+)?|\d{4}-\d\d(?:-\d\d)?|SRC_\w+|\w*_\d+\w*|IN_\w+|\d+_\w+|\bGM\d+|\bE\d{3}\b|第 \d+[–\-]\d+ 列|\d+[–\-]\d+ 列|\b\d+\.\d+\.\d+\b|第 \d+(?:[–＋]\d+)? 列|\d+＋\d+ 列|格點第 \d+ 列|\d+:\d+|\d+-\d+ \d+:\d+|\d+-\d+(?= \d+:)')
# 結構常數（單位換算、天數），不是模型數值
CONSTANTS = {'1000', '1,000', '1000000', '525,600', '365', '100'}
_TOK = re.compile(r'(?<![A-Za-z_\d.])[−\-+]?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(%?)')


def significant_tokens(text):
    t = _SKIP.sub(' ', text)
    out = []
    for m in _TOK.finditer(t):
        ip, fp, pc = m.group(1).replace(',', ''), m.group(2), m.group(3)
        if m.group(0) in CONSTANTS:
            continue
        if fp or pc or ',' in m.group(1):
            out.append(m.group(0))
        elif int(ip) >= 13 and not (2000 <= int(ip) <= 2099):
            out.append(m.group(0))
    return out


def scan_static(wb_formulas):
    """回傳 [(頁, 格, 文字, 顯著數字)]：靜態文字格中含顯著數字者（排除公式與純數值格）。"""
    res = []
    for ws in wb_formulas:
        if ws.title.startswith('9_'):
            continue   # 核對對照表：Tokenomics 位置字串，不是說明句
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str) and not v.startswith('='):
                    tk = significant_tokens(v)
                    if tk:
                        res.append((ws.title, c.coordinate, v, tk))
    return res

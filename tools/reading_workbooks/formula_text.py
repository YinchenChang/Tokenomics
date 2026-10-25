"""閱讀版「說明句公式化」共用工具（工作單 20261025_閱讀版說明句公式化）。

把說明句裡寫死的「現行值」數字換成公式：原句的文字不動，只把數字那一小段換成
TEXT(<本簿來源格>, "<格式>")，整句變成 ="…"&TEXT(…)&"…"。

用法（建檔程式或換版腳本內）：
    from formula_text import apply_text, num, pct, gen
    apply_text(ws, 'E30', [('−9%', pct('IN_g')), ('6', num('IN_T', '0')), ('76%', num('LS_L_price', '0%'))])

規則：
- subs 依「原句出現順序」排列；每項 (原句中的數字字串, 公式片段[, 略過幾次])。
  原句找不到該字串就丟例外（不會悄悄漏改）。
- Excel 公式中的字串常數每段不得超過 255 字元，本工具自動切段。
- 套用後句子的「顯示文字」必須與原句相同（由換版驗收的逐格比對檢查）；
  原句若與現行值不符（原本就過時），不要硬改，列入報告「待 Project 判斷」。
"""
import re

MINUS = '−'   # 閱讀版文字用的負號 −
_CHUNK = 240


def _q(s):
    return '"' + s.replace('"', '""') + '"'


def num(ref, fmt):
    """TEXT(ref, fmt)；負號沿用 Excel 的 "-"。"""
    return f'TEXT({ref},"{fmt}")'


def neg(expr):
    """把 "-" 換成閱讀版慣用的 − (U+2212)。"""
    return f'SUBSTITUTE({expr},"-","{MINUS}")'


def numn(ref, fmt):
    """帶 − 號的數字。"""
    return neg(num(ref, fmt))


def pct(ref, dec=0, plus=False):
    """百分比；負號用 −；plus=True 時正值前加 +。"""
    fmt = '0%' if dec == 0 else '0.' + '0' * dec + '%'
    e = neg(num(ref, fmt))
    if plus:
        e = f'IF({ref}>0,"+","")&{e}'
    return e


def gen(ref):
    """一般數字（整數不帶小數點、小數不補零），用於 2、0.5 這類值。"""
    return f'ROUND({ref},6)&""'


def _lit(s):
    """字串常數，過長就切段。"""
    if s == '':
        return None
    out = []
    for i in range(0, len(s), _CHUNK):
        out.append(_q(s[i:i + _CHUNK]))
    return '&'.join(out)


def build_formula(text, subs):
    pos = 0
    parts = []
    for sub in subs:
        lit, expr = sub[0], sub[1]
        skip = sub[2] if len(sub) > 2 else 0
        i = pos - 1
        for _ in range(skip + 1):
            i = text.find(lit, i + 1)
            if i < 0:
                raise ValueError(f'原句找不到「{lit}」（略過 {skip} 次；自第 {pos} 字起）：{text[:60]}…')
        lead = _lit(text[pos:i])
        if lead:
            parts.append(lead)
        parts.append(f'({expr})' if '&' in expr else expr)
        pos = i + len(lit)
    tail = _lit(text[pos:])
    if tail:
        parts.append(tail)
    return '=' + '&'.join(parts)


REPLACED = []   # (頁, 格, 原句, 公式)；供報告與核對使用


def apply_text(ws, addr, subs):
    c = ws[addr]
    text = c.value
    if not isinstance(text, str) or text.startswith('='):
        raise ValueError(f'{ws.title}!{addr} 不是靜態文字：{text!r}')
    f = build_formula(text, subs)
    if len(f) > 8000:
        raise ValueError(f'{ws.title}!{addr} 公式過長 {len(f)}')
    c.value = f
    REPLACED.append((ws.title, addr, text, f))
    return f


def replace_label(ws, addr, old, new):
    """版本標籤等純文字替換（不是公式化）；old 必須存在。"""
    c = ws[addr]
    assert isinstance(c.value, str) and old in c.value, f'{ws.title}!{addr} 找不到 {old}'
    c.value = c.value.replace(old, new)

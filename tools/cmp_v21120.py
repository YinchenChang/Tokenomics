"""v21.12（v22.0 B2）驗收 V1：v21.11 與 v21.12 逐值比較，以「鍵」對齊而不是以座標對齊（沿用 tools/cmp_relayout.py 的比較規則）。

用法：python3 tools/cmp_v21120.py <舊 v21.11.xlsx> <新 v21.12.xlsx> [<輸出.json>]
兩個檔都必須是 LibreOffice 重算存檔後的檔（含快取值）。

對齊規則（舊座標 → 新座標）：
- Cap_In 第 5–8、21–24、30–32 列：標記 F → G、說明 G → H（Terra 放 F，J2 (a)）；F 節註記第 59 列 → 第 60 列（第 59 列為 Terra 候選）。
- Price_Frontier A 節：混合 H–J 不變、合格 K–M → L–N、中國合格 N–P → P–R（每組加一個 Terra 欄）；A 節註記第 19 列 → 第 20 列。
- Alloc：P 節（區間時效指紋）以下依 P 節列數差位移（同 cmp_relayout）。
- 各頁「用途」欄依舊／新欄位對齊。其餘頁座標不變。
比較：數值相對差 ≤ 1e-9（絕對 1e-12）；文字逐字。具名範圍：同名者逐格比（1×3 → 1×4 者比前 3 格）；只在一邊的名稱另列。"""
import json
import sys
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter as L, range_boundaries


TIER_ROWS = {5, 6, 7, 8, 21, 22, 23, 24, 30, 31, 32}
PF_COLS = {11: 12, 12: 13, 13: 14, 14: 16, 15: 17, 16: 18}      # Price_Frontier K–M -> L–N, N–P -> P–R


def purpose_col(ws):
    for c in range(3, ws.max_column + 2):
        if ws.cell(3, c).value == "用途":
            return c
    return None


def row_map(sheet):
    if sheet == "Cap_In":
        return lambda r: 60 if r == 59 else r
    if sheet == "Price_Frontier":
        return lambda r: 20 if r == 19 else r
    return lambda r: r


def colmap_factory(sheet, wo, wn):
    po, pn = purpose_col(wo), purpose_col(wn)

    def f(r, c):
        if po is not None and c == po:
            return pn
        if sheet == "Cap_In" and r in TIER_ROWS and c in (6, 7):
            return c + 1
        if sheet == "Price_Frontier" and 6 <= r <= 18 and c in PF_COLS:
            return PF_COLS[c]
        return c
    return f


FP_TITLE = "P. 區間時效指紋"
FP_NEXT = "Q. 推論支出區間"


def fp_block(ws):
    """(first, last) rows of Alloc section P (title row .. row before section Q)."""
    p = q = None
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, 1).value
        if isinstance(v, str) and v.startswith(FP_TITLE):
            p = r
        if isinstance(v, str) and v.startswith(FP_NEXT):
            q = r
    return (p, q - 1) if p and q else None


def row_shift(sheet, wo, wn):
    """Alloc: rows below the regenerated fingerprint block (section P) shift with its row count; Cap_In／Price_Frontier: the moved note rows."""
    if sheet != "Alloc":
        return row_map(sheet), None
    a, b = fp_block(wo), fp_block(wn)
    d = (b[1] - a[1]) if a and b else 0
    return (lambda r: r + d if a and r > a[1] else r), a


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


def name_cells(names, wb, n):
    t = names[n]
    if "!" not in t or "," in t:
        return None
    sh, rg = t.rsplit("!", 1)
    sh = sh.strip("'")
    if sh not in wb.sheetnames:
        return None
    try:
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    except Exception:
        return None
    return sh, [(r, c) for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def main():
    old, new = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    fo, vo = openpyxl.load_workbook(old), openpyxl.load_workbook(old, data_only=True)
    fn, vn = openpyxl.load_workbook(new), openpyxl.load_workbook(new, data_only=True)
    res = {"sheets": {}, "names": {}}
    mapped_new = {}
    for ws in fo.worksheets:
        s = ws.title
        if s not in fn.sheetnames:
            res["sheets"][s] = {"missing_in_new": True}
            continue
        f = colmap_factory(s, ws, fn[s])
        a, b = vo[s], vn[s]
        rs, fp = row_shift(s, ws, fn[s])
        diffs, n = [], 0
        seen = mapped_new.setdefault(s, set())
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                r0, c = cell.row, cell.column
                if fp and fp[0] <= r0 <= fp[1]:
                    continue          # Alloc P (range freshness fingerprint): regenerated list, compared separately (counts below)
                r = rs(r0)
                c2 = f(r0, c)
                seen.add((r, c2))
                n += 1
                x, y = a.cell(r0, c).value, b.cell(r, c2).value
                fx, fy = cell.value, fn[s].cell(r, c2).value
                isf_x = isinstance(fx, str) and fx.startswith("=")
                isf_y = isinstance(fy, str) and fy.startswith("=")
                if isf_x != isf_y and not (isf_x and same(x, y)):
                    diffs.append((cell.coordinate, L(c2) + str(r), "kind", str(fx)[:80], str(fy)[:80]))
                    continue
                if not same(x, y):
                    diffs.append((cell.coordinate, L(c2) + str(r), "value", str(x)[:80], str(y)[:80]))
        added = 0
        fpn = fp_block(fn[s]) if s == "Alloc" else None
        for row in fn[s].iter_rows():
            for cell in row:
                if fpn and fpn[0] <= cell.row <= fpn[1]:
                    continue
                if cell.value is not None and (cell.row, cell.column) not in seen:
                    added += 1
        res["sheets"][s] = {"cells": n, "diffs": len(diffs), "added_in_new": added, "first": diffs[:400]}
    for s in fn.sheetnames:
        if s not in fo.sheetnames:
            res["sheets"][s] = {"new_sheet": True}
    no = {k: d.attr_text for k, d in fo.defined_names.items()}
    nn = {k: d.attr_text for k, d in fn.defined_names.items()}
    cmp_n = mism = 0
    bad = []
    for k in sorted(set(no) & set(nn)):
        A, B = name_cells(no, vo, k), name_cells(nn, vn, k)
        if A is None or B is None:
            if no[k] != nn[k]:
                bad.append((k, "ref", no[k], nn[k]))
            continue
        cmp_n += 1
        sa, ca = A
        sb, cb = B
        f = colmap_factory(sa, fo[sa], fn[sb])
        rs, _ = row_shift(sa, fo[sa], fn[sb])
        exp = [(rs(r), f(r, c)) for r, c in ca]
        if sa != sb or (len(ca) != len(cb) and not set(exp) <= set(cb)):      # 1×3 -> 1×4: the three old cells must be the first three new cells
            mism += 1; bad.append((k, "shape", no[k], nn[k])); continue
        for (r, c), (r2, c2) in zip(ca, exp):
            if not same(vo[sa].cell(r, c).value, vn[sb].cell(r2, c2).value):
                mism += 1
                bad.append((k, "value", f"{L(c)}{r}", vo[sa].cell(r, c).value, f"{L(c2)}{r2}", vn[sb].cell(r2, c2).value))
                break
    res["names"] = {"compared": cmp_n, "mismatch": mism, "only_old": sorted(set(no) - set(nn)), "only_new": sorted(set(nn) - set(no)),
                    "bad": bad[:200], "shape_changed": sorted(k for k in set(no) & set(nn) if no[k] != nn[k])}
    tot = sum(v.get("diffs", 0) for v in res["sheets"].values())
    print(f"names compared {cmp_n}, mismatches {mism}; only old {len(res['names']['only_old'])}, only new {len(res['names']['only_new'])}; "
          f"ref text changed {len(res['names']['shape_changed'])}")
    print(f"cell diffs total {tot}")
    for s, v in res["sheets"].items():
        if v.get("diffs") or v.get("missing_in_new") or v.get("new_sheet"):
            print(" ", s, {k: v[k] for k in v if k != "first"})
    if out:
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()

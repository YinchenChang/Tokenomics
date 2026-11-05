"""v22.0（B3）驗收 V7：v21.12 → v22.0 逐格比較，並對照預期變動 CSV（tools/v22000_prerun.py 的預檢值）。

用法：python3 tools/cmp_v22000.py <舊 v21.12.xlsx> <新 v22.0.xlsx> <預期變動.csv> [<輸出.json>]
兩個檔都必須是 LibreOffice 重算存檔後的檔。

對齊：各頁座標不變（J14：既有列不位移），只有 Alloc 的 O 節（RNG_ 端點表，新增 Terra 名稱依字母序插入）與其下的 P 節（區間時效指紋）、Q 節
依「A 欄＋B 欄文字＋出現序」對齊。P 節指紋格另計（重產清單）。
分類：
  hit      值改變、在 CSV 且新值＝預檢值（相對 1e-9）
  csv_off  值改變、在 CSV 但新值≠預檢值
  csv_same 在 CSV 但新值＝舊值（例如區間過期旗標：預檢時過期，重產後回原值）
  extra    值改變、不在 CSV（逐格列出，交報告表 2 分類）
  formula  公式文字改變（列出）
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter as L


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


def parse_csv_val(s):
    if s == "":
        return None
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def alloc_rowmap(wo, wn):
    def start(ws):
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if isinstance(v, str) and v.startswith("O. 批次口徑倍數區間端點"):
                return r
        raise KeyError("Alloc O")
    so, sn = start(wo), start(wn)
    assert so == sn, (so, sn)

    def keys(ws, s):
        cnt = Counter(); out = {}
        for r in range(s, ws.max_row + 1):
            k = (ws.cell(r, 1).value, ws.cell(r, 2).value)
            if k == (None, None):
                continue
            cnt[k] += 1
            out[(k, cnt[k])] = r
        return out
    ko, kn = keys(wo, so), keys(wn, sn)
    m = {r: kn.get(k) for k, r in ko.items()}
    return so, m


def main():
    old, new, csvp = sys.argv[1:4]
    out = sys.argv[4] if len(sys.argv) > 4 else None
    fo, vo = openpyxl.load_workbook(old), openpyxl.load_workbook(old, data_only=True)
    fn, vn = openpyxl.load_workbook(new), openpyxl.load_workbook(new, data_only=True)
    exp = {}
    with open(csvp, encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            exp[(row["工作表"], row["儲存格"])] = parse_csv_val(row["預檢值（LibreOffice 重算）"])
    res = defaultdict(list)
    seen_csv = set()
    for ws in fo.worksheets:
        s = ws.title
        a, b, bf = vo[s], vn[s], fn[s]
        if s == "Alloc":
            so, m = alloc_rowmap(ws, bf)
        else:
            so, m = None, None
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                r0, c = cell.row, cell.column
                r = r0
                if so and r0 >= so:
                    r = m.get(r0)
                    if r is None:
                        res["unmatched_old"].append((s, cell.coordinate, str(cell.value)[:60]))
                        continue
                k_old = (s, cell.coordinate)
                x, y = a.cell(r0, c).value, b.cell(r, c).value
                fx, fy = cell.value, bf.cell(r, c).value
                isf = isinstance(fx, str) and fx.startswith("=")
                if isf and fx != fy and not (so and r != r0):
                    res["formula"].append((s, cell.coordinate, fx[:150], str(fy)[:150]))
                if k_old in exp:
                    seen_csv.add(k_old)
                    if same(x, y):
                        res["csv_same"].append((s, cell.coordinate, x, exp[k_old]))
                    elif same(y, exp[k_old]):
                        res["hit"].append((s, cell.coordinate))
                    else:
                        res["csv_off"].append((s, cell.coordinate, x, y, exp[k_old]))
                elif not same(x, y):
                    res["extra"].append((s, cell.coordinate, L(c) + str(r), str(x)[:100], str(y)[:100]))
    res["csv_not_seen"] = sorted(set(exp) - seen_csv)
    summ = {k: len(v) for k, v in res.items()}
    print(summ)
    by = Counter(x[0] for x in res["extra"])
    print("extra by sheet", dict(by))
    if out:
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()

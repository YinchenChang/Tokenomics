"""v22.0（B3）預期變動 CSV：在 v21.12 的暫存複本上預跑「組合改變」，以 LibreOffice 重算後逐格比較（同 v21.8–v21.10 的做法：chat 端預檢值）。

用法：python3 tools/v22000_prerun.py <v21.12.xlsx（LibreOffice 重算存檔）> <輸出 csv> [<暫存資料夾>]

暫存複本只做 B3 的「值」變動，不建 Terra 名稱（builder 以外的獨立路徑，用來核對 builder 的結果）：
  1. Cap_In D31 0.45 → 0.30、F31 0 → 0.15（2026 付費組合，J6 (a)）；B4_TerraFam 0 → 1（J9 (a)）。
  2. 兩個三項讀者改四項（B2 報告第 5 節第 2 項）：Interface N 節 IF_TokGWPaidMix 每格、L1 D127（L1_TokGW_PaidCap_VR200）；
     Terra 的每 GW 產能直接讀 Perf 第 98 列 Terra 欄（4×(世代−1)＋4），值與 v22.0 的 IF_TokGW_Terra 相同。
輸出：v21.12 值與預檢值不同的每一格（相對容差 1e-9），欄位「工作表,儲存格,v21.12 值,預檢值（LibreOffice 重算）,來源」。"""
import csv
import shutil
import sys
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter as L, range_boundaries

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests" / "parity"))
from parity_lib import lo_recalc  # noqa: E402

SRC = "B3 組合 0.40／0.30／0.15／0.15、B4_TerraFam 1、IF_TokGWPaidMix／L1_TokGW_PaidCap_VR200 四項"


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


def ref_rc(wb, name):
    sh, rg = wb.defined_names[name].attr_text.rsplit("!", 1)
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    return sh.strip("'"), c1, r1, c2, r2


def main():
    base, out = Path(sys.argv[1]), Path(sys.argv[2])
    tmp = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(tempfile.mkdtemp(prefix="v22pre_"))
    tmp.mkdir(parents=True, exist_ok=True)
    s = tmp / base.name
    wb = openpyxl.load_workbook(base)
    ws = wb["Cap_In"]
    assert ws["D31"].value == 0.45 and ws["F31"].value == 0, (ws["D31"].value, ws["F31"].value)
    ws["D31"].value, ws["F31"].value = 0.30, 0.15
    sh, c1, r1, _, _ = ref_rc(wb, "B4_TerraFam")
    assert wb[sh].cell(r1, c1).value == 0
    wb[sh].cell(r1, c1).value = 1
    sh, c1, r1, c2, _ = ref_rc(wb, "IF_TokGWPaidMix")
    iw = wb[sh]
    for c in range(c1, c2 + 1):
        k = c - c1 + 1
        X = L(c)
        terra = f"INDEX(Perf!$C$98:$V$98,4*(Unit_Cost!{X}$6-1)+4)"
        assert "IF_MixPaid_Astra/INDEX(IF_TokGW_Astra" in iw.cell(r1, c).value
        iw.cell(r1, c).value = (f"=1/(IF_MixPaid_Luna/INDEX(IF_TokGW_Luna,1,{k})+IF_MixPaid_Sol/INDEX(IF_TokGW_Sol,1,{k})+IF_MixPaid_Astra/INDEX(IF_TokGW_Astra,1,{k})"
                                f"+INDEX(B4_MixPaid,1,4)/{terra})")
    sh, c1, r1, _, _ = ref_rc(wb, "L1_TokGW_PaidCap_VR200")
    lw = wb[sh]
    assert lw.cell(r1, c1).value.endswith("INDEX(IF_TokGW_Astra,1,11))"), lw.cell(r1, c1).value
    lw.cell(r1, c1).value = lw.cell(r1, c1).value[:-1] + "+INDEX(B4_MixPaid,1,4)/INDEX(Perf!$C$98:$V$98,4*(Unit_Cost!M$6-1)+4))"
    wb.save(s)
    o = lo_recalc(s, tmp / "lo")
    a = openpyxl.load_workbook(base, data_only=True)
    b = openpyxl.load_workbook(o, data_only=True)
    rows = []
    for w in a.worksheets:
        wb2 = b[w.title]
        for row in w.iter_rows():
            for cell in row:
                y = wb2.cell(cell.row, cell.column).value
                if not same(cell.value, y):
                    rows.append((w.title, cell.coordinate, cell.value, y, SRC))
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["工作表", "儲存格", "v21.12 值", "預檢值（LibreOffice 重算）", "來源"])
        wr.writerows(sorted(rows, key=lambda x: (x[0], x[1])))
    print("cells", len(rows), "->", out)
    shutil.rmtree(tmp / "lo", ignore_errors=True)


if __name__ == "__main__":
    main()

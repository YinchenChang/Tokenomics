"""由 4-0 明細（頁 1_死格_逐列）產生 builder/v1010_marks.py：1-b 第 1 項「用途」欄的標記資料。
用法：python3 docs/evidence/20261016_瘦身4-1/gen_marks.py
規則→標記：R02 未接線；R03 複本讀取；R07、R08、R12、R14、R15、R17、R19、R20、R21 顯示用。其餘規則（判斷類）不標。
標記文字＝「<標記>：<儲存格範圍>（<4-0 建議處置括號內的口徑>）」；同一頁同一列有多筆時以「；」相接。"""
import collections
import re
import openpyxl

SRC = "docs/reports/20261016_瘦身盤點4-0_明細.xlsx"
KIND = {"R02": "未接線", "R03": "複本讀取"}
KIND.update({r: "顯示用" for r in ("R07", "R08", "R12", "R14", "R15", "R17", "R19", "R20", "R21")})
FIX = {
    "R02": "MAG、智譜、AI 半導體待用；目前不進任何輸出",
    "R03": "被 Sens_／_Prod 複本頁讀取，不是死格",
}
ws = openpyxl.load_workbook(SRC)["1_死格_逐列"]
out = collections.defaultdict(lambda: collections.defaultdict(list))
for row in ws.iter_rows(min_row=3, values_only=True):
    rule = row[11]
    if rule not in KIND:
        continue
    sheet, cells, action = row[0], row[1], row[5] or ""
    m = re.findall(r"（([^（）]*)）", action)
    reason = FIX.get(rule) or (m[-1] if m else "")
    r = int(re.search(r"\d+", cells).group())
    out[sheet][r].append(f"{KIND[rule]}：{cells}" + (f"（{reason}）" if reason else ""))
lines = ['"""1-b 第 1 項：「用途」欄標記資料（由 docs/evidence/20261016_瘦身4-1/gen_marks.py 產生，勿手改）。{頁: {列: 標記文字}}"""', "MARKS = {"]
n = 0
for s, rows in out.items():
    lines.append(f"    {s!r}: {{")
    for r in sorted(rows):
        txt = "；".join(dict.fromkeys(rows[r]))
        lines.append(f"        {r}: {txt!r},")
        n += 1
    lines.append("    },")
lines.append("}")
open("builder/v1010_marks.py", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("sheets", len(out), "rows", n)

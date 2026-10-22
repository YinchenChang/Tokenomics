"""v17.2 W1 第二來源 B1（工作單 docs/workorders/20261020_W1第二來源_B1.md）專屬測試：與封存的 v17.1 逐格比對。
模型格（SRC_* 與 SRC_Index 以外）只允許下列差異：版本字串與 README 新列、Decisions SL51-*、Checks 的 W1／GOV_Warnings 計數與 E13 範圍公式、
SRC 審查日的連帶顯示（Gov_Map AF 列位置、AI／AJ 審查日；Interface U／V 最弱輸入更新日 IFC_Updated）。"""
import json
import re
from pathlib import Path

import openpyxl

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V171 = REPO / "model" / "archive" / "20261020_Tokenomics_v17.1.xlsx"
V172 = REPO / "model" / "archive" / "20261020_Tokenomics_v17.2.xlsx"      # v18.0：現行版已是 v18.0；v17.1→v17.2 的逐格比較改對封存的 v17.2 釘住（v17.2→v18.0 由 test_v1800 檢查）
DATA = json.loads((REPO / "builder" / "v1720_data.json").read_text(encoding="utf-8"))
SRC = ["SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Cap", "SRC_Harness", "SRC_Demand"]
Q_NEW = {"SRC_PRC_049", "SRC_PRC_050", "SRC_HW_096", "SRC_HW_097", "SRC_DC_021", "SRC_DC_022"}


def _col(coord):
    return re.match(r"[A-Z]+", coord).group()


def _allowed(sh, coord):
    if sh in SRC or sh == "SRC_Index":
        return True
    if sh == "README":
        return coord in ("A1", "B5", "A64", "B64")
    if sh == "Alloc":
        return coord in ("C177", "C178")
    if sh == "Checks":
        return coord in ("D86", "D87", "D98")      # E13 範圍公式、W1、GOV_Warnings
    if sh == "Gov_Map":
        return _col(coord) in ("AF", "AI", "AJ")
    if sh == "Interface":
        return _col(coord) in ("U", "V")
    if sh == "Decisions":
        return True                                 # 只新增列，下面另查
    return False


def _diffs(data_only):
    a, b = openpyxl.load_workbook(V171, data_only=data_only), openpyxl.load_workbook(V172, data_only=data_only)
    assert a.sheetnames == b.sheetnames
    out = []
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    out.append((ws.title, ws.cell(r, c).coordinate, x, y))
    return out, a, b


def test_v1720_diffs_only_expected():
    for mode in (False, True):
        d, a, b = _diffs(mode)
        bad = [t for t in d if not _allowed(t[0], t[1])]
        assert bad == [], bad[:10]
        dec = [t for t in d if t[0] == "Decisions"]
        assert all(t[2] is None for t in dec) and len({re.sub(r"[A-Z]+", "", t[1]) for t in dec}) == 2      # 只新增兩列（SL51-01／02）
    names_a, names_b = set(a.defined_names), set(b.defined_names)
    assert names_a <= names_b
    changed = {k for k in names_a if a.defined_names[k].attr_text != b.defined_names[k].attr_text}
    assert changed == {"IDX_SrcID", "IDX_SrcStat", "IDX_SrcGrade", "IDX_SrcDate"}, changed      # SRC_Index 變長
    assert all(n.startswith("SRC_") for n in names_b - names_a)


def test_v1720_no_model_number_changes():
    """數字格：SRC_*／SRC_Index、Checks 計數、Gov_Map AF／AJ（列位置、審查日數值）、Interface V（審查日數值）以外不得有數值差異。"""
    d, _, _ = _diffs(True)
    num = [t for t in d if isinstance(t[2], (int, float)) or isinstance(t[3], (int, float))]
    other = [t for t in num if not (t[0] in SRC or t[0] == "SRC_Index" or (t[0], t[1]) in (("Checks", "D87"), ("Checks", "D98"))
                                    or (t[0] == "Gov_Map" and _col(t[1]) in ("AF", "AJ")) or (t[0] == "Interface" and _col(t[1]) == "V"))]
    assert other == [], other[:10]
    for t in num:
        if t[0] == "Interface":      # 審查日數值 yyyymmdd 只會變成 2026-10-20
            assert t[3] == 20261020, t


def _rows(wb):
    out = {}
    for sh in SRC:
        ws = wb[sh]
        for r in range(5, ws.max_row + 1):
            if isinstance(ws.cell(r, 1).value, str) and ws.cell(r, 1).value.startswith("SRC_"):
                out[ws.cell(r, 1).value] = (ws, r)
    return out


def test_v1720_records():
    wb = openpyxl.load_workbook(model_path(), data_only=True)
    rows = _rows(wb)
    for a in DATA["A"]:
        ws, r = rows[a["orig"]]
        assert ws[f"R{r}"].value == a["id"] and ws[f"S{r}"].value == "2026-10-20", a["orig"]
        wn, rn = rows[a["id"]]
        assert wn.title == ws.title and wn[f"O{rn}"].value == "Alt" and wn[f"K{rn}"].value in (2, 3)
        assert [wn[f"{c}{rn}"].value for c in "BGH"] == [ws[f"{c}{r}"].value for c in "BGH"]      # 指標、口徑、適用對象沿用原紀錄
    for c in DATA["C1"]:
        ws, r = rows[c["id"]]
        assert ws[f"R{r}"].value == "免（C1 官方牌價／規格表；Andy 2026-10-20 17:17）"
    for q in DATA["Q11"]:
        ws, r = rows[q["id"]]
        assert ws[f"L{r}"].value == "中立" and ws[f"M{r}"].value == "ARC Prize 官方自測（官方頁已讀 2026-10-20）"
        assert "v17.2 更正（修訂九；Decisions SL51-01）：原 L 欄（立場）＝『利害關係方』" in ws[f"W{r}"].value
    ws, r = rows["SRC_HAR_007"]
    assert ws[f"L{r}"].value == "利害關係方"
    for sid in Q_NEW:
        ws, r = rows[sid]
        assert ws[f"O{r}"].value == "Alt"
    for sid in ("SRC_DEM_004", "SRC_DEM_005", "SRC_DEM_006"):
        ws, r = rows[sid]
        assert ws[f"L{r}"].value == "利害關係方" and ws[f"R{r}"].value == "—" and ws[f"O{r}"].value == "Active"
    for sid in ("SRC_DEM_004", "SRC_DEM_005"):
        ws, r = rows[sid]
        assert "FT" not in ws[f"M{r}"].value and ws[f"J{r}"].value.startswith("The Information〈")
    ws, r = rows["SRC_DC_010"]
    assert (ws[f"D{r}"].value, ws[f"E{r}"].value) == (50, 60)


def test_v1720_w1_and_gov():
    wb = openpyxl.load_workbook(model_path(), data_only=True)
    ck = wb["Checks"]
    got = {ck.cell(r, 1).value: ck.cell(r, 4).value for r in range(1, ck.max_row + 1) if ck.cell(r, 1).value in ("E7", "E8", "E12", "E13", "W1")}
    assert got == {"E7": 0, "E8": 0, "E12": 0, "E13": 0, "W1": 131}      # v20.0：130 → 131（SRC_DEM_088 缺第二來源）； v19.1：131 → 130（SRC_MOD_018 填 C1 免除標記）

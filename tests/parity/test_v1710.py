"""v17.1 文字修補（工作單 docs/workorders/20261020_v17.1_文字修補.md）專屬測試：與封存的 v17.0 逐格比對，只有 W1–W7 的文字格與版本字串不同；數值（含 LibreOffice 存檔的快取值）一律相同。"""
from pathlib import Path

import openpyxl

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V170 = REPO / "model" / "archive" / "20261020_Tokenomics_v17.0.xlsx"

W_CELLS = {("L1", "B114"), ("L1", "B115"), ("Cap_In", "A314"), ("Cap_In", "A315"), ("Cap_In", "G242"), ("Cap_In", "G243"),
           ("Cap_In", "G232"), ("Cap_In", "G233"), ("Cap_In", "G226"), ("Gov_Map", "M673")}
VERSION_CELLS = {("README", "A1"), ("README", "B5"), ("README", "A63"), ("README", "B63"), ("Alloc", "C177"), ("Alloc", "C178")}      # 版本字串與 README 新列（C177／C178＝RNG_Version／RNG_Current）


def _diffs(data_only):
    a, b = openpyxl.load_workbook(V170, data_only=data_only), openpyxl.load_workbook(model_path(), data_only=data_only)
    assert a.sheetnames == b.sheetnames
    out = set()
    for ws in a:
        wn = b[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                if ws.cell(r, c).value != wn.cell(r, c).value:
                    out.add((ws.title, ws.cell(r, c).coordinate))
    return out, a, b


def test_v1710_formula_and_text_diffs_only_expected():
    d, a, b = _diffs(False)
    exp = W_CELLS | (VERSION_CELLS - {("Alloc", "C178")})      # C178（RNG_Current）是讀 README B5 的公式，公式文字不變
    assert d == exp, sorted(d ^ exp)
    assert set(a.defined_names) == set(b.defined_names) and all(a.defined_names[k].attr_text == b.defined_names[k].attr_text for k in a.defined_names)
    for sh, cell in exp:      # 差異格在 v17.0 與 v17.1 都是文字，且都不是公式
        for wb in (a, b):
            v = wb[sh][cell].value
            assert v is None or (isinstance(v, str) and not v.startswith("=")), (sh, cell)


def test_v1710_no_numeric_value_changes():
    d, a, b = _diffs(True)
    assert d == W_CELLS | VERSION_CELLS, sorted(d ^ (W_CELLS | VERSION_CELLS))      # C178（RNG_Current）為讀 README B5 的公式，快取值是版本字串
    for sh, cell in d:
        for wb in (a, b):
            v = wb[sh][cell].value
            assert v is None or isinstance(v, str), (sh, cell, v)      # 差異格不得有數字


def test_v1710_w_texts():
    wb = openpyxl.load_workbook(model_path())
    ci, l1, gm = wb["Cap_In"], wb["L1"], wb["Gov_Map"]
    assert "（v17.0 起主口徑：F2 已採用，未回應依預設，可撤回；" in ci["A314"].value and "（F2 對照" not in ci["A314"].value
    assert "（v17.0 起主口徑：F1 已採用，未回應依預設，可撤回）" in ci["A315"].value and "F1 對照" not in ci["A315"].value
    assert l1["B114"].value == "壽命期價格係數 L — 折現版（v17.0 起主口徑：F2 已採用，未回應依預設，可撤回；WACC 折現）"
    assert l1["B115"].value == "回本所需 L — 恆等式讀法、不含 κ（v17.0 起主口徑：F1 已採用，未回應依預設，可撤回）"
    assert ci["G242"].value.startswith("文字；現行判讀見 C 欄（v17.0：未定，L 0.759 對所需 L 0.756）｜【v5.35 原說明，已不適用】基準 0.6426 ≥ 0.3645 → 回本（L_total 口徑）｜v15.3 D1：")
    assert ci["G243"].value.startswith("文字；【v5.35 原說明，已不適用】基準 0.6426 ≥ 0.5237 → 回本（L_total 口徑）｜v15.3 D1：")
    assert ci["G232"].value == "壽命期內牌價相對第 0 年的連續平均；數值以 C–E 欄為準（v17.0：基準 0.7637、D 0.5511、E 1.1618）"
    assert ci["G233"].value == "前 T1 年中階牌價、之後 ρ × 中階牌價的連續平均；數值以 C–E 欄為準（v17.0：基準 0.6595、D 0.3963、E 1.0964）"
    assert ci["G226"].value.startswith("藍字三格（登錄 Gov_Map）；現值以 C226:E226 為準（v17.0：基準 −0.09、低 −0.20、高 +0.05）｜原始設定：基準 −0.10、低 −0.25、高 +0.05。依據：")
    assert gm["M673"].value == "3.3–5.9 $/M（v15.2 B2 用量加權；舊區間 2.089–16.33 為在售天數加權，保留於 Cap_In G280）（低、高端的層級對應見註）"
    assert gm["D673"].value == "C280"


def test_v1710_w5_numbers_follow_cells():
    """W5 文字內的數字等於 C232:E233 四捨五入到小數 4 位。"""
    ci = openpyxl.load_workbook(model_path(), data_only=True)["Cap_In"]
    for row, txt in ((232, ci["G232"].value), (233, ci["G233"].value)):
        for col in "CDE":
            assert f"{ci[f'{col}{row}'].value:.4f}".rstrip("0").rstrip(".") in txt, (row, col, txt)

"""v21.5 專屬測試（工作單 docs/workorders/20261025_v21.5_計價倍數新舊約與GM088.md r0）。只改文字與治理欄；讀 LibreOffice 重算後的值。

  1. 全部具名範圍（1,821 個）的值與封存 v21.4 相同，只有版本字串 RNG_Version／RNG_Current 例外；名稱沒有增減。
  2. W1：DB_Evidence E407、E408（接 E406）；W2：Alloc_In G23 加 v21.5 段（C23:E23 值不變）；W4：Decisions SL62-01、README B5 開頭與第 75 列。
  3. W3 保留現狀：Gov_Map H92 仍為 SRC_HW_015（加回 v2130.GOV_MAP_UPD 會使 IDX_SrcID 改變，觸發停止條件）；預期變動 CSV 存在。
  4. GOV 三項計數 0／134／182；RNG_StaleFlag 一致；全部公式格無錯誤值。
  5. 逐格比較 v21.4 → v21.5：數值差異 0 格；文字／公式差異只落在工作單列明的格與版本字串。
"""
import csv
from pathlib import Path

import openpyxl
import pytest
from openpyxl.utils import range_boundaries

from conftest import model_path

REPO = Path(__file__).resolve().parents[2]
V214 = REPO / "model" / "archive" / "20261024_Tokenomics_v21.4.xlsx"
VERSION_NAMES = {"RNG_Version", "RNG_Current"}


def _flat(v):
    if isinstance(v, (list, tuple)):
        return [x for r in v for x in _flat(r)]
    return [v]


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _eq(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if _num(a) and _num(b):
        return abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1e-300) + 1e-12
    return a == b


def _arch_value(pw, d):
    sh, rg = d.attr_text.rsplit("!", 1)
    c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
    return [pw[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


@pytest.fixture(scope="module")
def wbf():
    return openpyxl.load_workbook(model_path())


@pytest.fixture(scope="module")
def pw():
    return openpyxl.load_workbook(V214, data_only=True)


def _row(ws, sid):
    rr = [r for r in range(5, ws.max_row + 1) if ws.cell(r, 1).value == sid]
    assert len(rr) == 1, (sid, rr)
    return rr[0]


# ---------------------------------------------------------------- 1. 具名範圍值不變
def test_v2150_all_names_unchanged(lo, pw, wbf):
    v = lo.view({})
    bad, n = [], 0
    for name, d in wbf.defined_names.items():
        if "!" not in d.attr_text or "," in d.attr_text or name not in pw.defined_names:
            continue
        want = _arch_value(pw, pw.defined_names[name])
        got = _flat(v.get_name(name))
        n += 1
        if not (len(want) == len(got) and all(_eq(a, b) for a, b in zip(want, got))):
            bad.append(name)
    assert n > 1500, n
    assert sorted(bad) == sorted(VERSION_NAMES), bad
    assert set(wbf.defined_names) == set(pw.defined_names)      # 名稱沒有增減


# ---------------------------------------------------------------- 2. 記錄與文字
def test_v2150_evidence_e407_e408(wbf):
    ev = wbf["DB_Evidence"]
    r7, r8 = _row(ev, "E407"), _row(ev, "E408")
    assert (r7, r8) == (331, 332) and ev.cell(r7 - 1, 1).value == "E406"
    for r in (r7, r8):
        assert ev.cell(r, 2).value == "2026-10-25" and ev.cell(r, 10).value == "v21.5" and ev.cell(r, 12).value == "已處理"
        assert ev.cell(r, 5).value == "Interested-party（出租方自揭）" and ev.cell(r, 6).value == "Alloc_In C23（AL_SpendBasis 1.8；0.85–2.3，不改）"
        assert "docs/evidence/20261025_計價倍數_第二出租方/" in ev.cell(r, 4).value and "PR #170" in ev.cell(r, 4).value
    t7 = " ".join(str(ev.cell(r7, c).value) for c in range(1, 19))
    for key in ("0.65–1.32", "CoreWeave 2026 Q1–Q2", "Nebius 2025 Q4", "WhiteFiber 2026 Q2", "弱反對 AL_SpendBasis 1.8；1.8 不改", "實耗讀法 0.46–0.75 只作敏感度，L2",
                "CoreWeave active power 口徑仍未定義（L3，Q3 財報再查）", "冰島 5.5 MW-IT，偏下界"):
        assert key in t7, key
    t8 = " ".join(str(ev.cell(r8, c).value) for c in range(1, 19))
    for key in ("1.36–2.30", "Nebius Q2 大單 ACV 2,000–2,500 萬美元／MW", "1.84–2.30", "WhiteFiber 10-Q Blackwell 新約 1.36–1.86", "支持 AL_SpendBasis 1.8 作為新增容量價",
                "1.8 讀作新舊約混合，不改", "VR200 為 1.64–2.04（L4）", "annual contract value", "Derived", "2,060 萬／MW·年", "3.7–4.6",
                "另記：GB300 IT 資本支出 2026 公開點多數高於 TK 32.2（L5）；IREN 推算營運費用 2.6–3.3（L6），只記錄、不改"):
        assert key in t8, key


def test_v2150_alloc_in_g23(wbf):
    ai = wbf["Alloc_In"]
    assert (ai["C23"].value, ai["D23"].value, ai["E23"].value, ai["F23"].value) == (1.8, 0.85, 2.3, "Derived")      # 值不改
    g = ai["G23"].value
    assert g.startswith("v21.5：出租方錨點依合約時點分兩群——存量機隊平均約 0.65–1.32（CoreWeave、Nebius、WhiteFiber），2026 新約約 1.36–2.30"
                        "（Nebius、IREN 自報新約 1.84–2.30；WhiteFiber 10-Q 新約 1.36–1.86）；1.8 讀作新舊約混合，值不改（E407、E408；PR #170）。｜v21.3（")
    assert g.count("v21.5：") == 1 and g.endswith("｜原說明（v21.1 以前）：經濟口徑：依據的價格 ÷ 會計成本 1.16 × 會計 ÷ 經濟持有成本 0.73 ≈ 0.85（區間 0.73–1.17）；分母維持經濟口徑持有成本。"
                                                 "小於 1 表示 Azure 計價未涵蓋全部資本成本，這本身是 m 的一項實質命題（決定紀錄 D10）")


def test_v2150_decisions_readme(wbf):
    d = wbf["Decisions"]
    r = _row(d, "SL62-01")
    assert r == 334 and d.cell(r - 1, 1).value == "SL61-01" and d.cell(r, 2).value == "v21.5" and d.cell(r, 7).value == "v21.5 已建"
    txt = d.cell(r, 4).value + d.cell(r, 6).value
    for key in ("E407", "E408", "Alloc_In G23", "IDX_SrcID", "SRC_Index!A980", "VR200 P×Q 營收的 IF_ 名稱", "IF_PxEffMix_Lo／_Hi", "新增契約名稱即主版升級", "PR #170", "v21.4 報告 P1"):
        assert key in txt, key
    rm = wbf["README"]
    b5 = str(rm["B5"].value)
    assert b5.startswith("20261025_Tokenomics_v21.5（次版，底版 v21.4：") and "只改文字與治理欄；所有契約名稱的值不變（版本字串除外）；GOV 三項計數 0／134／182 不變。" in b5
    assert "v21.4（次版，底版 v21.3：" in b5 and str(rm["A1"].value).startswith("Tokenomics v21.5")
    rr = [x for x in range(4, rm.max_row + 1) if rm.cell(x, 1).value == "v21.5 計價倍數新舊約混合登錄（Gov_Map GM088 暫緩）"]
    assert rr == [75] and "只改文字與治理欄，所有契約名稱的值不變" in rm.cell(75, 2).value


# ---------------------------------------------------------------- 3. W3 保留現狀
def test_v2150_w3_held(wbf, lo):
    gm = wbf["Gov_Map"]
    rows = [r for r in range(5, gm.max_row + 1) if gm.cell(r, 3).value == "Spec_Rack" and gm.cell(r, 4).value == "F11"]
    assert rows == [92]
    assert gm["H92"].value == "SRC_HW_015" and gm["I92"].value == "Derived：MS BOM 7.8（零毛利下限；r3 I2）"      # 未套用 v2130.GOV_MAP_UPD
    csv_path = REPO / "docs" / "workorders" / "20261025_v21.5_預期變動.csv"
    rows = list(csv.reader(open(csv_path, encoding="utf-8-sig")))
    assert {(r[0], r[1]) for r in rows[1:]} >= {("Gov_Map", "H92"), ("Gov_Map", "R92"), ("Gov_Map", "AF92"), ("SRC_Index", "A980"), ("具名範圍 IDX_SrcID", "SRC_Index!A5:A1588")}
    assert wbf["Spec_Rack"]["F11"].value == 7.5      # 輸入值不改


# ---------------------------------------------------------------- 4. GOV
def test_v2150_gov_counts(lo):
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 134, 182)
    assert v.get_name("RNG_StaleFlag") == "一致" and v.get_name("RNG_OutCount") == 0
    assert str(v.get_name("RNG_Version")).endswith("v21.5") and str(v.get_name("RNG_Current")).endswith("v21.5")
    errs = [(s, c) for (s, c), x in v.evaluate_all().items() if isinstance(x, str) and x.startswith("#")]
    assert errs == []


# ---------------------------------------------------------------- 5. 逐格比較 v21.4 → v21.5
EXACT_CELLS = {
    "README": {"A1", "B5", "A75", "B75"}, "Alloc": {"C177"}, "Alloc_In": {"G23"},
    "Decisions": {f"{c}334" for c in "ABCDEFGHIJ"},
    "DB_Evidence": {f"{c}{r}" for r in (331, 332) for c in "ABCDEFGHIJKLMNOPQR"},
}


def test_v2150_cell_diffs_only_expected():
    a, b = openpyxl.load_workbook(V214), openpyxl.load_workbook(model_path())
    av, bv = openpyxl.load_workbook(V214, data_only=True), openpyxl.load_workbook(model_path(), data_only=True)
    assert a.sheetnames == b.sheetnames
    fd, nd = {}, []
    for ws in a:
        wn, va, vb = b[ws.title], av[ws.title], bv[ws.title]
        for r in range(1, max(ws.max_row, wn.max_row) + 1):
            for c in range(1, max(ws.max_column, wn.max_column) + 1):
                x, y = ws.cell(r, c).value, wn.cell(r, c).value
                if x != y:
                    fd.setdefault(ws.title, set()).add(ws.cell(r, c).coordinate)
                p, q = va.cell(r, c).value, vb.cell(r, c).value
                if _num(p) and _num(q) and not _eq(p, q):
                    nd.append((ws.title, ws.cell(r, c).coordinate, p, q))
    assert fd == EXACT_CELLS, {k: sorted(fd.get(k, set()) ^ EXACT_CELLS.get(k, set())) for k in set(fd) | set(EXACT_CELLS) if fd.get(k, set()) != EXACT_CELLS.get(k, set())}
    assert nd == [], nd      # 數值差異 0 格
    for sh, cells in fd.items():
        for coord in cells:
            x, y = a[sh][coord].value, b[sh][coord].value
            assert not (isinstance(x, str) and x.startswith("=")) or sh in ("README", "Alloc"), (sh, coord)

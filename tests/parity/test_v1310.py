"""D15 B 段（v13.1）專屬測試：區間時效指紋（P2-2）、既有契約名稱不變（P1 驗收）。
讀 LibreOffice 重算後的值；不刪除、不放寬任何既有測試。"""
import json
from pathlib import Path

import openpyxl
from openpyxl.utils import range_boundaries

from conftest import model_path
import deadcells_lib

REPO = Path(__file__).resolve().parents[2]
V130_PREV = REPO / "model" / "archive" / "20261017_Tokenomics_v13.0.xlsx"      # v13.0（LibreOffice 重算存檔）：v13.1 的「既有名稱不得變」對照
CONTRACT_PREFIX = ("IF_", "IFW_", "IFC_", "L1_", "CHK_", "CAP_", "RNG_")
NEW_IN_V131 = {"RNG_Version", "RNG_Current"}      # 版本字串，隨版本改變
PREWARM = {}


def _flat(v):
    if isinstance(v, list):
        return [x for r in v for x in _flat(r)]
    return [v]


def _same(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return (a in (None, "") and b in (None, "")) or a == b


def _chk_row(v, code):
    for r in range(1, 400):
        if v.get("Checks", f"A{r}") == code:
            return r
    raise AssertionError(code)


def _fp():
    return json.loads((REPO / "builder" / "v1310_fingerprint.json").read_text(encoding="utf-8"))


def _pick_leaf(fp):
    """Inputs 頁中第一個非零數值葉格（改動後模型仍可重算）。"""
    for s, a, v in fp["leaves"]:
        if s == "Inputs" and isinstance(v, (int, float)) and v != 0:
            return s, a, v
    raise AssertionError("指紋中沒有 Inputs 頁葉格")


PREWARM["test_v1310_fingerprint_flag_fires"] = [{f"{_pick_leaf(_fp())[0]}!{_pick_leaf(_fp())[1]}": _pick_leaf(_fp())[2] * 1.01}]


def test_v1310_fingerprint_file_matches_workbook(lo):
    """builder/v1310_fingerprint.json（tools/gen_fingerprint.py 的輸出）與現行 Excel 的上游數值常數格逐格相同；版本字串等於現行版本；
    基準時效旗標『一致』、Checks RG3 為 0；GOV_Warnings 280。"""
    rng = json.loads((REPO / "builder" / "v1300_ranges.json").read_text(encoding="utf-8"))
    leaves = deadcells_lib.upstream_numeric_leaves(model_path(), sorted(rng["names"]))
    fp = _fp()
    assert fp["version"] == model_path().name[: -len(".xlsx")] == rng["version"]
    assert [(s, a) for s, a, _ in fp["leaves"]] == [(s, a) for s, a, _ in leaves], "葉格集合不同"
    bad = [(s, a, v, w) for (s, a, v), (_, _, w) in zip(fp["leaves"], leaves) if not _same(v, w)]
    assert bad == [], (len(bad), bad[:8])
    assert len(fp["leaves"]) == 579
    base = lo.view({})
    assert base.get_name("RNG_StaleFlag") == "一致" and base.get("Checks", f"D{_chk_row(base, 'RG3')}") == 0
    assert base.get("Checks", f"D{_chk_row(base, 'RG1')}") == 0 and base.get("Checks", f"D{_chk_row(base, 'RG2')}") == 0
    assert (base.get_name("GOV_Errors"), base.get_name("GOV_Warnings")) == (0, 280)


def test_v1310_fingerprint_flag_fires(lo):
    """P2-2：只改上游一個輸入（Inputs 的第一個數值葉格 ×1.01），不重新產生端點與指紋——基準仍可能在 Lo／Hi 之內，
    但 RNG_StaleFlag 必須顯示『區間過期』，Checks RG3 觸發（舊的兩道檢查——版本字串、基準出區間——抓不到這種情況）。"""
    s, a, v = _pick_leaf(_fp())
    edited = lo.view({f"{s}!{a}": v * 1.01})
    assert edited.get_name("RNG_StaleFlag") == "區間過期"
    assert edited.get("Checks", f"D{_chk_row(edited, 'RG3')}") == 1
    assert edited.get_name("RNG_Version") == edited.get_name("RNG_Current")      # 版本字串仍相符：只有指紋抓到
    base = lo.view({})
    assert base.get_name("RNG_StaleFlag") == "一致"


def test_v1310_existing_contract_names_unchanged(lo):
    """D15 B 段驗收：v13.0 既有的 IF_／IFW_／IFC_／L1_／CHK_／CAP_／RNG_ 名稱，值與 v13.0 逐格相同（容差 1e-9）；
    只有 RNG_Version／RNG_Current 兩個版本字串可以不同（隨版本更新）。"""
    prev = openpyxl.load_workbook(V130_PREV, data_only=True)
    v = lo.view({})
    keep = [n for n in prev.defined_names if n.startswith(CONTRACT_PREFIX) and n not in NEW_IN_V131]
    assert len(keep) >= 600, len(keep)
    for n in keep:
        sh, rg = prev.defined_names[n].attr_text.rsplit("!", 1)
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        want = [prev[sh.strip("'")].cell(r, c).value for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
        got = _flat(v.get_name(n))
        assert len(want) == len(got) and all(_same(a, b) for a, b in zip(want, got)), n
    assert v.get_name("RNG_Version") == model_path().name[: -len(".xlsx")]

"""4-2a F5（查核 D 第 4 項）：契約名稱快照、驗證清單逐項斷言、GOV 三項計數（新基準）。
讀 LibreOffice 重算後的值（`lo.view({})`，即新 SLO 基準；其他測試的 `_vo` 會改回舊 SLO，所以 GOV 計數在新基準下需要在這裡斷言）。

快照更新規則：之後每個版本若有預期變動，必須在同一個 PR 以 `python3 tools/make_test_fixtures.py <重算後的 xlsx>` 更新
tests/parity/fixtures/contract_snapshot_v10.3.json，並在報告列出差異（名稱、舊值、新值、理由）。不得為了讓測試通過而更新快照。"""
import json
import re
from pathlib import Path

import pytest
from openpyxl.utils import get_column_letter as L, range_boundaries

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAP = json.loads((FIXTURES / "contract_snapshot_v10.3.json").read_text(encoding="utf-8"))
ROOT_PREFIX = ("IF_", "L1_", "GOV_", "IFW_", "IFC_", "CHK_", "CAP_")


def _cells(attr):
    out = []
    for part in attr.lstrip("=").split(","):
        sh, rg = part.rsplit("!", 1)
        sh = sh.strip("'").replace("''", "'")
        c1, r1, c2, r2 = range_boundaries(rg.replace("$", ""))
        out += [(sh, f"{L(c)}{r}") for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]
    return out


def _same(a, b):
    a = None if a == "" else a
    b = None if b == "" else b
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-12 or abs(a - b) <= 1e-9 * max(abs(a), abs(b))
    return a == b


def test_contract_snapshot_values(lo):
    """契約名稱（下游契約文件所列＋全部 IF_／IFW_／IFC_／L1_／GOV_／CHK_／CAP_）逐格值等於 v10.3 快照（相對容差 1e-9）。"""
    v = lo.view({})
    bad, ncell = [], 0
    for name, rec in SNAP["names"].items():
        assert name in v.names, f"快照中的名稱已不存在：{name}（契約名稱不得刪除）"
        assert v.names[name] == rec["ref"], (name, v.names[name], rec["ref"])
        cells = _cells(rec["ref"])
        assert len(cells) == len(rec["values"]), name
        for (sh, a), want in zip(cells, rec["values"]):
            got = v.get(sh, a)
            ncell += 1
            if not _same(got, want):
                bad.append((name, f"{sh}!{a}", want, got))
    assert ncell == SNAP["n_cells"]
    assert bad == [], (len(bad), bad[:12])


def test_snapshot_covers_every_prefix_name(lo):
    """新增的 IF_／IFW_／IFC_／L1_／GOV_／CHK_／CAP_ 名稱必須同時加進快照（避免新名稱沒有人看守）。"""
    v = lo.view({})
    cur = {n for n, t in v.names.items() if n.startswith(ROOT_PREFIX) and "!" in t}
    missing = sorted(cur - set(SNAP["names"]))
    assert missing == [], missing


# 驗證清單 V1–V19：模型 ÷ 對照（或模型值）與通過判定（v10.3 的 LibreOffice 重算值；列 E＝比值，F＝1 通過／0 失敗）。
# 數值與判定隨輸入改變；預期變動時在同一個 PR 更新此表並於報告列出（同快照規則）。
VERIFY_EXPECTED = {
    "V1": (1.21767628625269, 0), "V2": (0.718430345941003, 1), "V3": (0.904516154853064, 1), "V4": (0.702796711119185, 1),
    "V5": (0.494242858903564, 1), "V6": (0.689214136000581, 1), "V7": (0.267266126717592, 0), "V8": (0.261055812652461, 0),
    "V9": (0.379829822080908, 0), "V10": (0.371397626434424, 0), "V11": (0.7, 0), "V12": (0.99108369917347, 1),
    "V13": (2.18428412747673, 1), "V14": (4.1124545381639, 0), "V15": (0.266287875672857, 0), "V16": (0.0852702650102943, 1),
    "V17": (0.252262860133895, 1), "V18": (0, 1), "V19": (0, 1),
}


def _verify_rows(v):
    rows = {}
    for r in range(1, 400):
        a = v.get("Checks", f"A{r}")
        if isinstance(a, str) and re.fullmatch(r"V\d+", a):
            rows[a] = r
    return rows


@pytest.mark.parametrize("vid", sorted(VERIFY_EXPECTED, key=lambda x: int(x[1:])))
def test_verify_item(lo, vid):
    """驗證清單逐項：比值、通過判定，以及判定與通過帶（H 下限、I 上限）一致。"""
    v = lo.view({})
    r = _verify_rows(v)[vid]
    ratio, passed = VERIFY_EXPECTED[vid]
    e, f = v.get("Checks", f"E{r}"), v.get("Checks", f"F{r}")
    assert _same(e, ratio), (vid, e, ratio)
    assert f == passed, (vid, f, passed)
    lo_b, hi_b = v.get("Checks", f"H{r}"), v.get("Checks", f"I{r}")
    inside = e >= lo_b and (hi_b in ("", None) or e <= hi_b)
    assert (1 if inside else 0) == f, (vid, e, lo_b, hi_b, f)


def test_verify_totals_and_list_complete(lo):
    """清單完整（V1–V19 共 19 項，無缺列）；CHK_VerifyTotal／Pass／Fail＝19／11／8（v10.2：17／9／8，F3 新增 V18、V19 皆通過）。"""
    v = lo.view({})
    assert sorted(_verify_rows(v), key=lambda x: int(x[1:])) == [f"V{i}" for i in range(1, 20)]
    assert (v.get_name("CHK_VerifyTotal"), v.get_name("CHK_VerifyPass"), v.get_name("CHK_VerifyFail")) == (19, 11, 8)
    assert sum(p for _, p in VERIFY_EXPECTED.values()) == 11


def test_gov_counts_new_baseline(lo):
    """GOV 三項計數在新基準（Serving 第 21 列為兩家量測商幾何平均）下：Errors 0、Warnings 279、Info 179。"""
    v = lo.view({})
    assert (v.get_name("GOV_Errors"), v.get_name("GOV_Warnings"), v.get_name("GOV_Info")) == (0, 279, 179)

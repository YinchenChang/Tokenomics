"""4-3 B 段 Q1：刪除清單的依賴再確認（只讀 v13.1）。
用法：python3 docs/evidence/20261017_4-3B/01_delete_deps.py <model.xlsx> <out.json>
刪除清單＝A 段明細「1_逐列建議」處置＝刪除的 72 列，加上 Har_In 44（B5_SelVendor）。
對每個刪除格找『會讀它的東西』：
  (a) 任何不在刪除集合內的公式格，其公式（含範圍、具名範圍展開）涵蓋該格；
  (b) 任何具名範圍直接指向該格；
  (c) Gov_Map／Decisions／DB_Evidence 等治理頁以外的文字不查（只查公式）。
輸出：被讀取的刪除列（需改為保留）與讀取者。"""
import collections
import json
import sys
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter as L, range_boundaries

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "tests" / "parity"))
import deadcells_lib as D  # noqa: E402

DETAIL = REPO / "docs" / "reports" / "20261017_4-3A_建議_明細.xlsx"


def delete_rows():
    ws = openpyxl.load_workbook(DETAIL)["1_逐列建議"]
    rows = []
    for r in ws.iter_rows(min_row=3, values_only=True):
        if r[0] and r[7] == "刪除":
            rows.append((r[0], r[1], r[2], r[5]))
    rows.append(("Har_In", 44, "供應商專屬（1＝是）", "C44:G44"))      # Andy 2026-10-17 09:18：刪除
    return rows


def cells_of(rng):
    c1, r1, c2, r2 = range_boundaries(rng)
    return [f"{L(c)}{r}" for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)]


def main(model, out):
    cells, names, maxrc, sheets = D.load_formulas(model)
    rows = delete_rows()
    # 刪除格＝該列『格範圍』內目前有內容的格；Har_In 44 以整列有值的格計
    dele = set()
    per_row = {}
    for sh, r, lab, rng in rows:
        cs = [(sh, a_) for a_ in cells_of(rng) if (sh, a_) in cells]
        per_row[(sh, r)] = cs
        dele |= set(cs)
    edges = D.build_graph(cells, names, maxrc)
    # 反向邊
    rev = collections.defaultdict(set)
    for a, bs in edges.items():
        for b in bs:
            rev[b].add(a)

    def readers(node, seen):
        out_ = set()
        for p in rev.get(node, ()):
            if p in seen:
                continue
            seen.add(p)
            if p[0] in ("NAME", "RANGE"):
                out_.add(p)                       # 範圍／名稱本身也列出
                out_ |= readers(p, seen)
            else:
                out_.add(p)
        return out_

    res = {}
    for (sh, r), cs in per_row.items():
        rd = set()
        for c in cs:
            rd |= readers(c, set())
        rd = {x for x in rd if x not in dele}
        # 只保留『真正的公式格或具名範圍』；RANGE 節點若沒有任何公式格使用則不算
        real = sorted(x for x in rd if x[0] != "RANGE")
        res[f"{sh}!{r}"] = dict(label=[x for x in rows if x[0] == sh and x[1] == r][0][2], ncell=len(cs), readers=[f"{a}!{b}" if a != "NAME" else f"NAME:{b}" for a, b in real][:30], n_readers=len(real))
    Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {k: v for k, v in res.items() if v["n_readers"]}
    print("刪除列", len(res), "刪除格", len(dele), "被讀取的列", len(bad))
    for k, v in bad.items():
        print(k, v["label"], v["n_readers"], v["readers"][:6])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

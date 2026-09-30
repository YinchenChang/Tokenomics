"""網站共用：載入引擎、以具名範圍取 Interface 資料、以標籤定位 Calib 驗證表。

規則（CLAUDE.md 第 1、6 節）：不含任何數值、價格或參數；標籤、單位、世代名稱全部來自 Excel。
Interface 資料只走具名範圍。世代與成本情境的表頭、Calib 驗證表沒有具名範圍，
以「欄 A 標籤」定位（不寫死位址）；建議 Excel 端補具名範圍（見每輪報告）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from openpyxl.utils import get_column_letter, range_boundaries

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine import Engine  # noqa: E402

# 欄位映射：Interface 具名範圍前綴 → 網站顯示順序（Block 2；標籤與單位取自 Excel）
BLOCK2_METRICS = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")
_TIER_NAME = re.compile(r"^IF_(?P<metric>%s)_(?P<tier>\w+)$" % "|".join(BLOCK2_METRICS))


@st.cache_resource(show_spinner="首次載入：以公式引擎建立並重算整份 Excel（約 10–15 秒）…")
def get_engine() -> Engine:
    return Engine()


def _label(text: str) -> str:
    """去掉標籤尾端的 '　[IF_…]' 具名範圍標註。"""
    return re.sub(r"\s*\[IF_\w+\]\s*$", "", text).strip("　 ")


def _header_rows(eng: Engine, sheet: str) -> tuple[int, int]:
    labels = dict((v, r) for r, v in eng.column_labels(sheet, "A"))
    return labels["指標"], labels["成本情境"]


def interface_series(eng: Engine, name: str) -> dict:
    """單一 Interface 具名範圍 → {label, unit, values, gens, cases}（列向範圍；純量則 gens/cases 為空）。"""
    sheet, ref = eng.name_ref(name)
    c1, r1, c2, _ = range_boundaries(ref)
    label = _label(str(eng.get(sheet, f"A{r1}")))
    unit = eng.get(sheet, f"B{r1}")
    values = eng.get_name(name)
    if not isinstance(values, list):
        return {"label": label, "unit": unit, "values": [values], "gens": [""], "cases": [""]}
    hg, hc = _header_rows(eng, sheet)
    span = lambda r: eng.get(sheet, f"{get_column_letter(c1)}{r}:{get_column_letter(c2)}{r}")[0]  # noqa: E731
    return {"label": label, "unit": unit, "values": values, "gens": span(hg), "cases": span(hc)}


def tiers(eng: Engine) -> dict[str, str]:
    """層級 → 顯示標題（如 'Luna（低層）'；由 Interface 欄 A 的分區標題取得）。順序＝Excel 列順序。"""
    found = {}
    for n in eng.names:
        m = _TIER_NAME.match(n)
        if m and m["metric"] == "TokGW":
            found[m["tier"]] = eng.name_ref(n)[1]
    order = sorted(found, key=lambda t: int(re.search(r"\d+", found[t]).group()))
    heads = {v: r for r, v in eng.column_labels("Interface", "A")}
    return {t: next((h for h in heads if h.startswith(t)), t) for t in order}


def fmt(v) -> str:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v)
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.4g}"


def block2_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """列＝指標（Excel 標籤＋單位，前綴層級）；欄＝世代；只取所選成本情境。"""
    rows = {}
    for metric in BLOCK2_METRICS:
        s = interface_series(eng, f"IF_{metric}_{tier}")
        picked = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
        rows[f"{tier}｜{s['label']}（{s['unit']}）"] = picked
    return pd.DataFrame(rows).T


def cost_cases(eng: Engine) -> list[str]:
    s = interface_series(eng, "IF_TokGW_" + next(iter(tiers(eng))))
    return list(dict.fromkeys(s["cases"]))


# ── Calib 驗證表（F 節：模型 ÷ 實測；H 節：模型 ÷ MLPerf）─────────────
def _section_bounds(labels: list[tuple[int, str]]) -> dict[str, tuple[int, int]]:
    starts = [(r, v[0]) for r, v in labels if re.match(r"^[A-Z]\. ", v)]
    end = labels[-1][0] + 1
    return {k: (r, (starts[i + 1][0] if i + 1 < len(starts) else end)) for i, (r, k) in enumerate(starts)}


def _find(labels, lo, hi, text, exact=False):
    for r, v in labels:
        if lo <= r < hi and (v == text if exact else v.startswith(text)):
            return r
    raise KeyError(f"Calib 找不到列標籤：{text}")


def calib_validation(eng: Engine) -> pd.DataFrame:
    sh = "Calib"
    labels = eng.column_labels(sh, "A")
    sec = _section_bounds(labels)

    def row(sec_key, text, n, exact=False):
        lo, hi = sec[sec_key]
        r = _find(labels, lo, hi, text, exact)
        return eng.row_values(sh, r, "C")[:n], str(eng.get(sh, f"A{r}"))

    out = []
    # F 節：錨點列在 B 節，模型值在 F 節
    n = len([x for x in eng.row_values(sh, _find(labels, *sec["B"], "用途"), "C") if x != ""])
    purpose, _ = row("B", "用途", n)
    gen, _ = row("B", "世代", n, exact=True)
    soft, _ = row("B", "軟體／日期", n)
    speed, _ = row("B", "每用戶速度", n)
    meas, meas_lbl = row("B", "實測 tok/s/GPU", n)
    src, _ = row("B", "來源", n)
    plat, _ = row("B", "量測平台", n)
    model, model_lbl = row("F", "模型 tok/s/GPU", n)
    ratio, _ = row("F", "模型 ÷ 實測", n)
    note, _ = row("F", "判讀", n)
    for i in range(n):
        out.append({"節": "F", "驗證點": f"F{i + 1}", "用途": purpose[i], "世代": gen[i], "軟體／日期": soft[i],
                    "量測平台": plat[i], "來源": src[i], "每用戶速度 tok/s": speed[i], "實測 tok/s/GPU": meas[i],
                    "模型 tok/s/GPU": model[i], "模型 ÷ 實測": ratio[i], "口徑（Excel 列標籤）": f"{meas_lbl}／{model_lbl}",
                    "判讀": note[i]})
    # H 節：無逐點「量測平台」列 → 取節標題（Excel 端缺口，見報告）
    h_title = str(eng.get(sh, f"A{sec['H'][0]}"))
    h_platform = re.sub(r"^H\.\s*第二來源驗證：", "", h_title)
    pts, _ = row("H", "驗證點", 12, exact=True)
    m = len([x for x in pts if x != ""])
    pts = pts[:m]
    gidx, _ = row("H", "世代索引", m, exact=True)
    gnames = eng.row_values(sh, _find(labels, *sec["E"], "世代", exact=True), "C")
    speed, _ = row("H", "每用戶速度下限", m)
    meas, meas_lbl = row("H", "MLPerf 實測輸出", m)
    model, model_lbl = row("H", "模型輸出", m)
    ratio, _ = row("H", "模型 ÷ MLPerf", m, exact=True)
    for i in range(m):
        g = gnames[int(gidx[i]) - 1] if isinstance(gidx[i], (int, float)) else ""
        out.append({"節": "H", "驗證點": f"H{i + 1}", "用途": "第二來源驗證", "世代": g, "軟體／日期": pts[i],
                    "量測平台": h_platform, "來源": "—", "每用戶速度 tok/s": speed[i], "實測 tok/s/GPU": meas[i],
                    "模型 tok/s/GPU": model[i], "模型 ÷ 實測": ratio[i], "口徑（Excel 列標籤）": f"{meas_lbl}／{model_lbl}",
                    "判讀": "—"})
    return pd.DataFrame(out)


def calib_platform_note(eng: Engine) -> str:
    """Excel 在「量測平台」列尾端（超出資料欄）附的說明文字。"""
    labels = eng.column_labels("Calib", "A")
    r = _find(labels, *_section_bounds(labels)["B"], "量測平台")
    vals = [x for x in eng.row_values("Calib", r, "C") if isinstance(x, str) and len(x) > 40]
    return vals[-1] if vals else ""

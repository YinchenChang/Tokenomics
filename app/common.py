"""網站共用：載入引擎，並只經由具名範圍取 Excel 的資料。

規則（CLAUDE.md 第 1、6 節）：不含任何數值、價格或參數；標籤、單位、世代與層級名稱全部來自 Excel。
- IF_（非 IF_Hdr）：Interface 輸出，下游模型連結用。
- IF_HdrGen／IF_HdrCost：Interface 表頭（世代、成本情境）——僅供顯示。
- DRV_：Perf 推導鏈——僅供顯示。
- CAL_：Calib 校準值與驗證表——僅供顯示。
列標籤與單位取具名範圍所在列的欄 A、欄 B（由名稱解析出列號，不搜尋標籤、不寫死位址）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from openpyxl.utils import range_boundaries

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from engine import Engine  # noqa: E402

# 欄位映射：Interface 具名範圍前綴（Block 2；依網站顯示順序）
BLOCK2_METRICS = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")
# 推導鏈顯示順序（由物理量到成本；DRV_Gen、DRV_Tier 為欄名）
DRV_CHAIN = ("FlopDec", "FlopPre", "WeightGB", "TfixMs", "SeqMs", "SeqBind", "Batch", "Bind",
             "DecTokGPU", "PreTokGPU", "PreShare", "RackTok", "GWTok", "CostDec", "Close")
_BLOCK2_NAME = re.compile(r"^IF_(?P<metric>%s)_(?P<tier>\w+)$" % "|".join(BLOCK2_METRICS))


def is_downstream_name(name: str) -> bool:
    """下游模型只可連結 IF_ 開頭且非 IF_Hdr 的名稱。"""
    return name.startswith("IF_") and not name.startswith("IF_Hdr")


@st.cache_resource(show_spinner="首次載入：以公式引擎建立並重算整份 Excel（約 10–15 秒）…")
def get_engine() -> Engine:
    return Engine()


def _label(text: str) -> str:
    """去掉標籤尾端的 '　[IF_…]' 具名範圍標註。"""
    return re.sub(r"\s*\[IF_\w+\]\s*$", "", text).strip("　 ")


def series(eng: Engine, name: str) -> dict:
    """具名範圍 → {label, unit, values, cols}；cols＝各值所在欄（0 起，相對工作表 A 欄），供對齊表頭。"""
    sheet, ref = eng.name_ref(name)
    c1, r1, c2, _ = range_boundaries(ref)
    label = _label(str(eng.get(sheet, f"A{r1}")))
    unit = eng.get(sheet, f"B{r1}")
    values = eng.get_name(name)
    values = values if isinstance(values, list) else [values]
    return {"label": label, "unit": unit, "values": values, "cols": list(range(c1, c1 + len(values)))}


def _by_col(eng: Engine, name: str) -> dict[int, object]:
    s = series(eng, name)
    return dict(zip(s["cols"], s["values"]))


def interface_series(eng: Engine, name: str) -> dict:
    """Interface 具名範圍，加上世代與成本情境（取自 IF_HdrGen、IF_HdrCost，依欄對齊）。"""
    s = series(eng, name)
    gens, cases = _by_col(eng, "IF_HdrGen"), _by_col(eng, "IF_HdrCost")
    if len(s["values"]) == 1 and s["cols"][0] not in gens:   # 純量（例：IF_Util）
        s["gens"], s["cases"] = [""], [""]
    else:
        s["gens"] = [gens[c] for c in s["cols"]]
        s["cases"] = [cases[c] for c in s["cols"]]
    return s


def tiers(eng: Engine) -> dict[str, str]:
    """層級 → 顯示標題（如 'Luna' → 'Luna（低層）'）；取自 DRV_Tier，順序＝Excel 欄順序。"""
    out = {}
    for title in eng.get_name("DRV_Tier"):
        out.setdefault(str(title).split("（")[0], str(title))
    return out


def cost_cases(eng: Engine) -> list[str]:
    return list(dict.fromkeys(eng.get_name("IF_HdrCost")))


def fmt(v) -> str:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return str(v)
    return f"{v:,.0f}" if abs(v) >= 1000 else f"{v:.4g}"


def fmt_unit(v, unit) -> str:
    """單位為 % 的格，Excel 存小數（0.6 ＝ 60%）；其餘沿用 fmt。"""
    if unit == "%" and isinstance(v, (int, float)) and not isinstance(v, bool):
        return f"{v * 100:.4g}%"
    return fmt(v)


def block2_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """列＝指標（Excel 標籤＋單位，前綴層級）；欄＝世代；只取所選成本情境。"""
    rows = {}
    for metric in BLOCK2_METRICS:
        s = interface_series(eng, f"IF_{metric}_{tier}")
        picked = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
        rows[f"{tier}｜{s['label']}（{s['unit']}）"] = picked
    return pd.DataFrame(rows).T


def drv_table(eng: Engine, tier: str) -> pd.DataFrame:
    """推導鏈：列＝DRV_ 中間量（依 DRV_CHAIN 順序），欄＝世代；只取所選層級的欄（欄名取 DRV_Gen、DRV_Tier）。"""
    gens, tier_of = _by_col(eng, "DRV_Gen"), _by_col(eng, "DRV_Tier")
    keep = [c for c in gens if str(tier_of[c]).split("（")[0] == tier]
    rows = {}
    for key in DRV_CHAIN:
        s = series(eng, f"DRV_{key}")
        by = dict(zip(s["cols"], s["values"]))
        unit = f"（{s['unit']}）" if s["unit"] not in (None, "") else ""
        rows[f"{s['label']}{unit}"] = {gens[c]: fmt_unit(by[c], s["unit"]) for c in keep}
    return pd.DataFrame(rows).T


def calib_scalars(eng: Engine) -> list[tuple[str, str]]:
    """校準值（CAL_EtaD、CAL_TlayerUs）：(標籤（單位）, 顯示值)。"""
    out = []
    for n in ("CAL_EtaD", "CAL_TlayerUs"):
        s = series(eng, n)
        out.append((f"{s['label']}（{s['unit']}）", fmt_unit(s["values"][0], s["unit"])))
    return out


def calib_validation(eng: Engine) -> pd.DataFrame:
    """驗證表：F 節（模型 ÷ 實測）與 H 節（模型 ÷ MLPerf）；每列都有「量測平台」。"""
    rows = []
    for sec in ("F", "H"):
        lab, plat, ratio = (series(eng, f"CAL_{sec}_{k}") for k in ("Label", "Platform", "Ratio"))
        assert len(lab["values"]) == len(plat["values"]) == len(ratio["values"])
        for i, (a, b, r) in enumerate(zip(lab["values"], plat["values"], ratio["values"]), start=1):
            rows.append({"節": sec, "驗證點": f"{sec}{i}", "點位": a, "點位欄（Excel 列標籤）": lab["label"],
                         "量測平台": b, "比值定義": ratio["label"], "比值（x）": r})
    return pd.DataFrame(rows)

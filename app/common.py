"""網站共用：載入引擎，並只經由具名範圍取 Excel 的資料。

規則（CLAUDE.md 第 1、6 節）：不含任何數值、價格或參數；標籤、單位、世代與層級名稱全部來自 Excel。
- IF_（非 IF_Hdr）：Interface 輸出，下游模型連結用。
- IF_HdrGen／IF_HdrCost：Interface 表頭（世代、成本情境）——僅供顯示。
- DRV_：Perf 推導鏈——僅供顯示。
- CAL_：Calib 校準值與驗證表——僅供顯示。
- TRN_：Training 推導鏈（Block 3）——僅供顯示。
列標籤與單位取具名範圍所在列的欄 A、欄 B（由名稱解析出列號，不搜尋標籤、不寫死位址）。
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

# 欄位映射：Interface 具名範圍前綴（Block 2；依網站顯示順序）
BLOCK2_METRICS = ("TokRack", "TokRackD", "TokGW", "VReq", "CostPre", "CostCache", "CostDec", "CostDecAcct", "TokPerJ")
# 欄位映射：Interface 具名範圍前綴（Block 3；依網站顯示順序，與 Interface C 節列序一致）
BLOCK3_METRICS = ("TrainGPUh", "TrainCost", "PostShareFLOP", "PostShareGPUh", "RLMFU", "ProgGPUh", "ProgCost", "ProgGWyr")
# J13（Andy 決定）：下游預設訓練世代與並列世代，由 Interface 的具名範圍 IF_TrainGenDefault／IF_TrainGenAlt 給出（世代索引，
# 對應 Spec_Rack 世代列的順序，亦即 IF_HdrGen 去重後的順序）。網站只用來把這兩個世代排在最前面。
TRAIN_GEN_NAMES = ("IF_TrainGenDefault", "IF_TrainGenAlt")
# 推導鏈顯示順序（由物理量到成本；DRV_Gen、DRV_Tier 為欄名）。
# "CostDec" 不讀 DRV_CostDec（只有基準成本），改讀 IF_CostDec_<層級>，跟隨成本情境選擇器。
DRV_CHAIN = ("FlopDec", "FlopPre", "WeightGB", "TfixMs", "SeqMs", "SeqBind", "Batch", "Bind",
             "DecTokGPU", "PreTokGPU", "PreShare", "RackTok", "GWTok", "CostDec", "Close")
BLOCK3_SCALARS = ("IF_RDMult",)       # Block 3 的純量輸出（與 IF_Util 同為單格）；IF_TrainGen* 為世代索引，另見 TRAIN_GEN_NAMES
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


def drv_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """推導鏈：列＝中間量（依 DRV_CHAIN 順序），欄＝世代；只取所選層級的欄（欄名取 DRV_Gen、DRV_Tier）。
    物理量列讀 DRV_*；decode $/M 列讀 IF_CostDec_<層級>，取所選成本情境（依世代名稱對齊）。"""
    gens, tier_of = _by_col(eng, "DRV_Gen"), _by_col(eng, "DRV_Tier")
    keep = [c for c in gens if str(tier_of[c]).split("（")[0] == tier]
    rows = {}
    for key in DRV_CHAIN:
        if key == "CostDec":
            s = interface_series(eng, f"IF_CostDec_{tier}")
            by_gen = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
            label = f"{tier}｜{s['label']}（{s['unit']}）｜{case}"
            rows[label] = {gens[c]: fmt_unit(by_gen[gens[c]], s["unit"]) for c in keep}
            continue
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


# 驗證表欄位映射：顯示欄 → CAL_<節>_<名稱>（H 節沒有「軟體／日期」）
_CALIB_COLS = {
    "F": (("點位", "Label"), ("世代", "Gen"), ("軟體／日期", "Eng"), ("每用戶速度", "Speed"), ("實測", "Meas"),
          ("模型", "Model"), ("比值", "Ratio"), ("口徑", "Basis"), ("量測平台", "Platform")),
    "H": (("點位", "Label"), ("世代", "Gen"), ("每用戶速度", "Speed"), ("實測", "Meas"),
          ("模型", "Model"), ("比值", "Ratio"), ("口徑", "Basis"), ("量測平台", "Platform")),
}


def calib_validation(eng: Engine, sec: str) -> tuple[pd.DataFrame, dict]:
    """驗證表（sec＝'F'：模型 ÷ 實測／InferenceX；'H'：模型 ÷ MLPerf）。
    回傳 (表, 欄說明)；欄說明含各欄 Excel 列標籤與單位（表頭註明用）。每列都有「量測平台」與「口徑」。"""
    cols, meta = {}, {}
    for shown, key in _CALIB_COLS[sec]:
        s = series(eng, f"CAL_{sec}_{key}")
        cols[shown] = s["values"]
        meta[shown] = (s["label"], s["unit"])
    n = {len(v) for v in cols.values()}
    assert len(n) == 1, f"CAL_{sec}_* 長度不一致：{n}"
    return pd.DataFrame(cols), meta


def basis_note(df: pd.DataFrame) -> str:
    """該表口徑（取自 CAL_*_Basis 的不重複值）。"""
    return "、".join(dict.fromkeys(str(x) for x in df["口徑"]))


# ── Block 3（Training）─────────────────────────────────────────────

def is_block3_name(name: str) -> bool:
    """Block 3 的 Interface 名稱（IF_<指標>_<層級>）與純量 IF_RDMult、IF_TrainGen*。"""
    return name in BLOCK3_SCALARS or name in TRAIN_GEN_NAMES or any(name.startswith(f"IF_{m}_") for m in BLOCK3_METRICS)


def train_gens(eng: Engine) -> list[str]:
    """J13 的訓練世代名稱（預設、並列；依序）：讀 IF_TrainGenDefault／IF_TrainGenAlt 的世代索引，
    對應 IF_HdrGen 去重後的世代順序（與 Spec_Rack 世代列相同）。"""
    gens = list(dict.fromkeys(eng.get_name("IF_HdrGen")))
    return [gens[int(eng.get_name(n)) - 1] for n in TRAIN_GEN_NAMES]


def order_gens(gens: list[str], first: list[str] | None = None) -> list[str]:
    """世代顯示順序：J13 的預設、並列世代排最前，其餘維持 Excel 順序。"""
    gens = list(dict.fromkeys(gens))
    head = [g for g in (first or []) if g in gens]
    return head + [g for g in gens if g not in head]


def block3_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """Block 3 產出：列＝指標（Excel 標籤＋單位，前綴層級）；欄＝世代（J13 預設世代在前）；只取所選成本情境。
    值依列單位格式化為字串（% 列由小數轉百分比）。"""
    first, rows = train_gens(eng), {}
    for metric in BLOCK3_METRICS:
        s = interface_series(eng, f"IF_{metric}_{tier}")
        picked = {g: fmt_unit(v, s["unit"]) for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
        rows[f"{tier}｜{s['label']}（{s['unit']}）"] = {g: picked[g] for g in order_gens(list(picked), first)}
    return pd.DataFrame(rows).T


def post_share_table(eng: Engine, tier: str) -> pd.DataFrame:
    """後訓練占比兩種口徑與 RL 有效 MFU（數值；列＝指標，欄＝世代）。三者皆不隨成本情境改變，取第一個成本情境。"""
    first_case, first = cost_cases(eng)[0], train_gens(eng)
    rows = {}
    for metric in ("PostShareFLOP", "PostShareGPUh", "RLMFU"):
        s = interface_series(eng, f"IF_{metric}_{tier}")
        picked = {g: v * 100 for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == first_case}   # 小數 → %
        rows[f"{s['label']}（%）"] = {g: picked[g] for g in order_gens(list(picked), first)}
    return pd.DataFrame(rows).T


def trn_table(eng: Engine, tier: str) -> pd.DataFrame:
    """Block 3 推導鏈：列＝TRN_ 中間量（依其在 Training 頁的列序），欄＝世代（欄名取 TRN_Gen、TRN_Tier）；只取所選層級。"""
    gens, tier_of = _by_col(eng, "TRN_Gen"), _by_col(eng, "TRN_Tier")
    keep = [c for c in gens if str(tier_of[c]).split("（")[0] == tier]
    names = sorted((n for n in eng.names if n.startswith("TRN_") and n not in ("TRN_Gen", "TRN_Tier")),
                   key=lambda n: range_boundaries(eng.name_ref(n)[1])[1])
    rows = {}
    for n in names:
        s = series(eng, n)
        by = dict(zip(s["cols"], s["values"]))
        unit = f"（{s['unit']}）" if s["unit"] not in (None, "") else ""
        rows[f"{s['label']}{unit}"] = {gens[c]: fmt_unit(by[c], s["unit"]) for c in keep}
    df = pd.DataFrame(rows).T
    return df[order_gens(list(df.columns), train_gens(eng))]


def tier_titles_trn(eng: Engine) -> dict[str, str]:
    """層級 → 顯示標題；取自 TRN_Tier。"""
    out = {}
    for title in eng.get_name("TRN_Tier"):
        out.setdefault(str(title).split("（")[0], str(title))
    return out


def _named_table(eng: Engine, prefix: str, names: list[str] | None = None) -> pd.DataFrame:
    """把 prefix 開頭的單欄具名範圍組成表：欄依其在工作表的欄序；欄名＝範圍正上方一格的表頭文字（讀自 Excel）。"""
    names = names or [n for n in eng.names if n.startswith(prefix)]
    cols = {}
    for n in sorted(names, key=lambda n: range_boundaries(eng.name_ref(n)[1])[0]):
        sheet, ref = eng.name_ref(n)
        c1, r1, _, _ = range_boundaries(ref)
        header = str(eng.get(sheet, f"{get_column_letter(c1)}{r1 - 1}"))
        cols[header] = eng.get_name(n)
    return pd.DataFrame(cols)


def registry_tables(eng: Engine) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tech_Registry 唯讀表：(技術登錄表, 掛鉤彙總表)；分別讀 TR_（不含 TR_Hook*）與 TR_Hook* 具名範圍。不寫入、不提供開關。"""
    hooks = [n for n in eng.names if n.startswith("TR_Hook") and n != "TR_Hook"]   # TR_Hook＝技術的掛鉤代碼欄，屬登錄表
    reg = [n for n in eng.names if n.startswith("TR_") and n not in hooks]
    return _named_table(eng, "TR_", reg), _named_table(eng, "TR_Hook", hooks)

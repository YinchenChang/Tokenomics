"""網站共用：載入引擎，並只經由具名範圍取 Excel 的資料。

規則（CLAUDE.md 第 1、6 節）：不含任何數值、價格或參數；標籤、單位、世代與層級名稱全部來自 Excel。
- IF_（非 IF_Hdr）：Interface 輸出，下游模型連結用。
- IF_HdrGen／IF_HdrCost：Interface 表頭（世代、成本情境）——僅供顯示。
- DRV_：Perf 推導鏈——僅供顯示。
- CAL_：Calib 校準值與驗證表——僅供顯示。
- TRN_：Training 推導鏈（Block 3）——僅供顯示。
- B4_：Block 4 顯示或內部用——下游模型不得連結（v5.8）。
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
# J13（Andy 決定）：下游預設訓練世代與並列世代。IF_TrainGenDefault／IF_TrainGenAlt 是世代索引（對應 Spec_Rack 世代列順序），
# IF_TrainGenDefaultName／IF_TrainGenAltName 是對應的世代名稱（v5.7）。網站讀名稱，只用來把這兩個世代排在最前面。
TRAIN_GEN_NAMES = ("IF_TrainGenDefault", "IF_TrainGenAlt")
TRAIN_GEN_LABEL_NAMES = ("IF_TrainGenDefaultName", "IF_TrainGenAltName")   # v5.7：世代名稱（Interface 世代名稱格）
# 推導鏈顯示順序（由物理量到成本；DRV_Gen、DRV_Tier 為欄名）。
# "CostDec" 不讀 DRV_CostDec（只有基準成本），改讀 IF_CostDec_<層級>，跟隨成本情境選擇器。
DRV_CHAIN = ("FlopDec", "FlopPre", "WeightGB", "TfixMs", "SeqMs", "SeqBind", "Batch", "Bind",
             "DecTokGPU", "PreTokGPU", "PreShare", "RackTok", "GWTok", "CostDec", "Close")
BLOCK3_SCALARS = ("IF_RDMult",)       # Block 3 的純量輸出（與 IF_Util 同為單格）；IF_TrainGen* 為世代索引，另見 TRAIN_GEN_NAMES
_BLOCK2_NAME = re.compile(r"^IF_(?P<metric>%s)_(?P<tier>\w+)$" % "|".join(BLOCK2_METRICS))


def is_downstream_name(name: str) -> bool:
    """下游模型只可連結 IF_ 開頭且非 IF_Hdr 的名稱。"""
    return name.startswith("IF_") and not name.startswith("IF_Hdr")


@st.cache_resource(show_spinner="首次載入：以公式引擎建立並重算整份 Excel（約 1 分鐘）…")
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
    return name in BLOCK3_SCALARS or name in TRAIN_GEN_NAMES or name in TRAIN_GEN_LABEL_NAMES or any(name.startswith(f"IF_{m}_") for m in BLOCK3_METRICS)


def train_gens(eng: Engine) -> list[str]:
    """J13 的訓練世代名稱（預設、並列；依序）：直接讀 IF_TrainGenDefaultName／IF_TrainGenAltName。"""
    return [str(eng.get_name(n)) for n in TRAIN_GEN_LABEL_NAMES]


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


def evidence_table(eng: Engine) -> pd.DataFrame:
    """DB_Evidence（證據登錄表，純輸入、無公式）：唯讀。本頁沒有具名範圍，以工作表直接讀取：
    欄 A 表頭「ID」所在列為表頭，其下連續非空列為資料；A:K 以外的欄不讀。已列入報告（建議補 EV_ 具名範圍）。"""
    grid = eng.get("DB_Evidence", "A1:K500")
    start = next(i for i, r in enumerate(grid) if r[0] == "ID")
    header = [str(h) for h in grid[start]]
    rows = [r for r in grid[start + 1:] if any(x != "" for x in r)]
    return pd.DataFrame(rows, columns=header)


# ── Block 4（價格、理論營收、成本與攤提）──────────────────────────
# 欄位映射：Interface D 節（v5.8）。形狀兩種：單格（含文字）與 15 欄（5 世代 × 3 成本情境，與 IF_HdrGen 同寬）。
# B4_ 名稱屬顯示或內部用，下游模型不得連結；網站只讀不寫。
B4_PRICE_TYPES = (   # (Interface 名稱前綴, 欄位簡稱)；每一列都帶層級，欄＝token 類型（CLAUDE.md 1a）
    "PriceFresh", "PriceCached", "PriceThink", "PriceOut", "PriceRef", "FrontRef", "FrontModel")
B4_REV_TIER = ("RevGW", "RevGWFront")                 # 依層級：每 GW 理論營收（理想上限）
B4_REV_FLEET = ("IF_RevGWFleet", "IF_RevGWFleetFront")  # 機隊（付費服務、層級組合）
B4_COST_METRICS = ("CacheStore", "AmortBU", "AmortTD", "FullCost")
# 市場候選表：B4_Mkt* 欄序（依工作表欄序排列，欄名取範圍正上方一格的表頭文字）
B4_MKT_NAMES = ("B4_MktModel", "B4_MktVendor", "B4_MktCountry", "B4_MktOpen", "B4_MktIn", "B4_MktCache",
                "B4_MktOut", "B4_MktPeak", "B4_MktIndex")
CN_COUNTRY = "中國"   # 顯示標記用：國別欄等於此值的列標為中國廠商（Excel 沒有專屬旗標欄；已列入報告）


B4_IF_TIER_METRICS = B4_PRICE_TYPES + ("Life", "CacheStore", "AmortBU", "AmortTD", "FullCost") + B4_REV_TIER
B4_IF_SCALARS = B4_REV_FLEET + ("IF_ServeShare", "IF_FreeShare")


def is_block4_name(name: str) -> bool:
    """Block 4 的 Interface 名稱（Interface D 節）：IF_<指標>_<層級> 與機隊、占比純量。"""
    return name in B4_IF_SCALARS or any(name.startswith(f"IF_{m}_") for m in B4_IF_TIER_METRICS)


def scalar(eng: Engine, name: str) -> dict:
    """單格具名範圍（數值或文字）→ {label, unit, value}；標籤與單位取該列欄 A、欄 B。"""
    sheet, ref = eng.name_ref(name)
    _, r1, _, _ = range_boundaries(ref)
    return {"label": _label(str(eng.get(sheet, f"A{r1}"))), "unit": eng.get(sheet, f"B{r1}"), "value": eng.get_name(name)}


def pick(s: dict, gen: str, case: str):
    """15 欄序列中，取指定世代與成本情境的值。"""
    for g, c, v in zip(s["gens"], s["cases"], s["values"]):
        if g == gen and c == case:
            return v
    raise KeyError((gen, case))


def generations(eng: Engine) -> list[str]:
    return list(dict.fromkeys(eng.get_name("IF_HdrGen")))


def price_table(eng: Engine, tier_map: dict[str, str]) -> pd.DataFrame:
    """單價表：列＝層級；欄＝token 類型（新鮮輸入、快取輸入、思考、可見輸出、參考請求混合、前緣混合、前緣模型）。
    欄名取 Excel 標籤（去掉層級以外的共同尾綴）與單位；單價不隨世代與成本情境改變（K9：一份價格快照）。"""
    cols: dict[str, dict] = {}
    for key in B4_PRICE_TYPES:
        for tier, title in tier_map.items():
            s = scalar(eng, f"IF_{key}_{tier}")
            head = s["label"] if s["unit"] in (None, "") or str(s["unit"]) in s["label"] else f"{s['label']}（{s['unit']}）"
            cols.setdefault(head, {})[title] = fmt(s["value"]) if not isinstance(s["value"], str) else s["value"]
    return pd.DataFrame(cols)


def market_table(eng: Engine) -> pd.DataFrame:
    """市場候選表（Cap_In F 節）：來源 B4_Mkt*；中國廠商以標記欄區分；空值顯示為「（空白）」。"""
    df = _named_table(eng, "B4_Mkt", list(B4_MKT_NAMES))
    df = df.map(lambda v: "（空白）" if v == "" else fmt(v))   # 全部轉字串（欄內數值與「（空白）」並存）
    df.insert(0, "標記", ["中國廠商" if c == CN_COUNTRY else "" for c in eng.get_name("B4_MktCountry")])
    return df


def rev_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """理論營收（理想上限）：列＝IF_RevGW_<層級>、IF_RevGWFront_<層級>、機隊兩列；欄＝世代；只取所選成本情境。
    機隊列是 Luna／Sol／Astra 依付費 token 組合（B4_MixPaid）加權的 1 GW 參考機隊，不是單一層級。"""
    rows = {}
    for key in B4_REV_TIER:
        s = interface_series(eng, f"IF_{key}_{tier}")
        rows[f"{tier}｜{s['label']}（{s['unit']}）"] = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
    for n in B4_REV_FLEET:
        s = interface_series(eng, n)
        rows[f"機隊（層級組合）｜{s['label']}（{s['unit']}）"] = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
    return pd.DataFrame(rows).T


def cost_table(eng: Engine, tier: str, case: str) -> pd.DataFrame:
    """成本與攤提：列＝快取儲存、攤提（自下而上、由上而下）、全成本；欄＝世代；每列前綴層級；只取所選成本情境。"""
    rows = {}
    for key in B4_COST_METRICS:
        s = interface_series(eng, f"IF_{key}_{tier}")
        rows[f"{tier}｜{s['label']}（{s['unit']}）"] = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
    return pd.DataFrame(rows).T


def b4_chain(eng: Engine, tier: str, gen: str, case: str) -> pd.DataFrame:
    """推導鏈（單一層級、世代、成本情境）：每 GW 產出 → 利用率 → 有效單價 → 理論營收 → 服務成本 → 快取儲存 → 攤提 → 全成本。
    全部讀既有 IF_ 具名範圍（不新增計算）；每列標明層級與 token 類型。"""
    steps: list[tuple[str, str, str, str, object]] = []

    def add_series(step, name, tokens):
        s = interface_series(eng, name)
        steps.append((step, tokens, s["label"], s["unit"], pick(s, gen, case)))

    def add_scalar(step, name, tokens):
        s = scalar(eng, name)
        steps.append((step, tokens, s["label"], s["unit"], s["value"]))

    add_series("1 每 GW 產出", f"IF_TokGW_{tier}", "總 token（100%）")
    add_scalar("2 利用率", "IF_Util", "（不分 token 類型）")
    for key, tokens in (("PriceFresh", "新鮮輸入"), ("PriceCached", "快取輸入"), ("PriceThink", "思考"), ("PriceOut", "可見輸出"),
                        ("PriceRef", "參考請求混合"), ("FrontRef", "參考請求混合（前緣）")):
        add_scalar("3 有效單價", f"IF_{key}_{tier}", tokens)
    add_series("4 理論營收（理想上限）", f"IF_RevGW_{tier}", "參考請求混合（OpenAI 有效）")
    add_series("4 理論營收（理想上限）", f"IF_RevGWFront_{tier}", "參考請求混合（前緣）")
    add_series("5 服務成本", f"IF_CostPre_{tier}", "新鮮輸入（prefill）")
    add_series("5 服務成本", f"IF_CostCache_{tier}", "快取輸入（prefill）")
    add_series("5 服務成本", f"IF_CostDec_{tier}", "思考＋可見輸出（decode）")
    add_series("6 快取儲存", f"IF_CacheStore_{tier}", "快取輸入")
    add_scalar("7 攤提", f"IF_Life_{tier}", "（商業壽命）")
    add_series("7 攤提", f"IF_AmortBU_{tier}", "參考請求混合（自下而上）")
    add_series("7 攤提", f"IF_AmortTD_{tier}", "參考請求混合（由上而下）")
    add_series("8 全成本", f"IF_FullCost_{tier}", "參考請求混合（自下而上攤提）")
    return pd.DataFrame([(a, tier, b, c, d, e) for a, b, c, d, e in steps],
                        columns=["步驟", "層級", "token 類型", "項目（Excel 標籤）", "單位", "值"])

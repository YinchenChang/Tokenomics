"""名稱查詢 — 用關鍵字找任一具名範圍或 L1 列，看值、位置、標籤與讀法。

Excel 已超過 8 萬格，整本閱讀不實際；本頁讓人用「名稱或中文標籤的片段」直接查到數字與它在 Excel 的位置。
唯讀：只列出 LibreOffice 重算後存下的值。
"""
import pandas as pd
import streamlit as st

from app.common import fmt, get_engine, l1_rows, name_label


@st.cache_data(show_spinner="建立名稱索引…")
def _index(_eng, path_key: str) -> pd.DataFrame:
    rows = []
    for n, attr in _eng.names.items():
        try:
            label, unit = name_label(_eng, n)
            v = _eng.get_name(n)
        except Exception:      # 名稱指向不存在的格等：只列位置
            label, unit, v = "", "", ""
        vals = v if isinstance(v, list) else [v]
        flat = [x for row in vals for x in (row if isinstance(row, list) else [row])]
        shown = "、".join(fmt(x) for x in flat[:16]) + ("…" if len(flat) > 16 else "")
        rows.append({"名稱": n, "值": shown, "單位": unit, "標籤": label, "位置": attr.replace("$", ""), "格數": len(flat)})
    return pd.DataFrame(rows).sort_values("名稱").reset_index(drop=True)


def render():
    eng = get_engine()
    st.title("名稱查詢")
    st.caption(f"事實來源：`{eng.path.name}`。輸入名稱或中文標籤的片段（例：`L1_M`、`持有成本`、`利用率`、`VR200`）；"
               "多個關鍵字以空白分隔，須全部符合。")
    idx = _index(eng, str(eng.path))
    q = st.text_input("關鍵字", key="lookup_q")
    prefixes = sorted({n.split("_")[0] for n in idx["名稱"]})
    pick = st.multiselect("只看這些前綴（空白＝全部）", prefixes, key="lookup_prefix")
    df = idx
    if pick:
        df = df[df["名稱"].str.split("_").str[0].isin(pick)]
    for word in q.split():
        hay = df["名稱"].str.contains(word, case=False, regex=False) | df["標籤"].astype(str).str.contains(word, case=False, regex=False)
        df = df[hay]
    st.write(f"符合 {len(df):,} 筆（全部 {len(idx):,} 個具名範圍）")
    st.dataframe(df, width="stretch", hide_index=True, height=min(38 + 35 * len(df), 600))

    st.divider()
    st.subheader("L1 全表（第 1 層常用推算值）")
    l1 = l1_rows(eng, str(eng.path))
    if q:
        mask = pd.Series(False, index=l1.index)
        for c in l1.columns:
            mask |= l1[c].astype(str).str.contains(q.split()[0], case=False, regex=False)
        l1 = l1[mask]
    st.dataframe(l1.astype(str), width="stretch", hide_index=True, height=min(38 + 35 * len(l1), 600))
    st.caption("L1 每列：基準值／低／高、單位、區間的定義、讀法、主要驅動、最弱輸入的標記，全部取自 Excel L1 頁。")

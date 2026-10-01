"""總覽：目前載入的活頁簿、控制輸入與 Interface Block 1（機架／資本支出／持有成本）。"""
import pandas as pd
import streamlit as st
from openpyxl.utils import range_boundaries

from app.common import (BLOCK2_METRICS, BLOCK3_SCALARS, fmt, fmt_unit, get_engine, interface_series, is_block3_name,
                        is_downstream_name)


def render():
    eng = get_engine()
    st.title("Tokenomics — 總覽")
    st.caption(f"事實來源：`{eng.path.name}`。本網站只呈現 Excel 由公式引擎重算的結果，不含任何自有計算或參數。")

    ctl = [n for n in eng.names if n.startswith("CTL_")]
    scalars = ("IF_Util",) + BLOCK3_SCALARS                      # 第 0 層純量：基準利用率、研發倍數
    cols = st.columns(len(ctl) + len(scalars))
    for c, n in zip(cols, ctl):
        c.metric(n, fmt(eng.get_name(n)))
    for c, n in zip(cols[len(ctl):], scalars):
        s = interface_series(eng, n)
        c.metric(n, fmt_unit(s["values"][0], s["unit"]))

    st.subheader("Interface — Block 1（每 GW＝IT 關鍵電力）")
    block1 = [n for n in eng.names if is_downstream_name(n) and n != "IF_Util" and not is_block3_name(n)
              and not any(n.startswith(f"IF_{m}_") for m in BLOCK2_METRICS)]
    rows = {}
    for n in sorted(block1, key=lambda n: range_boundaries(eng.name_ref(n)[1])[1]):   # 依 Excel 列序
        s = interface_series(eng, n)
        rows[f"{s['label']}（{s['unit']}）"] = s["values"]
    idx = pd.MultiIndex.from_arrays([s["gens"], s["cases"]], names=["世代", "成本情境"])
    df = pd.DataFrame(rows, index=idx).T
    st.dataframe(df.map(fmt), use_container_width=True)
    st.caption("列標籤、單位、世代與成本情境皆取自 Excel Interface 頁；Block 2、Block 3 見左側頁面。")

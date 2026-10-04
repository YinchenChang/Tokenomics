"""治理（v5.11；v5.13 起 SRC 八頁）：Checks G 節、第 1 層 L1、第 0 層 Source（唯讀）。資料只來自 Excel 的 GOV_／L1_／SRC_ 具名範圍與其所在工作表。"""
import streamlit as st

from app.common import get_engine, gov_status, gov_table, l1_table, src_tables


def render():
    eng = get_engine()
    st.title("治理 — Source（第 0 層）、L1（第 1 層）、Checks G 節")
    st.caption("本頁唯讀，只呈現 Excel 的內容；新增或修改請在 Excel（Project 端）進行並升版。")

    s = gov_status(eng)
    c = st.columns(3)
    for col, (n, v) in zip(c, s.items()):
        col.metric(n, v)
    st.subheader("Checks G 節")
    st.table(gov_table(eng).astype(str))

    st.subheader("L1 — 第 1 層常用推算值")
    df = l1_table(eng)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"共 {len(df)} 列；基準值、低、高皆為 Excel 即時公式。")

    st.subheader("Source — 第 0 層（SRC_*，A–W 欄）")
    tables = src_tables(eng)
    sheet = st.radio("工作表", list(tables), horizontal=True, key="src_sheet")
    t = tables[sheet]
    states = st.multiselect("狀態", sorted({str(x) for x in t["狀態"]}), key="src_state")
    show = t[t["狀態"].isin(states)] if states else t
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.caption(f"{sheet}：共 {len(t)} 筆；目前顯示 {len(show)} 筆。")

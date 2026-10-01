"""證據登錄（DB_Evidence，唯讀）：每筆新資訊與 Tokenomics 現值的比對與判定。資料只來自 Excel 的 DB_Evidence 工作表。"""
import streamlit as st

from app.common import evidence_table, get_engine


def render():
    eng = get_engine()
    st.title("證據登錄（DB_Evidence，唯讀）")
    st.caption("每一筆新資訊先與 Tokenomics 現值比對，再判定採納與否；本頁只呈現 Excel 的內容，不提供編輯。"
               "新增或修改證據請在 Excel（Project 端）進行並升版。")
    df = evidence_table(eng)
    c1, c2 = st.columns(2)
    verdicts = c1.multiselect("判定", sorted({str(x) for x in df["判定"]}), key="ev_verdict")
    tags = c2.multiselect("標記", sorted({str(x) for x in df["標記"]}), key="ev_tag")
    show = df
    if verdicts:
        show = show[show["判定"].isin(verdicts)]
    if tags:
        show = show[show["標記"].isin(tags)]
    st.dataframe(show, use_container_width=True, hide_index=True, height=38 + 35 * len(show))
    st.caption(f"共 {len(df)} 筆；目前顯示 {len(show)} 筆。")

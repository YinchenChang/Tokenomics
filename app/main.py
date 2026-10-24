"""Tokenomics 網站入口：streamlit run app/main.py（或 streamlit run tokenomics.py）。唯讀呈現現行活頁簿（CLAUDE.md 修訂十一）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.views import alloc, block2, block3, block4, block5, evidence, governance, lookup, overview, payback, qa  # noqa: E402

st.set_page_config(page_title="Tokenomics", layout="wide")
nav = st.navigation([
    st.Page(payback.render, title="回本判讀（m、L、P×Q）", default=True),
    st.Page(lookup.render, title="名稱查詢", url_path="lookup"),
    st.Page(overview.render, title="總覽（Interface Block 1）", url_path="overview"),
    st.Page(block2.render, title="Block 2", url_path="block2"),
    st.Page(block3.render, title="Block 3", url_path="block3"),
    st.Page(block4.render, title="Block 4", url_path="block4"),
    st.Page(block5.render, title="Block 5", url_path="block5"),
    st.Page(alloc.render, title="Alloc", url_path="alloc"),
    st.Page(qa.render, title="問答", url_path="qa"),
    st.Page(evidence.render, title="證據登錄", url_path="evidence"),
    st.Page(governance.render, title="治理（Source／L1）", url_path="governance"),
])
nav.run()

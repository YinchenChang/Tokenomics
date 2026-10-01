"""Tokenomics 網站入口：streamlit run app/main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.views import block2, block3, block4, evidence, overview  # noqa: E402

st.set_page_config(page_title="Tokenomics", layout="wide")
nav = st.navigation([
    st.Page(overview.render, title="總覽", url_path="overview", default=True),
    st.Page(block2.render, title="Block 2", url_path="block2"),
    st.Page(block3.render, title="Block 3", url_path="block3"),
    st.Page(block4.render, title="Block 4", url_path="block4"),
    st.Page(evidence.render, title="證據登錄", url_path="evidence"),
])
nav.run()

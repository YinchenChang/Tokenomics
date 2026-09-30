"""Tokenomics 網站入口：streamlit run app/main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.views import block2, overview  # noqa: E402

st.set_page_config(page_title="Tokenomics", layout="wide")
nav = st.navigation([
    st.Page(overview.render, title="總覽", url_path="overview", default=True),
    st.Page(block2.render, title="Block 2", url_path="block2"),
])
nav.run()

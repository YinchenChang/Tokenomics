"""Tokenomics 網站入口：streamlit run app/main.py（或 streamlit run tokenomics.py）。唯讀呈現現行活頁簿（CLAUDE.md 修訂十一）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from app.nav import PAGES  # noqa: E402
from app.views import alloc, block2, block3, block4, block5, evidence, governance, lookup, overview, payback, qa  # noqa: E402

st.set_page_config(page_title="Tokenomics", layout="wide")
_VIEWS = {"payback": payback, "lookup": lookup, "overview": overview, "block2": block2, "block3": block3, "block4": block4,
          "block5": block5, "alloc": alloc, "qa": qa, "evidence": evidence, "governance": governance}
# 頁名取自 app/nav.py（與靜態網站 site/build_site.py 共用，兩邊一致）；第一頁為預設頁
nav = st.navigation([
    st.Page(_VIEWS[key].render, title=title, url_path=path, default=(i == 0))
    for i, (key, title, path) in enumerate(PAGES)
])
nav.run()

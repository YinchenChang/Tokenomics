"""網站入口（Streamlit Community Cloud 以本檔為主程式）：執行 app/main.py。
本機：streamlit run tokenomics.py（或雙擊 run_local.bat）。網站唯讀呈現現行活頁簿（CLAUDE.md 修訂十一）。"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "app" / "main.py"), run_name="__main__")

@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo 第一次執行：建立 Python 環境並安裝套件（約 1-2 分鐘）...
  python -m venv .venv || (echo 找不到 Python，請先安裝 Python 3.11 以上 & pause & exit /b 1)
  ".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
)
".venv\Scripts\python.exe" -m streamlit run tokenomics.py
pause

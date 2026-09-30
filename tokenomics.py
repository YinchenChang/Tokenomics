"""相容入口：舊版（v4 手抄公式）已停用，改由 app/main.py 呈現 Excel（見 legacy/）。"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "app" / "main.py"), run_name="__main__")

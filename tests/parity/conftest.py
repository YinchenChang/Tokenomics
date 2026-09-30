import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo 根目錄
sys.path.insert(0, str(Path(__file__).resolve().parent))

RESULTS = Path(__file__).parent / "_results.json"   # 由 .gitignore 排除；供每輪報告取數


@pytest.fixture(scope="session")
def results_store():
    data = json.loads(RESULTS.read_text()) if RESULTS.exists() else {}
    yield data
    RESULTS.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str))

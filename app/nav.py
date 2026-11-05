"""網站頁面清單（Streamlit app/main.py 與靜態網站 site/build_site.py 共用，兩邊頁名一致）。

不 import streamlit：靜態網站建置程式也讀這份清單。
每列：(模組名, 左側導覽頁名, url_path／靜態檔名主幹)。順序＝左側導覽順序；第一列為預設頁。
Block 2–5、Alloc 的頁名由 Andy 2026-11-05 核定；其餘頁名同一風格（中文、自明）。
"""

PAGES = (
    ("payback", "回本判讀：m、L 與每 GW 營收", "payback"),
    ("lookup", "名稱查詢：具名範圍與 L1 全表", "lookup"),
    ("overview", "總覽", "overview"),
    ("block2", "推論：每 GW 產能與單位成本", "block2"),
    ("block3", "訓練：算力與成本", "block3"),
    ("block4", "價格、營收與攤提", "block4"),
    ("block5", "任務成功率與每任務成本", "block5"),
    ("alloc", "算力分配：服務／訓練／研發", "alloc"),
    ("qa", "九題問答：答案、區間與缺口", "qa"),
    ("evidence", "證據登錄：新資訊比對與判定", "evidence"),
    ("governance", "治理：來源、L1 與檢查", "governance"),
)

TITLES = {key: title for key, title, _ in PAGES}

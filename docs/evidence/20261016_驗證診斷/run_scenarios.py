"""V1／V2／V7／V8 條件對齊情境（唯讀診斷；只在 scratch 複本上改格，不動 repo 的 model/）。

用法：python3 run_scenarios.py <現行 xlsx> <scratch 目錄> <輸出 json>

每個情境：複製活頁簿 → 覆寫指定格（含公式格，僅 scratch）→ LibreOffice headless 重算 → 讀出下列量。
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl

SRC = Path(sys.argv[1])
WORK = Path(sys.argv[2])
OUT = Path(sys.argv[3])
WORK.mkdir(parents=True, exist_ok=True)

# Perf：D 欄＝Hopper×Sol，G 欄＝GB200×Sol；Calib：G 欄＝Hopper server（v5.1），H 欄＝GB200 server（v5.1）
PERF_ROWS = [28, 41, 43, 44, 45, 49, 53, 55, 65, 71, 72, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90]
CALIB_ROWS = [118, 125, 126, 133, 134, 135, 136, 140, 144, 145, 146, 147, 148, 149]
CHECK_CELLS = ["E148", "E149", "E154", "E155", "F146"]

LMSYS_CAL = {"Calib!C110": 2000, "Calib!C111": 2000}  # 輸入 2,000；輸出長度來源未寫，取 2,000（decode 上下文 3,000）

SCEN = {
    "S0_基準": {},
    # ---- Perf 路線（Sol 架構，V7／V8 實際讀的格） ----
    "P1_SLO10": {"Serving!D21": 10},
    "P2_SLO10_ISL2000": {"Serving!D21": 10, "Serving!D23": 2000},
    "P3_SLO10_ISL2000_無MTP": {"Serving!D21": 10, "Serving!D23": 2000, "Serving!C6": 0},
    "P4_P3_規模37B": {"Serving!D21": 10, "Serving!D23": 2000, "Serving!C6": 0,
                     "Arch!D7": 37, "Arch!D6": 671},
    "P5_P4_無SLO上限": {"Serving!D21": 0.5, "Serving!D23": 2000, "Serving!C6": 0,
                      "Arch!D7": 37, "Arch!D6": 671},
    # 注意：P3–P5 改的是全域 Serving!C6 與 Arch!D6／D7，Calib 擬合點也讀這兩格，所以 η_d 與每層延遲會被重新擬合；
    # 這三個情境只用來說明「MTP 假設與 η_d 擬合連動」。乾淨的對齊用下列 Q 情境：只改被比較的 Perf 欄，校準不動。
    "Q3_SLO10_ISL2000_該欄無MTP": {"Serving!D21": 10, "Serving!D23": 2000, "Perf!D47": 0, "Perf!G47": 0},
    "Q4_Q3_V3規模": {"Serving!D21": 10, "Serving!D23": 2000, "Perf!D47": 0, "Perf!G47": 0,
                    "Perf!D28": 37, "Perf!G28": 37, "Perf!D32": 13.99, "Perf!G32": 13.99,
                    "Perf!D33": 657, "Perf!G33": 657, "Perf!D31": 8, "Perf!G31": 8},
    "Q5_Q4_無SLO上限": {"Serving!D21": 0.5, "Serving!D23": 2000, "Perf!D47": 0, "Perf!G47": 0,
                      "Perf!D28": 37, "Perf!G28": 37, "Perf!D32": 13.99, "Perf!G32": 13.99,
                      "Perf!D33": 657, "Perf!G33": 657, "Perf!D31": 8, "Perf!G31": 8},
    # ---- Calib 路線（DeepSeek-V3／R1 架構 671B／37B，MLA；讀 decode-only 第 147 列） ----
    "C1_V3架構_ITL100": dict(LMSYS_CAL, **{"Calib!G118": 10, "Calib!H118": 10}),
    "C2_V3架構_ITL200": dict(LMSYS_CAL, **{"Calib!G118": 5, "Calib!H118": 5}),
    "C3_V3架構_無SLO上限": dict(LMSYS_CAL, **{"Calib!G118": 0.5, "Calib!H118": 0.5}),
    # ---- V1：MLPerf v5.1 Hopper 實為 DGX H200（8 GPU） ----
    "A1_H200規格": {"Calib!G125": 141, "Calib!G126": 4.8},
    "A2_H200規格_8GPU": {"Calib!G125": 141, "Calib!G126": 4.8, "Calib!G133": 8},
}


def lo_recalc(xlsx: Path, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="lo_profile_"))
    try:
        subprocess.run(["soffice", f"-env:UserInstallation=file://{profile}", "--headless", "--calc",
                        "--convert-to", "xlsx", "--outdir", str(outdir), str(xlsx)],
                       capture_output=True, text=True, timeout=600)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    return outdir / xlsx.name


results = {}
only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
for name, edits in SCEN.items():
    if only and name not in only:
        continue
    wb = openpyxl.load_workbook(SRC)
    for key, v in edits.items():
        sh, coord = key.split("!")
        wb[sh][coord].value = v
    tmp = WORK / f"{name}.xlsx"
    wb.save(tmp)
    rec = lo_recalc(tmp, WORK / "recalc")
    wv = openpyxl.load_workbook(rec, data_only=True)
    r = {"edits": edits, "Perf": {}, "Calib": {}, "Checks": {}}
    for row in PERF_ROWS:
        r["Perf"][row] = {c: wv["Perf"][f"{c}{row}"].value for c in ("D", "G")}
    for row in CALIB_ROWS:
        r["Calib"][row] = {c: wv["Calib"][f"{c}{row}"].value for c in ("G", "H")}
    for cell in CHECK_CELLS:
        r["Checks"][cell] = wv["Checks"][cell].value
    results[name] = r
    print(name, "Perf88", r["Perf"][88], "Calib147", r["Calib"][147], "Calib148", r["Calib"][148], flush=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str))

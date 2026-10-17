"""4-3 B 段 Q1：說明文字中指向被刪除列的參照（只讀 v13.1）。
找法：任何文字或公式字串中出現「<頁名> 第 N 列」（含「第 N–M 列」「第 N、M 列」）且 (頁, N) 在刪除清單內者；
同時找「<頁名>!<欄><N>」直接參照（這類在 01_delete_deps.py 已由公式讀取檢查涵蓋，此處只列文字內的）。
輸出：待修正的文字格（頁、格、片段）。Decisions／DB_Evidence／Gov_Map／SRC_* 等紀錄頁的歷史敘述不改（紀錄性文字，保留原貌）。"""
import re
import sys
from pathlib import Path

import openpyxl

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("deps01", Path(__file__).parent / "01_delete_deps.py")
d01 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d01)

RECORD_PAGES = {"Decisions", "DB_Evidence", "Gov_Map", "Sources_Legacy", "README", "Load_Bearing", "SRC_Index"}
PAT = re.compile(r"(Arch|Serving|Workload|Unit_Cost|Training|Cap_In|Price_Frontier|Cache_Store|Theory_Rev|Harness|Har_In)\s*第\s*([0-9０-９、–\-，, ]+?)\s*列")


def expand(spec):
    out = set()
    for part in re.split(r"[、，,]", spec):
        part = part.strip()
        m = re.fullmatch(r"(\d+)\s*[–\-]\s*(\d+)", part)
        if m:
            out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        elif part.isdigit():
            out.add(int(part))
    return out


def main(model):
    dele = {(s, r) for s, r, _, _ in d01.delete_rows()}
    wb = openpyxl.load_workbook(model)
    hits = []
    for ws in wb.worksheets:
        if ws.title in RECORD_PAGES or ws.title.startswith("SRC_"):
            continue
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not isinstance(v, str):
                    continue
                for m in PAT.finditer(v):
                    rows = expand(m.group(2))
                    gone = sorted(r for r in rows if (m.group(1), r) in dele)
                    if gone and not (ws.title == m.group(1) and c.row in gone):
                        hits.append((ws.title, c.coordinate, m.group(1), gone, v[max(0, m.start() - 20): m.end() + 20].replace("\n", " ")))
    # 同頁內不帶頁名的「第 N 列」
    pat2 = re.compile(r"(?<![A-Za-z_])第\s*([0-9、–\-，, ]+?)\s*列")
    for ws in wb.worksheets:
        if ws.title in RECORD_PAGES or ws.title.startswith("SRC_"):
            continue
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not isinstance(v, str):
                    continue
                for m in pat2.finditer(v):
                    pre = v[max(0, m.start() - 14): m.start()]
                    if re.search(r"(Arch|Serving|Workload|Unit_Cost|Training|Cap_In|Price_Frontier|Cache_Store|Theory_Rev|Harness|Har_In|Perf|Alloc|Fleet_1GW|Amortize|Calib|Interface|Checks|L1|DC_Cost|Train_In)\s*$", pre):
                        continue          # 已帶頁名者由上面處理
                    gone = sorted(r for r in expand(m.group(1)) if (ws.title, r) in dele)
                    if gone and c.row not in gone:
                        hits.append((ws.title, c.coordinate, "(同頁)", gone, v[max(0, m.start() - 20): m.end() + 20].replace("\n", " ")))
    for h in hits:
        print(h)
    print("指向被刪列的文字", len(hits))


if __name__ == "__main__":
    main(sys.argv[1])

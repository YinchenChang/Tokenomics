#!/usr/bin/env python3
"""由 builder/*.py 重新產生 docs/builder/Tokenomics_builder_v5.md（CLAUDE.md 第 4a 節第 4 點；標題與各檔區塊格式不變）。
用法：python3 tools/gen_builder_md.py [--note "<本版變動說明>"] [--title "<新標題>"]
只重排檔案內容，不改內容；檔案順序依現有 md，新檔插入指定位置。"""
import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MD = REPO / "docs" / "builder" / "Tokenomics_builder_v5.md"
AFTER = {"block6.py": "block5.py", "gov_seed3.py": "gov_seed2.py", "gov_seed4.py": "gov_seed3.py", "v518.py": "gov_seed4.py", "v519.py": "v518.py", "v520.py": "v519.py", "v521.py": "v520.py", "v522.py": "v521.py", "v523.py": "v522.py", "v524.py": "v523.py", "v525.py": "v524.py", "v526.py": "v525.py", "v527.py": "v526.py", "v529.py": "v527.py", "deps.py": "v529.py", "v530.py": "deps.py"}      # 新檔放在哪個檔之後


def parse(text):
    parts = re.split(r"^## (\S+\.py)\n\n```python\n", text, flags=re.M)
    head, blocks = parts[0], {}
    order = []
    for name, body in zip(parts[1::2], parts[2::2]):
        code = body[: body.rindex("\n```")]
        blocks[name] = code; order.append(name)
    return head, order, blocks


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--note", default=""); ap.add_argument("--title", default="")
    a = ap.parse_args()
    head, order, _ = parse(MD.read_text(encoding="utf-8"))
    for new, after in AFTER.items():
        if new not in order and (REPO / "builder" / new).exists(): order.insert(order.index(after) + 1, new)
    if a.title:
        head = re.sub(r"\A# .*\n", a.title + "\n", head, count=1)
    if a.note and a.note not in head:
        lines = head.split("\n"); i = max(k for k, l in enumerate(lines) if l.startswith("- v5."))
        lines.insert(i + 1, a.note); head = "\n".join(lines)
    out = [head.rstrip("\n") + "\n"]
    for n in order:
        out.append(f"## {n}\n\n```python\n{(REPO / 'builder' / n).read_text(encoding='utf-8').rstrip(chr(10))}\n```\n")
    MD.write_text("\n".join(out), encoding="utf-8")
    print("written", MD, len(order), "files")


if __name__ == "__main__":
    main()

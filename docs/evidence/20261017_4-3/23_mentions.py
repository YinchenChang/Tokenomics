"""各 B 級列在 docs/（報告、工作單、契約、計畫）與 Interface／L1／Checks 等文字格中被提到的次數與檔名。
比對：『<工作表> ... 第 N 列／第 N–M 列／第 N、M 列』與『<工作表>!<欄>N』。用法：python3 23_mentions.py <rows.pkl> <out.pkl>（工作目錄＝repo 根）"""
import sys, re, pickle, collections
from pathlib import Path
rows = pickle.load(open(sys.argv[1], "rb"))
sheets = sorted({x["sheet"] for x in rows}, key=len, reverse=True)
files = [p for p in Path("docs").rglob("*") if p.suffix in (".md", ".txt") and "evidence" not in p.parts[:2]]
files += [p for p in Path("docs/evidence").rglob("*.md")]
files = [p for p in files if "20261017_4-3" not in str(p)]
idx = collections.defaultdict(set)     # (sheet,row) -> {檔名}
numre = re.compile(r"第\s*([0-9０-９]+)(?:\s*[–\-～~]\s*([0-9]+))?")
for p in files:
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for s in sheets:
        for m in re.finditer(re.escape(s), t):
            seg = t[m.end(): m.end() + 60]
            seg = re.split(r"[；;。\n]", seg)[0]
            # 『Sheet!C13』
            m2 = re.match(r"!\$?[A-Z]{1,2}\$?(\d+)(?::\$?[A-Z]{1,2}\$?(\d+))?", seg)
            if m2:
                a = int(m2.group(1)); b = int(m2.group(2) or a)
                for r in range(a, min(b, a + 200) + 1): idx[(s, r)].add(p.name)
                continue
            # 『Sheet ... 第 N 列』，容許『第 N、M 列』『第 N–M 列』
            m3 = re.match(r"[^第]{0,10}第\s*([0-9、,，\s–\-～~及和與]+?)\s*列", seg)
            if m3:
                body = m3.group(1)
                for part in re.split(r"[、,，\s及和與]+", body):
                    if not part: continue
                    mm = re.fullmatch(r"(\d+)[–\-～~](\d+)", part)
                    if mm:
                        a, b = int(mm.group(1)), int(mm.group(2))
                        for r in range(a, min(b, a + 200) + 1): idx[(s, r)].add(p.name)
                    elif part.isdigit():
                        idx[(s, int(part))].add(p.name)
out = {}
for x in rows:
    k = (x["sheet"], x["row"])
    out[k] = sorted(idx.get(k, []))
pickle.dump(out, open(sys.argv[2], "wb"))
hit = [(k, v) for k, v in out.items() if v]
print("files", len(files), "rows with mentions", len(hit), "of", len(out))
for k, v in sorted(hit, key=lambda kv: (kv[0][0], kv[0][1])):
    print(k, len(v), v[:4])

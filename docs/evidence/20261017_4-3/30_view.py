"""輔助：列出某頁某範圍的列，標示每列狀態（B＝B 級死格、M＝死格但已標用途、C＝核心／可達、空＝無公式），並列出直接使用此列的具名範圍。
用法：python3 30_view.py <工作表> <起列> <迄列>   （工作目錄＝repo 根）"""
import sys, pickle, re
from pathlib import Path
SC = Path("/tmp/claude-0/-home-claude/37be10be-3d01-559e-b6b2-0e13e0d5ba5b/scratchpad")
import openpyxl
specs = [a.split(":") for a in sys.argv[1:]]  # 工作表:起:迄
P = pickle.load(open(SC / "dead.pkl", "rb"))
model = Path("model") / P["model"]
wbf = openpyxl.load_workbook(model)
wbv = openpyxl.load_workbook(model, data_only=True)
B = set(P["unmarked"]); M = set(P["marked"]); Dd = set(P["dead"])
names = {n: dn.attr_text for n, dn in wbf.defined_names.items()}
rowname = {}
for n, t in names.items():
    for part in t.lstrip("=").split(","):
        if "!" not in part: continue
        s, rg = part.rsplit("!", 1)
        s = s.strip("'"); rg = rg.replace("$", "")
        m = re.fullmatch(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?", rg)
        if not m: continue
        a, b = int(m.group(2)), int(m.group(4) or m.group(2))
        for r in range(a, b + 1): rowname.setdefault((s, r), []).append(n)
for sh, r1, r2 in specs:
  r1, r2 = int(r1), int(r2)
  print("=====", sh, r1, r2)
  ws, wv = wbf[sh], wbv[sh]
  for r in range(r1, r2 + 1):
      cs = [c for c in ws[r] if c.value is not None]
      if not cs: continue
      st = ""
      for c in cs:
          k = (sh, c.coordinate)
          if k in B: st = "B"; break
      if not st:
          for c in cs:
              if (sh, c.coordinate) in M: st = "M"; break
      if not st and any(isinstance(c.value, str) and c.value.startswith("=") for c in cs): st = "C"
      lab = ""
      for col in ("A", "B"):
          x = wv[f"{col}{r}"].value
          if isinstance(x, str) and x.strip(): lab = x.strip(); break
      f = next((c for c in cs if c.column >= 3), None)
      fv = str(f.value)[:90] if f else ""
      vv = wv[f.coordinate].value if f else ""
      nm = ",".join(rowname.get((sh, r), []))[:60]
      print(f"{r:>4} {st or '-'} {lab[:50]} | {fv} | {str(vv)[:14]} | {nm}")

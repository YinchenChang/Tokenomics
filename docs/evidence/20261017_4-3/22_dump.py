"""把 rows.pkl 傾印成純文字供逐列閱讀。用法：python3 22_dump.py <rows.pkl> <out.txt>"""
import sys, pickle
rows = pickle.load(open(sys.argv[1], "rb"))
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for i, x in enumerate(rows):
        cs = x["cells"]
        rng = cs[0] if len(cs) == 1 else f"{cs[0]}..{cs[-1]}"
        v = x["value"]
        if isinstance(v, float): v = f"{v:.4g}"
        f.write(f"#{i} {x['sheet']}!{x['row']} [{rng}] n={x['n']} core={'Y' if x['row_has_core'] else 'N'} users={x['users']}\n   L={x['label'][:70]} | V={str(v)[:40]} | F={x['formula'][:150]}\n")

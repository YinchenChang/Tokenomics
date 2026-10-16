"""把 run_scenarios.py 的 json 整理成報告用表格（唯讀）。用法：python3 summarize.py <json>

另算兩個導出量（只用重算後的格值，不另設參數）：
- 無限批次上限＝每步接受 token ÷ 每序列每步時間（批次無限大時每 GPU decode tok/s 的極限）
- 達到實測所需的每序列時間縮小倍數：在同一每用戶速度下，要讓 decode tok/s＝實測，每序列每步時間須縮小幾倍
"""
import json
import sys

LMSYS = {"D": 2785, "G": 13386, "Gc": 2785, "Hc": 13386}
MLPERF = {"G": 556, "H": 2327}
d = json.load(open(sys.argv[1]))


def need_mult(acc, speed, fixed, perseq, meas):
    step = 1000 * acc / speed
    if step <= fixed:
        return None
    b_need = meas / speed
    perseq_need = (step - fixed) / b_need
    return perseq / perseq_need


print("## Perf 路線（Sol；V7＝D 欄 Hopper、V8＝G 欄 GB200）")
print("| 情境 | 欄 | SLO tok/s/user | 每步接受 | 固定延遲 ms | 每序列 ms | B* | decode tok/s/GPU | ÷LMSYS | 無限批次上限 | 所需縮小倍數 | 綁定 |")
for n, r in d.items():
    P = r["Perf"]
    for c in ("D", "G"):
        acc, spd, fx, ps = P["49"][c], P["41"][c], P["79"][c], P["83"][c]
        tok = P["88"][c]
        print(f"| {n} | {c} | {spd} | {acc:.3f} | {fx:.2f} | {ps:.3f} | {P['87'][c]:.1f} | {tok:.1f} | "
              f"{tok/LMSYS[c]:.3f} | {1000*acc/ps:.0f} | "
              f"{(need_mult(acc, spd, fx, ps, LMSYS[c]) or float('nan')):.2f} | {P['90'][c]} |")

print("\n## Calib 路線（DeepSeek-V3／R1 架構；G＝Hopper、H＝GB200）")
print("| 情境 | 欄 | 速度下限 | HBM | 頻寬 | EP | 每GPU權重 | 固定 ms | 每序列 ms | B* | decode-only 147 | 含prefill 148 | 148÷MLPerf | 147÷LMSYS | 無限批次上限 | 所需縮小倍數(對LMSYS) |")
for n, r in d.items():
    C = r["Calib"]
    for c in ("G", "H"):
        spd, fx, ps = C["118"][c], C["144"][c], C["145"][c]
        dec, tot = C["147"][c], C["148"][c]
        nm = need_mult(1, spd, fx, ps, LMSYS[c + "c"])
        print(f"| {n} | {c} | {spd:.3g} | {C['125'][c]} | {C['126'][c]} | {C['133'][c]} | {C['134'][c]:.1f} | {fx:.2f} | {ps:.3f} | "
              f"{C['146'][c]:.1f} | {dec:.0f} | {tot:.0f} | {tot/MLPERF[c]:.3f} | {dec/LMSYS[c+'c']:.3f} | {1000/ps:.0f} | "
              f"{(nm or float('nan')):.2f} |")

print("\n## Checks")
for n, r in d.items():
    print(n, r["Checks"])

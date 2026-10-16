"""把 q4_results.json 整理成報告用的表（印到標準輸出）。用法：python3 summarize.py <q4_results.json>"""
import json
import sys

R = json.load(open(sys.argv[1]))
S0 = R["S0_基準"]
print("| 情境 | C 校準 DeepSeek 2,324 | D 校準 vLLM 10.1K | E 驗證 V15 1,850 | F 驗證 V7 LMSYS H100 | G 驗證 V8 LMSYS GB200 | V2 MLPerf server GB200 | V3 GB300 server | V5 GB200 interactive | V1 | 驗證失敗數 | Sol IF_TokGW Hopper／GB200 | L1_MFleet | IF_AllocRDGW |")
print("|" + "---|" * 14)
for n, r in R.items():
    J = r["J"]
    ck = r["Checks"]
    print(f"| {n} | {J['C']['ratio']:.3f} | {J['D']['ratio']:.3f} | {J['E']['ratio']:.3f} | {J['F']['ratio']:.3f} | {J['G']['ratio']:.3f} | "
          f"{ck['V2']:.3f} | {ck['V3']:.3f} | {ck['V5']:.3f} | {ck['V1']:.3f} | {ck['VF']} | {r['IF_Sol']['Hopper']:.2f}／{r['IF_Sol']['GB200']:.2f} | "
          f"{r['L1_MFleet']:.4f} | {r['IF_AllocRDGW']:.4f} |")
print()
for n, r in R.items():
    print("##", n)
    print("  J B*:", {c: round(r["J"][c]["B"], 1) for c in "CDEFG"}, " J η:", {c: round(r["J"][c]["eta"], 4) for c in "CDEFG"})
    print("  H B*:", {c: round(r["H"][c]["B"], 1) for c in "CDEFGH"}, " H ratio:", {c: round(r["H"][c]["ratio"], 3) for c in "CDEFGH"},
          " H tok:", {c: round(r["H"][c]["tok"], 0) for c in "CDEFGH"})
    print("  Perf B*:", {c: round(r["Perf"][c]["B"], 1) for c in "CDEFGH"}, " Perf dec:", {c: round(r["Perf"][c]["dec"], 0) for c in "CDEFGH"})
    print("  IF Sol:", {g: round(x, 2) for g, x in r["IF_Sol"].items()}, " Luna:", {g: round(x, 2) for g, x in r["IF_Luna"].items()},
          " Astra:", {g: round(x, 2) for g, x in r["IF_Astra"].items()})
    if r.get("b_info"):
        print("  k_cal:", r["b_info"]["kcal"])
        bad = {k: v for k, v in r["verify_B"].items() if abs(v[0] - v[1]) > 1e-3 * max(1, abs(v[0]))}
        print("  verify mismatches:", bad)
        print("  fixedpoint k:", {k: round(v[1], 3) for k, v in r["b_info"]["fixedpoint"].items()})

"""列出 MLPerf Inference v5.1 summary_results.json 中全部 deepseek-r1 列（SRC_PERF_060、081 第二來源查證）。
資料：https://raw.githubusercontent.com/mlcommons/inference_results_v5.1/main/summary_results.json（2026-10-17 下載，未放入 repo）
用法：python3 -I 04_mlperf51.py <summary_results.json> > 04_mlperf51_deepseek列.txt
欄位：ID、提交者、組別、可得性、系統、情境、a#（加速器數欄；GB200／GB300 列此欄為節點數 4，每 GPU 應除以 72）、總 tokens/s、總 ÷ a#"""
import json, sys
rows = json.load(open(sys.argv[1]))
for r in rows:
    if 'deepseek' in str(r.get('Model')).lower():
        a = r.get('a#'); p = r.get('Performance_Result')
        print(r['ID'], r['Submitter'], r['Category'], r['Availability'], r['System'][:60], r['Scenario'], a, p, round(p / a, 1) if a and p else None)

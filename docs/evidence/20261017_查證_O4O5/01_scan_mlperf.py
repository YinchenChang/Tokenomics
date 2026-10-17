"""O5／O4 查證：掃描 MLPerf Inference v6.1 summary.csv 與 v6.0 summary_results.json 中
DeepSeek-R1 的 Hopper（H100／H200）與 Rubin（VR200）列，以及 GB300 列（對照）。
資料（2026-10-17 下載，未放入 repo）：
  v6.1: https://raw.githubusercontent.com/mlcommons/inference_results_v6.1/4bb63cd28eb136be221bc801a9e38c66c8a7553f/summary.csv
        （SHA-256 87980a2dfba85139ca806b63634305bcbc4ad6803bf2d520351e022ba905065a，與 SRC_PERF_055 所記相同）
  v6.0: https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json
用法：python3 -I 01_scan_mlperf.py <v6.1 summary.csv> <v6.0 summary_results.json> > 01_scan_輸出.txt
"""
import csv, json, sys

KEYS = ['H200', 'H100', 'Rubin', 'VR', 'GB300', 'GB200']

print('=== v6.1 summary.csv：deepseek 列（加速器名含 H100/H200/Rubin/VR/GB300/GB200）')
for r in csv.DictReader(open(sys.argv[1])):
    acc = r['accelerator_model_name']
    if 'deepseek' in r['Model'].lower() and any(k in acc for k in KEYS):
        n = float(r['total_accelerators'] or 0); v = float(r['Result'])
        print(r['Organization'], r['Division'], r['Availability'], acc, r['Model'],
              r['Scenario'], int(n), v, round(v / n, 1) if n else None, r['Units'])

print('=== v6.0 summary_results.json：deepseek 列（系統名含 H100/H200/Rubin/VR）')
for r in json.load(open(sys.argv[2])):
    if 'deepseek' in str(r.get('Model')).lower() and any(k in str(r.get('System')) for k in ['H200', 'H100', 'Rubin', 'VR']):
        print(r['ID'], r['Submitter'], r['Category'], r['Availability'], str(r['System'])[:70],
              r['Scenario'], r.get('a#'), r.get('Performance_Result'))
print('=== 結束')

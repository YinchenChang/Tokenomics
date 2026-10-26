# 2026-10-26 DeepInfer 證據入庫（只新增證據，不改 Excel）

- 分支：`claude/evidence-deepinfer`；證據資料夾：`docs/evidence/20261026_DeepInfer/`（README＝完整檢核報告）
- 類別：只新增 `docs/evidence/` 與本報告；**model/、builder/、tests/ 未動**，故不需重跑 parity（現行 v21.7 不變）。

## 本輪做了什麼
1. 讀 DeepSeek 開源推理框架 DeepInfer（repo、部署 QA、Pareto 圖）與 DeepSeek 知乎官方文章「實際線上運行數據」表，檢核 TK v21.7。
2. 以 LibreOffice 重算三個情境（Calib 第 67 列 η_d 倍數 ×1／×3／×5）；×1 與現行快取值逐位相同。
3. 未參與製作的代理已獨立核對全部數字（更正 2 處、收斂 4 處過度推論，已改入 README）。

## 主要結果
- prefill 對得上；decode 每卡低估 3.6–4.7 倍（η_d 4.1% vs 隱含 13–23%）。
- η_d ×3／×5：主判讀 0.940 → 0.938／0.934（不動）；`L1_PriceReqBE` 1.634 → 0.725／0.553；`L1_TokLedger_GW25` 1.52 → 3.43／4.52。
- DeepSeek「每卡時 38 美元」可重建為 39.1，屬產能營收（原表註「不考慮波峰波谷」），非實收。

## 檔案
| 檔 | 內容 |
|---|---|
| `README.md` | 完整檢核報告（來源與標記、數字檢核、敏感度、啟示、判斷題 D1–D5） |
| `calc.py` | 報告第 2 節所有推算 |
| `sens_eta_d.py`、`sens_eta_d_結果.txt` | η_d 敏感度重算程式與輸出 |

## 待 Project 判斷
D1–D5（見 README 第 5 節；未回應照預設：η_d 不改只加情境、ProdDerate 維持 0.85、Luna 下一主版換 V4.1 Flash、CacheHit 維持 0.55、快取儲存不改）。

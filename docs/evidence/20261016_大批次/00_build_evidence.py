"""產生 證據表.xlsx（大批次低估查證 A 段）。用法：python3 00_build_evidence.py <輸出 xlsx>"""
import sys

import openpyxl

hdr = ["題號", "數值", "單位與口徑", "日期", "來源（URL）", "標記", "利害關係方與動機", "是否為獨立的第二來源", "讀取狀態", "來源等級", "備註"]
IP_SGL = "Interested-party：SGLang 團隊（推廣自家引擎）；硬體由 Atlas Cloud／合作方提供"
IP_NV = "Interested-party：NVIDIA（硬體與 TensorRT-LLM 供應商，有誘因展示高吞吐）"
IP_DS = "Interested-party：DeepSeek（自家系統揭露；誘因為技術聲譽）"
IP_VL = "Interested-party：vLLM 社群／Red Hat 與合作硬體商（推廣自家引擎）"
rows = [
    # ---- Q1 通訊重疊 ----
    ("Q1", "TBO 在 decode：每裝置 256 token 時 +25.5%（22,310 tok/s/節點）；每裝置 32 token 時 −27%；門檻在每裝置 64–128 token 之間", "每節點 decode 吞吐，開 TBO ÷ 不開；96×H100（decode 9 節點，EP72）", "2025-05-05",
     "https://lmsys.org/blog/2025-05-05-large-scale-ep/", "Interested-party", IP_SGL, "與 Ant H20 為不同團隊、不同硬體（部分獨立）", "WebFetch 讀全文；圖檔未讀", 1, "消融的 EP 寬度文內未寫"),
    ("Q1", "模擬 MTP、每裝置 128 序列：開 TBO 17,552 對不開 12,929 tok/s（+35%）", "同上", "2025-05-05", "https://lmsys.org/blog/2025-05-05-large-scale-ep/", "Interested-party", IP_SGL, "否（同一來源）", "WebFetch 讀全文", 1, "MTP 為模擬"),
    ("Q1", "SBO（單批次重疊）在 BS 20–56 +8%–10%；TBO 只在 BS 64 或 128 以上為正", "每 GPU decode 吞吐；H20，2 節點 16 GPU（Attention-DP16＋EP16）", "2025-09-26",
     "https://lmsys.org/blog/2025-09-26-sglang-ant-group", "Interested-party", "Interested-party：螞蟻集團（自家服務）與 SGLang", "是（不同團隊、不同 Hopper 型號）", "WebFetch 讀全文", 1, "絕對值未給，只給百分比"),
    ("Q1", "decode 用兩個 micro-batch 重疊計算與 all-to-all；all-to-all 不占 SM；計算完成後等待通訊完成", "定性；H800，EP128，每 GPU 128 請求，4K", "2025-02",
     "https://github.com/deepseek-ai/profile-data", "Interested-party", IP_DS, "—", "WebFetch 讀 README；decode.json 未讀", 1, "無消融數字"),
    ("Q1", "H800 每層通訊 120.96 µs（每裝置 32 token、FP8 dispatch＋BF16 combine、9 個專家、50 GB/s）；雙 micro-batch 每層 241.92 µs；61 層 14.76 ms（67 tok/s 上限）；GB200 每層 6.72 µs", "理論推算", "2025-05",
     "https://arxiv.org/abs/2505.09343", "Interested-party", IP_DS, "—", "WebFetch 讀摘要頁與第 2.3.2 節", 1, "模型 Hopper 每層延遲 241.8 µs 與此 241.92 µs 數字相同（模型值由 GB300 擬合 161.2 × 倍數 1.5 得來，非引用此式；巧合，見報告 2.3）"),
    ("Q1", "DBO 與 kernel 改善合計使 H200 由約 1.5k 升到 2.2k tok/s/GPU；未分開兩者貢獻", "每 GPU decode；CoreWeave H200、IB", "2025-12-17",
     "https://vllm.ai/blog/2025-12-17-large-scale-serving", "Interested-party", IP_VL, "—", "WebFetch 讀全文；圖未讀", 1, "無 DBO 單獨消融"),
    ("Q1", "GB200 10.1K decode：計算與通訊重疊列為「未來工作」（即 10.1K 未使用重疊）", "定性", "2026-02-03",
     "https://vllm.ai/blog/2026-02-03-dsr1-gb200-part1", "Interested-party", IP_VL, "—", "WebFetch 讀全文", 1, "直接影響 (a) 對 GB200 校準點的適用性"),
    ("Q1", "GB200 上可關閉 TBO（「避免重疊的通訊比計算長時的浪費」）；7,583 tok/s/GPU decode（2K 輸入）；「批次越大吞吐越高」", "定性＋單點", "2025-06-16",
     "https://lmsys.org/blog/2025-06-16-gb200-part-1", "Interested-party", IP_SGL, "—", "WebFetch 讀全文；批次掃描只在圖中", 1, ""),
    ("Q1", "至少 3 個 micro-batch 才能完全遮蔽（Tc < Tf/2 時）；例：batch 156 的 Mixtral 每專家 39 token，FFN 理論 MFU 25%", "分析式", "2025-04",
     "https://arxiv.org/html/2504.02263v4", "Interested-party", "Interested-party：字節跳動（自家系統）", "—", "WebFetch 讀 HTML；第 7 節評估未取得", 1, "支持「專家 GEMM 效率隨每專家 token 數上升」的物理機制"),
    ("Q1", "已搜尋，未找到：vLLM DBO 開關的吞吐數字", "—", "—", "https://docs.vllm.ai/en/v0.11.1/design/dbo/", "—", "—", "—", "WebFetch 只取得目錄", 3, "管道：WebSearch 2 組、vLLM 部落格 2 篇、vLLM 文件"),
    ("Q1", "讀取被擋：Perplexity 多節點 DeepSeek 部署（單節點對 EP128 的吞吐曲線）", "—", "—", "https://www.perplexity.ai/hub/blog/lower-latency-and-higher-throughput-with-multi-node-deepseek-deployment", "—", "Interested-party：Perplexity", "—", "權限請求逾時，依指示未重試", 3, "服務條件查證已摘要過：40–80 tok/s 區間吞吐急降"),
    # ---- Q2 同硬體、多批次 ----
    ("Q2", "GB200 NVL72（NVIDIA 6.0-0075，72 GPU）：interactive 3,337.8／server 4,668.1／offline 6,752.0", "每 GPU 輸出 tok/s（含 prefill 分攤）；DeepSeek-R1，800／3,880", "2026",
     "MLCommons v6.0 原始資料（docs/evidence/20261016_服務條件/mlperf_v6.0_deepseek-r1.csv）", "Interested-party", IP_NV + "；MLCommons 稽核", "否（同一提交者三情境）", "repo 內原始資料檔", 1, "同一系統、同一軟體的三個批次點"),
    ("Q2", "GB300 NVL72（NVIDIA 6.0-0078，72 GPU）：interactive 3,481.0／server 5,561.6／offline 8,987.2", "同上", "2026", "同上", "Interested-party", IP_NV + "；MLCommons 稽核", "否", "repo 內原始資料檔", 1, ""),
    ("Q2", "offline ÷ server：NVIDIA GB200 1.45、CoreWeave GB200（64 GPU）1.50、Google GB200 1.96、NVIDIA GB300 1.62", "比值（Derived）", "2026", "同上", "Derived", "提交者各自為利害方", "是（不同提交者）", "repo 內原始資料檔", 1, "形狀的第二來源"),
    ("Q2", "H200 8 GPU：batch 1（MTP）158.1 tok/s/user、19.76 tok/s/GPU；並行 1,024（每 rank 128）11.35 tok/s/user、1,436.2 tok/s/GPU", "每 GPU 輸出 tok/s（同一批 GPU 做 prefill）；ISL 1K／OSL 2K；EP8、attention DP", "2025（0.21.0rc1 文件）",
     "https://nvidia.github.io/TensorRT-LLM/0.21.0rc1/blogs/Best_perf_practice_on_DeepSeek-R1_in_TensorRT-LLM.html", "Interested-party", IP_NV, "否（只有兩點）", "WebFetch 讀全文", 1, "B200：274.7 tok/s/user→34.3／GPU；11.67 tok/s/user→4,451／GPU"),
    ("Q2", "Hopper 大批次點：DeepSeek profile 2,324（B 128）、線上 1,850（約 88）、LMSYS 2,785（約 278）", "decode-only 每 GPU", "2025", "既有 SRC_PERF_072／073／062", "Interested-party", IP_DS + "；LMSYS 見上", "是（不同公司）", "沿用服務條件查證", 1, "隱含 MFU 9.3%–12.5%"),
    ("Q2", "GB200 大批次點：vLLM 10.1K、LMSYS 13,386（NVFP4）", "decode-only 每 GPU", "2025–2026", "既有 SRC_PERF_074／063", "Interested-party", IP_VL + "；" + IP_SGL, "是", "沿用服務條件查證", 1, "隱含 MFU 9.0%、11.9%"),
    # ---- Q3 Hopper 中等互動速度 ----
    ("Q3", "H20 分級：TPOT<70 ms，BS 48 → 714；TPOT<50 ms，BS 32 → 675；TPOT<30 ms（約 33 tok/s），BS 12 → 423 tok/s/GPU（MTP）", "每 GPU decode 吞吐；H20（Hopper，FP8 約 0.30 PF、HBM 4.0 TB/s）；EP16", "2025-09-26",
     "https://lmsys.org/blog/2025-09-26-sglang-ant-group", "Analogy", "Interested-party：螞蟻集團與 SGLang", "—", "WebFetch 讀全文", 1, "H20 算力只有 H100 的約 15%，只能作類比"),
    ("Q3", "InferenceX H200（SGLang FP8，8K／1K）：30 tok/s/user → 1,582；50 → 1,235；75 → 932；100 → 739 tok/s/GPU", "每 GPU 總 token（輸入＋輸出；沿用本工作簿擬合點的口徑，本段未重新查核）", "2025-12～2026-09",
     "https://inferencex.semianalysis.com/run/deepseek-r1-on-h200", "Interested-party", "SemiAnalysis（顧問與資料商）", "否", "WebFetch 讀頁面文字", 2, "旁證（紀律：SemiAnalysis 不可單獨使用）"),
    ("Q3", "已搜尋，未找到：非 SemiAnalysis 的 H100／H200 在每用戶 30–60 tok/s 的每 GPU 吞吐（有寫明設定者）", "—", "—", "—", "—", "—", "—",
     "WebSearch 3 組；LMSYS 96×H100、GB200 兩篇；vLLM 兩篇；TensorRT-LLM 最佳實務；dstack H200 對 MI300X（數字只在圖中）；Perplexity（被擋）", 3, "只有 TensorRT-LLM 的 batch 1（158 tok/s/user）與 Ant H20 類比"),
]
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "證據表"
ws.append(hdr)
for r in rows:
    ws.append(list(r))
ws.append([])
ws.append(["說明", "來源等級：1＝原始一手（官方頁、原始資料檔、論文）；2＝獨立第三方量測；3＝二手轉述或未讀到內容。標記依 CLAUDE.md 第 7 節。"])
for col, wdt in zip("ABCDEFGHIJK", (6, 60, 34, 12, 46, 14, 36, 22, 26, 8, 40)):
    ws.column_dimensions[col].width = wdt
wb.save(sys.argv[1])
print(len(rows), "rows")

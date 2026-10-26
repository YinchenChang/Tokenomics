# Anthropic S-1 vs Tokenomics v21.7：推算（只用本檔寫明的數字；無外部依賴）
# 執行：python calc.py
# 單位：S-1 金額為百萬美元；TK 值為 v21.7 Excel 快取值（Cap_In C28/C29、Interface 第 9/13 列、Alloc_In C23:E23、L1 D129）

# ---- S-1 原文數字（S1_原文摘錄.md）----
rev = {'2024': 386, '2025': 4585, 'H1_25': 1163, 'H1_26': 16286}
compute = {'2024': 2522, '2025': 7326, 'H1_25': 2334, 'H1_26': 8945}      # 性質別「Compute and infrastructure」
cor = {'2024': 752, '2025': 2773, 'H1_25': 1019, 'H1_26': 2380}          # 功能別「Cost of revenue」＝付費服務算力（幾乎全部）
sm_func = {'2024': 163, '2025': 911, 'H1_25': 239, 'H1_26': 3808}        # 功能別 S&M（含免費存取算力）
sm_nat = {'2024': 43, '2025': 568, 'H1_25': 120, 'H1_26': 3168}          # 性質別 S,M&P（通路費＋行銷；不含算力）
quarters = {'Q1_25': (376, 944), 'Q2_25': (787, 1390), 'Q3_25': (1382, 2047),
            'Q4_25': (2040, 2945), 'Q1_26': (4731, 3387), 'Q2_26': (11555, 5558)}  # (營收, 算力費用)

# ---- TK v21.7 ----
B4_SERVE = (0.30, 0.41, 0.60)    # 對外服務占機隊（低/基準/高）
B4_FREE = (0.35, 0.46, 0.60)     # 免費占服務
SPEND_BASIS = (0.85, 1.8, 2.3)   # AL_SpendBasis：租用付款 ÷ 持有成本
CAPEX_IT_VR200 = 37.586352       # Interface 第 9 列 VR200 基準（$B/GW）
CAPEX_IT_GB300 = 32.237224
HOLD_TPU = (0.65, 0.70, 0.90)    # IF_NonNV_Hold_TPU
OAI_RATIO_2025 = 1.239           # OpenAI v0.6.3 PxQ 頁 2025 主值（實收 ÷ 機隊持有成本）

print('== 1. 算力用途拆分（以費用占比代替 GW 占比；S-1 稱算力為單一可互換的池）==')
for k in rev:
    paid = cor[k] / compute[k]                       # 上限：Cost of revenue 含少量人事與分攤
    free_ub = (sm_func[k] - sm_nat[k]) / compute[k]  # 上限：差額還含 S&M 人事與分攤
    serve_ub = paid + free_ub
    print(f'{k:6s} 付費服務≤{paid:.3f}  免費服務≤{free_ub:.3f}  對外服務≤{serve_ub:.3f}  '
          f'免費占服務≤{free_ub/serve_ub:.3f}  研發＋內部使用≥{1-serve_ub:.3f}')
lo, base, hi = B4_SERVE
print(f'TK：對外服務 {base}（{lo}–{hi}）；付費服務 {base*(1-B4_FREE[1]):.3f}'
      f'（{lo*(1-B4_FREE[2]):.3f}–{hi*(1-B4_FREE[0]):.3f}）；免費占服務 {B4_FREE[1]}（{B4_FREE[0]}–{B4_FREE[2]}）')

print('\n== 2. 營收 ÷ 全部算力費用（同 TK 1.4 成本範圍；租用口徑）與換到持有成本口徑 ==')
for k, (r, c) in quarters.items():
    x = r / c
    print(f'{k}  營收/算力 {x:.3f}  ×計價倍數 → {x*SPEND_BASIS[0]:.2f}／{x*SPEND_BASIS[1]:.2f}／{x*SPEND_BASIS[2]:.2f}')
for k in ('2025', 'H1_26'):
    x = rev[k] / compute[k]
    print(f'{k}  營收/算力 {x:.3f}  ×計價倍數 → {x*SPEND_BASIS[0]:.2f}／{x*SPEND_BASIS[1]:.2f}／{x*SPEND_BASIS[2]:.2f}')
print(f'趨勢（與計價倍數無關，只要倍數不變）：Q2_26 ÷ 2025 ＝ {(11555/5558)/(4585/7326):.2f} 倍；OpenAI 2025 主值 {OAI_RATIO_2025}')

print('\n== 3. 付費服務的毛利 ==')
for k in rev:
    print(f'{k}  營收 ÷ Cost of revenue {rev[k]/cor[k]:.2f}；毛利率 {1-cor[k]/rev[k]:.3f}')

print('\n== 4. Broadcom TPU 設備租賃：$161.2B 租金（不含利息）、五年；對應 GW 未揭露 ==')
for gw in (3.5, 4.5, 5.0):
    per = 161.2 / gw
    print(f'若涵蓋 {gw} GW → IT 設備每 GW ${per:.1f}B；÷ TK VR200 {per/CAPEX_IT_VR200:.2f}；÷ TK GB300 {per/CAPEX_IT_GB300:.2f}')
print(f'TK TPU 持有比 {HOLD_TPU[1]}（{HOLD_TPU[0]}–{HOLD_TPU[2]}）；持有成本含兩者相近的設施成本，換成 IT 設備成本比會低於持有比')

print('\n== 5. Q3 2026 營收（S-1 留空；用兩個揭露推回）==')
ttm_q3_25 = 197 + 376 + 787 + 1382                 # Q4_24 + Q1–Q3_25
known = 2040 + 4731 + 11555                        # Q4_25 + Q1–Q2_26
a = ttm_q3_25 * 13.0 - known                       # 「TTM revenue increased approximately 1,200%」→ ×13
b = 6.6 * 5300 - known                             # 「over $6.6 million」× 約 5,300 人（期末人數；若以平均人數計會更高）
print(f'TTM 增 1,200% → Q3 ≈ {a:,.0f}；每人營收 × 人數 → Q3 ≥ {b:,.0f}（百萬美元）')

print('\n== 6. 通路費（性質別 S,M&P 增加 3,048 中 2,700 為通路費；行銷增 273）==')
ch_lo = 2700; ch_hi = 2700 + 120                    # 上半年 2025 S,M&P 全額 120 為上限
print(f'2026 上半年通路費約 {ch_lo:,}–{ch_hi:,}，占營收 {ch_lo/16286:.3f}–{ch_hi/16286:.3f}')

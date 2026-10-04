# v5.15 (Block 6) seeds, all Excel-owned once written (same rule as gov_seed2): SRC_Demand +4 records, DB_Evidence +4 rows,
# Decisions A9／A10 (+ A1–A8 status), Gov_Map rows for the Alloc_In inputs. Work order docs/workorders/20261004_v5.15.md (B1–B3).
V = "U-V515"
_STANCE = "OpenAI 管理層公開宣示（經媒體報導）：有呈現成長的誘因"

SRC_RECORDS3 = [
 {'id': 'SRC_DEM_010', 'sheet': 'SRC_Demand', 's': V, 'metric': 'OpenAI API 處理量', 'val': 6, 'lo': None, 'hi': None, 'unit': 'B tok/min',
  'basis': '時點值；API 全部', 'applies': 'OpenAI', 'date': '2025-10-06',
  'src': 'Altman，DevDay 2025（TechCrunch 2025-10-06 報導；Epoch usage reports 收錄）', 'grade': 2, 'stance': '利害關係方',
  'stance_note': _STANCE, 'hand': '二手', 'status': 'Active', 'use': 'Alloc!A 節（AL_DAPI）｜換算', 'note': '10 月時點值；全年平均由 Alloc_In「API 全年平均 ÷ 10 月時點值」換算（A9）', 'ev': 'E166'},
 {'id': 'SRC_DEM_011', 'sheet': 'SRC_Demand', 's': V, 'metric': 'OpenAI API 處理量', 'val': 15, 'lo': None, 'hi': None, 'unit': 'B tok/min',
  'basis': '時點值；「超過」；API 全部', 'applies': 'OpenAI', 'date': '2026-03-31',
  'src': 'OpenAI 融資公告（$122B）；TechRadar、Business Analytics 2026-04 轉述', 'grade': 2, 'stance': '利害關係方',
  'stance_note': 'OpenAI 融資公告：有呈現成長的誘因', 'hand': '二手', 'status': 'Active', 'use': '（備查；Alloc 基準年為 2025，A1；不在模型內使用）',
  'note': '2026 時點值，晚於 2025 穩態基準年（A1）；與 SRC_DEM_010 口徑不同（「超過」；日期不同），不構成 E7 重複', 'ev': 'E167'},
 {'id': 'SRC_DEM_012', 'sheet': 'SRC_Demand', 's': V, 'metric': 'ChatGPT 每日提示數', 'val': 2.5, 'lo': None, 'hi': None, 'unit': 'B 則/日',
  'basis': '全球；其中美國約 0.33B', 'applies': 'OpenAI', 'date': '2025-07-21',
  'src': 'OpenAI 告知 Axios（TechCrunch 2025-07-21 報導）', 'grade': 2, 'stance': '利害關係方',
  'stance_note': _STANCE, 'hand': '二手', 'status': 'Active', 'use': 'Alloc!A 節（AL_DChat）｜換算',
  'note': '2025-07 年中時點值；年內近似線性成長下視同全年平均（A9，Assumed）', 'ev': 'E168'},
 {'id': 'SRC_DEM_013', 'sheet': 'SRC_Demand', 's': V, 'metric': '前沿實驗室（OpenAI）每日 token', 'val': None, 'lo': 10, 'hi': 100, 'unit': 'T tok/日',
  'basis': '由算力推估', 'applies': 'OpenAI（前沿實驗室）', 'date': '2025',
  'src': 'Epoch AI（tokensperday.com 引用）', 'grade': 2, 'stance': '中立',
  'stance_note': 'Epoch AI：獨立研究機構，由算力推估，無銷售誘因', 'hand': '二手', 'status': 'Active', 'use': 'L1 外部對照、Alloc F 節',
  'note': '低 10、高 100 T tok/日（由算力推估的區間）', 'ev': 'E169'},
]
_ROW = lambda eid, claim, src, loc, new, note, sid, stance: [eid, '2026-10-04', claim, src, '二手（待查原文）', loc, '—', new, '補登（G2；2 級）', 'v5.15', note,
                                                              '已處理', sid, '', 'IF_Alloc*、L1_Ans1–9', '2', stance]
EVID_MIG3 = [
 _ROW('E166', 'OpenAI API 處理量 6B tok/min（DevDay 2025-10-06，Altman）', 'TechCrunch 2025-10-06；Epoch usage reports', 'Alloc!A 節', '6 B tok/min',
      '10 月時點值；工作單 v5.15 B2 登錄；原文未直接讀取', 'SRC_DEM_010', '利害關係方'),
 _ROW('E167', 'OpenAI API 處理量「超過」15B tok/min（融資公告，2026-03-31）', 'OpenAI 融資公告（$122B）；TechRadar、Business Analytics 轉述', '（備查）', '15 B tok/min',
      '工作單 v5.15 B2 登錄；CC 2026-10-04 以網路搜尋交叉確認「15 billion tokens per minute」見於多家轉述（pulse2、CoinDesk 2026-04-01 等）；openai.com 原文未能直接讀取，仍為二手', 'SRC_DEM_011', '利害關係方'),
 _ROW('E168', 'ChatGPT 每日提示數 2.5B（2025-07-21；美國約 0.33B）', 'OpenAI 告知 Axios（TechCrunch 2025-07-21）', 'Alloc!A 節', '2.5 B 則/日',
      '年中時點值視同全年平均（A9）；工作單 v5.15 B2 登錄', 'SRC_DEM_012', '利害關係方'),
 _ROW('E169', '前沿實驗室每日 token 10–100T（Epoch AI 由算力推估）', 'Epoch AI（tokensperday.com 引用）', 'L1 外部對照', '10–100 T tok/日',
      '工作單 v5.15 B2 登錄；CC 2026-10-04 搜尋未找到 tokensperday.com 或 Epoch 原始頁，數值未查核，仍為二手', 'SRC_DEM_013', '中立'),
]

DECISIONS_V515 = [
 ['A9', 'Block 6', '需求 D 的來源',
  'token 路線為基準，支出路線並列為外部對照（選項 (c)）。API：SRC 原始值（每分鐘 token）× 全年平均比例 × 525,600 分鐘。ChatGPT：SRC 每日提示數 × 每則提示 token 數 × 365。'
  'OpenAI 模型 v0.5 的 FY2025 2,628T 是下游推導值，不進 Source，也不連結。年化：API 為 10 月時點值，乘「全年平均比例」；ChatGPT 的 2025-07 每日提示數視同全年平均（年內近似線性成長），不另設輸入',
  '2026-10-04', '「D: 先做網路搜索，看看有沒有新的資訊，若無:(c)」；「我沒意見，請繼續」；年化處理：「(a) 保留，Gov_Map 写明理由（建议）」', 'v5.15 已建',
  'Alloc_In、Alloc A 節；SRC_DEM_010–013', '工作單 v5.15 B1', '否'],
 ['A10', 'Block 6', '每則提示 token 數',
  '基準 2,000，區間 1,000–6,000，Assumed。包含輸入、上下文、推理與輸出 token。上限 6,000 為 chat 端依推理模型與長對話酌定，沒有直接來源。標為 Q1 的最弱輸入',
  '2026-10-04', '「我沒意見，請繼續」（工作單 v5.15 B1 新決定 A10）', 'v5.15 已建', 'Alloc_In 每則提示 token 數；L1_Ans1、L1_Ans2', '工作單 v5.15 B1', '否'],
]
# A1–A8: status "生效（v5.13 建置）" → "v5.15 已建" (applied once, only while the cell still holds the v5.13 value)
DEC_STATUS_V515 = {f"A{i}": {'G': ('生效（v5.14 建置；版號調整見交接第 0 節）', 'v5.15 已建')} for i in range(1, 9)}

_SC = '切片三（v5.15 Block 6）'
_N = 'Alloc_In'
_LAB = {'Nmajor': '家族計畫數 N_major（個／年）', 'Nrefresh': '改版計畫數 N_refresh（個／年）', 'k': '計畫規模倍數 k（相對 Block 3）',
        'g': '機隊年成長率 g', 'APIratio': 'API 全年平均 ÷ 10 月時點值', 'TokPerPrompt': '每則提示 token 數', 'FreeShare': 'ChatGPT token 中免費用戶占比'}
_ROWS = {'Nmajor': 6, 'Nrefresh': 7, 'k': 8, 'g': 12, 'APIratio': 13, 'TokPerPrompt': 14, 'FreeShare': 15}   # Alloc_In row numbers (labels are re-checked at build)
_REASON = {
 'Nmajor': '8f 驅動表：前沿實驗室每年約 1–2 個旗艦家族（基準 1）',
 'Nrefresh': '8f 驅動表、A2：改版計畫計入（基準 2，區間 0–4）',
 'k': 'A3：不以 59% 校準 k；基準 k＝1，校準值只反推隱含 N × k 並列 J8 落差（區間 0.5–7）',
 'g': 'A6：成長只作情境；基準為穩態年度（A1）；成長情境下研發計畫依未來需求定規模',
 'APIratio': 'A9：API 處理量為 2025-10 時點值，乘全年平均比例換成全年平均（Assumed）',
 'TokPerPrompt': 'A10：含輸入、上下文、推理與輸出 token；上限 6,000 為 chat 端依推理模型與長對話酌定，沒有直接來源；Q1 最弱輸入。'
                 'A9 年化：SRC_DEM_012 的 2025-07 每日提示數為年中時點值，在年內近似線性成長下約等於全年平均，因此直接視同全年平均，不另設輸入（Assumed）',
 'FreeShare': '新增；以 L1 外部對照（免費服務算力占比對 SRC_DEM_005 ÷ SRC_DEM_004）檢查',
}
_SRC = {'APIratio': ('SRC_DEM_010', '換算（時點值→全年平均）'), 'TokPerPrompt': ('SRC_DEM_012', '換算（每日提示數 × 每則 token；2025-07 視同全年平均）'),
        'FreeShare': ('SRC_DEM_005', '外部對照（免費推論支出占比，支出口徑）')}

GOV_MAP_V515 = [{'scope': _SC, 'sheet': _N, 'cell': 'C5', 'label': '實驗室', 'cls': 'Decision', 'role': '單值', 'src': '', 'rel': '', 'dec': 'A8',
                 'lo': None, 'hi': None, 'rtext': '結構選擇（無數值區間）', 'reason': 'A8：建「實驗室」選擇器，只放 OpenAI 一組；Anthropic 待來源查核後加入', 'retag': '', 'seg': '—'}]
for _k, _r in _ROWS.items():
    _s = _SRC.get(_k, ('', ''))
    GOV_MAP_V515.append({'scope': _SC, 'sheet': _N, 'cell': f'C{_r}', 'label': _LAB[_k], 'cls': 'Assumed', 'role': '基準', 'src': _s[0], 'rel': _s[1], 'dec': '',
                         'lo': f'=Alloc_In!D{_r}', 'hi': f'=Alloc_In!E{_r}', 'rtext': '', 'reason': _REASON[_k], 'retag': '', 'seg': '—'})
    GOV_MAP_V515.append({'scope': _SC, 'sheet': _N, 'cell': f'D{_r}:E{_r}', 'label': _LAB[_k], 'cls': 'Assumed', 'role': '低／高', 'src': '', 'rel': '', 'dec': '',
                         'lo': None, 'hi': None, 'rtext': f'C{_r} 的低、高端點', 'reason': _REASON[_k], 'retag': '', 'seg': '—'})
GOV_MAP_V515 += [
 {'scope': _SC, 'sheet': _N, 'cell': 'C9:C11', 'label': '服務世代組合：GB200', 'cls': 'Assumed', 'role': '群組', 'src': '', 'rel': '', 'dec': '', 'lo': None, 'hi': None,
  'rtext': '各 0–100%，合計 100%（Checks H1）', 'reason': '8f 驅動表：服務機隊的世代組合（GB200／GB300／VR200 基準 40%／40%／20%）；三者合計須為 100%', 'retag': '', 'seg': '—'},
 {'scope': _SC, 'sheet': _N, 'cell': 'D9:E11', 'label': '服務世代組合：GB200', 'cls': 'Assumed', 'role': '低／高', 'src': '', 'rel': '', 'dec': '', 'lo': None, 'hi': None,
  'rtext': 'C9:C11 的低、高端點（各 0–100%）', 'reason': '8f 驅動表：服務機隊的世代組合', 'retag': '', 'seg': '—'},
]

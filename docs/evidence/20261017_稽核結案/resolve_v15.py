"""v15.0（工作單 docs/workorders/20261017_v14.3_稽核結案.md r1）結案後的狀態判定：把 O1–O22 的處置寫回總帳。

用法：環境變數 LEDGER_SUFFIX=_v15.0 時，30_build_ledger.py／40_write_report.py 載入本模組，輸出另存為帶後綴的新檔（ledger_v15.0.json、
20261017_稽核結案對帳_明細_v15.0.xlsx、20261017_稽核結案對帳_v15.0.md）；原結案報告與原總帳不覆寫。
判定依據：現行活頁簿（model/CURRENT＝v15.0）與 Decisions SL46-01…24（Andy 2026-10-17 13:39 照預設；O4、O5：13:52 照建議）。
"""
FIX, DEC, KEEP, OPEN = '已修正', '已記為決策', '刻意保留', '未處理'
V = 'v15.0'

# 待判斷編號 → (狀態, 處理, 查證, 殘餘)
BY_O = {
    'O8': (DEC, 'v15.0 Decisions SL46-13（Andy 13:39 照預設）', 'Hopper 對外標「保守下界」：Calib J5／J67、Interface A2 已加註；V7／V8／V15 失敗照常揭露', '獨立依據仍待找（外部搜尋待辦）'),
    'O9': (FIX, 'v15.0 Checks V16（Decisions SL46-08）', 'V16 F 欄改文字「恆等式（非驗證）」，驗證計數 22／14 → 21／13（失敗 7、警示 1 不變）', ''),
    'O12': (DEC, 'v15.0 Decisions SL46-16；標籤口徑', '縮放倍數 2.42、家族計畫 3.07、機隊占比取 2025 支出比：接受為 Assumed；Fleet_1GW／Amortize／Interface／Cap_In 共 21 列與 12 格已標口徑', '公式與數值未改'),
    'O13': (FIX, 'v15.0 Alloc Q 節＋RNG_Dem004_*（Decisions SL46-01）', 'SRC_DEM_004_Lo／_Hi 以公式接進支出路線；IF_AllocServeGW／Q1／Q2 帶低高兩端；Checks RG4', 'IF_AllocQ1_R2、L1_MFleet 的支出敏感度未納入（待 Project 判斷）'),
    'O14': (FIX, 'v15.0 L1 第 31、59–65 列（Decisions SL46-02）', '外部對照換算成模型單位；第 35 列單位本已一致，加註定義差；新增 SRC_PRC_047', '第 35 列的定義差仍在（Hopper 占比 0.57 對 0.60）'),
    'O17': (DEC, 'v15.0 Decisions SL46-18', 'Astra 預訓練 token 基準維持 60T，Epoch 區間並列', ''),
    'O18': (DEC, 'v15.0 Decisions SL46-19', '研發倍數 J10 接受', ''),
    'O19': (DEC, 'v15.0 Decisions SL46-20', '無來源高敏感 Assumed 輸入總決策：接受為 Assumed，區間已涵蓋；席次占比與每則提示 token 數列入外部搜尋待辦', '證據仍待補（後續外部搜尋）'),
    'O20': (FIX, 'v15.0 Alloc_In κ 推導區塊＋Checks KP（Decisions SL46-10）', 'κ 推導搬進活頁簿（公式），AL_Kappa 值不變（1.0）；重算值見 AL_KappaCalc', '重算值與 v5.36A 的 1.035 不同（4K 欄已不存在、權重改用需求 token）'),
}
# 主題 → (狀態, 處理, 查證, 殘餘)；O15 逐項
BY_TOPIC = {
    'B11': (FIX, 'v15.0 Interface 第 193 列 IF_FrontSuccVRQual（SL46-03）', '守衛旗標：1＝有合格組合、0＝無合格；Harness 第 151–153 列說明已標', '原「無合格」文字行為不變（刻意）'),
    'B20': (DEC, 'v15.0 Decisions SL46-04', 'Training 第 74、97、100 列口徑標註（decode 計價、不含 prefill；參考模型前向 ÷3）；數值不改', '改機制會動數值，列待 Project 判斷'),
    'Y9': (FIX, 'v15.0 Decisions SL46-05', 'Sens_Rev 折扣兩列連結 Cap_In D12／E12；Sens_Train 第 13 列端點改 Gov_Map GM519 區間 0.18／0.35', 'Train_In H6 說明仍寫 0.15–0.40（Excel 擁有），待 Project 判斷'),
    'F16': (DEC, 'v15.0 Decisions SL46-06', 'Cap_In G81 註記：低高欄為多輸入角落組合（包絡，非機率區間）', '改獨立加總會動數值，列待 Project 判斷'),
    'F17': (FIX, 'v15.0 Alloc Q 節（Decisions SL46-01）', 'SRC_DEM_004_Lo／_Hi 現被公式引用', ''),
    'F12': (FIX, 'v15.0 Alloc_In κ 推導區塊（SL46-10）', 'κ 推導已在簿內（公式）；AL_Kappa 值不變', '重算值 ≠ 1.035（見 O20）'),
    'G11': (FIX, 'v15.0 Checks V16（SL46-08）', 'V16 標「恆等式（非驗證）」並移出驗證計數', ''),
    'B07': (FIX, 'v15.0 L1 第 59、60 列（SL46-02）', 'M59／M60 外部比乘每 GW 機架數比後再比', '換算後仍有差距屬實質差異'),
    'G13': (DEC, 'v15.0 Decisions SL46-16', '訓練成本 100% 利用率、服務 ÷IF_Util：標籤已寫明口徑', ''),
    'G14': (DEC, 'v15.0 Decisions SL46-16', '縮放倍數 2.42、家族計畫 3.07：接受為 Assumed，標籤已寫明口徑', ''),
    'G15': (DEC, 'v15.0 Decisions SL46-16', '機隊占比取 2025 支出比：接受為 Assumed，標籤已寫明口徑', ''),
    'B15': (DEC, 'v15.0 Decisions SL46-16', '攤提對象為 1 GW 參考機隊：接受為 Assumed，標籤已寫明口徑', ''),
}
KEEP_TOPICS = ('G10', 'G12', 'G16', 'G18', 'G19', 'G21', 'G22', 'G23', 'B13', 'B14', 'B19', 'B22')
KEEP_ENTRY = (KEEP, 'v15.0 Decisions SL46-07（O15 其餘小項記為刻意保留，逐項理由見該筆）', '基準影響 0 或僅註記性；理由見 SL46-07', '')


def apply_findings(FINDINGS):
    n = 0
    for k, (st, how, ev, res) in BY_TOPIC.items():
        if k in FINDINGS and FINDINGS[k]['status'] == OPEN:
            FINDINGS[k].update(status=st, how=how, evidence=ev, residual=res); n += 1
    for k in KEEP_TOPICS:
        if k in FINDINGS and FINDINGS[k]['status'] == OPEN:
            FINDINGS[k].update(status=KEEP_ENTRY[0], how=KEEP_ENTRY[1], evidence=KEEP_ENTRY[2], residual=KEEP_ENTRY[3]); n += 1
    return n


def apply_rows(ledger):
    """第 0、1 段不經主題判定的列：未處理者依其待判斷編號改判（O15 一律刻意保留）。"""
    n = 0
    for r in ledger:
        if r['status'] != OPEN:
            continue
        o = r['open']
        if o in BY_O:
            st, how, ev, res = BY_O[o]
        elif o == 'O15':
            st, how, ev, res = KEEP_ENTRY
        else:
            continue
        r.update(status=st, how=how, evidence=ev, residual=res); n += 1
    return n


def patch_DZ(ns):
    """報告第 2 節 D1–D16、Z1–Z10 對照：把 O8／O9／O12／O13／O20／O14／O15 結案的殘餘文字更新。"""
    D = []
    for x in ns['D']:
        x = list(x)
        if x[0] == 'D5':
            x[5] = '驗證 21＝13 通過／7 失敗／1 警示；V16 已標恆等式（v15.0 O9）'; x[4] = '驗證 21＝13 通過／7 失敗／1 警示'
        elif x[0] == 'D14':
            x[2] = FIX; x[5] = 'SRC_DEM_004 區間已以公式接進支出路線（v15.0 O13）'
        elif x[0] == 'D16':
            x[2] = DEC; x[5] = '訓練 100%／服務 ÷IF_Util 口徑已標籤（v15.0 O12，SL46-16）'
        elif x[0] in ('D6',):
            x[5] = '獨立驗證失敗；Hopper 對外標保守下界（v15.0 O8，SL46-13）'
        elif x[0] in ('D9', 'D13'):
            x[5] = '' if x[0] == 'D9' else '證據待補（外部搜尋待辦；O19 總決策 SL46-20）'
        D.append(tuple(x))
    ns['D'][:] = D
    Z = []
    for x in ns['Z']:
        x = list(x)
        if x[0] == 'Z2':
            x[4] = '口徑已標籤（O12）'
        elif x[0] == 'Z3':
            x[4] = 'Hopper 對外標保守下界（O8）'
        elif x[0] == 'Z4':
            x[4] = 'V23／V24／V16 皆標恆等式（O9）'
        elif x[0] == 'Z6':
            x[4] = '口徑已標籤（O12）'
        elif x[0] == 'Z8':
            x[4] = '證據待補（O19 總決策）'
        elif x[0] == 'Z9':
            x[3] = DEC; x[4] = 'B07（O14）、Y9（O15）已處理'
        Z.append(tuple(x))
    ns['Z'][:] = Z

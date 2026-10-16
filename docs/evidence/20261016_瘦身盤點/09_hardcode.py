"""C5 重跑：只取「疑似參數或門檻」並逐處給建議。用法：python3 09_hardcode.py <wb.pkl> <a.pkl> <out.pkl>"""
import pickle, sys, collections
d = pickle.load(open(sys.argv[1], 'rb')); cells = d['cells']
a = pickle.load(open(sys.argv[2], 'rb'))
out = []
for z in a['c5']:
    if z['ctx'] != '疑似參數或門檻（需判讀）': continue
    s, c, k = z['sheet'], z['const'], z['frag']
    x = cells[(s, z['cell'])]
    if s == 'L1' and c == '0.2':
        act, why, nat, grp = ('外露為具名輸入（建議名稱 L1_CmpTol，標記 Assumed／Decision）',
                              '「±20%」判讀門檻寫死在 96 格的公式內，同時文字「±20% 內」「差距 >20%」也寫死；改門檻時兩處要同步。建議外露一個輸入格，文字用 TEXT(門檻) 組出。', '判斷類', 'H1 L1 對照門檻 0.2')
    elif s == 'L1' and c == '4':
        act, why, nat, grp = ('外露為具名輸入（CoreWeave 隨需牌價的每實例 GPU 數 4，附 SRC 註記）',
                              'SRC_PRC_001 是每實例牌價，「÷ 4」是該實例的 GPU 數；來源寫在公式裡看不到，且 M30、N30 各寫一次。', '判斷類', 'H2 L1 外部值 ÷ 4')
    elif s == 'Spec_Rack' and c in ('1.5', '2.5'):
        act, why, nat, grp = ('外露為具名輸入（Rubin Ultra 機架價格低／高倍數，標記 Assumed，區間 1.5／2.5）',
                              '低、高價以基準價 × 1.5、× 2.5 推得，倍數是無來源的假設，卻藏在公式裡；依 CLAUDE.md 第 7 節 Assumed 須以區間呈現，且應在 Gov_Map 登錄。', '判斷類', 'H3 Rubin Ultra 價格倍數')
    elif s == 'Spec_Rack' and c == '8':
        act, why, nat, grp = ('屬物理慣例，只加註（Gb/s → GB/s：8 bit／byte；pJ/bit → pJ/byte）', '單位換算常數，不是模型參數。', '工程類', 'H4 位元組換算 8')
    elif s == 'Arch' and c == '4':
        act, why, nat, grp = ('屬物理慣例，只加註（注意力 QK^T 與 AV 各 2 FLOPs／MAC，共 4）', '標準注意力 FLOPs 公式的係數。', '工程類', 'H5 注意力係數 4')
    elif s == 'Training' and c == '3':
        act, why, nat, grp = ('屬物理慣例，只加註（前向 1 ＋ 反向 2 ＝ 3 倍前向 FLOPs）', '訓練 FLOPs ＝ 3 × 前向的通用慣例，出現在 90 格（Training 第 34、41、48、69、74、76 列）；若日後要改為 Tech_Registry 條目（例如重算省略），再外露。', '工程類', 'H6 訓練 3 倍')
    elif s == 'Cap_In' and c == '6':
        act, why, nat, grp = ('屬物理慣例，只加註（預訓練 FLOPs ≈ 6 × 啟用參數 × token）', '6ND 慣例係數。', '工程類', 'H7 6ND')
    elif s == 'Cap_In' and c == '0.5':
        act, why, nat, grp = ('屬統計慣例，只加註（Epoch 區間以幾何平均取點估計）', '取 (低 × 高)^0.5 為點估計是口徑選擇；若要改取算術平均或中位數，是判斷類。建議在標籤註明「幾何平均」。', '工程類', 'H8 幾何平均 ^0.5')
    elif s == 'Har_In' and c == '4':
        act, why, nat, grp = ('屬定義常數，只加註（80% 成功率對 20% 失敗的勝算 ＝ 4，logit 尺度）', 'β ＝ ln(4) ÷ ln(50% 時間範圍 ÷ 80% 時間範圍)，4 來自 METR 的 80% 門檻定義。', '工程類', 'H9 logit ln4')
    elif c == '3' and (s == 'Fleet_1GW' or (s == 'Alloc' and 'COUNT' in k)):
        act, why, nat, grp = ('屬結構常數，只加註（三個層級 Luna／Sol／Astra 全部可達才加總）', '層級數 3；若日後增減層級須全頁同步，建議在 README 的「結構常數」一節列出。', '工程類', 'H10 層級數 3')
    elif c == '3' and s == 'Alloc':
        act, why, nat, grp = ('屬版面慣例，只加註（每世代佔 3 欄，+2 取中層）', '欄索引 3*(世代−1)+2 在全簿出現上千處（見 C5 的索引運算類）；建議 4-2 一併評估改用 MATCH 而不是算欄位。', '工程類', 'H11 欄索引 3*(g-1)+2')
    else:
        act, why, nat, grp = ('待判斷：未分類', '', '判斷類', 'H99')
    out.append(dict(sheet=s, cell=z['cell'], row=z['row'], label=z['label'], const=c, frag=z['frag'].replace('\n', ' '), value=x['v'], formula=x['f'][:200] if isinstance(x['f'], str) else x['f'], grp=grp, act=act, why=why, nat=nat))
print(len(out), collections.Counter((z['grp'], z['nat']) for z in out))
pickle.dump(out, open(sys.argv[3], 'wb'))

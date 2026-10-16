# v8.0 (work order docs/workorders/20261016_稽核修正2.md r1, section 4r1 = segment 2-3): annual basis D2 + service GW main basis D14 (major version: IF_AllocQ1／Q2／ServeGW
# change definition from the token route to the spend route; L1_MFleet, L1_LReqFleet and the R&D names change value).
#   L1 2025 annual tier prices (Cap_In M section, blue inputs: reference-request blended list price per tier, base／low／high from the 2Q report 1.3, Derived);
#      the 2025 mixed effective price (same writing as Cap_In row 90: paid mix x list price x (1 - B4_Disc)) and the fleet-basis 2025 price (Alloc K section, AL_PriceFleet25: tier weights
#      renormalised over the reachable tiers per generation, generations weighted by paid-token share, same as AL_PriceFleet). Cap_In H7 (m_fleet, m floor, "must be true" rows), H10 C column
#      (B4_PriceFleet[1]), L1_PriceRealFleet and L1_PriceReqBE read it. The v7.0 value stays as the comparison row "m (2026 list-price comparison)". No further kappa deduction (2Q 1.4).
#   L2 2025 model scale: baseline keeps the fixed model (R1); scenario d2_model_2025 (ARCH_ScaleGen Hopper／GB200 = 0.65, range 0.35–1.1) is in tests/parity/scenarios.yaml; nothing in the workbook.
#   L3 2025 R&D generation mix (Alloc_In four blue rows, Derived, 2Q section 3): Alloc J section blends the family plan GW-years (AL_FamGWyr), the refresh plan GW-years (AL_RefGWyr) and the
#      holding cost (AL_HoldTrain) over the mix (GW shares: harmonic blend of GW-years, share-weighted holding cost, the same as the serving-side capacity blend); a generation whose tiers are
#      not all numeric is excluded and the mix renormalised (D8), the excluded share is shown. Train_In C16 and the Training sheet are untouched.
#   L4 payback on one generation basis: L1_LReqFleet reads the 2025 fleet breakeven L1_FleetBreakeven2025 (Alloc K: AL_HoldGen weighted by the generation mix over the 2025-price revenue per GW);
#      the v7.0 VR200 reading stays as L1_LReqFleet_VR200. L1_PriceReqBE reads the same fleet breakeven. L1_FleetBreakeven／L1_FleetMargin stay VR200 cross-section names (label only).
#      Checks B43 reads AL_MixHopper (block4.py).
#   L5 service GW main basis = spend route (block6.py): AL_Q1／Q2／Q1g／Q2g／ImpliedRDGW and IF_AllocQ1／Q2／ServeGW read AL_ServeGWSpend; the token route stays as AL_Q1_Tok／AL_Q2_Tok
#      (Alloc L section) and IF_AllocServeGW_Tok (Interface K section); L1_ScaleServe relabelled (unexplained gap, value unchanged); L1_ExtServeGW compares the token route with the spend route;
#      L1!L69 source label SRC_DEM_004. Astra Epoch 1.0e27 labelled as the upper bound; three implied-token rows (180B／400B／800B active parameters).
# Every write to an Excel-owned cell is guarded (text not yet present ／ cell still holds its v7.0 value) so a rebuild never overwrites a later Excel edit.
import re
from openpyxl.workbook.defined_name import DefinedName
from common import put, F_IN, F_NOTE, F_BOLD, F_CALC, F_LINK, FILL_KEY, section
import v533
import v535
import v603
import v700

VERSION = "20261016_Tokenomics_v8.0"      # single source of the version string: README!B5 and README!A1 (finish.readme)
DATE = "2026-10-16"
V = "v8.0"
WO = "工作單 docs/workorders/20261016_稽核修正2.md r1 第 4r1 節"
Q2R = "docs/reports/20261016_稽核修正2Q_查證.md"
CHAT_DEF = "chat 端預設（L1–L5 見工作單 4r1），可撤回"
DASH = "—"
SLO = "SLO 不可達"
GENX = "整代不可達"
UN = "AL_UnavailTxt"
TXTM = "m 非數字（本情境）"
TIERS = [("Luna", 1), ("Sol", 2), ("Astra", 3)]
PX25 = {"Luna": (0.1035, 0.0669, 0.3026, "nano 線（OpenAI 官方 GPT-5 nano 頁指向 GPT-5.6 Luna）；高＝mini 線（4o-mini→4.1-mini→GPT-5 mini）；低＝GPT-5 nano 全年"),
        "Sol": (2.184, 1.672, 2.338, "API 主力（4o→4.1→GPT-5→5.2）與 ChatGPT 預設按付費 token 加權（API 2,365：ChatGPT 1,460）；低＝GPT-5 全年；高＝ChatGPT 預設序列"),
        "Astra": (7.174, 2.089, 16.33, "推理旗艦序列（o1→o3→GPT-5 thinking）；低＝同 Sol API 主力；高＝o1 全年；Pro 層（63.9）排除")}
RDMIX = [("Hopper", 0.60, 0.40, 0.75), ("GB200", 0.38, 0.25, 0.55), ("GB300", 0.02, 0.0, 0.05), ("VR200", 0.0, 0.0, 0.0)]
MFLEET_TAIL = "｜m 同時含 API 實際折扣以外的訂閱收入對 API 等值比率（2025 約七成營收為訂閱；2Q 1.4）"
_PATCHED = False
CM = {}          # Cap_In M section rows (filled by cap_in_m; read by l1_rows_new／gov_map_rows／text_update)
AM = {}          # Alloc J／K／L rows (filled by alloc_sections)
RDIN_ROWS = {}   # Alloc_In R&D mix rows (filled by alloc_in_rd_mix)
LAB_RDMIX = lambda g: f"研發世代組合（2025）：{g}"
LAB_N = lambda n: f"Astra 啟用參數情境 {n}B（Epoch 全算為預訓練時的隱含 token 用）"


def _px(s):
    """AL_PriceFleet -> AL_PriceFleet25 (word boundary; AL_PriceFleet25 is not matched again)."""
    return re.sub(r"\bAL_PriceFleet\b", "AL_PriceFleet25", s)


# ================================================================== spec patches (before the specs are written; call right after v603.patch_specs())
def patch_specs():
    global _PATCHED
    if _PATCHED: return
    sp = v533.SPEC
    for key in ("m_fleet", "m_fleet_rs", "m_floor", "need_1", "need_06", "need_03"):
        i = next(i for i, it in enumerate(sp) if it[0] == key)
        it = list(sp[i])
        for k in range(1, len(it)):
            if isinstance(it[k], str): it[k] = _px(it[k])
        it[1] = it[1].replace("機隊口徑混合有效單價（AL_PriceFleet25", "2025 年度機隊口徑混合有效單價（AL_PriceFleet25").replace("機隊口徑單價（AL_PriceFleet25", "2025 年度機隊口徑單價（AL_PriceFleet25")
        if key == "m_fleet": it[1] = it[1].replace("　→ L1_MFleet", MFLEET_TAIL + "　→ L1_MFleet")
        assert "AL_PriceFleet25" in "".join(str(x) for x in it[3:6]), key
        sp[i] = tuple(it)
    sp = v535.SPEC_I
    for i, it in enumerate(sp):
        if it[0] is None and it[1].startswith("I-7. 「必須為真」"):
            sp[i] = (None, "I-7. 「必須為真」：回本所需 L＝L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate × m）（v8.0 L4：2025 機隊口徑，成本用 AL_HoldGen 依 AL_Mix* 加權、營收用 2025 單價；"
                           "原 VR200 口徑見 M 節 L1_LReqFleet_VR200）；與 H6／H7 的 m「必須為真」並列。D 欄 m 取高端（所需 L 低）、E 欄 m 取低端")
        if it[0] == "i_req_fleet":
            it = list(it)
            for k in (3, 4, 5): it[k] = re.sub(r"\bL1_FleetBreakeven\b", "L1_FleetBreakeven2025", it[k])
            it[1] = "回本所需 L（2025 機隊口徑；m＝L1_MFleet；D 欄 m＝L1_MFleet_Hi、E 欄 L1_MFleet_Lo）　→ L1_LReqFleet"
            it[7] = "v8.0 L4：L1_FleetBreakeven2025（Alloc K 節）÷（IF_Util × CTL_ProdDerate × m）；基準值見 L1_LReqFleet；v7.0 的 VR200 口徑（0.530）保留於 M 節對照列"
            sp[i] = tuple(it)
    _PATCHED = True


# ================================================================== Cap_In M section (below the L section; nothing above moves)
SEC_M = ("M. 2025 年度口徑（v8.0 D2／D14，工作單 4r1 L1／L4／L5）：M-1 2025 年度層級單價（藍字，參考請求混合單價，表列未折扣；按在售天數加權，不是按用量）與 2025 混合有效單價；"
         "M-2 m 的單價對照與 2025 單價區間；M-3 回本所需 L 的對照（VR200 舊口徑、恆等式讀法）；M-4 Astra Epoch 上限的隱含 token。欄位：C 基準、D 低、E 高（M-3 欄位同 H7）")


def cap_in_m(wb, l_sec):
    ws = wb["Cap_In"]
    r0 = l_sec["end"] + 2
    assert ws.max_row == l_sec["end"], (ws.max_row, l_sec["end"])
    put(ws, f"A{r0}", SEC_M, F_BOLD)
    r = r0 + 1
    put(ws, f"A{r}", "M-1. 2025 年度層級單價（D2；參考請求 16,384 入／2,048 出／快取命中 0.55 的混合單價，表列未折扣；來源 2Q 報告第 1.3 節）", F_BOLD); r += 1
    for tn, (base, lo, hi, note) in PX25.items():
        put(ws, f"A{r}", f"2025 年度層級單價：{tn}（參考請求混合單價，表列未折扣；在售天數加權）", wrap=True); put(ws, f"B{r}", "$/M")
        put(ws, f"C{r}", base, F_IN, fmt="0.0000", fill=FILL_KEY); put(ws, f"D{r}", lo, F_IN, fmt="0.0000"); put(ws, f"E{r}", hi, F_IN, fmt="0.0000")
        put(ws, f"F{r}", "Derived")
        put(ws, f"G{r}", f"{note}。按在售天數加權，不是按用量（用量占比找不到）；牌價本身是 Interested-party；不再乘能力倍數（2025 價格對應 2025 年的模型）。來源：{Q2R} 第 1.2–1.3 節", F_NOTE)
        for nmx, col in ((f"CAP_Px25_{tn}", "C"), (f"CAP_Px25_{tn}_Lo", "D"), (f"CAP_Px25_{tn}_Hi", "E")):
            wb.defined_names[nmx] = DefinedName(nmx, attr_text=f"Cap_In!${col}${r}")
        CM[f"px_{tn}"] = r; r += 1
    put(ws, f"A{r}", "2025 付費 token 混合有效單價（全層級；B4_MixPaid × 2025 層級單價 ×（1 − B4_Disc）× AL_Kappa；寫法同第 90 列；κ 為 v8.1 M3）", wrap=True); put(ws, f"B{r}", "$/M")
    for col, suf in (("C", ""), ("D", "_Lo"), ("E", "_Hi")):
        # v9.0 M3 (D9): kappa on the price end as on the token end (kappa = 1 in the base case)
        f = "+".join(f"INDEX(B4_MixPaid,1,{t})*CAP_Px25_{tn}{suf}*(1-B4_Disc)" for tn, t in TIERS)
        put(ws, f"{col}{r}", "=(" + f + ")*AL_Kappa", F_CALC, fmt="0.0000", fill=FILL_KEY if col == "C" else None)
    put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", "基準約 1.680（第 90 列 1.9607 的 0.857 倍）；低 0.874、高 2.899（2Q 第 1.3 節）。機隊口徑（可達層級重新正規化）見 Alloc K 節 AL_PriceFleet25", F_NOTE)
    for nmx, col in (("CAP_Price25Mix", "C"), ("CAP_Price25Mix_Lo", "D"), ("CAP_Price25Mix_Hi", "E")):
        wb.defined_names[nmx] = DefinedName(nmx, attr_text=f"Cap_In!${col}${r}")
    CM["mix25"] = r; r += 1
    put(ws, f"A{r}", "2025 混合有效單價 ÷ 2026 快照（第 90 列）", wrap=True); put(ws, f"B{r}", "x")
    for col in "CDE": put(ws, f"{col}{r}", f"={col}{CM['mix25']}/$C$90", F_CALC, fmt="0.000")
    put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", "主要差距來自 Astra：GPT-6 Astra（10／50）比 2025 下半年的頂層（GPT-5，1.25／10）貴得多；Luna、Sol 兩層差不到 10%", F_NOTE)
    CM["ratio25"] = r; r += 1
    put(ws, f"A{r}", "M-2. m 的單價對照（D2）：m＝營收 ÷（機隊付費 token × 單價）；C／D／E 同第 119 列（基準／token 取高／token 取低）。2025 單價區間只作顯示，不乘入 L1_MFleet 的 _Lo／_Hi", F_BOLD); r += 1
    tokrow = v533.ROWS["tok_fleet"]
    CM["tok"] = tokrow
    for key, lab, px, note in (("m26", "m（2026 牌價對照）＝營收 ÷（機隊付費 token × AL_PriceFleet）：v7.0 口徑，單價為 2026 快照，不是 2025 年度單價", "AL_PriceFleet",
                               "v7.0 的 L1_MFleet 值（0.5565）；D2 之前的混用口徑，只作對照 → L1_MFleet_Px2026"),
                              ("m25lo", "m（2025 單價取低端）＝營收 ÷（機隊付費 token × AL_PriceFleet25_Lo）", "AL_PriceFleet25_Lo", "單價低端使 m 較高；顯示用"),
                              ("m25hi", "m（2025 單價取高端）＝營收 ÷（機隊付費 token × AL_PriceFleet25_Hi）", "AL_PriceFleet25_Hi", "單價高端使 m 較低；顯示用")):
        put(ws, f"A{r}", lab, wrap=True); put(ws, f"B{r}", "x")
        for col in "CDE":
            put(ws, f"{col}{r}", f"=IF(ISNUMBER({col}{tokrow}),SRC_DEM_007*1000000000/({col}{tokrow}*{px}),{UN})", F_CALC, fmt="0.0000", fill=FILL_KEY if (col == "C" and key == "m26") else None)
        put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", note, F_NOTE)
        CM[key] = r; r += 1
    put(ws, f"A{r}", "M-3. 回本所需 L 的對照（D2／L4）：C／D／E 同第 240 列（D 欄 m 取高端、E 欄取低端）", F_BOLD); r += 1
    put(ws, f"A{r}", "回本所需 L（VR200 新建、2026 單價、固定模型；不與 2025 m 比較）＝L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m（2026 牌價對照））　→ L1_LReqFleet_VR200", wrap=True); put(ws, f"B{r}", "x")
    for col, mc in (("C", "C"), ("D", "E"), ("E", "D")):
        put(ws, f"{col}{r}", f'=IF(AND(ISNUMBER(L1_FleetBreakeven),ISNUMBER({mc}{CM["m26"]})),L1_FleetBreakeven/(IF_Util*CTL_ProdDerate*{mc}{CM["m26"]}),"{TXTM}")', F_CALC, fmt="0.000")
    put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", "v7.0 的 L1_LReqFleet 值（0.5304）原樣保留；VR200 損益兩平（2026 單價）對 2025 的 m（2026 牌價）混用世代與年度，故不再作為所需 L 的主口徑（v8.0 L4）", F_NOTE)
    CM["lreq_vr"] = r; r += 1
    put(ws, f"A{r}", "對照：恆等式讀法的所需 L＝機隊持有成本 ÷ 實收營收＝（第 109 列 有效服務 GW × Σ 世代占比 × 各世代持有成本）÷ SRC_DEM_007　→ L1_LReqFleet_Id", wrap=True); put(ws, f"B{r}", "x")
    for col, gc in (("C", "C"), ("D", "E"), ("E", "D")):
        put(ws, f"{col}{r}", f"=IF(ISNUMBER({gc}109),{gc}109*SUMPRODUCT(AL_ShareGen,AL_HoldGen)/SRC_DEM_007,{UN})", F_CALC, fmt="0.000")
    put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", "不經每 GW 營收與 m 配對：成本（支出路線 GW × 持有成本）÷ 實收營收。與第 240 列（字面口徑）的差距見報告；列待 Project 判斷", F_NOTE)
    CM["lreq_id"] = r; r += 1
    put(ws, f"A{r}", "M-4. Astra Epoch 上限的隱含 token（D14）：Epoch 1.0e27 為 GPT-6 Astra 叢集總算力（含後訓練，上限）；全算為預訓練時 token＝FLOP ÷（6 × 啟用參數）。基準 token 60T 與參數 180B 不變；差距分配不在本段決定", F_BOLD); r += 1
    for n, nm_ in ((180, None), (400, 400), (800, 800)):
        put(ws, f"A{r}", LAB_N(n), wrap=True); put(ws, f"B{r}", "B 參數")
        if nm_ is None: put(ws, f"C{r}", "=Training!$N$22", F_LINK, fmt="0")
        else: put(ws, f"C{r}", nm_, F_IN, fmt="0", fill=FILL_KEY)
        put(ws, f"F{r}", "Derived（連結 Arch）" if nm_ is None else "Assumed")
        put(ws, f"G{r}", ("連結 Training 第 22 列（Astra 啟用參數，Arch 基準）" if nm_ is None else "2Q 報告第 4.2 節的敏感度情境（參數放大則隱含 token 縮小）；不進任何計算，只用於下列隱含 token 列"), F_NOTE)
        CM[f"n{n}"] = r; r += 1
    for n in (180, 400, 800):
        put(ws, f"A{r}", f"Epoch 全算為預訓練時的隱含 token：啟用 {n}B（T tok；D 欄＝Epoch 區間低端、E 欄＝高端）　→ L1_AstraExtTok_{n}B", wrap=True); put(ws, f"B{r}", "T tok")
        for col, sid in (("C", "SRC_MOD_055"), ("D", "SRC_MOD_055_Lo"), ("E", "SRC_MOD_055_Hi")):
            put(ws, f"{col}{r}", f'=IF(ISNUMBER($C{CM[f"n{n}"]}),IF($C{CM[f"n{n}"]}>0,{sid}/(6*$C{CM[f"n{n}"]}*1000000000)/1000000000000,"{DASH}"),"{DASH}")', F_CALC, fmt="#,##0")
        put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", "180B 基準 926T（463–1,852T）、400B 417T、800B 208T；對照 Train_In 基準預訓練 token 60T。Epoch 數字的口徑見 2Q 報告第 4.1 節（硬體推估，含後訓練）", F_NOTE)
        CM[f"tok{n}"] = r; r += 1
    CM["start"], CM["end"] = r0, r - 1
    return dict(start=r0, end=r - 1, rows=dict(CM))


# ================================================================== L3: Alloc_In R&D generation mix (appended after the existing content)
def alloc_in_rd_mix(wb):
    import v529
    ws = wb["Alloc_In"]
    r = v529._last_row(ws) + 2
    put(ws, f"A{r}", "v8.0 L3：研發世代組合（2025；Derived；GW 占比，四格合計 100%，Checks Z2）。研發算力用的硬體世代組合，與服務世代組合分開輸入；Train_In 第 16 列（訓練世代 VR200）與 Training 頁不動", F_BOLD)
    r += 1
    out = {}
    note = (f"2Q 報告第 3 節（Derived，低信心）：GPT-5.2（2025-12）在 Hopper 與 GB200 NVL72 上訓練；Stargate Abilene GB200 自 2025-06 交付；VR200 雲端最早 2026-09-30 才供應，所以 2025 年 VR200＝0 是高信心結論，"
            f"其餘三個世代的比例是推導。研發偏新世代，但全年平均只略偏新於服務組合（0.6／0.4／0／0）。低／高為各格的區間端點，不是情境（四格各自取端點時合計不為 100%）")
    for g, base, lo, hi in RDMIX:
        put(ws, f"A{r}", LAB_RDMIX(g), wrap=True); put(ws, f"B{r}", "%")
        put(ws, f"C{r}", base, F_IN, fmt="0%", fill=FILL_KEY); put(ws, f"D{r}", lo, F_IN, fmt="0%"); put(ws, f"E{r}", hi, F_IN, fmt="0%")
        put(ws, f"F{r}", "Derived"); put(ws, f"G{r}", note, F_NOTE, wrap=True)
        for nmx, col in ((f"AL_RDMix{g}", "C"), (f"AL_RDMix{g}_Lo", "D"), (f"AL_RDMix{g}_Hi", "E")):
            v529._nm(wb, nmx, f"Alloc_In!${col}${r}")
        out[g] = r; r += 1
    put(ws, f"A{r}", "研發世代組合合計（應為 100%；Checks Z2）")
    put(ws, f"C{r}", "=AL_RDMixHopper+AL_RDMixGB200+AL_RDMixGB300+AL_RDMixVR200", F_CALC, fmt="0%")
    out["sum"] = r
    RDIN_ROWS.update(out)
    return out


# ================================================================== Alloc J／K／L sections (appended after the I section; nothing above moves)
def alloc_sections(wb, R):
    from block6 import _row_of
    ws = wb["Alloc"]
    CF = "CDEF"
    r = ws.max_row + 2
    col = lambda c: f"{c}${R['col']}"
    gi = lambda c: f"{c}${R['genidx']}"
    tr = wb["Training"]
    r104 = _row_of(tr, "後訓練 GPU 小時（SFT＋RL＋蒸餾）"); r18 = _row_of(tr, "每 GW GPU 數")

    def row(key, label, unit, f, fmt, name=None, span=None, note=None, fill=False):
        nonlocal r
        put(ws, f"A{r}", label, wrap=True); put(ws, f"B{r}", unit)
        if isinstance(f, dict):
            for c, v in f.items(): put(ws, f"{c}{r}", v, fmt=fmt, fill=FILL_KEY if fill else None)
        else:
            put(ws, f"C{r}", f, fmt=fmt, fill=FILL_KEY if fill else None)
        if note: put(ws, f"G{r}", note, F_NOTE)
        AM[key] = r
        if name:
            ref = f"Alloc!$C${r}" if span is None else f"Alloc!${span[0]}${r}:${span[1]}${r}"
            wb.defined_names[name] = DefinedName(name, attr_text=ref)
        r += 1

    # ---------------- J. R&D generation mix (L3)
    section(ws, r, "J. 研發世代組合（v8.0 L3；欄 C–F＝Hopper／GB200／GB300／VR200）：研發 GW 年與研發持有成本依 2025 研發世代組合（Alloc_In）加權；各世代以 GW 占比計，家族／改版計畫 GW 年取調和加權"
                   "（固定算力需求在各世代上的 GW 年 ＝ 1 ÷ Σ（占比 ÷ 該世代 GW 年），同服務側產能加權），持有成本取占比加權；不可達世代依 D8 排除並重新正規化，被排除占比另列", 7); r += 1
    row("j_share", "研發世代組合占比（Alloc_In；2025；GW 占比）", "%", {"C": "=AL_RDMixHopper", "D": "=AL_RDMixGB200", "E": "=AL_RDMixGB300", "F": "=AL_RDMixVR200"}, "0%", "AL_RDShareGen", ("C", "F"))
    for t, (tk, tn) in enumerate(TIERS, 1):
        row(f"j_fam{t}", f"家族計畫 GW 年 — {tn}（IF_ProgGWyr_{tk}；各世代；含研發倍數）", "GW·年",
            {c: f"=INDEX(IF_ProgGWyr_{tk},1,{col(c)})" for c in CF}, "0.00000")
    for t, (tk, tn) in enumerate(TIERS, 1):
        p = lambda c, t=t: f"INDEX(Training!$C${r104}:$Q${r104},3*({gi(c)}-1)+{t})"
        g_ = lambda c, t=t: f"INDEX(Training!$C${r18}:$Q${r18},3*({gi(c)}-1)+{t})"
        row(f"j_ref{t}", f"改版計畫 GW 年 — {tn}（後訓練 GPU 小時 × 研發倍數 ÷（每 GW GPU 數 × 8,760）；各世代）", "GW·年",
            {c: f'=IF(AND(ISNUMBER({p(c)}),ISNUMBER({g_(c)})),{p(c)}*IF_RDMult/({g_(c)}*8760),"{SLO}")' for c in CF}, "0.00000")
    nums = lambda c: ",".join(f"ISNUMBER({c}{AM[k]})" for k in ("j_fam1", "j_fam2", "j_fam3", "j_ref1", "j_ref2", "j_ref3"))
    row("j_ok", "可用於研發（三個層級的家族與改版計畫 GW 年皆為數值＝1；否則排除，D8）", "旗標", {c: f"=IF(AND({nums(c)}),1,0)" for c in CF}, "0", "AL_RDGenOK", ("C", "F"))
    row("j_oks", "研發組合中可用世代的占比合計（重新正規化的分母）", "%", f"=SUMPRODUCT(C{AM['j_share']}:F{AM['j_share']},C{AM['j_ok']}:F{AM['j_ok']})", "0.0%", "AL_RDShareOK")
    row("j_excl", "被排除的研發組合占比（世代的家族或改版計畫不可達）", "%", f"=SUM(C{AM['j_share']}:F{AM['j_share']})-C{AM['j_oks']}", "0.0%", "AL_RDShareExcl",
        note="D8：不可達＝不可用，排除並重新正規化，不靜默；基準為 0")
    row("j_w", "研發世代權重（重新正規化後；不可用世代為 0）", "%", {c: f"=IF(AND({c}{AM['j_ok']}=1,AL_RDShareOK>0),{c}{AM['j_share']}/AL_RDShareOK,0)" for c in CF}, "0.0%", "AL_RDWeight", ("C", "F"))
    w = lambda c: f"{c}{AM['j_w']}"

    def harm(rows_by_gen):
        den = "+".join(f"IF({w(c)}>0,{w(c)}/{c}{rows_by_gen},0)" for c in CF)
        return f'=IF(AL_RDShareOK>0,1/({den}),"{SLO}")'
    put(ws, f"A{r}", "層級", F_BOLD)
    for c, (tk, tn) in zip("CDE", TIERS): put(ws, f"{c}{r}", tn, F_BOLD)
    put(ws, f"F{r}", "合計", F_BOLD); r += 1
    fam = {c: harm(AM[f"j_fam{t}"]) for t, c in zip((1, 2, 3), "CDE")}
    fam["F"] = f'=IF(COUNT(C{r}:E{r})=3,SUM(C{r}:E{r}),"{SLO}")'
    row("j_famb", "家族計畫 GW 年（研發組合加權；每層級 1 ÷ Σ（權重 ÷ 該世代家族計畫 GW 年）；→ 第 46 列 AL_FamGWyr）", "GW·年", fam, "0.00000")
    rf = {c: harm(AM[f"j_ref{t}"]) for t, c in zip((1, 2, 3), "CDE")}
    rf["F"] = f'=IF(COUNT(C{r}:E{r})=3,SUM(C{r}:E{r}),"{SLO}")'
    row("j_refb", "改版計畫 GW 年（研發組合加權；調和；→ 第 49 列 AL_RefGWyr）", "GW·年", rf, "0.00000")
    row("j_hold", "研發世代每 GW 年經濟持有成本（權重 × 各世代 IF_HoldEcon；→ 第 52 列 AL_HoldTrain）", "$B/GW/年",
        f'=IF(AL_RDShareOK>0,SUMPRODUCT(C{AM["j_w"]}:F{AM["j_w"]},C{R["hold"]}:F{R["hold"]}),"{SLO}")', "0.000", "AL_HoldRD")
    v7 = lambda tk: f"INDEX(IF_ProgGWyr_{tk},1,AL_TrainCol)"
    row("j_famv", "對照：單一訓練世代（IF_TrainGenDefault＝VR200）家族計畫 GW 年（v7.0 口徑）", "GW·年",
        f'=IF(AND(ISNUMBER({v7("Luna")}),ISNUMBER({v7("Sol")}),ISNUMBER({v7("Astra")})),{v7("Luna")}+{v7("Sol")}+{v7("Astra")},"{SLO}")', "0.00000")
    pv = lambda c: f"IF(AND(ISNUMBER({c}{R['post']}),ISNUMBER({c}{R['gpugw']})),{c}{R['post']}*IF_RDMult/({c}{R['gpugw']}*8760),\"{SLO}\")"
    row("j_refv", "對照：單一訓練世代改版計畫 GW 年（v7.0 口徑；第 47–48 列）", "GW·年",
        f'=IF(AND(ISNUMBER({pv("C")}),ISNUMBER({pv("D")}),ISNUMBER({pv("E")})),{pv("C")}+{pv("D")}+{pv("E")},"{SLO}")', "0.00000")
    row("j_rdv", "對照：研發 GW 年（單一訓練世代口徑，v7.0）", "GW·年",
        f'=IF(AND(ISNUMBER(C{AM["j_famv"]}),ISNUMBER(C{AM["j_refv"]})),AL_k*(AL_Nmajor*C{AM["j_famv"]}+AL_Nrefresh*C{AM["j_refv"]}),"{SLO}")', "0.0000")
    row("j_rdr", "研發 GW 年（研發組合）÷ 單一訓練世代口徑", "x", f'=IF(AND(ISNUMBER(AL_RDGW),ISNUMBER(C{AM["j_rdv"]})),IF(C{AM["j_rdv"]}>0,AL_RDGW/C{AM["j_rdv"]},"{SLO}"),"{SLO}")', "0.000",
        note="研發改用較舊世代（每 GW 產出較低）→ 同樣的算力需求占用更多 GW 年，比值 > 1")
    row("j_holdr", "研發持有成本（研發組合）÷ 訓練世代（VR200）持有成本", "x", f'=IF(AND(ISNUMBER(AL_HoldRD),ISNUMBER(INDEX(IF_HoldEcon,1,AL_TrainCol))),AL_HoldRD/INDEX(IF_HoldEcon,1,AL_TrainCol),"{SLO}")', "0.000")
    r += 1

    # ---------------- K. 2025 annual price and fleet breakeven (L1, L4)
    section(ws, r, "K. 2025 年度單價與機隊損益兩平（v8.0 L1／L4；欄 C–F＝Hopper／GB200／GB300／VR200）：2025 層級單價（Cap_In M 節）依 K1 的可達層級重新正規化；機隊損益兩平＝服務世代組合持有成本 ÷ 2025 單價下的每 GW 營收", 7); r += 1
    flags = lambda c: [f"{c}{R[k]}" for k in ("rl", "rs", "ra")]

    def pg25(suf):
        price = {tn: f"CAP_Px25_{tn}{suf}" for tn, _ in TIERS}
        out = {}
        for c in CF:
            num = "+".join(f"IF({f}=1,INDEX(B4_MixPaid,1,{t})*{price[tn]},0)" for t, (f, (tn, _)) in enumerate(zip(flags(c), TIERS), 1))
            out[c] = f'=IF({c}{R["ok"]}=1,({num})*(1-B4_Disc)/{c}{R["wp"]},"{SLO}")'
        return out
    row("k_pg", "各世代付費 token 2025 混合有效單價＝Σ（可達層級的付費組合權重 × 該層級 2025 單價）×（1 − B4_Disc）÷ 可達層級權重合計（全不可達的世代為文字）", "$/M", pg25(""), "0.0000", "AL_PriceGen25", ("C", "F"),
        note="與第 119 列（2026 快照）同一組可達層級；基準 Hopper 欄排除 Astra")
    row("k_pgl", "同上（2025 單價低端）", "$/M", pg25("_Lo"), "0.0000", "AL_PriceGen25_Lo", ("C", "F"))
    row("k_pgh", "同上（2025 單價高端）", "$/M", pg25("_Hi"), "0.0000", "AL_PriceGen25_Hi", ("C", "F"))
    ss = [f"{c}${R['share']}" for c in CF]; ok = [f"{c}${R['ok']}" for c in CF]; cp = [f"{c}${R['capp']}" for c in CF]

    def fleet_px(rowkey):
        pgc = [f"{c}${AM[rowkey]}" for c in CF]
        num = "+".join(f"IF(AND({s}>0,{o}=1),{s}*{k}*{p},0)" for s, o, k, p in zip(ss, ok, cp, pgc))
        return f'IF(AL_BlendPaid="{GENX}","{GENX}",IF(AND(ISNUMBER(AL_BlendPaid),AL_GenShareOK>0),IF(AL_BlendPaid>0,({num})/AL_GenShareOK/AL_BlendPaid,"{SLO}"),"{SLO}"))'
    put(ws, f"A{r}", "機隊口徑 2025 混合有效單價＝Σ（世代占比 × 各世代付費產能 × 各世代 2025 單價）÷ Σ（世代占比 × 各世代付費產能）；C 基準、D 低端、E 高端　→ Cap_In H7／H10 m_fleet", wrap=True); put(ws, f"B{r}", "$/M")
    put(ws, f"C{r}", "=" + fleet_px("k_pg"), fmt="0.0000", fill=FILL_KEY); put(ws, f"D{r}", "=" + fleet_px("k_pgl"), fmt="0.0000"); put(ws, f"E{r}", "=" + fleet_px("k_pgh"), fmt="0.0000")
    put(ws, f"G{r}", "分子分母同為可達層級、可服務世代，與機隊付費 token（AL_BlendPaid 加權）同口徑；H7 讀 C 欄", F_NOTE)
    for nmx, c in (("AL_PriceFleet25", "C"), ("AL_PriceFleet25_Lo", "D"), ("AL_PriceFleet25_Hi", "E")):
        wb.defined_names[nmx] = DefinedName(nmx, attr_text=f"Alloc!${c}${r}")
    AM["k_pf"] = r; r += 1
    row("k_pfr", "機隊口徑 2025 單價 ÷ 2026 快照機隊口徑單價（AL_PriceFleet）", "x", f'=IF(AND(ISNUMBER(C{AM["k_pf"]}),ISNUMBER(AL_PriceFleet)),C{AM["k_pf"]}/AL_PriceFleet,C{AM["k_pf"]})', "0.0000")
    row("k_rev", "各世代每 GW 付費營收（2025 單價）＝IF_RevGWFleet（該世代基準欄）× 2025 單價 ÷ 2026 單價（同一組可達層級與付費 token，只換單價；IF_Util 基準）", "$B/GW/年",
        {c: (f'=IF(AND(ISNUMBER(INDEX(IF_RevGWFleet,1,{col(c)})),ISNUMBER({c}{AM["k_pg"]}),ISNUMBER({c}{R["pg"]})),IF({c}{R["pg"]}>0,INDEX(IF_RevGWFleet,1,{col(c)})*{c}{AM["k_pg"]}/{c}{R["pg"]},"{SLO}"),"{SLO}")') for c in CF},
        "0.000", "AL_RevGW25", ("C", "F"), note="IF_RevGWFleet＝Fleet_1GW 付費 token × 2026 單價（Theory_Rev 第 67 列），故可依單價比例換算")
    row("k_holdl", "各世代每 GW 年經濟持有成本 — 低成本欄", "$B/GW/年", {c: f"=INDEX(IF_HoldEcon,1,{col(c)}-1)" for c in CF}, "0.000", "AL_HoldGen_Lo", ("C", "F"))
    row("k_holdh", "各世代每 GW 年經濟持有成本 — 高成本欄", "$B/GW/年", {c: f"=INDEX(IF_HoldEcon,1,{col(c)}+1)" for c in CF}, "0.000", "AL_HoldGen_Hi", ("C", "F"))
    ss_ = [f"{c}${R['share']}" for c in CF]

    def wavg(rownum):
        terms = "+".join(f"IF(AND({s}>0,{o}=1),{s}*{c}${rownum},0)" for s, o, c in zip(ss_, ok, CF))
        return f'=IF(AND(ISNUMBER(AL_BlendPaid),AL_GenShareOK>0),({terms})/AL_GenShareOK,{UN})'
    row("k_frev", "機隊每 GW 付費營收（2025 單價；服務世代組合加權，只含可服務世代）", "$B/GW/年", wavg(AM["k_rev"]), "0.000", "AL_FleetRev25")
    put(ws, f"A{r}", "機隊每 GW 年持有成本（服務世代組合加權＝Σ 占比 × AL_HoldGen，只含可服務世代）；C 基準、D 低成本、E 高成本", wrap=True); put(ws, f"B{r}", "$B/GW/年")
    put(ws, f"C{r}", wavg(R["hold"]), fmt="0.000"); put(ws, f"D{r}", wavg(AM["k_holdl"]), fmt="0.000"); put(ws, f"E{r}", wavg(AM["k_holdh"]), fmt="0.000")
    for nmx, c in (("AL_FleetHold", "C"), ("AL_FleetHold_Lo", "D"), ("AL_FleetHold_Hi", "E")):
        wb.defined_names[nmx] = DefinedName(nmx, attr_text=f"Alloc!${c}${r}")
    AM["k_fh"] = r; r += 1
    put(ws, f"A{r}", "機隊損益兩平乘積（2025 機隊口徑）＝機隊持有成本 ÷（機隊每 GW 營收 ÷ IF_Util）：令機隊營收＝持有成本所需的「利用率 × 折減 × L × m」；C 基準、D 低成本、E 高成本　→ L1_FleetBreakeven2025", wrap=True); put(ws, f"B{r}", "x")
    for c in "CDE":
        put(ws, f"{c}{r}", f'=IF(AND(ISNUMBER(AL_FleetRev25),ISNUMBER({c}{AM["k_fh"]})),IF(AL_FleetRev25>0,{c}{AM["k_fh"]}/(AL_FleetRev25/IF_Util),{UN}),{UN})', fmt="0.0000", fill=FILL_KEY if c == "C" else None)
    put(ws, f"G{r}", "取代 L1_FleetBreakeven（VR200 截面）作為所需 L 的損益兩平；成本與營收同為服務世代組合（Hopper 0.6／GB200 0.4）、同為 2025 單價", F_NOTE)
    for nmx, c in (("AL_FleetBE25", "C"), ("AL_FleetBE25_Lo", "D"), ("AL_FleetBE25_Hi", "E")):
        wb.defined_names[nmx] = DefinedName(nmx, attr_text=f"Alloc!${c}${r}")
    AM["k_be"] = r; r += 2

    # ---------------- L. token route comparison rows (L5)
    section(ws, r, "L. token 路線對照（v8.0 L5，D14）：Q1、Q2、服務 GW 的主口徑為支出路線（D 節與 Interface F 節）；本節保留 token 路線作對照，兩者差距列「未解釋」（需求 D、每 GW 產能、支出口徑三者之一偏離）", 7); r += 1
    row("l_q1", "Q1_Tok（token 路線）＝研發 GW ÷（研發 GW＋token 路線服務 GW）", "%",
        f'=IF(AL_ServeGW="{GENX}","{GENX}",IF(AND(ISNUMBER(AL_ServeGW),ISNUMBER(AL_RDGW)),AL_RDGW/(AL_RDGW+AL_ServeGW),"{SLO}"))', "0.0%", "AL_Q1_Tok")
    row("l_q2", "Q2_Tok（token 路線）＝研發 GW × 持有成本 ÷（＋Σ 各世代服務 GW × 各世代持有成本）", "%",
        f'=IF(AL_ServeGW="{GENX}","{GENX}",IF(AND(ISNUMBER(AL_ServeGW),ISNUMBER(AL_RDGW)),AL_RDGW*AL_HoldTrain/(AL_RDGW*AL_HoldTrain+SUMPRODUCT(AL_ServeGen,AL_HoldGen)),"{SLO}"))', "0.0%", "AL_Q2_Tok")
    row("l_gw", "服務 GW 差距（支出路線 − token 路線；未解釋）", "GW", f'=IF(AND(ISNUMBER(AL_ServeGW),ISNUMBER(AL_ServeGWSpend)),AL_ServeGWSpend-AL_ServeGW,{UN})', "0.0000",
        note="＝L1_ScaleServe 的絕對值版本；差距不分配到需求 D、每 GW 產能或支出口徑（D14）")
    row("l_q1d", "Q1 差距（支出路線 − token 路線；百分點）", "%", f'=IF(AND(ISNUMBER(AL_Q1),ISNUMBER(AL_Q1_Tok)),AL_Q1-AL_Q1_Tok,{UN})', "0.0%")
    row("l_q2d", "Q2 差距（支出路線 − token 路線；百分點）", "%", f'=IF(AND(ISNUMBER(AL_Q2),ISNUMBER(AL_Q2_Tok)),AL_Q2-AL_Q2_Tok,{UN})', "0.0%")
    AM["end"] = r - 1
    return dict(AM)


def alloc_patch(wb, R):
    """L3: rows 46／49 (C–E per tier) and 52 now read the Alloc J section (single-generation VR200 reading kept in J as a comparison); labels updated. Returns a log."""
    ws = wb["Alloc"]; log = []
    for c in "CDE":
        ws[f"{c}{R['fam']}"].value = f"={c}{AM['j_famb']}"
        ws[f"{c}{R['ref']}"].value = f"={c}{AM['j_refb']}"
    ws[f"C{R['ht']}"].value = f"=C{AM['j_hold']}"
    ws[f"A{R['fam']}"].value = "家族計畫 GW 年（v8.0 L3：2025 研發世代組合加權，J 節；單一訓練世代 VR200 的 v7.0 口徑見 J 節對照列；含研發倍數）"
    ws[f"A{R['ref']}"].value = "改版計畫 GW 年（v8.0 L3：研發世代組合加權，J 節；第 47–48 列為訓練世代 VR200 對照輸入）＝後訓練 GPU 小時 × 研發倍數 ÷（每 GW GPU 數 × 8,760）"
    ws[f"A{R['ht']}"].value = "研發世代每 GW 年經濟持有成本（v8.0 L3：研發世代組合 × 各世代 IF_HoldEcon，J 節；v7.0 為訓練世代 VR200）"
    ws[f"A{R['rd']}"].value = "研發 GW 年＝k ×（N_major × 家族計畫＋N_refresh × 改版計畫）（v8.0 L3：2025 研發世代組合加權）"
    log.append("Alloc rows %d／%d／%d: read the J section (v8.0 L3)" % (R["fam"], R["ref"], R["ht"]))
    # price row labels: the 2026 snapshot stays; the 2025 annual price is in K
    pf = int(wb.defined_names["AL_PriceFleet"].attr_text.split("$")[-1])
    a = ws[f"A{pf}"].value
    tail = "（2026 快照單價；v8.0 起 m 與回本比較改讀 K 節 AL_PriceFleet25，2025 年度單價）"
    if tail not in a: ws[f"A{pf}"].value = a + tail; log.append(f"Alloc!A{pf}: label")
    return log


# ================================================================== Interface K section (appended at the end) and Checks Z2
def interface_k(wb):
    ws = wb["Interface"]
    start = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, start, "K. 服務 GW 的 token 路線對照（v8.0 L5，D14）：IF_AllocServeGW 為支出路線主口徑；本列保留 token 路線供對照，兩者差距未解釋（L1_ScaleServe）", 17)
    r = start + 1
    put(ws, f"A{r}", "服務 GW 合計（token 路線；付費＋免費；IT 關鍵電力；對照用，v8.0 D14 起不是主口徑）　[IF_AllocServeGW_Tok]"); put(ws, f"B{r}", "GW")
    put(ws, f"C{r}", "=AL_ServeGW", fmt="0.0000")
    wb.defined_names["IF_AllocServeGW_Tok"] = DefinedName("IF_AllocServeGW_Tok", attr_text=f"Interface!$C${r}")
    return dict(start=start, row=r)


def checks_z2(wb):
    ws = wb["Checks"]
    r = max(c.row for row in ws.iter_rows() for c in row if c.value is not None) + 2
    section(ws, r, "Z2. 研發世代組合檢查（工作單 稽核修正2 4r1 L3，v8.0）：Z2 為 ERROR 計入 GOV_Errors", 6); r += 1
    for i, h in enumerate(["編號", "檢查", "等級", "筆數", "範圍與算法"]): put(ws, f"{'ABCDE'[i]}{r}", h, F_BOLD)
    r += 1
    put(ws, f"A{r}", "Z2"); put(ws, f"B{r}", "研發世代組合 Hopper＋GB200＋GB300＋VR200（Alloc_In，2025）合計 ≠ 100%（容差 1e-9）"); put(ws, f"C{r}", "ERROR", F_BOLD)
    put(ws, f"D{r}", "=IF(ABS(AL_RDMixHopper+AL_RDMixGB200+AL_RDMixGB300+AL_RDMixVR200-1)>1E-9,1,0)", fmt="0")
    put(ws, f"E{r}", "Alloc_In 研發世代組合四格（基準欄）", F_NOTE)
    ref = wb.defined_names["GOV_Errors"].attr_text.split("!")[1].replace("$", "")
    cell = ws[ref]
    if f"D{r}" not in str(cell.value): cell.value = f"{cell.value}+D{r}"
    ws[f"B{int(ref[1:])}"].value = "ERROR 合計（CI 讀取 GOV_Errors；含 G、H、X、Y、Z、Z2 節）"
    wb.defined_names["CHK_RDMixSum"] = DefinedName("CHK_RDMixSum", attr_text=f"Checks!$D${r}")
    return r


# ================================================================== L1 rows (appended last) and patches of existing rows
def _row(key, lab, cond, d, e, f, unit, rdef, read, drv, weak, nmref, where, gap, sid="無外部對照", elo=DASH, ehi=DASH):
    return (key, lab, cond, d, e, f, unit, rdef, read, drv, weak, sid, elo, ehi, nmref, where, gap)


def l1_rows_new():
    c = lambda col, k: f"=Cap_In!${col}${CM[k]}"
    px = "2025 年度單價（Cap_In M 節）"
    out = [
        _row("MFleet_Px2026", "m（2026 牌價對照）＝營收 ÷（機隊付費 token × AL_PriceFleet）：v7.0 口徑", "OpenAI 2025；單價為 2026 快照（AL_PriceFleet），不是 2025 年度單價；v8.0 L1 對照列",
             c("C", "m26"), c("D", "m26"), c("E", "m26"), "x", "低＝token 取高、高＝token 取低（同 L1_MFleet）",
             "v7.0 的 L1_MFleet 值；D2 之前把 2025 營收配 2026 牌價。保留作對照，不進回本比較", "機隊付費 token、2026 快照單價", "同 L1_MFleet：Assumed 分母", "AL_PriceFleet；L1_MFleet", "L1 本頁；Cap_In M 節", "顯示用"),
        _row("Price25Mix", "2025 付費 token 混合有效單價（全層級；B4_MixPaid × 2025 層級單價 ×（1 − B4_Disc））", f"{px}；寫法同 Cap_In 第 90 列；v8.0 L1",
             c("C", "mix25"), c("D", "mix25"), c("E", "mix25"), "$/M", "低／高＝2025 層級單價低端／高端（2Q 第 1.3 節）",
             "按在售天數加權，不是按用量；Astra 的差距最大（2025 加權 7.17，2026 快照 8.04）。用牌價不用實收（以實收取代牌價使 m 恆等於 1，2Q 1.4）",
             "層級對應（Luna 取 nano 線、Astra 取推理旗艦序列）", "牌價本身 Interested-party；層級對應 Derived", "CAP_Price25Mix", "L1 本頁；Cap_In M 節", "顯示用；機隊口徑見 L1_PriceFleet25"),
        _row("PriceFleet25", "機隊口徑 2025 混合有效單價（可達層級重新正規化；世代間以付費 token 占比加權）", "OpenAI 2025；Alloc K 節；v8.0 L1。L1_MFleet、L1_PriceRealFleet、L1_PriceReqBE 讀它",
             "=AL_PriceFleet25", "=AL_PriceFleet25_Lo", "=AL_PriceFleet25_Hi", "$/M", "低／高＝2025 層級單價低端／高端",
             "與機隊付費 token 同口徑（K1）：Hopper 欄排除 Astra（TTFT 不可達）", "層級單價、世代組合、可達層級", "2025 層級單價：Derived", "AL_PriceFleet25", "L1 本頁；Alloc K 節", "顯示用"),
        _row("FleetBreakeven2025", "機隊損益兩平乘積（2025 機隊口徑）＝機隊持有成本 ÷（機隊每 GW 營收 ÷ IF_Util）", "服務世代組合 AL_Mix*（Hopper 0.6／GB200 0.4）加權；營收用 2025 單價；v8.0 L4",
             "=AL_FleetBE25", "=AL_FleetBE25_Lo", "=AL_FleetBE25_Hi", "x", "E＝低成本欄、F＝高成本欄（營收不隨成本欄變）",
             "令機隊營收＝持有成本所需的「利用率 × 折減 × L × m」；L1_LReqFleet 與 L1_PriceReqBE 讀它。L1_FleetBreakeven／L1_FleetMargin 維持 VR200 截面（Checks K4 比對的恆等式）",
             "持有成本（機架價格、折舊年限、WACC）、世代組合、2025 單價", "世代組合：Derived；2025 單價：Derived", "AL_FleetBE25", "L1 本頁；Alloc K 節", "顯示用；所需 L 的中間量"),
        _row("LReqFleet_VR200", "回本所需 L（VR200 新建、2026 單價、固定模型；不與 2025 m 比較）", "L1_FleetBreakeven ÷（IF_Util × CTL_ProdDerate × m（2026 牌價對照））；v7.0 的 L1_LReqFleet 值保留；v8.0 L4",
             c("C", "lreq_vr"), c("D", "lreq_vr"), c("E", "lreq_vr"), "x", "低＝m 取高端、高＝m 取低端（同 L1_LReqFleet）",
             "VR200 損益兩平（2026 單價）對 2025 的 m：世代與年度混用，只作對照，不是回本判讀的主口徑", "VR200 損益兩平、機隊 m", "同 L1_LReqFleet", "L1_FleetBreakeven；L1_MFleet_Px2026", "L1 本頁；Cap_In M 節", "顯示用"),
        _row("LReqFleet_Id", "回本所需 L（恆等式讀法）＝機隊持有成本 ÷ 實收營收", "（第 109 列有效服務 GW × Σ 占比 × 持有成本）÷ SRC_DEM_007；不經每 GW 營收與 m 配對；v8.0 對照列（待 Project 判斷）",
             c("C", "lreq_id"), c("D", "lreq_id"), c("E", "lreq_id"), "x", "低＝GW 取低端、高＝GW 取高端",
             "與 L1_LReqFleet（字面口徑）並列：兩者都高於 L_total 基準時，回本判讀同向；差距來自每 GW 營收（IF_RevGWFleet，付費 GW 占比與實際利用率）與機隊 m 的 token 口徑不同",
             "有效服務 GW、持有成本、2025 營收", "有效服務 GW：Assumed 分母（計價倍數、κ）", "L1_LReqFleet", "L1 本頁；Cap_In M 節", "顯示用；口徑未決"),
    ]
    for n in (180, 400, 800):
        out.append(_row(f"AstraExtTok_{n}B", f"Epoch 全算為預訓練時的隱含 token（啟用 {n}B）＝L1_PretrainFLOP_Astra_Ext ÷（6 × 啟用參數）", "T tok；Epoch 1.0e27 為叢集總算力（含後訓練，上限）；v8.0 D14",
                        c("C", f"tok{n}"), c("D", f"tok{n}"), c("E", f"tok{n}"), "T tok", "低／高＝Epoch 區間低端／高端（SRC_MOD_055_Lo／_Hi）",
                        "差距分配到參數、token 或後訓練，不在本段決定；基準 token 60T 與參數 180B 不變。對照 Train_In 基準預訓練 token", "啟用參數情境（Cap_In M 節）", "Epoch：硬體推估，1 級、中立",
                        f"Cap_In 第 {CM[f'tok{n}']} 列", "L1 本頁；Cap_In M 節", "顯示用", sid="SRC_MOD_055", elo="=SRC_MOD_055_Lo", ehi="=SRC_MOD_055_Hi"))
    return out


def l1_patch(R):
    out = []
    for row in R:
        row = list(row)
        key = row[0]
        if key == "MFleet":
            row[1] = row[1] + MFLEET_TAIL
            row[2] = ("OpenAI 2025；毛額營收 SRC_DEM_007 ÷（機隊付費 token（點估計）× 2025 年度機隊口徑混合有效單價 AL_PriceFleet25）；v8.0 L1（D2）：單價由 2026 快照改為 2025 年度；"
                      "v7.0 的值保留為 L1_MFleet_Px2026")
        elif key == "LReqFleet":
            row[1] = "回本所需壽命期價格係數 L（2025 機隊口徑；m＝L1_MFleet）"
            row[2] = "L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate × L1_MFleet）；v8.0 L4：成本與營收同為服務世代組合、2025 單價；VR200 舊口徑見 L1_LReqFleet_VR200"
            row[7] = ("回本所需 L＝L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate × m）：給定 m，L 至少要多少才達 2025 機隊回本。與 L_total 並列判讀（Cap_In 第 242 列）。"
                      "v7.0 的 VR200 口徑（0.530）保留為 L1_LReqFleet_VR200；兩者口徑不同，不可互比。恆等式讀法見 L1_LReqFleet_Id")
            row[8] = "機隊回本門檻（2025 機隊口徑）、利用率、生產折減、機隊 m"
        elif key == "PriceRealFleet":
            row[2] = "OpenAI 2025；m_fleet × 2025 年度機隊口徑單價（Alloc AL_PriceFleet25；v8.0 L1）；v5.36 B6"
            for k in (3, 4, 5): row[k] = _px(row[k])
        elif key == "PriceReqBE":
            row[2] = "L1_FleetBreakeven2025 ÷（IF_Util × CTL_ProdDerate）× 2025 年度機隊口徑單價（AL_PriceFleet25）÷ L_total；v8.0 L4"
            for k in (3, 4, 5): row[k] = _px(re.sub(r"\bL1_FleetBreakeven\b", "L1_FleetBreakeven2025", row[k]))
        elif key == "FleetBreakeven":
            row[1] = "機隊損益兩平乘積（_Util 層；VR200 截面，非 2025 機隊）：令機隊營收（IF_RevGWFleet，_Util 層）＝持有成本所需的「利用率 × 折減 × L × m」（VR200）"
            row[8] = row[8] + "。v8.0 L4：維持 VR200 截面（Checks K4 比對的恆等式、契約內已列）；2025 機隊口徑見 L1_FleetBreakeven2025，所需 L 讀後者"
        elif key == "FleetMargin":
            row[1] = row[1].replace("（四層口徑：", "（VR200 截面，非 2025 機隊；四層口徑：")
        elif key == "ExtServeGW":
            row[1] = "服務 GW：token 路線（對照）對 支出路線（D14 主口徑）"
            row[2] = "OpenAI 2025；v8.0 D14：IF_AllocServeGW 已改為支出路線，本列以 token 路線（IF_AllocServeGW_Tok，需求 D ÷ 每 GW 產能）為推算、支出路線（推論支出 ÷ 持有成本）為外部對照，差距未解釋"
            assert row[3] == "=IF_AllocServeGW", row[3]
            row[3] = row[4] = row[5] = "=IF_AllocServeGW_Tok"
        elif key == "ScaleServe":
            row[1] = "服務端落差（未解釋）：支出路線服務 GW ÷ token 路線服務 GW（Alloc F 節 ÷ B 節）"
            row[2] = "Decision Use＝下游校準用，不得當產能；X14 (g)；v8.0 D14：主口徑已改支出路線，本列改標為兩路線的未解釋差距，數值不變"
            if "SRC_DEM_018" in row[11]: row[11] = row[11].replace("SRC_DEM_018", "SRC_DEM_004")
        elif key == "PretrainFLOP_Astra_Ext":
            row[1] = "Astra 預訓練算力（external-anchor：Epoch GPT-6 Astra 估計；叢集總算力，含後訓練，為上限）"
            row[2] = "SRC_MOD_055（低高＝_Lo／_Hi）；X14 (f)；v8.0 D14：Epoch 1.0e27 標為上限（GPT-6 Astra 叢集總算力，含後訓練）；隱含 token 見 L1_AstraExtTok_*B"
        elif key == "AstraScale":
            row[1] = "Astra 規模係數（未解釋）：Epoch 上限 ÷ 模型 bottom-up"
            row[2] = "X14 (f)；v8.0 D14：差距分配到參數、token 或後訓練，不在本版決定；數值不變"
        out.append(tuple(row))
    return out


# ================================================================== guarded text updates
SEC_K_OLD = "C＝2025 年度（Alloc 的 AL_PriceFleet）"
SEC_K_NEW = "C＝2025 年度（Alloc K 節的 AL_PriceFleet25，2025 年度層級單價；v8.0 L1，v7.0 為 2026 快照 AL_PriceFleet）"
LAB_K268_OLD = "對照：完整層級組合混合有效單價（第 90 列；需求路線的模型 token 用此價）"
LAB_K268_NEW = "對照：完整層級組合混合有效單價（C 欄＝2025 年度，Cap_In M 節 CAP_Price25Mix；D–F 欄＝第 90 列 2026 快照；需求路線的模型 token 用第 90 列）"


def text_update(wb, append_text):
    log = []
    ci = wb["Cap_In"]
    ref = wb.defined_names["B4_PriceFleet"].attr_text.split("!")[1].replace("$", "")
    k_row = int("".join(ch for ch in ref.split(":")[0] if ch.isdigit()))
    if ci[f"C{k_row}"].value == "=AL_PriceFleet":
        ci[f"C{k_row}"].value = "=AL_PriceFleet25"; log.append(f"Cap_In!C{k_row}: =AL_PriceFleet25 (v8.0 L1)")
    for rr in range(k_row - 3, k_row):
        a = ci.cell(rr, 1).value
        if isinstance(a, str) and SEC_K_OLD in a:
            ci.cell(rr, 1).value = a.replace(SEC_K_OLD, SEC_K_NEW); log.append(f"Cap_In!A{rr}: K section title (v8.0)")
    if ci[f"A{k_row + 1}"].value == LAB_K268_OLD:
        ci[f"A{k_row + 1}"].value = LAB_K268_NEW
        if ci[f"C{k_row + 1}"].value == "=$C$90": ci[f"C{k_row + 1}"].value = f"=$C${CM['mix25']}"
        log.append(f"Cap_In!C{k_row + 1}: 2025 full-tier price (v8.0)")
    return log


# ================================================================== Gov_Map rows for the new blue inputs
def gov_map_rows(wb):
    out = []
    ci, ai = wb["Cap_In"], wb["Alloc_In"]
    sc = "切片三（v8.0 D2／D14）"
    for tn, (base, lo, hi, note) in PX25.items():
        r = CM[f"px_{tn}"]; lab = ci[f"A{r}"].value
        reason = (f"v8.0 L1（{CHAT_DEF}）：2025 年度層級單價，參考請求混合單價（表列未折扣；乘 1 − B4_Disc 後進入 2025 混合有效單價）。{note}。按在售天數加權，不是按用量；牌價本身是 Interested-party，"
                  f"標記 Derived；不再乘能力倍數。來源 {Q2R} 第 1.2–1.3 節（證據表 Q1）。只進 Alloc K 節 AL_PriceFleet25、Cap_In M 節與 L1_MFleet 等")
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '基準', 'src': '', 'rel': '', 'dec': 'AF2d-L1',
                    'lo': f'=Cap_In!D{r}', 'hi': f'=Cap_In!E{r}', 'rtext': f'{lo}–{hi} $/M（低、高端的層級對應見註）', 'reason': reason, 'retag': '', 'seg': '中'})
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'D{r}:E{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '低／高', 'src': '', 'rel': '', 'dec': 'AF2d-L1',
                    'lo': None, 'hi': None, 'rtext': f'C{r} 的低、高端點', 'reason': reason, 'retag': '', 'seg': '—'})
    for g, base, lo, hi in RDMIX:
        r = RDIN_ROWS[g]; lab = ai[f"A{r}"].value
        reason = (f"v8.0 L3（{CHAT_DEF}）：2025 年 OpenAI 研發算力的世代組合（GW 占比），基準 {base:.0%}（{lo:.0%}–{hi:.0%}）。依據 {Q2R} 第 3 節（證據表 Q3）：GPT-5.2 在 Hopper 與 GB200 NVL72 上訓練，"
                  f"Abilene GB200 自 2025-06 交付，VR200 雲端最早 2026-09-30 才供應（VR200＝0 為高信心結論，其餘為低信心推導）。只進 Alloc J 節（AL_FamGWyr／AL_RefGWyr／AL_HoldTrain），"
                  f"Train_In 第 16 列與 Training 頁不動；四格合計 100%（Checks Z2）")
        out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '基準', 'src': '', 'rel': '', 'dec': 'AF2d-L3',
                    'lo': f'=Alloc_In!D{r}', 'hi': f'=Alloc_In!E{r}', 'rtext': f'{lo:.0%}–{hi:.0%}（區間端點，非情境）', 'reason': reason, 'retag': '', 'seg': '中' if g != "VR200" else '無'})
        out.append({'scope': sc, 'sheet': 'Alloc_In', 'cell': f'D{r}:E{r}', 'label': lab, 'check': lab, 'cls': 'Derived', 'role': '低／高', 'src': '', 'rel': '', 'dec': 'AF2d-L3',
                    'lo': None, 'hi': None, 'rtext': f'C{r} 的低、高端點', 'reason': reason, 'retag': '', 'seg': '—'})
    for n in (400, 800):
        r = CM[f"n{n}"]; lab = ci[f"A{r}"].value
        reason = (f"v8.0 D14（{CHAT_DEF}）：Epoch 1.0e27 全算為預訓練時，隱含 token 對啟用參數的敏感度情境（{n}B）。{Q2R} 第 4.2 節。不進任何計算，只用於 Cap_In M-4 與 L1_AstraExtTok_{n}B")
        out.append({'scope': sc, 'sheet': 'Cap_In', 'cell': f'C{r}', 'label': lab, 'check': lab, 'cls': 'Assumed', 'role': '單值', 'src': '', 'rel': '', 'dec': 'AF2d-L5',
                    'lo': ci[f'C{r}'].value, 'hi': ci[f'C{r}'].value, 'rtext': f'單值（{n}B 情境）', 'reason': reason, 'retag': '', 'seg': '無'})
    return out


# ================================================================== DB_Evidence E374–E377 (17 columns A..Q; layout of v700)
_PN = ["Q1", "Q2", "Q3", "Q4"]
EV = {n: f"E{374 + i}" for i, n in enumerate(_PN)}


def _ev(n, claim, src, tag, param, cur, new, verdict, grade, stance, note=""):
    nt = f"{note}｜暫編 {n}｜{CHAT_DEF}｜讀取者：chat 端（{WO}；來源 {Q2R}）"
    return [EV[n], DATE, claim, src, tag, param, cur, new, verdict, V, nt, "已處理", DASH, DASH, "Cap_In M 節；Alloc J／K 節；L1_MFleet、L1_LReqFleet、IF_AllocQ1／Q2／RDGW", grade, stance]


EVIDENCE_V800 = [
    _ev("Q1", "2025 年度各層級時間加權單價（參考請求混合，表列未折扣）：Luna 0.1035（0.0669–0.3026）、Sol 2.184（1.672–2.338）、Astra 7.174（2.089–16.33）；C90 口徑 1.680（現值 1.9607 的 0.857 倍）",
        "OpenAI 官方模型頁（developers.openai.com）、世代價格 A 段已讀官方公告頁、v5.36A 二手彙整（benchlm，等級 3）", "Derived（牌價本身 Interested-party）", "Cap_In M 節 2025 年度層級單價",
        "C90 口徑 1.9607（2026 快照）", "1.680（0.874–2.899）", "採納為 L1 輸入；按在售天數加權而非用量；Astra 取推理旗艦序列、Luna 取 nano 線（待 Project 判斷）", "3（部分快取價為 Derived）", "利害關係方",
        "GPT-4.1／GPT-5／GPT-5.2 的快取價官方頁讀取受阻，由同家族折扣推得，影響小於 3%"),
    _ev("Q2", "各世代服務期間的代表模型規模（相對 2026 Arch）：2025 年度倍數 0.65（0.35–1.1）；Hopper 0.8、GB200 0.55、GB300 1、VR200 1.4。啟用參數沒有隨世代穩定變大；閉源模型啟用參數從未揭露",
        "SemiAnalysis（GPT-4）、Epoch、arXiv 2604.24827、開放權重模型卡", "Analogy（單一樣本、閉源間接估計）", "ARCH_ScaleGen；情境 d2_model_2025", "基準 1（固定模型）", "情境 0.65（0.35–1.1）",
        "不進基準（Analogy 不作點估計）；以情境 d2_model_2025 呈現（R1）", "3", "中立"),
    _ev("Q3", "2025 年 OpenAI 研發算力的世代組合：Hopper 0.60／GB200 0.38／GB300 0.02／VR200 0（區間 0.40–0.75／0.25–0.55／0–0.05／0）；研發與服務的硬體分配已搜尋，未找到",
        "NVIDIA 部落格（GPT-5.2 在 Hopper 與 GB200 NVL72 上訓練）、科技新報、Epoch Abilene、OpenAI CFO", "Derived（低信心推導）", "Alloc_In 研發世代組合", "Train_In 第 16 列＝VR200（訓練世代）",
        "0.60／0.38／0.02／0", "採納為 AL_RDMix*（Alloc J 節）；Train_In 第 16 列不動", "3", "中立"),
    _ev("Q4", "Epoch 1.0e27 為 GPT-6 Astra 單一訓練期間的叢集總算力（≥10 萬顆 GB200 × 約 90 天 × FP8 MFU 25%），不分預訓練與後訓練；全算為預訓練時，啟用 180B 隱含約 926T token（463–1,852T）、400B 約 417T、800B 約 208T",
        "Epoch AI GPT-6 硬體推估；legrandcontinent／PC Gamer 轉述", "Derived（Epoch 硬體推估）", "L1_PretrainFLOP_Astra_Ext 標示；L1_AstraExtTok_*B", "標 Astra 預訓練算力的外部錨點",
        "標為上限；隱含 token 三列", "採納為標示與顯示；基準 token 60T、參數 180B 不變；差距分配不在本段決定", "2（硬體推估）", "中立"),
]


def evidence_rows():
    return EVIDENCE_V800


# ================================================================== Decisions (10 columns; layout of v603／v700)
_D = [
    ("L1", "2025 年度層級單價（D2）：Cap_In M 節藍字輸入", "新增 Cap_In M 節：三層級各一列的 2025 年度參考請求混合單價（表列未折扣；基準／低／高取 2Q 第 1.3 節：Luna 0.1035／0.0669／0.3026、Sol 2.184／1.672／2.338、Astra 7.174／2.089／16.33），"
     "Derived，說明欄寫明按在售天數加權而非用量。2025 混合有效單價＝付費組合 × 單價 ×（1 − B4_Disc）＝1.680（寫法同第 90 列）。機隊口徑（可達層級重新正規化、世代間以付費 token 占比加權，同 K1）為 Alloc K 節 AL_PriceFleet25。"
     "Cap_In H7（m_fleet、m 下限、『必須為真』）、H10 C 欄（B4_PriceFleet[1]）、L1_PriceRealFleet、L1_PriceReqBE 讀它；v7.0 的值保留為 L1_MFleet_Px2026。不另扣 κ（2Q 1.4：以實收取代牌價使 m 恆等於 1）；m 的標籤補『m 同時含 API 實際折扣以外的訂閱收入對 API 等值比率』。"
     "H5（L1_MImplied 等需求路線）與 H8 的 m 仍用第 90 列 2026 單價——工作單 4r1 只列 L1_MFleet，列待 Project 判斷。",
     "Cap_In M-1；Alloc K 節；Cap_In H7／H10／K；L1_MFleet、L1_PriceRealFleet、L1_PriceReqBE、L1_PriceFleet25", "v8.0 已建"),
    ("L2", "2025 年度模型規模（D2 × D1(c)）：採 R1，基準維持固定模型", "R1：基準的年度計算仍用固定模型產能，在標籤中明示；情境 d2_model_2025（ARCH_ScaleGen Hopper、GB200 兩欄＝0.65，其餘 1）及低端 0.35、高端 1.1 兩個情境見 tests/parity/scenarios.yaml 與報告。"
     "理由：2025 年度倍數 0.65 的區間 0.35–1.1 跨過 1，標記 Analogy（依使用者偏好第 3 條，Analogy 不作點估計進入基準；決定紀錄 D1(c) 也寫『作為情境使用』）。這一項偏離 D2『一律取該年度的值』的字面。"
     "R2（另建 Hopper／GB200 的 2025 模型鏡像頁）留待 Andy 選擇，工程量約多 1 小時。", "Spec_Rack ARCH_ScaleGen；情境 d2_model_2025", "v8.0 已建（情境）"),
    ("L3", "2025 研發世代組合（D2）：Alloc J 節", "Alloc_In 新增研發世代組合四格（Hopper 0.60／GB200 0.38／GB300 0.02／VR200 0；區間 0.40–0.75／0.25–0.55／0–0.05／0；Derived，2Q 第 3 節）。"
     "AL_FamGWyr、AL_RefGWyr 改為各世代的 GW 年依研發組合調和加權（固定算力需求在各世代上的 GW 年＝1 ÷ Σ（占比 ÷ 該世代 GW 年），同服務側產能加權），AL_HoldTrain 為占比加權的 IF_HoldEcon；"
     "不可達世代依 D8 排除並重新正規化，被排除占比另列（AL_RDShareExcl）。Train_In 第 16 列與 Training 頁截面輸出（IF_Train*）不動。AL_RDGW、IF_AllocRDGW、AL_RDCost、L1_ScaleRD 隨之變動。"
     "占比取 GW 口徑（與服務側世代組合一致）；若改為算力口徑，調和／算術的角色互換——列待 Project 判斷。", "Alloc_In 研發世代組合；Alloc J 節與第 46／49／52 列；Checks Z2", "v8.0 已建"),
    ("L4", "回本比較同一世代口徑（D2）", "L1_LReqFleet 改為 2025 機隊口徑：L1_FleetBreakeven2025＝服務世代組合持有成本（AL_HoldGen 依 AL_Mix* 加權）÷（機隊每 GW 營收 ÷ IF_Util），營收以 2025 單價換算（Alloc K 節）；m 用 L1_MFleet。"
     "原 VR200 口徑的值保留為 L1_LReqFleet_VR200（標籤：VR200 新建、2026 單價、固定模型；不與 2025 m 比較）。L1_PriceReqBE 與 L1_PriceRealFleet 同為 2025 單價與機隊口徑。"
     "L1_FleetBreakeven／L1_FleetMargin 維持 VR200 截面，只改標籤（寫明『VR200 截面，非 2025 機隊』）；判斷依據：兩者是 Checks K4 比對的恆等式（IF_RevGWFleet_Prod[VR200] ÷ IF_HoldEcon[VR200]），契約第 5 節已列 L1_FleetMargin 為 VR200 倍數，"
     "改為機隊口徑會同時改變契約內既有名稱的定義。Checks B43 的 Hopper 占比改讀 AL_Mix 的 AL_MixHopper（0.6），不再讀 Checks!I46（0.57）。", "L1_LReqFleet、L1_LReqFleet_VR200、L1_FleetBreakeven2025、L1_PriceReqBE；Cap_In 第 240 列與 M-3；Checks B43", "v8.0 已建"),
    ("L5", "服務 GW 主口徑改支出路線（D14）", "AL_Q1、AL_Q2、AL_Q1g、AL_Q2g、AL_ImpliedRDGW 的服務 GW 改讀 AL_ServeGWSpend；AL_Q2 的服務持有成本＝AL_ServeGWSpend × Σ（AL_ShareGen × AL_HoldGen）（＝SRC_DEM_004）。"
     "IF_AllocQ1、IF_AllocQ2、IF_AllocServeGW 隨之改為支出路線（契約改變，主版 v8.0）。token 路線保留為對照列：AL_Q1_Tok、AL_Q2_Tok（Alloc L 節）、IF_AllocServeGW_Tok（Interface K 節）；IF_AllocQ1_R2 維持 token 路線。"
     "L1_ScaleServe 改標『支出路線 ÷ token 路線差距（未解釋）』，數值不變（工作單寫『token 路線 ÷ 支出路線』，與實際比值方向相反，以實際為準）；L1_ExtServeGW 改為 token 路線（推算）對支出路線（外部）；L1!L69 來源標籤改 SRC_DEM_004。"
     "Astra：L1_PretrainFLOP_Astra_Ext 標為 Epoch 1.0e27 上限（叢集總算力，含後訓練）；新增 L1_AstraExtTok_180B／400B／800B（FLOP ÷ 6N）；基準 token 60T 與參數 180B 不變；L1_AstraScale 標『未解釋』。",
     "Alloc D 節與 L 節；Interface F／K 節；L1_ScaleServe／ExtServeGW／AstraScale／AstraExtTok_*", "v8.0 已建"),
]
DECISIONS_V800 = [[f"AF2d-{i}", V, f"稽核修正第 2 批 2-3：{t}", txt, DATE, CHAT_DEF, st, where, f"{WO} {i}", "否"] for i, t, txt, where, st in _D]

# ================================================================== README
README_VERSION = (VERSION + "（主版：稽核修正第 2 批 2-3 段，" + WO + "——D2 年度口徑與 D14 服務 GW 主口徑：Cap_In M 節 2025 年度層級單價、Alloc K 節 AL_PriceFleet25 與 2025 機隊損益兩平、"
                  "L1_MFleet／L1_LReqFleet／L1_PriceReqBE 改 2025 口徑；Alloc_In 研發世代組合與 Alloc J 節（AL_FamGWyr／AL_RefGWyr／AL_HoldTrain 依研發組合加權）；"
                  "IF_AllocQ1／Q2／ServeGW 改支出路線（token 路線保留為 AL_Q1_Tok／AL_Q2_Tok／IF_AllocServeGW_Tok）；Checks B43 讀 AL_MixHopper、Z2；Astra Epoch 上限標示與隱含 token；Decisions AF2d-*）。以下為 "
                  + v700.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v700.README_TITLE
README_TITLE = VERSION.split("_")[-1] + _T[len(v700.VERSION.split("_")[-1]):]
README_ROW = ("2025 年度口徑與服務 GW 主口徑（v8.0）",
              "稽核修正 2-3：m 與回本比較改用 2025 年度層級單價與 2025 機隊口徑（Cap_In M 節、Alloc K 節）；研發算力依 2025 研發世代組合加權（Alloc_In、Alloc J 節）；"
              "Q1、Q2、服務 GW 的主口徑改為支出路線（token 路線保留為對照）。標記與理由見 Gov_Map 與 Decisions AF2d-*。")

"""回本判讀 — m、L、每 GW 營收 P × Q、持有成本與承重輸入（v18.0 起的主輸出）。

資料只來自 Excel：L1 頁的表（基準／低／高、單位、讀法）、各輸入頁的整列（Cap_In、Alloc_In）與具名範圍。
本頁不做任何計算（含比值）：Excel 沒有的數字，本頁不顯示。下列名稱清單只是「顯示哪幾列」的欄位映射。
"""
import pandas as pd
import streamlit as st

from app.common import fmt, get_engine, header_above, input_row, l1_lookup, name_label

# 頁首四張卡：判讀主口徑（交接檔 §2；名稱依 Excel）
HEADLINE = ("L1_LTotalFleetVDisc", "L1_LReqFleet_Full", "L1_RevGW_PQ_VR200", "L1_M")
# P × Q 推導鏈（依 L1 列序：產能 → Q → P 的單價 → m → 營收）
PQ_CHAIN = ("L1_TokGW_PaidCap_VR200", "L1_TokGW_PaidPQ_VR200", "L1_PxList_2026", "L1_PxEff_2026", "L1_M",
            "L1_RevGW_PQ_VR200", "L1_RevGW_PQ_VR200_FY", "L1_RevGW_PQ_VR200_Life",
            "L1_FreeShare_2026", "L1_RevGW_PQ_VR200_F2026", "L1_FreeShare_2030", "L1_RevGW_PQ_VR200_F2030")
# m 序列與分項
M_ROWS = ("L1_M_2025", "L1_M_2026Q1", "L1_M_2026Q2", "L1_M_FY2026", "L1_M", "L1_M_API", "L1_M_Sub", "L1_M_Seat",
          "L1_TokLedger", "L1_TokLedger_2026Q2")
# L 與所需 L、2025 回本比
L_ROWS = ("L1_LTotalFleetVDisc", "L1_LTotalFleetV", "L1_LTotalDisc", "L1_LTotal", "L1_LReqFleet_Full",
          "L1_LReqFleet_IdNoK", "L1_PriceReqBE", "L1_HoldFleet25", "L1_PayRatio25", "L1_RevPerGW25")
# 承重輸入（交接檔 §2「承重輸入（信心低）」與 d）
LOAD_BEARING = ("AL_UtilActual", "B4_Serve", "B4_Free", "AL_SpendBasis", "B4_Disc")
SHOW_COLS = ("基準值", "低", "高", "單位", "指標或問題")


def _l1_table(l1: dict, ids) -> pd.DataFrame:
    rows = []
    for i in ids:
        if i not in l1:
            continue
        r = l1[i]
        rows.append({"名稱": i, **{c: (fmt(r[c]) if c in ("基準值", "低", "高") else r[c]) for c in SHOW_COLS}})
    return pd.DataFrame(rows)


def _details(l1: dict, ids, key: str):
    pick = st.selectbox("看某一列的條件、區間定義與讀法", [i for i in ids if i in l1], key=key,
                        format_func=lambda i: f"{i}｜{l1[i]['指標或問題']}")
    r = l1[pick]
    for c in ("條件", "區間的定義", "讀法", "主要驅動", "最弱輸入的標記"):
        st.markdown(f"**{c}**：{r[c]}")


def render():
    eng = get_engine()
    l1 = l1_lookup(eng)
    st.title("回本判讀 — m、L、每 GW 營收 P × Q")
    st.caption(f"事實來源：`{eng.path.name}`（L1 頁與輸入頁；LibreOffice 重算後的值）。本頁不做任何計算；"
               "低／高為 Excel 的區間欄。Assumed、Analogy、Derived 輸入的判讀一律讀作「在某假設下」。")

    cols = st.columns(len(HEADLINE))
    for c, i in zip(cols, HEADLINE):
        r = l1[i]
        c.metric(f"{i}（{r['單位']}）", fmt(r["基準值"]), help=str(r["指標或問題"]))
        c.caption(f"區間 {fmt(r['低'])}–{fmt(r['高'])}")
    st.info("讀法（Andy 2026-10-22）：看「實際 ÷ 所需」的年度趨勢，不看單一年的絕對值。"
            "上方 L（主口徑）與所需 L（主口徑）並列；兩者的比值不是 Excel 的具名範圍，本頁不另算。")

    st.divider()
    st.subheader("1. 每 GW 營收 P × Q（VR200，新建 1 GW）")
    st.caption("P＝表列牌價 ×（1 − d）× m（× L 為壽命期）；Q＝付費產能 × 對外服務占比 ×（1 − 免費占比）× 實際利用率。"
               "免費占比 2026／2030 兩列是情境，不回流主序列。")
    st.dataframe(_l1_table(l1, PQ_CHAIN), width="stretch", hide_index=True)
    _details(l1, PQ_CHAIN, "pq")

    st.divider()
    st.subheader("2. 收入面 m（付費服務 token 的有效牌價變現率）")
    st.caption("m＝實收單價 ÷ 有效牌價；有效牌價＝表列牌價 ×（1 − d）。m 只看收入面。"
               "token 帳（L1_TokLedger）是診斷，不是 m。注意 m ∝ 1／(1 − d)：改 d 時 m 會變，m ×（1 − d）不變。")
    st.dataframe(_l1_table(l1, M_ROWS), width="stretch", hide_index=True)
    _details(l1, M_ROWS, "m")

    st.divider()
    st.subheader("3. L（壽命期價格係數）與回本所需 L")
    st.dataframe(_l1_table(l1, L_ROWS), width="stretch", hide_index=True)
    gens = header_above(eng, "L1_LDiscGen")
    st.markdown("**各世代折現 L（`L1_LDiscGen`，相對自身起點）**")
    st.dataframe(pd.DataFrame([eng.get_name("L1_LDiscGen")], columns=gens, index=[name_label(eng, "L1_LDiscGen")[0]]).map(fmt),
                 width="stretch")
    _details(l1, L_ROWS, "l")

    st.divider()
    st.subheader("4. 每 GW 年持有成本（各世代；$B/GW·年）")
    hold = {n: eng.get_name(n) for n in ("AL_HoldGen_Lo", "AL_HoldGen", "AL_HoldGen_Hi") if n in eng.names}
    df = pd.DataFrame(hold, index=header_above(eng, "AL_HoldGen")).T
    df.index = [f"{n}｜{name_label(eng, n)[0]}" for n in df.index]
    st.dataframe(df.map(fmt), width="stretch")
    st.caption("2025 機隊每 GW 年持有成本 `AL_FleetHold` ＝ " + fmt(eng.get_name("AL_FleetHold")) +
               "（低 " + fmt(eng.get_name("AL_FleetHold_Lo")) + "、高 " + fmt(eng.get_name("AL_FleetHold_Hi")) + "）。")

    st.divider()
    st.subheader("5. 承重輸入（信心低）")
    st.dataframe(pd.DataFrame([input_row(eng, n) for n in LOAD_BEARING if n in eng.names]).astype(str),
                 width="stretch", hide_index=True)
    st.caption("整列取自輸入頁（標籤、單位、基準、低、高、標記、來源）。改這些值一律改 Excel，網站不提供改值。")

    st.divider()
    st.subheader("6. 非 NVIDIA 晶片（相對 VR200）")
    rows = [eng.row_values("NonNV", r, 10) for r in range(4, eng.max_row("NonNV") + 1)]
    rows = [r for r in rows if any(x != "" for x in r)]
    if rows:
        nn = pd.DataFrame(rows[1:], columns=[str(x) for x in rows[0]])
        st.dataframe(nn.map(fmt), width="stretch", hide_index=True)
        st.caption(str(eng.get("NonNV", "A2")))

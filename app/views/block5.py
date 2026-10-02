"""Block 5 — Harness：任務層的 token、成功率與每成功任務成本。資料只來自 Excel 的具名範圍（Interface E 節、IF_HdrTask）。"""
import streamlit as st

from app.common import b5_chain, b5_front, b5_table, fmt_unit, get_engine, scalar, task_names, tiers


def _h(df) -> int:
    """依列數設定表高，避免表內捲動。"""
    return 38 + 35 * len(df)


def render():
    eng = get_engine()
    st.title("Block 5 — 任務層：token、成功率與每成功任務成本")
    st.caption("只讀 Interface E 節與 IF_HdrTask。每一個依層級的欄都標明層級（Luna／Sol／Astra）；每次嘗試的 token 依類型分列"
               "（新鮮輸入、快取輸入、decode）。資料只來自 Excel 的具名範圍。")

    tier_map = tiers(eng)
    tier = st.radio("層級", list(tier_map), format_func=lambda t: tier_map[t], horizontal=True, key="b5_tier")
    tasks = task_names(eng)

    w, prof = scalar(eng, "IF_HarW"), scalar(eng, "IF_HarProfile")
    c1, c2 = st.columns(2)
    c1.metric(f"{w['label']}（{w['unit']}）", fmt_unit(w["value"], w["unit"]))
    c2.markdown(f"**{prof['label']}**\n\n{prof['value']}")
    st.info("基準 w＝0，現行＝標準 harness；選定檔案為情境（欄名含「選定檔案」者）。"
            "每 GW 理論營收不受 harness 影響（L4），Block 4 的營收表不隨本頁的 harness 設定改變。")

    st.divider()
    st.subheader(f"任務表｜{tier_map[tier]}")
    tbl = b5_table(eng, tier)
    st.table(tbl.T)                                                  # 小表（5 任務欄）：表頭與標籤自動換行，1280 px 下不需橫向捲動
    st.caption("欄＝任務（取自 IF_HdrTask）；列＝每次嘗試 token（新鮮輸入、快取輸入、decode）、成功率（現行、選定檔案）、"
               "每成功任務成本（VR200、GB300；經濟、基準成本、基準利用率）、每成功任務營收（OpenAI 有效單價）與 R（選定 ÷ 標準，VR200）。")

    st.divider()
    task = st.selectbox("任務（推導鏈）", tasks, key="b5_task")
    st.subheader(f"推導鏈｜{tier_map[tier]}｜{task}")
    st.caption("依序：任務長度 → 時間範圍（有效值；層級基準列為對照）→ 成功率 → 每次嘗試（token）→ 每次嘗試成本（$）→ ÷ p → 每成功任務成本 → 每成功任務營收。"
               "每一步都是 Excel 既有具名範圍的值（IF_、B5_），本頁不自行計算；成功率為百分比。")
    chain = b5_chain(eng, tier, list(tier_map), task)
    chain["值"] = [fmt_unit(v, u) for v, u in zip(chain["值"], chain["單位"])]
    chain = chain[["步驟", "層級", "token 類型", "值", "單位", "項目（Excel 標籤）"]]      # 值與單位靠前，避免被長標籤擠出畫面
    st.dataframe(chain, use_container_width=True, hide_index=True, height=_h(chain))

    st.divider()
    pf = scalar(eng, "IF_PFloor")
    st.subheader("成功任務成本前緣（VR200）")
    st.metric(f"{pf['label']}（{pf['unit']}）", fmt_unit(pf["value"], pf["unit"]))
    front = b5_front(eng)
    st.table(front)                                                  # 小表：自動換行、不橫向捲動，Coding agent 欄不被截斷
    st.caption("只比較 p ≥ p_min 的層級 × 檔案組合；p_min 為 Excel 輸入（B5_PFloor）。欄＝任務；列＝最低每成功任務成本、組合（層級｜檔案）、組合成功率；"
               "『無合格』＝無組合達下限。本頁只顯示 Excel 的前緣（IF_FrontSuccVR*），不在網站重算。")

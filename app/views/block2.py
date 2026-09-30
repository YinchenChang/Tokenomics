"""Block 2：依層級的產出、VR-eq、$/M、tokens/焦耳（只讀 Interface 具名範圍）＋ Calib 驗證表。"""
import streamlit as st

from app.common import (block2_table, calib_platform_note, calib_validation, cost_cases, fmt, get_engine,
                        interface_series, tiers)


def render():
    eng = get_engine()
    st.title("Block 2 — 依層級的產出與成本")
    st.caption("每一列都帶層級（Luna／Sol／Astra）；100%＝理想上限，下游以自身利用率換算。資料只來自 Interface 的具名範圍。")

    tier_map = tiers(eng)
    c1, c2 = st.columns(2)
    tier = c1.radio("層級", list(tier_map), format_func=lambda t: tier_map[t], horizontal=True)
    case = c2.radio("成本情境", cost_cases(eng), index=1, horizontal=True)

    df = block2_table(eng, tier, case)
    st.subheader(f"{tier_map[tier]}｜成本情境：{case}")
    st.dataframe(df.map(fmt), use_container_width=True)
    st.caption("物理量（每架 tok/s、每 GW 產出、VR-eq、tokens/焦耳）不隨成本情境改變；\\$/M 隨成本情境改變。"
               "decode \\$/M 在 Excel 未分列「思考」與「可見輸出」，此處不自行拆分。")

    metric = st.selectbox("圖：跨世代比較", list(df.index))
    chart = df.loc[metric].astype(float).rename_axis("世代").reset_index(name="值")   # 固定欄名，避免標籤內的冒號被 Altair 解析
    st.bar_chart(chart, x="世代", y="值", sort=False)
    st.caption(metric.replace("$", "\\$"))

    util = interface_series(eng, "IF_Util")
    st.caption(f"{util['label']}：{fmt(util['values'][0])}（{util['unit']}）")

    st.divider()
    st.subheader("Calib 驗證結果（唯讀）")
    st.caption("F 節：模型 ÷ 實測（InferenceX）；H 節：模型 ÷ MLPerf。兩節的實測口徑不同（總 token／輸出 token），見「口徑」欄。")
    st.warning("InferenceX 為單一平台來源（七個點全部來自同一平台）；MLPerf 由 NVIDIA 提交（利害關係方）。")
    cal = calib_validation(eng)
    show = cal.copy()
    for c in ("每用戶速度 tok/s", "實測 tok/s/GPU", "模型 tok/s/GPU", "模型 ÷ 實測"):
        show[c] = show[c].map(fmt)
    st.dataframe(show, use_container_width=True, hide_index=True)
    note = calib_platform_note(eng)
    if note:
        st.caption(f"Excel 註記：{note}")

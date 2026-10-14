"""Block 2：依層級的產出、VR-eq、$/M、tokens/焦耳（只讀 Interface 具名範圍）＋ 推導鏈（DRV_）＋ Calib 驗證表（CAL_）。"""
import streamlit as st

from app.common import (basis_note, block2_table, calib_scalars, calib_validation, cost_cases, drv_table, fmt, fmt_unit,
                        get_engine, interface_series, tiers)


def _h(df) -> int:
    """依列數設定表高，避免表內捲動。"""
    return 38 + 35 * len(df)


def render():
    eng = get_engine()
    st.title("Block 2 — 依層級的產出與成本")
    st.caption("每一列都帶層級（Luna／Sol／Astra）；100%＝理想上限，下游以自身利用率換算。資料只來自 Excel 的具名範圍。")

    tier_map = tiers(eng)
    c1, c2 = st.columns(2)
    tier = c1.radio("層級", list(tier_map), format_func=lambda t: tier_map[t], horizontal=True)
    case = c2.radio("成本情境", cost_cases(eng), index=1, horizontal=True)

    df = block2_table(eng, tier, case)
    st.subheader(f"{tier_map[tier]}｜成本情境：{case}")
    st.dataframe(df.map(fmt), use_container_width=True, height=_h(df))
    st.caption("物理量（每架 tok/s、每 GW 產出、VR-eq、tokens/焦耳）不隨成本情境改變；\\$/M 隨成本情境改變。")

    metric = st.selectbox("圖：跨世代比較", list(df.index))
    chart = df.loc[metric].astype(float).rename_axis("世代").reset_index(name="值")   # 固定欄名，避免標籤內的冒號被 Altair 解析
    st.bar_chart(chart, x="世代", y="值", sort=False)
    st.caption(metric.replace("$", "\\$"))

    util = interface_series(eng, "IF_Util")
    st.caption(f"{util['label']}：{fmt_unit(util['values'][0], util['unit'])}")

    st.divider()
    st.subheader(f"推導鏈｜{tier_map[tier]}")
    st.caption("由上而下：每 token FLOPs → 每 GPU 權重 → 每步固定延遲 → 每序列每步時間與綁定項 → 批次與綁定約束 → "
               "decode／prefill 每 GPU 產出 → prefill 占比 → 每架、每 GW 產出 → decode $/M → 能量閉合比。"
               "欄＝世代；本區僅供顯示，下游模型不得連結 DRV_ 名稱。")
    drv = drv_table(eng, tier, case)
    st.dataframe(drv, use_container_width=True, height=_h(drv))
    st.caption(f"decode \\$/M 列讀 Interface 的 IF_CostDec，跟隨上方成本情境選擇器（目前：{case}）；其餘為不隨成本情境改變的物理量。")

    st.divider()
    st.subheader("Calib 驗證結果（唯讀）")
    st.warning("InferenceX 為單一平台來源；MLPerf 由 NVIDIA 提交（利害關係方）。"
               "F 與 H 兩節的口徑不同，比值不可並列比較。")
    for sec, title in (("F", "F 節：模型 ÷ 實測（InferenceX）"), ("H", "H 節：模型 ÷ MLPerf")):
        df, meta = calib_validation(eng, sec)
        st.markdown(f"**{title}**　口徑：{basis_note(df)}")
        show = df.copy()
        for col in ("每用戶速度", "實測", "模型", "比值"):
            show[col] = show[col].map(fmt)
        st.dataframe(show, use_container_width=True, hide_index=True, height=_h(show))
        notes = [f"{k}＝{v[0]}" + (f"（{v[1]}）" if v[1] not in (None, "") else "")
                 for k, v in meta.items() if k in ("每用戶速度", "實測", "模型", "比值") and v[0] != k]   # 只列與欄名不同的 Excel 標籤
        if notes:
            st.caption("；".join(notes))
    cols = st.columns(2)
    for col, (label, value) in zip(cols, calib_scalars(eng)):
        col.metric(label, value)

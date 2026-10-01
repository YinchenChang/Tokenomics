"""Block 4 — 單價、理論營收（理想上限）、成本與攤提。資料只來自 Excel 的具名範圍（IF_、B4_）。"""
import streamlit as st

from app.common import (b4_chain, cost_cases, cost_table, fmt, generations, get_engine,
                        market_table, price_table, rev_table, tiers)


def _h(df) -> int:
    """依列數設定表高，避免表內捲動。"""
    return 38 + 35 * len(df)


def _fmt_df(df):
    return df.map(fmt)


def render():
    eng = get_engine()
    st.title("Block 4 — 單價、理論營收（理想上限）與成本攤提")
    st.caption("每一列都標明層級（Luna／Sol／Astra）與 token 類型；單價為單一價格快照、不隨世代與成本情境改變，"
               "營收隨世代改變（只由產能、利用率與單價決定，不隨成本情境）；成本與攤提隨世代與成本情境改變。B4_ 名稱屬顯示或內部用，下游模型只可連結 IF_ 名稱。資料只來自 Excel 的具名範圍。")

    tier_map = tiers(eng)
    gens = generations(eng)
    c1, c2, c3 = st.columns(3)
    tier = c1.radio("層級", list(tier_map), format_func=lambda t: tier_map[t], horizontal=True, key="b4_tier")
    gen = c2.selectbox("世代", gens, key="b4_gen")
    case = c3.radio("成本情境", cost_cases(eng), index=1, horizontal=True, key="b4_case")

    st.divider()
    st.subheader("單價表（依層級）")
    st.dataframe(price_table(eng, tier_map), use_container_width=True, height=_h(tier_map))
    st.caption("列＝層級；欄＝token 類型。「OpenAI 有效」＝牌價 ×（1−折扣）× 能力單價倍數；「前緣混合」與「前緣模型」為候選表中"
               "能力不低於該層級 OpenAI 模型者的最低請求混合單價。思考 token 依輸出價計費。")

    st.divider()
    st.subheader("市場候選表")
    mkt = market_table(eng)
    st.dataframe(mkt, use_container_width=True, hide_index=True, height=_h(mkt))
    st.caption("標記＝「中國廠商」者為中國廠商列（國別欄取自 Excel）。能力指數空白者不參與前緣；"
               "Artificial Analysis 的指數跨版本不可比（各列的指數版本以 Excel 為準）。價格為國際站美元牌價、非折扣後。")

    st.divider()
    st.subheader(f"每 GW 理論營收（理想上限）｜{tier_map[tier]}｜成本情境：{case}")
    rev = rev_table(eng, tier, case, list(tier_map))
    st.dataframe(_fmt_df(rev), use_container_width=True, height=_h(rev))
    st.caption("理想上限＝SLO 產能 × 利用率 × 有效單價，未計需求不足、價格競爭與未售出產能。"
               "機隊列為 1 GW 參考機隊：先列 Luna、Sol、Astra 三層級的貢獻，再列合計；合計是依付費 token 組合加權的層級組合，不是單一層級。")
    chart = rev.T.rename_axis("世代").reset_index().melt("世代", var_name="項目", value_name="營收")
    st.bar_chart(chart, x="世代", y="營收", color="項目", x_label="世代", y_label="營收（單位見上表）", sort=False, stack=False)

    st.divider()
    st.subheader(f"成本與攤提｜{tier_map[tier]}｜成本情境：{case}")
    cost = cost_table(eng, tier, case)
    st.dataframe(_fmt_df(cost), use_container_width=True, height=_h(cost))
    st.info("K6 下游預設為 (c)：由上而下總額 × 自下而上權重（`IF_AmortDefault_*`、`IF_FullCostDefault_*`，下游連結此兩者）。"
            "自下而上、由上而下、(d)（由上而下總額 × 營收權重）與以自下而上攤提計的全成本，列為對照；對照列不是下游預設。")
    st.markdown("**攤提 $/M 對照（跨世代）**")
    amort_rows = [i for i in cost.index if any(k in i for k in ("攤提",))]
    chart = cost.loc[amort_rows].T.rename_axis("世代").reset_index().melt("世代", var_name="口徑", value_name="攤提")
    st.bar_chart(chart, x="世代", y="攤提", color="口徑", x_label="世代", y_label="攤提（$/M）", sort=False, stack=False)

    st.divider()
    st.subheader(f"推導鏈｜{tier_map[tier]}｜{gen}｜成本情境：{case}")
    st.caption("依序：每 GW 產出 → 利用率 → 有效單價 → 理論營收 → 服務成本 → 快取儲存 → 攤提 → 全成本。"
               "每一步都是 Excel 既有具名範圍的值（IF_），此處不新增計算。")
    chain = b4_chain(eng, tier, gen, case)
    chain["值"] = chain["值"].map(fmt)
    st.dataframe(chain, use_container_width=True, hide_index=True, height=_h(chain))

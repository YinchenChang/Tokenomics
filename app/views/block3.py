"""Block 3 — 訓練：依層級與世代的 GPU 小時、成本、後訓練占比與研發計畫。資料只來自 Excel 的具名範圍。"""
import streamlit as st

from app.common import (DEFAULT_GEN_KEYS, block3_table, cost_cases, fmt, fmt_unit, get_engine, interface_series,
                        post_share_table, registry_tables, tier_titles_trn, trn_table)


def _h(df) -> int:
    """依列數設定表高，避免表內捲動。"""
    return 38 + 35 * len(df)


def render():
    eng = get_engine()
    st.title("Block 3 — 依層級的訓練 GPU 小時、成本與研發計畫")
    st.caption("每一列都帶層級（Luna／Sol／Astra）；GPU 小時不隨成本情境改變，\\$ 隨成本情境改變。"
               f"下游預設訓練世代為 {'、'.join(DEFAULT_GEN_KEYS)} 並列（J13），已排在各表最前面。資料只來自 Excel 的具名範圍。")

    tier_map = tier_titles_trn(eng)
    c1, c2 = st.columns(2)
    tier = c1.radio("層級", list(tier_map), format_func=lambda t: tier_map[t], horizontal=True, key="b3_tier")
    case = c2.radio("成本情境", cost_cases(eng), index=1, horizontal=True, key="b3_case")

    st.subheader(f"{tier_map[tier]}｜成本情境：{case}")
    out = block3_table(eng, tier, case)
    st.dataframe(out, use_container_width=True, height=_h(out))
    rd = interface_series(eng, "IF_RDMult")
    st.caption(f"{rd['label']}：{fmt_unit(rd['values'][0], rd['unit'])}（研發計畫 GPU 小時＝最終訓練 GPU 小時 × 研發倍數）。")

    st.divider()
    st.subheader(f"後訓練占比（兩種口徑）與 RL 有效 MFU｜{tier_map[tier]}")
    share = post_share_table(eng, tier)
    shown = share.copy().astype(object)
    for label in shown.index:
        shown.loc[label] = [f"{v:.4g}%" for v in share.loc[label]]
    st.dataframe(shown, use_container_width=True, height=_h(shown))
    st.caption("FLOPs 口徑＝後訓練計算量 ÷ 最終訓練計算量；GPU 小時口徑＝後訓練 GPU 小時 ÷ 最終訓練 GPU 小時。"
               "兩者的差距來自後訓練（尤其 RL）的有效 MFU 遠低於預訓練：同樣的 FLOPs 要用更多 GPU 小時。"
               "兩種口徑不可互換使用；外部以支出或 GPU 小時為口徑的比較，應對照 GPU 小時口徑。")
    chart = share.iloc[:2].T.rename_axis("世代").reset_index()
    chart.columns = ["世代", "FLOPs 口徑", "GPU 小時口徑"]                 # 固定欄名，避免標籤內的括號被 Altair 解析
    st.bar_chart(chart.melt("世代", var_name="口徑", value_name="占比（%）"), x="世代", y="占比（%）", color="口徑",
                 x_label="世代", sort=False, stack=False)

    st.divider()
    st.subheader(f"推導鏈｜{tier_map[tier]}")
    st.caption("由上而下依 Excel Training 頁列序：訓練 FLOPs/token → 預訓練 FLOPs 與 GPU 小時 → RL（有效 MFU、與預訓練之比）→ "
               "最終訓練 → 後訓練占比 → 研發計畫。欄＝世代，表頭取自 TRN_Gen／TRN_Tier；本區僅供顯示，下游模型不得連結 TRN_ 名稱。")
    trn = trn_table(eng, tier)
    st.dataframe(trn, use_container_width=True, height=_h(trn))

    st.divider()
    st.subheader("Tech_Registry（唯讀）")
    st.info("技術開關、採用比例與倍數只能在 Excel（Project 端）修改並升版；本網站不提供開關。"
            "有效倍數＝1＋開關 × 採用比例 ×（所選倍數−1）；已在基準者恆為 1。")
    reg, hook = registry_tables(eng)
    st.dataframe(reg.map(fmt), use_container_width=True, hide_index=True, height=_h(reg))
    st.markdown("**掛鉤彙總**（同一掛鉤多條目時取乘積；Perf、Perf_Batch、Training 連結此表）")
    st.dataframe(hook.map(fmt), use_container_width=True, hide_index=True, height=_h(hook))

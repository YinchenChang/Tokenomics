"""問答（v5.15）：第 1 層 L1 的 L1_Ans1–9（題目、答案、區間、讀法、缺口）。資料只來自 L1_ 具名範圍所在列。"""
import streamlit as st

from app.common import get_engine, l1_table


def answers(eng):
    df = l1_table(eng)
    df = df[df["L1_ID"].astype(str).str.startswith("L1_Ans")].reset_index(drop=True)
    def key(i):                                   # 子項（L1_Ans5_GM 等）緊接在所屬題目之後
        n, _, sub = str(i)[len("L1_Ans"):].partition("_")
        return (int(n), sub != "", sub)
    return df.iloc[sorted(range(len(df)), key=lambda k: key(df["L1_ID"].iloc[k]))].reset_index(drop=True)


def render():
    eng = get_engine()
    st.title("問答 — Block 6 九題（L1_Ans1–9；含毛利率與 GPU 小時口徑子項）")
    st.caption("答案、區間、讀法與缺口全部來自 Excel 的 L1 頁；本頁唯讀。")
    df = answers(eng)
    for _, r in df.iterrows():
        st.subheader(str(r["指標或問題"]))
        c = st.columns(3)
        c[0].metric("答案（基準值）", str(r["基準值"]), help=str(r["單位"]))
        c[1].metric("低", str(r["低"]))
        c[2].metric("高", str(r["高"]))
        st.write(f"單位：{r['單位']}　條件：{r['條件']}")
        st.write(f"區間的定義：{r['區間的定義']}")
        st.write(f"讀法：{r['讀法']}")
        st.write(f"最弱輸入：{r['最弱輸入的標記']}　所在頁與列：{r['所在頁與列']}")
        st.write(f"未能回答的部分（缺口）：{r['未能回答的部分']}")

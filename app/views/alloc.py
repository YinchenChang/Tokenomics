"""Alloc（v5.15，Block 6）：研發與服務的算力配置。依 CLAUDE.md 第 1a 節逐列顯示推導鏈：需求 D → 服務 GW → 研發 GW → Q1、Q2。
資料只來自 Excel 的 AL_ 具名範圍（僅供顯示）；標籤與單位取自名稱所在列的欄 A、欄 B；不在此計算任何數值。"""
import pandas as pd
import streamlit as st

from app.common import fmt_unit, get_engine, series

CHAIN = (
    ("A. 需求 D（M tok/年；token 路線，A9）", ("AL_DAPI", "AL_DChat", "AL_DChatFree", "AL_DChatPaid", "AL_DPaid", "AL_DFree", "AL_D", "AL_DDaily")),
    ("B. 服務 GW（世代組合 GB200／GB300／VR200）", ("AL_ShareGen", "AL_GenOK", "AL_CapPaid", "AL_CapFree", "AL_BlendPaid", "AL_BlendFree",
                                              "AL_ServeGWPaid", "AL_ServeGWFree", "AL_ServeGW", "AL_ServeGen", "AL_HoldGen")),
    ("C. 研發 GW 年（物理下限）", ("AL_FamGWyr", "AL_RefGWyr", "AL_RDGW", "AL_RDGWg", "AL_HoldTrain", "AL_RDCost")),
    ("D. Q1、Q2", ("AL_Q1", "AL_Q1R2", "AL_Q2", "AL_Q1g", "AL_Q2g")),
    ("E. 校準反推（A3）", ("AL_SpendRatio", "AL_ImpliedRDGW", "AL_ImpliedNk", "AL_J8Gap")),
    ("F. 外部對照", ("AL_ServeGWSpend", "AL_FreeServeShare", "AL_FreeSpendShare")),
)


def chain_table(eng) -> pd.DataFrame:
    rows = []
    for sec, names in CHAIN:
        for n in names:
            s = series(eng, n)
            unit = s["unit"] if s["unit"] not in (None, "") else ""
            rows.append((sec, s["label"], unit, " ｜ ".join(fmt_unit(v, unit) for v in s["values"])))
    return pd.DataFrame(rows, columns=["節", "項目（Excel 標籤）", "單位", "值（多格為 C–E 欄：世代或層級）"])


def render():
    eng = get_engine()
    st.title("Alloc — 研發與服務的算力配置（Block 6）")
    st.caption("需求 D → 服務 GW → 研發 GW → Q1、Q2；基準為 2025 穩態年度。輸入在 Excel 的 Alloc_In（Project 端修改），本頁唯讀。SLO 不可達時顯示文字。")
    df = chain_table(eng)
    for sec in dict.fromkeys(df["節"]):
        st.subheader(sec)
        st.table(df[df["節"] == sec].drop(columns="節").reset_index(drop=True).astype(str))

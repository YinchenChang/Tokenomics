"""網站煙霧測試：各頁可渲染、無例外，且 Block 2 表格與選擇器運作。"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HEAD = f"import sys; sys.path.insert(0, {str(ROOT)!r})\n"


def test_overview():
    at = AppTest.from_string(HEAD + "from app.views import overview; overview.render()", default_timeout=180).run()
    assert not at.exception
    assert len(at.dataframe) == 1
    idx = " ".join(map(str, at.dataframe[0].value.index))
    assert "訓練" not in idx and "研發" not in idx      # Block 3 列不混入 Block 1 表


def test_block2_selectors_and_calib_table():
    at = AppTest.from_string(HEAD + "from app.views import block2; block2.render()", default_timeout=180).run()
    assert not at.exception
    for tier in ("Luna", "Sol", "Astra"):
        at.radio[0].set_value(tier).run()
        for case in ("低成本", "基準", "高成本"):
            at.radio[1].set_value(case).run()
            assert not at.exception
            assert all(str(i).startswith(tier) for i in at.dataframe[0].value.index)
    drv = at.dataframe[1].value
    assert len(drv) == 15 and drv.shape[1] == 5          # 15 個推導鏈量 × 5 世代
    f, h = at.dataframe[2].value, at.dataframe[3].value
    assert len(f) == 7 and len(h) == 4                    # F 節 7 點、H 節 4 點，分兩張表
    for tbl in (f, h):
        assert (tbl["量測平台"].astype(str).str.len() > 0).all() and (tbl["口徑"].astype(str).str.len() > 0).all()
        for col in ("點位", "世代", "每用戶速度", "實測", "模型", "比值"):
            assert col in tbl.columns
    assert "軟體／日期" in f.columns and "軟體／日期" not in h.columns


def test_drv_cost_row_follows_case_selector():
    """推導鏈的 decode $/M 列跟隨成本情境（讀 IF_CostDec），且與上方主表同列數值一致。"""
    at = AppTest.from_string(HEAD + "from app.views import block2; block2.render()", default_timeout=180).run()
    at.radio[0].set_value("Sol").run()
    seen = {}
    for case in ("低成本", "基準", "高成本"):
        at.radio[1].set_value(case).run()
        assert not at.exception
        main, drv = at.dataframe[0].value, at.dataframe[1].value
        drv_cost = drv[drv.index.str.contains(f"｜{case}")]
        assert len(drv_cost) == 1
        main_cost = main[main.index.str.contains("decode") & main.index.str.contains("經濟")].iloc[0]
        assert list(drv_cost.iloc[0]) == list(main_cost), (case, list(drv_cost.iloc[0]), list(main_cost))
        seen[case] = tuple(drv_cost.iloc[0])
    assert len(set(seen.values())) == 3                  # 三個成本情境的值各不相同


B3 = "from app.views import block3; block3.render()"


def test_block3_tables_selectors_and_registry_readonly():
    at = AppTest.from_string(HEAD + B3, default_timeout=180).run()
    assert not at.exception
    assert len(at.radio) == 2 and not at.toggle and not at.checkbox     # 只有層級、成本情境選擇器；沒有 Tech_Registry 開關
    for tier in ("Luna", "Sol", "Astra"):
        at.radio[0].set_value(tier).run()
        for case in ("低成本", "基準", "高成本"):
            at.radio[1].set_value(case).run()
            assert not at.exception
            out = at.dataframe[0].value
            assert len(out) == 8 and all(str(i).startswith(tier) for i in out.index)
            assert ["VR200" in out.columns[0], "GB300" in out.columns[1]] == [True, True]   # J13：IF_TrainGenDefault、IF_TrainGenAlt 在最前
            assert out.shape[1] == 5
    share, trn, reg, hook = (at.dataframe[i].value for i in (1, 2, 3, 4))
    assert share.shape == (3, 5) and any("FLOPs 口徑" in i for i in share.index) and any("GPU 小時口徑" in i for i in share.index)
    assert any("RL 有效 MFU" in i for i in share.index)
    assert trn.shape == (13, 5)                                            # TRN_ 13 個量（不含表頭 2 個）× 5 世代
    assert len(reg) == 12 and reg.shape[1] == 20 and {"ID", "開關（0／1）", "有效倍數", "證據標記"} <= set(reg.columns)   # 讀 TR_*，欄名取自 Excel 表頭
    assert len(hook) == 11 and hook.shape[1] == 3 and "倍數" in hook.columns


def test_block3_cost_follows_case_and_shares_match_chain():
    """GPU 小時不隨成本情境變、成本隨情境變；後訓練占比表（IF_）與推導鏈（TRN_）同列數值一致。"""
    at = AppTest.from_string(HEAD + B3, default_timeout=180).run()
    at.radio[0].set_value("Astra").run()
    seen = {}
    for case in ("低成本", "基準", "高成本"):
        at.radio[1].set_value(case).run()
        out = at.dataframe[0].value
        gpuh = [r for r in out.index if "最終訓練 GPU 小時" in r][0]
        cost = [r for r in out.index if "最終訓練成本" in r][0]
        seen[case] = (tuple(out.loc[gpuh]), tuple(out.loc[cost]))
    assert len({v[0] for v in seen.values()}) == 1 and len({v[1] for v in seen.values()}) == 3
    share, trn = at.dataframe[1].value, at.dataframe[2].value
    for key in ("FLOPs 口徑", "GPU 小時口徑"):
        a = share.loc[[i for i in share.index if f"後訓練占比（{key}" in i]].iloc[0]
        b = trn.loc[[i for i in trn.index if f"後訓練占比（{key}" in i]].iloc[0]
        assert list(a) == list(b), (key, list(a), list(b))


B4 = "from app.views import block4; block4.render()"


def test_block4_tables_selectors_and_k6_both_bases():
    """Block 4：價格表 3 列 × 7 欄；市場表 13 列且中國廠商（B4_MktChina）有標記；營收標題含「理想上限」；K6 下游預設 (c) 與三種對照並列；推導鏈 8 步。"""
    at = AppTest.from_string(HEAD + B4, default_timeout=180).run()
    assert not at.exception
    assert len(at.radio) == 2 and len(at.selectbox) == 1 and not at.toggle and not at.checkbox   # 層級、成本情境、世代
    price, mkt = at.dataframe[0].value, at.dataframe[1].value
    assert price.shape == (3, 7) and any("前緣模型" in c for c in price.columns)
    assert any("新鮮輸入" in c for c in price.columns) and any("快取輸入" in c for c in price.columns)
    assert any("思考" in c for c in price.columns) and any("可見輸出" in c for c in price.columns)
    assert len(mkt) == 13 and mkt.shape[1] == 10 and {"模型", "廠商", "國別", "開放權重", "能力指數", "標記"} <= set(mkt.columns)
    assert set(mkt.loc[mkt["國別"] == "中國", "標記"]) == {"中國廠商"} and set(mkt.loc[mkt["國別"] != "中國", "標記"]) == {""}
    assert "CN_COUNTRY" not in (ROOT / "app" / "common.py").read_text(encoding="utf-8")                 # v5.9：旗標改讀 B4_MktChina，不再比對國別字串
    assert any("理想上限" in sub.value for sub in at.subheader)
    for tier in ("Luna", "Sol", "Astra"):
        at.radio[0].set_value(tier).run()
        for case in ("低成本", "基準", "高成本"):
            at.radio[1].set_value(case).run()
            assert not at.exception
            rev, cost, chain = at.dataframe[2].value, at.dataframe[3].value, at.dataframe[4].value
            assert len(rev) == 10 and rev.shape[1] == 5 and sum(str(i).startswith(tier) for i in rev.index) == 2   # 2 列層級＋機隊（3 層級貢獻＋合計）× 2 種單價
            assert sum("合計" in str(i) and "層級組合" in str(i) for i in rev.index) == 2                      # 合計列標「層級組合」
            assert len(cost) == 7 and all(str(i).startswith(tier) for i in cost.index)
            assert any("自下而上" in i for i in cost.index) and any("由上而下" in i for i in cost.index)
            assert any("K6 預設 (c)" in i and "【對照】" not in i for i in cost.index) and any("(d)" in i and "【對照】" in i for i in cost.index)
            assert chain["層級"].eq(tier).all() and chain["步驟"].str[0].tolist() == sorted(chain["步驟"].str[0].tolist())
            assert set(chain["步驟"].str[0]) == set("12345678")
    assert any("K6 下游預設為 (c)" in w.value for w in at.info)           # v5.9：顯示下游預設 (c)，其餘為對照
    assert not any("待 Andy 決定" in str(e.value) for e in list(at.info) + list(at.warning) + list(at.caption) + list(at.markdown))


def test_block4_matches_interface_and_follows_case():
    """表內數值即 IF_ 具名範圍的值；成本情境變動時全成本變動，營收（只由產能、利用率、單價決定）與單價不變。"""
    from app.common import get_engine, interface_series
    at = AppTest.from_string(HEAD + B4, default_timeout=180).run()
    at.radio[0].set_value("Astra").run()
    eng = get_engine()
    gens = list(dict.fromkeys(eng.get_name("IF_HdrGen")))
    seen = {}
    for case in ("低成本", "基準", "高成本"):
        at.radio[1].set_value(case).run()
        rev, price, cost = at.dataframe[2].value, at.dataframe[0].value, at.dataframe[3].value
        s = interface_series(eng, "IF_RevGW_Astra")
        want = {g: v for g, c, v in zip(s["gens"], s["cases"], s["values"]) if c == case}
        row = rev.loc[[i for i in rev.index if "OpenAI 有效單價" in i and i.startswith("Astra")][0]]
        assert [float(x) for x in row.map(str).str.replace(",", "")] == [float(f"{want[g]:,.0f}".replace(",", "")) if abs(want[g]) >= 1000 else float(f"{want[g]:.4g}") for g in gens]
        full = cost.loc[[i for i in cost.index if "全成本" in i][0]]
        seen[case] = (tuple(row), tuple(map(tuple, price.values.tolist())), tuple(full))
    assert len({v[0] for v in seen.values()}) == 1 and len({v[1] for v in seen.values()}) == 1   # 營收、單價不隨成本情境
    assert len({v[2] for v in seen.values()}) == 3                                                 # 全成本隨成本情境


B5 = "from app.views import block5; block5.render()"


def test_block5_tables_chain_and_overview_exclusion():
    """Block 5：任務表（依層級欄前綴層級）、推導鏈 8 步、說明文字；總覽排除 Block 5 名稱。"""
    from app.common import get_engine
    at = AppTest.from_string(HEAD + B5, default_timeout=180).run()
    assert not at.exception and len(at.radio) == 1 and len(at.selectbox) == 1 and not at.toggle and not at.checkbox   # 層級、任務
    eng = get_engine()
    tasks = [str(x) for x in eng.get_name("IF_HdrTask")]
    for tier in ("Luna", "Sol", "Astra"):
        at.radio[0].set_value(tier).run()
        assert not at.exception
        tbl = at.table[0].value                                        # 列＝指標、欄＝任務（第 10 輪起為 st.table，1280 px 無橫向捲動）
        assert list(tbl.columns) == tasks and len(tbl) == 12
        tier_rows = [i for i in tbl.index if str(i).startswith(f"{tier}｜")]
        assert len(tier_rows) == 6 and all(any(k in i for k in ("成功率", "每成功任務成本", "每成功任務營收", "R＝")) for i in tier_rows)
        assert any("新鮮輸入" in i for i in tbl.index) and any("快取輸入" in i for i in tbl.index) and any("decode" in i for i in tbl.index)
        assert any("VR200" in i for i in tier_rows) and any("GB300" in i for i in tier_rows)
        for t in tasks:
            at.selectbox[0].set_value(t).run()
            chain = at.dataframe[0].value
            assert not at.exception and chain["層級"].eq(tier).all() and set(chain["步驟"].str[0]) == set("12345678")
    texts = " ".join(str(e.value) for e in list(at.info) + list(at.caption) + list(at.markdown))
    assert "基準 w＝0" in texts and "L4" in texts and "選定檔案為情境" in texts
    ov = AppTest.from_string(HEAD + "from app.views import overview; overview.render()", default_timeout=180).run()
    idx = " ".join(map(str, ov.dataframe[0].value.index))
    assert not ov.exception and "成功率" not in idx and "每成功任務" not in idx and "harness" not in idx


def test_block5_values_equal_interface():
    """任務表的值即 IF_ 具名範圍（列順序與 IF_HdrTask 一致）。"""
    from app.common import fmt_unit, get_engine, series
    at = AppTest.from_string(HEAD + B5, default_timeout=180).run()
    at.radio[0].set_value("Sol").run()
    eng = get_engine()
    s = series(eng, "IF_CostSuccVR_Sol")
    tbl = at.table[0].value
    row = tbl.loc[[i for i in tbl.index if i.startswith("Sol｜") and "VR200" in i][0]]
    assert list(row) == [fmt_unit(v, s["unit"]) for v in s["values"]]


def test_overview_excludes_block4_names():
    at = AppTest.from_string(HEAD + "from app.views import overview; overview.render()", default_timeout=180).run()
    assert not at.exception
    idx = " ".join(map(str, at.dataframe[0].value.index))
    assert "理想上限" not in idx and "攤提" not in idx and "快取儲存" not in idx


def test_evidence_page_readonly_table():
    at = AppTest.from_string(HEAD + "from app.views import evidence; evidence.render()", default_timeout=180).run()
    assert not at.exception
    df = at.dataframe[0].value
    assert df.shape == (89, 11) and {"ID", "主張（摘要）", "標記", "判定", "處理版本"} <= set(df.columns)
    assert df["ID"].tolist()[:2] == ["E001", "E002"] and df["ID"].is_unique
    at.multiselect[0].set_value([df["判定"].iloc[0]]).run()                # 篩選可用且不拋例外
    assert not at.exception and 0 < len(at.dataframe[0].value) <= 89


def test_no_label_lookup_in_app_and_engine():
    """網站與引擎不再以欄 A 標籤定位（改讀 IF_Hdr／DRV_／CAL_ 具名範圍）。"""
    for path in list((ROOT / "app").rglob("*.py")) + list((ROOT / "engine").rglob("*.py")):
        assert "column_labels" not in path.read_text(encoding="utf-8"), path


def test_governance_page_and_overview_status():
    """v5.11：治理頁（L1、Source、Checks G 節）可渲染；總覽顯示 GOV_ 合計且 ERROR＝0。"""
    at = AppTest.from_string(HEAD + "from app.views import governance; governance.render()", default_timeout=180).run()
    assert not at.exception
    m = {x.label: x.value for x in at.metric}
    assert m["GOV_Errors"] == "0" and set(m) == {"GOV_Errors", "GOV_Warnings", "GOV_Info"}
    assert len(at.table) == 1 and len(at.table[0].value) == 23         # Checks G 節 23 項（E13＋W2＋I8；v5.12 新增 E13）
    l1, src = at.dataframe[0].value, at.dataframe[1].value
    assert len(l1) == 47 and "L1_ID" in l1.columns                  # v5.16：44 → 47（毛利率兩列、GPU 小時口徑）；v5.15：32 → 44（Block 6：Answers 9＋外部對照 3）；v5.13：25 → 32（第 30–36 列為 Checks 移入的外部比對）
    assert len(src) == 60                                              # 預設顯示 SRC_HW 60 筆
    at.radio[0].set_value("SRC_Perf").run()
    assert not at.exception and len(at.dataframe[1].value) == 51      # v5.13：SRC_Perf 40 → 51（補登 SRC_PERF_041–051）
    assert list(at.radio[0].options) == ["SRC_HW", "SRC_DC", "SRC_Model", "SRC_Perf", "SRC_Price", "SRC_Cap", "SRC_Harness", "SRC_Demand"]
    for sheet, n in (("SRC_Price", 44), ("SRC_Cap", 21), ("SRC_Harness", 15), ("SRC_Demand", 13)):
        at.radio[0].set_value(sheet).run()
        assert not at.exception and len(at.dataframe[1].value) == n
    at = AppTest.from_string(HEAD + "from app.views import overview; overview.render()", default_timeout=180).run()
    assert not at.exception and {x.label: x.value for x in at.metric}["GOV_Errors"] == "0"
    assert len(at.dataframe) == 1                                      # Block 1 表仍只有一張 dataframe


def test_alloc_and_qa_pages():
    """v5.15：Alloc 頁逐列顯示推導鏈（6 節）；問答頁顯示 L1_Ans1–9 九題；兩頁無例外。"""
    at = AppTest.from_string(HEAD + "from app.views import alloc; alloc.render()", default_timeout=300).run()
    assert not at.exception and len(at.table) == 6
    flat = " ".join(" ".join(map(str, t.value.iloc[:, 0])) for t in at.table)
    assert "Q1（R1）" in flat and "服務 GW 合計" in flat and "研發 GW 年" in flat
    at = AppTest.from_string(HEAD + "from app.views import qa; qa.render()", default_timeout=300).run()
    assert not at.exception and len(at.subheader) == 12        # v5.16：9 題＋子項 3（Ans5_GM、Ans5_FullMargin、Ans6_GPUh）

#!/usr/bin/env python3
"""Tokenomics 靜態網站（GitHub Pages 唯讀版）建置程式。

用法：python3 site/build_site.py [--out site/dist]

- 讀 model/CURRENT 指向的活頁簿（openpyxl data_only=True：LibreOffice 重算後存下的值；app/workbook.py）。
- 取數與表格組成全部沿用 Streamlit 網站的 app/common.py 與 app/views/*（同一批函式），本程式只把結果轉成 HTML：
  表格 → 靜態表；圖 → inline SVG；選擇器（層級、成本情境、世代、任務、工作表）→ 預先產生每個組合，以小段 inline JS 切換。
- 不做任何計算（含比值）；Excel 沒有的數字，網站不顯示。頁名取自 app/nav.py（與 Streamlit 共用）。
- 每頁一個自含的 HTML 檔（CSS、JS 皆 inline，不載入任何外部資源），寫入 site/dist/。
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import re
import subprocess
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")
import streamlit.logger  # noqa: E402

streamlit.logger.set_log_level("error")      # 無 runtime 時 Streamlit 快取的提示訊息：不影響取值

import pandas as pd  # noqa: E402

from app import common as C  # noqa: E402
from app.nav import PAGES  # noqa: E402
from app.views import alloc as v_alloc  # noqa: E402
from app.views import lookup as v_lookup  # noqa: E402
from app.views import payback as v_payback  # noqa: E402
from app.views import qa as v_qa  # noqa: E402
from app.workbook import Workbook  # noqa: E402

DEFAULT_OUT = ROOT / "site" / "dist"
TZ_TPE = dt.timezone(dt.timedelta(hours=8))


def page_file(path: str) -> str:
    """第一頁（預設頁）為 index.html，其餘為 <url_path>.html。"""
    return "index.html" if path == PAGES[0][2] else f"{path}.html"


# ── 文字與表格 ──────────────────────────────────────────────────────

NUM_RE = re.compile(r"^[-+−]?(?:\d[\d,]*\.?\d*|\.\d+)(?:e[-+]?\d+)?%?$", re.I)


def e(x) -> str:
    return html.escape(str(x), quote=True)


def txt(v) -> str:
    """顯示字串：數值沿用 Streamlit 的 fmt；Excel 空白（含 NaN）回傳空字串。"""
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    if isinstance(v, (dt.datetime, dt.date)):
        if isinstance(v, dt.datetime) and (v.hour, v.minute, v.second) != (0, 0, 0):
            return v.strftime("%Y-%m-%d %H:%M")
        return v.strftime("%Y-%m-%d")
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        return C.fmt(v)
    return str(v)


def td(v, tag: str = "td", extra: str = "") -> str:
    s = txt(v)
    if s.strip() == "":
        return f'<{tag} class="blank{extra}" title="Excel 該格空白">—</{tag}>'
    cls = []
    if NUM_RE.match(s.strip()):
        cls.append("n")
    elif len(s) > 36:
        cls.append("wr")
    if extra:
        cls.append(extra.strip())
    c = f' class="{" ".join(cls)}"' if cls else ""
    return f"<{tag}{c}>{e(s).replace(chr(10), '<br>')}</{tag}>"


ANNOT_RE = re.compile(r"\s*\[IF[A-Z]?_\w+\]")


def row_head(label) -> str:
    """列首：Excel 標籤中「[IF_…]｜口徑說明」很長時，只顯示短標籤（加單位），完整文字放 title（滑鼠停留可見）。"""
    text = str(label)
    m = ANNOT_RE.search(text)
    if not m:
        return f'<th class="ix" scope="row">{e(text)}</th>'
    unit = re.search(r"（[^（）]*）$", text)
    short = text[:m.start()].rstrip() + (unit.group(0) if unit else "")
    return f'<th class="ix ab" scope="row" title="{e(text)}">{e(short)}<span class="more">…</span></th>'


def table(df: pd.DataFrame, index: bool = True, index_head: str = "", tid: str = "", row_attrs=None,
          cls: str = "", scroll: bool = False) -> str:
    """DataFrame → HTML 表。值應已是顯示字串（或數值，交給 txt）。欄可為兩層 MultiIndex。"""
    out = []
    cols = df.columns
    if isinstance(cols, pd.MultiIndex):
        lv0 = [str(c[0]) for c in cols]
        lv1 = [str(c[1]) for c in cols]
        head0 = [f'<th class="ix" rowspan="2">{e(index_head or " / ".join(str(n) for n in cols.names if n))}</th>'] if index else []
        i = 0
        while i < len(lv0):
            j = i
            while j < len(lv0) and lv0[j] == lv0[i]:
                j += 1
            head0.append(f'<th colspan="{j - i}" class="grp">{e(lv0[i])}</th>')
            i = j
        out.append("<thead><tr>" + "".join(head0) + "</tr><tr>" + "".join(f"<th>{e(x)}</th>" for x in lv1) + "</tr></thead>")
    else:
        head = ([f'<th class="ix">{e(index_head)}</th>'] if index else []) + [f"<th>{e(c)}</th>" for c in cols]
        out.append("<thead><tr>" + "".join(head) + "</tr></thead>")
    out.append("<tbody>")
    for k, (idx, row) in enumerate(df.iterrows()):
        attrs = ""
        if row_attrs:
            attrs = "".join(f' data-{a}="{e(v)}"' for a, v in row_attrs[k].items())
        cells = ([row_head(idx)] if index else []) + [td(v) for v in row.tolist()]
        out.append(f"<tr{attrs}>" + "".join(cells) + "</tr>")
    out.append("</tbody>")
    t_id = f' id="{tid}"' if tid else ""
    wrap = "tw scroll" if scroll else "tw"
    return f'<div class="{wrap}"><table{t_id} class="{cls}">' + "".join(out) + "</table></div>"


def fmt_df(df: pd.DataFrame, f=None) -> pd.DataFrame:
    f = f or txt
    return df.map(f)


def kpis(items) -> str:
    """items: [(label, value, sub)]。"""
    cells = []
    for label, value, sub in items:
        v = txt(value)
        sub_html = f'<div class="s">{e(sub)}</div>' if sub not in (None, "") else ""
        cells.append(f'<div class="kpi"><div class="k">{e(label)}</div><div class="v num">{e(v) if v else "—"}</div>{sub_html}</div>')
    return '<div class="kpis">' + "".join(cells) + "</div>"


def note(text: str, kind: str = "note") -> str:
    return f'<p class="{kind}">{e(text)}</p>'


def callout(text: str, kind: str = "info") -> str:
    return f'<div class="callout {kind}">{e(text)}</div>'


def section(title: str, *parts: str, sub: str = "") -> str:
    s = f'<p class="lede">{e(sub)}</p>' if sub else ""
    return f'<section class="sec"><h3>{e(title)}</h3>{s}' + "".join(parts) + "</section>"


def variant(body: str, **dims) -> str:
    """選擇器組合的一個版本：data-v-<維度>＝選項索引；非預設組合以 hidden 開始（無 JS 時顯示預設組合）。"""
    attrs = "".join(f' data-v-{k}="{v}"' for k, v in dims.items())
    return f'<div class="var"{attrs}>{body}</div>'


def controls(spec) -> str:
    """spec: [(dim, 標籤, [選項標題], 預設索引)] → 黏在頁頂的切換列。"""
    groups = []
    for dim, label, options, default in spec:
        btns = "".join(f'<button type="button" data-v="{i}" aria-pressed="{"true" if i == default else "false"}">{e(o)}</button>'
                       for i, o in enumerate(options))
        groups.append(f'<div class="cg"><span class="cl">{e(label)}</span><div class="seg" data-dim="{dim}" role="group" '
                      f'aria-label="{e(label)}">{btns}</div></div>')
    return '<div class="ctlbar">' + "".join(groups) + "</div>"


# ── inline SVG 長條圖 ─────────────────────────────────────────────

def _nice_step(span: float) -> float:
    raw = span / 5 if span > 0 else 1
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _axis(t: float) -> str:
    """座標軸刻度（只用於刻度文字；長條的值見 tooltip 與上方表格）：大數以科學記號縮短。"""
    t = round(t, 12)
    if t != 0 and (abs(t) >= 1e6 or abs(t) < 1e-3):
        return f"{t:.3g}"
    return C.fmt(t)


def _short(name: str) -> str:
    """圖例文字：去掉 Excel 標籤中「[IF_…]」之後的口徑說明（完整標籤見上表）。"""
    return re.split(r"\s*\[IF", name)[0] + ("…" if "[IF" in name else "")


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or (isinstance(v, float) and math.isnan(v)):
        return None
    return float(v)


def bar_chart(cats: list[str], series: list[tuple[str, list]], y_label: str = "", title: str = "", w: int = 680, h: int = 280) -> str:
    """分組長條圖（不堆疊）。series: [(名稱, 各類別值)]；非數值跳過。數值與 Excel 存值相同，標籤以 fmt 顯示。"""
    vals = [x for _, vs in series for x in (_num(v) for v in vs) if x is not None]
    if not vals:
        return ""
    lo, hi = min(0.0, min(vals)), max(0.0, max(vals))
    step = _nice_step(hi - lo)
    y0, y1 = math.floor(lo / step) * step, math.ceil(hi / step) * step
    if y1 == y0:
        y1 = y0 + step
    ml, mr, mt, mb = 70, 10, 14, 54
    pw, ph = w - ml - mr, h - mt - mb

    def y(v):
        return mt + ph * (1 - (v - y0) / (y1 - y0))

    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(title or y_label)}" class="chart" preserveAspectRatio="xMidYMid meet">']
    t = y0
    while t <= y1 + step / 2:
        yy = y(t)
        parts.append(f'<line x1="{ml}" x2="{w - mr}" y1="{yy:.1f}" y2="{yy:.1f}" class="grid"/>')
        parts.append(f'<text x="{ml - 6}" y="{yy + 4:.1f}" class="ax" text-anchor="end">{e(_axis(t))}</text>')
        t += step
    gw = pw / len(cats)
    ns = len(series)
    bw = gw * 0.78 / ns
    for ci, cat in enumerate(cats):
        gx = ml + gw * ci + gw * 0.11
        for si, (sname, vs) in enumerate(series):
            v = _num(vs[ci]) if ci < len(vs) else None
            if v is None:
                continue
            top, bot = (y(v), y(0)) if v >= 0 else (y(0), y(v))
            parts.append(f'<rect x="{gx + bw * si:.1f}" y="{top:.1f}" width="{max(bw - 1.5, 1):.1f}" height="{max(bot - top, 0.5):.1f}" '
                         f'class="b{si % 10}"><title>{e(sname)}｜{e(cat)}：{e(C.fmt(v))}</title></rect>')
        label = str(cat)
        room = max(int(gw / 6.5), 4)                               # 約每字 6.5 px：放不下時取第一個詞（例：GB200 NVL72 → GB200）
        short = label if len(label) <= room else re.split(r"[\s（(]", label)[0]
        short = short if len(short) <= room else short[:room - 1] + "…"
        parts.append(f'<text x="{ml + gw * ci + gw / 2:.1f}" y="{h - mb + 16}" class="ax" text-anchor="middle">{e(short)}<title>{e(label)}</title></text>')
    parts.append(f'<line x1="{ml}" x2="{w - mr}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="zero"/>')
    if y_label:
        parts.append(f'<text x="{ml}" y="{h - 8}" class="ax lab">{e(y_label)}</text>')
    parts.append("</svg>")
    legend = ""
    if ns > 1:
        legend = '<div class="legend">' + "".join(f'<span title="{e(n)}"><i class="k{i % 10}"></i>{e(_short(n))}</span>' for i, (n, _) in enumerate(series)) + "</div>"
    cap = f"<figcaption>{e(title)}</figcaption>" if title else ""
    return f'<figure class="fig">{cap}{"".join(parts)}{legend}</figure>'


def df_chart(df: pd.DataFrame, rows: list[str] | None = None, y_label: str = "", title: str = "", **size) -> str:
    """列＝序列、欄＝世代 的表 → 分組長條圖（值取表內原始數值）。"""
    rows = rows if rows is not None else list(df.index)
    return bar_chart([str(c) for c in df.columns], [(str(r), list(df.loc[r])) for r in rows], y_label, title, **size)


# ── 頁面 ───────────────────────────────────────────────────────────

class Ctx:
    def __init__(self, eng: Workbook):
        self.eng = eng


def page_payback(cx: Ctx):
    eng = cx.eng
    l1 = C.l1_lookup(eng)
    parts = [note(f"事實來源：{eng.path.name}（L1 頁與輸入頁；LibreOffice 重算後的值）。本頁不做任何計算；"
                  "低／高為 Excel 的區間欄。Assumed、Analogy、Derived 輸入的判讀一律讀作「在某假設下」。")]
    cards = []
    for i in v_payback.HEADLINE:
        r = l1[i]
        u = r["單位"]
        cards.append((f"{i}（{u}）", C.fmt_unit(r["基準值"], u), f"{r['指標或問題']}｜區間 {C.fmt_unit(r['低'], u)}–{C.fmt_unit(r['高'], u)}"))
    parts.append(kpis(cards))
    parts.append(callout("讀法（Andy 2026-10-22）：看「實際 ÷ 所需」的年度趨勢，不看單一年的絕對值。"
                         "上方 L（主口徑）與所需 L（主口徑）並列；兩者的比值不是 Excel 的具名範圍，本頁不另算。"))

    def details(ids):
        items = []
        for i in ids:
            if i not in l1:
                continue
            r = l1[i]
            body = "".join(f"<dt>{e(c)}</dt><dd>{e(txt(r[c])) or '—'}</dd>" for c in ("條件", "區間的定義", "讀法", "主要驅動", "最弱輸入的標記"))
            items.append(f'<details class="det"><summary><code>{e(i)}</code>｜{e(r["指標或問題"])}</summary><dl>{body}</dl></details>')
        return '<div class="dets"><p class="label">每一列的條件、區間定義與讀法（點開）</p>' + "".join(items) + "</div>"

    parts.append(section("1. 每 GW 營收 P × Q（VR200，新建 1 GW）",
                         table(v_payback._l1_table(l1, v_payback.PQ_CHAIN), index=False), details(v_payback.PQ_CHAIN),
                         sub="P＝表列牌價 ×（1 − d）× m；Q＝付費產能 × 對外服務占比 ×（1 − 免費占比）× 實際利用率 × 生產折減（L1_FleetProdRatio）。"
                             "壽命期年均列＝第一年 × L1_LTotalDisc（VR200 自身起點的折現 L），不是頁首的機隊主口徑 L1_LTotalFleetVDisc。"
                             "免費占比 2026／2030 兩列是情境，不回流主序列。"))
    parts.append(section("2. 收入面 m（付費服務 token 的有效牌價變現率）",
                         table(v_payback._l1_table(l1, v_payback.M_ROWS), index=False), details(v_payback.M_ROWS),
                         sub="m＝實收單價 ÷ 有效牌價；有效牌價＝表列牌價 ×（1 − d）。m 只看收入面。"
                             "token 帳（L1_TokLedger）是診斷，不是 m。注意 m ∝ 1／(1 − d)：改 d 時 m 會變，m ×（1 − d）不變。"))
    gens = C.header_above(eng, "L1_LDiscGen")
    lab = C.name_label(eng, "L1_LDiscGen")[0]
    ldisc = pd.DataFrame([eng.get_name("L1_LDiscGen")], columns=gens, index=[lab])
    parts.append(section("3. L（壽命期價格係數）與回本所需 L",
                         table(v_payback._l1_table(l1, v_payback.L_ROWS), index=False),
                         f'<p class="label">各世代折現 L（L1_LDiscGen）：{e(lab)}</p>', table(fmt_df(ldisc)),
                         details(v_payback.L_ROWS)))
    hold = {n: eng.get_name(n) for n in ("AL_HoldGen_Lo", "AL_HoldGen", "AL_HoldGen_Hi") if n in eng.names}
    hdf = pd.DataFrame(hold, index=C.header_above(eng, "AL_HoldGen")).T
    hdf.index = [f"{n}｜{C.name_label(eng, n)[0]}" for n in hdf.index]
    parts.append(section("4. 每 GW 年持有成本（各世代；$B/GW·年）", table(fmt_df(hdf)),
                         note("2025 機隊每 GW 年持有成本 AL_FleetHold ＝ " + txt(eng.get_name("AL_FleetHold")) +
                              "（低 " + txt(eng.get_name("AL_FleetHold_Lo")) + "、高 " + txt(eng.get_name("AL_FleetHold_Hi")) + "）。")))
    lb = []
    for n in v_payback.LOAD_BEARING:
        if n in eng.names:
            r = C.input_row(eng, n)
            for k in ("基準", "低", "高"):
                r[k] = C.fmt_unit(r[k], r["單位"])
            lb.append(r)
    parts.append(section("5. 承重輸入（信心低）", table(pd.DataFrame(lb).map(txt), index=False),
                         note("整列取自輸入頁（標籤、單位、基準、低、高、標記、來源）。改這些值一律改 Excel，網站不提供改值。")))
    rows = [eng.row_values("NonNV", r, 12) for r in range(4, eng.max_row("NonNV") + 1)]
    rows = [r for r in rows if any(x != "" for x in r)]
    if rows:
        nn = pd.DataFrame(rows[1:], columns=[str(x) for x in rows[0]])
        parts.append(section("6. 非 NVIDIA 晶片（相對 VR200）", table(fmt_df(nn), index=False), note(str(eng.get("NonNV", "A2")))))
    return "回本判讀 — m、L、每 GW 營收 P × Q", "".join(parts), None


def page_lookup(cx: Ctx):
    eng = cx.eng
    idx = v_lookup._index(eng, str(eng.path))
    prefixes = sorted({n.split("_")[0] for n in idx["名稱"]})
    attrs = [{"pfx": n.split("_")[0], "s": f"{n} {lab}".lower()} for n, lab in zip(idx["名稱"], idx["標籤"].astype(str))]
    l1 = C.pct_by_unit_col(C.l1_rows(eng, str(eng.path)))      # 單位 % 的列以百分比顯示（與 Streamlit 名稱查詢頁相同）
    l1_attrs = [{"s": " ".join(txt(x) for x in row).lower()} for row in l1.itertuples(index=False)]
    chips = "".join(f'<button type="button" data-val="{e(p)}" aria-pressed="false">{e(p)}</button>' for p in prefixes)
    parts = [
        note(f"事實來源：{eng.path.name}。輸入名稱或中文標籤的片段（例：L1_M、持有成本、利用率、VR200）；多個關鍵字以空白分隔，須全部符合。"
             "關鍵字同時篩選下方 L1 全表（L1 比對整列文字）。"),
        '<div class="filters"><label class="qbox"><span>關鍵字</span><input type="search" class="q" data-targets="lk l1" '
        'placeholder="名稱或標籤片段" autocomplete="off"></label>'
        f'<div class="chips" data-target="lk" data-key="pfx"><span class="cl">只看這些前綴（全不選＝全部）</span>{chips}</div></div>',
        f'<p class="count">符合 <b class="cnt" data-target="lk">{len(idx):,}</b> 筆（全部 {len(idx):,} 個具名範圍）</p>',
        table(idx.map(txt), index=False, tid="lk", row_attrs=attrs, scroll=True),
        section("L1 全表（第 1 層常用推算值）",
                f'<p class="count">顯示 <b class="cnt" data-target="l1">{len(l1):,}</b> 列</p>',
                table(l1.map(txt), index=False, tid="l1", row_attrs=l1_attrs, scroll=True),
                note("L1 每列：基準值／低／高、單位、區間的定義、讀法、主要驅動、最弱輸入的標記，全部取自 Excel L1 頁。")),
    ]
    return "名稱查詢", "".join(parts), None


def page_overview(cx: Ctx):
    from openpyxl.utils import range_boundaries
    eng = cx.eng
    parts = [note(f"事實來源：{eng.path.name}。本網站只呈現 Excel 經 LibreOffice 重算後存下的值（唯讀），不含任何自有計算或參數。")]
    ctl = [n for n in eng.names if n.startswith("CTL_")]
    cards = [(n, eng.get_name(n), "") for n in ctl]
    for n in ("IF_Util",) + C.BLOCK3_SCALARS:
        s = C.interface_series(eng, n)
        cards.append((n, C.fmt_unit(s["values"][0], s["unit"]), s["label"]))
    parts.append(kpis(cards))
    gs = C.gov_status(eng)
    parts.append(section("治理狀態（Checks G 節）", kpis([(n, v, "") for n, v in gs.items()]),
                         table(C.gov_table(eng).map(txt), index=False),
                         note("ERROR 必須為 0（CI 讀取 GOV_Errors）；WARN、INFO 為待辦。完整表與 L1、Source 見「" + dict((k, t) for k, t, _ in PAGES)["governance"] + "」頁。")))
    block1 = [n for n in eng.names if C.is_downstream_name(n) and n != "IF_Util" and not C.is_block3_name(n) and not C.is_block4_name(n)
              and not C.is_block5_name(n) and not C.is_block6_name(n) and not any(n.startswith(f"IF_{m}_") for m in C.BLOCK2_METRICS)]
    hdr = len(eng.get_name("IF_HdrGen"))
    rows, units, idx, others = {}, [], None, []
    for n in sorted(block1, key=lambda n: range_boundaries(eng.name_ref(n)[1])[1]):
        s = C.interface_series(eng, n)
        if len(s["values"]) != hdr:
            others.append(n)
            continue
        rows[f"{s['label']}（{s['unit']}）"] = s["values"]
        units.append(s["unit"])
        if idx is None:
            idx = pd.MultiIndex.from_arrays([s["gens"], s["cases"]], names=["世代", "成本情境"])
    df = pd.DataFrame(rows, index=idx).T
    sec = [table(C.fmt_rows(df, units), index_head="指標（單位）＼世代｜成本情境")]      # 單位 % 的列 ×100 加 %
    if others:
        other_rows = []
        for n in others:
            s = C.series(eng, n)
            other_rows.append({"名稱": n, "標籤": s["label"], "單位": s["unit"], "值": "、".join(C.fmt_unit(v, s["unit"]) for v in s["values"])})
        sec += ['<p class="label">其他 Interface 名稱（不是「世代 × 成本情境」的形狀）</p>', table(pd.DataFrame(other_rows).map(txt), index=False)]
    sec.append(note("列標籤、單位、世代與成本情境皆取自 Excel Interface 頁；Block 2–5 見左側頁面。"))
    parts.append(section("Interface — Block 1（每 GW＝IT 關鍵電力）", *sec))
    return "Tokenomics — 總覽（Interface Block 1）", "".join(parts), None


def page_block2(cx: Ctx):
    eng = cx.eng
    tier_map = C.tiers(eng)
    tiers_, cases = list(tier_map), C.cost_cases(eng)
    spec = [("tier", "層級", list(tier_map.values()), 0), ("case", "成本情境", cases, 1)]
    parts = [note("每一列都帶層級（Luna／Sol／Astra）；100%＝理想上限，下游以自身利用率換算。資料只來自 Excel 的具名範圍。")]
    v_main, v_drv = [], []
    for ti, tier in enumerate(tiers_):
        for ci, case in enumerate(cases):
            df = C.block2_table(eng, tier, case)
            charts = "".join(df_chart(df, [m], title=m, w=380, h=230) for m in df.index)
            v_main.append(variant(
                f"<h4>{e(tier_map[tier])}｜成本情境：{e(case)}</h4>" + table(fmt_df(df, C.fmt), index_head="指標（單位）＼世代") +
                note("物理量（每架 tok/s、每 GW 產出、VR-eq、tokens/焦耳）不隨成本情境改變；$/M 隨成本情境改變。") +
                '<p class="label">圖：跨世代比較（每個指標一張）</p><div class="figs">' + charts + "</div>", tier=ti, case=ci))
            drv = C.drv_table(eng, tier, case)
            v_drv.append(variant(
                f"<h4>推導鏈｜{e(tier_map[tier])}</h4>" + table(drv, index_head="中間量（單位）＼世代") +
                note(f"decode $/M 列讀 Interface 的 IF_CostDec，跟隨上方成本情境選擇器（目前：{case}）；其餘為不隨成本情境改變的物理量。"),
                tier=ti, case=ci))
    util = C.interface_series(eng, "IF_Util")
    parts.append(section("依層級的產出與成本", *v_main, note(f"{util['label']}：{C.fmt_unit(util['values'][0], util['unit'])}")))
    parts.append(section("推導鏈", *v_drv,
                         sub="由上而下：每 token FLOPs → 每 GPU 權重 → 每步固定延遲 → 每序列每步時間與綁定項 → 批次與綁定約束 → "
                             "decode／prefill 每 GPU 產出 → prefill 占比 → 每架、每 GW 產出 → decode $/M → 能量閉合比。"
                             "欄＝世代；本區僅供顯示，下游模型不得連結 DRV_ 名稱。"))
    cal = [callout("InferenceX 為單一平台來源；MLPerf 由 NVIDIA 提交（利害關係方）。F 與 H 兩節的口徑不同，比值不可並列比較。", "warn")]
    for sec, title in (("F", "F 節：模型 ÷ 實測（InferenceX）"), ("H", "H 節：模型 ÷ MLPerf")):
        df, meta = C.calib_validation(eng, sec)
        show = df.copy()
        for col in ("每用戶速度", "實測", "模型", "比值"):
            show[col] = show[col].map(C.fmt)
        cal.append(f'<p class="label">{e(title)}　口徑：{e(C.basis_note(df))}</p>' + table(show.map(txt), index=False))
        notes = [f"{k}＝{v[0]}" + (f"（{v[1]}）" if v[1] not in (None, "") else "")
                 for k, v in meta.items() if k in ("每用戶速度", "實測", "模型", "比值") and v[0] != k]
        if notes:
            cal.append(note("；".join(notes)))
    cal.append(kpis([(label, value, "") for label, value in C.calib_scalars(eng)]))
    parts.append(section("Calib 驗證結果（唯讀）", *cal))
    return "Block 2 — 依層級的產出與成本", "".join(parts), spec


def page_block3(cx: Ctx):
    eng = cx.eng
    tier_map = C.tier_titles_trn(eng)
    tiers_, cases = list(tier_map), C.cost_cases(eng)
    spec = [("tier", "層級", list(tier_map.values()), 0), ("case", "成本情境", cases, 1)]
    parts = [note("每一列都帶層級（Luna／Sol／Astra）；GPU 小時不隨成本情境改變，$ 隨成本情境改變。"
                  f"下游預設訓練世代為 {'、'.join(C.train_gens(eng))} 並列（J13；讀 IF_TrainGenDefaultName／IF_TrainGenAltName），已排在各表最前面。"
                  "資料只來自 Excel 的具名範圍。")]
    rd = C.interface_series(eng, "IF_RDMult")
    v_out, v_share, v_trn = [], [], []
    for ti, tier in enumerate(tiers_):
        for ci, case in enumerate(cases):
            out = C.block3_table(eng, tier, case)
            v_out.append(variant(f"<h4>{e(tier_map[tier])}｜成本情境：{e(case)}</h4>" + table(out, index_head="指標（單位）＼世代"),
                                 tier=ti, case=ci))
        share = C.post_share_table(eng, tier)
        shown = share.copy().astype(object)
        for label in shown.index:
            shown.loc[label] = [f"{v:.4g}%" for v in share.loc[label]]
        chart = bar_chart([str(c) for c in share.columns],
                          [("FLOPs 口徑", list(share.iloc[0])), ("GPU 小時口徑", list(share.iloc[1]))], "占比（%）",
                          "後訓練占比：FLOPs 口徑對 GPU 小時口徑（%）")
        v_share.append(variant(f"<h4>後訓練占比（兩種口徑）與 RL 有效 MFU｜{e(tier_map[tier])}</h4>" + table(shown, index_head="指標＼世代") +
                               note("FLOPs 口徑＝後訓練計算量 ÷ 最終訓練計算量；GPU 小時口徑＝後訓練 GPU 小時 ÷ 最終訓練 GPU 小時。"
                                    "兩者的差距來自後訓練（尤其 RL）的有效 MFU 遠低於預訓練：同樣的 FLOPs 要用更多 GPU 小時。"
                                    "兩種口徑不可互換使用；外部以支出或 GPU 小時為口徑的比較，應對照 GPU 小時口徑。") + chart, tier=ti))
        v_trn.append(variant(f"<h4>推導鏈｜{e(tier_map[tier])}</h4>" + table(C.trn_table(eng, tier), index_head="中間量（單位）＼世代"), tier=ti))
    parts.append(section("依層級的訓練 GPU 小時、成本與研發計畫", *v_out,
                         note(f"{rd['label']}：{C.fmt_unit(rd['values'][0], rd['unit'])}（研發計畫 GPU 小時＝最終訓練 GPU 小時 × 研發倍數）。")))
    parts.append(section("後訓練占比與 RL 有效 MFU", *v_share))
    parts.append(section("推導鏈", *v_trn,
                         sub="由上而下依 Excel Training 頁列序：訓練 FLOPs/token → 預訓練 FLOPs 與 GPU 小時 → RL（有效 MFU、與預訓練之比）→ "
                             "最終訓練 → 後訓練占比 → 研發計畫。欄＝世代，表頭取自 TRN_Gen／TRN_Tier；本區僅供顯示，下游模型不得連結 TRN_ 名稱。"))
    reg, hook = C.registry_tables(eng)
    parts.append(section("Tech_Registry（唯讀）",
                         callout("技術開關、採用比例與倍數只能在 Excel（Project 端）修改並升版；本網站不提供開關。"
                                 "有效倍數＝1＋開關 × 採用比例 ×（所選倍數−1）；已在基準者恆為 1。"),
                         table(reg.map(txt), index=False),
                         '<p class="label">掛鉤彙總（同一掛鉤多條目時取乘積；Perf、Perf_Batch、Training 連結此表）</p>',
                         table(hook.map(txt), index=False)))
    return "Block 3 — 依層級的訓練 GPU 小時、成本與研發計畫", "".join(parts), spec


def page_block4(cx: Ctx):
    eng = cx.eng
    tier_map = C.tiers(eng)
    tiers_, gens, cases = list(tier_map), C.generations(eng), C.cost_cases(eng)
    spec = [("tier", "層級", list(tier_map.values()), 0), ("case", "成本情境", cases, 1), ("gen", "世代（推導鏈）", gens, 0)]
    parts = [note("每一列都標明層級（Luna／Sol／Astra）與 token 類型；單價為單一價格快照、不隨世代與成本情境改變，"
                  "營收隨世代改變（只由產能、利用率與單價決定，不隨成本情境）；成本與攤提隨世代與成本情境改變。"
                  "B4_ 名稱屬顯示或內部用，下游模型只可連結 IF_ 名稱。資料只來自 Excel 的具名範圍。")]
    parts.append(section("單價表（依層級）", table(C.price_table(eng, tier_map).map(txt), index_head="層級＼token 類型"),
                         note("列＝層級；欄＝token 類型。「OpenAI 有效」＝牌價 ×（1−折扣）× 能力單價倍數；「前緣混合」與「前緣模型」為候選表中"
                              "能力不低於該層級 OpenAI 模型者的最低請求混合單價。思考 token 依輸出價計費。")))
    parts.append(section("市場候選表", table(C.market_table(eng).map(txt), index=False),
                         note("標記＝「中國廠商」者為中國廠商列（國別欄取自 Excel）。能力指數空白者不參與前緣；"
                              "Artificial Analysis 的指數跨版本不可比（各列的指數版本以 Excel 為準）。價格為國際站美元牌價、非折扣後。")))
    v_rev, v_cost, v_chain = [], [], []
    for ti, tier in enumerate(tiers_):
        for ci, case in enumerate(cases):
            rev = C.rev_table(eng, tier, case, list(tier_map))
            v_rev.append(variant(f"<h4>每 GW 理論營收（理想上限）｜{e(tier_map[tier])}｜成本情境：{e(case)}</h4>" +
                                 table(fmt_df(rev, C.fmt), index_head="項目（單位）＼世代") +
                                 df_chart(rev, y_label="營收（單位見上表）", title="每 GW 理論營收（跨世代）"), tier=ti, case=ci))
            cost = C.cost_table(eng, tier, case)
            amort_rows = [i for i in cost.index if "訓練攤提" in i]
            full_rows = [i for i in cost.index if "全成本" in i]
            v_cost.append(variant(f"<h4>成本與攤提｜{e(tier_map[tier])}｜成本情境：{e(case)}</h4>" +
                                  table(fmt_df(cost, C.fmt), index_head="項目（單位）＼世代") +
                                  '<div class="figs two">' +
                                  df_chart(cost, amort_rows, "攤提（$/M）", "攤提 $/M 對照（跨世代）") +
                                  df_chart(cost, full_rows, "全成本（$/M）", "全成本 $/M 對照（跨世代；服務＋快取儲存＋攤提）") + "</div>",
                                  tier=ti, case=ci))
            for gi, gen in enumerate(gens):
                chain = C.b4_chain(eng, tier, gen, case)
                chain["值"] = [C.fmt_unit(v, u) for v, u in zip(chain["值"], chain["單位"])]   # 利用率等單位 % 者 ×100 加 %
                v_chain.append(variant(f"<h4>推導鏈｜{e(tier_map[tier])}｜{e(gen)}｜成本情境：{e(case)}</h4>" + table(chain.map(txt), index=False),
                                       tier=ti, case=ci, gen=gi))
    parts.append(section("每 GW 理論營收（理想上限）", *v_rev,
                         note("理想上限＝SLO 產能 × 利用率 × 有效單價，未計需求不足、價格競爭與未售出產能。"
                              "機隊列為 1 GW 參考機隊：先列 Luna、Sol、Astra 三層級的貢獻，再列合計；合計是依付費 token 組合加權的層級組合，不是單一層級。")))
    parts.append(section("成本與攤提", *v_cost,
                         callout("K6 下游預設為 (c)：由上而下總額 × 自下而上權重（IF_AmortDefault_*、IF_FullCostDefault_*，下游連結此兩者）。"
                                 "自下而上、由上而下、(d)（由上而下總額 × 營收權重）與以自下而上攤提計的全成本，列為對照；對照列不是下游預設。")))
    parts.append(section("推導鏈", *v_chain,
                         sub="依序：每 GW 產出 → 利用率 → 有效單價 → 理論營收 → 服務成本 → 快取儲存 → 攤提 → 全成本。"
                             "每一步都是 Excel 既有具名範圍的值（IF_），此處不新增計算。世代由上方「世代（推導鏈）」選擇。"))
    return "Block 4 — 單價、理論營收（理想上限）與成本攤提", "".join(parts), spec


def page_block5(cx: Ctx):
    eng = cx.eng
    tier_map = C.tiers(eng)
    tiers_, tasks = list(tier_map), C.task_names(eng)
    spec = [("tier", "層級", list(tier_map.values()), 0), ("task", "任務（推導鏈）", tasks, 0)]
    parts = [note("只讀 Interface E 節與 IF_HdrTask。每一個依層級的欄都標明層級（Luna／Sol／Astra）；每次嘗試的 token 依類型分列"
                  "（新鮮輸入、快取輸入、decode）。資料只來自 Excel 的具名範圍。")]
    w, prof = C.scalar(eng, "IF_HarW"), C.scalar(eng, "IF_HarProfile")
    parts.append(kpis([(f"{w['label']}（{w['unit']}）", C.fmt_unit(w["value"], w["unit"]), ""), (prof["label"], prof["value"], "")]))
    parts.append(callout("基準 w＝0，現行＝標準 harness；選定檔案為情境（欄名含「選定檔案」者）。"
                         "每 GW 理論營收不受 harness 影響（L4），Block 4 的營收表不隨本頁的 harness 設定改變。"))
    v_tbl, v_chain = [], []
    for ti, tier in enumerate(tiers_):
        tbl = C.b5_table(eng, tier)
        v_tbl.append(variant(f"<h4>任務表｜{e(tier_map[tier])}</h4>" + table(tbl.T, index_head="項目（單位）＼任務"), tier=ti))
        for ki, task in enumerate(tasks):
            chain = C.b5_chain(eng, tier, tiers_, task)
            chain["值"] = [C.fmt_unit(v, u) for v, u in zip(chain["值"], chain["單位"])]
            chain = chain[["步驟", "層級", "token 類型", "值", "單位", "項目（Excel 標籤）"]]
            v_chain.append(variant(f"<h4>推導鏈｜{e(tier_map[tier])}｜{e(task)}</h4>" + table(chain.map(txt), index=False), tier=ti, task=ki))
    parts.append(section("任務表", *v_tbl,
                         note("欄＝任務（取自 IF_HdrTask）；列＝每次嘗試 token（新鮮輸入、快取輸入、decode）、成功率（現行、選定檔案）、"
                              "每成功任務成本（VR200、GB300；經濟、基準成本、基準利用率）、每成功任務營收（OpenAI 有效單價）與 R（選定 ÷ 標準，VR200）。")))
    parts.append(section("推導鏈", *v_chain,
                         sub="依序：任務長度 → 時間範圍（有效值；層級基準列為對照）→ 成功率 → 每次嘗試（token）→ 每次嘗試成本（$）→ ÷ p → 每成功任務成本 → 每成功任務營收。"
                             "每一步都是 Excel 既有具名範圍的值（IF_、B5_），本頁不自行計算；成功率為百分比。任務由上方「任務（推導鏈）」選擇。"))
    pf = C.scalar(eng, "IF_PFloor")
    parts.append(section("成功任務成本前緣（VR200）", kpis([(f"{pf['label']}（{pf['unit']}）", C.fmt_unit(pf["value"], pf["unit"]), "")]),
                         table(C.b5_front(eng).map(txt), index_head="項目＼任務"),
                         note("只比較 p ≥ p_min 的層級 × 檔案組合；p_min 為 Excel 輸入（B5_PFloor）。欄＝任務；列＝最低每成功任務成本、組合（層級｜檔案）、組合成功率；"
                              "『無合格』＝無組合達下限。本頁只顯示 Excel 的前緣（IF_FrontSuccVR*），不在網站重算。")))
    return "Block 5 — 任務層：token、成功率與每成功任務成本", "".join(parts), spec


def page_alloc(cx: Ctx):
    df = v_alloc.chain_table(cx.eng)
    parts = [note("需求 D → 服務 GW → 研發 GW → Q1、Q2；基準為 2025 穩態年度。輸入在 Excel 的 Alloc_In（Project 端修改），本頁唯讀。SLO 不可達時顯示文字。")]
    for sec in dict.fromkeys(df["節"]):
        parts.append(section(sec, table(df[df["節"] == sec].drop(columns="節").reset_index(drop=True).map(txt), index=False)))
    return "Alloc — 研發與服務的算力配置（Block 6）", "".join(parts), None


def page_qa(cx: Ctx):
    df = v_qa.answers(cx.eng)
    parts = [note("答案、區間、讀法與缺口全部來自 Excel 的 L1 頁；本頁唯讀。")]
    for _, r in df.iterrows():
        rows = "".join(f"<dt>{e(k)}</dt><dd>{e(txt(r[c])) or '—'}</dd>" for k, c in (
            ("單位", "單位"), ("條件", "條件"), ("區間的定義", "區間的定義"), ("讀法", "讀法"), ("最弱輸入", "最弱輸入的標記"),
            ("所在頁與列", "所在頁與列"), ("未能回答的部分（缺口）", "未能回答的部分")))
        parts.append(f'<section class="sec qa"><h3>{e(r["指標或問題"])}</h3><p class="tagx">{e(r["L1_ID"])}</p>' +
                     kpis([("答案（基準值）", C.fmt_unit(r["基準值"], r["單位"]), f"單位：{txt(r['單位'])}"),
                           ("低", C.fmt_unit(r["低"], r["單位"]), ""), ("高", C.fmt_unit(r["高"], r["單位"]), "")]) +
                     f'<dl class="kv">{rows}</dl></section>')
    return "問答 — Block 6 九題（L1_Ans1–9；含毛利率與 GPU 小時口徑子項）", "".join(parts), None


def _chips(target: str, key: str, label: str, values) -> str:
    """篩選控制：選項 ≤ 12 個用可複選的 chips；更多（自由文字欄）用下拉選單（單選，空白＝全部）。"""
    values = list(values)
    if len(values) > 12:
        opts = "".join(f'<option value="{e(v)}">{e(v if len(v) <= 60 else v[:59] + "…")}</option>' for v in values)
        return (f'<label class="qbox"><span>{e(label)}</span><select class="fsel" data-target="{target}" data-key="{key}">'
                f'<option value="">（全部 {len(values)} 種）</option>{opts}</select></label>')
    btns = "".join(f'<button type="button" data-val="{e(v)}" aria-pressed="false">{e(v)}</button>' for v in values)
    return f'<div class="chips" data-target="{target}" data-key="{key}"><span class="cl">{e(label)}</span>{btns}</div>'


def page_evidence(cx: Ctx):
    df = C.evidence_table(cx.eng)
    shown = df.map(txt)
    verdicts = sorted({str(x) for x in shown["判定"]})
    tags = sorted({str(x) for x in shown["標記"]})
    attrs = [{"verdict": v, "tag": t, "s": " ".join(r).lower()} for v, t, r in zip(shown["判定"], shown["標記"], shown.itertuples(index=False))]
    parts = [note("每一筆新資訊先與 Tokenomics 現值比對，再判定採納與否；本頁只呈現 Excel 的內容，不提供編輯。"
                  "新增或修改證據請在 Excel（Project 端）進行並升版。"),
             '<div class="filters"><label class="qbox"><span>關鍵字</span><input type="search" class="q" data-targets="ev" placeholder="任一欄文字片段" autocomplete="off"></label>' +
             _chips("ev", "verdict", "判定", verdicts) + _chips("ev", "tag", "標記", tags) + "</div>",
             f'<p class="count">共 {len(df)} 筆；目前顯示 <b class="cnt" data-target="ev">{len(df)}</b> 筆。</p>',
             table(shown, index=False, tid="ev", row_attrs=attrs, scroll=True)]
    return "證據登錄（DB_Evidence，唯讀）", "".join(parts), None


def page_governance(cx: Ctx):
    eng = cx.eng
    parts = [note("本頁唯讀，只呈現 Excel 的內容；新增或修改請在 Excel（Project 端）進行並升版。")]
    parts.append(kpis([(n, v, "") for n, v in C.gov_status(eng).items()]))
    parts.append(section("Checks G 節", table(C.gov_table(eng).map(txt), index=False)))
    l1 = C.l1_table(eng)
    parts.append(section("L1 — 第 1 層常用推算值", table(l1.map(txt), index=False, scroll=True),
                         note(f"共 {len(l1)} 列；基準值、低、高皆為 Excel 即時公式。")))
    tables = C.src_tables(eng)
    names = list(tables)
    v = []
    for i, (sheet, t) in enumerate(tables.items()):
        shown = t.map(txt)
        states = sorted({str(x) for x in shown["狀態"]})
        tid = f"src{i}"
        v.append(variant(f"<h4>{e(sheet)}</h4>" + '<div class="filters">' + _chips(tid, "state", "狀態（全不選＝全部）", states) + "</div>" +
                         f'<p class="count">{e(sheet)}：共 {len(t)} 筆；目前顯示 <b class="cnt" data-target="{tid}">{len(t)}</b> 筆。</p>' +
                         table(shown, index=False, tid=tid, row_attrs=[{"state": s} for s in shown["狀態"]], scroll=True), sheet=i))
    parts.append(section("Source — 第 0 層（SRC_*，A–W 欄）", controls([("sheet", "工作表", names, 0)]), *v))
    return "治理 — Source（第 0 層）、L1（第 1 層）、Checks G 節", "".join(parts), None


BUILDERS = {"payback": page_payback, "lookup": page_lookup, "overview": page_overview, "block2": page_block2, "block3": page_block3,
            "block4": page_block4, "block5": page_block5, "alloc": page_alloc, "qa": page_qa, "evidence": page_evidence,
            "governance": page_governance}


# ── 版面 ───────────────────────────────────────────────────────────

CSS = r"""
/* 版面：研究入口式刊頭（與 company-models 的 AI 投資地圖同色系）→ 左側導覽 → 單頁內容；表格細線、數字等寬 */
:root{
  --paper:#F5F6F8; --surface:#FFFFFF; --sunken:#EEF1F5; --ink:#0F1B2D; --muted:#5A6577; --faint:#8A94A3;
  --rule:#D8DDE4; --rule-strong:#AEB7C3; --navy:#12284A; --navy-ink:#E9EEF6; --navy-muted:#9FB0C9;
  --brass:#8C6A2E; --info:#2F4C78; --info-bg:#E6ECF5; --watch:#9A6410; --watch-bg:#F7EDDB;
  --c0:#2F4C78; --c1:#B07A2A; --c2:#1D7A52; --c3:#8E3B46; --c4:#5B3C88; --c5:#4D8FB8; --c6:#7A8B3A; --c7:#C4572C; --c8:#6B7480; --c9:#2B8C88;
  --f-display:"Noto Serif TC","Noto Serif CJK TC","Songti TC",Georgia,serif;
  --f-body:"IBM Plex Sans","Noto Sans TC","Noto Sans CJK TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
  --f-mono:"IBM Plex Mono","SFMono-Regular",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root{
  --paper:#0C1118; --surface:#121923; --sunken:#0F151E; --ink:#E4E9F0; --muted:#9BA6B6; --faint:#6F7A8A;
  --rule:#243041; --rule-strong:#3A4A60; --navy:#0A1626; --navy-ink:#E4EAF3; --navy-muted:#8296B3;
  --brass:#C9A35C; --info:#8FB0E0; --info-bg:#15233A; --watch:#E2A64A; --watch-bg:#2B2213;
  --c0:#7FA2D6; --c1:#D9A75A; --c2:#55C08E; --c3:#E07A86; --c4:#B79AE6; --c5:#7CC3E8; --c6:#B5C46A; --c7:#F08C5E; --c8:#9AA3AF; --c9:#5FC7C2;
  color-scheme:dark}}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{background:var(--paper);color:var(--ink);font-family:var(--f-body);font-size:14px;line-height:1.55;margin:0}
h1,h2,h3,h4{font-family:var(--f-display);margin:0;font-weight:700;text-wrap:balance}
code,.num,td.n,.mono{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
a{color:inherit}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px}
.mast{background:var(--navy);color:var(--navy-ink)}
.mast .in{max-width:1440px;margin:0 auto;padding:22px 20px 18px}
.eyebrow{font-size:11px;letter-spacing:.14em;color:var(--navy-muted);display:flex;gap:10px;align-items:center}
.eyebrow::before{content:"";width:18px;height:2px;background:var(--brass)}
.mast h1{font-size:30px;letter-spacing:.02em;margin-top:6px}
.mast p{margin:6px 0 0;color:var(--navy-muted);max-width:980px}
.meta{display:flex;flex-wrap:wrap;gap:4px 22px;font-size:12px;color:var(--navy-muted);border-top:1px solid #ffffff2e;margin:14px 0 0;padding-top:10px}
.meta div{display:flex;gap:8px;min-width:0}
.meta dt{white-space:nowrap}
.meta dd{margin:0;color:var(--navy-ink);font-family:var(--f-mono);overflow-wrap:anywhere}
.shell{max-width:1440px;margin:0 auto;display:grid;grid-template-columns:250px minmax(0,1fr);gap:0;align-items:start}
.side{position:sticky;top:0;max-height:100vh;overflow-y:auto;padding:18px 0 24px;border-right:1px solid var(--rule);background:var(--surface);min-height:calc(100vh - 160px)}
.side .lab{font-size:11px;letter-spacing:.12em;color:var(--faint);padding:0 18px 8px}
.side ol{list-style:none;margin:0;padding:0;counter-reset:p;position:relative}
.side li a{display:flex;gap:8px;padding:9px 18px;text-decoration:none;color:var(--muted);border-left:3px solid transparent;line-height:1.35}
.side li a::before{counter-increment:p;content:counter(p,decimal-leading-zero);font-family:var(--f-mono);font-size:11px;color:var(--faint);padding-top:2px}
.side li a:hover{color:var(--ink);background:var(--sunken)}
.side li a[aria-current="page"]{color:var(--ink);font-weight:600;border-left-color:var(--brass);background:var(--sunken)}
main{min-width:0;padding:20px 24px 56px}
.pt{font-size:24px}
.ptsub{margin:4px 0 0;color:var(--muted);font-size:13px}
.sec>.ctlbar{margin:0}
.ctlbar{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1px solid var(--rule-strong);padding:10px 0;margin:12px 0 4px;display:flex;flex-wrap:wrap;gap:8px 22px}
.cg{display:flex;gap:8px;align-items:center;flex-wrap:wrap;min-width:0}
.cl{font-size:12px;color:var(--muted);white-space:nowrap}
.seg{display:flex;flex-wrap:wrap;border:1px solid var(--rule-strong);border-radius:3px;overflow:hidden;background:var(--surface)}
.seg button{font:500 13px var(--f-body);background:none;color:var(--ink);border:0;border-right:1px solid var(--rule);padding:5px 10px;cursor:pointer}
.seg button:last-child{border-right:0}
.seg button[aria-pressed="true"]{background:var(--navy);color:var(--navy-ink)}
.sec{margin-top:26px;display:grid;gap:10px;min-width:0}
.sec>*{min-width:0}
.sec h3{font-size:18px;padding-bottom:6px;border-bottom:1px solid var(--rule)}
.sec h4{font-size:15px;margin:4px 0 8px}
.var{display:grid;gap:10px;min-width:0}
.lede{margin:0;color:var(--muted)}
.note{margin:0;font-size:12.5px;color:var(--muted)}
.label{margin:6px 0 0;font-size:12px;letter-spacing:.04em;color:var(--muted);font-weight:600}
.callout{border-left:3px solid var(--info);background:var(--info-bg);padding:10px 14px;font-size:13px}
.callout.warn{border-left-color:var(--watch);background:var(--watch-bg)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));border:1px solid var(--rule);background:var(--surface);margin-top:12px}
.kpi{padding:12px 16px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);min-width:0;margin:0 -1px -1px 0}
.kpi .k{font-size:11.5px;color:var(--muted);overflow-wrap:anywhere}
.kpi .v{font-size:22px;font-weight:500;margin-top:2px;overflow-wrap:anywhere}
.kpi .s{font-size:12px;color:var(--muted);margin-top:2px}
.tw{overflow:auto;max-width:100%;border:1px solid var(--rule);background:var(--surface)}
.tw.scroll{max-height:640px}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{border-bottom:1px solid var(--rule);padding:5px 9px;vertical-align:top;text-align:left;white-space:nowrap}
thead th{position:sticky;top:0;z-index:2;background:var(--sunken);font-weight:600;color:var(--ink);white-space:normal;min-width:72px;border-bottom:1px solid var(--rule-strong)}
thead tr+tr th{top:30px}
th.grp{text-align:center;border-left:1px solid var(--rule)}
th.ix{font-weight:500;color:var(--ink);white-space:normal;min-width:200px;max-width:340px;background:var(--surface)}
thead th.ix{background:var(--sunken)}
td.n{text-align:right}
th.ab{cursor:help}
th.ab .more{color:var(--faint);margin-left:2px}
td.wr{white-space:normal;min-width:220px;max-width:460px}
td.blank{color:var(--faint);text-align:center}
tbody tr:hover td,tbody tr:hover th{background:var(--sunken)}
.figs{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.figs.two{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.fig{margin:0;max-width:860px;background:var(--surface);border:1px solid var(--rule);padding:10px 10px 6px;min-width:0}
.fig figcaption{font-size:12px;color:var(--muted);margin-bottom:4px}
svg.chart{width:100%;height:auto;display:block}
svg .grid{stroke:var(--rule);stroke-width:1}
svg .zero{stroke:var(--rule-strong);stroke-width:1}
svg .ax{fill:var(--muted);font-size:11px;font-family:var(--f-body)}
svg .lab{fill:var(--faint)}
.b0{fill:var(--c0)}.b1{fill:var(--c1)}.b2{fill:var(--c2)}.b3{fill:var(--c3)}.b4{fill:var(--c4)}.b5{fill:var(--c5)}.b6{fill:var(--c6)}.b7{fill:var(--c7)}.b8{fill:var(--c8)}.b9{fill:var(--c9)}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:11.5px;color:var(--muted);margin-top:4px}
.legend i{display:inline-block;width:10px;height:10px;margin-right:5px;vertical-align:-1px}
.k0{background:var(--c0)}.k1{background:var(--c1)}.k2{background:var(--c2)}.k3{background:var(--c3)}.k4{background:var(--c4)}.k5{background:var(--c5)}.k6{background:var(--c6)}.k7{background:var(--c7)}.k8{background:var(--c8)}.k9{background:var(--c9)}
.dets{display:grid;gap:4px}
.det{background:var(--surface);border:1px solid var(--rule);padding:6px 12px}
.det summary{cursor:pointer;font-size:13px}
.det dl,.kv{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:4px 14px;margin:8px 0 2px;font-size:13px}
.det dt,.kv dt{color:var(--muted);font-weight:600}
.det dd,.kv dd{margin:0;overflow-wrap:anywhere}
.tagx{margin:0;font-family:var(--f-mono);font-size:11px;color:var(--faint)}
.filters{display:grid;gap:8px;margin-top:10px}
.qbox{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.qbox span{font-size:12px;color:var(--muted)}
.qbox input,.qbox select{font:inherit;max-width:100%;padding:6px 10px;border:1px solid var(--rule-strong);border-radius:3px;background:var(--surface);color:var(--ink);width:min(420px,100%)}
.chips{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.chips button{font:12px var(--f-body);border:1px solid var(--rule-strong);background:var(--surface);color:var(--ink);border-radius:12px;padding:2px 10px;cursor:pointer}
.chips button[aria-pressed="true"]{background:var(--navy);color:var(--navy-ink);border-color:var(--navy)}
.count{margin:0;font-size:12.5px;color:var(--muted)}
footer{border-top:1px solid var(--rule);color:var(--muted);font-size:12px}
footer .in{max-width:1440px;margin:0 auto;padding:16px 20px 28px}
@media (max-width:900px){
  .mast .in{padding:16px 14px 14px}
  .mast h1{font-size:24px}
  .shell{grid-template-columns:minmax(0,1fr)}
  .side{position:static;max-height:none;min-height:0;border-right:0;border-bottom:1px solid var(--rule);padding:8px 0}
  .side .lab{display:none}
  .side ol{display:flex;overflow-x:auto;gap:0;scrollbar-width:thin}
  .side li{flex:0 0 auto}
  .side li a{border-left:0;border-bottom:3px solid transparent;padding:8px 12px;white-space:nowrap}
  .side li a[aria-current="page"]{border-bottom-color:var(--brass)}
  main{padding:14px 12px 40px}
  .pt{font-size:20px}
  th.ix{min-width:150px;max-width:200px}
  td.wr{min-width:180px;max-width:280px}
  .figs{grid-template-columns:minmax(0,1fr)}
  .kpis{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
  .det dl,.kv{grid-template-columns:minmax(0,1fr)}
  .ctlbar{gap:6px 14px;position:static}
}
"""

JS = r"""
(function(){
  var st={};
  function apply(){
    document.querySelectorAll('.var').forEach(function(el){
      var ok=true;
      Object.keys(el.dataset).forEach(function(k){
        if(k.length>1&&k[0]==='v'&&k[1]===k[1].toUpperCase()){var d=k.slice(1).toLowerCase(); if(st[d]!==undefined&&st[d]!==el.dataset[k]) ok=false;}
      });
      el.hidden=!ok;
    });
  }
  document.querySelectorAll('.seg[data-dim]').forEach(function(g){
    var on=g.querySelector('button[aria-pressed="true"]'); st[g.dataset.dim]=on?on.dataset.v:'0';
    g.addEventListener('click',function(ev){var b=ev.target.closest('button'); if(!b) return;
      g.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
      st[g.dataset.dim]=b.dataset.v; apply();});
  });
  apply();
  // 窄螢幕：導覽列橫向捲到目前頁
  var cur=document.querySelector('.side a[aria-current="page"]'), ol=document.querySelector('.side ol');
  if(cur&&ol&&ol.scrollWidth>ol.clientWidth){ ol.scrollLeft=Math.max(0,cur.parentNode.offsetLeft-12); }
  // 表格篩選：chips（依列的 data-<key>）＋關鍵字（依列的 data-s，全部關鍵字須符合）
  var words=[];
  function filter(id){
    var t=document.getElementById(id); if(!t) return;
    var sel={};
    document.querySelectorAll('.chips[data-target="'+id+'"]').forEach(function(c){
      var v=[]; c.querySelectorAll('button[aria-pressed="true"]').forEach(function(b){v.push(b.dataset.val);});
      if(v.length) sel[c.dataset.key]=v;
    });
    document.querySelectorAll('.fsel[data-target="'+id+'"]').forEach(function(c){ if(c.value) sel[c.dataset.key]=[c.value]; });
    var useQ=!!document.querySelector('.q[data-targets~="'+id+'"]');
    var n=0;
    t.querySelectorAll('tbody tr').forEach(function(r){
      var ok=true;
      Object.keys(sel).forEach(function(k){ if(sel[k].indexOf(r.dataset[k])<0) ok=false; });
      if(ok&&useQ){ var s=r.dataset.s||''; for(var i=0;i<words.length;i++){ if(s.indexOf(words[i])<0){ok=false;break;} } }
      r.hidden=!ok; if(ok) n++;
    });
    document.querySelectorAll('.cnt[data-target="'+id+'"]').forEach(function(c){c.textContent=n.toLocaleString('en-US');});
  }
  document.querySelectorAll('.chips').forEach(function(c){
    c.addEventListener('click',function(ev){var b=ev.target.closest('button'); if(!b) return;
      b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true'); filter(c.dataset.target);});
  });
  document.querySelectorAll('.fsel').forEach(function(c){ c.addEventListener('change',function(){filter(c.dataset.target);}); });
  document.querySelectorAll('.q').forEach(function(q){
    q.addEventListener('input',function(){
      words=q.value.toLowerCase().split(/\s+/).filter(Boolean);
      q.dataset.targets.split(' ').forEach(filter);
    });
  });
})();
"""


def git_meta() -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout.strip()
        except Exception:
            return ""
    head = run("rev-parse", "--short=7", "HEAD")
    master = ""
    for ref in ("origin/master", "master"):
        if run("rev-parse", "--verify", "-q", ref):
            master = ref
            break
    out = {"head": head, "master": head, "on_master": True}
    if master and head:
        on = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", "HEAD", master]).returncode == 0
        if not on:
            out["master"] = run("rev-parse", "--short=7", run("merge-base", "HEAD", master))
            out["on_master"] = False
    return out


def render_page(key: str, nav_title: str, path: str, body_title: str, body: str, spec, meta: dict) -> str:
    links = "".join(
        f'<li><a href="{page_file(p)}"{" aria-current=\"page\"" if k == key else ""}>{e(t)}</a></li>' for k, t, p in PAGES)
    commit = meta["master"] + ("" if meta["on_master"] else f"（建置自分支 commit {meta['head']}）")
    ctl = controls(spec) if spec else ""
    sub = f'<p class="ptsub">{e(body_title)}</p>' if body_title else ""
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(nav_title)}｜Tokenomics {e(meta['version'])}</title>
<style>{CSS}</style>
</head>
<body>
<header class="mast"><div class="in">
<div class="eyebrow">算力收支｜第 0 層模型｜唯讀靜態版</div>
<h1>Tokenomics</h1>
<p>AI 資料中心的 token 經濟學：由物理量推到每 GW 的產能、成本、營收與回本。本站只呈現 Excel 經 LibreOffice 重算後存下的值，不做任何計算、不可調整。</p>
<dl class="meta">
<div><dt>模型版本</dt><dd id="meta-version">{e(meta['version'])}</dd></div>
<div><dt>Excel</dt><dd id="meta-excel">{e(meta['excel'])}</dd></div>
<div><dt>master commit</dt><dd id="meta-commit">{e(commit)}</dd></div>
<div><dt>建置日期</dt><dd id="meta-date">{e(meta['date'])}</dd></div>
</dl>
</div></header>
<div class="shell">
<nav class="side" aria-label="頁面"><div class="lab">頁面</div><ol>{links}</ol></nav>
<main id="main" data-page="{e(key)}">
<h2 class="pt">{e(nav_title)}</h2>{sub}
{ctl}
{body}
</main>
</div>
<footer><div class="in">研究整理，非投資建議。數字全部取自 {e(meta['excel'])}（LibreOffice 重算後存下的值）；「—」＝Excel 該格空白。
選擇器只切換預先產生的版本，網站不重算。改值一律改 Excel 並升版。</div></footer>
<script>{JS}</script>
</body>
</html>
"""


def build(out: Path = DEFAULT_OUT, model: Path | None = None) -> dict:
    eng = Workbook(model)
    m = re.search(r"_(v[\d.]+)\.xlsx$", eng.path.name)
    g = git_meta()
    meta = {"version": m.group(1) if m else "", "excel": eng.path.name, "date": dt.datetime.now(TZ_TPE).strftime("%Y-%m-%d"),
            "head": g["head"], "master": g["master"], "on_master": g["on_master"]}
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.html"):
        old.unlink()
    cx = Ctx(eng)
    files = {}
    for key, title, path in PAGES:
        body_title, body, spec = BUILDERS[key](cx)
        fn = page_file(path)
        (out / fn).write_text(render_page(key, title, path, body_title, body, spec, meta), encoding="utf-8")
        files[key] = fn
    meta["pages"] = [{"key": k, "title": t, "file": files[k]} for k, t, _ in PAGES]
    (out / "build.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--model", type=Path, default=None, help="預設讀 model/CURRENT")
    a = ap.parse_args()
    meta = build(a.out, a.model)
    sizes = {p["file"]: (a.out / p["file"]).stat().st_size for p in meta["pages"]}
    print(f"已建置 {len(sizes)} 頁 → {a.out}（{meta['excel']}，{meta['version']}，master {meta['master']}，{meta['date']}）")
    for f, s in sizes.items():
        print(f"  {f:18s} {s / 1024:8.0f} KB")


if __name__ == "__main__":
    main()

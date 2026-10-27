"""token 牌價每月追蹤（API 版，2026-10-27 起）。

目的：替 L 的 g（token 單價下跌趨勢）每月留一份可回溯的牌價快照，並列出與上月相比的變動。
只產出資料與說明，不改 Tokenomics 模型；g 的計算與是否更新參數由 chat 端與 Andy 判斷。

資料來源：OpenRouter 公開模型清單 API（https://openrouter.ai/api/v1/models，免金鑰、供程式讀取）。
  - 價格為 OpenRouter 上的牌價（每 token 美元），可能與原廠直連價不同；同一模型多個供應商時為 OpenRouter 顯示價。
  - 屬第三方彙整資料，標記 [Interested-party]（OpenRouter 是轉售平台）；重要價格須以原廠價目頁覆核。

輸出（commit 回分支）：
  data/price_track/YYYY-MM.csv   全部模型快照（id、名稱、建立日、輸入／輸出／快取讀取單價、上下文長度）
  tools/price_track/out/YYYY-MM.xlsx 與 .md  觀察清單（原廠前沿模型）與上月比較；API（Sonnet）寫一段繁中摘要
"""
import csv
import datetime as dt
import glob
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
UA = "Tokenomics price tracking (github.com/YinchenChang/Tokenomics)"
# 觀察清單：原廠前綴（OpenRouter id 的前段）。只用來挑出前沿模型做比較表；快照保留全部模型。
WATCH = ["openai/", "anthropic/", "google/", "deepseek/", "x-ai/", "qwen/", "moonshotai/", "z-ai/", "minimax/", "meta-llama/", "mistralai/"]


def get_models():
    req = urllib.request.Request("https://openrouter.ai/api/v1/models", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]


def per_m(x):
    """每 token 美元 → 每百萬 token 美元；缺值或負值（動態定價）回傳 None。"""
    try:
        v = float(x)
        return round(v * 1e6, 4) if v >= 0 else None
    except (TypeError, ValueError):
        return None


def snapshot(models):
    rows = []
    for m in models:
        p = m.get("pricing", {}) or {}
        rows.append({"id": m.get("id"), "name": m.get("name"),
                     "created": dt.datetime.utcfromtimestamp(m.get("created", 0)).strftime("%Y-%m-%d") if m.get("created") else "",
                     "in_per_m": per_m(p.get("prompt")), "out_per_m": per_m(p.get("completion")),
                     "cache_read_per_m": per_m(p.get("input_cache_read")), "context": m.get("context_length")})
    return sorted(rows, key=lambda r: r["id"] or "")


def load_prev(month):
    files = sorted(f for f in glob.glob(f"{ROOT}/data/price_track/*.csv") if os.path.basename(f)[:7] < month)
    if not files:
        return None, {}
    with open(files[-1], encoding="utf-8") as f:
        return os.path.basename(files[-1])[:7], {r["id"]: r for r in csv.DictReader(f)}


def summarize(text):
    if not API_KEY:
        return "（未設定 API 金鑰，略過摘要）", 0.0
    body = {"model": "claude-sonnet-5-5", "max_tokens": 2000,
            "system": "你是研究助理。根據提供的 token 牌價比較表，用繁體中文（台灣用語）寫 5–8 條客觀重點："
                      "新上架的前沿模型與其價位、同一模型的調價、各家旗艦輸出價的相對位置、快取價格的變化。"
                      "只根據表中數字，不推測原因，不下投資判斷；註明資料來自 OpenRouter 牌價、可能不同於原廠直連價。",
            "messages": [{"role": "user", "content": text[:150000]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
                                 headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        res = json.load(r)
    u = res.get("usage", {})
    return "".join(c.get("text", "") for c in res["content"]), (u.get("input_tokens", 0) * 2 + u.get("output_tokens", 0) * 10) / 1e6


def main():
    month = os.environ.get("TRACK_MONTH") or dt.datetime.utcnow().strftime("%Y-%m")
    rows = snapshot(get_models())
    os.makedirs(f"{ROOT}/data/price_track", exist_ok=True)
    with open(f"{ROOT}/data/price_track/{month}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    prev_month, prev = load_prev(month)
    watch = [r for r in rows if any((r["id"] or "").startswith(p) for p in WATCH) and r["out_per_m"] is not None]
    lines = []
    for r in watch:
        p = prev.get(r["id"])
        status = "新上架" if prev and not p else ("" if not prev else "")
        chg_in = chg_out = None
        if p:
            for k, tgt in (("in_per_m", "chg_in"), ("out_per_m", "chg_out")):
                try:
                    old, new = float(p[k]), float(r[k])
                    val = round(new / old - 1, 4) if old > 0 else None
                except (TypeError, ValueError):
                    val = None
                if tgt == "chg_in":
                    chg_in = val
                else:
                    chg_out = val
            if (chg_in or 0) != 0 or (chg_out or 0) != 0:
                status = "調價"
        r.update({"status": status, "chg_in": chg_in, "chg_out": chg_out})
        lines.append(r)
    gone = [i for i in prev if any(i.startswith(p) for p in WATCH) and i not in {r["id"] for r in rows}] if prev else []

    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "觀察清單"
    ws.append(["模型 id", "名稱", "OpenRouter 建立日", "輸入（美元／百萬 token）", "輸出", "快取讀取", "上下文長度", "狀態", "輸入價變動", "輸出價變動"])
    for r in sorted(lines, key=lambda r: (r["status"] == "", r["id"])):
        ws.append([r["id"], r["name"], r["created"], r["in_per_m"], r["out_per_m"], r["cache_read_per_m"], r["context"],
                   r["status"], r["chg_in"], r["chg_out"]])
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "B2"
    for col, w in zip("ABCDEFGHIJ", (40, 36, 14, 12, 12, 12, 12, 10, 12, 12)):
        ws.column_dimensions[col].width = w
    s2 = wb.create_sheet("下架")
    s2.append(["上月有、本月無的觀察清單模型"])
    for i in gone:
        s2.append([i])
    s3 = wb.create_sheet("說明")
    for row in [["資料月份", month], ["比較基準", prev_month or "（無：首月）"], ["來源", "OpenRouter /api/v1/models（[Interested-party] 轉售平台牌價）"],
                ["用途", "供 L 的 g（token 單價下跌趨勢）每月追蹤；g 的計算與參數更新由 chat 端與 Andy 判斷"],
                ["全部模型快照", f"data/price_track/{month}.csv（{len(rows)} 個模型）"]]:
        s3.append(row)

    table = "\n".join(f"{r['id']}｜in {r['in_per_m']}｜out {r['out_per_m']}｜cache {r['cache_read_per_m']}｜{r['status']}｜Δin {r['chg_in']}｜Δout {r['chg_out']}｜建立 {r['created']}"
                      for r in lines)
    summary, cost = summarize(f"資料月份 {month}，比較基準 {prev_month or '無（首月）'}。\n下架：{', '.join(gone) or '無'}\n\n{table}")
    s3.append(["API 摘要費用（美元）", round(cost, 3)])
    os.makedirs(f"{HERE}/out", exist_ok=True)
    wb.save(f"{HERE}/out/{month}.xlsx")
    n_new = sum(1 for r in lines if r["status"] == "新上架")
    n_chg = sum(1 for r in lines if r["status"] == "調價")
    md = [f"# token 牌價追蹤｜{month}", "", f"- 全部模型 {len(rows)}；觀察清單 {len(lines)}；比較基準 {prev_month or '無（首月，只建基準）'}",
          f"- 新上架 {n_new}、調價 {n_chg}、下架 {len(gone)}；API 摘要費用約 US${cost:.3f}",
          "- 來源：OpenRouter 公開 API（轉售平台牌價，[Interested-party]；重要價格須以原廠價目頁覆核）", "", "## 摘要（API 產生）", "", summary]
    open(f"{HERE}/out/{month}.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md[:5]))


if __name__ == "__main__":
    main()

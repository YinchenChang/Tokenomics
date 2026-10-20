# v17.1 (work order docs/workorders/20261020_v17.1_文字修補.md, branch claude/v17-1-text): stale-label text repair after v17.0 (F1／F2 main basis).
# PATCH-level engineering change (CLAUDE.md 4a): labels and explanation text only.  No value, formula, blue input or named range changes.
#   W1  L1 B114 / Cap_In A314: "（F2 對照；" -> "（v17.0 起主口徑：F2 已採用，未回應依預設，可撤回；"
#   W2  L1 B115 / Cap_In A315: "（F1 對照）" -> "（v17.0 起主口徑：F1 已採用，未回應依預設，可撤回）"
#   W3  Cap_In G242: opening re-pointed to the current reading; the v5.35 sentence kept verbatim and marked as no longer applicable
#   W4  Cap_In G243: "【v5.35 原說明，已不適用】" prefix
#   W5  Cap_In G232／G233: hard-coded v5.35 values replaced by "數值以 C–E 欄為準（v17.0：…）" (v17.0 values of C232:E233, rounded to 4 decimals)
#   W6  Cap_In G226: opening points to C226:E226 (v17.0 values), original setting kept
#   r1 (chat review of PR #135): W1 reworded (L1_LTotalDisc is a component, not the main basis); W8 L1 B89, W9 L1 H89, W10 L1 I107, W11 Cap_In O241, W12 Cap_In G237, W13 Gov_Map E (Astra row), W14 Cap_In G242 divider
#   W7  Gov_Map M (row of Cap_In C280, GM669): range text 3.3–5.9 $/M, old range kept in the text and in Cap_In G280
# These cells are Excel-owned text (Cap_In is rebuilt but its explanation columns carry the earlier modules' appends), so every edit is a guarded
# replacement of the exact old opening; an already-applied cell is skipped (idempotent).  Run last in build.py, after v1700.apply.
V = "v17.1"
VERSION = "20261020_Tokenomics_v17.1"      # single source of the version string: README!B5 and README!A1 (finish.readme); work order names 20261021, build day is 2026-10-20
WO = "工作單 docs/workorders/20261020_v17.1_文字修補.md"

import v1700

MINUS = "−"
EDITS = [
    # (id, sheet, how to find the cell, old opening (exact prefix or substring), new text, mode)
    ("W1a", "L1", ("B", "L1_LTotalDisc"), "（F2 對照；WACC 折現）", "（2025＝第 0 年；F2 已採用＝v17.0 起 L 用折現版，未回應依預設，可撤回。回本判讀主口徑是世代起點＋折現 L1_LTotalFleetVDisc，本列為其分項對照；WACC 折現）", "sub"),
    ("W2a", "L1", ("B", "L1_LReqFleet_IdNoK"), "（F1 對照）", "（v17.0 起主口徑：F1 已採用，未回應依預設，可撤回）", "sub"),
    ("W1b", "Cap_In", "A314", "（F2 對照；WACC＝Inputs E28／D28／F28）", "（2025＝第 0 年；F2 已採用，未回應依預設，可撤回；主口徑為世代起點＋折現 L1_LTotalFleetVDisc，見 L1 第 116 列（Cap_In 第 325 列）；WACC＝Inputs E28／D28／F28）", "sub"),
    ("W2b", "Cap_In", "A315", "（F1 對照）", "（v17.0 起主口徑：F1 已採用，未回應依預設，可撤回）", "sub"),
    ("W3", "Cap_In", "G242", "文字；基準 0.6426 ≥ 0.3645 → 回本（L_total 口徑）",
     "文字；現行判讀見 C 欄（v17.0：未定，L 0.759 對所需 L 0.756）｜【v5.35 原說明，已不適用】基準 0.6426 ≥ 0.3645 → 回本（L_total 口徑）", "prefix"),
    ("W14", "Cap_In", "G242", "所需 L 0.756）｜【v5.35 原說明", "所需 L 0.756）｜【以下為歷次修訂紀錄，現行判讀以本格開頭與 C 欄為準】｜【v5.35 原說明", "sub"),
    ("W4", "Cap_In", "G243", "文字；基準 0.6426 ≥ 0.5237 → 回本（L_total 口徑）",
     "文字；【v5.35 原說明，已不適用】基準 0.6426 ≥ 0.5237 → 回本（L_total 口徑）", "prefix"),
    ("W8", "L1", ("B", "L1_LReqFleet"), "判讀只用恆等式讀法 L1_LReqFleet_Id", "判讀只用恆等式讀法；v17.0 起主口徑為不含 κ 的 L1_LReqFleet_IdNoK（F1），含 κ 的 L1_LReqFleet_Id 為對照", "sub"),
    ("W9a", "L1", ("H", "L1_LReqFleet"), "與 L_total 並列判讀（Cap_In 第 242 列）", "與 L_total 並列判讀（舊讀法；v17.0 起 Cap_In 第 242 列改為 L1_LTotalFleetVDisc 對 L1_LReqFleet_IdNoK）", "sub"),
    ("W9b", "L1", ("H", "L1_LReqFleet"), "恆等式讀法見 L1_LReqFleet_Id", "恆等式讀法見 L1_LReqFleet_IdNoK（主口徑）與 L1_LReqFleet_Id（含 κ，對照）", "sub"),
    ("W10", "L1", ("I", "L1_LReqFleet_Id"), "與 L1_LReqFleet（字面口徑）並列", "（字面讀法的對照說明；現行判讀見 Cap_In 第 242 列）與 L1_LReqFleet（字面口徑）並列", "prefix"),
    ("W11", "Cap_In", "O241", "契約已定恆等式讀法 L1_LReqFleet_Id", "契約已定恆等式讀法（v17.0 起主口徑 L1_LReqFleet_IdNoK；含 κ 的 L1_LReqFleet_Id 為對照）", "sub"),
    ("W12", "Cap_In", "G237", "L_total 基準 0.6426 落在其內", "L_total 基準（v17.0：0.6595，以 C 欄為準）落在其內", "sub"),
    ("W5a", "Cap_In", "G232", "壽命期內牌價相對第 0 年的連續平均；基準 0.7412、D 0.4762、E 1.1618",
     "壽命期內牌價相對第 0 年的連續平均；數值以 C–E 欄為準（v17.0：基準 0.7637、D 0.5511、E 1.1618）", "exact"),
    ("W5b", "Cap_In", "G233", "前 T1 年中階牌價、之後 ρ × 中階牌價的連續平均；基準 0.6426、D 0.342、E 1.1618",
     "前 T1 年中階牌價、之後 ρ × 中階牌價的連續平均；數值以 C–E 欄為準（v17.0：基準 0.6595、D 0.3963、E 1.0964）", "exact"),
    ("W6", "Cap_In", "G226", "藍字三格（登錄 Gov_Map）：基準 " + MINUS + "0.10、低 " + MINUS + "0.25、高 +0.05。",
     "藍字三格（登錄 Gov_Map）；現值以 C226:E226 為準（v17.0：基準 " + MINUS + "0.09、低 " + MINUS + "0.20、高 +0.05）｜原始設定：基準 " + MINUS + "0.10、低 " + MINUS + "0.25、高 +0.05。", "prefix"),
]
GM_OLD = "2.089–16.33 $/M（低、高端的層級對應見註）"
GM_NEW = "3.3–5.9 $/M（v15.2 B2 用量加權；舊區間 2.089–16.33 為在售天數加權，保留於 Cap_In G280）（低、高端的層級對應見註）"


def _l1_cell(wb, col, name):
    ws = wb["L1"]
    r = [x for x in range(5, ws.max_row + 1) if ws.cell(x, 1).value == name]
    assert len(r) == 1, (name, r)
    return ws[f"{col}{r[0]}"]


def _apply(cell, old, new, mode):
    cur = cell.value
    assert isinstance(cur, str) and not cur.startswith("="), (cell.coordinate, cur)
    if new in cur:
        return 0                                     # already applied
    if mode == "exact":
        assert cur == old, (cell.coordinate, cur)
        cell.value = new
    elif mode == "prefix":
        assert cur.startswith(old), (cell.coordinate, cur[:80])
        cell.value = new + cur[len(old):]
    else:
        assert cur.count(old) == 1, (cell.coordinate, cur)
        cell.value = cur.replace(old, new)
    return 1


def apply(wb):
    log = {}
    for wid, sh, loc, old, new, mode in EDITS:
        cell = _l1_cell(wb, *loc) if isinstance(loc, tuple) else wb[sh][loc]
        log[wid] = _apply(cell, old, new, mode)
    g = wb["Gov_Map"]
    rows = [r for r in range(5, g.max_row + 1) if g[f"C{r}"].value == "Cap_In" and g[f"D{r}"].value == "C280"]
    assert len(rows) == 1, rows
    log["W7"] = _apply(g[f"M{rows[0]}"], GM_OLD, GM_NEW, "exact")
    log["W7_row"] = rows[0]
    log["W13"] = _apply(g[f"E{rows[0]}"], "；在售天數加權）", "；用量加權）", "sub")      # r1: same wording as Cap_In A280
    return log


# ================================================================== README
README_VERSION = (VERSION + "（修補版，工程類：" + WO + "——只改標籤與說明文字：L1 第 114 列與 Cap_In A314 註明『分項對照，主口徑為 L1_LTotalFleetVDisc』、L1 第 115 列與 Cap_In A315 改標『v17.0 起主口徑』；L1 B89／H89／I107、Cap_In O241／G237 與 Gov_Map（Astra 列）E 欄的舊口徑說明改為現行說明；Cap_In G242／G243 加註『v5.35 原說明，已不適用』；G232／G233／G226 的寫死舊值改指向 C–E 欄現值；"
                  "Gov_Map（Cap_In C280）範圍文字改為 3.3–5.9 $/M。數值、公式、藍字輸入、具名範圍不變）。以下為 "
                  + v1700.README_VERSION.split("_Tokenomics_", 1)[1])
_T = v1700.README_TITLE
README_TITLE = V + _T[len(v1700.V):]
README_ROW = ("v17.1 文字修補",
              "只改標籤與說明文字，不改任何數值、公式、藍字輸入或具名範圍：v17.0 已採用 F1／F2，但 L1 第 114／115 列、Cap_In G242／G243／G232／G233／G226 與 Gov_Map（Cap_In C280）仍寫「對照」或保留 v5.35 舊數字；"
              "本版改為現行口徑或標明『已不適用』。細節見工作單 docs/workorders/20261020_v17.1_文字修補.md。")

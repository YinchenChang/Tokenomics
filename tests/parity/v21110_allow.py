"""v21.11（v22.0 B1，Terra 第四層級結構一）之後，舊測試讀取「世代 × 層級」位置時的對照工具（R10）。

v21.11 把 Perf／Perf_Batch／Training（及 _Prod 鏡像）由 15 欄（C–Q＝5 世代 × 3 層級，索引 3×(g−1)＋t）改為 20 欄
（C–V＝5 世代 × 4 層級，索引 4×(g−1)＋t），Perf_Batch FP8 情境欄 R／S → W／X；DRV_*／TRN_* 名稱由 1×15 改 1×20。
所有既有值不變（tools/cmp_relayout.py 逐鍵核對；test_v21110 看守）。舊測試寫死的位置以本模組換算，期望值本身不改。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "builder"))
import tiers  # noqa: E402

V2110 = Path(__file__).resolve().parents[2] / "model" / "archive" / "20261104_Tokenomics_v21.10.xlsx"
WIDE = ("DRV_", "TRN_")      # 形狀 1×15 → 1×20 的名稱前綴


def pos(old_pos: int) -> int:
    """15 欄位置（1 起算）→ 20 欄位置。"""
    return tiers.old_to_new_col(old_pos + 2) - 2


def col(sheet: str, letter: str) -> str:
    """Perf／Perf_Batch／Training 的舊欄字母 → 新欄字母（其他頁原樣）。"""
    from openpyxl.utils import column_index_from_string as CI, get_column_letter as L
    if sheet not in tiers.RELAID:
        return letter
    return L(tiers.old_col_map(sheet).get(CI(letter), CI(letter)))


def narrow(name: str, values):
    """DRV_／TRN_ 名稱的 20 欄值 → v21.10 的 15 欄排列（取 Luna／Sol／Astra 三層、依舊順序）；其他名稱原樣。"""
    if not name.startswith(WIDE) or not isinstance(values, list) or len(values) != tiers.NG * tiers.NT:
        return values
    return [values[pos(i) - 1] for i in range(1, tiers.NG * tiers.OLD_NT + 1)]


def ref_moved(name: str) -> bool:
    """v21.11 參照位址改變、但值不變的名稱：DRV_／TRN_（1×15 → 1×20）與 RNG_Dem004_*（Alloc P 節時效指紋多 62 葉格，Q 節下移 62 列）。
    舊測試的「參照位址不變」檢查略過這些名稱；它們對 v21.10 的逐值相等由 test_v21110 以鍵對齊比較看守。"""
    return name.startswith(WIDE) or name.startswith("RNG_") or name in B2_SHAPE      # v22.0：Alloc O 節依字母序插入 Terra 區間名稱，其下 RNG_ 列下移（值由 gen_ranges --check／test_v22000 看守）


# v21.12（v22.0 B2，R10）：1×3 → 1×4（Terra 欄）與 1×13 → 1×14（Terra 候選列）的名稱，值的前 3／13 格不變（test_v21120 看守）
B2_SHAPE = ({"B4_PriceIn", "B4_PriceCache", "B4_PriceOut", "B4_Life", "B4_MixPaid", "B4_MixFree", "B4_ISL", "B4_OSL", "B4_EffIn", "B4_EffCache",
             "B4_EffOut", "B4_EffRef", "B4_FrontRef", "B5_H50", "B5_H50Lo", "B5_H50Hi"}
            | {f"B4_Mkt{x}" for x in ("Model", "Vendor", "Country", "Open", "In", "Cache", "Out", "Peak", "Index", "China")})
B2_NEW = {"B4_MixPaid25", "B4_MixFree25", "B4_TerraFam", "CAP_TokGWPaidMix25", "B5_SuccOvr_Terra"}      # v21.12 新增的內部名稱（非契約）
# v22.0（B3，R10）：新增的 107 個名稱（Terra 契約名稱與新 SRC 紀錄；清單見 fixtures/v22000_new_names.json，值由 test_v22000 看守）。
# 舊測試的「名稱不增不減」檢查把它們與 B2_NEW 一起略過。
import json as _json
from pathlib import Path as _Path
B3_NEW = set(_json.loads((_Path(__file__).resolve().parent / "fixtures" / "v22000_new_names.json").read_text(encoding="utf-8"))["names"])
B2_NEW = B2_NEW | B3_NEW

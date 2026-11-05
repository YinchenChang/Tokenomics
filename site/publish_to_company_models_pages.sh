#!/usr/bin/env bash
# 把 Tokenomics 靜態網站（site/dist）發布到 company-models 的 gh-pages 分支 tokenomics/ 子目錄：
#   https://yinchenchang.github.io/company-models/tokenomics/
# 做法同 company-models 的 markets/invest_map/publish_map_only.sh：在最新 origin/gh-pages 上「追加一個 commit」，
# 只新增或取代 tokenomics/，不 force、不動其他目錄（index.html、models/、wattonomics/、siliconomics/）。
# 不可改用 company-models 的 publish_pages.sh：它以全新歷史 force 覆寫整個 gh-pages。
#
# 預設為 dry run：建置 → 在臨時 worktree 放入 tokenomics/ → 列出 gh-pages 上會變動的檔案 → 停止（不 commit、不 push）。
# 實際發布加 --push；需要 Andy 明確指示發布（Project Instructions 第 6 條）。
#
# 用法（在 Tokenomics repo 任一工作目錄）：
#   bash site/publish_to_company_models_pages.sh                    # dry run
#   bash site/publish_to_company_models_pages.sh --push             # 發布
# 選項：--company-models <路徑>（預設 $COMPANY_MODELS，或與 Tokenomics 同層的 company-models）；--skip-build（直接用現有 site/dist）
set -euo pipefail

PUSH=0
BUILD=1
TK_ROOT=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)
CM="${COMPANY_MODELS:-$TK_ROOT/../company-models}"
while [ $# -gt 0 ]; do
  case "$1" in
    --push) PUSH=1 ;;
    --skip-build) BUILD=0 ;;
    --company-models) CM="$2"; shift ;;
    *) echo "未知選項：$1" >&2; exit 2 ;;
  esac
  shift
done
CM=$(git -C "$CM" rev-parse --show-toplevel)
DIST="$TK_ROOT/site/dist"

# 1) 建置（讀 model/CURRENT）並檢查頁面齊全
if [ "$BUILD" = 1 ]; then
  python3 "$TK_ROOT/site/build_site.py" --out "$DIST"
fi
python3 - "$DIST" <<'PY'
import json, os, sys
d = sys.argv[1]
meta = json.load(open(os.path.join(d, "build.json"), encoding="utf-8"))
missing = [p["file"] for p in meta["pages"] if not os.path.exists(os.path.join(d, p["file"]))]
if missing or not os.path.exists(os.path.join(d, "index.html")):
    sys.exit(f"停止：site/dist 缺頁：{missing or ['index.html']}")
extra = sorted(set(os.listdir(d)) - {p["file"] for p in meta["pages"]} - {"build.json"})
if extra:
    sys.exit(f"停止：site/dist 有清單外的檔案（請重建）：{extra}")
print(f"頁面檢查通過：{len(meta['pages'])} 頁（{meta['excel']}，{meta['version']}，master {meta['master']}，建置 {meta['date']}）")
PY
VER=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1],encoding='utf-8'))['version'])" "$DIST/build.json")
SRC=$(python3 -c "import json,sys;m=json.load(open(sys.argv[1],encoding='utf-8'));print(m['master'] if m['on_master'] else m['head'])" "$DIST/build.json")

# 2) 在 gh-pages 最新版上，只取代 tokenomics/
git -C "$CM" fetch -q origin +refs/heads/gh-pages:refs/remotes/origin/gh-pages
BASE=$(git -C "$CM" rev-parse --short origin/gh-pages)
WT=$(mktemp -d)
git -C "$CM" worktree add -q --detach "$WT" origin/gh-pages
trap 'git -C "$CM" worktree remove --force "$WT" >/dev/null 2>&1 || true; rm -rf "$WT"' EXIT
rm -rf "$WT/tokenomics"
mkdir -p "$WT/tokenomics"
cp "$DIST"/*.html "$DIST/build.json" "$WT/tokenomics/"
git -C "$WT" add -A tokenomics

# 3) 安全檢查：變動只能在 tokenomics/ 之內
CHANGED=$(git -C "$WT" diff --cached --name-status)
if [ -z "$CHANGED" ]; then
  echo "gh-pages（$BASE）上的 tokenomics/ 已與本次建置相同，沒有要發布的變動。"
  exit 0
fi
OUTSIDE=$(git -C "$WT" diff --cached --name-only | grep -v '^tokenomics/' || true)
if [ -n "$OUTSIDE" ]; then
  echo "停止：有 tokenomics/ 以外的變動：" >&2
  echo "$OUTSIDE" >&2
  exit 1
fi
echo "gh-pages 基準：origin/gh-pages $BASE；會變動的檔案（A 新增、M 修改、D 刪除）："
echo "$CHANGED" | sed 's/^/  /'
git -C "$WT" diff --cached --stat | tail -1
echo "其他目錄（index.html、models/、wattonomics/、siliconomics/ 等）不變。"

if [ "$PUSH" != 1 ]; then
  echo "dry run：未 commit、未 push。實際發布：bash site/publish_to_company_models_pages.sh --push"
  exit 0
fi

# 4) 發布：追加一個 commit，一般 push（不 force）；被拒（他人先推）時停止，重跑本程式即可
# 署名行：環境變數 COMMIT_TRAILERS（多行，例：Co-Authored-By 與 Claude-Session）由發布端提供；未設定則不加
MSG="發布 Tokenomics 靜態網站 $VER（來源 Tokenomics $SRC；只更新 tokenomics/）"
if [ -n "${COMMIT_TRAILERS:-}" ]; then MSG="$MSG"$'\n\n'"$COMMIT_TRAILERS"; fi
git -C "$WT" -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "$MSG"
if ! git -C "$WT" push -q origin HEAD:gh-pages; then
  echo "停止：push 被拒（gh-pages 已有新 commit）。未 force；請重跑本程式。" >&2
  exit 1
fi
echo "已發布 Tokenomics $VER 到 gh-pages：$(git -C "$WT" rev-parse --short HEAD)（基準 $BASE）"
echo "https://yinchenchang.github.io/company-models/tokenomics/"

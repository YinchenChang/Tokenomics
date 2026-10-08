#!/usr/bin/env bash
# v5.23 (工單 3.1，工程類)：在 CI runner 安裝 headless 重算所需的 LibreOffice Calc。
# 原因：v5.22 push run 189（a5931f0）的 scenarios 第 4 片在此步驟下載 libreoffice-core（43 MB）耗時約 19 分鐘，job 在 30 分鐘逾時被取消，與內容無關。
# 做法：只裝 libreoffice-calc 與其必要相依（--no-install-recommends，不連帶 gstreamer 等推薦套件）；apt 加重試與逾時；
# 整個安裝（update＋install）每次嘗試有總時限，失敗時重試一次（以 shell 迴圈實作，不引入第三方 action）。
# 若 headless 重算缺少必要套件（例如 python3-uno、字型），只補必要者並寫入 PKGS。
# v5.27 (工單 3.1)：apt 單次逾時 90／180 → 180／420 秒、嘗試次數 2 → 3；成功分支以 command -v soffice 驗證，找不到即 exit 1
# （CI 步驟另加 shell: bash，使 pipefail 生效，本腳本的失敗結束碼不被 tee 遮蓋）。
set -u
PKGS="libreoffice-calc"
APT_OPTS=(-o Acquire::Retries=3 -o Acquire::http::Timeout=30 -o Acquire::https::Timeout=30)
for attempt in 1 2 3; do
  start=$(date +%s)
  if sudo timeout 180 apt-get update -q "${APT_OPTS[@]}" && \
     sudo timeout 420 apt-get install -y -q --no-install-recommends "${APT_OPTS[@]}" $PKGS; then
    if ! command -v soffice >/dev/null 2>&1; then
      echo "apt-get 回報成功，但找不到 soffice（PATH=${PATH}）" >&2
      exit 1
    fi
    echo "LibreOffice 安裝成功：第 ${attempt} 次嘗試，$(( $(date +%s) - start )) 秒；soffice＝$(command -v soffice)"
    soffice --version
    echo "已安裝套件數（libreoffice／uno／fonts 相關）：$(dpkg -l | grep -E '^ii +(libreoffice|python3-uno|libuno|uno-|fonts-)' | wc -l)"
    dpkg -l | grep -E '^ii +(libreoffice|python3-uno|libuno|uno-|fonts-)' | awk '{print $2}' | tr '\n' ' '; echo
    exit 0
  fi
  echo "LibreOffice 安裝失敗（第 ${attempt} 次嘗試，$(( $(date +%s) - start )) 秒）" >&2
done
exit 1

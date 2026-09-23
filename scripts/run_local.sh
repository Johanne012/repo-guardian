#!/usr/bin/env bash
# تشغيل محلي لنظام المراقبة
set -euo pipefail
cd "$(dirname "$0")/.."

export GITHUB_OWNER="${GITHUB_OWNER:-Johanne012}"
export REPORT_PATH="${REPORT_PATH:-report.json}"
export SUMMARY_PATH="${SUMMARY_PATH:-summary.md}"
export AUTO_ISSUE="${AUTO_ISSUE:-false}"

if [[ -z "${GITHUB_TOKEN:-}${GH_TOKEN:-}" ]]; then
  echo "تحذير: لا يوجد GITHUB_TOKEN — سيتم جلب المستودعات العامة فقط"
fi

echo "→ Monitor"
python3 agent/monitor.py || true

echo "→ Decision"
python3 agent/decision.py

echo "→ Healer (AUTO_ISSUE=$AUTO_ISSUE)"
python3 agent/healer.py

echo "→ Notify"
python3 agent/notify.py || true

echo "تم. راجع report.json و summary.md"

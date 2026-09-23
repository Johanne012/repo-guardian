# STATUS — Repo Guardian

**آخر تحديث:** 2026-09-23 14:05 CET

## مكتمل

| البند | الحالة |
|------|--------|
| إعادة تسمية → `agentic-ai` | ✅ |
| أرشفة `ZYNTRA-storage` | ✅ |
| إغلاق Issue الأرشفة | ✅ |
| تعليم `forge-agent` Deprecated | ✅ |
| Issue لإعادة تسمية `Repository-name-api-server` | ✅ |
| محرك Monitor (عام + خاص) | ✅ |
| Healer مع dedupe | ✅ |
| Decision + notify.flag | ✅ |
| Discord/Slack webhooks (اختياري) | ✅ |
| Memory module | ✅ |
| GitHub Actions يومي | ✅ |
| LICENSE + .gitignore + run_local.sh | ✅ |

## ينتظر المالك (يدوي)

1. أرشفة `forge-agent` من Settings → Danger Zone
2. إعادة تسمية `Repository-name-api-server` (خاص)
3. (اختياري) إضافة secrets في repo-guardian:
   - `DISCORD_WEBHOOK_URL`
   - `SLACK_WEBHOOK_URL`

## تشغيل

- تلقائي: يومياً 06:00 UTC
- يدوي: Actions → Repo Guardian Health Check → Run workflow
- محلي: `bash scripts/run_local.sh`

## سياسة التنبيه

Critical فقط → Issue (+ webhook إن وُجد)  
Warning → سجل فقط

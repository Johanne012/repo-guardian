# Repo Guardian

[![Health Check](https://github.com/Johanne012/repo-guardian/actions/workflows/health-check.yml/badge.svg)](https://github.com/Johanne012/repo-guardian/actions/workflows/health-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

نظام مراقبة ذاتي لمستودعات GitHub — يراقب، يحلل، ينشئ Issues عند الحاجة، ويرسل تنبيهات **فقط في الحالات الحرجة**.

## ماذا يفعل؟

1. **Monitor** — يجلب المستودعات ويفحص Vercel
2. **Decision** — يصنّف Critical / Warning / OK
3. **Healer** — ينشئ Issues (مع منع التكرار)
4. **Notify** — Discord/Slack اختياري

## التشغيل

| الحدث | الوقت |
|-------|-------|
| Schedule | يومياً 06:00 UTC |
| Manual | Actions → Run workflow |
| Local | `bash scripts/run_local.sh` |

## الأسرار (Settings → Secrets and variables → Actions)

| Secret | مطلوب؟ | الغرض |
|--------|---------|--------|
| `GUARDIAN_PAT` | مُستحسن | Personal Access Token بصلاحية `repo` لرؤية كل المستودعات (عامة + خاصة) وإنشاء Issues فيها |
| `DISCORD_WEBHOOK_URL` | لا | تنبيه Discord |
| `SLACK_WEBHOOK_URL` | لا | تنبيه Slack |

بدون `GUARDIAN_PAT` يعمل النظام على المستودعات العامة فقط (عبر fallback).

### إنشاء GUARDIAN_PAT

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token — صلاحية: **repo**
3. الصقه كـ Secret باسم `GUARDIAN_PAT` في مستودع `repo-guardian`

## الهيكل

```
agent/monitor.py decision.py healer.py notify.py memory.py
config/rules.yaml repos.yaml
.github/workflows/health-check.yml
scripts/run_local.sh
```

## المبادئ

- لا تنبيه روتيني
- Critical فقط → Issue (+ webhook)
- لا حذف/أرشفة تلقائية
- منع تكرار Issues

## الترخيص

MIT

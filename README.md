# Repo Guardian

[![Health Check](https://github.com/Johanne012/repo-guardian/actions/workflows/health-check.yml/badge.svg)](https://github.com/Johanne012/repo-guardian/actions/workflows/health-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

نظام مراقبة ذاتي لمستودعات GitHub — يراقب، يحلل، ينشئ Issues عند الحاجة، ويرسل تنبيهات **فقط في الحالات الحرجة**.

## ماذا يفعل؟

1. **Monitor** — يجلب كل المستودعات (عامة + خاصة عبر التوكن) ويفحص Vercel
2. **Decision** — يصنّف Critical / Warning / OK
3. **Healer** — ينشئ Issues للحالات الحرجة (مع منع التكرار)
4. **Notify** — Discord/Slack اختياري عبر Secrets

## التشغيل التلقائي

| الحدث | الوقت |
|-------|-------|
| Schedule | يومياً 06:00 UTC |
| Manual | Actions → Run workflow |

## التشغيل المحلي

```bash
export GITHUB_TOKEN=ghp_xxx   # اختياري للمستودعات الخاصة
bash scripts/run_local.sh
```

## الأسرار الاختيارية (Settings → Secrets)

| Secret | الغرض |
|--------|--------|
| `DISCORD_WEBHOOK_URL` | تنبيه Discord عند Critical |
| `SLACK_WEBHOOK_URL` | تنبيه Slack عند Critical |

`GITHUB_TOKEN` يُوفَّر تلقائياً من Actions.

## الهيكل

```
agent/
  monitor.py    # جمع + تحليل
  healer.py     # Issues + dedupe
  decision.py   # ملخص + notify.flag
  notify.py     # webhooks
  memory.py     # سجل القرارات
config/
  rules.yaml
  repos.yaml
.github/workflows/health-check.yml
scripts/run_local.sh
```

## المبادئ

- لا بريد/تنبيه روتيني
- Critical فقط → Issue (+ webhook)
- لا حذف ولا أرشفة تلقائية (تأكيد بشري)
- منع تكرار Issues

## الترخيص

MIT

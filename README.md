# Repo Guardian

نظام مراقبة ذاتي لمستودعات GitHub — يراقب، يحلل، ينشئ Issues عند الحاجة، ويرسل تنبيهات **فقط في الحالات الحرجة**.

## التشغيل التلقائي

GitHub Actions يعمل يومياً الساعة 06:00 UTC:

```
.github/workflows/health-check.yml
```

- يجمع بيانات كل المستودعات
- يفحص روابط Vercel
- يصنّف: Critical / Warning / OK
- ينشئ Issue تلقائياً عند Critical
- يرفع `report.json` + `summary.md` كـ Artifact

## التشغيل اليدوي

Actions → **Repo Guardian Health Check** → Run workflow

## المكونات

| الملف | الوظيفة |
|-------|--------|
| `agent/monitor.py` | جلب + تحليل |
| `agent/healer.py` | إنشاء Issues |
| `agent/decision.py` | ملخص + قرار تنبيه |
| `config/rules.yaml` | قواعد الخطورة |
| `config/repos.yaml` | أولويات المستودعات |

## المبادئ

1. لا بريد يومي/أسبوعي روتيني
2. Critical فقط → تنبيه + Issue
3. لا حذف ولا أرشفة تلقائية (تحتاج تأكيد بشري)
4. النظام يتعلم من القرارات عبر Issues المغلقة

## الترخيص

MIT

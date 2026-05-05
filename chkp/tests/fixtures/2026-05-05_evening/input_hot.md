---
project: insilver-v3
updated: 2026-05-05
---

# HOT — InSilver v3

## Now

Сесія 05.05 — **Voice reference інтегровано в core/prompt.py + merged на prod.** Базуючись на вчорашньому voice_reference архіві (60 скрінів → 7 діалогів C001-C007 + 4 extracted YAML), сьогодні зроблено:
- Ed-блок `12_voice_critical.json` (5 P0 кейсів) у `ed/suites/data/insilver/blocks/`
- Ed-інфра для dev: `BOT_PATHS["insilver_dev"]` у `ed/transports/direct.py`, `bots.yaml` запис, symlink `suites/data/insilver_dev → insilver`
- Рефактор `core/prompt.py`: 4× `+=` ланцюжок → один `SYSTEM_PROMPT` у 12 секцій, +53.5% розмір (6973 → 10709 символів). Коміт `98c7bc7`, merged dev → main → prod.

**3 gap-и закрито у промпті:** [7] no-total-without-specs, [8] lom-protocol timing, [6б] third-party items "Не знаю, це не наша". Виправлено баг — блок ЯКІСТЬ тепер у ENHANCED_SYSTEM_PROMPT (раніше додавався після експорту, не потрапляв). 4 few-shot з реальних діалогів: торг (C001), лом-timing (C003), чужий виріб (C001), браслет-замір (C006).

**Валідація:** Ed-блок 12_voice_critical на prod після rollout — 4/5 правил стабільно покращились (lom, discount, wrist, third-party voice). Total-price stochastic ~50/50. Manual smoke на @insilver_silvia_bot — 5/5 правильні відповіді (після patch'у Прикладу Г про браслет).

## Last done

**Сесія 05.05 — Ed-блок 12_voice_critical + рефактор core/prompt.py + voice integration:**
- ✅ Створено `ed/suites/data/insilver/blocks/12_voice_critical.json` — 5 P0 кейсів (no_total_price, wrist_measurement, lom_before_work, no_third_party, no_discount)
- ✅ Налаштовано Ed для dev-бота `@insilver_silvia_bot`: `BOT_PATHS["insilver_dev"]` додано в `direct.py`, `insilver_dev` запис у `config/bots.yaml`, symlink `suites/data/insilver_dev → insilver`
- ✅ Рефактор `core/prompt.py` на dev: 4× `+=` → монолітний SYSTEM_PROMPT з 12 секціями (ІДЕНТИЧНІСТЬ, 20 ПРАВИЛ, МОВА, ПОВЕДІНКОВІ, МОВНА ПОЛІТИКА, ОБМЕЖЕННЯ [6а]/[6б], ЦІНОУТВОРЕННЯ, ЛОМ-ПРОТОКОЛ, СПЕЦИФІКАЦІЯ, ЯКІСТЬ, ГОЛОС ТА СТИЛЬ, ПРИКЛАДИ)
- ✅ Виправлено bug — блок ЯКІСТЬ тепер у ENHANCED_SYSTEM_PROMPT
- ✅ Уточнено правило 13: order_id формат YYYYMMDD-N (приклад 20260315-7)
- ✅ Додано 4 few-shot приклади з C001/C003/C006 — дослівні формулювання Влада
- ✅ Smoke на `@insilver_silvia_bot` — 5/5 кейсів коректні після patch'у Прикладу Г
- ✅ Merge: dev → main → prod, рестарт `insilver-v3.service`, Ed regression — 4/5 стабільно покращені
- ✅ Коміт рефактору `98c7bc7`, chkp коміт `c6704d5`

## Next

**Дрібниці й оптимізації (не критичні):**
1. **Підсилити anti-russism у мовній політиці** — баг "какой"/"какій" з'явився 1 раз з 2 прогонів у `no_third_party_pricing` після рефактору. Можливо посилити секцію [3]/[5] ще одним правилом або винести anti-russism у кінець промпту до прикладів.
2. **Додатковий few-shot для total-after-specs** — `no_total_price_before_specs` зараз stochastic ~50/50. Додати приклад "клієнт назвав масу — все одно не давати total без довжини+замка".
3. **Ed reset_command для блоку 12** — direct transport state-leak'ає user_id 999999 між кейсами. Додати reset у блок або в loader.
4. **Voice rubric для Ed** — поточна generic insilver-rubric (12 criteria: price_transparency, offers_variants, etc) не оцінює наші `expected_behavior`. Зробити окрему рубрику `voice_rubric.py` для блоку 12.
5. **Відповіді Влада на 5 questions_for_vlad** — карта C001 vs C006 (різні правила?), передоплата правило, lom rate 85 vs 87, military greeting, recognition повторного клієнта.

## Blockers
- ⏳ **Влад відповіді на questions_for_vlad** (estimate: 0.5-1 день) — тільки для P3 пунктів, не блокує основні задачі

## Infrastructure issues (окремо в backlog)
- 🔴 **insilver-v3-dev watchdog timeout** — 1522 рестарти за добу, кожні ~5 хв SIGABRT. Не блокер для prod (insilver-v3 стабільний since 2026-05-02), але dev майже непридатний для довгих тестів. Окрема задача.

---
project: insilver-v3
updated: 2026-05-05
---

# HOT — InSilver v3

## Now

Сесія 05.05 — **Voice Reference Extraction завершено.** 60 скрінів Влада з TG експортовано → анонімізовано й організовано у 7 діалогів (C001_yevhen.md, C002_natalia.md, ..., C007_dmytro.md). **Архітектура:**
- `private/raw/` — оригінальні скрін-архіви (gitignored)
- `private/archive/` — анонімізовані діалоги з .md по 1 діалогу, 4 YAML-блоки (client_persona, interaction_pattern, product_preference, communication_style) + questions_for_vlad (5 питань для уточнення)
- `private/client_keymap.yaml` — TODO: заповнити після скрінів (mapping ID → real client data)
- `data/docs/archive/voice_reference_extracted_2026-05-05.md` — публічна зведена версія (анонімізована, без приватних даних)

**Результат:** 4 extracted YAML блоки × 7 клієнтів + 5 питань Владу на уточнення (у questions_for_vlad). **Статус:** готово до review Vladом. **Коміт:** 1106b8b (not pushed). **Next:** заповнити client_keymap.yaml, задати Владу 5 питань, отримати відповіді, оновити ed_assertion_candidates + добавити блок 12_voice_consistency у Ed.

## Last done

**Сесія 05.05 — Voice Reference Extraction (60 скрінів) → 7 анонімізованих діалогів + YAML архітектура**

- ✅ **60 скрінів Влада експортовано з TG** — архів у `private/raw/` (gitignored)
- ✅ **7 анонімізованих діалогів створено** (C001_yevhen.md, C002_natalia.md, C003_iryna.md, C004_oksana.md, C005_andriy.md, C006_pavlo.md, C007_dmytro.md)
- ✅ **YAML структура кожного діалогу:** 4 extracted блоки (client_persona, interaction_pattern, product_preference, communication_style) + questions_for_vlad
- ✅ **client_keymap.yaml шаблон створений** — TODO: заповнити з приватних даних
- ✅ **voice_reference_extracted_2026-05-05.md** — публічна версія (анонімізована)
- ✅ **Всі шаблони українською** — без fallback англійськогооо
- ✅ **Ціни вибрані історичні** — історичні коефіцієнти з pricing.json, стабільні
- ✅ **Коміт 1106b8b** (main, not pushed)
- ✅ **ed_assertion_candidates.json підготований** —待機 на відповіді Влада

## Next

**Фаза 2: Vladом review + ed/12_voice_consistency block:**

1. **Заповнити `private/client_keymap.yaml`** з оригінальних скрінів (ID → real client name/phone/notes)
2. **Задати Владу 5 питань** з questions_for_vlad — отримати відповіді
3. **Оновити ed_assertion_candidates.json** на основі відповідей
4. **Добавити блок 12_voice_consistency у Ed QA** (`ed/suites/data/insilver/blocks/12_voice_consistency.json`) з multi-client use cases
5. **Запустити Ed блок 12** — дебаг multi-turn, проверка consistency
6. **Push коміту 1106b8b** на GitHub з моменту коли Ed green

**Резервні завдання (паралельна трек):**
- P1.4 Sam NBLM diagnostic (待機 на Sam-session)
- Side-effect (а): PROMPT.md git add+commit у chkp.py
- Side-effect (б): pre-push hook .jpg/.jpeg/.png false positive

## Blockers

- 待機 **Vladом відповіді на 5 питань** з questions_for_vlad (estimate: 0.5–1 день)
- 待機 **Ed блок 12 реалізація** (потребує структури multi-turn test cases)

## Active branches

- **insilver-v3/main (prod):** cf98f3f, GitHub, push-protected
- **insilver-v3-dev/main (dev):** 538602e, GitHub, sync'd with prod
- **insilver-v3/WIP (work-in-progress):** 1106b8b (not pushed, voice reference extraction)

## Open questions

- Яка структура questions_for_vlad матиме вплив на ed_assertion_candidates.json?
- Чи потрібна окрема таблиця mapping ID → real client data у client_keymap.yaml?
- Чи Ed блок 12 матиме multi-turn або single-turn структуру?

## Reminders

- **Voice reference extraction**: 60 скрінів → 7 діалогів → YAML + ed_assertion_candidates → Ed блок 12
- **Приватні дані:** `private/raw/`, `private/archive/client_keymap.yaml` — gitignored, НЕ синхронізуються на GitHub
- **Публічна версія:** `data/docs/archive/voice_reference_extracted_2026-05-05.md` — анонімізована, для потреб тестування
- **Коміт 1106b8b:** чекайте review Влада перед push
- **Наступна сесія:** читати HOT.md + WARM.md + private/archive/questions_for_vlad.md
- **Беклог-пункт 'InSilver voice reference extraction (2026-04-26)':** закритий після Vladом review
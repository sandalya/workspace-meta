---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

WARM diff-mode v3.5 (warm_ops) запущено в продакшені на insilver-v3. Парсер + серіалізатор + 5 операцій (touch/update_field/add/move_to_cold/replace_body) повністю протестовані: 16/16 unit-тестів, backward-compat з legacy warm field. Перший прод-чекпоінт (commit 4580c35) показав економію 16k→3.4k tokens у WARM, чекпоінт завершився за 15с замість 5хв. JSON malformed на першому запуску самопоправився на retry — кандидат у P3 уроки. Архітектура ready для масштабування на інші проекти (garcia, abby-v2, ed, sam).

## Last done

**2026-05-05** — WARM diff-mode v3.5 інтеграція + фінальне тестування (Sprint A завершено):

- **warm_ops парсер (meta/chkp/warm_ops.py):** Реалізовано 5 операцій: touch (update last_touched), update_field (status/tags), add (нові блоки), move_to_cold (архів), replace_body (оновлення контенту). Серіалізатор повністю обертає операції назад у YAML/markdown. Backward-compat: if WARM не має field (legacy), treat as default (status=active, tags=[], last_touched=None).

- **Unit-тестування:** 16/16 тестів на parse/serialize/apply для всіх операцій. Coverage: edge cases (empty tags, duplicate ops, malformed YAML). Сценарії: touch existing block, add new block after/before, move to cold з валідацією exists, replace_body з збереженням YAML header.

- **Перший прод-чекпоінт (insilver-v3, commit 4580c35):** chkp викликано зі стандартною сесією. Результат: WARM output скоротився з 16k до 3.4k tokens (79% економія через diff-mode). Час чекпоінту: 15 сек замість 5 хвилин при legacy full-WARM. JSON response_metadata malformed на першому виклику (`unexpected character at line 1 column 17`), але потім автоматично retry повернув чистий JSON. Явно документовано у COLD як P3 потреба (retry-loop improvement).

- **Verifikacija на інших проектах:** garcia, abby-v2, ed, sam — протестовані локально (dry-run). Всі операції парсяться правильно, не видно несумісностей. Ready для включення в обовʼязковий workflow.

- **Prompt caching P2 закриття (попередня сесія):** smoke test 1+2 показали cache miss через WARM волатильність. Висновок: diff-mode НЕ вирішує caching (SYSTEM+MEMORY<1024 tokens мінімум), потреба інших підходів (COLD frozen split, output streaming). Beta header залишено для майбутніх експериментів.

## Next

1. **WARM diff-mode масштабування (2-3 год, P1):**
   - garcia: `chkp garcia "warm_ops інтеграція" "масштабування" ""`
   - abby-v2: `chkp abby-v2 "warm_ops інтеграція" "масштабування" ""`
   - ed: `chkp ed "warm_ops інтеграція" "масштабування" ""`
   - sam: `chkp sam "warm_ops інтеграція" "масштабування" "zombie external_stop pending"`
   - Перевірити що tokens скорочуються >50% на кожному проекті

2. **JSON malformed retry-loop (1 год, P3):**
   - Додати explicit retry логіку в chkp.py при JSONDecodeError
   - Max retries=2, exponential backoff (1s, 2s)
   - Документувати у WARM/Компоненти: JSON graceful degradation

3. **Optional — Sam external_stop zombie fix (15 хв, P3, з попередньої сесії):**
   - `systemctl restart sam.service`
   - Перевірити лог, чи zombie повернувся

4. **Optional — Sprint C/D вибір:**
   - Після масштабування WARM diff-mode (якщо все стабільно)
   - Sprint C: Voice extraction (2h) або Sprint D: Sam evals (3h)

## Blockers

Немає активних блокерів. JSON malformed на першому чекпоінті — виявлено, на фіксі (P3).

## Active branches

- meta: main (v3.5 warm_ops stable, готово до масштабування)
- insilver-v3: main (commit 4580c35, перший прод warm_ops, monitored)
- garcia, abby-v2, ed, sam: main (локальні dry-run OK, чекають чекпоінтів)

## Open questions

- JSON malformed на першому чекпоінті: AI bug в claude.ai response_metadata formatting, або edge case у chkp.py JSON parsing?
- Чи 79% token економія стабільна на всіх проектах, чи залежить від розміру WARM?
- Zombie external_stop у sam — локальна Pi5 issue або cross-project pattern? (scheduled для завтра ранок)

## Reminders

- WARM diff-mode v3.5 = Sprint A завершено. Наступна: масштабування + P3 cleanup.
- Сесія 05.05 кульмінація: warm_ops парсер live, first prod checkpoint positive.
- Caching архітектура (WARM diff-mode, COLD frozen) — diff-mode зробив свою роботу (79% token save), але caching як ціль закрита (потреба інших підходів).
- Kit міграція на HOT/WARM/COLD — коли буде час
- tmux-restore.sh на Pi5 — TODO 2026-05-06

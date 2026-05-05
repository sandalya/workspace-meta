---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

Проект meta — триярусна пам'ять з WARM diff-mode v3.5 (warm_ops) live у продакшені. Перший прод-чекпоінт (insilver-v3, commit 4580c35) досяг 79% token економії (16k→3.4k) на WARM output, чекпоінт за 15с замість 5хв. Архітектура: парсер (parse JSON операцій), серіалізатор (write YAML/markdown), 5 операцій (touch/update_field/add/move_to_cold/replace_body), 16/16 unit-тестів, backward-compat з legacy WARM. JSON malformed на першому запуску самопоправився на retry (P3 потреба: explicit retry-loop). Ready для масштабування на garcia, abby-v2, ed, sam.

## Last done

**2026-05-05** — WARM diff-mode v3.5 фіналізація + Sprint A завершення:

- **warm_ops парсер (meta/chkp/warm_ops.py):** Реалізовано 5 операцій (touch, update_field, add, move_to_cold, replace_body). Серіалізатор обертає операції назад у YAML/markdown. Backward-compat: якщо WARM не має field, default (status=active, tags=[], last_touched=None).
- **Unit-тестування:** 16/16 на parse/serialize/apply для всіх операцій. Coverage: edge cases (empty tags, duplicate ops, malformed YAML), 4 сценарія з реальними даними.
- **Перший прод-чекпоінт (insilver-v3):** Economia 16k→3.4k tokens (79%), 5хв→15с. JSON malformed на першому запуску, retry OK. Документовано як P3.
- **Локальна верифікація:** garcia, abby-v2, ed, sam dry-run OK, готові до чекпоінтів.
- **Prompt caching P2 закрито (попередня сесія):** Smoke test показав що diff-mode НЕ вирішує caching (SYSTEM+MEMORY<1024 мінімум), потреба COLD frozen split + output streaming.

## Next

1. **WARM diff-mode масштабування (2-3 год, P1):**
   - garcia, abby-v2, ed, sam: `chkp <project> "warm_ops масштабування" "наступний крок" ""`
   - Перевірити що tokens скорочуються >50%

2. **JSON malformed retry-loop (1 год, P3):**
   - Explicit retry у chkp.py при JSONDecodeError
   - Max retries=2, exponential backoff (1s, 2s)
   - Документувати у WARM/Компоненти

3. **Optional — Sam external_stop zombie (15 хв, P3):**
   - `systemctl restart sam.service` + лог перевірка

4. **Optional — Sprint C/D після стабілізації WARM**

## Blockers

Без активних блокерів. JSON malformed на першому чекпоінті — виявлено, на фіксі (P3).

## Active branches

- meta: main (v3.5 warm_ops stable)
- insilver-v3: main (commit 4580c35, monitored)
- garcia, abby-v2, ed, sam: main (ready для чекпоінтів)

## Open questions

- JSON malformed: AI bug у claude.ai response_metadata, чи edge case у chkp.py?
- Чи 79% token економія стабільна на всіх проектах?
- Zombie external_stop у sam — локальна issue чи cross-project? (завтра ранок)

## Reminders

- WARM diff-mode v3.5 = Sprint A завершено, наступна: масштабування + P3 cleanup
- Caching як P2 закрита, diff-mode свою роботу зробив
- Kit міграція на HOT/WARM/COLD — коли буде час
- tmux-restore.sh на Pi5 — TODO 2026-05-06

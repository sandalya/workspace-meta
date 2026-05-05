---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

Оновлено SYSTEM_PROMPT у chkp/chkp.py: додано двошарову механіку для запобігання галюцинаціям на ## Now. Правило 1 — явні canonical sources (ONLY from WHAT WAS DONE THIS SESSION для ## Now, CRITICAL). Правило 2 — _redact_now_for_context() видаляє ## Now і ## Last done з попередньої HOT перед API-call. Додано третю fixture з цієї сесії (c46cf24). Валідація: 19/19 тестів pass (3 no_hallucination + 16 warm_ops).

## Last done

- SYSTEM_PROMPT patch в chkp/chkp.py: двошарова архітектура (правила + mechanical redaction)
- _redact_now_for_context() функція: видаляє старий контекст перед API-call
- Третя fixture додана (meta, commit c46cf24)
- Усі 19 pytest тестів: PASS (3 no_hallucination для чекпоінтів + 16 warm_ops)
- Локальна верифікація на meta завершена

## Next

Завтра: спостерігати за реальними chkp на insilver-v3, sam, garcia — чи патч SYSTEM_PROMPT тримається на нових сесіях. Якщо OK — продовжити InSilver Етап 4 STABILIZATION_PLAN: Ed-блоки 02_search_intent, 03_complex_keywords, 11_order_each_type, 13_trainer_flow, скрипти run_ed_regression.sh. Опціонально оновити BACKLOG.md: chkp regression tests P1 (зараз PROMPT.md issue як P3).

## Blockers

Немає.

## Active branches

- chkp SYSTEM_PROMPT patch (готовий до Production)
- insilver-v3 Etap 4 STABILIZATION_PLAN (Ed coverage ~50% done)

## Open questions

- Чи SYSTEM_PROMPT патч вистоїть на живих чекпоінтах інших проектів?
- BACKLOG: чи piority chkp regression tests P1 або продовжити Ed coverage?

## Reminders

- Спостерігати реальні чекпоінти на insilver-v3/sam/garcia на наступних сесіях
- Если patchtримається → масштабувати на усі 6 проектів
- InSilver Etap 4: 5 Ed-блоків залишилось + scripts/run_ed_regression.sh

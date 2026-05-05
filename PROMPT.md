Проект: meta

Завершено SYSTEM_PROMPT patch у chkp/chkp.py (двошарова no-hallucination механіка). Додано правило 1 (canonical sources per section) + _redact_now_for_context() (видалення старого контексту перед API). Третя fixture додана. Валідація: 19/19 тестів PASS. Потрібна спостереження на реальних чекпоінтах (insilver-v3/sam/garcia) наступні сесії.

Наступно: якщо патч тримається → продовжити insilver-v3 Etap 4 STABILIZATION_PLAN (Ed блоки). BACKLOG: чи chkp regression tests P1 або Ed coverage?

Перепроекти HOT.md + WARM.md перед роботою.

Блокерів немає.
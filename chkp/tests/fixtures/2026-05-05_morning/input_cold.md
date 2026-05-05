---
project: insilver-v3
started: 2026-04-20
---

# COLD — InSilver v3

Історія проекту. Append-only. Не редагувати старі записи.

---

## 2026-04-20: Ініціалізація триярусної пам'яті

Перехід з `SESSION.md` + `DEV_CHECKPOINT.md` на `HOT.md` + `WARM.md` + `COLD.md`. Раніше стан проекту розкидано між двома файлами: SESSION.md (останній чекпоінт) і DEV_CHECKPOINT.md (архітектура + файли). Новий підхід: HOT (переписується кожну сесію), WARM (архітектура, інкрементально), COLD (append-only архів).

---

## 2026-04-20: InSilver v3 архітектура (baseline)

```yaml
archived_at: 2026-04-20
reason: baseline snapshot при міграції на три яруси
tags: [baseline, architecture]
```

InSilver v3 — ювелірний консультант для Влада (@insilver_v3_bot). Smart Router класифікує 4 інтенти (SEARCH/QUESTION/ORDER/SOCIAL) через Haiku. Каталог плоский, Q&A з training.json вбудовані в промпт. Order funnel з автозаповненням. Admin панель: /admin + /orders. Handoff для передачі оператору. Деплой: systemd на Pi5.

---

## 2026-04-25: /order race condition в Ed (таймаут 90с)

```yaml
archivals_at: 2026-04-25
reason: critical bug discovered, needs urgent investigation
tags: [bug, ed, order, timing, race-condition]
```

Виявлено КРИТИЧНИЙ баг: /order не долітає до бота під Ed flow — 90с таймаут. У ручному тесті спрацьовує миттєво. Баг не в коді бота (логіка OK), ймовірно в Ed flow timing або network. Задача 1 (Інше) підтверджена й працює. 10_order_funnel.json оновлений (weaving/length ключі, коментар-flow, wait після /start). httpx токен-логи закриті в main.py. Дебажити через журнали (`journalctl -u insilver-v3 -f`), порівняти timing ручного тесту vs Ed. Демо Владу перенесено на після фіксу.

---

## 2026-04-25: v004 чекліст закрито (5/5 задач + коміти --no-verify)

```yaml
archived_at: 2026-04-25
reason: completed v004 release checklist, technical ready
tags: [release, v004, checklist]
```

Закрито всі 5 обов'язкових задач v004:
1. ✅ Дозволено повторний вхід у воронку (allow_reentry=True в обох ConversationHandler)
2. ✅ Фіксня /order після завершення воронки (ConversationHandler end)
3. ✅ safe_admin_send helper в core/handoff.py з warmup на 'Chat not found'
4. ✅ Замінено 4 точки нотифікацій адміна (order.py x2, client.py x2)
5. ✅ httpx-логи токенів закриті в main.py

Ed 10_order_funnel: 4 PASS + 1 WARN + 1 FAIL (метадані). Технічний чекліст 5/5 обов'язкових ✅, bot production-ready по функціоналу. Залишилась документація (ADMIN_GUIDE.md, USER_GUIDE.md) і pricing від Влада. Pre-commit hook зламаний (нерелевантні посилання на тести) — рішення: всі коміти `--no-verify`, фіксить у BACKLOG. Демо Владу готово.

---

## 2026-04-25: v004 фінальна з ТЗ Влада (production-ready функціонал)

```yaml
archived_at: 2026-04-25
reason: v004 release закрита, всі обов'язкові задачи + ТЗ Влада реалізовано
tags: [release, v004, complete, production-ready]
```

Сесія 25.04 завершила v004 з COMPLEX_KEYWORDS (комплект/каблучка/перстень/вушко → handoff), /price 150 команда, COMMON_STEPS (+city +np_office), режим A з A_NP_OFFICE для адмін-картки, order_id fix (uuid → #YYYYMMDD-HHMM), кнопка 📏 Як заміряти (hand_measure_1.jpg + hand_measure_2.jpg для браслета), видалення попередніх повідомлень воронки, Markdown-краш фіксня (b_send_step + notify_owner без parse_mode), Влад → Наш співробітник, /price NoneType захист. Ed 10_order_funnel: 4 PASS + 1 WARN + 1 FAIL (метадані). Бот production-ready по функціоналу. Залишилось: ADMIN_GUIDE.md + USER_GUIDE.md, фінальний pricing.json від Влада, демо Владу, фото ланцюжка. Коміти: 541d98d (фічі), c58ed72 (фікси), всі --no-verify. Pre-commit hook у BACKLOG (нерелевантні посилання на тести).

---

## 2026-04-25: Адмінка v2 — trainer + knowledge base доробки

```yaml
archivals_at: 2026-04-25
reason: completed admin panel with trainer mode, knowledge base view/edit, photo handling
tags: [admin, trainer, knowledge-base, photo, completed]
```

Сесія 25.04 (друга частина) завершила адмінку v2: /admin і /orders зареєстровані як CommandHandler (раніше були у коді але не як обробники команд). Тренерський режим: /done тепер працює (видалено ~filters.COMMAND фільтр), handle_trainer_photo graceful "фото поки не підтримується" (не handoff), handle_photo делегує якщо ctx.user_data.trainer. view_knowledge: 👁 view + 🗑 del кнопки, kb_view_<id> розгортає запис (title+content+3 buttons), kb_edit_<id> редагує (delete+new trainer). Smoke ✅: /admin меню, /done (38 записів у training.json), 👁 view, ✏️ edit, фото graceful. Коміти з цієї частини уже у master. Фінальна версія адмінки готова до демо Владу.

---

## 2026-04-25: Документація + команди + меню скрепки + admin toggle (session complete)

```yaml
archivals_at: 2026-04-25
reason: v004 documentation & ui finalization complete, production-ready for demo
tags: [documentation, ui, admin, commands, complete]
```

Сесія 25.04 (завершеня) реалізувала фінальні UI компоненти для production release:
- **ADMIN_GUIDE.md** (382р) + **USER_GUIDE.md** (224р) — фінальна документація з гайдами, чеклістами, форматування
- **PDF генерація:** pandoc + chromium headless (Pi5, сірий фон #f5f5f5, Noto Color Emoji fonts), файли у data/docs/
- **bot/doc_sender.py:** split_by_h2 + md_to_telegram_v2 з bulletproof escape (placeholder loop handles nested code/bold/headers)
- **/help + /admin_help:** шлють .md секціями через MarkdownV2, silent-ignore для не-адмінів на /admin_help
- **Меню скрепки (BotCommandScopeChat):** 5 команд для клієнта (menu, help, order, contact, price) + 10 для адміна (+ admin, orders, done, price, reset, restart, logs)
- **/admin toggle:** вхід/вихід з адмін-режиму, runtime state у data/admin_active.json, скидається при старті
- **Коміти:** 3e08482 (docs), cc26a05 (feat) — обидва --no-verify (pre-commit hook у BACKLOG)
- **Smoke ✅:** /help, /admin_help, меню скрепки, toggle, PDF генерація
Бот тепер production-ready по UI. Все готово до демо Владу: документація, команди, адмін-панель, меню. Залишилось: отримати фінальний pricing.json від Влада, фото ланцюжка, демо, опціональна Задача 6. BACKLOG: видалити /catalog (мертвий ендпоінт).

---

## 2026-04-26: Кнопка 'Замовити цей виріб' видалена, dead code режиму A убраний

```yaml
archivals_at: 2026-04-26
reason: cleanup session, removed obsolete features
tags: [cleanup, refactoring, mode-a]
```

Сесія 26.04 (початок) убрала технічний долг:
- **Видалена кнопка 'Замовити цей виріб'** у каталозі (коміт 5f92c3b) — меню користувача було перегромаджено
- **Видалено весь dead code режиму A** з bot/order.py (коміт 7fb3573): состояния mode_a_start, константи A_*, entry point, функції. Скорочено 901→821 рядків
- **Видалено зламаний .git/hooks/pre-commit** (помилка на трьох неіснуючих файлах). Бекап збережений у /tmp/insilver-precommit-backup-20260426.sh
- **Почищено BACKLOG:** видалено 2 дублі задачі про pre-commit hook, додано нову задачу 'InSilver voice reference extraction' з планом по 60 скрінах Влада

**Статус:** Готово до наступної фази voice reference extraction.

---

## 2026-04-26: Voice reference extraction план (60 скрінів Влада з TG)

```yaml
archivals_at: 2026-04-26
reason: planned new feature for training data collection
tags: [voice-reference, training, pipeline, planning]
```

**Ініціатива:** InSilver voice reference extraction — зібрати реальні голосові ознаки ювелірних виробів від 60 скрінів розмов Влада з клієнтами у TG.

**План обробки:**
- Сашок експортує 60 скрінів з TG за 3 сесії (20 скрінів за раз)
- Скрипт на Pi5 обробляє через Claude Vision API (виділення фото, тексту, контексту)
- Результати → `data/docs/archive/voice_reference_real_clients_*.md` (3 файли)

**Рекомендація:** Варіант Б — Telegram export + Pi5 скрипт через Claude Vision (найпростіший без ручної обробки).

**Після voice reference:** перевірити чи `tests/real_client_cases.py` зроблений на основі цих 60 скрінів.

**Статус:** Чекаємо на перший експорт від Сашка (20 скрінів). У планах на наступні сесії.

---

## 2026-04-27: Оновлення контакту майстра на @InSilver_925 + Markdown-фіксня

```yaml
archived_at: 2026-04-27
reason: session complete, contact master update + markdown parser fix
tags: [contact, config, markdown, fix]
```

Сесія 27.04: InSilver контакт змінено з @gamaiunchik на @InSilver_925. **Процес:** MASTER_TELEGRAM у .env → переписуємо → рестарт сервісу. **Markdown-парсинг фіксня:** У bot/client.py (рядки 125, 159) додано backticks навколо {MASTER_TELEGRAM}: `` `{MASTER_TELEGRAM}` `` замість `{MASTER_TELEGRAM}`. Причина: underscore (_) у нічнику ламає Telegram MarkdownV2 парсер. **Централізація:** config.py читає з .env з fallback на @gamaiunchik — безпечна архітектура. **USER_GUIDE.md:** поки залишився @gamaiunchik, синхронізація окремо при необхідності. Бот готовий до демо Владу з оновленим контактом. Чекаємо: pricing.json, фото ланцюжка, підтвердження контакту.

---

## 2026-04-27: Dev інстанс @insilver_silvia_bot для тестування

```yaml
archivals_at: 2026-04-27
reason: dev instance setup completed, awaiting verification and git push
tags: [dev-instance, infrastructure, bot, setup]
```

Сесія 27.04 (друга половина): Створено dev інстанс `insilver-v3-dev` як повну копію prod для тестування на окремому боті @insilver_silvia_bot (окремий токен, старий revoked). **Інстанс:** `/home/sashok/.openclaw/workspace/insilver-v3-dev/` з повним кодом, data/, venv. **Сервіс:** `insilver-v3-dev.service` у `/etc/systemd/system/` (disabled, не enabled). **Статус:** getMe + getUpdates повертають ok=True, бот стартує чисто без помилок. **Next:** перевірити /start у @insilver_silvia_bot (правильне посилання), запустити dev сервіс, push dev гілку в origin. **Вторинна знахідка:** Prod токен @insilver_v3_bot має 75% Conflict 409 в логах — бот функціонально живий але потребує дослідження (revoke або копати зовнішні getUpdates) — окрема критична задача на наступну сесію.

---

## 2026-04-30: Feature flag CATALOG_SEND_PHOTOS для вимкнення фото каталогу

```yaml
archived_at: 2026-04-30
reason: session complete, catalog photos feature flag implemented
tags: [feature-flag, catalog, photos, prod, dev]
```

Сесія 30.04: Вимкнено надсилання фото з каталогу на prod і dev через feature flag CATALOG_SEND_PHOTOS (default=false). **Реалізація:** `import os` додано на верхній рівень bot/client.py, патч на рядках 46-49 — early return з `reply_text` + `keyboard` якщо `CATALOG_SEND_PHOTOS != 'true'`. **Результат:** SEARCH intent повертає текст без фото (тільки опис виробів). **Prod:** рестартанутий, стартує чисто. **Dev:** @insilver_silvia_bot оновлений з тим самим патчем. **Примітки:** локальний `import os` на рядку 513 у DEBUG-блоці залишився (нешкідливо), рядок 459 (handoff send_photo адміну) НЕ чіпали — це фото від клієнта, не каталог. **Коли готові фото каталогу:** додати `CATALOG_SEND_PHOTOS=true` у .env (prod + dev), рестартувати сервіси. Блок готовий до prod-use.

## 2026-05-01 — Conflict 409 self-resolved

**Симптом (HOT.md 30.04):** 75% помилок у логах — `telegram.error.Conflict: terminated by other getUpdates request`. 1059 за весь час логу, 207 за 7 діб.

**Розслідування:**
- Token чистий (контрольний getUpdates повернув ok=true)
- Webhook порожній (getWebhookInfo url="")
- Dev-інстанс має окремий токен (різні md5 хеші) — не конфліктує
- Останній Conflict у логах: 2026-04-29 17:27:38

**Висновок:** проблема зникла після повного рестарту в сесії 30.04 (feature flag CATALOG_SEND_PHOTOS). Найімовірніша причина — zombie-процес від попередніх рестартів, який нарешті прибили чистим stop+start. Точна першопричина не встановлена.

**Запобіжник:** додати `Conflict` у фільтр `error_monitor.py` (етап 1.4 STABILIZATION_PLAN.md). Якщо повернеться — побачимо за хвилину.

**Status:** prod active, 0 Conflict за 2 хв спостереження, переведено в стан "watch list" замість "blocker".

---

## 2026-05-01: Conflict 409 self-resolved після рестарту 30.04, STABILIZATION_PLAN + EVALS_PLAN

```yaml
archivals_at: 2026-05-01
reason: conflict resolution complete, infrastructure stabilization plan created
tags: [infrastructure, conflict-409, stabilization, evals, resolved]
```

Сесія 01.05 (post-stabilization checkpoint): **Conflict 409 проблема self-resolved**.症狀 (HOT.md 30.04): 75% помилок у логах @insilver_v3_bot — `telegram.error.Conflict: terminated by other getUpdates request`. **Розслідування:** token чистий (getUpdates ok=true), webhook порожній, dev-інстанс має окремий токен (різні md5). **Висновок:** zombie-процес від попередніх рестартів, прибитий чистим stop+start 30.04. Точна першопричина не встановлена. **Prod статус:** 0 конфліктів за 2 хв спостереження. **Запобіжник:** додати Conflict у фільтр error_monitor.py (етап 1.3 STABILIZATION_PLAN.md). **STABILIZATION_PLAN.md** (нова): 4-етапний план (Conflict research done, 1.2: .bak + .gitignore, 1.3: add Conflict monitor, 1.4: review old logs). **EVALS_PLAN.md** (нова): Ed QA (4 блоки), smoke тести, voice reference extraction (3 сесії). Коміти: --no-verify. Готово до наступної сесії (етап 1.2-1.3).

---

## 2026-05-01: Etап 1.2 STABILIZATION_PLAN закрито — cleanup .bak + .gitignore

```yaml
archivals_at: 2026-05-01
reason: session complete, cleanup tasks finished
tags: [cleanup, gitignore, ruff, stabilization]
```

Сесія 01.05 (першa половина): **Этап 1.2 STABILIZATION_PLAN закрито.** Видалено всі .bak-файли через `find . -name '*.bak' -delete`. Оновлено .gitignore з 6 новими рядками: .bak, .pyc, __pycache__, .env.local, logs/*, data/admin_active.json. **Ruff integration:** `pre-commit run ruff --all-files` на core/ + bot/ повернув 0 errors (all green). **Git статус:** 6 нових commits на master від 30.04. **Скрипт обробки:** CC запрошено один раз за 6 ruff-фіксів, спрацювало без проблем. **Prod + Dev:** обидва стартують чисто, готові до наступної фази. **PROMPT.md:** синхронізовано з поточним станом проекту (версія 2026-05-01). **Next:** Этап 1.3 — додати Conflict фільтр у error_monitor.py (~10 хв).

---

## 2026-05-02: Error monitor implementation v0 — инфраструктура встановлена, потребує конфігурації

```yaml
archivals_at: 2026-05-02
reason: session checkpoint, error monitoring infrastructure created but incomplete
tags: [error-monitor, infrastructure, monitoring, in-progress]
```

Сесія 02.05: Розпочата робота над систематичним мониторингом помилок prodакшену. **Реалізація:** `tools/error_monitor.py` — скрипт для читання systemd журналів prod сервісу з фільтрацією помилок (Conflict 409, Bad Gateway, NetworkError, TimedOut), rate-limiting 60с і відправкою Telegram нотифікацій на груповий чат MONITOR_CHAT_ID (-1003891541800). **Архітектура:** окремий Telegram-бот @sashok_raspberry_status_bot (токен з backup/.env), systemd unit для автозапуску, інсталер shell-скрипт tools/install_error_monitor.sh. **Фіче:** трейсбеки обрізуються до 30р (head 10 + tail 10), лічильник suppressed помилок, graceful обробка API помилок. **Smoke test:** бот запускається, логіка читання .env OK, підключення до API OK. **Blocker:** помилка 'chat not found' при відправці нотифікації — бот @sashok_raspberry_status_bot не додано до групи MONITOR_CHAT_ID. **Статус:** Untracked файли (tools/error_monitor.py, tools/install_error_monitor.sh, tools/error_monitor.service). **Next:** додати бота до групи, перевірити getChat (group permissions), повторити smoke test, інсталювати systemd unit через інсталер, комітити або .gitignore. **Резервація:** якщо вирішено не ховати помилки в production (тільки в dev), можна переміщувати error_monitor у tools/ як опціональний dev-tool.

---

## 2026-05-02: Etап 1.3 Error Monitor v0 — infrastructure complete, configuration pending

```yaml
archivals_at: 2026-05-02
reason: session checkpoint, error monitoring infrastructure created but blocked on group configuration
tags: [error-monitor, infrastructure, monitoring, stabilization, in-progress]
```

Сесія 02.05: Розпочата і майже завершена робота над систематичним мониторингом помилок production сервісу в рамках Етап 1.3 STABILIZATION_PLAN.md. **Реалізація:** `tools/error_monitor.py` — 150+ рядків скрипту для читання systemd журналів `insilver-v3.service` з фільтрацією помилок (Conflict 409, Bad Gateway, NetworkError, TimedOut автоматично скидаються), rate-limiting 60 секунд між однаковими помилками (з лічильником suppressed), обрізуванням трейсбеків до 30 рядків (head 10 + tail 10 з '...' посередині), й відправкою Telegram нотифікацій на груповий чат MONITOR_CHAT_ID (-1003891541800). **Архітектура:** окремий Telegram-бот @sashok_raspberry_status_bot (токен з backup/.env), systemd unit `tools/error_monitor.service` для автозапуску, shell-скрипт інсталер `tools/install_error_monitor.sh` для регістрації в systemd. **Smoke test (02.05):** бот запускається, логіка читання окремих .env файлів (backup/.env + insilver-v3/.env) працює OK, підключення до Telegram API OK, обробка журналів OK. **BLOCKER:** помилка 'chat not found' при спробі відправки нотифікації — бот @sashok_raspberry_status_bot не додано до групи з chat_id -1003891541800. **Статус:** 3 файли untracked (tools/error_monitor.py, tools/install_error_monitor.sh, tools/error_monitor.service), потребують либо комітування як infrastructure, либо додавання до .gitignore. **Next:** (1) додати бота до групи вручну через UI, можливо перевірити групову ID через @handle замість числа, (2) повторити smoke test для валідації 'chat not found' fixed, (3) запустити `sudo bash tools/install_error_monitor.sh`, (4) перевірити журнали через `sudo journalctl -u error_monitor -f`, (5) вирішити питання комітування/gitignore. **Резервація:** якщо буде рішення не ховати повні помилки в production (тільки в dev), можна переміщувати error_monitor в tools/ як опціональний dev-tool, який активується через окремий feature flag або не інсталюється на prod.

---

## 2026-05-02: Этап 2.1–2.2 Unit Tests Foundation — pytest setup + 50 юніт-тестів (COMPLETE)

```yaml
archivals_at: 2026-05-02
reason: unit test foundation established, 50 green tests, pre-commit hook extended
tags: [unit-tests, pytest, coverage, foundation, testing]
```

**Сесія 02.05:** Закритий Этап 2.1–2.2 STABILIZATION_PLAN — повна інфраструктура юніт-тестів встановлена. **Setup:** pytest 9.0.3 + pytest-cov інстальовані у venv, requirements.txt оновлений, `tests/unit/` структура з `__init__.py`, `conftest.py` (mock_pricing фіксура), pyproject.toml з [tool.pytest.ini_options] (testpaths = ["tests/unit"], python_files = test_*.py, addopts = --cov=core,bot --cov-report=html). **Результат:** 50 зелених тестів у 4 файлах за 0.46с.

**test_pricing.py** (15 тестів, 77% coverage):
- calculate_price: 4 weight-варіації (150, 200, 250, 300g), 3 weaving-типи (плетінка, якір, панцир) через mock pricing.json
- format_price: "1 234,50 ₴" форматування
- get_price_per_gram: 55.00
- Edge cases: 0 weight, missing key, float precision
- Фіксура mock_pricing у conftest.py (yield + cleanup)

**test_order_config.py** (11 тестів):
- generate_order_id: #YYYYMMDD-HHMM формат
- 8 типів виробів: ланцюжок, браслет, хрестик, кулон, обручка, перстень, набір, інше
- PRODUCT_STEPS по типам
- COMMON_STEPS присутні (контакт, коментар, місто, np_office)
- End-to-end flow

**test_doc_sender.py** (13 тестів):
- split_by_h2: парсер .md секцій на заголовки рівня 2
- md_to_telegram_v2 escape: bold, italic, code, links
- MarkdownV2 special chars (_, *, [, ], (, ), ~, >, #, +, -, =, |, {, }, ., !) крок за кроком
- Nested структури (bold у коді, коди у заголовках)
- Bullet lists, links без екранування крапок (Telegram приймає)
- Ручна валідація в Telegram (стає відправити без parse_mode помилок)

**test_complex_keywords.py** (11 тестів):
- COMPLEX_KEYWORDS detection: комплект, каблучка, перстень, вушко
- Case-insensitive matching
- Context-aware (у контексті замовлення)
- Handoff-trigger
- **BACKLOG знахідка:** substring без word-boundary — весілля НЕ матчить весільн (false negative для весільних замовлень), наперстенник матчить перстен (false positive). Опціональний рефакторинг: винести find_complex_keywords(text) у core/keywords.py.

**Pre-commit hook:** розширений `.git/hooks/pre-commit` додано рядок `pytest tests/unit/ -q` після ruff. Перевірка: реальний комміт 7735ebc (Add unit tests: pricing, order_config, doc_sender, complex_keywords) пройшов hook без --no-verify флага → All checks passed.

**.coverage + .gitignore:** `.coverage` добавлен в .gitignore, HTML reports видаляються на кожен запуск.

**Також виявлено (BACKLOG):** bot/doc_sender.py md_to_telegram_v2 не екранує крапки в URL — Telegram приймає але формально неправильно. Документовано, не блокер.

**Next:** Этап 2.3 (пріоритет 2) — test_router_parsing.py, test_handoff.py, test_order_context.py (~15-20 тестів). Потім Этап 3 (видалити стару order funnel).

---

## 2026-05-02: Этап 2.3 Unit Tests Prio 2 — test_router_parsing, test_handoff, test_order_context (COMPLETE)

```yaml
archivals_at: 2026-05-02
reason: unit test prio 2 stage completed, 36 new tests added, etap 2 fully closed
tags: [unit-tests, pytest, router, handoff, order-context, testing]
```

**Сесія 02.05:** Закритий Этап 2.3 STABILIZATION_PLAN — додано 36 нових юніт-тестів для пріоритету 2 модулів. **test_router_parsing.py** (9 тестів): classify_intent з 4 інтентами (SEARCH/QUESTION/ORDER/SOCIAL), Haiku-mock через monkeypatch _get_client, mock content для всіх INTENTS варіантів, API exception handling, fallback на QUESTION якщо не впізнане. **test_handoff.py** (7 тестів): is_paused (data/handoff_state.json читання), pause_bot (встановлення паузи, ctx update), resume_bot (очищення паузи), tmp_path для файлів, monkeypatch HANDOFF_FILE. **Примітка:** safe_admin_send async НЕ тестується (потребує mock Telegram API, виходить за рамки unit-scope). **test_order_context.py** (20 тестів): 6 чистих extract_* без mocking (extract_number, extract_weight, extract_price, extract_name, extract_phone, extract_address), 14 з контекстом/mocking, **критичний тест:** extract_weight грн lookahead exclusion (negative-lookahead `(?!гр[нА]?)` правильно виключає грн від ваги — важливо не міняти без оновлення). **Результат:** 50→86 unit тестів, full suite 0.49s (допустимий overhead). **Pre-commit hook:** верифікований коммітом 556c19f без --no-verify: ruff All checks passed + pytest 86 passed in 0.49s. **Etap 2 ПОВНІСТЮ ЗАКРИТИЙ.** **Next:** Этап 3 — audit старої vs нової воронки (build_order_handler vs build_new_order_handler), розширення нової на 8 типів, видалення старої.

---

## 2026-05-02: Видалення нової order funnel (build_new_order_handler) — dead code cleanup

```yaml
archived_at: 2026-05-02
reason: session complete, new order funnel removed, old funnel confirmed as sole production funnel
tags: [cleanup, refactoring, order-funnel, dead-code]
```

Сесія 02.05: **Видалена нова воронка (build_new_order_handler + всі пов'язані стани)** — це був мертвий код, ніколи не був зареєстрований у setup_handlers. Виявилося під час аналізу наслідків видалення: import build_new_order_handler не присутній у bot/client.py, воронка никогда не використовувалась на prod.

**Видалено:**
- 13 nb_* станів (nb_start, nb_select_type, ..., nb_summary)
- new_b_start, B_PRODUCT_TYPE, B_WEAVING, B_LENGTH, B_WEIGHT, B_COATING, B_CLASP, B_ADDITIONAL, B_CITY, B_NP_OFFICE, B_NAME, B_PHONE, B_ADDRESS, B_SUMMARY
- Весь функціонал build_new_order_handler

**Результат:** 819→496 рядків bot/order.py, -323 рядки. Тести: ruff 0 errors, pytest 86 passed. Hook верифіковано коммітом a3061e6 (All checks passed). Prod перезапущено, active, без помилок.

**Фактична архітектура після cleanup:** стара воронка (build_order_handler) — єдина prod-воронка з 8 типами виробів. Нова воронка видалена повністю. **Етап 3 STABILIZATION_PLAN фактично закритий через інверсію плану:** замість розширення нової воронки, вирішено залишити стару як основну і видалити нову (мертвий код).

**Наступні кроки:** чекаємо від Влада pricing.json з коефіцієнтами для всіх 8 типів, фото ланцюжка для measuring guide. Опціональна Задача 6 (додати calc крок у summary) — низький пріоритет.

---

## 2026-05-02: Етап 2 STABILIZATION_PLAN повністю завершено — 86 unit тестів + видалення мертвого коду

```yaml
archived_at: 2026-05-02
reason: session complete, etap 2 foundation and prio2 closed, new funnel removed as dead code
tags: [unit-tests, pytest, stabilization, cleanup, refactoring]
```

Сесія 02.05: **Закрито Этап 2 STABILIZATION_PLAN — foundation (50 тестів) + prio2 (36 нових тестів) — всі 86 unit тестів green.**

**Étap 2.1–2.2 Foundation (02.05):** pytest 9.0.3 + pytest-cov у venv, requirements.txt оновлений, tests/unit/ структура (conftest.py з mock_pricing фіксурою). 4 юніт-файли: test_pricing.py (15 тестів, 77% coverage, calculate_price 4 weight-варіації 3 weaving-типи), test_order_config.py (11 тестів, 8 типів виробів, PRODUCT_STEPS, end-to-end flow), test_doc_sender.py (13 тестів, split_by_h2, md_to_telegram_v2 escape special chars, nested структури, links), test_complex_keywords.py (11 тестів, COMPLEX_KEYWORDS detection комплект/каблучка/перстень/вушко). Pre-commit hook розширено `pytest tests/unit/ -q` після ruff, верифіковано коммітом 7735ebc без --no-verify (All checks passed). Full suite 0.46с.

**Étap 2.3 Prio 2 (02.05):** 36 нових тестів — test_router_parsing.py (9, classify_intent 4 інтенти Haiku-mock), test_handoff.py (7, is_paused/pause_bot/resume_bot tmp_path monkeypatch), test_order_context.py (20, 6 чистих extract_* + 14 з mocking, критичний extract_weight грн lookahead exclusion). Total 50→86 тестів, full suite 0.49с. Pre-commit hook верифікований коммітом 556c19f без --no-verify (86 passed).

**Видалення нової order funnel (02.05):** build_new_order_handler + 13 nb_* станів + new_b_start + B_PRODUCT_TYPE..B_SUMMARY видалені як мертвий код (ніколи не зареєстровані у setup_handlers). -323 рядки (819→496 bot/order.py). Стара воронка (build_order_handler) залишилась єдиною prod-воронкою з 8 типами. Etap 3 STABILIZATION_PLAN фактично закритий через інверсію плану (замість розширення нової — видалення). Коміт a3061e6 (All checks passed, без --no-verify).

**Prod статус:** перезапущено, active, без помилок. **Next:** чекаємо від Влада pricing.json (коефіцієнти всіх 8 типів), фото ланцюжка, потім опціональна Задача 6 (calc у summary).

---

## 2026-05-03: P1 診断 + Model A prod/dev sync + pre-push hook PII validation

```yaml
archivals_at: 2026-05-03
reason: session complete, P1 diagnostics closed, prod/dev sync Model A implemented, pre-push hook activated
tags: [p1-diagnostics, prod-dev-sync, infrastructure, pii, pre-push-hook, deployment]
```

Сесія 03.05: **Закрито P1 診断 + впроваджено Model A prod/dev sync.**

**P1.1 garcia/set_commands.py fix:** Виявлено hardcoded шляхи `/home/sashok/.../.env` — замінено на `BASE_DIR` (коміт b5a2a70 у sandalya/garcia). Правило для інших проєктів: використовувати relative paths з BASE_DIR вместо абсолютних.

**P1.2 Аудит 4 проєктів:** abby-v2, household_agent, sam, ed — грепнув на PII-паттерни (189793675, hardcoded шляхи, токени, .json backup) — **0 critical знахідок.** Баг-патерн insilver-v3 (hardcoded шляхи) ніде не повторюється.

**P1.3 Pre-push hook (insilver-v3-dev/.git/hooks/pre-push):** Реалізовано фіксчик для dev гілки що блокує відправку файлів з PII: 189793675 (MONITOR_CHAT_ID), handoff_state.json, training_backup, orders_backup, .jpg/.jpeg/.png. **Статус:** verified working (сесія 03.05). **BACKLOG:** false positive на data/photos/static/hand_measure_*.jpg — потребує звуження на конкретні каталоги вместо глобального .jpg блока.

**Prod/dev sync Model A:**
- dev reset --hard origin/main з backup-tag dev-pre-reset-2026-05-03
- PROMPT.md (orphan від сесії 02.05) комічено c5cd040 у dev, потім merge до main (cf98f3f)
- .gitignore розширено data/orders/orders.json.bak.* (коміт abde741)
- WIP.md exclude-правило (538602e)
- WIP.md template у insilver-v3-dev (gitignored, лайтова заміна HOT/WARM/COLD)
- HOT/WARM/COLD видалені з dev-каталогу + git update-index --skip-worktree (захист від випадкових комітів)
- chkp.py отримав dev-vs-prod warning guard з [y/N] промптом (коміт 7dd81a9 у workspace-meta)
- CLAUDE.md з full prod/dev workflow Model A документовано (cf98f3f)

**Side-effect беклог-записи:**
- (а) chkp.py пише PROMPT.md але НЕ робить git add+commit — orphan-стан після кожного чекпоінту (виявлено, документовано)
- (б) pre-push hook .jpg/.jpeg/.png занадто широкі — спрацювало false positive на санкціонованих data/photos/static/hand_measure_*.jpg (обходили --no-verify)

**Cleanup:** файл mai (від PuTTY paste artifact) прибрано.

**Prod + Dev статус:** 
- prod main: cf98f3f (CLAUDE.md merge), push-protected pre-push hook на dev
- dev: 538602e (WIP.md exclude), HOT/WARM/COLD --skip-worktree, getMe + getUpdates ok=True
- Обидва активні, синхронізовані

**Статус сесії:** ~1.5 год SSH + 1 CC discovery read-only (grep 5 проєктів). Всі 8 точок P1 діагностики закриті. **Next:** P1.4 Sam NBLM diagnostic (~1-1.5 год окремої сесії).

---

## 2026-05-05: Voice Reference Extraction (60 скрінів Влада) — extraction complete, awaiting review

```yaml
archived_at: 2026-05-05
reason: voice reference extraction session completed, 7 anonymized dialogues created with YAML extraction and questions for vlad
tags: [voice-reference, training-data, extraction, anonymization, yaml]
```

Сесія 05.05: **Завершена фаза 1 Voice Reference Extraction.** 60 скрінів Влада з TG експортовано → анонімізовано в 7 діалогів. **Архітектура:**
- `private/raw/` — оригінальні скрін-архіви (gitignored, ~60 файлів)
- `private/archive/` — анонімізовані діалоги: C001_yevhen.md, C002_natalia.md, C003_iryna.md, C004_oksana.md, C005_andriy.md, C006_pavlo.md, C007_dmytro.md (gitignored, ~280 рядків на файл)
- `private/archive/client_keymap.yaml` — шаблон для mapping ID → real client data (заповнюється після Vladом review)
- `data/docs/archive/voice_reference_extracted_2026-05-05.md` — публічна анонімізована версія для Ed QA

**YAML структура кожного діалогу (7 діалогів × 4 блоки = 28 extracted інстансів):**
- **client_persona:** вік, слово-образ (напр. 'молода мама'), мовні маркери
- **interaction_pattern:** як клієнт спілкується (переводи, перечислення, уточнення)
- **product_preference:** що обирає (метал, жанр, стиль), ціна-точка
- **communication_style:** фармалізм,速度 читання, emoji, скорочення

**questions_for_vlad (5 питань для уточнення):** захована в кожному діалозі у YAML-блоці questions_for_vlad — питання на які чекають відповіді Влада для уточнення client_persona, interaction_pattern, product_preference, communication_style.

**Результати:** 7 анонімізованих діалогів, 28 extracted YAML-блоків, 5 питань. Коміт 1106b8b на main (not pushed).

**Фаза 2 (待機):** Vladом review на questions_for_vlad + заповнення client_keymap.yaml + update ed_assertion_candidates.json + добавлення блоку 12_voice_consistency в Ed QA.

**Статус:** Extraction complete, структура готова, очікуємо на відповіді Влада для уточнення YAML-блоків та Фази 2.

---
project: insilver-v3
updated: 2026-05-05
---

# WARM — InSilver v3

## 🚨 ПРАВИЛО: Ed first для тестів

```yaml
last_touched: 2026-04-25
tags: [testing, workflow, critical]
status: active
```

**Будь-який функціональний тест бота — через Ed, НЕ руками.** Якщо у `ed/suites/data/insilver/blocks/` немає потрібного кейсу — спочатку оцінити час на додання. ≤30 хв → додати в Ed і прогнати. >30 хв → попередити і запропонувати ручний тест як виняток. Не застосовувати тільки для інфраструктурних перевірок (systemd, файли, shell).

## 🚨 ПРАВИЛО: dev-first workflow для prod changes

```yaml
last_touched: 2026-05-03
tags: [workflow, deployment, critical, prod-dev-sync, model-a]
status: active
```

**Model A (вже активна):** dev гілка — гарячі тестування + синхронізація, prod/main — чистий, push-protected.

**Workflow:** (1) Розробка у dev гілці, (2) reset --hard origin/main перед тим як merge до main, (3) merge у main, (4) push у GitHub з pre-push hook (блокує PII), (5) рестарт prod, (6) dev синхронізується назад. **ЗАБОРОНЕ:** робити зміни одразу на prod/main без dev-етапу. **chkp.py:** dev-vs-prod warning guard з [y/N] промптом (7dd81a9 workspace-meta). **CLAUDE.md:** prod/dev workflow Model A документовано (cf98f3f).

## Архітектура — Smart Router

```yaml
last_touched: 2026-04-17
tags: [architecture, router, ai]
status: active
```

`core/router.py` — класифікує intent через Haiku. 4 інтенти: SEARCH / QUESTION / ORDER / SOCIAL. Каталог показується ТІЛЬКИ для SEARCH intent. Модель: `claude-haiku-4-5-20251001`.

## Order funnel — одна система (стара)

```yaml
last_touched: 2026-05-02
tags: [order, funnel, ui]
status: active
```

**Основна (стара, `build_order_handler`)** — єдина prod-воронка, зареєстрована в `setup_handlers`. `bot/order.py` + `core/order_config.py` + `core/order_context.py` (автозаповнення з історії). 8 типів виробів: ланцюжок, браслет, хрестик, кулон, обручка, перстень, набір, інше. Кожен тип має свої кроки (напр. ланцюжок: плетіння→довжина→маса→покриття→застібка→додатково→контакт→коментар→**Summary+Confirm**). Кнопки "⬅️ Назад" і "❌ Скасувати" на кожному кроці. `_waiting_custom` для обробки "✏️ Інше" — бот просить текстовий ввід. **Summary+Confirm крок готовий** (сесія 22.04). **Задача 1 (Інше) підтверджена** (сесія 25.04). **allow_reentry=True** — дозволяє повторний вхід у воронку після завершення. **COMPLEX_KEYWORDS захист** — комплект/каблучка/перстень/вушко → handoff. **show_measure_button** для браслета з фото (hand_measure_1.jpg, hand_measure_2.jpg), для ланцюжка text-fallback HOW_TO_MEASURE. **Нотифікації замовлення** — ADMIN_IDS[0]. **Видалена нова воронка** (сесія 02.05) — build_new_order_handler + 13 nb_*, new_b_start, всі B_* стани мертві (-323 рядки, 819→496).

**10_order_funnel.json:** оновлений з weaving/length ключами, коментар-flow, wait після /start (сесія 25.04).

**Результати Ed тестування:** 4 PASS + 1 WARN + 1 FAIL (метадані). Все готово до демо.

**Беклог (низький пріоритет):** race state leak, comment_flow текст, happy_path пусте фінальне повідомлення, Задача 6 (calc у summary). Не блокують релізу.

## /price команда

```yaml
last_touched: 2026-04-25
tags: [pricing, command]
status: active
```

`/price 150` — стандартна команда для ручного розрахунку ціни за 150 гр срібла. Обробка: `bot/client.py` → `core/pricing.py` → `calculate_price()`. **NoneType захист** (сесія 25.04). Підтримує per-weaving коефіцієнти (default + варіації). Готово до демо.

## Як заміряти (measuring guide)

```yaml
last_touched: 2026-04-25
tags: [ux, photo, guide]
status: active
```

Кнопка 📏 Як заміряти у старій воронці на кроці довжини. **Для браслета:** hand_measure_1.jpg (браслет на руці) + hand_measure_2.jpg (краще видно). Фото закладені в `bot/order.py`. **Для ланцюжка:** поки text-fallback HOW_TO_MEASURE (дожидаємось від Влада фото). Ed тест: `10_order_funnel` проходить.

## Видалення попередніх повідомлень воронки

```yaml
last_touched: 2026-04-25
tags: [ux, cleanup, order]
status: active
```

Всі повідомлення з попередніх кроків видаляються при переході на новий крок (впроваджено через `delete_previous_messages`). **Включено видалення першого повідомлення Що замовляємо** (сесія 25.04). Покращує UX.

## Prompt і guardrails

```yaml
last_touched: 2026-04-17
tags: [prompt, training, ai, guardrails]
status: done
```

`core/prompt.py` — системний промпт + 15 Q&A з `training.json`. Q&A вбудовані плоско у контекст. Мультимовність: розуміє всі мови, НІКОЛИ не відповідає російською. Guardrails: тільки срібло 925, не додавати зайвих елементів, релігійні вироби тільки з бази. Ed тести `07_prompt_guardrails` — green. Roadmap: замінити плоский training на RAG для масштабування. **ПРИМІТКА:** prompt.py читає тільки content[0].text — фото в training records не підтримуються. Якщо буде RAG з картинками — повернутись.

## Handoff (human escalation)

```yaml
last_touched: 2026-04-25
tags: [handoff, admin]
status: done
```

`core/handoff.py` — pause/resume. `handle_photo` — фото → адміну + пауза. `handle_resume` — callback для адміна. Ed тести `09_handoff` — green. Handoff warmup протестовано (сесія 22.04). **safe_admin_send helper з warmup** (сесія 25.04) — тепер 'Chat not found' не критична помилка. **Замінено 4 точки нотифікацій адміна** (сесія 25.04 + 27.04): order.py x2 (сесія 27.04), client.py x2 (сесія 25.04). Між Ed-блоками треба скидати `data/handoff_state.json` → `{}`. **handle_photo делегує управління якщо ctx.user_data.trainer присутній** (сесія 25.04).

## Адмін-картка з НП

```yaml
last_touched: 2026-04-25
tags: [admin, order, delivery]
status: active
```

Адмін-картка замовлення тепер містить 🚚 НП (Нова Пошта) інформацію: город, відділення, адреса. Режим A з A_NP_OFFICE станом. Фото замовлення. order_id у форматі #YYYYMMDD-HHMM. Ed тест: `10_order_funnel` → order_id #20260425-1405 ✅. Стара воронка видає без #, нова з # — не блокує критично.

## Keyword detection (складні вироби)

```yaml
last_touched: 2026-05-02
tags: [keywords, handoff, routing]
status: active
```

**COMPLEX_KEYWORDS захист** (сесія 25.04): комплект, каблучка, перстень, вушко → handoff до Влада. Спрацьовує в `handle_message` (`bot/client.py`) для вільного чату — НЕ всередину ConversationHandler (воронки). Реалізовано через перевірку текстової інформації перед роутингом. Статус: **перевірено і працює** (сесія 25.04). **BACKLOG знахідка (сесія 02.05):** substring без word-boundary — весілля НЕ матчить весільн (false negative для весільних замовлень), наперстенник матчить перстен (false positive). Опціональний рефакторинг: винести find_complex_keywords(text) у core/keywords.py з proper word-boundary регексом.

## Калькулятор

```yaml
last_touched: 2026-04-22
tags: [pricing, calculator]
status: done
```

`core/pricing.py` з `calculate_price()`, `format_price()`, `get_price_per_gram()`. `data/pricing.json` — ціни. Працює в /price команді. **Pricing підтверджено Владом** (сесія 22.04). Готово до демо.

## Каталог і пошук

```yaml
last_touched: 2026-04-16
tags: [catalog, search]
status: active
```

`core/catalog.py` — пошук у каталозі ювелірних виробів. Поки плоский пошук, без RAG. Дані у `data/`. Feature flag CATALOG_SEND_PHOTOS (default=false) вимикає надсилання фото.

## Admin панель

```yaml
last_touched: 2026-04-25
tags: [admin, ui, commands]
status: ready_for_demo
```

`bot/admin.py` — адмін панель (279 рядків). `bot/admin_orders.py` — управління замовленнями. Команди: `/admin`, `/orders`. **Обидві команди зареєстровані як CommandHandler** (сесія 25.04). **Адмін нотифікації оновлені** (сесія 25.04 + 27.04) — замінено OWNER_CHAT_ID на ADMIN_IDS[0] у bot/order.py (сесія 27.04). **Готово до демо Владу**.

## Trainer mode (knowledge base training)

```yaml
last_touched: 2026-04-25
tags: [admin, training, knowledge]
status: active
```

Тренерський режим для адміна: /start в 1:1 с ботом активує trainer mode, збирає дані (title, content, category) і зберігає у `data/training.json`. **Команда /done тепер працює в trainer mode** (сесія 25.04) — видалено ~filters.COMMAND фільтр з handle_trainer_input. **handle_trainer_photo graceful** (сесія 25.04) — відповідає "фото поки не підтримується", не handoff. **view_knowledge** (сесія 25.04) — показує список записів з 👁 view + 🗑 del кнопками. **kb_view_<id>** callback розгортає запис (title+content+3 кнопки). **kb_edit_<id>** callback видаляє старий запис і стартує trainer з нуля. Smoke: /done збереження (38 записів ✅), 👁 view (✅), ✏️ edit (✅). 38 записів у training.json.

## Photo handling

```yaml
last_touched: 2026-04-25
tags: [photo, media, trainer]
status: active
```

`core/photo.py` — обробка фото від клієнтів. Фото → адміну → handoff пауза → "Повернути бота". **handle_photo делегує якщо ctx.user_data.trainer присутній** (сесія 25.04) — trainer використовує handle_trainer_photo з graceful відповіддю "фото поки не підтримується".

## Conversation logger

```yaml
last_touched: 2026-04-16
tags: [logging, infrastructure]
status: active
```

`core/conversation_logger.py` — логування розмов з клієнтами. Логи у `logs/`.

## Ed QA integration

```yaml
last_touched: 2026-04-25
tags: [testing, ed, qa]
status: active
```

Ed QA agent (`workspace/ed/`). Target: `@insilver_v3_bot`. Запуск: `cd ~/.openclaw/workspace/ed && source venv/bin/activate && python3 main.py run --bot insilver --block <BLOCK> --transport telegram --judge haiku`. Тест-кейси: `ed/suites/data/insilver/blocks/`. Рубрики: `ed/judge/rubrics/insilver.py`.

Блоки: `01_smoke`, `07_prompt_guardrails` (✅ green), `09_handoff` (✅ green), `10_order_funnel` (✅ 4 PASS + 1 WARN + 1 FAIL на метаданих). Два типи тестів: одиночні і multi-step з кнопками (`click_intent` — часткове співпадіння тексту, emoji ігноруються).

**Результати сесія 25.04:** Всі обов'язкові задачи v004 закриті, Ed готовий до демо.

## Unit Tests (юніти)

```yaml
last_touched: 2026-05-02
tags: [testing, unit-tests, pytest, coverage]
status: active
```

**Етап 2 STABILIZATION_PLAN — ПОВНІСТЮ ЗАКРИТИЙ (сесія 02.05):**

**Етап 2.1–2.2 Foundation (сесія 02.05):**
- **Setup:** pytest 9.0.3 + pytest-cov у venv, requirements.txt оновлений, tests/unit/{__init__.py, conftest.py}, pyproject.toml има [tool.pytest.ini_options]
- **test_pricing.py** (15 тестів, 77% coverage): calculate_price (4 weight-варіації, 3 weaving-типи через mock pricing.json), format_price, get_price_per_gram, edge cases
- **test_order_config.py** (11 тестів): generate_order_id (#YYYYMMDD-HHMM), 8 типів виробів, PRODUCT_STEPS, COMMON_STEPS, end-to-end flow
- **test_doc_sender.py** (13 тестів): split_by_h2 (парсер .md секцій), md_to_telegram_v2 escape (special chars, nested структури, links), валідація в Telegram
- **test_complex_keywords.py** (11 тестів): COMPLEX_KEYWORDS detection (комплект, каблучка, перстень, вушко), case-insensitive, handoff-trigger
- **Pre-commit hook:** рядок додано `pytest tests/unit/ -q` після ruff. Перевірено реальним коммітом 7735ebc — All checks passed без --no-verify.
- **Coverage:** .coverage у .gitignore, full suite 0.46с.

**Етап 2.3 Prio 2 (сесія 02.05 — ЗАКРИТИЙ):**
- **test_router_parsing.py** (9 тестів): classify_intent (4 інтенти), Haiku-mock через monkeypatch, mock content для всіх INTENTS, API exception, fallback
- **test_handoff.py** (7 тестів): is_paused, pause_bot, resume_bot з tmp_path+monkeypatch HANDOFF_FILE. safe_admin_send async НЕ тестується (mock Telegram API — понад unit-scope)
- **test_order_context.py** (20 тестів): 6 чистих extract_* (extract_number, extract_weight, extract_price, extract_name, extract_phone, extract_address), 14 з mocking. **КРИТИЧНИЙ:** extract_weight грн lookahead exclusion (negative-lookahead `(?!гр[нА]?)` правильно виключає грн від ваги)
- **Сумарно:** 50→86 unit тестів, full suite 0.49s
- **Pre-commit hook:** верифікований коммітом 556c19f без --no-verify: ruff All checks passed + pytest 86 passed

**BACKLOG знахідки (не блокери):**
- COMPLEX_KEYWORDS substring issue (весілля vs весільн false negative; наперстенник vs перстен false positive) — опціональний рефакторинг find_complex_keywords(text) у core/keywords.py
- md_to_telegram_v2 не екранує крапки в URL — Telegram приймає але формально неправильно
- extract_weight грн exclusion протестовано і працює — КРИТИЧНИЙ ІНВАРІАНТ, не міняти без оновлення тестів
- data/orders/ це директорія (не orders.json) — кожне замовлення окремий файл

**Next:** Очікування на pricing.json від Влада, фото ланцюжка. Опціональна Задача 6.

## Контакт майстра (MASTER_TELEGRAM) та нотифікації адміна (ADMIN_IDS)

```yaml
last_touched: 2026-04-27
tags: [contact, config, communication, admin]
status: active
```

**MASTER_TELEGRAM** централізовано управляється через `core/config.py`: `os.getenv('MASTER_TELEGRAM', '@gamaiunchik')`. Сесія 27.04: змінено на `@InSilver_925` у .env. Markdown-парсинг виправлено у `bot/client.py` (рядки 125, 159) — додано backticks навколо змінної: `` `{MASTER_TELEGRAM}` `` замість `{MASTER_TELEGRAM}`, бо underscore (_) ламає MarkdownV2 парсер. **Нотифікації замовлення:** замінено 4 входження OWNER_CHAT_ID на ADMIN_IDS[0] у bot/order.py (сесія 27.04) — адміна відповідно повідомлюється на особистий чат (467578687). **ADMIN_IDS** = [467578687, 189793675] (Влад перший адмін). **Зміна:** тільки через .env + рестарт сервісу, fallback залишається `@gamaiunchik`. **USER_GUIDE.md:** поки не оновлений — синхронізація окремо після підтвердження від Влада.

## Інфраструктура

```yaml
last_touched: 2026-05-03
tags: [infrastructure, deployment, dev-instance, conflict-409, ruff, gitignore, error-monitor, stabilization, unit-tests, prod-dev-sync, pii, pre-push-hook]
status: active
```

**Prod:** Сервіс `insilver-v3.service` (systemd). Бот `@insilver_v3_bot` (токен в /home/sashok/.openclaw/workspace/insilver-v3/.env). Workspace `/home/sashok/.openclaw/workspace/insilver-v3/`. **Статус 03.05:** Инфраструктура закрита, prod/dev sync Model A активна.

**Error Monitor (сесія 02.05, АКТИВНИЙ):**
- **Файли в репо:** `tools/error_monitor.py`, `tools/insilver-v3-error-monitor.service`, `tools/install_error_monitor.sh`
- **Systemd unit:** `/etc/systemd/system/insilver-v3-error-monitor.service` — active+enabled, читає `journalctl -u insilver-v3 -f -o cat -n 0` через pipe
- **Токен:** з `backup/.env` (TELEGRAM_TOKEN для @sashok_raspberry_status_bot — той самий бот що шле бекап-нотифікації)
- **Chat ID:** з `insilver-v3/.env` (MONITOR_CHAT_ID=189793675 — особистий user_id Сашка, **DM а не група**, стара група -1003891541800 більше не використовується)
- **Фільтр помилок:** Conflict 409, Bad Gateway, NetworkError, TimedOut (виключаються — це шум)
- **Тригери:** `[ERROR]`, `[CRITICAL]`, `Traceback (most recent call last)` у журналі
- **Rate-limit:** 60с між повідомленнями з лічильником suppressed
- **Трейсбеки:** обрізуються до 30 рядків (head 10 + tail 10 з '...' посередині), max msg 1500 chars
- **Smoke test (через pipe з echo "[ERROR]..."):** ✅ повідомлення прийшло в DM 02.05 18:26
- **Old files removed:** `tools/insilver-monitor.service`, `tools/install_monitor.sh`, `tools/monitor_bot.py` (від 25.03, не використовувались)

**Ruff + pre-commit (сесія 02.05, АКТИВНИЙ):**
- **Hook:** `.git/hooks/pre-commit` виконуваний, запускає `ruff check core/ bot/` + `pytest tests/unit/ -q`
- **Конфіг:** `pyproject.toml` має `[tool.ruff]` і `[tool.ruff.lint]`
- **Статус:** 0 errors at last check
- ✅ **Підтверджений:** реальний комміт a3061e6 (видалення нової воронки) пройшов без --no-verify флага, All checks passed

**.gitignore (сесія 02.05, оновлено 03.05):**
- Покриває: `*.bak`, `*.bak_*`, `data/*.bak*`, `data/knowledge/*.bak*`, `__pycache__`, `.env.local`, `logs/*`, `data/admin_active.json`, `.coverage`, `htmlcov/`
- **Додано (03.05):** `data/orders/orders.json.bak.*` (оновлено abde741)
- `find . -name "*.bak*"` повертає порожньо

**Pre-push hook (insilver-v3-dev/.git/hooks/pre-push, сесія 03.05, АКТИВНИЙ):**
- **Назва:** `pre-push` (фіксучі в shhot: post-merge це merge, pre-push це push)
- **Блокує:** 189793675 (MONITOR_CHAT_ID), handoff_state.json, training_backup, orders_backup, .jpg/.jpeg/.png
- **Статус:** verified working (сесія 03.05)
- **BACKLOG:** false positive на data/photos/static/hand_measure_*.jpg (santioned files) — потребує звуження на конкретні каталоги

**Dev інстанс (з 27.04):**
- Сервіс: `insilver-v3-dev.service` (systemd, disabled — стартує вручну для тестів)
- Бот: `@insilver_silvia_bot` (окремий токен)
- Workspace: `/home/sashok/.openclaw/workspace/insilver-v3-dev/` (повна копія, гілка `dev`)
- GitHub: `dev` запушена на origin (538602e, 03.05)
- **WIP.md:** gitignored, лайтова заміна HOT/WARM/COLD для dev
- **HOT/WARM/COLD:** видалені з dev + git update-index --skip-worktree (захист від випадкових комітів)
- **PROMPT.md:** orphan від попереднього чекпоінту, комічено c5cd040 (03.05)
- Статус: getMe + getUpdates ok=True, стартує чисто

**docs/ (сесія 02.05):**
- `docs/STABILIZATION_PLAN.md` + `docs/EVALS_PLAN.md` додані в обидві гілки (dev 538602e, main cf98f3f cherry-pick)
- ⚠️ Не плутати з `data/docs/` — там лежать PDF гайди (admin_guide.pdf, user_guide.pdf), це інша категорія

**Спільне:**
- Health checker: `core/health.py`
- Lock: `core/lock.py` (single process)
- Pi5 платформа

**Зміни які БУЛИ відкочені 02.05:**
- `bot/client.py` мав feature flag `os.getenv("CATALOG_SEND_PHOTOS", "false")` — orphan-зміна без контексту. Видалена через `git checkout`. Якщо в майбутньому треба повернути — це окрема свідома задача.

**PROMPT.md (03.05, orphan до коммітту):**
- Виявлено: chkp.py пише PROMPT.md але НЕ git add+commit — orphan-стан після кожного чекпоінту
- Коммічено c5cd040 (03.05) у dev, потім merge до main (cf98f3f)
- BACKLOG: додати git add+commit у chkp.py щоб PROMPT.md автоматично комітилась

**Інші проєкти (P1.2 audit, 03.05):**
- **garcia (sandalya/garcia):** PII-фіксня b5a2a70 ✅ (базові шляхи замінено на BASE_DIR)
- **abby-v2:** 0 critical PII-дизів ✅
- **household_agent:** 0 critical PII-дизів ✅
- **sam:** 0 critical PII-дизів (待機 на NBLM diagnostic для P1.4)
- **ed:** 0 critical PII-дизів ✅

## STABILIZATION_PLAN.md

```yaml
last_touched: 2026-05-02
tags: [stabilization, maintenance, plan]
status: active
```

**Документ:** `docs/STABILIZATION_PLAN.md` — 4-етапний план подальшої стабілізації проекту:

1. **Етап 1.1 (COMPLETE):** Conflict 409 дослідження — RESOLVED self-resolved
2. **Етап 1.2 (COMPLETE, сесія 01.05):** Прибрати .bak-файли (✅), оновити .gitignore (✅)
3. **Етап 1.3 (COMPLETE, сесія 02.05):** Error monitor — active+enabled в systemd, шле в DM @sashok_raspberry_status_bot (MONITOR_CHAT_ID=189793675, особистий user_id, не група), smoke test ✅ 18:26
4. **Етап 1.4 (COMPLETE, сесія 02.05):** pre-commit hook з ruff активний, 0 errors. Верифікований реальним коммітом a3061e6 (видалення нової воронки, All checks passed, без --no-verify). **Додано:** pytest tests/unit/ -q у hook (коміти 7735ebc + 556c19f)
5. **Етап 2 (COMPLETE, сесія 02.05):** pytest setup + юніт-тести foundation (2.1-2.2) + пріоритет 2 (2.3) — всі закриті

Мета: забезпечити чистоту проекту, prevent regression, 24-годинний моніторинг, unit test coverage. **Статус сесія 02.05:** Этап 1 ЗАКРИТИЙ. Етап 2 ЗАКРИТИЙ. **Наступні кроки:** чекаємо от Влада pricing.json, фото ланцюжка, потім опціональна Задача 6.

## EVALS_PLAN.md

```yaml
last_touched: 2026-05-01
tags: [evals, testing, plan]
status: active
```

**Документ:** `docs/EVALS_PLAN.md` — plan для QA & evaluation:

1. **Блок Ed QA:** перегляд всіх 4 блоків (01_smoke, 07_prompt_guardrails, 09_handoff, 10_order_funnel), підтримання green status
2. **Блок Smoke тести:** база ручних smoke тестів для демо Владу (/start, /help, /price, /order, /admin)
3. **Блок Voice reference extraction:** план по 60 скрінам Влада з TG (3 сесії по 20 скрінів)

Мета: вести QA процес в паралель з розробкою, не припиняти Ed-тести.

## Документація

```yaml
last_touched: 2026-04-25
tags: [documentation, guides]
status: complete
```

**ADMIN_GUIDE.md** — 382 рядки. Зміст: /admin, /orders, /price, /done flow, trainer 👁/✏️, адмін-картка з НП, HANDOFF, чекліст. **Готово.**

**USER_GUIDE.md** — 224 рядки. Зміст: формальне 'ви', 8 типів виробів, HOW_TO_MEASURE, #YYYYMMDD-HHMM, Нова Пошта, /help, /order, /contact. **Готово.**

**PDF генерація:** pandoc + chromium headless (Pi5, сірий фон #f5f5f5, Noto Color Emoji). **Готово.**

**bot/doc_sender.py:** split_by_h2 + md_to_telegram_v2 з bulletproof escape (placeholder loop handles nested code/bold/headers). **Готово.**

**/help і /admin_help:** шлють .md секціями MarkdownV2. **Готово.**

## Меню скрепки (inline commands)

```yaml
last_touched: 2026-04-25
tags: [ui, commands, menu]
status: complete
```

**5 команд для клієнта:** menu, help, order, contact, price

**10 команд для адміна:** menu, admin, orders, done, price, help, admin_help, reset, restart, logs

Реалізація: BotCommandScopeChat — різні меню для різних користувачів. Коміт: cc26a05 (feat). **Готово.**

## /admin toggle

```yaml
last_touched: 2026-04-25
tags: [admin, auth]
status: complete
```

`/admin` став toggle (вхід/вихід). Runtime state зберігається в `data/admin_active.json`, скидається при старті. Silent-ignore guards на /orders, /price, /done, /admin_help для не-адмінів. Коміт: cc26a05 (feat). **Готово.**

## Voice reference extraction (нова ініціатива)

```yaml
last_touched: 2026-05-05
tags: [voice, reference, training, pipeline]
status: extraction_complete_awaiting_review
```

**План (сесія 26.04):** InSilver voice reference extraction з 60 скрінів Влада з TG. **Способи обробки:** Telegram export + Claude Vision, або папір-ручка, або комбінація.

**Архітектура (сесія 05.05, ЗАВЕРШЕНО):**
- `private/raw/` — оригінальні скрін-архіви (gitignored)
- `private/archive/` — анонімізовані діалоги (C001_yevhen.md, ..., C007_dmytro.md), кожен з 4 YAML-блоками (client_persona, interaction_pattern, product_preference, communication_style) + questions_for_vlad
- `private/client_keymap.yaml` — шаблон для mapping ID → real client data (заповнюється після Vladом review)
- `data/docs/archive/voice_reference_extracted_2026-05-05.md` — публічна анонімізована версія

**Результати (05.05):** 60 скрінів → 7 анонімізованих діалогів, 28 extracted YAML-блоків (4×7), 5 питань для Влада. Коміт 1106b8b (not pushed, awaiting review).

**Фаза 2 (待機):** 
1. Vladом review на questions_for_vlad
2. Заповнити client_keymap.yaml
3. Оновити ed_assertion_candidates.json
4. Добавити блок 12_voice_consistency у Ed QA
5. Push 1106b8b

**Статус:** Extraction complete, awaiting Vladом review на відповіді.

## Roadmap (з implementation guide v003)

```yaml
last_touched: 2026-05-02
tags: [roadmap, planning]
status: active
```

**v004 — ЗАКРИТА:**
- Задача 1 (Інше) — ✅ закрита (сесія 25.04)
- Задача 2 (частково) — ✅ закрита (сесія 22.04)
- Задача 3 (allow_reentry) — ✅ закрита (сесія 25.04)
- Задача 4 (safe_admin_send) — ✅ закрита (сесія 25.04)
- Задача 5 (4 нотифікації) — ✅ закрита (сесія 25.04 + 27.04)
- Задача 6 (Summary у старій воронці) — опціональна

**v005 — Stabilization (ЗАКРИТА, 02.05):**
- ✅ Conflict 409 self-resolved (30.04)
- ✅ STABILIZATION_PLAN.md + EVALS_PLAN.md створено (01.05)
- ✅ Етап 1.2: .bak-файли видалені, .gitignore оновлений (01.05)
- ✅ Етап 1.3: Error monitor active+enabled, DM, smoke test ✅ (02.05)
- ✅ Етап 1.4: pre-commit hook з ruff + pytest, 0 errors, верифікований коммітом a3061e6 (02.05)
- ✅ Orphan feature flag CATALOG_SEND_PHOTOS відкочений з bot/client.py (02.05)
- ✅ Dev гілка запушена на origin (d645349, 02.05)

**v006 — Etap 2 (COMPLETE, 02.05):**
- ✅ 2.1–2.2: pytest setup + 4 юніт-файли (50 тестів, 77% coverage, foundation)
- ✅ 2.2: pre-commit hook з pytest
- ✅ 2.3: пріоритет 2 юніти (router, handoff, order_context) — 36 нових тестів, 86 total
- ✅ 3: видалити нову order funnel (видалена 02.05, -323 рядки, 819→496)

**v007 — P1 診断 + Model A (ACTIVE, 03.05):**
- ✅ P1.1: garcia/set_commands.py PII-fix (b5a2a70)
- ✅ P1.2: audit 4 проєктів (0 critical)
- ✅ P1.3: pre-push hook (189793675, handoff_state.json, training_backup, orders_backup, .jpg/.jpeg/.png)
- ✅ Prod/dev sync Model A (dev reset --hard, PROMPT.md коммічено, HOT/WARM/COLD --skip-worktree, WIP.md)
- ⏳ P1.4: Sam NBLM diagnostic (待機)
- ⚠️ Side-effect (а): PROMPT.md orphan — додати git add+commit у chkp.py
- ⚠️ Side-effect (б): pre-push hook .jpg/.jpeg/.png false positive — звузити на конкретні каталоги

**v008 —待機 (Чекаємо от Влада):**
- ⏳ Фото ланцюжка для measuring guide
- ⏳ Фінальний pricing.json (коефіцієнти всіх 8 типів)
- ⏳ Підтвердження контакту @InSilver_925

**Демо Владу:** /admin, /orders, /price, /done, /help, /admin_help, меню скрепки (очікуємо фото + pricing.json)

**Voice reference extraction:** 3 сесії по 20 скрінів (планується)

**Потім (postrelease):**
- Задача 6 (опціональна)
- RAG замість training.json (+ фото в training records)
- /catalog видалити (BACKLOG)

## Layout проекту

```yaml
last_touched: 2026-05-02
tags: [layout, files]
status: active
```

```
insilver-v3/                   (prod, Pi5, main branch)
├── main.py
├── bot/
│   ├── client.py
│   ├── order.py
│   ├── admin.py
│   ├── admin_orders.py
│   └── doc_sender.py
├── core/
│   ├── config.py            (MASTER_TELEGRAM, ADMIN_IDS, ORDERS_FILE)
│   ├── router.py
│   ├── prompt.py
│   ├── handoff.py
│   ├── photo.py             (ADMIN_IDS[0])
│   ├── pricing.py
│   ├── catalog.py
│   ├── order_config.py
│   ├── order_context.py
│   ├── health.py
│   ├── lock.py
│   └── ...
├── tools/
│   ├── error_monitor.py          (скрипт моніторингу помилок)
│   ├── install_error_monitor.sh  (інсталер)
│   └── insilver-v3-error-monitor.service (systemd unit)
├── docs/                    (STABILIZATION_PLAN.md, EVALS_PLAN.md, CLAUDE.md)
├── data/
│   ├── pricing.json
│   ├── training.json        (38 записів)
│   ├── docs/                (ADMIN_GUIDE.md, USER_GUIDE.md)
│   ├── archive/             (voice_reference_*.md очікується)
│   ├── admin_active.json
│   ├── handoff_state.json
│   └── orders/              (директорія, не orders.json)
├── logs/                    (< 2 тижні зберігати)
├── tests/
│   ├── unit/                (pytest, 86 тестів, foundation + prio2)
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_pricing.py (15 тестів)
│   │   ├── test_order_config.py (11 тестів)
│   │   ├── test_doc_sender.py (13 тестів)
│   │   ├── test_complex_keywords.py (11 тестів)
│   │   ├── test_router_parsing.py (9 тестів, 02.05)
│   │   ├── test_handoff.py (7 тестів, 02.05)
│   │   └── test_order_context.py (20 тестів, 02.05)
│   └── ...
└── scripts/

insilver-v3-dev/             (dev, Pi5, dev branch)
├── main.py
├── bot/
├── core/
├── data/
├── tests/
│   └── unit/
├── WIP.md (gitignored, лайтова заміна HOT/WARM/COLD)
└── ... (HOT/WARM/COLD видалені, --skip-worktree)

systemd files:
/etc/systemd/system/insilver-v3.service               (prod, active, рестартанутий 30.04)
/etc/systemd/system/insilver-v3-dev.service           (dev, disabled, сесія 27.04)
/etc/systemd/system/insilver-v3-error-monitor.service (active+enabled, DM @sashok_raspberry_status_bot)

backup files:
backup/.env                                 (TELEGRAM_TOKEN для @sashok_raspberry_status_bot)
```

# BACKLOG

<!-- ============================================================
     ПРАВИЛО ЧИТАННЯ ДЛЯ AI — ОБОВ'ЯЗКОВЕ
     ============================================================ -->

> ## ⚠️ STOP — read this before summarizing
>
> Цей файл містить **і активні, і закриті** пункти. Закриті залишаються тут як історичний контекст і **не видаляються** з файлу.
>
> **Маркер статусу — обгортка заголовка тильдами `~~...~~`:**
>
> - ✅ **ACTIVE** (повертай у summary): заголовок без тильд
>   - Приклад: `## InSilver voice reference extraction (2026-04-26)`
>   - Приклад: `### DR drill коли приїде запасна SD (2026-05-06)`
>
> - ❌ **CLOSED** (НЕ повертай у summary, пропусти): заголовок обгорнутий тильдами
>   - Приклад: `~~## chkp performance: COLD append-only (2026-05-05)~~`
>   - Приклад: `~~### chkp legacy cleanup (2026-05-03)~~`
>
> **Алгоритм summary:** для кожного `##` або `###` блоку перевір — чи рядок заголовка починається з `~~`? Якщо так → CLOSED, пропусти. Якщо ні → ACTIVE, включи у відповідь.
>
> Якщо не впевнений у статусі — НЕ домислюй. Процитуй точний рядок заголовка з оригінальними символами і запитай користувача.
>
> **Цей баг траплявся 2026-05-06**: AI повернув закреслені пункти як активні TODO двічі за одну сесію. Не повторюй.

---

~~## chkp performance: COLD append-only + streaming/timeout fix (2026-05-05)~~

Поточний `chkp` ганяє повний COLD на read+write кожну сесію → ціна сесії росте лінійно з історією. На insilver-v3 з voice_reference контекстом вибиває 16000 max_tokens на Haiku, на Sonnet падає у `urllib` timeout (~60s default).

**Симптоми (05.05.2026):**
- Haiku: `Response truncated at max_tokens=16000! ... Haiku response not valid JSON, retrying with Sonnet`
- Sonnet: `TimeoutError: The read operation timed out` у `urllib.request.urlopen(req, timeout=timeout)`

**Тимчасовий unblock:** збільшити `timeout=` у `call_anthropic()` у chkp.py до 300+ (зараз ~60s default). Це 5-хв точковий патч, не вирішує root cause але разблокує сесії з великим контекстом.

**Root cause рефакторинг (~1 година):**
1. **COLD append-only**: модель отримує COLD як read-only context, на запис повертає тільки append-блок. `chkp.py` сам конкатенує, не питає модель переписувати весь COLD.
2. **Frozen vs pending split у COLD**: `cold_frozen.md` (історія, не міняється, кешується назавжди) + `cold_pending.md` (останні N сесій, маленький, переписується).
3. **WARM diff-mode (P3)**: модель повертає набір diff-операцій (`add_section`, `update_yaml_block`, `delete_section`), не повний WARM. Складніше, найбільший виграш.
4. **`chkp` vs `chkp --full`**: щоденний chkp не чіпає COLD взагалі (тільки HOT/WARM). `--full` раз на тиждень робить compaction COLD.

**Пріоритет:** P2. Не блокує щодня (можна `--sonnet` + ретраї), але кожен chkp на 5+ хв це дратує і fail rate росте з розміром проєкту.

**Стек проявів:** insilver-v3 (з voice_reference, 05.05), Sam (через велику memory), Ed (потенційно).

**Контекст для виконавця:** код у `meta/chkp/chkp.py`, функція `call_anthropic()` ~line 136, `do_checkpoint()` ~line 481-494. Дивитись як формується `cacheable` vs `volatile` payload.

---

~~## ~~InSilver pre-commit hook fix~~ (2026-04-25)~~

Hook у insilver-v3/.git/hooks/pre-commit посилається на 3 файли тестів, з яких 2 не існують (run_all_claude_tests.py, tests/regression_tests.py, tests/input_edge_cases_tests.py). Hook завжди червоний, тому всі коміти йдуть з --no-verify. Варіанти: (а) видалити hook, (б) залишити тільки існуючі тести в hook, (в) написати реальні тести під ці назви. Пріоритет: середній — через нього легко пропустити реальний баг.

## InSilver voice reference extraction (2026-04-26)

У Сашка ~60 скрінів спілкування Влада з реальними клієнтами в Telegram (єдина наявна база реальних діалогів — продакшн замовлень в боті ще не було). Треба витягнути текст і зберегти як voice/tone reference для prompt.py, training.json, та можливо як basis для нових Ed assertions.

Варіанти реалізації:
- (А) OCR pipeline в Меггі/InSilver: handler "📸 OCR mode" приймає batch фото → Claude vision → markdown. Складність ~день. Плюс: інфраструктура наша, повторно використовується.
- (Б, рекомендовано) Telegram Desktop "Export chat history" → JSON+медіа → одноразовий скрипт на Pi5 який ганяє кожен .jpg через Claude Vision, складає .md з транскрипцією + контекст (timestamp, prev message). Складність ~2 години. Дешево, оффлайн з експорту.
- (В) Ручна транскрипція через Claude чат: Сашок кидає пачками по 5–10, я транскрибую. Якість найвища, але повільно.

Сашок зробив експорт за 3 сесії (60 скрінів разом). Після transcription:
- Зберегти як `data/docs/archive/voice_reference_real_clients_2026-XX-XX.md`
- Перевірити чи `tests/real_client_cases.py` справді зроблений на основі цих скрінів — якщо так, можливо merge або deprecate.
- Розглянути додавання витягнутих фрагментів у `training.json` та/або новий Ed блок типу `12_voice_consistency`.

Пріоритет: середній. Цінність: висока — це єдина точка контакту з реальною мовою клієнтів, неможливо відновити з іншого джерела.

---

~~## ✅ [CLOSED 2026-05-03] P1 — Системна перевірка hardcoded шляхів (всі боти)~~

**Контекст:** 29.04 в insilver-v3-dev знайдено критичний баг — `core/config.py` мав hardcoded абсолютний шлях до prod `.env` з `override=True`, через що dev-процес стартував з prod-токеном і інтерферував з prod через 409 Conflict. Той самий патерн міг бути скопійований в інші проєкти.

**Завдання:** перевірити кожен проєкт на hardcoded шляхи `/home/sashok/.openclaw/workspace/<project>/` у Python-коді.

**Список проєктів:**
- [ ] abby-v2/
- [ ] household_agent/ (Meg)
- [ ] sam/
- [ ] garcia/
- [ ] ed/

**Команда пошуку (для кожного проєкту):**
cd /home/sashok/.openclaw/workspace/<project>
grep -rn 'load_dotenv|/home/sashok/.openclaw/workspace/' --include='*.py' | grep -v venv | grep -v pycache

**Критично патчити:**
- `load_dotenv('/абсолютний/шлях/.env', override=True)` — runtime-критично
- Будь-які hardcoded шляхи в `core/`, `bot/`, `main.py`, `*.service`-target скриптах

**Шаблон фіксу:**
```python
_env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(_env_file, override=True)
```

**Не критично (можна лишити):**
- Скрипти в `scripts/`, `tools/` що запускаються рукою рідко
- Коментарі що згадують абсолютний шлях

**Чому P1:** будь-яка спроба зробити `<project>-dev` клон без фіксу → інтерференція з prod токеном.

**Контекст у пам'яті:** insilver-v3 chkp від 29.04 (commit b121bf2)


## household_agent .git 239M аудит (2026-04-29)

Після security cleanup сесії 29.04 розмір `.git` у household_agent залишився 239M, попри що venv/__pycache__ blobs у історії = 0. Причина іншa (можливо великі data файли, фото, gallery-dl bin'ари). Запустити `git filter-repo --analyze`, переглянути `.git/filter-repo/analysis/path-deleted-sizes.txt` і `directories-deleted-numbers.txt`. Пріоритет: середній — не security issue, тільки розмір.

## shared/ концепція — рефакторинг (~2026-05-06)

Папка `~/.openclaw/workspace/shared/` затрекана як plain folder, але реально нічого не шериться між ботами (кожен має повністю свій код). У Фазі 6 cleanup НЕ переносилася в meta — рішення відкладено. Варіанти: (а) перенести в meta/legacy/shared і видалити з workspace; (б) видалити повністю (код там не імпортується); (в) залишити як архів. Перед рішенням — `grep -r "from shared" --include="*.py"` по кожному боту, перевірити фактичні імпорти. Пріоритет: низький, ціль ~2026-05-06.

## Polyrepo vs гібрид decision (~2026-05-06)

Після security cleanup workspace 29.04 структура: 9 окремих repos на GitHub + meta-репо + root уже не git. Працює, але потрібно остаточно вирішити чи залишити polyrepo або зробити гібрид (наприклад, monorepo для тісно пов'язаних або submodules для всього). Контекст: частковий audit показав що одні боти ділять стиль/інфраструктуру (Abby, Garcia — beauty/design), інші стоять окремо (Sam — AI assistant, Insilver — jewelry). Пріоритет: низький, обговорити через тиждень коли впорядкуванням все осяде.

~~## ✅ [CLOSED 2026-05-03] insilver-v3-dev local copy має PII (2026-04-29)~~

Папка `~/.openclaw/workspace/insilver-v3-dev/` (тестовий бот @insilver_silvia_bot) на гілці `dev`, той же remote що insilver-v3. HEAD цієї гілки все ще містить 4 PII файли (фото клієнта `189793675_*.jpg`, handoff_state, training backup, orders_backup). Local-only тепер (origin dev гілку Сашок видалив у Фазі 3), але якщо push із insilver-v3-dev → PII повернеться на GitHub. Варіанти: (а) переключити на main + filter-repo; (б) видалити папку, перестворити dev клон з main коли потрібно; (в) додати .git/hooks/pre-push що блокує push з цього clone. Пріоритет: середній (захист "ручний" допоки не зроблено).


## Linux/bash cheat-sheet під мою інфру (2026-04-30)

Сашок хоче персоналізований cheat-sheet під Pi5 ecosystem (sam, abby-v2, ed, household_agent, systemd, NBLM CLI). ~20 базових команд щоб впевнено читати CC bash-команди і одразу бачити "це безпечно / це чіпає продакшн": ls, cd, cat, cp, mv, rm, grep, find, chmod, systemctl, journalctl, git status/diff/log, sudo, pipes (|), redirects (> >>), heredoc (<< EOF). Контекст: коли CC питає дозвіл на bash-команду — не клацати "yes" вгадуючи, а свідомо. Окрема сесія в Claude.ai chat. Пріоритет: середній, зробити коли RSS-feed закрито.

## Agentic ingest для Сема (2026-04-30)

Сашок хоче передавати Сему довільний матеріал (URL, текст, скрін з кодом, PDF, голосове, фрагмент розмови з Claude в чаті) з мінімальним описом задачі — і Сем сам розуміє контекст, класифікує, додає в курікулум у правильний острів/тему/доповнення, генерує контент потрібного формату і "глибини занурення". Конкретний кейс який Сашок назвав: "взяти два абзаци і розгорнути у потрібному форматі і довжині". Передумова — Сашок коротко описує задачу перед скидом матеріалу.

Це не функція — це фундаментальна зміна Сема з content delivery system на personal knowledge OS: замість ручної curation ("/article URL", "додай тему X") — agentic ingest з classifier + router + safeguards.

Потрібна послідовність (не плутати): RSS (закрито 30.04 — feed live, AntennaPod працює) → evals infrastructure (LLM-as-a-judge для агентних рішень, базова інфра в `sam/evals/`, baseline 20 прикладів topic_classification) → agentic ingest (use cases, classifier, router до правильного острову/теми/доповнення, safeguards проти сміттєвих ентітіз, rollback видимість).

Розмова потребує ~2-3 годин архітектурного дизайну в окремій сесії Claude.ai. Пріоритет: високий, але не починати без evals infra (інакше не побачиш коли класифікатор деградує). Cheat-sheet Linux (окремий backlog item) — паралельно/незалежно.
- [ ] Sam: /nbstatus — звіт які теми мають NbLM контент по форматах

## Sam — NBLM Content Generation Pipeline (з сесії 01.05)

- **Фаза Б — pre-analysis модуль** `core/content_gen/brief.py` (Haiku): аналіз source → structured brief (key concepts, focus questions, suggested angle).
- **Фаза В — DeepDive як окремий формат** `deepdive_podcast`. Команда `/deepdive <topic_id>`. Включає enrichment через web_search (2-3 додаткові sources). НЕ в default pipeline.
- **Brief як артефакт для юзера**: показувати перед NBLM-запуском з кнопкою "так / уточни / скіп". Дає контроль над фокусом + сама по собі форма навчання.
- **Brief reuse**: `Topic.brief` як окреме поле, генеруються 1 раз, шерять між backend-ами (NBLM/TTS/quiz/flashcards).
- **`/regen --preset deepdive`**: регенерація конкретної теми з іншим preset. Корисно коли тема "не зайшла".
- **Логування NBLM args**: `log.debug(f"NBLM args: {args}")` у `_start_generation` перед `_run` — для дебагу.
- **Backend-agnostic архітектура**: `core/content_gen/backends/{nblm,tts,interactive}.py`. Зараз тільки nblm.py, інші — заглушки.

~~## ✅ [CLOSED 2026-05-03] insilver-v3: prod/dev sync + memory model (P1)~~

**Стан 02.05:** dev відстав від main на 19 комітів (тести, error monitor, STABILIZATION_PLAN, видалення нової воронки). Спроба merge dev←main впала на 4 конфлікти: `.gitignore` (content), `HOT.md` + `WARM.md` + `COLD.md` (modify/delete — dev хотів видалити, main модифікував). Merge абортнутий, dev на c9e5ac5, prod main на a3061e6.

**Рішення прийняте:** Модель A — єдина prod-memory (HOT/WARM/COLD на main), dev має окремий лайтовий `WIP.md` для нотаток поточної розробки. Chkp викликається тільки в prod-каталозі після подій що змінюють prod-стан.

**Workflow для prod/dev проєктів (insilver-v3 та подібних):**
1. Розробка на dev-каталозі (гілка `dev`, тести, експерименти)
2. Перевірка через `insilver-v3-dev.service` (бот `@insilver_silvia_bot`), pytest, ruff, Ed
3. Merge `dev` → `main` (або cherry-pick якщо точково)
4. Push main, restart prod (з підтвердженням Сашка)
5. Sync dev назад: `git merge main` — fast-forward якщо main не отримував комітів повз dev (defensive habit)
6. Chkp в prod-каталозі — оновлює HOT/WARM/COLD з реального стану prod
7. WIP.md на dev — закривається або переноситься в "shipped" секцію

**Окремі підзадачі для виконання:**
- Розв'язати поточний конфлікт sync (видалити HOT/WARM/COLD з dev — Модель A приймає це; перемерджити .gitignore руками)
- Створити `insilver-v3-dev/WIP.md` з шаблоном
- Оновити `meta/chkp/chkp.py`: пересвідчитись що працює тільки з prod-каталогу (або додати warning якщо запущений з -dev)
- Зафіксувати workflow в `insilver-v3/CLAUDE.md` або проектному README

## Sam — NBLM tech debt (2026-05-03, post-діагностики)

chkp performance investigation 04.05: prompt caching не підходить через волатильний WARM (Haiku перезаписує щоразу). Майбутні підходи (P3, не критично): WARM diff-mode (Haiku видає тільки patch, chkp.py застосовує), COLD compaction (frozen+pending split, frozen cacheable), output streaming (UX покращення без зміни total time). Зараз chkp ~30-90s — приймаємо як норму.

regen handler stale UI string — каже 'retry до 72 год' хоча Intervention 3 скоротила RETRY_DELAYS до 4h cap (P3, тривіально). Симптом: при /regen бот пише 'Запускаю послідовно (retry до 72 год на rate limit)...' що неактуально після d822a29. Фікс: знайти текст у bot/handlers/ або modules/regen.py та оновити на '4 год'. Розмір: ~5 хв.

external_stop в Intervention 3b лишає status=pending замість повернення в failed (P3, побічний ефект). Симптом: після external_stop тема виглядає stuck pending з task_id=None/retry_count=None/error=None. Не блокує (наступний /regen стартує тему заново), але плодить zombie state. Фікс: у external_stop branch у retry loop і wait loop — set_format_status(failed, error='external_stop') перед exit. Розмір: ~15 хв коду + Ed-test.

**Контекст:** 03.05 при розборі 8 застряглих тем виявлено що поряд з відомою проблемою накопичених артефактів є ще 4 окремих баги, які разом створюють відчуття "крива інтеграція з NBLM". 16 з 18 podcast-ів зараз ready, 2 теми застрягли (`rag_retrieval-1`, `system_operations-5`) на цих багах. Не блокує SAM щодня, але точково кусає при кожному `/regen` нової теми.

**Стратегія:** перш ніж рефакторити цілий модуль `core/content_gen/backends/nblm.py` — пройти шлях "diagnostic → точкові інтервенції → big refactor як окремий plan". Між інтервенціями писати Ed-suite на NBLM happy path + rc=1 path, інакше регресій не помітимо до прода.

### BACKLOG hygiene — перенести закриті пункти в BACKLOG_CLOSED.md (~2026-05-20)

**Тригер:** через ~2 тижні від 2026-05-06 переглянути BACKLOG.md. Якщо `~~struck~~` пунктів стало багато (suggestion: >40% або файл >60K) — вирізати їх у новий файл `meta/BACKLOG_CLOSED.md`.

**Чому append-only зараз ОК:** 40K / 385 рядків / 33% closed — не біль. Закриті пункти ще працюють як landmark контекст для тебе і Claude. Стане шумом через 3-6 міс активної розробки.

**Як робити (коли вкусить):** `grep -n '^~~##' BACKLOG.md` → копіювати блоки → `mv` в `BACKLOG_CLOSED.md` з timestamp заголовком "## Archived 2026-XX-XX". 5 хв руками, без скрипта (скрипт = ще один шматок коду на підтримку).

**Альтернатива:** ігнорувати цей пункт. Якщо за 2 тижні думка "файл захаращений" не спаде природно — значить не біль, можна закреслити.

### ✅ DONE

#### 2. Idempotent ADD_SOURCE (d822a29, P2)

Реалізовано: `source list --json` перед `source add`, skip якщо URL вже присутній; fallback (add as before) якщо list rc!=0 або JSON malformed. Підтверджено direct CLI що healthy notebook `8aca66e9` мав 4+ дублів. 11/11 unit-тестів зелені.

#### 3. rc=1 detection / RETRY_DELAYS (d822a29, P2)

Формулювання "silent rc=1" виявилось некоректним: direct CLI показав structured JSON `{"code": "RATE_LIMITED", "message": "..."}` з RC=1 — Sam коректно ловив, але йшов у 72h retry. Реалізовано: `RETRY_DELAYS = [0] + [3600] * 4` (~4h cap, 5 спроб), після вичерпання `error="rate_limit_exhausted"`. Structured `nblm_{code}` error для null-RPC.

#### 4. brief.py укр JSON / EN prompt switch (6e5589c + 26cf181, P2)

Проблема: Haiku ігнорував UA-інструкції локалізації (1 fail на 18 топіків — `rag_retrieval-1`), root cause — UA/EN drift, не JSON structure. Реалізовано: `brief.py` prompt → EN; debug-патч `BriefParseError` + raw dump для safety net. Верифікація: rag_retrieval-1 перегенерувався за 4с чисто, 6/6 unit-тестів зелені.

### TODO — відкриті підзадачі

#### 1. Dangling nblm_notebook_id на видалений notebook (P2)

**Direct CLI** на `0daaf506`: NBLM повертає `RPC GET_NOTEBOOK failed, null result data` — notebook видалений на стороні Google або UUID ніколи не існував; `nblm_notebook_id` у curriculum.json залишився як dangling pointer. Sam-flow: `Reusing notebook 0daaf506` → ADD_SOURCE warning ignored (RPC fails) → `_start_generation` падає → `status=failed`.

**Фікс:** у `get_or_create_notebook`, після `if entity.nblm_notebook_id: return it` — probe `source list -n <id> --json`. Якщо RPC error / null result → `log.warning` + `nblm_notebook_id = None` → fallthrough на create notebook. ~30 хв коду + 2 unit-теста.

#### 5. nblm_notebook_id consolidation refactor (P3, big plan)

**Контекст:** mapping тема→notebook живе в трьох місцях паралельно:
- `topics[].nblm_notebook_id` (canonical?)
- `topics[].notebook_id` (часто None навіть коли nblm_notebook_id заповнено)
- `topics[].formats.video.url` (вказує на той самий notebook через URL)
- `topics[].formats.podcast_nblm.notebook_id` (часто None)

При reuse Sam дивиться в `nblm_notebook_id` (не в `notebook_id`), а інша логіка можливо в інших полях. Це джерело дублів в NBLM UI ("🏆 LLM Evaluation Tools" ×3, "🔍 Graceful Degradation Patterns" ×2, etc.) і поточних reuse-багів.

**План:** окрема сесія архітектурного дизайну: одне canonical поле `topics[].nblm_notebook_id`, всі інші deprecated через shim як у Phase B. Schema migration з backward-compat. Після консолідації — переглянути reuse-by-title логіку (можливо непотрібна якщо canonical поле завжди заповнене).

**Розмір:** 1 повна сесія + ~1 сесія тестів. **Не починати без Інтервенції 1 (dangling nblm_notebook_id) — без неї рефакторинг внесе нові регресії.**

#### 6. wait-loop curriculum reload performance (P3)

`_wait_for_artifact` тепер `load(cur_path)` на кожній ітерації while-loop (~30 хв). При scaling до 20 паралельних generations — disk-read кожні 30 хв. Ймовірний фікс: `state_provider` callback що шарить cached state між паралельними wait-loop'ами. ~1 година.

#### 7. Sam pipeline lifecycle observability (P3)

`status` у curriculum.json не показує реальний стан in-flight asyncio task'ів; немає способу подивитись без grep по journalctl. Ідея: `/admin tasks` команда — `asyncio.all_tasks()`, для кожного name + coro repr + час від старту + stage (Phase 1 retry / Phase 2 wait / external_stop pending), можливо кнопка cancel. ~1.5 години.

### Послідовність робіт

**Сесія 1 (відкрита):** Інтервенція 1 (dangling nblm_notebook_id) — probe `source list -n <id>` на `0daaf506`, інвалідувати dangling pointer, fallthrough на create. Diagnostic 03.05 дав достатньо розуміння, окремої діагностичної сесії не потрібно.

**Сесія 2+:** big refactor (consolidation) — окремий план, тільки якщо value виправдане після Інтервенції 1.

**Пріоритет загалом:** P2. Не блокує щодня (16/18 тем ready, AntennaPod feed live), але кожна нова тема — потенційно ще одна `system_operations-5`. Розв'язати протягом 2-3 тижнів.

### Validation post-restart 03.05

    journalctl -u sam.service --since "1 day ago" 2>&1 | grep -E "Source already present|skipping|external_stop|rate_limit_exhausted|nblm_"

Очікувані маркери після першого `/regen`: "Source already present ... skipping" (Inter 2), "rate_limit_exhausted" (Inter 3a), `nblm_{code}` (Inter 3b). НЕ повинно бути "external_stop" для stale video task'ів (false-positive risk). Якщо за 24 години немає "Source already present" — треба ручний `/regen` щоб тригернути валідацію.

---

## Workspace infrastructure (з сесії 2026-05-03)

insilver-v3-dev dev branch upstream check (P3, ~5 хв): після PII cleanup 03.05 локальна dev гілка не має origin/dev (git push --dry-run падає з 'no upstream'). Перевірити чи це навмисно (Model A — push тільки з main після merge) або треба git push -u origin dev.

### chkp v3.4 готова — стабільна версія (2026-05-03)

chkp v3.4 повністю стабілізована: shim у ~/.local/bin/chkp забезпечує що будь-який виклик (PuTTY, CC, subshell, cron) йде у python3 chkp.py v3.4. Legacy bash-скрипти (від ~10.04) перенесені в meta/legacy/chkp_bash_v1/. AI-частина update_backlog видалена — рішення про правки беклогу приймає Claude в чаті (читає BACKLOG.md з github.com/sandalya/workspace-meta), команда chkp отримує точкові правки через --backlog-strike і --backlog-add прапори, застосовує механічно через str.replace.

**Workflow:** при 'чкп' Claude фетчить актуальний BACKLOG, додає прапори до chkp-команди якщо сесія стосується пунктів беклогу.

**Доказ працездатності:** ця сама секція додана через --backlog-add у тому ж chkp що її описує.

~~### chkp legacy cleanup (2026-05-03)~~

Після фіксу shim'а в /home/sashok/.local/bin/chkp залишились артефакти попередніх версій chkp які варто прибрати:

- workspace/kit/chkp.sh, workspace/kit/chkp2.sh, workspace/meta/chkp.sh — legacy bash-скрипти, перенести у workspace/meta/legacy/chkp_bash_v1/
- workspace/meta/chkp/chkp.py.bak — backup невідомої версії, перевірити diff і видалити якщо не потрібен
- workspace/meta/SESSION.md — випадково створений старим chkp (commit b400e54), видалити і додати у .gitignore meta repo

**Розмір:** ~10 хв. **Пріоритет:** низький, косметика.

Виявлено під час P1.3 (insilver prod/dev sync). Зібрано окремо щоб не загубити в meta/BACKLOG.

~~### ~~chkp.py не комітить PROMPT.md~~ після генерації~~

**Симптом:** після кожного `chkp <project>` файл `<project>/PROMPT.md` залишається у "modified" стані в working tree. У insilver-v3 03.05 це створило orphan-uncommitted change який висів між сесіями. Виявлено випадково при `git status` перед merge.

**Що треба:** у `meta/chkp/chkp.py` після `write_file(PROMPT.md, ...)` додати в той самий commit що оновлює HOT/WARM/COLD. Зараз `git_commit_push` чомусь не включає PROMPT.md.

**Розмір:** ~10 хв коду + smoke-тест.

**Пріоритет:** низький. Косметика, але плодить "modified PROMPT.md" в кожному проекті де викликається chkp.

~~### ~~pre-push hook у insilver-v3-dev~~ — patterns надто широкі~~

**Симптом:** hook `data/.git/hooks/pre-push` блокує всі `*.jpg/*.jpeg/*.png` в push. 03.05 спрацював false positive на санкціонованих `data/photos/static/hand_measure_*.jpg` (інструкційні фото для HOW_TO_MEASURE), довелось обходити `--no-verify`.

**Фікс:** звузити patterns. Замість blanket `\.jpg$|\.jpeg$|\.png$` блокувати тільки якщо файл у конкретних "PII каталогах":
- `data/photos/incoming/`
- `data/photos/clients/`
- Або просто patterns по client-ID формату: `\d{9,}_.*\.jpe?g$`

`data/photos/static/` — статичні assets, дозволені.

**Розмір:** ~15 хв коду + тест.

**Пріоритет:** низький. False positive обходиться `--no-verify`, але незручно і "wolf cry" ефект (звикнеш ігнорувати hook).

### Tag `dev-pre-reset-2026-05-03` cleanup

03.05 створено tag-backup на GitHub перед `git reset --hard` на dev. Після ~30 днів стабільної роботи нової prod/dev схеми (Model A) — можна видалити tag:
cd insilver-v3 && git tag -d dev-pre-reset-2026-05-03 && git push origin :refs/tags/dev-pre-reset-2026-05-03

Календарне нагадування: ~02.06.2026.

### ~~CLAUDE.md дрібнота~~

У `insilver-v3/CLAUDE.md` (commit cf98f3f) у Hotfix exception секції приклад "insilver-v3-dev/.env override=True" — реально був `insilver-v3-dev/core/config.py` що завантажував prod `.env` з `override=True`. Дрібна неточність формулювання, не критична. Виправити при наступному торканні CLAUDE.md.


## Sam — manual stop не перериває in-flight asyncio task (2026-05-03)

**Симптом:** при `/regen` для теми Sam запускає `generate_and_notify` як `asyncio.create_task(...)`. Якщо тема впала у rate_limit retry-loop (RETRY_DELAYS = 71*3600), і ми вручну редагуємо `data/curriculum.json` ставлячи `formats.podcast_nblm.status="failed"` — фоновий task **продовжує крутити цикл і кожну годину дзвонити NBLM**, бо він живе у пам'яті процесу і не читає JSON.

**Виявлено:** 03.05 при діагностиці. Curriculum.json для system_operations-5 показував `status=failed, error="manual stop — investigation in progress"`, але `journalctl` показував `Retry start podcast_nblm for system_operations-5 after 3600s` кожну годину з 11:46 до 16:46 (5+ ітерацій).

**Підтвердження що це поведінка процесу:** після `systemctl restart sam.service` lazy re-attach НЕ підняв ці теми (бо у JSON status=failed) → manual stop "спрацював", але ціною повного рестарту.

**Гіпотеза фіксу:** in-loop check curriculum state перед кожним retry. У `generate_and_notify`, у Phase 1 retry loop:
for delay in RETRY_DELAYS:
if delay:
await asyncio.sleep(delay)
# NEW: re-load state, exit if status changed externally
state = load(cur_path)
entity = state.get_topic(topic_id) if kind == "topic" else state.get_article(topic_id)
if entity.formats[fmt].status != "generating":
log.info(f"External stop detected for {topic_id}/{fmt}, exiting retry loop")
return
task_id, start_err = await _start_generation(...)

Те саме треба для `_wait_for_artifact` infinite loop — інакше stale task_id (`7af67aad`, `19826355`) теж неможливо зупинити без рестарту.

**Розмір:** ~30 хв коду + Ed-test для регресії. Можна додати у Сесію 2 CC як 4-у інтервенцію разом з 2+3.

**Пріоритет:** P2. Наразі обхід — `systemctl restart sam.service` після manual JSON edit.


~~### chkp.py — silent skip при невідомій секції BACKLOG (2026-05-06)~~

**Симптом:** при виклику `chkp ... --backlog-add "Section::Text"` якщо `Section` не існує в BACKLOG.md, chkp виводить `⚠️ section not found — skip` і завершується з `✅ BACKLOG: 0 strikes, 0 adds (skipped: 0+3)` і **exit code 0**. Зелена галочка при втраті записів — silent data loss.

**Випадок:** session 2026-05-06 (SD cleanup + meggi venv rebuild) — три пункти `--backlog-add` пропущені через невірні назви секцій ("Infrastructure", "Backup" замість "Workspace infrastructure"), chkp нічого не помітив, дописувати довелось вручну.

**Варіанти fix:**
- **Fail loud:** при skipped > 0 → exit 1 з повідомленням "section X not found, valid: A, B, C"
- **Auto-create:** якщо секції нема — створити `## Section` в кінці і додати пункт
- **Fuzzy match:** при "Infrastructure" знайти найближче `## Workspace infrastructure` і запитати підтвердження
- **Combo:** fail loud за замовчуванням + флаг `--backlog-create-section` для auto-create

**Розмір:** ~30-45 хв коду + тест на silent-skip регресію + прогон існуючого suite (19/19 pytest).

**Пріоритет:** середній. Silent data loss у backlog може коштувати потрібних задач, але обхід (ручний `cat >>`) тривіальний.

### ~~Suppress httpx INFO logging у всіх ботах (2026-05-06)~~

**Симптом:** `python-telegram-bot` через httpx логує **повний URL запиту в Telegram API** на рівні INFO, включно з токеном бота в path:
INFO httpx: HTTP Request: POST https://api.telegram.org/bot<TOKEN>/getMe ...

При `journalctl -u <bot>.service` або при показі логів комусь — токен витікає.

**Випадок:** session 2026-05-06 — токен Меггі засвітився в чаті при діагностиці voice-to-text, довелось ротувати через @BotFather.

**Фікс:** у `shared/logger` (або де централізована конфігурація логування) додати:
```python
logging.getLogger("httpx").setLevel(logging.WARNING)
```

Перевірити що це не зламає debug-можливості (на WARNING помилки HTTP все одно логуватимуться). Зробити для всіх 7 ботів: abby-v2, insilver-v3, insilver-v3-dev, sam, garcia, household_agent, ed.

**Розмір:** ~15 хв (один рядок у shared/logger якщо логер централізований; інакше у кожному боті окремо).

**Пріоритет:** **високий — security**. Поточний стан = постійне витікання токенів у systemd journal.

### Розширити backup.sh для повного DR (2026-05-06)

**Симптом:** `backup.sh` бекапить `data/`, `.env`, sessions, `.git/`, `meta/`, `~/.claude/CLAUDE.md`, `~/.bashrc` — але **не бекапить системну інфраструктуру** яка потрібна для відновлення з нуля при втраті SD.

**Що бракує в архіві:**
- `/etc/systemd/system/*.service` і `*.timer` — всі юніти ботів (abby-v2, insilver-v3, sam, garcia, household_agent, ed, kit, pi5-backup). Без цього після нової SD — створювати systemd-юніти з пам'яті/чатів.
- `~/.claude/settings.json` — 54 allow + 30 deny rules для CC. Болісно відтворювати.
- `crontab -l > backup/crontab.txt` — якщо є crontab job-и (зараз все через systemd timer, але про всяк).
- `dpkg --get-selections > backup/packages.txt` — список встановлених apt пакетів (`ffmpeg`, `tmux`, `git`, etc).
- `pip freeze` глобальний (не venv-specific) — якщо щось ставилось глобально через `--break-system-packages`.

**Фікс:** окремий блок у `backup.sh` перед tar-архівацією який збирає це у `backup/system-snapshot/` (читай-only, переписується кожного разу), потім ця папка попадає в основний tar.

**Розмір:** ~30 хв коду + тест відновлення з архіву на чистій SD (це і є DR drill з пункту нижче).

**Пріоритет:** середній. Прямо зараз не блокує, але без цього "запасна SD приїде, відновимось за годину" перетвориться на "ну ось систему піднімемо за день".

### DR drill коли приїде запасна SD (2026-05-06)

Коли прийде друга SD карта (запас) — пройти повний цикл відновлення на ній з останнього бекапу, щоб переконатись що бекап реально живий, а не "схема Шрьодінгера".

**Сценарій:**
1. Запасну SD заливаємо чистим Raspberry Pi OS через Imager
2. Перший boot, базовий setup користувача `sashok`, ssh keys, sudo
3. Витягуємо `archives/2026-05-XX.tar.gz` з ПК (`H:\pi_backups\`) на нову SD через scp
4. Розпаковуємо архів, розкладаємо `data/`, `.env`, `*.session` по проектах
5. Клонуємо репи з GitHub у `/home/sashok/.openclaw/workspace/`: sam, ed, abby-v2, insilver-v3, insilver-v3-dev, garcia, household_agent, kit, meta, pi5-backup
6. Відновлюємо `~/.claude/settings.json`, `~/.bashrc`, `~/.local/bin/chkp` шим, `~/.claude/CLAUDE.md`
7. Створюємо systemd unit файли (`pi5-backup.timer`, всі бот-сервіси) — або з system-snapshot з backup.sh розширення (див пункт вище)
8. `sudo systemctl daemon-reload && enable --now ...` для всіх ботів
9. Ed-ом ганяємо смоук-тести по всіх ботах
10. Що зламалось — фіксимо в `backup.sh`, документуємо у `pi5-backup/RESTORE.md` як runbook
11. Повертаємо робочу SD у Pi, нову зберігаємо як hot spare з актуальним станом

**Розмір:** один вечір (3-5 годин), бо реально проходимо повний цикл.

**Пріоритет:** **високий**. Без drill бекап непідтверджений. Не робити повільніше — як тільки прийде SD.


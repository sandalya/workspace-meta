
## chkp3 max_tokens bug (2026-04-24)

Haiku обрізає JSON при WARM+контекст >~13k токенів (Phase 6.1 сесія Sam): `Unterminated string at char 4041` після `max_tokens=8000 out=8000`. Sonnet fallback теж впав — timeout 120s на Pi.

Варіанти фіксу:
1. Підняти `max_tokens` Haiku до 16000 (дешево, тестувати чи пройде)
2. Chunk WARM: стисти перед відправкою (додатковий LLM call — дорого)
3. Timeout Sonnet підняти з 120s до 300s
4. Fallback на повний rewrite HOT без попереднього контексту (скласти з user input тільки)

Пріоритет: середній, бо HOT можна руками оновити як fallback.

## InSilver pre-commit hook fix (2026-04-25)

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

## chkp xclip під SSH без $DISPLAY (2026-04-25)

`chkp` спроба `xclip` для копіювання NEXT SESSION PROMPT падає з `Error: Can't open display: (null)` під SSH. Скрипт коректно робить фолбек у PROMPT.md, але видає шум помилки в stdout. Фікс: перевіряти `os.environ.get("DISPLAY")` перед викликом xclip або обернути в try/except SilentError. Пріоритет: низький — косметика.

---

## P1 — Системна перевірка hardcoded шляхів (всі боти)

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


## abby-v1 GitHub repo deletion (2026-04-29)

Локально папку `~/.openclaw/workspace/abby/` видалено в Фазі 1.2 security cleanup. PAT `ghp_EYFzv...` revoked. **Лишається видалити сам репозиторій:** github.com/sandalya/abby-v1 → Settings → Danger Zone → Delete repository → ввести `sandalya/abby-v1` для підтвердження. Пріоритет: низький (ризику немає, бо PAT revoked і код архівний).

## household_agent .git 239M аудит (2026-04-29)

Після security cleanup сесії 29.04 розмір `.git` у household_agent залишився 239M, попри що venv/__pycache__ blobs у історії = 0. Причина іншa (можливо великі data файли, фото, gallery-dl bin'ари). Запустити `git filter-repo --analyze`, переглянути `.git/filter-repo/analysis/path-deleted-sizes.txt` і `directories-deleted-numbers.txt`. Пріоритет: середній — не security issue, тільки розмір.

## shared/ концепція — рефакторинг (~2026-05-06)

Папка `~/.openclaw/workspace/shared/` затрекана як plain folder, але реально нічого не шериться між ботами (кожен має повністю свій код). У Фазі 6 cleanup НЕ переносилася в meta — рішення відкладено. Варіанти: (а) перенести в meta/legacy/shared і видалити з workspace; (б) видалити повністю (код там не імпортується); (в) залишити як архів. Перед рішенням — `grep -r "from shared" --include="*.py"` по кожному боту, перевірити фактичні імпорти. Пріоритет: низький, ціль ~2026-05-06.

## Polyrepo vs гібрид decision (~2026-05-06)

Після security cleanup workspace 29.04 структура: 9 окремих repos на GitHub + meta-репо + root уже не git. Працює, але потрібно остаточно вирішити чи залишити polyrepo або зробити гібрид (наприклад, monorepo для тісно пов'язаних або submodules для всього). Контекст: частковий audit показав що одні боти ділять стиль/інфраструктуру (Abby, Garcia — beauty/design), інші стоять окремо (Sam — AI assistant, Insilver — jewelry). Пріоритет: низький, обговорити через тиждень коли впорядкуванням все осяде.

## insilver-v3-dev local copy має PII (2026-04-29)

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

## insilver-v3: prod/dev sync + memory model (P1)

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

### Sam queue застрягає на NBLM-обмеженнях (2026-05-02, ROOT CAUSE)

**Симптом:** `/regen --only podcast_nblm` для 12 тем — 12 готові за ~2 години, далі pipeline стає на 13-й (`production_reliability-5`). Решта 7 тем не стартують навіть через години. Виглядає як "queue не завершується".

**Реальна причина (знайдена 02.05 діагностикою на гарячу):**
NBLM накопичує артефакти в notebook-ах: за квітень кожен notebook зібрав 10-15 готових артефактів (audio, slides, infographic, video). Коли Sam просить новий audio через CLI `notebooklm generate audio -n <id>`, NBLM відмовляє (ймовірно ліміт на кількість артефактів у notebook-у), повертаючи `rc=1` з ПОРОЖНІМ stderr — без чіткої причини відмови. Код у `core/content_gen/backends/nblm.py` інтерпретує це як rate-limit і ставить retry на 3600s. Через `RETRY_DELAYS=[3600]*71` загальний цикл — до 72 годин послідовно. Pipeline послідовний → інші теми чекають за застряглою.

**Той самий клас проблеми у двох симптомах сьогодні:**
- `rag_retrieval-1`: `No all artifacts found` — артефакти зникли з NBLM, але JSON тримав `status=ready` з URL (zombie ready).
- `production_reliability-5`: 12+ накопичених артефактів — новий audio не пускається.

**Що треба:**

1. **Розпізнавання rc=1 зі stderr=""** у `core/content_gen/backends/nblm.py` — НЕ припускати rate-limit за замовчуванням. Логувати reason як "unknown" + робити `notebooklm artifact list` для діагностики (артефактів забагато? notebook порожній? auth fail?).

2. **Скоротити `RETRY_DELAYS`** з 72h sequentially до чогось розумного. Наприклад `[300, 600, 1800, 3600]` (5 хв, 10 хв, 30 хв, 1 год) — 4 спроби максимум, потім `failed`. Залежить від API behavior — потребує тесту.

3. **Зачистка старих артефактів** — або ручна (CLI `notebooklm artifact delete` якщо існує), або автоматична: перед новим `generate audio` видаляти старі audio-артефакти в тому ж notebook-у.

4. **Stale task_id fallback** (вже відомий, P1) — `Wait <id>: status=timeout` крутиться в логах паралельно (video 19826355 + 7af67aad). Окрема задача, але того ж класу: NBLM API state vs Sam state desync.

**Поточний стан після сесії 02.05:**
- 12 нових подкастів готові (`agent_architecture-2/3`, `production_reliability-2/3/4`, плюс попередні).
- 8 тем pending: `production_reliability-5` (застрягла в retry), `multi_model_orchestration-1/2`, `system_operations-2/3/4/5`, `rag_retrieval-1` (reset).
- Sam продовжує retry-loop на `production_reliability-5` до ~03.05 19:26 (72h ETA), решта чекають за нею.
- Український brief через CC в коді (`core/content_gen/brief.py` + `presets.py`), не активований — потребує restart Sam після того як зачистимо стан.

**Пріоритет:** P1. Блокує full curriculum generation через NBLM. Без зачистки + кращої обробки rc=1 кожна нова тема може ламати pipeline на дні.
## Sam — NBLM tech debt (2026-05-03, post-діагностики)

**Контекст:** 03.05 при розборі 8 застряглих тем виявлено що поряд з відомою проблемою накопичених артефактів є ще 4 окремих баги, які разом створюють відчуття "крива інтеграція з NBLM". 16 з 18 podcast-ів зараз ready, 2 теми застрягли (`rag_retrieval-1`, `system_operations-5`) на цих багах. Не блокує SAM щодня, але точково кусає при кожному `/regen` нової теми.

**Стратегія:** перш ніж рефакторити цілий модуль `core/content_gen/backends/nblm.py` — пройти шлях "diagnostic → точкові інтервенції → big refactor як окремий plan". Між інтервенціями писати Ed-suite на NBLM happy path + rc=1 path, інакше регресій не помітимо до прода.

### Підзадачі

#### 1. Reuse-by-title повертає root list UUID (P2)

**Симптом:** для `rag_retrieval-1` Sam reuse-нув notebook UUID `0daaf506-53db-4e78-b08a-1016082af708`, але цей UUID вказує на **список notebook-ів** в NBLM, а не на конкретний notebook. RPC GET_NOTEBOOK і ADD_SOURCE падають.

**Гіпотеза:** reuse-by-title логіка десь в backends/nblm.py при missing записі у notebook_id повертає або кешує root list UUID замість легітимного або None. Можливо це орфан з минулих сесій що залишився в `topics[].nblm_notebook_id`.

**Дослідити:** як саме формується reuse у backends/nblm.py; де живе кеш title→UUID; чому `0daaf506` UUID присвоївся темі.

#### 2. Auto ADD_SOURCE при кожному /regen засмічує notebook (P2)

**Симптом:** при кожному `/regen --only podcast_nblm` Sam викликає ADD_SOURCE незалежно від того чи source вже там є. Підтверджено: cleanup `2d0285dd` notebook-у в NBLM UI до 1 source — наступний `/regen` додав ще один. Це робить ручний cleanup марним.

**Фікс:** перед ADD_SOURCE — GET notebook sources → перевіряти чи source вже є → skip якщо так. Idempotency check.

**Розмір:** ~30 хв коду + Ed-test.

#### 3. Silent rc=1 detection improvement (P2)

**Симптом:** NBLM повертає `rc=1` без structured error для `system_operations-5` після cleanup sources. Sam інтерпретує це як rate-limit і ставить 72h retry-loop. Cleanup не допоміг — root cause silent rc=1 не sources count, а щось інше (можливо quota per-notebook на podcast generation, soft-deleted artifacts, NBLM internal state).

**Фікс:** розрізнити в nblm.py три кейси:
- rc=1 з structured error response → одразу failed з error message (як rag_retrieval-1)
- rc=1 silent (порожній stderr) → НЕ припускати rate-limit; логувати "unknown reason" + одна-дві спроби з малим backoff → потім failed
- справжній rate-limit (якщо API повертає specific signal) → стандартний retry-loop, але скорочений з 72h до ~4 годин

**Розмір:** ~30 хв коду + Ed-test, але треба спочатку зрозуміти що NBLM реально повертає (Інтервенція 1 — diagnostic).

#### 4. Brief generator JSON parse fail на укр промпті (P2)

**Симптом:** після активації укр-перекладу `core/content_gen/brief.py` Haiku ламається на JSON output: `Expecting ',' delimiter: line 17 column 331 (char 1124)`. Fallback brief спрацьовує (тому `/regen` все ж формує deepdive angle), але якість brief погіршена.

**Гіпотеза:** Haiku гірше тримає JSON структуру при українському промпті з спеціальними символами / довгими рядками / лапками всередині українських слів. Можливо треба `response_format: json` або більш суворий prompt template.

**Дослідити:** додати `log.debug` повного raw output Haiku перед JSON parse → побачити де саме ламається. Спробувати: (а) перенести Haiku → Sonnet тільки для brief; (б) дешевше — переписати укр-промпт щоб key_concepts/focus_questions були англомовними field names з українським content; (в) використовувати tools API замість JSON-in-text.

**Розмір:** ~1 година з тестами.

#### 5. nblm_notebook_id consolidation refactor (P3, big plan)

**Контекст:** mapping тема→notebook живе в трьох місцях паралельно:
- `topics[].nblm_notebook_id` (canonical?)
- `topics[].notebook_id` (часто None навіть коли nblm_notebook_id заповнено)
- `topics[].formats.video.url` (вказує на той самий notebook через URL)
- `topics[].formats.podcast_nblm.notebook_id` (часто None)

При reuse Sam дивиться в `nblm_notebook_id` (не в `notebook_id`), а інша логіка можливо в інших полях. Це джерело дублів в NBLM UI ("🏆 LLM Evaluation Tools" ×3, "🔍 Graceful Degradation Patterns" ×2, etc.) і поточних reuse-багів.

**План:** окрема сесія архітектурного дизайну: одне canonical поле `topics[].nblm_notebook_id`, всі інші deprecated через shim як у Phase B. Schema migration з backward-compat. Після консолідації — переглянути reuse-by-title логіку (можливо непотрібна якщо canonical поле завжди заповнене).

**Розмір:** 1 повна сесія + ~1 сесія тестів. **Не починати без diagnostic (Інтервенція 1) і фіксу пунктів 1-4 — інакше рефакторинг внесе нові регресії.**

### Послідовність робіт

**Сесія 1 (наступна):** Diagnostic — знайти `nblm` CLI на Pi5, прямий виклик на `2d0285dd` для ізоляції Sam-bug vs NBLM-bug; прочитати `core/content_gen/backends/nblm.py` цілком; записати inputs/outputs.

**Сесія 2:** Інтервенції 2 + 3 (idempotent ADD_SOURCE + rc=1 detection) разом, з Ed-suite на NBLM happy path.

**Сесія 3:** Інтервенція 4 (brief.py укр JSON fix).

**Сесія 4 (через тиждень-два):** Інтервенція 1 (reuse-by-title bug) — після того як diagnostic дасть розуміння джерела `0daaf506`.

**Сесія 5+:** big refactor (consolidation) — окремий план, тільки якщо value виправдане після інтервенцій 1-4.

**Пріоритет загалом:** P2. Не блокує щодня (16/18 тем ready, AntennaPod feed live), але кожна нова тема — потенційно ще одна `system_operations-5`. Розв'язати протягом 2-3 тижнів.

**Примітка:** попередня секція `### Sam queue застрягає на NBLM-обмеженнях (2026-05-02, ROOT CAUSE)` вище — частково застаріла після 03.05. Її пункти (1) і (2) (silent rc=1, скорочення RETRY_DELAYS) увійшли сюди як підзадача 3 з розширеним контекстом. Зачистка артефактів (3) — вирішена частково (cleanup sources не допоміг, шукаємо інший корінь). Stale task_id (4) — окрема задача, не торкалось 03.05. Старий запис можна або видалити, або помітити `[superseded by 2026-05-03 entry]` — на твій розсуд.

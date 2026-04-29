
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


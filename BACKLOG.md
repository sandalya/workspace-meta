
## Workspace git-структура: submodules без .gitmodules (2026-04-28)

Git-структура workspace має аномалії: корінний `workspace/.git` має у своєму index 8 submodules (abby, abby-v2, ed, household_agent, insilver-v2, insilver-v3, kit, sam-v2 — visible у `git ls-files --stage | grep 160000`), але **немає .gitmodules файлу**. Окремо існують embedded repos (garcia/, meta/, sam/, shared/) які НЕ зареєстровані як submodules. Це можливо corrupted state або legacy setup. 

Варіанти:
- (А) .gitmodules був видалений, потрібно його відновити з `git config -f .gitmodules` або скопіювати з backup'у
- (Б) Це штучна структура яка працює — залишити як є (verify що все синхронізується коректно)
- (В) Переміграти на чистий submodule setup з proper .gitmodules

Пріоритет: низький. Backup цьому не заважає (буде бекапити .git/ директорії самі по собі). Цінність: середня — залежить від того чи git-команди на workspace роблять те що потрібно.

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


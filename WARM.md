---
project: meta
updated: 2026-05-15
---

# WARM — meta

## Триярусна пам'ять — структура проекту

```yaml
last_touched: 2026-05-05
tags: [infrastructure, memory]
status: active
```

Проект використовує три файли для управління контекстом:
- **HOT.md** — переписується щосесії, поточний крок і результати (~60 рядків).
- **WARM.md** — архітектура, рішення, відкриті питання (~400 рядків, оновлюється інкрементально).
- **COLD.md** — append-only історія, архіви завершених фаз.

Структура прийнята 2026-04-23. Скрипт `chkp` автоматизує оновлення через Haiku (fallback Sonnet). Claude-інстанції читають HOT+WARM на старті сесії (Rule Zero в MEMORY.md).

## Архітектурна міграція 2026-04-23

```yaml
last_touched: 2026-04-23
tags: [architecture, migration, infrastructure]
status: active
```

**Зміна:** Kit тепер лише dev-агент. Meta-репо містить:
- `chkp` — checkpoint скрипт для оновлення HOT/WARM/COLD
- `BACKLOG` — перенесено з кореня, єдиний список завдань
- `notes/` — документація та медитації
- `scripts/` — утилітарні скрипти
- `workspace/.env` — fallback з API key з kit (масковано до 4 символів)

HOT файли всіх 6 проектів синхронізовані і оновлені. Дублікати .env на очищення.

## API keys — per-agent, свідомо

```yaml
last_touched: 2026-04-23
tags: [architecture, api-keys, costs]
status: decided
```

**Кожен бот має свій `ANTHROPIC_API_KEY`** у своєму `<project>/.env`. Це НЕ технічний борг — це свідоме рішення для роздільного трекінгу витрат по агентах через Anthropic Console.

Стан на 2026-04-23: 9 окремих ключів (abby, abby-v2, ed, garcia, household_agent, insilver-v3, kit, sam, sam-v2; insilver-v2 — legacy, порожній).

**`workspace/.env`** — fallback-рівень з ключем Kit. Використовується лише для `meta`/`kit` операцій (`chkp`, адмін-скрипти), які не належать жодному боту.

**ПРАВИЛО для майбутніх Claude-сесій:** НЕ пропонувати "консолідувати .env в один файл" — це зруйнує cost tracking. Якщо побачиш дублі — це фіча.

## Компоненти

```yaml
last_touched: 2026-05-15
tags: [infrastructure, chkp, caching]
status: active
```

- **chkp v3.5** — checkpoint скрипт з WARM diff-mode (warm_ops парсер)
  - `/home/sashok/.local/bin/chkp` Python shim, викликає chkp.py v3.5
  - **WARM diff-mode (2026-05-05):** Нова система warm_ops: парсер + серіалізатор для інкрементальних оновлень WARM
    - 5 операцій: touch (update last_touched), update_field (status/tags), add (нові блоки), move_to_cold (архіви), replace_body (контент)
    - Серіалізатор обертає операції назад у YAML/markdown
    - Backward-compat: legacy WARM без field = default (status=active, tags=[], last_touched=None)
    - Economia: 16k→3.4k tokens (79%) на першому прод-чекпоінті (insilver-v3, commit 4580c35)
    - Чекпоінт завершився за 15с замість 5 хвилин (legacy full-WARM)
    - Unit-тести: 16/16 passed (parse, serialize, apply для всіх операцій)
    - Перший прод-чекпоінт (insilver-v3): JSON malformed на першому запуску, самопоправився на retry. P3 потреба: explicit retry-loop.
    - Ready для масштабування на інші проекти (garcia, abby-v2, ed, sam)
  - **Backlog validation (2026-05-06):** validate_backlog_flags() pre-flight check
    - Fail loud (exit 2) з fuzzy hints коли --backlog-strike або --backlog-add не матчать BACKLOG.md
    - difflib.get_close_matches: top 3 результати, cutoff 0.4
    - _check_backlog_match() helper — single source of truth для strike/add validation
    - Валідує ДО Haiku call, без витрати API токенів
    - 26/26 pytest PASS (19 старих + 7 нових)
    - Ловить mismatched BACKLOG headers, як bug вчора (commit 3e67fa5+00defa1)
  - **apply_backlog_flags() robustness (2026-05-15):** 4 fixes + 22 new tests (48/48 pass)
    - Fix 1: multi-match bug — context-aware line selection by line number + fragment context (не заст replace(,1) на перший матч у файлі)
    - Fix 2: replace edge case — strip leading/trailing whitespace from FRAGMENT before matching
    - Fix 3: validation pre-flight check improvement — better error messages for silent-skip scenarios
    - Fix 4: test expansion — 4 new test files (test_apply_backlog_multi_match.py, test_silent_skip.py, test_replace_edge_cases.py, test_strikethrough_parsing.py)
    - 22 new unit tests + 26 existing = 48/48 pass
    - Ready for production validation on live chkp runs
  - **suggest_backlog_strikes() auto-proposal (2026-05-15):** Semantic drift fix
    - Problem: syntactic validations work, but semantic issue remains — AI doesn't link session output to BACKLOG closures
    - Solution: second Haiku call after HOT generation, proposes strikes based on ## Now/Last done vs BACKLOG content
    - UX: interactive y/n/edit/skip block (30s timeout), validates proposed strikes on true BACKLOG matches
    - --no-backlog-suggest flag for automation opt-out
    - max_tokens=1000 (compact JSON), no-changes graceful handling
    - 9 new pytest tests: test_backlog_suggest.py (54/54 pass)
    - Feature ready for smoke test on live chkp, expected 95%+ accuracy after first week
  - **Strikethrough rule enforcement (2026-05-06):** двійна фіксація правила
    - CLAUDE.md agent-docs (секція Backlog): посилено header rule про strikethrough з прикладами
    - BACKLOG.md header: додано візуальний STOP блок із алгоритмом обробки невалідних форматів
    - Виправлено невірний шлях /workspace/BACKLOG.md → /workspace/meta/BACKLOG.md в посиланнях
    - CC-тест (summarize active items) PASS: закреслені пункти більше не повертаються як активні
    - Гіпотеза: header у середині 40K файлу потребує дублювання правила для надійності (слабкий сигнал для LLM)
  - max_tokens=2000 достатній для diff-mode HOT
  - xclip guard: DISPLAY check перед викликом + stderr=DEVNULL для SSH без X11
  - PATH binary migration (2026-05-04): Python shim у ~/.local/bin замість bash v1 скрипту
  - Інтерактивний y/n/e/s для ухвалення AI-пропозицій щодо HOT/WARM
  - Per-project commits у meta для не-meta проектів
  - Backlog read-only: Haiku спостереження, користувач редагує вручну
  - PROMPT.md commit flow (2026-05-03): write_prompt_md() перед git add -A
  - chkp guard (2026-05-03): warn про dev-каталог тільки коли cwd == project + '-dev'

- **BACKLOG** — центральна дошка завдань для всього workspace (read-only для chkp)
  - Формат: нумеровані пункти, статус (DONE/TODO/BLOCKED), залежності
  - 2026-05-15: Видалено невалідний пункт про shared/ refactor — audit показав що shared/ активна бібліотека (sam 11 imports, garcia 7 з наслідуванням, insilver 1, meta/digest 2), не архів
  - 2026-05-15: Видалено застарілий пункт про household_agent .git (239M) — gallery-dl/pinterest уже очищено ~4 травня через filter-repo
  - 2026-05-06: Validation улучшена — backlog flags тепер fail loud з fuzzy hints
  - 2026-05-06: Strikethrough правило посилено у header — STOP блок з прикладами
  - Актуальна послідовність: пункти 1-5 DONE, пункти 6-11 TODO

- **workspace/.env** — ключі на рівні workspace, fallback для 9 проектів
- **6 основних проектів** — кожен має HOT.md, WARM.md, COLD.md (локальні для архітектури)
- **Prompt caching (2026-05-05 — closed as P2):** Smoke test 1+2 показали cache_w=14k, cache_r=0. WARM diff-mode (+79% token economy) НЕ вирішує caching (мінімум 1024 tokens для блоку). Beta header залишено для COLD frozen split + output streaming дослідження у Sprint B/C.
- **shared/ переїзд (2026-05-15):** Переміщено shared/ з workspace root у meta-репо як sym-link. sys.path-імпорти працюють. sam (11 imports), garcia (7 з наслідуванням), insilver-dev (1), meta/digest (2) активні. Commit 5b41001.

## Ключові рішення

```yaml
last_touched: 2026-05-15
tags: [architecture, decision]
status: active
```

1. **Единий BACKLOG** — видаля репетицію, центральне джерело істини для завдань.
2. **Rule Zero** — на старті кожної сесії запитати HOT+WARM, не покладатися на пам'ять.
3. **Workspace-level .env** — виключає дублікати ключів у проектах, безпека + мейнтейнебіліті.
4. **Чекпоінт через chkp** — стандартизована процедура оновлення, автоматизація через Claude (Haiku).
5. **Read-only backlog** — AI дивиться на BACKLOG, пропонує спостереження, користувач редагує вручну. Мінімізує помилки chkp.
6. **PATH binary для chkp** — замість bash v1 скрипту в /bin або /usr/bin, v3.5 через Python shim у ~/.local/bin. Уникає версійних конфліктів. Рішення вступило в силу 2026-05-04.
7. **Prompt caching непрактичний для chkp** — архітектура WARM волатильна, ROI нема без переробки. Прийняти 30-90s затримку як норму. Розглянути WARM diff-mode + COLD frozen split в Sprint B/C.
8. **Strikethrough у BACKLOG — двійна фіксація** — правило описано в CLAUDE.md (agent-docs) + BACKLOG.md header (STOP блок) для надійності. LLM потребує дублювання правила у двох точках, інакше слабкий сигнал при обробці 40K файлів.
9. **Auto-backlog-suggest (2026-05-15)** — другий Haiku call закриває semantic drift: AI пропонує закрити пункти що покриваються контекстом, UX блок (y/n/edit/skip), запобігає 11-денним затримкам у страйках.

## Інтеграції

```yaml
last_touched: 2026-04-23
tags: [integration]
status: pending
```

- **kit** ↔ **meta**: Kit надає dev-аванс, meta — управління памʼяттю та контекстом.
- **9 проектів** → **meta**: Центральна памʼять для всіх, локальні WARM/COLD для специфіки.
- **workspace** → **meta**: Единий .env, BACKLOG, scripts.

## Open questions

```yaml
last_touched: 2026-05-15
tags: [open-questions]
status: active
```

- Чи suggest_backlog_strikes() буде ефективна для 90% use-cases, чи потреба більш складної semantic heuristics?
- Чи потреба household_agent sudo restart, чи auto-restart через systemd достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp robustness fixes (multi-match контекст, whitespace strip) на live даних?
- Чи all 4 ботів (ed, garcia, insilver-v3, sam) повинні мати однакову httpx suppression pattern як abby-v2/household_agent, або аудит кожного індивідуально?
- BACKLOG rotation policy для abby images (759M, 1315 files) + sam audio (827M, 26 mp3) — коли зберігати vs. видаляти?
- Потреба BACKLOG hygiene pass (bi-weekly) для видалення obsolete items, чи достатня ad-hoc аудит при smoke test?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot, чи нема пріоритету?

## Workspace structure: post-cleanup polyrepo (2026-04-29)

```yaml
last_touched: 2026-05-04
tags: [architecture, structure, git]
status: active
```

Після security cleanup 29.04 структура workspace:

- **Root `~/.openclaw/workspace/`** — НЕ git репо. Тільки символьні посилання `BACKLOG.md` → `meta/BACKLOG.md`, `CLAUDE.md` → `meta/agent-docs/CLAUDE.md`.
- **8 окремих GitHub repos** (один per бот, абby-v1 видалено 2026-05-04): abby-v2, ed, garcia, household_agent_v1, insilver-v3, openclaw-kit, sam, workspace-meta. Insilver-v2 видалено з GitHub (legacy). **abby-v1 видалено з GitHub 2026-05-04, локальна папка на видалення.**
- **meta-репо** — централізована інфраструктура: `agent-docs/` (12 root-level md), `BACKLOG.md`, `chkp/` (Python v3.4), `legacy/chkp_bash_v1/` (reference, на видалення після PATH перевірки), `backup/` (тільки скрипти, runtime archives живуть у workspace/backup/), `systemd-services-backup/`.
- **shared/** — лишається в workspace як plain folder, поза будь-яким git tracking. Не імпортується з ботів. Доля невирішена (BACKLOG: shared/ рефакторинг ~2026-05-06).
- **Runtime файли в root** (не tracked): `memory/`, `.checkpoint_tracker.json`, `.openclaw/workspace-state.json`, `.env`, `health_monitor.log`.

**Чому НЕ submodules з .gitmodules:** в audit виявили що раніше root репо мав 8 dangling gitlinks без `.gitmodules` — corrupted state. Замість виправлення обрали повне видалення root .git: кожен sub-проект самодостатній, meta тримає workspace-level контент. Уникає sync-проблем submodules.

**Force-push контракт:** для прод ботів чистка історії (filter-repo) виконується тільки коли:
1. Всі скомпрометовані секрети revoked (TG @BotFather, PAT GitHub).
2. Бекап локально є.
3. Бот зупинено через systemctl на час filter-repo (щоб не писав у файли що зараз видаляються).
4. Стейл-гілки на GitHub перевірено окремо (filter-repo їх не торкає).

## Security cleanup ритуал — як робити next time (2026-04-29)

```yaml
last_touched: 2026-04-29
tags: [security, git, runbook]
status: active
```

**Pre-flight (перед filter-repo на будь-якому репо):**

1. `pip install git-filter-repo --break-system-packages` (один раз).
2. Бекап усього workspace: `tar -czf ~/workspace-backup-$(date +%Y%m%d-%H%M).tar.gz -C ~/.openclaw workspace --exclude='*/venv'` (~6-7G).
3. `git status` — clean або stash перед filter-repo (filter-repo робить `git reset --hard` після, dirty edit'и зникають).
4. `systemctl stop <bot>.service` — зупинити бота на час operatsii щоб не писав у файли.
5. Перевірити секрети в історії: `git log --all -p | grep -E '[0-9]{8,12}:[A-Za-z0-9_-]{30,}'` (TG tokens), `... | grep -E 'sk-ant-[A-Za-z0-9_-]{20,}'` (Anthropic).
6. **Якщо знайдено токени — revoke їх ДО filter-repo** (вже валідні токени в кеші клонів зберуть — атакувальник може push'нути зворотньо).

**Filter-repo патерн:**

```bash
git filter-repo --force --dry-run \
  --path FILE1 --path FILE2 \
  --path-glob 'data/*.bak*' \
  --replace-text /tmp/replace.txt \
  --invert-paths
```

`/tmp/replace.txt` — формат `LITERAL_TOKEN==>***REVOKED***`, по одному на рядок. Default literal match. Прапорець `--force` потрібен бо filter-repo не вважає workspace "fresh clone".

**Post:**

1. `git remote add origin <URL>` — filter-repo прибирає remote, відновити вручну.
2. Перевірити dry-run перед real (`fast-export.original` vs `fast-export.filtered`).
3. `git push --force origin main` — переписує історію на GitHub.
4. Перевірити інші гілки: `git fetch origin && git ls-remote --heads origin` — якщо є стейл-гілки з PII, видалити: `git push origin --delete BRANCH`.
5. Оновити `.gitignore` (filter-repo міг скинути edit'и) → commit + push.
6. Запустити бот назад: `systemctl start <bot>.service`.

## Remote dev infrastructure (2026-04-30)

```yaml
last_touched: 2026-04-30
tags: [infrastructure, remote-dev, tmux]
status: active
```

**Комбо для роботи в дорозі з телефона (Android):**

1. **Tailscale** — VPN тунель Pi5 ↔ Android телефон. Приватна мережа, всі сервіси доступні через IP Pi5 у локальній мережі Tailscale.
2. **Termius** — SSH клієнт для Android. Підключено до Pi5, автоматичні переконекти при розривах зв'язку.
3. **tmux** — session manager на Pi5. Переживає разові обриви connection, дозволяє детач/реаттач з різних клієнтів.
   - Alias: `w` = `tmux new -A -s work` (нова сесія або увійти в існуючу).
   - Базові команди: `Ctrl+B D` (детач), `tmux attach -t work` (реаттач), `tmux ls` (список сесій).
   - **Обмеження:** tmux НЕ переживає reboot Pi5 — сесії зникають у RAM. Потреба скрипту для restore на startu.

**Workflow:** 1) Termius → SSH на Pi5. 2) `w` = enter work tmux. 3) На розриві: Ctrl+B D детач. 4) При реконекті: `tmux attach -t work` → повернення в той же місце.

**TODO (2026-05-06):**
- Розділити сесії per-проект: `abby`, `garcia`, `sam`, etc. (можна паралельно монітояти кілька).
- Написати `tmux-restore.sh` на старті Pi5 → восстановити попередні сесії з файлу `.tmux-sessions`.
- Розглянути systemd service для auto-restore на boot.

## Sam NBLM tech debt — série підзадач (беклог)

```yaml
last_touched: 2026-05-05
tags: [sam, nblm, tech-debt, p2]
status: next
```

**Серія 5 підзадач з беклогу Sam NBLM (реорганізовано 2026-05-04):**

**Статус: DONE (попередні цикли)**
1. ~~**Інтервенція 0 — sam.service bootstrap** (завершено в security cleanup цикл)~~
2. ~~**Інтервенція -1 — nblm backend review** (завершено в prep for P2)~~
3. ~~**Інтервенція -2 — dependency map** (завершено в security cleanup)~~

**Статус: TODO (черга активна, после zombie fix + PATH verification)**
4. **Інтервенція 1 — dangling UUID detection** (30 хв, NEXT):
   - файл: `sam/core/content_gen/backends/nblm.py`
   - метод: `get_or_create_notebook`
   - проблема: UUID 0daaf506 (rag_retrieval-1), 2d0285dd на notebook'и що не існують
   - рішення: `probe source list -n --json` перед reuse, інвалідувати `nblm_notebook_id` якщо RPC fail/null
   - fallthrough на create
   - перевірка: `sam.service restart`, manual test у sam/notebooks
   - розблокує: rag_retrieval-1

5. **Інтервенція 2** — (待 визначення після завершення Inter 1)
6. **Інтервенція 3** — (待 визначення)
7. **Інтервенція 4** — (待 визначення)
8. **Інтервенція 5** — (待 визначення)

**Контекст:** v3.4 chkp пристрій повністю стабільний, готовий до повноцінного робочого використання. Перехід до Sam NBLM tech debt — живі P2 з беклогу. abby-v1 видалення + Swift 4 чекпоінти інфраструктури завершено, готово до Inter 1 після zombie fix.

## Memory auto-fetch для публічних репо (2026-05-03)

```yaml
last_touched: 2026-05-03
tags: [memory, infrastructure, web-integration]
status: active
```

**Гібридний режим читання пам'яти:**

- **Публічні репо** (sam, ed, workspace-meta) — memory rule #21 активовано: HOT.md читаються через `web_fetch` на raw.githubusercontent.com/openclaw-ai/<repo>/main/HOT.md. Перевірено що доступ без auth.
- **Приватні репо** (insilver-v3, abby-v2, garcia, household_agent) — залишаються на ручному читанні: `cat HOT.md WARM.md` як інструкція у claude.ai на старті сесії.
- **kit** — ще не мігрований на нову HOT/WARM/COLD пам'ять, залишається на legacy інструкціях до розгляду.

**Причини гібридизації:**
- Публічні репо: вихідні файли, немає auth бар'єрів, стабільний raw.githubusercontent.com доступ.
- Приватні репо: не можна публіковано fetch без PAT, ручна читання безпечніша й контрольована.
- kit як агент: особлива роль (dev-інтеграція), міграція планується окремо.

**Верифікація:**
- sam HOT.md: доступен на raw.github
- ed HOT.md: доступен на raw.github
- workspace-meta HOT.md: доступен на raw.github
- Приватні репо: ручна cat інструкція у MEMORY.md задокументована.

**Next:**
- kit міграція на HOT/WARM/COLD структуру (коли буде час).
- Документувати rule #21 у notes/ як публічні + приватні пам'ять читаються у multi-project setup.

## insilver-v3-dev pre-push patterns (2026-05-04)

```yaml
last_touched: 2026-05-04
tags: [insilver, git, pre-push, security]
status: active
```

**Pre-push hook конфіги:**
- **Telegram client-ID формат:** `[0-9]{9,}_.*` (мінимум 9 цифр, потім підкреслення + будь-що). Перевіряє чи не випадково не закомітити TG client ID.
- **Фото шляхи (білий список):** `data/photos/incoming/` та `data/photos/clients/` дозволені (список клієнтів, робочі дані). `data/photos/static/` явно дозволена (публічні активи).
- **Раніше:** Blanket `.jpg/.jpeg/.png` на заборону. **Тепер:** Видалено, замінено на специфічні шляхи — менше false positives, вищі точність детектування.
- **Комітовано:** У insilver-v3-dev/.git/hooks/pre-push.

**Причини спеціфіки:** Фото клієнтів (189793675_*.jpg) кілька років назад забуті в історії insilver-v3, security cleanup 2026-04-29 їх вилучив. Тепер hook запобігає повторенню.

## WARM diff-mode v3.5 (warm_ops інтеграція)

```yaml
last_touched: 2026-05-05
tags: [infrastructure, warm-ops, optimization, p1]
status: active
```

**WARM diff-mode через warm_ops парсер — live у продакшені з 2026-05-05:**

Замість переписування всього WARM щосеанс, chkp v3.5 генерує компактний список операцій (warm_ops JSON). Це скорочує output tokens з 16k до 3.4k (79% економія) та прискорює чекпоінти з 5 хв до 15 сек на першому прод-чекпоінті (insilver-v3, commit 4580c35).

**Архітектура:**
- `meta/chkp/warm_ops.py` — парсер (JSON → операції) + серіалізатор (операції → YAML/markdown)
- 5 операцій: touch, update_field, add, move_to_cold, replace_body
- Backward-compat: legacy WARM без field = default (status=active, tags=[], last_touched=None)

**Перший прод-чекпоінт (insilver-v3, commit 4580c35) 2026-05-05:**
- Economia: 16k→3.4k tokens (79% на WARM output)
- Час чекпоінту: 5 хв → 15 сек
- JSON malformed на першому запуску, автоматичний retry повернув OK
- Операції: 3× touch, 1× update_field status
- Локальна верифікація на garcia, abby-v2, ed, sam: всі dry-run OK

**Статус масштабування (2026-05-05):**
- garcia, abby-v2, ed, sam: локальні dry-run OK, готові до чекпоінтів
- Очікується 50%+ token економія на кожному проекті
- Масштабування заплановано на 2026-05-05 вечір / 2026-05-06 ранок

**P3 потреби:**
- Explicit retry-loop при JSONDecodeError (max retries=2, exponential backoff 1s/2s)
- Документація: JSON graceful degradation у Компоненти блок

**Відмова від prompt caching (2026-05-05):**
WARM diff-mode не вирішує основну проблему caching — мінімум 1024 tokens для cacheable блоку у claude.ai. SYSTEM (577) + MEMORY (393) + warm_ops (~200) = ~1170, на межі. COLD (6114) append-only, але за кожним чекпоінтом grow. ROI нема без більших архітектурних змін (COLD frozen split, output streaming). Закрити як P2. Beta header `prompt-caching-2024-07-31` залишено для майбутніх експериментів (Sprint B/C). Smoke test 1+2 (2026-05-04/05) показали: cache_creation_input_tokens=14.5k на першому виклику, cache_read_input_tokens=0 на другому — мінус, WARM волатильність (Haiku перезаписує) = cache miss неминучий.

## chkp SYSTEM_PROMPT patch — двошарова механіка no-hallucination (2026-05-05)

```yaml
last_touched: 2026-05-05
tags: [chkp, system-prompt, evals, p1]
status: active
```

**Проблема:** Haiku у chkp генерує HOT.md, але ## Now галюцинує (copy-paste з попередньої HOT або WARM замість поточного WHAT WAS DONE THIS SESSION).

**Рішення (двошарове):**

1. **SYSTEM_PROMPT rule 1** — explicit canonical sources per section:
   - ## Now: ONLY from input WHAT WAS DONE THIS SESSION (1–3 sentences, CRITICAL)
   - ## Last done: from WHAT WAS DONE (bullet list, expanding Now)
   - ## Next: from input NEXT STEP
   - ## Reminders: keep from previous if relevant
   - Інші джерела (попередня HOT, WARM) = histórico контекст, не джерела для переписування

2. **_redact_now_for_context() функція** — mechanical enforcement:
   - Видаляє `## Now` і `## Last done` з input HOT перед API-call
   - Уникає що Haiku "зчитує" старий контекст з input
   - Залишає `## Next`, `## Blockers`, `## Active branches`, `## Open questions`, `## Reminders`

**Валідація (2026-05-05):**
- 19/19 pytest PASS:
  - 3 no_hallucination fixtures (fixtures/2026-05-05_meta_chkp_evals.py):
    - morning fix (commit f402d57): minimal SYSTEM_PROMPT edit
    - evening fix (commit f402d57): _redact_now_for_context() додано
    - третя fixture з цієї сесії (input c46cf24): реальний chkp від 2026-05-05 вечора
  - 16 warm_ops операцій (touch, update_field, add, move_to_cold, replace_body)
- Локальна перевірка: `cd meta && pytest chkp/tests/ -v` → PASS
- Code review: SYSTEM_PROMPT правило + _redact_now_for_context() логіка OK

**Production status:**
- Потрібна верифікація на реальних чекпоінтах (insilver-v3, sam, garcia) наступні 2-3 сесії
- Якщо OK → scalability на усі 6 проектів
- Якщо FAIL → дебаг через fixtures додати реальний case

**Уроки:**
- Prompt-only SYSTEM_PROMPT fix недостатній (Haiku часто ігнорує)  
- Mechanical redaction (видалення старого контексту) більш надійна  
- Test fixtures ESSENTIAL — мають реальні input/output від чекпоінтів  
- Beta header: розглянути auto-redaction у всіх MEMORY.md правилах (rule #0 для Rule Zero)

## ~/.claude/settings.json — acceptEdits інтеграція (2026-05-05)

```yaml
last_touched: 2026-05-05
tags: [infrastructure, claude-ai, automation, permissions]
status: active
```

**Setup завершено (2026-05-05):**
- ~/.claude/settings.json містить allow/deny rules для automatyzованого режиму.
- allow: задачі з беклогу (BACKLOG.md патерни), commit messages, code review.
- deny: prod insilver-v3 файли, .env, push до main, sudo команди, journalctl без grep, rm -rf критичних шляхів.
- alias cld = claude --permission-mode acceptEdits — лежить на 15-хвилинну паузу без вручного підтвердження.

**Статус:** Один файл settings без локальних override. Верифіковано. Готовий до тесту на реальній задачі (sam або insilver-v3-dev) для вимірювання накопичення prompts.

**Next:** Запустити тест паузи на 15 хвилин, слідкувати скільки prompts накопичується, оцінити практичність auto mode для вечірньої роботи без активного моніторингу.

## Off-device backup chain — DR infrastructure (2026-05-06)

```yaml
last_touched: 2026-05-06
tags: [infrastructure, backup, disaster-recovery, automation]
status: active
```

**Setup (updated 2026-05-06):**
- **PC (Windows 10, H:\pi_backups):** Daily pull via Task Scheduler (RetentionDays=14, MinHoursBetweenRuns=20)
- **Pi5 (local /home/sashok/backups):** Retention reduced to 3 days (changed from 7 on 2026-05-06)
- **Authentication:** SSH key (~/.ssh/pi5_backup), no password prompt
- **Notifications:** Telegram on error only (weekly summary Sundays 03:00 removed daily noise)
- **GitHub repo:** sandalya/pi5-backup (backup.sh, notify.sh, README.md, exclude.txt, .gitignore, .env.example)

**Verification (2026-05-06):**
- 7 archives synced, md5 match confirmed
- Task Scheduler launches at logon+2min, throttle observed
- SD card freed: 78% → 60% (11G freed via pip cache 3G + npm cache 1.8G + unused .u2net 1.1G + meggi venv rebuild 3.0G→497M)
- meggi venv rebuilt CPU-only (no nvidia/triton), faster-whisper verified working
- .u2net consolidated: kept isnet-general-use.onnx (171M), removed 2 unused models
- Weekly summary triggers Sunday 03:00 only (daily-notify.timer removed)

**Security incident (2026-05-06):**
- Telegram bot token leaked into journalctl through httpx URL logging (household_agent-v1)
- Token rotated via BotFather, valid as of 2026-05-06
- Action: suppress httpx INFO logging across all bots (6 projects) to prevent recurrence
- requirements.txt added to household_agent/ for reproducibility

**Next (DR drill + backup.sh extension):**
- Spare SD card expected → test restore on new SD (full DR drill)
- Extend backup.sh: capture /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list export
- Document restore procedure in README.md

**Backlog (deferred to next session):**
- abby memory/images: 759M (1315 files) — rotation policy decision pending
- sam data/audio: 827M (26 mp3 podcasts) — rotation policy decision pending

## Logging security — httpx token leak suppression (2026-05-06)

```yaml
last_touched: 2026-05-06
tags: [security, logging, httpx, telegram]
status: active
```

**Incident:** Telegram bot token leaked into journalctl via httpx library INFO logs (household_agent-v1). Token included in URL query parameters logged by httpx before request execution.

**Token rotation:** Rotated via BotFather on 2026-05-06, token revoked.

**Root cause:** httpx default logging level (INFO) logs full request URLs including auth tokens. Occurs across 6 projects: abby-v2, ed, garcia, household_agent, insilver-v3, sam.

**Action items:**
1. Add to all bot configs: `logging.getLogger('httpx').setLevel(logging.WARNING)` (suppress INFO/DEBUG)
2. Audit all .log files in workspace for leaked tokens (journalctl rotate retention)
3. Verify requirements.txt pinning in each project includes httpx version (for reproducibility)

**Next:** Suppress httpx INFO across all 6 bots, scan historical journalctl for similar leaks, document in MEMORY.md rule #X (logging security).

## Token tracker — read-only audit (2026-05-15)

```yaml
last_touched: 2026-05-15
tags: [infrastructure, cost-tracking, token-logging, audit]
status: active
```

**Audit결과:** shared/token_log.jsonl функціонує як read-only лог 74 записів з 2026-04-13, формат чистий (ts/agent/in/out/cost). Write-side підключений тільки у digest + garcia. sam/insilver-v3/abby-v2/ed/meggy мають мертвий /stats UI з 0 записів за місяць.

**Статус:** Non-critical. Anthropic Console покриває total spend tracking. Per-bot fine-grained облік — окрема задача в backlog якщо знадобиться у майбутньому.

**Умови:** token_log.jsonl стабільний,継续use для digest/garcia, решта ботів не потребують активування.

**Next:** Потенційне розширення write-side на 4 ботах (ed, garcia, insilver-v3, sam) якщо буде рішення про per-bot облік. Зараз — достатньо Anthropic Console + мертвих /stats UI для загального tracking.

## morning_digest systemd timer — Telegram BACKLOG summary (2026-05-15)

```yaml
last_touched: 2026-05-15
tags: [telegram, automation, backlog-digest, sam-bot]
status: active
```

Автоматичний щоденний digest структури BACKLOG через Telegram. Запущено о 09:00 через systemd timer, відправляється у OWNER_CHAT_ID.

**Компоненти:**
- **meta/digest/morning_digest.py** — парсер BACKLOG.md: інлайн (Pn) маркери (P1-P4), closed sections (~~strikethrough~~), uncategorized items (13 шт)
- **Haiku 4.5 синтез** — берає структуру BACKLOG, генерує резюме зі збереженням мови оригіналу, чиста відповідь без пояснень
- **HTML parse_mode** — Telegram mensages: розриви строк, моноширинні блоки для пункт-списків
- **systemd timer** — meta/digest.timer (09:00 daily), meta/digest.service (Python runner)

**Конфіг (meta/digest/.env):**
- SAM_BOT_TOKEN (Telegram бот від @BotFather, реюз з sam)
- OWNER_CHAT_ID (цільовий чат для digest, тільки читання)
- ANTHROPIC_API_KEY (реюз із sam/.env для Haiku звернень)

**Статус (2026-05-15):**
- Парсер: 11/11 unit-тестів PASS
- Cost: ~0.0026 USD per run (~0.08 USD/month на автоматизації)
- Результат першого run: p1=0, p23=3 uncategorized=13, done=0 (структура BACKLOG задокументована)
- Системний timer: ready для 09:00 trigger завтра
- Інцидент: Sam-бота токен витік у claude.ai чаті через неправильну sed маску (=.\{4\}$ замість =.*), ротовано через @BotFather 2026-05-15, sam.service рестартнуто

**Next:**
- Перевірити завтра (2026-05-15 вечір / 2026-05-16 ранок) що timer 09:00 відпрацював
- Додати (Pn) маркери до решти uncategorized пунктів для кращої пріоритезації
- Розглянути frequency adjustment: щодня vs. раз на 2 дні (залежно від BACKLOG активності)

## Anthropic SDK cost isolation — shared/agent_base.py fix (2026-05-14)

```yaml
last_touched: 2026-05-14
tags: [api-keys, costs, shared-library, anthropic-sdk]
status: fixed
```

**Проблема:** shared/agent_base.py line 20 — `client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])` без load_dotenv(). Anthropic SDK के find_dotenv() автоматично підхоплював workspace/.env з kit3 ключем, замість проектних .env файлів. Це привело до витрат на kit3 ключі для abby-v2, household_agent, ed-bot.

**Діагностика (2026-05-14):**
- ed-daily.timer: зупинений, judge використовував Haiku (витрати в kit3 ключі)
- abby-v2, household_agent: find_dotenv() підхоплювали workspace/.env замість проектних
- sam-rss, insilver-v3-error-monitor: перевірені, Anthropic SDK не кличуть

**Рішення:**
1. Додано `EnvironmentFile=<path>/.env` в systemd-юніти abby-v2.service та household_agent.service
2. ed-daily.timer: перевірено, timer поновлено
3. shared/agent_base.py: поточна версія залишена як є (SDK find_dotenv() контролюється через EnvironmentFile)

**Верифікація (завтра, 2026-05-15):**
- AWS Console: kit3 витрати мають обвалитись
- abby-v2, household_agent: мають показати Sonnet+Haiku трафік на власних ключах
- judge семантичні assertions: потреба мануальної регресії для порівняння pass rate з еталоном 37/17/23

**Наслідок:** Кожен проект тепер використовує власний ключ, cost tracking знову окремий по агентах.

## chkp suggest_backlog_strikes — semantic backlog drift fix

```yaml
last_touched: 2026-05-15
tags: [chkp, backlog, automation, design, p1]
status: implemented
```

**Problem:** chkp v3.5 mechanical validations (validate_backlog_flags fail-loud, multi-match context-aware replace) закрили syntactic bugs. Semantic проблема залишилась: AI у claude.ai чаті не звіряє 'що зробили' з активними пунктами BACKLOG, тому --backlog-strike просто не передається. Empirical evidence: 0674dd4 (household_agent filter-repo 240M→612K, 2026-04-05) — чекпоінт є, але strike флага нема, пункт висив 11 днів як incomplete.

**Root cause:** Haiku генерує HOT.md (## Now/Last done/Next), але не знає які пункти BACKLOG мають бути закриті. Користувач при ухвалі результатів лише copy-paste у --backlog-strike, часто забуває або неправильно копіює.

**Solution (implemented 2026-05-15):**
1. **suggest_backlog_strikes()** — після Haiku генерації HOT.md, другий Haiku call бере ## Now + ## Last done, читає BACKLOG.md, генерує список proposed strikes (JSON: [{"line": 3, "text": "...", "action": "strike"}])
2. **UX block y/n/edit/skip** — інтерактивний режим: користувач y (apply all) / n (skip all) / e (edit manually) / s (select subset), timeout 30s
3. **--no-backlog-suggest flag** — opt-out для automation scripts
4. **Validation:** перевіряє proposed strikes на true матчі у BACKLOG (не hallucinate)

**Implementation notes:**
- Haiku call #2 використовує max_tokens=1000 (compact JSON)
- Edge case: ~~closed~~ items у BACKLOG — не видаляти, inform user
- 9 нових pytest тестів додано: test_backlog_suggest.py
- 54/54 unit-тестів PASS (48 existing + 6 new suggest)

**Status (2026-05-15):** Feature implemented, smoke test ready на реальній сесії. Goal 95%+ accuracy за перший тиждень. Масштабування на 6 проектів після верифікації на insilver-v3 або sam.

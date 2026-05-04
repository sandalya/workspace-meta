---
project: meta
updated: 2026-05-04
---

# WARM — meta

## Триярусна пам'ять — структура проекту

```yaml
last_touched: 2026-05-04
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
last_touched: 2026-05-04
tags: [infrastructure, chkp]
status: active
```

- **chkp v3.4** — checkpoint скрипт з PATH binary shim + read-only backlog assistant
  - `/home/sashok/.local/bin/chkp` тепер Python shim що викликає `chkp.py` з аргументами
  - Усунено розбіжність: alias в PuTTY vs PATH binary у CC/subshell/cron
  - update_backlog() генерує текстові спостереження про BACKLOG (без редагування файлу)
  - Видалено JSON-action підхід (чомплікс, false matches)
  - Видалено apply_backlog_changes, commit_backlog, прапор --no-backlog
  - BACKLOG редагується руками через nano після спостережень
  - Використовує Haiku → Sonnet fallback для HOT/WARM оновлень
  - Інтерактивний y/n/e/s для ухвалення AI-пропозицій щодо HOT/WARM
  - Per-project commits у meta для не-meta проектів
  - max_tokens=2000 для повних відповідей (верифіковано 2026-05-04)
  - **xclip guard (2026-05-03):** copy_to_clipboard() перевіряє os.environ.get('DISPLAY') перед викликом xclip. Якщо DISPLAY не існує (SSH без X11) — return False без шуму. stderr=DEVNULL на Popen як defense-in-depth. Ціль: мовчазний fallback на headless системах. Протестовано на Pi5, працює.
  - **PROMPT.md commit flow (2026-05-03):** write_prompt_md() викликається ПЕРЕД git add -A, тому PROMPT.md потрапляє до чекпоінт-комміту. Раніше писався після commit і залишався modified. Видалено дублювання prompt= у output.
  - **chkp guard рефакторинг (2026-05-03):** warn про dev-каталог тільки коли cwd basename == args.project + '-dev' (тобто у dev-каталозі ТОГО Ж проекту що чекпоінтиш). Cross-project (cd insilver-v3-dev && chkp meta) — без warning, бо це штатний workflow. Раніше warn спрацьовував на будь-який cwd закінчуючись на -dev, що було false positive у 90% випадків. Перевірка: `cwd_basename == f"{project}-dev"` перед warn. Рішення мінімізує шум при крос-проектній роботі.
  - **PATH binary migration (2026-05-04):** Перехід з bash v1 скрипту на Python shim у ~/.local/bin. Проблема: PuTTY викликав v3.4 через alias, але CC/subshell/cron потрапляли у системні шляхи з legacy v1. Рішення: shim викликає chkp.py v3.4. Верифікація: `bash -c chkp --help` показує v3.4. SESSION.md видалено, .gitignore оновлено. Потреба перевірки на не-meta (garcia, abby-v2, ed) та видалення legacy скриптів (kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh).
  - **Backlog-strike прецизність (2026-05-04):** Уроки з BACKLOG cleanup: --backlog-strike FRAGMENT мусить бути дослівним підрядком заголовка або рядка беклогу. При неточному фрагменті chkp не знаходить рядок на видалення і повідомляє про невдачу. Рішення: користувач копіює точний текст з BACKLOG перед запуском chkp. Перевірено на пункті 5 (xclip validation).
  - **Status after 2026-05-04:** PATH binary v3.4 запущено на meta, верифіковано на інших проектах потреба (garcia, abby-v2, ed). Legacy скрипти на видалення коли верифікація OK. Інфра готова до P2 + Sam NBLM Inter 1.

- **BACKLOG** — центральна дошка завдань для всього workspace (read-only для chkp)
  - Формат: нумеровані пункти (1-11+), статус (DONE/TODO/BLOCKED), залежності
  - 2026-05-04: видалено NBLM-05-02 (28 рядків superseded), реорганізовано Sam NBLM як 5 Інтервенцій
  - Актуальна послідовність: пункти 1-5 DONE (чkp infrastructure, abby-v1 GitHub deletion), пункти 6-11+ TODO (PATH verification, legacy cleanup, Sam Inter 1)
  - Статус 2026-05-04: пункти 1-5 закриті, лишилось 11 пунктів

- **workspace/.env** — ключі на рівні workspace, fallback для 9 проектів
- **6 основних проектів** — кожен має HOT.md, WARM.md, COLD.md (локальні для архітектури)
- **Legacy скрипти (status 2026-05-04):**
  - kit/chkp.sh (v1 reference) — на видалення після перевірки на не-meta
  - kit/chkp2.sh (тест v2) — на видалення після перевірки на не-meta
  - meta/legacy/chkp_bash_v1/chkp.sh (копія v1) — перенесено, на видалення після перевірки
  - meta/chkp.py.bak (backup v3.0) — залишено для git історії
  - SESSION.md (артефакт v1) — видалено, додано в .gitignore

## Prompt caching infrastructure (2026-05-04)

```yaml
last_touched: 2026-05-04
tags: [infrastructure, prompt-caching, api, optimization]
status: baseline-setup
```

**Baseline smoke test 1 (2026-05-04):** Setup завершено. Інструкція додана у claude.yaml (Claude API config на claude.ai): див. MEMORY.md rule #42. Метрика: cache_creation_input_tokens > 0 на першому виклику означає успішну кешізацію. На другому та наступних викликах — cache_read_input_tokens повинен відобразити переиспользование кешованого контенту. **Next:** Першого claude.ai запиту з prompt caching instructions (на наступну сесію для інших проектів) → перевірити response_metadata → документувати у notes/PROMPT-CACHING.md. Rozглянути можливість автоматизації cache refresh через `chkp` системи (якщо помінявся HOT/WARM) — для Sprint B або C.

## Ключові рішення

```yaml
last_touched: 2026-04-23
tags: [architecture, decision]
status: active
```

1. **Единий BACKLOG** — видаля репетицію, центральне джерело істини для завдань.
2. **Rule Zero** — на старті кожної сесії запитати HOT+WARM, не покладатися на пам'ять.
3. **Workspace-level .env** — виключає дублікати ключів у проектах, безпека + мейнтейнебіліті.
4. **Чекпоінт через chkp** — стандартизована процедура оновлення, автоматизація через Claude (Haiku).
5. **Read-only backlog** — AI дивиться на BACKLOG, пропонує спостереження, користувач редагує вручну. Мінімізує помилки chkp.
6. **PATH binary для chkp** — замість bash v1 скрипту в /bin або /usr/bin, v3.4 через Python shim у ~/.local/bin. Уникає версійних конфліктів. Рішення вступило в силу 2026-05-04.

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
last_touched: 2026-05-04
tags: [open-questions]
status: active
```

- Чи cache_creation_input_tokens показується в claude.ai response або тільки при API debug?
- Видалити kit/legacy скрипти одним commit'ом чи per-project?
- Чи потреба .gitignore update у kit після видалення chkp.sh, chkp2.sh?
- Чи abby-v1 локальна папка (~/openclaw/workspace/abby-v1/) розглядається как окремий проект чи просто видалити вручну?
- Як часто запускати `chkp` для backlog analysis? Чи варто в systemd timer?
- Список конкретних .env дублікатів на видалення — які проекти мають локальні копії?
- ROADMAP/IDEAS — при якому стані тестування почати заповнювати?
- Чи потреба синхронізувати інші файли на рівні meta (config, templates)?
- Чи збережувати legacy папка як reference чи видалити всередину?
- Чи pre-commit hooks однакові для всіх проектів чи per-project?
- Чи pre-push patterns синхронізуються у workspace/.env або локально в кожному проекті?
- Чи cache refresh потребує окремої інструкції у chkp коли HOT/WARM змінилися?

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
last_touched: 2026-05-04
tags: [sam, nblm, tech-debt, p2]
status: next
```

**Серія 5 підзадач з беклогу Sam NBLM (реорганізовано 2026-05-04):**

**Статус: DONE (попередні цикли)**
1. ~~**Інтервенція 0 — sam.service bootstrap** (завершено в security cleanup цикл)~~
2. ~~**Інтервенція -1 — nblm backend review** (завершено в prep for P2)~~
3. ~~**Інтервенція -2 — dependency map** (завершено в security cleanup)~~

**Статус: TODO (черга активна, после PATH verification)**
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

**Контекст:** v3.4 chkp пристрій повністю стабільний, готовий до повноцінного робочого використання. Перехід до Sam NBLM tech debt — живі P2 з беклогу. abby-v1 видалення + Swift 4 чекпоінти інфраструктури завершено, готово до Inter 1.

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

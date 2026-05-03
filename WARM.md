---
project: meta
updated: 2026-05-03
---

# WARM — meta

## Триярусна пам'ять — структура проекту

```yaml
last_touched: 2026-04-23
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
last_touched: 2026-05-03
tags: [infrastructure, chkp]
status: active
```

- **chkp v3.4** — checkpoint скрипт з PATH binary shim + read-only backlog assistant
  - `/home/sashok/.local/bin/chkp` тепер Python shim що викликає `chkp.py` з аргументами
  - Усунено розбіжність: alias в PuTTY vs PATH binary у CC/subshell/cron
  - update_backlog() генерує текстові спостереження про BACKLOG (без редагування файлу)
  - Видалено JSON-action підхід (чомпілкс, false matches)
  - Видалено apply_backlog_changes, commit_backlog, прапор --no-backlog
  - BACKLOG редагується руками через nano після спостережень
  - Використовує Haiku → Sonnet fallback для HOT/WARM оновлень
  - Інтерактивний y/n/e/s для ухвалення AI-пропозицій щодо HOT/WARM
  - Per-project commits у meta для не-meta проектів
  - max_tokens=2000 для повних відповідей
  - **Next:** перевірити на не-meta проекті, видалити legacy скрипти (kit/chkp.sh, kit/chkp2.sh)
- **BACKLOG** — центральна дошка завдань для всього workspace (read-only для chkp)
- **workspace/.env** — ключі на рівні workspace, fallback для 9 проектів
- **6 основних проектів** — кожен має HOT.md, WARM.md, COLD.md (локальні для архітектури)
- **Legacy скрипти** — видалення зафіксовано:
  - kit/chkp.sh (v1 reference) — на видалення
  - kit/chkp2.sh (тест v2) — на видалення
  - meta/chkp.sh (копія v1) — перенесено в meta/legacy/chkp_bash_v1/, на видалення
  - meta/chkp.py.bak (backup v3.0, 15K, 23.04) — залишено для git історії, може видалитися пізніше

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
6. **PATH binary для chkp** — замість bash v1 скрипту в /bin або /usr/bin, v3.4 через Python shim у ~/.local/bin. Уникає версійних конфліктів. Рішення вступило в силу 2026-05-03.

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
last_touched: 2026-05-03
tags: [open-questions]
status: active
```

- Чи commit_backlog коректно працює для не-meta проектів (окремий коміт у meta)?
- Чи AI-спостереження про BACKLOG будуть корисні при тестуванні чи буде шумом?
- Чи додати параметр `--quiet` щоб пропустити update_backlog при спіху?
- Як часто запускати `chkp` для backlog analysis? Чи варто в systemd timer?
- Чи генерувати AI-пропозицію для кількох проектів за раз (batch mode)?
- Список конкретних .env дублікатів на видалення — які проекти мають локальні копії?
- ROADMAP/IDEAS — при якому стані тестування почати заповнювати?
- Чи потреба синхронізувати інші файли на рівні meta (config, templates)?
- Чи збережувати meta/chkp.sh для документації чи видалити як legacy?

## Workspace structure: post-cleanup polyrepo (2026-04-29)

```yaml
last_touched: 2026-04-29
tags: [architecture, structure, git]
status: active
```

Після security cleanup 29.04 структура workspace:

- **Root `~/.openclaw/workspace/`** — НЕ git репо. Тільки символьні посилання `BACKLOG.md` → `meta/BACKLOG.md`, `CLAUDE.md` → `meta/agent-docs/CLAUDE.md`.
- **9 окремих GitHub repos** (один per бот): abby-v2, ed, garcia, household_agent_v1, insilver-v3, openclaw-kit, sam, workspace-meta. Insilver-v2 видалено з GitHub (legacy).
- **meta-репо** — централізована інфраструктура: `agent-docs/` (12 root-level md), `BACKLOG.md`, `chkp/` (Python v3.4), `legacy/chkp_bash_v1/` (чkp.sh v1, reference), `backup/` (тільки скрипти, runtime archives живуть у workspace/backup/), `systemd-services-backup/`.
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

## chkp v3.4 — PATH binary shim + backlog read-only assistant (2026-05-03)

```yaml
last_touched: 2026-05-03
tags: [chkp, backlog, integration, automation, infrastructure]
status: active
```

**Інфра-фікс: перехід на PATH binary (замість bash v1 скрипту):**

- **Проблема:** `/home/sashok/.local/bin/chkp` раніше був bash v1 скрипт (дельта з 2010.04). PuTTY викликав `chkp` через alias (v3.4), але `bash -c chkp` (CC, subshell, cron) потрапляв у `/usr/bin/chkp` або `/bin/chkp` (системні legacy шляхи) та виконував v1. Результат: SESSION.md замість HOT/WARM/COLD, розбіжність версій.
- **Рішення:** `/home/sashok/.local/bin/chkp` переписано на Python shim:
  ```python
  #!/usr/bin/env python3
  import subprocess, sys
  subprocess.run(["python3", "<path>/chkp.py"] + sys.argv[1:])
  ```
- **Результат:** Все — PuTTY, CC, subshell, cron, systemd — йдуть на одну версію (v3.4 через PATH, ~/.local/bin має приоритет).
- **Верифікація:** `bash -c chkp --help` показує v3.4 з --backlog-strike, --backlog-add, --sonnet.
- **Сайд-ефект:** Знайдено SESSION.md у meta repo (артефакт старого v1 запуску). Потреба cleanup + .gitignore.

**Видалити legacy скрипти:**
- `workspace/kit/chkp.sh` (v1 reference) — NEXT
- `workspace/kit/chkp2.sh` (тест v2) — NEXT
- `workspace/meta/chkp.sh` (копія v1, перенесено в legacy/) — NEXT
- `workspace/meta/chkp.py.bak` (backup v3.0) — залишено поки
- `workspace/meta/SESSION.md` (артефакт v1) — видалено, додано в .gitignore

**Backlog read-only assistant (стан з 2026-05-03):**

- **Спрощення** — update_backlog() генерує текстові спостереження про BACKLOG (без механічного редагування).
- **Видалено JSON-action підхід** — чомпліпкс, false matches на форматуванні.
- **Контроль у користувача** — BACKLOG редагується руками через nano після прочитання AI-спостережень.
- **Backward compatibility** — HOT/WARM оновлюються нормально, інтерактивний y/n/e/s flow зберігається.

**Next:** Протестувати PATH binary на реальному (не-meta) проекті, видалити legacy скрипти, синхронізувати .gitignore.

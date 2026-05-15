---
project: meta
created: 2026-04-23
---

# COLD — meta

Архів завершених фаз, міграцій, рефакторингів. Append-only: нові записи додаються вниз з датою.

---

## 2026-04-23 — Ініціалізація триярусної пам'яті

Проект переведено на структуру HOT/WARM/COLD/MEMORY. Створено через `chkp --init meta`. Rule Zero прийнято. Попередній стан виведено з userMemories Claude + поточної структури проекту.

---

## 2026-04-29 — Workspace security + structure cleanup (повна доба)

Розпочато з аудиту усіх git-репо в workspace. Знайдено: PAT в abby/.git/config, hardcoded TG tokens в історії insilver-v3 (3 шт) і insilver-v2 (4 шт), broken `.gitignore` в garcia (literal `\n`), затрекані PII файли в abby-v2/insilver-v3/sam (фото клієнта 189793675_*.jpg в insilver-v3 — privacy violation), 28k+ venv blobs в історії sam, root workspace помилково пушив у sam.git remote.

**8 фаз cleanup:**
1. abby PAT revoke + папка видалена (1.1G).
2. abby-v2 filter-repo: 13 PII, .git 12M→1.2M.
3. insilver-v3 filter-repo з --replace-text для 3 revoked TG токенів + invert-paths для 4 PII; dev гілка видалена. .git 342M→17M.
3b. insilver-v2 — GitHub repo видалено повністю (архівний бот, не варто filter-repo).
4. garcia: переписано broken `.gitignore`, filter-repo 6 PII + 4175 venv + 2008 pyc. .git 31M→1.3M.
5. sam filter-repo: 8 PII + 28k venv + 12k pyc + усі історичні .bak/_legacy/_deprecated; master і curriculum-v2 стейл-гілки з GitHub видалені. .git 72M→3.9M.
6. Root workspace → meta: 24 файли перенесено в meta (BACKLOG, agent-docs/, backup/, chkp.sh, systemd-services-backup/), BACKLOG.md і CLAUDE.md → symlinks; root .git видалено.
7. meta: створено .gitignore, дублікат `notes/BACKLOG.md` → `BACKLOG-archive-2026-04-29.md`.
8. Верифікація: 5 prod services + backup timer active, sub-repos чисті.

**Економія:** ~415M (лише по торкнутих репо). **Revoke'd:** 1 PAT + 5 TG bot tokens. **Force pushes:** 4 (abby-v2, insilver-v3, garcia, sam). **Бекап:** `~/workspace-backup-20260429-1944.tar.gz` (6.7G, перед стартом).

**Ключові уроки** (записано в WARM):
- `git filter-repo` чистить тільки локальні checkout'нуті refs — стейл-гілки на GitHub треба видаляти окремо.
- filter-repo робить implicit `git reset --hard` після переписування — working tree edit'и .gitignore зникають, треба commit'ити після filter-repo.
- Hardcoded TG bot tokens у logger output (insilver-v2 bot.log, 17590 матчів) — лог-файли НЕ повинні бути в git, навіть для архівних ботів.
- При filter-repo з `--replace-text` подбати про revoke токенів *перед* переписуванням, бо вони все ще валідні в кешах і клонах.

---

## 2026-04-30 — Remote dev infrastructure bootstrap

```yaml
archived_at: 2026-04-30
reason: завершено, переведено в WARM як active блок
tags: [infrastructure, remote-dev]
```

налаштовано tmux + Tailscale + Termius для роботи з Pi5 у дорозі з Android телефона. Структура: Tailscale VPN туннель (Pi5 ↔ телефон), Termius SSH клієнт з авто-reconnect, tmux на Pi5 для переживання обривів. Alias `w` = `tmux new -A -s work`. Базові команди засвоєні. Обмеження: tmux теряється при reboot Pi5 (сесії в RAM) — потреба скрипту для restore на startu. Next: розділити per-проект сесії (abby, garcia, sam, etc) для паралельного моніторингу, написати `tmux-restore.sh`.

---

## 2026-05-03 — chkp v3.2 JSON-action refactor (видалено)

```yaml
archived_at: 2026-05-03
reason: замінено v3.3 read-only assistant, чомпілкс не виправдав себе
tags: [chkp, backlog, automation]
```

v3.2 вводив JSON-action підхід: update_backlog() просив AI генерувати JSON з "strike": [рядки на видалення], "add": [нові рядки], "summary": опис. chkp застосовував дії механічно через str.replace. Мета: більше контролю, менше ризику. Реальність: AI часто вигадував рядки для видалення, false matches на пробілах/форматуванні, сніжний ком складності. max_tokens=2000, commit логіка, батарея open questions. Замінено v3.3 де update_backlog() просто видає текстові спостереження. BACKLOG редагується руками. Простіше, надійніше.

---

## 2026-05-03 — chkp v3.4 PATH binary migration

```yaml
archi6ved_at: 2026-05-03
reason: завершено, PATH binary заміна активна
tags: [chkp, infrastructure, binaries]
```

Перехід з bash v1 скрипту на Python shim у `/home/sashok/.local/bin/chkp`. Проблема: PuTTY викликав v3.4 через alias, але CC/subshell/cron потрапляли у системні шляхи (/usr/bin, /bin) з legacy v1, писали SESSION.md замість HOT/WARM/COLD. Рішення: /home/sashok/.local/bin/chkp переписано на Python shim що викликає chkp.py v3.4 з аргументами. Верифікація: `bash -c chkp --help` показує v3.4. Сайд-ефект: SESSION.md у meta repo. Потреба cleanup (видалити legacy chkp.sh у kit, meta; чkp2.sh; chkp.py.bak; SESSION.md; додати SESSION.md в .gitignore). Next: перевірити інші версійні конфлікти у workspace, синхронізувати .gitignore у всіх проектах.

---

## 2026-05-03 — chkp v3.4 PATH binary shim — стабілізація на meta

```yaml
archiued_at: 2026-05-03
reason: завершено інфра-фікс, переведено в WARM як active, готово до перевірки на не-meta
tags: [chkp, infrastructure, binaries, stabilization]
```

Перехід з bash v1 скрипту (дельта з 2010) на Python shim у `/home/sashok/.local/bin/chkp`. Проблема: PuTTY викликав v3.4 через alias, але CC/subshell/cron потрапляли у системні шляхи (/usr/bin, /bin) з legacy v1, писали SESSION.md замість HOT/WARM/COLD. Рішення: перереквест /home/sashok/.local/bin/chkp на Python shim що викликає chkp.py v3.4 з аргументами. Результат: усе — PuTTY, CC, subshell, cron, systemd — йдуть на одну версію. Верифікація: `bash -c chkp --help` показує v3.4. Сайд-ефект: SESSION.md у meta repo видалено, додане в .gitignore. Legacy скрипти (kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh) перенесені в meta/legacy/chkp_bash_v1/. chkp.py.bak залишено для git історії. NEXT: перевірити на не-meta проектах, видалити legacy за підтвердженням.

---

## 2026-05-03 — Memory auto-fetch для публічних репо (гібридний режим)

```yaml
archived_at: 2026-05-03
reason: завершено, переведено в WARM як active, готово до документації
tags: [memory, infrastructure, web-integration]
```

Активовано memory rule #21 для публічних репо (sam, ed, workspace-meta): HOT.md читаються через `web_fetch` на raw.githubusercontent.com без auth. Приватні репо (insilver-v3, abby-v2, garcia, household_agent) залишаються на ручному `cat HOT.md WARM.md` як інструкція. kit поки не мігрований, потребує окремої розгляду. Верифікація: усі три публічні репо дозволяють read. Гібридний режим: баланс між automation (публічні) і безпекою (приватні). Next: документувати у notes/, розглянути kit міграцію.

---

## 2026-05-03 — insilver-v3-dev pre-push patterns + дрібниці цикл

```yaml
archived_at: 2026-05-03
reason: завершено, переведено в WARM як active
tags: [insilver, git, pre-push, security, chkp-cycle]
```

Завершено 5 з 5 дрібниць цикла за ~1 год. **insilver-v3-dev pre-push patterns:** видалено blanket .jpg/.jpeg/.png бан, замінено на специфічні шляхи (data/photos/incoming/, data/photos/clients/) + Telegram client-ID формат [0-9]{9,}_.*. data/photos/static/ явно дозволено. Причина: 2026-04-29 security cleanup вилучив 8 PII фото, тепер hook запобігає рецидиву. **CLAUDE.md дрібнота:** уточнення правил, commit 99330fa. **insilver pre-commit hook:** перевірено, працює (раніше переписаний, беклог-пункт застарів). **PROMPT.md flow** (попередня сесія): write_prompt_md() перед git add -A, потрапляє до чекпоінту. **xclip guard** (попередня сесія): os.environ.get('DISPLAY') check + stderr=DEVNULL для SSH без X11. Разом 60 хв інкрементальних фіксів. Готово до P2: Sam NBLM Інтервенція 1 (dangling UUID), restart sam.service.

---

## 2026-05-03 — chkp guard рефакторинг: cross-project workflow

```yaml
archiued_at: 2026-05-03
reason: завершено, переведено в WARM як active, перевірено на meta
tags: [chkp, cross-project, guard, workflow]
```

Оптимізація warn-логіки в `meta/chkp/chkp.py`. Проблема: warn про dev-каталог спрацьовував на будь-який cwd закінчуючись на -dev (e.g., cd insilver-v3-dev && chkp meta), що創造ло false positives у 90% випадків при крос-проектній роботі. Рішення: warn тільки коли cwd basename == project + '-dev' (тобто у dev-каталозі ТОГО Ж проекту що чекпоінтиш). Перевірка: `if cwd_basename == f"{project}-dev": warn(...)`. Результат: cross-project workflow (cd insilver-v3-dev && chkp meta) тепер мовчазний, як очікується при Model A потоці; локальна (cd meta-dev && chkp meta) продовжує перепитувати. Рішення мінімізує шум при паралельній роботі з кількома проектами на Pi5. Тестовано на meta, потреба перевірки на не-meta проектах.

---

## 2026-05-03 — chkp v3.4 PATH binary migration + guard рефакторинг + дрібниці цикл

```yaml
archived_at: 2026-05-03
reason: завершено, переведено в WARM як active, готово до P2
tags: [chkp, infrastructure, binaries, stabilization, cross-project, security]
```

Повна стабілізація чkp v3.4 + Path binary шим + дрібниці цикл за ~4 год. **PATH binary migration:** Перехід з bash v1 скрипту (дельта з 2010) на Python shim у `/home/sashok/.local/bin/chkp`. Проблема: PuTTY викликав v3.4 через alias, але CC/subshell/cron потрапляли у системні шляхи з legacy v1, писали SESSION.md замість HOT/WARM/COLD. Рішення: shim викликає chkp.py v3.4. Верифікація: `bash -c chkp --help` показує v3.4. SESSION.md видалено, .gitignore оновлено. **Guard рефакторинг:** Warn про dev-каталог тільки коли cwd == args.project + '-dev'. Cross-project (cd insilver-v3-dev && chkp meta) — мовчазний, це штатний workflow. Раніше false positives у 90%. Перевірка: `cwd_basename == f"{project}-dev"` перед warn. **Дрібниці цикл:** insilver-v3-dev pre-push patterns (видалено blanket .jpg, додано специфічні шляхи + TG client-ID regex), CLAUDE.md, PROMPT.md flow (перед git add), xclip guard (DISPLAY check + stderr=DEVNULL). Разом 60 хв. **Legacy скрипти status:** kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh перенесені в meta/legacy/chkp_bash_v1/. chkp.py.bak залишено. SESSION.md видалено. Потреба фінального видалення коли v3.4 протестується на не-meta проектах (garcia, abby-v2, ed).

---

## 2026-05-04 — BACKLOG cleanup: NBLM-05-02 видалено + Sam реорганізовано

```yaml
archiued_at: 2026-05-04
reason: завершено, переведено до WARM як активна послідовність
tags: [backlog, cleanup, sam-nblm, organization]
```

Видалено superseded NBLM-05-02 секцію з BACKLOG (28 рядків, застарі фаза). Реорганізовано Sam NBLM tech debt як послідовність 5 Інтервенцій з явною нумерацією і залежностями. Статус переклавифікований: DONE (пункти 1-3 закриті в chkp cycles + security cleanup), TODO (пункти 4-7 активні на черзі). Залежності актуалізовані: Inter 1 (dangling UUID) розблокує rag_retrieval-1. Запис у WARM під Sam NBLM блок. Беклог тепер компактніший і фокусований. Послідовність готова до P2 після abby-v1 видалення та швидких чекпоінтів (max_tokens, xclip validation).

---

## 2026-05-04 — BACKLOG cleanup #2: max_tokens + xclip + abby-v1 verifikacija

```yaml
archiued_at: 2026-05-04
reason: завершено, переведено до HOT/WARM як актуальні результати
tags: [backlog, cleanup, chkp-verification, p2]
```

Викопано пункти 3-5 з беклогу (список 1-16). **Пункт 3 (chkp3 max_tokens):** Верифіковано що max_tokens=2000 актуальний в chkp.py, достатній для повних HOT/WARM відповідей. Потреба підвищення до 4096 не визначена, залишено як есть. **Пункт 5 (chkp xclip validation):** Commit e1f5439 додав xclip guard — DISPLAY check перед викликом + stderr=DEVNULL (commit e1f5439: "silence xclip stdout error noise"). На SSH без X11 (Pi5 headless) мовчазно повертає False без noise. Протестовано на Pi5 (headless), працює. **Пункт (abby-v1 repo):** Верифіковано що abby-v1 локально не потребуємо (код давно архівний, супорт припинений), GitHub repo готовий до видалення у Settings → Danger Zone. Лишилось 11 пунктів. Беклог оптимізований для P2. Послідовність: abby-v1 видалення → PATH binary перевірка на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → вибір пункту 8 або 11 → Sam NBLM Інтервенція 1 (dangling UUID restart).

---

## 2026-05-04: Backlog cleanup #2 — Sprint A completion (max_tokens + xclip + abby-v1 verification)

```yaml
archived_at: 2026-05-04
reason: завершено, переведено до HOT/WARM як актуальні результати
tags: [backlog, cleanup, chkp-verification, sprint-a, p2]
```

Викопано пункти 3-5 з беклогу (список 1-16). **Пункт 3 (chkp3 max_tokens):** Верифіковано що max_tokens=2000 актуальний в chkp.py, достатній для повних HOT/WARM відповідей. Потреба підвищення до 4096 не визначена, залишено як есть. **Пункт 5 (chkp xclip validation):** Commit e1f5439 додав xclip guard — DISPLAY check перед викликом + stderr=DEVNULL. На SSH без X11 (Pi5 headless) мовчазно повертає False без noise. Протестовано на Pi5 (headless), працює. **Пункт (abby-v1 repo):** Верифіковано що abby-v1 локально не потребуємо (код давно архівний), GitHub repo готовий до видалення у Settings → Danger Zone. **Статус беклогу:** Лишилось 11 пунктів. Беклог оптимізований для P2. Sprint A завершено за один SSH-крок. Послідовність: abby-v1 видалення → PATH binary перевірка на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → Sam NBLM Інтервенція 1 (dangling UUID restart).

---

## 2026-05-04: BACKLOG реорганізація — Sam NBLM як послідовність Інтервенцій

```yaml
archived_at: 2026-05-04
reason: завершено, переведено до WARM як активна послідовність
tags: [backlog, cleanup, sam-nblm, organization, sprint-a]
```

Видалено superseded NBLM-05-02 секцію з BACKLOG (28 рядків, застарі фаза). Реорганізовано Sam NBLM tech debt як послідовність 5 Інтервенцій з явною нумерацією і залежностями. Класифіковано: DONE (пункти 1-3 закриті в chkp cycles + security cleanup), TODO (пункти 4-7 активні на черзі). Залежності актуалізовані: Inter 1 (dangling UUID) розблокує rag_retrieval-1. Запис у WARM під Sam NBLM блок. Беклог тепер компактніший і фокусований на P2. Послідовність готова до стартування після abby-v1 видалення та PATH binary верифікації.

---

## 2026-05-04: BACKLOG cleanup tail — 5-й strike verification (max_tokens + xclip + abby-v1)

```yaml
archived_at: 2026-05-04
reason: завершено, переведено до HOT/WARM як актуальні результати + уроки
tags: [backlog, cleanup, chkp-verification, sprint-a, p2, backlog-strike]
```

Викопано пункти 3-5 з беклогу BACKLOG (список 1-16). **Пункт 3 (chkp3 max_tokens):** Верифіковано що max_tokens=2000 актуальний в chkp.py, достатній для повних HOT/WARM відповідей. Потреба підвищення до 4096 не визначена, залишено як есть. **Пункт 5 (chkp xclip validation):** Commit e1f5439 додав xclip guard — DISPLAY check перед викликом + stderr=DEVNULL. На SSH без X11 (Pi5 headless) мовчазно повертає False без noise. Протестовано на Pi5 (headless), працює. **Пункт (abby-v1 repo):** Верифіковано що abby-v1 локально не потребуємо (код давно архівний, супорт припинений), GitHub repo готовий до видалення у Settings → Danger Zone. **Уроки з беклог-стройку:** --backlog-strike FRAGMENT повинен бути дослівним підрядком рядка BACKLOG. При неточному match chkp не знаходить рядок. **Статус беклогу:** Лишилось 11 пунктів. Беклог оптимізований для P2. Sprint A завершено за один SSH-крок. Послідовність: abby-v1 видалення → PATH binary перевірка на не-meta (garcia, abby-v2, ed) → legacy скрипти видалення → Sam NBLM Інтервенція 1 (dangling UUID restart).

---

## 2026-05-04: Prompt caching baseline smoke test 1 — infrastructure setup

```yaml
archiued_at: 2026-05-04
reason: завершено baseline test, переведено в WARM як active infrastructure block
tags: [infrastructure, prompt-caching, api, optimization, sprint-b]
```

Поставлено baseline smoke test для prompt caching на claude.ai. Інструкція додана у claude.yaml (Claude API config на claude.ai): див. MEMORY.md rule #42. Ціль: перевірити що cache_creation_input_tokens > 0 на першому виклику означає успішну кешізацію. На другому та наступних — cache_read_input_tokens повинен показати переиспользование. **Метрика:** якщо cache_creation_input_tokens = 0 (не кешується) — потреба debug. Очікується успіх на claude.ai публічній (beta feature). Протестовано на meta проекті, результати документуються у notes/PROMPT-CACHING.md. Next: auto-cache refresh через `chkp` системи (якщо помінявся HOT/WARM), розглянути per-project cache strategies.

---

## 2026-05-04: abby-v1 GitHub repository deletion

```yaml
archived_at: 2026-05-04
reason: GitHub repo deleted via Settings → Danger Zone, local backup verified
tags: [cleanup, abby, github, sprint-a]
```

Delete completed на GitHub (Settings → Danger Zone, ввід `sandalya/abby-v1`, confirm). Локальна папка ~/openclaw/workspace/abby-v1 перевірена на бекап, готова до видалення вручну при наступному численні. Рамка: код давно архівний, супорт припинений 2026-03-15. GitHub repo був 0B (empty), лише historici metadata. Беклог пункт 3 DONE. Уроки: GitHub deletion передує локальній папці — менше шансів на accidental push з legacy. Next: локальна папка на видалення, PATH binary верифікація на не-meta проектах.

---

## 2026-05-04: Prompt caching baseline infrastructure — smoke test 1 setup

```yaml
archived_at: 2026-05-04
reason: завершено baseline setup, переведено в WARM як active infrastructure
tags: [infrastructure, prompt-caching, api, optimization, sprint-b]
```

Setup завершено для smoke test 1. Інструкція додана у claude.yaml (Claude API config на claude.ai, MEMORY.md rule #42). Метрика: cache_creation_input_tokens > 0 на першому виклику означає успішну кешізацію. На другому та наступних — cache_read_input_tokens повинен показати переиспользование кешованого контенту. Документація шаблон у notes/PROMPT-CACHING.md (на заповнення після першого claude.ai запиту). **Очікування:** Перша claude.ai сесія з prompt caching instructions на наступну роботу по іншим проектам (sam, garcia, etc) → перевірити response_metadata → записати результати → розглянути auto-cache refresh через chkp системи для Sprint B/C. Next: першого claude.ai запиту з инструкцією → документація → розглянути per-project cache strategies.

---

## 2026-05-05: Prompt caching investigation closed — smoke test 1+2 unpractical

```yaml
archiued_at: 2026-05-05
reason: P2 closed, architecture volatihlity makes caching ROI zero in current setup
tags: [infrastructure, prompt-caching, api, optimization, investigation]
```

Baseline smoke test 1+2 completed. Results: cache_creation_input_tokens=14,547 first call, cache_read_input_tokens=0 second call. Root cause: Haiku в update_backlog() перезаписує WARM щоразу → контент змінюється між викликами → cache miss. Мінімальна cacheable одиниця claude.ai — 1024 tokens. SYSTEM (577) + MEMORY (393) = 970 < 1024. HOT (1031) на межі. COLD (6114) append-only, потенційно cacheable, але WARM динаміка усереджує весь стек. CC реалізував cache_control PR (статусний кеш для WARM diff), але stash повернув — не потребується. Висновок: ROI нема без архітектурної переробки (WARM diff-mode, COLD frozen split, output streaming). Рішення: закрити як P2, прийняти chkp 30-90s як норму. Beta header `prompt-caching-2024-07-31` залишено у claude.yaml для майбутніх експериментів. BACKLOG +1 P3 пункт для переглядання caching підходів після архітектурної стабілізації (Sprint B/C).

---

## 2026-05-05: Sam external_stop zombie pending — scheduled for morning

```yaml
archiued_at: 2026-05-05
reason: pending fix, CC informed, scheduled for tomrrow morning
tags: [sam, p3, zombie, pending]
```

Sam external_stop call має мертвий zombie process. CC інформував про issue. Запуск на завтра ранок: `systemctl restart sam.service`, перевірка логів. Потім вибір Sprint C (voice extraction Влада, ~2h) або Sprint D (Sam evals + agentic ingest, ~3h, потребує свіжого мозку). Енергія циклу закривається, 4 спринти + caching investigation + 3 P3 cleanup завершено за 04-05.05.

## 2026-05-05: WARM diff-mode v3.5 інтеграція — Sprint A завершено

```yaml
archived_at: 2026-05-05
reason: live у продакшені, переведено в WARM як active
tags: [infrastructure, warm-ops, optimization, sprint-a, p1]
```

WARM diff-mode через warm_ops парсер запущено в продакшені. Замість переписування всього WARM (16k tokens), chkp v3.5 генерує компактний JSON з операціями (warm_ops). Результат: **economia 79% (16k→3.4k tokens), прискорення 5хв→15с на чекпоінті.** Архітектура: `meta/chkp/warm_ops.py` парсер + серіалізатор для 5 операцій (touch, update_field, add, move_to_cold, replace_body). Backward-compat з legacy WARM (без field = default status=active). Unit-тестування: 16/16 passed. Перший прод-чекпоінт (insilver-v3, commit 4580c35): JSON malformed на першому запуску, автоматичний retry OK — P3 потреба explicit retry-loop. garcia, abby-v2, ed, sam готові до масштабування (локальні dry-run перевірені). **Prompt caching P2 закрито:** Smoke test 1+2 показали що WARM diff-mode (+79% token save) НЕ вирішує caching (мінімум 1024 tokens для claude.ai блоку). Beta header залишено для COLD frozen split експериментів у Sprint B/C.

---

## 2026-05-05: Prompt caching дослідження закрито — WARM diff-mode не рятує

```yaml
archiued_at: 2026-05-05
reason: P2 задача закрита, WARM diff-mode готовий до інших потреб
tags: [infrastructure, prompt-caching, api, optimization, investigation, sprint-a]
```

Prompt caching як рішення для chkp закрито на P2. Дослідження показало що WARM diff-mode (+79% token economy через warm_ops) НЕ вирішує основну проблему: мінімум cacheable блоку в claude.ai = 1024 tokens. SYSTEM (577) + MEMORY (393) + warm_ops (~200) = ~1170, на межі. COLD (6114) append-only але grow щосеанс. WARM волатильна (Haiku сам перезаписує), cache miss неминучий. Базова логіка: cache_creation_input_tokens показується на першому виклику, cache_read_input_tokens на наступних — якщо нуль, cache miss. CC реалізував cache_control PR для WARM diff, але stash повернув (не потребується). Висновок: ROI нема без більших архітектурних змін (COLD frozen split для append-only historico, output streaming для HOT). Прийняти chkp 30-90s як норму. Beta header `prompt-caching-2024-07-31` залишено у claude.yaml для майбутніх експериментів. Next: розглянути COLD frozen split у Sprint B/C після WARM diff-mode стабілізації на всіх проектах.

## 2026-05-05: Prompt caching infrastructure (2026-05-05 — closed as P2 impractical)

```yaml
archived_at: 2026-05-05
reason: moved from WARM (status:closed-p2, stale)
tags: [infrastructure, prompt-caching, api, optimization, archived]
```

**Baseline smoke test 1+2 results (2026-05-05):** Setup завершено, тестування показало непрактичність caching для chkp у поточній архітектурі. **Результати:** cache_creation_input_tokens=14,547 на першому виклику, cache_read_input_tokens=0 на другому. **Причина:** Haiku у update_backlog() перезаписує WARM щоразу → контент змінюється між викликами → cache miss. **Мінімальні блоки:** SYSTEM (577 tokens) + MEMORY (393 tokens) = 970 < 1024 (мінімум claude.ai). HOT (1031) на межі. COLD (6114) append-only, потенційно cacheable, але WARM волатильність усереджує весь стек. **CC реалізація:** CC запропонував cache_control PR (статусний кеш для WARM diff), але stash повернув — не потребується у поточному стані. **Висновок:** ROI нема без архітектурної переробки (WARM diff-mode, COLD frozen split, output streaming). **Рішення:** Закрити як P2 задачу. Прийняти chkp 30-90s як нормальну затримку. Beta header `prompt-caching-2024-07-31` залишено у claude.yaml для майбутніх експериментів. **BACKLOG +1 P3:** Додано пункт для переглядання caching підходів після архітектурної стабілізації (можливо Sprint C/D).

---

## 2026-05-05: WARM diff-mode v3.5 — live production checkpoint (Sprint A complete)

```yaml
archived_at: 2026-05-05
reason: live в продакшені, переведено до WARM як active, масштабування заплановано
tags: [infrastructure, warm-ops, optimization, sprint-a, p1]
```

WARM diff-mode v3.5 запущено в живу на insilver-v3 (commit 4580c35). Парсер + серіалізатор 5 операцій (touch/update_field/add/move_to_cold/replace_body) повністю протестовані: 16/16 unit-тестів, backward-compat з legacy WARM без field. Перший прод-чекпоінт: **economia 79% (16k→3.4k tokens), чекпоінт за 15 сек замість 5 хвилин.** JSON malformed на першому запуску автоматично retry OK — кандидат P3 (explicit retry-loop удосконалення). garcia, abby-v2, ed, sam локально dry-run OK, готові до масштабування. **Sprint A (2026-04-29 ... 2026-05-05) завершено:** security cleanup (415M дисків), workspace polyrepo (8 окремих репо), PATH binary migration (chkp v3.4 shim), WARM diff-mode інфраструктура і перший прод-чекпоінт. Prompt caching P2 закрито (smoke test показав мінімум 1024 tokens для cacheable блоку недопустимий у поточній архітектурі SYSTEM+MEMORY). Наступна фаза (2026-05-05 вечір / 2026-05-06): масштабування на 4 проекти + P3 cleanup (JSON retry, опціонально Sam zombie fix).

---

## 2026-05-05: Prompt caching дослідження закрито — P2 як impractical у поточній архітектурі

```yaml
archiued_at: 2026-05-05
reason: moved from WARM (status:closed-p2), smoke test 1+2 unpractical
tags: [infrastructure, prompt-caching, api, optimization, investigation, sprint-a]
```

Smoke test 1+2 (2026-05-04/05) завершено. **Результати:** cache_creation_input_tokens=14,547 на першому claude.ai виклику (WARM update), cache_read_input_tokens=0 на другому (cache miss). **Причина:** Haiku у update_backlog() перезаписує WARM щоразу → контент змінюється між викликами → claude.ai не кешує. **Мінімальні блоки:** SYSTEM (577) + MEMORY (393) = 970 < 1024 мінімум. HOT (1031) на межі. COLD (6114) append-only, потенційно cacheable, але WARM волатильність усереджує весь стек. **CC реалізація:** CC запропонував cache_control PR (stateful cache для WARM diff), але stash повернув — не потребується. **Висновок:** ROI zero без архітектурної переробки (WARM diff-mode done, але потреба COLD frozen split для append-only historico, output streaming для HOT). **Рішення:** Закрити як P2 задачу, прийняти chkp 30-90s як нормальну затримку. Beta header `prompt-caching-2024-07-31` залишено у claude.yaml для Sprint B/C експериментів. **BACKLOG:** Додано +1 P3 пункт про майбутні caching підходи після архітектурної стабілізації (можливо Sprint C/D).

---

## 2026-05-05: chkp SYSTEM_PROMPT patch — двошарова no-hallucination механіка

```yaml
archiued_at: 2026-05-05
reason: live у продакшені, переведено в WARM як active patch
tags: [chkp, system-prompt, evals, p1, patch]
```

чекпоінт v3.5 генерує HOT.md, але ## Now галюцинує (copy-paste з попередньої HOT або WARM замість WHAT WAS DONE THIS SESSION). Рішення: двошарова механіка. **Шар 1 — SYSTEM_PROMPT rule:** explicit canonical sources per section. ## Now ONLY від input, CRITICAL. WARM = histórico, не джерело. **Шар 2 — _redact_now_for_context():** видаляє ## Now і ## Last done з input HOT перед API-call, mechanical enforcement. **Валідація:** 19/19 pytest PASS (3 no_hallucination fixtures + 16 warm_ops). Локальна верифікація OK. Перша prod верифікація на інших проектах заплановано 2026-05-06+. Якщо тримається → scalability на 6 проектів. Patch готовий до production deploy після спостереження реальних чекпоінтів.

---

## 2026-05-06: Off-device backup chain — DR infrastructure setup

```yaml
archived_at: 2026-05-06
reason: completed, moved to WARM as active infrastructure
tags: [infrastructure, backup, disaster-recovery, automation]
```

Set up comprehensive off-device backup strategy: PC (Windows 10, H:\pi_backups) pulls daily via Task Scheduler with 14-day retention, SSH key auth (~/.ssh/pi5_backup), MinHoursBetweenRuns=20 (throttle). Pi5 local retention reduced from 7 to 3 days on 2026-05-06. Notifications: Telegram on error only (removed daily-notify noise, kept weekly summary Sundays 03:00). Verification: 7 archives synced, md5 match, Task Scheduler launch at logon+2min, SD card space freed 78%→70%. Created backup/ git repo (sandalya/pi5-backup) with backup.sh, notify.sh, README.md, exclude.txt, .gitignore, .env.example pushed to GitHub. DR drill scheduled for spare SD arrival. Next: extend backup.sh to capture /etc/systemd/system, ~/.claude/settings.json, crontab, dpkg list for faster rebuilds.

---

## 2026-05-06: SD card cleanup + venv rebuild + Telegram token rotation

```yaml
archived_at: 2026-05-06
reason: completed, monitoring for logging security compliance
tags: [maintenance, disk-space, security, telegram, logging]
```

SD card optimization and security incident remediation. Freed 11GB on Pi5 (/: 78%→60%) via pip cache cleanup (3G), npm cache (1.8G), unused .u2net models (1.1G), and meggi venv rebuild 3.0G→497M (CPU-only PyTorch without nvidia/triton). Verified faster-whisper still functions on CPU. .u2net consolidated to isnet-general-use.onnx (171M, used by abby-v2 rembg). requirements.txt added to household_agent/ for reproducibility.

Security incident: Telegram bot token (household_agent-v1) leaked into journalctl via httpx library INFO logging (token in URL parameters). Token rotated via BotFather. Root cause: httpx default logging level logs full request URLs. Action: suppress httpx INFO/DEBUG across all 6 bots (abby-v2, ed, garcia, household_agent, insilver-v3, sam) — add `logging.getLogger('httpx').setLevel(logging.WARNING)`. Audit historical journalctl for similar leaks. Document in MEMORY.md logging security rule.

Backup chain continues: PC pulls 14-day retention to H:\pi_backups, Pi local 3-day rotation, weekly Telegram summary Sundays 03:00. DR drill pending spare SD arrival. Backlog: abby images (759M, 1315 files) + sam audio (827M, 26 mp3 podcasts) rotation policy deferred to next session.

---

## 2026-05-06: Logging security — httpx token leak suppression (patching cycle)

```yaml
archiued_at: 2026-05-06
reason: incident remediation in progress, 2/6 bots patched, remaining 4 to audit
tags: [security, logging, httpx, telegram, incident]
```

Httpx library INFO-level logging exposes Telegram bot tokens in URLs. Incident: household_agent-v1 token leaked, rotated via BotFather 2026-05-06. Audit found 4 of 6 bots leak: abby-v2 (30k entries/7d), ed-bot (60k), household_agent (28k), insilver-v3 (TBD); garcia and sam clean (use shared/logger module). **Action completed this session:** patched abby-v2 main.py and ed/bot.py with `logging.getLogger('httpx').setLevel(logging.WARNING)`, rotated both bot tokens. Journalctl vacuumed: 834M→16M, 105k+ token leak entries removed. **Next session:** audit household_agent and insilver-v3 httpx usage, apply same suppression pattern, verify garcia/sam logger pattern adoption across ecosystem. All 6 bots must suppress httpx INFO before next checkpoint. Backlog +1 item: "Enforce httpx logging suppression in requirements.txt/docker configs"

---

## 2026-05-06: chkp.py backlog validation pre-flight check — validate_backlog_flags()

```yaml
archived_at: 2026-05-06
reason: live у продакшені, переведено в WARM як active компонент
tags: [chkp, validation, backlog, p1]
```

Implemented validate_backlog_flags() pre-flight check у chkp.py. Проблема: --backlog-strike та --backlog-add можуть мовчазно скипуватися, якщо користувач не копіює дослівно рядок з BACKLOG.md (вчора: commit 3e67fa5+00defa1 мав mismatched header). Рішення: перед Haiku call валідувати флаги через difflib.get_close_matches (top 3 результати, cutoff 0.4). Якщо не матчить — fail loud (exit 2) з fuzzy hints. _check_backlog_match() helper — single source of truth для strike/add validation, используется в apply_backlog_flags(). Результат: **26/26 pytest PASS (19 старих + 7 нових)**. Smoke test: вчорашня помилка (mismatched httpx strike) тепер ловиться з правильною hint про BACKLOG header. NO API token waste на невалідні флаги. Live у meta/chkp/chkp.py v3.5. Готово до масштабування на інші проекти при наступному checkpoint cycle.

---

## 2026-05-06: Strikethrough rule enforcement — dual-location fix для LLM reliability

```yaml
archiued_at: 2026-05-06
reason: completed, moved to WARM компонент Компоненти + Ключові рішення
tags: [backlog, instruction-clarity, llm-reliability, claude-instructions]
```

Посилено strikethrough правило у двох місцях для захисту від поновлення закреслених пунктів як активних. Проблема: за 2026-05-06 Claude двічі резюмував ~~struck~~ пункти як активні TODO. Гіпотеза про рендер (тильди не передаються) спростована — тильди доходять як токени. Реальна причина: header rule у середині 40K файлу (BACKLOG.md) мав слабкий сигнал, інструкція `summarize active items` знаходилась зовні контексту й перебивала локальне правило. **Рішення:** дублювати правило у двох місцях. (1) CLAUDE.md agent-docs, секція Backlog — детальний header rule про strikethrough з прикладами. (2) BACKLOG.md header — додано візуальний STOP блок з алгоритмом обробки та прикладами невалідних форматів. Також виправлено невірний шлях /workspace/BACKLOG.md → /workspace/meta/BACKLOG.md у посиланнях. CC-тест (claude.ai з claude.yaml правилом): summarize active items — закреслені пункти НЕ повернулись як активні, тест PASS. Спостереження: LLM требує дублювання правила на всіх рівнях системи (CLAUDE.md + BACKLOG.md + claude.yaml) для надійності у великих контекстах. Моніторинг 2-3 наступних сесій на рецидиви — якщо відбудеться, перейти на [CLOSED] markup замість ~~strikethrough~~.

---

## 2026-05-06: httpx logging security incident — token rotation + patch cycle

```yaml
archiued_at: 2026-05-06
reason: incident remediation in progress, monitored for compliance
tags: [security, logging, httpx, telegram, incident, bots]
```

Телеграм bot token (household_agent-v1) витік у journalctl через httpx INFO-level логування. Токен присутній у URL query parameters, залоговано перед виконанням запиту. Token rotated via BotFather на 2026-05-06, revoked. Root cause: httpx default logging level (INFO) включає full request URLs. Поширений по 6 проектам (abby-v2, ed, garcia, household_agent, insilver-v3, sam). **Action completed:** (1) patched abby-v2 main.py + ed/bot.py з `logging.getLogger('httpx').setLevel(logging.WARNING)`; (2) rotated обидва tokens; (3) vacuumed journalctl: 834M→16M, 105k+ leak entries removed. **Next session:** audit household_agent та insilver-v3 httpx usage, apply same suppression, verify garcia/sam logger pattern compliance. Backlog +1: enforce httpx suppression в requirements.txt/docker configs.

---

## 2026-05-06: chkp.py BACKLOG strike validation — replace(,1) bug + test expansion

```yaml
archiued_at: 2026-05-06
reason: identified bugs in BACKLOG parsing, added test cases for robustness
tags: [chkp, backlog, validation, testing, p2]
```

виявлено 3 класи bagів у `meta/chkp/chkp.py` apply_backlog_flags() під час аудиту П.1 manual fix сесії. (1) **Silent-skip bug:** коли --backlog-strike FRAGMENT не знайшовся у BACKLOG (user помилка у copy-paste), флаг мовчазно пропускається без error. Рішення: validate_backlog_flags() вже ловить через fuzzy hints, але потреба explicit test case. (2) **Multi-match bug:** коли FRAGMENT матчиться у BACKLOG 2+ рази (e.g., "TODO" в 10 пунктах), replace(FRAGMENT, 1) замінює ТІЛЬКИ перший матч, решта залишаються. Користувач очікує всі видалити. Рішення: потреба уточнення яку лінію видалити або multi-line pattern matching. (3) **Replace(,1) bug (виявлено цієї сесії):** Python str.replace(s, 1) означає "заміни ПЕРШИЙ матч", но коєсь багу заповняє FRAGMENT неправильно, повертає перше входження у файлі замість рядка в BACKLOG. Контекст: вчорашня П.1 apply видалила неправильно, manual fix потребував. Рішення: написати тест case з дублік FRAGMENT у BACKLOG, перевірити replace() поведінку. **Test expansion (2026-05-06):** Додано до BACKLOG пункт про розширення `meta/chkp/tests/` новими case'ами: (a) silent-skip (BACKLOG item без матча), (b) multi-match (FRAGMENT матчиться 2+ рази), (c) replace(,1) (баг з першим матчем), (d) ~~closed~~ strikethrough парсинг (закреслені пункти не повинні бути видалені). Unit-тести очікуються на наступну сесію. Live validation (validate_backlog_flags) вже захищає від простих помилок copy-paste; потреба більш роботимої стратегії для multi-line + duplicate FRAGMENT сценаріїв.

---

## 2026-05-06: chkp.py apply_backlog_flags() — bug audit + test expansion roadmap

```yaml
archiued_at: 2026-05-06
reason: identified bugs, added roadmap for test expansion in next sprint
tags: [chkp, backlog, validation, testing, p2]
```

Виявлено 3 класи багів у `meta/chkp/chkp.py` apply_backlog_flags() під час аудиту попередньої сесії. **(1) Silent-skip bug:** коли --backlog-strike FRAGMENT не знайшовся у BACKLOG (user помилка copy-paste), флаг мовчазно пропускається без error. Рішення: validate_backlog_flags() вже ловить через fuzzy hints, але потреба explicit test case. **(2) Multi-match bug:** FRAGMENT матчиться у BACKLOG 2+ рази (e.g., "TODO" в 10 пунктах), replace(FRAGMENT, 1) замінює ТІЛЬКИ перший матч, решта залишаються. Користувач очікує видалити вказаний пункт, не перший матч у файлі. Потреба уточнення яку лінію видалити або multi-line pattern matching. **(3) Replace(,1) точність:** str.replace(s, 1) означає "заміни ПЕРШИЙ матч", потреба более точної селекції по контексту (номер пункта, рядок) замість простого FRAGMENT. Вчорашня apply видалила неправильно, manual fix потребував.

**Test expansion (2026-05-06):** Додано до BACKLOG пункт про розширення `meta/chkp/tests/` новими case'ами: (a) silent-skip (BACKLOG item без матча), (b) multi-match (FRAGMENT матчиться 2+ рази), (c) replace(,1) (баг з першим матчем), (d) ~~closed~~ strikethrough парсинг (закреслені пункти не повинні бути видалені або summaryуватися як активні). Unit-тести очікуються на наступну сесію. Live validation (validate_backlog_flags) вже захищає від простих помилок copy-paste. Потреба більш роботимої стратегії для multi-line + duplicate FRAGMENT сценаріїв. Next: написати тести, потім підтримати replace() логіку для вибір вірного рядка за лінійним номером + контекстом.

---

## 2026-05-14: Anthropic SDK cost isolation — shared/agent_base.py fix

```yaml
archiued_at: 2026-05-14
reason: root cause found, fix deployed, monitoring cost isolation tomorrow
tags: [api-keys, costs, shared-library, anthropic-sdk, cost-tracking]
```

Виявлено витік витрат на kit3 ключі через shared/agent_base.py. Anthropic SDK's find_dotenv() автоматично підхоплював workspace/.env (з kit3 ключем) замість проектних .env для abby-v2, household_agent, ed-bot. Рішення: додано EnvironmentFile=<path>/.env в systemd-юніти для abby-v2.service та household_agent.service. ed-daily.timer поновлено (раніше зупинений, judge використовував Haiku). Перевірено sam-rss і insilver-v3-error-monitor — Anthropic SDK не кличуть. Верифікація завтра (2026-05-15): AWS Console (kit3 витрати мають обвалитись), abby-v2/household_agent ключи (мають показати власний трафік). Judge семантичні assertions — потреба мануальної регресії для порівняння pass rate 37/17/23. Cost tracking знову окремий по агентах.

---

## 2026-05-15: morning_digest systemd timer — Telegram BACKLOG summary automation

```yaml
archiued_at: 2026-05-15
reason: live у продакшені, переведено в WARM як active, завтра timer verification
tags: [telegram, automation, backlog-digest, sam-bot, incident-response]
```

Розгорнуто автоматичний щоденний digest BACKLOG структури через Telegram. **Компоненти:** meta/digest/morning_digest.py парсер (інлайн Pn маркери, closed sections, uncategorized items), Haiku 4.5 синтез (мова оригіналу, чиста відповідь), HTML parse_mode для Telegram, systemd timer 09:00 daily. **Конфіг:** meta/digest/.env (SAM_BOT_TOKEN, OWNER_CHAT_ID, ANTHROPIC_API_KEY реюз із sam). **Статус:** 11/11 unit-тестів PASS, cost ~0.0026 USD/run (~0.08/місяць), перший run OK (p1=0, p23=3, uncategorized=13, done=0). **Інцидент:** Sam-бота токен витік у claude.ai чаті через неправильну sed маску, ротовано через @BotFather 2026-05-15, sam.service рестартнуто. **Next:** перевірити 09:00 timer завтра, додати (Pn) маркери до решти uncategorized пунктів, розглянути frequency adjustment (щодня vs. раз на 2 дні).

---

## 2026-05-15: Batch 1 chkp.py robustness + httpx suppression + NBLM verification

```yaml
archiued_at: 2026-05-15
reason: tasks 1-7 completed, live validation pending
tags: [chkp, testing, logging-security, nblm, batch-1]
```

Batch 1 sprint завершено за одну сесію. **Task 1:** httpx INFO logging suppression added to household_agent/main.py (others already inherit via shared/logger.py). Token rotated via BotFather. **Tasks 2–5:** chkp.py robustness fixes: (1) multi-match replace bug — context-aware line selection by line number instead of replace(,1) first match; (2) replace edge case — strip whitespace from FRAGMENT before matching; (3) validation pre-flight check improvement — better error messages; (4) test expansion — 4 new test files (test_apply_backlog_multi_match.py, test_silent_skip.py, test_replace_edge_cases.py, test_strikethrough_parsing.py). Total 22 new tests added, 48/48 pass locally. **Task 6:** pre-push hook verification skipped (not found in insilver-v3-dev/.git/hooks/pre-push). **Task 7:** dangling NBLM UUID probe (sam/core/content_gen/backends/nblm.py get_or_create_notebook) already fully implemented with 17 passing tests — no further action needed. All components tested, ready for production validation. Next: deploy household_agent restart (requires sudo), optionally run `chkp insilver-v3` separately to verify fixes on live data.

---

## 2026-05-15: shared/ library audit — BACKLOG item invalidated

```yaml
archiued_at: 2026-05-15
reason: invalid assumption discovered, BACKLOG item deleted
tags: [shared, architecture, backlog-correction]
```

Аудит shared/ использования показав що BACKLOG пункт про shared/ refactor основувався на невирному припущенні. Реальна картина: **shared/ активна бібліотека, не архів.** sam використовує 11 imports, garcia використовує 7 с наслідуванням (PodcastModule, DigestModule, CurriculumEngine, CatchupModule), insilver-v3 використовує 1, meta/digest використовує 2. agent_base.py (24K) — активна інфраструктура, не мертвий код. BACKLOG пункт про shared/ refactor/cleanup видалено. Архітектурна стратегія shared/ + polyrepo — коли буде час — окрема дедикована сесія, не CC-task. Corrected assumption: shared/ не потребує невідкладного рефакторингу, integration stable.

---

## 2026-05-15: shared/ переїзд завершено — sym-link workspace → meta/shared

```yaml
archived_at: 2026-05-15
reason: completed, live in production
tags: [shared, architecture, workspace-refactor]
```

Reorganized shared/ library from workspace root to meta-репо as sym-link (git-tracked via meta). sys.path-import compatibility maintained across all users: sam (11 imports), garcia (7 with PodcastModule inheritance), insilver-v3-dev (1), meta/digest (2). Commit 5b41001 pushed to GitHub. Integration verified stable. Invalidated BACKLOG item about shared/ refactor (audit revealed shared/ is active library, not dead code — no immediate action needed). Polyrepo architecture strategy deferred to dedicated session when time allocated.

---

## 2026-05-15: Batch 1 chkp robustness + logging security + shared audit — completion

```yaml
archived_at: 2026-05-15
reason: tasks 1-7 completed, live validation pending
tags: [chkp, testing, logging-security, shared, batch-1]
```

Batch 1 sprint завершено. **httpx logging suppression:** household_agent/main.py + BotFather token rotation (others via shared/logger.py inheritance). **chkp.py robustness:** 4 fixes applied (multi-match context-aware line selection, replace() edge case whitespace strip, validation pre-flight improvement, test expansion) + 22 new unit tests (48/48 pass). **shared/ audit:** sym-link migration (workspace/shared → meta/shared), active users verified (sam 11, garcia 7 inheritance, insilver 1, meta/digest 2), BACKLOG item invalidated (shared/ not dead code). **Pre-push hook verification:** skipped (not found in insilver-v3-dev/.git/hooks/pre-push). **NBLM dangling UUID probe:** already fully implemented with 17 passing tests. Ready for production validation. Next: deploy household_agent restart, optionally run chkp separately on live data to verify fixes, continue httpx suppression on remaining 4 bots (ed, garcia, insilver-v3, sam).

---

## 2026-05-15: Token tracker audit — read-only log non-critical status

```yaml
archiued_at: 2026-05-15
reason: audit completed, non-critical finding, no action needed
tags: [cost-tracking, token-logging, audit, infrastructure]
```

Audit of shared/token_log.jsonl revealed: 74 entries since 2026-04-13, clean format (ts/agent/in/out/cost), write-side integrated only with digest + garcia. sam/insilver-v3/abby-v2/ed/meggy have inactive /stats UI (0 records for 30 days). **Conclusion:** per-bot token logging non-critical for current operations; Anthropic Console sufficient for total spend tracking. Per-bot fine-grained billing — deferred to future backlog item if granular allocation becomes business requirement. No code changes, no API impacts. Token_log.jsonl continues as audit trail for digest/garcia; other bots not required to activate. Monitoring: continue current state, revisit if cost allocation strategy changes.

---

## 2026-05-15: household_agent .git audit — gallery-dl cleanup verification

```yaml
archiued_at: 2026-05-15
reason: completed, obsolete BACKLOG item cleaned
tags: [household-agent, git, cleanup, backlog-maintenance]
```

Audit of household_agent .git after filter-repo cleanup (applied ~2026-05-04). **Finding:** 376K final size after cleanup, not 239M as BACKLOG item from 2026-04-29 suggested. Root cause: gallery-dl/pinterest images (252MB) already removed by filter-repo ~4 days prior, BACKLOG.md never updated. **Cleanup:** deleted .git/filter-repo/analysis (340K additional recovery). **Lesson:** BACKLOG item retention problem — obsolete tasks accumulate faster than review cycle. Entries without active work drift into stale state. Consider implementing bi-weekly BACKLOG hygiene pass to catch post-fix updates. Household_agent .git confirmed clean, no further action needed.

---

## 2026-05-15: BACKLOG hygiene pattern identified — shared/ + household_agent + pre-push hook

```yaml
archiued_at: 2026-05-15
reason: pattern observation for future workflow improvement
tags: [backlog, workflow, maintenance, process]
```

Pattern emerging: shared/ library refactor (invalidated 2026-05-15 after audit), household_agent .git cleanup (obsolete item from 2026-04-29), pre-push hook verification (skipped, hook not found). Three separate BACKLOG items pointing to same underlying issue: **BACKLOG accumulates obsolete faster than review velocity.** Filter-repo cleanups happen, but BACKLOG not updated. Audits reveal assumptions wrong, but items linger. Solutions: (1) establish bi-weekly BACKLOG hygiene pass during morning_digest review, (2) tag BACKLOG items with "verified-by-date" to age-sort inactive tasks, (3) link BACKLOG strikes to commits for traceability (prevent orphaned items). Next session: consider scheduling dedicated 30-min BACKLOG audit slot, post-digest summary.

---

## 2026-05-15: Postmortem chkp/BACKLOG drift — root cause identified

```yaml
archiued_at: 2026-05-15
reason: design brief ready, scheduled for CC implementation
tags: [chkp, backlog, automation, design, p1, postmortem]
```

Postmortem chkp v3.5 BACKLOG strike drift (empirical: 0674dd4 household_agent 2026-04-05, strike флага 11 днів). Mechanical validations (validate_backlog_flags fail-loud, multi-match context-aware replace) закрили syntactic bugs, але semantic проблема залишилась: AI у claude.ai чаті не звіряє 'що зробили' з активними пунктами BACKLOG, тому користувач просто не передає --backlog-strike флаги.

**Root cause:** Haiku генерує HOT.md, але не знає які пункти BACKLOG мають бути закриті. Користувач при ухвалі результатів лише читає ## Now/Last done, часто забуває звірити з BACKLOG або неправильно копіює FRAGMENT.

**Solution (CC brief ready):** suggest_backlog_strikes() — другий Haiku call після HOT генерації, пропонує список proposed strikes з UX блоком y/n/edit/skip. --no-backlog-suggest flag для opt-out. 8 pytest fixtures написано (clean_nblm_uuid, ambiguous_grep, multi_strike, closed_items, add_only, empty_backlog, no_changes, refactor_strike). Дизайн brief готовий, CC implementation session 2-3h. Smoke test на реальній сесії, потім rollout на 6 проектів.

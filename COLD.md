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

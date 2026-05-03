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

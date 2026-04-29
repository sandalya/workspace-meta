---
project: meta
updated: 2026-04-29
---

# HOT — meta

## Now

Workspace security + structure cleanup завершено. Root перестав бути git-репо (раніше пушився в `sandalya/sam.git` помилково), всі workspace-level файли перенесені в meta. 7 репо торкнуто: PII вирізана з історії, токени revoked, broken `.gitignore` виправлено.

## Last done

**2026-04-29** — security cleanup сесія (~6 год):

- abby legacy: PAT з .git/config revoked, папка видалена локально
- abby-v2: filter-repo (13 PII файлів), .git 12M→1.2M
- insilver-v3: filter-repo (4 PII + 3 TG tokens via --replace-text), .git 342M→17M, dev гілка з GH видалена
- insilver-v2: GitHub repo видалено повністю (легше за filter-repo, архів — legacy)
- garcia: .gitignore переписано (literal \n → newlines), filter-repo (6 PII + 4175 venv + 2008 pyc), .git 31M→1.3M
- sam: filter-repo (8 PII + 28k venv + 12k pyc + всі .bak/legacy), master + curriculum-v2 гілки з GH видалені, .git 72M→3.9M
- root → meta: 24 файли (BACKLOG, agent-docs, backup, chkp.sh, systemd-services-backup) перенесено, BACKLOG.md і CLAUDE.md → symlinks, root .git видалено
- meta: .gitignore створено, notes/BACKLOG.md → BACKLOG-archive-2026-04-29.md

**Сумарно:** ~415M звільнено, 1 PAT + 5 TG bot tokens revoked, всі prod services (abby-v2, household_agent, insilver-v3, garcia, sam) + pi5-backup.timer active.

## Next

1. Видалити репозиторій github.com/sandalya/abby-v1 вручну (Settings → Danger Zone).
2. Запустити `git filter-repo --analyze` на household_agent (.git 239M, причина не venv/pyc).
3. Через тиждень (~2026-05-06): рефакторинг shared/, рішення polyrepo vs гібрид.
4. Закрити insilver-v3-dev cleanup (4 PII файли в HEAD гілки dev — local-only, але push зруйнує).

## Blockers

Немає. Сервіси active.

## Active branches

Усі sub-repos (abby-v2, ed, garcia, household_agent, insilver-v3, kit, sam) на `main`, sync з GitHub. insilver-v3-dev на гілці `dev` (PII у HEAD, не пушити).

## Open questions

- Polyrepo (поточний стан) vs monorepo vs submodule-гібрид — обговорити через тиждень.
- shared/ — чи має взагалі існувати? (нічого не імпортується).

## Reminders

- `git filter-repo` чистить тільки checkout'нуті refs — стейл-гілки на GitHub потрібно видаляти окремо (`git push origin --delete <branch>`).
- Після filter-repo working tree скидається до HEAD через `git reset --hard` — нові edit'и .gitignore треба робити після filter-repo або комітити окремо.
- `chkp` alias викликає `meta/chkp/chkp.py` (Python). Старий root `chkp.sh` видалено.
- Backup тригер: `pi5-backup.timer` → `/home/sashok/.openclaw/workspace/backup/backup.sh` (root backup/ лишається на місці, не переноситься в meta).
- Workspace bekap: `/home/sashok/workspace-backup-20260429-1944.tar.gz` (6.7G).

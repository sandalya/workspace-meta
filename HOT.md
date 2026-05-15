---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

shared/ переїзд завершено: sym-link workspace/shared → meta/shared, sys.path-імпорти працюють, sam/garcia/insilver активні. Commit 5b41001 на GitHub. household_agent .git аудит: 712K (здоровий репо, давно вирішено).

## Last done

- Реорганізовано shared/ як sym-link з workspace на meta/shared (git-based, trackable)
- Перевірено sys.path-імпорти: sam (11 imports), garcia (7 з наслідуванням), insilver-v3-dev (1), meta/digest (2)
- Commit 5b41001 push на GitHub, структура поновлена
- household_agent .git аудит: виявлено 712K (183 objects, 78.61KiB pack) — мінімально здоровий репо, не 239M як у BACKLOG беклозі
- BACKLOG пункт про shared/ refactor видалено (invalid assumption — shared/ активна бібліотека)
- Batch 1 завершено: httpx logging, chkp robustness (48/48 tests PASS), morning_digest live

## Next

Либо Влада-Ксюші (voice extraction, ~2h) — коли часу виділено, либо антипастка #24 по іншому пункту беклогу. shared/ polyrepo architecture strategy — окрема дедикована сесія, коли час буде, не CC-task.

## Blockers

Нема.

## Active branches

- httpx logging suppression: live на 2/6 ботів (abby-v2, household_agent), решта 4 (ed, garcia, insilver-v3, sam) на черзі аудиту
- chkp.py robustness: 4 fixes + 22 нові тести (48/48 pass), ready for production validation
- morning_digest: systemd timer live 09:00 daily, Telegram delivery confirmed
- shared/ library: аудит завершено, BACKLOG кориговано

## Open questions

- Чи shared/ usage залишиться стабільною, чи garcia refactor (PodcastModule наслідування) потребує polyrepo planning?
- Потреба household_agent sudo restart, чи перезапуст уже автоматичний після токен ротації?
- Які регресії можуть виникнути від 4 chkp robustness fixes на live данних?
- Чи all 6 ботів (abby-v2, ed, garcia, household_agent, insilver-v3, sam) повинні мати однакову httpx suppression pattern?

## Reminders

- household_agent token ротований (BotFather, 2026-05-15), монітувати на anomalous use
- Backup chain ready, DR drill awaит spare SD card arrival
- BACKLOG rotation policy для abby images (759M) + sam audio (827M) відкладено на наступну сесію
- Strikethrough rule enforcement (CLAUDE.md + BACKLOG.md dual-location): спостереження 2–3 сесії, потім рішення про [CLOSED] markup
- httpx suppression потребується на 4 ботах (ed, garcia, insilver-v3, sam) перед наступним чекпоінтом
- shared/ BACKLOG item видалено (активна бібліотека, не мертвий код)
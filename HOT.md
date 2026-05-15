---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Аудит Sam NBLM Content Generation Pipeline завершено: всі 7 пунктів реалізовані (brief.py, DeepDive preset, Topic.brief, /regen --preset deepdive, NBLM logging, backend-agnostic архітектура). П.3 (кнопки перед запуском) навмисно пропущено (не потребується). Закрито insilver-v3-dev upstream без origin/dev (Model A).

## Last done

- Аудит Sam NBLM Content Generation Pipeline: brief.py ✅
- DeepDive preset implementation ✅
- Topic.brief поле в models.py ✅
- /regen --preset deepdive в article.py ✅
- NBLM args logging (info+debug) ✅
- Backend-agnostic архітектура ✅
- Пункт П.3 (кнопки перед запуском) навмисно пропущено
- Закрито insilver-v3-dev upstream без origin/dev (Model A)

## Next

token_tracker write-side експансія або аудит наступного проекту (garcia, ed, abby-v2). Якщо час дозволяє — дизайн Sam NBLM Інтервенція 2 (content_gen pipeline log aggregation).

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, smoke test + reason-quality моніторинг
- httpx logging suppression: 6/6 ботів live, токени ротовані
- backup.sh system-snapshot: live, real-run verified
- morning_digest: systemd timer 09:00, перевірка 2026-05-16
- shared/ sym-link: live (commit 5b41001)
- Sam NBLM Інтервенція 1: DONE, Інтервенція 2+ на черзі

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes при варіативних контекстах?
- Потреба household_agent sudo restart, чи systemd auto-restart достатній?
- Які регресії можуть виникнути з 4 chkp fixes при наступних strike-операціях?
- BACKLOG rotation policy для abby images (759M) + sam audio (827M)?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot?

## Reminders

- household_agent токен ротовано 2026-05-15 — монітор аномалій завтра
- morning_digest systemd timer verify 2026-05-16 о 09:00 (перший run)
- Backup chain: PC 14-day + Pi 3-day, weekly digest Sundays 03:00 (активна)
- DR drill очікує spare SD карти (фізична поставка)
- httpx suppression: усі 6 ботів live, якість перевірена
- shared/ library: active (sam 11, garcia 7, insilver 1, digest 2 imports) — не архів
- backup.sh system-snapshot: real-run tested, all config captured
- Sam NBLM Inter 1: DONE (uuid probe), Inter 2–5 на черзі

---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Aудит Sam P2 (NBLM Інтервенція 1) завершено: dangling nblm_notebook_id вже реалізовано в sam/core/content_gen/backends/nblm.py через probe source list -n <id> --json, invalidation + fallthrough на create. 4/4 тести TestNotebookProbe pass. Пункт був відкритий тому що написаний до реалізації.

## Last done

- Прочитав Sam NBLM backend код, get_or_create_notebook (lines 45–80)
- Перевірив UUID probe logic: source list -n --json для валідності перед reuse
- Запустив pytest sam/tests/test_nblm_backends.py::TestNotebookProbe — 4/4 pass
- Закрив BACKLOG пункт Інтервенція 1 як вже реалізовано (вказав у беклогу)
- Документував у WARM.md Sam NBLM блок що Inter 1 DONE,준비 для Inter 2 дизайну

## Next

Продовжити з огляду беклогу (пункти 7–11) або перейти на аудит наступного проекту (garcia, ed, abby-v2). Якщо час дозволяє — розглянути Sam NBLM Інтервенція 2 (content_gen pipeline лог агрегація) дизайн.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, smoke test + reason-quality моніторинг на наступні сесії
- httpx logging suppression: 6/6 ботів готово, токени ротовані
- backup.sh system-snapshot: live, syntax OK, real-run verified
- morning_digest: systemd timer 09:00, перевірка завтра (2026-05-16)
- shared/ sym-link: live (commit 5b41001), active users verified
- Sam NBLM Інтервенція 1: DONE (реалізовано раніше), Інтервенція 2+ на черзі

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes при варіативних контекстах (домашня робота, NBLM контекст)?
- Потреба household_agent sudo restart, чи systemd auto-restart достатній після токен ротації?
- Які регресії можуть виникнути з 4 chkp fixes (multi-match context, whitespace strip) на live даних при наступних strike-операціях?
- BACKLOG rotation policy для abby images (759M, 1315 files) + sam audio (827M, 26 mp3) — коли зберігати vs. видаляти?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot?

## Reminders

- household_agent токен ротовано 2026-05-15 — монітор аномалій у логах завтра
- morning_digest systemd timer verify завтра о 09:00 (перший run)
- Backup chain: PC 14-day + Pi 3-day, weekly digest Sundays 03:00 (активна)
- DR drill очікує spare SD карти (фізична поставка)
- httpx suppression: усі 6 ботів live, семантична якість перевірена
- shared/ library: active (sam 11, garcia 7, insilver 1, digest 2 imports) — не архів, не потребує рефакторингу
- backup.sh system-snapshot: real-run tested, settings.json + crontab/dpkg/pip все захоплено
- Sam NBLM Inter 1: DONE (uuid probe + invalidation live), Inter 2–5 на черзі у BACKLOG

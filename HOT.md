---
project: meta
updated: 2026-05-16
---

# HOT — meta

## Now

Верифіковано token tracker: /cost endpoint в Sam показує реальні дані після першого повідомлення. Усі 5 ботів (Sam, Garcia, household_agent, abby-v2, insilver-v3) мають write-side integration live. Зміни сесії в продакшені, готові до systemd restart для активації.

## Last done

- Token tracker write-side expansion: Sam (13 call sites, /stats live), Garcia (own tracker + set_default_tracker), household_agent (summarize_session instrumented), abby-v2 (fully tracked), insilver-v3 (fully tracked)
- shared/token_tracker.py enhancements: get_stats() per-agent filter, track_raw() з model= parameter для per-call pricing
- 23/23 unit tests PASS (Sam coverage)
- Verifikacija: /cost endpoint responses в реальному часі

## Next

Perезапустити sam.service та garcia.service (`sudo systemctl restart sam.service && sudo systemctl restart garcia.service`) щоб token_tracker write-side активувався. Потім перевірити /stats endpoint у обох ботів. Далі: token_tracker write-side на ed та household_agent, або дизайн Sam NBLM Інтервенція 2 (log aggregation) залежно від енергії.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, UX блок y/n/e/s, 54/54 pytest PASS, smoke test готовий
- httpx logging suppression: 6/6 ботів live, усі токени ротовані 2026-05-15, journalctl clean (834M→16M)
- backup.sh system-snapshot: live, real-run verified, configuration recovery functional
- morning_digest systemd timer: 09:00 daily, очікує першого 2026-05-16 запуску
- shared/ sym-link: live (workspace/shared → meta/shared, commit 5b41001)
- Sam NBLM Інтервенція 1: DONE (uuid probe), Інтервенція 2–5 на черзі
- token_tracker write-side: live для 5 ботів, systemd restart pending
- WARM diff-mode v3.5: live у продакшені, 79% token economia, масштабування повне
- chkp robustness fixes: 4 fixes (multi-match, replace edge case, validation, tests), 48/48 pytest PASS

## Open questions

- Яка точність reason-текстів у suggest_backlog_strikes при варіативних контекстах (NBLM, logging, cleanup)?
- Чи token tracker write-side вплине на latency /stats відповідей?
- Які регресії можуть виникнути з 4 chkp fixes при наступних strike-операціях на live BACKLOG?
- BACKLOG rotation policy для abby images (759M, 1315 files) + sam audio (827M, 26 mp3)?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot?
- Чи morning_digest 09:00 timer відпрацює коректно на Pi5 (першої виконання 2026-05-16)?

## Reminders

- household_agent токен ротовано 2026-05-15 — монітор аномалій у journalctl завтра
- morning_digest systemd timer verify 2026-05-16 о 09:00 (перший live run)
- Backup chain: PC (Windows 10, H:\pi_backups) 14-day retention, Pi 3-day local, weekly digest Sundays 03:00 — active
- DR drill очікує spare SD карти (фізична поставка) для restore verification
- httpx suppression: усі 6 ботів live, semantic quality перевірена в chatlog
- shared/ library: active (sam 11 imports, garcia 7 inheritance, insilver 1, digest 2) — BACKLOG item invalidated
- backup.sh system-snapshot: real-run tested 2026-05-15, all config captured (.claude/settings.json, systemd units, crontab, dpkg, pip freeze)
- Sam NBLM Inter 1: DONE (uuid probe logic verified), Inter 2 (log aggregation) ready для дизайну
- sam.service + garcia.service restart needed для token_tracker write-side activation (обов'язково для next checkpoint)
- shared/token_log.jsonl: 74 entries, write-side live для digest+garcia, non-critical для інших
- NBLM Content Generation: all 7 items verified live (brief.py, DeepDive preset, .brief field, /regen --preset deepdive, NBLM logging, backend-agnostic pipeline) — audit complete

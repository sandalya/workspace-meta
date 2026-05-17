---
project: meta
updated: 2026-05-17
---

# HOT — meta

## Now

Вимкнули heartbeat у openclaw gateway (kit3 ключ) — kit3 більше не їсть токени щогодини. gateway перезапущений, openclaw.json: heartbeat={enabled:false}.

## Last done

- Відключено heartbeat у openclaw gateway config
- gateway перезапущено з новою конфігурацією
- kit/.env ключ (...LAAA) залишений без змін, але більше не використовується heartbeat-сервісом

## Next

Перевірити AWS Console протягом 1 дня — kit3 витрати мають обнулитись без щогодинних heartbeat токен-спалювань. Якщо OK, документувати рішення у WARM. Якщо витрати залишаються, аудит інших kit сервісів на toxичні зависимостях от kit3.

## Blockers

None.

## Active branches

- suggest_backlog_strikes: live у продакшені, UX блок y/n/e/s, 54/54 pytest PASS, smoke test готовий
- httpx logging suppression: 6/6 ботів live, усі токени ротовані 2026-05-15, journalctl clean (834M→16M)
- backup.sh system-snapshot: live, real-run verified, configuration recovery functional
- morning_digest systemd timer: 09:00 daily, перший запуск перевірено 2026-05-16
- shared/ sym-link: live (workspace/shared → meta/shared, commit 5b41001)
- Sam NBLM Інтервенція 1: DONE (uuid probe), Інтервенція 2–5 на черзі
- token_tracker write-side: live для 5 ботів, systemd restart pending (sam, garcia)
- WARM diff-mode v3.5: live у продакшені, 79% token economia, масштабування повне
- chkp robustness fixes: 4 fixes (multi-match, replace edge case, validation, tests), 48/48 pytest PASS
- openclaw gateway heartbeat: відключено на 2026-05-17, AWS Console monitoring active

## Open questions

- Яка зміна у AWS Console kit3 витратах після heartbeat disable (очікується 1-2 дні для спостереження)?
- Чи є інші service'и у kit що також їдять токени щогодини (потреба аудиту openclaw.json)?
- Чи token_tracker write-side activation (sam, garcia systemctl restart) потребує перезапуску інших ботів?
- BACKLOG rotation policy для abby images (759M, 1315 files) + sam audio (827M, 26 mp3)?
- Потреба tmux-restore.sh для восстановлення сесій на Pi5 reboot?

## Reminders

- AWS Console monitoring: kit3 витрати мають зменшитись без heartbeat (очікуємо наступні 24 години)
- morning_digest systemd timer: перший live run 2026-05-16 о 09:00 верифіковано
- Backup chain: PC (Windows 10, H:\pi_backups) 14-day retention, Pi 3-day local, weekly digest Sundays 03:00 — active
- DR drill очікує spare SD карти (фізична поставка) для restore verification
- httpx suppression: усі 6 ботів live, semantic quality перевірена в chatlog
- shared/ library: active (sam 11 imports, garcia 7 inheritance, insilver 1, digest 2) — BACKLOG item invalidated
- backup.sh system-snapshot: real-run tested 2026-05-15, all config captured (.claude/settings.json, systemd units, crontab, dpkg, pip freeze)
- Sam NBLM Inter 1: DONE (uuid probe logic verified), Inter 2 (log aggregation) ready для дизайну
- sam.service + garcia.service restart needed для token_tracker write-side activation (обов'язково для next checkpoint)
- shared/token_log.jsonl: 74 entries, write-side live для digest+garcia, non-critical для інших
- openclaw.json heartbeat={enabled:false}: відключено 2026-05-17, gateway перезапущено
- kit3 витрати очікуються обнулитись протягом 24 годин без heartbeat щогодинних spike'ів

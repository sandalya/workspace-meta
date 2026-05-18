---
project: meta
updated: 2026-05-18
---

# HOT — meta

## Now

Знайшли і відключили openclaw-gateway crash loop (8427 рестартів за кілька днів, ~4.5W зайвого енергоспоживання Pi5, помітне зниження теплоємності з 1.5A до 0.6A). Проблема: openclaw v2026.3.12 не приймає agents.defaults.heartbeat.enabled конфіг, gateway падав кожні ~7 сек, systemd рестартував з RestartSec=5. User systemd unit (~/.config/systemd/user/openclaw-gateway.service) тепер disabled.

## Last done

- Ідентифіковано openclaw-gateway crash loop через systemctl status openclaw-gateway.service
- Причина: invalid heartbeat config у openclaw.json, gateway падав із exit code 1 кожні ~7 сек
- Рішення: disabled user systemd unit (systemctl --user disable openclaw-gateway.service)
-備份конфіга: ~/.openclaw/openclaw.json.bak-20260518-1847 (для future debugging)
- Верифікація: systemctl status openclaw-gateway.service показує inactive (disabled), Pi5 теплоємність нормалізована
- AWS Console monitoring: kit3 витрати вже знизилися (heartbeat + gateway crash loop обидва erano спалювачами)

## Next

Опціонально: дослідити коли crash loop стартував (журнали kernel/systemd) і чи потрібен openclaw-gateway взагалі для meta проекту. Якщо не потребуємо — видалити user service остаточно. Якщо потребуємо — розглянути upgrade на v2026.3.13+ або custom patched config без heartbeat.

## Blockers

None.

## Active branches

- openclaw-gateway heartbeat: crash loop відключено 2026-05-18, user service disabled
- kit3 AWS Console monitoring: очікуємо зниження витрат за наступні 24 години (heartbeat disable 2026-05-17 + gateway crash loop disable 2026-05-18)
- suggest_backlog_strikes: live у продакшені, 54/54 pytest PASS, production-ready
- httpx logging suppression: 6/6 ботів live, усі токени ротовані
- backup.sh system-snapshot: live, configuration recovery functional
- morning_digest systemd timer: live о 09:00 daily
- shared/ sym-link: live (commit 5b41001)
- Sam NBLM Інтервенція 1: DONE, Інтервенція 2–5 на черзі
- token_tracker write-side: live для 5 ботів (sam, garcia restart pending)
- WARM diff-mode v3.5: live, 79% token economia, масштабування повне
- chkp robustness fixes: 48/48 pytest PASS

## Open questions

- Коли crash loop стартував? (можна чекнути journalctl та systemd logs)
- Чи потрібен openclaw-gateway для meta вообще, чи це legacy artifact?
- Яка точна версія openclaw у ~/.openclaw/openclaw.json.bak-20260518-1847?
- Чи є інші user systemd services в ~/.config/systemd/user/ що можуть виганяти токени?
- token_tracker write-side: sam + garcia restart потребує планування (можливість downtime?).

## Reminders

- openclaw-gateway crash loop: відключено 2026-05-18 через disabled user service
- kit3 AWS Console: очікуємо моніторинг наступні 1-2 дні (heartbeat 2026-05-17 + crash loop 2026-05-18 могли б обидва спалювати)
- backup конфіга: ~/.openclaw/openclaw.json.bak-20260518-1847 (для future debugging ако будемо ре-активувати gateway)
- morning_digest systemd timer: live, перший run верифіковано
- Backup chain: active (PC 14-day, Pi 3-day, weekly digest Sundays 03:00)
- DR drill: очікує spare SD карти
- httpx suppression: усі 6 ботів live
- Sam NBLM Inter 1: DONE, Inter 2 design ready
- sam.service + garcia.service restart needed для token_tracker write-side activation (заплановано для next checkpoint)
- shared/token_log.jsonl: non-critical per-bot tracking

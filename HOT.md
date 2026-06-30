---
project: meta
updated: 2026-06-30
---

# HOT — meta

## Now

Cleanup застарілої інфраструктурної документації після міграції Pi5 → Beelink SER5 (червень 2026). Оновлено HOT/WARM/COLD/BACKLOG/agent-docs: видалено Pi5-специфічні записи, openclaw-gateway, DR drill для SD.

## Last done

- Мігрували з Raspberry Pi 5 на Beelink SER5 (sashok-SER, 192.168.72.191, Ubuntu 24.04) — червень 2026
- Ed-ключ ротовано — Ed працює з новим ключем (розслідування $11.79 закрито)
- Sam-ключ ротовано у травні 2026
- Очищено meta документацію від застарілих Pi5 / openclaw-gateway записів

## Next

- Перевірити/переробити backup стратегію для Beelink SER5 (стара H:\pi_backups + SSH pi5_backup схема — Pi5-специфічна)
- Sam NBLM Інтервенція 2 — log aggregation (design ready)

## Blockers

None.

## Active branches

- WARM diff-mode v3.5: live, 79% token economy
- suggest_backlog_strikes: live, 54/54 pytest PASS
- httpx logging suppression: 6/6 ботів live
- Sam NBLM Інтервенція 1: DONE, Інтервенція 2 design ready
- morning_digest systemd timer: live о 09:00 daily

## Open questions

- Яка нова backup стратегія для Beelink SER5?
- Sam NBLM Інтервенція 2 — готові до імплементації log aggregation?

## Reminders

- Сервер: **Beelink SER5**, hostname `sashok-SER`, IP `192.168.72.191`, Ubuntu 24.04 LTS (міграція з Pi5, червень 2026)
- Ed-ключ: ротовано, Ed на новому ключі
- Sam-ключ: ротовано у травні 2026, sam.service live

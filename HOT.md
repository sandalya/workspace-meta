---
project: meta
updated: 2026-07-01
---

# HOT — meta

## Now

Зачищено Pi5/gateway/samuel-v1 References у meta документації на користь Beelink SER5/abby-v2. Закрито backlog пункти: DR drill SD, Ed-ключ P1. Виконано чекпоінти для abby-v2 і drone-recon, filter-repo drone-recon скоротив .git з 2.2G до 6.9M (видалено scraper+raw_frames з історії).

## Last done

- Оновлено WARM.md: Off-device backup chain archived як outdated (Pi5-специфічна схема)
- COLD.md: додано 2026-06-30 записи про міграцію Pi5→Beelink SER5 та Ed-ключ ротацію
- BACKLOG.md: замінено Pi5 referencias на Beelink SER5, видалено застарілі пункти про openclaw-gateway
- CLAUDE.md agent-docs: видалено інструкції для Pi5, оновлено на Beelink SER5 SSH інструкції
- drone-recon filter-repo: .git 2.2G→6.9M, .gitignore переписаний, force push успішний, repository чистий
- abby-v2 чекпоінт: HOT/WARM/COLD синхронізовані, готові до сесійного запуску

## Next

- Продовжити Pi5-cleanup в решті 5 проектів (insilver-v3, sam, garcia, ed, household_agent): видалити Pi5 references, оновити COLD.md
- Переробити backup стратегію для Beelink SER5 (замість H:\pi_backups + SSH pi5_backup, розглянути systemd timer + local USB backup або cloud solution)
- Sam NBLM Інтервенція 2 — дизайн log aggregation, готовий до імплементації

## Blockers

None.

## Active branches

- WARM diff-mode v3.5: live, 79% token economy ( 6 проектів готові до масштабування)
- suggest_backlog_strikes: live, semantic drift fix, 54/54 pytest PASS
- httpx logging suppression: 6/6 ботів live, security patch deployed
- Sam NBLM Інтервенція 1: DONE (UUID dangling detection live), Інтервенція 2 design ready
- morning_digest systemd timer: live о 09:00 daily, Telegram BACKLOG summary
- Infrastructure: migrated Pi5→Beelink SER5 (червень 2026), backup strategy outdated

## Open questions

- Яка нова backup стратегія для Beelink SER5? (local USB + systemd timer vs. cloud S3 vs. intra-LAN pull?)
- Чи потреба переробити инші проекти (insilver-v3, sam, garcia, ed, household_agent) у цьому циклі, чи закласти на наступну сесію?
- Sam NBLM Інтервенція 2 (log aggregation) — який пріоритет у поточному backlog?

## Reminders

- Сервер: **Beelink SER5**, hostname `sashok-SER`, IP `192.168.72.191`, Ubuntu 24.04 LTS (основний, Pi5 deprecated)
- Off-device backup chain (Pi5 схема): archived 2026-06-30, потребує переробки для Beelink
- Ed-ключ: ротовано 2026-06-30, Ed на новому ключі
- Sam-ключ: ротовано у травні 2026, sam.service live
- DIY UPS для Pi5 (XL4015 + 18650): зібрано 2026-05-19, GPIO integration incomplete (залишилось з Pi5)
- Api keys: 9 окремих ключів (abby-v2, ed, garcia, household_agent, insilver-v3, kit, sam, sam-v2, meta/digest) — НЕ консолідувати

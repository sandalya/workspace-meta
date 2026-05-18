---
project: meta
updated: 2026-05-19
---

# HOT — meta

## Now

Зібрав DIY UPS для Pi5 (XL4015 + LX-LIFC + 2S2P 18650 + SR340), пройшов всі тести, throttled=0x0, EXT5V=5.27V стабільно.

## Last done

- Спроектував та паяв DIY UPS модуль для Pi5 із XL4015 buck-boost контролером
- Скомплектував 2S2P 18650 батарею (4 комірки, ~5800mAh) із SR340 BMS
- Перевірив регуляцію напруги: 5.27V стабільна при нормальному навантаженні
- Запустив стрес-тест на 8 годин, throttled=0x0 (без дроселювання)
- Оцінив час автономії ~7-8 годин для київських blackouts

## Next

Інтегрувати моніторинг батареї через GPIO або розробити safe shutdown скрипт для перезагавання перед відключенням мережі.

## Blockers

None.

## Active branches

- DIY UPS для Pi5: завершено фізичну збірку і тестування, наступний крок software integration
- Prompt caching reuse: готово до live test на meta/insilver-v3-dev
- openclaw-gateway crash loop: відключено 2026-05-18, user service disabled
- kit3 AWS Console monitoring: очікуємо зниження витрат за наступні 24 години
- suggest_backlog_strikes: live у продакшені, 54/54 pytest PASS
- httpx logging suppression: 6/6 ботів live, усі токени ротовані
- backup.sh system-snapshot: live, configuration recovery functional
- morning_digest systemd timer: live о 09:00 daily
- shared/ sym-link: live (commit 5b41001)
- Sam NBLM Інтервенція 1: DONE, Інтервенція 2–5 на черзі
- token_tracker write-side: live для 5 ботів (sam, garcia restart pending)
- WARM diff-mode v3.5: live, 79% token economia
- chkp robustness fixes: 48/48 pytest PASS

## Open questions

- Яким GPIO пінам присвоїти battery voltage sense для hardware monitoring? (i2c-pull-ups для ADS1115 чи GPIO на 3v3 divider?)
- Які порогові значення напруги для safe shutdown? (critical: 4.5V, warning: 5.0V?)
- Чи інтегрувати safe shutdown у systemd-hibernate-resume.service чи окремий daemon скрипт?
- Чи cache_r > 0 буде спостережено на реальному чекпоінті при suggest_backlog_strikes?
- Чи потрібен openclaw-gateway для meta вообще?

## Reminders

- DIY UPS готовий до software integration наступної сесії
- openclaw-gateway crash loop: відключено 2026-05-18, disabled user service, конфіг бекапований
- kit3 AWS Console: очікуємо моніторинг наступні 1-2 дні
- Backup chain: active (PC 14-day, Pi 3-day, weekly digest Sundays 03:00)
- DR drill: очікує spare SD карти
- httpx suppression: усі 6 ботів live
- Sam NBLM Inter 1: DONE, Inter 2 design ready
- sam.service + garcia.service restart needed для token_tracker write-side activation
- Prompt caching reuse: live test потребує перевірки response_metadata.usage.cache_read_input_tokens > 0
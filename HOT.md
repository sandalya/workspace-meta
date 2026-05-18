---
project: meta
updated: 2026-05-19
---

# HOT — meta

## Now

Аудит витрат: знайшов і ротував витік sam API-ключа (засвітився у grep), додатково розслідував $11.79 USD на Ed-ключі за 18.05 — джерело не на Pi5. Sam-ключ дисейблено, новий записано в sam/.env та meta/digest/.env, sam.service рестартнутий.

## Last done

- Знайшов витік sam API-ключа в grep логах
- Ротував sam-ключ через AWS Console, записав новий у sam/.env і meta/digest/.env
- Рестартнув sam.service — працює
- Розслідував $11.79 USD витрат на Ed-ключі за 18.05 — джерело не на Pi5 (можливо інший пристрій)
- Додав пункт у BACKLOG про Ed-ключ дослідження

## Next

Disable Ed-ключ після перевірки інших пристроїв на використання.

## Blockers

None.

## Active branches

- Ed-ключ audit: $11.79 USD витрати 18.05 незрозумілого походження, потреба перевірки на інших машинах
- DIY UPS для Pi5: завершено фізичну збірку, software integration наступна сесія
- Prompt caching reuse: live test потребує перевірки response_metadata.usage.cache_read_input_tokens
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

- Де на інших пристроях може використовуватися Ed-ключ? (laptop, інший сервер, CI/CD?)
- Яким GPIO пінам присвоїти battery voltage sense для DIY UPS? (i2c pull-ups для ADS1115 чи 3v3 voltage divider?)
- Які порогові значення напруги для safe shutdown? (critical: 4.5V, warning: 5.0V?)
- Чи cache_r > 0 буде спостережено на реальному чекпоінті при suggest_backlog_strikes?
- Чи потрібен openclaw-gateway для meta взагалі?

## Reminders

- Sam-ключ новий: `sam.service` працює з оновленим ключем, потреба перевірки інших сервісів що можуть його кешувати
- Ed-ключ поки активний — потреба аудиту інших пристроїв перед disable
- ed-bot.service потребує додання `EnvironmentFile=/path/.env` як у abby-v2/household_agent (той самий баг витрат, як у 2026-05-14)
- DIY UPS готовий до software integration наступної сесії
- openclaw-gateway crash loop: відключено 2026-05-18, конфіг бекапований
- kit3 AWS Console: очікуємо моніторинг наступні 1-2 дні
- Backup chain: active, DR drill очікує spare SD
- Sam NBLM Inter 1: DONE, Inter 2 design ready
- sam.service + garcia.service restart needed для token_tracker write-side activation
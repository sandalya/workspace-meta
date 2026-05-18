---
project: meta
updated: 2026-05-18
---

# HOT — meta

## Now

Промпт caching оптимізація в chkp: перенесено _SUGGEST_SYSTEM конфіг до _SUGGEST_USER_PREFIX для reuse SYSTEM_PROMPT (1612 токенів) між main HOT call і suggest_backlog_strikes. Очікується cache_r > 0 на другому виклику Haiku.

## Last done

- Розширено SYSTEM_PROMPT до 1612 токенів з явною канонічною источниками для кожної секції HOT
- Переведено _SUGGEST_SYSTEM → _SUGGEST_USER_PREFIX, тепер шарить cacheable контент з main call
- Оновлено suggest_backlog_strikes() для reuse SYSTEM_PROMPT вміст (cache control)
- Додано 2 integration test case'и (test_cache_suggest_reuse, test_prompt_caching_integration) до test_prompt_caching.py
- 7 unit-тестів + 2 integration = 64/64 PASS локально

## Next

Запустити реальний chkp на meta або insilver-v3-dev, перевірити response_metadata на cache_r > 0 при другому виклику suggest_backlog_strikes. Якщо cache_r спостережено — документувати token savings у PROMPT-CACHING.md (очікується +10-20% на 1000-token overhead). Якщо cache miss — дебаг через fixtures перевірити prompt структуру.

## Blockers

None.

## Active branches

- Prompt caching reuse: готово до live test
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

- Чи cache_r > 0 буде спостережено на реальному чекпоінті при suggest_backlog_strikes?
- Як повинна виглядати SYSTEM_PROMPT структура для оптимальної cacheable granularity (сейчас 1612 tokens, що більш 1024 мінімум)?
- Чи потрібен openclaw-gateway для meta вообще, чи це legacy artifact (користувався у 2026-04 для пілотів)?
- Яка точна версія openclaw у ~/.openclaw/openclaw.json.bak-20260518-1847?
- Чи є інші user systemd services в ~/.config/systemd/user/ що можуть виганяти токени?

## Reminders

- openclaw-gateway crash loop: відключено 2026-05-18, disabled user service, конфіг бекапований
- kit3 AWS Console: очікуємо моніторинг наступні 1-2 дні (heartbeat + crash loop combo)
- Backup конфіга: ~/.openclaw/openclaw.json.bak-20260518-1847 для future debugging
- morning_digest systemd timer: live, перший run верифіковано
- Backup chain: active (PC 14-day, Pi 3-day, weekly digest Sundays 03:00)
- DR drill: очікує spare SD карти
- httpx suppression: усі 6 ботів live
- Sam NBLM Inter 1: DONE, Inter 2 design ready
- sam.service + garcia.service restart needed для token_tracker write-side activation
- shared/token_log.jsonl: non-critical per-bot tracking
- Prompt caching reuse: live test потребує перевірки response_metadata.usage.cache_read_input_tokens > 0
---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

morning_digest готовий: парсер реальної структури BACKLOG (інлайн (Pn) маркери + closed sections), Haiku 4.5 синтез зі збереженням мови оригіналу, HTML parse_mode для Telegram, systemd timer 09:00 щодня. Токен Sam-бота ротовано через @BotFather після витоку у claude.ai чаті, sam.service рестартнуто.

## Last done

- Написано morning_digest скрипт із реальним парсером BACKLOG структури (інлайн (Pn) маркери, closed sections, uncategorized items)
- Реалізовано Haiku 4.5 синтез із збереженням мови оригіналу та чистою відповіддю (без пояснень)
- Додано HTML parse_mode для Telegram mensages (розривів строк, моноширинних блоків)
- Налаштовано systemd timer на 09:00 щодня з автоматичним відправленням digest до chat_id
- Виявлено та ротовано Sam-бота токен (витік через sed маску у claude.ai), sam.service перезапущено
- Завершено 11/11 unit-тестів, cost ~0.0026 USD за run (~0.08/місяць на автоматизації)
- Налаштовано meta/digest/.env з SAM_BOT_TOKEN, OWNER_CHAT_ID, ANTHROPIC_API_KEY (реюз із sam/.env)

## Next

Перевірити завтра що systemd timer 09:00 відпрацював; додати (Pn) маркери до решти uncategorized пунктів у BACKLOG для кращої пріоритезації.

## Blockers

Нема.

## Active branches

- morning_digest: live systemd timer 09:00 daily, Telegram delivery ready
- Logging security: httpx suppression live на 2/6 ботів, audit старих journalctl продовжується
- Anthropic SDK cost isolation: EnvironmentFile= fix live, AWS Console перевірка 2026-05-15
- chkp.py validation: pre-flight checks, fail-loud з fuzzy hints

## Open questions

- Чи 09:00 timer відпрацює завтра з правильною структурою digest?
- Чи (Pn) маркери будуть розпізнані у решти uncategorized пунктів або потреба рефакторингу парсера?
- Які ще витоки API keys або токенів у claude.ai логах чекати?

## Reminders

- BACKLOG.py replace() bug: потреба fix для multi-match сценаріїв
- httpx INFO logging: suppression на всіх 6 ботах required
- Strikethrough дублювання: CLAUDE.md + BACKLOG.md для надійності
- Sam токен ротовано на 2026-05-15, monitor для аномального use
- Backup chain готовий, DR drill очікує запасної SD карти
- abby images (759M) + sam audio (827M) — rotation policy відкладене
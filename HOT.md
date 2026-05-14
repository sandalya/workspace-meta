---
project: meta
updated: 2026-05-14
---

# HOT — meta

## Now

Знайшли й пофіксили причину фонових витрат на kit3+Ed ключах: ed-daily.timer був зупинений, judge використовував Haiku; abby-v2 й household_agent отримали EnvironmentFile= в systemd-юнітах (раніше Anthropic SDK знаходив workspace/.env з kit3 ключем через find_dotenv()).

## Last done

- Виявлено витік витрат: ed-daily.timer зупинений, judge на Haiku
- Діагностовано корінь у shared/agent_base.py: client = anthropic.Anthropic() без load_dotenv()
- find_dotenv() автоматично підхоплював workspace/.env з kit3 ключем замість проектних .env
- Додано EnvironmentFile= в systemd-юніти abby-v2 та household_agent
- Перевірено sam-rss і insilver-v3-error-monitor — не кличуть Anthropic
- Вивчено judge семантичні assertions — потреба мануальної регресії для порівняння з еталоном 37/17/23

## Next

Завтра перевірити AWS Console: kit3 ключ має обвалитись, на abby-v2/household_agent ключах мають з'явитися Sonnet+Haiku трафік.

## Blockers

Нема.

## Active branches

- Logging security (httpx suppression): live на abby-v2, ed-bot; household_agent, insilver-v3 ще under audit
- Backup chain: PC pull (14d) + Pi rotation (3d) — fully automated
- chkp.py validation: pre-flight checks live, fail-loud з fuzzy hints
- Anthropic SDK cost isolation: EnvironmentFile= fix live, Console перевірка завтра

## Open questions

- Обвалиться ли kit3 витрати завтра? Чи есть інші витоки на інших ключах?
- Judge Haiku assertions: яка реальна pass rate після першої регресії порівняно з 37/17/23?
- Які ще dotfiles потребують резервування: systemd/user/, crontab, dpkg list, git config?

## Reminders

- BACKLOG.py replace() bug: replace(FRAGMENT, 1) замість replace(FRAGMENT) — fix потрібен
- httpx INFO logging suppression: live на 2/6 ботів, потреба audit старих journalctl за leaks
- Strikethrough правило дублюється (CLAUDE.md + BACKLOG.md) для надійності LLM
- Backup chain повністю автоматизована, DR drill очікує приїзду запасної SD карти
- abby images (759M) + sam audio (827M) — rotation policy відкладене на наступний цикл
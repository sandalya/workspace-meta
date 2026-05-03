---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

chkp v3.2 — backlog v2. Переписано `update_backlog` на JSON-action підхід (strike/add/summary). AI більше не пише повний файл, а генерує дії які chkp застосовує механічно через str.replace. max_tokens=2000 щоб не обрізалось.

## Last done

**2026-05-03** — chkp backlog v2 рефакторинг (~1 година):

- **JSON-action підхід** — `update_backlog()` тепер просить AI генерувати JSON з "strike": ["рядки для видалення"], "add": ["нові рядки"], "summary": "опис змін". Механічне застосування через str.replace замість повного переписування файлу.
- **Надійність** — max_tokens=2000 щоб AI не обрізав відповідь на середині JSON. Менше ризику втратити дані через неповні відповіді.
- **Контроль якості** — AI тепер повинен точно знаходити існуючі рядки для strike-операцій, не може вигадувати зміст файлу.
- **Backward compatibility** — зберігається інтерактивний y/n/e/s flow і commit логіка.

## Next

1. **Протестувати на реальному виклику** — запустити `chkp <project> "..." "..." "..."` на реальному проекті (abby, garcia, або household_agent), перевірити якість strike-match і чи AI не вигадує неіснуючі рядки.
2. **Спостерігати за edge cases** — чи правильно AI знаходить рядки для видалення, чи не конфліктує з форматуванням markdown.
3. Якщо працює стабільно — документувати JSON-action підхід у BACKLOG як "chkp workflow v2" блок.

## Blockers

Немає. chkp v3.2 готовий для тестування.

## Active branches

- meta: main (v3.2 з backlog v2)
- Усі sub-repos на main, sync з GitHub
- Remote dev: Pi5 через Tailscale + Termius

## Open questions

- Чи AI буде правильно знаходити рядки для strike без false matches?
- Чи достатньо max_tokens=2000 для складних backlog змін?
- Чи додати валідацію JSON перед застосуванням дій?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи, використовувати для тестування нових фіч в реальних умовах.
- chkp --help має документуватися у notes/ для майбутніх розробників.
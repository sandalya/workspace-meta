---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

chkp v3.3 — backlog read-only assistant. AI тепер видає текстові спостереження про BACKLOG, не редагує файл. BACKLOG править руками через nano. Видалено apply_backlog_changes, commit_backlog, прапор --no-backlog.

## Last done

**2026-05-03** — спрощення update_backlog (30 хв):

- **Видалено JSON-action підхід** — складність не виправдана. AI часто вигадував рядки для strike, false matches на форматуванні.
- **Новий підхід** — update_backlog() тепер просто читає BACKLOG, генерує текстові спостереження ("Видно 3 висячих пункти", "garcia task стара", "insilver на review"), друкує їх. Жодних дій на файл.
- **Контроль у користувача** — BACKLOG відкривається в nano руками. Користувач вирішує що редагувати. Видалено commit_backlog () і прапор --no-backlog.
- **Результат** — менше потенціалу для помилок, CI/CD простіший, користувач має явний контроль.

## Next

1. **Протестувати на реальному вызові** — `chkp <project> "..." "..." "..."`, перевірити чи AI-спостереження корисні чи буде шумом.
2. **Зібрати фідбек** — чи користувач читає текстові підказки, чи вони впливають на рішення про редагування BACKLOG.
3. Якщо корисно — залишити як є. Якщо шум — можна видалити update_backlog() повністю.

## Blockers

Немає. chkp v3.3 готовий для тестування.

## Active branches

- meta: main (v3.3 з backlog read-only assistant)
- Усі sub-repos на main, sync з GitHub
- Remote dev: Pi5 через Tailscale + Termius

## Open questions

- Чи AI-спостереження будуть корисні чи буде шумом при частих запусках chkp?
- Чи варто додати параметр `--quiet` щоб пропустити update_backlog при спіху?
- Чи окремо видавати спостереження для BACKLOG vs HOT/WARM?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи, використовувати для тестування нових фіч в реальних умовах.
- chkp --help має документуватися у notes/ для майбутніх розробників.
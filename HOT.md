---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

chkp v3.1 — backlog integration. Додано `update_backlog` і `commit_backlog` в chkp.py: AI-пропозиція оновлень BACKLOG через Haiku, інтерактивний y/n/e/s, окремий commit у meta repo для не-meta проектів.

## Last done

**2026-05-03** — chkp backlog integration (~1.5 год):

- **update_backlog()** — генерує AI-пропозицію змін до BACKLOG.md через Haiku (fallback Sonnet), показує diff.
- **commit_backlog()** — інтерактивний цикл: y (прийняти), n (відхилити), e (edit), s (skip). При прийнятті — commit у meta-репо.
- **Per-project commits** — якщо chkp запущений з non-meta проекту (abby, garcia, sam, etc.), commit іде в meta як `Update <project> backlog` без спроб писати в sub-проект.
- **Тестування** — попередні інтеграційні test'и (mock Haiku, mock git) пройшли. Ready для реального виклику з бекло́г-оновленням.

## Next

1. **Протестувати на реальному виклику** — запустити `chkp <project> "..." "..." "..."` на реальному проекті (abby, garcia, або household_agent), спостерігати AI-пропозицію, інтерактивний y/n/e/s, commit у meta.
2. Якщо працює — документувати flow у BACKLOG як "chkp workflow" блок.
3. Додати `--no-commit` прапорець для сухого запуску (для перевірки без commit'у).
4. Розглянути інтеграцію в systemd timer для периодичного backlog refresh'у (раз на день/тиждень).

## Blockers

Немає. chkp v3.1 вже у workspace/meta, git sync'd.

## Active branches

- meta: main (v3.1 з backlog integration)
- Усі sub-repos на main, sync з GitHub
- Remote dev: Pi5 через Tailscale + Termius

## Open questions

- Як часто запускати backlog refresh? Чи варто в systemd timer?
- Чи додати `--dry-run` окрім `--no-commit`?
- Чи генерувати AI-пропозицію для кількох проектів за раз (batch mode)?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи, використовувати для тестування нових фіч в реальних умовах.
- chkp --help має документуватися у notes/ для майбутніх розробників.
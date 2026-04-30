---
project: meta
updated: 2026-04-30
---

# HOT — meta

## Now

Remote dev setup завершено. tmux + Tailscale + Termius налаштовано для роботи з ботами в дорозі через Pi5.

## Last done

**2026-04-30** — Remote dev infrastructure (~2 год):

- **tmux** — налаштовано для переживання обривів мережі (detach/reattach). Alias `w` = `tmux new -A -s work`. Базові команди: Ctrl+B D (detach), `tmux attach -t work` (reattach), `tmux ls` (список сесій). ⚠️ Важливо: tmux НЕ переживає reboot Pi5 — сесії теряються, потрібна автоматизація відновлення на старті.
- **Tailscale** — тунель Pi5 ↔ телефон (Android). Мережа стабільна, всі сервіси доступні через приватну IP Pi5.
- **Termius** — SSH-клієнт на Android, підключено до tmux на Pi5 через Tailscale. Robustness: розриви connection автоматично перелогінюються.
- **Workflow** — 1) Запустити `w` в Termius → tmux attach до роботочої сесії. 2) Детач Ctrl+B D при очікуванні. 3) Reattach пізніше з того ж або іншого пристрою.

**Сумарно:** готово до роботи в дорозі, базова інфраструктура стабільна.

## Next

1. Почати реально працювати в дорозі — розтестувати workflow на довших сесіях (2-3+ год).
2. Розділити роботочі сесії — один tmux-сесія per проект (окрім `work` базової): `abby`, `garcia`, `sam`, etc. Це дозволить паралельно монітояти кілька ботів.
3. Написати `tmux-restore` скрипт на старті Pi5 — восстановити попередні сесії після reboot (зберігати список сесій в файл, відновлювати через цикл в systemd).
4. Додати `tmux` секцію до BACKLOG як future refactor.

## Blockers

Немає. Сервіси active, мережа стабільна.

## Active branches

Усі sub-repos на `main`, sync з GitHub. Remote dev на Pi5 через Tailscale.

## Open questions

- Скільки сесій розділяти? (Per-проект, per-компонент, per-користувач?)
- Чи варто автоматизувати reboot-recovery для tmux через systemd service?
- Мониторинг long-running сесій — логування в файл чи tmux буфер?

## Reminders

- tmux buffer на Pi5 зберігає історію в RAM — при reboot теряється. Якщо критичні логи — перенаправляти в файл через `tee`.
- Termius підтримує port forwarding — можна пробросити локальні порти на телефон для web-интерфейсів (приклад: `http://localhost:8000` → household_agent веб-панель).
- Tailscale на Pi5 має baked-in exit node — можна конфігурувати як VPN для телефона через Pi5.
- `alias w` живе в `~/.bashrc` на Pi5 — повинен бути скопійований при setup нового сессиона.

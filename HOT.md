---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

chkp v3.4 — біна-шим для PATH. Legacy bash v1 з /home/sashok/.local/bin/chkp замінена на Python shim що викликає chkp.py v3.4. Усі звернення (PuTTY, CC, subshell, cron) тепер йдуть на v3.4, не на застарілий v1.

## Last done

**2026-05-03** — інфра-фікс PATH бінарного підходу (40 хв):

- **Створено Python shim** — `/home/sashok/.local/bin/chkp` тепер викликає `python3 chkp.py v3.4` з аргументами, замість виконання bash v1 скрипту.
- **Усунено розбіжність alias vs PATH** — раніше PuTTY викликав chkp через alias (v3.4), але `bash -c chkp` (CC/subshell/cron) потрапляв у /usr/bin/chkp або /bin/chkp (legacy v1), писав SESSION.md замість HOT/WARM/COLD.
- **Верифікація** — `bash -c chkp --help` тепер показує v3.4 з опціями --backlog-strike, --backlog-add, --sonnet.
- **Сайд-ефект** — виявлено SESSION.md у meta repo (зі старого v1 запуску), потреба cleanup.

## Next

1. **Видалити legacy скрипти:**
   - `/home/sashok/workspace/kit/chkp.sh` (v1 reference)
   - `/home/sashok/workspace/kit/chkp2.sh` (тест v2)
   - `/home/sashok/.openclaw/workspace/meta/chkp.sh` (копія v1)
   - `/home/sashok/.openclaw/workspace/meta/chkp.py.bak` (backup v3.0)
2. **Видалити SESSION.md з meta repo** — це артефакт старого v1 запуску, потрапив у git.
3. **Додати SESSION.md до .gitignore** — уникнути майбутніх подібних файлів від v1 або тесту.
4. **Перевірити .gitignore в усіх проектах** — чи там SESSION.md вже, чи потреба синхронізації.

## Blockers

Немає. Перехід на PATH binary завершено, система стабільна.

## Active branches

- meta: main (v3.4 з PATH binary shim, WARM обновлено)
- kit: main (legacy chkp.sh залишається для reference)
- Усі 9 проектів на main, синхронізовані з GitHub
- Remote dev: Pi5 через Tailscale + Termius

## Open questions

- Чи потреба зберігати chkp.sh у meta для документації або це технічний борг?
- Чи є інші legacy скрипти в workspace що потребують cleanup?
- Чи синхронізовані .gitignore файли в усіх проектах під один стандарт?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи, використовувати для тестування нових фіч в реальних умовах.
- chkp v3.4 (PATH binary) — задокументувати у notes/ для майбутніх розробників (як вибір між alias vs binary).
- Розглянути systemd service для auto-update BACKLOG assistant через timer (периодичний `chkp meta --backlog-only`).
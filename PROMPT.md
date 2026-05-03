Проект: meta

Поточний стан: chkp v3.4 — PATH binary shim замість bash v1. Усі звернення (PuTTY, CC, cron) тепер йдуть на v3.4, узгодженість версій. Виявлено SESSION.md у git (артефакт v1). Backlog assistant read-only (AI спостереження, ручне редагування).

Наступний крок: видалити legacy скрипти (kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh, meta/chkp.py.bak), SESSION.md з meta repo, додати SESSION.md в .gitignore, перевірити .gitignore у всіх проектах.

Блокерів немає. Система стабільна.

**Перед роботою: `cat meta/HOT.md meta/WARM.md` для актуального контексту.**
---
project: meta
updated: 2026-04-23
---

# HOT — meta

## Now

Архітектурна міграція завершена. Meta-репо містить chkp, BACKLOG, notes, scripts. Kit тепер лише dev-агент. Workspace/.env створено як fallback (ключ з kit). HOT всіх 6 проектів оновлено.

## Last done

**2026-04-23** — Створено meta-репо, перенесено chkp з kit/, BACKLOG з кореня, написано README, оновлено HOT всіх 6 проектів, workspace/.env створено як fallback (ключ з kit).

## Next

1. Почистити дублікати .env по 9 проектах (видалити локальні копії, залишити лише workspace-level).
2. Додати ROADMAP/IDEAS при потребі.
3. Першою робочою сесією заповнити WARM.md реальною архітектурою.

## Blockers

Немає.

## Active branches

- **meta-репо** (`main`): Міграція завершена, ready for cleanup.
- **9 проектів**: Синхронізовані HOT файли, дублікати .env очікують видалення.

## Open questions

- Які саме дублікати .env знайдені? Список проектів для cleanup?
- ROADMAP — потребу визначити з тестуванням.

## Reminders

- Workspace: `/home/sashok/.openclaw/workspace/meta/`
- API keys маскувати до останніх 4 символів
- Checkpoint: `chkp meta "що зробили" "наступний крок" "контекст"`
- Перед тестуванням — `journalctl -u meta -f`
- Rule Zero: запитати HOT+WARM перед відповіддю про стан проекту
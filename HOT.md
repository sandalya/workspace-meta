---
project: meta
updated: 2026-05-03
---

# HOT — meta

## Now

Memory auto-fetch активовано для публічних репо (sam, ed, workspace-meta). Правило #21 в синтез-пам'яті оновлено. Підтверджено web_fetch доступність HOT.md на raw.githubusercontent.com для всіх трьох. Гібридний режим читання: публічні репо fetch автоматом, приватні (insilver-v3, abby-v2, garcia, household_agent, kit) — cat HOT.md WARM.md як раніше. kit ще не мігрований на нову пам'ять.

## Last done

**2026-05-03** — memory auto-fetch для публічних репо (25 хв):

- **Активовано memory rule #21** — публічні репо (sam, ed, workspace-meta) читаються через `web_fetch` на raw.githubusercontent.com/openclaw-ai/..../main/HOT.md.
- **Верифікація доступності** — усі три репо дозволяють public read HOT.md без auth.
- **Гібридний режим** — приватні репо (insilver-v3, abby-v2, garcia, household_agent, kit) залишаються на ручному `cat HOT.md WARM.md` як інструкції.
- **kit: старі файли** — kit ще не мігрований на нову пам'ять, лишається на legacy инструкциях.
- **MEMORY.md оновлено** — додано примітку про web_fetch для публічних репо.

## Next

1. **sam: перезапустити sam.service та відновити 2 зламаних notebook'ів** — UUID 0daaf506 (rag_retrieval-1), UUID 2d0285dd (system_operations-5). Види: `systemctl restart sam.service`, потім дебаг у notebooks.
2. **kit: міграція на нову пам'ять** — дати kit інструкцію для ініціалізації HOT/WARM/COLD структури (ймовірно через `chkp kit --init`).
3. **Решта приватних репо** — перевірити чи todas (insilver-v3, abby-v2, garcia, household_agent) готові до web_fetch або залишаються на ручному read.
4. **Документувати правило #21** — написати у notes/ як публічні та приватні репо читаються по-різному в multi-project setup.

## Blockers

Немає. Публічні репо готові. sam потребує restart + notebook recovery (очікується на черзі).

## Active branches

- meta: main (memory rule #21 додано, гібридний режим задокументовано)
- sam: main (потребує restart sam.service + notebook recovery)
- ed: main (public, у web_fetch chain)
- workspace-meta: main (public, у web_fetch chain)
- insilver-v3, abby-v2, garcia, household_agent, kit: main (приватні, ручна читання на разі)
- Усі на основних гілках, синхронізовані з GitHub

## Open questions

- Чи всі публічні репо мають raw.githubusercontent.com доступ без rate-limit проблем?
- Чи потреба кешування HOT.md локально для offline режиму?
- Чи додавати інші публічні репо (ed, workspace-meta) до повної web_fetch стратегії або вибірково?
- kit: чи мігрувати на HOT/WARM/COLD структуру разом з web_fetch або залишити на ручному режимі як агент?
- Чи вмонтовувати правило #21 у claude.ai як instruction чи тримати у MEMORY.md?

## Reminders

- tmux на Pi5 теряється при reboot — TODO: написати `tmux-restore.sh` за вікна (2026-05-06).
- Termius + Tailscale — стабільна база для дорожної роботи.
- chkp v3.4 (PATH binary) — перевірка на не-meta проектах, видалення legacy скрипів очікується (2026-05-04).
- sam.service restart — важливо на черзі (зламані notebooks 0daaf506, 2d0285dd).
- kit migration — коли буде час, дати інструкцію для HOT/WARM/COLD переходу.

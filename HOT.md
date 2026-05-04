---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

Caching investigation closed: prompt caching несумісний з chkp архітектурою через волатильний WARM (Haiku сам перезаписує його щоразу). Smoke 1+2 показали cache_w=14k але cache_r=0 — Haiku змінював WARM між викликами. Мінімум cacheable block 1024 tokens; SYSTEM+MEMORY<1024. Beta header застарів. Рішення: відмовитись від prompt caching, прийняти chkp 30-90s як норму. BACKLOG +1 P3 пункт про майбутні підходи (WARM diff-mode, COLD frozen split, output streaming). Завтра: external_stop zombie fix у sam (P3, 15 хв), потім вибір Sprint C voice extraction або Sprint D Sam evals.

## Last done

**2026-05-04-05** — Caching investigation + cleanup цикл (~4 год):

- **Prompt caching baseline smoke test 1+2:** Запустив claude.ai з prompt caching instructions, перевірив response_metadata. Результат: cache_creation_input_tokens=14,547 на першому виклику, cache_read_input_tokens=0 на другому. Причина: Haiku у update_backlog() перезаписує WARM щоразу → контент змінюється → cache miss. Мінімальна cacheable одиниця в claude.ai — 1024 tokens (документовано у claude.ai debug). SYSTEM (577 tokens) + MEMORY (393 tokens) = 970 < 1024. HOT (1031) на межі. COLD (6114) append-only, потенційно cacheable. Beta header `prompt-caching-2024-07-31` актуальний у claude.yaml, але cache miss на динамічному контенті. Висновок: caching непрактичний для chkp до поки HОТ/WARM волатильні.

- **Сценарій 2 — COLD-only cache:** Спробував замерзити COLD (append-only) як cacheable basis, HОТ/WARM як prompt-in. Результат: cache_w=14k, але cache_r=0, бо WARM змінювався. CC (Claude Coder) реалізував cache_control PR, але stash повернув все на місце — meta/chkp/chkp.py не змінений. Рішення: закрити caching як P2 задачу, нема ROI без архітектурної переробки (diff-mode для WARM, frozen split для COLD, streaming output).

- **BACKLOG актуалізація:** Додано +1 P3 пункт для майбутніх підходів до caching (WARM diff-mode, COLD frozen, output streaming). Беклог стиснувся до ~6 P3 пунктів.

- **Disk cleanup P3 пункти (попередня сесія):** household_agent (551M economy), insilver-v3 tag cleanup (завершено).

## Next

1. **Tomorrow morning — external_stop zombie fix** (~15 хв, P3):
   - Sam pending external_stop call мертва (zombie process)
   - CC інформував про проблему
   - Запуск: `systemctl restart sam.service`, перевірка лог

2. **Post-fix вибір Sprint** (~2-3 год):
   - **Sprint C:** Voice extraction Влада (синтез мовних даних, ~2h)
   - **Sprint D:** Sam evals + agentic ingest (~3h, потребує свіжого мозку)
   - Вибір залежить від енергії после zombie fix

3. **Opional:** Cheat-sheet Linux/bash блок 2 (grep як точка тертя, ~1h)

## Blockers

Немає активних блокерів. Zombie процес known, scheduled на ранок.

## Active branches

- meta: main (v3.4 stable, caching closed, готово до Sprint C/D)
- sam: main (external_stop zombie pending на завтра ранок)
- garcia, abby-v2, ed, insilver-v3: main (завершено S.A. верифікацію)

## Open questions

- Чи cache_creation_input_tokens показується в claude.ai response або тільки при API inspect? (відповідь: response_metadata в claude.ai при інтернет-з'єднанні)
- Чи COLD-only cache варто повертати у Sprint B/C після архітектурної переробки?
- Zombie external_stop — локальна проблема Sam або cross-project issue?

## Reminders

- Сесія 04.05 закрита: 4 спринти + caching investigation + 3 P3 cleanup. Sasha бойовий до самого кінця.
- Kit міграція на HOT/WARM/COLD структуру — коли буде час
- tmux-restore.sh на Pi5 — TODO 2026-05-06
- Caching архітектура (WARM diff-mode, COLD frozen) — зберігти на Sprint B/C

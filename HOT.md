---
project: meta
updated: 2026-05-04
---

# HOT — meta

## Now

Smoke test 1: prompt caching baseline setup. Перевіряю cache_creation_input_tokens > 0 на першому виклику. Sprint A+B+UI fix завершено, інфра v3.4 стабільна. Беклог очищено. Активна послідовність: abby-v1 видалення → PATH binary перевірка на не-meta → legacy скрипти видалення → Sam NBLM Інтервенція 1.

## Last done

**2026-05-04** — BACKLOG cleanup tail + Sprint A completion (~2.5 год):

- **BACKLOG cleanup #2:** Видалено NBLM-05-02 (28 рядків, застарі), реорганізовано Sam NBLM як 5 Інтервенцій. Пункти 1-5 верифіковані (chkp max_tokens=2000, xclip DISPLAY guard на SSH, abby-v1 на видалення). Лишилось 11 пунктів.
- **Уроки беклог-страйку:** --backlog-strike FRAGMENT повинен бути дослівним match у BACKLOG. При неточному фрагменті chkp не знаходить рядок на видалення.
- **Sprint A status:** Завершено за один SSH-крок. Активна послідовність на черзі.

## Next

1. **Prompt caching smoke test** (~15 хв) — Запустити перший claude.ai запит з prompt caching instructions, перевірити cache_creation_input_tokens > 0 у response_metadata. Документувати результат у notes/PROMPT-CACHING.md.

2. **abby-v1 GitHub repo deletion** (~5 хв) — Settings → Danger Zone, ввести `sandalya/abby-v1`, confirm. Перевірити локальний бекап.

3. **PATH binary verification на не-meta** (~20 хв) — garcia, abby-v2, ed: `chkp --help` → v3.4, потім cross-project `cd ed && chkp garcia` → перевірити guard поведінку.

4. **Legacy скрипти видалення** (~10 хв) — kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh (окрім chkp.py.bak).

5. **Sam NBLM Інтервенція 1** (~30 хв) — dangling UUID detection, `probe source list -n --json`, restart sam.service.

## Blockers

Немає. Prompt caching — виключно інформаційна перевірка, не блокує інші пункти.

## Active branches

- meta: main (v3.4 PATH stable, готово до P2 + caching baseline)
- insilver-v3-dev: dev (pre-push patterns актуалізовані)
- sam: main (очікує Inter 1)
- abby-v1: main (на видалення)
- ed, garcia, abby-v2: main (чекають PATH binary верифікації)

## Open questions

- Чи prompt caching потребує окремої YAML конфіги у claude.yaml чи інструкції в prompt'і достатньо?
- Чи cache_creation_input_tokens показується в усіх API responses чи тільки при дебаг=true?
- Видалити abby-v1 локальний checkout вручну чи скриптом?
- Чи потреба post-cache метрик (cache_read, cache_creation для повторних викликів)?

## Reminders

- Prompt caching baseline документувати у notes/PROMPT-CACHING.md
- tmux на Pi5 теряється при reboot — TODO: `tmux-restore.sh` (2026-05-06)
- kit міграція на HOT/WARM/COLD — коли буде час
- .env дублікати у проектах — перевірити після PATH binary cleanup

# Workspace: openclaw multi-bot infrastructure

## Огляд
Це monorepo з кількома AI-powered Telegram-ботами що крутяться на Raspberry Pi 5.
BASE_DIR кожного проекту: `/home/sashok/.openclaw/workspace/<project>/`

## Активні проекти
- **abby-v2/** — design assistant для Ksyusha (UI/UX). Production. `abby-v2.service`.
- **household_agent/** — family household bot (shopping, kitchen, freezer, metro/zakaz.ua).
- **sam/** — AI assistant з curriculum + NotebookLM. Tripartite memory done.
- **insilver-v3/** — jewelry store consultant. Tripartite memory done. v4 у підготовці.
- **ed/** — QA test runner для всіх ботів.
- **garcia/** — TBD.

## Алясі імен проектів
Маппінг прізвиськ та альтернативних назв на директорії:
- **Meg / Меггі / меггі / Мег** → `household_agent/`
- **Самуель / Сем** → `sam/`
- **Еббі / Abby** → `abby-v2/` (production), `abby/` (legacy, не чіпати)
- **Інсілвер / Insilver** → `insilver-v3/`
- **Едік / Ed** → `ed/`
- **Гарсія / Garcia** → `garcia/`

## Legacy (НЕ чіпати без явного запиту)
- **abby/** + `abby.service` — стара версія, замінена на abby-v2.

## Архітектурні патерни (спільні для всіх ботів)
- venv per project: `<project>/venv/`. Активація: `source venv/bin/activate`.
- systemd для всіх сервісів. Рестарт: `sudo systemctl restart <name>.service`.
- JSON файли замість DB. Зберігання: `<project>/data/`.
- BASE_DIR через `Path(__file__).parent.parent` (не hardcode).
- Lock files для duplicate process protection.
- `cache_control: ephemeral` на system prompts (token economy).

## Спільна інфраструктура
- **shared/** — модулі що використовуються кількома ботами. **ФАЗА РЕДУКЦІЇ** — НЕ пропонувати move to shared/ без явного запиту.
- **meta/** — мета-workspace: chkp, нотатки, документація крос-проектних ініціатив.
- **meta/chkp/chkp.py** — alias `chkp`. Backward-compat alias `chkp3`. Haiku 4.5 default, Sonnet fallback.

## chkp ритуал (КРИТИЧНО)
Команда `chkp [project] "зроблено" "далі" "контекст"`:
1. Оновлює HOT/WARM/COLD memory у проекті
2. `git add -A` (ВЕСЬ workspace)
3. `git commit --no-verify`
4. `git push`
5. Регенерує PROMPT.md

**НЕ робити окремий `git push` перед chkp** — це ламає sync між commit і memory.

## Tripartite memory система
Файлова структура для проектів зі статусом "done" або "ініціалізована": Sam, InSilver-v3, Meg.
- `<project>/meta/HOT.md` — поточні активні справи (топ контексту)
- `<project>/meta/WARM.md` — недавні рішення, що ще пам'ятаємо
- `<project>/meta/COLD.md` — архів, історія, рідко потрібне
- `<project>/PROMPT.md` — згенерований агрегат для системного промпта

Meg: ініціалізована 2026-04-23 (HOT stub, WARM/COLD заповнені, наповнення HOT на наступному chkp).

Pending міграція: Ed, Garcia, Abby-v2.

При старті сесії з проектом що має tripartite — починати з читання `HOT.md` + `WARM.md`.

## File operations: правила
- Малі патчі (<20 рядків) → `sed`.
- Середні (20-200) → `cat > /tmp/patch.py << 'PYEOF'` + `python3`.
- Великі (>200) → cat-heredoc у блоках.
- Triple-quoted strings у патч-скриптах: `\n` пиши як `\\n` всередині `'''...'''` (інакше SyntaxError).
- НІКОЛИ: `nano` на `.md`, `scp`, `base64`, WinSCP.

## Search правила
- ЗАВЖДИ виключати venv: `--exclude-dir=venv` або `rg`.
- Default search tool — `rg` (ripgrep).

## Backlog
Source of truth: `/home/sashok/.openclaw/workspace/meta/BACKLOG.md`.
Не дублювати його контент в інших місцях.

**КРИТИЧНО — формат BACKLOG.md (append-only, з історією):**
- Активний пункт: `## Title` або `### Title` БЕЗ обгортки тильдами.
- Закритий пункт: `~~## Title~~` або `~~### Title~~` — обгорнутий у markdown strikethrough. Закриті лишаються в файлі як історичний контекст, **НЕ видаляються**.
- Коли тебе просять "summarize / show active items / що в backlog" — повертай **ТІЛЬКИ** заголовки без `~~`.
- Перевірка перед тим як включити пункт у відповідь: чи починається рядок заголовка з `~~`? Якщо так — це CLOSED, пропусти.
- Якщо не впевнений у статусі пункту — НЕ домислюй, перепитай користувача або процитуй точний рядок заголовка з тильдами як є.
- Цей баг вже траплявся (2026-05-06): Claude резюмував закреслені пункти як активні TODO. Не повторюй.

## Git workflow
- Один спільний repo для всього workspace.
- Коміти переважно через chkp.
- `git status` перед серйозними змінами — нормально.
- `--no-verify` використовується chkp'ом свідомо (pre-commit hooks обходяться).

## Поточні приорітети (Q2 2026)
1. **Tripartite memory міграція**: Ed, Garcia, Abby-v2.
2. **Abby-v2**: image gen на Gemini Flash Image (`gemini-3.1-flash-image-preview`, `core/image_gen.py`); humanize pipeline (`core/humanize.py` + `core/ai_score.py` через Sightengine).
3. **Meg (household_agent) Phase 5**: zakaz.ua/metro API — order history, shopping list priority logic, cart item comments для weighted products.
4. **InSilver-v4 prep**: оновити implementation guide v003 → v004.


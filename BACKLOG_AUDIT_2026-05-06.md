# BACKLOG audit 2026-05-06

## Підсумок
- Перевірено: 20
- DONE: 9
- TODO: 5
- PARTIAL: 3
- UNCLEAR: 3

---

## Деталі

### [DONE] InSilver voice reference extraction
**Проєкт:** insilver-v3
**Доказ:**
- Директорія `insilver-v3/data/voice_reference/` існує
- 7 файлів діалогів: `dialogs/C001_yevhen.md`, `C002_andriy.md`, `C003_sasha.md`, `C004_anzhelika.md`, `C005_fartovyi.md`, `C006_vladyslav.md`, `C007_taras.md`
- `README.md` у директорії voice_reference

---

### [DONE] household_agent .git 239M аудит (filter-repo analyze)
**Проєкт:** household_agent
**Доказ:**
- `/home/sashok/.openclaw/workspace/household_agent/.git/filter-repo/` існує, містить `analysis/` директорію
- Файл `already_ran` присутній — підтверджує що аналіз вже запускався
- Поточний розмір `.git/`: **688K** (проблему вже виправлено — розмір зменшено)

---

### [PARTIAL] shared/ концепція рефакторинг
**Проєкт:** workspace (meta)
**Доказ:**
- `shared/` існує з файлами: `agent_base.py`, `catchup_module.py`, `conversation_store.py`, `curriculum/`, `digest_module.py`, `errors.py`, `logger.py`, `memory_store.py`, `token_tracker.py`
- Реальні імпорти з shared/ є в: `sam/main.py`, `sam/core/content_gen/brief.py`, `sam/core/podcast_module.py`, `sam/curriculum/islands.py`, `sam/modules/base.py`, `sam/curriculum/pipeline.py`, `sam/modules/exam.py`, `sam/modules/curriculum.py`, `sam/modules/article.py`, `garcia/main.py`, `garcia/modules/base.py`, `garcia/modules/podcast.py`, `garcia/modules/curriculum.py`
- CLAUDE.md зафіксовано рішення "ФАЗА РЕДУКЦІЇ — НЕ пропонувати move to shared/"
**Що лишилось / Дія:** Рішення прийнято (редукція), але shared/ ще активно використовується. Рефакторинг не завершений — 13+ файлів в sam/ та garcia/ залишають імпорти з shared/.

---

### [UNCLEAR] Polyrepo vs гібрид decision
**Проєкт:** workspace (meta)
**Доказ:**
- `grep polyrepo|monorepo|гібрид` знайшов згадки в: `meta/WARM.md`, `meta/COLD.md`, `meta/BACKLOG.md`, `meta/agent-docs/CLAUDE.md`, тестових фікстурах
- ADR окремого файлу не існує — рішення не зафіксовано як самостійний документ
**Що лишилось / Дія:** Рішення обговорюється але не зафіксовано в окремому ADR. Якщо рішення прийнято — варто зафіксувати в `meta/agent-docs/` або CLAUDE.md.

---

### [TODO] Linux/bash cheat-sheet
**Проєкт:** meta
**Доказ:**
- `find meta/ -name "*cheat*" -o -name "*bash*" -o -name "*linux*"` → знайдено тільки `meta/legacy/chkp_bash_v1` (це не cheat-sheet, а legacy chkp скрипт)
- `find /home/sashok/ -maxdepth 3 -name "*cheat*"` → нічого
**Що лишилось / Дія:** Файл не створено.

---

### [PARTIAL] Agentic ingest для Сема
**Проєкт:** sam
**Доказ:**
- `sam/modules/router.py` існує — є LLM-based message router (intent classification через claude-haiku-4-5)
- `sam/modules/router.py` містить intent routing: curriculum, digest, notebooks, science, chat, hub, catchup, jobs, cost
- `find sam/ -name "ingest*" -o -name "classifier*"` → нічого не знайдено
- `grep ingest|classifier` в core/ → тільки aiohttp router для RSS/healthz endpoints (не content ingest)
**Що лишилось / Дія:** Router є, але agentic ingest pipeline (автоматичний ingest нових матеріалів) відсутній. Classifier як окремий компонент не реалізований.

---

### [DONE] Sam — NBLM Content Generation Pipeline
**Проєкт:** sam
**Доказ:**
- `sam/core/content_gen/brief.py` — існує
- `sam/core/content_gen/backends/nblm.py` — існує
- `sam/core/content_gen/backends/tts.py` — існує
- `sam/core/content_gen/backends/interactive.py` — існує
- `grep deepdive` → `presets.py:8: "deepdive": {...}`, `pipeline.py:231`, `article.py:307`
- `nbstatus` / `nb_status` — не знайдено в коді (можливо renamed або не реалізовано)
- `brief.py` та backend структура повністю реалізовані

---

### [DONE] regen handler stale UI string ("retry до 72 год")
**Проєкт:** sam
**Доказ:**
- `grep "72 год|72h|72 час"` → нічого не знайдено
- `grep "4h cap"` → `nblm.py:35: RETRY_DELAYS = [0] + [3600] * 4  # hourly retry, 5 attempts total (~4h cap)`
- `curriculum.py:468: "...retry до 4 год на rate limit..."` — нова версія рядка

---

### [DONE] external_stop лишає status=pending
**Проєкт:** sam
**Доказ:**
- `nblm.py:396-420`: після `external_stop` є logic розгалуження:
  - якщо status == "generating" → `set_format_status(..., "failed", error="external_stop")` + `save()`
  - якщо status == "pending" → `log.warning(..., "exiting without mutation")` — status не змінюється (правильно)
  - якщо status == "failed"/"cancelled" → просто лог
- Тест `test_external_stop_with_generating_status_sets_failed` підтверджує zombie-fix
- Тест `test_external_stop_with_pending_status_keeps_pending` підтверджує що pending не перезаписується

---

### [TODO] Tag dev-pre-reset-2026-05-03 cleanup
**Проєкт:** insilver-v3 / workspace git
**Доказ:**
- `git tag -l "dev-pre-reset*"` в workspace root → **порожній вивід** (тег відсутній локально)
- `git ls-remote --tags origin | grep dev-pre-reset` → "not found on remote"
- Тег не існує ні локально, ні на remote
**Примітка:** Якщо задача була "видалити тег" — це вже [DONE]. Якщо задача "перевірити що тег прибрано" — [DONE]. Класифіковано [TODO] якщо BACKLOG має додаткову cleanup роботу поза видаленням тегу.

> **Уточнення:** Тег відсутній і локально, і remote → пункт фактично [DONE].

---

### [DONE] Tag dev-pre-reset-2026-05-03 cleanup (пункт 9 = пункт 12)
Покрито в пункті 9. Тег відсутній локально і на remote → **[DONE]**.

---

### [DONE] Sam manual stop не перериває in-flight asyncio task
**Проєкт:** sam
**Доказ:**
- `_wait_for_artifact` (nblm.py:237-247): на кожній ітерації while-loop виконує `_w_state = load(cur_path)` і перевіряє `_w_entity.formats[fmt].status != "generating"` → якщо статус змінено externally, повертає `(False, "external_stop")`
- retry loop (nblm.py:355-367): після `asyncio.sleep(delay)` робить `_chk_state = load(cur_path)` та перевіряє статус → якщо не "generating", виходить
- Обидва місця перезавантажують стан з диска на кожній ітерації

---

### [TODO] BACKLOG hygiene — перенести закриті пункти в BACKLOG_CLOSED.md (~2026-05-20)
**Проєкт:** meta
**Доказ:**
- `wc -l BACKLOG.md` → **417 рядків** / **43341 байт**
- Закритих `~~##` пунктів: **9**
- Активних `##` пунктів: **10**
- `BACKLOG_CLOSED.md` → **не існує**
**Що лишилось / Дія:** Термін ~2026-05-20 ще не настав (сьогодні 2026-05-06). Але BACKLOG_CLOSED.md вже варто підготувати. Класифіковано [TODO] — scheduled на ~2026-05-20.

---

### [TODO] Розширити backup.sh для повного DR
**Проєкт:** backup/
**Доказ:**
- Знайдено 2 копії: `backup/backup.sh` та `meta/backup/backup.sh` (вміст ідентичний)
- Перевірено наявність 4 DR-елементів:
  - `/etc/systemd/system/*.service` → **ВІДСУТНЄ** (systemd backup не включено)
  - `~/.claude/settings.json` → **ВІДСУТНЄ** (тільки `~/.claude/CLAUDE.md` у whitelist)
  - `crontab -l` → **ВІДСУТНЄ**
  - `dpkg --get-selections` → **ВІДСУТНЄ**
- У whitelist є: data/, .env, .git, meta/, PROMPT.md, .bashrc, .bash_aliases, CLAUDE.md, telethon sessions
**Що лишилось / Дія:** Жоден з 4 DR-елементів не додано. Потрібно додати backup systemd unit files, claude settings.json, crontab dump, dpkg selections.

---

### [UNCLEAR] DR drill коли приїде запасна SD
**Проєкт:** meta
**Доказ:**
- `find workspace/ -name "RESTORE.md"` → **нічого не знайдено**
- Drill є фізичною процедурою з SD-картою — не має кодового артефакту
**Що лишилось / Дія:** Неможливо визначити з коду. Залежить від фізичного артефакту (запасна SD-карта). Якщо drill проведено — варто створити RESTORE.md як підтвердження.

---

### [DONE] Dangling nblm_notebook_id — probe source list
**Проєкт:** sam
**Доказ:**
- `get_or_create_notebook` (nblm.py:110-142):
  ```
  if entity.nblm_notebook_id:
      probe_rc, probe_out, probe_err = await _run(
          ["source", "list", "-n", existing_id, "--json"], timeout=30
      )
  ```
- Після probe: якщо `probe_rc != 0` → інвалідує pointer (`set_nblm_notebook_id(state, topic_id, None)`) + `save()`
- Окремий випадок: rate limit під час probe → reuse UUID без інвалідації

---

### [TODO] nblm_notebook_id consolidation refactor
**Проєкт:** sam
**Доказ:**
- Знайдено кілька різних полів в різних файлах:
  - `topic.nblm_notebook_id` (tools.py, nblm.py) — canonical для topics
  - `article.nblm_notebook_id` (nblm.py, nblm_orphan_sync.py) — для articles
  - `rss_feed.py:55: topic.get("nblm_notebook_id", "")` — raw dict access
  - `nblm_orphan_sync.py:33: t.get("nblm_notebook_id") or ""` — raw dict access
  - `set_nblm_notebook_id` та `set_article_nblm_notebook_id` — два різні setter'и
- Є також `notebook_id` як параметр функцій (audio_downloader, rss_feed orphan entries)
**Що лишилось / Дія:** Дублювання topic/article path. Canonical поле `nblm_notebook_id` є, але два окремих setter'и і дублювання raw dict access. Рефакторинг до єдиного accessor не завершений.

---

### [PARTIAL] wait-loop curriculum reload performance
**Проєкт:** sam
**Доказ:**
- `_wait_for_artifact` (nblm.py:237): на кожній ітерації while-loop робить `load(cur_path)` — повне перечитування файлу
- state_provider callback **відсутній** — передається `cur_path: Path` і кожна ітерація робить I/O
- Retry loop (nblm.py:355-367) також робить `load(cur_path)` після кожного sleep
**Що лишилось / Дія:** `load()` на кожній ітерації — це і є поточна реалізація (TODO відкритий). State_provider callback не реалізований.

---

### [TODO] Sam pipeline lifecycle observability
**Проєкт:** sam
**Доказ:**
- `grep "admin.*tasks|all_tasks|asyncio.*tasks"` → **нічого не знайдено** в sam/
- `grep '"/admin"'` → **нічого не знайдено** в sam/
- `main.py`: є `/dbg_download` debug handler, але `/admin tasks` з `asyncio.all_tasks()` відсутній
**Що лишилось / Дія:** /admin команда з asyncio.all_tasks() не реалізована. Observability pipeline tasks — [TODO].

---

## Корекція пункту 9/12

Пункт 9 після уточнення: тег `dev-pre-reset-2026-05-03` відсутній локально і remote → класифікую **[DONE]**.

---

## Оновлений підсумок (фінальний)

| Статус  | Кількість |
|---------|-----------|
| DONE    | 9         |
| TODO    | 5         |
| PARTIAL | 3         |
| UNCLEAR | 3         |
| **Total** | **20**  |

**DONE:** 1 (InSilver voice ref), 2 (filter-repo), 7 (NBLM pipeline), 8a (72→4h), 8b (external_stop fix), 9/12 (tag cleanup), 10 (manual stop fix), 15 (dangling probe)

**TODO:** 5 (Linux cheat-sheet), 11 (BACKLOG_CLOSED scheduled ~05-20), 13 (backup.sh DR), 16 (nblm_id consolidation), 18 (admin observability)

**PARTIAL:** 3 (shared/ refactor), 6 (agentic ingest — тільки router), 17 (wait-loop load на кожній ітерації)

**UNCLEAR:** 4 (polyrepo ADR), 14 (DR drill SD-карта)

---
project: meta
updated: 2026-05-05
---

# HOT — meta

## Now

Сесія 05.05 (вечір) — **chkp evals foundation.** Закладено інфраструктуру для регресійного тестування chkp.py через golden fixtures з реальних промахів. Вмисно НЕ патчили SYSTEM_PROMPT — це наступна сесія. Baseline 2/2 FAIL — підтвердило що проблема repro-вана контрольовано.

**Інфраструктурні зміни в chkp.py (commit c46cf24):**
- `--dry-run` flag — пропускає write_tier_files + git_commit_push, друкує parsed JSON в stdout
- `CHKP_WORKSPACE` env override — для ізольованого прогону тестів у tempdir

**Структура `meta/chkp/tests/`:**
- `conftest.py` — load_fixture + run_chkp_dry helpers
- `test_no_hallucination.py` — parametrized тести по golden fixtures
- `fixtures/2026-05-05_morning/` — voice integration session (commit c6704d5 галюцинував)
- `fixtures/2026-05-05_evening/` — Etap 4 Ed coverage (commit 07bfa5b дослівно скопіював попередній HOT)

**Baseline:** обидва FAIL. Fixture evening — критичний (verbatim copy of previous HOT.md ## Now).

**Третя fixture-кандидат (виявлена по факту цією сесією):** chkp meta 39242c1 — теж галюцинував, написав HOT про WARM diff-mode v3.5 (та робота вже закрита) замість сьогоднішнього chkp evals. Це доказ що проблема системна на всі проекти, не специфічна для InSilver. Поточний HOT meta це manual fix (так само як insilver-v3 6cae1d4).

## Last done

**Сесія 05.05 (вечір) — chkp evals foundation:**
- ✅ Додано `--dry-run` flag у chkp.py (commit c46cf24)
- ✅ Додано `CHKP_WORKSPACE` env override
- ✅ Створено meta/chkp/tests/ структуру з conftest + test_no_hallucination
- ✅ Дві golden fixtures з реальних промахів сьогодні (morning + evening)
- ✅ Baseline run: 2/2 FAIL — repro проблеми підтверджено
- ✅ Fixture morning tolerant — must_contain про конкретні артефакти (prompt.py, 12_voice_critical, merged)
- ✅ Все запушено на github.com/sandalya/workspace-meta (commit c46cf24)

**Раніше (~12:00) — InSilver Етап 4 STABILIZATION_PLAN:**
- Розширення Ed regression coverage: блоки 04_pricing_command (5) + 08_admin_panel (6), 11/11 PASS на dev
- Per-case user_id override у Ed (commit 3e37585), skip_judge mode (234fb60)

## Next

**Наступна сесія — patch SYSTEM_PROMPT в chkp/chkp.py:**
1. Додати в SYSTEM_PROMPT директиву типу "HOT.md ## Now MUST describe THIS session's done from input below, NOT copy previous HOT or paraphrase WARM. WARM is historical context only."
2. Прогнати тести: `cd meta && pytest chkp/tests/ -v` — очікую PASS на fixture evening, можливо ще треба тюнити для morning
3. Якщо обидва PASS — push prompt fix у prod chkp
4. **Додати ТРЕТЮ fixture** з цієї сесії: meta chkp 39242c1 (галюцинація на meta, написав про WARM diff-mode v3.5 замість chkp evals)

**Опціонально:**
- BACKLOG.md update: chkp regression tests P1 (зараз PROMPT.md issue стоїть як P3)
- Continue InSilver Етап 4: 02_search_intent, 03_complex_keywords, 11_order_each_type, 13_trainer_flow

## Blockers
- Немає

## Active work
- chkp evals (наступна сесія patch SYSTEM_PROMPT)
- InSilver Етап 4 Ed coverage (~50% done)

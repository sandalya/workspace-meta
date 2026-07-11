# BACKLOG

---

## Polyrepo vs гібрид decision

Після security cleanup workspace 29.04 структура: 9 окремих repos на GitHub + meta-репо + root уже не git. Потрібно вирішити чи залишити polyrepo або зробити гібрид (monorepo або submodules). Abby/Garcia ділять стиль/інфраструктуру, Sam/Insilver стоять окремо. Пріоритет: низький.

## Linux/bash cheat-sheet під мою інфру (2026-04-30)

Персоналізований cheat-sheet під Beelink SER5 ecosystem (sam, abby-v2, ed, household_agent, systemd, NBLM CLI). ~20 базових команд щоб впевнено читати CC bash-команди і розуміти "це безпечно / це чіпає продакшн": ls, cd, cat, cp, mv, rm, grep, find, chmod, systemctl, journalctl, git status/diff/log, sudo, pipes (|), redirects (> >>), heredoc. Пріоритет: середній.

## Agentic ingest для Сема (2026-04-30)

Сем приймає довільний матеріал (URL, текст, скрін, PDF, голосове) з мінімальним описом, сам розуміє контекст, класифікує, додає в курікулум у правильний острів/тему/доповнення. Фундаментальна зміна: content delivery system → personal knowledge OS.

Послідовність: evals infra (LLM-as-a-judge, базова інфра в `sam/evals/`, baseline 20 прикладів topic_classification) → agentic ingest (classifier, router, safeguards, rollback). Архітектурний дизайн ~2-3h окремою сесією в Claude.ai. Пріоритет: високий, але не починати без evals infra.

- [ ] Sam: /nbstatus — звіт які теми мають NbLM контент по форматах

## Sam — NBLM tech debt (2026-05-03)

16 з 18 podcast-ів ready. 2 теми застрягли (`rag_retrieval-1`, `system_operations-5`). Стратегія: точкові інтервенції → big refactor як окремий план. Ed-suite на NBLM happy path + rc=1 path між інтервенціями.

### TODO

#### 5. nblm_notebook_id consolidation refactor (P3)

Mapping тема→notebook живе в трьох місцях паралельно (`nblm_notebook_id`, `notebook_id`, `formats.video.url`, `formats.podcast_nblm.notebook_id`). Джерело дублів в NBLM UI ("🏆 LLM Evaluation Tools" ×3 тощо) та reuse-багів.

Фікс: одне canonical поле `topics[].nblm_notebook_id`, всі інші deprecated через shim. Schema migration з backward-compat. Розмір: 1 повна сесія + ~1 сесія тестів.

#### 6. wait-loop curriculum reload performance (P3)

`_wait_for_artifact` робить `load(cur_path)` на кожній ітерації while-loop (~30 хв). При scaling до 20 паралельних generations — постійні disk-read'и. Фікс: `state_provider` callback що шарить cached state між паралельними wait-loop'ами. ~1 година.

#### 7. Sam pipeline lifecycle observability (P3)

`status` у curriculum.json не показує стан in-flight asyncio task'ів; немає способу подивитись без grep по journalctl. Ідея: `/admin tasks` — `asyncio.all_tasks()` з name/stage/час від старту/кнопка cancel. ~1.5 години.

## Workspace infrastructure

- (P2) Додати `EnvironmentFile=/home/sashok/.openclaw/workspace/ed/.env` в `ed-bot.service` (той самий баг як був у abby/household)
- (P3) Додати (Pn) маркери до пунктів без пріоритету в BACKLOG — зараз кілька uncategorized

## drone-recon

Проект: meta

Постмортем чekпointu/BACKLOG: виявили system gap — AI чаті не звіряє 'що зробили' з активними пунктами BACKLOG перед chkp, тому --backlog-strike флаги просто не передаються (доказ: 0674dd4 household_agent 11 днів без strike). Дизайн brief готовий: suggest_backlog_strikes() з другим Haiku call, UX y/n/edit/skip, --no-backlog-suggest opt-out. 8 pytest fixture'и написано.

Чиній: скинути код + тести (est. 2-3h) для CC implementation, потім smoke test на реальній сесії що закриває пункт, rollout на 6 проектів.

Перш ніж почати кодити — поділися HOT.md + WARM.md (Rule Zero) для контексту.
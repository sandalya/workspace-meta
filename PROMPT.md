Проект: meta

Стан: chkp v3.1 вже готово з backlog integration (update_backlog, commit_backlog функції, інтерактивний y/n/e/s, per-project commits). Попереднє тестування з mock'ами пройшло успішно.

Что робити: Протестувати на реальному виклику — запустити `chkp <project> "..." "наступний крок" "..."` на якомусь реальному проекті (abby, garcia, household_agent), спостерігати AI-пропозицію, інтерактивний цикл, комміт у meta. Якщо працює — документувати workflow, додати --no-commit прапорець, розглянути systemd timer для периодичного refresh'у.

Блокери: немає.

Погодися з HOT.md + WARM.md з `/home/sashok/.openclaw/workspace/meta/` перед стартом.
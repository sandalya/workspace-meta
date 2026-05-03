Проект: meta

Стан: chkp v3.4 PATH binary стабілізовано на meta. SESSION.md видалено. Legacy скрипти в legacy/. Готово до перевірки на не-meta проектах (sam, garcia, insilver, abby) — чи commit_backlog коректно робить окремий коміт у meta repo.

Далі:
1. Протестувати `chkp <не-meta-проект>` на реальному проекті.
2. Видалити legacy скрипти (kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh) якщо v3.4 працює.
3. Синхронізувати .gitignore у всіх проектах.

Бекап: чkp.py.bak залишений у chkp/ — git історія має все.

Шелфіть HOT.md + WARM.md на старті сесії.
Проект: meta

Стан: Цикл дрібниць беклогу завершено (5 з 5 пунктів за 60 хв), включаючи рефакторинг chkp guard для крос-проектного workflow без false positives. Готово до P2 (Sam NBLM dangling UUID).

Что робити:
1. Sam NBLM Інтервенція 1 (30 хв) — dangling UUID detection у get_or_create_notebook, restart sam.service.
2. Перевірити PATH binary на не-meta проектах (15 хв).
3. Видалити legacy скрипти (kit/chkp.sh, kit/chkp2.sh, meta/chkp.sh).

Блокери: Немає.

Погляд HOT.md + WARM.md перед роботою.
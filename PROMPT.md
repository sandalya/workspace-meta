Проект: meta

Стан: Sprint A завершено (chkp v3.4 PATH binary стабільний, max_tokens=2000 верифіковано, xclip guard готовий, abby-v1 GitHub видалено). Беклог 11/16 пунктів. Готово до P2.

Чергові кроки:
1. PATH binary верифікація на не-meta проектах (garcia, abby-v2, ed) — `chkp --help` має показувати v3.4
2. Legacy скрипти видалення (kit/chkp.sh, kit/chkp2.sh) — коли верифікація OK
3. Sam NBLM Інтервенція 1 (dangling UUID detection у nblm.py, метод get_or_create_notebook)

Блокери: Немає.

Українською: поділись HOT.md + WARM.md (це базова інформація для наступної Claude-сесії). Запит: які кроки зробити спочатку — PATH binary перевірка або legacy cleanup?
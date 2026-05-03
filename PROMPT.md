Проект: meta

Стан: чkp v3.4 PATH binary шим стабілізований і протестований на meta (все робить через ~/.local/bin). Завершено дрібниці цикл (pre-push patterns, guard рефакторинг, PROMPT.md flow, xclip guard для SSH без X11). Legacy bash скрипти v1 архівовано. Готово до P2.

Что робити:
1. **Sam NBLM Інтервенція 1** (~30 хв) — dangling UUID detection у `sam/core/content_gen/backends/nblm.py` get_or_create_notebook. Probe source list перед reuse, інвалідувати nblm_notebook_id якщо fail/null, fallthrough на create. Разблокує rag_retrieval-1.
2. Перевірити PATH binary на не-meta проектах (garcia, abby-v2, ed), видалити legacy скрипти після підтвердження.
3. Синхронізувати .gitignore (SESSION.md, legacy/ шляхи).

Блокери: немає.

Повернись до HOT.md + WARM.md для деталей. Посилання на BACKLOG для priority матриці.

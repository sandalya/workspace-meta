Проект: meta

Стан: Завершено Sprint A (chkp v3.4 PATH binary, max_tokens=2000, xclip guard, BACKLOG cleanup, abby-v1 GitHub deletion). Prompt caching baseline setup готово. Беклог 11/16 пунктів активних. Потреба: PATH binary верифікація на не-meta проектах (garcia, abby-v2, ed), legacy скрипти видалення, Sam NBLM Інтервенція 1 (dangling UUID detection).

Што робити: 1) Запустити `chkp --help` на garcia, abby-v2, ed → перевірити v3.4 у output. 2) Cross-project тест (cd ed && chkp garcia) → guard мовчазна. 3) Видалити kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh. 4) На наступну claude-сесію (для sam/garcia/etc) — запустити перший claude.ai запит з prompt caching instructions, перевірити cache_creation_input_tokens > 0, документувати у notes/PROMPT-CACHING.md. 5) Sam NBLM Inter 1: файл sam/core/content_gen/backends/nblm.py, метод get_or_create_notebook, додати UUID validation, restart sam.service.

Блокери: немає. Усі пункти паралелізуються.

Документи: cat /home/sashok/.openclaw/workspace/meta/HOT.md /home/sashok/.openclaw/workspace/meta/WARM.md (Rule Zero перед початком).
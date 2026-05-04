Проект: meta

Стан: BACKLOG cleanup завершено (видалено NBLM-05-02, реорганізовано Sam NBLM як 5 Інтервенцій). PATH binary v3.4 stable на meta, готовий до тестування на non-meta проектах (garcia, abby-v2, ed). Наступні 6 кроків у HOT.md: abby-v1 GitHub deletion, max_tokens fix, xclip validation, PATH на не-meta, видалення legacy, Sam Inter 1 (dangling UUID).

Что робити: 1) abby-v1 Settings→Danger Zone delete; 2) max_tokens=2000 vs 4096 перевірка; 3) xclip на Pi5 SSH без X11; 4) PATH binary тест (garcia, ed); 5) видалення legacy скрипів; 6) Sam restart + Inter 1 (dangling UUID detection).

Блокери: немає критичних. abby-v1 потребує ручної GitHub операції.

📋 Поділися HOT.md + WARM.md перед тим як продовжити.
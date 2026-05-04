Проект: meta

Стан: Sprint A завершено за один SSH-крок (pre-push hook patterns + BACKLOG cleanup #2). Smoke-test 4/4 зелений. BACKLOG очищено й реорганізовано: видалено NBLM-05-02, переведено Sam NBLM в послідовність 5 Інтервенцій, статус 1-5 DONE / 6-16 TODO. chkp v3.4 PATH binary стабільний, готовий до перевірки на не-meta проектах (garcia, abby-v2, ed).

Наступні кроки:
1. abby-v1 GitHub видалення (Settings → Danger Zone) (~5 хв).
2. PATH binary верифікація на не-meta — cross-project workflow (cd ed && chkp garcia) без warning (~20 хв).
3. Legacy скрипти видалення (kit/chkp.sh, kit/chkp2.sh, meta/legacy/chkp_bash_v1/chkp.sh) після підтвердження v3.4 (~10 хв).
4. Sam NBLM Інтервенція 1 — dangling UUID detection в nblm.py (30 хв).

Блокери: abby-v1 потребує ручної GitHub операції, інші локальні.

Прошу: 1) Поділися HOT.md + WARM.md з meta репозиторію, 2) Поточний статус meta/.git/hooks/pre-push, 3) Чи є локальний backup abby-v1 перед GitHub deletion?
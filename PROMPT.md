Проект: meta

Стан: Sprint A завершено (chkp v3.4 PATH stable, BACKLOG cleanup #2). Тепер smoke test 1: prompt caching baseline на claude.ai. Перевіряю cache_creation_input_tokens > 0.

Що робити далі:
1. Перевірити результат caching (cache_creation_input_tokens у response metadata).
2. Якщо OK — abby-v1 видалення, PATH binary на не-meta, legacy скрипти видалення.
3. Якщо fail — debug claude.yaml rule #42 або claude.ai API settings.
4. Sam NBLM Inter 1 (dangling UUID) на черзі після.

Блокери: немає. Поділитись HOT.md + WARM.md перед стартом нової сесії.

Сеcія: smoke-test + sprint B prep (caching + quick fixes).
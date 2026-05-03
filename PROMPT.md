Проект: meta

Стан: Memory auto-fetch активовано для публічних репо (sam, ed, workspace-meta) через web_fetch на raw.github. Приватні репо (insilver-v3, abby-v2, garcia, household_agent, kit) на ручному читанні. PATH binary для chkp v3.4 стабілізовано і готово до перевірки на не-meta проектах.

Наступні кроки:
1. sam: перезапустити sam.service + відновити 2 зламаних notebooks (rag_retrieval-1 UUID 0daaf506, system_operations-5 UUID 2d0285dd)
2. kit: міграція на HOT/WARM/COLD структуру та гібридний режим пам'яті
3. Документувати rule #21 та гібридний режим у notes/

Блокери: немає.

Прошу: поділитися HOT.md + WARM.md з meta проекту для контексту. Зосередимося на sam restart та notebook recovery, а потім kit міграція.
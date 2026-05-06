Проект: meta

**Поточний стан:** chkp.py BACKLOG валідація live з fuzzy hints, але apply_backlog_flags() має 3 класи багів (silent-skip, multi-match, replace точність). Backup infrastructure автоматизована (PC 14d + Pi 3d rotation), logging security на 2/6 ботів patched (httpx INFO suppression). Strikethrough rule посилено в двох місцях.

**Наступний крок:** написати розширені тести в meta/chkp/tests/ для silent-skip, multi-match, replace(,1), ~~closed~~ strikethrough cases. Потім підтримати replace() логіку за лінійним номером пункта замість простого FRAGMENT match.

**Блокери:** немає.

**Розділити HOT.md + WARM.md на старті сесії.**
---
project: {PROJECT_NAME}
created: {DATE}
---

# COLD — {PROJECT_NAME}

Архів завершених фаз, міграцій, рефакторингів. Append-only: нові записи додаються вниз з датою.

---

## {DATE} — Ініціалізація триярусної пам'яті

Проект переведено на структуру HOT/WARM/COLD/MEMORY. Створено через `chkp3 --init {PROJECT_NAME}`. Rule Zero прийнято. Попередній стан виведено з userMemories Claude + поточної структури проекту.


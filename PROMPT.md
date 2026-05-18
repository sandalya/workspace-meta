Проект: meta

Стан: openclaw-gateway crash loop відключено (user service disabled), Pi5 теплоємність нормалізована з 1.5A→0.6A. Heartbeat відключено 2026-05-17, crash loop відключено 2026-05-18. AWS Console monitoring активний (kit3 витрати очікуються упати).

Что робити далі: (opcional) дослідити коли crash loop стартував (journalctl) і чи потребуємо openclaw-gateway для meta вообще. Якщо не потребуємо — видалити service остаточно. Якщо потребуємо — розглянути upgrade або custom config.

Блокери: немає.

Будь ласка, поділись HOT.md + WARM.md з кількома речами з попередніх сесій для контексту.
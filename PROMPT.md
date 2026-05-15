Проект: meta

Стан: suggest_backlog_strikes() feature implements semantic drift fix у chkp — AI пропонує закрити BACKLOG пункти на основі сесійного контексту. 54/54 unit-тестів PASS, UX блок готовий. httpx suppression live на 2/6 ботів, 4 на черзі. morning_digest timer live 09:00 щодня.

Что робити: smoke test на реальному чекпоінті (переконатись пропозиція з'являється, y коректно страйкує, false positives 0). После — масштабування на інші проекти.

Блокери: None. Потреба: verify household_agent restart після BotFather rotation, httpx suppression на ed/garcia/insilver-v3/sam, BACKLOG rotation policy для abby/sam архівів.

Поділитись HOT.md + WARM.md на старті.
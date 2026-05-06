Проект: meta

Поточний стан: SD карта очищена (78%→60%, 11G вільне), meggi venv перебудована на CPU-only (497M). Виявлена і відновлена теча Telegram токена через httpx логування — потреба: подавити httpx INFO на всіх 6 ботах + DR дриль коли прийде spare SD.

Чтобы продовжити:
1. Переглянути поточну HOT.md + WARM.md: `cat ~/openclaw/workspace/meta/HOT.md ~/openclaw/workspace/meta/WARM.md`
2. Далі за дорученнями в ## Next.

Блокери: щодини. Наступна фаза: logging security compliance (httpx), DR drill, backup.sh extension.
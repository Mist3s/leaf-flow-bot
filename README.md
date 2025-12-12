# LeafFlow Telegram Bot

Телеграм-бот и HTTP веб-приложение на FastAPI, которое расширяет LeafFlow API и WebApp.

## Стек
- FastAPI — HTTP вебхуки
- aiogram 3 — обработка апдейтов Telegram
- httpx — клиент для LeafFlow API
- Pydantic settings — конфигурация через `.env`

## Быстрый старт
1. Скопируйте `.env.example` в `.env` и заполните токены и URL.
2. Установите зависимости:
   ```bash
   pip install -e .
   ```
3. Запустите приложение (по умолчанию `0.0.0.0:8000`):
   ```bash
   python -m tg_bot.main
   ```
4. Настройте вебхук у Telegram на URL `/telegram/webhook?secret_token=...` (см. `WEBHOOK_SECRET`).

## HTTP эндпоинты
- `POST /telegram/webhook` — вебхук Telegram (проверяет `secret_token`).
- `POST /internal/order-status-changed` — уведомление о статусе заказа (требует Bearer `INTERNAL_LEAFFLOW_TOKEN`).
- `GET /health` — проверка доступности.

## Основные сценарии
- `/start` — приветствие и проверка регистрации в LeafFlow.
- `/orders` — последние заказы и карточка заказа по кнопке «Подробнее».
- `/support` — отправка сообщения в приватный админский чат с кнопкой «Ответить пользователю».
- «Чат по заказу» — связывает конкретный заказ с перепиской, ответы админа копируются пользователю.
- `/help` — краткая справка.

## Скрипты
- `scripts/set_webhook.py` — установка вебхука для бота.

## Разработка
Проект использует структуру пакета `tg_bot` внутри `src/`. При желании добавьте линтеры/тесты в `pyproject.toml`.

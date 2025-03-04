# Devman notification Telegram-Bot

Этот проект представляет собой Telegram-бота, который отслеживает и отправляет уведомления о проверке работ на платформе [Devman](https://dvmn.org/).

## Установка и настройка

Установите зависимости:

```shell
pip install -r requirements.txt
```
Для работы с Telegram-ботом необходимо создать бота через [BotFather](https://telegram.me/BotFather) и получить токен. 
Укажите этот токен в переменной окружения `TG_BOT_TOKEN`. 
Также укажите id вашего чата - `TG_CHAT_ID`, который можно узнать в Telegram (например, через `@userinfobot`).

## Переменные окружения
Создайте файл `.env` в корневой папке вашего проекта и добавьте в него переменные:

- `DEVMAN_TOKEN` — токен для доступа к API DevMan.
- `TG_BOT_TOKEN` — токен вашего Telegram-бота.
- `TG_CHAT_ID` — ID чата в Telegram, куда бот будет отправлять сообщения.

Пример содержимого `.env` файла:

```
DEVMAN_TOKEN=your_devman_token
TG_BOT_TOKEN=your_telegram_bot_token
TG_CHAT_ID=your_chat_id
```

## Запуск основного скрипта
Чтобы запустить бота, выполните команду:

```bash
python main.py
```
Бот начнёт отслеживать новые проверки работ на платформе Devman и отправлять уведомления в ваш Telegram-чат.


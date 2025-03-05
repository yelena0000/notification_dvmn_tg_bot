import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv


logging.basicConfig(level=logging.ERROR)


def create_verdict_message(user_name, lesson_title, lesson_url, is_negative):
    """Создает сообщение о результатах проверки для отправки в Telegram."""
    result = '❌ Работа не принята.' if is_negative else '✅ Работа принята!'
    verdict = ('К сожалению, работа не принята и требует улучшений.'
               if is_negative else 'Работа принята!')

    return (f'{result}\n\n{user_name}, преподаватель проверил урок: '
            f'"{lesson_title}"\n🔗 {lesson_url}\n{verdict}')


def get_new_reviews(token, last_timestamp):
    """Получает новые проверки от Devman API."""
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': last_timestamp} if last_timestamp else {}

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()

    return response.json()


def send_notification_to_tg(response_content, bot, chat_id, user_name):
    """Обрабатывает данные о проверках и отправляет сообщения в Telegram."""
    if response_content['status'] == 'found':
        for attempt in response_content['new_attempts']:
            message = create_verdict_message(
                user_name,
                attempt['lesson_title'],
                attempt['lesson_url'],
                attempt['is_negative']
            )
            bot.send_message(chat_id=chat_id, text=message)


def main():
    """Запускает бота и бесконечный цикл проверки новых работ."""
    load_dotenv()

    devman_token = os.environ['DEVMAN_TOKEN']
    tg_bot_token = os.environ['TG_BOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']

    bot = telegram.Bot(token=tg_bot_token)
    user_name = bot.get_chat(tg_chat_id).first_name

    welcome_message = (
        f'👋 Привет, {user_name}! Я слежу за проверками твоих работ. '
        f'Информацию о проверках я отправлю, '
        f'когда преподаватель проверит твой урок.'
    )

    bot.send_message(chat_id=tg_chat_id, text=welcome_message)

    last_timestamp = None

    connection_retry_count = 0
    max_retries = 5

    while True:
        try:
            response_content = get_new_reviews(devman_token, last_timestamp)
            send_notification_to_tg(
                response_content,
                bot,
                tg_chat_id,
                user_name
            )
            last_timestamp = response_content.get('timestamp_to_request')

            connection_retry_count = 0

        except requests.Timeout:
            logging.info('Request timed out during polling')

        except requests.exceptions.ConnectionError:
            connection_retry_count += 1
            logging.error('Connection lost during polling')

            if connection_retry_count > max_retries:
                retry_delay = min(60, connection_retry_count * 5)
                time.sleep(retry_delay)
            else:
                time.sleep(5)


if __name__ == '__main__':
    main()

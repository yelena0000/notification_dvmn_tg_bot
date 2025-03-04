import requests
import telegram
from environs import Env


def get_new_reviews(token, last_timestamp):
    """Получает новые проверки от Devman API."""
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': last_timestamp} if last_timestamp else {}

    print(f'Отправляю запрос с params: {params}')

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()

    return response.json()


def send_notification_to_tg(response_content, bot, chat_id, last_timestamp, user_name):
    """Обрабатывает полученные проверки и отправляет сообщения в Telegram."""
    if response_content['status'] == 'timeout':
        last_timestamp = response_content.get('timestamp_to_request', last_timestamp)
    elif response_content['status'] == 'found':
        last_timestamp = response_content['last_attempt_timestamp']

        for attempt in response_content['new_attempts']:
            lesson_title = attempt['lesson_title']
            lesson_url = attempt['lesson_url']
            is_negative = attempt['is_negative']

            result = '❌ Работа не принята.' if is_negative else '✅ Работа принята!'
            verdict = ('К сожалению, работа не принята и требует улучшений.' if is_negative
                       else 'Работа принята!')

            message = (f'{result}\n\n{user_name}, преподаватель проверил урок: '
                       f'"{lesson_title}"\n🔗 {lesson_url}\n{verdict}')

            bot.send_message(chat_id=chat_id, text=message)

    return last_timestamp


def main():
    """Запускает бота и бесконечный цикл проверки новых работ."""
    env = Env()
    env.read_env()

    devman_token = env.str('DEVMAN_TOKEN')
    tg_bot_token = env.str('TG_BOT_TOKEN')
    tg_chat_id = env.int('TG_CHAT_ID')

    if not devman_token or not tg_bot_token:
        raise ValueError('Tokens cannot be empty!')

    if not isinstance(tg_chat_id, int) or tg_chat_id < 0:
        raise ValueError('Invalid TG_CHAT_ID, it must be a positive integer for personal chat')

    bot = telegram.Bot(token=tg_bot_token)

    user = bot.get_chat(tg_chat_id)
    user_name = user.first_name

    welcome_message = (f'👋 Привет, {user_name}! Я слежу за проверками твоих работ. '
                       f'Информацию о проверках я отправлю, когда преподаватель проверит твой урок.')
    bot.send_message(chat_id=tg_chat_id, text=welcome_message)

    last_timestamp = None

    while True:
        try:
            response_content = get_new_reviews(
                devman_token,
                last_timestamp
            )
            last_timestamp = send_notification_to_tg(
                response_content,
                bot,
                tg_chat_id,
                last_timestamp,
                user_name
            )

        except requests.Timeout:
            print('error: Request timed out')
        except requests.exceptions.ConnectionError:
            print('error: Connection lost')


if __name__ == '__main__':
    main()

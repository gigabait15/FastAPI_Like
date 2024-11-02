from utils_import.se_import import *


async def send_email_notification(user1, user2):
    """
    Асинхронная функция для отправки письма пользователям, если прохоит условие в роутере
    """
    await send_email(user1.email,f"Вы понравились {user2.first_name}! Почта участника: {user2.email}")
    await send_email(user2.email,f"Вы понравились {user1.first_name}! Почта участника: {user1.email}")


async def send_email(to_email, message):
    """
    Функция для отправки письма
    :param to_email: адрес получеталя письма
    :param message: текст сообщения
    """
    msg['Subject'] = 'Вам пришло оповещение'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(message)

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


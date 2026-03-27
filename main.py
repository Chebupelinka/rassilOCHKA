import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass
from cred import name, password

def send_email(
        sender: str,
        password: str,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: str = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465
) -> bool:
    """
    Отправляет письмо через SMTP-сервер (например, Gmail) с поддержкой русского языка.

    Параметры:
        sender (str): адрес отправителя (например, your_email@gmail.com)
        password (str): пароль приложения для Gmail
        recipient (str): адрес получателя
        subject (str): тема письма
        body_text (str): текстовая версия письма (обязательна)
        body_html (str, optional): HTML-версия письма (если не указана, будет использован текст)
        smtp_server (str): SMTP-сервер (по умолчанию smtp.gmail.com)
        smtp_port (int): порт (по умолчанию 465 для SSL)

    Возвращает:
        bool: True, если отправка успешна, иначе False
    """
    # Создаём сообщение
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # Прикрепляем текстовую версию (всегда)
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    # Если передана HTML-версия, прикрепляем и её
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    try:
        # Подключаемся к серверу через SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Письмо успешно отправлено!")
        return True
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")
        return False


def main():
    # Пример использования с запросом данных у пользователя
    print("=== Отправка письма через Gmail SMTP ===\n")

    subject = input("Тема письма: ")
    print("Введите текст письма (для завершения введите пустую строку):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    body_text = "\n".join(lines)
    sender = name
    pas = password
    recipient = "spb@dyanovsky.ru"
    # Можно дополнительно предложить ввести HTML-версию, но для простоты оставим только текст
    send_email(sender, pas, recipient, subject, body_text)


if __name__ == "__main__":
    main()
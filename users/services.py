#########################################################################################
import logging

import stripe
from django.core.mail import send_mail
from email_validator import EmailNotValidError, validate_email

from uni_school import settings
from uni_school.settings import STRIPE_API_KEY

logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_API_KEY


def create_stripe_session(price):
    """Создаёт цену продукта в Stripe."""
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


def get_course_subscriber_emails(course):
    """
    Возвращает список нормализованных и валидных email-адресов подписчиков курса.
    Использует `email_validator` для более строгой валидации и нормализации.
    """
    subscribers = course.subscribers.select_related('user').all()
    valid_emails = []

    for subscriber in subscribers:
        user = subscriber.user
        if not user.email:
            continue

        try:
            # Используем email_validator для валидации и нормализации
            validation_result = validate_email(user.email)
            normalized_email = validation_result.normalized
            valid_emails.append(normalized_email)
        except EmailNotValidError as e:
            logger.error(f"Некорректный email у пользователя {user.id}: {str(e)}")
            continue

    return valid_emails


def send_email_to_recipient(subject, message, recipient_email):
    """
    Отправляет письмо одному получателю.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"Письмо успешно отправлено: {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки письма на {recipient_email}: {str(e)}")
        return False


def send_email_to_recipients(subject, message, recipient_emails):
    """
    Отправляет письмо списку email-адресов.
    Возвращает количество успешно отправленных писем.
    """
    success_count = 0
    for email in recipient_emails:
        if send_email_to_recipient(subject, message, email):
            success_count += 1
    return success_count


def notify_subscribers(course):
    """
    Отправляет уведомление всем подписчикам курса.
    Возвращает количество успешных отправок.
    """
    # Проверяем, есть ли подписчики
    if not course.subscribers.exists():
        logger.warning(f"Нет подписчиков на курс {course.id}")
        return 0
    # Получаем список email-адресов подписчиков
    subscribers_emails = get_course_subscriber_emails(course)
    if not subscribers_emails:
        logger.warning(f"Нет валидных email-адресов для курса {course.id}")
        return 0
    # Формируем сообщение и отправляем
    subject = f"Обновление курса: {course.title}"
    message = f"Курс {course.title} был обновлен. Посетите страницу курса для получения информации."
    result = send_email_to_recipients(subject, message, subscribers_emails)
    if result:
        course.save(update_fields=["last_notified_at"])
    return result


#########################################################################################

#########################################################################################
import logging
from datetime import timedelta

import stripe
from django.core.mail import send_mail
from django.utils import timezone
from email_validator import EmailNotValidError, validate_email

from materials.models import Course
from uni_school import settings
from uni_school.settings import STRIPE_API_KEY
from users.models import User

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
    subscribers = course.subscribers.select_related("user").all()
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


def notify_subscribers_on_course_update():
    """
    Отправляет уведомления подписчикам о курсах, обновлённых за последние 4 часа,
    но только если они ещё не были уведомлены после обновления.
    """
    now = timezone.now()
    four_hours_ago = now - timedelta(hours=4)

    # Курсы, обновлённые за последние 4 часа и требующие уведомления
    courses = Course.objects.filter(updated_at__gte=four_hours_ago).exclude(
        # Исключаем уже уведомлённые в последние 4 часа
        last_notified_at__gte=four_hours_ago
    )

    notified_count = 0
    notified_courses = []

    for course in courses:
        # Проверяем, что уведомление ещё не отправлялось после обновления
        if not course.last_notified_at or course.last_notified_at < course.updated_at:
            sent_count = notify_subscribers(course)
            if sent_count:
                course.last_notified_at = now
                course.save(update_fields=["last_notified_at"])
                logger.info(f"Уведомления о курсе '{course.title}' отправлены {sent_count} пользователям")
                notified_count += sent_count
                notified_courses.append(course.title)

    logger.info(f"Успешно отправлено уведомлений: {notified_count} пользователям по {len(notified_courses)} курсам.")
    if notified_courses:
        logger.debug(f"Обновлённые и уведомлённые курсы: {', '.join(notified_courses)}")

    return notified_count


def deactivate_expired_users():
    """
    Деактивирует пользователей:
    - которые не заходили более 30 дней,-
    - или никогда не входили, но зарегистрированы более 30 дней назад.
    """
    expiry_time = timezone.now() - timedelta(days=30)
    # Пользователи, которые входили, но давно
    expired_active_users = User.objects.filter(is_active=True, last_login__lt=expiry_time)
    # Пользователи, которые никогда не входили, но зарегистрированы давно
    dormant_expired_users = User.objects.filter(is_active=True, last_login__isnull=True, date_joined__lt=expiry_time)
    # Объединяем QuerySets
    expired_users = expired_active_users.union(dormant_expired_users)
    # Логируем общее количество найденных пользователей
    count = expired_users.count()
    if count == 0:
        logger.info("Нет пользователей, подлежащих деактивации.")
    else:
        logger.info(f"Найдено {count} пользователей для деактивации.")
    # Деактивируем по одному с логированием
    deactivated_count = 0
    for user in expired_users:
        user.is_active = False
        user.save(update_fields=["is_active"])
        logger.info(
            f"Пользователь {user.id} ({user.email}) деактивирован: "
            f"last_login={user.last_login}, date_joined={user.date_joined}"
        )
        deactivated_count += 1

    return deactivated_count


#########################################################################################

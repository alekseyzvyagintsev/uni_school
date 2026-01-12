###############################################################################
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from materials.models import Course
from users.services import notify_subscribers

logger = logging.getLogger(__name__)


@shared_task
def send_payment_confirmation_email(payment_id):
    # Имитация отправки письма
    print(f"Отправка письма о подтверждении оплаты: {payment_id}")
    return f"Email sent for payment {payment_id}"


@shared_task
def notify_subscribers_on_course_update():
    """
    Отправляет уведомления подписчикам о курсах, обновлённых за последние 4 часа,
    но только если они ещё не были уведомлены после обновления.
    """
    now = timezone.now()
    four_hours_ago = now - timedelta(hours=4)

    # Курсы, обновлённые за последние 4 часа и требующие уведомления
    courses = Course.objects.filter(
        updated_at__gte=four_hours_ago
    ).exclude(
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
                course.save(update_fields=['last_notified_at'])
                logger.info(f"Уведомления о курсе '{course.title}' отправлены {sent_count} пользователям")
                notified_count += sent_count
                notified_courses.append(course.title)

    logger.info(f"Успешно отправлено уведомлений: {notified_count} пользователям по {len(notified_courses)} курсам.")
    if notified_courses:
        logger.debug(f"Обновлённые и уведомлённые курсы: {', '.join(notified_courses)}")

    return notified_count

###############################################################################

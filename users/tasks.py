###############################################################################
import logging

from celery import shared_task

from users.services import deactivate_expired_users, notify_subscribers_on_course_update

logger = logging.getLogger(__name__)


@shared_task
def notify_subscribers_on_course_update_task():
    """Celery задача для уведомления подписчиков о новых курсах."""
    try:
        notify_subscribers_on_course_update()
        return "Уведомления о курсах отправлены"
    except Exception as e:
        logger.error(e)
        return f"Ошибка: {str(e)}"


@shared_task
def deactivate_expired_users_task():
    """Celery задача для деактивации неактивных пользователей."""
    try:
        count = deactivate_expired_users()
        return f"Деактивировано пользователей: {count}"
    except Exception as e:
        logger.error(e)
        return f"Ошибка: {str(e)}"


###############################################################################

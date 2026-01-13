####################################################################################################################
from django.db import models
from django.utils import timezone


class Course(models.Model):
    """
    Модель представляет собой учебный курс.

    Каждый курс имеет заголовок, краткую аннотацию (предпросмотр) и подробное описание.

    #### Атрибуты:
    - **title**: Заголовок курса (строка длиной до 250 символов).
    - **preview**: Изображение-превью курса (загружается в папку `preview`).
    - **description**: Подробное описание курса (текст неограниченной длины).

    #### Особенности:
    - Название выводится как значение объекта (при помощи магического метода `__str__`).
    - Имеет настройку упорядочивания по названию.
    - Таблица базы данных именуется как `"courses"`.
    """

    title = models.CharField(max_length=250, verbose_name="название")  # Заголовок курса
    preview = models.ImageField(upload_to="preview/", blank=True, null=True)  # Картинка-предпросмотр курса
    description = models.TextField(verbose_name="описание")  # Подробное описание курса
    is_active = models.BooleanField(default=False)  # Флаг активности курса, по умолчанию курс выключен.
    price = models.PositiveIntegerField(verbose_name="Сумма оплаты", blank=True, null=True)
    # Владелец курса
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Владелец курса",
        blank=True,
        null=True,
        related_name="owned_courses",
    )
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title  # Строковое представление курса

    class Meta:
        verbose_name = "Курс"  # Наименование модели
        verbose_name_plural = "Курсы"  # Множественное наименование модели
        ordering = ["title"]  # Упорядочивание по названию
        db_table = "courses"  # Имя таблицы в БД


class Lesson(models.Model):
    """
    Модель описывает отдельный урок, принадлежащий определенному курсу.

    Урок имеет заголовок, описание и привязку к одному из курсов.

    #### Атрибуты:
    - **title**: Заголовок урока (строка длиной до 250 символов).
    - **preview**: Изображение-превью урока (загружается в папку `preview`).
    - **description**: Подробное описание урока (текст неограниченной длины).
    - **course**: Внешний ключ на соответствующий курс, к которому относится урок.

    #### Особенности:
    - Название выводится как значение объекта (через метод `__str__`).
    - Курсам разрешено иметь несколько уроков благодаря внешнему ключу с каскадным удалением.
    - Порядок вывода задаётся по названию урока.
    - Таблица базы данных называется `"lessons"`.
    """

    title = models.CharField(max_length=250, verbose_name="название")  # Заголовок урока
    preview = models.ImageField(upload_to="preview/", blank=True, null=True)  # Картинка-привью урока
    description = models.TextField(verbose_name="описание")  # Подробное описание урока
    # Связанный курс (внешний ключ)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    is_active = models.BooleanField(default=False)  # Флаг активности урока, по умолчанию урок выключен.
    link = models.URLField(blank=True, null=True)
    price = models.PositiveIntegerField(verbose_name="Сумма оплаты", blank=True, null=True)
    # Владелец урока
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Владелец урока",
        blank=True,
        null=True,
        related_name="owned_lessons",
    )

    def __str__(self):
        return self.title  # Строковое представление урока

    class Meta:
        verbose_name = "Урок"  # Наименование модели
        verbose_name_plural = "Уроки"  # Множественное наименование модели
        ordering = ["title"]  # Упорядочивание по названию
        db_table = "lessons"  # Имя таблицы в БД


class Subscription(models.Model):
    """
    Модель представляет собой подписку на курс.

    Каждая запись связывает пользователя и курс, на который подписан пользователь.

    #### Атрибуты:
    - **user**: Внешний ключ на пользователя, который подписывается.
    - **course**: Внешний ключ на курс, на который подписывается пользователь.

    #### Особенности:
    - Пользователь может подписаться на несколько курсов. На каждый курс нельзя подписаться дважды не отписавшись.
    - Таблица базы данных называется `"subscriptions"`.
    """

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="subscriptions")
    course = models.ForeignKey("materials.Course", on_delete=models.CASCADE, related_name="subscribers")

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"


####################################################################################################################

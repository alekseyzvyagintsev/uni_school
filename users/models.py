#############################################################################################
from django.contrib.auth.models import AbstractUser
from django.db import models

from materials.models import Course, Lesson


class User(AbstractUser):
    """
    Расширенная модель пользователя.

    Эта модель расширяет стандартную модель пользователя Django (AbstractUser), добавляя дополнительные поля
    для хранения контактной информации, аватара и токенов активации аккаунта.

    Поля:
        * email (EmailField): Уникальная почта пользователя (используется как основное имя пользователя).
        * phone_number (CharField): Номер телефона пользователя (необязательно).
        * avatar (ImageField): Изображение профиля пользователя (необязательно).
        * country (CharField): Страна проживания пользователя (необязательно).
        * is_active (BooleanField): Активирован ли аккаунт пользователя (по умолчанию неактивен).
        * activation_token (CharField): Токен подтверждения регистрации (необязательно).
        * token_expires_at (DateTimeField): Срок истечения токена подтверждения регистрации (необязательно).

    Методы:
        * __str__(): Возвращает электронную почту пользователя в качестве строкового представления.

    Конфигурация:
        * USERNAME_FIELD (str): Поле, используемое для идентификации пользователя (почта).
        * REQUIRED_FIELDS (list): Список обязательных полей помимо username и password.
        * verbose_name (str): Название одной записи в единственном числе.
        * verbose_name_plural (str): Название множества записей.
        * ordering (list): Порядок сортировки объектов.
        * db_table (str): Название таблицы в БД.
        * permissions (tuple): Специальные разрешения для управления пользователями.
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    activation_token = models.CharField(max_length=100, blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = [
            "username",
        ]
        db_table = "user"
        permissions = [
            ("can_block_user", "can_block_user"),
            ("can_view_user", "can_view_user"),
            ("can_add_user", "can_add_user"),
            ("can_change_user", "can_change_user"),
            ("can_delete_user", "can_delete_user"),
        ]


# Возможные варианты способов оплаты
PAYMENT_METHODS = [
    ('cash', 'Наличные'),
    ('transfer', 'Перевод на счет')
]


class Payment(models.Model):
    """
    Модель платежа.

    Хранит информацию о платеже конкретного пользователя, позволяя фиксировать оплаченный курс или урок,
    дату оплаты, метод и сумму платежа.

    Поля:
        * user (ForeignKey): Связанный пользователь, совершивший оплату.
        * date (DateTimeField): Дата совершения платежа (может быть пустой).
        * paid_course (ForeignKey): Связанный курс, который был оплачен (может быть пустым).
        * paid_lesson (ForeignKey): Связанный урок, который был оплачен (может быть пустым).
        * amount (FloatField): Размер оплаты (может быть пустым).
        * method (CharField): Способ оплаты (наличные, Перевод на счёт).

    Методы:
        * __str__(): Строковое представление платежа с указанием пользователя, предмета оплаты и суммы.

    Конфигурация:
        * verbose_name (str): Название отдельной записи.
        * verbose_name_plural (str): Название множественного числа записей.
        * db_table (str): Таблица в базе данных.
        * ordering (list): Порядок сортировки платежей (по убыванию даты оплаты).
        * permissions (tuple): Разрешения для добавления, просмотра, изменения и удаления платежей.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment")
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    paid_course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name="course")
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True, related_name="lesson")
    amount = models.FloatField(blank=True, null=True)
    method = models.CharField(max_length=8, choices=PAYMENT_METHODS, default='cash')

    def __str__(self):
        if self.paid_course:
            item = self.paid_course.title
        elif self.paid_lesson:
            item = self.paid_lesson.title
        else:
            item = "Нет информации"

        return f"Пользователь {self.user.email}, оплатил '{item}' на сумму {self.amount} руб."

    class Meta:

        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        db_table = "payment"
        ordering = ["-date"]
        permissions = [
            ("can_add_payment", "can_add_payment"),
            ("can_view_payment", "can_view_payment"),
            ("can_change_payment", "can_change_payment"),
            ("can_delete_payment", "can_delete_payment"),
        ]
        unique_together = (("user", "paid_course"), ("user", "paid_lesson"))  # Уникальность по полям


#############################################################################################

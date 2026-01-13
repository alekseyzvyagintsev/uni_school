#############################################################################################
import uuid

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
    """

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=False)

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


# Возможные варианты способов оплаты
PAYMENT_METHODS = [("cash", "Наличные"), ("transfer", "Перевод на счет")]


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
        * sum (PositiveIntegerField): Сумма платежа устанавливается автоматически при выборе урока или курса

    Методы:
        * __str__(): Строковое представление платежа с указанием пользователя, предмета оплаты и суммы.

    Конфигурация:
        * verbose_name (str): Название отдельной записи.
        * verbose_name_plural (str): Название множественного числа записей.
        * db_table (str): Таблица в базе данных.
        * ordering (list): Порядок сортировки платежей (по убыванию даты оплаты).
        * permissions (tuple): Разрешения для добавления, просмотра, изменения и удаления платежей.
    """

    ext_pay_sess_id = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    paid_course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name="payments")
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True, related_name="payments")
    method = models.CharField(max_length=8, choices=PAYMENT_METHODS, default="cash")
    amount = models.PositiveIntegerField(verbose_name="Сумма оплаты", blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.paid_course:
            self.amount = self.paid_course.price
        elif self.paid_lesson:
            self.amount = self.paid_lesson.price
        super().save(*args, **kwargs)

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
        unique_together = (
            ("user", "paid_course"),  # Платёж за курс уникальным для каждого пользователя
            ("user", "paid_lesson"),  # Платёж за урок уникальным для каждого пользователя
        )


#############################################################################################

#############################################################################################################
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.filters import OrderingFilter

from users.models import User, Payment
from users.serializer import UserSerializer, PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Представление для управления пользователями.

    Предоставляет полный CRUD-функционал для работы с объектами пользователей.
    Включает создание, просмотр списка, получение подробной информации,
    редактирование и удаление пользователей.
    """
    # Набор запросов для выборки всех пользователей
    queryset = User.objects.all()
    # Сериализатор для преобразования моделей в JSON и обратно
    serializer_class = UserSerializer


class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания новых платежных операций.

    Метод POST используется для добавления новой записи платежа.
    Полностью обрабатывается созданием экземпляра объекта Payment.
    """
    # Сериализатор для обработки входящей информации
    serializer_class = PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    Представление для отображения списка платежей.

    Позволяет получать полный список записей о платежах с поддержкой фильтрации
    и сортировки.
    Доступны поля фильтрации:
      - paid_course (оплаченный курс),
      - paid_lesson (оплаченное занятие),
      - method (метод оплаты).
    Поля сортировки:
      - date (дата платежа).
    """
    # Выборка всех существующих платежей
    queryset = Payment.objects.all()
    # Сериализатор для вывода данных
    serializer_class = PaymentSerializer
    # Задание фильтров и полей сортировки
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('paid_course', 'paid_lesson', 'method')
    ordering_fields = ('date',)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """
    Представление для просмотра детальной информации о конкретной оплате.

    Через этот endpoint доступна полная информация о заданном платеже по id.
    Метод GET возвращает всю доступную информацию по запросу.
    """
    # Выборка всех платежей
    queryset = Payment.objects.all()
    # Сериализация результата
    serializer_class = PaymentSerializer


class PaymentUpdateAPIView(generics.UpdateAPIView):
    """
    Представление для обновления существующего платежа.

    Этот класс поддерживает частичные (PATCH) и полные (PUT) обновления существующей записи платежа.
    Запись определяется по уникальному идентификатору (ID).
    """
    # Источник данных для изменений
    queryset = Payment.objects.all()
    # Инструмент сериализации обновляемых данных
    serializer_class = PaymentSerializer


class PaymentDestroyAPIView(generics.DestroyAPIView):
    """
    Представление для удаления отдельного платежа.

    Использование метода DELETE удалит соответствующую запись платежа.
    Операция необратима!
    """
    # Исходный источник данных
    queryset = Payment.objects.all()
    # Сериализатор для подтверждения операции
    serializer_class = PaymentSerializer


#############################################################################################################

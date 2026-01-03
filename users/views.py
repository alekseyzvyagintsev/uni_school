#############################################################################################################
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from materials.paginators import CustomPageNumberPagination
from users.models import Payment, User
from users.permissions import IsAdminUser, IsUserOwner
from users.serializer import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Представление для управления пользователями.

    Включает CRUD-функционал для работы с объектами пользователей.
    Предоставляет доступ к созданию новых пользователей, просмотру существующих,
    получению детальной информации, редактированию и удалению.
    """

    queryset = User.objects.all()  # Выборка всех пользователей
    pagination_class = CustomPageNumberPagination  # Кастомный постраничный пагинатор

    def get_permissions(self):
        # Описание прав для каждого варианта запроса
        if self.action == "create":
            self.permission_classes = [
                AllowAny,
            ]  # Создание профиля доступно любому пользователю
        elif self.action == "list":  # Ограничиваем просмотр списка только администраторами
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == "retrieve":  # Детализированный просмотр пользователя
            self.permission_classes = [IsAuthenticated, IsUserOwner | IsAdminUser]
        elif self.action in ["update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsUserOwner | IsAdminUser]
        return super().get_permissions()

    def get_serializer_class(self):
        # Определим сериализатор на основе текущего пользователя и запрашиваемого объекта
        user = getattr(self.request, "user", None)
        requested_user_id = self.kwargs.get("pk")

        # Если пользователь авторизован и запрашивает собственный профиль
        if user and str(user.id) == requested_user_id:
            return PrivateUserSerializer
        # Если пользователь не авторизован или запрашивает чужой профиль
        return PublicUserSerializer

    def get_queryset(self):
        # Определяем queryset в зависимости от роли пользователя
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return User.objects.all()  # Все пользователи доступны сотрудникам
            return User.objects.filter(id=self.request.user.id)  # Только собственный профиль
        return []

    def list(self, request, *args, **kwargs):
        # Переопределен метод запроса списка пользователей
        if not request.user.is_staff:
            raise PermissionDenied("У Вас недостаточно прав для просмотра списка пользователей")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Переопределен метод просмотра подробностей модели пользователя
        instance = self.get_object()  # Получаем объект пользователя по указанному pk
        current_user = request.user  # Текущий авторизованный пользователь

        # Проверяем права доступа
        if current_user.is_superuser or current_user == instance:
            return super().retrieve(request, *args, **kwargs)
        else:
            raise PermissionDenied("У вас недостаточно прав для просмотра профиля.")


class UserCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания нового пользователя.

    Метод POST используется для добавления новой записи пользователя.
    Полностью обрабатывается созданием экземпляра объекта User.
    """

    # Сериализатор для обработки входящей информации
    serializer_class = PublicUserSerializer


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
    filterset_fields = ("paid_course", "paid_lesson", "method")
    ordering_fields = ("date",)


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

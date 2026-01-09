#############################################################################################################
import stripe
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from materials.models import Course, Lesson
from materials.paginators import CustomPageNumberPagination
from users.models import Payment, User
from users.permissions import IsAdminUser, IsUserOwner
from users.serializer import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer
from users.services import create_stripe_session


@extend_schema(tags=["Users"])
@extend_schema_view(
    retrieve=extend_schema(
        summary="Детальная информация о пользователе",
    ),
    list=extend_schema(
        summary="Получение списка пользователей.",
    ),
    update=extend_schema(
        summary="Полное (PUT) обновление пользователя.",
    ),
    partial_update=extend_schema(
        summary="Частичное (PATCH) обновление пользователя.",
    ),
    destroy=extend_schema(
        summary="Удаление пользователя.",
    ),
)
class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet для работы с моделями пользователей.

    Обеспечивает базовые операции CRUD над пользователями, включая создание нового пользователя,
    получение общего списка пользователей ,
    детализацию конкретного пользователя, обновление и удаление.

    #### Основные возможности:
    - Просмотр списка пользователей (ограничено правами доступа).
    - Детальная информация о каждом пользователей (ограничено правами доступа).
    - Редактирование сведений о пользователях (ограничено правами доступа).
    - Возможность удалить пользователя (ограничено правами доступа).

    #### Методы HTTP:
    - GET /users/: Получение списка пользователей.
    - GET /users/id/: Информация о конкретном пользователе.
    - PUT /users/id/: Полное обновление пользователя.
    - PATCH /users/id/: Частичное обновление пользователя.
    - DELETE /users/id/: Удаление пользователя.

    Доступ к различным действиям контролируется системой разрешений:
    - `create`: разрешено анонимному пользователю (AllowAny).
    - `list`: ограничено администратором системы (IsAuthenticated & IsAdminUser).
    - `retrieve`, `update`, `partial_update` и `destroy`: доступ предоставляется либо владельцу аккаунта,
      либо сотруднику с ролью администратора (IsAuthenticated & (IsUserOwner | IsAdminUser)).

    Для сериализации используется два типа сериалайзера:
    - `PrivateUserSerializer`: для приватных данных самого пользователя.
    - `PublicUserSerializer`: для публичного отображения чужих профилей.

    Примечания:
    - Обычные пользователи видят только собственные профили.
    - Администратор видит полный список всех пользователей.
    - Анонимные пользователи имеют право только создать новый аккаунт.
    - Для метода retrieve применен декоратор extend_schema. В данном случае он добавляет схему для сериализатора
    PrivateUserSerializer так-как выбор сериализатора зависит от прав пользователя, то данный сериализатор не виден
    по умолчанию для swagger UI
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
        # Метод запроса списка пользователей
        if not request.user.is_staff:
            raise PermissionDenied("У Вас недостаточно прав для просмотра списка пользователей")
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={200: PrivateUserSerializer})
    def retrieve(self, request, *args, **kwargs):
        # Переопределен метод просмотра подробностей модели пользователя
        instance = self.get_object()  # Получаем объект пользователя по указанному pk
        current_user = request.user  # Текущий авторизованный пользователь

        # Проверяем права доступа
        if current_user.is_superuser or current_user == instance:
            return super().retrieve(request, *args, **kwargs)
        else:
            raise PermissionDenied("У вас недостаточно прав для просмотра профиля.")

    def update(self, request, *args, **kwargs):
        # Метод PUT остается не низменным.
        pass

    def partial_update(self, request, *args, **kwargs):
        # Метод PATCH остается не низменным
        pass

    def destroy(self, request, *args, **kwargs):
        # Метод DELETE остается не низменным
        pass


class UserCreateAPIView(CreateAPIView):
    """
    Представление для создания нового пользователя.

    Метод POST используется для добавления новой записи пользователя.
    Полностью обрабатывается созданием экземпляра объекта User.

    #### Возможности:
    - Только создание нового пользователя.

    #### Метод HTTP:
    - POST /register/: Отправка формы для создания пользователя.
    """

    # Сериализатор для обработки входящей информации
    serializer_class = PublicUserSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Users"],
        summary="Регистрация нового пользователя",
        description="Создает нового пользователя с указанным именем, почтой и паролем.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@extend_schema(tags=["Payments"])
class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания новых платежных операций.

    **Метод POST** используется для добавления новой записи платежа.

    ### Процесс обработки запросов:

    - Передаются данные выбранной единицы оплаты (`paid_course` или `paid_lesson`), а также методы оплаты.
    - Обязательно наличие ровно одной из указанных единиц (`paid_course` или `paid_lesson`) для корректной обработки.
    - В зависимости от переданного типа (`Course` или `Lesson`) выбирается соответствующий элемент базы данных.
    - Создается новая платежная операция, фиксируется выбранный объект и тип оплаты.
    - Запись сохраняется в БД.

    #### Описание шагов обработки:

    1. Извлекается информация из HTTP-запроса:
       - Тип оплачиваемого объекта (`Course` или `Lesson`)
       - Идентификатор конкретного объекта
       - Способ оплаты

    2. Исходя из указанного типа, определяется конкретный объект для оплаты.

    3. Если выбран вариант оплаты через Stripe:
       - Форматируется название продукта для сервиса Stripe.
       - Создаются соответствующие сущности в Stripe (продукт, цена, сессия оплаты).
       - Генерируется уникальная ссылка на оплату.
       - Дополнительные поля (идентификатор сессии Stripe и ссылка на оплату) сохраняются в модели Payment.

    ### Возможные фильтры и поисковые критерии:

    - **Фильтрация**: по полю оплаченного курса (`paid_course`), урока (`paid_lesson`) и способа оплаты (`method`).
    - **Поиск**: по email пользователя (`user__email`) и названию курса (`course__name`).
    - **Сортировка**: возможна по дате платежа (`date`).

    ---

    Таким образом, логика обеспечивает надежное создание платежей с возможностью интеграции сторонних сервисов оплаты.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["paid_course", "paid_lesson", "method"]  # Фильтры по курсу, уроку и методу оплаты
    search_fields = ["user__email", "course__name"]  # Поиск по email пользователя и названию курса
    ordering_fields = ["date"]  # Возможность сортировки по дате платежа

    def perform_create(self, serializer):
        # Получаем данные из запроса
        data = self.request.data

        # Определяем тип объекта (курс или урок)
        object_type = data.get('product')
        object_id = data.get('id')

        if object_type == 'Course':
            course_or_lesson = Course.objects.get(id=object_id)
        elif object_type == 'Lesson':
            course_or_lesson = Lesson.objects.get(id=object_id)
        else:
            raise ValueError("Необходимо передать объект типа Course или Lesson.")

        # Данные метода оплаты
        method = data.get("method")
        user = self.request.user

        # Создаем запись платежа
        payment = serializer.save(user=user,)
        payment.title = data.get('title')
        payment.description = data.get('description')
        payment.method=method
        payment.paid_course = course_or_lesson if isinstance(course_or_lesson, Course) else None
        payment.paid_lesson = course_or_lesson if isinstance(course_or_lesson, Lesson) else None
        payment.save()
        print(f'mey be cash {payment}')

        # Если оплата производится через Stripe
        if method == "transfer":
            # Формируем наименование продукта для Stripe
            stripe_product_name = f"{type(course_or_lesson).__name__.capitalize()} '{course_or_lesson.title}'"

            # Создаем продукт в Stripe
            stripe_product = stripe.Product.create(
                name=stripe_product_name,
                description=course_or_lesson.description,
                metadata={"prod_id_from_db": course_or_lesson.id}
            )

            # Создаем цену в Stripe
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(course_or_lesson.price * 100),
                currency="rub"
            )

            # Создаем сессию Stripe и фиксируем её ID и ссылку
            session_id, session_url = create_stripe_session(stripe_price)

            # Сохраняем дополнительную информацию в модели Payment
            payment.ext_pay_sess_id = session_id
            payment.link = session_url
            payment.save()
            print(f'transfer {payment}')


    @extend_schema(
        summary="Создание платежа",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@extend_schema(tags=["Payments"])
class PaymentListAPIView(generics.ListAPIView):
    """
    Представление для отображения списка платежей.

    Позволяет получать полный список записей о платежах с поддержкой фильтрации
    и сортировки.
    #### Доступны поля фильтрации:
      - paid_course (оплаченный курс),
      - paid_lesson (оплаченное занятие),
      - method (метод оплаты).
    #### Поля сортировки:
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

    @extend_schema(
        summary="Получение списка платежей",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


@extend_schema(tags=["Payments"])
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

    @extend_schema(
        summary="Получение подробностей о платеже",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=["Payments"])
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

    @extend_schema(
        summary="Полное изменение платежа",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное изменение платежа"
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema(tags=["Payments"])
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

    @extend_schema(
        summary="Удаление платежа",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


#############################################################################################################

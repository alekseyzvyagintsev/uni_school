##############################################################################################################
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.paginators import CustomPageNumberPagination
from materials.serializer import CourseSerializer, LessonSerializer
from users.permissions import IsAdminUser, IsModer, IsUserOwner
from users.tasks import notify_subscribers_on_course_update, notify_subscribers_on_course_update_task


@extend_schema(tags=["Courses"])
@extend_schema_view(
    create=extend_schema(
        summary="Создание курса",
    ),
    retrieve=extend_schema(
        summary="Детальная информация о курсе",
    ),
    list=extend_schema(
        summary="Получение списка курсов.",
    ),
    update=extend_schema(
        summary="Полное (PUT) обновление сурса.",
    ),
    partial_update=extend_schema(
        summary="Частичное (PATCH) обновление курса.",
    ),
    destroy=extend_schema(
        summary="Удаление курса.",
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    """
    Представление для полного управления учебными курсами.

    Реализует стандартный CRUD-контроллер для учебных курсов, позволяя создавать новые курсы,
    просматривать существующие, изменять их содержимое и удалять ненужные.

    #### Основные возможности:
    - Просмотр списка курсов.
    - Детальная информация о каждом курсе.
    - Редактирование сведений о курсах.
    - Возможность удалить курс.

    #### Методы HTTP:
    - GET /courses/: Получение списка курсов.
    - GET /courses/id/: Информация о конкретном курсе.
    - POST /courses/: Создание нового курса.
    - PUT /courses/id/: Полное обновление курса.
    - PATCH /courses/id/: Частичное обновление курса.
    - DELETE /courses/id/: Удаление курса.
    """

    queryset = Course.objects.all()  # Выборка всех курсов
    serializer_class = CourseSerializer  # Сериализатор для преобразования моделей в JSON
    pagination_class = CustomPageNumberPagination  # Кастомный постраничный пагинатор

    def perform_create(self, serializer):
        """Функция автоматически добавляет текущего аутентифицированного пользователя
        в поле owner объекта курса и устанавливает текущее время обновления."""
        serializer.save(owner=self.request.user, updated_at=now())

    # Определяем правила доступа для разных действий.
    permission_classes_by_action = {
        # Курс может создать только авторизованный пользователь.
        "create": [
            IsAuthenticated,
        ],
        # Список курсов виден только авторизованным пользователям.
        "list": [IsAuthenticated, IsModer | IsUserOwner | IsAdminUser],
        # Детали конкретного курса видны только авторизованным пользователям.
        "retrieve": [IsAuthenticated, IsModer | IsUserOwner | IsAdminUser],
        # Крс может обновлять сам пользователь и модератор.
        "update": [IsAuthenticated, IsModer | IsUserOwner | IsAdminUser],
        "partial_update": [IsAuthenticated, IsModer | IsUserOwner | IsAdminUser],
        # Удалить курс разрешено только администраторам и владельцам.
        "destroy": [IsUserOwner | IsAdminUser],
    }

    def get_permissions(self):
        try:
            # Возвращаем список классов разрешений для соответствующего действия
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # По умолчанию используем разрешения, указанные в классе представления
            return super().get_permissions()

    def list(self, request, *args, **kwargs):
        # Переопределен метод запроса списка пользователей
        is_admin = request.user.is_superuser
        is_moder = request.user.groups.filter(name="Модератор").exists()
        if is_admin or is_moder:
            return super().list(request, *args, **kwargs)
        else:
            # Обычные пользователи видят только свои курсы
            queryset = self.get_queryset().filter(owner=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    def get_serializer_context(self):
        """
        Возвращает словарь с контекстом, который сериализатор сможет использовать для обработки.
        Здесь передаём экземпляр запроса (request), чтобы сериализатор имел доступ к пользователю.
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})  # Добавляем объект запроса в контекст
        return context

    def perform_update(self, serializer):
        serializer.save(updated_at=now())
        notify_subscribers_on_course_update.delay()

    def perform_destroy(self, instance):
        course_id = instance.id
        super().perform_destroy(instance)
        notify_subscribers_on_course_update.delay(course_id)


@extend_schema(tags=["Lessons"])
class LessonCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания новых уроков.

    Позволяет пользователям создать новый урок с указанием обязательных полей.

    #### Возможности:
    - Только создание нового урока.

    #### Метод HTTP:
    - POST /lesson/create/: Отправка формы для создания урока.
    """

    serializer_class = LessonSerializer  # Сериализатор для формирования формы создания урока
    # Урок может создать только авторизованный пользователь.
    permission_classes = (
        IsAuthenticated,
        ~IsModer,
    )

    @extend_schema(
        summary="Создание нового урока",
        description="Создает новый с указанным названия, описания и принадлежность к курсу.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Функция автоматически добавляет текущего аутентифицированного пользователя
        в поле owner объекта урока."""
        lesson = serializer.save(owner=self.request.user)
        # Обновляем `updated_at` у курса
        course = lesson.course
        course.updated_at = now()
        course.save(update_fields=["updated_at"])  # Чтобы не срабатывали другие сигналы
        notify_subscribers_on_course_update_task.delay()  # Запускаем в фоне рассылку уведомлений об обновлении курса


@extend_schema(tags=["Lessons"])
class LessonListAPIView(generics.ListAPIView):
    """
    Представление для отображения списка уроков.

    Показывает полный перечень созданных уроков.

    #### Возможности:
    - Просмотр списка всех уроков.

    #### Метод HTTP:
    - GET /lessons/: Получение списка уроков.
    """

    queryset = Lesson.objects.all()  # Выборка всех уроков
    serializer_class = LessonSerializer  # Сериализатор для подготовки данных
    pagination_class = CustomPageNumberPagination  # Кастомный постраничный пагинатор
    # Список уроков виден только авторизованным пользователям:
    # Админимтраторам и модераторам список всех уроков.
    # Владельцам только свои уроки.
    permission_classes = (
        IsAuthenticated,
        IsModer | IsAdminUser | IsUserOwner,
    )

    @extend_schema(
        summary="Получение списка уроков",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        if self.request.user.is_staff:
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


@extend_schema(tags=["Lessons"])
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Представление для получения детальной информации об одном уроке.

    Позволяет просмотреть полную информацию о конкретном уроке.

    #### Возможности:
    - Подробная информация о конкретном уроке.

    #### Метод HTTP:
    - GET /lesson/<id>/: Получение деталей урока по его идентификатору.
    """

    queryset = Lesson.objects.all()  # Выборка всех уроков
    serializer_class = LessonSerializer  # Сериализатор для отображения данных
    # Подробности урока виден только авторизованным пользователям:
    # Админимтраторам и модераторам список всех уроков.
    # Владельцам только свои уроки.
    permission_classes = (
        IsAuthenticated,
        IsModer | IsAdminUser | IsUserOwner,
    )

    @extend_schema(
        summary="Получение подробностей об уроке",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=["Lessons"])
class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Представление для изменения данных об уроке.

    Позволяет обновить содержание урока путём полной замены данных (PUT) или частичного обновления (PATCH).

    #### Возможности:
    - Изменение содержимого урока.

    #### Методы HTTP:
    - PUT /lesson/<id>/: Полное обновление урока.
    - PATCH /lesson/<id>/: Частичное обновление урока.
    """

    queryset = Lesson.objects.all()  # Выборка всех уроков
    serializer_class = LessonSerializer  # Сериализатор для сохранения изменений
    # Редактировать урок могут только авторизованные пользователи:
    # Админимтраторам и модераторам доступны все уроки.
    # Владельцам только свои уроки.
    permission_classes = (
        IsAuthenticated,
        IsModer | IsAdminUser | IsUserOwner,
    )

    @extend_schema(
        summary="Полное изменение урок",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(summary="Частичное изменение урока")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    # Обновляем `updated_at` у курса
    def perform_update(self, serializer):
        lesson = serializer.save()
        course = lesson.course
        course.updated_at = now()
        course.save(update_fields=["updated_at"])  # Чтобы не срабатывали другие сигналы
        notify_subscribers_on_course_update_task.delay()  # Запускаем в фоне рассылку уведомлений об обновлении курса


@extend_schema(tags=["Lessons"])
class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Представление для удаления урока.

    Позволяет администраторам удалить указанный урок навсегда.

    #### Возможности:
    - Удаление выбранного урока.

    #### Метод HTTP:
    - DELETE /lesson/<id>/: Удаление урока по указанному идентификатору.
    """

    queryset = Lesson.objects.all()  # Выборка всех уроков
    serializer_class = LessonSerializer  # Сериализатор для подтверждения операции
    # Удалить урок разрешено только администраторам и владельцам.
    # Модераторы не могут удалять уроки.
    permission_classes = (
        IsAuthenticated,
        ~IsModer | IsAdminUser | IsUserOwner,
    )

    @extend_schema(
        summary="Удаление урока",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    # Обновляем `updated_at` у курса
    def perform_destroy(self, instance):
        course = instance.course
        super().perform_destroy(instance)
        course.updated_at = now()
        course.save(update_fields=["updated_at"])  # Чтобы не срабатывали другие сигналы
        notify_subscribers_on_course_update_task.delay()  # Запускаем в фоне рассылку уведомлений об обновлении курса


@extend_schema(tags=["Subscribe"])
class SubscribeToCourse(APIView):
    """
    Представление для управления подписками пользователей на курсы.

    Методы:
        POST: Добавляет или удаляет подписку текущего пользователя на указанный курс.

    Параметры запроса:
        course_id (int): ID курса, на который подписывается или отказывается пользователь.

    Возвращаемые значения:
        Успех (HTTP 200 OK):
            {"message": "Подписка добавлена."}
            {"message": "Подписка удалена."}

        Ошибка (HTTP 400 Bad Request):
            {"error": "Требуется course_id."}
            {"error": "Курс не найден."}
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Подписаться/отписаться от курса",
        description="Добавляет или удаляет подписку текущего пользователя на указанный курс.",
        request={"application/json": {"type": "object", "properties": {"course_id": {"type": "integer"}}}},
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    def post(self, request):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "Требуется course_id."}, status=400)

        try:
            course = get_object_or_404(Course, pk=course_id)
            subscription_exists = Subscription.objects.filter(user=user, course=course).exists()

            if subscription_exists:
                Subscription.objects.filter(user=user, course=course).delete()
                message = "Подписка удалена."
            else:
                Subscription.objects.create(user=user, course=course)
                message = "Подписка добавлена."

            return Response({"message": message}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


##############################################################################################################

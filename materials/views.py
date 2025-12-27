##############################################################################################################
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from materials.models import Course, Lesson
from materials.serializer import CourseSerializer, LessonSerializer
from users.permissions import IsAdminUser, IsModer, IsUserOwner


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
    - GET /courses/<id>/: Информация о конкретном курсе.
    - POST /courses/: Создание нового курса.
    - PUT /courses/<id>/: Полное обновление курса.
    - PATCH /courses/<id>/: Частичное обновление курса.
    - DELETE /courses/<id>/: Удаление курса.
    """

    queryset = Course.objects.all()  # Выборка всех курсов
    serializer_class = CourseSerializer  # Сериализатор для преобразования моделей в JSON

    def perform_create(self, serializer):
        """Функция автоматически добавляет текущего аутентифицированного пользователя
        в поле owner объекта курса."""
        serializer.save(owner=self.request.user)

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

    def perform_create(self, serializer):
        """Функция автоматически добавляет текущего аутентифицированного пользователя
        в поле owner объекта урока."""
        serializer.save(owner=self.request.user)


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
    # Список уроков виден только авторизованным пользователям:
    # Админимтраторам и модераторам список всех уроков.
    # Владельцам только свои уроки.
    permission_classes = (
        IsAuthenticated,
        IsModer | IsAdminUser | IsUserOwner,
    )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return Lesson.objects.all()
            return Lesson.objects.filter(owner=self.request.user)
        return None


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


##############################################################################################################

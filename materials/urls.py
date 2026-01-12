##############################################################################################################
from django.urls import path
from rest_framework.routers import DefaultRouter

from materials.apps import MaterialsConfig
from materials.views import (CourseViewSet,
                             LessonCreateAPIView,
                             LessonDestroyAPIView,
                             LessonListAPIView,
                             LessonRetrieveAPIView,
                             LessonUpdateAPIView,
                             SubscribeToCourse)

app_name = MaterialsConfig.name

# Создаем экземпляр роутера
router = DefaultRouter()

# Регистрируем ViewSets для модели courses
router.register(r"courses", CourseViewSet, basename="courses")  # Роутер для курсов
urlpatterns = [
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-get"),
    path("lesson/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lesson/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-destroy"),
    path("subscribe/", SubscribeToCourse.as_view(), name="subscribe"),
]
urlpatterns += router.urls  # Включаем автоматически созданные URL-адреса

##############################################################################################################

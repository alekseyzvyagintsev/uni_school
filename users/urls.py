#############################################################################################################
from users.apps import UsersConfig
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

app_name = UsersConfig.name

# Регистрируем ViewSets для модели User
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users') # Роутер для пользователя

urlpatterns = [

]

urlpatterns += router.urls  # Включаем автоматически созданные URL-адреса


#############################################################################################################

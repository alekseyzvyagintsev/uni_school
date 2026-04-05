#############################################################################################################
from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from users.apps import UsersConfig
from users.views import (PaymentCreateAPIView,
                         PaymentDestroyAPIView,
                         PaymentListAPIView,
                         PaymentRetrieveAPIView,
                         PaymentUpdateAPIView,
                         UserCreateAPIView,
                         UserViewSet)

app_name = UsersConfig.name

# Регистрируем ViewSets для модели User
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")  # Роутер для пользователя


urlpatterns = [
    path("register/", UserCreateAPIView.as_view(permission_classes=(AllowAny,)), name="user-create"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("payment/create/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("payment/<int:pk>/", PaymentRetrieveAPIView.as_view(), name="payment-get"),
    path("payment/update/<int:pk>/", PaymentUpdateAPIView.as_view(), name="payment-update"),
    path("payment/delete/<int:pk>/", PaymentDestroyAPIView.as_view(), name="payment-destroy"),
]

urlpatterns += router.urls  # Включаем автоматически созданные URL-адреса


#############################################################################################################

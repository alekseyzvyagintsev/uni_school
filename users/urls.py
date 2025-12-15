#############################################################################################################
from django.urls import path

from users.apps import UsersConfig
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, PaymentCreateAPIView, PaymentListAPIView, PaymentRetrieveAPIView, \
    PaymentUpdateAPIView, PaymentDestroyAPIView

app_name = UsersConfig.name

# Регистрируем ViewSets для модели User
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users') # Роутер для пользователя

urlpatterns = [
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payment/<int:pk>/', PaymentRetrieveAPIView.as_view(), name='payment-get'),
    path('payment/update/<int:pk>/', PaymentUpdateAPIView.as_view(), name='payment-update'),
    path('payment/delete/<int:pk>/', PaymentDestroyAPIView.as_view(), name='payment-destroy'),

]

urlpatterns += router.urls  # Включаем автоматически созданные URL-адреса


#############################################################################################################

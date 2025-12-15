##############################################################################################################
from rest_framework import serializers

from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Отвечает за преобразование экземпляров модели Payment в JSON и обратно.

    **Настройки:**
    - `model`: Используется модель Payment.
    - `fields`: Все поля модели.
    - `read_only_fields`: ID автоматически генерируется системой и доступен только для чтения.
    """

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Включает вложенную структуру для отображения платежей пользователя.

    **Поля:**
    - `payment`: Представляет платежи пользователя с использованием PaymentSerializer.
      Может содержать несколько платежей (many=True). Доступно только для чтения.

    **Настройки:**
    - `model`: Используется модель User.
    - `fields`: Все поля модели.
    - `read_only_fields`: ID автоматически генерируется системой и доступен только для чтения.
    """
    payment = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id',)


##############################################################################################################

#############################################################################################################
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from users.models import User


def create_admin_group():
    # Создание группы администраторов
    try:
        admin_group = Group.objects.get(name="Администратор")
    except Group.DoesNotExist:
        admin_group = Group.objects.create(name="Администратор")

    # Получение всех существующих разрешений
    all_permissions = list(Permission.objects.all())

    # Присвоение всех разрешений группе
    admin_group.permissions.add(*all_permissions)


def create_moderator_group():
    # Создание группы модераторов
    try:
        Group.objects.get(name="Модератор")
    except Group.DoesNotExist:
        Group.objects.create(name="Модератор")


def create_user_group():
    # Создание группы пользователей
    try:
        Group.objects.get(name="Пользователь")
    except Group.DoesNotExist:
        Group.objects.create(name="Пользователь")


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            admin = User.objects.get(email="admin@example.com")
        except User.DoesNotExist:
            admin = User.objects.create(
                email="admin@example.com",
            )
        print(f"admin.id {admin.id}")
        admin.username = "admin"
        admin.set_password("qwer1234")
        admin.is_active = True
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        create_admin_group()
        admin_group = Group.objects.get(name="Администратор")
        admin.groups.add(admin_group)

        try:
            moderator = User.objects.get(
                email="moderator@example.com")
        except User.DoesNotExist:
            moderator = User.objects.create(
                email="moderator@example.com",
            )
        print(f"moderator.id {moderator.id}")
        moderator.username = "moderator"
        moderator.set_password("qwer1234")
        moderator.is_active = True
        moderator.is_staff = True
        moderator.save()
        create_moderator_group()
        moderator_group = Group.objects.get(name="Модератор")
        moderator.groups.add(moderator_group)

        try:
            user = User.objects.create(
                email="user@example.com")
        except User.DoesNotExist:
            user = User.objects.create(
                email="user@example.com",
            )
        print(f"user.id {user.id}")
        user.username = "user"
        user.set_password("qwer1234")
        user.is_active = True
        user.save()
        create_user_group()
        user_group = Group.objects.get(name="Пользователь")
        user.groups.add(user_group)


#############################################################################################################

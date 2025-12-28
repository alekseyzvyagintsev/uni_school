#############################################################################################################
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from users.models import User


def create_admin_group():
    # Создание группы администраторов
    admin_group = Group.objects.create(name="Администратор")

    # Получение всех существующих разрешений
    all_permissions = list(Permission.objects.all())

    # Присвоение всех разрешений группе
    admin_group.permissions.add(*all_permissions)


def create_manager_group():
    # Создание группы менеджеров.
    manager_group = Group.objects.create(name="Менеджер")

    # Назначение необходимых разрешений
    required_permissions = [
        "can_block_user",
        "can_view_user",
        "view_course",
        "view_lesson",
        "view_payment",
    ]

    # Преобразуем имена разрешений в объекты разрешений
    permissions_objects = []
    for perm_codename in required_permissions:
        try:
            perm_obj = Permission.objects.get(codename=perm_codename)
            permissions_objects.append(perm_obj)
        except Permission.DoesNotExist:
            print(f"Право '{perm_codename}' не найдено.")

    # Присвоение выбранных разрешений группе
    if permissions_objects:
        manager_group.permissions.add(*permissions_objects)


def create_moderator_group():
    # Создание группы модераторов
    moderator_group = Group.objects.create(name="Модератор")

    # Назначение необходимых разрешений
    required_permissions = [
        "change_course",
        "view_course",
        "view_lesson",
        "change_lesson",
    ]

    # Преобразуем имена разрешений в объекты разрешений
    permissions_objects = []
    for perm_codename in required_permissions:
        try:
            perm_obj = Permission.objects.get(codename=perm_codename)
            permissions_objects.append(perm_obj)
        except Permission.DoesNotExist:
            print(f"Право '{perm_codename}' не найдено.")

    # Присвоение выбранных разрешений группе
    if permissions_objects:
        moderator_group.permissions.add(*permissions_objects)


def create_user_group():
    # Создание группы пользователей
    user_group = Group.objects.create(name="Пользователь")

    # Назначение необходимых разрешений
    required_permissions = [
        "can_view_user",
        "can_change_user",
        "can_delete_user",
        "view_lesson",
        "view_course",
        "view_payment",
    ]

    # Преобразуем имена разрешений в объекты разрешений
    permissions_objects = []
    for perm_codename in required_permissions:
        try:
            perm_obj = Permission.objects.get(codename=perm_codename)
            permissions_objects.append(perm_obj)
        except Permission.DoesNotExist:
            print(f"Право '{perm_codename}' не найдено.")

    # Присвоение выбранных разрешений группе
    if permissions_objects:
        user_group.permissions.add(*permissions_objects)


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin = User.objects.create(
            email="admin@example.com",
            username="admin",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        admin.set_password("qwer1234")
        admin.save()
        create_admin_group()
        admin_group = Group.objects.get(name="Администратор")
        admin.groups.add(admin_group)

        moderator = User.objects.create(
            email="moderator@example.com",
            username="moderator",
            is_active=True,
            is_staff=True,
        )
        moderator.set_password("qwer1234")
        moderator.save()
        create_manager_group()
        moderator_group = Group.objects.get(name="Модератор")
        moderator.groups.add(moderator_group)

        manager = User.objects.create(
            email="manager@example.com",
            username="manager",
            is_active=True,
            is_staff=True,
        )
        manager.set_password("qwer1234")
        manager.save()
        create_manager_group()
        manager_group = Group.objects.get(name="Менеджер")
        manager.groups.add(manager_group)

        user = User.objects.create(
            email="user@example.com",
            username="user",
            is_active=True,
        )
        user.set_password("qwer1234")
        user.save()
        create_user_group()
        user_group = Group.objects.get(name="Пользователь")
        user.groups.add(user_group)


#############################################################################################################

from django.contrib import admin

from materials.models import Subscription
from users.models import Payment, User


# admin.site.register(CustomUser)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ("password",)


admin.site.register(Payment)
admin.site.register(Subscription)

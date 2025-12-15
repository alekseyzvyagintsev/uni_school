from django.contrib import admin

from users.models import User, Payment


# admin.site.register(CustomUser)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ("password",)


admin.site.register(Payment)

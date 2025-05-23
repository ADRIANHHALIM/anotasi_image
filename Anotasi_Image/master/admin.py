from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Dataset

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dataset)

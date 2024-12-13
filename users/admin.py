from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Transaction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Делаем так, чтобы при добавлении пользователя не выходили из админки
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'balance')}),
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('phone', 'balance')}),  # Поля телефона и баланса      
    )
    
    list_display = ('phone', 'first_name', 'last_name', 'balance')
    ordering = ['last_name']  # Сортировка по по фамилии 
admin.site.register(Transaction)
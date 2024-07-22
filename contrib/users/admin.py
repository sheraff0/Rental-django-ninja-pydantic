from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from contrib.users.models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    model = User
    list_display = ( 'email', 'phone_str', 'fio', 'is_active', 'is_verified', 'create_time')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'last_name', 'first_name', 'middle_name', 'birth_date', 'avatar',
            'email', 'phone', 'contact_phone', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'is_verified')}),
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'last_name', 'first_name', 'middle_name', 'birth_date', 'avatar', 'email', 'phone', 'password1', 'password2',)}
        ),
        ('Permissions', {
                'fields': ('is_active', 'is_superuser', 'is_staff', 'is_verified')
            }
        ),
    )

    #readonly_fields = ("phone", "contact_phone", "email", )
    search_fields = ('last_name', 'first_name', 'middle_name', 'email')
    ordering = ('-update_time',)

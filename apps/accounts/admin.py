from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import User, EmailOTP


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'email',
        'first_name',
        'last_name',
        'phone',
        'role',
        'email_verified',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'role',
        'email_verified',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'email',
        'first_name',
        'last_name',
        'phone',
    )

    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Room Finder Details', {
            'fields': (
                'phone',
                'role',
                'email_verified',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Room Finder Details', {
            'fields': (
                'email',
                'first_name',
                'last_name',
                'phone',
                'role',
                'email_verified',
            )
        }),
    )

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__email', 'otp')
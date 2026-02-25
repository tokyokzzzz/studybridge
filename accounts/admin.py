from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'current_country', 'university', 'is_verified', 'date_joined')
    list_filter = ('is_verified', 'study_level', 'current_country')
    search_fields = ('email', 'username', 'full_name', 'university')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('StudyBridge Profile', {
            'fields': ('full_name', 'country_of_origin', 'current_country', 'university',
                       'study_level', 'field_of_study', 'bio', 'avatar', 'is_verified')
        }),
    )

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from .models import User, UniversitySubmission, ScholarshipSubmission


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'current_country', 'university', 'is_verified', 'date_joined')
    list_filter = ('is_verified', 'study_level', 'current_country')
    search_fields = ('email', 'username', 'full_name', 'university')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('StudyBridge Profile', {
            'fields': ('full_name', 'country_of_origin', 'current_country', 'university',
                       'study_level', 'year_of_study', 'field_of_study', 'bio', 'avatar', 'is_verified')
        }),
    )


@admin.register(UniversitySubmission)
class UniversitySubmissionAdmin(admin.ModelAdmin):
    list_display = ('university_name', 'country', 'city', 'submitted_by', 'status_badge', 'submitted_at', 'preview_photo')
    list_filter = ('status', 'country')
    search_fields = ('university_name', 'country', 'city', 'submitted_by__email', 'submitted_by__username')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_by', 'submitted_at', 'reviewed_at', 'preview_photo_large')
    actions = ['approve_submissions', 'reject_submissions']

    fieldsets = (
        ('Submission Info', {
            'fields': ('submitted_by', 'submitted_at', 'status', 'admin_note', 'reviewed_at')
        }),
        ('University Details', {
            'fields': ('university_name', 'country', 'city', 'description', 'website', 'founded_year')
        }),
        ('Photo', {
            'fields': ('photo', 'preview_photo_large')
        }),
    )

    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'approved': '#10b981', 'rejected': '#ef4444'}
        labels = {'pending': '⏳ Pending', 'approved': '✅ Approved', 'rejected': '❌ Rejected'}
        color = colors.get(obj.status, '#64748b')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:50px;font-size:12px;font-weight:700;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'

    def preview_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:6px;" />', obj.photo.url)
        return '—'
    preview_photo.short_description = 'Photo'

    def preview_photo_large(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-width:500px;max-height:300px;object-fit:cover;border-radius:10px;margin-top:8px;" />', obj.photo.url
            )
        return '—'
    preview_photo_large.short_description = 'Photo Preview'

    def approve_submissions(self, request, queryset):
        updated = queryset.exclude(status='approved').update(status='approved', reviewed_at=timezone.now())
        self.message_user(request, f'✅ {updated} submission(s) approved and published to the Universities page.')
    approve_submissions.short_description = '✅ Approve selected submissions'

    def reject_submissions(self, request, queryset):
        updated = queryset.exclude(status='rejected').update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f'❌ {updated} submission(s) rejected.')
    reject_submissions.short_description = '❌ Reject selected submissions'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ScholarshipSubmission)
class ScholarshipSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'university_name', 'scholarship_type', 'submitted_by', 'status_badge', 'submitted_at')
    list_filter = ('status', 'scholarship_type', 'coverage')
    search_fields = ('title', 'university_name', 'submitted_by__email', 'submitted_by__username')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_by', 'submitted_at', 'reviewed_at')
    actions = ['approve_submissions', 'reject_submissions']

    fieldsets = (
        ('Submission Info', {
            'fields': ('submitted_by', 'submitted_at', 'status', 'admin_note', 'reviewed_at')
        }),
        ('Scholarship Details', {
            'fields': ('title', 'university_name', 'scholarship_type', 'coverage',
                       'stipend_amount', 'stipend_unknown', 'deadline', 'no_deadline',
                       'description', 'link')
        }),
    )

    def status_badge(self, obj):
        colors = {'pending': '#f59e0b', 'approved': '#10b981', 'rejected': '#ef4444'}
        labels = {'pending': '⏳ Pending', 'approved': '✅ Approved', 'rejected': '❌ Rejected'}
        color = colors.get(obj.status, '#64748b')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:50px;font-size:12px;font-weight:700;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'

    def approve_submissions(self, request, queryset):
        updated = queryset.exclude(status='approved').update(status='approved', reviewed_at=timezone.now())
        self.message_user(request, f'✅ {updated} scholarship(s) approved and published.')
    approve_submissions.short_description = '✅ Approve selected scholarships'

    def reject_submissions(self, request, queryset):
        updated = queryset.exclude(status='rejected').update(status='rejected', reviewed_at=timezone.now())
        self.message_user(request, f'❌ {updated} scholarship(s) rejected.')
    reject_submissions.short_description = '❌ Reject selected scholarships'

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

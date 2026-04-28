from django.contrib import admin

from .models import SecurityProfile


@admin.register(SecurityProfile)
class SecurityProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "domain", "score", "mfa_enabled", "password_manager_used", "recovery_email_secured", "updated_at")
    search_fields = ("email", "domain")

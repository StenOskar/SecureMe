from django.db import models


class SecurityProfile(models.Model):
    email = models.EmailField(unique=True)
    domain = models.CharField(max_length=255, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    password_manager_used = models.BooleanField(default=False)
    recovery_email_secured = models.BooleanField(default=False)
    device_updates_current = models.BooleanField(default=False)
    breach_monitoring_enabled = models.BooleanField(default=False)
    privacy_exposure_reviewed = models.BooleanField(default=False)
    score = models.PositiveSmallIntegerField(default=0)
    assessment_answers = models.JSONField(default=dict, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

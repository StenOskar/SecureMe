from rest_framework import serializers

from .models import SecurityProfile
from .scoring import score_profile


class SecurityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityProfile
        fields = [
            "id",
            "email",
            "domain",
            "mfa_enabled",
            "password_manager_used",
            "recovery_email_secured",
            "device_updates_current",
            "breach_monitoring_enabled",
            "privacy_exposure_reviewed",
            "score",
            "assessment_answers",
            "recommendations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "score", "recommendations", "created_at", "updated_at")
        extra_kwargs = {
            "email": {"validators": []},
        }

    def create(self, validated_data):
        score, recommendations = score_profile(validated_data)
        profile, _created = SecurityProfile.objects.update_or_create(
            email=validated_data["email"],
            defaults={
                **validated_data,
                "score": score,
                "recommendations": recommendations,
            },
        )
        return profile

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        score, recommendations = score_profile(
            {
                "mfa_enabled": instance.mfa_enabled,
                "password_manager_used": instance.password_manager_used,
                "recovery_email_secured": instance.recovery_email_secured,
                "assessment_answers": instance.assessment_answers,
            }
        )
        instance.score = score
        instance.recommendations = recommendations
        instance.save()
        return instance

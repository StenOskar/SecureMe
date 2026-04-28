from celery import shared_task

from .models import SecurityProfile
from .scoring import score_profile


@shared_task
def recalculate_profile_score(profile_id):
    profile = SecurityProfile.objects.get(id=profile_id)
    score, recommendations = score_profile(
        {
            "mfa_enabled": profile.mfa_enabled,
            "password_manager_used": profile.password_manager_used,
            "recovery_email_secured": profile.recovery_email_secured,
            "assessment_answers": profile.assessment_answers,
        }
    )
    profile.score = score
    profile.recommendations = recommendations
    profile.save(update_fields=["score", "recommendations", "updated_at"])
    return {"profile_id": profile.id, "score": score}

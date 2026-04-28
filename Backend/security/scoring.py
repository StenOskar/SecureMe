CHECKS = {
    "mfa_enabled": {
        "points": 25,
        "recommendation": "Enable MFA on your main email account and any account that can reset it.",
    },
    "password_manager_used": {
        "points": 20,
        "recommendation": "Use a password manager and replace reused passwords, starting with email and recovery accounts.",
    },
    "recovery_email_secured": {
        "points": 20,
        "recommendation": "Secure or remove recovery emails and phone numbers that could reset your account.",
    },
    "forwarding_rules_checked": {
        "points": 15,
        "recommendation": "Check email forwarding, filters, and app passwords for anything you do not recognize.",
    },
    "backup_codes_stored": {
        "points": 10,
        "recommendation": "Generate recovery codes and store them somewhere safe, not inside the same email inbox.",
    },
    "security_activity_reviewed": {
        "points": 10,
        "recommendation": "Review recent sign-ins and connected apps for unfamiliar access.",
    },
}

LEGACY_FIELDS = ("mfa_enabled", "password_manager_used", "recovery_email_secured")


def score_profile(values):
    answers = _answers_from_values(values)
    score = 0
    recommendations = []

    for field, check in CHECKS.items():
        answer = answers.get(field, "no")

        if answer == "yes":
            score += check["points"]
        elif answer in {"unsure", "unknown"}:
            score += round(check["points"] * 0.35)
            recommendations.append(f"Confirm this: {check['recommendation']}")
        else:
            recommendations.append(check["recommendation"])

    return min(score, 100), recommendations


def _answers_from_values(values):
    answers = dict(values.get("assessment_answers") or {})

    for field in LEGACY_FIELDS:
        if field not in answers and field in values:
            answers[field] = "yes" if values.get(field) else "no"

    return answers

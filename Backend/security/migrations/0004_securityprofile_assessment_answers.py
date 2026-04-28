from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("security", "0003_securityprofile_recovery_email_secured"),
    ]

    operations = [
        migrations.AddField(
            model_name="securityprofile",
            name="assessment_answers",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

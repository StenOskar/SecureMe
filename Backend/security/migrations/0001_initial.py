from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SecurityProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("mfa_enabled", models.BooleanField(default=False)),
                ("password_manager_used", models.BooleanField(default=False)),
                ("device_updates_current", models.BooleanField(default=False)),
                ("breach_monitoring_enabled", models.BooleanField(default=False)),
                ("privacy_exposure_reviewed", models.BooleanField(default=False)),
                ("score", models.PositiveSmallIntegerField(default=0)),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

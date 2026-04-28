from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("security", "0002_securityprofile_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="securityprofile",
            name="recovery_email_secured",
            field=models.BooleanField(default=False),
        ),
    ]

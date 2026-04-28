from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("security", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="securityprofile",
            name="domain",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-28 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0003_delete_bank"),
    ]

    operations = [
        migrations.AlterField(
            model_name="otp",
            name="otp_type",
            field=models.CharField(
                choices=[
                    ("password_reset", "password_reset"),
                    ("transaction", "transaction"),
                ],
                max_length=20,
            ),
        ),
    ]

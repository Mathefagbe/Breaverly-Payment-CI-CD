# Generated by Django 4.2.13 on 2024-06-26 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("beaverly_api", "0008_capyboostbalance_balance"),
    ]

    operations = [
        migrations.RenameField(
            model_name="capyboostbalance",
            old_name="pay_off_amount",
            new_name="loan_amount",
        ),
        migrations.RemoveField(
            model_name="capyboostbalance",
            name="balance",
        ),
    ]

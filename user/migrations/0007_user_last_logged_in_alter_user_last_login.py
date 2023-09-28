# Generated by Django 4.2.5 on 2023-09-26 19:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0006_alter_user_last_login"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_logged_in",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_login",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="last login"
            ),
        ),
    ]

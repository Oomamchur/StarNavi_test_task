# Generated by Django 4.2.5 on 2023-09-27 13:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0008_remove_user_last_logged_in_dislike"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_activity",
            field=models.DateTimeField(null=True),
        ),
    ]

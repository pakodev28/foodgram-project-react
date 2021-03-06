# Generated by Django 3.2 on 2021-11-29 21:39

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="follow",
            options={
                "verbose_name": "Подписка",
                "verbose_name_plural": "Подписки",
            },
        ),
        migrations.AlterUniqueTogether(
            name="follow",
            unique_together={("user", "author")},
        ),
    ]

# Generated by Django 3.2 on 2021-11-23 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_alter_ingridient_measurement_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingridient",
            name="measurement_unit",
            field=models.CharField(
                max_length=60, verbose_name="Еденицы измерения"
            ),
        ),
    ]

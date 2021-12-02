# Generated by Django 3.2 on 2021-11-23 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingridient",
            name="measurement_unit",
            field=models.CharField(
                choices=[
                    (1, "г"),
                    (2, "стакан"),
                    (3, "по вкусу"),
                    (4, "ст. л."),
                    (5, "шт."),
                    (6, "мл"),
                    (7, "ч. л."),
                    (8, "капля"),
                    (9, "звездочка"),
                    (10, "щепотка"),
                    (11, "горсть"),
                    (12, "кусок"),
                    (13, "кг"),
                    (14, "пакет"),
                    (15, "пучок"),
                    (16, "долька"),
                    (17, "банка"),
                    (18, "упаковка"),
                    (19, "зубчик"),
                    (20, "пласт"),
                    (21, "пачка"),
                    (22, "тушка"),
                    (23, "стручок"),
                    (24, "веточка"),
                    (25, "бутылка"),
                    (26, "л"),
                    (27, "батон"),
                    (28, "пакетик"),
                    (29, "лист"),
                    (30, "стебель"),
                ],
                max_length=20,
                verbose_name="Еденицы измерения",
            ),
        ),
    ]
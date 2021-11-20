from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingridient(models.Model):

    MEASUREMENT_UNIT_CHOICES = [
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
    ]

    name = models.CharField(
        max_length=60,
        unique=True,
        null=False,
        blank=False,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=20,
        choices=MEASUREMENT_UNIT_CHOICES,
        default=1,
        verbose_name="Еденицы измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=60, unique=True, null=False, blank=False, verbose_name="Тег"
    )
    color = ColorField(default="#FF0000")
    slug = models.SlugField(
        max_length=60,
        unique=True,
        null=False,
        blank=False,
    )

    class Meta:
        ordering = ["slug"]
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe",
    )
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to="media/", verbose_name="Фотография готового блюда"
    )
    text_description = models.TextField(verbose_name="Описание блюда")
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления блюда",
    )
    ingridients = models.ManyToManyField(
        Ingridient, through="IngridientInRecipe", verbose_name="Ингредиенты"
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipe", verbose_name="Теги"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngridientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingridient_in_recipe"
    )
    ingridient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name="ingridient_in_recipe",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"

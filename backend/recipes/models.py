from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):

    name = models.CharField(
        max_length=60,
        unique=True,
        null=False,
        blank=False,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=60,
        verbose_name="Еденицы измерения",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return "{}, {}".format(self.name, self.measurement_unit)


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
        Ingredient, through="IngridientInRecipe", verbose_name="Ингредиенты"
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
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingridient_in_recipe",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


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
        verbose_name_plural = "Избранное"


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
        verbose_name_plural = "Списки покупок"

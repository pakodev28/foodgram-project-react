from django.contrib import admin

from .models import Ingredient, Tag, Recipe, Favorite, ShoppingCart


class IngredientAdmin(admin.ModelAdmin):
    list_dispaly = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "color",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class IngredientInRecipeInLine(admin.TabularInline):
    model = Recipe.ingridients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_dispaly = (
        "name",
        "author",
    )
    inlines = (IngredientInRecipeInLine,)
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)

from django.contrib import admin

from .models import Ingredient, Tag, Recipe, Favorite, ShoppingCart


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
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
    model = Recipe.ingredients.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "favorite_count",
    )
    inlines = (IngredientInRecipeInLine,)
    list_filter = (
        "name",
        "author",
        "tags",
    )
    empty_value_display = "-пусто-"

    @admin.display(description="В избранном")
    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe",
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

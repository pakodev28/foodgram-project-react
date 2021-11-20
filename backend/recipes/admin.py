from django.contrib import admin

from .models import Ingridient, Tag, Recipe


class IngridientAdmin(admin.ModelAdmin):
    list_dispaly = ("name", "measurement_unit",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class RecipeAdmin(admin.ModelAdmin):
    list_dispaly = ("name", "author",)
    list_filter = ("name", "author", "tags",)
    empty_value_display = "-пусто-"


admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)

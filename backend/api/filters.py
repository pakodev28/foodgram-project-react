import django_filters as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):

    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )

    class Meta:
        model = Ingredient
        fields = [
            "name",
            "measurement_unit",
        ]


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug", conjoined=False
    )
    is_favorited = filters.BooleanFilter(
        method="is_favorited",
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method="is_in_shopping_cart",
    )

    def is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_favorite__user=self.request.user)
        return queryset

    def is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                recipe_shopping_cart__user=self.request.user
            )
        return queryset

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

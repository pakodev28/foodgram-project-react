from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteView, FollowView, IngredientViewSet, MyUserViewSet,
                    RecipeViewSet, ShoppingCartView, TagViewSet)

app_name = "api"

router = DefaultRouter()
router.register("users", MyUserViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)

urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "recipes/<int:id>/favorite/",
        FavoriteView.as_view(),
        name="favorite",
    ),
    path(
        "recipes/<int:id>/shopping_cart/",
        ShoppingCartView.as_view(),
        name="shopping_cart",
    ),
    path(
        "users/subscriptions/",
        FollowView.as_view(),
        name="subscriptions",
    ),
    path("", include(router.urls)),
]

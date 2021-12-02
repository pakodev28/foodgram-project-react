from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, TagViewSet

app_name = "api"

router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredient", IngredientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

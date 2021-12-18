from django.contrib.auth import get_user_model
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet)

from recipes.models import (Favorite, Ingredient, IngridientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FolllowSerializer,
                          IngredientSerializer, MyUserSerializer,
                          RecipeGetSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserRegistrationSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    search_fields = ("^name",)
    filterset_class = IngredientFilter
    permission_classes = (IsAdminOrReadOnly,)


class MyUserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [
        permissions.AllowAny,
    ]

    def get_serializer_class(self):
        if self.action == "set_password":
            return SetPasswordSerializer
        elif self.action == "me":
            return MyUserSerializer
        elif self.action == "create":
            return UserRegistrationSerializer
        return self.serializer_class

    @action(
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        detail=False,
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data["new_password"]
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get", "delete"],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path="subscribe",
    )
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if request.method == "GET":
            instance = Follow.objects.create(author=author, user=request.user)
            serializer = FolllowSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        instance = Follow.objects.filter(author=author, user=request.user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        obj = Favorite.objects.filter(user=request.user, recipe_id=id).exists()
        if obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe_id=id)

        serialized = FavoriteSerializer(get_object_or_404(Recipe, id=id))
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id=None):
        obj = Favorite.objects.filter(user=request.user, recipe_id=id).exists()
        if not obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=request.user, recipe_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None):
        obj = ShoppingCart.objects.filter(
            user=request.user, recipe_id=id
        ).exists()
        if obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=request.user, recipe_id=id)

        serialized = ShoppingCartSerializer(get_object_or_404(Recipe, id=id))
        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id=None):
        obj = ShoppingCart.objects.filter(
            user=request.user, recipe_id=id
        ).exists()
        if not obj:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user=request.user, recipe_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = FolllowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]

    def get_queryset(self):
        return User.objects.filter(follow__user=self.request.user)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeGetSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        res_queryset = {}
        queryset = IngridientInRecipe.objects.filter(
            recipe__shopping_cart__user__id=request.user.id
        ).values_list(
            "ingredient__name",
            "ingredient__measurement_unit",
            "amount",
            named=True,
        )
        for amount in queryset:
            name = (
                amount.ingredient__name,
                amount.ingredient__measurement_unit,
            )
            if name in res_queryset:
                res_queryset[name] += amount.amount
            else:
                res_queryset[name] = amount.amount
        rows = (
            [ingredient[0], str(res_queryset[ingredient]), ingredient[1], "\n"]
            for ingredient in res_queryset
        )
        inputs = (", ".join(row) for row in rows)

        response = StreamingHttpResponse(inputs, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="recipes.txt"'
        return response

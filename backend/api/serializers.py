from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngridientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow

from .fields import Base64ImageField

User = get_user_model()


class MyUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=obj).exists()
        )


class UserRegistrationSerializer(UserCreateSerializer):
    email = serializers.EmailField(allow_blank=False)
    first_name = serializers.CharField(allow_blank=False)
    last_name = serializers.CharField(allow_blank=False)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeSimpleSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FavoriteSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    image = Base64ImageField(source="recipe.image", read_only=True)
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Favorite
        fields = ("id", "name", "image", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source="recipe.id")
    name = serializers.ReadOnlyField(source="recipe.name")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")
    image = Base64ImageField(read_only=True, source="recipe.image")

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "name",
            "cooking_time",
            "image",
        )


class FolllowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_recipes(self, obj):
        return RecipeSimpleSerializer(obj.recipe.all(), many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, author):
        user = self.context["request"].user
        return Follow.objects.filter(
            author__id=author.id, user__id=user.id
        ).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ("user", "author")


class IngredientsInRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngridientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = IngredientsInRecipeGetSerializer(
        many=True, source="ingridient_in_recipe"
    )
    author = MyUserSerializer(many=False)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context["request"].user.id, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user=self.context["request"].user.id, recipe=obj.id
        ).exists()


class IngridientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    ingredients = IngridientInRecipeCreateSerializer(many=True)
    author = MyUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "author",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get("ingredients")
        ingredients_set = set()
        if not ingredients:
            raise serializers.ValidationError(
                "Вы не добавили не одного ингредиента"
            )
        for ingredient in ingredients:
            if int(ingredient["amount"]) < 1:
                raise serializers.ValidationError(
                    "Вы указали колличество меньше 1"
                )
            id = ingredient.get("id")
            ingredients_set.add(id)
        return data

    def validate_tags(self, data):
        tags_set = set()
        if not data:
            raise serializers.ValidationError("Вы не указали ни одного тэга")
        for tag in data:
            if tag in tags_set:
                raise serializers.ValidationError(
                    "Вы указали два одинаковых тэга"
                )
            tags_set.add(tag)
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                "Время готовки должно быть больше нуля!"
            )
        return data

    def create_ingridients(self, ingredients, recipe):
        for ingredient in ingredients:
            instance = get_object_or_404(Ingredient, id=ingredient["id"])
            amount = ingredient["amount"]
            if IngridientInRecipe.objects.filter(
                recipe=recipe, ingredient=instance
            ).exists():
                amount += F("amount")
            IngridientInRecipe.objects.update_or_create(
                recipe=recipe, ingredient=instance, defaults={"amount": amount}
            )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingridients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        if "ingredients" in self.initial_data:
            instance.ingredients.clear()
            self.create_ingridients(ingredients, instance)

        if "tags" in self.initial_data:
            instance.tags.set(tags)

        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        data = RecipeGetSerializer(
            instance, context={"request": self.context.get("request")}
        ).data
        return data

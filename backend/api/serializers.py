from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    IngridientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
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
            and Follow.objects.filter(user=user, author=obj.id).exists()
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


class IngridientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(read_only=True, source="ingredients.name")
    measurement_unit = serializers.CharField(
        read_only=True, source="ingredients.measurement_unit"
    )

    class Meta:
        model = IngridientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngridientInRecipeGetSerializer(serializers.ModelSerializer):
    id = IngredientSerializer()
    name = serializers.CharField(required=False)
    measurement_unit = serializers.IntegerField(required=False)
    amount = serializers.IntegerField()

    class Meta:
        model = IngridientInRecipe
        fields = ("id", "amount", "name", "measurement_unit")

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data["amount"] = instance.amount
        return data


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
        if self.context["request"].query_params.get("recipes_limit"):
            count = int(self.context.GET["recipes_limit"])
            data = Recipe.objects.filter(author=obj).all()[:count]
        else:
            data = Recipe.objects.filter(author=obj).all()
        serializers = FavoriteSerializer(data, many=True)
        return serializers.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return Follow.objects.filter(author=obj, user=request.user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngridientInRecipeSerializer(
        many=True, source="ingridient_in_recipe"
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
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

    def create_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            instance = get_object_or_404(Ingredient, id=ingredient["id"].id)
            IngridientInRecipe.objects.get_or_create(
                ingredient=instance, recipe=recipe, amount=ingredient["amount"]
            )
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingridient_in_recipe")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe = self.create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingridient_in_recipe")
        instance.name = validated_data["name"]
        instance.text = validated_data["text"]
        instance.cooking_time = validated_data["cooking_time"]
        instance.tags.set(tags)
        instance.ingredients.clear()
        instance = self.create_ingredient(ingredients, instance)
        instance.save()
        return instance


class RecipeGetSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngridientInRecipeGetSerializer(
        many=True, source="ingridient_in_recipe"
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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


class SubscribeSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ("user", "author")

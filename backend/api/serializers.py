from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredient,
    IngridientInRecipe,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart,
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
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngridientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")
        validators = [
            UniqueTogetherValidator(
                queryset=IngridientInRecipe.objects.all(),
                fields=["ingredient", "recipe"],
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
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
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )

    def create(self, validated_data):

        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.get_or_create(**validated_data)
        recipe.save()
        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngridientInRecipe.objects.create(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):

        ingredients = validated_data.pop("ingredients")
        IngridientInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop("tags")

        for ingredient in ingredients:
            IngridientInRecipe.objects.create(
                ingredient=get_object_or_404(Ingredient, id=ingredient["id"]),
                recipe=instance,
                amount=ingredient["amount"],
            )

        instance.name = validated_data.pop("name")
        instance.text = validated_data.pop("text")
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.pop("cooking_time")
        instance.tags.set(tags)
        return super().update(instance, validated_data)

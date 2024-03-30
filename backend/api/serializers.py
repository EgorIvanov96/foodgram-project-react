import re

from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers, status
from reviews.models import (Favorite, Ingredient, Recipe, IngredientRecipes,
                            ShoppingList, Tag)
from users.models import Follow, User

from .constans import MIN, MAX


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, instance):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=instance).exists()

    def validate_username(self, data):
        if not re.match(r'^[\w.@+-]+\Z`', data):
            raise serializers.ValidationError(
                'Поле username содержит недопустимые символы.'
            )
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError('Пользователь с таким username '
                                              'уже существует.')

        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError('Пользователь с таким email '
                                              'уже существует.')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(
        source='ingredient.name',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = IngredientRecipes
        fields = ('amount', 'name', 'measurement_unit', 'id')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецептов."""

    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer()
    tags = TagSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_in_shopping_cart',
            'is_favorited'
        )

    def get_is_favorited(self, instance):
        request = self.context.get('request')
        return (request.user.is_authenticated and instance.favorites.filter(
            user=request.user
        ).exists())

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get('request')
        return (
            request.user.is_authenticated and instance.shopping_list.filter(
                user=request.user
            ).exists()
        )


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов в рецепт и кол-во."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MIN,
        max_value=MAX
    )

    class Meta:
        model = IngredientRecipes
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    ingredients = IngredientCreateInRecipeSerializer(many=True)
    image = Base64ImageField(allow_null=True, allow_empty_file=True)
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(min_value=MIN)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, date):
        ingredients = date.get('ingredients')
        tags = date.get('tags')
        image = date.get('get')

        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте ингредиенты.'
            )
        if not tags:
            raise serializers.ValidationError(
                'Добавьте хотя бы один тег.'
            )
        if not image:
            serializers.ValidationError(
                'Добавьте изображение блюда.'
            )
        ingredients_count = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_count) != len(set(ingredients_count)):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые ингредиенты'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Нельзя добавлять одинаковые теги.'
            )

        return date

    @staticmethod
    def recipe_ingredient_create(ingredients_data, recipe):
        IngredientRecipes.objects.bulk_create(
            [
                IngredientRecipes(
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount'],
                    recipe=recipe
                ) for ingredient in ingredients_data
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredient_create(ingredients_data=ingredients_data,
                                      recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        IngredientRecipes.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        self.recipe_ingredient_create(ingredients_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance,
                                    context=context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time',
            'image'
        )


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes',
                                                     'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя',
                status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя',
                status.HTTP_400_BAD_REQUEST)
        return data

    def get_recipes(self, instance):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = instance.recipes.all()
        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    """def get_recipes_count(self, instance):
        return Recipe.objects.filter(author__id=instance.id).count()"""


class FollowCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Подписаться на себя невозможно.'
            )
        if Follow.objects.filter(
                user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                'Повторная подписка на автора невозможна.'
            )
        return data


class BaseCreateSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context).data


class FavoriteCreateSerializer(BaseCreateSerializer):
    """Сериализатор модели избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт в избранное.'
            )
        ]


class ShoppingListCreateSerializer(BaseCreateSerializer):
    """Сериализатор модели список покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт в списке покупок.'
            )
        ]

from drf_base64.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers

from reviews.models import (Favorite, Ingredient, Recipe, IngredientRecipes,
                            ShoppingList, Tag)
from users.models import Follow, User

from .constans import MIN, MAX


class UserSerializer(serializers.ModelSerializer):
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
        request = self.context['request']
        user = request.user

        return user.is_authenticated and user.follower.filter(
            author=instance).exists()


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
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit',
        read_only=True
    )

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
    author = UserSerializer()
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

    ingredients = IngredientCreateInRecipeSerializer(many=True,
                                                     write_only=True)
    image = Base64ImageField(allow_null=True, allow_empty_file=True)
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    cooking_time = serializers.IntegerField(min_value=MIN, max_value=MAX)

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

        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте ингредиенты.'}
            )
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Добавьте хотя бы один тег.'}
            )
        ingredients_count = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_count) != len(set(ingredients_count)):
            raise serializers.ValidationError(
                {'ingredients': 'Нельзя добавлять одинаковые ингредиенты'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Нельзя добавлять одинаковые теги.'}
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


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes',
                                               'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, instance):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        recipes = instance.recipes.all()
        try:
            if recipes_limit:
                recipes = recipes[:int(recipes_limit)]
        except ValueError:
            pass
        return RecipeShortSerializer(recipes, many=True).data


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

    def to_representation(self, instance):
        return FollowSerializer(
            instance=instance.author,
            context=self.context).data


class BaseCreateSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe, context=self.context).data

    def validate_unique_together(self, attrs, serializer):
        queryset = self.Meta.model.objects.all()
        fields = self.Meta.fields
        message = self.Meta.message
        validator = UniqueTogetherValidator(
            queryset=queryset,
            fields=fields,
            message=message
        )
        validator.set_context(serializer)
        validator(attrs)


class FavoriteCreateSerializer(BaseCreateSerializer):
    """Сериализатор модели избранное."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        message = 'Рецепт в избранном.'


class ShoppingListCreateSerializer(BaseCreateSerializer):
    """Сериализатор модели список покупок."""

    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')
        message = 'Рецепт в списке покупок.'

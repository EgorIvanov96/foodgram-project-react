from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from reviews.models import Tag, Ingredient, Recipes, IngredientRecipes
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.BooleanField()
    """Отображение user."""
    is_subscribed = serializers.BooleanField(default=False)

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
        read_only_fields = ('id', 'is_subscribed')


class UserCreateSerializer(UserCreateSerializer):
    """Регисрация пользователя."""
    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password')
        read_only_fields = ('id',)

    def validate(self, data):
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError('Пользователь с таким username '
                                              'уже существует.')

        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError('Пользователь с таким email '
                                              'уже существует.')
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для связи модели  Рецепта с Игредиентом"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
        )
    # ingredient = IngredientsSerializer()

    class Meta:
        model = IngredientRecipes
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount'
                  )


class RecipsSerializer(serializers.ModelSerializer):
    """GET: список и отдельный рецепт"""
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientRecipesSerializer(source='recip', many=True)
    is_favorited = serializers.BooleanField(default=True)
    is_in_shopping_cart = serializers.BooleanField(default=True)

    class Meta:
        model = Recipes
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField

from users.models import User
from .constants import (
    MEDIUM_LENGTH, MAX_COLOR, MIN, MAX
)


class Tag(models.Model):
    """Теги."""

    name = models.CharField(
        max_length=MEDIUM_LENGTH,
        verbose_name='Тег',
        unique=True)
    color = ColorField(
        max_length=MAX_COLOR,
        verbose_name='Цвет',
        default='#hhhhhh')
    slug = models.SlugField(
        max_length=MEDIUM_LENGTH,
        verbose_name='Slug',
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        max_length=MEDIUM_LENGTH,
        verbose_name='Ингредиент')
    measurement_unit = models.CharField(
        max_length=MEDIUM_LENGTH,
        verbose_name='Единицы измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit')
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта')

    name = models.CharField(
        max_length=MEDIUM_LENGTH,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        help_text='Прикрепите фото рецепта')
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(мин)',
        help_text='Время приготовления',
        validators=[
            MinValueValidator(
                MIN, f'Время приготовления должно быть больше {MIN} мин.'
            ),
            MaxValueValidator(
                MAX, f'Время приготовления должно быть меньше {MAX} мин.'
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'name'),
                name='unique_author_name'
            )
        ]

    def __str__(self):
        return f'{self.author} - {self.name}'


class IngredientRecipes(models.Model):
    """Связь между ингредиентами и рецептами."""

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN, f'Количество ингредиентов должно быть больше {MIN}.'
            ),
            MaxValueValidator(
                MAX, f'Количество ингредиентов должно быть меньше {MAX}.'
            )
        ]
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes')
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients')

    class Meta:
        verbose_name = 'Состав рецепта'
        verbose_name_plural = 'Состав рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredients_recipe'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class RecipUserBase(models.Model):
    """Абстрактный класс для моделей избранных и список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Ползователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.recipe} {self._meta.verbose_name} у {self.user}'


class Favorite(RecipUserBase):
    """Избранное."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            ),
        ]


class ShoppingList(RecipUserBase):
    """Список покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_list'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe'
            ),
        ]

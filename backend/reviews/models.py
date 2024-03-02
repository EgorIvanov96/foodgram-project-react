from typing import Optional

from django.core.validators import MinValueValidator, validate_slug
from django.db import models

from users.models import User


class Tag(models.Model):
    """Тег"""

    name = models.CharField(max_length=200,
                            verbose_name='Тег',
                            blank=False,
                            unique=True)
    color = models.CharField(max_length=7,
                             verbose_name='Цвет',
                             blank=False,
                             default='#hhhhhh')
    slug = models.SlugField(max_length=200,
                            verbose_name='Slug',
                            unique=True,
                            blank=False)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты."""
    name = models.CharField(max_length=200,
                            verbose_name='Ингредиент',
                            blank=False)
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единицы измерения',
                                        blank=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id: Optional[int]):
        return self.annotate(
            is_favorited=models.Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=models.OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):
    """Рецепты."""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=False,
                               related_name='recipes',
                               verbose_name='Автор рецепта')

    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта',
                            blank=False,
                            help_text='Введите название рецепта')
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='recipes',
                              blank=False,
                              help_text='Прикрепите фото рецепта2')
    text = models.TextField(verbose_name='Описание рецепта',
                            blank=False,
                            help_text='Введите описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='IngredientRecipes',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(Tag,
                                  blank=False,
                                  related_name='recipes',
                                  verbose_name='Теги',
                                  help_text='Выберите теги')
    cooking_time = models.IntegerField(verbose_name='Время приготовления(мин)',
                                       blank=False,
                                       help_text='Время приготовления')
    objects = RecipeQuerySet.as_manager()
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        unique_together = ('author', 'name')

    def __str__(self):
        return f'{self.author} - {self.name}'


class IngredientRecipes(models.Model):
    """Связь между ингредиентами и рецептами."""
    amount = models.PositiveSmallIntegerField(blank=False,
                                              verbose_name='Количество')
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipes')
    recipe = models.ForeignKey(Recipe,
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


class Favorite(models.Model):
    """Избранное."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='user_favorites',
                             verbose_name='Ползователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               null=True,
                               related_name='favorites',
                               verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            ),
        ]

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingList(models.Model):

    user = models.ForeignKey(User,
                             verbose_name='Покупатель',
                             on_delete=models.CASCADE,
                             related_name='shopping_list')
    recipe = models.ForeignKey(Recipe,
                               verbose_name='Рецепт к покупке',
                               on_delete=models.CASCADE,
                               related_name='shopping_list')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe'
            ),
        ]

    def __str__(self):
        return f'Корзина пользователя {self.user}'

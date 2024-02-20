from django.db import models

from users.models import User


class Tag(models.Model):
    """Тег"""
    name = models.CharField(max_length=200,
                            verbose_name='Тег',
                            unique=True
                            )
    color = models.CharField(max_length=7,
                             verbose_name='Цвет',
                             unique=True
                             )
    slug = models.SlugField(max_length=200,
                            verbose_name='Slug',
                            unique=True
                            )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингредиенты."""
    name = models.CharField(max_length=200,
                            verbose_name='Ингридиенты',
                            unique=True
                            )
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единицы измерения',
                                        )

    class Meta:
        verbose_name = 'ингредиенты'
        verbose_name_plural = 'Ингредиент'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipes(models.Model):
    """Рецепты."""
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               on_delete=models.CASCADE,
                               blank=False
                               )
    name = models.CharField(max_length=200,
                            verbose_name='Название рецепта',
                            unique=True,
                            blank=False
                            )
    image = models.ImageField(upload_to='recipes', verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание рецепта',
                            blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipes',
        through_fields=('recipes', 'ingredient'),
        verbose_name='Ингредиенты',
        related_name='ingredients_recipes'
        )
    tags = models.ManyToManyField(Tag, verbose_name='Тег',
                                  blank=False,
                                  related_name='tags')
    cooking_time = models.IntegerField(verbose_name='Время проготовления(мин)',
                                       blank=False)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        unique_together = ('author', 'name')

    def __str__(self):
        return f'{self.author} - {self.name}'


class IngredientRecipes(models.Model):
    amount = models.IntegerField(verbose_name='Количество')
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name='Ингредиент',
                                   on_delete=models.CASCADE)
    recipes = models.ForeignKey(Recipes,
                                verbose_name='Рецепт',
                                on_delete=models.CASCADE,
                                related_name='recip')

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        unique_together = ('recipes', 'ingredient')

    def __str__(self):
        return f'{self.ingredient} в {self.recipes}'

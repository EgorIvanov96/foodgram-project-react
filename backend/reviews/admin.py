from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, IngredientRecipes,
                     ShoppingList, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientRecipes
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    list_display = ('name', 'author',
                    'favorites_count', 'get_ingredients_display')
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    exclude = ('ingredients',)

    @admin.display(description='Добавлено в избранное')
    def favorites_count(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" width="80" height="60">')

    @admin.display(description='Изображение')
    def get_img(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description='Ингредиенты')
    def get_ingredients_display(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(ShoppingList)
admin.site.register(Favorite)

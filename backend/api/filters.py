from django_filters import CharFilter, AllValuesMultipleFilter, BooleanFilter
from django_filters.rest_framework import FilterSet

from reviews.models import Recipe, Ingredient


class RecipeFilter(FilterSet):
    """Фильтр по рецептам."""
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    author = CharFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['tags', 'is_favorited', 'is_in_shopping_cart', 'author']

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр по ингредиентам."""
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']

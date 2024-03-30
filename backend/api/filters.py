from django_filters.rest_framework import filters
from django_filters.rest_framework import FilterSet

from reviews.models import Recipe, Ingredient, Tag


class IngredientFilter(FilterSet):
    """Фильтр по ингредиентам."""

    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """"Фильтр по тега, авторам, избранном и спискам покупок."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_by_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_by_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset

    def filter_by_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

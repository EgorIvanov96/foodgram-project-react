from django_filters import CharFilter, BooleanFilter, ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet

from reviews.models import Recipe, Ingredient, Tag


class RecipeFilter(FilterSet):
    """
    Фильтр для рецептов.
    """

    is_in_shopping_cart = BooleanFilter(method="filter_by_shopping_cart")
    is_favorited = BooleanFilter(method="filter_by_favorited")
    author = CharFilter()
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all()
    )

    def filter_by_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list=self.request.user)
        return queryset

    def filter_by_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags", "is_in_shopping_cart", "is_favorited")


class IngredientFilter(FilterSet):
    """Фильтр по ингредиентам."""
    name = CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']

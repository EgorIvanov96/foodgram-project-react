from django.db.models import Sum, Count
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        SAFE_METHODS)
from rest_framework.response import Response

from reviews.models import (Favorite, Ingredient, Recipe, IngredientRecipes,
                            ShoppingList, Tag)
from users.models import Follow, User
from .serializers import (UserSerializer, FollowCreateSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          TagSerializer, FavoriteCreateSerializer,
                          ShoppingListCreateSerializer)
from .filters import RecipeFilter, IngredientFilter
from .pagination import Paginator
from .permissions import IsAuthorOrReadOnly


class UserCustomViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all()
    pagination_class = Paginator
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ('me', 'subscriptions', 'subscribe'):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        following_users = User.objects.filter(
            following__user=self.request.user
        ).annotate(
            recipes_count=Count('recipes'))
        paginated_queryset = self.paginate_queryset(following_users)
        serializer = FollowSerializer(
            paginated_queryset,
            context={'request': request},
            many=True
        )
        if paginated_queryset is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        url_path='subscribe',
        methods=('post',),
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id):
        serializer = FollowCreateSerializer(
            data={
                'user': request.user.id,
                'author': id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        follow_instance = Follow.objects.filter(
            user=request.user, author=id).first()
        if follow_instance:
            follow_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'ingredients')
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = Paginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def add_recipes(request, serializer, pk):
        """Статический метод для POST запроса."""
        serializer = serializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipes(request, model, pk):
        """Статический метод для DELETE запроса."""

        delete_instanse = model.objects.filter(user=request.user,
                                               recipe=pk).first()
        if delete_instanse:
            delete_instanse.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.add_recipes(request, FavoriteCreateSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        return self.delete_recipes(request, Favorite, **kwargs)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.add_recipes(request, ShoppingListCreateSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self.delete_recipes(request, ShoppingList, **kwargs)

    @staticmethod
    def creating_shopping_list(ingredients):
        purchased = ['Список покупок:', ]
        for item in ingredients:
            purchased.append(
                f"{item['ingredient__name']}: {item['amount_of_item']}, "
                f"{item['ingredient__measurement_unit']}"
            )
        purchased_file = "\n".join(purchased)
        return purchased_file

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipes.objects.filter(
            recipe__shopping_list__user=self.request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount_of_item=Sum('amount')).order_by('ingredient__name')
        purchased_list = self.creating_shopping_list(ingredients)
        response = FileResponse(purchased_list, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response

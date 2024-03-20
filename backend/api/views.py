from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from reviews.models import (Favorite, Ingredient, Recipe, IngredientRecipes,
                            ShoppingList, Tag)
from users.models import Follow, User

from .serializers import (CustomUserSerializer,
                          FollowCreateSerializer, FollowSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeListSerializer,
                          TagSerializer, FavoriteRecipeSerializer)
from .filters import RecipeFilter, IngredientFilter


class CustomPaginator(pagination.PageNumberPagination):
    page_size_query_param = 'limit'


class UserCustomViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPaginator
    serializer_class = CustomUserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        following_users = User.objects.filter(
            following__user=self.request.user
        )
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
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        serializer_class=FollowSerializer
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowCreateSerializer(
                data={
                    'user': request.user.id,
                    'author': id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=self.request.user)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = Follow.objects.filter(user=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(
                {'message': 'Вы отписались от автора.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'message': 'Вы не были подписаны на автора'},
            status=status.HTTP_400_BAD_REQUEST
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=True, url_path='favorites',
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        """Метод для добавления и удаления рецепта в избранное."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'favorite'
            }
        )
        if request.method == 'POST':
            if serializer.is_valid():
                Favorite.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        if request.method == 'DELETE':
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='cart',
            methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        """Метод для добавления и удаления рецепта в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={
                'request': request,
                'action_name': 'shopping_cart'
            }
        )
        if request.method == 'POST' and serializer.is_valid():
            ShoppingList.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            ShoppingList.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipes.objects.filter(
            recipe__shopping_list__user=self.request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            amount_of_item=Sum('amount'))
        purchased = [
            "Список покупок:",
        ]
        for item in ingredients:
            purchased.append(
                f"{item['ingredient__name']}: {item['amount_of_item']}, "
                f"{item['ingredient__measurement_unit']}"
            )
        purchased_file = "\n".join(purchased)

        response = HttpResponse(purchased_file, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=shopping-list.txt'
        )
        return response

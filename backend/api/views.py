from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .serializers import (TagSerializer, UserCreateSerializer,
                          UserSerializer, IngredientsSerializer, RecipsSerializer)
from reviews.models import Tag, Ingredient, Recipes
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        elif self.action == 'me':
            return UserSerializer

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = request.user
        if not user.check_password(current_password):
            return Response({'error': 'Invalid current password'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Теги"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = IsAdminUser


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    lookup_field = 'name'
    # permission_classes = IsAdminUser

    """ Посиск ингредиентоыв по названию
    def get_queryset(self):
        query = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__startswith=query)
        return queryset"""


class RecipsViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipsSerializer

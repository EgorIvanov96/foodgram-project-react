from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.core.validators import RegexValidator

from .constants import MAX_LENGTH_EMAIL, LENGHT_FIELDS


class User(AbstractUser):
    """Модель пользоветеля."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL, unique=True,
        verbose_name='e-mail',
        help_text='Укажите свой e-mail')
    username = models.CharField(
        max_length=LENGHT_FIELDS,
        verbose_name='Никнейм пользователя',
        help_text='Укажите никнейм',
        validators=[
            RegexValidator(
                r'^[\w.@+-]+\Z',
                'Поле username содержит недопустимые символы.'
            )])
    first_name = models.CharField(
        max_length=LENGHT_FIELDS, blank=True,
        verbose_name='Имя пользователя',
        help_text='Укажите имя пользователя')
    last_name = models.CharField(
        max_length=LENGHT_FIELDS, blank=True,
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию пользователя')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following'
            ),
            models.CheckConstraint(
                check=(~Q(user=F('author'))),
                name='no_self_following'
            )
        ]

    def __str__(self):
        return f"{self.user} подписчик - {self.author}"

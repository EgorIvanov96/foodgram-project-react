from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q

class User(AbstractUser):
    """Модель пользоветеля"""
    email = models.EmailField(max_length=254, unique=True,
                              verbose_name='e-mail',
                              help_text='Укажите свой e-mail')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    username = models.CharField(max_length=150, blank=True,
                                verbose_name='Никнейм пользователя',
                                help_text='Укажите никнейм')
    first_name = models.CharField(max_length=150, blank=True,
                                  verbose_name='Имя пользователя',
                                  help_text='Укажите имя пользователя')
    last_name = models.CharField(max_length=150, blank=True,
                                 verbose_name='Фамилия пользователя',
                                 help_text='Укажите фамилию пользователя')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
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

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import IsPublishedAbsract, CreatedAt
from .const import MAX_CHARFIELD_LENGTH, MAX_DISPLAY_LENGTH

User = get_user_model()


class Category(IsPublishedAbsract, CreatedAt):
    title = models.CharField(
        help_text='Максимальная длина строки — 256 символов',
        max_length=MAX_CHARFIELD_LENGTH,
        verbose_name='Заголовок',
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        help_text='Идентификатор страницы для URL; разрешены '
        'символы латиницы, цифры, дефис и подчёркивание.',
        verbose_name='Идентификатор',
        unique=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:MAX_DISPLAY_LENGTH]


class Location(IsPublishedAbsract, CreatedAt):
    name = models.CharField(
        help_text='Максимальная длина строки — 256 символов',
        max_length=MAX_CHARFIELD_LENGTH,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:MAX_DISPLAY_LENGTH]


class Post(IsPublishedAbsract, CreatedAt):
    title = models.CharField(
        help_text='Максимальная длина строки — 256 символов',
        max_length=MAX_CHARFIELD_LENGTH,
        verbose_name='Заголовок',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.',
        default=timezone.now,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        related_name='posts',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        related_name='posts',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
    )
    image = models.ImageField(
        upload_to="images",
        blank=True,
        null=True,
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.title[:MAX_DISPLAY_LENGTH]


class Comment(CreatedAt):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self) -> str:
        return self.text[:20]

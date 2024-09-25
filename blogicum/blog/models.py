from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone as dt

User = get_user_model()

TITLE_LETTER_LIMIT = 30


class PublishModel(models.Model):
    """Абстрактная модель с 'is_published' и 'created_at'"""

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(PublishModel):
    """Модель с категориями"""

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField('Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_LETTER_LIMIT]


class Location(PublishModel):
    """Модель с местоположениями"""

    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TITLE_LETTER_LIMIT]


class Post(PublishModel):
    """Модель с постами"""

    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время'
            ' в будущем — можно делать отложенные публикации.'
        ),
        default=dt.localtime,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField('Фото', upload_to='posts_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:TITLE_LETTER_LIMIT]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.id})


class Comment(models.Model):
    """Модель комментария"""

    text = models.TextField(
        'Текст комментария',
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Публикация',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('created_at',)
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:TITLE_LETTER_LIMIT]

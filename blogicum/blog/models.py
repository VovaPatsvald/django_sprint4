from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

User = get_user_model()


class MyUser(AbstractUser):
    bio = models.TextField('Биография', blank=True)

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.username

    def __str__(self):
        return self.get_full_name()


class BaseBlogModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True,)

    class Meta:
        abstract = True
        ordering = ('created_at',)


class Category(BaseBlogModel):
    title = models.CharField('Заголовок', max_length=settings.MAX_FIELD_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        ),
        unique=True
    )

    class Meta(BaseBlogModel.Meta):

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:settings.REPRESENTATION_LENGHT]


class Location(BaseBlogModel):
    name = models.CharField('Название места',
                            max_length=settings.MAX_FIELD_LENGTH)

    class Meta(BaseBlogModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:settings.REPRESENTATION_LENGHT]


class PostQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.select_related('author', 'category', 'location')

    def published(self):
        return self.filter(is_published=True)

    def with_pub_date__lt(self):
        return self.filter(pub_date__lt=now())

    def category__is(self):
        return self.filter(category__is_published=True)


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return (PostQuerySet(self.model)
                .with_related_data()
                .published()
                .with_pub_date__lt()
                .category__is()
                )


class Post(BaseBlogModel):
    title = models.CharField('Заголовок', max_length=settings.MAX_FIELD_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно '
        'делать отложенные публикации.'
    )
    image = models.ImageField(verbose_name='Картинка у публикации', blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    category = models.ForeignKey(
        Category, null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория'
    )
    location = models.ForeignKey(
        Location,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение'
    )
    objects = PostQuerySet.as_manager()
    published = PublishedPostManager()

    class Meta(BaseBlogModel.Meta):
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return self.title[:settings.REPRESENTATION_LENGHT]

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=(self.pk,))


class Comment(BaseBlogModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комметария',
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемый пост',
        related_name='comments',
    )
    text = models.TextField(verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:settings.REPRESENTATION_LENGHT]

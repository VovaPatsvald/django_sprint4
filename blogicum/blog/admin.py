from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
    )
    list_editable = (
        'is_published',
        'slug',
    )
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'location',
        'category',
        'is_published',
        'comments'
    )

    list_display_links = (
        'location',
        'title',
    )

    list_editable = (
        'author',
        'category',
        'is_published'
    )
    search_fields = ('title',)
    list_filter = ('category', 'location', 'author')

    @admin.display(description='колличество комментариев',)
    def comments(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author'
    )
    search_fields = ('author__username',)
    list_filter = ('post', 'author')

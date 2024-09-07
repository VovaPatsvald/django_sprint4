from django.contrib import admin

from .models import Post, Location, Category
from django.contrib.auth.admin import UserAdmin

from .models import MyUser

UserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('bio',)}),
)

admin.site.register(MyUser, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('text', )
    list_display = (
        'id', 'title', 'description', 'slug',
        'is_published', 'created_at'
    )
    list_display_links = ('title', )
    list_editable = ['is_published']
    list_filter = ('created_at', )
    empty_value_display = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('text', )
    list_display = (
        'id', 'title', 'author', 'text', 'category', 'pub_date',
        'location', 'is_published', 'created_at'
    )
    list_display_links = ('title', )
    list_editable = ('category', 'is_published', 'location')
    list_filter = ('created_at', )
    empty_value_display = '-пусто-'


@admin.register(Location)
class LocationyAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = (
        'id', 'name',
        'is_published', 'created_at'
    )
    list_display_links = ('name', )
    list_editable = ['is_published']
    list_filter = ('created_at', )
    empty_value_display = '-пусто-'

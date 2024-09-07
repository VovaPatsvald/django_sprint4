from django.urls import path

from .views import (
    DeletePostView, EditPostView, PostCreateViews, PostDetailView,
    ProfileUpdateView, ProfileView, add_comment, index,
    category_posts)

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post_detail'),

    path(
        'posts/<int:post_id>/edit/',
        EditPostView.as_view(),
        name='edit_post',
    ),

    path('posts/<int:post_id>/delete/',
         DeletePostView.as_view(), name='delete_post'),

    path('category/<slug:category_slug>/',
         category_posts, name='category_posts'),

    path('posts/create/', PostCreateViews.as_view(), name='create_post'),

    path('profile/edit/', ProfileUpdateView.as_view(), name='edit_profile'),

    path('profile/<str:username', ProfileView.as_view(), name='profile'),

    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
]
"""    path('posts/<int:post_id>/edit_comment/<int:comment_id/', edit_comment,
         name='edit_comment'),

    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
    delete_comment, name='delete_comment'),"""

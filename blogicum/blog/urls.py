from django.urls import path

from .views import DeletePostView, EditPostView, index, post_detail, category_posts  post_create

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path('category/<slug:category_slug>/',
         category_posts, name='category_posts'),
    path('posts/create/', post_create, name='create_post'),
    path(
        'posts/<int:post_id>/edit/',
        EditPostView.as_view(),
        name='edit_post',
    ),
    path(
        'posts/<int:post_id>/delete/',
        DeletePostView.as_view(),
        name='dalete_post',
    ),
]

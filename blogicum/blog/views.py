from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.conf import settings
from .models import Post, Category


def index(request):
    post_list = Post.published.all()[:settings.POSTS_BY_PAGE]
    return render(request, 'blog/index.html', {'page_obj': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.published, id=post_id,
    )
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    get_posts = category.posts.select_related(
        'category', 'author', 'location'
    ).filter(
        is_published=True,
        pub_date__lt=now(),
        category__is_published=True,)
    context = {
        'post_list': get_posts,
        'category': category
    }
    return render(request, 'blog/category.html', context)

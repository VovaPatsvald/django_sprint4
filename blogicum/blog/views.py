from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone as dt

from blog.forms import CommentForm, EditProfileForm, PostForm
from blog.models import Category, Comment, Post, User

LIMIT_FOR_PAGES = 10


def paginate_posts(request, posts, limit):
    paginator = Paginator(posts, limit)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def check_auth(request):
    return Q(
        category__is_published=True,
        pub_date__lte=dt.now(),
        is_published=True
    ) | Q(author_id=request.user.id)


def post_select_realted():
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    )


def count_comments(obj):
    return obj.annotate(
        comment_count=Count('comments')
    ).all().order_by('-pub_date')


def select_posts():
    return post_select_realted().filter(
        category__is_published=True,
        pub_date__lte=dt.now(),
        is_published=True
    )


def index(request):
    """Главная страница"""
    posts = count_comments(select_posts())
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Страница с информацией о посте"""
    post = get_object_or_404(
        post_select_realted(),
        Q(id=post_id),
        check_auth(request)
    )
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница с категорией поста"""
    category = get_object_or_404(
        Category,
        is_published=True, slug=category_slug
    )
    posts = select_posts().filter(category__slug=category_slug)
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)


def profile(request, username):
    """Страница с профилем"""
    profile = get_object_or_404(
        User,
        username=username,
    )

    posts = count_comments(post_select_realted().filter(
        Q(author__username=username),
        check_auth(request)
    ))
    page_obj = paginate_posts(request, posts, LIMIT_FOR_PAGES)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    """Страница создания публикации"""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    context = {
        'form': form
    }
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'blog/create.html', context)


@login_required
def edit_profile(request):
    """Страница редактирования профиля"""
    user = get_object_or_404(User, username=request.user.username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', user.username)
    context = {
        'form': form,
    }
    return render(request, 'blog/user.html', context)


@login_required
def edit_post(request, post_id):
    """Страница редактирования публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author_id:
        return redirect('blog:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'form': form,
    }
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Страница удаления публикации"""
    post = get_object_or_404(Post, id=post_id)
    if request.user.id != post.author_id:
        return redirect('blog:post_detail', post_id)
    form = PostForm(instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {
        'form': form,
    }
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Страница изменения комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.id != comment.author_id:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Страница удаления комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.id != comment.author_id:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.conf import settings
from django.views.generic import UpdateView, DeleteView, DetailView, CreateView

from .forms import PostForm, UserForm, CommentForm
from .models import Post, Category, User
from datetime import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
"""from django.db.models.base import Model as Model"""
from django.db.models import Count
"""from django.db.models.query import QuerySet"""


def index(request):
    post_list = Post.published.all()[:settings.POSTS_BY_PAGE]
    paginator = Paginator(post_list, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


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
    paginator = Paginator(get_posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, 'blog/category.html', context)


def delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=request.user.username)
        instance.delete()
        return redirect('blog:index')
    else:
        form = PostForm(instance=request.user)
        return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:index')
        else:
            form = UserForm(instance=request.user)
        context = {'form': form}
        return render(request, 'blog/user.html', context)


def get_profile(request, username):
    profile = get_object_or_404(User, username=username)
    user_posts = profile.posts.select_related('author').annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    if not request.user.is_authenticated:
        user_posts = profile.posts.select_related('author').filter(
            pub_date__lte=timezone.now(),
            is_published=True).order_by('-pub_date')
        paginator = Paginator(user_posts, settings.POSTS_ON_PAGE)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'profile': profile,
            'page_obj': page_obj,
        }
        return render(request, 'blog/profile.html', context)


@login_required
def post_create(request):
    template_name = 'blog/create.html'
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:index')
    return render(request, template_name, {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)
        else:
            form = CommentForm()
        context = {
            'form': form,
            'post': post
        }

        return render(request, 'blog/detail.html', context)


class EditPostView(LoginRequiredMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateViews (LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = form.save(commit=False)
        post.pub_date = timezone.now()
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user.username
        return reverse('blog:profile', kwargs={'username': user})


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return get_object_or_404(User, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        posts = Post.objects.filter(
            author=user,
            is_published=True
        ).annotate(comment_count=Count('comments'))

        paginator = Paginator(posts, settings.POSTS_ON_PAGE)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['is_owner'] = self.request.user == user

        return context


class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileView
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

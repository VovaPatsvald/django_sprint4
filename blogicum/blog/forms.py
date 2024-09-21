from django.forms import DateTimeInput, ModelForm
from django.contrib.auth.models import User
from .models import Post, Comment


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'last_login', 'username')


class PostForm(ModelForm):
    """Форма для добавления поста."""

    class Meta:
        model = Post
        exclude = (
            "author",
            "is_published",
        )
        widgets = {
            "pub_date": DateTimeInput(attrs={"type": "datetime-local"}),
        }


class CommentForm(ModelForm):
    """Форма для добавления комментария к посту."""

    class Meta:
        model = Comment
        fields = ("text",)

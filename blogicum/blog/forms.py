from datetime import datetime
from django.forms import DateTimeField, DateTimeInput, ModelForm

from .models import Post


class PostForm(ModelForm):
    pub_date = DateTimeField(
        label='Дата публикации',
        widget=DateTimeInput(attrs={'typet': 'datetime-local'}),
        initial=format(datetime.now(), '%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
        localize=True
    )

    class Meta:
        model = Post
        exclude = ('author',)

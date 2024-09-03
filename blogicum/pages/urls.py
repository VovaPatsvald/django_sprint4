"""from django.urls import path, include"""
from django.urls import path
from django.views.generic import TemplateView


app_name = 'pages'


urlpatterns = [
    path(
        'about/',
        TemplateView.as_view(template_name='pages/about.html'),
    ),
    path(
        'rules/',
        TemplateView.as_view(template_name='pages/rules.html'),
    ),
]

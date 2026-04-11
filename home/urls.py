from django.urls import path

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.get_home_page, name='main_page'),
]
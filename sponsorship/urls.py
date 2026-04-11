from . import views
from django.urls import path

app_name = 'sponsorship'

urlpatterns = [
    path('', views.get_sponsorship_page, name='sponsorship_page'),
]
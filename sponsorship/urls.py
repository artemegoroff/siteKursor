from django.conf.urls import url
from . import views

app_name = 'sponsorship'

urlpatterns = [
    url(r'^$', views.get_sponsorship_page, name='sponsorship_page'),
]
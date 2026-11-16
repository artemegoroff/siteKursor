from django.urls import path
from . import landing_views

app_name = 'course_landings'

urlpatterns = [
    path('<slug:course_slug>/', landing_views.detail, name='detail'),
]

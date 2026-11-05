from django.urls import path

from . import views


urlpatterns = [
    path('', views.legacy_course_redirect, name='legacy_course_catalogue'),
    path('<path:old_path>', views.legacy_course_redirect, name='legacy_course_redirect'),
]

from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.courses_home, name='courses_home'),
    path('<slug:course_slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/<slug:module_slug>/', views.module_detail, name='module_detail'),
    path('<slug:course_slug>/<slug:module_slug>/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
]
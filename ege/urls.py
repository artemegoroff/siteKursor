from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'ege'

urlpatterns = [
    path('task/<int:number_task>/', views.ege_task_detail, name='ege_task_detail'),
    path('var/<int:variant_number>/', views.ege_get_var, name='ege_get_var'),
    path('exercise/<int:id_exercise>/', views.ege_get_exercise, name='ege_get_exercise'),

    path('videotask/', views.ege_videotask_AllTask, name='ege_videotask_AllTask'),
    path(
        'videotask/<int:id_theme>/<int:id_task>/',
        views.ege_videotask_detail,
        name='ege_videotask_detail',
    ),
    path(
        'videotask/<int:id_theme>/',
        views.ege_videotask_ONEtheme,
        name='ege_videotask_ONEtheme',
    ),

    path('', views.ege_home_page, name='base_ege'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
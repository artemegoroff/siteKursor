from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

app_name = 'oge'

urlpatterns = [
    path('task/<int:number_task>/', views.oge_task_detail, name='oge_task_detail'),
    path('var/<int:variant_number>/', views.oge_get_var, name='oge_get_var'),
    path('exercise/<int:id_exercise>/', views.oge_get_exercise, name='oge_get_exercise'),

    path(
        'videotask/<int:id_theme>/<int:id_task>/',
        views.oge_videotask_detail,
        name='oge_videotask_detail'
    ),
    path(
        'videotask/<int:id_theme>/',
        views.oge_videotask_ONEtheme,
        name='oge_videotask_ONEtheme'
    ),
    path(
        'videotask/',
        views.oge_videotask_AllTask,
        name='oge_videotask_AllTask'
    ),

    path('', views.oge_home_page, name='base_oge'),
]

# только для разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

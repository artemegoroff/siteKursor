from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

app_name = 'videos'

urlpatterns = [
    path('decision/', views.videos_decision_all, name='decision_all'),
    re_path(
        r'^decision/(?P<ref_decision>[\w-]+)/$',
        views.videos_decision_one,
        name='videos_decision_one'
    ),

    re_path(r'^python/(?P<number>[0-9]+)/$', views.videos_python_theme, name='videos_python_theme'),
    re_path(
        r'^python/(?P<slug>[\w-]+)/$',
        views.videos_python_theme_by_slug,
        name='videos_python_theme_by_slug'
    ),
    path('python/', views.videos_python_all, name='videos_python_all'),

    re_path(r'^turtle/(?P<number>[0-9]+)/$', views.videos_turtle_theme, name='videos_turtle_theme'),
    re_path(
        r'^turtle/(?P<slug>[\w-]+)/$',
        views.videos_turtle_theme_by_slug,
        name='videos_turtle_theme_by_slug'
    ),
    path('turtle/', views.videos_turtle_all, name='videos_turtle_all'),

    re_path(r'^pygame/(?P<number>[0-9]+)/$', views.videos_pygame_theme, name='videos_pygame_theme'),
    re_path(
        r'^pygame/(?P<slug>[\w-]+)/$',
        views.videos_pygame_theme_by_slug,
        name='videos_pygame_theme_by_slug'
    ),
    path('pygame/', views.videos_pygame_all, name='videos_pygame_all'),

    re_path(
        r'^oop-python/(?P<number>[0-9]+)/$',
        views.videos_oop_python_theme,
        name='videos_oop_python_theme'
    ),
    re_path(
        r'^oop-python/(?P<slug>[\w-]+)/$',
        views.videos_oop_python_theme_by_slug,
        name='videos_oop_python_theme_by_slug'
    ),
    path('oop-python/', views.videos_oop_python_all, name='videos_oop_python_all'),

    re_path(
        r'^tkinter/(?P<number>[0-9]+)/$',
        views.videos_tkinter_theme,
        name='videos_tkinter_theme'
    ),
    re_path(
        r'^tkinter/(?P<slug>[\w-]+)/$',
        views.videos_tkinter_theme_by_slug,
        name='videos_tkinter_theme_by_slug'
    ),
    path('tkinter/', views.videos_tkinter_all, name='videos_tkinter_all'),

    path('django/<int:number>/', views.videos_django_theme, name='videos_django_theme'),
    path('django/<slug:slug>/', views.videos_django_theme_by_slug, name='videos_django_theme_by_slug'),
    path('django/', views.videos_django_all, name='videos_django_all'),

    path('test/', views.videos_test, name='videos_test'),
    path('indi_course/', views.get_landing_indi_course_page, name='main_p'),

    path('', views.videos_home, name='videos_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.conf.urls import url
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'videos'

urlpatterns = [
                  url(r'^decision/$', views.videos_decision_all, name='decision_all'),
                  url(r'^decision/(?P<ref_decision>[\w-]+)$', views.videos_decision_one, name='videos_decision_one'),
                  url(r'^python/(?P<number>[0-9]+)$', views.videos_python_theme, name='videos_python_theme'),
                  url(r'^python/(?P<slug>[\w-]+)$', views.videos_python_theme_by_slug,
                      name='videos_python_theme_by_slug'),
                  url(r'^python/$', views.videos_python_all, name='videos_python_all'),

                  url(r'^turtle/(?P<number>[0-9]+)$', views.videos_turtle_theme, name='videos_turtle_theme'),
                  url(r'^turtle/(?P<slug>[\w-]+)$', views.videos_turtle_theme_by_slug,
                      name='videos_turtle_theme_by_slug'),
                  url(r'^turtle/$', views.videos_turtle_all, name='videos_turtle_all'),

                  url(r'^pygame/(?P<number>[0-9]+)$', views.videos_pygame_theme, name='videos_pygame_theme'),
                  url(r'^pygame/(?P<slug>[\w-]+)$', views.videos_pygame_theme_by_slug,
                      name='videos_pygame_theme_by_slug'),
                  url(r'^pygame/$', views.videos_pygame_all, name='videos_pygame_all'),

                  url(r'^oop-python/(?P<number>[0-9]+)$', views.videos_oop_python_theme,
                      name='videos_oop_python_theme'),
                  url(r'^oop-python/(?P<slug>[\w-]+)$', views.videos_oop_python_theme_by_slug,
                      name='videos_oop_python_theme_by_slug'),
                  url(r'^oop-python/$', views.videos_oop_python_all, name='videos_oop_python_all'),

                  url(r'^tkinter/(?P<number>[0-9]+)$', views.videos_tkinter_theme,
                      name='videos_tkinter_theme'),
                  url(r'^tkinter/(?P<slug>[\w-]+)$', views.videos_tkinter_theme_by_slug,
                      name='videos_tkinter_theme_by_slug'),
                  url(r'^tkinter/$', views.videos_tkinter_all, name='videos_tkinter_all'),

                  path('django/<int:number>', views.videos_django_theme,
                      name='videos_django_theme'),
                  path('django/<slug:slug>', views.videos_django_theme_by_slug,
                      name='videos_django_theme_by_slug'),
                  path('django/', views.videos_django_all, name='videos_django_all'),

                  url(r'^test/$', views.videos_test, name='videos_test'),
                  url(r'^$', views.videos_home, name='videos_home'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

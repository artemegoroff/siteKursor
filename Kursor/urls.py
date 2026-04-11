from .sitemaps import EgeTaskSiteMap, EgeVarSiteMap, EgeVideoSiteMap, EgeStaticSiteMap
from .sitemaps import OgeTaskSiteMap, OgeVarSiteMap, OgeVideoSiteMap, OgeStaticSiteMap
import home.views as home_view

from .sitemaps import CoursePythonSiteMap, AllLastSiteMap
from django.conf import settings
from django.conf.urls import include
from django.urls import path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.static import serve

sitemaps = {
    'egeStatic': EgeStaticSiteMap,
    'egeTask': EgeTaskSiteMap,
    'egeVar': EgeVarSiteMap,
    'egeRazbor': EgeVideoSiteMap,
    'ogeStatic': OgeStaticSiteMap,
    'ogeTask': OgeTaskSiteMap,
    'ogeVar': OgeVarSiteMap,
    'ogeRazbor': OgeVideoSiteMap,
    'coursePython': CoursePythonSiteMap,
    'allLast': AllLastSiteMap,
}

handler404 = home_view.e_handler404
handler500 = home_view.e_handler500

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('subscribe/', include('sponsorship.urls')),
    # path('accounts/', include('accounts.urls')),
    path('ege/', include('ege.urls')),
    path('oge/', include('oge.urls')),
    path('services/', include('services.urls')),
    path('course/', include('videos.urls')),

    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path('robots.txt', include('robots.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('tinymce/', include('tinymce.urls')),
]
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
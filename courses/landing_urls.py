from django.urls import path
from django.views.generic import RedirectView
from . import landing_views

app_name = 'course_landings'

urlpatterns = [
    path('python/', RedirectView.as_view(
        url='/learn/basic-python/', permanent=True, query_string=True,
    ), name='python_legacy'),
    path('<slug:course_slug>/', landing_views.detail, name='detail'),
]

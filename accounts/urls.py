from django.conf.urls import url

from . import views

urlpatterns = [
    url('signup/', views.signup, name='sign_up'),
    url('login/', views.login_user, name='login'),
    url('logout/', views.logout_user, name='logout'),
    url('profile/', views.get_profile_page, name='profile'),
]

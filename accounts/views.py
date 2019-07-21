from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import Profile
from django.contrib.auth.decorators import login_required

# Create your views here.
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('password_repeat')
        if password == repeat_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Имя пользователя %s уже занято' % username)
                return redirect('sign_up')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Почта %s уже занята'% email)
                return redirect('sign_up')
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()
            messages.success(request, 'Пользователь успешно создан. Теперь можете войти на сайт')
            return redirect('login')
        else:
            messages.error(request, 'Пароли в полях не совпали')
            return redirect('sign_up')
    return render(request, 'registration/sign_up.html')


HTTP_REFERER = '/'

def login_user(request):
    global HTTP_REFERER
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('psw')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                if not Profile.objects.filter(user=user).exists():
                    Profile.objects.create(user=user)
                login(request, user)
                path_http_referer,HTTP_REFERER = HTTP_REFERER, '/'
                return HttpResponseRedirect(path_http_referer)
            return HttpResponse("Your account was inactive.")
        else:
            messages.error(request, 'Такого пользователя не существует или неверный пароль')
            return redirect('login')
    HTTP_REFERER = request.META.get('HTTP_REFERER','/')
    return render(request, 'registration/login.html')


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/')

@login_required
def get_profile_page(request):
    return render(request, 'profile_page.html')
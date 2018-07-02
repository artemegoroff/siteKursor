from django.shortcuts import render
from .models import Course
# Create your views here.

def videos_python_all(request):
    allThemes = Course.objects.filter(language=Course.PYTHON)
    context={}
    context['allThemes']=allThemes
    return render(request,'videos/allThemes.html',context)


def videos_python_theme(request,number):
    Theme = Course.objects.filter(language=Course.PYTHON).get(number_theme=number)
    allThemes = Course.objects.filter(language=Course.PYTHON)
    context={}
    context["Theme"]=Theme
    context["allThemes"] = allThemes
    return  render(request,'videos/oneTheme.html',context)

def videos_home(request):
    context={}
    return render(request, 'videos/allThemes.html', context)
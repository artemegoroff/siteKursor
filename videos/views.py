from django.shortcuts import render,get_object_or_404
from .models import Course
# Create your views here.

def videos_python_all(request):
    allThemes = Course.objects.filter(language=Course.PYTHON)
    context={}
    context['allThemes']=allThemes
    return render(request,'videos/allThemes.html',context)


def videos_python_theme(request,number):
    Theme = get_object_or_404(Course,language=Course.PYTHON,number_theme=number)
    allThemes = Course.objects.filter(language=Course.PYTHON)
    nextThemes = Course.objects.filter(number_theme__gt=number)[:6]
    context={}
    context["Theme"]=Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return  render(request,'videos/oneTheme.html',context)

def videos_home(request):
    context={}
    return render(request, 'videos/allThemes.html', context)


def videos_test(request):
    context = {}
    return render(request, 'videos/test.html', context)
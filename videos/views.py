from django.shortcuts import render, get_object_or_404
from .models import Course


# Create your views here.

def videos_python_all(request):
    allThemes = Course.objects.filter(language=Course.PYTHON)
    context = {}
    context['allThemes'] = allThemes
    return render(request, 'videos/allThemes.html', context)


def videos_turtle_all(request):
    allThemes = Course.objects.filter(language=Course.TURTLEPython)
    context = {}
    context['allThemes'] = allThemes
    return render(request, 'videos/allThemes.html', context)


def videos_pygame_all(request):
    allThemes = Course.objects.filter(language=Course.PYGAMEPython)
    context = {}
    context['allThemes'] = allThemes
    return render(request, 'videos/allThemes.html', context)

def videos_python_theme(request, number):
    Theme = get_object_or_404(Course, language=Course.PYTHON, number_theme=number)
    allThemes = Course.objects.filter(language=Course.PYTHON)
    nextThemes = allThemes.filter(number_theme__gt=number)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_python_theme_by_slug(request, slug):
    Theme = get_object_or_404(Course, language=Course.PYTHON, slug=slug)
    allThemes = Course.objects.filter(language=Course.PYTHON)
    nextThemes = allThemes.filter(language=Course.PYTHON, number_theme__gt=Theme.number_theme)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_turtle_theme(request, number):
    Theme = get_object_or_404(Course, language=Course.TURTLEPython, number_theme=number)
    allThemes = Course.objects.filter(language=Course.TURTLEPython)
    nextThemes = allThemes.filter(number_theme__gt=number)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_turtle_theme_by_slug(request, slug):
    Theme = get_object_or_404(Course, language=Course.TURTLEPython, slug=slug)
    allThemes = Course.objects.filter(language=Course.TURTLEPython)
    nextThemes = allThemes.filter(number_theme__gt=Theme.number_theme)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_pygame_theme(request, number):
    Theme = get_object_or_404(Course, language=Course.PYGAMEPython, number_theme=number)
    allThemes = Course.objects.filter(language=Course.PYGAMEPython)
    nextThemes = allThemes.filter(number_theme__gt=number)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_pygame_theme_by_slug(request, slug):
    Theme = get_object_or_404(Course, language=Course.PYGAMEPython, slug=slug)
    allThemes = Course.objects.filter(language=Course.PYGAMEPython)
    nextThemes = Course.objects.filter(number_theme__gt=Theme.number_theme)[:8]
    context = {}
    context["Theme"] = Theme
    context["video"] = Theme
    context["allThemes"] = allThemes
    # context["nextThemes"] = nextThemes
    return render(request, 'videos/oneTheme.html', context)


def videos_home(request):
    context = {}
    return render(request, 'videos/allThemes.html', context)


def videos_test(request):
    context = {}
    return render(request, 'videos/test.html', context)

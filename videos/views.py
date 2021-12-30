from django.shortcuts import render, get_object_or_404
from .models import Course, ProgrammTask


# Create your views here.

def get_all_themes_by_course(course):
    return {'allThemes': Course.objects.filter(language=course)}


def get_course_theme_by_number(course, number):
    theme = get_object_or_404(Course, language=course, number_theme=number)
    all_themes = Course.objects.filter(language=course)
    next_themes = all_themes.filter(number_theme__gt=number)[:8]
    context = {"Theme": theme, "video": theme, "allThemes": all_themes, "nextThemes": next_themes}
    return context


def get_course_theme_by_slug(course, slug):
    theme = get_object_or_404(Course, language=course, slug=slug)
    all_themes = Course.objects.filter(language=course)
    next_themes = all_themes.filter(number_theme__gt=theme.number_theme)[:8]
    context = {"Theme": theme, "video": theme, "allThemes": all_themes, "nextThemes": next_themes}
    return context


def videos_python_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.PYTHON, number))


def videos_django_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.DJANGO))


def videos_python_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.PYTHON))


def videos_turtle_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.TURTLEPython))


def videos_oop_python_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.OOP))


def videos_tkinter_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.TKINTER))


def videos_pygame_all(request):
    return render(request, 'videos/allThemes.html', get_all_themes_by_course(Course.PYGAMEPython))


def videos_decision_all(request):
    allThemes = ProgrammTask.objects.exclude(decision__isnull=True). \
        exclude(decision__exact='')
    context = {}
    context['allThemes'] = allThemes
    return render(request, 'videos/decisionAll.html', context)


def videos_decision_one(request, ref_decision):
    Decision = get_object_or_404(ProgrammTask, decision=ref_decision)
    allThemes = Course.objects.filter(language=Course.PYTHON)
    nextThemes = ProgrammTask.objects.exclude(decision__isnull=True). \
        exclude(decision__exact='').exclude(decision__exact=ref_decision)
    context = {}
    context["Decision"] = Decision
    context["video"] = Decision
    context["allThemes"] = allThemes
    context["nextThemes"] = nextThemes
    return render(request, 'videos/decisionTheme.html', context)


def videos_python_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.PYTHON, slug))


def videos_turtle_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.TURTLEPython, number))


def videos_turtle_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.TURTLEPython, slug))


def videos_tkinter_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.TKINTER, number))


def videos_tkinter_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.TKINTER, slug))


def videos_django_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.DJANGO, number))


def videos_django_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.DJANGO, slug))


def videos_pygame_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.PYGAMEPython, number))


def videos_pygame_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.PYGAMEPython, slug))


def videos_oop_python_theme(request, number):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_number(Course.OOP, number))


def videos_oop_python_theme_by_slug(request, slug):
    return render(request, 'videos/oneTheme.html', get_course_theme_by_slug(Course.OOP, slug))


def videos_home(request):
    context = {}
    return render(request, 'videos/allThemes.html', context)


def videos_test(request):
    context = {}
    return render(request, 'videos/test.html', context)

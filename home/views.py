from django.db.models import Count
from django.shortcuts import render

from courses.models import LearningCourse
from ege.models import NumberTaskEge, VideoRazborEGE
from oge.models import NumberTaskOge, VideoRazborOGE


COURSE_COVERS = {
    'python': 'c2.jpg',
    'oop-python': 'oop-bg.png',
    'django': 'django-bg.png',
    'pygame': 'gamedev.png',
    'turtle': 'c4.jpg',
}


def get_home_page(request):
    courses = list(
        LearningCourse.objects
        .exclude(slug__isnull=True)
        .exclude(slug='')
        .annotate(lessons_count=Count('modules__lessons'))
        .order_by('sort_order', 'title', 'pk')
    )
    for course in courses:
        cover = COURSE_COVERS.get(course.slug, 'c5.jpg')
        course.cover_static_path = f'base_static/img/bg-img/{cover}'

    return render(request, 'home/home_page.html', {
        'learning_courses': courses,
        'countEGERazbor': VideoRazborEGE.objects.count(),
        'countOGERazbor': VideoRazborOGE.objects.count(),
        'CountTaskEGE': NumberTaskEge.objects.count(),
        'CountTaskOge': NumberTaskOge.objects.count(),
    })


def e_handler404(request, exception):
    return render(request, 'error404.html', status=404)


def e_handler500(request):
    return render(request, 'error500.html', status=500)

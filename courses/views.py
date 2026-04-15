from django.db.models import Prefetch, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import LearningCourse, LearningModule, Lesson


def get_video_sources(lesson):
    sources = {}

    if lesson.rutube_id:
        sources['rutube'] = {
            'url': f'https://rutube.ru/play/embed/{lesson.rutube_id}',
            'label': 'Rutube',
        }

    if lesson.youtube_id:
        sources['youtube'] = {
            'url': f'https://www.youtube.com/embed/{lesson.youtube_id}',
            'label': 'YouTube',
        }

    return sources


def build_course_navigation(course, current_lesson):
    lesson_qs = Lesson.objects.order_by('sort_order', 'title')

    modules = list(
        LearningModule.objects
        .filter(course=course)
        .prefetch_related(Prefetch('lessons', queryset=lesson_qs))
        .order_by('sort_order', 'title')
    )

    all_lessons = []
    lesson_counter = 1

    for module in modules:
        module.lessons_for_menu = list(module.lessons.all())

        for lesson in module.lessons_for_menu:
            lesson.menu_number = lesson_counter
            all_lessons.append(lesson)
            lesson_counter += 1

    current_index = None
    for index, lesson in enumerate(all_lessons):
        if lesson.id == current_lesson.id:
            current_index = index
            break

    if current_index is None:
        raise Http404('Текущий урок не найден в структуре курса')

    current_lesson.menu_number = all_lessons[current_index].menu_number

    prev_lessons = all_lessons[max(0, current_index - 5):current_index]
    next_lessons = all_lessons[current_index + 1:current_index + 6]

    return modules, all_lessons, prev_lessons, next_lessons


def courses_home(request):
    courses = (
        LearningCourse.objects
        .annotate(
            lessons_count=Count('modules__lessons')
        )
        .order_by('sort_order')
    )
    context = {
        'courses': courses,
    }
    return render(request, 'courses/courses.html', context)


def course_detail(request, course_slug):
    course = get_object_or_404(LearningCourse, slug=course_slug)

    lesson_qs = Lesson.objects.order_by('sort_order', 'title')
    modules = (
        LearningModule.objects
        .filter(course=course)
        .prefetch_related(Prefetch('lessons', queryset=lesson_qs))
        .order_by('sort_order', 'title')
    )

    current_lesson_id = request.GET.get('current')

    try:
        current_lesson_id = int(current_lesson_id) if current_lesson_id else None
    except (TypeError, ValueError):
        current_lesson_id = None

    context = {
        'course': course,
        'modules': modules,
        'current_lesson_id': current_lesson_id,
    }
    return render(request, 'courses/course_detail.html', context)


def module_detail(request, course_slug, module_slug):
    module = get_object_or_404(
        LearningModule.objects.select_related('course').prefetch_related(
            Prefetch('lessons', queryset=Lesson.objects.order_by('sort_order', 'title'))
        ),
        course__slug=course_slug,
        slug=module_slug,
    )

    context = {
        'course': module.course,
        'module': module,
        'lessons': module.lessons.all(),
    }
    return render(request, 'courses/module_detail.html', context)


def lesson_detail(request, course_slug, module_slug, lesson_slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related('module', 'module__course'),
        module__course__slug=course_slug,
        module__slug=module_slug,
        slug=lesson_slug,
    )

    course = lesson.module.course
    modules, all_lessons, prev_lessons, next_lessons = build_course_navigation(course, lesson)

    context = {
        'Theme': lesson,
        'course': course,
        'module': lesson.module,
        'modules': modules,
        'allThemes': all_lessons,
        'prevThemes': prev_lessons,
        'nextThemes': next_lessons,
        'video_sources': get_video_sources(lesson),
    }
    return render(request, 'courses/lesson_detail.html', context)
from django.db.models import Count, Prefetch
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import LearningCourse, LearningModule, Lesson, LegacyCourseRedirect
from .navigation import build_lesson_tree


def legacy_course_redirect(request, old_path=''):
    if not old_path:
        return HttpResponsePermanentRedirect(reverse('courses:courses_home'))
    destination = get_object_or_404(
        LegacyCourseRedirect.objects.select_related(
            'course', 'lesson__module__course',
        ),
        old_path=old_path,
    )
    return HttpResponsePermanentRedirect(destination.get_absolute_url())


def get_course_tree(course, current_id=None):
    lessons = Lesson.objects.order_by(
        'sort_order', 'title', 'pk',
    )

    modules = list(
        LearningModule.objects
        .filter(course=course)
        .select_related('course')
        .prefetch_related(
            Prefetch('lessons', queryset=lessons),
        )
        .order_by('sort_order', 'title', 'pk')
    )

    all_lessons = build_lesson_tree(modules, current_id)
    return modules, all_lessons


def courses_home(request):
    courses = (
        LearningCourse.objects
        .annotate(
            lessons_count=Count('modules__lessons'),
        )
        .order_by('sort_order', 'title', 'pk')
    )

    return render(
        request,
        'courses/courses.html',
        {'courses': courses},
    )


def course_detail(request, course_slug):
    course = get_object_or_404(
        LearningCourse,
        slug=course_slug,
    )

    try:
        current_id = int(request.GET.get('current', ''))
    except (TypeError, ValueError):
        current_id = None

    modules, all_lessons = get_course_tree(
        course,
        current_id,
    )

    context = {
        'course': course,
        'modules': modules,
        'first_lesson': (
            all_lessons[0] if all_lessons else None
        ),
        'current_lesson_id': current_id,
    }

    return render(
        request,
        'courses/course_detail.html',
        context,
    )


def module_detail(request, course_slug, module_slug):
    module = get_object_or_404(
        LearningModule.objects.select_related('course'),
        course__slug=course_slug,
        slug=module_slug,
    )

    modules, _ = get_course_tree(module.course)

    module = next(
        item for item in modules
        if item.pk == module.pk
    )

    return render(
        request,
        'courses/module_detail.html',
        {
            'course': module.course,
            'module': module,
        },
    )


def lesson_detail(
    request,
    course_slug,
    module_slug,
    lesson_slug,
):
    lesson = get_object_or_404(
        Lesson.objects.select_related('module__course'),
        module__course__slug=course_slug,
        module__slug=module_slug,
        slug=lesson_slug,
    )

    course = lesson.module.course

    modules, all_lessons = get_course_tree(
        course,
        lesson.pk,
    )

    current_index = next(
        (
            index
            for index, item in enumerate(all_lessons)
            if item.pk == lesson.pk
        ),
        None,
    )

    if current_index is None:
        raise Http404(
            'Урок отсутствует в структуре курса.'
        )

    # У этого экземпляра уже есть номер, предки и подуроки.
    lesson = all_lessons[current_index]

    previous = (
        all_lessons[current_index - 1]
        if current_index else None
    )

    following = (
        all_lessons[current_index + 1]
        if current_index + 1 < len(all_lessons)
        else None
    )

    context = {
        'Theme': lesson,
        'course': course,
        'module': lesson.module,
        'modules': modules,
        'blocks': lesson.blocks.order_by(
            'sort_order', 'id',
        ),
        'ancestors': lesson.ancestors_for_menu,
        'child_lessons': lesson.children_for_menu,
        'previous_lesson': previous,
        'next_lesson': following,
    }

    return render(
        request,
        'courses/lesson_detail.html',
        context,
    )

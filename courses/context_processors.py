from .models import LearningCourse


def course_navigation(request):
    """Keep the shared menu in sync with the course catalogue."""
    return {
        'navigation_courses': (
            LearningCourse.objects
            .exclude(slug__isnull=True)
            .exclude(slug='')
            .order_by('sort_order', 'title', 'pk')
        ),
    }

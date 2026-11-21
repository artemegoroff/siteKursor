from .catalogue import course_catalogue, landing_cards


def course_navigation(request):
    courses = course_catalogue(request)
    return {
        'navigation_courses': [course for course in courses if course.lessons_count],
        'navigation_landings': landing_cards(courses),
    }

from django import template

register = template.Library()


@register.filter(name='get_route')
def get_route(path):
    if 'turtle' in path:
        return 'videos:videos_turtle_theme_by_slug'
    if 'pygame' in path:
        return 'videos:videos_pygame_theme_by_slug'
    if 'oop-python' in path:
        return 'videos:videos_oop_python_theme_by_slug'
    if 'tkinter' in path:
        return 'videos:videos_tkinter_theme_by_slug'
    if 'django' in path:
        return 'videos:videos_django_theme_by_slug'
    return 'videos:videos_python_theme_by_slug'

from videos.models import Course


def change_number_theme(start_with, lang=Course.PYTHON, up=1):
    themes = Course.objects.filter(number_theme__gte=start_with, language=lang).order_by(
        '-number_theme')
    for theme in themes:
        theme.number_theme += up
        theme.save()


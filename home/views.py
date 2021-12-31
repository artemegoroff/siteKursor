from django.shortcuts import render
from ege.models import VideoRazborEGE, NumberTaskEge
from oge.models import VideoRazborOGE, NumberTaskOge
from videos.models import Course


def get_home_page(request):
    countEGERazbor = len(VideoRazborEGE.objects.all())
    countOGERazbor = len(VideoRazborOGE.objects.all())
    countPythonVideos = len(Course.objects.filter(language=Course.PYTHON))
    countTURTLEVideos = len(Course.objects.filter(language=Course.TURTLEPython))
    countPYGAMEVideos = len(Course.objects.filter(language=Course.PYGAMEPython))
    countDJANGO = Course.objects.filter(language=Course.DJANGO).count()
    countOOPVideos = len(Course.objects.filter(language=Course.OOP))
    CountTaskEGE = len(NumberTaskEge.objects.all())
    CountTaskOge = len(NumberTaskOge.objects.all())
    context = {
        'countEGERazbor': countEGERazbor, 'countOGERazbor': countOGERazbor,
        'countPythonVideos': countPythonVideos, 'CountTaskEGE': CountTaskEGE, 'CountTaskOge': CountTaskOge,
        'countTURTLEVideos': countTURTLEVideos, 'countPYGAMEVideos': countPYGAMEVideos,
        'countOOPVideos': countOOPVideos, 'countDJANGO': countDJANGO
    }
    return render(request, 'home/home_page.html', context)


def e_handler404(request, exception):
    context = {}
    return render(request, 'error404.html', context)


def e_handler500(request):
    context = {}
    return render(request, 'error500.html', context)

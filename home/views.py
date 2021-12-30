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
    countOOPVideos = len(Course.objects.filter(language=Course.OOP))
    CountTaskEGE = len(NumberTaskEge.objects.all())
    CountTaskOge = len(NumberTaskOge.objects.all())
    context = {}
    context['countEGERazbor'] = countEGERazbor
    context['countOGERazbor'] = countOGERazbor
    context['countPythonVideos'] = countPythonVideos
    context['CountTaskEGE'] = CountTaskEGE
    context['CountTaskOge'] = CountTaskOge
    context['countTURTLEVideos'] = countTURTLEVideos
    context['countPYGAMEVideos'] = countPYGAMEVideos
    context['countOOPVideos'] = countOOPVideos
    return render(request, 'home/home_page.html', context)


def e_handler404(request, exception):
    context = {}
    return render(request, 'error404.html', context)


def e_handler500(request):
    context = {}
    return render(request, 'error500.html', context)
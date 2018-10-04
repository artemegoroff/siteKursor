from django.shortcuts import render

from ege.models import VideoRazborEGE, NumberTaskEge
from oge.models import VideoRazborOGE, NumberTaskOge
from videos.models import Course


def get_home_page(request):
    countEGERazbor = len(VideoRazborEGE.objects.all())
    countOGERazbor = len(VideoRazborOGE.objects.all())
    countPythonVideos = len(Course.objects.filter(language=Course.PYTHON))
    CountTaskEGE = len(NumberTaskEge.objects.all())
    CountTaskOge = len(NumberTaskOge.objects.all())
    context = {}
    context['countEGERazbor'] = countEGERazbor
    context['countOGERazbor'] = countOGERazbor
    context['countPythonVideos'] = countPythonVideos
    context['CountTaskEGE'] = CountTaskEGE
    context['CountTaskOge'] = CountTaskOge

    return render(request, 'home/home_page.html', context)


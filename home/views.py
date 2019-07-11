from django.shortcuts import render_to_response, render
from django.template import RequestContext
from ege.models import VideoRazborEGE, NumberTaskEge
from oge.models import VideoRazborOGE, NumberTaskOge
from videos.models import Course


def get_home_page(request):
    countEGERazbor = len(VideoRazborEGE.objects.all())
    countOGERazbor = len(VideoRazborOGE.objects.all())
    countPythonVideos = len(Course.objects.filter(language=Course.PYTHON))
    countTURTLEVideos = len(Course.objects.filter(language=Course.TURTLEPython))
    CountTaskEGE = len(NumberTaskEge.objects.all())
    CountTaskOge = len(NumberTaskOge.objects.all())
    context = {}
    context['countEGERazbor'] = countEGERazbor
    context['countOGERazbor'] = countOGERazbor
    context['countPythonVideos'] = countPythonVideos
    context['CountTaskEGE'] = CountTaskEGE
    context['CountTaskOge'] = CountTaskOge
    context['countTURTLEVideos'] = countTURTLEVideos

    return render(request, 'home/home_page.html', context)


def e_handler404(request):
    context = RequestContext(request)
    response = render_to_response('error404.html', context)
    response.status_code = 404
    return response


def e_handler500(request):
    context = RequestContext(request)
    response = render_to_response('error500.html', context)
    response.status_code = 500
    return response
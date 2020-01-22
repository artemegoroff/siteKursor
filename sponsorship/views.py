from django.shortcuts import render_to_response, render
from django.template import RequestContext
from ege.models import VideoRazborEGE, NumberTaskEge
from oge.models import VideoRazborOGE, NumberTaskOge
from videos.models import Course


def get_sponsorship_page(request):
    context = {}
    return render(request, 'sponsorship/sponsorship_page.html', context)


def e_handler404(request):
    context = {}
    return render(request, 'error404.html', context)


def e_handler500(request):
    context = {}
    return render(request, 'error500.html', context)
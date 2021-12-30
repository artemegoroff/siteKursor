from django.shortcuts import render


def get_sponsorship_page(request):
    context = {}
    return render(request, 'sponsorship/sponsorship_page.html', context)


def e_handler404(request):
    context = {}
    return render(request, 'error404.html', context)


def e_handler500(request):
    context = {}
    return render(request, 'error500.html', context)
from django.shortcuts import render

# Create your views here.

def services_home_page(request):
    context = {}
    return render(request, 'service/service_home.html', context)
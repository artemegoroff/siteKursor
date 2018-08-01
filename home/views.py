from django.shortcuts import render

from .models import Review


def get_home_page(request):
    rand_9_review = list(Review.objects.order_by('?')[:9])
    reviews = []
    if rand_9_review:
        for i in range(3):
            row =[]
            for j in range(3):
                row.append(rand_9_review.pop())
            reviews.append(row)
    return render(request, 'home/home_page.html', {'reviews':reviews})


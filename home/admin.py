from django.contrib import admin
from .models import Review


# Register your models here.
class AdminReview(admin.ModelAdmin):
    list_display = ["client", "date", "mark"]

admin.site.register(Review, AdminReview)
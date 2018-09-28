from django.contrib import admin
from .models import CategoryTheory,TheoryVideo



class AdminTheoryVideo(admin.ModelAdmin):
    list_display = ["name", 'category']




admin.site.register(CategoryTheory)
admin.site.register(TheoryVideo,AdminTheoryVideo)
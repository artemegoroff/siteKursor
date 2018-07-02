from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Course
# Register your models here.

class AdminCourseSummernote(SummernoteModelAdmin):
    summernote_fields = ('article',)

admin.site.register(Course,AdminCourseSummernote)

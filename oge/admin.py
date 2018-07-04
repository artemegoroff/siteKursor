from django.contrib import admin
from .models import QuestionsOge, NumberTaskOge, CategoryOge, VariantOge, VideoRazborOGE
from django.forms import TextInput, Textarea, Select
from django.db import models


# Register your models here.
class AdminQuestionsOGE(admin.ModelAdmin):
    list_display = ["number_of_task", 'text', "category", "answer"]
    list_filter = ['number_of_task']
    list_editable = ['text', 'category', 'answer']

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '15'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 55})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "number_of_task":
            if '_changelist_filters' in request.GET:
                query = NumberTaskOge.objects.all()
                s = request.GET['_changelist_filters'].split('&')
                for i in s:
                    if 'number_of_task__id__exact' in i:
                        query = query.filter(number=int(i.split('=')[1]))
                        break
                kwargs["queryset"] = query

        elif db_field.name == "category":
            if '_changelist_filters' in request.GET:
                query = CategoryOge.objects.all()
                s = request.GET['_changelist_filters'].split('&')
                for i in s:
                    if 'number_of_task__id__exact' in i:
                        query = query.filter(number_task=int(i.split('=')[1]))
                        break
                kwargs["queryset"] = query
            elif "number_of_task__number__exact" in request.GET:
                s = request.GET["number_of_task__number__exact"]
                query = CategoryOge.objects.all().filter(number_task=int(s))
                kwargs["queryset"] = query

        return super(AdminQuestionsOGE, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AdminNumberTaskOGE(admin.ModelAdmin):
    list_display = ["number", "title", "seo_description", "seo_keywords"]
    list_editable = ["title", 'seo_description', 'seo_keywords']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '15'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 45})},
    }


class AdminCategoryOGE(admin.ModelAdmin):
    list_display = ['number_task', 'text']


class AdminVariantOGE(admin.ModelAdmin):
    list_display = ['number_var']
    ordering = ['number_var']

class AdminVideoRazborOGE(admin.ModelAdmin):
    list_display = ['url_video','number_of_task','seo_description','seo_keywords']
    ordering = ['number_of_task']

admin.site.register(QuestionsOge, AdminQuestionsOGE)
admin.site.register(NumberTaskOge, AdminNumberTaskOGE)
admin.site.register(CategoryOge, AdminCategoryOGE)
admin.site.register(VariantOge, AdminVariantOGE)
admin.site.register(VideoRazborOGE, AdminVideoRazborOGE)
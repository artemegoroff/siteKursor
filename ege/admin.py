from django.contrib import admin
from .models import QuestionsEGE, NumberTaskEge, CategoryEge, VarEge, VideoRazborEGE
from django.forms import TextInput, Textarea, Select
from django.db import models


# Register your models here.
class AdminQuestionsEGE(admin.ModelAdmin):
    list_display = ["number_of_task", "text", "number_of_variant", "passed"]
    # list_select_related = ('number_of_task',)
    list_filter = ['number_of_task', 'number_of_variant']
    save_as = True
    save_on_top = True
    list_editable = ['text', 'number_of_variant']

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 55})},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "number_of_task":
            if '_changelist_filters' in request.GET:
                query = NumberTaskEge.objects.all()
                s = request.GET['_changelist_filters'].split('&')
                for i in s:
                    if 'number_of_task__number__exact' in i:
                        query = query.filter(number=int(i.split('=')[1]))
                        break
                kwargs["queryset"] = query

        elif db_field.name == "category":
            if '_changelist_filters' in request.GET:
                query = CategoryEge.objects.all()
                s = request.GET['_changelist_filters'].split('&')
                for i in s:
                    if 'number_of_task__number__exact' in i:
                        query = query.filter(number_task=int(i.split('=')[1]))
                        break
                kwargs["queryset"] = query
            elif "number_of_task__number__exact" in request.GET:
                s = request.GET["number_of_task__number__exact"]
                query = CategoryEge.objects.all().filter(number_task=int(s))
                kwargs["queryset"] = query

        return super(AdminQuestionsEGE, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AdminNumberTaskEge(admin.ModelAdmin):
    list_display = ["number", "title", "seo_description", "seo_keywords"]
    list_editable = ["title", 'seo_description', 'seo_keywords']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '15'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 10, 'cols': 45})},
    }

class AdminCategoryEge(admin.ModelAdmin):
    list_display = ['number_task', 'text']


class AdminVariantEge(admin.ModelAdmin):
    list_display = ['number_var']
    ordering = ['number_var']


class AdminVideoRazborEGE(admin.ModelAdmin):
    list_display = ['id', 'url_video', 'number_of_task']
    list_editable = ['url_video', 'number_of_task']
    filter_horizontal = ['treoryKnowledge']


admin.site.register(QuestionsEGE, AdminQuestionsEGE)
admin.site.register(NumberTaskEge, AdminNumberTaskEge)
admin.site.register(CategoryEge, AdminCategoryEge)
admin.site.register(VarEge, AdminVariantEge)
admin.site.register(VideoRazborEGE, AdminVideoRazborEGE)

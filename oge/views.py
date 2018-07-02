from django.shortcuts import render
from .models import QuestionsOge, NumberTaskOge, VariantOge,CategoryOge


def oge_home_page(request):
    tasksOge = NumberTaskOge.objects.all()
    varsOge = VariantOge.objects.all().order_by('number_var')
    if len(varsOge) % 3 == 0:
        kol_elem_in_group = len(varsOge) // 3
    else:
        kol_elem_in_group = len(varsOge) // 3 + 1
    groups = [i * kol_elem_in_group + 1 for i in range(3)]
    context = {}
    context['tasksOge'] = tasksOge
    context['varsOge'] = varsOge
    context['groups'] = groups
    context['kol'] = kol_elem_in_group
    return render(request, 'oge/oge_home.html', context)


def oge_task_list(request):
    tasks = NumberTaskOge.objects.all()
    return render(request, 'task_list_all.html', {'tasks': tasks})


def oge_task_detail(request, number_task):
    exam = 'oge'
    tasks_prism = [6, 8, 9, 10]
    questions = QuestionsOge.objects.filter(number_of_task=number_task)
    category = list(CategoryOge.objects.filter(number_task=number_task))
    if len(category) != 1:
        category += ['Все']
    if request.method == "POST":
        text_cat = request.GET.get("category_sel", 'Все')
        if text_cat != 'Все':
            id_cat = CategoryOge.objects.all().get(text=text_cat)
            questions = questions.filter(number_of_task=number_task).filter(category=id_cat)
        for dataPost in request.POST:
            if not ('input' in dataPost or 'radio' in dataPost):
                continue
            num = int(dataPost[5:])
            for i in range(len(questions)):
                if questions[i].id == num:
                    if request.POST[dataPost] == "":
                        questions[i].status = 'empty'
                    elif request.POST[dataPost].lower() != questions[i].answer.lower():
                        questions[i].status = 'wrong'
                    else:
                        questions[i].status = 'good'
                    questions[i].old_answer = request.POST[dataPost]
                    break
    elif request.method == "GET":
        text_cat = request.GET.get("category_sel", 'Все')
        if text_cat != "Все":
            id_cat = CategoryOge.objects.all().get(text=text_cat)
            questions = questions.filter(number_of_task=number_task).filter(category=id_cat)
    questions=list(questions)
    tasks = NumberTaskOge.objects.all()
    context = {"questions": questions, 'tasks': tasks, 'number_task': NumberTaskOge.objects.all().get(number=number_task), 'exam': exam,'tasks_prism':tasks_prism, 'category':category}

    return render(request, 'task_detail.html', context)

def oge_get_var(request,variant_number):
    exam = 'oge_var'
    tasks_prism = ['6', '8', '9', '10']
    var = VariantOge.objects.get(number_var=int(variant_number))
    questions = list(QuestionsOge.objects.filter(number_of_variant=var).order_by('number_of_task'))
    if request.method == "POST":
        for dataPost in request.POST:
            if not ('input' in dataPost or 'radio' in dataPost):
                continue
            num = int(dataPost[5:])
            for i in range(len(questions)):
                if questions[i].id == num:
                    if request.POST[dataPost] != questions[i].answer:
                        questions[i].status = 'wrong'
                    else:
                        questions[i].status = 'good'
                    questions[i].old_answer = request.POST[dataPost]
                    break
    tasks = VariantOge.objects.all().order_by('number_var')
    context = {"questions": questions, 'tasks': tasks, 'number_task': var, 'exam': exam,
               'tasks_prism': tasks_prism}

    return render(request, 'task_detail.html', context)
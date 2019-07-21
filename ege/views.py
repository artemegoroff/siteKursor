from django.shortcuts import render, get_object_or_404, redirect
from .models import QuestionsEGE, NumberTaskEge, VarEge, CategoryEge, VideoRazborEGE, CommentEge
from .forms import CommentForm
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import QuestionsEGE, NumberTaskEge, VarEge, CategoryEge, VideoRazborEGE

TASK_PRISM_JS = (8, 11, 14, 19, 20, 21, 24, 25)


def ege_home_page(request):
    context = {
        'videosEGE':len(VideoRazborEGE.objects.all()),
        'tasks': NumberTaskEge.objects.all(),
        'vars': VarEge.objects.all().order_by('number_var'),
        'numAllTask': len(QuestionsEGE.objects.all()),
    }

    count_video_parse = set(VideoRazborEGE.objects.values_list('number_of_task', flat=True).distinct())
    videos=[]
    for i in count_video_parse:
        videos.append(NumberTaskEge.objects.get(number=i))
    context['videos'] = videos
    return render(request, 'ege/ege_home.html', context)


def ege_task_detail(request, number_task):
    exam = 'ege'
    questions = QuestionsEGE.objects.filter(number_of_task=number_task)[::-1]
    category = list(CategoryEge.objects.filter(number_task=number_task))
    category.insert(0,'Все категории задания')
    text_cat = 'Все'
    if request.method == "POST":
        text_cat = request.POST.get("category_sel", 'Все')
        # if text_cat != 'Все':
        #     id_cat = CategoryEge.objects.get(text=text_cat)
        #     questions = QuestionsEGE.objects.filter(number_of_task=number_task).filter(category=id_cat)[::-1]
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
                        request.user.profile.fail_ege_tasks.add(questions[i].id)
                        request.user.profile.done_ege_tasks.remove(questions[i].id)
                        questions[i].failed += 1
                    else:
                        questions[i].status = 'good'
                        request.user.profile.done_ege_tasks.add(questions[i].id)
                        request.user.profile.fail_ege_tasks.remove(questions[i].id)
                        questions[i].passed += 1
                    questions[i].old_answer = request.POST[dataPost]
                    break

    questions = list(questions)
    tasks = NumberTaskEge.objects.all()
    context = {"questions": questions,
               'tasks': tasks,
               'number_task': NumberTaskEge.objects.all().get(number=number_task),
               'exam': exam,
               'tasks_prism': TASK_PRISM_JS,
               'category': category,
               'text_cat':text_cat}

    return render(request, 'task_detail.html', context)


def ege_get_var(request, variant_number):
    exam = 'ege_var'
    var = VarEge.objects.get(number_var=int(variant_number))
    questions = list(QuestionsEGE.objects.filter(number_of_variant=var).order_by('number_of_task'))
    if request.method == "POST":
        for dataPost in request.POST:
            if not ('input' in dataPost or 'radio' in dataPost):
                continue
            num = int(dataPost[5:])
            for i in range(len(questions)):
                if questions[i].id == num:
                    if request.POST[dataPost] != questions[i].answer:
                        questions[i].status = 'wrong'
                        request.user.profile.fail_ege_tasks.add(questions[i].id)
                        request.user.profile.done_ege_tasks.remove(questions[i].id)
                        questions[i].failed += 1
                    else:
                        questions[i].status = 'good'
                        request.user.profile.done_ege_tasks.add(questions[i].id)
                        request.user.profile.fail_ege_tasks.remove(questions[i].id)
                        questions[i].passed += 1
                    questions[i].old_answer = request.POST[dataPost]
                    break

    tasks = VarEge.objects.all().order_by('number_var')
    context = {"questions": questions,
               'tasks': tasks,
               'number_task': var,
               'exam': exam,
               'tasks_prism': TASK_PRISM_JS}

    return render(request, 'task_detail.html', context)


def ege_videotask_detail(request, id_theme, id_task):
    number_values = VideoRazborEGE.objects.values_list('number_of_task', flat=True).distinct()
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskEge.objects.get(number=cat))
    razbor = get_object_or_404(VideoRazborEGE, id=int(id_task))
    task = get_object_or_404(QuestionsEGE, q_url_video=razbor)
    context = {'vopros': task, 'video': razbor, 'tasks': numbers, 'exam': 'ege'}
    task = QuestionsEGE.objects.get(q_url_video=razbor)
    context = {'vopros': task,
               'video': razbor,
               'tasks': numbers,
               'exam':'ege'}

    return render(request, 'video_task_detail.html', context)


def ege_videotask_ONEtheme(request, id_theme):
    razbors = VideoRazborEGE.objects.filter(number_of_task=int(id_theme))
    number_values = set(VideoRazborEGE.objects.values_list('number_of_task', flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskEge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks': numbers, 'exam': 'ege'}

    return render(request, 'video_task_list.html', context)


def ege_videotask_AllTask(request):
    razbors = VideoRazborEGE.objects.all().order_by('-data_add')
    number_values = set(VideoRazborEGE.objects.values_list('number_of_task',flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskEge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks':numbers,'exam':'ege'}

    return render(request, 'video_task_list.html', context)


def ege_get_exercise(request, id_exercise):
    number_values = VideoRazborEGE.objects.values_list('number_of_task', flat=True).distinct()
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskEge.objects.get(number=cat))
    task = get_object_or_404(QuestionsEGE, id=int(id_exercise))
    comments = CommentEge.objects.filter(task_ege=task.id, reply=None).order_by('-id')
    comment_form = CommentForm()
    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')
        if user_answer and user_answer.lower() != task.answer.lower():
            task.status = 'wrong'
            request.user.profile.fail_ege_tasks.add(task.id)
            request.user.profile.done_ege_tasks.remove(task.id)
        else:
            task.status = 'good'
            request.user.profile.done_ege_tasks.add(task.id)
            request.user.profile.fail_ege_tasks.remove(task.id)
        task.old_answer = user_answer
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = CommentEge.objects.get(id=reply_id)
            comment = CommentEge.objects.create(task_ege=task, user=request.user, content=content, reply=comment_qs)
            comment.save()
            return redirect('ege:ege_get_exercise', id_exercise=task.id)

    context = {
        'vopros': task,
        'tasks': numbers,
        'exam': 'ege',
        'comments': comments,
        'comment_form': comment_form
    }

    if request.is_ajax():
        html = render_to_string('partitions/_comments.html', context=context, request=request)
        return JsonResponse({'form':html})


    return render(request, 'exercise.html', context)

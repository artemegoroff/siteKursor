from django.shortcuts import render,get_object_or_404,redirect
from .models import QuestionsOge, NumberTaskOge, VariantOge,CategoryOge,VideoRazborOGE, CommentOge
from .forms import CommentForm
from django.template.loader import render_to_string
from django.http import JsonResponse


def oge_home_page(request):
    tasksOge = NumberTaskOge.objects.all()
    varsOge = VariantOge.objects.all().order_by('number_var')
    videosOGE = len(VideoRazborOGE.objects.all())

    context = {}
    context['tasks'] = tasksOge
    context['vars'] = varsOge
    context['videosOGE'] = videosOGE
    context['numAllTask'] = len(QuestionsOge.objects.all())

    numbersVideoRazbor = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    videos = []
    for i in numbersVideoRazbor:
        videos.append(NumberTaskOge.objects.get(number=i))
    context['videos'] = videos

    return render(request, 'oge/oge_home.html', context)


def oge_task_detail(request, number_task):
    exam = 'oge'
    tasks_prism = [6, 8, 9, 10]
    questions = QuestionsOge.objects.filter(number_of_task=number_task)
    category = list(CategoryOge.objects.filter(number_task=number_task))
    category.insert(0, 'Все категории задания')
    text_cat = 'Все'
    if request.method == "POST":
        text_cat = request.POST.get("category_sel", 'Все')
        # if text_cat != 'Все':
        #     id_cat = CategoryOge.objects.all().get(text=text_cat)
        #     questions = questions.filter(number_of_task=number_task).filter(category=id_cat)
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
                        request.user.profile.fail_oge_tasks.add(questions[i].id)
                        request.user.profile.done_oge_tasks.remove(questions[i].id)
                    else:
                        questions[i].status = 'good'
                        request.user.profile.done_oge_tasks.add(questions[i].id)
                        request.user.profile.fail_oge_tasks.remove(questions[i].id)
                    questions[i].old_answer = request.POST[dataPost]
                    break
    questions=list(questions)
    tasks = NumberTaskOge.objects.all()
    context = {"questions": questions, 'tasks': tasks,
               'number_task': NumberTaskOge.objects.all().get(number=number_task),
               'exam': exam,'tasks_prism':tasks_prism,
               'category':category,'text_cat':text_cat}

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


def oge_videotask_detail(request, id_theme, id_task):
    number_values = VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct()
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))
    razbor = get_object_or_404(VideoRazborOGE, id=int(id_task))
    task = QuestionsOge.objects.get(q_url_video=razbor)
    context = {'vopros': task, 'video': razbor,'tasks': numbers,'exam':'oge'}

    return render(request, 'video_task_detail.html', context)


def oge_videotask_ONEtheme(request, id_theme):
    razbors = VideoRazborOGE.objects.filter(number_of_task=int(id_theme))
    number_values = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks': numbers, 'exam': 'oge'}

    return render(request, 'video_task_list.html', context)


def oge_videotask_AllTask(request):
    razbors = VideoRazborOGE.objects.all().order_by('-data_add')
    number_values = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks': numbers, 'exam': 'ege'}

    return render(request, 'video_task_list.html', context)


def oge_get_exercise(request, id_exercise):
    number_values = VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct()
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))
    task = get_object_or_404(QuestionsOge, id=int(id_exercise))
    comments = CommentOge.objects.filter(task_ege=task.id, reply=None).order_by('-id')
    comment_form = CommentForm()
    if request.method == 'POST':
        user_answer = request.POST.get('user_answer')
        if user_answer and user_answer.lower() != task.answer.lower():
            task.status = 'wrong'
            request.user.profile.fail_oge_tasks.add(task.id)
            request.user.profile.done_oge_tasks.remove(task.id)
        else:
            task.status = 'good'
            request.user.profile.done_oge_tasks.add(task.id)
            request.user.profile.fail_oge_tasks.remove(task.id)
        task.old_answer = user_answer
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = CommentOge.objects.get(id=reply_id)
            comment = CommentOge.objects.create(task_ege=task, user=request.user, content=content, reply=comment_qs)
            comment.save()
            return redirect('oge:oge_get_exercise', id_exercise=task.id)

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
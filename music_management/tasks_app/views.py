from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.models import Project, ProjectMember
from .models import Task
from notifications.models import Notification
from core.models import Activity
from django.contrib.auth.models import User


@login_required
def task_list(request, project_id):
    """Список задач проекта"""
    project = get_object_or_404(Project, pk=project_id)

    # Проверка доступа
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, 'У вас нет доступа к этому проекту')
        return redirect('project_list')

    tasks = Task.objects.filter(project=project)
    members = ProjectMember.objects.filter(project=project)

    return render(request, 'tasks_app/list.html', {
        'project': project,
        'tasks': tasks,
        'members': members
    })


@login_required
def task_create(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)

        title = request.POST.get('title')
        description = request.POST.get('description', '')
        assignee_id = request.POST.get('assignee')
        due_date = request.POST.get('due_date') or None
        priority = request.POST.get('priority', 2)

        if title:
            task = Task.objects.create(
                project=project,
                title=title,
                description=description,
                assignee_id=assignee_id if assignee_id else None,
                due_date=due_date,
                priority=priority,
                created_by=request.user
            )

            Activity.objects.create(
                user=request.user,
                project=project,
                type='task_created',
                message=f'Создал задачу "{title}"'
            )

            # СОЗДАЕМ УВЕДОМЛЕНИЕ ДЛЯ ИСПОЛНИТЕЛЯ
            if assignee_id and int(assignee_id) != request.user.id:  # Не отправляем себе
                Notification.objects.create(
                    user_id=assignee_id,
                    type='task_assigned',
                    message=f'Вам назначена задача "{title}" в проекте {project.title}',
                    related_object_id=task.id
                )

            messages.success(request, f'Задача "{title}" создана!')

    return redirect('task_list', project_id=project_id)


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == 'POST':
        old_status = task.status
        new_status = request.POST.get('status')

        task.title = request.POST.get('title')
        task.description = request.POST.get('description', '')
        task.status = new_status
        task.assignee_id = request.POST.get('assignee') or None
        task.due_date = request.POST.get('due_date') or None
        task.priority = request.POST.get('priority', 2)
        task.save()

        # Если задача выполнена и статус изменился на done
        if new_status == 'done' and old_status != 'done':
            Activity.objects.create(
                user=request.user,
                project=task.project,
                type='task_completed',
                message=f'Выполнил задачу "{task.title}"'
            )
            if task.created_by != request.user:  # Не отправляем себе
                Notification.objects.create(
                    user=task.created_by,
                    type='task_completed',
                    message=f'Задача "{task.title}" выполнена пользователем {request.user.username}',
                    related_object_id=task.id
                )

        messages.success(request, 'Задача обновлена!')
        return redirect('task_list', project_id=task.project.id)

    members = ProjectMember.objects.filter(project=task.project)
    return render(request, 'tasks_app/edit.html', {
        'task': task,
        'members': members
    })

@login_required
def task_delete(request, task_id):
    """Удаление задачи"""
    task = get_object_or_404(Task, pk=task_id)
    project_id = task.project.id
    task.delete()
    messages.success(request, 'Задача удалена!')
    return redirect('task_list', project_id=project_id)


@login_required
def my_tasks(request):
    """Мои задачи (назначенные мне)"""
    tasks = Task.objects.filter(assignee=request.user).select_related('project')
    return render(request, 'tasks_app/my_tasks.html', {'tasks': tasks})

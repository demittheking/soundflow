from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, ProjectMember
from django.contrib.auth.models import User
from core.models import Activity


@login_required
def project_list(request):
    # Получаем все проекты, где пользователь является участником
    projects = Project.objects.filter(members__user=request.user).distinct()
    return render(request, 'projects/list.html', {'projects': projects})


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Проверяем, имеет ли пользователь доступ к проекту
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, 'У вас нет доступа к этому проекту')
        return redirect('project_list')
    return render(request, 'projects/detail.html', {'project': project})


@login_required
def project_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        cover = request.FILES.get('cover')  # ЭТА СТРОКА ДОЛЖНА БЫТЬ

        if title:
            project = Project.objects.create(
                owner=request.user,
                title=title,
                description=description,
                cover=cover  # ИСПРАВЛЕНО: cover определена выше
            )
            ProjectMember.objects.create(
                project=project,
                user=request.user,
                role='owner'
            )

            # Добавляем активность
            Activity.objects.create(
                user=request.user,
                project=project,
                type='project_created',
                message=f'Создал новый проект "{title}"'
            )

            messages.success(request, f'Проект "{title}" успешно создан!')
            return redirect('project_detail', pk=project.pk)

    return render(request, 'projects/create.html')


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Проверяем, что пользователь - владелец
    if project.owner != request.user:
        messages.error(request, 'Только владелец может редактировать проект')
        return redirect('project_detail', pk=project.pk)

    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')

        # Обработка новой обложки
        if request.FILES.get('cover'):
            # Удаляем старую обложку если есть
            if project.cover:
                project.cover.delete()
            project.cover = request.FILES.get('cover')

        project.save()
        messages.success(request, 'Проект обновлен!')
        return redirect('project_detail', pk=project.pk)

    return render(request, 'projects/edit.html', {'project': project})


@login_required
def project_members(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'viewer')

        try:
            user_to_invite = User.objects.get(email=email)
            # Проверяем, не состоит ли уже в проекте
            if not ProjectMember.objects.filter(project=project, user=user_to_invite).exists():
                ProjectMember.objects.create(
                    project=project,
                    user=user_to_invite,
                    role=role,
                    invited_by=request.user
                )
                messages.success(request, f'Пользователь {user_to_invite.username} добавлен в проект')
            else:
                messages.error(request, 'Пользователь уже состоит в проекте')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден')

        return redirect('project_members', pk=project.pk)

    members = ProjectMember.objects.filter(project=project).select_related('user')
    return render(request, 'projects/members.html', {'project': project, 'members': members})

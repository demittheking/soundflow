from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.models import Project, ProjectMember
from .models import Activity, Profile
from .forms import CustomUserCreationForm


@login_required
def home(request):
    projects = Project.objects.filter(members__user=request.user).distinct()
    user_project_ids = projects.values_list('id', flat=True)
    activities = Activity.objects.filter(project_id__in=user_project_ids)[:20]
    return render(request, 'core/home.html', {'projects': projects, 'activities': activities})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Профиль создастся автоматически через сигнал
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def change_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        # Проверяем и создаем профиль если его нет
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Удаляем старый аватар если есть
        if profile.avatar:
            profile.avatar.delete()

        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Аватар успешно обновлен!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))
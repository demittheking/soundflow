from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from projects.models import Project, ProjectMember
from .models import Track, AudioFile
from core.models import Activity
import os


@login_required
def track_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, 'У вас нет доступа к этому проекту')
        return redirect('project_list')

    tracks = Track.objects.filter(project=project)
    return render(request, 'tracks/list.html', {'project': project, 'tracks': tracks})


@login_required
def track_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        position = request.POST.get('position', 1)

        if title:
            track = Track.objects.create(
                project=project,
                title=title,
                position=position,
                bpm=request.POST.get('bpm') or None,
                key=request.POST.get('key', ''),
                status=request.POST.get('status', 'demo')
            )
            # Добавляем активность
            Activity.objects.create(
                user=request.user,
                project=project,
                type='track_created',
                message=f'Создал трек "{title}" в проекте {project.title}'
            )
            messages.success(request, f'Трек "{title}" создан!')
            return redirect('track_list', project_id=project.pk)

    return render(request, 'tracks/create.html', {'project': project})


@login_required
def track_detail(request, pk):
    track = get_object_or_404(Track, pk=pk)
    if not ProjectMember.objects.filter(project=track.project, user=request.user).exists():
        messages.error(request, 'У вас нет доступа к этому треку')
        return redirect('project_list')

    audio_files = track.audio_files.all()
    return render(request, 'tracks/detail.html', {'track': track, 'audio_files': audio_files})


@login_required
def track_edit(request, pk):
    track = get_object_or_404(Track, pk=pk)

    if request.method == 'POST':
        track.title = request.POST.get('title')
        track.bpm = request.POST.get('bpm') or None
        track.key = request.POST.get('key', '')
        track.status = request.POST.get('status')
        track.position = request.POST.get('position', 1)
        track.save()
        messages.success(request, 'Трек обновлен!')
        return redirect('track_detail', pk=track.pk)

    return render(request, 'tracks/edit.html', {'track': track})


@login_required
def audio_upload(request, track_id):
    track = get_object_or_404(Track, pk=track_id)

    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        version_comment = request.POST.get('version_comment', '')

        # Проверяем расширение файла
        ext = os.path.splitext(audio_file.name)[1].lower()
        if ext not in ['.mp3', '.wav', '.ogg', '.m4a']:
            messages.error(request, 'Поддерживаются только аудиофайлы (MP3, WAV, OGG, M4A)')
            return redirect('track_detail', pk=track.pk)

        # Сохраняем файл
        file_path = default_storage.save(
            f'audio/{track.project.id}/{track.id}/{audio_file.name}',
            ContentFile(audio_file.read())
        )

        # Создаем запись в БД
        audio = AudioFile.objects.create(
            track=track,
            original_filename=audio_file.name,
            file=file_path,
            file_size=audio_file.size,
            version_comment=version_comment,
            uploaded_by=request.user
        )
        if audio_file:
            Activity.objects.create(
                user=request.user,
                project=track.project,
                type='audio_uploaded',
                message=f'Загрузил новую версию аудио для трека "{track.title}"'
            )
        messages.success(request, f'Файл "{audio_file.name}" загружен! Версия {audio.version}')

    return redirect('track_detail', pk=track.pk)


@login_required
def audio_delete(request, audio_id):
    audio = get_object_or_404(AudioFile, pk=audio_id)
    track_id = audio.track.id

    # Проверяем права (только владелец проекта или загрузивший)
    if request.user != audio.track.project.owner and request.user != audio.uploaded_by:
        messages.error(request, 'У вас нет прав на удаление этого файла')
        return redirect('track_detail', pk=track_id)

    # Удаляем файл с диска
    if audio.file:
        audio.file.delete()

    audio.delete()
    messages.success(request, 'Файл удален')
    return redirect('track_detail', pk=track_id)
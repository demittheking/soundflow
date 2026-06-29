from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import AudioFile, AudioComment
from notifications.models import Notification
from projects.models import ProjectMember
from core.models import Activity
import json

# Добавь вспомогательную функцию форматирования времени
def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

@login_required
@require_http_methods(["GET"])
def get_comments(request):
    audio_file_id = request.GET.get('audio_file_id')
    if not audio_file_id:
        return JsonResponse({'error': 'audio_file_id required'}, status=400)

    try:
        audio_file = AudioFile.objects.get(pk=audio_file_id)
    except AudioFile.DoesNotExist:
        return JsonResponse({'error': 'Audio file not found'}, status=404)

    comments = AudioComment.objects.filter(audio_file=audio_file).select_related('author')

    data = [{
        'id': c.id,
        'text': c.text,
        'timestamp_seconds': c.timestamp_seconds,
        'is_resolved': c.is_resolved,
        'created_at': c.created_at.isoformat(),
        'author_username': c.author.username,
        'author_id': c.author.id,
    } for c in comments]

    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
def add_comment(request):
    try:
        data = json.loads(request.body)
        audio_file_id = data.get('audio_file_id')
        text = data.get('text')
        timestamp_seconds = data.get('timestamp_seconds')

        if not all([audio_file_id, text, timestamp_seconds is not None]):
            return JsonResponse({'error': 'Missing fields'}, status=400)

        audio_file = AudioFile.objects.get(pk=audio_file_id)
        project = audio_file.track.project

        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            return JsonResponse({'error': 'No permission'}, status=403)

        comment = AudioComment.objects.create(
            audio_file=audio_file,
            author=request.user,
            text=text,
            timestamp_seconds=int(timestamp_seconds)
        )

        # УВЕДОМЛЕНИЯ ДЛЯ ВСЕХ УЧАСТНИКОВ КРОМЕ АВТОРА
        members = ProjectMember.objects.filter(project=project).exclude(user=request.user)
        for member in members:
            Notification.objects.create(
                user=member.user,
                type='comment',
                message=f'{request.user.username} оставил комментарий в треке {audio_file.track.title}',
                related_object_id=comment.id
            )
        Activity.objects.create(
            user=request.user,
            project=project,
            type='comment_added',
            message=f'Добавил комментарий в треке "{audio_file.track.title}" на {format_time(timestamp_seconds)}'
        )

        return JsonResponse({'success': True, 'id': comment.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def resolve_comment(request, comment_id):
    try:
        comment = AudioComment.objects.get(pk=comment_id)
        project = comment.audio_file.track.project

        # Только участники проекта могут решать комментарии
        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            return JsonResponse({'error': 'No permission'}, status=403)

        comment.is_resolved = True
        comment.save()

        return JsonResponse({'success': True})

    except AudioComment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)
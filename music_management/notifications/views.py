from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def unread_count(request):
    """Количество непрочитанных уведомлений"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def notification_list(request):
    """Список уведомлений (последние 10)"""
    notifications = Notification.objects.filter(user=request.user)[:10]
    data = [{
        'id': n.id,
        'message': n.message,
        'type': n.type,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%d.%m.%Y %H:%M'),
        'related_object_id': n.related_object_id
    } for n in notifications]
    return JsonResponse(data, safe=False)

@login_required
def mark_as_read(request, notification_id):
    """Отметить уведомление как прочитанное"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)

@login_required
def mark_all_read(request):
    """Отметить все уведомления как прочитанные"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
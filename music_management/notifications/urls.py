from django.urls import path
from . import views

urlpatterns = [
    path('api/unread-count/', views.unread_count, name='api_unread_count'),
    path('api/list/', views.notification_list, name='api_notification_list'),
    path('api/mark/<int:notification_id>/read/', views.mark_as_read, name='api_mark_read'),
    path('api/mark-all-read/', views.mark_all_read, name='api_mark_all_read'),
]
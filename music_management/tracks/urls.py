from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Основные URL
    path('project/<int:project_id>/', views.track_list, name='track_list'),
    path('project/<int:project_id>/create/', views.track_create, name='track_create'),
    path('<int:pk>/', views.track_detail, name='track_detail'),
    path('<int:pk>/edit/', views.track_edit, name='track_edit'),
    path('<int:track_id>/upload/', views.audio_upload, name='audio_upload'),
    path('audio/<int:audio_id>/delete/', views.audio_delete, name='audio_delete'),

    # API для комментариев
    path('api/comments/', api_views.get_comments, name='api_get_comments'),
    path('api/comments/add/', api_views.add_comment, name='api_add_comment'),
    path('api/comments/<int:comment_id>/resolve/', api_views.resolve_comment, name='api_resolve_comment'),
]
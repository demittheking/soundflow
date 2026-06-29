from django.urls import path
from . import views

urlpatterns = [
    path('project/<int:project_id>/', views.task_list, name='task_list'),
    path('project/<int:project_id>/create/', views.task_create, name='task_create'),
    path('<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),  # Этот маршрут должен быть
]
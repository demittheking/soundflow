from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнена'),
    )

    PRIORITY_CHOICES = (
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    due_date = models.DateField(null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
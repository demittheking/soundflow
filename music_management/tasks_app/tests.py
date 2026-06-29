from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project, ProjectMember
from .models import Task
from django.urls import reverse


class TasksTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.project = Project.objects.create(
            owner=self.user,
            title='Project with Tasks'
        )
        ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role='owner'
        )

    def test_create_task(self):
        """Тест создания задачи"""
        response = self.client.post(
            reverse('task_create', args=[self.project.id]),
            {
                'title': 'Mix the track',
                'description': 'Need to mix the vocals',
                'priority': '3'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'Mix the track')
        self.assertEqual(task.priority, 3)

    def test_task_status_update(self):
        """Тест обновления статуса задачи"""
        task = Task.objects.create(
            project=self.project,
            title='Recording',
            status='todo',
            created_by=self.user
        )
        task.status = 'in_progress'
        task.save()
        self.assertEqual(task.status, 'in_progress')

    def test_my_tasks_view(self):
        """Тест страницы 'Мои задачи'"""
        Task.objects.create(
            project=self.project,
            title='Assigned Task',
            assignee=self.user,
            created_by=self.user
        )
        response = self.client.get(reverse('my_tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Assigned Task')
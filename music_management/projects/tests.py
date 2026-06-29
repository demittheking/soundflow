from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, ProjectMember


class ProjectsTest(TestCase):

    def setUp(self):
        """Создаем тестового пользователя"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_create_project(self):
        """Тест создания проекта"""
        response = self.client.post(reverse('project_create'), {
            'title': 'Test Project',
            'description': 'Test Description'
        })
        # Проверяем редирект после создания
        self.assertEqual(response.status_code, 302)
        # Проверяем, что проект создался
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.first()
        self.assertEqual(project.title, 'Test Project')
        self.assertEqual(project.owner, self.user)

    def test_project_list_view(self):
        """Тест отображения списка проектов"""
        # Создаем проект и добавляем пользователя как участника
        project = Project.objects.create(
            owner=self.user,
            title='My Project',
            description='Test'
        )
        ProjectMember.objects.create(
            project=project,
            user=self.user,
            role='owner'
        )
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Project')

    def test_project_detail_view(self):
        """Тест страницы деталей проекта"""
        project = Project.objects.create(
            owner=self.user,
            title='Detail Project',
            description='Test Detail'
        )
        # Добавляем пользователя как участника
        ProjectMember.objects.create(
            project=project,
            user=self.user,
            role='owner'
        )
        response = self.client.get(reverse('project_detail', args=[project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Project')

    def test_add_member_to_project(self):
        """Тест добавления участника в проект"""
        project = Project.objects.create(
            owner=self.user,
            title='Team Project'
        )
        # Добавляем владельца как участника
        ProjectMember.objects.create(
            project=project,
            user=self.user,
            role='owner'
        )
        new_user = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='pass123'
        )
        ProjectMember.objects.create(
            project=project,
            user=new_user,
            role='editor',
            invited_by=self.user
        )
        self.assertEqual(project.members.count(), 2)  # owner + member
        self.assertEqual(project.members.filter(role='editor').count(), 1)

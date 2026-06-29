from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Activity, Profile


class AuthTest(TestCase):

    def setUp(self):
        # Создаем тестового пользователя для тестов, где нужен авторизованный пользователь
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )

    def test_user_registration(self):
        """Тест регистрации пользователя"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        # Должен быть редирект на главную после регистрации
        self.assertEqual(response.status_code, 302)
        # Проверяем, что пользователь создался
        self.assertEqual(User.objects.count(), 2)  # testuser + newuser
        user = User.objects.get(username='newuser')
        self.assertEqual(user.username, 'newuser')

    def test_user_login(self):
        """Тест входа пользователя"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # редирект после входа

    def test_profile_creation(self):
        """Тест создания профиля при регистрации"""
        user = User.objects.create_user(
            username='profileuser',
            email='profile@test.com',
            password='pass123'
        )
        # Профиль должен создаться автоматически
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsNotNone(user.profile)

    def test_home_page_authenticated(self):
        """Тест главной страницы для авторизованного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        # Должен быть 200 OK, а не редирект
        self.assertEqual(response.status_code, 200)
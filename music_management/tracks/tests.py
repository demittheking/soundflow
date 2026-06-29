from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project, ProjectMember
from .models import Track, AudioFile, AudioComment
from django.urls import reverse


class TracksTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.project = Project.objects.create(
            owner=self.user,
            title='Music Project'
        )
        ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role='owner'
        )

    def test_create_track(self):
        """Тест создания трека"""
        response = self.client.post(
            reverse('track_create', args=[self.project.id]),
            {
                'title': 'New Song',
                'bpm': '120',
                'key': 'Cm'
            }
        )
        self.assertEqual(response.status_code, 302)  # редирект
        self.assertEqual(Track.objects.count(), 1)
        track = Track.objects.first()
        self.assertEqual(track.title, 'New Song')
        self.assertEqual(track.bpm, 120)

    def test_track_detail_view(self):
        """Тест страницы трека"""
        track = Track.objects.create(
            project=self.project,
            title='Test Track',
            position=1
        )
        response = self.client.get(reverse('track_detail', args=[track.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Track')

    def test_create_comment(self):
        """Тест создания комментария к аудио"""
        track = Track.objects.create(
            project=self.project,
            title='Track with Comments'
        )
        # Создаем тестовый аудиофайл (без реального файла)
        audio = AudioFile.objects.create(
            track=track,
            original_filename='test.mp3',
            file='test.mp3',
            file_size=1024,
            uploaded_by=self.user
        )
        comment = AudioComment.objects.create(
            audio_file=audio,
            author=self.user,
            text='Great track!',
            timestamp_seconds=30
        )
        self.assertEqual(AudioComment.objects.count(), 1)
        self.assertEqual(comment.text, 'Great track!')
        self.assertEqual(comment.timestamp_seconds, 30)
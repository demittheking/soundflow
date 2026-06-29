from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            # Оптимизируем изображение
            img = Image.open(self.avatar.path)
            if img.height > 200 or img.width > 200:
                output_size = (200, 200)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('project_created', 'Создан проект'),
        ('track_created', 'Создан трек'),
        ('audio_uploaded', 'Загружен аудиофайл'),
        ('comment_added', 'Добавлен комментарий'),
        ('task_created', 'Создана задача'),
        ('task_completed', 'Задача выполнена'),
        ('member_added', 'Добавлен участник'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    message = models.CharField(max_length=500)
    related_object_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
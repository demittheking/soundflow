from django.db import models
from django.contrib.auth.models import User
from projects.models import Project  # Абсолютный импорт, без точек


class Track(models.Model):
    STATUS_CHOICES = (
        ('demo', 'Демо'),
        ('recording', 'В записи'),
        ('mixing', 'На сведении'),
        ('mastering', 'На мастеринге'),
        ('done', 'Готов'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=200)
    position = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='demo')
    bpm = models.IntegerField(null=True, blank=True)
    key = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title


class AudioFile(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='audio_files')
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='audio/%Y/%m/%d/', null=True, blank=True)
    file_size = models.BigIntegerField(default=0)
    duration_seconds = models.IntegerField(null=True, blank=True)
    version = models.IntegerField(default=1)
    version_comment = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_audio')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['track', 'version']
        ordering = ['-version']

    def __str__(self):
        return f"{self.track.title} - v{self.version}"

    def save(self, *args, **kwargs):
        if not self.pk:
            max_version = AudioFile.objects.filter(track=self.track).aggregate(
                models.Max('version')
            )['version__max']
            if max_version:
                self.version = max_version + 1
        super().save(*args, **kwargs)


class AudioComment(models.Model):
    audio_file = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_comments')
    text = models.TextField()
    timestamp_seconds = models.IntegerField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp_seconds']

    def __str__(self):
        return f"Комментарий от {self.author.username} на {self.timestamp_seconds}с"
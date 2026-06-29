from django.contrib import admin
from .models import Track, AudioFile, AudioComment

admin.site.register(Track)
admin.site.register(AudioFile)
admin.site.register(AudioComment)
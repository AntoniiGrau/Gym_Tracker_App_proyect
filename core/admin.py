from django.contrib import admin
from .models import Exercise, TrainingHistory


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'muscle_group', 'video_url')
    search_fields = ('name', 'muscle_group')
    list_filter = ('muscle_group',)


@admin.register(TrainingHistory)
class TrainingHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exercise', 'series',
                    'reps', 'weight_kg', 'date')
    list_filter = ('date', 'user', 'exercise')
    search_fields = ('user_username', 'exercise_name')
    readonly_fields = ('date',)

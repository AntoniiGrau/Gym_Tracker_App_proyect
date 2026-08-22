from rest_framework import serializers
from .models import Exercise, TrainingHistory

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'muscle_group', ' video_url']

class HistorySerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)

    class Meta:
        model = TrainingHistory
        fields = ['id', 'user', 'exercise', 'exercise_name', 'date', 'series', 'reps', 'weight_kg' ]
        extra_kwargs = {'user': {'requierd': False}}
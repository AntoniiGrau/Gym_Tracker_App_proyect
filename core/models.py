from django.db import models
from django.contrib.auth.models import User

# exercise chart


class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='assigned_exercise', blank=True, null=True)
    name = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=50)
    video_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.muscle_group}) - for_ {self.user.username if self.user else 'ALL'}"

# Table to record the series that the user performs on their phone


class TrainingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    series = models.IntegerField()
    reps = models.IntegerField()
    weight_kg = models.FloatField()

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.decorators import api_view, permission_classes as decorator_permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .models import Exercise, TrainingHistory
from .serializers import ExerciseSerializer, HistorySerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_authenticated:
            return Exercise.objects.filter(user=current_user)
        return Exercise.objects.none()


class HistoryViewSet(viewsets.ModelViewSet):
    queryset = TrainingHistory.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [IsAuthenticated]

    # Filter so that the user only sees their own workouts.
    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_authenticated:
            return TrainingHistory.objects.filter(user=current_user)
        return TrainingHistory.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Self-service customer registration


@api_view(['POST'])
@decorator_permission_classes([AllowAny])
def register_client(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Basic engineering validation: avoid empty fields
    if not username or not password or not email:
        return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Security validation: verify that the username is not taken.
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"},  status=status.HTTP_400_BAD_REQUEST)

    # We create the user, automatically encrypting the password.
    user = User.objects.create_user(
        username=username, email=email, password=password)

    #  We generate your unique security token immediately.
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        "message": "User created successfully",
        "token": token.key,
        "user_id": user.id
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@decorator_permission_classes([AllowAny])
def home_index(request):
    return Response({
        "status": "Online",
        "project": "My Gym Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "dashboard": "/api/dashboard/",
            "exercises": "/api/exercises/",
            "history": "/api/history",
            "register": "/api/register/",
            "admin_panel": "/admin/"
        }
    })


@api_view(['GET'])
@decorator_permission_classes([AllowAny])
def dashboard_metrics(request):
    total_exercises_catalog = Exercise.objects.count()
    total_sets_logged = TrainingHistory.objects.count()
    distinct_workout_days = TrainingHistory.objects.values(
        'date').distinct().count()

    return Response({
        "Catalog_exercises": total_exercises_catalog,
        "total_sets": total_sets_logged,
        "completed_workouts": distinct_workout_days,
        "completion_rate": 75
    })

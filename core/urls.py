from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import ExerciseViewSet, HistoryViewSet, register_client, dashboard_metrics

# The router automatically generates clean URLs based on the views.
router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'history', HistoryViewSet, basename='history')

urlpatterns = [
    path('register/', register_client),
    path('login/', obtain_auth_token),
    path('dashboard/', dashboard_metrics),
    path('', include(router.urls)),
]

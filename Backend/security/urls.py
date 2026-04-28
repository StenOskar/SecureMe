from django.urls import path

from .views import AnalyzeTargetView, EmailCheckView, HealthCheckView, SecurityProfileDetailView, SecurityProfileListView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("analyze/", AnalyzeTargetView.as_view(), name="analyze-target"),
    path("email/check/", EmailCheckView.as_view(), name="email-check"),
    path("profiles/", SecurityProfileListView.as_view(), name="profile-list"),
    path("profiles/<int:pk>/", SecurityProfileDetailView.as_view(), name="profile-detail"),
]

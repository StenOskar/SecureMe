from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .analyzers import analyze_domain, analyze_email, normalize_domain
from .models import SecurityProfile
from .serializers import SecurityProfileSerializer


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "secureme-api"})


class AnalyzeTargetView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        domain = normalize_domain(
            email=request.data.get("email", ""),
            domain=request.data.get("domain", ""),
        )
        return Response(analyze_domain(domain))


class EmailCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        return Response(analyze_email(request.data.get("email", "")))


class SecurityProfileListView(generics.ListCreateAPIView):
    queryset = SecurityProfile.objects.order_by("-updated_at")
    serializer_class = SecurityProfileSerializer


class SecurityProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SecurityProfile.objects.all()
    serializer_class = SecurityProfileSerializer

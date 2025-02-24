from rest_framework import viewsets
from ioc_scraper.models import Vulnerability
from .serializers import VulnerabilitySerializer


class VulnerabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows vulnerabilities to be viewed, created, updated, or deleted.
    """
    queryset = Vulnerability.objects.all().order_by("-published_date")
    serializer_class = VulnerabilitySerializer
# Create your views here.

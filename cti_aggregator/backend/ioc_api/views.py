from rest_framework import viewsets
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel
from .serializers import VulnerabilitySerializer, IntelligenceArticleSerializer, CrowdStrikeIntelSerializer


class VulnerabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows vulnerabilities to be viewed, created, updated, or deleted.
    """
    queryset = Vulnerability.objects.all().order_by("-published_date")
    serializer_class = VulnerabilitySerializer

class IntelligenceArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows intelligence articles to be viewed.
    """
    queryset = IntelligenceArticle.objects.all().order_by("-published_date")
    serializer_class = IntelligenceArticleSerializer
    filterset_fields = ['source']
    search_fields = ['title', 'summary']

class CrowdStrikeIntelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows CrowdStrike threat intelligence to be viewed.
    """
    queryset = CrowdStrikeIntel.objects.all().order_by("-last_update_date")
    serializer_class = CrowdStrikeIntelSerializer
    filterset_fields = ['adversary_type']
    search_fields = ['name', 'description']

# Create your views here.

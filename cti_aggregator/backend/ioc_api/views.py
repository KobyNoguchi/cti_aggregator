from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, CharFilter, FilterSet
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel, CrowdStrikeMalware
from .serializers import VulnerabilitySerializer, IntelligenceArticleSerializer, CrowdStrikeIntelSerializer, CrowdStrikeMalwareSerializer
from django.db import models
import os
from django.http import FileResponse, HttpResponse
from django.conf import settings

# Custom filterset class for handling JSONField
class CustomFilterSet(FilterSet):
    class Meta:
        filter_overrides = {
            models.JSONField: {
                'filter_class': CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                }
            },
        }

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = type('CrowdStrikeIntelFilterSet', (CustomFilterSet,), {
        'Meta': type('Meta', (), {
            'model': CrowdStrikeIntel,
            'fields': ['adversary_type'],
            'filter_overrides': CustomFilterSet.Meta.filter_overrides
        })
    })

class CrowdStrikeMalwareViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows CrowdStrike malware families to be viewed.
    """
    queryset = CrowdStrikeMalware.objects.all().order_by("-publish_date")
    serializer_class = CrowdStrikeMalwareSerializer
    filterset_fields = ['name', 'threat_groups']  # Add back threat_groups
    search_fields = ['name', 'description']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = type('CrowdStrikeMalwareFilterSet', (CustomFilterSet,), {
        'Meta': type('Meta', (), {
            'model': CrowdStrikeMalware,
            'fields': ['name', 'threat_groups'],
            'filter_overrides': CustomFilterSet.Meta.filter_overrides
        })
    })

# CIRA Data endpoint
def get_cira_data(request):
    """
    Serve the CIRA_Data.xlsx file from the data_sources directory
    """
    file_path = os.path.join(settings.BASE_DIR, '..', 'data_sources', 'CIRA_Data.xlsx')
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as excel_file:
            response = HttpResponse(
                excel_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'inline; filename=CIRA_Data.xlsx'
            return response
    else:
        return HttpResponse(status=404, content="CIRA data file not found.")

# Create your views here.

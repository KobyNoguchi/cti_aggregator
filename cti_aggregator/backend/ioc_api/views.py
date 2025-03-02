from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, CharFilter, FilterSet
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel, CrowdStrikeMalware
from .serializers import (
    VulnerabilitySerializer, 
    IntelligenceArticleSerializer, 
    CrowdStrikeIntelSerializer, 
    CrowdStrikeMalwareSerializer, 
    CISAKevSerializer
)
from django.db import models
import os
import sys
import hashlib
import json
import logging
from django.http import FileResponse, HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q

# Configure logging
logger = logging.getLogger(__name__)

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

class CISAKevViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that specifically returns CISA KEV vulnerabilities.
    """
    # Define a more comprehensive filter to identify CISA KEV vulnerabilities
    # This approach uses multiple signals to identify vulnerabilities that came from CISA
    queryset = Vulnerability.objects.all().order_by("-published_date")
    
    def get_queryset(self):
        """
        Return vulnerabilities that match CISA KEV characteristics.
        We use multiple filter criteria to identify CISA KEV data:
        1. URLs containing cisa.gov (direct identification)
        2. CVE IDs that follow the CVE-YYYY-NNNNN format
        3. Vulnerabilities with the characteristics of CISA KEV data
        """
        # Build a comprehensive filter
        return Vulnerability.objects.filter(
            # Either the URL contains cisa.gov
            Q(source_url__contains="cisa.gov") |
            # Or it has a well-formed CVE ID and looks like KEV data
            (
                Q(cve_id__regex=r'^CVE-\d{4}-\d+$') &
                # Typically CISA KEV entries have these characteristics
                ~Q(vulnerability_name="Unknown") &
                ~Q(description="No description provided")
            )
        ).order_by("-published_date")
        
    serializer_class = CISAKevSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['cve_id', 'vulnerability_name', 'description']
    filterset_fields = ['severity']

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
    Provides comprehensive data about malware families, their characteristics,
    targeted industries, and associated threat groups.
    """
    # Override get_queryset to provide more comprehensive filtering
    def get_queryset(self):
        """
        Return CrowdStrike malware families with intelligent filtering.
        We use multiple criteria to ensure we get high-quality, relevant data:
        1. Filter by standard CrowdStrike attributes
        2. Ensure we have proper data characteristics (name, description)
        3. Sort by most recent publication date
        """
        return CrowdStrikeMalware.objects.filter(
            # Ensure we have meaningful data
            ~Q(name="") & 
            ~Q(description="") &
            # At least one of these fields should have meaningful content
            (
                ~Q(ttps=[]) | 
                ~Q(targeted_industries=[]) | 
                ~Q(threat_groups=[])
            )
        ).order_by("-publish_date")
    
    serializer_class = CrowdStrikeMalwareSerializer
    filterset_fields = ['name', 'threat_groups']
    search_fields = ['name', 'description', 'targeted_industries', 'ttps']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = type('CrowdStrikeMalwareFilterSet', (CustomFilterSet,), {
        'Meta': type('Meta', (), {
            'model': CrowdStrikeMalware,
            'fields': ['name', 'threat_groups', 'targeted_industries'],
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

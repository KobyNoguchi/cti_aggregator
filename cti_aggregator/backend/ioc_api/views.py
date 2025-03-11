from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend, CharFilter, FilterSet
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel, CrowdStrikeMalware, CISAKev, CrowdStrikeTailoredIntel
from .serializers import (
    VulnerabilitySerializer, 
    IntelligenceArticleSerializer, 
    CrowdStrikeIntelSerializer, 
    CrowdStrikeMalwareSerializer, 
    CISAKevSerializer,
    CrowdStrikeTailoredIntelSerializer
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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from ioc_scraper.tasks import fetch_all_intelligence
from datetime import datetime
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.views.decorators.cache import cache_control

# Add the data_sources directory to the path
sys.path.insert(0, os.path.join(settings.BASE_DIR, '..', 'data_sources'))

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

class CrowdStrikeTailoredIntelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows CrowdStrike Tailored Intelligence reports to be viewed.
    Provides comprehensive data about intelligence reports, including threat groups,
    targeted sectors, and report URLs.
    """
    queryset = CrowdStrikeTailoredIntel.objects.all().order_by("-publish_date")
    serializer_class = CrowdStrikeTailoredIntelSerializer
    filterset_fields = ['threat_groups', 'targeted_sectors']
    search_fields = ['title', 'summary']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

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

@api_view(['POST'])
@permission_classes([AllowAny])  # Consider requiring authentication in production
def refresh_intelligence(request):
    """
    Endpoint to manually trigger intelligence feed refresh
    """
    try:
        # Run the task synchronously for immediate feedback
        result = fetch_all_intelligence.delay()
        
        return JsonResponse({
            "status": "success",
            "message": "Intelligence refresh task started",
            "task_id": result.id
        })
    except Exception as e:
        logger.error(f"Error starting intelligence refresh: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Failed to start intelligence refresh: {str(e)}"
        }, status=500)

def threat_intelligence_feed(request):
    """
    Endpoint to display intelligence feed in a browser-friendly format.
    This is useful for debugging the backend data.
    """
    articles = IntelligenceArticle.objects.all().order_by('-published_date')
    
    # Group articles by source
    sources = articles.values_list('source', flat=True).distinct()
    articles_by_source = {}
    for source in sources:
        articles_by_source[source] = list(articles.filter(source=source).values('id', 'title', 'url', 'published_date', 'summary'))
    
    # Create a simple HTML response
    html = "<html><head><title>Threat Intelligence Feed</title>"
    html += "<style>"
    html += "body { font-family: Arial, sans-serif; margin: 20px; }"
    html += "h1 { color: #333; }"
    html += "h2 { color: #444; background-color: #f5f5f5; padding: 10px; margin-top: 30px; }"
    html += ".article { margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 15px; }"
    html += ".article h3 { margin: 0 0 5px 0; }"
    html += ".article .meta { color: #666; font-size: 0.8em; margin-bottom: 8px; }"
    html += ".article .summary { font-size: 0.9em; }"
    html += "</style></head><body>"
    html += "<h1>Threat Intelligence Feed</h1>"
    html += f"<p>Total articles: {articles.count()}</p>"
    
    for source, source_articles in articles_by_source.items():
        html += f"<h2>{source} ({len(source_articles)} articles)</h2>"
        for article in source_articles:
            published_date = article['published_date'].strftime('%Y-%m-%d %H:%M:%S') if article['published_date'] else 'Unknown'
            html += f"<div class='article'>"
            html += f"<h3><a href='{article['url']}' target='_blank'>{article['title']}</a></h3>"
            html += f"<div class='meta'>Published: {published_date} | ID: {article['id']}</div>"
            html += f"<div class='summary'>{article['summary']}</div>"
            html += "</div>"
    
    html += "</body></html>"
    return HttpResponse(html)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_crowdstrike_api(request):
    """
    Endpoint to test connection to CrowdStrike API
    """
    try:
        # Try importing the function to check falconpy availability
        try:
            # Import here to avoid circular imports
            from tailored_intelligence import FALCONPY_AVAILABLE
            
            if not FALCONPY_AVAILABLE:
                return JsonResponse({
                    "status": "warning",
                    "message": "FalconPy library is not installed. This is non-critical for development.",
                    "details": {
                        "solution": "Install falconpy with: pip install falconpy"
                    }
                })
            
            from tailored_intelligence import fetch_tailored_intel
            
            # For testing we use mock credentials
            mock_reports = fetch_tailored_intel("test-client-id", "test-client-secret")
            
            return JsonResponse({
                "status": "success",
                "message": "Using mock CrowdStrike data for development",
                "reports_sample": mock_reports[:2] if len(mock_reports) > 0 else []
            })
            
        except ImportError as e:
            return JsonResponse({
                "status": "error",
                "message": f"Failed to import necessary modules: {str(e)}",
                "details": {
                    "error_type": "ImportError"
                }
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Error testing CrowdStrike API: {str(e)}",
        }, status=500)

@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
@cache_control(max_age=300)  # Cache for 5 minutes
def health_check(request):
    """
    API endpoint that returns the health status of the API.
    This can be used by frontend applications to verify connectivity.
    """
    # Check if we're responding to a HEAD request (used for connectivity checks)
    if request.method == 'HEAD':
        return Response(status=HTTP_200_OK)
    
    # Get basic system statistics
    try:
        article_count = IntelligenceArticle.objects.count()
        intel_count = CrowdStrikeTailoredIntel.objects.count()
        actor_count = CrowdStrikeIntel.objects.count()
        malware_count = CrowdStrikeMalware.objects.count()
        
        # Get latest update timestamps
        latest_article = IntelligenceArticle.objects.order_by('-published_date').first()
        latest_intel = CrowdStrikeTailoredIntel.objects.order_by('-last_updated').first()
        
        last_updated = latest_intel.last_updated if latest_intel else None
        if latest_article and latest_article.published_date:
            if not last_updated or latest_article.published_date > last_updated:
                last_updated = latest_article.published_date
                
        data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_version": "1.0.0",
            "stats": {
                "article_count": article_count,
                "intel_count": intel_count,
                "actor_count": actor_count,
                "malware_count": malware_count,
            },
            "last_updated": last_updated.isoformat() if last_updated else None,
        }
    except Exception as e:
        # If we encounter any error, still return a response but with degraded status
        data = {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "api_version": "1.0.0",
            "error": str(e),
        }
    
    # Set CORS headers to allow cross-origin requests
    response = JsonResponse(data)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response

@api_view(['GET'])
def refresh_tailored_intel(request):
    """
    Endpoint to manually trigger tailored intelligence refresh
    """
    try:
        # Import the task
        from ioc_scraper.tasks import update_tailored_intelligence
        
        # Run the task synchronously
        result = update_tailored_intelligence()
        
        return JsonResponse({
            "status": "success",
            "message": "Tailored intelligence refresh completed",
            "result": result
        })
    except Exception as e:
        logger.error(f"Error refreshing tailored intelligence: {str(e)}")
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )

# Create your views here.

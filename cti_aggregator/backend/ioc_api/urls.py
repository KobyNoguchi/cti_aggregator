from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VulnerabilityViewSet, 
    IntelligenceArticleViewSet, 
    CrowdStrikeIntelViewSet,
    CrowdStrikeMalwareViewSet,
    CISAKevViewSet,
    get_cira_data,
    refresh_intelligence,
    threat_intelligence_feed
)

router = DefaultRouter()
router.register(r'vulnerabilities', VulnerabilityViewSet)
router.register(r'intelligence', IntelligenceArticleViewSet)
router.register(r'crowdstrike-intel', CrowdStrikeIntelViewSet)
router.register(r'crowdstrike/malware', CrowdStrikeMalwareViewSet, basename='crowdstrike-malware')
router.register(r'cisa/kev', CISAKevViewSet, basename='cisa-kev')

urlpatterns = [
    path('', include(router.urls)),
    path('cira-data/', get_cira_data, name='cira-data'),
    path('refresh-intelligence/', refresh_intelligence, name='refresh-intelligence'),
    path('threat-intelligence-feed/', threat_intelligence_feed, name='threat-intelligence-feed'),
]

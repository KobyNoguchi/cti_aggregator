from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VulnerabilityViewSet, 
    IntelligenceArticleViewSet, 
    CrowdStrikeIntelViewSet,
    CrowdStrikeMalwareViewSet,
    CISAKevViewSet,
    CrowdStrikeTailoredIntelViewSet,
    get_cira_data,
    refresh_intelligence,
    refresh_tailored_intel,
    threat_intelligence_feed,
    test_crowdstrike_api,
    health_check
)

router = DefaultRouter()
router.register(r'vulnerabilities', VulnerabilityViewSet)
router.register(r'intelligence', IntelligenceArticleViewSet)
router.register(r'crowdstrike-intel', CrowdStrikeIntelViewSet)
router.register(r'crowdstrike/malware', CrowdStrikeMalwareViewSet, basename='crowdstrike-malware')
router.register(r'cisa/kev', CISAKevViewSet, basename='cisa-kev')
router.register(r'crowdstrike/tailored-intel', CrowdStrikeTailoredIntelViewSet, basename='crowdstrike-tailored-intel')

urlpatterns = [
    path('', include(router.urls)),
    path('cira-data/', get_cira_data, name='cira-data'),
    path('refresh-intelligence/', refresh_intelligence, name='refresh-intelligence'),
    path('refresh-tailored-intel/', refresh_tailored_intel, name='refresh-tailored-intel'),
    path('threat-intelligence-feed/', threat_intelligence_feed, name='threat-intelligence-feed'),
    path('test-crowdstrike-api/', test_crowdstrike_api, name='test-crowdstrike-api'),
    path('health-check/', health_check, name='health-check'),
]

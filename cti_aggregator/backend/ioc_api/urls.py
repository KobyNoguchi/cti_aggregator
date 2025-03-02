from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VulnerabilityViewSet, 
    IntelligenceArticleViewSet, 
    CrowdStrikeIntelViewSet,
    CrowdStrikeMalwareViewSet,
    CISAKevViewSet,
    get_cira_data
)

router = DefaultRouter()
router.register(r'vulnerabilities', VulnerabilityViewSet)
router.register(r'intelligence', IntelligenceArticleViewSet)
router.register(r'crowdstrike-intel', CrowdStrikeIntelViewSet)
router.register(r'crowdstrike-malware', CrowdStrikeMalwareViewSet)
router.register(r'cisa/kev', CISAKevViewSet, basename='cisa-kev')

urlpatterns = [
    path('api/', include(router.urls)),
    path('cira-data/', get_cira_data, name='cira-data'),
]

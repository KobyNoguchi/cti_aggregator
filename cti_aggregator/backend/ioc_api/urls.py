from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VulnerabilityViewSet, 
    IntelligenceArticleViewSet, 
    CrowdStrikeIntelViewSet,
    CrowdStrikeMalwareViewSet
)

router = DefaultRouter()
router.register(r'vulnerabilities', VulnerabilityViewSet)
router.register(r'intelligence', IntelligenceArticleViewSet)
router.register(r'crowdstrike-intel', CrowdStrikeIntelViewSet)
router.register(r'crowdstrike-malware', CrowdStrikeMalwareViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

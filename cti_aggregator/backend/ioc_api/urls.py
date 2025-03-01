from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VulnerabilityViewSet, IntelligenceArticleViewSet

router = DefaultRouter()
router.register(r'vulnerabilities', VulnerabilityViewSet)
router.register(r'intelligence', IntelligenceArticleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

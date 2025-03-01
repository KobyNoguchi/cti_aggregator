from rest_framework import serializers
from ioc_scraper.models import Vulnerability, IntelligenceArticle

class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = "__all__"

class IntelligenceArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntelligenceArticle
        fields = "__all__"

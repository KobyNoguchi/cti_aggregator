from rest_framework import serializers
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel, CrowdStrikeMalware

class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = "__all__"

class IntelligenceArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntelligenceArticle
        fields = "__all__"

class CrowdStrikeIntelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdStrikeIntel
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Initialize array fields to empty list if they are None
        array_fields = ['capabilities', 'motivations', 'objectives', 'origins']
        for field in array_fields:
            if representation[field] is None:
                representation[field] = []
                
        return representation

class CrowdStrikeMalwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrowdStrikeMalware
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Initialize array fields to empty list if they are None
        array_fields = ['ttps', 'targeted_industries', 'threat_groups']
        for field in array_fields:
            if representation[field] is None:
                representation[field] = []
                
        return representation

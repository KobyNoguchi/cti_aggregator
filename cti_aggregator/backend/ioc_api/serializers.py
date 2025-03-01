from rest_framework import serializers
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel

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
        fields = ['actor_id', 'name', 'description', 'capabilities', 'motivations', 
                  'objectives', 'adversary_type', 'origins', 'last_update_date']

    def to_representation(self, instance):
        """Ensure array fields are properly serialized."""
        representation = super().to_representation(instance)
        
        # Ensure array fields are properly serialized
        for field in ['capabilities', 'motivations', 'objectives', 'origins']:
            if representation.get(field) is None:
                representation[field] = []
                
        return representation

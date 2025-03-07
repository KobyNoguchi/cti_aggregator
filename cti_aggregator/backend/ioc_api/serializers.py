from rest_framework import serializers
from ioc_scraper.models import Vulnerability, IntelligenceArticle, CrowdStrikeIntel, CrowdStrikeMalware

class VulnerabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vulnerability
        fields = "__all__"

class CISAKevSerializer(serializers.ModelSerializer):
    # Map Django model fields to the frontend expected field names
    id = serializers.CharField()
    cveID = serializers.CharField(source='cve_id')
    vulnerabilityName = serializers.CharField(source='vulnerability_name')
    dateAdded = serializers.DateField(source='published_date')
    shortDescription = serializers.CharField(source='description')
    vendorProject = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    severityLevel = serializers.CharField(source='severity')
    requiredAction = serializers.SerializerMethodField()
    dueDate = serializers.SerializerMethodField()
    
    class Meta:
        model = Vulnerability
        fields = [
            'id', 'cveID', 'vulnerabilityName', 'dateAdded', 
            'shortDescription', 'requiredAction', 'dueDate',
            'vendorProject', 'product', 'severityLevel'
        ]
    
    def get_vendorProject(self, obj):
        # Try to extract vendor from vulnerability name or return a default
        if 'Microsoft' in obj.vulnerability_name:
            return 'Microsoft'
        elif 'Adobe' in obj.vulnerability_name:
            return 'Adobe'
        elif 'Cisco' in obj.vulnerability_name:
            return 'Cisco'
        elif 'Oracle' in obj.vulnerability_name:
            return 'Oracle'
        elif 'VMware' in obj.vulnerability_name:
            return 'VMware'
        # Add more vendors as needed
        return 'Unknown'
    
    def get_product(self, obj):
        # Try to extract product from vulnerability name or description
        # This is a simple implementation; you might want to enhance it
        return 'Affected Product'
    
    def get_requiredAction(self, obj):
        return "Apply vendor patch or update as available."
    
    def get_dueDate(self, obj):
        # You could calculate a due date based on severity and published date
        # For now, just return None
        return None

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
